"""People, version 1.4: draft rosters for next week and the rules they are checked against.

Six draft rosters: four restaurants and two stores. Colleagues appear by id and role only. Three rosters hold
planted breaches, one is plain, and two sit exactly on a limit in several places without crossing it. What a
careful reader should list is kept in its own record set (roster_answers) and no operation serves it. The seed
works the breaches out from the rosters with find_breaches and stops when they are not the planted ones.
"""

from __future__ import annotations

from datetime import date, timedelta

from .seed_stores import build_sites

NOTICE = "Rowanmere Group is invented, and so is this document. It is not the document of any real retailer."
DOCUMENT = "Working Time and Staffing Rules"
VERSION = "1.2"
OWNER = "Head of People"
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

MAX_SHIFT_HOURS = 10
MIN_REST_HOURS = 11
MAX_WEEK_HOURS = 48
BREAK_AFTER_HOURS = 6
BREAK_MINUTES = 30
YOUNG_MAX_SHIFT_HOURS = 8
YOUNG_MAX_WEEK_HOURS = 40
YOUNG_EARLIEST = "06:00"
YOUNG_LATEST = "22:00"
MIN_PEOPLE_TO_OPEN_AND_CLOSE = 2

PART_A = ("Part A states the working time rules of Meridia as the company states them for its managers. Meridia is an "
          "invented country, and these are not the rules of any real country.")
PART_B = "Part B holds the company's own staffing rules. They apply to every store and every restaurant on every day it trades."
COUNTING = ("Hours are counted from the start of a shift to its end, and a break is part of the shift. The roster week "
            "runs from Monday to Sunday. A young worker is a colleague aged 16 or 17, and the roster gives the age band "
            "of each colleague as adult or young worker. A colleague is on shift at a time when the shift has started "
            "and has not ended. A figure exactly on a limit keeps the rule.")
NOT_DECIDED = ("These rules do not say who should work which shift, and they do not say how a breach is put right: the "
               "manager who owns the roster changes it. They set no limit by a colleague's contracted hours, which are on "
               "the roster for the manager's use. They say nothing about pay, and they rate no colleague.")

# rule, part, title, text, limit, unit, applies to
_RULES = [
    ("WT-1", "working_time", "Maximum shift length",
     f"No shift is longer than {MAX_SHIFT_HOURS} hours.", MAX_SHIFT_HOURS, "hours", "every colleague"),
    ("WT-2", "working_time", "Rest between shifts",
     f"A colleague has at least {MIN_REST_HOURS} hours of rest between the end of one shift and the start of the next.",
     MIN_REST_HOURS, "hours", "every colleague"),
    ("WT-3", "working_time", "Maximum weekly hours",
     f"A colleague is rostered for no more than {MAX_WEEK_HOURS} hours in a roster week.", MAX_WEEK_HOURS, "hours",
     "every colleague"),
    ("WT-4", "working_time", "Break",
     f"A shift longer than {BREAK_AFTER_HOURS} hours has a break of at least {BREAK_MINUTES} minutes.", BREAK_MINUTES,
     "minutes", "every colleague"),
    ("WT-5", "working_time", "Young workers: shift length",
     f"No shift of a young worker is longer than {YOUNG_MAX_SHIFT_HOURS} hours.", YOUNG_MAX_SHIFT_HOURS, "hours",
     "young workers"),
    ("WT-6", "working_time", "Young workers: weekly hours",
     f"A young worker is rostered for no more than {YOUNG_MAX_WEEK_HOURS} hours in a roster week.", YOUNG_MAX_WEEK_HOURS,
     "hours", "young workers"),
    ("WT-7", "working_time", "Young workers: early and late hours",
     f"No shift of a young worker starts before {YOUNG_EARLIEST} or ends after {YOUNG_LATEST}.", YOUNG_LATEST,
     "time of day", "young workers"),
    ("WT-8", "working_time", "Weekly rest day",
     "A colleague has at least one day with no shift in a roster week.", 1, "days", "every colleague"),
    ("SR-1", "staffing", "A shift manager on every trading hour",
     "A shift manager is on shift at every time between the site's opening time and its closing time.", 1,
     "shift managers", "the site"),
    ("SR-2", "staffing", "Two people to open and to close",
     f"At least {MIN_PEOPLE_TO_OPEN_AND_CLOSE} colleagues are on shift at the site's opening time, and at least "
     f"{MIN_PEOPLE_TO_OPEN_AND_CLOSE} at its closing time.", MIN_PEOPLE_TO_OPEN_AND_CLOSE,
     "colleagues", "the site"),
    ("SR-3", "staffing", "A trained first aider on site",
     "A colleague with a current first aid certificate is on shift at every time between the site's opening time and "
     "its closing time. The roster marks each first aider.", 1, "first aiders", "the site"),
]
RULE_IDS = [r[0] for r in _RULES]


def rules_markdown() -> str:
    out = [f"# {DOCUMENT} (invented)", "", NOTICE, "",
           f"Version: {VERSION}. Owner: {OWNER}. A draft roster is checked against these rules before it is published.", "",
           "## How hours and times are counted", "", COUNTING, "",
           "## Part A. Working time rules of Meridia, as the company states them", "", PART_A, ""]
    for rule, part, title, text, _, _, _ in _RULES:
        if rule == "SR-1":
            out += ["## Part B. The company's staffing rules", "", PART_B, ""]
        out += [f"### {rule}. {title}", "", text, ""]
    out += ["## What these rules do not decide", "", NOT_DECIDED, ""]
    return "\n".join(out)


RULES = {
    "document": DOCUMENT, "version": VERSION, "owner": OWNER, "notice": NOTICE,
    "how_hours_and_times_are_counted": COUNTING, "part_a": PART_A, "part_b": PART_B,
    "rules": [{"rule": r, "part": p, "title": t, "text": x, "limit": lim, "unit": unit, "applies_to": who}
              for r, p, t, x, lim, unit, who in _RULES],
    "what_the_rules_do_not_decide": NOT_DECIDED, "text": rules_markdown(),
}

# ---------------------------------------------------------------- the rosters

# shift codes: start, end, break in minutes
_CODES = {
    "restaurant": {"E": ("10:00", "16:00", 0), "M": ("12:00", "20:00", 30), "L": ("16:00", "23:00", 30)},
    "store": {"E": ("06:30", "14:30", 30), "M": ("10:00", "18:00", 30), "L": ("14:30", "22:30", 30)},
}
_TRADING = {"restaurant": ("11:00", "22:00"), "store": ("07:00", "22:00")}
# number, role, age band, first aider, one letter for each day from Monday (- is a day off)
_TEMPLATE = [
    (1, "shift_manager", "adult", True, "EEEEE--"),
    (2, "shift_manager", "adult", True, "LLLLL--"),
    (3, "shift_manager", "adult", True, "--MM-EE"),
    (4, "shift_manager", "adult", True, "-M--MLL"),
    (5, "team_member", "adult", True, "EEEEE--"),
    (6, "team_member", "adult", False, "EE--EEE"),
    (7, "team_member", "adult", False, "--EE-EE"),
    (8, "team_member", "young_worker", False, "MMMM---"),
    (9, "team_member", "adult", False, "LLLLL--"),
    (10, "team_member", "adult", True, "LL--LLL"),
    (11, "team_member", "adult", False, "--LL-LL"),
    (12, "team_member", "young_worker", False, "----MMM"),
]
_CONTRACTED = {"restaurant": {1: 30, 2: 35, 3: 28, 4: 28, 5: 30, 6: 30, 7: 24, 8: 24, 9: 35, 10: 35, 11: 28, 12: 16},
               "store": {1: 40, 2: 40, 3: 32, 4: 32, 5: 40, 6: 40, 7: 32, 8: 24, 9: 40, 10: 40, 11: 32, 12: 24}}

# site: {(colleague number, day from 0): a shift code, or (start, end, break), or None for a day off}
_CHANGES = {
    # two breaches: rest too short, and a missed break
    "R-014": {(7, 1): ("16:30", "23:30", 30), (9, 4): ("16:00", "23:00", 0)},
    # nothing outside the rules
    "R-022": {},
    # two breaches: a young worker past the evening limit, and an hour with no shift manager
    "R-047": {(12, 5): ("16:00", "23:00", 30), (4, 6): ("17:00", "23:00", 0)},
    # no breach: rest of exactly 11 hours, a young worker's shift of exactly 8 hours that ends at exactly 22:00,
    # and a shift of exactly 10 hours
    "R-063": {(7, 1): "L", (12, 5): ("14:00", "22:00", 30), (4, 5): ("13:00", "23:00", 30)},
    # two breaches: a week over the maximum, and an opening with one person
    "S-103": {(6, 2): "E", (6, 5): ("06:30", "15:30", 30), (5, 3): ("08:00", "16:00", 30), (7, 3): ("08:00", "16:00", 30)},
    # no breach: a week of exactly 48 hours, exactly two people at an opening, a young worker on exactly 40 hours
    "S-106": {(6, 2): "E", (7, 3): ("08:00", "16:00", 30), (8, 4): "M"},
}
ROSTER_SITES = list(_CHANGES)

# What a careful reader lists: site -> (rule, colleague number or 0, day from 0, what the roster shows)
_PLANTED = {
    "R-014": [("WT-2", 7, 2, "10 hours 30 minutes of rest: Tuesday's shift ends at 23:30 and Wednesday's starts at 10:00"),
              ("WT-4", 9, 4, "a shift of 7 hours, 16:00 to 23:00, with no break")],
    "R-022": [],
    "R-047": [("WT-7", 12, 5, "a young worker's shift ends at 23:00"),
              ("SR-1", 0, 6, "no shift manager on shift from 16:00 to 17:00")],
    "R-063": [],
    "S-103": [("WT-3", 6, 0, "49 hours in the week"),
              ("SR-2", 1, 3, "one colleague on shift at the opening time, 07:00")],
    "S-106": [],
}
_NEAR = {
    "R-063": ["{c07} has exactly 11 hours of rest between Tuesday (ends 23:00) and Wednesday (starts 10:00): WT-2 is kept.",
              "{c12}, a young worker, has a Saturday shift of exactly 8 hours that ends at exactly 22:00: WT-5 and WT-7 are kept.",
              "{c04} has a Saturday shift of exactly 10 hours, 13:00 to 23:00: WT-1 is kept."],
    "S-106": ["{c06} is rostered for exactly 48 hours: WT-3 is kept.",
              "On Thursday exactly two colleagues, {c01} and {c05}, are on shift at the opening time, 07:00: SR-2 is kept.",
              "{c08}, a young worker, is rostered for exactly 40 hours: WT-6 is kept."],
}


def minutes(hhmm: str) -> int:
    return int(hhmm[:2]) * 60 + int(hhmm[3:])


def next_monday(today: date) -> date:
    return today + timedelta(days=7 - today.weekday())


def colleague_id(site_id: str, number: int) -> str:
    return f"C-{int(site_id[2:]):03d}{number:02d}"


def roster_id_of(site_id: str, week_start: date) -> str:
    return f"RS-{week_start.strftime('%y%m%d')}-{site_id.replace('-', '')}"


def make_roster(site: dict, week_start: date) -> dict:
    kind, site_id = site["kind"], site["site_id"]
    codes, changes = _CODES[kind], _CHANGES[site_id]
    opens, closes = _TRADING[kind]
    raw = []
    for number, role, age, first_aider, pattern in _TEMPLATE:
        for day in range(7):
            what = changes.get((number, day), pattern[day] if pattern[day] != "-" else None)
            if what is None:
                continue
            start, end, pause = codes[what] if isinstance(what, str) else what
            raw.append((day, start, number, role, end, pause))
    raw.sort()
    short = site_id.replace("-", "")
    shifts = []
    for n, (day, start, number, role, end, pause) in enumerate(raw, start=1):
        shifts.append({"shift_id": f"SH-{short}-{n:02d}", "colleague_id": colleague_id(site_id, number), "role": role,
                       "day": DAYS[day], "date": (week_start + timedelta(days=day)).isoformat(), "start": start, "end": end,
                       "hours": round((minutes(end) - minutes(start)) / 60, 2), "break_minutes": pause})
    colleagues = []
    for number, role, age, first_aider, _ in _TEMPLATE:
        cid = colleague_id(site_id, number)
        own = [s for s in shifts if s["colleague_id"] == cid]
        colleagues.append({"colleague_id": cid, "role": role, "age_band": age, "first_aider": first_aider,
                           "contracted_hours": _CONTRACTED[kind][number],
                           "rostered_hours": round(sum(s["hours"] for s in own), 2), "days_rostered": len({s["day"] for s in own})})
    return {"roster_id": roster_id_of(site_id, week_start), "site_id": site_id, "site_name": site["name"], "town": site["town"],
            "week_start": week_start.isoformat(), "week_end": (week_start + timedelta(days=6)).isoformat(),
            "opens": opens, "closes": closes, "status": "draft", "rules_document": f"{DOCUMENT}, version {VERSION}",
            "colleagues": colleagues, "shifts": shifts, "checks": [], "published_by": "", "published_at": ""}


def _hhmm(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


def find_breaches(roster: dict) -> list[dict]:
    """Every breach of the rules in one roster, worked out from what get_draft_roster serves."""
    out = []
    people = {c["colleague_id"]: c for c in roster["colleagues"]}
    opens, closes = minutes(roster["opens"]), minutes(roster["closes"])

    def add(rule, colleague="", shift="", day="", what=""):
        out.append({"rule": rule, "colleague_id": colleague, "shift_id": shift, "day": day, "what": what})

    for cid, person in people.items():
        own = sorted((s for s in roster["shifts"] if s["colleague_id"] == cid), key=lambda s: (s["date"], s["start"]))
        young = person["age_band"] == "young_worker"
        for s in own:
            if s["hours"] > MAX_SHIFT_HOURS:
                add("WT-1", cid, s["shift_id"], s["day"], f"{s['hours']} hours")
            if s["hours"] > BREAK_AFTER_HOURS and s["break_minutes"] < BREAK_MINUTES:
                add("WT-4", cid, s["shift_id"], s["day"], f"{s['hours']} hours with a break of {s['break_minutes']} minutes")
            if young and s["hours"] > YOUNG_MAX_SHIFT_HOURS:
                add("WT-5", cid, s["shift_id"], s["day"], f"{s['hours']} hours")
            if young and (minutes(s["start"]) < minutes(YOUNG_EARLIEST) or minutes(s["end"]) > minutes(YOUNG_LATEST)):
                add("WT-7", cid, s["shift_id"], s["day"], f"{s['start']} to {s['end']}")
        for before, after in zip(own, own[1:]):
            gap_days = (date.fromisoformat(after["date"]) - date.fromisoformat(before["date"])).days
            rest = gap_days * 1440 + minutes(after["start"]) - minutes(before["end"])
            if rest < MIN_REST_HOURS * 60:
                add("WT-2", cid, after["shift_id"], after["day"], f"{rest // 60} hours {rest % 60} minutes of rest")
        total = round(sum(s["hours"] for s in own), 2)
        if total > MAX_WEEK_HOURS:
            add("WT-3", cid, "", "", f"{total} hours")
        if young and total > YOUNG_MAX_WEEK_HOURS:
            add("WT-6", cid, "", "", f"{total} hours")
        if len({s["day"] for s in own}) == 7:
            add("WT-8", cid, "", "", "a shift on every day")
    for day in DAYS:
        today = [s for s in roster["shifts"] if s["day"] == day]

        def gaps(wanted) -> list[str]:
            found, start = [], None
            for slot in range(opens, closes, 30):
                covered = any(wanted(s) and minutes(s["start"]) <= slot and minutes(s["end"]) >= slot + 30 for s in today)
                if not covered and start is None:
                    start = slot
                if covered and start is not None:
                    found.append(f"{_hhmm(start)} to {_hhmm(slot)}")
                    start = None
            if start is not None:
                found.append(f"{_hhmm(start)} to {_hhmm(closes)}")
            return found

        for gap in gaps(lambda s: s["role"] == "shift_manager"):
            add("SR-1", "", "", day, gap)
        for gap in gaps(lambda s: people[s["colleague_id"]]["first_aider"]):
            add("SR-3", "", "", day, gap)
        at_open = [s for s in today if minutes(s["start"]) <= opens < minutes(s["end"])]
        at_close = [s for s in today if minutes(s["start"]) <= closes < minutes(s["end"])]
        for label, there in (("opening", at_open), ("closing", at_close)):
            if len(there) < MIN_PEOPLE_TO_OPEN_AND_CLOSE:
                lone = there[0] if there else {"colleague_id": "", "shift_id": ""}
                add("SR-2", lone["colleague_id"], lone["shift_id"], day, f"{len(there)} on shift at the {label} time")
    return sorted(out, key=lambda b: (b["rule"], b["colleague_id"], b["day"]))


def build_people(today: date) -> dict:
    week_start = next_monday(today)
    sites = build_sites()
    rosters, answers = {}, {}
    for site_id in ROSTER_SITES:
        roster = make_roster(sites[site_id], week_start)
        found = find_breaches(roster)
        planted = sorted((rule, colleague_id(site_id, number) if number else "", DAYS[day] if rule not in ("WT-3", "WT-6", "WT-8") else "")
                         for rule, number, day, _ in _PLANTED[site_id])
        if sorted((b["rule"], b["colleague_id"], b["day"]) for b in found) != planted:
            raise AssertionError(f"roster {site_id}: the breaches found are not the planted ones: {found}")
        names = {f"c{n:02d}": colleague_id(site_id, n) for n in range(1, 13)}
        answers[roster["roster_id"]] = {
            "roster_id": roster["roster_id"], "site_id": site_id,
            "breaches": [{**b, "note": next(text for rule, number, day, text in _PLANTED[site_id] if rule == b["rule"])}
                         for b in found],
            "on_a_limit": [text.format(**names) for text in _NEAR.get(site_id, [])]}
        rosters[roster["roster_id"]] = roster
    return {"draft_rosters": rosters, "roster_answers": answers}
