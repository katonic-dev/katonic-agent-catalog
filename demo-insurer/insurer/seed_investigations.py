"""Seed data, part 4: closed claims for the leakage review with the handling standards, new claims for the fraud
check with the indicators, claims referred to the investigations desk, the parties on them, and public notices.

The sums are here as well: what should have been paid on a closed claim, every indicator with its measured value
and its threshold, the earlier claims of the parties, and the links between parties. The system calls them, so an
agent never adds up, counts or compares dates.

The policies and the claims handling guide of the policy and claims systems are read where a case uses them. They
are not copied. Policies that only this system needs are in a set of their own, so the policy system's list stays
as it was.
"""

from __future__ import annotations

import copy
from datetime import date, timedelta

from .seed_claims import CLAIM_TYPES
from .seed_health import money, plural, usd
from .seed_policy import _home, _motor, build_policies, cover_on, d_ago, long_date


# ---------------------------------------------------------------- the handling standards (leakage review)

STANDARDS_HOW_TO_APPLY = (
    "Every standard is tested on every closed claim. calculate_what_should_have_been_paid gives the result of each test "
    "with its figures: met, not_met or cannot_tell. A standard that cannot be tested because a document is not on the "
    "file is neither met nor broken: a person looks at the file. A finding says what the records show. It does not say "
    "who was at fault, it asks nobody for money back and it changes nothing on the claim.")

STANDARDS = {
    "LS-1": {"standard_id": "LS-1", "title": "The deductible is taken",
             "text": "The deductible is taken once from each claim before anything is paid: the deductible in the policy schedule "
                     "(clause 4.1 of either wording), or USD 500 for a home escape of water claim (clause 4.2 of the home wording). "
                     "The further deductible for a young driver (clause 4.2 of the motor wording) is outside this review."},
    "LS-2": {"standard_id": "LS-2", "title": "A line over its limit is paid at the limit",
             "text": "A line that the policy wording limits is paid at the limit and no higher. Motor wording TMI-MOT-01: windscreen "
                     "and glass USD 500 for any one claim (clause 3.2), personal belongings USD 300 (clause 3.3), hire car USD 40 a "
                     "day for up to 10 days (clause 3.4), the vehicle never more than the sum insured (clause 3.1). Home wording "
                     "TMI-HOM-02: USD 2,500 for any one item of contents that is not listed in the schedule (clause 3.2), trace and "
                     "access USD 1,500 (clause 3.4)."},
    "LS-3": {"standard_id": "LS-3", "title": "A payment above the handler's authority has a second approval",
             "text": "A claim on which more than USD 5,000 is paid in all needs the approval of a senior adjuster on the file, and a "
                     "claim on which more than USD 25,000 is paid needs the approval of the claims manager (rule HG-5 of the claims "
                     "handling guide). Above USD 5,000 the handler's own approval is not enough."},
    "LS-4": {"standard_id": "LS-4", "title": "A recovery is raised where another party is at fault",
             "text": "Where the file names another party as at fault for the loss, a recovery is raised with the recoveries team "
                     "before the claim is closed, and its reference is on the file (rule HG-7 of the claims handling guide)."},
    "LS-5": {"standard_id": "LS-5", "title": "An invoice is paid once",
             "text": "An invoice is paid once. Two payments to the same payee against the same invoice number are a duplicate."},
    "LS-6": {"standard_id": "LS-6", "title": "The policy was in force",
             "text": "Nothing is paid on a loss dated outside the policy period, or on or after the date a policy was cancelled."},
}

STATUS_WORDS = {"new": "waiting for the fraud check", "flagged": "referred to the investigations desk", "closed": "closed"}
RANK = {"handler": 0, "senior adjuster": 1, "claims manager": 2}


# ---------------------------------------------------------------- the fraud indicators

INDICATORS_HOW_TO_APPLY = (
    "Each indicator is a test with a figure. run_fraud_indicators measures every one on a claim and says whether it is "
    "met. An indicator that is met is a reason to pass the claim to the investigations desk. It is not a finding that "
    "the claim is false, and nobody is told that it is. A claim with no indicator met goes on with its handler. Two "
    "people are the same person only when the name and the date of birth are both the same.")

INDICATORS = {
    "FI-1": {"indicator_id": "FI-1", "name": "Early loss", "threshold": 30, "unit": "days",
             "test": "The date of the loss is 30 days or fewer after the start of the policy period."},
    "FI-2": {"indicator_id": "FI-2", "name": "Frequent claimant", "threshold": 3, "unit": "earlier claims",
             "test": "The claimant has 3 or more earlier claims with a date of loss in the 24 months before the date of this loss. "
                     "Only claims by the same person count: the same name and the same date of birth."},
    "FI-3": {"indicator_id": "FI-3", "name": "Same repairer", "threshold": 3, "unit": "claims",
             "test": "The repairer on this claim is on 3 or more claims by the same claimant, this claim included."},
    "FI-4": {"indicator_id": "FI-4", "name": "Shared bank account", "threshold": 1, "unit": "unrelated claimants",
             "test": "The bank account given for payment is also on a claim by 1 or more unrelated claimants. Unrelated means a "
                     "different person who is not recorded at the same address as the claimant."},
    "FI-5": {"indicator_id": "FI-5", "name": "Invoice dated before the loss", "threshold": 1, "unit": "days",
             "test": "A repair invoice or a repair estimate in the file is dated 1 day or more before the date of the loss."},
    "FI-6": {"indicator_id": "FI-6", "name": "Estimate close to the limit", "threshold": 95.0, "unit": "percent",
             "test": "The estimate is 95 percent or more of the sum insured that applies: the vehicle's sum insured for a motor "
                     "claim, the contents sum insured for a home theft claim, the buildings sum insured for any other home claim."},
}


# ---------------------------------------------------------------- policies that only this system needs

def build_investigation_policies(today: date) -> dict:
    rows = [
        # Leakage review.
        _motor("POL-2701", "Fenwick Aldergrove", "6 Tidewater Lane, Port Ilvane, Meridia", "Orrin Bay 2.0 estate, 2023", "PI-6120-A", 21000, 350, 200),
        _home("POL-2702", "Ignatius Corbrook", "15 Saddlers Court, Marlow Reach, Meridia", 270000, 36000, 250, 180),
        _motor("POL-2703", "Sunniva Marchbank", "22 Lantern Hill, Tallowby, Meridia", "Halden Crest 1.6 saloon, 2022", "TB-3307-L", 14000, 300, 250),
        # New claims for the fraud check.
        _motor("POL-2711", "Perpetua Hollowell", "3 Gullwing Terrace, Tallowby, Meridia", "Tarn Vale 1.4 hatchback, 2021", "TB-1184-G", 13000, 300, 300),
        _motor("POL-2712", "Lorcan Whitmarsh", "18 Ferry Road, Port Ilvane, Meridia", "Vesper Lane 1.6 saloon, 2020", "PI-7302-W", 12000, 300, 41),
        _motor("POL-2713", "Benedikt Farrowdale", "9 Cinder Path, Marlow Reach, Meridia", "Halden Crest 2.0 estate, 2022", "MR-5519-F", 16000, 350, 20),
        _home("POL-2714", "Clementine Durrow", "41 Orchard Rise, Tallowby, Meridia", 280000, 35000, 250, 320),
        _motor("POL-2715", "Rafferty Coombe", "2 Netmakers Row, Port Ilvane, Meridia", "Orrin Bay 1.6 saloon, 2021", "PI-4460-R", 14500, 300, 205),
        _home("POL-2716", "Marguerite Ashdown", "5 Swallowfield, Tallowby, Meridia", 300000, 40000, 250, 265),
        _motor("POL-2717", "Thaddeus Wren", "30 Quayside Steps, Port Ilvane, Meridia", "Vesper Lane 2.0 estate, 2024", "PI-8077-T", 18000, 400, 14),
        _motor("POL-2718", "Gideon Marlowe", "12 Hazel Bank, Marlow Reach, Meridia", "Tarn Vale 1.6 saloon, 2023", "MR-2291-G", 15500, 300, 150),
        # Claims referred to the investigations desk.
        _motor("POL-2721", "Osric Fenn", "8 Tannery Close, Port Ilvane, Meridia", "Orrin Bay 1.6 saloon, 2020", "PI-3345-O", 14000, 300, 30),
        _motor("POL-2722", "Dagny Rookhope", "53 Milldam Street, Marlow Reach, Meridia", "Halden Crest 1.8 hatchback, 2021", "MR-9016-D", 15000, 300, 220),
        _motor("POL-2723", "Ulric Staveley", "19 Barley Mow Lane, Tallowby, Meridia", "Vesper Lane 1.4 hatchback, 2022", "TB-6621-U", 17000, 350, 31),
        _motor("POL-2724", "Evander Pryce", "4 Rope Walk, Port Ilvane, Meridia", "Tarn Vale 1.2 hatchback, 2019", "PI-1408-E", 12500, 300, 280),
        _motor("POL-2725", "Leofric Tansley", "27 Mariners Row, Port Ilvane, Meridia", "Orrin Bay 1.6 saloon, 2019", "PI-5593-L", 13000, 300, 25),
        _motor("POL-2726", "Wilhelmina Orrell", "11 Foxglove Court, Tallowby, Meridia", "Halden Crest 1.6 saloon, 2023", "TB-7740-W", 16500, 300, 190),
        _motor("POL-2727", "Cuthbert Lyle", "36 Lower Wharf, Port Ilvane, Meridia", "Vesper Lane 1.4 hatchback, 2018", "PI-2256-C", 11000, 300, 140),
    ]
    policies = {}
    for row in rows:
        start = today - timedelta(days=row.pop("_start_ago"))
        end = start + timedelta(days=row.pop("_term")) - timedelta(days=1)
        row["period_start"], row["period_end"] = start.isoformat(), end.isoformat()
        row["cancelled_on"] = None
        row["currency"] = "USD"
        policies[row["policy_id"]] = row
    return policies


# ---------------------------------------------------------------- closed claims for the leakage review

def _closed(claim_id, policy_id, claimant, claim_type, today, loss_ago, reported_ago, closed_ago, description, *, invoices, allowed,
            deductible_taken, approved_by, payments, second_approval=None, other_party=None, recovery=None, notes=()):
    """One closed claim with its payment file. invoices: (supplier, number, dated_ago, [(description, category, amount, qty, unit)])."""
    rows, n = [], 0
    for supplier, number, dated_ago, lines in invoices:
        inv = {"supplier": supplier, "invoice_number": number, "dated": d_ago(today, dated_ago), "lines": []}
        for line in lines:
            n += 1
            item = {"line_id": f"{claim_id}-L{n}", "description": line[0], "category": line[1], "amount": float(line[2])}
            if len(line) > 3:
                item["quantity"], item["unit_amount"] = line[3], float(line[4])
            inv["lines"].append(item)
        inv["total"] = money(sum(x["amount"] for x in inv["lines"]))
        rows.append(inv)
    line_ids = [x["line_id"] for inv in rows for x in inv["lines"]]
    pays = [{"payment_id": f"{claim_id}-P{i}", "paid_on": d_ago(today, ago), "payee": payee, "invoice_number": number, "amount": float(amount)}
            for i, (ago, payee, number, amount) in enumerate(payments, start=1)]
    if second_approval:
        second_approval = {"name": second_approval[0], "role": second_approval[1], "approved_on": d_ago(today, second_approval[2])}
    if recovery:
        recovery = {"raised": True, "reference": recovery[0], "raised_on": d_ago(today, recovery[1])}
    elif other_party:
        recovery = {"raised": False, "reference": None, "raised_on": None}
    return {"claim_id": claim_id, "policy_id": policy_id, "claimant": claimant, "claim_type": claim_type,
            "claim_type_label": CLAIM_TYPES[claim_type], "status": "closed", "loss_date": d_ago(today, loss_ago),
            "reported_date": d_ago(today, reported_ago), "closed_on": d_ago(today, closed_ago), "currency": "USD", "description": description,
            "other_party_at_fault": other_party,
            "payment_file": {
                "invoices": rows,
                "settlement_record": {"lines_allowed": [{"line_id": i, "amount_allowed": float(a)} for i, a in zip(line_ids, allowed)],
                                      "deductible_taken": float(deductible_taken),
                                      "approved_by": {"name": approved_by[0], "role": approved_by[1]},
                                      "second_approval": second_approval},
                "payments": pays, "total_paid": money(sum(p["amount"] for p in pays)), "recovery": recovery,
                "file_notes": list(notes)},
            "leakage_finding_drafts": []}


def build_leakage_claims(today: date) -> dict:
    L = lambda ago: long_date(d_ago(today, ago))
    handler, second_handler = ("Ottilie Marsh", "handler"), ("Lucan Thirlby", "handler")
    rows = [
        # Paid correctly. The windscreen line is over its limit and was paid at the limit: LS-2 must not fire.
        _closed("CLM-6101", "POL-2011", "Isaura Venn", "motor_own_damage", today, 40, 39, 21,
                "A branch fell on the parked vehicle in a storm. The rear bumper, a light cluster and the rear windscreen were damaged.",
                invoices=[("Candlewick Coachworks", "CC-3117", 30, [("Rear bumper and light cluster", "repair", 1480),
                                                                    ("Rear windscreen replacement", "windscreen", 610)])],
                allowed=[1480, 500], deductible_taken=300, approved_by=handler,
                payments=[(22, "Candlewick Coachworks", "CC-3117", 1680)]),
        # Paid correctly. Above the handler's authority with a senior adjuster's approval on file, and the recovery is raised.
        _closed("CLM-6102", "POL-2701", "Fenwick Aldergrove", "motor_third_party", today, 55, 54, 18,
                "A van ran into the back of the insured vehicle while it stood at a junction. The rear of the vehicle was rebuilt.",
                invoices=[("Tidewater Accident Repair", "TAR-0871", 33, [("Rear panel, boot floor and bumper", "repair", 6900)]),
                          ("Ilvane Car Hire", "ICH-2256", 31, [("Hire car, 8 days at 38.00 a day", "hire_car", 304, 8, 38)])],
                allowed=[6900, 304], deductible_taken=350, approved_by=second_handler,
                second_approval=("Fenella Arkwright", "senior adjuster", 20),
                other_party={"name": "Hollis Drummock", "at_fault_per_the_file": True,
                             "source": f"The other driver's insurer admitted fault in its letter of {L(45)}."},
                recovery=("REC-0412", 19),
                payments=[(19, "Tidewater Accident Repair", "TAR-0871", 6550), (19, "Ilvane Car Hire", "ICH-2256", 304)]),
        # The deductible of 250.00 was not taken.
        _closed("CLM-6103", "POL-2001", "Corwin Ashgrove", "motor_own_damage", today, 48, 47, 25,
                "The insured vehicle scraped a wall in a car park. The left front door and wing were repaired.",
                invoices=[("Gatewick Body Repairs", "GBR-2240", 34, [("Left front door and wing, repair and paint", "repair", 1940)])],
                allowed=[1940], deductible_taken=0, approved_by=handler,
                payments=[(26, "Gatewick Body Repairs", "GBR-2240", 1940)]),
        # A bracelet that is not listed in the schedule was paid at 3,400.00, over the single item limit of 2,500.00.
        _closed("CLM-6104", "POL-2002", "Elspeth Marrowdene", "home_theft", today, 44, 43, 14,
                "A window was forced and a bracelet and a television were taken.",
                invoices=[("Tallowby Jewellers", "TJ-5520", 28, [("Gold bracelet, replacement", "contents_item", 3400)]),
                          ("Marlow Electrical Stores", "MES-1904", 27, [("Television, replacement", "contents_item", 900)])],
                allowed=[3400, 900], deductible_taken=300, approved_by=second_handler,
                payments=[(15, "Elspeth Marrowdene", "TJ-5520 and MES-1904", 4000)]),
        # The joinery invoice was paid twice.
        _closed("CLM-6105", "POL-2702", "Ignatius Corbrook", "home_fire", today, 52, 51, 8,
                "A pan fire damaged the kitchen units and the wiring behind them.",
                invoices=[("Marlow Reach Joinery", "MRJ-0448", 36, [("Kitchen units, supplied and fitted", "repair", 2300)]),
                          ("Saddlers Electrical", "SE-7713", 35, [("Rewiring behind the kitchen units", "repair", 640)])],
                allowed=[2300, 640], deductible_taken=250, approved_by=handler,
                payments=[(27, "Marlow Reach Joinery", "MRJ-0448", 2050), (27, "Saddlers Electrical", "SE-7713", 640),
                          (18, "Marlow Reach Joinery", "MRJ-0448", 2050)]),
        # 6,850.00 paid on the handler's approval alone.
        _closed("CLM-6106", "POL-2014", "Ansel Whitlocke", "motor_own_damage", today, 37, 36, 11,
                "The insured vehicle left a wet road and struck a tree. The front of the vehicle was rebuilt.",
                invoices=[("Beacon Hill Motor Engineers", "BHM-6031", 20, [("Front panel, radiator, bonnet and both wings", "repair", 7150)])],
                allowed=[7150], deductible_taken=300, approved_by=handler,
                payments=[(12, "Beacon Hill Motor Engineers", "BHM-6031", 6850)]),
        # Another driver admitted fault and no recovery was raised.
        _closed("CLM-6107", "POL-2703", "Sunniva Marchbank", "motor_third_party", today, 42, 41, 16,
                "Another car reversed into the insured vehicle while it was parked. The right rear door and wing were repaired.",
                invoices=[("Lantern Hill Garage", "LHG-4472", 29, [("Right rear door and wing, repair and paint", "repair", 2860)])],
                allowed=[2860], deductible_taken=300, approved_by=second_handler,
                other_party={"name": "Edric Vollenhoe", "at_fault_per_the_file": True,
                             "source": f"The other driver's signed statement of {L(41)} says he reversed into the parked vehicle."},
                payments=[(17, "Lantern Hill Garage", "LHG-4472", 2560)]),
        # The record is incomplete: one payment has no invoice on the file.
        _closed("CLM-6108", "POL-2012", "Elric Stannaway", "home_escape_of_water", today, 50, 49, 6,
                "A waste pipe under the bath failed. The ceiling below was dried out and redecorated.",
                invoices=[("Otterburn Plumbing", "OP-3381", 38, [("Repair of the waste pipe under the bath", "repair", 780)])],
                allowed=[780], deductible_taken=500, approved_by=handler,
                payments=[(20, "Otterburn Plumbing", "OP-3381", 280), (7, "Dunmere Drying and Decorating", "DDD-2291", 1930)],
                notes=[f"File note of {L(7)}: invoice DDD-2291 was sent to the handler by post. It has not been scanned to the file."]),
    ]
    return {r["claim_id"]: r for r in rows}


def _limit(line: dict, policy: dict) -> tuple[float | None, str | None, str]:
    """The limit of the wording on one invoice line: the amount, the clause and a sentence. None when no limit applies."""
    sched, cat, amount = policy["schedule"], line["category"], line["amount"]
    if policy["product"] == "private_motor":
        if cat == "windscreen":
            return 500.0, "3.2", "Windscreen and glass: USD 500.00 for any one claim (motor clause 3.2)."
        if cat == "personal_belongings":
            return 300.0, "3.3", "Personal belongings: USD 300.00 for any one claim (motor clause 3.3)."
        if cat == "hire_car":
            days, rate = min(line.get("quantity", 1), 10), min(line.get("unit_amount", amount), 40.0)
            return money(days * rate), "3.4", (f"Hire car: USD 40.00 a day for up to 10 days (motor clause 3.4); "
                                               f"{days} days at {usd(rate)} a day is {usd(money(days * rate))}.")
        if cat == "vehicle":
            return sched["sum_insured"], "3.1", f"The vehicle: never more than the sum insured of {usd(sched['sum_insured'])} (motor clause 3.1)."
    else:
        listed = {str(item).lower() for item in sched.get("listed_items", [])}
        if cat == "trace_and_access":
            return 1500.0, "3.4", "Trace and access: USD 1,500.00 for any one claim (home clause 3.4)."
        if cat == "contents_item" and line["description"].lower() not in listed:
            return 2500.0, "3.2", "An item of contents not listed in the schedule: USD 2,500.00 for any one item (home clause 3.2)."
    return None, None, "No limit of the wording applies to this line."


def leakage_check(claim: dict, policy: dict, guide: dict) -> dict:
    """A closed claim set against the handling standards: what should have been paid, what was paid, and each standard's result."""
    pf, cid = claim["payment_file"], claim["claim_id"]
    record = pf["settlement_record"]
    on_file = {inv["invoice_number"] for inv in pf["invoices"]}
    allowed_by_handler = {row["line_id"]: row["amount_allowed"] for row in record["lines_allowed"]}

    def covered(number):  # a payment may name one invoice, or two joined by "and"
        return all(part.strip() in on_file for part in number.split(" and "))

    missing = [p for p in pf["payments"] if not covered(p["invoice_number"])]
    complete = not missing
    what_is_missing = [f"Invoice {p['invoice_number']} from {p['payee']}: payment {p['payment_id']} of {usd(p['amount'])} was made against "
                       "it and the invoice is not on the file." for p in missing]

    # lines against the limits (LS-2)
    lines = []
    for inv in pf["invoices"]:
        for line in inv["lines"]:
            limit, clause, sentence = _limit(line, policy)
            under = line["amount"] if limit is None else min(line["amount"], limit)
            on_the_file = allowed_by_handler.get(line["line_id"], line["amount"])
            lines.append({"line_id": line["line_id"], "invoice_number": inv["invoice_number"], "supplier": inv["supplier"],
                          "description": line["description"], "category": line["category"], "amount_invoiced": line["amount"],
                          "limit": limit, "limit_clause": clause, "limit_sentence": sentence,
                          "amount_under_the_standards": money(under), "amount_allowed_on_the_file": on_the_file,
                          "allowed_over_the_limit": money(max(0.0, on_the_file - under))})
    over_lines = [x for x in lines if x["allowed_over_the_limit"] > 0]
    total_under = money(sum(x["amount_under_the_standards"] for x in lines))

    # the deductible (LS-1)
    if claim["claim_type"] == "home_escape_of_water":
        due, ded_clause = 500.0, "4.2"
    else:
        due, ded_clause = policy["schedule"]["deductible"], "4.1"
    taken = record["deductible_taken"]
    short = money(max(0.0, due - taken))

    # payments (LS-5)
    paid = pf["total_paid"]
    seen, duplicates = {}, []
    for p in pf["payments"]:
        key = (p["payee"], p["invoice_number"])
        if key in seen:
            duplicates.append({"payment_id": p["payment_id"], "repeats_payment_id": seen[key]["payment_id"], "payee": p["payee"],
                               "invoice_number": p["invoice_number"], "amount": p["amount"], "paid_on": p["paid_on"],
                               "first_paid_on": seen[key]["paid_on"]})
        else:
            seen[key] = p
    duplicate_total = money(sum(x["amount"] for x in duplicates))

    should = money(max(0.0, total_under - due)) if complete else None
    difference = money(paid - should) if complete else None

    # authority (LS-3)
    needed = next(level["approver"] for level in guide["settlement_authority"]["levels"] if level["up_to"] is None or paid <= level["up_to"])
    approvals = [record["approved_by"]] + ([record["second_approval"]] if record["second_approval"] else [])
    has_authority = any(RANK.get(a["role"], 0) >= RANK[needed] for a in approvals)
    approvals = [{"role": a["role"]} for a in approvals]  # the role only: a finding names no person
    approval_words = " and ".join(f"a {a['role']}" for a in approvals)

    # recovery (LS-4) and cover (LS-6)
    other, recovery = claim["other_party_at_fault"], pf["recovery"]
    cover = cover_on(policy, claim["loss_date"])

    def row(sid, result, measured, amount=None):
        return {"standard_id": sid, "title": STANDARDS[sid]["title"], "result": result, "measured": measured, "amount": amount}

    rows = [row("LS-1", "met" if short == 0 else "not_met",
                f"The deductible due is {usd(due)} (clause {ded_clause}). The settlement record shows {usd(taken)} taken."
                + (f" {usd(short)} was not taken." if short else ""), short if short else None)]
    if not complete:
        rows.append(row("LS-2", "cannot_tell", "The lines of an invoice that was paid are not on the file, so they cannot be set "
                                               "against the limits. " + " ".join(what_is_missing)))
    elif over_lines:
        rows.append(row("LS-2", "not_met", " ".join(
            f"{x['line_id']} {x['description']}: {usd(x['amount_allowed_on_the_file'])} was allowed on the file where the limit is "
            f"{usd(x['limit'])} (clause {x['limit_clause']}); {usd(x['allowed_over_the_limit'])} over." for x in over_lines),
            money(sum(x["allowed_over_the_limit"] for x in over_lines))))
    else:
        limited = [x for x in lines if x["limit"] is not None and x["amount_invoiced"] > x["limit"]]
        rows.append(row("LS-2", "met", " ".join(
            f"{x['line_id']} {x['description']}: invoiced at {usd(x['amount_invoiced'])}, limit {usd(x['limit'])} (clause "
            f"{x['limit_clause']}), allowed on the file at {usd(x['amount_allowed_on_the_file'])}." for x in limited)
            or "No line was allowed above a limit of the wording."))
    rows.append(row("LS-3", "met" if has_authority else "not_met",
                    f"{usd(paid)} was paid in all. That needs the approval of the {needed} (rule HG-5). Approval on the file: "
                    f"{approval_words}." + ("" if has_authority else f" No approval by a {needed} is on the file.")))
    if not other:
        rows.append(row("LS-4", "met", "The file names no other party as at fault, so no recovery is called for."))
    elif recovery and recovery["raised"]:
        rows.append(row("LS-4", "met", f"The file names {other['name']} as at fault. Recovery {recovery['reference']} was raised on "
                                       f"{long_date(recovery['raised_on'])}."))
    else:
        rows.append(row("LS-4", "not_met", f"The file names {other['name']} as at fault. {other['source']} No recovery is raised on "
                                           f"the file. {usd(paid)} was paid on the claim.", None))
    rows.append(row("LS-5", "met" if not duplicates else "not_met",
                    " ".join(f"{x['payment_id']} of {usd(x['amount'])} to {x['payee']} on {long_date(x['paid_on'])} is against invoice "
                             f"{x['invoice_number']}, which {x['repeats_payment_id']} had paid on {long_date(x['first_paid_on'])}."
                             for x in duplicates) or "No invoice was paid more than once.", duplicate_total if duplicates else None))
    rows.append(row("LS-6", "met" if cover["in_force"] else "not_met", cover["reason"]))

    not_met = [r["standard_id"] for r in rows if r["result"] == "not_met"]
    cannot = [r["standard_id"] for r in rows if r["result"] == "cannot_tell"]
    if cannot:
        outcome = "cannot_tell_needs_a_person"
        sentence = (f"The record of {cid} is incomplete, so what should have been paid cannot be worked out. A person looks at the "
                    "file. " + " ".join(what_is_missing))
    elif not_met:
        outcome = "paid_outside_the_standards"
        sentence = (f"{cid} was paid outside the handling standards: {', '.join(not_met)} not met. {usd(should)} should have been "
                    f"paid and {usd(paid)} was paid, a difference of {usd(difference)}.")
    else:
        outcome = "paid_within_the_standards"
        sentence = f"{cid} was paid within the handling standards: {usd(should)} should have been paid and {usd(paid)} was paid."
    plus = " + ".join(f"{x['amount_under_the_standards']:,.2f}" for x in lines) or "0.00"
    if complete:
        working = [f"Lines under the standards: {plus} = {total_under:,.2f}",
                   f"Less the deductible due under clause {ded_clause}: {total_under:,.2f} - {due:,.2f} = {should:,.2f}",
                   "Paid: " + " + ".join(f"{p['amount']:,.2f}" for p in pf["payments"]) + f" = {paid:,.2f}",
                   f"Difference: {paid:,.2f} - {should:,.2f} = {difference:,.2f}"]
    else:
        working = ["Paid: " + " + ".join(f"{p['amount']:,.2f}" for p in pf["payments"]) + f" = {paid:,.2f}",
                   "What should have been paid is not worked out: " + " ".join(what_is_missing)]
    return {"claim_id": cid, "currency": "USD", "can_be_worked_out": complete, "what_is_missing": what_is_missing, "lines": lines,
            "total_of_the_lines_under_the_standards": total_under if complete else None,
            "deductible": {"due": due, "clause": ded_clause, "taken": taken, "not_taken": short},
            "should_have_been_paid": should, "amount_paid": paid, "difference": difference,
            "payments_that_repeat_an_invoice": duplicates,
            "authority": {"amount_paid": paid, "approval_needed_from": needed, "approvals_on_the_file": approvals,
                          "approval_with_the_authority_is_on_the_file": has_authority},
            "standards": rows, "standards_not_met": not_met, "standards_that_cannot_be_told": cannot,
            "outcome": outcome, "outcome_sentence": sentence, "working": working}


# ---------------------------------------------------------------- parties

def _person(party_id, name, born, phone_tail, address, account=None):
    return {"party_id": party_id, "kind": "person", "name": name, "date_of_birth": born, "phone": f"+999 555 {phone_tail}",
            "address": f"{address}, Meridia", "bank_account": account or f"DEMO-ACCT-{party_id[4:]}"}


def _firm(party_id, name, phone_tail, address):
    return {"party_id": party_id, "kind": "firm", "name": name, "date_of_birth": None, "phone": f"+999 555 {phone_tail}",
            "address": f"{address}, Meridia", "bank_account": None}


def build_parties() -> dict:
    rows = [
        _person("PTY-3001", "Perpetua Hollowell", "1988-04-09", "0101", "3 Gullwing Terrace, Tallowby"),
        _person("PTY-3002", "Lorcan Whitmarsh", "1979-11-23", "0102", "18 Ferry Road, Port Ilvane"),
        # Lives at the same address as PTY-3002 and uses the same bank account: not an unrelated claimant.
        _person("PTY-3003", "Niamh Whitmarsh", "1981-03-15", "0103", "18 Ferry Road, Port Ilvane", "DEMO-ACCT-3002"),
        _person("PTY-3004", "Benedikt Farrowdale", "1992-08-30", "0104", "9 Cinder Path, Marlow Reach"),
        _person("PTY-3005", "Clementine Durrow", "1970-01-17", "0105", "41 Orchard Rise, Tallowby"),
        # Two unrelated people with one bank account.
        _person("PTY-3006", "Rafferty Coombe", "1986-12-05", "0106", "2 Netmakers Row, Port Ilvane", "DEMO-ACCT-7741"),
        _person("PTY-3007", "Isolde Penhallow", "1990-05-21", "0107", "77 Limekiln Lane, Marlow Reach", "DEMO-ACCT-7741"),
        _person("PTY-3008", "Marguerite Ashdown", "1983-09-12", "0108", "5 Swallowfield, Tallowby"),
        _person("PTY-3009", "Thaddeus Wren", "1995-02-27", "0109", "30 Quayside Steps, Port Ilvane"),
        # Two people with one name and different dates of birth.
        _person("PTY-3010", "Gideon Marlowe", "1985-06-02", "0110", "12 Hazel Bank, Marlow Reach"),
        _person("PTY-3011", "Gideon Marlowe", "1961-10-19", "0111", "64 Coopers Field, Tallowby"),
        # Three claimants who gave one phone number.
        _person("PTY-3021", "Osric Fenn", "1987-03-11", "0142", "8 Tannery Close, Port Ilvane"),
        _person("PTY-3022", "Dagny Rookhope", "1991-07-25", "0142", "53 Milldam Street, Marlow Reach"),
        _person("PTY-3023", "Ulric Staveley", "1984-10-02", "0142", "19 Barley Mow Lane, Tallowby"),
        _person("PTY-3024", "Evander Pryce", "1979-03-12", "0124", "4 Rope Walk, Port Ilvane"),
        _person("PTY-3025", "Leofric Tansley", "1991-07-14", "0125", "27 Mariners Row, Port Ilvane"),
        _person("PTY-3026", "Wilhelmina Orrell", "1976-06-08", "0126", "11 Foxglove Court, Tallowby"),
        _person("PTY-3027", "Cuthbert Lyle", "1982-01-30", "0127", "36 Lower Wharf, Port Ilvane"),
        # A witness on two claims by claimants who share nothing else.
        _person("PTY-3028", "Hester Quarmby", "1968-11-04", "0128", "90 Chandlers Hill, Marlow Reach"),
        _person("PTY-3029", "Ambrose Tidewell", "1973-04-18", "0129", "14 Rushmere Way, Tallowby"),
        _firm("PTY-3501", "Brackenfold Motor Works", "0190", "Unit 4, Saltpan Yard, Port Ilvane"),
        _firm("PTY-3502", "Tallowby Panel and Paint", "0191", "2 Kiln Lane, Tallowby"),
        _firm("PTY-3503", "Ferry Road Motors", "0192", "60 Ferry Road, Port Ilvane"),
        _firm("PTY-3504", "Hazel Bank Autos", "0193", "1 Hazel Bank, Marlow Reach"),
        _firm("PTY-3505", "Netmakers Garage", "0194", "31 Netmakers Row, Port Ilvane"),
        _firm("PTY-3506", "Quayside Accident Repair", "0195", "Quay Shed 7, Port Ilvane"),
        _firm("PTY-3507", "Rope Walk Motors", "0196", "40 Rope Walk, Port Ilvane"),
        _firm("PTY-3508", "Mariners Body Shop", "0197", "3 Mariners Row, Port Ilvane"),
        _firm("PTY-3509", "Foxglove Garage Services", "0198", "Foxglove Lane, Tallowby"),
        _firm("PTY-3510", "Lower Wharf Coachworks", "0199", "Arch 12, Lower Wharf, Port Ilvane"),
        _firm("PTY-3511", "Rushmere Motor Repairs", "0180", "8 Rushmere Way, Tallowby"),
        _firm("PTY-3512", "Limekiln Autos", "0181", "5 Limekiln Lane, Marlow Reach"),
        _firm("PTY-3513", "Harbour Bodyworks", "0182", "Harbour Road, Port Ilvane"),
    ]
    return {r["party_id"]: r for r in rows}


# ---------------------------------------------------------------- claims this system holds for checking

def _claim(claim_id, policy_id, claimant_id, claim_type, status, today, loss_ago, reported_ago, parties, *, what, place="",
           estimate=None, repairer=None, witness=None, work="", doc_ago=None, doc_type="repair_estimate", doc_number="",
           closed_ago=None, paid=None, policy_note="", issuer=None):
    me = parties[claimant_id]
    loss, reported = d_ago(today, loss_ago), d_ago(today, reported_ago)
    on_claim = [{"party_id": claimant_id, "name": me["name"], "role": "claimant"}]
    if witness:
        on_claim.append({"party_id": witness, "name": parties[witness]["name"], "role": "witness"})
    if repairer:
        on_claim.append({"party_id": repairer, "name": parties[repairer]["name"], "role": "repairer"})
    docs = []
    if status != "closed":
        n = claim_id[4:]
        docs.append({"document_id": f"DOC-{n}-1", "doc_type": "claim_form", "title": "Claim form", "dated": reported,
                     "text": f"CLAIM FORM\nPolicyholder: {me['name']}\nDate of birth: {long_date(me['date_of_birth'])}\n"
                             f"Date of loss: {long_date(loss)}\nPlace: {place}\nWhat happened: {what}\n"
                             + (f"Witness: {parties[witness]['name']}\n" if witness else "")
                             + f"Contact number: {me['phone']}\nPayment to account: {me['bank_account']}\n"
                               f"Signed: {me['name']}\nDated: {long_date(reported)}"})
        if doc_ago is not None:
            dated = d_ago(today, doc_ago)
            title = {"repair_estimate": "Repair estimate", "repair_invoice": "Repair invoice", "valuation": "Valuation"}[doc_type]
            issuer = issuer or (parties[repairer]["name"] if repairer else "Meridia Motor Valuers")
            docs.append({"document_id": f"DOC-{n}-2", "doc_type": doc_type, "title": f"{title}, {issuer}", "dated": dated,
                         "text": f"{issuer.upper()}, {title.lower()} {doc_number}\nDated: {long_date(dated)}\n{work}: "
                                 f"{estimate:,.2f}\nTotal {estimate:,.2f} USD"})
    return {"claim_id": claim_id, "policy_id": policy_id, "policy_note": policy_note, "claimant_party_id": claimant_id,
            "claimant": me["name"], "claim_type": claim_type, "claim_type_label": CLAIM_TYPES[claim_type], "status": status,
            "loss_date": loss, "reported_date": reported, "closed_on": d_ago(today, closed_ago) if closed_ago is not None else None,
            "estimate": float(estimate) if estimate is not None else None, "amount_paid": float(paid) if paid is not None else None,
            "currency": "USD", "description": what, "parties": on_claim, "repairer_party_id": repairer,
            "bank_account_for_payment": me["bank_account"], "documents": docs, "referral": None,
            "fraud_referral_drafts": [], "case_file_drafts": []}


EARLIER = "An earlier policy of the same holder, now ended. It is not held in this system."


def build_investigation_claims(today: date, parties: dict, policies: dict) -> dict:
    def old(claim_id, claimant, claim_type, loss_ago, paid, what, old_policy, **kw):
        return _claim(claim_id, old_policy, claimant, claim_type, "closed", today, loss_ago, loss_ago - 2, parties, what=what,
                      closed_ago=loss_ago - 30, paid=paid, policy_note="" if old_policy in policies else EARLIER, **kw)

    def new(claim_id, policy_id, claimant, claim_type, loss_ago, reported_ago, status="new", **kw):
        return _claim(claim_id, policy_id, claimant, claim_type, status, today, loss_ago, reported_ago, parties, **kw)

    rows = [
        # ---- earlier claims, closed
        old("CLM-6011", "PTY-3002", "motor_own_damage", 400, 1200, "The vehicle was scratched along one side in a car park.", "POL-2612",
            repairer="PTY-3513"),
        old("CLM-6012", "PTY-3002", "motor_own_damage", 150, 2050, "The vehicle struck a kerb and a wheel and wing were damaged.", "POL-2612",
            repairer="PTY-3503"),
        old("CLM-6013", "PTY-3003", "motor_own_damage", 500, 900, "A door mirror and a door were damaged while the vehicle was parked.", "POL-2613"),
        old("CLM-6014", "PTY-3005", "home_escape_of_water", 900, 1850, "A washing machine hose failed and the kitchen floor was damaged.", "POL-2614"),
        old("CLM-6015", "PTY-3005", "home_theft", 650, 2400, "A shed was broken into and garden tools were taken.", "POL-2614"),
        old("CLM-6016", "PTY-3005", "home_escape_of_water", 420, 3100, "A radiator valve failed and a bedroom carpet was damaged.", "POL-2614"),
        old("CLM-6017", "PTY-3005", "home_theft", 170, 1600, "A bicycle was taken from a locked garage.", "POL-2714"),
        old("CLM-6021", "PTY-3007", "motor_own_damage", 210, 3300, "The vehicle hit a gate post and the front bumper and a wing were damaged.",
            "POL-2621", repairer="PTY-3512"),
        old("CLM-6022", "PTY-3011", "motor_own_damage", 600, 1450, "The vehicle was damaged by a falling roof tile.", "POL-2622"),
        old("CLM-6023", "PTY-3011", "motor_own_damage", 380, 2200, "The vehicle slid on ice into a wall.", "POL-2622"),
        old("CLM-6024", "PTY-3011", "motor_own_damage", 120, 1750, "The vehicle was scraped by a passing lorry that did not stop.", "POL-2622"),
        old("CLM-6031", "PTY-3029", "motor_own_damage", 260, 4100, "The vehicle left the road on a bend and struck a hedge bank.", "POL-2631",
            repairer="PTY-3511", witness="PTY-3028"),
        old("CLM-6041", "PTY-3024", "motor_own_damage", 480, 1300, "The vehicle was damaged by a shopping trolley in a car park.", "POL-2641",
            repairer="PTY-3507"),

        # ---- new claims, waiting for the fraud check
        # Clean.
        new("CLM-6201", "POL-2711", "PTY-3001", "motor_own_damage", 6, 5, estimate=1820, repairer="PTY-3502", doc_ago=4, doc_number="TPP-4410",
            place="Kiln Lane, Tallowby", what="I misjudged a gateway and dented the left rear door and wing.",
            work="Left rear door and wing, repair and paint"),
        # Clean, though it looks odd: every indicator is below its threshold.
        new("CLM-6202", "POL-2712", "PTY-3002", "motor_own_damage", 7, 6, estimate=10920, repairer="PTY-3503", doc_ago=7, doc_number="FRM-0933",
            place="Ferry Road, Port Ilvane", what="The car left the road in heavy rain and went into a ditch. The front and the underside are badly damaged.",
            work="Front end, subframe and underside, repair"),
        # Early loss.
        new("CLM-6203", "POL-2713", "PTY-3004", "motor_theft", 8, 8, estimate=9600, doc_ago=5, doc_type="valuation", doc_number="MMV-6120",
            place="Cinder Path, Marlow Reach", what="The car was taken overnight from outside my home. I have both keys.",
            work="Market value of the insured vehicle at the date of the loss"),
        # Frequent claimant.
        new("CLM-6204", "POL-2714", "PTY-3005", "home_escape_of_water", 9, 8, estimate=3360, doc_ago=6, doc_number="ORF-2207", issuer="Orchard Rise Flooring",
            place="41 Orchard Rise, Tallowby", what="A pipe joint under the kitchen sink failed and the kitchen floor is damaged.",
            work="Lift and relay the kitchen floor"),
        # The bank account is also on a claim by an unrelated claimant.
        new("CLM-6205", "POL-2715", "PTY-3006", "motor_own_damage", 5, 4, estimate=2900, repairer="PTY-3505", doc_ago=3, doc_number="NG-1178",
            place="Netmakers Row, Port Ilvane", what="I reversed into a bollard. The rear bumper and the tailgate are dented.",
            work="Rear bumper and tailgate, repair and paint"),
        # The repair invoice is dated before the loss.
        new("CLM-6206", "POL-2716", "PTY-3008", "home_escape_of_water", 10, 9, estimate=4200, doc_ago=16, doc_type="repair_invoice", doc_number="SWF-0561", issuer="Swallowfield Flooring",
            place="5 Swallowfield, Tallowby", what="A pipe behind the dishwasher failed and the kitchen and hall floors are damaged.",
            work="Kitchen and hall floors, lifted and relaid"),
        # Two indicators: an early loss and an estimate close to the sum insured.
        new("CLM-6207", "POL-2717", "PTY-3009", "motor_own_damage", 5, 4, estimate=17640, repairer="PTY-3506", doc_ago=3, doc_number="QAR-3302",
            place="Quayside Steps, Port Ilvane", what="The car rolled down the slipway into the harbour at high water. It was under water for some hours.",
            work="Engine, electrics and interior, replacement after immersion"),
        # The claimant has the name of an earlier claimant and another date of birth.
        new("CLM-6208", "POL-2718", "PTY-3010", "motor_own_damage", 4, 3, estimate=2480, repairer="PTY-3504", doc_ago=2, doc_number="HBA-7719",
            place="Hazel Bank, Marlow Reach", what="A deer ran into the side of the car. The right front door and wing are dented.",
            work="Right front door and wing, repair and paint"),

        # ---- claims referred to the investigations desk
        # Three claims with one repairer, by three claimants who gave one phone number.
        new("CLM-6301", "POL-2721", "PTY-3021", "motor_own_damage", 12, 11, "flagged", estimate=5200, repairer="PTY-3501", doc_ago=10, doc_number="BMW-0611",
            place="Tannery Close, Port Ilvane", what="I hit a low wall while turning. The front bumper, a wing and a headlamp are damaged.",
            work="Front bumper, left wing and headlamp, repair"),
        new("CLM-6302", "POL-2722", "PTY-3022", "motor_own_damage", 15, 14, "flagged", estimate=14400, repairer="PTY-3501", doc_ago=12, doc_number="BMW-0604",
            place="Milldam Street, Marlow Reach", what="The car slid on wet leaves into a stone gatepost. The front of the car is crushed.",
            work="Front end and chassis legs, repair"),
        new("CLM-6303", "POL-2723", "PTY-3023", "motor_own_damage", 9, 8, "flagged", estimate=6800, repairer="PTY-3501", doc_ago=7, doc_number="BMW-0618",
            place="Barley Mow Lane, Tallowby", what="I reversed into a parked trailer. The rear of the car is badly dented.",
            work="Rear panel, bumper and tailgate, repair"),
        # A public notice names the claimant, with the same date of birth and address.
        new("CLM-6304", "POL-2724", "PTY-3024", "motor_own_damage", 11, 10, "flagged", estimate=12125, repairer="PTY-3507", doc_ago=9, doc_number="RWM-2054",
            place="Rope Walk, Port Ilvane", what="The car caught fire while parked. The engine bay and the dashboard are burnt out.",
            work="Engine bay, wiring and dashboard, replacement"),
        # A public notice names another person with the claimant's name.
        new("CLM-6305", "POL-2725", "PTY-3025", "motor_own_damage", 6, 5, "flagged", estimate=3900, repairer="PTY-3508", doc_ago=4, doc_number="MBS-1490",
            place="Mariners Row, Port Ilvane", what="I clipped a parked skip. The left side of the car is scraped and a door is dented.",
            work="Left side doors and sill, repair and paint"),
        # No links at all.
        new("CLM-6306", "POL-2726", "PTY-3026", "motor_own_damage", 8, 7, "flagged", estimate=2640, repairer="PTY-3509", doc_ago=10, doc_number="FGS-0882",
            place="Foxglove Court, Tallowby", what="A gate swung shut on the car in the wind. The right rear wing and the bumper are dented.",
            work="Right rear wing and bumper, repair and paint"),
        # The only link runs through the witness, who is also the witness on an earlier claim by another claimant.
        new("CLM-6307", "POL-2727", "PTY-3027", "motor_own_damage", 13, 12, "flagged", estimate=10560, repairer="PTY-3510", witness="PTY-3028",
            doc_ago=11, doc_number="LWC-3316", place="Chandlers Hill, Marlow Reach",
            what="The car left the road on a bend and rolled onto its side. A passer-by saw it happen.",
            work="Roof, right side and suspension, repair"),
    ]
    claims = {r["claim_id"]: r for r in rows}
    for claim in claims.values():
        if claim["status"] == "flagged":
            met = run_indicators(claim, policies[claim["policy_id"]], claims, parties)["indicators_met"]
            day = (date.fromisoformat(claim["reported_date"]) + timedelta(days=1)).isoformat()
            claim["referral"] = {"referred_by": "Lucan Thirlby, claims handler", "referred_on": day, "indicators_met": met,
                                 "note": "Passed to the investigations desk for a case file. Payment is on hold until the "
                                         "investigator has read it."}
    return claims


# ---------------------------------------------------------------- earlier claims, indicators and links

def is_person(party: dict) -> bool:
    return party["kind"] == "person"


def role_on(claim: dict, party_id: str) -> str | None:
    return next((p["role"] for p in claim["parties"] if p["party_id"] == party_id), None)


def months_before(day: date, months: int) -> date:
    year, month = day.year, day.month - months
    while month <= 0:
        year, month = year - 1, month + 12
    for d in (day.day, 30, 29, 28):
        try:
            return date(year, month, d)
        except ValueError:
            continue
    return date(year, month, 28)


def claim_row(other: dict, party_id: str, parties: dict, this_loss: str | None = None) -> dict:
    """One claim as a row of a party's history."""
    row = {"claim_id": other["claim_id"], "role_of_the_party": role_on(other, party_id), "claimant_party_id": other["claimant_party_id"],
           "claimant": other["claimant"], "claim_type": other["claim_type"], "claim_type_label": other["claim_type_label"],
           "status": other["status"], "status_in_words": STATUS_WORDS[other["status"]], "loss_date": other["loss_date"],
           "amount_paid": other["amount_paid"], "estimate": other["estimate"],
           "repairer": parties[other["repairer_party_id"]]["name"] if other["repairer_party_id"] else None,
           "repairer_party_id": other["repairer_party_id"], "bank_account_for_payment": other["bank_account_for_payment"],
           "description": other["description"]}
    if this_loss:
        row["days_before_this_loss"] = (date.fromisoformat(this_loss) - date.fromisoformat(other["loss_date"])).days
    return row


def earlier_claims(claim: dict, claims: dict, parties: dict) -> dict:
    """The earlier claims of every party on a claim, and people who only share a name with a party."""
    loss = date.fromisoformat(claim["loss_date"])
    since = months_before(loss, 24)
    out = []
    for on in claim["parties"]:
        party = parties[on["party_id"]]
        rows = sorted((claim_row(c, party["party_id"], parties, claim["loss_date"]) for c in claims.values()
                       if c["claim_id"] != claim["claim_id"] and role_on(c, party["party_id"]) and c["loss_date"] < claim["loss_date"]),
                      key=lambda r: r["loss_date"])
        for r in rows:
            r["loss_in_the_24_months_before_this_loss"] = date.fromisoformat(r["loss_date"]) >= since
        entry = {"party_id": party["party_id"], "name": party["name"], "kind": party["kind"], "role_on_this_claim": on["role"],
                 "date_of_birth": party["date_of_birth"], "earlier_claims": rows, "earlier_claim_count": len(rows)}
        if on["role"] == "claimant":
            mine = [r for r in rows if r["role_of_the_party"] == "claimant"]
            recent = [r for r in mine if r["loss_in_the_24_months_before_this_loss"]]
            entry["earlier_claims_as_claimant"] = len(mine)
            entry["earlier_claims_as_claimant_in_the_24_months_before_this_loss"] = len(recent)
            entry["sentence"] = (f"{party['name']} ({party['party_id']}), born {long_date(party['date_of_birth'])}, has "
                                 f"{plural(len(mine), 'earlier claim')} as claimant. {len(recent)} of them "
                                 f"{'has' if len(recent) == 1 else 'have'} a date of loss in the 24 months before {long_date(claim['loss_date'])}, "
                                 f"that is on or after {long_date(since.isoformat())}.")
        else:
            entry["sentence"] = (f"{party['name']} ({party['party_id']}) is on {plural(len(rows), 'earlier claim')} the insurer holds."
                                 if rows else f"{party['name']} ({party['party_id']}) is on no earlier claim the insurer holds.")
        out.append(entry)
    me = parties[claim["claimant_party_id"]]
    namesakes = []
    for other in parties.values():
        if other["party_id"] != me["party_id"] and is_person(other) and other["name"].lower() == me["name"].lower():
            theirs = sorted(c["claim_id"] for c in claims.values() if role_on(c, other["party_id"]))
            namesakes.append({"party_id": other["party_id"], "name": other["name"], "date_of_birth": other["date_of_birth"],
                              "address": other["address"], "claims": theirs, "the_same_person": False, "counted": False,
                              "sentence": f"{other['party_id']} is also named {other['name']}, but was born on "
                                          f"{long_date(other['date_of_birth'])} and the claimant was born on "
                                          f"{long_date(me['date_of_birth'])}. The dates of birth differ, so this is another person. "
                                          f"That person's {plural(len(theirs), 'claim')} ({', '.join(theirs) or 'none'}) "
                                          f"{'is' if len(theirs) == 1 else 'are'} not the claimant's and {'is' if len(theirs) == 1 else 'are'} "
                                          "not counted."})
    return {"claim_id": claim["claim_id"], "loss_date": claim["loss_date"], "the_24_months_start_on": since.isoformat(),
            "parties": out, "other_people_with_the_claimants_name": namesakes,
            "other_people_note": ("" if namesakes else "No other person on the insurer's records has the claimant's name.")}


def limit_that_applies(claim: dict, policy: dict) -> tuple[float, str]:
    sched = policy["schedule"]
    if policy["product"] == "private_motor":
        return sched["sum_insured"], "the sum insured for the vehicle"
    if claim["claim_type"] == "home_theft":
        return sched["contents_sum_insured"], "the sum insured for contents"
    return sched["buildings_sum_insured"], "the sum insured for buildings"


def run_indicators(claim: dict, policy: dict, claims: dict, parties: dict) -> dict:
    """Every indicator measured on one claim: the figure, the threshold and whether it is met. The system counts."""
    loss = date.fromisoformat(claim["loss_date"])
    me = parties[claim["claimant_party_id"]]
    others = [c for c in claims.values() if c["claim_id"] != claim["claim_id"]]
    rows = []

    def add(fid, measured, met, sentence):
        ind = INDICATORS[fid]
        rows.append({"indicator_id": fid, "name": ind["name"], "test": ind["test"], "measured": measured, "threshold": ind["threshold"],
                     "unit": ind["unit"], "met": met, "sentence": sentence})

    # FI-1
    days = (loss - date.fromisoformat(policy["period_start"])).days
    met = 0 <= days <= 30
    add("FI-1", days, met, f"The policy period started on {long_date(policy['period_start'])} and the loss was on "
                           f"{long_date(claim['loss_date'])}, {plural(days, 'day')} after the start. The threshold is 30 days or fewer: "
                           f"{'met' if met else 'not met'}.")
    # FI-2
    since = months_before(loss, 24)
    mine = [c for c in others if c["claimant_party_id"] == me["party_id"] and since <= date.fromisoformat(c["loss_date"]) < loss]
    ids = sorted(c["claim_id"] for c in mine)
    namesakes = [p for p in parties.values() if p["party_id"] != me["party_id"] and is_person(p) and p["name"].lower() == me["name"].lower()]
    extra = "".join(f" {p['party_id']} has the same name and another date of birth ({long_date(p['date_of_birth'])}): another person, "
                    "whose claims are not counted." for p in namesakes)
    met = len(mine) >= 3
    add("FI-2", len(mine), met, f"The claimant, {me['name']} born {long_date(me['date_of_birth'])}, has {plural(len(mine), 'earlier claim')} "
                                f"with a date of loss on or after {long_date(since.isoformat())}, the 24 months before this loss"
                                + (f" ({', '.join(ids)})" if ids else "") + f". The threshold is 3 or more: {'met' if met else 'not met'}.{extra}")
    # FI-3
    repairer = claim["repairer_party_id"]
    if repairer:
        same = sorted(c["claim_id"] for c in others if c["claimant_party_id"] == me["party_id"] and c["repairer_party_id"] == repairer)
        count = len(same) + 1
        met = count >= 3
        add("FI-3", count, met, f"{parties[repairer]['name']} is the repairer on {plural(count, 'claim')} by the claimant, this claim "
                                f"included" + (f" (also {', '.join(same)})" if same else "") + f". The threshold is 3 or more: "
                                f"{'met' if met else 'not met'}.")
    else:
        add("FI-3", 0, False, "No repairer is named on this claim. The threshold is 3 or more claims: not met.")
    # FI-4
    account = claim["bank_account_for_payment"]
    shared = [c for c in others if c["bank_account_for_payment"] == account and c["claimant_party_id"] != me["party_id"]]
    unrelated, same_address = {}, {}
    for c in shared:
        other = parties[c["claimant_party_id"]]
        (same_address if other["address"] == me["address"] else unrelated).setdefault(other["party_id"], []).append(c["claim_id"])
    met = len(unrelated) >= 1
    words = f"The bank account given for payment, {account}, is on a claim by {plural(len(unrelated), 'unrelated claimant')}"
    if unrelated:
        words += " (" + "; ".join(f"{parties[p]['name']}, {p}, of {parties[p]['address']}, on {', '.join(sorted(c))}" for p, c in unrelated.items()) + ")"
    words += f". The threshold is 1 or more: {'met' if met else 'not met'}."
    for p, c in same_address.items():
        words += (f" The account is also on {', '.join(sorted(c))} by {parties[p]['name']} ({p}), who is recorded at the claimant's own "
                  "address and so is not unrelated: not counted.")
    add("FI-4", len(unrelated), met, words)
    # FI-5
    before = [(d["document_id"], (loss - date.fromisoformat(d["dated"])).days, d) for d in claim["documents"]
              if d["doc_type"] in ("repair_invoice", "repair_estimate")]
    worst = max(before, key=lambda x: x[1], default=None)
    if worst is None:
        add("FI-5", 0, False, "The file holds no repair invoice and no repair estimate. The threshold is 1 day or more before the loss: not met.")
    else:
        did, gap, doc = worst
        measured = max(0, gap)
        met = measured >= 1
        where = (f"{plural(gap, 'day')} before the loss" if gap > 0 else "the day of the loss" if gap == 0 else f"{plural(-gap, 'day')} after the loss")
        add("FI-5", measured, met, f"{doc['title']} ({did}) is dated {long_date(doc['dated'])} and the loss was on "
                                   f"{long_date(claim['loss_date'])}: {where}. The threshold is 1 day or more before the loss: "
                                   f"{'met' if met else 'not met'}.")
    # FI-6
    limit, name = limit_that_applies(claim, policy)
    percent = round(claim["estimate"] * 100 / limit + 1e-9, 1) if claim["estimate"] is not None else 0.0
    met = percent >= 95.0
    add("FI-6", percent, met, (f"The estimate is {usd(claim['estimate'])} and {name} is {usd(limit)}: {percent:.1f} percent. The threshold "
                               f"is 95 percent or more: {'met' if met else 'not met'}.") if claim["estimate"] is not None
        else "No estimate is on the claim. The threshold is 95 percent or more: not met.")
    ids_met = [r["indicator_id"] for r in rows if r["met"]]
    return {"claim_id": claim["claim_id"], "indicators": rows, "indicators_met": ids_met, "count_met": len(ids_met),
            "sentence": (f"{plural(len(ids_met), 'indicator')} met on {claim['claim_id']}: {', '.join(ids_met)}." if ids_met
                         else f"No indicator is met on {claim['claim_id']}."),
            "what_this_is": "A measurement against the insurer's own indicators. An indicator that is met is a reason to pass the "
                            "claim to the investigations desk. It is not a finding that the claim is false."}


SHARED_FIELDS = (("phone", "phone number"), ("address", "address"), ("bank_account", "bank account"))


def shared_attributes(party: dict, parties: dict) -> list[dict]:
    """Every other person who shares a phone number, an address or a bank account with this party."""
    rows = []
    for other in parties.values():
        if other["party_id"] == party["party_id"] or not is_person(other) or not is_person(party):
            continue
        for field, words in SHARED_FIELDS:
            if party[field] and party[field] == other[field]:
                rows.append({"attribute": field, "value": party[field], "party_id": party["party_id"], "party_name": party["name"],
                             "other_party_id": other["party_id"], "other_party_name": other["name"],
                             "sentence": f"{party['name']} ({party['party_id']}) and {other['name']} ({other['party_id']}) are recorded "
                                         f"with the same {words}: {party[field]}."})
    return rows


def party_view(party: dict, claims: dict, parties: dict) -> dict:
    mine = sorted((claim_row(c, party["party_id"], parties) for c in claims.values() if role_on(c, party["party_id"])),
                  key=lambda r: r["claim_id"])
    return {**party, "claims": mine, "claim_count": len(mine)}


LINK_NOTE = ("A link is a fact that two records share. It is not a finding about any person: a shared repairer, phone number, address, "
             "bank account or witness can have an ordinary reason. The investigator decides what a link means.")


def claim_links(claim: dict, claims: dict, parties: dict) -> dict:
    """What a claim shares with other claims and other parties: a repairer, a witness, a phone number, an address, a bank account."""
    me = claim["claimant_party_id"]
    people = [parties[p["party_id"]] for p in claim["parties"] if is_person(parties[p["party_id"]])]
    shared = [row for person in people for row in shared_attributes(person, parties)]
    own, linked = [], []
    for other in sorted(claims.values(), key=lambda c: c["claim_id"]):
        if other["claim_id"] == claim["claim_id"]:
            continue
        if other["claimant_party_id"] == me:
            own.append(claim_row(other, me, parties, claim["loss_date"]))
            continue
        reasons = []
        if claim["repairer_party_id"] and claim["repairer_party_id"] == other["repairer_party_id"]:
            firm = parties[claim["repairer_party_id"]]
            reasons.append({"link_type": "repairer", "through_party_id": firm["party_id"], "through_party_name": firm["name"], "value": firm["name"],
                            "sentence": f"{firm['name']} ({firm['party_id']}) is the repairer on {claim['claim_id']} and on {other['claim_id']}."})
        for person in people:
            there = role_on(other, person["party_id"])
            if there:
                here = role_on(claim, person["party_id"])
                reasons.append({"link_type": here if here == there else "party_on_both_claims", "through_party_id": person["party_id"],
                                "through_party_name": person["name"], "value": person["name"],
                                "sentence": f"{person['name']} ({person['party_id']}) is recorded as {here} on {claim['claim_id']} and as "
                                            f"{there} on {other['claim_id']}, a claim by another claimant ({other['claimant']}, "
                                            f"{other['claimant_party_id']}). The records show that and nothing more about "
                                            f"{person['name']}."})
        there_people = {p["party_id"] for p in other["parties"]}
        for row in shared:
            if row["other_party_id"] in there_people:
                reasons.append({"link_type": row["attribute"], "through_party_id": row["other_party_id"],
                                "through_party_name": row["other_party_name"], "value": row["value"], "sentence": row["sentence"]})
        if reasons:
            linked.append({"claim_id": other["claim_id"], "claimant": other["claimant"], "claimant_party_id": other["claimant_party_id"],
                           "claim_type": other["claim_type"], "claim_type_label": other["claim_type_label"],
                           "status": other["status"], "status_in_words": STATUS_WORDS[other["status"]], "loss_date": other["loss_date"],
                           "linked_by": sorted({r["link_type"] for r in reasons}), "links": reasons})
    nothing = not linked and not shared
    if nothing:
        sentence = (f"{claim['claim_id']} shares no repairer, witness, phone number, address or bank account with any other claim or "
                    "party the insurer holds.")
    else:
        sentence = (f"{claim['claim_id']} is linked to {plural(len(linked), 'claim')} by another claimant: "
                    + "; ".join(f"{x['claim_id']} ({x['claimant']}) by {', '.join(w.replace('_', ' ') for w in x['linked_by'])}" for x in linked) + ".")
    own_repairer = [r["claim_id"] for r in own if claim["repairer_party_id"] and r["repairer_party_id"] == claim["repairer_party_id"]]
    if own_repairer:
        firm = parties[claim["repairer_party_id"]]
        sentence += (f" {firm['name']} ({firm['party_id']}) is also the repairer on the claimant's own other "
                     f"claim{'' if len(own_repairer) == 1 else 's'} {', '.join(own_repairer)}; no other claimant's claim names it"
                     + (" apart from the linked claims above." if any("repairer" in x["linked_by"] for x in linked) else ".")
                     + " A claimant's own other claims are not counted as links.")
    return {"claim_id": claim["claim_id"], "parties_on_this_claim": claim["parties"],
            "same_repairer_on_the_claimants_own_other_claims": own_repairer,
            "other_claims_by_the_same_claimant": own, "other_claims_by_the_same_claimant_count": len(own),
            "linked_claims": linked, "linked_claim_count": len(linked), "shared_attributes": shared,
            "no_links_found": nothing, "sentence": sentence, "what_a_link_is": LINK_NOTE}


# ---------------------------------------------------------------- public notices (all invented)

def build_public_notices(today: date) -> dict:
    L = lambda ago: long_date(d_ago(today, ago))

    def notice(nid, kind, source, ago, headline, text, name, *, born=None, year=None, address=None):
        return {"notice_id": nid, "kind": kind, "source": source, "published": d_ago(today, ago), "headline": headline, "text": text,
                "person_name": name, "date_of_birth": born, "year_of_birth": year or (int(born[:4]) if born else None),
                "address": address, "invented": True}

    rows = [
        notice("PN-901", "court_list", "Port Ilvane District Court, public list (invented)", 620,
               "Port Ilvane District Court: false statement in support of an insurance claim",
               f"PORT ILVANE DISTRICT COURT, list of {L(620)}. Evander Pryce, born 12 Mar 1979, of 4 Rope Walk, Port Ilvane. Charge: "
               "making a false statement in support of an insurance claim. Plea: guilty. Sentence: a fine of USD 1,200.",
               "Evander Pryce", born="1979-03-12", address="4 Rope Walk, Port Ilvane"),
        notice("PN-902", "press_item", "Tallowby Courier (invented newspaper)", 410,
               "Tallowby man barred from running companies",
               f"TALLOWBY COURIER, {L(410)}. A Tallowby man has been barred from acting as a company director for six years. Leofric "
               "Tansley, born in 1968, of Sheepwash Lane, Tallowby, ran a furniture firm that took deposits for goods it never "
               "delivered, the Meridia Companies Office said.",
               "Leofric Tansley", year=1968, address="Sheepwash Lane, Tallowby"),
        notice("PN-903", "court_list", "Marlow Reach County Court, public list (invented)", 300,
               "Marlow Reach County Court: bankruptcy order",
               f"MARLOW REACH COUNTY COURT, list of {L(300)}. Dorian Applegarth, born in 1959, of Marlow Reach. Bankruptcy order made.",
               "Dorian Applegarth", year=1959, address="Marlow Reach"),
    ]
    return {r["notice_id"]: r for r in rows}


def notice_for_party(notice: dict, party: dict) -> dict:
    """One notice that names a person with the party's name, set against the party's own date of birth and address."""
    if notice["date_of_birth"]:
        birth = "same" if notice["date_of_birth"] == party["date_of_birth"] else "differs"
        notice_birth = f"a date of birth of {long_date(notice['date_of_birth'])}"
    elif notice["year_of_birth"]:
        birth = "same_year" if str(notice["year_of_birth"]) == party["date_of_birth"][:4] else "differs"
        notice_birth = f"{notice['year_of_birth']} as the year of birth"
    else:
        birth, notice_birth = "not_given", "no date of birth"
    if notice["address"]:
        address = "same" if party["address"].lower().startswith(notice["address"].lower()) else "differs"
    else:
        address = "not_given"
    if birth == "differs":
        about = "a_different_person"
        verdict = "The dates of birth differ, so the notice is about another person with the same name. It says nothing about the party."
    elif birth == "same" and address != "differs":
        about = "the_same_person"
        verdict = ("The name, the date of birth and the address are the same, so the notice is about the party. It is a public record "
                   "of what it says. It is not a finding about any claim the insurer holds.")
    else:
        about = "cannot_tell"
        verdict = "The identifiers do not settle whether the notice is about the party. A person checks."
    return {**notice, "party_id": party["party_id"], "same_name": True, "date_of_birth_compared": birth, "address_compared": address,
            "about": about,
            "sentence": f"{notice['notice_id']} names {notice['person_name']} and gives {notice_birth} and "
                        f"{notice['address'] or 'no address'}. The party's record gives {long_date(party['date_of_birth'])} and "
                        f"{party['address']}. {verdict}"}


def notices_for_party(party: dict, notices: dict) -> list[dict]:
    if not is_person(party):
        return []
    return [notice_for_party(n, party) for n in notices.values() if n["person_name"].lower() == party["name"].lower()]


# ---------------------------------------------------------------- the whole system

def build_investigations(today: date) -> dict:
    own_policies = build_investigation_policies(today)
    parties = build_parties()
    return {
        "leakage_standards": copy.deepcopy(STANDARDS),
        "leakage_claims": build_leakage_claims(today),
        "fraud_indicators": copy.deepcopy(INDICATORS),
        "investigation_policies": own_policies,
        "investigation_parties": parties,
        "investigation_claims": build_investigation_claims(today, parties, {**build_policies(today), **own_policies}),
        "public_notices": build_public_notices(today),
    }
