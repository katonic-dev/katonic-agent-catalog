"""Builds cases.json for the accounts payable desk from the invented retailer's own records.

Sixteen cases, as the purchasing system holds them when the retailer's date is 24 November 2026:
the six supplier invoices, four delivery notes (the three that differ from what was booked in, and
one that agrees) and the six open supplier questions. Nothing is typed here by hand: suppliers,
orders, receipts, invoices, notes, payments and questions come from the seed of the service in
../../../demo-retailer. No server is started.

Each case carries the records its agent needs, because the desk's agents work from the message
alone. For a supplier question the records are found the way a person would find them: by the
invoice, order and delivery note numbers the supplier wrote. The service's own answer sets are
never read.

Usage, from anywhere:
    python make_cases.py           writes cases.json beside this file
    python make_cases.py --check   exits 1 if cases.json differs from what would be written

The test demo-retailer/tests/test_accounts_payable_desk_cases.py runs the same comparison, and
builds every case again from what the service returns.
Rowanmere Group is invented, and so is every record.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
RETAILER = HERE.parents[2] / "demo-retailer"
OUT = HERE / "cases.json"

RETAILER_DATE = date(2026, 11, 24)
INVOICES = ["INV-88214", "INV-3391", "INV-77102", "INV-5120", "INV-6417", "INV-9034"]
# The three notes that differ from what was booked in, then one that agrees.
NOTES = ["DN-4135", "DN-4142", "DN-4149", "DN-4100"]
QUESTIONS = ["SQ-2611-01", "SQ-2611-02", "SQ-2611-03", "SQ-2611-04", "SQ-2611-05", "SQ-2611-06"]

KIND_INVOICE = "Invoice match"
KIND_NOTE = "Delivery discrepancy"
KIND_QUESTION = "Supplier question"

COMMENT = ("Sixteen invented cases for the demo: six supplier invoices, four delivery notes and six supplier questions. Made by "
           "make_cases.py from the records the invented retailer (demo-retailer) holds at retailer date 2026-11-24. Do not edit "
           "by hand: change the service's seed and run the script. Rowanmere Group, its suppliers and every record are invented.")

SYSTEM_HOLDS = ("The purchasing system holds orders, goods receipts, invoices, delivery notes and payments. It holds no "
                "delivery slots and no dock rules.")
NO_PAYMENT = "None. An invoice with no payment row is not paid and has no payment scheduled."
NOTHING_NAMED = "None. The question names no invoice, order or delivery note."


def money(v) -> str:
    return f"{v:,.2f}"


def qty(v) -> str:
    return f"{v:,}"


def amount(quantity, unit: str) -> str:
    """600 bags, 400 kg, 20,000: a quantity with its unit, as a person writes it."""
    if unit == "each":
        return qty(quantity)
    if unit == "kg":
        return f"{qty(quantity)} kg"
    return f"{qty(quantity)} {unit}{'' if quantity == 1 else 's'}"


def price(value, unit: str) -> str:
    """46.00 a bag, 24.50 a kg, 0.42 each."""
    return f"{money(value)} {'each' if unit == 'each' else 'a ' + unit}"


def status(value: str) -> str:
    return value.replace("_", " ")


def supplier_of(record: dict) -> str:
    return f"{record['supplier_name']} ({record['supplier_id']})"


# ---------------------------------------------------------------- the blocks of a case's text

def order_block(po: dict, received: bool = False) -> list:
    lines = ["THE PURCHASE ORDER", f"Order: {po['po_number']}, ordered {po['order_date']}", f"Buyer: {po['buyer']}",
             f"Order status: {status(po['status'])}", "ORDER LINES"]
    for x in po["lines"]:
        line = f"{x['line_no']}. {x['item']}: {amount(x['quantity_ordered'], x['unit'])} at {price(x['unit_price'], x['unit'])}"
        if received:
            line += f", {amount(x['quantity_received'], x['unit'])} received so far"
        lines.append(line)
    return lines


def receipt_block(receipts: list) -> list:
    lines = ["GOODS RECEIVED"]
    if not receipts:
        return lines + ["Nothing is booked in against this order."]
    for r in receipts:
        lines.append(f"Receipt: {r['receipt_id']}, booked in {r['received_on']} at {r['received_at']}")
        lines += [f"{x['line_no']}. {x['item']}: {amount(x['quantity_received'], x['unit'])} booked in" for x in r["lines"]]
    return lines


def note_lines(note: dict) -> list:
    return [f"{x['line_no']}. {x['item']}: {amount(x['quantity_delivered'], x['unit'])} on the note" for x in note["lines"]]


def invoice_text(inv: dict, po: dict | None, receipts: list) -> str:
    """One supplier invoice with its purchase order and what was received against it."""
    lines = ["THE INVOICE", f"Invoice: {inv['invoice_number']}", f"Supplier: {supplier_of(inv)}", f"Dated: {inv['invoice_date']}",
             f"Due: {inv['due_date']}", f"Order: {inv['po_number']}", f"Invoice status: {status(inv['status'])}", "INVOICE LINES"]
    lines += [f"{x['line_no']}. {x['item']}: {amount(x['quantity'], x['unit'])} at {price(x['unit_price'], x['unit'])}, amount {money(x['amount'])}"
              for x in inv["lines"]]
    lines += [f"Net: USD {money(inv['net'])}", f"Tax: USD {money(inv['tax'])}", f"Total: USD {money(inv['total'])}"]
    if po is None:
        lines += ["THE PURCHASE ORDER", f"The purchasing system holds no order {inv['po_number']}."]
    else:
        lines += order_block(po) + receipt_block(receipts)
    return "\n".join(lines)


def note_text(note: dict, po: dict, receipts: list, invoices: list) -> str:
    """One delivery note with its purchase order, what was booked in, and what any invoice for the order bills."""
    lines = ["THE DELIVERY NOTE", f"Note: {note['note_number']}", f"Supplier: {supplier_of(note)}",
             f"Delivered: {note['delivered_on']} to {note['delivered_to']}", f"Order: {note['po_number']}", "NOTE LINES"]
    lines += note_lines(note)
    lines.append(f"Dock remark: {note['remarks_at_delivery'] or 'nothing'}")
    lines += order_block(po) + receipt_block(receipts)
    lines.append("INVOICES FOR THE ORDER")
    if not invoices:
        lines.append("No invoice refers to this order yet.")
    for inv in invoices:
        billed = "; ".join(f"{x['item']}, {amount(x['quantity'], x['unit'])}" for x in inv["lines"])
        lines.append(f"{inv['invoice_number']} bills: {billed}")
    return "\n".join(lines)


def payment_lines(p: dict) -> list:
    when = f"paid on {p['paid_on']}" if p["status"] == "paid" else f"scheduled for {p['scheduled_for']}"
    lines = [f"Payment: {p['payment_id']}, {when} by {p['method']}", f"Amount: USD {money(p['amount'])}",
             f"Invoice total: USD {money(p['invoice_total'])}, dated {p['invoice_date']}, due {p['due_date']}"]
    if p["remittance_advice"]:
        lines.append(f"Remittance: {p['remittance_advice']}")
    ded = p["deduction"]
    if ded:
        lines += [f"Deduction: USD {money(ded['net'])} net and USD {money(ded['tax'])} tax, USD {money(ded['amount'])} in all",
                  f"Reason: {ded['reason']}", f"Debit note: {ded['debit_note']}"]
    else:
        lines.append("Deduction: none")
    return lines


def ids_named(question: dict) -> dict:
    """The invoice, order and delivery note numbers the supplier wrote, in the order they appear."""
    words = f"{question['subject']} {question['message']}"
    found = {}
    for key, pattern in (("invoices", r"\bINV-\d+\b"), ("orders", r"\bPO-\d+\b"), ("notes", r"\bDN-\d+\b")):
        found[key] = list(dict.fromkeys(re.findall(pattern, words)))
    return found


def question_text(question: dict, source) -> str:
    """One supplier question with the records it points to, for that supplier only.

    source gives the records: payments_for(invoice_number), invoice(number), order(po_number),
    receipts_for(po_number), notes_for(po_number) and note(number). Each returns what the service holds, or None or [].
    """
    sid = question["supplier_id"]
    mine = lambda record: record is not None and record["supplier_id"] == sid  # noqa: E731
    lines = ["THE SUPPLIER'S MESSAGE", f"Number: {question['question_id']}",
             f"From: {question['from_name']}, {supplier_of(question)}", f"Received: {question['received_on']}",
             f"Subject: {question['subject']}", f"Message: {question['message']}"]
    named = ids_named(question)
    shown_notes = []
    for number in named["invoices"]:
        lines.append(f"PAYMENTS FOR {number}")
        payments = [p for p in source.payments_for(number) if mine(p)]
        if not payments:
            lines.append(NO_PAYMENT)
        for p in payments:
            lines += payment_lines(p)
        inv = source.invoice(number)
        if mine(inv):
            lines += [f"INVOICE {number}", f"Dated: {inv['invoice_date']}", f"Invoice status: {status(inv['status'])}",
                      f"Due: {inv['due_date']}", f"Total: USD {money(inv['total'])}"]
    for number in named["orders"]:
        po = source.order(number)
        if not mine(po):
            continue
        lines += order_block(po, received=True) + receipt_block(source.receipts_for(number))
        for note in source.notes_for(number):
            shown_notes.append(note["note_number"])
            lines += [f"DELIVERY NOTE {note['note_number']}", f"Delivered: {note['delivered_on']}"] + note_lines(note)
            lines.append(f"Dock remark: {note['remarks_at_delivery'] or 'nothing'}")
    for number in named["notes"]:
        note = source.note(number)
        if number in shown_notes or not mine(note):
            continue
        lines += [f"DELIVERY NOTE {number}", f"Delivered: {note['delivered_on']}"] + note_lines(note)
        lines.append(f"Dock remark: {note['remarks_at_delivery'] or 'nothing'}")
    if not any(named.values()):
        lines += ["RECORDS NAMED IN THE MESSAGE", NOTHING_NAMED]
    lines += ["WHAT THE SYSTEM HOLDS", SYSTEM_HOLDS]
    return "\n".join(lines)


# ---------------------------------------------------------------- the cases

def invoice_case(inv: dict, po: dict | None, receipts: list) -> dict:
    return {"title": f"{inv['invoice_number']} from {inv['supplier_name']}", "kind": KIND_INVOICE, "supplier": supplier_of(inv),
            "about": f"USD {money(inv['total'])}", "order": inv["po_number"], "buyer": po["buyer"] if po else "",
            "received_on": inv["invoice_date"], "text": invoice_text(inv, po, receipts), "arrived_via": "feed"}


def note_case(note: dict, po: dict, receipts: list, invoices: list) -> dict:
    return {"title": f"{note['note_number']} from {note['supplier_name']}", "kind": KIND_NOTE, "supplier": supplier_of(note),
            "about": f"Delivered {note['delivered_on']}", "order": note["po_number"], "buyer": po["buyer"],
            "received_on": note["delivered_on"], "text": note_text(note, po, receipts, invoices), "arrived_via": "feed"}


def question_case(question: dict, source) -> dict:
    return {"title": f"{question['question_id']} from {question['supplier_name']}", "kind": KIND_QUESTION,
            "supplier": supplier_of(question), "about": question["subject"], "order": "", "buyer": "",
            "received_on": question["received_on"], "text": question_text(question, source), "arrived_via": "feed"}


class SeedSource:
    """The records as the service's seed holds them. The test has the same five readers over the API."""

    def __init__(self, data: dict):
        self.data = data

    def payments_for(self, invoice_number: str) -> list:
        return sorted((p for p in self.data["supplier_payments"].values() if p["invoice_number"] == invoice_number),
                      key=lambda p: (p["invoice_date"], p["payment_id"]))

    def invoice(self, number: str):
        return self.data["supplier_invoices"].get(number)

    def order(self, number: str):
        return self.data["purchase_orders"].get(number)

    def receipts_for(self, po_number: str) -> list:
        return sorted((r for r in self.data["goods_receipts"].values() if r["po_number"] == po_number),
                      key=lambda r: r["receipt_id"])

    def notes_for(self, po_number: str) -> list:
        return sorted((n for n in self.data["delivery_notes"].values() if n["po_number"] == po_number),
                      key=lambda n: (n["delivered_on"], n["note_number"]))

    def note(self, number: str):
        return self.data["delivery_notes"].get(number)

    def invoices_for(self, po_number: str) -> list:
        return sorted((i for i in self.data["supplier_invoices"].values() if i["po_number"] == po_number),
                      key=lambda i: (i["invoice_date"], i["invoice_number"]))


def _seed() -> dict:
    """The service's starting data for the retailer date. Imported, never served."""
    if str(RETAILER) not in sys.path:
        sys.path.insert(0, str(RETAILER))
    from retailer.seed import build_all  # noqa: E402

    return build_all(RETAILER_DATE)


def build() -> dict:
    data = _seed()
    source = SeedSource(data)
    cases = []
    for number in INVOICES:
        inv = data["supplier_invoices"][number]
        cases.append(invoice_case(inv, source.order(inv["po_number"]), source.receipts_for(inv["po_number"])))
    for number in NOTES:
        note = data["delivery_notes"][number]
        po = note["po_number"]
        cases.append(note_case(note, source.order(po), source.receipts_for(po), source.invoices_for(po)))
    for number in QUESTIONS:
        cases.append(question_case(data["supplier_questions"][number], source))
    return {"$comment": COMMENT, "cases": cases}


def render() -> str:
    return json.dumps(build(), ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str]) -> int:
    text = render()
    if "--check" in argv:
        held = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if held != text:
            print("cases.json differs from what make_cases.py would write. Run make_cases.py.")
            return 1
        print("cases.json is what make_cases.py would write.")
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.name}: {len(build()['cases'])} cases")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
