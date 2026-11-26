"""The investigations system: the right answers of the Investigations section of SCENARIOS.md, every refusal, and the rules drafts keep.

Checked against the data the service gives at the insurer date 2026-11-26."""
import json
import re
from datetime import date

from insurer.seed import build_all
from insurer.seed_investigations import build_investigations
from conftest import H, TODAY

TODAY_D = date.fromisoformat(TODAY)
OWN_SETS = sorted(build_investigations(TODAY_D))


def get(client, path, status=200):
    r = client.get(f"/investigations{path}", headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:300])
    return r.json()


def post(client, path, body=None, status=200):
    r = client.post(f"/investigations{path}", json=body or {}, headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:400])
    return r.json()


def paid(client, n):
    return get(client, f"/closed-claims/CLM-{n}/should-have-been-paid")


def results(k):
    return {r["standard_id"]: r["result"] for r in k["standards"]}


def indicators(client, n):
    k = get(client, f"/claims/CLM-{n}/indicators")
    return k, {r["indicator_id"]: r for r in k["indicators"]}


def links(client, n):
    return get(client, f"/claims/CLM-{n}/links")


# ---------------------------------------------------------------- the service as a whole
def test_the_system_has_21_operations_and_every_one_that_writes_is_a_draft(client):
    doc = client.get("/investigations/openapi.json").json()
    ops = [(method, op) for item in doc["paths"].values() for method, op in item.items()]
    assert len(ops) == 21
    writes = sorted(op["operationId"] for method, op in ops if method != "get")
    assert writes == ["save_case_file", "save_fraud_referral", "save_leakage_finding"]
    for method, op in ops:
        assert "(change)" not in op["summary"], op["operationId"]
        if method != "get":
            assert op["summary"].endswith("(draft)"), op["operationId"]
    assert client.get("/investigations/claims").status_code == 401 and "investigations/openapi.json" in client.get("/").text


def test_ids_do_not_collide_with_the_other_systems_and_keep_their_ranges():
    data = build_all(TODAY_D)
    seen = {}
    for name, records in data.items():
        if isinstance(records, dict):
            for key in records:
                assert key not in seen, (key, name, seen.get(key))
                seen[key] = name
    prefixes = {"leakage_standards": "LS-", "leakage_claims": "CLM-61", "fraud_indicators": "FI-", "investigation_policies": "POL-27",
                "investigation_parties": "PTY-3", "investigation_claims": "CLM-6", "public_notices": "PN-9"}
    assert sorted(prefixes) == OWN_SETS
    for name, prefix in prefixes.items():
        assert all(key.startswith(prefix) for key in data[name]), name
    assert len(data["policies"]) == 14 and len(data["claims"]) == 10  # the policy and claims systems are as they were


def test_no_document_holds_a_bare_date_or_counts_days_and_everything_is_marked_invented():
    data = build_investigations(TODAY_D)
    texts = [doc["text"] for c in data["investigation_claims"].values() for doc in c["documents"]]
    texts += [n["text"] for n in data["public_notices"].values()]
    assert len(texts) == 33
    for text in texts:
        assert not re.search(r"\b20\d\d-\d\d-\d\d\b", text), text
    blob = json.dumps(data).lower()
    for word in ("yesterday", "last week", "days ago", "weeks ago", "last month", "this morning", "tomorrow", "monday", "tuesday",
                 "wednesday", "thursday", "friday", "saturday", "sunday", chr(8212)):
        assert word not in blob, word
    people = data["investigation_parties"].values()
    assert all(p["phone"].startswith("+999 555 ") for p in people)
    assert all(p["bank_account"].startswith("DEMO-ACCT-") for p in people if p["kind"] == "person")
    assert all(p["address"].endswith(", Meridia") for p in people)
    assert all(n["invented"] is True and "invented" in n["source"] for n in data["public_notices"].values())


# ---------------------------------------------------------------- leakage review: the standards and the list
def test_the_six_handling_standards(client):
    out = get(client, "/handling-standards")
    assert [s["standard_id"] for s in out["items"]] == ["LS-1", "LS-2", "LS-3", "LS-4", "LS-5", "LS-6"]
    text = {s["standard_id"]: s["text"] for s in out["items"]}
    assert "USD 500 for a home escape of water claim" in text["LS-1"] and "USD 2,500 for any one item" in text["LS-2"]
    assert "more than USD 5,000" in text["LS-3"] and "rule HG-7" in text["LS-4"] and "same invoice number" in text["LS-5"]
    assert "neither met nor broken" in out["how_to_apply"]


def test_the_review_period_and_the_eight_closed_claims(client):
    out = get(client, "/closed-claims")
    assert out["review_period"] == {"closed_from": "2026-10-27", "closed_to": "2026-11-26",
                                    "sentence": "Claims closed from 27 Oct 2026 to 26 Nov 2026."}
    assert [(c["claim_id"], c["policy_id"], c["claimant"], c["loss_date"], c["closed_on"], c["payment_file"]["total_paid"]) for c in out["items"]] == [
        ("CLM-6101", "POL-2011", "Isaura Venn", "2026-10-17", "2026-11-05", 1680.0),
        ("CLM-6102", "POL-2701", "Fenwick Aldergrove", "2026-10-02", "2026-11-08", 6854.0),
        ("CLM-6103", "POL-2001", "Corwin Ashgrove", "2026-10-09", "2026-11-01", 1940.0),
        ("CLM-6104", "POL-2002", "Elspeth Marrowdene", "2026-10-13", "2026-11-12", 4000.0),
        ("CLM-6105", "POL-2702", "Ignatius Corbrook", "2026-10-05", "2026-11-18", 4740.0),
        ("CLM-6106", "POL-2014", "Ansel Whitlocke", "2026-10-20", "2026-11-15", 6850.0),
        ("CLM-6107", "POL-2703", "Sunniva Marchbank", "2026-10-15", "2026-11-10", 2560.0),
        ("CLM-6108", "POL-2012", "Elric Stannaway", "2026-10-07", "2026-11-20", 2210.0)]
    assert all("leakage_finding_drafts" not in c and c["drafts_on_file"] == 0 for c in out["items"])
    narrow = get(client, "/closed-claims?closed_from=2026-11-10&closed_to=2026-11-15")
    assert [c["claim_id"] for c in narrow["items"]] == ["CLM-6104", "CLM-6106", "CLM-6107"]
    assert get(client, "/closed-claims?closed_from=10-11-2026", 422)["applied"] is False


def test_a_payment_file_reads_the_policy_from_where_it_is_held(client):
    c = get(client, "/closed-claims/CLM-6103")
    assert c["policy"]["held_in"] == "the policy system" and c["policy"]["schedule"]["deductible"] == 250.0
    assert c["cover_on_loss_date"]["in_force"] is True and c["payment_file"]["settlement_record"]["deductible_taken"] == 0.0
    own = get(client, "/closed-claims/CLM-6102")
    assert own["policy"]["held_in"] == "the investigations system only" and own["policy"]["holder"] == "Fenwick Aldergrove"
    assert own["other_party_at_fault"]["name"] == "Hollis Drummock" and own["payment_file"]["recovery"]["reference"] == "REC-0412"
    assert client.get("/policy/policies/POL-2701", headers=H).status_code == 404  # the policy system's list is as it was


# ---------------------------------------------------------------- leakage review: the eight right answers
def test_clm_6101_was_paid_correctly_and_the_limit_rule_does_not_fire(client):
    k = paid(client, 6101)
    assert (k["should_have_been_paid"], k["amount_paid"], k["difference"], k["outcome"]) == (1680.0, 1680.0, 0.0, "paid_within_the_standards")
    assert set(results(k).values()) == {"met"} and k["standards_not_met"] == [] and k["saved"] is False
    glass = k["lines"][1]
    assert (glass["amount_invoiced"], glass["limit"], glass["limit_clause"], glass["amount_allowed_on_the_file"], glass["allowed_over_the_limit"]) == (
        610.0, 500.0, "3.2", 500.0, 0.0)
    assert k["working"] == ["Lines under the standards: 1,480.00 + 500.00 = 1,980.00",
                            "Less the deductible due under clause 4.1: 1,980.00 - 300.00 = 1,680.00",
                            "Paid: 1,680.00 = 1,680.00", "Difference: 1,680.00 - 1,680.00 = 0.00"]


def test_clm_6102_was_paid_correctly_with_a_second_approval_and_a_recovery(client):
    k = paid(client, 6102)
    assert (k["should_have_been_paid"], k["amount_paid"], k["difference"], k["outcome"]) == (6854.0, 6854.0, 0.0, "paid_within_the_standards")
    assert set(results(k).values()) == {"met"}
    assert k["authority"]["approval_needed_from"] == "senior adjuster" and k["authority"]["approval_with_the_authority_is_on_the_file"] is True
    measured = {r["standard_id"]: r["measured"] for r in k["standards"]}
    assert "Fenella Arkwright, senior adjuster" in measured["LS-3"]
    assert measured["LS-4"] == "The file names Hollis Drummock as at fault. Recovery REC-0412 was raised on 7 Nov 2026."
    assert k["lines"][1]["limit"] == 304.0 and k["lines"][1]["allowed_over_the_limit"] == 0.0


def test_clm_6103_the_deductible_was_not_taken(client):
    k = paid(client, 6103)
    assert (k["should_have_been_paid"], k["amount_paid"], k["difference"]) == (1690.0, 1940.0, 250.0)
    assert k["standards_not_met"] == ["LS-1"] and k["outcome"] == "paid_outside_the_standards"
    assert k["deductible"] == {"due": 250.0, "clause": "4.1", "taken": 0.0, "not_taken": 250.0}
    row = k["standards"][0]
    assert row["amount"] == 250.0 and row["measured"] == ("The deductible due is USD 250.00 (clause 4.1). The settlement record shows "
                                                         "USD 0.00 taken. USD 250.00 was not taken.")
    assert k["outcome_sentence"] == ("CLM-6103 was paid outside the handling standards: LS-1 not met. USD 1,690.00 should have been paid "
                                     "and USD 1,940.00 was paid, a difference of USD 250.00.")


def test_clm_6104_a_line_was_paid_over_its_limit(client):
    k = paid(client, 6104)
    assert (k["should_have_been_paid"], k["amount_paid"], k["difference"], k["standards_not_met"]) == (3100.0, 4000.0, 900.0, ["LS-2"])
    line = k["lines"][0]
    assert (line["line_id"], line["limit"], line["limit_clause"], line["amount_under_the_standards"], line["allowed_over_the_limit"]) == (
        "CLM-6104-L1", 2500.0, "3.2", 2500.0, 900.0)
    row = next(r for r in k["standards"] if r["standard_id"] == "LS-2")
    assert row["amount"] == 900.0 and "USD 3,400.00 was allowed on the file where the limit is USD 2,500.00 (clause 3.2)" in row["measured"]
    assert results(k)["LS-3"] == "met"  # 4,000.00 is within the handler's authority


def test_clm_6105_an_invoice_was_paid_twice(client):
    k = paid(client, 6105)
    assert (k["should_have_been_paid"], k["amount_paid"], k["difference"], k["standards_not_met"]) == (2690.0, 4740.0, 2050.0, ["LS-5"])
    assert k["payments_that_repeat_an_invoice"] == [{
        "payment_id": "CLM-6105-P3", "repeats_payment_id": "CLM-6105-P1", "payee": "Marlow Reach Joinery", "invoice_number": "MRJ-0448",
        "amount": 2050.0, "paid_on": "2026-11-08", "first_paid_on": "2026-10-30"}]
    row = next(r for r in k["standards"] if r["standard_id"] == "LS-5")
    assert row["amount"] == 2050.0 and row["measured"] == ("CLM-6105-P3 of USD 2,050.00 to Marlow Reach Joinery on 8 Nov 2026 is against "
                                                          "invoice MRJ-0448, which CLM-6105-P1 had paid on 30 Oct 2026.")
    assert results(k)["LS-3"] == "met"  # 4,740.00 in all is still within the handler's authority


def test_clm_6106_was_paid_above_authority_with_no_second_approval(client):
    k = paid(client, 6106)
    assert (k["should_have_been_paid"], k["amount_paid"], k["difference"], k["standards_not_met"]) == (6850.0, 6850.0, 0.0, ["LS-3"])
    assert k["authority"]["approval_needed_from"] == "senior adjuster" and k["authority"]["approval_with_the_authority_is_on_the_file"] is False
    row = next(r for r in k["standards"] if r["standard_id"] == "LS-3")
    assert row["measured"] == ("USD 6,850.00 was paid in all. That needs the approval of the senior adjuster (rule HG-5). Approval on "
                               "the file: Ottilie Marsh, handler. No approval by a senior adjuster is on the file.")
    assert k["outcome"] == "paid_outside_the_standards"


def test_clm_6107_no_recovery_was_raised(client):
    k = paid(client, 6107)
    assert (k["should_have_been_paid"], k["amount_paid"], k["difference"], k["standards_not_met"]) == (2560.0, 2560.0, 0.0, ["LS-4"])
    row = next(r for r in k["standards"] if r["standard_id"] == "LS-4")
    assert row["measured"] == ("The file names Edric Vollenhoe as at fault. The other driver's signed statement of 16 Oct 2026 says he "
                               "reversed into the parked vehicle. No recovery is raised on the file. USD 2,560.00 was paid on the claim.")
    assert get(client, "/closed-claims/CLM-6107")["payment_file"]["recovery"] == {"raised": False, "reference": None, "raised_on": None}


def test_clm_6108_has_an_incomplete_record_and_needs_a_person(client):
    k = paid(client, 6108)
    assert k["can_be_worked_out"] is False and k["outcome"] == "cannot_tell_needs_a_person"
    assert (k["should_have_been_paid"], k["difference"], k["amount_paid"]) == (None, None, 2210.0)
    assert k["standards_not_met"] == [] and k["standards_that_cannot_be_told"] == ["LS-2"]
    assert k["what_is_missing"] == ["Invoice DDD-2291 from Dunmere Drying and Decorating: payment CLM-6108-P2 of USD 1,930.00 was made "
                                    "against it and the invoice is not on the file."]
    assert k["deductible"] == {"due": 500.0, "clause": "4.2", "taken": 500.0, "not_taken": 0.0} and results(k)["LS-1"] == "met"
    assert "DDD-2291" in get(client, "/closed-claims/CLM-6108")["payment_file"]["file_notes"][0]


def test_the_cover_standard_is_met_on_all_eight_and_a_check_changes_nothing(client, store):
    for n in range(6101, 6109):
        assert results(paid(client, n))["LS-6"] == "met", n
    assert store.data == build_all(TODAY_D)


# ---------------------------------------------------------------- leakage review: the draft
def test_a_leakage_finding_is_a_draft_with_the_systems_figures_and_changes_nothing(client, store):
    body = {"outcome": "paid outside the standards", "standards": [{"standard_id": "ls 1", "finding": "not met", "note": "250.00 not taken."}]}
    r = post(client, "/closed-claims/CLM-6103/findings", body)
    assert r["kind"] == "draft" and r["draft"]["version"] == 1 and r["draft"]["outcome"] == "paid_outside_the_standards"
    assert r["draft"]["standards"][0] == {"standard_id": "LS-1", "finding": "not_met", "note": "250.00 not taken."}
    assert r["draft"]["figures_worked_out_by_the_system"] == {
        "should_have_been_paid": 1690.0, "amount_paid": 1940.0, "difference": 250.0, "standards_not_met": ["LS-1"],
        "standards_that_cannot_be_told": [], "outcome": "paid_outside_the_standards"}
    assert post(client, "/closed-claims/CLM-6103/findings", {**body, "drafted_by": "Leakage review"})["draft"]["version"] == 2
    fresh = build_all(TODAY_D)["leakage_claims"]["CLM-6103"]
    stored = {k: v for k, v in store.data["leakage_claims"]["CLM-6103"].items() if k != "leakage_finding_drafts"}
    assert stored == {k: v for k, v in fresh.items() if k != "leakage_finding_drafts"}
    c = get(client, "/closed-claims/CLM-6103")
    assert "leakage_finding_drafts" not in c and c["drafts_on_file"] == 2 and "paid_outside_the_standards" not in json.dumps(c)
    assert "paid_outside_the_standards" not in json.dumps(get(client, "/closed-claims"))
    drafts = get(client, "/closed-claims/CLM-6103/findings")
    assert drafts["count"] == 2 and drafts["items"][1]["drafted_by"] == "Leakage review"
    assert post(client, "/closed-claims/CLM-6101/findings", {"outcome": "paid_within_the_standards"})["applied"] is True
    missing = {"outcome": "cannot_tell_needs_a_person", "standards": [{"standard_id": "LS-2", "finding": "cannot_tell"}],
               "what_is_missing": "Invoice DDD-2291 is not on the file."}
    assert post(client, "/closed-claims/CLM-6108/findings", missing)["draft"]["figures_worked_out_by_the_system"]["should_have_been_paid"] is None


def test_a_leakage_finding_is_refused_with_a_plain_sentence_and_nothing_saved(client, store):
    def refused(body, words):
        r = post(client, "/closed-claims/CLM-6104/findings", body, 409)
        assert words in r["detail"] and "Nothing was saved" in r["detail"] and r["applied"] is False
        assert store.data["leakage_claims"]["CLM-6104"]["leakage_finding_drafts"] == []

    row = {"standard_id": "LS-2", "finding": "not_met"}
    refused({"outcome": "paid_outside_the_standards", "standards": [{"standard_id": "LS-9", "finding": "not_met"}]}, "Not a standard or given twice: LS-9")
    refused({"outcome": "paid_outside_the_standards", "standards": [row, row]}, "an id given twice")
    refused({"outcome": "paid_outside_the_standards"}, "needs one row for each standard that is not met")
    refused({"outcome": "paid_within_the_standards", "standards": [row]}, "takes no row that says not_met or cannot_tell")
    refused({"outcome": "cannot_tell_needs_a_person"}, "needs what_is_missing")
    assert client.post("/investigations/closed-claims/CLM-6104/findings", headers=H, json={"outcome": "recover the money"}).status_code == 422
    assert "read it with get_claim_for_checking" in post(client, "/closed-claims/CLM-6201/findings", {"outcome": "paid_within_the_standards"}, 404)["detail"]


# ---------------------------------------------------------------- fraud check: the indicators and the list
def test_the_six_indicators_and_the_eight_new_claims(client):
    out = get(client, "/fraud-indicators")
    assert [(i["indicator_id"], i["threshold"], i["unit"]) for i in out["items"]] == [
        ("FI-1", 30, "days"), ("FI-2", 3, "earlier claims"), ("FI-3", 3, "claims"), ("FI-4", 1, "unrelated claimants"),
        ("FI-5", 1, "days"), ("FI-6", 95.0, "percent")]
    assert "only when the name and the date of birth are both the same" in out["how_to_apply"]
    rows = get(client, "/claims")["items"]
    assert [(c["claim_id"], c["policy_id"], c["claimant"], c["loss_date"], c["reported_date"], c["estimate"]) for c in rows] == [
        ("CLM-6201", "POL-2711", "Perpetua Hollowell", "2026-11-20", "2026-11-21", 1820.0),
        ("CLM-6202", "POL-2712", "Lorcan Whitmarsh", "2026-11-19", "2026-11-20", 10920.0),
        ("CLM-6203", "POL-2713", "Benedikt Farrowdale", "2026-11-18", "2026-11-18", 9600.0),
        ("CLM-6204", "POL-2714", "Clementine Durrow", "2026-11-17", "2026-11-18", 3360.0),
        ("CLM-6205", "POL-2715", "Rafferty Coombe", "2026-11-21", "2026-11-22", 2900.0),
        ("CLM-6206", "POL-2716", "Marguerite Ashdown", "2026-11-16", "2026-11-17", 4200.0),
        ("CLM-6207", "POL-2717", "Thaddeus Wren", "2026-11-21", "2026-11-22", 17640.0),
        ("CLM-6208", "POL-2718", "Gideon Marlowe", "2026-11-22", "2026-11-23", 2480.0)]
    assert all(c["status"] == "new" and "fraud_referral_drafts" not in c and "case_file_drafts" not in c for c in rows)


def test_a_claim_for_checking_is_whole_in_one_call(client):
    c = get(client, "/claims/CLM-6205")
    assert c["status_in_words"] == "waiting for the fraud check" and c["days_from_loss_to_report"] == 1
    assert c["policy"]["period_start"] == "2026-05-05" and c["cover_on_loss_date"]["in_force"] is True
    assert c["bank_account_for_payment"] == "DEMO-ACCT-7741" and c["drafts_on_file"] == {"fraud_referral_drafts": 0, "case_file_drafts": 0}
    me = c["parties"][0]
    assert (me["party_id"], me["role"], me["date_of_birth"], me["phone"]) == ("PTY-3006", "claimant", "1986-12-05", "+999 555 0106")
    assert [d["document_id"] for d in c["documents"]] == ["DOC-6205-1", "DOC-6205-2"] and "Dated: 23 Nov 2026" in c["documents"][1]["text"]
    old = get(client, "/claims/CLM-6021")
    assert old["status"] == "closed" and old["policy"] is None and old["cover_on_loss_date"] is None and "now ended" in old["policy_note"]


# ---------------------------------------------------------------- fraud check: the eight right answers
def test_clm_6201_is_clean(client):
    k, row = indicators(client, 6201)
    assert k["indicators_met"] == [] and k["count_met"] == 0 and k["sentence"] == "No indicator is met on CLM-6201."
    assert [row[f"FI-{n}"]["measured"] for n in range(1, 7)] == [294, 0, 1, 0, 0, 14.0] and k["saved"] is False


def test_clm_6202_looks_odd_and_every_indicator_is_below_its_threshold(client):
    k, row = indicators(client, 6202)
    assert k["indicators_met"] == [] and [row[f"FI-{n}"]["measured"] for n in range(1, 7)] == [34, 2, 2, 0, 0, 91.0]
    assert row["FI-1"]["sentence"] == ("The policy period started on 16 Oct 2026 and the loss was on 19 Nov 2026, 34 days after the "
                                       "start. The threshold is 30 days or fewer: not met.")
    assert "has 2 earlier claims" in row["FI-2"]["sentence"] and "(CLM-6011, CLM-6012)" in row["FI-2"]["sentence"]
    assert "on 2 claims by the claimant, this claim included (also CLM-6012)" in row["FI-3"]["sentence"]
    assert "CLM-6013 by Niamh Whitmarsh (PTY-3003), who is recorded at the claimant's own address and so is not unrelated: not counted" in row["FI-4"]["sentence"]
    assert "the day of the loss" in row["FI-5"]["sentence"] and "91.0 percent" in row["FI-6"]["sentence"]


def test_clm_6203_is_an_early_loss(client):
    k, row = indicators(client, 6203)
    assert k["indicators_met"] == ["FI-1"] and row["FI-1"]["measured"] == 12 and row["FI-1"]["met"] is True
    assert row["FI-1"]["sentence"] == ("The policy period started on 6 Nov 2026 and the loss was on 18 Nov 2026, 12 days after the "
                                       "start. The threshold is 30 days or fewer: met.")
    assert row["FI-5"]["sentence"].startswith("The file holds no repair invoice and no repair estimate.")


def test_clm_6204_is_a_frequent_claimant_and_the_claim_before_the_24_months_is_not_counted(client):
    k, row = indicators(client, 6204)
    assert k["indicators_met"] == ["FI-2"] and row["FI-2"]["measured"] == 3
    assert row["FI-2"]["sentence"] == ("The claimant, Clementine Durrow born 17 Jan 1970, has 3 earlier claims with a date of loss on or "
                                       "after 17 Nov 2024, the 24 months before this loss (CLM-6015, CLM-6016, CLM-6017). The threshold "
                                       "is 3 or more: met.")
    e = get(client, "/claims/CLM-6204/earlier-claims")
    me = e["parties"][0]
    assert (me["earlier_claims_as_claimant"], me["earlier_claims_as_claimant_in_the_24_months_before_this_loss"]) == (4, 3)
    assert [(r["claim_id"], r["loss_date"], r["loss_in_the_24_months_before_this_loss"]) for r in me["earlier_claims"]] == [
        ("CLM-6014", "2024-06-09", False), ("CLM-6015", "2025-02-14", True), ("CLM-6016", "2025-10-02", True), ("CLM-6017", "2026-06-09", True)]
    assert me["earlier_claims"][3]["days_before_this_loss"] == 161 and e["the_24_months_start_on"] == "2024-11-17"


def test_clm_6205_shares_a_bank_account_with_an_unrelated_claimant(client):
    k, row = indicators(client, 6205)
    assert k["indicators_met"] == ["FI-4"] and row["FI-4"]["measured"] == 1
    assert row["FI-4"]["sentence"] == ("The bank account given for payment, DEMO-ACCT-7741, is on a claim by 1 unrelated claimant "
                                       "(Isolde Penhallow, PTY-3007, of 77 Limekiln Lane, Marlow Reach, Meridia, on CLM-6021). The "
                                       "threshold is 1 or more: met.")
    assert [(x["claim_id"], x["linked_by"]) for x in links(client, 6205)["linked_claims"]] == [("CLM-6021", ["bank_account"])]


def test_clm_6206_has_a_repair_invoice_dated_before_the_loss(client):
    k, row = indicators(client, 6206)
    assert k["indicators_met"] == ["FI-5"] and row["FI-5"]["measured"] == 6
    assert row["FI-5"]["sentence"] == ("Repair invoice, Swallowfield Flooring (DOC-6206-2) is dated 10 Nov 2026 and the loss was on "
                                       "16 Nov 2026: 6 days before the loss. The threshold is 1 day or more before the loss: met.")


def test_clm_6207_meets_two_indicators(client):
    k, row = indicators(client, 6207)
    assert k["indicators_met"] == ["FI-1", "FI-6"] and k["sentence"] == "2 indicators met on CLM-6207: FI-1, FI-6."
    assert (row["FI-1"]["measured"], row["FI-6"]["measured"]) == (9, 98.0)
    assert row["FI-6"]["sentence"] == ("The estimate is USD 17,640.00 and the sum insured for the vehicle is USD 18,000.00: 98.0 percent. "
                                       "The threshold is 95 percent or more: met.")


def test_clm_6208_has_the_name_of_an_earlier_claimant_and_is_another_person(client):
    k, row = indicators(client, 6208)
    assert k["indicators_met"] == [] and row["FI-2"]["measured"] == 0 and row["FI-2"]["met"] is False
    assert "PTY-3011 has the same name and another date of birth (19 Oct 1961): another person, whose claims are not counted." in row["FI-2"]["sentence"]
    e = get(client, "/claims/CLM-6208/earlier-claims")
    assert e["parties"][0]["earlier_claims"] == [] and e["parties"][0]["earlier_claims_as_claimant"] == 0
    other = e["other_people_with_the_claimants_name"]
    assert len(other) == 1 and (other[0]["party_id"], other[0]["claims"], other[0]["the_same_person"], other[0]["counted"]) == (
        "PTY-3011", ["CLM-6022", "CLM-6023", "CLM-6024"], False, False)
    assert "The dates of birth differ, so this is another person." in other[0]["sentence"]
    # the older man's own three claims would meet the indicator on a claim of his own: they are his, not the claimant's
    assert [p["party_id"] for p in get(client, "/parties?text=Gideon Marlowe")["items"]] == ["PTY-3010", "PTY-3011"]
    assert get(client, "/claims/CLM-6201/earlier-claims")["other_people_note"] == "No other person on the insurer's records has the claimant's name."


def test_the_indicators_are_refused_for_a_closed_claim_and_change_nothing(client, store):
    r = get(client, "/claims/CLM-6021/indicators", 409)
    assert "CLM-6021 is closed" in r["detail"] and "Nothing was worked out" in r["detail"]
    indicators(client, 6207)
    get(client, "/claims/CLM-6207/earlier-claims")
    assert store.data == build_all(TODAY_D)


# ---------------------------------------------------------------- fraud check: the draft
REFER = {"proposal": "refer to the investigations desk", "indicators_met": [{"indicator_id": "fi-1", "note": "9 days, threshold 30."},
                                                                          {"indicator_id": "FI-6", "note": "98.0 percent, threshold 95."}],
         "reasons": "Two indicators are met."}


def test_a_fraud_referral_is_a_draft_with_the_systems_measurement_and_changes_nothing(client, store):
    r = post(client, "/claims/CLM-6207/referrals", REFER)
    assert r["kind"] == "draft" and r["draft"]["version"] == 1 and r["draft"]["proposal"] == "refer_to_the_investigations_desk"
    assert [x["indicator_id"] for x in r["draft"]["indicators_met"]] == ["FI-1", "FI-6"]
    assert r["draft"]["measured_by_the_system"] == {"indicators_met": ["FI-1", "FI-6"],
                                                    "measured": {"FI-1": 9, "FI-2": 0, "FI-3": 1, "FI-4": 0, "FI-5": 0, "FI-6": 98.0}}
    assert post(client, "/claims/CLM-6207/referrals", {**REFER, "drafted_by": "Fraud check"})["draft"]["version"] == 2
    stored = store.data["investigation_claims"]["CLM-6207"]
    assert stored["status"] == "new" and stored["referral"] is None
    c = get(client, "/claims/CLM-6207")
    assert "fraud_referral_drafts" not in c and c["drafts_on_file"]["fraud_referral_drafts"] == 2
    assert "refer_to_the_investigations_desk" not in json.dumps(c) and "refer_to_the_investigations_desk" not in json.dumps(get(client, "/claims"))
    assert [c["claim_id"] for c in get(client, "/flagged-claims")["items"]] == [f"CLM-630{n}" for n in range(1, 8)]
    assert get(client, "/claims/CLM-6207/referrals")["items"][1]["drafted_by"] == "Fraud check"
    none = {"proposal": "no_referral_continue_handling", "reasons": "No indicator is met."}
    assert post(client, "/claims/CLM-6208/referrals", none)["draft"]["measured_by_the_system"]["indicators_met"] == []


def test_a_fraud_referral_is_refused_with_a_plain_sentence_and_nothing_saved(client, store):
    def refused(n, body, words):
        r = post(client, f"/claims/CLM-{n}/referrals", body, 409)
        assert words in r["detail"] and "Nothing was saved" in r["detail"] and r["applied"] is False
        assert store.data["investigation_claims"][f"CLM-{n}"]["fraud_referral_drafts"] == []

    refused(6207, {**REFER, "indicators_met": [{"indicator_id": "FI-9"}]}, "Not an indicator or given twice: FI-9")
    refused(6207, {**REFER, "indicators_met": []}, "needs one row for each indicator that is met")
    refused(6207, {**REFER, "proposal": "no_referral_continue_handling"}, "takes no rows")
    refused(6301, REFER, "CLM-6301 is not waiting for the fraud check: it is referred to the investigations desk. It was referred by "
                         "Lucan Thirlby, claims handler on 16 Nov 2026.")
    refused(6021, REFER, "it is closed")
    assert client.post("/investigations/claims/CLM-6207/referrals", headers=H, json={**REFER, "proposal": "decline the claim"}).status_code == 422
    assert client.post("/investigations/claims/CLM-6207/referrals", headers=H, json={"proposal": "no_referral_continue_handling"}).status_code == 422


# ---------------------------------------------------------------- investigations: the five right answers
def test_the_seven_referred_claims_carry_the_indicators_the_system_measures(client):
    rows = get(client, "/flagged-claims")["items"]
    assert [(c["claim_id"], c["claimant_party_id"], c["claimant"], c["loss_date"], c["estimate"], c["referral"]["indicators_met"],
             c["referral"]["referred_on"]) for c in rows] == [
        ("CLM-6301", "PTY-3021", "Osric Fenn", "2026-11-14", 5200.0, ["FI-1"], "2026-11-16"),
        ("CLM-6302", "PTY-3022", "Dagny Rookhope", "2026-11-11", 14400.0, ["FI-6"], "2026-11-13"),
        ("CLM-6303", "PTY-3023", "Ulric Staveley", "2026-11-17", 6800.0, ["FI-1"], "2026-11-19"),
        ("CLM-6304", "PTY-3024", "Evander Pryce", "2026-11-15", 12125.0, ["FI-6"], "2026-11-17"),
        ("CLM-6305", "PTY-3025", "Leofric Tansley", "2026-11-20", 3900.0, ["FI-1"], "2026-11-22"),
        ("CLM-6306", "PTY-3026", "Wilhelmina Orrell", "2026-11-18", 2640.0, ["FI-5"], "2026-11-20"),
        ("CLM-6307", "PTY-3027", "Cuthbert Lyle", "2026-11-13", 10560.0, ["FI-6"], "2026-11-15")]
    for c in rows:
        assert indicators(client, c["claim_id"][4:])[0]["indicators_met"] == c["referral"]["indicators_met"], c["claim_id"]
    measured = {n: indicators(client, n)[1] for n in (6301, 6302, 6303, 6304, 6305, 6306, 6307)}
    assert [measured[6301]["FI-1"]["measured"], measured[6303]["FI-1"]["measured"], measured[6305]["FI-1"]["measured"]] == [18, 22, 19]
    assert [measured[6302]["FI-6"]["measured"], measured[6304]["FI-6"]["measured"], measured[6307]["FI-6"]["measured"]] == [96.0, 97.0, 96.0]
    assert measured[6306]["FI-5"]["measured"] == 2


def test_three_claims_are_linked_through_one_repairer_and_one_phone_number(client):
    k = links(client, 6301)
    assert [(x["claim_id"], x["claimant"], x["linked_by"]) for x in k["linked_claims"]] == [
        ("CLM-6302", "Dagny Rookhope", ["phone", "repairer"]), ("CLM-6303", "Ulric Staveley", ["phone", "repairer"])]
    assert k["no_links_found"] is False and k["other_claims_by_the_same_claimant"] == []
    assert k["sentence"] == ("CLM-6301 is linked to 2 claims by another claimant: CLM-6302 (Dagny Rookhope) by phone, repairer; "
                             "CLM-6303 (Ulric Staveley) by phone, repairer.")
    first = {x["link_type"]: x for x in k["linked_claims"][0]["links"]}
    assert first["repairer"]["through_party_id"] == "PTY-3501"
    assert first["repairer"]["sentence"] == "Brackenfold Motor Works (PTY-3501) is the repairer on CLM-6301 and on CLM-6302."
    assert first["phone"]["sentence"] == "Osric Fenn (PTY-3021) and Dagny Rookhope (PTY-3022) are recorded with the same phone number: +999 555 0142."
    assert [(s["attribute"], s["value"], s["other_party_id"]) for s in k["shared_attributes"]] == [
        ("phone", "+999 555 0142", "PTY-3022"), ("phone", "+999 555 0142", "PTY-3023")]
    assert [x["claim_id"] for x in links(client, 6302)["linked_claims"]] == ["CLM-6301", "CLM-6303"]
    assert [x["claim_id"] for x in links(client, 6303)["linked_claims"]] == ["CLM-6301", "CLM-6302"]
    assert [p["party_id"] for p in get(client, "/parties?phone=%2B999 555 0142")["items"]] == ["PTY-3021", "PTY-3022", "PTY-3023"]
    firm = get(client, "/parties/PTY-3501/links")
    assert [c["claim_id"] for c in firm["party"]["claims"]] == ["CLM-6301", "CLM-6302", "CLM-6303"] and firm["shared_attributes"] == []
    assert "not a finding about any person" in k["what_a_link_is"]
    for party in ("PTY-3021", "PTY-3022", "PTY-3023"):
        assert get(client, f"/parties/{party}/public-notices")["count"] == 0


def test_clm_6304_has_a_public_notice_about_the_claimant(client):
    out = get(client, "/parties/PTY-3024/public-notices")
    assert out["count"] == 1 and out["sentence"] == "1 public notice names a person called Evander Pryce."
    n = out["items"][0]
    assert (n["notice_id"], n["kind"], n["published"], n["date_of_birth_compared"], n["address_compared"], n["about"]) == (
        "PN-901", "court_list", "2025-03-16", "same", "same", "the_same_person")
    assert "list of 16 Mar 2025" in n["text"] and "It is not a finding about any claim the insurer holds." in n["sentence"]
    k = links(client, 6304)
    assert k["no_links_found"] is True and [c["claim_id"] for c in k["other_claims_by_the_same_claimant"]] == ["CLM-6041"]
    e = get(client, "/claims/CLM-6304/earlier-claims")["parties"][0]
    assert (e["earlier_claims"][0]["claim_id"], e["earlier_claims"][0]["loss_date"], e["earlier_claims"][0]["amount_paid"]) == (
        "CLM-6041", "2025-08-03", 1300.0)


def test_clm_6305_has_a_notice_about_another_person_of_the_same_name(client):
    out = get(client, "/parties/PTY-3025/public-notices")
    n = out["items"][0]
    assert (n["notice_id"], n["kind"], n["published"], n["date_of_birth_compared"], n["address_compared"], n["about"]) == (
        "PN-902", "press_item", "2025-10-12", "differs", "differs", "a_different_person")
    assert n["sentence"] == ("PN-902 names Leofric Tansley and gives 1968 as the year of birth and Sheepwash Lane, Tallowby. The party's "
                             "record gives 14 Jul 1991 and 27 Mariners Row, Port Ilvane, Meridia. The dates of birth differ, so the "
                             "notice is about another person with the same name. It says nothing about the party.")
    k = links(client, 6305)
    assert k["no_links_found"] is True and k["other_claims_by_the_same_claimant"] == []


def test_clm_6306_has_no_links_at_all_and_the_system_says_so(client):
    k = links(client, 6306)
    assert k["no_links_found"] is True and k["linked_claims"] == [] and k["shared_attributes"] == [] and k["other_claims_by_the_same_claimant"] == []
    assert k["sentence"] == ("CLM-6306 shares no repairer, witness, phone number, address or bank account with any other claim or party "
                             "the insurer holds.")
    notices = get(client, "/parties/PTY-3026/public-notices")
    assert notices["count"] == 0 and notices["sentence"] == "No public notice names a person called Wilhelmina Orrell."
    assert get(client, "/claims/CLM-6306/earlier-claims")["parties"][0]["earlier_claims"] == []
    assert get(client, "/parties/PTY-3026/links")["sentence"].startswith("Wilhelmina Orrell (PTY-3026) shares no phone number")


def test_clm_6307_is_linked_only_through_its_witness_who_is_named_and_not_accused(client):
    k = links(client, 6307)
    assert [(x["claim_id"], x["claimant"], x["linked_by"]) for x in k["linked_claims"]] == [("CLM-6031", "Ambrose Tidewell", ["witness"])]
    link = k["linked_claims"][0]["links"][0]
    assert (link["link_type"], link["through_party_id"], link["through_party_name"]) == ("witness", "PTY-3028", "Hester Quarmby")
    assert link["sentence"] == ("Hester Quarmby (PTY-3028) is recorded as witness on CLM-6307 and as witness on CLM-6031, a claim by "
                                "another claimant (Ambrose Tidewell, PTY-3029). The records show that and nothing more about Hester Quarmby.")
    assert k["shared_attributes"] == [] and k["other_claims_by_the_same_claimant"] == []
    e = {p["party_id"]: p for p in get(client, "/claims/CLM-6307/earlier-claims")["parties"]}
    assert [r["claim_id"] for r in e["PTY-3028"]["earlier_claims"]] == ["CLM-6031"] and e["PTY-3028"]["role_on_this_claim"] == "witness"
    assert e["PTY-3027"]["earlier_claims"] == []
    for party in ("PTY-3027", "PTY-3028", "PTY-3029"):
        assert get(client, f"/parties/{party}/public-notices")["count"] == 0
    assert get(client, "/parties/PTY-3028/links")["shared_attributes"] == []


# ---------------------------------------------------------------- investigations: searches
def test_a_party_search_matches_any_word_and_lists_everyone_with_nothing_sent(client):
    assert get(client, "/parties")["count"] == 33
    assert [p["party_id"] for p in get(client, "/parties?text=Leofric Tansly")["items"]] == ["PTY-3025"]
    assert [p["party_id"] for p in get(client, "/parties?text=Whitmarsh")["items"]] == ["PTY-3002", "PTY-3003"]
    assert [p["party_id"] for p in get(client, "/parties?bank_account=DEMO-ACCT-7741")["items"]] == ["PTY-3006", "PTY-3007"]
    assert get(client, "/parties?text=Zebedee")["count"] == 0
    row = get(client, "/parties?text=PTY-3028")["items"][0]
    assert [(c["claim_id"], c["role_of_the_party"]) for c in row["claims"]] == [("CLM-6031", "witness"), ("CLM-6307", "witness")]


def test_the_public_notices_are_three_and_a_search_matches_any_word(client):
    assert [n["notice_id"] for n in get(client, "/public-notices")["items"]] == ["PN-901", "PN-902", "PN-903"]
    assert [n["notice_id"] for n in get(client, "/public-notices?text=Tansley Pryce")["items"]] == ["PN-901", "PN-902"]
    assert get(client, "/public-notices?text=Quarmby")["count"] == 0
    assert get(client, "/parties/PTY-3501/public-notices")["count"] == 0  # a firm


# ---------------------------------------------------------------- investigations: the draft
CASE = {"summary": "CLM-6301 was referred on an early loss. The records link it to two other claims.",
        "links_found": "links found",
        "links": [{"link_type": "repairer", "linked_claim_id": "CLM-6302", "through_party_id": "PTY-3501",
                   "note": "Brackenfold Motor Works is the repairer on both claims."},
                  {"link_type": "phone", "linked_claim_id": "CLM-6303", "through_party_id": "PTY-3023",
                   "note": "The two claimants gave the same phone number."}],
        "open_points": ["Whose number is +999 555 0142?"]}


def test_a_case_file_is_a_draft_with_what_the_system_found_and_changes_nothing(client, store):
    r = post(client, "/claims/CLM-6301/case-file", CASE)
    assert r["kind"] == "draft" and r["draft"]["version"] == 1 and r["draft"]["links_found"] == "links_found"
    assert r["draft"]["found_by_the_system"] == {
        "other_claims_by_the_same_claimant": [],
        "linked_claims": [{"claim_id": "CLM-6302", "linked_by": ["phone", "repairer"]}, {"claim_id": "CLM-6303", "linked_by": ["phone", "repairer"]}],
        "no_links_found": False, "public_notices_naming_a_party": []}
    assert post(client, "/claims/CLM-6301/case-file", {**CASE, "drafted_by": "Case file agent"})["draft"]["version"] == 2
    fresh = build_all(TODAY_D)["investigation_claims"]["CLM-6301"]
    stored = store.data["investigation_claims"]["CLM-6301"]
    assert {k: v for k, v in stored.items() if k != "case_file_drafts"} == {k: v for k, v in fresh.items() if k != "case_file_drafts"}
    c = get(client, "/claims/CLM-6301")
    assert "case_file_drafts" not in c and c["drafts_on_file"]["case_file_drafts"] == 2 and "Whose number" not in json.dumps(c)
    assert "Whose number" not in json.dumps(get(client, "/flagged-claims")) and "Whose number" not in json.dumps(links(client, 6301))
    assert get(client, "/claims/CLM-6301/case-file")["items"][1]["drafted_by"] == "Case file agent"
    notice = {"summary": "One notice names the claimant.", "links_found": "no_links_found", "earlier_claims": [{"claim_id": "CLM-6041"}],
              "public_notices": [{"notice_id": "pn-901", "about": "the same person", "note": "Name, date of birth and address agree."}]}
    saved = post(client, "/claims/CLM-6304/case-file", notice)["draft"]
    assert saved["public_notices"][0] == {"notice_id": "PN-901", "about": "the_same_person", "note": "Name, date of birth and address agree."}
    assert saved["found_by_the_system"]["public_notices_naming_a_party"] == [{"notice_id": "PN-901", "party_id": "PTY-3024", "about": "the_same_person"}]
    nothing = {"summary": "No link and no notice was found.", "links_found": "no_links_found"}
    assert post(client, "/claims/CLM-6306/case-file", nothing)["draft"]["found_by_the_system"]["no_links_found"] is True


def test_a_case_file_is_refused_with_a_plain_sentence_and_nothing_saved(client, store):
    def refused(n, body, words):
        r = post(client, f"/claims/CLM-{n}/case-file", body, 409)
        assert words in r["detail"] and "Nothing was saved" in r["detail"] and r["applied"] is False
        assert store.data["investigation_claims"][f"CLM-{n}"]["case_file_drafts"] == []

    refused(6207, CASE, "CLM-6207 is not referred to the investigations desk: it is waiting for the fraud check")
    refused(6301, {**CASE, "links": [{**CASE["links"][0], "linked_claim_id": "CLM-9999"}]}, "not a claim this system holds: CLM-9999")
    refused(6301, {**CASE, "links": [{**CASE["links"][0], "through_party_id": "PTY-0000"}]}, "not a party: PTY-0000")
    refused(6301, {**CASE, "public_notices": [{"notice_id": "PN-999", "about": "cannot_tell"}]}, "not a public notice: PN-999")
    refused(6301, {**CASE, "links": []}, "links_found needs one row for each link")
    refused(6301, {**CASE, "links_found": "no_links_found"}, "no_links_found takes no link rows")
    bad = client.post("/investigations/claims/CLM-6301/case-file", headers=H, json={**CASE, "links": [{**CASE["links"][0], "note": ""}]})
    assert bad.status_code == 422 and bad.json()["applied"] is False
    assert client.post("/investigations/claims/CLM-6301/case-file", headers=H, json={"links_found": "no_links_found"}).status_code == 422


# ---------------------------------------------------------------- unknown ids, reset and counts
def test_an_unknown_id_is_a_plain_404(client):
    for path, words in (("/closed-claims/CLM-9999", "No closed claim in the leakage review with id CLM-9999"),
                        ("/closed-claims/CLM-6201/should-have-been-paid", "read it with get_claim_for_checking"),
                        ("/claims/CLM-6103", "read it with get_closed_claim_payment_file"),
                        ("/claims/CLM-4001", "No claim held for checking with id CLM-4001"),
                        ("/claims/CLM-4001/links", "This system holds the claims passed to it"),
                        ("/parties/PTY-9999/links", "No party with id PTY-9999"),
                        ("/parties/PTY-9999/public-notices", "No party with id PTY-9999")):
        r = client.get(f"/investigations{path}", headers=H)
        assert r.status_code == 404 and words in r.json()["detail"] and r.json()["applied"] is False, path


def test_putting_this_system_back_leaves_the_others_alone_and_the_other_way_round(client, store):
    triage = {"rule_id": "HG-3", "track": "fast track", "team": "fast-track team", "severity": "low", "reason": "Estimate under 2,500."}
    client.post("/claims/claims/CLM-4001/triage", headers=H, json=triage)
    post(client, "/closed-claims/CLM-6101/findings", {"outcome": "paid_within_the_standards"})
    post(client, "/claims/CLM-6207/referrals", REFER)
    post(client, "/claims/CLM-6301/case-file", CASE)
    changed = client.get("/admin/state", headers=H).json()["changed_by"]
    assert changed == {"claims": ["claims"], "investigations": ["investigation_claims", "leakage_claims"]}
    fresh = build_all(TODAY_D)
    assert client.post("/admin/reset/claims", headers=H).json()["put_back"] == ["claims"]
    assert store.data["claims"] == fresh["claims"] and len(store.data["leakage_claims"]["CLM-6101"]["leakage_finding_drafts"]) == 1
    client.post("/claims/claims/CLM-4001/triage", headers=H, json=triage)
    assert client.post("/admin/reset/investigations", headers=H).json()["put_back"] == ["investigation_claims", "leakage_claims"]
    assert all(store.data[name] == fresh[name] for name in OWN_SETS)
    assert len(store.data["claims"]["CLM-4001"]["triage_drafts"]) == 1
    assert post(client, "/claims/CLM-6207/referrals", REFER)["draft"]["version"] == 1
    client.post("/admin/reset", headers=H)
    assert store.data == fresh


def test_the_counts_name_the_open_items_of_this_system(client):
    counts = client.get("/admin/state", headers=H).json()["counts"]
    assert (counts["closed_claims_in_the_leakage_review"], counts["claims_waiting_for_the_fraud_check"],
            counts["claims_referred_to_investigations"]) == (8, 8, 7)
    assert "claims waiting for the fraud check" in client.get("/").text


def test_every_id_in_the_investigations_section_of_the_scenarios_is_in_the_data():
    from pathlib import Path
    text = (Path(__file__).resolve().parent.parent / "SCENARIOS.md").read_text(encoding="utf-8")
    section = text.split("## Investigations (system: investigations)")[1].split("## Rules for checking")[0]
    data = build_all(TODAY_D)
    held = set()
    for name in OWN_SETS + ["policies"]:
        held |= set(data[name])
    for claim in data["leakage_claims"].values():
        held |= {p["payment_id"] for p in claim["payment_file"]["payments"]}
        held |= {line["line_id"] for inv in claim["payment_file"]["invoices"] for line in inv["lines"]}
    held |= {doc["document_id"] for c in data["investigation_claims"].values() for doc in c["documents"]}
    named = set(re.findall(r"\b(?:CLM-6\d{3}(?:-[PL]\d)?|POL-2\d{3}|PTY-3\d{3}|PN-9\d{2}|DOC-6\d{3}-\d|LS-\d|FI-\d)\b", section))
    assert len(named) > 80 and named <= held, sorted(named - held)
    assert chr(8212) not in section
