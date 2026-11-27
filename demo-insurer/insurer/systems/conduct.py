"""Conduct: complaints with the complaints procedure, the conduct rules with an audit sample, the regulators' publications
with the obligations register, and the document sets of disputed claims with the privilege guide.

Every save is a draft: a complaints officer, the compliance officer or a lawyer decides."""

from __future__ import annotations

from typing import Literal

from fastapi import Path, Query
from pydantic import Field

from ..common import Ctx, conflict, ForgivingModel, listing, make_subapp, not_found, reg
from ..seed_conduct import (COMPLAINT_ROLES, COMPLAINTS_HOW_TO_READ, CONDUCT_RULES_HOW_TO_READ, DOCUMENT_CATEGORIES_HOW_TO_READ,
                            FILE_KINDS, LINES_NOTE, LINES_WRITTEN, OBLIGATION_STOP_WORDS, OBLIGATIONS_HOW_TO_READ,
                            PRIVILEGE_HOW_TO_READ, REGULATORS, WORKING_DAYS_NOTE, complaint_deadlines, document_facts, holiday_list,
                            measure_audit_file, publication_key_dates, rules_for_kind)
from ..seed_policy import cover_on

KEY = "conduct"
TITLE = "Conduct"
LINE = ("Complaints with the complaints procedure, the conduct rules with an audit sample, the regulators' publications with the "
        "obligations register, and the document sets of disputed claims with the privilege guide.")

DRAFTED_BY = Field("agent", description="Who wrote the draft. Free text.")


class ComplaintResponse(ForgivingModel):
    is_a_complaint: Literal["yes", "no"] = Field(
        ..., description="yes when the customer expresses dissatisfaction, however it is worded. no when the item is only a question "
                         "or a request (rule CH-6): it is then an enquiry for the policy servicing team.")
    category_id: str = Field("", description="The complaint category, for example CC-3. One category: the main thing the customer "
                                             "is unhappy with. Leave empty when the item is not a complaint.")
    rules_that_apply: list[str] = Field(default_factory=list, description="The handling rules that turn on this complaint, by id: "
                                        "for example CH-3 for a customer marked vulnerable, CH-4 where the regulator or a lawyer is "
                                        "mentioned, CH-5 for a repeat complaint, CH-6 for an item that is not a complaint. Leave "
                                        "empty when none of these applies.")
    route_to: Literal["complaints_officer", "senior_complaints_officer", "policy_servicing"] = Field(
        ..., description="Who the item goes to: complaints_officer for a complaint; senior_complaints_officer where the complaint "
                         "mentions the regulator, a lawyer or legal action (CH-4); policy_servicing for an item that is not a "
                         "complaint (CH-6).")
    linked_complaint_id: str = Field("", description="For a repeat complaint (CH-5), the id of the earlier complaint about the same "
                                                     "matter, for example CMP-7051. Leave empty when there is none, or when the "
                                                     "earlier complaint was about a different matter.")
    draft_response: str = Field(..., min_length=1, description="The response to the customer, as a draft for the complaints officer: "
                                "what we understood, what will be looked at, and the dates the system gives. It does not say that "
                                "the complaint is upheld or rejected, offers no money and gives no opinion on the law. For an item "
                                "that is not a complaint, a short reply that the question has gone to the policy servicing team.")
    log_entry: str = Field(..., min_length=1, description="The entry for the complaints log, in a few sentences: who, about what, "
                                                          "the policy and the claim, the category, the dates the system gives, who "
                                                          "it goes to and why.")
    drafted_by: str = DRAFTED_BY


class AuditRow(ForgivingModel):
    file_id: str = Field(..., description="The id of the file, for example AF-7203.")
    rule_id: str = Field(..., description="The id of the conduct rule, for example CND-1.")
    result: Literal["met", "not_met", "cannot_tell", "not_applicable"] = Field(
        ..., description="met when the file meets the rule, also when the value is exactly on the limit; not_met when it plainly "
                         "does not; cannot_tell when a date or a document the rule needs is not on the record; not_applicable when "
                         "the rule does not apply to this file, for example the decline letter rule on a claim that was accepted.")
    evidence: str = Field("", description="What the result rests on: the measured value and the limit as the system gives them, or "
                                          "the words of the letter or the field of the file. For cannot_tell, say what is missing.")


class AuditRecord(ForgivingModel):
    rows: list[AuditRow] = Field(..., min_length=1, description="One row for every conduct rule of every file in the sample, the "
                                 "rules that are met as well: three rows for a claims file, two for a sales file, two for a policy "
                                 "file.")
    files_that_need_a_person: list[str] = Field(default_factory=list, description="The ids of the files a person must look at, "
                                                "because a rule could not be told. Leave empty when there is none.")
    summary: str = Field(..., min_length=1, description="The audit in a few sentences for the compliance officer: how many files, "
                                                        "which rules were not met on which files with the figures the system gives, "
                                                        "and what could not be told. It does not call anything a breach.")
    drafted_by: str = DRAFTED_BY


class ImpactNote(ForgivingModel):
    finding: Literal["bears_on_an_obligation", "consultation_only", "does_not_apply", "duplicate_of_an_earlier_publication",
                     "no_matching_obligation"] = Field(
        ..., description="bears_on_an_obligation when the publication changes, sets or restates what an obligation of the register "
                         "says; consultation_only when it is a proposal and changes nothing yet; does_not_apply when it is about a "
                         "line of business the insurer does not write; duplicate_of_an_earlier_publication when it repeats an "
                         "earlier item under a new reference; no_matching_obligation when it applies to the insurer and no "
                         "obligation of the register covers it.")
    obligation_ids: list[str] = Field(default_factory=list, description="The obligations the publication bears on, by id, for "
                                      "example OBL-05. For a consultation, the obligations it would bear on if adopted. For a "
                                      "duplicate, the obligations the earlier item was noted against. Leave empty for does_not_apply "
                                      "and for no_matching_obligation.")
    related_publication_id: str = Field("", description="The id of an earlier publication this one amends or repeats, for example "
                                                        "PUB-7291. Needed for a duplicate. Otherwise leave empty when there is none.")
    note: str = Field(..., min_length=1, description="The impact note for the compliance officer: what the publication says, what "
                                                     "changes and from which date as the system gives it, and who owns the "
                                                     "obligation. It gives no opinion on the law and reports nothing to a regulator.")
    drafted_by: str = DRAFTED_BY


class ScheduleRow(ForgivingModel):
    document_id: str = Field(..., description="The id of the document, for example DSP-7401-D08.")
    category_id: str = Field(..., description="The document category, for example DC-5. A copy takes the category of the original.")
    date: str = Field("", description="The date of the document as the record gives it. Leave empty when the document has no date.")
    author: str = Field("", description="The author as the record gives it. Leave empty when the document names no author.")
    may_be_privileged: Literal["yes", "no", "unclear"] = Field(
        ..., description="yes when the privilege guide says the document may be privileged; no when the guide says it is not; "
                         "unclear when the guide does not settle it or says the question is for the lawyer, for example legal "
                         "advice that was sent outside the insurer. This is a flag for the lawyers, not a legal opinion.")
    rule_id: str = Field(..., description="The rule of the privilege guide the flag rests on, for example PG-4.")
    duplicate_of: str = Field("", description="For a copy, the id of the original document in the same set. Otherwise leave empty.")
    note: str = Field("", description="A sentence of reason: who wrote to whom and what the document does.")


class DocumentSchedule(ForgivingModel):
    rows: list[ScheduleRow] = Field(..., min_length=1, description="One row for every document of the set, each document once.")
    summary: str = Field(..., min_length=1, description="The schedule in a few sentences for the lawyers: how many documents, how "
                                                        "many flagged yes, no and unclear, and which ones the lawyer must look at "
                                                        "first.")
    drafted_by: str = DRAFTED_BY


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds complaints with the complaint categories and handling rules, the insurer's "
                                  "conduct rules with a sample of files to audit, the publications of the regulators the insurer "
                                  "names with the obligations register, and the documents of disputed claims with the document "
                                  "categories and the privilege guide. The Meridia Insurance Authority and the Meridia Data "
                                  "Protection Office are invented, as is every circular. The system does every day count. Every "
                                  "save is a draft with who wrote it, a time and a version number. Nothing here upholds or rejects "
                                  "a complaint, sends a letter, reports to a regulator or gives a legal opinion: a person decides.")
    st = ctx.store
    d = lambda: st.data
    today = lambda: ctx.settings.insurer_today.isoformat()
    cmp_p = Path(..., description="Complaint id, for example CMP-7101.")
    aud_p = Path(..., description="Audit sample id, for example AUD-7200.")
    file_p = Path(..., description="Audit file id, for example AF-7201.")
    pub_p = Path(..., description="Publication id, for example PUB-7301.")
    dsp_p = Path(..., description="Disputed claim id, for example DSP-7401.")

    def one(name, kind, ident, hint):
        item = d()[name].get(ident)
        if not item:
            raise not_found(kind, ident, hint)
        return item

    cmp_or_404 = lambda i: one("cd_complaints", "complaint", i, "Use list_complaints to find ids.")
    aud_or_404 = lambda i: one("cd_audit_samples", "audit sample", i, "Use list_audit_samples to find ids.")
    file_or_404 = lambda i: one("cd_audit_files", "audit file", i, "Use get_audit_sample to find ids.")
    pub_or_404 = lambda i: one("cd_publications", "publication", i, "Use list_regulatory_publications to find ids.")
    dsp_or_404 = lambda i: one("cd_disputes", "disputed claim", i, "Use list_disputed_claims to find ids.")

    def without(record, *fields):
        return {k: v for k, v in record.items() if k not in fields}

    def ids(values):
        return [x.strip().upper() for x in values if x and x.strip()]

    # ------------------------------------------------------------ complaints
    def care_of(customer):
        rec = d()["cd_customer_care"].get(customer)
        if rec:
            return dict(rec)
        return {"customer": customer, "vulnerable": False, "note": "The customer care record holds no mark for this customer."}

    def complaint_view(c):
        care = care_of(c["customer"])
        view = {**without(c, "response_drafts"), "customer_care_record": care}
        policy = d()["policies"].get(c["policy_id"]) if c["policy_id"] else None
        if policy:
            view["policy"] = {k: policy.get(k) for k in ("policy_id", "product", "holder", "address", "status", "status_note",
                                                         "period_start", "period_end", "wording_id")}
            view["policy"]["cover_on_the_day_received"] = cover_on(policy, c["received"])
            view["claims_on_the_policy"] = [
                {"claim_id": k["claim_id"], "claim_is_for": k["claim_type_label"], "description": k["description"],
                 "date_of_loss": k["loss_date"], "date_reported": k["reported_date"], "status": k["status"],
                 "handling_team": k.get("handling_team"), "estimate": k["estimate"], "decision": k.get("decision"),
                 "notes": k.get("notes", []), "letters_sent": len(k.get("letters_sent", [])),
                 "paid": round(sum(p["amount"] for p in k.get("payments", [])), 2),
                 "this_complaint_names_it": k["claim_id"] == c["claim_id"]}
                for k in d()["claims"].values() if k["policy_id"] == c["policy_id"]]
        else:
            view["policy"], view["claims_on_the_policy"] = None, []
        view["earlier_complaints_by_this_customer"] = [
            without(o, "response_drafts") for o in d()["cd_complaints"].values()
            if o["customer"] == c["customer"] and o["complaint_id"] != c["complaint_id"] and o["received"] < c["received"]]
        view["deadlines"] = complaint_deadlines(c, care["vulnerable"], today()) if c["status"] == "new" else None
        view["drafts_on_file"] = len(c["response_drafts"])
        view["read_on"] = today()
        return view

    @reg(app, "get", "/complaints-procedure", "get_complaints_procedure", "Get the complaint categories and the handling rules",
         "Read the complaints procedure in one call. categories gives the numbered complaint categories CC-1 to CC-6, each with a "
         "name and what it covers. handling_rules gives the rules CH-1 to CH-7 with their exact text: the time limit for the "
         "acknowledgement in working days, the time limit for the final response in days, what a vulnerable customer mark changes, "
         "where a complaint that mentions the regulator or a lawyer goes, how a repeat complaint is linked, what is not a complaint, "
         "and who decides. A rule of the kind measured turns on dates and the system works them out; a rule of the kind for_reading "
         "is read against the words of the complaint. who_handles names the people an item is sent to. public_holidays lists the "
         "invented public holidays of Meridia that the system leaves out when it counts working days. It works out no date itself: "
         "get_complaint gives a complaint with its dates.")
    def get_complaints_procedure():
        return {"document": "Complaints procedure", "version": "5", "how_to_read": COMPLAINTS_HOW_TO_READ,
                "categories": list(d()["cd_complaint_categories"].values()),
                "handling_rules": list(d()["cd_complaint_rules"].values()), "who_handles": dict(COMPLAINT_ROLES),
                "working_days_note": WORKING_DAYS_NOTE, "public_holidays": holiday_list(ctx.settings.insurer_today)}

    @reg(app, "get", "/complaints", "list_complaints", "List the complaints",
         "List the complaints, whole: id, status (new or closed), the channel, the date received, the customer, the policy and the "
         "claim it concerns where it names one, the text as the customer wrote or said it, the date it was acknowledged (empty when "
         "no acknowledgement is recorded) and, for a closed complaint, the category, the matter and the outcome a complaints officer "
         "recorded. With a status only complaints of that status are returned. Saved drafts are not in the list. For one complaint "
         "with the policy, the claims, the earlier complaints and the dates worked out, use get_complaint.")
    def list_complaints(status: str | None = Query(None, description="Only complaints with this status: new or closed. Leave empty "
                                                                     "for all.")):
        wanted = (status or "").strip().lower()
        if wanted and wanted not in ("new", "closed"):
            raise conflict(f"{status} is not a status here. Use new or closed, or leave it empty. Nothing was read.")
        return listing([without(c, "response_drafts") for c in d()["cd_complaints"].values() if not wanted or c["status"] == wanted])

    @reg(app, "get", "/complaints/{complaint_id}", "get_complaint", "Get one complaint with the policy, the claims and the deadlines",
         "Read one complaint with everything a response needs, in one call. It gives the text as the customer wrote or said it, the "
         "channel, the date received and the date acknowledged (empty when none is recorded). customer_care_record says whether the "
         "customer is marked vulnerable, with the reason and the way the customer prefers to be contacted. policy gives the policy "
         "from the policy system as it stands, with cover on the day the complaint was received. claims_on_the_policy lists every "
         "claim on that policy from the claims system as it stands: what it is for, the dates of loss and report, the status, the "
         "team, the adjuster's decision with its reason and clause where one is recorded, the notes, the number of letters sent and "
         "what was paid. earlier_complaints_by_this_customer lists each earlier complaint whole, with the matter and the outcome a "
         "complaints officer recorded: compare the matter before you call this one a repeat. deadlines is the system's count: the "
         "acknowledgement (limit, due date, working days elapsed, left and late, a status of met, met_late, not_yet_due, due_today or "
         "late, and a sentence) and the final response (the limit that applies, the due date, days elapsed and left, a sentence), "
         "with the public holidays inside the count. A complaint on its last day is due_today and is not late. Use these dates and "
         "do not count days yourself. The system does not sort the complaint and does not read its words: the category, and whether "
         "it is a complaint at all, are yours to read. Saved drafts are not part of the complaint: drafts_on_file only counts them, "
         "and list_complaint_response_drafts reads them.")
    def get_complaint(complaint_id: str = cmp_p):
        return complaint_view(cmp_or_404(complaint_id))

    @reg(app, "get", "/complaints/{complaint_id}/deadlines", "calculate_complaint_deadlines",
         "Work out the acknowledgement and final response dates of a complaint",
         "Work out the dates of one complaint against the handling rules. acknowledgement gives the limit in working days, the date "
         "it is due, the date it was acknowledged where one is recorded, the working days elapsed since the day received, the "
         "working days left or late, a status (met, met_late, not_yet_due, due_today or late), whether it is late as true or false, "
         "and a sentence. final_response gives the rule that sets the limit (CH-2, or CH-3 for a customer marked vulnerable), the "
         "limit in days, the due date (moved back to the last working day when the last day is not a working day), the days elapsed "
         "and left, and a sentence. public_holidays_in_the_count lists the public holidays the count passed over. The day received "
         "is day 0. It is the same count get_complaint carries. It saves nothing. The dates apply only where the item is a "
         "complaint. Refused with 409 for a closed complaint.")
    def calculate_complaint_deadlines(complaint_id: str = cmp_p):
        c = cmp_or_404(complaint_id)
        if c["status"] != "new":
            raise conflict(f"{complaint_id} is closed: a complaints officer closed it on {c['closed']['closed_on']}. Deadlines are "
                           "worked out for a complaint that is open. Nothing was worked out.")
        return {**complaint_deadlines(c, care_of(c["customer"])["vulnerable"], today()), "saved": False}

    @reg(app, "get", "/complaints/{complaint_id}/drafts", "list_complaint_response_drafts", "List the drafts saved on a complaint",
         "Read every draft response and log entry saved on a complaint, each with its version number, who wrote it and when. A saved "
         "draft is somebody's preparation for the complaints officer, not a fact of the complaint, not a decision and not a letter "
         "that was sent.")
    def list_complaint_response_drafts(complaint_id: str = cmp_p):
        return listing(cmp_or_404(complaint_id)["response_drafts"], complaint_id=complaint_id)

    @reg(app, "post", "/complaints/{complaint_id}/response", "save_complaint_response",
         "Save the draft response and log entry on a complaint (draft)",
         "Save what was prepared on a complaint: whether it is a complaint, its category, the handling rules that turn on it, who it "
         "goes to, the earlier complaint it is linked to where it is a repeat, the draft response to the customer and the entry for "
         "the complaints log. The system stores its own dates with it (the acknowledgement and final response dates) and the answer "
         "returns them. This is a draft for the complaints officer: stored with who wrote it, a time and a version number, earlier "
         "versions kept. It upholds nothing, rejects nothing, sends no letter, acknowledges nothing and pays nothing, and it changes "
         "nothing else: not the complaint's status, not the policy, not a claim. Refused with 409, and nothing saved, when the "
         "complaint is closed, when the category is not one of CC-1 to CC-6, when a complaint has no category, when an item that is "
         "not a complaint has a category or is not sent to policy_servicing, when a complaint is sent to policy_servicing, when a "
         "rule named is not one of CH-1 to CH-7, or when the linked complaint is not an earlier complaint by the same customer.")
    def save_complaint_response(body: ComplaintResponse, complaint_id: str = cmp_p):
        c = cmp_or_404(complaint_id)
        if c["status"] != "new":
            raise conflict(f"{complaint_id} is closed. A draft is saved only on a complaint that is open. Nothing was saved.")
        category = body.category_id.strip().upper()
        cats = d()["cd_complaint_categories"]
        if category and category not in cats:
            raise conflict(f"{body.category_id} is not a complaint category. The categories are {', '.join(cats)}. Nothing was saved.")
        if body.is_a_complaint == "yes":
            if not category:
                raise conflict(f"A complaint needs one category ({', '.join(cats)}). Nothing was saved.")
            if body.route_to == "policy_servicing":
                raise conflict("A complaint goes to the complaints officer, or to the senior complaints officer where it mentions "
                               "the regulator or a lawyer. Only an item that is not a complaint goes to policy_servicing. Nothing "
                               "was saved.")
        else:
            if category:
                raise conflict("An item that is not a complaint has no category (rule CH-6). Leave category_id empty. Nothing was saved.")
            if body.route_to != "policy_servicing":
                raise conflict("An item that is not a complaint goes to policy_servicing (rule CH-6). Nothing was saved.")
        rules = ids(body.rules_that_apply)
        unknown = [x for x in rules if x not in d()["cd_complaint_rules"]]
        if unknown:
            raise conflict(f"Not a handling rule (CH-1 to CH-7): {', '.join(unknown)}. Nothing was saved.")
        linked = body.linked_complaint_id.strip().upper()
        if linked:
            earlier = [o["complaint_id"] for o in d()["cd_complaints"].values()
                       if o["customer"] == c["customer"] and o["complaint_id"] != complaint_id and o["received"] < c["received"]]
            if linked not in earlier:
                raise conflict(f"{linked} is not an earlier complaint by {c['customer']}. Earlier complaints by this customer: "
                               f"{', '.join(earlier) or 'none'}. Leave linked_complaint_id empty when there is none. Nothing was saved.")
        dates = complaint_deadlines(c, care_of(c["customer"])["vulnerable"], today())
        worked = None
        if body.is_a_complaint == "yes":
            worked = {"received": c["received"], "acknowledgement_due_on": dates["acknowledgement"]["due_on"],
                      "acknowledgement_status": dates["acknowledgement"]["status"],
                      "acknowledgement_working_days_late": dates["acknowledgement"]["working_days_late"],
                      "final_response_rule": dates["final_response"]["rule_id"],
                      "final_response_due_on": dates["final_response"]["due_on"],
                      "customer_marked_vulnerable": dates["customer_marked_vulnerable"]}
        payload = {**body.model_dump(exclude={"drafted_by", "category_id", "rules_that_apply", "linked_complaint_id"}),
                   "category_id": category or None, "rules_that_apply": rules, "linked_complaint_id": linked or None,
                   "goes_to": COMPLAINT_ROLES[body.route_to], "dates_worked_out_by_the_system": worked}
        v = st.add_draft(c, "response_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v,
                "message": f"The response and the log entry are saved on {complaint_id} as a draft. Nothing is sent and the "
                           "complaint itself is unchanged."}

    # ------------------------------------------------------------ conduct rules and the audit sample
    def file_view(f):
        return {**f, "conduct_rules_for_this_kind_of_file": rules_for_kind(f["kind_of_file"]), "measured": measure_audit_file(f)}

    def sample_files(s):
        return [d()["cd_audit_files"][fid] for fid in s["file_ids"]]

    def pairs_of(s):
        return [(f["file_id"], rule) for f in sample_files(s) for rule in rules_for_kind(f["kind_of_file"])]

    @reg(app, "get", "/conduct-rules", "get_conduct_rules", "Get the conduct rules as numbered rules",
         "Read the insurer's conduct rules CND-1 to CND-7, each with its id, the kind of file it is for (claims, sales or policy), a "
         "heading, its text with the exact test, and its kind. A rule of the kind measured turns on dates: the system counts the "
         "days for a file and gives the measured value beside the limit. A rule of the kind for_reading is read against the file: "
         "the decline letter's text, or the field that says whether a needs statement is on the sales file. With a kind of file "
         "only the rules for that kind are returned. public_holidays lists the invented public holidays the system leaves out of a "
         "count of working days. It measures no file itself: get_audit_sample gives every file measured.")
    def get_conduct_rules(kind_of_file: str | None = Query(None, description="Only rules for this kind of file: claims, sales or "
                                                                             "policy. Leave empty for every rule.")):
        kind = (kind_of_file or "").strip().lower()
        if kind and kind not in FILE_KINDS:
            raise conflict(f"{kind_of_file} is not a kind of file here. Use one of: {', '.join(FILE_KINDS)}. Nothing was read.")
        rules = [r for r in d()["cd_conduct_rules"].values() if not kind or r["kind_of_file"] == kind]
        return listing(rules, document="Conduct rules", version="4", how_to_read=CONDUCT_RULES_HOW_TO_READ,
                       kind_of_file=kind or "all", working_days_note=WORKING_DAYS_NOTE,
                       public_holidays=holiday_list(ctx.settings.insurer_today))

    @reg(app, "get", "/audit-samples", "list_audit_samples", "List the audit samples",
         "List the audit samples: id, status, the period the files come from with its first and last day, when and by whom the "
         "sample was drawn, what it is, the ids of its files and how many files of each kind it holds. The files themselves are not "
         "in the list, and nor are saved audit records. For a sample with every file and its measure, use get_audit_sample.")
    def list_audit_samples():
        rows = []
        for s in d()["cd_audit_samples"].values():
            kinds = [f["kind_of_file"] for f in sample_files(s)]
            rows.append({**without(s, "record_drafts"), "files": len(kinds),
                         "files_by_kind": {k: kinds.count(k) for k in FILE_KINDS}})
        return listing(rows)

    @reg(app, "get", "/audit-samples/{sample_id}", "get_audit_sample", "Get one audit sample with every file and its measure",
         "Read one audit sample with everything an audit record needs, in one call. files has one whole record for each file: id, "
         "the kind of file, the customer, the product, a note where the file has one, and facts. For a claims file the facts are "
         "what the claim is for, the dates reported, acknowledged, pack complete and decided, the decision (accepted or declined) "
         "and, for a declined claim, the decline letter with its text. For a sales file: who sold the policy, whether a needs "
         "statement is on the file (yes or no) and its date, the date the policy was issued and the date the cooling-off notice was "
         "sent. For a policy file: the date the period ends, the date the renewal notice was sent, the change asked for with the "
         "dates it was asked for and confirmed. A date that is empty is not on the record. conduct_rules_for_this_kind_of_file names "
         "the rules to check on the file. measured is the system's count for the file: one row for each of those rules with the "
         "result (met, not_met, cannot_tell when a date is missing, for_reading when the rule is yours to read, not_applicable), the "
         "measured value, the limit, the unit, the amount over or short, and a sentence. A value exactly on a limit is met. Use "
         "these figures and do not count days yourself. rows_an_audit_record_needs says how many rows a complete record has. Saved "
         "audit records are not part of the sample: drafts_on_file only counts them, and list_audit_record_drafts reads them.")
    def get_audit_sample(sample_id: str = aud_p):
        s = aud_or_404(sample_id)
        return {**without(s, "record_drafts"), "conduct_rules": list(d()["cd_conduct_rules"].values()),
                "files": [file_view(f) for f in sample_files(s)], "rows_an_audit_record_needs": len(pairs_of(s)),
                "drafts_on_file": len(s["record_drafts"]), "read_on": today()}

    @reg(app, "get", "/audit-files/{file_id}/measure", "measure_audit_file_against_conduct_rules",
         "Measure one audit file against the dated conduct rules",
         "Measure one file of an audit sample against the conduct rules of its kind. The answer gives one row for each rule: the "
         "rule id and heading, the result (met, not_met, cannot_tell when a date the rule needs is not on the record, for_reading "
         "when the rule has no date and is read against the file, not_applicable when the rule does not apply to the file), the "
         "measured value, the limit, the unit (working days, days, or days before the period ends), the amount over or short of the "
         "limit, and a sentence with the dates. It also lists the rule ids by result and the public holidays that fell in the "
         "period of the file. A value exactly on a limit is met. It is the same measure get_audit_sample carries for the file. It "
         "reads no letter and no note, saves nothing and is not a finding.")
    def measure_audit_file_against_conduct_rules(file_id: str = file_p):
        return {**measure_audit_file(file_or_404(file_id)), "saved": False}

    @reg(app, "get", "/audit-samples/{sample_id}/drafts", "list_audit_record_drafts", "List the audit records saved on a sample",
         "Read every audit record saved on a sample, each with its version number, who wrote it and when. A saved record is "
         "somebody's preparation for the compliance officer, not a fact of any file and not a finding of a breach.")
    def list_audit_record_drafts(sample_id: str = aud_p):
        return listing(aud_or_404(sample_id)["record_drafts"], sample_id=sample_id)

    @reg(app, "post", "/audit-samples/{sample_id}/record", "save_audit_record", "Save the audit record on a sample (draft)",
         "Save the record of an audit: one row for every conduct rule of every file in the sample (met, not_met, cannot_tell or "
         "not_applicable, with the evidence), the files a person must look at, and a summary. The rules that are met are listed as "
         "well: the record shows what was checked. The system stores its own measure of the dated rules with it and the answer "
         "returns it. This is a draft for the compliance officer: stored with who wrote it, a time and a version number, earlier "
         "versions kept. It finds no breach, reports nothing to a regulator and contacts nobody, and it changes nothing else. "
         "Refused with 409, and nothing saved, when a row names a file that is not in the sample, a rule that is not a rule for "
         "that kind of file, or the same file and rule twice, when a rule of a file has no row (the refusal names every one that "
         "is missing), or when a file named as needing a person is not in the sample.")
    def save_audit_record(body: AuditRecord, sample_id: str = aud_p):
        s = aud_or_404(sample_id)
        needed = pairs_of(s)
        sent = [(r.file_id.strip().upper(), r.rule_id.strip().upper()) for r in body.rows]
        not_file = sorted({f for f, _ in sent if f not in s["file_ids"]})
        if not_file:
            raise conflict(f"Not a file of {sample_id}: {', '.join(not_file)}. The files are {', '.join(s['file_ids'])}. Nothing was saved.")
        wrong = [f"{f} {r}" for f, r in sent if (f, r) not in needed]
        if wrong:
            raise conflict(f"Not a conduct rule for that kind of file: {', '.join(wrong)}. A claims file has CND-1, CND-2 and CND-3; "
                           "a sales file CND-4 and CND-5; a policy file CND-6 and CND-7. Nothing was saved.")
        twice = sorted({f"{f} {r}" for f, r in sent if sent.count((f, r)) > 1})
        if twice:
            raise conflict(f"Given twice: {', '.join(twice)}. Each rule of each file has one row. Nothing was saved.")
        missing = [f"{f} {r}" for f, r in needed if (f, r) not in sent]
        if missing:
            raise conflict(f"The record must list every rule checked for every file, the rules met as well. {len(missing)} of "
                           f"{len(needed)} rows are missing: {', '.join(missing)}. Nothing was saved.")
        people = ids(body.files_that_need_a_person)
        not_file = [f for f in people if f not in s["file_ids"]]
        if not_file:
            raise conflict(f"Not a file of {sample_id}: {', '.join(not_file)}. Nothing was saved.")
        measured = {}
        for f in sample_files(s):
            m = measure_audit_file(f)
            measured[f["file_id"]] = {r["rule_id"]: r["result"] for r in m["rules"]}
        payload = {"rows": [{**r.model_dump(), "file_id": f, "rule_id": rule} for r, (f, rule) in zip(body.rows, sent)],
                   "files_that_need_a_person": people, "summary": body.summary, "rows_in_the_record": len(sent),
                   "measured_by_the_system": measured}
        v = st.add_draft(s, "record_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v,
                "message": f"The audit record is saved on {sample_id} as a draft. No file is changed and nothing is reported."}

    # ------------------------------------------------------------ regulators' publications and the obligations register
    def pub_view(p):
        return {**without(p, "impact_note_drafts"), "key_dates": publication_key_dates(p, today())}

    @reg(app, "get", "/publications", "list_regulatory_publications", "List the publications of the regulators the insurer names",
         "List the publications feed, whole, newest first: id, status (new for an item with no impact note yet, noted_earlier for an "
         "item the compliance officer has already mapped), the regulator, the regulator's own reference, the kind (circular, "
         "consultation_paper, fee_notice, guidance or notice), the title, the date published, the full text, and key_dates: each "
         "date the item carries (published, has effect from, comments close on, payment is due by) with the days from the insurer "
         "date worked out by the system. An item noted earlier also carries noted_earlier: the obligations it was mapped to and the "
         "note. regulators_named gives the regulators the insurer follows, and lines_of_business_written the lines the insurer "
         "writes: a publication about any other line does not apply to it. With a status only items of that status are returned. "
         "Saved impact notes are not in the list. The feed is invented, as are both regulators.")
    def list_regulatory_publications(status: str | None = Query(None, description="Only items with this status: new or "
                                                                                  "noted_earlier. Leave empty for all.")):
        wanted = "_".join((status or "").strip().lower().replace("-", " ").split())
        if wanted and wanted not in ("new", "noted_earlier"):
            raise conflict(f"{status} is not a status here. Use new or noted_earlier, or leave it empty. Nothing was read.")
        rows = [pub_view(p) for p in d()["cd_publications"].values() if not wanted or p["status"] == wanted]
        rows.sort(key=lambda p: p["published"], reverse=True)
        return listing(rows, regulators_named=REGULATORS, lines_of_business_written=LINES_WRITTEN, lines_note=LINES_NOTE,
                       counted_from=today())

    @reg(app, "get", "/publications/{publication_id}", "get_regulatory_publication", "Get one publication with its dates worked out",
         "Read one publication: the regulator, the reference, the kind, the title, the date published, the full text, and key_dates "
         "with the days from the insurer date worked out by the system (a date that has passed is given as days before). An item "
         "noted earlier carries the obligations it was mapped to. lines_of_business_written gives the lines the insurer writes. The "
         "system does not say which obligation a publication bears on, whether it amends or repeats an earlier item, or whether it "
         "applies: read the text, and use search_obligations_register. Saved impact notes are not part of the publication: "
         "drafts_on_file only counts them, and list_regulatory_impact_note_drafts reads them.")
    def get_regulatory_publication(publication_id: str = pub_p):
        p = pub_or_404(publication_id)
        return {**pub_view(p), "lines_of_business_written": LINES_WRITTEN, "lines_note": LINES_NOTE,
                "drafts_on_file": len(p["impact_note_drafts"]), "read_on": today()}

    @reg(app, "get", "/obligations", "get_obligations_register", "Get the obligations register",
         "Read the obligations register: a note on how to read it and every numbered obligation OBL-01 to OBL-12, each with its id, "
         "a heading, its text with the figures, the source it comes from (a rule of the regulator's rulebook, a circular or a piece "
         "of guidance, by reference), the owner with role and name, and the lines of business it is for. Where no obligation covers "
         "what a publication asks, the register is silent and the compliance officer decides whether a new one is needed. It maps "
         "nothing itself and is not advice on the law.")
    def get_obligations_register():
        return listing(list(d()["cd_obligations"].values()), document="Obligations register", version="11",
                       how_to_read=OBLIGATIONS_HOW_TO_READ, lines_of_business_written=LINES_WRITTEN)

    @reg(app, "get", "/obligations/search", "search_obligations_register", "Search the obligations register by words",
         "Find the obligations that name any word of the text, for example complaints or cooling-off, or a reference such as "
         "MIA-C-2026-09. Any word may match, in any order; common words are left out. The heading, the text, the source and the "
         "owner are searched. Each row is a whole obligation with the words that matched, and the rows with the most matching words "
         "come first. With no text every obligation is listed. When nothing matches the answer says so: the register is then silent "
         "on those words. Read the text of an obligation before you rely on it: a word can match an obligation that is about "
         "something else.")
    def search_obligations_register(text: str | None = Query(None, description="Words from the publication, for example complaints "
                                                                               "final response, or a reference. Leave empty to list "
                                                                               "every obligation.")):
        raw = (text or "").lower()
        for ch in ",.?:;()":
            raw = raw.replace(ch, " ")
        words = [w for w in raw.split() if len(w) > 2 and w not in OBLIGATION_STOP_WORDS]
        rows = []
        for o in d()["cd_obligations"].values():
            hay = f"{o['obligation_id']} {o['heading']} {o['text']} {o['source']} {o['owner']['role']} {o['owner']['name']}".lower()
            hits = [w for w in words if w in hay]
            if hits or not words:
                rows.append({**o, "matched_words": hits})
        rows.sort(key=lambda r: -len(r["matched_words"]))
        note = ""
        if words and not rows:
            note = ("No obligation of the register names any of these words. The register is silent on them: the compliance officer "
                    "decides whether a new obligation is needed.")
        return listing(rows, searched_for=text or "", words_used=words, note=note)

    @reg(app, "get", "/publications/{publication_id}/drafts", "list_regulatory_impact_note_drafts",
         "List the impact notes saved on a publication",
         "Read every impact note saved on a publication, each with its version number, who wrote it and when. A saved note is "
         "somebody's preparation for the compliance officer, not a change to the obligations register and not advice on the law.")
    def list_regulatory_impact_note_drafts(publication_id: str = pub_p):
        return listing(pub_or_404(publication_id)["impact_note_drafts"], publication_id=publication_id)

    @reg(app, "post", "/publications/{publication_id}/impact-note", "save_regulatory_impact_note",
         "Save an impact note on a publication (draft)",
         "Save the impact note on one publication: the finding (bears_on_an_obligation, consultation_only, does_not_apply, "
         "duplicate_of_an_earlier_publication or no_matching_obligation), the obligations it bears on, the earlier publication it "
         "amends or repeats, and the note. The system stores with it the owner of each obligation named, from the register, and the "
         "publication's dates with the days worked out, and the answer returns them. This is a draft for the compliance officer: "
         "stored with who wrote it, a time and a version number, earlier versions kept. It changes no obligation, reports nothing "
         "to a regulator and gives no legal opinion, and it changes nothing else: not the publication's status, not the register. "
         "Refused with 409, and nothing saved, when an obligation named is not in the register, when the related publication is not "
         "another item of the feed, when the finding is bears_on_an_obligation and no obligation is named, when the finding is "
         "does_not_apply or no_matching_obligation and obligations are named, or when a duplicate names no earlier publication.")
    def save_regulatory_impact_note(body: ImpactNote, publication_id: str = pub_p):
        p = pub_or_404(publication_id)
        named = ids(body.obligation_ids)
        register = d()["cd_obligations"]
        unknown = [x for x in named if x not in register]
        if unknown:
            raise conflict(f"Not an obligation of the register (OBL-01 to OBL-12): {', '.join(unknown)}. Nothing was saved.")
        related = body.related_publication_id.strip().upper()
        if related and (related not in d()["cd_publications"] or related == publication_id):
            raise conflict(f"{related} is not another publication of the feed. Use list_regulatory_publications to find ids, or "
                           "leave related_publication_id empty. Nothing was saved.")
        if body.finding == "bears_on_an_obligation" and not named:
            raise conflict("The finding bears_on_an_obligation needs the obligation, by id. Where no obligation covers the "
                           "publication, the finding is no_matching_obligation. Nothing was saved.")
        if body.finding in ("does_not_apply", "no_matching_obligation") and named:
            raise conflict(f"The finding {body.finding} names no obligation: leave obligation_ids empty. Nothing was saved.")
        if body.finding == "duplicate_of_an_earlier_publication" and not related:
            raise conflict("A duplicate needs the id of the earlier publication it repeats, in related_publication_id. Nothing was saved.")
        payload = {**body.model_dump(exclude={"drafted_by", "obligation_ids", "related_publication_id"}), "obligation_ids": named,
                   "related_publication_id": related or None,
                   "owners_from_the_register": [{"obligation_id": x, "heading": register[x]["heading"], "owner": dict(register[x]["owner"])}
                                                for x in named],
                   "dates_worked_out_by_the_system": publication_key_dates(p, today())}
        v = st.add_draft(p, "impact_note_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v,
                "message": f"The impact note is saved on {publication_id} as a draft. The obligations register is unchanged and "
                           "nothing is reported."}

    # ------------------------------------------------------------ disputed claims
    @reg(app, "get", "/document-guide", "get_litigation_document_guide", "Get the document categories and the privilege guide",
         "Read the two guides for sorting the documents of a disputed claim, in one call. document_categories gives the numbered "
         "categories DC-1 to DC-7 with a name and what each covers, and a note: a document is sorted by what it is and who it is "
         "from and to, not by what it quotes, and a copy takes the category of the original. privilege_guide gives the numbered "
         "rules PG-1 to PG-7, each with the flag it leads to (yes, no, unclear, or as the original for a copy) and its text: legal "
         "advice, documents made for litigation, a lawyer who is only copied, legal advice sent outside the insurer, the ordinary "
         "course of the claim, what the guide does not settle, and copies. PG-4 comes before PG-1. The guide is the insurer's own: "
         "it flags what may be privileged for the lawyers, who decide. It is not a legal opinion.")
    def get_litigation_document_guide():
        return {"document": "Litigation document guide", "version": "2",
                "document_categories": list(d()["cd_document_categories"].values()),
                "categories_how_to_read": DOCUMENT_CATEGORIES_HOW_TO_READ,
                "privilege_guide": list(d()["cd_privilege_guide"].values()), "privilege_how_to_read": PRIVILEGE_HOW_TO_READ}

    def dispute_brief(x):
        return {**without(x, "documents", "schedule_drafts"), "documents_in_the_set": len(x["documents"])}

    @reg(app, "get", "/disputed-claims", "list_disputed_claims", "List the disputed claims",
         "List the disputed claims: id, status, the claim reference, the title of the matter, the line of business, the "
         "policyholder, the amount in dispute, the stage (whether proceedings have started or are expected), a summary, the people "
         "in the matter with role, organisation and side, and the number of documents in the set. The documents themselves and "
         "saved schedules are not in the list: get_disputed_claim gives one claim with every document.")
    def list_disputed_claims():
        return listing([dispute_brief(x) for x in d()["cd_disputes"].values()])

    @reg(app, "get", "/disputed-claims/{dispute_id}", "get_disputed_claim", "Get one disputed claim with every document as text",
         "Read one disputed claim with everything a document schedule needs, in one call. people_in_the_matter names each person "
         "with role, organisation and side: insurer, insurer's lawyers (in-house counsel and the external firm), policyholder, "
         "claimant, their lawyers, expert, or third party. documents has every document of the set in the order of its id: the "
         "form (letter, email, file note, report, draft and so on), a title, the date (empty when the document has none), the "
         "author (empty when it names none) with the author's role, who it is to, who is copied, and the full text. For each "
         "document the system also gives recipients_outside_thornmere_and_its_lawyers (the people it was sent or copied to who are "
         "neither Thornmere staff nor Thornmere's lawyers) and identical_text_to (the id of an earlier document of the set with "
         "exactly the same text, for a copy). documents_in_date_order lists the ids oldest first, undated ones last. The system does "
         "not sort the documents into categories and does not say what may be privileged: read each text against the guide. Saved "
         "schedules are not part of the claim: drafts_on_file only counts them, and list_document_schedule_drafts reads them.")
    def get_disputed_claim(dispute_id: str = dsp_p):
        x = dsp_or_404(dispute_id)
        docs = document_facts(x)
        order = [doc["document_id"] for doc in sorted(docs, key=lambda doc: (doc["dated"] is None, doc["dated"] or "", doc["document_id"]))]
        return {**dispute_brief(x), "documents": docs, "documents_in_date_order": order,
                "documents_with_no_date": [doc["document_id"] for doc in docs if doc["dated"] is None],
                "drafts_on_file": len(x["schedule_drafts"]), "read_on": today()}

    @reg(app, "get", "/disputed-claims/{dispute_id}/drafts", "list_document_schedule_drafts",
         "List the document schedules saved on a disputed claim",
         "Read every document schedule saved on a disputed claim, each with its version number, who wrote it and when. A saved "
         "schedule is somebody's preparation for the lawyers, not a fact of any document and not a decision on privilege.")
    def list_document_schedule_drafts(dispute_id: str = dsp_p):
        return listing(dsp_or_404(dispute_id)["schedule_drafts"], dispute_id=dispute_id)

    @reg(app, "post", "/disputed-claims/{dispute_id}/schedule", "save_document_schedule",
         "Save the document schedule on a disputed claim (draft)",
         "Save the schedule of a disputed claim's documents: one row for each document with its category, date, author, whether it "
         "may be privileged (yes, no or unclear) with the rule of the privilege guide, the original it is a copy of where it is "
         "one, and a note; then a summary. The system stores its own counts with it (documents in the set, rows flagged yes, no "
         "and unclear) and the answer returns them. This is a draft for the lawyers: stored with who wrote it, a time and a "
         "version number, earlier versions kept. It decides nothing about privilege, discloses and withholds nothing, gives no "
         "legal opinion and contacts nobody, and it changes nothing else. Refused with 409, and nothing saved, when a row names a "
         "document that is not in the set or names one twice, when a document of the set has no row (the refusal names each one), "
         "when a category is not one of DC-1 to DC-7, when a rule is not one of PG-1 to PG-7, or when duplicate_of is not another "
         "document of the set.")
    def save_document_schedule(body: DocumentSchedule, dispute_id: str = dsp_p):
        x = dsp_or_404(dispute_id)
        known = [doc["document_id"] for doc in x["documents"]]
        sent = [r.document_id.strip().upper() for r in body.rows]
        unknown = [i for i in sent if i not in known]
        if unknown:
            raise conflict(f"Not a document of {dispute_id}: {', '.join(unknown)}. The set runs from {known[0]} to {known[-1]}. "
                           "Nothing was saved.")
        twice = sorted({i for i in sent if sent.count(i) > 1})
        if twice:
            raise conflict(f"Given twice: {', '.join(twice)}. Each document has one row. Nothing was saved.")
        missing = [i for i in known if i not in sent]
        if missing:
            raise conflict(f"The schedule has one row for every document of the set. {len(missing)} of {len(known)} have no row: "
                           f"{', '.join(missing)}. Nothing was saved.")
        cats, guide = d()["cd_document_categories"], d()["cd_privilege_guide"]
        rows = []
        for r, doc_id in zip(body.rows, sent):
            category, rule, original = r.category_id.strip().upper(), r.rule_id.strip().upper(), r.duplicate_of.strip().upper()
            if category not in cats:
                raise conflict(f"{r.category_id} on {doc_id} is not a document category. The categories are {', '.join(cats)}. "
                               "Nothing was saved.")
            if rule not in guide:
                raise conflict(f"{r.rule_id} on {doc_id} is not a rule of the privilege guide. The rules are {', '.join(guide)}. "
                               "Nothing was saved.")
            if original and (original not in known or original == doc_id):
                raise conflict(f"duplicate_of on {doc_id} must be another document of the set, and {original} is not. Leave it "
                               "empty when the document is not a copy. Nothing was saved.")
            rows.append({**r.model_dump(), "document_id": doc_id, "category_id": category, "rule_id": rule,
                         "duplicate_of": original or None})
        flags = [r["may_be_privileged"] for r in rows]
        payload = {"rows": rows, "summary": body.summary,
                   "counted_by_the_system": {"documents_in_the_set": len(known), "rows": len(rows), "flagged_yes": flags.count("yes"),
                                             "flagged_no": flags.count("no"), "flagged_unclear": flags.count("unclear")}}
        v = st.add_draft(x, "schedule_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v,
                "message": f"The document schedule is saved on {dispute_id} as a draft. No document is changed and nothing is "
                           "decided about privilege."}

    return app
