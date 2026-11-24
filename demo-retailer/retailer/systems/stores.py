"""Stores: the group's stores and restaurants, their areas, area managers and franchisees, and area manager visits."""

from __future__ import annotations

from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, listing, make_subapp, not_found, reg
from ..seed_visits import STANDARDS

KEY = "stores"
TITLE = "Stores"
LINE = ("The group's stores and restaurants: town, street, area, area manager and franchisee. Also the area managers' visits, "
        "with the checklist, the notes and the reports saved on them.")

SITE_FIELDS = "site_id, name, kind (store or restaurant), format, town, street, area, area_manager, franchised and franchisee"
PERIOD_RE = r"^\d{4}-(0[1-9]|1[0-2])$"
STANDARD_RE = r"^BS-\d\.\d$"
VISIT_ROW = "visit_id, site_id, site_name, town, date, time, area, area_manager, score, max_score, findings_on_checklist and reports"


class Finding(BaseModel):
    standard: str = Field(..., pattern=STANDARD_RE, description="The number of the brand standard the finding rests on, written "
                                                                "as on the checklist, for example BS-3.2.")
    source: Literal["checklist", "notes"] = Field(..., description="Where the finding comes from: an item of the checklist "
                                                                   "scored below 2, or the area manager's notes.")
    checklist_item: int = Field(0, ge=0, description="The item number on the checklist, when the source is checklist. 0 when "
                                                     "the source is notes.")
    what_was_found: str = Field(..., min_length=1, description="What the area manager found, in their own words or close to them.")


class VisitReport(BaseModel):
    findings: list[Finding] = Field(default_factory=list, description="One entry for each finding that rests on a standard. An "
                                    "empty list means the visit has none.")
    to_clarify: list[str] = Field(default_factory=list, description="Each point in the notes that is too vague to tie to a "
                                  "standard, in the area manager's own words. The area manager is asked what was meant.")
    summary: str = Field("", description="A short summary in plain sentences. No action, no deadline and nothing about any "
                                         "colleague. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds the group's sites: eight stores of Rowanmere Market and twelve restaurants "
                                  "of Rowanmere Kitchen. It also holds the area managers' visits to them. Saving a visit report "
                                  "is a draft: the area manager signs the report and owns the actions.")
    st = ctx.store
    d = lambda: st.data

    def visit_or_404(i):
        v = d()["site_visits"].get(i)
        if not v:
            raise not_found("visit", i, "Use list_site_visits to find visit ids.")
        return v

    visit_p = Path(..., description="Visit id, for example SV-2610-01.")

    @reg(app, "get", "/sites", "list_sites", "List stores and restaurants",
         f"List the group's sites, sorted by site id. Each row has {SITE_FIELDS}. Store ids start with S- and restaurant ids "
         "start with R-. franchised is true for a restaurant run by a franchisee, and then franchisee names the company. "
         "Every filter is optional and the filters add up. Use the site_id from here in the other systems.")
    def list_sites(kind: Literal["store", "restaurant"] | None = Query(None, description="Only this kind of site: store or restaurant."),
                   town: str | None = Query(None, description="Only sites in this town, for example Port Ilvane. Not case sensitive."),
                   franchised: bool | None = Query(None, description="true for franchised restaurants only, false for all the others.")):
        rows = [s for s in d()["sites"].values()
                if (kind is None or s["kind"] == kind)
                and (not town or s["town"].lower() == town.strip().lower())
                and (franchised is None or s["franchised"] == franchised)]
        return listing(sorted(rows, key=lambda s: s["site_id"]))

    @reg(app, "get", "/sites/{site_id}", "get_site", "Get one store or restaurant",
         f"Read one site: {SITE_FIELDS}. Find the id with list_sites, for example R-014 or S-101.")
    def get_site(site_id: str = Path(..., description="Site id, for example R-014 or S-101.")):
        site = d()["sites"].get(site_id)
        if not site:
            raise not_found("site", site_id, "Use list_sites to find site ids.")
        return site

    @reg(app, "get", "/visits", "list_site_visits", "List area manager visits",
         f"List the area managers' visits to stores and restaurants, oldest first. Each row has {VISIT_ROW}. "
         "findings_on_checklist is how many checklist items scored below 2, and reports is how many reports are saved. "
         "Filters are optional and add up: site_id and period (YYYY-MM, the month of the visit). An unknown site_id is "
         "refused with 404. Read the checklist and the notes with get_site_visit.")
    def list_site_visits(site_id: str | None = Query(None, description="Only visits to this site, for example R-047."),
                         period: str | None = Query(None, pattern=PERIOD_RE, description="Only visits made in this month, as YYYY-MM, for example 2026-10.")):
        if site_id and site_id not in d()["sites"]:
            raise not_found("site", site_id, "Use list_sites to find site ids.")
        keys = ("visit_id", "site_id", "site_name", "town", "date", "time", "area", "area_manager", "score", "max_score")
        rows = [{**{k: v[k] for k in keys}, "findings_on_checklist": sum(1 for x in v["checklist"] if x["score"] < x["max_score"]),
                 "reports": len(v["reports"])}
                for v in d()["site_visits"].values()
                if (not site_id or v["site_id"] == site_id) and (not period or v["date"].startswith(period))]
        return listing(sorted(rows, key=lambda v: (v["date"], v["visit_id"])))

    @reg(app, "get", "/visits/{visit_id}", "get_site_visit", "Get one visit with its checklist and notes",
         "Read one visit: visit_id, site_id, site_name, town, date, time, area, area_manager, standards_document (the brand "
         "standards the checklist rests on), checklist, score, max_score, notes and reports. Each checklist item has item_no, "
         "standard (the number of the brand standard, for example BS-3.2), item, score (2 met, 1 partly met, 0 not met), "
         "max_score and note. An item scored 1 or 0 is a finding. notes is the area manager's free text: some sentences are "
         "findings that rest on a standard, some are too vague to tie to one, and some are not findings at all. reports "
         "holds every saved report, each a version. This system does not hold the wording of the standards. Find the id with "
         "list_site_visits.")
    def get_site_visit(visit_id: str = visit_p):
        return visit_or_404(visit_id)

    @reg(app, "post", "/visits/{visit_id}/report", "save_visit_report", "Save the report of a visit (draft)",
         "Save the report of one visit, as a draft. It changes nothing in the visit. Each call is kept as a new version with "
         "who wrote it and when. Send findings (each with standard, source, checklist_item and what_was_found; an empty list "
         "when there is none), to_clarify (the points in the notes too vague to tie to a standard), an optional summary and "
         "drafted_by. standard is written as on the checklist, for example BS-3.2, and must be a standard of the brand "
         "standards. source is checklist or notes. A finding from the checklist names its item number, and its standard must "
         "be the one that item rests on. Anything else is refused with 422 and the message says what to correct. The area "
         "manager signs the report and owns the actions. Returns the saved version.")
    def save_visit_report(body: VisitReport, visit_id: str = visit_p):
        visit = visit_or_404(visit_id)
        items = {x["item_no"]: x for x in visit["checklist"]}
        for n, f in enumerate(body.findings, start=1):
            if f.standard not in STANDARDS:
                raise HTTPException(422, f"Finding {n}: {f.standard} is not a brand standard. Nothing was saved. The standards "
                                         f"are {', '.join(STANDARDS)}.")
            if f.source == "checklist":
                item = items.get(f.checklist_item)
                if not item:
                    raise HTTPException(422, f"Finding {n}: the checklist of visit {visit_id} has no item {f.checklist_item}. "
                                             f"Nothing was saved. Its items are numbered 1 to {len(items)}.")
                if item["standard"] != f.standard:
                    raise HTTPException(422, f"Finding {n}: checklist item {f.checklist_item} rests on {item['standard']}, not "
                                             f"on {f.standard}. Nothing was saved.")
            elif f.checklist_item:
                raise HTTPException(422, f"Finding {n}: a finding from the notes has checklist_item 0. Nothing was saved.")
        payload = {"findings": [f.model_dump() for f in body.findings], "to_clarify": list(body.to_clarify),
                   "summary": body.summary}
        v = st.add_draft(visit, "reports", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "visit_id": visit_id}

    return app
