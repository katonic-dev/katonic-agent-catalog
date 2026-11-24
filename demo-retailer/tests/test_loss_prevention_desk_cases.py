"""The loss prevention desk's demo cases are this retailer's own records.

../retail/desks/loss-prevention/cases.json is written by make_cases.py in the same folder, from the
seed of this service at retailer date 2026-11-24: the four orders flagged for a fraud review, a till
audit for each of four sites, and six stock loss cases (three stores and three lines). These tests fail
when the file differs from what the script would write, and when a case differs from what the service
returns for that order, site, store or line. They also hold the cases to what the service's own answer
sets say: which rows are outside a till rule, which stores and lines are beyond tolerance.

The module is skipped when the desk folder is not next to this copy of the retailer.
"""
import importlib.util
import json
import re
from pathlib import Path

import pytest

from conftest import H

DESK = Path(__file__).resolve().parents[2] / "retail" / "desks" / "loss-prevention"
if not (DESK / "make_cases.py").is_file():
    pytest.skip("the loss prevention desk folder is not next to this copy of the retailer", allow_module_level=True)

PERIOD = "2026-10"
ORDERS = ["RM-58192", "RM-58194", "RM-58196", "RM-58198"]
TILL_SITES = ["S-106", "S-101", "S-104", "R-117"]
STOCK_STORES = ["S-103", "S-106", "S-102"]
STOCK_LINES = ["DR-5905", "HH-6105", "PC-6604"]
NUMBERS = (ORDERS + ["TA-2610-S106", "TA-2610-S101", "TA-2610-S104", "TA-2610-R117"]
           + ["SC-2610-103", "SC-2610-106", "SC-2610-102"] + ["SL-2610-DR5905", "SL-2610-HH6105", "SL-2610-PC6604"])


def _script():
    spec = importlib.util.spec_from_file_location("loss_prevention_desk_make_cases", DESK / "make_cases.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _held() -> list:
    return json.loads((DESK / "cases.json").read_text(encoding="utf-8"))["cases"]


def _cases() -> dict:
    return {c["title"].split(" ")[0]: c for c in _held()}


class ApiSource:
    """The readers make_cases.py uses over the seed, here over the service's API."""

    def __init__(self, client):
        self.client = client

    def _get(self, path, **params):
        answer = self.client.get(path, headers=H, params=params)
        assert answer.status_code == 200, f"{path} {params}: {answer.status_code}"
        return answer.json()

    def site(self, site_id):
        return self._get(f"/stores/sites/{site_id}")

    def order(self, number):
        return self._get(f"/orders/orders/{number}")

    def history(self, customer_id):
        answer = self._get(f"/orders/customers/{customer_id}/history")
        return {"orders": [o for o in answer["orders"] if not o["flagged"]], "account_changes": answer["account_changes"],
                "average_total": answer["average_total"], "highest_total": answer["highest_total"]}

    def till_row(self, row_id):
        rows = self._get("/tills/entries", limit=500)["items"]
        return next((r for r in rows if r["row_id"] == row_id), None)

    def till_rows(self, period, site_id):
        return self._get("/tills/entries", period=period, site_id=site_id, limit=500)["items"]

    def till_rules(self):
        return self._get("/tills/rules")

    def tolerance(self):
        return self._get("/stock/shrink-tolerance")

    def count(self, period, site_id):
        return self._get(f"/stock/counts/{period}", view="by_store", site_id=site_id)["items"][0]

    def count_rows(self, period, site_id):
        return self._get(f"/stock/counts/{period}", view="rows", site_id=site_id, limit=500)["items"]

    def line(self, period, sku):
        return next(x for x in self._get(f"/stock/counts/{period}", view="by_line", limit=500)["items"] if x["sku"] == sku)

    def line_rows(self, period, sku):
        return self._get(f"/stock/counts/{period}", view="rows", sku=sku, limit=500)["items"]


def test_cases_file_is_what_the_script_writes():
    held = (DESK / "cases.json").read_text(encoding="utf-8")
    assert held == _script().render(), "cases.json differs from what make_cases.py would write: run make_cases.py"


def test_the_fourteen_cases_in_order_each_with_its_kind():
    held = _held()
    assert [c["title"].split(" ")[0] for c in held] == NUMBERS
    assert [c["kind"] for c in held] == ["Flagged order"] * 4 + ["Till audit"] * 4 + ["Stock loss"] * 6
    config = json.loads((DESK / "desk.config.json").read_text(encoding="utf-8"))
    assert set(c["kind"] for c in held) == set(config["routing"]["kinds"])
    keys = {f["key"] for f in config["intake"]["fields"]}
    for c in held:
        assert set(c) - {"arrived_via"} == keys


def test_every_case_holds_what_the_service_returns(client):
    """The whole file, built again from the API in place of the seed."""
    assert _held() == _script().cases_from(ApiSource(client))


def test_the_orders_are_the_four_that_wait_for_a_review(client, store):
    flagged = client.get("/orders/flagged", headers=H, params={"status": "awaiting_review"}).json()["items"]
    assert sorted(o["order_number"] for o in flagged) == ORDERS
    cases, source = _cases(), ApiSource(client)
    for number in ORDERS:
        text = cases[number]["text"]
        order = source.order(number)
        history = source.history(order["customer_id"])
        assert f"Earlier orders: {len(history['orders'])}" in text
        for earlier in history["orders"]:
            assert f"{earlier['order_number']}: {earlier['placed_on']}" in text
            if earlier["refund"]:
                assert f"{earlier['refund']['till_row_id']}: " in text, f"{number}: the till row of the refund is not in the case"
        # A customer is an id. The case holds no name and no address of a person.
        assert order["customer_name"] not in json.dumps(cases[number]) and "@" not in text
    assert set(store.data["fraud_answers"]) == set(ORDERS)


def _outside(text: str) -> dict:
    """The rows of a case that are outside a till rule, worked out from the case's own lines by the four rules."""
    out = {}
    for line in text.split("THE TILL ROWS\n", 1)[1].splitlines():
        row_id, rest = line.split(": ", 1)
        rules = []
        refund = re.search(r"refund of ([\d.,]+), approver (\S+), receipt (\S+)$", rest)
        discount = re.search(r"discount of [\d.,]+, ([\d.]+) percent of [\d.,]+, reason code (\S+)$", rest)
        void = re.search(r"void of [\d.,]+, (after|before) payment, second person (\S+)$", rest)
        assert refund or discount or void, f"a till row was not read: {line}"
        if refund:
            if float(refund.group(1).replace(",", "")) > 50 and refund.group(2) == "none":
                rules.append("TC-1")
            if refund.group(3) == "none":
                rules.append("TC-2")
        elif discount:
            if float(discount.group(1)) > 20 and discount.group(2) == "none":
                rules.append("TC-3")
        elif void.group(1) == "after" and void.group(2) == "none":
            rules.append("TC-4")
        if rules:
            out[row_id] = rules
    return out


def test_a_till_audit_case_holds_every_row_of_its_site_and_the_rows_outside_a_rule_can_be_read_from_it(store):
    cases = _cases()
    planted = store.data["till_planted"]
    rows = store.data["till_rows"]
    found = []
    for site_id in TILL_SITES:
        text = cases[f"TA-2610-{site_id.replace('-', '')}"]["text"]
        mine = {r["row_id"] for r in rows.values() if r["site_id"] == site_id and r["date"].startswith(PERIOD)}
        assert set(re.findall(r"^(TR-\d+-\d+): ", text, flags=re.M)) == mine
        assert _outside(text) == {k: v for k, v in planted.items() if k in mine}, site_id
        found.append(len(_outside(text)))
        # The system's field names stay out of the case: each row is written in plain words.
        assert not re.search(r"approver_id|original_receipt|discount_percent|after_payment", text)
    # The site with the most rows outside the rules, two sites with two each, and a site with none.
    assert found == [12, 2, 2, 0]
    by_site = {}
    for row_id in planted:
        by_site[rows[row_id]["site_id"]] = by_site.get(rows[row_id]["site_id"], 0) + 1
    assert max(by_site, key=by_site.get) == TILL_SITES[0] and TILL_SITES[3] not in by_site


def test_the_stock_cases_are_the_stores_and_lines_the_service_holds_as_beyond_tolerance(client, store):
    planted = store.data["stock_planted"]
    assert planted["loss_stores"] == sorted(STOCK_STORES[:2]) and planted["loss_lines"] == STOCK_LINES
    cases, source = _cases(), ApiSource(client)
    tolerance = source.tolerance()
    for site_id in STOCK_STORES:
        count = source.count(PERIOD, site_id)
        case = cases[count["count_id"]]
        assert f"Loss percent: {count['loss_percent']:.2f}" in case["text"]
        assert (count["loss_percent"] > tolerance["store_tolerance_percent"]) == (site_id in planted["loss_stores"])
        # The till figures are counts and totals. No till row, cashier id or approver id is in a stock case.
        assert not re.search(r"TR-\d|C-3\d{3}|M-7\d{2}", case["text"])
    for sku in STOCK_LINES:
        line = source.line(PERIOD, sku)
        case = cases[f"SL-2610-{sku.replace('-', '')}"]
        assert f"Loss percent: {line['loss_percent']:.2f}" in case["text"]
        assert line["loss_percent"] > tolerance["line_tolerance_percent"]
        assert case["text"].count(" on the books, loss value ") == line["stores_counted"]
