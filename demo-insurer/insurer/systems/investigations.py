"""Investigations: closed claims for the leakage review with the handling standards, new claims for the fraud check
with the indicators, claims referred to the investigations desk, the parties on them and public notices."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import Field

from ..common import Ctx, conflict, ForgivingModel, listing, make_subapp, not_found, reg
from ..seed_investigations import (INDICATORS_HOW_TO_APPLY, LINK_NOTE, STANDARDS_HOW_TO_APPLY, claim_links, earlier_claims, is_person,
                                   leakage_check, notices_for_party, party_view, run_indicators, shared_attributes)
from ..seed_policy import cover_on, long_date

KEY = "investigations"
TITLE = "Investigations"
LINE = ("Closed claims for the leakage review with the handling standards, new claims for the fraud check with the indicators, "
        "claims referred to the investigations desk, the parties on them and public notices.")

DRAFTED_BY = Field("agent", description="Who wrote the draft. Free text.")
REVIEW_DAYS = 30
STATUS_WORDS = {"new": "waiting for the fraud check", "flagged": "referred to the investigations desk", "closed": "closed"}


def tidy_id(value: str) -> str:
    """LS 1, ls-1 and LS_1 are read as LS-1."""
    return "-".join(value.strip().upper().replace("_", " ").replace("-", " ").split())


class StandardFinding(ForgivingModel):
    standard_id: str = Field(..., description="The id of the handling standard, for example LS-2.")
    finding: Literal["not_met", "cannot_tell", "met"] = Field(
        ..., description="The result the calculation gives for this standard on this claim: not_met, cannot_tell or met.")
    note: str = Field("", description="The figures the result rests on, as the calculation gives them, with the line or payment id.")


class LeakageFinding(ForgivingModel):
    outcome: Literal["paid_within_the_standards", "paid_outside_the_standards", "cannot_tell_needs_a_person"] = Field(
        ..., description="paid_within_the_standards when every standard is met; paid_outside_the_standards when one or more is "
                         "not met; cannot_tell_needs_a_person when the record is incomplete and a standard cannot be tested.")
    standards: list[StandardFinding] = Field(default_factory=list, description="One row for each standard that is not met or cannot be "
                                             "told. Leave the list empty when the claim was paid within the standards.")
    what_is_missing: str = Field("", description="What the file lacks, in a sentence, when the outcome is cannot_tell_needs_a_person, "
                                                 "for example the invoice a payment was made against. Otherwise leave empty.")
    notes: str = Field("", description="Anything else the claims quality team should know.")
    drafted_by: str = DRAFTED_BY


class IndicatorFinding(ForgivingModel):
    indicator_id: str = Field(..., description="The id of the indicator that is met, for example FI-1.")
    note: str = Field("", description="The measured value and the threshold, as run_fraud_indicators gives them.")


class FraudReferral(ForgivingModel):
    proposal: Literal["refer_to_the_investigations_desk", "no_referral_continue_handling"] = Field(
        ..., description="refer_to_the_investigations_desk when one or more indicators are met; no_referral_continue_handling when "
                         "none is met. Neither value declines the claim, and neither says that the claim is false.")
    indicators_met: list[IndicatorFinding] = Field(default_factory=list, description="One row for each indicator that is met. Leave "
                                                   "the list empty when no indicator is met.")
    reasons: str = Field(..., min_length=1, description="Why this proposal, in one or two sentences, with the figures the system gave. "
                                                        "When no indicator is met, say so.")
    notes: str = Field("", description="Anything else the investigator or the handler should know, for example a person with the "
                                       "claimant's name who is not the claimant.")
    drafted_by: str = DRAFTED_BY


class EarlierClaim(ForgivingModel):
    claim_id: str = Field(..., description="The id of the earlier claim, for example CLM-6041.")
    note: str = Field("", description="Whose claim it is and what it was for, in a few words.")


class CaseLink(ForgivingModel):
    link_type: Literal["repairer", "witness", "phone", "address", "bank_account", "party_on_both_claims", "other"] = Field(
        ..., description="What the two records share, in the word get_claim_links gives.")
    linked_claim_id: str | None = Field(None, description="The other claim the link leads to, for example CLM-6302. Leave empty when "
                                                          "the link is between two parties and no other claim.")
    through_party_id: str | None = Field(None, description="The party the link runs through, for example PTY-3501 for a repairer or "
                                                           "PTY-3028 for a witness. Leave empty when there is none.")
    note: str = Field(..., min_length=1, description="What the records show, in a sentence. State the link as a fact of the records. "
                                                     "Do not say what it means about any person.")


class CaseNotice(ForgivingModel):
    notice_id: str = Field(..., description="The id of the public notice, for example PN-901.")
    about: Literal["the_same_person", "a_different_person", "cannot_tell"] = Field(
        ..., description="Whether the notice is about the party, as get_public_notices_for_party gives it: the_same_person when the "
                         "name, the date of birth and the address agree; a_different_person when the date of birth differs; "
                         "cannot_tell otherwise.")
    note: str = Field("", description="What the notice says and which identifiers agree or differ.")


class CaseFile(ForgivingModel):
    summary: str = Field(..., min_length=1, description="The case file's summary, in plain sentences: the claim, why it was referred, "
                                                        "and what the records show. It accuses nobody.")
    earlier_claims: list[EarlierClaim] = Field(default_factory=list, description="The earlier claims of the parties on this claim, one "
                                               "row each. Leave the list empty when there are none.")
    links_found: Literal["links_found", "no_links_found"] = Field(
        ..., description="links_found when the claim shares a repairer, a witness, a phone number, an address or a bank account with "
                         "another claim or party; no_links_found when it shares none.")
    links: list[CaseLink] = Field(default_factory=list, description="One row for each link. Leave the list empty when no link was found.")
    public_notices: list[CaseNotice] = Field(default_factory=list, description="One row for each public notice that names a person "
                                             "with the name of a party on the claim, also when it is about a different person. "
                                             "Leave the list empty when there is none.")
    open_points: list[str] = Field(default_factory=list, description="What the investigator may want to check next, one point each. "
                                                                     "Empty when there is none.")
    drafted_by: str = DRAFTED_BY


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system serves the claims quality team and the investigations desk. It holds closed claims with "
                                  "their payment files and the handling standards they are reviewed against; new claims with the "
                                  "fraud indicators they are checked against; claims referred to the investigations desk; the "
                                  "parties on those claims; and public notices. The system does every sum and count. Nothing here "
                                  "declines a claim, pays a claim or says that a person did wrong: an agent prepares, a person "
                                  "decides. Every save is a draft, stored with who wrote it, a time and a version number.")
    st = ctx.store
    d = lambda: st.data
    today = lambda: ctx.settings.insurer_today.isoformat()
    closed_p = Path(..., description="Closed claim id, for example CLM-6103.")
    clm_p = Path(..., description="Claim id, for example CLM-6205.")
    pty_p = Path(..., description="Party id, for example PTY-3021.")

    def policy_of(policy_id):
        """The policy from the policy system, or from this system's own set. None for an earlier policy that has ended."""
        return d()["policies"].get(policy_id) or d()["investigation_policies"].get(policy_id)

    def policy_brief(policy_id):
        p = policy_of(policy_id)
        if not p:
            return None
        keys = ("policy_id", "product", "wording_id", "wording_version", "holder", "address", "status", "period_start", "period_end", "schedule")
        return {**{k: p[k] for k in keys},
                "held_in": "the policy system" if policy_id in d()["policies"] else "the investigations system only"}

    def closed_or_404(i):
        c = d()["leakage_claims"].get(i)
        if not c:
            hint = ("It is a claim held for checking: read it with get_claim_for_checking." if i in d()["investigation_claims"]
                    else "Use list_closed_claims_for_review to find ids.")
            raise not_found("closed claim in the leakage review", i, hint)
        return c

    def claim_or_404(i):
        c = d()["investigation_claims"].get(i)
        if not c:
            hint = ("It is a closed claim in the leakage review: read it with get_closed_claim_payment_file." if i in d()["leakage_claims"]
                    else "Use list_claims_for_fraud_check or list_flagged_claims to find ids. This system holds the claims passed to "
                         "it, CLM-6xxx.")
            raise not_found("claim held for checking", i, hint)
        return c

    def party_or_404(i):
        p = d()["investigation_parties"].get(i)
        if not p:
            raise not_found("party", i, "Use search_parties with a name to find the id.")
        return p

    def check_date(on):
        try:
            return date.fromisoformat(on)
        except ValueError:
            raise HTTPException(422, f"The date {on} is not valid. Send it as YYYY-MM-DD, for example 2026-11-17. Nothing was read.")

    def check(c):
        return leakage_check(c, policy_of(c["policy_id"]), d()["handling_guide"])

    # ------------------------------------------------------------ leakage review
    @reg(app, "get", "/handling-standards", "get_claims_handling_standards", "Get the handling standards a closed claim is reviewed against",
         "Read the handling standards of the leakage review, whole: each with its id (LS-1 to LS-6), a title and its text, and a note "
         "on how they are applied. They cover the deductible, the limits of the policy wording, the approval a payment needs, a "
         "recovery where another party is at fault, an invoice paid twice, and cover on the date of the loss. The amounts in them "
         "are the insurer's own. To test one closed claim against them, use calculate_what_should_have_been_paid.")
    def get_claims_handling_standards():
        return listing(list(d()["leakage_standards"].values()), how_to_apply=STANDARDS_HOW_TO_APPLY)

    def closed_view(c):
        return {**{k: v for k, v in c.items() if k != "leakage_finding_drafts"}, "drafts_on_file": len(c["leakage_finding_drafts"])}

    @reg(app, "get", "/closed-claims", "list_closed_claims_for_review", "List the closed claims of a review period",
         "List the closed claims whose date of closing is in a review period, whole. With no dates the period is the 30 days up to "
         "the insurer date. The answer says which period it used. Each claim has its id, the policy id, the claimant, the claim "
         "type, the dates of the loss, the report and the closing, a description, another party the file names as at fault, and the "
         "payment file: the invoices with their lines (line id, description, category and amount), the settlement record (what the "
         "handler allowed on each line, the deductible taken, who approved and any second approval), every payment (payment id, "
         "date, payee, invoice number and amount) with the total paid, whether a recovery was raised, and the file notes. It does "
         "not test the claims against the standards: calculate_what_should_have_been_paid does that for one claim. Saved findings "
         "are not in the list: drafts_on_file only counts them.")
    def list_closed_claims_for_review(
            closed_from: str | None = Query(None, description="First day of the review period, as YYYY-MM-DD. Leave empty for 30 days "
                                                              "before the insurer date."),
            closed_to: str | None = Query(None, description="Last day of the review period, as YYYY-MM-DD. Leave empty for the insurer date.")):
        end = check_date(closed_to) if closed_to else ctx.settings.insurer_today
        start = check_date(closed_from) if closed_from else ctx.settings.insurer_today - timedelta(days=REVIEW_DAYS)
        rows = [closed_view(c) for c in d()["leakage_claims"].values() if start <= date.fromisoformat(c["closed_on"]) <= end]
        return listing(rows, review_period={"closed_from": start.isoformat(), "closed_to": end.isoformat(),
                                            "sentence": f"Claims closed from {long_date(start.isoformat())} to {long_date(end.isoformat())}."})

    @reg(app, "get", "/closed-claims/{claim_id}", "get_closed_claim_payment_file", "Get one closed claim with its payment file",
         "Read one closed claim with its whole payment file, in one call: the claimant, the claim type, the dates of the loss, the "
         "report and the closing, a description, another party the file names as at fault with the source, the invoices with their "
         "lines, the settlement record (what the handler allowed on each line, the deductible taken, who approved and any second "
         "approval), every payment with the total paid, whether a recovery was raised with its reference, and the file notes. policy "
         "gives the policy the claim was made on with its schedule, and cover_on_loss_date says whether it was in force on the date "
         "of the loss, with the reason. It does not say whether the claim was paid correctly: calculate_what_should_have_been_paid "
         "does. Saved findings are not part of the file: drafts_on_file only counts them, and list_leakage_finding_drafts reads them.")
    def get_closed_claim_payment_file(claim_id: str = closed_p):
        c = closed_or_404(claim_id)
        return {**closed_view(c), "policy": policy_brief(c["policy_id"]),
                "cover_on_loss_date": cover_on(policy_of(c["policy_id"]), c["loss_date"]), "read_on": today()}

    @reg(app, "get", "/closed-claims/{claim_id}/should-have-been-paid", "calculate_what_should_have_been_paid",
         "Work out what should have been paid on a closed claim under the handling standards",
         "Work out what should have been paid on one closed claim and test the claim against every handling standard. The answer "
         "gives each invoice line with the amount invoiced, the limit of the wording that applies with its clause, the amount under "
         "the standards, what the handler allowed on the file and how much of that is over the limit; the deductible due with its "
         "clause, the deductible taken and the part not taken; what should have been paid, what was paid and the difference; each "
         "payment that repeats an invoice already paid; the approval the amount paid needs and the approvals on the file; and "
         "standards, one row for each of LS-1 to LS-6 with a result (met, not_met or cannot_tell), the figures it rests on in a "
         "sentence, and an amount where the standard has one. It also gives the standards not met, the standards that cannot be "
         "told, an outcome (paid_within_the_standards, paid_outside_the_standards or cannot_tell_needs_a_person) with a sentence, "
         "and the working. When a payment was made against an invoice that is not on the file, what should have been paid is not "
         "worked out: the amounts are empty, what_is_missing names the invoice, and the outcome is cannot_tell_needs_a_person. Use "
         "these figures and do not add up yourself. It saves nothing and changes nothing.")
    def calculate_what_should_have_been_paid(claim_id: str = closed_p):
        return {**check(closed_or_404(claim_id)), "saved": False}

    @reg(app, "get", "/closed-claims/{claim_id}/findings", "list_leakage_finding_drafts", "List the leakage findings saved on a closed claim",
         "Read every leakage finding saved on a closed claim, each with its version number, who wrote it and when. A finding is "
         "somebody's draft for the claims quality team, not a fact of the claim file and not a decision.")
    def list_leakage_finding_drafts(claim_id: str = closed_p):
        c = closed_or_404(claim_id)
        return listing(c["leakage_finding_drafts"], claim_id=claim_id)

    @reg(app, "post", "/closed-claims/{claim_id}/findings", "save_leakage_finding", "Save a leakage finding on a closed claim (draft)",
         "Save the finding of the leakage review on one closed claim: the outcome (paid within the standards, paid outside the "
         "standards, or cannot tell and needs a person), one row for each standard that is not met or cannot be told, and what the "
         "file lacks. The system stores its own figures with it (what should have been paid, what was paid, the difference and the "
         "standards not met) and the answer returns them. This is a draft for the claims quality team: stored with who wrote it, a "
         "time and a version number, earlier versions kept. It reopens no claim, asks nobody for money back and changes nothing on "
         "the claim. Refused with 409, and nothing saved, when a row names a standard the insurer does not have or names one twice, "
         "when the outcome is paid_outside_the_standards and no row says not_met, when the outcome is paid_within_the_standards and "
         "a row says not_met or cannot_tell, or when the outcome is cannot_tell_needs_a_person and what_is_missing is empty.")
    def save_leakage_finding(body: LeakageFinding, claim_id: str = closed_p):
        c = closed_or_404(claim_id)
        known = list(d()["leakage_standards"])
        sent = [tidy_id(row.standard_id) for row in body.standards]
        unknown = [s for s in sent if s not in known]
        if unknown or len(sent) != len(set(sent)):
            raise conflict(f"The handling standards are {', '.join(known)}, each to be given once at most. Not a standard or given "
                           f"twice: {', '.join(unknown) or 'an id given twice'}. Nothing was saved.")
        findings = [row.finding for row in body.standards]
        if body.outcome == "paid_outside_the_standards" and "not_met" not in findings:
            raise conflict("The outcome paid_outside_the_standards needs one row for each standard that is not met. Nothing was saved.")
        if body.outcome == "paid_within_the_standards" and ("not_met" in findings or "cannot_tell" in findings):
            raise conflict("The outcome paid_within_the_standards takes no row that says not_met or cannot_tell. Choose another outcome, "
                           "or leave the rows out. Nothing was saved.")
        if body.outcome == "cannot_tell_needs_a_person" and not body.what_is_missing.strip():
            raise conflict("The outcome cannot_tell_needs_a_person needs what_is_missing: what the file lacks, in a sentence. Nothing "
                           "was saved.")
        k = check(c)
        payload = {"outcome": body.outcome,
                   "standards": [{**row.model_dump(), "standard_id": sid} for row, sid in zip(body.standards, sent)],
                   "what_is_missing": body.what_is_missing, "notes": body.notes,
                   "figures_worked_out_by_the_system": {key: k[key] for key in ("should_have_been_paid", "amount_paid", "difference",
                                                                                "standards_not_met", "standards_that_cannot_be_told",
                                                                                "outcome")}}
        v = st.add_draft(c, "leakage_finding_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    # ------------------------------------------------------------ claims held for checking
    DRAFT_SETS = ("fraud_referral_drafts", "case_file_drafts")

    def brief(c):
        return {**{k: v for k, v in c.items() if k not in DRAFT_SETS}, "status_in_words": STATUS_WORDS[c["status"]]}

    @reg(app, "get", "/fraud-indicators", "get_fraud_indicators", "Get the insurer's fraud indicators",
         "Read the insurer's fraud indicators, whole: each with its id (FI-1 to FI-6), a name, the exact test in a sentence, the "
         "threshold as a figure and its unit, and a note on how they are applied. They cover a loss soon after the start of the "
         "policy, a claimant with several earlier claims, one repairer on several claims by the same claimant, a bank account "
         "shared with an unrelated claimant, a repair invoice dated before the loss, and an estimate close to the sum insured. To "
         "measure them on one claim, use run_fraud_indicators.")
    def get_fraud_indicators():
        return listing(list(d()["fraud_indicators"].values()), how_to_apply=INDICATORS_HOW_TO_APPLY)

    @reg(app, "get", "/claims", "list_claims_for_fraud_check", "List the new claims waiting for the fraud check",
         "List the new claims that wait for the fraud check before anything is paid, whole: id, the policy id, the claimant with "
         "the party id, the claim type, the dates of the loss and of the report, the estimate, a description, the parties on the "
         "claim with their roles (claimant, witness, repairer), the repairer, the bank account given for payment, and the documents "
         "with their dates and text. It does not measure the indicators: run_fraud_indicators does that for one claim. Saved "
         "referrals are not in the list.")
    def list_claims_for_fraud_check():
        return listing([brief(c) for c in d()["investigation_claims"].values() if c["status"] == "new"])

    @reg(app, "get", "/flagged-claims", "list_flagged_claims", "List the claims referred to the investigations desk",
         "List the claims a handler has referred to the investigations desk for a case file, whole: id, the policy id, the claimant "
         "with the party id, the claim type, the dates of the loss and of the report, the estimate, a description, the parties on "
         "the claim with their roles, the repairer, the bank account given for payment, the documents, and referral: who referred "
         "the claim, on which date and which indicators were met. A referral is a reason to look. It is not a finding. Saved case "
         "files are not in the list.")
    def list_flagged_claims():
        return listing([brief(c) for c in d()["investigation_claims"].values() if c["status"] == "flagged"])

    @reg(app, "get", "/claims/{claim_id}", "get_claim_for_checking", "Get one claim held for checking, with its parties and its policy",
         "Read one claim this system holds, in one call: a new claim waiting for the fraud check, a claim referred to the "
         "investigations desk, or an earlier closed claim. It gives the status in a word and in plain words, the claimant, the "
         "claim type, the dates of the loss and of the report with days_from_loss_to_report worked out by the system, the estimate "
         "or the amount paid, a description, the bank account given for payment, the documents with their dates and text, and the "
         "referral when a handler has made one. parties gives every party on the claim with the role and the party's own record: "
         "name, date of birth, phone number, address and bank account. policy gives the policy with its period and schedule, and "
         "cover_on_loss_date whether it was in force on the date of the loss; both are empty for an earlier claim on a policy that "
         "has ended, and policy_note says so. It does not measure the indicators, list earlier claims or find links: "
         "run_fraud_indicators, get_parties_earlier_claims and get_claim_links do. Saved referrals and case files are not part of "
         "the claim: drafts_on_file only counts them.")
    def get_claim_for_checking(claim_id: str = clm_p):
        c = claim_or_404(claim_id)
        policy = policy_of(c["policy_id"])
        days = (date.fromisoformat(c["reported_date"]) - date.fromisoformat(c["loss_date"])).days
        people = [{**p, **{k: v for k, v in d()["investigation_parties"][p["party_id"]].items() if k not in ("party_id", "name")}}
                  for p in c["parties"]]
        return {**brief(c), "parties": people, "days_from_loss_to_report": days, "policy": policy_brief(c["policy_id"]),
                "cover_on_loss_date": cover_on(policy, c["loss_date"]) if policy else None,
                "drafts_on_file": {name: len(c[name]) for name in DRAFT_SETS}, "read_on": today()}

    @reg(app, "get", "/claims/{claim_id}/earlier-claims", "get_parties_earlier_claims", "Get the earlier claims of the claimant and the other parties",
         "Read the earlier claims of every party on one claim: the claimant, a witness, the repairer. For each party it gives the "
         "party id, the name, the role on this claim, and every claim the insurer holds with a date of loss before this one on "
         "which the party appears: the claim id, the party's role on it, the claimant, the claim type, the date of the loss with "
         "the days before this loss worked out by the system, the amount paid, the repairer, the bank account, and whether the loss "
         "falls in the 24 months before this loss. For the claimant it counts the earlier claims as claimant, in all and in those 24 "
         "months, and says so in a sentence. other_people_with_the_claimants_name lists any other person on the insurer's records "
         "who has the claimant's name and another date of birth: that is a different person, and that person's claims are not the "
         "claimant's and are not counted. Use these counts and do not count yourself. It changes nothing.")
    def get_parties_earlier_claims(claim_id: str = clm_p):
        return earlier_claims(claim_or_404(claim_id), d()["investigation_claims"], d()["investigation_parties"])

    def indicators(c):
        if c["status"] == "closed":
            raise conflict(f"{c['claim_id']} is closed. The indicators are measured on a claim before it is paid. Nothing was worked out.")
        return run_indicators(c, policy_of(c["policy_id"]), d()["investigation_claims"], d()["investigation_parties"])

    @reg(app, "get", "/claims/{claim_id}/indicators", "run_fraud_indicators", "Measure every fraud indicator on one claim",
         "Measure every indicator, FI-1 to FI-6, on one claim. For each indicator the answer gives the id, the name, the test, the "
         "measured value (a number of days, a count or a percentage, worked out by the system), the threshold, whether the "
         "indicator is met, and a sentence that says all of it with the dates, the claim ids and the names it rests on. It also "
         "gives the ids of the indicators met and their count. The system does the day counts, the counts of claims and the "
         "percentage: use them and do not work them out yourself. An indicator that is met is a reason to pass the claim to the "
         "investigations desk; it is not a finding that the claim is false. Refused with 409 for a closed claim. It saves nothing "
         "and changes nothing.")
    def run_fraud_indicators(claim_id: str = clm_p):
        return {**indicators(claim_or_404(claim_id)), "saved": False}

    @reg(app, "get", "/claims/{claim_id}/referrals", "list_fraud_referral_drafts", "List the fraud referrals saved on a claim",
         "Read every fraud referral saved on a claim, each with its version number, who wrote it and when. A saved referral is "
         "somebody's draft for the investigations desk, not a fact of the claim and not a decision.")
    def list_fraud_referral_drafts(claim_id: str = clm_p):
        c = claim_or_404(claim_id)
        return listing(c["fraud_referral_drafts"], claim_id=claim_id)

    @reg(app, "post", "/claims/{claim_id}/referrals", "save_fraud_referral", "Save a fraud referral on a new claim (draft)",
         "Save the result of the fraud check on a new claim: the proposal (refer to the investigations desk, or no referral and the "
         "handler goes on), one row for each indicator that is met, and the reasons. The system stores its own measurement with it "
         "(the indicators it found met, with the measured values) and the answer returns it. This is a draft for the investigations "
         "desk: stored with who wrote it, a time and a version number, earlier versions kept. It does not change the claim's "
         "status, holds no payment, declines nothing and tells the claimant nothing. Refused with 409, and nothing saved, when the "
         "claim is not waiting for the fraud check, when a row names an indicator the insurer does not have or names one twice, "
         "when the proposal is refer_to_the_investigations_desk and no row is sent, or when the proposal is "
         "no_referral_continue_handling and rows are sent.")
    def save_fraud_referral(body: FraudReferral, claim_id: str = clm_p):
        c = claim_or_404(claim_id)
        if c["status"] != "new":
            was = (f" It was referred by {c['referral']['referred_by']} on {long_date(c['referral']['referred_on'])}." if c["referral"] else "")
            raise conflict(f"{claim_id} is not waiting for the fraud check: it is {STATUS_WORDS[c['status']]}.{was} Nothing was saved.")
        known = list(d()["fraud_indicators"])
        sent = [tidy_id(row.indicator_id) for row in body.indicators_met]
        unknown = [s for s in sent if s not in known]
        if unknown or len(sent) != len(set(sent)):
            raise conflict(f"The indicators are {', '.join(known)}, each to be given once at most. Not an indicator or given twice: "
                           f"{', '.join(unknown) or 'an id given twice'}. Nothing was saved.")
        if body.proposal == "refer_to_the_investigations_desk" and not sent:
            raise conflict("The proposal refer_to_the_investigations_desk needs one row for each indicator that is met. Nothing was saved.")
        if body.proposal == "no_referral_continue_handling" and sent:
            raise conflict("The proposal no_referral_continue_handling takes no rows. Send refer_to_the_investigations_desk with the "
                           "rows, or leave the rows out. Nothing was saved.")
        k = indicators(c)
        payload = {"proposal": body.proposal,
                   "indicators_met": [{"indicator_id": sid, "note": row.note} for row, sid in zip(body.indicators_met, sent)],
                   "reasons": body.reasons, "notes": body.notes,
                   "measured_by_the_system": {"indicators_met": k["indicators_met"],
                                              "measured": {r["indicator_id"]: r["measured"] for r in k["indicators"]}}}
        v = st.add_draft(c, "fraud_referral_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    # ------------------------------------------------------------ parties, links and public notices
    @reg(app, "get", "/parties", "search_parties", "Search the parties on the claims this system holds",
         "Find parties: the people and firms on the claims this system holds, as claimant, witness or repairer. text matches the "
         "name, the party id or the address; any word of it may match, in any order. phone and bank_account match a whole phone "
         "number or account exactly. With nothing sent, every party is listed. Each row is whole: party id, kind (person or firm), "
         "name, date of birth, phone number, address, bank account, and every claim the party is on with the party's role, the "
         "claimant, the claim type, the status, the date of the loss, the amount paid or the estimate, the repairer and the bank "
         "account. Two people with one name and different dates of birth are two parties with two ids: they are not the same "
         "person. It does not say what two parties share: get_party_links and get_claim_links do.")
    def search_parties(text: str | None = Query(None, description="Words from a name, a party id or an address, for example Tansley. "
                                                                  "Leave empty to list every party."),
                       phone: str | None = Query(None, description="A whole phone number, for example +999 555 0142."),
                       bank_account: str | None = Query(None, description="A whole bank account, for example DEMO-ACCT-7741.")):
        words = [w.lower() for w in (text or "").replace(",", " ").split() if len(w) > 2]
        squash = lambda v: "".join((v or "").split()).lower()
        rows = []
        for p in d()["investigation_parties"].values():
            hay = f"{p['name']} {p['party_id']} {p['address']}".lower()
            if words and not any(w in hay for w in words):
                continue
            if phone and squash(phone) != squash(p["phone"]):
                continue
            if bank_account and squash(bank_account) != squash(p["bank_account"]):
                continue
            rows.append(party_view(p, d()["investigation_claims"], d()["investigation_parties"]))
        return listing(rows, searched_for={"text": text or "", "phone": phone or "", "bank_account": bank_account or ""})

    @reg(app, "get", "/parties/{party_id}/links", "get_party_links", "Get what one party shares with other parties",
         "Read what one party shares with every other party on the insurer's records: a phone number, an address or a bank "
         "account. Each row names the attribute, its value, the other party's id and name, and says it in a sentence. It also gives "
         "the party's own record and every claim the party is on, with the party's role. For a firm, such as a repairer, it gives "
         "the claims that name the firm. A link is a fact two records share, not a finding about a person. For the links of a whole "
         "claim in one call, use get_claim_links.")
    def get_party_links(party_id: str = pty_p):
        p = party_or_404(party_id)
        rows = shared_attributes(p, d()["investigation_parties"])
        view = party_view(p, d()["investigation_claims"], d()["investigation_parties"])
        return {"party": view, "shared_attributes": rows, "shared_attribute_count": len(rows),
                "sentence": (f"{p['name']} ({party_id}) shares {plural_words(len(rows))} with other parties on the insurer's records."
                             if rows else f"{p['name']} ({party_id}) shares no phone number, address or bank account with any other "
                                          "party on the insurer's records."),
                "what_a_link_is": LINK_NOTE}

    def plural_words(n):
        return f"{n} attribute{'' if n == 1 else 's'}"

    @reg(app, "get", "/claims/{claim_id}/links", "get_claim_links", "Get the links between one claim and other claims and parties",
         "Read everything one claim shares with other claims and parties the insurer holds, in one call. "
         "other_claims_by_the_same_claimant lists the claimant's own other claims. linked_claims lists each claim by another "
         "claimant that shares something with this one, with linked_by (repairer, witness, phone, address, bank_account, or "
         "party_on_both_claims) and one row for each link: the party the link runs through, the value shared and a sentence. "
         "shared_attributes lists each phone number, address or bank account that a person on this claim shares with another "
         "person. no_links_found is true when the claim shares nothing with any other claim or party, and sentence says the whole "
         "result. The system does the matching: use its result and do not match names or numbers yourself. A link is a fact two "
         "records share. It is not a finding about any person, and a party a link runs through is named as a fact of the records "
         "only. It does not search public notices: get_public_notices_for_party does.")
    def get_claim_links(claim_id: str = clm_p):
        return claim_links(claim_or_404(claim_id), d()["investigation_claims"], d()["investigation_parties"])

    @reg(app, "get", "/public-notices", "search_public_notices", "Search the public notices",
         "Search the public notices the insurer keeps: court lists and press items. All of them are invented. Any word of the text "
         "may match the headline, the text, the source or the person named. With no text, every notice is listed. Each notice is "
         "whole: id, kind (court_list or press_item), source, the date published, headline, text, the person it names, and the date "
         "or year of birth and the address it gives for that person. A notice that names somebody with a party's name is not yet a "
         "notice about that party: get_public_notices_for_party sets the notice's date of birth and address beside the party's.")
    def search_public_notices(text: str | None = Query(None, description="Words to look for, for example a surname. Leave empty to "
                                                                         "list every notice.")):
        words = [w.lower() for w in (text or "").replace(",", " ").split() if len(w) > 2]
        rows = [n for n in d()["public_notices"].values()
                if not words or any(w in f"{n['headline']} {n['text']} {n['source']} {n['person_name']}".lower() for w in words)]
        return listing(rows, searched_for=text or "")

    @reg(app, "get", "/parties/{party_id}/public-notices", "get_public_notices_for_party", "Get the public notices that name a person with a party's name",
         "Read every public notice that names a person with the same name as one party, each set beside the party's own record by "
         "the system. For each notice the answer gives the notice whole, date_of_birth_compared (same, same_year, differs or "
         "not_given), address_compared (same, differs or not_given), about (the_same_person when the name, the date of birth and "
         "the address agree; a_different_person when the date of birth differs; cannot_tell otherwise) and a sentence. With no "
         "notice the list is empty and the sentence says so. A notice about the same person is a public record of what it says. It "
         "is not a finding about any claim. A notice about a different person says nothing about the party. All notices are "
         "invented. A firm has no notices here.")
    def get_public_notices_for_party(party_id: str = pty_p):
        p = party_or_404(party_id)
        rows = notices_for_party(p, d()["public_notices"])
        return listing(rows, party_id=party_id, party_name=p["name"], party_date_of_birth=p["date_of_birth"], party_address=p["address"],
                       sentence=(f"{len(rows)} public notice{'' if len(rows) == 1 else 's'} name{'s' if len(rows) == 1 else ''} a person "
                                 f"called {p['name']}." if rows else f"No public notice names a person called {p['name']}."))

    # ------------------------------------------------------------ case files
    @reg(app, "get", "/claims/{claim_id}/case-file", "list_case_file_drafts", "List the case files saved on a claim",
         "Read every case file saved on a claim, each with its version number, who wrote it and when. A saved case file is "
         "somebody's draft for the investigator, not a fact of the claim and not a finding.")
    def list_case_file_drafts(claim_id: str = clm_p):
        c = claim_or_404(claim_id)
        return listing(c["case_file_drafts"], claim_id=claim_id)

    @reg(app, "post", "/claims/{claim_id}/case-file", "save_case_file", "Save a case file on a claim referred to the investigations desk (draft)",
         "Save the case file for a claim that was referred to the investigations desk, in sections: a summary; the earlier claims "
         "of the parties; whether links were found, with one row for each link (what is shared, the other claim, the party the "
         "link runs through and what the records show); one row for each public notice that names a person with a party's name, "
         "with whether it is about the same person; and the points the investigator may want to check. The system stores what it "
         "found itself with it (the linked claims, the claimant's other claims and the notices) and the answer returns that. This "
         "is a draft for the investigator: stored with who wrote it, a time and a version number, earlier versions kept. It changes "
         "nothing on the claim, declines nothing, contacts nobody and is not a finding about any person. Refused with 409, and "
         "nothing saved, when the claim is not referred to the investigations desk, when a row names a claim, a party or a notice "
         "the insurer does not hold, when links_found is sent with no link row, or when no_links_found is sent with link rows.")
    def save_case_file(body: CaseFile, claim_id: str = clm_p):
        c = claim_or_404(claim_id)
        if c["status"] != "flagged":
            raise conflict(f"{claim_id} is not referred to the investigations desk: it is {STATUS_WORDS[c['status']]}. A case file is "
                           "saved only on a referred claim. Nothing was saved.")
        claims, parties, notices = d()["investigation_claims"], d()["investigation_parties"], d()["public_notices"]
        bad_claims = [x for x in [row.claim_id for row in body.earlier_claims] + [row.linked_claim_id for row in body.links if row.linked_claim_id]
                      if x not in claims]
        bad_parties = [row.through_party_id for row in body.links if row.through_party_id and row.through_party_id not in parties]
        bad_notices = [row.notice_id for row in body.public_notices if tidy_id(row.notice_id) not in notices]
        if bad_claims or bad_parties or bad_notices:
            parts = ([f"not a claim this system holds: {', '.join(bad_claims)}"] if bad_claims else []) \
                + ([f"not a party: {', '.join(bad_parties)}"] if bad_parties else []) \
                + ([f"not a public notice: {', '.join(bad_notices)}"] if bad_notices else [])
            raise conflict(f"The case file for {claim_id} names a record the insurer does not hold; {'; '.join(parts)}. Use the ids "
                           "that get_claim_links, get_parties_earlier_claims and get_public_notices_for_party give. Nothing was saved.")
        if body.links_found == "links_found" and not body.links:
            raise conflict("links_found needs one row for each link. Nothing was saved.")
        if body.links_found == "no_links_found" and body.links:
            raise conflict("no_links_found takes no link rows. Send links_found with the rows, or leave the rows out. Nothing was saved.")
        found = claim_links(c, claims, parties)
        named = [{"notice_id": n["notice_id"], "party_id": n["party_id"], "about": n["about"]}
                 for p in c["parties"] if is_person(parties[p["party_id"]]) for n in notices_for_party(parties[p["party_id"]], notices)]
        payload = {"summary": body.summary, "earlier_claims": [row.model_dump() for row in body.earlier_claims],
                   "links_found": body.links_found, "links": [row.model_dump() for row in body.links],
                   "public_notices": [{**row.model_dump(), "notice_id": tidy_id(row.notice_id)} for row in body.public_notices],
                   "open_points": body.open_points,
                   "found_by_the_system": {"other_claims_by_the_same_claimant": [x["claim_id"] for x in found["other_claims_by_the_same_claimant"]],
                                           "linked_claims": [{"claim_id": x["claim_id"], "linked_by": x["linked_by"]} for x in found["linked_claims"]],
                                           "no_links_found": found["no_links_found"], "public_notices_naming_a_party": named}}
        v = st.add_draft(c, "case_file_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    return app
