"""Assembles the service: the insurer's systems, admin routes, landing page, health."""

from __future__ import annotations

import asyncio
import html
import logging
import threading
from typing import Literal

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field

from . import events
from .common import Ctx, public_scheme, DemoJSONResponse, FastAPIOffline, make_auth, not_found
from .config import INSURER_NAME, INVENTED_NOTICE, load_settings
from .mcp_doors import install_mcp
from .store import Store
from .systems import claims, policy

log = logging.getLogger("demo-insurer")
SYSTEMS = [policy, claims]


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


class WriteNotes:
    """Notes, after every request that may write, which records changed and for which system.

    That is what lets one system be put back without the others (POST /admin/reset/{system}).
    Requests that may write go through one at a time, so a change is never put down to the wrong system.
    """

    def __init__(self, app, store: Store, owner_of):
        self.app, self.store, self.owner_of = app, store, owner_of
        self.gate = threading.Lock()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http" or scope.get("method", "GET") in ("GET", "HEAD", "OPTIONS"):
            await self.app(scope, receive, send)
            return
        while not self.gate.acquire(blocking=False):
            await asyncio.sleep(0.005)
        try:
            await self.app(scope, receive, send)
        finally:
            try:
                self.store.note_writes(self.owner_of(scope.get("path", "")))
            finally:
                self.gate.release()


class SubscriptionBody(BaseModel):
    event_kind: Literal["*", "loss-report"] = Field(
        "*", description="Which events to send. * means all.")
    url: str = Field(..., description="Where to POST the event.")
    header_name: str = Field("", description="Name of the header that carries the secret.")
    secret_value: str = Field("", description="Value of that header.")


def create_app(env: dict | None = None) -> FastAPI:
    settings = load_settings(env)
    store = Store(settings)
    ctx = Ctx(settings=settings, store=store)
    if settings.key_was_generated and settings.auth_enabled:
        msg = f"No INSURER_API_KEY was set. Generated a key for this run: {settings.api_key}"
        log.warning(msg)
        print(msg, flush=True)
    if not settings.auth_enabled:
        log.warning("INSURER_AUTH=off: the service needs no key. Use this only on a laptop.")

    app = FastAPI(title=f"{INSURER_NAME} (invented)", docs_url=None, redoc_url=None, openapi_url=None,
                  default_response_class=DemoJSONResponse)
    app.state.ctx = ctx
    app.add_middleware(DemoHeaderMiddleware)

    system_keys = {mod.KEY for mod in SYSTEMS}
    can_be_put_back = sorted(system_keys | set(events.SYSTEM_OF.values()))

    def owner_of(path: str) -> str:
        """The system a request's changes are put down to: the system in its path, or the system an arrival is for."""
        parts = [p for p in path.split("/") if p]
        for i, part in enumerate(parts):
            if part in system_keys:
                return part
            if part == "admin":
                if parts[i + 1:i + 2] == ["simulate"] and len(parts) > i + 2:
                    return events.SYSTEM_OF.get(parts[i + 2], "admin")
                return "admin"
        return "admin"

    app.add_middleware(WriteNotes, store=store, owner_of=owner_of)

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
        return {"status": "ok", "insurer": INSURER_NAME, "insurer_date": settings.insurer_today.isoformat()}

    # ------------------------------------------------------------ admin
    admin = APIRouter(prefix="/admin", dependencies=[Depends(make_auth(ctx))], include_in_schema=False)

    @admin.post("/reset")
    async def reset():
        store.reset()
        return {"applied": True, "message": "Back to the starting data.", "counts": store.counts()}

    @admin.post("/reset/{system}")
    async def reset_one(system: str):
        if system not in can_be_put_back:
            raise HTTPException(404, f"No system named {system}. Use one of: {', '.join(can_be_put_back)}. "
                                     "POST /admin/reset without a name puts everything back.")
        kinds = tuple(kind for kind, owner in events.SYSTEM_OF.items() if owner == system)
        put_back = store.reset_system(system, kinds)
        message = (f"Put back what {system} had changed. The rest of the insurer is as it was." if put_back
                   else f"{system} had changed nothing, so nothing was put back.")
        return {"applied": True, "system": system, "message": message, "put_back": put_back, "counts": store.counts()}

    @admin.get("/state")
    async def state():
        return {"insurer_date": settings.insurer_today.isoformat(), "auth_enabled": settings.auth_enabled,
                "data_dir_set": settings.data_dir is not None, "counts": store.counts(),
                "subscriptions": len(store.subscriptions),
                "changed_by": {name: rec["sets"] for name, rec in sorted(store.changed.items())}}

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
                    "(INSURER_AUTH=off).</b> Anyone who can reach this address can read and change the data. "
                    "Use this only on your own laptop.</p>")
        count_rows = "".join(f"<tr><td>{html.escape(k.replace('_', ' '))}</td><td>{v}</td></tr>" for k, v in counts.items())
        page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>{INSURER_NAME} (invented)</title>
<style>body{{font-family:system-ui,Segoe UI,Arial,sans-serif;max-width:60rem;margin:2rem auto;padding:0 1rem;line-height:1.5;color:#1b2430}}
table{{border-collapse:collapse;width:100%;margin:1rem 0}}td,th{{border:1px solid #c9d1dc;padding:6px 10px;text-align:left;vertical-align:top;font-size:.92rem}}
th{{background:#eef2f7}}code{{background:#eef2f7;padding:1px 4px}}</style></head><body>
<h1>{INSURER_NAME} (invented)</h1>
<p><b>{html.escape(INVENTED_NOTICE)}</b></p>
{warn}
<p>This service plays the back-office systems of an insurer so that AI agents have something realistic to read and act on.
Every JSON answer carries <code>"demo_data": true</code> and the header <code>X-Demo-Data: invented</code>.</p>
<p>Insurer date: <b>{settings.insurer_today.isoformat()}</b>. Data operations need a key in the <code>X-API-Key</code> header
(or <code>Authorization: Bearer ...</code>). The key is not shown here.</p>
<h2>The systems</h2>
<table><tr><th>System</th><th>API docs</th><th>OpenAPI document</th><th>MCP addresses</th></tr>{''.join(rows)}</table>
<h2>Open items</h2><table>{count_rows}</table>
<h2>Start again</h2>
<p>Send <code>POST {html.escape(root)}/admin/reset</code> with the key. This puts all data back to the starting point.
<code>POST {html.escape(root)}/admin/reset/&lt;system&gt;</code> puts back only what that one system has changed,
so several people can test against one insurer.
<code>POST {html.escape(root)}/admin/simulate/&lt;kind&gt;</code> makes one new item arrive
(kinds: {', '.join(events.KINDS)}).</p>
</body></html>"""
        return HTMLResponse(page)

    return app
