"""Assembles the service: nineteen systems, the regulator's public feed, admin routes, landing page, health."""

from __future__ import annotations

import html
import logging
from typing import Literal

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field

from . import events
from .common import Ctx, public_scheme, DemoJSONResponse, FastAPIOffline, make_auth, not_found
from .config import BANK_NAME, INVENTED_NOTICE, load_settings
from .mcp_doors import install_mcp
from .store import Store
from .regulator import make_router as make_regulator_router
from .seed_reg import REGULATOR_NAME
from .systems import (aml, audit, cards, collections, complaints, core, crm, finance, fraud, funds, itops, legacy, lending, news, onboarding,
                      payments, recon, research, screening)

log = logging.getLogger("demo-bank")
SYSTEMS = [core, cards, screening, aml, payments, lending, fraud, recon, news, onboarding, complaints, collections, audit,
           itops, legacy, funds, crm, finance, research]


class DemoHeaderMiddleware:
    """Adds X-Demo-Data: invented to every HTTP response, streaming ones included."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def wrapped(message):
            if message["type"] == "http.response.start":
                headers = [(k, v) for k, v in message.get("headers", []) if k.lower() != b"x-demo-data"]
                headers.append((b"x-demo-data", b"invented"))
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, wrapped)


class SubscriptionBody(BaseModel):
    event_kind: Literal["*", "screening-alert", "payment-repair", "payment-investigation", "loan-application",
                        "fraud-case", "reconciliation-break", "regulator-publication", "onboarding-application", "kyc-review",
                        "complaint", "collections-call", "incident", "contribution-batch", "client-meeting",
                        "monitoring-alert"] = Field(
        "*", description="Which events to send. * means all.")
    url: str = Field(..., description="Where to POST the event.")
    header_name: str = Field("", description="Name of the header that carries the secret.")
    secret_value: str = Field("", description="Value of that header.")


def create_app(env: dict | None = None) -> FastAPI:
    settings = load_settings(env)
    store = Store(settings)
    ctx = Ctx(settings=settings, store=store)
    if settings.key_was_generated and settings.auth_enabled:
        msg = f"No BANK_API_KEY was set. Generated a key for this run: {settings.api_key}"
        log.warning(msg)
        print(msg, flush=True)
    if not settings.auth_enabled:
        log.warning("BANK_AUTH=off: the service needs no key. Use this only on a laptop.")

    app = FastAPI(title=f"{BANK_NAME} (invented)", docs_url=None, redoc_url=None, openapi_url=None,
                  default_response_class=DemoJSONResponse)
    app.state.ctx = ctx
    app.add_middleware(DemoHeaderMiddleware)

    subs = []
    for mod in SYSTEMS:
        sub = mod.build(ctx)
        install_mcp(sub, ctx)

        async def to_docs(request: Request):
            root = request.scope.get("root_path", "")
            target = f"{root}/docs" if FastAPIOffline is not None else f"{root}/openapi.json"
            return RedirectResponse(target)

        sub.add_route("/", to_docs, methods=["GET"], include_in_schema=False)
        app.mount(f"/{mod.KEY}", sub, name=mod.KEY)
        subs.append((mod, sub))

    @app.get("/health", include_in_schema=False)
    @app.get("/healthz", include_in_schema=False)
    async def health():
        return {"status": "ok", "bank": BANK_NAME, "bank_date": settings.bank_today.isoformat()}

    # ------------------------------------------------------------ admin
    admin = APIRouter(prefix="/admin", dependencies=[Depends(make_auth(ctx))], include_in_schema=False)

    @admin.post("/reset")
    async def reset():
        store.reset()
        return {"applied": True, "message": "Back to the starting data.", "counts": store.counts()}

    @admin.get("/state")
    async def state():
        return {"bank_date": settings.bank_today.isoformat(), "auth_enabled": settings.auth_enabled,
                "data_dir_set": settings.data_dir is not None, "counts": store.counts(),
                "subscriptions": len(store.subscriptions)}

    @admin.get("/events")
    async def get_events():
        return {"count": len(store.events), "items": list(store.events)}

    @admin.get("/subscriptions")
    async def list_subs():
        items = [{**s, "secret_value": "***" if s["secret_value"] else ""} for s in store.subscriptions]
        return {"count": len(items), "items": items}

    @admin.post("/subscriptions")
    async def add_sub(body: SubscriptionBody):
        s = store.add_subscription(body.event_kind, body.url, body.header_name, body.secret_value)
        return {"applied": True, "subscription": {**s, "secret_value": "***" if s["secret_value"] else ""}}

    @admin.delete("/subscriptions/{subscription_id}")
    async def delete_sub(subscription_id: str):
        with store.lock:
            before = len(store.subscriptions)
            store.subscriptions = [s for s in store.subscriptions if s["subscription_id"] != subscription_id]
            if len(store.subscriptions) == before:
                raise not_found("subscription", subscription_id)
        return {"applied": True, "deleted": subscription_id}

    @admin.delete("/subscriptions")
    async def delete_all_subs():
        with store.lock:
            n = len(store.subscriptions)
            store.subscriptions = []
        return {"applied": True, "deleted": n}

    @admin.post("/simulate/{kind}")
    async def simulate(kind: str):
        if kind not in events.KINDS:
            raise HTTPException(404, f"Unknown kind {kind}. Use one of: {', '.join(events.KINDS)}.")
        return events.simulate(store, kind)

    app.include_router(admin)
    app.include_router(make_regulator_router(ctx))

    @app.exception_handler(HTTPException)
    async def _err(_: Request, exc: HTTPException):
        return DemoJSONResponse({"detail": exc.detail, "applied": False}, status_code=exc.status_code)

    # ------------------------------------------------------------ landing
    @app.get("/", include_in_schema=False)
    async def landing(request: Request):
        root = request.scope.get("root_path", "").rstrip("/")
        origin = f"{public_scheme(request)}://{request.headers.get('host', request.url.netloc)}{root}"
        counts = store.counts()
        rows = []
        for mod, _ in subs:
            k = mod.KEY
            docs = f'<a href="{root}/{k}/docs">docs</a>' if FastAPIOffline is not None else "docs are off"
            rows.append(f"<tr><td><b>{html.escape(mod.TITLE)}</b><br>{html.escape(mod.LINE)}</td><td>{docs}</td>"
                        f'<td><a href="{root}/{k}/openapi.json">{html.escape(origin)}/{k}/openapi.json</a></td>'
                        f"<td>{html.escape(origin)}/{k}/mcp<br>{html.escape(origin)}/{k}/sse</td></tr>")
        warn = ""
        if not settings.auth_enabled:
            warn = ('<p style="background:#fde8e8;border:2px solid #b00;padding:10px"><b>Warning: sign-in is OFF '
                    "(BANK_AUTH=off).</b> Anyone who can reach this address can read and change the data. "
                    "Use this only on your own laptop.</p>")
        pubs = sorted(store.data["regulator_publications"].values(), key=lambda p: (p["published"], p["publication_id"]))
        first_pub = html.escape(pubs[-1]["publication_id"]) if pubs else ""
        count_rows = "".join(f"<tr><td>{html.escape(k.replace('_', ' '))}</td><td>{v}</td></tr>" for k, v in counts.items())
        page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{BANK_NAME} (invented)</title>
<style>body{{font-family:system-ui,Segoe UI,Arial,sans-serif;max-width:60rem;margin:2rem auto;padding:0 1rem;line-height:1.5;color:#1b2430}}
table{{border-collapse:collapse;width:100%;margin:1rem 0}}td,th{{border:1px solid #c9d1dc;padding:6px 10px;text-align:left;vertical-align:top;font-size:.92rem}}
th{{background:#eef2f7}}code{{background:#eef2f7;padding:1px 4px}}</style></head><body>
<h1>{BANK_NAME} (invented)</h1>
<p><b>{html.escape(INVENTED_NOTICE)}</b></p>
{warn}
<p>This service plays the back-office systems of a bank so that AI agents have something realistic to read and act on.
Every JSON answer carries <code>"demo_data": true</code> and the header <code>X-Demo-Data: invented</code>.</p>
<p>Bank date: <b>{settings.bank_today.isoformat()}</b>. Data operations need a key in the <code>X-API-Key</code> header
(or <code>Authorization: Bearer ...</code>). The key is not shown here.</p>
<h2>The nineteen systems</h2>
<table><tr><th>System</th><th>API docs</th><th>OpenAPI document</th><th>MCP addresses</th></tr>{''.join(rows)}</table>
<h2>A regulator's public website (invented)</h2>
<p><b>{html.escape(REGULATOR_NAME)}</b> is invented. It is not one of the bank's systems: it stands for a regulator's
public website. It needs no key and has no MCP address.</p>
<ul><li><a href="{root}/regulator/feed.xml">{html.escape(origin)}/regulator/feed.xml</a> (RSS 2.0, newest first)</li>
<li><a href="{root}/regulator/publications.json">{html.escape(origin)}/regulator/publications.json</a> (the same list as JSON)</li>
<li>{html.escape(origin)}/regulator/publications/&lt;id&gt; (one publication as a web page, for example
<a href="{root}/regulator/publications/{first_pub}">{first_pub}</a>)</li></ul>
<h2>Open items</h2><table>{count_rows}</table>
<h2>Start again</h2>
<p>Send <code>POST {html.escape(root)}/admin/reset</code> with the key. This puts all data back to the starting point.
<code>POST {html.escape(root)}/admin/simulate/&lt;kind&gt;</code> makes one new item arrive
(kinds: {', '.join(events.KINDS)}).</p>
</body></html>"""
        return HTMLResponse(page)

    return app
