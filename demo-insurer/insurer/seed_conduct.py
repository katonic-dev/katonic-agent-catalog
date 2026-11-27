"""Seed data, part 6: conduct. Complaints with the complaints procedure, the conduct rules with an audit sample, the
publications of the regulators with the obligations register, and the document sets of disputed claims with the privilege guide.

The day counts are here as well: working days with the public holidays of Meridia, the deadlines of a complaint, and an audit
file measured against the dated conduct rules. The system calls them, so an agent never counts a day.

Everything is invented: the Meridia Insurance Authority, the Meridia Data Protection Office, every circular, every person,
every firm of lawyers and every court reference.
"""

from __future__ import annotations

import copy
from datetime import date, timedelta

from .seed_policy import d_ago, d_ahead, long_date


def plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


# ---------------------------------------------------------------- working days

# The public holidays of Meridia, the same day each year. Invented.
HOLIDAYS_EACH_YEAR = [(3, 9, "Founding Day"), (6, 22, "Harbour Day"), (10, 12, "Lantern Day"), (11, 16, "Charter Day")]


def holidays_of(year: int) -> dict:
    return {date(year, m, d): name for m, d, name in HOLIDAYS_EACH_YEAR}


def holiday_name(day: date) -> str | None:
    return holidays_of(day.year).get(day)


def is_working_day(day: date) -> bool:
    return day.weekday() < 5 and holiday_name(day) is None


def add_working_days(start: date, n: int) -> date:
    """The n-th working day after the start. The start itself is day 0."""
    day = start
    while n > 0:
        day += timedelta(days=1)
        if is_working_day(day):
            n -= 1
    return day


def sub_working_days(start: date, n: int) -> date:
    day = start
    while n > 0:
        day -= timedelta(days=1)
        if is_working_day(day):
            n -= 1
    return day


def working_days_between(first: date, last: date) -> int:
    """Working days after the first day, up to and including the last. 0 when the last is not after the first."""
    n, day = 0, first
    while day < last:
        day += timedelta(days=1)
        if is_working_day(day):
            n += 1
    return n


def holidays_between(first: date, last: date) -> list[dict]:
    out, day = [], first
    while day < last:
        day += timedelta(days=1)
        name = holiday_name(day)
        if name:
            out.append({"date": day.isoformat(), "name": name})
    return out


def last_working_day_on_or_before(day: date) -> date:
    while not is_working_day(day):
        day -= timedelta(days=1)
    return day


def holiday_list(today: date) -> list[dict]:
    rows = []
    for year in (today.year - 1, today.year, today.year + 1):
        rows += [{"date": d.isoformat(), "name": name} for d, name in sorted(holidays_of(year).items())]
    return rows


WORKING_DAYS_NOTE = ("A working day is any day that is not one of the two weekend days and not a public holiday of Meridia. The "
                     "public holidays are Founding Day (9 Mar), Harbour Day (22 Jun), Lantern Day (12 Oct) and Charter Day (16 Nov), "
                     "each year. The day something is received is day 0 and the count starts on the next day. The system does every "
                     "count and lists the public holidays that fell inside it.")


# ---------------------------------------------------------------- complaints procedure

ACK_WORKING_DAYS = 3
FINAL_DAYS = 30
FINAL_DAYS_VULNERABLE = 15

COMPLAINT_CATEGORIES = {c["category_id"]: c for c in [
    {"category_id": "CC-1", "name": "Service",
     "text": "How we treated the customer outside a claim: long waits on the telephone, a call back that was promised and not made, "
             "rudeness, letters or emails not answered."},
    {"category_id": "CC-2", "name": "Claim decision",
     "text": "The customer does not accept a decision on a claim: a claim declined in whole or in part, or the amount offered."},
    {"category_id": "CC-3", "name": "Claim handling",
     "text": "How a claim is being handled while it is open: delay, no news, help that was not arranged. The decision itself is not "
             "in question."},
    {"category_id": "CC-4", "name": "Premiums, charges and refunds",
     "text": "Money taken or owed outside a claim: a premium collected twice, a charge the customer did not expect, a refund not paid."},
    {"category_id": "CC-5", "name": "Sale of the policy",
     "text": "What the customer was told or not told when the policy was sold, or a policy that did not fit what the customer asked for."},
    {"category_id": "CC-6", "name": "Policy administration",
     "text": "Policy documents not sent or wrong, a change to the policy not made, a certificate not issued, renewal or cancellation "
             "handled wrongly."},
]}

COMPLAINT_RULES = {r["rule_id"]: r for r in [
    {"rule_id": "CH-1", "heading": "Acknowledgement", "kind": "measured",
     "text": f"A complaint is acknowledged in writing within {ACK_WORKING_DAYS} working days after the day it is received. An "
             "acknowledgement on the last of those days is in time: the complaint is late only from the day after."},
    {"rule_id": "CH-2", "heading": "Final response", "kind": "measured",
     "text": f"The final response is given within {FINAL_DAYS} days after the day the complaint is received. These are calendar days. "
             "Where the last day is not a working day, the response is due on the last working day before it."},
    {"rule_id": "CH-3", "heading": "A vulnerable customer", "kind": "measured",
     "text": "Where the customer care record marks the customer as vulnerable, the complaint goes to a complaints officer on the day "
             f"it is logged, the customer is contacted in the way the record prefers, and the final response is given within "
             f"{FINAL_DAYS_VULNERABLE} days in place of {FINAL_DAYS}. The system reads the mark from the customer care record and "
             "applies the shorter limit."},
    {"rule_id": "CH-4", "heading": "The regulator or a lawyer is mentioned", "kind": "for_reading",
     "text": "A complaint that mentions the Meridia Insurance Authority, any other regulator, a lawyer or legal action goes to the "
             "senior complaints officer. The time limits do not change. This rule is read against the words of the complaint."},
    {"rule_id": "CH-5", "heading": "A repeat complaint", "kind": "for_reading",
     "text": "A complaint by the same customer about the same matter as an earlier complaint is a repeat complaint. It is logged as a "
             "new complaint with its own time limits and is linked to the first by that complaint's id. An earlier complaint by the "
             "same customer about a different matter is not linked."},
    {"rule_id": "CH-6", "heading": "What is not a complaint", "kind": "for_reading",
     "text": "A complaint is any expression of dissatisfaction, however it is worded. A question or a request that expresses no "
             "dissatisfaction is not a complaint: it is logged as an enquiry and passed to the policy servicing team, it has no "
             "category, and the time limits of CH-1 and CH-2 do not apply to it."},
    {"rule_id": "CH-7", "heading": "Who decides", "kind": "for_reading",
     "text": "A complaints officer decides whether a complaint is upheld or rejected, and signs and sends every letter. A draft "
             "response says what we understood, what will be looked at and by when. It does not say that the complaint is upheld or "
             "rejected, offers no money and gives no opinion on the law."},
]}

COMPLAINTS_HOW_TO_READ = ("The categories CC-1 to CC-6 sort a complaint by what it is about: choose the one that fits the main "
                          "thing the customer is unhappy with. The handling rules CH-1 to CH-7 say what happens next. Rules of the "
                          "kind measured turn on dates: the system works the dates and the day counts out. Rules of the kind "
                          "for_reading are read against the words of the complaint and the earlier complaints.")

COMPLAINT_ROLES = {"complaints_officer": "Rosamund Achterberg, complaints officer",
                   "senior_complaints_officer": "Leopold Vanterpool, senior complaints officer",
                   "policy_servicing": "the policy servicing team"}


def build_customer_care(today: date) -> dict:
    L = lambda ago: long_date(d_ago(today, ago))
    return {"Aldous Pennicott": {"customer": "Aldous Pennicott", "vulnerable": True, "recorded_on": d_ago(today, 3),
                                 "recorded_by": "Ottilie Marsh, claims handler",
                                 "reason": f"Aged 81, lives alone, and has been out of his home since the fire of {L(3)}.",
                                 "preferred_contact": "telephone"}}


def build_complaints(today: date) -> dict:
    L = lambda ago: long_date(d_ago(today, ago))
    A = lambda ahead: long_date(d_ahead(today, ahead))
    W = lambda n: sub_working_days(today, n).isoformat()
    out = {}

    def add(cid, status, channel, received, customer, policy_id, claim_id, text, acknowledged_on=None, closed=None):
        out[cid] = {"complaint_id": cid, "status": status, "channel": channel, "received": received, "customer": customer,
                    "policy_id": policy_id, "claim_id": claim_id, "text": text, "acknowledged_on": acknowledged_on,
                    "closed": closed, "response_drafts": []}

    # Two earlier complaints, closed by a complaints officer.
    add("CMP-7051", "closed", "email", d_ago(today, 44), "Henrietta Quillby", "POL-2006", None,
        "You have taken my premium of USD 31.50 twice from my bank account this month. Please pay the second one back.",
        acknowledged_on=d_ago(today, 43),
        closed={"closed_on": d_ago(today, 30), "category_id": "CC-4", "matter": "A premium of USD 31.50 collected twice.",
                "outcome_recorded": "Upheld by Rosamund Achterberg, complaints officer: the premium was collected twice. Her letter of "
                                    f"{L(30)} says the second payment of USD 31.50 will be refunded within 10 working days."})
    add("CMP-7052", "closed", "telephone", d_ago(today, 230), "Bram Tollermoor", "POL-2005", None,
        "Note of a telephone call, in the customer's words. 'I was kept waiting 50 minutes on your service line and then cut off. "
        "That is not good enough.'",
        acknowledged_on=d_ago(today, 229),
        closed={"closed_on": d_ago(today, 215), "category_id": "CC-1", "matter": "A wait of 50 minutes on the service line.",
                "outcome_recorded": f"Upheld by Rosamund Achterberg, complaints officer, with an apology by letter of {L(215)}."})

    add("CMP-7101", "new", "email", W(2), "Corwin Ashgrove", "POL-2001", None,
        f"I rang your service line on {L(9)} and again on {L(7)} with a simple question about my policy. Both times I waited more "
        "than 30 minutes, and both times I was promised a call back that never came. This is poor service and I want it looked into.")
    add("CMP-7102", "new", "letter", W(1), "Yvaine Corrimond", "POL-2010", "CLM-4010",
        "You have refused my claim CLM-4010 for the burst pipe at 2 Heron Wharf because the house was empty. I was abroad for my "
        "work and a neighbour looked in on the house. I think your decision is wrong and I want it looked at again.")
    add("CMP-7103", "new", "web form", W(2), "Odalys Fenwright", "POL-2004", "CLM-4004",
        f"I reported the theft of my car on {L(7)} (claim CLM-4004). Since then nobody has told me what is happening or when I "
        "will hear. I am paying for a hire car every day. If I do not get a proper answer I will take this to the Meridia Insurance "
        "Authority.", acknowledged_on=W(1))
    add("CMP-7104", "new", "telephone", W(1), "Aldous Pennicott", "POL-2007", "CLM-4007",
        f"Note of a telephone call, in the customer's words. 'I have been out of my house since the fire on {L(3)}. I am staying "
        "with a neighbour and sleeping on a settee. Nobody from your company has told me whether you will pay for somewhere for me "
        "to stay. I am 81 and I cannot go on like this. I want to complain.'")
    add("CMP-7105", "new", "email", W(3), "Henrietta Quillby", "POL-2006", None,
        f"On {L(44)} I complained that you had taken my premium of USD 31.50 twice. Your letter of {L(30)} said the second payment "
        "would be refunded within 10 working days. It has not been refunded. I am complaining again and I want my money back.",
        acknowledged_on=W(2))
    add("CMP-7106", "new", "email", W(1), "Isaura Venn", "POL-2011", None,
        "Could you tell me whether my motor policy gives me a courtesy car while mine is being repaired? I would also like to add my "
        f"daughter as a named driver from {A(5)}. What do you need from me?")
    add("CMP-7107", "new", "web form", W(8), "Bram Tollermoor", "POL-2005", None,
        f"I asked for my certificate of motor insurance on {L(24)} and again on {L(17)}. It has still not been sent and I need it "
        "for the vehicle licence. Please treat this as a formal complaint.")
    add("CMP-7108", "new", "email", W(3), "Teodor Brackwell", "POL-2009", None,
        f"My bank statement shows a charge of USD 25.00 from you on {L(6)} for moving my payment date. Nobody told me there would "
        "be a charge when I asked for the change. I want it refunded.")
    return out


def complaint_deadlines(complaint: dict, vulnerable: bool, today_iso: str) -> dict:
    """The acknowledgement and final response dates of a complaint, with every day count. The system does the counting."""
    received, today = date.fromisoformat(complaint["received"]), date.fromisoformat(today_iso)
    R, T = long_date(complaint["received"]), long_date(today_iso)
    ack_due = add_working_days(received, ACK_WORKING_DAYS)
    ack_on = date.fromisoformat(complaint["acknowledged_on"]) if complaint["acknowledged_on"] else None
    until = ack_on or today
    elapsed = working_days_between(received, until)
    late_by = working_days_between(ack_due, until) if until > ack_due else 0
    lead = (f"Received on {R}. The acknowledgement is due within {plural(ACK_WORKING_DAYS, 'working day')}, by "
            f"{long_date(ack_due.isoformat())}.")
    if ack_on:
        status = "met" if ack_on <= ack_due else "met_late"
        verdict = "in time" if status == "met" else "late by " + plural(late_by, "working day")
        sentence = (f"{lead} It was acknowledged on {long_date(ack_on.isoformat())}, {plural(elapsed, 'working day')} after the day "
                    f"received: {verdict}.")
        left = None
    elif today > ack_due:
        status, left = "late", 0
        sentence = (f"{lead} No acknowledgement is recorded. {T} is {plural(elapsed, 'working day')} after the day received: the "
                    f"acknowledgement is late by {plural(late_by, 'working day')}.")
    elif today == ack_due:
        status, left = "due_today", 0
        sentence = (f"{lead} No acknowledgement is recorded. {T} is {plural(elapsed, 'working day')} after the day received, which "
                    "is the last day allowed: the acknowledgement is due on this day and is not late.")
    else:
        status, left = "not_yet_due", working_days_between(today, ack_due)
        sentence = (f"{lead} No acknowledgement is recorded. {T} is {plural(elapsed, 'working day')} after the day received: "
                    f"{plural(left, 'working day')} left, not late.")
    ack = {"rule_id": "CH-1", "limit_working_days": ACK_WORKING_DAYS, "due_on": ack_due.isoformat(),
           "acknowledged_on": complaint["acknowledged_on"], "working_days_elapsed": elapsed, "working_days_left": left,
           "working_days_late": late_by, "status": status, "late": status in ("late", "met_late"), "sentence": sentence}

    limit = FINAL_DAYS_VULNERABLE if vulnerable else FINAL_DAYS
    rule = "CH-3" if vulnerable else "CH-2"
    raw = received + timedelta(days=limit)
    due = last_working_day_on_or_before(raw)
    moved = ""
    if due != raw:
        moved = (f" Day {limit} is {long_date(raw.isoformat())}, which is not a working day, so the response is due on the last "
                 f"working day before it.")
    elapsed_days, left_days = (today - received).days, (due - today).days
    f_status = "late" if today > due else ("due_today" if today == due else "not_yet_due")
    why = ("The customer care record marks the customer as vulnerable, so the limit is "
           f"{FINAL_DAYS_VULNERABLE} days in place of {FINAL_DAYS} (CH-3)." if vulnerable else f"The limit is {FINAL_DAYS} days (CH-2).")
    tail = (f"{plural(left_days, 'day')} left." if left_days > 0 else
            ("It is due on this day." if left_days == 0 else f"It is late by {plural(-left_days, 'day')}."))
    final = {"rule_id": rule, "limit_days": limit, "due_on": due.isoformat(), "days_elapsed": elapsed_days,
             "days_left": max(left_days, 0), "days_late": max(-left_days, 0), "status": f_status, "late": f_status == "late",
             "sentence": f"{why} The final response is due by {long_date(due.isoformat())}.{moved} {T} is "
                         f"{plural(elapsed_days, 'day')} after the day received: {tail}"}
    return {"complaint_id": complaint["complaint_id"], "received": complaint["received"], "counted_to": today_iso,
            "customer_marked_vulnerable": vulnerable, "acknowledgement": ack, "final_response": final,
            "public_holidays_in_the_count": holidays_between(received, max(due, today)),
            "working_days_note": WORKING_DAYS_NOTE,
            "note": "These dates apply to a complaint. Where the item is a question or a request and not a complaint (CH-6), no time "
                    "limit of CH-1 or CH-2 applies."}


# ---------------------------------------------------------------- conduct rules and the audit sample

CND_ACK_WORKING_DAYS = 5
CND_DECISION_WORKING_DAYS = 20
CND_COOLING_OFF_NOTICE_DAYS = 7
CND_RENEWAL_NOTICE_DAYS = 21
CND_CHANGE_WORKING_DAYS = 10

FILE_KINDS = {"claims": "Claims file", "sales": "Sales file", "policy": "Policy file"}


def _cnd(rule_id, kind_of_file, heading, kind, text):
    return {"rule_id": rule_id, "kind_of_file": kind_of_file, "heading": heading, "kind": kind, "text": text}


CONDUCT_RULES = {r["rule_id"]: r for r in [
    _cnd("CND-1", "claims", "Acknowledging a claim", "measured",
         f"A claim is acknowledged in writing within {CND_ACK_WORKING_DAYS} working days after the day it is reported. An "
         f"acknowledgement on working day {CND_ACK_WORKING_DAYS} meets the rule."),
    _cnd("CND-2", "claims", "Deciding a claim", "measured",
         f"The decision on a claim is given within {CND_DECISION_WORKING_DAYS} working days after the day the pack is complete. A "
         f"decision on working day {CND_DECISION_WORKING_DAYS} meets the rule."),
    _cnd("CND-3", "claims", "A decline letter cites the clause", "for_reading",
         "A letter that declines a claim names the clause of the policy wording the decision relies on, by its number. The rule "
         "applies only to a claim that was declined. It is read against the text of the letter on the file."),
    _cnd("CND-4", "sales", "A needs statement on the sales file", "for_reading",
         "The sales file holds a needs statement: the record of what the customer asked for and why the policy sold fits it. The "
         "rule is read against the file's own field for it."),
    _cnd("CND-5", "sales", "The cooling-off notice", "measured",
         f"The cooling-off notice is sent within {CND_COOLING_OFF_NOTICE_DAYS} days after the day the policy is issued. These are "
         f"calendar days. A notice sent on day {CND_COOLING_OFF_NOTICE_DAYS} meets the rule."),
    _cnd("CND-6", "policy", "The renewal notice", "measured",
         f"The renewal notice is sent at least {CND_RENEWAL_NOTICE_DAYS} days before the day the policy period ends. These are "
         f"calendar days. A notice sent exactly {CND_RENEWAL_NOTICE_DAYS} days before meets the rule."),
    _cnd("CND-7", "policy", "Confirming a mid-term change", "measured",
         f"A change the customer asks for during the policy period is confirmed in writing within {CND_CHANGE_WORKING_DAYS} working "
         "days after the day it is asked for."),
]}

CONDUCT_RULES_HOW_TO_READ = ("Each conduct rule is for one kind of file: claims, sales or policy. A rule of the kind measured turns "
                             "on dates: the system counts the days and gives the measured value beside the limit. A value exactly on "
                             "a limit meets the rule. Where a date the rule needs is not on the record, the rule cannot be told and a "
                             "person looks at the file: nothing is assumed. A rule of the kind for_reading is read against the file. "
                             "An audit record lists every rule checked for every file, the rules met as well.")


def build_audit(today: date) -> tuple[dict, dict]:
    L = lambda ago: long_date(d_ago(today, ago))
    D = lambda ago: today - timedelta(days=ago)
    files = {}

    def add(fid, kind, customer, product, facts, note=""):
        files[fid] = {"file_id": fid, "sample_id": "AUD-7200", "kind_of_file": kind, "kind_name": FILE_KINDS[kind],
                      "customer": customer, "product": product, "facts": facts, "note": note}

    def claim(reported_ago, ack_wd, pack_ago, decision_wd, decision, what, letter=None):
        reported, pack = D(reported_ago), D(pack_ago)
        decided = add_working_days(pack, decision_wd)
        return {"claim_is_for": what, "reported_on": reported.isoformat(),
                "acknowledged_on": add_working_days(reported, ack_wd).isoformat() if ack_wd is not None else None,
                "pack_complete_on": pack.isoformat(), "decision_on": decided.isoformat(), "decision": decision,
                "decline_letter": {"sent_on": decided.isoformat(), "text": letter(long_date(decided.isoformat()))} if letter else None}

    add("AF-7201", "claims", "Ottoline Brackenridge", "home",
        claim(52, 2, 48, 12, "accepted", "Storm damage to a garden wall and a fence."))
    add("AF-7202", "sales", "Jasper Windlesham", "private motor",
        {"sold_by": "telephone sales team", "needs_statement_on_file": "yes", "needs_statement_dated": d_ago(today, 44),
         "policy_issued_on": d_ago(today, 43), "cooling_off_notice_sent_on": d_ago(today, 41)})
    add("AF-7203", "claims", "Corisande Yarrow", "private motor",
        claim(49, 8, 43, 10, "accepted", "Damage to a parked car."))
    add("AF-7204", "sales", "Barnaby Thistlewood", "home",
        {"sold_by": "branch, Tallowby", "needs_statement_on_file": "no", "needs_statement_dated": None,
         "policy_issued_on": d_ago(today, 36), "cooling_off_notice_sent_on": d_ago(today, 31)},
        note="The sales file holds the proposal form and the payment record. No needs statement is on it.")
    add("AF-7205", "claims", "Evadne Larkhill", "home",
        claim(55, 1, 51, 15, "declined", "Theft of jewellery from the home.",
              letter=lambda on: f"THORNMERE MUTUAL INSURANCE\n{on}\nDear Ms Larkhill,\nYour claim for the theft of jewellery from "
                                "your home.\nWe are sorry to tell you that we cannot pay this claim. The police report says there was "
                                "no sign that anyone forced their way into or out of the home, and your policy does not cover a theft "
                                "in those circumstances.\nIf you think this decision is wrong, you can ask us to look at it again. "
                                "Write to our Complaints Team at Thornmere House, 1 Assurance Row, Port Ilvane, Meridia.\n"
                                "Claims Department"))
    add("AF-7206", "policy", "Mungo Pettifer", "private motor",
        {"period_ends_on": d_ago(today, 26), "renewal_notice_sent_on": d_ago(today, 54),
         "change_asked_for": "A change of address.", "change_asked_for_on": d_ago(today, 47), "change_confirmed_on": None},
        note=f"The file holds the customer's request of {L(47)} for a change of address and a confirmation letter that carries no "
             "date. The policy system shows the new address. The day the confirmation was sent is not recorded.")
    add("AF-7207", "claims", "Sidonie Marchmont", "home",
        claim(70, 5, 65, 20, "declined", "Escape of water in a home that was empty.",
              letter=lambda on: f"THORNMERE MUTUAL INSURANCE\n{on}\nDear Ms Marchmont,\nYour claim for water damage at your home.\n"
                                "We are sorry to tell you that we cannot pay this claim. When the pipe burst the home had been "
                                "unoccupied for 68 days in a row. Clause 2.2 of your policy wording (TMI-HOM-02) says that we do not "
                                "pay for loss or damage that happens after the home has been unoccupied for more than 60 days in a "
                                "row.\nIf you think this decision is wrong, you can ask us to look at it again. Write to our "
                                "Complaints Team at Thornmere House, 1 Assurance Row, Port Ilvane, Meridia.\nClaims Department"))
    add("AF-7208", "policy", "Lysander Crowhurst", "home",
        {"period_ends_on": d_ago(today, 29), "renewal_notice_sent_on": d_ago(today, 44),
         "change_asked_for": "A bicycle added to the listed items.", "change_asked_for_on": d_ago(today, 50),
         "change_confirmed_on": add_working_days(D(50), 4).isoformat()})

    samples = {"AUD-7200": {"sample_id": "AUD-7200", "status": "to_be_checked", "period_start": d_ago(today, 56),
                            "period_end": d_ago(today, 26), "drawn_on": d_ago(today, 2),
                            "drawn_by": "Seraphina Lockhart, compliance officer",
                            "what_it_is": "Eight files with a claim decision, a sale or a renewal in the period: four claims files, "
                                          "two sales files and two policy files. The sample holds a copy of the facts a check needs. "
                                          "These files are not in the policy or claims systems.",
                            "file_ids": sorted(files), "record_drafts": []}}
    return samples, files


def _measure_row(rule_id, result, measured, limit, unit, sentence, over_by=None):
    rule = CONDUCT_RULES[rule_id]
    return {"rule_id": rule_id, "heading": rule["heading"], "kind": rule["kind"], "result": result, "measured": measured,
            "limit": limit, "unit": unit, "over_or_short_by": over_by, "sentence": sentence}


def _missing(rule_id, limit, unit, what):
    return _measure_row(rule_id, "cannot_tell", None, limit, unit,
                        f"{what} is not on the record, so the rule cannot be measured. Nothing is assumed: a person looks at the file.")


def measure_audit_file(f: dict) -> dict:
    """One audit file against the conduct rules of its kind. The system counts every day."""
    x, rows = f["facts"], []
    day = lambda key: date.fromisoformat(x[key]) if x.get(key) else None
    LD = lambda key: long_date(x[key])
    if f["kind_of_file"] == "claims":
        a, b = day("reported_on"), day("acknowledged_on")
        if not a or not b:
            rows.append(_missing("CND-1", CND_ACK_WORKING_DAYS, "working days",
                                 "The day the claim was acknowledged" if a else "The day the claim was reported"))
        else:
            n = working_days_between(a, b)
            ok = n <= CND_ACK_WORKING_DAYS
            on = " That is exactly the limit, which meets the rule." if n == CND_ACK_WORKING_DAYS else ""
            rows.append(_measure_row("CND-1", "met" if ok else "not_met", n, CND_ACK_WORKING_DAYS, "working days",
                                     f"Reported on {LD('reported_on')}, acknowledged on {LD('acknowledged_on')}: "
                                     f"{plural(n, 'working day')}. The limit is {plural(CND_ACK_WORKING_DAYS, 'working day')}."
                                     + (on if ok else f" Over the limit by {plural(n - CND_ACK_WORKING_DAYS, 'working day')}."),
                                     None if ok else n - CND_ACK_WORKING_DAYS))
        a, b = day("pack_complete_on"), day("decision_on")
        if not a or not b:
            rows.append(_missing("CND-2", CND_DECISION_WORKING_DAYS, "working days",
                                 "The day of the decision" if a else "The day the pack was complete"))
        else:
            n = working_days_between(a, b)
            ok = n <= CND_DECISION_WORKING_DAYS
            on = " That is exactly the limit, which meets the rule." if n == CND_DECISION_WORKING_DAYS else ""
            rows.append(_measure_row("CND-2", "met" if ok else "not_met", n, CND_DECISION_WORKING_DAYS, "working days",
                                     f"Pack complete on {LD('pack_complete_on')}, decision on {LD('decision_on')}: "
                                     f"{plural(n, 'working day')}. The limit is {plural(CND_DECISION_WORKING_DAYS, 'working day')}."
                                     + (on if ok else f" Over the limit by {plural(n - CND_DECISION_WORKING_DAYS, 'working day')}."),
                                     None if ok else n - CND_DECISION_WORKING_DAYS))
        if x["decision"] == "declined":
            rows.append(_measure_row("CND-3", "for_reading", None, None, None,
                                     "The claim was declined. Not measured: read the text of the decline letter on the file for the "
                                     "number of a clause."))
        else:
            rows.append(_measure_row("CND-3", "not_applicable", None, None, None,
                                     f"The claim was {x['decision']}, not declined, so there is no decline letter and the rule does "
                                     "not apply to this file."))
        first, last = day("reported_on"), day("decision_on")
    elif f["kind_of_file"] == "sales":
        rows.append(_measure_row("CND-4", "for_reading", None, None, None,
                                 "Not measured: read the field needs_statement_on_file and the note on the file."))
        a, b = day("policy_issued_on"), day("cooling_off_notice_sent_on")
        if not a or not b:
            rows.append(_missing("CND-5", CND_COOLING_OFF_NOTICE_DAYS, "days",
                                 "The day the cooling-off notice was sent" if a else "The day the policy was issued"))
        else:
            n = (b - a).days
            ok = n <= CND_COOLING_OFF_NOTICE_DAYS
            rows.append(_measure_row("CND-5", "met" if ok else "not_met", n, CND_COOLING_OFF_NOTICE_DAYS, "days",
                                     f"Policy issued on {LD('policy_issued_on')}, cooling-off notice sent on "
                                     f"{LD('cooling_off_notice_sent_on')}: {plural(n, 'day')}. The limit is "
                                     f"{plural(CND_COOLING_OFF_NOTICE_DAYS, 'day')}."
                                     + ("" if ok else f" Over the limit by {plural(n - CND_COOLING_OFF_NOTICE_DAYS, 'day')}."),
                                     None if ok else n - CND_COOLING_OFF_NOTICE_DAYS))
        first, last = day("policy_issued_on"), day("cooling_off_notice_sent_on")
    else:
        a, b = day("renewal_notice_sent_on"), day("period_ends_on")
        if not a or not b:
            rows.append(_missing("CND-6", CND_RENEWAL_NOTICE_DAYS, "days before the period ends",
                                 "The day the period ends" if a else "The day the renewal notice was sent"))
        else:
            n = (b - a).days
            ok = n >= CND_RENEWAL_NOTICE_DAYS
            on = " That is exactly the least allowed, which meets the rule." if n == CND_RENEWAL_NOTICE_DAYS else ""
            rows.append(_measure_row("CND-6", "met" if ok else "not_met", n, CND_RENEWAL_NOTICE_DAYS, "days before the period ends",
                                     f"Renewal notice sent on {LD('renewal_notice_sent_on')}, period ends on {LD('period_ends_on')}: "
                                     f"{plural(n, 'day')} before the end. The rule asks for at least "
                                     f"{plural(CND_RENEWAL_NOTICE_DAYS, 'day')}."
                                     + (on if ok else f" Short by {plural(CND_RENEWAL_NOTICE_DAYS - n, 'day')}."),
                                     None if ok else CND_RENEWAL_NOTICE_DAYS - n))
        a, b = day("change_asked_for_on"), day("change_confirmed_on")
        if not a and not b:
            rows.append(_measure_row("CND-7", "not_applicable", None, CND_CHANGE_WORKING_DAYS, "working days",
                                     "No mid-term change was asked for on this file, so the rule does not apply."))
        elif not a or not b:
            rows.append(_missing("CND-7", CND_CHANGE_WORKING_DAYS, "working days",
                                 "The day the change was confirmed" if a else "The day the change was asked for"))
        else:
            n = working_days_between(a, b)
            ok = n <= CND_CHANGE_WORKING_DAYS
            rows.append(_measure_row("CND-7", "met" if ok else "not_met", n, CND_CHANGE_WORKING_DAYS, "working days",
                                     f"Change asked for on {LD('change_asked_for_on')}, confirmed on {LD('change_confirmed_on')}: "
                                     f"{plural(n, 'working day')}. The limit is {plural(CND_CHANGE_WORKING_DAYS, 'working day')}."
                                     + ("" if ok else f" Over the limit by {plural(n - CND_CHANGE_WORKING_DAYS, 'working day')}."),
                                     None if ok else n - CND_CHANGE_WORKING_DAYS))
        dates = [d for d in (day("renewal_notice_sent_on"), day("change_asked_for_on"), day("change_confirmed_on"),
                             day("period_ends_on")) if d]
        first, last = (min(dates), max(dates)) if dates else (None, None)
    pick = lambda result: [r["rule_id"] for r in rows if r["result"] == result]
    return {"file_id": f["file_id"], "kind_of_file": f["kind_of_file"], "rules": rows, "met": pick("met"), "not_met": pick("not_met"),
            "cannot_tell": pick("cannot_tell"), "for_reading": pick("for_reading"), "not_applicable": pick("not_applicable"),
            "public_holidays_in_the_period_of_the_file": holidays_between(first, last) if first and last else [],
            "what_this_is": "A measure of the file's dates against the dated conduct rules. It reads no letter and no note, and it "
                            "is not a finding: the compliance officer decides what is a breach."}


def rules_for_kind(kind: str) -> list[str]:
    return [r["rule_id"] for r in CONDUCT_RULES.values() if r["kind_of_file"] == kind]


# ---------------------------------------------------------------- regulators, publications and the obligations register

REGULATORS = [
    {"regulator_id": "MIA", "name": "Meridia Insurance Authority",
     "what_it_does": "Licenses and supervises insurers in Meridia. It publishes circulars, consultation papers and fee notices."},
    {"regulator_id": "MDPO", "name": "Meridia Data Protection Office",
     "what_it_does": "Supervises how personal data is kept and used in Meridia. It publishes guidance and notices."},
]

LINES_WRITTEN = ["private motor", "home", "commercial property", "motor fleet", "public liability", "group medical"]
LINES_NOTE = ("Thornmere Mutual Insurance writes these lines of business and no others. It writes no aviation, marine, life, crop or "
              "travel insurance.")


def _obl(oid, heading, text, source, role, name, lines="all lines written"):
    return {"obligation_id": oid, "heading": heading, "text": text, "source": source, "owner": {"role": role, "name": name},
            "lines_of_business": lines}


OBLIGATIONS = {o["obligation_id"]: o for o in [
    _obl("OBL-01", "Needs statement before a sale",
         "Before a policy is sold, the customer's needs are recorded in a needs statement and kept on the sales file.",
         "Conduct Rulebook of the Meridia Insurance Authority, rule 4.1", "Head of Distribution", "Tiberius Ockenden",
         "private motor, home"),
    _obl("OBL-02", "Cooling-off period",
         "A customer may cancel a home or private motor policy within 14 days of the day it is issued and get the premium back. The "
         "cooling-off notice is sent within 7 days of the day the policy is issued.",
         "Conduct Rulebook, rule 4.6", "Head of Distribution", "Tiberius Ockenden", "private motor, home"),
    _obl("OBL-03", "Claims: time limits",
         "A claim is acknowledged within 5 working days of the day it is reported. The decision is given within 20 working days of "
         "the day the last document asked for is received.",
         "Circular MIA-C-2026-09, paragraphs 2 and 3", "Head of Claims", "Araminta Feldspar"),
    _obl("OBL-04", "Claims: decline letters",
         "A letter that declines a claim names the clause of the wording relied on and tells the customer how to complain.",
         "Circular MIA-C-2026-09, paragraph 4", "Head of Claims", "Araminta Feldspar"),
    _obl("OBL-05", "Complaints: time limits",
         "A complaint is acknowledged within 3 working days of the day it is received. The final response is given within 30 days of "
         "the day it is received.",
         "Conduct Rulebook, rules 7.2 and 7.3", "Head of Complaints", "Winifred Stannard"),
    _obl("OBL-06", "Vulnerable customers",
         "A customer who may be vulnerable is marked on the customer care record, and that customer's claims and complaints are "
         "handled first.",
         "Conduct Rulebook, rule 2.4", "Customer Care Lead", "Odessa Merriweather"),
    _obl("OBL-07", "Renewal notice",
         "A renewal notice with the new premium is sent at least 21 days before the policy period ends.",
         "Conduct Rulebook, rule 5.2", "Head of Policy Servicing", "Horatio Quince"),
    _obl("OBL-08", "Group medical: pre-authorisation",
         "A request for pre-authorisation of treatment is answered within 5 working days of the day it is received.",
         "Circular MIA-C-2025-21, paragraph 2", "Head of Health Claims", "Cordelia Brightwater", "group medical"),
    _obl("OBL-09", "Personal data breach",
         "A breach of personal data that is likely to harm the people concerned is reported to the Meridia Data Protection Office "
         "within 72 hours of the hour it is found.",
         "Guidance MDPO-G-2026-04", "Data Protection Officer", "Ambrose Kettleby"),
    _obl("OBL-10", "Keeping records",
         "Policy, claims, sales and complaints files are kept for 7 years after the policy ends.",
         "Conduct Rulebook, rule 9.1", "Compliance Officer", "Seraphina Lockhart"),
    _obl("OBL-11", "Supervisory fee",
         "The annual supervisory fee is paid to the Meridia Insurance Authority by the date in the Authority's fee notice for the year.",
         "Licensing Regulations of the Meridia Insurance Authority, regulation 12", "Finance Director", "Gideon Farnsworth"),
    _obl("OBL-12", "Conduct return",
         "A conduct return with the numbers of claims, declined claims and complaints is sent to the Meridia Insurance Authority "
         "within 30 days of the end of each quarter.",
         "Conduct Rulebook, rule 10.3", "Compliance Officer", "Seraphina Lockhart"),
]}

OBLIGATIONS_HOW_TO_READ = ("The obligations register lists what the regulators ask of the insurer, one numbered obligation each, with "
                           "its source and the person who owns it. A publication bears on an obligation when it changes, sets or "
                           "restates what that obligation says. Where no obligation covers what a publication asks, the register is "
                           "silent: the compliance officer decides whether a new obligation is needed. Nothing here is advice on the law.")

OBLIGATION_STOP_WORDS = {"the", "and", "for", "with", "that", "this", "from", "are", "its", "our", "who", "what", "which", "does",
                         "have", "has", "any", "all", "each", "within", "must", "insurer", "insurers", "insurance", "meridia",
                         "authority", "rule", "rules", "circular", "obligation", "obligations", "register", "days", "day"}

BREACH_TEXT = ("1. This guidance applies to every organisation in Meridia that keeps personal data.\n"
               "2. A breach of personal data that is likely to harm the people concerned is reported to the Office within 72 hours of "
               "the hour it is found.\n"
               "3. The report says what happened, how many people are concerned and what has been done.\n"
               "4. The people concerned are told without delay.")


def build_publications(today: date) -> dict:
    A = lambda ahead: long_date(d_ahead(today, ahead))
    L = lambda ago: long_date(d_ago(today, ago))
    pubs = {}

    def add(pid, regulator, reference, kind, title, published_ago, text, *, status="new", effective=None, comments=None,
            payment=None, noted=None):
        pubs[pid] = {"publication_id": pid, "status": status, "regulator_id": regulator,
                     "regulator": next(r["name"] for r in REGULATORS if r["regulator_id"] == regulator), "reference": reference,
                     "kind": kind, "title": title, "published": d_ago(today, published_ago), "effective_from": effective,
                     "comments_close_on": comments, "payment_due_on": payment, "text": text, "noted_earlier": noted,
                     "impact_note_drafts": []}

    add("PUB-7291", "MIA", "MIA-C-2026-09", "circular", "Claims handling standards", 199,
        f"MERIDIA INSURANCE AUTHORITY\nCircular MIA-C-2026-09, published {L(199)}\nClaims handling standards\n"
        "1. This circular applies to every insurer licensed by the Authority, for all classes of business.\n"
        "2. An insurer acknowledges a claim within 5 working days of the day it is reported.\n"
        "3. An insurer gives its decision on a claim within 20 working days of the day the last document it asked for is received.\n"
        "4. A letter that declines a claim names the clause of the wording relied on and tells the customer how to complain.\n"
        f"5. This circular has effect from {L(140)}.",
        status="noted_earlier", effective=d_ago(today, 140),
        noted={"noted_on": d_ago(today, 189), "noted_by": "Seraphina Lockhart, compliance officer",
               "obligation_ids": ["OBL-03", "OBL-04"],
               "note": "Paragraphs 2 and 3 are OBL-03. Paragraph 4 is OBL-04."})
    add("PUB-7292", "MDPO", "MDPO-G-2026-04", "guidance", "Reporting a personal data breach", 150,
        f"MERIDIA DATA PROTECTION OFFICE\nGuidance MDPO-G-2026-04, published {L(150)}\nReporting a personal data breach\n" + BREACH_TEXT,
        status="noted_earlier", effective=d_ago(today, 120),
        noted={"noted_on": d_ago(today, 145), "noted_by": "Seraphina Lockhart, compliance officer", "obligation_ids": ["OBL-09"],
               "note": "Paragraph 2 is OBL-09."})

    add("PUB-7301", "MIA", "MIA-C-2026-14", "circular", "Complaints: time limit for the final response", 6,
        f"MERIDIA INSURANCE AUTHORITY\nCircular MIA-C-2026-14, published {L(6)}\nComplaints: time limit for the final response\n"
        "1. This circular applies to every insurer licensed by the Authority, for all classes of business.\n"
        f"2. From {A(36)} an insurer gives its final response to a complaint within 20 days of the day the complaint is received. "
        "Until then the limit stays at 30 days.\n"
        "3. The time limit for acknowledging a complaint does not change.\n"
        "4. Rule 7.3 of the Conduct Rulebook is amended to match.", effective=d_ahead(today, 36))
    add("PUB-7302", "MIA", "MIA-CP-2026-03", "consultation_paper", "Consultation: a longer cooling-off period for home and motor policies", 8,
        f"MERIDIA INSURANCE AUTHORITY\nConsultation paper MIA-CP-2026-03, published {L(8)}\n"
        "A longer cooling-off period for home and private motor policies\n"
        "1. The Authority proposes to lengthen the cooling-off period for home and private motor policies from 14 days to 21 days.\n"
        "2. This paper is a proposal. No rule changes until the Authority publishes a circular after the consultation.\n"
        f"3. Insurers and the public may send comments until {A(50)}.", comments=d_ahead(today, 50))
    add("PUB-7303", "MIA", "MIA-FN-2026-02", "fee_notice", "Supervisory fee for the coming year", 3,
        f"MERIDIA INSURANCE AUTHORITY\nFee notice MIA-FN-2026-02, published {L(3)}\nSupervisory fee\n"
        "1. Each insurer licensed by the Authority for general insurance pays a supervisory fee of USD 84,000.00 for the coming year.\n"
        f"2. The fee is due by {A(66)}.\n"
        "3. A fee paid late carries a charge set out in regulation 12 of the Licensing Regulations.", payment=d_ahead(today, 66))
    add("PUB-7304", "MIA", "MIA-C-2026-15", "circular", "Aviation hull and liability insurance: lowest policy limits", 7,
        f"MERIDIA INSURANCE AUTHORITY\nCircular MIA-C-2026-15, published {L(7)}\nAviation hull and liability insurance: lowest policy limits\n"
        "1. This circular applies only to insurers licensed for the aviation class.\n"
        f"2. From {A(96)} a policy of aviation liability insurance has a limit of at least USD 5,000,000.00 for any one event.\n"
        "3. Insurers that do not write aviation insurance need do nothing.", effective=d_ahead(today, 96))
    add("PUB-7305", "MIA", "MIA-C-2026-16", "circular", "Claims handling: amendment to Circular MIA-C-2026-09", 2,
        f"MERIDIA INSURANCE AUTHORITY\nCircular MIA-C-2026-16, published {L(2)}\nClaims handling: amendment to Circular MIA-C-2026-09\n"
        "1. This circular amends Circular MIA-C-2026-09 (Claims handling standards).\n"
        f"2. In paragraph 3 of that circular, 20 working days is replaced by 15 working days. From {A(36)} an insurer gives its "
        "decision on a claim within 15 working days of the day the last document it asked for is received.\n"
        "3. Paragraph 2 of that circular (acknowledgement within 5 working days) and paragraph 4 (decline letters) are unchanged.",
        effective=d_ahead(today, 36))
    add("PUB-7306", "MDPO", "MDPO-N-2026-19", "notice", "Reporting a personal data breach", 6,
        f"MERIDIA DATA PROTECTION OFFICE\nNotice MDPO-N-2026-19, published {L(6)}\nReporting a personal data breach\n"
        "This notice republishes Guidance MDPO-G-2026-04 under the Office's new way of numbering. The text is unchanged.\n" + BREACH_TEXT)
    add("PUB-7307", "MIA", "MIA-C-2026-17", "circular", "Automated tools in pricing and underwriting", 1,
        f"MERIDIA INSURANCE AUTHORITY\nCircular MIA-C-2026-17, published {L(1)}\nAutomated tools in pricing and underwriting\n"
        "1. This circular applies to every insurer licensed by the Authority that uses an automated tool to set a price or to accept "
        "or refuse a risk, for all classes of business.\n"
        f"2. From {A(126)} such an insurer keeps a list of those tools, tests each one once a year for unfair outcomes, and names a "
        "senior person who answers for them.\n"
        "3. The list and the results of the tests are shown to the Authority when it asks.", effective=d_ahead(today, 126))
    add("PUB-7308", "MIA", "MIA-C-2026-13", "circular", "Group medical insurance: time limit for pre-authorisation", 7,
        f"MERIDIA INSURANCE AUTHORITY\nCircular MIA-C-2026-13, published {L(7)}\nGroup medical insurance: time limit for pre-authorisation\n"
        "1. This circular applies to every insurer that writes group medical insurance.\n"
        f"2. From {A(67)} a request for pre-authorisation of treatment is answered within 2 working days of the day it is received. "
        "Until then the limit stays at 5 working days.\n"
        "3. Paragraph 2 of Circular MIA-C-2025-21 is amended to match.", effective=d_ahead(today, 67))
    return pubs


def publication_key_dates(pub: dict, today_iso: str) -> list[dict]:
    """The dates of a publication set against the insurer date. The system counts the days."""
    today, rows = date.fromisoformat(today_iso), []
    for key, what in (("published", "published"), ("effective_from", "has effect from"), ("comments_close_on", "comments close on"),
                      ("payment_due_on", "payment is due by")):
        if not pub.get(key):
            continue
        n = (date.fromisoformat(pub[key]) - today).days
        where = (f"{plural(n, 'day')} after {long_date(today_iso)}" if n > 0 else
                 (f"{plural(-n, 'day')} before {long_date(today_iso)}" if n < 0 else "the insurer date itself"))
        rows.append({"what": what, "date": pub[key], "days_from_the_insurer_date": n,
                     "sentence": f"{pub['reference']} {what} {long_date(pub[key])}: {where}."})
    return rows


# ---------------------------------------------------------------- disputed claims: documents and the privilege guide

DOCUMENT_CATEGORIES = {c["category_id"]: c for c in [
    {"category_id": "DC-1", "name": "Court documents and documents made for the proceedings",
     "text": "Claim forms, defences and witness statements, drafts of these, and letters before action."},
    {"category_id": "DC-2", "name": "Correspondence with the policyholder or the claimant",
     "text": "Claim forms and accident reports sent to the insurer, letters and emails to and from the policyholder or the claimant, "
             "decline letters and letters of complaint. A letter before action is DC-1."},
    {"category_id": "DC-3", "name": "Internal notes and internal emails",
     "text": "File notes, and emails between Thornmere staff about handling, reserves and payments. An internal note that passes on "
             "legal advice is DC-5."},
    {"category_id": "DC-4", "name": "Expert reports", "text": "Reports by engineers, surveyors and doctors."},
    {"category_id": "DC-5", "name": "Legal advice",
     "text": "A request for legal advice sent to Thornmere's lawyers, in-house or external, the advice they give, and an internal "
             "note that passes that advice on inside Thornmere."},
    {"category_id": "DC-6", "name": "Correspondence with third parties",
     "text": "Letters and emails to and from brokers, repairers, reinsurers and witnesses: anybody outside Thornmere who is not the "
             "policyholder, the claimant or a lawyer in the matter."},
    {"category_id": "DC-7", "name": "Policy documents", "text": "The schedule, the wording, endorsements and the proposal form."},
]}

DOCUMENT_CATEGORIES_HOW_TO_READ = ("A document goes in one category, by what the document itself is and who it is from and to, not by "
                                   "what it attaches or quotes. An email to a broker that quotes legal advice is correspondence with a "
                                   "third party. A copy of a document already in the set takes the category of the original, and the "
                                   "row names the original.")

PRIVILEGE_GUIDE = {r["rule_id"]: r for r in [
    {"rule_id": "PG-1", "flag": "yes", "heading": "Legal advice",
     "text": "A document in which Thornmere asks one of its lawyers, in-house or external, for legal advice, or in which the lawyer "
             "gives it, may be privileged. So may an internal note that passes that advice on inside Thornmere. Flag: yes."},
    {"rule_id": "PG-2", "flag": "yes", "heading": "Made for litigation",
     "text": "A document made mainly for court proceedings that have started or are expected may be privileged: a draft marked as "
             "prepared for litigation, a draft witness statement or defence, an expert report asked for by Thornmere's lawyers for "
             "the proceedings. Flag: yes."},
    {"rule_id": "PG-3", "flag": "no", "heading": "A lawyer is only copied",
     "text": "Copying a lawyer on an ordinary business email does not make it privileged. Where the document neither asks for nor "
             "gives legal advice, the flag is no, whoever is copied."},
    {"rule_id": "PG-4", "flag": "unclear", "heading": "Legal advice sent outside",
     "text": "Where legal advice has been sent, forwarded or quoted to anybody outside Thornmere other than its own lawyers, privilege "
             "may have been lost. The flag is unclear, for the lawyer. This rule comes before PG-1."},
    {"rule_id": "PG-5", "flag": "no", "heading": "Ordinary course of the claim",
     "text": "Documents made in the ordinary course of handling the claim are not privileged: letters to and from the policyholder, "
             "the claimant or their lawyers, file notes of the adjuster, a report by an engineer, surveyor or doctor asked for by "
             "the claims team to decide the claim, policy documents, and documents filed at court or served by the other side. "
             "Flag: no."},
    {"rule_id": "PG-6", "flag": "unclear", "heading": "The guide does not settle it",
     "text": "Where a document may record legal advice but does not say who gave it, or has no author or no date so that its purpose "
             "cannot be told, the flag is unclear, for the lawyer. Nothing is guessed."},
    {"rule_id": "PG-7", "flag": "as the original", "heading": "A copy",
     "text": "A copy of a document already in the set takes the same flag and the same rule as the original. The row names the original."},
]}

PRIVILEGE_HOW_TO_READ = ("The privilege guide is Thornmere's own guide for sorting documents. It does not decide whether a document is "
                         "privileged: the lawyers decide. A row of the schedule says only that a document may be privileged (yes), "
                         "does not appear to be (no), or cannot be told from the guide (unclear, for the lawyer), with the rule. "
                         "Apply PG-4 before PG-1. No row is a legal opinion.")

INSIDE = ("insurer", "insurer's lawyers")


def _person(name, role, organisation, side):
    return {"name": name, "role": role, "organisation": organisation, "side": side}


HOXTON = _person("Griselda Hoxton", "claims manager", "Thornmere Mutual Insurance", "insurer")
ACKERLEY = _person("Wilfred Ackerley", "loss adjuster", "Thornmere Mutual Insurance", "insurer")
ORLOP = _person("Matthias Orlop", "claims handler", "Thornmere Mutual Insurance", "insurer")
ROKE = _person("Clemency Roke", "claims handler", "Thornmere Mutual Insurance", "insurer")
FANE = _person("Osbert Fane", "finance officer", "Thornmere Mutual Insurance", "insurer")
THORNBURY = _person("Emeric Thornbury", "in-house counsel", "Thornmere Mutual Insurance", "insurer's lawyers")
PARGETER = _person("Lucasta Pargeter", "partner, external lawyer for Thornmere", "Pargeter Voss Legal", "insurer's lawyers")


def build_disputes(today: date) -> dict:
    L = lambda ago: long_date(d_ago(today, ago))
    out = {}

    def dispute(did, reference, title, line, policyholder, amount, stage, summary, people, docs):
        documents = []
        for n, (form, doc_title, ago, sender, to, cc, text) in enumerate(docs, start=1):
            documents.append({"document_id": f"{did}-D{n:02d}", "form": form, "title": doc_title,
                              "dated": d_ago(today, ago) if ago is not None else None, "author": sender, "to": to, "cc": cc,
                              "text": text})
        out[did] = {"dispute_id": did, "status": "documents_to_be_sorted", "claim_reference": reference, "title": title,
                    "line_of_business": line, "policyholder": policyholder, "amount_in_dispute": float(amount), "currency": "USD",
                    "stage": stage, "summary": summary, "people_in_the_matter": copy.deepcopy(people), "documents": documents,
                    "schedule_drafts": []}

    # ---- DSP-7401 a cold store roof, declined as gradual deterioration
    advice_7401 = ("ADVICE. Privileged and confidential.\nYou ask whether the decision to decline will stand. In my view the "
                   "engineer's finding of corrosion over several years supports the exclusion for gradual deterioration, but a court "
                   "may give weight to the storm on the night. I put the prospects of defending the claim at somewhat better than "
                   "even. I advise against any admission.")
    engineer_7401 = (f"CALDERBROOK STRUCTURAL ENGINEERS, report CSE-2291, {L(100)}\nRoof of the cold store at Unit 4, Frostgate "
                     f"Estate, Marlow Reach\nInstructed by Wilfred Ackerley of Thornmere Mutual Insurance on {L(112)} to help decide "
                     "the claim.\nFindings: the fixings of the roof sheets are corroded through along the north edge. The corrosion "
                     "is the work of several years. The sheets lifted in the wind because the fixings no longer held them.\n"
                     "Ignatius Calderbrook, engineer")
    dispute("DSP-7401", "DCL-7451", "Hollowmere Cold Stores Ltd and Thornmere Mutual Insurance", "commercial property",
            "Hollowmere Cold Stores Ltd", 186000,
            "A letter before action has been received. Court proceedings are expected.",
            f"Roof sheets of a cold store lifted in a storm on {L(121)}. The claim was declined on {L(90)} as gradual deterioration. "
            "The policyholder's lawyers say the storm was the cause.",
            [HOXTON, ACKERLEY, FANE, THORNBURY, PARGETER,
             _person("Ignatius Calderbrook", "engineer, asked by the claims team to report", "Calderbrook Structural Engineers", "expert"),
             _person("Barnabas Hollowmere", "director", "Hollowmere Cold Stores Ltd", "policyholder"),
             _person("Perpetua Quillon", "lawyer for the policyholder", "Quillon & Marsh Advocates", "policyholder's lawyers"),
             _person("Imelda Roe", "broker", "Quillfeather & Roe Insurance Brokers", "third party")],
            [("letter", "Notice of the loss", 120, "Barnabas Hollowmere", ["Thornmere Mutual Insurance, claims"], [],
              f"HOLLOWMERE COLD STORES LTD\n{L(120)}\nDear Sirs,\nIn the storm on the night of {L(121)} a large part of the roof of our "
              "cold store at Unit 4, Frostgate Estate was torn off. Stock was lost. Please treat this letter as notice of a claim "
              "under our policy.\nBarnabas Hollowmere, director"),
             ("file note", "Adjuster's note of the site visit", 113, "Wilfred Ackerley", [], [],
              f"FILE NOTE, DCL-7451, {L(113)}\nVisited the cold store. About a third of the roof sheets on the north side are gone. "
              "The fixings left in the purlins are heavily rusted. Asked the director when the roof was last inspected: he did not "
              "know. I will ask an engineer to report.\nW. Ackerley"),
             ("report", "Engineer's report", 100, "Ignatius Calderbrook", ["Wilfred Ackerley"], [], engineer_7401),
             ("letter", "Letter declining the claim", 90, "Griselda Hoxton", ["Barnabas Hollowmere"], [],
              f"THORNMERE MUTUAL INSURANCE\n{L(90)}\nDear Mr Hollowmere,\nClaim DCL-7451. We are sorry to tell you that we cannot pay "
              "this claim. Our engineer finds that the roof fixings had corroded over several years. Clause 2.1 of your policy "
              "wording excludes gradual deterioration.\nGriselda Hoxton, claims manager"),
             ("letter", "Letter before action", 40, "Perpetua Quillon", ["Thornmere Mutual Insurance"], [],
              f"QUILLON & MARSH ADVOCATES\n{L(40)}\nLetter before action\nWe act for Hollowmere Cold Stores Ltd. The roof was torn "
              "off by a storm, which the policy covers. Unless you agree within 28 days to pay USD 186,000.00 our client will start "
              "proceedings in the Marlow Reach County Court.\nPerpetua Quillon"),
             ("email", "Request for advice on the decline", 38, "Griselda Hoxton", ["Lucasta Pargeter"], ["Emeric Thornbury"],
              f"Sent {L(38)}\nLucasta, we have a letter before action on DCL-7451 (attached). Please advise whether our decision "
              "to decline under clause 2.1 will stand, and what our prospects are if they sue.\nGriselda"),
             ("note of advice", "Advice on the decline", 33, "Lucasta Pargeter", ["Griselda Hoxton", "Emeric Thornbury"], [],
              f"PARGETER VOSS LEGAL, {L(33)}\n" + advice_7401 + "\nLucasta Pargeter"),
             ("email", "Email to the broker with the lawyers' advice", 31, "Griselda Hoxton", ["Imelda Roe"], [],
              f"Sent {L(31)}\nImelda, for your information, this is what our lawyers said on {L(33)} about the Hollowmere claim:\n"
              + advice_7401 + "\nGriselda"),
             ("draft", "Draft witness statement of the adjuster", 12, "Lucasta Pargeter", ["Wilfred Ackerley"], [],
              f"DRAFT. Prepared for litigation. {L(12)}\nWitness statement of Wilfred Ackerley\n1. I am a loss adjuster employed by "
              f"Thornmere Mutual Insurance.\n2. I visited the cold store on {L(113)}. [WA to confirm what he saw of the fixings.]\n"
              "3. [To be completed.]"),
             ("report", "Engineer's report (copy from the broker's file)", 100, "Ignatius Calderbrook", ["Wilfred Ackerley"], [], engineer_7401),
             ("email", "Email to finance about the reserve", 36, "Griselda Hoxton", ["Osbert Fane"], ["Emeric Thornbury"],
              f"Sent {L(36)}\nOsbert, please raise the reserve on DCL-7451 to USD 186,000.00 from this month's accounts. The "
              "policyholder is asking for that sum. Emeric is copied so that he knows.\nGriselda")])

    # ---- DSP-7402 a road accident, proceedings issued
    claim_letter_7402 = (f"{L(160)}\nDear Sirs,\nOn {L(172)} your policyholder Alaric Penhale drove into the back of my car at the "
                         "junction of Ferry Road and Cable Street, Port Ilvane. My neck and shoulder were hurt and my car was badly "
                         "damaged. I hold him to blame and I claim for my injury and my losses.\nFerelith Dunmore")
    dispute("DSP-7402", "DCL-7452", "Ferelith Dunmore and Alaric Penhale (insured by Thornmere Mutual Insurance)", "private motor",
            "Alaric Penhale", 74500,
            f"Proceedings were issued in the Port Ilvane District Court on {L(44)}, case PIDC-2026-0871.",
            f"A collision at a junction in Port Ilvane on {L(172)}. The other driver claims for an injury to her neck and shoulder. "
            "Who was at fault is in dispute.",
            [HOXTON, ORLOP, ROKE, THORNBURY,
             _person("Alaric Penhale", "policyholder and driver", "", "policyholder"),
             _person("Ferelith Dunmore", "claimant, the other driver", "", "claimant"),
             _person("Dorothea Kite", "lawyer for the claimant", "Sorrel & Kite Advocates", "claimant's lawyers"),
             _person("Hesketh Vane", "doctor, asked by Thornmere's in-house counsel to report for the proceedings", "", "expert"),
             _person("Hobart Wynn", "witness", "", "third party"),
             _person("Tidewater Coachworks", "repairer of the policyholder's car", "Tidewater Coachworks", "third party")],
            [("letter", "Letter of claim from the other driver", 160, "Ferelith Dunmore", ["Thornmere Mutual Insurance, claims"], [],
              claim_letter_7402),
             ("form", "Accident report form", 170, "Alaric Penhale", ["Thornmere Mutual Insurance, claims"], [],
              f"ACCIDENT REPORT FORM\nPolicyholder: Alaric Penhale\nDate of the accident: {L(172)}\nWhat happened: the car in front "
              f"stopped suddenly at the junction with no brake lights showing. I could not stop in time.\nSigned: A. Penhale\nDated: {L(170)}"),
             ("file note", "Note of a call with the witness", 150, "Matthias Orlop", [], [],
              f"FILE NOTE, DCL-7452, {L(150)}\nTelephoned the witness, Hobart Wynn. He was at the bus stop. He says the front car "
              "braked hard for a dog. He did not notice its brake lights.\nM. Orlop"),
             ("court document", "Claim form", 44, "Dorothea Kite", ["Port Ilvane District Court"], [],
              f"PORT ILVANE DISTRICT COURT, case PIDC-2026-0871\nClaim form, issued {L(44)}\nClaimant: Ferelith Dunmore. Defendant: "
              "Alaric Penhale.\nThe claimant claims damages of USD 74,500.00 for personal injury and loss caused by the defendant's "
              "negligent driving.\nSorrel & Kite Advocates, for the claimant"),
             ("email", "In-house counsel on liability", 40, "Emeric Thornbury", ["Griselda Hoxton"], [],
              f"Sent {L(40)}\nGriselda, you asked for my view on liability in Dunmore. A driver who runs into the back of another "
              "starts at a disadvantage. The witness helps us on the sudden braking but not on the brake lights. My advice is to "
              "defend on contributory fault and not to deny liability outright.\nEmeric Thornbury, in-house counsel"),
             ("email", "Email passing on counsel's view", 39, "Matthias Orlop", ["Clemency Roke"], [],
              f"Sent {L(39)}\nClemency, for the file while I am away: Emeric's legal advice on Dunmore is that we defend on "
              "contributory fault and do not deny liability outright, because a driver who hits another from behind starts at a "
              "disadvantage.\nMatthias"),
             ("report", "Medical report on the claimant", 20, "Hesketh Vane", ["Emeric Thornbury"], [],
              f"MEDICAL REPORT, {L(20)}\nPrepared on the instructions of Emeric Thornbury, in-house counsel of Thornmere Mutual "
              "Insurance, for the proceedings PIDC-2026-0871.\nI examined Ferelith Dunmore. She has a soft tissue injury of the neck "
              "and the right shoulder. I expect a full recovery within 9 months of the accident.\nDr Hesketh Vane"),
             ("email", "Email to the repairer about an invoice", 140, "Matthias Orlop", ["Tidewater Coachworks"], ["Emeric Thornbury"],
              f"Sent {L(140)}\nDear Tidewater Coachworks, your invoice TC-5518 for the repair of Mr Penhale's car, USD 3,240.00, is "
              "approved and will be paid this month. Please send the car's inspection sheet when you can.\nMatthias Orlop, claims handler"),
             ("letter", "Letter of claim from the other driver (second scan)", 160, "Ferelith Dunmore",
              ["Thornmere Mutual Insurance, claims"], [], claim_letter_7402)])

    # ---- DSP-7403 subsidence at a home, declined as starting before the policy
    dispute("DSP-7403", "DCL-7453", "Thaddea Wolstencroft and Thornmere Mutual Insurance", "home", "Thaddea Wolstencroft", 58200,
            "The policyholder has complained and says she will go to court. Proceedings are expected.",
            f"Cracks in the rear wall of a house at 14 Kiln Lane, Tallowby. The claim was declined on {L(105)} because the surveyor "
            "found that the movement began before the policy started.",
            [HOXTON, ACKERLEY, PARGETER,
             _person("Thaddea Wolstencroft", "policyholder", "", "policyholder"),
             _person("Fennimore Drake", "surveyor, asked by the claims team to report", "Drake & Sallow Chartered Surveyors", "expert")],
            [("policy document", "Policy schedule", 400, "Thornmere Mutual Insurance, policy administration", ["Thaddea Wolstencroft"], [],
              f"THORNMERE MUTUAL INSURANCE\nHome policy schedule, issued {L(400)}\nPolicyholder: Thaddea Wolstencroft\nThe home: 14 "
              f"Kiln Lane, Tallowby, Meridia\nCover starts: {L(400)}\nBuildings sum insured: USD 260,000.00\nWording: TMI-HOM-02"),
             ("form", "Claim form", 140, "Thaddea Wolstencroft", ["Thornmere Mutual Insurance, claims"], [],
              f"CLAIM FORM\nPolicyholder: Thaddea Wolstencroft\nWhat happened: cracks have opened in the rear wall of the house and "
              f"the back door no longer shuts. I first saw them on {L(150)}.\nSigned: T. Wolstencroft\nDated: {L(140)}"),
             ("report", "Surveyor's report", 118, "Fennimore Drake", ["Wilfred Ackerley"], [],
              f"DRAKE & SALLOW CHARTERED SURVEYORS, report DS-0934, {L(118)}\n14 Kiln Lane, Tallowby\nInstructed by Wilfred Ackerley "
              "of Thornmere Mutual Insurance to help decide the claim.\nFindings: the rear wall has moved downwards at the corner. "
              "Old filler in the cracks and paint over it show that the movement began some years before, and before the cover "
              "started.\nFennimore Drake, surveyor"),
             ("letter", "Letter declining the claim", 105, "Griselda Hoxton", ["Thaddea Wolstencroft"], [],
              f"THORNMERE MUTUAL INSURANCE\n{L(105)}\nDear Ms Wolstencroft,\nClaim DCL-7453. We are sorry to tell you that we cannot "
              "pay this claim. Our surveyor finds that the movement of the wall began before your cover started. Clause 2.1 of your "
              "policy wording excludes gradual damage.\nGriselda Hoxton, claims manager"),
             ("letter", "Letter of complaint", 95, "Thaddea Wolstencroft", ["Thornmere Mutual Insurance"], [],
              f"{L(95)}\nDear Sirs,\nI do not accept your decision. There were no cracks when I bought the house. If you do not change "
              "your mind I will take you to court.\nThaddea Wolstencroft"),
             ("letter", "Advice from the external lawyers", 60, "Lucasta Pargeter", ["Griselda Hoxton"], [],
              f"PARGETER VOSS LEGAL, {L(60)}\nADVICE. Privileged and confidential.\nYou ask for our advice on the Wolstencroft claim. "
              "The surveyor's evidence on when the movement began is the heart of the case. It is arguable but it is not strong, "
              "because he cannot date the old filler. We advise that you get a second opinion before any proceedings.\nLucasta Pargeter"),
             ("note", "Note with no date and no name", None, None, [], [],
              "Spoke to L. about the start date point. View is: arguable but not strong. Think about an offer?"),
             ("draft", "Draft defence", 9, "Lucasta Pargeter", ["Griselda Hoxton"], [],
              f"DRAFT. Prepared for litigation. Not filed. {L(9)}\nDefence of Thornmere Mutual Insurance\n1. The defendant admits "
              "that it issued the policy.\n2. The defendant denies that the damage was caused by an insured event during the period "
              "of cover. [Second surveyor's report to be added.]")])
    return out


def document_facts(dispute: dict) -> list[dict]:
    """Each document with what the system can match: the recipients outside Thornmere and its lawyers, and any identical text."""
    side = {p["name"]: p["side"] for p in dispute["people_in_the_matter"]}
    first_with_text: dict = {}
    rows = []
    for doc in dispute["documents"]:
        outside = [n for n in doc["to"] + doc["cc"] if n in side and side[n] not in INSIDE]
        unknown = [n for n in doc["to"] + doc["cc"] if n not in side and not n.startswith("Thornmere Mutual Insurance")]
        original = first_with_text.setdefault(doc["text"], doc["document_id"])
        rows.append({**doc,
                     "author_role": next((f"{p['role']}{', ' + p['organisation'] if p['organisation'] else ''}"
                                          for p in dispute["people_in_the_matter"] if p["name"] == doc["author"]), None),
                     "recipients_outside_thornmere_and_its_lawyers": outside + unknown,
                     "identical_text_to": original if original != doc["document_id"] else None})
    return rows


def build_conduct(today: date) -> dict:
    samples, files = build_audit(today)
    return {
        "cd_complaint_categories": copy.deepcopy(COMPLAINT_CATEGORIES),
        "cd_complaint_rules": copy.deepcopy(COMPLAINT_RULES),
        "cd_customer_care": build_customer_care(today),
        "cd_complaints": build_complaints(today),
        "cd_conduct_rules": copy.deepcopy(CONDUCT_RULES),
        "cd_audit_samples": samples,
        "cd_audit_files": files,
        "cd_obligations": copy.deepcopy(OBLIGATIONS),
        "cd_publications": build_publications(today),
        "cd_document_categories": copy.deepcopy(DOCUMENT_CATEGORIES),
        "cd_privilege_guide": copy.deepcopy(PRIVILEGE_GUIDE),
        "cd_disputes": build_disputes(today),
    }
