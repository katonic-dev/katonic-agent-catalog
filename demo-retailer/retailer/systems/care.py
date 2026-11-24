"""Customer care, version 1: guest feedback only."""

from __future__ import annotations

from typing import Literal

from fastapi import Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, listing, make_subapp, not_found, reg

KEY = "care"
TITLE = "Customer care"
LINE = "Guest feedback from the restaurants: comments with date, site, channel and rating, and the analyses saved on them."

PERIOD_RE = r"^\d{4}-(0[1-9]|1[0-2])$"
FIELDS = "reference, date, site_id, channel (call centre, app review, survey or web form), rating (1 to 5) and comment"


class Theme(BaseModel):
    name: str = Field(..., min_length=1, description="The theme in plain words, for example late delivery.")
    count: int = Field(..., ge=0, description="How many comments belong to this theme.")
    counts_by_site: dict[str, int] = Field(default_factory=dict, description="How many of those comments came from each site, "
                                           "for example {\"R-047\": 20}. The keys are site ids.")
    quoted_references: list[str] = Field(default_factory=list, description="The references of the comments quoted for this theme, "
                                         "for example GF-2610-0042. Each must be a comment of the same period.")


class FeedbackAnalysis(BaseModel):
    period: str = Field(..., pattern=PERIOD_RE, description="The month the analysis covers, as YYYY-MM, for example 2026-10.")
    themes: list[Theme] = Field(..., min_length=1, description="The themes found, each with a name, a count, counts by site and "
                                "the references of the comments quoted.")
    harm_comments: list[str] = Field(default_factory=list, description="The references of every comment that describes harm or a "
                                     "safety matter. Leave the list empty if there is none. A person must see each one.")
    summary: str = Field("", description="A short summary in plain sentences. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds guest feedback. Version 1 has no tickets, complaints, returns or public "
                                  "reviews. Saving an analysis is a draft.")
    st = ctx.store
    d = lambda: st.data

    def feedback_or_404(ref):
        x = d()["guest_feedback"].get(ref)
        if not x:
            raise not_found("guest feedback", ref, "Use list_guest_feedback to find references.")
        return x

    @reg(app, "get", "/feedback", "list_guest_feedback", "List guest feedback",
         f"List guest feedback comments, oldest first. Each row has {FIELDS}. Every filter is optional and the filters add up: "
         "period (YYYY-MM), site_id, channel and max_rating (only ratings up to this number). The answer has count (the rows "
         "returned), total (all rows that match), offset and limit. Use limit and offset to read the next page. "
         "The comment is the guest's own words.")
    def list_guest_feedback(
            period: str | None = Query(None, pattern=PERIOD_RE, description="Only comments from this month, as YYYY-MM, for example 2026-10."),
            site_id: str | None = Query(None, description="Only comments about this restaurant, for example R-047."),
            channel: Literal["call centre", "app review", "survey", "web form"] | None = Query(None, description="Only this channel."),
            max_rating: int | None = Query(None, ge=1, le=5, description="Only comments with this rating or lower, 1 to 5."),
            limit: int = Query(100, ge=1, le=500, description="Most rows to return, up to 500."),
            offset: int = Query(0, ge=0, description="How many matching rows to skip.")):
        rows = [x for x in d()["guest_feedback"].values()
                if (not period or x["date"].startswith(period)) and (not site_id or x["site_id"] == site_id)
                and (not channel or x["channel"] == channel) and (max_rating is None or x["rating"] <= max_rating)]
        rows.sort(key=lambda x: x["reference"])
        page = rows[offset:offset + limit]
        return listing(page, total=len(rows), offset=offset, limit=limit)

    @reg(app, "get", "/feedback/{reference}", "get_guest_feedback", "Get one guest comment",
         f"Read one guest comment: {FIELDS}. The reference looks like GF-2610-0001. Find it with list_guest_feedback.")
    def get_guest_feedback(reference: str = Path(..., description="Comment reference, for example GF-2610-0001.")):
        return feedback_or_404(reference)

    @reg(app, "get", "/analysis/{period}", "get_feedback_analysis", "Get the saved analyses for a month",
         "Read every analysis saved for one month, oldest first. Fields: period, count and analyses, a list of versions, each with "
         "version, drafted_by, drafted_at, themes (name, count, counts_by_site, quoted_references), harm_comments and summary. "
         "The list is empty when nothing was saved.")
    def get_feedback_analysis(period: str = Path(..., pattern=PERIOD_RE, description="Month as YYYY-MM, for example 2026-10.")):
        item = d()["feedback_analyses"].get(period, {"analyses": []})
        return {"period": period, "count": len(item["analyses"]), "analyses": item["analyses"]}

    @reg(app, "post", "/analysis", "save_feedback_analysis", "Save an analysis of a month's feedback (draft)",
         "Save an analysis of one month's guest feedback, as a draft. It changes no comment. Each call is kept as a new version "
         "with who wrote it and when. Send period, themes (each with name, count, counts_by_site and quoted_references), "
         "harm_comments (the references of every comment that describes harm or a safety matter), an optional summary, and "
         "drafted_by. Every reference must be a comment of that month, or the call is refused with 404. A person reads the "
         "harm comments first. Returns the saved version.")
    def save_feedback_analysis(body: FeedbackAnalysis):
        refs = list(body.harm_comments) + [r for t in body.themes for r in t.quoted_references]
        for ref in refs:
            x = feedback_or_404(ref)
            if not x["date"].startswith(body.period):
                raise not_found("guest feedback in period " + body.period, ref, "Use list_guest_feedback with the period.")
        for t in body.themes:
            for site in t.counts_by_site:
                if site not in d()["sites"]:
                    raise not_found("site", site, "Use list_sites to find site ids.")
        with st.lock:
            item = d()["feedback_analyses"].setdefault(body.period, {"period": body.period, "analyses": []})
            payload = {"themes": [t.model_dump() for t in body.themes], "harm_comments": list(body.harm_comments),
                       "summary": body.summary}
            v = st.add_draft(item, "analyses", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "period": body.period}

    return app
