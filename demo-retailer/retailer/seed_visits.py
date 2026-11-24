"""Stores, version 1.1: area manager visits to stores and restaurants in the period.

Each visit has the checklist with a score for every item, and the area manager's notes in free text. An item
scored 1 or 0 is a finding. Some sentences of the notes are findings too, and some are too vague to tie to a
standard. What a careful reader should list is kept in its own record set (visit_answers) and no operation
serves it.
"""

from __future__ import annotations

from datetime import date

from .seed_base import period_of, yymm
from .seed_stores import build_sites

# The numbered standards of the Brand Standards document, version 2.0 (retail/policy-library/brand-standards-v2.0.md).
STANDARDS = ["BS-1.1", "BS-1.2", "BS-1.3", "BS-2.1", "BS-2.2", "BS-2.3", "BS-3.1", "BS-3.2", "BS-3.3", "BS-4.1", "BS-4.2",
             "BS-4.3", "BS-5.1", "BS-5.2", "BS-6.1", "BS-6.2", "BS-7.1", "BS-7.2", "BS-7.3", "BS-8.1", "BS-8.2"]
STANDARDS_DOCUMENT = "Brand Standards, version 2.0"

# item number, the standard it rests on, the item as printed on the checklist
CHECKLIST = [
    (1, "BS-1.1", "Sign outside clean and fully lit"),
    (2, "BS-1.2", "Entrance, windows and frontage free of litter"),
    (3, "BS-2.1", "Customers greeted within 30 seconds"),
    (4, "BS-2.2", "Full uniform and name badge"),
    (5, "BS-3.1", "Floors, tables and counters clean and dry"),
    (6, "BS-3.2", "Customer toilets checked every hour and the sheet signed"),
    (7, "BS-4.1", "Everything on the menu board or shelf plan on sale, gaps labelled"),
    (8, "BS-4.3", "No product on display past its date"),
    (9, "BS-5.1", "Shelf or menu price is the till price"),
    (10, "BS-6.1", "Equipment faults written in the maintenance log"),
    (11, "BS-7.1", "Fire exits clear and unlocked"),
    (12, "BS-8.1", "Training records up to date for everyone on shift"),
]
MAX_SCORE = 2

# site, day of the period, time, {item: (score, note)}, notes,
# findings in the notes that rest on a standard [(standard, what)], sentences too vague to tie to a standard
_VISITS = [
    ("R-047", 6, "15:30",
     {3: (1, "Two guests stood at the counter for over a minute before anyone spoke to them."),
      6: (0, "Toilet check sheet last signed at 11:00. The visit was at 15:30."),
      10: (1, "The second oven has a door fault that is not in the log. The manager says it was reported by phone.")},
     "Arrived at 15:30 in the afternoon lull. Posters for the meal deal that ended two weeks ago are still up in the front window. "
     "Something is not right with the evening team, I could not put my finger on it. The manager was helpful throughout.",
     [("BS-5.2", "Posters for the meal deal that ended two weeks ago are still up in the front window.")],
     ["Something is not right with the evening team, I could not put my finger on it."]),
    ("S-106", 9, "16:10",
     {8: (0, "Two packs of sliced ham on display were one day past their date."),
      9: (0, "Three shelf-edge prices did not match the till: washing powder, olive oil and a cereal."),
      11: (1, "Rear fire exit partly blocked by a roll cage. It was moved while I was there.")},
     "A busy afternoon. The till area felt chaotic. Refunds seem high here, worth a look by someone.",
     [],
     ["The till area felt chaotic.", "Refunds seem high here, worth a look by someone."]),
    ("R-014", 14, "11:45", {},
     "A good visit. The team knew the standards and the restaurant was ready for the lunch rush. Nothing to raise.",
     [], []),
    ("S-104", 20, "17:00",
     {1: (1, "Two letters of the sign over the door were not lit."),
      7: (1, "Six gaps on the bakery shelves with no out-of-stock label.")},
     "The bins by the entrance were overflowing at 17:00. Could be better generally.",
     [("BS-3.3", "The bins by the entrance were overflowing at 17:00.")],
     ["Could be better generally."]),
    ("R-090", 23, "13:20",
     {4: (1, "Two crew members had no name badge."),
      12: (0, "No up-to-date training record for three of the seven colleagues on shift.")},
     "The seal on the first aid box was broken and there were no plasters in it. The manager mentioned issues with a "
     "supplier and gave no detail.",
     [("BS-7.3", "The seal on the first aid box was broken and there were no plasters in it.")],
     ["The manager mentioned issues with a supplier and gave no detail."]),
    ("S-102", 28, "10:40",
     {10: (0, "The fault on the bottle return machine is not in the maintenance log.")},
     "The bottle return machine has been out of use for 26 days and nobody could give me a date for its repair. "
     "The atmosphere was a bit flat.",
     [("BS-6.2", "The bottle return machine has been out of use for 26 days and nobody could give me a date for its repair.")],
     ["The atmosphere was a bit flat."]),
]

# What arrives with the event "site-visit". Four templates, in turn.
_SIM = [
    ("R-022", "12:15", {}, "Nothing to raise. The restaurant was clean and the team was ready.", [], []),
    ("S-101", "09:50",
     {5: (0, "A spill in aisle 4 had not been cleaned or signed."),
      9: (1, "One shelf-edge price did not match the till: a jar of honey.")},
     "The store manager walked the floor with me.", [], []),
    ("R-063", "18:05",
     {3: (1, "A guest waited about a minute at the counter before being greeted.")},
     "The floor by the drinks machine was wet and there was no sign beside it. I am not sure the new manager has "
     "settled in.",
     [("BS-7.2", "The floor by the drinks machine was wet and there was no sign beside it.")],
     ["I am not sure the new manager has settled in."]),
    ("S-107", "14:30", {}, "It felt untidy in places. I will look again next time.", [],
     ["It felt untidy in places."]),
]


def make_visit(visit_id: str, site: dict, on: str, time: str, scores: dict, notes: str, in_notes: list, vague: list) -> tuple[dict, dict]:
    checklist = []
    for item_no, standard, item in CHECKLIST:
        score, note = scores.get(item_no, (MAX_SCORE, ""))
        checklist.append({"item_no": item_no, "standard": standard, "item": item, "score": score, "max_score": MAX_SCORE,
                          "note": note})
    visit = {"visit_id": visit_id, "site_id": site["site_id"], "site_name": site["name"], "town": site["town"],
             "date": on, "time": time, "area": site["area"], "area_manager": site["area_manager"],
             "standards_document": STANDARDS_DOCUMENT, "checklist": checklist,
             "score": sum(x["score"] for x in checklist), "max_score": MAX_SCORE * len(checklist),
             "notes": notes, "reports": []}
    answer = {"visit_id": visit_id,
              "from_checklist": [{"item_no": x["item_no"], "standard": x["standard"], "score": x["score"]}
                                 for x in checklist if x["score"] < MAX_SCORE],
              "from_notes": [{"standard": s, "what": what} for s, what in in_notes],
              "to_clarify": list(vague)}
    return visit, answer


def build_visits(today: date) -> dict:
    period = period_of(today)
    sites = build_sites()
    visits, answers = {}, {}
    for n, (site_id, day, time, scores, notes, in_notes, vague) in enumerate(_VISITS, start=1):
        visit_id = f"SV-{yymm(period)}-{n:02d}"
        visits[visit_id], answers[visit_id] = make_visit(visit_id, sites[site_id], f"{period}-{day:02d}", time, scores,
                                                         notes, in_notes, vague)
    return {"site_visits": visits, "visit_answers": answers}


def sim_visit(data: dict, today: date, kind: int, visit_id: str) -> tuple[str, str]:
    """One more visit arrives, made today. Returns the visit id and the message."""
    site_id, time, scores, notes, in_notes, vague = _SIM[kind]
    site = data["sites"][site_id]
    data["site_visits"][visit_id], data["visit_answers"][visit_id] = make_visit(
        visit_id, site, today.isoformat(), time, scores, notes, in_notes, vague)
    return visit_id, (f"A new area manager visit {visit_id} to {site_id} ({site['name']}, {site['town']}) has arrived in the "
                      f"stores system. It was made on {today.isoformat()} by {site['area_manager']}. No report has been "
                      f"written for it. Read the checklist and the notes with get_site_visit for {visit_id}.")
