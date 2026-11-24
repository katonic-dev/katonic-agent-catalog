"""Franchise, version 1.4: the three franchisees with their restaurants, and questions franchisees have asked.

The questions are there for trying an agent that answers from the Franchise Operations Manual, version 3.0, and the
Brand Standards, version 2.0 (both in retail/policy-library). The service does not hold the wording of either
document. Where the answer to each question is found is kept in its own record set (franchise_answers) and no
operation serves it.
"""

from __future__ import annotations

from datetime import date, timedelta

from .seed_stores import build_sites

MANUAL = "Franchise Operations Manual, version 3.0"
STANDARDS = "Brand Standards, version 2.0"
FRANCHISE_TEAM = "franchise.team@rowanmere.example"
AGREEMENT_NOTE = ("The franchise agreement is not held in this system. A question about the agreement goes to the franchise "
                  f"team at {FRANCHISE_TEAM}.")

# id, company as the stores system names it, franchisee since (year)
_FRANCHISEES = [
    ("FR-01", "Brindle-Crake Foods Ltd", 2019),
    ("FR-02", "Wickersham-Ode Pizza Partners Ltd", 2021),
    ("FR-03", "Ostrand-Pell Quick Meals Ltd", 2023),
]

# franchisee, days before the retailer date, the question, the kind of answer, where the answer is found, the answer in short
_QUESTIONS = [
    ("FR-01", 20, "By when do I have to send the weekly sales report?", "answered", ["1.2"],
     "By 12:00 on the Tuesday after the week ends. The week runs Monday to Sunday."),
    ("FR-03", 19, "What do I pay in royalty, and when is the invoice due?", "answered", ["1.1", "1.3"],
     "6 percent of net sales, and 3 percent to the national marketing fund. The invoice is sent on the 5th and is payable by the 20th."),
    ("FR-02", 18, "How many audits will my restaurant get in a year, and will I be told before one?", "answered", ["2.1"],
     "Two a year. An audit is not announced."),
    ("FR-01", 16, "We scored 19 on the last audit. What happens now?", "answered", ["2.2", "2.3"],
     "19 is below the pass score of 20 out of 24. An action plan goes to the area manager within 14 days, and the "
     "restaurant is audited again within 60 days."),
    ("FR-03", 15, "I think the auditor scored one item wrongly. Can I ask for the score to be looked at again?", "answered", ["2.4"],
     "Yes: in writing to the Head of Franchise Operations, within 7 days of receiving the audit report."),
    ("FR-02", 13, "Can I put a local dish on my menu?", "answered", ["3.2", "3.4"],
     "Up to three local items, each with the menu team's written approval asked for at least 30 days ahead. It is not "
     "sold until it is in the Allergen Matrix."),
    ("FR-01", 12, "Can I charge more than the recommended price for a pizza?", "answered", ["3.3"],
     "Yes, up to 10 percent above the recommended price list. During a national promotion the promoted items are sold "
     "at the promotion price."),
    ("FR-03", 10, "Can I print my own flyers for the neighbourhood?", "answered", ["4.2"],
     "Local marketing uses the artwork on the brand portal. Own artwork needs the marketing team's approval first, which "
     "takes up to 10 working days."),
    ("FR-02", 9, "How much do I have to spend on local marketing?", "answered", ["4.1"],
     "At least 1 percent of net sales each year, with the receipts kept for the yearly review."),
    ("FR-01", 7, "My restaurant opened in 2019. When is it due a refit, and who pays for it?", "answered", ["5.2", "5.3"],
     "Every 7 years from opening or the last refit, so 2026 for a restaurant opened in 2019. The franchisee pays, and the "
     "property team approves the plans before work starts."),
    ("FR-03", 6, "My produce supplier did not deliver this morning. Can I buy from the shop down the road?", "answered", ["6.3"],
     "Milk, fresh produce and ice may be bought from a local shop for up to 3 days. The supply team is told within 24 "
     "hours of the first purchase."),
    ("FR-02", 5, "A national promotion ended on Sunday. How long do I have to take the posters down?", "answered", ["BS-5.2"],
     "Within 24 hours of the end of the promotion. That is brand standard 5.2. Section 2.5 of the manual says the Brand "
     "Standards apply in full."),
    ("FR-01", 4, "Can I close early on a public holiday?", "silent", [],
     "The manual and the brand standards do not say what hours a franchised restaurant trades on a public holiday. "
     "The question goes to the franchise team (section 7.4)."),
    ("FR-03", 3, "Can I sign up with a delivery app of my own choice?", "silent", [],
     "The manual and the brand standards say nothing about delivery apps. The question goes to the franchise team (section 7.4)."),
    ("FR-02", 3, "When the uniform design changes, who pays for the new uniforms?", "silent", [],
     "The manual and the brand standards do not say who pays for a new uniform. Brand standard 2.2 says only that the "
     "full uniform is worn. The question goes to the franchise team (section 7.4)."),
    ("FR-01", 2, "My agreement runs out in 2029. How do I renew it, and will the terms change?", "franchise_agreement", ["7.1"],
     "Renewal is a matter of the franchise agreement itself. The manual gives no answer. The question goes to the franchise team."),
    ("FR-03", 1, "Can I sell my restaurant to another operator, and could a second Rowanmere Kitchen open inside my territory?",
     "franchise_agreement", ["7.1"],
     "The sale or transfer of a franchise and the territory are matters of the franchise agreement itself. The manual "
     "gives no answer. The question goes to the franchise team."),
]


def build_franchise(today: date) -> dict:
    sites = build_sites()
    franchisees = {}
    for fid, company, since in _FRANCHISEES:
        own = [s for s in sites.values() if s["franchisee"] == company]
        if not own:
            raise AssertionError(f"{company} runs no restaurant in the stores seed")
        franchisees[fid] = {
            "franchisee_id": fid, "company": company, "franchisee_since": since,
            "restaurants": [{"site_id": s["site_id"], "name": s["name"], "town": s["town"], "street": s["street"],
                             "area": s["area"], "area_manager": s["area_manager"]} for s in sorted(own, key=lambda s: s["site_id"])],
            "operations_manual": MANUAL, "brand_standards": STANDARDS, "agreement_note": AGREEMENT_NOTE,
            "franchise_team_email": FRANCHISE_TEAM}
    month = f"{today.year % 100:02d}{today.month:02d}"
    questions, answers = {}, {}
    for n, (fid, days, text, kind, sections, short) in enumerate(_QUESTIONS, start=1):
        qid = f"FQ-{month}-{n:02d}"
        questions[qid] = {"question_id": qid, "franchisee_id": fid, "company": franchisees[fid]["company"],
                          "asked_on": (today - timedelta(days=days)).isoformat(), "question": text}
        answers[qid] = {"question_id": qid, "kind": kind, "sections": list(sections), "answer_in_short": short}
    return {"franchisees": franchisees, "franchise_questions": questions, "franchise_answers": answers}
