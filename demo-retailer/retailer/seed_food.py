"""Food safety: the plan (version 5.0), the monthly records of the restaurants, and the review of each month.

The planted faults are written out here, restaurant by restaurant. Every other reading is drawn inside the plan's limits.
"""

from __future__ import annotations

import random
from datetime import date

from .seed_base import days_in, period_of
from .seed_stores import EXTRA_RESTAURANT_IDS

MANAGERS = ["shift manager A", "shift manager B", "closing manager C"]
DELIVERY_DAYS = [2, 6, 9, 13, 16, 20, 23, 27, 30]
HOT_TIMES = ["12:00", "14:00", "16:00", "18:00", "20:00"]

TEMPERATURE_COLUMNS = [
    "date", "walk_in_chiller_opening_c", "walk_in_chiller_afternoon_c", "make_line_chiller_opening_c",
    "make_line_chiller_afternoon_c", "freezer_opening_c", "hot_holding_12h_c", "hot_holding_14h_c", "hot_holding_16h_c",
    "hot_holding_18h_c", "hot_holding_20h_c", "chicken_core_first_batch_am_c", "chicken_core_first_batch_pm_c",
    "daily_cleaning_signed_by"]
DELIVERY_COLUMNS = ["date", "chilled_item_c", "frozen_item_c", "outcome"]

# --------------------------------------------------------------------------- the plan

_LIMITS = [
    ("2.1", "Walk-in chiller and reach-in chillers", "2", "Cold storage", "1.0 °C to 5.0 °C", 1.0, 5.0,
     "Twice a day: at opening, and between 15:00 and 17:00", "Temperature log",
     ["walk_in_chiller_opening_c", "walk_in_chiller_afternoon_c", "make_line_chiller_opening_c",
      "make_line_chiller_afternoon_c"]),
    ("2.2", "Freezers", "2", "Cold storage", "−18.0 °C or colder", None, -18.0,
     "Once a day, at opening", "Temperature log", ["freezer_opening_c"]),
    ("3.1", "Cooked chicken, core temperature", "3", "Cooking and hot holding", "75.0 °C or hotter", 75.0, None,
     "First batch of each shift", "Temperature log", ["chicken_core_first_batch_am_c", "chicken_core_first_batch_pm_c"]),
    ("3.2", "Hot holding cabinet", "3", "Cooking and hot holding", "63.0 °C or hotter", 63.0, None,
     "Every two hours while holding food", "Temperature log",
     ["hot_holding_12h_c", "hot_holding_14h_c", "hot_holding_16h_c", "hot_holding_18h_c", "hot_holding_20h_c"]),
    ("4.1", "Chilled delivery", "4", "Deliveries", "5.0 °C or colder", None, 5.0,
     "One item per delivery", "Delivery log", ["chilled_item_c"]),
    ("4.2", "Frozen delivery", "4", "Deliveries", "−15.0 °C or colder", None, -15.0,
     "One item per delivery", "Delivery log", ["frozen_item_c"]),
    ("5.1", "Daily cleaning schedule", "5", "Cleaning", "One signed entry for each day the restaurant trades", None, None,
     "Every trading day, signed by the closing manager", "Temperature log", ["daily_cleaning_signed_by"]),
    ("5.2", "Weekly deep clean", "5", "Cleaning", "One entry in each calendar week, signed by the restaurant manager", None, None,
     "Once a week", "Cleaning schedule (not part of the monthly records served here)", []),
]

_SECTIONS = [
    ("1", "Scope", [
        ("1.1", "This plan sets the checks every restaurant must make and record, how often, and the limit for each."),
        ("1.2", "A reading outside a limit, or a check that was not made, is a deviation. Every deviation needs a corrective "
                "action recorded by the restaurant manager and reviewed by the food safety lead."),
        ("1.3", "Whether food was safe after a deviation is decided by the restaurant manager and the food safety lead. "
                "No record and no report decides that.")]),
    ("2", "Cold storage", [
        ("2.1", None), ("2.2", None),
        ("2.3", "A chiller reading above 5.0 °C is a deviation. A second reading is taken after 15 minutes. If the second "
                "reading is above 8.0 °C the restaurant manager is called before any food from that unit is used.")]),
    ("3", "Cooking and hot holding", [
        ("3.1", None), ("3.2", None),
        ("3.3", "A hot holding reading below 63.0 °C is a deviation. Food that has been below 63.0 °C for more than two hours "
                "is discarded; the restaurant manager decides.")]),
    ("4", "Deliveries", [
        ("4.1", None), ("4.2", None),
        ("4.3", "An item outside its limit is refused and the refusal is written on the delivery note.")]),
    ("5", "Cleaning", [
        ("5.1", "The daily cleaning schedule has one entry for each day the restaurant trades, signed by the closing manager."),
        ("5.2", "The weekly deep clean has one entry in each calendar week, signed by the restaurant manager."),
        ("5.3", "A day with no signed daily entry is a deviation.")]),
    ("6", "Corrective actions", [
        ("6.1", "Every deviation is given a corrective action by the restaurant manager within 24 hours: what was done with "
                "the food, what was done with the equipment, and who was told."),
        ("6.2", "Three or more readings outside the limit on the same unit in one calendar month are reported to the food safety lead, who decides whether the unit is taken out of use until it is serviced. A check that was not made and a day with no signed entry are deviations under 6.1, and are not counted here."),
        ("6.3", "The area manager reviews each restaurant's records every month and signs the review.")]),
    ("7", "What this plan does not decide", [
        ("7.1", "This plan does not say whether any particular food was safe. That is a judgement for the restaurant manager "
                "and the food safety lead."),
        ("7.2", "This plan does not cover allergens. See the Allergen Matrix.")]),
]


def build_plan() -> dict:
    limits = [{"ref": ref, "unit_or_check": unit, "section": ref, "section_number": sec, "section_title": title,
               "limit": limit, "minimum": lo, "maximum": hi, "unit_of_measure": "degrees Celsius" if (lo is not None or hi is not None) else "",
               "how_often": how, "recorded_in": rec, "log_columns": cols}
              for ref, unit, sec, title, limit, lo, hi, how, rec, cols in _LIMITS]
    by_ref = {x["ref"]: x for x in limits}
    sections = []
    for number, title, clauses in _SECTIONS:
        rows = []
        for ref, text in clauses:
            if text is None:
                x = by_ref[ref]
                text = f"{x['unit_or_check']}. Limit: {x['limit']}. Check: {x['how_often']}. Recorded in: {x['recorded_in']}."
            rows.append({"ref": ref, "text": text})
        sections.append({"section": number, "title": title, "clauses": rows})
    clause = {c["ref"]: c["text"] for s in sections for c in s["clauses"]}
    return {
        "plan_id": "FSP-5.0", "title": "Food Safety Plan", "version": "5.0", "effective_date": "2026-07-01",
        "owner": "Head of Food Safety and Quality",
        "notice": "This plan is invented. Every limit, schedule and name in it is made up. It is not food safety guidance.",
        "limits": limits,
        "repeat_rule": {"section": "6.2", "text": clause["6.2"], "minimum_readings": 3,
                        "in_plain_words": "Three or more readings outside the limit on the same piece of equipment in the period "
                                          "are reported to the food safety lead. The food safety lead decides about the unit.",
                        "proposed_next_step": "refer_to_food_safety_lead"},
        "deviation": {"section": "1.2", "text": clause["1.2"]},
        "what_the_plan_does_not_decide": [
            {"section": "1.3", "text": clause["1.3"]}, {"section": "7.1", "text": clause["7.1"]},
            {"section": "7.2", "text": clause["7.2"]}],
        "sections": sections,
    }


# --------------------------------------------------------------------------- the records

# Faults by restaurant. ch2 is the make-line chiller: day -> (opening, afternoon). hh is hot holding: day -> {time: value}.
# fz is the freezer: day -> value. clean_missing: days with no signed cleaning entry. ch1_missed_pm: days on which the
# walk-in chiller afternoon check was recorded as not made. delivery_chilled: day -> reading.
FAULTS = {
    "R-014": dict(ch2={8: (None, 6.8), 9: (7.4, None), 21: (None, 6.1)},
                  hh={14: {"16:00": 58.5}, 27: {"18:00": 60.2}}, clean_missing=[5, 17, 26]),
    "R-022": dict(),
    "R-031": dict(fz={11: -15.5, 12: -14.9}, clean_missing=[19]),
    "R-047": dict(hh={3: {"14:00": 59.0}, 16: {"16:00": 57.5, "18:00": 61.0}, 24: {"20:00": 60.5}}),
    "R-058": dict(ch1_missed_pm=[6, 7, 13, 20], clean_missing=[13]),
    "R-063": dict(delivery_chilled={13: 6.5}),
}

# What arrives with the event "food-safety-records": four templates, in turn. Days are inside every month.
TEMPLATES = [
    dict(),  # 0: everything inside the plan
    dict(ch1={4: (None, 6.4), 5: (6.9, None), 18: (None, 7.2)}),  # 1: walk-in chiller above 5.0 three times
    dict(delivery_chilled={9: 7.1}, clean_missing=[12]),  # 2: a chilled delivery at 7.1 and one missing sign-off
    dict(hh={10: {"14:00": 60.8}, 22: {"16:00": 61.5}}, ck={15: (73.5, None)}),  # 3: hot holding twice, chicken core once
]


def build_records(site_id: str, period: str, spec: dict) -> dict:
    rng = random.Random(f"records-{site_id}-{period}")

    def r(a, b):
        return round(rng.uniform(a, b), 1)

    rows = []
    for day in range(1, days_in(period) + 1):
        ch1_am, ch1_pm = r(2.0, 4.4), r(2.2, 4.6)
        if day in spec.get("ch1_missed_pm", []):
            ch1_pm = "MISSED"
        if day in spec.get("ch1", {}):
            a, p = spec["ch1"][day]
            ch1_am, ch1_pm = (a if a is not None else ch1_am), (p if p is not None else ch1_pm)
        ch2_am, ch2_pm = r(2.4, 4.6), r(2.6, 4.8)
        if day in spec.get("ch2", {}):
            a, p = spec["ch2"][day]
            ch2_am, ch2_pm = (a if a is not None else ch2_am), (p if p is not None else ch2_pm)
        fz = spec.get("fz", {}).get(day, r(-21.5, -18.6))
        hot = {t: spec.get("hh", {}).get(day, {}).get(t, r(64.5, 71.0)) for t in HOT_TIMES}
        ck_am, ck_pm = r(76.0, 82.5), r(76.0, 82.5)
        if day in spec.get("ck", {}):
            a, p = spec["ck"][day]
            ck_am, ck_pm = (a if a is not None else ck_am), (p if p is not None else ck_pm)
        signer = "" if day in spec.get("clean_missing", []) else rng.choice(MANAGERS)
        rows.append(dict(zip(TEMPERATURE_COLUMNS, [
            f"{period}-{day:02d}", ch1_am, ch1_pm, ch2_am, ch2_pm, fz, hot["12:00"], hot["14:00"], hot["16:00"],
            hot["18:00"], hot["20:00"], ck_am, ck_pm, signer])))
    deliveries = []
    for day in DELIVERY_DAYS:
        if day > days_in(period):
            continue
        chilled = spec.get("delivery_chilled", {}).get(day, r(2.0, 4.6))
        frozen = r(-20.5, -16.5)
        deliveries.append(dict(zip(DELIVERY_COLUMNS, [f"{period}-{day:02d}", chilled, frozen, "accepted"])))
    return {"site_id": site_id, "period": period, "temperature_log": rows, "delivery_log": deliveries,
            "notes": "A blank daily_cleaning_signed_by means no signed entry. MISSED means the check was recorded as not made."}


def new_review(site_id: str, period: str) -> dict:
    return {"site_id": site_id, "period": period, "status": "not_reviewed", "checks": [], "corrective_actions": [],
            "corrective_actions_request": None, "signed_by": "", "signed_at": None}


def build_food(today: date) -> dict:
    period = period_of(today)
    records, reviews = {}, {}
    for site_id, spec in FAULTS.items():
        key = f"{site_id}:{period}"
        records[key] = build_records(site_id, period, spec)
        reviews[key] = new_review(site_id, period)
    return {"food_plan": build_plan(), "fs_records": records, "fs_reviews": reviews}


def sim_records(data: dict, today: date, kind: int, number: int) -> tuple[str, str]:
    """Records for one more restaurant arrive. number counts from 1. Returns the key and the message."""
    n = number - 1
    site_id = EXTRA_RESTAURANT_IDS[n % len(EXTRA_RESTAURANT_IDS)]
    period = period_of(today, back=n // len(EXTRA_RESTAURANT_IDS))
    key = f"{site_id}:{period}"
    data["fs_records"][key] = build_records(site_id, period, TEMPLATES[kind])
    data["fs_reviews"][key] = new_review(site_id, period)
    site = data["sites"][site_id]
    return key, (f"Food safety records for restaurant {site_id} ({site['name']}, {site['town']}) for the period {period} have "
                 f"arrived in the foodsafety system. They have not been reviewed. Read them with get_food_safety_records "
                 f"for site {site_id} and period {period}, and check them against the plan with get_food_safety_plan.")
