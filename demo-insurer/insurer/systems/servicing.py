"""Servicing: the servicing rules, change requests, certificate requests with the certificate and endorsement templates,
a policy as it stands on a date, and the broker desk. Every save is a draft: a servicing officer decides."""

from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import Field

from ..common import Ctx, conflict, ForgivingModel, listing, make_subapp, not_found, reg
from ..seed_policy import long_date
from ..seed_servicing import (ENDORSEMENT_HOW_TO_USE, RATING_AREAS, RULES_HOW_TO_READ, book_of, check_certificate_request,
                              claim_for_broker, claims_on_policy, find_claim, find_policy, gap_between, last_day_of_cover,
                              measure_change, policy_as_it_stands, premium_pro_rata, return_premium_on_cancellation, terms_of)

KEY = "servicing"
TITLE = "Policy servicing"
LINE = ("The servicing rules, change requests, certificate requests with the certificate and endorsement templates, a policy as it "
        "stands on a date, and the broker desk: brokers, the policies each one places, and what a broker may be told.")

DRAFTED_BY = Field("agent", description="Who wrote the draft. Free text.")


class ChangeDraft(ForgivingModel):
    next_step: Literal["ready_for_the_servicing_officer", "refer_to_underwriting", "refer_to_the_team_leader", "ask_the_requester"] = Field(
        ..., description="ready_for_the_servicing_officer when no referral rule applies; refer_to_underwriting when rule SR-2, SR-3 "
                         "or SR-5 applies; refer_to_the_team_leader when rule SR-1, SR-4 or SR-8 applies; ask_the_requester when "
                         "the request lacks something. The system's own answer is next_step_by_the_rules on the change request. "
                         "No value changes the policy.")
    rules_that_apply: list[str] = Field(default_factory=list, description="The servicing rules that apply, by id, for example SR-3, "
                                                                          "as the system gives them. Leave empty when none applies.")
    gap_in_cover: Literal["yes", "no", "not_checked"] = Field(
        "not_checked", description="yes when the system's gap check finds a day without cover; no when it finds none; not_checked "
                                   "when the request ends no cover or names no new cover.")
    points_to_raise: list[str] = Field(default_factory=list, description="What the servicing officer should see, one point each, "
                                       "with the dates, days and amounts as the system gives them: a gap in cover, an effective "
                                       "date before the insurer date, an open claim. Leave empty when there is none.")
    question_for_the_requester: str = Field("", description="What to ask, in a sentence. Needed when the next step is "
                                                            "ask_the_requester. Otherwise leave empty.")
    summary: str = Field(..., min_length=1, description="The change in a few sentences for the servicing officer: who asks, what "
                                                        "changes and from which date, the premium adjustment with the system's "
                                                        "working, and the rules that apply.")
    drafted_by: str = DRAFTED_BY


class EndorsementDraft(ForgivingModel):
    template_id: str = Field(..., description="The endorsement template used, for example ET-ADDRESS. It must be the template for "
                                              "this kind of change.")
    effective_date: str = Field("", description="The effective date of the endorsement as YYYY-MM-DD. It must be the effective "
                                                "date of the change request. Leave empty and the system fills it in.")
    endorsement_text: str = Field(..., min_length=1, description="The endorsement wording in full, paragraph by paragraph, from the "
                                                                 "template and the policy as it stands.")
    notes: str = Field("", description="Anything the servicing officer should know. Leave empty when there is nothing.")
    drafted_by: str = DRAFTED_BY


class CertificateDraft(ForgivingModel):
    can_be_prepared_as_asked: Literal["yes", "no"] = Field(
        ..., description="What the system's check says: yes when everything the request asks to be shown is on the policy as it "
                         "stands on the certificate date; no when the request asks for a higher limit, a party or a waiver the "
                         "policy does not hold, or the policy is not in force on that date.")
    next_step: Literal["ready_for_the_servicing_officer", "refer_to_the_servicing_officer", "ask_the_requester"] = Field(
        ..., description="ready_for_the_servicing_officer when the certificate can be prepared as asked; "
                         "refer_to_the_servicing_officer when it cannot: the officer decides what happens next; ask_the_requester "
                         "when the request lacks something. No value issues a certificate.")
    differences: list[str] = Field(default_factory=list, description="Each point where the request asks for something the policy "
                                   "does not hold on the certificate date, with the figures as the system gives them. Leave empty "
                                   "when there is none.")
    certificate_text: str = Field("", description="The certificate in full, paragraph by paragraph, from the template and the "
                                                  "policy as it stands on the certificate date. It shows only what the policy "
                                                  "holds. Leave empty when the policy is not in force on the certificate date.")
    notes: str = Field("", description="Anything the servicing officer should know. Leave empty when there is nothing.")
    drafted_by: str = DRAFTED_BY


class CallBack(ForgivingModel):
    policy_id: str | None = Field(None, description="The policy the question is about, when there is one. It must be a policy the "
                                                    "broker places.")
    claim_id: str | None = Field(None, description="The claim the question is about, when there is one. It must be a claim on a "
                                                   "policy the broker places.")
    question: str = Field(..., min_length=1, description="The broker's question, in the broker's words.")
    why_the_records_do_not_settle_it: str = Field("", description="Why the answer could not be given from the records, in a "
                                                                  "sentence. Leave empty when you cannot say.")
    caller_name: str = Field("", description="The person at the broker who asks. Leave empty when not known.")
    drafted_by: str = DRAFTED_BY


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds the servicing rules as numbered rules, change requests, certificate requests, "
                                  "the certificate template and the endorsement templates, and the broker desk: brokers, the "
                                  "policies each one places and what a broker may be told about a policy or a claim. The system "
                                  "does every sum, day count and comparison. Every save is a draft with who wrote it, a time and a "
                                  "version number. Nothing here changes a policy, issues a document or sends anything to a "
                                  "customer or a broker: a servicing officer decides.")
    st = ctx.store
    d = lambda: st.data
    today = lambda: ctx.settings.insurer_today.isoformat()
    chg_p = Path(..., description="Change request id, for example CHG-7301.")
    crq_p = Path(..., description="Certificate request id, for example CRQ-7401.")
    pol_p = Path(..., description="Policy id, for example POL-2001.")
    brk_p = Path(..., description="Broker id, for example BRK-7501.")

    def one(name, kind, ident, hint):
        item = d()[name].get(ident)
        if not item:
            raise not_found(kind, ident, hint)
        return item

    chg_or_404 = lambda i: one("sv_change_requests", "change request", i, "Use list_change_requests to find ids.")
    crq_or_404 = lambda i: one("sv_certificate_requests", "certificate request", i, "Use list_certificate_requests to find ids.")
    brk_or_404 = lambda i: one("sv_brokers", "broker", i, "Use list_brokers to find ids.")

    def policy_or_404(policy_id):
        p, _ = find_policy(d(), policy_id)
        if not p:
            raise not_found("policy", policy_id, "The policy id is on the change request or the certificate request.")
        return p

    def iso(value, name):
        try:
            return date.fromisoformat((value or "").strip()).isoformat()
        except ValueError:
            raise HTTPException(422, f"{name} is not a valid date: {value}. Send it as YYYY-MM-DD, for example 2026-12-01. "
                                     "Nothing was worked out.")

    def without(record, *fields):
        return {k: v for k, v in record.items() if k not in fields}

    # ------------------------------------------------------------ rules and change requests
    @reg(app, "get", "/rules", "get_servicing_rules", "Get the servicing rules as numbered rules",
         "Read the servicing rules SR-1 to SR-8, each with its id, heading, kind (referral, calculation or point_to_raise), who a "
         "referral goes to, and its text with the exact test: backdating, a change of address to another rating area, an increase "
         "in a sum insured, a cancellation with an open claim, a young driver, the premium adjustment pro rata, a gap in cover, "
         "and a policy not in force on the effective date. It also gives the three rating areas of Meridia. A value exactly on a "
         "limit does not make a rule apply. It measures no request: get_change_request gives a request measured against these "
         "rules.")
    def get_servicing_rules():
        return listing(list(d()["sv_rules"].values()), document="Servicing rules", version="5", how_to_read=RULES_HOW_TO_READ,
                       rating_areas=[{"rating_area": code, "town": town} for town, code in RATING_AREAS.items()])

    def change_view(c):
        return {**without(c, "change_drafts", "endorsement_drafts"), **measure_change(c, d(), today()),
                "change_drafts_on_file": len(c["change_drafts"]), "endorsement_drafts_on_file": len(c["endorsement_drafts"]),
                "drafts_on_file": len(c["change_drafts"]) + len(c["endorsement_drafts"]), "read_on": today()}

    @reg(app, "get", "/change-requests", "list_change_requests", "List the change requests received",
         "List the requests for a mid-term change, whole: id, status, the date received, the policy id, who asked (name, role and "
         "channel), the kind of change (address, vehicle, sum_insured, add_driver or cancellation), the effective date asked for, "
         "the details of the change, the new annual premium from the rating engine where there is one, and the request in the "
         "requester's words. Saved drafts are not in the list. For one request measured against the rules, with the premium "
         "adjustment and the gap check, use get_change_request.")
    def list_change_requests(change_type: str | None = Query(None, description="Only requests of this kind: address, vehicle, "
                                                                               "sum_insured, add_driver or cancellation.")):
        return listing([without(c, "change_drafts", "endorsement_drafts") for c in d()["sv_change_requests"].values()
                        if not change_type or c["change_type"] == change_type])

    @reg(app, "get", "/change-requests/{change_request_id}", "get_change_request",
         "Get one change request with everything needed to prepare the change",
         "Read one change request with everything a draft change needs, in one call: who asked, the kind of change, the effective "
         "date, the details and the request text. policy_as_it_stands_on_the_effective_date gives the policy with its schedule, "
         "endorsements in effect, cover on that date and the annual premium. claims_on_the_policy lists every claim on the policy "
         "with whether it is open. dates gives the days the effective date is before the date received and before the insurer "
         "date, with a sentence. what_changes sets the present value beside the requested one (for an address the two rating "
         "areas; for a sum insured the increase as an amount and a percentage; for a driver the age on the effective date). rules "
         "has one row for each referral rule with whether it applies, the measured value, the limit, who it sends the request to "
         "and a sentence; then rules_that_apply, referral_needed, refer_to and next_step_by_the_rules. premium_adjustment is the "
         "system's sum: whether it was worked out, the kind (additional_premium, return_premium, no_change or not_worked_out), "
         "the amount, the days counted and the working in a sentence. gap_in_cover gives the days without cover between the end "
         "of this cover and new cover, with the dates. points_to_raise_by_rule_sr_7 lists what must be pointed out to the "
         "officer. Use these figures and do not add up, count days or compare yourself. Saved drafts are not part of the request: "
         "drafts_on_file only counts them, and list_change_drafts and list_endorsement_drafts read them. It changes nothing.")
    def get_change_request(change_request_id: str = chg_p):
        return change_view(chg_or_404(change_request_id))

    @reg(app, "get", "/change-requests/{change_request_id}/drafts", "list_change_drafts", "List the draft changes saved on a change request",
         "Read every draft change saved on a change request, each with its version number, who wrote it and when. A saved draft is "
         "somebody's preparation for the servicing officer, not a fact of the request and not a change to the policy.")
    def list_change_drafts(change_request_id: str = chg_p):
        return listing(chg_or_404(change_request_id)["change_drafts"], change_request_id=change_request_id)

    @reg(app, "post", "/change-requests/{change_request_id}/draft", "save_change_draft", "Save a draft change on a change request (draft)",
         "Save the change prepared on a change request: the next step, the rules that apply, whether the gap check found a gap, "
         "the points to raise and a summary. The system stores its own measure with it (the rules that apply, the next step by the "
         "rules, the premium adjustment and the gap check) and the answer returns it. This is a draft for the servicing officer: "
         "stored with who wrote it, a time and a version number, earlier versions kept. It changes no policy, charges and returns "
         "no premium, cancels nothing and contacts nobody, and it changes nothing else. Refused with 409, and nothing saved, when "
         "a rule named is not a servicing rule, when the next step is ready_for_the_servicing_officer and a referral rule applies, "
         "when the gap answer differs from the system's gap check, or when the next step is ask_the_requester and no question is "
         "given.")
    def save_change_draft(body: ChangeDraft, change_request_id: str = chg_p):
        c = chg_or_404(change_request_id)
        rules = [x.strip().upper() for x in body.rules_that_apply]
        unknown = [x for x in rules if x not in d()["sv_rules"]]
        if unknown:
            raise conflict(f"Not a servicing rule (SR-1 to SR-8): {', '.join(unknown)}. Nothing was saved.")
        m = measure_change(c, d(), today())
        if body.next_step == "ready_for_the_servicing_officer" and m["referral_needed"]:
            raise conflict(f"On {change_request_id} the system finds that {', '.join(m['rules_that_apply'])} "
                           f"{'applies' if len(m['rules_that_apply']) == 1 else 'apply'}: the request goes to "
                           f"{' and '.join(m['refer_to'])} first. Choose that next step. Nothing was saved.")
        found = m["gap_in_cover"]["gap_in_cover"]
        if (body.gap_in_cover == "yes" and found is not True) or (body.gap_in_cover == "no" and found is True):
            raise conflict(f"The gap answer differs from the system's gap check on {change_request_id}. {m['gap_in_cover']['sentence']} "
                           "Nothing was saved.")
        if body.next_step == "ask_the_requester" and not body.question_for_the_requester.strip():
            raise conflict("The next step ask_the_requester needs the question, in a sentence. Nothing was saved.")
        measured = {k: m[k] for k in ("rules_that_apply", "referral_needed", "refer_to", "next_step_by_the_rules")}
        measured["premium_adjustment"] = {k: m["premium_adjustment"].get(k) for k in ("worked_out", "kind", "amount", "working", "note")}
        measured["gap_in_cover"] = {k: m["gap_in_cover"].get(k) for k in ("checked", "gap_in_cover", "days_without_cover", "sentence")}
        payload = {**body.model_dump(exclude={"drafted_by", "rules_that_apply"}), "rules_that_apply": rules,
                   "measured_by_the_system": measured}
        v = st.add_draft(c, "change_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v,
                "message": f"The change is saved on {change_request_id} as a draft. The policy and the request itself are unchanged."}

    @reg(app, "get", "/change-requests/{change_request_id}/endorsement-drafts", "list_endorsement_drafts",
         "List the draft endorsements saved on a change request",
         "Read every draft endorsement saved on a change request, each with its version number, who wrote it and when. A draft "
         "endorsement is wording for the servicing officer to read. It is not part of the policy.")
    def list_endorsement_drafts(change_request_id: str = chg_p):
        return listing(chg_or_404(change_request_id)["endorsement_drafts"], change_request_id=change_request_id)

    @reg(app, "post", "/change-requests/{change_request_id}/endorsement", "save_endorsement_draft",
         "Save a draft endorsement on a change request (draft)",
         "Save the endorsement wording prepared for a change request: the template used, the effective date and the wording in "
         "full. The system stores the request's effective date and its own premium adjustment with it. This is a draft for the "
         "servicing officer: stored with who wrote it, a time and a version number, earlier versions kept. It adds no endorsement "
         "to the policy, issues nothing and sends nothing, and it changes nothing else. Refused with 409, and nothing saved, when "
         "the template is not an endorsement template, when the template is for another kind of change, or when the effective "
         "date given is not the effective date of the request.")
    def save_endorsement_draft(body: EndorsementDraft, change_request_id: str = chg_p):
        c = chg_or_404(change_request_id)
        templates = d()["sv_endorsement_templates"]
        hits = [t for t in templates if t.replace("-", "").lower() == body.template_id.strip().replace("-", "").replace(" ", "").lower()]
        if not hits:
            raise conflict(f"{body.template_id} is not an endorsement template. Use one of: {', '.join(templates)}. Nothing was saved.")
        template = templates[hits[0]]
        if template["for_change_type"] != c["change_type"]:
            right = next(t["template_id"] for t in templates.values() if t["for_change_type"] == c["change_type"])
            raise conflict(f"{template['template_id']} is the template for the change {template['for_change_type']}. "
                           f"{change_request_id} is a change of the kind {c['change_type']}: use {right}. Nothing was saved.")
        if body.effective_date.strip() and iso(body.effective_date, "effective_date") != c["effective_date"]:
            raise conflict(f"The effective date of {change_request_id} is {long_date(c['effective_date'])} ({c['effective_date']}). "
                           "The endorsement takes effect on that date. Nothing was saved.")
        m = measure_change(c, d(), today())
        payload = {"template_id": template["template_id"], "effective_date": c["effective_date"], "endorsement_text": body.endorsement_text,
                   "notes": body.notes,
                   "premium_adjustment_by_the_system": {k: m["premium_adjustment"].get(k) for k in ("worked_out", "kind", "amount", "working", "note")}}
        v = st.add_draft(c, "endorsement_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v,
                "message": f"The endorsement is saved on {change_request_id} as a draft. Nothing is added to the policy."}

    # ------------------------------------------------------------ a policy on a date, and the two sums
    @reg(app, "get", "/policies/{policy_id}/as-it-stands", "get_policy_as_it_stands_on_date",
         "Get a policy as it stands on a date, with the endorsements in effect",
         "Read one policy as it stands on one date. The answer gives the holder, address and rating area, the status, the period "
         "with the days in it, the wording id, and cover_on_the_date (in_force and a sentence with the days worked out). "
         "schedule_on_the_date is the schedule with every endorsement in effect on that date applied, so a limit an endorsement "
         "changed mid-term shows the figure that held on the date asked. endorsements_in_effect and "
         "endorsements_not_yet_in_effect list the endorsements on each side of the date; changed_by_endorsement says which figure "
         "an endorsement changed, from what to what and from which date. interested_parties lists the parties named in the "
         "schedule. waiver_of_rights_of_recovery says whether the wording or an endorsement holds a waiver. annual_premium is "
         "the premium for the period. With no date the insurer date is used. It reads policies of the policy system and the "
         "policies held in this system (POL-28..). Use this answer and do not work out days or pick a limit yourself. It "
         "changes nothing.")
    def get_policy_as_it_stands_on_date(policy_id: str = pol_p,
                                        on: str | None = Query(None, description="The date, as YYYY-MM-DD, for example 2026-10-12. "
                                                                                 "Leave empty for the insurer date.")):
        policy_or_404(policy_id)
        return {**policy_as_it_stands(d(), policy_id, iso(on, "on") if on else today(), today()), "read_on": today()}

    @reg(app, "get", "/policies/{policy_id}/premium-adjustment", "calculate_premium_adjustment",
         "Work out the premium adjustment pro rata for a change",
         "Work out, under rule SR-6, what a mid-term change costs or returns. For a change of premium send the effective date and "
         "the new annual premium: the answer gives the difference a year, the days in the period, the days that remain from the "
         "effective date to the last day of the period, the amount, its kind (additional_premium, return_premium or no_change) "
         "and the working in a sentence. For a cancellation send the effective date as the cancellation date and cancellation as "
         "true: the answer gives the return premium for the days after that date, and works out nothing when the policy has an "
         "open claim (rule SR-4). When the date is outside the policy period nothing is worked out and the note says why. The "
         "present annual premium is the one servicing holds. Use the amount given and do not do the sum yourself. It saves "
         "nothing and changes nothing.")
    def calculate_premium_adjustment(
            policy_id: str = pol_p,
            effective_on: str = Query(..., description="The effective date of the change, or the cancellation date, as YYYY-MM-DD."),
            new_annual_premium: float | None = Query(None, ge=0, description="The new annual premium in USD, from the rating "
                                                     "engine. Leave empty for a cancellation."),
            cancellation: bool = Query(False, description="true to work out the return premium on a cancellation.")):
        p = policy_or_404(policy_id)
        eff = iso(effective_on, "effective_on")
        annual = terms_of(d(), policy_id).get("annual_premium")
        if cancellation:
            answer = return_premium_on_cancellation(p, annual, eff, [c for c in claims_on_policy(d(), policy_id) if c["open"]])
        elif new_annual_premium is None:
            raise conflict("Send new_annual_premium for a change of premium, or cancellation=true for a cancellation. Nothing was "
                           "worked out.")
        else:
            answer = premium_pro_rata(p, annual, new_annual_premium, eff)
        return {"policy_id": policy_id, "effective_on": eff, "cancellation": cancellation, **answer, "saved": False}

    @reg(app, "get", "/policies/{policy_id}/gap-in-cover", "check_gap_in_cover", "Check for days without cover between two dates",
         "Say whether there are days without cover between the end of this policy's cover and the start of new cover, under rule "
         "SR-7. Send the date new cover starts. Send cover_ends_on when cover would end on another date than the policy's own last "
         "day, for example the date of a cancellation that is asked for; with none, the policy's own last day of cover is used "
         "(the last day of the period, or the day before a cancellation already made). The answer gives gap_in_cover (true or "
         "false), the number of days without cover, the first and the last day without cover, the days of overlap when new cover "
         "starts early, and a sentence. Cover runs to the end of its last day, so new cover that starts the next day leaves no "
         "gap. Use this answer and do not count days yourself. It saves nothing and changes nothing.")
    def check_gap_in_cover(
            policy_id: str = pol_p,
            new_cover_starts_on: str = Query(..., description="The first day of the new cover, a renewal or a replacement policy, "
                                                              "as YYYY-MM-DD."),
            cover_ends_on: str | None = Query(None, description="The last day of this cover, as YYYY-MM-DD, when it is not the "
                                                                "policy's own last day. Leave empty to use the policy's own.")):
        p = policy_or_404(policy_id)
        ends = iso(cover_ends_on, "cover_ends_on") if cover_ends_on else last_day_of_cover(p)
        return {"policy_id": policy_id, "cover_end_taken_from": "the request" if cover_ends_on else "the policy",
                **gap_between(ends, iso(new_cover_starts_on, "new_cover_starts_on")), "saved": False}

    # ------------------------------------------------------------ certificates and endorsement templates
    @reg(app, "get", "/certificate-template", "get_certificate_template", "Get the certificate of insurance template",
         "Read the template for a certificate of insurance: its id, title, version, a note on how to use it, and its numbered "
         "paragraphs. Words in square brackets are filled from the policy as it stands on the certificate date. Paragraph 7 is "
         "copied word for word. A certificate shows only what the policy holds: never a limit, a party or a waiver the policy does "
         "not hold. It prepares nothing itself.")
    def get_certificate_template():
        return dict(d()["sv_certificate_templates"]["CT-COI-1"])

    @reg(app, "get", "/endorsement-templates", "get_endorsement_templates", "Get the endorsement templates",
         "Read the endorsement templates, one for each kind of change: ET-ADDRESS, ET-VEHICLE, ET-SUM-INSURED, ET-DRIVER and "
         "ET-CANCELLATION. Each has its id, the kind of change it is for, a title and its numbered paragraphs. Words in square "
         "brackets are filled from the change request and the policy as it stands on the effective date. Paragraph 4 is copied "
         "word for word. With a kind of change only that template is returned. It prepares nothing itself.")
    def get_endorsement_templates(change_type: str | None = Query(None, description="Only the template for this kind of change: "
                                                                  "address, vehicle, sum_insured, add_driver or cancellation.")):
        return listing([t for t in d()["sv_endorsement_templates"].values() if not change_type or t["for_change_type"] == change_type],
                       document="Endorsement templates", version="3", how_to_use=ENDORSEMENT_HOW_TO_USE)

    @reg(app, "get", "/certificate-requests", "list_certificate_requests", "List the certificate requests received",
         "List the requests for a certificate of insurance, whole: id, status, the date received, the policy id, who asked, the "
         "certificate holder with name and address, the certificate date, what the certificate must show (each item with its id, "
         "kind and any figure or party asked for) and the request in the requester's words. Saved drafts are not in the list. For "
         "one request checked against the policy, use get_certificate_request.")
    def list_certificate_requests():
        return listing([without(r, "certificate_drafts") for r in d()["sv_certificate_requests"].values()])

    @reg(app, "get", "/certificate-requests/{certificate_request_id}", "get_certificate_request",
         "Get one certificate request checked against the policy as it stands",
         "Read one certificate request with everything a draft certificate needs, in one call: the certificate holder, the "
         "certificate date, what the certificate must show and the request text. checked_against_the_policy is the system's "
         "check: one row for cover on the certificate date and one for each item asked, each with a result (in_force_on_the_date, "
         "not_in_force_on_the_date, matches_the_policy, shown_from_the_policy when the request names no figure, "
         "higher_than_the_policy, lower_than_the_policy or not_on_the_policy), what was asked, what the policy holds and a "
         "sentence; then can_be_prepared_as_asked (true or false), differences (one sentence for each point the policy does not "
         "hold) and a sentence. policy_as_it_stands_on_the_certificate_date gives the policy with the schedule and the "
         "endorsements in effect on that date: a limit changed by a later endorsement shows the earlier figure. Use these answers "
         "and do not compare figures or dates yourself. Saved drafts are not part of the request: drafts_on_file only counts them, "
         "and list_certificate_drafts reads them. It issues nothing.")
    def get_certificate_request(certificate_request_id: str = crq_p):
        r = crq_or_404(certificate_request_id)
        check = check_certificate_request(r, d(), today())
        stands = check.pop("policy_as_it_stands_on_the_certificate_date")
        return {**without(r, "certificate_drafts"), "checked_against_the_policy": check,
                "policy_as_it_stands_on_the_certificate_date": stands, "drafts_on_file": len(r["certificate_drafts"]),
                "read_on": today()}

    @reg(app, "get", "/certificate-requests/{certificate_request_id}/drafts", "list_certificate_drafts",
         "List the draft certificates saved on a certificate request",
         "Read every draft certificate saved on a certificate request, each with its version number, who wrote it and when. A "
         "draft is for the servicing officer to read. It is not a certificate and nothing was issued.")
    def list_certificate_drafts(certificate_request_id: str = crq_p):
        return listing(crq_or_404(certificate_request_id)["certificate_drafts"], certificate_request_id=certificate_request_id)

    @reg(app, "post", "/certificate-requests/{certificate_request_id}/certificate", "save_certificate_draft",
         "Save a draft certificate on a certificate request (draft)",
         "Save the certificate prepared on a certificate request: whether it can be prepared as asked, the next step, each "
         "difference between the request and the policy, and the certificate text. The system stores its own check with it "
         "(can_be_prepared_as_asked and the differences) and the answer returns it. This is a draft for the servicing officer: "
         "stored with who wrote it, a time and a version number, earlier versions kept. It issues no certificate, sends nothing to "
         "the certificate holder and changes no policy, and it changes nothing else. Refused with 409, and nothing saved, when the "
         "answer to can_be_prepared_as_asked differs from the system's check, when the next step is "
         "ready_for_the_servicing_officer and the system finds a difference, or when the certificate can be prepared as asked and "
         "no certificate text is given.")
    def save_certificate_draft(body: CertificateDraft, certificate_request_id: str = crq_p):
        r = crq_or_404(certificate_request_id)
        check = check_certificate_request(r, d(), today())
        as_asked = check["can_be_prepared_as_asked"]
        if (body.can_be_prepared_as_asked == "yes") != as_asked:
            raise conflict(f"The system's check on {certificate_request_id} says can_be_prepared_as_asked is "
                           f"{'yes' if as_asked else 'no'}. {' '.join(check['differences']) or check['sentence']} Nothing was saved.")
        if body.next_step == "ready_for_the_servicing_officer" and not as_asked:
            raise conflict(f"The certificate on {certificate_request_id} cannot be prepared as asked, so the next step is "
                           "refer_to_the_servicing_officer or ask_the_requester. Nothing was saved.")
        if as_asked and not body.certificate_text.strip():
            raise conflict("The certificate can be prepared as asked, so the certificate text is needed. Nothing was saved.")
        payload = {**body.model_dump(exclude={"drafted_by"}), "certificate_date": r["certificate_date"],
                   "checked_by_the_system": {"can_be_prepared_as_asked": as_asked, "differences": check["differences"]}}
        v = st.add_draft(r, "certificate_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v,
                "message": f"The certificate is saved on {certificate_request_id} as a draft. No certificate is issued."}

    # ------------------------------------------------------------ the broker desk
    def refuse(broker, what):
        return HTTPException(403, f"{what} is not in the book of {broker['name']} ({broker['broker_id']}). A broker is told nothing "
                                  "about a policy or a claim that is not its own client's. Nothing was read out.")

    def claims_in_book(broker_id):
        book = book_of(d(), broker_id)
        ids = [c["claim_id"] for c in d()["claims"].values() if c["policy_id"] in book]
        return ids + [c["claim_id"] for c in d()["sv_claims"].values() if c["policy_id"] in book]

    def broker_view(b):
        rows = []
        for pid in book_of(d(), b["broker_id"]):
            p, held = find_policy(d(), pid)
            rows.append({"policy_id": pid, "holder": p["holder"], "product": p["product"], "status": p["status"],
                         "period_start": p["period_start"], "period_end": p["period_end"], "held_in": held,
                         "claims": [c["claim_id"] for c in claims_on_policy(d(), pid)]})
        return {**without(b, "call_back_requests"), "policies_placed": rows, "policies_placed_count": len(rows),
                "call_back_requests_on_file": len(b["call_back_requests"])}

    @reg(app, "get", "/brokers", "list_brokers", "List the brokers",
         "List the brokers: id, name, address, the contact person and the number of policies each one places. The list gives no "
         "book, so that one broker's clients are never read out while another broker is served: get_broker gives one broker's "
         "own book. Saved call-back requests are not in the list.")
    def list_brokers():
        return listing([{**without(b, "call_back_requests"), "policies_placed_count": len(book_of(d(), b["broker_id"]))}
                        for b in d()["sv_brokers"].values()])

    @reg(app, "get", "/brokers/{broker_id}", "get_broker", "Get one broker with the policies it places",
         "Read one broker: id, name, address, the contact person, and policies_placed, the broker's book: every policy the broker "
         "places with its holder, product, status, period and the ids of the claims on it. A policy or claim that is not in this "
         "list is not the broker's and nothing about it is given to the broker. call_back_requests_on_file only counts the saved "
         "call-back requests; list_broker_call_back_requests reads them.")
    def get_broker(broker_id: str = brk_p):
        return {**broker_view(brk_or_404(broker_id)), "read_on": today()}

    @reg(app, "get", "/brokers/{broker_id}/book-check", "check_broker_book", "Say whether a policy or a claim belongs to a broker's book",
         "Say whether one policy or one claim is in a broker's book. Send a policy id or a claim id. The answer gives in_book (true "
         "or false) and a sentence. A claim is in the book when it is on a policy the broker places. When in_book is false the "
         "broker is told nothing about the record, not even whether it exists, and the answer names no other broker. It reads "
         "out nothing of the record itself.")
    def check_broker_book(broker_id: str = brk_p,
                          policy_id: str | None = Query(None, description="The policy to check, for example POL-2009."),
                          claim_id: str | None = Query(None, description="The claim to check, for example SCL-7801.")):
        b = brk_or_404(broker_id)
        if bool(policy_id) == bool(claim_id):
            raise conflict("Send one policy id or one claim id, not both and not neither. Nothing was checked.")
        ident = (policy_id or claim_id).strip().upper()
        inside = ident in (book_of(d(), broker_id) if policy_id else claims_in_book(broker_id))
        return {"broker_id": broker_id, "checked": ident, "kind": "policy" if policy_id else "claim", "in_book": inside,
                "sentence": (f"{ident} is in the book of {b['name']}." if inside else
                             f"{ident} is not in the book of {b['name']}. The broker is told nothing about it.")}

    @reg(app, "get", "/brokers/{broker_id}/policies/{policy_id}", "get_policy_for_broker", "Get a policy for the broker who places it",
         "Read one policy for a broker. The read is refused with 403 and a plain sentence when the policy is not in the broker's "
         "book: nothing about another broker's client is given, and the same refusal is given for a policy id that does not "
         "exist. For a policy in the book the answer gives the policy as it stands on the insurer date, or on the date sent: "
         "holder, address, status, period, cover on the date with a sentence, the schedule with the endorsements in effect "
         "applied, the endorsements, interested parties, the wording id, the annual premium, and the ids of the claims on the "
         "policy. The source to cite is the policy id and, for a figure, the schedule. It changes nothing.")
    def get_policy_for_broker(broker_id: str = brk_p, policy_id: str = pol_p,
                              on: str | None = Query(None, description="The date, as YYYY-MM-DD. Leave empty for the insurer date.")):
        b = brk_or_404(broker_id)
        if policy_id not in book_of(d(), broker_id):
            raise refuse(b, policy_id)
        stands = policy_as_it_stands(d(), policy_id, iso(on, "on") if on else today(), today())
        return {"broker_id": broker_id, **without(stands, "placed_by_broker", "rating_area"),
                "claims_on_the_policy": [c["claim_id"] for c in claims_on_policy(d(), policy_id)],
                "source": f"Policy {policy_id}, held in {stands['held_in']}.", "read_on": today()}

    @reg(app, "get", "/brokers/{broker_id}/claims/{claim_id}", "get_claim_status_for_broker",
         "Get what a broker may be told about a claim of its own client",
         "Read the status of one claim for a broker. The read is refused with 403 and a plain sentence when the claim is not on a "
         "policy in the broker's book, and the same refusal is given for a claim id that does not exist. For a claim in the book "
         "the answer gives only what a broker may be told: the policy, the policyholder, the kind of claim, the dates of the loss "
         "and the report, the stage (reported, waiting_for_documents, under_review, part_paid, decided or paid) with "
         "stage_in_words, what_is_outstanding (what the client or broker is asked for), last_payment (date, amount and who was "
         "paid) with a sentence, and a recorded decision to decline with its clause and reason. held_back names what is never "
         "given to a broker: the reserve, internal notes, and anything about an internal review of the file. This list is the "
         "same for every claim. When the stage is under_review, say that the claim is under review and nothing more. When the "
         "answer does not hold what the broker asks, the records are silent: save a call-back request. The source to cite is the "
         "claim id. It changes nothing.")
    def get_claim_status_for_broker(broker_id: str = brk_p, claim_id: str = Path(..., description="Claim id, for example SCL-7801.")):
        b = brk_or_404(broker_id)
        if claim_id not in claims_in_book(broker_id):
            raise refuse(b, claim_id)
        _, held = find_claim(d(), claim_id)
        return {"broker_id": broker_id, **claim_for_broker(d(), claim_id), "source": f"Claim {claim_id}, held in {held}.",
                "read_on": today()}

    @reg(app, "get", "/broker-queries", "list_broker_queries", "List the questions brokers have sent in",
         "List the questions received from brokers, whole: id, the broker id, the person who asks, the date received and the "
         "question in the broker's words. With a broker id only that broker's questions are returned. A question is answered "
         "from the broker's own book only. The list holds no answers.")
    def list_broker_queries(broker_id: str | None = Query(None, description="Only questions from this broker, for example BRK-7501.")):
        return listing([q for q in d()["sv_broker_queries"].values() if not broker_id or q["broker_id"] == broker_id])

    @reg(app, "get", "/brokers/{broker_id}/call-backs", "list_broker_call_back_requests", "List the call-back requests saved for a broker",
         "Read every call-back request saved for a broker, each with its id, version number, who wrote it and when, the policy or "
         "claim it is about, the question and why the records did not settle it. A saved request books nothing and promises no "
         "time.")
    def list_broker_call_back_requests(broker_id: str = brk_p):
        return listing(brk_or_404(broker_id)["call_back_requests"], broker_id=broker_id)

    @reg(app, "post", "/brokers/{broker_id}/call-backs", "save_broker_call_back_request",
         "Save a broker's request for a call from a person (draft)",
         "Save a broker's request to be called back by a person, for a question the records do not settle: the question, the "
         "policy or claim it is about when there is one, and why the records did not settle it. This is a draft for the broker "
         "desk: stored with an id, who wrote it, a time and a version number. It books no call, promises no time, sends nothing "
         "to the broker and changes nothing else. Refused with 403, and nothing saved, when the policy or claim named is not in "
         "the broker's book.")
    def save_broker_call_back_request(body: CallBack, broker_id: str = brk_p):
        b = brk_or_404(broker_id)
        pid = (body.policy_id or "").strip().upper() or None
        cid = (body.claim_id or "").strip().upper() or None
        if pid and pid not in book_of(d(), broker_id):
            raise refuse(b, pid)
        if cid and cid not in claims_in_book(broker_id):
            raise refuse(b, cid)
        payload = {"call_back_id": f"CBK-{broker_id[4:]}-{len(b['call_back_requests']) + 1}", "broker_id": broker_id,
                   **body.model_dump(exclude={"drafted_by", "policy_id", "claim_id"}), "policy_id": pid, "claim_id": cid,
                   "status": "draft"}
        v = st.add_draft(b, "call_back_requests", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v,
                "message": f"The call-back request is saved for {b['name']} as a draft. No call is booked and no time is promised."}

    return app
