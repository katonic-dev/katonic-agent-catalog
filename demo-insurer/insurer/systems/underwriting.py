"""Underwriting: the underwriting guidelines, the appetite statement, broker submissions, authority levels and referral
rules, referrals with precedents, the renewal rules and renewals. Every save is a draft: an underwriter decides."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import Path, Query
from pydantic import Field, model_validator

from ..common import Ctx, conflict, ForgivingModel, listing, make_subapp, not_found, reg, _choices_of
from ..seed_underwriting import (ALL_CLASSES, APPETITE_HOW_TO_READ, AUTHORITY_HOW_TO_READ, CLASSES, CONSTRUCTION_CLASSES, GRADE_ORDER,
                                 GUIDELINES_HOW_TO_READ, RENEWAL_RULES_HOW_TO_READ, SEARCH_STOP_WORDS, check_authority,
                                 measure_submission, renewal_expiry, renewal_pack)

KEY = "underwriting"
TITLE = "Underwriting"
LINE = ("The underwriting guidelines, the appetite statement, broker submissions, authority levels and referral rules, referrals "
        "with precedents, the renewal rules and renewals.")

DRAFTED_BY = Field("agent", description="Who wrote the draft. Free text.")
CLASS_Q = "One of commercial_property, motor_fleet or public_liability."
NO_VALUE_WORDS = {"", "none", "no", "null", "nil", "na", "n a", "not needed", "not applicable", "nobody", "no one", "no grade",
                  "no referral", "no referral needed", "empty"}


class ForgivingModel(ForgivingModel):  # noqa: F811
    """As the shared model, and an optional fixed choice sent as an empty text, "none", "not needed" and the like is no value."""

    @model_validator(mode="before")
    @classmethod
    def _read_empty_words_as_no_value(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data
        out = dict(data)
        for name, field in cls.model_fields.items():
            value = out.get(name)
            if isinstance(value, str) and not field.is_required() and field.default is None and _choices_of(field.annotation):
                plain = " ".join(value.strip().lower().replace("/", " ").replace("-", " ").replace("_", " ").replace(".", " ").split())
                if plain in NO_VALUE_WORDS:
                    out[name] = None
        return out


class GuidelineFinding(ForgivingModel):
    rule_id: str = Field(..., description="The id of the guideline, for example UG-3.")
    finding: Literal["within", "outside", "missing", "cannot_tell"] = Field(
        ..., description="within when the submission meets the rule; outside when it plainly does not; missing when the submission "
                         "lacks what the rule needs, for example no claims history; cannot_tell when the form and a document "
                         "disagree, or the documents do not settle it.")
    evidence: str = Field("", description="What the finding rests on: the measured figure and the limit as the system gives them, or "
                                          "the words of a document with its id, for example the survey note (SBM-6506-D2). For "
                                          "missing, say what is missing.")


class UnderwritingFile(ForgivingModel):
    findings: list[GuidelineFinding] = Field(..., min_length=1, description="One row for each guideline of the submission's class "
                                             "of business, the measured ones and the ones for reading.")
    missing_items: list[str] = Field(default_factory=list, description="What the submission lacks, one item each. Leave empty when "
                                                                       "nothing is missing. Never fill a gap with a guess.")
    contradictions: list[str] = Field(default_factory=list, description="Each place where the form and a document say different "
                                                                        "things, with both versions and the document id. Leave "
                                                                        "empty when there is none.")
    next_step: Literal["ready_for_the_underwriter", "ask_the_broker"] = Field(
        ..., description="ready_for_the_underwriter when the file is complete, whether the risk is within or outside the guidelines: "
                         "the underwriter decides. ask_the_broker when something is missing or two sources disagree. No value "
                         "accepts, declines or quotes.")
    question_for_the_broker: str = Field("", description="What to ask the broker, in a sentence. Needed when the next step is "
                                                         "ask_the_broker. Otherwise leave empty.")
    summary: str = Field(..., min_length=1, description="The file in a few sentences for the underwriter: what is within, what is "
                                                        "outside, what is missing, with the figures the system gives.")
    drafted_by: str = DRAFTED_BY


class PrecedentRow(ForgivingModel):
    precedent_id: str = Field(..., description="The id of the precedent, for example PRC-6401.")
    bearing: Literal["agrees", "differs_on_a_material_fact", "went_against", "not_alike"] = Field(
        ..., description="agrees when the earlier risk matches this one on the facts that matter and was approved; "
                         "differs_on_a_material_fact when it looks alike but a fact the earlier decision rested on is different "
                         "here; went_against when the earlier risk matches and the request was declined; not_alike when the "
                         "search returned it but it is another kind of risk, for example another occupancy and construction "
                         "class, so it does not bear on this one.")
    note: str = Field("", description="The decision taken, by whom, and the fact that matches or differs, in a sentence. For "
                                      "not_alike, say why it is not alike.")


class ReferralMemo(ForgivingModel):
    referral_needed: Literal["yes", "no"] = Field(
        ..., description="What the system's authority check says: yes when a referral rule applies, no when the authority of the "
                         "asking grade covers the risk. For no, the memo says so and names nobody to refer to.")
    refer_to_grade: Literal["assistant_underwriter", "underwriter", "senior_underwriter", "head_of_underwriting"] | None = Field(
        None, description="The grade the referral goes to, as the authority check gives it. Leave empty when no referral is "
                          "needed: an empty text, none or not needed is read as no grade.")
    forcing_rules: list[str] = Field(default_factory=list, description="The rules that force the referral, by id: the referral rules "
                                     "(for example RF-2) and the guidelines the risk is outside (for example UG-1). Leave empty when "
                                     "no referral is needed.")
    precedents: list[PrecedentRow] = Field(default_factory=list, description="One row for each precedent the memo cites. Leave empty "
                                           "when the search finds none, and say so in the memo.")
    memo: str = Field(..., min_length=1, description="The memo in full: the risk, the terms proposed, the rule that forces the "
                                                     "referral with the figures the system gives, and the precedents. It "
                                                     "recommends no decision.")
    drafted_by: str = DRAFTED_BY


class RenewalReview(ForgivingModel):
    next_step: Literal["ready_for_the_underwriter", "refer_to_the_senior_underwriter", "survey_before_terms", "ask_the_claims_team"] = Field(
        ..., description="ready_for_the_underwriter when no renewal rule applies; refer_to_the_senior_underwriter when the loss "
                         "ratio is above the limit or a change in protections is reported; survey_before_terms when a change of "
                         "occupancy is reported; ask_the_claims_team when two records disagree. When more than one rule applies, the "
                         "order is: ask_the_claims_team first, then refer_to_the_senior_underwriter, then survey_before_terms. "
                         "No value offers or refuses terms.")
    rules_that_apply: list[str] = Field(default_factory=list, description="The renewal rules that apply, by id, for example RN-1. "
                                                                          "Leave empty when none applies.")
    points_to_raise: list[str] = Field(default_factory=list, description="The points the underwriter should raise, one each, with "
                                                                         "the figures and dates the system gives.")
    summary: str = Field(..., min_length=1, description="The review in a few sentences: the expiring terms, the claims of the period "
                                                        "with the loss ratio, and the changes in the risk.")
    drafted_by: str = DRAFTED_BY


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds the underwriting guidelines as numbered rules, the appetite statement by class "
                                  "of business, submissions from brokers, the authority of each underwriter grade with the referral "
                                  "rules, referrals and earlier referred risks, the renewal rules and the renewals that are due. The "
                                  "system does every sum, ratio and comparison. Every save is a draft with who wrote it, a time and "
                                  "a version number. Nothing here accepts, declines, quotes or binds: an underwriter decides.")
    st = ctx.store
    d = lambda: st.data
    today = lambda: ctx.settings.insurer_today.isoformat()
    sub_p = Path(..., description="Submission id, for example SBM-6501.")
    ref_p = Path(..., description="Referral id, for example REF-6601.")
    rnw_p = Path(..., description="Renewal id, for example RNW-6701.")

    def one(name, kind, ident, hint):
        item = d()[name].get(ident)
        if not item:
            raise not_found(kind, ident, hint)
        return item

    sub_or_404 = lambda i: one("uw_submissions", "submission", i, "Use list_submissions to find ids.")
    ref_or_404 = lambda i: one("uw_referrals", "referral", i, "Use list_underwriting_referrals to find ids.")
    rnw_or_404 = lambda i: one("uw_renewals", "renewal", i, "Use list_renewals_due to find ids.")

    def class_or_422(value):
        if value and value not in CLASSES:
            raise conflict(f"{value} is not a class of business here. Use one of: {', '.join(CLASSES)}. Nothing was read.")

    def words_of(text):
        return [w for w in (text or "").lower().replace(",", " ").replace("?", " ").replace(".", " ").split()
                if len(w) > 2 and w not in SEARCH_STOP_WORDS]

    def without(record, field):
        return {k: v for k, v in record.items() if k != field}

    # ------------------------------------------------------------ guidelines and appetite
    @reg(app, "get", "/guidelines", "get_underwriting_guidelines", "Get the underwriting guidelines as numbered rules",
         "Read the underwriting guidelines: a note on how to read them, the three construction classes in words, and every rule with "
         "its id (UG-1 to UG-10), the class of business it is for, a heading, its text with the exact test, and its kind. A rule of "
         "the kind measured has figures and the system measures a submission against it. A rule of the kind for_reading has no "
         "figure and is read against the occupancy or use and the documents. With a class of business only the rules of that class "
         "are returned. It measures nothing itself: get_submission gives a submission measured against these rules.")
    def get_underwriting_guidelines(class_of_business: str | None = Query(None, description=f"Only rules of this class. {CLASS_Q} "
                                                                                           "Leave empty for every rule.")):
        class_or_422(class_of_business)
        rules = [r for r in d()["uw_guidelines"].values() if not class_of_business or r["class_of_business"] == class_of_business]
        return listing(rules, document="Underwriting guidelines", version="6", how_to_read=GUIDELINES_HOW_TO_READ,
                       construction_classes=CONSTRUCTION_CLASSES, class_of_business=class_of_business or "all")

    @reg(app, "get", "/appetite", "get_appetite_statement", "Get the appetite statement, whole or for one class of business",
         "Read the appetite statement: a note on how to read it and its numbered rules. Each rule has an id (for example AP-P3), the "
         "class of business, one position (within, outside or refer) and its text. With a class of business only the rules of that "
         "class are returned, with the general rule AP-G1, which is the usual way to answer a question about one risk. AP-G1 says "
         "which position wins when two rules name one risk: the stricter one (outside over refer over within), and the answer "
         "names both rules. construction_classes says in a sentence what construction class A, B and C each is, for a rule that "
         "speaks of a class. A rule speaks only of what it names. A "
         "risk that no rule names is not within and not outside: the statement is silent on it and an underwriter answers. It "
         "saves nothing and decides nothing.")
    def get_appetite_statement(class_of_business: str | None = Query(None, description=f"Only rules of this class. {CLASS_Q} Leave "
                                                                                      "empty for the whole statement.")):
        class_or_422(class_of_business)
        rules = [r for r in d()["uw_appetite"].values()
                 if not class_of_business or r["class_of_business"] in (class_of_business, ALL_CLASSES)]
        return listing(rules, document="Appetite statement", version="3", how_to_read=APPETITE_HOW_TO_READ,
                       classes_of_business=CLASSES, construction_classes=CONSTRUCTION_CLASSES, class_of_business=class_of_business or "all")

    @reg(app, "get", "/appetite/search", "search_appetite_rules", "Search the appetite statement by words",
         "Find the rules of the appetite statement that name any word of the text, for example fireworks or joinery. Any word may "
         "match, in any order; common words are left out. Each row is a whole rule (id, class of business, position, text) with the "
         "words that matched, and the rows with the most matching words come first. With no text every rule is listed. When no "
         "rule matches, the answer says so: that does not make the risk within or outside. The statement is then silent, and an "
         "underwriter answers. Read the text of a rule before you rely on it: a word can match a rule that is about something else.")
    def search_appetite_rules(text: str | None = Query(None, description="Words that describe the risk, for example scrap yard or "
                                                                         "joinery workshop. Leave empty to list every rule."),
                              class_of_business: str | None = Query(None, description=f"Only rules of this class. {CLASS_Q}")):
        class_or_422(class_of_business)
        words = words_of(text)
        rows = []
        for r in d()["uw_appetite"].values():
            if class_of_business and r["class_of_business"] not in (class_of_business, ALL_CLASSES):
                continue
            hay = f"{r['rule_id']} {r['text']}".lower()
            hits = [w for w in words if w in hay]
            if hits or not words:
                rows.append({**r, "matched_words": hits})
        rows.sort(key=lambda r: -len(r["matched_words"]))
        note = ""
        if words and not rows:
            note = ("No rule of the appetite statement names any of these words. That does not make the risk within or outside: "
                    "the statement is silent on it, and an underwriter answers.")
        return listing(rows, searched_for=text or "", words_used=words, note=note, construction_classes=CONSTRUCTION_CLASSES,
                       when_two_rules_match=d()["uw_appetite"]["AP-G1"]["text"])

    # ------------------------------------------------------------ submissions
    def sub_view(s):
        rules = [r for r in d()["uw_guidelines"].values() if r["class_of_business"] == s["class_of_business"]]
        return {**without(s, "file_drafts"), "guidelines_for_this_class": rules, "measured_against_guidelines": measure_submission(s),
                "drafts_on_file": len(s["file_drafts"]), "read_on": today()}

    @reg(app, "get", "/submissions", "list_submissions", "List the submissions from brokers",
         "List the submissions, whole: id, status, class of business, the broker and the broker's contact, the insured, the date "
         "received, the date cover is wanted from, the risk as the broker's form gives it (for commercial property: location, flood "
         "zone, occupancy, construction class and construction in words, the sums insured for buildings, contents and stock, the "
         "sprinklers field and the alarm; for a motor fleet: base, use, number of vehicles, named drivers and how many are under "
         "25), the requested terms, the claims history (empty when the broker sent none) and the documents as text. Saved "
         "underwriting files are not in the list. For one submission measured against the guidelines, use get_submission.")
    def list_submissions(class_of_business: str | None = Query(None, description=f"Only submissions of this class. {CLASS_Q}")):
        class_or_422(class_of_business)
        return listing([without(s, "file_drafts") for s in d()["uw_submissions"].values()
                        if not class_of_business or s["class_of_business"] == class_of_business])

    @reg(app, "get", "/submissions/{submission_id}", "get_submission", "Get one submission with everything needed to prepare the file",
         "Read one submission with everything an underwriting file needs, in one call: the broker, the insured, the risk as the "
         "form gives it, the requested terms, the claims history (empty when the broker sent none: it is then missing and nothing "
         "is assumed), and every document as text with its id. guidelines_for_this_class gives the rules of the submission's class "
         "of business. measured_against_guidelines is the system's measure: the total sum insured with its working, then one row "
         "for each rule with the result (within, outside, cannot_be_measured or for_reading), the measured value, the limit, the "
         "amount over the limit and a sentence. A value exactly on a limit is within. The measure uses the form's fields only: it "
         "reads no free text, so the documents must still be read for anything that contradicts a field, and the rules for reading "
         "are yours to read. Use the figures given and do not add up or compare yourself. Saved underwriting files are not part of "
         "the submission: drafts_on_file only counts them, and list_underwriting_file_drafts reads them.")
    def get_submission(submission_id: str = sub_p):
        return sub_view(sub_or_404(submission_id))

    @reg(app, "get", "/submissions/{submission_id}/measure", "measure_submission_against_guidelines",
         "Measure a submission against every guideline with figures",
         "Measure one submission against each underwriting guideline of its class of business. The answer gives the total sum "
         "insured with its working (buildings plus contents plus stock) and one row for each rule: the rule id and heading, the "
         "result (within, outside, cannot_be_measured when the submission lacks what the rule needs, or for_reading when the rule "
         "has no figure), the measured value, the limit, the amount over the limit and a sentence. It also lists the rule ids by "
         "result. A value exactly on a limit is within. The measure uses the form's fields only and reads no document. It is the "
         "same measure get_submission carries. It saves nothing and decides nothing.")
    def measure_submission_against_guidelines(submission_id: str = sub_p):
        return {**measure_submission(sub_or_404(submission_id)), "saved": False}

    @reg(app, "get", "/submissions/{submission_id}/drafts", "list_underwriting_file_drafts", "List the underwriting files saved on a submission",
         "Read every underwriting file saved on a submission, each with its version number, who wrote it and when. A saved file is "
         "somebody's preparation for the underwriter, not a fact of the submission and not a decision.")
    def list_underwriting_file_drafts(submission_id: str = sub_p):
        return listing(sub_or_404(submission_id)["file_drafts"], submission_id=submission_id)

    @reg(app, "post", "/submissions/{submission_id}/file", "save_underwriting_file", "Save the underwriting file on a submission (draft)",
         "Save the underwriting file prepared on a submission: one finding for each guideline of its class (within, outside, missing "
         "or cannot_tell, with the evidence), what is missing, where the form and a document contradict each other, the next step "
         "and a summary. The system stores its own measure with it (the rules outside on the figures and the rules it could not "
         "measure) and the answer returns it. This is a draft for the underwriter: stored with who wrote it, a time and a version "
         "number, earlier versions kept. It accepts nothing, declines nothing, quotes nothing and contacts nobody, and it changes "
         "nothing else. Refused with 409, and nothing saved, when a finding names a rule that is not a guideline of the "
         "submission's class or names a rule twice, or when the next step is ask_the_broker and no question is given.")
    def save_underwriting_file(body: UnderwritingFile, submission_id: str = sub_p):
        s = sub_or_404(submission_id)
        known = [r["rule_id"] for r in d()["uw_guidelines"].values() if r["class_of_business"] == s["class_of_business"]]
        sent = [f.rule_id.strip().upper() for f in body.findings]
        unknown = [x for x in sent if x not in known]
        if unknown or len(sent) != len(set(sent)):
            raise conflict(f"The guidelines for {submission_id} ({s['class_of_business']}) are {', '.join(known)}, each to be given "
                           f"once. Not one of them or given twice: {', '.join(unknown) or 'a rule given twice'}. Nothing was saved.")
        if body.next_step == "ask_the_broker" and not body.question_for_the_broker.strip():
            raise conflict("The next step ask_the_broker needs the question for the broker, in a sentence. Nothing was saved.")
        measure = measure_submission(s)
        payload = {**body.model_dump(exclude={"drafted_by", "findings"}),
                   "findings": [{**f.model_dump(), "rule_id": f.rule_id.strip().upper()} for f in body.findings],
                   "measured_by_the_system": {k: measure[k] for k in ("within", "outside", "cannot_be_measured", "for_reading")}}
        v = st.add_draft(s, "file_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v,
                "message": f"The underwriting file is saved on {submission_id} as a draft. The submission itself is unchanged."}

    # ------------------------------------------------------------ authority, referrals and precedents
    @reg(app, "get", "/authority-levels", "get_authority_levels", "Get the authority of each underwriter grade and the referral rules",
         "Read the authority levels and the referral rules. grades has one row for each grade, lowest first (assistant underwriter, "
         "underwriter, senior underwriter, head of underwriting): the most total sum insured at one location, the most vehicles in "
         "a fleet, the most discount from the technical premium as a percentage, whether the grade may decide a risk outside a "
         "guideline, and a sentence. referral_rules gives RF-1 to RF-3 with their text. Where several rules apply, a risk goes to "
         "the highest grade any of them names. It measures no risk: get_underwriting_referral gives a referral measured against "
         "these rules.")
    def get_authority_levels():
        return {"document": "Underwriting authority levels", "version": "4", "how_to_read": AUTHORITY_HOW_TO_READ,
                "grades": [d()["uw_authority_levels"][g] for g in GRADE_ORDER],
                "referral_rules": list(d()["uw_referral_rules"].values()), "currency": "USD"}

    def ref_view(r):
        return {**without(r, "memo_drafts"), "authority_check": check_authority(r),
                "drafts_on_file": len(r["memo_drafts"]), "read_on": today()}

    @reg(app, "get", "/referrals", "list_underwriting_referrals", "List the referrals raised by underwriters",
         "List the referrals, whole: id, status, the date raised, the underwriter who asks with name and grade, the class of "
         "business, the insured, the submission it came from where there is one, the risk (occupancy or use, construction class, "
         "total sum insured, sprinklers, number of vehicles), the proposed terms (technical premium, proposed premium, deductible, "
         "conditions), the guidelines the risk is outside as the underwriter recorded them, and the underwriter's note. Saved memos "
         "are not in the list. For one referral with the authority check, use get_underwriting_referral.")
    def list_underwriting_referrals():
        return listing([without(r, "memo_drafts") for r in d()["uw_referrals"].values()])

    @reg(app, "get", "/referrals/{referral_id}", "get_underwriting_referral", "Get one referral with the authority check",
         "Read one referral with what a memo needs, in one call: the underwriter who asks with name and grade, the insured, the "
         "risk, the proposed terms, the guidelines the risk is outside, the underwriter's note, and authority_check. "
         "authority_check is the system's answer: one row for each referral rule (RF-1 size, RF-2 outside a guideline, RF-3 "
         "discount) with whether it applies, the measured value, the authority of the asking grade, the grade needed and a "
         "sentence; then referral_needed (true or false), refer_to_grade, forced_by (the rule ids), the discount as a percentage of "
         "the technical premium worked out by the system, and a sentence. When referral_needed is false the asking underwriter may "
         "decide alone and the memo says so. Use this answer and do not compare figures yourself. Precedents are not part of the "
         "referral: search_referral_precedents finds them. Saved memos are not part of the referral either: drafts_on_file only "
         "counts them, and list_referral_memo_drafts reads them.")
    def get_underwriting_referral(referral_id: str = ref_p):
        return ref_view(ref_or_404(referral_id))

    @reg(app, "get", "/referrals/{referral_id}/authority", "check_referral_authority", "Say which rule forces a referral and to which grade",
         "Measure one referral against the referral rules and the authority of the grade that asks. The answer gives one row for "
         "each rule (RF-1 size above the authority, RF-2 a risk outside a guideline, RF-3 a discount above the authority) with "
         "whether it applies, the measured value, the authority of the asking grade, the grade needed and a sentence; then "
         "referral_needed, refer_to_grade (the highest grade any applying rule names), forced_by, the discount as a percentage "
         "worked out by the system, and a sentence. A value exactly on an authority needs no referral. It is the same check "
         "get_underwriting_referral carries. It saves nothing and decides nothing.")
    def check_referral_authority(referral_id: str = ref_p):
        return {**check_authority(ref_or_404(referral_id)), "saved": False}

    @reg(app, "get", "/precedents", "search_referral_precedents", "Search earlier referred risks and the decisions taken",
         "Find earlier referred risks. Each row is whole: id (for example PRC-6401), the date decided, the class of business, the "
         "insured, the occupancy, the construction class, the total sum insured, whether there were sprinklers, the referral rules "
         "that forced the referral (forced_by) and the guidelines the risk was outside, the terms proposed, the decision (approved, "
         "approved_with_conditions or declined), the conditions, who decided with name and grade, and a summary that says what the "
         "decision rested on. Filter by class of business, by a rule id (a referral rule such as RF-3 or a guideline such as UG-1), "
         "by words, or any mix; any word may match. With no filter every precedent is listed. When nothing matches the answer says "
         "so: the memo then states that no precedent was found. A precedent is a past decision on another risk, not a rule: "
         "compare its facts with the referral before you call it alike, above all the fact its decision rested on.")
    def search_referral_precedents(
            text: str | None = Query(None, description="Words from the occupancy, the insured or the summary, for example showroom "
                                                       "or grain. Leave empty to filter by class or rule only."),
            class_of_business: str | None = Query(None, description=f"Only precedents of this class. {CLASS_Q}"),
            rule_id: str | None = Query(None, description="Only precedents forced by this referral rule or outside this guideline, "
                                                          "for example RF-3 or UG-1.")):
        class_or_422(class_of_business)
        words = [w for w in (text or "").lower().replace(",", " ").split() if len(w) > 2]
        rule = (rule_id or "").strip().upper()
        rows = []
        for p in d()["uw_precedents"].values():
            if class_of_business and p["class_of_business"] != class_of_business:
                continue
            if rule and rule not in p["forced_by"] and rule not in p["outside_guidelines"]:
                continue
            hay = f"{p['precedent_id']} {p['insured']} {p['occupancy']} {p['summary']} {p['conditions']}".lower()
            if not words or any(w in hay for w in words):
                rows.append(p)
        note = "" if rows else "No earlier referred risk matches. The memo says that no precedent was found."
        return listing(rows, searched_for=text or "", class_of_business=class_of_business or "all", rule_id=rule, note=note)

    @reg(app, "get", "/referrals/{referral_id}/drafts", "list_referral_memo_drafts", "List the memos saved on a referral",
         "Read every referral memo saved on a referral, each with its version number, who wrote it and when. A saved memo is "
         "somebody's draft for the deciding underwriter, not a fact of the referral and not a decision.")
    def list_referral_memo_drafts(referral_id: str = ref_p):
        return listing(ref_or_404(referral_id)["memo_drafts"], referral_id=referral_id)

    @reg(app, "post", "/referrals/{referral_id}/memo", "save_referral_memo", "Save a referral memo (draft)",
         "Save the referral memo: whether a referral is needed, the grade it goes to, the rules that force it, one row for each "
         "precedent cited (agrees, differs_on_a_material_fact or went_against, with a note), and the memo in full. The system "
         "stores its own authority check with it (referral_needed, refer_to_grade, forced_by) and the answer returns it. This is a "
         "draft for the deciding underwriter: stored with who wrote it, a time and a version number, earlier versions kept. It "
         "refers nothing, decides nothing and contacts nobody, and it changes nothing else. Refused with 409, and nothing saved, "
         "when a forcing rule is not a referral rule or a guideline, when a precedent id is not a precedent the insurer holds, or "
         "when no referral is needed and a grade to refer to is given.")
    def save_referral_memo(body: ReferralMemo, referral_id: str = ref_p):
        r = ref_or_404(referral_id)
        known = set(d()["uw_referral_rules"]) | set(d()["uw_guidelines"])
        rules = [x.strip().upper() for x in body.forcing_rules]
        unknown = [x for x in rules if x not in known]
        if unknown:
            raise conflict(f"Not a referral rule (RF-1 to RF-3) or a guideline (UG-1 to UG-10): {', '.join(unknown)}. Nothing was saved.")
        missing = [p.precedent_id for p in body.precedents if p.precedent_id.strip().upper() not in d()["uw_precedents"]]
        if missing:
            raise conflict(f"Not a precedent the insurer holds: {', '.join(missing)}. Use search_referral_precedents to find ids, "
                           "or leave the precedents empty when none was found. Nothing was saved.")
        if body.referral_needed == "no" and body.refer_to_grade:
            raise conflict("When no referral is needed there is no grade to refer to. Leave refer_to_grade empty. Nothing was saved.")
        check = check_authority(r)
        payload = {**body.model_dump(exclude={"drafted_by", "precedents", "forcing_rules"}), "forcing_rules": rules,
                   "precedents": [{**p.model_dump(), "precedent_id": p.precedent_id.strip().upper()} for p in body.precedents],
                   "authority_check_by_the_system": {k: check[k] for k in ("referral_needed", "refer_to_grade", "forced_by",
                                                                           "discount_percent")}}
        v = st.add_draft(r, "memo_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v,
                "message": f"The memo is saved on {referral_id} as a draft. Nothing is referred and the referral itself is unchanged."}

    # ------------------------------------------------------------ renewals
    @reg(app, "get", "/renewal-rules", "get_renewal_rules", "Get the renewal rules",
         "Read the renewal rules RN-1 to RN-5, each with its id, heading and text, and a note on how to read them: the loss ratio "
         "above which a referral is needed, what a change of occupancy and a change in protections need, how an open claim's "
         "reserve is shown, and what happens when two records disagree. It measures no renewal: get_renewal gives a renewal "
         "measured against these rules.")
    def get_renewal_rules():
        return listing(list(d()["uw_renewal_rules"].values()), document="Renewal rules", version="2",
                       how_to_read=RENEWAL_RULES_HOW_TO_READ)

    def rnw_brief(r):
        return {**without(r, "review_drafts"), **renewal_expiry(r, d(), today())}

    @reg(app, "get", "/renewals", "list_renewals_due", "List the policies whose period ends within a number of days",
         "List the renewals whose policy period ends within a window, soonest first. The window is a number of days from the "
         "insurer date, 60 when none is given. Each row is whole: the renewal id, status, the policy id and where the policy is "
         "held (this system for a commercial policy, the policy system for a home or motor policy), the insured, the class of "
         "business, the period, the days until the period ends worked out by the system, and the changes in the risk reported "
         "since the period started. Saved reviews are not in the list. For one renewal with its claims, loss ratio and rules, use "
         "get_renewal.")
    def list_renewals_due(within_days: int = Query(60, ge=1, le=366, description="The window in days from the insurer date, for "
                                                                                  "example 30. The period must end within it.")):
        rows = [rnw_brief(r) for r in d()["uw_renewals"].values()]
        rows = sorted((r for r in rows if 0 <= r["days_until_the_period_ends"] <= within_days),
                      key=lambda r: r["days_until_the_period_ends"])
        return listing(rows, within_days=within_days, counted_from=today())

    @reg(app, "get", "/renewals/{renewal_id}", "get_renewal", "Get one renewal with expiring terms, claims, loss ratio and changes",
         "Read one renewal with everything a review needs, in one call. expiring_terms gives the policy, the insured, what is "
         "insured, the total sum insured, the deductible, the period, the premium for the period and the days until the period "
         "ends. claims_of_the_period lists every claim booked to the policy with its date of loss, cause, status (open, closed or "
         "declined), the amount paid, the outstanding reserve, the two added up, and whether the date of loss is inside the "
         "period. totals gives the number of claims, the open ones, paid, reserves, the cost in all, the loss ratio on payments "
         "alone and the loss ratio with reserves, both as a percentage of the premium, with the working. record_disagreements "
         "lists each place where the claims record and the policy record disagree on a date, with both versions and the days "
         "between; totals_leaving_out_the_disputed_claims then gives the same totals without those claims. changes_reported lists "
         "the changes in the risk since the period started, each with its date, kind (occupancy, protections or other) and text. "
         "rules has one row for each renewal rule with whether it applies (true, false, or depends_on_the_disagreement) and a "
         "sentence. Use these figures and do not add up, divide or count days yourself. A home or motor policy and its claims are "
         "read from the policy and claims systems as they stand. Saved reviews are not part of the renewal: drafts_on_file only "
         "counts them, and list_renewal_review_drafts reads them. It offers no terms.")
    def get_renewal(renewal_id: str = rnw_p):
        r = rnw_or_404(renewal_id)
        pack = renewal_pack(r, d(), today())
        return {**without(without(r, "review_drafts"), "changes_reported"), **pack,
                "drafts_on_file": len(r["review_drafts"]), "read_on": today()}

    @reg(app, "get", "/renewals/{renewal_id}/drafts", "list_renewal_review_drafts", "List the reviews saved on a renewal",
         "Read every renewal review saved on a renewal, each with its version number, who wrote it and when. A saved review is "
         "somebody's preparation for the underwriter, not a fact of the renewal and not an offer of terms.")
    def list_renewal_review_drafts(renewal_id: str = rnw_p):
        return listing(rnw_or_404(renewal_id)["review_drafts"], renewal_id=renewal_id)

    @reg(app, "post", "/renewals/{renewal_id}/review", "save_renewal_review", "Save a renewal review (draft)",
         "Save the review of a renewal: the next step, the renewal rules that apply, the points to raise and a summary. The system "
         "stores its own figures with it (claims, paid, reserves, the loss ratios, the rules that apply) and the answer returns "
         "them. This is a draft for the underwriter: stored with who wrote it, a time and a version number, earlier versions "
         "kept. It offers no terms, renews nothing and contacts nobody, and it changes nothing else: not the policy, not a claim. "
         "Refused with 409, and nothing saved, when a rule named is not a renewal rule (RN-1 to RN-5), or when the next step is "
         "ready_for_the_underwriter and rules that apply are named.")
    def save_renewal_review(body: RenewalReview, renewal_id: str = rnw_p):
        r = rnw_or_404(renewal_id)
        rules = [x.strip().upper() for x in body.rules_that_apply]
        unknown = [x for x in rules if x not in d()["uw_renewal_rules"]]
        if unknown:
            raise conflict(f"Not a renewal rule (RN-1 to RN-5): {', '.join(unknown)}. Nothing was saved.")
        if body.next_step == "ready_for_the_underwriter" and rules:
            raise conflict("The next step ready_for_the_underwriter is for a renewal to which no rule applies. Leave the rules "
                           "empty, or choose the next step the rule asks for. Nothing was saved.")
        pack = renewal_pack(r, d(), today())
        figures = {**{k: v for k, v in pack["totals"].items() if k != "working"},
                   "rules_that_apply": pack["rules_that_apply"],
                   "rules_that_depend_on_the_disagreement": pack["rules_that_depend_on_the_disagreement"]}
        payload = {**body.model_dump(exclude={"drafted_by", "rules_that_apply"}), "rules_that_apply": rules,
                   "figures_worked_out_by_the_system": figures}
        v = st.add_draft(r, "review_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v,
                "message": f"The review is saved on {renewal_id} as a draft. No terms are offered and the policy is unchanged."}

    return app
