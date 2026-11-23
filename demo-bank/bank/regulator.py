"""The Meridia Financial Conduct Authority (invented): a regulator's public website.

It is not one of the bank's systems. It needs no key, has no MCP address and is not in any OpenAPI document.
Routes: /regulator/feed.xml (RSS 2.0), /regulator/publications.json and /regulator/publications/{id} (an HTML page).
"""

from __future__ import annotations

import html
from datetime import date
from email.utils import format_datetime
from datetime import datetime, timezone
from xml.sax.saxutils import escape

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, Response

from .common import Ctx
from .config import INVENTED_NOTICE
from .seed_reg import REGULATOR_NAME

DESCRIPTION = ("The public website of an invented financial regulator. It publishes circulars, guidelines, notices and "
               "consultation papers.")


def _origin(request: Request) -> str:
    root = request.scope.get("root_path", "").rstrip("/")
    return f"{request.url.scheme}://{request.headers.get('host', request.url.netloc)}{root}"


def _rfc822(day: str) -> str:
    d = date.fromisoformat(day)
    return format_datetime(datetime(d.year, d.month, d.day, 9, 0, tzinfo=timezone.utc))


def make_router(ctx: Ctx) -> APIRouter:
    router = APIRouter(prefix="/regulator", include_in_schema=False)
    st = ctx.store

    def newest_first() -> list[dict]:
        return sorted(st.data["regulator_publications"].values(),
                      key=lambda p: (p["published"], p["publication_id"]), reverse=True)

    @router.get("/feed.xml")
    async def feed(request: Request):
        origin = _origin(request)
        items = "".join(
            "<item>"
            f"<title>{escape(p['title'])}</title>"
            f"<link>{escape(origin)}/regulator/publications/{p['publication_id']}</link>"
            f"<pubDate>{_rfc822(p['published'])}</pubDate>"
            f'<guid isPermaLink="false">{p["publication_id"]}</guid>'
            f"<description>{escape(p['summary'])}</description>"
            "</item>" for p in newest_first())
        xml = ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
               f"<title>{escape(REGULATOR_NAME)}: publications</title>"
               f"<link>{escape(origin)}/regulator/publications.json</link>"
               f"<description>{escape(DESCRIPTION)}</description><language>en</language>{items}</channel></rss>")
        return Response(xml, media_type="application/rss+xml; charset=utf-8")

    @router.get("/publications.json")
    async def publications(request: Request):
        origin = _origin(request)
        items = [{"id": p["publication_id"], "title": p["title"], "kind": p["kind"], "binding": p["binding"],
                  "published": p["published"], "link": f"{origin}/regulator/publications/{p['publication_id']}",
                  "description": p["summary"]} for p in newest_first()]
        return {"regulator": REGULATOR_NAME, "count": len(items), "items": items}

    @router.get("/publications/{publication_id}")
    async def publication(publication_id: str):
        p = st.data["regulator_publications"].get(publication_id)
        if not p:
            return HTMLResponse("<!doctype html><title>Not found</title><p>No publication with this id.</p>", status_code=404)
        paras = "".join(f'<p id="p{n}"><b>{n}.</b> {html.escape(t)}</p>' for n, t in enumerate(p["paragraphs"], start=1))
        status = "Binding on banks." if p["binding"] else "Consultation. Not yet binding."
        page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width, initial-scale=1">'
                f"<title>{html.escape(p['title'])}</title>"
                "<style>body{font-family:system-ui,Segoe UI,Arial,sans-serif;max-width:44rem;margin:2rem auto;padding:0 1rem;"
                "line-height:1.6;color:#1b2430}small{color:#555}</style></head><body>"
                f"<small>{html.escape(REGULATOR_NAME)} &middot; {html.escape(p['kind'])} &middot; {p['publication_id']} "
                f"&middot; published {p['published']} &middot; {status}</small>"
                f"<h1>{html.escape(p['title'])}</h1>{paras}"
                f"<hr><small>{html.escape(INVENTED_NOTICE)} This regulator is invented too.</small></body></html>")
        return HTMLResponse(page)

    return router
