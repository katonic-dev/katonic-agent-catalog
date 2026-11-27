"""The servicing system: the right answers of the Servicing section of SCENARIOS.md, every refusal, and the rules drafts keep.

Checked against the data the service gives at the insurer date 2026-11-26."""
import copy
import json
import re
from datetime import date

from insurer.seed import build_all
from insurer.seed_servicing import build_servicing
from conftest import H, TODAY

TODAY_D = date.fromisoformat(TODAY)
SV_SETS = sorted(build_servicing(TODAY_D))


def get(client, path, status=200):
    r = client.get(f"/servicing{path}", headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:300])
    return r.json()


def post(client, path, body=None, status=200):
    r = client.post(f"/servicing{path}", json=body or {}, headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:400])
    return r.json()


def chg(client, n):
    return get(client, f"/change-requests/CHG-{n}")


def crq(client, n):
    return get(client, f"/certificate-requests/CRQ-{n}")


def rules_of(pack):
    return {r["rule_id"]: r for r in pack["rules"]}


def rows_of(request):
    return {r["item_id"]: r for r in request["checked_against_the_policy"]["rows"]}


READY = {"next_step": "ready_for_the_servicing_officer", "summary": "No rule applies."}
CERT = {"can_be_prepared_as_asked": "yes", "next_step": "ready_for_the_servicing_officer", "certificate_text": "CERTIFICATE OF INSURANCE."}
CANNOT = {"can_be_prepared_as_asked": "no", "next_step": "refer_to_the_servicing_officer", "differences": ["The limit asked is higher."]}


# ---------------------------------------------------------------- the system as a whole
def test_the_servicing_system_has_24_operations_and_every_save_is_a_draft(client):
    doc = client.get("/servicing/openapi.json").json()
    ops = [(method, op) for item in doc["paths"].values() for method, op in item.items()]
    assert len(ops) == 24
    saves = sorted(op["operationId"] for method, op in ops if method != "get")
    assert saves == ["save_broker_call_back_request", "save_certificate_draft", "save_change_draft", "save_endorsement_draft"]
    for method, op in ops:
        assert not op["summary"].endswith("(change)"), op["operationId"]
        if method != "get":
            assert op["summary"].endswith("(draft)"), op["operationId"]
    assert client.get("/servicing/change-requests").status_code == 401
    assert "servicing/openapi.json" in client.get("/").text


def test_servicing_ids_have_their_own_ranges_and_collide_with_nothing():
    data = build_all(TODAY_D)
    prefixes = {"sv_rules": "SR-", "sv_policies": "POL-28", "sv_change_requests": "CHG-73", "sv_certificate_requests": "CRQ-74",
                "sv_brokers": "BRK-75", "sv_claims": "SCL-78", "sv_broker_queries": "BQ-76", "sv_endorsement_templates": "ET-"}
    for name, prefix in prefixes.items():
        assert all(key.startswith(prefix) for key in data[name]), name
    counts = {name: len(data[name]) for name in prefixes}
    assert counts == {"sv_rules": 8, "sv_policies": 9, "sv_change_requests": 8, "sv_certificate_requests": 7, "sv_brokers": 3,
                      "sv_claims": 4, "sv_broker_queries": 8, "sv_endorsement_templates": 5}
    keyed = [name for name in SV_SETS if name != "sv_policy_terms"]
    mine = {key for name in keyed for key in data[name]}
    others = {key for name, records in data.items() if name not in SV_SETS and isinstance(records, dict) for key in records}
    assert not mine & others
    assert len(data["policies"]) == 14 and not set(data["sv_policies"]) & set(data["policies"])


def test_no_text_of_the_servicing_data_holds_a_bare_date_counts_days_or_names_a_real_thing():
    data = build_servicing(TODAY_D)
    texts = [c["text"] for c in data["sv_change_requests"].values()] + [c["text"] for c in data["sv_certificate_requests"].values()]
    texts += [q["text"] for q in data["sv_broker_queries"].values()]
    texts += [n["text"] for c in data["sv_claims"].values() for n in c["internal_notes"]]
    assert len(texts) == 8 + 7 + 8 + 4
    for text in texts:
        assert not re.search(r"\b20\d\d-\d\d-\d\d\b", text), text
    blob = json.dumps(data).lower()
    for word in ("yesterday", "last week", "days ago", "weeks ago", "last month", "this morning", "tomorrow", "monday", "tuesday",
                 "wednesday", "thursday", "friday", "saturday", "sunday", chr(8212)):
        assert word not in blob, word
    for policy in data["sv_policies"].values():
        assert policy["address"].endswith(", Meridia")
    for broker in data["sv_brokers"].values():
        assert broker["address"].endswith(", Meridia")


def test_the_servicing_rules_are_eight_numbered_rules_with_their_limits(client):
    rules = get(client, "/rules")
    assert [r["rule_id"] for r in rules["items"]] == [f"SR-{n}" for n in range(1, 9)]
    by_id = {r["rule_id"]: r for r in rules["items"]}
    assert "14 days" in by_id["SR-1"]["text"] and "20 percent" in by_id["SR-3"]["text"] and "under 25" in by_id["SR-5"]["text"]
    assert [r["kind"] for r in rules["items"]] == ["referral"] * 5 + ["calculation", "point_to_raise", "referral"]
    assert rules["rating_areas"] == [{"rating_area": "RA-1", "town": "Port Ilvane"}, {"rating_area": "RA-2", "town": "Marlow Reach"},
                                     {"rating_area": "RA-3", "town": "Tallowby"}]


# ---------------------------------------------------------------- change requests
def test_the_list_of_change_requests_is_whole_and_holds_no_drafts(client):
    post(client, "/change-requests/CHG-7301/draft", READY)
    items = get(client, "/change-requests")["items"]
    assert [c["change_request_id"] for c in items] == [f"CHG-73{n:02d}" for n in range(1, 9)]
    assert all("change_drafts" not in c and "endorsement_drafts" not in c and c["text"] and c["requested_by"]["name"] for c in items)
    assert [c["change_request_id"] for c in get(client, "/change-requests?change_type=cancellation")["items"]] == ["CHG-7305", "CHG-7306"]


def test_chg_7301_an_address_change_in_the_same_rating_area_is_clean(client):
    c = chg(client, 7301)
    assert (c["policy_id"], c["received"], c["effective_date"]) == ("POL-2001", "2026-11-25", "2026-12-03")
    what = c["what_changes"]
    assert (what["present_rating_area"], what["new_rating_area"], what["same_rating_area"]) == ("RA-2", "RA-2", True)
    assert c["rules_that_apply"] == [] and c["referral_needed"] is False and c["next_step_by_the_rules"] == "ready_for_the_servicing_officer"
    assert (c["premium_adjustment"]["kind"], c["premium_adjustment"]["amount"]) == ("no_change", 0.0)
    assert c["points_to_raise_by_rule_sr_7"] == []


def test_chg_7302_an_address_change_to_another_rating_area_needs_re_rating(client):
    c = chg(client, 7302)
    what = c["what_changes"]
    assert (c["policy_id"], what["present_rating_area"], what["new_rating_area"], what["same_rating_area"]) == ("POL-2006", "RA-3", "RA-1", False)
    assert c["rules_that_apply"] == ["SR-2"] and c["refer_to"] == ["underwriting"] and c["next_step_by_the_rules"] == "refer_to_underwriting"
    assert c["premium_adjustment"]["worked_out"] is False and c["premium_adjustment"]["amount"] is None
    assert "SR-2" in c["premium_adjustment"]["note"]


def test_chg_7303_a_sum_insured_increase_over_20_percent_goes_to_an_underwriter(client):
    c = chg(client, 7303)
    what = c["what_changes"]
    assert (what["present_sum_insured"], what["new_sum_insured"], what["increase"], what["increase_percent"]) == (40000.0, 50000.0, 10000.0, 25.0)
    sr3 = rules_of(c)["SR-3"]
    assert sr3["applies"] is True and sr3["measured"] == "25.00 percent" and sr3["limit"] == "20.00 percent"
    assert c["rules_that_apply"] == ["SR-3"] and c["next_step_by_the_rules"] == "refer_to_underwriting"
    assert c["premium_adjustment"]["worked_out"] is False


def test_chg_7304_a_change_backdated_beyond_14_days_goes_to_the_team_leader(client):
    c = chg(client, 7304)
    assert (c["policy_id"], c["received"], c["effective_date"]) == ("POL-2801", "2026-11-24", "2026-11-04")
    dates = c["dates"]
    assert dates["days_effective_date_is_before_the_date_received"] == 20 and dates["days_before_the_insurer_date"] == 22
    assert dates["effective_date_is_before_the_insurer_date"] is True
    sr1 = rules_of(c)["SR-1"]
    assert sr1["applies"] is True and "6 days more than the 14 days allowed" in sr1["sentence"]
    assert c["what_changes"]["age_on_the_effective_date"] == 45 and rules_of(c)["SR-5"]["applies"] is False
    assert c["rules_that_apply"] == ["SR-1"] and c["refer_to"] == ["the servicing team leader"]
    assert c["next_step_by_the_rules"] == "refer_to_the_team_leader"
    assert len(c["points_to_raise_by_rule_sr_7"]) == 1 and "22 days before the insurer date" in c["points_to_raise_by_rule_sr_7"][0]
    assert c["policy_as_it_stands_on_the_effective_date"]["schedule_on_the_date"]["named_drivers"] == ["Ottoline Merrivale"]


def test_chg_7305_a_cancellation_with_an_open_claim_goes_to_the_team_leader_and_follows_the_claims_system(client, store):
    c = chg(client, 7305)
    assert (c["policy_id"], c["effective_date"], c["open_claims"]) == ("POL-2005", "2026-11-30", 1)
    assert c["claims_on_the_policy"] == [{"claim_id": "CLM-4005", "date_of_loss": "2026-11-21", "open": True, "held_in": "the claims system"}]
    assert c["rules_that_apply"] == ["SR-4"] and c["next_step_by_the_rules"] == "refer_to_the_team_leader"
    assert c["premium_adjustment"]["worked_out"] is False and "CLM-4005" in c["premium_adjustment"]["note"]
    assert c["gap_in_cover"]["checked"] is False and c["gap_in_cover"]["gap_in_cover"] is None
    store.data["claims"]["CLM-4005"]["status"] = "closed"  # the claims system as it stands is what counts
    after = chg(client, 7305)
    assert after["rules_that_apply"] == [] and after["premium_adjustment"]["amount"] == 189.04


def test_chg_7306_a_cancellation_leaves_4_days_without_cover_before_the_new_policy(client):
    c = chg(client, 7306)
    assert (c["policy_id"], c["what_changes"]["cancel_on"], c["what_changes"]["replacement_cover_starts"]) == ("POL-2802", "2026-12-06", "2026-12-11")
    gap = c["gap_in_cover"]
    assert (gap["gap_in_cover"], gap["days_without_cover"], gap["first_day_without_cover"], gap["last_day_without_cover"]) == \
        (True, 4, "2026-12-07", "2026-12-10")
    assert "4 days without cover: 7 Dec 2026 to 10 Dec 2026" in gap["sentence"]
    prem = c["premium_adjustment"]
    assert (prem["kind"], prem["amount"], prem["days_remaining"], prem["days_in_the_period"]) == ("return_premium", 381.0, 254, 365)
    assert "547.50 x 254 / 365 = 381.00" in prem["working"]
    assert c["rules_that_apply"] == [] and c["next_step_by_the_rules"] == "ready_for_the_servicing_officer"
    assert c["points_to_raise_by_rule_sr_7"] == [gap["sentence"]]


def test_chg_7307_a_vehicle_change_has_its_additional_premium_worked_out_pro_rata(client):
    c = chg(client, 7307)
    assert (c["policy_id"], c["effective_date"], c["rating"]["new_annual_premium"]) == ("POL-2803", "2026-12-01", 912.5)
    prem = c["premium_adjustment"]
    assert (prem["kind"], prem["amount"], prem["difference_a_year"], prem["days_remaining"], prem["days_in_the_period"]) == \
        ("additional_premium", 73.0, 182.5, 146, 365)
    assert prem["working"] == ("912.50 - 730.00 = 182.50 a year. 146 of 365 days remain, from 1 Dec 2026 to 25 Apr 2027, both included. "
                               "182.50 x 146 / 365 = 73.00.")
    assert c["rules_that_apply"] == [] and c["what_changes"]["new_registration"] == "MR-5068-N"
    same = get(client, "/policies/POL-2803/premium-adjustment?effective_on=2026-12-01&new_annual_premium=912.5")
    assert same["amount"] == 73.0 and same["saved"] is False


def test_chg_7308_an_increase_of_exactly_20_percent_does_not_fire_the_rule(client):
    c = chg(client, 7308)
    what = c["what_changes"]
    assert (what["present_sum_insured"], what["new_sum_insured"], what["increase"], what["increase_percent"]) == (19500.0, 23400.0, 3900.0, 20.0)
    sr3 = rules_of(c)["SR-3"]
    assert sr3["applies"] is False and "exactly on the limit" in sr3["sentence"]
    assert c["rules_that_apply"] == [] and c["referral_needed"] is False and c["next_step_by_the_rules"] == "ready_for_the_servicing_officer"
    prem = c["premium_adjustment"]
    assert (prem["kind"], prem["amount"], prem["days_remaining"]) == ("additional_premium", 60.4, 302)
    assert "73.00 x 302 / 365 = 60.40" in prem["working"]


def test_the_premium_sum_refuses_what_it_cannot_work_out(client):
    outside = get(client, "/policies/POL-2803/premium-adjustment?effective_on=2027-06-01&new_annual_premium=900")
    assert outside["worked_out"] is False and "outside the policy period" in outside["note"]
    lower = get(client, "/policies/POL-2803/premium-adjustment?effective_on=2026-12-01&new_annual_premium=547.5")
    assert (lower["kind"], lower["amount"]) == ("return_premium", 73.0)
    assert "Nothing was worked out" in get(client, "/policies/POL-2803/premium-adjustment?effective_on=2026-12-01", 409)["detail"]
    assert get(client, "/policies/POL-2803/premium-adjustment?effective_on=1-Dec&new_annual_premium=1", 422)["applied"] is False
    assert "No policy with id POL-9999" in get(client, "/policies/POL-9999/premium-adjustment?effective_on=2026-12-01&cancellation=true", 404)["detail"]
    open_claim = get(client, "/policies/POL-2005/premium-adjustment?effective_on=2026-11-30&cancellation=true")
    assert open_claim["worked_out"] is False and "SR-4" in open_claim["note"]


def test_the_gap_check_counts_the_days_between_an_expiry_and_a_renewal(client):
    lapse = get(client, "/policies/POL-2003/gap-in-cover?new_cover_starts_on=2026-11-26")
    assert (lapse["cover_ends_on"], lapse["gap_in_cover"], lapse["days_without_cover"]) == ("2026-11-05", True, 20)
    assert (lapse["first_day_without_cover"], lapse["last_day_without_cover"]) == ("2026-11-06", "2026-11-25")
    next_day = get(client, "/policies/POL-2003/gap-in-cover?new_cover_starts_on=2026-11-06")
    assert next_day["gap_in_cover"] is False and next_day["days_without_cover"] == 0 and next_day["days_of_overlap"] == 0
    overlap = get(client, "/policies/POL-2802/gap-in-cover?new_cover_starts_on=2026-12-04&cover_ends_on=2026-12-06")
    assert overlap["gap_in_cover"] is False and overlap["days_of_overlap"] == 3 and overlap["cover_end_taken_from"] == "the request"
    cancelled = get(client, "/policies/POL-2013/gap-in-cover?new_cover_starts_on=2026-10-20")
    assert (cancelled["cover_ends_on"], cancelled["days_without_cover"]) == ("2026-10-16", 3)


def test_a_draft_change_is_versioned_carries_the_systems_measure_and_changes_nothing_else(client, store):
    before = copy.deepcopy({k: v for k, v in store.data.items() if k != "sv_change_requests"})
    body = {"next_step": "ready for the servicing officer", "gap_in_cover": "yes", "points_to_raise": ["4 days without cover."],
            "summary": "Cancellation on 6 Dec 2026; return premium 381.00."}
    first = post(client, "/change-requests/CHG-7306/draft", body)
    second = post(client, "/change-requests/CHG-7306/draft", {**body, "drafted_by": "Policy Servicing agent"})
    assert first["kind"] == "draft" and (first["draft"]["version"], second["draft"]["version"]) == (1, 2)
    assert first["draft"]["next_step"] == "ready_for_the_servicing_officer"
    measured = first["draft"]["measured_by_the_system"]
    assert measured["premium_adjustment"]["amount"] == 381.0 and measured["gap_in_cover"]["days_without_cover"] == 4
    c = chg(client, 7306)
    assert "change_drafts" not in c and (c["change_drafts_on_file"], c["drafts_on_file"], c["status"]) == (2, 2, "received")
    assert "4 days without cover." not in json.dumps(c)
    assert len(get(client, "/change-requests/CHG-7306/drafts")["items"]) == 2
    assert {k: v for k, v in store.data.items() if k != "sv_change_requests"} == before
    assert store.data["sv_policies"]["POL-2802"]["status"] == "in_force" and store.data["sv_policies"]["POL-2802"]["cancelled_on"] is None


def test_a_draft_change_is_refused_with_a_reason_and_nothing_is_saved(client):
    ready = post(client, "/change-requests/CHG-7303/draft", READY, 409)
    assert "SR-3" in ready["detail"] and "underwriting" in ready["detail"] and "Nothing was saved" in ready["detail"]
    assert "SR-9" in post(client, "/change-requests/CHG-7301/draft", {**READY, "rules_that_apply": ["SR-9"]}, 409)["detail"]
    gap = post(client, "/change-requests/CHG-7306/draft", {**READY, "gap_in_cover": "no"}, 409)
    assert "4 days without cover" in gap["detail"]
    assert "gap" in post(client, "/change-requests/CHG-7301/draft", {**READY, "gap_in_cover": "yes"}, 409)["detail"]
    assert "question" in post(client, "/change-requests/CHG-7301/draft", {**READY, "next_step": "ask_the_requester"}, 409)["detail"]
    assert post(client, "/change-requests/CHG-7301/draft", {**READY, "next_step": "make the change"}, 422)["applied"] is False
    for n in (7301, 7303, 7306):
        assert chg(client, n)["drafts_on_file"] == 0
    ok = post(client, "/change-requests/CHG-7303/draft", {"next_step": "Refer to underwriting", "rules_that_apply": ["sr-3"], "summary": "25.00 percent."})
    assert ok["draft"]["rules_that_apply"] == ["SR-3"] and ok["draft"]["next_step"] == "refer_to_underwriting"


def test_a_draft_endorsement_uses_the_template_of_the_change_and_adds_nothing_to_the_policy(client, store):
    templates = get(client, "/endorsement-templates")
    assert [t["template_id"] for t in templates["items"]] == ["ET-ADDRESS", "ET-VEHICLE", "ET-SUM-INSURED", "ET-DRIVER", "ET-CANCELLATION"]
    assert all([p["number"] for p in t["paragraphs"]] == ["1", "2", "3", "4"] for t in templates["items"])
    assert [t["template_id"] for t in get(client, "/endorsement-templates?change_type=vehicle")["items"]] == ["ET-VEHICLE"]
    body = {"template_id": "ET-VEHICLE", "endorsement_text": "ENDORSEMENT to policy POL-2803."}
    saved = post(client, "/change-requests/CHG-7307/endorsement", body)
    assert saved["draft"]["version"] == 1 and saved["draft"]["effective_date"] == "2026-12-01"
    assert saved["draft"]["premium_adjustment_by_the_system"]["amount"] == 73.0
    wrong = post(client, "/change-requests/CHG-7307/endorsement", {**body, "template_id": "ET-ADDRESS"}, 409)
    assert "use ET-VEHICLE" in wrong["detail"] and "Nothing was saved" in wrong["detail"]
    assert "not an endorsement template" in post(client, "/change-requests/CHG-7307/endorsement", {**body, "template_id": "ET-NONE"}, 409)["detail"]
    late = post(client, "/change-requests/CHG-7307/endorsement", {**body, "effective_date": "2026-12-02"}, 409)
    assert "1 Dec 2026" in late["detail"]
    c = chg(client, 7307)
    assert "endorsement_drafts" not in c and (c["endorsement_drafts_on_file"], c["change_drafts_on_file"]) == (1, 0)
    assert len(get(client, "/change-requests/CHG-7307/endorsement-drafts")["items"]) == 1
    policy = store.data["sv_policies"]["POL-2803"]
    assert policy["endorsements"] == [] and policy["schedule"]["registration"] == "MR-2291-C"


# ---------------------------------------------------------------- a policy on a date, and certificates
def test_a_policy_as_it_stands_shows_the_limit_that_held_on_the_date(client):
    early = get(client, "/policies/POL-2822/as-it-stands?on=2026-10-12")
    assert early["schedule_on_the_date"]["contents_sum_insured"] == 35000.0 and early["endorsements_in_effect"] == []
    assert [e["endorsement_id"] for e in early["endorsements_not_yet_in_effect"]] == ["END-2822-1"]
    assert early["not_yet_applied"] == ["END-2822-1 takes effect on 27 Oct 2026, after 12 Oct 2026: it is not applied."]
    on_the_day = get(client, "/policies/POL-2822/as-it-stands?on=2026-10-27")
    assert on_the_day["schedule_on_the_date"]["contents_sum_insured"] == 50000.0
    now = get(client, "/policies/POL-2822/as-it-stands")
    assert now["on"] == TODAY and now["schedule_on_the_date"]["contents_sum_insured"] == 50000.0
    change = now["changed_by_endorsement"][0]
    assert (change["field"], change["from"], change["to"], change["endorsement_id"], change["effective"]) == \
        ("contents_sum_insured", 35000.0, 50000.0, "END-2822-1", "2026-10-27")
    held = get(client, "/policies/POL-2008/as-it-stands")
    assert held["held_in"] == "the policy system" and [e["endorsement_id"] for e in held["endorsements_in_effect"]] == ["END-2008-1"]
    assert held["annual_premium"] == 610.0 and held["waiver_of_rights_of_recovery"]["held"] is False
    assert get(client, "/policies/POL-2821/as-it-stands")["interested_parties"] == ["Otterbank Home Loans Ltd"]
    assert "No policy with id POL-9999" in get(client, "/policies/POL-9999/as-it-stands", 404)["detail"]
    assert get(client, "/policies/POL-2822/as-it-stands?on=12-10-2026", 422)["applied"] is False


def test_the_certificate_template_is_numbered_text(client):
    t = get(client, "/certificate-template")
    assert t["template_id"] == "CT-COI-1" and [p["number"] for p in t["paragraphs"]] == [str(n) for n in range(1, 8)]
    assert "gives the certificate holder no rights" in t["paragraphs"][6]["text"]


def test_crq_7401_and_7402_are_clean(client):
    one = crq(client, 7401)
    assert (one["policy_id"], one["certificate_date"], one["certificate_holder"]["name"]) == ("POL-2002", "2026-11-26", "Weavers Yard Mutual Loan Society")
    assert one["checked_against_the_policy"]["can_be_prepared_as_asked"] is True and one["checked_against_the_policy"]["differences"] == []
    assert (rows_of(one)["CRQ-7401-A"]["result"], rows_of(one)["CRQ-7401-A"]["the_policy_holds"]) == ("shown_from_the_policy", 310000.0)
    assert (one["policy_as_it_stands_on_the_certificate_date"]["period_start"], one["policy_as_it_stands_on_the_certificate_date"]["period_end"]) == \
        ("2026-06-29", "2027-06-28")
    two = crq(client, 7402)
    row = rows_of(two)["CRQ-7402-A"]
    assert (two["policy_id"], row["result"], row["asked"], row["the_policy_holds"]) == ("POL-2014", "matches_the_policy", 1000000.0, 1000000.0)
    assert two["checked_against_the_policy"]["can_be_prepared_as_asked"] is True


def test_crq_7403_asks_for_a_limit_higher_than_the_policy_holds(client):
    r = crq(client, 7403)
    row = rows_of(r)["CRQ-7403-A"]
    assert (r["policy_id"], row["result"], row["asked"], row["the_policy_holds"]) == ("POL-2001", "higher_than_the_policy", 2000000.0, 1000000.0)
    assert "USD 1,000,000.00 higher than the policy" in row["sentence"]
    check = r["checked_against_the_policy"]
    assert check["can_be_prepared_as_asked"] is False and check["differences"] == [row["sentence"]]


def test_crq_7404_names_a_party_that_is_not_on_the_policy(client):
    r = crq(client, 7404)
    rows = rows_of(r)
    assert r["policy_id"] == "POL-2821" and rows["CRQ-7404-A"]["result"] == "shown_from_the_policy" and rows["CRQ-7404-A"]["the_policy_holds"] == 225000.0
    assert rows["CRQ-7404-B"]["result"] == "not_on_the_policy" and rows["CRQ-7404-B"]["the_policy_holds"] == ["Otterbank Home Loans Ltd"]
    assert r["checked_against_the_policy"]["can_be_prepared_as_asked"] is False and len(r["checked_against_the_policy"]["differences"]) == 1


def test_crq_7405_asks_for_a_date_after_the_policy_period_ends(client):
    r = crq(client, 7405)
    cover = rows_of(r)["COVER"]
    assert (r["policy_id"], r["certificate_date"], cover["result"]) == ("POL-2012", "2027-05-25", "not_in_force_on_the_date")
    assert cover["sentence"] == "The policy period ends on 9 May 2027 and no renewal is on record. 25 May 2027 is 16 days after the end."
    assert r["checked_against_the_policy"]["can_be_prepared_as_asked"] is False


def test_crq_7405_the_item_row_gives_no_figure_for_a_date_outside_the_period(client):
    check = crq(client, 7405)["checked_against_the_policy"]
    row = {r["item_id"]: r for r in check["rows"]}["CRQ-7405-A"]
    assert (row["result"], row["the_policy_holds"], row["field"]) == ("not_in_force_on_the_date", None, "buildings_sum_insured")
    assert row["sentence"] == "The policy is not in force on 25 May 2027, so it gives nothing to show for this item on that date."
    assert "298" not in json.dumps(check) and len(check["differences"]) == 1
    inside = {r["item_id"]: r for r in crq(client, 7401)["checked_against_the_policy"]["rows"]}["CRQ-7401-A"]
    assert inside["result"] == "shown_from_the_policy" and inside["the_policy_holds"] == 310000.0


def test_crq_7406_the_certificate_date_decides_which_limit_shows(client):
    r = crq(client, 7406)
    row = rows_of(r)["CRQ-7406-A"]
    assert (r["policy_id"], r["certificate_date"], row["result"], row["the_policy_holds"]) == ("POL-2822", "2026-10-12", "shown_from_the_policy", 35000.0)
    assert r["checked_against_the_policy"]["can_be_prepared_as_asked"] is True
    stands = r["policy_as_it_stands_on_the_certificate_date"]
    assert stands["schedule_on_the_date"]["contents_sum_insured"] == 35000.0 and stands["endorsements_in_effect"] == []
    assert "50,000.00" not in row["sentence"]


def test_crq_7407_asks_for_a_waiver_the_wording_does_not_hold(client):
    r = crq(client, 7407)
    rows = rows_of(r)
    assert r["policy_id"] == "POL-2011" and rows["CRQ-7407-A"]["the_policy_holds"] == 19500.0
    assert rows["CRQ-7407-B"]["result"] == "not_on_the_policy" and "TMI-MOT-01 holds no waiver" in rows["CRQ-7407-B"]["sentence"]
    assert r["checked_against_the_policy"]["can_be_prepared_as_asked"] is False


def test_a_draft_certificate_is_versioned_and_issues_nothing(client, store):
    before = copy.deepcopy({k: v for k, v in store.data.items() if k != "sv_certificate_requests"})
    first = post(client, "/certificate-requests/CRQ-7406/certificate", {**CERT, "next_step": "Ready for the servicing officer"})
    second = post(client, "/certificate-requests/CRQ-7406/certificate", CERT)
    assert (first["draft"]["version"], second["draft"]["version"]) == (1, 2) and first["draft"]["certificate_date"] == "2026-10-12"
    assert first["draft"]["checked_by_the_system"] == {"can_be_prepared_as_asked": True, "differences": []}
    r = crq(client, 7406)
    assert "certificate_drafts" not in r and r["drafts_on_file"] == 2 and r["status"] == "received"
    assert "CERTIFICATE OF INSURANCE." not in json.dumps(r)
    assert all("certificate_drafts" not in x for x in get(client, "/certificate-requests")["items"])
    assert len(get(client, "/certificate-requests/CRQ-7406/drafts")["items"]) == 2
    assert {k: v for k, v in store.data.items() if k != "sv_certificate_requests"} == before


def test_a_draft_certificate_is_refused_when_it_goes_against_the_systems_check(client):
    yes = post(client, "/certificate-requests/CRQ-7403/certificate", CERT, 409)
    assert "USD 1,000,000.00 higher than the policy" in yes["detail"] and "Nothing was saved" in yes["detail"]
    assert "cannot be prepared as asked" in post(client, "/certificate-requests/CRQ-7403/certificate",
                                                 {**CANNOT, "next_step": "ready_for_the_servicing_officer"}, 409)["detail"]
    assert "says can_be_prepared_as_asked is yes" in post(client, "/certificate-requests/CRQ-7401/certificate", CANNOT, 409)["detail"]
    assert "certificate text is needed" in post(client, "/certificate-requests/CRQ-7401/certificate", {**CERT, "certificate_text": ""}, 409)["detail"]
    assert post(client, "/certificate-requests/CRQ-7401/certificate", {**CERT, "next_step": "issue"}, 422)["applied"] is False
    assert crq(client, 7403)["drafts_on_file"] == 0 and crq(client, 7401)["drafts_on_file"] == 0
    for n in (7403, 7404, 7405, 7407):
        saved = post(client, f"/certificate-requests/CRQ-{n}/certificate", CANNOT)
        assert saved["draft"]["checked_by_the_system"]["can_be_prepared_as_asked"] is False


# ---------------------------------------------------------------- the broker desk
def test_brokers_are_records_and_only_get_broker_gives_a_book(client):
    brokers = get(client, "/brokers")["items"]
    assert [(b["broker_id"], b["name"], b["policies_placed_count"]) for b in brokers] == [
        ("BRK-7501", "Pennywhistle & Crane Insurance Brokers", 3), ("BRK-7502", "Marlow Lantern Brokers Ltd", 2),
        ("BRK-7503", "Thistle & Wren Broking", 2)]
    assert all("policies_placed" not in b and "call_back_requests" not in b for b in brokers)
    books = {n: {p["policy_id"]: p["claims"] for p in get(client, f"/brokers/BRK-{n}")["policies_placed"]} for n in (7501, 7502, 7503)}
    assert books == {7501: {"POL-2009": ["CLM-4009"], "POL-2010": ["CLM-4010"], "POL-2811": ["SCL-7801"]},
                     7502: {"POL-2812": ["SCL-7802"], "POL-2813": ["SCL-7803"]}, 7503: {"POL-2814": ["SCL-7804"], "POL-2822": []}}
    queries = get(client, "/broker-queries")["items"]
    assert [q["query_id"] for q in queries] == [f"BQ-76{n:02d}" for n in range(1, 9)]
    assert [q["query_id"] for q in get(client, "/broker-queries?broker_id=BRK-7503")["items"]] == ["BQ-7603", "BQ-7606"]


def test_the_book_check_says_yes_or_no_and_names_no_other_broker(client):
    assert get(client, "/brokers/BRK-7502/book-check?claim_id=SCL-7803")["in_book"] is True
    no = get(client, "/brokers/BRK-7503/book-check?claim_id=SCL-7803")
    assert no["in_book"] is False and "Marlow Lantern" not in json.dumps(no) and "Ashcombe" not in json.dumps(no)
    assert get(client, "/brokers/BRK-7501/book-check?policy_id=POL-2009")["in_book"] is True
    assert get(client, "/brokers/BRK-7502/book-check?policy_id=POL-2009")["in_book"] is False
    assert get(client, "/brokers/BRK-7501/book-check?policy_id=POL-2001")["in_book"] is False
    assert get(client, "/brokers/BRK-7501/book-check?policy_id=POL-9999")["in_book"] is False
    assert "Nothing was checked" in get(client, "/brokers/BRK-7501/book-check", 409)["detail"]


def test_bq_7601_a_clean_status_gives_the_stage_what_is_outstanding_and_the_last_payment(client):
    s = get(client, "/brokers/BRK-7501/claims/SCL-7801")
    assert (s["policy_id"], s["policyholder"], s["stage"]) == ("POL-2811", "Jocasta Wimberry", "part_paid")
    assert s["what_is_outstanding"] == ["The repairer's final invoice."]
    assert s["last_payment"] == {"date": "2026-11-19", "amount": 1800.0, "paid_to": "Harbour Lane Coachworks"}
    assert s["last_payment_note"] == "The last payment was USD 1,800.00 on 19 Nov 2026." and s["source"] == "Claim SCL-7801, held in this system."


def test_bq_7602_a_broker_reads_its_own_clients_policy(client):
    p = get(client, "/brokers/BRK-7501/policies/POL-2009")
    assert p["holder"] == "Teodor Brackwell" and p["cover_on_the_date"]["in_force"] is True
    assert (p["period_start"], p["period_end"], p["schedule_on_the_date"]["deductible"]) == ("2026-03-31", "2027-03-30", 300.0)
    assert p["claims_on_the_policy"] == ["CLM-4009"] and "placed_by_broker" not in p


def test_bq_7603_and_7608_another_brokers_client_is_refused_by_the_read_itself(client):
    claim = get(client, "/brokers/BRK-7503/claims/SCL-7803", 403)
    assert claim["detail"] == ("SCL-7803 is not in the book of Thistle & Wren Broking (BRK-7503). A broker is told nothing about a policy "
                               "or a claim that is not its own client's. Nothing was read out.")
    assert not any(word in json.dumps(claim) for word in ("Ashcombe", "POL-2813", "plumber", "waiting"))
    policy = get(client, "/brokers/BRK-7502/policies/POL-2009", 403)
    assert "POL-2009 is not in the book of Marlow Lantern Brokers Ltd (BRK-7502)" in policy["detail"]
    assert not any(word in json.dumps(policy) for word in ("Brackwell", "Millpond", "285"))
    assert get(client, "/brokers/BRK-7501/claims/CLM-9999", 403)["detail"].startswith("CLM-9999 is not in the book")
    assert get(client, "/brokers/BRK-7501/policies/POL-2001", 403)["applied"] is False
    assert get(client, "/brokers/BRK-7501/claims/CLM-4001", 403)["applied"] is False
    assert "No broker with id BRK-9999" in get(client, "/brokers/BRK-9999/claims/SCL-7801", 404)["detail"]


def test_bq_7604_the_reserve_is_held_back(client, store):
    s = get(client, "/brokers/BRK-7502/claims/SCL-7803")
    assert s["stage"] == "waiting_for_documents" and s["what_is_outstanding"] == ["The plumber's report on where the water came from."]
    assert s["last_payment"] is None and s["last_payment_note"] == "No payment is recorded."
    assert store.data["sv_claims"]["SCL-7803"]["reserve"] == 6200.0
    blob = json.dumps(s)
    assert "6200" not in blob and "6,200" not in blob and "Reserve set" not in blob and "internal_notes" not in blob
    assert s["held_back"][0] == "the reserve and any estimate of what the claim will cost"


def test_bq_7605_a_claim_under_an_internal_referral_reads_as_under_review_and_nothing_more(client, store):
    assert store.data["sv_claims"]["SCL-7802"]["internal_referral"]["to"] == "the investigations desk"
    s = get(client, "/brokers/BRK-7502/claims/SCL-7802")
    assert (s["stage"], s["stage_in_words"], s["what_is_outstanding"], s["last_payment"]) == ("under_review", "The claim is under review.", [], None)
    blob = json.dumps(s).lower()
    for word in ("fraud", "investigat", "fi-1", "thirlby", "9500", "9,500", "receipts", "indicator"):
        assert word not in blob, word
    plain = get(client, "/brokers/BRK-7503/claims/SCL-7804")
    same = ("stage", "stage_in_words", "what_is_outstanding", "outstanding_note", "last_payment", "last_payment_note", "decision", "held_back",
            "anything_else")
    assert {k: s[k] for k in same} == {k: plain[k] for k in same} and set(s) == set(plain)


def test_bq_7606_the_records_are_silent_so_a_call_back_is_saved_as_a_draft(client, store):
    s = get(client, "/brokers/BRK-7503/claims/SCL-7804")
    assert s["stage"] == "under_review" and "adjuster" not in json.dumps(s).lower() and "call-back request" in s["anything_else"]
    before = copy.deepcopy({k: v for k, v in store.data.items() if k != "sv_brokers"})
    body = {"claim_id": "scl-7804", "question": "On what date will the loss adjuster visit?",
            "why_the_records_do_not_settle_it": "The record holds no date of a visit."}
    first = post(client, "/brokers/BRK-7503/call-backs", body)
    second = post(client, "/brokers/BRK-7503/call-backs", {"question": "Please call about renewal terms."})
    assert first["kind"] == "draft" and (first["draft"]["version"], first["draft"]["call_back_id"], first["draft"]["claim_id"]) == (1, "CBK-7503-1", "SCL-7804")
    assert (second["draft"]["version"], second["draft"]["call_back_id"]) == (2, "CBK-7503-2")
    assert "No call is booked and no time is promised" in first["message"]
    b = get(client, "/brokers/BRK-7503")
    assert "call_back_requests" not in b and b["call_back_requests_on_file"] == 2
    assert len(get(client, "/brokers/BRK-7503/call-backs")["items"]) == 2 and get(client, "/brokers/BRK-7501/call-backs")["items"] == []
    assert {k: v for k, v in store.data.items() if k != "sv_brokers"} == before
    refused = post(client, "/brokers/BRK-7503/call-backs", {"claim_id": "SCL-7803", "question": "Where does it stand?"}, 403)
    assert "not in the book" in refused["detail"]
    assert post(client, "/brokers/BRK-7503/call-backs", {"policy_id": "POL-2009", "question": "Is it in force?"}, 403)["applied"] is False
    assert post(client, "/brokers/BRK-7503/call-backs", {}, 422)["applied"] is False
    assert get(client, "/brokers/BRK-7503")["call_back_requests_on_file"] == 2


def test_bq_7607_a_recorded_decision_is_read_from_the_claims_system_as_it_stands(client, store):
    s = get(client, "/brokers/BRK-7501/claims/CLM-4010")
    assert s["stage"] == "decided" and s["source"] == "Claim CLM-4010, held in the claims system."
    assert s["decision"] == {"decision": "declined", "decided_on": "2026-11-20", "clause": "2.2",
                             "reason": "The home had been unoccupied for 74 days in a row when the loss happened."}
    assert s["stage_in_words"].startswith("The claim was declined on 20 Nov 2026 under clause 2.2")
    assert "working abroad" not in json.dumps(s) and "11200" not in json.dumps(s)
    open_claim = get(client, "/brokers/BRK-7501/claims/CLM-4009")
    assert (open_claim["stage"], open_claim["last_payment"], open_claim["decision"]) == ("under_review", None, None)
    store.data["claims"]["CLM-4009"]["payments"].append({"amount": 5100.0, "paid_on": "2026-11-26"})
    store.data["claims"]["CLM-4009"]["status"] = "closed"
    paid = get(client, "/brokers/BRK-7501/claims/CLM-4009")
    assert paid["stage"] == "paid" and paid["last_payment"]["amount"] == 5100.0 and paid["last_payment"]["date"] == "2026-11-26"


# ---------------------------------------------------------------- unknown ids, reset and counts
def test_an_unknown_servicing_id_is_a_plain_404(client):
    for path, words in (("/change-requests/CHG-9999", "No change request with id CHG-9999"),
                        ("/certificate-requests/CRQ-9999", "No certificate request with id CRQ-9999"),
                        ("/brokers/BRK-9999", "No broker with id BRK-9999"), ("/change-requests/CHG-9999/drafts", "No change request"),
                        ("/policies/POL-9999/gap-in-cover?new_cover_starts_on=2026-12-01", "No policy with id POL-9999")):
        body = get(client, path, 404)
        assert words in body["detail"] and body["applied"] is False
    assert client.post("/servicing/change-requests/CHG-9999/draft", headers=H, json=READY).status_code == 404
    assert client.post("/servicing/certificate-requests/CRQ-9999/certificate", headers=H, json=CERT).status_code == 404


def test_putting_the_servicing_system_back_leaves_the_claims_system_alone_and_the_other_way_round(client, store):
    triage = {"rule_id": "HG-3", "track": "fast track", "team": "fast-track team", "severity": "low", "reason": "Estimate under 2,500."}
    client.post("/claims/claims/CLM-4001/triage", headers=H, json=triage)
    post(client, "/change-requests/CHG-7301/draft", READY)
    post(client, "/certificate-requests/CRQ-7401/certificate", CERT)
    post(client, "/brokers/BRK-7501/call-backs", {"question": "Please call."})
    changed = client.get("/admin/state", headers=H).json()["changed_by"]
    assert changed["claims"] == ["claims"] and changed["servicing"] == ["sv_brokers", "sv_certificate_requests", "sv_change_requests"]
    fresh = build_all(TODAY_D)
    assert client.post("/admin/reset/claims", headers=H).json()["put_back"] == ["claims"]
    assert len(store.data["sv_change_requests"]["CHG-7301"]["change_drafts"]) == 1
    client.post("/claims/claims/CLM-4001/triage", headers=H, json=triage)
    back = client.post("/admin/reset/servicing", headers=H).json()
    assert back["put_back"] == ["sv_brokers", "sv_certificate_requests", "sv_change_requests"]
    assert all(store.data[name] == fresh[name] for name in SV_SETS)
    assert len(store.data["claims"]["CLM-4001"]["triage_drafts"]) == 1
    client.post("/admin/reset", headers=H)
    assert store.data == fresh


def test_the_counts_name_the_open_items_of_the_servicing_system(client):
    counts = client.get("/admin/state", headers=H).json()["counts"]
    assert (counts["change_requests_received"], counts["certificate_requests_received"], counts["broker_call_back_requests_saved"]) == (8, 7, 0)


def test_every_id_in_the_servicing_section_of_the_scenarios_is_in_the_data():
    from pathlib import Path
    text = (Path(__file__).resolve().parent.parent / "SCENARIOS.md").read_text(encoding="utf-8")
    section = text.split("## Servicing (system: servicing)")[1].split("\n## ")[0]
    data = build_all(TODAY_D)
    held = set(data["policies"]) | set(data["claims"])
    for name in SV_SETS:
        if isinstance(data[name], dict):
            held |= set(data[name])
    held |= {e["endorsement_id"] for p in data["sv_policies"].values() for e in p["endorsements"]}
    held |= {c["rating"]["quote_id"] for c in data["sv_change_requests"].values() if c["rating"]}
    named = set(re.findall(r"\b(?:CHG-\d{4}|CRQ-\d{4}|BRK-\d{4}|BQ-\d{4}|SCL-\d{4}|CLM-\d{4}|POL-2\d{3}|SR-\d|RQ-\d{4}|END-\d{4}-\d|ET-[A-Z-]+[A-Z]|CT-COI-1)\b",
                           section))
    assert len(named) > 60 and named <= held, sorted(named - held)
    assert chr(8212) not in section
