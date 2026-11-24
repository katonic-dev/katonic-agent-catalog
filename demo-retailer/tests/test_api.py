import json
import os
import threading
import time
from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer

from fastapi.testclient import TestClient
from openapi_spec_validator import validate

from conftest import H, KEY, SYSTEMS, TODAY, make_env
from retailer.app import create_app
from retailer.seed import build_all


# ---------------------------------------------------------------- sign-in

def test_key_is_required_and_both_forms_work(client):
    assert client.get("/stores/sites").status_code == 401
    assert client.get("/stores/sites", headers={"X-API-Key": "wrong"}).status_code == 401
    assert client.get("/stores/sites", headers=H).status_code == 200
    assert client.get("/stores/sites", headers={"Authorization": f"Bearer {KEY}"}).status_code == 200
    assert client.get("/admin/state").status_code == 401
    assert client.get("/admin/state", headers=H).status_code == 200
    for method, path in [("post", "/admin/reset"), ("post", "/admin/reset/care"), ("get", "/admin/events"),
                         ("post", "/admin/simulate/supplier-invoice")]:
        assert getattr(client, method)(path).status_code == 401, path


def test_every_system_refuses_a_call_without_a_key(client):
    probes = {"stores": "/stores/sites", "foodsafety": "/foodsafety/plan", "care": "/care/feedback",
              "purchasing": "/purchasing/invoices"}
    assert list(probes) == SYSTEMS
    for path in probes.values():
        r = client.get(path)
        assert r.status_code == 401 and r.json()["applied"] is False
        assert client.get(path, headers=H).status_code == 200


def test_open_pages_need_no_key(client):
    paths = ["/", "/health", "/healthz"] + [f"/{s}/{p}" for s in SYSTEMS for p in ("docs", "openapi.json")]
    for path in paths:
        assert client.get(path).status_code == 200, path
    body = client.get("/health").json()
    assert body["status"] == "ok" and body["retailer_date"] == TODAY


def test_auth_off_shows_warning_and_needs_no_key():
    c = TestClient(create_app(make_env(RETAILER_AUTH="off")))
    assert c.get("/stores/sites").status_code == 200
    assert c.get("/admin/state").status_code == 200
    assert c.post("/foodsafety/reviews/R-022/2026-10/sign", json={"signed_by": "A. Manager"}).status_code == 200
    assert "sign-in is OFF" in c.get("/").text
    assert "RETAILER_AUTH=off" in c.get("/").text


def test_auth_on_shows_no_warning(client):
    assert "sign-in is OFF" not in client.get("/").text


def test_generated_key_is_not_on_any_page(capsys):
    app = create_app({"RETAILER_TODAY": TODAY})
    key = app.state.ctx.settings.api_key
    assert key in capsys.readouterr().out
    c = TestClient(app)
    assert key not in c.get("/").text
    assert c.get("/stores/sites", headers={"X-API-Key": key}).status_code == 200


def test_demo_markers(client):
    r = client.get("/stores/sites/R-014", headers=H)
    assert r.json()["demo_data"] is True and r.headers["x-demo-data"] == "invented"
    r = client.get("/stores/sites/R-999", headers=H)
    assert r.status_code == 404 and r.json()["demo_data"] is True and r.headers["x-demo-data"] == "invented"
    assert client.get("/").headers["x-demo-data"] == "invented"
    assert client.get("/foodsafety/openapi.json").headers["x-demo-data"] == "invented"


def test_the_name_shown_is_rowanmere_group_invented(client):
    page = client.get("/").text
    assert "<h1>Rowanmere Group (invented)</h1>" in page
    assert "invented" in page.split("</h1>")[1][:300].lower()
    for s in SYSTEMS:
        doc = client.get(f"/{s}/openapi.json").json()
        assert doc["info"]["title"].startswith("Rowanmere Group (invented)")


# ---------------------------------------------------------------- OpenAPI

def docs(client):
    return {s: client.get(f"/{s}/openapi.json").json() for s in SYSTEMS}


def test_openapi_documents_are_valid_303(client):
    for system, doc in docs(client).items():
        assert doc["openapi"] == "3.0.3"
        validate(doc)
        first = doc["info"]["description"].split(".")[0]
        assert "invented" in first.lower(), system
        assert "ApiKeyAuth" in doc["components"]["securitySchemes"]
        assert "anyOf" not in json.dumps(doc), system
        assert '"type": "null"' not in json.dumps(doc), system


def test_operations_have_clean_unique_ids_summaries_descriptions(client):
    seen, counts = {}, {}
    for system, doc in docs(client).items():
        counts[system] = 0
        for path, item in doc["paths"].items():
            for method, op in item.items():
                counts[system] += 1
                oid = op["operationId"]
                assert oid.islower() and all(c.isalnum() or c == "_" for c in oid), oid
                assert oid.split("_")[0] in ("list", "get", "save", "request", "record", "sign", "approve", "raise"), oid
                assert oid not in seen, f"duplicate {oid}"
                seen[oid] = system
                assert op["summary"].strip() and len(op["description"]) > 40, oid
                for p in op.get("parameters", []):
                    assert p.get("description"), (oid, p["name"])
                if "(change)" in op["summary"]:
                    assert method == "post", oid
    assert counts == {"stores": 2, "foodsafety": 8, "care": 4, "purchasing": 10}
    assert sorted(seen) == sorted([
        "list_sites", "get_site",
        "get_food_safety_plan", "list_record_periods", "get_food_safety_records", "get_record_review", "save_record_check",
        "request_corrective_actions", "record_corrective_action", "sign_monthly_review",
        "list_guest_feedback", "get_guest_feedback", "get_feedback_analysis", "save_feedback_analysis",
        "list_suppliers", "get_supplier", "list_purchase_orders", "get_purchase_order", "list_goods_receipts",
        "list_supplier_invoices", "get_supplier_invoice", "save_invoice_match", "approve_invoice_for_payment",
        "raise_invoice_query"])


def test_the_operations_that_change_a_record_say_so_in_the_summary(client):
    changes = set()
    for doc in docs(client).values():
        for item in doc["paths"].values():
            for op in item.values():
                if op["summary"].endswith("(change)"):
                    changes.add(op["operationId"])
                if op["summary"].endswith("(draft)"):
                    assert op["operationId"].startswith("save_")
    assert changes == {"request_corrective_actions", "record_corrective_action", "sign_monthly_review",
                       "approve_invoice_for_payment", "raise_invoice_query"}


def test_servers_and_docs_under_a_prefix():
    app = create_app(make_env())
    c = TestClient(app, root_path="/apps/demo-retailer")
    doc = c.get("/apps/demo-retailer/stores/openapi.json").json()
    assert doc["servers"][0]["url"] == "/apps/demo-retailer/stores"
    page = c.get("/apps/demo-retailer/stores/docs").text
    assert "/apps/demo-retailer/stores/openapi.json" in page
    assert "cdn" not in page.lower() and "unpkg" not in page.lower()
    assert "/apps/demo-retailer/stores/docs" in c.get("/apps/demo-retailer/").text


def test_landing_page_has_no_external_assets(client):
    text = client.get("/").text
    assert "http://" not in text.replace("http://testserver", "") and "https://" not in text
    for s in SYSTEMS:
        assert f"/{s}/openapi.json" in text and f"/{s}/mcp" in text and f"/{s}/sse" in text
    assert "supplier-invoice" in text and "food-safety-records" in text


# ---------------------------------------------------------------- data invariants

def test_data_is_identical_for_same_date_and_seed():
    assert build_all(date(2026, 11, 24)) == build_all(date(2026, 11, 24))
    assert build_all(date(2026, 11, 24)) != build_all(date(2026, 11, 25))


def test_the_period_follows_the_retailer_date():
    d = build_all(date(2026, 12, 3))
    assert {r["period"] for r in d["fs_records"].values()} == {"2026-11"}
    assert all(ref.startswith("GF-2611-") for ref in d["guest_feedback"])
    jan = build_all(date(2027, 1, 5))
    assert {r["period"] for r in jan["fs_records"].values()} == {"2026-12"}
    assert len(jan["guest_feedback"]) == 260


def test_ids_and_counts(store):
    d = store.data
    assert len(d["sites"]) == 20 and len(d["suppliers"]) == 4 and len(d["purchase_orders"]) == 6
    assert len(d["goods_receipts"]) == 6 and len(d["supplier_invoices"]) == 6 and len(d["guest_feedback"]) == 260
    for ref, x in d["guest_feedback"].items():
        assert x["site_id"] in d["sites"] and d["sites"][x["site_id"]]["kind"] == "restaurant"
        assert 1 <= x["rating"] <= 5 and x["date"].startswith("2026-10-")
    for key, rec in d["fs_records"].items():
        assert key == f"{rec['site_id']}:{rec['period']}" and key in d["fs_reviews"]
    for p in d["purchase_orders"].values():
        assert p["supplier_id"] in d["suppliers"]
    for r in d["goods_receipts"].values():
        assert r["po_number"] in d["purchase_orders"]
    for i in d["supplier_invoices"].values():
        assert i["po_number"] in d["purchase_orders"] and i["supplier_id"] in d["suppliers"]


def test_all_invoice_dates_are_in_the_ten_days_before_the_retailer_date(store):
    today = date.fromisoformat(TODAY)
    for i in store.data["supplier_invoices"].values():
        assert 0 < (today - date.fromisoformat(i["invoice_date"])).days <= 10, i["invoice_number"]


def test_amounts_are_in_dollars_and_tax_is_fifteen_percent(store):
    for i in store.data["supplier_invoices"].values():
        assert i["currency"] == "USD" and i["tax"] == round(i["net"] * 0.15, 2) and i["total"] == round(i["net"] + i["tax"], 2)
        assert i["net"] == round(sum(x["amount"] for x in i["lines"]), 2)


# ---------------------------------------------------------------- reset

def test_reset_restores_starting_data(client, store):
    client.post("/foodsafety/reviews/R-022/2026-10/sign", json={"signed_by": "A. Manager"}, headers=H)
    client.post("/admin/simulate/supplier-invoice", headers=H)
    assert store.data["fs_reviews"]["R-022:2026-10"]["status"] == "signed"
    assert len(store.data["supplier_invoices"]) == 7
    r = client.post("/admin/reset", headers=H)
    assert r.status_code == 200 and r.json()["applied"] is True
    assert store.data == build_all(date.fromisoformat(TODAY))
    state = client.get("/admin/state", headers=H).json()
    assert state["counts"]["record_periods_not_reviewed"] == 6 and state["counts"]["supplier_invoices_received"] == 6
    assert state["retailer_date"] == TODAY and state["auth_enabled"] is True and state["changed_by"] == {}
    assert client.get("/admin/events", headers=H).json()["count"] == 0


# ---------------------------------------------------------------- events

class Receiver(BaseHTTPRequestHandler):
    got = []

    def do_POST(self):
        body = self.rfile.read(int(self.headers["Content-Length"]))
        Receiver.got.append((dict(self.headers), json.loads(body)))
        self.send_response(200)
        self.end_headers()

    def log_message(self, *a):
        pass


def test_simulate_creates_item_and_subscriber_receives_it(client, store):
    Receiver.got = []
    srv = HTTPServer(("127.0.0.1", 0), Receiver)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_port}/hook"
    sub = client.post("/admin/subscriptions", json={"event_kind": "supplier-invoice", "url": url,
                                                     "header_name": "X-Hook-Secret", "secret_value": "s3cret"}, headers=H).json()
    assert sub["subscription"]["secret_value"] == "***"
    assert client.get("/admin/subscriptions", headers=H).json()["items"][0]["secret_value"] == "***"
    before = len(store.data["supplier_invoices"])
    r = client.post("/admin/simulate/supplier-invoice", headers=H).json()
    assert len(store.data["supplier_invoices"]) == before + 1 and r["item_id"] in store.data["supplier_invoices"]
    for _ in range(50):
        if Receiver.got:
            break
        time.sleep(0.1)
    headers, payload = Receiver.got[0]
    assert headers["X-Hook-Secret"] == "s3cret"
    assert payload["event_type"] == "supplier-invoice" and payload["item_id"] == r["item_id"]
    assert payload["system"] == "purchasing" and payload["demo_data"] is True and r["item_id"] in payload["message"]
    assert "purchasing system" in payload["message"]
    ev = client.get("/admin/events", headers=H).json()["items"]
    assert any(e.get("status") == "delivered" for e in ev) and any(e.get("status") == "created" for e in ev)
    # the other kind does not reach this subscriber
    client.post("/admin/simulate/food-safety-records", headers=H)
    time.sleep(0.3)
    srv.shutdown()
    assert len(Receiver.got) == 1


def test_a_star_subscription_gets_both_kinds_and_can_be_deleted(client):
    Receiver.got = []
    srv = HTTPServer(("127.0.0.1", 0), Receiver)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    sub = client.post("/admin/subscriptions", json={"url": f"http://127.0.0.1:{srv.server_port}/h"}, headers=H).json()["subscription"]
    assert sub["event_kind"] == "*"
    client.post("/admin/simulate/supplier-invoice", headers=H)
    client.post("/admin/simulate/food-safety-records", headers=H)
    for _ in range(50):
        if len(Receiver.got) >= 2:
            break
        time.sleep(0.1)
    srv.shutdown()
    assert sorted(p["event_type"] for _, p in Receiver.got) == ["food-safety-records", "supplier-invoice"]
    assert client.delete(f"/admin/subscriptions/{sub['subscription_id']}", headers=H).status_code == 200
    assert client.delete(f"/admin/subscriptions/{sub['subscription_id']}", headers=H).status_code == 404
    client.post("/admin/subscriptions", json={"url": "http://127.0.0.1:9/a"}, headers=H)
    assert client.delete("/admin/subscriptions", headers=H).json()["deleted"] == 1
    assert client.post("/admin/subscriptions", json={"event_kind": "nonsense", "url": "http://x"}, headers=H).status_code == 422


def test_unknown_kind_is_404(client):
    r = client.post("/admin/simulate/nonsense", headers=H)
    assert r.status_code == 404 and "supplier-invoice" in r.json()["detail"] and "food-safety-records" in r.json()["detail"]


def test_subscription_to_dead_url_never_fails_caller(client):
    client.post("/admin/subscriptions", json={"url": "http://127.0.0.1:9/none"}, headers=H)
    assert client.post("/admin/simulate/supplier-invoice", headers=H).status_code == 200
    assert client.post("/admin/simulate/food-safety-records", headers=H).status_code == 200


def test_webhooks_from_environment():
    env = make_env(RETAILER_WEBHOOKS=json.dumps([{"event_kind": "*", "url": "http://127.0.0.1:9/x", "header_name": "H",
                                                  "secret_value": "v"}]))
    c = TestClient(create_app(env))
    assert c.get("/admin/subscriptions", headers=H).json()["count"] == 1
    bad = TestClient(create_app(make_env(RETAILER_WEBHOOKS="not json")))
    assert bad.get("/admin/subscriptions", headers=H).json()["count"] == 0


def test_public_scheme_setting_is_read(monkeypatch):
    monkeypatch.setenv("RETAILER_PUBLIC_SCHEME", "https")
    c = TestClient(create_app(make_env()))
    assert "https://" in c.get("/").text


# ---------------------------------------------------------------- disk

def test_nothing_is_written_without_a_data_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    c = TestClient(create_app(make_env()))
    c.post("/foodsafety/reviews/R-022/2026-10/sign", json={"signed_by": "A. Manager"}, headers=H)
    c.post("/admin/simulate/supplier-invoice", headers=H)
    assert list(tmp_path.iterdir()) == []
    repo = os.path.dirname(os.path.dirname(__file__))
    assert not [f for f in os.listdir(repo) if f.endswith(".json")]


def test_state_file_written_only_when_directory_given_and_never_holds_secrets(tmp_path):
    c = TestClient(create_app(make_env(DATA_DIR=str(tmp_path / "state"))))
    c.post("/admin/subscriptions", json={"url": "http://127.0.0.1:9/x", "header_name": "H", "secret_value": "topsecret"}, headers=H)
    c.post("/foodsafety/reviews/R-022/2026-10/sign", json={"signed_by": "A. Manager"}, headers=H)
    f = tmp_path / "state" / "demo-retailer-state.json"
    assert f.exists() and "topsecret" not in f.read_text()
    again = create_app(make_env(DATA_DIR=str(tmp_path / "state")))
    assert again.state.ctx.store.data["fs_reviews"]["R-022:2026-10"]["status"] == "signed"


def test_dataset_path_env_chooses_subfolder(tmp_path):
    c = TestClient(create_app(make_env(KATONIC_DATASET_PATH=str(tmp_path))))
    c.post("/foodsafety/reviews/R-022/2026-10/sign", json={"signed_by": "A. Manager"}, headers=H)
    assert (tmp_path / "demo-retailer-state" / "demo-retailer-state.json").exists()


def test_a_state_file_of_another_date_is_ignored(tmp_path):
    c = TestClient(create_app(make_env(DATA_DIR=str(tmp_path))))
    c.post("/foodsafety/reviews/R-022/2026-10/sign", json={"signed_by": "A. Manager"}, headers=H)
    other = create_app(make_env(DATA_DIR=str(tmp_path), RETAILER_TODAY="2026-11-25"))
    assert other.state.ctx.store.data["fs_reviews"]["R-022:2026-10"]["status"] == "not_reviewed"
