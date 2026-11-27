"""The underwriting system: the right answers of the Underwriting section of SCENARIOS.md, every refusal, and the rules drafts keep.

Checked against the data the service gives at the insurer date 2026-11-26."""
import copy
import json
import re
from datetime import date

from insurer.seed import build_all
from insurer.seed_underwriting import build_underwriting
from conftest import H, TODAY

TODAY_D = date.fromisoformat(TODAY)
UW_SETS = sorted(build_underwriting(TODAY_D))


def get(client, path):
    r = client.get(f"/underwriting{path}", headers=H)
    assert r.status_code == 200, (path, r.status_code, r.text[:300])
    return r.json()


def post(client, path, body=None, status=200):
    r = client.post(f"/underwriting{path}", json=body or {}, headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:400])
    return r.json()


def sub(client, n):
    return get(client, f"/submissions/SBM-{n}")


def measure(client, n):
    return {r["rule_id"]: r for r in sub(client, n)["measured_against_guidelines"]["rules"]}


def ref(client, n):
    return get(client, f"/referrals/REF-{n}")


def rnw(client, n):
    return get(client, f"/renewals/RNW-{n}")


def rules_of(pack):
    return {r["rule_id"]: r for r in pack["rules"]}


PROPERTY_ROWS = [{"rule_id": f"UG-{n}", "finding": "within", "evidence": "As the system measures it."} for n in range(1, 7)]
FILE = {"findings": PROPERTY_ROWS, "next_step": "ready_for_the_underwriter", "summary": "Within every guideline."}
MEMO = {"referral_needed": "yes", "refer_to_grade": "senior_underwriter", "forcing_rules": ["RF-2", "UG-1"],
        "precedents": [{"precedent_id": "PRC-6401", "bearing": "agrees", "note": "Approved with conditions by Isolde Varney."}],
        "memo": "The risk is outside UG-1 and goes to a senior underwriter under RF-2."}
REVIEW = {"next_step": "refer_to_the_senior_underwriter", "rules_that_apply": ["RN-1"], "points_to_raise": ["Loss ratio 82.50 percent."],
          "summary": "The loss ratio is above the limit."}


# ---------------------------------------------------------------- the system as a whole
def test_the_underwriting_system_has_20_operations_and_every_save_is_a_draft(client):
    doc = client.get("/underwriting/openapi.json").json()
    ops = [(method, op) for item in doc["paths"].values() for method, op in item.items()]
    assert len(ops) == 20
    saves = sorted(op["operationId"] for method, op in ops if method != "get")
    assert saves == ["save_referral_memo", "save_renewal_review", "save_underwriting_file"]
    for method, op in ops:
        assert not op["summary"].endswith("(change)"), op["operationId"]
        if method != "get":
            assert op["summary"].endswith("(draft)"), op["operationId"]
    assert client.get("/underwriting/submissions").status_code == 401
    assert "underwriting/openapi.json" in client.get("/").text


def test_underwriting_ids_have_their_own_ranges_and_collide_with_nothing():
    data = build_all(TODAY_D)
    prefixes = {"uw_guidelines": "UG-", "uw_appetite": "AP-", "uw_submissions": "SBM-65", "uw_referral_rules": "RF-",
                "uw_referrals": "REF-66", "uw_precedents": "PRC-64", "uw_renewal_rules": "RN-", "uw_commercial_policies": "CPL-68",
                "uw_renewals": "RNW-67"}
    for name, prefix in prefixes.items():
        assert all(key.startswith(prefix) for key in data[name]), name
    mine = {key for name in UW_SETS for key in data[name]}
    others = {key for name, records in data.items() if name not in UW_SETS and isinstance(records, dict) for key in records}
    assert not mine & others
    claim_ids = [c["claim_id"] for p in data["uw_commercial_policies"].values() for c in p["claims"]]
    assert claim_ids == [f"CCL-69{n:02d}" for n in range(1, 7)] and not set(claim_ids) & set(data["claims"])


def test_no_text_of_the_underwriting_data_holds_a_bare_date_or_counts_days():
    data = build_underwriting(TODAY_D)
    texts = [doc["text"] for s in data["uw_submissions"].values() for doc in s["documents"]]
    texts += [c["text"] for r in data["uw_renewals"].values() for c in r["changes_reported"]]
    texts += [r["underwriter_note"] for r in data["uw_referrals"].values()] + [p["summary"] for p in data["uw_precedents"].values()]
    assert len(texts) == 9 + 2 + 5 + 5
    for text in texts:
        assert not re.search(r"\b20\d\d-\d\d-\d\d\b", text), text
    blob = json.dumps(data).lower()
    for word in ("yesterday", "last week", "days ago", "weeks ago", "last month", "this morning", "tomorrow", "monday", "tuesday",
                 "wednesday", "thursday", "friday", "saturday", "sunday", chr(8212)):
        assert word not in blob, word


# ---------------------------------------------------------------- guidelines and the measure
def test_the_guidelines_are_ten_numbered_rules_by_class(client):
    doc = get(client, "/guidelines")
    assert [r["rule_id"] for r in doc["items"]] == [f"UG-{n}" for n in range(1, 11)]
    assert [r["rule_id"] for r in doc["items"] if r["kind"] == "for_reading"] == ["UG-2", "UG-9"]
    assert sorted(doc["construction_classes"]) == ["A", "B", "C"]
    assert [r["rule_id"] for r in get(client, "/guidelines?class_of_business=motor_fleet")["items"]] == ["UG-7", "UG-8", "UG-9", "UG-10"]
    assert client.get("/underwriting/guidelines?class_of_business=marine", headers=H).status_code == 409


def test_the_list_of_submissions_is_whole_and_holds_no_drafts(client):
    post(client, "/submissions/SBM-6501/file", FILE)
    rows = get(client, "/submissions")["items"]
    assert [r["submission_id"] for r in rows] == [f"SBM-65{n:02d}" for n in range(1, 9)]
    assert all("file_drafts" not in r and r["documents"] and r["risk"] for r in rows)
    assert [r["submission_id"] for r in get(client, "/submissions?class_of_business=motor_fleet")["items"]] == ["SBM-6502", "SBM-6505"]


def test_sbm_6501_is_within_every_measured_rule(client):
    s = sub(client, 6501)
    m = s["measured_against_guidelines"]
    assert (s["insured"], s["received"], s["cover_start_requested"]) == ("Larkspur Lane Stationers Ltd", "2026-11-24", "2026-12-31")
    assert m["total_sum_insured"] == 1800000.0 and "USD 1,200,000.00 buildings + USD 350,000.00 contents + USD 250,000.00 stock" in m["total_sum_insured_working"]
    assert (m["within"], m["outside"], m["cannot_be_measured"], m["for_reading"]) == (["UG-1", "UG-3", "UG-4", "UG-5", "UG-6"], [], [], ["UG-2"])
    assert [r["rule_id"] for r in s["guidelines_for_this_class"]] == [f"UG-{n}" for n in range(1, 7)]
    assert get(client, "/submissions/SBM-6501/measure")["rules"] == m["rules"]


def test_sbm_6502_is_a_fleet_within_every_measured_rule(client):
    m = measure(client, 6502)
    assert [m[r]["result"] for r in ("UG-7", "UG-8", "UG-9", "UG-10")] == ["within", "within", "for_reading", "within"]
    assert (m["UG-7"]["measured"], m["UG-8"]["measured"], m["UG-8"]["limit"], m["UG-10"]["measured"], m["UG-10"]["limit"]) == (24, 12.5, 20.0, 5, 6)
    assert "4 of the 32 named drivers are under 25: 12.50 percent" in m["UG-8"]["sentence"]


def test_sbm_6503_is_over_the_sum_insured_limit_for_its_construction_class(client):
    s = sub(client, 6503)
    m = s["measured_against_guidelines"]
    row = measure(client, 6503)["UG-1"]
    assert s["risk"]["construction_class"] == "C" and m["outside"] == ["UG-1"]
    assert (row["measured"], row["limit"], row["over_by"], row["result"]) == (1350000.0, 1000000.0, 350000.0, "outside")
    assert "over the limit by USD 350,000.00" in row["sentence"]
    assert measure(client, 6503)["UG-3"]["limit"] == "not needed" and measure(client, 6503)["UG-4"]["measured"]["claims"] == 0


def test_sbm_6504_is_an_excluded_occupancy_that_only_reading_finds(client):
    s = sub(client, 6504)
    m = s["measured_against_guidelines"]
    assert m["outside"] == [] and m["for_reading"] == ["UG-2"] and m["total_sum_insured"] == 900000.0
    assert "waste recycling" in s["risk"]["occupancy"] and "scrap" in s["risk"]["occupancy"].lower()
    ug2 = next(r for r in s["guidelines_for_this_class"] if r["rule_id"] == "UG-2")
    assert "waste recycling or a scrap yard" in ug2["text"]


def test_sbm_6505_has_no_claims_history_and_the_system_does_not_guess(client):
    s = sub(client, 6505)
    row = measure(client, 6505)["UG-10"]
    assert s["claims_history"] is None and row["result"] == "cannot_be_measured" and row["measured"] is None
    assert "nothing is assumed" in row["sentence"] and s["measured_against_guidelines"]["cannot_be_measured"] == ["UG-10"]
    assert "will follow from the holding insurer" in s["documents"][0]["text"]
    assert (measure(client, 6505)["UG-7"]["measured"], measure(client, 6505)["UG-8"]["measured"]) == (40, 12.0)


def test_sbm_6506_the_form_says_sprinklers_and_the_survey_note_says_decommissioned(client):
    s = sub(client, 6506)
    row = measure(client, 6506)["UG-3"]
    assert s["risk"]["sprinklers"] == "yes" and row["result"] == "within" and row["limit"] == "needed"
    assert "uses the form's field only" in row["sentence"] and s["measured_against_guidelines"]["total_sum_insured"] == 2200000.0
    note = s["documents"][1]
    assert note["document_id"] == "SBM-6506-D2" and "decommissioned on 17 Sep 2026" in note["text"] and "Visited: 17 Oct 2026" in note["text"]


def test_sbm_6507_is_outside_on_two_rules(client):
    m = sub(client, 6507)["measured_against_guidelines"]
    rows = measure(client, 6507)
    assert m["outside"] == ["UG-1", "UG-4"] and m["total_sum_insured"] == 3100000.0
    assert (rows["UG-1"]["over_by"], rows["UG-4"]["measured"], rows["UG-4"]["over_by"]) == (600000.0, {"claims": 4, "largest_claim": 48000.0}, 1)
    assert rows["UG-3"]["result"] == "within"


def test_sbm_6508_is_exactly_on_two_limits_and_neither_rule_fires(client):
    m = sub(client, 6508)["measured_against_guidelines"]
    rows = measure(client, 6508)
    assert m["outside"] == [] and m["total_sum_insured"] == 2500000.0
    assert (rows["UG-1"]["measured"], rows["UG-1"]["limit"], rows["UG-1"]["result"], rows["UG-1"]["over_by"]) == (2500000.0, 2500000.0, "within", None)
    assert "exactly on the limit, which is within" in rows["UG-1"]["sentence"]
    assert (rows["UG-6"]["measured"], rows["UG-6"]["limit"], rows["UG-6"]["result"]) == (5000.0, 5000.0, "within")


def test_an_underwriting_file_is_a_versioned_draft_and_not_part_of_the_submission(client, store):
    before = copy.deepcopy({k: v for k, v in store.data.items() if k != "uw_submissions"})
    body = {"findings": [{"rule_id": "ug-1", "finding": "Within", "evidence": "USD 2,200,000.00 against USD 2,500,000.00."},
                         {"rule_id": "UG-3", "finding": "cannot tell", "evidence": "Form: yes. Survey note SBM-6506-D2: decommissioned."}],
            "contradictions": ["Sprinklers: the form says yes, SBM-6506-D2 says decommissioned on 17 Sep 2026."],
            "next_step": "Ask the broker", "question_for_the_broker": "Is the sprinkler system in working order?",
            "summary": "UG-3 cannot be settled from the file."}
    one = post(client, "/submissions/SBM-6506/file", body)
    two = post(client, "/submissions/SBM-6506/file", {**body, "drafted_by": "Underwriting Support"})
    assert (one["kind"], one["draft"]["version"], two["draft"]["version"], two["draft"]["drafted_by"]) == ("draft", 1, 2, "Underwriting Support")
    assert one["draft"]["next_step"] == "ask_the_broker" and one["draft"]["findings"][1]["finding"] == "cannot_tell"
    assert one["draft"]["findings"][0]["rule_id"] == "UG-1"
    assert one["draft"]["measured_by_the_system"] == {"within": ["UG-1", "UG-3", "UG-4", "UG-5", "UG-6"], "outside": [],
                                                      "cannot_be_measured": [], "for_reading": ["UG-2"]}
    s = sub(client, 6506)
    assert "file_drafts" not in s and s["drafts_on_file"] == 2 and s["status"] == "received" and "ask_the_broker" not in json.dumps(s)
    assert [x["version"] for x in get(client, "/submissions/SBM-6506/drafts")["items"]] == [1, 2]
    assert {k: v for k, v in store.data.items() if k != "uw_submissions"} == before


def test_an_underwriting_file_is_refused_with_a_reason_and_nothing_is_saved(client):
    wrong = post(client, "/submissions/SBM-6501/file", {**FILE, "findings": [{"rule_id": "UG-7", "finding": "within"}]}, 409)
    assert "UG-7" in wrong["detail"] and "Nothing was saved" in wrong["detail"] and wrong["applied"] is False
    twice = post(client, "/submissions/SBM-6501/file", {**FILE, "findings": PROPERTY_ROWS[:1] * 2}, 409)
    assert "given twice" in twice["detail"]
    ask = post(client, "/submissions/SBM-6505/file", {"findings": [{"rule_id": "UG-10", "finding": "missing"}], "next_step": "ask_the_broker",
                                                      "summary": "No claims history."}, 409)
    assert "question for the broker" in ask["detail"]
    assert post(client, "/submissions/SBM-6501/file", {**FILE, "next_step": "accept"}, 422)["applied"] is False
    assert post(client, "/submissions/SBM-6501/file", {"findings": PROPERTY_ROWS, "next_step": "ready_for_the_underwriter"}, 422)["applied"] is False
    assert all(sub(client, n)["drafts_on_file"] == 0 for n in (6501, 6505))


# ---------------------------------------------------------------- appetite
def test_the_appetite_statement_reads_whole_and_by_class(client):
    doc = get(client, "/appetite")
    assert doc["count"] == 14 and "silent" in doc["how_to_read"] and "stricter position wins" in doc["how_to_read"]
    assert "brick or concrete walls" in doc["construction_classes"]["A"] and "brick or block walls" in doc["construction_classes"]["B"]
    assert doc["construction_classes"] == get(client, "/guidelines")["construction_classes"]
    assert all(doc["construction_classes"][k].startswith(f"Class {k} is ") and doc["construction_classes"][k].endswith(".") for k in "ABC")
    general = doc["items"][-1]
    assert (general["rule_id"], general["position"], general["class_of_business"]) == ("AP-G1", "general", "all_classes")
    assert "outside over refer, and refer over within" in general["text"] and "names both rules" in general["text"]
    assert [(r["rule_id"], r["position"]) for r in get(client, "/appetite?class_of_business=commercial_property")["items"]] == [
        ("AP-P1", "within"), ("AP-P2", "within"), ("AP-P3", "outside"), ("AP-P4", "within"), ("AP-P5", "refer"), ("AP-P6", "refer"),
        ("AP-G1", "general")]
    assert [(r["rule_id"], r["position"]) for r in get(client, "/appetite?class_of_business=motor_fleet")["items"]] == [
        ("AP-M1", "within"), ("AP-M2", "outside"), ("AP-M3", "refer"), ("AP-M4", "within"), ("AP-G1", "general")]
    assert [(r["rule_id"], r["position"]) for r in get(client, "/appetite?class_of_business=public_liability")["items"]] == [
        ("AP-L1", "within"), ("AP-L2", "outside"), ("AP-L3", "refer"), ("AP-G1", "general")]


def test_the_eight_appetite_questions_have_their_rule(client):
    def first(text):
        rows = get(client, f"/appetite/search?text={text}")["items"]
        return (rows[0]["rule_id"], rows[0]["position"]) if rows else None

    assert first("brick warehouse storing tinned food") == ("AP-P1", "within")
    assert first("fireworks store") == ("AP-P3", "outside")
    assert first("joinery workshop with dust extraction") == ("AP-P4", "within")
    assert first("unoccupied mill building") == ("AP-P5", "refer")
    assert first("vans carrying the firm's own bread") == ("AP-M1", "within")
    assert first("taxi") == ("AP-M2", "outside")
    assert [r["rule_id"] for r in get(client, "/appetite/search?text=taxi fleet")["items"]] == ["AP-M1", "AP-M2", "AP-M3"]
    assert first("roofing contractor") == ("AP-L3", "refer")
    silent = get(client, "/appetite/search?text=solar farm")
    assert silent["count"] == 0 and "silent" in silent["note"] and "an underwriter answers" in silent["note"]
    blob = json.dumps(get(client, "/appetite")["items"]).lower()
    assert "solar" not in blob and "farm" not in blob


def test_the_appetite_search_matches_any_word_and_lists_all_when_empty(client):
    everything = get(client, "/appetite/search")
    assert everything["count"] == 14 and sorted(everything["construction_classes"]) == ["A", "B", "C"]
    assert "stricter position wins" in everything["when_two_rules_match"]
    rows = get(client, "/appetite/search?text=nightclubs zebra")["items"]
    assert [r["rule_id"] for r in rows] == ["AP-P3"] and rows[0]["matched_words"] == ["nightclubs"]
    assert get(client, "/appetite/search?text=taxis&class_of_business=commercial_property")["count"] == 0


# ---------------------------------------------------------------- authority, referrals and precedents
def test_the_authority_levels_are_four_grades_lowest_first(client):
    doc = get(client, "/authority-levels")
    assert [(g["grade"], g["most_total_sum_insured"], g["most_vehicles_in_a_fleet"], g["most_discount_percent"],
             g["may_write_outside_a_guideline"]) for g in doc["grades"]] == [
        ("assistant_underwriter", 500000.0, 25, 0.0, False), ("underwriter", 1500000.0, 75, 10.0, False),
        ("senior_underwriter", 5000000.0, 150, 20.0, True), ("head_of_underwriting", 15000000.0, 400, 35.0, True)]
    assert [r["rule_id"] for r in doc["referral_rules"]] == ["RF-1", "RF-2", "RF-3"]


def check(client, n):
    r = ref(client, n)
    a = r["authority_check"]
    return r, a, {x["rule_id"]: x for x in a["rules"]}


def test_ref_6601_is_forced_by_rf_2_and_two_precedents_agree(client):
    r, a, rows = check(client, 6601)
    assert (r["asked_by"], r["submission_id"], r["raised_on"]) == ({"name": "Benedick Morrow", "grade": "underwriter"}, "SBM-6503", "2026-11-25")
    assert (a["referral_needed"], a["refer_to_grade"], a["forced_by"]) == (True, "senior_underwriter", ["RF-2"])
    assert rows["RF-1"]["applies"] is False and rows["RF-1"]["measured"] == 1350000.0 and rows["RF-2"]["measured"] == ["UG-1"]
    found = get(client, "/precedents?rule_id=UG-1")["items"]
    assert [p["precedent_id"] for p in found] == ["PRC-6401", "PRC-6402", "PRC-6403"]
    assert [(p["construction_class"], p["decision"], p["decided_by"]["name"], p["total_sum_insured"]) for p in found[:2]] == [
        ("C", "approved_with_conditions", "Isolde Varney", 1280000.0), ("C", "approved_with_conditions", "Isolde Varney", 1150000.0)]
    assert [p["precedent_id"] for p in get(client, "/precedents?text=showroom")["items"]] == ["PRC-6401", "PRC-6402"]
    assert get(client, "/referrals/REF-6601/authority")["rules"] == a["rules"]


def test_ref_6602_has_a_precedent_that_looks_alike_and_differs_on_sprinklers(client):
    r, a, rows = check(client, 6602)
    assert (a["referral_needed"], a["refer_to_grade"], a["forced_by"]) == (True, "senior_underwriter", ["RF-1", "RF-2"])
    assert (rows["RF-1"]["measured"], rows["RF-1"]["authority_of_the_asking_grade"], rows["RF-1"]["grade_needed"]) == (
        2900000.0, 1500000.0, "senior_underwriter")
    assert rows["RF-2"]["measured"] == ["UG-1", "UG-3"] and r["risk"]["sprinklers"] == "no"
    alike = get(client, "/precedents?text=grain")["items"]
    assert [p["precedent_id"] for p in alike] == ["PRC-6403"]
    p = alike[0]
    assert (p["occupancy"], p["construction_class"], p["total_sum_insured"], p["sprinklers"], p["decision"]) == (
        r["risk"]["occupancy"], "B", 2850000.0, "yes", "approved_with_conditions")
    assert "rests on the sprinklers" in p["summary"]
    assert get(client, "/precedents?rule_id=UG-3")["count"] == 0


def test_ref_6603_goes_to_the_head_of_underwriting_and_has_no_precedent(client):
    r, a, rows = check(client, 6603)
    assert r["asked_by"]["grade"] == "senior_underwriter" and r["class_of_business"] == "motor_fleet"
    assert (a["referral_needed"], a["refer_to_grade"], a["forced_by"]) == (True, "head_of_underwriting", ["RF-1"])
    assert (rows["RF-1"]["measured"], rows["RF-1"]["authority_of_the_asking_grade"]) == (180, 150)
    assert rows["RF-2"]["applies"] is False and rows["RF-2"]["measured"] == ["UG-7"]
    for query in ("?class_of_business=motor_fleet", "?rule_id=UG-7", "?text=fleet vehicles"):
        none = get(client, f"/precedents{query}")
        assert none["count"] == 0 and "no precedent was found" in none["note"]


def test_ref_6604_needs_no_referral_the_asking_grade_has_the_authority(client):
    r, a, rows = check(client, 6604)
    assert (a["referral_needed"], a["refer_to_grade"], a["forced_by"], a["discount_percent"]) == (False, None, [], 15.0)
    assert all(row["applies"] is False for row in rows.values())
    assert (rows["RF-1"]["measured"], rows["RF-1"]["authority_of_the_asking_grade"], rows["RF-3"]["authority_of_the_asking_grade"]) == (
        3200000.0, 5000000.0, 20.0)
    assert "Isolde Varney may decide it without a referral" in a["sentence"]
    saved = post(client, "/referrals/REF-6604/memo", {"referral_needed": "No", "memo": "No referral is needed."})["draft"]
    assert saved["referral_needed"] == "no" and saved["authority_check_by_the_system"]["referral_needed"] is False
    refused = post(client, "/referrals/REF-6604/memo", {"referral_needed": "no", "refer_to_grade": "head of underwriting", "memo": "x"}, 409)
    assert "no grade to refer to" in refused["detail"]


def test_ref_6605_is_forced_by_the_discount_and_one_precedent_went_against(client):
    r, a, rows = check(client, 6605)
    assert (a["referral_needed"], a["refer_to_grade"], a["forced_by"], a["discount_percent"]) == (True, "senior_underwriter", ["RF-3"], 18.0)
    assert (r["proposed_terms"]["technical_premium"], r["proposed_terms"]["proposed_premium"]) == (8000.0, 6560.0)
    assert "18.00 percent below the technical premium of USD 8,000.00" in rows["RF-3"]["sentence"]
    found = get(client, "/precedents?rule_id=RF-3")["items"]
    assert [(p["precedent_id"], p["decision"], p["decided_by"]["grade"], p["decided_on"]) for p in found] == [
        ("PRC-6404", "declined", "senior_underwriter", "2026-05-30"), ("PRC-6405", "approved", "head_of_underwriting", "2025-06-24")]
    assert "three-year agreement" in found[1]["summary"] and "matching another insurer's price" in found[0]["summary"]


def test_precedents_list_whole_and_search_matches_any_word(client):
    assert [p["precedent_id"] for p in get(client, "/precedents")["items"]] == [f"PRC-640{n}" for n in range(1, 6)]
    assert [p["precedent_id"] for p in get(client, "/precedents?text=coffee zebra")["items"]] == ["PRC-6404"]
    assert [(p["precedent_id"], p["decided_on"]) for p in get(client, "/precedents?rule_id=RF-1")["items"]] == [("PRC-6403", "2026-01-30")]


def test_a_referral_memo_is_a_versioned_draft_and_not_part_of_the_referral(client, store):
    before = copy.deepcopy({k: v for k, v in store.data.items() if k != "uw_referrals"})
    one = post(client, "/referrals/REF-6601/memo", {**MEMO, "referral_needed": "Yes", "refer_to_grade": "Senior underwriter",
                                                    "precedents": [{"precedent_id": "PRC-6401", "bearing": "Agrees"},
                                                                   {"precedent_id": "PRC-6403", "bearing": "differs on a material fact"}]})
    two = post(client, "/referrals/REF-6601/memo", MEMO)
    assert (one["draft"]["version"], two["draft"]["version"], one["draft"]["refer_to_grade"]) == (1, 2, "senior_underwriter")
    assert [p["bearing"] for p in one["draft"]["precedents"]] == ["agrees", "differs_on_a_material_fact"]
    assert one["draft"]["authority_check_by_the_system"] == {"referral_needed": True, "refer_to_grade": "senior_underwriter",
                                                             "forced_by": ["RF-2"], "discount_percent": 0.0}
    r = ref(client, 6601)
    assert "memo_drafts" not in r and r["drafts_on_file"] == 2 and r["status"] == "memo_to_be_drafted" and "PRC-6401" not in json.dumps(r)
    assert all("memo_drafts" not in x for x in get(client, "/referrals")["items"])
    assert len(get(client, "/referrals/REF-6601/drafts")["items"]) == 2
    assert {k: v for k, v in store.data.items() if k != "uw_referrals"} == before


def test_a_referral_memo_is_refused_with_a_reason_and_nothing_is_saved(client):
    rule = post(client, "/referrals/REF-6601/memo", {**MEMO, "forcing_rules": ["RF-9"]}, 409)
    assert "RF-9" in rule["detail"] and "Nothing was saved" in rule["detail"]
    prec = post(client, "/referrals/REF-6601/memo", {**MEMO, "precedents": [{"precedent_id": "PRC-9999", "bearing": "agrees"}]}, 409)
    assert "PRC-9999" in prec["detail"]
    assert post(client, "/referrals/REF-6601/memo", {**MEMO, "referral_needed": "approve"}, 422)["applied"] is False
    assert ref(client, 6601)["drafts_on_file"] == 0


def test_an_empty_text_or_none_for_an_optional_fixed_choice_is_read_as_no_value(client):
    for n, word in enumerate(("", "none", "None", "not needed", "N/A", "not_applicable", "null"), start=1):
        saved = post(client, "/referrals/REF-6604/memo", {"referral_needed": "no", "refer_to_grade": word, "memo": "No referral is needed."})
        assert saved["draft"]["version"] == n and saved["draft"]["refer_to_grade"] is None, word
    assert post(client, "/referrals/REF-6604/memo", {"referral_needed": "no", "refer_to_grade": "the committee", "memo": "x"}, 422)["applied"] is False
    assert post(client, "/referrals/REF-6601/memo", {**MEMO, "refer_to_grade": "senior underwriter"})["draft"]["refer_to_grade"] == "senior_underwriter"
    assert post(client, "/referrals/REF-6601/memo", {**MEMO, "referral_needed": ""}, 422)["applied"] is False


def test_a_precedent_that_is_not_alike_is_saved_with_its_reason(client):
    rows = [{"precedent_id": "PRC-6401", "bearing": "agrees"}, {"precedent_id": "PRC-6402", "bearing": "agrees"},
            {"precedent_id": "PRC-6403", "bearing": "Not alike", "note": "A class B grain warehouse, not a class C showroom."}]
    saved = post(client, "/referrals/REF-6601/memo", {**MEMO, "precedents": rows})["draft"]
    assert [p["bearing"] for p in saved["precedents"]] == ["agrees", "agrees", "not_alike"]
    assert saved["precedents"][2]["note"].startswith("A class B grain warehouse")
    assert post(client, "/referrals/REF-6601/memo", {**MEMO, "precedents": [{"precedent_id": "PRC-6403", "bearing": "irrelevant"}]}, 422)["applied"] is False


# ---------------------------------------------------------------- renewals
def test_the_renewal_rules_say_the_order_of_the_next_step(client):
    how = get(client, "/renewal-rules")["how_to_read"]
    assert how.index("claims team first") < how.index("then a referral to the senior underwriter") < how.index("then a survey")
    for n, rules in ((6701, []), (6702, ["RN-1"]), (6703, ["RN-2"]), (6704, ["RN-1", "RN-4"]), (6705, ["RN-3"]), (6706, ["RN-5"])):
        assert rnw(client, n)["rules_that_apply"] == rules


def test_the_renewal_rules_are_five(client):
    doc = get(client, "/renewal-rules")
    assert [r["rule_id"] for r in doc["items"]] == ["RN-1", "RN-2", "RN-3", "RN-4", "RN-5"] and "70 percent" in doc["items"][0]["text"]


def test_the_renewals_due_are_listed_by_window_soonest_first(client):
    rows = get(client, "/renewals")["items"]
    assert [(r["renewal_id"], r["policy_id"], r["days_until_the_period_ends"], r["period_end"]) for r in rows] == [
        ("RNW-6701", "CPL-6801", 21, "2026-12-17"), ("RNW-6702", "CPL-6802", 28, "2026-12-24"), ("RNW-6703", "CPL-6803", 33, "2026-12-29"),
        ("RNW-6704", "POL-2007", 34, "2026-12-30"), ("RNW-6705", "CPL-6805", 40, "2027-01-05"), ("RNW-6706", "CPL-6806", 48, "2027-01-13")]
    assert all("review_drafts" not in r for r in rows)
    assert [r["renewal_id"] for r in get(client, "/renewals?within_days=30")["items"]] == ["RNW-6701", "RNW-6702"]
    assert [r["renewal_id"] for r in get(client, "/renewals?within_days=34")["items"]][-1] == "RNW-6704"


def test_rnw_6701_is_clean_and_no_rule_applies(client):
    r = rnw(client, 6701)
    t = r["expiring_terms"]
    assert (t["insured"], t["period_start"], t["period_end"], t["annual_premium"], t["total_sum_insured"], t["deductible"]) == (
        "Ivelet & Thorn Bookbinders Ltd", "2025-12-18", "2026-12-17", 6000.0, 900000.0, 2500.0)
    assert (r["totals"]["claims"], r["totals"]["paid"], r["totals"]["incurred"], r["totals"]["loss_ratio_percent"]) == (1, 900.0, 900.0, 15.0)
    assert r["rules_that_apply"] == [] and r["changes_reported"] == [] and "ready for the underwriter" in r["sentence"]
    assert r["claims_of_the_period"][0]["claim_id"] == "CCL-6901" and r["claims_of_the_period"][0]["date_of_loss"] == "2026-05-07"


def test_rnw_6702_has_a_loss_ratio_above_the_limit(client):
    r = rnw(client, 6702)
    assert [(c["claim_id"], c["date_of_loss"], c["paid"]) for c in r["claims_of_the_period"]] == [
        ("CCL-6902", "2026-03-15", 4600.0), ("CCL-6903", "2026-07-28", 3650.0)]
    assert (r["totals"]["paid"], r["totals"]["loss_ratio_percent"], r["expiring_terms"]["annual_premium"]) == (8250.0, 82.5, 10000.0)
    assert r["rules_that_apply"] == ["RN-1"] and rules_of(r)["RN-1"]["limit"] == 70.0
    assert "82.50 percent, above the limit of 70.00 percent" in rules_of(r)["RN-1"]["sentence"]


def test_rnw_6703_has_a_change_of_occupancy_and_needs_a_survey(client):
    r = rnw(client, 6703)
    assert r["rules_that_apply"] == ["RN-2"] and r["totals"]["loss_ratio_percent"] == 20.0
    change = r["changes_reported"][0]
    assert (change["reported_on"], change["kind"]) == ("2026-06-29", "occupancy") and "stores car and van tyres" in change["text"]
    assert "29 Jun 2026: a survey is needed" in rules_of(r)["RN-2"]["sentence"]


def test_rnw_6704_reads_the_policy_and_the_open_claim_from_their_own_systems(client):
    r = rnw(client, 6704)
    t = r["expiring_terms"]
    assert (t["policy_id"], t["policy_held_in"], t["insured"], t["annual_premium"], t["total_sum_insured"], t["deductible"]) == (
        "POL-2007", "the policy system", "Aldous Pennicott", 1240.0, 270000.0, 250.0)
    assert (t["period_start"], t["period_end"]) == ("2025-12-31", "2026-12-30")
    claim = r["claims_of_the_period"][0]
    assert (claim["claim_id"], claim["date_of_loss"], claim["status"], claim["paid"], claim["outstanding_reserve"], claim["held_in"]) == (
        "CLM-4007", "2026-11-23", "open", 0.0, 62000.0, "the claims system")
    assert (r["totals"]["loss_ratio_on_payments_percent"], r["totals"]["loss_ratio_percent"], r["totals"]["open_claims"]) == (0.0, 5000.0, 1)
    assert r["rules_that_apply"] == ["RN-1", "RN-4"]
    assert "USD 62,000.00 is reserve and USD 0.00 is paid" in rules_of(r)["RN-4"]["sentence"]
    assert "5,000.00 percent" in rules_of(r)["RN-1"]["sentence"]


def test_rnw_6704_follows_the_claims_system_and_writes_nothing_to_it(client, store):
    client.post("/claims/claims/CLM-4007/decision", headers=H, json={"decision": "declined", "decided_by": "Fenella Arkwright",
                                                                    "reason": "Test.", "clause": "2.4"})
    r = rnw(client, 6704)
    assert (r["claims_of_the_period"][0]["status"], r["totals"]["loss_ratio_percent"], r["rules_that_apply"]) == ("declined", 0.0, [])
    client.post("/admin/reset/claims", headers=H)
    before = copy.deepcopy((store.data["policies"], store.data["claims"]))
    post(client, "/renewals/RNW-6704/review", {**REVIEW, "rules_that_apply": ["RN-1", "RN-4"]})
    assert (store.data["policies"], store.data["claims"]) == before


def test_rnw_6705_has_no_claims_and_a_change_in_protections(client):
    r = rnw(client, 6705)
    assert r["claims_of_the_period"] == [] and r["totals"]["loss_ratio_percent"] == 0.0 and "No claim is recorded" in r["claims_note"]
    assert r["rules_that_apply"] == ["RN-3"]
    change = r["changes_reported"][0]
    assert (change["reported_on"], change["kind"]) == ("2026-10-12", "protections") and "out of service since 5 Oct 2026" in change["text"]
    assert (r["expiring_terms"]["construction_class"], r["expiring_terms"]["total_sum_insured"], r["expiring_terms"]["sprinklers"]) == ("B", 1900000.0, "yes")


def test_rnw_6706_the_two_records_disagree_on_a_date_and_both_ratios_are_given(client):
    r = rnw(client, 6706)
    assert [(c["claim_id"], c["date_of_loss"], c["paid"], c["date_of_loss_is_inside_the_period"]) for c in r["claims_of_the_period"]] == [
        ("CCL-6905", "2026-07-29", 3875.0, True), ("CCL-6906", "2026-01-05", 5625.0, False)]
    assert r["expiring_terms"]["period_start"] == "2026-01-14" and r["expiring_terms"]["annual_premium"] == 12500.0
    assert (r["totals"]["incurred"], r["totals"]["loss_ratio_percent"]) == (9500.0, 76.0)
    assert (r["totals_leaving_out_the_disputed_claims"]["incurred"], r["totals_leaving_out_the_disputed_claims"]["loss_ratio_percent"]) == (3875.0, 31.0)
    assert r["rules_that_apply"] == ["RN-5"] and r["rules_that_depend_on_the_disagreement"] == ["RN-1"]
    assert rules_of(r)["RN-1"]["applies"] == "depends_on_the_disagreement"
    d = r["record_disagreements"][0]
    assert d["claim_id"] == "CCL-6906" and "5 Jan 2026, 9 days before the period started on 14 Jan 2026" in d["sentence"]


def test_a_renewal_review_is_a_versioned_draft_and_not_part_of_the_renewal(client, store):
    before = copy.deepcopy({k: v for k, v in store.data.items() if k != "uw_renewals"})
    one = post(client, "/renewals/RNW-6702/review", {**REVIEW, "next_step": "Refer to the senior underwriter", "rules_that_apply": ["rn-1"]})
    two = post(client, "/renewals/RNW-6702/review", REVIEW)
    assert (one["draft"]["version"], two["draft"]["version"], one["draft"]["next_step"], one["draft"]["rules_that_apply"]) == (
        1, 2, "refer_to_the_senior_underwriter", ["RN-1"])
    figures = one["draft"]["figures_worked_out_by_the_system"]
    assert (figures["paid"], figures["loss_ratio_percent"], figures["rules_that_apply"]) == (8250.0, 82.5, ["RN-1"])
    r = rnw(client, 6702)
    assert "review_drafts" not in r and r["drafts_on_file"] == 2 and r["status"] == "review_due"
    assert "refer_to_the_senior_underwriter" not in json.dumps(r)
    assert len(get(client, "/renewals/RNW-6702/drafts")["items"]) == 2
    assert {k: v for k, v in store.data.items() if k != "uw_renewals"} == before


def test_a_renewal_review_is_refused_with_a_reason_and_nothing_is_saved(client):
    rule = post(client, "/renewals/RNW-6702/review", {**REVIEW, "rules_that_apply": ["RN-9"]}, 409)
    assert "RN-9" in rule["detail"] and "Nothing was saved" in rule["detail"]
    ready = post(client, "/renewals/RNW-6702/review", {**REVIEW, "next_step": "ready_for_the_underwriter"}, 409)
    assert "no rule applies" in ready["detail"]
    assert post(client, "/renewals/RNW-6702/review", {**REVIEW, "next_step": "renew"}, 422)["applied"] is False
    assert rnw(client, 6702)["drafts_on_file"] == 0
    assert post(client, "/renewals/RNW-6701/review", {"next_step": "ready for the underwriter", "summary": "Clean."})["draft"]["version"] == 1


# ---------------------------------------------------------------- unknown ids, reset and counts
def test_an_unknown_underwriting_id_is_a_plain_404(client):
    for path, words in (("/submissions/SBM-9999", "No submission with id SBM-9999"), ("/referrals/REF-9999", "No referral with id REF-9999"),
                        ("/renewals/RNW-9999", "No renewal with id RNW-9999"), ("/renewals/POL-2007", "No renewal with id POL-2007"),
                        ("/submissions/SBM-9999/measure", "No submission"), ("/referrals/REF-9999/authority", "No referral")):
        r = client.get(f"/underwriting{path}", headers=H)
        assert r.status_code == 404 and words in r.json()["detail"] and r.json()["applied"] is False
    assert client.post("/underwriting/renewals/RNW-9999/review", headers=H, json=REVIEW).status_code == 404


def test_putting_the_underwriting_system_back_leaves_the_claims_system_alone_and_the_other_way_round(client, store):
    triage = {"rule_id": "HG-3", "track": "fast track", "team": "fast-track team", "severity": "low", "reason": "Estimate under 2,500."}
    client.post("/claims/claims/CLM-4001/triage", headers=H, json=triage)
    post(client, "/submissions/SBM-6501/file", FILE)
    post(client, "/referrals/REF-6601/memo", MEMO)
    post(client, "/renewals/RNW-6702/review", REVIEW)
    changed = client.get("/admin/state", headers=H).json()["changed_by"]
    assert changed["claims"] == ["claims"] and changed["underwriting"] == ["uw_referrals", "uw_renewals", "uw_submissions"]
    fresh = build_all(TODAY_D)
    assert client.post("/admin/reset/claims", headers=H).json()["put_back"] == ["claims"]
    assert len(store.data["uw_submissions"]["SBM-6501"]["file_drafts"]) == 1
    client.post("/claims/claims/CLM-4001/triage", headers=H, json=triage)
    back = client.post("/admin/reset/underwriting", headers=H).json()
    assert back["put_back"] == ["uw_referrals", "uw_renewals", "uw_submissions"]
    assert all(store.data[name] == fresh[name] for name in UW_SETS)
    assert len(store.data["claims"]["CLM-4001"]["triage_drafts"]) == 1
    client.post("/admin/reset", headers=H)
    assert store.data == fresh


def test_the_counts_name_the_open_items_of_the_underwriting_system(client):
    counts = client.get("/admin/state", headers=H).json()["counts"]
    assert (counts["underwriting_submissions_received"], counts["underwriting_referrals_to_draft"], counts["renewals_due_for_review"]) == (8, 5, 6)
