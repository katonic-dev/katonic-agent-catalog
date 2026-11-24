"""Purchasing, version 1: suppliers, purchase orders, goods receipts and supplier invoices."""

from __future__ import annotations

from datetime import date, timedelta

from .seed_base import VAT_RATE, d_ago, money

SUPPLIERS = {
    "SUP-301": dict(name="Ilvane Valley Dairy Ltd", supplies="mozzarella, butter", town="Port Ilvane",
                    contact_name="Perrin Haldwick-Sorrel", contact_email="accounts@ilvane-valley-dairy.example"),
    "SUP-302": dict(name="Marlow Reach Packaging Ltd", supplies="pizza boxes", town="Marlow Reach",
                    contact_name="Tamsin Ordway-Kell", contact_email="accounts@marlow-reach-packaging.example"),
    "SUP-303": dict(name="Tallowby Flour Mills Ltd", supplies="pizza flour", town="Tallowby",
                    contact_name="Gideon Rushmere-Alt", contact_email="accounts@tallowby-flour-mills.example"),
    "SUP-304": dict(name="Orchard Gate Fresh Produce Ltd", supplies="green peppers, onions", town="Marlow Reach",
                    contact_name="Linnet Carraway-Dunn", contact_email="accounts@orchard-gate-produce.example"),
}
BUYERS = {"fresh": "Hesper Valdane-Orr", "dry": "Dorian Ketterly-Voss"}
RECEIVERS = ["Ilsabet Thornquist-Bray", "Marek Sollander-Vyne"]
PAYMENT_TERMS_DAYS = 45

# po_number, supplier, buyer, days ago ordered, days ago received, [(item, unit, ordered, price, received)]
_ORDERS = [
    ("PO-450112", "SUP-301", "fresh", 22, 11, [("Mozzarella, shredded", "kg", 400, 24.50, 400), ("Butter, unsalted", "kg", 60, 31.00, 60)]),
    ("PO-450127", "SUP-302", "dry", 20, 10, [("Pizza box, medium", "each", 20000, 0.42, 20000), ("Pizza box, large", "each", 15000, 0.55, 15000)]),
    ("PO-450131", "SUP-303", "dry", 19, 9, [("Pizza flour, 25 kg bag", "bag", 600, 44.50, 600)]),
    ("PO-450140", "SUP-304", "fresh", 18, 8, [("Green peppers", "kg", 720, 6.20, 720), ("Onions, white", "kg", 900, 2.80, 900)]),
    ("PO-450152", "SUP-302", "dry", 14, 6, [("Wrap sleeve, foil-lined", "each", 30000, 0.09, 30000), ("Doughnut box, six", "each", 10000, 0.36, 10000)]),
    ("PO-450158", "SUP-301", "fresh", 10, 3, [("Mozzarella, shredded", "kg", 500, 24.50, 300)]),
]
_RECEIPT_IDS = {"PO-450112": "GR-60112", "PO-450127": "GR-60127", "PO-450131": "GR-60131", "PO-450140": "GR-60140",
                "PO-450152": "GR-60152", "PO-450158": "GR-60158"}

# invoice, po, days ago dated, [(item, unit, quantity, unit price)]
_INVOICES = [
    ("INV-88214", "PO-450112", 9, [("Mozzarella, shredded", "kg", 400, 24.50), ("Butter, unsalted", "kg", 60, 31.00)]),
    ("INV-3391", "PO-450127", 8, [("Pizza box, medium", "each", 20000, 0.42), ("Pizza box, large", "each", 15000, 0.55)]),
    ("INV-77102", "PO-450131", 7, [("Pizza flour, 25 kg bag", "bag", 600, 46.00)]),
    ("INV-5120", "PO-450140", 6, [("Green peppers", "kg", 800, 6.20), ("Onions, white", "kg", 900, 2.80)]),
    ("INV-6417", "PO-450152", 4, [("Wrap sleeve, foil-lined", "each", 30000, 0.09), ("Doughnut box, six", "each", 10000, 0.36),
                                  ("Delivery charge", "each", 1, 180.00)]),
    ("INV-9034", "PO-450158", 2, [("Mozzarella, shredded", "kg", 500, 24.50)]),
]


def make_po(number: str, supplier_id: str, buyer: str, order_date: str, lines: list) -> dict:
    out = []
    for n, (item, unit, qty, price, got) in enumerate(lines, start=1):
        out.append({"line_no": n, "item": item, "unit": unit, "quantity_ordered": qty, "unit_price": price,
                    "quantity_received": got, "buyer": buyer})
    done = all(x["quantity_received"] >= x["quantity_ordered"] for x in out)
    return {"po_number": number, "supplier_id": supplier_id, "supplier_name": SUPPLIERS[supplier_id]["name"],
            "order_date": order_date, "buyer": buyer, "currency": "USD", "status": "received" if done else "part_received",
            "net_total": money(sum(x["quantity_ordered"] * x["unit_price"] for x in out)), "lines": out}


def make_receipt(receipt_id: str, po: dict, received_on: str, who: str, note_no: str) -> dict:
    return {"receipt_id": receipt_id, "po_number": po["po_number"], "supplier_id": po["supplier_id"],
            "supplier_name": po["supplier_name"], "received_on": received_on, "received_by": who,
            "received_at": "Port Ilvane Distribution Centre", "delivery_note": note_no,
            "lines": [{"line_no": x["line_no"], "item": x["item"], "unit": x["unit"], "quantity_received": x["quantity_received"]}
                      for x in po["lines"]]}


def invoice_text(inv: dict) -> str:
    rows = "\n".join(f"{x['item']} | {x['unit']} | {x['quantity']} | {x['unit_price']:.2f} | {x['amount']:.2f}" for x in inv["lines"])
    return (f"INVENTED SAMPLE. Every supplier, item and amount here is made up.\nTAX INVOICE\n"
            f"Supplier: {inv['supplier_name']} ({inv['supplier_id']})\nInvoice number: {inv['invoice_number']}\n"
            f"Invoice date: {inv['invoice_date']}\nPurchase order: {inv['po_number']}\n"
            f"Payment terms: {PAYMENT_TERMS_DAYS} days\n\nItem | Unit | Quantity | Unit price (USD) | Amount (USD)\n{rows}\n\n"
            f"Net amount: {inv['net']:.2f}\nTax 15%: {inv['tax']:.2f}\nTotal due (USD): {inv['total']:.2f}\n")


def make_invoice(number: str, po_number: str, supplier_id: str, invoice_date: str, lines: list) -> dict:
    rows = [{"line_no": n, "item": item, "unit": unit, "quantity": qty, "unit_price": price, "amount": money(qty * price)}
            for n, (item, unit, qty, price) in enumerate(lines, start=1)]
    net = money(sum(x["amount"] for x in rows))
    tax = money(net * VAT_RATE)
    due = (date.fromisoformat(invoice_date) + timedelta(days=PAYMENT_TERMS_DAYS)).isoformat()
    inv = {"invoice_number": number, "supplier_id": supplier_id, "supplier_name": SUPPLIERS[supplier_id]["name"],
           "invoice_date": invoice_date, "due_date": due, "po_number": po_number, "status": "received", "currency": "USD",
           "lines": rows, "net": net, "tax": tax, "total": money(net + tax), "matches": [], "query": None,
           "approved_by": "", "approved_at": None}
    inv["text"] = invoice_text(inv)
    return inv


def build_purchasing(today: date) -> dict:
    suppliers = {sid: {"supplier_id": sid, **s, "payment_terms_days": PAYMENT_TERMS_DAYS, "currency": "USD"}
                 for sid, s in SUPPLIERS.items()}
    pos, receipts, invoices = {}, {}, {}
    for i, (number, sid, buyer, ordered_ago, received_ago, lines) in enumerate(_ORDERS):
        po = make_po(number, sid, buyer and BUYERS[buyer], d_ago(today, ordered_ago), lines)
        pos[number] = po
        receipts[_RECEIPT_IDS[number]] = make_receipt(_RECEIPT_IDS[number], po, d_ago(today, received_ago),
                                                      RECEIVERS[i % 2], f"DN-{4100 + i * 7}")
    for number, po_number, ago, lines in _INVOICES:
        invoices[number] = make_invoice(number, po_number, pos[po_number]["supplier_id"], d_ago(today, ago), lines)
    return {"suppliers": suppliers, "purchase_orders": pos, "goods_receipts": receipts, "supplier_invoices": invoices}


# What arrives with the event "supplier-invoice". Four templates, in turn:
#   0 agrees, 1 price differs, 2 quantity differs, 3 a line that is not on the order.
# supplier, buyer, ordered-and-received line, invoice lines
_SIM = [
    ("SUP-303", "dry", ("Pizza flour, 25 kg bag", "bag", 400, 44.50), [("Pizza flour, 25 kg bag", "bag", 400, 44.50)]),
    ("SUP-301", "fresh", ("Butter, unsalted", "kg", 80, 31.00), [("Butter, unsalted", "kg", 80, 32.50)]),
    ("SUP-304", "fresh", ("Onions, white", "kg", 600, 2.80), [("Onions, white", "kg", 650, 2.80)]),
    ("SUP-302", "dry", ("Pizza box, medium", "each", 10000, 0.42), [("Pizza box, medium", "each", 10000, 0.42),
                                                                  ("Pallet charge", "each", 1, 95.00)]),
]


def sim_invoice(data: dict, today: date, kind: int, po_number: str, receipt_id: str, invoice_number: str) -> tuple[str, str]:
    sid, buyer, (item, unit, qty, price), inv_lines = _SIM[kind]
    po = make_po(po_number, sid, BUYERS[buyer], d_ago(today, 9), [(item, unit, qty, price, qty)])
    data["purchase_orders"][po_number] = po
    data["goods_receipts"][receipt_id] = make_receipt(receipt_id, po, d_ago(today, 2), RECEIVERS[kind % 2], f"DN-{4300 + kind}")
    inv = make_invoice(invoice_number, po_number, sid, today.isoformat(), inv_lines)
    data["supplier_invoices"][invoice_number] = inv
    return invoice_number, (f"A new supplier invoice {invoice_number} from {inv['supplier_name']} has arrived in the purchasing "
                            f"system. It is for purchase order {po_number}, with a total of USD {inv['total']:,.2f}. It has been "
                            f"received and has not been matched. Read it with get_supplier_invoice, then compare it with "
                            f"get_purchase_order and list_goods_receipts for {po_number}.")
