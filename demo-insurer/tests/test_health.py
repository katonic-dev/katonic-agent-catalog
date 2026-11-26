"""The health system: the right answers of the Health section of SCENARIOS.md, every refusal, and the rules drafts and changes keep.

Checked against the data the service gives at the insurer date 2026-11-26."""
import json
import re
from datetime import date

from insurer.seed import build_all
from insurer.seed_health import build_health
from conftest import H, TODAY

TODAY_D = date.fromisoformat(TODAY)
HEALTH_SETS = sorted(build_health(TODAY_D))


def get(client, path):
    r = client.get(f"/health{path}", headers=H)
    assert r.status_code == 200, (path, r.status_code, r.text[:300])
    return r.json()


def post(client, path, body=None, status=200):
    r = client.post(f"/health{path}", json=body or {}, headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:400])
    return r.json()


def benefits(client, scheme_id):
    return {b["benefit"]: b for b in get(client, f"/schemes/{scheme_id}")["benefits"]}


def member_benefits(client, member_id):
    return {b["benefit"]: b for b in get(client, f"/members/{member_id}")["benefits"]}


def pa(client, n):
    return get(client, f"/pre-authorisations/PA-{n}")


def claim(client, n):
    return get(client, f"/medical-claims/MC-{n}")


def invoice(client, n):
    return get(client, f"/invoices/PI-{n}")


MET = [{"criterion": n, "finding": "met", "evidence": "The notes say so (PA-8101-D2)."} for n in ("1", "2", "3")]
ASSESSMENT = {"cover_in_force_on_planned_date": "yes", "plan_position": "needs_pre_authorisation", "criteria": MET,
              "proposal": "send_to_the_assessor_as_met", "reason": "Every criterion of MP-301 is met."}
TO_THE_ASSESSOR = {"cover_in_force_on_planned_date": "yes", "plan_position": "not_covered_by_the_plan", "proposal": "refer_to_the_assessor",
                   "reason": "The plan does not cover the procedure."}


# ---------------------------------------------------------------- the service as a whole
def test_the_health_system_has_26_operations_and_none_writes_without_saying_so(client):
    doc = client.get("/health/openapi.json").json()
    ops = [(method, op) for item in doc["paths"].values() for method, op in item.items()]
    assert len(ops) == 26
    for method, op in ops:
        if method != "get":
            assert op["summary"].endswith("(draft)") or op["summary"].endswith("(change)"), op["operationId"]
    changes = sorted(op["operationId"] for _, op in ops if op["summary"].endswith("(change)"))
    assert changes == ["decide_medical_claim", "decide_pre_authorisation", "record_invoice_query"]


def test_the_health_check_still_answers_beside_the_health_system(client):
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/health/openapi.json").status_code == 200 and "health/openapi.json" in client.get("/").text
    assert client.get("/health/members").status_code == 401


def test_health_ids_do_not_collide_with_the_other_systems():
    data = build_all(TODAY_D)
    seen = {}
    for name, records in data.items():
        if isinstance(records, dict):
            for key in records:
                assert key not in seen, (key, name, seen.get(key))
                seen[key] = name
    prefixes = {"health_schemes": "GRP-61", "health_members": "MEM-72", "medical_policies": "MP-3", "pre_authorisations": "PA-81",
                "medical_claims": "MC-9", "health_providers": "PRV-51", "provider_invoices": "PI-95"}
    for name, prefix in prefixes.items():
        assert all(key.startswith(prefix) for key in data[name]), name


def test_no_document_of_the_health_system_holds_a_bare_date_or_counts_days():
    data = build_health(TODAY_D)
    texts = [doc["text"] for name in ("pre_authorisations", "medical_claims") for rec in data[name].values() for doc in rec["documents"]]
    assert len(texts) == 15
    for text in texts:
        assert not re.search(r"\b20\d\d-\d\d-\d\d\b", text), text
    blob = json.dumps(data).lower()
    for word in ("yesterday", "last week", "days ago", "weeks ago", "last month", "this morning", "tomorrow", "monday", "tuesday",
                 "wednesday", "thursday", "friday", "saturday", "sunday"):
        assert word not in blob, word


def test_everything_in_the_health_data_is_the_insurers_own(client):
    blob = json.dumps(build_health(TODAY_D))
    assert set(re.findall(r"TMI-T-\d{4}", blob)) >= {"TMI-T-1010", "TMI-T-8050"}
    for word in ("CPT", "ICD", "HCPCS", "SNOMED"):
        assert word not in blob, word


# ---------------------------------------------------------------- schemes and their tables of benefits
def test_the_list_of_schemes_gives_no_table_of_benefits(client):
    rows = get(client, "/schemes")["items"]
    assert [(r["scheme_id"], r["plan_name"]) for r in rows] == [("GRP-6101", "Thornmere Health Complete"),
                                                               ("GRP-6102", "Thornmere Health Essential")]
    assert all("benefits" not in r and "exclusions" not in r for r in rows)
    assert (rows[0]["period_start"], rows[0]["period_end"], rows[1]["period_start"], rows[1]["period_end"]) == (
        "2026-03-31", "2027-03-30", "2026-06-29", "2027-06-28")


def test_each_scheme_has_its_own_table_with_its_own_ids(client):
    full, basic = get(client, "/schemes/GRP-6101"), get(client, "/schemes/GRP-6102")
    assert [b["benefit_id"] for b in full["benefits"]] == [f"BEN-F{n:02d}" for n in range(1, 11)]
    assert [b["benefit_id"] for b in basic["benefits"]] == [f"BEN-E{n:02d}" for n in range(1, 11)]
    assert [e["exclusion_id"] for e in full["exclusions"]] == ["EXC-F1", "EXC-F2", "EXC-F3", "EXC-F4"]
    assert [e["exclusion_id"] for e in basic["exclusions"]] == ["EXC-E1", "EXC-E2", "EXC-E3", "EXC-E4"]
    assert "BEN-E" not in json.dumps(full) and "BEN-F" not in json.dumps(basic)
    for b in full["benefits"] + basic["benefits"]:
        assert b["state"] in ("covered", "covered_with_conditions", "not_covered") and b["limit_sentence"] and b["member_share_sentence"]


def test_the_two_plans_give_different_answers_to_the_same_question(client):
    full, basic = benefits(client, "GRP-6101"), benefits(client, "GRP-6102")
    assert (full["physiotherapy"]["limit"]["sessions"], basic["physiotherapy"]["limit"]["sessions"]) == (12, 6)
    assert (full["maternity"]["state"], basic["maternity"]["state"]) == ("covered_with_conditions", "not_covered")
    assert full["maternity"]["limit_sentence"] == "Up to USD 6,000.00 for each pregnancy." and full["maternity"]["waiting_period_days"] == 300
    assert (full["dental"]["state"], basic["dental"]["state"]) == ("covered_with_conditions", "not_covered")
    assert full["dental"]["member_share_sentence"] == "The member pays 20 percent, up to USD 100.00 in a benefit year."
    assert full["medicines"]["member_share"] == {"percent": 10, "cap_per_year": 150.0}
    assert basic["medicines"]["member_share"] == {"percent": 20, "cap_per_year": 300.0}
    assert (full["medicines"]["limit"]["amount"], basic["medicines"]["limit"]["amount"]) == (2000.0, 800.0)
    assert (full["mri"]["pre_authorisation_needed"], basic["mri"]["pre_authorisation_needed"]) == (False, True)
    assert (full["consultation"]["limit"]["amount"], basic["consultation"]["limit"]["amount"]) == (150.0, 80.0)
    assert basic["dental"]["limit"] is None and basic["dental"]["pre_authorisation_needed"] is None


def test_both_tables_are_silent_on_hearing_aids_and_travel_vaccinations(client):
    for scheme_id in ("GRP-6101", "GRP-6102"):
        s = get(client, f"/schemes/{scheme_id}")
        text = json.dumps([s["benefits"], s["exclusions"]]).lower()
        for word in ("hearing", "vaccin", "travel"):
            assert word not in text, (scheme_id, word)
        assert "a person at the insurer answers" in s["how_to_read"]


# ---------------------------------------------------------------- members
def test_the_eight_members(client):
    rows = {m["member_id"]: m for m in get(client, "/members")["items"]}
    assert list(rows) == [f"MEM-72{n:02d}" for n in range(1, 9)]
    assert [m["scheme_id"] for m in rows.values()] == ["GRP-6101"] * 4 + ["GRP-6102"] * 4
    assert (rows["MEM-7203"]["relationship"], rows["MEM-7203"]["dependant_of"]) == ("dependant", "MEM-7202")
    assert (rows["MEM-7204"]["cover_start"], rows["MEM-7206"]["cover_end"]) == ("2026-10-17", "2026-10-27")
    assert [m["member_id"] for m in rows.values() if not m["cover_on_read_date"]["in_force"]] == ["MEM-7206"]
    assert get(client, "/members/MEM-7202")["dependants"] == ["MEM-7203"]
    assert [get(client, f"/members/MEM-72{n:02d}")["age_on_read_date"] for n in range(1, 9)] == [47, 45, 42, 33, 51, 38, 56, 36]


def test_a_search_matches_any_word_and_lists_everyone_with_no_text(client):
    assert [m["member_id"] for m in get(client, "/members?text=Tobias Wrenfeild")["items"]] == ["MEM-7207"]
    assert [m["member_id"] for m in get(client, "/members?text=Thorneloe")["items"]] == ["MEM-7202", "MEM-7203"]
    assert get(client, "/members?text=Brindlemoor")["count"] == 4 and get(client, "/members")["count"] == 8
    assert get(client, "/members?text=Zebedee")["count"] == 0


def test_cover_on_a_date_is_the_systems_answer_with_the_days(client):
    out = get(client, "/members/MEM-7206/cover?on=2026-11-14")
    assert out["in_force"] is False
    assert out["reason"] == "The member's cover ended on 27 Oct 2026: The member left the employer. 14 Nov 2026 is 18 days after the end."
    assert get(client, "/members/MEM-7206/cover?on=2026-10-27")["in_force"] is True
    early = get(client, "/members/MEM-7204/cover?on=2026-10-10")
    assert early["in_force"] is False and "started on 17 Oct 2026" in early["reason"] and "7 days before the start" in early["reason"]
    assert get(client, "/members/MEM-7204/cover?on=2026-11-26")["in_force"] is True
    assert client.get("/health/members/MEM-7204/cover?on=26-11-2026", headers=H).status_code == 422


def test_what_a_member_has_used_and_has_left_is_worked_out(client):
    rosalind, barnaby, tobias = (member_benefits(client, m) for m in ("MEM-7201", "MEM-7205", "MEM-7207"))
    assert (rosalind["physiotherapy"]["used"], rosalind["physiotherapy"]["remaining"]) == ({"sessions": 12}, {"sessions": 0})
    assert rosalind["physiotherapy"]["usage_sentence"] == "12 of 12 sessions used this benefit year. No session remains."
    assert rosalind["physiotherapy"]["benefit_id"] == "BEN-F07"
    assert (barnaby["physiotherapy"]["used"], barnaby["physiotherapy"]["remaining"]) == ({"sessions": 3}, {"sessions": 3})
    assert barnaby["physiotherapy"]["benefit_id"] == "BEN-E07"
    assert (tobias["medicines"]["used"], tobias["medicines"]["remaining"]) == ({"amount": 730.0}, {"amount": 70.0})
    assert (tobias["medicines"]["member_share_paid_this_benefit_year"], tobias["medicines"]["member_share_left_before_the_cap"]) == (146.0, 154.0)
    assert tobias["medicines"]["usage_sentence"] == ("USD 730.00 used of USD 800.00 this benefit year. USD 70.00 remains. The member has "
                                                    "paid USD 146.00 of the share cap of USD 300.00; USD 154.00 is left before the cap.")
    assert (rosalind["medicines"]["remaining"], rosalind["consultation"]["remaining"]) == ({"amount": 1820.0}, None)
    assert barnaby["dental"]["usage_sentence"] == "This plan does not cover it."


def test_the_waiting_period_for_maternity_care_of_the_member_who_joined_recently(client):
    wait = member_benefits(client, "MEM-7204")["maternity"]["waiting_period"]
    assert (wait["can_be_used_from"], wait["over"], wait["days"]) == ("2027-08-13", False, 300)
    assert wait["sentence"] == ("The member's cover started on 17 Oct 2026. This benefit can be used from 13 Aug 2027, after 300 days "
                                "of cover. 26 Nov 2026 is before that date.")
    assert member_benefits(client, "MEM-7201")["maternity"]["waiting_period"]["can_be_used_from"] == "2027-01-25"
    assert "waiting_period" not in member_benefits(client, "MEM-7204")["medicines"]
    assert "waiting_period" not in member_benefits(client, "MEM-7208")["maternity"]  # not covered on the basic plan


def test_what_the_plan_pays_on_a_bill_for_medicines_differs_by_member(client):
    t = get(client, "/members/MEM-7207/benefits/BEN-E06/estimate?amount=100")
    assert (t["within_the_limit"], t["over_the_limit"], t["member_share"], t["plan_pays"], t["member_pays"]) == (70.0, 30.0, 14.0, 56.0, 44.0)
    assert t["saved"] is False and t["note"] == (
        "USD 70.00 is within the limit of USD 800.00 a benefit year (USD 730.00 already used, USD 70.00 left). USD 30.00 is over the "
        "limit. The member's share is 20 percent of USD 70.00 = USD 14.00. The plan pays USD 56.00.")
    r = get(client, "/members/MEM-7201/benefits/BEN-F06/estimate?amount=100")
    assert (r["within_the_limit"], r["over_the_limit"], r["member_share"], r["plan_pays"], r["member_pays"]) == (100.0, 0.0, 10.0, 90.0, 10.0)


def test_other_estimates_sessions_a_limit_for_each_visit_and_a_benefit_not_covered(client):
    s = get(client, "/members/MEM-7205/benefits/BEN-E07/estimate?amount=168&visits_or_sessions=4")
    assert (s["sessions_within_the_plan"], s["sessions_beyond_the_plan"], s["within_the_limit"], s["over_the_limit"]) == (3, 1, 126.0, 42.0)
    assert (s["member_share"], s["plan_pays"], s["member_pays"]) == (25.2, 100.8, 67.2)
    v = get(client, "/members/MEM-7208/benefits/BEN-E03/estimate?amount=100")
    assert (v["within_the_limit"], v["over_the_limit"], v["member_share"], v["plan_pays"], v["member_pays"]) == (80.0, 20.0, 16.0, 64.0, 36.0)
    n = get(client, "/members/MEM-7208/benefits/BEN-E09/estimate?amount=380")
    assert (n["plan_pays"], n["member_pays"], n["state"]) == (0.0, 380.0, "not_covered")
    d = get(client, "/members/MEM-7201/benefits/BEN-F09/estimate?amount=380")
    assert (d["member_share"], d["plan_pays"]) == (76.0, 304.0)
    capped = get(client, "/members/MEM-7201/benefits/BEN-F06/estimate?amount=1500")
    assert (capped["member_share"], capped["plan_pays"]) == (132.0, 1368.0)
    assert "= USD 150.00, held to USD 132.00 by the share cap of USD 150.00 a benefit year." in capped["note"]


def test_an_estimate_works_out_nothing_when_cover_is_not_in_force(client):
    e = get(client, "/members/MEM-7206/benefits/BEN-E03/estimate?amount=100")
    assert (e["within_the_limit"], e["over_the_limit"], e["member_share"], e["plan_pays"], e["member_pays"]) == (0.0, 0.0, 0.0, 0.0, 100.0)
    assert e["cover_on_read_date"]["in_force"] is False and e["saved"] is False and e["benefit_id"] == "BEN-E03"
    assert e["note"] == ("The member's cover is not in force. The member's cover ended on 27 Oct 2026: The member left the employer. "
                         "26 Nov 2026 is 30 days after the end. Nothing is worked out against the plan: the plan pays USD 0.00 and "
                         "the member pays the whole USD 100.00.")
    m = get(client, "/members/MEM-7206/benefits/BEN-E06/estimate?amount=50")
    assert (m["plan_pays"], m["member_pays"]) == (0.0, 50.0)
    assert set(e) == set(get(client, "/members/MEM-7207/benefits/BEN-E06/estimate?amount=100"))  # the same fields


def test_an_estimate_works_out_nothing_while_a_waiting_period_runs(client):
    e = get(client, "/members/MEM-7204/benefits/BEN-F08/estimate?amount=1000")
    assert (e["within_the_limit"], e["over_the_limit"], e["member_share"], e["plan_pays"], e["member_pays"]) == (0.0, 0.0, 0.0, 0.0, 1000.0)
    assert e["waiting_period"]["over"] is False and e["cover_on_read_date"]["in_force"] is True
    assert e["note"] == ("The member cannot use this benefit yet. The member's cover started on 17 Oct 2026. This benefit can be used "
                         "from 13 Aug 2027, after 300 days of cover. 26 Nov 2026 is before that date. Nothing is worked out against "
                         "the plan: the plan pays USD 0.00 and the member pays the whole USD 1,000.00.")
    # the same member's other benefits are worked out as before
    assert get(client, "/members/MEM-7204/benefits/BEN-F06/estimate?amount=100")["plan_pays"] == 90.0


def test_an_estimate_refuses_another_schemes_benefit_and_an_amount_that_is_missing(client):
    r = client.get("/health/members/MEM-7207/benefits/BEN-F06/estimate?amount=100", headers=H)
    assert r.status_code == 409 and r.json()["applied"] is False
    assert "BEN-F06 is not a benefit of GRP-6102, the scheme of MEM-7207" in r.json()["detail"] and "Nothing was worked out" in r.json()["detail"]
    assert client.get("/health/members/MEM-7207/benefits/BEN-E06/estimate", headers=H).status_code == 422
    assert client.get("/health/members/MEM-7207/benefits/BEN-E06/estimate?amount=0", headers=H).status_code == 422


def test_an_estimate_changes_nothing(client, store):
    get(client, "/members/MEM-7207/benefits/BEN-E06/estimate?amount=100")
    assert store.data == build_all(TODAY_D)


# ---------------------------------------------------------------- medical policies
def test_the_three_medical_policies(client):
    rows = {p["medical_policy_id"]: p for p in get(client, "/medical-policies")["items"]}
    assert list(rows) == ["MP-301", "MP-302", "MP-303"]
    assert [p["procedure_code"] for p in rows.values()] == ["TMI-T-3010", "TMI-T-4020", "TMI-T-5030"]
    assert all([c["number"] for c in p["criteria"]] == ["1", "2", "3"] for p in rows.values())
    assert "at least 6 weeks" in rows["MP-301"]["criteria"][0]["text"] and "at least 4 weeks" in rows["MP-301"]["criteria"][1]["text"]
    assert "no more than 6" in rows["MP-302"]["criteria"][2]["text"] and "at least 6 weeks" in rows["MP-303"]["criteria"][1]["text"]
    assert "neither met nor failed" in rows["MP-301"]["how_to_read"]


# ---------------------------------------------------------------- pre-authorisation requests: the six right answers
def test_the_six_requests_and_their_dates(client):
    rows = get(client, "/pre-authorisations")["items"]
    assert [(r["pre_authorisation_id"], r["member_id"], r["provider_id"], r["procedure_code"], r["date_requested"], r["planned_date"])
            for r in rows] == [
        ("PA-8101", "MEM-7205", "PRV-5101", "TMI-T-3010", "2026-11-24", "2026-12-03"),
        ("PA-8102", "MEM-7202", "PRV-5101", "TMI-T-5030", "2026-11-23", "2026-12-08"),
        ("PA-8103", "MEM-7207", "PRV-5102", "TMI-T-3010", "2026-11-25", "2026-12-05"),
        ("PA-8104", "MEM-7206", "PRV-5101", "TMI-T-5030", "2026-11-23", "2026-12-06"),
        ("PA-8105", "MEM-7208", "PRV-5102", "TMI-T-6040", "2026-11-24", "2026-12-10"),
        ("PA-8106", "MEM-7204", "PRV-5101", "TMI-T-3010", "2026-11-25", "2026-12-02")]
    assert all(r["status"] == "received" and r["decision"] is None and "assessment_drafts" not in r for r in rows)
    assert all([d["document_id"] for d in r["documents"]] == [f"{r['pre_authorisation_id']}-D1", f"{r['pre_authorisation_id']}-D2"] for r in rows)


def test_pa_8101_meets_every_criterion_of_mp_301(client):
    r = pa(client, 8101)
    assert r["cover_on_planned_date"]["in_force"] is True
    assert r["plan_position"] == {"position": "needs_pre_authorisation", "pre_authorisation_needed": True,
                                  "sentence": "Thornmere Health Essential needs pre-authorisation for BEN-E05 MRI scans."}
    assert r["medical_policy"]["medical_policy_id"] == "MP-301" and r["plan_benefit"]["benefit_id"] == "BEN-E05"
    assert r["plan_benefit"]["remaining"] == {"amount": 1500.0}
    notes = r["documents"][1]["text"]
    assert "Lower back pain for 9 weeks" in notes and "physiotherapy for 5 weeks" in notes and "left ankle reflex reduced" in notes


def test_pa_8102_plainly_fails_the_second_criterion_of_mp_303(client):
    r = pa(client, 8102)
    assert r["medical_policy"]["medical_policy_id"] == "MP-303" and r["plan_position"]["position"] == "needs_pre_authorisation"
    assert r["plan_benefit"]["benefit_id"] == "BEN-F02" and r["cover_on_planned_date"]["in_force"] is True
    notes = r["documents"][1]["text"]
    assert "for 4 months" in notes and "physiotherapy for 2 weeks" in notes and "MRI report of 16 Nov 2026: tear of the medial meniscus" in notes


def test_pa_8103_says_nothing_about_the_examination(client):
    r = pa(client, 8103)
    assert r["medical_policy"]["medical_policy_id"] == "MP-301" and r["cover_on_planned_date"]["in_force"] is True
    notes = r["documents"][1]["text"].lower()
    assert "pain for 8 weeks" in notes and "pain relief for 6 weeks" in notes
    for word in ("examination", "reflex", "numb", "weakness"):
        assert word not in notes, word


def test_pa_8104_is_for_a_member_whose_cover_ended(client):
    r = pa(client, 8104)
    assert r["cover_on_planned_date"]["in_force"] is False
    assert r["cover_on_planned_date"]["reason"] == ("The member's cover ended on 27 Oct 2026: The member left the employer. "
                                                   "6 Dec 2026 is 40 days after the end.")
    assert r["medical_policy"] is None
    assert r["medical_policy_note"] == "No medical policy is read: the member's cover is not in force on the planned date."


def test_pa_8105_is_for_a_procedure_the_plan_does_not_cover(client):
    r = pa(client, 8105)
    assert r["plan_position"] == {"position": "not_covered_by_the_plan", "pre_authorisation_needed": None,
                                  "sentence": "BEN-E09 Dental treatment is not covered by Thornmere Health Essential, so there is "
                                              "nothing to pre-authorise."}
    assert r["medical_policy"] is None and r["medical_policy_note"] == "No medical policy is read: the plan does not cover the procedure."
    assert r["cover_on_planned_date"]["in_force"] is True


def test_pa_8106_needs_no_pre_authorisation_on_the_fuller_plan(client):
    r = pa(client, 8106)
    assert r["plan_position"] == {"position": "no_pre_authorisation_needed", "pre_authorisation_needed": False,
                                  "sentence": "Thornmere Health Complete needs no pre-authorisation for BEN-F05 MRI scans."}
    assert r["medical_policy"] is None
    assert r["medical_policy_note"] == "No medical policy is read: the plan needs no pre-authorisation for the procedure."
    assert r["cover_on_planned_date"]["in_force"] is True and r["member"]["cover_start"] == "2026-10-17"


# ---------------------------------------------------------------- pre-authorisation requests: drafts and the change
def test_an_assessment_is_a_draft_keeps_every_version_and_decides_nothing(client, store):
    assert post(client, "/pre-authorisations/PA-8101/assessment", ASSESSMENT)["draft"]["version"] == 1
    second = post(client, "/pre-authorisations/PA-8101/assessment", {**ASSESSMENT, "drafted_by": "Pre-authorisation agent"})
    assert second["kind"] == "draft" and second["draft"]["version"] == 2 and second["draft"]["drafted_by"] == "Pre-authorisation agent"
    stored = store.data["pre_authorisations"]["PA-8101"]
    assert stored["status"] == "received" and stored["decision"] is None
    r = pa(client, 8101)
    assert "assessment_drafts" not in r and r["drafts_on_file"] == 2 and "send_to_the_assessor_as_met" not in json.dumps(r)
    assert all("assessment_drafts" not in x for x in get(client, "/pre-authorisations")["items"])
    drafts = get(client, "/pre-authorisations/PA-8101/drafts")
    assert drafts["count"] == 2 and drafts["items"][0]["proposal"] == "send_to_the_assessor_as_met"
    assert [c["finding"] for c in drafts["items"][0]["criteria"]] == ["met", "met", "met"]


def test_the_right_assessments_of_the_other_five_requests_can_be_saved(client):
    refer = {**ASSESSMENT, "proposal": "refer_to_the_medical_reviewer", "reason": "Criterion 2 is not met.",
             "criteria": [MET[0], {"criterion": "2", "finding": "not_met", "evidence": "Physiotherapy for 2 weeks (PA-8102-D2)."}, MET[2]]}
    assert post(client, "/pre-authorisations/PA-8102/assessment", refer)["applied"] is True
    ask = {**ASSESSMENT, "proposal": "ask_the_provider", "reason": "The notes say nothing about the examination.",
           "question_for_the_provider": "What did the examination find?",
           "criteria": [MET[0], MET[1], {"criterion": "3", "finding": "not_stated", "evidence": "No examination in PA-8103-D2."}]}
    assert post(client, "/pre-authorisations/PA-8103/assessment", ask)["applied"] is True
    out = {**TO_THE_ASSESSOR, "cover_in_force_on_planned_date": "no", "plan_position": "needs_pre_authorisation"}
    assert post(client, "/pre-authorisations/PA-8104/assessment", out)["applied"] is True
    assert post(client, "/pre-authorisations/PA-8105/assessment", TO_THE_ASSESSOR)["applied"] is True
    assert post(client, "/pre-authorisations/PA-8106/assessment", {**TO_THE_ASSESSOR, "plan_position": "no_pre_authorisation_needed"})["applied"]


def test_an_assessment_is_refused_with_a_plain_sentence_and_nothing_saved(client, store):
    def refused(n, body, words):
        r = post(client, f"/pre-authorisations/PA-{n}/assessment", body, 409)
        assert words in r["detail"] and "Nothing was saved" in r["detail"] and r["applied"] is False
        assert store.data["pre_authorisations"][f"PA-{n}"]["assessment_drafts"] == []

    refused(8101, {**ASSESSMENT, "criteria": MET + [{"criterion": "4", "finding": "met"}]}, "MP-301 has the criteria 1, 2, 3")
    refused(8101, {**ASSESSMENT, "criteria": MET[:2]}, "only with one row for every criterion")
    refused(8103, {**ASSESSMENT, "criteria": MET[:2] + [{"criterion": "3", "finding": "not_stated"}]}, "each with the finding met")
    refused(8103, {**ASSESSMENT, "proposal": "ask_the_provider"}, "needs the question for the provider")
    refused(8105, {**TO_THE_ASSESSOR, "criteria": MET}, "No medical policy is to be read for PA-8105")
    refused(8106, {**ASSESSMENT, "plan_position": "no_pre_authorisation_needed"}, "No medical policy is to be read for PA-8106")
    refused(8106, {**ASSESSMENT, "plan_position": "no_pre_authorisation_needed", "criteria": []}, "only with one row for every criterion")
    bad = client.post("/health/pre-authorisations/PA-8101/assessment", headers=H, json={**ASSESSMENT, "proposal": "decline"})
    assert bad.status_code == 422 and bad.json()["applied"] is False


def test_a_decision_on_a_request_needs_the_right_person_and_happens_once(client, store):
    def refused(n, body, words):
        r = post(client, f"/pre-authorisations/PA-{n}/decision", body, 409)
        assert words in r["detail"] and "Nothing was changed" in r["detail"]
        assert store.data["pre_authorisations"][f"PA-{n}"]["status"] == "received"

    assessor = {"decision": "approved", "decided_by": "Ottilie Marsh", "role": "authorised_assessor", "reason": "Every criterion is met."}
    refused(8102, {**assessor, "decision": "declined"}, "Only the medical reviewer declines")
    refused(8104, assessor, "PA-8104 cannot be approved: The member's cover ended on 27 Oct 2026")
    assert client.post("/health/pre-authorisations/PA-8101/decision", headers=H, json={"decision": "approved"}).status_code == 422
    done = post(client, "/pre-authorisations/PA-8101/decision", assessor)
    assert done["kind"] == "change" and done["decision"]["decided_on"] == TODAY and pa(client, 8101)["status"] == "approved"
    again = post(client, "/pre-authorisations/PA-8101/decision", assessor, 409)
    assert "already recorded on PA-8101, by Ottilie Marsh on 26 Nov 2026" in again["detail"]
    reviewer = {"decision": "declined", "decided_by": "Dr Linnea Ashcombe", "role": "medical_reviewer", "reason": "Criterion 2 is not met."}
    assert post(client, "/pre-authorisations/PA-8102/decision", reviewer)["decision"]["role"] == "medical_reviewer"
    assert [r["pre_authorisation_id"] for r in get(client, "/pre-authorisations?status=received")["items"]] == [
        "PA-8103", "PA-8104", "PA-8105", "PA-8106"]


# ---------------------------------------------------------------- medical claims: the six right answers
def test_the_held_claims_and_the_earlier_paid_ones(client):
    held = get(client, "/medical-claims?status=held")["items"]
    assert [(c["claim_id"], c["member_id"], c["provider_id"], c["hold_reason"], c["amount_claimed"]) for c in held] == [
        ("MC-9101", "MEM-7201", "PRV-5102", "duplicate", 55.0), ("MC-9102", "MEM-7205", "PRV-5102", "duplicate", 42.0),
        ("MC-9103", "MEM-7206", "PRV-5101", "eligibility", 60.0), ("MC-9104", "MEM-7207", "PRV-5101", "limit", 113.4),
        ("MC-9105", "MEM-7203", "PRV-5101", "medical_necessity", 620.0), ("MC-9106", "MEM-7201", "PRV-5102", "medical_necessity", 126.0)]
    assert [c["claim_id"] for c in get(client, "/medical-claims?status=paid")["items"]] == ["MC-9011", "MC-9012", "MC-9013"]
    assert [c["claim_id"] for c in get(client, "/medical-claims?hold_reason=duplicate")["items"]] == ["MC-9101", "MC-9102"]
    assert get(client, "/medical-claims")["count"] == 9 and all("determination_drafts" not in c for c in held)


def test_mc_9101_is_a_true_duplicate_of_mc_9011(client):
    c = claim(client, 9101)
    assert len(c["compared_with"]) == 1
    row = c["compared_with"][0]
    assert (row["earlier_claim_id"], row["same_provider"], row["same_date_of_service"], row["same_amount"],
            row["days_between_the_dates_of_service"], row["member_provider_date_and_code_all_match"]) == ("MC-9011", True, True, True, 0, True)
    assert row["sentence"] == ("MC-9011 is for the same member, the same provider, the same code and the same date of service, "
                               "6 Nov 2026. It was paid on 11 Nov 2026.")
    assert c["cover_on_date_of_service"]["in_force"] is True and c["medical_policy"] is None


def test_mc_9102_looks_like_mc_9012_and_is_not_a_duplicate(client):
    c = claim(client, 9102)
    row = c["compared_with"][0]
    assert (row["earlier_claim_id"], row["same_provider"], row["same_date_of_service"], row["days_between_the_dates_of_service"],
            row["member_provider_date_and_code_all_match"]) == ("MC-9012", True, False, 7, False)
    assert row["sentence"] == ("MC-9012 is for the same member and the same code, but its date of service is 10 Nov 2026 and this "
                               "line's is 17 Nov 2026, 7 days apart. It was paid on 15 Nov 2026.")
    f = c["if_paid_under_the_plan"]
    assert (f["total_claimed"], f["total_within_the_limits"], f["member_share"], f["plan_pays"], f["member_pays"]) == (42.0, 42.0, 8.4, 33.6, 8.4)
    assert f["lines"][0]["sessions_within_the_plan"] == 1 and f["lines"][0]["benefit_id"] == "BEN-E07"


def test_mc_9103_has_a_date_of_service_after_the_cover_ended(client):
    c = claim(client, 9103)
    assert c["cover_on_date_of_service"] == {"member_id": "MEM-7206", "on": "2026-11-14", "in_force": False,
                                             "reason": "The member's cover ended on 27 Oct 2026: The member left the employer. "
                                                       "14 Nov 2026 is 18 days after the end."}
    assert c["compared_with"] == [] and c["compared_with_note"] == "No earlier claim of this member carries the same code."
    assert "does not say the claim is to be paid" in c["if_paid_under_the_plan"]["what_this_is"]


def test_mc_9104_goes_over_the_yearly_limit_for_medicines(client):
    c = claim(client, 9104)
    f = c["if_paid_under_the_plan"]
    assert (f["total_claimed"], f["total_within_the_limits"], f["total_over_the_limits"]) == (113.4, 70.0, 43.4)
    assert (f["member_share"], f["plan_pays"], f["member_pays"]) == (14.0, 56.0, 57.4)
    assert f["working"] == ["Within the limits: 64.80 + 5.20 = 70.00", "Over the limits: 113.40 - 70.00 = 43.40",
                            "Less the member's share: 70.00 - 14.00 = 56.00", "The plan pays USD 56.00. The member pays USD 57.40."]
    assert [(x["within_the_limit"], x["over_the_limit"], x["member_share"], x["plan_pays"]) for x in f["lines"]] == [
        (64.8, 0.0, 12.96, 51.84), (5.2, 43.4, 1.04, 4.16)]
    assert all(x["benefit_id"] == "BEN-E06" for x in f["lines"])
    assert c["cover_on_date_of_service"]["in_force"] is True
    assert [r["member_provider_date_and_code_all_match"] for r in c["compared_with"]] == [False]  # MC-9013, 33 days apart


def test_mc_9105_is_held_for_medical_necessity_and_its_notes_meet_mp_301(client):
    c = claim(client, 9105)
    assert c["medical_policy"]["medical_policy_id"] == "MP-301" and c["member"]["plan_name"] == "Thornmere Health Complete"
    notes = c["documents"][0]["text"]
    assert "Lower back pain for 10 weeks" in notes and "physiotherapy for 6 weeks" in notes and "weakness lifting the right foot" in notes
    f = c["if_paid_under_the_plan"]
    assert (f["total_within_the_limits"], f["member_share"], f["plan_pays"]) == (620.0, 0.0, 620.0) and "sessions_beyond_the_plan" not in f
    assert c["cover_on_date_of_service"]["in_force"] is True and c["compared_with"] == []


def test_mc_9106_is_held_for_medical_necessity_and_the_file_does_not_settle_mp_302(client):
    c = claim(client, 9106)
    assert c["medical_policy"]["medical_policy_id"] == "MP-302"
    assert c["sessions_used_before_this_claim"] == {
        "used": 12, "plan_gives": 12, "all_used": True,
        "sentence": "Before this claim the member had used 12 of the 12 physiotherapy sessions the plan gives in the benefit year."}
    assert [d["doc_type"] for d in c["documents"]] == ["referral"]
    assert "3 further sessions of physiotherapy" in c["documents"][0]["text"] and "Dated: 10 Nov 2026" in c["documents"][0]["text"]
    f = c["if_paid_under_the_plan"]
    assert (f["total_claimed"], f["total_within_the_limits"], f["total_over_the_limits"], f["plan_pays"]) == (126.0, 0.0, 126.0, 0.0)
    assert (f["sessions_beyond_the_plan"], f["plan_pays_if_the_medical_policy_is_met"]) == (3, 126.0)
    assert [x["date_of_service"] for x in c["lines"]] == ["2026-11-12", "2026-11-16", "2026-11-20"]
    assert c["compared_with"] == []


# ---------------------------------------------------------------- medical claims: drafts and the change
def test_a_determination_is_a_draft_carries_the_systems_figures_and_decides_nothing(client, store):
    body = {"suggestion": "pay_as_the_plan_allows", "reasons": ["USD 70.00 is within the limit and USD 43.40 is over it."]}
    r = post(client, "/medical-claims/MC-9104/determination", body)
    assert r["kind"] == "draft" and r["draft"]["version"] == 1
    assert r["draft"]["figures_worked_out_by_the_system"] == {
        "total_claimed": 113.4, "total_within_the_limits": 70.0, "total_over_the_limits": 43.4, "member_share": 14.0, "plan_pays": 56.0,
        "member_pays": 57.4}
    assert post(client, "/medical-claims/MC-9104/determination", body)["draft"]["version"] == 2
    stored = store.data["medical_claims"]["MC-9104"]
    assert stored["status"] == "held" and stored["decision"] is None
    c = claim(client, 9104)
    assert "determination_drafts" not in c and c["drafts_on_file"] == 2 and "pay_as_the_plan_allows" not in json.dumps(c)
    assert get(client, "/medical-claims/MC-9104/drafts")["items"][1]["suggestion"] == "pay_as_the_plan_allows"
    assert store.data["health_members"]["MEM-7207"]["used_this_benefit_year"]["medicines"]["amount"] == 730.0


def test_the_right_determinations_of_the_other_claims_can_be_saved(client):
    dup = {"suggestion": "do_not_pay", "reasons": ["A duplicate of MC-9011."], "duplicate_of": "MC-9011"}
    assert post(client, "/medical-claims/MC-9101/determination", dup)["draft"]["duplicate_of"] == "MC-9011"
    assert post(client, "/medical-claims/MC-9102/determination", {"suggestion": "pay_as_the_plan_allows",
                                                                 "reasons": ["Not a duplicate: the dates of service differ."]})["applied"]
    assert post(client, "/medical-claims/MC-9103/determination", {"suggestion": "do_not_pay", "reasons": ["Cover ended on 27 Oct 2026."]})["applied"]
    met = {"suggestion": "pay_as_the_plan_allows", "reasons": ["MP-301 is met."], "criteria": MET}
    assert post(client, "/medical-claims/MC-9105/determination", met)["applied"] is True
    ask = {"suggestion": "ask_the_provider", "reasons": ["No report by the physiotherapist is in the file."],
           "question_for_the_provider": "Please send the physiotherapist's report.",
           "criteria": [MET[0], {"criterion": "2", "finding": "not_stated", "evidence": "No report in the file."}, MET[2]]}
    assert post(client, "/medical-claims/MC-9106/determination", ask)["draft"]["figures_worked_out_by_the_system"][
        "plan_pays_if_the_medical_policy_is_met"] == 126.0


def test_a_determination_is_refused_with_a_plain_sentence_and_nothing_saved(client, store):
    def refused(n, body, words):
        r = post(client, f"/medical-claims/MC-{n}/determination", body, 409)
        assert words in r["detail"] and "Nothing was saved" in r["detail"] and r["applied"] is False
        assert store.data["medical_claims"][f"MC-{n}"]["determination_drafts"] == []

    base = {"suggestion": "do_not_pay", "reasons": ["A duplicate."]}
    refused(9101, {**base, "duplicate_of": "MC-9999"}, "MC-9999 is not an earlier medical claim the insurer holds")
    refused(9101, {**base, "duplicate_of": "MC-9101"}, "is not an earlier medical claim")
    refused(9101, {**base, "criteria": MET}, "No medical policy is to be read for MC-9101")
    refused(9105, {**base, "criteria": [{"criterion": "7", "finding": "met"}]}, "MP-301 has the criteria 1, 2, 3")
    refused(9011, base, "MC-9011 is not held for review: its status is paid")
    refused(9106, {"suggestion": "ask_the_provider", "reasons": ["No report."]}, "needs the question for the provider")
    refused(9106, {"suggestion": "ask_the_provider", "reasons": ["No report."], "question_for_the_provider": "  "},
            "The suggestion ask_the_provider needs the question for the provider, in a sentence.")
    empty = client.post("/health/medical-claims/MC-9101/determination", headers=H, json={"suggestion": "do_not_pay", "reasons": []})
    assert empty.status_code == 422


def test_a_decision_on_a_claim_needs_an_assessor_and_happens_once(client, store):
    pay = {"decision": "pay", "decided_by": "Ottilie Marsh", "reason": "Within the plan."}
    out = post(client, "/medical-claims/MC-9103/decision", pay, 409)
    assert "MC-9103 cannot be paid: The member's cover ended on 27 Oct 2026" in out["detail"] and "Nothing was changed" in out["detail"]
    assert store.data["medical_claims"]["MC-9103"]["status"] == "held"
    assert "not held for review" in post(client, "/medical-claims/MC-9011/decision", pay, 409)["detail"]
    assert client.post("/health/medical-claims/MC-9104/decision", headers=H, json={"decision": "pay", "reason": "x"}).status_code == 422
    done = post(client, "/medical-claims/MC-9104/decision", pay)
    assert done["kind"] == "change" and done["decision"]["amount_to_pay"] == 56.0 and done["message"] == "MC-9104 is decided: pay, USD 56.00."
    assert claim(client, 9104)["status"] == "decided"
    assert "already recorded on MC-9104, by Ottilie Marsh on 26 Nov 2026" in post(client, "/medical-claims/MC-9104/decision", pay, 409)["detail"]
    assert post(client, "/medical-claims/MC-9106/decision", pay)["decision"]["amount_to_pay"] == 126.0
    no = post(client, "/medical-claims/MC-9101/decision", {"decision": "do_not_pay", "decided_by": "Ottilie Marsh", "reason": "A duplicate."})
    assert no["decision"]["amount_to_pay"] == 0.0 and no["message"] == "MC-9101 is decided: do not pay."
    # a decision moves no usage: paying is another system's work
    assert store.data["health_members"]["MEM-7207"]["used_this_benefit_year"]["medicines"]["amount"] == 730.0


# ---------------------------------------------------------------- providers, contracts and tariffs
def test_the_two_providers_have_their_own_prices_and_their_own_figures(client):
    rows = {p["provider_id"]: p for p in get(client, "/providers")["items"]}
    assert list(rows) == ["PRV-5101", "PRV-5102"] and all(p["tariff_line_count"] == 12 for p in rows.values())
    one, two = rows["PRV-5101"], rows["PRV-5102"]
    assert (one["medicines_discount_percent"], one["follow_up_free_within_days"]) == (10, 14)
    assert (two["medicines_discount_percent"], two["follow_up_free_within_days"]) == (5, 7)
    assert [c["clause"] for c in one["contract"]] == ["1.1", "2.1", "3.1", "4.1", "5.1", "6.1"]
    clause = lambda p, n: next(c["text"] for c in p["contract"] if c["clause"] == n)
    assert clause(one, "3.1") == "Medicines are billed at the tariff price less 10 percent."
    assert "within 7 days" in clause(two, "4.1") and "agreement in writing" in clause(one, "5.1")
    price = lambda p, code: next((t["agreed_price"] for t in p["tariff"] if t["code"] == code), None)
    assert (price(one, "TMI-T-1010"), price(two, "TMI-T-1010"), price(one, "TMI-T-2020"), price(two, "TMI-T-2020")) == (60.0, 55.0, 70.0, 65.0)
    assert price(one, "TMI-T-8050") is None and price(one, "TMI-T-6040") is None and price(two, "TMI-T-3020") is None
    assert get(client, "/providers/PRV-5102")["contract_id"] == "CON-5102"


# ---------------------------------------------------------------- provider invoices: the five right answers
def test_the_five_invoices(client):
    rows = get(client, "/invoices")["items"]
    assert [(i["invoice_id"], i["provider_id"], i["received"], i["total_charged"]) for i in rows] == [
        ("PI-9501", "PRV-5101", "2026-11-22", 170.0), ("PI-9502", "PRV-5102", "2026-11-23", 180.0),
        ("PI-9503", "PRV-5101", "2026-11-21", 165.0), ("PI-9504", "PRV-5102", "2026-11-24", 112.0),
        ("PI-9505", "PRV-5101", "2026-11-25", 102.0)]
    assert all(i["status"] == "received" and "difference_drafts" not in i for i in rows)
    assert [i["invoice_id"] for i in get(client, "/invoices?provider_id=PRV-5102")["items"]] == ["PI-9502", "PI-9504"]


def test_pi_9501_agrees_with_the_tariff_and_its_follow_up_is_outside_the_free_period(client):
    k = invoice(client, 9501)["check"]
    assert (k["total_charged"], k["total_agreed"], k["total_difference"], k["lines_with_a_difference"], k["agrees_with_the_contract"]) == (
        170.0, 170.0, 0.0, [], True)
    assert all(x["kind"] == "agrees" for x in k["lines"])
    assert [x["clause"] for x in k["lines"]] == ["1.1", "1.1", "4.1", "1.1"]  # every line has its clause, also one that agrees
    assert k["lines"][0]["note"].startswith("Charged at the agreed price (clause 1.1).")
    follow = k["lines"][2]["follow_up"]
    assert follow == {"first_consultation_line_id": "PI-9501-L1", "first_consultation_date": "2026-10-27",
                      "days_after_the_first_consultation": 16, "free_within_days": 14, "inside_the_free_period": False}
    assert "is 16 days later. Clause 4.1 gives 14 days, so the follow-up is charged." in k["lines"][2]["note"]


def test_pi_9502_has_one_line_over_the_tariff(client):
    k = invoice(client, 9502)["check"]
    assert (k["total_charged"], k["total_agreed"], k["total_difference"], k["lines_with_a_difference"]) == (180.0, 165.0, 15.0, ["PI-9502-L2"])
    line = k["lines"][1]
    assert (line["code"], line["kind"], line["clause"], line["tariff_price"], line["unit_price_charged"], line["difference"]) == (
        "TMI-T-2020", "over_the_tariff", "1.1", 65.0, 80.0, 15.0)
    assert k["working"] == ["Charged: 100.00 + 80.00 = 180.00", "Agreed: 100.00 + 65.00 = 165.00", "Difference: 180.00 - 165.00 = 15.00"]


def test_pi_9503_has_one_line_that_is_not_on_the_tariff(client):
    inv = invoice(client, 9503)
    k = inv["check"]
    assert (k["total_charged"], k["total_agreed"], k["total_difference"], k["lines_with_a_difference"]) == (165.0, 110.0, 55.0, ["PI-9503-L2"])
    line = k["lines"][1]
    assert (line["code"], line["on_the_tariff"], line["kind"], line["clause"], line["agreed_amount"], line["difference"]) == (
        "TMI-T-8050", False, "not_on_the_tariff", "5.1", 0.0, 55.0)
    assert "no such agreement is on file" in line["note"] and inv["agreements_in_writing"] == []


def test_pi_9504_charges_a_follow_up_inside_the_free_period(client):
    k = invoice(client, 9504)["check"]
    assert (k["total_charged"], k["total_agreed"], k["total_difference"], k["lines_with_a_difference"]) == (112.0, 77.0, 35.0, ["PI-9504-L3"])
    line = k["lines"][2]
    assert (line["kind"], line["clause"], line["agreed_amount"], line["difference"]) == ("follow_up_inside_the_free_period", "4.1", 0.0, 35.0)
    assert line["follow_up"] == {"first_consultation_line_id": "PI-9504-L1", "first_consultation_date": "2026-11-14",
                                 "days_after_the_first_consultation": 5, "free_within_days": 7, "inside_the_free_period": True}
    assert line["note"].startswith("The same patient's first consultation was on 14 Nov 2026 (PI-9504-L1). This follow-up on "
                                   "19 Nov 2026 is 5 days later. Clause 4.1 gives 7 days, so the follow-up is not charged.")


def test_pi_9505_leaves_out_the_discount_on_medicines(client):
    inv = invoice(client, 9505)
    k = inv["check"]
    assert (k["total_charged"], k["total_agreed"], k["total_difference"]) == (102.0, 97.8, 4.2)
    assert k["lines_with_a_difference"] == ["PI-9505-L2", "PI-9505-L3"]
    two, three = k["lines"][1], k["lines"][2]
    assert (two["kind"], two["clause"], two["agreed_unit_price"], two["agreed_amount"], two["difference"]) == (
        "medicines_discount_not_applied", "3.1", 10.8, 21.6, 2.4)
    assert (three["kind"], three["agreed_unit_price"], three["agreed_amount"], three["difference"]) == (
        "medicines_discount_not_applied", 16.2, 16.2, 1.8)
    assert inv["medicines_discount_percent"] == 10 and [c["clause"] for c in inv["contract"]][2] == "3.1"
    assert k["lines"][0]["clause"] == "1.1"


def test_every_line_of_every_invoice_has_a_governing_clause(client):
    for n in range(9501, 9506):
        inv = invoice(client, n)
        known = {c["clause"] for c in inv["contract"]}
        assert all(x["clause"] in known for x in inv["check"]["lines"]), n


def test_a_medicine_that_agrees_a_line_under_the_tariff_and_an_agreement_in_writing():
    import copy
    from insurer.seed_health import check_invoice
    data = build_health(TODAY_D)
    provider, invoices = data["health_providers"]["PRV-5101"], data["provider_invoices"]
    inv = copy.deepcopy(invoices["PI-9505"])
    inv["lines"][1].update(unit_price_charged=10.8, amount_charged=21.6)   # the medicine at the discounted price
    inv["lines"][2].update(unit_price_charged=15.0, amount_charged=15.0)   # a medicine under the agreed 16.20
    k = check_invoice(inv, provider, invoices)
    assert (k["lines"][1]["kind"], k["lines"][1]["clause"], k["lines"][1]["difference"]) == ("agrees", "3.1", 0.0)
    assert (k["lines"][2]["kind"], k["lines"][2]["clause"], k["lines"][2]["difference"]) == ("under_the_tariff", "3.1", -1.2)
    assert "less than the USD 16.20 agreed" in k["lines"][2]["note"] and k["lines_with_a_difference"] == ["PI-9505-L3"]
    # a code that is not on the tariff, with an agreement in writing on file
    before = check_invoice(invoices["PI-9503"], provider, invoices)
    assert (before["lines"][1]["kind"], before["total_difference"]) == ("not_on_the_tariff", 55.0)
    provider["agreements_in_writing"].append({"code": "TMI-T-8050", "description": "Shockwave therapy session", "agreed_price": 55.0,
                                              "reference": "AGR-5101-1"})
    after = check_invoice(invoices["PI-9503"], provider, invoices)
    line = after["lines"][1]
    assert (line["kind"], line["clause"], line["on_the_tariff"], line["agreed_unit_price"], line["difference"]) == ("agrees", "5.1", False, 55.0, 0.0)
    assert line["agreement_in_writing"]["reference"] == "AGR-5101-1" and "an agreement in writing is on file for it (AGR-5101-1)" in line["note"]
    assert (after["total_agreed"], after["total_difference"], after["agrees_with_the_contract"]) == (165.0, 0.0, True)
    provider["agreements_in_writing"][0]["agreed_price"] = 50.0
    over = check_invoice(invoices["PI-9503"], provider, invoices)["lines"][1]
    assert (over["kind"], over["clause"], over["difference"]) == ("over_the_tariff", "5.1", 5.0)


def test_the_kinds_of_the_check_are_the_kinds_the_save_takes(client):
    doc = client.get("/health/openapi.json").json()
    kinds = set(doc["components"]["schemas"]["InvoiceDifference"]["properties"]["kind"]["enum"])
    assert kinds == {"over_the_tariff", "under_the_tariff", "not_on_the_tariff", "follow_up_inside_the_free_period",
                     "medicines_discount_not_applied", "other"}
    under = {"finding": "differences_found", "differences": [{"line_id": "PI-9502-L1", "kind": "under_the_tariff", "clause": "1.1"}]}
    assert post(client, "/invoices/PI-9502/differences", under)["applied"] is True
    positions = doc["components"]["schemas"]["PreAuthorisationAssessment"]["properties"]["plan_position"]["enum"]
    assert "plan_is_silent" in positions
    assert post(client, "/pre-authorisations/PA-8105/assessment", {**TO_THE_ASSESSOR, "plan_position": "plan_is_silent"})["applied"] is True


# ---------------------------------------------------------------- provider invoices: drafts and the change
DIFFERENCE = {"finding": "differences_found",
              "differences": [{"line_id": "PI-9502-L2", "kind": "over_the_tariff", "clause": "1.1", "note": "80.00 charged, 65.00 agreed."}]}


def test_a_list_of_differences_is_a_draft_and_queries_nothing(client, store):
    r = post(client, "/invoices/PI-9502/differences", DIFFERENCE)
    assert r["kind"] == "draft" and r["draft"]["version"] == 1
    assert r["draft"]["totals_worked_out_by_the_system"] == {"total_charged": 180.0, "total_agreed": 165.0, "total_difference": 15.0,
                                                             "lines_with_a_difference": ["PI-9502-L2"]}
    assert post(client, "/invoices/PI-9502/differences", DIFFERENCE)["draft"]["version"] == 2
    assert post(client, "/invoices/PI-9501/differences", {"finding": "agrees_with_the_contract"})["applied"] is True
    stored = store.data["provider_invoices"]["PI-9502"]
    assert stored["status"] == "received" and stored["decision"] is None
    inv = invoice(client, 9502)
    assert "difference_drafts" not in inv and inv["drafts_on_file"] == 2 and "differences_found" not in json.dumps(inv)
    assert get(client, "/invoices/PI-9502/drafts")["items"][0]["differences"][0]["line_id"] == "PI-9502-L2"


def test_a_list_of_differences_is_refused_with_a_plain_sentence_and_nothing_saved(client, store):
    def refused(body, words):
        r = post(client, "/invoices/PI-9502/differences", body, 409)
        assert words in r["detail"] and "Nothing was saved" in r["detail"] and r["applied"] is False
        assert store.data["provider_invoices"]["PI-9502"]["difference_drafts"] == []

    refused({"finding": "differences_found", "differences": [{"line_id": "PI-9503-L2", "kind": "not_on_the_tariff"}]},
            "Not a line of PI-9502: PI-9503-L2. Its lines are: PI-9502-L1, PI-9502-L2")
    refused({"finding": "differences_found"}, "needs one row for each line with a difference")
    refused({**DIFFERENCE, "finding": "agrees_with_the_contract"}, "takes no rows")


def test_a_query_is_a_claims_officers_decision_and_contacts_nobody(client, store):
    def refused(body, words):
        r = post(client, "/invoices/PI-9502/query", body, 409)
        assert words in r["detail"] and "Nothing was changed" in r["detail"]
        assert store.data["provider_invoices"]["PI-9502"]["status"] == "received"

    query = {"decision": "query_the_lines", "line_ids": ["PI-9502-L2"], "decided_by": "Corin Ashby", "reason": "Over the tariff."}
    refused({**query, "line_ids": []}, "needs the ids of the lines to query")
    refused({**query, "line_ids": ["PI-9502-L9"]}, "Not a line of PI-9502: PI-9502-L9")
    refused({**query, "decision": "accept_as_charged"}, "takes no lines")
    assert client.post("/health/invoices/PI-9502/query", headers=H, json={"decision": "query_the_lines"}).status_code == 422
    done = post(client, "/invoices/PI-9502/query", query)
    assert done["kind"] == "change" and done["message"] == "PI-9502 is queried. Nobody has contacted the provider."
    assert invoice(client, 9502)["status"] == "queried"
    assert "already recorded on PI-9502, by Corin Ashby on 26 Nov 2026" in post(client, "/invoices/PI-9502/query", query, 409)["detail"]
    accepted = post(client, "/invoices/PI-9501/query", {"decision": "accept_as_charged", "decided_by": "Corin Ashby"})
    assert accepted["decision"]["line_ids"] == [] and invoice(client, 9501)["status"] == "accepted"


# ---------------------------------------------------------------- call-back requests
def test_a_call_back_request_is_a_draft_that_books_nothing(client, store):
    body = {"question": "Are hearing aids covered?",
            "why_the_documents_do_not_settle_it": "Neither the table of benefits nor the exclusions of GRP-6102 names hearing aids."}
    r = post(client, "/members/MEM-7208/call-back-requests", body)
    assert r["kind"] == "draft" and r["draft"]["call_back_id"] == "CB-0001" and r["draft"]["status"] == "draft"
    assert r["message"] == "CB-0001 is recorded for the member services team. No call is booked and no time is promised."
    assert post(client, "/members/MEM-7201/call-back-requests", body)["draft"]["call_back_id"] == "CB-0002"
    m = get(client, "/members/MEM-7208")
    assert m["call_back_requests_on_file"] == 1 and "hearing" not in json.dumps(m).lower()
    listed = get(client, "/members/MEM-7208/call-back-requests")
    assert listed["count"] == 1 and listed["items"][0]["question"] == "Are hearing aids covered?"
    assert store.data["health_members"] == build_all(TODAY_D)["health_members"]
    assert client.post("/health/members/MEM-7208/call-back-requests", headers=H, json={"question": "x"}).status_code == 422
    assert client.post("/health/members/MEM-9999/call-back-requests", headers=H, json=body).status_code == 404


# ---------------------------------------------------------------- unknown ids, reset and arrivals
def test_an_unknown_id_is_a_plain_404(client):
    for path, words in (("/schemes/GRP-9999", "No scheme with id GRP-9999"), ("/members/MEM-9999", "No member with id MEM-9999"),
                        ("/pre-authorisations/PA-9999", "No pre-authorisation request with id PA-9999"),
                        ("/medical-claims/MC-0000", "No medical claim with id MC-0000"), ("/providers/PRV-9999", "No provider with id PRV-9999"),
                        ("/invoices/PI-9999", "No provider invoice with id PI-9999"), ("/members/POL-2001", "No member with id POL-2001")):
        r = client.get(f"/health{path}", headers=H)
        assert r.status_code == 404 and words in r.json()["detail"] and r.json()["applied"] is False


def test_putting_the_health_system_back_leaves_the_claims_system_alone_and_the_other_way_round(client, store):
    triage = {"rule_id": "HG-3", "track": "fast track", "team": "fast-track team", "severity": "low", "reason": "Estimate under 2,500."}
    client.post("/claims/claims/CLM-4001/triage", headers=H, json=triage)
    post(client, "/pre-authorisations/PA-8105/assessment", TO_THE_ASSESSOR)
    post(client, "/medical-claims/MC-9101/decision", {"decision": "do_not_pay", "decided_by": "Ottilie Marsh", "reason": "A duplicate."})
    post(client, "/members/MEM-7208/call-back-requests", {"question": "q", "why_the_documents_do_not_settle_it": "w"})
    changed = client.get("/admin/state", headers=H).json()["changed_by"]
    assert changed == {"claims": ["claims"], "health": ["call_back_requests", "medical_claims", "pre_authorisations"]}
    fresh = build_all(TODAY_D)
    assert client.post("/admin/reset/claims", headers=H).json()["put_back"] == ["claims"]
    assert store.data["claims"] == fresh["claims"] and store.data["medical_claims"]["MC-9101"]["status"] == "decided"
    client.post("/claims/claims/CLM-4001/triage", headers=H, json=triage)
    back = client.post("/admin/reset/health", headers=H).json()
    assert back["put_back"] == ["call_back_requests", "medical_claims", "pre_authorisations"]
    assert all(store.data[name] == fresh[name] for name in HEALTH_SETS)
    assert len(store.data["claims"]["CLM-4001"]["triage_drafts"]) == 1
    assert post(client, "/members/MEM-7208/call-back-requests", {"question": "q", "why_the_documents_do_not_settle_it": "w"})[
        "draft"]["call_back_id"] == "CB-0001"
    assert client.post("/admin/reset", headers=H).json()["counts"]["medical_claims_held"] == 6
    assert store.data == fresh


def test_the_counts_name_the_open_items_of_the_health_system(client):
    counts = client.get("/admin/state", headers=H).json()["counts"]
    assert (counts["health_members"], counts["pre_authorisation_requests_received"], counts["medical_claims_held"],
            counts["provider_invoices_received"]) == (8, 6, 6, 5)
    assert "medical claims held" in client.get("/").text


def test_a_simulated_pre_authorisation_request_arrives_and_goes_back_with_the_health_system(client, store):
    first = client.post("/admin/simulate/pre-authorisation-request", headers=H).json()
    second = client.post("/admin/simulate/pre-authorisation-request", headers=H).json()
    assert (first["item_id"], second["item_id"], first["system"], first["event_type"]) == ("PA-8201", "PA-8202", "health", "pre-authorisation-request")
    one, two = pa(client, 8201), pa(client, 8202)
    assert (one["member_id"], one["plan_position"]["position"], one["medical_policy"]["medical_policy_id"]) == (
        "MEM-7208", "needs_pre_authorisation", "MP-301")
    assert (one["date_requested"], one["planned_date"]) == ("2026-11-26", "2026-12-06")
    assert (two["member_id"], two["plan_position"]["position"], two["medical_policy"]) == ("MEM-7202", "no_pre_authorisation_needed", None)
    third, fourth = (client.post("/admin/simulate/pre-authorisation-request", headers=H).json()["item_id"] for _ in range(2))
    assert pa(client, 8203)["medical_policy"]["medical_policy_id"] == "MP-303" and "MRI" not in pa(client, 8203)["documents"][1]["text"]
    assert (third, fourth, pa(client, 8204)["plan_position"]["position"]) == ("PA-8203", "PA-8204", "not_covered_by_the_plan")
    client.post("/admin/simulate/loss-report", headers=H)
    client.post("/admin/reset/health", headers=H)
    assert store.data["pre_authorisations"] == build_all(TODAY_D)["pre_authorisations"] and "LR-3101" in store.data["loss_reports"]
    assert store.simulated == {"loss-report": 1}
    assert client.post("/admin/simulate/pre-authorisation-request", headers=H).json()["item_id"] == "PA-8201"
    sub = client.post("/admin/subscriptions", headers=H, json={"event_kind": "pre-authorisation-request", "url": "http://127.0.0.1:9/x"})
    assert sub.status_code == 200
