"""Customer care, version 1.2: customer tickets, help articles, past cases, complaints and public reviews.

Which article answers a ticket, how a complaint is classified and which reviews go to a person are kept in
their own record sets (ticket_answers, complaint_answers, review_answers) and no operation serves them.
"""

from __future__ import annotations

from datetime import date, timedelta

from .seed_base import d_ago
from .seed_orders import _NAMES

NOTICE = "Rowanmere Group is invented, and so is this document. It is not the document of any real retailer."
CARE_ADDRESS = "care@rowanmere-market.example"

# ---------------------------------------------------------------- help articles

HELP_ARTICLES = [
    ("HA-01", "Delivery times and charges", "delivery",
     "Standard delivery takes 2 to 4 working days and costs USD 4.95. It is free when the goods in the order come to "
     "USD 60.00 or more. Next-day delivery costs USD 7.95 and is offered on orders placed before 14:00."),
    ("HA-02", "Click and collect", "delivery",
     "An order placed before 15:00 is ready at the store within 4 hours. We send a message when it is ready. The store holds "
     "it for 5 days. Bring the order number when you collect. Click and collect is free."),
    ("HA-03", "Changing or cancelling an order", "orders",
     "You can change or cancel an order in your account for 60 minutes after you place it, or until its status becomes "
     "packed, whichever comes first. After that the order cannot be changed, and the item can be returned once it arrives."),
    ("HA-04", "How to return an item", "returns",
     "Ask for a return in your account, under the order, within 30 days of delivery. We check the request against the "
     "Returns Policy and send a prepaid label when it is approved. An item can also be handed in at any Rowanmere Market "
     "store with the order number."),
    ("HA-05", "When a refund arrives", "returns",
     "A refund goes to the payment method used for the order, within 5 working days of the day the return is approved. "
     "Your bank may take a further 2 days to show it."),
    ("HA-06", "Ways to pay", "payment",
     "The online shop takes debit cards, credit cards and Rowanmere gift cards. It does not take cash or payment on "
     "collection: a click and collect order is paid for when it is placed."),
    ("HA-07", "Gift cards", "payment",
     "A Rowanmere gift card is valid for 24 months from the day it was bought. It can be used together with a payment card "
     "in one order. The balance is shown in your account under Gift cards. A gift card cannot be exchanged for cash."),
    ("HA-08", "Rowanmere Rewards points", "account",
     "You earn 1 point for each dollar spent. Points show in your account within 48 hours of delivery or collection. Points "
     "lapse when 12 months pass without a purchase."),
    ("HA-09", "A missing or damaged item in a delivery", "delivery",
     "Tell us within 7 days of delivery. Send the order number, the name of the item and, for a damaged item, a photograph. "
     "A member of the care team then looks at the order and writes back."),
    ("HA-10", "Substitutions in a grocery order", "orders",
     "When an item is out of stock we may send the nearest one in its place, at no higher price. You can hand a substitute "
     "back to the driver and it is refunded within 5 working days. You can switch substitutions off in your account under "
     "Shopping preferences."),
    ("HA-11", "Your account: password and email address", "account",
     "To reset a password, choose Forgotten password on the sign-in page and follow the link we send. To change the email "
     "address on an account, sign in, open Account details and choose Change email. We send a confirmation to both the old "
     "and the new address."),
    ("HA-12", "Delivery to a neighbour or a safe place", "delivery",
     "When nobody is in, the carrier may leave a parcel with a neighbour and puts a card through your door saying where it "
     "is. You can switch this off in your account under Delivery preferences. Chilled and frozen food is never left with a "
     "neighbour."),
]


def help_articles() -> list[dict]:
    return [{"article_id": a, "title": t, "category": c, "body": b} for a, t, c, b in HELP_ARTICLES]


def help_articles_markdown() -> str:
    out = ["# Help Articles (invented)", "",
           "Rowanmere Group is invented, and so is this document. It is not the document of any real retailer.", "",
           "The help articles of Rowanmere Market's online shop, as the customer care team uses them. Twelve articles, "
           "HA-01 to HA-12.", ""]
    for a, t, _, b in HELP_ARTICLES:
        out += [f"## {a}. {t}", "", b, ""]
    return "\n".join(out)


# ---------------------------------------------------------------- the complaints procedure, version 2.1

CLASSES = [
    ("A", "safety_or_legal", 2, "The complaint describes an injury, an illness, an allergic reaction or a hazard, or the "
                                "customer says they will take legal action."),
    ("B", "repeat_contact", 5, "The contact history shows two or more earlier contacts about the same matter."),
    ("C", "service_failure", 10, "We did not do what we said we would: a late, missing, damaged or wrong delivery, or the way "
                                 "a colleague or a driver behaved. Fewer than two earlier contacts."),
    ("D", "policy_disagreement", 14, "We did what our policy says and the customer disagrees with the policy or the charge."),
]
DAYS_FOR = {name: days for _, name, days, _ in CLASSES}
_PROCEDURE = [
    ("1", "What a complaint is", [
        ("1.1", "A complaint is any message in which a customer says they are unhappy and expects an answer. Every complaint "
                "is logged with its class and the date its response is due."),
    ]),
    ("2", "The four classes", [
        (f"2.{n}", f"Class {letter}, written {name}. {text} Response due within {days} days of the day the complaint was received.")
        for n, (letter, name, days, text) in enumerate(CLASSES, start=1)
    ] + [
        ("2.5", "When more than one class fits, the complaint takes the first that fits in the order A, B, C, D."),
        ("2.6", "Days are calendar days. The day the complaint was received is day 0."),
    ]),
    ("3", "What a response holds", [
        ("3.1", "It thanks the customer and says in one sentence what the complaint is about."),
        ("3.2", "It says what our records show, with the dates, and says so when the records do not explain what happened."),
        ("3.3", "It says what happens next and by when."),
        ("3.4", "It admits no fault and offers no money, credit or goodwill. The Customer Relations Lead decides those."),
    ]),
    ("4", "Who decides", [
        ("4.1", "A class A complaint goes to the Customer Relations Lead on the day it is received. No finding and no "
                "response is sent before the Lead has read it."),
        ("4.2", "The Customer Relations Lead approves every response before it is sent, and decides any goodwill payment."),
    ]),
]
PROCEDURE_NOT_DECIDED = ("This procedure does not decide whether the company was at fault, and it does not decide what a "
                         "customer is paid. It sets the class, the date and who decides.")


def complaints_procedure_markdown() -> str:
    out = ["# Complaints Procedure (invented)", "",
           "Rowanmere Group is invented, and so is this document. It is not the procedure of any real retailer.", "",
           "Version: 2.1. Owner: Customer Relations Lead. It covers complaints about Rowanmere Market's stores and online shop.", ""]
    for number, title, clauses in _PROCEDURE:
        out += [f"## {number}. {title}", ""]
        out += [f"{c} {text}" for c, text in clauses]
        out.append("")
    out += ["## 5. What this procedure does not decide", "", PROCEDURE_NOT_DECIDED, ""]
    return "\n".join(out)


COMPLAINTS_PROCEDURE = {
    "document": "Complaints Procedure", "version": "2.1", "owner": "Customer Relations Lead", "notice": NOTICE,
    "classes": [{"class": letter, "classification": name, "response_due_days": days, "applies_when": text, "section": f"2.{n}"}
                for n, (letter, name, days, text) in enumerate(CLASSES, start=1)],
    "order_when_more_than_one_fits": ["safety_or_legal", "repeat_contact", "service_failure", "policy_disagreement"],
    "sections": [{"number": n, "title": t, "clauses": [{"clause": c, "text": x} for c, x in clauses]} for n, t, clauses in _PROCEDURE],
    "what_the_procedure_does_not_decide": PROCEDURE_NOT_DECIDED,
    "text": complaints_procedure_markdown(),
}

# ---------------------------------------------------------------- tickets

# number, customer (index into the names), received days ago, channel, order, subject, message, the article that answers it
_TICKETS = [
    (1, 6, "web form", "", "Delivery cost", "How much is delivery, and is there an order size where it becomes free?", "HA-01"),
    (11, 0, "chat", "RM-58163", "Change my order", "I placed order RM-58163 twenty minutes ago and picked the wrong hose reel. "
                                                  "Can I still change it?", "HA-03"),
    (10, 5, "email", "RM-58108", "Sending a jumper back", "How do I send back the jumper from order RM-58108? It was "
                                                         "delivered last month.", "HA-04"),
    (22, 4, "email", "", "Refund timing", "My return was approved last Friday. When will the money reach my card?", "HA-05"),
    (9, 4, "web form", "", "Gift card and card together", "Can I pay part of an order with a gift card and the rest with my "
                                                          "debit card?", "HA-07"),
    (4, 3, "email", "", "Gift card expiry", "I was given a Rowanmere gift card last year. Does it run out?", "HA-07"),
    (5, 3, "chat", "RM-58143", "Points missing", "The points from order RM-58143 are not in my account yet. When do they show?", "HA-08"),
    (15, 5, "email", "RM-58160", "Item missing from delivery", "The frozen fish was missing from order RM-58160. What do you "
                                                               "need from me?", "HA-09"),
    (17, 3, "web form", "RM-58168", "Substitute in my grocery box", "You sent a different milk in order RM-58168. Am I "
                                                                    "allowed to refuse a substitute next time?", "HA-10"),
    (2, 2, "chat", "", "Forgotten password", "I cannot sign in. I have forgotten my password.", "HA-11"),
    (19, 2, "email", "RM-58166", "Left with a neighbour", "A card says order RM-58166 was left at number 14. Are your drivers "
                                                          "allowed to do that?", "HA-12"),
    (14, 1, "chat", "RM-58165", "Collecting my order", "Order RM-58165 is ready at the store. How long will you keep it for me?", "HA-02"),
    (3, 2, "web form", "", "Paying on collection", "Which cards do you take, and can I pay when I collect?", "HA-06"),
    (12, 2, "email", "", "Price match", "Another supermarket sells the same coffee beans for less. Do you match their price?", ""),
    (16, 1, "web form", "", "Account for my coffee shop", "I run a coffee shop. Can I open a business account and pay by monthly invoice?", ""),
    (18, 1, "email", "RM-58152", "Nut allergy", "My daughter has a nut allergy. Is the granola in the weekly grocery box of "
                                                "order RM-58152 safe for her?", ""),
    (7, 1, "chat", "", "Next-day delivery", "What time do I have to order by to get next-day delivery, and what does it cost?", "HA-01"),
    (8, 1, "web form", "", "Do points expire", "Do my Rewards points ever expire?", "HA-08"),
    (13, 0, "email", "", "Change my email address", "I have a new email address. How do I change it on my account?", "HA-11"),
    (18, 0, "email", "RM-58170", "Kettle lid cracked", "The kettle in order RM-58170 arrived with a cracked lid. What should I do?", "HA-09"),
]


def person(n: int) -> dict:
    name = _NAMES[n - 1]
    return {"customer_id": f"C-{4000 + n}", "customer_name": name, "customer_email": name.lower().replace(" ", ".") + "@mail.invalid"}


def make_ticket(today: date, ticket_id: str, cust: int, ago: int, channel: str, order: str, subject: str, message: str) -> dict:
    return {"ticket_id": ticket_id, "received_on": d_ago(today, ago), "channel": channel, **person(cust), "order_number": order,
            "subject": subject, "message": message, "status": "open", "reply_drafts": [], "reply_sent": None}


# ---------------------------------------------------------------- past cases

_CASES = [
    (40, "A customer asked how long a click and collect order is kept.", "Answered from the article: the store holds it for 5 days.", "HA-02"),
    (37, "A customer wanted to cancel an order two hours after placing it. Its status was packed.",
     "Answered from the article: it could not be changed, and the item could be returned once it arrived.", "HA-03"),
    (35, "A customer asked for a return of an opened hand mixer because it was not wanted.",
     "The team leader refused it under condition 2.2 of the Returns Policy.", "HA-04"),
    (33, "A customer asked to return a pack of chilled soup, unopened, bought by mistake.",
     "The team leader refused it under condition 3.1 of the Returns Policy.", "HA-04"),
    (31, "A customer reported a chipped serving bowl 12 days after delivery, with a photograph.",
     "It was passed to the Customer Care Team Leader under condition 5.3 of the Returns Policy, who decided it.", "HA-09"),
    (28, "A customer asked why a refund had not arrived 3 working days after the return was approved.",
     "Answered from the article: within 5 working days of the approval.", "HA-05"),
    (26, "A customer asked whether a gift card could be turned into cash.", "Answered from the article: it cannot.", "HA-07"),
    (22, "A customer reported a carton of eggs missing from a grocery delivery, 2 days after delivery.",
     "The customer was asked for the order number and the item, and a member of the care team looked at the order.", "HA-09"),
    (19, "A customer asked to return a toaster that stopped working after two weeks.",
     "The team leader approved it under condition 5.2 of the Returns Policy.", "HA-04"),
    (16, "A customer did not want parcels left with a neighbour again.",
     "Answered from the article: it can be switched off in the account under Delivery preferences.", "HA-12"),
]

# ---------------------------------------------------------------- complaints

# number, customer, received days ago, channel, order, subject, the customer's words, earlier contacts (days ago, channel,
# summary), then the right class
_COMPLAINTS = [
    ("01", 24, 2, "email", "RM-58162", "Order is late",
     "My dinner set was promised for last week and it has not come. Nobody has told me anything.", [], "service_failure"),
    ("02", 14, 3, "email", "RM-58118", "Still no refund",
     "This is the third time I am writing about the refund for the towels. You approved it and the money has not arrived.",
     [(9, "phone", "Asked when the refund for the towel set would arrive. Told within 5 working days of the approval."),
      (6, "email", "Wrote that the refund had still not arrived. Told it had been passed to the payments team.")], "repeat_contact"),
    ("03", 18, 1, "phone", "RM-58152", "Glass in a jar of pasta sauce",
     "There was a piece of glass in one of the jars of pasta sauce. I cut my finger on it while serving.", [], "safety_or_legal"),
    ("04", 12, 6, "web form", "RM-58158", "Charged for delivery",
     "I was charged 4.95 for delivery on an order of nearly sixty dollars. That is petty and I want it back.", [],
     "policy_disagreement"),
    ("05", 19, 1, "email", "RM-58166", "Parcel left with a neighbour",
     "I was at home all day and the driver left my parcel at number 14 without knocking. I had to go and fetch it.",
     [(2, "email", "Asked whether drivers may leave a parcel with a neighbour. No reply has been sent.")], "service_failure"),
    ("06", 13, 2, "email", "RM-58156", "Charged twice",
     "My bank statement shows two payments for the towels. If this is not put right this week I will take legal action.", [],
     "safety_or_legal"),
    ("07", 15, 1, "phone", "RM-58160", "Fish missing from my order",
     "I told you last week that the frozen fish was missing and I have heard nothing since.",
     [(5, "email", "Wrote that the frozen fish was missing from the delivery. Asked for the order number and the item.")],
     "service_failure"),
    ("08", 17, 7, "email", "RM-58139", "Wrong item, third time of asking",
     "I ordered a toaster and received a kettle. I have phoned twice. I want to speak to a manager.",
     [(9, "phone", "Said a kettle had arrived in place of the toaster. Told a collection would be arranged."),
      (8, "phone", "Asked when the kettle would be collected and the toaster sent. Told it would be chased.")], "repeat_contact"),
]


def make_complaint(today: date, complaint_id: str, cust: int, ago: int, channel: str, order: str, subject: str, words: str,
                   earlier: list) -> dict:
    return {"complaint_id": complaint_id, "received_on": d_ago(today, ago), "channel": channel, **person(cust),
            "order_number": order, "subject": subject, "message": words,
            "contact_history": [{"date": d_ago(today, a), "channel": ch, "summary": s, "about_the_same_matter": True}
                                for a, ch, s in earlier],
            "status": "open", "classifications": [], "response_drafts": [], "response_sent": None}


def due_date(received_on: str, classification: str) -> str:
    return (date.fromisoformat(received_on) + timedelta(days=DAYS_FOR[classification])).isoformat()


# ---------------------------------------------------------------- public reviews

REVIEW_SITES = ["Meridia Shoppers' Forum", "Ilvane Local Pages"]
# number, days ago, site (0 or 1), about, rating, reviewer's display name, text, whether it must go to a person
_REVIEWS = [
    ("01", 9, 0, "S-101", 5, "harbourwalker22", "The team at the Market Street store helped me find everything for a big "
                                               "family meal. Friendly and quick.", False),
    ("02", 8, 1, "online shop", 2, "tidewatcher", "My order came two days late and nobody sent an update. I had to chase it myself.", False),
    ("03", 7, 0, "S-104", 1, "marlowmum", "I found a piece of metal wire in a loaf from the in-store bakery. My child nearly "
                                          "swallowed it.", True),
    ("04", 6, 0, "S-107", 4, "kilnroadcook", "Good range and fair prices. The queues at the weekend are long.", False),
    ("05", 6, 1, "online shop", 3, "quietgardener", "The delivery was on time but two of the substitutes were nothing like what I ordered.", False),
    ("06", 5, 1, "S-102", 1, "docksidedan", "I slipped on a wet floor by the chillers with no sign out and hurt my back. My "
                                            "solicitor will be in touch.", True),
    ("07", 4, 0, "S-105", 5, "reachroadrunner", "Click and collect was ready in under two hours and the colleague brought it "
                                                "to the car.", False),
    ("08", 4, 1, "S-108", 2, "millroadlocal", "Half the fresh shelves were empty on Sunday evening. Not for the first time.", False),
    ("09", 3, 0, "online shop", 4, "bookishbee", "Sent a jacket back and the refund was in my account within the week. Easy.", False),
    ("10", 2, 1, "S-103", 1, "ferryroadfan", "The colleague on the till was short with me and did not say a word while serving.", False),
    ("11", 1, 0, "online shop", 3, "appgrumbler", "The app keeps signing me out halfway through a shop. Fine when it works.", False),
    ("12", 1, 1, "S-106", 5, "causewaybaker", "The bakery team at Causeway Park are a delight. Best bread in town.", False),
]


def make_review(today: date, review_id: str, ago: int, site: int, about: str, rating: int, name: str, text: str) -> dict:
    return {"review_id": review_id, "posted_on": d_ago(today, ago), "review_site": REVIEW_SITES[site], "about": about,
            "rating": rating, "reviewer_display_name": name, "text": text, "status": "unanswered", "reply_drafts": [],
            "reply_published": None}


def build_care_desk(today: date) -> dict:
    month = f"{today.year % 100:02d}{today.month:02d}"
    tickets, ticket_answers = {}, {}
    for n, (cust, ago, channel, order, subject, message, article) in enumerate(_TICKETS, start=1):
        tid = f"CT-{month}-{n:03d}"
        tickets[tid] = make_ticket(today, tid, cust, ago, channel, order, subject, message)
        ticket_answers[tid] = article
    cases = {}
    for n, (ago, question, done, article) in enumerate(_CASES, start=1):
        cid = f"PC-{month}-{n:02d}"
        cases[cid] = {"case_id": cid, "closed_on": d_ago(today, ago), "question": question, "what_was_done": done,
                      "article_id": article}
    complaints, complaint_answers = {}, {}
    for n, cust, ago, channel, order, subject, words, earlier, right in _COMPLAINTS:
        cid = f"CM-{month}-{n}"
        complaints[cid] = make_complaint(today, cid, cust, ago, channel, order, subject, words, earlier)
        complaint_answers[cid] = {"classification": right, "response_due": due_date(complaints[cid]["received_on"], right)}
    reviews, review_answers = {}, {}
    for n, ago, site, about, rating, name, text, to_a_person in _REVIEWS:
        rid = f"PR-{month}-{n}"
        reviews[rid] = make_review(today, rid, ago, site, about, rating, name, text)
        review_answers[rid] = "mark_for_a_person" if to_a_person else "reply"
    return {"tickets": tickets, "ticket_answers": ticket_answers, "past_cases": cases, "complaints": complaints,
            "complaint_answers": complaint_answers, "public_reviews": reviews, "review_answers": review_answers}


# ---------------------------------------------------------------- arrivals

# customer-ticket: three that an article answers and one that none does
_SIM_TICKETS = [
    (1, "web form", "Delivery charge", "Is delivery free if I spend seventy dollars?", "HA-01"),
    (2, "email", "Where is my refund", "My return was approved on Monday. How long does the refund take?", "HA-05"),
    (3, "chat", "Locked out", "I have forgotten my password and cannot get into my account.", "HA-11"),
    (4, "email", "Catering for an event", "Can you cater a wedding for 120 people and deliver on a Sunday?", ""),
]


def sim_ticket(data: dict, today: date, kind: int, ticket_id: str) -> tuple[str, str]:
    cust, channel, subject, message, article = _SIM_TICKETS[kind]
    data["tickets"][ticket_id] = make_ticket(today, ticket_id, cust, 0, channel, "", subject, message)
    data["ticket_answers"][ticket_id] = article
    return ticket_id, (f"A new customer ticket {ticket_id} has arrived in the care system, by {channel}, with the subject "
                       f"\"{subject}\". It is open and has no reply. Read it with get_customer_ticket and look for the article "
                       "that answers it with search_help_articles.")


# complaint: one of each class, in turn
_SIM_COMPLAINTS = [
    (1, "email", "RM-58172", "Box arrived crushed", "The box for my order was crushed and wet when it arrived.", [], "service_failure"),
    (5, "email", "RM-58178", "Third message about my parcel", "I have written twice about my parcel and had no answer. Where is it?",
     [(2, "email", "Asked where the parcel was. No reply was sent."), (1, "chat", "Asked again where the parcel was. Told it would be chased.")],
     "repeat_contact"),
    (6, "phone", "RM-58180", "Unwell after eating", "Two of us were sick the night after eating food from the grocery box in this order.", [],
     "safety_or_legal"),
    (8, "web form", "RM-58184", "Charged for delivery", "Why am I paying 4.95 for delivery on a blender? Other shops deliver free.", [],
     "policy_disagreement"),
]


def sim_complaint(data: dict, today: date, kind: int, complaint_id: str) -> tuple[str, str]:
    cust, channel, order, subject, words, earlier, right = _SIM_COMPLAINTS[kind]
    c = make_complaint(today, complaint_id, cust, 0, channel, order, subject, words, earlier)
    data["complaints"][complaint_id] = c
    data["complaint_answers"][complaint_id] = {"classification": right, "response_due": due_date(c["received_on"], right)}
    return complaint_id, (f"A new complaint {complaint_id} has arrived in the care system, by {channel}, about order {order}. It "
                          f"was received on {today.isoformat()}, it is open and it has {len(earlier)} earlier "
                          f"contact{'s' if len(earlier) != 1 else ''} in its history. Read it with get_complaint and the classes "
                          "with get_complaints_procedure.")


# public-review: praise, criticism, mixed, and one that describes a safety matter
_SIM_REVIEWS = [
    (0, "S-104", 5, "highstreetregular", "Spotless store and the colleague at the deli counter could not have been kinder.", False),
    (1, "online shop", 2, "latebasket", "Third order in a row with an item missing. Getting tired of it.", False),
    (0, "S-107", 3, "brewerylanedad", "Great fresh fruit, but the car park is chaos on a Saturday.", False),
    (1, "S-101", 1, "marketstreetmia", "My son had an allergic reaction to a pastry labelled nut free. We spent the evening at the clinic.", True),
]


def sim_review(data: dict, today: date, kind: int, review_id: str) -> tuple[str, str]:
    site, about, rating, name, text, to_a_person = _SIM_REVIEWS[kind]
    data["public_reviews"][review_id] = make_review(today, review_id, 0, site, about, rating, name, text)
    data["review_answers"][review_id] = "mark_for_a_person" if to_a_person else "reply"
    return review_id, (f"A new public review {review_id} has been posted on {REVIEW_SITES[site]} about {about}, with {rating} "
                       f"star{'s' if rating != 1 else ''}. It is held in the care system and has no reply. Read it with "
                       "get_public_review.")
