"""Performance, version 1.1: restaurant sales, labour and food waste against plan and peer group."""

from __future__ import annotations

from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..seed_base import period_of
from ..seed_perf import DEPARTURE_RULES

KEY = "performance"
TITLE = "Performance"
LINE = ("Each restaurant's sales, labour cost, labour hours and food waste for a month, with its plan and its peer group, "
        "and the reviews saved on them.")

PERIOD_RE = r"^\d{4}-(0[1-9]|1[0-2])$"
FIGURES = ("sales, sales_plan, sales_against_plan_pct, labour_cost, labour_cost_plan, labour_cost_against_plan_pct, labour_hours, "
           "labour_hours_plan, labour_hours_against_plan_pct, food_waste, food_waste_plan, food_waste_against_plan_pct, "
           "labour_cost_pct_of_sales and food_waste_pct_of_sales")


class Departure(BaseModel):
    measure: Literal["sales", "labour_cost", "labour_hours", "food_waste", "labour_cost_pct_of_sales",
                     "food_waste_pct_of_sales"] = Field(
        ..., description="The figure that departs. Against plan: sales, labour_cost, labour_hours or food_waste. Against the peer "
                         "group: labour_cost_pct_of_sales or food_waste_pct_of_sales.")
    compared_with: Literal["plan", "peer_group"] = Field(..., description="What the figure is set against: plan or peer_group.")
    direction: Literal["above", "below"] = Field(..., description="Whether the restaurant's figure is above or below what it is set against.")
    actual: float = Field(..., description="The restaurant's figure, as the system gives it.")
    compared_to: float = Field(..., description="The plan figure, or the average of the other restaurants in the peer group.")
    difference_pct: float = Field(0.0, description="Against plan: how far the figure is from plan, as a percentage of plan, for "
                                                   "example -18.6. Against the peer group: leave 0 and give times_peer_average.")
    times_peer_average: float = Field(0.0, description="Against the peer group: the restaurant's percentage divided by the "
                                                       "average of the others, for example 2.0. Against plan: leave 0.")
    note: str = Field("", description="One plain sentence about the figures. Nothing about a person. Optional.")


class PerformanceReview(BaseModel):
    departures: list[Departure] = Field(default_factory=list, description="One entry for each figure that departs under the "
                                        "company's rules. An empty list means nothing departs.")
    summary: str = Field("", description="A short summary of the figures in plain sentences. No conclusion about any colleague. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds the monthly figures of the twelve restaurants: sales, labour cost, labour "
                                  "hours and food waste, each with its plan, and each restaurant's peer group. Amounts are US "
                                  "dollars. Saving a review is a draft: the area manager draws the conclusions.")
    st = ctx.store
    d = lambda: st.data

    def periods() -> list[str]:
        return sorted({x["period"] for x in d()["performance"].values()}, reverse=True)

    def figures_or_error(site_id: str, period: str) -> dict:
        site = d()["sites"].get(site_id)
        if not site:
            raise not_found("site", site_id, "Use list_sites in the stores system to find restaurant ids.")
        if site["kind"] != "restaurant":
            raise not_found("restaurant", site_id, f"{site_id} is a store. This system holds figures for restaurants only.")
        row = d()["performance"].get(f"{site_id}:{period}")
        if not row:
            if period > period_of(st.settings.retailer_today):
                raise conflict(f"The period {period} has not ended, so it has no figures yet. Nothing was changed. "
                               f"The periods with figures are {', '.join(periods())}.")
            raise not_found(f"figures for restaurant {site_id} in period", period,
                            f"The periods with figures are {', '.join(periods())}.")
        return row

    site_p = Path(..., description="Restaurant id, for example R-047.")
    period_p = Path(..., pattern=PERIOD_RE, description="Month as YYYY-MM, for example 2026-10.")

    def average(rows: list[dict], key: str) -> float:
        return round(sum(r[key] for r in rows) / len(rows), 1) if rows else 0.0

    @reg(app, "get", "/periods", "list_performance_periods", "List the months that have figures",
         "List the months that have figures, newest first. Each row has period (YYYY-MM), restaurants (how many restaurants "
         "have figures) and is_latest (true for the last full month before the retailer date). The answer also has "
         "retailer_date. Use a period from here with get_restaurant_performance.")
    def list_performance_periods():
        latest = period_of(st.settings.retailer_today)
        rows = [{"period": p, "restaurants": sum(1 for x in d()["performance"].values() if x["period"] == p),
                 "is_latest": p == latest} for p in periods()]
        return listing(rows, retailer_date=st.settings.retailer_today.isoformat())

    @reg(app, "get", "/restaurants/{site_id}/{period}", "get_restaurant_performance", "Get one restaurant's figures for a month",
         f"Read one restaurant's figures for one month, with plan: site_id, period, peer_group, currency, {FIGURES}. Each "
         "against_plan_pct is how far the figure is from its plan as a percentage of the plan; a minus sign means below plan. "
         "The two pct_of_sales figures are the cost or the waste as a percentage of the restaurant's own sales. Also "
         "departure_rules (the company's rules for when a figure departs from plan or from the peer group, and what the "
         "figures do not decide) and reviews (every saved review, each a version). A store, or a restaurant the system does "
         "not hold, answers 404. A month with no figures answers 404, and a month that has not ended answers 409. Find "
         "restaurant ids with list_sites in the stores system and months with list_performance_periods.")
    def get_restaurant_performance(site_id: str = site_p, period: str = period_p):
        row = figures_or_error(site_id, period)
        saved = d()["performance_reviews"].get(f"{site_id}:{period}", {"reviews": []})
        return {**row, "departure_rules": DEPARTURE_RULES, "reviews": saved["reviews"]}

    @reg(app, "get", "/restaurants/{site_id}/{period}/peer-group", "get_peer_group_performance",
         "Get the figures of a restaurant's peer group for a month",
         "Read the figures of the peer group one restaurant belongs to, for one month: peer_group, name, site_id (the restaurant "
         "asked about), period, members (one row for each restaurant in the group, the one asked about included, each with the "
         "same figures as get_restaurant_performance), and average_of_the_others: the average of the other restaurants in the "
         "group, the one asked about left out, for sales_against_plan_pct, labour_cost_against_plan_pct, "
         "labour_hours_against_plan_pct, food_waste_against_plan_pct, labour_cost_pct_of_sales and food_waste_pct_of_sales. "
         "The company's rule sets a restaurant's two pct_of_sales figures against average_of_the_others. Errors are as for "
         "get_restaurant_performance.")
    def get_peer_group_performance(site_id: str = site_p, period: str = period_p):
        own = figures_or_error(site_id, period)
        group = d()["peer_groups"][own["peer_group"]]
        members = [d()["performance"][f"{s}:{period}"] for s in group["site_ids"] if f"{s}:{period}" in d()["performance"]]
        others = [m for m in members if m["site_id"] != site_id]
        keys = ("sales_against_plan_pct", "labour_cost_against_plan_pct", "labour_hours_against_plan_pct",
                "food_waste_against_plan_pct", "labour_cost_pct_of_sales", "food_waste_pct_of_sales")
        return {"peer_group": group["peer_group"], "name": group["name"], "site_id": site_id, "period": period,
                "members": members, "average_of_the_others": {k: average(others, k) for k in keys}}

    @reg(app, "post", "/restaurants/{site_id}/{period}/review", "save_performance_review",
         "Save the review of a restaurant's month (draft)",
         "Save a review of one restaurant's figures for one month, as a draft. It changes no figure. Each call is kept as a new "
         "version with who wrote it and when. Send departures (each with measure, compared_with, direction, actual, "
         "compared_to, and difference_pct or times_peer_average; an empty list when nothing departs), an optional summary and "
         "drafted_by. A departure against plan names sales, labour_cost, labour_hours or food_waste. A departure against the "
         "peer group names labour_cost_pct_of_sales or food_waste_pct_of_sales. A measure that does not fit what it is "
         "compared with is refused with 422. The review lists figures. It draws no conclusion about any colleague: the area "
         "manager does that. Returns the saved version.")
    def save_performance_review(body: PerformanceReview, site_id: str = site_p, period: str = period_p):
        figures_or_error(site_id, period)
        for n, x in enumerate(body.departures, start=1):
            is_share = x.measure.endswith("_pct_of_sales")
            if (x.compared_with == "peer_group") != is_share:
                raise HTTPException(422, f"Departure {n}: {x.measure} cannot be compared with {x.compared_with}. Nothing was "
                                         "saved. Against plan use sales, labour_cost, labour_hours or food_waste. Against "
                                         "peer_group use labour_cost_pct_of_sales or food_waste_pct_of_sales.")
        with st.lock:
            item = d()["performance_reviews"].setdefault(f"{site_id}:{period}", {"site_id": site_id, "period": period, "reviews": []})
            payload = {"departures": [x.model_dump() for x in body.departures], "summary": body.summary}
            v = st.add_draft(item, "reviews", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "site_id": site_id, "period": period}

    return app
