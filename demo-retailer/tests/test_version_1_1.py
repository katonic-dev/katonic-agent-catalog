"""Version 1.1: leases, restaurant performance, till rows and area manager visits.

Every planted case is read back through the API and compared with the tables in SCENARIOS.md.
"""
from collections import Counter
from datetime import date
from pathlib import Path

import pytest

from conftest import H, TODAY
from retailer.seed import build_all
from test_operations import PERIOD, get, post

TEXT = (Path(__file__).resolve().parent.parent / "SCENARIOS.md").read_text(encoding="utf-8")
TODAY_D = date.fromisoformat(TODAY)


def section(title):
    return TEXT.split(f"## {title}")[1].split("\n## ")[0]


def rows(prefix, text):
    return [[c.strip() for c in line.strip().strip("|").split("|")] for line in text.splitlines() if line.startswith(f"| {prefix}")]


def num(text):
    return float(text.replace(",", ""))


VISITS = section("Area manager visits")
LEASES = section("Leases")
PERFORMANCE = section("Restaurant performance")
TILLS = section("Refunds, voids and discounts")


# ================================================================ visits (stores)

REPORT = {"findings": [{"standard": "BS-3.2", "source": "checklist", "checklist_item": 6,
                        "what_was_found": "Toilet check sheet last signed at 11:00."},
                       {"standard": "BS-5.2", "source": "notes", "what_was_found": "Old posters still in the window."}],
          "to_clarify": ["Something is not right with the evening team."]}
V1 = "/stores/visits/SV-2610-01"


def test_the_six_visits_match_the_scenario_table(client):
    listed = get(client, "/stores/visits")
    table = [r for r in rows("SV-", VISITS) if len(r) == 5]
    assert listed["count"] == 6 == len(table)
    for row, (visit_id, site, day, manager, score) in zip(listed["items"], table):
        assert (row["visit_id"], row["site_id"], row["date"], row["area_manager"], row["score"]) == (
            visit_id, site, day, manager, int(score))
        assert row["max_score"] == 24 and row["reports"] == 0
        v = get(client, f"/stores/visits/{visit_id}")
        assert v["standards_document"] == "Brand Standards, version 2.0" and len(v["checklist"]) == 12
        assert row["findings_on_checklist"] == sum(1 for x in v["checklist"] if x["score"] < 2)
        site_row = get(client, f"/stores/sites/{site}")
        assert (v["area_manager"], v["area"], v["town"]) == (site_row["area_manager"], site_row["area"], site_row["town"])


def test_each_visit_holds_exactly_its_planted_findings_and_no_others(client):
    table = [r for r in rows("SV-", VISITS) if len(r) == 6]
    assert len(table) == 22
    tied = [r for r in table if r[2] != "none"]
    assert len(tied) == 15 and sum(1 for r in tied if r[3] == "notes") == 4
    assert sum(1 for r in table if r[3] == "to clarify") == 6
    for visit_id in sorted({r[0] for r in table}):
        v = get(client, f"/stores/visits/{visit_id}")
        mine = [r for r in table if r[0] == visit_id]
        assert {r[1] for r in mine} == {v["site_id"]}
        expected = {}
        for _, _, standard, where, score, what in mine:
            if where.startswith("checklist item"):
                expected[int(where.split()[-1])] = (standard, int(score), what)
            elif where in ("notes", "to clarify"):
                assert what in v["notes"], (visit_id, what)
        found = {x["item_no"]: (x["standard"], x["score"], x["note"]) for x in v["checklist"] if x["score"] < 2}
        assert found == expected, visit_id
        assert all(x["note"] == "" for x in v["checklist"] if x["score"] == 2)
        assert v["score"] == 24 - sum(2 - s for _, s, _ in expected.values())
    clean = get(client, "/stores/visits/SV-2610-03")
    assert clean["score"] == 24 and "Nothing to raise" in clean["notes"]


def test_the_checklist_rests_on_standards_of_the_brand_standards_document(client):
    doc = (Path(__file__).resolve().parents[2] / "retail" / "policy-library" / "brand-standards-v2.0.md")
    if not doc.exists():
        pytest.skip("the policy library is not next to this copy of the retailer")
    text = doc.read_text(encoding="utf-8")
    assert "invented" in text.splitlines()[0] and "Version: 2.0" in text
    in_document = {f"BS-{line.split()[0]}" for line in text.splitlines() if line[:1].isdigit() and line[1:2] == "."}
    from retailer.seed_visits import STANDARDS
    assert in_document == set(STANDARDS) and len(STANDARDS) == 21
    v = get(client, V1)
    assert [x["standard"] for x in v["checklist"]] == ["BS-1.1", "BS-1.2", "BS-2.1", "BS-2.2", "BS-3.1", "BS-3.2", "BS-4.1",
                                                       "BS-4.3", "BS-5.1", "BS-6.1", "BS-7.1", "BS-8.1"]


def test_visit_filters_404_and_422(client):
    assert [v["visit_id"] for v in get(client, "/stores/visits", site_id="S-106")["items"]] == ["SV-2610-02"]
    assert get(client, "/stores/visits", period=PERIOD)["count"] == 6
    assert get(client, "/stores/visits", period="2026-09")["count"] == 0
    assert get(client, "/stores/visits", site_id="R-117")["count"] == 0
    assert "list_sites" in get(client, "/stores/visits", 404, site_id="R-999")["detail"]
    assert client.get("/stores/visits", params={"period": "October"}, headers=H).status_code == 422
    r = get(client, "/stores/visits/SV-0000-00", 404)
    assert r["applied"] is False and "list_site_visits" in r["detail"]


def test_what_a_careful_reader_should_list_is_not_served(client, store):
    assert len(store.data["visit_answers"]) == 6 and len(store.data["lease_answers"]) == 9
    assert len(store.data["till_planted"]) == 28
    for path in ("/stores/visits", V1, "/property/leases", "/property/leases/LS-2001", "/tills/entries", "/tills/rules"):
        body = client.get(path, headers=H).text
        for word in ("to_clarify", "from_notes", "notice_by", "till_planted", "planted"):
            assert word not in body, (path, word)


def test_a_visit_report_is_a_draft_kept_in_versions(client):
    first = post(client, f"{V1}/report", REPORT)
    assert first["applied"] is True and first["kind"] == "draft" and first["draft"]["version"] == 1
    assert first["draft"]["drafted_by"] == "agent" and first["visit_id"] == "SV-2610-01"
    second = post(client, f"{V1}/report", {**REPORT, "drafted_by": "Store Visit Report"})
    assert second["draft"]["version"] == 2
    v = get(client, V1)
    assert [x["version"] for x in v["reports"]] == [1, 2] and v["reports"][1]["drafted_by"] == "Store Visit Report"
    assert v["reports"][0]["findings"][1]["checklist_item"] == 0 and v["reports"][0]["to_clarify"] == REPORT["to_clarify"]
    assert get(client, "/stores/visits", site_id="R-047")["items"][0]["reports"] == 2
    # a visit with nothing to report can be saved with no finding
    assert post(client, "/stores/visits/SV-2610-03/report", {"findings": []})["draft"]["findings"] == []
    post(client, "/stores/visits/SV-0000-00/report", REPORT, 404)


@pytest.mark.parametrize("finding, words", [
    ({"standard": "3.2", "source": "checklist", "checklist_item": 6, "what_was_found": "x"}, "standard"),
    ({"standard": "BS-9.9", "source": "notes", "what_was_found": "x"}, "is not a brand standard"),
    ({"standard": "BS-3.2", "source": "checklist", "checklist_item": 13, "what_was_found": "x"}, "has no item 13"),
    ({"standard": "BS-3.1", "source": "checklist", "checklist_item": 6, "what_was_found": "x"}, "rests on BS-3.2"),
    ({"standard": "BS-5.2", "source": "notes", "checklist_item": 4, "what_was_found": "x"}, "checklist_item 0"),
    ({"standard": "BS-5.2", "source": "hearsay", "what_was_found": "x"}, "source"),
    ({"standard": "BS-5.2", "source": "notes", "what_was_found": ""}, "what_was_found"),
])
def test_a_visit_report_that_does_not_fit_the_visit_is_refused_with_a_readable_message(client, finding, words):
    r = post(client, f"{V1}/report", {"findings": [finding]}, 422)
    assert r["applied"] is False and words in r["detail"], r["detail"]
    assert get(client, V1)["reports"] == []


# ================================================================ leases (property)

SUMMARY = {"term": {"start_date": "2022-07-01", "end_date": "2032-06-30", "clause": "2.1"},
           "rent": {"annual_rent": 412000, "clause": "3.1"},
           "rent_reviews": [{"review_date": "2027-07-01", "basis": "upward_or_downward", "clause": "4.2"}],
           "break_options": [{"break_date": "2027-07-01", "who_may_break": "tenant", "notice_months": 6,
                              "notice_by": "2027-01-01", "clause": "5.1"}],
           "repair_duties": [{"party": "tenant", "duty": "the whole of the premises", "clause": "6.1"}]}
L1 = "/property/leases/LS-2001"
BASIS = {"upward only": "upward_only", "market rent, up or down": "upward_or_downward", "fixed 3 percent": "fixed_increase",
         "price index, up or down": "index_linked"}


def clause(text):
    """'2027-07-01 (5.1)' -> ('2027-07-01', '5.1')"""
    body, _, number = text.rpartition(" (")
    return body, number.rstrip(")")


def test_nine_leases_five_stores_and_four_restaurants(client):
    listed = get(client, "/property/leases")
    assert listed["count"] == 9 and listed["retailer_date"] == TODAY
    assert [x["lease_id"] for x in listed["items"]] == [f"LS-200{n}" for n in range(1, 10)]
    assert sum(1 for x in listed["items"] if x["site_id"].startswith("S-")) == 5
    for x in listed["items"]:
        assert set(x) == {"lease_id", "site_id", "site_name", "town", "landlord", "tenant", "term_start", "term_end",
                          "annual_rent", "currency"}
        assert x["tenant"] == ("Rowanmere Market Ltd" if x["site_id"].startswith("S-") else "Rowanmere Kitchen Ltd")
        assert x["currency"] == "USD" and x["site_name"] == get(client, f"/stores/sites/{x['site_id']}")["name"]
    assert [x["lease_id"] for x in get(client, "/property/leases", site_id="R-031")["items"]] == ["LS-2007"]
    assert get(client, "/property/leases", site_id="S-103")["count"] == 0
    assert get(client, "/property/leases", 404, site_id="S-999")["applied"] is False
    r = get(client, "/property/leases/LS-9999", 404)
    assert "list_leases" in r["detail"]


def test_every_lease_matches_its_row_of_the_scenario_table(client, store):
    table = rows("LS-", LEASES)
    assert len(table) == 9
    for lease_id, site, landlord, term, rent, reviews, basis, brk, notice, repairs in table:
        x = get(client, f"/property/leases/{lease_id}")
        a = store.data["lease_answers"][lease_id]
        clauses = {c["number"]: c for c in x["clauses"]}
        assert (x["site_id"], x["landlord"], x["retailer_date"]) == (site, landlord, TODAY)
        span, number = clause(term)
        assert span == f"{x['term_start']} to {x['term_end']}" and number == a["term"]["clause"] == "2.1"
        assert clauses[number]["heading"] == "Term"
        amount, number = clause(rent)
        assert num(amount) == x["annual_rent"] == a["rent"]["annual_rent"] and clauses[number]["heading"] == "Rent"
        assert f"USD {amount}" in clauses[number]["text"]
        dates, number = clause(reviews)
        assert dates.split(", ") == [r["review_date"] for r in a["rent_reviews"]] and number == a["review_dates_clause"]
        kind, number = clause(basis)
        assert {r["basis"] for r in a["rent_reviews"]} == {BASIS[kind]} and number == a["review_basis_clause"]
        assert clauses[number]["heading"] == "Rent review"
        if a["break_options"]:
            b = a["break_options"][0]
            what, number = clause(brk)
            assert what == f"{b['who_may_break']}, {b['break_date']}" and number == b["clause"]
            assert clauses[number]["heading"] == "Break option"
            what, number = clause(notice)
            assert what == f"{b['notice_months']} months, so by {b['notice_by']}" and number == b["notice_clause"]
            assert "months' written notice before the break date" in clauses[number]["text"]
        else:
            assert brk.startswith("none") and notice == "none"
        assert f"({a['repairs_tenant_clause']})" in repairs and f"({a['repairs_landlord_clause']})" in repairs
        assert clauses[a["repairs_tenant_clause"]]["text"].startswith("The tenant keeps")
        assert clauses[a["repairs_landlord_clause"]]["text"].startswith("The landlord")
        # the text is the clauses, in order, under an opening line that says it is invented
        assert x["text"].startswith("INVENTED SAMPLE.") and f"LEASE {lease_id}" in x["text"]
        for c in x["clauses"]:
            assert f"{c['number']} {c['text']}" in x["text"]
        assert x["summaries"] == []


def test_the_lease_dates_are_written_out_in_the_text(client):
    x = get(client, L1)
    text = {c["number"]: c["text"] for c in x["clauses"]}
    assert text["2.1"] == "The term is 10 years. It begins on 1 July 2022 and ends on 30 June 2032."
    assert text["4.1"].startswith("The rent is reviewed on 1 July 2027.")
    assert text["5.1"] == "The tenant may end this lease on 1 July 2027 (the break date)."
    assert "not less than six months' written notice" in text["5.2"]
    assert "paid up to date" in text["5.3"] and "An email is not a notice" in text["9.1"]
    assert "2027-01-01" not in x["text"] and "1 January 2027" not in x["text"]  # the last day for the notice is not given


def test_planted_one_break_notice_falls_in_the_next_ninety_days(store):
    due = {}
    for lease_id, a in store.data["lease_answers"].items():
        for b in a["break_options"]:
            due[lease_id] = (date.fromisoformat(b["notice_by"]) - TODAY_D).days
    assert due["LS-2001"] == 38
    assert [k for k, days in due.items() if 0 <= days <= 90] == ["LS-2001"]
    assert min(days for k, days in due.items() if k != "LS-2001") > 180
    reviews_soon = {k: r["review_date"] for k, a in store.data["lease_answers"].items() for r in a["rent_reviews"]
                    if 0 <= (date.fromisoformat(r["review_date"]) - TODAY_D).days <= 90}
    assert reviews_soon == {"LS-2007": "2027-02-01"}
    assert (date(2027, 2, 1) - TODAY_D).days == 69


@pytest.mark.parametrize("today", ["2026-11-01", "2026-11-30", "2027-02-28", "2027-07-15"])
def test_the_break_notice_is_due_within_ninety_days_on_any_retailer_date(today):
    day = date.fromisoformat(today)
    answers = build_all(day)["lease_answers"]
    due = {k: (date.fromisoformat(b["notice_by"]) - day).days for k, a in answers.items() for b in a["break_options"]}
    assert [k for k, days in due.items() if 0 <= days <= 90] == ["LS-2001"]


def test_planted_one_rent_review_is_upward_only(client, store):
    upward = [k for k, a in store.data["lease_answers"].items() if a["rent_reviews"][0]["basis"] == "upward_only"]
    assert upward == ["LS-2003"]
    for lease_id in store.data["leases"]:
        text = get(client, f"/property/leases/{lease_id}")["text"]
        assert ("The rent cannot go down on a review." in text) == (lease_id == "LS-2003")
    c = {x["number"]: x["text"] for x in get(client, "/property/leases/LS-2003")["clauses"]}
    assert "higher of the open market rent and the rent payable immediately before" in c["4.2"]


def test_planted_one_lease_has_no_break_clause(client, store):
    none = [k for k, a in store.data["lease_answers"].items() if not a["break_options"]]
    assert none == ["LS-2005"]
    x = get(client, "/property/leases/LS-2005")
    assert "break" not in x["text"].lower()
    headings = []
    for c in x["clauses"]:
        if c["heading"] not in headings:
            headings.append(c["heading"])
    assert headings == ["Parties and premises", "Term", "Rent", "Rent review", "Repairs", "Service charge",
                        "Assignment and subletting", "Notices"]
    assert x["clauses"][-1]["number"] == "8.2"
    assert "may not assign this lease" in {c["number"]: c["text"] for c in x["clauses"]}["7.1"]
    for other in store.data["leases"]:
        if other != "LS-2005":
            assert "Break option" in get(client, f"/property/leases/{other}")["text"]


def test_planted_the_landlord_repairs_the_roof_and_the_tenant_everything_else(client, store):
    assert [k for k, a in store.data["lease_answers"].items() if a["repairs"] == "roof_landlord"] == ["LS-2007"]
    c = {x["number"]: x for x in get(client, "/property/leases/LS-2007")["clauses"]}
    assert c["5.1"]["text"] == "The landlord keeps the roof of the premises in good repair."
    assert c["5.2"]["text"].startswith("The tenant keeps every other part of the premises")
    assert "the structure, the outside walls" in c["5.2"]["text"]
    assert (c["5.1"]["heading"], c["6.1"]["heading"], c["7.1"]["heading"]) == ("Repairs", "Service charge", "Break option")
    assert c["7.1"]["text"].startswith("Either the landlord or the tenant may end this lease on 1 February 2032")


def test_only_the_landlord_can_break_one_lease(client, store):
    who = {k: a["break_options"][0]["who_may_break"] for k, a in store.data["lease_answers"].items() if a["break_options"]}
    assert [k for k, v in who.items() if v == "landlord"] == ["LS-2009"] and [k for k, v in who.items() if v == "either"] == ["LS-2007"]
    c = {x["number"]: x["text"] for x in get(client, "/property/leases/LS-2009")["clauses"]}
    assert "The tenant has no right to end this lease before the end of the term." in c["5.1"]


def test_a_lease_summary_is_a_draft_kept_in_versions(client):
    first = post(client, f"{L1}/summary", SUMMARY)
    assert first["applied"] is True and first["kind"] == "draft" and first["draft"]["version"] == 1
    assert first["lease_id"] == "LS-2001" and first["draft"]["drafted_by"] == "agent"
    second = post(client, f"{L1}/summary", {**SUMMARY, "drafted_by": "Lease Summary", "summary": "Break notice due soon.",
                                             "other_points": [{"point": "No service charge.", "clause": "7.1"}]})
    assert second["draft"]["version"] == 2
    saved = get(client, L1)["summaries"]
    assert [v["version"] for v in saved] == [1, 2] and saved[1]["drafted_by"] == "Lease Summary"
    assert saved[0]["break_options"][0]["notice_by"] == "2027-01-01" and saved[1]["other_points"][0]["clause"] == "7.1"
    assert get(client, "/admin/state")["counts"]["lease_summaries"] == 2
    # a lease with no break clause is saved with an empty list
    no_break = {**SUMMARY, "break_options": [], "repair_duties": [{"party": "landlord", "duty": "roof and structure", "clause": "5.1"}]}
    assert post(client, "/property/leases/LS-2005/summary", no_break)["draft"]["break_options"] == []
    post(client, "/property/leases/LS-9999/summary", SUMMARY, 404)


def test_a_lease_summary_that_cites_a_clause_the_lease_does_not_have_is_refused(client):
    wrong = {**SUMMARY, "repair_duties": [{"party": "tenant", "duty": "everything", "clause": "9.1"}]}
    r = post(client, "/property/leases/LS-2005/summary", wrong, 422)
    assert r["applied"] is False and "has no clause 9.1" in r["detail"] and "8.2" in r["detail"] and "Nothing was saved" in r["detail"]
    assert get(client, "/property/leases/LS-2005")["summaries"] == []


@pytest.mark.parametrize("change, words", [
    ({"rent_reviews": [{"review_date": "2027-07-01", "basis": "open_market", "clause": "4.2"}]}, "basis"),
    ({"rent_reviews": [{"review_date": "1 July 2027", "basis": "upward_only", "clause": "4.2"}]}, "review_date"),
    ({"break_options": [{"break_date": "2027-07-01", "who_may_break": "both", "notice_months": 6, "notice_by": "2027-01-01",
                         "clause": "5.1"}]}, "who_may_break"),
    ({"repair_duties": []}, "repair_duties"),
    ({"repair_duties": [{"party": "tenant", "duty": "all", "clause": "clause 6"}]}, "clause"),
    ({"term": {"start_date": "2022-07-01", "end_date": "2032-06-30"}}, "term.clause"),
])
def test_a_lease_summary_with_a_value_the_system_does_not_accept_is_refused(client, change, words):
    r = post(client, f"{L1}/summary", {**SUMMARY, **change}, 422)
    assert r["applied"] is False and words in r["detail"], r["detail"]


# ================================================================ performance

R47 = f"/performance/restaurants/R-047/{PERIOD}"
REVIEW = {"departures": [{"measure": "sales", "compared_with": "plan", "direction": "below", "actual": 148150,
                          "compared_to": 182000, "difference_pct": -18.6}]}
MEASURES = ("sales", "labour_cost", "labour_hours", "food_waste")
SHARES = ("labour_cost_pct_of_sales", "food_waste_pct_of_sales")


def departures(client, site_id, period=PERIOD):
    """What departs, worked out from the figures and the rules the API serves."""
    x = get(client, f"/performance/restaurants/{site_id}/{period}")
    peers = get(client, f"/performance/restaurants/{site_id}/{period}/peer-group")
    rules = x["departure_rules"]
    found = []
    for m in rules["against_plan"]["measures"]:
        if abs(x[f"{m}_against_plan_pct"]) > rules["against_plan"]["more_than_pct"]:
            found.append((m, "plan", "above" if x[f"{m}_against_plan_pct"] > 0 else "below"))
    for m in rules["against_peer_group"]["measures"]:
        if x[m] > rules["against_peer_group"]["more_than_times"] * peers["average_of_the_others"][m]:
            found.append((m, "peer_group", "above"))
    return found


def test_three_months_of_figures_for_twelve_restaurants(client):
    p = get(client, "/performance/periods")
    assert p["retailer_date"] == TODAY
    assert [(x["period"], x["restaurants"], x["is_latest"]) for x in p["items"]] == [
        ("2026-10", 12, True), ("2026-09", 12, False), ("2026-08", 12, False)]


def test_the_figures_of_the_period_match_the_scenario_table(client):
    table = rows("R-", PERFORMANCE)
    assert [r[0] for r in table] == ["R-014", "R-022", "R-031", "R-047", "R-058", "R-063", "R-071", "R-076", "R-082",
                                     "R-090", "R-104", "R-117"]
    keys = ("sales", "sales_plan", "sales_against_plan_pct", "labour_cost", "labour_cost_plan", "labour_cost_against_plan_pct",
            "labour_hours", "labour_hours_plan", "labour_hours_against_plan_pct", "food_waste", "food_waste_plan",
            "food_waste_against_plan_pct", "labour_cost_pct_of_sales", "food_waste_pct_of_sales")
    for row in table:
        x = get(client, f"/performance/restaurants/{row[0]}/{PERIOD}")
        assert x["peer_group"] == row[1] and x["currency"] == "USD" and x["reviews"] == []
        assert [x[k] for k in keys] == [num(v) for v in row[2:]], row[0]
        # the percentages follow from the amounts
        for m in MEASURES:
            assert x[f"{m}_against_plan_pct"] == round(100 * (x[m] - x[f"{m}_plan"]) / x[f"{m}_plan"], 1) + 0.0
        assert x["labour_cost_pct_of_sales"] == round(100 * x["labour_cost"] / x["sales"], 1)
        assert x["food_waste_pct_of_sales"] == round(100 * x["food_waste"] / x["sales"], 1)
        assert x["labour_cost_plan"] == round(x["sales_plan"] * 0.26, -1) and x["food_waste_plan"] == round(x["sales_plan"] * 0.02, -1)


EXPECTED_DEPARTURES = {
    "R-022": [("sales", "plan", "above"), ("food_waste", "plan", "below")],
    "R-031": [("food_waste", "plan", "above"), ("food_waste_pct_of_sales", "peer_group", "above")],
    "R-047": [("sales", "plan", "below"), ("labour_cost", "plan", "above"), ("labour_hours", "plan", "above")],
}
ALL_RESTAURANTS = ["R-014", "R-022", "R-031", "R-047", "R-058", "R-063", "R-071", "R-076", "R-082", "R-090", "R-104", "R-117"]


@pytest.mark.parametrize("site_id", ALL_RESTAURANTS)
def test_each_restaurant_has_exactly_its_planted_departures(client, site_id):
    assert departures(client, site_id) == EXPECTED_DEPARTURES.get(site_id, [])


def test_planted_one_restaurant_is_well_under_its_sales_plan_with_labour_over_plan(client):
    x = get(client, R47)
    assert (x["sales"], x["sales_plan"], x["sales_against_plan_pct"]) == (148150.0, 182000.0, -18.6)
    assert (x["labour_cost"], x["labour_cost_plan"], x["labour_cost_against_plan_pct"]) == (51340.0, 47320.0, 8.5)
    assert (x["labour_hours"], x["labour_hours_plan"], x["labour_hours_against_plan_pct"]) == (3557.0, 3263.0, 9.0)
    assert x["food_waste_against_plan_pct"] == 1.1 and x["labour_cost_pct_of_sales"] == 34.7
    peers = get(client, f"{R47}/peer-group")
    assert peers["average_of_the_others"]["labour_cost_pct_of_sales"] == 25.8  # 34.7 is 1.34 times, below 1.5
    assert round(34.7 / 25.8, 2) == 1.34
    assert [get(client, f"/performance/restaurants/R-047/{p}")["sales_against_plan_pct"] for p in ("2026-08", "2026-09")] == [-2.8, -9.5]
    assert departures(client, "R-047", "2026-09") == [("sales", "plan", "below")] and departures(client, "R-047", "2026-08") == []


def test_planted_one_restaurant_wastes_about_twice_its_peer_group(client):
    x = get(client, f"/performance/restaurants/R-031/{PERIOD}")
    assert (x["food_waste"], x["food_waste_plan"], x["food_waste_against_plan_pct"], x["food_waste_pct_of_sales"]) == (
        6640.0, 3160.0, 110.1, 4.2)
    peers = get(client, f"/performance/restaurants/R-031/{PERIOD}/peer-group")
    assert (peers["peer_group"], peers["name"], peers["site_id"]) == ("PG-2", "Marlow Reach restaurants", "R-031")
    assert [m["site_id"] for m in peers["members"]] == ["R-031", "R-063", "R-076", "R-104"]
    assert peers["average_of_the_others"]["food_waste_pct_of_sales"] == 2.0 and round(4.2 / 2.0, 1) == 2.1
    assert all(abs(x[f"{m}_against_plan_pct"]) < 2 for m in ("sales", "labour_cost", "labour_hours"))
    assert [get(client, f"/performance/restaurants/R-031/{p}")["food_waste_against_plan_pct"] for p in ("2026-08", "2026-09")] == [3.9, 39.9]


def test_planted_one_restaurant_is_ahead_on_everything(client):
    x = get(client, f"/performance/restaurants/R-022/{PERIOD}")
    assert (x["sales"], x["sales_plan"], x["sales_against_plan_pct"]) == (183650.0, 171000.0, 7.4)
    assert (x["food_waste"], x["food_waste_plan"], x["food_waste_against_plan_pct"]) == (3010.0, 3420.0, -12.0)
    assert (x["labour_cost_against_plan_pct"], x["labour_hours_against_plan_pct"]) == (-2.8, -3.2)
    for p in ("2026-08", "2026-09"):
        y = get(client, f"/performance/restaurants/R-022/{p}")
        assert y["sales_against_plan_pct"] > 0 and y["labour_cost_against_plan_pct"] < 0 and y["food_waste_against_plan_pct"] < 0


def test_the_other_nine_restaurants_sit_near_plan(client):
    for site_id in ALL_RESTAURANTS:
        if site_id in EXPECTED_DEPARTURES:
            continue
        x = get(client, f"/performance/restaurants/{site_id}/{PERIOD}")
        peers = get(client, f"/performance/restaurants/{site_id}/{PERIOD}/peer-group")["average_of_the_others"]
        assert max(abs(x[f"{m}_against_plan_pct"]) for m in MEASURES) <= 3.2, site_id
        assert max(x[m] / peers[m] for m in SHARES) <= 1.115, site_id


def test_the_rules_are_served_with_the_figures(client):
    rules = get(client, R47)["departure_rules"]
    assert rules["against_plan"]["more_than_pct"] == 5.0 and rules["against_plan"]["measures"] == list(MEASURES)
    assert rules["against_peer_group"]["more_than_times"] == 1.5 and rules["against_peer_group"]["measures"] == list(SHARES)
    assert "nothing about any" in rules["what_the_figures_do_not_decide"] and "area manager" in rules["what_the_figures_do_not_decide"]


def test_performance_404_409_and_422(client):
    r = get(client, f"/performance/restaurants/S-101/{PERIOD}", 404)
    assert r["applied"] is False and "is a store" in r["detail"]
    assert "list_sites" in get(client, f"/performance/restaurants/R-999/{PERIOD}", 404)["detail"]
    assert "2026-10, 2026-09, 2026-08" in get(client, "/performance/restaurants/R-047/2026-07", 404)["detail"]
    r = get(client, "/performance/restaurants/R-047/2026-11", 409)
    assert r["applied"] is False and "has not ended" in r["detail"]
    get(client, "/performance/restaurants/R-047/2026-11/peer-group", 409)
    get(client, "/performance/restaurants/S-101/2026-10/peer-group", 404)
    assert client.get("/performance/restaurants/R-047/October", headers=H).status_code == 422
    post(client, "/performance/restaurants/R-047/2026-11/review", REVIEW, 409)
    post(client, "/performance/restaurants/R-047/2026-07/review", REVIEW, 404)
    post(client, f"/performance/restaurants/S-101/{PERIOD}/review", REVIEW, 404)


def test_a_performance_review_is_a_draft_kept_in_versions(client):
    first = post(client, f"{R47}/review", REVIEW)
    assert first["applied"] is True and first["kind"] == "draft" and first["draft"]["version"] == 1
    assert (first["site_id"], first["period"]) == ("R-047", PERIOD)
    peer = {"measure": "food_waste_pct_of_sales", "compared_with": "peer_group", "direction": "above", "actual": 4.2,
            "compared_to": 2.0, "times_peer_average": 2.1}
    second = post(client, f"{R47}/review", {"departures": [peer], "drafted_by": "Restaurant Performance Review"})
    assert second["draft"]["version"] == 2
    saved = get(client, R47)["reviews"]
    assert [v["version"] for v in saved] == [1, 2] and saved[0]["departures"][0]["difference_pct"] == -18.6
    assert saved[1]["drafted_by"] == "Restaurant Performance Review"
    assert get(client, R47)["sales"] == 148150.0  # the figures are untouched
    # nothing departs: an empty list is saved
    assert post(client, f"/performance/restaurants/R-058/{PERIOD}/review", {"departures": []})["draft"]["departures"] == []
    assert get(client, "/admin/state")["counts"]["performance_reviews"] == 3


@pytest.mark.parametrize("departure, words", [
    ({"measure": "sales", "compared_with": "peer_group", "direction": "below", "actual": 1, "compared_to": 2}, "cannot be compared with peer_group"),
    ({"measure": "food_waste_pct_of_sales", "compared_with": "plan", "direction": "above", "actual": 1, "compared_to": 2}, "cannot be compared with plan"),
    ({"measure": "profit", "compared_with": "plan", "direction": "below", "actual": 1, "compared_to": 2}, "measure"),
    ({"measure": "sales", "compared_with": "plan", "direction": "down", "actual": 1, "compared_to": 2}, "direction"),
    ({"measure": "sales", "compared_with": "plan", "direction": "below"}, "actual"),
])
def test_a_review_with_a_value_the_system_does_not_accept_is_refused(client, departure, words):
    r = post(client, f"{R47}/review", {"departures": [departure]}, 422)
    assert r["applied"] is False and words in r["detail"], r["detail"]
    assert get(client, R47)["reviews"] == []


def test_the_performance_periods_follow_the_retailer_date():
    d = build_all(date(2027, 1, 5))
    assert sorted({x["period"] for x in d["performance"].values()}) == ["2026-10", "2026-11", "2026-12"]
    assert d["performance"]["R-047:2026-12"]["sales_against_plan_pct"] == -18.6


# ================================================================ tills

AUDIT = {"rows": [{"row_id": "TR-2610-0064", "rules": ["TC-1", "TC-2"], "note": "No approver and no receipt number."},
                  {"row_id": "TR-2610-0016", "rules": ["TC-1"]}]}
AUDITS = f"/tills/audits/{PERIOD}"


def all_rows(client, **params):
    return get(client, "/tills/entries", limit=500, **params)["items"]


def outside(row):
    """The rules a row is outside, worked out from the row and the four rules in SCENARIOS.md."""
    found = []
    if row["kind"] == "refund" and row["amount"] > 50.00 and row["approver_id"] == "":
        found.append("TC-1")
    if row["kind"] == "refund" and row["original_receipt"] == "":
        found.append("TC-2")
    if row["kind"] == "discount" and row["discount_percent"] > 20 and row["reason_code"] == "":
        found.append("TC-3")
    if row["kind"] == "void" and row["after_payment"] is True and row["approver_id"] == "":
        found.append("TC-4")
    return found


def test_the_four_till_rules(client):
    rules = get(client, "/tills/rules")
    assert (rules["document"], rules["version"]) == ("Till Controls", "1.3") and "invented" in rules["notice"]
    assert [(r["rule_id"], r["applies_to"]) for r in rules["rules"]] == [
        ("TC-1", "refund"), ("TC-2", "refund"), ("TC-3", "discount"), ("TC-4", "void")]
    text = {r["rule_id"]: r["text"] for r in rules["rules"]}
    assert "above USD 50.00" in text["TC-1"] and "manager's approval" in text["TC-1"]
    assert "original receipt number" in text["TC-2"] and "above 20 percent" in text["TC-3"] and "second person" in text["TC-4"]
    assert all(r["how_to_test"] for r in rules["rules"]) and sorted(rules["discount_reason_codes"]) == ["D1", "D2", "D3", "D4", "D5"]
    assert "do not say that any colleague did anything wrong" in rules["what_the_rules_do_not_decide"]
    table = rows("TC-", TILLS)
    assert [(r[0], r[1]) for r in table] == [(r["rule_id"], r["applies_to"]) for r in rules["rules"]]


def test_till_rows_totals_filters_and_paging(client):
    first = get(client, "/tills/entries")
    assert (first["total"], first["count"], first["limit"], first["offset"]) == (180, 100, 100, 0)
    rest = get(client, "/tills/entries", offset=100)
    assert rest["count"] == 80 and rest["items"][-1]["row_id"] == "TR-2610-0180" and first["items"][0]["row_id"] == "TR-2610-0001"
    assert "`TR-2610-0001` to `TR-2610-0180`" in TILLS and "72 refunds, 48 voids and 60 discounts" in TILLS
    every = all_rows(client)
    assert len(every) == 180 and [r["row_id"] for r in every] == sorted(r["row_id"] for r in every)
    assert [(r["date"], r["time"]) for r in every] == sorted((r["date"], r["time"]) for r in every)
    assert Counter(r["kind"] for r in every) == {"refund": 72, "void": 48, "discount": 60}
    assert {r["date"][:7] for r in every} == {PERIOD} and len({r["site_id"] for r in every}) == 20
    for kind, n in (("refund", 72), ("void", 48), ("discount", 60)):
        assert get(client, "/tills/entries", kind=kind, limit=500)["total"] == n
    assert get(client, "/tills/entries", site_id="S-106")["total"] == 27
    assert get(client, "/tills/entries", site_id="S-106", kind="refund", period=PERIOD)["total"] == len(
        [r for r in every if r["site_id"] == "S-106" and r["kind"] == "refund"])
    assert get(client, "/tills/entries", period="2026-09")["total"] == 0
    assert get(client, "/tills/entries", limit=5, offset=178)["count"] == 2
    assert "Site ids" in get(client, "/tills/entries", 404, site_id="S-999")["detail"]
    for bad in ({"kind": "sale"}, {"limit": 501}, {"period": "2026"}, {"offset": -1}):
        assert client.get("/tills/entries", params=bad, headers=H).status_code == 422, bad


def test_a_till_row_names_no_colleague(client):
    for r in all_rows(client):
        assert set(r) == {"row_id", "date", "time", "site_id", "till", "cashier_id", "kind", "amount", "currency", "reason",
                          "approver_id", "original_receipt", "sale_amount", "discount_percent", "reason_code", "after_payment"}
        assert r["cashier_id"].startswith("C-") and r["cashier_id"][2:].isdigit() and r["currency"] == "USD"
        assert r["approver_id"] == "" or r["approver_id"][:2] in ("M-", "C-")
        assert r["approver_id"] != r["cashier_id"] and r["amount"] > 0
        assert (r["discount_percent"] is not None) == (r["kind"] == "discount") == (r["sale_amount"] is not None)
        assert (r["after_payment"] is not None) == (r["kind"] == "void")
        if r["kind"] == "discount":
            assert r["amount"] == round(r["sale_amount"] * r["discount_percent"] / 100 + 1e-9, 2)


def test_the_rows_outside_the_rules_are_exactly_the_scenario_table(client):
    found = {r["row_id"]: (r, outside(r)) for r in all_rows(client) if outside(r)}
    table = rows("TR-", TILLS)
    assert len(table) == 28 == len(found) and [r[0] for r in table] == sorted(found)
    for row_id, day, time, site, till, cashier, kind, amount, rules, _ in table:
        r, broken = found[row_id]
        assert (r["date"], r["time"], r["site_id"], r["till"], r["cashier_id"], r["kind"], r["amount"]) == (
            day, time, site, till, cashier, kind, num(amount)), row_id
        assert broken == rules.split(", "), row_id


def test_planted_the_rules_are_broken_an_exact_number_of_times(client, store):
    every = all_rows(client)
    broken = Counter(rule for r in every for rule in outside(r))
    assert broken == {"TC-1": 9, "TC-2": 7, "TC-3": 8, "TC-4": 6}
    both = sorted(r["row_id"] for r in every if len(outside(r)) == 2)
    assert both == ["TR-2610-0064", "TR-2610-0090"]
    assert {k: v for k, v in store.data["till_planted"].items()} == {r["row_id"]: outside(r) for r in every if outside(r)}
    # many rows are within the rules, some only just
    within = [r for r in every if not outside(r)]
    assert len(within) == 152
    assert sum(1 for r in within if r["kind"] == "refund" and r["amount"] == 50.00 and not r["approver_id"]) == 3
    assert sum(1 for r in within if r["kind"] == "refund" and r["amount"] > 50.00) == 24
    assert sum(1 for r in within if r["kind"] == "discount" and r["discount_percent"] > 20) == 13
    assert sum(1 for r in within if r["kind"] == "discount" and r["discount_percent"] == 20 and not r["reason_code"]) >= 5
    assert sum(1 for r in within if r["kind"] == "void" and not r["after_payment"]) == 17
    assert sum(1 for r in within if r["kind"] == "void" and r["after_payment"]) == 25


def test_planted_one_site_and_one_cashier_id_stand_out(client):
    every = all_rows(client)
    flagged = [r for r in every if outside(r)]
    by_site = Counter(r["site_id"] for r in flagged)
    assert by_site.most_common(3) == [("S-106", 12), ("S-101", 2), ("S-104", 2)] and len(by_site) == 15
    by_cashier = Counter(r["cashier_id"] for r in flagged)
    assert by_cashier.most_common(3) == [("C-3173", 8), ("C-3171", 2), ("C-3174", 2)]
    assert sum(1 for n in by_cashier.values() if n == 1) == 16
    assert {r["site_id"] for r in every if r["cashier_id"] == "C-3173"} == {"S-106"}
    assert sum(1 for r in every if r["cashier_id"] == "C-3173") == 12
    assert sorted({r["site_id"] for r in every} - set(by_site)) == ["R-071", "R-076", "R-082", "R-117", "S-108"]
    for words in ("twelve of the 28 are at S-106", "Eight of the twelve at S-106 carry cashier id C-3173",
                  "R-071, R-076, R-082, R-117 and S-108"):
        assert words in TILLS, words


def test_two_rows_only_just_within_the_rules(client):
    every = {r["row_id"]: r for r in all_rows(client)}
    refund, discount = every["TR-2610-0019"], every["TR-2610-0002"]
    assert (refund["site_id"], refund["kind"], refund["amount"], refund["approver_id"]) == ("R-117", "refund", 50.0, "")
    assert refund["original_receipt"] and outside(refund) == []
    assert (discount["site_id"], discount["kind"], discount["discount_percent"], discount["reason_code"]) == ("R-117", "discount", 20.0, "")
    assert (discount["amount"], discount["sale_amount"]) == (23.82, 119.08) and outside(discount) == []
    assert get(client, "/tills/entries", site_id="R-117")["total"] == 9
    assert "`TR-2610-0019` is a refund of exactly 50.00" in TILLS and "(23.82 off 119.08)" in TILLS


def test_a_till_audit_is_a_draft_kept_in_versions(client):
    assert get(client, AUDITS) == {"demo_data": True, "period": PERIOD, "count": 0, "audits": []}
    first = post(client, AUDITS, AUDIT)
    assert first["applied"] is True and first["kind"] == "draft" and first["draft"]["version"] == 1 and first["period"] == PERIOD
    second = post(client, AUDITS, {"rows": [{"row_id": "TR-2610-0016", "rules": ["TC-1"]}], "site_id": "S-106",
                                   "drafted_by": "Refund and Discount Audit"})
    assert second["draft"]["version"] == 2 and second["draft"]["site_id"] == "S-106"
    saved = get(client, AUDITS)
    assert saved["count"] == 2 and [v["version"] for v in saved["audits"]] == [1, 2]
    assert saved["audits"][0]["rows"][0] == AUDIT["rows"][0] and saved["audits"][0]["site_id"] == ""
    assert get(client, "/tills/entries", limit=500)["total"] == 180  # no row is changed
    # an audit that finds nothing is saved with no rows
    assert post(client, AUDITS, {"rows": [], "site_id": "R-117"})["draft"]["rows"] == []
    assert get(client, "/admin/state")["counts"]["till_audits"] == 3


def test_a_till_audit_404_409_and_422(client):
    r = post(client, AUDITS, {"rows": [{"row_id": "TR-2610-9999", "rules": ["TC-1"]}]}, 404)
    assert r["applied"] is False and "TR-2610-9999" in r["detail"] and "Nothing was saved" in r["detail"]
    r = post(client, AUDITS, {"rows": [{"row_id": "TR-2610-0020", "rules": ["TC-1"]}], "site_id": "S-106"}, 404)
    assert "The row is at S-101" in r["detail"]
    post(client, AUDITS, {"rows": [], "site_id": "S-999"}, 404)
    r = post(client, "/tills/audits/2026-11", {"rows": []}, 409)
    assert r["applied"] is False and "has not ended" in r["detail"] and "2026-10" in r["detail"]
    assert "2026-10" in post(client, "/tills/audits/2026-07", {"rows": []}, 404)["detail"]
    r = post(client, AUDITS, {"rows": AUDIT["rows"] + [{"row_id": "TR-2610-0016", "rules": ["TC-1"]}]}, 422)
    assert "listed twice" in r["detail"]
    for bad in ({"row_id": "TR-2610-0016", "rules": ["TC-9"]}, {"row_id": "TR-2610-0016", "rules": []}, {"rules": ["TC-1"]}):
        assert post(client, AUDITS, {"rows": [bad]}, 422)["applied"] is False
    assert client.post("/tills/audits/October", json={"rows": []}, headers=H).status_code == 422
    assert client.get("/tills/audits/October", headers=H).status_code == 422
    assert get(client, AUDITS)["count"] == 0


def test_the_till_rows_follow_the_retailer_date():
    d = build_all(date(2027, 3, 9))
    assert len(d["till_rows"]) == 180 and all(k.startswith("TR-2702-") for k in d["till_rows"])
    assert {r["date"][:7] for r in d["till_rows"].values()} == {"2027-02"} and len(d["till_planted"]) == 28
    assert all(k.startswith("SV-2702-") for k in d["site_visits"])


# ================================================================ reset of each new system

def test_each_new_system_is_put_back_on_its_own(client, store):
    post(client, f"{V1}/report", REPORT)
    post(client, f"{L1}/summary", SUMMARY)
    post(client, f"{R47}/review", REVIEW)
    post(client, AUDITS, AUDIT)
    assert get(client, "/admin/state")["changed_by"] == {
        "performance": ["performance_reviews"], "property": ["leases"], "stores": ["site_visits"], "tills": ["till_audits"]}
    r = post(client, "/admin/reset/property")
    assert r["put_back"] == ["leases"] and r["counts"]["lease_summaries"] == 0
    assert get(client, L1)["summaries"] == [] and len(get(client, R47)["reviews"]) == 1
    r = post(client, "/admin/reset/performance")
    assert r["put_back"] == ["performance_reviews"] and get(client, R47)["reviews"] == []
    assert get(client, AUDITS)["count"] == 1 and len(get(client, V1)["reports"]) == 1
    r = post(client, "/admin/reset/tills")
    assert r["put_back"] == ["till_audits"] and get(client, AUDITS)["count"] == 0
    r = post(client, "/admin/reset/stores")
    assert r["put_back"] == ["site_visits"] and get(client, V1)["reports"] == []
    assert store.data == build_all(TODAY_D) and store.changed == {}


def test_a_full_reset_puts_the_new_systems_back(client, store):
    post(client, f"{V1}/report", REPORT)
    post(client, f"{L1}/summary", SUMMARY)
    post(client, f"{R47}/review", REVIEW)
    post(client, AUDITS, AUDIT)
    post(client, "/admin/simulate/site-visit")
    assert store.data != build_all(TODAY_D)
    counts = post(client, "/admin/reset")["counts"]
    assert store.data == build_all(TODAY_D)
    assert (counts["leases"], counts["site_visits"], counts["site_visits_without_a_report"], counts["performance_periods"]) == (9, 6, 6, 3)
    assert (counts["till_refunds"], counts["till_voids"], counts["till_discounts"]) == (72, 48, 60)
    assert (counts["lease_summaries"], counts["performance_reviews"], counts["till_audits"]) == (0, 0, 0)


# ================================================================ the event site-visit

def simulate(client):
    r = client.post("/admin/simulate/site-visit", headers=H)
    assert r.status_code == 200, r.text
    return r.json()


def test_site_visit_four_templates_in_turn(client, store):
    expected = [
        ("R-022", [], 0, 0),
        ("S-101", [(5, "BS-3.1", 0), (9, "BS-5.1", 1)], 0, 0),
        ("R-063", [(3, "BS-2.1", 1)], 1, 1),
        ("S-107", [], 0, 1),
    ]
    made = []
    for n in range(8):
        r = simulate(client)
        site, items, in_notes, vague = expected[n % 4]
        made.append(r["item_id"])
        assert r["item_id"] == f"SV-2611-{n + 1:02d}" and r["event_type"] == "site-visit" and r["system"] == "stores"
        assert r["item_id"] in r["message"] and site in r["message"] and "stores system" in r["message"]
        assert "has arrived" in r["message"] and "get_site_visit" in r["message"]
        v = get(client, f"/stores/visits/{r['item_id']}")
        assert (v["site_id"], v["date"], v["reports"]) == (site, TODAY, [])
        assert v["area_manager"] == get(client, f"/stores/sites/{site}")["area_manager"] and v["area_manager"] in r["message"]
        assert [(x["item_no"], x["standard"], x["score"]) for x in v["checklist"] if x["score"] < 2] == items
        answer = store.data["visit_answers"][r["item_id"]]
        assert (len(answer["from_notes"]), len(answer["to_clarify"])) == (in_notes, vague)
        for f in answer["from_notes"]:
            assert f["what"] in v["notes"]
        for sentence in answer["to_clarify"]:
            assert sentence in v["notes"]
    assert len(set(made)) == 8 and get(client, "/stores/visits")["count"] == 14
    assert get(client, "/stores/visits", period="2026-11")["count"] == 8
    assert get(client, "/admin/state")["counts"]["site_visits_without_a_report"] == 14
    wet = get(client, "/stores/visits/SV-2611-03")
    assert "wet and there was no sign" in wet["notes"] and store.data["visit_answers"]["SV-2611-03"]["from_notes"][0]["standard"] == "BS-7.2"


def test_a_visit_that_arrives_belongs_to_stores_and_goes_back_with_it(client, store):
    post(client, "/purchasing/invoices/INV-5120/query", {"raised_by": "C. Payer", "message": "Please explain."})
    assert simulate(client)["item_id"] == "SV-2611-01"
    assert get(client, "/admin/state")["changed_by"]["stores"] == ["site_visits", "visit_answers"]
    r = post(client, "/admin/reset/stores")
    assert r["put_back"] == ["site_visits", "visit_answers"] and len(store.data["site_visits"]) == 6
    assert get(client, "/purchasing/invoices/INV-5120")["status"] == "queried"
    assert simulate(client)["item_id"] == "SV-2611-01"  # the count of arrivals went back too
    items = get(client, "/admin/events")["items"]
    assert [e["event_type"] for e in items] == ["site-visit", "site-visit"]


def test_a_subscription_can_ask_for_site_visits_only(client):
    sub = client.post("/admin/subscriptions", json={"event_kind": "site-visit", "url": "http://127.0.0.1:9/none"}, headers=H)
    assert sub.status_code == 200 and sub.json()["subscription"]["event_kind"] == "site-visit"
    assert simulate(client)["deliveries"][0]["status"] == "queued"
    assert client.post("/admin/simulate/supplier-invoice", headers=H).json()["deliveries"] == []
    assert "site-visit" in client.post("/admin/simulate/nonsense", headers=H).json()["detail"]
    assert "site-visit" in client.get("/").text
