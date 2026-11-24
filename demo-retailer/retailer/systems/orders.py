"""Orders, version 1.2: the online shop's orders, deliveries, return requests and the orders held for a fraud review."""

from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..seed_base import money
from ..seed_orders import CONDITION_IDS, RETURNS_POLICY
from ..store import now_iso

KEY = "orders"
TITLE = "Orders"
LINE = ("The online shop's orders with their deliveries and carrier scans, the return requests and the returns policy, and "
        "the orders flagged for a fraud review with each customer's earlier orders.")

ORDER_ROW = ("order_number, placed_on, customer_id, customer_name, status (placed, packed, dispatched, out_for_delivery, "
             "delivered, ready_for_collection, collected, awaiting_fraud_review, released_for_dispatch or on_hold), total in US "
             "dollars, delivery_method (home_delivery or click_and_collect), promised_date, delivered_on (empty until it is "
             "delivered or collected) and flagged (true when the order is flagged for a fraud review)")
STATUSES = Literal["placed", "packed", "dispatched", "out_for_delivery", "delivered", "ready_for_collection", "collected",
                   "awaiting_fraud_review", "released_for_dispatch", "on_hold"]
SIGNALS = Literal["device", "delivery_address", "basket_value", "payment_method", "items", "delivery_method",
                  "account_change", "earlier_refund", "other"]


class ConditionCheck(BaseModel):
    condition: str = Field(..., description="The number of a condition of the returns policy, for example 1.1 or 5.2, as "
                                            "get_returns_policy gives it.")
    result: Literal["met", "not_met", "does_not_apply"] = Field(..., description="Whether the request meets the condition.")
    note: str = Field("", description="What the request and the order show for this condition, in one plain sentence. Optional.")


class ReturnAssessment(BaseModel):
    conditions: list[ConditionCheck] = Field(..., min_length=1, description="One entry for each condition that was checked.")
    proposed_decision: Literal["approve", "refuse", "refer_to_a_person"] = Field(
        ..., description="What the drafter proposes. approve: the request meets the policy. refuse: a condition is not met. "
                         "refer_to_a_person: the policy does not decide it. A person decides.")
    refund_amount: float = Field(0.0, ge=0, description="The refund proposed, in US dollars: the price paid for the quantity "
                                                        "returned. 0 unless the proposal is approve.")
    customer_message: str = Field("", description="The message to the customer, as a draft. A person sends it. Optional.")
    summary: str = Field("", description="A short summary in plain sentences. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class Signal(BaseModel):
    signal: SIGNALS = Field(..., description="What was compared with the customer's earlier orders.")
    departs_from_pattern: bool = Field(..., description="true when this order differs from the customer's earlier orders on "
                                                        "this point, false when it is in line with them.")
    what_the_record_shows: str = Field(..., min_length=1, description="What this order shows and what the earlier orders show, "
                                                                       "in one plain sentence with the figures.")


class FraudReview(BaseModel):
    signals: list[Signal] = Field(..., min_length=1, description="One entry for each point that was compared.")
    proposed_decision: Literal["release", "hold"] = Field(
        ..., description="What the drafter proposes: release the order for dispatch, or hold it. A person decides.")
    explanation: str = Field(..., min_length=1, description="Why the order departs from the pattern, or why it does not, in "
                             "plain words. It describes the order. It says nothing about what kind of person the customer is.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class ApproveReturn(BaseModel):
    approved_by: str = Field(..., min_length=1, description="The person who approves the return. Free text.")
    note: str = Field("", description="Optional note kept with the decision.")


class RefuseReturn(BaseModel):
    refused_by: str = Field(..., min_length=1, description="The person who refuses the return. Free text.")
    reason: str = Field(..., min_length=1, description="The reason given to the customer, in plain sentences.")


class ReleaseOrder(BaseModel):
    released_by: str = Field(..., min_length=1, description="The person who releases the order. Free text.")
    note: str = Field("", description="Optional note kept with the decision.")


class HoldOrder(BaseModel):
    held_by: str = Field(..., min_length=1, description="The person who holds the order. Free text.")
    reason: str = Field(..., min_length=1, description="Why the order is held, in plain sentences.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds the orders of Rowanmere Market's online shop, their deliveries and carrier "
                                  "scans, the return requests, the returns policy and the orders flagged for a fraud review. "
                                  "A customer appears by name, id and an address ending in .invalid. Saving a return assessment "
                                  "or a fraud review is a draft. Approving or refusing a return, and releasing or holding a "
                                  "flagged order, change a record and need a named person.")
    st = ctx.store
    d = lambda: st.data
    today = lambda: st.settings.retailer_today.isoformat()

    def order_or_404(number):
        o = d()["orders"].get(number)
        if not o:
            raise not_found("order", number, "Order numbers look like RM-58162. Use search_orders to find one.")
        return o

    def return_or_404(request_id):
        r = d()["return_requests"].get(request_id)
        if not r:
            raise not_found("return request", request_id, "Use list_return_requests to find request ids.")
        return r

    def row(o: dict) -> dict:
        return {"order_number": o["order_number"], "placed_on": o["placed_on"], "customer_id": o["customer_id"],
                "customer_name": o["customer_name"], "status": o["status"], "total": o["total"], "currency": o["currency"],
                "delivery_method": o["delivery"]["method"], "promised_date": o["delivery"]["promised_date"],
                "delivered_on": o["delivery"]["delivered_on"] or "", "flagged": o["flag"] is not None}

    def flagged_or_409(o: dict) -> dict:
        if not o["flag"]:
            raise conflict(f"Order {o['order_number']} is not flagged for a fraud review. Nothing was changed. Use "
                           "list_flagged_orders to find the orders that are.")
        return o["flag"]

    order_p = Path(..., description="Order number, for example RM-58162.")
    request_p = Path(..., description="Return request id, for example RR-2611-01.")

    # ------------------------------------------------------------ orders and deliveries
    @reg(app, "get", "/orders", "search_orders", "Search orders",
         f"Search the online shop's orders, newest first. Each row has {ORDER_ROW}. Every filter is optional and the filters "
         "add up: order_number (the whole number), customer_email (the whole address on the order), customer_id and status. "
         "The answer has count (the rows returned), total (all rows that match), offset, limit and retailer_date. A home "
         "delivery is late when its promised_date is before the retailer_date and delivered_on is empty. For click and "
         "collect, promised_date is the day the order is ready at the store. Read one order with get_order.")
    def search_orders(order_number: str | None = Query(None, description="Only the order with this number, for example RM-58162."),
                      customer_email: str | None = Query(None, description="Only orders placed with this email address."),
                      customer_id: str | None = Query(None, description="Only orders of this customer, for example C-4024."),
                      status: STATUSES | None = Query(None, description="Only orders with this status."),
                      limit: int = Query(50, ge=1, le=200, description="Most rows to return, up to 200."),
                      offset: int = Query(0, ge=0, description="How many matching rows to skip.")):
        rows = [row(o) for o in d()["orders"].values()
                if (not order_number or o["order_number"] == order_number.strip().upper())
                and (not customer_email or o["customer_email"] == customer_email.strip().lower())
                and (not customer_id or o["customer_id"] == customer_id) and (not status or o["status"] == status)]
        rows.sort(key=lambda r: (r["placed_on"], r["order_number"]), reverse=True)
        return listing(rows[offset:offset + limit], total=len(rows), offset=offset, limit=limit, retailer_date=today())

    @reg(app, "get", "/orders/{order_number}", "get_order", "Get one order",
         "Read one order: order_number, placed_at, customer_id, customer_name, customer_email, channel (web or app), status, "
         "lines (line_no, sku, item, category, quantity, unit_price, amount), goods_total, delivery_charge and total in US "
         "dollars; payment (method, card_ref, card_first_used_on_this_order, status, charges, each with amount and "
         "charged_on); delivery (method, service, carrier, collect_site_id and collector for click and collect, promised_date, "
         "delivered_on, delivered_to, rescheduled_date, address_ref and address_first_used_on_this_order); device_ref and "
         "device_first_seen_on_this_order; refunds (amount, for, approved_on, paid_on); flag (flagged_on, reasons and status "
         "when the order is flagged for a fraud review, otherwise empty); fraud_reviews (every saved review, each a version); "
         "fraud_decision; scan_count and last_scan (the latest carrier scan); return_request_ids and retailer_date. An address, "
         "a device and a card appear as a reference only, such as ADDR-1. The carrier's scans are read with get_delivery_scans.")
    def get_order(order_number: str = order_p):
        o = order_or_404(order_number)
        out = {k: v for k, v in o.items() if k != "scans"}
        return {**out, "scan_count": len(o["scans"]), "last_scan": o["scans"][-1] if o["scans"] else None,
                "return_request_ids": sorted(r["request_id"] for r in d()["return_requests"].values()
                                             if r["order_number"] == order_number),
                "retailer_date": today()}

    @reg(app, "get", "/orders/{order_number}/scans", "get_delivery_scans", "Get the carrier scans of an order",
         "Read the carrier's scans for one order, oldest first: order_number, carrier, status, promised_date, delivered_on, "
         "delivered_to, rescheduled_date, retailer_date, count and scans, each with time, place and text (the carrier's own "
         "words). A click and collect order has no scans. When an order is late, the scans either say why or they do not: "
         "the text of a scan is the only explanation the record holds.")
    def get_delivery_scans(order_number: str = order_p):
        o = order_or_404(order_number)
        dl = o["delivery"]
        return {"order_number": order_number, "carrier": dl["carrier"], "status": o["status"],
                "promised_date": dl["promised_date"], "delivered_on": dl["delivered_on"], "delivered_to": dl["delivered_to"],
                "rescheduled_date": dl["rescheduled_date"], "retailer_date": today(), "count": len(o["scans"]),
                "scans": o["scans"]}

    # ------------------------------------------------------------ returns
    @reg(app, "get", "/returns-policy", "get_returns_policy", "Get the returns policy",
         "Read the returns policy: document, version, owner, window_days, damage_report_days, excluded_categories, sections "
         "(each with number, title and conditions, each condition with its number and text), "
         "what_the_policy_does_not_decide and text (the whole policy as plain text). Check a return request against the "
         "conditions as they are written here, and cite a condition by its number.")
    def get_returns_policy():
        return RETURNS_POLICY

    @reg(app, "get", "/returns", "list_return_requests", "List return requests",
         "List return requests, oldest first. Each row has request_id, order_number, customer_name, requested_on, item, "
         "category, quantity, reason (changed_mind, faulty or damaged_on_arrival), condition_reported (unopened or opened), "
         "status (requested, approved or refused) and assessments (how many are saved). Filters are optional: status and "
         "order_number. Read one with get_return_request.")
    def list_return_requests(status: Literal["requested", "approved", "refused"] | None = Query(None, description="Only requests with this status."),
                             order_number: str | None = Query(None, description="Only requests on this order, for example RM-58131.")):
        keys = ("request_id", "order_number", "customer_name", "requested_on", "item", "category", "quantity", "reason",
                "condition_reported", "status")
        rows = [{**{k: r[k] for k in keys}, "assessments": len(r["assessments"])} for r in d()["return_requests"].values()
                if (not status or r["status"] == status) and (not order_number or r["order_number"] == order_number)]
        return listing(sorted(rows, key=lambda r: (r["requested_on"], r["request_id"])))

    @reg(app, "get", "/returns/{request_id}", "get_return_request", "Get one return request",
         "Read one return request: request_id, order_number, customer_id, customer_name, requested_on, sku, item, category, "
         "quantity, quantity_bought, unit_price, reason, condition_reported, photo_attached, customer_statement (the "
         "customer's own words), delivered_on (the day the order was delivered or collected), days_since_delivery (from "
         "delivered_on to requested_on, with the day of delivery as day 0), status, assessments (every saved assessment, each "
         "a version), decided_by and decision_note. Read the order with get_order and the conditions with get_returns_policy.")
    def get_return_request(request_id: str = request_p):
        r = return_or_404(request_id)
        days = (date.fromisoformat(r["requested_on"]) - date.fromisoformat(r["delivered_on"])).days
        return {**r, "days_since_delivery": days}

    @reg(app, "post", "/returns/{request_id}/assessment", "save_return_assessment", "Save the assessment of a return request (draft)",
         "Save the assessment of one return request against the returns policy, as a draft. It changes no status and issues no "
         "refund. Each call is kept as a new version with who wrote it and when. Send conditions (each with condition, result "
         "and an optional note), proposed_decision, refund_amount, an optional customer_message, an optional summary and "
         "drafted_by. condition is the number of a condition of the policy, such as 1.1. result is met, not_met or "
         "does_not_apply. proposed_decision is approve, refuse or refer_to_a_person. A condition number the policy does not "
         "have, a refund above the price paid for the quantity returned, and a refund with a proposal other than approve are "
         "each refused with 422. A person approves or refuses. Returns the saved version.")
    def save_return_assessment(body: ReturnAssessment, request_id: str = request_p):
        r = return_or_404(request_id)
        for c in body.conditions:
            if c.condition not in CONDITION_IDS:
                raise HTTPException(422, f"{c.condition} is not a condition of the returns policy. Nothing was saved. The "
                                         f"conditions are {', '.join(CONDITION_IDS)}.")
        paid = money(r["unit_price"] * r["quantity"])
        if body.refund_amount > paid + 0.001:
            raise HTTPException(422, f"The refund {body.refund_amount:.2f} is above the price paid for the quantity returned, "
                                     f"{paid:.2f}. Nothing was saved.")
        if body.proposed_decision != "approve" and body.refund_amount > 0:
            raise HTTPException(422, f"A refund is proposed only with the decision approve. Nothing was saved. Send "
                                     f"refund_amount 0 with {body.proposed_decision}.")
        payload = {"conditions": [c.model_dump() for c in body.conditions], "proposed_decision": body.proposed_decision,
                   "refund_amount": body.refund_amount, "customer_message": body.customer_message, "summary": body.summary}
        v = st.add_draft(r, "assessments", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "request_status": r["status"]}

    def decide(request_id: str, status: str, who: str, note: str) -> dict:
        r = return_or_404(request_id)
        with st.lock:
            if r["status"] != "requested":
                raise conflict(f"Return request {request_id} is already {r['status']} by {r['decided_by']}. Nothing was changed.")
            if not r["assessments"]:
                raise conflict(f"No assessment is saved for return request {request_id}. Nothing was changed. Use "
                               "save_return_assessment first.")
            r.update(status=status, decided_by=who, decided_at=now_iso(), decision_note=note)
            st.save()
        return {"applied": True, "kind": "change", "status": status, "return_request": r}

    @reg(app, "post", "/returns/{request_id}/approve", "approve_return", "Approve a return (change)",
         "Approve one return request. This is a change: the status becomes approved. Needs approved_by. Refused with 409 "
         "until an assessment has been saved with save_return_assessment, and when the request is already approved or "
         "refused. It pays no refund: the refund follows in the payment system.")
    def approve_return(body: ApproveReturn, request_id: str = request_p):
        return decide(request_id, "approved", body.approved_by, body.note)

    @reg(app, "post", "/returns/{request_id}/refuse", "refuse_return", "Refuse a return (change)",
         "Refuse one return request. This is a change: the status becomes refused. Needs refused_by and the reason given to "
         "the customer. Refused with 409 until an assessment has been saved with save_return_assessment, and when the "
         "request is already approved or refused.")
    def refuse_return(body: RefuseReturn, request_id: str = request_p):
        return decide(request_id, "refused", body.refused_by, body.reason)

    # ------------------------------------------------------------ fraud review
    @reg(app, "get", "/flagged", "list_flagged_orders", "List the orders flagged for a fraud review",
         "List the orders the screening rules have flagged, oldest first. Each row has order_number, placed_at, customer_id, "
         "customer_name, total in US dollars, reasons (why the screening rules flagged it, in their words), flag_status "
         "(awaiting_review, released or held) and reviews (how many are saved). The filter status is optional. A flag is "
         "a request for a person to look. It is not a finding about the customer. Read the order with get_order and the "
         "customer's earlier orders with get_customer_order_history.")
    def list_flagged_orders(status: Literal["awaiting_review", "released", "held"] | None = Query(None, description="Only flags with this status.")):
        rows = [{"order_number": o["order_number"], "placed_at": o["placed_at"], "customer_id": o["customer_id"],
                 "customer_name": o["customer_name"], "total": o["total"], "currency": o["currency"],
                 "reasons": o["flag"]["reasons"], "flag_status": o["flag"]["status"], "reviews": len(o["fraud_reviews"])}
                for o in d()["orders"].values() if o["flag"] and (not status or o["flag"]["status"] == status)]
        return listing(sorted(rows, key=lambda r: (r["placed_at"], r["order_number"])))

    @reg(app, "get", "/customers/{customer_id}/history", "get_customer_order_history", "Get a customer's order history",
         "Read one customer's orders: customer_id, name, account_opened, account_changes (date and change), orders_count, "
         "average_total and highest_total (over the orders that are not flagged), and orders, newest first. Each order has "
         "order_number, placed_on, total, items, delivery_method, service, address_ref, device_ref, card_ref, outcome, "
         "flagged, and refund (where, site_id, till_row_id, date and amount when a refund was made at a till, otherwise "
         "empty). An address, a device and a card are references: the same reference on two orders means the same address, "
         "device or card. A refund made at a till can be read in the tills system by its till_row_id. Find the customer_id "
         "on the order.")
    def get_customer_order_history(customer_id: str = Path(..., description="Customer id, for example C-4020.")):
        c = d()["customers"].get(customer_id)
        if not c:
            raise not_found("customer", customer_id, "The customer_id is on the order: read it with get_order.")
        current = []
        for o in d()["orders"].values():
            if o["customer_id"] != customer_id:
                continue
            current.append({"order_number": o["order_number"], "placed_on": o["placed_on"], "total": o["total"],
                            "items": ", ".join(f"{x['quantity']} x {x['item']}" for x in o["lines"]),
                            "delivery_method": o["delivery"]["method"], "service": o["delivery"]["service"],
                            "address_ref": o["delivery"]["address_ref"], "device_ref": o["device_ref"],
                            "card_ref": o["payment"]["card_ref"], "outcome": o["status"], "refund": None,
                            "flagged": o["flag"] is not None})
        earlier = [{**x, "flagged": False} for x in c["earlier_orders"]]
        rows = sorted(current + earlier, key=lambda x: (x["placed_on"], x["order_number"]), reverse=True)
        plain = [x["total"] for x in rows if not x["flagged"]]
        return {"customer_id": customer_id, "name": c["name"], "account_opened": c["account_opened"],
                "account_changes": c["account_changes"], "orders_count": len(rows),
                "average_total": money(sum(plain) / len(plain)) if plain else 0.0,
                "highest_total": max(plain) if plain else 0.0, "currency": "USD", "orders": rows, "retailer_date": today()}

    @reg(app, "post", "/flagged/{order_number}/review", "save_fraud_review", "Save the review of a flagged order (draft)",
         "Save the review of one flagged order against the customer's earlier orders, as a draft. It changes no status. Each "
         "call is kept as a new version with who wrote it and when. Send signals (each with signal, departs_from_pattern and "
         "what_the_record_shows), proposed_decision, explanation and drafted_by. signal is one of device, delivery_address, "
         "basket_value, payment_method, items, delivery_method, account_change, earlier_refund or other. proposed_decision is "
         "release or hold. A signal listed twice is refused with 422. An order that is not flagged is refused with 409. The "
         "review describes the order. It says nothing about what kind of person the customer is. A person releases or holds. "
         "Returns the saved version.")
    def save_fraud_review(body: FraudReview, order_number: str = order_p):
        o = order_or_404(order_number)
        flagged_or_409(o)
        names = [s.signal for s in body.signals if s.signal != "other"]
        if len(names) != len(set(names)):
            twice = sorted({n for n in names if names.count(n) > 1})
            raise HTTPException(422, f"The signal {twice[0]} is listed twice. Nothing was saved. List each signal once.")
        payload = {"signals": [s.model_dump() for s in body.signals], "proposed_decision": body.proposed_decision,
                   "explanation": body.explanation}
        v = st.add_draft(o, "fraud_reviews", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "flag_status": o["flag"]["status"]}

    def settle(order_number: str, flag_status: str, order_status: str, who: str, note: str) -> dict:
        o = order_or_404(order_number)
        with st.lock:
            f = flagged_or_409(o)
            if f["status"] != "awaiting_review":
                raise conflict(f"Order {order_number} is already {f['status']} by {o['fraud_decision']['decided_by']}. "
                               "Nothing was changed.")
            if not o["fraud_reviews"]:
                raise conflict(f"No review is saved for order {order_number}. Nothing was changed. Use save_fraud_review first.")
            f["status"] = flag_status
            o["status"] = order_status
            o["fraud_decision"] = {"decision": flag_status, "decided_by": who, "decided_at": now_iso(), "note": note}
            st.save()
        return {"applied": True, "kind": "change", "status": flag_status, "order": {k: v for k, v in o.items() if k != "scans"}}

    @reg(app, "post", "/flagged/{order_number}/release", "release_flagged_order", "Release a flagged order (change)",
         "Release one flagged order for dispatch. This is a change: the flag becomes released and the order's status becomes "
         "released_for_dispatch. Needs released_by. Refused with 409 until a review has been saved with save_fraud_review, "
         "when the order is not flagged, and when it is already released or held.")
    def release_flagged_order(body: ReleaseOrder, order_number: str = order_p):
        return settle(order_number, "released", "released_for_dispatch", body.released_by, body.note)

    @reg(app, "post", "/flagged/{order_number}/hold", "hold_flagged_order", "Hold a flagged order (change)",
         "Hold one flagged order. This is a change: the flag becomes held and the order's status becomes on_hold. Needs "
         "held_by and a reason. Refused with 409 until a review has been saved with save_fraud_review, when the order is not "
         "flagged, and when it is already released or held. It cancels nothing and contacts no one.")
    def hold_flagged_order(body: HoldOrder, order_number: str = order_p):
        return settle(order_number, "held", "on_hold", body.held_by, body.reason)

    return app
