"""Health: group medical schemes with their tables of benefits, members, medical policies, pre-authorisation requests,
medical claims held for review, providers with their contracts and tariffs, and provider invoices."""

from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, ForgivingModel, listing, make_subapp, not_found, reg
from ..seed_health import (CODES, POLICY_FOR_CODE, age_on, apply_benefit, benefit_of, check_invoice, claim_figures,
                           compare_with_earlier, member_cover_on, usage_row, usd)
from ..seed_policy import long_date
from ..store import now_iso

KEY = "health"
TITLE = "Health"
LINE = ("Group medical schemes with their tables of benefits, members, medical policies, pre-authorisation requests, medical "
        "claims held for review, providers with their contracts and tariffs, and provider invoices.")

DRAFTED_BY = Field("agent", description="Who wrote the draft. Free text.")


class CriterionFinding(ForgivingModel):
    criterion: str = Field(..., description="The number of the criterion in the medical policy, for example 2.")
    finding: Literal["met", "not_met", "not_stated"] = Field(
        ..., description="met when the file states a fact that meets the criterion; not_met when the file states a fact that plainly "
                         "fails it; not_stated when the file says nothing about it.")
    evidence: str = Field("", description="The fact the finding rests on, in the file's words, with the document id, for example "
                                          "physiotherapy for 5 weeks (PA-8101-D2). For not_stated, say what the file lacks.")


class PreAuthorisationAssessment(ForgivingModel):
    cover_in_force_on_planned_date: Literal["yes", "no", "not_checked"] = Field(
        ..., description="What the request's record says about the member's cover on the planned date.")
    plan_position: Literal["needs_pre_authorisation", "no_pre_authorisation_needed", "not_covered_by_the_plan", "plan_is_silent"] = Field(
        ..., description="What the member's plan says about this procedure, as the request's record gives it. plan_is_silent when "
                         "no benefit of the plan names the procedure: the proposal is then refer_to_the_assessor.")
    criteria: list[CriterionFinding] = Field(default_factory=list, description="One row for each criterion of the medical policy the "
                                             "record gives. Leave the list empty when the record gives no medical policy to read.")
    proposal: Literal["send_to_the_assessor_as_met", "ask_the_provider", "refer_to_the_medical_reviewer", "refer_to_the_assessor"] = Field(
        ..., description="send_to_the_assessor_as_met when every criterion is met; ask_the_provider when the notes say nothing about "
                         "a criterion; refer_to_the_medical_reviewer when a criterion is plainly not met; refer_to_the_assessor when "
                         "the member's cover is not in force on the planned date, the plan does not cover the procedure, the plan "
                         "needs no pre-authorisation for it, or the plan is silent on it. No value refuses the request.")
    question_for_the_provider: str = Field("", description="What to ask the provider, in a sentence. Needed when the proposal is "
                                                           "ask_the_provider. Otherwise leave empty.")
    reason: str = Field(..., min_length=1, description="Why this proposal, in one or two sentences, with the dates and figures the record gives.")
    drafted_by: str = DRAFTED_BY


class PreAuthorisationDecision(ForgivingModel):
    decision: Literal["approved", "declined"] = Field(..., description="The decision on the request.")
    decided_by: str = Field(..., min_length=1, description="The name of the person who decided.")
    role: Literal["authorised_assessor", "medical_reviewer"] = Field(
        ..., description="That person's role. An authorised assessor may approve. Only the medical reviewer, a clinician, may decline.")
    reason: str = Field(..., min_length=1, description="The reason, in a sentence.")


class ClaimDetermination(ForgivingModel):
    suggestion: Literal["pay_as_the_plan_allows", "do_not_pay", "ask_the_provider", "refer_to_the_medical_reviewer"] = Field(
        ..., description="pay_as_the_plan_allows when nothing stands against the claim: the plan's limit and the member's share are "
                         "applied by the system. do_not_pay for a duplicate of an earlier claim or when the member's cover was not in "
                         "force on the date of service. ask_the_provider when the file lacks a document the medical policy asks for. "
                         "refer_to_the_medical_reviewer when a criterion of the medical policy is plainly not met.")
    reasons: list[str] = Field(..., min_length=1, description="The reasons, one each, with the dates, ids and figures the record gives.")
    duplicate_of: str | None = Field(None, description="The id of the earlier claim this one repeats, for example MC-9011. Leave empty "
                                                       "when the claim is not a duplicate.")
    criteria: list[CriterionFinding] = Field(default_factory=list, description="One row for each criterion of the medical policy, "
                                             "when the claim is held for medical necessity. Otherwise leave the list empty.")
    question_for_the_provider: str = Field("", description="What to ask the provider, in a sentence, when the suggestion is "
                                                           "ask_the_provider. Otherwise leave empty.")
    notes: str = Field("", description="Anything else the assessor should know.")
    drafted_by: str = DRAFTED_BY


class ClaimDecision(ForgivingModel):
    decision: Literal["pay", "do_not_pay"] = Field(..., description="The assessor's decision. pay records the amount the system worked out.")
    decided_by: str = Field(..., min_length=1, description="The name of the assessor who decided.")
    reason: str = Field(..., min_length=1, description="The reason, in a sentence.")


class InvoiceDifference(ForgivingModel):
    line_id: str = Field(..., description="The id of the invoice line, for example PI-9502-L2.")
    kind: Literal["over_the_tariff", "under_the_tariff", "not_on_the_tariff", "follow_up_inside_the_free_period",
                  "medicines_discount_not_applied", "other"] = Field(
        ..., description="What kind of difference it is, in the word the invoice's check gives for the line: over_the_tariff, "
                         "under_the_tariff (charged less than the agreed price), not_on_the_tariff, "
                         "follow_up_inside_the_free_period or medicines_discount_not_applied. other only for a difference the check "
                         "does not name.")
    clause: str = Field("", description="The clause of the provider's contract the difference rests on, for example 4.1.")
    note: str = Field("", description="The figures in a few words: charged, agreed and the difference, as the check gives them.")


class InvoiceDifferences(ForgivingModel):
    finding: Literal["agrees_with_the_contract", "differences_found"] = Field(
        ..., description="agrees_with_the_contract when the check shows no line with a difference; differences_found otherwise.")
    differences: list[InvoiceDifference] = Field(default_factory=list, description="One row for each line with a difference. Leave "
                                                 "the list empty when the invoice agrees with the contract.")
    notes: str = Field("", description="Anything the claims officer should know.")
    drafted_by: str = DRAFTED_BY


class InvoiceQuery(ForgivingModel):
    decision: Literal["query_the_lines", "accept_as_charged"] = Field(..., description="The claims officer's decision on the invoice.")
    line_ids: list[str] = Field(default_factory=list, description="The lines to query, by id. Needed for query_the_lines. Leave empty "
                                                                  "for accept_as_charged.")
    decided_by: str = Field(..., min_length=1, description="The name of the claims officer who decided.")
    reason: str = Field("", description="The reason, in a sentence.")


class CallBackRequest(ForgivingModel):
    question: str = Field(..., min_length=1, description="The member's question, in the member's words or close to them.")
    why_the_documents_do_not_settle_it: str = Field(
        ..., min_length=1, description="Why a person is needed, in a sentence: for example that neither the table of benefits nor the "
                                       "exclusions of the member's scheme names the treatment.")
    drafted_by: str = DRAFTED_BY


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds group medical schemes, each with its own table of benefits and exclusions; the "
                                  "members of each scheme with what they have used; medical policies with numbered criteria; "
                                  "pre-authorisation requests; medical claims held for review; providers with their contracts and "
                                  "tariffs; and provider invoices. The system does every sum and counts every day. A draft is saved "
                                  "with who wrote it, a time and a version number. A change needs a named person.")
    st = ctx.store
    d = lambda: st.data
    today = lambda: ctx.settings.insurer_today.isoformat()
    grp_p = Path(..., description="Scheme id, for example GRP-6101.")
    mem_p = Path(..., description="Member id, for example MEM-7201.")
    pa_p = Path(..., description="Pre-authorisation request id, for example PA-8101.")
    mc_p = Path(..., description="Medical claim id, for example MC-9101.")
    prv_p = Path(..., description="Provider id, for example PRV-5101.")
    pi_p = Path(..., description="Provider invoice id, for example PI-9501.")

    def one(name, kind, ident, hint):
        item = d()[name].get(ident)
        if not item:
            raise not_found(kind, ident, hint)
        return item

    scheme_or_404 = lambda i: one("health_schemes", "scheme", i, "Use list_schemes to find ids. A member's scheme id is on the member.")
    member_or_404 = lambda i: one("health_members", "member", i, "Use search_members with the member's name to find the id.")
    pa_or_404 = lambda i: one("pre_authorisations", "pre-authorisation request", i, "Use list_pre_authorisation_requests to find ids.")
    claim_or_404 = lambda i: one("medical_claims", "medical claim", i, "Use list_medical_claims to find ids.")
    provider_or_404 = lambda i: one("health_providers", "provider", i, "Use list_providers to find ids.")
    invoice_or_404 = lambda i: one("provider_invoices", "provider invoice", i, "Use list_provider_invoices to find ids.")

    def check_date(on):
        try:
            date.fromisoformat(on)
        except ValueError:
            raise HTTPException(422, f"The date {on} is not valid. Send it as YYYY-MM-DD, for example 2026-11-17. Nothing was checked.")

    def member_brief(m):
        scheme = d()["health_schemes"][m["scheme_id"]]
        return {"member_id": m["member_id"], "name": m["name"], "date_of_birth": m["date_of_birth"], "scheme_id": m["scheme_id"],
                "employer": scheme["employer"], "plan_name": scheme["plan_name"], "relationship": m["relationship"],
                "dependant_of": m["dependant_of"], "cover_start": m["cover_start"], "cover_end": m["cover_end"],
                "cover_note": m["cover_note"]}

    def scheme_brief(s):
        return {k: s[k] for k in ("scheme_id", "employer", "employer_place", "plan_name", "status", "period_start", "period_end")}

    def policy_check(criteria, policy, what):
        """Refuse criterion rows that are not criteria of the medical policy that applies."""
        if not criteria:
            return
        if policy is None:
            raise conflict(f"No medical policy is to be read for {what}, so it takes no criterion rows. Leave the criteria empty. "
                           "Nothing was saved.")
        known = [c["number"] for c in policy["criteria"]]
        sent = [c.criterion.strip() for c in criteria]
        unknown = [n for n in sent if n not in known]
        if unknown or len(sent) != len(set(sent)):
            raise conflict(f"{policy['medical_policy_id']} has the criteria {', '.join(known)}, each to be given once. Not a criterion "
                           f"of it or given twice: {', '.join(unknown) or 'a number given twice'}. Nothing was saved.")

    # ------------------------------------------------------------ schemes
    @reg(app, "get", "/schemes", "list_schemes", "List the group medical schemes",
         "List the schemes: id, employer, the employer's place, the name of the plan, status and the scheme's period, which is also "
         "its benefit year. It does not give any table of benefits: two schemes have different plans, and get_scheme reads one "
         "scheme's table at a time.")
    def list_schemes():
        return listing([scheme_brief(s) for s in d()["health_schemes"].values()])

    @reg(app, "get", "/schemes/{scheme_id}", "get_scheme", "Get one scheme with its table of benefits and exclusions",
         "Read one scheme in full: employer, plan name, period and benefit year, a note on how to read it, the table of benefits and "
         "the exclusions. Each benefit row has an id (for example BEN-F07), a plain name, a state (covered, covered_with_conditions "
         "or not_covered), the limit as figures and as a sentence (an amount in a benefit year, an amount for each visit or "
         "pregnancy, or a number of sessions), the member's share as a percentage with its yearly cap and as a sentence, the "
         "conditions in words, whether pre-authorisation is needed, and a waiting period in days where there is one. Each exclusion "
         "has an id (for example EXC-F2) and its text. The table belongs to this scheme only: another scheme's plan differs. A "
         "treatment that is in neither the table nor the exclusions is not settled here, and a person answers. It does not say "
         "what one member has used: get_member does.")
    def get_scheme(scheme_id: str = grp_p):
        s = scheme_or_404(scheme_id)
        return {**s, "benefit_count": len(s["benefits"]), "exclusion_count": len(s["exclusions"]), "read_on": today()}

    # ------------------------------------------------------------ members
    @reg(app, "get", "/members", "search_members", "Search members by name, id, scheme or employer",
         "Find members by name, member id, scheme id or employer. Any word of the text may match, in any order. With no text, every "
         "member is listed. Each row is whole: member id, name, date of birth, scheme id, employer, plan name, whether the member is "
         "an employee or a dependant and of whom, the dates the member's cover started and ended (cover_end is empty when no end is "
         "recorded), and whether cover is in force on the insurer date, with the reason. It does not give what the member has used: "
         "get_member does.")
    def search_members(text: str | None = Query(None, description="Words from the member's name, or a member id, scheme id or "
                                                                  "employer, for example Wrenfield. Leave empty to list every member.")):
        words = [w.lower() for w in (text or "").replace(",", " ").split() if len(w) > 2]
        rows = []
        for m in d()["health_members"].values():
            brief = member_brief(m)
            hay = f"{m['name']} {m['member_id']} {m['scheme_id']} {brief['employer']}".lower()
            if not words or any(w in hay for w in words):
                rows.append({**brief, "cover_on_read_date": member_cover_on(m, today())})
        return listing(rows, searched_for=text or "")

    @reg(app, "get", "/members/{member_id}", "get_member", "Get one member with cover and what has been used",
         "Read one member in full: name, date of birth with the age on the insurer date worked out by the system, the scheme id, "
         "employer and plan name, whether the member is an employee or a dependant, the dates cover started and ended, and "
         "cover_on_read_date (whether cover is in force on the insurer date, with the reason). benefits has one row for every "
         "benefit of the member's own plan: the whole benefit row as get_scheme gives it, then what the member has used this benefit "
         "year and what remains (an amount or a number of sessions, worked out by the system), the share the member has paid "
         "against the yearly cap, a sentence that says all of it, and for a benefit with a waiting period the date from which the "
         "member can use it and whether that date has come. Use these figures and do not work them out. It does not give the "
         "exclusions: get_scheme does. Call-back requests are not part of the member: call_back_requests_on_file only counts them.")
    def get_member(member_id: str = mem_p):
        m = member_or_404(member_id)
        scheme = d()["health_schemes"][m["scheme_id"]]
        return {**member_brief(m), "age_on_read_date": age_on(m["date_of_birth"], today()),
                "benefit_year_start": scheme["period_start"], "benefit_year_end": scheme["period_end"],
                "cover_on_read_date": member_cover_on(m, today()),
                "benefits": [usage_row(m, b, today()) for b in scheme["benefits"]],
                "dependants": [x["member_id"] for x in d()["health_members"].values() if x["dependant_of"] == member_id],
                "call_back_requests_on_file": sum(1 for c in d()["call_back_requests"].values() if c["member_id"] == member_id),
                "read_on": today()}

    @reg(app, "get", "/members/{member_id}/cover", "check_member_cover_on_date", "Check whether a member's cover was in force on a date",
         "Say whether the member's cover was in force on one date, for example a date of service or a planned date. The answer gives "
         "in_force (true or false) and the reason in a sentence, with the dates and the number of days worked out by the system. "
         "Use this answer and do not work out the days yourself. It changes nothing.")
    def check_member_cover_on_date(member_id: str = mem_p,
                                   on: str = Query(..., description="The date to check, as YYYY-MM-DD, for example 2026-11-14.")):
        m = member_or_404(member_id)
        check_date(on)
        return member_cover_on(m, on)

    @reg(app, "get", "/members/{member_id}/benefits/{benefit_id}/estimate", "calculate_member_benefit",
         "Work out what the plan pays on an amount for one member and one benefit",
         "Work out what the member's plan would pay on an amount under one benefit, from what the member has used so far this "
         "benefit year. The answer gives the amount within the limit, the amount over the limit, the member's share (the percentage "
         "of the amount within the limit, held to what is left of the yearly cap), what the plan pays, what the member pays in all, "
         "and a note that says the working in a sentence. For a benefit counted in sessions it also gives the sessions within and "
         "beyond the plan's. It also gives whether the member's cover is in force on the insurer date and, for a benefit with a "
         "waiting period, whether the member can use it yet. This is an estimate for an answer to a member: it saves nothing, "
         "changes nothing and promises no payment. Use these figures and do not work them out yourself.")
    def calculate_member_benefit(
            member_id: str = mem_p,
            benefit_id: str = Path(..., description="The benefit's id in the member's own plan, for example BEN-E06."),
            amount: float = Query(..., gt=0, description="The amount of the bill in USD, for example 100."),
            visits_or_sessions: int = Query(1, ge=1, description="How many visits or sessions the amount is for. Leave at 1 for one "
                                                                 "visit, one session or a bill for medicines.")):
        m = member_or_404(member_id)
        scheme = d()["health_schemes"][m["scheme_id"]]
        benefit = next((b for b in scheme["benefits"] if b["benefit_id"] == benefit_id), None)
        if benefit is None:
            raise conflict(f"{benefit_id} is not a benefit of {m['scheme_id']}, the scheme of {member_id}. Its benefits are: "
                           f"{', '.join(b['benefit_id'] for b in scheme['benefits'])}. Nothing was worked out.")
        used = dict(m["used_this_benefit_year"].get(benefit["benefit"], {"amount": 0.0, "sessions": 0, "member_share_paid": 0.0}))
        row = usage_row(m, benefit, today())
        return {"member_id": member_id, "scheme_id": m["scheme_id"], "plan_name": scheme["plan_name"], "currency": "USD",
                **apply_benefit(benefit, used, amount, visits_or_sessions), "state": benefit["state"],
                "conditions": benefit["conditions"], "pre_authorisation_needed": benefit["pre_authorisation_needed"],
                "waiting_period": row.get("waiting_period"), "cover_on_read_date": member_cover_on(m, today()), "saved": False}

    @reg(app, "get", "/members/{member_id}/call-back-requests", "list_call_back_requests", "List the call-back requests saved for a member",
         "Read every call-back request saved for a member, each with its id, the member's question, why the documents do not settle "
         "it, who wrote it and when. A request is a draft for the member services team: it has booked nothing.")
    def list_call_back_requests(member_id: str = mem_p):
        member_or_404(member_id)
        return listing([c for c in d()["call_back_requests"].values() if c["member_id"] == member_id], member_id=member_id)

    @reg(app, "post", "/members/{member_id}/call-back-requests", "save_call_back_request", "Save a member's request for a call from a person (draft)",
         "Record that a member asks for a call from a person, with the member's question and why the scheme's documents do not settle "
         "it. This is a draft for the member services team: stored with an id, who wrote it and a time. It books no call, promises "
         "no time and tells nobody. The answer returns the request with its id, for example CB-0001.")
    def save_call_back_request(body: CallBackRequest, member_id: str = mem_p):
        member_or_404(member_id)
        with st.lock:
            cb_id = st.next_free("call_back", 1, d()["call_back_requests"], lambda n: f"CB-{n:04d}")
            record = {"call_back_id": cb_id, "member_id": member_id, "status": "draft", "question": body.question,
                      "why_the_documents_do_not_settle_it": body.why_the_documents_do_not_settle_it,
                      "drafted_by": body.drafted_by or "agent", "drafted_at": now_iso()}
            d()["call_back_requests"][cb_id] = record
            st.save()
        return {"applied": True, "kind": "draft", "draft": record,
                "message": f"{cb_id} is recorded for the member services team. No call is booked and no time is promised."}

    # ------------------------------------------------------------ medical policies
    @reg(app, "get", "/medical-policies", "list_medical_policies", "List the medical policies with their criteria",
         "Read every medical policy, whole: its id (for example MP-301), title, the procedure it is for by the insurer's code and "
         "plain name, a note on how to read it, and its numbered criteria. Every criterion must be met; a criterion the notes say "
         "nothing about is neither met nor failed. A pre-authorisation request and a held claim already carry the policy that "
         "applies to them, so this list is for a question about the policies themselves.")
    def list_medical_policies():
        return listing(list(d()["medical_policies"].values()))

    # ------------------------------------------------------------ pre-authorisation requests
    def pa_view(r):
        m = d()["health_members"][r["member_id"]]
        scheme = d()["health_schemes"][m["scheme_id"]]
        cover = member_cover_on(m, r["planned_date"])
        key = CODES.get(r["procedure_code"], (None, None))[1]
        benefit = benefit_of(scheme, key) if key else None
        row = usage_row(m, benefit, today()) if benefit else None
        label = f"{benefit['benefit_id']} {benefit['name']}" if benefit else ""
        if benefit is None:
            position, needed = "plan_is_silent", None
            sentence = (f"No benefit of {scheme['plan_name']} names {r['procedure']}. The plan's documents do not settle it.")
        elif benefit["state"] == "not_covered":
            position, needed = "not_covered_by_the_plan", None
            sentence = f"{label} is not covered by {scheme['plan_name']}, so there is nothing to pre-authorise."
        elif key == "physiotherapy":
            left = row["remaining"]["sessions"]
            needed = left == 0
            position = "needs_pre_authorisation" if needed else "no_pre_authorisation_needed"
            sentence = (f"{label}: {row['usage_sentence']} "
                        + ("Further sessions need pre-authorisation." if needed else "Sessions within the plan's need no pre-authorisation."))
        elif benefit["pre_authorisation_needed"]:
            position, needed = "needs_pre_authorisation", True
            sentence = f"{scheme['plan_name']} needs pre-authorisation for {label}."
        else:
            position, needed = "no_pre_authorisation_needed", False
            sentence = f"{scheme['plan_name']} needs no pre-authorisation for {label}."
        policy = d()["medical_policies"].get(POLICY_FOR_CODE.get(r["procedure_code"], ""))
        if not cover["in_force"]:
            policy, why = None, "No medical policy is read: the member's cover is not in force on the planned date."
        elif position != "needs_pre_authorisation":
            policy, why = None, "No medical policy is read: " + {
                "plan_is_silent": "the plan's documents do not name the procedure.",
                "not_covered_by_the_plan": "the plan does not cover the procedure.",
                "no_pre_authorisation_needed": "the plan needs no pre-authorisation for the procedure."}[position]
        elif policy is None:
            why = "The insurer holds no medical policy for this procedure. A medical reviewer reads the request."
        else:
            why = f"{policy['medical_policy_id']} applies. Read each criterion against the provider's documents."
        return ({**{k: v for k, v in r.items() if k != "assessment_drafts"},
                 "member": member_brief(m), "cover_on_planned_date": cover, "plan_benefit": row,
                 "plan_position": {"position": position, "pre_authorisation_needed": needed, "sentence": sentence},
                 "medical_policy": policy, "medical_policy_note": why,
                 "drafts_on_file": len(r["assessment_drafts"]), "read_on": today()}, policy, cover)

    @reg(app, "get", "/pre-authorisations", "list_pre_authorisation_requests", "List pre-authorisation requests",
         "List the pre-authorisation requests, whole: id, status (received, approved or declined), the member's id and name, the "
         "provider's id and name, the procedure by the insurer's code and plain name, the date requested, the planned date, the "
         "provider's documents as text, and the decision once a person has recorded one. Saved assessments are not in the list. For "
         "one request with the member's cover, the plan's position and the medical policy, use get_pre_authorisation_request.")
    def list_pre_authorisation_requests(status: str | None = Query(None, description="Only requests with this status: received, "
                                                                                     "approved or declined.")):
        return listing([{k: v for k, v in r.items() if k != "assessment_drafts"} for r in d()["pre_authorisations"].values()
                        if not status or r["status"] == status])

    @reg(app, "get", "/pre-authorisations/{pre_authorisation_id}", "get_pre_authorisation_request",
         "Get one pre-authorisation request with everything needed to assess it",
         "Read one pre-authorisation request with everything an assessment needs, in one call: the member, the provider, the "
         "procedure by code and plain name, the date requested, the planned date, and the provider's documents as text (the request "
         "form and the clinical notes). member gives the member's scheme and plan. cover_on_planned_date says whether the member's "
         "cover is in force on the planned date, with the reason and the days worked out. plan_benefit is the row of the member's own "
         "plan for this procedure, with what the member has used and has left. plan_position says in a word and a sentence whether "
         "the plan needs pre-authorisation for it, needs none, or does not cover it. medical_policy is the policy whose numbered "
         "criteria are to be read against the documents; it is empty, and medical_policy_note says why, when cover is not in force, "
         "the plan does not cover the procedure or the plan needs no pre-authorisation. decision is a person's decision once "
         "recorded. Saved assessments are not part of the request: drafts_on_file only counts them, and "
         "list_pre_authorisation_drafts reads them.")
    def get_pre_authorisation_request(pre_authorisation_id: str = pa_p):
        return pa_view(pa_or_404(pre_authorisation_id))[0]

    @reg(app, "get", "/pre-authorisations/{pre_authorisation_id}/drafts", "list_pre_authorisation_drafts",
         "List the assessments saved on a pre-authorisation request",
         "Read every assessment saved on a pre-authorisation request, each with its version number, who wrote it and when. An "
         "assessment is somebody's proposal, not a fact of the request and not a decision.")
    def list_pre_authorisation_drafts(pre_authorisation_id: str = pa_p):
        r = pa_or_404(pre_authorisation_id)
        return listing(r["assessment_drafts"], pre_authorisation_id=pre_authorisation_id)

    @reg(app, "post", "/pre-authorisations/{pre_authorisation_id}/assessment", "save_pre_authorisation_assessment",
         "Save an assessment of a pre-authorisation request (draft)",
         "Save the assessment of a pre-authorisation request: whether the member's cover is in force on the planned date, what the "
         "plan says about the procedure (when the plan is silent on it, the proposal is to refer to the assessor), one row for each criterion of the medical policy (met, not_met or not_stated, with the "
         "evidence), a proposal and the reason. This is a draft for the assessor or the medical reviewer: stored with who wrote it, "
         "a time and a version number, earlier versions kept. It approves nothing, declines nothing and contacts nobody. Refused "
         "with 409, and nothing saved, when a row names a criterion the request's medical policy does not have, when rows are sent "
         "and no medical policy is to be read, when the proposal is send_to_the_assessor_as_met and not every criterion has a row "
         "that says met, or when the proposal is ask_the_provider and no question is given.")
    def save_pre_authorisation_assessment(body: PreAuthorisationAssessment, pre_authorisation_id: str = pa_p):
        r = pa_or_404(pre_authorisation_id)
        _, policy, _ = pa_view(r)
        policy_check(body.criteria, policy, pre_authorisation_id)
        if body.proposal == "send_to_the_assessor_as_met":
            met = {c.criterion.strip() for c in body.criteria if c.finding == "met"}
            if policy is None or met != {c["number"] for c in policy["criteria"]}:
                raise conflict(f"{pre_authorisation_id} can be sent to the assessor as met only with one row for every criterion of "
                               "its medical policy, each with the finding met. Send the rows, or choose another proposal. Nothing "
                               "was saved.")
        if body.proposal == "ask_the_provider" and not body.question_for_the_provider.strip():
            raise conflict("The proposal ask_the_provider needs the question for the provider, in a sentence. Nothing was saved.")
        payload = {**body.model_dump(exclude={"drafted_by", "criteria"}), "criteria": [c.model_dump() for c in body.criteria]}
        v = st.add_draft(r, "assessment_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    @reg(app, "post", "/pre-authorisations/{pre_authorisation_id}/decision", "decide_pre_authorisation",
         "Record a person's decision on a pre-authorisation request (change)",
         "Record the decision on a pre-authorisation request: approved or declined, with the reason. This is a change and needs the "
         "name and the role of the person who decided. Refused with 409, and nothing changed, when a decision is already recorded, "
         "when an authorised assessor declines (only the medical reviewer declines), or when the request is approved and the "
         "member's cover is not in force on the planned date.")
    def decide_pre_authorisation(body: PreAuthorisationDecision, pre_authorisation_id: str = pa_p):
        r = pa_or_404(pre_authorisation_id)
        if r["decision"]:
            raise conflict(f"A decision is already recorded on {pre_authorisation_id}, by {r['decision']['decided_by']} on "
                           f"{long_date(r['decision']['decided_on'])}. Nothing was changed.")
        if body.decision == "declined" and body.role != "medical_reviewer":
            raise conflict(f"Only the medical reviewer declines a pre-authorisation request. {body.decided_by} is recorded as an "
                           "authorised assessor. Nothing was changed.")
        cover = member_cover_on(d()["health_members"][r["member_id"]], r["planned_date"])
        if body.decision == "approved" and not cover["in_force"]:
            raise conflict(f"{pre_authorisation_id} cannot be approved: {cover['reason']} Nothing was changed.")
        with st.lock:
            r["decision"] = {"decision": body.decision, "decided_by": body.decided_by, "role": body.role, "decided_on": today(),
                             "reason": body.reason}
            r["status"] = body.decision
            st.save()
        return {"applied": True, "kind": "change", "pre_authorisation_id": pre_authorisation_id, "decision": r["decision"]}

    # ------------------------------------------------------------ medical claims
    def claim_policy(c):
        if c["hold_reason"] != "medical_necessity":
            return None
        return next((d()["medical_policies"][POLICY_FOR_CODE[line["code"]]] for line in c["lines"] if line["code"] in POLICY_FOR_CODE), None)

    def claim_view(c):
        m = d()["health_members"][c["member_id"]]
        scheme = d()["health_schemes"][m["scheme_id"]]
        provider = d()["health_providers"][c["provider_id"]]
        first = min(line["date_of_service"] for line in c["lines"])
        compared = compare_with_earlier(c, d()["medical_claims"])
        policy = claim_policy(c)
        figures = claim_figures(c, m, scheme)
        out = {**{k: v for k, v in c.items() if k != "determination_drafts"},
               "provider_name": provider["name"], "member": member_brief(m),
               "cover_on_date_of_service": member_cover_on(m, first),
               "compared_with": compared,
               "compared_with_note": ("" if compared else "No earlier claim of this member carries the same code."),
               "if_paid_under_the_plan": figures,
               "medical_policy": policy,
               "medical_policy_note": (f"{policy['medical_policy_id']} applies. Read each criterion against the documents of the claim."
                                       if policy else "No medical policy is read: the claim is not held for medical necessity."),
               "drafts_on_file": len(c["determination_drafts"]), "read_on": today()}
        if policy and policy["medical_policy_id"] == "MP-302":
            used = m["used_this_benefit_year"].get("physiotherapy", {"sessions": 0})["sessions"]
            limit = benefit_of(scheme, "physiotherapy")["limit"]["sessions"]
            out["sessions_used_before_this_claim"] = {
                "used": used, "plan_gives": limit, "all_used": used >= limit,
                "sentence": f"Before this claim the member had used {used} of the {limit} physiotherapy sessions the plan gives in the "
                            f"benefit year{'' if used >= limit else ', so sessions remain'}."}
        return out

    @reg(app, "get", "/medical-claims", "list_medical_claims", "List medical claims",
         "List medical claims, whole: id, the member's id, the provider's id, status (held, decided or paid), the date received, the "
         "hold reason set by the claims engine for a held claim (duplicate, eligibility, limit or medical_necessity) with the "
         "engine's note, the amount claimed, every line (line id, the insurer's code, description, quantity, amount and date of "
         "service), the documents as text, and the decision once an assessor has recorded one. Saved determinations are not in the "
         "list. Earlier claims that were paid are listed with the status paid. For one held claim with everything an assessor "
         "needs, use get_medical_claim.")
    def list_medical_claims(status: str | None = Query(None, description="Only claims with this status: held, decided or paid."),
                            hold_reason: str | None = Query(None, description="Only claims held for this reason: duplicate, "
                                                                              "eligibility, limit or medical_necessity.")):
        return listing([{k: v for k, v in c.items() if k != "determination_drafts"} for c in d()["medical_claims"].values()
                        if (not status or c["status"] == status) and (not hold_reason or c["hold_reason"] == hold_reason)])

    @reg(app, "get", "/medical-claims/{claim_id}", "get_medical_claim", "Get one medical claim with everything needed to review it",
         "Read one medical claim with everything an assessor needs, in one call: the member with scheme and plan, the provider, the "
         "date received, the hold reason set by the claims engine with its note, every line with code, description, quantity, amount "
         "and date of service, and the documents as text. cover_on_date_of_service says whether the member's cover was in force on "
         "the date of service, with the reason and the days worked out. For a claim with several dates of service it is given "
         "for the earliest one. compared_with sets each line beside every earlier claim "
         "line of the same member with the same code: whether the provider, the date of service and the amount are the same, the "
         "days between the two dates of service, whether member, provider, date and code all match, and a sentence. "
         "if_paid_under_the_plan gives, for each line and in total, the amount within the plan's limit, the amount over it, the "
         "member's share, what the plan pays and the working; for physiotherapy sessions beyond the plan's it also gives what the "
         "plan would pay if the medical policy is met. medical_policy is the policy to read when the hold is medical necessity, "
         "and for physiotherapy sessions_used_before_this_claim says whether the member had used every session. decision is the "
         "assessor's decision once recorded. Saved determinations are not part of the claim: drafts_on_file only counts them, and "
         "list_medical_claim_drafts reads them. Use the figures given and do not add up yourself.")
    def get_medical_claim(claim_id: str = mc_p):
        return claim_view(claim_or_404(claim_id))

    @reg(app, "get", "/medical-claims/{claim_id}/drafts", "list_medical_claim_drafts", "List the determinations saved on a medical claim",
         "Read every suggested determination saved on a medical claim, each with its version number, who wrote it and when. A "
         "determination is somebody's suggestion, not a fact of the claim and not a decision.")
    def list_medical_claim_drafts(claim_id: str = mc_p):
        c = claim_or_404(claim_id)
        return listing(c["determination_drafts"], claim_id=claim_id)

    @reg(app, "post", "/medical-claims/{claim_id}/determination", "save_medical_claim_determination",
         "Save a suggested determination on a held medical claim (draft)",
         "Save a suggested determination on a held medical claim: the suggestion (pay as the plan allows, do not pay, ask the "
         "provider, or refer to the medical reviewer), the reasons, the earlier claim it repeats when it is a duplicate, and one row "
         "for each criterion of the medical policy when the hold is medical necessity. The system stores its own figures with it "
         "(within the limit, over the limit, the member's share and what the plan pays) and the answer returns them. This is a draft "
         "for the assessor: stored with who wrote it, a time and a version number. It decides nothing, pays nothing and contacts "
         "nobody. Refused with 409, and nothing saved, when the claim is not held, when duplicate_of is not a medical claim the "
         "insurer holds or is the claim itself, when a row names a criterion the claim's medical policy does not have, when rows "
         "are sent for a claim that is not held for medical necessity, or when the suggestion is ask_the_provider and no question "
         "is given.")
    def save_medical_claim_determination(body: ClaimDetermination, claim_id: str = mc_p):
        c = claim_or_404(claim_id)
        if c["status"] != "held":
            raise conflict(f"{claim_id} is not held for review: its status is {c['status']}. Nothing was saved.")
        if body.duplicate_of and (body.duplicate_of not in d()["medical_claims"] or body.duplicate_of == claim_id):
            raise conflict(f"{body.duplicate_of} is not an earlier medical claim the insurer holds. The earlier claims this one was "
                           "compared with are in compared_with of get_medical_claim. Leave duplicate_of empty when the claim is not "
                           "a duplicate. Nothing was saved.")
        policy_check(body.criteria, claim_policy(c), claim_id)
        if body.suggestion == "ask_the_provider" and not body.question_for_the_provider.strip():
            raise conflict("The suggestion ask_the_provider needs the question for the provider, in a sentence. Nothing was saved.")
        view = claim_view(c)
        figures = {k: v for k, v in view["if_paid_under_the_plan"].items() if k not in ("lines", "working", "what_this_is")}
        payload = {**body.model_dump(exclude={"drafted_by", "criteria"}), "criteria": [x.model_dump() for x in body.criteria],
                   "figures_worked_out_by_the_system": figures}
        v = st.add_draft(c, "determination_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    @reg(app, "post", "/medical-claims/{claim_id}/decision", "decide_medical_claim", "Record an assessor's decision on a held medical claim (change)",
         "Record the assessor's decision on a held medical claim: pay or do not pay, with the reason. This is a change and needs the "
         "assessor's name. For pay the system records the amount it worked out: what the plan pays, or for a claim held for medical "
         "necessity with physiotherapy sessions beyond the plan's, what the plan pays when the medical policy is met. Refused with "
         "409, and nothing changed, when the claim is not held, when a decision is already recorded, or when the decision is pay "
         "and the member's cover was not in force on the date of service.")
    def decide_medical_claim(body: ClaimDecision, claim_id: str = mc_p):
        c = claim_or_404(claim_id)
        if c["decision"]:
            raise conflict(f"A decision is already recorded on {claim_id}, by {c['decision']['decided_by']} on "
                           f"{long_date(c['decision']['decided_on'])}. Nothing was changed.")
        if c["status"] != "held":
            raise conflict(f"{claim_id} is not held for review: its status is {c['status']}. Nothing was changed.")
        view = claim_view(c)
        if body.decision == "pay" and not view["cover_on_date_of_service"]["in_force"]:
            raise conflict(f"{claim_id} cannot be paid: {view['cover_on_date_of_service']['reason']} Nothing was changed.")
        figures = view["if_paid_under_the_plan"]
        amount = 0.0
        if body.decision == "pay":
            amount = (figures.get("plan_pays_if_the_medical_policy_is_met", figures["plan_pays"])
                      if c["hold_reason"] == "medical_necessity" else figures["plan_pays"])
        with st.lock:
            c["decision"] = {"decision": body.decision, "decided_by": body.decided_by, "role": "assessor", "decided_on": today(),
                             "reason": body.reason, "amount_to_pay": amount, "currency": "USD"}
            c["status"] = "decided"
            st.save()
        return {"applied": True, "kind": "change", "claim_id": claim_id, "decision": c["decision"],
                "message": f"{claim_id} is decided: {body.decision.replace('_', ' ')}"
                           + (f", {usd(amount)}." if body.decision == "pay" else ".")}

    # ------------------------------------------------------------ providers and invoices
    @reg(app, "get", "/providers", "list_providers", "List the providers with their contracts and tariffs",
         "List the providers, whole: id, name, place, the lead doctor, the contract id, the contract as numbered clauses (number, "
         "heading and text), the two figures the clauses turn on (the discount on medicines as a percentage and the number of days "
         "within which a follow-up consultation is not charged), the tariff (each line with the insurer's code, a description, the "
         "agreed price for one unit and whether it is a medicine), and any agreement in writing on file for a service not on the "
         "tariff. Each provider has its own prices and its own figures: read the right one.")
    def list_providers():
        return listing([{**p, "tariff_line_count": len(p["tariff"])} for p in d()["health_providers"].values()])

    @reg(app, "get", "/providers/{provider_id}", "get_provider", "Get one provider with its contract and tariff",
         "Read one provider in full: name, place, the lead doctor, the contract as numbered clauses (number, heading and text), the "
         "discount on medicines as a percentage, the number of days within which a follow-up consultation is not charged, the "
         "tariff (each line with the insurer's code, a description, the agreed price for one unit and whether it is a medicine), "
         "and any agreement in writing on file for a service not on the tariff. It changes nothing.")
    def get_provider(provider_id: str = prv_p):
        p = provider_or_404(provider_id)
        return {**p, "tariff_line_count": len(p["tariff"]), "read_on": today()}

    def invoice_check(inv):
        return check_invoice(inv, d()["health_providers"][inv["provider_id"]], d()["provider_invoices"])

    @reg(app, "get", "/invoices", "list_provider_invoices", "List provider invoices",
         "List the provider invoices, whole: id, the provider's id and name, status (received, queried or accepted), the date "
         "received, the total charged, every line (line id, the insurer's code, description, quantity, the unit price charged, the "
         "amount charged, the date of service and the patient's member id), and the claims officer's decision once recorded. Saved "
         "lists of differences are not in the list. For one invoice checked against the contract, use get_provider_invoice.")
    def list_provider_invoices(status: str | None = Query(None, description="Only invoices with this status: received, queried or accepted."),
                               provider_id: str | None = Query(None, description="Only invoices of this provider, for example PRV-5101.")):
        return listing([{k: v for k, v in i.items() if k != "difference_drafts"} for i in d()["provider_invoices"].values()
                        if (not status or i["status"] == status) and (not provider_id or i["provider_id"] == provider_id)])

    @reg(app, "get", "/invoices/{invoice_id}", "get_provider_invoice", "Get one provider invoice checked against the contract",
         "Read one provider invoice with everything needed to check it, in one call: the invoice and its lines as charged, the "
         "provider's contract as numbered clauses, and check, the invoice set against the contract and tariff by the system. In "
         "check, each line gives the unit price and amount charged, whether the code is on the provider's tariff, the tariff price, "
         "the agreed unit price (for a medicine the tariff price less the contract's discount; for a follow-up consultation inside "
         "the contract's free period, nothing), the agreed amount, the difference, the kind of difference (agrees, over_the_tariff, "
         "under_the_tariff, not_on_the_tariff, follow_up_inside_the_free_period or medicines_discount_not_applied), the contract "
         "clause that governs the line and a note with the working. Every line has a clause, also a line that agrees: the clause on "
         "prices for a line charged at the agreed price, the clause on medicines for a medicine, the clause on follow-up "
         "consultations for a follow-up measured against the free period (charged or not), and the clause on services not on the "
         "tariff for a code that is not on it. A code that is not on the tariff and has an agreement in writing on file is set "
         "against the price in that agreement and is not a difference when charged at it. For a follow-up consultation it gives the same patient's first "
         "consultation, the days between the two visits worked out by the system, and whether that is inside the free period. "
         "check also gives the totals charged and agreed, the total difference, the lines with a difference and the working. Use "
         "these figures and do not add up or count days yourself. decision is the claims officer's decision once recorded. Saved "
         "lists of differences are not part of the invoice: drafts_on_file only counts them, and list_provider_invoice_drafts reads "
         "them. It contacts nobody.")
    def get_provider_invoice(invoice_id: str = pi_p):
        inv = invoice_or_404(invoice_id)
        p = d()["health_providers"][inv["provider_id"]]
        return {**{k: v for k, v in inv.items() if k != "difference_drafts"}, "contract_id": p["contract_id"], "contract": p["contract"],
                "medicines_discount_percent": p["medicines_discount_percent"],
                "follow_up_free_within_days": p["follow_up_free_within_days"], "agreements_in_writing": p["agreements_in_writing"],
                "check": invoice_check(inv), "drafts_on_file": len(inv["difference_drafts"]), "read_on": today()}

    @reg(app, "get", "/invoices/{invoice_id}/drafts", "list_provider_invoice_drafts", "List the lists of differences saved on a provider invoice",
         "Read every list of differences saved on a provider invoice, each with its version number, who wrote it and when. A list "
         "of differences is somebody's finding for the claims officer, not a decision and not a query to the provider.")
    def list_provider_invoice_drafts(invoice_id: str = pi_p):
        inv = invoice_or_404(invoice_id)
        return listing(inv["difference_drafts"], invoice_id=invoice_id)

    def lines_of(inv, line_ids, verb):
        ids = [line["line_id"] for line in inv["lines"]]
        unknown = [x for x in line_ids if x not in ids]
        if unknown:
            raise conflict(f"Not a line of {inv['invoice_id']}: {', '.join(unknown)}. Its lines are: {', '.join(ids)}. Nothing was {verb}.")

    @reg(app, "post", "/invoices/{invoice_id}/differences", "save_invoice_differences", "Save the differences found on a provider invoice (draft)",
         "Save the differences between a provider invoice and the provider's contract: the finding (agrees with the contract, or "
         "differences found) and one row for each line with a difference, with its kind, the contract clause and a note. The system "
         "stores its own totals with it (charged, agreed and the difference) and the answer returns them. This is a draft for the "
         "claims officer: stored with who wrote it, a time and a version number. It queries nothing, pays nothing and contacts "
         "nobody. Refused with 409, and nothing saved, when a row names a line that is not a line of the invoice, when the finding "
         "is differences_found and no row is sent, or when the finding is agrees_with_the_contract and rows are sent.")
    def save_invoice_differences(body: InvoiceDifferences, invoice_id: str = pi_p):
        inv = invoice_or_404(invoice_id)
        lines_of(inv, [x.line_id for x in body.differences], "saved")
        if body.finding == "differences_found" and not body.differences:
            raise conflict("The finding differences_found needs one row for each line with a difference. Nothing was saved.")
        if body.finding == "agrees_with_the_contract" and body.differences:
            raise conflict("The finding agrees_with_the_contract takes no rows. Send differences_found with the rows, or leave the "
                           "rows out. Nothing was saved.")
        check = invoice_check(inv)
        payload = {"finding": body.finding, "differences": [x.model_dump() for x in body.differences], "notes": body.notes,
                   "totals_worked_out_by_the_system": {k: check[k] for k in ("total_charged", "total_agreed", "total_difference",
                                                                             "lines_with_a_difference")}}
        v = st.add_draft(inv, "difference_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    @reg(app, "post", "/invoices/{invoice_id}/query", "record_invoice_query", "Record a claims officer's decision on a provider invoice (change)",
         "Record the claims officer's decision on a provider invoice: query named lines, or accept the invoice as charged. This is a "
         "change and needs the claims officer's name. It sets the invoice's status to queried or accepted. It does not contact the "
         "provider: the provider relations team writes to the provider. Refused with 409, and nothing changed, when a decision is "
         "already recorded, when the decision is query_the_lines and no line is named, when a line named is not a line of the "
         "invoice, or when the decision is accept_as_charged and lines are named.")
    def record_invoice_query(body: InvoiceQuery, invoice_id: str = pi_p):
        inv = invoice_or_404(invoice_id)
        if inv["decision"]:
            raise conflict(f"A decision is already recorded on {invoice_id}, by {inv['decision']['decided_by']} on "
                           f"{long_date(inv['decision']['decided_on'])}. Nothing was changed.")
        lines_of(inv, body.line_ids, "changed")
        if body.decision == "query_the_lines" and not body.line_ids:
            raise conflict("The decision query_the_lines needs the ids of the lines to query. Nothing was changed.")
        if body.decision == "accept_as_charged" and body.line_ids:
            raise conflict("The decision accept_as_charged takes no lines. Nothing was changed.")
        with st.lock:
            inv["decision"] = {"decision": body.decision, "line_ids": list(body.line_ids), "decided_by": body.decided_by,
                               "role": "claims officer", "decided_on": today(), "reason": body.reason}
            inv["status"] = "queried" if body.decision == "query_the_lines" else "accepted"
            st.save()
        return {"applied": True, "kind": "change", "invoice_id": invoice_id, "decision": inv["decision"],
                "message": f"{invoice_id} is {inv['status']}. Nobody has contacted the provider."}

    return app
