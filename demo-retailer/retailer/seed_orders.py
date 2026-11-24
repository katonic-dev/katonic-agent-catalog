"""Orders, version 1.2: the online shop's orders, deliveries, return requests and the orders held for a fraud review.

43 orders of Rowanmere Market's online shop. Three have a delivery worth asking about, ten have a return
request, and four are flagged for a fraud review. What a careful reader should conclude is kept in its own
record sets (return_answers, fraud_answers) and no operation serves it.
"""

from __future__ import annotations

from datetime import date

from .seed_base import d_ago, money

NOTICE = "Rowanmere Group is invented, and so is this document. It is not the policy of any real retailer."
CARRIERS = {"fern": "Fernhollow Couriers", "quick": "Quickwillow Parcels", "van": "Rowanmere Market van", "": ""}
DEPOTS = ["Port Ilvane depot", "Marlow Reach depot", "Tallowby depot"]
CENTRE = "Port Ilvane fulfilment centre"
FREE_DELIVERY_FROM, STANDARD_CHARGE, NEXT_DAY_CHARGE = 60.00, 4.95, 7.95

_NAMES = ["Elowen Farrowby-Kent", "Corwin Daskell-Reeve", "Ysolde Marrick-Thane", "Bastian Orrell-Quince",
          "Nerys Coldwater-Finch", "Tobin Hallowmere-Graye", "Linnea Vossberg-Ash", "Ansel Pettigrove-Lune",
          "Marit Sundquay-Roe", "Jorah Wexcombe-Dell", "Seren Abbotsford-Wyle", "Calder Rensworth-Pike",
          "Odette Fairlamb-Stroud", "Emrys Kettleby-Marsh", "Thea Lindqvale-Burr", "Rufus Amberley-Skein",
          "Isolde Varnham-Crewe", "Kit Dunmorrow-Hale", "Petra Ashgrove-Lyle", "Lorcan Thistlewood-Rae",
          "Greta Mosswick-Trent", "Alaric Penhallow-Stone", "Wren Castellane-Voss", "Dunstan Yarrowby-Finn"]
# customers who exist only so that a simulated flagged order has a history to be read against
_SIM_NAMES = {31: "Halden Brookmyre-Vale", 32: "Sunniva Larchfield-Oake", 33: "Ivo Tanglewick-Moor", 34: "Clemency Harrowell-Byrne"}

# sku: (item, category, price in US dollars, tax included)
ITEMS = {
    "HW-1101": ("Cast-iron casserole, 24 cm", "homeware", 64.00),
    "HW-1102": ("Cotton bath towel set", "homeware", 28.00),
    "HW-1103": ("Ceramic dinner set, 12 piece", "homeware", 54.00),
    "EL-2201": ("Hand blender, 600 W", "electricals", 39.00),
    "EL-2202": ("Kettle, 1.7 litre", "electricals", 34.50),
    "EL-2203": ("Wireless headphones", "electricals", 312.00),
    "EL-2204": ("Games console", "electricals", 445.00),
    "EL-2205": ("Tablet computer, 10 inch", "electricals", 289.00),
    "EL-2206": ("Toaster, four slice", "electricals", 42.00),
    "CL-3301": ("Rain jacket, adult", "clothing", 72.00),
    "CL-3302": ("Wool jumper", "clothing", 46.00),
    "CL-3303": ("School shoes, child", "clothing", 31.00),
    "AG-4401": ("Olive oil, 1 litre bottle", "ambient_grocery", 11.50),
    "AG-4402": ("Coffee beans, 1 kg", "ambient_grocery", 18.40),
    "AG-4403": ("Pasta sauce, six jars", "ambient_grocery", 13.20),
    "AG-4404": ("Weekly grocery box", "ambient_grocery", 58.60),
    "CH-5501": ("Chilled ready meals, pack of four", "chilled_food", 19.80),
    "FZ-5601": ("Frozen fish fillets, 1 kg", "frozen_food", 14.90),
    "PC-6601": ("Electric toothbrush heads, pack of eight", "personal_care", 22.00),
    "PC-6602": ("Moisturising cream, 200 ml", "personal_care", 16.50),
    "GC-7702": ("Rowanmere gift card, USD 50", "gift_cards", 50.00),
    "TY-8801": ("Wooden train set", "toys", 38.00),
    "GD-9901": ("Garden hose reel, 30 m", "garden", 47.00),
}

# ---------------------------------------------------------------- the returns policy, version 3.0

EXCLUDED = ["chilled_food", "frozen_food", "fresh_produce", "bakery", "personal_care", "gift_cards", "made_to_order"]
_POLICY = [
    ("1", "The window", [
        ("1.1", "A return is asked for within 30 days of the day the order was delivered or collected. The day of delivery or "
                "collection is day 0, and day 30 is inside the window."),
        ("1.2", "A return asked for after day 30 is refused, unless section 5 applies."),
    ]),
    ("2", "The condition of the item", [
        ("2.1", "The item is unused and in its original packaging."),
        ("2.2", "An item that has been opened or used is not taken back because the customer changed their mind."),
        ("2.3", "Clothing and footwear tried on indoors, with the labels still attached, count as unused."),
    ]),
    ("3", "Categories that are not taken back for a change of mind", [
        ("3.1", "Chilled food, frozen food, fresh produce and bakery."),
        ("3.2", "Personal care items."),
        ("3.3", "Gift cards."),
        ("3.4", "Items made or cut to order."),
    ]),
    ("4", "The order", [
        ("4.1", "The item is a line of the order named on the request, and the quantity is not more than the quantity bought."),
        ("4.2", "The refund is the price paid for the quantity returned."),
    ]),
    ("5", "Damaged, faulty or wrong items", [
        ("5.1", "An item that arrived damaged, or that is not the item ordered, is taken back whatever sections 2 and 3 say, "
                "when it is reported within 7 days of delivery with a photograph."),
        ("5.2", "An item that is faulty is taken back within 30 days of delivery, opened or not, whatever section 2 says."),
        ("5.3", "Damage reported after day 7 is not decided by this policy. It goes to the Customer Care Team Leader."),
    ]),
    ("6", "Refunds", [
        ("6.1", "A refund goes to the payment method used for the order, within 5 working days of the approval."),
        ("6.2", "The delivery charge is refunded only when the whole order is returned under section 5."),
    ]),
]
NOT_DECIDED = ("This policy does not decide goodwill outside its conditions: that is for the Customer Care Team Leader. "
               "A request that describes an injury or an illness is a complaint and follows the Complaints Procedure.")
CONDITION_IDS = [c for _, _, conds in _POLICY for c, _ in conds]


def returns_policy_markdown() -> str:
    out = ["# Returns Policy (invented)", "",
           "Rowanmere Group is invented, and so is this document. It is not the policy of any real retailer.", "",
           "Version: 3.0. Owner: Head of Customer Care. It covers orders from Rowanmere Market's online shop.", ""]
    for number, title, conds in _POLICY:
        out += [f"## {number}. {title}", ""]
        out += [f"{c} {text}" for c, text in conds]
        out.append("")
    out += ["## 7. What this policy does not decide", "", NOT_DECIDED, ""]
    return "\n".join(out)


RETURNS_POLICY = {
    "document": "Returns Policy", "version": "3.0", "owner": "Head of Customer Care", "notice": NOTICE,
    "window_days": 30, "damage_report_days": 7, "excluded_categories": EXCLUDED,
    "sections": [{"number": n, "title": t, "conditions": [{"condition": c, "text": x} for c, x in conds]} for n, t, conds in _POLICY],
    "what_the_policy_does_not_decide": NOT_DECIDED,
    "text": returns_policy_markdown(),
}

# ---------------------------------------------------------------- orders

# number, customer, placed days ago, time, method (home, next, cc), carrier or collection store, lines, promised days ago,
# delivered or collected days ago (None: not yet), status
_ORDERS = [
    ("RM-58101", 2, 46, "10:12", "home", "fern", [("CL-3301", 1)], 43, 43, "delivered"),
    ("RM-58104", 11, 41, "19:30", "home", "quick", [("HW-1102", 1), ("AG-4402", 1)], 38, 39, "delivered"),
    ("RM-58108", 10, 38, "08:45", "home", "fern", [("CL-3302", 1)], 35, 35, "delivered"),
    ("RM-58112", 12, 33, "12:05", "cc", "S-104", [("TY-8801", 1)], 33, 32, "collected"),
    ("RM-58115", 13, 30, "07:50", "home", "van", [("AG-4404", 1)], 29, 29, "delivered"),
    ("RM-58118", 14, 27, "21:14", "home", "fern", [("HW-1102", 1), ("AG-4401", 1)], 24, 24, "delivered"),
    ("RM-58121", 15, 24, "16:40", "home", "quick", [("GD-9901", 1), ("AG-4403", 1)], 21, 22, "delivered"),
    ("RM-58125", 7, 22, "13:22", "home", "fern", [("HW-1103", 1)], 19, 19, "delivered"),
    ("RM-58128", 9, 20, "09:03", "home", "quick", [("GC-7702", 1)], 17, 17, "delivered"),
    ("RM-58131", 1, 17, "18:27", "home", "fern", [("HW-1101", 1)], 14, 14, "delivered"),
    ("RM-58134", 16, 15, "11:48", "cc", "S-101", [("EL-2206", 1)], 15, 14, "collected"),
    ("RM-58136", 3, 13, "20:02", "home", "van", [("CH-5501", 1), ("AG-4402", 1)], 11, 11, "delivered"),
    ("RM-58139", 17, 13, "14:36", "home", "quick", [("EL-2206", 1)], 10, 10, "delivered"),
    ("RM-58140", 4, 12, "10:55", "home", "fern", [("EL-2201", 1)], 9, 9, "delivered"),
    ("RM-58143", 5, 11, "17:19", "home", "quick", [("EL-2202", 1)], 9, 9, "delivered"),
    ("RM-58147", 6, 9, "08:31", "home", "fern", [("AG-4401", 2), ("AG-4403", 1)], 7, 7, "delivered"),
    ("RM-58150", 8, 8, "15:44", "home", "quick", [("CL-3303", 2)], 6, 6, "delivered"),
    ("RM-58152", 18, 8, "19:08", "home", "van", [("AG-4403", 1), ("AG-4404", 1)], 7, 7, "delivered"),
    ("RM-58154", 19, 7, "12:33", "home", "fern", [("PC-6601", 1), ("PC-6602", 1)], 4, 5, "delivered"),
    ("RM-58156", 13, 7, "22:10", "home", "quick", [("HW-1102", 2)], 4, 4, "delivered"),
    ("RM-58158", 12, 7, "09:26", "home", "fern", [("CL-3302", 1), ("AG-4401", 1)], 5, 5, "delivered"),
    ("RM-58160", 15, 6, "07:15", "home", "van", [("AG-4404", 1), ("CH-5501", 1), ("FZ-5601", 1)], 5, 5, "delivered"),
    ("RM-58161", 16, 7, "16:52", "home", "quick", [("EL-2206", 1), ("AG-4402", 1)], 4, None, "dispatched"),
    ("RM-58162", 24, 6, "11:07", "home", "fern", [("HW-1103", 1), ("HW-1102", 1)], 3, None, "dispatched"),
    ("RM-58163", 11, 0, "09:40", "home", "quick", [("GD-9901", 1)], -3, None, "placed"),
    ("RM-58165", 14, 2, "13:58", "cc", "S-105", [("HW-1101", 1)], 2, None, "ready_for_collection"),
    ("RM-58166", 19, 5, "18:41", "home", "fern", [("TY-8801", 1), ("CL-3303", 1)], 2, 2, "delivered"),
    ("RM-58168", 17, 4, "06:55", "home", "van", [("AG-4404", 1)], 3, 3, "delivered"),
    ("RM-58170", 18, 5, "20:25", "home", "fern", [("EL-2202", 1), ("AG-4402", 1)], 2, 3, "delivered"),
    ("RM-58172", 1, 4, "10:17", "home", "quick", [("PC-6601", 1)], 1, 1, "delivered"),
    ("RM-58174", 2, 3, "15:03", "home", "fern", [("CL-3302", 2)], 0, None, "out_for_delivery"),
    ("RM-58176", 3, 3, "09:49", "cc", "S-107", [("TY-8801", 2)], 3, 2, "collected"),
    ("RM-58178", 5, 2, "21:36", "home", "quick", [("HW-1102", 1), ("PC-6602", 1)], -1, None, "dispatched"),
    ("RM-58180", 6, 2, "07:42", "home", "van", [("AG-4404", 1), ("AG-4401", 1)], 1, 1, "delivered"),
    ("RM-58182", 7, 1, "12:11", "home", "fern", [("GD-9901", 1), ("HW-1102", 1)], -2, None, "packed"),
    ("RM-58184", 8, 1, "08:08", "home", "quick", [("EL-2201", 1)], -2, None, "dispatched"),
    ("RM-58186", 9, 1, "17:27", "cc", "S-102", [("AG-4402", 2)], 0, None, "ready_for_collection"),
    ("RM-58188", 10, 0, "08:15", "home", "van", [("AG-4404", 1)], -1, None, "placed"),
    ("RM-58190", 24, 0, "12:20", "home", "fern", [("CL-3301", 1)], -3, None, "placed"),
    ("RM-58192", 20, 0, "02:14", "next", "quick", [("EL-2203", 4)], -1, None, "awaiting_fraud_review"),
    ("RM-58194", 21, 0, "03:40", "cc", "S-108", [("EL-2204", 2)], -1, None, "awaiting_fraud_review"),
    ("RM-58196", 22, 0, "10:05", "home", "fern", [("EL-2205", 2)], -3, None, "awaiting_fraud_review"),
    ("RM-58198", 23, 0, "11:30", "home", "van", [("AG-4404", 1), ("AG-4402", 1)], -1, None, "awaiting_fraud_review"),
]
LATE_WITH_A_REASON, LATE_WITHOUT_A_REASON, LEFT_WITH_A_NEIGHBOUR = "RM-58162", "RM-58161", "RM-58166"
REFUND_NOT_PAID = "RM-58118"


def customer_id(n: int) -> str:
    return f"C-{4000 + n}"


def customer(n: int) -> dict:
    name = _SIM_NAMES.get(n) or _NAMES[n - 1]
    return {"customer_id": customer_id(n), "name": name, "email": name.lower().replace(" ", ".") + "@mail.invalid",
            "account_opened": "", "account_changes": [], "earlier_orders": []}


def scan(today: date, ago: int, time: str, place: str, text: str) -> dict:
    return {"time": f"{d_ago(today, ago)}T{time}:00", "place": place, "text": text}


def make_order(today: date, number: str, cust: dict, placed_ago: int, time: str, method: str, where: str, lines: list,
               promised_ago: int, done_ago, status: str) -> dict:
    rows = []
    for n, (sku, qty) in enumerate(lines, start=1):
        item, category, price = ITEMS[sku]
        rows.append({"line_no": n, "sku": sku, "item": item, "category": category, "quantity": qty, "unit_price": price,
                     "amount": money(qty * price)})
    goods = money(sum(x["amount"] for x in rows))
    cc = method == "cc"
    charge = 0.0 if cc else NEXT_DAY_CHARGE if method == "next" else 0.0 if goods >= FREE_DELIVERY_FROM else STANDARD_CHARGE
    total = money(goods + charge)
    placed_on = d_ago(today, placed_ago)
    depot = DEPOTS[int(cust["customer_id"][-2:]) % 3]
    carrier = "" if cc else CARRIERS[where]
    scans = []
    if not cc and status in ("dispatched", "out_for_delivery", "delivered"):
        sent = placed_ago - 1
        scans = [scan(today, sent, "09:10", CENTRE, f"Collected by {carrier} from the fulfilment centre."),
                 scan(today, sent, "20:40", depot, f"Arrived at the {depot}.")]
        if status in ("out_for_delivery", "delivered"):
            day = done_ago if done_ago is not None else promised_ago
            scans.append(scan(today, day, "07:35", depot, "Out for delivery."))
        if status == "delivered":
            scans.append(scan(today, done_ago, "13:05", "Delivery address", "Delivered. Handed to the customer at the door."))
    return {
        "order_number": number, "placed_on": placed_on, "placed_at": f"{placed_on}T{time}:00",
        "customer_id": cust["customer_id"], "customer_name": cust["name"], "customer_email": cust["email"],
        "channel": "app" if int(number[-1]) % 3 == 0 else "web", "status": status, "currency": "USD",
        "lines": rows, "goods_total": goods, "delivery_charge": charge, "total": total,
        "payment": {"method": "card", "card_ref": "CARD-1", "card_first_used_on_this_order": False, "status": "paid",
                    "charges": [{"amount": total, "charged_on": placed_on}]},
        "delivery": {"method": "click_and_collect" if cc else "home_delivery",
                     "service": "click_and_collect" if cc else "next_day" if method == "next" else "standard",
                     "carrier": carrier, "collect_site_id": where if cc else "", "collector": "the account holder" if cc else "",
                     "promised_date": d_ago(today, promised_ago),
                     "delivered_on": d_ago(today, done_ago) if done_ago is not None else None,
                     "delivered_to": "" if done_ago is None else "collected at the store" if cc else "the customer",
                     "rescheduled_date": None, "address_ref": "" if cc else "ADDR-1", "address_first_used_on_this_order": False},
        "device_ref": "DEV-1", "device_first_seen_on_this_order": False,
        "scans": scans, "refunds": [], "flag": None, "fraud_reviews": [], "fraud_decision": None,
    }


# ---------------------------------------------------------------- return requests

# id, order, sku, quantity, asked days ago, reason, condition, photo, the customer's words, then the right answer:
# proposed decision, the condition that decides, refund
_RETURNS = [
    ("01", "RM-58131", "HW-1101", 1, 6, "changed_mind", "unopened", False,
     "It is too heavy for me. It is still sealed in its box.", "approve", "1.1", 64.00),
    ("02", "RM-58101", "CL-3301", 1, 5, "changed_mind", "unopened", False,
     "I never wore the jacket. The labels are still on. I would like my money back.", "refuse", "1.2", 0.0),
    ("03", "RM-58136", "CH-5501", 1, 8, "changed_mind", "unopened", False,
     "We went away for the week and will not eat the ready meals. They are unopened.", "refuse", "3.1", 0.0),
    ("04", "RM-58140", "EL-2201", 1, 4, "changed_mind", "opened", False,
     "I used the blender once. It works, but it does not suit my kitchen.", "refuse", "2.2", 0.0),
    ("05", "RM-58143", "EL-2202", 1, 3, "faulty", "opened", False,
     "The kettle stopped heating after three uses. The light comes on and nothing happens.", "approve", "5.2", 34.50),
    ("06", "RM-58147", "AG-4401", 1, 5, "damaged_on_arrival", "opened", True,
     "One of the two bottles of olive oil was cracked and had leaked in the box. Photograph attached.", "approve", "5.1", 11.50),
    ("07", "RM-58125", "HW-1103", 1, 4, "damaged_on_arrival", "opened", True,
     "I only unpacked the dinner set this week. Two plates are chipped. Photograph attached.", "refer_to_a_person", "5.3", 0.0),
    ("08", "RM-58150", "CL-3303", 1, 2, "changed_mind", "unopened", False,
     "One pair is the wrong size for my son. He tried them on indoors and the labels are attached.", "approve", "2.3", 31.00),
    ("09", "RM-58128", "GC-7702", 1, 7, "changed_mind", "unopened", False,
     "I bought the gift card for a birthday and no longer need it.", "refuse", "3.3", 0.0),
    ("10", "RM-58108", "CL-3302", 1, 5, "changed_mind", "unopened", False,
     "The jumper has not been worn and is in its bag. I would like to send it back.", "approve", "1.1", 46.00),
]


def make_return(today: date, request_id: str, order: dict, sku: str, qty: int, asked_ago: int, reason: str, condition: str,
                photo: bool, words: str) -> dict:
    line = next(x for x in order["lines"] if x["sku"] == sku)
    return {"request_id": request_id, "order_number": order["order_number"], "customer_id": order["customer_id"],
            "customer_name": order["customer_name"], "requested_on": d_ago(today, asked_ago),
            "sku": sku, "item": line["item"], "category": line["category"], "quantity": qty,
            "quantity_bought": line["quantity"], "unit_price": line["unit_price"], "reason": reason,
            "condition_reported": condition, "photo_attached": photo, "customer_statement": words,
            "delivered_on": order["delivery"]["delivered_on"], "status": "requested", "currency": "USD",
            "assessments": [], "decided_by": "", "decided_at": None, "decision_note": ""}


# ---------------------------------------------------------------- flagged orders and the history they are read against

def history(today: date, first_number: int, totals: list, gap: int, start_ago: int, **same) -> list:
    """Earlier orders of one customer, newest first. Every row has the same device, address and card unless said."""
    rows = []
    for n, total in enumerate(totals):
        rows.append({"order_number": f"RM-{first_number - n * 37}", "placed_on": d_ago(today, start_ago + n * gap), "total": total,
                     "items": "two tablet computers" if total > 500 else "groceries and household items", "delivery_method": "home_delivery", "service": "standard",
                     "address_ref": "ADDR-1", "device_ref": "DEV-1", "card_ref": "CARD-1", "outcome": "delivered",
                     "refund": None, **same})
    return rows


def pick_till_refund(till_rows: dict, planted: dict) -> dict | None:
    """A refund at a store that is inside every till rule: it has an approver and a receipt number. Store S-101 first."""
    rows = [r for r in till_rows.values() if r["kind"] == "refund" and r["site_id"].startswith("S-") and r["approver_id"]
            and r["original_receipt"] and r["row_id"] not in planted]
    rows = [r for r in rows if r["site_id"] == "S-101"] or rows
    return sorted(rows, key=lambda r: r["row_id"])[-1] if rows else None


def flag(today: date, order: dict, reasons: list) -> None:
    order["status"] = "awaiting_fraud_review"
    order["flag"] = {"flagged_on": order["placed_on"], "reasons": reasons, "status": "awaiting_review",
                     "screening_note": "The screening rules flag an order for a person to look at. A flag is not a finding."}


def build_orders(today: date, tills: dict) -> dict:
    customers = {customer_id(n): customer(n) for n in list(range(1, 25)) + sorted(_SIM_NAMES)}
    for n, c in enumerate(customers.values()):
        c["account_opened"] = d_ago(today, 400 + n * 31)
    orders = {}
    for number, cust, placed_ago, time, method, where, lines, promised_ago, done_ago, status in _ORDERS:
        orders[number] = make_order(today, number, customers[customer_id(cust)], placed_ago, time, method, where, lines,
                                    promised_ago, done_ago, status)

    # --- three deliveries worth asking about
    o = orders[LATE_WITH_A_REASON]
    depot = o["scans"][1]["place"]
    o["scans"] = o["scans"][:2] + [
        scan(today, 3, "07:20", depot, "Held at the depot. The delivery route is closed by flooding. Delivery will be "
                                       "rescheduled."),
        scan(today, 1, "16:05", depot, f"New delivery date set: {d_ago(today, -1)}.")]
    o["delivery"]["rescheduled_date"] = d_ago(today, -1)
    o = orders[LEFT_WITH_A_NEIGHBOUR]
    o["scans"][-1] = scan(today, 2, "13:26", "Delivery address", "Delivered to a neighbour at number 14. A card was left at the "
                                                                "delivery address.")
    o["delivery"]["delivered_to"] = "a neighbour at number 14"
    orders[REFUND_NOT_PAID]["refunds"] = [{"amount": 28.00, "for": "Cotton bath towel set, returned",
                                           "approved_on": d_ago(today, 12), "paid_on": None}]
    orders[REFUND_NOT_PAID]["payment"]["status"] = "refund_approved_not_paid"

    # --- ten return requests
    month = f"{today.year % 100:02d}{today.month:02d}"
    returns, return_answers = {}, {}
    for n, number, sku, qty, asked_ago, reason, condition, photo, words, decision, decides, refund in _RETURNS:
        rid = f"RR-{month}-{n}"
        returns[rid] = make_return(today, rid, orders[number], sku, qty, asked_ago, reason, condition, photo, words)
        return_answers[rid] = {"proposed_decision": decision, "deciding_condition": decides, "refund_amount": refund}

    # --- four orders flagged for a fraud review
    till = pick_till_refund(tills["till_rows"], tills["till_planted"])
    c = customers["C-4020"]
    c["earlier_orders"] = history(today, 57940, [42.10, 58.75, 31.20, 96.40, 64.30, 47.85, 71.15, 38.90, 55.60], 19, 12)
    c["account_changes"] = [{"date": d_ago(today, 1), "change": "The email address on the account was changed."}]
    o = orders["RM-58192"]
    o.update(device_ref="DEV-2", device_first_seen_on_this_order=True)
    o["delivery"].update(address_ref="ADDR-2", address_first_used_on_this_order=True)
    flag(today, o, ["basket value above five times the customer's average", "device not seen before",
                    "delivery address not used before"])

    c = customers["C-4021"]
    c["earlier_orders"] = history(today, 57960, [35.40, 41.20, 28.75, 52.10, 44.95, 39.80, 22.60, 61.30, 47.25, 33.90, 78.00,
                                                 36.45, 29.70, 22.60], 16, 9)
    o = orders["RM-58194"]
    o["payment"].update(card_ref="CARD-2", card_first_used_on_this_order=True)
    o["delivery"]["collector"] = "someone other than the account holder"
    flag(today, o, ["basket value above five times the customer's average", "payment card not used before",
                    "first click and collect order"])

    c = customers["C-4022"]
    c["earlier_orders"] = history(today, 57975, [48.20, 605.50, 39.90, 61.75, 574.00, 44.10, 52.35, 57.30], 31, 32)
    flag(today, orders["RM-58196"], ["basket value above five times the customer's usual order"])

    c = customers["C-4023"]
    c["earlier_orders"] = history(today, 57990, [70.98, 66.40, 52.10, 81.25, 74.60, 58.90, 88.00, 63.35, 69.70, 77.15, 60.45], 14, 20)
    first = c["earlier_orders"][0]
    if till:
        first.update(placed_on=till["date"], total=money(till["amount"] + 18.40), delivery_method="click_and_collect",
                     service="click_and_collect", address_ref="", outcome="collected, then part refunded at the till",
                     refund={"where": "at the till", "site_id": till["site_id"], "till_row_id": till["row_id"],
                             "date": till["date"], "amount": till["amount"]})
    o = orders["RM-58198"]
    o.update(device_ref="DEV-2", device_first_seen_on_this_order=True)
    flag(today, o, ["device not seen before"] + (["a refund on the customer's previous order"] if till else []))

    fraud_answers = {
        "RM-58192": {"proposed_decision": "hold", "departs": ["device", "delivery_address", "basket_value", "items",
                                                              "delivery_method", "account_change"]},
        "RM-58194": {"proposed_decision": "hold", "departs": ["payment_method", "delivery_method", "basket_value", "items"]},
        "RM-58196": {"proposed_decision": "release", "departs": []},
        "RM-58198": {"proposed_decision": "release", "departs": []},
    }

    # --- the customers a simulated flagged order is read against
    customers["C-4031"]["earlier_orders"] = history(today, 57801, [44.00, 51.50, 38.25, 62.25], 21, 15)
    customers["C-4032"]["earlier_orders"] = history(today, 57811, [49.90, 590.00, 42.30, 55.80], 28, 25)
    customers["C-4033"]["earlier_orders"] = history(today, 57821, [33.10, 47.40, 29.95, 58.75, 40.80], 17, 11)
    customers["C-4034"]["earlier_orders"] = history(today, 57831, [61.20, 72.45, 66.90, 58.25, 70.20], 13, 8)
    return {"orders": orders, "customers": customers, "return_requests": returns, "return_answers": return_answers,
            "fraud_answers": fraud_answers}


# ---------------------------------------------------------------- arrivals

# What arrives with the event "return-request". Four templates, in turn. Each makes a delivered order and a request on it.
#   sku, delivered days ago, reason, condition, the customer's words; right answer in SCENARIOS.md
_SIM_RETURNS = [
    ("TY-8801", 9, "changed_mind", "unopened", "The train set is a duplicate present. The box has not been opened."),
    ("GD-9901", 41, "changed_mind", "unopened", "I never fitted the hose reel. It is still in its box."),
    ("FZ-5601", 3, "changed_mind", "unopened", "I ordered the fish by mistake and it is still in the freezer, unopened."),
    ("EL-2206", 6, "changed_mind", "opened", "I have used the toaster for a few days and would prefer a two-slice one."),
]


def sim_return(data: dict, today: date, kind: int, order_number: str, request_id: str) -> tuple[str, str]:
    sku, delivered_ago, reason, condition, words = _SIM_RETURNS[kind]
    cust = data["customers"][customer_id(1 + kind * 4)]
    order = make_order(today, order_number, cust, delivered_ago + 3, "10:00", "home", "fern", [(sku, 1)], delivered_ago,
                       delivered_ago, "delivered")
    data["orders"][order_number] = order
    data["return_requests"][request_id] = make_return(today, request_id, order, sku, 1, 0, reason, condition, False, words)
    return request_id, (f"A new return request {request_id} has arrived in the orders system. It is for order {order_number}, "
                        f"item {order['lines'][0]['item']}, delivered on {order['delivery']['delivered_on']} and asked for on "
                        f"{today.isoformat()}. Nothing has been decided. Read it with get_return_request, read the order with "
                        "get_order and the conditions with get_returns_policy.")


# What arrives with the event "flagged-order". Four templates, in turn: two that depart from the customer's pattern
# and two that the history explains.
def sim_flagged(data: dict, today: date, kind: int, order_number: str) -> tuple[str, str]:
    cust = data["customers"][customer_id(31 + kind)]
    if kind == 0:
        o = make_order(today, order_number, cust, 0, "01:50", "next", "quick", [("EL-2205", 3)], -1, None, "placed")
        o.update(device_ref="DEV-2", device_first_seen_on_this_order=True)
        o["delivery"].update(address_ref="ADDR-2", address_first_used_on_this_order=True)
        reasons = ["basket value above five times the customer's average", "device not seen before",
                   "delivery address not used before"]
    elif kind == 1:
        o = make_order(today, order_number, cust, 0, "14:20", "home", "fern", [("EL-2205", 2)], -3, None, "placed")
        reasons = ["basket value above five times the customer's usual order"]
    elif kind == 2:
        o = make_order(today, order_number, cust, 0, "04:05", "cc", "S-103", [("EL-2204", 1), ("EL-2203", 1)], -1, None, "placed")
        o["payment"].update(card_ref="CARD-2", card_first_used_on_this_order=True)
        o["delivery"]["collector"] = "someone other than the account holder"
        reasons = ["basket value above five times the customer's average", "payment card not used before",
                   "first click and collect order"]
    else:
        o = make_order(today, order_number, cust, 0, "16:45", "home", "van", [("AG-4404", 1), ("AG-4401", 1)], -1, None, "placed")
        o.update(device_ref="DEV-2", device_first_seen_on_this_order=True)
        reasons = ["device not seen before"]
    flag(today, o, reasons)
    data["orders"][order_number] = o
    return order_number, (f"Order {order_number} has been flagged for a fraud review in the orders system. It was placed on "
                          f"{today.isoformat()} for USD {o['total']:,.2f} and is waiting for a person. The screening rules gave "
                          f"{len(reasons)} reason{'s' if len(reasons) != 1 else ''}. Read it with get_order and read the "
                          "customer's earlier orders with get_customer_order_history.")
