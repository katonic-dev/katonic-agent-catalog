"""Lending: loan applications, documents, policy and approved loans."""

from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg

KEY = "lending"
TITLE = "Lending"
LINE = "Loan applications, their documents, the credit policy and approved loans."


SOURCE_HELP = ("Where the figure was read. Either a document id of this application, as listed by list_application_documents, for "
               "example DOC-8203, or the word FORM when the figure is written on the application form itself, or the word RECORD "
               "when it is on the application record (the amount, the term, the indicative rate or the indicative instalment).")


class Figure(BaseModel):
    name: str = Field(..., description="Figure name, for example average_monthly_turnover. Free text.")
    value: str = Field(..., description="Figure value with its unit, for example 51400 USD.")
    source_document_id: str = Field(..., description=SOURCE_HELP)


class MissingItems(BaseModel):
    missing_items: list[str] = Field(default_factory=list, description="Required document types that are missing. Each is a type from the "
                                     "application's document checklist. For personal_loan: identity_document, payslips_3_months, "
                                     "bank_statements_3_months, employment_letter. For business_loan_small: company_registration, "
                                     "financial_statements, bank_statements_6_months, tax_return, ownership_declaration, directors_identity. "
                                     "Leave the list empty if nothing is missing.")
    extracted_figures: list[Figure] = Field(default_factory=list, description="Figures read from the documents and from the application form. "
                                            "Each has a name, a value with its unit and a source: a document id or FORM.")
    notes: str = Field("", description="Anything else, for example a figure that differs between sources.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class Ratio(BaseModel):
    name: str = Field(..., description="Ratio name as the policy writes it: debt_to_income (personal_loan) or current_ratio, "
                                       "debt_to_equity, debt_service_cover (business_loan_small). get_credit_policy lists them.")
    value: float = Field(..., description="Computed value, for example 3.31.")
    threshold: str = Field("", description="Policy threshold as written in the policy, for example at least 1.25.")
    calculation: str = Field("", description="How it was computed, with the figures used.")


class FigureSource(BaseModel):
    figure: str = Field(..., description="Figure name, for example latest_year_ebitda. Free text.")
    value: str = Field(..., description="Value used, with its unit, for example 258000 USD.")
    source_document_id: str = Field(..., description=SOURCE_HELP)


class CreditMemo(BaseModel):
    memo_text: str = Field(..., min_length=1, description="The memo, in plain sentences.")
    ratios: list[Ratio] = Field(default_factory=list, description="Ratios the policy names, with values.")
    figure_sources: list[FigureSource] = Field(..., min_length=1, description="The source of every figure used. Each has a figure "
                                               "name, the value used and a source: a document id or FORM for the application form.")
    recommendation: Literal["approve", "decline", "refer"] = Field("refer", description="The recommendation for the credit committee: "
                                                                   "approve, decline or refer (a person must look closer). The default is refer.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class Difference(BaseModel):
    item: str = Field(..., description="What differs, for example interest margin.")
    approved_value: str = Field(..., description="Value in the approved terms.")
    contract_value: str = Field(..., description="Value in the contract.")
    document_id: str = Field(..., description="Contract document id.")
    clause: str = Field("", description="Clause number in the contract.")


class Differences(BaseModel):
    differences: list[Difference] = Field(..., description="Every place where the contract differs from the approved terms.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds loan applications, their documents as extracted text, the credit policy and approved loans.")
    st = ctx.store
    d = lambda: st.data
    app_p = Path(..., description="Application id, for example LAP-8001.")
    loan_p = Path(..., description="Loan id, for example LN-9001.")

    def app_or_404(i):
        a = d()["applications"].get(i)
        if not a:
            raise not_found("loan application", i, "Use list_loan_applications to find ids.")
        return a

    def loan_or_404(i):
        if i not in d()["approved_terms"]:
            raise not_found("approved loan", i, "Only approved loans with documents are held here, for example LN-9001.")

    @reg(app, "get", "/applications", "list_loan_applications", "List loan applications",
         "List loan applications: id, status, applicant, product (personal_loan or business_loan_small), amount, currency, term and "
         "received date.")
    def list_loan_applications(status: str | None = Query(None, description="Only applications with this status, for example received.")):
        keys = ("application_id", "status", "customer_id", "applicant", "product", "amount", "currency", "term_months", "purpose", "received")
        return listing([{k: a[k] for k in keys} for a in d()["applications"].values() if not status or a["status"] == status])

    @reg(app, "get", "/applications/{application_id}", "get_loan_application", "Get one loan application",
         "Read one application: applicant, product, amount, term, purpose, the figures the applicant wrote on the form, and the "
         "checklist of documents the product requires, each marked received (with the document id) or missing. Earlier drafts are included.")
    def get_loan_application(application_id: str = app_p):
        a = app_or_404(application_id)
        have = {x["doc_type"]: x["document_id"] for x in d()["application_docs"].get(application_id, {}).values()}
        req = d()["credit_policy"]["products"][a["product"]]["required_documents"]
        checklist = [{"type": r["type"], "label": r["label"], "received": r["type"] in have, "document_id": have.get(r["type"])}
                     for r in req]
        return {**a, "policy_id": d()["credit_policy"]["products"][a["product"]]["policy_id"], "document_checklist": checklist}

    @reg(app, "get", "/applications/{application_id}/documents", "list_application_documents", "List an application's documents",
         "List the documents received for an application: document_id, type, title and received date. The text is read with "
         "get_application_document.")
    def list_application_documents(application_id: str = app_p):
        app_or_404(application_id)
        rows = [{k: x[k] for k in ("document_id", "doc_type", "title", "received")}
                for x in d()["application_docs"].get(application_id, {}).values()]
        return listing(rows, application_id=application_id)

    @reg(app, "get", "/applications/{application_id}/documents/{document_id}", "get_application_document", "Read one application document",
         "Read one document as extracted text: payslips, bank statements and financial statements come as text tables.")
    def get_application_document(application_id: str = app_p,
                                 document_id: str = Path(..., description="Document id, for example DOC-8203.")):
        app_or_404(application_id)
        doc = d()["application_docs"].get(application_id, {}).get(document_id)
        if not doc:
            raise not_found("document", document_id, "Use list_application_documents to find ids.")
        return doc

    @reg(app, "get", "/policy", "get_credit_policy", "Get the credit policy",
         "Read the lending policy: for each product the required documents and the ratios the policy names, with their definition "
         "and threshold.")
    def get_credit_policy():
        return d()["credit_policy"]

    @reg(app, "post", "/applications/{application_id}/missing-items", "save_missing_items", "Save missing items and figures (draft)",
         "Save the list of missing documents and the figures you extracted. Missing items are document types from the application's "
         "checklist (for example tax_return). Each figure has a name, a value with its unit and a source: a document id of this "
         "application (for example DOC-8203) or FORM when the figure is on the application form. This is a draft: stored with who wrote "
         "it, a timestamp and a version number, earlier versions kept. Nothing is sent to the applicant.")
    def save_missing_items(body: MissingItems, application_id: str = app_p):
        a = app_or_404(application_id)
        v = st.add_draft(a, "missing_items_drafts", {"missing_items": body.missing_items,
                                                     "extracted_figures": [f.model_dump() for f in body.extracted_figures],
                                                     "notes": body.notes}, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    @reg(app, "post", "/applications/{application_id}/credit-memo", "save_credit_memo", "Save a credit memo (draft)",
         "Save a credit memo with its ratios and the source of every figure. A ratio name is one the policy lists (debt_to_income, "
         "current_ratio, debt_to_equity or debt_service_cover). The source of a figure is a document id of this application (for "
         "example DOC-8302), FORM when the figure is on the application form itself, or RECORD when it is on the application record. The recommendation is approve, decline or "
         "refer. This is a draft: stored with who wrote it, a timestamp and a version number, earlier versions kept. It does not "
         "decide the application.")
    def save_credit_memo(body: CreditMemo, application_id: str = app_p):
        a = app_or_404(application_id)
        v = st.add_draft(a, "credit_memo_drafts", {"memo_text": body.memo_text, "ratios": [r.model_dump() for r in body.ratios],
                                                   "figure_sources": [f.model_dump() for f in body.figure_sources],
                                                   "recommendation": body.recommendation}, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    @reg(app, "get", "/loans/{loan_id}/approved-terms", "get_approved_terms", "Get the approved terms of a loan",
         "Read the terms the credit committee approved: amount, term, rate margin, repayment, fees, covenants, security, "
         "governing law and the approval reference. Compare them with the signed contract.")
    def get_approved_terms(loan_id: str = loan_p):
        loan_or_404(loan_id)
        return d()["approved_terms"][loan_id]

    @reg(app, "get", "/loans/{loan_id}/documents", "list_loan_documents", "List a loan's documents",
         "List the documents of an approved loan: id, type and title (facility agreement, schedules, resolutions).")
    def list_loan_documents(loan_id: str = loan_p):
        loan_or_404(loan_id)
        rows = [{k: x[k] for k in ("document_id", "doc_type", "title")} for x in d()["loan_docs"].get(loan_id, {}).values()]
        return listing(rows, loan_id=loan_id)

    @reg(app, "get", "/loans/{loan_id}/documents/{document_id}", "get_loan_document", "Read one loan document",
         "Read one loan document as extracted text, with numbered clauses.")
    def get_loan_document(loan_id: str = loan_p, document_id: str = Path(..., description="Document id, for example DOC-9101.")):
        loan_or_404(loan_id)
        doc = d()["loan_docs"].get(loan_id, {}).get(document_id)
        if not doc:
            raise not_found("document", document_id, "Use list_loan_documents to find ids.")
        return doc

    @reg(app, "post", "/loans/{loan_id}/document-differences", "save_document_differences", "Save contract differences (draft)",
         "Save the places where the signed contract differs from the approved terms, each with both values, the document and the clause. "
         "This is a draft: stored with who wrote it, a timestamp and a version number, earlier versions kept. Refused with 409 when the "
         "loan's funds were already released (funds_released_on in the approved terms): its document check is closed.")
    def save_document_differences(body: Differences, loan_id: str = loan_p):
        loan_or_404(loan_id)
        released = d()["approved_terms"][loan_id].get("funds_released_on")
        if released:
            day = date.fromisoformat(released)
            month = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")[day.month - 1]
            raise conflict(f"The funds of {loan_id} were released on {day.day} {month} {day.year}. Its document check is closed, so no "
                           "draft of differences can be saved. Nothing was saved.")
        item = d()["document_differences"].setdefault(loan_id, {"loan_id": loan_id})
        v = st.add_draft(item, "drafts", {"differences": [x.model_dump() for x in body.differences]}, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    return app
