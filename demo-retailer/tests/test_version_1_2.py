"""Version 1.2: the online shop's orders, return requests and flagged orders; customer tickets, complaints and public
reviews; delivery notes, supplier payments and supplier questions.

Every planted case is read back through the API and compared with the tables in SCENARIOS.md.
"""
import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from conftest import H, KEY, TODAY
from retailer.seed import build_all
from retailer.seed_care_desk import complaints_procedure_markdown, help_articles_markdown
from retailer.seed_orders import returns_policy_markdown
from test_operations import get, post

TEXT = (Path(__file__).resolve().parent.parent / "SCENARIOS.md").read_text(encoding="utf-8")
LIBRARY = Path(__file__).resolve().parents[2] / "retail" / "policy-library"
TODAY_D = date.fromisoformat(TODAY)


def section(title):
    return TEXT.split(f"## {title}")[1].split("\n## ")[0]


def rows(prefix, text):
    return [[c.strip() for c in line.strip().strip("|").split("|")] for line in text.splitlines() if line.startswith(f"| {prefix}")]


def num(text):
    return float(text.replace(",", ""))


ORDERS = section("Online orders")
RETURNS = section("Return requests")
FLAGGED = section("Orders flagged for a fraud review")
TICKETS = section("Customer tickets")
COMPLAINTS = section("Complaints")
REVIEWS = section("Public reviews")
NOTES = section("Delivery notes")
PAYMENTS = section("Supplier payments and questions")
ARRIVALS = section("Simulated arrivals")


def simulate(client, kind):
    return post(client, f"/admin/simulate/{kind}")


# ================================================================ orders and deliveries

def test_forty_three_orders_with_the_statuses_of_the_scenario_file(client):
    listed = get(client, "/orders/orders", limit=200)
    assert listed["count"] == listed["total"] == 43 and listed["retailer_date"] == TODAY
    numbers = sorted(o["order_number"] for o in listed["items"])
    assert numbers[0] == "RM-58101" and numbers[-1] == "RM-58198" and len({o["customer_id"] for o in listed["items"]}) == 24
    by_status = {}
    for o in listed["items"]:
        by_status[o["status"]] = by_status.get(o["status"], 0) + 1
    said = ORDERS.split("By status at the start: ")[1].split(".")[0]
    assert ", ".join(f"{k} {v}" for k, v in sorted(by_status.items(), key=lambda kv: said.index(kv[0]))) == said
    assert [o["placed_on"] for o in listed["items"]] == sorted((o["placed_on"] for o in listed["items"]), reverse=True)
    for o in listed["items"]:
        assert set(o) == {"order_number", "placed_on", "customer_id", "customer_name", "status", "total", "currency",
                          "delivery_method", "promised_date", "delivered_on", "flagged"}


def test_only_the_two_planted_home_deliveries_are_late(client):
    late = []
    for o in get(client, "/orders/orders", limit=200)["items"]:
        if o["delivery_method"] == "home_delivery" and not o["delivered_on"] and o["promised_date"] < TODAY:
            late.append(o["order_number"])
        if o["delivered_on"] and o["delivery_method"] == "home_delivery":
            assert o["delivered_on"] <= o["promised_date"], o["order_number"]
    assert sorted(late) == ["RM-58161", "RM-58162"]


def test_the_three_deliveries_match_the_scenario_table(client):
    table = rows("RM-", ORDERS)
    assert [r[0] for r in table] == ["RM-58162", "RM-58161", "RM-58166"]
    for number, customer, promised, status, last_scan, _ in table:
        o = get(client, f"/orders/orders/{number}")
        assert (o["customer_name"], o["delivery"]["promised_date"], o["status"], o["last_scan"]["time"]) == (
            customer, promised, status, last_scan), number
        assert o["customer_email"] == customer.lower().replace(" ", ".") + "@mail.invalid" and o["customer_email"] in ORDERS
        assert "scans" not in o and o["retailer_date"] == TODAY and o["demo_data"] is True

    explained = get(client, "/orders/orders/RM-58162/scans")
    assert explained["count"] == 4 and explained["carrier"] == "Fernhollow Couriers" and explained["delivered_on"] is None
    assert explained["scans"][2]["time"] == "2026-11-21T07:20:00" and "closed by flooding" in explained["scans"][2]["text"]
    assert explained["scans"][3]["text"] == "New delivery date set: 2026-11-25." and explained["rescheduled_date"] == "2026-11-25"

    silent = get(client, "/orders/orders/RM-58161/scans")
    assert silent["count"] == 2 and silent["rescheduled_date"] is None and silent["delivered_on"] is None
    assert silent["scans"][-1] == {"time": "2026-11-18T20:40:00", "place": "Marlow Reach depot",
                                   "text": "Arrived at the Marlow Reach depot."}
    assert not any(word in s["text"].lower() for s in silent["scans"] for word in ("held", "delay", "closed", "resched"))

    neighbour = get(client, "/orders/orders/RM-58166/scans")
    assert neighbour["delivered_on"] == "2026-11-22" == neighbour["promised_date"]
    assert neighbour["delivered_to"] == "a neighbour at number 14"
    assert neighbour["scans"][-1]["text"] == "Delivered to a neighbour at number 14. A card was left at the delivery address."
    # no other order was left with a neighbour or rescheduled
    for o in get(client, "/orders/orders", limit=200)["items"]:
        if o["order_number"] not in ("RM-58162", "RM-58166"):
            s = get(client, f"/orders/orders/{o['order_number']}/scans")
            assert s["rescheduled_date"] is None and "neighbour" not in json.dumps(s), o["order_number"]


def test_the_other_orders_the_care_cases_refer_to(client):
    o = get(client, "/orders/orders/RM-58174")
    assert (o["status"], o["delivery"]["promised_date"]) == ("out_for_delivery", TODAY)
    o = get(client, "/orders/orders/RM-58165")
    assert (o["status"], o["delivery"]["collect_site_id"], o["delivery"]["promised_date"], o["scan_count"]) == (
        "ready_for_collection", "S-105", "2026-11-22", 0)
    o = get(client, "/orders/orders/RM-58163")
    assert (o["status"], o["placed_on"], o["delivery"]["promised_date"], o["last_scan"]) == ("placed", TODAY, "2026-11-27", None)
    o = get(client, "/orders/orders/RM-58118")
    assert o["refunds"] == [{"amount": 28.0, "for": "Cotton bath towel set, returned", "approved_on": "2026-11-12", "paid_on": None}]
    assert o["delivery"]["delivered_on"] == "2026-10-31"
    o = get(client, "/orders/orders/RM-58158")
    assert (o["goods_total"], o["delivery_charge"], o["total"]) == (57.50, 4.95, 62.45)
    o = get(client, "/orders/orders/RM-58156")
    assert o["payment"]["charges"] == [{"amount": 60.95, "charged_on": "2026-11-17"}]


def test_delivery_charges_follow_the_rule_and_totals_add_up(store):
    for o in store.data["orders"].values():
        assert o["goods_total"] == round(sum(x["amount"] for x in o["lines"]), 2) and o["currency"] == "USD"
        service = o["delivery"]["service"]
        charge = 0.0 if service == "click_and_collect" else 7.95 if service == "next_day" else 0.0 if o["goods_total"] >= 60 else 4.95
        assert o["delivery_charge"] == charge and o["total"] == round(o["goods_total"] + charge, 2), o["order_number"]
        assert o["customer_email"].endswith("@mail.invalid") and o["customer_id"] in store.data["customers"]


def test_order_search_filters_and_404(client):
    one = get(client, "/orders/orders", order_number="rm-58162")
    assert one["count"] == 1 and one["items"][0]["customer_name"] == "Dunstan Yarrowby-Finn"
    mine = get(client, "/orders/orders", customer_email="Dunstan.Yarrowby-Finn@mail.invalid")
    assert [o["order_number"] for o in mine["items"]] == ["RM-58190", "RM-58162"]
    assert get(client, "/orders/orders", order_number="RM-58162", customer_email="someone.else@mail.invalid")["count"] == 0
    assert get(client, "/orders/orders", customer_id="C-4013")["count"] == 2
    assert get(client, "/orders/orders", status="awaiting_fraud_review")["count"] == 4
    assert get(client, "/orders/orders", limit=5, offset=40)["count"] == 3
    assert client.get("/orders/orders", params={"status": "lost"}, headers=H).status_code == 422
    r = get(client, "/orders/orders/RM-00000", 404)
    assert r["applied"] is False and "search_orders" in r["detail"]
    assert get(client, "/orders/orders/RM-00000/scans", 404)["applied"] is False


def test_an_order_is_found_with_its_number_and_the_surname_on_it(client, store):
    def numbers(**params):
        return [o["order_number"] for o in get(client, "/orders/orders", **params)["items"]]

    assert store.data["orders"]["RM-58162"]["customer_name"] == "Dunstan Yarrowby-Finn"
    assert store.data["orders"]["RM-58161"]["customer_name"] == "Rufus Amberley-Skein"
    # the surname matches
    one = get(client, "/orders/orders", order_number="RM-58162", customer_surname="Yarrowby-Finn")
    assert one["count"] == 1 and one["total"] == 1 and one["items"][0]["customer_name"] == "Dunstan Yarrowby-Finn"
    assert set(one["items"][0]) == set(get(client, "/orders/orders", order_number="RM-58162")["items"][0])
    assert numbers(customer_surname="Yarrowby-Finn") == ["RM-58190", "RM-58162"]
    # a wrong surname gives no row, and so does a part of the surname or the whole name
    for wrong in ("Nobody-Here", "Yarrowby", "Finn", "Dunstan", "Dunstan Yarrowby-Finn", "", "   "):
        assert numbers(order_number="RM-58162", customer_surname=wrong) == [], wrong
    # capital letters and spaces around the surname do not matter
    for typed in ("yarrowby-finn", "YARROWBY-FINN", "  Yarrowby-Finn  ", "yArRoWbY-fInN"):
        assert numbers(order_number="RM-58162", customer_surname=typed) == ["RM-58162"], typed
    # the hyphen typed as a space
    for typed in ("Yarrowby Finn", " yarrowby  finn ", "Yarrowby - Finn"):
        assert numbers(order_number="RM-58162", customer_surname=typed) == ["RM-58162"], typed
    # the order number of one customer with the surname of another gives no row
    assert numbers(order_number="RM-58162", customer_surname="Amberley-Skein") == []
    assert numbers(order_number="RM-58161", customer_surname="Yarrowby-Finn") == []
    assert numbers(order_number="RM-58161", customer_surname="Amberley-Skein") == ["RM-58161"]
    assert numbers(order_number="RM-58166", customer_surname="ashgrove lyle") == ["RM-58166"]
    # the filters add up, and the email filter works as before
    assert numbers(customer_surname="Yarrowby-Finn", customer_email="dunstan.yarrowby-finn@mail.invalid") == ["RM-58190", "RM-58162"]
    assert numbers(customer_surname="Yarrowby-Finn", customer_email="rufus.amberley-skein@mail.invalid") == []
    assert numbers(order_number="RM-58162", customer_email="Dunstan.Yarrowby-Finn@mail.invalid") == ["RM-58162"]
    # every order is found by its own number and surname, and by no other customer's surname
    for o in store.data["orders"].values():
        surname = o["customer_name"].split()[-1]
        assert numbers(order_number=o["order_number"], customer_surname=surname) == [o["order_number"]]
        other = "Amberley-Skein" if surname != "Amberley-Skein" else "Yarrowby-Finn"
        assert numbers(order_number=o["order_number"], customer_surname=other) == []


# ================================================================ returns

ASSESS = {"conditions": [{"condition": "1.1", "result": "met", "note": "Day 8."}, {"condition": "2.1", "result": "met"}],
          "proposed_decision": "approve", "refund_amount": 64.0, "customer_message": "Your return is being looked at."}
R1 = "/orders/returns/RR-2611-01"


def test_the_returns_policy_is_served_and_is_the_document_in_the_policy_library(client):
    p = get(client, "/orders/returns-policy")
    assert (p["document"], p["version"], p["window_days"], p["damage_report_days"]) == ("Returns Policy", "3.0", 30, 7)
    numbers = [c["condition"] for s in p["sections"] for c in s["conditions"]]
    assert numbers == ["1.1", "1.2", "2.1", "2.2", "2.3", "3.1", "3.2", "3.3", "3.4", "4.1", "4.2", "5.1", "5.2", "5.3", "6.1", "6.2"]
    assert p["excluded_categories"] == ["chilled_food", "frozen_food", "fresh_produce", "bakery", "personal_care", "gift_cards",
                                        "made_to_order"]
    assert "invented" in p["notice"] and p["text"] == returns_policy_markdown()
    for s in p["sections"]:
        for c in s["conditions"]:
            assert f"{c['condition']} {c['text']}" in p["text"]
    doc = LIBRARY / "returns-policy-v3.0.md"
    if doc.exists():
        assert doc.read_text(encoding="utf-8") == p["text"] and "invented" in p["text"].splitlines()[0]


def test_the_ten_return_requests_match_the_scenario_table(client, store):
    table = rows("RR-", RETURNS)
    listed = get(client, "/orders/returns")
    assert listed["count"] == 10 == len(table) and {r["status"] for r in listed["items"]} == {"requested"}
    for rid, order, item, delivered, asked, day, reason, condition, proposal, decides, refund in table:
        r = get(client, f"/orders/returns/{rid}")
        assert (r["order_number"], r["item"], r["delivered_on"], r["requested_on"], r["days_since_delivery"], r["reason"],
                r["condition_reported"]) == (order, item, delivered, asked, int(day), reason, condition), rid
        assert store.data["return_answers"][rid] == {"proposed_decision": proposal, "deciding_condition": decides,
                                                     "refund_amount": num(refund)}, rid
        o = get(client, f"/orders/orders/{order}")
        assert o["delivery"]["delivered_on"] == delivered and rid in o["return_request_ids"]
        assert r["customer_name"] == o["customer_name"] and any(x["sku"] == r["sku"] for x in o["lines"])
        if proposal == "approve":
            assert num(refund) == r["unit_price"] * r["quantity"]
    proposals = [r[8] for r in table]
    assert (proposals.count("approve"), proposals.count("refuse"), proposals.count("refer_to_a_person")) == (5, 4, 1)
    assert sum(num(r[10]) for r in table) == 187.00 and "add up to 187.00" in RETURNS


def test_each_planted_return_shows_what_decides_it(client):
    policy = get(client, "/orders/returns-policy")
    r = {n: get(client, f"/orders/returns/RR-2611-{n}") for n in ("01", "02", "03", "04", "05", "06", "07", "08", "09", "10")}
    inside = lambda x: x["days_since_delivery"] <= policy["window_days"]
    assert inside(r["01"]) and r["01"]["category"] not in policy["excluded_categories"] and r["01"]["quantity"] == 1
    assert not inside(r["02"]) and r["02"]["days_since_delivery"] == 38
    assert inside(r["03"]) and r["03"]["category"] == "chilled_food" and r["03"]["category"] in policy["excluded_categories"]
    assert (r["04"]["condition_reported"], r["04"]["reason"]) == ("opened", "changed_mind") and "works" in r["04"]["customer_statement"]
    assert (r["05"]["condition_reported"], r["05"]["reason"]) == ("opened", "faulty") and inside(r["05"])
    assert r["06"]["reason"] == "damaged_on_arrival" and r["06"]["photo_attached"] and r["06"]["days_since_delivery"] <= 7
    assert (r["06"]["quantity"], r["06"]["quantity_bought"], r["06"]["unit_price"]) == (1, 2, 11.50)
    assert r["07"]["reason"] == "damaged_on_arrival" and r["07"]["days_since_delivery"] == 15 > policy["damage_report_days"]
    assert (r["08"]["quantity"], r["08"]["quantity_bought"]) == (1, 2) and "labels are attached" in r["08"]["customer_statement"]
    assert r["09"]["category"] == "gift_cards" and r["10"]["days_since_delivery"] == 30
    assert get(client, "/orders/returns", order_number="RM-58131")["count"] == 1
    assert get(client, "/orders/returns/RR-0000-00", 404)["applied"] is False


def test_a_return_assessment_is_a_draft_and_a_person_decides(client):
    post(client, f"{R1}/approve", {"approved_by": "G. Leader"}, 409)
    r = post(client, "/orders/returns/RR-2611-02/refuse", {"refused_by": "G. Leader", "reason": "Outside the window."}, 409)
    assert r["applied"] is False and "save_return_assessment" in r["detail"]
    first = post(client, f"{R1}/assessment", ASSESS)
    assert first["applied"] is True and first["kind"] == "draft" and first["draft"]["version"] == 1
    assert first["draft"]["drafted_by"] == "agent" and first["request_status"] == "requested"
    second = post(client, f"{R1}/assessment", {**ASSESS, "drafted_by": "Returns Processing"})
    assert second["draft"]["version"] == 2
    seen = get(client, R1)
    assert [a["version"] for a in seen["assessments"]] == [1, 2] and seen["status"] == "requested"
    assert get(client, "/orders/returns", status="requested")["count"] == 10
    post(client, f"{R1}/approve", {"note": "no name"}, 422)
    done = post(client, f"{R1}/approve", {"approved_by": "G. Leader"})
    assert done["kind"] == "change" and done["status"] == "approved" and done["return_request"]["decided_by"] == "G. Leader"
    again = post(client, f"{R1}/refuse", {"refused_by": "X", "reason": "y"}, 409)
    assert "already approved by G. Leader" in again["detail"]
    post(client, "/orders/returns/RR-2611-02/assessment", {"conditions": [{"condition": "1.2", "result": "not_met"}],
                                                           "proposed_decision": "refuse"})
    post(client, "/orders/returns/RR-2611-02/refuse", {"refused_by": "G. Leader"}, 422)
    r = post(client, "/orders/returns/RR-2611-02/refuse", {"refused_by": "G. Leader", "reason": "Asked for on day 38."})
    assert r["status"] == "refused" and r["return_request"]["decision_note"] == "Asked for on day 38."
    assert get(client, "/orders/returns", status="refused")["count"] == 1
    assert get(client, "/admin/state")["counts"]["return_requests_not_decided"] == 8


@pytest.mark.parametrize("change, words", [
    ({"conditions": [{"condition": "9.9", "result": "met"}]}, "9.9 is not a condition of the returns policy"),
    ({"conditions": [{"condition": "1.1", "result": "passed"}]}, "result"),
    ({"refund_amount": 64.01}, "above the price paid"),
    ({"proposed_decision": "refuse"}, "only with the decision approve"),
    ({"proposed_decision": "accept"}, "proposed_decision"),
    ({"conditions": []}, "conditions"),
])
def test_a_return_assessment_that_does_not_fit_is_refused_with_a_readable_message(client, change, words):
    r = post(client, f"{R1}/assessment", {**ASSESS, **change}, 422)
    assert r["applied"] is False and words in r["detail"], r["detail"]
    assert get(client, R1)["assessments"] == []
    post(client, "/orders/returns/RR-0000-00/assessment", ASSESS, 404)


# ================================================================ flagged orders

REVIEW = {"signals": [{"signal": "device", "departs_from_pattern": True, "what_the_record_shows": "DEV-2 is new."},
                      {"signal": "basket_value", "departs_from_pattern": True, "what_the_record_shows": "1,248.00 against 56.25."}],
          "proposed_decision": "hold", "explanation": "The order differs from the nine earlier orders on device and value."}
F1 = "/orders/flagged/RM-58192"


def test_the_four_flagged_orders_match_the_scenario_table(client, store):
    table = rows("RM-", FLAGGED)
    listed = get(client, "/orders/flagged")
    assert [r[0] for r in table] == [o["order_number"] for o in listed["items"]] == ["RM-58192", "RM-58194", "RM-58196", "RM-58198"]
    for row, (number, customer, total, reasons, earlier, average, highest, proposal) in zip(listed["items"], table):
        assert (row["customer_id"], row["total"], len(row["reasons"]), row["flag_status"], row["reviews"]) == (
            customer, num(total), int(reasons), "awaiting_review", 0), number
        h = get(client, f"/orders/customers/{customer}/history")
        assert (h["orders_count"], h["average_total"], h["highest_total"]) == (int(earlier) + 1, num(average), num(highest)), number
        assert h["orders"][0]["order_number"] == number and h["orders"][0]["flagged"] is True
        assert store.data["fraud_answers"][number]["proposed_decision"] == proposal
        o = get(client, f"/orders/orders/{number}")
        assert o["status"] == "awaiting_fraud_review" and o["placed_on"] == TODAY and o["flag"]["status"] == "awaiting_review"
    assert get(client, "/orders/flagged", status="held")["count"] == 0


def test_two_flagged_orders_depart_from_the_pattern_in_ways_the_record_shows(client):
    o = get(client, "/orders/orders/RM-58192")
    h = get(client, "/orders/customers/C-4020/history")
    earlier = h["orders"][1:]
    assert o["lines"][0]["quantity"] == 4 and o["lines"][0]["unit_price"] == 312.00 and o["goods_total"] == 1248.00
    assert o["device_first_seen_on_this_order"] and o["device_ref"] == "DEV-2" and {x["device_ref"] for x in earlier} == {"DEV-1"}
    assert o["delivery"]["address_first_used_on_this_order"] and o["delivery"]["address_ref"] == "ADDR-2"
    assert {x["address_ref"] for x in earlier} == {"ADDR-1"} and {x["service"] for x in earlier} == {"standard"}
    assert o["delivery"]["service"] == "next_day" and o["payment"]["card_first_used_on_this_order"] is False
    assert h["account_changes"] == [{"date": "2026-11-23", "change": "The email address on the account was changed."}]
    assert len(earlier) == 9 and max(x["total"] for x in earlier) == 96.40

    o = get(client, "/orders/orders/RM-58194")
    h = get(client, "/orders/customers/C-4021/history")
    earlier = h["orders"][1:]
    assert o["total"] == 890.00 and o["lines"][0]["item"] == "Games console" and o["lines"][0]["quantity"] == 2
    assert o["payment"]["card_first_used_on_this_order"] and o["payment"]["card_ref"] == "CARD-2"
    assert {x["card_ref"] for x in earlier} == {"CARD-1"} and {x["delivery_method"] for x in earlier} == {"home_delivery"}
    assert o["delivery"]["method"] == "click_and_collect" and o["delivery"]["collect_site_id"] == "S-108"
    assert o["delivery"]["collector"] == "someone other than the account holder"
    assert o["device_first_seen_on_this_order"] is False and len(earlier) == 14 and h["account_changes"] == []


def test_two_flagged_orders_look_odd_and_the_history_explains_them(client):
    o = get(client, "/orders/orders/RM-58196")
    h = get(client, "/orders/customers/C-4022/history")
    big = [(x["order_number"], x["placed_on"], x["total"], x["items"], x["outcome"]) for x in h["orders"][1:] if x["total"] > 500]
    assert big == [("RM-57938", "2026-09-22", 605.50, "two tablet computers", "delivered"),
                   ("RM-57827", "2026-06-21", 574.00, "two tablet computers", "delivered")]
    assert o["total"] == 578.00 and not o["device_first_seen_on_this_order"] and not o["payment"]["card_first_used_on_this_order"]
    assert not o["delivery"]["address_first_used_on_this_order"] and len(o["flag"]["reasons"]) == 1
    for line in big:
        assert line[0] in FLAGGED and line[1] in FLAGGED

    o = get(client, "/orders/orders/RM-58198")
    h = get(client, "/orders/customers/C-4023/history")
    assert o["device_first_seen_on_this_order"] and o["total"] == 77.00 and o["delivery"]["address_ref"] == "ADDR-1"
    previous = h["orders"][1]
    assert previous["order_number"] == "RM-57990" and previous["outcome"] == "collected, then part refunded at the till"
    assert previous["refund"] == {"where": "at the till", "site_id": "S-101", "till_row_id": "TR-2610-0138",
                                  "date": "2026-10-26", "amount": 52.58}
    # the refund is a row of the tills system, inside every till rule
    till = [x for x in get(client, "/tills/entries", site_id="S-101", kind="refund", period="2026-10")["items"]
            if x["row_id"] == "TR-2610-0138"][0]
    assert (till["amount"], till["date"], till["reason"]) == (52.58, "2026-10-26", "wrong item sold")
    assert till["approver_id"] and till["original_receipt"] and "TR-2610-0138" in FLAGGED
    assert get(client, "/orders/customers/C-0000/history", 404)["applied"] is False


def test_a_fraud_review_is_a_draft_and_a_person_releases_or_holds(client):
    r = post(client, f"{F1}/hold", {"held_by": "H. Reviewer", "reason": "To be checked."}, 409)
    assert r["applied"] is False and "save_fraud_review" in r["detail"]
    post(client, f"{F1}/release", {"released_by": "H. Reviewer"}, 409)
    first = post(client, f"{F1}/review", REVIEW)
    assert first["kind"] == "draft" and first["draft"]["version"] == 1 and first["flag_status"] == "awaiting_review"
    assert post(client, f"{F1}/review", {**REVIEW, "drafted_by": "Fraud Prevention"})["draft"]["version"] == 2
    o = get(client, "/orders/orders/RM-58192")
    assert o["status"] == "awaiting_fraud_review" and [v["drafted_by"] for v in o["fraud_reviews"]] == ["agent", "Fraud Prevention"]
    post(client, f"{F1}/hold", {"held_by": "H. Reviewer"}, 422)
    held = post(client, f"{F1}/hold", {"held_by": "H. Reviewer", "reason": "Six points differ."})
    assert held["kind"] == "change" and held["status"] == "held" and held["order"]["status"] == "on_hold"
    assert "already held by H. Reviewer" in post(client, f"{F1}/release", {"released_by": "X"}, 409)["detail"]
    post(client, "/orders/flagged/RM-58196/review", {**REVIEW, "proposed_decision": "release"})
    released = post(client, "/orders/flagged/RM-58196/release", {"released_by": "H. Reviewer"})
    assert released["status"] == "released" and released["order"]["status"] == "released_for_dispatch"
    assert get(client, "/orders/flagged", status="awaiting_review")["count"] == 2
    assert get(client, "/admin/state")["counts"]["orders_awaiting_fraud_review"] == 2
    # an order that is not flagged
    r = post(client, "/orders/flagged/RM-58162/review", REVIEW, 409)
    assert "is not flagged" in r["detail"]
    post(client, "/orders/flagged/RM-58162/hold", {"held_by": "H", "reason": "r"}, 409)
    post(client, "/orders/flagged/RM-00000/review", REVIEW, 404)


@pytest.mark.parametrize("change, words", [
    ({"signals": [{"signal": "weather", "departs_from_pattern": True, "what_the_record_shows": "x"}]}, "signal"),
    ({"signals": REVIEW["signals"] + [REVIEW["signals"][0]]}, "device is listed twice"),
    ({"signals": []}, "signals"),
    ({"proposed_decision": "cancel"}, "proposed_decision"),
    ({"explanation": ""}, "explanation"),
])
def test_a_fraud_review_that_does_not_fit_is_refused_with_a_readable_message(client, change, words):
    r = post(client, f"{F1}/review", {**REVIEW, **change}, 422)
    assert r["applied"] is False and words in r["detail"], r["detail"]
    assert get(client, "/orders/orders/RM-58192")["fraud_reviews"] == []


# ================================================================ customer tickets

REPLY = {"answer_status": "answered_from_articles", "reply": "A refund arrives within 5 working days of the approval.",
         "articles_cited": ["HA-05"], "proposed_next_step": "send_reply"}
NO_ANSWER = {"answer_status": "no_article_answers", "reply": "Our help articles do not cover this. A colleague will write to you.",
             "articles_cited": [], "proposed_next_step": "pass_to_a_colleague"}
T4 = "/care/tickets/CT-2611-004"


def test_the_twenty_tickets_and_the_article_that_answers_each(client, store):
    table = rows("CT-", TICKETS)
    listed = get(client, "/care/tickets")
    assert listed["count"] == 20 == len(table) and {t["status"] for t in listed["items"]} == {"open"}
    for tid, received, customer, order, subject, article in table:
        t = get(client, f"/care/tickets/{tid}")
        assert (t["received_on"], t["customer_name"], t["order_number"], t["subject"]) == (received, customer, order, subject), tid
        assert store.data["ticket_answers"][tid] == ("" if article == "none" else article), tid
        assert t["customer_email"].endswith("@mail.invalid") and t["reply_drafts"] == [] and t["reply_sent"] is None
        if order:
            assert order in t["message"] and get(client, f"/orders/orders/{order}")["customer_name"] == customer
    unanswered = [r[0] for r in table if r[5] == "none"]
    assert unanswered == ["CT-2611-014", "CT-2611-015", "CT-2611-016"]
    assert {r[5] for r in table} - {"none"} == {f"HA-{n:02d}" for n in range(1, 13)}
    assert "ticket_answers" not in json.dumps(listed) and "HA-" not in json.dumps(listed)


def test_help_articles_are_served_searched_and_are_the_document_in_the_policy_library(client):
    every = get(client, "/care/help-articles")
    table = rows("HA-", TICKETS)
    assert every["count"] == 12 == len(table)
    for a, (aid, title, _) in zip(every["items"], table):
        assert (a["article_id"], a["title"]) == (aid, title) and len(a["body"]) > 60
    text = help_articles_markdown()
    for a in every["items"]:
        assert f"## {a['article_id']}. {a['title']}\n\n{a['body']}" in text
    doc = LIBRARY / "help-articles.md"
    if doc.exists():
        assert doc.read_text(encoding="utf-8") == text and "invented" in text.splitlines()[0]
    assert get(client, "/care/help-articles", q="refund arrive approved")["items"][0]["article_id"] == "HA-05"
    assert get(client, "/care/help-articles", q="forgotten password")["items"][0]["article_id"] == "HA-11"
    assert get(client, "/care/help-articles", q="neighbour")["items"][0]["article_id"] == "HA-12"
    assert get(client, "/care/help-articles", q="zebra")["count"] == 0
    bodies = " ".join(a["body"].lower() for a in every["items"])
    for word in ("price match", "invoice", "allergy", " nut "):  # the three tickets no article answers
        assert word not in bodies


def test_past_cases_are_searched_and_answer_none_of_the_three(client):
    every = get(client, "/care/past-cases")
    assert every["count"] == 10 and [c["case_id"] for c in every["items"]][0] == "PC-2611-10"
    assert [c["closed_on"] for c in every["items"]] == sorted((c["closed_on"] for c in every["items"]), reverse=True)
    found = get(client, "/care/past-cases", q="opened hand mixer")
    assert found["items"][0]["case_id"] == "PC-2611-03" and "condition 2.2" in found["items"][0]["what_was_done"]
    text = json.dumps(every).lower()
    for word in ("price match", "business account", "allergy"):
        assert word not in text
    assert "@" not in text


def test_a_ticket_reply_is_a_draft_and_a_person_sends_it(client):
    r = post(client, f"{T4}/send", {"sent_by": "D. Carer"}, 409)
    assert r["applied"] is False and "save_ticket_reply" in r["detail"]
    first = post(client, f"{T4}/reply", REPLY)
    assert first["kind"] == "draft" and first["draft"]["version"] == 1 and first["ticket_status"] == "open"
    assert post(client, f"{T4}/reply", {**REPLY, "drafted_by": "Customer Service"})["draft"]["version"] == 2
    assert get(client, "/care/tickets", status="open")["count"] == 20
    assert [t["reply_drafts"] for t in get(client, "/care/tickets")["items"] if t["ticket_id"] == "CT-2611-004"] == [2]
    post(client, f"{T4}/send", {}, 422)
    sent = post(client, f"{T4}/send", {"sent_by": "D. Carer"})
    assert sent["kind"] == "change" and sent["status"] == "replied" and sent["ticket"]["reply_sent"]["version"] == 2
    assert sent["ticket"]["reply_sent"]["to"] == "alaric.penhallow-stone@mail.invalid"
    assert "already replied to by D. Carer" in post(client, f"{T4}/send", {"sent_by": "X"}, 409)["detail"]
    assert post(client, "/care/tickets/CT-2611-014/reply", NO_ANSWER)["draft"]["proposed_next_step"] == "pass_to_a_colleague"
    assert get(client, "/admin/state")["counts"]["customer_tickets_open"] == 19
    assert get(client, "/care/tickets/CT-0000-000", 404)["applied"] is False


@pytest.mark.parametrize("body, status, words", [
    ({**REPLY, "articles_cited": ["HA-99"]}, 404, "No help article with id HA-99"),
    ({**REPLY, "articles_cited": []}, 422, "needs at least one article"),
    ({**NO_ANSWER, "articles_cited": ["HA-01"]}, 422, "no_article_answers goes with an empty articles_cited"),
    ({**NO_ANSWER, "proposed_next_step": "send_reply"}, 422, "pass_to_a_colleague"),
    ({**REPLY, "answer_status": "guessed"}, 422, "answer_status"),
    ({**REPLY, "reply": ""}, 422, "reply"),
])
def test_a_ticket_reply_that_does_not_fit_is_refused_with_a_readable_message(client, body, status, words):
    r = post(client, f"{T4}/reply", body, status)
    assert r["applied"] is False and words in r["detail"], r["detail"]
    assert get(client, T4)["reply_drafts"] == []


# ================================================================ complaints

CLASSIFY = {"classification": "repeat_contact", "procedure_section": "2.2", "response_due": "2026-11-26",
            "what_happened": "A refund of 28.00 was approved on 2026-11-12 and has not been paid. Two earlier contacts."}
RESPONSE = {"response": "Thank you for writing again about your refund.", "proposed_next_step": "send_response"}
C2 = "/care/complaints/CM-2611-02"


def test_the_complaints_procedure_is_served_and_is_the_document_in_the_policy_library(client):
    p = get(client, "/care/complaints-procedure")
    assert (p["document"], p["version"], p["owner"]) == ("Complaints Procedure", "2.1", "Customer Relations Lead")
    table = [r for r in rows("", COMPLAINTS) if len(r) == 5 and r[0] in "ABCD"]
    assert len(table) == 4
    for c, (letter, written, sect, due, _) in zip(p["classes"], table):
        assert (c["class"], f"`{c['classification']}`", c["section"], f"{c['response_due_days']} days") == (letter, written, sect, due)
    assert p["order_when_more_than_one_fits"] == [c["classification"] for c in p["classes"]]
    assert p["text"] == complaints_procedure_markdown() and "invented" in p["notice"]
    for s in p["sections"]:
        for c in s["clauses"]:
            assert f"{c['clause']} {c['text']}" in p["text"]
    doc = LIBRARY / "complaints-procedure-v2.1.md"
    if doc.exists():
        assert doc.read_text(encoding="utf-8") == p["text"] and "invented" in p["text"].splitlines()[0]


def test_the_eight_complaints_match_the_scenario_table(client, store):
    table = rows("CM-", COMPLAINTS)
    listed = get(client, "/care/complaints")
    days = {c["classification"]: c["response_due_days"] for c in get(client, "/care/complaints-procedure")["classes"]}
    sections = {c["classification"]: c["section"] for c in get(client, "/care/complaints-procedure")["classes"]}
    assert listed["count"] == 8 == len(table) and {c["status"] for c in listed["items"]} == {"open"}
    for cid, received, customer, order, earlier, klass, sect, due in table:
        c = get(client, f"/care/complaints/{cid}")
        assert (c["received_on"], c["customer_name"], c["order_number"], len(c["contact_history"])) == (
            received, customer, order, int(earlier)), cid
        assert store.data["complaint_answers"][cid] == {"classification": klass, "response_due": due}, cid
        assert due == (date.fromisoformat(received) + timedelta(days=days[klass])).isoformat() and sect == sections[klass]
        assert get(client, f"/orders/orders/{order}")["customer_name"] == customer
        assert all(h["date"] < received and h["about_the_same_matter"] for h in c["contact_history"])
        assert c["retailer_date"] == TODAY and c["classifications"] == [] and c["response_drafts"] == []
        # the right class follows from the complaint itself, read in the order the procedure gives
        words = c["message"].lower()
        if any(w in words for w in ("cut my finger", "legal action")):
            assert klass == "safety_or_legal", cid
        elif int(earlier) >= 2:
            assert klass == "repeat_contact", cid
        else:
            assert klass in ("service_failure", "policy_disagreement"), cid
    assert [r[0] for r in table if r[5] == "safety_or_legal"] == ["CM-2611-03", "CM-2611-06"]
    assert [r[0] for r in table if r[7] < TODAY] == ["CM-2611-08"]
    assert [h["date"] for h in get(client, f"{C2}")["contact_history"]] == ["2026-11-15", "2026-11-18"]
    assert "classification" not in json.dumps(get(client, "/care/complaints/CM-2611-03")["contact_history"])
    assert get(client, "/care/complaints/CM-0000-00", 404)["applied"] is False


def test_a_complaint_is_classified_then_answered_and_a_person_sends(client):
    r = post(client, f"{C2}/response", RESPONSE, 409)
    assert r["applied"] is False and "save_complaint_classification" in r["detail"]
    post(client, f"{C2}/send", {"sent_by": "E. Lead"}, 409)
    first = post(client, f"{C2}/classification", CLASSIFY)
    assert first["kind"] == "draft" and first["draft"]["version"] == 1 and first["complaint_status"] == "open"
    r = post(client, f"{C2}/send", {"sent_by": "E. Lead"}, 409)
    assert "save_complaint_response" in r["detail"]
    draft = post(client, f"{C2}/response", RESPONSE)
    assert draft["kind"] == "draft" and draft["draft"]["version"] == 1
    assert post(client, f"{C2}/response", {**RESPONSE, "drafted_by": "Complaint Handling"})["draft"]["version"] == 2
    row = [c for c in get(client, "/care/complaints")["items"] if c["complaint_id"] == "CM-2611-02"][0]
    assert (row["classifications"], row["response_drafts"], row["status"], row["earlier_contacts"]) == (1, 2, "open", 2)
    sent = post(client, f"{C2}/send", {"sent_by": "E. Lead"})
    assert sent["kind"] == "change" and sent["status"] == "responded" and sent["complaint"]["response_sent"]["version"] == 2
    assert "already responded to by E. Lead" in post(client, f"{C2}/send", {"sent_by": "X"}, 409)["detail"]
    assert get(client, "/care/complaints", status="responded")["count"] == 1
    assert get(client, "/admin/state")["counts"]["complaints_open"] == 7


def test_complaint_drafts_that_do_not_fit_are_refused_with_a_readable_message(client):
    for change, words in (({"classification": "angry"}, "classification"), ({"response_due": "26 November"}, "response_due"),
                          ({"response_due": "2026-11-20"}, "before the day the complaint was received"),
                          ({"what_happened": ""}, "what_happened")):
        r = post(client, f"{C2}/classification", {**CLASSIFY, **change}, 422)
        assert r["applied"] is False and words in r["detail"], r["detail"]
    assert get(client, C2)["classifications"] == []
    # a safety or legal complaint always goes to the Customer Relations Lead
    c3 = "/care/complaints/CM-2611-03"
    post(client, f"{c3}/classification", {**CLASSIFY, "classification": "safety_or_legal", "procedure_section": "2.1",
                                         "response_due": "2026-11-25"})
    r = post(client, f"{c3}/response", RESPONSE, 422)
    assert "pass_to_the_customer_relations_lead" in r["detail"] and get(client, c3)["response_drafts"] == []
    ok = post(client, f"{c3}/response", {"response": "Thank you for telling us. A colleague will contact you today.",
                                         "proposed_next_step": "pass_to_the_customer_relations_lead"})
    assert ok["draft"]["proposed_next_step"] == "pass_to_the_customer_relations_lead"
    post(client, f"{c3}/response", {"response": "x", "proposed_next_step": "pay_compensation"}, 422)
    post(client, "/care/complaints/CM-0000-00/classification", CLASSIFY, 404)


# ================================================================ public reviews

P1 = "/care/reviews/PR-2611-01"
P3 = "/care/reviews/PR-2611-03"
MARK = {"action": "mark_for_a_person", "reason": "The review says metal wire was found in a loaf."}


def test_the_twelve_reviews_match_the_scenario_table(client, store):
    table = rows("PR-", REVIEWS)
    listed = get(client, "/care/reviews")
    assert listed["count"] == 12 == len(table)
    for row, (rid, posted, site, about, rating, name, action) in zip(listed["items"], table):
        assert (row["review_id"], row["posted_on"], row["review_site"], row["about"], row["rating"], row["reviewer_display_name"]) == (
            rid, posted, site, about, int(rating), name)
        assert store.data["review_answers"][rid] == action and row["status"] == "unanswered" and row["marked_for_a_person"] is False
        if about != "online shop":
            assert get(client, f"/stores/sites/{about}")["kind"] == "store"
    assert [r[0] for r in table if r[6] == "mark_for_a_person"] == ["PR-2611-03", "PR-2611-06"]
    assert "metal wire" in get(client, P3)["text"] and "solicitor" in get(client, "/care/reviews/PR-2611-06")["text"]
    assert [r["review_id"] for r in get(client, "/care/reviews", max_rating=1)["items"]] == ["PR-2611-03", "PR-2611-06", "PR-2611-10"]
    assert "review_answers" not in json.dumps(listed) and "mark_for_a_person" not in json.dumps(listed).replace("marked_for_a_person", "")
    assert get(client, "/care/reviews/PR-0000-00", 404)["applied"] is False


def test_the_brand_voice_guide_is_in_the_policy_library():
    doc = LIBRARY / "brand-voice-guide.md"
    if not doc.exists():
        pytest.skip("the policy library is not next to this copy of the retailer")
    text = doc.read_text(encoding="utf-8")
    assert "invented" in text.splitlines()[0] and "Version: 1.2" in text
    rules = [line.split()[0] for line in text.splitlines() if line.startswith("V-")]
    assert rules == [f"V-{n}" for n in range(1, 14)]
    for words in ("no longer than 80 words", "care@rowanmere-market.example", "The Rowanmere Market team", "gets no drafted reply"):
        assert words in text
    assert "80 words" in REVIEWS and "The Rowanmere Market team" in REVIEWS


def test_a_review_reply_is_a_draft_and_a_person_publishes(client):
    r = post(client, f"{P1}/publish", {"published_by": "E. Lead"}, 409)
    assert r["applied"] is False and "save_review_reply" in r["detail"]
    first = post(client, f"{P1}/reply", {"action": "reply", "reply": "Thank you, harbourwalker22.\nThe Rowanmere Market team"})
    assert first["kind"] == "draft" and first["draft"]["version"] == 1 and first["review_status"] == "unanswered"
    assert first["marked_for_a_person"] is False
    done = post(client, f"{P1}/publish", {"published_by": "E. Lead"})
    assert done["kind"] == "change" and done["status"] == "reply_published" and done["review"]["reply_published"]["version"] == 1
    assert "already published by E. Lead" in post(client, f"{P1}/publish", {"published_by": "X"}, 409)["detail"]
    post(client, f"{P1}/reply", {"action": "reply", "reply": "Again."}, 409)
    # a review that describes a safety matter is marked, and holds no reply to publish
    marked = post(client, f"{P3}/reply", MARK)
    assert marked["marked_for_a_person"] is True and marked["draft"]["reply"] == "" and marked["review_status"] == "unanswered"
    seen = get(client, P3)
    assert seen["marked_for_a_person"] is True and seen["status"] == "unanswered"
    r = post(client, f"{P3}/publish", {"published_by": "E. Lead"}, 409)
    assert "marked for a person and holds no reply" in r["detail"]
    assert get(client, "/care/reviews", status="reply_published")["count"] == 1
    assert get(client, "/admin/state")["counts"]["public_reviews_unanswered"] == 11


@pytest.mark.parametrize("body, words", [
    ({"action": "reply", "reply": "  "}, "needs the reply text"),
    ({"action": "mark_for_a_person", "reply": "Sorry to hear this.", "reason": "An injury."}, "empty reply and a reason"),
    ({"action": "mark_for_a_person"}, "empty reply and a reason"),
    ({"action": "ignore", "reply": "x"}, "action"),
])
def test_a_review_reply_that_does_not_fit_is_refused_with_a_readable_message(client, body, words):
    r = post(client, f"{P3}/reply", body, 422)
    assert r["applied"] is False and words in r["detail"], r["detail"]
    assert get(client, P3)["reply_drafts"] == []


# ================================================================ delivery notes

CLAIM = {"lines": [{"kind": "short_delivery", "item": "Mozzarella, shredded", "note_says": "500 kg", "received": "300 kg",
                    "quantity_claimed": 200, "unit": "kg", "amount_claimed": 4900.0}],
         "proposed_next_step": "send_claim", "message": "Delivery note DN-4135 says 500 kg. We received 300 kg."}
N6 = "/purchasing/delivery-notes/DN-4135"


def difference(client, note_number):
    """Set a note against its order and its receipt, the way a careful reader would: (kind, item, quantity, net amount)."""
    note = get(client, f"/purchasing/delivery-notes/{note_number}")
    po = get(client, f"/purchasing/purchase-orders/{note['po_number']}")
    receipt = get(client, "/purchasing/goods-receipts", po_number=note["po_number"])["items"][0]
    price = {x["item"]: x["unit_price"] for x in po["lines"]}
    got = {x["item"]: x["quantity_received"] for x in receipt["lines"]}
    extra = [x["item"] for x in receipt["lines"] if x["item"] not in price]
    out = []
    for x in note["lines"]:
        short = x["quantity_delivered"] - got.get(x["item"], 0)
        if short > 0:
            kind = "wrong_item" if extra else "damaged" if "crushed" in note["remarks_at_delivery"] else "short_delivery"
            out.append((kind, x["item"], short, round(short * price[x["item"]], 2)))
    return out


def test_the_eight_delivery_notes_match_the_scenario_table(client, store):
    table = rows("DN-", NOTES)
    listed = get(client, "/purchasing/delivery-notes")
    assert listed["count"] == 8 == len(table) and {n["status"] for n in listed["items"]} == {"received"}
    for row, (number, po, supplier, delivered, receipt, answer) in zip(listed["items"], table):
        assert (row["note_number"], row["po_number"], row["supplier_id"], row["delivered_on"], row["receipt_id"], row["claims"]) == (
            number, po, supplier, delivered, receipt, 0)
        found = difference(client, number)
        planted = [(a["kind"], a["item"], a["quantity_claimed"], a["amount_claimed"]) for a in store.data["delivery_note_answers"][number]]
        assert found == planted, number
        assert ("`no_claim`" in answer) == (found == []) and ("`send_claim`" in answer) == (found != [])
        for _, _, _, amount in found:
            assert f"{amount:,.2f} net" in answer, number
        note = get(client, f"/purchasing/delivery-notes/{number}")
        assert note["text"].startswith("INVENTED SAMPLE") and number in note["text"] and po in note["text"]
        assert [r["delivery_note"] for r in get(client, "/purchasing/goods-receipts", po_number=po)["items"]] == [number]
    assert difference(client, "DN-4135") == [("short_delivery", "Mozzarella, shredded", 200, 4900.00)]
    assert difference(client, "DN-4142") == [("wrong_item", "Pizza box, large", 8000, 4400.00)]
    assert difference(client, "DN-4149") == [("damaged", "Onions, white", 120, 336.00)]
    assert "9,636.00 net" in NOTES and 4900.00 + 4400.00 + 336.00 == 9636.00
    assert get(client, f"{N6}")["remarks_at_delivery"] == ""
    assert "small boxes, not large" in get(client, "/purchasing/delivery-notes/DN-4142")["remarks_at_delivery"]
    assert "6 cases of white onions (20 kg each) crushed" in get(client, "/purchasing/delivery-notes/DN-4149")["remarks_at_delivery"]
    small = get(client, "/purchasing/goods-receipts", po_number="PO-450161")["items"][0]["lines"]
    assert [(x["item"], x["quantity_received"]) for x in small] == [("Pizza box, medium", 12000), ("Pizza box, large", 0),
                                                                    ("Pizza box, small", 8000)]


def test_the_two_new_orders_have_a_receipt_and_no_invoice(client):
    for po, supplier, net, buyer in (("PO-450161", "SUP-302", 9440.00, "Dorian Ketterly-Voss"),
                                     ("PO-450164", "SUP-304", 5960.00, "Hesper Valdane-Orr")):
        x = get(client, f"/purchasing/purchase-orders/{po}")
        assert (x["supplier_id"], x["net_total"], x["buyer"], x["status"], x["invoice_numbers"]) == (supplier, net, buyer, "part_received", [])
        assert f"{net:,.2f} net" in NOTES and po in NOTES
    assert get(client, "/purchasing/invoices")["count"] == 6
    assert get(client, "/purchasing/purchase-orders/PO-450158")["invoice_numbers"] == ["INV-9034"]


def test_delivery_note_filters_and_404(client):
    assert [n["note_number"] for n in get(client, "/purchasing/delivery-notes", po_number="PO-450158")["items"]] == ["DN-4135"]
    assert get(client, "/purchasing/delivery-notes", supplier_id="SUP-302")["count"] == 3
    assert get(client, "/purchasing/delivery-notes", status="claim_sent")["count"] == 0
    assert "list_purchase_orders" in get(client, "/purchasing/delivery-notes", 404, po_number="PO-000000")["detail"]
    assert "list_delivery_notes" in get(client, "/purchasing/delivery-notes/DN-0000", 404)["detail"]
    assert client.get("/purchasing/delivery-notes", params={"status": "lost"}, headers=H).status_code == 422


def test_a_discrepancy_claim_is_a_draft_and_a_person_sends_it(client):
    r = post(client, f"{N6}/claim/send", {"sent_by": "F. Receiver"}, 409)
    assert r["applied"] is False and "save_discrepancy_claim" in r["detail"]
    first = post(client, f"{N6}/claim", CLAIM)
    assert first["kind"] == "draft" and first["draft"]["version"] == 1 and first["draft"]["total_claimed"] == 4900.00
    assert first["note_status"] == "received"
    assert post(client, f"{N6}/claim", {**CLAIM, "drafted_by": "Delivery Discrepancy"})["draft"]["version"] == 2
    sent = post(client, f"{N6}/claim/send", {"sent_by": "F. Receiver"})
    assert sent["kind"] == "change" and sent["status"] == "claim_sent" and sent["delivery_note"]["claim_sent"]["version"] == 2
    assert sent["delivery_note"]["claim_sent"]["to"] == "accounts@ilvane-valley-dairy.example"
    assert "already sent by F. Receiver" in post(client, f"{N6}/claim/send", {"sent_by": "X"}, 409)["detail"]
    # a note that agrees is saved with no line, and there is then nothing to send
    n1 = "/purchasing/delivery-notes/DN-4100"
    assert post(client, f"{n1}/claim", {"lines": [], "proposed_next_step": "no_claim"})["draft"]["total_claimed"] == 0
    assert "holds no line" in post(client, f"{n1}/claim/send", {"sent_by": "F. Receiver"}, 409)["detail"]
    assert get(client, "/admin/state")["counts"]["delivery_note_claims_sent"] == 1


@pytest.mark.parametrize("change, words", [
    ({"proposed_next_step": "no_claim"}, "no_claim goes with no lines"),
    ({"lines": []}, "send_claim needs at least one line"),
    ({"message": ""}, "send_claim needs at least one line and the message"),
    ({"lines": [{**CLAIM["lines"][0], "item": "Cheddar"}]}, "Cheddar is on neither"),
    ({"lines": [{**CLAIM["lines"][0], "kind": "stolen"}]}, "kind"),
    ({"lines": [{**CLAIM["lines"][0], "quantity_claimed": 0}]}, "quantity_claimed"),
    ({"proposed_next_step": "pay_less"}, "proposed_next_step"),
])
def test_a_claim_that_does_not_fit_is_refused_with_a_readable_message(client, change, words):
    r = post(client, f"{N6}/claim", {**CLAIM, **change}, 422)
    assert r["applied"] is False and words in r["detail"], r["detail"]
    assert get(client, N6)["claims"] == []
    post(client, "/purchasing/delivery-notes/DN-0000/claim", CLAIM, 404)


# ================================================================ supplier payments and questions

S_REPLY = {"answer_status": "answered_from_records", "reply": "INV-76410 was paid in full on 2026-11-10.",
           "records_cited": ["PAY-7003", "INV-76410"], "proposed_next_step": "send_reply"}
S_NONE = {"answer_status": "records_do_not_answer", "reply": "Our records hold no delivery slots. A colleague will reply.",
          "records_cited": [], "proposed_next_step": "refer_to_a_person"}
Q1 = "/purchasing/supplier-questions/SQ-2611-01"


def test_the_ten_payments_match_the_scenario_table(client):
    table = rows("PAY-", PAYMENTS)
    listed = get(client, "/purchasing/payments")
    assert listed["count"] == 10 == len(table) and listed["retailer_date"] == TODAY
    for pid, supplier, invoice, inv_date, inv_total, status, when, amount, deduction in table:
        p = get(client, f"/purchasing/payments/{pid}")
        assert (p["supplier_id"], p["invoice_number"], p["invoice_date"], p["invoice_total"], p["status"], p["amount"]) == (
            supplier, invoice, inv_date, num(inv_total), status, num(amount)), pid
        assert when == (p["paid_on"] if status == "paid" else p["scheduled_for"]) == p["due_date"]
        assert p["due_date"] == (date.fromisoformat(inv_date) + timedelta(days=45)).isoformat()
        assert (p["paid_on"] is None) == (status == "scheduled") == (p["due_date"] > TODAY)
        assert (p["deduction"]["amount"] if p["deduction"] else None) == (num(deduction) if deduction else None)
        assert p["amount"] == round(p["invoice_total"] - (p["deduction"]["amount"] if p["deduction"] else 0), 2)
        assert p["remittance_advice"] == (pid.replace("PAY", "RA") if status == "paid" else "")
    assert [r[5] for r in table].count("paid") == 6 and "six paid and four scheduled" in PAYMENTS
    d4 = get(client, "/purchasing/payments/PAY-7004")["deduction"]
    assert (d4["net"], d4["tax"], d4["amount"], d4["debit_note"]) == (310.00, 46.50, 356.50, "DBN-0412")
    d9 = get(client, "/purchasing/payments/PAY-7009")["deduction"]
    assert (d9["net"], d9["tax"], d9["amount"], d9["debit_note"]) == (840.00, 126.00, 966.00, "DBN-0431")
    assert [p["payment_id"] for p in get(client, "/purchasing/payments", invoice_number="INV-76410")["items"]] == ["PAY-7003"]
    assert get(client, "/purchasing/payments", supplier_id="SUP-301", status="scheduled")["count"] == 2
    assert get(client, "/purchasing/payments", invoice_number="INV-77102")["count"] == 0  # received, not paid, nothing scheduled
    assert "list_supplier_payments" in get(client, "/purchasing/payments/PAY-0000", 404)["detail"]
    # no payment is for one of the six invoices that are still to be matched
    assert not {p["invoice_number"] for p in listed["items"]} & {i["invoice_number"] for i in get(client, "/purchasing/invoices")["items"]}


def test_the_six_supplier_questions_and_the_records_that_answer_them(client, store):
    table = rows("SQ-", PAYMENTS)
    listed = get(client, "/purchasing/supplier-questions")
    assert listed["count"] == 6 == len(table) and {q["status"] for q in listed["items"]} == {"open"}
    for qid, received, supplier, _, answer, records in table:
        q = get(client, f"/purchasing/supplier-questions/{qid}")
        assert (q["received_on"], q["supplier_id"]) == (received, supplier), qid
        assert q["from_email"] == get(client, f"/purchasing/suppliers/{supplier}")["contact_email"]
        right = store.data["supplier_question_answers"][qid]
        assert right["records"] == ([] if records == "none" else records.split(", ")), qid
        assert (right["answer_status"] == "records_do_not_answer") == ("`refer_to_a_person`" in answer)
    answers = {r[0]: r[4] for r in table}
    p = get(client, "/purchasing/payments/PAY-7003")
    assert (p["paid_on"], p["amount"], p["remittance_advice"]) == ("2026-11-10", 30705.00, "RA-7003")
    assert all(x in answers["SQ-2611-01"] for x in ("2026-11-10", "30,705.00", "RA-7003"))
    p = get(client, "/purchasing/payments/PAY-7006")
    assert (p["scheduled_for"], p["amount"]) == ("2026-11-30", 9890.00) and "2026-11-30" in answers["SQ-2611-02"]
    p = get(client, "/purchasing/payments/PAY-7004")
    assert (p["invoice_total"], p["amount"], p["paid_on"]) == (7567.00, 7210.50, "2026-11-14")
    assert all(x in answers["SQ-2611-03"] for x in ("7,567.00", "7,210.50", "356.50", "310.00", "46.50", "DBN-0412"))
    assert "7,567.00" in get(client, "/purchasing/supplier-questions/SQ-2611-03")["message"]
    inv = get(client, "/purchasing/invoices/INV-77102")
    assert (inv["invoice_date"], inv["status"], inv["due_date"]) == ("2026-11-17", "received", "2027-01-01")
    assert all(x in answers["SQ-2611-05"] for x in ("2026-11-17", "2027-01-01"))
    gr = get(client, "/purchasing/goods-receipts", po_number="PO-450158")["items"][0]
    assert (gr["receipt_id"], gr["received_on"], gr["lines"][0]["quantity_received"]) == ("GR-60158", "2026-11-21", 300)
    # nothing in the system holds a delivery slot
    everything = json.dumps({k: v for k, v in store.data.items() if k in ("purchase_orders", "goods_receipts", "delivery_notes",
                                                                         "supplier_payments", "supplier_invoices", "suppliers")})
    assert "slot" not in everything and "13:00" not in everything
    assert get(client, "/purchasing/supplier-questions", supplier_id="SUP-303")["count"] == 2
    assert "list_supplier_questions" in get(client, "/purchasing/supplier-questions/SQ-0000-00", 404)["detail"]


def test_a_supplier_reply_is_a_draft_and_a_person_sends_it(client):
    r = post(client, f"{Q1}/send", {"sent_by": "C. Payer"}, 409)
    assert r["applied"] is False and "save_supplier_reply" in r["detail"]
    first = post(client, f"{Q1}/reply", S_REPLY)
    assert first["kind"] == "draft" and first["draft"]["version"] == 1 and first["question_status"] == "open"
    assert post(client, f"{Q1}/reply", {**S_REPLY, "drafted_by": "Supplier Query"})["draft"]["version"] == 2
    sent = post(client, f"{Q1}/send", {"sent_by": "C. Payer"})
    assert sent["kind"] == "change" and sent["status"] == "replied" and sent["supplier_question"]["reply_sent"]["version"] == 2
    assert sent["supplier_question"]["reply_sent"]["to"] == "accounts@tallowby-flour-mills.example"
    assert "already replied to by C. Payer" in post(client, f"{Q1}/send", {"sent_by": "X"}, 409)["detail"]
    none = post(client, "/purchasing/supplier-questions/SQ-2611-04/reply", S_NONE)
    assert none["draft"]["proposed_next_step"] == "refer_to_a_person"
    assert post(client, "/purchasing/supplier-questions/SQ-2611-06/reply",
                {**S_REPLY, "records_cited": ["GR-60158", "DN-4135", "PO-450158"]})["applied"] is True
    assert get(client, "/purchasing/supplier-questions", status="replied")["count"] == 1
    assert get(client, "/admin/state")["counts"]["supplier_questions_open"] == 5


@pytest.mark.parametrize("body, status, words", [
    ({**S_REPLY, "records_cited": ["PAY-9999"]}, 404, "PAY-9999"),
    ({**S_REPLY, "records_cited": []}, 422, "needs at least one record"),
    ({**S_NONE, "records_cited": ["PAY-7003"]}, 422, "records_do_not_answer goes with an empty records_cited"),
    ({**S_NONE, "proposed_next_step": "send_reply"}, 422, "refer_to_a_person"),
    ({**S_REPLY, "answer_status": "probably"}, 422, "answer_status"),
])
def test_a_supplier_reply_that_does_not_fit_is_refused_with_a_readable_message(client, body, status, words):
    r = post(client, f"{Q1}/reply", body, status)
    assert r["applied"] is False and words in r["detail"], r["detail"]
    assert get(client, Q1)["reply_drafts"] == []


# ================================================================ what is never served

def test_the_right_answers_are_kept_and_never_served(client, store):
    sizes = {"return_answers": 10, "fraud_answers": 4, "ticket_answers": 20, "complaint_answers": 8, "review_answers": 12,
             "delivery_note_answers": 8, "supplier_question_answers": 6}
    for name, n in sizes.items():
        assert len(store.data[name]) == n, name
    paths = ["/orders/orders?limit=200", "/orders/orders/RM-58192", "/orders/returns", "/orders/returns/RR-2611-07", "/orders/flagged",
             "/orders/customers/C-4020/history", "/care/tickets", "/care/tickets/CT-2611-014", "/care/complaints",
             "/care/complaints/CM-2611-06", "/care/reviews", "/care/reviews/PR-2611-03", "/purchasing/delivery-notes",
             "/purchasing/delivery-notes/DN-4142", "/purchasing/supplier-questions", "/purchasing/supplier-questions/SQ-2611-04"]
    for path in paths:
        body = client.get(path, headers=H).text
        assert client.get(path, headers=H).status_code == 200, path
        for word in ("_answers", "deciding_condition", "departs\"", "records_do_not_answer", "planted"):
            assert word not in body, (path, word)
    # a customer appears by name, id and an address that ends in .invalid, and nothing more
    for c in store.data["customers"].values():
        assert set(c) == {"customer_id", "name", "email", "account_opened", "account_changes", "earlier_orders"}
        assert c["email"].endswith("@mail.invalid")
    text = json.dumps(store.data["orders"]) + json.dumps(store.data["tickets"]) + json.dumps(store.data["complaints"])
    for word in ("phone_number", "street", "postcode", "date_of_birth", "card_number"):
        assert word not in text


# ================================================================ reset of each system

def test_each_system_is_put_back_without_the_others(client, store):
    post(client, f"{R1}/assessment", ASSESS)
    post(client, f"{F1}/review", REVIEW)
    post(client, f"{T4}/reply", REPLY)
    post(client, f"{C2}/classification", CLASSIFY)
    post(client, f"{P3}/reply", MARK)
    post(client, f"{N6}/claim", CLAIM)
    post(client, f"{Q1}/reply", S_REPLY)
    assert get(client, "/admin/state")["changed_by"] == {
        "care": ["complaints", "public_reviews", "tickets"], "orders": ["orders", "return_requests"],
        "purchasing": ["delivery_notes", "supplier_questions"]}

    r = post(client, "/admin/reset/orders")
    assert r["put_back"] == ["orders", "return_requests"]
    assert get(client, R1)["assessments"] == [] and get(client, "/orders/orders/RM-58192")["fraud_reviews"] == []
    assert len(get(client, T4)["reply_drafts"]) == 1 and len(get(client, N6)["claims"]) == 1

    r = post(client, "/admin/reset/care")
    assert r["put_back"] == ["complaints", "public_reviews", "tickets"]
    assert get(client, T4)["reply_drafts"] == [] and get(client, C2)["classifications"] == []
    assert get(client, P3)["marked_for_a_person"] is False and len(get(client, Q1)["reply_drafts"]) == 1

    r = post(client, "/admin/reset/purchasing")
    assert r["put_back"] == ["delivery_notes", "supplier_questions"]
    assert store.data == build_all(TODAY_D) and store.changed == {}


def test_arrivals_go_back_with_the_system_they_are_for(client, store):
    for kind in ("customer-ticket", "return-request", "complaint", "public-review", "flagged-order", "delivery-note",
                 "supplier-question"):
        simulate(client, kind)
    changed = get(client, "/admin/state")["changed_by"]
    assert changed == {"care": ["complaint_answers", "complaints", "public_reviews", "review_answers", "ticket_answers", "tickets"],
                       "orders": ["orders", "return_requests"],
                       "purchasing": ["delivery_note_answers", "delivery_notes", "goods_receipts", "purchase_orders",
                                      "supplier_question_answers", "supplier_questions"]}
    post(client, "/admin/reset/orders")
    assert len(store.data["orders"]) == 43 and len(store.data["return_requests"]) == 10 and len(store.data["tickets"]) == 21
    assert simulate(client, "return-request")["item_id"] == "RR-2611-51"  # the count of arrivals went back with the system
    post(client, "/admin/reset/care")
    post(client, "/admin/reset/purchasing")
    post(client, "/admin/reset/orders")
    assert store.data == build_all(TODAY_D) and store.simulated == {}
    assert {k: v for k, v in store.counters.items() if k != "event"} == {}


def test_the_data_follows_the_retailer_date(client):
    later = build_all(date(2026, 12, 3))
    assert "RR-2612-01" in later["return_requests"] and "CT-2612-001" in later["tickets"] and "SQ-2612-01" in later["supplier_questions"]
    assert later["orders"]["RM-58162"]["delivery"]["promised_date"] == "2026-11-30"
    assert later["complaints"]["CM-2612-08"]["received_on"] == "2026-11-26"
    assert later["supplier_payments"]["PAY-7006"]["due_date"] == "2026-12-09"
    january = build_all(date(2027, 1, 5))  # a month with no till refund to point at still builds
    assert len(january["orders"]) == 43 and len(january["customers"]["C-4023"]["earlier_orders"]) == 11


# ================================================================ events

def test_customer_ticket_four_templates_in_turn(client, store):
    right = ["HA-01", "HA-05", "HA-11", ""]
    for n in range(5):
        r = simulate(client, "customer-ticket")
        assert (r["event_type"], r["system"], r["item_id"]) == ("customer-ticket", "care", f"CT-2611-{101 + n}")
        t = get(client, f"/care/tickets/{r['item_id']}")
        assert t["status"] == "open" and t["received_on"] == TODAY and t["reply_drafts"] == []
        assert store.data["ticket_answers"][r["item_id"]] == right[n % 4]
        assert r["item_id"] in r["message"] and "care system" in r["message"] and "has arrived" in r["message"]
        assert "get_customer_ticket" in r["message"] and t["subject"] in r["message"]
    assert get(client, "/care/tickets")["count"] == 25
    for n, article in enumerate(right):
        assert (f"Article {article} answers it" if article else "No article answers it") in ARRIVALS.split("customer-ticket.")[1].split("\n\n")[1].splitlines()[n]


def test_return_request_four_templates_in_turn(client):
    right = [("Wooden train set", 9, "unopened", 38.00), ("Garden hose reel, 30 m", 41, "unopened", 47.00),
             ("Frozen fish fillets, 1 kg", 3, "unopened", 14.90), ("Toaster, four slice", 6, "opened", 42.00)]
    for n in range(5):
        r = simulate(client, "return-request")
        assert (r["event_type"], r["system"], r["item_id"]) == ("return-request", "orders", f"RR-2611-{51 + n}")
        x = get(client, f"/orders/returns/{r['item_id']}")
        item, day, condition, price = right[n % 4]
        assert (x["item"], x["days_since_delivery"], x["condition_reported"], x["unit_price"], x["requested_on"], x["status"]) == (
            item, day, condition, price, TODAY, "requested")
        assert x["order_number"] == f"RM-{59001 + n}" and get(client, f"/orders/orders/{x['order_number']}")["status"] == "delivered"
        assert r["item_id"] in r["message"] and x["order_number"] in r["message"] and "orders system" in r["message"]
        assert "get_return_request" in r["message"] and "get_returns_policy" in r["message"]
    assert get(client, "/orders/returns")["count"] == 15 and get(client, "/orders/orders", limit=200)["total"] == 48
    for words in ("approve, 38.00", "refuse under 1.2", "refuse under 3.1", "Refuse under 2.2"):
        assert words in ARRIVALS


def test_complaint_four_templates_in_turn(client, store):
    right = [("service_failure", 0, "2026-12-04"), ("repeat_contact", 2, "2026-11-29"), ("safety_or_legal", 0, "2026-11-26"),
             ("policy_disagreement", 0, "2026-12-08")]
    for n in range(5):
        r = simulate(client, "complaint")
        assert (r["event_type"], r["system"], r["item_id"]) == ("complaint", "care", f"CM-2611-{51 + n}")
        c = get(client, f"/care/complaints/{r['item_id']}")
        klass, earlier, due = right[n % 4]
        assert (c["received_on"], len(c["contact_history"]), c["status"]) == (TODAY, earlier, "open")
        assert store.data["complaint_answers"][r["item_id"]] == {"classification": klass, "response_due": due}
        assert f"`{klass}`, due {due}" in ARRIVALS
        assert get(client, f"/orders/orders/{c['order_number']}")["customer_name"] == c["customer_name"]
        assert r["item_id"] in r["message"] and c["order_number"] in r["message"] and "care system" in r["message"]
        assert "get_complaint" in r["message"] and f"{earlier} earlier contact" in r["message"]
    assert get(client, "/care/complaints")["count"] == 13


def test_public_review_four_templates_in_turn(client, store):
    right = [("S-104", 5, "reply"), ("online shop", 2, "reply"), ("S-107", 3, "reply"), ("S-101", 1, "mark_for_a_person")]
    for n in range(5):
        r = simulate(client, "public-review")
        assert (r["event_type"], r["system"], r["item_id"]) == ("public-review", "care", f"PR-2611-{51 + n}")
        x = get(client, f"/care/reviews/{r['item_id']}")
        about, rating, action = right[n % 4]
        assert (x["about"], x["rating"], x["posted_on"], x["status"], x["reply_drafts"]) == (about, rating, TODAY, "unanswered", [])
        assert store.data["review_answers"][r["item_id"]] == action
        assert r["item_id"] in r["message"] and x["review_site"] in r["message"] and "care system" in r["message"]
        assert "get_public_review" in r["message"]
    assert "allergic reaction" in get(client, "/care/reviews/PR-2611-54")["text"]
    assert get(client, "/care/reviews")["count"] == 17


def test_flagged_order_four_templates_in_turn(client):
    right = [("C-4031", 874.95, 3, 4, 49.00, 62.25), ("C-4032", 578.00, 1, 4, 184.50, 590.00),
             ("C-4033", 757.00, 3, 5, 42.00, 58.75), ("C-4034", 70.10, 1, 5, 65.80, 72.45)]
    for n in range(4):
        r = simulate(client, "flagged-order")
        assert (r["event_type"], r["system"], r["item_id"]) == ("flagged-order", "orders", f"RM-{59501 + n}")
        o = get(client, f"/orders/orders/{r['item_id']}")
        customer, total, reasons, earlier, average, highest = right[n]
        assert (o["customer_id"], o["total"], len(o["flag"]["reasons"]), o["status"], o["placed_on"]) == (
            customer, total, reasons, "awaiting_fraud_review", TODAY)
        h = get(client, f"/orders/customers/{customer}/history")
        assert (h["orders_count"], h["average_total"], h["highest_total"]) == (earlier + 1, average, highest)
        assert f"Customer {customer}" in ARRIVALS and f"{total:,.2f}" in ARRIVALS and f"{average:,.2f}" in ARRIVALS.replace("590.00", "184.50")
        assert r["item_id"] in r["message"] and "orders system" in r["message"] and "flagged for a fraud review" in r["message"]
        assert "get_customer_order_history" in r["message"]
    first, third = get(client, "/orders/orders/RM-59501"), get(client, "/orders/orders/RM-59503")
    assert first["device_first_seen_on_this_order"] and first["delivery"]["address_first_used_on_this_order"]
    assert third["payment"]["card_first_used_on_this_order"] and third["delivery"]["collect_site_id"] == "S-103"
    second = get(client, "/orders/customers/C-4032/history")["orders"]
    assert [(x["total"], x["items"]) for x in second if x["total"] == 590.00] == [(590.00, "two tablet computers")]
    assert simulate(client, "flagged-order")["item_id"] == "RM-59505"
    assert get(client, "/orders/flagged")["count"] == 9


def test_delivery_note_four_templates_in_turn(client, store):
    right = [[], [("short_delivery", "Butter, unsalted", 20, 620.00)], [("wrong_item", "Pizza box, medium", 10000, 4200.00)],
             [("damaged", "Green peppers", 40, 248.00)]]
    for n in range(5):
        r = simulate(client, "delivery-note")
        assert (r["event_type"], r["system"], r["item_id"]) == ("delivery-note", "purchasing", f"DN-{4501 + n}")
        note = get(client, f"/purchasing/delivery-notes/{r['item_id']}")
        assert (note["po_number"], note["receipt_id"], note["delivered_on"], note["status"]) == (
            f"PO-{450301 + n}", f"GR-{60301 + n}", TODAY, "received")
        assert difference(client, r["item_id"]) == right[n % 4], n
        for _, _, _, amount in right[n % 4]:
            assert f"{amount:,.2f} net" in ARRIVALS
        assert r["item_id"] in r["message"] and note["po_number"] in r["message"] and "purchasing system" in r["message"]
        assert "has arrived" in r["message"] and "get_delivery_note" in r["message"]
    assert len(store.data["delivery_notes"]) == 13 and len(store.data["purchase_orders"]) == 13
    assert get(client, "/purchasing/invoices")["count"] == 6


def test_supplier_question_four_templates_in_turn(client, store):
    right = [("SUP-301", ["PAY-7001"]), ("SUP-303", ["PAY-7007"]), ("SUP-302", ["PAY-7009"]), ("SUP-304", [])]
    for n in range(5):
        r = simulate(client, "supplier-question")
        assert (r["event_type"], r["system"], r["item_id"]) == ("supplier-question", "purchasing", f"SQ-2611-{51 + n}")
        q = get(client, f"/purchasing/supplier-questions/{r['item_id']}")
        supplier, records = right[n % 4]
        assert (q["supplier_id"], q["received_on"], q["status"]) == (supplier, TODAY, "open")
        assert store.data["supplier_question_answers"][r["item_id"]]["records"] == records
        for record in records:
            assert f"payment {record}" in ARRIVALS
        assert r["item_id"] in r["message"] and q["supplier_name"] in r["message"] and "purchasing system" in r["message"]
        assert "get_supplier_question" in r["message"]
    assert get(client, "/purchasing/supplier-questions")["count"] == 11
    assert all(x in ARRIVALS for x in ("2026-10-30: 12,880.00", "2026-12-06: 15,352.50", "966.00", "DBN-0431", "10,143.00"))


def test_a_new_item_never_takes_an_id_of_the_starting_data(client, store):
    store.data["tickets"]["CT-2611-101"] = {"ticket_id": "CT-2611-101", "status": "open"}
    store.data["orders"]["RM-59001"] = dict(store.data["orders"]["RM-58101"], order_number="RM-59001")
    assert simulate(client, "customer-ticket")["item_id"] == "CT-2611-102"
    assert simulate(client, "return-request")["item_id"] == "RR-2611-51"
    assert get(client, "/orders/returns/RR-2611-51")["order_number"] == "RM-59002"


def test_every_new_kind_can_be_subscribed_to_and_is_logged(client):
    kinds = ["customer-ticket", "return-request", "complaint", "public-review", "flagged-order", "delivery-note", "supplier-question"]
    for kind in kinds:
        sub = client.post("/admin/subscriptions", json={"event_kind": kind, "url": "http://127.0.0.1:9/a"}, headers=H)
        assert sub.status_code == 200 and sub.json()["subscription"]["event_kind"] == kind
        simulate(client, kind)
    created = [e for e in get(client, "/admin/events")["items"] if e["status"] == "created"]
    assert [e["event_type"] for e in created] == kinds and all(e["subscribers"] == 1 for e in created)
    unknown = client.post("/admin/simulate/lost-parcel", headers=H)
    assert unknown.status_code == 404 and all(kind in unknown.json()["detail"] for kind in kinds)
    text = client.get("/").text
    assert all(kind in text for kind in kinds)


# ================================================================ the MCP door and the OpenAPI documents

def tools(client, system):
    body = {"jsonrpc": "2.0", "id": 1, "method": "tools/list"}
    return {t["name"]: t for t in client.post(f"/{system}/mcp", json=body, headers={"X-API-Key": KEY}).json()["result"]["tools"]}


def call(client, system, name, arguments):
    body = {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": name, "arguments": arguments}}
    return client.post(f"/{system}/mcp", json=body, headers={"X-API-Key": KEY}).json()["result"]


def test_the_drafts_of_version_1_2_are_described_with_their_accepted_values(client):
    orders, care, purchasing = tools(client, "orders"), tools(client, "care"), tools(client, "purchasing")
    assert len(orders) == 14 and len(care) == 20 and len(purchasing) == 20
    a = orders["save_return_assessment"]["inputSchema"]
    assert set(a["required"]) == {"request_id", "conditions", "proposed_decision"} and "$ref" not in json.dumps(a)
    assert a["properties"]["proposed_decision"]["enum"] == ["approve", "refuse", "refer_to_a_person"]
    assert a["properties"]["conditions"]["items"]["properties"]["result"]["enum"] == ["met", "not_met", "does_not_apply"]
    f = orders["save_fraud_review"]["inputSchema"]
    assert f["properties"]["proposed_decision"]["enum"] == ["release", "hold"]
    assert f["properties"]["signals"]["items"]["properties"]["signal"]["enum"] == [
        "device", "delivery_address", "basket_value", "payment_method", "items", "delivery_method", "account_change",
        "earlier_refund", "other"]
    assert care["save_ticket_reply"]["inputSchema"]["properties"]["answer_status"]["enum"] == ["answered_from_articles", "no_article_answers"]
    assert care["save_ticket_reply"]["inputSchema"]["properties"]["proposed_next_step"]["enum"] == ["send_reply", "pass_to_a_colleague"]
    assert care["save_complaint_classification"]["inputSchema"]["properties"]["classification"]["enum"] == [
        "safety_or_legal", "repeat_contact", "service_failure", "policy_disagreement"]
    assert care["save_complaint_response"]["inputSchema"]["properties"]["proposed_next_step"]["enum"] == [
        "send_response", "pass_to_the_customer_relations_lead"]
    assert care["save_review_reply"]["inputSchema"]["properties"]["action"]["enum"] == ["reply", "mark_for_a_person"]
    c = purchasing["save_discrepancy_claim"]["inputSchema"]
    assert c["properties"]["lines"]["items"]["properties"]["kind"]["enum"] == ["short_delivery", "wrong_item", "damaged"]
    assert c["properties"]["proposed_next_step"]["enum"] == ["send_claim", "no_claim", "refer_to_the_buyer"]
    s = purchasing["save_supplier_reply"]["inputSchema"]
    assert s["properties"]["answer_status"]["enum"] == ["answered_from_records", "records_do_not_answer"]
    assert s["properties"]["proposed_next_step"]["enum"] == ["send_reply", "refer_to_a_person"]
    assert set(orders["search_orders"]["inputSchema"]["properties"]) == {"order_number", "customer_surname", "customer_email", "customer_id", "status",
                                                                         "limit", "offset"}
    assert set(orders["hold_flagged_order"]["inputSchema"]["required"]) == {"order_number", "held_by", "reason"}


def test_the_mcp_door_reads_and_writes_through_and_gives_the_refusal_in_words(client, store):
    r = call(client, "orders", "get_delivery_scans", {"order_number": "RM-58161"})
    assert not r.get("isError") and json.loads(r["content"][0]["text"])["count"] == 2
    r = call(client, "care", "search_help_articles", {"q": "gift card expire"})
    assert json.loads(r["content"][0]["text"])["items"][0]["article_id"] == "HA-07"
    r = call(client, "purchasing", "list_supplier_payments", {"invoice_number": "INV-5066"})
    assert json.loads(r["content"][0]["text"])["items"][0]["amount"] == 7210.50
    r = call(client, "orders", "approve_return", {"request_id": "RR-2611-01", "approved_by": "G. Leader"})
    assert r["isError"] is True and "409" in r["content"][0]["text"] and "save_return_assessment" in r["content"][0]["text"]
    r = call(client, "orders", "save_return_assessment", {"request_id": "RR-2611-01", **ASSESS, "drafted_by": "a test"})
    assert not r.get("isError") and store.data["return_requests"]["RR-2611-01"]["assessments"][0]["drafted_by"] == "a test"
    r = call(client, "orders", "save_return_assessment", {"request_id": "RR-2611-01", **ASSESS, "refund_amount": 99})
    assert r["isError"] is True and "422" in r["content"][0]["text"] and "above the price paid" in r["content"][0]["text"]
    r = call(client, "care", "save_review_reply", {"review_id": "PR-2611-06", **MARK})
    assert not r.get("isError") and json.loads(r["content"][0]["text"])["marked_for_a_person"] is True
    r = call(client, "care", "publish_review_reply", {"review_id": "PR-2611-06", "published_by": "E. Lead"})
    assert r["isError"] is True and "holds no reply" in r["content"][0]["text"]
    r = call(client, "purchasing", "save_discrepancy_claim", {"note_number": "DN-4149", "lines": [
        {"kind": "damaged", "item": "Onions, white", "note_says": "800 kg", "received": "680 kg", "quantity_claimed": 120,
         "unit": "kg", "amount_claimed": 336.0}], "proposed_next_step": "send_claim", "message": "6 cases were crushed."})
    assert not r.get("isError") and store.data["delivery_notes"]["DN-4149"]["claims"][0]["total_claimed"] == 336.00
    r = call(client, "purchasing", "send_supplier_reply", {"question_id": "SQ-2611-02", "sent_by": "C. Payer"})
    assert r["isError"] is True and "409" in r["content"][0]["text"]
    r = call(client, "orders", "get_order", {"order_number": "RM-00000"})
    assert r["isError"] is True and "404" in r["content"][0]["text"]


def test_the_openapi_documents_describe_version_1_2(client):
    counts = {}
    for system in ("orders", "care", "purchasing"):
        doc = client.get(f"/{system}/openapi.json").json()
        assert doc["openapi"] == "3.0.3" and doc["info"]["version"] == "1.4.0" and "invented" in doc["info"]["description"]
        ops = [op for item in doc["paths"].values() for op in item.values()]
        counts[system] = len(ops)
        for op in ops:
            assert len(op["description"]) > 80 and op["summary"], op["operationId"]
            if op["operationId"].split("_")[0] in ("send", "publish", "approve", "refuse", "release", "hold", "raise"):
                assert op["summary"].endswith("(change)"), op["operationId"]
            if op["operationId"].startswith("save_"):
                assert op["summary"].endswith("(draft)"), op["operationId"]
    assert counts == {"orders": 14, "care": 20, "purchasing": 20}
    doc = client.get("/orders/openapi.json").json()
    assert set(doc["paths"]) == {"/orders", "/orders/{order_number}", "/orders/{order_number}/scans", "/returns-policy", "/returns",
                                 "/returns/{request_id}", "/returns/{request_id}/assessment", "/returns/{request_id}/approve",
                                 "/returns/{request_id}/refuse", "/flagged", "/customers/{customer_id}/history",
                                 "/flagged/{order_number}/review", "/flagged/{order_number}/release", "/flagged/{order_number}/hold"}
    assert "anyOf" not in json.dumps(doc) and "ApiKeyAuth" in doc["components"]["securitySchemes"]


def test_the_operations_version_1_added_to_keep_their_paths_and_shapes(client):
    """Agents built on care and purchasing rely on these. Version 1.2 adds beside them and changes none."""
    care = client.get("/care/openapi.json").json()["paths"]
    assert {"/feedback", "/feedback/{reference}", "/analysis/{period}", "/analysis"} <= set(care)
    assert care["/feedback"]["get"]["operationId"] == "list_guest_feedback" and care["/analysis"]["post"]["operationId"] == "save_feedback_analysis"
    p = client.get("/purchasing/openapi.json").json()["paths"]
    assert {"/suppliers", "/suppliers/{supplier_id}", "/purchase-orders", "/purchase-orders/{po_number}", "/goods-receipts",
            "/invoices", "/invoices/{invoice_number}", "/invoices/{invoice_number}/match", "/invoices/{invoice_number}/approve",
            "/invoices/{invoice_number}/query"} <= set(p)
    inv = get(client, "/purchasing/invoices/INV-77102")
    assert set(inv) == {"demo_data", "invoice_number", "supplier_id", "supplier_name", "invoice_date", "due_date", "po_number",
                        "status", "currency", "lines", "net", "tax", "total", "matches", "query", "approved_by", "approved_at", "text"}
    po = get(client, "/purchasing/purchase-orders/PO-450131")
    assert set(po) == {"demo_data", "po_number", "supplier_id", "supplier_name", "order_date", "buyer", "currency", "status",
                       "net_total", "lines", "goods_receipt_ids", "invoice_numbers"}
    gr = get(client, "/purchasing/goods-receipts", po_number="PO-450131")["items"][0]
    assert set(gr) == {"receipt_id", "po_number", "supplier_id", "supplier_name", "received_on", "received_by", "received_at",
                       "delivery_note", "lines"}
    fb = get(client, "/care/feedback/GF-2610-0001")
    assert set(fb) == {"demo_data", "reference", "date", "site_id", "channel", "rating", "comment"}
    assert get(client, "/care/feedback", limit=500)["total"] == 260


def test_the_landing_page_and_the_counts_show_version_1_2(client):
    text = client.get("/").text
    assert "The fourteen systems" in text and "/orders/openapi.json" in text and "/orders/mcp" in text
    for words in ("online orders", "return requests not decided", "customer tickets open", "complaints open",
                  "public reviews unanswered", "delivery notes", "supplier questions open"):
        assert words in text
    c = get(client, "/admin/state")["counts"]
    assert (c["online_orders"], c["orders_awaiting_fraud_review"], c["return_requests"], c["return_requests_not_decided"]) == (43, 4, 10, 10)
    assert (c["customer_tickets_open"], c["complaints_open"], c["public_reviews_unanswered"]) == (20, 8, 12)
    assert (c["delivery_notes"], c["delivery_note_claims_sent"], c["supplier_payments"], c["supplier_questions_open"]) == (8, 0, 10, 6)
    assert (c["purchase_orders"], c["goods_receipts"], c["supplier_invoices_received"]) == (8, 8, 6)
