"""Pricing, version 1.3: the price file, two competitors' published prices, the pricing rules, finished promotions
with plan and result, range review data with the company's thresholds, and a file of market notes.

Planted, and written out below: seven lines priced more than 5 percent away from the competitors (three changes
the rules allow and four they forbid), one promotion that sold well and lost money, one that displaced a
neighbouring line, and nine lines below a range review threshold. What a careful reader should conclude is kept
in its own record set (pricing_planted) and no operation serves it.
"""

from __future__ import annotations

import random
from datetime import date, timedelta

from .seed_base import d_ago, days_in, money, period_of
from .seed_range import CATEGORIES, NOTICE, PRODUCTS, SKUS, ex_tax, margin_percent, unit_profit

COMPETITORS = {"quarrowdale": "Quarrowdale Stores", "oxenwick": "Oxenwick Fresh"}
FLOOR_MARGIN, MAX_MOVE, BAND, MIN_COVER_DAYS = 18.0, 10.0, 5.0, 14

# ---------------------------------------------------------------- the pricing rules, version 2.0

PRICING_RULES = {
    "document": "Pricing Rules", "version": "2.0", "owner": "Head of Merchandising", "notice": NOTICE,
    "floor_margin_percent": FLOOR_MARGIN, "maximum_weekly_move_percent": MAX_MOVE, "band_percent": BAND,
    "minimum_days_of_cover_for_a_reduction": MIN_COVER_DAYS, "allowed_last_digits": [5, 9],
    "rules": [
        {"rule_id": "PR-1", "title": "Floor margin",
         "text": "No new price leaves a margin below 18.0 percent. The price without tax is the price divided by 1.15. The "
                 "margin is the price without tax minus the cost, as a percent of the price without tax, to one decimal "
                 "place. A margin of exactly 18.0 percent is allowed."},
        {"rule_id": "PR-2", "title": "Price endings",
         "text": "A new price ends in 5 or 9: the last digit of the cents is 5 or 9, as in 2.45 or 8.49."},
        {"rule_id": "PR-3", "title": "Maximum weekly move",
         "text": "A price moves by no more than 10.0 percent of the current price in one week, up or down, worked to one "
                 "decimal place. A move of exactly 10.0 percent is allowed."},
        {"rule_id": "PR-4", "title": "No reduction on a line that is running short",
         "text": "The price of a line with fewer than 14 days of stock cover is not reduced. Days of cover are the stock "
                 "on hand in all stores divided by the daily forecast, as the stock system's replenishment rules work it out."},
    ],
    "how_a_recommendation_is_worked_out": [
        {"step": "M-1", "text": "The reference price of a line is the lower of the competitors' published prices for it. A "
                                "line with no published competitor price gets no recommendation."},
        {"step": "M-2", "text": "The gap is our price minus the reference price, as a percent of the reference price, to "
                                "one decimal place. A gap within 5.0 percent either way, 5.0 included, is a hold: no change."},
        {"step": "M-3", "text": "When our price is more than 5.0 percent above the reference price, the recommendation is a "
                                "decrease to the reference price. When it is more than 5.0 percent below, the "
                                "recommendation is an increase to the reference price."},
        {"step": "M-4", "text": "When that new price would break one of the rules PR-1 to PR-4, the recommendation is a "
                                "hold and the rule is named. No other price is proposed in its place: a merchant decides."},
    ],
    "what_the_rules_do_not_decide": "The rules do not change a price. A merchant approves every change. They do not say "
                                    "what a competitor will do next, and a published price is only what the competitor "
                                    "showed on the day it was read.",
}

# sku: (Quarrowdale Stores, Oxenwick Fresh). None: that competitor publishes no price for the line.
_COMP = {
    "DR-5901": (2.49, 2.55), "HH-6102": (8.49, None), "FP-5804": (1.25, 1.29),                       # allowed
    "BK-5701": (1.49, 1.55), "PC-6604": (8.49, 8.79), "CH-5502": (2.29, 2.35), "HH-6103": (2.49, 2.59),  # forbidden
    "FZ-5602": (4.00, 4.10),                                                                         # exactly 5.0 percent
    "AG-4401": (11.49, 11.95), "AG-4402": (17.99, 18.49), "AG-4405": (1.45, 1.49), "AG-4406": (3.45, 3.59),
    "AG-4408": (1.95, 1.99), "AG-4411": (3.95, None), "CH-5504": (1.25, 1.29), "CH-5506": (1.79, 1.89),
    "CH-5507": (2.29, 2.39), "FZ-5601": (14.49, 14.95), "FZ-5604": (3.99, 3.95), "BK-5702": (1.69, 1.79),
    "BK-5703": (2.59, 2.75), "FP-5802": (1.29, 1.39), "FP-5805": (0.95, 0.99), "FP-5807": (2.29, 2.35),
    "DR-5903": (3.49, None), "DR-5905": (9.99, 9.49), "DR-5907": (5.99, 6.25), "HH-6101": (1.59, 1.69),
    "HH-6104": (4.99, 4.89), "PC-6603": (3.79, 3.99),
}
# sku: (action, new price, the rule that forbids the move)
PRICE_ANSWERS = {
    "DR-5901": ("decrease", 2.49, ""), "HH-6102": ("decrease", 8.49, ""), "FP-5804": ("increase", 1.25, ""),
    "BK-5701": ("hold", None, "PR-1"), "PC-6604": ("hold", None, "PR-3"), "CH-5502": ("hold", None, "PR-4"),
    "HH-6103": ("hold", None, "PR-3"),
}


def ends_right(price: float) -> bool:
    return int(round(price * 100)) % 10 in (5, 9)


def move_percent(current: float, new: float) -> float:
    return round((new - current) / current * 100 + (1e-9 if new >= current else -1e-9), 1)


def broken_rules(current: float, cost: float, new: float, cover_days: float | None) -> list[str]:
    """The pricing rules a new price would break. cover_days None: the stock rule is not looked at."""
    out = []
    if margin_percent(new, cost) < FLOOR_MARGIN:
        out.append("PR-1")
    if not ends_right(new):
        out.append("PR-2")
    if abs(move_percent(current, new)) > MAX_MOVE:
        out.append("PR-3")
    if cover_days is not None and new < current and cover_days < MIN_COVER_DAYS:
        out.append("PR-4")
    return out


def price_position(price: float, cost: float, published: list, cover_days: float) -> dict:
    """What the method gives for one line. Used to check the seed and by the tests, never served."""
    reference = min(published)
    gap = round((price - reference) / reference * 100 + (1e-9 if price >= reference else -1e-9), 1)
    if abs(gap) <= BAND:
        return {"reference": reference, "gap_percent": gap, "action": "hold", "new_price": None, "rule": ""}
    broken = broken_rules(price, cost, reference, cover_days)
    if broken:
        return {"reference": reference, "gap_percent": gap, "action": "hold", "new_price": None, "rule": broken[0],
                "rules": broken}
    return {"reference": reference, "gap_percent": gap, "action": "decrease" if reference < price else "increase",
            "new_price": reference, "rule": ""}


def price_row(sku: str, price: float, changed_on: str) -> dict:
    p = PRODUCTS[sku]
    return {"sku": sku, "name": p["name"], "category": p["category"], "price": price, "currency": "USD",
            "price_excluding_tax": money(ex_tax(price)), "cost": p["cost"], "margin_percent": margin_percent(price, p["cost"]),
            "last_changed_on": changed_on}


# ---------------------------------------------------------------- promotions

HOW_IT_ADDS_UP = ("Net effect on profit = the line's profit in the promotion, minus its profit in the same number of days "
                  "before, minus the profit lost on each neighbouring line whose units fell (units lost times its profit a "
                  "unit), minus the display and leaflet cost, plus the supplier's funding. Profit is at the price without tax.")
# id, line, mechanic, promotion price, first and last day of the period, planned units, units sold, units in the 14 days
# before, neighbours (line, units in the 14 days before, units in the promotion), display and leaflet cost, supplier funding
_PROMOS = [
    ("PM-3101", "FZ-5601", "25 percent off", 11.15, 10, 23, 400, 1040, 300, [("FZ-5602", 560, 548)], 250.00, 0.00),
    ("PM-3102", "BK-5703", "Reduced to 2.15", 2.15, 3, 16, 600, 640, 400, [("BK-5705", 350, 190), ("BK-5702", 520, 510)], 60.00, 0.00),
    ("PM-3103", "DR-5901", "Reduced to 2.25", 2.25, 17, 30, 900, 930, 500, [("DR-5902", 300, 295)], 80.00, 200.00),
    ("PM-3104", "HH-6102", "Reduced to 7.49", 7.49, 1, 14, 500, 290, 240, [], 40.00, 0.00),
    ("PM-3105", "AG-4402", "15 percent off", 15.65, 8, 21, 300, 345, 150, [], 120.00, 300.00),
    ("PM-3106", "CH-5506", "Reduced to 1.59", 1.59, 15, 28, 700, 700, 480, [], 0.00, 100.00),
]
SOLD_WELL_AND_LOST_MONEY, DISPLACED_A_NEIGHBOUR, RUNNING = "PM-3101", "PM-3102", "PM-3107"


def make_promotion(promo_id: str, sku: str, mechanic: str, promo_price: float, start: str, end: str, planned: int,
                   sold, before: int, neighbours: list, display: float, funding: float, status: str = "finished") -> dict:
    p = PRODUCTS[sku]
    normal, on_offer = unit_profit(p["price"], p["cost"]), unit_profit(promo_price, p["cost"])
    rows = [{"sku": n, "name": PRODUCTS[n]["name"], "units_in_the_14_days_before": b, "units_in_the_promotion": u,
             "profit_a_unit": unit_profit(PRODUCTS[n]["price"], PRODUCTS[n]["cost"])} for n, b, u in neighbours]
    result = None
    if sold is not None:
        result = {"units": sold, "sales_value": money(sold * promo_price), "profit": money(sold * on_offer)}
    return {"promotion_id": promo_id, "sku": sku, "name": p["name"], "category": p["category"], "mechanic": mechanic,
            "status": status, "start_date": start, "end_date": end, "days": 14, "normal_price": p["price"],
            "promotion_price": promo_price, "cost": p["cost"], "profit_a_unit_at_the_normal_price": normal,
            "profit_a_unit_at_the_promotion_price": on_offer,
            "plan": {"units": planned, "sales_value": money(planned * promo_price), "profit": money(planned * on_offer)},
            "result": result,
            "the_14_days_before": {"units": before, "sales_value": money(before * p["price"]), "profit": money(before * normal)},
            "neighbouring_lines": rows, "display_and_leaflet_cost": display, "supplier_funding": funding,
            "how_the_review_adds_up": HOW_IT_ADDS_UP, "reviews": []}


def promotion_answer(promo: dict) -> dict:
    """What a review of a finished promotion adds up to. Used by the tests, never served."""
    r, b = promo["result"], promo["the_14_days_before"]
    displaced = [{"sku": n["sku"], "units_lost": n["units_in_the_14_days_before"] - n["units_in_the_promotion"],
                  "profit_lost": money((n["units_in_the_14_days_before"] - n["units_in_the_promotion"]) * n["profit_a_unit"])}
                 for n in promo["neighbouring_lines"] if n["units_in_the_promotion"] < n["units_in_the_14_days_before"]]
    net = money(r["profit"] - b["profit"] - sum(x["profit_lost"] for x in displaced) - promo["display_and_leaflet_cost"]
                + promo["supplier_funding"])
    return {"units_against_plan_percent": round(r["units"] / promo["plan"]["units"] * 100, 1), "displaced": displaced,
            "net_effect_on_profit": net}


# ---------------------------------------------------------------- range review

RT_SALES, RT_MARGIN, RT_AVAILABILITY = 12.00, 20.0, 92.0
RANGE_THRESHOLDS = {
    "document": "Range Review Thresholds", "version": "3.0", "owner": "Head of Buying", "notice": NOTICE,
    "thresholds": [
        {"threshold_id": "RT-1", "measure": "sales_per_facing_per_week", "below": RT_SALES,
         "text": "A line is below this threshold when its sales value for each shelf facing, for each week, is below "
                 "USD 12.00. Exactly 12.00 is not below."},
        {"threshold_id": "RT-2", "measure": "margin_percent", "below": RT_MARGIN,
         "text": "A line is below this threshold when its margin is below 20.0 percent. Exactly 20.0 is not below."},
        {"threshold_id": "RT-3", "measure": "availability_percent", "below": RT_AVAILABILITY,
         "text": "A line is below this threshold when it was on the shelf for less than 92.0 percent of the checks in the "
                 "thirteen weeks. Exactly 92.0 is not below."},
    ],
    "what_the_thresholds_do_not_decide": "A line below a threshold is a line for the buying team to talk about. The "
                                         "thresholds do not delist anything and do not say why a line is below: the "
                                         "buying team decides every listing and delisting.",
}
_FACINGS = {"HH-6105": 48, "DR-5904": 40, "HH-6106": 24}
_AVAILABILITY = {"CH-5502": 88.5, "PC-6604": 86.0, "FZ-5605": 91.0, "DR-5907": 90.4, "CH-5505": 92.0}
BELOW = {"HH-6105": ["RT-1"], "DR-5904": ["RT-1"], "HH-6106": ["RT-1"], "BK-5701": ["RT-2"], "AG-4407": ["RT-2"],
         "FZ-5605": ["RT-2", "RT-3"], "CH-5502": ["RT-3"], "PC-6604": ["RT-3"], "DR-5907": ["RT-3"]}


def below_thresholds(row: dict) -> list[str]:
    out = []
    if row["sales_per_facing_per_week"] < RT_SALES:
        out.append("RT-1")
    if row["margin_percent"] < RT_MARGIN:
        out.append("RT-2")
    if row["availability_percent"] < RT_AVAILABILITY:
        out.append("RT-3")
    return out


def _range(levels: dict) -> dict:
    out = {}
    for sku in SKUS:
        p = PRODUCTS[sku]
        rng = random.Random(f"range-{sku}")
        units = sum(sum(x["weekly_sales"]) for x in levels[sku]["by_store"].values())
        value = money(units * p["price"])
        facings = _FACINGS.get(sku) or max(2, round(value / 13 / rng.uniform(25, 45)))
        out[sku] = {"sku": sku, "name": p["name"], "category": p["category"], "sales_13_weeks_units": units,
                    "sales_13_weeks_value": value, "margin_percent": margin_percent(p["price"], p["cost"]),
                    "facings": facings, "sales_per_facing_per_week": money(value / 13 / facings),
                    "availability_percent": _AVAILABILITY.get(sku) or round(rng.uniform(94.0, 99.5), 1)}
    return out


# ---------------------------------------------------------------- market notes

# id, days ago, source, in writing, text
_NOTES = [
    ("MN-01", 6, "The Meridia Grocer (trade paper)", True,
     "Sales of chilled soup across Meridia's grocers were up 12 percent this autumn on the autumn before."),
    ("MN-02", 6, "The Meridia Grocer (trade paper)", True,
     "Sales of frozen ready meals across Meridia's grocers fell 8 percent over the same months."),
    ("MN-03", 4, "Port Ilvane weather office, monthly outlook", True,
     "December is expected to be colder than usual in all three towns."),
    ("MN-04", 9, "Oxenwick Fresh, press notice", True,
     "Oxenwick Fresh will open a new store in Tallowby in January."),
    ("MN-05", 3, "A telephone call with a representative of Marrowby Provisions Ltd", False,
     "The representative said the cost of olive oil will rise by about 15 percent in the new year. Nothing has been "
     "received in writing."),
    ("MN-06", 12, "The Meridia Grocer (trade paper)", True,
     "Sales of cola and other sugared soft drinks fell 5 percent across Meridia's grocers over the year."),
    ("MN-07", 2, "A post on a social network, author unknown", False,
     "The post says wholemeal bread will be in short supply this winter. No source is given."),
    ("MN-08", 8, "Quarrowdale Stores, press notice", True,
     "Quarrowdale Stores has put four oat drinks under its own label on sale in all its stores."),
]
UNCONFIRMED_NOTES = ["MN-05", "MN-07"]
NOTE_AGAINST_THE_RECORDS = ("MN-02", "FZ-5603")
TREND_LINES = {"CH-5508": "rising", "FZ-5603": "rising", "BK-5702": "rising", "DR-5903": "falling", "FZ-5604": "falling",
               "FP-5806": "falling"}


def make_market_notes(today: date) -> dict:
    notes = [{"note_id": i, "dated": d_ago(today, ago), "source": source, "in_writing": written, "text": text}
             for i, ago, source, written, text in _NOTES]
    lines = ["MARKET NOTES (invented). Kept by the buying office of Rowanmere Market. Every source and figure is made up.",
             "Each line: note id | date | source | in writing or not | the note.", ""]
    lines += [f"{n['note_id']} | {n['dated']} | {n['source']} | {'in writing' if n['in_writing'] else 'not in writing'} | {n['text']}"
              for n in notes]
    return {"file": "market-notes.txt", "notice": NOTICE, "notes": notes, "text": "\n".join(lines) + "\n"}


def sales_history_row(level: dict) -> dict:
    weekly = [sum(x["weekly_sales"][n] for x in level["by_store"].values()) for n in range(13)]
    first, last = sum(weekly[:4]) / 4, sum(weekly[-4:]) / 4
    return {"sku": level["sku"], "name": level["name"], "category": level["category"], "weekly_units": weekly,
            "units_13_weeks": sum(weekly), "average_first_four_weeks": round(first, 1),
            "average_last_four_weeks": round(last, 1), "change_percent": round((last - first) / first * 100, 1)}


# ---------------------------------------------------------------- the whole starting set

def build_pricing(today: date, levels: dict, cover_days: dict) -> dict:
    period = period_of(today)
    changed = d_ago(today, 60)
    prices = {sku: price_row(sku, PRODUCTS[sku]["price"], changed) for sku in SKUS}
    assert all(x["margin_percent"] >= FLOOR_MARGIN for x in prices.values())
    published_on = d_ago(today, 1)
    comps = {}
    for sku, pair in _COMP.items():
        rows = [{"competitor": COMPETITORS[key], "price": price, "published_on": published_on}
                for key, price in zip(COMPETITORS, pair) if price is not None]
        comps[sku] = {"sku": sku, "name": PRODUCTS[sku]["name"], "our_price": PRODUCTS[sku]["price"], "prices": rows}
        got = price_position(PRODUCTS[sku]["price"], PRODUCTS[sku]["cost"], [r["price"] for r in rows], cover_days[sku])
        want = PRICE_ANSWERS.get(sku, ("hold", None, ""))
        assert (got["action"], got["new_price"], got["rule"]) == want and len(got.get("rules", [1])) == 1, (sku, got)
    assert len(comps) == 30

    def day(n: int) -> str:
        return f"{period}-{min(n, days_in(period)):02d}"

    promos = {}
    for promo_id, sku, mechanic, price, first, last, planned, sold, before, neighbours, display, funding in _PROMOS:
        promos[promo_id] = make_promotion(promo_id, sku, mechanic, price, day(first), day(last), planned, sold, before,
                                          neighbours, display, funding)
    promos[RUNNING] = make_promotion(RUNNING, "AG-4405", "Reduced to 1.25", 1.25, d_ago(today, 3),
                                     (today + timedelta(days=10)).isoformat(), 1500, None, 1400, [], 50.00, 0.00, "running")
    rows = _range(levels)
    assert {s: below_thresholds(r) for s, r in rows.items() if below_thresholds(r)} == BELOW
    history = {sku: sales_history_row(levels[sku]) for sku in SKUS}
    for sku, h in history.items():
        way = "rising" if h["change_percent"] > 20 else "falling" if h["change_percent"] < -20 else ""
        assert way == TREND_LINES.get(sku, "") and (way or abs(h["change_percent"]) < 10), (sku, h["change_percent"])
    planted = {"price_answers": {s: {"action": a, "new_price": n, "rule": r} for s, (a, n, r) in PRICE_ANSWERS.items()},
               "sold_well_and_lost_money": SOLD_WELL_AND_LOST_MONEY, "displaced_a_neighbour": DISPLACED_A_NEIGHBOUR,
               "below_thresholds": {s: list(t) for s, t in BELOW.items()}, "trend_lines": dict(TREND_LINES),
               "unconfirmed_notes": list(UNCONFIRMED_NOTES), "note_against_the_records": list(NOTE_AGAINST_THE_RECORDS)}
    return {"price_file": prices, "competitor_prices": comps, "price_recommendations": {"drafts": [], "approval": None},
            "promotions": promos, "range_review": rows, "range_packs": {c: {"category": c, "packs": []} for c in CATEGORIES},
            "market_notes": make_market_notes(today), "demand_notes": {"notes": []}, "pricing_planted": planted}


# ---------------------------------------------------------------- what arrives

# promotion-ended. Four templates, in turn: on plan and in profit, sold well and lost money, displaced a neighbour, undersold.
_SIM_PROMOS = [
    ("FP-5807", "Reduced to 1.95", 1.95, 800, 815, 520, [("FP-5805", 610, 604)], 50.00, 150.00),
    ("FZ-5604", "Reduced to 2.95", 2.95, 300, 780, 140, [], 90.00, 0.00),
    ("BK-5702", "Reduced to 1.45", 1.45, 700, 730, 560, [("BK-5701", 1800, 1490)], 40.00, 0.00),
    ("HH-6101", "Reduced to 1.35", 1.35, 900, 430, 380, [], 30.00, 0.00),
]


def sim_promotion(data: dict, today: date, kind: int, promo_id: str) -> tuple[str, str]:
    sku, mechanic, price, planned, sold, before, neighbours, display, funding = _SIM_PROMOS[kind]
    p = make_promotion(promo_id, sku, mechanic, price, d_ago(today, 14), d_ago(today, 1), planned, sold, before, neighbours,
                       display, funding)
    data["promotions"][promo_id] = p
    return promo_id, (f"Promotion {promo_id} on {p['name']} ({sku}) ended yesterday and its result has arrived in the pricing "
                      f"system. The plan was {planned} units and {sold} were sold. No review has been saved on it. Read it "
                      "with get_promotion.")
