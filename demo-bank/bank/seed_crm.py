"""Seed data, part 13: relationship managers' meetings with clients.

Holdings are not stored here. They are read from the core, lending and funds systems, so the totals always agree with them.
Tomorrow, relationship manager Sunniva Haldane-Rook meets three clients (MTG-1001 to MTG-1003). SCENARIOS.md has the right answer for each.
"""

from __future__ import annotations

from datetime import date, timedelta

from .seed_base import d_ago

RM_MAIN = "Sunniva Haldane-Rook"
RM_OTHER = "Bertil Ashgrove-Nye"


def meeting(mid, cid, day, time, rm, purpose, attendees, location, status, notes):
    return {"meeting_id": mid, "customer_id": cid, "date": day, "time": time, "relationship_manager": rm, "purpose": purpose,
            "attendees": attendees, "location": location, "status": status, "notes": notes, "briefs": []}


def build_crm(today: date) -> dict:
    tomorrow = (today + timedelta(days=1)).isoformat()
    m = {}
    m["MTG-1001"] = meeting("MTG-1001", "CUS-1007", tomorrow, "09:30", RM_MAIN, "Review of his savings and a question about moving money abroad.",
                            ["Valdis Orrenmoor", RM_MAIN], "Port Ilvane private banking suite", "scheduled", [])
    m["MTG-1002"] = meeting("MTG-1002", "CUS-1018", tomorrow, "11:00", RM_MAIN, "Update on the equipment loan application and the next documents.",
                            ["Hollis Merriweather-Cole (finance director)", RM_MAIN], "Marlow Reach business centre", "scheduled", [])
    m["MTG-1003"] = meeting("MTG-1003", "CUS-1011", tomorrow, "14:30", RM_MAIN, "Yearly review of his accounts and his pension.",
                            ["Tobias Wrenfield", RM_MAIN], "Tallowby branch", "scheduled", [])
    m["MTG-1004"] = meeting("MTG-1004", "CUS-1019", tomorrow, "10:00", RM_OTHER, "Check-in after the vehicle loan was signed.",
                            ["Lanternfish Logistics owner", RM_OTHER], "Port Ilvane depot", "scheduled", [])
    m["MTG-1005"] = meeting("MTG-1005", "CUS-1018", d_ago(today, 35), "10:00", RM_MAIN, "First talk about replacing two machines.",
                            ["Hollis Merriweather-Cole (finance director)", RM_MAIN], "Marlow Reach business centre", "held",
                            ["The client wants to replace the older of two machines financed by LN-9002.", "He will send three years of accounts."])
    m["MTG-1006"] = meeting("MTG-1006", "CUS-1007", d_ago(today, 120), "15:00", RM_MAIN, "Savings review.", ["Valdis Orrenmoor", RM_MAIN],
                            "Port Ilvane private banking suite", "held",
                            ["The client said he is in a legal dispute in Quenmark. He gave no details.", "He asked how fast he can move money to a Quenmark account."])
    return {"crm_meetings": m}


def sim_meeting(data: dict, today: date, kind: int, num: int) -> tuple[str, str]:
    mid = f"MTG-{1100 + num}"
    tomorrow = (today + timedelta(days=1)).isoformat()
    specs = [("CUS-1016", "Talk about her personal loan application.", "10:00"), ("CUS-1009", "Follow up after her complaint was answered.", "12:00"),
             ("CUS-1013", "Talk about the home loan and the missed payment.", "15:30"), ("CUS-1019", "Routine check-in.", "16:30")]
    cid, purpose, time = specs[kind % 4]
    name = data["customers"][cid]["name"]
    data["crm_meetings"][mid] = meeting(mid, cid, tomorrow, time, RM_MAIN, purpose, [name, RM_MAIN], "Tallowby branch", "scheduled", [])
    msg = (f"A new client meeting {mid} has been booked in the crm system for tomorrow at {time} with {name} ({cid}). The relationship manager is "
           f"{RM_MAIN}. Read it with get_client_meeting and prepare a brief.")
    return mid, msg
