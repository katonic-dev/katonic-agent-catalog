"""The portfolio system: the right answers of the Portfolio section of SCENARIOS.md, every refusal, and the rules a draft keeps.

Checked against the data the service gives at the insurer date 2026-11-26."""
import json
import re
from datetime import date
from pathlib import Path

from insurer.common import ForgivingModel
from insurer.seed import build_all
from insurer.seed_health import COMPLETE_BENEFITS
from insurer.seed_portfolio import build_portfolio, find_target
from insurer.seed_underwriting import GUIDELINES
from insurer.systems import portfolio as portfolio_system
from conftest import H, TODAY

TODAY_D = date.fromisoformat(TODAY)
PF_SETS = sorted(build_portfolio(TODAY_D))
SECTION = (Path(__file__).resolve().parent.parent / "SCENARIOS.md").read_text(encoding="utf-8").split(
    "## Portfolio (system: portfolio)")[1].split("\n## ")[0]


def get(client, path, status=200, **params):
    r = client.get(f"/portfolio{path}", headers=H, params=params or None)
    assert r.status_code == status, (path, r.status_code, r.text[:400])
    return r.json()


def post(client, path, body, status=200):
    r = client.post(f"/portfolio{path}", json=body, headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:400])
    return r.json()


def money(x):
    return f"{x:,.2f}"


def says(*texts):
    """Every one of these figures or words is in the Portfolio section of SCENARIOS.md, exactly."""
    for text in texts:
        assert text in SECTION, text


def impact(client, n):
    return get(client, f"/proposed-changes/PCR-{n}")["impact"]


def touched(x):
    return [r["item_id"] for r in x["items_touched"]]


def change(client, segment, **params):
    return get(client, f"/segments/SEG-{segment}/premium-change", **params)


def query(client, status=200, **params):
    return get(client, "/warehouse/query", status, **params)


def limit(client, n):
    return get(client, "/concentration-limits/measure", limit_id=f"LIM-{n}")["items"][0]


QUESTION = {"topic": "product_change", "about": "PCR-8503", "question": "Would the reinsurers agree to flood being covered?",
            "why_the_system_does_not_settle_it": "The catalogue holds a note of the clauses the treaty relies on, not the treaty.",
            "for_whom": "Marguerite Tolland, reinsurance manager"}


# ---------------------------------------------------------------- the system as a whole
def test_the_portfolio_system_has_17_operations_and_its_one_save_is_a_draft(client):
    doc = client.get("/portfolio/openapi.json").json()
    ops = [(method, op) for item in doc["paths"].values() for method, op in item.items()]
    assert len(ops) == 17
    assert [op["operationId"] for method, op in ops if method != "get"] == ["save_portfolio_question_for_a_person"]
    for method, op in ops:
        assert not op["summary"].endswith("(change)"), op["operationId"]
        if method != "get":
            assert op["summary"].endswith("(draft)")
        says(f"`{op['operationId']}`")
    assert client.get("/portfolio/products").status_code == 401
    assert "portfolio/openapi.json" in client.get("/").text


def test_the_request_model_is_forgiving_and_reads_plain_words(client):
    assert issubclass(portfolio_system.QuestionForAPerson, ForgivingModel)
    saved = post(client, "/questions", {**QUESTION, "topic": "Product change"})
    assert saved["draft"]["topic"] == "product_change"


def test_portfolio_ids_have_their_own_ranges_and_collide_with_nothing():
    data = build_all(TODAY_D)
    prefixes = {"pf_products": "PRD-83", "pf_items": "DEP-84", "pf_change_requests": "PCR-85", "pf_pricing_method": "PM-",
                "pf_segments": "SEG-86", "pf_warehouse": "WR-", "pf_limits": "LIM-"}
    for name, prefix in prefixes.items():
        assert data[name] and all(key.startswith(prefix) for key in data[name]), name
    mine = {key for name in PF_SETS for key in data[name]}
    others = {key for name, records in data.items() if name not in PF_SETS and isinstance(records, dict) for key in records}
    assert not mine & others
    assert data["pf_questions"] == {}


def test_no_text_of_the_portfolio_data_holds_a_bare_date_counts_days_or_names_a_weekday():
    data = build_portfolio(TODAY_D)
    for c in data["pf_change_requests"].values():
        assert not re.search(r"\b20\d\d-\d\d-\d\d\b", c["text"]) and "Proposal of " in c["text"]
    blob = json.dumps(data).lower()
    for word in ("yesterday", "last week", "days ago", "weeks ago", "last month", "this morning", "tomorrow", "monday", "tuesday",
                 "wednesday", "thursday", "friday", "saturday", "sunday", chr(8212)):
        assert word not in blob, word
    assert chr(8212) not in SECTION


def test_every_reference_of_the_catalogue_names_a_clause_a_section_or_a_factor_that_exists():
    data = build_portfolio(TODAY_D)
    for item in data["pf_items"].values():
        assert item["product_id"] in data["pf_products"] and item["refers_to"]
        for ref in item["refers_to"]:
            found = find_target(data, ref["target_id"])
            assert found and found[0]["product_id"] == item["product_id"], (item["item_id"], ref["target_id"])
            assert (ref["applies_when"] is not None) == (found[2] == "section"), (item["item_id"], ref["target_id"])
    for c in data["pf_change_requests"].values():
        assert all(find_target(data, t) for t in c["targets"])


def test_the_catalogue_stays_in_step_with_the_policy_health_and_underwriting_systems(client):
    data = build_all(TODAY_D)
    for product_id, wording_id in (("PRD-8301", "TMI-MOT-01"), ("PRD-8302", "TMI-HOM-02")):
        clauses = {s["clause"]: s["text"] for s in data["pf_products"][product_id]["sections"] if s["kind"] == "clause"}
        assert clauses == {c["clause"]: c["text"] for c in data["wordings"][wording_id]["clauses"]}
    maternity = next(b for b in COMPLETE_BENEFITS if b["benefit_id"] == "BEN-F08")
    assert maternity["waiting_period_days"] == 300
    assert "300 days" in get(client, "/references/SEC-8304-BEN-F08")["target"]["text"]
    for item_id, rule_id in (("DEP-8427", "UG-6"), ("DEP-8428", "UG-5"), ("DEP-8429", "UG-3"), ("DEP-8430", "UG-1")):
        item = data["pf_items"][item_id]
        assert item["reference"] == rule_id and GUIDELINES[rule_id]["text"] in item["the_catalogue_holds"]
    assert "USD 2,500" in GUIDELINES["UG-6"]["text"] and "USD 5,000" in GUIDELINES["UG-6"]["text"]


def test_every_id_in_the_portfolio_section_of_the_scenarios_is_in_the_data():
    data = build_all(TODAY_D)
    held = {key for name in PF_SETS for key in data[name]}
    for p in data["pf_products"].values():
        held |= {s["section_id"] for s in p["sections"]} | {f["factor_id"] for f in p["rating_factors"]}
    named = set(re.findall(r"\b(?:PRD-\d{4}|DEP-\d{4}|PCR-\d{4}|SEG-\d{4}|LIM-\d|PM-\d|SEC-\d{4}-[A-Z0-9.-]*[A-Z0-9]|FAC-\d{4}-\d)\b",
                           SECTION))
    assert len(named) > 60 and named <= held, sorted(named - held)
    assert set(re.findall(r"\bPCR-\d{4}\b", SECTION)) == set(data["pf_change_requests"])
    assert set(re.findall(r"\bSEG-\d{4}\b", SECTION)) == set(data["pf_segments"])
    assert set(re.findall(r"\bLIM-\d\b", SECTION)) == set(data["pf_limits"])
    assert set(re.findall(r"\bPQ-87\d\d\b", SECTION)) == {f"PQ-87{n:02d}" for n in range(1, 8)}
    assert set(re.findall(r"\bEXQ-88\d\d\b", SECTION)) == {f"EXQ-88{n:02d}" for n in range(1, 9)}


# ---------------------------------------------------------------- the product catalogue
def test_the_catalogue_has_four_products_and_says_what_it_never_holds(client):
    doc = get(client, "/products")
    assert [p["product_id"] for p in doc["items"]] == ["PRD-8301", "PRD-8302", "PRD-8303", "PRD-8304"]
    assert [p["dependent_items"] for p in doc["items"]] == [6, 6, 10, 7] and len(doc["the_catalogue_never_holds"]) == 4
    p = get(client, "/products/PRD-8303")
    assert len([s for s in p["sections"] if s["kind"] == "clause"]) == 13 and len(p["rating_factors"]) == 5
    assert [i["item_id"] for i in p["dependent_items"]] == [f"DEP-84{n}" for n in range(21, 31)]
    assert p["proposed_changes"] == ["PCR-8501", "PCR-8503", "PCR-8505"] and "questions" not in json.dumps(p).lower().replace(
        "questions_the_catalogue", "")
    assert get(client, "/products/PRD-9999", 404)["applied"] is False


def test_the_dependency_read_gives_what_refers_to_a_clause_a_section_and_a_factor(client):
    x = get(client, "/references/SEC-8303-4.1")
    assert [r["item_id"] for r in x["items_that_refer_to_it"]] == ["DEP-8421", "DEP-8424", "DEP-8427"]
    assert [r["item_id"] for r in x["items_that_refer_to_its_section_as_a_whole"]] == ["DEP-8425"]
    assert x["counts"] == {"items_that_refer_to_it": 3, "that_quote_it": 3, "that_rely_on_it": 0, "items_of_the_product_that_do_not": 7}
    x = get(client, "/references/SEC-8303-2.1")
    assert [r["item_id"] for r in x["items_that_refer_to_it"]] == ["DEP-8422", "DEP-8423", "DEP-8424", "DEP-8426", "DEP-8428"]
    assert x["counts"]["that_rely_on_it"] == 3
    x = get(client, "/references/SEC-8303-5.3")
    assert x["items_that_refer_to_it"] == [] and x["items_that_refer_to_its_section_as_a_whole"] == []
    assert x["sentence"] == ("No item of the catalogue refers to SEC-8303-5.3 (Governing law). A change to it changes the wording "
                             "itself only.")
    x = get(client, "/references/FAC-8301-1")
    assert [r["item_id"] for r in x["items_that_refer_to_it"]] == ["DEP-8402", "DEP-8404", "DEP-8405", "DEP-8406"]
    assert x["wording_clauses_that_name_it"][0]["section_id"] == "SEC-8301-4.2"
    assert x["wording_clauses_that_name_it"][0]["items_that_refer_to_this_clause"] == ["DEP-8403", "DEP-8404"]
    x = get(client, "/references/SEC-8302-1")
    assert [r["item_id"] for r in x["items_that_refer_to_it"]] == ["DEP-8412", "DEP-8413", "DEP-8414", "DEP-8415", "DEP-8416"]
    assert "DEP-8416" in [r["item_id"] for r in x["items_that_refer_to_a_clause_of_it"]]
    assert "SEC-8303-4.1" in get(client, "/references/SEC-9999-1", 404)["detail"]


def test_a_search_matches_any_word_lists_everything_when_empty_and_says_when_it_is_silent(client):
    x = get(client, "/catalogue/search", text="flood exclusion")
    assert x["words_used"] == ["flood", "exclusion"] and "SEC-8303-2.1" in [r["id"] for r in x["items"]]
    assert {r["product_id"] for r in get(client, "/catalogue/search", text="glass")["items"]} == {"PRD-8301"}
    assert get(client, "/catalogue/search")["count"] == 62 + 18 + 29
    x = get(client, "/catalogue/search", text="earthquake")
    assert x["count"] == 0 and "silent" in x["note"]


def test_the_list_of_proposed_changes_is_whole_and_holds_no_answer(client):
    doc = get(client, "/proposed-changes")
    assert [c["change_id"] for c in doc["items"]] == [f"PCR-850{n}" for n in range(1, 7)]
    assert all(c["status"] == "proposed" and c["text"] and "impact" not in c for c in doc["items"])
    assert [c["received"] for c in doc["items"]] == ["2026-11-20", "2026-11-21", "2026-11-22", "2026-11-23", "2026-11-24", "2026-11-25"]
    says("20 Nov 2026", "25 Nov 2026")


def test_pcr_8501_raising_a_deductible_touches_five_items_and_four_quote_the_figure(client):
    x = impact(client, 8501)
    assert touched(x) == ["DEP-8421", "DEP-8422", "DEP-8424", "DEP-8425", "DEP-8427"]
    assert x["items_that_quote_the_current_figure"] == ["DEP-8421", "DEP-8422", "DEP-8424", "DEP-8427"]
    assert x["items_that_rely_on_what_is_changed"] == []
    assert [i["item_id"] for i in x["items_of_the_product_not_touched"]] == ["DEP-8423", "DEP-8426", "DEP-8428", "DEP-8429", "DEP-8430"]
    assert [(q["item_id"], q["cannot_say"][:40]) for q in x["what_the_catalogue_cannot_say"]] == [
        ("DEP-8422", "What the rates would be with other level")]
    filing = next(r for r in x["items_touched"] if r["item_id"] == "DEP-8425")
    assert "at least 30 days" in filing["on_a_change"] and filing["references"][0]["relation"] == "is_filed"
    assert x["counts"] == {"items_touched": 5, "items_that_quote_the_current_figure": 4, "items_that_rely_on_what_is_changed": 0,
                           "items_of_the_product_not_touched": 5, "questions_the_catalogue_cannot_answer": 1}


def test_pcr_8502_adding_a_peril_touches_five_items_and_the_new_term_is_named_for_another_product_only(client):
    x = impact(client, 8502)
    assert touched(x) == ["DEP-8412", "DEP-8413", "DEP-8414", "DEP-8415", "DEP-8416"]
    assert [i["item_id"] for i in x["items_of_the_product_not_touched"]] == ["DEP-8411"]
    term = x["the_new_term_in_the_catalogue"]
    assert term["named_in_this_product"] == [] and term["named_in_other_products"] == ["SEC-8301-1.4", "SEC-8301-3.2"]
    assert [q["item_id"] for q in x["what_the_catalogue_cannot_say"]] == ["DEP-8412", "DEP-8413", "DEP-8416", None]
    assert x["counts"]["questions_the_catalogue_cannot_answer"] == 4 and x["items_that_rely_on_what_is_changed"] == []


def test_pcr_8503_removing_the_flood_exclusion_meets_three_items_that_rely_on_it_the_treaty_among_them(client):
    x = impact(client, 8503)
    assert touched(x) == ["DEP-8422", "DEP-8423", "DEP-8424", "DEP-8425", "DEP-8426", "DEP-8428"]
    assert x["items_that_rely_on_what_is_changed"] == ["DEP-8422", "DEP-8423", "DEP-8426"]
    treaty = next(r for r in x["items_touched"] if r["item_id"] == "DEP-8426")
    assert treaty["kind"] == "reinsurance_treaty" and treaty["owner"] == "Marguerite Tolland, reinsurance manager"
    assert "on the footing that flood is excluded" in treaty["references"][0]["says"]
    assert [q["item_id"] for q in x["what_the_catalogue_cannot_say"]] == ["DEP-8422", "DEP-8426", "DEP-8428"]
    assert "3 items rely on what is changed staying as it is: DEP-8422, DEP-8423, DEP-8426." in x["sentence"]


def test_pcr_8504_a_shorter_waiting_period_touches_five_items_and_four_quote_300_days(client):
    x = impact(client, 8504)
    assert touched(x) == ["DEP-8431", "DEP-8432", "DEP-8433", "DEP-8434", "DEP-8435"]
    assert x["items_that_quote_the_current_figure"] == ["DEP-8431", "DEP-8432", "DEP-8433", "DEP-8434"]
    assert x["items_that_rely_on_what_is_changed"] == ["DEP-8432"]
    assert [i["item_id"] for i in x["items_of_the_product_not_touched"]] == ["DEP-8436", "DEP-8437"]
    assert [q["item_id"] for q in x["what_the_catalogue_cannot_say"]] == ["DEP-8432"]


def test_pcr_8505_touches_nothing_but_the_wording(client):
    x = impact(client, 8505)
    assert x["items_touched"] == [] and x["what_the_catalogue_cannot_say"] == [] and len(x["items_of_the_product_not_touched"]) == 10
    assert x["sentence"] == ("PCR-8505 touches the wording TMI-COM-03 itself and nothing else: no item of the catalogue refers to "
                             "what it changes.")
    says("touches the wording TMI-COM-03 itself and nothing else")


def test_pcr_8506_the_catalogue_cannot_say_what_the_change_does_to_the_filed_rates(client):
    x = impact(client, 8506)
    assert touched(x) == ["DEP-8402", "DEP-8404", "DEP-8405", "DEP-8406"]
    assert x["items_that_quote_the_current_figure"] == ["DEP-8402", "DEP-8404", "DEP-8406"]
    cannot = x["what_the_catalogue_cannot_say"]
    assert [q["item_id"] for q in cannot] == ["DEP-8402", "DEP-8405", None]
    assert cannot[1]["cannot_say"].startswith("Whether the filed rates must be filed again, and what the change does to them.")
    assert cannot[2]["cannot_say"].startswith("Whether SEC-8301-4.2 changes as well.")
    same = x["wording_clauses_that_name_the_same_thing"]
    assert [c["section_id"] for c in same] == ["SEC-8301-4.2"] and same[0]["items_that_refer_to_this_clause"] == ["DEP-8403", "DEP-8404"]
    assert [i["item_id"] for i in x["items_of_the_product_not_touched"]] == ["DEP-8401", "DEP-8403"]


# ---------------------------------------------------------------- pricing
def test_the_pricing_method_has_eight_rules_and_the_assumptions_of_each_product(client):
    doc = get(client, "/pricing-method")
    assert [r["rule_id"] for r in doc["rules"]] == [f"PM-{n}" for n in range(1, 9)]
    assert doc["accident_years_held"] == [2023, 2024, 2025] and doc["rating_year"] == 2027
    assert (doc["claims_for_full_credibility"], doc["claims_needed_to_rely_on_a_figure"]) == (1000, 250)
    got = {p: (a["claims_trend_percent"], a["expense_ratio_percent"], a["target_loss_ratio_percent_when_none_is_given"])
           for p, a in doc["default_assumptions_by_product"].items()}
    assert got == {"private_motor": (5.0, 25.0, 70.0), "home": (4.0, 30.0, 65.0), "commercial_property": (4.0, 28.0, 67.0),
                   "motor_fleet": (6.0, 22.0, 73.0)}


def test_the_segments_are_listed_whole_with_every_ratio_worked_out(client):
    doc = get(client, "/segments")
    rows = {s["segment_id"]: s for s in doc["items"]}
    assert list(rows) == [f"SEG-860{n}" for n in range(1, 7)]
    got = {k: (s["totals"]["loss_ratio_percent"], s["totals"]["claims"], s["credibility"]["credibility"], s["credibility"]["reliable"])
           for k, s in rows.items()}
    assert got == {"SEG-8601": (68.15, 3730, 1.0, True), "SEG-8602": (88.6, 675, 0.82, True), "SEG-8603": (47.73, 1905, 1.0, True),
                   "SEG-8604": (92.71, 46, 0.21, False), "SEG-8605": (63.68, 300, 0.55, True), "SEG-8606": (72.63, 250, 0.5, True)}
    for k, (ratio, claims, z, _) in got.items():
        row = next(line for line in SECTION.splitlines() if line.startswith(f"| {k} "))
        assert f"{ratio:.2f}" in row and f"{claims:,}" in row and f"{z:.2f}" in row, k


def test_pq_8701_the_loss_ratio_of_a_segment_by_year_and_together(client):
    x = get(client, "/segments/SEG-8601/experience")
    assert [r["loss_ratio_percent"] for r in x["by_year"]] == [65.0, 68.0, 71.04]
    t = x["totals"]
    assert (t["earned_premium"], t["incurred_claims"], t["loss_ratio_percent"]) == (13500000.0, 9200000.0, 68.15)
    assert t["working"] == "USD 9,200,000.00 / USD 13,500,000.00 = 68.15 percent (PM-1)."
    assert x["saved"] is False
    says("65.00, 68.00 and 71.04", "9,200,000.00 / 13,500,000.00 = 68.15 percent")
    two = get(client, "/segments/SEG-8601/experience", years_to_read="2024-2025")
    assert two["years_read"] == [2024, 2025] and two["totals"]["loss_ratio_percent"] == 69.57


def test_pq_8702_the_premium_change_that_holds_70_percent_with_every_assumption_named(client):
    x = change(client, 8601, target_loss_ratio_percent=70)
    assert {a["name"]: a["value"] for a in x["assumptions"]} == {
        "target_loss_ratio_percent": 70.0, "expense_ratio_percent": 25.0, "claims_trend_percent_a_year": 5.0,
        "profit_margin_percent": 5.0, "years_read": [2023, 2024, 2025], "rating_year": 2027, "trend_years": 3.0}
    assert x["assumptions"][0]["source"] == "given in the question" and "default" in x["assumptions"][2]["source"]
    assert (x["trend_factor"], x["trended_incurred_claims"], x["trended_loss_ratio_percent"]) == (1.157625, 10650150.0, 78.89)
    assert (x["premium_change_on_these_figures_percent"], x["premium_change_to_rely_on_percent"]) == (12.7, 12.7)
    assert x["premium_needed_for_the_same_exposure"] == 15214500.0 and x["reliable"] is True and x["target_already_met"] is False
    assert x["combined_ratio_at_the_target_percent"] == 95.0 and len(x["working"]) == 6 and len(x["sensitivity"]) == 9
    grid = {(g["target_loss_ratio_percent"], g["claims_trend_percent_a_year"]): g["premium_change_needed_percent"] for g in x["sensitivity"]}
    assert (grid[(65.0, 5.0)], grid[(70.0, 5.0)], grid[(75.0, 5.0)], grid[(70.0, 3.0)], grid[(70.0, 7.0)], grid[(75.0, 3.0)]) == (
        21.37, 12.7, 5.19, 6.38, 19.26, 0.0)
    says("1.157625", "10,650,150.00", "78.89 percent", "12.70 percent", "15,214,500.00", "21.37", "5.19", "6.38", "19.26")
    assert change(client, 8601) == x | {"assumptions": change(client, 8601)["assumptions"]}  # the default target is 70 as well
    assert "worked out under PM-4" in change(client, 8601)["assumptions"][0]["source"]


def test_pq_8703_a_thin_segment_is_not_reliable_and_the_answer_says_why(client):
    x = change(client, 8604)
    cred = x["credibility"]
    assert (cred["claims_in_the_years_read"], cred["claims_needed_to_rely_on_a_figure"], cred["credibility"], cred["reliable"],
            cred["claims_short_of_the_threshold"]) == (46, 250, 0.21, False, 204)
    assert x["reliable"] is False and x["premium_change_to_rely_on_percent"] is None
    assert (x["experience"]["loss_ratio_percent"], x["trended_loss_ratio_percent"], x["premium_change_on_these_figures_percent"]) == (
        92.71, 104.28, 60.44)
    assert x["sentence"].startswith("SEG-8604 is too thin to rely on: 46 claims against the 250 the method needs, credibility 0.21")
    assert get(client, "/segments/SEG-8604/credibility")["sentence"] == cred["sentence"]
    assert [r["loss_ratio_percent"] for r in get(client, "/segments/SEG-8604/experience")["by_year"]] == [40.0, 193.75, 44.12]
    says("46 claims", "204 short", "0.21", "92.71", "104.28", "60.44", "40.00, 193.75 and 44.12")


def test_pq_8704_a_target_that_is_already_met_needs_no_change(client):
    x = change(client, 8603, target_loss_ratio_percent=60)
    assert (x["trended_loss_ratio_percent"], x["target_already_met"], x["points_below_the_target"]) == (53.69, True, 6.31)
    assert (x["premium_change_on_these_figures_percent"], x["premium_change_to_rely_on_percent"]) == (0.0, 0.0)
    assert x["premium_needed_for_the_same_exposure"] == x["earned_premium_of_the_years_read"] == 7500000.0
    assert "No premium change is needed (PM-6)" in x["sentence"]
    says("47.73", "1.124864", "53.69", "6.31 points")


def test_pq_8705_a_year_that_is_not_held_is_refused_and_no_figure_is_estimated(client):
    for path in ("experience", "credibility", "premium-change"):
        x = get(client, f"/segments/SEG-8601/{path}", 409, years_to_read="2026")
        assert x["applied"] is False and "2026 is not held" in x["detail"] and "no figure is estimated" in x["detail"]
    assert "2022 is not held" in get(client, "/segments/SEG-8601/experience", 409, years_to_read="2022-2023")["detail"]
    x = get(client, "/segments/SEG-8699/experience", 404)
    assert "not split by fuel type" in x["detail"]
    assert "not split by fuel type" in get(client, "/segments")["how_the_experience_is_split"]


def test_pq_8706_a_segment_exactly_on_the_claims_threshold_is_reliable(client):
    x = change(client, 8606)
    cred = x["credibility"]
    assert (cred["claims_in_the_years_read"], cred["credibility"], cred["reliable"], cred["claims_short_of_the_threshold"]) == (
        250, 0.5, True, 0)
    assert (x["target_loss_ratio_percent"], x["trend_factor"], x["trended_incurred_claims"], x["trended_loss_ratio_percent"],
            x["premium_change_to_rely_on_percent"], x["premium_needed_for_the_same_exposure"]) == (
        73.0, 1.191016, 4930806.24, 86.51, 18.5, 6754529.1)
    says("250 claims", "1.191016", "4,930,806.24", "86.51", "18.50 percent", "6,754,529.10")


def test_pq_8707_the_users_own_assumptions_are_used_and_named_as_given(client):
    x = change(client, 8602, target_loss_ratio_percent=65, claims_trend_percent=7)
    src = {a["name"]: a["source"] for a in x["assumptions"]}
    assert src["target_loss_ratio_percent"] == src["claims_trend_percent_a_year"] == "given in the question"
    assert src["expense_ratio_percent"] == "the method's default for this product"
    assert (x["trend_factor"], x["trended_incurred_claims"], x["trended_loss_ratio_percent"], x["premium_change_to_rely_on_percent"],
            x["premium_needed_for_the_same_exposure"], x["credibility"]["credibility"]) == (
        1.225043, 2094823.53, 108.54, 66.98, 3222805.43, 0.82)
    says("88.60", "1.225043", "2,094,823.53", "108.54", "66.98 percent", "3,222,805.43")
    over = change(client, 8602, target_loss_ratio_percent=80, expense_ratio_percent=25)
    assert over["combined_ratio_at_the_target_percent"] == 105.0 and over["target_and_expenses_fit_within_the_premium"] is False


def test_a_value_outside_what_the_method_works_with_is_refused(client):
    for params in ({"target_loss_ratio_percent": 5}, {"claims_trend_percent": 40}, {"expense_ratio_percent": 90}):
        x = get(client, "/segments/SEG-8601/premium-change", 409, **params)
        assert "outside what the method works with" in x["detail"] and "Nothing was worked out" in x["detail"]


# ---------------------------------------------------------------- the exposure warehouse
def test_the_warehouse_guide_says_what_is_held_and_what_is_not(client):
    doc = get(client, "/warehouse")
    assert doc["as_at"] == "2026-10-31" and doc["rows_held"] == 39
    assert [f["field"] for f in doc["fields"]] == ["product", "region", "construction_class", "vehicle_class", "sum_insured_band"]
    assert list(doc["measures"]) == ["policies_in_force", "total_sum_insured", "annual_premium", "average_sum_insured"]
    assert any("flood zone" in x for x in doc["not_held"])
    assert doc["totals"] == {"policies_in_force": 9757, "total_sum_insured": 815500000.0, "annual_premium": 13413450.0}
    assert doc["by_product"]["home"] == {"policies_in_force": 1510, "total_sum_insured": 315200000.0, "annual_premium": 2679200.0}
    says("31 Oct 2026", "9,757", "815,500,000.00", "13,413,450.00")


def test_exq_8801_commercial_property_by_construction_class_with_the_query_as_run(client):
    x = query(client, measure="total_sum_insured", group_by="construction_class", product="commercial_property")
    assert [(r["construction_class"], r["value"], r["share_of_the_total_percent"]) for r in x["rows"]] == [
        ("A", 160600000.0, 51.07), ("B", 90000000.0, 28.62), ("C", 63900000.0, 20.32)]
    assert x["total"] == 314500000.0 and x["saved"] is False
    assert x["query"] == {"measure": "total_sum_insured", "group_by": ["construction_class"],
                          "filters": {"product": ["commercial_property"]}, "as_at": "2026-10-31"}
    assert x["query_in_words"] == ("Total sum insured of the policies in force on 31 Oct 2026, where product is commercial_property, "
                                   "grouped by construction_class.")
    says(x["query_in_words"], "160,600,000.00", "90,000,000.00", "63,900,000.00", "314,500,000.00", "51.07", "28.62", "20.32")


def test_exq_8802_a_count_with_two_filters_read_from_plain_words(client):
    x = query(client, measure="Policies in force", product="Home", region="tallowby")
    assert x["total"] == 360 and x["rows"] == [] and x["warehouse_rows_read"] == 3 and x["unit"] == "policies"
    assert x["query_in_words"] == "Number of policies in force on 31 Oct 2026, where product is home; region is Tallowby, as one figure."
    says(x["query_in_words"], "360")


def test_exq_8803_class_c_is_over_its_limit(client):
    x = limit(client, 2)
    assert (x["measured"], x["limit"], x["result"], x["over_by_points"], x["over_by_amount"], x["amount"], x["of_a_total_of"],
            x["amount_at_the_limit"]) == (20.32, 15.0, "over", 5.32, 16725000.0, 63900000.0, 314500000.0, 47175000.0)
    assert len(x["queries_run"]) == 2 and x["exactly_on_the_limit"] is False
    says("20.32 percent", "5.32 points", "16,725,000.00", "47,175,000.00")


def test_exq_8804_the_saltmarsh_coast_is_exactly_on_its_limit_and_so_within(client):
    x = limit(client, 3)
    assert (x["measured"], x["limit"], x["result"], x["exactly_on_the_limit"], x["over_by"], x["room_left"]) == (
        60000000.0, 60000000.0, "within", True, 0.0, 0.0)
    assert x["sentence"] == ("LIM-3: USD 60,000,000.00 against a limit of USD 60,000,000.00. Exactly on the limit, which is within "
                             "it: no room is left.")
    q = query(client, measure="total_sum_insured", group_by="product", region="Saltmarsh Coast", product="home,commercial_property")
    assert [(r["product"], r["value"]) for r in q["rows"]] == [("home", 24000000.0), ("commercial_property", 36000000.0)]
    says("60,000,000.00", "24,000,000.00", "36,000,000.00")


def test_exq_8805_a_field_the_warehouse_does_not_hold_is_refused_and_nothing_is_estimated(client):
    for params in ({"group_by": "flood_zone"}, {"other_field": "flood_zone"}, {"flood_zone": "3"}, {"other_field": "flood zone=3"}):
        x = query(client, 409, measure="total_sum_insured", **params)
        assert x["applied"] is False and "does not hold the flood zone of a location" in x["detail"], params
        assert "no figure is estimated" in x["detail"] and "product, region, construction_class, vehicle_class, sum_insured_band" in x["detail"]
    assert "holds no field called colour" in query(client, 409, measure="total_sum_insured", group_by="colour")["detail"]
    assert "claims is not a measure" in query(client, 409, measure="claims")["detail"]
    assert "not as other_field" in query(client, 409, measure="total_sum_insured", other_field="region")["detail"]
    assert "at most two fields" in query(client, 409, measure="total_sum_insured", group_by="product,region,sum_insured_band")["detail"]


def test_exq_8806_property_in_marlow_reach_has_two_readings_and_the_system_names_them(client):
    x = query(client, 409, measure="total_sum_insured", product="property", region="Marlow Reach")
    assert "can be read two ways" in x["detail"] and "home,commercial_property" in x["detail"]
    both = query(client, measure="total_sum_insured", group_by="product", product="home,commercial_property", region="Marlow Reach")
    assert both["total"] == 181900000.0
    assert [(r["product"], r["value"], r["share_of_the_total_percent"]) for r in both["rows"]] == [
        ("home", 93300000.0, 51.29), ("commercial_property", 88600000.0, 48.71)]
    one = query(client, measure="total_sum_insured", product="commercial_property", region="Marlow Reach")
    assert one["total"] == 88600000.0
    assert query(client, measure="policies_in_force", product="home,commercial_property", region="Marlow Reach")["total"] == 524
    says("181,900,000.00", "88,600,000.00", "93,300,000.00", "524")


def test_exq_8807_the_largest_region_is_within_the_limit_for_one_region(client):
    x = limit(client, 1)
    assert (x["measured_for"], x["measured"], x["limit"], x["result"], x["room_left_points"], x["room_left_amount"], x["amount"],
            x["of_a_total_of"], x["amount_at_the_limit"]) == (
        "Port Ilvane", 43.8, 45.0, "within", 1.2, 7565000.0, 275800000.0, 629700000.0, 283365000.0)
    assert [(v["is"], v["amount"], v["share_percent"]) for v in x["every_value_measured"]] == [
        ("Port Ilvane", 275800000.0, 43.8), ("Marlow Reach", 181900000.0, 28.89), ("Tallowby", 112000000.0, 17.79),
        ("Saltmarsh Coast", 60000000.0, 9.53)]
    says("275,800,000.00", "629,700,000.00", "43.80 percent", "1.20 points", "7,565,000.00", "28.89", "17.79", "9.53")


def test_exq_8808_no_rows_means_zero_which_is_not_the_same_as_not_held(client):
    x = query(client, measure="policies_in_force", product="commercial_property", construction_class="class C",
              sum_insured_band="over 2,500,000")
    assert x["total"] == 0 and x["warehouse_rows_read"] == 0 and "The answer is zero" in x["notes"][0]
    assert x["query"]["filters"] == {"product": ["commercial_property"], "construction_class": ["C"], "sum_insured_band": ["over_2500000"]}
    assert query(client, measure="total_sum_insured", product="commercial_property", construction_class="C",
                 sum_insured_band="1000001_to_2500000")["total"] == 0.0
    says("The answer is zero")


def test_an_average_is_worked_from_its_parts_and_a_missing_class_is_grouped_as_not_applicable(client):
    x = query(client, measure="average_sum_insured", group_by="product")
    assert [(r["product"], r["value"]) for r in x["rows"]] == [("home", 208741.72), ("commercial_property", 964723.93),
                                                               ("private_motor", 17439.49), ("motor_fleet", 688732.39)]
    assert x["total"] == 83581.02 and x["total_worked_from"] == {"total_sum_insured": 815500000.0, "policies_in_force": 9757}
    y = query(client, measure="policies_in_force", group_by="construction_class")
    assert [(r["construction_class"], r["value"]) for r in y["rows"]] == [("A", 1065), ("B", 511), ("C", 260), ("not_applicable", 7921)]
    assert any("not_applicable" in n for n in y["notes"])


def test_the_six_limits_one_over_one_exactly_on_and_the_rest_within(client):
    doc = get(client, "/concentration-limits")
    assert [(x["limit_id"], x["unit"], x["limit"]) for x in doc["items"]] == [
        ("LIM-1", "percent", 45.0), ("LIM-2", "percent", 15.0), ("LIM-3", "USD", 60000000.0), ("LIM-4", "percent", 25.0),
        ("LIM-5", "percent", 30.0), ("LIM-6", "percent", 50.0)]
    m = get(client, "/concentration-limits/measure")
    assert (m["limits_over"], m["limits_exactly_on"]) == (["LIM-2"], ["LIM-3"]) and m["as_at"] == "2026-10-31"
    assert m["limits_within"] == ["LIM-1", "LIM-3", "LIM-4", "LIM-5", "LIM-6"]
    got = {x["limit_id"]: x["measured"] for x in m["items"]}
    assert got == {"LIM-1": 43.8, "LIM-2": 20.32, "LIM-3": 60000000.0, "LIM-4": 18.44, "LIM-5": 29.04, "LIM-6": 40.82}
    for limit_id, measured in got.items():
        row = next(line for line in SECTION.splitlines() if line.startswith(f"| {limit_id} "))
        assert money(measured) in row, limit_id
    assert (m["items"][4]["room_left_points"], m["items"][4]["room_left_amount"]) == (0.96, 470000.0)
    assert m["items"][5]["measured_for"] == "private_motor"
    assert get(client, "/concentration-limits/measure", 404, limit_id="LIM-9")["applied"] is False


# ---------------------------------------------------------------- the one draft, and what a read never returns
def test_a_question_for_a_person_is_a_draft_that_changes_nothing_else(client, store):
    before = {k: json.dumps(v, sort_keys=True) for k, v in store.data.items()}
    saved = post(client, "/questions", QUESTION)
    assert saved["applied"] is True and saved["kind"] == "draft"
    note = saved["draft"]
    assert (note["question_id"], note["version"], note["about"], note["drafted_by"]) == ("QN-8901", 1, "PCR-8503", "agent")
    assert post(client, "/questions", {**QUESTION, "about": "", "topic": "pricing"})["draft"]["question_id"] == "QN-8902"
    changed = [k for k, v in store.data.items() if json.dumps(v, sort_keys=True) != before[k]]
    assert changed == ["pf_questions"]
    assert [q["question_id"] for q in get(client, "/questions")["items"]] == ["QN-8901", "QN-8902"]
    assert [q["question_id"] for q in get(client, "/questions", about="pcr-8503")["items"]] == ["QN-8901"]


def test_a_read_of_a_record_never_returns_a_saved_question(client):
    post(client, "/questions", QUESTION)
    post(client, "/questions", {**QUESTION, "topic": "pricing", "about": "SEG-8604"})
    post(client, "/questions", {**QUESTION, "topic": "portfolio_exposure", "about": "LIM-2"})
    record = get(client, "/proposed-changes/PCR-8503")
    assert record["questions_on_file"] == 2 - 1 and QUESTION["question"] not in json.dumps(record)
    for path in ("/proposed-changes", "/products/PRD-8303", "/references/SEC-8303-2.1", "/segments", "/segments/SEG-8604/experience",
                 "/concentration-limits/measure", "/warehouse"):
        assert QUESTION["question"] not in json.dumps(get(client, path)), path
    assert record["status"] == "proposed"


def test_a_question_about_an_id_the_system_does_not_hold_is_refused_and_nothing_is_saved(client, store):
    x = post(client, "/questions", {**QUESTION, "about": "CLM-4001"}, 409)
    assert x["applied"] is False and "Nothing was saved" in x["detail"]
    assert post(client, "/questions", {**QUESTION, "topic": "claims"}, 422)["applied"] is False
    assert post(client, "/questions", {"topic": "pricing"}, 422)["applied"] is False
    assert store.data["pf_questions"] == {}
    assert post(client, "/questions", {**QUESTION, "about": "SEC-8303-2.1"})["draft"]["about"] == "SEC-8303-2.1"


def test_the_portfolio_reset_puts_back_its_own_notes_and_leaves_the_other_systems_alone(client, store):
    post(client, "/questions", QUESTION)
    client.post("/claims/claims/CLM-4001/triage", headers=H, json={"rule_id": "HG-3", "track": "fast track", "team": "fast-track team",
                                                                  "severity": "low", "reason": "Estimate under 2,500."})
    assert client.get("/admin/state", headers=H).json()["changed_by"] == {"claims": ["claims"], "portfolio": ["pf_questions"]}
    assert client.get("/admin/state", headers=H).json()["counts"]["portfolio_questions_saved_for_a_person"] == 1
    assert client.post("/admin/reset/portfolio", headers=H).json()["put_back"] == ["pf_questions"]
    assert store.data["pf_questions"] == {} and len(store.data["claims"]["CLM-4001"]["triage_drafts"]) == 1
    assert post(client, "/questions", QUESTION)["draft"]["question_id"] == "QN-8901"
    counts = client.get("/admin/state", headers=H).json()["counts"]
    assert counts["product_changes_proposed"] == 6
    assert "product changes proposed" in client.get("/").text
