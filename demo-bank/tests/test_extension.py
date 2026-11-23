"""Tests for the fraud, recon and news systems, the regulator's public feed and the three new event kinds."""

import asyncio
import json
import xml.etree.ElementTree as ET
from datetime import date, datetime
from pathlib import Path

import pytest
from openapi_spec_validator import validate

from bank.seed import build_all
from conftest import H, KEY, TODAY

NEW = ["fraud", "recon", "news"]
POLICY_DIR = Path(__file__).resolve().parents[2] / "banking" / "policy-library"


def get(client, path, **kw):
    r = client.get(path, headers=H, **kw)
    assert r.status_code == 200, (path, r.status_code, r.text[:200])
    return r.json()


def post(client, path, body, status=200):
    r = client.post(path, json=body, headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:300])
    return r.json()


# ---------------------------------------------------------------- sign-in, documents, tools

def test_new_systems_need_a_key(client):
    for path in ["/fraud/cases", "/fraud/rules/FRD-RULE-001", "/recon/breaks", "/recon/rules/RECON-RULE-001",
                 "/news/articles", "/news/articles/ART-6001"]:
        assert client.get(path).status_code == 401, path
        assert client.get(path, headers=H).status_code == 200, path
        assert client.get(path, headers={"Authorization": f"Bearer {KEY}"}).status_code == 200, path
    assert client.post("/fraud/cases/FRD-3001/decision", json={"decision": "release", "decided_by": "x"}).status_code == 401
    assert client.post("/recon/breaks/BRK-4001/post", json={"approved_by": "x"}).status_code == 401
    assert client.post("/news/screenings", json={"subject_name": "x"}).status_code == 401
    for s in NEW:
        assert client.post(f"/{s}/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).status_code == 401


def test_new_openapi_documents_are_valid_and_plain(client):
    for s in NEW:
        doc = client.get(f"/{s}/openapi.json").json()
        assert doc["openapi"] == "3.0.3"
        validate(doc)
        text = json.dumps(doc)
        assert "anyOf" not in text and "nullable" not in text and '"type": "null"' not in text, s
        assert "/pages/" not in json.dumps(doc["paths"])


def test_operation_ids_per_new_system_and_total(client):
    expected = {"fraud": {"list_fraud_cases", "get_fraud_case", "get_fraud_rule", "save_fraud_case_summary", "decide_fraud_case"},
                "recon": {"list_reconciliation_breaks", "get_reconciliation_break", "get_reconciliation_rule",
                          "propose_break_resolution", "post_break_resolution"},
                "news": {"search_news", "get_news_article", "save_media_screening_summary"}}
    seen = []
    for s in ["core", "cards", "screening", "aml", "payments", "lending", *NEW]:
        doc = client.get(f"/{s}/openapi.json").json()
        ids = [op["operationId"] for item in doc["paths"].values() for op in item.values()]
        seen += ids
        if s in expected:
            assert set(ids) == expected[s], s
            for item in doc["paths"].values():
                for op in item.values():
                    assert op["description"].strip() and len(op["description"]) > 60
    assert len(seen) == len(set(seen)) == 66


def test_landing_page_lists_new_systems_and_the_regulator(client):
    text = client.get("/").text
    assert "The nine systems" in text
    for s in NEW:
        assert f"/{s}/openapi.json" in text and f"/{s}/mcp" in text and f"/{s}/docs" in text
    section = text.split("A regulator's public website")[1]
    assert "invented" in section[:300].lower() and "/regulator/feed.xml" in section and "no MCP address" in section
    assert "/regulator/mcp" not in text
    assert client.get("/regulator/mcp", headers=H).status_code == 404


# ---------------------------------------------------------------- data

def test_new_data_links_to_existing_records(store):
    d = store.data
    assert len(d["news_articles"]) == 25 and len(d["regulator_publications"]) == 6
    for c in d["fraud_cases"].values():
        assert c["customer_id"] in d["customers"] and c["account_id"] in d["accounts"]
        assert d["accounts"][c["account_id"]]["customer_id"] == c["customer_id"]
        assert c["rule_id"] in d["fraud_rules"]
        if c["card_id"]:
            assert d["cards"][c["card_id"]]["customer_id"] == c["customer_id"]
        for i in c["flagged_items"]:
            coll = d["card_transactions"] if i["kind"] == "card_payment" else d["payments"]
            assert i["id"] in coll and coll[i["id"]]["customer_id" if i["kind"] == "payment" else "card_id"]
            if i["kind"] == "payment":
                assert coll[i["id"]]["customer_id"] == c["customer_id"]
            else:
                assert coll[i["id"]]["card_id"] == c["card_id"]
    for b in d["recon_breaks"].values():
        assert b["account_id"] in d["recon_accounts"]
        ids = [b["entry_id"]] + [c["entry_id"] for c in b["candidates"]]
        for eid in ids:
            e = d["recon_ledger"].get(eid) or d["recon_statement"][eid]
            assert e["account_id"] == b["account_id"]
    assert store.counts()["open_fraud_cases"] == 4 and store.counts()["open_reconciliation_breaks"] == 5
    assert store.counts()["news_articles"] == 25 and store.counts()["regulator_publications"] == 6


def test_data_has_no_real_countries_and_only_invented_outlets(store):
    outlets = {a["outlet"] for a in store.data["news_articles"].values()}
    assert outlets == {"The Meridia Courier", "Port Ilvane Business Daily"}
    allowed = {"XM", "XA", "XB", "XQ", "XR", "XT", "QN", "QP"}
    for p in store.data["payments"].values():
        assert p["beneficiary"]["country"] in allowed
    for t in store.data["card_transactions"].values():
        assert t.get("country", "XM") in allowed
    for c in store.data["fraud_cases"].values():
        assert c["channel_details"].get("ip_country", "XM") in allowed | {"XB"}


# ---------------------------------------------------------------- fraud scenarios

def test_fraud_case_1_card_not_present_abroad_at_night(client):
    c = get(client, "/fraud/cases/FRD-3001")
    assert c["rule"]["rule_id"] == "FRD-RULE-001" and c["customer"]["customer_id"] == "CUS-1012"
    items = c["flagged_items"]
    assert len(items) == 3 and all(i["kind"] == "card_payment" and not i["card_present"] and i["merchant_country"] == "QN"
                                   for i in items)
    assert all("02:00" <= i["time"] < "04:00" for i in items) and round(sum(i["amount"] for i in items), 2) == 2219.90
    home = [x for x in c["earlier_contacts"] if "home" in x["summary"]]
    assert len(home) == 2 and c["channel_details"]["card_present"] is False
    others = get(client, "/cards/cards/CRD-2008/transactions")["items"]
    assert all(t.get("country", "XM") == "XM" for t in others if t["card_transaction_id"] not in {i["id"] for i in items})
    assert c["earlier_fraud_cases"] == [] and c["status"] == "open" and c["decision"] is None


def test_fraud_case_2_confirmed_by_phone(client):
    c = get(client, "/fraud/cases/FRD-3002")
    p = c["flagged_items"][0]
    assert p["id"] == "PAY-6401" and p["amount"] == 18500.0 and p["status"] == "held"
    call = [x for x in c["earlier_contacts"] if x["direction"] == "outbound"][0]
    assert "added the payee himself" in call["summary"] and "read back the payee name and the amount" in call["summary"]
    pays = get(client, "/payments/payments?customer_id=CUS-1015")["items"]
    assert [x["beneficiary_name"] for x in pays if x["beneficiary_name"] == "Brookhaven Joinery Works"] == ["Brookhaven Joinery Works"]
    assert c["earlier_fraud_cases"][0]["decision"]["decision"] == "release"


def test_fraud_case_3_account_takeover_within_the_hour(client):
    c = get(client, "/fraud/cases/FRD-3003")
    ev = c["security_events"]
    assert [e["event"] for e in ev] == ["new_device_signed_in", "password_reset", "payee_added", "payment_made"]
    t = [datetime.strptime(e["time"], "%Y-%m-%d %H:%M") for e in ev]
    assert t == sorted(t) and (t[-1] - t[0]).total_seconds() / 60 < 60
    assert c["channel_details"]["device_seen_before"] is False and c["rule"]["rule_id"] == "FRD-RULE-003"
    assert c["flagged_items"][0]["id"] == "PAY-6402" and c["flagged_items"][0]["amount"] == 7400.0


def test_fraud_case_4_subscription_belongs_with_disputes(client):
    c = get(client, "/fraud/cases/FRD-3004")
    flagged = c["flagged_items"][0]
    assert flagged["merchant"] == "Streamline Video Club" and flagged["amount"] == 11.99
    rows = get(client, f"/cards/cards/{flagged['card_id']}/transactions")["items"]
    same = [t for t in rows if t["merchant"] == "Streamline Video Club" and t["card_transaction_id"] != flagged["id"]]
    assert len(same) == 3 and all(t["amount"] == 11.99 for t in same)
    assert c["earlier_fraud_cases"][0]["case_id"] == "FRD-2901" and c["earlier_fraud_cases"][0]["status"] == "decided"


def test_fraud_list_and_rule(client):
    assert get(client, "/fraud/cases")["count"] == 6
    ids = {x["case_id"] for x in get(client, "/fraud/cases?status=open")["items"]}
    assert ids == {"FRD-3001", "FRD-3002", "FRD-3003", "FRD-3004"}
    assert {x["case_id"] for x in get(client, "/fraud/cases?status=decided")["items"]} == {"FRD-2901", "FRD-2902"}
    assert get(client, "/fraud/rules/FRD-RULE-002")["text"]
    assert client.get("/fraud/rules/FRD-RULE-999", headers=H).status_code == 404
    assert client.get("/fraud/cases/FRD-0000", headers=H).status_code == 404


def test_fraud_summary_is_a_draft_with_versions(client):
    body = {"summary": "Card abroad at night.", "recommended_action": "refund", "customer_message": "We have blocked your card.",
            "drafted_by": "tester"}
    a = post(client, "/fraud/cases/FRD-3001/summary", body)
    assert a["applied"] is True and a["kind"] == "draft" and a["draft"]["version"] == 1 and a["draft"]["drafted_by"] == "tester"
    assert a["draft"]["drafted_at"] and a["case_status"] == "open"
    body["recommended_action"] = "block"
    del body["drafted_by"]
    b = post(client, "/fraud/cases/FRD-3001/summary", body)
    assert b["draft"]["version"] == 2 and b["draft"]["drafted_by"] == "agent"
    full = get(client, "/fraud/cases/FRD-3001")
    assert [s["version"] for s in full["summaries"]] == [1, 2] and full["status"] == "open"
    assert client.post("/fraud/cases/FRD-3001/summary", json={"summary": "x", "recommended_action": "maybe"},
                       headers=H).status_code == 422


def test_fraud_decisions_change_things_and_refuse_a_second_time(client, store):
    assert client.post("/fraud/cases/FRD-3001/decision", json={"decision": "refund"}, headers=H).status_code == 422
    r = post(client, "/fraud/cases/FRD-3001/decision", {"decision": "refund", "decided_by": "A. Reviewer"})
    assert r["applied"] is True and r["status"] == "decided" and r["decision"]["decided_by"] == "A. Reviewer"
    assert store.data["cards"]["CRD-2008"]["status"] == "blocked" and store.data["cards"]["CRD-2008"]["block_reason"] == "fraud"
    assert {store.data["card_transactions"][i]["status"] for i in ("CTX-2008-F01", "CTX-2008-F02", "CTX-2008-F03")} == {"refunded"}
    again = client.post("/fraud/cases/FRD-3001/decision", json={"decision": "release", "decided_by": "B"}, headers=H)
    assert again.status_code == 409 and "already decided" in again.json()["detail"] and again.json()["applied"] is False
    assert client.post("/fraud/cases/FRD-3001/summary", json={"summary": "x", "recommended_action": "block"},
                       headers=H).status_code == 409
    assert client.post("/cards/cards/CRD-2008/block", json={"reason": "fraud"}, headers=H).status_code == 409

    post(client, "/fraud/cases/FRD-3002/decision", {"decision": "release", "decided_by": "A. Reviewer"})
    assert store.data["payments"]["PAY-6401"]["status"] == "released"

    post(client, "/fraud/cases/FRD-3003/decision", {"decision": "refund", "decided_by": "A. Reviewer"})
    assert store.data["payments"]["PAY-6402"]["status"] == "recall_requested"
    assert store.data["customers"]["CUS-1014"]["online_banking"] == "blocked"

    post(client, "/fraud/cases/FRD-3004/decision", {"decision": "release", "decided_by": "A. Reviewer", "note": "A dispute."})
    assert store.data["cards"]["CRD-2006"]["status"] == "active"
    assert get(client, "/fraud/cases?status=open")["count"] == 0
    assert get(client, "/admin/state")["counts"]["open_fraud_cases"] == 0


# ---------------------------------------------------------------- recon scenarios

def distance(a, b):
    assert len(a) == len(b)
    return sum(x != y for x, y in zip(a, b))


def test_recon_break_1_one_mistyped_character(client):
    b = get(client, "/recon/breaks/BRK-4001")
    item = b["statement_side"][0]
    assert b["ledger_side"] == [] and b["missing_side"] == "ledger" and b["age_days"] == 5
    likely = [c for c in b["candidates"] if c["likely"]]
    assert [c["entry_id"] for c in likely] == ["LED-7101"] and all(c["reason"] for c in b["candidates"])
    cand = likely[0]["entry"]
    assert cand["amount"] == item["amount"] and b["amount_difference"] == 0
    assert distance(cand["reference"], item["reference"]) == 1
    assert (date.fromisoformat(item["value_date"]) - date.fromisoformat(cand["value_date"])).days == 1
    assert len(b["candidates"]) == 2 and b["rules"] and b["auto_match_checks"]


def test_recon_break_2_one_statement_to_two_ledger_entries(client):
    b = get(client, "/recon/breaks/BRK-4002")
    likely = [c for c in b["candidates"] if c["likely"]]
    assert sorted(c["entry_id"] for c in likely) == ["LED-7201", "LED-7202"]
    assert sum(c["entry"]["amount"] for c in likely) == b["statement_side"][0]["amount"] == 8000.0
    assert {c["entry"]["batch_id"] for c in likely} == {"BATCH-0457"} and b["amount_difference"] == 0


def test_recon_break_3_bank_charge(client):
    b = get(client, "/recon/breaks/BRK-4003")
    assert b["amount_difference"] == -15.0 and b["candidates"][0]["entry"]["reference"] == b["statement_side"][0]["reference"]
    assert "15.00" in b["statement_side"][0]["narrative"]
    assert "GL-6120" in get(client, "/recon/rules/RECON-RULE-003")["text"]


def test_recon_break_4_duplicate_posting(client):
    b = get(client, "/recon/breaks/BRK-4004")
    item, orig = b["ledger_side"][0], b["candidates"][0]["entry"]
    assert b["item_side"] == "ledger" and b["missing_side"] == "statement" and orig["status"] == "matched"
    for k in ("account_id", "amount", "value_date", "reference", "batch_id", "direction"):
        assert item[k] == orig[k], k
    assert item["entry_id"] != orig["entry_id"] and item["posted_at"] > orig["posted_at"]
    assert b["candidates"][0]["side"] == "ledger"


def test_recon_break_5_cannot_be_resolved(client):
    b = get(client, "/recon/breaks/BRK-4005")
    assert b["candidates"] == [] and b["amount_difference"] is None and b["ledger_side"] == []
    assert b["age_days"] == 9 and len(b["auto_match_checks"]) >= 3
    r5 = get(client, "/recon/rules/RECON-RULE-005")
    assert "refer" in r5["text"].lower()


def test_recon_list_filters_and_rules(client):
    assert get(client, "/recon/breaks")["count"] == 6
    openb = get(client, "/recon/breaks?status=open")
    assert openb["count"] == 5 and openb["items"][0]["age_days"] >= openb["items"][-1]["age_days"]
    assert [x["break_id"] for x in get(client, "/recon/breaks?status=resolved")["items"]] == ["BRK-3901"]
    assert {x["break_id"] for x in get(client, "/recon/breaks?account=NOS-QNMK-01")["items"]} == {"BRK-4002", "BRK-4005"}
    assert len({get(client, f"/recon/rules/RECON-RULE-00{n}")["rule_id"] for n in range(1, 6)}) == 5
    assert client.get("/recon/rules/RECON-RULE-099", headers=H).status_code == 404
    assert client.get("/recon/breaks/BRK-0", headers=H).status_code == 404


def proposal(**kw):
    base = {"resolution": "match", "matched_entry_ids": ["LED-7101"], "evidence": ["LED-7101 has the same amount."],
            "rule_relied_on": "RECON-RULE-001", "explanation": "x", "drafted_by": "tester"}
    base.update(kw)
    return base


def test_recon_proposal_is_a_draft_with_versions(client):
    a = post(client, "/recon/breaks/BRK-4001/proposal", proposal())
    assert a["applied"] is True and a["kind"] == "draft" and a["draft"]["version"] == 1 and a["break_status"] == "open"
    b = post(client, "/recon/breaks/BRK-4001/proposal", proposal(explanation="second"))
    assert b["draft"]["version"] == 2
    full = get(client, "/recon/breaks/BRK-4001")
    assert [p["version"] for p in full["proposals"]] == [1, 2] and full["status"] == "open"
    assert client.post("/recon/breaks/BRK-4001/proposal", json=proposal(rule_relied_on="NOPE"), headers=H).status_code == 422
    assert client.post("/recon/breaks/BRK-4001/proposal", json=proposal(matched_entry_ids=["LED-0000"]), headers=H).status_code == 404
    assert client.post("/recon/breaks/BRK-4001/proposal", json=proposal(matched_entry_ids=["LED-6006"]), headers=H).status_code == 404
    assert client.post("/recon/breaks/BRK-4001/proposal", json=proposal(resolution="match_with_adjustment"), headers=H).status_code == 422
    assert client.post("/recon/breaks/BRK-4001/proposal", json=proposal(resolution="reverse_duplicate", matched_entry_ids=[]),
                       headers=H).status_code == 422


def test_recon_post_needs_a_proposal_and_an_approver_and_refuses_twice(client, store):
    assert client.post("/recon/breaks/BRK-4001/post", json={"approved_by": "P. Approver"}, headers=H).status_code == 409
    post(client, "/recon/breaks/BRK-4001/proposal", proposal())
    assert client.post("/recon/breaks/BRK-4001/post", json={}, headers=H).status_code == 422
    r = post(client, "/recon/breaks/BRK-4001/post", {"approved_by": "P. Approver"})
    assert r["applied"] is True and r["status"] == "resolved" and r["resolution"]["approved_by"] == "P. Approver"
    assert store.data["recon_ledger"]["LED-7101"]["status"] == "matched"
    assert store.data["recon_statement"]["STM-8101"]["status"] == "matched"
    again = client.post("/recon/breaks/BRK-4001/post", json={"approved_by": "P"}, headers=H)
    assert again.status_code == 409 and "already resolved" in again.json()["detail"]
    assert client.post("/recon/breaks/BRK-4001/proposal", json=proposal(), headers=H).status_code == 409
    assert get(client, "/admin/state")["counts"]["open_reconciliation_breaks"] == 4


def test_recon_one_to_many_adjustment_and_reversal(client, store):
    post(client, "/recon/breaks/BRK-4002/proposal", proposal(matched_entry_ids=["LED-7201", "LED-7202"],
                                                             rule_relied_on="RECON-RULE-002"))
    post(client, "/recon/breaks/BRK-4002/post", {"approved_by": "P"})
    assert {store.data["recon_ledger"][i]["status"] for i in ("LED-7201", "LED-7202")} == {"matched"}

    post(client, "/recon/breaks/BRK-4003/proposal", proposal(
        resolution="match_with_adjustment", matched_entry_ids=["LED-7301"], adjusting_debit_account="GL-6120",
        adjusting_credit_account="NOS-TESL-01", adjusting_amount=15.0, rule_relied_on="RECON-RULE-003"))
    r = post(client, "/recon/breaks/BRK-4003/post", {"approved_by": "P"})
    new = store.data["recon_ledger"][r["resolution"]["entries_created"][0]]
    assert new["amount"] == 15.0 and new["debit_account"] == "GL-6120" and new["credit_account"] == "NOS-TESL-01"

    post(client, "/recon/breaks/BRK-4004/proposal", {"resolution": "reverse_duplicate", "reverse_entry_id": "LED-7402",
                                                      "evidence": ["Same reference, amount and batch as LED-7401."],
                                                      "rule_relied_on": "RECON-RULE-004"})
    r = post(client, "/recon/breaks/BRK-4004/post", {"approved_by": "P"})
    rev = store.data["recon_ledger"][r["resolution"]["entries_created"][0]]
    assert rev["direction"] == "credit" and rev["amount"] == 4175.50 and store.data["recon_ledger"]["LED-7402"]["status"] == "reversed"
    assert store.data["recon_ledger"]["LED-7401"]["status"] == "matched"


def test_recon_referral_cannot_be_posted(client):
    post(client, "/recon/breaks/BRK-4005/proposal", {"resolution": "refer_to_person", "evidence": [
        "No ledger entry has the amount 3,275.40 within 5 days.", "No reference matches UNK-77QX."]})
    r = client.post("/recon/breaks/BRK-4005/post", json={"approved_by": "P"}, headers=H)
    assert r.status_code == 409 and "refers it to a person" in r.json()["detail"]
    assert get(client, "/recon/breaks/BRK-4005")["status"] == "open"


# ---------------------------------------------------------------- news

def ids(client, text, **q):
    rows = get(client, "/news/articles", params={"text": text, **q})
    return [x["article_id"] for x in rows["items"]]


def test_news_search_is_newest_first_and_filters(client):
    assert get(client, "/news/articles?limit=100")["total_matches"] == 25
    assert ids(client, "Orrenmoor") == ["ART-6002", "ART-6001"]
    assert ids(client, "orrenmoor valdis") == ["ART-6002", "ART-6001"]
    assert ids(client, "Karn Harbour") == ["ART-6004", "ART-6003"]
    assert ids(client, "Vanhollow") == ["ART-6006", "ART-6005"]
    assert ids(client, "zzzz-nothing") == []
    rows = get(client, "/news/articles", params={"limit": 100})["items"]
    dates = [r["date"] for r in rows]
    assert dates == sorted(dates, reverse=True) and len(get(client, "/news/articles?limit=3")["items"]) == 3
    cut = get(client, "/news/articles/ART-6002")["date"]
    assert ids(client, "Orrenmoor", date_from=cut) == ["ART-6002"]
    assert ids(client, "Orrenmoor", date_to=cut) == ["ART-6002", "ART-6001"]
    body_only = ids(client, "dredging")
    assert body_only and "ART-6017" in body_only


def test_news_article_has_page_url_and_page_opens_without_a_key(client):
    a = get(client, "/news/articles/ART-6001")
    assert a["outlet"] == "The Meridia Courier" and "Orrenmoor" in a["body"] and a["page_url"] == "http://testserver/news/pages/ART-6001"
    page = client.get("/news/pages/ART-6001")
    assert page.status_code == 200 and "text/html" in page.headers["content-type"] and "Orrenmoor" in page.text
    assert "http://" not in page.text and "https://" not in page.text and "cdn" not in page.text.lower()
    assert client.get("/news/pages/ART-9999").status_code == 404
    assert client.get("/news/articles/ART-9999", headers=H).status_code == 404
    assert "/pages/" not in json.dumps(client.get("/news/openapi.json").json())
    assert get(client, "/news/articles?text=Orrenmoor")["items"][0]["page_url"].startswith("http://testserver/news/pages/ART-")


def test_news_page_url_under_a_prefix_and_through_mcp():
    from fastapi.testclient import TestClient
    from bank.app import create_app
    from conftest import make_env
    c = TestClient(create_app(make_env()), root_path="/apps/demo-bank")
    a = c.get("/apps/demo-bank/news/articles/ART-6001", headers=H).json()
    assert a["page_url"] == "http://testserver/apps/demo-bank/news/pages/ART-6001"
    body = {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "get_news_article", "arguments": {"article_id": "ART-6001"}}}
    r = c.post("/apps/demo-bank/news/mcp", json=body, headers=H).json()
    assert json.loads(r["result"]["content"][0]["text"])["page_url"] == "http://testserver/apps/demo-bank/news/pages/ART-6001"


def test_news_subject_tables(store, client):
    """The subjects in SCENARIOS.md: which articles are adverse and about the subject, namesakes, neutral."""
    cust = {c["name"]: c for c in store.data["customers"].values()}

    def mentions(name):
        words = name.lower().split()
        return sorted(a["article_id"] for a in store.data["news_articles"].values()
                      if all(w in (a["title"] + " " + a["body"]).lower() for w in words))

    assert mentions("Valdis Orrenmoor") == ["ART-6001", "ART-6002"]
    assert "1971" in store.data["news_articles"]["ART-6001"]["body"] and "Port Ilvane" in store.data["news_articles"]["ART-6001"]["body"]
    assert cust["Valdis Orrenmoor"]["date_of_birth"].startswith("1971")
    assert mentions("Karn Harbour Freight Agency") == ["ART-6003", "ART-6004"]
    assert mentions("Leopold Vanhollow") == ["ART-6005", "ART-6006"]
    assert mentions("Perdita Vanhollow") == []
    namesakes = {"Ilvane Marrowick": ("ART-6007", "63", "Brevnia"), "Wynne Castellane": ("ART-6008", "54", "Tessaly"),
                 "Oskar Brindlemoor": ("ART-6009", "19", "Norvania"), "Sabine Tarrowgate": ("ART-6010", "71", "Aldoria"),
                 "Harrowgate Bakery Supplies Ltd": ("ART-6011", "Hartsfell", "Quenmark")}
    for name, (aid, fact1, fact2) in namesakes.items():
        assert mentions(name) == [aid], name
        body = store.data["news_articles"][aid]["body"]
        assert fact1 in body and fact2 in body
    assert cust["Ilvane Marrowick"]["date_of_birth"] == "1984-03-12" and cust["Ilvane Marrowick"]["nationality"] == "XM"
    neutral = {"Pinecrest Tooling Works Ltd": "ART-6012", "Lanternfish Logistics Ltd": "ART-6013",
               "Saltmarsh Catering Co": "ART-6014", "Marguerite Oakhaven": "ART-6015"}
    for name, aid in neutral.items():
        assert mentions(name.replace(" Ltd", "")) == [aid], name
    named = set(sum(([a] for a in ["ART-6001", "ART-6002", "ART-6003", "ART-6004", "ART-6005", "ART-6006"]), []))
    noise = [a for a in store.data["news_articles"] if a >= "ART-6016"]
    assert len(noise) == 10
    for cname in cust:
        for aid in noise:
            assert cname.lower() not in (store.data["news_articles"][aid]["body"]).lower(), (cname, aid)
    assert named.isdisjoint(noise)


def test_media_screening_summary_is_a_draft_with_versions(client, store):
    body = {"subject_name": "Valdis Orrenmoor", "customer_id": "CUS-1007", "conclusion": "Adverse.",
            "findings": [{"article_id": "ART-6001", "relevance": "about_subject", "adverse": True,
                          "reason": "Born 1971, lives in Port Ilvane."}], "drafted_by": "tester"}
    a = post(client, "/news/screenings", body)
    assert a["applied"] is True and a["kind"] == "draft" and a["draft"]["version"] == 1 and a["draft"]["drafted_by"] == "tester"
    assert a["screening_id"].startswith("MS-") and a["draft"]["drafted_at"]
    b = post(client, "/news/screenings", {**body, "conclusion": "Adverse, confirmed."})
    assert b["draft"]["version"] == 2 and b["screening_id"] == a["screening_id"]
    other = post(client, "/news/screenings", {"subject_name": "Ilvane Marrowick", "customer_id": "CUS-1001", "findings": [
        {"article_id": "ART-6007", "relevance": "not_about_subject", "reason": "Aged 63, a skipper from Corrowick in Brevnia."}]})
    assert other["screening_id"] != a["screening_id"] and other["draft"]["version"] == 1 and other["draft"]["drafted_by"] == "agent"
    saved = store.data["media_screenings"][a["screening_id"]]
    assert [s["version"] for s in saved["summaries"]] == [1, 2]
    assert client.post("/news/screenings", json={**body, "customer_id": "CUS-9999"}, headers=H).status_code == 404
    assert client.post("/news/screenings", json={"subject_name": "x", "findings": [
        {"article_id": "ART-0", "relevance": "unclear", "reason": "x"}]}, headers=H).status_code == 404
    assert client.post("/news/screenings", json={"subject_name": "x", "findings": [
        {"article_id": "ART-6001", "relevance": "maybe", "reason": "x"}]}, headers=H).status_code == 422


# ---------------------------------------------------------------- the regulator

def feed_items(client):
    r = client.get("/regulator/feed.xml")
    assert r.status_code == 200
    root = ET.fromstring(r.content)
    assert root.tag == "rss" and root.attrib["version"] == "2.0"
    return r, root.find("channel"), root.findall("./channel/item")


def test_feed_needs_no_key_and_is_well_formed_rss(client):
    r, channel, items = feed_items(client)
    assert "xml" in r.headers["content-type"] and r.headers["x-demo-data"] == "invented"
    assert "invented" in channel.find("title").text.lower() and len(items) == 6
    for it in items:
        assert [c.tag for c in it] == ["title", "link", "pubDate", "guid", "description"]
        assert it.find("guid").text.startswith("MFCA-2026-") and it.find("link").text.startswith("http://testserver/regulator/publications/")
        assert it.find("description").text.strip()
    dates = [datetime.strptime(it.find("pubDate").text, "%a, %d %b %Y %H:%M:%S %z") for it in items]
    assert dates == sorted(dates, reverse=True)
    today = date.fromisoformat(TODAY)
    assert all(0 <= (today - d.date()).days <= 60 for d in dates)
    assert client.get("/regulator/publications.json").status_code == 200
    assert client.get("/regulator/publications/MFCA-2026-045").status_code == 200


def test_publications_json_matches_the_feed_and_pages_have_numbered_paragraphs(client):
    _, _, items = feed_items(client)
    j = client.get("/regulator/publications.json").json()
    assert j["demo_data"] is True and j["count"] == 6
    assert [x["id"] for x in j["items"]] == [it.find("guid").text for it in items]
    assert [x["title"] for x in j["items"]] == [it.find("title").text for it in items]
    assert [x["link"] for x in j["items"]] == [it.find("link").text for it in items]
    page = client.get("/regulator/publications/MFCA-2026-045")
    assert "text/html" in page.headers["content-type"] and "<b>1.</b>" in page.text and "<b>5.</b>" in page.text
    assert "consent" in page.text and "dispute" in page.text and "invented" in page.text.lower()
    assert client.get("/regulator/publications/MFCA-2026-999").status_code == 404


def test_publications_give_the_known_results_against_the_policies(client, store):
    pubs = store.data["regulator_publications"]
    text = {k: " ".join(v["paragraphs"]).lower() for k, v in pubs.items()}
    assert pubs["MFCA-2026-045"]["binding"] and all(w in text["MFCA-2026-045"] for w in ("consent", "data format", "dispute"))
    assert "supplier" in text["MFCA-2026-036"] and "artificial intelligence" in text["MFCA-2026-036"]
    assert "four hours" in text["MFCA-2026-040"] and "incident" in text["MFCA-2026-040"]
    assert "reviews every output" in text["MFCA-2026-033"] and "name of the person who reviewed" in text["MFCA-2026-033"]
    assert "banknotes" in text["MFCA-2026-029"] and "policy" not in text["MFCA-2026-029"]
    assert pubs["MFCA-2026-043"]["binding"] is False and "not binding" in text["MFCA-2026-043"]
    assert sum(1 for p in pubs.values() if not p["binding"]) == 1
    kinds = {k: v["kind"] for k, v in pubs.items()}
    assert kinds["MFCA-2026-043"] == "consultation paper" and kinds["MFCA-2026-045"] == "circular"


@pytest.mark.skipif(not POLICY_DIR.exists(), reason="the policy library is not next to this folder")
def test_policy_clauses_the_publications_are_marked_against():
    def read(name):
        return next(POLICY_DIR.glob(f"{name}*.md")).read_text(encoding="utf-8")

    pol21, pol33, std41, pol14 = read("MTB-POL-021"), read("MTB-POL-033"), read("MTB-STD-041"), read("MTB-POL-014")
    assert "7.1 The bank does not currently share customer information with other financial institutions" in pol21
    assert "consent mechanism, a data format and a dispute process" in pol21
    assert "7.1 This policy does not set out how the bank assesses a provider's own use of artificial intelligence" in pol33
    assert "8.1 This standard does not set out how the bank assesses a supplier's own use of artificial intelligence" in std41
    assert "within the period the regulator sets" in pol33
    assert "5.2 A person reviews every customer-facing output of a generative AI model before it is sent. The reviewer's name is recorded." in pol14
    assert "5.3 Staff are told which systems use AI" in pol14
    assert "7.2 This policy does not set out how customers are told that AI was used" in pol14


def test_simulated_publication_appears_in_the_feed(client, store):
    seen = []
    for n in range(5):
        r = post(client, "/admin/simulate/regulator-publication", {})
        assert r["event_type"] == "regulator-publication" and r["system"] == "regulator"
        assert r["item_id"] in r["message"] and "invented" in r["message"].lower()
        seen.append(r["item_id"])
        _, _, items = feed_items(client)
        assert len(items) == 6 + n + 1
        assert items[0].find("guid").text == r["item_id"] or items[0].find("guid").text in seen
        assert r["item_id"] in [it.find("guid").text for it in items]
        assert client.get(f"/regulator/publications/{r['item_id']}").status_code == 200
    assert len(set(seen)) == 5
    titles = [store.data["regulator_publications"][i]["title"] for i in seen]
    assert len(set(titles[:4])) == 4 and titles[4] == titles[0]


# ---------------------------------------------------------------- events

def test_new_kinds_rotate_through_four_templates(client, store):
    for kind, coll, system in [("fraud-case", "fraud_cases", "fraud"), ("reconciliation-break", "recon_breaks", "recon"),
                               ("regulator-publication", "regulator_publications", "regulator")]:
        n0 = len(store.data[coll])
        out = [post(client, f"/admin/simulate/{kind}", {}) for _ in range(5)]
        ids_ = [o["item_id"] for o in out]
        assert len(set(ids_)) == 5 and len(store.data[coll]) == n0 + 5
        assert all(o["system"] == system and o["item_id"] in o["message"] for o in out)
        assert all(o["message"].endswith(".") and "  " not in o["message"] and chr(0x2014) not in o["message"] for o in out)
    created = [e for e in get(client, "/admin/events")["items"] if e["status"] == "created"]
    assert {e["event_type"] for e in created} == {"fraud-case", "reconciliation-break", "regulator-publication"}


def test_simulated_fraud_cases_are_complete_and_readable(client, store):
    shapes = []
    for _ in range(4):
        r = post(client, "/admin/simulate/fraud-case", {})
        c = get(client, f"/fraud/cases/{r['item_id']}")
        assert c["status"] == "open" and c["flagged_items"] and c["rule"]["text"] and c["customer"]["name"]
        shapes.append((c["rule_id"], len(c["security_events"])))
        for i in c["flagged_items"]:
            assert i["amount"] > 0 and i["status"]
    assert shapes == [("FRD-RULE-001", 0), ("FRD-RULE-003", 4), ("FRD-RULE-004", 0), ("FRD-RULE-002", 0)]
    third = [c for c in store.data["fraud_cases"].values() if c["case_id"].startswith("FRD-31")][2]
    rows = get(client, f"/cards/cards/{third['card_id']}/transactions")["items"]
    merchant = store.data["card_transactions"][third["flagged_items"][0]["id"]]["merchant"]
    assert len([t for t in rows if t["merchant"] == merchant]) == 4


def test_simulated_breaks_are_complete_and_readable(client):
    shapes = []
    for _ in range(4):
        r = post(client, "/admin/simulate/reconciliation-break", {})
        b = get(client, f"/recon/breaks/{r['item_id']}")
        assert b["status"] == "open" and b["rules"]
        shapes.append((b["item_side"], len(b["candidates"]), b["amount_difference"]))
    assert shapes == [("statement", 1, 0), ("statement", 1, -12.5), ("ledger", 1, 0), ("statement", 0, None)]


def test_new_kinds_can_be_subscribed_to(client):
    for kind in ("fraud-case", "reconciliation-break", "regulator-publication"):
        r = post(client, "/admin/subscriptions", {"event_kind": kind, "url": "http://127.0.0.1:9/x"})
        assert r["subscription"]["event_kind"] == kind
    assert client.post("/admin/subscriptions", json={"event_kind": "nonsense", "url": "http://127.0.0.1:9/x"},
                       headers=H).status_code == 422


def test_reset_restores_the_new_data(client, store):
    post(client, "/fraud/cases/FRD-3001/decision", {"decision": "refund", "decided_by": "x"})
    post(client, "/recon/breaks/BRK-4005/proposal", {"resolution": "refer_to_person", "evidence": ["x"]})
    post(client, "/news/screenings", {"subject_name": "Someone"})
    post(client, "/admin/simulate/regulator-publication", {})
    post(client, "/admin/simulate/fraud-case", {})
    assert len(store.data["regulator_publications"]) == 7
    assert post(client, "/admin/reset", {})["applied"] is True
    assert store.data == build_all(date.fromisoformat(TODAY))
    counts = get(client, "/admin/state")["counts"]
    assert counts["open_fraud_cases"] == 4 and counts["regulator_publications"] == 6 and counts["open_reconciliation_breaks"] == 5
    assert len(feed_items(client)[2]) == 6


def test_state_file_from_an_older_version_still_loads(tmp_path):
    from fastapi.testclient import TestClient
    from bank.app import create_app
    from conftest import make_env
    env = make_env(DATA_DIR=str(tmp_path / "state"))
    c = TestClient(create_app(env))
    c.post("/cards/cards/CRD-2001/block", json={"reason": "lost"}, headers=H)
    f = tmp_path / "state" / "demo-bank-state.json"
    saved = json.loads(f.read_text())
    for k in ("fraud_cases", "recon_breaks", "news_articles", "regulator_publications"):
        saved["data"].pop(k)
    f.write_text(json.dumps(saved))
    again = TestClient(create_app(env))
    assert again.get("/fraud/cases", headers=H).json()["count"] == 6 and again.get("/regulator/feed.xml").status_code == 200
