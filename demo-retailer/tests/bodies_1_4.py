"""Version 1.4: one valid call for each operation of the people and franchise systems, and for the shift logs and
incident accounts of the stores system.

test_operations.py adds them to its table so that every operation of the service is called once, in an order in
which each change comes after the draft it needs. test_version_1_4.py uses the same bodies.
"""

ROSTER = "RS-261130-S103"
ROSTER_CHECK = {
    "breaches": [
        {"rule": "WT-3", "colleague_id": "C-10306", "what_the_roster_shows": "49 hours in the week. The rule allows 48."},
        {"rule": "SR-2", "colleague_id": "C-10301", "shift_id": "SH-S103-25", "day": "thursday",
         "what_the_roster_shows": "One colleague is on shift at the opening time, 07:00. The next two start at 08:00."}],
    "summary": "Two breaches: one of WT-3 and one of SR-2.", "drafted_by": "a test"}

LOG_SITE = "R-014"
HANDOVER = {
    "what_happened": [
        {"entry_id": "LE-R014-1123-04", "text": "Oven 2 conveyor stopped at 12:40 and has run since 12:48."},
        {"entry_id": "LE-R014-1123-05", "text": "One remake for a cold pizza, reason code R2."}],
    "still_open": [
        {"entry_id": "LE-R014-1123-06", "text": "Packaging delivery two cases of medium boxes short. The supplier has not been told."},
        {"entry_id": "LE-R014-1123-08", "text": "C-01411 is off sick for tomorrow's late shift at 16:00. No cover yet."},
        {"entry_id": "LE-R014-1123-09", "text": "Make-line chiller read 6.5 °C. Stock is in the walk-in chiller. Engineer tomorrow between 08:00 and 10:00."},
        {"entry_id": "LE-R014-1123-10", "text": "A guest asked for a refund for a missing side. The restaurant manager has not called back."},
        {"entry_id": "LE-R014-1123-12", "text": "Deep clean of the dough mixer left for the opening shift."}],
    "do_first": [
        {"entry_id": "LE-R014-1123-09", "text": "Be ready for the engineer between 08:00 and 10:00."},
        {"entry_id": "LE-R014-1123-08", "text": "Find cover for the late shift at 16:00."}],
    "summary": "Five entries are open.", "drafted_by": "a test"}

ACCOUNT = "IA-2611-04"
INCIDENT = {
    "incident_type": "cut", "who_was_affected": "guest", "incident_date": "2026-11-20", "incident_time": "20:15",
    "location": "Table 6",
    "what_happened": "A guest picked up a water glass that had a crack in it. The glass broke in her hand and cut her palm.",
    "injury_or_damage": "A cut to the palm that bled through two plasters. A pad and a bandage were put on.",
    "first_aid_given": "yes", "reported_to_shift_manager": "yes", "area_manager_to_be_phoned_the_same_day": True,
    "next_steps": [
        {"clause": "15.1", "step": "The accident is reported to the shift manager at once. The shift manager wrote the account."},
        {"clause": "15.2", "step": "The shift manager completes the incident form before the end of the shift, and reports "
                                   "the cut to the area manager by phone the same day."},
        {"clause": "15.3", "step": "Nobody admits fault or discusses compensation with the guest. Her contact details are "
                                   "taken and she is told the restaurant manager will call."}],
    "not_in_the_account": ["the guest's contact details"], "drafted_by": "a test"}

CALLS_1_4 = {
    # stores: shift logs and incident accounts
    "get_shift_log": ("get", f"/stores/shift-logs/{LOG_SITE}", None),
    "save_handover_note": ("post", f"/stores/shift-logs/{LOG_SITE}/handover-note", HANDOVER),
    "list_incident_accounts": ("get", "/stores/incident-accounts", None),
    "get_incident_account": ("get", f"/stores/incident-accounts/{ACCOUNT}", None),
    "save_incident_report": ("post", f"/stores/incident-accounts/{ACCOUNT}/report", INCIDENT),
    "submit_incident_report": ("post", f"/stores/incident-accounts/{ACCOUNT}/submit", {"submitted_by": "M. Manager"}),
    # people
    "list_draft_rosters": ("get", "/people/rosters", None),
    "get_draft_roster": ("get", f"/people/rosters/{ROSTER}", None),
    "get_working_time_rules": ("get", "/people/rules", None),
    "save_roster_check": ("post", f"/people/rosters/{ROSTER}/check", ROSTER_CHECK),
    "publish_roster": ("post", f"/people/rosters/{ROSTER}/publish", {"published_by": "N. Manager"}),
    # franchise
    "list_franchisees": ("get", "/franchise/franchisees", None),
    "get_franchisee": ("get", "/franchise/franchisees/FR-01", None),
    "list_franchisee_questions": ("get", "/franchise/questions", None),
    "get_franchisee_question": ("get", "/franchise/questions/FQ-2611-01", None),
}
