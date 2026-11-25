"""Tests for the four added systems: onboarding, complaints, collections and audit, and their four event kinds."""

import json
from datetime import date, datetime
from pathlib import Path

import pytest
from openapi_spec_validator import validate

from bank.seed import build_all
from bank.seed_aud import last_quarters, months_back
from bank.seed_cmp import add_working_days, working_days_between
from conftest import H, KEY, TODAY

TODAY_D = date.fromisoformat(TODAY)
OLD = ["core", "cards", "screening", "aml", "payments", "lending", "fraud", "recon", "news"]
NEW = ["onboarding", "complaints", "collections", "audit"]
POLICY_DIR = Path(__file__).resolve().parents[2] / "banking" / "policy-library"
DASH = chr(0x2014)

EXPECTED = {
    "onboarding": {"list_onboarding_applications", "get_onboarding_application", "list_onboarding_documents", "get_onboarding_document",
                   "get_onboarding_requirements", "save_onboarding_file", "decide_onboarding_application", "list_kyc_reviews",
                   "get_kyc_review", "get_kyc_review_document", "save_refreshed_profile", "complete_kyc_review"},
    "complaints": {"list_complaints", "get_complaint", "get_complaints_procedure", "save_complaint_classification",
                   "save_complaint_response", "send_complaint_response"},
    "collections": {"list_collections_calls", "get_collections_call", "get_conduct_rules", "save_call_review", "mark_call_reviewed"},
    "audit": {"list_control_tests", "get_control_test", "search_tickets", "get_ticket", "list_change_records", "get_change_record",
              "list_access_reviews", "get_access_review", "list_recovery_tests", "get_recovery_test", "save_evidence_pack"},
}


def get(client, path, **kw):
    r = client.get(path, headers=H, **kw)
    assert r.status_code == 200, (path, r.status_code, r.text[:200])
    return r.json()


def post(client, path, body, status=200):
    r = client.post(path, json=body, headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:300])
    return r.json()


def words(text):
    return len(text.split())


# ---------------------------------------------------------------- sign-in, documents, tools

def test_new_systems_need_a_key(client):
    for path in ["/onboarding/applications", "/onboarding/requirements", "/onboarding/reviews", "/complaints/complaints", "/complaints/procedure",
                 "/collections/calls", "/collections/conduct-rules", "/audit/control-tests", "/audit/tickets", "/audit/changes",
                 "/audit/access-reviews", "/audit/recovery-tests"]:
        assert client.get(path).status_code == 401, path
        assert client.get(path, headers=H).status_code == 200, path
        assert client.get(path, headers={"Authorization": f"Bearer {KEY}"}).status_code == 200, path
    for path, body in [("/onboarding/applications/ONB-1001/decision", {"decision": "approve", "decided_by": "x"}),
                       ("/onboarding/reviews/KYR-1001/complete", {"signed_off_by": "x"}),
                       ("/complaints/complaints/CMP-1001/send", {"approved_by": "x"}),
                       ("/collections/calls/CAL-1001/reviewed", {"reviewed_by": "x"}),
                       ("/audit/control-tests/CTL-1001/evidence-pack", {})]:
        assert client.post(path, json=body).status_code == 401, path
    for s in NEW:
        assert client.post(f"/{s}/mcp", json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"}).status_code == 401


def test_new_openapi_documents_are_valid_and_plain(client):
    for s in NEW:
        doc = client.get(f"/{s}/openapi.json").json()
        assert doc["openapi"] == "3.0.3"
        validate(doc)
        text = json.dumps(doc)
        assert "anyOf" not in text and "nullable" not in text and '"type": "null"' not in text, s
        assert "ApiKeyAuth" in doc["components"]["securitySchemes"]
        assert "invented" in doc["info"]["description"].split(".")[0].lower()
        assert DASH not in json.dumps(doc, ensure_ascii=False)
        for item in doc["paths"].values():
            for op in item.values():
                assert op["operationId"] == op["operationId"].lower() and all(c.isalnum() or c == "_" for c in op["operationId"])
                assert op["summary"].strip() and len(op["description"]) > 60
                for p in op.get("parameters", []):
                    assert p.get("description"), (op["operationId"], p["name"])
                    assert p["schema"].get("type") in ("string", "integer", "number", "boolean"), (op["operationId"], p["name"])


def test_operation_ids_per_new_system_and_across_all_systems(client):
    seen = []
    counts = {}
    for s in OLD + NEW:
        doc = client.get(f"/{s}/openapi.json").json()
        ids = [op["operationId"] for item in doc["paths"].values() for op in item.values()]
        counts[s] = len(ids)
        seen += ids
        if s in EXPECTED:
            assert set(ids) == EXPECTED[s], s
    assert counts["onboarding"] == 12 and counts["complaints"] == 6 and counts["collections"] == 5 and counts["audit"] == 11
    assert len(seen) == len(set(seen)) == 105
    for name in ("file_report", "submit_report", "conclude_control_test", "pass_control_test"):
        assert name not in seen
    pack = client.get("/audit/openapi.json").json()["components"]["schemas"]["EvidencePack"]["properties"]
    assert not any("conclusion" in k or "verdict" in k or "result" in k for k in pack)


def mcp(client, system, method, params=None, mid=1):
    body = {"jsonrpc": "2.0", "id": mid, "method": method, "params": params or {}}
    r = client.post(f"/{system}/mcp", json=body, headers=H)
    assert r.status_code == 200
    return r.json()["result"]


@pytest.mark.parametrize("system", NEW)
def test_every_operation_id_is_an_mcp_tool_of_its_system(client, system):
    doc = client.get(f"/{system}/openapi.json").json()
    ops = {op["operationId"]: op for item in doc["paths"].values() for op in item.values()}
    tools = mcp(client, system, "tools/list")["tools"]
    assert {t["name"] for t in tools} == set(ops)
    for t in tools:
        assert t["description"] == ops[t["name"]]["description"]


def test_mcp_tool_calls_read_and_write_through(client, store):
    r = mcp(client, "complaints", "tools/call", {"name": "get_complaint", "arguments": {"complaint_id": "CMP-1001"}})
    assert json.loads(r["content"][0]["text"])["complaint_id"] == "CMP-1001"
    args = {"decision": "approve", "decided_by": "A. Officer", "application_id": "ONB-1001"}
    r = mcp(client, "onboarding", "tools/call", {"name": "decide_onboarding_application", "arguments": args})
    assert "applied" in r["content"][0]["text"] and store.data["onb_applications"]["ONB-1001"]["status"] == "approved"
    r2 = mcp(client, "onboarding", "tools/call", {"name": "decide_onboarding_application", "arguments": args}, mid=2)
    assert r2["isError"] is True and "409" in r2["content"][0]["text"]


def test_landing_page_lists_the_four_new_systems(client):
    text = client.get("/").text
    assert "The nineteen systems" in text and "Four more systems" not in text
    for s in NEW:
        assert f"/{s}/openapi.json" in text and f"/{s}/mcp" in text and f"/{s}/docs" in text
    counts = get(client, "/admin/state")["counts"]
    assert {"open_onboarding_applications", "open_kyc_reviews", "open_complaints", "unreviewed_collections_calls", "open_control_tests"} <= set(counts)


def test_documents_are_text_of_a_sensible_length_without_dashes(store):
    d = store.data
    docs = [x for coll in d["onb_documents"].values() for x in coll.values()] + [x for coll in d["kyc_documents"].values() for x in coll.values()]
    assert len(docs) == 21
    for x in docs:
        assert x["format"] == "extracted text" and 150 <= words(x["text"]) <= 400, (x["document_id"], words(x["text"]))
    for cid in ("CMP-1001", "CMP-1002", "CMP-1003", "CMP-1004", "CMP-1005"):
        assert 150 <= words(d["complaints"][cid]["customer_words"]) <= 400, cid
    for c in d["collections_calls"].values():
        total = sum(words(t["text"]) for t in c["transcript"])
        assert 150 <= total <= 400, (c["call_id"], total)
    for coll in ("onb_applications", "onb_documents", "kyc_reviews", "kyc_documents", "complaints", "complaints_procedure", "collections_calls",
                 "conduct_rules", "control_tests", "tickets", "change_records", "access_reviews", "recovery_tests", "onb_requirements"):
        assert DASH not in json.dumps(d[coll], ensure_ascii=False), coll


def test_new_data_uses_only_invented_countries_and_existing_records(store):
    d = store.data
    allowed = {"Meridia", "Aldoria", "Brevnia", "Quenmark", "Rovaland", "Tessaly", "Norvania", "Kharnovia"}
    for a in d["onb_applications"].values():
        f = a["form"]
        for o in f.get("owners_declared", []):
            assert o["country"] in allowed
        if a["kind"] == "individual":
            assert f["nationality"] in allowed
    for r in d["kyc_reviews"].values():
        assert r["customer_id"] in d["customers"]
    for c in d["complaints"].values():
        assert c["customer_id"] in d["customers"]
        ln = c["linked"]
        for i in ln["account_ids"]:
            assert d["accounts"][i]["customer_id"] == c["customer_id"]
        for i in ln["card_ids"]:
            assert d["cards"][i]["customer_id"] == c["customer_id"]
        for i in ln["payment_ids"]:
            assert d["payments"][i]["customer_id"] == c["customer_id"]
        for i in ln["loan_ids"]:
            assert d["loans"][i]["customer_id"] == c["customer_id"]
        for i in ln["loan_application_ids"]:
            assert d["applications"][i]["customer_id"] == c["customer_id"]
        for i in ln["transaction_ids"]:
            assert d["transactions"][i]["account_id"] in ln["account_ids"]
    for c in d["collections_calls"].values():
        assert d["loans"][c["loan_id"]]["customer_id"] == c["customer_id"]
        e = d["exposure"][c["customer_id"]]
        assert c["loan_id"] in [x["loan_id"] for x in e["loans"]]
        assert e["total_outstanding_loans"] == round(sum(x["outstanding"] for x in e["loans"]), 2)


def test_counts_include_the_new_systems(client):
    counts = get(client, "/admin/state")["counts"]
    assert counts["open_onboarding_applications"] == 6 and counts["open_kyc_reviews"] == 3
    assert counts["open_complaints"] == 5 and counts["unreviewed_collections_calls"] == 5 and counts["open_control_tests"] == 4
    assert counts["open_fraud_cases"] == 4 and counts["news_articles"] == 25


# ---------------------------------------------------------------- onboarding scenarios

def app_docs(client, aid):
    rows = get(client, f"/onboarding/applications/{aid}/documents")["items"]
    return {r["doc_type"]: get(client, f"/onboarding/applications/{aid}/documents/{r['document_id']}")["text"] for r in rows}


def line(text, label):
    return next(l.split(":", 1)[1].strip() for l in text.splitlines() if l.startswith(label))


def test_onboarding_list_and_requirements(client):
    assert get(client, "/onboarding/applications")["count"] == 6
    assert get(client, "/onboarding/applications?kind=individual")["count"] == 3
    assert get(client, "/onboarding/applications?kind=business")["count"] == 3
    assert get(client, "/onboarding/applications?status=approved")["count"] == 0
    assert client.get("/onboarding/applications?kind=other", headers=H).status_code == 422
    req = get(client, "/onboarding/requirements")
    assert {x["type"] for x in req["kinds"]["individual"]["documents"]} == {"identity_document", "proof_of_address"}
    assert {x["type"] for x in req["kinds"]["business"]["documents"]} == {"company_registry_extract", "constitutional_documents", "ownership_declaration"}
    assert "3 months" in req["bank_rules"]["proof_of_address_max_age"] and "25 percent" in req["bank_rules"]["ownership_threshold"]
    assert req["differences_that_matter"] and req["differences_that_do_not_matter"]
    one = get(client, "/onboarding/applications/ONB-1001")
    assert [c["received"] for c in one["required_documents"]] == [True, True] and one["form"]["full_name"] == "Odalys Merrowby"
    assert client.get("/onboarding/applications/ONB-9999", headers=H).status_code == 404
    assert client.get("/onboarding/applications/ONB-1001/documents/NOPE", headers=H).status_code == 404


def test_onb_1_individual_clean_complete_pack(client):
    a = get(client, "/onboarding/applications/ONB-1001")
    docs = app_docs(client, "ONB-1001")
    ident, addr = docs["identity_document"], docs["proof_of_address"]
    assert line(ident, "Surname and given names") == a["form"]["full_name"] and line(ident, "Date of birth") == a["form"]["date_of_birth"]
    assert line(ident, "Identity number") == a["form"]["id_number"] and line(ident, "Nationality") == a["form"]["nationality"]
    assert line(addr, "Account holder") == a["form"]["full_name"] and line(addr, "Supply address") == a["form"]["address"]
    assert (TODAY_D - date.fromisoformat(line(addr, "Document date"))).days <= 90
    assert date.fromisoformat(line(ident, "Date of expiry")) > TODAY_D
    hits = post(client, "/screening/search", {"name": a["form"]["full_name"], "date_of_birth": a["form"]["date_of_birth"], "country": "XM"})
    assert hits["count"] == 0


def test_onb_2_name_spelled_differently_and_old_proof_of_address(client):
    a = get(client, "/onboarding/applications/ONB-1002")
    docs = app_docs(client, "ONB-1002")
    assert a["form"]["full_name"] == "Isadora Fenimore" and line(docs["identity_document"], "Surname and given names") == "Isadora Fennimore"
    assert line(docs["identity_document"], "Date of birth") == a["form"]["date_of_birth"]
    age = (TODAY_D - date.fromisoformat(line(docs["proof_of_address"], "Document date"))).days
    assert age == 150 and age > 90
    assert get(client, "/screening/search".replace("/search", "/alerts"))["count"] >= 6


def test_onb_3_strong_match_to_a_watchlist_entry(client):
    a = get(client, "/onboarding/applications/ONB-1003")
    docs = app_docs(client, "ONB-1003")
    assert line(docs["identity_document"], "Identity number") == "BRV-559120"
    hits = post(client, "/screening/search", {"name": a["form"]["full_name"], "date_of_birth": a["form"]["date_of_birth"], "country": "XB"})
    top = hits["items"][0]
    assert top["entry_id"] == "WL-9001" and top["score"] == 100 and top["date_of_birth"] == "match" and top["nationality"] == "match"
    entry = get(client, "/screening/watchlist/WL-9001")
    assert entry["id_number"] == "BRV-559120" and entry["date_of_birth"] == a["form"]["date_of_birth"]
    assert "refer_to_compliance" in get(client, "/onboarding/requirements")["decisions"]


def test_onb_4_company_with_one_owner_of_100_percent(client):
    a = get(client, "/onboarding/applications/ONB-1004")
    assert [c["received"] for c in a["required_documents"]] == [True, True, True]
    assert a["form"]["owners_declared"] == [{"name": "Bertrand Ulverstone", "type": "person", "percent": 100, "country": "Meridia"}]
    docs = app_docs(client, "ONB-1004")
    assert "Bertrand Ulverstone: person, Meridia, 100 percent" in docs["ownership_declaration"]
    assert "100 percent" in docs["ownership_declaration"] and "100 percent of the shares" in docs["company_registry_extract"]
    assert docs["company_registry_extract"].count(", director") == 1 and "Bertrand Ulverstone" in docs["company_registry_extract"]


def test_onb_5_ownership_chain_has_a_gap_that_no_document_fills(client, store):
    a = get(client, "/onboarding/applications/ONB-1005")
    owners = {o["name"]: o for o in a["form"]["owners_declared"]}
    assert owners["Vardane Holdings Ltd"]["percent"] == 60 and owners["Vardane Holdings Ltd"]["type"] == "company"
    assert owners["Vardane Holdings Ltd"]["country"] == "Quenmark" and owners["Corwin Ashdown"]["percent"] == 40
    docs = app_docs(client, "ONB-1005")
    for t, text in docs.items():
        assert "Vardane Holdings Ltd" in text or t == "constitutional_documents"
        assert "owned by" not in text.lower() and "shareholders of vardane" not in text.lower()
    assert "does not record who owns a shareholder that is itself a company" in docs["company_registry_extract"]
    # the only person named anywhere in the application papers is the director and 40 percent owner
    names = {"Corwin Ashdown"}
    text = " ".join(docs.values())
    assert [n for n in ("Brackenridge", "Orrelby", "Ulverstone", "Oldacre") if n in text] == []
    assert names <= {o["name"] for o in owners.values()}


def test_onb_6_registry_shows_a_director_the_form_does_not_list(client):
    a = get(client, "/onboarding/applications/ONB-1006")
    assert a["form"]["directors"] == ["Nerys Hallowfield"]
    reg = app_docs(client, "ONB-1006")["company_registry_extract"]
    assert "Garrick Oldacre, director" in reg and "Nerys Hallowfield, director" in reg
    assert a["bank_rules"]["screening"]


def test_onboarding_file_is_a_draft_with_versions(client, store):
    body = {"details_extracted": [{"field": "full_name", "value": "Isadora Fennimore", "source_document_id": "OND-1002-01"}],
            "mismatches": [{"field": "full_name", "form_value": "Isadora Fenimore", "document_value": "Isadora Fennimore",
                            "source_document_id": "OND-1002-01", "note": "One letter differs."}],
            "screening_result": {"screened_name": "Isadora Fennimore", "outcome": "no_match"},
            "missing_items": ["A proof of address dated within 3 months."], "recommendation": "ask_applicant", "drafted_by": "tester"}
    a = post(client, "/onboarding/applications/ONB-1002/file", body)
    assert a["applied"] is True and a["kind"] == "draft" and a["draft"]["version"] == 1 and a["draft"]["drafted_by"] == "tester"
    assert a["draft"]["drafted_at"] and a["application_status"] == "received"
    del body["drafted_by"]
    b = post(client, "/onboarding/applications/ONB-1002/file", {**body, "recommendation": "ask_applicant", "summary": "second"})
    assert b["draft"]["version"] == 2 and b["draft"]["drafted_by"] == "agent"
    full = get(client, "/onboarding/applications/ONB-1002")
    assert [f["version"] for f in full["files"]] == [1, 2] and full["status"] == "received"
    assert client.post("/onboarding/applications/ONB-1002/file", json={**body, "recommendation": "maybe"}, headers=H).status_code == 422
    bad = {**body, "mismatches": [{**body["mismatches"][0], "source_document_id": "OND-0000-00"}]}
    assert client.post("/onboarding/applications/ONB-1002/file", json=bad, headers=H).status_code == 404
    assert client.post("/onboarding/applications/ONB-1002/file", json={"recommendation": "approve"}, headers=H).status_code == 422


def test_onboarding_ownership_chain_with_a_gap_can_be_saved(client):
    body = {"screening_result": {"screened_name": "Larkfield Marine Services Ltd", "outcome": "no_match"},
            "ownership_chain": [
                {"owner": "Corwin Ashdown", "owner_type": "person", "percent": 40, "country": "Meridia", "source_document_id": "OND-1005-03"},
                {"owner": "Vardane Holdings Ltd", "owner_type": "company", "percent": 60, "country": "Quenmark",
                 "source_document_id": "OND-1005-03", "gap": True, "gap_note": "No document shows who owns Vardane Holdings Ltd."}],
            "ownership_gaps": ["60 percent is held by Vardane Holdings Ltd and no document shows who owns it."],
            "missing_items": ["A document that shows the owners of Vardane Holdings Ltd."], "recommendation": "ask_applicant"}
    r = post(client, "/onboarding/applications/ONB-1005/file", body)
    assert r["draft"]["ownership_gaps"] and r["draft"]["ownership_chain"][1]["gap"] is True


def test_onboarding_decision_is_a_change_and_refuses_twice(client, store):
    assert client.post("/onboarding/applications/ONB-1001/decision", json={"decision": "approve"}, headers=H).status_code == 422
    assert client.post("/onboarding/applications/ONB-1001/decision", json={"decision": "open", "decided_by": "x"}, headers=H).status_code == 422
    r = post(client, "/onboarding/applications/ONB-1001/decision", {"decision": "approve", "decided_by": "A. Officer", "note": "Complete."})
    assert r["applied"] is True and r["kind"] == "change" and r["status"] == "approved" and r["decision"]["decided_by"] == "A. Officer"
    again = client.post("/onboarding/applications/ONB-1001/decision", json={"decision": "decline", "decided_by": "B"}, headers=H)
    assert again.status_code == 409 and "already approved" in again.json()["detail"] and again.json()["applied"] is False
    assert client.post("/onboarding/applications/ONB-1001/file", json={"screening_result": {"screened_name": "x", "outcome": "no_match"},
                                                                       "recommendation": "approve"}, headers=H).status_code == 409
    r = post(client, "/onboarding/applications/ONB-1002/decision", {"decision": "ask_applicant", "decided_by": "A", "message_to_applicant": "Send a newer bill."})
    assert r["status"] == "awaiting_applicant"
    assert client.post("/onboarding/applications/ONB-1002/decision", json={"decision": "ask_applicant", "decided_by": "A"}, headers=H).status_code == 409
    post(client, "/onboarding/applications/ONB-1002/decision", {"decision": "decline", "decided_by": "A"})
    assert client.post("/onboarding/applications/ONB-1002/decision", json={"decision": "approve", "decided_by": "A"}, headers=H).status_code == 409
    assert get(client, "/admin/state")["counts"]["open_onboarding_applications"] == 4


# ---------------------------------------------------------------- periodic reviews

def test_kyc_review_1_nothing_changed(client):
    r = get(client, "/onboarding/reviews/KYR-1001")
    assert r["customer"]["customer_id"] == "CUS-1013" and r["risk_rating"] == "standard" and r["status"] == "open"
    cust = get(client, "/core/customers/CUS-1013")
    held = r["held_profile"]
    assert held["address"] == cust["address"] and held["id_number"] == cust["id_number"]
    docs = {x["doc_type"]: get(client, f"/onboarding/reviews/KYR-1001/documents/{x['document_id']}")["text"] for x in r["fresh_documents"]}
    assert line(docs["identity_document"], "Identity number") == held["id_number"]
    assert line(docs["proof_of_address"], "Supply address") == held["address"] and line(docs["proof_of_address"], "Account holder") == held["name"]
    assert (TODAY_D - date.fromisoformat(r["last_review_date"])).days > 300


def test_kyc_review_2_new_address_and_occupation_same_rating(client):
    r = get(client, "/onboarding/reviews/KYR-1002")
    held = r["held_profile"]
    docs = {x["doc_type"]: get(client, f"/onboarding/reviews/KYR-1002/documents/{x['document_id']}")["text"] for x in r["fresh_documents"]}
    assert line(docs["proof_of_address"], "Supply address") == "22 Barley Mill Lane, Tallowby, Meridia" != held["address"]
    assert "self-employed building surveyor" in docs["occupation_letter"] and held["occupation"] == "Quantity surveyor"
    assert r["risk_rating"] == "standard"


def test_kyc_review_3_new_owner_in_the_higher_risk_country(client):
    r = get(client, "/onboarding/reviews/KYR-1003")
    held = r["held_profile"]
    assert r["customer"]["type"] == "business" and [o["percent"] for o in held["owners"]] == [55, 45]
    assert all(o["country"] == "Meridia" for o in held["owners"])
    docs = {x["doc_type"]: get(client, f"/onboarding/reviews/KYR-1003/documents/{x['document_id']}")["text"] for x in r["fresh_documents"]}
    decl = docs["ownership_declaration"]
    assert "Tavish Orrelby: person, Kharnovia, 30 percent" in decl and "Ottoline Brackenridge: person, Meridia, 40 percent" in decl
    assert "Tavish Orrelby (person, Kharnovia), 30 percent" in docs["company_registry_extract"]
    assert "Kharnovia (QP)" in r["higher_risk_countries"]


def test_kyc_list_and_unknown_ids(client):
    assert get(client, "/onboarding/reviews")["count"] == 3
    assert get(client, "/onboarding/reviews?status=completed")["count"] == 0
    rows = get(client, "/onboarding/reviews?status=open")["items"]
    assert [x["review_id"] for x in rows] == ["KYR-1003", "KYR-1002", "KYR-1001"]
    assert client.get("/onboarding/reviews/KYR-9999", headers=H).status_code == 404
    assert client.get("/onboarding/reviews/KYR-1001/documents/NOPE", headers=H).status_code == 404


def profile(**kw):
    base = {"changes": [{"field": "address", "old_value": "8 Kestrel Hill, Marlow Reach, Meridia",
                         "new_value": "22 Barley Mill Lane, Tallowby, Meridia", "source_document_id": "KYD-1002-01"}],
            "unchanged_fields": ["id_number"], "proposed_risk_rating": "standard", "rating_reason": "Nothing raises the risk.", "drafted_by": "tester"}
    base.update(kw)
    return base


def test_refreshed_profile_is_a_draft_with_versions(client):
    a = post(client, "/onboarding/reviews/KYR-1002/profile-draft", profile())
    assert a["applied"] is True and a["kind"] == "draft" and a["draft"]["version"] == 1 and a["draft"]["drafted_by"] == "tester"
    b = post(client, "/onboarding/reviews/KYR-1002/profile-draft", profile(rating_reason="Second.", drafted_by="agent"))
    assert b["draft"]["version"] == 2
    full = get(client, "/onboarding/reviews/KYR-1002")
    assert [p["version"] for p in full["profile_drafts"]] == [1, 2] and full["status"] == "open"
    assert get(client, "/core/customers/CUS-1015")["address"] == "8 Kestrel Hill, Marlow Reach, Meridia"
    assert client.post("/onboarding/reviews/KYR-1002/profile-draft", json=profile(proposed_risk_rating="low"), headers=H).status_code == 422
    assert client.post("/onboarding/reviews/KYR-1002/profile-draft", json=profile(rating_reason=""), headers=H).status_code == 422
    bad = profile(changes=[{"field": "address", "old_value": "a", "new_value": "b", "source_document_id": "KYD-0000-00"}])
    assert client.post("/onboarding/reviews/KYR-1002/profile-draft", json=bad, headers=H).status_code == 404


def test_kyc_completion_needs_a_draft_a_signature_and_for_a_rating_change_an_approver(client, store):
    assert client.post("/onboarding/reviews/KYR-1001/complete", json={"signed_off_by": "P. Signer"}, headers=H).status_code == 409
    post(client, "/onboarding/reviews/KYR-1001/profile-draft", profile(changes=[], unchanged_fields=["address", "id_number"]))
    assert client.post("/onboarding/reviews/KYR-1001/complete", json={}, headers=H).status_code == 422
    r = post(client, "/onboarding/reviews/KYR-1001/complete", {"signed_off_by": "P. Signer"})
    assert r["applied"] is True and r["status"] == "completed" and r["completion"]["rating_changed"] is False
    again = client.post("/onboarding/reviews/KYR-1001/complete", json={"signed_off_by": "P"}, headers=H)
    assert again.status_code == 409 and "already completed" in again.json()["detail"]
    assert client.post("/onboarding/reviews/KYR-1001/profile-draft", json=profile(), headers=H).status_code == 409

    post(client, "/onboarding/reviews/KYR-1002/profile-draft", profile())
    post(client, "/onboarding/reviews/KYR-1002/complete", {"signed_off_by": "P. Signer"})
    assert store.data["customers"]["CUS-1015"]["address"] == "22 Barley Mill Lane, Tallowby, Meridia"

    post(client, "/onboarding/reviews/KYR-1003/profile-draft", profile(
        changes=[{"field": "owners", "old_value": "Ottoline 55, Hamish 45", "new_value": "Ottoline 40, Hamish 30, Tavish Orrelby 30 (Kharnovia)",
                  "source_document_id": "KYD-1003-02"}], proposed_risk_rating="high",
        rating_reason="A new owner of 30 percent lives in Kharnovia, on the higher-risk list."))
    refused = client.post("/onboarding/reviews/KYR-1003/complete", json={"signed_off_by": "P. Signer"}, headers=H)
    assert refused.status_code == 409 and "rating_change_approved_by" in refused.json()["detail"]
    assert store.data["kyc_reviews"]["KYR-1003"]["status"] == "open" and store.data["customers"]["CUS-1024"]["risk_rating"] == "standard"
    r = post(client, "/onboarding/reviews/KYR-1003/complete", {"signed_off_by": "P. Signer", "rating_change_approved_by": "R. Head"})
    assert r["completion"]["rating_changed"] is True and r["completion"]["new_risk_rating"] == "high"
    assert get(client, "/core/customers/CUS-1024")["risk_rating"] == "high"
    assert get(client, "/admin/state")["counts"]["open_kyc_reviews"] == 0


# ---------------------------------------------------------------- complaints

def test_complaints_procedure_and_list(client):
    p = get(client, "/complaints/procedure")
    assert "2 working days" in p["time_limits"]["acknowledge"] and "15 working days" in p["time_limits"]["final_response"]
    assert p["what_a_response_must_contain"] and p["redress"]["when_it_applies"] and "Ombudsman" in p["escalation"]
    assert len(p["categories"]) == 7 and "30 days" in p["credit_decisions"]
    rows = get(client, "/complaints/complaints")["items"]
    assert [r["complaint_id"] for r in rows][0] == "CMP-0901" and len(rows) == 6
    assert get(client, "/complaints/complaints?status=open")["count"] == 5 and get(client, "/complaints/complaints?status=closed")["count"] == 1
    assert client.get("/complaints/complaints/CMP-9999", headers=H).status_code == 404


def test_cmp_1_fee_charged_twice(client):
    c = get(client, "/complaints/complaints/CMP-1001")
    fees = c["linked_records"]["transactions"]
    assert len(fees) == 2 and fees[0]["amount"] == fees[1]["amount"] == 12.0 and fees[0]["date"] == fees[1]["date"] and fees[0]["type"] == "fee"
    rows = get(client, "/core/accounts/ACC-1009-01/transactions")["items"]
    same_day = [t for t in rows if t["type"] == "fee" and t["date"] == fees[0]["date"]]
    assert len(same_day) == 2
    monthly = [t for t in rows if t["type"] == "fee"]
    assert len(monthly) == 4 and len({t["date"] for t in monthly}) == 3
    assert c["earlier_complaints"][0]["complaint_id"] == "CMP-0901" and c["earlier_complaints"][0]["outcome"] == "not_upheld"
    assert c["dates"]["acknowledged_late"] is False and c["dates"]["acknowledgement_overdue"] is False


def test_cmp_2_late_payment_explained_by_the_investigation(client):
    c = get(client, "/complaints/complaints/CMP-1002")
    inv = c["linked_records"]["payment_investigations"][0]
    pay = c["linked_records"]["payments"][0]
    assert inv["investigation_id"] == "INV-5001" and pay["payment_id"] == "PAY-6001" and pay["status"] == "credited"
    notes = " ".join(t["note"] for t in pay["timeline"])
    assert "correspondent bank until its next processing day" in notes
    credited = next(t for t in pay["timeline"] if t["status"] == "credited")
    sent = next(t for t in pay["timeline"] if t["status"] == "sent")
    assert (date.fromisoformat(credited["date"]) - date.fromisoformat(sent["date"])).days == 3
    assert get(client, "/payments/investigations/INV-5001")["type"] == "beneficiary_not_received"


def test_cmp_2_linked_payment_carries_its_status_reports(client):
    pay = get(client, "/complaints/complaints/CMP-1002")["linked_records"]["payments"][0]
    reports = pay["status_reports"]
    assert [r["message_id"] for r in reports] == ["MSG-6001-2"] and reports[0]["type"] == "pacs.002"
    credited = next(t for t in pay["timeline"] if t["status"] == "credited")
    assert reports[0]["status"] == "ACSC" and reports[0]["credited_on"] == reports[0]["date"] == credited["date"]
    assert "credited to the beneficiary" in reports[0]["summary"] and "direction" not in reports[0] and "key_fields" not in reports[0]
    # the same report the payments system holds, and only the inbound ones: the message the bank sent is not a status report
    full = get(client, "/payments/payments/PAY-6001")
    inbound = [m for m in full["messages"] if m["direction"] == "inbound"]
    assert len(full["messages"]) == 2 and len(inbound) == 1
    assert inbound[0]["message_id"] == "MSG-6001-2" and inbound[0]["key_fields"] == {"status": "ACSC", "credited_on": credited["date"]}
    assert "messages" not in pay


def test_complaint_with_no_payment_or_card_has_empty_lists(client):
    ln = get(client, "/complaints/complaints/CMP-1001")["linked_records"]
    assert ln["payments"] == [] and ln["cards"] == []


def test_cmp_3_declined_loan_is_not_a_service_failure(client):
    c = get(client, "/complaints/complaints/CMP-1003")
    la = c["linked_records"]["loan_applications"][0]
    assert la["application_id"] == "LAP-8010" and la["status"] == "declined" and la["decision"]["policy_id"] == "MTB-POL-030"
    full = get(client, "/lending/applications/LAP-8010")
    f = full["form_fields"]
    dti = (f["existing_monthly_debt_payments"] + full["indicative_monthly_installment"]) / f["gross_monthly_income"]
    assert round(dti, 2) == 0.48 and dti > 0.40
    assert all(x["received"] for x in full["document_checklist"])
    assert get(client, "/lending/applications?status=received")["count"] == 3
    assert c["dates"]["working_days_since_received"] == 5
    assert "Credit Review Desk" in get(client, "/complaints/procedure")["credit_decisions"]


def test_cmp_4_bereaved_customer_whose_card_was_blocked(client):
    c = get(client, "/complaints/complaints/CMP-1004")
    card = c["linked_records"]["cards"][0]
    assert card["card_id"] == "CRD-2004" and card["status"] == "blocked" and "deceased accounts" in card["block_note"].lower()
    assert "husband died" in c["customer_words"] and c["channel"] == "branch"
    assert get(client, "/cards/cards/CRD-2004")["status"] == "blocked"
    assert "vulnerable" in get(client, "/complaints/procedure")["vulnerable_customers"]


def test_cmp_4_linked_card_names_its_holder_and_the_note_says_whose_cards_the_process_is_for(client):
    c = get(client, "/complaints/complaints/CMP-1004")
    card = c["linked_records"]["cards"][0]
    # the card is the complainant's own, and the records say so
    assert card["customer_id"] == c["customer_id"] == "CUS-1001"
    assert card["customer_id"] == get(client, "/cards/cards/CRD-2004")["customer_id"]
    note = card["block_note"]
    assert note.startswith("Blocked by the deceased accounts process after a death was recorded on the household.")
    assert "The process is for cards held by the person who died." in note
    assert "This card is held by CUS-1001, who reported the death." in note
    assert card["blocked_by"] == "Deceased accounts desk" and card["block_reason"] == "other"


def test_complaints_procedure_has_a_rule_for_severity(client):
    sev = get(client, "/complaints/procedure")["severity"]
    assert set(sev) == {"rule", "low", "medium", "high"} and "highest level" in sev["rule"]
    assert "small sum" in sev["low"] and "can still use the account and the card" in sev["low"]
    assert "without money or a service" in sev["medium"] and "time limit" in sev["medium"]
    assert "cannot reach" in sev["high"] and "may be vulnerable" in sev["high"]
    # the levels are the ones a classification accepts, and the closed complaint in the history carries one of them
    old = get(client, "/complaints/complaints/CMP-0901")["classifications"][0]
    assert old["severity"] == "low" and old["severity"] in sev


def test_cmp_5_never_acknowledged_after_thirteen_working_days(client):
    c = get(client, "/complaints/complaints/CMP-1005")
    dt = c["dates"]
    assert dt["working_days_since_received"] == 13 and dt["acknowledged_on"] == "" and dt["acknowledgement_overdue"] is True
    assert dt["acknowledgement_days_late"] == 11 and dt["working_days_left_for_final_response"] == 2
    rec = date.fromisoformat(dt["received"])
    assert working_days_between(rec, TODAY_D) == 13 and rec.weekday() < 5
    assert dt["final_response_due"] == add_working_days(rec, 15).isoformat() and dt["acknowledge_due"] == add_working_days(rec, 2).isoformat()
    rows = get(client, "/complaints/complaints")["items"]
    assert [r["complaint_id"] for r in rows if r["acknowledgement_overdue"]] == ["CMP-1005"]


def test_working_day_helpers():
    assert add_working_days(date(2026, 11, 20), 1) == date(2026, 11, 23)
    assert add_working_days(date(2026, 11, 23), -1) == date(2026, 11, 20)
    assert working_days_between(date(2026, 11, 20), date(2026, 11, 24)) == 2
    assert working_days_between(date(2026, 11, 24), date(2026, 11, 20)) == -2


def classification(**kw):
    base = {"category": "fees_and_charges", "severity": "low", "may_be_vulnerable": False, "drafted_by": "tester"}
    base.update(kw)
    return base


def response(**kw):
    base = {"response_text": "We charged the fee twice. We are sorry.", "outcome": "upheld", "redress_amount": 12.0, "redress_account_id": "ACC-1009-01",
            "redress_description": "The second fee.", "log_entry": "CMP-1001 fees upheld, USD 12.00 refunded.", "drafted_by": "tester"}
    base.update(kw)
    return base


def test_complaint_classification_and_response_are_drafts_with_versions(client):
    a = post(client, "/complaints/complaints/CMP-1004/classification",
             classification(category="cards", severity="high", may_be_vulnerable=True, vulnerability_reason="Recent bereavement.", priority="priority"))
    assert a["applied"] is True and a["kind"] == "draft" and a["draft"]["version"] == 1 and a["draft"]["drafted_by"] == "tester"
    b = post(client, "/complaints/complaints/CMP-1004/classification", classification(drafted_by="agent"))
    assert b["draft"]["version"] == 2 and b["draft"]["drafted_by"] == "agent"
    c = post(client, "/complaints/complaints/CMP-1001/response-draft", response())
    assert c["draft"]["version"] == 1 and c["complaint_status"] == "open"
    d2 = post(client, "/complaints/complaints/CMP-1001/response-draft", response(redress_amount=0, redress_account_id=""))
    assert d2["draft"]["version"] == 2
    full = get(client, "/complaints/complaints/CMP-1001")
    assert [x["version"] for x in full["response_drafts"]] == [1, 2] and full["status"] == "open"
    assert client.post("/complaints/complaints/CMP-1004/classification", json=classification(severity="extreme"), headers=H).status_code == 422
    assert client.post("/complaints/complaints/CMP-1001/response-draft", json=response(redress_account_id="ACC-1001-01"), headers=H).status_code == 422
    assert client.post("/complaints/complaints/CMP-1001/response-draft", json=response(outcome="maybe"), headers=H).status_code == 422
    assert [t for t in get(client, "/core/accounts/ACC-1009-01/transactions")["items"] if t["type"] == "redress"] == []


def test_sending_a_response_is_a_change_that_credits_redress_and_refuses_twice(client, store):
    assert client.post("/complaints/complaints/CMP-1001/send", json={"approved_by": "P. Approver"}, headers=H).status_code == 409
    post(client, "/complaints/complaints/CMP-1001/response-draft", response())
    assert client.post("/complaints/complaints/CMP-1001/send", json={}, headers=H).status_code == 422
    before = store.data["accounts"]["ACC-1009-01"]["balance"]
    r = post(client, "/complaints/complaints/CMP-1001/send", {"approved_by": "P. Approver"})
    assert r["applied"] is True and r["kind"] == "change" and r["status"] == "responded" and r["sent"]["approved_by"] == "P. Approver"
    tid = r["sent"]["redress_transaction_id"]
    t = store.data["transactions"][tid]
    assert t["amount"] == 12.0 and t["direction"] == "credit" and t["type"] == "redress"
    assert store.data["accounts"]["ACC-1009-01"]["balance"] == round(before + 12.0, 2)
    again = client.post("/complaints/complaints/CMP-1001/send", json={"approved_by": "B"}, headers=H)
    assert again.status_code == 409 and "already answered" in again.json()["detail"] and again.json()["applied"] is False
    assert client.post("/complaints/complaints/CMP-1001/response-draft", json=response(), headers=H).status_code == 409
    assert client.post("/complaints/complaints/CMP-1001/classification", json=classification(), headers=H).status_code == 409
    assert get(client, "/admin/state")["counts"]["open_complaints"] == 4


# ---------------------------------------------------------------- collections

def call(client, cid):
    return get(client, f"/collections/calls/{cid}")


def who(c):
    return [t["speaker"] for t in c["transcript"]]


def test_conduct_rules_and_call_list(client):
    rules = get(client, "/collections/conduct-rules")
    assert [r["rule_id"] for r in rules["items"]] == [f"CR-0{n}" for n in range(1, 8)]
    text = " ".join(r["title"] + " " + r["text"] for r in rules["items"])
    assert "08:00 and 20:00" in text and "hardship options" in text and "promise to pay" in text
    rows = get(client, "/collections/calls")["items"]
    assert len(rows) == 5 and [r["started_at"] for r in rows] == sorted((r["started_at"] for r in rows), reverse=True)
    one = (TODAY_D.replace(day=TODAY_D.day - 1)).isoformat()
    assert {r["call_id"] for r in get(client, f"/collections/calls?date={one}")["items"]} == {"CAL-1001", "CAL-1002", "CAL-1005"}
    assert get(client, "/collections/calls?status=reviewed")["count"] == 0
    assert client.get("/collections/calls/CAL-9999", headers=H).status_code == 404


def test_cal_1_clean_call_ends_in_a_promise_to_pay(client):
    c = call(client, "CAL-1001")
    t = c["transcript"]
    assert "calling from Meridian Trust Bank" in t[0]["text"] and t[0]["speaker"] == "Caller"
    first_debt = next(i for i, x in enumerate(t) if "USD" in x["text"])
    last_id = max(i for i, x in enumerate(t) if "date of birth" in x["text"] or "first line of your address" in x["text"])
    assert last_id < first_debt
    promise = [x["text"] for x in t if "USD 450.00" in x["text"] and x["speaker"] == "Customer"]
    assert promise and "by card in the app" in promise[0]
    assert c["arrears"]["amount_overdue"] == 450.0 and c["customer"]["customer_id"] == "CUS-1012" and c["loan"]["loan_id"] == "LN-9005"
    assert not any("job" in x["text"] or "ill" in x["text"].split() for x in t)


def test_cal_2_debt_discussed_before_identity_is_confirmed(client):
    t = call(client, "CAL-1002")["transcript"]
    debt = next(i for i, x in enumerate(t) if "USD 1,860.00" in x["text"] and x["speaker"] == "Caller")
    ident = next(i for i, x in enumerate(t) if "date of birth" in x["text"] and x["speaker"] == "Caller")
    assert debt < ident
    assert any("USD 1,860.00 on" in x["text"] for x in t if x["speaker"] == "Caller")


def test_cal_3_job_loss_and_no_hardship_option_offered(client):
    c = call(client, "CAL-1003")
    assert any("lost my job" in x["text"] for x in c["transcript"] if x["speaker"] == "Customer")
    caller = " ".join(x["text"].lower() for x in c["transcript"] if x["speaker"] == "Caller")
    for option in ("payment holiday", "reduced payments", "longer loan term", "money advice", "hardship"):
        assert option not in caller
    assert "confirm" not in caller


def test_cal_4_someone_else_answers_and_the_caller_mentions_the_debt(client):
    c = call(client, "CAL-1004")
    assert "Other person" in who(c) and "Customer" not in who(c)
    caller = [x["text"] for x in c["transcript"] if x["speaker"] == "Caller"]
    assert any("loan" in x and "USD 275.00" in x for x in caller)
    assert c["started_at"].endswith("18:50:41")


def test_cal_5_firm_call_that_breaks_no_rule(client):
    c = call(client, "CAL-1005")
    t = c["transcript"]
    assert "calling from Meridian Trust Bank" in t[0]["text"] and "08:00:00" <= t[0]["time"] < "20:00:00" and t[-1]["time"] < "20:00:00"
    firm = next(x["text"] for x in t if "straightforward" in x["text"])
    assert "45 days" in firm and "recovery team" in firm and "Is anything making it hard" in firm
    for bad in ("lose your home", "bailiff", "tonight", "court"):
        assert bad not in firm
    assert any("USD 1,040.00 on" in x["text"] and x["speaker"] == "Caller" for x in t) and "Other person" not in who(c)


def test_every_transcript_has_rising_times_and_only_known_speakers(store):
    for c in store.data["collections_calls"].values():
        times = [t["time"] for t in c["transcript"]]
        assert times == sorted(times) and times[0] == c["started_at"].split(" ")[1]
        assert {t["speaker"] for t in c["transcript"]} <= {"Caller", "Customer", "Other person"}


def call_review(**kw):
    base = {"summary": "A clean call.", "rule_findings": [{"rule_id": "CR-01", "finding": "followed", "evidence": "11:20:05 said calling from Meridian Trust Bank."}],
            "follow_up_note": "Chase on the promised date.", "supervisor_review": False, "drafted_by": "tester"}
    base.update(kw)
    return base


def test_call_review_is_a_draft_with_versions(client):
    a = post(client, "/collections/calls/CAL-1002/review", call_review(
        rule_findings=[{"rule_id": "CR-02", "finding": "breached", "evidence": "15:40:42 the caller said USD 1,860.00 before asking for the date of birth."}],
        supervisor_review=True))
    assert a["applied"] is True and a["kind"] == "draft" and a["draft"]["version"] == 1 and a["draft"]["drafted_by"] == "tester"
    b = post(client, "/collections/calls/CAL-1002/review", call_review(drafted_by="agent"))
    assert b["draft"]["version"] == 2 and b["call_status"] == "unreviewed"
    full = call(client, "CAL-1002")
    assert [r["version"] for r in full["reviews"]] == [1, 2] and full["status"] == "unreviewed"
    assert client.post("/collections/calls/CAL-1002/review", json=call_review(rule_findings=[{"rule_id": "CR-99", "finding": "followed"}]), headers=H).status_code == 422
    assert client.post("/collections/calls/CAL-1002/review", json=call_review(rule_findings=[{"rule_id": "CR-02", "finding": "breached"}]), headers=H).status_code == 422
    assert client.post("/collections/calls/CAL-1002/review", json=call_review(rule_findings=[{"rule_id": "CR-02", "finding": "maybe"}]), headers=H).status_code == 422
    assert client.post("/collections/calls/CAL-1002/review", json=call_review(rule_findings=[]), headers=H).status_code == 422


def test_marking_a_call_reviewed_is_a_change_and_refuses_twice(client):
    assert client.post("/collections/calls/CAL-1001/reviewed", json={"reviewed_by": "S. Supervisor"}, headers=H).status_code == 409
    post(client, "/collections/calls/CAL-1001/review", call_review())
    assert client.post("/collections/calls/CAL-1001/reviewed", json={}, headers=H).status_code == 422
    r = post(client, "/collections/calls/CAL-1001/reviewed", {"reviewed_by": "S. Supervisor"})
    assert r["applied"] is True and r["kind"] == "change" and r["status"] == "reviewed" and r["reviewed"]["reviewed_by"] == "S. Supervisor"
    again = client.post("/collections/calls/CAL-1001/reviewed", json={"reviewed_by": "B"}, headers=H)
    assert again.status_code == 409 and "already reviewed" in again.json()["detail"]
    assert client.post("/collections/calls/CAL-1001/review", json=call_review(), headers=H).status_code == 409
    assert get(client, "/admin/state")["counts"]["unreviewed_collections_calls"] == 4
    assert get(client, "/collections/calls?status=reviewed")["count"] == 1


# ---------------------------------------------------------------- audit

def plan(client, tid):
    return get(client, f"/audit/control-tests/{tid}")


@pytest.mark.skipif(not POLICY_DIR.exists(), reason="the policy library is not next to this folder")
def test_each_control_test_tests_a_real_clause_of_the_policy(client):
    policy = next(POLICY_DIR.glob("MTB-POL-033*.md")).read_text(encoding="utf-8")
    seen = {}
    for row in get(client, "/audit/control-tests")["items"]:
        t = plan(client, row["test_id"])
        assert t["policy_id"] == "MTB-POL-033" and f"\n{t['clause']} {t['clause_text']}" in policy, t["test_id"]
        seen[t["test_id"]] = t["clause"]
    assert seen == {"CTL-1001": "6.1", "CTL-1002": "3.1", "CTL-1003": "2.2", "CTL-1004": "6.2"}


def test_control_test_list_and_unknown_ids(client):
    rows = get(client, "/audit/control-tests")["items"]
    assert [r["test_id"] for r in rows] == ["CTL-1001", "CTL-1002", "CTL-1003", "CTL-1004"] and all(r["status"] == "open" for r in rows)
    for tid in ("CTL-1001", "CTL-1002", "CTL-1003", "CTL-1004"):
        t = plan(client, tid)
        assert t["steps"] and t["evidence_plan"] and t["control_objective"] and "conclu" in " ".join(t["steps"]).lower()
        assert [i["item_no"] for i in t["evidence_plan"]] == list(range(1, len(t["evidence_plan"]) + 1))
        assert all(i["where_to_look"] and i["item"] for i in t["evidence_plan"])
    for path in ("/audit/control-tests/CTL-9", "/audit/tickets/TKT-1", "/audit/changes/CHG-1", "/audit/access-reviews/ACR-1", "/audit/recovery-tests/RCV-1"):
        assert client.get(path, headers=H).status_code == 404


def test_ctl_1_access_reviewed_quarterly_one_missing(client):
    t = plan(client, "CTL-1001")
    qs = [f"{y}-Q{q}" for y, q in last_quarters(TODAY_D)]
    assert qs == ["2025-Q4", "2026-Q1", "2026-Q2", "2026-Q3"]
    assert len(t["evidence_plan"]) == 12 and t["systems_in_scope"] == ["core-banking", "payments-hub", "card-platform"]
    rows = get(client, "/audit/access-reviews")["items"]
    have = {(r["system"], r["quarter"]) for r in rows}
    want = {(s, q) for s in t["systems_in_scope"] for q in qs}
    assert len(rows) == 11 and want - have == {("payments-hub", "2026-Q2")} and have <= want
    for r in rows:
        full = get(client, f"/audit/access-reviews/{r['review_id']}")
        assert full["signed_off_by"] and date.fromisoformat(full["completed_on"]) <= TODAY_D
    assert get(client, "/audit/access-reviews?system=payments-hub")["count"] == 3
    assert get(client, "/audit/access-reviews?quarter=2026-Q2")["count"] == 2
    hit = get(client, "/audit/tickets", params={"text": "access review postponed"})["items"]
    assert len(hit) == 1 and "2026-Q2" in hit[0]["title"]
    assert "no review record" in " ".join(get(client, f"/audit/tickets/{hit[0]['ticket_id']}")["comments"]).lower()


def test_ctl_2_change_control_one_without_rollback_one_without_approver(client):
    t = plan(client, "CTL-1002")
    ids = [i["item"].split()[2] for i in t["evidence_plan"]]
    assert ids == ["CHG-2201", "CHG-2202", "CHG-2203", "CHG-2204", "CHG-2205"]
    recs = {i: get(client, f"/audit/changes/{i}") for i in ids}
    assert all(r["critical_system"] for r in recs.values())
    assert [i for i, r in recs.items() if not r["rollback_plan"]] == ["CHG-2203"]
    assert [i for i, r in recs.items() if not r["approver"]] == ["CHG-2204"]
    rows = {r["change_id"]: r for r in get(client, "/audit/changes")["items"]}
    assert rows["CHG-2203"]["rollback_plan_recorded"] is False and rows["CHG-2204"]["approver"] == ""
    assert get(client, "/audit/changes?system=core-banking")["count"] == 2
    assert [r["change_id"] for r in get(client, "/audit/changes", params={"date_from": (TODAY_D.replace(year=2026, month=9, day=1)).isoformat()})["items"]] != []
    assert rows["CHG-2208"]["critical_system"] is False and rows["CHG-2208"]["rollback_plan_recorded"] is False
    tk = get(client, f"/audit/tickets/{recs['CHG-2204']['ticket_id']}")
    assert tk["related_change_id"] == "CHG-2204"
    found = get(client, "/audit/tickets", params={"text": "approval emergency"})["items"]
    assert "Approval for the emergency certificate change" in [f["title"] for f in found]


def test_ctl_3_recovery_tested_yearly_one_system_last_tested_14_months_ago(client):
    t = plan(client, "CTL-1003")
    assert t["systems_in_scope"] == ["core-banking", "payments-hub", "card-platform", "online-banking"]
    cutoff = months_back(TODAY_D, 12)
    latest = {}
    for s in t["systems_in_scope"]:
        rows = get(client, f"/audit/recovery-tests?system={s}")["items"]
        assert len(rows) == 2 and rows[0]["test_date"] > rows[1]["test_date"]
        latest[s] = rows[0]
    old = [s for s, r in latest.items() if date.fromisoformat(r["test_date"]) < cutoff]
    assert old == ["card-platform"] and latest["card-platform"]["test_date"] == months_back(TODAY_D, 14).isoformat()
    assert months_back(TODAY_D, 14) == date(2025, 9, 24)
    full = get(client, f"/audit/recovery-tests/{latest['payments-hub']['recovery_test_id']}")
    assert full["rto_achieved_hours"] > full["rto_target_hours"] and full["findings"]
    assert "moved" in get(client, "/audit/tickets", params={"text": "recovery test card platform"})["items"][0]["title"].lower()


def test_ctl_4_multi_factor_two_service_accounts_exempt(client):
    t = plan(client, "CTL-1004")
    assert t["clause"] == "6.2" and len(t["evidence_plan"]) == 4
    exempt = []
    for s in t["systems_in_scope"]:
        rows = get(client, f"/audit/access-reviews?system={s}")["items"]
        r = get(client, f"/audit/access-reviews/{rows[-1]['review_id']}")
        assert r["quarter"] == "2026-Q3" and r["staff_accounts_with_mfa"] == r["staff_accounts_reviewed"] - len(r["mfa_exemptions"])
        exempt += [(s, e["account_id"], e["account_type"], e["ticket_id"]) for e in r["mfa_exemptions"]]
    assert len(exempt) == 2 and {e[2] for e in exempt} == {"service account"} and {e[0] for e in exempt} == {"payments-hub", "card-platform"}
    found = get(client, "/audit/tickets", params={"text": "multi-factor"})["items"]
    assert {e[3] for e in exempt} <= {f["ticket_id"] for f in found}
    assert get(client, f"/audit/tickets/{exempt[0][3]}")["type"] == "exemption"
    assert get(client, "/audit/tickets?system=online-banking&text=multi-factor")["count"] == 1
    assert get(client, "/audit/tickets", params={"text": "zzz-nothing"})["count"] == 0
    assert get(client, "/audit/tickets", params={"date_from": TODAY, "date_to": TODAY})["count"] == 0


def whole(record):
    return {k: v for k, v in record.items() if k != "demo_data"}


def test_one_list_call_returns_everything_a_control_test_plan_needs(client):
    # An agent may call one operation at most eight times in a turn: one list call must cover a whole plan, with no get per item.
    reviews = get(client, "/audit/access-reviews")["items"]
    assert len(reviews) == 11
    for r in reviews:
        assert r == whole(get(client, f"/audit/access-reviews/{r['review_id']}"))
    by_id = {r["review_id"]: r for r in reviews}
    assert by_id["ACR-1004"]["staff_accounts_with_mfa"] == 145 and by_id["ACR-1004"]["mfa_exemptions"] == []
    assert by_id["ACR-1007"]["mfa_exemptions"][0]["account_id"] == "svc-recon-batch" and by_id["ACR-1007"]["mfa_exemptions"][0]["ticket_id"] == "TKT-3001"
    assert by_id["ACR-1011"]["mfa_exemptions"][0]["account_id"] == "svc-card-feed" and by_id["ACR-1011"]["mfa_exemptions"][0]["ticket_id"] == "TKT-3002"
    # several systems or quarters in one filter; one value still works as before
    assert get(client, "/audit/access-reviews", params={"system": "core-banking,card-platform"})["count"] == 8
    assert get(client, "/audit/access-reviews", params={"quarter": "2026-Q2, 2026-Q3"})["count"] == 5
    assert get(client, "/audit/access-reviews", params={"system": "payments-hub", "quarter": "2026-Q2"})["count"] == 0
    sample = ",".join(f"CHG-220{i}" for i in range(1, 6))
    changes = get(client, "/audit/changes", params={"change_ids": sample})["items"]
    assert [c["change_id"] for c in changes] == sample.split(",")
    for c in changes:
        full = whole(get(client, f"/audit/changes/{c['change_id']}"))
        assert {k: v for k, v in c.items() if k != "rollback_plan_recorded"} == full and c["rollback_plan_recorded"] == bool(full["rollback_plan"])
    assert get(client, "/audit/changes", params={"system": "card-platform,online-banking"})["count"] == 3
    tests = get(client, "/audit/recovery-tests")["items"]
    assert len(tests) == 8 and all(t == whole(get(client, f"/audit/recovery-tests/{t['recovery_test_id']}")) for t in tests)
    assert get(client, "/audit/recovery-tests", params={"system": "card-platform,payments-hub"})["count"] == 4
    tickets = get(client, "/audit/tickets")["items"]
    assert all(t == whole(get(client, f"/audit/tickets/{t['ticket_id']}")) for t in tickets)
    approval = get(client, "/audit/tickets", params={"system": "online-banking", "text": "approval"})["items"]
    tk = [t for t in approval if not t["related_change_id"]]
    assert len(tk) == 1 and tk[0]["status"] == "open" and "No approval has been recorded yet." in tk[0]["comments"]
    assert [t["ticket_id"] for t in get(client, "/audit/tickets", params={"ticket_ids": "TKT-3001,TKT-3002"})["items"]] == ["TKT-3002", "TKT-3001"]
    assert get(client, "/audit/tickets", params={"system": "payments-hub,card-platform", "text": "multi-factor"})["count"] == 2
    for tid in ("CTL-1001", "CTL-1002", "CTL-1003", "CTL-1004"):
        assert all("one call" in i["where_to_look"] for i in plan(client, tid)["evidence_plan"] if i["record_type"] != "ticket")


def pack(**kw):
    base = {"evidence_found": [{"item_no": 1, "record_ids": ["ACR-1001"], "note": "Signed off."}],
            "evidence_missing": [{"item_no": 7, "searched": ["list_access_reviews system=payments-hub quarter=2026-Q2: no record"],
                                  "note": "TKT-3002 says it was postponed."}],
            "exceptions": [{"description": "No access review record for the payments hub for 2026-Q2.", "record_ids": []}], "drafted_by": "tester"}
    base.update(kw)
    return base


def test_evidence_pack_is_a_draft_with_versions_and_gives_no_conclusion(client, store):
    first = get(client, "/audit/access-reviews")["items"][0]["review_id"]
    a = post(client, "/audit/control-tests/CTL-1001/evidence-pack", pack(evidence_found=[{"item_no": 1, "record_ids": [first]}]))
    assert a["applied"] is True and a["kind"] == "draft" and a["draft"]["version"] == 1 and a["draft"]["drafted_by"] == "tester"
    assert a["conclusion"].startswith("none") and a["test_status"] == "open"
    assert not any("conclusion" in k for k in a["draft"])
    b = post(client, "/audit/control-tests/CTL-1001/evidence-pack", pack(evidence_found=[{"item_no": 1, "record_ids": [first]}], drafted_by="agent"))
    assert b["draft"]["version"] == 2
    full = plan(client, "CTL-1001")
    assert [p["version"] for p in full["evidence_packs"]] == [1, 2] and full["status"] == "open"
    assert client.post("/audit/control-tests/CTL-1001/evidence-pack", json=pack(evidence_found=[{"item_no": 99, "record_ids": [first]}]), headers=H).status_code == 422
    assert client.post("/audit/control-tests/CTL-1001/evidence-pack", json=pack(evidence_found=[{"item_no": 1, "record_ids": ["ACR-0000"]}]), headers=H).status_code == 404
    assert client.post("/audit/control-tests/CTL-1001/evidence-pack", json=pack(evidence_found=[{"item_no": 1, "record_ids": []}]), headers=H).status_code == 422
    both = pack(evidence_found=[{"item_no": 1, "record_ids": [first]}], evidence_missing=[{"item_no": 1, "searched": ["x"]}])
    assert client.post("/audit/control-tests/CTL-1001/evidence-pack", json=both, headers=H).status_code == 409
    assert client.post("/audit/control-tests/CTL-9/evidence-pack", json=pack(), headers=H).status_code == 404
    assert store.data["control_tests"]["CTL-1001"]["status"] == "open"


# ---------------------------------------------------------------- events

PLAIN = lambda m: m.endswith(".") and "  " not in m and DASH not in m and "\n" not in m


def test_new_kinds_rotate_through_four_templates(client, store):
    for kind, coll, system in [("onboarding-application", "onb_applications", "onboarding"), ("kyc-review", "kyc_reviews", "onboarding"),
                               ("complaint", "complaints", "complaints"), ("collections-call", "collections_calls", "collections")]:
        n0 = len(store.data[coll])
        out = [post(client, f"/admin/simulate/{kind}", {}) for _ in range(5)]
        ids_ = [o["item_id"] for o in out]
        assert len(set(ids_)) == 5 and len(store.data[coll]) == n0 + 5
        assert all(o["event_type"] == kind and o["system"] == system and o["item_id"] in o["message"] for o in out)
        assert all(PLAIN(o["message"]) for o in out)
    created = [e for e in get(client, "/admin/events")["items"] if e["status"] == "created"]
    assert {e["event_type"] for e in created} == {"onboarding-application", "kyc-review", "complaint", "collections-call"}


def test_simulated_applications_are_complete_and_readable(client):
    shapes = []
    for _ in range(4):
        r = post(client, "/admin/simulate/onboarding-application", {})
        a = get(client, f"/onboarding/applications/{r['item_id']}")
        assert a["status"] == "received" and all(c["received"] for c in a["required_documents"])
        docs = app_docs(client, r["item_id"])
        assert all(150 <= words(x) <= 400 for x in docs.values())
        shapes.append((a["kind"], len(a["form"].get("owners_declared", []))))
    assert shapes == [("individual", 0), ("individual", 0), ("business", 1), ("business", 2)]
    # the second one has an identity card that expired 20 days ago, the fourth has a holding company in Rovaland
    rows = get(client, "/onboarding/applications")["items"]
    new = sorted(r["application_id"] for r in rows if r["application_id"] >= "ONB-1100")
    assert "Date of expiry" in app_docs(client, new[1])["identity_document"]
    assert (date.fromisoformat(line(app_docs(client, new[1])["identity_document"], "Date of expiry")) - TODAY_D).days == -20
    assert get(client, f"/onboarding/applications/{new[3]}")["form"]["owners_declared"][0]["country"] == "Rovaland"


def test_simulated_reviews_complaints_and_calls_are_complete_and_readable(client):
    kinds = []
    for _ in range(4):
        r = post(client, "/admin/simulate/kyc-review", {})
        v = get(client, f"/onboarding/reviews/{r['item_id']}")
        assert v["status"] == "open" and v["fresh_documents"] and v["held_profile"]
        kinds.append((v["customer"]["customer_id"], v["fresh_documents"][0]["doc_type"]))
    assert kinds == [("CUS-1003", "proof_of_address"), ("CUS-1005", "proof_of_address"), ("CUS-1018", "ownership_declaration"),
                     ("CUS-1009", "occupation_letter")]
    subjects = []
    for _ in range(4):
        r = post(client, "/admin/simulate/complaint", {})
        c = get(client, f"/complaints/complaints/{r['item_id']}")
        assert c["status"] == "open" and c["customer_words"] and c["dates"]["acknowledge_due"]
        subjects.append((c["subject"], c["dates"]["acknowledgement_overdue"], len(c["linked_records"]["transactions"])))
    assert [s[0] for s in subjects] == ["Card replacement fee taken twice", "Card declined abroad", "Home loan statement was wrong",
                                        "Overdraft fee after losing my job"]
    assert [s[1] for s in subjects] == [False, False, True, False] and subjects[0][2] == 2
    starts = []
    for _ in range(4):
        r = post(client, "/admin/simulate/collections-call", {})
        c = call(client, r["item_id"])
        assert c["status"] == "unreviewed" and len(c["transcript"]) >= 8 and c["staff"]["name"]
        starts.append(c["started_at"].split(" ")[1][:5])
        times = [t["time"] for t in c["transcript"]]
        assert times == sorted(times)
    assert starts == ["10:10", "20:25", "13:30", "14:05"]


def test_new_kinds_can_be_subscribed_to(client):
    for kind in ("onboarding-application", "kyc-review", "complaint", "collections-call"):
        r = post(client, "/admin/subscriptions", {"event_kind": kind, "url": "http://127.0.0.1:9/x"})
        assert r["subscription"]["event_kind"] == kind
    assert client.post("/admin/subscriptions", json={"event_kind": "nonsense", "url": "http://127.0.0.1:9/x"}, headers=H).status_code == 422
    assert client.post("/admin/simulate/nonsense", headers=H).status_code == 404


def test_reset_restores_the_new_data(client, store):
    post(client, "/onboarding/applications/ONB-1001/decision", {"decision": "approve", "decided_by": "x"})
    post(client, "/onboarding/reviews/KYR-1001/profile-draft", profile(changes=[], unchanged_fields=["address"]))
    post(client, "/complaints/complaints/CMP-1001/response-draft", response())
    post(client, "/complaints/complaints/CMP-1001/send", {"approved_by": "x"})
    post(client, "/collections/calls/CAL-1001/review", call_review())
    post(client, "/audit/control-tests/CTL-1002/evidence-pack", {"exceptions": [{"description": "x"}]})
    for kind in ("onboarding-application", "kyc-review", "complaint", "collections-call"):
        post(client, f"/admin/simulate/{kind}", {})
    assert len(store.data["complaints"]) == 7
    assert post(client, "/admin/reset", {})["applied"] is True
    assert store.data == build_all(TODAY_D)
    counts = get(client, "/admin/state")["counts"]
    assert counts["open_onboarding_applications"] == 6 and counts["open_complaints"] == 5 and counts["unreviewed_collections_calls"] == 5
    assert get(client, "/onboarding/applications/ONB-1001")["status"] == "received"
    assert get(client, "/audit/control-tests/CTL-1002")["evidence_packs"] == []


def test_data_is_identical_for_same_date_and_changes_with_the_date():
    assert build_all(date(2026, 11, 24)) == build_all(date(2026, 11, 24))
    other = build_all(date(2026, 11, 25))
    assert other["complaints"]["CMP-1005"]["received"] != build_all(date(2026, 11, 24))["complaints"]["CMP-1005"]["received"]
    # whatever the bank date, the unacknowledged complaint is 13 working days old
    for day in (date(2026, 11, 25), date(2026, 11, 28), date(2026, 12, 2)):
        rec = date.fromisoformat(build_all(day)["complaints"]["CMP-1005"]["received"])
        assert working_days_between(rec, day) == 13 and rec.weekday() < 5


def test_state_file_from_an_older_version_still_loads(tmp_path):
    from fastapi.testclient import TestClient
    from bank.app import create_app
    from conftest import make_env
    env = make_env(DATA_DIR=str(tmp_path / "state"))
    c = TestClient(create_app(env))
    c.post("/cards/cards/CRD-2001/block", json={"reason": "lost"}, headers=H)
    f = tmp_path / "state" / "demo-bank-state.json"
    saved = json.loads(f.read_text())
    for k in ("onb_applications", "kyc_reviews", "complaints", "collections_calls", "control_tests", "tickets"):
        saved["data"].pop(k)
    f.write_text(json.dumps(saved))
    again = TestClient(create_app(env))
    assert again.get("/complaints/complaints", headers=H).json()["count"] == 6
    assert again.get("/audit/control-tests", headers=H).json()["count"] == 4


# ---------------------------------------------------------------- addresses behind a gateway

def test_public_scheme_setting_wins_over_the_headers(client, monkeypatch):
    monkeypatch.setenv("BANK_PUBLIC_SCHEME", "https")
    page = client.get("/", headers={"X-Forwarded-Proto": "http"}).text
    assert "https://testserver/core/openapi.json" in page and "http://testserver" not in page
    feed = client.get("/regulator/feed.xml").text
    assert "https://testserver/regulator/publications/" in feed and "http://testserver" not in feed
    monkeypatch.setenv("BANK_PUBLIC_SCHEME", "ftp")  # not a scheme the bank serves: ignored
    assert "http://testserver/core/openapi.json" in client.get("/").text


def test_forwarded_proto_gives_https_addresses(client):
    fwd = {"X-Forwarded-Proto": "https"}
    page = client.get("/", headers=fwd).text
    assert "https://testserver/core/openapi.json" in page and "https://testserver/audit/mcp" in page and "http://testserver" not in page
    plain = client.get("/").text
    assert "http://testserver/core/openapi.json" in plain
    both = client.get("/", headers={"X-Forwarded-Proto": "https, http"}).text
    assert "https://testserver/core/openapi.json" in both
    a = client.get("/news/articles/ART-6001", headers={**H, **fwd}).json()
    assert a["page_url"] == "https://testserver/news/pages/ART-6001"
    assert client.get("/news/articles/ART-6001", headers=H).json()["page_url"].startswith("http://")
    feed = client.get("/regulator/feed.xml", headers=fwd).text
    assert "https://testserver/regulator/publications/" in feed and "http://testserver" not in feed
    assert client.get("/regulator/publications/MFCA-2026-045", headers=fwd).status_code == 200
    body = {"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "get_news_article", "arguments": {"article_id": "ART-6001"}}}
    r = client.post("/news/mcp", json=body, headers={**H, **fwd}).json()
    assert json.loads(r["result"]["content"][0]["text"])["page_url"] == "https://testserver/news/pages/ART-6001"


# ---------------------------------------------------------------- records that describe the same thing agree

def test_car_loan_of_cus_1012_agrees_between_exposure_statements_and_core(client):
    ex = get(client, "/core/customers/CUS-1012/exposure")
    loan = ex["loans"][0]
    assert loan["loan_id"] == "LN-9005" and loan["product"] == "Car loan"
    app = get(client, "/lending/applications/LAP-8001")
    assert app["form_fields"]["existing_monthly_debt_payments"] == 450.0
    stmt = get(client, "/lending/applications/LAP-8001/documents/DOC-8103")["text"]
    assert stmt.count("Car loan instalment               -450.00") == 3
    rows = get(client, "/core/accounts/ACC-1012-01/transactions")["items"]
    assert sorted(t["amount"] for t in rows if t["type"] == "loan_repayment") == [450.0, 450.0]
    assert {t["amount"] for t in rows if t["type"] == "salary"} == {4010.0}
    assert {t["counterparty"] for t in rows if t["type"] == "salary"} == {"Westergate Water Board"}
    assert not [t for t in rows if t["narrative"] == "Rent"]
    call = get(client, "/collections/calls/CAL-1001")
    assert call["arrears"]["monthly_instalment"] == 450.0 and "car loan LN-9005" in call["transcript"][6]["text"]
    assert call["loan"]["product"] == "Car loan"


def test_equipment_loan_of_cus_1018_agrees_with_the_financial_statements(client):
    loan = get(client, "/core/customers/CUS-1018/exposure")["loans"][0]
    assert loan["loan_id"] == "LN-9002" and loan["outstanding"] == 180000.0
    fs = get(client, "/lending/applications/LAP-8003/documents/DOC-8302")["text"]
    latest = lambda label: int(next(l for l in fs.splitlines() if l.startswith(label)).split()[-1].replace(",", ""))
    assert latest("Long-term debt") + latest("Current portion of long-term debt") == loan["outstanding"]
    assert round(loan["outstanding"] / latest("Total equity"), 2) == 0.26
    rows = get(client, "/core/accounts/ACC-1018-01/transactions", params={"limit": 500})["items"]
    credits = sorted(t["amount"] for t in rows if t["narrative"] == "Customer receipts, month total")
    assert credits == [137500.0, 138100.0, 142400.0]


def test_business_account_credits_agree_with_the_bank_statements_in_the_applications(client):
    rows = get(client, "/core/accounts/ACC-1017-01/transactions", params={"limit": 500})["items"]
    stmt = get(client, "/lending/applications/LAP-8002/documents/DOC-8203")["text"]
    for t in rows:
        if t["narrative"] == "Customer receipts, month total":
            assert f"{t['amount']:,.2f}" in stmt
    assert len([t for t in rows if t["narrative"] == "Customer receipts, month total"]) == 3
    home = get(client, "/core/accounts/ACC-1013-01/transactions")["items"]
    assert [t["amount"] for t in home if t["type"] == "loan_repayment"] == [930.0]
    assert get(client, "/collections/calls/CAL-1002")["arrears"]["monthly_instalment"] == 930.0
