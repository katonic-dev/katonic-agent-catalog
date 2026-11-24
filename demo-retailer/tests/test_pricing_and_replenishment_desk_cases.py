"""The pricing and replenishment desk's demo cases are this retailer's own records.

../retail/desks/pricing-and-replenishment/cases.json is written by make_cases.py in the same folder, from
the seed of this service at retailer date 2026-11-24: one price review for each category with a published
competitor price, one replenishment case for each supplier with a line that runs out, and one for a supplier
with nothing to order. These tests fail when the file differs from what the script would write, and when a
case differs from what the service returns for that category or supplier.

The module is skipped when the desk folder is not next to this copy of the retailer.
"""
import importlib.util
import json
from pathlib import Path

import pytest

from conftest import H, TODAY

DESK = Path(__file__).resolve().parents[2] / "retail" / "desks" / "pricing-and-replenishment"
if not (DESK / "make_cases.py").is_file():
    pytest.skip("the pricing and replenishment desk folder is not next to this copy of the retailer", allow_module_level=True)

CATEGORIES = ["Ambient grocery", "Chilled food", "Frozen food", "Bakery", "Fresh produce", "Drinks", "Household", "Personal care"]
SHORT = ["SUP-301", "SUP-303", "SUP-304"]
NOTHING_TO_ORDER = "SUP-317"


def _script():
    spec = importlib.util.spec_from_file_location("pricing_and_replenishment_desk_make_cases", DESK / "make_cases.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _held() -> list:
    return json.loads((DESK / "cases.json").read_text(encoding="utf-8"))["cases"]


class ApiSource:
    """The readers make_cases.py uses over the seed, here over the service's API."""

    def __init__(self, client):
        self.client = client

    def _get(self, path, **params):
        answer = self.client.get(path, headers=H, params=params)
        assert answer.status_code == 200, (path, params, answer.text)
        return answer.json()

    def prices(self, category):
        return self._get("/pricing/prices", category=category)["items"]

    def competitors(self):
        return {x["sku"]: x for x in self._get("/pricing/competitor-prices")["items"]}

    def levels(self):
        answer = self._get("/stock/levels")
        assert answer["retailer_date"] == TODAY
        return {x["sku"]: x for x in answer["items"]}

    def terms(self, supplier_id=None):
        return self._get("/stock/supply-terms", **({"supplier_id": supplier_id} if supplier_id else {}))["items"]

    def pricing_rules(self):
        return self._get("/pricing/rules")

    def replenishment_rules(self):
        return self._get("/stock/replenishment-rules")


def test_cases_file_is_what_the_script_writes():
    held = (DESK / "cases.json").read_text(encoding="utf-8")
    assert held == _script().render(), "cases.json differs from what make_cases.py would write: run make_cases.py"


def test_the_twelve_cases_in_order_each_with_its_kind():
    held = _held()
    assert [c["category"] for c in held[:8]] == CATEGORIES
    assert [c["supplier"].split("(")[1].rstrip(")") for c in held[8:]] == SHORT + [NOTHING_TO_ORDER]
    assert [c["kind"] for c in held] == ["Price change"] * 8 + ["Replenishment order"] * 4
    config = json.loads((DESK / "desk.config.json").read_text(encoding="utf-8"))
    assert set(c["kind"] for c in held) == set(config["routing"]["kinds"])
    keys = {f["key"] for f in config["intake"]["fields"]}
    for c in held:
        assert set(c) - {"arrived_via"} == keys
        assert c["received_on"] == TODAY
    replies = json.loads((DESK / "demo-replies.json").read_text(encoding="utf-8"))
    assert set(replies["replies"]) == {c["title"] for c in held} and replies["default"]


def test_every_case_holds_what_the_service_returns(client):
    script = _script()
    assert _held() == script.build_from(ApiSource(client))


def test_each_price_case_carries_its_category_and_the_pricing_rules(client):
    source = ApiSource(client)
    competitors, rules = source.competitors(), source.pricing_rules()
    assert len(competitors) == 30
    seen = set()
    for c in _held()[:8]:
        rows = source.prices(c["category"].lower().replace(" ", "_"))
        assert c["lines"].split(", ") == [p["sku"] for p in rows]
        for p in rows:
            assert f"{p['sku']} {p['name']}" in c["text"]
            if p["sku"] in competitors:
                seen.add(p["sku"])
                for x in competitors[p["sku"]]["prices"]:
                    assert f"{x['competitor']} {x['price']:,.2f}" in c["text"]
        for rule in rules["rules"]:
            assert f"{rule['rule_id']} {rule['title']}: {rule['text']}" in c["text"]
        for step in rules["how_a_recommendation_is_worked_out"]:
            assert f"{step['step']}: {step['text']}" in c["text"]
    assert seen == set(competitors), "a line with a published competitor price is in no price case"


def test_the_cases_carry_the_lines_the_right_answers_name(store):
    """Which suppliers have a line that runs out is worked out by the script. It must be what the service's own answer set names."""
    held = _held()
    planted = store.data["pricing_planted"]["price_answers"]
    price_lines = {sku for c in held[:8] for sku in c["lines"].split(", ")}
    assert set(planted) <= price_lines
    short = store.data["stock_planted"]["run_out"]
    assert sorted({x["supplier_id"] for x in short.values()}) == SHORT
    for sku, x in short.items():
        case = next(c for c in held[8:] if f"({x['supplier_id']})" in c["supplier"])
        assert sku in case["lines"].split(", ") and f"{sku} " in case["text"]
    nothing = next(c for c in held[8:] if f"({NOTHING_TO_ORDER})" in c["supplier"])
    assert not set(nothing["lines"].split(", ")) & set(short)
    assert set(nothing["lines"].split(", ")) & set(store.data["stock_planted"]["overstocked"]) == {"HH-6105"}


def test_the_replenishment_rules_and_supply_terms_are_in_each_supplier_case(client):
    source = ApiSource(client)
    rules = source.replenishment_rules()
    for c in _held()[8:]:
        supplier_id = c["supplier"].split("(")[1].rstrip(")")
        terms = source.terms(supplier_id)
        assert c["lines"].split(", ") == [t["sku"] for t in terms]
        for t in terms:
            for o in t["open_orders"]:
                assert f"{o['order_ref']}, {o['units']:,} units, due {o['due_on']}" in c["text"]
        for rule in rules["rules"]:
            assert f"{rule['rule_id']} {rule['title']}: {rule['text']}" in c["text"]
