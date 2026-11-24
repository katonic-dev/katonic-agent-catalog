"""Seed data, part 7: customer complaints, the complaints procedure, and the records in other systems that they point at."""

from __future__ import annotations

from datetime import date, timedelta

from .seed_base import d_ago
from .seed_lend import installment
from .seed_onb import identity_text


# ------------------------------------------------------------------ working days (Monday to Friday, no holidays)

def add_working_days(start: date, n: int) -> date:
    d, step = start, 1 if n >= 0 else -1
    left = abs(n)
    while left:
        d += timedelta(days=step)
        if d.weekday() < 5:
            left -= 1
    return d


def last_working_day(d: date) -> date:
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


def working_days_between(a: date, b: date) -> int:
    """Working days after a, up to and including b. Negative when b is before a."""
    if b < a:
        return -working_days_between(b, a)
    n, d = 0, a
    while d < b:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


PROCEDURE = {
    "procedure_id": "MTB-PROC-CMP-1", "title": "Customer complaints procedure (invented)",
    "what_is_a_complaint": "Any expression of dissatisfaction about the bank's service, a charge, a payment, a card, a loan or a member of staff, "
                           "by any channel. The customer does not need to use the word complaint.",
    "categories": [
        {"category": "fees_and_charges", "covers": "A fee or charge the customer disputes."},
        {"category": "payments", "covers": "A payment that was late, short, returned or not received."},
        {"category": "cards", "covers": "A card that was blocked, declined, lost, or a card payment."},
        {"category": "lending_decision", "covers": "A declined or restricted loan application. See the rule on credit decisions below."},
        {"category": "service_and_staff", "covers": "Delay, wrong information, manner of staff, promises not kept."},
        {"category": "accounts", "covers": "Opening, closing, statements, interest and account terms."},
        {"category": "other", "covers": "Anything that fits none of the above."}],
    "severity": {
        "rule": "Severity is how serious the matter is for the customer. Give the highest level whose description fits.",
        "low": "A small sum or an inconvenience, and the customer can still use the account and the card.",
        "medium": "The customer was without money or a service for a time, or a time limit of this procedure was missed.",
        "high": "The customer cannot reach their money or their card, or the customer may be vulnerable."},
    "time_limits": {
        "acknowledge": "Within 2 working days of receipt. The acknowledgement says who deals with the complaint and when to expect an answer.",
        "final_response": "Within 15 working days of receipt.",
        "working_days": "Monday to Friday. The day of receipt is not counted.",
        "late_acknowledgement": "If the acknowledgement was late or never sent, the response must say so and apologise for it. It is never left out."},
    "what_a_response_must_contain": [
        "A plain statement of what the customer complained about, in the bank's words and in the order the customer raised it.",
        "What the bank found, with the dates and amounts that prove it, and whether the complaint is upheld, partly upheld or not upheld.",
        "What the bank will do, and by when, for example a refund, a correction or a call.",
        "Where the bank was at fault, a clear apology. Where it was not, a clear explanation without blame.",
        "The customer's right to escalate (see below), written in full.",
        "The name and direct line of the person who answers further questions."],
    "redress": {
        "when_it_applies": "When the bank made an error, acted late, or did not follow its own process and the customer lost money or time.",
        "what_it_covers": "A refund of the amount wrongly charged, any charge that followed from the error, and where the customer was put to real trouble a "
                          "goodwill payment of up to USD 50.",
        "when_it_does_not_apply": "When the bank acted correctly under the account terms, or the delay was caused by another bank or a payment system and the "
                                  "bank acted within its own times. Explain with dates. Do not offer redress to end the complaint."},
    "credit_decisions": "A declined loan is not a service failure when the bank applied its credit policy to the figures the customer gave. The response "
                        "explains the main reasons in plain words and tells the customer they may ask for a review: write to the Credit Review Desk within "
                        "30 days, with any new information, and a different credit officer looks again. Do not promise a different result.",
    "vulnerable_customers": "A customer who may be vulnerable (a recent bereavement, serious illness, a job loss, age, difficulty with language or "
                            "money) is handled with priority, by one named person, in a plain and kind tone, with no standard letters, and "
                            "without waiting for the full 15 working days where the customer is in difficulty.",
    "escalation": "After the final response, or after 15 working days without one, the customer may take the complaint to the Meridia Financial "
                  "Ombudsman Service (invented). The customer must do so within 6 months of the final response. It costs the customer nothing.",
    "logging": "Every complaint has a log entry that gives the category, the dates, the outcome, any redress and the name of the person who "
               "approved the response."}


# ------------------------------------------------------------------ cross-system records the complaints point at

def _add_loan_application(applications, app_docs, customers, today):
    cust = customers["CUS-1016"]
    inst = installment(14000, 9.5, 36)
    aid = "LAP-8010"
    applications[aid] = {
        "application_id": aid, "status": "declined", "customer_id": "CUS-1016", "applicant": cust["name"], "product": "personal_loan",
        "amount": 14000.0, "currency": "USD", "term_months": 36, "indicative_apr_pct": 9.5, "indicative_monthly_installment": inst,
        "purpose": "Furniture and a used car", "received": d_ago(today, 22),
        "form_fields": {"employer": "Quillon Software Ltd", "gross_monthly_income": 2400.0, "existing_monthly_debt_payments": 700.0,
                        "employment_start": "2025-09-01"},
        "decision": {"decision": "declined", "decided_on": d_ago(today, 14), "policy_id": "MTB-POL-030",
                     "reason": "Debt to income is 0.48, above the limit of 0.40: (700.00 + %.2f) / 2,400.00." % inst},
        "missing_items_drafts": [], "credit_memo_drafts": []}
    app_docs[aid] = {}
    texts = [("identity_document", "National identity card (extract)",
              identity_text(cust["name"], cust["date_of_birth"], "Meridia", cust["id_number"], d_ago(today, 800), d_ago(today, -2800),
                            "Port Ilvane", d_ago(today, 22))),
             ("payslips_3_months", "Payslips, last three months", "Gross monthly pay USD 2,400.00 in each of the last three months. Employer: Quillon Software Ltd."),
             ("bank_statements_3_months", "Bank statements, last three months", "Salary credited on the 28th each month. Regular monthly debits of about USD 700.00 for credit commitments."),
             ("employment_letter", "Employment letter", "Quillon Software Ltd confirms the applicant is employed full time since 2025-09-01 on a permanent contract.")]
    for i, (t, title, text) in enumerate(texts, start=1):
        did = f"DOC-8010{i:02d}"
        app_docs[aid][did] = {"document_id": did, "application_id": aid, "doc_type": t, "title": title, "received": d_ago(today, 22),
                              "format": "extracted text", "text": text}


def build_complaints(today: date, customers: dict, accounts: dict, tb, cards: dict, applications: dict, app_docs: dict) -> dict:
    """Adds the fee entries, the declined loan application and the blocked card the complaints point at, and returns the complaints."""
    # fees charged twice on ACC-1009-01 (CMP-1001): a monthly fee of 12.00, taken twice last time
    acc = accounts["ACC-1009-01"]
    f1 = tb.add(acc, 68, 12.00, "debit", "fee", "Meridian Trust Bank", "Monthly account fee")
    f2 = tb.add(acc, 38, 12.00, "debit", "fee", "Meridian Trust Bank", "Monthly account fee")
    f3 = tb.add(acc, 8, 12.00, "debit", "fee", "Meridian Trust Bank", "Monthly account fee")
    f4 = tb.add(acc, 8, 12.00, "debit", "fee", "Meridian Trust Bank", "Monthly account fee")
    _add_loan_application(applications, app_docs, customers, today)
    # CMP-1004: a card blocked by mistake by the deceased accounts process
    cards["CRD-2004"].update(status="blocked", block_reason="other", blocked_by="Deceased accounts desk", blocked_at=f"{d_ago(today, 6)}T10:12:00+00:00",
                             block_note="Blocked by the deceased accounts process after a death was recorded on the household. The process is for "
                                        "cards held by the person who died. This card is held by CUS-1001, who reported the death.")

    base = last_working_day(today)
    rec_1, rec_2, rec_3, rec_4, rec_5 = (add_working_days(base, -n) for n in (4, 3, 5, 2, 13))
    acked = lambda r, extra=1: add_working_days(r, extra).isoformat()

    def cmp_(cid, customer, channel, received, ack, subject, words, linked):
        link = {"account_ids": [], "transaction_ids": [], "card_ids": [], "payment_ids": [], "investigation_ids": [],
                "loan_ids": [], "loan_application_ids": []}
        link.update(linked)
        return {"complaint_id": cid, "customer_id": customer, "status": "open", "channel": channel, "received": received.isoformat(),
                "acknowledged_on": ack, "subject": subject, "customer_words": words, "linked": link, "classifications": [],
                "response_drafts": [], "sent": None}

    out = {}
    out["CMP-1001"] = cmp_("CMP-1001", "CUS-1009", "email", rec_1, acked(rec_1), "Account fee taken twice", (
        "To the complaints team,\n\nI am writing because I was charged the monthly account fee twice this month. The fee is USD 12.00 and "
        "it has always come out once a month, on the same day. Please look at my current account ACC-1009-01. On the day it was due I can "
        f"see two lines for the same fee, one straight after the other, on {d_ago(today, 8)}. That is USD 24.00 for one month. "
        "I have not changed my account, I have not added any new service, and no one from the bank told me about any new charge.\n\n"
        "This is not the first time I have had to write about fees. Last time I was told I had not read the notice. I do read my notices. "
        "I would like the extra fee given back, and I would like to know why it happened so that it does not happen again next month. "
        "I am on a fixed income and USD 12.00 matters to me.\n\nI would like an answer in writing, by email, and I would like it to say "
        "plainly what you found.\n\nAnselm Drozdowich"),
        {"account_ids": ["ACC-1009-01"], "transaction_ids": [f3, f4]})
    out["CMP-1002"] = cmp_("CMP-1002", "CUS-1014", "call", rec_2, acked(rec_2), "Payment arrived late", (
        "Call recorded by the contact centre, written up word for word by the officer.\n\nThe customer, Rosalind Heathcote-Brae, said: I sent USD 1,850 "
        "to a friend a week ago as a deposit for a flat. It had to be there by the end of last week. Your app told me it was sent, but my friend "
        "says nothing arrived for days. The landlord nearly gave the flat to someone else and my friend had to beg for more time. I want to know "
        "where the money was and why it took so long. I also want the bank to pay me something for the stress, because this was my deposit and "
        "I did everything right. I have already spoken to your payments people and they opened a case, but nobody has told me what happened. "
        "Please do not send me a standard letter. I want the dates, the actual dates, of when each bank had my money. If you lost it, say "
        "so. If you did not, show me. I am not accusing anyone yet. I only want a straight account of what happened to my payment and "
        "whether the bank did anything wrong.\n\nThe customer asked for a reply in writing within the time the bank promises."),
        {"account_ids": ["ACC-1014-01"], "payment_ids": ["PAY-6001"], "investigation_ids": ["INV-5001"]})
    out["CMP-1003"] = cmp_("CMP-1003", "CUS-1016", "letter", rec_3, acked(rec_3), "Loan declined", (
        "Dear Sir or Madam,\n\nI applied for a personal loan of USD 14,000 three weeks ago. I have a permanent job, I have never missed a payment on "
        "anything, and I was told in the branch that my application looked fine. Two weeks ago I received a short letter saying the loan was declined. "
        "The letter gave no real reason. I think this is unfair and I think I was treated badly by the bank. I was also told by the officer that "
        "I would hear within five days and it took much longer.\n\nI need the money for furniture and a second-hand car, because my current car "
        "has failed its test. Without the loan I cannot get to work. I would like you to look at the decision again and approve the loan, and "
        "I would like an apology for the way my application was handled.\n\nI have attached nothing new because I have nothing new to add. "
        "My income is what it is. I only want the bank to be fair to me.\n\nYours faithfully,\nIsolde Pennywhistle"),
        {"account_ids": ["ACC-1016-01"], "loan_application_ids": ["LAP-8010"]})
    out["CMP-1004"] = cmp_("CMP-1004", "CUS-1001", "branch", rec_4, acked(rec_4), "Card blocked after a death in the family", (
        "Written down by the branch officer at the customer's request, and read back to her.\n\nI came in today because my debit card stopped "
        f"working at the chemist and again at the grocer. I am told it was blocked six days ago. My husband died on {d_ago(today, 18)}. I told the "
        "bank, because I thought I had to. Nobody asked me whether I wanted anything done to my own card. I am a customer too. I have "
        "had to go to the funeral director, to the doctor and to the registry on my own, and now I cannot even buy bread without asking my sister "
        "for money. I cried at the till. I do not want a lot of forms. I want my card to work, I want someone to tell me what happened, and "
        "I want it written to me in a kind way, because I have had enough of letters that talk to me like a file number.\n\nThe customer "
        "was composed but upset during the visit. She asked that one person deals with this and that she is not asked to explain "
        "again what has happened in her family.\n\nCard ending 9143. Signed by the officer, with the customer's agreement."),
        {"account_ids": ["ACC-1001-01"], "card_ids": ["CRD-2004"]})
    out["CMP-1005"] = cmp_("CMP-1005", "CUS-1003", "letter", rec_5, "", "Reference letter never sent", (
        f"Dear Sir or Madam,\n\nOn {add_working_days(rec_5, -3).isoformat()} I asked at the Marlow Reach branch for a letter from the bank confirming "
        "that I have held my account with you for more than ten years. I needed it for a rental application. The cashier said it would "
        "be posted to me within five working days. It has not come. I rang the branch twice and each time was told that someone would call me back. "
        "No one has.\n\nBecause of the delay I missed the date the letting agent gave me, and I have had to ask them for more time as a favour. "
        "I am writing this as a formal complaint because I have already tried the ordinary way twice. I would like the letter sent today, by "
        "email and by post, and I would like to know why a simple request took so long.\n\nI have not heard anything from the bank about this "
        "letter of complaint either. If there is a process, I should have been told about it.\n\nSabine Tarrowgate"),
        {"account_ids": ["ACC-1003-01"]})
    # an earlier, closed complaint by CUS-1009, for the history
    r0 = add_working_days(base, -105)
    c0 = cmp_("CMP-0901", "CUS-1009", "letter", r0, acked(r0), "Notice of a change in the account fee not received", (
        "Dear Sir or Madam,\n\nThe monthly fee on my account went up from USD 10.00 to USD 12.00 and I never received a notice. I want the "
        "increase reversed. I am a pensioner and I count every dollar.\n\nAnselm Drozdowich"), {"account_ids": ["ACC-1009-01"]})
    c0.update(status="closed", sent={
        "sent_on": add_working_days(r0, 11).isoformat(), "approved_by": "S. Pellworth, Complaints team lead", "outcome": "not_upheld",
        "response_text": "The notice was posted 60 days before the change, as the account terms require, and a copy is attached. The change stands.",
        "redress_amount": 0.0, "redress_currency": "USD"})
    c0["classifications"] = [{"version": 1, "drafted_by": "S. Pellworth", "drafted_at": f"{add_working_days(r0, 2).isoformat()}T09:00:00+00:00",
                              "category": "fees_and_charges", "severity": "low", "may_be_vulnerable": False, "vulnerability_reason": "",
                              "priority": "normal"}]
    out["CMP-0901"] = c0
    return out


def align_accounts(tb, accounts: dict, today: date) -> None:
    """Make the core transactions agree with the documents and loans that describe the same customers."""
    rows = tb.rows
    # CUS-1012: salary and car loan instalments as the application LAP-8001 shows them, no rent (she owns her home)
    for t in list(rows.values()):
        if t["account_id"] == "ACC-1012-01" and t["type"] == "salary":
            t.update(amount=4010.0, counterparty="Westergate Water Board", narrative="Salary Westergate Water Board")
        if t["account_id"] in ("ACC-1012-01", "ACC-1013-01") and t["narrative"] == "Rent":
            del rows[t["transaction_id"]]
    loans = [("ACC-1012-01", 42, 450.0), ("ACC-1012-01", 72, 450.0), ("ACC-1013-01", 70, 930.0), ("ACC-1002-01", 75, 210.0),
             ("ACC-1004-01", 50, 275.0), ("ACC-1005-01", 63, 520.0)]
    for acc, ago, amount in loans:
        name = "Car loan instalment" if acc == "ACC-1012-01" else "Home loan instalment" if acc == "ACC-1013-01" else "Loan instalment"
        tb.add(accounts[acc], ago, amount, "debit", "loan_repayment", "Meridian Trust Bank", name)
    # CUS-1017 and CUS-1018: three months of credits and debits that add up to the monthly totals on the statements in LAP-8002 and LAP-8003
    for acc, months in (("ACC-1017-01", [(75, 55600.0, 52310.0), (45, 50300.0, 49120.0), (15, 52400.0, 50010.0)]),
                        ("ACC-1018-01", [(75, 142400.0, 136900.0), (45, 138100.0, 131250.0), (15, 137500.0, 132800.0)])):
        for t in list(rows.values()):
            if t["account_id"] == acc and t["narrative"] in ("Customer payment", "Supplier payment"):
                del rows[t["transaction_id"]]
        for ago, cr, dr in months:
            tb.add(accounts[acc], ago, cr, "credit", "transfer_in", "Dunmere Retail Group", "Customer receipts, month total")
            tb.add(accounts[acc], ago, dr, "debit", "transfer_out", "Tallowmere Packaging", "Supplier payments, month total")


# ------------------------------------------------------------------ simulated arrivals

def sim_complaint(d: dict, today: date, tb_add, kind: int, n: int) -> tuple[str, str]:
    """One new complaint from four rotating templates. tb_add(account, days_ago, amount, ...) adds a transaction."""
    cid = f"CMP-{1100 + n}"
    today = last_working_day(today)
    link = {"account_ids": [], "transaction_ids": [], "card_ids": [], "payment_ids": [], "investigation_ids": [], "loan_ids": [],
            "loan_application_ids": []}
    ack, vulnerable_note = "", ""
    if kind == 0:
        num, received, channel = 1011, add_working_days(today, -2), "email"
        acc = d["accounts"]["ACC-1011-01"]
        t1 = tb_add(acc, 3, 9.00, "debit", "fee", "Meridian Trust Bank", "Card replacement fee")
        t2 = tb_add(acc, 3, 9.00, "debit", "fee", "Meridian Trust Bank", "Card replacement fee")
        link.update(account_ids=["ACC-1011-01"], transaction_ids=[t1, t2])
        subject = "Card replacement fee taken twice"
        words = ("I asked for one replacement card and I have been charged the replacement fee of USD 9.00 two times on the same day. "
                 "Please check account ACC-1011-01 and give one of them back. I only ever received one card. I would like a short written answer "
                 "that says what happened and when I will see the money, and I would like it done quickly. Thank you. Tobias Wrenfield")
        ack = add_working_days(received, 1).isoformat()
        text = "A customer says a fee was charged twice. Two fee entries of the same amount are on the account."
    elif kind == 1:
        num, received, channel = 1011, add_working_days(today, -3), "call"
        link.update(account_ids=["ACC-1011-01"], card_ids=["CRD-2007"])
        subject = "Card declined abroad"
        words = ("The customer says his card was declined three times at a hotel in Norvania last week. He had not told the bank he was travelling. "
                 "He says the bank should have known and wants an apology and the card checked. The contact centre notes that the card was stopped "
                 "by the fraud rule for online payments abroad at night, as it is designed to do, and that it was released on the same call when he "
                 "confirmed it was him. No fee was charged. He asked for a written answer.")
        ack = add_working_days(received, 1).isoformat()
        text = "A customer says his card was declined abroad. The decline was the fraud rule working as designed and it was released at once."
    elif kind == 2:
        num, received, channel = 1013, add_working_days(today, -9), "letter"
        link.update(account_ids=["ACC-1013-01"], loan_ids=["LN-9003"])
        subject = "Home loan statement was wrong"
        words = ("My annual home loan statement for the loan LN-9003 shows an interest figure that is different from the figure in my own records "
                 "by about USD 140. I wrote to the bank nine working days ago and have had no reply of any kind, not even a note that you "
                 "received it. I would like the statement checked and corrected if it is wrong, and I would like to be told why I have been "
                 "ignored. Cassius Dunmore")
        text = "A customer wrote nine working days ago and has not been acknowledged. The acknowledgement is overdue."
    else:
        num, received, channel = 1016, add_working_days(today, -1), "branch"
        link.update(account_ids=["ACC-1016-01"])
        subject = "Overdraft fee after losing my job"
        words = ("I lost my job two weeks ago and my pay did not arrive this month. I went USD 60 over my limit and the bank charged me a USD 15.00 "
                 "overdraft fee. I am frightened about money and I cannot sleep. I am asking the bank to take the fee off and to tell me what help "
                 "there is. I do not understand the letters you send me. I would like someone to talk to me in person. Isolde Pennywhistle")
        ack = add_working_days(received, 1).isoformat()
        text = "A customer who lost her job is charged an overdraft fee and says she is frightened. She may be vulnerable."
    cust = d["customers"][f"CUS-{num}"]
    d["complaints"][cid] = {"complaint_id": cid, "customer_id": cust["customer_id"], "status": "open", "channel": channel,
                            "received": received.isoformat(), "acknowledged_on": ack, "subject": subject, "customer_words": words,
                            "linked": link, "classifications": [], "response_drafts": [], "sent": None}
    return cid, (f"A new complaint {cid} has arrived in the complaints system from {cust['name']} ({cust['customer_id']}): {subject.lower()}. {text} "
                 f"It is open and needs a classification and a response. Read it with get_complaint in the complaints system.")
