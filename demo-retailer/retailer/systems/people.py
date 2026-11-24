"""People, version 1.4: draft rosters for next week, the working time and staffing rules, and the checks saved on a roster."""

from __future__ import annotations

from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..seed_people import RULES
from ..store import now_iso

KEY = "people"
TITLE = "People"
LINE = ("Next week's draft rosters of four restaurants and two stores, with colleagues by id and role, the working time "
        "and staffing rules a roster is checked against, and the checks saved on each roster.")

ROSTER_ROW = ("roster_id, site_id, site_name, town, week_start, week_end, status (draft or published), colleagues, shifts and "
              "checks")
RULE = Literal["WT-1", "WT-2", "WT-3", "WT-4", "WT-5", "WT-6", "WT-7", "WT-8", "SR-1", "SR-2", "SR-3"]
DAY = Literal["", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
PER_SHIFT = ("WT-1", "WT-2", "WT-4", "WT-5", "WT-7")
PER_WEEK = ("WT-3", "WT-6", "WT-8")


class Breach(BaseModel):
    rule: RULE = Field(..., description="The number of the rule that is broken, as the rules write it: WT-1 to WT-8 for a "
                                        "working time rule, SR-1 to SR-3 for a staffing rule.")
    colleague_id: str = Field("", description="The id of the colleague the breach is about, for example C-01407. Needed for "
                                              "every working time rule. For a staffing rule it may be left empty, or name "
                                              "the one colleague who is on shift alone.")
    shift_id: str = Field("", description="The id of the shift the breach is on, for example SH-R014-17. Needed for WT-1, "
                                          "WT-2, WT-4, WT-5 and WT-7. For WT-2 it is the later of the two shifts, the one "
                                          "that starts too soon. Leave empty for a rule about the whole week.")
    day: DAY = Field("", description="The day the breach falls on, in lower case, monday to sunday. Needed for a staffing "
                                     "rule. Leave empty for a rule about the whole week.")
    what_the_roster_shows: str = Field(..., min_length=1, description="The figures of the breach in one plain sentence, for "
                                       "example '10 hours 30 minutes of rest between the two shifts'. No proposal and "
                                       "nothing about the colleague.")


class RosterCheck(BaseModel):
    breaches: list[Breach] = Field(default_factory=list, description="One entry for each breach of a rule. An empty list "
                                   "means the roster keeps every rule.")
    summary: str = Field("", description="A short summary in plain sentences. No change to the roster, no shift given to "
                                         "anyone and nothing about any colleague. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class PublishBody(BaseModel):
    published_by: str = Field(..., min_length=1, description="The name of the manager who publishes the roster.")
    note: str = Field("", description="An optional note, for example what was changed after the check.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds next week's draft rosters of four restaurants and two stores, and the "
                                  "working time and staffing rules a roster is checked against. Colleagues appear by id and "
                                  "role only. Saving a roster check is a draft: it lists breaches, it changes no shift and "
                                  "it gives no shift to anyone. The manager who owns the roster changes it and publishes it.")
    st = ctx.store
    d = lambda: st.data

    def roster_or_404(i):
        r = d()["draft_rosters"].get(i)
        if not r:
            raise not_found("draft roster", i, "Use list_draft_rosters to find roster ids.")
        return r

    roster_p = Path(..., description="Roster id, for example RS-261130-R014.")

    @reg(app, "get", "/rosters", "list_draft_rosters", "List next week's rosters",
         "List the rosters for next week, sorted by site id. Each row has roster_id, site_id, site_name, town, week_start "
         "and week_end (the Monday and the Sunday of the roster week), status (draft or published), colleagues and shifts "
         "(how many of each) and checks (how many checks are saved). The answer also has retailer_date. Filters are "
         "optional and add up: site_id and status. An unknown site_id is refused with 404. Read one roster with "
         "get_draft_roster.")
    def list_draft_rosters(site_id: str | None = Query(None, description="Only the roster of this site, for example R-014."),
                           status: Literal["draft", "published"] | None = Query(None, description="Only rosters with this status: draft or published.")):
        if site_id and site_id not in d()["sites"]:
            raise not_found("site", site_id, "Use list_sites in the stores system to find site ids.")
        rows = [{"roster_id": r["roster_id"], "site_id": r["site_id"], "site_name": r["site_name"], "town": r["town"],
                 "week_start": r["week_start"], "week_end": r["week_end"], "status": r["status"],
                 "colleagues": len(r["colleagues"]), "shifts": len(r["shifts"]), "checks": len(r["checks"])}
                for r in d()["draft_rosters"].values()
                if (not site_id or r["site_id"] == site_id) and (not status or r["status"] == status)]
        return listing(sorted(rows, key=lambda r: r["site_id"]), retailer_date=st.settings.retailer_today.isoformat())

    @reg(app, "get", "/rosters/{roster_id}", "get_draft_roster", "Get one roster with its colleagues and shifts",
         f"Read one roster: {ROSTER_ROW}, with opens and closes (the site's opening and closing time on every day, as "
         "HH:MM), rules_document, published_by and published_at. Each colleague has colleague_id, role (shift_manager or "
         "team_member), age_band (adult or young_worker), first_aider (true when the colleague holds a current first aid "
         "certificate), contracted_hours, rostered_hours (the hours of all the colleague's shifts in the week, each counted "
         "from start to end) and days_rostered. Each shift has shift_id, colleague_id, role, day (monday to sunday), date, "
         "start and end (HH:MM, on the same day), hours (from start to end) and break_minutes. Shifts are sorted by day, "
         "then by start. The roster does not give the rest between two shifts, who is on shift at a given time or which "
         "rule is broken: those are worked out from the shifts and the rules. No colleague is named. checks holds every "
         "saved check, each a version. Find the id with list_draft_rosters and the rules with get_working_time_rules.")
    def get_draft_roster(roster_id: str = roster_p):
        return roster_or_404(roster_id)

    @reg(app, "get", "/rules", "get_working_time_rules", "Get the working time and staffing rules",
         "Read the rules a roster is checked against: document, version, owner, notice, how_hours_and_times_are_counted, "
         "part_a and part_b (what each part of the document is), rules, what_the_rules_do_not_decide and text (the whole "
         "document). Each rule has rule (WT-1 to WT-8 are the working time rules of Meridia as the company states them, "
         "SR-1 to SR-3 are the company's own staffing rules), part (working_time or staffing), title, text, limit, unit and "
         "applies_to (every colleague, young workers, or the site). A figure exactly on a limit keeps the rule.")
    def get_working_time_rules():
        return RULES

    @reg(app, "post", "/rosters/{roster_id}/check", "save_roster_check", "Save the check of a roster (draft)",
         "Save the check of one roster against the rules, as a draft. It changes no shift, gives no shift to anyone and "
         "does not change the roster's status. Each call is kept as a new version with who wrote it and when. Send breaches "
         "(each with rule, colleague_id, shift_id, day and what_the_roster_shows; an empty list when the roster keeps every "
         "rule), an optional summary and drafted_by. rule is WT-1 to WT-8 or SR-1 to SR-3. A working time rule needs the "
         "colleague_id. WT-1, WT-2, WT-4, WT-5 and WT-7 need the shift_id as well, and the shift must be that colleague's. "
         "WT-3, WT-6 and WT-8 are about the whole week: leave shift_id and day empty. A staffing rule needs the day, and "
         "may name the one colleague on shift alone. A colleague or a shift that is not on this roster is refused with 422, "
         "and the message says what to correct. The body has no field for a change to the roster: the manager who owns "
         "the roster changes it. Returns the saved version.")
    def save_roster_check(body: RosterCheck, roster_id: str = roster_p):
        roster = roster_or_404(roster_id)
        people = {c["colleague_id"] for c in roster["colleagues"]}
        shifts = {s["shift_id"]: s for s in roster["shifts"]}
        for n, b in enumerate(body.breaches, start=1):
            where = f"Breach {n} ({b.rule})"
            if b.colleague_id and b.colleague_id not in people:
                raise HTTPException(422, f"{where}: {b.colleague_id} is not a colleague on roster {roster_id}. Nothing was "
                                         "saved. Use the colleague_id as the roster gives it.")
            if b.shift_id and b.shift_id not in shifts:
                raise HTTPException(422, f"{where}: {b.shift_id} is not a shift on roster {roster_id}. Nothing was saved. "
                                         "Use the shift_id as the roster gives it.")
            if b.rule.startswith("WT-") and not b.colleague_id:
                raise HTTPException(422, f"{where}: a working time rule needs the colleague_id. Nothing was saved.")
            if b.rule in PER_SHIFT and not b.shift_id:
                raise HTTPException(422, f"{where}: this rule is about one shift, so it needs the shift_id. Nothing was "
                                         "saved. For WT-2 give the later of the two shifts.")
            if b.rule in PER_WEEK and (b.shift_id or b.day):
                raise HTTPException(422, f"{where}: this rule is about the whole week. Leave shift_id and day empty. "
                                         "Nothing was saved.")
            if b.shift_id and b.colleague_id and shifts[b.shift_id]["colleague_id"] != b.colleague_id:
                raise HTTPException(422, f"{where}: shift {b.shift_id} belongs to {shifts[b.shift_id]['colleague_id']}, not "
                                         f"to {b.colleague_id}. Nothing was saved.")
            if b.rule.startswith("SR-") and not b.day:
                raise HTTPException(422, f"{where}: a staffing rule needs the day, monday to sunday. Nothing was saved.")
            if b.shift_id and b.day and shifts[b.shift_id]["day"] != b.day:
                raise HTTPException(422, f"{where}: shift {b.shift_id} is on {shifts[b.shift_id]['day']}, not on {b.day}. "
                                         "Nothing was saved.")
        payload = {"breaches": [b.model_dump() for b in body.breaches], "summary": body.summary}
        v = st.add_draft(roster, "checks", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "roster_id": roster_id}

    @reg(app, "post", "/rosters/{roster_id}/publish", "publish_roster", "Publish a roster (change)",
         "Publish one roster, so that colleagues see their shifts. This is the manager's decision: it needs published_by, "
         "the manager's name. It is refused with 409 until a check of the roster has been saved with save_roster_check, "
         "and when the roster is already published. Publishing changes the status to published and records who published "
         "it and when. It changes no shift: this system has no operation that changes a shift. Returns the roster's new "
         "status.")
    def publish_roster(body: PublishBody, roster_id: str = roster_p):
        roster = roster_or_404(roster_id)
        with st.lock:
            if roster["status"] == "published":
                raise conflict(f"Roster {roster_id} is already published, by {roster['published_by']}. Nothing was changed.")
            if not roster["checks"]:
                raise conflict(f"Roster {roster_id} has no saved check. Nothing was changed. Use save_roster_check first, "
                               "so that the manager publishes with the breaches in view.")
            roster["status"], roster["published_by"], roster["published_at"] = "published", body.published_by, now_iso()
            roster["publish_note"] = body.note
            st.save()
        return {"applied": True, "kind": "change", "roster_id": roster_id, "status": roster["status"],
                "published_by": roster["published_by"], "published_at": roster["published_at"]}

    return app
