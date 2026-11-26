"""Regulator test feeds: two invented RSS 2.0 feeds that a scheduled monitoring workflow can be tested against.

They are not one of the bank's systems and not a real regulator. They need no key, have no MCP address and are
not in any OpenAPI document. Each feed stands in for one live regulator feed and copies its layout: the "fca" feed
has one element per line, the "ecb" feed has all its items on one long line. Every item is invented.

A tester picks a series (any short token) for each test run. A series starts at the starting items. Only what the
admin routes change is stored, in the record set feed_series, so POST /admin/reset/feeds puts every series back.

Routes: GET /feeds/{feed}.xml (the series "default") and GET /feeds/{series}/{feed}.xml, open;
POST /admin/feeds/{series}/{feed}/publish, POST /admin/feeds/{series}/{feed}/unreadable?on=true|false and
GET /admin/feeds/{series}, behind the key like the other admin routes.
"""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse, Response

from .common import Ctx, make_auth

KEY = "feeds"
FEEDS = ("fca", "ecb")
SERIES = re.compile(r"[a-z0-9-]{1,40}")
LINK_BASE = "https://feeds.meridian-demo.example"
CHANNEL = {
    "fca": ("Test copy of a regulator news feed (FCA slot), invented items, Meridian demo bank",
            "Test copy of a regulator news feed, invented items, Meridian demo bank. It stands in for the FCA news "
            "feed in tests. Nothing in it was published by any regulator."),
    "ecb": ("Test copy of a regulator press feed (ECB slot), invented items, Meridian demo bank",
            "Test copy of a regulator press feed, invented items, Meridian demo bank. It stands in for the ECB press "
            "feed in tests. Nothing in it was published by any regulator."),
}
# Starting items, newest first, with their age in days at the bank date.
START = {
    "fca": [
        (0, "Test notice: clearer fee tables for invented savings accounts"),
        (1, "Test consultation: plain wording in invented loan agreements"),
        (3, "Test statement: invented review of branch opening hours"),
        (6, "Test guidance: handling invented complaints about card fees"),
        (9, "Test notice: updated contact address for invented firms"),
        (13, "Test speech: invented remarks on fair treatment of savers"),
        (18, "Test policy statement: invented rules for payment reminders"),
        (24, "Test notice: invented register maintenance & downtime"),
    ],
    "ecb": [
        (0, "Test press release: invented interest rate decision held steady"),
        (2, "Test press release: invented survey of bank lending conditions"),
        (4, "Test speech: invented address on payments in a small economy"),
        (7, "Test press release: invented results of a liquidity exercise"),
        (10, "Test interview: invented questions on digital cash"),
        (14, "Test press release: invented statistics on household deposits"),
        (19, "Test blog post: invented notes on supervisory priorities"),
        (25, "Test press release: invented calendar of supervisory meetings"),
    ],
}
# Items that POST /admin/feeds/.../publish adds, in this order. After the last, the list starts again with a round number.
NEW = {
    "fca": ["Test notice: invented rules on dormant accounts", "Test consultation: invented limits on overdraft charges",
            "Test statement: invented review of mortgage arrears handling", "Test guidance: invented checks on new payees",
            "Test notice: invented reporting dates for small firms", "Test policy statement: invented record keeping rules",
            "Test speech: invented remarks on vulnerable customers", "Test notice: invented changes to the firm register",
            "Test consultation: invented disclosure of savings rates", "Test statement: invented outcome of a fee review"],
    "ecb": ["Test press release: invented monetary policy statement", "Test speech: invented address on bank resilience",
            "Test press release: invented consolidated banking data", "Test interview: invented questions on inflation",
            "Test press release: invented minutes of a policy meeting", "Test blog post: invented notes on climate risk",
            "Test press release: invented supervisory fees for next year", "Test speech: invented remarks on cash use",
            "Test press release: invented euro area bank lending figures", "Test interview: invented questions on payments"],
}


def _check(series: str, feed: str) -> None:
    if not SERIES.fullmatch(series):
        raise HTTPException(404, "A series is 1 to 40 characters: small letters, digits and hyphens.")
    if feed not in FEEDS:
        raise HTTPException(404, f"No feed named {feed}. Use one of: {', '.join(FEEDS)}.")


def _rfc822(day: date, feed: str) -> str:
    when = datetime(day.year, day.month, day.day, 9 if feed == "fca" else 14, 30, tzinfo=timezone.utc)
    return format_datetime(when, usegmt=feed == "fca")


def _item(feed: str, ident: str, day: date, title: str) -> dict:
    return {"id": ident, "title": title, "date": day.isoformat(), "link": f"{LINK_BASE}/{feed}/{ident.lower()}"}


def starting_items(feed: str, today: date) -> list[dict]:
    n = len(START[feed])
    return [_item(feed, f"{feed.upper()}-T{n - i:03d}", today - timedelta(days=ago), title)
            for i, (ago, title) in enumerate(START[feed])]


def new_item(feed: str, today: date, k: int) -> dict:
    """The k-th published item (k from 0): a title from the fixed list, dated k + 1 days after the bank date."""
    pool = NEW[feed]
    title = pool[k % len(pool)] + (f" (round {k // len(pool) + 1})" if k >= len(pool) else "")
    return _item(feed, f"{feed.upper()}-P{k + 1:03d}", today + timedelta(days=k + 1), title)


def _xml_fca(items: list[dict]) -> str:
    title, desc = CHANNEL["fca"]
    lines = ['<?xml version="1.0" encoding="utf-8"?>', '<rss version="2.0">', "  <channel>",
             f"    <title>{escape(title)}</title>", f"    <link>{LINK_BASE}/fca/</link>",
             f"    <description>{escape(desc)}</description>", "    <language>en</language>"]
    for it in items:
        lines += ["    <item>", f"      <title>{escape(it['title'])}</title>", f"      <link>{it['link']}</link>",
                  f"      <description>{escape(it['title'])}. Invented test item.</description>",
                  f"      <pubDate>{_rfc822(date.fromisoformat(it['date']), 'fca')}</pubDate>",
                  f'      <guid isPermaLink="false">{it["id"]}</guid>', "    </item>"]
    return "\n".join(lines + ["  </channel>", "</rss>", ""])


def _xml_ecb(items: list[dict]) -> str:
    title, desc = CHANNEL["ecb"]
    head = (f'<rss version="2.0"><channel><title>{escape(title)}</title><link>{LINK_BASE}/ecb/</link>'
            f"<description>{escape(desc)}</description><language>en</language>")
    body = "".join(
        f"<item><title>{escape(it['title'])}</title><link>{it['link']}</link>"
        f"<description><![CDATA[<p>{escape(it['title'])}. Invented test item.</p>]]></description>"
        f"<pubDate>{_rfc822(date.fromisoformat(it['date']), 'ecb')}</pubDate>"
        f'<guid isPermaLink="false">{it["id"]}</guid></item>' for it in items)
    return "\n".join(['<?xml version="1.0" encoding="UTF-8"?>', head, body, "</channel></rss>", ""])


def make_routers(ctx: Ctx) -> tuple[APIRouter, APIRouter]:
    st = ctx.store
    today = lambda: ctx.settings.bank_today

    def state(series: str, feed: str) -> dict:
        """What the admin routes have changed in one series and feed. Never stored by a read."""
        return st.data["feed_series"].get(series, {}).get(feed, {"published": [], "unreadable": False})

    def stored_state(series: str, feed: str) -> dict:
        return st.data["feed_series"].setdefault(series, {}).setdefault(feed, {"published": [], "unreadable": False})

    def items(series: str, feed: str) -> list[dict]:
        return list(reversed(state(series, feed)["published"])) + starting_items(feed, today())

    public = APIRouter(prefix="/feeds", include_in_schema=False)

    def serve(series: str, feed: str):
        _check(series, feed)
        if state(series, feed)["unreadable"]:
            return PlainTextResponse("Service unavailable. This test feed is switched to unreadable.", status_code=503)
        xml = (_xml_fca if feed == "fca" else _xml_ecb)(items(series, feed))
        return Response(xml, media_type="application/rss+xml; charset=utf-8")

    @public.get("/{feed}.xml")
    async def default_feed(feed: str):
        return serve("default", feed)

    @public.get("/{series}/{feed}.xml")
    async def series_feed(series: str, feed: str):
        return serve(series, feed)

    admin = APIRouter(prefix="/admin/feeds", dependencies=[Depends(make_auth(ctx))], include_in_schema=False)

    @admin.post("/{series}/{feed}/publish")
    async def publish(series: str, feed: str):
        _check(series, feed)
        with st.lock:
            s = stored_state(series, feed)
            it = new_item(feed, today(), len(s["published"]))
            s["published"].append(it)
        return {"applied": True, "series": series, "feed": feed, "count": len(items(series, feed)),
                "item": {"title": it["title"], "date": it["date"], "link": it["link"]}}

    @admin.post("/{series}/{feed}/unreadable")
    async def unreadable(series: str, feed: str,
                         on: bool = Query(True, description="true: the feed answers 503. false: it answers again.")):
        _check(series, feed)
        with st.lock:
            stored_state(series, feed)["unreadable"] = on
        return {"applied": True, "series": series, "feed": feed, "unreadable": on}

    @admin.get("/{series}")
    async def show(series: str):
        _check(series, FEEDS[0])
        return {"series": series, "feeds": {
            feed: {"address": f"/feeds/{series}/{feed}.xml", "unreadable": state(series, feed)["unreadable"],
                   "count": len(items(series, feed)),
                   "items": [{"title": it["title"], "date": it["date"], "link": it["link"]} for it in items(series, feed)]}
            for feed in FEEDS}}

    return public, admin
