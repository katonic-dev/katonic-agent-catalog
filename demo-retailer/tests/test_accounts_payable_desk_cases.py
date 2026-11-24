"""The accounts payable desk's demo cases are this retailer's own records.

../retail/desks/accounts-payable/cases.json is written by make_cases.py in the same folder, from the
seed of this service at retailer date 2026-11-24: the six supplier invoices, four delivery notes and the
six open supplier questions. These tests fail when the file differs from what the script would write,
and when a case differs from what the service returns for that invoice, note or question.

The module is skipped when the desk folder is not next to this copy of the retailer.
"""
import importlib.util
import json
from pathlib import Path

import pytest

from conftest import H

DESK = Path(__file__).resolve().parents[2] / "retail" / "desks" / "accounts-payable"
if not (DESK / "make_cases.py").is_file():
    pytest.skip("the accounts payable desk folder is not next to this copy of the retailer", allow_module_level=True)

INVOICES = ["INV-88214", "INV-3391", "INV-77102", "INV-5120", "INV-6417", "INV-9034"]
NOTES = ["DN-4135", "DN-4142", "DN-4149", "DN-4100"]
QUESTIONS = ["SQ-2611-01", "SQ-2611-02", "SQ-2611-03", "SQ-2611-04", "SQ-2611-05", "SQ-2611-06"]


def _script():
    spec = importlib.util.spec_from_file_location("accounts_payable_desk_make_cases", DESK / "make_cases.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _cases() -> dict:
    held = json.loads((DESK / "cases.json").read_text(encoding="utf-8"))["cases"]
    return {c["title"].split(" ")[0]: c for c in held}


class ApiSource:
    """The readers make_cases.py uses over the seed, here over the service's API."""

    def __init__(self, client):
        self.client = client

    def _get(self, path, **params):
        return self.client.get(f"/purchasing{path}", headers=H, params=params)

    def _one(self, path):
        answer = self._get(path)
        return answer.json() if answer.status_code == 200 else None

    def _items(self, path, **params):
        answer = self._get(path, **params)
        return answer.json()["items"] if answer.status_code == 200 else []

    def payments_for(self, invoice_number):
        return self._items("/payments", invoice_number=invoice_number)

    def invoice(self, number):
        return self._one(f"/invoices/{number}")

    def order(self, number):
        return self._one(f"/purchase-orders/{number}")

    def receipts_for(self, po_number):
        return self._items("/goods-receipts", po_number=po_number)

    def notes_for(self, po_number):
        return [self._one(f"/delivery-notes/{n['note_number']}") for n in self._items("/delivery-notes", po_number=po_number)]

    def note(self, number):
        return self._one(f"/delivery-notes/{number}")

    def invoices_for(self, po_number):
        po = self.order(po_number)
        return [self.invoice(n) for n in po["invoice_numbers"]]


def test_cases_file_is_what_the_script_writes():
    held = (DESK / "cases.json").read_text(encoding="utf-8")
    assert held == _script().render(), "cases.json differs from what make_cases.py would write: run make_cases.py"


def test_the_sixteen_cases_in_order_each_with_its_kind():
    held = json.loads((DESK / "cases.json").read_text(encoding="utf-8"))["cases"]
    assert [c["title"].split(" ")[0] for c in held] == INVOICES + NOTES + QUESTIONS
    assert [c["kind"] for c in held] == ["Invoice match"] * 6 + ["Delivery discrepancy"] * 4 + ["Supplier question"] * 6
    config = json.loads((DESK / "desk.config.json").read_text(encoding="utf-8"))
    assert set(c["kind"] for c in held) == set(config["routing"]["kinds"])
    keys = {f["key"] for f in config["intake"]["fields"]}
    for c in held:
        assert set(c) - {"arrived_via"} == keys


def test_each_invoice_case_holds_what_the_service_returns(client):
    script, cases, source = _script(), _cases(), ApiSource(client)
    for number in INVOICES:
        inv = source.invoice(number)
        assert inv is not None and inv["status"] == "received"
        po = source.order(inv["po_number"])
        assert cases[number] == script.invoice_case(inv, po, source.receipts_for(inv["po_number"]))
        assert cases[number]["buyer"] == po["buyer"]


def test_each_delivery_note_case_holds_what_the_service_returns(client):
    script, cases, source = _script(), _cases(), ApiSource(client)
    for number in NOTES:
        note = source.note(number)
        assert note is not None and note["status"] == "received"
        po = note["po_number"]
        assert cases[number] == script.note_case(note, source.order(po), source.receipts_for(po), source.invoices_for(po))
    # The three that differ are the three whose order is part received. The fourth agrees.
    assert [source.order(source.note(n)["po_number"])["status"] for n in NOTES] == ["part_received"] * 3 + ["received"]


def test_each_supplier_question_case_holds_what_the_service_returns(client):
    script, cases, source = _script(), _cases(), ApiSource(client)
    open_now = [q["question_id"] for q in client.get("/purchasing/supplier-questions", headers=H, params={"status": "open"}).json()["items"]]
    assert sorted(open_now) == QUESTIONS
    for number in QUESTIONS:
        question = client.get(f"/purchasing/supplier-questions/{number}", headers=H).json()
        assert cases[number] == script.question_case(question, source)


def test_a_question_case_carries_the_records_that_answer_it(store):
    """The records are found by the numbers the supplier wrote. They must be the ones the service's own answer names."""
    cases = _cases()
    answers = store.data["supplier_question_answers"]
    for number in QUESTIONS:
        text = cases[number]["text"]
        for record in answers[number]["records"]:
            assert record in text, f"{number}: {record} is not in the case"
        if not answers[number]["records"]:
            assert "The question names no invoice, order or delivery note." in text
