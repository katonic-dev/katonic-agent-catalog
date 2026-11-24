"""Stores: the group's stores and restaurants, their areas, area managers and franchisees, area manager visits,
and from version 1.4 the shift logs and the incident accounts."""

from __future__ import annotations

from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..seed_visits import STANDARDS
from ..store import now_iso

KEY = "stores"
TITLE = "Stores"
LINE = ("The group's stores and restaurants: town, street, area, area manager and franchisee. Also the area managers' visits, "
        "with the checklist, the notes and the reports saved on them, the shift log of a site for a day with the handover "
        "notes saved on it, and colleagues' accounts of accidents and incidents with the report forms saved on them.")

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


DATE_RE = r"^\d{4}-\d{2}-\d{2}$"
TIME_RE = r"^(([01]\d|2[0-3]):[0-5]\d)?$"
LOG_ROW = "site_id, site_name, town, date, retailer_date, entries and handover_notes"
ACCOUNT_ROW = ("account_id, site_id, site_name, town, incident_date, written_at, written_by (a colleague id), written_by_role, "
               "status (account_received or report_submitted) and reports")


class HandoverItem(BaseModel):
    entry_id: str = Field(..., min_length=1, description="The id of the log entry the line rests on, as the log gives it, "
                                                         "for example LE-R014-1123-09.")
    text: str = Field(..., min_length=1, description="What the entry says, in one or two plain sentences. Nothing the entry "
                                                     "does not say.")


class HandoverNote(BaseModel):
    what_happened: list[HandoverItem] = Field(default_factory=list, description="The entries of the day worth telling the "
                                              "next shift about, each with the entry it rests on. Routine entries may be "
                                              "left out.")
    still_open: list[HandoverItem] = Field(default_factory=list, description="One line for each entry that is not finished at "
                                           "the end of the day. An empty list means the log leaves nothing open.")
    do_first: list[HandoverItem] = Field(default_factory=list, description="The open entries that need doing first, in order, "
                                         "each with the time the entry gives. Every entry here is also in still_open. An "
                                         "empty list means the log gives no time for any open entry.")
    summary: str = Field("", description="A short summary in plain sentences. Nothing that is not in the log. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class NextStep(BaseModel):
    clause: Literal["15.1", "15.2", "15.3"] = Field(..., description="The clause of procedure SP-15 that sets the step: "
                                                                     "15.1, 15.2 or 15.3.")
    step: str = Field(..., min_length=1, description="What the clause says must happen, and who does it, in the procedure's "
                                                     "own terms.")


class IncidentReport(BaseModel):
    incident_type: Literal["fall", "burn", "cut", "guest_illness", "near_miss", "property_damage", "other"] = Field(
        ..., description="What kind of incident the account describes. fall covers a slip or a trip that ends in a fall. "
                         "guest_illness covers any report of a guest or a customer becoming ill, an allergic reaction "
                         "included. near_miss is an incident in which nobody was hurt and nothing was damaged beyond stock.")
    who_was_affected: Literal["crew_member", "guest", "nobody", "other"] = Field(
        ..., description="Who was hurt or became ill: crew_member (a colleague), guest (a guest or a customer), nobody, or "
                         "other (for example a driver or a contractor).")
    incident_date: str = Field(..., pattern=DATE_RE, description="The date of the incident as YYYY-MM-DD: the incident_date "
                                                                 "of the account.")
    incident_time: str = Field("", pattern=TIME_RE, description="The time of the incident as HH:MM, when the account gives "
                                                                "one. Empty when it does not.")
    location: str = Field(..., min_length=1, description="Where on the site it happened, in the account's words.")
    what_happened: str = Field(..., min_length=1, description="What happened, in plain sentences taken from the account. No "
                                                              "cause the account does not give and no view on who was at fault.")
    injury_or_damage: str = Field("", description="The injury, the illness or the damage as the account describes it. Empty "
                                                  "when the account describes none.")
    first_aid_given: Literal["yes", "no", "not_said"] = Field(..., description="Whether first aid was given: yes, no, or "
                                                                               "not_said when the account does not say.")
    reported_to_shift_manager: Literal["yes", "no", "not_said"] = Field(
        ..., description="Whether the shift manager or duty manager was told: yes (also when a shift manager wrote the "
                         "account), no, or not_said when the account does not say.")
    area_manager_to_be_phoned_the_same_day: bool = Field(
        ..., description="true when clause 15.2 of the procedure requires a phone call to the area manager the same day for "
                         "this kind of incident, false when it does not.")
    next_steps: list[NextStep] = Field(..., min_length=1, description="What procedure SP-15 says must happen next, one entry "
                                       "for each step, each with its clause.")
    not_in_the_account: list[str] = Field(default_factory=list, description="Each thing the form or the procedure needs that "
                                          "the account does not give, for example the time of the incident or the guest's "
                                          "contact details.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class SubmitBody(BaseModel):
    submitted_by: str = Field(..., min_length=1, description="The name of the manager who submits the report.")
    note: str = Field("", description="An optional note.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds the group's sites: eight stores of Rowanmere Market and twelve restaurants "
                                  "of Rowanmere Kitchen. It also holds the area managers' visits to them. Saving a visit report "
                                  "is a draft: the area manager signs the report and owns the actions. From version 1.4 it "
                                  "holds the shift log of a site for a day, and colleagues' accounts of accidents and "
                                  "incidents. A handover note and an incident report are drafts. The outgoing manager "
                                  "checks the note, and a manager submits the report: safety decisions are theirs.")
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

    # ------------------------------------------------------------ version 1.4: shift logs
    def log_or_error(site_id: str, log_date: str | None) -> dict:
        if site_id not in d()["sites"]:
            raise not_found("site", site_id, "Use list_sites to find site ids.")
        own = sorted((x for x in d()["shift_logs"].values() if x["site_id"] == site_id), key=lambda x: x["date"])
        if not own:
            held = sorted({x["site_id"] for x in d()["shift_logs"].values()})
            raise not_found("shift log for site", site_id, f"The sites with a shift log are {', '.join(held)}.")
        if not log_date:
            return own[-1]
        for x in own:
            if x["date"] == log_date:
                return x
        raise not_found(f"shift log for site {site_id} on", log_date,
                        f"{site_id} has a shift log for {', '.join(x['date'] for x in own)}.")

    site_log_p = Path(..., description="Site id, for example R-014 or S-101.")
    log_date_q = Query(None, pattern=DATE_RE, description="The day of the log as YYYY-MM-DD, for example 2026-11-23. Leave "
                                                          "it out for the latest log the site has.")

    @reg(app, "get", "/shift-logs/{site_id}", "get_shift_log", "Get a site's shift log for a day",
         f"Read the shift log of one site for one day: {LOG_ROW}. Each entry has entry_id, time (HH:MM), category (routine, "
         "delivery, equipment_fault, complaint, cash_difference, staffing_gap or task), logged_by (a colleague id), "
         "logged_by_role and text (what the colleague wrote). Entries are in the order of the day. Most entries are "
         "finished business. The log does not say which entries are still open or what comes first: that is read from the "
         "text of each entry. handover_notes holds every saved note, each a version. log_date is optional: without it the "
         "answer is the latest log the site has, which at the start is the day before the retailer date. A site with no "
         "log, or a day with no log, answers 404 and the message says what is held. Find site ids with list_sites.")
    def get_shift_log(site_id: str = site_log_p, log_date: str | None = log_date_q):
        return {**log_or_error(site_id, log_date), "retailer_date": st.settings.retailer_today.isoformat()}

    @reg(app, "post", "/shift-logs/{site_id}/handover-note", "save_handover_note", "Save a handover note for the next shift (draft)",
         "Save a handover note on one site's shift log, as a draft. It changes no entry of the log. Each call is kept as a "
         "new version with who wrote it and when. Send what_happened, still_open and do_first (each a list of lines with "
         "entry_id and text), an optional summary and drafted_by. Every line rests on an entry of that log: an entry_id the "
         "log does not hold is refused with 422, so a note cannot hold something the log does not. Every entry under "
         "do_first must also be under still_open. An empty still_open means the log leaves nothing open. log_date is "
         "optional and works as in get_shift_log. The outgoing manager checks and signs the note. Returns the saved version.")
    def save_handover_note(body: HandoverNote, site_id: str = site_log_p, log_date: str | None = log_date_q):
        log = log_or_error(site_id, log_date)
        held = {e["entry_id"] for e in log["entries"]}
        for name in ("what_happened", "still_open", "do_first"):
            for n, item in enumerate(getattr(body, name), start=1):
                if item.entry_id not in held:
                    raise HTTPException(422, f"{name}, line {n}: {item.entry_id} is not an entry of the shift log of "
                                             f"{site_id} for {log['date']}. Nothing was saved. Its entries are "
                                             f"{log['entries'][0]['entry_id']} to {log['entries'][-1]['entry_id']}.")
        open_ids = {item.entry_id for item in body.still_open}
        for n, item in enumerate(body.do_first, start=1):
            if item.entry_id not in open_ids:
                raise HTTPException(422, f"do_first, line {n}: {item.entry_id} is not under still_open. Nothing was saved. "
                                         "An entry that needs doing first is an open entry: list it under still_open as well.")
        payload = {"what_happened": [x.model_dump() for x in body.what_happened],
                   "still_open": [x.model_dump() for x in body.still_open],
                   "do_first": [x.model_dump() for x in body.do_first], "summary": body.summary}
        v = st.add_draft(log, "handover_notes", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "site_id": site_id, "date": log["date"]}

    # ------------------------------------------------------------ version 1.4: incident accounts
    def account_or_404(i):
        a = d()["incident_accounts"].get(i)
        if not a:
            raise not_found("incident account", i, "Use list_incident_accounts to find account ids.")
        return a

    account_p = Path(..., description="Incident account id, for example IA-2611-01.")

    @reg(app, "get", "/incident-accounts", "list_incident_accounts", "List colleagues' accounts of accidents and incidents",
         f"List the accounts colleagues have written of accidents and incidents, newest first. Each row has {ACCOUNT_ROW} "
         "(how many report forms are saved). Filters are optional and add up: site_id and status. An unknown site_id is "
         "refused with 404. Read the account itself with get_incident_account.")
    def list_incident_accounts(site_id: str | None = Query(None, description="Only accounts from this site, for example R-031."),
                               status: Literal["account_received", "report_submitted"] | None = Query(
                                   None, description="Only accounts with this status: account_received or report_submitted.")):
        if site_id and site_id not in d()["sites"]:
            raise not_found("site", site_id, "Use list_sites to find site ids.")
        keys = ("account_id", "site_id", "site_name", "town", "incident_date", "written_at", "written_by", "written_by_role", "status")
        rows = [{**{k: a[k] for k in keys}, "reports": len(a["reports"])} for a in d()["incident_accounts"].values()
                if (not site_id or a["site_id"] == site_id) and (not status or a["status"] == status)]
        return listing(sorted(rows, key=lambda a: (a["incident_date"], a["account_id"]), reverse=True))

    @reg(app, "get", "/incident-accounts/{account_id}", "get_incident_account", "Get one account of an accident or incident",
         "Read one account: account_id, site_id, site_name, town, incident_date, written_at (HH:MM, when the colleague wrote "
         "it), written_by (a colleague id), written_by_role, account (the colleague's own words, free text), procedure (the "
         "procedure the report form follows: SP-15 of the Store Procedures Manual), status (account_received until a "
         "manager submits a report, then report_submitted), reports (every saved report form, each a version), submitted_by "
         "and submitted_at. No colleague and no guest is named. This system does not hold the wording of the procedure. It "
         "does not say what kind of incident this is or what must happen next: that is read from the account and the "
         "procedure. Find the id with list_incident_accounts.")
    def get_incident_account(account_id: str = account_p):
        return account_or_404(account_id)

    @reg(app, "post", "/incident-accounts/{account_id}/report", "save_incident_report", "Save the report form of an incident (draft)",
         "Save the incident report form for one account, as a draft. It changes nothing in the account and it submits "
         "nothing. Each call is kept as a new version with who wrote it and when. Send incident_type (fall, burn, cut, "
         "guest_illness, near_miss, property_damage or other), who_was_affected (crew_member, guest, nobody or other), "
         "incident_date (the account's date), incident_time (HH:MM, or empty when the account gives none), location, "
         "what_happened, injury_or_damage, first_aid_given and reported_to_shift_manager (each yes, no or not_said), "
         "area_manager_to_be_phoned_the_same_day (true or false, as clause 15.2 of the procedure requires), next_steps "
         "(each with clause 15.1, 15.2 or 15.3 and the step), not_in_the_account and drafted_by. Refused with 422 when "
         "incident_date is not the date of the account, when the area manager is to be phoned and no step cites clause "
         "15.2, and when a guest was affected and no step cites clause 15.3. The message says what to correct. The form "
         "holds no decision about safety and no view on who was at fault: a manager submits it. Returns the saved version.")
    def save_incident_report(body: IncidentReport, account_id: str = account_p):
        account = account_or_404(account_id)
        cited = {x.clause for x in body.next_steps}
        if body.incident_date != account["incident_date"]:
            raise HTTPException(422, f"incident_date: account {account_id} is dated {account['incident_date']}, not "
                                     f"{body.incident_date}. Nothing was saved.")
        if body.area_manager_to_be_phoned_the_same_day and "15.2" not in cited:
            raise HTTPException(422, "next_steps: the area manager is to be phoned the same day, and no step cites clause "
                                     "15.2, which sets that call. Nothing was saved. Add the step with clause 15.2.")
        if body.who_was_affected == "guest" and "15.3" not in cited:
            raise HTTPException(422, "next_steps: a guest was affected, and no step cites clause 15.3, which says what is "
                                     "said to a guest and what is taken from them. Nothing was saved. Add the step with "
                                     "clause 15.3.")
        payload = body.model_dump(exclude={"drafted_by"})
        v = st.add_draft(account, "reports", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "account_id": account_id}

    @reg(app, "post", "/incident-accounts/{account_id}/submit", "submit_incident_report", "Submit an incident report (change)",
         "Submit the incident report of one account. This is the manager's decision: it needs submitted_by, the manager's "
         "name. It is refused with 409 until a report form has been saved for the account with save_incident_report, and "
         "when a report is already submitted. Submitting changes the status to report_submitted and records who submitted "
         "it, when, and which version of the form. Returns the account's new status.")
    def submit_incident_report(body: SubmitBody, account_id: str = account_p):
        account = account_or_404(account_id)
        with st.lock:
            if account["status"] == "report_submitted":
                raise conflict(f"The report of account {account_id} is already submitted, by {account['submitted_by']}. "
                               "Nothing was changed.")
            if not account["reports"]:
                raise conflict(f"No report form is saved for account {account_id}. Nothing was changed. Use "
                               "save_incident_report first.")
            account.update(status="report_submitted", submitted_by=body.submitted_by, submitted_at=now_iso(),
                           submitted_version=account["reports"][-1]["version"], submit_note=body.note)
            st.save()
        return {"applied": True, "kind": "change", "account_id": account_id, "status": account["status"],
                "submitted_by": account["submitted_by"], "submitted_version": account["submitted_version"]}

    return app
