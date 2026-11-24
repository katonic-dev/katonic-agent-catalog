"""One MCP door per system, generated from the system's own OpenAPI document.

Two transports are served for each system, so any client or gateway can use it:
  streamable HTTP : POST <system>/mcp   (stateless, JSON replies)
  SSE             : GET  <system>/sse   (then POST <system>/messages?session_id=...)
POST <system>/sse also answers stateless, because some gateways try a plain POST first.
The tool list is built from the OpenAPI document, so names and descriptions cannot drift.
"""

from __future__ import annotations

import asyncio
import json
import re
import uuid
from contextvars import ContextVar
from typing import Any
from urllib.parse import quote, urlencode

from fastapi import FastAPI, Request
from starlette.responses import Response, StreamingResponse

from .common import Ctx, public_scheme, DemoJSONResponse, KEY_HEADER, key_is_valid
from .config import INVENTED_NOTICE

SUPPORTED = ["2024-11-05", "2025-03-26", "2025-06-18", "2025-11-25"]
METHODS = ("get", "post", "put", "patch", "delete")
# where the caller reached us, so a tool that returns an address (news page_url) gives one the caller can open
_caller: ContextVar[dict] = ContextVar("mcp_caller", default={})


def _resolve(doc: dict, node: Any, depth: int = 0) -> Any:
    if depth > 8 or not isinstance(node, (dict, list)):
        return node
    if isinstance(node, list):
        return [_resolve(doc, x, depth + 1) for x in node]
    if "$ref" in node:
        target: Any = doc
        for part in node["$ref"].lstrip("#/").split("/"):
            target = target[part]
        return _resolve(doc, target, depth + 1)
    if "allOf" in node and len(node["allOf"]) == 1:
        rest = {k: v for k, v in node.items() if k != "allOf"}
        return {**_resolve(doc, node["allOf"][0], depth + 1), **rest}
    return {k: _resolve(doc, v, depth + 1) for k, v in node.items()}


def build_tools(doc: dict) -> dict[str, dict]:
    """operationId -> {tool, method, path, path_params, query_params, body_props}."""
    tools = {}
    for path, item in doc["paths"].items():
        for method in METHODS:
            op = item.get(method)
            if not op:
                continue
            props: dict = {}
            required: list = []
            pp, qp = [], []
            for p in op.get("parameters", []):
                p = _resolve(doc, p)
                sch = {k: v for k, v in _resolve(doc, p.get("schema", {})).items() if k != "nullable"}
                sch["description"] = p.get("description", "")
                props[p["name"]] = sch
                (pp if p["in"] == "path" else qp).append(p["name"])
                if p.get("required"):
                    required.append(p["name"])
            body_props: list = []
            body = op.get("requestBody")
            if body:
                schema = _resolve(doc, body["content"]["application/json"]["schema"])
                for k, v in schema.get("properties", {}).items():
                    props[k] = v
                    body_props.append(k)
                required += [k for k in schema.get("required", []) if k not in required]
            input_schema = {"type": "object", "properties": props}
            if required:
                input_schema["required"] = required
            tools[op["operationId"]] = {
                "tool": {"name": op["operationId"], "title": op["summary"], "description": op["description"],
                         "inputSchema": input_schema},
                "method": method, "path": path, "path_params": pp, "query_params": qp, "body_props": body_props}
    return tools


async def call_asgi(app: Any, method: str, path: str, query: str, body: bytes, headers: dict[str, str],
                    scheme: str = "http"):
    scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": method.upper(),
             "scheme": scheme, "path": path, "raw_path": path.encode(), "query_string": query.encode(),
             "root_path": "", "headers": [(k.lower().encode(), v.encode()) for k, v in headers.items()],
             "server": ("internal", 80), "client": ("internal", 0), "state": {}}
    sent = {"done": False}
    out: dict = {"status": 500, "body": b""}

    async def receive():
        if not sent["done"]:
            sent["done"] = True
            return {"type": "http.request", "body": body, "more_body": False}
        await asyncio.sleep(3600)
        return {"type": "http.disconnect"}

    async def send(message):
        if message["type"] == "http.response.start":
            out["status"] = message["status"]
        elif message["type"] == "http.response.body":
            out["body"] += message.get("body", b"")

    await app(scope, receive, send)
    return out["status"], out["body"]


def install_mcp(app: FastAPI, ctx: Ctx) -> None:
    system = app.state.system_key
    summary_line = app.state.summary_line
    cache: dict = {}
    sessions: dict[str, asyncio.Queue] = {}

    def tools() -> dict:
        if "t" not in cache:
            cache["t"] = build_tools(app.openapi())
        return cache["t"]

    async def run_tool(name: str, args: dict) -> dict:
        spec = tools().get(name)
        if not spec:
            raise KeyError(name)
        path = spec["path"]
        for p in spec["path_params"]:
            if p not in args:
                return {"isError": True, "content": [{"type": "text", "text": f"Missing argument {p}."}]}
            path = path.replace("{" + p + "}", quote(str(args[p]), safe=""))
        query = urlencode([(k, args[k]) for k in spec["query_params"] if args.get(k) is not None])
        body_args = {k: args[k] for k in spec["body_props"] if k in args}
        headers = {"content-type": "application/json"}
        if ctx.settings.auth_enabled:
            headers[KEY_HEADER] = ctx.settings.api_key
        payload = json.dumps(body_args).encode() if spec["method"] in ("post", "put", "patch") else b""
        caller = _caller.get()
        if caller.get("host"):
            headers["x-public-root-path"] = caller.get("root_path", "")
            headers["host"] = caller["host"]
        status, raw = await call_asgi(app, spec["method"], path, query, payload, headers,
                                      scheme=caller.get("scheme", "http"))
        text = raw.decode("utf-8", "replace")
        if status >= 400:
            try:
                text = json.loads(text).get("detail", text)
            except ValueError:
                pass
            return {"isError": True, "content": [{"type": "text", "text": f"HTTP {status}: {text}"}]}
        return {"content": [{"type": "text", "text": text}]}

    async def handle(msg: dict) -> dict | None:
        method, mid, params = msg.get("method"), msg.get("id"), msg.get("params") or {}
        if mid is None:  # notification
            return None

        def ok(result):
            return {"jsonrpc": "2.0", "id": mid, "result": result}

        def err(code, text):
            return {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": text}}

        if method == "initialize":
            asked = params.get("protocolVersion")
            return ok({"protocolVersion": asked if asked in SUPPORTED else SUPPORTED[-1],
                       "capabilities": {"tools": {"listChanged": False}},
                       "serverInfo": {"name": f"rowanmere-group-{system}", "version": "1.1.0"},
                       "instructions": f"{INVENTED_NOTICE} {summary_line}"})
        if method == "ping":
            return ok({})
        if method == "tools/list":
            return ok({"tools": [t["tool"] for t in tools().values()]})
        if method == "tools/call":
            name = params.get("name", "")
            if name not in tools():
                return err(-32602, f"Unknown tool {name}")
            return ok(await run_tool(name, params.get("arguments") or {}))
        return err(-32601, f"Method not found: {method}")

    def denied() -> Response:
        return DemoJSONResponse({"detail": "A valid key is needed. Send it in the X-API-Key header or as "
                                           "'Authorization: Bearer <key>'."}, status_code=401)

    def note_caller(request: Request) -> None:
        _caller.set({"host": request.headers.get("host", ""), "scheme": public_scheme(request),
                     "root_path": request.scope.get("root_path", "")})

    async def rpc_post(request: Request) -> Response:
        if not key_is_valid(ctx, request):
            return denied()
        note_caller(request)
        try:
            data = await request.json()
        except ValueError:
            return DemoJSONResponse({"detail": "Body is not JSON."}, status_code=400)
        if isinstance(data, list):
            replies = [r for r in [await handle(m) for m in data] if r]
            if not replies:
                return Response(status_code=202)
            return Response(json.dumps(replies), media_type="application/json")
        reply = await handle(data)
        if reply is None:
            return Response(status_code=202)
        return Response(json.dumps(reply), media_type="application/json")

    async def mcp_other(request: Request) -> Response:
        if request.method == "DELETE":
            return Response(status_code=200)
        return Response("Use POST for streamable HTTP, or GET /sse for the SSE transport.", status_code=405,
                        headers={"Allow": "POST, DELETE"})

    async def sse_get(request: Request) -> Response:
        if not key_is_valid(ctx, request):
            return denied()
        note_caller(request)
        sid = uuid.uuid4().hex
        q: asyncio.Queue = asyncio.Queue()
        sessions[sid] = q
        root = request.scope.get("root_path", "").rstrip("/")

        async def stream():
            try:
                yield f"event: endpoint\ndata: {root}/messages?session_id={sid}\n\n"
                idle = 0
                while True:
                    try:
                        item = await asyncio.wait_for(q.get(), timeout=1)
                    except asyncio.TimeoutError:
                        if await request.is_disconnected():
                            return
                        idle += 1
                        if idle % 15 == 0:
                            yield ": ping\n\n"
                        continue
                    yield f"event: message\ndata: {json.dumps(item)}\n\n"
            finally:
                sessions.pop(sid, None)

        return StreamingResponse(stream(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    async def messages_post(request: Request) -> Response:
        if not key_is_valid(ctx, request):
            return denied()
        note_caller(request)
        q = sessions.get(request.query_params.get("session_id", ""))
        if q is None:
            return DemoJSONResponse({"detail": "Unknown or closed session. Open /sse again."}, status_code=404)
        try:
            data = await request.json()
        except ValueError:
            return DemoJSONResponse({"detail": "Body is not JSON."}, status_code=400)
        for m in (data if isinstance(data, list) else [data]):
            reply = await handle(m)
            if reply:
                await q.put(reply)
        return Response("Accepted", status_code=202)

    app.add_route("/mcp", rpc_post, methods=["POST"], include_in_schema=False)
    app.add_route("/mcp", mcp_other, methods=["GET", "DELETE"], include_in_schema=False)
    app.add_route("/sse", sse_get, methods=["GET"], include_in_schema=False)
    app.add_route("/sse", rpc_post, methods=["POST"], include_in_schema=False)
    app.add_route("/messages", messages_post, methods=["POST"], include_in_schema=False)
