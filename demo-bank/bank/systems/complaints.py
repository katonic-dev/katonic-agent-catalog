"""Complaints: customer complaints, the procedure that governs them, classifications, responses and redress."""

from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..seed_cmp import add_working_days, working_days_between
from ..store import now_iso

KEY = "complaints"
TITLE = "Complaints"
LINE = "Customer complaints, the complaints procedure, classifications, responses and redress."


class Classification(BaseModel):
    category: Literal["fees_and_charges", "payments", "cards", "lending_decision", "service_and_staff", "accounts", "other"] = Field(
        ..., description="The category from the procedure.")
    severity: Literal["low", "medium", "high"] = Field(..., description="How serious the matter is for the customer.")
    may_be_vulnerable: bool = Field(..., description="True if the customer may be vulnerable under the procedure.")
    vulnerability_reason: str = Field("", description="Why the customer may be vulnerable. Empty if not.")
    priority: Literal["normal", "priority", "urgent"] = Field("normal", description="normal, priority (vulnerable customer) or urgent (a time limit is near or missed).")
    reasoning: str = Field("", description="Why this category and severity, in plain sentences.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class ResponseDraft(BaseModel):
    response_text: str = Field(..., min_length=1, description="The text of the response to the customer, in plain sentences.")
    outcome: Literal["upheld", "partly_upheld", "not_upheld"] = Field(..., description="The outcome of the complaint.")
    redress_amount: float = Field(0, ge=0, description="Redress proposed, in the account currency. 0 if none.")
    redress_currency: str = Field("USD", description="Currency of the redress.")
    redress_account_id: str = Field("", description="Account of the customer to credit with the redress. Needed if redress_amount is above 0.")
    redress_description: str = Field("", description="What the redress is for, for example the second fee refunded.")
    late_acknowledgement_admitted: bool = Field(False, description="True if the response admits that the acknowledgement was late or never sent.")
    log_entry: str = Field(..., min_length=1, description="The entry for the complaints log: category, dates, outcome, redress.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class SendBody(BaseModel):
    approved_by: str = Field(..., min_length=1, description="Name of the person who approves the response.")
    note: str = Field("", description="Optional note.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds customer complaints and the procedure that governs them. Some operations change a complaint or an account.")
    st = ctx.store
    d = lambda: st.data
    cmp_p = Path(..., description="Complaint id, for example CMP-1001.")

    def cmp_or_404(i):
        c = d()["complaints"].get(i)
        if not c:
            raise not_found("complaint", i, "Use list_complaints to find ids.")
        return c

    def dates(c):
        today = ctx.settings.bank_today
        rec = date.fromisoformat(c["received"])
        ack_due, final_due = add_working_days(rec, 2), add_working_days(rec, 15)
        acked = c["acknowledged_on"]
        done = c["sent"]["sent_on"] if c["sent"] else ""
        late_ack = bool(acked) and date.fromisoformat(acked) > ack_due
        overdue = not acked and today > ack_due
        return {"received": c["received"], "acknowledge_due": ack_due.isoformat(), "acknowledged_on": acked,
                "acknowledged_late": late_ack, "acknowledgement_overdue": overdue,
                "acknowledgement_days_late": working_days_between(ack_due, today) if overdue else
                (working_days_between(ack_due, date.fromisoformat(acked)) if late_ack else 0),
                "final_response_due": final_due.isoformat(), "final_response_sent_on": done,
                "working_days_since_received": working_days_between(rec, today),
                "working_days_left_for_final_response": working_days_between(today, final_due)}

    def linked(c):
        ln, dd = c["linked"], d()
        out = {"accounts": [{k: dd["accounts"][i][k] for k in ("account_id", "product", "currency", "status", "balance")} for i in ln["account_ids"]],
               "transactions": [dd["transactions"][i] for i in ln["transaction_ids"]],
               "cards": [{k: dd["cards"][i].get(k, "") for k in ("card_id", "masked_number", "status", "block_reason", "blocked_by", "blocked_at", "block_note")}
                         for i in ln["card_ids"]],
               "payments": [{"payment_id": p["payment_id"], "amount": p["amount"], "currency": p["currency"], "status": p["status"],
                             "created": p["created"], "timeline": p["timeline"]} for p in (dd["payments"][i] for i in ln["payment_ids"])],
               "payment_investigations": [{k: dd["investigations"][i][k] for k in ("investigation_id", "status", "type", "raised", "claim")}
                                          for i in ln["investigation_ids"]],
               "loans": [dd["loans"][i] for i in ln["loan_ids"]],
               "loan_applications": [{k: dd["applications"][i].get(k, "") for k in ("application_id", "status", "product", "amount", "currency",
                                                                                   "term_months", "received", "decision")}
                                     for i in ln["loan_application_ids"]]}
        return out

    @reg(app, "get", "/complaints", "list_complaints", "List complaints",
         "List complaints: complaint_id, customer, status (open, responded or closed), channel, received date, subject, the date the final response "
         "is due and whether the acknowledgement is overdue. Filter by status. Open complaints need a classification and a response.")
    def list_complaints(status: str = Query("", description="Only complaints with this status: open, responded or closed. Leave empty for all.")):
        rows = []
        for c in d()["complaints"].values():
            if status and c["status"] != status:
                continue
            dt = dates(c)
            rows.append({"complaint_id": c["complaint_id"], "customer_id": c["customer_id"], "customer_name": d()["customers"][c["customer_id"]]["name"],
                         "status": c["status"], "channel": c["channel"], "received": c["received"], "subject": c["subject"],
                         "final_response_due": dt["final_response_due"], "acknowledgement_overdue": dt["acknowledgement_overdue"]})
        rows.sort(key=lambda r: (r["received"], r["complaint_id"]))
        return listing(rows)

    @reg(app, "get", "/complaints/{complaint_id}", "get_complaint", "Get one complaint in full",
         "Read one complaint: the customer's own words, the channel, the date received, the dates the procedure sets (acknowledgement and final "
         "response due, whether the acknowledgement was late or never sent, working days left), the linked records read from the other systems "
         "(accounts, the transactions named, cards, payments and investigations, loans and loan applications), the customer's earlier complaints "
         "with their outcome, and any saved classifications and response drafts. Read the procedure with get_complaints_procedure.")
    def get_complaint(complaint_id: str = cmp_p):
        c = cmp_or_404(complaint_id)
        cust = d()["customers"][c["customer_id"]]
        earlier = [{"complaint_id": x["complaint_id"], "subject": x["subject"], "received": x["received"], "status": x["status"],
                    "outcome": x["sent"]["outcome"] if x["sent"] else ""}
                   for x in d()["complaints"].values() if x["customer_id"] == c["customer_id"] and x["complaint_id"] != complaint_id]
        return {**{k: c[k] for k in ("complaint_id", "customer_id", "status", "channel", "subject", "customer_words")},
                "customer": {k: cust[k] for k in ("customer_id", "type", "name", "segment", "risk_rating")}, "dates": dates(c),
                "linked_records": linked(c), "earlier_complaints": earlier, "classifications": c["classifications"],
                "response_drafts": c["response_drafts"], "sent": c["sent"]}

    @reg(app, "get", "/procedure", "get_complaints_procedure", "Get the complaints procedure",
         "Read the bank's complaints procedure: the categories, the time limits (acknowledge within 2 working days, final response within 15 working "
         "days), what a response must contain, when redress applies and how much, the rule on declined loans, how vulnerable customers are handled "
         "and the customer's right to escalate to the ombudsman.")
    def get_complaints_procedure():
        return d()["complaints_procedure"]

    @reg(app, "post", "/complaints/{complaint_id}/classification", "save_complaint_classification", "Save a complaint classification (draft)",
         "Save your classification of a complaint: category, severity, whether the customer may be vulnerable and why, and the priority. This is a "
         "draft: stored with who wrote it, a timestamp and a version number, earlier versions kept. Nothing is sent. Refused with 409 if the "
         "response was already sent.")
    def save_complaint_classification(body: Classification, complaint_id: str = cmp_p):
        c = cmp_or_404(complaint_id)
        if c["status"] != "open":
            raise conflict(f"Complaint {complaint_id} is already {c['status']}. Nothing was changed.")
        v = st.add_draft(c, "classifications", {k: val for k, val in body.model_dump().items() if k != "drafted_by"}, body.drafted_by)
        return {"applied": True, "kind": "draft", "complaint_status": c["status"], "draft": v}

    @reg(app, "post", "/complaints/{complaint_id}/response-draft", "save_complaint_response", "Save a complaint response (draft)",
         "Save your draft response to the customer, the outcome, any redress proposed (amount and the account to credit) and the log entry. This is a "
         "draft: stored with who wrote it, a timestamp and a version number, earlier versions kept. Nothing is sent and no money moves until "
         "send_complaint_response. Refused with 409 if the response was already sent.")
    def save_complaint_response(body: ResponseDraft, complaint_id: str = cmp_p):
        c = cmp_or_404(complaint_id)
        if c["status"] != "open":
            raise conflict(f"Complaint {complaint_id} is already {c['status']}. Nothing was changed.")
        if body.redress_amount > 0:
            acc = d()["accounts"].get(body.redress_account_id)
            if not acc or acc["customer_id"] != c["customer_id"]:
                raise HTTPException(422, "redress_account_id must be an account of this customer when redress_amount is above 0.")
        v = st.add_draft(c, "response_drafts", {k: val for k, val in body.model_dump().items() if k != "drafted_by"}, body.drafted_by)
        return {"applied": True, "kind": "draft", "complaint_status": c["status"], "draft": v}

    @reg(app, "post", "/complaints/{complaint_id}/send", "send_complaint_response", "Send the response (change)",
         "Send the latest saved response to the customer and credit any redress to the named account. This is a change and needs the name of the "
         "person who approves. Refused with 409 if there is no saved response or if the response was already sent.")
    def send_complaint_response(body: SendBody, complaint_id: str = cmp_p):
        c = cmp_or_404(complaint_id)
        today = ctx.settings.bank_today.isoformat()
        with st.lock:
            if c["status"] != "open":
                raise conflict(f"Complaint {complaint_id} was already answered. Nothing was changed.")
            if not c["response_drafts"]:
                raise conflict(f"Complaint {complaint_id} has no saved response yet. Save one with save_complaint_response first. Nothing was changed.")
            draft = c["response_drafts"][-1]
            credited = ""
            if draft["redress_amount"] > 0:
                acc = d()["accounts"][draft["redress_account_id"]]
                n = st.next_number("redress", 1)
                credited = f"TXN-{acc['account_id'].replace('ACC-', '').replace('-', '')}-R{n:03d}"
                d()["transactions"][credited] = {
                    "transaction_id": credited, "account_id": acc["account_id"], "date": today, "amount": round(draft["redress_amount"], 2),
                    "currency": acc["currency"], "direction": "credit", "type": "redress", "counterparty": "Meridian Trust Bank",
                    "counterparty_id": "", "counterparty_country": "XM", "narrative": f"Complaint redress {complaint_id}"}
                acc["balance"] = round(acc["balance"] + draft["redress_amount"], 2)
            c["status"] = "responded"
            c["sent"] = {"sent_on": today, "approved_by": body.approved_by, "note": body.note, "outcome": draft["outcome"],
                         "response_text": draft["response_text"], "redress_amount": draft["redress_amount"],
                         "redress_currency": draft["redress_currency"], "redress_transaction_id": credited,
                         "log_entry": draft["log_entry"], "draft_version": draft["version"], "sent_at": now_iso()}
            st.save()
        return {"applied": True, "kind": "change", "complaint_id": complaint_id, "status": c["status"], "sent": c["sent"]}

    return app
