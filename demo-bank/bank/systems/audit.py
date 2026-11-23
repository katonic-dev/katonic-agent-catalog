"""Audit: control tests against the technology policy, and the records an auditor reads as evidence."""

from __future__ import annotations

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg

KEY = "audit"
TITLE = "Audit evidence"
LINE = "Control tests against policy MTB-POL-033, with the tickets, change records, access reviews and recovery tests an auditor reads as evidence."


class Found(BaseModel):
    item_no: int = Field(..., ge=1, description="The item number in the test's evidence plan.")
    record_ids: list[str] = Field(..., min_length=1, description="The ids of the records that are the evidence, for example ACR-1001 or CHG-2201.")
    note: str = Field("", description="What the records show, in plain sentences. Facts only.")


class Missing(BaseModel):
    item_no: int = Field(..., ge=1, description="The item number in the test's evidence plan.")
    searched: list[str] = Field(..., min_length=1, description="What was searched, for example 'list_access_reviews system=payments-hub quarter=2026-Q2: no record'.")
    note: str = Field("", description="Anything found that bears on why the item is missing, with record ids.")


class ExceptionSeen(BaseModel):
    description: str = Field(..., min_length=1, description="The exception, in plain sentences. State what the records show. Do not say whether the control passed.")
    record_ids: list[str] = Field(default_factory=list, description="The records that show the exception.")


class EvidencePack(BaseModel):
    evidence_found: list[Found] = Field(default_factory=list, description="Each evidence item found, with the record ids.")
    evidence_missing: list[Missing] = Field(default_factory=list, description="Each evidence item not found, with what was searched.")
    exceptions: list[ExceptionSeen] = Field(default_factory=list, description="The exceptions seen in the records. Empty if there are none.")
    notes: str = Field("", description="Anything else the auditor should know about how the evidence was gathered. It gives no conclusion: the auditor concludes.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds control tests of the technology policy MTB-POL-033 and the records used as evidence. "
                                  "It gathers evidence. It never concludes whether a control passed.")
    st = ctx.store
    d = lambda: st.data
    test_p = Path(..., description="Control test id, for example CTL-1001.")

    def get_or_404(coll, i, kind, hint):
        x = d()[coll].get(i)
        if not x:
            raise not_found(kind, i, hint)
        return x

    def in_range(day, date_from, date_to):
        return (not date_from or day >= date_from) and (not date_to or day <= date_to)

    @reg(app, "get", "/control-tests", "list_control_tests", "List control tests",
         "List control tests: test_id, title, the policy and clause it tests, the systems in scope, the period and status. Start here to see which "
         "controls need evidence.")
    def list_control_tests():
        keys = ("test_id", "title", "policy_id", "clause", "systems_in_scope", "period_from", "period_to", "status")
        return listing([{k: t[k] for k in keys} for t in d()["control_tests"].values()])

    @reg(app, "get", "/control-tests/{test_id}", "get_control_test", "Get one control test",
         "Read one control test: the control objective, the policy clause it tests with the clause text, the steps to follow, and the evidence plan: "
         "each evidence item with its number, what it is, the kind of record and where to look for it. Also any saved evidence packs.")
    def get_control_test(test_id: str = test_p):
        return get_or_404("control_tests", test_id, "control test", "Use list_control_tests to find ids.")

    @reg(app, "get", "/tickets", "search_tickets", "Search tickets",
         "Search the ticket system. Filter by words in the title, description or comments, by system and by the date opened. Each row has ticket_id, "
         "system, type, title, opened date, status and the related change id. Read one with get_ticket. Use it to find explanations and approvals.")
    def search_tickets(text: str = Query("", description="Words to look for in the title, description and comments. Not case sensitive. Leave empty for all."),
                       system: str = Query("", description="Only tickets for this system, for example payments-hub. Leave empty for all."),
                       date_from: str = Query("", description="First opened date to include, YYYY-MM-DD. Leave empty for no limit."),
                       date_to: str = Query("", description="Last opened date to include, YYYY-MM-DD. Leave empty for no limit.")):
        words = text.lower().split()
        rows = []
        for t in d()["tickets"].values():
            blob = (t["title"] + " " + t["description"] + " " + " ".join(t["comments"])).lower()
            if (system and t["system"] != system) or not in_range(t["opened"], date_from, date_to) or not all(w in blob for w in words):
                continue
            rows.append({k: t[k] for k in ("ticket_id", "system", "type", "title", "opened", "status", "related_change_id")})
        rows.sort(key=lambda r: (r["opened"], r["ticket_id"]), reverse=True)
        return listing(rows)

    @reg(app, "get", "/tickets/{ticket_id}", "get_ticket", "Get one ticket",
         "Read one ticket in full: system, type, title, who raised it, who it was given to, the dates, the status, the description, the related "
         "change id and the comments.")
    def get_ticket(ticket_id: str = Path(..., description="Ticket id, for example TKT-3001.")):
        return get_or_404("tickets", ticket_id, "ticket", "Use search_tickets to find ids.")

    @reg(app, "get", "/changes", "list_change_records", "List change records",
         "List change records: change_id, system, title, type (standard, normal or emergency), whether the system is critical, the date implemented, "
         "the approver and whether a rollback plan is recorded. Filter by system and by the date implemented. Read one with get_change_record.")
    def list_change_records(system: str = Query("", description="Only changes to this system, for example core-banking. Leave empty for all."),
                            date_from: str = Query("", description="First implemented date to include, YYYY-MM-DD. Leave empty for no limit."),
                            date_to: str = Query("", description="Last implemented date to include, YYYY-MM-DD. Leave empty for no limit.")):
        rows = [{"change_id": c["change_id"], "system": c["system"], "title": c["title"], "type": c["type"], "critical_system": c["critical_system"],
                 "implemented_on": c["implemented_on"], "approver": c["approver"], "rollback_plan_recorded": bool(c["rollback_plan"]),
                 "ticket_id": c["ticket_id"]}
                for c in d()["change_records"].values() if (not system or c["system"] == system) and in_range(c["implemented_on"], date_from, date_to)]
        rows.sort(key=lambda r: (r["implemented_on"], r["change_id"]))
        return listing(rows)

    @reg(app, "get", "/changes/{change_id}", "get_change_record", "Get one change record",
         "Read one change record in full: system, title, type, who requested it, the approver (empty if none is named), the rollback plan (empty if "
         "none is recorded), the date implemented, the description and the ticket.")
    def get_change_record(change_id: str = Path(..., description="Change id, for example CHG-2201.")):
        return get_or_404("change_records", change_id, "change record", "Use list_change_records to find ids.")

    @reg(app, "get", "/access-reviews", "list_access_reviews", "List access reviews",
         "List quarterly access reviews: review_id, system, quarter (for example 2026-Q2), the date completed, who reviewed and signed off, and the "
         "counts. A quarter with no row has no review record. Filter by system and quarter. Read one with get_access_review.")
    def list_access_reviews(system: str = Query("", description="Only reviews of this system, for example payments-hub. Leave empty for all."),
                            quarter: str = Query("", description="Only this quarter, for example 2026-Q2. Leave empty for all.")):
        rows = [{k: r[k] for k in ("review_id", "system", "quarter", "completed_on", "reviewer", "signed_off_by", "staff_accounts_reviewed")}
                for r in d()["access_reviews"].values() if (not system or r["system"] == system) and (not quarter or r["quarter"] == quarter)]
        rows.sort(key=lambda r: (r["system"], r["quarter"]))
        return listing(rows)

    @reg(app, "get", "/access-reviews/{review_id}", "get_access_review", "Get one access review",
         "Read one access review in full: system, quarter, date completed, reviewer, sign-off, accounts reviewed and removed, how many staff accounts "
         "use multi-factor sign-in, and every account exempt from it with the ticket that approved the exemption.")
    def get_access_review(review_id: str = Path(..., description="Access review id, for example ACR-1001.")):
        return get_or_404("access_reviews", review_id, "access review", "Use list_access_reviews to find ids.")

    @reg(app, "get", "/recovery-tests", "list_recovery_tests", "List recovery tests",
         "List recovery tests: recovery_test_id, system, test date, scenario, the target and the achieved recovery time in hours, and the result. "
         "Filter by system. Read one with get_recovery_test.")
    def list_recovery_tests(system: str = Query("", description="Only tests of this system, for example card-platform. Leave empty for all.")):
        rows = [{k: r[k] for k in ("recovery_test_id", "system", "test_date", "scenario", "rto_target_hours", "rto_achieved_hours", "result")}
                for r in d()["recovery_tests"].values() if not system or r["system"] == system]
        rows.sort(key=lambda r: (r["system"], r["test_date"]), reverse=True)
        return listing(rows)

    @reg(app, "get", "/recovery-tests/{recovery_test_id}", "get_recovery_test", "Get one recovery test",
         "Read one recovery test in full: system, date, scenario, who tested, the target and achieved recovery time, the result, the report "
         "reference and any findings.")
    def get_recovery_test(recovery_test_id: str = Path(..., description="Recovery test id, for example RCV-4001.")):
        return get_or_404("recovery_tests", recovery_test_id, "recovery test", "Use list_recovery_tests to find ids.")

    @reg(app, "post", "/control-tests/{test_id}/evidence-pack", "save_evidence_pack", "Save an evidence pack (draft)",
         "Save the evidence you gathered for a control test: each evidence item found with the ids of the records, each item missing with what was "
         "searched, and the exceptions seen. This is a draft: stored with who wrote it, a timestamp and a version number, earlier versions kept. It "
         "gives no conclusion: the auditor concludes. Every item number must be in the test's plan and every record id must exist.")
    def save_evidence_pack(body: EvidencePack, test_id: str = test_p):
        t = get_or_404("control_tests", test_id, "control test", "Use list_control_tests to find ids.")
        plan = {i["item_no"] for i in t["evidence_plan"]}
        for x in body.evidence_found + body.evidence_missing:
            if x.item_no not in plan:
                raise HTTPException(422, f"item_no {x.item_no} is not in the evidence plan of {test_id}. Use get_control_test to read the plan.")
        known = {}
        for coll in ("tickets", "change_records", "access_reviews", "recovery_tests"):
            known.update({k: coll for k in d()[coll]})
        for rid in [r for x in body.evidence_found for r in x.record_ids] + [r for x in body.exceptions for r in x.record_ids]:
            if rid not in known:
                raise not_found("record", rid, "Record ids come from the ticket, change, access review and recovery test operations.")
        both = {x.item_no for x in body.evidence_found} & {x.item_no for x in body.evidence_missing}
        if both:
            raise conflict(f"Item {sorted(both)[0]} is listed as both found and missing. Nothing was changed.")
        v = st.add_draft(t, "evidence_packs", {k: val for k, val in body.model_dump().items() if k != "drafted_by"}, body.drafted_by)
        return {"applied": True, "kind": "draft", "test_status": t["status"], "conclusion": "none: this pack gathers evidence only, the auditor concludes",
                "draft": v}

    return app
