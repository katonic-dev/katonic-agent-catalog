"""Food safety: the plan, the monthly records of each restaurant, and the monthly review."""

from __future__ import annotations

from typing import Literal

from fastapi import Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..store import now_iso

KEY = "foodsafety"
TITLE = "Food safety"
LINE = "The food safety plan, each restaurant's monthly temperature, cleaning and delivery records, and the monthly review."

PERIOD_RE = r"^\d{4}-(0[1-9]|1[0-2])$"
SITE_P = Path(..., description="Restaurant id, for example R-014. list_record_periods shows which restaurants have records.")
PERIOD_P = Path(..., pattern=PERIOD_RE, description="Month as YYYY-MM, for example 2026-10.")


class Reading(BaseModel):
    date: str = Field(..., description="Date of the reading as YYYY-MM-DD.")
    time: str = Field("", description="Time of the reading, for example 16:00. Leave empty if the log has no time.")
    value: float | None = Field(None, description="The reading in degrees Celsius. Leave it out when the check was not made or "
                                                  "the entry is missing.")
    note: str = Field("", description="Anything else about the reading, for example MISSED or no signed entry.")


class CheckRow(BaseModel):
    unit_or_check: str = Field(..., description="The equipment or the check, as the plan names it, for example Hot holding cabinet "
                                                "or Daily cleaning schedule.")
    plan_section: str = Field(..., description="The plan reference that sets the limit, for example 3.2. get_food_safety_plan lists them.")
    limit: str = Field(..., description="The limit as the plan writes it, for example 63.0 °C or hotter.")
    readings: list[Reading] = Field(default_factory=list, description="The readings that are outside the limit or missing, "
                                    "each with its date and value. Leave the list empty for a row marked within_plan.")
    mark: Literal["repeated_deviation", "outside_limit", "missing_entry", "missed_check", "within_plan"] = Field(
        ..., description="repeated_deviation: three or more readings outside the limit on the same equipment in the period "
                         "(plan section 6.2). outside_limit: one or two readings outside the limit. missing_entry: no signed "
                         "entry. missed_check: the check was recorded as not made. within_plan: nothing outside the plan.")
    note: str = Field("", description="Anything else the reviewer should know about this row.")


class CheckDraft(BaseModel):
    rows: list[CheckRow] = Field(..., min_length=1, description="One row for each equipment or check that was looked at.")
    proposed_next_step: Literal["sign_review", "ask_for_corrective_actions", "refer_to_food_safety_lead"] = Field(
        ..., description="What the drafter proposes for the whole month. sign_review: nothing outside the plan. "
                         "ask_for_corrective_actions: there are deviations. refer_to_food_safety_lead: the repeat rule applies. "
                         "A person decides.")
    summary: str = Field("", description="A short summary in plain sentences. Optional.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class RequestActions(BaseModel):
    requested_by: str = Field(..., min_length=1, description="The person who asks the restaurant for corrective actions. Free text.")
    note: str = Field(..., min_length=1, description="What the restaurant manager is asked to do, in plain sentences.")
    items: list[str] = Field(default_factory=list, description="The equipment or checks that need an answer, as the plan names them. "
                                                               "Optional.")


class ActionAnswer(BaseModel):
    unit_or_check: str = Field(..., min_length=1, description="The equipment or check this answer is for, as the plan names it.")
    what_was_done: str = Field(..., min_length=1, description="What was done with the food and the equipment, and who was told.")
    done_by: str = Field(..., min_length=1, description="The restaurant manager or colleague who did it. Free text.")
    done_on: str = Field(..., description="The date it was done, as YYYY-MM-DD.")


class SignBody(BaseModel):
    signed_by: str = Field(..., min_length=1, description="The person who signs the monthly review, normally the area manager.")
    note: str = Field("", description="Optional note kept with the signature.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds the food safety plan, the monthly records of the restaurants and the review of "
                                  "each month. Saving a check is a draft. Asking for corrective actions, recording one and "
                                  "signing the review change a record.")
    st = ctx.store
    d = lambda: st.data

    def records_or_404(site_id, period):
        rec = d()["fs_records"].get(f"{site_id}:{period}")
        if not rec:
            raise not_found("records for site and period", f"{site_id} / {period}",
                            "Use list_record_periods to see which restaurant and period have records.")
        return rec

    def review_of(site_id, period):
        records_or_404(site_id, period)
        return d()["fs_reviews"][f"{site_id}:{period}"]

    def view(rev):
        site = d()["sites"][rev["site_id"]]
        return {**rev, "site_name": site["name"], "area_manager": site["area_manager"], "plan_version": d()["food_plan"]["version"]}

    @reg(app, "get", "/plan", "get_food_safety_plan", "Get the food safety plan",
         "Read version 5.0 of the food safety plan as data. Fields: plan_id, version, effective_date, owner; limits (a list: ref, "
         "unit_or_check, section, limit as text, minimum and maximum in degrees Celsius, how_often, recorded_in, and log_columns, "
         "the columns of the temperature or delivery log that the limit applies to); repeat_rule (section 6.2: three or more readings "
         "outside the limit on the same equipment in the period are reported to the food safety lead); deviation (what counts as "
         "one); what_the_plan_does_not_decide (sections 1.3, 7.1 and 7.2: whether food was safe is for people to decide); and "
         "sections with the text of every clause. Read it before you check any records.")
    def get_food_safety_plan():
        return d()["food_plan"]

    @reg(app, "get", "/records", "list_record_periods", "List restaurants and months that have records",
         "List which restaurant and month have food safety records, newest month first. Each row has site_id, site_name, period "
         "(YYYY-MM), review_status (not_reviewed, corrective_actions_requested or signed), days_recorded and deliveries_recorded. "
         "Use site_id and period with get_food_safety_records.")
    def list_record_periods(site_id: str | None = Query(None, description="Only this restaurant, for example R-014.")):
        rows = []
        for key, rec in d()["fs_records"].items():
            if site_id and rec["site_id"] != site_id:
                continue
            rows.append({"site_id": rec["site_id"], "site_name": d()["sites"][rec["site_id"]]["name"], "period": rec["period"],
                         "review_status": d()["fs_reviews"][key]["status"], "days_recorded": len(rec["temperature_log"]),
                         "deliveries_recorded": len(rec["delivery_log"])})
        rows.sort(key=lambda r: (r["site_id"], r["period"]))
        rows.sort(key=lambda r: r["period"], reverse=True)
        return listing(rows)

    @reg(app, "get", "/records/{site_id}/{period}", "get_food_safety_records", "Get a restaurant's records for a month",
         "Read one restaurant's records for one month. Fields: site_id, period, temperature_log (one row a day: date, "
         "walk_in_chiller_opening_c, walk_in_chiller_afternoon_c, make_line_chiller_opening_c, make_line_chiller_afternoon_c, "
         "freezer_opening_c, hot_holding_12h_c, hot_holding_14h_c, hot_holding_16h_c, hot_holding_18h_c, hot_holding_20h_c, "
         "chicken_core_first_batch_am_c, chicken_core_first_batch_pm_c, and daily_cleaning_signed_by) and delivery_log (date, "
         "chilled_item_c, frozen_item_c, outcome). A blank daily_cleaning_signed_by means no signed entry. The word MISSED in a "
         "reading means the check was recorded as not made. Compare every value with the limits from get_food_safety_plan.")
    def get_food_safety_records(site_id: str = SITE_P, period: str = PERIOD_P):
        return records_or_404(site_id, period)

    @reg(app, "get", "/reviews/{site_id}/{period}", "get_record_review", "Get the review of a restaurant's month",
         "Read the review of one restaurant's month. Fields: status (not_reviewed, corrective_actions_requested or signed), checks "
         "(every saved check, each a version with version number, drafted_by, drafted_at, rows, proposed_next_step and summary), "
         "corrective_actions_request (who asked, when, and the note) , corrective_actions (the restaurant manager's answers: "
         "action_id, unit_or_check, what_was_done, done_by, done_on), signed_by and signed_at, plus site_name and area_manager.")
    def get_record_review(site_id: str = SITE_P, period: str = PERIOD_P):
        return view(review_of(site_id, period))

    @reg(app, "post", "/reviews/{site_id}/{period}/checks", "save_record_check", "Save a check of a month's records (draft)",
         "Save the result of checking one restaurant's month against the plan, as a draft. It changes no status. Each call is "
         "kept as a new version with who wrote it and when. Send rows (each with unit_or_check, plan_section, limit, readings, "
         "mark and note), a proposed_next_step for the whole month, an optional summary, and drafted_by. A person decides what "
         "happens next. Returns the saved version.")
    def save_record_check(body: CheckDraft, site_id: str = SITE_P, period: str = PERIOD_P):
        rev = review_of(site_id, period)
        payload = {"rows": [r.model_dump() for r in body.rows], "proposed_next_step": body.proposed_next_step,
                   "summary": body.summary}
        v = st.add_draft(rev, "checks", payload, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v, "review_status": rev["status"]}

    @reg(app, "post", "/reviews/{site_id}/{period}/corrective-actions/request", "request_corrective_actions",
         "Ask the restaurant for corrective actions (change)",
         "Ask the restaurant manager for corrective actions on a month's deviations. This is a change: the review status becomes "
         "corrective_actions_requested. Needs requested_by and a note. items is an optional list of the equipment or checks. "
         "Refused with 409 if the review is already signed or the actions were already requested.")
    def request_corrective_actions(body: RequestActions, site_id: str = SITE_P, period: str = PERIOD_P):
        rev = review_of(site_id, period)
        with st.lock:
            if rev["status"] == "signed":
                raise conflict(f"The review of {site_id} for {period} is already signed by {rev['signed_by']}. Nothing was changed.")
            if rev["status"] == "corrective_actions_requested":
                raise conflict(f"Corrective actions for {site_id} and {period} were already requested. Nothing was changed.")
            rev["status"] = "corrective_actions_requested"
            rev["corrective_actions_request"] = {"requested_by": body.requested_by, "requested_at": now_iso(),
                                                 "note": body.note, "items": list(body.items)}
            st.save()
        return {"applied": True, "kind": "change", "status": rev["status"], "review": view(rev)}

    @reg(app, "post", "/reviews/{site_id}/{period}/corrective-actions", "record_corrective_action",
         "Record a corrective action (change)",
         "Record the restaurant manager's answer for one row: what was done, by whom and when. This is a change. Needs "
         "unit_or_check, what_was_done, done_by and done_on (YYYY-MM-DD). Refused with 409 if corrective actions were not "
         "requested for this month or the review is already signed. Returns the new action with its id.")
    def record_corrective_action(body: ActionAnswer, site_id: str = SITE_P, period: str = PERIOD_P):
        rev = review_of(site_id, period)
        with st.lock:
            if rev["status"] == "signed":
                raise conflict(f"The review of {site_id} for {period} is already signed. Nothing was changed.")
            if rev["status"] != "corrective_actions_requested":
                raise conflict(f"Corrective actions were not requested for {site_id} and {period}. Nothing was changed. "
                               "Use request_corrective_actions first.")
            action = {"action_id": f"CA-{st.next_number('corrective_action', 1):04d}", "unit_or_check": body.unit_or_check,
                      "what_was_done": body.what_was_done, "done_by": body.done_by, "done_on": body.done_on,
                      "recorded_at": now_iso()}
            rev["corrective_actions"].append(action)
            st.save()
        return {"applied": True, "kind": "change", "corrective_action": action, "status": rev["status"]}

    @reg(app, "post", "/reviews/{site_id}/{period}/sign", "sign_monthly_review", "Sign the monthly review (change)",
         "Sign the review of one restaurant's month. This is a change: the status becomes signed. Needs signed_by. Refused with 409 "
         "while corrective actions are requested and none is recorded, and when the review is already signed.")
    def sign_monthly_review(body: SignBody, site_id: str = SITE_P, period: str = PERIOD_P):
        rev = review_of(site_id, period)
        with st.lock:
            if rev["status"] == "signed":
                raise conflict(f"The review of {site_id} for {period} is already signed by {rev['signed_by']}. Nothing was changed.")
            if rev["status"] == "corrective_actions_requested" and not rev["corrective_actions"]:
                raise conflict(f"Corrective actions were requested for {site_id} and {period} and none is recorded yet. "
                               "Nothing was changed. Use record_corrective_action first.")
            rev.update(status="signed", signed_by=body.signed_by, signed_at=now_iso(), sign_note=body.note)
            st.save()
        return {"applied": True, "kind": "change", "status": "signed", "review": view(rev)}

    return app
