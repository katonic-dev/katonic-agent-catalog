"""Pricing, version 1.3: the price file, competitor prices, the pricing rules, promotions, range review data and market notes."""

from __future__ import annotations

from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..seed_pricing import PRICING_RULES, RANGE_THRESHOLDS, broken_rules, price_row, sales_history_row
from ..seed_range import CATEGORIES
from ..store import now_iso

KEY = "pricing"
TITLE = "Pricing"
LINE = ("The price file with costs, two competitors' published prices, the pricing rules, promotions with plan and "
        "result, range review data with the company's thresholds, sales history by line, and the buying office's market notes.")

Category = Literal["ambient_grocery", "chilled_food", "frozen_food", "bakery", "fresh_produce", "drinks", "household",
                   "personal_care"]
PRICE_FIELDS = ("sku, name, category, price (the shelf price in US dollars, tax included), price_excluding_tax, cost (what a "
                "unit costs, without tax), margin_percent (to one decimal place) and last_changed_on")
PROMO_FIELDS = ("promotion_id, sku, name, category, mechanic, status (finished or running), start_date, end_date, days, "
                "normal_price, promotion_price, cost, profit_a_unit_at_the_normal_price, profit_a_unit_at_the_promotion_price, "
                "plan (units, sales_value, profit), result (units, sales_value, profit; empty while the promotion runs), "
                "the_14_days_before (units, sales_value, profit of the same line at the normal price), neighbouring_lines "
                "(each with sku, name, units_in_the_14_days_before, units_in_the_promotion and profit_a_unit), "
                "display_and_leaflet_cost, supplier_funding and how_the_review_adds_up")


class Recommendation(BaseModel):
    sku: str = Field(..., min_length=1, description="The line, for example DR-5901.")
    action: Literal["decrease", "increase", "hold"] = Field(
        ..., description="decrease or increase: a new price is proposed. hold: no change is proposed.")
    current_price: float = Field(..., gt=0, description="The price in the price file now.")
    proposed_price: float | None = Field(None, gt=0, description="The new price, with decrease or increase. Leave it out with hold.")
    reason: str = Field(..., min_length=1, description="Why, in one plain sentence with the figures: our price, the reference "
                                                       "price, the gap, and with a hold outside the band the rule that forbids the move.")
    rule: Literal["", "PR-1", "PR-2", "PR-3", "PR-4"] = Field(
        "", description="With a hold that a rule forces: the rule that forbids the move. Empty otherwise.")


class PriceRecommendations(BaseModel):
    recommendations: list[Recommendation] = Field(..., min_length=1, description="One entry for each line looked at. A "
                                                  "line with no published competitor price is left out.")
    summary: str = Field("", description="A short summary in plain sentences. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class ApproveBody(BaseModel):
    approved_by: str = Field(..., min_length=1, description="The merchant who approves the changes. Free text.")
    note: str = Field("", description="Optional note kept with the record.")


class Displaced(BaseModel):
    sku: str = Field(..., min_length=1, description="A neighbouring line of the promotion whose units fell, for example BK-5705.")
    units_lost: int = Field(..., gt=0, description="Its units in the 14 days before minus its units in the promotion.")


class PromotionReview(BaseModel):
    units_sold: int = Field(..., ge=0, description="The units the promoted line sold in the promotion, as the result gives them.")
    units_planned: int = Field(..., ge=0, description="The units the plan gave.")
    displaced: list[Displaced] = Field(default_factory=list, description="Each neighbouring line whose units fell. Empty "
                                       "when none fell.")
    net_effect_on_profit: float = Field(..., description="The net effect on profit in US dollars, added up as the "
                                                         "promotion's how_the_review_adds_up says. Negative when the "
                                                         "promotion lost money.")
    findings: list[str] = Field(..., min_length=1, description="What the figures show, each in one plain sentence with "
                                                               "its figures. No conclusion about what to do next.")
    summary: str = Field("", description="A short summary in plain sentences. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class BelowLine(BaseModel):
    sku: str = Field(..., min_length=1, description="A line that is below a threshold, for example HH-6105.")
    thresholds: list[Literal["RT-1", "RT-2", "RT-3"]] = Field(
        ..., min_length=1, description="The threshold or thresholds the line is below, by id: RT-1, RT-2 or RT-3.")
    note: str = Field("", description="The figures, in one plain sentence. Nothing about whether to keep the line. Optional.")


class RangePack(BaseModel):
    lines_below_thresholds: list[BelowLine] = Field(default_factory=list, description="One entry for each line of the "
                                                    "category that is below a threshold. Empty when none is.")
    summary: str = Field("", description="A short summary in plain sentences. It proposes no listing and no delisting. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class RecordPoint(BaseModel):
    sku: str = Field(..., min_length=1, description="The line the statement is about, for example CH-5508.")
    statement: str = Field(..., min_length=1, description="What the company's own records show, with the figures.")


class NotePoint(BaseModel):
    note_id: str = Field(..., min_length=1, description="The market note, for example MN-02.")
    statement: str = Field(..., min_length=1, description="What the note says, with its source.")
    in_writing: bool = Field(..., description="true when the note's source is in writing, false when it is not, as the "
                                              "market notes give it.")


class Forecast(BaseModel):
    sku: str = Field(..., min_length=1, description="The line the forecast is for.")
    statement: str = Field(..., min_length=1, description="The forecast and what it rests on. It starts with the word "
                                                          "Forecast and a colon.")


class DemandPlanNote(BaseModel):
    from_the_records: list[RecordPoint] = Field(default_factory=list, description="What the company's own sales records show.")
    from_the_market_notes: list[NotePoint] = Field(default_factory=list, description="What the market notes say. Kept "
                                                   "apart from the records.")
    forecasts: list[Forecast] = Field(default_factory=list, description="Every forecast, each marked as a forecast.")
    points_for_the_buyer: list[str] = Field(default_factory=list, description="Where the records and a note disagree, and "
                                            "anything else the buyer should weigh. No decision.")
    summary: str = Field("", description="A short summary in plain sentences. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds what Rowanmere Market's merchants work from: the prices and costs of "
                                  "sixty lines, what two competitors publish for thirty of them, the pricing rules, six "
                                  "finished promotions, range review data, thirteen weeks of sales by line and a file of "
                                  "market notes. Saving recommendations, a review, a pack or a note is a draft. A merchant "
                                  "approves every price change.")
    st = ctx.store
    d = lambda: st.data

    def price_or_404(sku: str) -> dict:
        x = d()["price_file"].get(sku)
        if not x:
            raise not_found("line in the price file", sku, "Use list_prices to find line ids. They look like DR-5901.")
        return x

    def promo_or_404(promotion_id: str) -> dict:
        x = d()["promotions"].get(promotion_id)
        if not x:
            raise not_found("promotion", promotion_id, "Use list_promotions to find promotion ids. They look like PM-3101.")
        return x

    def category_or_404(category: str) -> None:
        if category not in CATEGORIES:
            raise not_found("category", category, f"The categories are: {', '.join(CATEGORIES)}.")

    promo_p = Path(..., description="Promotion id, for example PM-3101.")
    category_p = Path(..., description="Category, for example household.")

    # ------------------------------------------------------------ prices
    @reg(app, "get", "/prices", "list_prices", "List the price file",
         f"List the price file, in order of line id. Each row has {PRICE_FIELDS}. Filters are optional: category and sku. The "
         "answer has count and retailer_date. An unknown sku is refused with 404.")
    def list_prices(category: Category | None = Query(None, description="Only lines of this category."),
                    sku: str | None = Query(None, description="Only this line, for example DR-5901.")):
        if sku:
            price_or_404(sku)
        rows = [x for x in d()["price_file"].values() if (not category or x["category"] == category) and (not sku or x["sku"] == sku)]
        return listing(sorted(rows, key=lambda x: x["sku"]), retailer_date=st.settings.retailer_today.isoformat())

    @reg(app, "get", "/competitor-prices", "list_competitor_prices", "List published competitor prices",
         "List what two competitors publish for the lines they share with us, in order of line id. Each row has sku, name, "
         "our_price and prices, a list with competitor, price and published_on. A competitor that publishes no price for a "
         "line is not in its list. A line that is not in this answer has no published competitor price. The filter sku is "
         "optional. The system works out no reference price and no gap: read get_pricing_rules.")
    def list_competitor_prices(sku: str | None = Query(None, description="Only this line, for example DR-5901.")):
        if sku:
            price_or_404(sku)
        rows = [{**x, "our_price": d()["price_file"][x["sku"]]["price"]} for x in d()["competitor_prices"].values()
                if not sku or x["sku"] == sku]
        return listing(sorted(rows, key=lambda x: x["sku"]))

    @reg(app, "get", "/rules", "get_pricing_rules", "Get the company's pricing rules",
         "Read the company's pricing rules: document, version, owner, floor_margin_percent (18.0), "
         "maximum_weekly_move_percent (10.0), band_percent (5.0), minimum_days_of_cover_for_a_reduction (14), "
         "allowed_last_digits (5 and 9), rules (each with rule_id PR-1 to PR-4, title and text), "
         "how_a_recommendation_is_worked_out (steps M-1 to M-4) and what_the_rules_do_not_decide. Rule PR-4 needs days of "
         "cover, which come from the stock system.")
    def get_pricing_rules():
        return PRICING_RULES

    @reg(app, "get", "/recommendations", "get_price_recommendations", "Get the saved price recommendations",
         "Read every set of price recommendations saved, oldest first, and whether one was approved. Fields: count, drafts "
         "(a list of versions, each with version, drafted_by, drafted_at, recommendations, changes and summary) and "
         "approval (approved_by, approved_at, the version approved and the changes made; empty until a merchant approves).")
    def get_price_recommendations():
        item = d()["price_recommendations"]
        return {"count": len(item["drafts"]), "drafts": item["drafts"], "approval": item["approval"]}

    @reg(app, "post", "/recommendations", "save_price_recommendations", "Save price recommendations (draft)",
         "Save a set of price recommendations, as a draft. It changes no price. Each call is kept as a new version with who "
         "wrote it and when. Send recommendations (each with sku, action, current_price, proposed_price, reason and rule), "
         "an optional summary and drafted_by. action is decrease, increase or hold. rule is PR-1, PR-2, PR-3 or PR-4 with a "
         "hold that a rule forces, and empty otherwise. An unknown sku is refused with 404. Refused with 422, with the "
         "reason: a line with no published competitor price; a current_price that is not the price in the price file; a "
         "decrease or an increase with no proposed_price, or one that does not go the way the action says; a hold with a "
         "proposed_price; a line listed twice; and a proposed price that breaks rule PR-1 (floor margin), PR-2 (price "
         "endings) or PR-3 (maximum weekly move). Rule PR-4 is not checked here, because this system holds no stock: the "
         "one who writes the recommendation checks it. A merchant approves every change. Returns the saved version.")
    def save_price_recommendations(body: PriceRecommendations):
        seen = set()
        for r in body.recommendations:
            row = price_or_404(r.sku)
            if r.sku not in d()["competitor_prices"]:
                raise HTTPException(422, f"{r.sku} has no published competitor price, so no recommendation is made for it. "
                                         "Nothing was saved. Leave the line out.")
            if r.sku in seen:
                raise HTTPException(422, f"{r.sku} is listed twice. Nothing was saved.")
            seen.add(r.sku)
            if abs(r.current_price - row["price"]) > 0.001:
                raise HTTPException(422, f"{r.sku}: {r.current_price} is not the price in the price file. Nothing was saved. "
                                         "Read it with list_prices.")
            if r.action == "hold":
                if r.proposed_price is not None:
                    raise HTTPException(422, f"{r.sku}: a hold proposes no price. Leave proposed_price out. Nothing was saved.")
                continue
            if r.rule:
                raise HTTPException(422, f"{r.sku}: rule goes with a hold only. Nothing was saved.")
            if r.proposed_price is None:
                raise HTTPException(422, f"{r.sku}: {r.action} needs a proposed_price. Nothing was saved.")
            if (r.action == "decrease") != (r.proposed_price < row["price"]) or r.proposed_price == row["price"]:
                raise HTTPException(422, f"{r.sku}: the proposed price {r.proposed_price} is not a {r.action} from "
                                         f"{row['price']}. Nothing was saved.")
            broken = broken_rules(row["price"], row["cost"], r.proposed_price, None)
            if broken:
                raise HTTPException(422, f"{r.sku}: the proposed price {r.proposed_price} breaks {' and '.join(broken)} of the "
                                         "pricing rules. Nothing was saved. Read get_pricing_rules. When the rules forbid the "
                                         "move, save a hold and name the rule.")
        recs = [r.model_dump() for r in body.recommendations]
        payload = {"recommendations": recs, "changes": sum(1 for r in recs if r["action"] != "hold"), "summary": body.summary}
        v = st.add_draft(d()["price_recommendations"], "drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "approved": False}

    @reg(app, "post", "/recommendations/approve", "approve_price_changes", "Approve the price changes (change)",
         "Approve the price changes of the latest saved set of recommendations. This is a change: each decrease and "
         "increase in it is written to the price file, with the retailer date as the day it changed. Needs approved_by. "
         "Refused with 409 until recommendations have been saved with save_price_recommendations, when the latest set "
         "holds no change, and when the latest set is already approved.")
    def approve_price_changes(body: ApproveBody):
        item = d()["price_recommendations"]
        with st.lock:
            if not item["drafts"]:
                raise conflict("No price recommendations are saved. Nothing was changed. Use save_price_recommendations first.")
            draft = item["drafts"][-1]
            if item["approval"] and item["approval"]["version"] == draft["version"]:
                raise conflict(f"Version {draft['version']} of the recommendations was already approved by "
                               f"{item['approval']['approved_by']}. Nothing was changed.")
            moves = [r for r in draft["recommendations"] if r["action"] != "hold"]
            if not moves:
                raise conflict("The latest saved recommendations hold no price change, so there is nothing to approve. "
                               "Nothing was changed.")
            today = st.settings.retailer_today.isoformat()
            changes = []
            for r in moves:
                old = d()["price_file"][r["sku"]]["price"]
                d()["price_file"][r["sku"]] = price_row(r["sku"], r["proposed_price"], today)
                changes.append({"sku": r["sku"], "from": old, "to": r["proposed_price"]})
            item["approval"] = {"approved_by": body.approved_by, "approved_at": now_iso(), "version": draft["version"],
                                "changes": changes, "note": body.note}
            st.save()
        return {"applied": True, "kind": "change", "status": "approved", "approval": item["approval"]}

    # ------------------------------------------------------------ promotions
    @reg(app, "get", "/promotions", "list_promotions", "List promotions",
         "List promotions, by end date. Each row has promotion_id, sku, name, mechanic, status (finished or running), "
         "start_date, end_date, planned_units, units_sold (empty while it runs) and reviews (how many drafts are saved). "
         "The filter status is optional. Read the plan and the result with get_promotion.")
    def list_promotions(status: Literal["finished", "running"] | None = Query(None, description="Only promotions with this status.")):
        rows = [{"promotion_id": p["promotion_id"], "sku": p["sku"], "name": p["name"], "mechanic": p["mechanic"],
                 "status": p["status"], "start_date": p["start_date"], "end_date": p["end_date"],
                 "planned_units": p["plan"]["units"], "units_sold": p["result"]["units"] if p["result"] else None,
                 "reviews": len(p["reviews"])} for p in d()["promotions"].values() if not status or p["status"] == status]
        return listing(sorted(rows, key=lambda p: (p["end_date"], p["promotion_id"])))

    @reg(app, "get", "/promotions/{promotion_id}", "get_promotion", "Get one promotion with its plan and result",
         f"Read one promotion: {PROMO_FIELDS}; and reviews (every saved review, each a version). Amounts are US dollars and "
         "profit is at the price without tax. The system gives no net effect and no verdict: how_the_review_adds_up says "
         "how the figures go together. Find ids with list_promotions.")
    def get_promotion(promotion_id: str = promo_p):
        return promo_or_404(promotion_id)

    @reg(app, "post", "/promotions/{promotion_id}/review", "save_promotion_review", "Save a review of a finished promotion (draft)",
         "Save a review of one finished promotion, as a draft. It changes nothing. Each call is kept as a new version with "
         "who wrote it and when. Send units_sold, units_planned, displaced (each with sku and units_lost), "
         "net_effect_on_profit, findings, an optional summary and drafted_by. Refused with 409 while the promotion is still "
         "running. Refused with 422: units_sold or units_planned that are not the figures of the record; a displaced line "
         "that is not a neighbouring line of the promotion; and units_lost that are not its units in the 14 days before "
         "minus its units in the promotion. The system does not check the net effect: the category manager does, and draws "
         "the conclusions. Returns the saved version.")
    def save_promotion_review(body: PromotionReview, promotion_id: str = promo_p):
        p = promo_or_404(promotion_id)
        if p["status"] != "finished":
            raise conflict(f"Promotion {promotion_id} is still running until {p['end_date']}, so it has no result to review. "
                           "Nothing was saved.")
        if body.units_sold != p["result"]["units"] or body.units_planned != p["plan"]["units"]:
            raise HTTPException(422, "units_sold and units_planned are not the figures of the record. Nothing was saved. Copy "
                                     "them from the result and the plan in get_promotion.")
        neighbours = {n["sku"]: n for n in p["neighbouring_lines"]}
        for x in body.displaced:
            n = neighbours.get(x.sku)
            if not n:
                raise HTTPException(422, f"{x.sku} is not a neighbouring line of promotion {promotion_id}. Nothing was saved. "
                                         f"Its neighbouring lines are: {', '.join(sorted(neighbours)) or 'none'}.")
            if x.units_lost != n["units_in_the_14_days_before"] - n["units_in_the_promotion"]:
                raise HTTPException(422, f"{x.sku}: units_lost is its units in the 14 days before minus its units in the "
                                         "promotion. Nothing was saved.")
        payload = {"units_sold": body.units_sold, "units_planned": body.units_planned,
                   "displaced": [x.model_dump() for x in body.displaced], "net_effect_on_profit": body.net_effect_on_profit,
                   "findings": list(body.findings), "summary": body.summary}
        v = st.add_draft(p, "reviews", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "promotion_status": p["status"]}

    # ------------------------------------------------------------ range review
    @reg(app, "get", "/range-review/thresholds", "get_range_review_thresholds", "Get the company's range review thresholds",
         "Read the company's thresholds for a range review: document, version, owner, thresholds (each with threshold_id "
         "RT-1 to RT-3, measure, below and text) and what_the_thresholds_do_not_decide. A line exactly on a threshold is "
         "not below it.")
    def get_range_review_thresholds():
        return RANGE_THRESHOLDS

    @reg(app, "get", "/range-review/{category}", "get_range_review_data", "Get the range review data of a category",
         "Read the range review data of one category, in order of line id. Fields: category, count, lines (each with sku, "
         "name, sales_13_weeks_units, sales_13_weeks_value, margin_percent, facings (shelf facings in all stores), "
         "sales_per_facing_per_week and availability_percent) and packs (every saved pack, each a version). The system "
         "does not say which line is below a threshold: read get_range_review_thresholds. An unknown category is refused "
         "with 404, and the reply names the eight categories.")
    def get_range_review_data(category: str = category_p):
        category_or_404(category)
        rows = sorted((x for x in d()["range_review"].values() if x["category"] == category), key=lambda x: x["sku"])
        return {"category": category, "count": len(rows), "lines": rows, "packs": d()["range_packs"][category]["packs"]}

    @reg(app, "post", "/range-review/{category}/pack", "save_range_review_pack", "Save a range review pack for a category (draft)",
         "Save the pack for the range review of one category, as a draft. It lists and delists nothing. Each call is kept "
         "as a new version with who wrote it and when. Send lines_below_thresholds (each with sku, thresholds and an "
         "optional note; an empty list when no line is below a threshold), an optional summary and drafted_by. thresholds "
         "holds ids: RT-1, RT-2 or RT-3. An unknown category or sku is refused with 404. Refused with 422: a line of "
         "another category, and a line listed twice. The buying team decides every listing and delisting. Returns the "
         "saved version.")
    def save_range_review_pack(body: RangePack, category: str = category_p):
        category_or_404(category)
        seen = set()
        for x in body.lines_below_thresholds:
            row = d()["range_review"].get(x.sku)
            if not row:
                raise not_found("line in the range review data", x.sku, "Nothing was saved. Use get_range_review_data.")
            if row["category"] != category:
                raise HTTPException(422, f"{x.sku} is in the category {row['category']}, not {category}. Nothing was saved.")
            if x.sku in seen:
                raise HTTPException(422, f"{x.sku} is listed twice. Nothing was saved. List each line once, with every "
                                         "threshold it is below.")
            seen.add(x.sku)
        payload = {"lines_below_thresholds": [x.model_dump() for x in body.lines_below_thresholds], "summary": body.summary}
        v = st.add_draft(d()["range_packs"][category], "packs", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "category": category}

    # ------------------------------------------------------------ sales history, market notes and the demand plan
    @reg(app, "get", "/sales-history", "list_line_sales_history", "List thirteen weeks of sales by line",
         "List the sales of every line in the last thirteen full weeks, all stores together, in order of line id. Each row "
         "has sku, name, category, weekly_units (thirteen figures, oldest first), units_13_weeks, "
         "average_first_four_weeks, average_last_four_weeks and change_percent (the last four weeks' average against the "
         "first four weeks' average). The answer has weeks (the Sunday each week ended on, oldest first). These are the "
         "company's own records. Filters are optional: category and sku.")
    def list_line_sales_history(category: Category | None = Query(None, description="Only lines of this category."),
                                sku: str | None = Query(None, description="Only this line, for example CH-5508.")):
        if sku:
            price_or_404(sku)
        rows = [sales_history_row(x) for x in d()["stock_levels"].values()
                if (not category or x["category"] == category) and (not sku or x["sku"] == sku)]
        return listing(sorted(rows, key=lambda x: x["sku"]), weeks=d()["stock_weeks"])

    @reg(app, "get", "/market-notes", "get_market_notes", "Get the buying office's market notes",
         "Read the buying office's file of market notes: file, notes (each with note_id, dated, source, in_writing and "
         "text) and text (the file as plain text). in_writing is false for a note that rests on a telephone call or on a "
         "source nobody can name. The notes are what other people have said. They are not the company's records and none "
         "of them has been checked.")
    def get_market_notes():
        return d()["market_notes"]

    @reg(app, "get", "/demand-plan-notes", "get_demand_plan_notes", "Get the saved demand plan notes",
         "Read every demand plan note saved, oldest first. Fields: count and notes, a list of versions, each with version, "
         "drafted_by, drafted_at, from_the_records, from_the_market_notes, forecasts, points_for_the_buyer and summary.")
    def get_demand_plan_notes():
        notes = d()["demand_notes"]["notes"]
        return {"count": len(notes), "notes": notes}

    @reg(app, "post", "/demand-plan-notes", "save_demand_plan_note", "Save a demand plan note (draft)",
         "Save a note for demand planning, as a draft. It changes nothing. Each call is kept as a new version with who "
         "wrote it and when. Send from_the_records (each with sku and statement), from_the_market_notes (each with "
         "note_id, statement and in_writing), forecasts (each with sku and statement), points_for_the_buyer, an optional "
         "summary and drafted_by. An unknown sku or note_id is refused with 404. Refused with 422: a forecast whose "
         "statement does not start with 'Forecast:'; a statement under from_the_records that starts with 'Forecast:'; an "
         "in_writing that is not what the market notes give for the note; and a note with nothing in it. Merchants decide "
         "the range. Returns the saved version.")
    def save_demand_plan_note(body: DemandPlanNote):
        notes = {n["note_id"]: n for n in d()["market_notes"]["notes"]}
        if not (body.from_the_records or body.from_the_market_notes or body.forecasts):
            raise HTTPException(422, "The note holds nothing: no record, no market note and no forecast. Nothing was saved.")
        for x in body.from_the_records:
            price_or_404(x.sku)
            if x.statement.strip().lower().startswith("forecast"):
                raise HTTPException(422, f"{x.sku}: a statement under from_the_records is what the records show, not a "
                                         "forecast. Put a forecast under forecasts. Nothing was saved.")
        for n in body.from_the_market_notes:
            if n.note_id not in notes:
                raise not_found("market note", n.note_id, "Nothing was saved. Use get_market_notes to find note ids.")
            if n.in_writing != notes[n.note_id]["in_writing"]:
                raise HTTPException(422, f"{n.note_id}: in_writing is not what the market notes give for this note. Nothing "
                                         "was saved.")
        for f in body.forecasts:
            price_or_404(f.sku)
            if not f.statement.strip().startswith("Forecast:"):
                raise HTTPException(422, f"{f.sku}: every forecast starts with 'Forecast:'. Nothing was saved.")
        payload = {"from_the_records": [x.model_dump() for x in body.from_the_records],
                   "from_the_market_notes": [x.model_dump() for x in body.from_the_market_notes],
                   "forecasts": [x.model_dump() for x in body.forecasts],
                   "points_for_the_buyer": list(body.points_for_the_buyer), "summary": body.summary}
        v = st.add_draft(d()["demand_notes"], "notes", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    return app
