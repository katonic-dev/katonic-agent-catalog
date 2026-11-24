"""Stores, version 1.4: yesterday's shift log of six sites, and six incident accounts as colleagues wrote them.

A shift log is a list of timed entries. A few of them matter for the next shift and most do not. An incident
account is free text. Colleagues appear by id and role only, and a guest is never named. What a careful reader
should put in a handover note or on the report form is kept in two record sets (shift_log_answers and
incident_answers) and no operation serves them.
"""

from __future__ import annotations

from datetime import date, timedelta

from .seed_people import colleague_id
from .seed_stores import build_sites

CATEGORIES = ["routine", "delivery", "equipment_fault", "complaint", "cash_difference", "staffing_gap", "task"]
PROCEDURE = "Store Procedures Manual, version 3.1, SP-15 Accidents and incidents"
CLAUSES = ["15.1", "15.2", "15.3"]
INCIDENT_TYPES = ["fall", "burn", "cut", "guest_illness", "near_miss", "property_damage", "other"]
AFFECTED = ["crew_member", "guest", "nobody", "other"]

# ---------------------------------------------------------------- shift logs
# site: entries (time, category, colleague number, text), the numbers of the entries still open at the end of the
# day, and the number of the one open entry that names the earliest time on the next day (0 when none names a time)
_LOGS = {
    "R-014": ([
        ("09:55", "routine", 1, "Opening checks done. All chillers in range."),
        ("10:20", "delivery", 1, "Dairy delivery arrived: 40 kg of mozzarella and 6 kg of butter. Checked and put away."),
        ("11:05", "routine", 1, "Opened on time with three on the floor."),
        ("12:40", "equipment_fault", 1, "Oven 2 conveyor stopped. Restarted it at 12:48 and it has run since."),
        ("13:15", "complaint", 1, "A guest said a pizza was cold. Remade it with reason code R2. The guest left content."),
        ("14:30", "delivery", 1, "Packaging delivery was two cases of medium boxes short against the delivery note. The "
                                 "driver signed the note as short. The supplier has not been told yet."),
        ("15:10", "routine", 1, "Afternoon temperature checks done."),
        ("16:00", "staffing_gap", 2, "C-01411 phoned in sick for tomorrow's late shift, which starts at 16:00. No cover found yet."),
        ("17:45", "equipment_fault", 2, "Make-line chiller read 6.5 °C at 17:40. Stock moved to the walk-in chiller. Engineer "
                                        "called and is coming tomorrow between 08:00 and 10:00."),
        ("18:30", "complaint", 2, "A guest phoned about a side missing from a delivery order and asked for a refund. Passed "
                                  "to the restaurant manager, who has not called the guest back yet."),
        ("19:20", "routine", 2, "Busy from 18:00 to 19:15. The queue never went past the door."),
        ("21:10", "task", 2, "Deep clean of the dough mixer not done: we ran out of time. Left for the opening shift."),
        ("22:20", "cash_difference", 2, "Till 1 counted 4.50 over. Recorded."),
        ("23:05", "routine", 2, "Closing checks done. Ovens off, back door locked, alarm set."),
    ], [6, 8, 9, 10, 12], 9),
    "R-031": ([
        ("10:00", "routine", 1, "Opening checks done."),
        ("10:35", "delivery", 1, "Flour delivery: 20 bags, all in date. Put away."),
        ("11:50", "staffing_gap", 1, "C-03108 arrived 50 minutes late. C-03106 stayed on and covered the gap."),
        ("13:05", "complaint", 1, "A guest found a hair in a wrap. Replaced it and apologised. The guest's phone number is in "
                                  "the incident folder. The restaurant manager is to call the guest and has not done so yet."),
        ("14:10", "equipment_fault", 1, "Drinks machine is leaking at the base. A tray is under it and a wet floor sign is "
                                        "out. Not written in the maintenance log yet."),
        ("15:00", "routine", 1, "Afternoon temperature checks done."),
        ("16:20", "delivery", 2, "Produce delivery refused: the peppers arrived at 9 °C. The supplier was told by phone and "
                                 "promised a new delivery tomorrow at 07:30."),
        ("17:30", "routine", 2, "Menu boards changed to the winter menu."),
        ("19:40", "cash_difference", 2, "Till 2 counted 35.00 short. Recounted, still 35.00 short. Recorded and reported to "
                                        "the restaurant manager by phone at 19:55."),
        ("21:00", "routine", 2, "Two crew members trained on the new wrap build."),
        ("22:45", "task", 2, "Packaging stock count not finished: boxes are counted, cups and lids are still to count."),
        ("23:00", "routine", 2, "Closing checks done."),
    ], [4, 5, 7, 11], 7),
    "R-058": ([
        ("09:50", "routine", 1, "Opening checks done."),
        ("10:30", "delivery", 1, "Dairy delivery complete and put away."),
        ("12:15", "complaint", 1, "A guest phoned: a delivery order was 25 minutes late. Apologised and the guest accepted it."),
        ("13:40", "equipment_fault", 1, "Card reader on till 2 froze twice. Restarted it, and it has worked since 13:50."),
        ("15:05", "routine", 1, "Afternoon temperature checks done."),
        ("15:45", "task", 1, "The allergen folder at the counter is the old version 4.0. Version 4.1 is printed and has not "
                             "been put out yet."),
        ("17:10", "staffing_gap", 2, "Late shift ran one short from 17:00 to 19:00, until C-05806 came in to cover."),
        ("18:20", "equipment_fault", 2, "Freezer door alarm sounds on and off. The door closes and the reading is −19 °C. "
                                        "Engineer booked for tomorrow at 14:00."),
        ("19:30", "complaint", 2, "A guest says she was charged twice for one order, 23.80 each time. A copy of the receipt "
                                  "is in the office. The restaurant manager is to check the card report tomorrow at 09:00."),
        ("20:15", "routine", 2, "A quiet evening."),
        ("22:10", "cash_difference", 2, "Till 1 counted 2.00 short. Recorded."),
        ("22:40", "routine", 2, "Oil in fryer 2 changed."),
        ("23:00", "routine", 2, "Closing checks done."),
    ], [6, 8, 9], 9),
    "R-104": ([
        ("10:00", "routine", 1, "Opening checks done."),
        ("10:40", "delivery", 1, "Packaging delivery complete."),
        ("11:30", "task", 1, "Two letters of the sign over the door are not lit. An electrician was asked for a quote. No "
                             "date for the repair yet."),
        ("12:50", "complaint", 1, "A guest was unhappy that the meal deal had ended. Explained, and the guest bought at the full price."),
        ("14:00", "equipment_fault", 1, "Hot holding cabinet read 61 °C at the 14:00 check. Food discarded, thermostat turned "
                                        "up, and it read 66 °C at 14:30."),
        ("15:20", "routine", 1, "Afternoon temperature checks done."),
        ("16:05", "staffing_gap", 2, "Nobody is rostered to open with the shift manager tomorrow at 10:00: C-10407 swapped "
                                     "shifts and the swap was not covered."),
        ("17:40", "delivery", 2, "Produce delivery arrived with 10 kg of onions missing. Written on the delivery note. The "
                                 "supplier's office was closed, so it has not been told."),
        ("19:00", "routine", 2, "Busy until 21:00."),
        ("21:30", "cash_difference", 2, "Till 2 counted 22.00 over. Recounted, the same. Recorded. Not reported to the "
                                        "restaurant manager yet."),
        ("23:00", "routine", 2, "Closing checks done."),
    ], [3, 7, 8, 10], 7),
    "S-101": ([
        ("06:40", "routine", 1, "Opening checks done."),
        ("07:15", "delivery", 1, "Bread delivery complete: 14 trays."),
        ("08:30", "equipment_fault", 1, "Self-checkout 3 does not take cards. It is out of use with a sign on it. The "
                                        "supplier's help desk gave a reference, and an engineer is due tomorrow before 12:00."),
        ("09:45", "complaint", 1, "A customer complained about the queue at the kiosk. A second till was opened."),
        ("11:00", "delivery", 1, "Chilled delivery: one cage of yoghurts arrived at 9 °C, was refused and went back. The "
                                 "rest was accepted. The credit claim has not been raised yet."),
        ("12:30", "routine", 1, "Shelf-edge labels changed for the new promotion."),
        ("13:50", "task", 1, "Last week's promotion posters are still up in the front window. They are to come down."),
        ("15:10", "staffing_gap", 2, "C-10109 went home ill at 15:00. The bakery counter closed an hour early."),
        ("16:40", "complaint", 2, "A customer says a jar of pasta sauce had a chipped rim. The jar and a copy of the receipt "
                                  "are in the manager's office. The customer wants a call back tomorrow before 10:00."),
        ("18:00", "routine", 2, "Evening date check on the bakery done."),
        ("19:20", "cash_difference", 2, "Kiosk till counted 1.20 short. Recorded."),
        ("20:30", "routine", 2, "Date check on the chilled aisle done. Six items reduced."),
        ("22:15", "routine", 2, "Store locked and alarm set."),
    ], [3, 5, 7, 9], 9),
    "S-104": ([
        ("06:45", "routine", 1, "Opening checks done."),
        ("07:30", "delivery", 1, "Newspaper and milk deliveries complete."),
        ("09:10", "equipment_fault", 1, "Bottle return machine jammed. Cleared at 09:25 and working."),
        ("10:20", "routine", 1, "Spill in aisle 6 cleaned and signed."),
        ("11:40", "delivery", 1, "Frozen delivery arrived two hours late. All of it was at −18 °C or colder. Put away."),
        ("13:00", "staffing_gap", 1, "Only one colleague is rostered to unload tomorrow's delivery at 06:30. It needs a second person."),
        ("14:20", "complaint", 1, "A customer was overcharged for washing powder: the shelf said 8.49 and the till took "
                                  "8.99. The difference was refunded. The shelf-edge label has not been corrected yet."),
        ("15:30", "routine", 2, "Afternoon temperature checks done."),
        ("17:00", "equipment_fault", 2, "Freezer 4 in aisle 9 showed −14 °C at 16:50. Stock moved to freezer 5. Engineer "
                                        "called. No time given yet."),
        ("18:45", "routine", 2, "Trolleys collected from the car park."),
        ("20:10", "cash_difference", 2, "Till 5 counted 48.00 short. Recounted with the duty manager, still 48.00 short. "
                                        "Recorded and reported to the store manager by phone at 20:25."),
        ("21:00", "routine", 2, "Car park lights checked. All working."),
        ("22:20", "routine", 2, "Store locked and alarm set."),
    ], [6, 7, 9], 6),
}
LOG_SITES = list(_LOGS)

# What arrives with the event "shift-end". Four templates, in turn. The log is for the retailer date.
_SIM_LOGS = [
    ("R-022", [
        ("10:00", "routine", 1, "Opening checks done."),
        ("10:45", "delivery", 1, "Dairy delivery complete and put away."),
        ("13:20", "complaint", 1, "A guest said a wrap was missing its sauce. Remade it. The guest was content."),
        ("15:00", "routine", 1, "Afternoon temperature checks done."),
        ("18:10", "equipment_fault", 2, "Fryer 1 tripped. Reset at 18:15 and it has run since."),
        ("22:15", "cash_difference", 2, "Till 1 counted 0.80 over. Recorded."),
        ("23:00", "routine", 2, "Closing checks done."),
    ], [], 0),
    ("S-106", [
        ("06:40", "routine", 1, "Opening checks done."),
        ("07:20", "delivery", 1, "Bread delivery was three trays short. Written on the delivery note. The bakery has not been told yet."),
        ("10:05", "routine", 1, "Shelf-edge labels checked on aisle 2."),
        ("13:30", "equipment_fault", 1, "Chiller cabinet 2 door does not close fully. Engineer booked for tomorrow at 08:30."),
        ("17:15", "complaint", 2, "A customer asked for a product we do not stock. Told them which store has it."),
        ("21:10", "cash_difference", 2, "Till 2 counted 3.10 short. Recorded."),
        ("22:15", "routine", 2, "Store locked and alarm set."),
    ], [2, 4], 4),
    ("R-047", [
        ("10:00", "routine", 1, "Opening checks done."),
        ("12:30", "routine", 1, "Lunch rush from 12:00. All orders out inside the target."),
        ("14:40", "task", 1, "The toilet check sheet ran out. New sheets are on order and have not arrived."),
        ("16:30", "delivery", 2, "Flour delivery complete."),
        ("19:50", "staffing_gap", 2, "C-04711 left 30 minutes early with the shift manager's agreement. The shift was covered."),
        ("23:00", "routine", 2, "Closing checks done."),
    ], [3], 0),
    ("S-102", [
        ("06:45", "routine", 1, "Opening checks done."),
        ("08:00", "delivery", 1, "Produce delivery complete."),
        ("09:30", "equipment_fault", 1, "Bottle return machine is still out of use. No repair date from the supplier yet."),
        ("11:15", "complaint", 1, "A customer wants a refund for a kettle bought last week, with no receipt. The store "
                                  "manager is to call the customer tomorrow before 11:00."),
        ("14:00", "staffing_gap", 1, "Nobody is rostered for the kiosk tomorrow from 07:00 to 09:00."),
        ("18:20", "routine", 2, "Evening date check done."),
        ("20:40", "cash_difference", 2, "Till 3 counted 5.00 over. Recorded."),
        ("22:20", "routine", 2, "Store locked and alarm set."),
    ], [3, 4, 5], 5),
]


def log_key(site_id: str, on: str) -> str:
    return f"{site_id}:{on}"


def make_log(site: dict, on: date, rows: list, still_open: list, first: int) -> tuple[dict, dict]:
    site_id = site["site_id"]
    stem = f"LE-{site_id.replace('-', '')}-{on.strftime('%m%d')}"
    entries = [{"entry_id": f"{stem}-{n:02d}", "time": time, "category": category,
                "logged_by": colleague_id(site_id, number), "logged_by_role": "shift_manager", "text": text}
               for n, (time, category, number, text) in enumerate(rows, start=1)]
    log = {"site_id": site_id, "site_name": site["name"], "town": site["town"], "date": on.isoformat(),
           "entries": entries, "handover_notes": []}
    answer = {"site_id": site_id, "date": on.isoformat(), "open_entries": [f"{stem}-{n:02d}" for n in still_open],
              "do_first": f"{stem}-{first:02d}" if first else ""}
    return log, answer


# ---------------------------------------------------------------- incident accounts
# site, days before the retailer date, time written, colleague number, role, the account,
# the right answers for the form and the clauses of SP-15 that set a next step
_ACCOUNTS = [
    ("R-014", 1, "14:50", 7, "team_member",
     "At about 14:20 I was carrying a tray of dough from the walk-in chiller to the make line. The floor by the dish wash "
     "was wet and there was no sign. My foot went from under me and I fell on my left side. My hip and elbow hurt. I told "
     "the shift manager straight away. A first aider put a cold pack on my elbow. I sat down for twenty minutes and then "
     "went back to work on the counter.",
     {"incident_type": "fall", "who_was_affected": "crew_member", "incident_time": "14:20", "first_aid_given": "yes",
      "reported_to_shift_manager": "yes", "area_manager_to_be_phoned_the_same_day": True, "clauses": ["15.1", "15.2"],
      "not_in_the_account": []}),
    ("R-047", 2, "19:30", 9, "team_member",
     "At 19:05 I reached across the open door of oven 1 to take a pizza out and my right forearm touched the top of the "
     "door. There is a red mark about five centimetres long and it has blistered. I held it under cold water for ten "
     "minutes and a first aider put a burn dressing on it. I told the shift manager when it happened.",
     {"incident_type": "burn", "who_was_affected": "crew_member", "incident_time": "19:05", "first_aid_given": "yes",
      "reported_to_shift_manager": "yes", "area_manager_to_be_phoned_the_same_day": True, "clauses": ["15.1", "15.2"],
      "not_in_the_account": []}),
    ("S-104", 3, "11:15", 6, "team_member",
     "This morning in the stockroom a stack of four crates of soft drinks tipped off the top of a roll cage while I was "
     "pulling the cage out. They landed where I had been standing a second before. Nobody was hit and nobody was hurt. Two "
     "crates split and I cleared up. The cage had been loaded above the fill line. I told the duty manager.",
     {"incident_type": "near_miss", "who_was_affected": "nobody", "incident_time": "", "first_aid_given": "no",
      "reported_to_shift_manager": "yes", "area_manager_to_be_phoned_the_same_day": False, "clauses": ["15.2"],
      "not_in_the_account": ["the time of the incident"]}),
    ("R-031", 4, "20:40", 2, "shift_manager",
     "At 20:15 a guest at table 6 picked up a water glass that had a crack in it. The glass broke in her hand and cut her "
     "palm. It bled through two plasters, so I put on a pad and a bandage from the first aid box. She said she would go to "
     "a walk-in clinic. She asked whether we would pay for her taxi and I said I could not say. She left before I took her "
     "phone number.",
     {"incident_type": "cut", "who_was_affected": "guest", "incident_time": "20:15", "first_aid_given": "yes",
      "reported_to_shift_manager": "yes", "area_manager_to_be_phoned_the_same_day": True,
      "clauses": ["15.1", "15.2", "15.3"], "not_in_the_account": ["the guest's contact details"]}),
    ("S-101", 5, "07:10", 11, "team_member",
     "At 06:50 the bread supplier's lorry reversed into the loading bay and hit the left-hand door post. The post is bent "
     "and the roller door now stops halfway down. The driver got out, looked and drove off after unloading. Nobody was "
     "near the door and nobody was hurt. I took a photo of the lorry's number plate. I have not told anyone else yet.",
     {"incident_type": "property_damage", "who_was_affected": "nobody", "incident_time": "06:50", "first_aid_given": "no",
      "reported_to_shift_manager": "no", "area_manager_to_be_phoned_the_same_day": False, "clauses": ["15.2"],
      "not_in_the_account": []}),
    ("R-058", 6, "13:50", 1, "shift_manager",
     "At about 13:25 a guest at table 3 called me over. She said her lips were swelling and she felt sick after eating half "
     "of a falafel wrap. She said she has a sesame allergy and that she had asked at the counter. Her partner drove her to "
     "hospital. I kept the rest of the wrap and the order ticket. I have her partner's phone number. I did not say whose "
     "fault it was.",
     {"incident_type": "guest_illness", "who_was_affected": "guest", "incident_time": "13:25", "first_aid_given": "not_said",
      "reported_to_shift_manager": "yes", "area_manager_to_be_phoned_the_same_day": True,
      "clauses": ["15.1", "15.2", "15.3"], "not_in_the_account": []}),
]

# What arrives with the event "incident-account". Four templates, in turn. The account is dated the retailer date.
_SIM_ACCOUNTS = [
    ("R-022", "12:10", 6, "team_member",
     "At 11:55 I nicked my left thumb on the vegetable slicer while I was cleaning the blade. It was a small cut. I washed "
     "it, put a blue plaster on it and put a glove over the top. I told the shift manager and carried on.",
     {"incident_type": "cut", "who_was_affected": "crew_member", "incident_time": "11:55", "first_aid_given": "yes",
      "reported_to_shift_manager": "yes", "area_manager_to_be_phoned_the_same_day": False, "clauses": ["15.1", "15.2"],
      "not_in_the_account": []}),
    ("S-107", "16:30", 2, "shift_manager",
     "At 16:05 a customer caught her foot on the mat at the entrance and fell onto her knees. She said her right knee hurt. "
     "A first aider helped her to a chair and she sat for ten minutes. She did not want anything else. She asked who would "
     "pay if her knee got worse and I said the store manager would call her. I have her phone number.",
     {"incident_type": "fall", "who_was_affected": "guest", "incident_time": "16:05", "first_aid_given": "yes",
      "reported_to_shift_manager": "yes", "area_manager_to_be_phoned_the_same_day": True,
      "clauses": ["15.1", "15.2", "15.3"], "not_in_the_account": []}),
    ("R-063", "21:20", 10, "team_member",
     "Tonight a full pan of hot oil slid off the edge of the fryer station when I turned round. It hit the floor about a "
     "metre from two of us. Nobody was splashed and nobody was hurt. We put out signs and cleaned the floor. I told the "
     "shift manager.",
     {"incident_type": "near_miss", "who_was_affected": "nobody", "incident_time": "", "first_aid_given": "no",
      "reported_to_shift_manager": "yes", "area_manager_to_be_phoned_the_same_day": False, "clauses": ["15.2"],
      "not_in_the_account": ["the time of the incident"]}),
    ("R-071", "10:40", 1, "shift_manager",
     "At 10:25 a guest phoned the restaurant. He said he was sick in the night after eating a chicken wrap he collected "
     "from us yesterday evening. He asked for his money back and I said the restaurant manager would call him. I have his "
     "phone number and the time of his order.",
     {"incident_type": "guest_illness", "who_was_affected": "guest", "incident_time": "10:25", "first_aid_given": "no",
      "reported_to_shift_manager": "yes", "area_manager_to_be_phoned_the_same_day": True,
      "clauses": ["15.1", "15.2", "15.3"], "not_in_the_account": []}),
]


def make_account(account_id: str, site: dict, on: str, written_at: str, number: int, role: str, text: str,
                 right: dict) -> tuple[dict, dict]:
    account = {"account_id": account_id, "site_id": site["site_id"], "site_name": site["name"], "town": site["town"],
               "incident_date": on, "written_at": written_at, "written_by": colleague_id(site["site_id"], number),
               "written_by_role": role, "account": text, "procedure": PROCEDURE, "status": "account_received",
               "reports": [], "submitted_by": "", "submitted_at": ""}
    return account, {"account_id": account_id, "incident_date": on, **{k: (list(v) if isinstance(v, list) else v) for k, v in right.items()}}


def build_shifts(today: date) -> dict:
    sites = build_sites()
    yesterday = today - timedelta(days=1)
    logs, log_answers = {}, {}
    for site_id, (rows, still_open, first) in _LOGS.items():
        key = log_key(site_id, yesterday.isoformat())
        logs[key], log_answers[key] = make_log(sites[site_id], yesterday, rows, still_open, first)
    month = f"{today.year % 100:02d}{today.month:02d}"
    accounts, answers = {}, {}
    for n, (site_id, days, written_at, number, role, text, right) in enumerate(_ACCOUNTS, start=1):
        account_id = f"IA-{month}-{n:02d}"
        accounts[account_id], answers[account_id] = make_account(
            account_id, sites[site_id], (today - timedelta(days=days)).isoformat(), written_at, number, role, text, right)
    return {"shift_logs": logs, "shift_log_answers": log_answers, "incident_accounts": accounts, "incident_answers": answers}


def sim_shift_end(data: dict, today: date, kind: int, back: int) -> tuple[str, str]:
    """One more shift log arrives: the day's log of another site. Returns its id and the message."""
    site_id, rows, still_open, first = _SIM_LOGS[kind]
    on = today - timedelta(days=back)
    site = data["sites"][site_id]
    key = log_key(site_id, on.isoformat())
    data["shift_logs"][key], data["shift_log_answers"][key] = make_log(site, on, rows, still_open, first)
    return key, (f"The shift log of {site_id} ({site['name']}, {site['town']}) for {on.isoformat()} has arrived in the stores "
                 f"system. It has {len(rows)} entries and no handover note has been written for it. Read it with "
                 f"get_shift_log for {site_id} and {on.isoformat()}.")


def sim_incident(data: dict, today: date, kind: int, account_id: str) -> tuple[str, str]:
    """One more incident account arrives, written today. Returns its id and the message."""
    site_id, written_at, number, role, text, right = _SIM_ACCOUNTS[kind]
    site = data["sites"][site_id]
    data["incident_accounts"][account_id], data["incident_answers"][account_id] = make_account(
        account_id, site, today.isoformat(), written_at, number, role, text, right)
    return account_id, (f"A new incident account {account_id} from {site_id} ({site['name']}, {site['town']}) has arrived in "
                        f"the stores system. A colleague wrote it on {today.isoformat()} at {written_at}. No report form has "
                        f"been filled in for it. Read it with get_incident_account for {account_id}.")
