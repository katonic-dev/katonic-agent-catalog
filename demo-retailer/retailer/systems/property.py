"""Property, version 1.1: store and restaurant leases, and the summaries saved on them."""

from __future__ import annotations

from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, listing, make_subapp, not_found, reg

KEY = "property"
TITLE = "Property"
LINE = "The leases of the group's stores and restaurants, each with its full text in numbered clauses, and the summaries saved on them."

DATE_RE = r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$"
CLAUSE_RE = r"^\d{1,2}\.\d{1,2}$"
ROW_FIELDS = ("lease_id, site_id, site_name, town, landlord, tenant, term_start, term_end, annual_rent in US dollars before "
              "value added tax, and currency")


class TermPart(BaseModel):
    start_date: str = Field(..., pattern=DATE_RE, description="The first day of the term, as YYYY-MM-DD.")
    end_date: str = Field(..., pattern=DATE_RE, description="The last day of the term, as YYYY-MM-DD.")
    clause: str = Field(..., pattern=CLAUSE_RE, description="The number of the clause that says so, for example 2.1.")


class RentPart(BaseModel):
    annual_rent: float = Field(..., gt=0, description="The rent for a year in US dollars, before value added tax, as a number.")
    clause: str = Field(..., pattern=CLAUSE_RE, description="The number of the clause that says so, for example 3.1.")


class ReviewPart(BaseModel):
    review_date: str = Field(..., pattern=DATE_RE, description="One rent review date, as YYYY-MM-DD.")
    basis: Literal["upward_only", "upward_or_downward", "fixed_increase", "index_linked"] = Field(
        ..., description="How the rent is reviewed on that date. upward_only: to the market rent, and it cannot go down. "
                         "upward_or_downward: to the market rent, higher or lower. fixed_increase: by a fixed percentage. "
                         "index_linked: in line with a price index.")
    clause: str = Field(..., pattern=CLAUSE_RE, description="The number of the clause that gives the basis, for example 4.2.")


class BreakPart(BaseModel):
    break_date: str = Field(..., pattern=DATE_RE, description="The date on which the lease may be ended early, as YYYY-MM-DD.")
    who_may_break: Literal["tenant", "landlord", "either"] = Field(..., description="Who may end the lease on that date.")
    notice_months: int = Field(..., ge=1, le=36, description="The least number of months of written notice, as a whole number.")
    notice_by: str = Field(..., pattern=DATE_RE, description="The last day on which the notice can be given: the break date "
                                                             "less the months of notice, as YYYY-MM-DD.")
    clause: str = Field(..., pattern=CLAUSE_RE, description="The number of the clause that gives the right to break, for example 5.1.")


class RepairPart(BaseModel):
    party: Literal["tenant", "landlord"] = Field(..., description="Who has the duty.")
    duty: str = Field(..., min_length=1, description="What that party keeps in repair, in the lease's own words, for example the roof.")
    clause: str = Field(..., pattern=CLAUSE_RE, description="The number of the clause that says so, for example 6.1.")


class OtherPoint(BaseModel):
    point: str = Field(..., min_length=1, description="One more point from the lease in a plain sentence, for example the service "
                                                      "charge, the rule on assignment or a notice period.")
    clause: str = Field(..., pattern=CLAUSE_RE, description="The number of the clause that says so.")


class LeaseSummary(BaseModel):
    term: TermPart = Field(..., description="The term: start_date, end_date and clause.")
    rent: RentPart = Field(..., description="The rent: annual_rent and clause.")
    rent_reviews: list[ReviewPart] = Field(default_factory=list, description="One entry for each rent review date, with its "
                                           "basis and clause. Leave empty only when the lease has no rent review.")
    break_options: list[BreakPart] = Field(default_factory=list, description="One entry for each break date. Leave the list "
                                           "empty when the lease has no break clause.")
    repair_duties: list[RepairPart] = Field(..., min_length=1, description="Who repairs what, one entry for each duty.")
    other_points: list[OtherPoint] = Field(default_factory=list, description="Other points worth a reader's attention. Optional.")
    summary: str = Field("", description="A short summary in plain sentences. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds the leases of some of the group's stores and restaurants. Each lease is "
                                  "served with its full text and its numbered clauses. Saving a summary is a draft: the "
                                  "property team checks it against the lease.")
    st = ctx.store
    d = lambda: st.data
    served = ("lease_id", "site_id", "site_name", "town", "landlord", "tenant", "term_start", "term_end", "annual_rent", "currency")

    def lease_or_404(i):
        x = d()["leases"].get(i)
        if not x:
            raise not_found("lease", i, "Use list_leases to find lease ids.")
        return x

    lease_p = Path(..., description="Lease id, for example LS-2001.")

    @reg(app, "get", "/leases", "list_leases", "List leases",
         f"List the leases, sorted by lease id. Each row has {ROW_FIELDS}. The answer also has retailer_date, the date the "
         "retailer counts as today. The filter site_id gives the lease of one store or restaurant. Not every site has a lease "
         "here: an unknown site_id is refused with 404, and a site with no lease gives an empty list. Read the text with get_lease.")
    def list_leases(site_id: str | None = Query(None, description="Only the lease of this site, for example S-101 or R-031.")):
        if site_id and site_id not in d()["sites"]:
            raise not_found("site", site_id, "Site ids look like S-101 or R-031.")
        rows = [{k: x[k] for k in served} for x in d()["leases"].values() if not site_id or x["site_id"] == site_id]
        return listing(sorted(rows, key=lambda x: x["lease_id"]), retailer_date=st.settings.retailer_today.isoformat())

    @reg(app, "get", "/leases/{lease_id}", "get_lease", "Get one lease with its text",
         f"Read one lease: {ROW_FIELDS}; clauses (every clause in order, each with number, heading and text); text (the whole "
         "lease as written); summaries (every saved summary, each a version); and retailer_date, the date the retailer counts "
         "as today, to work out how far away a date in the lease is. Dates in the text are written out, for example 1 July "
         "2027. The lease says how many months of notice a break needs; it does not give the last day for the notice. Find "
         "the id with list_leases.")
    def get_lease(lease_id: str = lease_p):
        return {**lease_or_404(lease_id), "retailer_date": st.settings.retailer_today.isoformat()}

    @reg(app, "post", "/leases/{lease_id}/summary", "save_lease_summary", "Save the summary of a lease (draft)",
         "Save a summary of one lease, as a draft. It changes nothing in the lease. Each call is kept as a new version with "
         "who wrote it and when. Send term (start_date, end_date, clause), rent (annual_rent, clause), rent_reviews (each "
         "with review_date, basis and clause), break_options (each with break_date, who_may_break, notice_months, notice_by "
         "and clause; an empty list when the lease has no break clause), repair_duties (each with party, duty and clause), "
         "optional other_points and summary, and drafted_by. Dates are YYYY-MM-DD. Every clause number must be a clause of "
         "this lease, or the call is refused with 422 and the message lists the clause numbers the lease has. The property "
         "team checks the summary against the lease. Returns the saved version.")
    def save_lease_summary(body: LeaseSummary, lease_id: str = lease_p):
        lease = lease_or_404(lease_id)
        numbers = [c["number"] for c in lease["clauses"]]
        cited = ([body.term.clause, body.rent.clause] + [x.clause for x in body.rent_reviews]
                 + [x.clause for x in body.break_options] + [x.clause for x in body.repair_duties]
                 + [x.clause for x in body.other_points])
        wrong = sorted({c for c in cited if c not in numbers})
        if wrong:
            raise HTTPException(422, f"Lease {lease_id} has no clause {', '.join(wrong)}. Nothing was saved. Its clauses are "
                                     f"{', '.join(numbers)}.")
        payload = body.model_dump(exclude={"drafted_by"})
        v = st.add_draft(lease, "summaries", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "lease_id": lease_id}

    return app
