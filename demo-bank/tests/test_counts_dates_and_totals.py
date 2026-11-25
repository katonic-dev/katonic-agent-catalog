"""Tests for the systems that give a count or a total so that an agent never works one out: the totals of a contribution
batch, the bank's date and the age of each onboarding document, a nationality given by name, the held total of a
client, the identity card's machine-readable line, the self-employment letter, the change date in the incident
timeline, and the refused save of differences on a loan whose funds were released."""

from datetime import date

from fastapi.testclient import TestClient

from bank.app import create_app
from conftest import H, TODAY, make_env


def get(client, path, status=200, **kw):
    r = client.get(path, headers=H, **kw)
    assert r.status_code == status, (path, r.status_code, r.text[:300])
    return r.json()


def post(client, path, body=None, status=200):
    r = client.post(path, json=body or {}, headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:400])
    return r.json()


def result(batch, failed=None):
    failed = failed or {}
    return {"rows": [{"row_no": r["row_no"], "outcome": "failed" if r["row_no"] in failed else "passed", "failed_rules": failed.get(r["row_no"], [])}
                     for r in batch["rows"]], "summary": "Checked."}


# ------------------------------------------------------------------ 1. contribution batch totals

def test_each_batch_row_carries_its_total(client, store):
    b = get(client, "/funds/batches/BAT-4002")
    assert all(r["row_total"] == round(r["employee_amount"] + r["employer_amount"], 2) for r in b["rows"])
    assert "row_total" not in store.data["pension_batches"]["BAT-4002"]["rows"][0]


def test_saved_batch_result_returns_counts_and_totals(client, store):
    b = get(client, "/funds/batches/BAT-4002")
    saved = post(client, "/funds/batches/BAT-4002/result", result(b, {4: [1], 5: [3], 6: [2]}))
    want = {"rows_passed": 3, "rows_failed": 3, "total_passed": 1215.5, "total_failed": 667.5, "total_all_rows": 1883.0,
            "control_total": 1883.0, "control_total_difference": 0.0}
    assert {k: saved[k] for k in want} == want
    assert saved["draft"]["totals"] == want and store.data["pension_batches"]["BAT-4002"]["results"][-1]["totals"] == want
    clean = get(client, "/funds/batches/BAT-4001")
    done = post(client, "/funds/batches/BAT-4001/result", result(clean))
    assert (done["rows_passed"], done["rows_failed"], done["total_passed"], done["total_failed"]) == (5, 0, 1959.1, 0.0)
    assert done["control_total"] == 1959.1 and done["control_total_difference"] == 0.0


def test_batch_totals_show_a_control_total_that_disagrees(client, store):
    store.data["pension_batches"]["BAT-4001"]["control_total"] = 2000.0
    b = get(client, "/funds/batches/BAT-4001")
    done = post(client, "/funds/batches/BAT-4001/result", result(b, {2: [4]}))
    assert done["total_all_rows"] == 1959.1 and done["control_total_difference"] == 40.9
    assert done["rows_passed"] == 4 and done["rows_failed"] == 1
    assert round(done["total_passed"] + done["total_failed"], 2) == 1959.1


# ------------------------------------------------------------------ 2. the bank's date and document ages

def test_onboarding_reads_give_the_bank_date_and_document_ages(client):
    for path in ("/onboarding/applications/ONB-1001", "/onboarding/applications", "/onboarding/reviews", "/onboarding/reviews/KYR-1002",
                 "/onboarding/applications/ONB-1001/documents", "/onboarding/applications/ONB-1001/documents/OND-1001-02",
                 "/onboarding/reviews/KYR-1001/documents/KYD-1001-02"):
        assert get(client, path)["read_on"] == TODAY, path
    ages = {x["document_id"]: (x["document_date"], x["age_days_at_bank_date"]) for x in get(client, "/onboarding/applications/ONB-1001")["documents_received"]}
    assert ages["OND-1001-02"] == ("2026-10-29", 26)
    assert get(client, "/onboarding/applications/ONB-1002/documents/OND-1002-02")["age_days_at_bank_date"] == 150
    assert get(client, "/onboarding/applications/ONB-1004/documents/OND-1004-01")["document_date"] == "2026-11-12"
    assert get(client, "/onboarding/applications/ONB-1004/documents/OND-1004-01")["age_days_at_bank_date"] == 12
    rev = {x["document_id"]: x for x in get(client, "/onboarding/reviews/KYR-1001")["fresh_documents"]}
    assert (rev["KYD-1001-02"]["document_date"], rev["KYD-1001-02"]["age_days_at_bank_date"]) == ("2026-10-22", 33)
    kyd = get(client, "/onboarding/reviews/KYR-1002/documents/KYD-1002-01")
    assert (kyd["document_date"], kyd["age_days_at_bank_date"]) == ("2026-11-10", 14)
    for a in get(client, "/onboarding/applications")["items"]:
        for x in get(client, f"/onboarding/applications/{a['application_id']}/documents")["items"]:
            assert x["document_date"] and x["age_days_at_bank_date"] == (date.fromisoformat(TODAY) - date.fromisoformat(x["document_date"])).days


def test_core_reads_give_the_bank_date_and_keep_every_other_field(client):
    paths = ("/core/customers?customer_id=CUS-1009", "/core/customers/CUS-1009/accounts",
             "/core/accounts/ACC-1009-01/transactions", "/core/customers/CUS-1009/contacts")
    for path in paths:
        body = get(client, path)
        assert body["read_on"] == TODAY, path
        assert {"count", "items"} <= set(body), path
    txns = get(client, "/core/accounts/ACC-1009-01/transactions")
    assert txns["account_id"] == "ACC-1009-01" and txns["total_matches"] == txns["count"]
    later = TestClient(create_app(make_env(BANK_TODAY="2027-03-02")))
    assert later.get("/core/customers/CUS-1009/accounts", headers=H).json()["read_on"] == "2027-03-02"


def test_document_ages_follow_the_bank_date_not_the_clock():
    later = TestClient(create_app(make_env(BANK_TODAY="2027-03-02")))
    doc = later.get("/onboarding/applications/ONB-1001/documents/OND-1001-02", headers=H).json()
    assert doc["read_on"] == "2027-03-02" and doc["age_days_at_bank_date"] == 26


# ------------------------------------------------------------------ 3. nationality by name or code

def test_screening_nationality_matches_by_code_or_name(client):
    for given in ("XB", "xb", "Brevnia", "BREVNIA"):
        hits = post(client, "/screening/search", {"name": "Wynn Castellano", "date_of_birth": "1962-02-02", "country": given})["items"]
        assert hits[0]["entry_id"] == "WL-9001" and hits[0]["nationality"] == "match" and hits[0]["date_of_birth"] == "match", given
    other = post(client, "/screening/search", {"name": "Wynn Castellano", "date_of_birth": "1962-02-02", "country": "Meridia"})["items"]
    assert other[0]["nationality"] == "differs"
    none = post(client, "/screening/search", {"name": "Wynn Castellano"})["items"]
    assert none[0]["nationality"] == "unknown"


# ------------------------------------------------------------------ 4, 5. the identity card and the self-employment letter

def test_identity_card_line_uses_the_card_country(client):
    brevnia = get(client, "/onboarding/applications/ONB-1003/documents/OND-1003-01")["text"]
    assert "Machine-readable line: IDXB<<WYNN<CASTELLANO<<" in brevnia and "Registry of Persons, Brevnia" in brevnia and "IDXM" not in brevnia
    meridia = get(client, "/onboarding/applications/ONB-1001/documents/OND-1001-01")["text"]
    assert "Machine-readable line: IDXM<<" in meridia and "IDMXM" not in meridia


def test_self_employment_letter_reads_as_self_employment(client):
    text = get(client, "/onboarding/reviews/KYR-1002/documents/KYD-1002-02")["text"]
    for word in ("works for", "payroll", "a few weeks", "Gross monthly pay"):
        assert word not in text
    assert "self-employed building surveyor" in text and "no employer" in text.lower()
    assert "dated 2026-11-14, 4 days before the bank received it on 2026-11-18" in text


# ------------------------------------------------------------------ 7. the change date in the incident timeline

def test_incident_timeline_gives_the_change_date(client):
    inc = get(client, "/itops/incidents/INC-7002")
    entry = next(t["entry"] for t in inc["timeline"] if "ITC-8104" in t["entry"])
    assert "on 12 Nov 2026 (ITC-8104)" in entry and "days ago" not in entry


# ------------------------------------------------------------------ 8. the held total of a client

def test_client_holdings_give_the_held_total(client):
    t = get(client, "/crm/clients/CUS-1011/holdings")["totals"]
    assert (t["deposits_usd"], t["investments_usd"], t["held_usd"]) == (6569.48, 29676.74, 36246.22)
    for cid in ("CUS-1018", "CUS-1013", "CUS-1001"):
        t = get(client, f"/crm/clients/{cid}/holdings")["totals"]
        assert t["held_usd"] == round(t["deposits_usd"] + t["investments_usd"], 2)


# ------------------------------------------------------------------ 10. a refused save on a loan whose funds were released

def test_save_of_differences_refused_on_a_released_loan(client, store):
    terms = get(client, "/lending/loans/LN-9006/approved-terms")
    assert terms["funds_released_on"] == "2026-10-25" and terms["amount"] == 40000.0
    assert [x["document_id"] for x in get(client, "/lending/loans/LN-9006/documents")["items"]] == ["DOC-9601"]
    r = client.post("/lending/loans/LN-9006/document-differences", json={"differences": []}, headers=H)
    assert r.status_code == 409 and r.json()["applied"] is False
    assert "released on 25 Oct 2026" in r.json()["detail"] and "Nothing was saved." in r.json()["detail"]
    assert "LN-9006" not in store.data["document_differences"]
    assert "funds_released_on" not in get(client, "/lending/loans/LN-9001/approved-terms")
    ok = post(client, "/lending/loans/LN-9001/document-differences", {"differences": []})
    assert ok["applied"] is True
