"""The right answers of SCENARIOS.md, checked against the data the service gives at the insurer date 2026-11-26."""
from conftest import H


def get(client, path):
    r = client.get(path, headers=H)
    assert r.status_code == 200, (path, r.status_code, r.text[:300])
    return r.json()


def post(client, path, body=None, status=200):
    r = client.post(path, json=body or {}, headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:400])
    return r.json()


def calc(client, claim_id, excluded=()):
    body = {"excluded_lines": [{"line_id": line, "clause": clause, "reason": "test"} for line, clause in excluded]}
    return post(client, f"/claims/claims/{claim_id}/settlement/calculate", body)


def checklist(client, claim_id):
    return {row["doc_type"]: row for row in get(client, f"/claims/claims/{claim_id}")["document_checklist"]}


# ---------------------------------------------------------------- policies and cover
def test_dates_of_the_ten_claims(client):
    expected = {"CLM-4001": ("2026-11-17", "2026-11-20", 3), "CLM-4002": ("2026-11-14", "2026-11-16", 2),
                "CLM-4003": ("2026-11-07", "2026-11-08", 1), "CLM-4004": ("2026-11-19", "2026-11-19", 0),
                "CLM-4005": ("2026-11-21", "2026-11-22", 1), "CLM-4006": ("2026-11-11", "2026-11-12", 1),
                "CLM-4007": ("2026-11-23", "2026-11-23", 0), "CLM-4008": ("2026-11-18", "2026-11-20", 2),
                "CLM-4009": ("2026-10-27", "2026-10-28", 1), "CLM-4010": ("2026-11-10", "2026-11-13", 3)}
    for claim_id, (loss, reported, days) in expected.items():
        c = get(client, f"/claims/claims/{claim_id}")
        assert (c["loss_date"], c["reported_date"], c["days_from_loss_to_report"]) == (loss, reported, days), claim_id


def test_only_clm_4003_was_out_of_cover_on_its_loss_date(client):
    for n in range(4001, 4011):
        cover = get(client, f"/claims/claims/CLM-{n}")["cover_on_loss_date"]
        assert cover["in_force"] is (n != 4003), n
    reason = get(client, "/claims/claims/CLM-4003")["cover_on_loss_date"]["reason"]
    assert reason == ("The policy period ended on 5 Nov 2026 and the policy was not renewed. 7 Nov 2026 is 2 days after the end.")


def test_cover_for_the_four_loss_reports(client):
    assert get(client, "/policy/policies/POL-2011/cover?on=2026-11-25")["in_force"] is True
    assert get(client, "/policy/policies/POL-2014/cover?on=2026-11-25")["in_force"] is True
    out = get(client, "/policy/policies/POL-2013/cover?on=2026-11-24")
    assert out["in_force"] is False and "cancelled on 17 Oct 2026" in out["reason"] and "38 days after" in out["reason"]
    assert client.get("/policy/policies/POL-2021", headers=H).status_code == 404
    found = get(client, "/policy/policies?text=Elric Stannaway")["items"]
    assert [p["policy_id"] for p in found] == ["POL-2012"] and found[0]["address"].startswith("7 Otterburn Gardens")
    assert client.get("/policy/policies/POL-2011/cover?on=25-11-2026", headers=H).status_code == 422


def test_a_search_finds_a_holder_with_one_word_misspelt_and_lists_all_with_no_text(client):
    assert [p["policy_id"] for p in get(client, "/policy/policies?text=Elrick Stannaway")["items"]] == ["POL-2012"]
    assert get(client, "/policy/policies")["count"] == 14


def test_the_wordings_and_the_one_endorsement(client):
    motor, home = get(client, "/policy/wordings/TMI-MOT-01"), get(client, "/policy/wordings/TMI-HOM-02")
    assert motor["clause_count"] == 19 and home["clause_count"] == 20
    text = " ".join(c["text"] for c in motor["clauses"]).lower()
    assert "key" not in text and "unattended" not in text  # the wording is silent on a key left in the vehicle
    p = get(client, "/policy/policies/POL-2008")
    assert p["schedule"]["named_drivers"] == ["Marisol Underhay", "Piers Underhay"]
    assert [e["endorsement_id"] for e in p["endorsements"]] == ["END-2008-1"]
    assert get(client, "/policy/policies/POL-2007")["schedule"]["alternative_accommodation_limit"] == 24000.0


# ---------------------------------------------------------------- packs
def test_pack_of_clm_4001_is_all_in_the_file(client):
    assert all(r["in_the_file"] and r["readable"] for r in checklist(client, "CLM-4001").values())


def test_pack_of_clm_4002_lacks_the_plumbers_report_and_has_unreadable_photographs(client):
    rows = checklist(client, "CLM-4002")
    assert rows["plumber_report"]["in_the_file"] is False
    assert rows["photographs"]["in_the_file"] is True and rows["photographs"]["readable"] is False
    assert rows["claim_form"]["in_the_file"] and rows["repair_estimate"]["in_the_file"]


def test_pack_of_clm_4005_lacks_the_police_report_and_its_estimate_names_another_registration(client):
    rows = checklist(client, "CLM-4005")
    assert rows["police_report"]["in_the_file"] is False
    c = get(client, "/claims/claims/CLM-4005")
    estimate = next(d for d in c["documents"] if d["doc_type"] == "repair_estimate")
    assert "MR-7702-B" in estimate["text"] and get(client, "/policy/policies/POL-2005")["schedule"]["registration"] == "MR-7720-B"


def test_pack_of_clm_4007_lacks_the_contents_list_and_two_documents_disagree_on_the_origin(client):
    assert checklist(client, "CLM-4007")["contents_list"]["in_the_file"] is False
    docs = {d["doc_type"]: d["text"] for d in get(client, "/claims/claims/CLM-4007")["documents"]}
    assert "cooker in the kitchen" in docs["claim_form"] and "tumble dryer in the utility room" in docs["fire_service_report"]


def test_packs_of_the_two_thefts_and_clm_4008_are_complete(client):
    for claim_id in ("CLM-4003", "CLM-4004", "CLM-4006", "CLM-4008"):
        assert all(r["in_the_file"] and r["readable"] for r in checklist(client, claim_id).values()), claim_id


# ---------------------------------------------------------------- settlements
def test_settlement_of_clm_4001(client):
    r = calc(client, "CLM-4001", [("DOC-4001-3-L4", "2.5")])
    assert (r["total_claimed"], r["total_not_covered"], r["total_reduced_by_limits"]) == (2350.0, 80.0, 120.0)
    assert (r["total_allowed"], r["deductible"], r["deductible_clause"], r["amount_payable"]) == (2150.0, 250.0, "4.1", 1900.0)
    assert r["approval_needed_from"] == "handler" and r["saved"] is False
    assert r["working"][0] == "Lines allowed: 1,200.00 + 450.00 + 500.00 = 2,150.00"
    glass = next(x for x in r["lines"] if x["category"] == "windscreen")
    assert glass["allowed"] == 500.0 and "clause 3.2" in glass["note"]


def test_settlement_of_clm_4001_with_the_valet_left_in_is_a_different_and_wrong_figure(client):
    assert calc(client, "CLM-4001")["amount_payable"] == 1980.0


def test_settlement_of_clm_4004(client):
    r = calc(client, "CLM-4004")
    assert (r["total_claimed"], r["total_allowed"], r["deductible"], r["amount_payable"]) == (14740.0, 14600.0, 400.0, 14200.0)
    hire = next(x for x in r["lines"] if x["category"] == "hire_car")
    assert hire["allowed"] == 400.0 and "10 days at USD 40.00 a day" in hire["note"]
    assert r["approval_needed_from"] == "senior adjuster"


def test_settlement_of_clm_4009(client):
    r = calc(client, "CLM-4009", [("DOC-4009-3-L4", "2.5")])
    assert (r["total_claimed"], r["total_not_covered"], r["total_allowed"]) == (8400.0, 2400.0, 5600.0)
    assert (r["deductible"], r["deductible_clause"], r["amount_payable"], r["approval_needed_from"]) == (500.0, "4.2", 5100.0, "senior adjuster")
    trace = next(x for x in r["lines"] if x["category"] == "trace_and_access")
    assert trace["allowed"] == 1500.0 and "clause 3.4" in trace["note"]


def test_the_single_item_limit_applies_to_the_watch_of_clm_4006(client):
    r = calc(client, "CLM-4006")
    watch = next(x for x in r["lines"] if x["description"] == "Wristwatch")
    assert watch["allowed"] == 2500.0 and "clause 3.2" in watch["note"]


def test_a_settlement_refuses_a_line_that_is_not_the_claims(client):
    r = post(client, "/claims/claims/CLM-4001/settlement/calculate",
             {"excluded_lines": [{"line_id": "DOC-4009-3-L4", "clause": "2.5", "reason": "x"}]}, 409)
    assert "Not a line of CLM-4001" in r["detail"] and r["applied"] is False


def test_a_saved_settlement_carries_the_figures_the_system_worked_out(client, store):
    r = post(client, "/claims/claims/CLM-4009/settlement",
             {"excluded_lines": [{"line_id": "DOC-4009-3-L4", "clause": "2.5", "reason": "An improvement."}]})
    assert r["applied"] is True and r["kind"] == "draft" and r["draft"]["version"] == 1 and r["draft"]["amount_payable"] == 5100.0
    assert store.data["claims"]["CLM-4009"]["payments"] == []


# ---------------------------------------------------------------- letters and decisions
def test_a_decline_letter_is_refused_where_no_decision_to_decline_is_recorded(client, store):
    body = {"template_id": "TPL-DECLINE", "letter_text": "We are not able to pay your claim."}
    r = post(client, "/claims/claims/CLM-4006/letters", body, 409)
    assert "No adjuster's decision to decline is recorded on CLM-4006" in r["detail"] and "HG-6" in r["detail"]
    assert store.data["claims"]["CLM-4006"]["letter_drafts"] == []
    assert post(client, "/claims/claims/CLM-4009/letters", body, 409)["applied"] is False  # cover accepted is not a decline
    ok = post(client, "/claims/claims/CLM-4010/letters", body)
    assert ok["draft"]["version"] == 1 and store.data["claims"]["CLM-4010"]["letters_sent"] == []


def test_the_decision_on_clm_4010(client):
    d = get(client, "/claims/claims/CLM-4010")["decision"]
    assert (d["decision"], d["decided_by"], d["clause"], d["decided_on"]) == ("declined", "Fenella Arkwright", "2.2", "2026-11-20")
    assert "74 days" in d["reason"]


def test_the_other_letters_can_be_saved_on_any_claim(client):
    for template in ("TPL-ACK", "TPL-MISSING"):
        assert post(client, "/claims/claims/CLM-4002/letters", {"template_id": template, "letter_text": "Dear Ms Marrowdene"})["applied"]
    assert get(client, "/claims/letter-templates")["count"] == 3


# ---------------------------------------------------------------- loss reports and registration
FILE = {"policy_id": "POL-2011", "claim_type": "motor_own_damage", "loss_date": "2026-11-25", "loss_place": "Marlow Reach retail park",
        "what_happened": "Reversed into a bollard.", "people_injured": "no", "another_party_involved": "no",
        "cover_in_force_on_loss_date": "yes", "missing_items": [], "proposal": "register"}


def test_the_four_loss_reports(client):
    reports = {r["loss_report_id"]: r for r in get(client, "/claims/loss-reports")["items"]}
    assert list(reports) == ["LR-3001", "LR-3002", "LR-3003", "LR-3004"]
    assert reports["LR-3002"]["policy_number_given"] == "POL-2021" and "date" not in reports["LR-3002"]["text"].lower()
    assert "25 Nov 2026" in reports["LR-3001"]["text"] and "24 Nov 2026" in reports["LR-3003"]["text"]
    assert "taken to hospital" in reports["LR-3004"]["text"]


def test_a_claim_file_is_a_draft_and_registers_nothing(client, store):
    r = post(client, "/claims/loss-reports/LR-3001/claim-file", FILE)
    assert r["kind"] == "draft" and r["draft"]["version"] == 1
    assert store.data["loss_reports"]["LR-3001"]["status"] == "new" and len(store.data["claims"]) == 10


def test_a_claim_file_with_a_policy_the_insurer_does_not_hold_is_refused(client):
    r = post(client, "/claims/loss-reports/LR-3002/claim-file", {**FILE, "policy_id": "POL-2021"}, 409)
    assert "no policy with the id POL-2021" in r["detail"]


def test_registering_needs_a_draft_that_proposes_it_and_happens_once(client, store):
    assert "no claim file draft" in post(client, "/claims/loss-reports/LR-3001/register", {"draft_version": 1}, 409)["detail"]
    post(client, "/claims/loss-reports/LR-3003/claim-file", {**FILE, "policy_id": "POL-2013", "cover_in_force_on_loss_date": "no",
                                                             "proposal": "refer_to_a_handler"})
    assert "cannot be registered" in post(client, "/claims/loss-reports/LR-3003/register", {"draft_version": 1}, 409)["detail"]
    post(client, "/claims/loss-reports/LR-3001/claim-file", FILE)
    r = post(client, "/claims/loss-reports/LR-3001/register", {"draft_version": 1, "registered_by": "Ottilie Marsh"})
    assert r["kind"] == "change" and r["claim_id"] == "CLM-4101"
    assert get(client, "/claims/claims/CLM-4101")["registered_from"] == "LR-3001"
    assert "already registered as CLM-4101" in post(client, "/claims/loss-reports/LR-3001/register", {"draft_version": 1}, 409)["detail"]


# ---------------------------------------------------------------- the other drafts
def test_a_pack_check_refuses_a_document_type_that_is_not_on_the_checklist(client):
    body = {"items": [{"doc_type": "police_report", "finding": "missing"}], "proposal": "ask_the_customer"}
    r = post(client, "/claims/claims/CLM-4002/pack-check", body, 422)
    assert "Not on the checklist for home_escape_of_water: police_report" in r["detail"]
    body["items"][0]["doc_type"] = "plumber_report"
    short = post(client, "/claims/claims/CLM-4002/pack-check", body, 422)
    assert "Left out: claim_form, repair_estimate, photographs" in short["detail"]
    body["items"] = [{"doc_type": "claim_form", "finding": "received", "document_id": "DOC-4002-1"},
                     {"doc_type": "plumber_report", "finding": "missing"},
                     {"doc_type": "repair_estimate", "finding": "received", "document_id": "DOC-4002-2"},
                     {"doc_type": "photographs", "finding": "cannot_be_read", "document_id": "DOC-4002-3"}]
    assert post(client, "/claims/claims/CLM-4002/pack-check", body)["draft"]["version"] == 1


def test_a_claim_carries_what_the_policy_insures_its_wording_and_its_team(client):
    c = get(client, "/claims/claims/CLM-4005")
    assert (c["insured_vehicle_registration"], c["wording_id"], c["wording_version"], c["handling_team"]) == ("MR-7720-B", "TMI-MOT-01", "3", None)
    assert get(client, "/claims/claims/CLM-4002")["insured_item"] == "3 Weavers Yard, Tallowby, Meridia"
    assert [get(client, f"/claims/claims/CLM-{n}")["handling_team"] for n in (4002, 4004, 4006, 4009, 4010)] == [
        "property team", "theft team", "property team", "property team", "property team"]
    for n in (4001, 4003, 4005, 4007, 4008):  # the claims used to test sorting have no team yet
        assert get(client, f"/claims/claims/CLM-{n}")["handling_team"] is None


def test_a_limited_line_names_the_clause_of_its_limit(client):
    lines = {x["category"]: x for x in calc(client, "CLM-4001", [("DOC-4001-3-L4", "2.5")])["lines"]}
    assert (lines["windscreen"]["limited"], lines["windscreen"]["clause"]) == (True, "3.2")
    assert (lines["repair"]["limited"], lines["repair"]["clause"]) == (False, None)
    assert (lines["cleaning"]["excluded"], lines["cleaning"]["clause"]) == (True, "2.5")


def test_drafts_keep_every_version_and_change_no_status(client, store):
    triage = {"rule_id": "HG-1", "track": "person first", "team": "senior adjuster", "severity": "high", "reason": "A passenger was hurt."}
    assert post(client, "/claims/claims/CLM-4005/triage", triage)["draft"]["version"] == 1
    assert post(client, "/claims/claims/CLM-4005/triage", triage)["draft"]["version"] == 2
    cover = {"rows": [{"reference": "1.2", "finding": "applies", "note": "Theft, DOC-4004-2."}], "position": "wording_is_silent",
             "silent_on": "A key left in the vehicle.", "recovery": "no_recovery_indicated"}
    assert post(client, "/claims/claims/CLM-4004/coverage-check", cover)["applied"] is True
    summary = {"summary_text": "A fire.", "recovery": "no_recovery_indicated",
               "disagreements": [{"point": "where the fire started", "first_source": "DOC-4007-1", "first_says": "the cooker",
                                  "second_source": "DOC-4007-2", "second_says": "the tumble dryer"}]}
    assert post(client, "/claims/claims/CLM-4007/summary", summary)["applied"] is True
    assert all(c["status"] in ("new", "in_assessment", "decided") for c in store.data["claims"].values())
    assert store.data["claims"]["CLM-4005"]["status"] == "new"


def test_an_unknown_claim_or_report_is_a_plain_404(client):
    assert "No claim with id CLM-9999" in client.get("/claims/claims/CLM-9999", headers=H).json()["detail"]
    assert "No loss report with id LR-9999" in client.get("/claims/loss-reports/LR-9999", headers=H).json()["detail"]


def test_the_handling_guide_holds_seven_rules(client):
    g = get(client, "/claims/handling-guide")
    assert [r["rule_id"] for r in g["sorting_rules"]["rules"]] == ["HG-1", "HG-2", "HG-3", "HG-4"]
    assert (g["settlement_authority"]["rule_id"], g["correspondence_rules"]["rule_id"], g["recovery_rule"]["rule_id"]) == ("HG-5", "HG-6", "HG-7")


def test_the_driver_of_a_motor_accident_comes_with_an_age_worked_out_by_the_system(client):
    d = get(client, "/claims/claims/CLM-4008")["driver"]
    assert (d["name"], d["age_on_the_date_of_the_loss"], d["under_25_on_the_date_of_the_loss"]) == ("Leander Underhay", 19, True)
    assert get(client, "/claims/claims/CLM-4001")["driver"]["age_on_the_date_of_the_loss"] == 44
    assert get(client, "/claims/claims/CLM-4005")["driver"]["under_25_on_the_date_of_the_loss"] is False
    assert get(client, "/claims/claims/CLM-4004")["driver"] is None


def test_saved_drafts_are_not_part_of_the_file_another_agent_reads(client):
    triage = {"rule_id": "HG-3", "track": "fast track", "team": "fast-track team", "severity": "low", "reason": "Estimate under 2,500."}
    post(client, "/claims/claims/CLM-4001/triage", triage)
    c = get(client, "/claims/claims/CLM-4001")
    assert "triage_drafts" not in c and "fast-track team" not in str(c)
    assert c["drafts_on_file"]["triage_drafts"] == 1 and c["drafts_on_file"]["letter_drafts"] == 0
    drafts = get(client, "/claims/claims/CLM-4001/drafts")
    assert drafts["triage_drafts"][0]["team"] == "fast-track team" and drafts["pack_check_drafts"] == []
    post(client, "/claims/loss-reports/LR-3001/claim-file", FILE)
    r = get(client, "/claims/loss-reports/LR-3001")
    assert "claim_file_drafts" not in r and r["claim_file_drafts_on_file"] == 1
    assert get(client, "/claims/loss-reports/LR-3001/claim-file")["items"][0]["proposal"] == "register"
    assert all("claim_file_drafts" not in x for x in get(client, "/claims/loss-reports")["items"])


def test_a_save_reads_plain_words_as_its_fixed_choices(client, store):
    """An agent that writes "condition met" in its reply sends the same words in a save."""
    cover = {"rows": [{"reference": "5.1", "finding": "Condition met", "note": "Told in 3 days, CLM-4001."},
                      {"reference": "no clause", "finding": "wording silent", "note": "A key left in the vehicle, DOC-4004-1."},
                      {"reference": "2.5", "finding": "EXCLUDES", "note": "The valet line."}],
             "position": "within the wording", "recovery": "No recovery indicated"}
    r = post(client, "/claims/claims/CLM-4001/coverage-check", cover)
    saved = r["draft"]
    assert [x["finding"] for x in saved["rows"]] == ["condition_met", "wording_silent", "excludes"]
    assert (saved["position"], saved["recovery"]) == ("within_the_wording", "no_recovery_indicated")
    pack = {"items": [{"doc_type": "claim_form", "finding": "received"}, {"doc_type": "plumber_report", "finding": "Missing"},
                      {"doc_type": "repair_estimate", "finding": "received"}, {"doc_type": "photographs", "finding": "cannot be read"}],
            "proposal": "ask the customer"}
    assert post(client, "/claims/claims/CLM-4002/pack-check", pack)["draft"]["proposal"] == "ask_the_customer"
    triage = {"rule_id": "hg-1", "track": "Person first", "team": "senior adjuster", "severity": "High", "reason": "A passenger was hurt."}
    assert post(client, "/claims/claims/CLM-4005/triage", triage)["draft"]["track"] == "person first"


def test_a_save_still_refuses_a_word_that_is_no_choice(client):
    cover = {"rows": [{"reference": "5.1", "finding": "probably fine", "note": "x"}], "position": "within_the_wording",
             "recovery": "no_recovery_indicated"}
    r = post(client, "/claims/claims/CLM-4001/coverage-check", cover, 422)
    assert r["applied"] is False and "finding" in r["detail"]
