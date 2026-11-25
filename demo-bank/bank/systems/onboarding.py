"""Onboarding: account opening applications and periodic reviews of existing customers (KYC)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..store import now_iso

KEY = "onboarding"
TITLE = "Onboarding and customer reviews"
LINE = "Account opening applications with their documents, the bank's requirements, and periodic reviews of existing customers."


class Detail(BaseModel):
    field: str = Field(..., description="The field read from a document, for example full_name or date_of_birth.")
    value: str = Field(..., description="The value as written in the document.")
    source_document_id: str = Field(..., description="The document it was read from, for example OND-1001-01.")


class Mismatch(BaseModel):
    field: str = Field(..., description="The field that differs between the form and a document.")
    form_value: str = Field(..., description="The value on the application form.")
    document_value: str = Field(..., description="The value in the document.")
    source_document_id: str = Field(..., description="The document that has the different value.")
    note: str = Field("", description="Why it matters or does not matter under the bank's requirements.")


class ScreeningResult(BaseModel):
    screened_name: str = Field(..., description="The name that was screened with screen_name.")
    outcome: Literal["no_match", "possible_match", "strong_match"] = Field(..., description="The result of reading the screen_name hits.")
    top_entry_id: str = Field("", description="The best hit's watchlist entry id, for example WL-9001. Empty if there was no hit.")
    top_score: int = Field(0, ge=0, le=100, description="The best hit's score from 0 to 100. 0 if there was no hit.")
    note: str = Field("", description="What agrees and what differs between the applicant and the entry.")


class ChainLink(BaseModel):
    owner: str = Field(..., description="Name of the owner as written in a document.")
    owner_type: Literal["person", "company"] = Field(..., description="Whether the owner is a person or a company.")
    percent: float = Field(..., ge=0, le=100, description="Percent of the shares held.")
    country: str = Field("", description="Country of the owner as written in the document. Empty if no document gives it.")
    held_through: str = Field("", description="The company through which the share is held. Empty for a direct owner.")
    source_document_id: str = Field("", description="The document that shows this holding. Empty if none does.")
    gap: bool = Field(False, description="True if this link cannot be traced further because no document shows who stands behind it.")
    gap_note: str = Field("", description="What is missing. Never fill a gap with a guess.")


class FileDraft(BaseModel):
    details_extracted: list[Detail] = Field(default_factory=list, description="The details read from the documents.")
    mismatches: list[Mismatch] = Field(default_factory=list, description="Every difference between the form and a document.")
    screening_result: ScreeningResult = Field(..., description="The screening result for the applicant (for a business, the company).")
    ownership_chain: list[ChainLink] = Field(default_factory=list, description="For a business: every owner down to the people behind it.")
    ownership_gaps: list[str] = Field(default_factory=list, description="For a business: every gap in the ownership chain, one per item. Empty if there is none.")
    missing_items: list[str] = Field(default_factory=list, description="Documents or facts that are missing, out of date or need to come from the applicant.")
    recommendation: Literal["approve", "decline", "ask_applicant", "refer_to_compliance"] = Field(
        ..., description="approve, decline, ask_applicant, or refer_to_compliance (a strong watchlist match).")
    summary: str = Field("", description="The file in plain sentences.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class DecisionBody(BaseModel):
    decision: Literal["approve", "decline", "ask_applicant"] = Field(
        ..., description="approve: open the account. decline: do not open it. ask_applicant: wait for the applicant to send what is missing.")
    decided_by: str = Field(..., min_length=1, description="Name of the person who decides.")
    note: str = Field("", description="Optional note with the reason.")
    message_to_applicant: str = Field("", description="Optional text of what the applicant is told. For ask_applicant, say exactly what is needed.")


class FieldChange(BaseModel):
    field: str = Field(..., description="The profile field that changed, for example address or occupation or owners.")
    old_value: str = Field(..., description="The value the bank holds today.")
    new_value: str = Field(..., description="The new value.")
    source_document_id: str = Field(..., description="The fresh document that shows the new value, for example KYD-1002-01.")


class ProfileDraft(BaseModel):
    changes: list[FieldChange] = Field(default_factory=list, description="Every changed field. Empty if nothing changed.")
    unchanged_fields: list[str] = Field(default_factory=list, description="Fields that were checked and are the same.")
    proposed_risk_rating: Literal["standard", "medium", "high"] = Field(..., description="The risk rating you propose after the review.")
    rating_reason: str = Field(..., min_length=1, description="Why that rating, in plain sentences.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class CompleteBody(BaseModel):
    signed_off_by: str = Field(..., min_length=1, description="Name of the person who signs off the review.")
    rating_change_approved_by: str = Field("", description="Name of the person who approves a change of risk rating. Needed if the latest draft proposes a rating different from the current one.")
    note: str = Field("", description="Optional note.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds account opening applications with their documents as extracted text, the bank's "
                                  "requirements for each kind of customer, and periodic reviews of existing customers.")
    st = ctx.store
    d = lambda: st.data
    app_p = Path(..., description="Application id, for example ONB-1001.")
    rev_p = Path(..., description="Review id, for example KYR-1001.")
    doc_p = Path(..., description="Document id, as listed on the application or the review.")

    def app_or_404(i):
        a = d()["onb_applications"].get(i)
        if not a:
            raise not_found("application", i, "Use list_onboarding_applications to find ids.")
        return a

    def rev_or_404(i):
        r = d()["kyc_reviews"].get(i)
        if not r:
            raise not_found("review", i, "Use list_kyc_reviews to find ids.")
        return r

    def bank_date():
        return ctx.settings.bank_today.isoformat()

    def with_age(doc):
        """A document with its own date and its age in whole days at the bank's date (0 on the day it is dated)."""
        dated = doc.get("document_date", "")
        age = (ctx.settings.bank_today - date.fromisoformat(dated)).days if dated else None
        return {**doc, "document_date": dated, "age_days_at_bank_date": age}

    def doc_summaries(coll, key):
        keys = ("document_id", "doc_type", "title", "received", "document_date", "age_days_at_bank_date")
        return [{k: with_age(x)[k] for k in keys} for x in d()[coll].get(key, {}).values()]

    # ------------------------------------------------------------ account opening

    @reg(app, "get", "/applications", "list_onboarding_applications", "List account opening applications",
         "List account opening applications: application_id, kind (individual or business), status (received, awaiting_applicant, approved or "
         "declined), applicant name, product, received date and how many documents arrived. Filter by status or kind. Applications with "
         "status received need a file and a decision.")
    def list_onboarding_applications(status: str = Query("", description="Only applications with this status. Leave empty for all."),
                                     kind: str = Query("", description="Only this kind: individual or business. Leave empty for all.")):
        if kind not in ("", "individual", "business"):
            raise HTTPException(422, "kind must be individual or business.")
        rows = [{"application_id": a["application_id"], "kind": a["kind"], "status": a["status"], "applicant": a["applicant"],
                 "product": a["product"], "received": a["received"], "documents_received": len(d()["onb_documents"].get(a["application_id"], {}))}
                for a in d()["onb_applications"].values() if (not status or a["status"] == status) and (not kind or a["kind"] == kind)]
        rows.sort(key=lambda r: (r["received"], r["application_id"]), reverse=True)
        return listing(rows, read_on=bank_date())

    @reg(app, "get", "/applications/{application_id}", "get_onboarding_application", "Get one application in full",
         "Read one application: the details exactly as typed on the form, the documents received (read each with "
         "get_onboarding_document), a checklist of the documents the bank requires for this kind of customer marked received or missing, "
         "the checks the bank requires, any earlier saved files and the decision if one was made. read_on is the bank's date today, the date of "
         "this reading: count the age of a document to it, never to any other clock. Each document listed carries document_date (the date the "
         "document itself carries: issued, dated or signed) and age_days_at_bank_date, its age in whole days at the bank's date. Compare the form "
         "with every document yourself: nothing here has done it for you.")
    def get_onboarding_application(application_id: str = app_p):
        a = app_or_404(application_id)
        got = {x["doc_type"]: x["document_id"] for x in d()["onb_documents"].get(application_id, {}).values()}
        req = d()["onb_requirements"]["kinds"][a["kind"]]
        checklist = [{"type": r["type"], "label": r["label"], "received": r["type"] in got, "document_id": got.get(r["type"], "")}
                     for r in req["documents"]]
        return {**a, "read_on": bank_date(), "documents_received": doc_summaries("onb_documents", application_id), "required_documents": checklist,
                "required_checks": req["checks"], "bank_rules": d()["onb_requirements"]["bank_rules"]}

    @reg(app, "get", "/applications/{application_id}/documents", "list_onboarding_documents", "List an application's documents",
         "List the documents received for an application: document_id, type, title, received date, document_date (the date the document "
         "carries) and age_days_at_bank_date (its age in whole days at the bank's date, read_on). Read the text of one with get_onboarding_document.")
    def list_onboarding_documents(application_id: str = app_p):
        app_or_404(application_id)
        return listing(doc_summaries("onb_documents", application_id), application_id=application_id, read_on=bank_date())

    @reg(app, "get", "/applications/{application_id}/documents/{document_id}", "get_onboarding_document", "Read one application document",
         "Read one document as extracted text: an identity document, a proof of address, a company registry extract, constitutional documents or "
         "an ownership declaration. The text is what the scanner read. It is not compared with the form. Also gives document_date (the date the "
         "document carries), age_days_at_bank_date (its age in whole days at the bank's date) and read_on (the bank's date today).")
    def get_onboarding_document(application_id: str = app_p, document_id: str = doc_p):
        app_or_404(application_id)
        doc = d()["onb_documents"].get(application_id, {}).get(document_id)
        if not doc:
            raise not_found("document", document_id, "Use list_onboarding_documents to find ids.")
        return {**with_age(doc), "read_on": bank_date()}

    @reg(app, "get", "/requirements", "get_onboarding_requirements", "Get the bank's account opening requirements",
         "Read what the bank requires: for an individual and for a business, the documents and the checks; the bank's rules (the age of a proof "
         "of address, the 25 percent ownership threshold, the higher-risk country list, screening); the differences that matter and the ones that "
         "do not; and what each decision means.")
    def get_onboarding_requirements():
        return d()["onb_requirements"]

    @reg(app, "post", "/applications/{application_id}/file", "save_onboarding_file", "Save the file on an application (draft)",
         "Save your file on an application: the details extracted from the documents, each mismatch with the form, the screening result, for a "
         "business the ownership chain with every gap listed, the missing items and a recommendation (approve, decline, ask_applicant or "
         "refer_to_compliance). This is a draft: stored with who wrote it, a timestamp and a version number, earlier versions kept. The application "
         "stays as it is. Refused with 409 if the application is already approved or declined.")
    def save_onboarding_file(body: FileDraft, application_id: str = app_p):
        a = app_or_404(application_id)
        if a["status"] in ("approved", "declined"):
            raise conflict(f"Application {application_id} is already {a['status']}. Nothing was changed.")
        docs = d()["onb_documents"].get(application_id, {})
        refs = [x.source_document_id for x in body.details_extracted + body.mismatches + body.ownership_chain if x.source_document_id]
        for ref in refs:
            if ref not in docs:
                raise not_found("document on this application", ref, "Use list_onboarding_documents to find ids.")
        v = st.add_draft(a, "files", {k: val for k, val in body.model_dump().items() if k != "drafted_by"}, body.drafted_by)
        return {"applied": True, "kind": "draft", "application_status": a["status"], "draft": v}

    @reg(app, "post", "/applications/{application_id}/decision", "decide_onboarding_application", "Decide an application (change)",
         "Decide an application: approve (open the account), decline, or ask_applicant (wait for what the applicant must send). This is a change "
         "and needs the name of the person who decides. Refused with 409 if the application is already approved or declined, or already waiting "
         "for the applicant. A strong watchlist match is not decided here: it is referred to Compliance.")
    def decide_onboarding_application(body: DecisionBody, application_id: str = app_p):
        a = app_or_404(application_id)
        with st.lock:
            if a["status"] in ("approved", "declined"):
                raise conflict(f"Application {application_id} is already {a['status']}. Nothing was changed.")
            if body.decision == "ask_applicant" and a["status"] == "awaiting_applicant":
                raise conflict(f"Application {application_id} is already waiting for the applicant. Nothing was changed.")
            a["status"] = {"approve": "approved", "decline": "declined", "ask_applicant": "awaiting_applicant"}[body.decision]
            a["decision"] = {"decision": body.decision, "decided_by": body.decided_by, "note": body.note,
                             "message_to_applicant": body.message_to_applicant, "decided_at": now_iso(), "file_version": len(a["files"])}
            st.save()
        return {"applied": True, "kind": "change", "application_id": application_id, "status": a["status"], "decision": a["decision"]}

    # ------------------------------------------------------------ periodic reviews

    @reg(app, "get", "/reviews", "list_kyc_reviews", "List periodic reviews of customers",
         "List periodic reviews (know your customer) of existing customers: review_id, customer, status (open or completed), the date of the "
         "last review, the date this one was due and the current risk rating. Open reviews need a refreshed profile.")
    def list_kyc_reviews(status: str = Query("", description="Only reviews with this status: open or completed. Leave empty for all.")):
        rows = [{"review_id": r["review_id"], "customer_id": r["customer_id"], "customer_name": d()["customers"][r["customer_id"]]["name"],
                 "status": r["status"], "last_review_date": r["last_review_date"], "due_date": r["due_date"], "risk_rating": r["risk_rating"]}
                for r in d()["kyc_reviews"].values() if not status or r["status"] == status]
        rows.sort(key=lambda r: (r["due_date"], r["review_id"]))
        return listing(rows, read_on=bank_date())

    @reg(app, "get", "/reviews/{review_id}", "get_kyc_review", "Get one periodic review in full",
         "Read one review: the customer, the profile the bank holds today (what is on file), the fresh documents received for this review (read each "
         "with get_kyc_review_document), the date of the last review, the current risk rating, saved profile drafts and the completion if the "
         "review is closed. read_on is the bank's date today, the date of this reading; each fresh document carries document_date and "
         "age_days_at_bank_date, its age in whole days at the bank's date. Compare the held profile with every fresh document yourself.")
    def get_kyc_review(review_id: str = rev_p):
        r = rev_or_404(review_id)
        c = d()["customers"][r["customer_id"]]
        return {**r, "read_on": bank_date(), "customer": {k: c[k] for k in ("customer_id", "type", "name", "segment", "status", "customer_since")},
                "fresh_documents": doc_summaries("kyc_documents", review_id), "higher_risk_countries": ["Kharnovia (QP)"],
                "bank_rules": d()["onb_requirements"]["bank_rules"]}

    @reg(app, "get", "/reviews/{review_id}/documents/{document_id}", "get_kyc_review_document", "Read one document of a review",
         "Read one fresh document received for a periodic review, as extracted text, with document_date (the date the document carries), "
         "age_days_at_bank_date (its age in whole days at the bank's date) and read_on (the bank's date today).")
    def get_kyc_review_document(review_id: str = rev_p, document_id: str = doc_p):
        rev_or_404(review_id)
        doc = d()["kyc_documents"].get(review_id, {}).get(document_id)
        if not doc:
            raise not_found("document", document_id, "Fresh documents are listed on the review.")
        return {**with_age(doc), "read_on": bank_date()}

    @reg(app, "post", "/reviews/{review_id}/profile-draft", "save_refreshed_profile", "Save a refreshed profile (draft)",
         "Save your refreshed profile for a review: every changed field with the old value, the new value and the document it came from, the "
         "fields that are the same, and a proposed risk rating with the reason. This is a draft: stored with who wrote it, a timestamp and a "
         "version number, earlier versions kept. The customer's record is not changed. Refused with 409 if the review is already completed.")
    def save_refreshed_profile(body: ProfileDraft, review_id: str = rev_p):
        r = rev_or_404(review_id)
        if r["status"] != "open":
            raise conflict(f"Review {review_id} is already {r['status']}. Nothing was changed.")
        docs = d()["kyc_documents"].get(review_id, {})
        for ch in body.changes:
            if ch.source_document_id not in docs:
                raise not_found("document on this review", ch.source_document_id, "Fresh documents are listed on the review.")
        v = st.add_draft(r, "profile_drafts", {k: val for k, val in body.model_dump().items() if k != "drafted_by"}, body.drafted_by)
        return {"applied": True, "kind": "draft", "review_status": r["status"], "draft": v}

    @reg(app, "post", "/reviews/{review_id}/complete", "complete_kyc_review", "Complete a periodic review (change)",
         "Complete a review using the latest saved profile draft: the customer's address is updated if the draft changes it, the risk rating is "
         "set to the proposed one, and the next review is set one year ahead. This is a change and needs the name of the person who signs off. If "
         "the proposed risk rating differs from the current one it also needs rating_change_approved_by. Refused with 409 if there is no draft, "
         "if the approval for a rating change is missing, or if the review is already completed.")
    def complete_kyc_review(body: CompleteBody, review_id: str = rev_p):
        r = rev_or_404(review_id)
        today = ctx.settings.bank_today
        with st.lock:
            if r["status"] != "open":
                raise conflict(f"Review {review_id} is already {r['status']}. Nothing was changed.")
            if not r["profile_drafts"]:
                raise conflict(f"Review {review_id} has no saved profile yet. Save one with save_refreshed_profile first. Nothing was changed.")
            draft = r["profile_drafts"][-1]
            cust = d()["customers"][r["customer_id"]]
            old = cust["risk_rating"].split()[0].lower()
            changed = draft["proposed_risk_rating"] != old
            if changed and not body.rating_change_approved_by.strip():
                raise conflict(f"The proposed risk rating ({draft['proposed_risk_rating']}) differs from the current one ({old}). "
                               "A change of risk rating needs rating_change_approved_by. Nothing was changed.")
            for ch in draft["changes"]:
                if ch["field"] == "address":
                    cust["address"] = ch["new_value"]
            if changed:
                cust["risk_rating"] = draft["proposed_risk_rating"]
            cust["kyc_review_due"] = (today + timedelta(days=365)).isoformat()
            r["status"] = "completed"
            r["last_review_date"] = today.isoformat()
            r["risk_rating"] = cust["risk_rating"]
            r["completion"] = {"signed_off_by": body.signed_off_by, "rating_change_approved_by": body.rating_change_approved_by,
                               "old_risk_rating": old, "new_risk_rating": draft["proposed_risk_rating"], "rating_changed": changed,
                               "note": body.note, "completed_at": now_iso(), "draft_version": draft["version"]}
            st.save()
        return {"applied": True, "kind": "change", "review_id": review_id, "status": r["status"], "completion": r["completion"]}

    return app
