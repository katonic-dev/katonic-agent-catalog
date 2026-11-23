"""Screening: sanctions and politically-exposed-person screening."""

from __future__ import annotations

import difflib
import re
from typing import Literal

from fastapi import Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..store import now_iso

KEY = "screening"
TITLE = "Screening"
LINE = "Sanctions and politically-exposed-person screening alerts and the watchlist."


class SearchBody(BaseModel):
    name: str = Field(..., min_length=1, description="Full name to screen.")
    date_of_birth: str = Field("", description="Date of birth YYYY-MM-DD. Leave empty if unknown.")
    country: str = Field("", description="Two-letter nationality code, for example XM. Leave empty if unknown.")


class FieldRow(BaseModel):
    field: str = Field(..., description="Field compared, for example date_of_birth.")
    customer_value: str = Field("", description="Value held for the customer.")
    list_value: str = Field("", description="Value on the list entry.")
    result: Literal["match", "differs", "unknown"] = Field(..., description="Outcome of the comparison.")


class Recommendation(BaseModel):
    recommendation: Literal["clear", "escalate"] = Field(..., description="Clear the alert, or escalate it to a person.")
    reasons: list[str] = Field(..., min_length=1, description="Reasons in plain sentences.")
    field_comparison: list[FieldRow] = Field(default_factory=list, description="Field by field comparison.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class CloseBody(BaseModel):
    disposition: Literal["false_positive", "true_match"] = Field(..., description="The decision.")
    decided_by: str = Field(..., min_length=1, description="Name of the person who decides.")
    note: str = Field(..., min_length=1, description="Reason for the decision.")


def _norm(s: str) -> str:
    return re.sub(r"[^a-z ]", "", s.lower()).strip()


def name_score(a: str, b: str) -> int:
    a, b = _norm(a), _norm(b)
    plain = difflib.SequenceMatcher(None, a, b).ratio()
    ta, tb = " ".join(sorted(a.split())), " ".join(sorted(b.split()))
    return round(100 * max(plain, difflib.SequenceMatcher(None, ta, tb).ratio()))


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds screening alerts against the Meridia Consolidated Demonstration List (invented).")
    st = ctx.store
    d = lambda: st.data
    alert_id = Path(..., description="Screening alert id, for example SCR-2001.")

    def alert_or_404(aid):
        a = d()["screening_alerts"].get(aid)
        if not a:
            raise not_found("screening alert", aid, "Use list_screening_alerts to find ids.")
        return a

    def row(a):
        c = d()["customers"][a["customer_id"]]
        e = d()["watchlist"][a["entry_id"]]
        return {"alert_id": a["alert_id"], "status": a["status"], "created": a["created"], "customer_id": c["customer_id"],
                "customer_name": c["name"], "entry_id": e["entry_id"], "entry_name": e["name"],
                "match_score": a["match_score"]}

    @reg(app, "get", "/alerts", "list_screening_alerts", "List screening alerts",
         "List screening alerts, newest first. Each row has alert_id, status (open or closed), created date, the customer, "
         "the matched list entry and the match score. Filter by status. Open alerts are the ones that need a decision.")
    def list_screening_alerts(status: Literal["open", "closed"] | None = Query(None, description="Only alerts with this status.")):
        rows = [row(a) for a in d()["screening_alerts"].values() if not status or a["status"] == status]
        rows.sort(key=lambda r: (r["created"], r["alert_id"]), reverse=True)
        return listing(rows)

    @reg(app, "get", "/alerts/{alert_id}", "get_screening_alert", "Get one screening alert in full",
         "Read one alert with the customer's fields and the matched list entry's fields side by side, the match score, which "
         "fields the matcher said matched, a field by field comparison (match, differs or unknown), earlier alerts on the same "
         "customer and entry with their outcome, drafted recommendations and the closing decision if any.")
    def get_screening_alert(alert_id: str = alert_id):
        a = alert_or_404(alert_id)
        c, e = d()["customers"][a["customer_id"]], d()["watchlist"][a["entry_id"]]

        def cmp(field, cv, lv):
            if cv in (None, "") or lv in (None, ""):
                res = "unknown"
            else:
                res = "match" if str(cv).lower() == str(lv).lower() else "differs"
            return {"field": field, "customer_value": cv, "list_value": lv, "result": res}

        comparison = [
            {"field": "name", "customer_value": c["name"], "list_value": e["name"],
             "result": "match" if _norm(c["name"]) == _norm(e["name"]) else "differs",
             "similarity": name_score(c["name"], e["name"]), "list_aliases": e["aliases"]},
            cmp("date_of_birth", c.get("date_of_birth"), e["date_of_birth"]),
            {"field": "year_of_birth", "customer_value": (c.get("date_of_birth") or "")[:4],
             "list_value": str(e["year_of_birth"] or ""),
             "result": "unknown" if not e["year_of_birth"] else
             ("match" if (c.get("date_of_birth") or "")[:4] == str(e["year_of_birth"]) else "differs")},
            cmp("nationality", c.get("nationality"), e["nationality"]),
            cmp("id_number", c.get("id_number"), e["id_number"]),
        ]
        earlier = [{k: x[k] for k in ("alert_id", "status", "created", "match_score", "closure")}
                   for x in d()["screening_alerts"].values()
                   if x["alert_id"] in a["earlier_alert_ids"]]
        return {**row(a), "screening_type": a["screening_type"], "matched_fields": a["matched_fields"],
                "customer_fields": {k: c.get(k) for k in ("name", "date_of_birth", "nationality", "nationality_name",
                                                           "id_number", "address", "risk_rating")},
                "list_entry_fields": e, "field_comparison": comparison, "earlier_alerts": earlier,
                "recommendations": a["recommendations"], "closure": a["closure"]}

    @reg(app, "get", "/watchlist/{entry_id}", "get_watchlist_entry", "Get a watchlist entry",
         "Read one entry of the Meridia Consolidated Demonstration List (invented): category (sanctions, pep), name, aliases, "
         "date or year of birth, nationality, identity number, reason listed and related persons.")
    def get_watchlist_entry(entry_id: str = Path(..., description="Watchlist entry id, for example WL-9001.")):
        e = d()["watchlist"].get(entry_id)
        if not e:
            raise not_found("watchlist entry", entry_id, "Entry ids appear in screening alerts and in screen_name results.")
        return e

    @reg(app, "post", "/search", "screen_name", "Screen a name against the watchlist",
         "Screen a name, with an optional date of birth and nationality code, against the watchlist. Returns hits with entry_id, "
         "name, score from 0 to 100 and, for each hit, which of date of birth and nationality agree. Only a read: nothing is stored.")
    def screen_name(body: SearchBody):
        hits = []
        for e in d()["watchlist"].values():
            best = max([name_score(body.name, e["name"])] + [name_score(body.name, x) for x in e["aliases"]])
            if best < 60:
                continue
            dob = "unknown" if not body.date_of_birth or not e["date_of_birth"] else (
                "match" if body.date_of_birth == e["date_of_birth"] else "differs")
            nat = "unknown" if not body.country or not e["nationality"] else (
                "match" if body.country.upper() == e["nationality"] else "differs")
            hits.append({"entry_id": e["entry_id"], "name": e["name"], "category": e["category"], "score": best,
                         "date_of_birth": dob, "nationality": nat})
        hits.sort(key=lambda h: -h["score"])
        return listing(hits, query=body.model_dump(), list_name="Meridia Consolidated Demonstration List (invented)")

    @reg(app, "post", "/alerts/{alert_id}/recommendation", "record_alert_recommendation",
         "Save a recommendation on an alert (draft)",
         "Save your recommendation (clear or escalate) with reasons and a field by field comparison. This is a draft: it is stored "
         "with who wrote it, a timestamp and a version number, earlier versions are kept, and the alert is NOT closed. A person "
         "closes the alert with close_screening_alert.")
    def record_alert_recommendation(body: Recommendation, alert_id: str = alert_id):
        a = alert_or_404(alert_id)
        if a["status"] == "closed":
            raise conflict(f"Alert {alert_id} is already closed. Nothing was changed.")
        v = st.add_draft(a, "recommendations", {"recommendation": body.recommendation, "reasons": body.reasons,
                                                "field_comparison": [r.model_dump() for r in body.field_comparison]},
                         body.drafted_by)
        return {"applied": True, "kind": "draft", "alert_status": a["status"], "draft": v}

    @reg(app, "post", "/alerts/{alert_id}/close", "close_screening_alert", "Close an alert with a decision (change)",
         "Close an alert as false_positive or true_match. This is a change and needs the name of the person who decides. "
         "Refused with 409 if the alert is already closed.")
    def close_screening_alert(body: CloseBody, alert_id: str = alert_id):
        a = alert_or_404(alert_id)
        with st.lock:
            if a["status"] == "closed":
                raise conflict(f"Alert {alert_id} is already closed as {a['closure']['disposition']}. Nothing was changed.")
            a["status"] = "closed"
            a["closure"] = {"disposition": body.disposition, "decided_by": body.decided_by, "note": body.note,
                            "closed_at": now_iso()}
            st.save()
        return {"applied": True, "kind": "change", "alert_id": alert_id, "status": "closed", "closure": a["closure"]}

    return app
