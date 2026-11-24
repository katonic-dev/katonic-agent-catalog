"""Builds cases.json for the customer care desk from the invented retailer's own records.

Thirty cases, as the care and orders systems hold them when the retailer's date is 24 November 2026:
six customer tickets (four that a help article answers and two that none does), all ten return
requests, all eight complaints and six public reviews (two of them describe a safety or legal matter).
Nothing is typed here by hand: tickets, help articles, return requests, orders, carrier scans,
complaints, the returns policy, the complaints procedure and reviews come from the seed of the service
in ../../../demo-retailer. The Brand Voice Guide, which the service does not serve, is read from
../../policy-library. No server is started.

Each case carries the records its agent needs, because the desk's agents work from the message alone.
The service's own answer sets (which article answers a ticket, the right proposal for a return, the
class of a complaint, which reviews go to a person) are never read.

A case shows a customer by an invented name, an order number and an address that ends in .invalid, and
nothing else about the customer: no customer id, no card, address or device reference.

Usage, from anywhere:
    python make_cases.py           writes cases.json beside this file
    python make_cases.py --check   exits 1 if cases.json differs from what would be written

The test demo-retailer/tests/test_customer_care_desk_cases.py runs the same comparison, and builds
every case again from what the service returns.
Rowanmere Group is invented, and so is every record.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
RETAILER = HERE.parents[2] / "demo-retailer"
GUIDE = HERE.parents[1] / "policy-library" / "brand-voice-guide.md"
OUT = HERE / "cases.json"

RETAILER_DATE = date(2026, 11, 24)
# Four tickets that a help article answers, then two that none answers.
TICKETS = ["CT-2611-001", "CT-2611-004", "CT-2611-011", "CT-2611-020", "CT-2611-014", "CT-2611-016"]
RETURNS = [f"RR-2611-{n:02d}" for n in range(1, 11)]
COMPLAINTS = [f"CM-2611-{n:02d}" for n in range(1, 9)]
# Praise, criticism, something found in food, praise with criticism, a fall and a solicitor, one star about a colleague's manner.
REVIEWS = ["PR-2611-01", "PR-2611-02", "PR-2611-03", "PR-2611-05", "PR-2611-06", "PR-2611-10"]

KIND_TICKET = "Customer ticket"
KIND_RETURN = "Return request"
KIND_COMPLAINT = "Complaint"
KIND_REVIEW = "Public review"

COMMENT = ("Thirty invented cases for the demo: six customer tickets, ten return requests, eight complaints and six public "
           "reviews. Made by make_cases.py from the records the invented retailer (demo-retailer) holds at retailer date "
           "2026-11-24. Do not edit by hand: change the service's seed and run the script. Rowanmere Group, its customers "
           "and every record are invented.")

NO_ORDER = "none named"
NO_HISTORY = "None. The contact history holds no earlier contact."
NO_SCANS = "None. The order has no carrier scans."
NO_REFUND = "None on the order."


def money(v) -> str:
    return f"{v:,.2f}"


def words(value: str) -> str:
    return value.replace("_", " ")


def stars(n: int) -> str:
    return f"{n} star{'' if n == 1 else 's'}"


def days_between(first: str, second: str) -> int:
    return (date.fromisoformat(second) - date.fromisoformat(first)).days


def document_body(text: str) -> list:
    """A policy as lines for the case: the title line and the notice go, a section title loses its marks, and a
    numbered clause is written 1.1: so that the page sets it as a plain line."""
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("# ") or line.startswith("Rowanmere Group is invented"):
            continue
        if line.startswith("## "):
            out.append(line[3:])
        else:
            out.append(re.sub(r"^(\d+\.\d+) ", r"\1: ", line))
    return out


# ---------------------------------------------------------------- the blocks of a case's text

def order_lines(order: dict) -> list:
    return [f"{x['line_no']}. {x['item']} ({words(x['category'])}): {x['quantity']} at {money(x['unit_price'])}, "
            f"amount {money(x['amount'])}" for x in order["lines"]]


def ticket_text(ticket: dict, articles: list) -> str:
    lines = ["THE TICKET", f"Ticket: {ticket['ticket_id']}", f"Received: {ticket['received_on']}, by {ticket['channel']}",
             f"Customer: {ticket['customer_name']}", f"Email: {ticket['customer_email']}",
             f"Order: {ticket['order_number'] or NO_ORDER}", f"Subject: {ticket['subject']}", f"Message: {ticket['message']}",
             "THE HELP ARTICLES"]
    for a in articles:
        lines += [f"{a['article_id']} {a['title']}", a["body"], ""]
    return "\n".join(lines[:-1])


def return_text(request: dict, order: dict, policy: dict) -> str:
    day = days_between(request["delivered_on"], request["requested_on"])
    lines = ["THE RETURN REQUEST", f"Request: {request['request_id']}", f"Customer: {request['customer_name']}",
             f"Order: {request['order_number']}", f"Item: {request['item']}", f"Category: {words(request['category'])}",
             f"Quantity: {request['quantity']} of {request['quantity_bought']} bought",
             f"Price paid: USD {money(request['unit_price'])} each", f"Delivered: {request['delivered_on']}",
             f"Asked: {request['requested_on']}, day {day} after delivery", f"Reason: {words(request['reason'])}",
             f"Condition: {request['condition_reported']}", f"Photograph: {'attached' if request['photo_attached'] else 'none'}",
             f"Statement: {request['customer_statement']}",
             "THE ORDER", f"Order: {order['order_number']}, placed {order['placed_on']}", f"Status: {words(order['status'])}",
             "ORDER LINES"]
    lines += order_lines(order)
    lines += [f"Goods: USD {money(order['goods_total'])}", f"Delivery: USD {money(order['delivery_charge'])}",
              f"Total: USD {money(order['total'])}",
              "THE RETURNS POLICY"]
    lines += document_body(policy["text"])
    return "\n".join(lines)


def complaint_text(complaint: dict, order: dict, scans: list, procedure: dict, today: str) -> str:
    delivery = order["delivery"]
    lines = ["THE COMPLAINT", f"Complaint: {complaint['complaint_id']}",
             f"Received: {complaint['received_on']}, by {complaint['channel']}", f"Customer: {complaint['customer_name']}",
             f"Email: {complaint['customer_email']}", f"Order: {complaint['order_number']}",
             f"Subject: {complaint['subject']}", f"Message: {complaint['message']}", f"Today: {today}",
             "CONTACT HISTORY"]
    history = sorted(complaint["contact_history"], key=lambda h: h["date"])
    lines += [f"{h['date']}, by {h['channel']}: {h['summary']}" for h in history] or [NO_HISTORY]
    lines += ["THE ORDER", f"Order: {order['order_number']}, placed {order['placed_on']}", f"Status: {words(order['status'])}",
              f"Service: {words(delivery['method'])}, {words(delivery['service'])}"
              + (f", by {delivery['carrier']}" if delivery["carrier"] else ""),
              f"Promised: {delivery['promised_date']}",
              f"Delivered: {delivery['delivered_on'] + ', to ' + delivery['delivered_to'] if delivery['delivered_on'] else 'not yet'}",
              f"New date: {delivery['rescheduled_date'] or 'none set'}", "ORDER LINES"]
    lines += order_lines(order)
    lines += [f"Goods: USD {money(order['goods_total'])}", f"Delivery: USD {money(order['delivery_charge'])}",
              f"Total: USD {money(order['total'])}", "CHARGES AND REFUNDS"]
    lines += [f"Charged: USD {money(c['amount'])} on {c['charged_on']}" for c in order["payment"]["charges"]]
    lines += [f"Refund: USD {money(r['amount'])} for {r['for']}, approved {r['approved_on']}, "
              f"{'paid ' + r['paid_on'] if r['paid_on'] else 'not paid'}" for r in order["refunds"]] or [f"Refund: {NO_REFUND}"]
    lines.append("CARRIER SCANS")
    lines += [f"{s['time'].replace('T', ' ')[:16]}, {s['place']}: {s['text']}" for s in scans] or [NO_SCANS]
    lines.append("THE COMPLAINTS PROCEDURE")
    lines += document_body(procedure["text"])
    return "\n".join(lines)


def review_text(review: dict, guide: str) -> str:
    lines = ["THE REVIEW", f"Review: {review['review_id']}", f"Posted: {review['posted_on']}", f"Site: {review['review_site']}",
             f"About: {review['about']}", f"Rating: {stars(review['rating'])} of 5",
             f"Display name: {review['reviewer_display_name']}", f"Text: {review['text']}", "THE BRAND VOICE GUIDE"]
    lines += document_body(guide)
    return "\n".join(lines)


# ---------------------------------------------------------------- the cases

def ticket_case(ticket: dict, articles: list) -> dict:
    return {"title": f"{ticket['ticket_id']} from {ticket['customer_name']}", "kind": KIND_TICKET,
            "customer": ticket["customer_name"], "about": ticket["subject"], "order": ticket["order_number"],
            "email": ticket["customer_email"], "received_on": ticket["received_on"], "text": ticket_text(ticket, articles),
            "arrived_via": "feed"}


def return_case(request: dict, order: dict, policy: dict) -> dict:
    return {"title": f"{request['request_id']} from {request['customer_name']}", "kind": KIND_RETURN,
            "customer": request["customer_name"], "about": request["item"], "order": request["order_number"],
            "email": order["customer_email"], "received_on": request["requested_on"],
            "text": return_text(request, order, policy), "arrived_via": "feed"}


def complaint_case(complaint: dict, order: dict, scans: list, procedure: dict, today: str) -> dict:
    return {"title": f"{complaint['complaint_id']} from {complaint['customer_name']}", "kind": KIND_COMPLAINT,
            "customer": complaint["customer_name"], "about": complaint["subject"], "order": complaint["order_number"],
            "email": complaint["customer_email"], "received_on": complaint["received_on"],
            "text": complaint_text(complaint, order, scans, procedure, today), "arrived_via": "feed"}


def review_case(review: dict, guide: str) -> dict:
    return {"title": f"{review['review_id']} from {review['reviewer_display_name']}", "kind": KIND_REVIEW,
            "customer": review["reviewer_display_name"], "about": f"{stars(review['rating'])}, about {review['about']}",
            "order": "", "email": "", "received_on": review["posted_on"], "text": review_text(review, guide),
            "arrived_via": "feed"}


def guide_text() -> str:
    return GUIDE.read_text(encoding="utf-8")


class SeedSource:
    """The records as the service's seed holds them. The test has the same readers over the API."""

    def __init__(self, data: dict):
        self.data = data
        if str(RETAILER) not in sys.path:
            sys.path.insert(0, str(RETAILER))
        from retailer.seed_care_desk import COMPLAINTS_PROCEDURE, help_articles  # noqa: E402
        from retailer.seed_orders import RETURNS_POLICY  # noqa: E402

        self._articles, self._policy, self._procedure = help_articles(), RETURNS_POLICY, COMPLAINTS_PROCEDURE

    def ticket(self, number: str) -> dict:
        return self.data["tickets"][number]

    def articles(self) -> list:
        return self._articles

    def return_request(self, number: str) -> dict:
        return self.data["return_requests"][number]

    def order(self, number: str) -> dict:
        return self.data["orders"][number]

    def scans(self, number: str) -> list:
        return self.data["orders"][number]["scans"]

    def returns_policy(self) -> dict:
        return self._policy

    def complaint(self, number: str) -> dict:
        return self.data["complaints"][number]

    def procedure(self) -> dict:
        return self._procedure

    def review(self, number: str) -> dict:
        return self.data["public_reviews"][number]


def _seed() -> dict:
    """The service's starting data for the retailer date. Imported, never served."""
    if str(RETAILER) not in sys.path:
        sys.path.insert(0, str(RETAILER))
    from retailer.seed import build_all  # noqa: E402

    return build_all(RETAILER_DATE)


def build() -> dict:
    source = SeedSource(_seed())
    today, guide = RETAILER_DATE.isoformat(), guide_text()
    cases = [ticket_case(source.ticket(n), source.articles()) for n in TICKETS]
    for n in RETURNS:
        request = source.return_request(n)
        cases.append(return_case(request, source.order(request["order_number"]), source.returns_policy()))
    for n in COMPLAINTS:
        complaint = source.complaint(n)
        number = complaint["order_number"]
        cases.append(complaint_case(complaint, source.order(number), source.scans(number), source.procedure(), today))
    cases += [review_case(source.review(n), guide) for n in REVIEWS]
    return {"$comment": COMMENT, "cases": cases}


def render() -> str:
    return json.dumps(build(), ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str]) -> int:
    text = render()
    if "--check" in argv:
        held = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if held != text:
            print("cases.json differs from what make_cases.py would write. Run make_cases.py.")
            return 1
        print("cases.json is what make_cases.py would write.")
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.name}: {len(build()['cases'])} cases")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
