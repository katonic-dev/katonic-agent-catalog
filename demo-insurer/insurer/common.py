"""Shared pieces for the systems: app factory, sign-in, responses, OpenAPI 3.0.3 conversion."""

from __future__ import annotations

import copy
import hmac
import os
from dataclasses import dataclass
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, Security
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader

try:  # offline docs when the package is installed, otherwise no docs UI at all
    from fastapi_offline import FastAPIOffline
except ImportError:  # pragma: no cover
    FastAPIOffline = None

from .config import INVENTED_NOTICE, Settings
from .store import Store

KEY_HEADER = "X-API-Key"
OPENAPI_VERSION = "3.0.3"


@dataclass
class Ctx:
    settings: Settings
    store: Store


class DemoJSONResponse(JSONResponse):
    """JSON responses always say the data is invented."""

    def render(self, content: Any) -> bytes:
        if isinstance(content, dict):
            content = {"demo_data": True, **content}
        return super().render(content)


def public_scheme(request: Request) -> str:
    """The scheme the visitor used.

    INSURER_PUBLIC_SCHEME wins when it is set to http or https: some gateways end the
    secure connection before the last proxy, and then every header says http.
    Otherwise the first X-Forwarded-Proto value if present, else the request's own.
    """
    forced = os.environ.get("INSURER_PUBLIC_SCHEME", "").strip().lower()
    if forced in ("http", "https"):
        return forced
    fwd = request.headers.get("x-forwarded-proto", "").split(",")[0].strip().lower()
    return fwd if fwd in ("http", "https") else request.url.scheme


def extract_key(request: Request) -> str:
    key = request.headers.get(KEY_HEADER, "").strip()
    if key:
        return key
    auth = request.headers.get("authorization", "").strip()
    if auth.lower().startswith("bearer "):
        return auth[7:].strip()
    return ""


def key_is_valid(ctx: Ctx, request: Request) -> bool:
    if not ctx.settings.auth_enabled:
        return True
    supplied = extract_key(request)
    return bool(supplied) and hmac.compare_digest(supplied.encode(), ctx.settings.api_key.encode())


def make_auth(ctx: Ctx):
    scheme = APIKeyHeader(
        name=KEY_HEADER, auto_error=False, scheme_name="ApiKeyAuth",
        description="The service key. Send it in the X-API-Key header. "
                    "The header 'Authorization: Bearer <key>' is accepted as well.")

    async def require_key(request: Request, _key: str | None = Security(scheme)) -> None:
        if not key_is_valid(ctx, request):
            raise HTTPException(status_code=401, detail="A valid key is needed. Send it in the X-API-Key header "
                                                        "or as 'Authorization: Bearer <key>'.")

    return require_key


def not_found(kind: str, ident: str, hint: str = "") -> HTTPException:
    return HTTPException(404, f"No {kind} with id {ident}. {hint}".strip())


def conflict(message: str) -> HTTPException:
    return HTTPException(409, message)


def listing(items: list, **extra) -> dict:
    return {"count": len(items), "items": items, **extra}


# ---------------------------------------------------------------- OpenAPI 3.0.3

def _schema(node: Any) -> Any:
    """Convert one JSON Schema (3.1 style) to the OpenAPI 3.0 dialect."""
    if not isinstance(node, dict):
        return node
    s = {k: v for k, v in node.items() if k != "title"}
    nullable = False
    if "anyOf" in s:
        variants = s.pop("anyOf")
        non_null = [v for v in variants if v != {"type": "null"}]
        nullable = len(non_null) != len(variants)
        if len(non_null) == 1:
            only = _schema(non_null[0])
            if "$ref" in only:
                s["allOf"] = [only]
            else:
                s = {**only, **s}
        elif non_null:
            s["anyOf"] = [_schema(v) for v in non_null]
    if isinstance(s.get("type"), list):
        kinds = [t for t in s["type"] if t != "null"]
        nullable = nullable or len(kinds) != len(s["type"])
        s["type"] = kinds[0] if kinds else "string"
    if "const" in s:
        s["enum"] = [s.pop("const")]
    if "examples" in s:
        ex = s.pop("examples")
        if isinstance(ex, list) and ex:
            s["example"] = ex[0]
    for key, flag in (("exclusiveMinimum", "minimum"), ("exclusiveMaximum", "maximum")):
        if isinstance(s.get(key), (int, float)) and not isinstance(s.get(key), bool):
            s[flag] = s.pop(key)
            s[key] = True
    for key in ("contentMediaType", "contentEncoding", "$schema", "prefixItems"):
        s.pop(key, None)
    if isinstance(s.get("properties"), dict):
        s["properties"] = {k: _schema(v) for k, v in s["properties"].items()}
    if "items" in s:
        s["items"] = _schema(s["items"])
    if isinstance(s.get("additionalProperties"), dict):
        s["additionalProperties"] = _schema(s["additionalProperties"])
    for key in ("allOf", "oneOf", "anyOf"):
        if key in s:
            s[key] = [_schema(v) for v in s[key]]
    if nullable:
        s["nullable"] = True
    return s


def to_openapi_303(raw: dict) -> dict:
    doc = copy.deepcopy(raw)
    doc["openapi"] = OPENAPI_VERSION
    doc.pop("jsonSchemaDialect", None)
    comps = doc.get("components", {})
    schemas = comps.get("schemas", {})
    for name in ("HTTPValidationError", "ValidationError"):
        schemas.pop(name, None)
    for name, sch in list(schemas.items()):
        schemas[name] = _schema(sch)
    for path_item in doc.get("paths", {}).values():
        for op in path_item.values():
            if not isinstance(op, dict):
                continue
            for p in op.get("parameters", []):
                if "schema" in p:
                    p["schema"] = _schema(p["schema"])
            body = op.get("requestBody")
            if body:
                for media in body.get("content", {}).values():
                    if "schema" in media:
                        media["schema"] = _schema(media["schema"])
            responses = op.get("responses", {})
            responses.pop("422", None)
            for resp in responses.values():
                for media in resp.get("content", {}).values():
                    media["schema"] = {"type": "object"}
    if not schemas:
        comps.pop("schemas", None)
    return doc


# ---------------------------------------------------------------- app factory

def make_subapp(ctx: Ctx, *, key: str, title: str, summary_line: str, description: str) -> FastAPI:
    """One system of the insurer: its own FastAPI app, OpenAPI document and docs page."""
    kwargs = dict(
        title=f"Thornmere Mutual Insurance (invented): {title}",
        version="1.0.0",
        description=f"{INVENTED_NOTICE} {description}",
        default_response_class=DemoJSONResponse,
        openapi_url="/openapi.json",
    )
    if FastAPIOffline is not None:
        app = FastAPIOffline(**kwargs)
    else:
        app = FastAPI(docs_url=None, redoc_url=None, **kwargs)
    app.state.system_key = key
    app.state.auth = make_auth(ctx)
    app.state.summary_line = summary_line
    cache: dict = {}

    def openapi() -> dict:
        if "doc" not in cache:
            raw = get_openapi(title=app.title, version=app.version, openapi_version="3.1.0",
                              description=app.description, routes=app.routes)
            cache["doc"] = to_openapi_303(raw)
        return cache["doc"]

    app.openapi = openapi  # type: ignore[method-assign]

    @app.exception_handler(HTTPException)
    async def _http_error(_: Request, exc: HTTPException):
        return DemoJSONResponse({"detail": exc.detail, "applied": False}, status_code=exc.status_code,
                                headers=getattr(exc, "headers", None))

    @app.exception_handler(RequestValidationError)
    async def _validation_error(_: Request, exc: RequestValidationError):
        problems = [f"{'.'.join(str(x) for x in e['loc'])}: {e['msg']}" for e in exc.errors()]
        return DemoJSONResponse({"detail": "The request is not valid. " + "; ".join(problems), "applied": False},
                                status_code=422)

    return app




def reg(app: FastAPI, method: str, path: str, op: str, summary: str, description: str):
    """Register one operation with a clean operationId, summary and description."""
    return getattr(app, method)(path, operation_id=op, summary=summary, description=description,
                                dependencies=[Depends(app.state.auth)],
                                response_description="JSON object. The field list is in the description.")
