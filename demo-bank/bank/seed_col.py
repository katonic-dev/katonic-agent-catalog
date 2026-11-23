"""Seed data, part 8: collections calls (transcripts), the bank's conduct rules for them, and the loans they concern."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from .seed_base import d_ago

RULES = {
    "CR-01": {"rule_id": "CR-01", "title": "Say who you are",
              "text": "At the start of the call the caller says their name and that they are calling from Meridian Trust Bank."},
    "CR-02": {"rule_id": "CR-02", "title": "Confirm identity before any detail of the debt",
              "text": "When the customer is on the line, the caller confirms who they are speaking to, with the date of birth and the first line "
                      "of the address, before giving any detail of the debt: the amount, the loan or the days overdue. Saying only that the "
                      "call is about the customer's account is allowed."},
    "CR-03": {"rule_id": "CR-03", "title": "No threats and no pressure",
              "text": "The caller does not threaten, shout, mock or press the customer. A caller may state calmly and accurately what the loan "
                      "terms say will happen next, and may be firm and ask for a date. The caller does not invent consequences, does not name "
                      "consequences that the terms do not provide, and does not keep demanding after the customer has answered."},
    "CR-04": {"rule_id": "CR-04", "title": "Calls only between 08:00 and 20:00",
              "text": "Collections calls are made only between 08:00 and 20:00, local time. A call that starts at or after 20:00 or before "
                      "08:00 breaks this rule."},
    "CR-05": {"rule_id": "CR-05", "title": "Offer hardship options when hardship is mentioned",
              "text": "When the customer mentions hardship (loss of a job, illness, bereavement, a reduction in pay or any other difficulty), the "
                      "caller offers the bank's hardship options in that call: a payment holiday of up to 3 months, reduced payments for up "
                      "to 6 months, a longer loan term, and a referral to the free money advice service. The caller does not need to push for "
                      "a payment first."},
    "CR-06": {"rule_id": "CR-06", "title": "Say nothing about the debt to anyone else",
              "text": "If someone other than the customer answers, the caller gives only their name and the bank's name, asks for the customer "
                      "to call back, and says nothing about a loan, a debt or an amount."},
    "CR-07": {"rule_id": "CR-07", "title": "Record any promise to pay exactly",
              "text": "When the customer promises to pay, the caller states the amount, the date and the way of paying, the customer agrees, and "
                      "the caller records exactly that."}}


def _fmt(d: date) -> str:
    return f"{d:%A} {d.day} {d:%B}"


def _speak(d: str) -> str:
    y, m, dd = (int(x) for x in d.split("-"))
    return f"{dd} {date(y, m, dd):%B %Y}"


def _turns(start: str, lines: list[tuple[str, str]]) -> list[dict]:
    t = datetime.strptime(start, "%H:%M:%S")
    out = []
    for who, text in lines:
        out.append({"time": t.strftime("%H:%M:%S"), "speaker": who, "text": text})
        t += timedelta(seconds=3 + round(len(text.split()) * 0.45))
    return out


def _call(call_id, day, start, customer, loan, staff, arrears, lines):
    return {"call_id": call_id, "date": day, "started_at": f"{day} {start}", "direction": "outbound", "status": "unreviewed",
            "customer_id": customer, "loan_id": loan, "staff": staff, "arrears": arrears,
            "transcript": _turns(start, lines), "reviews": [], "reviewed": None}


def add_loans(loans: dict, exposure: dict, today: date) -> None:
    extra = {"LN-9101": ("CUS-1002", 6000.0, 3900.0, 420), "LN-9102": ("CUS-1004", 5500.0, 4100.0, 300), "LN-9103": ("CUS-1005", 9000.0, 7200.0, 600)}
    for lid, (cid, principal, outstanding, ago) in extra.items():
        loans[lid] = {"loan_id": lid, "customer_id": cid, "product": "Personal loan", "currency": "USD", "principal": principal,
                      "outstanding": outstanding, "status": "active", "start_date": d_ago(today, ago),
                      "maturity_date": d_ago(today, -(1095 - ago))}
        e = exposure[cid]
        e["loans"].append({k: loans[lid][k] for k in ("loan_id", "product", "principal", "outstanding", "status", "maturity_date")})
        e["total_outstanding_loans"] = round(sum(x["outstanding"] for x in e["loans"]), 2)


def build_calls(customers: dict, today: date) -> dict:
    out = {}
    one, two = d_ago(today, 1), d_ago(today, 2)

    def put(c):
        out[c["call_id"]] = c

    def arrears(instalment, behind, days, last):
        return {"monthly_instalment": instalment, "instalments_behind": behind, "amount_overdue": round(instalment * behind, 2),
                "currency": "USD", "days_past_due": days, "last_payment_date": d_ago(today, last)}

    # CAL-1001: clean call, ends in a promise to pay
    c = customers["CUS-1012"]
    pay = today + timedelta(days=3)
    put(_call("CAL-1001", one, "11:20:05", "CUS-1012", "LN-9005", {"staff_id": "STF-3301", "name": "Anneliese Rookwood"},
              arrears(450.00, 1, 12, 42), [
        ("Caller", "Good morning. This is Anneliese Rookwood, calling from Meridian Trust Bank. Am I speaking with Marguerite Oakhaven?"),
        ("Customer", "Yes, speaking."),
        ("Caller", "Thank you. Before I say anything about your account, I need to check who I am talking to. Could you tell me your date of birth, please?"),
        ("Customer", _speak(c["date_of_birth"]) + "."),
        ("Caller", "Thank you. And the first line of your address?"),
        ("Customer", "19 Bellwether Close."),
        ("Caller", "That matches our records, thank you. I am calling about your car loan LN-9005. The monthly payment of USD 450.00 that was due 12 days ago has not reached us. Do you know what happened?"),
        ("Customer", "Oh no. I changed my debit card last month and I think the direct debit failed. I did not notice."),
        ("Caller", "That is a common reason. Is there anything else going on that makes the payments hard at the moment?"),
        ("Customer", "No, it is only the new card. Nothing else."),
        ("Caller", "Good. Would you be able to make the payment now, or on a date that suits you better?"),
        ("Customer", f"I can pay on {_fmt(pay)}, when I am paid."),
        ("Caller", f"So that I record it correctly: you will pay USD 450.00 on {_fmt(pay)}, by card in the app. Is that right?"),
        ("Customer", f"Yes. USD 450.00 on {_fmt(pay)}, by card in the app."),
        ("Caller", "Thank you. I will note exactly that, and I will not call again before then. Would you like to update the card for your direct debit as well?"),
        ("Customer", "Yes please. I will do it in the app tonight."),
        ("Caller", "Thank you for your time, Ms Oakhaven. Goodbye."),
        ("Customer", "Goodbye.")]))
    # CAL-1002: the debt is discussed before identity is confirmed
    c = customers["CUS-1013"]
    pay = today + timedelta(days=2)
    put(_call("CAL-1002", one, "15:40:30", "CUS-1013", "LN-9003", {"staff_id": "STF-3302", "name": "Dermot Fallowfield"},
              arrears(930.00, 2, 38, 70), [
        ("Caller", "Hello, is that Mr Dunmore? This is Dermot Fallowfield from Meridian Trust Bank."),
        ("Customer", "Yes?"),
        ("Caller", "I am calling about your home loan. You are two payments behind, a total of USD 1,860.00, and the loan is now 38 days past due."),
        ("Customer", "What? I thought that was sorted out last month."),
        ("Caller", "Before we go on I do need to confirm it is you. Could you give me your date of birth?"),
        ("Customer", _speak(c["date_of_birth"]) + "."),
        ("Caller", "And the first line of your address?"),
        ("Customer", "5 Thistledown Mews."),
        ("Caller", "Thank you. As I said, USD 1,860.00 is overdue. When can you pay it?"),
        ("Customer", "I had a problem with a bank transfer last month and then I was away. I can pay all of it."),
        ("Caller", "That is good to hear. When?"),
        ("Customer", f"On {_fmt(pay)}."),
        ("Caller", f"To be exact: USD 1,860.00 on {_fmt(pay)}, by bank transfer from your account with us. Is that correct?"),
        ("Customer", "Yes, that is correct."),
        ("Caller", f"Thank you. I have noted USD 1,860.00 on {_fmt(pay)} by bank transfer. Goodbye, Mr Dunmore."),
        ("Customer", "Goodbye.")]))
    # CAL-1003: the customer says they lost their job, no hardship option is offered
    c = customers["CUS-1002"]
    pay = today + timedelta(days=4)
    put(_call("CAL-1003", two, "09:05:12", "CUS-1002", "LN-9101", {"staff_id": "STF-3303", "name": "Maren Tidewell"},
              arrears(210.00, 2, 41, 75), [
        ("Caller", "Good morning, this is Maren Tidewell from Meridian Trust Bank. Is that Mr Quillfeather?"),
        ("Customer", "Yes, it is."),
        ("Caller", "Thank you. For security I need to check a few things before I talk about your account. What is your date of birth?"),
        ("Customer", _speak(c["date_of_birth"]) + "."),
        ("Caller", "And the first line of your address?"),
        ("Customer", "3 Copper Kettle Lane."),
        ("Caller", "Thank you. I am calling about your personal loan LN-9101. Two payments of USD 210.00 are overdue, USD 420.00 in all, and it is 41 days past due."),
        ("Customer", "I know. I lost my job six weeks ago. They closed the depot. I have nothing coming in."),
        ("Caller", "I see. The payments are still due, though. Can you find the USD 420.00 this week?"),
        ("Customer", "I cannot. I have nothing. I am living on what is left in my current account."),
        ("Caller", "Is there a family member who could help, or any savings you could use?"),
        ("Customer", "No. My family does not have it either."),
        ("Caller", "I do need a date from you. What can you pay and when?"),
        ("Customer", f"I could try USD 100 on {_fmt(pay)}. That is all."),
        ("Caller", f"So USD 100.00 on {_fmt(pay)}, by card. Is that right?"),
        ("Customer", "Yes, by card."),
        ("Caller", f"Thank you. I have noted USD 100.00 on {_fmt(pay)} by card. Goodbye."),
        ("Customer", "Goodbye.")]))
    # CAL-1004: someone else answers and the caller mentions the debt
    put(_call("CAL-1004", two, "18:50:41", "CUS-1004", "LN-9102", {"staff_id": "STF-3304", "name": "Casimir Holloway"},
              arrears(275.00, 1, 20, 50), [
        ("Caller", "Good evening. This is Casimir Holloway, calling from Meridian Trust Bank. May I speak to Emeric Lowenhall, please?"),
        ("Other person", "He is out at the moment. Who is this?"),
        ("Caller", "I am calling about his loan. He is behind with a payment of USD 275.00 and we need him to call us."),
        ("Other person", "His loan? He never told me he had a loan."),
        ("Caller", "Oh, I see. Well, it is urgent. He owes the bank USD 275.00 and it is 20 days late."),
        ("Other person", "I am only his sister. I am staying for a few days. I do not know anything about his money."),
        ("Caller", "Please ask him to ring the number on his last letter from us. It really cannot wait."),
        ("Other person", "I will tell him you called. Which number should he ring? What is your name again?"),
        ("Caller", "Casimir Holloway, from Meridian Trust Bank. The number is at the top of the last letter we sent him."),
        ("Other person", "Casimir Holloway, Meridian Trust Bank. I have written it on the pad by the phone. Is there anything else?"),
        ("Caller", "No, that is all. Thank you. Goodbye."),
        ("Other person", "Goodbye.")]))
    # CAL-1005: a firm call that breaks no rule
    c = customers["CUS-1005"]
    pay = today + timedelta(days=4)
    put(_call("CAL-1005", one, "19:35:20", "CUS-1005", "LN-9103", {"staff_id": "STF-3305", "name": "Bronagh Stillwell"},
              arrears(520.00, 2, 33, 63), [
        ("Caller", "Good evening. This is Bronagh Stillwell, calling from Meridian Trust Bank. Am I speaking with Mr Castellane?"),
        ("Customer", "Yes. What is this about? It is a bit late."),
        ("Caller", "I am sorry to call in the evening. I will be brief. First I need to check it is you. What is your date of birth?"),
        ("Customer", _speak(c["date_of_birth"]) + "."),
        ("Caller", "And the first line of your address?"),
        ("Customer", "9 Orchard Gate."),
        ("Caller", "Thank you. I am calling about your personal loan LN-9103. Two payments of USD 520.00 are overdue, USD 1,040.00 in all, and it is 33 days past due."),
        ("Customer", "I will pay it when I can. I have been travelling and I forgot. Do not keep chasing me."),
        ("Caller", "Mr Castellane, I have to be straightforward. Under your loan terms, when a loan is 45 days past due the account passes to the bank's recovery team, and that adds costs. You are at 33 days. I would much rather we agree a payment today. Is anything making it hard for you to pay?"),
        ("Customer", "No. I just forgot. I am annoyed, that is all."),
        ("Caller", "Understood. What can you pay, and on what date?"),
        ("Customer", f"All of it. USD 1,040 on {_fmt(pay)}."),
        ("Caller", f"To be exact: USD 1,040.00 on {_fmt(pay)}, by bank transfer. Is that right?"),
        ("Customer", "Yes. By bank transfer."),
        ("Caller", f"Thank you. I have noted USD 1,040.00 on {_fmt(pay)} by bank transfer. Goodbye."),
        ("Customer", "Goodbye.")]))
    return out


def sim_call(d: dict, today: date, kind: int, n: int) -> tuple[str, str]:
    """One new call from four rotating templates. Returns the id and a plain sentence."""
    cid_call = f"CAL-{1100 + n}"
    cid, loan, staff = [("CUS-1012", "LN-9005", "Ruairi Penhallow"), ("CUS-1002", "LN-9101", "Elsbeth Marchbank"),
                        ("CUS-1005", "LN-9103", "Gawain Thornley"), ("CUS-1004", "LN-9102", "Odette Ravensdale")][kind]
    c = d["customers"][cid]
    first = c["name"].split()[0]
    sid = f"STF-33{20 + kind}"
    st = {"staff_id": sid, "name": staff}
    ident = [("Caller", f"Thank you. And the first line of your address?"), ("Customer", c["address"].split(",")[0] + ".")]
    dob = [("Caller", "Please confirm your date of birth first."), ("Customer", _speak(c["date_of_birth"]) + "."), *ident]
    pay = today + timedelta(days=3)
    if kind == 0:
        start, arr = "10:10:00", (450.00, 1, 9)
        lines = [("Caller", f"Good morning, this is {staff} from Meridian Trust Bank. Is that {c['name']}?"), ("Customer", "Yes."), *dob,
                 ("Caller", "Thank you. Your loan payment of USD 450.00 is 9 days overdue. Do you know why?"),
                 ("Customer", "I was away on holiday and forgot it. It is just a mix-up."),
                 ("Caller", "Thank you. Is there anything that makes payments hard for you?"), ("Customer", "No, nothing."),
                 ("Caller", f"When can you pay?"), ("Customer", f"On {_fmt(pay)}."),
                 ("Caller", f"So USD 450.00 on {_fmt(pay)}, by card in the app. Is that right?"), ("Customer", "Yes, that is right."),
                 ("Caller", "Thank you. I have noted it exactly. Goodbye.")]
        text = "A clean call that ends in an exact promise to pay."
    elif kind == 1:
        start, arr = "20:25:10", (210.00, 1, 17)
        lines = [("Caller", f"Good evening, this is {staff} from Meridian Trust Bank. Is that {c['name']}?"), ("Customer", "Yes. It is after eight."),
                 *dob, ("Caller", "Thank you. Your loan payment of USD 210.00 is 17 days overdue."),
                 ("Customer", "I will pay it on payday. Please do not ring this late again."),
                 ("Caller", f"When is payday?"), ("Customer", f"{_fmt(pay)}."),
                 ("Caller", f"So USD 210.00 on {_fmt(pay)}, by card in the app. Is that right?"), ("Customer", "Yes."),
                 ("Caller", "Thank you. Goodbye.")]
        text = "A call that starts at 20:25, after the permitted hours."
    elif kind == 2:
        start, arr = "13:30:00", (520.00, 2, 52)
        lines = [("Caller", f"Hello, this is {staff} from Meridian Trust Bank. Is that {c['name']}?"), ("Customer", "Yes."), *dob,
                 ("Caller", "Your loan is 52 days past due. USD 1,040.00 is overdue."),
                 ("Customer", "I know. I will pay at the end of the week."),
                 ("Caller", "That is not good enough. If you do not pay today we will send someone to your house tonight and you will lose your home."),
                 ("Customer", "That is not what my loan says. It is a personal loan. It is not secured on my house."),
                 ("Caller", "Do not argue with me. Pay today or you will be sorry."),
                 ("Customer", "I am going to hang up and speak to the bank in writing."),
                 ("Caller", "You do that. Goodbye.")]
        text = "The caller says someone will come to the customer's house tonight and that the customer will lose their home."
    else:
        start, arr = "14:05:30", (275.00, 3, 75)
        lines = [("Caller", f"Good afternoon, this is {staff} from Meridian Trust Bank. Is that {c['name']}?"), ("Customer", "Yes."), *dob,
                 ("Caller", "Thank you. Your loan has three payments overdue, USD 825.00, and it is 75 days past due."),
                 ("Customer", "I have been very ill. I was in hospital for a month and I cannot work yet."),
                 ("Caller", "I am sorry to hear that. The bank has hardship options: a payment holiday of up to 3 months, reduced payments for up to 6 months, a longer loan term, and a referral to the free money advice service. Would you like me to explain any of them?"),
                 ("Customer", "Yes please, the payment holiday."),
                 ("Caller", "I will pass your request for a 3 month payment holiday to the hardship team today. They will call you within two working days. Is that all right?"),
                 ("Customer", "Yes, thank you. That is a relief."),
                 ("Caller", "I have noted that you agreed to the hardship team calling you within two working days. Goodbye and take care.")]
        text = "The customer says they have been ill and the caller offers the hardship options."
    inst, behind, days = arr
    d["collections_calls"][cid_call] = _call(cid_call, today.isoformat(), start, cid, loan, st, {
        "monthly_instalment": inst, "instalments_behind": behind, "amount_overdue": round(inst * behind, 2), "currency": "USD",
        "days_past_due": days, "last_payment_date": d_ago(today, days + 30)}, lines)
    return cid_call, (f"A new collections call {cid_call} has arrived in the collections system: a call by {staff} to {first} {c['name'].split()[-1]} "
                      f"({cid}) about loan {loan}. {text} It is unreviewed and needs a review. Read it with get_collections_call in the collections system.")
