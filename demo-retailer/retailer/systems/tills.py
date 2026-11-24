"""Tills, version 1.1: refunds, voids and discounts, the company's till rules, and the audits saved on a month."""

from __future__ import annotations

from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..seed_base import period_of
from ..seed_tills import RULES_DOCUMENT

KEY = "tills"
TITLE = "Tills"
LINE = "Refunds, voids and discounts from the tills of the stores and restaurants, the company's till rules, and the audits saved on a month."

PERIOD_RE = r"^\d{4}-(0[1-9]|1[0-2])$"
ROW_FIELDS = ("row_id, date, time, site_id, till, cashier_id, kind (refund, void or discount), amount in US dollars, reason, "
              "approver_id (the manager who approved, or the second person at a void; empty when there is none), "
              "original_receipt (refunds: the receipt number of the sale; empty when none was recorded), sale_amount and "
              "discount_percent (discounts only), reason_code (discounts: D1 to D5; empty when none was recorded) and "
              "after_payment (voids only: true when the sale was voided after it had been paid)")


class AuditRow(BaseModel):
    row_id: str = Field(..., min_length=1, description="The id of a row that is outside a rule, for example TR-2610-0042.")
    rules: list[Literal["TC-1", "TC-2", "TC-3", "TC-4"]] = Field(
        ..., min_length=1, description="The rule or rules the row is outside, by rule id: TC-1, TC-2, TC-3 or TC-4.")
    note: str = Field("", description="What the row shows, in one plain sentence. Nothing about who is at fault. Optional.")


class TillAudit(BaseModel):
    rows: list[AuditRow] = Field(default_factory=list, description="One entry for each row that is outside a rule. An empty "
                                 "list means no row was found outside the rules.")
    site_id: str = Field("", description="Leave empty for an audit of every site. Give a site id when the audit covers one site only.")
    summary: str = Field("", description="A short summary in plain sentences. It names no person as at fault. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds the refunds, voids and discounts rung up on the tills of the eight stores "
                                  "and twelve restaurants, and the company's till rules. Colleagues appear by id only. Saving "
                                  "an audit is a draft: an auditor reviews every row.")
    st = ctx.store
    d = lambda: st.data

    def periods() -> list[str]:
        return sorted({x["date"][:7] for x in d()["till_rows"].values()}, reverse=True)

    def period_or_error(period: str) -> None:
        if period in periods():
            return
        if period > period_of(st.settings.retailer_today):
            raise conflict(f"The period {period} has not ended, so it cannot be audited yet. Nothing was changed. "
                           f"The periods with rows are {', '.join(periods())}.")
        raise not_found("till rows for the period", period, f"The periods with rows are {', '.join(periods())}.")

    def site_or_404(site_id: str) -> None:
        if site_id not in d()["sites"]:
            raise not_found("site", site_id, "Site ids look like S-106 or R-014.")

    period_p = Path(..., pattern=PERIOD_RE, description="Month as YYYY-MM, for example 2026-10.")

    @reg(app, "get", "/rules", "get_till_rules", "Get the company's till rules",
         "Read the company's till rules: document, version, owner, rules (each with rule_id, applies_to, text and how_to_test, "
         "which says which fields of a row decide it), discount_reason_codes and what_the_rules_do_not_decide. There are four "
         "rules, TC-1 to TC-4. Check every row from list_till_entries against the rules for its kind.")
    def get_till_rules():
        return RULES_DOCUMENT

    @reg(app, "get", "/entries", "list_till_entries", "List refunds, voids and discounts",
         f"List the refunds, voids and discounts rung up on the tills, oldest first. Each row has {ROW_FIELDS}. Every filter is "
         "optional and the filters add up: period (YYYY-MM), site_id and kind. The answer has count (the rows returned), total "
         "(all rows that match), offset and limit. Use limit and offset to read the next page. A cashier and an approver "
         "appear by id only. An unknown site_id is refused with 404.")
    def list_till_entries(
            period: str | None = Query(None, pattern=PERIOD_RE, description="Only rows from this month, as YYYY-MM, for example 2026-10."),
            site_id: str | None = Query(None, description="Only rows from this store or restaurant, for example S-106."),
            kind: Literal["refund", "void", "discount"] | None = Query(None, description="Only this kind of row."),
            limit: int = Query(100, ge=1, le=500, description="Most rows to return, up to 500."),
            offset: int = Query(0, ge=0, description="How many matching rows to skip.")):
        if site_id:
            site_or_404(site_id)
        rows = [x for x in d()["till_rows"].values()
                if (not period or x["date"].startswith(period)) and (not site_id or x["site_id"] == site_id)
                and (not kind or x["kind"] == kind)]
        rows.sort(key=lambda x: x["row_id"])
        return listing(rows[offset:offset + limit], total=len(rows), offset=offset, limit=limit)

    @reg(app, "get", "/audits/{period}", "get_till_audit", "Get the saved audits for a month",
         "Read every refund and discount audit saved for one month, oldest first. Fields: period, count and audits, a list of "
         "versions, each with version, drafted_by, drafted_at, site_id (empty for every site), rows (row_id, rules, note) and "
         "summary. The list is empty when nothing was saved.")
    def get_till_audit(period: str = period_p):
        item = d()["till_audits"].get(period, {"audits": []})
        return {"period": period, "count": len(item["audits"]), "audits": item["audits"]}

    @reg(app, "post", "/audits/{period}", "save_till_audit", "Save a refund and discount audit for a month (draft)",
         "Save an audit of one month's refunds, voids and discounts, as a draft. It changes no row. Each call is kept as a new "
         "version with who wrote it and when. Send rows (each with row_id, rules and an optional note; an empty list when no "
         "row is outside the rules), an optional site_id when the audit covers one site, an optional summary and drafted_by. "
         "rules holds rule ids: TC-1, TC-2, TC-3 or TC-4. Every row_id must be a row of that month, and of that site when "
         "site_id is given, or the call is refused with 404. A row listed twice is refused with 422. A month that has not "
         "ended is refused with 409, and a month with no rows with 404. The audit lists rows and rules. It names no person "
         "as at fault: an auditor reviews every row. Returns the saved version.")
    def save_till_audit(body: TillAudit, period: str = period_p):
        period_or_error(period)
        if body.site_id:
            site_or_404(body.site_id)
        seen = set()
        for x in body.rows:
            row = d()["till_rows"].get(x.row_id)
            if not row or not row["date"].startswith(period):
                raise not_found(f"till row in period {period}", x.row_id, "Nothing was saved. Use list_till_entries with the period.")
            if body.site_id and row["site_id"] != body.site_id:
                raise not_found(f"till row at site {body.site_id}", x.row_id,
                                f"Nothing was saved. The row is at {row['site_id']}.")
            if x.row_id in seen:
                raise HTTPException(422, f"Row {x.row_id} is listed twice. Nothing was saved. List each row once, with every "
                                         "rule it is outside.")
            seen.add(x.row_id)
        with st.lock:
            item = d()["till_audits"].setdefault(period, {"period": period, "audits": []})
            payload = {"site_id": body.site_id, "rows": [x.model_dump() for x in body.rows], "summary": body.summary}
            v = st.add_draft(item, "audits", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "period": period}

    return app
