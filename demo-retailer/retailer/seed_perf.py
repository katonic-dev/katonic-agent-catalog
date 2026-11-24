"""Performance, version 1.1: restaurant sales, labour and food waste against plan, for three months.

The plan is the same for every month's set of figures: labour cost is planned at 26 percent of planned
sales, labour hours at one hour for each USD 14.50 of planned labour cost, and food waste at 2 percent of
planned sales. What a restaurant did is its plan times a factor. Most factors sit within 3 percent of
plan. The planted cases are in PLANTED.
"""

from __future__ import annotations

import random
from datetime import date

from .seed_base import period_of
from .seed_stores import RESTAURANT_IDS

PEER_GROUPS = {
    "PG-1": ("Port Ilvane restaurants", ["R-014", "R-022", "R-058", "R-071"]),
    "PG-2": ("Marlow Reach restaurants", ["R-031", "R-063", "R-076", "R-104"]),
    "PG-3": ("Neighbourhood restaurants", ["R-047", "R-082", "R-090", "R-117"]),
}
PEER_GROUP_OF = {site: group for group, (_, sites) in PEER_GROUPS.items() for site in sites}

# planned sales for the period, in US dollars
SALES_PLAN = {"R-014": 196000, "R-022": 171000, "R-031": 158000, "R-047": 182000, "R-058": 204000, "R-063": 149000,
              "R-071": 133000, "R-076": 127000, "R-082": 141000, "R-090": 118000, "R-104": 122000, "R-117": 136000}
SEASON = [1.00, 0.96, 0.98]  # the period, the month before, the month before that
LABOUR_SHARE, HOURLY_COST, WASTE_SHARE = 0.26, 14.50, 0.02

# site -> for the period and the two months before it: (sales, labour cost, labour hours, food waste) as factors of plan
PLANTED = {
    "R-047": [(0.814, 1.085, 1.090, 1.010), (0.905, 1.045, 1.042, 0.990), (0.972, 1.012, 1.015, 1.005)],
    "R-031": [(0.991, 1.012, 1.008, 2.100), (1.004, 0.995, 0.998, 1.400), (0.997, 1.006, 1.002, 1.040)],
    "R-022": [(1.074, 0.972, 0.968, 0.880), (1.058, 0.981, 0.979, 0.910), (1.041, 0.990, 0.986, 0.960)],
}

DEPARTURE_RULES = {
    "against_plan": {"measures": ["sales", "labour_cost", "labour_hours", "food_waste"], "more_than_pct": 5.0,
                     "text": "A figure departs from plan when it is more than 5.0 percent above or below its plan. "
                             "Being ahead of plan by more than that is a departure too, and is listed as one."},
    "against_peer_group": {"measures": ["labour_cost_pct_of_sales", "food_waste_pct_of_sales"], "more_than_times": 1.5,
                           "text": "A restaurant departs from its peer group when its labour cost as a percentage of sales, or "
                                   "its food waste as a percentage of sales, is more than 1.5 times the average of the other "
                                   "restaurants in the group."},
    "what_the_figures_do_not_decide": "The figures do not say why a restaurant departs, and they say nothing about any "
                                      "colleague. The area manager draws the conclusions and agrees the actions with the "
                                      "restaurant.",
}


def pct(part: float, whole: float) -> float:
    return round(100.0 * part / whole, 1)


def against(actual: float, plan: float) -> float:
    """How far a figure is from its plan, as a percentage of the plan. Positive is above plan."""
    return round(100.0 * (actual - plan) / plan, 1) + 0.0  # + 0.0 turns -0.0 into 0.0


def figures(site_id: str, period: str, back: int) -> dict:
    rng = random.Random(f"performance-{period}-{site_id}")
    near = (rng.uniform(0.972, 1.028), rng.uniform(0.975, 1.028), rng.uniform(0.975, 1.028), rng.uniform(0.965, 1.035))
    f_sales, f_cost, f_hours, f_waste = PLANTED[site_id][back] if site_id in PLANTED else near
    sales_plan = float(round(SALES_PLAN[site_id] * SEASON[back], -2))
    cost_plan = float(round(sales_plan * LABOUR_SHARE, -1))
    hours_plan = float(round(cost_plan / HOURLY_COST))
    waste_plan = float(round(sales_plan * WASTE_SHARE, -1))
    sales = float(round(sales_plan * f_sales, -1))
    cost = float(round(cost_plan * f_cost, -1))
    hours = float(round(hours_plan * f_hours))
    waste = float(round(waste_plan * f_waste, -1))
    return {
        "site_id": site_id, "period": period, "peer_group": PEER_GROUP_OF[site_id], "currency": "USD",
        "sales": sales, "sales_plan": sales_plan, "sales_against_plan_pct": against(sales, sales_plan),
        "labour_cost": cost, "labour_cost_plan": cost_plan, "labour_cost_against_plan_pct": against(cost, cost_plan),
        "labour_hours": hours, "labour_hours_plan": hours_plan, "labour_hours_against_plan_pct": against(hours, hours_plan),
        "food_waste": waste, "food_waste_plan": waste_plan, "food_waste_against_plan_pct": against(waste, waste_plan),
        "labour_cost_pct_of_sales": pct(cost, sales), "food_waste_pct_of_sales": pct(waste, sales),
    }


def build_performance(today: date) -> dict:
    rows = {}
    for back in range(3):
        period = period_of(today, back)
        for site_id in RESTAURANT_IDS:
            rows[f"{site_id}:{period}"] = figures(site_id, period, back)
    groups = {gid: {"peer_group": gid, "name": name, "site_ids": list(sites)} for gid, (name, sites) in PEER_GROUPS.items()}
    return {"performance": rows, "peer_groups": groups, "performance_reviews": {}}
