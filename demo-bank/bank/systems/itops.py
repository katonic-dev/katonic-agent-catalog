"""IT operations: incidents, monitoring metrics, dashboards, recent changes and runbooks. It reads and drafts. It never changes a service."""

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..seed_itops import MEASURE_NOTES, NOW_TIME, UNITS

KEY = "itops"
TITLE = "IT operations"
LINE = "Incidents, monitoring metrics, dashboards, recent changes and runbooks. It never runs a runbook step or changes a service."


class Assessment(BaseModel):
    what_is_happening: str = Field(..., min_length=1, description="What is happening now, in plain sentences, with the times that matter.")
    likely_cause: str = Field(..., min_length=1, description="The most likely cause. Say if it is not yet known.")
    evidence_for: list[str] = Field(default_factory=list, description="Each fact that supports the likely cause, with the record or measure it came from.")
    evidence_against: list[str] = Field(default_factory=list, description="Each fact that weighs against it, or the checks that could still prove it wrong.")
    next_checks: list[str] = Field(default_factory=list, description="What to check next, in order. These are checks to read, not steps to run.")
    customer_impact: str = Field("", description="What customers experience and how many are affected, if the data shows it.")
    confidence: str = Field("medium", description="How sure you are: low, medium or high.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class TimelineEntry(BaseModel):
    time: str = Field(..., min_length=1, description="When it happened, as YYYY-MM-DDTHH:MM.")
    event: str = Field(..., min_length=1, description="What happened, in one plain sentence.")


class ReviewAction(BaseModel):
    action: str = Field(..., min_length=1, description="The action that would stop this happening again, in one plain sentence.")
    owner: str = Field("", description="Leave empty. A person assigns the owner.")
    due: str = Field("", description="Leave empty. A person sets the date.")


class PostIncidentReview(BaseModel):
    timeline: list[TimelineEntry] = Field(..., min_length=1, description="The timeline from first cause to close, in time order.")
    root_cause: str = Field(..., min_length=1, description="The root cause, in plain sentences. Say what was first assumed and why that was wrong, if it was.")
    what_went_well: list[str] = Field(default_factory=list, description="What went well.")
    what_did_not: list[str] = Field(default_factory=list, description="What did not go well.")
    actions: list[ReviewAction] = Field(default_factory=list, description="Actions to stop it happening again. Owners stay empty.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds IT incidents, monitoring metrics, dashboards, change records and runbooks. It only reads and keeps drafts. "
                                  "There is no operation that runs a runbook step or changes a system.")
    st = ctx.store
    d = lambda: st.data
    inc_p = Path(..., description="Incident id, for example INC-7001.")

    def now() -> datetime:
        return datetime.fromisoformat(f"{ctx.settings.bank_today.isoformat()}T{NOW_TIME}")

    def inc_or_404(i):
        x = d()["itops_incidents"].get(i)
        if not x:
            raise not_found("incident", i, "Use list_incidents to find ids.")
        return x

    @reg(app, "get", "/incidents", "list_incidents", "List incidents",
         "List incidents: incident_id, title, status (open or closed), severity, when it opened, the alert that raised it and the services affected. "
         "Filter by status. Start here to see what needs attention, then read one with get_incident.")
    def list_incidents(status: str = Query("", description="Only incidents with this status: open or closed. Leave empty for all.")):
        keys = ("incident_id", "title", "status", "severity", "opened_at", "alert_id", "services_affected")
        rows = [{k: i[k] for k in keys} for i in d()["itops_incidents"].values() if not status or i["status"] == status]
        rows.sort(key=lambda r: (r["opened_at"], r["incident_id"]), reverse=True)
        return listing(rows)

    @reg(app, "get", "/incidents/{incident_id}", "get_incident", "Get one incident in full",
         "Read one incident: what was reported and when, the alert that raised it, the services affected, the timeline so far (who did what and when), "
         "the linked change records in full, the resolution note if it is closed, and any saved assessments and post-incident reviews. It does not hold "
         "metrics: read them with get_service_metrics.")
    def get_incident(incident_id: str = inc_p):
        i = inc_or_404(incident_id)
        changes = [d()["itops_changes"][c] for c in i["linked_change_ids"]]
        return {**{k: v for k, v in i.items() if k != "linked_change_ids"}, "linked_changes": changes,
                "service_clock": f"{ctx.settings.bank_today.isoformat()}T{NOW_TIME}"}

    @reg(app, "get", "/metrics", "get_service_metrics", "Get metrics of a service",
         "Read the monitoring metrics of one service: for each measure (error rate, 95th percentile latency, volume and others) the unit, what it means, "
         "the time series (time and value), a summary (first, minimum, maximum, latest) and any gap where samples are missing. Filter by date or time "
         "with date_from and date_to, written as YYYY-MM-DD or YYYY-MM-DDTHH:MM. Some measures come from the monitoring collector and some from the "
         "service's own log: the description of each measure says which.")
    def get_service_metrics(service: str = Query(..., description="The service name, for example payment-service."),
                            date_from: str = Query("", description="First time to include, YYYY-MM-DD or YYYY-MM-DDTHH:MM. Leave empty for no limit."),
                            date_to: str = Query("", description="Last time to include, YYYY-MM-DD or YYYY-MM-DDTHH:MM. Leave empty for no limit.")):
        all_series = d()["itops_metrics"].get(service)
        if not all_series:
            raise not_found("service", service, "Services with metrics: " + ", ".join(sorted(d()["itops_metrics"])) + ".")
        out = {}
        for measure, pts in all_series.items():
            sel = [p for p in pts if (not date_from or p["time"] >= date_from) and (not date_to or p["time"][:len(date_to)] <= date_to)]
            vals = [p["value"] for p in sel]
            gaps = []
            if len(pts) > 2:
                tt = [datetime.fromisoformat(p["time"]) for p in pts]
                diffs = sorted((b - a).total_seconds() / 60 for a, b in zip(tt, tt[1:]))
                step = diffs[len(diffs) // 2]
                for a, b, p, q in zip(tt, tt[1:], pts, pts[1:]):
                    minutes = (b - a).total_seconds() / 60
                    if minutes > 1.5 * step and p in sel and q in sel:
                        gaps.append({"last_sample_before": p["time"], "next_sample_after": q["time"], "minutes_without_data": int(minutes)})
            out[measure] = {"unit": UNITS.get(measure, ""), "meaning": MEASURE_NOTES.get(measure, ""),
                            "points": sel, "gaps": gaps,
                            "summary": ({"first": vals[0], "minimum": min(vals), "maximum": max(vals), "latest": vals[-1]} if vals else {})}
        return {"service": service, "date_from": date_from, "date_to": date_to, "measures": out}

    @reg(app, "get", "/dashboards/{dashboard_id}", "get_dashboard_snapshot", "Get a dashboard snapshot",
         "Read a snapshot of a monitoring dashboard as it stands now: each panel with its latest value, the time of that sample, the thresholds and a status "
         "(ok, warning, critical, no data). The certificate dashboard lists every certificate with its expiry time and whether it has expired. "
         "Dashboards: DASH-1001 payments health, DASH-1002 card authorisation health, DASH-1003 certificate expiry, DASH-1004 statement service.")
    def get_dashboard_snapshot(dashboard_id: str = Path(..., description="Dashboard id, for example DASH-1001.")):
        dash = d()["itops_dashboards"].get(dashboard_id)
        if not dash:
            raise not_found("dashboard", dashboard_id, "Dashboards: " + ", ".join(sorted(d()["itops_dashboards"])) + ".")
        as_of = now()
        panels = []
        for p in dash["panels"]:
            if p["kind"] == "certificates":
                rows = []
                for c in d()["itops_certificates"]:
                    left = datetime.fromisoformat(c["expires_at"]) - as_of
                    state = "expired" if left.total_seconds() <= 0 else ("expires within 30 days" if left.days < 30 else "valid")
                    rows.append({**c, "status": state, "days_left": left.days if left.total_seconds() > 0 else 0})
                panels.append({"title": p["title"], "kind": "certificates", "rows": rows})
                continue
            pts = [q for q in d()["itops_metrics"].get(p["service"], {}).get(p["measure"], []) if datetime.fromisoformat(q["time"]) <= as_of]
            if not pts:
                panels.append({"title": p["title"], "service": p["service"], "measure": p["measure"], "status": "no data"})
                continue
            last = pts[-1]
            status = "ok"
            if p["crit"] and last["value"] >= p["crit"]:
                status = "critical"
            elif p["warn"] and last["value"] >= p["warn"]:
                status = "warning"
            panels.append({"title": p["title"], "service": p["service"], "measure": p["measure"], "unit": UNITS.get(p["measure"], ""),
                           "latest_value": last["value"], "latest_sample_time": last["time"], "warning_at": p["warn"], "critical_at": p["crit"],
                           "status": status})
        return {"dashboard_id": dashboard_id, "title": dash["title"], "as_of": as_of.isoformat(timespec="minutes"), "panels": panels}

    @reg(app, "get", "/changes", "list_recent_changes", "List recent changes",
         "List change records implemented in the last N hours before now: change_id, service, title, type, when it was implemented, who did it, who "
         "approved it, the plan time if it differed, the description and any note. Filter by service. An empty list means no change was made in that "
         "window, which is itself evidence. Use a larger number of hours to look back further.")
    def list_recent_changes(service: str = Query("", description="Only changes to this service, for example payment-service. Leave empty for all."),
                            hours: int = Query(24, ge=1, le=720, description="How many hours back from now to look. 24 is one day, 168 is one week.")):
        cutoff = now() - timedelta(hours=hours)
        rows = [c for c in d()["itops_changes"].values()
                if (not service or c["service"] == service) and cutoff <= datetime.fromisoformat(c["implemented_at"]) <= now()]
        rows.sort(key=lambda c: (c["implemented_at"], c["change_id"]), reverse=True)
        return {"count": len(rows), "from": cutoff.isoformat(timespec="minutes"), "to": now().isoformat(timespec="minutes"), "service": service, "items": rows}

    @reg(app, "get", "/runbooks/{service}", "get_runbook", "Get the runbook of a service",
         "Read the runbook of a service: the numbered steps an on-call engineer follows, and who may run each step. Some steps need the approval of the "
         "incident manager or the change manager. This system cannot run any step: it only tells you what the runbook says.")
    def get_runbook(service: str = Path(..., description="The service name, for example payment-service.")):
        r = d()["itops_runbooks"].get(service)
        if not r:
            raise not_found("runbook", service, "Runbooks exist for: " + ", ".join(sorted(d()["itops_runbooks"])) + ".")
        return r

    @reg(app, "post", "/incidents/{incident_id}/assessment", "save_incident_assessment", "Save an incident assessment (draft)",
         "Save your assessment of an open incident: what is happening, the likely cause with the evidence for and against, what to check next and the "
         "customer impact. This is a draft: stored with who wrote it, a timestamp and a version number, earlier versions kept. It changes no service. "
         "Refused with 409 if the incident is closed.")
    def save_incident_assessment(body: Assessment, incident_id: str = inc_p):
        i = inc_or_404(incident_id)
        if i["status"] == "closed":
            raise conflict(f"Incident {incident_id} is closed. Write a post-incident review with save_post_incident_review instead. Nothing was changed.")
        v = st.add_draft(i, "assessments", {k: val for k, val in body.model_dump().items() if k != "drafted_by"}, body.drafted_by)
        return {"applied": True, "kind": "draft", "incident_status": i["status"], "draft": v}

    @reg(app, "post", "/incidents/{incident_id}/review", "save_post_incident_review", "Save a post-incident review (draft)",
         "Save your post-incident review of a closed incident: the timeline, the root cause, what went well, what did not, and the actions with the owner "
         "left empty for a person to assign. This is a draft: stored with who wrote it, a timestamp and a version number, earlier versions kept. "
         "Refused with 409 if the incident is not closed yet, and with 422 if an action names an owner.")
    def save_post_incident_review(body: PostIncidentReview, incident_id: str = inc_p):
        i = inc_or_404(incident_id)
        if i["status"] != "closed":
            raise conflict(f"Incident {incident_id} is still {i['status']}. A review is written after it is closed. Use save_incident_assessment now. Nothing was changed.")
        if any(a.owner.strip() or a.due.strip() for a in body.actions):
            raise HTTPException(422, "Leave owner and due empty on every action. A person assigns them.")
        v = st.add_draft(i, "reviews", {k: val for k, val in body.model_dump().items() if k != "drafted_by"}, body.drafted_by)
        return {"applied": True, "kind": "draft", "incident_status": i["status"], "draft": v}

    return app
