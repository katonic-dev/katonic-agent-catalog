"""The conduct system: the right answers of the Conduct section of SCENARIOS.md, every refusal, and the rules drafts keep.

Checked against the data the service gives at the insurer date 2026-11-26."""
import copy
import json
import re
from datetime import date

from insurer.seed import build_all
from insurer.seed_conduct import (add_working_days, build_conduct, is_working_day, last_working_day_on_or_before,
                                  working_days_between)
from conftest import H, TODAY

TODAY_D = date.fromisoformat(TODAY)
CD_SETS = sorted(build_conduct(TODAY_D))


def get(client, path):
    r = client.get(f"/conduct{path}", headers=H)
    assert r.status_code == 200, (path, r.status_code, r.text[:300])
    return r.json()


def post(client, path, body=None, status=200):
    r = client.post(f"/conduct{path}", json=body or {}, headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:400])
    return r.json()


def cmp(client, n):
    return get(client, f"/complaints/CMP-{n}")


def dates(client, n):
    x = cmp(client, n)["deadlines"]
    return x["acknowledgement"], x["final_response"], x


RESPONSE = {"is_a_complaint": "yes", "category_id": "CC-1", "route_to": "complaints_officer",
            "draft_response": "Thank you for telling us. We will look into the calls and write to you by 24 Dec 2026.",
            "log_entry": "Service complaint, CC-1, acknowledgement due 27 Nov 2026."}

# The right answer of the audit sample: every rule of every file.
AUDIT = {"AF-7201": {"CND-1": "met", "CND-2": "met", "CND-3": "not_applicable"},
         "AF-7202": {"CND-4": "met", "CND-5": "met"},
         "AF-7203": {"CND-1": "not_met", "CND-2": "met", "CND-3": "not_applicable"},
         "AF-7204": {"CND-4": "not_met", "CND-5": "met"},
         "AF-7205": {"CND-1": "met", "CND-2": "met", "CND-3": "not_met"},
         "AF-7206": {"CND-6": "met", "CND-7": "cannot_tell"},
         "AF-7207": {"CND-1": "met", "CND-2": "met", "CND-3": "met"},
         "AF-7208": {"CND-6": "not_met", "CND-7": "met"}}
AUDIT_ROWS = [{"file_id": f, "rule_id": r, "result": v, "evidence": "As the system measures it."}
              for f, rules in AUDIT.items() for r, v in rules.items()]
RECORD = {"rows": AUDIT_ROWS, "files_that_need_a_person": ["AF-7206"], "summary": "Eight files, twenty rules checked."}
NOTE = {"finding": "bears_on_an_obligation", "obligation_ids": ["OBL-05"], "note": "The final response limit falls to 20 days."}

# The right answer of each document schedule: category, may be privileged, rule, the original of a copy.
SCHEDULES = {
    "DSP-7401": [("DC-2", "no", "PG-5", ""), ("DC-3", "no", "PG-5", ""), ("DC-4", "no", "PG-5", ""), ("DC-2", "no", "PG-5", ""),
                 ("DC-1", "no", "PG-5", ""), ("DC-5", "yes", "PG-1", ""), ("DC-5", "yes", "PG-1", ""), ("DC-6", "unclear", "PG-4", ""),
                 ("DC-1", "yes", "PG-2", ""), ("DC-4", "no", "PG-5", "DSP-7401-D03"), ("DC-3", "no", "PG-3", "")],
    "DSP-7402": [("DC-2", "no", "PG-5", ""), ("DC-2", "no", "PG-5", ""), ("DC-3", "no", "PG-5", ""), ("DC-1", "no", "PG-5", ""),
                 ("DC-5", "yes", "PG-1", ""), ("DC-5", "yes", "PG-1", ""), ("DC-4", "yes", "PG-2", ""), ("DC-6", "no", "PG-3", ""),
                 ("DC-2", "no", "PG-5", "DSP-7402-D01")],
    "DSP-7403": [("DC-7", "no", "PG-5", ""), ("DC-2", "no", "PG-5", ""), ("DC-4", "no", "PG-5", ""), ("DC-2", "no", "PG-5", ""),
                 ("DC-2", "no", "PG-5", ""), ("DC-5", "yes", "PG-1", ""), ("DC-3", "unclear", "PG-6", ""), ("DC-1", "yes", "PG-2", "")],
}


def schedule(client, dispute_id):
    docs = get(client, f"/disputed-claims/{dispute_id}")["documents"]
    rows = [{"document_id": doc["document_id"], "category_id": cat, "date": doc["dated"] or "", "author": doc["author"] or "",
             "may_be_privileged": flag, "rule_id": rule, "duplicate_of": original}
            for doc, (cat, flag, rule, original) in zip(docs, SCHEDULES[dispute_id])]
    assert len(rows) == len(docs) == len(SCHEDULES[dispute_id])
    return {"rows": rows, "summary": "Every document of the set, one row each."}


# ---------------------------------------------------------------- the system as a whole
def test_the_conduct_system_has_23_operations_and_every_save_is_a_draft(client):
    doc = client.get("/conduct/openapi.json").json()
    ops = [(method, op) for item in doc["paths"].values() for method, op in item.items()]
    assert len(ops) == 23
    saves = sorted(op["operationId"] for method, op in ops if method != "get")
    assert saves == ["save_audit_record", "save_complaint_response", "save_document_schedule", "save_regulatory_impact_note"]
    for method, op in ops:
        assert not op["summary"].endswith("(change)"), op["operationId"]
        if method != "get":
            assert op["summary"].endswith("(draft)"), op["operationId"]
    assert client.get("/conduct/complaints").status_code == 401
    assert "conduct/openapi.json" in client.get("/").text


def test_conduct_ids_have_their_own_ranges_and_collide_with_nothing():
    data = build_all(TODAY_D)
    prefixes = {"cd_complaint_categories": "CC-", "cd_complaint_rules": "CH-", "cd_complaints": "CMP-7", "cd_conduct_rules": "CND-",
                "cd_audit_samples": "AUD-72", "cd_audit_files": "AF-72", "cd_obligations": "OBL-", "cd_publications": "PUB-7",
                "cd_document_categories": "DC-", "cd_privilege_guide": "PG-", "cd_disputes": "DSP-74"}
    for name, prefix in prefixes.items():
        assert all(key.startswith(prefix) for key in data[name]), name
    mine = {key for name in CD_SETS for key in data[name]}
    others = {key for name, records in data.items() if name not in CD_SETS and isinstance(records, dict) for key in records}
    assert not mine & others
    assert all(doc["document_id"].startswith(x["dispute_id"] + "-D") for x in data["cd_disputes"].values() for doc in x["documents"])


def test_no_text_of_the_conduct_data_holds_a_bare_date_counts_days_or_names_a_real_regulator():
    data = build_conduct(TODAY_D)
    texts = [c["text"] for c in data["cd_complaints"].values()] + [p["text"] for p in data["cd_publications"].values()]
    texts += [doc["text"] for x in data["cd_disputes"].values() for doc in x["documents"]]
    texts += [f["facts"]["decline_letter"]["text"] for f in data["cd_audit_files"].values() if f["facts"].get("decline_letter")]
    texts += [f["note"] for f in data["cd_audit_files"].values()]
    assert len(texts) == 10 + 10 + 28 + 2 + 8
    for text in texts:
        assert not re.search(r"\b20\d\d-\d\d-\d\d\b", text), text
    blob = json.dumps(data).lower()
    for word in ("yesterday", "last week", "days ago", "weeks ago", "last month", "this morning", "tomorrow", "monday", "tuesday",
                 "wednesday", "thursday", "friday", "saturday", "sunday", chr(8212), "ombudsman", "gdpr", "solvency", "financial "
                 "conduct authority"):
        assert word not in blob, word
    assert {p["regulator"] for p in data["cd_publications"].values()} == {"Meridia Insurance Authority", "Meridia Data Protection Office"}


def test_working_days_leave_out_the_weekend_and_the_invented_public_holidays():
    charter_day, lantern_day = date(2026, 11, 16), date(2026, 10, 12)
    assert not is_working_day(charter_day) and not is_working_day(lantern_day) and not is_working_day(date(2026, 11, 21))
    assert is_working_day(date(2026, 11, 17))
    assert add_working_days(date(2026, 11, 13), 3) == date(2026, 11, 19)
    assert working_days_between(date(2026, 11, 13), TODAY_D) == 8 and working_days_between(TODAY_D, TODAY_D) == 0
    assert last_working_day_on_or_before(date(2026, 12, 13)) == date(2026, 12, 11)


# ---------------------------------------------------------------- complaints
def test_the_complaints_procedure_has_six_categories_seven_rules_and_the_holidays(client):
    doc = get(client, "/complaints-procedure")
    assert [c["category_id"] for c in doc["categories"]] == [f"CC-{n}" for n in range(1, 7)]
    assert [r["rule_id"] for r in doc["handling_rules"]] == [f"CH-{n}" for n in range(1, 8)]
    assert [r["rule_id"] for r in doc["handling_rules"] if r["kind"] == "measured"] == ["CH-1", "CH-2", "CH-3"]
    rules = {r["rule_id"]: r["text"] for r in doc["handling_rules"]}
    assert "within 3 working days" in rules["CH-1"] and "within 30 days" in rules["CH-2"] and "within 15 days in place of 30" in rules["CH-3"]
    assert "Meridia Insurance Authority" in rules["CH-4"] and "policy servicing team" in rules["CH-6"]
    days = [(h["date"], h["name"]) for h in doc["public_holidays"] if h["date"].startswith("2026")]
    assert days == [("2026-03-09", "Founding Day"), ("2026-06-22", "Harbour Day"), ("2026-10-12", "Lantern Day"), ("2026-11-16", "Charter Day")]
    assert doc["who_handles"]["senior_complaints_officer"] == "Leopold Vanterpool, senior complaints officer"


def test_the_list_of_complaints_is_whole_and_holds_no_drafts(client):
    post(client, "/complaints/CMP-7101/response", RESPONSE)
    rows = get(client, "/complaints")["items"]
    assert [r["complaint_id"] for r in rows] == ["CMP-7051", "CMP-7052"] + [f"CMP-71{n:02d}" for n in range(1, 9)]
    assert all("response_drafts" not in r and r["text"] and r["channel"] for r in rows)
    assert [r["complaint_id"] for r in get(client, "/complaints?status=new")["items"]] == [f"CMP-71{n:02d}" for n in range(1, 9)]
    assert get(client, "/complaints?status=closed")["count"] == 2
    assert client.get("/conduct/complaints?status=open", headers=H).status_code == 409


def test_cmp_7101_is_a_plain_service_complaint_with_a_day_left(client):
    c = cmp(client, 7101)
    ack, final, _ = dates(client, 7101)
    assert (c["customer"], c["channel"], c["received"], c["policy_id"], c["claim_id"], c["acknowledged_on"]) == (
        "Corwin Ashgrove", "email", "2026-11-24", "POL-2001", None, None)
    assert "17 Nov 2026 and again on 19 Nov 2026" in c["text"] and "call back that never came" in c["text"]
    assert (ack["due_on"], ack["status"], ack["working_days_elapsed"], ack["working_days_left"], ack["late"]) == ("2026-11-27", "not_yet_due", 2, 1, False)
    assert (final["rule_id"], final["limit_days"], final["due_on"], final["days_elapsed"], final["days_left"]) == ("CH-2", 30, "2026-12-24", 2, 28)
    assert c["customer_care_record"]["vulnerable"] is False and c["earlier_complaints_by_this_customer"] == []
    assert c["policy"]["holder"] == "Corwin Ashgrove" and c["policy"]["cover_on_the_day_received"]["in_force"] is True
    assert get(client, "/complaints/CMP-7101/deadlines")["acknowledgement"] == ack


def test_cmp_7102_is_about_a_declined_claim_read_from_the_claims_system(client):
    c = cmp(client, 7102)
    ack, final, _ = dates(client, 7102)
    assert (c["customer"], c["channel"], c["received"], c["policy_id"], c["claim_id"]) == ("Yvaine Corrimond", "letter", "2026-11-25", "POL-2010", "CLM-4010")
    claim = c["claims_on_the_policy"][0]
    assert (claim["claim_id"], claim["status"], claim["this_complaint_names_it"], claim["date_of_loss"]) == ("CLM-4010", "decided", True, "2026-11-10")
    assert (claim["decision"]["decision"], claim["decision"]["clause"], claim["decision"]["decided_on"]) == ("declined", "2.2", "2026-11-20")
    assert (ack["due_on"], ack["status"], final["due_on"]) == ("2026-11-30", "not_yet_due", "2026-12-25")
    assert not re.search(r"authority|lawyer|solicitor|court|legal", c["text"].lower())


def test_cmp_7103_mentions_the_regulator_and_was_acknowledged_in_time(client):
    c = cmp(client, 7103)
    ack, final, _ = dates(client, 7103)
    assert (c["customer"], c["channel"], c["received"], c["acknowledged_on"], c["claim_id"]) == ("Odalys Fenwright", "web form", "2026-11-24", "2026-11-25", "CLM-4004")
    assert "I will take this to the Meridia Insurance Authority" in c["text"] and "19 Nov 2026" in c["text"]
    assert (ack["status"], ack["working_days_elapsed"], ack["late"], final["due_on"]) == ("met", 1, False, "2026-12-24")
    assert c["claims_on_the_policy"][0]["date_reported"] == "2026-11-19" and c["claims_on_the_policy"][0]["decision"] is None
    saved = post(client, "/complaints/CMP-7103/response", {**RESPONSE, "category_id": "cc-3", "rules_that_apply": ["ch-4"],
                                                          "route_to": "Senior complaints officer"})["draft"]
    assert (saved["category_id"], saved["rules_that_apply"], saved["route_to"], saved["goes_to"]) == (
        "CC-3", ["CH-4"], "senior_complaints_officer", "Leopold Vanterpool, senior complaints officer")


def test_cmp_7104_is_from_a_customer_marked_vulnerable_and_has_the_shorter_limit(client):
    c = cmp(client, 7104)
    ack, final, whole = dates(client, 7104)
    care = c["customer_care_record"]
    assert (c["customer"], c["channel"], c["received"], c["claim_id"]) == ("Aldous Pennicott", "telephone", "2026-11-25", "CLM-4007")
    assert (care["vulnerable"], care["preferred_contact"], care["recorded_on"]) == (True, "telephone", "2026-11-23")
    assert "Aged 81, lives alone" in care["reason"] and "fire of 23 Nov 2026" in care["reason"]
    assert whole["customer_marked_vulnerable"] is True
    assert (final["rule_id"], final["limit_days"], final["due_on"], final["days_left"]) == ("CH-3", 15, "2026-12-10", 14)
    assert "15 days in place of 30 (CH-3)" in final["sentence"] and (ack["due_on"], ack["status"]) == ("2026-11-30", "not_yet_due")


def test_cmp_7105_repeats_an_earlier_complaint_on_the_same_matter(client):
    c = cmp(client, 7105)
    earlier = c["earlier_complaints_by_this_customer"]
    assert (c["customer"], c["received"], c["acknowledged_on"], c["policy_id"]) == ("Henrietta Quillby", "2026-11-23", "2026-11-24", "POL-2006")
    assert [e["complaint_id"] for e in earlier] == ["CMP-7051"]
    assert (earlier[0]["received"], earlier[0]["closed"]["closed_on"], earlier[0]["closed"]["category_id"]) == ("2026-10-13", "2026-10-27", "CC-4")
    assert "USD 31.50 collected twice" in earlier[0]["closed"]["matter"] and "USD 31.50 twice" in c["text"]
    assert "On 13 Oct 2026 I complained" in c["text"] and "letter of 27 Oct 2026" in c["text"]
    ack, final, _ = dates(client, 7105)
    assert (ack["status"], final["due_on"]) == ("met", "2026-12-23")
    saved = post(client, "/complaints/CMP-7105/response", {**RESPONSE, "category_id": "CC-4", "rules_that_apply": ["CH-5"],
                                                          "linked_complaint_id": "cmp-7051"})["draft"]
    assert saved["linked_complaint_id"] == "CMP-7051"
    refused = post(client, "/complaints/CMP-7105/response", {**RESPONSE, "category_id": "CC-4", "linked_complaint_id": "CMP-7052"}, 409)
    assert "not an earlier complaint by Henrietta Quillby" in refused["detail"] and "CMP-7051" in refused["detail"]


def test_cmp_7106_is_a_question_and_not_a_complaint(client):
    c = cmp(client, 7106)
    assert (c["customer"], c["policy_id"], c["received"]) == ("Isaura Venn", "POL-2011", "2026-11-25")
    assert "courtesy car" in c["text"] and "named driver from 1 Dec 2026" in c["text"]
    assert not re.search(r"complain|unhappy|poor|wrong|refund", c["text"].lower())
    assert "not a complaint (CH-6)" in c["deadlines"]["note"]
    saved = post(client, "/complaints/CMP-7106/response", {"is_a_complaint": "No", "rules_that_apply": ["CH-6"], "route_to": "Policy servicing",
                                                          "draft_response": "Your question has gone to our policy servicing team.",
                                                          "log_entry": "An enquiry, not a complaint."})["draft"]
    assert (saved["is_a_complaint"], saved["category_id"], saved["route_to"], saved["dates_worked_out_by_the_system"]) == (
        "no", None, "policy_servicing", None)
    with_category = post(client, "/complaints/CMP-7106/response", {**RESPONSE, "is_a_complaint": "no", "route_to": "policy_servicing"}, 409)
    assert "has no category" in with_category["detail"]
    wrong_route = post(client, "/complaints/CMP-7106/response", {**RESPONSE, "is_a_complaint": "no", "category_id": ""}, 409)
    assert "goes to policy_servicing" in wrong_route["detail"]


def test_cmp_7107_is_past_its_acknowledgement_date_and_the_count_passes_a_public_holiday(client):
    c = cmp(client, 7107)
    ack, final, whole = dates(client, 7107)
    assert (c["customer"], c["channel"], c["received"], c["acknowledged_on"], c["policy_id"]) == ("Bram Tollermoor", "web form", "2026-11-13", None, "POL-2005")
    assert (ack["due_on"], ack["status"], ack["working_days_elapsed"], ack["working_days_late"], ack["late"]) == ("2026-11-19", "late", 8, 5, True)
    assert "late by 5 working days" in ack["sentence"]
    assert whole["public_holidays_in_the_count"] == [{"date": "2026-11-16", "name": "Charter Day"}]
    assert (final["due_on"], final["days_elapsed"], final["days_left"], final["late"]) == ("2026-12-11", 13, 15, False)
    assert "Day 30 is 13 Dec 2026, which is not a working day" in final["sentence"]
    earlier = c["earlier_complaints_by_this_customer"]
    assert [(e["complaint_id"], e["closed"]["category_id"], e["received"]) for e in earlier] == [("CMP-7052", "CC-1", "2026-04-10")]
    assert "certificate of motor insurance on 2 Nov 2026 and again on 9 Nov 2026" in c["text"] and "50 minutes" in earlier[0]["closed"]["matter"]


def test_cmp_7108_is_exactly_on_its_acknowledgement_day_and_is_not_late(client):
    c = cmp(client, 7108)
    ack, final, _ = dates(client, 7108)
    assert (c["customer"], c["received"], c["acknowledged_on"], c["policy_id"]) == ("Teodor Brackwell", "2026-11-23", None, "POL-2009")
    assert (ack["due_on"], ack["status"], ack["working_days_elapsed"], ack["working_days_left"], ack["working_days_late"], ack["late"]) == (
        TODAY, "due_today", 3, 0, 0, False)
    assert "is not late" in ack["sentence"] and final["due_on"] == "2026-12-23"
    assert "USD 25.00" in c["text"] and "20 Nov 2026" in c["text"]


def test_a_complaint_response_is_a_versioned_draft_and_not_part_of_the_complaint(client, store):
    before = copy.deepcopy({k: v for k, v in store.data.items() if k != "cd_complaints"})
    one = post(client, "/complaints/CMP-7101/response", {**RESPONSE, "is_a_complaint": "Yes", "route_to": "Complaints officer"})
    two = post(client, "/complaints/CMP-7101/response", {**RESPONSE, "drafted_by": "Complaint Handling"})
    assert (one["kind"], one["draft"]["version"], two["draft"]["version"], two["draft"]["drafted_by"]) == ("draft", 1, 2, "Complaint Handling")
    assert (one["draft"]["is_a_complaint"], one["draft"]["route_to"]) == ("yes", "complaints_officer")
    assert one["draft"]["dates_worked_out_by_the_system"] == {
        "received": "2026-11-24", "acknowledgement_due_on": "2026-11-27", "acknowledgement_status": "not_yet_due",
        "acknowledgement_working_days_late": 0, "final_response_rule": "CH-2", "final_response_due_on": "2026-12-24",
        "customer_marked_vulnerable": False}
    c = cmp(client, 7101)
    assert "response_drafts" not in c and c["drafts_on_file"] == 2 and c["status"] == "new" and c["acknowledged_on"] is None
    assert "look into the calls" not in json.dumps(c)
    assert [x["version"] for x in get(client, "/complaints/CMP-7101/drafts")["items"]] == [1, 2]
    assert {k: v for k, v in store.data.items() if k != "cd_complaints"} == before


def test_a_complaint_response_is_refused_with_a_reason_and_nothing_is_saved(client):
    category = post(client, "/complaints/CMP-7101/response", {**RESPONSE, "category_id": "CC-9"}, 409)
    assert "CC-9 is not a complaint category" in category["detail"] and "Nothing was saved" in category["detail"] and category["applied"] is False
    assert "needs one category" in post(client, "/complaints/CMP-7101/response", {**RESPONSE, "category_id": ""}, 409)["detail"]
    assert "Only an item that is not a complaint" in post(client, "/complaints/CMP-7101/response", {**RESPONSE, "route_to": "policy_servicing"}, 409)["detail"]
    assert "CH-9" in post(client, "/complaints/CMP-7101/response", {**RESPONSE, "rules_that_apply": ["CH-9"]}, 409)["detail"]
    assert "earlier complaints by this customer: none" in post(client, "/complaints/CMP-7101/response", {**RESPONSE, "linked_complaint_id": "CMP-7051"}, 409)["detail"].lower()
    assert post(client, "/complaints/CMP-7101/response", {**RESPONSE, "route_to": "uphold"}, 422)["applied"] is False
    assert post(client, "/complaints/CMP-7101/response", {k: v for k, v in RESPONSE.items() if k != "log_entry"}, 422)["applied"] is False
    assert "is closed" in post(client, "/complaints/CMP-7051/response", RESPONSE, 409)["detail"]
    assert client.get("/conduct/complaints/CMP-7051/deadlines", headers=H).status_code == 409
    assert cmp(client, 7101)["drafts_on_file"] == 0 and cmp(client, 7051)["deadlines"] is None


def test_a_complaint_follows_the_claims_system_and_writes_nothing_to_it(client, store):
    client.post("/claims/claims/CLM-4004/decision", headers=H, json={"decision": "declined", "decided_by": "Fenella Arkwright",
                                                                    "reason": "Test.", "clause": "2.2"})
    assert cmp(client, 7103)["claims_on_the_policy"][0]["decision"]["decision"] == "declined"
    client.post("/admin/reset/claims", headers=H)
    before = copy.deepcopy((store.data["policies"], store.data["claims"]))
    post(client, "/complaints/CMP-7103/response", {**RESPONSE, "category_id": "CC-3", "route_to": "senior_complaints_officer"})
    assert (store.data["policies"], store.data["claims"]) == before


# ---------------------------------------------------------------- conduct rules and the audit sample
def test_the_conduct_rules_are_seven_numbered_rules_by_kind_of_file(client):
    doc = get(client, "/conduct-rules")
    assert [(r["rule_id"], r["kind_of_file"], r["kind"]) for r in doc["items"]] == [
        ("CND-1", "claims", "measured"), ("CND-2", "claims", "measured"), ("CND-3", "claims", "for_reading"),
        ("CND-4", "sales", "for_reading"), ("CND-5", "sales", "measured"), ("CND-6", "policy", "measured"), ("CND-7", "policy", "measured")]
    text = {r["rule_id"]: r["text"] for r in doc["items"]}
    assert "within 5 working days" in text["CND-1"] and "within 20 working days" in text["CND-2"] and "within 7 days" in text["CND-5"]
    assert "at least 21 days before" in text["CND-6"] and "within 10 working days" in text["CND-7"]
    assert [r["rule_id"] for r in get(client, "/conduct-rules?kind_of_file=sales")["items"]] == ["CND-4", "CND-5"]
    assert client.get("/conduct/conduct-rules?kind_of_file=marine", headers=H).status_code == 409


def test_the_audit_sample_holds_eight_files_of_three_kinds(client):
    s = get(client, "/audit-samples/AUD-7200")
    assert (s["period_start"], s["period_end"], s["drawn_on"], s["rows_an_audit_record_needs"]) == ("2026-10-01", "2026-10-31", "2026-11-24", 20)
    assert [(f["file_id"], f["kind_of_file"], f["customer"]) for f in s["files"]] == [
        ("AF-7201", "claims", "Ottoline Brackenridge"), ("AF-7202", "sales", "Jasper Windlesham"), ("AF-7203", "claims", "Corisande Yarrow"),
        ("AF-7204", "sales", "Barnaby Thistlewood"), ("AF-7205", "claims", "Evadne Larkhill"), ("AF-7206", "policy", "Mungo Pettifer"),
        ("AF-7207", "claims", "Sidonie Marchmont"), ("AF-7208", "policy", "Lysander Crowhurst")]
    brief = get(client, "/audit-samples")["items"][0]
    assert brief["files_by_kind"] == {"claims": 4, "sales": 2, "policy": 2} and "record_drafts" not in brief and "files" in brief


def measured(client, n):
    f = next(f for f in get(client, "/audit-samples/AUD-7200")["files"] if f["file_id"] == f"AF-{n}")
    return f, {r["rule_id"]: r for r in f["measured"]["rules"]}


def test_the_measure_of_every_audit_file_agrees_with_the_right_answer_on_the_dated_rules(client):
    for file_id, rules in AUDIT.items():
        _, rows = measured(client, file_id[3:])
        assert list(rows) == list(rules)
        for rule_id, right in rules.items():
            got = rows[rule_id]["result"]
            assert got == right or got == "for_reading", (file_id, rule_id, got)
        assert get(client, f"/audit-files/{file_id}/measure")["rules"] == list(rows.values())


def test_af_7201_and_af_7202_are_fully_compliant(client):
    f, rows = measured(client, 7201)
    assert (f["facts"]["reported_on"], f["facts"]["acknowledged_on"], f["facts"]["pack_complete_on"], f["facts"]["decision_on"], f["facts"]["decision"]) == (
        "2026-10-05", "2026-10-07", "2026-10-09", "2026-10-28", "accepted")
    assert (rows["CND-1"]["measured"], rows["CND-1"]["limit"], rows["CND-2"]["measured"], rows["CND-2"]["limit"]) == (2, 5, 12, 20)
    assert rows["CND-3"]["result"] == "not_applicable" and f["facts"]["decline_letter"] is None
    assert f["measured"]["public_holidays_in_the_period_of_the_file"] == [{"date": "2026-10-12", "name": "Lantern Day"}]
    f, rows = measured(client, 7202)
    assert (f["facts"]["needs_statement_on_file"], f["facts"]["needs_statement_dated"], f["facts"]["policy_issued_on"],
            f["facts"]["cooling_off_notice_sent_on"]) == ("yes", "2026-10-13", "2026-10-14", "2026-10-16")
    assert (rows["CND-5"]["measured"], rows["CND-5"]["limit"], rows["CND-5"]["result"], rows["CND-4"]["result"]) == (2, 7, "met", "for_reading")


def test_af_7203_was_acknowledged_late(client):
    f, rows = measured(client, 7203)
    assert (f["facts"]["reported_on"], f["facts"]["acknowledged_on"]) == ("2026-10-08", "2026-10-21")
    assert (rows["CND-1"]["result"], rows["CND-1"]["measured"], rows["CND-1"]["limit"], rows["CND-1"]["over_or_short_by"]) == ("not_met", 8, 5, 3)
    assert "Over the limit by 3 working days" in rows["CND-1"]["sentence"] and (rows["CND-2"]["result"], rows["CND-2"]["measured"]) == ("met", 10)


def test_af_7204_has_no_needs_statement(client):
    f, rows = measured(client, 7204)
    assert (f["facts"]["needs_statement_on_file"], f["facts"]["needs_statement_dated"]) == ("no", None) and "No needs statement is on it" in f["note"]
    assert (f["facts"]["policy_issued_on"], f["facts"]["cooling_off_notice_sent_on"], rows["CND-5"]["measured"], rows["CND-5"]["result"]) == (
        "2026-10-21", "2026-10-26", 5, "met")


def test_af_7205_declines_without_the_clause_and_af_7207_cites_it(client):
    f, rows = measured(client, 7205)
    letter = f["facts"]["decline_letter"]
    assert f["facts"]["decision"] == "declined" and letter["sent_on"] == "2026-10-28" and "28 Oct 2026" in letter["text"]
    assert "no sign that anyone forced their way" in letter["text"] and not re.search(r"clause|\b\d\.\d\b", letter["text"].lower())
    assert (rows["CND-1"]["measured"], rows["CND-2"]["measured"], rows["CND-3"]["result"]) == (1, 15, "for_reading")
    f, _ = measured(client, 7207)
    assert "Clause 2.2 of your policy wording (TMI-HOM-02)" in f["facts"]["decline_letter"]["text"] and "68 days" in f["facts"]["decline_letter"]["text"]


def test_af_7206_lacks_a_date_and_the_system_does_not_guess(client):
    f, rows = measured(client, 7206)
    assert (f["facts"]["change_asked_for_on"], f["facts"]["change_confirmed_on"]) == ("2026-10-10", None)
    assert (rows["CND-7"]["result"], rows["CND-7"]["measured"]) == ("cannot_tell", None) and "Nothing is assumed" in rows["CND-7"]["sentence"]
    assert "carries no date" in f["note"] and "10 Oct 2026" in f["note"] and f["measured"]["cannot_tell"] == ["CND-7"]
    assert (f["facts"]["renewal_notice_sent_on"], f["facts"]["period_ends_on"], rows["CND-6"]["measured"], rows["CND-6"]["result"]) == (
        "2026-10-03", "2026-10-31", 28, "met")


def test_af_7207_is_exactly_on_two_limits_and_neither_rule_fires(client):
    f, rows = measured(client, 7207)
    assert (f["facts"]["reported_on"], f["facts"]["acknowledged_on"], f["facts"]["pack_complete_on"], f["facts"]["decision_on"]) == (
        "2026-09-17", "2026-09-24", "2026-09-22", "2026-10-21")
    assert (rows["CND-1"]["measured"], rows["CND-1"]["limit"], rows["CND-1"]["result"], rows["CND-1"]["over_or_short_by"]) == (5, 5, "met", None)
    assert (rows["CND-2"]["measured"], rows["CND-2"]["limit"], rows["CND-2"]["result"]) == (20, 20, "met")
    assert "exactly the limit, which meets the rule" in rows["CND-1"]["sentence"] and f["measured"]["not_met"] == []


def test_af_7208_sent_the_renewal_notice_too_late(client):
    f, rows = measured(client, 7208)
    assert (f["facts"]["renewal_notice_sent_on"], f["facts"]["period_ends_on"]) == ("2026-10-13", "2026-10-28")
    assert (rows["CND-6"]["result"], rows["CND-6"]["measured"], rows["CND-6"]["limit"], rows["CND-6"]["over_or_short_by"]) == ("not_met", 15, 21, 6)
    assert (f["facts"]["change_asked_for_on"], f["facts"]["change_confirmed_on"], rows["CND-7"]["measured"], rows["CND-7"]["result"]) == (
        "2026-10-07", "2026-10-14", 4, "met")


def test_an_audit_record_is_a_versioned_draft_and_not_part_of_the_sample(client, store):
    before = copy.deepcopy({k: v for k, v in store.data.items() if k != "cd_audit_samples"})
    plain = [{**r, "file_id": r["file_id"].lower(), "result": r["result"].replace("_", " ").title()} for r in AUDIT_ROWS]
    one = post(client, "/audit-samples/AUD-7200/record", {**RECORD, "rows": plain})
    two = post(client, "/audit-samples/AUD-7200/record", {**RECORD, "drafted_by": "Compliance Audit"})
    assert (one["kind"], one["draft"]["version"], two["draft"]["version"], one["draft"]["rows_in_the_record"]) == ("draft", 1, 2, 20)
    assert [(r["file_id"], r["rule_id"], r["result"]) for r in one["draft"]["rows"]] == [(r["file_id"], r["rule_id"], r["result"]) for r in AUDIT_ROWS]
    system = one["draft"]["measured_by_the_system"]
    assert system["AF-7203"] == {"CND-1": "not_met", "CND-2": "met", "CND-3": "not_applicable"}
    assert system["AF-7206"]["CND-7"] == "cannot_tell" and system["AF-7205"]["CND-3"] == "for_reading"
    s = get(client, "/audit-samples/AUD-7200")
    assert "record_drafts" not in s and s["drafts_on_file"] == 2 and s["status"] == "to_be_checked" and "Eight files, twenty" not in json.dumps(s)
    assert [x["version"] for x in get(client, "/audit-samples/AUD-7200/drafts")["items"]] == [1, 2]
    assert {k: v for k, v in store.data.items() if k != "cd_audit_samples"} == before


def test_an_audit_record_is_refused_with_a_reason_and_nothing_is_saved(client):
    only_failures = [r for r in AUDIT_ROWS if r["result"] != "met"]
    short = post(client, "/audit-samples/AUD-7200/record", {**RECORD, "rows": only_failures}, 409)
    assert "the rules met as well" in short["detail"] and "13 of 20 rows are missing" in short["detail"] and "AF-7201 CND-1" in short["detail"]
    assert short["applied"] is False and "Nothing was saved" in short["detail"]
    wrong_kind = post(client, "/audit-samples/AUD-7200/record", {**RECORD, "rows": AUDIT_ROWS + [{"file_id": "AF-7202", "rule_id": "CND-1", "result": "met"}]}, 409)
    assert "AF-7202 CND-1" in wrong_kind["detail"]
    assert "AF-9999" in post(client, "/audit-samples/AUD-7200/record", {**RECORD, "rows": [{"file_id": "AF-9999", "rule_id": "CND-1", "result": "met"}]}, 409)["detail"]
    assert "Given twice: AF-7201 CND-1" in post(client, "/audit-samples/AUD-7200/record", {**RECORD, "rows": AUDIT_ROWS + AUDIT_ROWS[:1]}, 409)["detail"]
    assert "AF-9999" in post(client, "/audit-samples/AUD-7200/record", {**RECORD, "files_that_need_a_person": ["AF-9999"]}, 409)["detail"]
    assert post(client, "/audit-samples/AUD-7200/record", {**RECORD, "rows": [{**AUDIT_ROWS[0], "result": "breach"}]}, 422)["applied"] is False
    assert get(client, "/audit-samples/AUD-7200")["drafts_on_file"] == 0


# ---------------------------------------------------------------- publications and the obligations register
def pub(client, n):
    return get(client, f"/publications/PUB-{n}")


def key_dates(p):
    return {k["what"]: (k["date"], k["days_from_the_insurer_date"]) for k in p["key_dates"]}


def test_the_feed_lists_ten_items_newest_first_with_the_regulators_and_the_lines_written(client):
    post(client, "/publications/PUB-7301/impact-note", NOTE)
    doc = get(client, "/publications")
    assert [(p["publication_id"], p["reference"], p["kind"], p["published"]) for p in doc["items"]] == [
        ("PUB-7307", "MIA-C-2026-17", "circular", "2026-11-25"), ("PUB-7305", "MIA-C-2026-16", "circular", "2026-11-24"),
        ("PUB-7303", "MIA-FN-2026-02", "fee_notice", "2026-11-23"), ("PUB-7301", "MIA-C-2026-14", "circular", "2026-11-20"),
        ("PUB-7306", "MDPO-N-2026-19", "notice", "2026-11-20"), ("PUB-7304", "MIA-C-2026-15", "circular", "2026-11-19"),
        ("PUB-7308", "MIA-C-2026-13", "circular", "2026-11-19"), ("PUB-7302", "MIA-CP-2026-03", "consultation_paper", "2026-11-18"),
        ("PUB-7292", "MDPO-G-2026-04", "guidance", "2026-06-29"), ("PUB-7291", "MIA-C-2026-09", "circular", "2026-05-11")]
    assert all("impact_note_drafts" not in p and p["text"] for p in doc["items"])
    assert [r["name"] for r in doc["regulators_named"]] == ["Meridia Insurance Authority", "Meridia Data Protection Office"]
    assert doc["lines_of_business_written"] == ["private motor", "home", "commercial property", "motor fleet", "public liability", "group medical"]
    assert get(client, "/publications?status=new")["count"] == 8
    assert [p["publication_id"] for p in get(client, "/publications?status=noted earlier")["items"]] == ["PUB-7292", "PUB-7291"]
    assert client.get("/conduct/publications?status=old", headers=H).status_code == 409


def test_the_obligations_register_has_twelve_obligations_each_with_an_owner(client):
    doc = get(client, "/obligations")
    assert [o["obligation_id"] for o in doc["items"]] == [f"OBL-{n:02d}" for n in range(1, 13)]
    owners = {o["obligation_id"]: (o["owner"]["role"], o["owner"]["name"]) for o in doc["items"]}
    assert owners["OBL-03"] == ("Head of Claims", "Araminta Feldspar") and owners["OBL-05"] == ("Head of Complaints", "Winifred Stannard")
    assert owners["OBL-08"] == ("Head of Health Claims", "Cordelia Brightwater") and owners["OBL-11"] == ("Finance Director", "Gideon Farnsworth")
    assert owners["OBL-02"] == ("Head of Distribution", "Tiberius Ockenden") and owners["OBL-09"] == ("Data Protection Officer", "Ambrose Kettleby")
    assert "silent" in doc["how_to_read"]


def test_the_register_search_matches_any_word_and_lists_all_when_empty(client):
    assert get(client, "/obligations/search")["count"] == 12
    assert [o["obligation_id"] for o in get(client, "/obligations/search?text=complaint final response")["items"]][0] == "OBL-05"
    assert [o["obligation_id"] for o in get(client, "/obligations/search?text=cooling-off zebra")["items"]] == ["OBL-02"]
    assert [o["obligation_id"] for o in get(client, "/obligations/search?text=MIA-C-2026-09")["items"]] == ["OBL-03", "OBL-04"]
    assert [o["obligation_id"] for o in get(client, "/obligations/search?text=pre-authorisation")["items"]] == ["OBL-08"]
    assert [o["obligation_id"] for o in get(client, "/obligations/search?text=supervisory fee")["items"]] == ["OBL-11"]
    assert [o["obligation_id"] for o in get(client, "/obligations/search?text=breach 72 hours")["items"]] == ["OBL-09"]
    silent = get(client, "/obligations/search?text=automated tools aviation")
    assert silent["count"] == 0 and "silent" in silent["note"]


def test_pub_7301_shortens_the_final_response_limit_and_bears_on_obl_05(client):
    p = pub(client, 7301)
    assert (p["reference"], p["kind"], p["regulator"]) == ("MIA-C-2026-14", "circular", "Meridia Insurance Authority")
    assert key_dates(p) == {"published": ("2026-11-20", -6), "has effect from": ("2027-01-01", 36)}
    assert "From 1 Jan 2027" in p["text"] and "within 20 days" in p["text"] and "stays at 30 days" in p["text"]
    saved = post(client, "/publications/PUB-7301/impact-note", {**NOTE, "finding": "Bears on an obligation", "obligation_ids": ["obl-05"]})["draft"]
    assert (saved["finding"], saved["obligation_ids"]) == ("bears_on_an_obligation", ["OBL-05"])
    assert saved["owners_from_the_register"] == [{"obligation_id": "OBL-05", "heading": "Complaints: time limits",
                                                  "owner": {"role": "Head of Complaints", "name": "Winifred Stannard"}}]
    assert saved["dates_worked_out_by_the_system"][1]["days_from_the_insurer_date"] == 36


def test_pub_7302_is_a_consultation_and_changes_nothing_yet(client):
    p = pub(client, 7302)
    assert (p["reference"], p["kind"], p["effective_from"]) == ("MIA-CP-2026-03", "consultation_paper", None)
    assert key_dates(p) == {"published": ("2026-11-18", -8), "comments close on": ("2027-01-15", 50)}
    assert "from 14 days to 21 days" in p["text"] and "No rule changes" in p["text"] and "until 15 Jan 2027" in p["text"]
    saved = post(client, "/publications/PUB-7302/impact-note", {"finding": "consultation only", "obligation_ids": ["OBL-02"], "note": "A proposal."})["draft"]
    assert saved["finding"] == "consultation_only" and saved["owners_from_the_register"][0]["owner"]["name"] == "Tiberius Ockenden"


def test_pub_7303_is_a_fee_notice_and_bears_on_obl_11(client):
    p = pub(client, 7303)
    assert (p["reference"], p["kind"]) == ("MIA-FN-2026-02", "fee_notice")
    assert key_dates(p) == {"published": ("2026-11-23", -3), "payment is due by": ("2027-01-31", 66)}
    assert "USD 84,000.00" in p["text"] and "due by 31 Jan 2027" in p["text"]


def test_pub_7304_is_about_a_line_the_insurer_does_not_write(client):
    p = pub(client, 7304)
    assert (p["reference"], p["title"]) == ("MIA-C-2026-15", "Aviation hull and liability insurance: lowest policy limits")
    assert "only to insurers licensed for the aviation class" in p["text"] and "aviation" not in " ".join(p["lines_of_business_written"])
    assert "no aviation" in p["lines_note"] and key_dates(p)["has effect from"] == ("2027-03-02", 96)
    saved = post(client, "/publications/PUB-7304/impact-note", {"finding": "Does not apply", "note": "The insurer writes no aviation."})["draft"]
    assert (saved["finding"], saved["obligation_ids"], saved["owners_from_the_register"]) == ("does_not_apply", [], [])
    refused = post(client, "/publications/PUB-7304/impact-note", {"finding": "does_not_apply", "obligation_ids": ["OBL-03"], "note": "x"}, 409)
    assert "names no obligation" in refused["detail"]


def test_pub_7305_amends_an_earlier_circular_and_bears_on_obl_03_only(client):
    p = pub(client, 7305)
    earlier = pub(client, 7291)
    assert p["reference"] == "MIA-C-2026-16" and "amends Circular MIA-C-2026-09" in p["text"]
    assert "20 working days is replaced by 15 working days" in p["text"] and "From 1 Jan 2027" in p["text"] and "are unchanged" in p["text"]
    assert key_dates(p)["has effect from"] == ("2027-01-01", 36)
    assert (earlier["reference"], earlier["status"], earlier["noted_earlier"]["obligation_ids"]) == ("MIA-C-2026-09", "noted_earlier", ["OBL-03", "OBL-04"])
    assert key_dates(earlier) == {"published": ("2026-05-11", -199), "has effect from": ("2026-07-09", -140)}
    saved = post(client, "/publications/PUB-7305/impact-note", {**NOTE, "obligation_ids": ["OBL-03"], "related_publication_id": "pub-7291"})["draft"]
    assert (saved["related_publication_id"], saved["owners_from_the_register"][0]["owner"]["name"]) == ("PUB-7291", "Araminta Feldspar")


def test_pub_7306_repeats_an_older_item_under_a_new_reference(client):
    p, older = pub(client, 7306), pub(client, 7292)
    assert (p["reference"], older["reference"], p["regulator"]) == ("MDPO-N-2026-19", "MDPO-G-2026-04", "Meridia Data Protection Office")
    assert "republishes Guidance MDPO-G-2026-04" in p["text"] and "The text is unchanged" in p["text"]
    assert p["text"].split("\n")[-4:] == older["text"].split("\n")[-4:] and older["noted_earlier"]["obligation_ids"] == ["OBL-09"]
    assert p["effective_from"] is None and key_dates(older)["has effect from"] == ("2026-07-29", -120)
    saved = post(client, "/publications/PUB-7306/impact-note", {"finding": "duplicate of an earlier publication", "obligation_ids": ["OBL-09"],
                                                                "related_publication_id": "PUB-7292", "note": "Nothing new."})["draft"]
    assert saved["finding"] == "duplicate_of_an_earlier_publication"
    refused = post(client, "/publications/PUB-7306/impact-note", {"finding": "duplicate_of_an_earlier_publication", "note": "x"}, 409)
    assert "needs the id of the earlier publication" in refused["detail"]


def test_pub_7307_applies_and_no_obligation_of_the_register_covers_it(client):
    p = pub(client, 7307)
    assert p["reference"] == "MIA-C-2026-17" and "for all classes of business" in p["text"] and "From 1 Apr 2027" in p["text"]
    assert key_dates(p)["has effect from"] == ("2027-04-01", 126)
    blob = json.dumps(get(client, "/obligations")["items"]).lower()
    assert "automated" not in blob and "pricing" not in blob and "underwriting" not in blob
    saved = post(client, "/publications/PUB-7307/impact-note", {"finding": "No matching obligation", "note": "The register is silent."})["draft"]
    assert saved["finding"] == "no_matching_obligation"
    assert "leave obligation_ids empty" in post(client, "/publications/PUB-7307/impact-note",
                                                {"finding": "no_matching_obligation", "obligation_ids": ["OBL-12"], "note": "x"}, 409)["detail"]


def test_pub_7308_is_for_group_medical_and_bears_on_obl_08(client):
    p = pub(client, 7308)
    assert p["reference"] == "MIA-C-2026-13" and "group medical" in p["lines_of_business_written"]
    assert "within 2 working days" in p["text"] and "From 1 Feb 2027" in p["text"] and "stays at 5 working days" in p["text"]
    assert key_dates(p) == {"published": ("2026-11-19", -7), "has effect from": ("2027-02-01", 67)}
    obl = next(o for o in get(client, "/obligations")["items"] if o["obligation_id"] == "OBL-08")
    assert "within 5 working days" in obl["text"] and obl["lines_of_business"] == "group medical"


def test_an_impact_note_is_a_versioned_draft_and_not_part_of_the_publication(client, store):
    before = copy.deepcopy({k: v for k, v in store.data.items() if k != "cd_publications"})
    one = post(client, "/publications/PUB-7301/impact-note", NOTE)
    two = post(client, "/publications/PUB-7301/impact-note", {**NOTE, "drafted_by": "Regulatory Monitoring"})
    assert (one["kind"], one["draft"]["version"], two["draft"]["version"], two["draft"]["drafted_by"]) == ("draft", 1, 2, "Regulatory Monitoring")
    p = pub(client, 7301)
    assert "impact_note_drafts" not in p and p["drafts_on_file"] == 2 and p["status"] == "new" and "falls to 20 days" not in json.dumps(p)
    assert [x["version"] for x in get(client, "/publications/PUB-7301/drafts")["items"]] == [1, 2]
    assert {k: v for k, v in store.data.items() if k != "cd_publications"} == before


def test_an_impact_note_is_refused_with_a_reason_and_nothing_is_saved(client):
    unknown = post(client, "/publications/PUB-7301/impact-note", {**NOTE, "obligation_ids": ["OBL-99"]}, 409)
    assert "OBL-99" in unknown["detail"] and "Nothing was saved" in unknown["detail"] and unknown["applied"] is False
    assert "needs the obligation" in post(client, "/publications/PUB-7301/impact-note", {**NOTE, "obligation_ids": []}, 409)["detail"]
    assert "PUB-9999" in post(client, "/publications/PUB-7301/impact-note", {**NOTE, "related_publication_id": "PUB-9999"}, 409)["detail"]
    assert "not another publication" in post(client, "/publications/PUB-7301/impact-note", {**NOTE, "related_publication_id": "PUB-7301"}, 409)["detail"]
    assert post(client, "/publications/PUB-7301/impact-note", {**NOTE, "finding": "breach"}, 422)["applied"] is False
    assert pub(client, 7301)["drafts_on_file"] == 0


# ---------------------------------------------------------------- disputed claims
def docs_of(client, n):
    x = get(client, f"/disputed-claims/DSP-{n}")
    return x, {doc["document_id"][-3:]: doc for doc in x["documents"]}


def test_the_document_guide_has_seven_categories_and_seven_privilege_rules(client):
    doc = get(client, "/document-guide")
    assert [c["category_id"] for c in doc["document_categories"]] == [f"DC-{n}" for n in range(1, 8)]
    assert [(r["rule_id"], r["flag"]) for r in doc["privilege_guide"]] == [
        ("PG-1", "yes"), ("PG-2", "yes"), ("PG-3", "no"), ("PG-4", "unclear"), ("PG-5", "no"), ("PG-6", "unclear"), ("PG-7", "as the original")]
    assert "Apply PG-4 before PG-1" in doc["privilege_how_to_read"] and "not by" in doc["categories_how_to_read"]


def test_the_list_of_disputed_claims_holds_no_documents_and_no_drafts(client):
    post(client, "/disputed-claims/DSP-7403/schedule", schedule(client, "DSP-7403"))
    rows = get(client, "/disputed-claims")["items"]
    assert [(r["dispute_id"], r["claim_reference"], r["amount_in_dispute"], r["documents_in_the_set"]) for r in rows] == [
        ("DSP-7401", "DCL-7451", 186000.0, 11), ("DSP-7402", "DCL-7452", 74500.0, 9), ("DSP-7403", "DCL-7453", 58200.0, 8)]
    assert all("documents" not in r and "schedule_drafts" not in r and r["people_in_the_matter"] for r in rows)


def test_dsp_7401_holds_advice_forwarded_to_the_broker_a_copy_and_an_email_that_only_copies_a_lawyer(client):
    x, docs = docs_of(client, 7401)
    assert (x["policyholder"], x["line_of_business"]) == ("Hollowmere Cold Stores Ltd", "commercial property")
    assert [(k, v["dated"], v["author"]) for k, v in docs.items()] == [
        ("D01", "2026-07-29", "Barnabas Hollowmere"), ("D02", "2026-08-05", "Wilfred Ackerley"), ("D03", "2026-08-18", "Ignatius Calderbrook"),
        ("D04", "2026-08-28", "Griselda Hoxton"), ("D05", "2026-10-17", "Perpetua Quillon"), ("D06", "2026-10-19", "Griselda Hoxton"),
        ("D07", "2026-10-24", "Lucasta Pargeter"), ("D08", "2026-10-26", "Griselda Hoxton"), ("D09", "2026-11-14", "Lucasta Pargeter"),
        ("D10", "2026-08-18", "Ignatius Calderbrook"), ("D11", "2026-10-21", "Griselda Hoxton")]
    advice = "I put the prospects of defending the claim at somewhat better than even"
    assert advice in docs["D07"]["text"] and advice in docs["D08"]["text"] and "Privileged and confidential" in docs["D07"]["text"]
    assert docs["D08"]["to"] == ["Imelda Roe"] and docs["D08"]["recipients_outside_thornmere_and_its_lawyers"] == ["Imelda Roe"]
    assert docs["D06"]["recipients_outside_thornmere_and_its_lawyers"] == [] and "Please advise" in docs["D06"]["text"]
    assert docs["D07"]["recipients_outside_thornmere_and_its_lawyers"] == [] and docs["D07"]["author_role"].startswith("partner, external lawyer")
    assert docs["D10"]["identical_text_to"] == "DSP-7401-D03" and docs["D10"]["text"] == docs["D03"]["text"]
    assert [k for k, v in docs.items() if v["identical_text_to"]] == ["D10"]
    assert "to help decide the claim" in docs["D03"]["text"] and "DRAFT. Prepared for litigation." in docs["D09"]["text"]
    assert docs["D11"]["cc"] == ["Emeric Thornbury"] and docs["D11"]["to"] == ["Osbert Fane"] and "raise the reserve" in docs["D11"]["text"]
    assert not re.search(r"advi[cs]e|prospects|privileged", docs["D11"]["text"].lower())
    assert x["documents_in_date_order"][0] == "DSP-7401-D01" and x["documents_with_no_date"] == []
    side = {p["name"]: p["side"] for p in x["people_in_the_matter"]}
    assert (side["Imelda Roe"], side["Lucasta Pargeter"], side["Emeric Thornbury"]) == ("third party", "insurer's lawyers", "insurer's lawyers")


def test_dsp_7402_holds_a_report_made_for_the_proceedings_and_advice_passed_on_inside(client):
    x, docs = docs_of(client, 7402)
    assert "issued in the Port Ilvane District Court on 13 Oct 2026, case PIDC-2026-0871" in x["stage"]
    assert [(k, v["dated"], v["author"]) for k, v in docs.items()] == [
        ("D01", "2026-06-19", "Ferelith Dunmore"), ("D02", "2026-06-09", "Alaric Penhale"), ("D03", "2026-06-29", "Matthias Orlop"),
        ("D04", "2026-10-13", "Dorothea Kite"), ("D05", "2026-10-17", "Emeric Thornbury"), ("D06", "2026-10-18", "Matthias Orlop"),
        ("D07", "2026-11-06", "Hesketh Vane"), ("D08", "2026-07-09", "Matthias Orlop"), ("D09", "2026-06-19", "Ferelith Dunmore")]
    assert "My advice is to defend on contributory fault" in docs["D05"]["text"]
    assert "Emeric's legal advice" in docs["D06"]["text"] and docs["D06"]["recipients_outside_thornmere_and_its_lawyers"] == []
    assert "on the instructions of Emeric Thornbury" in docs["D07"]["text"] and "for the proceedings PIDC-2026-0871" in docs["D07"]["text"]
    assert docs["D08"]["cc"] == ["Emeric Thornbury"] and docs["D08"]["recipients_outside_thornmere_and_its_lawyers"] == ["Tidewater Coachworks"]
    assert "USD 3,240.00" in docs["D08"]["text"] and not re.search(r"advi[cs]e|liab", docs["D08"]["text"].lower())
    assert docs["D09"]["identical_text_to"] == "DSP-7402-D01" and "USD 74,500.00" in docs["D04"]["text"]
    assert x["documents_in_date_order"][:2] == ["DSP-7402-D02", "DSP-7402-D01"]


def test_dsp_7403_holds_a_note_with_no_date_and_no_author(client):
    x, docs = docs_of(client, 7403)
    assert [(k, v["dated"], v["author"]) for k, v in docs.items()] == [
        ("D01", "2025-10-22", "Thornmere Mutual Insurance, policy administration"), ("D02", "2026-07-09", "Thaddea Wolstencroft"),
        ("D03", "2026-07-31", "Fennimore Drake"), ("D04", "2026-08-13", "Griselda Hoxton"), ("D05", "2026-08-23", "Thaddea Wolstencroft"),
        ("D06", "2026-09-27", "Lucasta Pargeter"), ("D07", None, None), ("D08", "2026-11-17", "Lucasta Pargeter")]
    assert docs["D07"]["text"] == "Spoke to L. about the start date point. View is: arguable but not strong. Think about an offer?"
    assert docs["D07"]["author_role"] is None and x["documents_with_no_date"] == ["DSP-7403-D07"] and x["documents_in_date_order"][-1] == "DSP-7403-D07"
    assert "arguable but it is not strong" in docs["D06"]["text"] and "DRAFT. Prepared for litigation. Not filed." in docs["D08"]["text"]
    assert all(v["identical_text_to"] is None for v in docs.values())


def test_the_right_schedule_of_every_disputed_claim_is_accepted(client):
    counts = {"DSP-7401": (3, 7, 1), "DSP-7402": (3, 6, 0), "DSP-7403": (2, 5, 1)}
    for dispute_id, (yes, no, unclear) in counts.items():
        saved = post(client, f"/disputed-claims/{dispute_id}/schedule", schedule(client, dispute_id))["draft"]
        system = saved["counted_by_the_system"]
        assert (system["flagged_yes"], system["flagged_no"], system["flagged_unclear"]) == (yes, no, unclear), dispute_id
        assert system["documents_in_the_set"] == system["rows"] == yes + no + unclear


def test_a_document_schedule_is_a_versioned_draft_and_not_part_of_the_disputed_claim(client, store):
    before = copy.deepcopy({k: v for k, v in store.data.items() if k != "cd_disputes"})
    body = schedule(client, "DSP-7401")
    plain = {**body, "rows": [{**r, "document_id": r["document_id"].lower(), "may_be_privileged": r["may_be_privileged"].title(),
                               "category_id": r["category_id"].lower()} for r in body["rows"]]}
    one = post(client, "/disputed-claims/DSP-7401/schedule", plain)
    two = post(client, "/disputed-claims/DSP-7401/schedule", {**body, "drafted_by": "Litigation Support"})
    assert (one["kind"], one["draft"]["version"], two["draft"]["version"], two["draft"]["drafted_by"]) == ("draft", 1, 2, "Litigation Support")
    row = one["draft"]["rows"][7]
    assert (row["document_id"], row["category_id"], row["may_be_privileged"], row["rule_id"]) == ("DSP-7401-D08", "DC-6", "unclear", "PG-4")
    assert one["draft"]["rows"][9]["duplicate_of"] == "DSP-7401-D03" and one["draft"]["rows"][0]["duplicate_of"] is None
    x = get(client, "/disputed-claims/DSP-7401")
    assert "schedule_drafts" not in x and x["drafts_on_file"] == 2 and x["status"] == "documents_to_be_sorted"
    assert "may_be_privileged" not in json.dumps(x)
    assert [v["version"] for v in get(client, "/disputed-claims/DSP-7401/drafts")["items"]] == [1, 2]
    assert {k: v for k, v in store.data.items() if k != "cd_disputes"} == before


def test_a_document_schedule_is_refused_with_a_reason_and_nothing_is_saved(client):
    body = schedule(client, "DSP-7403")
    rows = body["rows"]
    short = post(client, "/disputed-claims/DSP-7403/schedule", {**body, "rows": rows[:6]}, 409)
    assert "2 of 8 have no row: DSP-7403-D07, DSP-7403-D08" in short["detail"] and "Nothing was saved" in short["detail"] and short["applied"] is False
    other = post(client, "/disputed-claims/DSP-7403/schedule", {**body, "rows": rows + [{**rows[0], "document_id": "DSP-7401-D01"}]}, 409)
    assert "Not a document of DSP-7403: DSP-7401-D01" in other["detail"]
    assert "Given twice: DSP-7403-D01" in post(client, "/disputed-claims/DSP-7403/schedule", {**body, "rows": rows + rows[:1]}, 409)["detail"]
    assert "DC-9" in post(client, "/disputed-claims/DSP-7403/schedule", {**body, "rows": [{**rows[0], "category_id": "DC-9"}] + rows[1:]}, 409)["detail"]
    assert "PG-9" in post(client, "/disputed-claims/DSP-7403/schedule", {**body, "rows": [{**rows[0], "rule_id": "PG-9"}] + rows[1:]}, 409)["detail"]
    self_copy = post(client, "/disputed-claims/DSP-7403/schedule", {**body, "rows": [{**rows[0], "duplicate_of": "DSP-7403-D01"}] + rows[1:]}, 409)
    assert "must be another document of the set" in self_copy["detail"]
    assert post(client, "/disputed-claims/DSP-7403/schedule", {**body, "rows": [{**rows[0], "may_be_privileged": "privileged"}] + rows[1:]}, 422)["applied"] is False
    assert get(client, "/disputed-claims/DSP-7403")["drafts_on_file"] == 0


# ---------------------------------------------------------------- unknown ids, reset and counts
def test_an_unknown_conduct_id_is_a_plain_404(client):
    for path, words in (("/complaints/CMP-9999", "No complaint with id CMP-9999"), ("/complaints/CLM-4010", "No complaint with id CLM-4010"),
                        ("/audit-samples/AUD-9999", "No audit sample with id AUD-9999"), ("/audit-files/AF-9999/measure", "No audit file"),
                        ("/publications/PUB-9999", "No publication with id PUB-9999"), ("/disputed-claims/DSP-9999", "No disputed claim"),
                        ("/complaints/CMP-9999/deadlines", "No complaint"), ("/disputed-claims/DSP-9999/drafts", "No disputed claim")):
        r = client.get(f"/conduct{path}", headers=H)
        assert r.status_code == 404 and words in r.json()["detail"] and r.json()["applied"] is False
    assert client.post("/conduct/complaints/CMP-9999/response", headers=H, json=RESPONSE).status_code == 404


def test_putting_the_conduct_system_back_leaves_the_claims_system_alone_and_the_other_way_round(client, store):
    triage = {"rule_id": "HG-3", "track": "fast track", "team": "fast-track team", "severity": "low", "reason": "Estimate under 2,500."}
    client.post("/claims/claims/CLM-4001/triage", headers=H, json=triage)
    post(client, "/complaints/CMP-7101/response", RESPONSE)
    post(client, "/audit-samples/AUD-7200/record", RECORD)
    post(client, "/publications/PUB-7301/impact-note", NOTE)
    post(client, "/disputed-claims/DSP-7402/schedule", schedule(client, "DSP-7402"))
    changed = client.get("/admin/state", headers=H).json()["changed_by"]
    assert changed["claims"] == ["claims"] and changed["conduct"] == ["cd_audit_samples", "cd_complaints", "cd_disputes", "cd_publications"]
    fresh = build_all(TODAY_D)
    assert client.post("/admin/reset/claims", headers=H).json()["put_back"] == ["claims"]
    assert len(store.data["cd_complaints"]["CMP-7101"]["response_drafts"]) == 1
    client.post("/claims/claims/CLM-4001/triage", headers=H, json=triage)
    back = client.post("/admin/reset/conduct", headers=H).json()
    assert back["put_back"] == ["cd_audit_samples", "cd_complaints", "cd_disputes", "cd_publications"]
    assert all(store.data[name] == fresh[name] for name in CD_SETS)
    assert len(store.data["claims"]["CLM-4001"]["triage_drafts"]) == 1
    client.post("/admin/reset", headers=H)
    assert store.data == fresh


def test_the_counts_name_the_open_items_of_the_conduct_system(client):
    counts = client.get("/admin/state", headers=H).json()["counts"]
    assert (counts["complaints_new"], counts["regulatory_publications_new"], counts["disputed_claims_to_be_sorted"]) == (8, 8, 3)
