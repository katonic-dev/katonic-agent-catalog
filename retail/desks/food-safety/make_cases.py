"""Builds cases.json for the food safety desk from the invented retailer's own records.

The six record checks are the records the retailer service holds for the period 2026-10
when its date is 24 November 2026. Nothing is typed here by hand: the restaurants, their
towns, streets and area managers, the plan's name and every reading come from the seed of
the service in ../../../demo-retailer. No server is started.

Usage, from anywhere:
    python make_cases.py           writes cases.json beside this file
    python make_cases.py --check   exits 1 if cases.json differs from what would be written

The test demo-retailer/tests/test_food_safety_desk_cases.py runs the same comparison.
Rowanmere Group is invented, and so is every record.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
RETAILER = HERE.parents[2] / "demo-retailer"
OUT = HERE / "cases.json"

RETAILER_DATE = date(2026, 11, 24)
PERIOD = "2026-10"
SITES = ["R-014", "R-022", "R-031", "R-047", "R-058", "R-063"]

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]

COMMENT = ("Six invented record checks for the demo, one restaurant each, October 2026. Made by make_cases.py from the "
           "records the invented retailer (demo-retailer) holds for the period 2026-10 at retailer date 2026-11-24. "
           "Do not edit by hand: change the service's seed and run the script. Rowanmere Group, its restaurants and "
           "every reading are invented. Nothing here is food safety guidance.")

# The records are written as four short logs, so that a line fits the width of the desk's pane and of a phone.
# Each log has one line per day (or per delivery) and one column per check, in the order its "Columns" line gives.
COLD = ("COLD STORAGE LOG", "Columns: date, walk-in chiller at opening, walk-in chiller in the afternoon, make-line chiller at "
        "opening, make-line chiller in the afternoon, freezer at opening",
        ["walk_in_chiller_opening_c", "walk_in_chiller_afternoon_c", "make_line_chiller_opening_c",
         "make_line_chiller_afternoon_c", "freezer_opening_c"])
HOT = ("HOT HOLDING LOG", "Columns: date, hot holding cabinet at 12:00, 14:00, 16:00, 18:00 and 20:00",
       ["hot_holding_12h_c", "hot_holding_14h_c", "hot_holding_16h_c", "hot_holding_18h_c", "hot_holding_20h_c"])
COOK = ("COOKING AND CLEANING LOG", "Columns: date, chicken core first batch of the morning shift, chicken core first batch of "
        "the afternoon shift, daily cleaning signed by",
        ["chicken_core_first_batch_am_c", "chicken_core_first_batch_pm_c", "daily_cleaning_signed_by"])
DELIVERY = ("DELIVERY LOG", "Columns: date, chilled item, frozen item, outcome", ["chilled_item_c", "frozen_item_c", "outcome"])
READINGS = ("Readings: degrees C. MISSED means the check was recorded as not made. (blank) means there is no signed daily "
            "cleaning entry for that day.")
BLANK = "(blank)"


def _seed():
    """The service's starting data for the retailer date. Imported, never served."""
    if str(RETAILER) not in sys.path:
        sys.path.insert(0, str(RETAILER))
    from retailer.seed import build_all  # noqa: E402
    from retailer.seed_base import period_of  # noqa: E402

    if period_of(RETAILER_DATE) != PERIOD:
        raise SystemExit(f"the retailer date {RETAILER_DATE} does not give the period {PERIOD}")
    return build_all(RETAILER_DATE)


def _day(iso: str) -> str:
    """2026-10-08 -> 08 Oct"""
    return f"{iso[8:10]} {MONTHS[int(iso[5:7]) - 1][:3]}"


def _value(v) -> str:
    if isinstance(v, (int, float)):
        return f"{v:.1f}"
    return str(v) if str(v) else BLANK


def _log(part: tuple, rows: list) -> list:
    heading, columns, keys = part
    return ["", heading, columns] + [", ".join([_day(row["date"])] + [_value(row[k]) for k in keys]) for row in rows]


def records_text(site: dict, records: dict, month: str, year: str) -> str:
    """The month as the desk holds it. Every value the service returns is here once, under its own column."""
    log = records["temperature_log"]
    served = set(log[0]) - {"date"}
    written = set(COLD[2] + HOT[2] + COOK[2])
    if served != written:
        raise SystemExit(f"the temperature log's columns changed: {sorted(served ^ written)}")
    lines = [
        f"Restaurant: {site['site_id']} {site['name']}, {site['town']}",
        f"Period: 1 to {len(log)} {month} {year}",
        READINGS,
    ]
    for part in (COLD, HOT, COOK):
        lines += _log(part, log)
    lines += _log(DELIVERY, records["delivery_log"])
    return "\n".join(lines)


def build() -> dict:
    data = _seed()
    plan = data["food_plan"]
    month, year = MONTHS[int(PERIOD[5:7]) - 1], PERIOD[:4]
    checks = []
    for site_id in SITES:
        site = data["sites"][site_id]
        records = data["fs_records"][f"{site_id}:{PERIOD}"]
        checks.append({
            "title": f"{site_id} {site['name']}",
            "town": site["town"],
            "street": site["street"],
            "period": f"{month} {year}",
            "area_manager": f"{site['area_manager']}, {site['area']}",
            "plan": f"{plan['title']}, version {plan['version']}",
            "text": records_text(site, records, month, year),
            "arrived_via": "feed",
        })
    return {"$comment": COMMENT, "checks": checks}


def render() -> str:
    return json.dumps(build(), ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str]) -> int:
    text = render()
    if "--check" in argv:
        held = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if held != text:
            print("cases.json differs from what make_cases.py would write. Run make_cases.py.")
            return 1
        print("cases.json is what make_cases.py would write.")
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.name}: {len(build()['checks'])} record checks")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
