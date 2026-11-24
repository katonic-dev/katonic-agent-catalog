"""The customer care desk's demo cases are this retailer's own records.

../retail/desks/customer-care/cases.json is written by make_cases.py in the same folder, from the seed
of this service at retailer date 2026-11-24: six customer tickets, the ten return requests, the eight
complaints and six public reviews. These tests fail when the file differs from what the script would
write, and when a case differs from what the service returns for that ticket, request, complaint or
review.

The module is skipped when the desk folder is not next to this copy of the retailer.
"""
import importlib.util
import json
import re
from pathlib import Path

import pytest

from conftest import H, TODAY

DESK = Path(__file__).resolve().parents[2] / "retail" / "desks" / "customer-care"
if not (DESK / "make_cases.py").is_file():
    pytest.skip("the customer care desk folder is not next to this copy of the retailer", allow_module_level=True)

TICKETS = ["CT-2611-001", "CT-2611-004", "CT-2611-011", "CT-2611-020", "CT-2611-014", "CT-2611-016"]
RETURNS = [f"RR-2611-{n:02d}" for n in range(1, 11)]
COMPLAINTS = [f"CM-2611-{n:02d}" for n in range(1, 9)]
REVIEWS = ["PR-2611-01", "PR-2611-02", "PR-2611-03", "PR-2611-05", "PR-2611-06", "PR-2611-10"]
KINDS = ["Customer ticket", "Return request", "Complaint", "Public review"]


def _script():
    spec = importlib.util.spec_from_file_location("customer_care_desk_make_cases", DESK / "make_cases.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _held() -> list:
    return json.loads((DESK / "cases.json").read_text(encoding="utf-8"))["cases"]


def _cases() -> dict:
    return {c["title"].split(" ")[0]: c for c in _held()}


class ApiSource:
    """The readers make_cases.py uses over the seed, here over the service's API."""

    def __init__(self, client):
        self.client = client

    def _one(self, path):
        answer = self.client.get(path, headers=H)
        assert answer.status_code == 200, path
        return answer.json()

    def ticket(self, number):
        return self._one(f"/care/tickets/{number}")

    def articles(self):
        return self._one("/care/help-articles")["items"]

    def return_request(self, number):
        return self._one(f"/orders/returns/{number}")

    def order(self, number):
        return self._one(f"/orders/orders/{number}")

    def scans(self, number):
        return self._one(f"/orders/orders/{number}/scans")["scans"]

    def returns_policy(self):
        return self._one("/orders/returns-policy")

    def complaint(self, number):
        return self._one(f"/care/complaints/{number}")

    def procedure(self):
        return self._one("/care/complaints-procedure")

    def review(self, number):
        return self._one(f"/care/reviews/{number}")


def test_cases_file_is_what_the_script_writes():
    held = (DESK / "cases.json").read_text(encoding="utf-8")
    assert held == _script().render(), "cases.json differs from what make_cases.py would write: run make_cases.py"


def test_the_thirty_cases_in_order_each_with_its_kind():
    held = _held()
    assert [c["title"].split(" ")[0] for c in held] == TICKETS + RETURNS + COMPLAINTS + REVIEWS
    assert [c["kind"] for c in held] == [KINDS[0]] * 6 + [KINDS[1]] * 10 + [KINDS[2]] * 8 + [KINDS[3]] * 6
    config = json.loads((DESK / "desk.config.json").read_text(encoding="utf-8"))
    assert list(config["routing"]["kinds"]) == KINDS
    assert len({k["agentEnv"] for k in config["routing"]["kinds"].values()}) == 4
    keys = {f["key"] for f in config["intake"]["fields"]}
    for c in held:
        assert set(c) - {"arrived_via"} == keys


def test_each_ticket_case_holds_what_the_service_returns(client):
    script, cases, source = _script(), _cases(), ApiSource(client)
    open_now = [t["ticket_id"] for t in client.get("/care/tickets", headers=H, params={"status": "open"}).json()["items"]]
    assert len(open_now) == 20 and set(TICKETS) <= set(open_now)
    articles = source.articles()
    assert [a["article_id"] for a in articles] == [f"HA-{n:02d}" for n in range(1, 13)]
    for number in TICKETS:
        assert cases[number] == script.ticket_case(source.ticket(number), articles)


def test_each_return_case_holds_what_the_service_returns(client):
    script, cases, source = _script(), _cases(), ApiSource(client)
    waiting = [r["request_id"] for r in client.get("/orders/returns", headers=H, params={"status": "requested"}).json()["items"]]
    assert sorted(waiting) == RETURNS
    policy = source.returns_policy()
    for number in RETURNS:
        request = source.return_request(number)
        assert cases[number] == script.return_case(request, source.order(request["order_number"]), policy)
        # The day number in the case is the one the service works out.
        assert f"day {request['days_since_delivery']} after delivery" in cases[number]["text"]


def test_each_complaint_case_holds_what_the_service_returns(client):
    script, cases, source = _script(), _cases(), ApiSource(client)
    open_now = [c["complaint_id"] for c in client.get("/care/complaints", headers=H, params={"status": "open"}).json()["items"]]
    assert sorted(open_now) == COMPLAINTS
    procedure = source.procedure()
    for number in COMPLAINTS:
        complaint = source.complaint(number)
        assert complaint["retailer_date"] == TODAY
        order = complaint["order_number"]
        assert cases[number] == script.complaint_case(complaint, source.order(order), source.scans(order), procedure, TODAY)


def test_each_review_case_holds_what_the_service_returns(client):
    script, cases, source = _script(), _cases(), ApiSource(client)
    guide = script.guide_text()
    assert "V-11" in guide and "V-13" in guide
    for number in REVIEWS:
        review = source.review(number)
        assert review["status"] == "unanswered"
        assert cases[number] == script.review_case(review, guide)


def test_the_spread_shows_every_right_answer(store):
    """The answer sets are never read by the script. Here they say that the cases chosen cover every kind of right answer."""
    data = store.data
    assert sorted(data["ticket_answers"][t] for t in TICKETS) == ["", "", "HA-01", "HA-05", "HA-09", "HA-12"]
    assert sorted({a["proposed_decision"] for a in data["return_answers"].values()}) == ["approve", "refer_to_a_person", "refuse"]
    assert {data["complaint_answers"][c]["classification"] for c in COMPLAINTS} == {
        "safety_or_legal", "repeat_contact", "service_failure", "policy_disagreement"}
    assert [r for r in REVIEWS if data["review_answers"][r] == "mark_for_a_person"] == ["PR-2611-03", "PR-2611-06"]
    assert [r for r, a in data["review_answers"].items() if a == "mark_for_a_person"] == ["PR-2611-03", "PR-2611-06"]


def test_a_case_shows_a_customer_by_name_order_number_and_invalid_address_only():
    for c in _held():
        whole = json.dumps(c)
        assert not re.search(r"\bC-40\d\d\b|CARD-\d|ADDR-\d|DEV-\d", whole), c["title"]
        for address in re.findall(r"[\w.+-]+@[\w.-]+\.[a-z]+", whole):
            assert address.endswith(".invalid") or address == "care@rowanmere-market.example", (c["title"], address)
        if c["kind"] != "Public review":
            assert c["email"].endswith("@mail.invalid")
        else:
            assert c["email"] == "" and c["order"] == ""
