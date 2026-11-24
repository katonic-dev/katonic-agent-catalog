"""Stock, version 1.3: stock by store and line, supply terms and open orders, stock counts and loss, batches and recalls."""

from __future__ import annotations

from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..seed_range import STORE_IDS
from ..seed_stock import RECALL_PROCEDURE, REPLENISHMENT_RULES, SHRINK_TOLERANCE, loss_by_line
from ..store import now_iso

KEY = "stock"
TITLE = "Stock"
LINE = ("Stock on hand and thirteen weeks of sales by store and line, supply terms and open orders, stock counts with "
        "loss and the company's tolerance, and batches with the stores and online orders that received them.")

PERIOD_RE = r"^\d{4}-(0[1-9]|1[0-2])$"
Category = Literal["ambient_grocery", "chilled_food", "frozen_food", "bakery", "fresh_produce", "drinks", "household",
                   "personal_care"]


class PlanLine(BaseModel):
    sku: str = Field(..., min_length=1, description="The line to order, for example CH-5502.")
    supplier_id: str = Field(..., min_length=1, description="The supplier the draft order goes to, as the line's supply "
                                                            "terms name it, for example SUP-301.")
    cases: int = Field(..., gt=0, description="How many whole cases to order.")
    reason: str = Field(..., min_length=1, description="Why, in one plain sentence with the figures: stock on hand, the "
                                                       "daily forecast, days of cover and the days to the next delivery.")


class ReplenishmentPlan(BaseModel):
    lines: list[PlanLine] = Field(default_factory=list, description="One entry for each line that runs out before its next "
                                  "delivery. An empty list means no line runs out.")
    overstocked: list[str] = Field(default_factory=list, description="The line ids that are overstocked under the rules. "
                                   "No order is drafted for them.")
    summary: str = Field("", description="A short summary in plain sentences. Every forecast in it is called a forecast. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class ApproveBody(BaseModel):
    approved_by: str = Field(..., min_length=1, description="The buyer who approves the plan. Free text.")
    note: str = Field("", description="Optional note kept with the record.")


class ShrinkStore(BaseModel):
    site_id: str = Field(..., min_length=1, description="The store, for example S-106.")
    loss_percent: float = Field(..., ge=0, description="The store's loss as a percent of its sales value, as the count gives it.")
    note: str = Field("", description="What the figures show, in one plain sentence. Nothing about who or what caused it. Optional.")


class ShrinkLine(BaseModel):
    sku: str = Field(..., min_length=1, description="The line, for example PC-6604.")
    loss_percent: float = Field(..., ge=0, description="The line's loss as a percent of its sales value, all counted stores "
                                                       "together, as the counts give it.")
    note: str = Field("", description="What the figures show, in one plain sentence. Nothing about who or what caused it. Optional.")


class ShrinkAnalysis(BaseModel):
    stores_beyond_tolerance: list[ShrinkStore] = Field(default_factory=list, description="Each store whose loss is beyond "
                                                       "the store tolerance. Empty when none is.")
    lines_beyond_tolerance: list[ShrinkLine] = Field(default_factory=list, description="Each line whose loss is beyond the "
                                                     "line tolerance. Empty when none is.")
    summary: str = Field("", description="A short summary in plain sentences. It names no person and gives no cause. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class PackStore(BaseModel):
    site_id: str = Field(..., min_length=1, description="A store the batch was delivered to, for example S-104.")
    units_delivered: int = Field(..., ge=0, description="The units of the batch delivered to that store, as the batch record gives them.")


class RecallPack(BaseModel):
    stores: list[PackStore] = Field(default_factory=list, description="Every store the batch was delivered to. Empty when "
                                    "it went to no store.")
    orders: list[str] = Field(default_factory=list, description="The number of every online order the batch was picked "
                              "for, for example RM-58147. Empty when it went to no order.")
    store_instruction: str = Field(..., min_length=1, description="The instruction to the stores, as a draft. It names the "
                                   "product, the batch number and the best-before date and follows step RC-2 of the recall "
                                   "procedure.")
    customer_notice: str = Field(..., min_length=1, description="The notice to customers, as a draft. It names the product, "
                                 "the batch number and the best-before date and follows steps RC-3 and RC-4 of the recall "
                                 "procedure.")
    summary: str = Field("", description="A short summary in plain sentences. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class IssueBody(BaseModel):
    issued_by: str = Field(..., min_length=1, description="The Head of Quality, or the person acting for them, who issues "
                                                          "the instruction and the notice. Free text.")
    note: str = Field("", description="Optional note kept with the record.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds the stock of Rowanmere Market's eight stores: stock on hand and "
                                  "thirteen weeks of sales for sixty lines, each line's supplier, lead time and open orders, "
                                  "the stock counts of the last full month with the loss they found, and batches with the "
                                  "stores and online orders that received them. Saving a replenishment plan, a shrink "
                                  "analysis or a recall pack is a draft. A buyer approves a plan and the Head of Quality "
                                  "issues a recall notice.")
    st = ctx.store
    d = lambda: st.data

    def level_or_404(sku: str) -> dict:
        x = d()["stock_levels"].get(sku)
        if not x:
            raise not_found("stock line", sku, "Use list_stock_levels to find line ids. They look like CH-5502.")
        return x

    def store_or_404(site_id: str) -> None:
        if site_id not in STORE_IDS:
            raise not_found("store with stock", site_id, f"The stores are: {', '.join(STORE_IDS)}. Restaurants hold no stock here.")

    def batch_or_404(batch_id: str) -> dict:
        x = d()["batches"].get(batch_id)
        if not x:
            raise not_found("batch", batch_id, "Use list_batches to find batch ids. They look like BT-44031.")
        return x

    def count_periods() -> list[str]:
        return sorted({c["period"] for c in d()["stock_counts"].values()}, reverse=True)

    def counts_or_404(period: str) -> list[dict]:
        found = [c for c in d()["stock_counts"].values() if c["period"] == period]
        if not found:
            raise not_found("stock counts for the period", period, f"The periods with a count are {', '.join(count_periods())}.")
        return sorted(found, key=lambda c: c["count_id"])

    def level_row(x: dict, site_id: str | None) -> dict:
        stores = [site_id] if site_id else STORE_IDS
        on_hand = sum(x["by_store"][s]["on_hand"] for s in stores)
        last4 = sum(sum(x["by_store"][s]["weekly_sales"][-4:]) for s in stores)
        return {"sku": x["sku"], "name": x["name"], "category": x["category"], "on_hand": on_hand,
                "units_sold_last_four_weeks": last4, "units_sold_13_weeks": sum(sum(x["by_store"][s]["weekly_sales"]) for s in stores)}

    sku_p = Path(..., description="Line id, for example CH-5502.")
    batch_p = Path(..., description="Batch id, for example BT-44031.")
    period_p = Path(..., pattern=PERIOD_RE, description="Month as YYYY-MM, for example 2026-10.")

    # ------------------------------------------------------------ stock, sales and supply
    @reg(app, "get", "/levels", "list_stock_levels", "List stock on hand and recent sales by line",
         "List the stock of every line, in order of line id. Each row has sku, name, category, on_hand (units in stock now), "
         "units_sold_last_four_weeks (the last four full weeks together; divide by 4 for the weekly forecast and by 28 for "
         "the daily forecast) and units_sold_13_weeks. Without site_id the figures are all eight stores together. Filters "
         "are optional: site_id for one store, and category. The answer has count, retailer_date and weeks (the Sunday each "
         "of the thirteen weeks ended on, oldest first). The system works out no forecast and no days of cover: read the "
         "rules with get_replenishment_rules. An unknown site_id is refused with 404.")
    def list_stock_levels(site_id: str | None = Query(None, description="Only this store, for example S-104. Leave empty for all stores together."),
                          category: Category | None = Query(None, description="Only lines of this category.")):
        if site_id:
            store_or_404(site_id)
        rows = [level_row(x, site_id) for x in d()["stock_levels"].values() if not category or x["category"] == category]
        return listing(sorted(rows, key=lambda r: r["sku"]), retailer_date=st.settings.retailer_today.isoformat(),
                       weeks=d()["stock_weeks"], stores="all eight stores together" if not site_id else site_id)

    @reg(app, "get", "/levels/{sku}", "get_line_stock_history", "Get one line's stock and sales history by store",
         "Read one line's stock and sales in each store: sku, name, category, weeks (the Sunday each of the thirteen weeks "
         "ended on, oldest first), on_hand (all stores), weekly_units (all stores together, one figure a week, oldest first) "
         "and stores, one row for each of the eight stores with site_id, on_hand and weekly_sales (thirteen figures, oldest "
         "first). Find line ids with list_stock_levels.")
    def get_line_stock_history(sku: str = sku_p):
        x = level_or_404(sku)
        return {"sku": x["sku"], "name": x["name"], "category": x["category"], "weeks": d()["stock_weeks"],
                "on_hand": sum(s["on_hand"] for s in x["by_store"].values()),
                "weekly_units": [sum(s["weekly_sales"][n] for s in x["by_store"].values()) for n in range(13)],
                "stores": [{"site_id": site, **x["by_store"][site]} for site in STORE_IDS]}

    @reg(app, "get", "/replenishment-rules", "get_replenishment_rules", "Get the company's replenishment rules",
         "Read the company's replenishment rules: document, version, owner, target_cover_days (14), overstock_days (56), "
         "rules (each with rule_id RP-1 to RP-6, title and text) and what_the_rules_do_not_decide. The rules say how the "
         "forecast and the days of cover are worked out, when a line runs out before its next delivery, how many cases to "
         "order, and when a line is overstocked. Use them with list_stock_levels and list_supply_terms.")
    def get_replenishment_rules():
        return REPLENISHMENT_RULES

    @reg(app, "get", "/supply-terms", "list_supply_terms", "List lead times and open purchase orders by line",
         "List the supply terms of every line, in order of line id. Each row has sku, name, supplier_id, supplier_name, "
         "lead_time_days, case_size (units in a case), minimum_order_cases, open_orders (each with order_ref, ordered_on, "
         "due_on and units; empty when nothing is on order), units_on_order, supplier_in_purchasing (true when the supplier "
         "also has a record in the purchasing system) and, for those suppliers, payment_terms_days read from that record. "
         "Filters are optional: supplier_id and sku. The answer has retailer_date. An unknown sku is refused with 404.")
    def list_supply_terms(supplier_id: str | None = Query(None, description="Only lines of this supplier, for example SUP-301."),
                          sku: str | None = Query(None, description="Only this line, for example CH-5502.")):
        if sku:
            level_or_404(sku)
        suppliers = d()["suppliers"]
        rows = []
        for t in d()["supply_terms"].values():
            if (supplier_id and t["supplier_id"] != supplier_id) or (sku and t["sku"] != sku):
                continue
            held = suppliers.get(t["supplier_id"])
            rows.append({**t, "units_on_order": sum(o["units"] for o in t["open_orders"]),
                         "supplier_in_purchasing": bool(held), "payment_terms_days": held["payment_terms_days"] if held else None})
        return listing(sorted(rows, key=lambda r: r["sku"]), retailer_date=st.settings.retailer_today.isoformat())

    @reg(app, "get", "/replenishment-plan", "get_replenishment_plan", "Get the saved replenishment plans",
         "Read every replenishment plan saved, oldest first, and whether one was approved. Fields: count, plans (a list of "
         "versions, each with version, drafted_by, drafted_at, lines, draft_orders, overstocked and summary) and approval "
         "(approved_by, approved_at and the version approved; empty until a buyer approves). draft_orders groups the lines "
         "of a plan by supplier, one draft purchase order for each, with the units of each line.")
    def get_replenishment_plan():
        item = d()["replenishment_plans"]
        return {"count": len(item["plans"]), "plans": item["plans"], "approval": item["approval"]}

    @reg(app, "post", "/replenishment-plan", "save_replenishment_plan", "Save a replenishment plan with draft purchase orders (draft)",
         "Save a replenishment plan, as a draft. It places no order and changes no stock. Each call is kept as a new version "
         "with who wrote it and when. Send lines (each with sku, supplier_id, cases and reason; an empty list when no line "
         "runs out), overstocked (line ids), an optional summary and drafted_by. The answer groups the lines by supplier "
         "into draft purchase orders and works out the units from the case size. An unknown sku is refused with 404. "
         "Refused with 422: a supplier_id that is not the supplier in the line's supply terms; fewer cases than the "
         "supplier's minimum order; and a line listed twice, or listed both to order and as overstocked. The system does "
         "not check the quantities against the rules: a buyer does. Returns the saved version.")
    def save_replenishment_plan(body: ReplenishmentPlan):
        terms = d()["supply_terms"]
        seen, orders = set(), {}
        for sku in body.overstocked:
            level_or_404(sku)
        for x in body.lines:
            level_or_404(x.sku)
            t = terms[x.sku]
            if x.supplier_id != t["supplier_id"]:
                raise HTTPException(422, f"{x.sku} is not supplied by {x.supplier_id}. Nothing was saved. list_supply_terms "
                                         "names the supplier of each line.")
            if x.cases < t["minimum_order_cases"]:
                raise HTTPException(422, f"{x.sku}: {x.cases} cases is fewer than the supplier's minimum order of "
                                         f"{t['minimum_order_cases']} cases. Nothing was saved.")
            if x.sku in seen or x.sku in body.overstocked:
                raise HTTPException(422, f"{x.sku} is listed twice. Nothing was saved. A line is either ordered once or "
                                         "listed as overstocked.")
            seen.add(x.sku)
            order = orders.setdefault(x.supplier_id, {"supplier_id": x.supplier_id, "supplier_name": t["supplier_name"],
                                                      "status": "draft", "lines": []})
            order["lines"].append({"sku": x.sku, "name": t["name"], "cases": x.cases, "case_size": t["case_size"],
                                   "units": x.cases * t["case_size"]})
        if len(set(body.overstocked)) != len(body.overstocked):
            raise HTTPException(422, "A line is listed twice under overstocked. Nothing was saved.")
        payload = {"lines": [x.model_dump() for x in body.lines], "draft_orders": [orders[k] for k in sorted(orders)],
                   "overstocked": list(body.overstocked), "summary": body.summary}
        v = st.add_draft(d()["replenishment_plans"], "plans", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "approved": False}

    @reg(app, "post", "/replenishment-plan/approve", "approve_replenishment_plan", "Approve the replenishment plan (change)",
         "Approve the latest saved replenishment plan. This is a change: the plan is recorded as approved by a named buyer, "
         "and its draft purchase orders take the status approved. Needs approved_by. Refused with 409 until a plan has been "
         "saved with save_replenishment_plan, when the latest plan orders nothing, and when the latest plan is already "
         "approved. Sending an order to a supplier is outside this service.")
    def approve_replenishment_plan(body: ApproveBody):
        item = d()["replenishment_plans"]
        with st.lock:
            if not item["plans"]:
                raise conflict("No replenishment plan is saved. Nothing was changed. Use save_replenishment_plan first.")
            plan = item["plans"][-1]
            if item["approval"] and item["approval"]["version"] == plan["version"]:
                raise conflict(f"Version {plan['version']} of the plan was already approved by "
                               f"{item['approval']['approved_by']}. Nothing was changed.")
            if not plan["lines"]:
                raise conflict("The latest saved plan orders nothing, so there is nothing to approve. Nothing was changed.")
            for order in plan["draft_orders"]:
                order["status"] = "approved"
            item["approval"] = {"approved_by": body.approved_by, "approved_at": now_iso(), "version": plan["version"],
                                "note": body.note}
            st.save()
        return {"applied": True, "kind": "change", "status": "approved", "approval": item["approval"],
                "draft_orders": plan["draft_orders"]}

    # ------------------------------------------------------------ counts and loss
    @reg(app, "get", "/counts/{period}", "list_stock_counts", "List stock counts and loss for a month",
         "Read the stock counts of one month. view chooses the shape. by_store (the default): one row for each store "
         "counted, with count_id, site_id, counted_on, lines_counted, sales_value, loss_units, loss_value and loss_percent "
         "(loss value as a percent of sales value). by_line: one row for each line, all counted stores together, with sku, "
         "name, category, units_sold, sales_value, loss_units, loss_value, loss_percent and stores_counted. rows: one row "
         "for each line in each store, with site_id, sku, name, category, units_sold, sales_value, book_units (what the "
         "books say should be there), counted_units, loss_units and loss_value; filter it with site_id or sku, and page it "
         "with limit and offset. Values are US dollars at the shelf price. The answer has period, view, count and total. "
         "The system does not say which store or line is beyond tolerance: read get_shrink_tolerance. A month with no "
         "count is refused with 404.")
    def list_stock_counts(period: str = period_p,
                          view: Literal["by_store", "by_line", "rows"] = Query("by_store", description="by_store, by_line or rows."),
                          site_id: str | None = Query(None, description="Only this store, for example S-106."),
                          sku: str | None = Query(None, description="Only this line, for example PC-6604. Used with the view rows."),
                          limit: int = Query(100, ge=1, le=500, description="Most rows to return, up to 500."),
                          offset: int = Query(0, ge=0, description="How many matching rows to skip.")):
        if site_id:
            store_or_404(site_id)
        counts = [c for c in counts_or_404(period) if not site_id or c["site_id"] == site_id]
        if view == "by_store":
            rows = [{k: v for k, v in c.items() if k != "rows"} for c in counts]
        elif view == "by_line":
            rows = sorted(loss_by_line(counts).values(), key=lambda r: r["sku"])
        else:
            rows = [{"count_id": c["count_id"], "site_id": c["site_id"], **r} for c in counts for r in c["rows"]
                    if not sku or r["sku"] == sku]
        return {"period": period, "view": view, "count": len(rows[offset:offset + limit]), "total": len(rows),
                "offset": offset, "limit": limit, "items": rows[offset:offset + limit]}

    @reg(app, "get", "/shrink-tolerance", "get_shrink_tolerance", "Get the company's stock loss tolerance",
         "Read the company's tolerance for stock loss: document, version, owner, store_tolerance_percent (1.5), "
         "line_tolerance_percent (2.5), rules (each with rule_id SL-1 to SL-3, applies_to and text) and "
         "what_the_tolerance_does_not_decide. A store or a line exactly on its tolerance is within it. The tolerance says "
         "nothing about why stock was lost or about any person.")
    def get_shrink_tolerance():
        return SHRINK_TOLERANCE

    @reg(app, "get", "/counts/{period}/analysis", "get_shrink_analysis", "Get the saved shrink analyses for a month",
         "Read every shrink analysis saved for one month, oldest first. Fields: period, count and analyses, a list of "
         "versions, each with version, drafted_by, drafted_at, stores_beyond_tolerance (site_id, loss_percent, note), "
         "lines_beyond_tolerance (sku, loss_percent, note) and summary. The list is empty when nothing was saved.")
    def get_shrink_analysis(period: str = period_p):
        item = d()["shrink_analyses"].get(period, {"analyses": []})
        return {"period": period, "count": len(item["analyses"]), "analyses": item["analyses"]}

    @reg(app, "post", "/counts/{period}/analysis", "save_shrink_analysis", "Save a shrink analysis for a month (draft)",
         "Save an analysis of one month's stock loss against the tolerance, as a draft. It changes no count. Each call is "
         "kept as a new version with who wrote it and when. Send stores_beyond_tolerance (each with site_id, loss_percent "
         "and an optional note), lines_beyond_tolerance (each with sku, loss_percent and an optional note), an optional "
         "summary and drafted_by. A store with no count in the month and a line that was not counted are refused with 404. "
         "Refused with 422: a loss_percent that is not the figure the counts give for that store or line, and a store or a "
         "line listed twice. A month with no count is refused with 404. The analysis lists figures. It names no person and "
         "gives no cause: the loss prevention lead decides what to look into. Returns the saved version.")
    def save_shrink_analysis(body: ShrinkAnalysis, period: str = period_p):
        counts = counts_or_404(period)
        by_site = {c["site_id"]: c for c in counts}
        by_line = loss_by_line(counts)
        seen = set()
        for x in body.stores_beyond_tolerance:
            if x.site_id not in by_site:
                raise not_found(f"stock count in {period} for the store", x.site_id, "Nothing was saved. Use list_stock_counts.")
            if abs(x.loss_percent - by_site[x.site_id]["loss_percent"]) > 0.005:
                raise HTTPException(422, f"{x.site_id}: {x.loss_percent} is not the loss percent the count gives for the "
                                         "store. Nothing was saved. Copy it from list_stock_counts with the view by_store.")
            if x.site_id in seen:
                raise HTTPException(422, f"{x.site_id} is listed twice. Nothing was saved.")
            seen.add(x.site_id)
        for y in body.lines_beyond_tolerance:
            if y.sku not in by_line:
                raise not_found(f"line counted in {period}", y.sku, "Nothing was saved. Use list_stock_counts with the view by_line.")
            if abs(y.loss_percent - by_line[y.sku]["loss_percent"]) > 0.005:
                raise HTTPException(422, f"{y.sku}: {y.loss_percent} is not the loss percent the counts give for the line. "
                                         "Nothing was saved. Copy it from list_stock_counts with the view by_line.")
            if y.sku in seen:
                raise HTTPException(422, f"{y.sku} is listed twice. Nothing was saved.")
            seen.add(y.sku)
        payload = {"stores_beyond_tolerance": [x.model_dump() for x in body.stores_beyond_tolerance],
                   "lines_beyond_tolerance": [y.model_dump() for y in body.lines_beyond_tolerance], "summary": body.summary}
        with st.lock:
            item = d()["shrink_analyses"].setdefault(period, {"period": period, "analyses": []})
            v = st.add_draft(item, "analyses", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "period": period}

    # ------------------------------------------------------------ batches and recalls
    @reg(app, "get", "/batches", "list_batches", "List batches",
         "List batches, newest first. Each row has batch_id, sku, name, supplier_name, received_on, best_before, "
         "units_received, status (on_sale, recalled or notice_issued), stores (how many stores it was delivered to), "
         "online_orders (how many orders it was picked for) and recall_packs (how many drafts are saved). Filters are "
         "optional: sku and status. Read where a batch went with get_batch_trace.")
    def list_batches(sku: str | None = Query(None, description="Only batches of this line, for example AG-4403."),
                     status: Literal["on_sale", "recalled", "notice_issued"] | None = Query(None, description="Only batches with this status.")):
        rows = [{"batch_id": b["batch_id"], "sku": b["sku"], "name": b["name"], "supplier_name": b["supplier_name"],
                 "received_on": b["received_on"], "best_before": b["best_before"], "units_received": b["units_received"],
                 "status": b["status"], "stores": len(b["stores"]), "online_orders": len(b["online_orders"]),
                 "recall_packs": len(b["recall_packs"])}
                for b in d()["batches"].values() if (not sku or b["sku"] == sku) and (not status or b["status"] == status)]
        return listing(sorted(rows, key=lambda b: (b["received_on"], b["batch_id"]), reverse=True))

    @reg(app, "get", "/batches/{batch_id}", "get_batch_trace", "Get one batch and where it went",
         "Read one batch and where it went: batch_id, sku, name, supplier_id, supplier_name, received_on, best_before, "
         "units_received, status (on_sale, recalled or notice_issued); fulfilment_centre (units_received, "
         "units_picked_for_orders, units_on_hand); stores (each store the batch was delivered to, with site_id, "
         "delivered_on, units_delivered, units_sold and units_on_hand); online_orders (each order the batch was picked for, "
         "with order_number, picked_on, units and went_out_as, the order line or lines it went out as); note; recall "
         "(raised_on, raised_by, reason in the supplier's own words, instruction_from_the_supplier, customer_remedy and "
         "customer_care_contact; empty when the batch is not recalled); recall_procedure (the company's steps RC-1 to "
         "RC-5); recall_packs (every saved pack, each a version) and notice (who issued the notice and when, empty until "
         "it is issued). The batch record is the only list of where a batch went: an order for the same line that is not "
         "in online_orders was picked from another batch. Read an order with the orders system and a store with the "
         "stores system.")
    def get_batch_trace(batch_id: str = batch_p):
        return {**batch_or_404(batch_id), "recall_procedure": RECALL_PROCEDURE}

    @reg(app, "post", "/batches/{batch_id}/recall-pack", "save_recall_pack", "Save a recall pack for a batch (draft)",
         "Save the recall pack of one recalled batch, as a draft. It sends nothing and changes no status. Each call is kept "
         "as a new version with who wrote it and when. Send stores (each with site_id and units_delivered), orders (order "
         "numbers), store_instruction, customer_notice, an optional summary and drafted_by. An order that the orders system "
         "does not hold is refused with 404. Refused with 422: a store or an order that is not on the batch record; a pack "
         "that leaves out a store or an order on the batch record (the reply says how many are missing); units that are "
         "not the units delivered; a store or an order listed twice; and a store instruction or a customer notice that "
         "does not give the batch number. Refused with 409 when the batch is not recalled. The Head of Quality approves "
         "every instruction and notice. Returns the saved version.")
    def save_recall_pack(body: RecallPack, batch_id: str = batch_p):
        b = batch_or_404(batch_id)
        if not b["recall"]:
            raise conflict(f"Batch {batch_id} is not recalled, so there is no recall pack to prepare. Nothing was saved.")
        delivered = {s["site_id"]: s["units_delivered"] for s in b["stores"]}
        picked = {o["order_number"] for o in b["online_orders"]}
        sites = [s.site_id for s in body.stores]
        if len(set(sites)) != len(sites) or len(set(body.orders)) != len(body.orders):
            raise HTTPException(422, "A store or an order is listed twice. Nothing was saved. List each one once.")
        for s in body.stores:
            if s.site_id not in delivered:
                raise HTTPException(422, f"{s.site_id} is not a store batch {batch_id} was delivered to. Nothing was saved. "
                                         "get_batch_trace lists the stores.")
            if s.units_delivered != delivered[s.site_id]:
                raise HTTPException(422, f"{s.site_id}: {s.units_delivered} is not the units of the batch delivered to that "
                                         "store. Nothing was saved. Copy the figure from get_batch_trace.")
        for o in body.orders:
            if o not in d()["orders"]:
                raise not_found("online order", o, "Nothing was saved. get_batch_trace lists the orders the batch was picked for.")
            if o not in picked:
                raise HTTPException(422, f"Order {o} was not picked from batch {batch_id}. Nothing was saved. The batch "
                                         "record is the only list: an order for the same line came from another batch.")
        missing_stores, missing_orders = len(delivered) - len(sites), len(picked) - len(body.orders)
        if missing_stores or missing_orders:
            raise HTTPException(422, f"The pack leaves out {missing_stores} of the stores and {missing_orders} of the orders "
                                     f"on the record of batch {batch_id}. Nothing was saved. A recall pack lists every one.")
        for label, text in (("store instruction", body.store_instruction), ("customer notice", body.customer_notice)):
            if batch_id not in text:
                raise HTTPException(422, f"The {label} does not give the batch number {batch_id}. Nothing was saved.")
        payload = {"stores": [s.model_dump() for s in body.stores], "orders": list(body.orders),
                   "store_instruction": body.store_instruction, "customer_notice": body.customer_notice,
                   "summary": body.summary}
        v = st.add_draft(b, "recall_packs", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "batch_status": b["status"]}

    @reg(app, "post", "/batches/{batch_id}/recall-notice/issue", "issue_recall_notice", "Issue the recall notice of a batch (change)",
         "Issue the store instruction and the customer notice of the latest saved recall pack of one batch. This is a "
         "change: the status of the batch becomes notice_issued. Needs issued_by. Refused with 409 when the batch is not "
         "recalled, until a pack has been saved with save_recall_pack, and when the notice was already issued.")
    def issue_recall_notice(body: IssueBody, batch_id: str = batch_p):
        b = batch_or_404(batch_id)
        with st.lock:
            if b["status"] == "notice_issued":
                raise conflict(f"The recall notice of batch {batch_id} was already issued by {b['notice']['issued_by']}. "
                               "Nothing was changed.")
            if not b["recall"]:
                raise conflict(f"Batch {batch_id} is not recalled. Nothing was changed.")
            if not b["recall_packs"]:
                raise conflict(f"No recall pack is saved for batch {batch_id}. Nothing was changed. Use save_recall_pack first.")
            pack = b["recall_packs"][-1]
            b["status"] = "notice_issued"
            b["notice"] = {"issued_by": body.issued_by, "issued_at": now_iso(), "version": pack["version"],
                           "stores": len(pack["stores"]), "orders": len(pack["orders"]), "note": body.note}
            st.save()
        return {"applied": True, "kind": "change", "status": "notice_issued", "batch": b}

    return app
