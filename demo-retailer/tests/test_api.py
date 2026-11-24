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
              "purchasing": "/purchasing/invoices", "property": "/property/leases", "performance": "/performance/periods",
              "tills": "/tills/rules", "orders": "/orders/orders", "catalogue": "/catalogue/listings",
              "stock": "/stock/levels", "pricing": "/pricing/prices", "loyalty": "/loyalty/members"}
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
                assert oid.split("_")[0] in ("list", "get", "save", "request", "record", "sign", "approve", "raise", "search", "send",
                                             "publish", "refuse", "release", "hold", "issue"), oid
                assert oid not in seen, f"duplicate {oid}"
                seen[oid] = system
                assert op["summary"].strip() and len(op["description"]) > 40, oid
                for p in op.get("parameters", []):
                    assert p.get("description"), (oid, p["name"])
                if "(change)" in op["summary"]:
                    assert method == "post", oid
    assert counts == {"stores": 5, "foodsafety": 8, "care": 20, "purchasing": 20, "property": 3, "performance": 4, "tills": 4,
                      "orders": 14, "catalogue": 12, "stock": 15, "pricing": 16, "loyalty": 10}
    assert sum(counts.values()) == 131
    assert sorted(seen) == sorted([
        "list_sites", "get_site", "list_site_visits", "get_site_visit", "save_visit_report",
        "get_food_safety_plan", "list_record_periods", "get_food_safety_records", "get_record_review", "save_record_check",
        "request_corrective_actions", "record_corrective_action", "sign_monthly_review",
        "list_guest_feedback", "get_guest_feedback", "get_feedback_analysis", "save_feedback_analysis",
        "list_suppliers", "get_supplier", "list_purchase_orders", "get_purchase_order", "list_goods_receipts",
        "list_supplier_invoices", "get_supplier_invoice", "save_invoice_match", "approve_invoice_for_payment",
        "raise_invoice_query",
        "list_leases", "get_lease", "save_lease_summary",
        "list_performance_periods", "get_restaurant_performance", "get_peer_group_performance", "save_performance_review",
        "get_till_rules", "list_till_entries", "get_till_audit", "save_till_audit",
        # version 1.2
        "list_customer_tickets", "get_customer_ticket", "search_help_articles", "search_past_cases", "save_ticket_reply",
        "send_ticket_reply", "list_complaints", "get_complaint", "get_complaints_procedure", "save_complaint_classification",
        "save_complaint_response", "send_complaint_response", "list_public_reviews", "get_public_review", "save_review_reply",
        "publish_review_reply",
        "list_delivery_notes", "get_delivery_note", "save_discrepancy_claim", "send_discrepancy_claim",
        "list_supplier_payments", "get_supplier_payment", "list_supplier_questions", "get_supplier_question",
        "save_supplier_reply", "send_supplier_reply",
        "search_orders", "get_order", "get_delivery_scans", "get_returns_policy", "list_return_requests", "get_return_request",
        "save_return_assessment", "approve_return", "refuse_return", "list_flagged_orders", "get_customer_order_history",
        "save_fraud_review", "release_flagged_order", "hold_flagged_order",
        # version 1.3
        "list_product_listings", "get_product_listing", "get_supplier_specification", "get_product_style_guide",
        "list_new_products", "save_product_description", "publish_product_description", "get_product_data_checks",
        "save_product_data_check", "get_search_log", "get_search_terms_analysis", "save_search_terms_analysis",
        "list_stock_levels", "get_line_stock_history", "get_replenishment_rules", "list_supply_terms",
        "get_replenishment_plan", "save_replenishment_plan", "approve_replenishment_plan", "list_stock_counts",
        "get_shrink_tolerance", "get_shrink_analysis", "save_shrink_analysis", "list_batches", "get_batch_trace",
        "save_recall_pack", "issue_recall_notice",
        "list_prices", "list_competitor_prices", "get_pricing_rules", "get_price_recommendations",
        "save_price_recommendations", "approve_price_changes", "list_promotions", "get_promotion", "save_promotion_review",
        "get_range_review_thresholds", "get_range_review_data", "save_range_review_pack", "list_line_sales_history",
        "get_market_notes", "get_demand_plan_notes", "save_demand_plan_note",
        "list_members", "get_member", "get_personalisation_rules", "save_product_suggestions",
        "get_loyalty_programme_summary", "list_past_campaigns", "get_past_campaign", "get_campaign_brief_template",
        "list_campaign_briefs", "save_campaign_brief"])


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
                       "approve_invoice_for_payment", "raise_invoice_query",
                       # version 1.2: nine changes, each made by a named person after a draft is saved
                       "send_ticket_reply", "send_complaint_response", "publish_review_reply", "send_discrepancy_claim",
                       "send_supplier_reply", "approve_return", "refuse_return", "release_flagged_order",
                       "hold_flagged_order",
                       # version 1.3: four changes, each made by a named person after a draft is saved
                       "publish_product_description", "approve_replenishment_plan", "issue_recall_notice",
                       "approve_price_changes"}
    # version 1.1 added no operation that changes a record: its four writes are drafts
    drafts = {op["operationId"] for doc in docs(client).values() for item in doc["paths"].values() for op in item.values()
              if op["summary"].endswith("(draft)")}
    assert drafts == {"save_record_check", "save_feedback_analysis", "save_invoice_match", "save_visit_report",
                      "save_lease_summary", "save_performance_review", "save_till_audit",
                      # version 1.2
                      "save_ticket_reply", "save_complaint_classification", "save_complaint_response", "save_review_reply",
                      "save_discrepancy_claim", "save_supplier_reply", "save_return_assessment", "save_fraud_review",
                      # version 1.3
                      "save_product_description", "save_product_data_check", "save_search_terms_analysis",
                      "save_replenishment_plan", "save_shrink_analysis", "save_recall_pack", "save_price_recommendations",
                      "save_promotion_review", "save_range_review_pack", "save_demand_plan_note", "save_product_suggestions",
                      "save_campaign_brief"}


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
    assert "supplier-invoice" in text and "food-safety-records" in text and "site-visit" in text
    assert "The twelve systems" in text


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
    assert len(d["sites"]) == 20 and len(d["suppliers"]) == 4 and len(d["purchase_orders"]) == 8
    assert len(d["goods_receipts"]) == 8 and len(d["supplier_invoices"]) == 6 and len(d["guest_feedback"]) == 260
    for ref, x in d["guest_feedback"].items():
        assert x["site_id"] in d["sites"] and d["sites"][x["site_id"]]["kind"] == "restaurant"
        assert 1 <= x["rating"] <= 5 and x["date"].startswith("2026-10-")
    for key, rec in d["fs_records"].items():
        assert key == f"{rec['site_id']}:{rec['period']}" and key in d["fs_reviews"]
    for p in d["purchase_orders"].values():
        assert p["supplier_id"] in d["suppliers"]
    assert len(d["leases"]) == 9 and len(d["site_visits"]) == 6 and len(d["performance"]) == 36 and len(d["till_rows"]) == 180
    restaurants = {k for k, s in d["sites"].items() if s["kind"] == "restaurant"}
    assert {x["site_id"] for x in d["leases"].values()} <= set(d["sites"]) and len({x["site_id"] for x in d["leases"].values()}) == 9
    assert {x["site_id"] for x in d["performance"].values()} == restaurants
    assert sorted(s for g in d["peer_groups"].values() for s in g["site_ids"]) == sorted(restaurants)
    assert {x["site_id"] for x in d["till_rows"].values()} == set(d["sites"])
    assert {v["site_id"] for v in d["site_visits"].values()} <= set(d["sites"])
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
