"""Reinsurance and partners: binders and treaties with numbered terms, bordereaux, paid claims with the recoveries raised,
and partners with their service levels and credentials.

Every save is a draft: the reinsurance accountant or the supplier manager decides."""

from __future__ import annotations

from typing import Any, Literal, Optional

from fastapi import Path, Query
from pydantic import Field, model_validator

from ..common import Ctx, ForgivingModel as SharedForgivingModel, _choices_of, conflict, listing, make_subapp, not_found, reg
from ..seed_policy import long_date
from ..seed_reinsurance import (BORDEREAU_KINDS, RECOVERY_LABELS, WHO_DECIDES, measure_bordereau, measure_partner, paid_total,
                                recovery_for_claim, usd)

KEY = "reinsurance"
TITLE = "Reinsurance and partners"
LINE = ("Binders and treaties with numbered terms, bordereaux, paid claims with the recoveries raised, and partners with their "
        "service levels and credentials.")

DRAFTED_BY = Field("agent", description="Who wrote the draft. Free text.")
NO_VALUE_WORDS = {"", "none", "no", "null", "nil", "na", "n a", "not needed", "not applicable", "nothing", "no step", "empty"}


class ForgivingModel(SharedForgivingModel):
    """As the shared model, and an optional fixed choice sent as an empty text, "none" and the like is no value."""

    @model_validator(mode="before")
    @classmethod
    def _read_empty_words_as_no_value(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        out = dict(data)
        for name, field in cls.model_fields.items():
            value = out.get(name)
            if isinstance(value, str) and not field.is_required() and field.default is None and _choices_of(field.annotation):
                words = " ".join(value.strip().lower().replace("/", " ").replace("-", " ").replace("_", " ").replace(".", " ").split())
                if words in NO_VALUE_WORDS:
                    out[name] = None
        return out


DIFFERENCE_KINDS = {
    "over_maximum_line": "the risk is over the maximum line",
    "outside_territory": "the risk is outside the territory",
    "class_not_allowed": "the class of business is not allowed",
    "excluded_risk": "the description puts the risk in an excluded group",
    "outside_period": "the risk or the loss is outside the period",
    "wrong_commission": "commission taken at the wrong rate",
    "wrong_share": "not the share of the treaty",
    "over_claims_authority": "a claim over the claims authority with no agreement",
    "total_does_not_add_up": "a row or a total does not add up",
    "duplicate_row": "a row declared twice",
    "other": "something else, said in the note",
}
NEXT_STEPS = {"a_person_queries_it_with_the_sender": "a person queries it with whoever sent the bordereau",
              "refer_to_the_reinsurance_accountant": "refer to the reinsurance accountant",
              "no_action": "no action"}
PARTNER_STEPS = {"no_action": "no action", "ask_the_partner_for_the_missing_figure": "a person asks the partner for the missing figure",
                 "ask_for_the_renewed_credential": "a person asks for the renewed credential",
                 "review_meeting_with_the_partner": "a review meeting with the partner"}


class BordereauDifference(ForgivingModel):
    row_number: int = Field(..., description="The number of the row the difference is on, as the bordereau numbers it. Use 0 for "
                                             "a difference in the totals of the whole bordereau.")
    kind: Literal["over_maximum_line", "outside_territory", "class_not_allowed", "excluded_risk", "outside_period",
                  "wrong_commission", "wrong_share", "over_claims_authority", "total_does_not_add_up", "duplicate_row", "other"] = Field(
        ..., description="What is wrong, in one choice: over_maximum_line, outside_territory, class_not_allowed, excluded_risk "
                         "(the description puts the risk in a group the terms exclude), outside_period, wrong_commission, "
                         "wrong_share, over_claims_authority, total_does_not_add_up, duplicate_row, or other.")
    term: str = Field(..., description="The number of the term of the binder or treaty the difference rests on, for example 3.")
    note: str = Field("", description="The figures as the system gives them, or for an excluded risk the words of the description "
                                      "and of the term.")


class BordereauDifferences(ForgivingModel):
    overall: Literal["no_differences", "differences_found"] = Field(
        ..., description="no_differences when every row is within every term and the totals add up; differences_found otherwise.")
    differences: list[BordereauDifference] = Field(default_factory=list, description="One entry for each difference. A row with "
                                                   "two differences has two entries. Leave empty when there is none.")
    suggested_step: Optional[Literal["a_person_queries_it_with_the_sender", "refer_to_the_reinsurance_accountant", "no_action"]] = Field(
        None, description="What you suggest the reinsurance accountant does next. Leave empty when you suggest nothing. It is a "
                          "suggestion: nothing is sent to anybody.")
    summary: str = Field(..., min_length=1, description="The check in a few sentences for the reinsurance accountant: how many "
                                                        "rows, which rows differ from which term with the figures the system gives, "
                                                        "and whether the totals add up. It rejects nothing.")
    drafted_by: str = DRAFTED_BY


class RecoveryRow(ForgivingModel):
    claim_id: str = Field(..., description="The id of the paid claim, for example RCL-8803.")
    treaty_id: str = Field(..., description="The id of the treaty, for example TRY-8651.")
    finding: Literal["recovery_to_raise", "recovery_raised_for_too_little", "needs_a_person"] = Field(
        ..., description="recovery_to_raise when a recovery is due and none is raised; recovery_raised_for_too_little when one is "
                         "raised for less than is due; needs_a_person when the system cannot settle it, for example a date of loss "
                         "outside the treaty period.")
    amount_to_raise: float = Field(0, ge=0, description="The amount still to raise on this claim, as the system gives it in "
                                                        "to_raise_on_this_claim. 0 for needs_a_person.")
    term: str = Field("", description="The number of the treaty term the row rests on, for example 4 for the attachment point or "
                                      "6 for one event.")
    event_id: str = Field("", description="The event id, where the claim is one of several claims from one event. Otherwise leave "
                                          "empty.")
    note: str = Field("", description="The working in a sentence, with the figures the system gives.")


class RecoveryList(ForgivingModel):
    rows: list[RecoveryRow] = Field(default_factory=list, description="One row for each claim with something to raise or to "
                                    "check. Two claims from one event have a row each. Leave empty when nothing is due.")
    claims_with_nothing_due: list[str] = Field(default_factory=list, description="The ids of the claims you checked on which "
                                               "nothing is to be raised. Leave empty when you list none.")
    summary: str = Field(..., min_length=1, description="The list in a few sentences for the reinsurance accountant: the period, "
                                                        "how many claims, what is to raise in all as the system adds it, and what "
                                                        "a person must check. It books nothing.")
    drafted_by: str = DRAFTED_BY


class PartnerFinding(ForgivingModel):
    item: str = Field(..., description="The service level, for example SL-1, or the id of a credential, for example PTN-8904-C2.")
    result: Literal["met", "not_met", "warning", "cannot_tell"] = Field(
        ..., description="met when the service level is met or the credential is valid, also when a figure is exactly on its "
                         "limit; not_met when a service level is missed or a credential has expired; warning when a credential "
                         "expires within the notice window; cannot_tell when a figure for the period is missing.")
    evidence: str = Field("", description="The measured figure and the limit as the system gives them. For cannot_tell, say what "
                                          "is missing.")


class PartnerReview(ForgivingModel):
    overall: Literal["within", "warning", "not_met", "cannot_tell"] = Field(
        ..., description="within when every service level is met and every credential is valid; warning when nothing is missed "
                         "and a credential expires within the notice window; not_met when a service level is missed or a "
                         "credential has expired; cannot_tell when a figure is missing and nothing is missed.")
    findings: list[PartnerFinding] = Field(default_factory=list, description="One entry for each service level and credential "
                                           "you report on. At least every item that is not met, a warning or cannot be told.")
    needs_a_person: Literal["yes", "no"] = Field("no", description="yes when a person must get a missing figure before the partner "
                                                                   "can be measured. Otherwise no.")
    suggested_step: Optional[Literal["no_action", "ask_the_partner_for_the_missing_figure", "ask_for_the_renewed_credential",
                                     "review_meeting_with_the_partner"]] = Field(
        None, description="What you suggest the supplier manager does next. Leave empty when you suggest nothing. It is a "
                          "suggestion: nobody is contacted.")
    summary: str = Field(..., min_length=1, description="The review in a few sentences for the supplier manager: the period, what "
                                                        "is met, what is not with the figures the system gives, and what is "
                                                        "missing. It ends no contract and contacts nobody.")
    drafted_by: str = DRAFTED_BY


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds two binders and two treaties with numbered terms, the bordereaux sent under "
                                  "them, paid claims with the recoveries already raised, and the partners (administrators, repair "
                                  "networks and suppliers) with their service levels, the month's figures and their credentials. "
                                  "Every coverholder, reinsurer and partner is invented. The system does every sum, share and day "
                                  "count and gives its working. Every save is a draft with who wrote it, a time and a version "
                                  "number. Nothing here books a recovery, pays, rejects a bordereau or contacts a reinsurer, a "
                                  "coverholder or a supplier: a person decides.")
    st = ctx.store
    d = lambda: st.data
    today = lambda: ctx.settings.insurer_today.isoformat()
    con_p = Path(..., description="Binder or treaty id, for example BND-8601 or TRY-8651.")
    bdx_p = Path(..., description="Bordereau id, for example BDX-8701.")
    clm_p = Path(..., description="Paid claim id, for example RCL-8803.")
    ptn_p = Path(..., description="Partner id, for example PTN-8901.")

    def one(name, kind, ident, hint):
        item = d()[name].get((ident or "").strip().upper())
        if not item:
            raise not_found(kind, ident, hint)
        return item

    con_or_404 = lambda i: one("ri_contracts", "binder or treaty", i, "Use list_binders_and_treaties to find ids.")
    bdx_or_404 = lambda i: one("ri_bordereaux", "bordereau", i, "Use list_bordereaux to find ids.")
    clm_or_404 = lambda i: one("ri_claims", "paid claim", i, "Use list_paid_claims_for_recovery to find ids.")
    ptn_or_404 = lambda i: one("ri_partners", "partner", i, "Use list_partners to find ids.")

    def without(record, *fields):
        return {k: v for k, v in record.items() if k not in fields}

    # ------------------------------------------------------------ binders and treaties
    @reg(app, "get", "/contracts", "list_binders_and_treaties", "List the binders and the treaties with their numbered terms",
         "List the two binders and the two treaties, whole. Each has its id, its kind with a plain label (binder, "
         "excess_of_loss_per_risk or quota_share), a title, the other side with its role (coverholder or reinsurer), the period "
         "with its first and last day, figures (the classes with code and label, the territory, the maximum line, the commission "
         "rate, the days for the premium, and for a treaty the attachment point, the limit, the share ceded and the cash call "
         "threshold), and terms: the numbered terms with a heading, the exact text and a kind. A term of the kind measured turns "
         "on a figure or a date and the system measures it. A term of the kind for_reading, such as the excluded risks, is read "
         "against the words of a row. With a kind only contracts of that kind are returned. It measures nothing itself.")
    def list_binders_and_treaties(kind: str | None = Query(None, description="Only contracts of this kind: binder, "
                                                                             "excess_of_loss_per_risk or quota_share. Leave empty "
                                                                             "for all four.")):
        wanted = "_".join((kind or "").strip().lower().replace("-", " ").split())
        kinds = ("binder", "excess_of_loss_per_risk", "quota_share")
        if wanted and wanted not in kinds:
            raise conflict(f"{kind} is not a kind here. Use one of: {', '.join(kinds)}, or leave it empty. Nothing was read.")
        return listing([c for c in d()["ri_contracts"].values() if not wanted or c["kind"] == wanted])

    @reg(app, "get", "/contracts/{contract_id}", "get_binder_or_treaty", "Get one binder or treaty with its numbered terms",
         "Read one binder or treaty: its kind with a plain label, the other side with its role, the period, the figures and every "
         "numbered term with its heading, exact text and kind (measured or for_reading). bordereaux_under_it lists the ids of the "
         "bordereaux sent under it. Quote a term by its number. It measures nothing itself: get_bordereau measures a bordereau "
         "and calculate_treaty_recovery works out a claim.")
    def get_binder_or_treaty(contract_id: str = con_p):
        c = con_or_404(contract_id)
        return {**c, "bordereaux_under_it": [b["bordereau_id"] for b in d()["ri_bordereaux"].values()
                                             if b["contract_id"] == c["contract_id"]]}

    # ------------------------------------------------------------ bordereaux
    def bordereau_brief(b):
        return {**without(b, "difference_drafts"), "rows_on_the_bordereau": len(b["rows"])}

    @reg(app, "get", "/bordereaux", "list_bordereaux", "List the bordereaux",
         "List the bordereaux, whole: id, status, the kind with a plain label (risks_bound, claims_paid or cessions), the binder "
         "or treaty it is sent under, who sent it and to whom with their roles, the month it covers, the day it was received, "
         "every row as it was sent, and the totals stated on it. With a kind only bordereaux of that kind are returned. Saved "
         "drafts are not in the list, and nor is the measure: get_bordereau gives one bordereau with the terms and the measure.")
    def list_bordereaux(kind: str | None = Query(None, description="Only bordereaux of this kind: risks_bound, claims_paid or "
                                                                   "cessions. Leave empty for all.")):
        wanted = "_".join((kind or "").strip().lower().replace("-", " ").split())
        if wanted and wanted not in BORDEREAU_KINDS:
            raise conflict(f"{kind} is not a kind here. Use one of: {', '.join(BORDEREAU_KINDS)}, or leave it empty. Nothing was read.")
        return listing([bordereau_brief(b) for b in d()["ri_bordereaux"].values() if not wanted or b["kind"] == wanted])

    @reg(app, "get", "/bordereaux/{bordereau_id}", "get_bordereau",
         "Get one bordereau with the terms it is checked against and the measure of every row",
         "Read one bordereau with everything a check needs, in one call. rows gives every row as it was sent: for risks bound the "
         "certificate, the insured, the description of the risk in words, the class with code and label, the place and country, "
         "the sum insured, the start date, the gross premium, the commission taken and the net premium; for claims paid the claim "
         "reference, the date of loss, the date paid, the indemnity, the fees, the row total and an agreement reference where the "
         "row has one; for cessions the sum insured and premium with the ceded part of each. contract gives the binder or treaty "
         "whole, with every numbered term. measured is the system's measure: for each row one entry per measured term (class, "
         "territory, maximum line, period, commission, share, claims authority, the row adds up, declared once) with the result "
         "(within or outside) and a plain label, the measured figure, the limit, the difference and a sentence. A figure exactly "
         "on a limit is within. Where a row gives the year the machinery was installed, the check machinery_age gives its age "
         "in years at the start of the risk beside the limit of the excluded risks term, so do not count the years yourself. "
         "totals gives the number of the term the totals are checked against, every column re-added by the system beside the "
         "total stated, with the difference, "
         "the commission at the rate of the term, and the totals without a row declared twice. premium_due gives the date the net "
         "premium is due and the days left or late. differences_measured lists each measured difference in one line. Use these "
         "figures and do not add or count yourself. excluded_risks_for_reading gives the term with the excluded risks: the system "
         "does not read the descriptions, that reading is yours. Saved drafts are not part of the bordereau: drafts_on_file only "
         "counts them, and list_bordereau_difference_drafts reads them.")
    def get_bordereau(bordereau_id: str = bdx_p):
        b = bdx_or_404(bordereau_id)
        contract = d()["ri_contracts"][b["contract_id"]]
        return {**bordereau_brief(b), "contract": contract, "measured": measure_bordereau(b, contract, today()),
                "drafts_on_file": len(b["difference_drafts"]), "read_on": today()}

    @reg(app, "get", "/bordereaux/{bordereau_id}/measure", "measure_bordereau_against_terms",
         "Measure every row of a bordereau against the terms and re-add the totals",
         "Measure one bordereau against the numeric and dated terms of its binder or treaty. rows has one entry for each row with "
         "its result (within or outside, with a plain label), the checks that are outside, and every check: the term number, the "
         "result, the measured figure, the limit, the difference and a sentence with the figures. A sum insured exactly on the "
         "maximum line is within. Where a row gives the year the machinery was installed, the check machinery_age measures its "
         "age in years at the start of the risk against the limit of the excluded risks term. totals gives the number of the "
         "term the totals are checked against and each column stated on the bordereau beside the system's own sum, the difference, "
         "whether the bordereau adds up, the commission at the rate of the term beside the commission taken, and the totals "
         "without a row that is declared twice. premium_due gives the due date of the net premium with the days left or late. "
         "differences_measured lists each difference in one line and counted gives the counts. The system does not read the "
         "description of a risk: excluded_risks_for_reading gives the term to read the descriptions against. It is the same "
         "measure get_bordereau carries. It saves nothing and rejects nothing.")
    def measure_bordereau_against_terms(bordereau_id: str = bdx_p):
        b = bdx_or_404(bordereau_id)
        return {**measure_bordereau(b, d()["ri_contracts"][b["contract_id"]], today()), "saved": False}

    @reg(app, "get", "/bordereaux/{bordereau_id}/drafts", "list_bordereau_difference_drafts",
         "List the difference lists saved on a bordereau",
         "Read every list of differences saved on a bordereau, each with its version number, who wrote it and when. A saved list "
         "is somebody's preparation for the reinsurance accountant, not a fact of the bordereau and not a rejection.")
    def list_bordereau_difference_drafts(bordereau_id: str = bdx_p):
        b = bdx_or_404(bordereau_id)
        return listing(b["difference_drafts"], bordereau_id=b["bordereau_id"])

    @reg(app, "post", "/bordereaux/{bordereau_id}/differences", "save_bordereau_differences",
         "Save the list of differences on a bordereau (draft)",
         "Save what the check of a bordereau found: whether there are differences, one entry for each difference with the row "
         "number, what is wrong, the term it rests on and a note, a suggested next step where you have one, and a summary. The "
         "system stores its own measured differences and totals with it and the answer returns them. This is a draft for the "
         "reinsurance accountant: stored with who wrote it, a time and a version number, earlier versions kept. It rejects no "
         "bordereau, changes no premium, contacts no coverholder and no reinsurer, and it changes nothing else. Refused with 409, "
         "and nothing saved, when a row number is not a row of the bordereau (0 is the totals), when a term is not a term of the "
         "binder or treaty, when overall is no_differences and differences are listed, or when overall is differences_found and "
         "none is listed.")
    def save_bordereau_differences(body: BordereauDifferences, bordereau_id: str = bdx_p):
        b = bdx_or_404(bordereau_id)
        contract = d()["ri_contracts"][b["contract_id"]]
        numbers = [r["row_number"] for r in b["rows"]]
        terms = [t["term"] for t in contract["terms"]]
        entries = []
        for x in body.differences:
            term = x.term.strip().lower().replace("term", "").strip()
            if x.row_number != 0 and x.row_number not in numbers:
                raise conflict(f"Row {x.row_number} is not a row of {b['bordereau_id']}. The rows run from {numbers[0]} to "
                               f"{numbers[-1]}; use 0 for the totals. Nothing was saved.")
            if term not in terms:
                raise conflict(f"{x.term} is not a term of {contract['contract_id']}. The terms are {', '.join(terms)}. Nothing "
                               "was saved.")
            entries.append({**x.model_dump(), "term": term, "kind_label": DIFFERENCE_KINDS[x.kind]})
        if body.overall == "no_differences" and entries:
            raise conflict("overall is no_differences and differences are listed. Use differences_found, or leave the list empty. "
                           "Nothing was saved.")
        if body.overall == "differences_found" and not entries:
            raise conflict("overall is differences_found and no difference is listed. List each one, or use no_differences. "
                           "Nothing was saved.")
        m = measure_bordereau(b, contract, today())
        payload = {"overall": body.overall, "differences": entries, "suggested_step": body.suggested_step,
                   "suggested_step_label": NEXT_STEPS[body.suggested_step] if body.suggested_step else None,
                   "summary": body.summary, "goes_to": WHO_DECIDES["reinsurance"],
                   "measured_by_the_system": {"differences_measured": m["differences_measured"], "counted": m["counted"],
                                              "totals_add_up": m["totals"]["adds_up"]}}
        v = st.add_draft(b, "difference_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v,
                "message": f"The list of differences is saved on {b['bordereau_id']} as a draft. The bordereau is unchanged, "
                           "nothing is rejected and nobody is told."}

    # ------------------------------------------------------------ paid claims and recoveries
    def claim_view(c):
        calc = recovery_for_claim(c, d())
        return {**c, "paid_total": paid_total(c),
                "event": d()["ri_events"].get(c["event_id"]) if c["event_id"] else None,
                "recoveries_raised_on_this_claim": [r for r in d()["ri_recoveries"].values() if r["claim_id"] == c["claim_id"]],
                "recovery": calc}

    @reg(app, "get", "/paid-claims", "list_paid_claims_for_recovery",
         "List the paid claims of a period with what each recovers under the treaties",
         "List the paid claims with a payment in a period, whole, each with the recovery worked out. A claim has its id, the "
         "insured, the class with code and label, what happened, the date of loss, every payment with its date and amount, "
         "paid_total as the system adds it, the event where several claims arise from one event, and the recoveries already raised "
         "on it. recovery is the system's working for the claim, the same as calculate_treaty_recovery gives: the treaty year the "
         "date of loss falls in, the amount recoverable under each treaty with the working, what is raised, what is still to "
         "raise, a status with a plain label, and to_raise_on_this_claim. paid_from and paid_to bound the period by the date of a "
         "payment; with neither, the period runs from the first day of the treaty year to the insurer date. The whole paid amount "
         "of a claim is measured, not only the payments in the period. summary counts the claims by status and adds what is to "
         "raise. Use these figures and do not add or take a share yourself. Saved recovery lists are not in the answer: "
         "recovery_list_drafts_on_file only counts them, and list_recovery_list_drafts reads them.")
    def list_paid_claims_for_recovery(
            paid_from: str | None = Query(None, description="First day of the period, as YYYY-MM-DD. Leave empty for the first "
                                                            "day of the treaty year."),
            paid_to: str | None = Query(None, description="Last day of the period, as YYYY-MM-DD. Leave empty for the insurer date.")):
        from datetime import date as _date
        treaty_start = min(c["period_start"] for c in d()["ri_contracts"].values() if c["kind"] != "binder")
        first, last = (paid_from or "").strip() or treaty_start, (paid_to or "").strip() or today()
        for label, value in (("paid_from", first), ("paid_to", last)):
            try:
                _date.fromisoformat(value)
            except ValueError:
                raise conflict(f"{label} must be a date written as YYYY-MM-DD, and {value} is not. Nothing was read.")
        if first > last:
            raise conflict(f"paid_from ({first}) is after paid_to ({last}). Nothing was read.")
        rows = [claim_view(c) for c in d()["ri_claims"].values() if any(first <= p["paid_on"] <= last for p in c["payments"])]
        by_status = {}
        for r in rows:
            by_status.setdefault(r["recovery"]["status"], []).append(r["claim_id"])
        total = round(sum(r["recovery"]["to_raise_on_this_claim"] for r in rows), 2)
        to_raise = [r["claim_id"] for r in rows if r["recovery"]["to_raise_on_this_claim"] > 0]
        summary = {"claims": len(rows),
                   "by_status": [{"status": s, "status_label": RECOVERY_LABELS[s], "claims": ids} for s, ids in by_status.items()],
                   "claims_with_something_to_raise": to_raise, "to_raise_in_all": total,
                   "claims_that_need_a_person": [r["claim_id"] for r in rows if r["recovery"]["needs_a_person"]],
                   "sentence": f"{len(rows)} paid claims have a payment from {long_date(first)} to {long_date(last)}. "
                               f"{len(to_raise)} have something to raise: {usd(total)} in all."}
        return listing(rows, period={"paid_from": first, "paid_to": last}, summary=summary,
                       recovery_list_drafts_on_file=len(d()["ri_recovery_lists"]["RLIST-8800"]["drafts"]), read_on=today())

    @reg(app, "get", "/paid-claims/{claim_id}", "get_paid_claim", "Get one paid claim with its payments, its event and its recovery",
         "Read one paid claim with everything a recovery needs, in one call: the insured, the class with code and label, what "
         "happened, the date of loss, every payment with its date and amount, paid_total as the system adds it, the event with "
         "the other claims that arise from it where there is one, the recoveries already raised on the claim, and recovery: the "
         "system's working, the same as calculate_treaty_recovery gives. It books nothing.")
    def get_paid_claim(claim_id: str = clm_p):
        return {**claim_view(clm_or_404(claim_id)), "read_on": today()}

    @reg(app, "get", "/paid-claims/{claim_id}/recovery", "calculate_treaty_recovery",
         "Work out what a paid claim recovers under each treaty, with the working",
         "Work out, for one paid claim, the amount recoverable under each treaty. paid_total is what was paid on the claim, added "
         "by the system. treaty_year says which treaty year the date of loss falls in, or that it falls outside the period. "
         "under_each_treaty has one entry for each treaty: whether it applies, a status with a plain label, and a sentence. For "
         "the excess of loss treaty it gives the loss measured (the sum of every claim of one event where the claim carries an "
         "event id, under the one event term), the attachment point, the limit, the part above the attachment point, the part "
         "above the limit that stays with the insurer, the amount recoverable, what is raised so far with the recovery ids, what "
         "is still to raise, the reinstatement premium with its working, and for an event each claim's share. For the quota share "
         "treaty it gives the reinsurer's share and whether it is collected by a cash call or in the quarterly account. working "
         "lists every step as a sentence with the figures. A paid loss exactly on the attachment point recovers nothing. status "
         "is one of nothing_due, recovery_to_raise, recovery_raised_for_too_little, recovery_raised_in_full, "
         "outside_the_treaty_period or collected_in_the_quarterly_account. to_raise_on_this_claim is the amount for this claim. "
         "It is a calculation: it saves nothing, raises nothing and tells no reinsurer.")
    def calculate_treaty_recovery(claim_id: str = clm_p):
        return {**recovery_for_claim(clm_or_404(claim_id), d()), "saved": False}

    @reg(app, "get", "/recoveries", "list_recoveries_raised", "List the recoveries already raised",
         "List every recovery and cash call the reinsurance accountant has raised: id, the claim, the treaty, the kind with a "
         "plain label, the amount, the day it was raised, the role that raised it, the paid loss as it stood on that day and a "
         "note. With a claim id only that claim's recoveries are returned. A recovery raised earlier may be for less than is due "
         "now, where a later payment was made: calculate_treaty_recovery gives the difference.")
    def list_recoveries_raised(claim_id: str | None = Query(None, description="Only recoveries on this paid claim, for example "
                                                                               "RCL-8804. Leave empty for all.")):
        wanted = (claim_id or "").strip().upper()
        if wanted:
            clm_or_404(wanted)
        return listing([r for r in d()["ri_recoveries"].values() if not wanted or r["claim_id"] == wanted])

    @reg(app, "get", "/recovery-lists/drafts", "list_recovery_list_drafts", "List the recovery lists saved",
         "Read every recovery list saved, each with its version number, who wrote it and when. A saved list is somebody's "
         "preparation for the reinsurance accountant, not a recovery that was raised and not a fact of any claim.")
    def list_recovery_list_drafts():
        return listing(d()["ri_recovery_lists"]["RLIST-8800"]["drafts"], recovery_list_id="RLIST-8800")

    @reg(app, "post", "/recovery-lists", "save_recovery_list", "Save a recovery list (draft)",
         "Save a list of recoveries to raise: one row for each claim with the treaty, the finding (recovery_to_raise, "
         "recovery_raised_for_too_little or needs_a_person), the amount still to raise, the term and a note; the claims checked "
         "with nothing due; and a summary. The system stores its own figure beside each row (the status and the amount to raise "
         "as it works them out, and whether the row agrees) and its own total, and the answer returns them. This is a draft for "
         "the reinsurance accountant: stored with who wrote it, a time and a version number, earlier versions kept. It raises no "
         "recovery, books nothing, pays no reinstatement premium and tells no reinsurer, and it changes nothing else: not a "
         "claim, not the recoveries raised. Refused with 409, and nothing saved, when a claim is not a paid claim of this system, "
         "when a treaty is not one of the two treaties, when the same claim and treaty are given twice, or when a claim is both in "
         "a row and among the claims with nothing due.")
    def save_recovery_list(body: RecoveryList):
        claims, contracts = d()["ri_claims"], d()["ri_contracts"]
        treaties = [k for k, c in contracts.items() if c["kind"] != "binder"]
        rows, seen = [], []
        for r in body.rows:
            cid, tid = r.claim_id.strip().upper(), r.treaty_id.strip().upper()
            if cid not in claims:
                raise conflict(f"{r.claim_id} is not a paid claim of this system. Use list_paid_claims_for_recovery to find ids. "
                               "Nothing was saved.")
            if tid not in treaties:
                raise conflict(f"{r.treaty_id} is not a treaty. The treaties are {', '.join(treaties)}. Nothing was saved.")
            if (cid, tid) in seen:
                raise conflict(f"{cid} under {tid} is given twice. Each claim has one row for a treaty. Nothing was saved.")
            seen.append((cid, tid))
            line = next(x for x in recovery_for_claim(claims[cid], d())["under_each_treaty"] if x["treaty_id"] == tid)
            rows.append({**r.model_dump(), "claim_id": cid, "treaty_id": tid, "event_id": r.event_id.strip().upper() or None,
                         "amount_to_raise": round(r.amount_to_raise, 2),
                         "worked_out_by_the_system": {"status": line["status"], "status_label": line["status_label"],
                                                      "to_raise_on_this_claim": line["to_raise_on_this_claim"],
                                                      "agrees": round(r.amount_to_raise, 2) == line["to_raise_on_this_claim"]}})
        nothing = [x.strip().upper() for x in body.claims_with_nothing_due if x and x.strip()]
        unknown = [x for x in nothing if x not in claims]
        if unknown:
            raise conflict(f"Not a paid claim of this system: {', '.join(unknown)}. Nothing was saved.")
        both = sorted({x for x in nothing if x in [c for c, _ in seen]})
        if both:
            raise conflict(f"Both in a row and among the claims with nothing due: {', '.join(both)}. A claim is in one place. "
                           "Nothing was saved.")
        payload = {"rows": rows, "claims_with_nothing_due": nothing, "summary": body.summary, "goes_to": WHO_DECIDES["reinsurance"],
                   "added_by_the_system": {"rows": len(rows), "amount_to_raise_as_listed": round(sum(r["amount_to_raise"] for r in rows), 2),
                                           "amount_to_raise_as_the_system_works_it_out": round(
                                               sum(r["worked_out_by_the_system"]["to_raise_on_this_claim"] for r in rows), 2),
                                           "rows_that_do_not_agree": [f"{r['claim_id']} {r['treaty_id']}" for r in rows
                                                                      if not r["worked_out_by_the_system"]["agrees"]]}}
        v = st.add_draft(d()["ri_recovery_lists"]["RLIST-8800"], "drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v,
                "message": "The recovery list is saved as a draft. No recovery is raised, nothing is booked and no reinsurer is told."}

    # ------------------------------------------------------------ partners
    def partner_view(p):
        return {**without(p, "review_drafts"), "measured": measure_partner(p, today()), "drafts_on_file": len(p["review_drafts"])}

    @reg(app, "get", "/partners", "list_partners", "List the partners with their service levels, figures, credentials and measure",
         "List the partners, whole: id, name, the kind with a plain label (administrator, repair_network or supplier), what the "
         "partner does, contract with the numbered service levels SL-1 to SL-4 (the metric with a plain label, the limit, the unit "
         "and the exact text) and the credentials term SL-5 with the notice window in days, period with the month and the figures "
         "reported for it (jobs, the average turnaround in days, complaints, repairs done again for a repair network, the day the "
         "monthly report was received; a figure that is empty was not reported), credentials with kind, name, issuer and expiry "
         "date, and measured: the system's measure on the insurer date, the same as measure_partner_against_service_levels gives. "
         "With a kind only partners of that kind are returned. Saved reviews are not in the list: drafts_on_file only counts them.")
    def list_partners(kind: str | None = Query(None, description="Only partners of this kind: administrator, repair_network or "
                                                                 "supplier. Leave empty for all.")):
        wanted = "_".join((kind or "").strip().lower().replace("-", " ").split())
        kinds = ("administrator", "repair_network", "supplier")
        if wanted and wanted not in kinds:
            raise conflict(f"{kind} is not a kind here. Use one of: {', '.join(kinds)}, or leave it empty. Nothing was read.")
        return listing([partner_view(p) for p in d()["ri_partners"].values() if not wanted or p["kind"] == wanted], measured_on=today())

    @reg(app, "get", "/partners/{partner_id}", "get_partner", "Get one partner with its service levels, figures, credentials and measure",
         "Read one partner with everything a review needs, in one call: the kind with a plain label, what the partner does, the "
         "contract's numbered service levels with their limits and exact text, the credentials term with the notice window, the "
         "month's figures as reported, the credentials with their expiry dates, and measured: the system's measure on the insurer "
         "date, the same as measure_partner_against_service_levels gives. Saved reviews are not part of the partner: "
         "drafts_on_file only counts them, and list_partner_review_drafts reads them.")
    def get_partner(partner_id: str = ptn_p):
        return {**partner_view(ptn_or_404(partner_id)), "read_on": today()}

    @reg(app, "get", "/partners/{partner_id}/measure", "measure_partner_against_service_levels",
         "Measure a partner against its service levels and credentials on the insurer date",
         "Measure one partner. service_levels has one entry for each service level of its contract: the term, the metric with a "
         "plain label, the result (met, not_met or cannot_tell, with a plain label), the measured figure, the limit, the unit, "
         "the difference, the working of a rate (count / jobs x 100) and a sentence. A figure exactly on a limit is met. A figure "
         "that was not reported gives cannot_tell: nothing is assumed and a person must get it. For the monthly report it gives "
         "the due date, the day received and the days late. credentials has one entry for each credential: the expiry date, the "
         "days to expiry counted from the insurer date (negative when it has passed), and the result with a plain label: valid, "
         "expires_within_the_notice_window (a warning, not a miss) or expired. A credential is valid up to and including its "
         "expiry date. not_met, cannot_tell and warnings list the items by id. overall is one of within, warning, not_met or "
         "cannot_tell, with a plain label; needs_a_person says whether a person must get a figure. goes_to names the role that "
         "decides. It saves nothing, ends no contract and contacts nobody.")
    def measure_partner_against_service_levels(partner_id: str = ptn_p):
        return {**measure_partner(ptn_or_404(partner_id), today()), "saved": False}

    @reg(app, "get", "/partners/{partner_id}/drafts", "list_partner_review_drafts", "List the reviews saved on a partner",
         "Read every review saved on a partner, each with its version number, who wrote it and when. A saved review is somebody's "
         "preparation for the supplier manager, not a fact of the partner and not a decision about its contract.")
    def list_partner_review_drafts(partner_id: str = ptn_p):
        p = ptn_or_404(partner_id)
        return listing(p["review_drafts"], partner_id=p["partner_id"])

    @reg(app, "post", "/partners/{partner_id}/review", "save_partner_review", "Save a review of a partner (draft)",
         "Save the review of one partner: the overall result (within, warning, not_met or cannot_tell), one finding for each "
         "service level or credential you report on (met, not_met, warning or cannot_tell, with the evidence), whether a person "
         "is needed, a suggested next step where you have one, and a summary. The system stores its own measure with it (the "
         "overall result, and the items not met, warned and not told) and the answer returns it. This is a draft for the supplier "
         "manager: stored with who wrote it, a time and a version number, earlier versions kept. It ends no contract, suspends "
         "nobody and contacts no partner, and it changes nothing else. Refused with 409, and nothing saved, when an item is not a "
         "service level or a credential of this partner, or when an item is given twice.")
    def save_partner_review(body: PartnerReview, partner_id: str = ptn_p):
        p = ptn_or_404(partner_id)
        known = [s["term"] for s in p["contract"]["service_levels"]] + [c["credential_id"] for c in p["credentials"]]
        sent = [f.item.strip().upper() for f in body.findings]
        unknown = [i for i in sent if i not in known]
        if unknown:
            raise conflict(f"Not a service level or a credential of {p['partner_id']}: {', '.join(unknown)}. Its items are "
                           f"{', '.join(known)}. Nothing was saved.")
        twice = sorted({i for i in sent if sent.count(i) > 1})
        if twice:
            raise conflict(f"Given twice: {', '.join(twice)}. Each item has one finding. Nothing was saved.")
        m = measure_partner(p, today())
        payload = {"overall": body.overall, "findings": [{**f.model_dump(), "item": i} for f, i in zip(body.findings, sent)],
                   "needs_a_person": body.needs_a_person, "suggested_step": body.suggested_step,
                   "suggested_step_label": PARTNER_STEPS[body.suggested_step] if body.suggested_step else None,
                   "summary": body.summary, "goes_to": WHO_DECIDES["partners"],
                   "measured_by_the_system": {"overall": m["overall"], "overall_label": m["overall_label"], "not_met": m["not_met"],
                                              "warnings": m["warnings"], "cannot_tell": m["cannot_tell"],
                                              "needs_a_person": m["needs_a_person"]}}
        v = st.add_draft(p, "review_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v,
                "message": f"The review is saved on {p['partner_id']} as a draft. The partner's record is unchanged and nobody is "
                           "contacted."}

    return app
