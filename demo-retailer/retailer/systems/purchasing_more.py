"""Purchasing, version 1.2: the operations for delivery notes, supplier payments and supplier questions.

They are added to the purchasing system by purchasing.build, so they share its OpenAPI document and its MCP address.
"""

from __future__ import annotations

from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, not_found, reg
from ..store import now_iso

NOTE_FIELDS = ("note_number, po_number, supplier_id, supplier_name, delivered_on, delivered_to, receipt_id (the goods receipt "
               "made when it was booked in) and status (received or claim_sent)")
PAYMENT_FIELDS = ("payment_id, supplier_id, supplier_name, invoice_number, invoice_date, invoice_total, due_date, status (paid "
                  "or scheduled), paid_on (empty until paid), scheduled_for (empty once paid), amount (what was or will be "
                  "paid, in US dollars), method, remittance_advice and deduction (net, tax, amount, reason and debit_note when "
                  "something was taken off the invoice, otherwise empty)")


class ClaimLine(BaseModel):
    kind: Literal["short_delivery", "wrong_item", "damaged"] = Field(
        ..., description="short_delivery: fewer were received than the note says. wrong_item: an item on the note was not "
                         "received and another came in its place. damaged: goods were refused at the dock as damaged.")
    item: str = Field(..., min_length=1, description="The item as the delivery note or the purchase order names it.")
    note_says: str = Field(..., description="What the delivery note says for this item, for example 500 kg.")
    received: str = Field(..., description="What the goods receipt says was received, for example 300 kg.")
    quantity_claimed: float = Field(..., gt=0, description="The quantity the claim is for.")
    unit: str = Field(..., min_length=1, description="The unit of that quantity, for example kg or each.")
    amount_claimed: float = Field(..., ge=0, description="The quantity claimed times the unit price on the purchase order, in "
                                                         "US dollars, net of tax.")


class DiscrepancyClaim(BaseModel):
    lines: list[ClaimLine] = Field(default_factory=list, description="One entry for each difference. Empty when the note, "
                                   "the order and the receipt agree.")
    proposed_next_step: Literal["send_claim", "no_claim", "refer_to_the_buyer"] = Field(
        ..., description="send_claim: there is a difference and the claim is ready for a person to send. no_claim: the note, "
                         "the order and the receipt agree. refer_to_the_buyer: the buyer must decide. A person decides.")
    message: str = Field("", description="The claim to the supplier, as a draft, in plain sentences. Needed with send_claim.")
    summary: str = Field("", description="A short summary in plain sentences. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class SupplierReply(BaseModel):
    answer_status: Literal["answered_from_records", "records_do_not_answer"] = Field(
        ..., description="answered_from_records: the records answer the question. records_do_not_answer: they do not.")
    reply: str = Field(..., min_length=1, description="The reply to the supplier, as a draft, in plain sentences. A person "
                                                      "sends it.")
    records_cited: list[str] = Field(default_factory=list, description="The ids of the records the reply rests on: a payment "
                                     "id, an invoice number, a purchase order number, a receipt id or a delivery note number. "
                                     "At least one with answered_from_records. Empty with records_do_not_answer.")
    proposed_next_step: Literal["send_reply", "refer_to_a_person"] = Field(
        ..., description="send_reply: ready for a person to send. refer_to_a_person: a colleague must answer, because the "
                         "records do not.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class SendBody(BaseModel):
    sent_by: str = Field(..., min_length=1, description="The person who sends it. Free text.")
    note: str = Field("", description="Optional note kept with the record.")


def add_more(app, ctx: Ctx) -> None:
    st = ctx.store
    d = lambda: st.data

    def note_or_404(i):
        x = d()["delivery_notes"].get(i)
        if not x:
            raise not_found("delivery note", i, "Use list_delivery_notes to find delivery note numbers.")
        return x

    def question_or_404(i):
        x = d()["supplier_questions"].get(i)
        if not x:
            raise not_found("supplier question", i, "Use list_supplier_questions to find question ids.")
        return x

    def known_record(i: str) -> bool:
        data = d()
        return (i in data["supplier_payments"] or i in data["supplier_invoices"] or i in data["purchase_orders"]
                or i in data["goods_receipts"] or i in data["delivery_notes"]
                or any(p["invoice_number"] == i for p in data["supplier_payments"].values()))

    note_p = Path(..., description="Delivery note number, for example DN-4135.")
    question_p = Path(..., description="Supplier question id, for example SQ-2611-03.")

    # ------------------------------------------------------------ delivery notes
    @reg(app, "get", "/delivery-notes", "list_delivery_notes", "List delivery notes",
         f"List delivery notes, oldest first. Each row has {NOTE_FIELDS}, and claims (how many drafts are saved). Filters are "
         "optional: po_number, supplier_id and status. An unknown po_number is refused with 404. Read the lines with "
         "get_delivery_note.")
    def list_delivery_notes(po_number: str | None = Query(None, description="Only notes for this purchase order, for example PO-450158."),
                            supplier_id: str | None = Query(None, description="Only notes of this supplier, for example SUP-304."),
                            status: Literal["received", "claim_sent"] | None = Query(None, description="Only notes with this status.")):
        if po_number and po_number not in d()["purchase_orders"]:
            raise not_found("purchase order", po_number, "Use list_purchase_orders to find purchase order numbers.")
        keys = ("note_number", "po_number", "supplier_id", "supplier_name", "delivered_on", "delivered_to", "receipt_id", "status")
        rows = [{**{k: n[k] for k in keys}, "claims": len(n["claims"])} for n in d()["delivery_notes"].values()
                if (not po_number or n["po_number"] == po_number) and (not supplier_id or n["supplier_id"] == supplier_id)
                and (not status or n["status"] == status)]
        return listing(sorted(rows, key=lambda n: (n["delivered_on"], n["note_number"])))

    @reg(app, "get", "/delivery-notes/{note_number}", "get_delivery_note", "Get one delivery note",
         f"Read one delivery note: {NOTE_FIELDS}; lines (line_no, item, unit, quantity_delivered: what the supplier's note says "
         "was delivered); remarks_at_delivery (what was written on the note at the dock, empty when nothing was); text (the "
         "note as printed); claims (every saved claim draft, each a version) and claim_sent (who sent the claim and when, "
         "empty until it is sent). Compare it with get_purchase_order for the po_number, with list_goods_receipts for what "
         "was booked in, and with the supplier's invoice for the order if there is one.")
    def get_delivery_note(note_number: str = note_p):
        return note_or_404(note_number)

    @reg(app, "post", "/delivery-notes/{note_number}/claim", "save_discrepancy_claim", "Save a discrepancy claim for a delivery note (draft)",
         "Save the result of setting one delivery note against its purchase order and goods receipt, as a draft. It sends "
         "nothing and changes no status. Each call is kept as a new version with who wrote it and when. Send lines (each with "
         "kind, item, note_says, received, quantity_claimed, unit and amount_claimed), proposed_next_step, message, an "
         "optional summary and drafted_by. kind is short_delivery, wrong_item or damaged. proposed_next_step is send_claim, "
         "no_claim or refer_to_the_buyer. Refused with 422: no_claim with a line, send_claim with no line or with no message, "
         "and an item that is on neither the note, the order nor the receipt. A person sends every claim. Returns the saved "
         "version.")
    def save_discrepancy_claim(body: DiscrepancyClaim, note_number: str = note_p):
        note = note_or_404(note_number)
        po = d()["purchase_orders"][note["po_number"]]
        receipt = d()["goods_receipts"][note["receipt_id"]]
        items = {x["item"] for x in note["lines"]} | {x["item"] for x in po["lines"]} | {x["item"] for x in receipt["lines"]}
        for x in body.lines:
            if x.item not in items:
                raise HTTPException(422, f"{x.item} is on neither the delivery note, the purchase order nor the goods receipt. "
                                         f"Nothing was saved. The items are: {'; '.join(sorted(items))}.")
        if body.proposed_next_step == "no_claim" and body.lines:
            raise HTTPException(422, "no_claim goes with no lines. Nothing was saved. Send lines with send_claim or "
                                     "refer_to_the_buyer, or send no_claim with an empty list.")
        if body.proposed_next_step == "send_claim" and (not body.lines or not body.message.strip()):
            raise HTTPException(422, "send_claim needs at least one line and the message to the supplier. Nothing was saved.")
        payload = {"lines": [x.model_dump() for x in body.lines], "proposed_next_step": body.proposed_next_step,
                   "message": body.message, "summary": body.summary,
                   "total_claimed": round(sum(x.amount_claimed for x in body.lines), 2)}
        v = st.add_draft(note, "claims", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "note_status": note["status"]}

    @reg(app, "post", "/delivery-notes/{note_number}/claim/send", "send_discrepancy_claim", "Send a discrepancy claim to the supplier (change)",
         "Send the latest saved claim of one delivery note to the supplier. This is a change: the status becomes claim_sent. "
         "Needs sent_by. Refused with 409 until a claim has been saved with save_discrepancy_claim, when the latest saved "
         "claim holds no line, and when a claim was already sent.")
    def send_discrepancy_claim(body: SendBody, note_number: str = note_p):
        note = note_or_404(note_number)
        with st.lock:
            if note["status"] == "claim_sent":
                raise conflict(f"A claim for delivery note {note_number} was already sent by {note['claim_sent']['sent_by']}. "
                               "Nothing was changed.")
            if not note["claims"]:
                raise conflict(f"No claim is saved for delivery note {note_number}. Nothing was changed. Use "
                               "save_discrepancy_claim first.")
            if not note["claims"][-1]["lines"]:
                raise conflict(f"The latest saved claim for delivery note {note_number} holds no line, so there is nothing to "
                               "claim. Nothing was changed.")
            note["status"] = "claim_sent"
            note["claim_sent"] = {"sent_by": body.sent_by, "sent_at": now_iso(), "version": note["claims"][-1]["version"],
                                  "to": d()["suppliers"][note["supplier_id"]]["contact_email"], "note": body.note}
            st.save()
        return {"applied": True, "kind": "change", "status": "claim_sent", "delivery_note": note}

    # ------------------------------------------------------------ supplier payments
    @reg(app, "get", "/payments", "list_supplier_payments", "List supplier payments",
         f"List payments to suppliers, made and scheduled, by invoice date. Each row has {PAYMENT_FIELDS}. Filters are "
         "optional and add up: supplier_id, status and invoice_number. An invoice with no payment row has not been paid and "
         "has no payment scheduled. The answer has retailer_date.")
    def list_supplier_payments(supplier_id: str | None = Query(None, description="Only payments to this supplier, for example SUP-303."),
                               status: Literal["paid", "scheduled"] | None = Query(None, description="Only payments with this status."),
                               invoice_number: str | None = Query(None, description="Only the payment of this invoice, for example INV-76410.")):
        rows = [p for p in d()["supplier_payments"].values()
                if (not supplier_id or p["supplier_id"] == supplier_id) and (not status or p["status"] == status)
                and (not invoice_number or p["invoice_number"] == invoice_number)]
        return listing(sorted(rows, key=lambda p: (p["invoice_date"], p["payment_id"])),
                       retailer_date=st.settings.retailer_today.isoformat())

    @reg(app, "get", "/payments/{payment_id}", "get_supplier_payment", "Get one supplier payment",
         f"Read one payment to a supplier: {PAYMENT_FIELDS}. Find the id with list_supplier_payments, for example PAY-7003.")
    def get_supplier_payment(payment_id: str = Path(..., description="Payment id, for example PAY-7003.")):
        p = d()["supplier_payments"].get(payment_id)
        if not p:
            raise not_found("supplier payment", payment_id, "Use list_supplier_payments to find payment ids.")
        return p

    # ------------------------------------------------------------ supplier questions
    @reg(app, "get", "/supplier-questions", "list_supplier_questions", "List supplier questions",
         "List the questions suppliers have sent, oldest first. Each row has question_id, received_on, supplier_id, "
         "supplier_name, subject, status (open or replied) and reply_drafts (how many are saved). Filters are optional: "
         "status and supplier_id. Read one with get_supplier_question.")
    def list_supplier_questions(status: Literal["open", "replied"] | None = Query(None, description="Only questions with this status."),
                                supplier_id: str | None = Query(None, description="Only questions of this supplier, for example SUP-301.")):
        rows = [{"question_id": q["question_id"], "received_on": q["received_on"], "supplier_id": q["supplier_id"],
                 "supplier_name": q["supplier_name"], "subject": q["subject"], "status": q["status"],
                 "reply_drafts": len(q["reply_drafts"])}
                for q in d()["supplier_questions"].values()
                if (not status or q["status"] == status) and (not supplier_id or q["supplier_id"] == supplier_id)]
        return listing(sorted(rows, key=lambda q: (q["received_on"], q["question_id"])))

    @reg(app, "get", "/supplier-questions/{question_id}", "get_supplier_question", "Get one supplier question",
         "Read one supplier question: question_id, received_on, supplier_id, supplier_name, from_name, from_email, subject, "
         "message (the supplier's own words), status, reply_drafts (every saved reply, each a version) and reply_sent (who "
         "sent the reply and when, empty until it is sent). Answer it from the records: list_supplier_payments, "
         "get_supplier_invoice, get_purchase_order, list_goods_receipts and get_delivery_note. This system holds no "
         "delivery slots and no dock rules.")
    def get_supplier_question(question_id: str = question_p):
        return question_or_404(question_id)

    @reg(app, "post", "/supplier-questions/{question_id}/reply", "save_supplier_reply", "Save a reply to a supplier question (draft)",
         "Save a reply to one supplier question, as a draft. It sends nothing and changes no status. Each call is kept as a "
         "new version with who wrote it and when. Send answer_status, reply, records_cited, proposed_next_step and "
         "drafted_by. answer_status is answered_from_records or records_do_not_answer. proposed_next_step is send_reply or "
         "refer_to_a_person. A record id that does not exist is refused with 404. answered_from_records with no record "
         "cited, and records_do_not_answer with a record cited or with send_reply, are refused with 422. A person sends "
         "every reply. Returns the saved version.")
    def save_supplier_reply(body: SupplierReply, question_id: str = question_p):
        q = question_or_404(question_id)
        for i in body.records_cited:
            if not known_record(i):
                raise not_found("payment, invoice, purchase order, goods receipt or delivery note", i, "Nothing was saved.")
        if body.answer_status == "answered_from_records" and not body.records_cited:
            raise HTTPException(422, "answered_from_records needs at least one record in records_cited. Nothing was saved.")
        if body.answer_status == "records_do_not_answer" and (body.records_cited or body.proposed_next_step != "refer_to_a_person"):
            raise HTTPException(422, "records_do_not_answer goes with an empty records_cited and the proposed_next_step "
                                     "refer_to_a_person. Nothing was saved.")
        payload = {"answer_status": body.answer_status, "reply": body.reply, "records_cited": list(body.records_cited),
                   "proposed_next_step": body.proposed_next_step}
        v = st.add_draft(q, "reply_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "question_status": q["status"]}

    @reg(app, "post", "/supplier-questions/{question_id}/send", "send_supplier_reply", "Send the reply to a supplier question (change)",
         "Send the latest saved reply of one supplier question to the supplier. This is a change: the status becomes replied. "
         "Needs sent_by. Refused with 409 until a reply has been saved with save_supplier_reply, and when the question is "
         "already replied.")
    def send_supplier_reply(body: SendBody, question_id: str = question_p):
        q = question_or_404(question_id)
        with st.lock:
            if q["status"] == "replied":
                raise conflict(f"Supplier question {question_id} was already replied to by {q['reply_sent']['sent_by']}. "
                               "Nothing was changed.")
            if not q["reply_drafts"]:
                raise conflict(f"No reply is saved for supplier question {question_id}. Nothing was changed. Use "
                               "save_supplier_reply first.")
            q["status"] = "replied"
            q["reply_sent"] = {"sent_by": body.sent_by, "sent_at": now_iso(), "to": q["from_email"],
                               "version": q["reply_drafts"][-1]["version"], "note": body.note}
            st.save()
        return {"applied": True, "kind": "change", "status": "replied", "supplier_question": q}
