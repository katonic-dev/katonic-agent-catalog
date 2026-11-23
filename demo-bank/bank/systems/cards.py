"""Cards: debit and credit cards, card payments, disputes."""

from __future__ import annotations

from typing import Literal

from fastapi import Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..store import now_iso

KEY = "cards"
TITLE = "Cards"
LINE = "Cards, card payments, blocks, replacements and disputes."


class BlockBody(BaseModel):
    reason: Literal["lost", "stolen", "fraud", "customer_request"] = Field(..., description="Why the card is blocked.")
    requested_by: str = Field("agent", description="Who asked for the block. Free text.")
    note: str = Field("", description="Optional note.")


class ReplacementBody(BaseModel):
    reason: Literal["lost", "stolen", "damaged", "expiring"] = Field(..., description="Why a new card is needed.")
    requested_by: str = Field("agent", description="Who asked for the replacement. Free text.")
    delivery: Literal["post", "branch"] = Field("post", description="How the customer gets the new card.")


class DisputeBody(BaseModel):
    transaction_ids: list[str] = Field(..., min_length=1, description="Card transaction ids to dispute, for example CTX-2001-U01.")
    reason: Literal["not_recognised", "duplicate_charge", "goods_not_received", "wrong_amount"] = Field(
        ..., description="Why the payments are disputed.")
    note: str = Field("", description="What the customer said, in plain sentences.")
    opened_by: str = Field("agent", description="Who opened the dispute. Free text.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds cards, card payments and disputes. Some operations change a card.")
    st = ctx.store
    d = lambda: st.data
    card_id = Path(..., description="Card id, for example CRD-2001.")

    def get_or_404(cid):
        c = d()["cards"].get(cid)
        if not c:
            raise not_found("card", cid, "Use list_customer_cards to find card ids.")
        return c

    @reg(app, "get", "/cards", "list_customer_cards", "List cards",
         "List cards, optionally for one customer. Each row has card_id, customer_id, masked number (last four digits only), "
         "type, status (active or blocked), expiry month and whether a replacement was requested.")
    def list_customer_cards(customer_id: str | None = Query(None, description="Only cards of this customer, for example CUS-1002.")):
        rows = [c for c in d()["cards"].values() if not customer_id or c["customer_id"] == customer_id]
        return listing(rows)

    @reg(app, "get", "/cards/{card_id}", "get_card", "Get one card",
         "Read one card: masked number, status, expiry (YYYY-MM), block reason, replacement flag, account and customer.")
    def get_card(card_id: str = card_id):
        return get_or_404(card_id)

    @reg(app, "get", "/cards/{card_id}/transactions", "list_card_transactions", "List card payments",
         "List recent payments made with one card, newest first: id, date, time, amount, merchant, channel (chip, contactless, "
         "online), status and whether it is already disputed.")
    def list_card_transactions(card_id: str = card_id, limit: int = Query(50, ge=1, le=200, description="Most rows to return.")):
        get_or_404(card_id)
        rows = [t for t in d()["card_transactions"].values() if t["card_id"] == card_id]
        rows.sort(key=lambda t: (t["date"], t["time"]), reverse=True)
        return listing(rows[:limit], card_id=card_id)

    @reg(app, "get", "/cards/{card_id}/disputes", "list_card_disputes", "List disputes on a card",
         "List the disputes opened on one card with reason, amount, status and note.")
    def list_card_disputes(card_id: str = card_id):
        get_or_404(card_id)
        return listing([x for x in d()["disputes"].values() if x["card_id"] == card_id], card_id=card_id)

    @reg(app, "post", "/cards/{card_id}/block", "block_card", "Block a card (change)",
         "Block a card so it cannot be used. This is a change: the card status becomes blocked and the response says "
         "applied true. If the card is already blocked the call is refused with 409.")
    def block_card(body: BlockBody, card_id: str = card_id):
        c = get_or_404(card_id)
        with st.lock:
            if c["status"] == "blocked":
                raise conflict(f"Card {card_id} is already blocked ({c['block_reason']}). Nothing was changed.")
            c.update(status="blocked", block_reason=body.reason, blocked_by=body.requested_by,
                     blocked_at=now_iso(), block_note=body.note)
            st.save()
        return {"applied": True, "kind": "change", "card": c}

    @reg(app, "post", "/cards/{card_id}/replacement", "request_card_replacement", "Request a replacement card (change)",
         "Ask for a new card to be made and sent. This is a change. Refused with 409 if a replacement was already requested.")
    def request_card_replacement(body: ReplacementBody, card_id: str = card_id):
        c = get_or_404(card_id)
        with st.lock:
            if c["replacement_requested"]:
                raise conflict(f"A replacement for card {card_id} was already requested. Nothing was changed.")
            rid = f"RPL-{st.next_number('replacement', 7001)}"
            rec = {"replacement_id": rid, "card_id": card_id, "reason": body.reason, "delivery": body.delivery,
                   "requested_by": body.requested_by, "requested_at": now_iso(), "status": "requested"}
            d()["card_replacements"][rid] = rec
            c["replacement_requested"] = True
            st.save()
        return {"applied": True, "kind": "change", "replacement": rec}

    @reg(app, "post", "/cards/{card_id}/disputes", "open_card_dispute", "Open a dispute (change)",
         "Open a dispute for one or more payments on a card. This is a change. Refused with 409 if a payment is already "
         "disputed, and with 422 if a payment does not belong to this card. Returns the new dispute with its id.")
    def open_card_dispute(body: DisputeBody, card_id: str = card_id):
        get_or_404(card_id)
        with st.lock:
            txs = []
            for tid in body.transaction_ids:
                t = d()["card_transactions"].get(tid)
                if not t or t["card_id"] != card_id:
                    raise not_found("transaction on this card", tid, "Use list_card_transactions to see valid ids.")
                if t["disputed"]:
                    raise conflict(f"Payment {tid} is already disputed. Nothing was changed.")
                txs.append(t)
            did = f"DSP-{st.next_number('dispute', 6002)}"
            rec = {"dispute_id": did, "card_id": card_id, "customer_id": d()["cards"][card_id]["customer_id"],
                   "transaction_ids": body.transaction_ids, "reason": body.reason,
                   "amount": round(sum(t["amount"] for t in txs), 2), "currency": "USD", "status": "open",
                   "opened": ctx.settings.bank_today.isoformat(), "opened_by": body.opened_by, "note": body.note,
                   "provisional_credit": False}
            for t in txs:
                t["disputed"] = True
            d()["disputes"][did] = rec
            st.save()
        return {"applied": True, "kind": "change", "dispute": rec}

    return app
