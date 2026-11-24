"""The recall desk's demo cases are this retailer's own records.

../retail/desks/recall/cases.json is written by make_cases.py in the same folder, from the seed of this
service at retailer date 2026-11-24: the recalled batch BT-44031, and the first two recalls that arrive,
BT-90001 and BT-90002. These tests fail when the file differs from what the script would write, and
when a case differs from what the service returns for that batch, its stores and its orders once the two
recalls have arrived. They also hold the first case to the batch record: the four stores and seven orders
that received the batch, and what must stay out of the recall.

The module is skipped when the desk folder is not next to this copy of the retailer.
"""
import importlib.util
import json
import re
from pathlib import Path

import pytest

from conftest import H

DESK = Path(__file__).resolve().parents[2] / "retail" / "desks" / "recall"
if not (DESK / "make_cases.py").is_file():
    pytest.skip("the recall desk folder is not next to this copy of the retailer", allow_module_level=True)

BATCHES = ["BT-44031", "BT-90001", "BT-90002"]
STORES = ["S-101", "S-104", "S-105", "S-107"]
ORDERS = ["RM-58115", "RM-58121", "RM-58147", "RM-58152", "RM-58160", "RM-58168", "RM-58180"]


def _script():
    spec = importlib.util.spec_from_file_location("recall_desk_make_cases", DESK / "make_cases.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _held() -> list:
    return json.loads((DESK / "cases.json").read_text(encoding="utf-8"))["cases"]


def _cases() -> dict:
    return {c["title"].split(" ")[0]: c for c in _held()}


def _lines(text: str, heading: str) -> list:
    out = []
    for line in text.split(heading + "\n", 1)[1].splitlines():
        if re.fullmatch(r"[A-Z][A-Z0-9 ,&/'()-]{2,}", line):
            break
        out.append(line)
    return out


class ApiSource:
    """The readers make_cases.py uses over the seed, here over the service's API.

    The two recalls that arrive are made the way the service makes them: one call for each to the
    arrival "recalled-batch".
    """

    def __init__(self, client, arrivals: int):
        self.client = client
        for n in range(arrivals):
            answer = client.post("/admin/simulate/recalled-batch", headers=H)
            assert answer.status_code == 200, answer.text
            assert answer.json()["item_id"] == f"BT-{90001 + n}"

    def _get(self, path, **params):
        answer = self.client.get(path, headers=H, params=params)
        assert answer.status_code == 200, f"{path} {params}: {answer.status_code}"
        return answer.json()

    def recalled(self):
        return sorted(b["batch_id"] for b in self._get("/stock/batches", status="recalled")["items"])

    def batch(self, batch_id):
        return self._get(f"/stock/batches/{batch_id}")

    def batches_of(self, sku):
        rows = self._get("/stock/batches", sku=sku)["items"]
        return sorted((self.batch(b["batch_id"]) for b in rows), key=lambda b: b["batch_id"])

    def site(self, site_id):
        return self._get(f"/stores/sites/{site_id}")

    def order(self, number):
        return self._get(f"/orders/orders/{number}")

    def order_numbers(self):
        answer = self._get("/orders/orders", limit=200)
        assert answer["total"] == answer["count"], "the orders do not fit one page"
        return sorted(o["order_number"] for o in answer["items"])

    def procedure(self):
        return self.batch("BT-44031")["recall_procedure"]


def test_cases_file_is_what_the_script_writes():
    held = (DESK / "cases.json").read_text(encoding="utf-8")
    assert held == _script().render(), "cases.json differs from what make_cases.py would write: run make_cases.py"


def test_the_three_recalls_in_order_with_the_desks_fields():
    held = _held()
    assert [c["title"].split(" ")[0] for c in held] == BATCHES
    config = json.loads((DESK / "desk.config.json").read_text(encoding="utf-8"))
    assert {c["kind"] for c in held} == set(config["routing"]["kinds"]) == {"Recalled batch"}
    keys = {f["key"] for f in config["intake"]["fields"]}
    for c in held:
        assert set(c) - {"arrived_via"} == keys
        # The queue's clock counts from the day the recall was raised.
        assert c[config["due"]["field"]] == "2026-11-24"


def test_every_case_holds_what_the_service_returns(client):
    """The whole file, built again from the API in place of the seed, once the two recalls have arrived."""
    script = _script()
    assert _held() == script.cases_from(ApiSource(client, script.ARRIVALS))


def test_the_first_recall_is_the_batch_record_and_nothing_else(store):
    batch = store.data["batches"]["BT-44031"]
    assert store.data["stock_planted"]["recalled_batch"] == "BT-44031" and batch["status"] == "recalled"
    text = _cases()["BT-44031"]["text"]
    stores = _lines(text, "STORES THE BATCH WAS DELIVERED TO")
    orders = _lines(text, "ONLINE ORDERS THE BATCH WAS PICKED FOR")
    assert [line.split(": ")[0] for line in stores] == STORES == [s["site_id"] for s in batch["stores"]]
    assert [line.split(": ")[0] for line in orders] == ORDERS == [o["order_number"] for o in batch["online_orders"]]
    for s, line in zip(batch["stores"], stores):
        assert f"{s['units_delivered']} units, {s['units_sold']} sold, {s['units_on_hand']} on hand" in line
    # What must stay out: the later batch and its two stores, and the two orders for a box that is not packed.
    out = _lines(text, "NOT ON THE BATCH RECORD")
    assert [line.split(": ")[0] for line in out] == ["BT-44032", "RM-58188", "RM-58198"]
    assert "S-102 and S-106" in out[0] and "not recalled" in out[0]
    assert not any(line.startswith(("S-102", "S-106")) for line in stores)
    assert store.data["orders"]["RM-58188"]["status"] == "placed"
    assert store.data["orders"]["RM-58198"]["status"] == "awaiting_fraud_review"
    # The supplier's words, as written.
    assert f"Reason: {batch['recall']['reason']}" in text


def test_a_customer_is_a_name_an_order_number_and_an_invalid_address(store):
    orders = store.data["orders"]
    for batch_id, case in _cases().items():
        text = case["text"]
        for line in _lines(text, "ONLINE ORDERS THE BATCH WAS PICKED FOR"):
            number = line.split(": ")[0]
            o = orders[number]
            assert f"{number}: {o['customer_name']}, {o['customer_email']}. " in line
            assert o["customer_email"].endswith("@mail.invalid")
            # Nothing else of the customer's: no customer id, and no card, address or device reference.
            assert o["customer_id"] not in text
        assert not re.search(r"CARD-\d|ADDR-\d|DEV-\d", text), batch_id
        others = [a.rstrip(".") for a in re.findall(r"\S+@\S+", text) if "@mail.invalid" not in a]
        assert others == ["care@rowanmere-market.example"], batch_id


def test_the_desk_records_a_decision_and_calls_no_operation_of_the_retailer():
    config = json.loads((DESK / "desk.config.json").read_text(encoding="utf-8"))
    assert all("act" not in d for d in config["decisions"])
    assert "sent nothing to a store or a customer" in config["next"]["issued"]
    assert config["rules"]["fourEyes"] is True
