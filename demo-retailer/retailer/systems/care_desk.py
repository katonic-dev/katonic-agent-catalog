"""Customer care, version 1.2: the operations for customer tickets, complaints and public reviews.

They are added to the care system by care.build, so they share its OpenAPI document and its MCP address.
"""

from __future__ import annotations

import re
from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, not_found, reg
from ..seed_care_desk import COMPLAINTS_PROCEDURE, help_articles
from ..store import now_iso

DATE_RE = r"^\d{4}-\d{2}-\d{2}$"
CLASSIFICATIONS = Literal["safety_or_legal", "repeat_contact", "service_failure", "policy_disagreement"]
TICKET_FIELDS = ("ticket_id, received_on, channel (email, web form or chat), customer_id, customer_name, customer_email, "
                 "order_number (empty when the message names no order), subject, message (the customer's own words) and "
                 "status (open or replied)")
ARTICLES = {a["article_id"]: a for a in help_articles()}


class TicketReply(BaseModel):
    answer_status: Literal["answered_from_articles", "no_article_answers"] = Field(
        ..., description="answered_from_articles: a help article answers the customer's question. no_article_answers: no "
                         "help article answers it.")
    reply: str = Field(..., min_length=1, description="The reply to the customer, as a draft, in plain sentences. A member of "
                                                      "the care team sends it.")
    articles_cited: list[str] = Field(default_factory=list, description="The ids of the help articles the reply rests on, for "
                                      "example HA-05. At least one when answer_status is answered_from_articles. Empty "
                                      "when it is no_article_answers.")
    proposed_next_step: Literal["send_reply", "pass_to_a_colleague"] = Field(
        ..., description="send_reply: the reply is ready for a member of the care team to send. pass_to_a_colleague: a "
                         "colleague must answer, because no article does.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class SendBody(BaseModel):
    sent_by: str = Field(..., min_length=1, description="The person who sends it. Free text.")
    note: str = Field("", description="Optional note kept with the record.")


class Classification(BaseModel):
    classification: CLASSIFICATIONS = Field(..., description="The class of the complaint under the complaints procedure.")
    procedure_section: str = Field(..., min_length=1, description="The section of the procedure the class rests on, for "
                                                                 "example 2.3.")
    response_due: str = Field(..., pattern=DATE_RE, description="The day the response is due, as YYYY-MM-DD: the day the "
                              "complaint was received plus the days the procedure gives for the class.")
    what_happened: str = Field(..., min_length=1, description="What the complaint, the order and the contact history show, in "
                               "plain sentences with dates. It says so when the records do not explain something.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class ComplaintResponse(BaseModel):
    response: str = Field(..., min_length=1, description="The response to the customer, as a draft. It admits no fault and "
                                                         "offers no money. The Customer Relations Lead approves it.")
    proposed_next_step: Literal["send_response", "pass_to_the_customer_relations_lead"] = Field(
        ..., description="send_response: ready for the Lead to approve and send. pass_to_the_customer_relations_lead: the "
                         "Lead must read the complaint first. A complaint classified safety_or_legal always takes this value.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class ReviewReply(BaseModel):
    action: Literal["reply", "mark_for_a_person"] = Field(
        ..., description="reply: a reply is drafted. mark_for_a_person: the review describes a safety or legal matter, so no "
                         "reply is drafted and a person reads it first.")
    reply: str = Field("", description="The reply in the brand's voice, as a draft. Leave it empty when the action is "
                                       "mark_for_a_person.")
    reason: str = Field("", description="Why the review is marked for a person, in one plain sentence. Needed when the "
                                        "action is mark_for_a_person.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class PublishBody(BaseModel):
    published_by: str = Field(..., min_length=1, description="The person who posts the reply. Free text.")
    note: str = Field("", description="Optional note kept with the record.")


def words_of(text: str) -> set:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 2}


def ranked(rows: list, q: str | None, text_of) -> list:
    """Rows that share a word with the question, best first. Every row when there is no question."""
    if not q or not words_of(q):
        return rows
    wanted = words_of(q)
    scored = [(len(wanted & words_of(text_of(r))), r) for r in rows]
    return [r for score, r in sorted(scored, key=lambda x: -x[0]) if score > 0]


def add_desk(app, ctx: Ctx) -> None:
    st = ctx.store
    d = lambda: st.data

    def ticket_or_404(i):
        x = d()["tickets"].get(i)
        if not x:
            raise not_found("customer ticket", i, "Use list_customer_tickets to find ticket ids.")
        return x

    def complaint_or_404(i):
        x = d()["complaints"].get(i)
        if not x:
            raise not_found("complaint", i, "Use list_complaints to find complaint ids.")
        return x

    def review_or_404(i):
        x = d()["public_reviews"].get(i)
        if not x:
            raise not_found("public review", i, "Use list_public_reviews to find review ids.")
        return x

    def marked(r: dict) -> bool:
        return bool(r["reply_drafts"]) and r["reply_drafts"][-1]["action"] == "mark_for_a_person"

    ticket_p = Path(..., description="Ticket id, for example CT-2611-004.")
    complaint_p = Path(..., description="Complaint id, for example CM-2611-02.")
    review_p = Path(..., description="Review id, for example PR-2611-03.")

    # ------------------------------------------------------------ tickets
    @reg(app, "get", "/tickets", "list_customer_tickets", "List customer tickets",
         f"List the customer tickets of the online shop, oldest first. Each row has {TICKET_FIELDS}, and reply_drafts (how "
         "many are saved). The filter status is optional. Read one with get_customer_ticket.")
    def list_customer_tickets(status: Literal["open", "replied"] | None = Query(None, description="Only tickets with this status.")):
        rows = [{**{k: v for k, v in t.items() if k not in ("reply_drafts", "reply_sent")}, "reply_drafts": len(t["reply_drafts"])}
                for t in d()["tickets"].values() if not status or t["status"] == status]
        return listing(sorted(rows, key=lambda t: (t["received_on"], t["ticket_id"])))

    @reg(app, "get", "/tickets/{ticket_id}", "get_customer_ticket", "Get one customer ticket",
         f"Read one customer ticket: {TICKET_FIELDS}; reply_drafts (every saved reply, each a version) and reply_sent (who "
         "sent the reply and when, empty until it is sent). Look for the article that answers it with search_help_articles.")
    def get_customer_ticket(ticket_id: str = ticket_p):
        return ticket_or_404(ticket_id)

    @reg(app, "get", "/help-articles", "search_help_articles", "Search the help articles",
         "Search the online shop's help articles. Each row has article_id, title, category and body (the whole article). q is "
         "a few words of the customer's question: the articles that share a word with it come back, the best match first. "
         "Without q, all twelve articles come back in order. An empty answer means no article shares a word with the "
         "question: try other words, or read all twelve, before saying that no article answers it.")
    def search_help_articles(q: str | None = Query(None, description="A few words of the question, for example refund arrive.")):
        return listing(ranked(help_articles(), q, lambda a: f"{a['title']} {a['category']} {a['body']}"))

    @reg(app, "get", "/past-cases", "search_past_cases", "Search past cases",
         "Search closed cases of the care team. Each row has case_id, closed_on, question (what the customer asked, with no "
         "name), what_was_done and article_id (the help article the answer rested on, empty when there was none). q is a few "
         "words: the cases that share a word with it come back, the best match first. Without q, every case comes back, newest "
         "first. A past case shows how the team answered before. It is not a rule: the help articles and the policies are.")
    def search_past_cases(q: str | None = Query(None, description="A few words, for example opened return.")):
        rows = sorted(d()["past_cases"].values(), key=lambda c: c["closed_on"], reverse=True)
        return listing(ranked(rows, q, lambda c: f"{c['question']} {c['what_was_done']}"))

    @reg(app, "post", "/tickets/{ticket_id}/reply", "save_ticket_reply", "Save a reply to a customer ticket (draft)",
         "Save a reply to one customer ticket, as a draft. It sends nothing and changes no status. Each call is kept as a new "
         "version with who wrote it and when. Send answer_status, reply, articles_cited, proposed_next_step and drafted_by. "
         "answer_status is answered_from_articles or no_article_answers. proposed_next_step is send_reply or "
         "pass_to_a_colleague. An article id that does not exist is refused with 404. answered_from_articles with no article "
         "cited, and no_article_answers with an article cited or with send_reply, are refused with 422. A member of the care "
         "team sends every reply. Returns the saved version.")
    def save_ticket_reply(body: TicketReply, ticket_id: str = ticket_p):
        t = ticket_or_404(ticket_id)
        for a in body.articles_cited:
            if a not in ARTICLES:
                raise not_found("help article", a, "Nothing was saved. Use search_help_articles to find article ids.")
        if body.answer_status == "answered_from_articles" and not body.articles_cited:
            raise HTTPException(422, "answered_from_articles needs at least one article in articles_cited. Nothing was saved.")
        if body.answer_status == "no_article_answers" and (body.articles_cited or body.proposed_next_step != "pass_to_a_colleague"):
            raise HTTPException(422, "no_article_answers goes with an empty articles_cited and the proposed_next_step "
                                     "pass_to_a_colleague. Nothing was saved.")
        payload = {"answer_status": body.answer_status, "reply": body.reply, "articles_cited": list(body.articles_cited),
                   "proposed_next_step": body.proposed_next_step}
        v = st.add_draft(t, "reply_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "ticket_status": t["status"]}

    @reg(app, "post", "/tickets/{ticket_id}/send", "send_ticket_reply", "Send the reply to a customer ticket (change)",
         "Send the latest saved reply of one ticket to the customer. This is a change: the status becomes replied. Needs "
         "sent_by. Refused with 409 until a reply has been saved with save_ticket_reply, and when the ticket is already "
         "replied.")
    def send_ticket_reply(body: SendBody, ticket_id: str = ticket_p):
        t = ticket_or_404(ticket_id)
        with st.lock:
            if t["status"] == "replied":
                raise conflict(f"Ticket {ticket_id} was already replied to by {t['reply_sent']['sent_by']}. Nothing was changed.")
            if not t["reply_drafts"]:
                raise conflict(f"No reply is saved for ticket {ticket_id}. Nothing was changed. Use save_ticket_reply first.")
            t["status"] = "replied"
            t["reply_sent"] = {"sent_by": body.sent_by, "sent_at": now_iso(), "to": t["customer_email"],
                               "version": t["reply_drafts"][-1]["version"], "note": body.note}
            st.save()
        return {"applied": True, "kind": "change", "status": "replied", "ticket": t}

    # ------------------------------------------------------------ complaints
    @reg(app, "get", "/complaints", "list_complaints", "List complaints",
         "List complaints, oldest first. Each row has complaint_id, received_on, channel, customer_name, order_number, "
         "subject, earlier_contacts (how many contacts are in the history), status (open or responded), classifications and "
         "response_drafts (how many of each are saved). The filter status is optional. Read one with get_complaint.")
    def list_complaints(status: Literal["open", "responded"] | None = Query(None, description="Only complaints with this status.")):
        rows = [{"complaint_id": c["complaint_id"], "received_on": c["received_on"], "channel": c["channel"],
                 "customer_name": c["customer_name"], "order_number": c["order_number"], "subject": c["subject"],
                 "earlier_contacts": len(c["contact_history"]), "status": c["status"],
                 "classifications": len(c["classifications"]), "response_drafts": len(c["response_drafts"])}
                for c in d()["complaints"].values() if not status or c["status"] == status]
        return listing(sorted(rows, key=lambda c: (c["received_on"], c["complaint_id"])))

    @reg(app, "get", "/complaints/{complaint_id}", "get_complaint", "Get one complaint with its contact history",
         "Read one complaint: complaint_id, received_on, channel, customer_id, customer_name, customer_email, order_number, "
         "subject, message (the customer's own words), contact_history (the earlier contacts, oldest first, each with date, "
         "channel, summary and about_the_same_matter), status, classifications and response_drafts (every saved version), "
         "response_sent and retailer_date. The complaint itself is not in contact_history. Read the order in the orders "
         "system, and the classes and deadlines with get_complaints_procedure.")
    def get_complaint(complaint_id: str = complaint_p):
        c = complaint_or_404(complaint_id)
        history = sorted(c["contact_history"], key=lambda h: h["date"])
        return {**c, "contact_history": history, "retailer_date": st.settings.retailer_today.isoformat()}

    @reg(app, "get", "/complaints-procedure", "get_complaints_procedure", "Get the complaints procedure",
         "Read the complaints procedure: document, version, owner, classes (each with class, classification, "
         "response_due_days, applies_when and section), order_when_more_than_one_fits, sections (each with number, title and "
         "clauses, each clause with its number and text), what_the_procedure_does_not_decide and text (the whole procedure "
         "as plain text). The response is due the day the complaint was received plus response_due_days, in calendar days.")
    def get_complaints_procedure():
        return COMPLAINTS_PROCEDURE

    @reg(app, "post", "/complaints/{complaint_id}/classification", "save_complaint_classification",
         "Save the classification of a complaint (draft)",
         "Save the classification of one complaint with what happened, as a draft. This is the log entry. It changes no "
         "status. Each call is kept as a new version with who wrote it and when. Send classification, procedure_section, "
         "response_due, what_happened and drafted_by. classification is safety_or_legal, repeat_contact, service_failure or "
         "policy_disagreement. response_due is a date as YYYY-MM-DD and is refused with 422 when it is before the day the "
         "complaint was received. Returns the saved version.")
    def save_complaint_classification(body: Classification, complaint_id: str = complaint_p):
        c = complaint_or_404(complaint_id)
        if body.response_due < c["received_on"]:
            raise HTTPException(422, f"response_due {body.response_due} is before the day the complaint was received, "
                                     f"{c['received_on']}. Nothing was saved.")
        payload = {"classification": body.classification, "procedure_section": body.procedure_section,
                   "response_due": body.response_due, "what_happened": body.what_happened}
        v = st.add_draft(c, "classifications", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "complaint_status": c["status"]}

    @reg(app, "post", "/complaints/{complaint_id}/response", "save_complaint_response", "Save a response to a complaint (draft)",
         "Save a response to one complaint, as a draft. It sends nothing and changes no status. Each call is kept as a new "
         "version with who wrote it and when. Send response, proposed_next_step and drafted_by. proposed_next_step is "
         "send_response or pass_to_the_customer_relations_lead. Refused with 409 until a classification has been saved with "
         "save_complaint_classification. Refused with 422 when the latest saved classification is safety_or_legal and "
         "proposed_next_step is send_response. The Customer Relations Lead approves every response. Returns the saved version.")
    def save_complaint_response(body: ComplaintResponse, complaint_id: str = complaint_p):
        c = complaint_or_404(complaint_id)
        if not c["classifications"]:
            raise conflict(f"No classification is saved for complaint {complaint_id}. Nothing was saved. Use "
                           "save_complaint_classification first.")
        if c["classifications"][-1]["classification"] == "safety_or_legal" and body.proposed_next_step == "send_response":
            raise HTTPException(422, "The complaint is classified safety_or_legal, so proposed_next_step must be "
                                     "pass_to_the_customer_relations_lead. Nothing was saved.")
        payload = {"response": body.response, "proposed_next_step": body.proposed_next_step}
        v = st.add_draft(c, "response_drafts", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "complaint_status": c["status"]}

    @reg(app, "post", "/complaints/{complaint_id}/send", "send_complaint_response", "Send the response to a complaint (change)",
         "Send the latest saved response of one complaint to the customer. This is a change: the status becomes responded. "
         "Needs sent_by. Refused with 409 until a response has been saved with save_complaint_response, and when the "
         "complaint is already responded.")
    def send_complaint_response(body: SendBody, complaint_id: str = complaint_p):
        c = complaint_or_404(complaint_id)
        with st.lock:
            if c["status"] == "responded":
                raise conflict(f"Complaint {complaint_id} was already responded to by {c['response_sent']['sent_by']}. "
                               "Nothing was changed.")
            if not c["response_drafts"]:
                raise conflict(f"No response is saved for complaint {complaint_id}. Nothing was changed. Use "
                               "save_complaint_response first.")
            c["status"] = "responded"
            c["response_sent"] = {"sent_by": body.sent_by, "sent_at": now_iso(), "to": c["customer_email"],
                                  "version": c["response_drafts"][-1]["version"], "note": body.note}
            st.save()
        return {"applied": True, "kind": "change", "status": "responded", "complaint": c}

    # ------------------------------------------------------------ public reviews
    @reg(app, "get", "/reviews", "list_public_reviews", "List public reviews",
         "List public reviews of the stores and the online shop, oldest first. Each row has review_id, posted_on, review_site, "
         "about (a store's site id, or online shop), rating (1 to 5), reviewer_display_name, text, status (unanswered or "
         "reply_published), reply_drafts (how many are saved) and marked_for_a_person (true when the latest saved version "
         "marks the review for a person). Filters are optional: status and max_rating. Read one with get_public_review.")
    def list_public_reviews(status: Literal["unanswered", "reply_published"] | None = Query(None, description="Only reviews with this status."),
                            max_rating: int | None = Query(None, ge=1, le=5, description="Only reviews with this rating or lower, 1 to 5.")):
        rows = [{**{k: v for k, v in r.items() if k not in ("reply_drafts", "reply_published")}, "reply_drafts": len(r["reply_drafts"]),
                 "marked_for_a_person": marked(r)}
                for r in d()["public_reviews"].values()
                if (not status or r["status"] == status) and (max_rating is None or r["rating"] <= max_rating)]
        return listing(sorted(rows, key=lambda r: (r["posted_on"], r["review_id"])))

    @reg(app, "get", "/reviews/{review_id}", "get_public_review", "Get one public review",
         "Read one public review: review_id, posted_on, review_site, about, rating, reviewer_display_name (the name the "
         "reviewer chose to show), text (the reviewer's own words), status, reply_drafts (every saved version), "
         "marked_for_a_person (true when the latest saved version marks the review for a person) and reply_published (who "
         "posted the reply and when, empty until it is posted).")
    def get_public_review(review_id: str = review_p):
        r = review_or_404(review_id)
        return {**r, "marked_for_a_person": marked(r)}

    @reg(app, "post", "/reviews/{review_id}/reply", "save_review_reply", "Save a reply to a public review (draft)",
         "Save what is proposed for one public review, as a draft. It posts nothing. Each call is kept as a new version with "
         "who wrote it and when. Send action, reply, reason and drafted_by. action is reply or mark_for_a_person. With "
         "reply, the reply text is needed. With mark_for_a_person, the review describes a safety or legal matter: reply "
         "must be empty and reason is needed, and the review then shows marked_for_a_person true so that a person reads it "
         "first. Anything else is refused with 422. A review whose reply is already published is refused with 409. A "
         "person posts every reply. Returns the saved version.")
    def save_review_reply(body: ReviewReply, review_id: str = review_p):
        r = review_or_404(review_id)
        if r["status"] == "reply_published":
            raise conflict(f"The reply to review {review_id} is already published. Nothing was saved.")
        if body.action == "reply" and not body.reply.strip():
            raise HTTPException(422, "The action reply needs the reply text in reply. Nothing was saved.")
        if body.action == "mark_for_a_person" and (body.reply.strip() or not body.reason.strip()):
            raise HTTPException(422, "The action mark_for_a_person goes with an empty reply and a reason. Nothing was saved.")
        v = st.add_draft(r, "reply_drafts", {"action": body.action, "reply": body.reply, "reason": body.reason}, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "review_status": r["status"], "marked_for_a_person": marked(r)}

    @reg(app, "post", "/reviews/{review_id}/publish", "publish_review_reply", "Publish the reply to a public review (change)",
         "Post the latest saved reply of one review on the review site. This is a change: the status becomes "
         "reply_published. Needs published_by. Refused with 409 until a reply has been saved with save_review_reply, when "
         "the latest saved version marks the review for a person and so holds no reply, and when a reply is already "
         "published.")
    def publish_review_reply(body: PublishBody, review_id: str = review_p):
        r = review_or_404(review_id)
        with st.lock:
            if r["status"] == "reply_published":
                raise conflict(f"The reply to review {review_id} was already published by "
                               f"{r['reply_published']['published_by']}. Nothing was changed.")
            if not r["reply_drafts"]:
                raise conflict(f"No reply is saved for review {review_id}. Nothing was changed. Use save_review_reply first.")
            if r["reply_drafts"][-1]["action"] != "reply":
                raise conflict(f"Review {review_id} is marked for a person and holds no reply to publish. Nothing was changed.")
            r["status"] = "reply_published"
            r["reply_published"] = {"published_by": body.published_by, "published_at": now_iso(),
                                    "version": r["reply_drafts"][-1]["version"], "note": body.note}
            st.save()
        return {"applied": True, "kind": "change", "status": "reply_published", "review": r}
