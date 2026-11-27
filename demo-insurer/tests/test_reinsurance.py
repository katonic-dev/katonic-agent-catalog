"""The reinsurance system: the right answers of the Reinsurance section of SCENARIOS.md, every refusal, and the rules drafts keep.

Checked against the data the service gives at the insurer date 2026-11-26."""
import copy
import json
import re
from datetime import date
from pathlib import Path

from insurer.seed import build_all
from insurer.seed_reinsurance import build_reinsurance
from conftest import H, TODAY

TODAY_D = date.fromisoformat(TODAY)
RI_SETS = sorted(build_reinsurance(TODAY_D))


def get(client, path, status=200):
    r = client.get(f"/reinsurance{path}", headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:300])
    return r.json()


def post(client, path, body=None, status=200):
    r = client.post(f"/reinsurance{path}", json=body or {}, headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:400])
    return r.json()


def measure(client, n):
    return get(client, f"/bordereaux/BDX-{n}/measure")


def found(m):
    return [(x["row_number"], x["check"], x["term"]) for x in m["differences_measured"]]


def check_of(m, row, check):
    return next(c for c in m["rows"][row - 1]["checks"] if c["check"] == check)


def totals(m):
    return {k: (v["stated_on_the_bordereau"], v["re_added_by_the_system"], v["difference"]) for k, v in m["totals"]["columns"].items()}


def recovery(client, n):
    return get(client, f"/paid-claims/RCL-{n}/recovery")


def xl(k):
    return next(x for x in k["under_each_treaty"] if x["treaty_id"] == "TRY-8651")


def qs(k):
    return next(x for x in k["under_each_treaty"] if x["treaty_id"] == "TRY-8652")


def partner(client, n):
    return get(client, f"/partners/PTN-{n}/measure")


def level(m, term):
    return next(s for s in m["service_levels"] if s["term"] == term)


DIFFS = {"overall": "differences_found", "summary": "Twelve rows, three differences.",
         "differences": [{"row_number": 5, "kind": "over_maximum_line", "term": "3", "note": "USD 75,000.00 over."},
                         {"row_number": 7, "kind": "outside_territory", "term": "2", "note": "Veldmark."},
                         {"row_number": 8, "kind": "excluded_risk", "term": "7", "note": "A thatched roof."}]}
RECOVERIES = {"summary": "Five claims to raise, USD 1,010,000.00 in all. RCL-8807 needs a person.",
              "claims_with_nothing_due": ["RCL-8801", "RCL-8802", "RCL-8805", "RCL-8810", "RCL-8811"],
              "rows": [{"claim_id": "RCL-8803", "treaty_id": "TRY-8651", "finding": "recovery_to_raise", "amount_to_raise": 160000, "term": "4"},
                       {"claim_id": "RCL-8804", "treaty_id": "TRY-8651", "finding": "recovery_raised_for_too_little", "amount_to_raise": 50000,
                        "term": "4"},
                       {"claim_id": "RCL-8806", "treaty_id": "TRY-8651", "finding": "recovery_to_raise", "amount_to_raise": 750000, "term": "5"},
                       {"claim_id": "RCL-8807", "treaty_id": "TRY-8651", "finding": "needs_a_person", "amount_to_raise": 0, "term": "3"},
                       {"claim_id": "RCL-8808", "treaty_id": "TRY-8651", "finding": "recovery_to_raise", "amount_to_raise": 30000, "term": "6",
                        "event_id": "EVT-8891"},
                       {"claim_id": "RCL-8809", "treaty_id": "TRY-8651", "finding": "recovery_to_raise", "amount_to_raise": 20000, "term": "6",
                        "event_id": "EVT-8891"}]}
REVIEW = {"overall": "not_met", "summary": "Two service levels are not met.", "needs_a_person": "no",
          "findings": [{"item": "SL-3", "result": "not_met", "evidence": "7.50 percent against 5.00."},
                       {"item": "SL-4", "result": "not_met", "evidence": "7 days late."}]}


# ---------------------------------------------------------------- the system as a whole
def test_the_reinsurance_system_has_18_operations_and_every_save_is_a_draft(client):
    doc = client.get("/reinsurance/openapi.json").json()
    ops = [(method, op) for item in doc["paths"].values() for method, op in item.items()]
    assert len(ops) == 18
    saves = sorted(op["operationId"] for method, op in ops if method != "get")
    assert saves == ["save_bordereau_differences", "save_partner_review", "save_recovery_list"]
    for method, op in ops:
        assert not op["summary"].endswith("(change)"), op["operationId"]
        assert chr(8212) not in op["description"] + op["summary"]
        if method != "get":
            assert op["summary"].endswith("(draft)"), op["operationId"]
    assert client.get("/reinsurance/bordereaux").status_code == 401
    assert "reinsurance/openapi.json" in client.get("/").text


def test_no_operation_id_is_shared_with_another_system(client):
    mine = {op["operationId"] for item in client.get("/reinsurance/openapi.json").json()["paths"].values() for op in item.values()}
    for other in ("policy", "claims", "health", "underwriting", "investigations", "servicing", "conduct"):
        theirs = {op["operationId"] for item in client.get(f"/{other}/openapi.json").json()["paths"].values() for op in item.values()}
        assert not mine & theirs, (other, mine & theirs)


def test_reinsurance_ids_have_their_own_ranges_and_collide_with_nothing():
    data = build_all(TODAY_D)
    prefixes = {"ri_bordereaux": "BDX-87", "ri_claims": "RCL-88", "ri_events": "EVT-88", "ri_recoveries": "RCV-88",
                "ri_recovery_lists": "RLIST-88", "ri_partners": "PTN-89"}
    for name, prefix in prefixes.items():
        assert all(key.startswith(prefix) for key in data[name]), name
    assert list(data["ri_contracts"]) == ["BND-8601", "BND-8602", "TRY-8651", "TRY-8652"]
    mine = {key for name in RI_SETS for key in data[name]}
    others = {key for name, records in data.items() if name not in RI_SETS and isinstance(records, dict) for key in records}
    assert not mine & others


def test_no_text_of_the_reinsurance_data_holds_a_bare_date_counts_days_or_names_a_member_of_staff():
    data = build_reinsurance(TODAY_D)
    texts = [t["text"] for c in data["ri_contracts"].values() for t in c["terms"]]
    texts += [r["description"] for b in data["ri_bordereaux"].values() for r in b["rows"]]
    texts += [c["description"] for c in data["ri_claims"].values()] + [r["note"] for r in data["ri_recoveries"].values()]
    texts += [e["description"] for e in data["ri_events"].values()]
    assert len(texts) == 35 + 39 + 11 + 2 + 1
    for text in texts:
        assert not re.search(r"\b20\d\d-\d\d-\d\d\b", text), text
    blob = json.dumps(data).lower()
    for word in ("yesterday", "last week", "days ago", "weeks ago", "last month", "this morning", "tomorrow", "monday", "tuesday",
                 "wednesday", "thursday", "friday", "saturday", "sunday", chr(8212)):
        assert word not in blob, word
    assert all(set(r["raised_by"]) == {"role"} for r in data["ri_recoveries"].values())
    assert build_reinsurance(TODAY_D) == data


def test_results_name_a_role_and_codes_carry_a_plain_label(client):
    assert measure(client, 8701)["goes_to"] == "the reinsurance accountant" == recovery(client, 8803)["goes_to"]
    assert partner(client, 8901)["goes_to"] == "the supplier manager"
    m = measure(client, 8701)
    assert m["kind_label"] == "risks bound in the month" and m["rows"][4]["checks"][2]["result_label"] == "outside the term"
    assert m["rows"][4]["checks"][2]["check_label"] == "maximum line per risk"
    k = recovery(client, 8803)
    assert k["status_label"] == "a recovery is due and none is raised" and xl(k)["treaty_kind_label"].startswith("excess of loss treaty")
    p = get(client, "/partners/PTN-8904")
    assert p["kind_label"] == "repair network" and p["measured"]["credentials"][1]["result_label"] == "expired"
    assert p["credentials"][1]["kind_label"] == "accreditation" and p["measured"]["service_levels"][0]["metric_label"]
    row = get(client, "/bordereaux/BDX-8701")["rows"][0]
    assert (row["class_code"], row["class_label"]) == ("HH", "household buildings and contents")


# ---------------------------------------------------------------- binders and treaties
def test_two_binders_and_two_treaties_carry_numbered_terms(client):
    rows = get(client, "/contracts")["items"]
    assert [(c["contract_id"], c["kind"], len(c["terms"])) for c in rows] == [
        ("BND-8601", "binder", 9), ("BND-8602", "binder", 9), ("TRY-8651", "excess_of_loss_per_risk", 8), ("TRY-8652", "quota_share", 9)]
    assert [c["contract_id"] for c in get(client, "/contracts?kind=quota share")["items"]] == ["TRY-8652"]
    b = get(client, "/contracts/BND-8601")
    assert (b["period_start"], b["period_end"]) == ("2026-01-01", "2026-12-31") and b["bordereaux_under_it"] == ["BDX-8701", "BDX-8703"]
    assert b["figures"]["maximum_line"] == 750000.0 and b["figures"]["commission_rate_percent"] == 25.0
    assert [t["term"] for t in b["terms"] if t["kind"] == "for_reading"] == ["7"] and "thatched roof" in b["terms"][6]["text"]
    m = get(client, "/contracts/bnd-8602")
    assert (m["period_start"], m["period_end"], m["figures"]["maximum_line"], m["figures"]["commission_rate_percent"]) == (
        "2026-04-01", "2027-03-31", 250000.0, 20.0)
    x = get(client, "/contracts/TRY-8651")
    assert (x["figures"]["attachment_point"], x["figures"]["limit"], x["figures"]["annual_premium"], x["treaty_year"]) == (
        250000.0, 750000.0, 180000.0, "2026")
    assert "added together and treated as one loss" in x["terms"][5]["text"] and "exactly on USD 250,000.00 gives no recovery" in x["terms"][3]["text"]
    q = get(client, "/contracts/TRY-8652")["figures"]
    assert (q["cession_percent"], q["maximum_line"], q["commission_rate_percent"], q["cash_loss_limit"]) == (40.0, 2000000.0, 30.0, 100000.0)
    assert get(client, "/contracts?kind=facultative", 409)["applied"] is False and get(client, "/contracts/BND-9999", 404)


# ---------------------------------------------------------------- bordereaux
def test_the_list_of_bordereaux_is_whole_and_holds_no_drafts_and_no_measure(client):
    post(client, "/bordereaux/BDX-8701/differences", DIFFS)
    rows = get(client, "/bordereaux")["items"]
    assert [(r["bordereau_id"], r["kind"], r["contract_id"], r["rows_on_the_bordereau"]) for r in rows] == [
        ("BDX-8701", "risks_bound", "BND-8601", 12), ("BDX-8702", "risks_bound", "BND-8602", 10),
        ("BDX-8703", "claims_paid", "BND-8601", 9), ("BDX-8704", "cessions", "TRY-8652", 8)]
    assert all("difference_drafts" not in r and "measured" not in r and len(r["rows"]) == r["rows_on_the_bordereau"] for r in rows)
    assert [r["bordereau_id"] for r in get(client, "/bordereaux?kind=claims paid")["items"]] == ["BDX-8703"]
    assert get(client, "/bordereaux?kind=premium", 409)["applied"] is False


def test_bdx_8701_has_a_risk_over_the_line_one_outside_the_territory_and_one_exactly_on_the_line(client):
    m = measure(client, 8701)
    assert found(m) == [(5, "maximum_line", "3"), (7, "territory", "2")]
    over = check_of(m, 5, "maximum_line")
    assert (over["measured"], over["limit"], over["difference"], over["result"]) == (825000.0, 750000.0, 75000.0, "outside")
    on = check_of(m, 3, "maximum_line")
    assert (on["measured"], on["difference"], on["result"]) == (750000.0, 0.0, "within") and "exactly on the maximum line" in on["sentence"]
    assert m["rows"][2]["result"] == "within" and check_of(m, 7, "territory")["measured"] == "Veldmark"
    assert m["counted"] == {"rows": 12, "rows_within_every_measured_term": 10, "rows_with_a_measured_difference": 2,
                            "differences_measured": 2, "totals_add_up": True}
    assert totals(m) == {"gross_premium": (11190.0, 11190.0, 0.0), "commission_stated": (2797.5, 2797.5, 0.0),
                         "net_premium_stated": (8392.5, 8392.5, 0.0)}
    due = m["premium_due"]
    assert (due["due_on"], due["status"], due["days_left"], due["late"]) == ("2026-12-15", "not_yet_due", 19, False)


def test_bdx_8701_row_8_is_excluded_by_its_description_which_the_system_does_not_read(client):
    b = get(client, "/bordereaux/BDX-8701")
    assert b["rows"][7]["description"] == "Cottage with a thatched roof, owner occupied."
    m = b["measured"]
    assert m["rows"][7]["result"] == "within" and m["excluded_risks_for_reading"]["term"] == "7"
    assert "thatched roof" in m["excluded_risks_for_reading"]["text"] and "does not read the description" in m["excluded_risks_for_reading"]["note"]
    assert sum("thatched" in r["description"] for r in b["rows"]) == 1
    assert b["contract"]["contract_id"] == "BND-8601" and len(b["contract"]["terms"]) == 9


def test_bdx_8702_has_a_wrong_commission_a_risk_outside_the_period_and_a_duplicate_row(client):
    m = measure(client, 8702)
    assert found(m) == [(5, "commission", "5"), (7, "period", "4"), (9, "declared_once", "9")]
    com = check_of(m, 5, "commission")
    assert (com["measured"], com["limit"], com["difference"], com["rate_taken_percent"], com["rate_of_the_term_percent"]) == (
        270.0, 240.0, 30.0, 22.5, 20.0)
    assert check_of(m, 5, "row_total")["result"] == "within"
    per = check_of(m, 7, "period")
    assert (per["measured"], per["difference"]) == ("2026-03-28", 4) and "4 days before the period starts" in per["sentence"]
    assert check_of(m, 9, "declared_once")["duplicate_of_row"] == 4 and m["rows"][3]["result"] == "within"
    assert totals(m) == {"gross_premium": (8510.0, 8510.0, 0.0), "commission_stated": (1732.0, 1732.0, 0.0),
                         "net_premium_stated": (6778.0, 6778.0, 0.0)}
    at = m["totals"]["commission_at_the_rate_of_the_term"]
    assert (at["commission_due_at_that_rate"], at["commission_taken"], at["difference"], at["net_premium_at_that_rate"]) == (
        1702.0, 1732.0, 30.0, 6808.0)
    less = m["totals"]["without_the_rows_declared_twice"]
    assert (less["rows_left_out"], less["gross_premium"], less["commission_stated"], less["net_premium_stated"]) == ([9], 8090.0, 1648.0, 6442.0)
    assert (m["premium_due"]["due_on"], m["premium_due"]["days_left"]) == ("2026-11-30", 4)
    assert m["counted"]["rows_within_every_measured_term"] == 7


def test_bdx_8703_has_a_row_that_does_not_add_up_and_two_claims_that_must_not_fire(client):
    m = measure(client, 8703)
    assert found(m) == [(5, "row_total", "9")]
    row = check_of(m, 5, "row_total")
    assert (row["measured"], row["limit"], row["difference"]) == (3850.0, 3650.0, 200.0)
    assert totals(m) == {"indemnity": (45040.0, 45040.0, 0.0), "fees": (3560.0, 3560.0, 0.0), "total": (48800.0, 48600.0, 200.0)}
    assert m["totals"]["adds_up"] is False and m["totals"]["columns"]["total"]["sum_of_the_row_totals_as_stated"] == 48800.0
    on = check_of(m, 4, "claims_authority")
    assert (on["measured"], on["limit"], on["result"]) == (10000.0, 10000.0, "within") and "exactly on the claims authority" in on["sentence"]
    agreed = check_of(m, 7, "claims_authority")
    assert (agreed["measured"], agreed["difference"], agreed["result"], agreed["agreement_reference"]) == (23400.0, 13400.0, "within", "TMI-AGR-0417")
    assert m["premium_due"] is None and m["excluded_risks_for_reading"] is None and m["counted"]["rows_within_every_measured_term"] == 8


def test_bdx_8704_is_clean_and_a_cession_exactly_on_the_line_is_within(client):
    m = measure(client, 8704)
    assert found(m) == [] and all(r["result"] == "within" and r["checks_outside"] == [] for r in m["rows"])
    assert m["counted"] == {"rows": 8, "rows_within_every_measured_term": 8, "rows_with_a_measured_difference": 0,
                            "differences_measured": 0, "totals_add_up": True}
    on = check_of(m, 5, "maximum_line")
    assert (on["measured"], on["limit"], on["difference"], on["result"]) == (2000000.0, 2000000.0, 0.0, "within")
    assert totals(m) == {"ceded_sum_insured_stated": (7200000.0, 7200000.0, 0.0), "ceded_premium_stated": (34160.0, 34160.0, 0.0),
                         "commission_stated": (10248.0, 10248.0, 0.0), "net_premium_stated": (23912.0, 23912.0, 0.0)}
    assert m["totals"]["commission_at_the_rate_of_the_term"]["difference"] == 0.0 and m["premium_due"]["due_on"] == "2026-12-15"
    assert m == get(client, "/bordereaux/BDX-8704")["measured"] | {"saved": False, "demo_data": True}


def test_a_difference_list_is_a_versioned_draft_and_not_part_of_the_bordereau(client, store):
    before = copy.deepcopy(store.data)
    one = post(client, "/bordereaux/BDX-8701/differences", {**DIFFS, "overall": "Differences found", "suggested_step": "none"})
    assert one["applied"] is True and one["kind"] == "draft" and one["draft"]["version"] == 1
    assert one["draft"]["suggested_step"] is None and one["draft"]["overall"] == "differences_found"
    assert one["draft"]["goes_to"] == "the reinsurance accountant" and one["draft"]["differences"][2]["kind_label"]
    assert [(x["row_number"], x["check"]) for x in one["draft"]["measured_by_the_system"]["differences_measured"]] == [
        (5, "maximum_line"), (7, "territory")]
    two = post(client, "/bordereaux/BDX-8701/differences",
               {**DIFFS, "suggested_step": "refer to the reinsurance accountant",
                "differences": [{**DIFFS["differences"][0], "kind": "Over maximum line", "term": "Term 3"}]})
    assert two["draft"]["version"] == 2 and two["draft"]["suggested_step"] == "refer_to_the_reinsurance_accountant"
    assert two["draft"]["differences"][0]["term"] == "3" and two["draft"]["differences"][0]["kind"] == "over_maximum_line"
    assert post(client, "/bordereaux/BDX-8701/differences", {**DIFFS, "suggested_step": ""})["draft"]["suggested_step"] is None
    b = get(client, "/bordereaux/BDX-8701")
    assert b["drafts_on_file"] == 3 and "difference_drafts" not in b and b["status"] == "received"
    assert [x["version"] for x in get(client, "/bordereaux/BDX-8701/drafts")["items"]] == [1, 2, 3]
    after = copy.deepcopy(store.data)
    after["ri_bordereaux"]["BDX-8701"]["difference_drafts"] = []
    assert after == before
    clean = post(client, "/bordereaux/BDX-8704/differences", {"overall": "no differences", "summary": "Eight rows, nothing differs."})
    assert clean["draft"]["differences"] == [] and clean["draft"]["measured_by_the_system"]["counted"]["differences_measured"] == 0


def test_a_difference_list_is_refused_with_a_reason_and_nothing_is_saved(client):
    row = DIFFS["differences"][0]
    for body, words in (({**DIFFS, "differences": [{**row, "row_number": 13}]}, "Row 13 is not a row"),
                        ({**DIFFS, "differences": [{**row, "term": "12"}]}, "is not a term of BND-8601"),
                        ({**DIFFS, "overall": "no_differences"}, "no_differences and differences are listed"),
                        ({**DIFFS, "differences": []}, "no difference is listed")):
        r = post(client, "/bordereaux/BDX-8701/differences", body, 409)
        assert words in r["detail"] and "Nothing was saved" in r["detail"] and r["applied"] is False
    assert post(client, "/bordereaux/BDX-8701/differences", {**DIFFS, "overall": "rejected"}, 422)["applied"] is False
    assert post(client, "/bordereaux/BDX-8799/differences", DIFFS, 404)["applied"] is False
    assert get(client, "/bordereaux/BDX-8701")["drafts_on_file"] == 0


# ---------------------------------------------------------------- paid claims and recoveries
def test_two_claims_below_the_attachment_point_recover_nothing(client):
    a, b = recovery(client, 8801), recovery(client, 8802)
    assert (a["paid_total"], a["status"], a["to_raise_on_this_claim"], xl(a)["recoverable"]) == (90000.0, "nothing_due", 0.0, 0.0)
    assert (b["paid_total"], b["status"], b["to_raise_on_this_claim"], xl(b)["above_the_attachment_point"]) == (240000.0, "nothing_due", 0.0, 0.0)
    assert "USD 160,000.00 below it" in a["sentence"] and "USD 10,000.00 below it" in b["sentence"]
    assert b["paid_working"] == "Paid on RCL-8802: 150,000.00 + 90,000.00 = USD 240,000.00."
    assert a["treaty_year"]["treaty_year"] == "2026" and xl(a)["reinstatement_premium"] is None
    assert qs(a)["status"] == "does_not_apply" and qs(a)["applies"] is False


def test_rcl_8803_is_above_the_attachment_point_with_no_recovery_raised(client):
    k = recovery(client, 8803)
    x = xl(k)
    assert (k["paid_total"], k["status"], k["to_raise_on_this_claim"], k["treaty_that_answers"]) == (410000.0, "recovery_to_raise", 160000.0, "TRY-8651")
    assert (x["above_the_attachment_point"], x["above_the_limit_kept_by_the_insurer"], x["recoverable"], x["raised_so_far"], x["still_to_raise"]) == (
        160000.0, 0.0, 160000.0, 0.0, 160000.0)
    assert (x["reinstatement_premium"]["on_the_whole_recovery"], x["reinstatement_premium"]["on_the_part_still_to_raise"]) == (38400.0, 38400.0)
    assert "410,000.00 - 250,000.00 = USD 160,000.00" in x["working"][1] and k["needs_a_person"] is False


def test_rcl_8804_has_a_recovery_raised_for_too_little(client):
    k = recovery(client, 8804)
    x = xl(k)
    assert (k["paid_total"], k["status"], k["to_raise_on_this_claim"]) == (600000.0, "recovery_raised_for_too_little", 50000.0)
    assert (x["recoverable"], x["raised_so_far"], x["recoveries_raised"], x["still_to_raise"]) == (350000.0, 300000.0, ["RCV-8851"], 50000.0)
    assert (x["reinstatement_premium"]["on_the_whole_recovery"], x["reinstatement_premium"]["on_the_part_still_to_raise"]) == (84000.0, 12000.0)
    raised = get(client, "/recoveries?claim_id=RCL-8804")["items"]
    assert [(r["recovery_id"], r["amount"], r["raised_on"], r["paid_loss_when_raised"]) for r in raised] == [("RCV-8851", 300000.0, "2026-09-11", 550000.0)]
    assert [p["amount"] for p in get(client, "/paid-claims/RCL-8804")["payments"]] == [300000.0, 250000.0, 50000.0]


def test_rcl_8805_is_exactly_on_the_attachment_point_and_recovers_nothing(client):
    k = recovery(client, 8805)
    assert (k["paid_total"], k["status"], k["to_raise_on_this_claim"], xl(k)["recoverable"], xl(k)["above_the_attachment_point"]) == (
        250000.0, "nothing_due", 0.0, 0.0, 0.0)
    assert "exactly on it" in k["sentence"] and k["needs_a_person"] is False


def test_rcl_8806_is_above_the_limit_and_the_recovery_is_capped(client):
    k = recovery(client, 8806)
    x = xl(k)
    assert (k["paid_total"], k["status"], k["to_raise_on_this_claim"]) == (1150000.0, "recovery_to_raise", 750000.0)
    assert (x["above_the_attachment_point"], x["above_the_limit_kept_by_the_insurer"], x["recoverable"]) == (900000.0, 150000.0, 750000.0)
    assert x["reinstatement_premium"]["on_the_whole_recovery"] == 180000.0 and "capped at USD 750,000.00" in x["working"][2]


def test_rcl_8807_has_a_date_of_loss_before_the_treaty_period(client):
    k = recovery(client, 8807)
    assert (k["paid_total"], k["status"], k["to_raise_on_this_claim"], k["needs_a_person"], k["treaty_that_answers"]) == (
        380000.0, "outside_the_treaty_period", 0.0, True, None)
    assert xl(k)["days_outside_the_period"] == 3 and xl(k)["applies"] is False and k["treaty_year"]["treaty_year"] is None
    assert "29 Dec 2025: 3 days before the period starts" in k["sentence"]


def test_two_claims_from_one_event_reach_the_attachment_point_only_together(client):
    a, b = recovery(client, 8808), recovery(client, 8809)
    for k, paid, share in ((a, 180000.0, 30000.0), (b, 120000.0, 20000.0)):
        x = xl(k)
        assert (k["paid_total"], k["status"], k["to_raise_on_this_claim"]) == (paid, "recovery_to_raise", share)
        assert (x["loss_measured"], x["above_the_attachment_point"], x["recoverable"], x["still_to_raise"]) == (300000.0, 50000.0, 50000.0, 50000.0)
        assert x["reinstatement_premium"]["on_the_whole_recovery"] == 12000.0
        assert [(c["claim_id"], c["paid"], c["share_of_the_recovery"]) for c in x["event"]["claims"]] == [
            ("RCL-8808", 180000.0, 30000.0), ("RCL-8809", 120000.0, 20000.0)]
        assert "One event (term 6)" in x["working"][1] and "180,000.00 + 120,000.00 = USD 300,000.00" in x["working"][1]
    c = get(client, "/paid-claims/RCL-8808")
    assert c["event"]["event_id"] == "EVT-8891" and c["event"]["claim_ids"] == ["RCL-8808", "RCL-8809"] and c["recovery"] == {
        k: v for k, v in a.items() if k not in ("saved", "demo_data")}


def test_the_quota_share_takes_its_share_by_a_cash_call_only_from_the_threshold(client):
    a, b = recovery(client, 8810), recovery(client, 8811)
    assert (a["paid_total"], a["status"], a["to_raise_on_this_claim"], qs(a)["share_of_the_reinsurer"]) == (
        80000.0, "collected_in_the_quarterly_account", 0.0, 32000.0)
    assert (b["paid_total"], b["status"], b["to_raise_on_this_claim"], qs(b)["share_of_the_reinsurer"], qs(b)["raised_so_far"]) == (
        150000.0, "recovery_raised_in_full", 0.0, 60000.0, 60000.0)
    assert xl(a)["status"] == "does_not_apply" and a["treaty_that_answers"] == "TRY-8652"


def test_the_list_for_a_period_is_whole_adds_what_is_to_raise_and_holds_no_drafts(client):
    post(client, "/recovery-lists", RECOVERIES)
    doc = get(client, "/paid-claims")
    assert doc["period"] == {"paid_from": "2026-01-01", "paid_to": "2026-11-26"} and doc["count"] == 11
    assert [r["claim_id"] for r in doc["items"]] == [f"RCL-88{n:02d}" for n in range(1, 12)]
    s = doc["summary"]
    assert s["claims_with_something_to_raise"] == ["RCL-8803", "RCL-8804", "RCL-8806", "RCL-8808", "RCL-8809"]
    assert s["to_raise_in_all"] == 1010000.0 and s["claims_that_need_a_person"] == ["RCL-8807"]
    assert {x["status"]: x["claims"] for x in s["by_status"]} == {
        "nothing_due": ["RCL-8801", "RCL-8802", "RCL-8805"], "recovery_to_raise": ["RCL-8803", "RCL-8806", "RCL-8808", "RCL-8809"],
        "recovery_raised_for_too_little": ["RCL-8804"], "outside_the_treaty_period": ["RCL-8807"],
        "collected_in_the_quarterly_account": ["RCL-8810"], "recovery_raised_in_full": ["RCL-8811"]}
    assert doc["recovery_list_drafts_on_file"] == 1 and "drafts" not in json.dumps(doc["items"])
    october = get(client, "/paid-claims?paid_from=2026-10-01&paid_to=2026-10-31")
    assert [r["claim_id"] for r in october["items"]] == ["RCL-8806", "RCL-8808", "RCL-8809"] and october["summary"]["to_raise_in_all"] == 800000.0
    assert october["items"][0]["paid_total"] == 1150000.0
    assert "not" in get(client, "/paid-claims?paid_from=October", 409)["detail"]
    assert "is after" in get(client, "/paid-claims?paid_from=2026-11-01&paid_to=2026-10-01", 409)["detail"]
    assert [r["recovery_id"] for r in get(client, "/recoveries")["items"]] == ["RCV-8851", "RCV-8852"]


def test_a_recovery_list_is_a_versioned_draft_and_changes_nothing_else(client, store):
    before = copy.deepcopy(store.data)
    one = post(client, "/recovery-lists", {**RECOVERIES, "rows": [{**RECOVERIES["rows"][0], "finding": "Recovery to raise"}] + RECOVERIES["rows"][1:]})
    d = one["draft"]
    assert one["kind"] == "draft" and d["version"] == 1 and d["goes_to"] == "the reinsurance accountant"
    assert d["added_by_the_system"] == {"rows": 6, "amount_to_raise_as_listed": 1010000.0,
                                        "amount_to_raise_as_the_system_works_it_out": 1010000.0, "rows_that_do_not_agree": []}
    assert d["rows"][0]["finding"] == "recovery_to_raise" and d["rows"][0]["event_id"] is None and d["rows"][4]["event_id"] == "EVT-8891"
    assert d["rows"][3]["worked_out_by_the_system"]["status"] == "outside_the_treaty_period"
    wrong = post(client, "/recovery-lists", {"summary": "One row.", "rows": [{**RECOVERIES["rows"][1], "amount_to_raise": 350000}]})["draft"]
    assert wrong["version"] == 2 and wrong["added_by_the_system"]["rows_that_do_not_agree"] == ["RCL-8804 TRY-8651"]
    assert wrong["rows"][0]["worked_out_by_the_system"]["to_raise_on_this_claim"] == 50000.0
    assert post(client, "/recovery-lists", {"summary": "Nothing is due in the period."})["draft"]["rows"] == []
    assert [x["version"] for x in get(client, "/recovery-lists/drafts")["items"]] == [1, 2, 3]
    assert recovery(client, 8803)["to_raise_on_this_claim"] == 160000.0 and len(get(client, "/recoveries")["items"]) == 2
    after = copy.deepcopy(store.data)
    after["ri_recovery_lists"]["RLIST-8800"]["drafts"] = []
    assert after == before


def test_a_recovery_list_is_refused_with_a_reason_and_nothing_is_saved(client):
    row = RECOVERIES["rows"][0]
    for body, words in (({**RECOVERIES, "rows": [{**row, "claim_id": "RCL-8899"}]}, "is not a paid claim"),
                        ({**RECOVERIES, "rows": [{**row, "treaty_id": "BND-8601"}]}, "is not a treaty"),
                        ({**RECOVERIES, "rows": [row, row]}, "given twice"),
                        ({**RECOVERIES, "claims_with_nothing_due": ["RCL-8803"]}, "Both in a row"),
                        ({**RECOVERIES, "claims_with_nothing_due": ["CLM-4001"]}, "Not a paid claim")):
        r = post(client, "/recovery-lists", body, 409)
        assert words in r["detail"] and "Nothing was saved" in r["detail"]
    assert post(client, "/recovery-lists", {**RECOVERIES, "rows": [{**row, "finding": "booked"}]}, 422)["applied"] is False
    assert get(client, "/recovery-lists/drafts")["count"] == 0


# ---------------------------------------------------------------- partners
def test_two_partners_are_fully_within(client):
    for n, levels in ((8901, ["SL-1", "SL-2", "SL-4"]), (8902, ["SL-1", "SL-2", "SL-3", "SL-4"])):
        m = partner(client, n)
        assert m["overall"] == "within" and m["not_met"] == m["cannot_tell"] == m["warnings"] == [] and m["needs_a_person"] is False
        assert [s["term"] for s in m["service_levels"]] == levels and all(s["result"] == "met" for s in m["service_levels"])
        assert all(c["result"] == "valid" for c in m["credentials"])
    a, b = partner(client, 8901), partner(client, 8902)
    assert (level(a, "SL-1")["measured"], level(a, "SL-2")["measured"], level(a, "SL-2")["working"], level(a, "SL-4")["measured"]) == (
        4.1, 1.25, "8 / 640 x 100 = 1.25 percent", 6)
    assert (level(b, "SL-1")["measured"], level(b, "SL-2")["measured"], level(b, "SL-3")["measured"], level(b, "SL-4")["measured"]) == (7.2, 2.0, 3.0, 9)
    assert [c["days_to_expiry"] for c in a["credentials"]] == [216, 125] and [c["days_to_expiry"] for c in b["credentials"]] == [308, 94]


def test_ptn_8903_missed_its_turnaround(client):
    m = partner(client, 8903)
    s = level(m, "SL-1")
    assert (m["overall"], m["not_met"]) == ("not_met", ["SL-1"]) and (s["measured"], s["limit"], s["difference"], s["result"]) == (4.2, 3.0, 1.2, "not_met")
    assert level(m, "SL-2")["measured"] == 1.2 and level(m, "SL-4")["measured"] == 5 and m["credentials"][0]["days_to_expiry"] == 186


def test_ptn_8904_has_an_expired_credential(client):
    m = partner(client, 8904)
    c = m["credentials"][1]
    assert (m["overall"], m["not_met"], m["warnings"]) == ("not_met", ["PTN-8904-C2"], [])
    assert (c["kind"], c["expires_on"], c["days_to_expiry"], c["result"]) == ("accreditation", "2026-11-14", -12, "expired")
    assert "expired on 14 Nov 2026, 12 days before 26 Nov 2026" in c["sentence"] and all(s["result"] == "met" for s in m["service_levels"])
    assert (level(m, "SL-2")["measured"], level(m, "SL-3")["measured"]) == (1.25, 2.5)


def test_ptn_8905_has_a_credential_inside_the_notice_window_which_is_a_warning(client):
    m = partner(client, 8905)
    c = m["credentials"][1]
    assert (m["overall"], m["not_met"], m["warnings"], m["needs_a_person"]) == ("warning", [], ["PTN-8905-C2"], False)
    assert (c["kind"], c["expires_on"], c["days_to_expiry"], c["notice_window_days"], c["result"]) == (
        "insurance_certificate", "2026-12-15", 19, 30, "expires_within_the_notice_window")
    assert "A warning, not a miss" in c["sentence"] and m["counted"]["credentials_expired"] == 0


def test_ptn_8906_is_exactly_on_a_service_level_and_meets_it(client):
    m = partner(client, 8906)
    s = level(m, "SL-2")
    assert (s["measured"], s["limit"], s["difference"], s["result"], s["working"]) == (2.0, 2.0, 0.0, "met", "4 / 200 x 100 = 2.00 percent")
    assert "exactly on the limit, which meets it" in s["sentence"] and m["overall"] == "within" and m["not_met"] == []


def test_ptn_8907_has_a_figure_missing_and_needs_a_person(client):
    m = partner(client, 8907)
    s = level(m, "SL-2")
    assert (m["overall"], m["cannot_tell"], m["not_met"], m["needs_a_person"]) == ("cannot_tell", ["SL-2"], [], True)
    assert (s["result"], s["measured"]) == ("cannot_tell", None) and "nothing is assumed" in s["sentence"]
    p = get(client, "/partners/PTN-8907")
    assert p["period"]["figures"]["complaints"] is None and p["period"]["figures"]["jobs"] == 510 and "empty" in p["period"]["note"]
    assert level(m, "SL-1")["measured"] == 4.6 and m["credentials"][1]["days_to_expiry"] == 66 and m["credentials"][1]["result"] == "valid"


def test_ptn_8908_has_two_service_levels_not_met(client):
    m = partner(client, 8908)
    r, late = level(m, "SL-3"), level(m, "SL-4")
    assert (m["overall"], m["not_met"]) == ("not_met", ["SL-3", "SL-4"])
    assert (r["measured"], r["limit"], r["difference"], r["working"]) == (7.5, 5.0, 2.5, "6 / 80 x 100 = 7.50 percent")
    assert (late["due_on"], late["received_on"], late["measured"], late["difference"]) == ("2026-11-10", "2026-11-17", 17, 7)
    assert m["counted"]["service_levels_not_met"] == 2 and level(m, "SL-2")["measured"] == 2.5 and level(m, "SL-1")["measured"] == 10.5


def test_the_list_of_partners_is_whole_with_the_measure_and_no_drafts(client):
    post(client, "/partners/PTN-8908/review", REVIEW)
    doc = get(client, "/partners")
    assert [(p["partner_id"], p["measured"]["overall"]) for p in doc["items"]] == [
        ("PTN-8901", "within"), ("PTN-8902", "within"), ("PTN-8903", "not_met"), ("PTN-8904", "not_met"), ("PTN-8905", "warning"),
        ("PTN-8906", "within"), ("PTN-8907", "cannot_tell"), ("PTN-8908", "not_met")]
    assert all("review_drafts" not in p for p in doc["items"]) and doc["items"][7]["drafts_on_file"] == 1
    assert [p["partner_id"] for p in get(client, "/partners?kind=repair network")["items"]] == ["PTN-8902", "PTN-8904", "PTN-8908"]
    assert get(client, "/partners?kind=broker", 409)["applied"] is False
    p = get(client, "/partners/PTN-8908")
    assert p["measured"] == {k: v for k, v in partner(client, 8908).items() if k not in ("saved", "demo_data")}
    assert p["contract"]["credentials_term"]["notice_window_days"] == 30 and [s["term"] for s in p["contract"]["service_levels"]] == [
        "SL-1", "SL-2", "SL-3", "SL-4"]


def test_a_partner_review_is_a_versioned_draft_and_not_part_of_the_partner(client, store):
    before = copy.deepcopy(store.data)
    one = post(client, "/partners/PTN-8908/review", {**REVIEW, "overall": "Not met", "needs_a_person": "No", "suggested_step": "None"})["draft"]
    assert (one["version"], one["overall"], one["needs_a_person"], one["suggested_step"], one["goes_to"]) == (1, "not_met", "no", None, "the supplier manager")
    assert one["measured_by_the_system"] == {"overall": "not_met", "overall_label": one["measured_by_the_system"]["overall_label"],
                                             "not_met": ["SL-3", "SL-4"], "warnings": [], "cannot_tell": [], "needs_a_person": False}
    two = post(client, "/partners/PTN-8908/review", {**REVIEW, "suggested_step": "review meeting with the partner",
                                                     "findings": [{"item": "sl-3", "result": "Not met"}]})["draft"]
    assert (two["version"], two["suggested_step"], two["findings"][0]["item"], two["findings"][0]["result"]) == (
        2, "review_meeting_with_the_partner", "SL-3", "not_met")
    p = get(client, "/partners/PTN-8908")
    assert p["drafts_on_file"] == 2 and "review_drafts" not in p and p["status"] == "active"
    assert [x["version"] for x in get(client, "/partners/PTN-8908/drafts")["items"]] == [1, 2]
    after = copy.deepcopy(store.data)
    after["ri_partners"]["PTN-8908"]["review_drafts"] = []
    assert after == before
    ok = post(client, "/partners/PTN-8905/review", {"overall": "warning", "summary": "One credential expires in 19 days.",
                                                    "findings": [{"item": "PTN-8905-C2", "result": "warning"}],
                                                    "suggested_step": "ask for the renewed credential"})["draft"]
    assert ok["suggested_step_label"] == "a person asks for the renewed credential"


def test_a_partner_review_is_refused_with_a_reason_and_nothing_is_saved(client):
    for body, words in (({**REVIEW, "findings": [{"item": "SL-9", "result": "met"}]}, "Not a service level or a credential"),
                        ({**REVIEW, "findings": [{"item": "PTN-8904-C2", "result": "not_met"}]}, "Not a service level or a credential"),
                        ({**REVIEW, "findings": REVIEW["findings"] + [REVIEW["findings"][0]]}, "Given twice")):
        r = post(client, "/partners/PTN-8908/review", body, 409)
        assert words in r["detail"] and "Nothing was saved" in r["detail"]
    assert post(client, "/partners/PTN-8908/review", {**REVIEW, "overall": "breach"}, 422)["applied"] is False
    assert post(client, "/partners/PTN-8999/review", REVIEW, 404)["applied"] is False
    assert get(client, "/partners/PTN-8908")["drafts_on_file"] == 0


# ---------------------------------------------------------------- reset, counts and the scenario list
def test_the_reinsurance_reset_puts_back_only_its_own_drafts(client, store):
    post(client, "/bordereaux/BDX-8701/differences", DIFFS)
    post(client, "/recovery-lists", RECOVERIES)
    post(client, "/partners/PTN-8908/review", REVIEW)
    client.post("/claims/claims/CLM-4001/triage", headers=H, json={"rule_id": "HG-3", "track": "fast track", "team": "fast-track team",
                                                                  "severity": "low", "reason": "Estimate under 2,500."})
    changed = client.get("/admin/state", headers=H).json()["changed_by"]
    assert changed["reinsurance"] == ["ri_bordereaux", "ri_partners", "ri_recovery_lists"]
    put_back = client.post("/admin/reset/reinsurance", headers=H).json()["put_back"]
    assert put_back == ["ri_bordereaux", "ri_partners", "ri_recovery_lists"]
    assert len(store.data["claims"]["CLM-4001"]["triage_drafts"]) == 1
    fresh = build_all(TODAY_D)
    assert all(store.data[name] == fresh[name] for name in RI_SETS)


def test_the_counts_name_the_open_items_of_this_system(client):
    counts = client.get("/admin/state", headers=H).json()["counts"]
    assert (counts["bordereaux_received"], counts["paid_claims_for_treaty_recovery"], counts["partners_to_review"]) == (4, 11, 8)
    assert "bordereaux received" in client.get("/").text


def test_every_id_in_the_reinsurance_section_of_the_scenarios_is_in_the_data():
    text = (Path(__file__).resolve().parent.parent / "SCENARIOS.md").read_text(encoding="utf-8")
    section = text.split("## Reinsurance and partners (system: reinsurance)")[1].split("\n## ")[0]
    data = build_reinsurance(TODAY_D)
    held = {key for records in data.values() for key in records}
    held |= {c["credential_id"] for p in data["ri_partners"].values() for c in p["credentials"]}
    held |= {f"SL-{n}" for n in range(1, 6)}
    named = set(re.findall(r"\b(?:BND-\d{4}|TRY-\d{4}|BDX-\d{4}|RCL-\d{4}|RCV-\d{4}|EVT-\d{4}|PTN-\d{4}(?:-C\d)?|RLIST-\d{4}|SL-\d)\b", section))
    assert len(named) >= 39 and named <= held, sorted(named - held)
    assert chr(8212) not in section
    for figure in ("USD 75,000.00", "USD 30.00", "USD 200.00", "USD 48,600.00", "USD 6,442.00", "USD 160,000.00", "USD 50,000.00",
                   "USD 750,000.00", "USD 1,010,000.00", "USD 38,400.00", "7.50 percent", "19 days"):
        assert figure in section, figure
