"""Franchise, version 1.4: the franchisees with their restaurants, and questions franchisees have asked."""

from __future__ import annotations

from fastapi import Path, Query

from ..common import Ctx, listing, make_subapp, not_found, reg
from ..seed_franchise import AGREEMENT_NOTE, MANUAL, STANDARDS

KEY = "franchise"
TITLE = "Franchise"
LINE = ("The three franchisees of Rowanmere Kitchen with their restaurants, and seventeen questions franchisees have asked, "
        "for trying an agent that answers from the franchise operations manual.")

FRANCHISEE_FIELDS = ("franchisee_id, company, franchisee_since (the year), restaurants, operations_manual, brand_standards, "
                     "agreement_note and franchise_team_email")
DOCUMENTS_NOTE = (f"This system does not hold the wording of the {MANUAL} or of the {STANDARDS}. An answer to a question "
                  "comes from those two documents. " + AGREEMENT_NOTE)


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds the franchisees of Rowanmere Kitchen, the restaurants each one runs, "
                                  "and questions franchisees have asked. It only reads: it has no operation that writes. "
                                  "It does not hold the franchise operations manual, the brand standards or any franchise "
                                  "agreement. A question about a franchise agreement goes to the franchise team.")
    st = ctx.store
    d = lambda: st.data

    def franchisee_or_404(i):
        f = d()["franchisees"].get(i)
        if not f:
            raise not_found("franchisee", i, "Use list_franchisees to find franchisee ids.")
        return f

    @reg(app, "get", "/franchisees", "list_franchisees", "List the franchisees",
         "List the companies that run franchised restaurants, sorted by id. Each row has franchisee_id, company, "
         "franchisee_since (the year), restaurants (the site ids) and questions (how many questions the franchisee has "
         "asked). Read one with get_franchisee.")
    def list_franchisees():
        rows = [{"franchisee_id": f["franchisee_id"], "company": f["company"], "franchisee_since": f["franchisee_since"],
                 "restaurants": [r["site_id"] for r in f["restaurants"]],
                 "questions": sum(1 for q in d()["franchise_questions"].values() if q["franchisee_id"] == f["franchisee_id"])}
                for f in d()["franchisees"].values()]
        return listing(sorted(rows, key=lambda f: f["franchisee_id"]))

    @reg(app, "get", "/franchisees/{franchisee_id}", "get_franchisee", "Get one franchisee with its restaurants",
         f"Read one franchisee: {FRANCHISEE_FIELDS}. Each restaurant has site_id, name, town, street, area and area_manager, "
         "the same as in the stores system. operations_manual and brand_standards name the two documents a franchisee's "
         "question is answered from, with their versions. agreement_note says that the franchise agreement is not held "
         "here and where a question about it goes. Find the id with list_franchisees, for example FR-01.")
    def get_franchisee(franchisee_id: str = Path(..., description="Franchisee id, for example FR-01.")):
        return franchisee_or_404(franchisee_id)

    @reg(app, "get", "/questions", "list_franchisee_questions", "List questions franchisees have asked",
         "List the questions franchisees have asked, oldest first. Each row has question_id, franchisee_id, company, "
         "asked_on and question (the franchisee's own words). The answer also has documents_note: this system holds no "
         "answer and no wording of the manual or the brand standards. Some questions are answered by a section of the "
         "manual or by a brand standard, some are answered by neither, and some are about the franchise agreement itself. "
         "The list does not say which. The filter franchisee_id is optional, and an unknown id is refused with 404.")
    def list_franchisee_questions(franchisee_id: str | None = Query(None, description="Only the questions of this franchisee, for example FR-02.")):
        if franchisee_id:
            franchisee_or_404(franchisee_id)
        rows = [q for q in d()["franchise_questions"].values() if not franchisee_id or q["franchisee_id"] == franchisee_id]
        return listing(sorted(rows, key=lambda q: (q["asked_on"], q["question_id"])), documents_note=DOCUMENTS_NOTE)

    @reg(app, "get", "/questions/{question_id}", "get_franchisee_question", "Get one question a franchisee asked",
         "Read one question: question_id, franchisee_id, company, asked_on, question (the franchisee's own words), "
         "restaurants (the site ids the franchisee runs) and documents_note. It holds no answer. Find the id with "
         "list_franchisee_questions, for example FQ-2611-01.")
    def get_franchisee_question(question_id: str = Path(..., description="Question id, for example FQ-2611-01.")):
        q = d()["franchise_questions"].get(question_id)
        if not q:
            raise not_found("question", question_id, "Use list_franchisee_questions to find question ids.")
        own = d()["franchisees"][q["franchisee_id"]]
        return {**q, "restaurants": [r["site_id"] for r in own["restaurants"]], "documents_note": DOCUMENTS_NOTE}

    return app
