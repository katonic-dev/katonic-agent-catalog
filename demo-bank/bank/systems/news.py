"""News: an invented press archive, for adverse media screening."""

from __future__ import annotations

import html
from typing import Literal

from fastapi import Path, Query, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from ..common import Ctx, listing, make_subapp, not_found, reg
from ..config import INVENTED_NOTICE

KEY = "news"
TITLE = "News archive"
LINE = "An invented press archive from two invented outlets, for adverse media screening."


class Finding(BaseModel):
    article_id: str = Field(..., description="Article id, for example ART-6001.")
    relevance: Literal["about_subject", "not_about_subject", "unclear"] = Field(
        ..., description="about_subject: the article is about the subject. not_about_subject: it is about someone else "
                         "with the same or a similar name. unclear: the article does not say enough.")
    adverse: bool = Field(False, description="True if the article reports wrongdoing, a charge, a sanction or an inquiry.")
    reason: str = Field(..., min_length=1, description="Why the article is or is not about the subject: age, town, country, trade or other facts.")


class ScreeningDraft(BaseModel):
    subject_name: str = Field(..., min_length=1, description="Name of the person or company that was screened.")
    customer_id: str = Field("", description="Customer id of the subject if the subject is a customer, for example CUS-1007. Leave empty if not.")
    findings: list[Finding] = Field(default_factory=list, description="One finding for each article read. Leave empty if nothing was found.")
    conclusion: str = Field("", description="The overall conclusion in plain sentences.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


def _origin(request: Request) -> str:
    # an MCP call reaches this app from inside, so the caller's own prefix arrives in a header
    root = request.headers.get("x-public-root-path", request.scope.get("root_path", "")).rstrip("/")
    return f"{request.url.scheme}://{request.headers.get('host', request.url.netloc)}{root}"


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds news articles from two invented outlets. Use it to look for adverse "
                                  "coverage of a customer or a counterparty.")
    st = ctx.store
    d = lambda: st.data
    art_p = Path(..., description="Article id, for example ART-6001.")

    def art_or_404(aid):
        a = d()["news_articles"].get(aid)
        if not a:
            raise not_found("article", aid, "Use search_news to find ids.")
        return a

    @reg(app, "get", "/articles", "search_news", "Search the news archive",
         "Search articles by text. Every word you give must appear in the title or the body, in any order, not case "
         "sensitive. Results are newest first. Each row has article_id, title, date, outlet, section and a short snippet. "
         "Names can be shared by different people, so read the article with get_news_article before you decide it is "
         "about your subject.")
    def search_news(request: Request,
                    text: str = Query("", description="Words to look for, for example a person's name. Leave empty for all articles."),
                    date_from: str = Query("", description="Earliest article date, YYYY-MM-DD."),
                    date_to: str = Query("", description="Latest article date, YYYY-MM-DD."),
                    limit: int = Query(10, ge=1, le=100, description="Most rows to return.")):
        words = text.lower().split()
        rows = []
        for a in d()["news_articles"].values():
            hay = (a["title"] + " " + a["body"]).lower()
            if any(w not in hay for w in words):
                continue
            if (date_from and a["date"] < date_from) or (date_to and a["date"] > date_to):
                continue
            rows.append(a)
        rows.sort(key=lambda a: (a["date"], a["article_id"]), reverse=True)
        origin = _origin(request)
        out = [{"article_id": a["article_id"], "title": a["title"], "date": a["date"], "outlet": a["outlet"],
                "section": a["section"], "snippet": a["body"].split("\n\n")[0][:220],
                "page_url": f"{origin}/pages/{a['article_id']}"} for a in rows[:limit]]
        return listing(out, total_matches=len(rows))

    @reg(app, "get", "/articles/{article_id}", "get_news_article", "Get one article in full",
         "Read one article: title, date, outlet, section, the full text and page_url, the address of the article's web page. "
         "Put page_url in a summary so a person can open the article. Read the full text for the age, town, country or trade "
         "of the person named before you decide who the article is about.")
    def get_news_article(request: Request, article_id: str = art_p):
        a = art_or_404(article_id)
        return {**a, "page_url": f"{_origin(request)}/pages/{article_id}"}

    @reg(app, "post", "/screenings", "save_media_screening_summary", "Save a media screening summary (draft)",
         "Save the findings of an adverse media screening of one subject: the subject's name, the customer id if there is one, "
         "and one finding per article read, each with the article id and why it is or is not about the subject. This is a "
         "draft: stored with who wrote it, a timestamp and a version number, earlier versions kept. A second summary for "
         "the same subject becomes the next version. Nothing else changes.")
    def save_media_screening_summary(body: ScreeningDraft):
        with st.lock:
            if body.customer_id and body.customer_id not in d()["customers"]:
                raise not_found("customer", body.customer_id, "Use search_customers in the core system to find the id.")
            for f in body.findings:
                art_or_404(f.article_id)
            key = body.customer_id or body.subject_name.strip().lower()
            item = next((x for x in d()["media_screenings"].values() if x["key"] == key), None)
            if item is None:
                sid = f"MS-{st.next_number('media_screening', 1001)}"
                item = {"screening_id": sid, "key": key, "subject_name": body.subject_name, "customer_id": body.customer_id,
                        "summaries": []}
                d()["media_screenings"][sid] = item
            v = st.add_draft(item, "summaries", {"subject_name": body.subject_name,
                                                  "findings": [f.model_dump() for f in body.findings],
                                                  "conclusion": body.conclusion}, body.drafted_by)
        return {"applied": True, "kind": "draft", "screening_id": item["screening_id"], "draft": v}

    @app.get("/pages/{article_id}", include_in_schema=False, response_class=HTMLResponse)
    async def article_page(article_id: str):
        a = d()["news_articles"].get(article_id)
        if not a:
            return HTMLResponse("<!doctype html><title>Not found</title><p>No article with this id.</p>", status_code=404)
        paras = "".join(f"<p>{html.escape(p)}</p>" for p in a["body"].split("\n\n"))
        page = (f'<!doctype html><html lang="en"><head><meta charset="utf-8">'
                f'<meta name="viewport" content="width=device-width, initial-scale=1">'
                f"<title>{html.escape(a['title'])}</title>"
                "<style>body{font-family:Georgia,serif;max-width:40rem;margin:2rem auto;padding:0 1rem;line-height:1.6;color:#1b2430}"
                "small{color:#555}</style></head><body>"
                f"<small>{html.escape(a['outlet'])} (invented) &middot; {html.escape(a['section'])} &middot; {a['date']}</small>"
                f"<h1>{html.escape(a['title'])}</h1>{paras}"
                f"<hr><small>{html.escape(INVENTED_NOTICE)} {a['article_id']}</small></body></html>")
        return HTMLResponse(page)

    return app
