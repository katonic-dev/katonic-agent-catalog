"""Funds: a pension scheme's funds, members, holdings and contribution processing."""

from __future__ import annotations

from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..seed_funds import MIN_EMPLOYER_RATE, PERIODS
from ..store import now_iso

KEY = "funds"
TITLE = "Pension funds"
LINE = "A pension scheme run by the bank's trust arm: funds and fact sheets, members and holdings, contribution batches and transfer forms."


class RowResult(BaseModel):
    row_no: int = Field(..., ge=1, description="The row number in the batch.")
    outcome: Literal["passed", "failed"] = Field(..., description="passed or failed.")
    failed_rules: list[int] = Field(default_factory=list, description="The rule numbers (1 to 4) that the row fails. Required for a failed row, empty for a passed row.")
    note: str = Field("", description="Why, in one plain sentence.")


class BatchResult(BaseModel):
    rows: list[RowResult] = Field(..., min_length=1, description="One entry for every row of the batch.")
    summary: str = Field("", description="A short plain summary of the result.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class PostBody(BaseModel):
    approved_by: str = Field(..., min_length=1, description="Name of the person who approves the posting.")
    note: str = Field("", description="Optional note.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds the funds, members, holdings, contribution batches and transfer forms of a pension scheme run by the bank's "
                                  "trust arm. One operation posts contributions: it needs a saved result and the name of the person who approves.")
    st = ctx.store
    d = lambda: st.data
    batch_p = Path(..., description="Batch id, for example BAT-4001.")

    def batch_or_404(i):
        b = d()["pension_batches"].get(i)
        if not b:
            raise not_found("batch", i, "Use list_contribution_batches to find ids.")
        return b

    def holdings_of(member_id):
        rows, total = [], 0.0
        for fid, units in d()["pension_holdings"].get(member_id, {}).items():
            f = d()["pension_funds"][fid]
            value = round(units * f["unit_price"], 2)
            total += value
            rows.append({"fund_id": fid, "fund_name": f["name"], "units": units, "unit_price": f["unit_price"], "price_date": f["price_date"],
                         "value": value, "currency": "USD"})
        return rows, round(total, 2)

    def rule_failures(b):
        """Rows that break rules 1 to 4, worked out from the data. Used to guard posting."""
        bad, seen = {}, set()
        for r in b["rows"]:
            fails = []
            if r["member_id"] not in d()["pension_members"]:
                fails.append(1)
            if r["employee_amount"] < 0 or r["employer_amount"] < 0:
                fails.append(2)
            if r["member_id"] in seen:
                fails.append(3)
            seen.add(r["member_id"])
            if r["employer_amount"] < round(MIN_EMPLOYER_RATE * r["pensionable_salary"], 2):
                fails.append(4)
            if fails:
                bad[r["row_no"]] = fails
        return bad

    @reg(app, "get", "/funds", "list_funds", "List the funds",
         "List the funds of the scheme: fund_id, name, risk level (1 to 7), the annual management charge and the date of the latest fact sheet. "
         "Read a fact sheet with get_fund_fact_sheet.")
    def list_funds():
        keys = ("fund_id", "name", "risk_level", "annual_management_charge_pct", "ongoing_charges_pct", "launched", "unit_price", "price_date")
        return listing([{k: f[k] for k in keys} for f in d()["pension_funds"].values()])

    @reg(app, "get", "/funds/{fund_id}/fact-sheet", "get_fund_fact_sheet", "Get a fund fact sheet",
         "Read the fact sheet of one fund as text with its date, the fees, the returns by period and the risk level, and the same figures as fields. "
         "The sheet shows only the periods it lists: 1 month, 3 months, 6 months, 1 year, 3 years a year, 5 years a year and since launch a year. "
         "A period it does not list, or a fund too young for a period, is not answered by the sheet.")
    def get_fund_fact_sheet(fund_id: str = Path(..., description="Fund id, for example FND-3001.")):
        f = d()["pension_funds"].get(fund_id)
        if not f:
            raise not_found("fund", fund_id, "Use list_funds to find ids.")
        return {**{k: f[k] for k in ("fund_id", "name", "as_of", "risk_level", "annual_management_charge_pct", "ongoing_charges_pct", "launched", "unit_price")},
                "returns_pct": {p: v for p, v in zip(PERIODS, f["returns_pct"])}, "fact_sheet_text": f["fact_sheet_text"]}

    @reg(app, "get", "/members/{member_id}", "get_member", "Get one scheme member",
         "Read one member of the pension scheme: name, date of birth, address, employer, when they joined, status, the fund their contributions go to and "
         "the customer id if the member is also a customer of the bank.")
    def get_member(member_id: str = Path(..., description="Member id, for example MEM-5001.")):
        m = d()["pension_members"].get(member_id)
        if not m:
            raise not_found("member", member_id, "Member ids look like MEM-5001.")
        return m

    @reg(app, "get", "/members/{member_id}/holdings", "get_member_holdings", "Get a member's holdings",
         "Read what one member holds: for each fund the units, the unit price, the price date and the value, and the total value. "
         "Values use the unit prices of the latest fact sheets.")
    def get_member_holdings(member_id: str = Path(..., description="Member id, for example MEM-5001.")):
        m = d()["pension_members"].get(member_id)
        if not m:
            raise not_found("member", member_id, "Member ids look like MEM-5001.")
        rows, total = holdings_of(member_id)
        return {"member_id": member_id, "member_name": m["name"], "holdings": rows, "total_value": total, "currency": "USD"}

    @reg(app, "get", "/batches", "list_contribution_batches", "List contribution batches",
         "List contribution batches: batch_id, employer, the period, the date received, the number of rows, the control total and the status "
         "(received or posted). Filter by status. A received batch has not been posted and needs its rows checked.")
    def list_contribution_batches(status: str = Query("", description="Only batches with this status: received or posted. Leave empty for all.")):
        rows = [{"batch_id": b["batch_id"], "employer": b["employer"], "period": b["period"], "received_on": b["received_on"], "row_count": len(b["rows"]),
                 "control_total": b["control_total"], "status": b["status"]} for b in d()["pension_batches"].values() if not status or b["status"] == status]
        rows.sort(key=lambda r: r["batch_id"])
        return listing(rows)

    @reg(app, "get", "/batches/{batch_id}", "get_contribution_batch", "Get one contribution batch",
         "Read one batch: the employer, the period, the control total and every row (member id, the name on the row, the pensionable salary, the employee "
         "amount and the employer amount). Also any saved results and, if posted, who approved the posting and which rows were posted. "
         "Check each row against the rules of get_processing_procedure.")
    def get_contribution_batch(batch_id: str = batch_p):
        return batch_or_404(batch_id)

    @reg(app, "get", "/forms/{form_id}", "get_transfer_form", "Get a transfer form",
         "Read a transfer form as text read by machine from a scan. Marks in square brackets are the reader's doubts, such as an unreadable digit. "
         "Check it against rules 5 to 8 of get_processing_procedure. A form that cannot be read with confidence goes to a person.")
    def get_transfer_form(form_id: str = Path(..., description="Form id, for example FRM-4001.")):
        f = d()["pension_forms"].get(form_id)
        if not f:
            raise not_found("form", form_id, "Form ids look like FRM-4001.")
        return f

    @reg(app, "get", "/procedures", "get_processing_procedure", "Get the processing procedure",
         "Read the written rules that a contribution row (rules 1 to 4) and a transfer form (rules 5 to 8) must pass, numbered, and what happens to a "
         "failed row. Use the rule numbers when you save a result.")
    def get_processing_procedure():
        return d()["pension_procedure"]

    @reg(app, "post", "/batches/{batch_id}/result", "save_batch_result", "Save the result of checking a batch (draft)",
         "Save what you found for every row of a batch: passed, or failed with the rule number of each failure. Every row must be given once. This is a "
         "draft: stored with who wrote it, a timestamp and a version number, earlier versions kept. Nothing is posted. Refused with 409 if the batch "
         "was already posted and with 422 if a row is missing, repeated or unknown, or a failed row has no rule number.")
    def save_batch_result(body: BatchResult, batch_id: str = batch_p):
        b = batch_or_404(batch_id)
        if b["status"] == "posted":
            raise conflict(f"Batch {batch_id} was already posted. Nothing was changed.")
        numbers = [r.row_no for r in body.rows]
        want = {r["row_no"] for r in b["rows"]}
        if len(numbers) != len(set(numbers)) or set(numbers) != want:
            raise HTTPException(422, f"Give every row of {batch_id} exactly once: rows {sorted(want)}.")
        for r in body.rows:
            if r.outcome == "failed" and not r.failed_rules:
                raise HTTPException(422, f"Row {r.row_no} is failed and needs at least one rule number from get_processing_procedure.")
            if r.outcome == "passed" and r.failed_rules:
                raise HTTPException(422, f"Row {r.row_no} is passed and must not have rule numbers.")
            if any(n < 1 or n > 4 for n in r.failed_rules):
                raise HTTPException(422, f"Row {r.row_no}: rule numbers for a contribution row are 1 to 4.")
        v = st.add_draft(b, "results", {k: val for k, val in body.model_dump().items() if k != "drafted_by"}, body.drafted_by)
        return {"applied": True, "kind": "draft", "batch_status": b["status"], "draft": v}

    @reg(app, "post", "/batches/{batch_id}/post", "post_contribution_batch", "Post a contribution batch (change)",
         "Post the rows of a batch that passed, and only those: units are bought in each member's contribution fund at the latest unit price. This is a "
         "change and needs the name of the person who approves. Refused with 409 if the batch was already posted, if no result is saved, if the latest "
         "saved result passes a row that breaks a rule, or if no row passed. Failed rows are not posted.")
    def post_contribution_batch(body: PostBody, batch_id: str = batch_p):
        b = batch_or_404(batch_id)
        with st.lock:
            if b["status"] == "posted":
                raise conflict(f"Batch {batch_id} was already posted. Nothing was changed.")
            if not b["results"]:
                raise conflict(f"Batch {batch_id} has no saved result. Check the rows and save the result with save_batch_result first. Nothing was changed.")
            result = b["results"][-1]
            passed = [r["row_no"] for r in result["rows"] if r["outcome"] == "passed"]
            failed = [r["row_no"] for r in result["rows"] if r["outcome"] == "failed"]
            real = rule_failures(b)
            wrong = [n for n in passed if n in real]
            if wrong:
                raise conflict(f"Row {wrong[0]} is saved as passed but it breaks rule {real[wrong[0]][0]}. Save a corrected result. Nothing was changed.")
            if not passed:
                raise conflict(f"No row of batch {batch_id} passed, so there is nothing to post. Nothing was changed.")
            total = 0.0
            for r in b["rows"]:
                if r["row_no"] not in passed:
                    continue
                m = d()["pension_members"][r["member_id"]]
                fund = d()["pension_funds"][m["contribution_fund_id"]]
                amount = round(r["employee_amount"] + r["employer_amount"], 2)
                units = round(amount / fund["unit_price"], 4)
                held = d()["pension_holdings"].setdefault(r["member_id"], {})
                held[fund["fund_id"]] = round(held.get(fund["fund_id"], 0.0) + units, 4)
                total += amount
            b["status"] = "posted"
            b["posted"] = {"posted_on": ctx.settings.bank_today.isoformat(), "approved_by": body.approved_by, "note": body.note, "rows_posted": passed,
                           "rows_not_posted": failed, "amount_posted": round(total, 2), "result_version": result["version"], "posted_at": now_iso()}
            st.save()
        return {"applied": True, "kind": "change", "batch_id": batch_id, "status": b["status"], "posted": b["posted"]}

    return app
