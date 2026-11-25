"""The workflow form of five agents does its comparisons in code, and that code agrees with this retailer.

Each folder ../retail/agents/<agent>/workflow/ holds step.py: the logic of the Code step, plain Python. These tests
load each step.py by its path, build its inputs from the seed of this service at retailer date 2026-11-24, in the
shape the tools return them, and hold the result to two things: the answer SCENARIOS.md gives, and the seed's own
answer.

The module is skipped when the workflow folders are not next to this copy of the retailer.
"""
import importlib.util
import json
import re
from datetime import date
from pathlib import Path

import pytest

from conftest import TODAY
from retailer import seed_catalogue, seed_people, seed_stock, seed_tills

AGENTS = Path(__file__).resolve().parents[2] / "retail" / "agents"
FORMS = ["roster-check", "inventory-forecasting", "shrink-analysis", "refund-and-discount-audit", "product-data-check"]
if not all((AGENTS / name / "workflow" / "step.py").is_file() for name in FORMS):
    pytest.skip("the workflow folders are not next to this copy of the retailer", allow_module_level=True)

DAY = date.fromisoformat(TODAY)
PERIOD = "2026-10"
SCENARIOS = (Path(__file__).resolve().parents[1] / "SCENARIOS.md").read_text(encoding="utf-8")


def step(agent: str):
    path = AGENTS / agent / "workflow" / "step.py"
    spec = importlib.util.spec_from_file_location("workflow_step_" + agent.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def section(heading: str) -> str:
    """One section of SCENARIOS.md, from its heading to the next heading of the same level."""
    start = SCENARIOS.index("## " + heading)
    end = SCENARIOS.find("\n## ", start + 1)
    return SCENARIOS[start:end if end > 0 else len(SCENARIOS)]


@pytest.mark.parametrize("agent", FORMS)
def test_a_step_file_uses_the_standard_library_only_and_has_unix_line_endings(agent):
    raw = (AGENTS / agent / "workflow" / "step.py").read_bytes()
    assert b"\r" not in raw
    imported = set(re.findall(r"^(?:import|from) (\w+)", raw.decode("utf-8"), re.M))
    assert imported <= {"json", "datetime", "fractions", "sys", "re"}, imported


# ---------------------------------------------------------------- roster check

# The breaches of the draft rosters section of SCENARIOS.md: rule, colleague, shift, day.
ROSTER_BREACHES = {
    "RS-261130-R014": [("WT-2", "C-01407", "SH-R014-19", "wednesday"), ("WT-4", "C-01409", "SH-R014-39", "friday")],
    "RS-261130-R022": [],
    "RS-261130-R047": [("SR-1", "", "", "sunday"), ("WT-7", "C-04712", "SH-R047-46", "saturday")],
    "RS-261130-R063": [],
    "RS-261130-S103": [("SR-2", "C-10301", "SH-S103-25", "thursday"), ("WT-3", "C-10306", "", "")],
    "RS-261130-S106": [],
}


def _key(breach: dict) -> tuple:
    return breach["rule"], breach["colleague_id"], breach["shift_id"], breach["day"]


def test_roster_check_finds_the_breaches_of_scenarios_and_of_the_seed():
    check_roster = step("roster-check").check_roster
    rosters = seed_people.build_people(DAY)["draft_rosters"]
    assert sorted(rosters) == sorted(ROSTER_BREACHES)
    text = section("Draft rosters")
    for roster_id, roster in rosters.items():
        got = check_roster(roster, seed_people.RULES)
        mine = sorted(_key(b) for b in got["breaches"])
        assert mine == sorted(ROSTER_BREACHES[roster_id]), roster_id
        assert mine == sorted(_key(b) for b in seed_people.find_breaches(roster)), roster_id
        assert roster_id in text
        for rule, colleague, shift, _ in ROSTER_BREACHES[roster_id]:
            assert rule in text and colleague in text and shift in text
        assert got["breach_count"] == len(mine)
        if not mine:
            assert got["summary"] == "No breach. The roster keeps every rule."
        # the limits written in the code are the ones the rules give
        assert check_roster(roster)["breaches"] == got["breaches"], roster_id


def test_roster_check_reads_its_limits_from_the_rules():
    check_roster = step("roster-check").check_roster
    rosters = seed_people.build_people(DAY)["draft_rosters"]
    tight = json.loads(json.dumps(seed_people.RULES))
    for rule in tight["rules"]:
        if rule["rule"] == "WT-3":
            assert rule["limit"] == 48
            rule["limit"] = 47
    added = 0
    for roster in rosters.values():
        before = [_key(b) for b in check_roster(roster, seed_people.RULES)["breaches"]]
        after = [_key(b) for b in check_roster(roster, tight)["breaches"]]
        assert all(b in after for b in before)
        new = [b for b in after if b not in before]
        assert all(b[0] == "WT-3" for b in new)
        added += len(new)
    assert added > 0, "lowering the weekly limit in the rules added no breach, so the limit is not read from the rules"


# ---------------------------------------------------------------- inventory forecasting

PLAN = {"AG-4408": ("SUP-303", 75, 750), "CH-5502": ("SUP-301", 87, 1740), "CH-5505": ("SUP-301", 73, 876),
        "FP-5801": ("SUP-304", 75, 900), "FP-5802": ("SUP-304", 145, 1160)}
OVERSTOCKED = ["DR-5904", "FZ-5604", "HH-6105"]


def test_inventory_forecasting_makes_the_plan_of_scenarios_and_agrees_with_the_seed_on_every_line():
    levels_raw, terms_raw = seed_stock._levels(), seed_stock._terms(DAY)
    stores = sorted(next(iter(levels_raw.values()))["by_store"])
    levels = {"retailer_date": TODAY, "items": [
        {"sku": x["sku"], "name": x["name"], "category": x["category"],
         "on_hand": sum(x["by_store"][s]["on_hand"] for s in stores),
         "units_sold_last_four_weeks": sum(sum(x["by_store"][s]["weekly_sales"][-4:]) for s in stores)}
        for x in levels_raw.values()]}
    terms = {"retailer_date": TODAY, "items": [dict(t) for t in terms_raw.values()]}
    rules = {"target_cover_days": seed_stock.TARGET_COVER_DAYS, "overstock_days": seed_stock.OVERSTOCK_DAYS}
    got = step("inventory-forecasting").make_plan(levels, terms, rules)

    assert {x["sku"]: (x["supplier_id"], x["cases"]) for x in got["plan"]["lines"]} == {k: v[:2] for k, v in PLAN.items()}
    assert got["plan"]["overstocked"] == OVERSTOCKED == seed_stock.OVERSTOCKED
    text = section("Replenishment")
    for sku in list(PLAN) + OVERSTOCKED:
        assert sku in text

    assert len(got["positions"]) == 60
    by_sku = {p["sku"]: p for p in got["positions"]}
    for p in got["positions"]:
        s = seed_stock.line_position(levels_raw[p["sku"]], terms_raw[p["sku"]], DAY)
        mine = (p["runs_out"], p["overstocked"], p["cases"], p["units"], p["days_to_next_delivery"], float(p["days_of_cover"]))
        seed = (s["runs_out"], s["overstocked"], s["cases"], s["units"], s["days_to_next_delivery"], s["days_of_cover"])
        assert mine == seed, p["sku"]
    for sku, (_, cases, units) in PLAN.items():
        assert (by_sku[sku]["cases"], by_sku[sku]["units"]) == (cases, units)

    # the edges SCENARIOS.md names
    assert by_sku["FP-5801"]["units_on_order"] == 360
    assert by_sku["CH-5503"]["runs_out"] is False and by_sku["CH-5503"]["cases"] == 0
    assert by_sku["AG-4410"]["days_of_cover"] == "5.0" and by_sku["AG-4410"]["runs_out"] is False
    assert by_sku["PC-6606"]["days_of_cover"] == "56.0" and by_sku["PC-6606"]["overstocked"] is False


# ---------------------------------------------------------------- shrink analysis

STORES_BEYOND = [("S-106", 2.5), ("S-103", 2.44)]
LINES_BEYOND = [("DR-5905", 6.68), ("HH-6105", 5.81), ("PC-6604", 5.48)]
TILL_FIGURES = {"S-103": "4 refunds (317.97), 5 voids (223.15), 3 discounts (26.54)",
                "S-106": "8 refunds (850.85), 8 voids (489.24), 11 discounts (156.94)"}


def test_shrink_analysis_lists_the_stores_and_lines_of_scenarios_with_the_till_figures():
    analyse = step("shrink-analysis").analyse
    counts = [c for c in seed_stock._counts(DAY).values() if c["period"] == PERIOD]
    by_store = {"period": PERIOD, "items": [{k: v for k, v in c.items() if k != "rows"} for c in counts]}
    by_line = {"period": PERIOD, "items": sorted(seed_stock.loss_by_line(counts).values(), key=lambda r: r["sku"])}
    rows = [r for r in seed_tills.build_tills(DAY)["till_rows"].values() if r["date"].startswith(PERIOD)]
    got = analyse(by_store, by_line, seed_stock.SHRINK_TOLERANCE, {"items": rows})

    assert len(by_store["items"]) == 8 and len(by_line["items"]) == 60 and len(rows) == 180
    assert [(x["site_id"], x["loss_percent"]) for x in got["stores_beyond_tolerance"]] == STORES_BEYOND
    assert [(x["sku"], x["loss_percent"]) for x in got["lines_beyond_tolerance"]] == LINES_BEYOND
    assert "S-102 at 1.33 percent" in got["summary"]
    assert "FP-5806 at 1.40 percent" in got["summary"]
    for x in got["stores_beyond_tolerance"]:
        assert TILL_FIGURES[x["site_id"]] in x["note"]

    text = section("Stock loss")
    for name, _ in STORES_BEYOND + LINES_BEYOND:
        assert name in text
    for figure in ("850.85", "489.24", "156.94", "1.33"):
        assert figure in text

    # figures only: no cashier and no approver leaves the code
    saved = json.dumps(got)
    people = {r["cashier_id"] for r in rows} | {r["approver_id"] for r in rows if r["approver_id"]}
    assert people and not [p for p in people if p in saved]
    assert "cashier" not in saved and "approver" not in saved


def test_shrink_analysis_keeps_a_store_and_a_line_exactly_on_the_tolerance_within_it():
    analyse = step("shrink-analysis").analyse
    store = {"site_id": "S-1", "loss_value": 15.0, "sales_value": 1000.0, "loss_percent": 1.5, "loss_units": 1}
    line = {"sku": "A", "name": "a", "loss_value": 25.0, "sales_value": 1000.0, "loss_percent": 2.5, "loss_units": 1}
    on = analyse({"period": "x", "items": [store]}, {"items": [line]}, seed_stock.SHRINK_TOLERANCE)
    assert on["stores_beyond_tolerance"] == [] and on["lines_beyond_tolerance"] == []
    over = analyse({"period": "x", "items": [dict(store, loss_value=15.01)]}, {"items": [dict(line, loss_value=25.01)]},
                   seed_stock.SHRINK_TOLERANCE)
    assert len(over["stores_beyond_tolerance"]) == 1 and len(over["lines_beyond_tolerance"]) == 1


# ---------------------------------------------------------------- refund and discount audit

def test_refund_and_discount_audit_lists_the_28_rows_of_scenarios_and_of_the_seed():
    audit = step("refund-and-discount-audit").audit
    want = {}
    for m in re.finditer(r"^\| (TR-2610-\d{4}) \|(?:[^|]*\|){7} ([^|]+) \|", section("Refunds, voids and discounts"), re.M):
        want[m.group(1)] = [x.strip() for x in m.group(2).split(",")]
    assert len(want) == 28

    rows = [r for r in seed_tills.build_tills(DAY)["till_rows"].values() if r["date"].startswith(PERIOD)]
    assert len(rows) == 180
    got = audit({"items": rows, "total": len(rows)})
    mine = {x["row_id"]: x["rules"] for x in got["rows"]}
    seed = {r["row_id"]: seed_tills.breaks(r) for r in rows if seed_tills.breaks(r)}
    assert mine == want
    assert mine == seed
    assert got["site_id"] == ""

    times = [rule for rules in mine.values() for rule in rules]
    assert {r: times.count(r) for r in ("TC-1", "TC-2", "TC-3", "TC-4")} == {"TC-1": 9, "TC-2": 7, "TC-3": 8, "TC-4": 6}
    assert "180 rows read. 28 rows are outside the rules, and the rules are broken 30 times" in got["summary"]
    assert "A count of rows is not a finding about anyone." in got["summary"]

    # two rules on one row, and the two rows exactly on a limit
    assert mine["TR-2610-0064"] == ["TC-1", "TC-2"] and mine["TR-2610-0090"] == ["TC-1", "TC-2"]
    assert "TR-2610-0019" not in mine and "TR-2610-0002" not in mine

    # one site at a time
    assert len(audit({"items": rows, "total": len(rows)}, "S-106")["rows"]) == 12
    assert audit({"items": rows, "total": len(rows)}, "R-117")["rows"] == []


def test_refund_and_discount_audit_stops_when_it_was_given_a_part_of_the_period():
    audit = step("refund-and-discount-audit").audit
    rows = [r for r in seed_tills.build_tills(DAY)["till_rows"].values() if r["date"].startswith(PERIOD)]
    with pytest.raises(SystemExit) as stop:
        audit({"items": rows[:100], "total": len(rows)})
    assert "Only 100 of 180 rows" in str(stop.value)


# ---------------------------------------------------------------- product data check

def test_product_data_check_lists_the_ten_findings_of_scenarios_and_of_the_seed():
    compare = step("product-data-check").compare
    want = []
    for m in re.finditer(r"^\| ([A-Z]{2}-\d{4}) \| [^|]+ \| (\w+) \| (\w+) \| ([^|]+) \| ([^|]+) \|", section("Product data check"), re.M):
        listed = "" if m.group(4).strip() == "(nothing)" else m.group(4).strip()
        want.append((m.group(1), m.group(2), m.group(3), listed, m.group(5).strip()))
    assert len(want) == 10

    data = seed_catalogue.build_catalogue(DAY)
    listings = {"items": list(data["catalogue_products"].values())}
    specs = list(data["supplier_specs"].values())
    assert len(listings["items"]) == 60 and len(specs) == 60
    got = compare(listings, specs)
    mine = [(f["sku"], f["attribute"], f["kind"], f["listing_value"], f["specification_value"]) for f in got["findings"]]
    assert sorted(mine) == sorted(want)
    planted = {sku: attribute for sku, (attribute, _) in seed_catalogue.MISMATCHES.items()}
    assert {f["sku"]: f["attribute"] for f in got["findings"]} == planted
    assert got["category"] == ""
    assert sorted(f["sku"] for f in got["findings"] if f["attribute"] == "allergen_statement") == ["AG-4412", "BK-5703", "CH-5506"]

    # one category at a time
    assert len(compare(listings, specs, "ambient_grocery")["findings"]) == 3
    assert len(compare(listings, specs, "bakery")["findings"]) == 1


def test_product_data_check_stops_when_a_specification_was_not_read():
    compare = step("product-data-check").compare
    data = seed_catalogue.build_catalogue(DAY)
    listings = {"items": list(data["catalogue_products"].values())}
    specs = list(data["supplier_specs"].values())
    left_out = specs[-1]["sku"]
    with pytest.raises(SystemExit) as stop:
        compare(listings, specs[:-1])
    assert left_out in str(stop.value) and "Nothing was checked." in str(stop.value)
