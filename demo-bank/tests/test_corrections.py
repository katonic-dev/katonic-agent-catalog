"""Tests for the corrections: alert investigations, monitoring arrivals, places of birth and addresses, the screening
vocabulary, card payment places, investigation rules, payment search, reconciliation entries, loan instalments,
the lending descriptions, and the agreement of the records that state the same fact."""

import json
import re
from datetime import date, timedelta
from pathlib import Path

import pytest

from bank.seed import build_all
from conftest import H, TODAY

TODAY_D = date.fromisoformat(TODAY)
ROOT = Path(__file__).resolve().parent.parent
DASH = chr(0x2014)
PLAIN = lambda m: m.endswith(".") and "  " not in m and DASH not in m and "\n" not in m


def get(client, path, status=200, **kw):
    r = client.get(path, headers=H, **kw)
    assert r.status_code == status, (path, r.status_code, r.text[:300])
    return r.json()


def post(client, path, body=None, status=200):
    r = client.post(path, json=body or {}, headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:400])
    return r.json()


def investigation(narrative="Seven cash deposits just under the threshold.", recommendation="open_case", evidence=("TXN-S3001-01",),
                  drafted_by="tester"):
    return {"findings": [{"finding": "Cash deposits of USD 9,100 to 9,800.", "evidence_ids": list(evidence)}],
            "narrative": narrative, "recommendation": recommendation, "drafted_by": drafted_by}


# ---------------------------------------------------------------- 1. alert investigations

def test_investigation_is_a_draft_with_who_when_and_versions(client):
    a = post(client, "/aml/alerts/TMA-3001/investigation", investigation())
    assert a["applied"] is True and a["kind"] == "draft" and a["alert_status"] == "open"
    assert a["draft"]["version"] == 1 and a["draft"]["drafted_by"] == "tester" and a["draft"]["drafted_at"]
    b = post(client, "/aml/alerts/TMA-3001/investigation",
             investigation(narrative="Second version.", recommendation="no_case", evidence=("MTB-AML-RULE-001", "CNT-5008")))
    assert b["draft"]["version"] == 2
    full = get(client, "/aml/alerts/TMA-3001")
    drafts = full["investigation_drafts"]
    assert [x["version"] for x in drafts] == [1, 2]
    assert [x["narrative"] for x in drafts] == ["Seven cash deposits just under the threshold.", "Second version."]
    assert drafts[0]["findings"][0]["evidence_ids"] == ["TXN-S3001-01"]
    assert drafts[1]["recommendation"] == "no_case"
    assert full["status"] == "open" and full["case_id"] is None
    default = post(client, "/aml/alerts/TMA-3002/investigation", {k: v for k, v in investigation().items() if k != "drafted_by"})
    assert default["draft"]["drafted_by"] == "agent"
    assert get(client, "/aml/alerts/TMA-3003")["investigation_drafts"] == []


def test_investigation_refusals_are_readable(client):
    r = client.post("/aml/alerts/TMA-3001/investigation", json=investigation(evidence=("TXN-NOPE-99",)), headers=H)
    assert r.status_code == 422 and "TXN-NOPE-99" in r.json()["detail"] and r.json()["applied"] is False
    assert client.post("/aml/alerts/TMA-3001/investigation", json=investigation(recommendation="file_report"), headers=H).status_code == 422
    assert client.post("/aml/alerts/TMA-3001/investigation", json={**investigation(), "findings": []}, headers=H).status_code == 422
    assert client.post("/aml/alerts/TMA-3001/investigation",
                       json={**investigation(), "findings": [{"finding": "x", "evidence_ids": []}]}, headers=H).status_code == 422
    assert client.post("/aml/alerts/TMA-9999/investigation", json=investigation(), headers=H).status_code == 404
    assert get(client, "/aml/alerts/TMA-3001")["investigation_drafts"] == []
    # closed and case_opened alerts are refused with 409
    post(client, "/aml/cases", {"customer_id": "CUS-1020", "alert_ids": ["TMA-3001"], "summary": "Structuring."})
    r = client.post("/aml/alerts/TMA-3001/investigation", json=investigation(), headers=H)
    assert r.status_code == 409 and "case_opened" in r.json()["detail"]
    r = client.post("/aml/alerts/TMA-2901/investigation", json=investigation(), headers=H)
    assert r.status_code == 409 and "closed" in r.json()["detail"]


def test_opening_a_case_makes_the_latest_draft_the_first_narrative_version(client):
    post(client, "/aml/alerts/TMA-3001/investigation", investigation(narrative="First try.", drafted_by="first writer"))
    post(client, "/aml/alerts/TMA-3001/investigation",
         investigation(narrative="Final narrative.", evidence=("TXN-S3001-02", "CNT-5008", "MTB-AML-RULE-001", "TMA-3001", "CPY-4001"),
                       drafted_by="second writer"))
    c = post(client, "/aml/cases", {"customer_id": "CUS-1020", "alert_ids": ["TMA-3001"], "summary": "Structuring.",
                                    "opened_by": "A. Officer"})["case"]
    assert len(c["narratives"]) == 1
    n = c["narratives"][0]
    assert n["version"] == 1 and n["narrative"] == "Final narrative." and n["drafted_by"] == "second writer" and n["drafted_at"]
    assert {e["id"]: e["type"] for e in n["evidence"]} == {"TXN-S3001-02": "transaction", "CNT-5008": "contact",
                                                           "MTB-AML-RULE-001": "rule", "TMA-3001": "alert", "CPY-4001": "counterparty"}
    assert n["from_investigation"] == {"alert_id": "TMA-3001", "draft_version": 2, "recommendation": "open_case"}
    assert get(client, f"/aml/cases/{c['case_id']}")["narratives"][0]["narrative"] == "Final narrative."
    again = post(client, f"/aml/cases/{c['case_id']}/narrative", {"narrative": "A person's version.", "evidence": [{"type": "alert", "id": "TMA-3001"}]})
    assert again["draft"]["version"] == 2
    assert [x["version"] for x in get(client, f"/aml/cases/{c['case_id']}")["narratives"]] == [1, 2]


def test_a_case_without_a_saved_investigation_starts_with_no_narrative(client):
    c = post(client, "/aml/cases", {"customer_id": "CUS-1021", "alert_ids": ["TMA-3002"], "summary": "Pass-through."})["case"]
    assert c["narratives"] == []


def test_a_case_from_several_alerts_takes_the_latest_draft(client, store):
    # a second open alert of the same customer, so that one case can hold both
    store.data["monitoring_alerts"]["TMA-3999"] = {**store.data["monitoring_alerts"]["TMA-3001"], "alert_id": "TMA-3999",
                                                   "investigation_drafts": []}
    ev = ("TXN-S3001-01",)
    post(client, "/aml/alerts/TMA-3001/investigation", investigation(narrative="From the original.", evidence=ev))
    post(client, "/aml/alerts/TMA-3999/investigation", investigation(narrative="From the twin.", evidence=ev))
    store.data["monitoring_alerts"]["TMA-3001"]["investigation_drafts"][0]["drafted_at"] = "2026-11-24T10:00:00+00:00"
    store.data["monitoring_alerts"]["TMA-3999"]["investigation_drafts"][0]["drafted_at"] = "2026-11-24T11:00:00+00:00"
    c = post(client, "/aml/cases", {"customer_id": "CUS-1020", "alert_ids": ["TMA-3001", "TMA-3999"], "summary": "Both."})["case"]
    assert c["narratives"][0]["narrative"] == "From the twin." and c["narratives"][0]["from_investigation"]["alert_id"] == "TMA-3999"


# ---------------------------------------------------------------- 2. the monitoring-alert kind

def test_monitoring_alert_kind_rotates_through_four_templates(client, store):
    n0 = len(store.data["monitoring_alerts"])
    out = [post(client, "/admin/simulate/monitoring-alert") for _ in range(5)]
    ids = [o["item_id"] for o in out]
    assert ids == ["TMA-3101", "TMA-3102", "TMA-3103", "TMA-3104", "TMA-3105"] and len(store.data["monitoring_alerts"]) == n0 + 5
    assert all(o["event_type"] == "monitoring-alert" and o["system"] == "aml" and o["item_id"] in o["message"] for o in out)
    assert all(PLAIN(o["message"]) and "get_monitoring_alert" in o["message"] for o in out)
    assert len({o["message"] for o in out[:4]}) == 4
    rules = [get(client, f"/aml/alerts/{i}")["rule_id"] for i in ids]
    assert rules == ["MTB-AML-RULE-001", "MTB-AML-RULE-002", "MTB-AML-RULE-003", "MTB-AML-RULE-004", "MTB-AML-RULE-001"]
    assert get(client, "/aml/alerts/TMA-3105")["customer_id"] == get(client, "/aml/alerts/TMA-3101")["customer_id"]
    created = [e for e in get(client, "/admin/events")["items"] if e["status"] == "created"]
    assert {e["event_type"] for e in created} == {"monitoring-alert"} and len(created) == 5


def test_simulated_alerts_are_readable_and_their_figures_agree(client, store):
    seen = {}
    for _ in range(4):
        i = post(client, "/admin/simulate/monitoring-alert")["item_id"]
        a = get(client, f"/aml/alerts/{i}")
        assert a["status"] == "open" and a["case_id"] is None and a["investigation_drafts"] == [] and a["rule"]["rule_id"] == a["rule_id"]
        assert a["transactions"] and len(a["transactions"]) == len(a["transaction_ids"])
        assert all(t["account_id"] == a["account_id"] for t in a["transactions"])
        assert a["period_start"] <= a["period_end"] <= TODAY
        seen[a["rule_id"]] = a
    structuring = seen["MTB-AML-RULE-001"]
    amounts = [t["amount"] for t in structuring["transactions"]]
    assert len(amounts) == 4 and all(9000 <= x < 10000 for x in amounts) and sum(amounts) == 38000 and "USD 38,000" in structuring["summary"]
    passthrough = seen["MTB-AML-RULE-002"]
    credits = sum(t["amount"] for t in passthrough["transactions"] if t["direction"] == "credit")
    debits = sum(t["amount"] for t in passthrough["transactions"] if t["direction"] == "debit")
    assert round(100 * (credits - debits) / credits, 2) == 1.17 and "1.17 percent" in passthrough["summary"]
    assert all(t["amount"] >= 25000 for t in passthrough["transactions"] if t["direction"] == "credit")
    jurisdiction = seen["MTB-AML-RULE-003"]
    assert sum(t["amount"] for t in jurisdiction["transactions"]) == 21600 and {t["counterparty_country"] for t in jurisdiction["transactions"]} == {"QP"}
    contacts = get(client, f"/core/customers/{jurisdiction['customer_id']}/contacts")["items"]
    assert any("supply contract" in c["summary"] for c in contacts)
    payroll = seen["MTB-AML-RULE-004"]
    assert len(payroll["transactions"]) == 13 and "13 outgoing payments" in payroll["summary"]
    # a simulated alert can be investigated and turned into a case like any other
    post(client, f"/aml/alerts/{structuring['alert_id']}/investigation",
         investigation(narrative="Structuring.", evidence=(structuring["transaction_ids"][0],)))
    case = post(client, "/aml/cases", {"customer_id": structuring["customer_id"], "alert_ids": [structuring["alert_id"]], "summary": "s"})["case"]
    assert case["narratives"][0]["narrative"] == "Structuring."


def test_alert_priority_rule_is_written_down_and_every_seeded_alert_carries_its_priority(client):
    a = get(client, "/aml/alerts/TMA-3003")
    rule = a["priority_rule"]
    assert rule["name"] == "Alert priority rule" and "risk score alone" in rule["rule"] and "risk rating does not change it" in rule["rule"]
    assert "80 or more" in rule["high"] and "60 to 79" in rule["medium"] and "under 60" in rule["low"]
    assert all("investigator looks at the alert" in rule[p] for p in ("high", "medium", "low"))
    bands = [(b["priority"], b["min_score"], b["max_score"]) for b in rule["bands"]]
    assert bands == [("high", 80, 100), ("medium", 60, 79), ("low", 0, 59)]
    assert (a["risk_score"], a["priority"]) == (74, "medium")
    # each seeded alert, open or closed, carries the priority the rule gives its score, in the list and in full
    want = {"TMA-3001": (86, "high"), "TMA-3002": (82, "high"), "TMA-3003": (74, "medium"), "TMA-3004": (52, "low"),
            "TMA-2901": (55, "low"), "TMA-2902": (50, "low")}
    rows = {r["alert_id"]: r for r in get(client, "/aml/alerts")["items"]}
    assert {k: (r["risk_score"], r["priority"]) for k, r in rows.items()} == want
    for aid, (score, word) in want.items():
        full = get(client, f"/aml/alerts/{aid}")
        assert (full["risk_score"], full["priority"]) == (score, word) and full["priority_rule"] == rule
        band = next(b for b in rule["bands"] if b["priority"] == word)
        assert band["min_score"] <= score <= band["max_score"]
    history = get(client, "/aml/customers/CUS-1020/alerts")["alerts"]
    assert {h["alert_id"]: h["priority"] for h in history} == {"TMA-3001": "high", "TMA-2901": "low"}


def test_alert_priority_follows_the_bands_at_their_edges(store):
    from bank.seed_scen1 import alert_priority
    assert [alert_priority(s) for s in (100, 80, 79, 60, 59, 0)] == ["high", "high", "medium", "medium", "low", "low"]
    assert all(a["priority"] == alert_priority(a["risk_score"]) for a in store.data["monitoring_alerts"].values())


def test_simulated_alerts_carry_the_priority_the_rule_gives_their_score(client, store):
    got = []
    for _ in range(4):
        i = post(client, "/admin/simulate/monitoring-alert")["item_id"]
        a = get(client, f"/aml/alerts/{i}")
        assert store.data["monitoring_alerts"][i]["priority"] == a["priority"] and a["priority_rule"]["name"] == "Alert priority rule"
        got.append((a["rule_id"][-3:], a["risk_score"], a["priority"]))
    assert got == [("001", 84, "high"), ("002", 80, "high"), ("003", 58, "low"), ("004", 46, "low")]
    listed = {r["alert_id"]: r["priority"] for r in get(client, "/aml/alerts?status=open")["items"]}
    assert [listed[f"TMA-310{n}"] for n in (1, 2, 3, 4)] == ["high", "high", "low", "low"]


def test_an_alert_stored_without_a_priority_gets_it_from_its_score(client, store):
    del store.data["monitoring_alerts"]["TMA-3002"]["priority"]
    assert get(client, "/aml/alerts/TMA-3002")["priority"] == "high"
    assert next(r for r in get(client, "/aml/alerts")["items"] if r["alert_id"] == "TMA-3002")["priority"] == "high"


def test_monitoring_alert_can_be_subscribed_to_and_counted(client):
    r = post(client, "/admin/subscriptions", {"event_kind": "monitoring-alert", "url": "http://127.0.0.1:9/x"})
    assert r["subscription"]["event_kind"] == "monitoring-alert"
    delivered = post(client, "/admin/simulate/monitoring-alert")
    assert [d["status"] for d in delivered["deliveries"]] == ["queued"]
    assert get(client, "/admin/state")["counts"]["open_monitoring_alerts"] == 5
    assert "monitoring-alert" in client.get("/").text


# ---------------------------------------------------------------- 3. TMA-3002

def test_tma_3002_text_agrees_with_the_figures(client, store):
    a = get(client, "/aml/alerts/TMA-3002")
    credits = sum(t["amount"] for t in a["transactions"] if t["direction"] == "credit")
    debits = sum(t["amount"] for t in a["transactions"] if t["direction"] == "debit")
    assert (credits, debits) == (139500.0, 137600.0)
    assert round(100 * (credits - debits) / credits, 2) == 1.36
    assert "about 1.36 percent" in a["summary"] and "1.3 percent" not in a["summary"]
    assert "1.3 percent" not in json.dumps(store.data, ensure_ascii=False)
    scenarios = (ROOT / "SCENARIOS.md").read_text(encoding="utf-8")
    assert "about 1.36 percent" in scenarios and "about 1.3 percent" not in scenarios


# ---------------------------------------------------------------- 4. place of birth and address

def test_every_individual_customer_and_every_list_entry_has_both_fields(store):
    d = store.data
    people = [c for c in d["customers"].values() if c["type"] == "individual"]
    assert len(people) == 16
    for c in people:
        assert c["place_of_birth"].count(",") == 1 and c["address"], c["customer_id"]
    assert not any("place_of_birth" in c for c in d["customers"].values() if c["type"] == "business")
    entries = list(d["watchlist"].values())
    assert len(entries) == 14
    for e in entries:
        assert "place_of_birth" in e and "address" in e, e["entry_id"]
    assert sum(1 for e in entries if not e["address"]) >= 3 and sum(1 for e in entries if not e["place_of_birth"]) >= 1
    assert all(e["place_of_birth"] or e["address"] for e in entries)


def test_identity_cards_agree_with_the_places_of_birth(store):
    d = store.data
    for rid, cid in (("KYR-1001", "CUS-1013"),):
        card = next(x["text"] for x in d["kyc_documents"][rid].values() if x["doc_type"] == "identity_document")
        assert f"Place of birth: {d['customers'][cid]['place_of_birth'].split(',')[0]}" in card
    card = next(x["text"] for x in d["application_docs"]["LAP-8010"].values() if x["doc_type"] == "identity_document")
    assert f"Place of birth: {d['customers']['CUS-1016']['place_of_birth'].split(',')[0]}" in card


ALERT_PLACES = {
    # alert: (place of birth result, address result)
    "SCR-2001": ("differs", "differs"), "SCR-2002": ("differs", "differs"), "SCR-2003": ("match", "match"),
    "SCR-2004": ("partial", "unknown"), "SCR-2005": ("match", "differs"), "SCR-2006": ("differs", "match"),
}


@pytest.mark.parametrize("alert", sorted(ALERT_PLACES))
def test_screening_alert_shows_place_of_birth_and_address_side_by_side(client, alert):
    r = get(client, f"/screening/alerts/{alert}")
    res = {x["field"]: x for x in r["field_comparison"]}
    assert (res["place_of_birth"]["result"], res["address"]["result"]) == ALERT_PLACES[alert]
    customer, entry = r["customer_fields"], r["list_entry_fields"]
    assert res["place_of_birth"]["customer_value"] == customer["place_of_birth"] and customer["place_of_birth"]
    assert res["place_of_birth"]["list_value"] == entry["place_of_birth"]
    assert res["address"]["customer_value"] == customer["address"] and res["address"]["list_value"] == entry["address"]
    assert "place_of_birth" in entry and "address" in entry


def test_the_right_answers_of_the_screening_alerts_still_hold(client):
    expected = {"SCR-2001": ("differs", "differs"), "SCR-2002": ("differs", "differs"), "SCR-2003": ("match", "match"),
                "SCR-2005": ("match", "match")}
    for alert, (dob, nat) in expected.items():
        res = {x["field"]: x["result"] for x in get(client, f"/screening/alerts/{alert}")["field_comparison"]}
        assert (res["date_of_birth"], res["nationality"]) == (dob, nat), alert
    r = get(client, "/screening/alerts/SCR-2004")
    res = {x["field"]: x["result"] for x in r["field_comparison"]}
    assert res["date_of_birth"] == "unknown" and res["nationality"] == "unknown" and res["id_number"] == "unknown"
    assert res["year_of_birth"] == "match"
    r = get(client, "/screening/alerts/SCR-2006")
    assert r["list_entry_fields"]["related_persons"][0]["relationship"] == "spouse" and r["list_entry_fields"]["category"] == "pep"
    assert get(client, "/screening/watchlist/WL-9004")["address"] == ""
    assert get(client, "/screening/watchlist/WL-9003")["address"] == get(client, "/core/customers/CUS-1007")["address"]


def test_simulated_watchlist_entries_have_both_fields(client, store):
    for _ in range(4):
        r = post(client, "/admin/simulate/screening-alert")
        a = get(client, f"/screening/alerts/{r['item_id']}")
        assert "place_of_birth" in a["list_entry_fields"] and "address" in a["list_entry_fields"]
        assert a["customer_fields"]["place_of_birth"]
        assert any(x["field"] == "place_of_birth" for x in a["field_comparison"])


# ---------------------------------------------------------------- 5. the vocabulary of a recommendation

@pytest.mark.parametrize("word", ["matches", "partly_matches", "differs", "not_on_entry", "noted"])
def test_each_allowed_result_is_saved(client, word):
    body = {"recommendation": "escalate", "reasons": ["Needs a person."],
            "field_comparison": [{"field": "place_of_birth", "customer_value": "Ambrel, Tessaly", "list_value": "Tessaly", "result": word}]}
    r = post(client, "/screening/alerts/SCR-2004/recommendation", body)
    assert r["applied"] is True and r["draft"]["field_comparison"][0]["result"] == word and r["alert_status"] == "open"


@pytest.mark.parametrize("word", ["match", "unknown", "partial", "MATCHES", "yes", ""])
def test_any_other_result_is_refused_with_a_readable_422(client, word):
    body = {"recommendation": "clear", "reasons": ["x"], "field_comparison": [{"field": "name", "result": "matches"},
                                                                                {"field": "address", "result": word}]}
    r = client.post("/screening/alerts/SCR-2001/recommendation", json=body, headers=H)
    assert r.status_code == 422 and r.json()["applied"] is False
    detail = r.json()["detail"]
    assert "field_comparison.1.result" in detail
    for allowed in ("matches", "partly_matches", "differs", "not_on_entry", "noted"):
        assert allowed in detail
    assert get(client, "/screening/alerts/SCR-2001")["recommendations"] == []


def test_the_recommendation_stays_clear_or_escalate(client):
    ok = {"reasons": ["x"], "field_comparison": [{"field": "name", "result": "differs"}]}
    assert client.post("/screening/alerts/SCR-2001/recommendation", json={**ok, "recommendation": "partly_matches"}, headers=H).status_code == 422
    assert client.post("/screening/alerts/SCR-2001/recommendation", json={**ok, "recommendation": "escalate"}, headers=H).status_code == 200
    assert client.post("/screening/alerts/SCR-2001/recommendation", json={**ok, "recommendation": "clear"}, headers=H).status_code == 200
    doc = client.get("/screening/openapi.json").json()
    row = doc["components"]["schemas"]["FieldRow"]["properties"]["result"]
    assert row["enum"] == ["matches", "partly_matches", "differs", "not_on_entry", "noted"]
    assert doc["components"]["schemas"]["Recommendation"]["properties"]["recommendation"]["enum"] == ["clear", "escalate"]


# ---------------------------------------------------------------- 6. card payments carry a country and a town

def test_every_card_payment_has_a_country_a_town_and_a_card_present_flag(store):
    for t in store.data["card_transactions"].values():
        assert re.fullmatch(r"[A-Z]{2}", t["country"]) and t["town"], t["card_transaction_id"]
        assert isinstance(t["card_present"], bool)
        assert t["card_present"] == (t["channel"] != "online"), t["card_transaction_id"]


def test_card_payments_show_the_place_through_the_api(client):
    rows = get(client, "/cards/cards/CRD-2008/transactions")["items"]
    assert rows and all({"country", "town", "card_present"} <= set(r) for r in rows)
    abroad = [r for r in rows if r["country"] != "XM"]
    home = [r for r in rows if r["country"] == "XM"]
    assert {r["card_transaction_id"] for r in abroad} == {"CTX-2008-F01", "CTX-2008-F02", "CTX-2008-F03"}
    assert {r["country"] for r in abroad} == {"QN"} and {r["town"] for r in abroad} == {"Silverkeld", "Norvik", "Kaldmoor"}
    assert len(home) == 4 and all(r["card_present"] and r["channel"] == "chip" for r in home)
    assert all(r["date"] < min(a["date"] for a in abroad) for r in home)


def test_the_fraud_and_lost_card_scenarios_still_hold(client):
    c = get(client, "/fraud/cases/FRD-3001")
    assert [i["merchant_country"] for i in c["flagged_items"]] == ["QN"] * 3 and [i["merchant_town"] for i in c["flagged_items"]][0] == "Silverkeld"
    assert round(sum(i["amount"] for i in c["flagged_items"]), 2) == 2219.90
    rows = {r["card_transaction_id"]: r for r in get(client, "/cards/cards/CRD-2001/transactions")["items"]}
    assert (rows["CTX-2001-U01"]["amount"], rows["CTX-2001-U01"]["channel"], rows["CTX-2001-U01"]["card_present"]) == (389.0, "online", False)
    assert (rows["CTX-2001-U02"]["amount"], rows["CTX-2001-U02"]["channel"], rows["CTX-2001-U02"]["card_present"]) == (85.4, "contactless", True)
    assert rows["CTX-2001-A01"]["country"] == rows["CTX-2001-A02"]["country"] == "XM"
    d = post(client, "/cards/cards/CRD-2001/disputes", {"transaction_ids": ["CTX-2001-U01", "CTX-2001-U02"], "reason": "not_recognised"})
    assert d["dispute"]["amount"] == 474.40
    s = get(client, "/fraud/cases/FRD-3004")
    assert all(not i["card_present"] for i in s["flagged_items"])
    earlier = [r for r in get(client, "/cards/cards/CRD-2006/transactions")["items"] if r["merchant"] == "Streamline Video Club"]
    assert len(earlier) == 4 and all(not r["card_present"] and r["country"] == "XM" for r in earlier)


def test_simulated_fraud_card_payments_have_a_town(client, store):
    for _ in range(4):
        post(client, "/admin/simulate/fraud-case")
    simulated = [t for k, t in store.data["card_transactions"].items() if "-X" in k]
    assert simulated and all(t["town"] and t["country"] for t in simulated)
    assert {t["country"]: t["town"] for t in simulated} == {"QN": "Silverkeld", "XM": "Port Ilvane"}


# ---------------------------------------------------------------- 7. investigations name their rules

def test_investigations_name_the_rules_that_apply(client, store):
    expected = {"INV-5001": [], "INV-5002": ["MTB-PAY-RULE-105"], "INV-5003": ["MTB-PAY-RULE-106"]}
    for inv, ids in expected.items():
        r = get(client, f"/payments/investigations/{inv}")
        assert r["rule_ids"] == ids and [x["rule_id"] for x in r["rules"]] == ids and r["rule_note"].endswith(".")
        assert all(x["text"] and x["title"] for x in r["rules"])
        assert all(i in store.data["payment_rules"] for i in r["rule_ids"])
    short = get(client, "/payments/investigations/INV-5002")
    assert "charges OUR" in short["rules"][0]["text"] and short["payment"]["charges_bearer"] == "OUR"
    returned = get(client, "/payments/investigations/INV-5003")
    assert "returned" in returned["rules"][0]["title"].lower() and returned["rules"][0]["reason_code"] == "AC04"
    assert "No bank rule applies" in get(client, "/payments/investigations/INV-5001")["rule_note"]


def test_simulated_investigations_name_their_rules(client):
    found = []
    for _ in range(4):
        r = post(client, "/admin/simulate/payment-investigation")
        i = get(client, f"/payments/investigations/{r['item_id']}")
        found.append((i["type"], i["rule_ids"]))
    assert found == [("beneficiary_not_received", []), ("amount_short", ["MTB-PAY-RULE-105"]),
                     ("payment_returned", ["MTB-PAY-RULE-106"]), ("payment_returned", ["MTB-PAY-RULE-106"])]


def test_the_list_of_investigations_is_unchanged(client):
    row = get(client, "/payments/investigations")["items"][0]
    assert set(row) == {"investigation_id", "payment_id", "customer_id", "type", "status", "raised", "claim"}


# ---------------------------------------------------------------- 8. search payments by beneficiary

def test_search_by_beneficiary_name_and_account(client):
    by_name = get(client, "/payments/payments", params={"beneficiary_name": "alder wharf"})
    assert {p["payment_id"] for p in by_name["items"]} == {"PAY-6050", "PAY-6101"}
    good = "XB82BRVN73201150000142"
    by_account = get(client, "/payments/payments", params={"beneficiary_account": good})
    assert [p["payment_id"] for p in by_account["items"]] == ["PAY-6050"] and by_account["items"][0]["beneficiary_account"] == good
    spaced = get(client, "/payments/payments", params={"beneficiary_account": "xb82 brvn 7320 1150 0001 42"})
    assert [p["payment_id"] for p in spaced["items"]] == ["PAY-6050"]
    part = get(client, "/payments/payments", params={"beneficiary_account": "BRVN73201150000142"})
    assert [p["payment_id"] for p in part["items"]] == ["PAY-6050"]
    both = get(client, "/payments/payments", params={"beneficiary_name": "Alder Wharf", "beneficiary_account": good})
    assert [p["payment_id"] for p in both["items"]] == ["PAY-6050"]
    none = get(client, "/payments/payments", params={"beneficiary_name": "Alder Wharf", "beneficiary_account": "XA00ALDB55210030008816"})
    assert none["count"] == 0
    steel = get(client, "/payments/payments", params={"beneficiary_name": "Aldoria Steel"})
    assert {p["payment_id"] for p in steel["items"]} == {"PAY-6051", "PAY-6103"} and steel["total_matches"] == 2
    mixed = get(client, "/payments/payments", params={"beneficiary_name": "Aldoria Steel", "customer_id": "CUS-1018", "status": "held"})
    assert [p["payment_id"] for p in mixed["items"]] == ["PAY-6103"]
    assert get(client, "/payments/payments", params={"beneficiary_name": "Nobody At All"})["count"] == 0
    assert client.get("/payments/payments", params={"beneficiary_account": "XB82"}, headers=H).status_code == 422


def test_search_without_the_new_filters_is_unchanged(client):
    assert get(client, "/payments/payments", params={"limit": 200})["total_matches"] == len(build_all(TODAY_D)["payments"])


# ---------------------------------------------------------------- 9. ledger and statement entries

def test_read_one_ledger_and_one_statement_entry(client):
    led = get(client, "/recon/ledger/LED-7101")
    assert led["side"] == "ledger" and led["amount"] == 12480.0 and led["reference"] == "INV-558210-AO" and led["batch_id"] == ""
    assert led["related_break_ids"] == ["BRK-4001"]
    stm = get(client, "/recon/statements/STM-8101")
    assert stm["side"] == "statement" and stm["reference"] == "INV-558210-AQ" and stm["related_break_ids"] == ["BRK-4001"]
    assert get(client, "/recon/ledger/LED-7102")["related_break_ids"] == ["BRK-4001"]
    assert get(client, "/recon/ledger/LED-6001")["related_break_ids"] == []
    assert client.get("/recon/ledger/STM-8101", headers=H).status_code == 404
    assert client.get("/recon/statements/LED-7101", headers=H).status_code == 404
    assert client.get("/recon/ledger/LED-0000", headers=H).status_code == 404


def test_search_filters_combine(client, store):
    everything = get(client, "/recon/ledger")
    assert everything["count"] == len(store.data["recon_ledger"]) and all(v is None for v in everything["searched"].values())
    on_account = get(client, "/recon/ledger", params={"account": "NOS-QNMK-01"})["items"]
    assert on_account and all(e["account_id"] == "NOS-QNMK-01" for e in on_account) and len(on_account) < everything["count"]
    exact = get(client, "/recon/ledger", params={"amount_from": 5250, "amount_to": 5250})["items"]
    assert {e["entry_id"] for e in exact} == {"LED-7201", "LED-7203"}
    assert {e["entry_id"] for e in get(client, "/recon/ledger", params={"amount_from": 12000})["items"]} == {"LED-7101", "LED-7102"}
    assert {e["entry_id"] for e in get(client, "/recon/ledger", params={"amount_to": 3, "reference": "BATCH-0457"})["items"]} == set()
    batch = get(client, "/recon/ledger", params={"reference": "batch-0457", "account": "NOS-QNMK-01"})
    assert {e["entry_id"] for e in batch["items"]} == {"LED-7201", "LED-7202"}
    recent = get(client, "/recon/ledger", params={"date_from": (TODAY_D - timedelta(days=4)).isoformat(),
                                                  "date_to": (TODAY_D - timedelta(days=3)).isoformat()})["items"]
    assert recent and all((TODAY_D - timedelta(days=4)).isoformat() <= e["value_date"] <= (TODAY_D - timedelta(days=3)).isoformat() for e in recent)
    assert [e["value_date"] for e in recent] == sorted((e["value_date"] for e in recent), reverse=True)
    stm = get(client, "/recon/statements", params={"reference": "SETT-BATCH", "amount_from": 8000, "amount_to": 8000})
    assert [e["entry_id"] for e in stm["items"]] == ["STM-8201"] and stm["searched"]["reference"] == "SETT-BATCH"
    assert all(e["side"] == "statement" for e in get(client, "/recon/statements")["items"])
    assert client.get("/recon/ledger", params={"account": "NOS-NOPE-01"}, headers=H).status_code == 404


def test_brk_4005_cannot_be_found_by_amount_and_date(client, store):
    item = get(client, "/recon/statements/STM-8501")
    assert (item["amount"], item["reference"], item["account_id"]) == (3275.40, "UNK-77QX", "NOS-QNMK-01")
    assert get(client, "/recon/breaks/BRK-4005")["candidates"] == []
    value = date.fromisoformat(item["value_date"])
    assert value == TODAY_D - timedelta(days=9)
    # the item's own amount, on any account and any date
    assert get(client, "/recon/ledger", params={"amount_from": 3275.40, "amount_to": 3275.40})["count"] == 0
    # the item's amount and its value date
    day = value.isoformat()
    assert get(client, "/recon/ledger", params={"amount_from": 3275.40, "amount_to": 3275.40, "date_from": day, "date_to": day})["count"] == 0
    # five days either side on the same account
    window = {"account": "NOS-QNMK-01", "date_from": (value - timedelta(days=5)).isoformat(), "date_to": (value + timedelta(days=5)).isoformat()}
    assert get(client, "/recon/ledger", params={**window, "amount_from": 3275.40, "amount_to": 3275.40})["count"] == 0
    near = get(client, "/recon/ledger", params=window)["items"]
    assert {e["entry_id"] for e in near} == {"LED-7201", "LED-7202", "LED-7203"}
    assert 3275.40 not in {e["amount"] for e in near}
    assert get(client, "/recon/ledger", params={"reference": "UNK-77QX"})["count"] == 0
    assert 3275.40 not in {sum(c) for c in ((5250.0, 2750.0), (5250.0,), (2750.0,))}
    # on the statement side only the item itself carries that amount
    same = get(client, "/recon/statements", params={"amount_from": 3275.40, "amount_to": 3275.40})
    assert [e["entry_id"] for e in same["items"]] == ["STM-8501"]
    # the searches really can find things: the same kind of search finds the match of another break
    found = get(client, "/recon/ledger", params={"amount_from": 12480, "amount_to": 12480, "account": "NOS-ALDB-01"})
    assert [e["entry_id"] for e in found["items"]] == ["LED-7101"]
    assert not any(e["amount"] == 3275.40 for e in store.data["recon_ledger"].values())


def test_search_works_through_the_mcp_door(client):
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": "search_ledger_entries", "arguments": {"amount_from": 12480, "amount_to": 12480}}}
    r = client.post("/recon/mcp", json=body, headers=H).json()["result"]
    assert json.loads(r["content"][0]["text"])["items"][0]["entry_id"] == "LED-7101"
    body["params"] = {"name": "get_statement_entry", "arguments": {"entry_id": "STM-8501"}}
    assert json.loads(client.post("/recon/mcp", json=body, headers=H).json()["result"]["content"][0]["text"])["reference"] == "UNK-77QX"


# ---------------------------------------------------------------- 10. loan instalments

def test_every_loan_in_the_exposure_has_a_monthly_instalment(client, store):
    seen = {}
    for cid in store.data["customers"]:
        for ln in get(client, f"/core/customers/{cid}/exposure")["loans"]:
            seen[ln["loan_id"]] = ln["monthly_instalment"]
    assert set(seen) == set(store.data["loans"]) and len(seen) == 8
    assert all(isinstance(v, float) and v > 0 for v in seen.values())
    assert seen["LN-9005"] == 450.0 and seen["LN-9003"] == 930.0 and seen["LN-9002"] == 6500.0
    assert all(store.data["loans"][k]["monthly_instalment"] == v for k, v in seen.items())


def test_instalments_agree_with_the_collections_data_and_the_statements(client, store):
    d = store.data
    by_loan = {}
    for call in d["collections_calls"].values():
        by_loan.setdefault(call["loan_id"], set()).add(call["arrears"]["monthly_instalment"])
    assert set(by_loan) == {"LN-9005", "LN-9003", "LN-9101", "LN-9102", "LN-9103"}
    for loan_id, values in by_loan.items():
        assert values == {d["loans"][loan_id]["monthly_instalment"]}, loan_id
        exposure = get(client, f"/core/customers/{d['loans'][loan_id]['customer_id']}/exposure")
        assert next(x for x in exposure["loans"] if x["loan_id"] == loan_id)["monthly_instalment"] in values
    # the instalments paid from the customer's account
    for loan_id, values in by_loan.items():
        cid = d["loans"][loan_id]["customer_id"]
        paid = {t["amount"] for t in d["transactions"].values()
                if t["type"] == "loan_repayment" and d["accounts"][t["account_id"]]["customer_id"] == cid}
        assert paid == values, loan_id
    # a simulated call agrees as well
    for _ in range(4):
        r = post(client, "/admin/simulate/collections-call")
        call = d["collections_calls"][r["item_id"]]
        assert call["arrears"]["monthly_instalment"] == d["loans"][call["loan_id"]]["monthly_instalment"]
    # LAP-8001 shows the car loan instalment of the same customer
    assert "Car loan instalment               -450.00" in " ".join(x["text"] for x in d["application_docs"]["LAP-8001"].values())


def test_the_instalment_of_ln_9002_is_the_debt_service_in_the_credit_analysis(client, store):
    text = get(client, "/lending/applications/LAP-8003/documents/DOC-8302")["text"]
    assert "Interest expense               21,000       19,500       18,000" in text
    assert "Current portion of long-term debt 60,000      60,000       60,000" in text
    assert (18000 + 60000) / 12 == store.data["loans"]["LN-9002"]["monthly_instalment"] == 6500.0


# ---------------------------------------------------------------- 11. the lending descriptions

def test_lending_descriptions_say_which_values_each_field_takes(client):
    doc = client.get("/lending/openapi.json").json()
    ops = {op["operationId"]: op for item in doc["paths"].values() for op in item.values()}
    for name in ("save_missing_items", "save_credit_memo"):
        assert "FORM" in ops[name]["description"] and "application form" in ops[name]["description"]
    assert "tax_return" in ops["save_missing_items"]["description"]
    assert "debt_service_cover" in ops["save_credit_memo"]["description"] and "refer" in ops["save_credit_memo"]["description"]
    schemas = doc["components"]["schemas"]
    for name in ("Figure", "FigureSource"):
        assert "FORM" in schemas[name]["properties"]["source_document_id"]["description"]
    missing = schemas["MissingItems"]["properties"]["missing_items"]["description"]
    for t in ("identity_document", "payslips_3_months", "employment_letter", "company_registration", "tax_return", "directors_identity"):
        assert t in missing
    ratio = schemas["Ratio"]["properties"]["name"]["description"]
    for t in ("debt_to_income", "current_ratio", "debt_to_equity", "debt_service_cover"):
        assert t in ratio
    assert schemas["CreditMemo"]["properties"]["recommendation"]["enum"] == ["approve", "decline", "refer"]


def test_a_figure_can_name_the_application_form_as_its_source(client):
    memo = {"memo_text": "Turnover differs.", "figure_sources": [
        {"figure": "average_monthly_turnover", "value": "62000 USD", "source_document_id": "FORM"},
        {"figure": "six_month_credits", "value": "308400 USD", "source_document_id": "DOC-8203"}], "recommendation": "refer"}
    r = post(client, "/lending/applications/LAP-8002/credit-memo", memo)
    assert r["draft"]["version"] == 1 and [f["source_document_id"] for f in r["draft"]["figure_sources"]] == ["FORM", "DOC-8203"]
    figures = {"missing_items": ["tax_return", "ownership_declaration"], "extracted_figures": [
        {"name": "average_monthly_turnover", "value": "62000 USD", "source_document_id": "FORM"}]}
    saved = post(client, "/lending/applications/LAP-8002/missing-items", figures)
    assert saved["draft"]["extracted_figures"][0]["source_document_id"] == "FORM"
    form = get(client, "/lending/applications/LAP-8002")["form_fields"]
    assert form["average_monthly_turnover"] == 62000.0
    checklist = get(client, "/lending/applications/LAP-8002")["document_checklist"]
    assert [c["type"] for c in checklist if not c["received"]] == figures["missing_items"]


# ---------------------------------------------------------------- 12. Pinecrest

def test_press_and_application_agree_on_the_staff_of_pinecrest(client, store):
    form = get(client, "/lending/applications/LAP-8003")["form_fields"]
    assert form["employees"] == 24
    article = get(client, "/news/articles/ART-6012")
    assert "Pinecrest Tooling Works" in article["body"] and f"its {form['employees']} staff" in article["body"]
    assert "85" not in article["body"]
    hits = get(client, "/news/articles", params={"text": "Pinecrest"})["items"]
    assert [h["article_id"] for h in hits] == ["ART-6012"]


# ---------------------------------------------------------------- the files

def test_readme_describes_the_platform_steps_and_the_new_operations():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "The steps are being proven" not in text
    section = text.split("## Connecting it to a platform")[1].split("## Notes for people who build on it")[0]
    assert "These steps were run on a development cluster of the Katonic platform on 24 November 2026." in section
    assert section.count("\n1. ") == 1 and "\n4. Attach the tools to an agent in Studio" in section
    assert "`demo-bank/main.py`" in section and "`<the app's address>/cards/openapi.json`" in section
    assert "What was proven:" in section and "What was not proven: registering a system's MCP address" in section
    assert "BANK_API_KEY" in section and "`/health`" in section and "X-API-Key" in section
    assert "146 operations" in text and "141 operations" not in text and "`monitoring-alert`" in text
    assert re.search(r"\| aml \|[^\n]*\| 9 \|", text) and re.search(r"\| recon \|[^\n]*\| 9 \|", text)
    assert "save_alert_investigation" in text and "search_ledger_entries" in text


def test_scenarios_file_covers_every_correction():
    text = (ROOT / "SCENARIOS.md").read_text(encoding="utf-8")
    for needle in ("save_alert_investigation", "investigation_drafts", "monitoring-alert", "place of birth differs", "partly_matches",
                   "not_on_entry", "rule_ids", "MTB-PAY-RULE-105", "MTB-PAY-RULE-106", "beneficiary_account", "search_ledger_entries",
                   "search_statement_entries", "get_ledger_entry", "monthly_instalment", "6,500.00", "`FORM`", "24 employees", "card_present",
                   "about 1.36 percent"):
        assert needle in text, needle


def test_the_files_have_no_dash_and_no_tool_names():
    words = ["cla" + "ude", "anth" + "ropic", "open" + "ai", "chat" + "gpt", "cop" + "ilot", "gem" + "ini", "co-" + "authored"]
    for path in list(ROOT.glob("*.md")) + list((ROOT / "bank").glob("*.py")) + list((ROOT / "bank" / "systems").glob("*.py")) + list((ROOT / "tests").glob("*.py")):
        text = path.read_text(encoding="utf-8")
        assert DASH not in text, path.name
        for w in words:
            assert w not in text.lower(), (path.name, w)
