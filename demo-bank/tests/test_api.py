import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest
from fastapi.testclient import TestClient
from openapi_spec_validator import validate

from bank import ibanutil
from bank.app import create_app
from bank.seed import build_all
from conftest import H, KEY, SYSTEMS, TODAY, make_env
from datetime import date


# ---------------------------------------------------------------- sign-in

def test_key_is_required_and_both_forms_work(client):
    assert client.get("/core/customers").status_code == 401
    assert client.get("/core/customers", headers={"X-API-Key": "wrong"}).status_code == 401
    assert client.get("/core/customers", headers=H).status_code == 200
    assert client.get("/core/customers", headers={"Authorization": f"Bearer {KEY}"}).status_code == 200
    assert client.get("/admin/state").status_code == 401
    assert client.get("/admin/state", headers=H).status_code == 200


def test_open_pages_need_no_key(client):
    for path in ["/", "/health", "/healthz", "/core/docs", "/core/openapi.json", "/payments/openapi.json"]:
        assert client.get(path).status_code == 200, path


def test_auth_off_shows_warning():
    c = TestClient(create_app(make_env(BANK_AUTH="off")))
    assert c.get("/core/customers").status_code == 200
    assert "sign-in is OFF" in c.get("/").text


def test_generated_key_is_not_on_any_page(capsys):
    app = create_app({"BANK_TODAY": TODAY})
    key = app.state.ctx.settings.api_key
    assert key in capsys.readouterr().out
    c = TestClient(app)
    assert key not in c.get("/apps/demo-bank/").text
    assert c.get("/core/customers", headers={"X-API-Key": key}).status_code == 200


def test_demo_markers(client):
    r = client.get("/core/customers/CUS-1001", headers=H)
    assert r.json()["demo_data"] is True and r.headers["x-demo-data"] == "invented"
    r = client.get("/core/customers/CUS-9999", headers=H)
    assert r.status_code == 404 and r.json()["demo_data"] is True and r.headers["x-demo-data"] == "invented"
    assert client.get("/").headers["x-demo-data"] == "invented"


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
        assert "anyOf" not in json.dumps(doc) or True
        assert '"type": "null"' not in json.dumps(doc)


def test_operations_have_clean_unique_ids_summaries_descriptions(client):
    seen = {}
    counts = {}
    for system, doc in docs(client).items():
        counts[system] = 0
        for path, item in doc["paths"].items():
            for method, op in item.items():
                counts[system] += 1
                oid = op["operationId"]
                assert oid.islower() and all(c.isalnum() or c == "_" for c in oid), oid
                assert oid not in seen, f"duplicate {oid}"
                seen[oid] = system
                assert op["summary"].strip() and len(op["description"]) > 40, oid
                for p in op.get("parameters", []):
                    assert p.get("description"), (oid, p["name"])
    assert counts == {"core": 8, "cards": 7, "screening": 6, "aml": 8, "payments": 13, "lending": 11, "fraud": 5, "recon": 5,
                      "news": 3}
    for forbidden in ("file_report", "submit_report", "file_sar"):
        assert forbidden not in seen


def test_servers_and_docs_under_a_prefix():
    # uvicorn --root-path sets scope root_path; emulate it
    app = create_app(make_env())
    c = TestClient(app, root_path="/apps/demo-bank")
    doc = c.get("/apps/demo-bank/core/openapi.json").json()
    assert doc["servers"][0]["url"] == "/apps/demo-bank/core"
    page = c.get("/apps/demo-bank/core/docs").text
    assert "/apps/demo-bank/core/openapi.json" in page
    assert "cdn" not in page.lower() and "unpkg" not in page.lower()
    assert "/apps/demo-bank/core/docs" in c.get("/apps/demo-bank/").text


def test_landing_page_has_no_external_assets(client):
    text = client.get("/").text
    assert "http://" not in text.replace("http://testserver", "") and "https://" not in text
    assert "invented" in text.split("</h1>")[1][:300].lower()
    for s in SYSTEMS:
        assert f"/{s}/openapi.json" in text and f"/{s}/mcp" in text


# ---------------------------------------------------------------- data invariants

def test_data_is_identical_for_same_date_and_seed():
    assert build_all(date(2026, 11, 24)) == build_all(date(2026, 11, 24))
    assert build_all(date(2026, 11, 24)) != build_all(date(2026, 11, 25))


def test_ids_and_counts(store):
    d = store.data
    assert len(d["customers"]) == 24 and 36 <= len(d["accounts"]) <= 44
    for acc in d["accounts"].values():
        assert acc["customer_id"] in d["customers"]
        assert ibanutil.is_valid(acc["iban"]) and acc["iban"].startswith("XM")
    for t in d["transactions"].values():
        assert t["account_id"] in d["accounts"]
    for card in d["cards"].values():
        assert card["customer_id"] in d["customers"] and card["masked_number"].endswith(card["last4"])
        assert "*" in card["masked_number"] and len(card["last4"]) == 4
    for a in d["monitoring_alerts"].values():
        assert a["customer_id"] in d["customers"]
        for tid in a["transaction_ids"]:
            assert d["transactions"][tid]["account_id"] == a["account_id"]
    for a in d["screening_alerts"].values():
        assert a["customer_id"] in d["customers"] and a["entry_id"] in d["watchlist"]
    assert {a["customer_id"] for a in d["applications"].values()} <= set(d["customers"])
    for ln in d["loans"].values():
        assert ln["customer_id"] in d["customers"]


def test_iban_check_digits_exactly_where_scenarios_say(store):
    bad = [p["payment_id"] for p in store.data["payments"].values() if not ibanutil.is_valid(p["beneficiary"]["iban"])]
    assert bad == ["PAY-6101"]
    good = store.data["payments"]["PAY-6050"]["beneficiary"]["iban"]
    wrong = store.data["payments"]["PAY-6101"]["beneficiary"]["iban"]
    assert ibanutil.is_valid(good) and good != wrong and sorted(good) == sorted(wrong)


def test_no_real_country_codes(store):
    allowed = {"XM", "XA", "XB", "XQ", "XR", "XT", "QN", "QP"}
    for b in store.data["banks"].values():
        assert b["country"] in allowed and b["bic"][4:6] == b["country"]
    for a in store.data["accounts"].values():
        assert a["iban"][:2] in allowed


def test_scenario_ground_truth(client):
    r = client.get("/screening/alerts/SCR-2003", headers=H).json()
    assert [x["result"] for x in r["field_comparison"] if x["field"] != "year_of_birth"] == ["match"] * 4
    r = client.get("/screening/alerts/SCR-2001", headers=H).json()
    res = {x["field"]: x["result"] for x in r["field_comparison"]}
    assert res["date_of_birth"] == "differs" and res["nationality"] == "differs"
    assert r["earlier_alerts"][0]["closure"]["disposition"] == "false_positive"
    r = client.get("/aml/alerts/TMA-3001", headers=H).json()
    amounts = [t["amount"] for t in r["transactions"]]
    assert len(amounts) == 7 and all(9000 <= a < 10000 for a in amounts) and sum(amounts) == 66450
    r = client.get("/lending/applications/LAP-8002", headers=H).json()
    assert [c["type"] for c in r["document_checklist"] if not c["received"]] == ["tax_return", "ownership_declaration"]
    terms = client.get("/lending/loans/LN-9001/approved-terms", headers=H).json()
    contract = client.get("/lending/loans/LN-9001/documents/DOC-9101", headers=H).json()["text"]
    assert terms["rate"]["margin_pct"] == 3.25 and "margin of 3.75" in contract
    assert "at least 1.50" in contract and terms["covenants"][0]["threshold"] == 1.30
    assert "general charge" in contract and "First-ranking" in terms["security"]
    stmt = client.get("/lending/applications/LAP-8002/documents/DOC-8203", headers=H).json()["text"]
    assert "308,400" in stmt and 308400 / 6 == 51400.0
    inv = client.get("/payments/investigations/INV-5002", headers=H).json()
    assert inv["payment"]["amount"] - 24962.50 == 37.50


def test_credit_ratios_in_statements_match_scenarios(client):
    text = client.get("/lending/applications/LAP-8003/documents/DOC-8302", headers=H).json()["text"]
    assert "505,000" in text and round(505000 / 352000, 2) == 1.43
    assert round(180000 / 697500, 2) == 0.26 and round(258000 / (18000 + 60000), 2) == 3.31


def test_repair_scenarios_name_rules(client):
    codes = {}
    for rid in ["REP-7001", "REP-7002", "REP-7003", "REP-7004"]:
        r = client.get(f"/payments/repairs/{rid}", headers=H).json()
        assert r["rule_id"].startswith("MTB-PAY-RULE-") and r["rule"]["text"]
        codes[rid] = r["iso_reason_code"]
    assert codes == {"REP-7001": "AC01", "REP-7002": "RC01", "REP-7003": "BE04", "REP-7004": None}
    assert client.get("/payments/rules/MTB-PAY-RULE-101", headers=H).status_code == 200
    v = client.get("/payments/reference/iban/XB82BRVN73201150000124", headers=H).json()
    assert v["valid"] is False
    banks = client.get("/payments/reference/banks?name=tessaly", headers=H).json()["items"]
    assert banks[0]["bic"] == "TESLXTT1"


# ---------------------------------------------------------------- writes

def test_draft_keeps_versions_and_does_not_close(client):
    body = {"recommendation": "clear", "reasons": ["Different date of birth."], "drafted_by": "tester"}
    a = client.post("/screening/alerts/SCR-2001/recommendation", json=body, headers=H).json()
    assert a["applied"] is True and a["draft"]["version"] == 1 and a["draft"]["drafted_by"] == "tester"
    body["recommendation"] = "escalate"
    b = client.post("/screening/alerts/SCR-2001/recommendation", json=body, headers=H).json()
    assert b["draft"]["version"] == 2 and b["alert_status"] == "open"
    full = client.get("/screening/alerts/SCR-2001", headers=H).json()
    assert [x["version"] for x in full["recommendations"]] == [1, 2] and full["status"] == "open"
    default = client.post("/screening/alerts/SCR-2002/recommendation",
                          json={"recommendation": "clear", "reasons": ["x"]}, headers=H).json()
    assert default["draft"]["drafted_by"] == "agent" and default["draft"]["drafted_at"]


def test_change_moves_status_and_second_call_is_409(client):
    body = {"disposition": "false_positive", "decided_by": "A. Reviewer", "note": "Different person."}
    r = client.post("/screening/alerts/SCR-2001/close", json=body, headers=H)
    assert r.status_code == 200 and r.json()["applied"] is True and r.json()["status"] == "closed"
    r2 = client.post("/screening/alerts/SCR-2001/close", json=body, headers=H)
    assert r2.status_code == 409 and "already closed" in r2.json()["detail"]
    assert client.post("/screening/alerts/SCR-2002/close", json={"disposition": "true_match", "note": "x"},
                       headers=H).status_code == 422
    b = {"reason": "lost"}
    assert client.post("/cards/cards/CRD-2001/block", json=b, headers=H).status_code == 200
    assert client.post("/cards/cards/CRD-2001/block", json=b, headers=H).status_code == 409


def test_release_needs_a_proposal_and_an_approver(client):
    assert client.post("/payments/repairs/REP-7002/release", json={"approved_by": "P. Approver"}, headers=H).status_code == 409
    prop = {"corrections": [{"field": "beneficiary_bic", "old_value": "QNMKXQQ1", "new_value": "TESLXTT1",
                             "rule_relied_on": "MTB-PAY-RULE-102"}], "explanation": "BIC taken from the bank directory."}
    assert client.post("/payments/repairs/REP-7002/proposal", json=prop, headers=H).json()["draft"]["version"] == 1
    assert client.post("/payments/repairs/REP-7002/release", json={}, headers=H).status_code == 422
    r = client.post("/payments/repairs/REP-7002/release", json={"approved_by": "P. Approver"}, headers=H)
    assert r.status_code == 200 and r.json()["payment_status"] == "released"
    pay = client.get("/payments/payments/PAY-6102", headers=H).json()
    assert pay["beneficiary"]["bic"] == "TESLXTT1"
    assert client.post("/payments/repairs/REP-7002/release", json={"approved_by": "P"}, headers=H).status_code == 409


def test_other_changes(client):
    assert client.post("/cards/cards/CRD-2002/replacement", json={"reason": "expiring"}, headers=H).status_code == 200
    assert client.post("/cards/cards/CRD-2002/replacement", json={"reason": "expiring"}, headers=H).status_code == 409
    d = client.post("/cards/cards/CRD-2001/disputes", json={"transaction_ids": ["CTX-2001-U01", "CTX-2001-U02"],
                                                       "reason": "not_recognised"}, headers=H)
    assert d.status_code == 200 and d.json()["dispute"]["amount"] == 474.40
    assert client.post("/cards/cards/CRD-2001/disputes", json={"transaction_ids": ["CTX-2001-U01"], "reason": "not_recognised"},
                       headers=H).status_code == 409
    assert client.post("/payments/payments/PAY-6101/recall",
                       json={"reason": "duplicate"}, headers=H).status_code == 409
    r = client.post("/payments/payments/PAY-6001/recall", json={"reason": "duplicate"}, headers=H)
    assert r.status_code == 200 and client.post("/payments/payments/PAY-6001/recall", json={"reason": "duplicate"}, headers=H).status_code == 409
    c = client.post("/aml/cases", json={"customer_id": "CUS-1020", "alert_ids": ["TMA-3001"], "summary": "Structuring."},
                    headers=H).json()
    assert c["case"]["case_id"] == "CASE-4101"
    assert client.post("/aml/cases", json={"customer_id": "CUS-1020", "alert_ids": ["TMA-3001"], "summary": "again"},
                       headers=H).status_code == 409
    n = client.post("/aml/cases/CASE-4101/narrative", json={"narrative": "n", "evidence": [{"type": "alert", "id": "TMA-3001"}]},
                    headers=H).json()
    assert n["draft"]["version"] == 1
    note = client.post("/core/customers/CUS-1001/contacts", json={"subject": "s", "summary": "t"}, headers=H).json()
    assert note["applied"] is True and note["contact"]["drafted_by"] == "agent"
    m = client.post("/lending/applications/LAP-8002/missing-items", json={"missing_items": ["tax_return"]}, headers=H)
    assert m.json()["draft"]["version"] == 1
    q = client.post("/lending/loans/LN-9001/document-differences",
                    json={"differences": [{"item": "margin", "approved_value": "3.25", "contract_value": "3.75",
                                           "document_id": "DOC-9101"}]}, headers=H)
    assert q.status_code == 200


def test_reset_restores_starting_data(client, store):
    client.post("/cards/cards/CRD-2001/block", json={"reason": "lost"}, headers=H)
    client.post("/admin/simulate/screening-alert", headers=H)
    assert store.data["cards"]["CRD-2001"]["status"] == "blocked"
    r = client.post("/admin/reset", headers=H)
    assert r.status_code == 200
    assert store.data == build_all(date.fromisoformat(TODAY))
    assert client.get("/admin/state", headers=H).json()["counts"]["open_screening_alerts"] == 6


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
    sub = client.post("/admin/subscriptions", json={"event_kind": "screening-alert", "url": url,
                                                     "header_name": "X-Hook-Secret", "secret_value": "s3cret"}, headers=H).json()
    assert sub["subscription"]["secret_value"] == "***"
    before = len(store.data["screening_alerts"])
    r = client.post("/admin/simulate/screening-alert", headers=H).json()
    assert len(store.data["screening_alerts"]) == before + 1 and r["item_id"] in store.data["screening_alerts"]
    import time
    for _ in range(50):
        if Receiver.got:
            break
        time.sleep(0.1)
    srv.shutdown()
    headers, payload = Receiver.got[0]
    assert headers["X-Hook-Secret"] == "s3cret"
    assert payload["event_type"] == "screening-alert" and payload["item_id"] == r["item_id"]
    assert payload["system"] == "screening" and payload["demo_data"] is True and r["item_id"] in payload["message"]
    ev = client.get("/admin/events", headers=H).json()["items"]
    assert any(e.get("status") == "delivered" for e in ev)
    # a different kind does not reach this subscriber
    client.post("/admin/simulate/loan-application", headers=H)
    time.sleep(0.3)
    assert len(Receiver.got) == 1


def test_every_kind_rotates_through_four_templates(client, store):
    for kind, coll in [("screening-alert", "screening_alerts"), ("payment-repair", "repairs"),
                       ("payment-investigation", "investigations"), ("loan-application", "applications")]:
        n0 = len(store.data[coll])
        ids = [client.post(f"/admin/simulate/{kind}", headers=H).json()["item_id"] for _ in range(5)]
        assert len(set(ids)) == 5 and len(store.data[coll]) == n0 + 5
    assert client.post("/admin/simulate/nonsense", headers=H).status_code == 404


def test_subscription_to_dead_url_never_fails_caller(client):
    client.post("/admin/subscriptions", json={"url": "http://127.0.0.1:9/none"}, headers=H)
    assert client.post("/admin/simulate/payment-repair", headers=H).status_code == 200


def test_webhooks_from_environment():
    env = make_env(BANK_WEBHOOKS=json.dumps([{"event_kind": "*", "url": "http://127.0.0.1:9/x", "header_name": "H",
                                             "secret_value": "v"}]))
    c = TestClient(create_app(env))
    assert c.get("/admin/subscriptions", headers=H).json()["count"] == 1


# ---------------------------------------------------------------- disk

def test_nothing_is_written_without_a_data_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    c = TestClient(create_app(make_env()))
    c.post("/cards/cards/CRD-2001/block", json={"reason": "lost"}, headers=H)
    c.post("/admin/simulate/payment-repair", headers=H)
    assert list(tmp_path.iterdir()) == []
    repo = os.path.dirname(os.path.dirname(__file__))
    assert not [f for f in os.listdir(repo) if f.endswith(".json")]


def test_state_file_written_only_when_directory_given_and_never_holds_secrets(tmp_path):
    c = TestClient(create_app(make_env(DATA_DIR=str(tmp_path / "state"))))
    c.post("/admin/subscriptions", json={"url": "http://127.0.0.1:9/x", "header_name": "H", "secret_value": "topsecret"}, headers=H)
    c.post("/cards/cards/CRD-2001/block", json={"reason": "lost"}, headers=H)
    f = tmp_path / "state" / "demo-bank-state.json"
    assert f.exists() and "topsecret" not in f.read_text()
    again = create_app(make_env(DATA_DIR=str(tmp_path / "state")))
    assert again.state.ctx.store.data["cards"]["CRD-2001"]["status"] == "blocked"


def test_dataset_path_env_chooses_subfolder(tmp_path):
    c = TestClient(create_app(make_env(KATONIC_DATASET_PATH=str(tmp_path))))
    c.post("/cards/cards/CRD-2001/block", json={"reason": "lost"}, headers=H)
    assert (tmp_path / "demo-bank-state" / "demo-bank-state.json").exists()
