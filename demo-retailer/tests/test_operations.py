"""Every operation, the planted faults read back through the API, and each 404 and 409 path."""

import json

import pytest

from bodies_1_3 import CALLS_1_3
from bodies_1_4 import CALLS_1_4
from conftest import ALL_SYSTEMS, H

PERIOD = "2026-10"
FS = "/foodsafety"


def get(client, path, _expect=200, **params):
    r = client.get(path, headers=H, params=params)
    assert r.status_code == _expect, (path, r.status_code, r.text[:400])
    return r.json()


def post(client, path, body=None, status=200):
    r = client.post(path, json=body if body is not None else {}, headers=H)
    assert r.status_code == status, (path, r.status_code, r.text[:400])
    return r.json()


# ---------------------------------------------------------------- every operation at least once

DRAFT_CHECK = {"rows": [{"unit_or_check": "Freezers", "plan_section": "2.2", "limit": "−18.0 °C or colder",
                         "readings": [{"date": "2026-10-11", "value": -15.5}], "mark": "outside_limit"}],
               "proposed_next_step": "ask_for_corrective_actions"}
ANALYSIS = {"period": PERIOD, "themes": [{"name": "late delivery", "count": 78, "counts_by_site": {"R-047": 36},
                                          "quoted_references": ["GF-2610-0001"]}], "harm_comments": []}
MATCH = {"lines": [{"field": "price", "item": "Pizza flour, 25 kg bag", "invoice_says": "46.00", "order_says": "44.50",
                    "received": "600 bags", "mark": "price_differs", "net_difference": 900.0}],
         "proposed_next_step": "query_the_supplier"}

VISIT_REPORT = {"findings": [{"standard": "BS-3.2", "source": "checklist", "checklist_item": 6,
                              "what_was_found": "Toilet check sheet last signed at 11:00."}], "to_clarify": []}
LEASE_SUMMARY = {"term": {"start_date": "2022-07-01", "end_date": "2032-06-30", "clause": "2.1"},
                 "rent": {"annual_rent": 412000, "clause": "3.1"},
                 "repair_duties": [{"party": "tenant", "duty": "the whole of the premises", "clause": "6.1"}]}
PERFORMANCE_REVIEW = {"departures": [{"measure": "sales", "compared_with": "plan", "direction": "below", "actual": 148150,
                                      "compared_to": 182000, "difference_pct": -18.6}]}
TILL_AUDIT = {"rows": [{"row_id": "TR-2610-0016", "rules": ["TC-1"]}]}

CALLS = {
    "list_sites": ("get", "/stores/sites", None),
    "get_site": ("get", "/stores/sites/R-014", None),
    "list_site_visits": ("get", "/stores/visits", None),
    "get_site_visit": ("get", "/stores/visits/SV-2610-01", None),
    "save_visit_report": ("post", "/stores/visits/SV-2610-01/report", VISIT_REPORT),
    "list_leases": ("get", "/property/leases", None),
    "get_lease": ("get", "/property/leases/LS-2001", None),
    "save_lease_summary": ("post", "/property/leases/LS-2001/summary", LEASE_SUMMARY),
    "list_performance_periods": ("get", "/performance/periods", None),
    "get_restaurant_performance": ("get", f"/performance/restaurants/R-047/{PERIOD}", None),
    "get_peer_group_performance": ("get", f"/performance/restaurants/R-047/{PERIOD}/peer-group", None),
    "save_performance_review": ("post", f"/performance/restaurants/R-047/{PERIOD}/review", PERFORMANCE_REVIEW),
    "get_till_rules": ("get", "/tills/rules", None),
    "list_till_entries": ("get", "/tills/entries", None),
    "get_till_audit": ("get", f"/tills/audits/{PERIOD}", None),
    "save_till_audit": ("post", f"/tills/audits/{PERIOD}", TILL_AUDIT),
    "get_food_safety_plan": ("get", f"{FS}/plan", None),
    "list_record_periods": ("get", f"{FS}/records", None),
    "get_food_safety_records": ("get", f"{FS}/records/R-014/{PERIOD}", None),
    "get_record_review": ("get", f"{FS}/reviews/R-014/{PERIOD}", None),
    "save_record_check": ("post", f"{FS}/reviews/R-031/{PERIOD}/checks", DRAFT_CHECK),
    "request_corrective_actions": ("post", f"{FS}/reviews/R-031/{PERIOD}/corrective-actions/request",
                                   {"requested_by": "A. Reviewer", "note": "Please answer for the freezer."}),
    "record_corrective_action": ("post", f"{FS}/reviews/R-031/{PERIOD}/corrective-actions",
                                 {"unit_or_check": "Freezers", "what_was_done": "Food moved, freezer serviced.",
                                  "done_by": "R. Manager", "done_on": "2026-10-13"}),
    "sign_monthly_review": ("post", f"{FS}/reviews/R-031/{PERIOD}/sign", {"signed_by": "B. Teague"}),
    "list_guest_feedback": ("get", "/care/feedback", None),
    "get_guest_feedback": ("get", "/care/feedback/GF-2610-0001", None),
    "get_feedback_analysis": ("get", f"/care/analysis/{PERIOD}", None),
    "save_feedback_analysis": ("post", "/care/analysis", ANALYSIS),
    "list_suppliers": ("get", "/purchasing/suppliers", None),
    "get_supplier": ("get", "/purchasing/suppliers/SUP-301", None),
    "list_purchase_orders": ("get", "/purchasing/purchase-orders", None),
    "get_purchase_order": ("get", "/purchasing/purchase-orders/PO-450131", None),
    "list_goods_receipts": ("get", "/purchasing/goods-receipts", None),
    "list_supplier_invoices": ("get", "/purchasing/invoices", None),
    "get_supplier_invoice": ("get", "/purchasing/invoices/INV-77102", None),
    "save_invoice_match": ("post", "/purchasing/invoices/INV-77102/match", MATCH),
    "approve_invoice_for_payment": ("post", "/purchasing/invoices/INV-77102/approve", {"approved_by": "C. Payer"}),
    "raise_invoice_query": ("post", "/purchasing/invoices/INV-5120/query",
                            {"raised_by": "C. Payer", "message": "Please explain 800 kg against 720 kg."}),
    # version 1.2: every change comes after the draft it needs
    "list_customer_tickets": ("get", "/care/tickets", None),
    "get_customer_ticket": ("get", "/care/tickets/CT-2611-001", None),
    "search_help_articles": ("get", "/care/help-articles?q=delivery", None),
    "search_past_cases": ("get", "/care/past-cases", None),
    "save_ticket_reply": ("post", "/care/tickets/CT-2611-001/reply",
                          {"answer_status": "answered_from_articles", "reply": "Standard delivery costs USD 4.95.",
                           "articles_cited": ["HA-01"], "proposed_next_step": "send_reply"}),
    "send_ticket_reply": ("post", "/care/tickets/CT-2611-001/send", {"sent_by": "D. Carer"}),
    "list_complaints": ("get", "/care/complaints", None),
    "get_complaint": ("get", "/care/complaints/CM-2611-01", None),
    "get_complaints_procedure": ("get", "/care/complaints-procedure", None),
    "save_complaint_classification": ("post", "/care/complaints/CM-2611-01/classification",
                                      {"classification": "service_failure", "procedure_section": "2.3",
                                       "response_due": "2026-12-02", "what_happened": "The order is late."}),
    "save_complaint_response": ("post", "/care/complaints/CM-2611-01/response",
                                {"response": "Thank you for writing.", "proposed_next_step": "send_response"}),
    "send_complaint_response": ("post", "/care/complaints/CM-2611-01/send", {"sent_by": "E. Lead"}),
    "list_public_reviews": ("get", "/care/reviews", None),
    "get_public_review": ("get", "/care/reviews/PR-2611-01", None),
    "save_review_reply": ("post", "/care/reviews/PR-2611-01/reply", {"action": "reply", "reply": "Thank you, harbourwalker22."}),
    "publish_review_reply": ("post", "/care/reviews/PR-2611-01/publish", {"published_by": "E. Lead"}),
    "list_delivery_notes": ("get", "/purchasing/delivery-notes", None),
    "get_delivery_note": ("get", "/purchasing/delivery-notes/DN-4135", None),
    "save_discrepancy_claim": ("post", "/purchasing/delivery-notes/DN-4135/claim",
                               {"lines": [{"kind": "short_delivery", "item": "Mozzarella, shredded", "note_says": "500 kg",
                                           "received": "300 kg", "quantity_claimed": 200, "unit": "kg", "amount_claimed": 4900.0}],
                                "proposed_next_step": "send_claim", "message": "200 kg were not received."}),
    "send_discrepancy_claim": ("post", "/purchasing/delivery-notes/DN-4135/claim/send", {"sent_by": "F. Receiver"}),
    "list_supplier_payments": ("get", "/purchasing/payments", None),
    "get_supplier_payment": ("get", "/purchasing/payments/PAY-7003", None),
    "list_supplier_questions": ("get", "/purchasing/supplier-questions", None),
    "get_supplier_question": ("get", "/purchasing/supplier-questions/SQ-2611-01", None),
    "save_supplier_reply": ("post", "/purchasing/supplier-questions/SQ-2611-01/reply",
                            {"answer_status": "answered_from_records", "reply": "Paid on 2026-11-10.",
                             "records_cited": ["PAY-7003"], "proposed_next_step": "send_reply"}),
    "send_supplier_reply": ("post", "/purchasing/supplier-questions/SQ-2611-01/send", {"sent_by": "C. Payer"}),
    "search_orders": ("get", "/orders/orders", None),
    "get_order": ("get", "/orders/orders/RM-58162", None),
    "get_delivery_scans": ("get", "/orders/orders/RM-58162/scans", None),
    "get_returns_policy": ("get", "/orders/returns-policy", None),
    "list_return_requests": ("get", "/orders/returns", None),
    "get_return_request": ("get", "/orders/returns/RR-2611-01", None),
    "save_return_assessment": ("post", "/orders/returns/RR-2611-01/assessment",
                               {"conditions": [{"condition": "1.1", "result": "met"}], "proposed_decision": "approve",
                                "refund_amount": 64.0}),
    "approve_return": ("post", "/orders/returns/RR-2611-01/approve", {"approved_by": "G. Leader"}),
    "refuse_return": ("post", "/orders/returns/RR-2611-02/refuse", {"refused_by": "G. Leader", "reason": "Outside the window."}),
    "list_flagged_orders": ("get", "/orders/flagged", None),
    "get_customer_order_history": ("get", "/orders/customers/C-4020/history", None),
    "save_fraud_review": ("post", "/orders/flagged/RM-58192/review",
                          {"signals": [{"signal": "device", "departs_from_pattern": True, "what_the_record_shows": "A new device."}],
                           "proposed_decision": "hold", "explanation": "The device is new."}),
    "hold_flagged_order": ("post", "/orders/flagged/RM-58192/hold", {"held_by": "H. Reviewer", "reason": "To be checked."}),
    "release_flagged_order": ("post", "/orders/flagged/RM-58196/release", {"released_by": "H. Reviewer"}),
}
# version 1.3: the catalogue, stock, pricing and loyalty systems, each change after the draft it needs
CALLS.update(CALLS_1_3)
# version 1.4: the people and franchise systems, and the shift logs and incident accounts of the stores system
CALLS.update(CALLS_1_4)


def test_every_operation_of_every_system_is_called_once_and_answers_200(client):
    # two changes of version 1.2 need a draft on a second record, saved here so that every operation is called once
    post(client, "/orders/returns/RR-2611-02/assessment", {"conditions": [{"condition": "1.2", "result": "not_met"}],
                                                           "proposed_decision": "refuse"})
    post(client, "/orders/flagged/RM-58196/review", {"signals": [{"signal": "basket_value", "departs_from_pattern": False,
                                                                 "what_the_record_shows": "Two earlier orders of this size."}],
                                                     "proposed_decision": "release", "explanation": "In line with the history."})
    in_document = set()
    for system in ALL_SYSTEMS:
        for item in client.get(f"/{system}/openapi.json").json()["paths"].values():
            for op in item.values():
                in_document.add(op["operationId"])
    assert in_document == set(CALLS)
    # the calls run in this order, so a change comes after the draft it needs
    for name, (method, path, body) in CALLS.items():
        r = client.get(path, headers=H) if method == "get" else client.post(path, json=body, headers=H)
        assert r.status_code == 200, (name, r.status_code, r.text[:300])
        assert r.json()["demo_data"] is True, name
        if method == "post":
            assert r.json()["applied"] is True and r.json()["kind"] in ("draft", "change"), name


# ---------------------------------------------------------------- stores

def test_sites_twenty_with_the_fixed_addresses(client):
    sites = get(client, "/stores/sites")
    assert sites["count"] == 20
    by = {s["site_id"]: s for s in sites["items"]}
    assert [s for s in by if s.startswith("S-")] == [f"S-10{n}" for n in range(1, 9)]
    assert [s for s in by if s.startswith("R-")] == ["R-014", "R-022", "R-031", "R-047", "R-058", "R-063", "R-071", "R-076",
                                                     "R-082", "R-090", "R-104", "R-117"]
    fixed = {"R-014": ("Port Ilvane", "Harbour Street"), "R-022": ("Port Ilvane", "Malting Lane"),
             "R-031": ("Marlow Reach", "Quayside"), "R-047": ("Tallowby", "Kiln Road"),
             "R-058": ("Port Ilvane", "Lantern Square"), "R-063": ("Marlow Reach", "Station Parade")}
    for sid, (town, street) in fixed.items():
        assert (by[sid]["town"], by[sid]["street"]) == (town, street)
    for s in by.values():
        assert set(s) >= {"site_id", "name", "kind", "town", "street", "area", "area_manager", "franchised", "franchisee"}
        assert s["town"] in ("Port Ilvane", "Marlow Reach", "Tallowby") and s["area_manager"]
        assert s["kind"] == ("store" if s["site_id"].startswith("S-") else "restaurant")
        assert (s["franchisee"] != "") == s["franchised"]
    assert sorted(k for k, s in by.items() if s["franchised"]) == ["R-090", "R-104", "R-117"]


def test_sites_filters(client):
    assert get(client, "/stores/sites", kind="store")["count"] == 8
    assert get(client, "/stores/sites", kind="restaurant")["count"] == 12
    assert [s["site_id"] for s in get(client, "/stores/sites", franchised="true")["items"]] == ["R-090", "R-104", "R-117"]
    assert get(client, "/stores/sites", franchised="false")["count"] == 17
    tally = get(client, "/stores/sites", town="tallowby")
    assert tally["count"] > 0 and {s["town"] for s in tally["items"]} == {"Tallowby"}
    both = get(client, "/stores/sites", kind="restaurant", town="Port Ilvane", franchised="false")
    assert [s["site_id"] for s in both["items"]] == ["R-014", "R-022", "R-058", "R-071"]
    assert get(client, "/stores/sites", town="Nowhere")["count"] == 0
    assert client.get("/stores/sites", params={"kind": "warehouse"}, headers=H).status_code == 422


def test_get_site_and_404(client):
    s = get(client, "/stores/sites/R-090")
    assert s["franchised"] is True and s["franchisee"] and s["kind"] == "restaurant"
    r = get(client, "/stores/sites/R-999", 404)
    assert r["applied"] is False and "list_sites" in r["detail"]


# ---------------------------------------------------------------- food safety plan

def test_the_plan_is_version_5_with_the_limits_the_records_are_checked_against(client):
    plan = get(client, f"{FS}/plan")
    assert plan["version"] == "5.0" and plan["effective_date"] == "2026-07-01"
    limits = {x["ref"]: x for x in plan["limits"]}
    assert set(limits) == {"2.1", "2.2", "3.1", "3.2", "4.1", "4.2", "5.1", "5.2"}
    assert (limits["2.1"]["minimum"], limits["2.1"]["maximum"]) == (1.0, 5.0)
    assert limits["2.2"]["maximum"] == -18.0 and limits["3.1"]["minimum"] == 75.0 and limits["3.2"]["minimum"] == 63.0
    assert limits["4.1"]["maximum"] == 5.0 and limits["4.2"]["maximum"] == -15.0
    assert "63.0" in limits["3.2"]["limit"] and limits["3.2"]["unit_or_check"] == "Hot holding cabinet"
    assert limits["3.2"]["how_often"] == "Every two hours while holding food"
    rule = plan["repeat_rule"]
    assert rule["section"] == "6.2" and rule["minimum_readings"] == 3 and "Three or more" in rule["text"]
    assert [x["section"] for x in plan["what_the_plan_does_not_decide"]] == ["1.3", "7.1", "7.2"]
    texts = {c["ref"]: c["text"] for s in plan["sections"] for c in s["clauses"]}
    assert texts["2.3"].startswith("A chiller reading above 5.0")
    assert "judgement" in texts["7.1"] and "Allergen Matrix" in texts["7.2"]
    assert "invented" in plan["notice"]


# ---------------------------------------------------------------- the planted faults, read back

CLEANING = "daily_cleaning_signed_by"


def deviations(client, site_id, period=PERIOD):
    """Every reading outside the plan's limits, found from the plan and the records served by the API."""
    plan = get(client, f"{FS}/plan")
    rec = get(client, f"{FS}/records/{site_id}/{period}")
    found = []
    for lim in plan["limits"]:
        for col in lim["log_columns"]:
            log = rec["delivery_log"] if lim["recorded_in"] == "Delivery log" else rec["temperature_log"]
            for row in log:
                v = row[col]
                if col == CLEANING:
                    if v == "":
                        found.append((col, row["date"], ""))
                elif v == "MISSED":
                    found.append((col, row["date"], "MISSED"))
                elif (lim["minimum"] is not None and v < lim["minimum"]) or (lim["maximum"] is not None and v > lim["maximum"]):
                    found.append((col, row["date"], v))
    return sorted(found)


def d(day):
    return f"{PERIOD}-{day:02d}"


EXPECTED = {
    "R-014": [("make_line_chiller_afternoon_c", d(8), 6.8), ("make_line_chiller_opening_c", d(9), 7.4),
              ("make_line_chiller_afternoon_c", d(21), 6.1), ("hot_holding_16h_c", d(14), 58.5),
              ("hot_holding_18h_c", d(27), 60.2), (CLEANING, d(5), ""), (CLEANING, d(17), ""), (CLEANING, d(26), "")],
    "R-022": [],
    "R-031": [("freezer_opening_c", d(11), -15.5), ("freezer_opening_c", d(12), -14.9), (CLEANING, d(19), "")],
    "R-047": [("hot_holding_14h_c", d(3), 59.0), ("hot_holding_16h_c", d(16), 57.5), ("hot_holding_18h_c", d(16), 61.0),
              ("hot_holding_20h_c", d(24), 60.5)],
    "R-058": [("walk_in_chiller_afternoon_c", d(6), "MISSED"), ("walk_in_chiller_afternoon_c", d(7), "MISSED"),
              ("walk_in_chiller_afternoon_c", d(13), "MISSED"), ("walk_in_chiller_afternoon_c", d(20), "MISSED"),
              (CLEANING, d(13), "")],
    "R-063": [("chilled_item_c", d(13), 6.5)],
}


@pytest.mark.parametrize("site_id", sorted(EXPECTED))
def test_each_restaurant_holds_exactly_its_planted_faults_and_no_others(client, site_id):
    assert deviations(client, site_id) == sorted(EXPECTED[site_id])


def test_the_repeat_rule_applies_to_two_pieces_of_equipment_only(client):
    groups = {"walk_in_chiller": "Walk-in chiller", "make_line_chiller": "Make-line chiller", "freezer": "Freezer",
              "hot_holding": "Hot holding", "chicken_core": "Chicken core"}
    repeated = {}
    for site_id in EXPECTED:
        counts = {}
        for col, _day, value in deviations(client, site_id):
            if value in ("", "MISSED") or col == "chilled_item_c":
                continue
            group = next(g for g in groups if col.startswith(g))
            counts[group] = counts.get(group, 0) + 1
        repeated[site_id] = sorted(g for g, n in counts.items() if n >= 3)
    assert repeated == {"R-014": ["make_line_chiller"], "R-022": [], "R-031": [], "R-047": ["hot_holding"], "R-058": [],
                        "R-063": []}


def test_hot_holding_counts_by_restaurant(client):
    below = {s: sum(1 for c, _, v in deviations(client, s) if c.startswith("hot_holding")) for s in EXPECTED}
    assert below == {"R-014": 2, "R-022": 0, "R-031": 0, "R-047": 4, "R-058": 0, "R-063": 0}


def test_records_shape_one_row_a_day_and_nine_deliveries(client):
    rec = get(client, f"{FS}/records/R-022/{PERIOD}")
    assert rec["site_id"] == "R-022" and rec["period"] == PERIOD
    rows = rec["temperature_log"]
    assert [r["date"] for r in rows] == [d(n) for n in range(1, 32)]
    assert set(rows[0]) == {"date", "walk_in_chiller_opening_c", "walk_in_chiller_afternoon_c", "make_line_chiller_opening_c",
                            "make_line_chiller_afternoon_c", "freezer_opening_c", "hot_holding_12h_c", "hot_holding_14h_c",
                            "hot_holding_16h_c", "hot_holding_18h_c", "hot_holding_20h_c", "chicken_core_first_batch_am_c",
                            "chicken_core_first_batch_pm_c", CLEANING}
    assert all(r[CLEANING] in ("shift manager A", "shift manager B", "closing manager C") for r in rows)
    assert [r["date"] for r in rec["delivery_log"]] == [d(n) for n in (2, 6, 9, 13, 16, 20, 23, 27, 30)]
    assert all(r["outcome"] == "accepted" for r in rec["delivery_log"])
    assert "MISSED" in rec["notes"]


def test_the_chilled_delivery_at_6_5_was_accepted(client):
    row = next(r for r in get(client, f"{FS}/records/R-063/{PERIOD}")["delivery_log"] if r["date"] == d(13))
    assert row["chilled_item_c"] == 6.5 and row["outcome"] == "accepted"


def test_ranges_stay_inside_the_plan_for_every_other_reading(store):
    for rec in store.data["fs_records"].values():
        for row in rec["temperature_log"]:
            for col in ("make_line_chiller_opening_c", "make_line_chiller_afternoon_c"):
                if rec["site_id"] != "R-014":
                    assert 1.0 <= row[col] <= 5.0


# ---------------------------------------------------------------- list_record_periods, 404s

def test_list_record_periods_and_filter(client):
    r = get(client, f"{FS}/records")
    assert r["count"] == 6 and {x["period"] for x in r["items"]} == {PERIOD}
    assert sorted(x["site_id"] for x in r["items"]) == ["R-014", "R-022", "R-031", "R-047", "R-058", "R-063"]
    assert {x["review_status"] for x in r["items"]} == {"not_reviewed"}
    assert all(x["days_recorded"] == 31 and x["deliveries_recorded"] == 9 for x in r["items"])
    one = get(client, f"{FS}/records", site_id="R-031")
    assert [x["site_id"] for x in one["items"]] == ["R-031"] and one["items"][0]["site_name"].startswith("Rowanmere Kitchen")
    assert get(client, f"{FS}/records", site_id="R-071")["count"] == 0


def test_records_and_review_404_and_422(client):
    for path in (f"{FS}/records/R-071/{PERIOD}", f"{FS}/records/R-014/2026-09", f"{FS}/records/S-101/{PERIOD}",
                 f"{FS}/reviews/R-071/{PERIOD}", f"{FS}/reviews/R-014/2026-09"):
        r = get(client, path, 404)
        assert r["applied"] is False and "list_record_periods" in r["detail"], path
    assert client.get(f"{FS}/records/R-014/October", headers=H).status_code == 422
    assert client.get(f"{FS}/records/R-014/2026-13", headers=H).status_code == 422
    post(client, f"{FS}/reviews/R-071/{PERIOD}/sign", {"signed_by": "A"}, 404)
    post(client, f"{FS}/reviews/R-071/{PERIOD}/checks", DRAFT_CHECK, 404)
    post(client, f"{FS}/reviews/R-071/{PERIOD}/corrective-actions/request", {"requested_by": "A", "note": "n"}, 404)
    post(client, f"{FS}/reviews/R-071/{PERIOD}/corrective-actions",
         {"unit_or_check": "u", "what_was_done": "w", "done_by": "b", "done_on": "2026-10-02"}, 404)


# ---------------------------------------------------------------- the review

def test_saving_a_check_is_a_draft_with_versions_and_changes_no_status(client):
    a = post(client, f"{FS}/reviews/R-031/{PERIOD}/checks", {**DRAFT_CHECK, "drafted_by": "tester"})
    assert a["kind"] == "draft" and a["draft"]["version"] == 1 and a["draft"]["drafted_by"] == "tester"
    assert a["draft"]["drafted_at"] and a["review_status"] == "not_reviewed"
    second = {**DRAFT_CHECK, "proposed_next_step": "refer_to_food_safety_lead", "summary": "Second look."}
    b = post(client, f"{FS}/reviews/R-031/{PERIOD}/checks", second)
    assert b["draft"]["version"] == 2 and b["draft"]["drafted_by"] == "agent"
    rev = get(client, f"{FS}/reviews/R-031/{PERIOD}")
    assert rev["status"] == "not_reviewed" and [c["version"] for c in rev["checks"]] == [1, 2]
    assert rev["checks"][0]["rows"][0]["readings"][0]["value"] == -15.5
    assert rev["checks"][1]["proposed_next_step"] == "refer_to_food_safety_lead"
    assert rev["signed_by"] == "" and rev["corrective_actions"] == [] and rev["plan_version"] == "5.0"
    assert get(client, f"{FS}/records", site_id="R-031")["items"][0]["review_status"] == "not_reviewed"


def test_a_check_with_a_bad_mark_or_next_step_or_no_rows_is_refused(client):
    path = f"{FS}/reviews/R-031/{PERIOD}/checks"
    bad_mark = {**DRAFT_CHECK, "rows": [{**DRAFT_CHECK["rows"][0], "mark": "bad"}]}
    assert client.post(path, json=bad_mark, headers=H).status_code == 422
    assert client.post(path, json={**DRAFT_CHECK, "proposed_next_step": "sign_it"}, headers=H).status_code == 422
    assert client.post(path, json={**DRAFT_CHECK, "rows": []}, headers=H).status_code == 422
    r = client.post(path, json={"rows": DRAFT_CHECK["rows"]}, headers=H)
    assert r.status_code == 422 and "proposed_next_step" in r.json()["detail"]
    assert get(client, f"{FS}/reviews/R-031/{PERIOD}")["checks"] == []


def test_every_mark_and_next_step_is_accepted(client):
    for mark in ("repeated_deviation", "outside_limit", "missing_entry", "missed_check", "within_plan"):
        for step in ("sign_review", "ask_for_corrective_actions", "refer_to_food_safety_lead"):
            row = {"unit_or_check": "Hot holding cabinet", "plan_section": "3.2", "limit": "63.0 °C or hotter", "mark": mark}
            post(client, f"{FS}/reviews/R-022/{PERIOD}/checks", {"rows": [row], "proposed_next_step": step})
    assert len(get(client, f"{FS}/reviews/R-022/{PERIOD}")["checks"]) == 15


def test_the_review_flow_request_answer_sign(client):
    base = f"{FS}/reviews/R-014/{PERIOD}"
    # signing is refused while actions are requested and none is recorded
    r = post(client, f"{base}/corrective-actions/request", {"requested_by": "A. Reviewer", "note": "Answer for the chiller.",
                                                            "items": ["Make-line chiller"]})
    assert r["kind"] == "change" and r["status"] == "corrective_actions_requested"
    assert r["review"]["corrective_actions_request"]["requested_by"] == "A. Reviewer"
    assert r["review"]["corrective_actions_request"]["items"] == ["Make-line chiller"]
    assert get(client, f"{FS}/records", site_id="R-014")["items"][0]["review_status"] == "corrective_actions_requested"
    refused = post(client, f"{base}/sign", {"signed_by": "B. Teague"}, 409)
    assert refused["applied"] is False and "none is recorded" in refused["detail"]
    assert get(client, base)["status"] == "corrective_actions_requested"
    # a second request is refused
    assert "already requested" in post(client, f"{base}/corrective-actions/request",
                                       {"requested_by": "A", "note": "again"}, 409)["detail"]
    # the restaurant manager answers one row
    a = post(client, f"{base}/corrective-actions", {"unit_or_check": "Make-line chiller", "what_was_done": "Food discarded.",
                                                      "done_by": "R. Manager", "done_on": "2026-10-09"})
    assert a["corrective_action"]["action_id"] == "CA-0001" and a["status"] == "corrective_actions_requested"
    b = post(client, f"{base}/corrective-actions", {"unit_or_check": "Hot holding cabinet", "what_was_done": "Held food binned.",
                                                      "done_by": "R. Manager", "done_on": "2026-10-14"})
    assert b["corrective_action"]["action_id"] == "CA-0002"
    rev = get(client, base)
    assert [x["unit_or_check"] for x in rev["corrective_actions"]] == ["Make-line chiller", "Hot holding cabinet"]
    assert rev["corrective_actions"][0]["done_by"] == "R. Manager" and rev["corrective_actions"][0]["done_on"] == "2026-10-09"
    # now it can be signed, once
    s = post(client, f"{base}/sign", {"signed_by": "Odalys Fenwright-Mourne", "note": "Reviewed."})
    assert s["kind"] == "change" and s["status"] == "signed" and s["review"]["signed_by"] == "Odalys Fenwright-Mourne"
    assert s["review"]["signed_at"]
    assert "already signed" in post(client, f"{base}/sign", {"signed_by": "X"}, 409)["detail"]
    assert "already signed" in post(client, f"{base}/corrective-actions/request", {"requested_by": "A", "note": "n"}, 409)["detail"]
    assert "already signed" in post(client, f"{base}/corrective-actions",
                                    {"unit_or_check": "u", "what_was_done": "w", "done_by": "b", "done_on": "2026-10-30"}, 409)["detail"]
    assert get(client, f"{FS}/records", site_id="R-014")["items"][0]["review_status"] == "signed"
    # nothing else moved
    assert {x["review_status"] for x in get(client, f"{FS}/records")["items"] if x["site_id"] != "R-014"} == {"not_reviewed"}


def test_a_clean_month_can_be_signed_straight_away(client):
    s = post(client, f"{FS}/reviews/R-022/{PERIOD}/sign", {"signed_by": "B. Teague"})
    assert s["status"] == "signed"


def test_recording_an_action_before_any_request_is_409(client):
    r = post(client, f"{FS}/reviews/R-047/{PERIOD}/corrective-actions",
             {"unit_or_check": "Hot holding cabinet", "what_was_done": "w", "done_by": "b", "done_on": "2026-10-03"}, 409)
    assert "not requested" in r["detail"] and "request_corrective_actions" in r["detail"]
    assert get(client, f"{FS}/reviews/R-047/{PERIOD}")["corrective_actions"] == []


def test_a_change_needs_the_name_of_the_person(client):
    base = f"{FS}/reviews/R-058/{PERIOD}"
    assert client.post(f"{base}/sign", json={}, headers=H).status_code == 422
    assert client.post(f"{base}/sign", json={"signed_by": ""}, headers=H).status_code == 422
    assert client.post(f"{base}/corrective-actions/request", json={"note": "n"}, headers=H).status_code == 422
    assert client.post(f"{base}/corrective-actions/request", json={"requested_by": "A"}, headers=H).status_code == 422
    assert client.post(f"{base}/corrective-actions", json={"unit_or_check": "u"}, headers=H).status_code == 422
    assert get(client, base)["status"] == "not_reviewed"


# ---------------------------------------------------------------- care

def test_guest_feedback_totals_filters_and_paging(client):
    allrows = get(client, "/care/feedback", limit=500)
    assert allrows["count"] == 260 and allrows["total"] == 260 and allrows["offset"] == 0 and allrows["limit"] == 500
    refs = [x["reference"] for x in allrows["items"]]
    assert refs == [f"GF-2610-{n:04d}" for n in range(1, 261)]
    assert set(allrows["items"][0]) == {"reference", "date", "site_id", "channel", "rating", "comment"}
    assert get(client, "/care/feedback")["count"] == 100 and get(client, "/care/feedback")["total"] == 260
    assert get(client, "/care/feedback", period=PERIOD, limit=500)["total"] == 260
    assert get(client, "/care/feedback", period="2026-09")["total"] == 0
    assert get(client, "/care/feedback", site_id="R-047", limit=500)["total"] == 47
    assert get(client, "/care/feedback", channel="survey")["total"] == 55
    assert get(client, "/care/feedback", channel="app review")["total"] == 75
    low = get(client, "/care/feedback", max_rating=1, limit=500)
    assert 7 <= low["total"] < 260 and {x["rating"] for x in low["items"]} == {1}
    assert get(client, "/care/feedback", max_rating=5)["total"] == 260
    both = get(client, "/care/feedback", site_id="R-031", channel="call centre", max_rating=2, limit=500)
    assert both["total"] == both["count"] > 0
    assert all(x["site_id"] == "R-031" and x["channel"] == "call centre" and x["rating"] <= 2 for x in both["items"])
    page2 = get(client, "/care/feedback", limit=50, offset=50)
    assert page2["count"] == 50 and page2["items"][0]["reference"] == "GF-2610-0051" and page2["total"] == 260
    last = get(client, "/care/feedback", limit=50, offset=250)
    assert last["count"] == 10
    assert get(client, "/care/feedback", offset=999)["count"] == 0
    assert client.get("/care/feedback", params={"limit": 501}, headers=H).status_code == 422
    assert client.get("/care/feedback", params={"limit": 0}, headers=H).status_code == 422
    assert client.get("/care/feedback", params={"max_rating": 6}, headers=H).status_code == 422
    assert client.get("/care/feedback", params={"channel": "letter"}, headers=H).status_code == 422
    assert client.get("/care/feedback", params={"period": "October"}, headers=H).status_code == 422


def test_guest_feedback_one_comment_and_404(client):
    x = get(client, "/care/feedback/GF-2610-0001")
    assert x["reference"] == "GF-2610-0001" and x["date"] == "2026-10-01" and x["site_id"] in [f"R-{n:03d}" for n in
                                                                                              (14, 22, 31, 47, 58, 63, 71, 76, 82, 90, 104, 117)]
    assert get(client, "/care/feedback/GF-2610-9999", 404)["applied"] is False


def test_the_theme_is_not_served_by_any_operation(client, store):
    assert "feedback_themes" in store.data and len(store.data["feedback_themes"]) == 260
    pages = [get(client, "/care/feedback", limit=500), get(client, "/care/feedback/GF-2610-0110"), get(client, f"/care/analysis/{PERIOD}")]
    text = json.dumps(pages).lower()
    assert "theme" not in text
    for system in ALL_SYSTEMS:
        assert "feedback_themes" not in json.dumps(client.get(f"/{system}/openapi.json").json())
    assert "feedback_themes" not in json.dumps(client.get("/admin/state", headers=H).json())


# the seven harm comments and the counts by theme, computed from the seed at the retailer date 2026-11-24
THEME_TOTALS = {"late": 78, "wrong": 52, "cold": 41, "app": 24, "praise": 30, "other": 28, "harm": 7}
TOP_SITE = {"late": ("R-047", 36), "wrong": ("R-014", 20), "cold": ("R-031", 20)}
HARM = ["GF-2610-0110", "GF-2610-0120", "GF-2610-0133", "GF-2610-0158", "GF-2610-0169", "GF-2610-0176", "GF-2610-0196"]


def test_feedback_plan_counts_top_sites_and_harm_references(client, store):
    themes = store.data["feedback_themes"]
    totals = {}
    for t in themes.values():
        totals[t] = totals.get(t, 0) + 1
    assert totals == THEME_TOTALS
    for theme, (site, n) in TOP_SITE.items():
        by_site = {}
        for ref, t in themes.items():
            if t == theme:
                s = store.data["guest_feedback"][ref]["site_id"]
                by_site[s] = by_site.get(s, 0) + 1
        ranked = sorted(by_site.values(), reverse=True)
        assert by_site[site] == n == ranked[0] and ranked[1] < n, theme
    assert sorted(ref for ref, t in themes.items() if t == "harm") == HARM
    for ref in HARM:
        assert get(client, f"/care/feedback/{ref}")["rating"] == 1


def test_a_feedback_analysis_is_a_draft_kept_in_versions(client):
    assert get(client, f"/care/analysis/{PERIOD}") == {"demo_data": True, "period": PERIOD, "count": 0, "analyses": []}
    a = post(client, "/care/analysis", {**ANALYSIS, "harm_comments": HARM[:2], "drafted_by": "tester", "summary": "First."})
    assert a["kind"] == "draft" and a["draft"]["version"] == 1 and a["draft"]["drafted_by"] == "tester" and a["period"] == PERIOD
    b = post(client, "/care/analysis", {**ANALYSIS, "harm_comments": HARM})
    assert b["draft"]["version"] == 2 and b["draft"]["drafted_by"] == "agent"
    got = get(client, f"/care/analysis/{PERIOD}")
    assert got["count"] == 2 and [v["version"] for v in got["analyses"]] == [1, 2]
    assert got["analyses"][1]["harm_comments"] == HARM and got["analyses"][0]["themes"][0]["counts_by_site"] == {"R-047": 36}
    assert get(client, "/care/analysis/2026-09")["count"] == 0
    # nothing about a comment changed
    assert get(client, "/care/feedback/GF-2610-0110")["rating"] == 1


def test_a_feedback_analysis_is_refused_when_a_reference_or_site_is_wrong(client):
    bad_ref = {**ANALYSIS, "harm_comments": ["GF-2610-9999"]}
    r = post(client, "/care/analysis", bad_ref, 404)
    assert "GF-2610-9999" in r["detail"]
    quoted = {**ANALYSIS, "themes": [{"name": "x", "count": 1, "quoted_references": ["GF-2610-9999"]}]}
    post(client, "/care/analysis", quoted, 404)
    other_month = {**ANALYSIS, "period": "2026-09"}
    assert "2026-09" in post(client, "/care/analysis", other_month, 404)["detail"]
    bad_site = {**ANALYSIS, "themes": [{"name": "x", "count": 1, "counts_by_site": {"R-999": 1}}]}
    post(client, "/care/analysis", bad_site, 404)
    assert client.post("/care/analysis", json={"period": PERIOD, "themes": []}, headers=H).status_code == 422
    assert client.post("/care/analysis", json={"period": "Oct", "themes": ANALYSIS["themes"]}, headers=H).status_code == 422
    assert get(client, f"/care/analysis/{PERIOD}")["count"] == 0


# ---------------------------------------------------------------- purchasing

def test_suppliers(client):
    r = get(client, "/purchasing/suppliers")
    assert [s["supplier_id"] for s in r["items"]] == ["SUP-301", "SUP-302", "SUP-303", "SUP-304"]
    assert [s["name"] for s in r["items"]] == ["Ilvane Valley Dairy Ltd", "Marlow Reach Packaging Ltd", "Tallowby Flour Mills Ltd",
                                              "Orchard Gate Fresh Produce Ltd"]
    assert all(s["contact_email"].endswith(".example") for s in r["items"])
    one = get(client, "/purchasing/suppliers/SUP-301")
    assert one["purchase_orders"] == ["PO-450112", "PO-450158"] and one["invoices"] == ["INV-88214", "INV-9034"]
    assert get(client, "/purchasing/suppliers/SUP-999", 404)["applied"] is False


def test_purchase_orders_lines_and_buyers(client):
    r = get(client, "/purchasing/purchase-orders")
    assert [p["po_number"] for p in r["items"]] == [
        "PO-450112", "PO-450127", "PO-450131", "PO-450140", "PO-450152", "PO-450158", "PO-450161", "PO-450164"]  # two added by 1.2
    assert {p["buyer"] for p in r["items"]} == {"Hesper Valdane-Orr", "Dorian Ketterly-Voss"}
    assert [p["po_number"] for p in get(client, "/purchasing/purchase-orders", supplier_id="SUP-302")["items"]] == [
        "PO-450127", "PO-450152", "PO-450161"]
    assert [p["po_number"] for p in get(client, "/purchasing/purchase-orders", status="part_received")["items"]] == [
        "PO-450158", "PO-450161", "PO-450164"]
    assert get(client, "/purchasing/purchase-orders", status="received")["count"] == 5
    assert get(client, "/purchasing/purchase-orders", supplier_id="SUP-301", status="received")["count"] == 1
    po = get(client, "/purchasing/purchase-orders/PO-450112")
    assert [(x["item"], x["unit"], x["quantity_ordered"], x["unit_price"], x["quantity_received"]) for x in po["lines"]] == [
        ("Mozzarella, shredded", "kg", 400, 24.50, 400), ("Butter, unsalted", "kg", 60, 31.00, 60)]
    assert po["buyer"] == "Hesper Valdane-Orr" and all(x["buyer"] == po["buyer"] for x in po["lines"])
    assert po["goods_receipt_ids"] == ["GR-60112"] and po["invoice_numbers"] == ["INV-88214"]
    flour = get(client, "/purchasing/purchase-orders/PO-450131")["lines"][0]
    assert (flour["item"], flour["quantity_ordered"], flour["unit_price"]) == ("Pizza flour, 25 kg bag", 600, 44.50)
    peppers = get(client, "/purchasing/purchase-orders/PO-450140")["lines"][0]
    assert (peppers["quantity_ordered"], peppers["quantity_received"], peppers["unit_price"]) == (720, 720, 6.20)
    boxes = get(client, "/purchasing/purchase-orders/PO-450127")["lines"]
    assert [(x["quantity_ordered"], x["unit_price"]) for x in boxes] == [(20000, 0.42), (15000, 0.55)]
    assert get(client, "/purchasing/purchase-orders/PO-999999", 404)["applied"] is False
    assert client.get("/purchasing/purchase-orders", params={"status": "open"}, headers=H).status_code == 422


def test_goods_receipts(client):
    r = get(client, "/purchasing/goods-receipts")
    assert [x["receipt_id"] for x in r["items"]] == [
        "GR-60112", "GR-60127", "GR-60131", "GR-60140", "GR-60152", "GR-60158", "GR-60161", "GR-60164"]  # two added by 1.2
    part = get(client, "/purchasing/goods-receipts", po_number="PO-450158")
    assert part["count"] == 1 and part["items"][0]["lines"][0]["quantity_received"] == 300
    assert part["items"][0]["received_by"] and part["items"][0]["delivery_note"].startswith("DN-")
    assert get(client, "/purchasing/goods-receipts", po_number="PO-450140")["items"][0]["lines"][0]["quantity_received"] == 720
    r404 = get(client, "/purchasing/goods-receipts", 404, po_number="PO-000000")
    assert r404["applied"] is False


INVOICES = {  # number: (supplier, po, net, tax, total)
    "INV-88214": ("SUP-301", "PO-450112", 11660.00, 1749.00, 13409.00),
    "INV-3391": ("SUP-302", "PO-450127", 16650.00, 2497.50, 19147.50),
    "INV-77102": ("SUP-303", "PO-450131", 27600.00, 4140.00, 31740.00),
    "INV-5120": ("SUP-304", "PO-450140", 7480.00, 1122.00, 8602.00),
    "INV-6417": ("SUP-302", "PO-450152", 6480.00, 972.00, 7452.00),
    "INV-9034": ("SUP-301", "PO-450158", 12250.00, 1837.50, 14087.50),
}


def test_the_six_invoices_with_their_exact_amounts(client):
    r = get(client, "/purchasing/invoices")
    assert r["count"] == 6 and {x["status"] for x in r["items"]} == {"received"}
    assert [x["invoice_date"] for x in r["items"]] == sorted(x["invoice_date"] for x in r["items"])
    for number, (supplier, po, net, tax, total) in INVOICES.items():
        inv = get(client, f"/purchasing/invoices/{number}")
        assert (inv["supplier_id"], inv["po_number"], inv["net"], inv["tax"], inv["total"]) == (supplier, po, net, tax, total), number
        assert inv["currency"] == "USD" and inv["status"] == "received" and inv["matches"] == []
        assert number in inv["text"] and po in inv["text"] and f"{total:.2f}" in inv["text"] and inv["text"].startswith("INVENTED")
        assert inv["due_date"] > inv["invoice_date"]
    assert [x["invoice_number"] for x in get(client, "/purchasing/invoices", supplier_id="SUP-302")["items"]] == ["INV-3391", "INV-6417"]
    assert get(client, "/purchasing/invoices", status="queried")["count"] == 0
    assert get(client, "/purchasing/invoices", status="received", supplier_id="SUP-301")["count"] == 2
    assert get(client, "/purchasing/invoices/INV-0", 404)["applied"] is False
    assert client.get("/purchasing/invoices", params={"status": "paid"}, headers=H).status_code == 422


def differences(client, number):
    """What the invoice charges that the order and the goods received do not support, found from the API."""
    inv = get(client, f"/purchasing/invoices/{number}")
    po = get(client, f"/purchasing/purchase-orders/{inv['po_number']}")
    found = []
    for line in inv["lines"]:
        ordered = next((x for x in po["lines"] if x["item"] == line["item"]), None)
        if ordered is None:
            found.append(("not_on_order", line["item"], line["amount"]))
            continue
        if line["unit_price"] != ordered["unit_price"]:
            found.append(("price_differs", line["item"], round((line["unit_price"] - ordered["unit_price"]) * line["quantity"], 2)))
        if line["quantity"] > ordered["quantity_received"]:
            kind = "not_received" if ordered["quantity_received"] < ordered["quantity_ordered"] else "quantity_differs"
            found.append((kind, line["item"], round((line["quantity"] - ordered["quantity_received"]) * line["unit_price"], 2)))
    return found


def test_each_invoice_has_exactly_its_planted_difference(client):
    assert differences(client, "INV-88214") == []
    assert differences(client, "INV-3391") == []
    assert differences(client, "INV-77102") == [("price_differs", "Pizza flour, 25 kg bag", 900.00)]
    assert differences(client, "INV-5120") == [("quantity_differs", "Green peppers", 496.00)]
    assert differences(client, "INV-6417") == [("not_on_order", "Delivery charge", 180.00)]
    assert differences(client, "INV-9034") == [("not_received", "Mozzarella, shredded", 4900.00)]


def test_invoice_lines_carry_the_planted_numbers(client):
    flour = get(client, "/purchasing/invoices/INV-77102")["lines"][0]
    assert (flour["quantity"], flour["unit_price"], flour["amount"]) == (600, 46.00, 27600.00)
    peppers = get(client, "/purchasing/invoices/INV-5120")["lines"][0]
    assert (peppers["quantity"], peppers["unit_price"], peppers["amount"]) == (800, 6.20, 4960.00)
    charge = get(client, "/purchasing/invoices/INV-6417")["lines"][2]
    assert (charge["item"], charge["quantity"], charge["amount"]) == ("Delivery charge", 1, 180.00)
    moz = get(client, "/purchasing/invoices/INV-9034")["lines"][0]
    assert moz["quantity"] == 500
    assert get(client, "/purchasing/purchase-orders/PO-450158")["lines"][0]["quantity_ordered"] == 500


def test_saving_a_match_is_a_draft_with_versions_and_changes_no_status(client):
    a = post(client, "/purchasing/invoices/INV-77102/match", {**MATCH, "drafted_by": "tester"})
    assert a["kind"] == "draft" and a["draft"]["version"] == 1 and a["draft"]["drafted_by"] == "tester"
    assert a["invoice_status"] == "received"
    b = post(client, "/purchasing/invoices/INV-77102/match", {**MATCH, "proposed_next_step": "refer_to_the_buyer"})
    assert b["draft"]["version"] == 2 and b["draft"]["drafted_by"] == "agent"
    inv = get(client, "/purchasing/invoices/INV-77102")
    assert inv["status"] == "received" and [m["version"] for m in inv["matches"]] == [1, 2]
    assert inv["matches"][0]["lines"][0]["net_difference"] == 900.0 and inv["matches"][1]["proposed_next_step"] == "refer_to_the_buyer"
    post(client, "/purchasing/invoices/INV-0/match", MATCH, 404)


def test_a_match_with_a_bad_field_mark_or_step_is_refused(client):
    path = "/purchasing/invoices/INV-77102/match"
    line = MATCH["lines"][0]
    assert client.post(path, json={**MATCH, "lines": [{**line, "field": "colour"}]}, headers=H).status_code == 422
    assert client.post(path, json={**MATCH, "lines": [{**line, "mark": "fine"}]}, headers=H).status_code == 422
    assert client.post(path, json={**MATCH, "proposed_next_step": "pay"}, headers=H).status_code == 422
    assert client.post(path, json={"lines": MATCH["lines"]}, headers=H).status_code == 422
    for field, mark in [("price", "price_differs"), ("quantity", "quantity_differs"), ("item", "agrees"),
                        ("not_on_order", "not_on_order"), ("not_received", "not_received")]:
        post(client, path, {**MATCH, "lines": [{**line, "field": field, "mark": mark}]})
    for step in ("ready_for_approval", "query_the_supplier", "refer_to_the_buyer"):
        post(client, path, {**MATCH, "proposed_next_step": step})


def test_approval_needs_a_match_a_name_and_works_once(client):
    path = "/purchasing/invoices/INV-88214"
    refused = post(client, f"{path}/approve", {"approved_by": "C. Payer"}, 409)
    assert "No match is saved" in refused["detail"] and refused["applied"] is False
    assert get(client, path)["status"] == "received"
    post(client, f"{path}/match", {"lines": [{"field": "price", "item": "Mozzarella, shredded", "invoice_says": "24.50",
                                              "order_says": "24.50", "received": "400 kg", "mark": "agrees"}],
                                   "proposed_next_step": "ready_for_approval"})
    assert client.post(f"{path}/approve", json={}, headers=H).status_code == 422
    ok = post(client, f"{path}/approve", {"approved_by": "C. Payer", "note": "Agrees."})
    assert ok["kind"] == "change" and ok["status"] == "approved" and ok["invoice"]["approved_by"] == "C. Payer"
    assert get(client, path)["status"] == "approved"
    assert "already approved" in post(client, f"{path}/approve", {"approved_by": "D"}, 409)["detail"]
    assert "already approved" in post(client, f"{path}/query", {"raised_by": "D", "message": "m"}, 409)["detail"]
    post(client, "/purchasing/invoices/INV-0/approve", {"approved_by": "x"}, 404)


def test_a_query_changes_the_status_and_works_once(client):
    path = "/purchasing/invoices/INV-5120"
    assert client.post(f"{path}/query", json={"raised_by": "C. Payer"}, headers=H).status_code == 422
    assert client.post(f"{path}/query", json={"message": "m"}, headers=H).status_code == 422
    q = post(client, f"{path}/query", {"raised_by": "C. Payer", "message": "800 kg invoiced, 720 kg ordered and received."})
    assert q["kind"] == "change" and q["status"] == "queried"
    assert q["invoice"]["query"]["raised_by"] == "C. Payer" and "720 kg" in q["invoice"]["query"]["message"]
    assert q["invoice"]["query"]["to"].endswith(".example")
    assert get(client, path)["status"] == "queried"
    assert get(client, "/purchasing/invoices", status="queried")["count"] == 1
    assert "already queried" in post(client, f"{path}/query", {"raised_by": "D", "message": "again"}, 409)["detail"]
    post(client, "/purchasing/invoices/INV-0/query", {"raised_by": "x", "message": "m"}, 404)
    # a queried invoice with a saved match can still be approved later by a person
    post(client, f"{path}/match", {**MATCH, "lines": [{**MATCH["lines"][0], "field": "quantity", "mark": "quantity_differs"}]})
    assert post(client, f"{path}/approve", {"approved_by": "C. Payer"})["status"] == "approved"


def test_counts_follow_the_changes(client):
    post(client, "/purchasing/invoices/INV-5120/query", {"raised_by": "A", "message": "m"})
    post(client, "/purchasing/invoices/INV-3391/match", MATCH)
    post(client, "/purchasing/invoices/INV-3391/approve", {"approved_by": "A"})
    post(client, f"{FS}/reviews/R-022/{PERIOD}/sign", {"signed_by": "A"})
    c = get(client, "/admin/state")["counts"]
    assert c["supplier_invoices_received"] == 4 and c["supplier_invoices_queried"] == 1 and c["supplier_invoices_approved"] == 1
    assert c["record_periods_not_reviewed"] == 5 and c["stores"] == 8 and c["restaurants"] == 12
    assert c["guest_feedback_comments"] == 260 and c["purchase_orders"] == 8 and c["goods_receipts"] == 8 and c["suppliers"] == 4

