"""Purchasing, version 1.2: delivery notes, supplier payments and supplier questions.

Two purchase orders are added to the six of version 1, each with a goods receipt and no invoice yet. Every
goods receipt has its delivery note. What a careful reader should find is kept in its own record sets
(delivery_note_answers, supplier_question_answers) and no operation serves it.
"""

from __future__ import annotations

from datetime import date, timedelta

from .seed_base import VAT_RATE, d_ago, money
from .seed_purch import BUYERS, PAYMENT_TERMS_DAYS, RECEIVERS, SUPPLIERS, make_po, make_receipt

DOCK = "Port Ilvane Distribution Centre"

# The two orders version 1.2 adds: po, supplier, buyer, ordered days ago, received days ago, receipt, note,
# order lines (item, unit, ordered, price, received), what the note says was delivered, an extra receipt line, remarks
_NEW_ORDERS = [
    ("PO-450161", "SUP-302", "dry", 8, 2, "GR-60161", "DN-4142",
     [("Pizza box, medium", "each", 12000, 0.42, 12000), ("Pizza box, large", "each", 8000, 0.55, 0)],
     [12000, 8000], ("Pizza box, small", "each", 8000),
     "Receiver's note: the 8,000 boxes on the second pallet are small boxes, not large. Booked in as small. Signed by the "
     "driver and the receiver."),
    ("PO-450164", "SUP-304", "fresh", 6, 1, "GR-60164", "DN-4149",
     [("Green peppers", "kg", 600, 6.20, 600), ("Onions, white", "kg", 800, 2.80, 680)],
     [600, 800], None,
     "Receiver's note: 6 cases of white onions (20 kg each) crushed on the pallet and refused at the dock. Signed by the "
     "driver and the receiver."),
]
# note number: (kind, item, quantity claimed, unit, net amount claimed)
NOTE_ANSWERS = {
    "DN-4135": [("short_delivery", "Mozzarella, shredded", 200, "kg", 4900.00)],
    "DN-4142": [("wrong_item", "Pizza box, large", 8000, "each", 4400.00)],
    "DN-4149": [("damaged", "Onions, white", 120, "kg", 336.00)],
}


def note_text(note: dict) -> str:
    rows = "\n".join(f"{x['item']} | {x['unit']} | {x['quantity_delivered']}" for x in note["lines"])
    return (f"INVENTED SAMPLE. Every supplier, item and quantity here is made up.\nDELIVERY NOTE\n"
            f"Supplier: {note['supplier_name']} ({note['supplier_id']})\nDelivery note number: {note['note_number']}\n"
            f"Delivered on: {note['delivered_on']}\nDelivered to: {note['delivered_to']}\nPurchase order: {note['po_number']}\n\n"
            f"Item | Unit | Quantity delivered\n{rows}\n\nWritten on the note at the dock: {note['remarks_at_delivery'] or 'nothing'}\n")


def make_note(number: str, po: dict, receipt: dict, delivered: list, remarks: str = "") -> dict:
    note = {"note_number": number, "po_number": po["po_number"], "supplier_id": po["supplier_id"],
            "supplier_name": po["supplier_name"], "delivered_on": receipt["received_on"], "delivered_to": DOCK,
            "receipt_id": receipt["receipt_id"],
            "lines": [{"line_no": x["line_no"], "item": x["item"], "unit": x["unit"], "quantity_delivered": q}
                      for x, q in zip(po["lines"], delivered)],
            "remarks_at_delivery": remarks, "status": "received", "claims": [], "claim_sent": None}
    note["text"] = note_text(note)
    return note


# payment, supplier, invoice, invoice dated days ago, net, deduction (net, reason, debit note) or None
_PAYMENTS = [
    ("PAY-7001", "SUP-301", "INV-87010", 70, 11200.00, None),
    ("PAY-7002", "SUP-302", "INV-3301", 66, 8100.00, None),
    ("PAY-7003", "SUP-303", "INV-76410", 59, 26700.00, None),
    ("PAY-7004", "SUP-304", "INV-5066", 55, 6580.00, (310.00, "50 kg of green peppers rejected at receipt as soft. 50 kg at 6.20.", "DBN-0412")),
    ("PAY-7005", "SUP-302", "INV-3352", 50, 5040.00, None),
    ("PAY-7006", "SUP-301", "INV-87655", 39, 8600.00, None),
    ("PAY-7007", "SUP-303", "INV-76833", 33, 13350.00, None),
    ("PAY-7008", "SUP-304", "INV-5098", 30, 3920.00, None),
    ("PAY-7009", "SUP-302", "INV-3377", 48, 9660.00, (840.00, "2,000 medium pizza boxes arrived water damaged. 2,000 at 0.42.", "DBN-0431")),
    ("PAY-7010", "SUP-301", "INV-87702", 28, 6200.00, None),
]


def make_payment(today: date, pay_id: str, sid: str, invoice: str, inv_ago: int, net: float, deduction) -> dict:
    total = money(net * (1 + VAT_RATE))
    invoice_date = today - timedelta(days=inv_ago)
    due = invoice_date + timedelta(days=PAYMENT_TERMS_DAYS)
    ded = None
    amount = total
    if deduction:
        d_net, reason, debit_note = deduction
        ded = {"net": d_net, "tax": money(d_net * VAT_RATE), "amount": money(d_net * (1 + VAT_RATE)), "reason": reason,
               "debit_note": debit_note}
        amount = money(total - ded["amount"])
    paid = due <= today
    return {"payment_id": pay_id, "supplier_id": sid, "supplier_name": SUPPLIERS[sid]["name"], "invoice_number": invoice,
            "invoice_date": invoice_date.isoformat(), "invoice_total": total, "due_date": due.isoformat(),
            "status": "paid" if paid else "scheduled", "paid_on": due.isoformat() if paid else None,
            "scheduled_for": None if paid else due.isoformat(), "amount": amount, "currency": "USD", "method": "bank transfer",
            "remittance_advice": pay_id.replace("PAY", "RA") if paid else "", "deduction": ded}


# number, supplier, received days ago, subject, message, then the right answer: answer status, the records that answer it
_QUESTIONS = [
    ("01", "SUP-303", 3, "Payment for INV-76410", "We cannot see payment for our invoice INV-76410 on our statement. Where is it?",
     "answered_from_records", ["PAY-7003"]),
    ("02", "SUP-301", 2, "When will INV-87655 be paid", "Please tell us when invoice INV-87655 will be paid.",
     "answered_from_records", ["PAY-7006"]),
    ("03", "SUP-304", 2, "INV-5066 short-paid", "Invoice INV-5066 was for 7,567.00 and we received 7,210.50. Why was it short-paid?",
     "answered_from_records", ["PAY-7004"]),
    ("04", "SUP-302", 1, "Delivery slot", "Our lorry is booked into your distribution centre at 07:00 next Thursday. Can the "
                                          "slot move to 13:00?", "records_do_not_answer", []),
    ("05", "SUP-303", 1, "Status of INV-77102", "Has invoice INV-77102 been approved for payment, and when is it due?",
     "answered_from_records", ["INV-77102"]),
    ("06", "SUP-301", 0, "Quantity booked in on PO-450158", "Our delivery note DN-4135 shows 500 kg delivered on PO-450158. What "
                                                            "quantity did you book in?", "answered_from_records", ["GR-60158", "DN-4135"]),
]


def make_question(today: date, qid: str, sid: str, ago: int, subject: str, message: str) -> dict:
    s = SUPPLIERS[sid]
    return {"question_id": qid, "received_on": d_ago(today, ago), "supplier_id": sid, "supplier_name": s["name"],
            "from_name": s["contact_name"], "from_email": s["contact_email"], "subject": subject, "message": message,
            "status": "open", "reply_drafts": [], "reply_sent": None}


def build_more(today: date, base: dict) -> dict:
    """Adds to what build_purchasing made. base holds purchase_orders and goods_receipts and gets the two new orders."""
    pos, receipts = base["purchase_orders"], base["goods_receipts"]
    notes, note_answers = {}, {}
    for receipt in list(receipts.values()):  # the six receipts of version 1, each with the note number it already carries
        po = pos[receipt["po_number"]]
        delivered = [x["quantity_ordered"] for x in po["lines"]]
        notes[receipt["delivery_note"]] = make_note(receipt["delivery_note"], po, receipt, delivered)
    for n, (number, sid, buyer, ordered_ago, received_ago, receipt_id, note_no, lines, delivered, extra, remarks) in enumerate(_NEW_ORDERS):
        po = make_po(number, sid, BUYERS[buyer], d_ago(today, ordered_ago), lines)
        receipt = make_receipt(receipt_id, po, d_ago(today, received_ago), RECEIVERS[n % 2], note_no)
        if extra:
            receipt["lines"].append({"line_no": len(receipt["lines"]) + 1, "item": extra[0], "unit": extra[1],
                                     "quantity_received": extra[2]})
        pos[number], receipts[receipt_id] = po, receipt
        notes[note_no] = make_note(note_no, po, receipt, delivered, remarks)
    for number in notes:
        note_answers[number] = [dict(zip(("kind", "item", "quantity_claimed", "unit", "amount_claimed"), row))
                                for row in NOTE_ANSWERS.get(number, [])]
    payments = {p[0]: make_payment(today, *p) for p in _PAYMENTS}
    month = f"{today.year % 100:02d}{today.month:02d}"
    questions, question_answers = {}, {}
    for n, sid, ago, subject, message, status, records in _QUESTIONS:
        qid = f"SQ-{month}-{n}"
        questions[qid] = make_question(today, qid, sid, ago, subject, message)
        question_answers[qid] = {"answer_status": status, "records": records}
    return {"delivery_notes": notes, "delivery_note_answers": note_answers, "supplier_payments": payments,
            "supplier_questions": questions, "supplier_question_answers": question_answers}


# ---------------------------------------------------------------- arrivals

# delivery-note: four templates in turn. supplier, buyer, (item, unit, ordered, price, received), delivered on the note,
# an extra receipt line, remarks, the right claim (kind, quantity, amount) or None
_SIM_NOTES = [
    ("SUP-303", "dry", ("Pizza flour, 25 kg bag", "bag", 300, 44.50, 300), 300, None, "", None),
    ("SUP-301", "fresh", ("Butter, unsalted", "kg", 80, 31.00, 60), 80, None,
     "Receiver's note: 60 kg counted on the pallet, not 80. Signed by the driver and the receiver.", ("short_delivery", 20, 620.00)),
    ("SUP-302", "dry", ("Pizza box, medium", "each", 10000, 0.42, 0), 10000, ("Pizza box, large", "each", 10000),
     "Receiver's note: the boxes delivered are large, not medium. Booked in as large. Signed by the driver and the receiver.",
     ("wrong_item", 10000, 4200.00)),
    ("SUP-304", "fresh", ("Green peppers", "kg", 400, 6.20, 360), 400, None,
     "Receiver's note: 4 cases of green peppers (10 kg each) crushed and refused at the dock. Signed by the driver and the receiver.",
     ("damaged", 40, 248.00)),
]


def sim_note(data: dict, today: date, kind: int, po_number: str, receipt_id: str, note_number: str) -> tuple[str, str]:
    sid, buyer, line, delivered, extra, remarks, claim = _SIM_NOTES[kind]
    po = make_po(po_number, sid, BUYERS[buyer], d_ago(today, 7), [line])
    receipt = make_receipt(receipt_id, po, today.isoformat(), RECEIVERS[kind % 2], note_number)
    if extra:
        receipt["lines"].append({"line_no": 2, "item": extra[0], "unit": extra[1], "quantity_received": extra[2]})
    data["purchase_orders"][po_number], data["goods_receipts"][receipt_id] = po, receipt
    data["delivery_notes"][note_number] = make_note(note_number, po, receipt, [delivered], remarks)
    data["delivery_note_answers"][note_number] = [] if not claim else [
        {"kind": claim[0], "item": line[0], "quantity_claimed": claim[1], "unit": line[1], "amount_claimed": claim[2]}]
    return note_number, (f"A new delivery note {note_number} from {po['supplier_name']} has arrived in the purchasing system. It "
                         f"is for purchase order {po_number} and the goods were booked in today as {receipt_id}. No claim has "
                         "been drafted. Read it with get_delivery_note, then compare it with get_purchase_order and "
                         f"list_goods_receipts for {po_number}.")


# supplier-question: paid in full, scheduled, short-paid, and one the records cannot answer
_SIM_QUESTIONS = [
    ("SUP-301", "Payment for INV-87010", "Has invoice INV-87010 been paid? We cannot match it.", "answered_from_records", ["PAY-7001"]),
    ("SUP-303", "When will INV-76833 be paid", "When can we expect payment of invoice INV-76833?", "answered_from_records", ["PAY-7007"]),
    ("SUP-302", "INV-3377 short-paid", "Invoice INV-3377 was for 11,109.00 and we received 10,143.00. What was taken off?",
     "answered_from_records", ["PAY-7009"]),
    ("SUP-304", "Pallet height at your dock", "What is the highest pallet your dock can take? Our next load is stacked to 1.9 m.",
     "records_do_not_answer", []),
]


def sim_question(data: dict, today: date, kind: int, question_id: str) -> tuple[str, str]:
    sid, subject, message, status, records = _SIM_QUESTIONS[kind]
    data["supplier_questions"][question_id] = make_question(today, question_id, sid, 0, subject, message)
    data["supplier_question_answers"][question_id] = {"answer_status": status, "records": records}
    return question_id, (f"A new supplier question {question_id} from {SUPPLIERS[sid]['name']} has arrived in the purchasing "
                         f"system, with the subject \"{subject}\". It is open and has no reply. Read it with "
                         "get_supplier_question, then look in the payments, invoices, orders, receipts and delivery notes.")
