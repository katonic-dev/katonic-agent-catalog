"""Claims: loss reports, claims with their documents, checklists, the handling guide, letter templates and settlements."""

from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..seed_claims import CLAIM_TYPES
from ..seed_policy import cover_on, long_date

KEY = "claims"
TITLE = "Claims"
LINE = "Loss reports, claims with their documents, checklists by claim type, the handling guide, letter templates and settlements."

CLAIM_TYPE = Literal["motor_own_damage", "motor_theft", "motor_third_party", "home_escape_of_water", "home_theft", "home_fire"]
DRAFTED_BY = Field("agent", description="Who wrote the draft. Free text.")


DRAFT_SETS = ("triage_drafts", "pack_check_drafts", "summary_drafts", "coverage_check_drafts", "settlement_drafts", "letter_drafts")


def usd(amount: float) -> str:
    return f"USD {amount:,.2f}"


class ClaimFileDraft(BaseModel):
    policy_id: str | None = Field(None, description="The policy the report belongs to, as the policy system gives it, for example "
                                  "POL-2011. Leave empty when no policy was found.")
    claim_type: CLAIM_TYPE | None = Field(None, description="The claim type, when the report says enough to choose one. Leave empty when it does not.")
    loss_date: str | None = Field(None, description="The date of the loss as YYYY-MM-DD, when the report gives it. Leave empty when it does not.")
    loss_place: str = Field("", description="Where the loss happened, as the report says.")
    what_happened: str = Field(..., min_length=1, description="What happened, in one or two plain sentences taken from the report.")
    people_injured: Literal["yes", "no", "not_stated"] = Field(..., description="Whether the report says a person was injured.")
    another_party_involved: Literal["yes", "no", "not_stated"] = Field(..., description="Whether the report says another party was involved.")
    cover_in_force_on_loss_date: Literal["yes", "no", "not_checked"] = Field(
        ..., description="What the policy system said when asked whether the policy was in force on the date of the loss. "
                         "not_checked when there is no policy or no loss date to check.")
    missing_items: list[str] = Field(default_factory=list, description="What the report does not say and a claim needs, one item each, "
                                     "for example date of the loss. Leave the list empty when nothing is missing.")
    notes: str = Field("", description="Anything a handler should know, for example that the policy number given does not exist and "
                                       "the policy was found by the holder's name and address.")
    proposal: Literal["register", "ask_the_reporter", "refer_to_a_handler"] = Field(
        ..., description="register when nothing is missing and the policy was in force; ask_the_reporter when something is missing; "
                         "refer_to_a_handler when the policy was not in force, a person was injured, or the records do not settle a point.")
    drafted_by: str = DRAFTED_BY


class RegisterClaim(BaseModel):
    draft_version: int = Field(..., ge=1, description="The version number of the saved claim file draft to register, as the save returned it.")
    registered_by: str = Field("", description="The handler who approved the registration. Free text.")


class Triage(BaseModel):
    rule_id: Literal["HG-1", "HG-2", "HG-3", "HG-4"] = Field(..., description="The sorting rule of the handling guide that applies first.")
    track: Literal["person first", "complex", "fast track", "standard"] = Field(..., description="The track that rule gives.")
    team: str = Field(..., min_length=1, description="The team that rule gives, in the guide's words, for example theft team.")
    severity: Literal["high", "medium", "low"] = Field(..., description="The severity that rule gives.")
    reason: str = Field(..., min_length=1, description="Why the rule applies, with the fact and the document or record it comes from.")
    drafted_by: str = DRAFTED_BY


class PackItem(BaseModel):
    doc_type: str = Field(..., description="The document type from the claim's checklist, for example plumber_report.")
    finding: Literal["received", "missing", "cannot_be_read", "does_not_show_what_it_must"] = Field(
        ..., description="received when the document is in the file and shows what the checklist says it must; missing when it is not "
                         "in the file; cannot_be_read when it is in the file and unreadable; does_not_show_what_it_must when it is in "
                         "the file and readable but lacks or contradicts what the checklist asks of it.")
    document_id: str | None = Field(None, description="The document's id when it is in the file, for example DOC-4002-3.")
    note: str = Field("", description="What is wrong, in a few words, with both values when two records disagree.")


class PackCheck(BaseModel):
    items: list[PackItem] = Field(..., min_length=1, description="One item for every document type on the claim's checklist, in the checklist's order.")
    proposal: Literal["pack_complete", "ask_the_customer", "refer_to_a_handler"] = Field(
        ..., description="pack_complete when every item is received; ask_the_customer when a document is missing, unreadable or does not "
                         "show what it must; refer_to_a_handler when the records do not settle a point.")
    drafted_by: str = DRAFTED_BY


class Disagreement(BaseModel):
    point: str = Field(..., description="What the two records disagree on, for example where the fire started.")
    first_source: str = Field(..., description="The id of the first document or record, for example DOC-4007-1.")
    first_says: str = Field(..., description="What the first one says.")
    second_source: str = Field(..., description="The id of the second document or record.")
    second_says: str = Field(..., description="What the second one says.")


class ClaimSummary(BaseModel):
    summary_text: str = Field(..., min_length=1, description="The summary, in plain sentences.")
    open_points: list[str] = Field(default_factory=list, description="What is still open, one point each. Empty when nothing is open.")
    disagreements: list[Disagreement] = Field(default_factory=list, description="Each place where two records disagree. Empty when none do.")
    recovery: Literal["recovery_possible", "no_recovery_indicated"] = Field(..., description="What rule HG-7 of the handling guide gives for this file.")
    drafted_by: str = DRAFTED_BY


class CoverageRow(BaseModel):
    reference: str = Field(..., description="The clause number of the wording, for example 1.3, or the endorsement id, for example "
                           "END-2008-1, or the words no clause for a row whose finding is wording_silent.")
    finding: Literal["applies", "does_not_apply", "excludes", "limits", "condition_met", "condition_not_met", "cannot_tell",
                     "wording_silent"] = Field(
        ..., description="applies for a clause that covers the loss; does_not_apply for a clause read and found not to bear on it; "
                         "excludes for a clause or endorsement that takes the loss out of cover; limits for a limit or a deductible; "
                         "condition_met or condition_not_met for a condition; cannot_tell when the file does not hold the fact needed; "
                         "wording_silent for a fact that matters and that no clause speaks of.")
    note: str = Field(..., min_length=1, description="The fact from the file that the finding rests on, with the document id.")


class CoverageCheck(BaseModel):
    rows: list[CoverageRow] = Field(..., min_length=1, description="One row for each clause and endorsement that bears on the loss.")
    position: Literal["within_the_wording", "outside_the_wording", "policy_not_in_force", "wording_is_silent", "cannot_tell_from_the_file"] = Field(
        ..., description="Where the loss stands against the wording. This is a reading for the adjuster, never a decision.")
    silent_on: str = Field("", description="When the wording is silent on a fact that matters, the fact, in a sentence. Otherwise empty.")
    recovery: Literal["recovery_possible", "no_recovery_indicated"] = Field(..., description="What rule HG-7 of the handling guide gives for this file.")
    drafted_by: str = DRAFTED_BY


class ExcludedLine(BaseModel):
    line_id: str = Field(..., description="The id of the invoice or estimate line, for example DOC-4001-3-L4.")
    clause: str = Field(..., description="The clause of the wording that takes the line out of cover, for example 2.5.")
    reason: str = Field(..., min_length=1, description="Why the clause applies to this line, in a few words.")


class SettlementRequest(BaseModel):
    excluded_lines: list[ExcludedLine] = Field(default_factory=list, description="The lines the wording does not cover, each with its "
                                               "clause. Leave the list empty when every line is covered. Limits and the deductible are "
                                               "applied by the system: do not list a line here because a limit applies to it.")


class SettlementDraft(SettlementRequest):
    notes: str = Field("", description="Anything the adjuster should know.")
    drafted_by: str = DRAFTED_BY


class Letter(BaseModel):
    template_id: Literal["TPL-ACK", "TPL-MISSING", "TPL-DECLINE"] = Field(..., description="The letter template used.")
    language: str = Field("English", description="The language the letter is written in.")
    letter_text: str = Field(..., min_length=1, description="The whole letter, as it would be sent.")
    drafted_by: str = DRAFTED_BY


class Decision(BaseModel):
    decision: Literal["cover_accepted", "declined"] = Field(..., description="The adjuster's decision.")
    decided_by: str = Field(..., min_length=1, description="The adjuster who decided.")
    reason: str = Field(..., min_length=1, description="The reason, in a sentence.")
    clause: str = Field(..., description="The clause the decision rests on.")


class SendLetter(BaseModel):
    draft_version: int = Field(..., ge=1, description="The version number of the saved letter to send.")
    sent_by: str = Field(..., min_length=1, description="The handler who read and sent the letter.")


class Payment(BaseModel):
    draft_version: int = Field(..., ge=1, description="The version number of the saved settlement calculation to pay.")
    approved_by: str = Field(..., min_length=1, description="The person with the authority for the amount who approved it.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds loss reports as they arrive, claims with their documents as extracted text, the "
                                  "checklist of documents for each claim type, the claims handling guide and the letter templates. "
                                  "A draft is saved with who wrote it, a time and a version number. A change needs a named person.")
    st = ctx.store
    d = lambda: st.data
    today = lambda: ctx.settings.insurer_today
    clm_p = Path(..., description="Claim id, for example CLM-4001.")
    lr_p = Path(..., description="Loss report id, for example LR-3001.")

    def claim_or_404(i):
        c = d()["claims"].get(i)
        if not c:
            raise not_found("claim", i, "Use list_claims to find ids.")
        return c

    def report_or_404(i):
        r = d()["loss_reports"].get(i)
        if not r:
            raise not_found("loss report", i, "Use list_loss_reports to find ids.")
        return r

    def checklist_for(claim):
        have = {}
        for doc in claim["documents"].values():
            have.setdefault(doc["doc_type"], doc)
        rows = []
        for doc_type, label, must_show in d()["claim_checklists"][claim["claim_type"]]:
            doc = have.get(doc_type)
            rows.append({"doc_type": doc_type, "label": label, "must_show": must_show, "in_the_file": doc is not None,
                         "document_id": doc["document_id"] if doc else None, "readable": doc["readable"] if doc else None})
        return rows

    def all_lines(claim):
        return [line for doc in claim["documents"].values() for line in doc.get("lines", [])]

    def full_claim(c):
        policy = d()["policies"].get(c["policy_id"])
        days = (date.fromisoformat(c["reported_date"]) - date.fromisoformat(c["loss_date"])).days
        about = {}
        if policy:
            sched = policy["schedule"]
            about = {"wording_id": policy["wording_id"], "wording_version": policy["wording_version"],
                     "insured_item": (f"{sched['insured_vehicle']}, registration {sched['registration']}"
                                      if policy["product"] == "private_motor" else sched["insured_home"])}
            if policy["product"] == "private_motor":
                about["insured_vehicle_registration"] = sched["registration"]
        if c.get("driver"):
            born, loss = date.fromisoformat(c["driver"]["date_of_birth"]), date.fromisoformat(c["loss_date"])
            age = loss.year - born.year - ((loss.month, loss.day) < (born.month, born.day))
            about["driver"] = {**c["driver"], "age_on_the_date_of_the_loss": age, "under_25_on_the_date_of_the_loss": age < 25}
        kept = {k: v for k, v in c.items() if k not in DRAFT_SETS}
        return {**kept, **about, "documents": list(c["documents"].values()), "days_from_loss_to_report": days,
                "drafts_on_file": {name: len(c.get(name, [])) for name in DRAFT_SETS},
                "cover_on_loss_date": cover_on(policy, c["loss_date"]) if policy else None,
                "document_checklist": checklist_for(c), "read_on": today().isoformat()}

    # ------------------------------------------------------------ loss reports
    @reg(app, "get", "/loss-reports", "list_loss_reports", "List loss reports",
         "List the loss reports received, whole: id, status (new or registered), channel, the date received, the reporter, the policy "
         "number the reporter gave, and the text of the report.")
    def list_loss_reports(status: str | None = Query(None, description="Only reports with this status: new or registered.")):
        return listing([{k: v for k, v in r.items() if k != "claim_file_drafts"} for r in d()["loss_reports"].values()
                        if not status or r["status"] == status])

    @reg(app, "get", "/loss-reports/{loss_report_id}", "get_loss_report", "Get one loss report",
         "Read one loss report: the channel, the date received, the reporter, the policy number the reporter gave (it may be wrong), the "
         "text of the report as it arrived, and the claim id once it is registered. Saved claim file drafts are not part of the "
         "report: claim_file_drafts_on_file only counts them, and list_claim_file_drafts reads them.")
    def get_loss_report(loss_report_id: str = lr_p):
        r = report_or_404(loss_report_id)
        return {**{k: v for k, v in r.items() if k != "claim_file_drafts"}, "claim_file_drafts_on_file": len(r["claim_file_drafts"]),
                "read_on": today().isoformat()}

    @reg(app, "get", "/loss-reports/{loss_report_id}/claim-file", "list_claim_file_drafts", "List the claim file drafts saved on a loss report",
         "Read every claim file draft saved on a loss report, each with its version number, who wrote it and when. A draft is "
         "somebody's proposal, not a fact of the report.")
    def list_claim_file_drafts(loss_report_id: str = lr_p):
        r = report_or_404(loss_report_id)
        return listing(r["claim_file_drafts"], loss_report_id=loss_report_id)

    @reg(app, "post", "/loss-reports/{loss_report_id}/claim-file", "save_claim_file_draft", "Save a claim file prepared from a loss report (draft)",
         "Save the claim file prepared from a loss report: the policy, the claim type, the date and place of the loss, what happened, "
         "whether a person was injured, whether another party was involved, whether the policy was in force on the date of the loss, "
         "what is missing, and a proposal. This is a draft: stored with who wrote it, a time and a version number, earlier versions kept. "
         "It registers no claim and contacts nobody. Refused with 409 when the policy id is not a policy of the insurer.")
    def save_claim_file_draft(body: ClaimFileDraft, loss_report_id: str = lr_p):
        r = report_or_404(loss_report_id)
        if body.policy_id and body.policy_id not in d()["policies"]:
            raise conflict(f"The insurer holds no policy with the id {body.policy_id}. Find the policy with search_policies in the policy "
                           "system, or leave the policy id empty. Nothing was saved.")
        v = st.add_draft(r, "claim_file_drafts", body.model_dump(exclude={"drafted_by"}), body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    @reg(app, "post", "/loss-reports/{loss_report_id}/register", "register_claim", "Register a claim from a loss report (change)",
         "Register a claim from a saved claim file draft. This is a change: it creates the claim, gives it a claim id and marks the "
         "loss report registered. It is refused with 409 when the report is already registered, when there is no such draft, or when "
         "the draft does not propose to register, has no policy, no claim type or no date of loss.")
    def register_claim(body: RegisterClaim, loss_report_id: str = lr_p):
        r = report_or_404(loss_report_id)
        if r["status"] == "registered":
            raise conflict(f"{loss_report_id} is already registered as {r['claim_id']}. Nothing was changed.")
        drafts = r["claim_file_drafts"]
        if body.draft_version > len(drafts):
            raise conflict(f"{loss_report_id} has no claim file draft with version {body.draft_version}. Save the draft first. Nothing was changed.")
        draft = drafts[body.draft_version - 1]
        if draft["proposal"] != "register" or not draft["policy_id"] or not draft["claim_type"] or not draft["loss_date"]:
            raise conflict(f"Version {body.draft_version} of the claim file for {loss_report_id} cannot be registered: it must propose to "
                           "register and hold a policy, a claim type and a date of loss. Nothing was changed.")
        with st.lock:
            claim_id = st.next_free("claim", 4101, d()["claims"], lambda n: f"CLM-{n}")
            policy = d()["policies"][draft["policy_id"]]
            d()["claims"][claim_id] = {
                "claim_id": claim_id, "policy_id": draft["policy_id"], "claimant": policy["holder"], "claim_type": draft["claim_type"],
                "claim_type_label": CLAIM_TYPES[draft["claim_type"]], "status": "new", "loss_date": draft["loss_date"],
                "reported_date": r["received"], "estimate": None, "currency": "USD",
                "third_party_involved": draft["another_party_involved"] == "yes", "description": draft["what_happened"],
                "notes": [], "decision": None, "driver": None, "handling_team": None, "team_assigned_by": None, "documents": {}, "triage_drafts": [], "pack_check_drafts": [], "summary_drafts": [],
                "coverage_check_drafts": [], "settlement_drafts": [], "letter_drafts": [], "letters_sent": [], "payments": [],
                "registered_from": loss_report_id, "registered_by": body.registered_by or "not recorded"}
            r["status"], r["claim_id"] = "registered", claim_id
            st.save()
        return {"applied": True, "kind": "change", "claim_id": claim_id, "loss_report_id": loss_report_id,
                "message": f"{loss_report_id} is registered as {claim_id}."}

    # ------------------------------------------------------------ claims: reads
    @reg(app, "get", "/claims", "list_claims", "List claims",
         "List claims: id, policy id, claimant, claim type, status (new, in_assessment, decided or closed), the date of the loss, the "
         "date reported and the estimate (empty when no estimate has been received yet).")
    def list_claims(status: str | None = Query(None, description="Only claims with this status, for example new."),
                    claim_type: str | None = Query(None, description="Only claims of this type, for example motor_theft.")):
        keys = ("claim_id", "policy_id", "claimant", "claim_type", "claim_type_label", "status", "loss_date", "reported_date", "estimate", "currency")
        return listing([{k: c[k] for k in keys} for c in d()["claims"].values()
                        if (not status or c["status"] == status) and (not claim_type or c["claim_type"] == claim_type)])

    @reg(app, "get", "/claims/{claim_id}", "get_claim", "Get one claim with its whole file",
         "Read one claim with its whole file: the policy id, the claimant, the claim type, the dates of the loss and of the report with "
         "days_from_loss_to_report worked out by the system, the estimate, whether another party is involved, the description, the "
         "wording id and version of the policy, the insured item as the policy schedule gives it (for a motor policy also the "
         "registration of the insured vehicle), the driver at the time of a motor accident with the age on the date of the loss "
         "worked out by the system, the team handling the claim once a handler has assigned one, the "
         "handlers' notes, an adjuster's decision when one is recorded, and every document with its id, type, title, text, whether it "
         "can be read, and its invoice or estimate lines (each with a line id, a description, a category and an amount). It also gives "
         "cover_on_loss_date (whether the policy was in force on the date of the loss, with the reason) and document_checklist (for "
         "each document the claim type requires: what it must show, whether it is in the file, its id and whether it can be read). "
         "A document in the file must still be read to see that it shows what the checklist says it must. Saved drafts are not "
         "part of the file: drafts_on_file only counts them, and list_claim_drafts reads them.")
    def get_claim(claim_id: str = clm_p):
        return full_claim(claim_or_404(claim_id))

    @reg(app, "get", "/claims/{claim_id}/drafts", "list_claim_drafts", "List the drafts saved on a claim",
         "Read every draft saved on a claim, by kind: how it was sorted, pack checks, summaries, coverage checks, settlement "
         "calculations and letters. Each draft has its version number, who wrote it and when. A draft is somebody's proposal, not a "
         "fact of the claim file.")
    def list_claim_drafts(claim_id: str = clm_p):
        c = claim_or_404(claim_id)
        return {"claim_id": claim_id, **{name: c.get(name, []) for name in DRAFT_SETS}}

    @reg(app, "get", "/checklists/{claim_type}", "get_claim_checklist", "Get the document checklist for a claim type",
         "Read the documents a claim of one type must hold, each with its type, its plain name and what it must show to count.")
    def get_claim_checklist(claim_type: str = Path(..., description="Claim type, for example home_escape_of_water.")):
        rows = d()["claim_checklists"].get(claim_type)
        if rows is None:
            raise not_found("claim type", claim_type, f"The claim types are: {', '.join(CLAIM_TYPES)}.")
        return listing([{"doc_type": t, "label": label, "must_show": must} for t, label, must in rows], claim_type=claim_type,
                       claim_type_label=CLAIM_TYPES[claim_type])

    @reg(app, "get", "/handling-guide", "get_claims_handling_guide", "Get the claims handling guide",
         "Read the insurer's claims handling guide: the sorting rules HG-1 to HG-4 that give a claim its track, team and severity "
         "(applied in order, the first that applies wins), the settlement authority HG-5, the rules for letters HG-6 and the rule on "
         "recovery from another party HG-7.")
    def get_claims_handling_guide():
        return d()["handling_guide"]

    @reg(app, "get", "/letter-templates", "list_letter_templates", "List the letter templates",
         "Read every letter template, whole: its id, title, when it is used, what a letter made from it must include, and its closing "
         "paragraph, which goes into the letter word for word.")
    def list_letter_templates():
        return listing(list(d()["letter_templates"].values()))

    # ------------------------------------------------------------ claims: drafts
    @reg(app, "post", "/claims/{claim_id}/triage", "save_claim_triage", "Save how a claim is sorted (draft)",
         "Save the sorting of a claim: the rule of the handling guide that applies first, and the track, team and severity it gives, "
         "with the reason. This is a draft: stored with who wrote it, a time and a version number. It assigns the claim to nobody.")
    def save_claim_triage(body: Triage, claim_id: str = clm_p):
        v = st.add_draft(claim_or_404(claim_id), "triage_drafts", body.model_dump(exclude={"drafted_by"}), body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    @reg(app, "post", "/claims/{claim_id}/pack-check", "save_pack_check", "Save a check of the claim pack (draft)",
         "Save the check of a claim's documents against the checklist for its type: one item for every document type on the "
         "checklist, each with a finding (received, missing, cannot_be_read or does_not_show_what_it_must), the document id when it is "
         "in the file, and a note. This is a draft: stored with who wrote it, a time and a version number. It contacts nobody. Refused "
         "with 422 when an item names a document type that is not on the claim's checklist.")
    def save_pack_check(body: PackCheck, claim_id: str = clm_p):
        c = claim_or_404(claim_id)
        known = [t for t, _, _ in d()["claim_checklists"][c["claim_type"]]]
        unknown = [i.doc_type for i in body.items if i.doc_type not in known]
        if unknown:
            from fastapi import HTTPException
            raise HTTPException(422, f"Not on the checklist for {c['claim_type']}: {', '.join(unknown)}. The checklist types are: "
                                     f"{', '.join(known)}. Nothing was saved.")
        sent = [i.doc_type for i in body.items]
        left_out = [t for t in known if t not in sent]
        if left_out or len(sent) != len(set(sent)):
            from fastapi import HTTPException
            raise HTTPException(422, f"A pack check holds one item for every document type on the checklist for {c['claim_type']}, each once: "
                                     f"{', '.join(known)}. Left out: {', '.join(left_out) or 'none'}. Nothing was saved.")
        v = st.add_draft(c, "pack_check_drafts", {"items": [i.model_dump() for i in body.items], "proposal": body.proposal}, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    @reg(app, "post", "/claims/{claim_id}/summary", "save_claim_summary", "Save a claim summary (draft)",
         "Save the summary of a claim file: the text, the open points, each place where two records disagree, and what the recovery "
         "rule gives. This is a draft: stored with who wrote it, a time and a version number.")
    def save_claim_summary(body: ClaimSummary, claim_id: str = clm_p):
        payload = {"summary_text": body.summary_text, "open_points": body.open_points,
                   "disagreements": [x.model_dump() for x in body.disagreements], "recovery": body.recovery}
        v = st.add_draft(claim_or_404(claim_id), "summary_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    @reg(app, "post", "/claims/{claim_id}/coverage-check", "save_coverage_check", "Save a coverage check (draft)",
         "Save the reading of a loss against the policy wording: one row for each clause and endorsement that bears on the loss, where "
         "the loss stands against the wording, what the wording is silent on, and what the recovery rule gives. This is a draft for "
         "the adjuster: stored with who wrote it, a time and a version number. It decides nothing about the claim.")
    def save_coverage_check(body: CoverageCheck, claim_id: str = clm_p):
        payload = {"rows": [x.model_dump() for x in body.rows], "position": body.position, "silent_on": body.silent_on,
                   "recovery": body.recovery}
        v = st.add_draft(claim_or_404(claim_id), "coverage_check_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    def settle(c, excluded):
        policy = d()["policies"][c["policy_id"]]
        sched, motor = policy["schedule"], policy["product"] == "private_motor"
        lines = all_lines(c)
        if not lines:
            raise conflict(f"{c['claim_id']} has no invoice or estimate line to work from. Nothing was worked out.")
        ids = {line["line_id"] for line in lines}
        unknown = [x.line_id for x in excluded if x.line_id not in ids]
        if unknown:
            raise conflict(f"Not a line of {c['claim_id']}: {', '.join(unknown)}. Its lines are: {', '.join(sorted(ids))}. Nothing was worked out.")
        out = {x.line_id: x for x in excluded}
        rows, glass_left, trace_left = [], 500.0, 1500.0
        listed = {str(item).lower() for item in sched.get("listed_items", [])}
        for line in lines:
            amount, cat, allowed, note = line["amount"], line["category"], line["amount"], ""
            limit_clause = None
            if line["line_id"] in out:
                x = out[line["line_id"]]
                rows.append({**line, "allowed": 0.0, "excluded": True, "limited": False, "clause": x.clause,
                             "note": f"Not covered under clause {x.clause}: {x.reason}"})
                continue
            if motor and cat == "windscreen":
                allowed = min(amount, glass_left)
                glass_left -= allowed
                if allowed < amount:
                    note = "Limited to USD 500.00 for any one claim by clause 3.2."
                    limit_clause = "3.2"
            elif motor and cat == "hire_car":
                days, rate = min(line.get("quantity", 1), 10), min(line.get("unit_amount", amount), 40.0)
                allowed = min(amount, round(days * rate, 2))
                if allowed < amount:
                    note = f"Limited to USD 40.00 a day for up to 10 days by clause 3.4: {days} days at {usd(rate)} a day."
                    limit_clause = "3.4"
            elif motor and cat == "vehicle":
                allowed = min(amount, sched["sum_insured"])
                if allowed < amount:
                    note = f"Limited to the sum insured of {usd(sched['sum_insured'])} by clause 3.1."
                    limit_clause = "3.1"
            elif motor and cat == "personal_belongings":
                allowed = min(amount, 300.0)
                if allowed < amount:
                    note = "Limited to USD 300.00 for any one claim by clause 3.3."
                    limit_clause = "3.3"
            elif not motor and cat == "trace_and_access":
                allowed = min(amount, trace_left)
                trace_left -= allowed
                if allowed < amount:
                    note = "Limited to USD 1,500.00 for any one claim by clause 3.4."
                    limit_clause = "3.4"
            elif not motor and cat == "contents_item" and line["description"].lower() not in listed:
                allowed = min(amount, 2500.0)
                if allowed < amount:
                    note = "Limited to USD 2,500.00 for any one item by clause 3.2: the item is not listed in the schedule."
                    limit_clause = "3.2"
            elif not motor and cat == "alternative_accommodation":
                allowed = min(amount, sched["alternative_accommodation_limit"])
                if allowed < amount:
                    note = f"Limited to {usd(sched['alternative_accommodation_limit'])}, 10 percent of the buildings sum insured, by clause 3.3."
                    limit_clause = "3.3"
            rows.append({**line, "allowed": round(allowed, 2), "excluded": False, "limited": limit_clause is not None,
                         "clause": limit_clause, "note": note})
        claimed = round(sum(r["amount"] for r in rows), 2)
        allowed_total = round(sum(r["allowed"] for r in rows), 2)
        if c["claim_type"] == "home_escape_of_water":
            deductible, ded_clause = 500.0, "4.2"
        else:
            deductible, ded_clause = sched["deductible"], "4.1"
        payable = round(max(0.0, allowed_total - deductible), 2)
        approver = next(level["approver"] for level in d()["handling_guide"]["settlement_authority"]["levels"]
                        if level["up_to"] is None or payable <= level["up_to"])
        parts = " + ".join(f"{r['allowed']:,.2f}" for r in rows if not r["excluded"]) or "0.00"
        return {"claim_id": c["claim_id"], "currency": "USD", "lines": rows, "total_claimed": claimed,
                "total_not_covered": round(sum(r["amount"] for r in rows if r["excluded"]), 2),
                "total_reduced_by_limits": round(sum(r["amount"] - r["allowed"] for r in rows if not r["excluded"]), 2),
                "total_allowed": allowed_total, "deductible": deductible, "deductible_clause": ded_clause, "amount_payable": payable,
                "approval_needed_from": approver, "authority_rule": "HG-5",
                "working": [f"Lines allowed: {parts} = {allowed_total:,.2f}",
                            f"Less the deductible under clause {ded_clause}: {allowed_total:,.2f} - {deductible:,.2f} = {payable:,.2f}",
                            f"Amount payable: {usd(payable)}. Under rule HG-5 this needs the approval of the {approver}."]}

    @reg(app, "post", "/claims/{claim_id}/settlement/calculate", "calculate_settlement", "Work out a settlement (reads only)",
         "Work out the amount payable on a claim. You say which invoice or estimate lines the wording does not cover, each with its "
         "clause. The system applies the limits of the wording to the other lines, takes the deductible, adds up, and says whose "
         "approval the amount needs under rule HG-5. The answer gives every line with the amount claimed, the amount allowed and a "
         "note, the totals, the deductible with its clause, the amount payable and the working, line by line. It saves nothing and "
         "changes nothing. Use these figures and do not add up yourself.")
    def calculate_settlement(body: SettlementRequest, claim_id: str = clm_p):
        return {**settle(claim_or_404(claim_id), body.excluded_lines), "saved": False}

    @reg(app, "post", "/claims/{claim_id}/settlement", "save_settlement_calculation", "Save a settlement calculation (draft)",
         "Save a settlement calculation for the adjuster. You send the lines the wording does not cover, each with its clause, as for "
         "calculate_settlement; the system works the figures out again and stores them, and the answer returns them. This is a draft: "
         "stored with who wrote it, a time and a version number. It approves nothing and pays nothing.")
    def save_settlement_calculation(body: SettlementDraft, claim_id: str = clm_p):
        c = claim_or_404(claim_id)
        result = settle(c, body.excluded_lines)
        v = st.add_draft(c, "settlement_drafts", {**result, "excluded_lines": [x.model_dump() for x in body.excluded_lines],
                                                  "notes": body.notes}, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    @reg(app, "post", "/claims/{claim_id}/letters", "save_claim_letter", "Save a letter to the claimant (draft)",
         "Save a letter to the claimant, made from one of the letter templates. This is a draft: stored with who wrote it, a time and "
         "a version number. It sends nothing. Refused with 409 for the decline template when no adjuster's decision to decline is "
         "recorded on the claim (rule HG-6).")
    def save_claim_letter(body: Letter, claim_id: str = clm_p):
        c = claim_or_404(claim_id)
        if body.template_id == "TPL-DECLINE" and (c.get("decision") or {}).get("decision") != "declined":
            raise conflict(f"No adjuster's decision to decline is recorded on {claim_id}. Under rule HG-6 a letter that declines a claim "
                           "is written only after that decision is recorded. Nothing was saved.")
        v = st.add_draft(c, "letter_drafts", {"template_id": body.template_id, "language": body.language,
                                              "letter_text": body.letter_text}, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    # ------------------------------------------------------------ claims: changes, each for a named person
    @reg(app, "post", "/claims/{claim_id}/decision", "record_claim_decision", "Record an adjuster's decision on cover (change)",
         "Record the adjuster's decision on a claim: cover accepted or declined, with the reason and the clause. This is a change and "
         "needs the adjuster's name. Refused with 409 when a decision is already recorded.")
    def record_claim_decision(body: Decision, claim_id: str = clm_p):
        c = claim_or_404(claim_id)
        if c.get("decision"):
            raise conflict(f"A decision is already recorded on {claim_id}, by {c['decision']['decided_by']} on "
                           f"{long_date(c['decision']['decided_on'])}. Nothing was changed.")
        with st.lock:
            c["decision"] = {"decision": body.decision, "decided_by": body.decided_by, "role": "adjuster",
                             "decided_on": today().isoformat(), "reason": body.reason, "clause": body.clause}
            c["status"] = "decided" if body.decision == "declined" else "in_assessment"
            st.save()
        return {"applied": True, "kind": "change", "claim_id": claim_id, "decision": c["decision"]}

    @reg(app, "post", "/claims/{claim_id}/letters/send", "send_claim_letter", "Send a saved letter to the claimant (change)",
         "Send a saved letter. This is a change and needs the name of the handler who read it. Refused with 409 when there is no such "
         "saved letter.")
    def send_claim_letter(body: SendLetter, claim_id: str = clm_p):
        c = claim_or_404(claim_id)
        if body.draft_version > len(c["letter_drafts"]):
            raise conflict(f"{claim_id} has no saved letter with version {body.draft_version}. Nothing was sent.")
        with st.lock:
            sent = {"letter_version": body.draft_version, "sent_by": body.sent_by, "sent_on": today().isoformat()}
            c["letters_sent"].append(sent)
            st.save()
        return {"applied": True, "kind": "change", "claim_id": claim_id, "sent": sent}

    @reg(app, "post", "/claims/{claim_id}/payments", "record_claim_payment", "Approve and record a claim payment (change)",
         "Approve a saved settlement calculation and record the payment. This is a change and needs the name of the person with the "
         "authority for the amount. Refused with 409 when there is no such saved calculation, or when the adjuster has not accepted cover.")
    def record_claim_payment(body: Payment, claim_id: str = clm_p):
        c = claim_or_404(claim_id)
        if (c.get("decision") or {}).get("decision") != "cover_accepted":
            raise conflict(f"No adjuster has accepted cover on {claim_id}. Nothing was paid.")
        if body.draft_version > len(c["settlement_drafts"]):
            raise conflict(f"{claim_id} has no saved settlement calculation with version {body.draft_version}. Nothing was paid.")
        with st.lock:
            draft = c["settlement_drafts"][body.draft_version - 1]
            paid = {"settlement_version": body.draft_version, "amount": draft["amount_payable"], "currency": "USD",
                    "approved_by": body.approved_by, "paid_on": today().isoformat()}
            c["payments"].append(paid)
            c["status"] = "closed"
            st.save()
        return {"applied": True, "kind": "change", "claim_id": claim_id, "payment": paid}

    return app
