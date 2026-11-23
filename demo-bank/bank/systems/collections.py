"""Collections: recorded calls to customers in arrears, the bank's conduct rules, and reviews of the calls."""

from __future__ import annotations

from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..store import now_iso

KEY = "collections"
TITLE = "Collections call review"
LINE = "Transcripts of collections calls, the bank's conduct rules for them, and reviews of the calls."


class RuleFinding(BaseModel):
    rule_id: str = Field(..., description="The conduct rule, for example CR-02.")
    finding: Literal["followed", "breached", "not_applicable"] = Field(..., description="Whether the caller followed the rule, breached it, or the rule did not apply on this call.")
    evidence: str = Field("", description="The words from the transcript that show it, with the time. Needed when the finding is breached.")


class CallReview(BaseModel):
    summary: str = Field(..., min_length=1, description="What the call was about and how it went, in plain sentences.")
    rule_findings: list[RuleFinding] = Field(..., min_length=1, description="One finding for each conduct rule.")
    follow_up_note: str = Field("", description="What should happen next, for example the promise to pay to chase, or a coaching note.")
    supervisor_review: bool = Field(False, description="True if a supervisor should look at this call.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class ReviewedBody(BaseModel):
    reviewed_by: str = Field(..., min_length=1, description="Name of the person who closes the review.")
    note: str = Field("", description="Optional note.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds transcripts of collections calls as speaker turns with times, and the bank's conduct rules for such calls.")
    st = ctx.store
    d = lambda: st.data
    call_p = Path(..., description="Call id, for example CAL-1001.")

    def call_or_404(i):
        c = d()["collections_calls"].get(i)
        if not c:
            raise not_found("call", i, "Use list_collections_calls to find ids.")
        return c

    @reg(app, "get", "/calls", "list_collections_calls", "List collections calls",
         "List recorded collections calls: call_id, date, start time, customer, loan, the member of staff, days past due and status (unreviewed or "
         "reviewed). Filter by date (YYYY-MM-DD) or status. Unreviewed calls need a review.")
    def list_collections_calls(date: str = Query("", description="Only calls on this date, YYYY-MM-DD. Leave empty for all."),
                               status: str = Query("", description="Only calls with this status: unreviewed or reviewed. Leave empty for all.")):
        rows = [{"call_id": c["call_id"], "date": c["date"], "started_at": c["started_at"], "customer_id": c["customer_id"],
                 "customer_name": d()["customers"][c["customer_id"]]["name"], "loan_id": c["loan_id"], "staff": c["staff"]["name"],
                 "days_past_due": c["arrears"]["days_past_due"], "status": c["status"]}
                for c in d()["collections_calls"].values() if (not date or c["date"] == date) and (not status or c["status"] == status)]
        rows.sort(key=lambda r: (r["started_at"], r["call_id"]), reverse=True)
        return listing(rows)

    @reg(app, "get", "/calls/{call_id}", "get_collections_call", "Get one call in full",
         "Read one call: the transcript as speaker turns with times (Caller, Customer or Other person), the start time, the loan and the customer, the "
         "arrears (instalment, instalments behind, amount overdue, days past due), the member of staff, any saved reviews and who closed the review. "
         "Read the rules with get_conduct_rules and judge each rule against the transcript.")
    def get_collections_call(call_id: str = call_p):
        c = call_or_404(call_id)
        cust = d()["customers"][c["customer_id"]]
        return {**c, "customer": {k: cust[k] for k in ("customer_id", "type", "name", "segment", "risk_rating")},
                "loan": d()["loans"][c["loan_id"]]}

    @reg(app, "get", "/conduct-rules", "get_conduct_rules", "Get the conduct rules for collections calls",
         "Read the bank's numbered conduct rules for a collections call: say who you are, confirm identity before any detail of the debt, no threats "
         "or pressure, calls only between 08:00 and 20:00, offer hardship options when hardship is mentioned, say nothing about the debt to anyone "
         "else, and record any promise to pay exactly.")
    def get_conduct_rules():
        return listing(list(d()["conduct_rules"].values()))

    @reg(app, "post", "/calls/{call_id}/review", "save_call_review", "Save a call review (draft)",
         "Save your review of a call: a summary, each conduct rule marked followed, breached or not_applicable with the words from the transcript, a "
         "follow-up note and whether a supervisor should look. This is a draft: stored with who wrote it, a timestamp and a version number, earlier "
         "versions kept. The call stays unreviewed. Refused with 409 if the review is already closed.")
    def save_call_review(body: CallReview, call_id: str = call_p):
        c = call_or_404(call_id)
        if c["status"] != "unreviewed":
            raise conflict(f"Call {call_id} is already {c['status']}. Nothing was changed.")
        for f in body.rule_findings:
            if f.rule_id not in d()["conduct_rules"]:
                raise HTTPException(422, f"{f.rule_id} is not a conduct rule. Use get_conduct_rules to read the rule ids.")
            if f.finding == "breached" and not f.evidence.strip():
                raise HTTPException(422, f"A breach of {f.rule_id} needs evidence: the words from the transcript and the time.")
        v = st.add_draft(c, "reviews", {k: val for k, val in body.model_dump().items() if k != "drafted_by"}, body.drafted_by)
        return {"applied": True, "kind": "draft", "call_status": c["status"], "draft": v}

    @reg(app, "post", "/calls/{call_id}/reviewed", "mark_call_reviewed", "Close the review of a call (change)",
         "Mark a call as reviewed, using the latest saved review. This is a change and needs the name of the person who closes the review. Refused "
         "with 409 if no review was saved or if the call is already reviewed.")
    def mark_call_reviewed(body: ReviewedBody, call_id: str = call_p):
        c = call_or_404(call_id)
        with st.lock:
            if c["status"] != "unreviewed":
                raise conflict(f"Call {call_id} is already {c['status']}. Nothing was changed.")
            if not c["reviews"]:
                raise conflict(f"Call {call_id} has no saved review yet. Save one with save_call_review first. Nothing was changed.")
            rev = c["reviews"][-1]
            c["status"] = "reviewed"
            c["reviewed"] = {"reviewed_by": body.reviewed_by, "note": body.note, "reviewed_at": now_iso(), "review_version": rev["version"],
                             "supervisor_review": rev["supervisor_review"]}
            st.save()
        return {"applied": True, "kind": "change", "call_id": call_id, "status": c["status"], "reviewed": c["reviewed"]}

    return app
