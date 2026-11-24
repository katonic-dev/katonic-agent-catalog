"""Stock, version 1.3: stock by store and line with thirteen weeks of sales, supply terms and open orders, stock
counts with loss, and batches with where they went.

Planted, and written out below: five lines that run out before their next delivery, three lines that are
overstocked, two stores and three lines whose loss is beyond the company's tolerance, and one recalled batch that
went to four stores and seven online orders. Everything else sits inside the rules. What a careful reader should
conclude is kept in its own record set (stock_planted) and no operation serves it.
"""

from __future__ import annotations

import random
from datetime import date, timedelta

from .seed_base import d_ago, days_in, money, period_of, yymm
from .seed_range import MARKET_SUPPLIERS, NOTICE, PRODUCTS, SHARES, SKUS, STORE_IDS, split, week_endings

# ---------------------------------------------------------------- the replenishment rules, version 2.1

TARGET_COVER_DAYS, OVERSTOCK_DAYS = 14, 56
REPLENISHMENT_RULES = {
    "document": "Replenishment Rules", "version": "2.1", "owner": "Head of Supply Chain", "notice": NOTICE,
    "target_cover_days": TARGET_COVER_DAYS, "overstock_days": OVERSTOCK_DAYS,
    "rules": [
        {"rule_id": "RP-1", "title": "The forecast",
         "text": "The weekly forecast of a line is the average of its sales in the last four full weeks, all stores together. "
                 "The daily forecast is the weekly forecast divided by 7. It is a forecast, and it is written as one."},
        {"rule_id": "RP-2", "title": "Days of cover",
         "text": "Days of cover is the stock on hand in all stores together, divided by the daily forecast."},
        {"rule_id": "RP-3", "title": "A line that runs out",
         "text": "The next delivery of a line is the earliest due date among its open orders. A line with no open order has "
                 "no delivery coming: the soonest one could arrive is the retailer date plus the supplier's lead time. A "
                 "line runs out when its days of cover are fewer than the days to that date. A line whose cover is exactly "
                 "the days to that date does not run out."},
        {"rule_id": "RP-4", "title": "The quantity to order",
         "text": "For a line that runs out, the quantity is the daily forecast times the lead time plus 14 days, minus the "
                 "stock on hand, minus the units on open orders. It is rounded up to whole cases and is never fewer than "
                 "the supplier's minimum order. No order is drafted for a line that does not run out."},
        {"rule_id": "RP-5", "title": "A line that is overstocked",
         "text": "A line is overstocked when its days of cover are more than 56. No order is drafted for it. It is listed "
                 "for the buyer. A line with exactly 56 days of cover is not overstocked."},
        {"rule_id": "RP-6", "title": "Who the order goes to",
         "text": "A draft order goes to the supplier named in the line's supply terms, and to no other."},
    ],
    "what_the_rules_do_not_decide": "The rules do not place an order. A buyer approves every plan, and may change any "
                                    "quantity. The rules say nothing about a promotion, the weather or a supplier's shortage: "
                                    "the buyer weighs those.",
}

# ---------------------------------------------------------------- the stock loss tolerance, version 1.4

STORE_TOLERANCE, LINE_TOLERANCE = 1.5, 2.5
SHRINK_TOLERANCE = {
    "document": "Stock Loss Tolerance", "version": "1.4", "owner": "Head of Loss Prevention", "notice": NOTICE,
    "store_tolerance_percent": STORE_TOLERANCE, "line_tolerance_percent": LINE_TOLERANCE,
    "rules": [
        {"rule_id": "SL-1", "applies_to": "store",
         "text": "A store's loss for a period is beyond tolerance when its loss value is more than 1.5 percent of its sales "
                 "value. A store at exactly 1.5 percent is within tolerance."},
        {"rule_id": "SL-2", "applies_to": "line",
         "text": "A line's loss for a period, all counted stores together, is beyond tolerance when its loss value is more "
                 "than 2.5 percent of its sales value. A line at exactly 2.5 percent is within tolerance."},
        {"rule_id": "SL-3", "applies_to": "both",
         "text": "Loss is the units the books say should be there minus the units counted. Loss value and sales value are "
                 "both at the shelf price, tax included."},
    ],
    "what_the_tolerance_does_not_decide": "A store or a line beyond tolerance is one for the loss prevention lead to look "
                                          "into. The tolerance does not say why stock was lost: waste, damage, a counting "
                                          "error, a delivery booked in wrongly and theft all look the same in a count. It "
                                          "does not say that any colleague or any customer did anything wrong.",
}

# ---------------------------------------------------------------- the recall procedure, version 1.2

RECALL_PROCEDURE = {
    "document": "Product Recall Procedure", "version": "1.2", "owner": "Head of Quality", "notice": NOTICE,
    "steps": [
        {"step": "RC-1", "text": "List every store the batch was delivered to and every online order it was picked for. "
                                 "The batch record is the only source: an order for the same product from another batch "
                                 "is not listed."},
        {"step": "RC-2", "text": "The store instruction names the product, the batch number and the best-before date, tells "
                                 "the store to take every unit of the batch off sale at once and hold it apart, to count "
                                 "the units and report the count to the Quality team, and to send customers who bring the "
                                 "product back to the service desk for a full refund without a receipt."},
        {"step": "RC-3", "text": "The customer notice names the product, the batch number and the best-before date, says "
                                 "what the supplier has reported in the supplier's own words, tells the customer not to "
                                 "use the product, and offers a full refund without a receipt, in store or through "
                                 "customer care."},
        {"step": "RC-4", "text": "Neither text says what caused the fault, says that anyone was or was not harmed, or gives "
                                 "medical advice. A customer who feels unwell is told to speak to a doctor, and nothing more."},
        {"step": "RC-5", "text": "The Head of Quality approves every instruction and every notice before it goes out. "
                                 "Nothing is sent to a store or a customer until then."},
    ],
}

# ---------------------------------------------------------------- stock on hand and sales

# the weekly sales the last four weeks settle at, where that is not the line's usual figure
TRENDS = {"CH-5508": 350, "FZ-5603": 210, "BK-5702": 350, "DR-5903": 280, "FZ-5604": 70, "FP-5806": 140}
# stock on hand in all stores together, where it is planted
ON_HAND = {"CH-5502": 300, "CH-5505": 150, "AG-4408": 200, "FP-5802": 120, "FP-5801": 180,   # run out
           "CH-5503": 100, "AG-4410": 100,                                                   # look low and do not run out
           "HH-6105": 900, "DR-5904": 1600, "FZ-5604": 700,                                  # overstocked
           "PC-6606": 560}                                                                   # exactly 56 days
# open orders: line, reference, ordered days ago, due in days, units
_OPEN = [("FP-5801", "MO-7131", 1, 4, 360), ("CH-5503", "MO-7128", 2, 2, 480), ("AG-4405", "MO-7119", 4, 3, 1400),
         ("DR-5901", "MO-7122", 3, 4, 800), ("HH-6104", "MO-7103", 6, 4, 600), ("BK-5701", "MO-7133", 0, 1, 900)]
MINIMUM_CASES = {"SUP-303": 10, "SUP-311": 2, "SUP-317": 5}
RUN_OUT = ["AG-4408", "CH-5502", "CH-5505", "FP-5801", "FP-5802"]
OVERSTOCKED = ["DR-5904", "FZ-5604", "HH-6105"]


def _weekly_totals(sku: str) -> list[int]:
    """Thirteen weekly totals for a line, oldest first. The last four weeks of a planted line are exact."""
    base = PRODUCTS[sku]["weekly_units"]
    if sku in TRENDS:
        end = TRENDS[sku]
        return [base] * 4 + [round(base + (end - base) * n / 6) for n in range(1, 6)] + [end] * 4
    return [base] * 13


def _levels() -> dict:
    out = {}
    for sku in SKUS:
        p = PRODUCTS[sku]
        rng = random.Random(f"stock-{sku}")
        totals = _weekly_totals(sku)
        by_store = {s: [] for s in STORE_IDS}
        for n, total in enumerate(totals):
            shares = split(total)
            for s in STORE_IDS:
                noisy = sku not in TRENDS and (n < 9 or sku not in ON_HAND)
                by_store[s].append(max(0, round(shares[s] * rng.uniform(0.93, 1.07))) if noisy else shares[s])
        last4 = sum(sum(by_store[s][-4:]) for s in STORE_IDS) / 4
        on_hand = ON_HAND.get(sku) or round(last4 / 7 * rng.uniform(15, 40))
        held = split(on_hand)
        out[sku] = {"sku": sku, "name": p["name"], "category": p["category"],
                    "by_store": {s: {"on_hand": held[s], "weekly_sales": by_store[s]} for s in STORE_IDS}}
    return out


def _terms(today: date) -> dict:
    out = {}
    for sku in SKUS:
        p = PRODUCTS[sku]
        name, lead, in_purchasing = MARKET_SUPPLIERS[p["supplier_id"]]
        out[sku] = {"sku": sku, "name": p["name"], "supplier_id": p["supplier_id"], "supplier_name": name,
                    "supplier_in_purchasing": in_purchasing, "lead_time_days": lead, "case_size": p["case_size"],
                    "minimum_order_cases": MINIMUM_CASES.get(p["supplier_id"], 1), "open_orders": []}
    for sku, ref, ordered_ago, due_in, units in _OPEN:
        out[sku]["open_orders"].append({"order_ref": ref, "ordered_on": d_ago(today, ordered_ago),
                                        "due_on": (today + timedelta(days=due_in)).isoformat(), "units": units})
    return out


def line_position(level: dict, terms: dict, today: date) -> dict:
    """Where one line stands under the replenishment rules. Used to check the seed and by the tests, never served."""
    on_hand = sum(x["on_hand"] for x in level["by_store"].values())
    weekly = sum(sum(x["weekly_sales"][-4:]) for x in level["by_store"].values()) / 4
    daily = weekly / 7
    cover = on_hand / daily
    on_order = sum(o["units"] for o in terms["open_orders"])
    dues = sorted(o["due_on"] for o in terms["open_orders"])
    days_to_next = (date.fromisoformat(dues[0]) - today).days if dues else terms["lead_time_days"]
    runs_out = cover < days_to_next
    cases = 0
    if runs_out:
        units = daily * (terms["lead_time_days"] + TARGET_COVER_DAYS) - on_hand - on_order
        cases = max(-(-int(round(units)) // terms["case_size"]), terms["minimum_order_cases"])
    return {"sku": level["sku"], "on_hand": on_hand, "weekly_forecast": round(weekly, 1), "daily_forecast": round(daily, 2),
            "days_of_cover": round(cover, 1), "on_order": on_order, "days_to_next_delivery": days_to_next,
            "runs_out": runs_out, "overstocked": cover > OVERSTOCK_DAYS, "cases": cases, "units": cases * terms["case_size"],
            "supplier_id": terms["supplier_id"]}


# ---------------------------------------------------------------- stock counts and loss

LOSS_STORES, NEAR_STORE = {"S-103", "S-106"}, "S-102"
LOSS_LINES = ["DR-5905", "HH-6105", "PC-6604"]


def count_id(period: str, site_id: str) -> str:
    return f"SC-{yymm(period)}-{site_id[2:]}"


def make_count(cid: str, site_id: str, period: str, counted_on: str, rows: list) -> dict:
    """rows: (sku, units sold in the period, units lost)."""
    out = []
    for sku, sold, lost in rows:
        p = PRODUCTS[sku]
        counted = max(4, round(sold / 4))
        out.append({"sku": sku, "name": p["name"], "category": p["category"], "units_sold": sold,
                    "sales_value": money(sold * p["price"]), "book_units": counted + lost, "counted_units": counted,
                    "loss_units": lost, "loss_value": money(lost * p["price"])})
    sales, loss = money(sum(x["sales_value"] for x in out)), money(sum(x["loss_value"] for x in out))
    return {"count_id": cid, "site_id": site_id, "period": period, "counted_on": counted_on, "lines_counted": len(out),
            "sales_value": sales, "loss_units": sum(x["loss_units"] for x in out), "loss_value": loss,
            "loss_percent": round(loss / sales * 100 + 1e-9, 2), "rows": out}


def _counts(today: date) -> dict:
    period = period_of(today)
    days = days_in(period)
    counted_on = f"{period}-{days:02d}"
    out = {}
    for site in STORE_IDS:
        rows = []
        for sku in SKUS:
            rng = random.Random(f"count-{sku}-{site}")
            sold = round(PRODUCTS[sku]["weekly_units"] * SHARES[site] / 70 * days / 7)
            if sku in LOSS_LINES:
                rate = rng.uniform(0.045, 0.075)
            elif site in LOSS_STORES:
                rate = rng.uniform(0.014, 0.030)
            elif site == NEAR_STORE:
                rate = rng.uniform(0.008, 0.014)
            else:
                rate = rng.uniform(0.0, 0.011)
            rows.append((sku, sold, round(sold * rate)))
        cid = count_id(period, site)
        out[cid] = make_count(cid, site, period, counted_on, rows)
    return out


def loss_by_line(counts: list) -> dict:
    """Loss by line over the counts given, all stores together."""
    out = {}
    for c in counts:
        for r in c["rows"]:
            x = out.setdefault(r["sku"], {"sku": r["sku"], "name": r["name"], "category": r["category"], "units_sold": 0,
                                          "sales_value": 0.0, "loss_units": 0, "loss_value": 0.0, "stores_counted": 0})
            x["units_sold"] += r["units_sold"]
            x["sales_value"] = money(x["sales_value"] + r["sales_value"])
            x["loss_units"] += r["loss_units"]
            x["loss_value"] = money(x["loss_value"] + r["loss_value"])
            x["stores_counted"] += 1
    for x in out.values():
        x["loss_percent"] = round(x["loss_value"] / x["sales_value"] * 100 + 1e-9, 2) if x["sales_value"] else 0.0
    return out


# ---------------------------------------------------------------- batches

RECALLED_BATCH = "BT-44031"
# batch, line, received days ago, best before in days, at the fulfilment centre (received, picked),
# stores (site, delivered days ago, delivered, sold), online orders (order, days ago picked, units, the order line it went out as)
_BATCHES = [
    ("BT-44031", "AG-4403", 34, 300, (280, 8),
     [("S-101", 31, 240, 198), ("S-104", 31, 180, 151), ("S-105", 30, 60, 44), ("S-107", 30, 200, 163)],
     [("RM-58115", 30, 1, "AG-4404"), ("RM-58121", 24, 1, "AG-4403"), ("RM-58147", 9, 1, "AG-4403"),
      ("RM-58152", 8, 2, "AG-4403 and AG-4404"), ("RM-58160", 6, 1, "AG-4404"), ("RM-58168", 4, 1, "AG-4404"),
      ("RM-58180", 2, 1, "AG-4404")]),
    ("BT-44032", "AG-4403", 5, 330, (200, 0), [("S-102", 3, 160, 21), ("S-106", 3, 60, 9)], []),
    ("BT-44012", "AG-4401", 20, 420, (240, 1), [("S-101", 18, 180, 96), ("S-102", 18, 120, 71)],
     [("RM-58180", 2, 1, "AG-4401")]),
    ("BT-55011", "CH-5501", 15, 12, (60, 0), [("S-104", 14, 40, 31), ("S-107", 14, 48, 37), ("S-108", 13, 12, 8)], []),
]
BOX_NOTE = ("One pack of this line goes into every Weekly grocery box (AG-4404), so an order for the box is on the "
            "list when its box was packed from this batch.")
RECALL_REASON = "The supplier has reported that pieces of glass may be present in jars of this batch."


def make_batch(today: date, batch_id: str, sku: str, received_ago: int, best_before_in: int, centre: tuple, stores: list,
               orders: list, recall: dict | None) -> dict:
    p = PRODUCTS[sku]
    site_rows = [{"site_id": s, "delivered_on": d_ago(today, ago), "units_delivered": n, "units_sold": sold,
                  "units_on_hand": n - sold} for s, ago, n, sold in stores]
    order_rows = [{"order_number": o, "picked_on": d_ago(today, ago), "units": n, "went_out_as": line}
                  for o, ago, n, line in orders]
    return {"batch_id": batch_id, "sku": sku, "name": p["name"], "supplier_id": p["supplier_id"],
            "supplier_name": p["supplier_name"], "received_on": d_ago(today, received_ago),
            "best_before": (today + timedelta(days=best_before_in)).isoformat(),
            "units_received": centre[0] + sum(x["units_delivered"] for x in site_rows),
            "fulfilment_centre": {"units_received": centre[0], "units_picked_for_orders": centre[1],
                                  "units_on_hand": centre[0] - centre[1]},
            "stores": site_rows, "online_orders": order_rows,
            "note": BOX_NOTE if sku == "AG-4403" else "",
            "status": "recalled" if recall else "on_sale", "recall": recall, "recall_packs": [], "notice": None}


def make_recall(today: date, supplier_name: str, reason: str) -> dict:
    return {"raised_on": today.isoformat(), "raised_by": supplier_name, "reason": reason,
            "instruction_from_the_supplier": "Stop the sale of the batch and hold every unit for collection.",
            "customer_remedy": "A full refund without a receipt, in store or through customer care.",
            "customer_care_contact": "care@rowanmere-market.example"}


def _batches(today: date, orders: dict) -> dict:
    out = {}
    for batch_id, sku, received_ago, bb, centre, stores, order_rows in _BATCHES:
        recall = make_recall(today, PRODUCTS[sku]["supplier_name"], RECALL_REASON) if batch_id == RECALLED_BATCH else None
        b = make_batch(today, batch_id, sku, received_ago, bb, centre, stores, order_rows, recall)
        for row in b["online_orders"]:
            order = orders[row["order_number"]]
            skus = {x["sku"] for x in order["lines"]}
            assert skus & set(row["went_out_as"].replace(" and ", " ").split()), row
            assert order["status"] in ("delivered", "collected") and row["picked_on"] >= order["placed_on"], row
        assert b["fulfilment_centre"]["units_picked_for_orders"] == sum(x["units"] for x in b["online_orders"]), batch_id
        out[batch_id] = b
    return out


# ---------------------------------------------------------------- the whole starting set

def build_stock(today: date, orders: dict) -> dict:
    levels, terms = _levels(), _terms(today)
    positions = {sku: line_position(levels[sku], terms[sku], today) for sku in SKUS}
    assert sorted(s for s, x in positions.items() if x["runs_out"]) == RUN_OUT, [s for s, x in positions.items() if x["runs_out"]]
    assert sorted(s for s, x in positions.items() if x["overstocked"]) == OVERSTOCKED
    counts = _counts(today)
    assert {c["site_id"] for c in counts.values() if c["loss_percent"] > STORE_TOLERANCE} == LOSS_STORES
    assert sorted(s for s, x in loss_by_line(list(counts.values())).items() if x["loss_percent"] > LINE_TOLERANCE) == LOSS_LINES
    planted = {"run_out": {s: {"cases": positions[s]["cases"], "units": positions[s]["units"],
                               "supplier_id": positions[s]["supplier_id"]} for s in RUN_OUT},
               "overstocked": list(OVERSTOCKED), "loss_stores": sorted(LOSS_STORES), "loss_lines": list(LOSS_LINES),
               "recalled_batch": RECALLED_BATCH}
    return {"stock_levels": levels, "stock_weeks": week_endings(today), "supply_terms": terms,
            "replenishment_plans": {"plans": [], "approval": None}, "stock_counts": counts, "shrink_analyses": {},
            "batches": _batches(today, orders), "stock_planted": planted}


# ---------------------------------------------------------------- what arrives

# The orders of the first two templates are on no other batch record, so a unit is never on two batches.
# recalled-batch. Four templates, in turn: line, best before in days, fulfilment centre (received, picked), stores, orders, reason
_SIM_RECALLS = [
    ("AG-4401", 400, (120, 3), [("S-103", 12, 60, 22), ("S-108", 12, 48, 17)],
     [("RM-58147", 9, 2, "AG-4401"), ("RM-58158", 7, 1, "AG-4401")],
     "The supplier has reported that the bottles of this batch may not be sealed."),
    ("CH-5501", 9, (40, 2), [("S-101", 6, 36, 20), ("S-102", 6, 24, 15), ("S-105", 5, 12, 5)],
     [("RM-58136", 13, 1, "CH-5501"), ("RM-58160", 6, 1, "CH-5501")],
     "The supplier has reported that milk is not named on the label of this batch."),
    ("FZ-5601", 200, (0, 0), [("S-107", 8, 90, 34)], [],
     "The supplier has reported that this batch may have thawed in transit."),
    ("AG-4402", 250, (60, 3), [], [("RM-58170", 5, 1, "AG-4402"), ("RM-58186", 1, 2, "AG-4402")],
     "The supplier has reported that small stones may be present in bags of this batch."),
]


def sim_recall(data: dict, today: date, kind: int, batch_id: str) -> tuple[str, str]:
    sku, bb, centre, stores, orders, reason = _SIM_RECALLS[kind]
    recall = make_recall(today, PRODUCTS[sku]["supplier_name"], reason)
    b = make_batch(today, batch_id, sku, 16, bb, centre, stores, orders, recall)
    data["batches"][batch_id] = b
    return batch_id, (f"Batch {batch_id} of {b['name']} ({sku}) has been recalled by {b['supplier_name']} and the recall has "
                      f"arrived in the stock system. The batch went to {len(stores)} stores and {len(orders)} online orders. "
                      "No recall pack has been drafted and no notice has been issued. Read where it went with "
                      "get_batch_trace.")


# stock-count. Four templates, in turn: a store, and the lines counted as (sku, units sold, units lost).
_SIM_COUNTS = [
    ("S-101", [("BK-5701", 420, 3), ("BK-5702", 130, 1), ("BK-5703", 126, 1), ("BK-5704", 96, 0), ("BK-5705", 98, 1),
               ("BK-5706", 64, 0)]),
    ("S-104", [("DR-5901", 220, 5), ("DR-5902", 140, 3), ("DR-5903", 160, 4), ("DR-5905", 84, 6), ("DR-5906", 80, 5),
               ("DR-5907", 110, 4)]),
    ("S-107", [("CH-5502", 360, 5), ("CH-5503", 120, 2), ("CH-5504", 150, 2), ("CH-5505", 180, 3), ("CH-5506", 210, 3),
               ("CH-5507", 240, 3)]),
    ("S-105", [("PC-6601", 12, 0), ("PC-6602", 12, 0), ("PC-6603", 24, 0), ("PC-6604", 20, 3), ("PC-6605", 36, 0),
               ("PC-6606", 12, 0)]),
]


def sim_count(data: dict, today: date, kind: int, cid: str) -> tuple[str, str]:
    site, rows = _SIM_COUNTS[kind]
    c = make_count(cid, site, today.isoformat()[:7], today.isoformat(), rows)
    data["stock_counts"][cid] = c
    return cid, (f"A stock count {cid} for store {site} has arrived in the stock system. It was counted today and covers "
                 f"{len(rows)} lines, for the period {c['period']}. No analysis has been saved on it. Read it with "
                 "list_stock_counts, and the tolerance with get_shrink_tolerance.")
