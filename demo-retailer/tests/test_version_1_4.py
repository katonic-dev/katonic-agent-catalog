"""Version 1.4: the people and franchise systems, and the shift logs and incident accounts of the stores system.

Every planted case is read back through the API and compared with the tables in SCENARIOS.md. The breaches of a
roster are worked out from the shifts and the rules the API serves. What a handover note, an incident report or an
answer to a franchisee should hold cannot be worked out by a program, so those tables are compared with the record
sets the service keeps and never serves, and with the words of the entries and accounts it does serve.
"""
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from bodies_1_4 import ACCOUNT, HANDOVER, INCIDENT, LOG_SITE, ROSTER, ROSTER_CHECK
from conftest import H, KEY, TODAY
from retailer.seed import build_all
from retailer.seed_people import find_breaches, rules_markdown
from test_operations import get, post

TEXT = (Path(__file__).resolve().parent.parent / "SCENARIOS.md").read_text(encoding="utf-8")
README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")
LIBRARY = Path(__file__).resolve().parents[2] / "retail" / "policy-library"
TODAY_D = date.fromisoformat(TODAY)
YESTERDAY = "2026-11-23"
ROSTERS = ["RS-261130-R014", "RS-261130-R022", "RS-261130-R047", "RS-261130-R063", "RS-261130-S103", "RS-261130-S106"]
LOG_SITES = ["R-014", "R-031", "R-058", "R-104", "S-101", "S-104"]
RULE_IDS = ["WT-1", "WT-2", "WT-3", "WT-4", "WT-5", "WT-6", "WT-7", "WT-8", "SR-1", "SR-2", "SR-3"]


def section(title):
    return TEXT.split(f"## {title}")[1].split("\n## ")[0]


def rows(prefix, text):
    return [[c.strip() for c in line.strip().strip("|").split("|")] for line in text.splitlines() if line.startswith(f"| {prefix}")]


def simulate(client, kind):
    return post(client, f"/admin/simulate/{kind}")


ROSTER_TEXT = section("Draft rosters")
LOG_TEXT = section("Shift logs")
INCIDENT_TEXT = section("Incident accounts")
FRANCHISE_TEXT = section("Franchisees and their questions")
ARRIVALS = section("Simulated arrivals")


def mins(hhmm):
    return int(hhmm[:2]) * 60 + int(hhmm[3:])


def shifts_of(roster, colleague):
    return sorted((s for s in roster["shifts"] if s["colleague_id"] == colleague), key=lambda s: (s["date"], s["start"]))


def rest_minutes(before, after):
    a = datetime.fromisoformat(f"{before['date']}T{before['end']}")
    b = datetime.fromisoformat(f"{after['date']}T{after['start']}")
    return int((b - a).total_seconds() // 60)


# ================================================================ people: rosters and rules

def test_six_draft_rosters_for_next_week(client):
    listed = get(client, "/people/rosters")
    assert listed["count"] == 6 and listed["retailer_date"] == TODAY
    assert [r["roster_id"] for r in listed["items"]] == ROSTERS
    assert [r["site_id"] for r in listed["items"]] == ["R-014", "R-022", "R-047", "R-063", "S-103", "S-106"]
    table = {r[0]: r for r in rows("RS-", ROSTER_TEXT) if len(r) == 5}
    assert list(table) == ROSTERS
    for r in listed["items"]:
        assert (r["week_start"], r["week_end"], r["status"], r["checks"]) == ("2026-11-30", "2026-12-06", "draft", 0)
        assert date.fromisoformat(r["week_start"]).weekday() == 0 and date.fromisoformat(r["week_start"]) > TODAY_D
        assert [r["site_id"], str(r["colleagues"]), str(r["shifts"])] == table[r["roster_id"]][1:4]
    assert "from 2026-11-30 to 2026-12-06" in ROSTER_TEXT
    assert [r["roster_id"] for r in get(client, "/people/rosters", site_id="S-103")["items"]] == ["RS-261130-S103"]
    assert get(client, "/people/rosters", site_id="R-031")["count"] == 0  # a real site with no roster
    assert get(client, "/people/rosters", status="published")["count"] == 0
    assert get(client, "/people/rosters", status="draft")["count"] == 6
    r = client.get("/people/rosters", headers=H, params={"site_id": "R-999"})
    assert r.status_code == 404 and "list_sites" in r.json()["detail"] and r.json()["applied"] is False
    assert client.get("/people/rosters", headers=H, params={"status": "signed"}).status_code == 422


def test_a_roster_holds_colleagues_by_id_and_role_and_every_shift(client):
    for roster_id in ROSTERS:
        r = get(client, f"/people/rosters/{roster_id}")
        site = get(client, f"/stores/sites/{r['site_id']}")
        assert (r["site_name"], r["town"]) == (site["name"], site["town"])
        assert (r["opens"], r["closes"]) == (("11:00", "22:00") if site["kind"] == "restaurant" else ("07:00", "22:00"))
        assert r["rules_document"] == "Working Time and Staffing Rules, version 1.2" and r["checks"] == []
        assert (r["status"], r["published_by"], r["published_at"]) == ("draft", "", "")
        people = {c["colleague_id"]: c for c in r["colleagues"]}
        digits = int(r["site_id"][2:])
        assert list(people) == [f"C-{digits:03d}{n:02d}" for n in range(1, 13)]
        assert [c["role"] for c in r["colleagues"]] == ["shift_manager"] * 4 + ["team_member"] * 8
        assert [c["colleague_id"][-2:] for c in r["colleagues"] if c["age_band"] == "young_worker"] == ["08", "12"]
        assert [c["colleague_id"][-2:] for c in r["colleagues"] if c["first_aider"]] == ["01", "02", "03", "04", "05", "10"]
        for c in r["colleagues"]:
            assert set(c) == {"colleague_id", "role", "age_band", "first_aider", "contracted_hours", "rostered_hours", "days_rostered"}
            own = shifts_of(r, c["colleague_id"])
            assert c["rostered_hours"] == sum(s["hours"] for s in own) and c["days_rostered"] == len({s["day"] for s in own})
        assert [s["shift_id"] for s in r["shifts"]] == [f"SH-{r['site_id'].replace('-', '')}-{n:02d}" for n in range(1, len(r["shifts"]) + 1)]
        assert r["shifts"] == sorted(r["shifts"], key=lambda s: (s["date"], s["start"], s["colleague_id"]))
        for s in r["shifts"]:
            assert set(s) == {"shift_id", "colleague_id", "role", "day", "date", "start", "end", "hours", "break_minutes"}
            assert s["role"] == people[s["colleague_id"]]["role"] and r["week_start"] <= s["date"] <= r["week_end"]
            assert date.fromisoformat(s["date"]).strftime("%A").lower() == s["day"]
            assert s["hours"] == (mins(s["end"]) - mins(s["start"])) / 60 and s["hours"] > 0 and s["break_minutes"] in (0, 30)
        # no name anywhere: a colleague is an id and a role
        assert "name" not in {k for c in r["colleagues"] for k in c}
    r = client.get("/people/rosters/RS-261130-R031", headers=H)
    assert r.status_code == 404 and "list_draft_rosters" in r.json()["detail"]


def test_the_rules_are_served_and_are_the_library_document(client):
    rules = get(client, "/people/rules")
    assert (rules["document"], rules["version"], rules["owner"]) == ("Working Time and Staffing Rules", "1.2", "Head of People")
    assert "invented" in rules["notice"] and "not the rules of any real country" in rules["part_a"]
    assert [r["rule"] for r in rules["rules"]] == RULE_IDS
    assert [r["part"] for r in rules["rules"]] == ["working_time"] * 8 + ["staffing"] * 3
    limits = {r["rule"]: (r["limit"], r["unit"]) for r in rules["rules"]}
    assert limits == {"WT-1": (10, "hours"), "WT-2": (11, "hours"), "WT-3": (48, "hours"), "WT-4": (30, "minutes"),
                      "WT-5": (8, "hours"), "WT-6": (40, "hours"), "WT-7": ("22:00", "time of day"), "WT-8": (1, "days"),
                      "SR-1": (1, "shift managers"), "SR-2": (2, "colleagues"), "SR-3": (1, "first aiders")}
    assert "exactly on a limit keeps the rule" in rules["how_hours_and_times_are_counted"]
    assert "contracted hours" in rules["what_the_rules_do_not_decide"]
    text = (LIBRARY / "working-time-and-staffing-rules-v1.2.md").read_text(encoding="utf-8")
    assert text == rules_markdown() == rules["text"]
    assert "invented" in text.splitlines()[0] and "Version: 1.2" in text
    table = rows("WT-", ROSTER_TEXT) + rows("SR-", ROSTER_TEXT)
    assert [(r[0], r[1], r[2]) for r in table] == [(r["rule"], r["title"], r["text"]) for r in rules["rules"]]
    for r in rules["rules"]:
        assert f"### {r['rule']}. {r['title']}" in text and r["text"] in text


EXPECTED = {
    "RS-261130-R014": [("WT-2", "C-01407", "SH-R014-19", "wednesday"), ("WT-4", "C-01409", "SH-R014-39", "friday")],
    "RS-261130-R022": [],
    "RS-261130-R047": [("SR-1", "", "", "sunday"), ("WT-7", "C-04712", "SH-R047-46", "saturday")],
    "RS-261130-R063": [],
    "RS-261130-S103": [("SR-2", "C-10301", "SH-S103-25", "thursday"), ("WT-3", "C-10306", "", "")],
    "RS-261130-S106": [],
}


def test_the_six_planted_breaches_and_no_others(client):
    table = [r for r in rows("RS-", ROSTER_TEXT) if len(r) == 6]
    assert len(table) == 6
    counts = {r[0]: int(r[4]) for r in rows("RS-", ROSTER_TEXT) if len(r) == 5}
    for roster_id in ROSTERS:
        roster = get(client, f"/people/rosters/{roster_id}")
        found = [(b["rule"], b["colleague_id"], b["shift_id"], b["day"]) for b in find_breaches(roster)]
        assert found == EXPECTED[roster_id], roster_id
        assert [tuple(r[1:5]) for r in table if r[0] == roster_id] == found, roster_id
        assert counts[roster_id] == len(found)


def test_each_breach_shows_in_the_shifts_the_api_serves(client):
    r14 = get(client, "/people/rosters/RS-261130-R014")
    own = shifts_of(r14, "C-01407")
    tue, wed = own[0], own[1]
    assert (tue["shift_id"], tue["day"], tue["start"], tue["end"]) == ("SH-R014-16", "tuesday", "16:30", "23:30")
    assert (wed["shift_id"], wed["day"], wed["start"]) == ("SH-R014-19", "wednesday", "10:00")
    assert rest_minutes(tue, wed) == 630 and "The rest is 10 hours 30 minutes" in ROSTER_TEXT
    fri = next(s for s in r14["shifts"] if s["shift_id"] == "SH-R014-39")
    assert (fri["colleague_id"], fri["start"], fri["end"], fri["hours"], fri["break_minutes"]) == ("C-01409", "16:00", "23:00", 7.0, 0)
    # every other shift longer than 6 hours has its break
    assert [s["shift_id"] for s in r14["shifts"] if s["hours"] > 6 and s["break_minutes"] < 30] == ["SH-R014-39"]

    r47 = get(client, "/people/rosters/RS-261130-R047")
    young = {c["colleague_id"] for c in r47["colleagues"] if c["age_band"] == "young_worker"}
    late = [(s["shift_id"], s["colleague_id"], s["day"], s["end"]) for s in r47["shifts"] if s["colleague_id"] in young and s["end"] > "22:00"]
    assert late == [("SH-R047-46", "C-04712", "saturday", "23:00")]
    managers = [(s["colleague_id"], s["start"], s["end"]) for s in r47["shifts"] if s["day"] == "sunday" and s["role"] == "shift_manager"]
    assert managers == [("C-04703", "10:00", "16:00"), ("C-04704", "17:00", "23:00")]
    first_aiders = {c["colleague_id"] for c in r47["colleagues"] if c["first_aider"]}
    assert any(s["colleague_id"] in first_aiders and s["start"] <= "16:00" and s["end"] >= "17:00"
               for s in r47["shifts"] if s["day"] == "sunday")

    s103 = get(client, "/people/rosters/RS-261130-S103")
    hours = {c["colleague_id"]: c["rostered_hours"] for c in s103["colleagues"]}
    assert hours["C-10306"] == 49.0 and [c for c, h in hours.items() if h > 48] == ["C-10306"]
    assert {c["colleague_id"]: c["days_rostered"] for c in s103["colleagues"]}["C-10306"] == 6
    at_open = [s["colleague_id"] for s in s103["shifts"] if s["day"] == "thursday" and s["start"] <= "07:00" < s["end"]]
    assert at_open == ["C-10301"]
    assert sorted(s["colleague_id"] for s in s103["shifts"] if s["day"] == "thursday" and s["start"] == "08:00") == ["C-10305", "C-10307"]


def test_a_figure_exactly_on_a_limit_is_not_a_breach(client):
    r63 = get(client, "/people/rosters/RS-261130-R063")
    own = shifts_of(r63, "C-06307")
    assert (own[0]["day"], own[0]["end"], own[1]["day"], own[1]["start"]) == ("tuesday", "23:00", "wednesday", "10:00")
    assert rest_minutes(own[0], own[1]) == 660
    sat = next(s for s in shifts_of(r63, "C-06312") if s["day"] == "saturday")
    assert (sat["start"], sat["end"], sat["hours"], sat["break_minutes"]) == ("14:00", "22:00", 8.0, 30)
    long = next(s for s in shifts_of(r63, "C-06304") if s["day"] == "saturday")
    assert (long["start"], long["end"], long["hours"]) == ("13:00", "23:00", 10.0)
    assert max(s["hours"] for s in r63["shifts"]) == 10.0

    s106 = get(client, "/people/rosters/RS-261130-S106")
    people = {c["colleague_id"]: c for c in s106["colleagues"]}
    assert people["C-10606"]["rostered_hours"] == 48.0 and people["C-10606"]["days_rostered"] == 6
    assert people["C-10608"]["rostered_hours"] == 40.0 and people["C-10608"]["age_band"] == "young_worker"
    at_open = [s["colleague_id"] for s in s106["shifts"] if s["day"] == "thursday" and s["start"] <= "07:00" < s["end"]]
    assert at_open == ["C-10601", "C-10605"]
    for line in ("C-06307 has exactly 11 hours of rest", "ends at exactly 22:00", "a Saturday shift of exactly 10 hours",
                 "C-10606 is rostered for exactly 48 hours", "exactly two colleagues, C-10601 and C-10605",
                 "C-10608, a young worker, is rostered for exactly 40 hours"):
        assert line in ROSTER_TEXT, line
    # the pattern itself: an early shift in a restaurant is exactly 6 hours with no break
    assert {(s["hours"], s["break_minutes"]) for s in r63["shifts"] if s["start"] == "10:00"} == {(6.0, 0)}


def test_save_roster_check_is_a_draft_and_changes_no_shift(client, store):
    path = f"/people/rosters/{ROSTER}/check"
    before = get(client, f"/people/rosters/{ROSTER}")
    saved = post(client, path, ROSTER_CHECK)
    assert (saved["applied"], saved["kind"], saved["roster_id"]) == (True, "draft", ROSTER)
    draft = saved["draft"]
    assert (draft["version"], draft["drafted_by"]) == (1, "a test") and len(draft["breaches"]) == 2
    assert set(draft) == {"version", "drafted_by", "drafted_at", "breaches", "summary"}
    assert set(draft["breaches"][0]) == {"rule", "colleague_id", "shift_id", "day", "what_the_roster_shows"}
    # a field that proposes a change is not part of the form, so it is not kept
    with_proposal = {**ROSTER_CHECK, "proposed_changes": [{"shift_id": "SH-S103-25", "give_to": "C-10305"}]}
    again = post(client, path, with_proposal)["draft"]
    assert again["version"] == 2 and "proposed_changes" not in again
    after = get(client, f"/people/rosters/{ROSTER}")
    assert after["shifts"] == before["shifts"] and after["colleagues"] == before["colleagues"] and after["status"] == "draft"
    assert [c["version"] for c in after["checks"]] == [1, 2]
    assert post(client, "/people/rosters/RS-261130-R022/check", {"breaches": []})["draft"]["drafted_by"] == "agent"
    assert get(client, "/people/rosters")["items"][4]["checks"] == 2
    assert get(client, "/admin/state")["counts"]["roster_checks"] == 3


def test_a_roster_check_that_does_not_fit_the_roster_is_refused(client, store):
    path = f"/people/rosters/{ROSTER}/check"
    ok = {"rule": "WT-4", "colleague_id": "C-10306", "shift_id": "SH-S103-42", "day": "saturday", "what_the_roster_shows": "x"}

    def refused(breach, words):
        r = post(client, path, {"breaches": [breach]}, 422)
        assert r["applied"] is False and words in r["detail"] and "Nothing was saved" in r["detail"], r["detail"]

    assert post(client, path, {"breaches": [ok]})["draft"]["version"] == 1
    refused({**ok, "colleague_id": "C-01407"}, "C-01407 is not a colleague on roster RS-261130-S103")
    refused({**ok, "shift_id": "SH-R014-19"}, "SH-R014-19 is not a shift on roster RS-261130-S103")
    refused({**ok, "colleague_id": ""}, "a working time rule needs the colleague_id")
    refused({**ok, "shift_id": ""}, "it needs the shift_id")
    refused({**ok, "colleague_id": "C-10301"}, "shift SH-S103-42 belongs to C-10306, not to C-10301")
    refused({**ok, "day": "sunday"}, "shift SH-S103-42 is on saturday, not on sunday")
    refused({"rule": "WT-3", "colleague_id": "C-10306", "day": "saturday", "what_the_roster_shows": "x"}, "about the whole week")
    refused({"rule": "WT-3", "colleague_id": "C-10306", "shift_id": "SH-S103-42", "what_the_roster_shows": "x"}, "about the whole week")
    refused({"rule": "SR-2", "what_the_roster_shows": "x"}, "a staffing rule needs the day")
    for bad in ({**ok, "rule": "WT-9"}, {**ok, "rule": "wt-4"}, {**ok, "day": "Saturday"}, {**ok, "what_the_roster_shows": ""},
                {k: v for k, v in ok.items() if k != "what_the_roster_shows"}):
        r = post(client, path, {"breaches": [bad]}, 422)
        assert r["detail"].startswith("The request is not valid.")
    assert "'WT-1'" in post(client, path, {"breaches": [{**ok, "rule": "WT-9"}]}, 422)["detail"]
    # a staffing rule may name nobody, or the one colleague on shift alone
    assert post(client, path, {"breaches": [{"rule": "SR-1", "day": "sunday", "what_the_roster_shows": "x"}]})["draft"]["version"] == 2
    assert len(store.data["draft_rosters"][ROSTER]["checks"]) == 2
    post(client, "/people/rosters/RS-000000-R014/check", {"breaches": []}, 404)


def test_publish_roster_waits_for_a_check_and_a_named_manager(client, store):
    path = f"/people/rosters/{ROSTER}/publish"
    before = get(client, f"/people/rosters/{ROSTER}")["shifts"]
    r = post(client, path, {"published_by": "N. Manager"}, 409)
    assert r["applied"] is False and "has no saved check" in r["detail"] and "Use save_roster_check first" in r["detail"]
    post(client, f"/people/rosters/{ROSTER}/check", ROSTER_CHECK)
    assert "published_by" in post(client, path, {}, 422)["detail"]
    post(client, path, {"published_by": ""}, 422)
    done = post(client, path, {"published_by": "N. Manager", "note": "Two shifts changed by hand."})
    assert (done["applied"], done["kind"], done["status"], done["published_by"]) == (True, "change", "published", "N. Manager")
    roster = get(client, f"/people/rosters/{ROSTER}")
    assert roster["status"] == "published" and roster["published_by"] == "N. Manager" and roster["published_at"]
    assert roster["shifts"] == before  # publishing changes no shift
    again = post(client, path, {"published_by": "Someone Else"}, 409)
    assert "already published, by N. Manager" in again["detail"]
    assert [r["roster_id"] for r in get(client, "/people/rosters", status="published")["items"]] == [ROSTER]
    counts = get(client, "/admin/state")["counts"]
    assert (counts["draft_rosters"], counts["rosters_published"], counts["roster_checks"]) == (6, 1, 1)
    post(client, "/people/rosters/RS-000000-R014/publish", {"published_by": "N. Manager"}, 404)


# ================================================================ stores: shift logs

def test_yesterdays_shift_log_of_six_sites(client, store):
    table = rows("`", LOG_TEXT)
    assert [r[0].strip("`") for r in table] == LOG_SITES
    total = still_open = 0
    for site, on, entries, open_ids, first in table:
        site = site.strip("`")
        log = get(client, f"/stores/shift-logs/{site}")
        assert log == get(client, f"/stores/shift-logs/{site}", log_date=YESTERDAY)
        info = get(client, f"/stores/sites/{site}")
        assert (log["site_id"], log["date"], log["retailer_date"]) == (site, YESTERDAY, TODAY) and on == YESTERDAY
        assert (log["site_name"], log["town"]) == (info["name"], info["town"]) and log["handover_notes"] == []
        assert len(log["entries"]) == int(entries)
        stem = f"LE-{site.replace('-', '')}-1123"
        assert [e["entry_id"] for e in log["entries"]] == [f"{stem}-{n:02d}" for n in range(1, len(log["entries"]) + 1)]
        assert [e["time"] for e in log["entries"]] == sorted(e["time"] for e in log["entries"])
        for e in log["entries"]:
            assert set(e) == {"entry_id", "time", "category", "logged_by", "logged_by_role", "text"}
            assert e["category"] in ("routine", "delivery", "equipment_fault", "complaint", "cash_difference", "staffing_gap", "task")
            assert re.fullmatch(r"C-\d{5}", e["logged_by"]) and e["logged_by_role"] == "shift_manager" and e["text"].endswith(".")
        answer = store.data["shift_log_answers"][f"{site}:{YESTERDAY}"]
        assert open_ids.split(", ") == answer["open_entries"] and first == answer["do_first"] and first in answer["open_entries"]
        total += len(log["entries"])
        still_open += len(answer["open_entries"])
        # the entry to do first names a time on the next day, and every open entry is explained in the file
        by = {e["entry_id"]: e for e in log["entries"]}
        assert "tomorrow" in by[first]["text"] and re.search(r"\d\d:\d\d", by[first]["text"])
        for entry in answer["open_entries"]:
            assert f"`{site}` `{entry}` ({by[entry]['time']}, {by[entry]['category']}): " in LOG_TEXT, entry
        assert "open_entries" not in json.dumps(log) and "do_first" not in json.dumps(log)
    assert (total, still_open) == (76, 23) and "hold 76 entries, and 23 of them are still open" in LOG_TEXT
    assert get(client, "/admin/state")["counts"]["shift_logs"] == 6


def test_what_the_open_entries_say(client):
    def text(site, n):
        log = get(client, f"/stores/shift-logs/{site}")
        return log["entries"][n - 1]["text"]

    assert "between 08:00 and 10:00" in text("R-014", 9) and "6.5" in text("R-014", 9)
    assert "tomorrow's late shift, which starts at 16:00" in text("R-014", 8) and "C-01411" in text("R-014", 8)
    assert "4.50 over. Recorded." in text("R-014", 13)
    assert "tomorrow at 07:30" in text("R-031", 7) and "reported to the restaurant manager by phone at 19:55" in text("R-031", 9)
    assert "tomorrow at 09:00" in text("R-058", 9) and "23.80" in text("R-058", 9) and "tomorrow at 14:00" in text("R-058", 8)
    assert "tomorrow at 10:00" in text("R-104", 7) and "22.00 over" in text("R-104", 10) and "Not reported" in text("R-104", 10)
    assert "tomorrow before 10:00" in text("S-101", 9) and "tomorrow before 12:00" in text("S-101", 3)
    assert "tomorrow's delivery at 06:30" in text("S-104", 6) and "No time given yet" in text("S-104", 9)
    assert "48.00 short" in text("S-104", 11) and "reported to the store manager by phone at 20:25" in text("S-104", 11)


def test_a_shift_log_that_is_not_held_answers_404(client):
    r = client.get("/stores/shift-logs/R-999", headers=H)
    assert r.status_code == 404 and "list_sites" in r.json()["detail"]
    r = client.get("/stores/shift-logs/R-022", headers=H)
    assert r.status_code == 404 and "The sites with a shift log are R-014, R-031, R-058, R-104, S-101, S-104." in r.json()["detail"]
    r = client.get("/stores/shift-logs/R-014", headers=H, params={"log_date": "2026-11-20"})
    assert r.status_code == 404 and "R-014 has a shift log for 2026-11-23." in r.json()["detail"]
    r = client.get("/stores/shift-logs/R-014", headers=H, params={"log_date": "yesterday"})
    assert r.status_code == 422 and "log_date" in r.json()["detail"]


def test_save_handover_note_is_a_draft_that_rests_on_the_log(client, store):
    path = f"/stores/shift-logs/{LOG_SITE}/handover-note"
    before = get(client, f"/stores/shift-logs/{LOG_SITE}")["entries"]
    saved = post(client, path, HANDOVER)
    assert (saved["applied"], saved["kind"], saved["site_id"], saved["date"]) == (True, "draft", "R-014", YESTERDAY)
    draft = saved["draft"]
    assert set(draft) == {"version", "drafted_by", "drafted_at", "what_happened", "still_open", "do_first", "summary"}
    assert (draft["version"], draft["drafted_by"]) == (1, "a test")
    answer = store.data["shift_log_answers"][f"R-014:{YESTERDAY}"]
    assert [x["entry_id"] for x in draft["still_open"]] == answer["open_entries"] and draft["do_first"][0]["entry_id"] == answer["do_first"]
    log = get(client, f"/stores/shift-logs/{LOG_SITE}")
    assert log["entries"] == before and len(log["handover_notes"]) == 1
    # a line that rests on no entry of this log is refused: a note cannot hold what the log does not
    made_up = {**HANDOVER, "still_open": HANDOVER["still_open"] + [{"entry_id": "LE-R014-1123-15", "text": "The fryer is broken."}]}
    r = post(client, path, made_up, 422)
    assert "still_open, line 6: LE-R014-1123-15 is not an entry of the shift log of R-014 for 2026-11-23" in r["detail"]
    assert "LE-R014-1123-01 to LE-R014-1123-14" in r["detail"] and "Nothing was saved" in r["detail"]
    other = {**HANDOVER, "what_happened": [{"entry_id": "LE-R031-1123-04", "text": "A hair in a wrap."}]}
    assert "what_happened, line 1: LE-R031-1123-04 is not an entry" in post(client, path, other, 422)["detail"]
    first = {**HANDOVER, "do_first": [{"entry_id": "LE-R014-1123-13", "text": "Check till 1."}]}
    assert "do_first, line 1: LE-R014-1123-13 is not under still_open" in post(client, path, first, 422)["detail"]
    post(client, path, {**HANDOVER, "still_open": [{"entry_id": "LE-R014-1123-06", "text": ""}]}, 422)
    post(client, path, {**HANDOVER, "still_open": [{"text": "No entry."}]}, 422)
    # a log that leaves nothing open is saved with empty lists, and the date can be given
    empty = post(client, path + f"?log_date={YESTERDAY}", {})
    assert empty["draft"]["version"] == 2 and empty["draft"]["still_open"] == [] and empty["draft"]["drafted_by"] == "agent"
    assert len(store.data["shift_logs"][f"R-014:{YESTERDAY}"]["handover_notes"]) == 2
    assert get(client, "/admin/state")["counts"]["handover_notes"] == 2
    post(client, "/stores/shift-logs/R-022/handover-note", HANDOVER, 404)
    post(client, "/stores/shift-logs/R-999/handover-note", HANDOVER, 404)
    post(client, path + "?log_date=2026-11-20", HANDOVER, 404)


# ================================================================ stores: incident accounts

def test_six_incident_accounts_and_the_right_answers_for_the_form(client, store):
    listed = get(client, "/stores/incident-accounts")
    assert listed["count"] == 6 and [a["account_id"] for a in listed["items"]] == [f"IA-2611-0{n}" for n in range(1, 7)]
    table = rows("IA-", INCIDENT_TEXT)
    assert [r[0] for r in table] == [f"IA-2611-0{n}" for n in range(1, 7)]
    assert [r[3] for r in table] == ["fall", "burn", "near_miss", "cut", "property_damage", "guest_illness"]
    for n, (aid, site, on, kind, who, time, first_aid, told, phoned, clauses) in enumerate(table, start=1):
        a = get(client, f"/stores/incident-accounts/{aid}")
        row = listed["items"][n - 1]
        assert set(a) == {"demo_data", "account_id", "site_id", "site_name", "town", "incident_date", "written_at", "written_by",
                          "written_by_role", "account", "procedure", "status", "reports", "submitted_by", "submitted_at"}
        assert (a["site_id"], a["incident_date"]) == (site, on) == (row["site_id"], row["incident_date"])
        assert on == (TODAY_D - timedelta(days=n)).isoformat()
        assert (a["status"], a["reports"], a["submitted_by"], row["reports"]) == ("account_received", [], "", 0)
        assert a["procedure"] == "Store Procedures Manual, version 3.1, SP-15 Accidents and incidents"
        assert re.fullmatch(r"C-\d{5}", a["written_by"]) and a["written_by_role"] in ("team_member", "shift_manager")
        assert len(a["account"]) > 200 and re.search(r"\bI\b", a["account"])
        right = store.data["incident_answers"][aid]
        assert (kind, who, first_aid, told) == (right["incident_type"], right["who_was_affected"], right["first_aid_given"],
                                                right["reported_to_shift_manager"])
        assert (phoned == "yes") == right["area_manager_to_be_phoned_the_same_day"] and clauses.split(", ") == right["clauses"]
        assert time == (right["incident_time"] or "not given")
        if right["incident_time"]:
            assert right["incident_time"] in a["account"], aid
        # the right answers follow SP-15: the list of clause 15.2, and clause 15.3 for a guest
        on_the_list = kind in ("fall", "burn", "guest_illness") or aid == "IA-2611-04"
        assert right["area_manager_to_be_phoned_the_same_day"] is on_the_list
        assert ("15.3" in right["clauses"]) == (who == "guest") and ("15.1" in right["clauses"]) == (who != "nobody")
        assert "incident_type" not in json.dumps(a) and "clauses" not in json.dumps(a)
    manual = (LIBRARY / "store-procedures-manual.md").read_text(encoding="utf-8")
    assert "## SP-15 Accidents and incidents (version 2.1)" in manual and "Version: 3.1" in manual
    for clause in ("15.1 Any accident", "15.2 The shift manager completes the incident form", "15.3 Do not admit fault"):
        assert clause in manual
    assert "A burn, a cut needing more than a plaster, a fall, or any report of a guest becoming ill" in manual


def test_what_the_accounts_say(client, store):
    text = {n: get(client, f"/stores/incident-accounts/IA-2611-0{n}")["account"] for n in range(1, 7)}
    assert "I fell on my left side" in text[1] and "told the shift manager straight away" in text[1] and "cold pack" in text[1]
    assert "it has blistered" in text[2] and "burn dressing" in text[2]
    assert "Nobody was hit and nobody was hurt" in text[3] and "This morning" in text[3] and not re.search(r"\d\d:\d\d", text[3])
    assert "bled through two plasters" in text[4] and "She left before I took her phone number" in text[4]
    assert "nobody was hurt" in text[5] and "I have not told anyone else yet" in text[5]
    assert "her lips were swelling" in text[6] and "drove her to hospital" in text[6] and "first aid" not in text[6]
    assert store.data["incident_answers"]["IA-2611-03"]["not_in_the_account"] == ["the time of the incident"]
    assert store.data["incident_answers"]["IA-2611-04"]["not_in_the_account"] == ["the guest's contact details"]
    assert "listed as not in the account" in INCIDENT_TEXT
    assert get(client, "/stores/incident-accounts", site_id="R-031")["items"][0]["account_id"] == "IA-2611-04"
    assert get(client, "/stores/incident-accounts", site_id="R-022")["count"] == 0
    assert get(client, "/stores/incident-accounts", status="report_submitted")["count"] == 0
    assert client.get("/stores/incident-accounts", headers=H, params={"site_id": "R-999"}).status_code == 404
    assert client.get("/stores/incident-accounts", headers=H, params={"status": "closed"}).status_code == 422
    r = client.get("/stores/incident-accounts/IA-2611-99", headers=H)
    assert r.status_code == 404 and "list_incident_accounts" in r.json()["detail"]


def test_save_incident_report_is_a_draft_checked_against_the_procedure(client, store):
    path = f"/stores/incident-accounts/{ACCOUNT}/report"
    saved = post(client, path, INCIDENT)
    assert (saved["applied"], saved["kind"], saved["account_id"]) == (True, "draft", ACCOUNT)
    draft = saved["draft"]
    assert (draft["version"], draft["drafted_by"], draft["incident_type"], draft["who_was_affected"]) == (1, "a test", "cut", "guest")
    assert [x["clause"] for x in draft["next_steps"]] == ["15.1", "15.2", "15.3"]
    right = store.data["incident_answers"][ACCOUNT]
    for key in ("incident_type", "who_was_affected", "incident_date", "incident_time", "first_aid_given",
                "reported_to_shift_manager", "area_manager_to_be_phoned_the_same_day", "not_in_the_account"):
        assert draft[key] == right[key], key
    account = get(client, f"/stores/incident-accounts/{ACCOUNT}")
    assert account["status"] == "account_received" and len(account["reports"]) == 1  # a draft submits nothing

    def refused(change, words):
        r = post(client, path, {**INCIDENT, **change}, 422)
        assert r["applied"] is False and words in r["detail"], r["detail"]

    refused({"incident_date": "2026-11-21"}, "account IA-2611-04 is dated 2026-11-20, not 2026-11-21")
    refused({"next_steps": [INCIDENT["next_steps"][0], INCIDENT["next_steps"][2]]}, "no step cites clause 15.2")
    refused({"next_steps": INCIDENT["next_steps"][:2]}, "no step cites clause 15.3")
    refused({"next_steps": []}, "next_steps")
    refused({"next_steps": [{"clause": "15.4", "step": "x"}]}, "'15.1', '15.2' or '15.3'")
    refused({"incident_type": "slip"}, "incident_type")
    refused({"who_was_affected": "customer"}, "who_was_affected")
    refused({"incident_time": "8pm"}, "incident_time")
    refused({"first_aid_given": "maybe"}, "first_aid_given")
    refused({"area_manager_to_be_phoned_the_same_day": "perhaps"}, "area_manager_to_be_phoned_the_same_day")
    refused({"what_happened": ""}, "what_happened")
    post(client, path, {k: v for k, v in INCIDENT.items() if k != "location"}, 422)
    # a near miss: no time in the account, the form only, nobody phoned
    near = {"incident_type": "near_miss", "who_was_affected": "nobody", "incident_date": "2026-11-21", "incident_time": "",
            "location": "Stockroom", "what_happened": "A stack of four crates tipped off a roll cage and hit nobody.",
            "first_aid_given": "no", "reported_to_shift_manager": "yes", "area_manager_to_be_phoned_the_same_day": False,
            "next_steps": [{"clause": "15.2", "step": "The shift manager completes the incident form before the end of the shift."}],
            "not_in_the_account": ["the time of the incident"]}
    assert post(client, "/stores/incident-accounts/IA-2611-03/report", near)["draft"]["incident_time"] == ""
    assert len(store.data["incident_accounts"][ACCOUNT]["reports"]) == 1
    assert post(client, path, {**INCIDENT, "drafted_by": "second"})["draft"]["version"] == 2
    post(client, "/stores/incident-accounts/IA-2611-99/report", INCIDENT, 404)
    assert get(client, "/admin/state")["counts"]["incident_reports_drafted"] == 3


def test_submit_incident_report_waits_for_a_form_and_a_named_manager(client, store):
    path = f"/stores/incident-accounts/{ACCOUNT}/submit"
    r = post(client, path, {"submitted_by": "M. Manager"}, 409)
    assert r["applied"] is False and "No report form is saved" in r["detail"] and "Use save_incident_report first" in r["detail"]
    post(client, f"/stores/incident-accounts/{ACCOUNT}/report", INCIDENT)
    post(client, f"/stores/incident-accounts/{ACCOUNT}/report", {**INCIDENT, "drafted_by": "second"})
    assert "submitted_by" in post(client, path, {}, 422)["detail"]
    done = post(client, path, {"submitted_by": "M. Manager"})
    assert (done["applied"], done["kind"], done["status"], done["submitted_by"], done["submitted_version"]) == (
        True, "change", "report_submitted", "M. Manager", 2)
    account = get(client, f"/stores/incident-accounts/{ACCOUNT}")
    assert (account["status"], account["submitted_by"], account["submitted_version"]) == ("report_submitted", "M. Manager", 2)
    assert account["submitted_at"] and len(account["reports"]) == 2
    assert "already submitted, by M. Manager" in post(client, path, {"submitted_by": "Another"}, 409)["detail"]
    assert [a["account_id"] for a in get(client, "/stores/incident-accounts", status="report_submitted")["items"]] == [ACCOUNT]
    assert get(client, "/stores/incident-accounts", status="account_received")["count"] == 5
    counts = get(client, "/admin/state")["counts"]
    assert (counts["incident_accounts"], counts["incident_reports_drafted"], counts["incident_reports_submitted"]) == (6, 2, 1)
    post(client, "/stores/incident-accounts/IA-2611-99/submit", {"submitted_by": "M. Manager"}, 404)


# ================================================================ franchise

def test_three_franchisees_with_their_restaurants(client):
    listed = get(client, "/franchise/franchisees")
    table = rows("FR-", FRANCHISE_TEXT)
    assert listed["count"] == 3 == len(table)
    stores = {s["franchisee"]: s for s in get(client, "/stores/sites", franchised="true")["items"]}
    assert len(stores) == 3
    for row, (fid, company, since, site) in zip(listed["items"], table):
        f = get(client, f"/franchise/franchisees/{fid}")
        assert (row["franchisee_id"], row["company"], str(row["franchisee_since"]), row["restaurants"]) == (fid, company, since, [site])
        assert (f["company"], f["franchisee_since"]) == (company, int(since)) and len(f["restaurants"]) == 1
        s = stores[company]
        assert f["restaurants"][0] == {k: s[k] for k in ("site_id", "name", "town", "street", "area", "area_manager")}
        assert f["operations_manual"] == "Franchise Operations Manual, version 3.0" and f["brand_standards"] == "Brand Standards, version 2.0"
        assert "not held in this system" in f["agreement_note"] and f["franchise_team_email"] == "franchise.team@rowanmere.example"
    assert [r[0] for r in table] == ["FR-01", "FR-02", "FR-03"] and [r[3] for r in table] == ["R-090", "R-104", "R-117"]
    assert [r["questions"] for r in listed["items"]] == [6, 5, 6]
    r = client.get("/franchise/franchisees/FR-09", headers=H)
    assert r.status_code == 404 and "list_franchisees" in r.json()["detail"]


def test_seventeen_questions_and_where_each_is_answered(client, store):
    listed = get(client, "/franchise/questions")
    table = rows("FQ-", FRANCHISE_TEXT)
    assert listed["count"] == 17 == len(table) and "holds no answer" not in listed["items"][0]
    assert "does not hold the wording" in listed["documents_note"] and "franchise team" in listed["documents_note"]
    assert [q["question_id"] for q in listed["items"]] == [f"FQ-2611-{n:02d}" for n in range(1, 18)] == [r[0] for r in table]
    assert [q["asked_on"] for q in listed["items"]] == sorted(q["asked_on"] for q in listed["items"])
    manual = (LIBRARY / "franchise-operations-manual-v3.0.md").read_text(encoding="utf-8")
    standards = (LIBRARY / "brand-standards-v2.0.md").read_text(encoding="utf-8")
    assert "invented" in manual.splitlines()[0] and "Version: 3.0" in manual
    kinds = []
    for q, (qid, fid, asked, kind, where, question, short) in zip(listed["items"], table):
        one = get(client, f"/franchise/questions/{qid}")
        assert set(q) == {"question_id", "franchisee_id", "company", "asked_on", "question"}
        assert (q["franchisee_id"], q["asked_on"], q["question"]) == (fid, asked, question) == (one["franchisee_id"], one["asked_on"], one["question"])
        assert one["restaurants"] == get(client, f"/franchise/franchisees/{fid}")["restaurants"][0]["site_id"].split()
        right = store.data["franchise_answers"][qid]
        assert (kind, short) == (right["kind"], right["answer_in_short"])
        assert where == (", ".join(right["sections"]) or "nowhere")
        for ref in right["sections"]:
            if ref.startswith("BS-"):
                assert re.search(rf"^{re.escape(ref[3:])} ", standards, re.M), ref
            else:
                assert re.search(rf"^{re.escape(ref)} ", manual, re.M), ref
        kinds.append(kind)
        assert "answer" not in json.dumps(one).replace("holds no answer", "").replace("An answer to a question", "")
    assert kinds == ["answered"] * 12 + ["silent"] * 3 + ["franchise_agreement"] * 2
    assert [r[4] for r in table[12:]] == ["nowhere", "nowhere", "nowhere", "7.1", "7.1"]
    assert [r["franchisee_id"] for r in get(client, "/franchise/questions", franchisee_id="FR-02")["items"]] == ["FR-02"] * 5
    assert client.get("/franchise/questions", headers=H, params={"franchisee_id": "FR-09"}).status_code == 404
    r = client.get("/franchise/questions/FQ-2611-99", headers=H)
    assert r.status_code == 404 and "list_franchisee_questions" in r.json()["detail"]


def test_the_manual_says_what_the_scenarios_say(client):
    manual = (LIBRARY / "franchise-operations-manual-v3.0.md").read_text(encoding="utf-8")
    assert [line for line in manual.splitlines() if line.startswith("## ")] == [
        "## 1. Fees and reporting dates", "## 2. Brand standards audits", "## 3. Menu and pricing freedom", "## 4. Local marketing",
        "## 5. Equipment and refits", "## 6. Supply through approved suppliers", "## 7. What this manual does not cover"]
    for words in ("1.2 The weekly sales report covers Monday to Sunday. It is sent through the franchisee website by 12:00 on the Tuesday",
                  "1.1 The royalty is 6 percent of net sales", "payable by the 20th", "2.1 Each franchised restaurant has two audits a year",
                  "A score of 20 or more is a pass", "within 14 days of the audit, and is audited again within 60 days",
                  "within 7 days of receiving the audit report", "up to three local items", "at least 30 days before",
                  "up to 10 percent above the recommended price list", "Approval takes up to 10 working days",
                  "at least 1 percent of net sales", "every 7 years", "The franchisee pays for a refit",
                  "milk, fresh produce and ice from a local shop for up to 3 days", "within 24 hours of the first purchase",
                  "7.1 The franchise agreement itself", "franchise.team@rowanmere.example",
                  "7.4 A question this manual does not answer goes to the franchise team"):
        assert words in manual, words
    standards = (LIBRARY / "brand-standards-v2.0.md").read_text(encoding="utf-8")
    assert "taken down within 24 hours of its end" in standards
    for word in ("holiday", "delivery app", "uniform", "renew", "territory"):
        hits = [line for line in manual.splitlines() if word in line.lower() and not line.startswith("7.1")]
        assert hits == [], (word, hits)
    assert "four operations and all of them read" in FRANCHISE_TEXT
    doc = client.get("/franchise/openapi.json").json()
    assert {method for item in doc["paths"].values() for method in item} == {"get"}


# ================================================================ arrivals

def test_shift_end_four_templates_in_turn(client, store):
    expected = [("R-022", 7, [], ""), ("S-106", 7, ["LE-S106-1124-02", "LE-S106-1124-04"], "LE-S106-1124-04"),
                ("R-047", 6, ["LE-R047-1124-03"], ""),
                ("S-102", 8, ["LE-S102-1124-03", "LE-S102-1124-04", "LE-S102-1124-05"], "LE-S102-1124-05")]
    for n in range(4):
        site, entries, still_open, first = expected[n]
        r = simulate(client, "shift-end")
        assert (r["item_id"], r["event_type"], r["system"]) == (f"{site}:{TODAY}", "shift-end", "stores")
        assert site in r["message"] and TODAY in r["message"] and "has arrived in the stores system" in r["message"]
        assert "get_shift_log" in r["message"] and f"{entries} entries" in r["message"]
        log = get(client, f"/stores/shift-logs/{site}")
        assert (log["date"], len(log["entries"]), log["handover_notes"]) == (TODAY, entries, [])
        answer = store.data["shift_log_answers"][f"{site}:{TODAY}"]
        assert (answer["open_entries"], answer["do_first"]) == (still_open, first)
        assert f"{n + 1}. `{site}`, {entries} entries." in ARRIVALS
        for entry in still_open:
            assert f"`{entry}`" in ARRIVALS
    assert "`LE-S106-1124-04` needs doing first" in ARRIVALS and "`LE-S102-1124-05` needs doing first" in ARRIVALS
    fifth = simulate(client, "shift-end")
    assert fifth["item_id"] == f"R-022:{YESTERDAY}"
    assert get(client, "/stores/shift-logs/R-022")["date"] == TODAY  # the latest log of the site
    assert get(client, "/stores/shift-logs/R-022", log_date=YESTERDAY)["entries"][0]["entry_id"] == "LE-R022-1123-01"
    assert get(client, "/admin/state")["counts"]["shift_logs"] == 11
    assert get(client, "/stores/shift-logs/R-014")["date"] == YESTERDAY  # the starting logs are not touched
    post(client, "/stores/shift-logs/S-106/handover-note", {"still_open": [{"entry_id": "LE-S106-1124-04", "text": "Engineer at 08:30."}],
                                                            "do_first": [{"entry_id": "LE-S106-1124-04", "text": "Engineer at 08:30."}]})


def test_incident_account_four_templates_in_turn(client, store):
    expected = [("R-022", "cut", "crew_member", "11:55", False, ["15.1", "15.2"]),
                ("S-107", "fall", "guest", "16:05", True, ["15.1", "15.2", "15.3"]),
                ("R-063", "near_miss", "nobody", "", False, ["15.2"]),
                ("R-071", "guest_illness", "guest", "10:25", True, ["15.1", "15.2", "15.3"])]
    for n in range(5):
        site, kind, who, time, phoned, clauses = expected[n % 4]
        r = simulate(client, "incident-account")
        aid = f"IA-2611-5{n + 1}"
        assert (r["item_id"], r["event_type"], r["system"]) == (aid, "incident-account", "stores")
        assert aid in r["message"] and site in r["message"] and "has arrived in the stores system" in r["message"]
        assert "get_incident_account" in r["message"]
        a = get(client, f"/stores/incident-accounts/{aid}")
        assert (a["site_id"], a["incident_date"], a["status"], a["reports"]) == (site, TODAY, "account_received", [])
        right = store.data["incident_answers"][aid]
        assert (right["incident_type"], right["who_was_affected"], right["incident_time"],
                right["area_manager_to_be_phoned_the_same_day"], right["clauses"]) == (kind, who, time, phoned, clauses)
        line = next(x for x in ARRIVALS.splitlines() if x.startswith(f"{n % 4 + 1}. `{site}`: "))
        assert f"Type `{kind}`, `{who}`" in line and (f"time {time}" in line if time else "no time given" in line)
        assert ("is phoned the same day" in line) == phoned and ("15.3" in line) == ("15.3" in clauses)
    listed = get(client, "/stores/incident-accounts")
    assert listed["count"] == 11 and listed["items"][0]["incident_date"] == TODAY
    assert get(client, "/admin/state")["counts"]["incident_accounts"] == 11
    assert "a blue plaster" in get(client, "/stores/incident-accounts/IA-2611-51")["account"]
    assert client.post("/admin/simulate/shift-start", headers=H).status_code == 404
    text = client.get("/").text
    assert "shift-end" in text and "incident-account" in text
    sub = post(client, "/admin/subscriptions", {"event_kind": "incident-account", "url": "http://127.0.0.1:9/hook"})
    assert sub["subscription"]["event_kind"] == "incident-account"
    assert client.post("/admin/subscriptions", json={"event_kind": "shift-start", "url": "http://127.0.0.1:9/hook"}, headers=H).status_code == 422
    client.delete("/admin/subscriptions", headers=H)


# ================================================================ reset

def change_everything(client):
    post(client, f"/people/rosters/{ROSTER}/check", ROSTER_CHECK)
    post(client, f"/people/rosters/{ROSTER}/publish", {"published_by": "N. Manager"})
    post(client, f"/stores/shift-logs/{LOG_SITE}/handover-note", HANDOVER)
    post(client, f"/stores/incident-accounts/{ACCOUNT}/report", INCIDENT)
    post(client, f"/stores/incident-accounts/{ACCOUNT}/submit", {"submitted_by": "M. Manager"})
    simulate(client, "shift-end")
    simulate(client, "incident-account")


CHANGED = {"people": ["draft_rosters"],
           "stores": ["incident_accounts", "incident_answers", "shift_log_answers", "shift_logs"]}


@pytest.mark.parametrize("system", ["people", "stores", "franchise"])
def test_each_system_of_version_1_4_is_put_back_alone(client, store, system):
    change_everything(client)
    assert get(client, "/admin/state")["changed_by"] == CHANGED
    fresh = build_all(TODAY_D)
    r = post(client, f"/admin/reset/{system}")
    assert r["applied"] is True and r["system"] == system and r["put_back"] == CHANGED.get(system, [])
    for name in CHANGED.get(system, []):
        assert store.data[name] == fresh[name], name
    for other, names in CHANGED.items():
        if other != system:
            assert store.data[names[0]] != fresh[names[0]], other
    assert get(client, "/admin/state")["changed_by"] == {k: v for k, v in CHANGED.items() if k != system}
    if system == "franchise":
        assert "nothing" in r["message"]
    if system == "stores":  # the arrivals of the system start again from the first one
        assert simulate(client, "shift-end")["item_id"] == f"R-022:{TODAY}"
        assert simulate(client, "incident-account")["item_id"] == "IA-2611-51"
        assert get(client, f"/people/rosters/{ROSTER}")["status"] == "published"
    if system == "people":
        assert get(client, f"/people/rosters/{ROSTER}")["status"] == "draft"
        assert get(client, f"/stores/incident-accounts/{ACCOUNT}")["status"] == "report_submitted"


def test_a_full_reset_puts_version_1_4_back(client, store):
    change_everything(client)
    post(client, "/stores/visits/SV-2610-01/report", {"findings": []})
    assert store.data != build_all(TODAY_D)
    counts = post(client, "/admin/reset")["counts"]
    assert store.data == build_all(TODAY_D) and store.changed == {} and store.simulated == {}
    assert (counts["draft_rosters"], counts["shift_logs"], counts["incident_accounts"], counts["franchisees"],
            counts["franchisee_questions"]) == (6, 6, 6, 3, 17)
    for name in ("roster_checks", "rosters_published", "handover_notes", "incident_reports_drafted", "incident_reports_submitted"):
        assert counts[name] == 0, name
    # the stores system put back alone takes its visit reports back with its logs and accounts
    change_everything(client)
    post(client, "/stores/visits/SV-2610-01/report", {"findings": []})
    assert post(client, "/admin/reset/stores")["put_back"] == CHANGED["stores"] + ["site_visits"]
    post(client, "/admin/reset/people")
    assert store.data == build_all(TODAY_D)


def test_the_older_record_sets_are_as_they_were(client, store):
    change_everything(client)
    fresh = build_all(TODAY_D)
    for name in ("sites", "site_visits", "visit_answers", "purchase_orders", "orders", "till_rows", "loyalty_members", "price_file"):
        assert store.data[name] == fresh[name], name
    assert len(store.data["sites"]) == 20 and len(store.data["site_visits"]) == 6
    assert get(client, "/stores/sites")["count"] == 20 and get(client, "/stores/visits")["count"] == 6
    assert set(get(client, "/stores/sites/R-090")) == {"demo_data", "site_id", "name", "kind", "format", "town", "street", "area",
                                                       "area_manager", "franchised", "franchisee"}


# ================================================================ data that holds on any date

@pytest.mark.parametrize("day", ["2026-11-22", "2026-11-23", "2026-12-03", "2027-01-05", "2027-03-01", "2028-02-29"])
def test_the_planted_cases_hold_on_any_retailer_date(day):
    today = date.fromisoformat(day)
    d = build_all(today)  # the seed works the breaches of each roster out and stops when they are not the planted ones
    starts = {r["week_start"] for r in d["draft_rosters"].values()}
    monday = date.fromisoformat(starts.pop())
    assert not starts and monday.weekday() == 0 and 1 <= (monday - today).days <= 7
    assert [len(a["breaches"]) for a in d["roster_answers"].values()] == [2, 0, 2, 0, 2, 0]
    assert [(b["rule"], b["day"]) for a in d["roster_answers"].values() for b in a["breaches"]] == [
        ("WT-2", "wednesday"), ("WT-4", "friday"), ("SR-1", "sunday"), ("WT-7", "saturday"), ("SR-2", "thursday"), ("WT-3", "")]
    yesterday = (today - timedelta(days=1)).isoformat()
    assert {x["date"] for x in d["shift_logs"].values()} == {yesterday} and len(d["shift_logs"]) == 6
    assert sorted(a["incident_date"] for a in d["incident_accounts"].values())[-1] == yesterday
    assert len(d["franchise_questions"]) == 17 and max(q["asked_on"] for q in d["franchise_questions"].values()) == yesterday


def test_what_a_careful_reader_should_find_is_never_served(client, store):
    kept = ["roster_answers", "shift_log_answers", "incident_answers", "franchise_answers"]
    assert all(name in store.data for name in kept)
    for system in ("people", "franchise", "stores"):
        doc = client.get(f"/{system}/openapi.json").json()
        for path, item in doc["paths"].items():
            if "get" in item and "{" not in path:
                text = client.get(f"/{system}{path}", headers=H).text
                for word in ("_answers", "on_a_limit", "open_entries", "answer_in_short"):
                    assert word not in text, (path, word)
    roster = client.get(f"/people/rosters/{ROSTER}", headers=H).text
    assert "breaches" not in roster and "on_a_limit" not in roster


# ================================================================ OpenAPI and the MCP door

def test_the_openapi_documents_of_version_1_4(client):
    seen = {}
    for system in ("people", "franchise", "stores"):
        doc = client.get(f"/{system}/openapi.json").json()
        assert doc["openapi"] == "3.0.3" and doc["info"]["version"] == "1.4.0" and "invented" in doc["info"]["description"].split(".")[0].lower()
        assert "anyOf" not in json.dumps(doc) and '"type": "null"' not in json.dumps(doc)
        for path, item in doc["paths"].items():
            for method, op in item.items():
                seen[op["operationId"]] = (system, method, op["summary"])
                assert len(op["description"]) > 80 and "422" not in op["responses"]
                for p in op.get("parameters", []):
                    assert p.get("description"), (op["operationId"], p["name"])
        assert client.get(f"/{system}/docs").status_code == 200 and client.get(f"/{system}/").status_code in (200, 307)
        assert client.get(f"/{system}/openapi.json").headers["x-demo-data"] == "invented"
    by_system = {s: sorted(op for op, (owner, _, _) in seen.items() if owner == s) for s in ("people", "franchise", "stores")}
    assert (len(by_system["people"]), len(by_system["franchise"]), len(by_system["stores"])) == (5, 4, 11)
    assert by_system["people"] == ["get_draft_roster", "get_working_time_rules", "list_draft_rosters", "publish_roster", "save_roster_check"]
    assert by_system["franchise"] == ["get_franchisee", "get_franchisee_question", "list_franchisee_questions", "list_franchisees"]
    new = sorted(set(by_system["stores"]) - {"list_sites", "get_site", "list_site_visits", "get_site_visit", "save_visit_report"})
    assert new == ["get_incident_account", "get_shift_log", "list_incident_accounts", "save_handover_note", "save_incident_report",
                   "submit_incident_report"]
    changes = sorted(op for op, (_, _, summary) in seen.items() if summary.endswith("(change)"))
    assert changes == ["publish_roster", "submit_incident_report"]
    drafts = sorted(op for op, (_, _, summary) in seen.items() if summary.endswith("(draft)"))
    assert drafts == ["save_handover_note", "save_incident_report", "save_roster_check", "save_visit_report"]
    assert all(method == "get" for op, (_, method, _) in seen.items() if op not in changes + drafts)
    # the paths of the older operations of the stores system are as they were
    paths = client.get("/stores/openapi.json").json()["paths"]
    assert {"/sites", "/sites/{site_id}", "/visits", "/visits/{visit_id}", "/visits/{visit_id}/report"} <= set(paths)


def test_the_new_systems_need_a_key(client):
    for path in ("/people/rosters", "/people/rules", "/franchise/franchisees", "/franchise/questions",
                 "/stores/shift-logs/R-014", "/stores/incident-accounts"):
        assert client.get(path).status_code == 401
        assert client.get(path, headers={"Authorization": f"Bearer {KEY}"}).status_code == 200
        assert client.get(path, headers=H).json()["demo_data"] is True
        assert client.get(path, headers=H).headers["x-demo-data"] == "invented"
    assert client.post(f"/people/rosters/{ROSTER}/check", json={}).status_code == 401
    assert client.post(f"/stores/incident-accounts/{ACCOUNT}/submit", json={}).status_code == 401
    assert client.post("/admin/reset/people").status_code == 401 and client.post("/admin/simulate/shift-end").status_code == 401


def test_the_drafts_of_version_1_4_are_described_for_a_tool_and_write_through(client, store):
    head = {"X-API-Key": KEY}
    listing = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}

    def tools(system):
        return client.post(f"/{system}/mcp", json=listing, headers=head).json()["result"]["tools"]

    def schema(system, name):
        found = next(t for t in tools(system) if t["name"] == name)["inputSchema"]
        assert "$ref" not in json.dumps(found), name
        return found

    def call(system, name, arguments):
        body = {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
        return client.post(f"/{system}/mcp", json=body, headers=head).json()["result"]

    assert [t["name"] for t in tools("people")] == ["list_draft_rosters", "get_draft_roster", "get_working_time_rules",
                                                    "save_roster_check", "publish_roster"]
    assert len(tools("franchise")) == 4 and len(tools("stores")) == 11
    s = schema("people", "save_roster_check")
    assert set(s["required"]) == {"roster_id"} and set(s["properties"]) == {"roster_id", "breaches", "summary", "drafted_by"}
    item = s["properties"]["breaches"]["items"]["properties"]
    assert item["rule"]["enum"] == RULE_IDS
    assert item["day"]["enum"] == ["", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    assert set(schema("people", "publish_roster")["required"]) == {"roster_id", "published_by"}
    s = schema("stores", "save_handover_note")
    assert set(s["properties"]) == {"site_id", "log_date", "what_happened", "still_open", "do_first", "summary", "drafted_by"}
    assert set(s["properties"]["still_open"]["items"]["required"]) == {"entry_id", "text"} and s["required"] == ["site_id"]
    s = schema("stores", "save_incident_report")
    assert s["properties"]["incident_type"]["enum"] == ["fall", "burn", "cut", "guest_illness", "near_miss", "property_damage", "other"]
    assert s["properties"]["who_was_affected"]["enum"] == ["crew_member", "guest", "nobody", "other"]
    assert s["properties"]["first_aid_given"]["enum"] == ["yes", "no", "not_said"] == s["properties"]["reported_to_shift_manager"]["enum"]
    assert s["properties"]["next_steps"]["items"]["properties"]["clause"]["enum"] == ["15.1", "15.2", "15.3"]
    assert s["properties"]["area_manager_to_be_phoned_the_same_day"]["type"] == "boolean"
    assert {"account_id", "incident_type", "who_was_affected", "incident_date", "location", "what_happened", "first_aid_given",
            "reported_to_shift_manager", "area_manager_to_be_phoned_the_same_day", "next_steps"} == set(s["required"])
    assert set(schema("stores", "get_shift_log")["properties"]) == {"site_id", "log_date"}

    r = call("people", "publish_roster", {"roster_id": ROSTER, "published_by": "N. Manager"})
    assert r["isError"] is True and "409" in r["content"][0]["text"] and "Use save_roster_check first" in r["content"][0]["text"]
    r = call("people", "save_roster_check", {"roster_id": ROSTER, **ROSTER_CHECK})
    assert not r.get("isError") and store.data["draft_rosters"][ROSTER]["checks"][0]["drafted_by"] == "a test"
    r = call("people", "save_roster_check", {"roster_id": ROSTER, "breaches": [{"rule": "WT-2", "colleague_id": "C-10306",
                                                                               "what_the_roster_shows": "x"}]})
    assert r["isError"] is True and "422" in r["content"][0]["text"] and "it needs the shift_id" in r["content"][0]["text"]
    r = call("people", "publish_roster", {"roster_id": ROSTER, "published_by": "N. Manager"})
    assert not r.get("isError") and store.data["draft_rosters"][ROSTER]["status"] == "published"
    r = call("stores", "get_shift_log", {"site_id": "S-104"})
    assert not r.get("isError") and len(json.loads(r["content"][0]["text"])["entries"]) == 13
    r = call("stores", "save_handover_note", {"site_id": LOG_SITE, "log_date": YESTERDAY, **HANDOVER})
    assert not r.get("isError") and len(store.data["shift_logs"][f"R-014:{YESTERDAY}"]["handover_notes"]) == 1
    r = call("stores", "save_handover_note", {"site_id": LOG_SITE, "do_first": [{"entry_id": "LE-R014-1123-09", "text": "x"}]})
    assert r["isError"] is True and "is not under still_open" in r["content"][0]["text"]
    r = call("stores", "save_incident_report", {"account_id": ACCOUNT, **INCIDENT, "next_steps": INCIDENT["next_steps"][:2]})
    assert r["isError"] is True and "422" in r["content"][0]["text"] and "clause 15.3" in r["content"][0]["text"]
    r = call("stores", "save_incident_report", {"account_id": ACCOUNT, **INCIDENT})
    assert not r.get("isError") and json.loads(r["content"][0]["text"])["draft"]["version"] == 1
    r = call("stores", "submit_incident_report", {"account_id": ACCOUNT, "submitted_by": "M. Manager"})
    assert not r.get("isError") and store.data["incident_accounts"][ACCOUNT]["status"] == "report_submitted"
    r = call("franchise", "get_franchisee_question", {"question_id": "FQ-2611-16"})
    assert not r.get("isError") and "renew" in json.loads(r["content"][0]["text"])["question"]
    r = call("franchise", "list_franchisee_questions", {"franchisee_id": "FR-09"})
    assert r["isError"] is True and "404" in r["content"][0]["text"]
    for system in ("people", "franchise"):
        assert client.post(f"/{system}/mcp", json=listing).status_code == 401 and client.get(f"/{system}/sse").status_code == 401
    init = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}}
    for system in ("people", "franchise"):
        r = client.post(f"/{system}/mcp", json=init, headers=head).json()["result"]
        assert r["serverInfo"]["name"] == f"rowanmere-group-{system}" and "invented" in r["instructions"]


def test_the_landing_page_and_the_readme_show_version_1_4(client):
    text = client.get("/").text
    assert "The fourteen systems" in text
    for system in ("people", "franchise"):
        assert f"/{system}/openapi.json" in text and f"/{system}/mcp" in text and f"/{system}/sse" in text
    for label in ("draft rosters", "roster checks", "shift logs", "handover notes", "incident accounts", "franchisees",
                  "franchisee questions"):
        assert label in text, label
    assert "## The fourteen systems" in README and "In all, 146 operations" in README and "holds fourteen systems" in README
    total = 0
    for system in ("stores", "people", "franchise"):
        doc = client.get(f"/{system}/openapi.json").json()
        ops = [op["operationId"] for item in doc["paths"].values() for op in item.values()]
        line = next(x for x in README.splitlines() if x.startswith(f"- {system}: "))
        assert line == f"- {system}: " + ", ".join(f"`{o}`" for o in ops), system
        assert next(x for x in README.splitlines() if x.startswith(f"| {system} | `/{system}` |")).endswith(f"| {len(ops)} |")
        total += len(ops)
    assert total == 20
    listed = [x for x in README.splitlines() if x.startswith("- ") and ": `" in x[:20]]
    assert len(listed) == 14 and sum(x.count("`") // 2 for x in listed) == 146
    for kind in ("shift-end", "incident-account"):
        assert f"`{kind}`" in README
    assert "tests/test_version_1_4.py" in README and "tests/test_version_1_4.py" in TEXT
