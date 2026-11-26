"""Seed data, part 3: group medical schemes, members, medical policies, pre-authorisation requests,
medical claims held for review, providers with their contracts and tariffs, and provider invoices.

The sums are here as well: cover on a date, what a member has used and has left, what the plan pays on an
amount, and an invoice checked against the contract. The systems call them, so an agent never adds up.
"""

from __future__ import annotations

import copy
from datetime import date, timedelta

from .seed_policy import d_ago, d_ahead, long_date


def usd(amount: float) -> str:
    return f"USD {amount:,.2f}"


def money(amount: float) -> float:
    return round(amount + 1e-9, 2)


def plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


# The insurer's own codes. Each belongs to one benefit of a plan.
CODES = {
    "TMI-T-1010": ("First consultation, general practitioner", "consultation"),
    "TMI-T-1020": ("Follow-up consultation, general practitioner", "consultation"),
    "TMI-T-1030": ("Consultation, specialist", "consultation"),
    "TMI-T-2010": ("Blood test, full count", "diagnostics"),
    "TMI-T-2020": ("X-ray, one region", "diagnostics"),
    "TMI-T-3010": ("MRI scan, lumbar spine", "mri"),
    "TMI-T-3020": ("Ultrasound scan, one region", "diagnostics"),
    "TMI-T-4020": ("Physiotherapy session", "physiotherapy"),
    "TMI-T-5030": ("Day-case knee arthroscopy", "day_case"),
    "TMI-T-6040": ("Surgical removal of a wisdom tooth", "dental"),
    "TMI-T-7010": ("Medicine: pain relief tablets, pack of 28", "medicines"),
    "TMI-T-7020": ("Medicine: anti-inflammatory gel, tube of 100 g", "medicines"),
    "TMI-T-7030": ("Medicine: antibiotic course, 7 days", "medicines"),
}
FIRST_CONSULTATION, FOLLOW_UP = "TMI-T-1010", "TMI-T-1020"
POLICY_FOR_CODE = {"TMI-T-3010": "MP-301", "TMI-T-4020": "MP-302", "TMI-T-5030": "MP-303"}


# ---------------------------------------------------------------- schemes and their tables of benefits

def _ben(benefit_id, key, name, state, *, kind=None, amount=None, sessions=None, each="visit", percent=0, cap=None,
         conditions="", pre_auth=False, waiting_days=None):
    if state == "not_covered":
        return {"benefit_id": benefit_id, "benefit": key, "name": name, "state": state, "limit": None, "member_share": None,
                "limit_sentence": "This plan does not cover it.", "member_share_sentence": "This plan does not cover it.",
                "conditions": conditions, "pre_authorisation_needed": None, "waiting_period_days": None}
    if kind == "per_year":
        limit_sentence = f"Up to {usd(amount)} in a benefit year."
    elif kind == "per_visit":
        limit_sentence = f"Up to {usd(amount)} for each {each}."
    elif kind == "per_pregnancy":
        limit_sentence = f"Up to {usd(amount)} for each pregnancy."
    else:
        kind, limit_sentence = "sessions_per_year", f"Up to {sessions} sessions in a benefit year."
    if percent == 0:
        share_sentence = "The member pays no share."
    else:
        share_sentence = f"The member pays {percent} percent, up to {usd(cap)} in a benefit year."
    return {"benefit_id": benefit_id, "benefit": key, "name": name, "state": state,
            "limit": {"kind": kind, "amount": float(amount) if amount is not None else None, "sessions": sessions},
            "member_share": {"percent": percent, "cap_per_year": float(cap) if cap is not None else None},
            "limit_sentence": limit_sentence, "member_share_sentence": share_sentence, "conditions": conditions,
            "pre_authorisation_needed": pre_auth, "waiting_period_days": waiting_days}


HOW_TO_READ = ("The table of benefits has one row for each benefit of this plan: its state (covered, covered_with_conditions or "
               "not_covered), its limit, the member's share, its conditions and whether pre-authorisation is needed. The exclusions "
               "are what the plan never pays for. Limits and shares are for each member, not for a family. A treatment that is in "
               "neither the table nor the exclusions is not settled by this document: a person at the insurer answers.")

COMPLETE_BENEFITS = [
    _ben("BEN-F01", "inpatient", "Hospital stay", "covered", kind="per_year", amount=250000, pre_auth=True,
         conditions="A stay of one night or more in a hospital of the provider network."),
    _ben("BEN-F02", "day_case", "Day-case surgery", "covered", kind="per_year", amount=20000, pre_auth=True,
         conditions="Surgery where the patient goes home the same day."),
    _ben("BEN-F03", "consultation", "Consultations with a general practitioner or a specialist", "covered", kind="per_visit", amount=150),
    _ben("BEN-F04", "diagnostics", "Blood tests, X-rays and ultrasound scans", "covered", kind="per_year", amount=1500,
         conditions="Asked for by a doctor."),
    _ben("BEN-F05", "mri", "MRI scans", "covered", kind="per_year", amount=3000, conditions="Asked for by a doctor."),
    _ben("BEN-F06", "medicines", "Medicines on prescription, outside hospital", "covered", kind="per_year", amount=2000, percent=10, cap=150),
    _ben("BEN-F07", "physiotherapy", "Physiotherapy", "covered_with_conditions", sessions=12,
         conditions="On a doctor's referral. Sessions beyond 12 in a benefit year need pre-authorisation under medical policy MP-302."),
    _ben("BEN-F08", "maternity", "Maternity care", "covered_with_conditions", kind="per_pregnancy", amount=6000, pre_auth=True,
         waiting_days=300, conditions="Only after the member has been covered for 300 days in a row."),
    _ben("BEN-F09", "dental", "Dental treatment", "covered_with_conditions", kind="per_year", amount=500, percent=20, cap=100,
         conditions="Examinations, fillings and extractions. Crowns, implants and braces are not covered."),
    _ben("BEN-F10", "ambulance", "Emergency ambulance", "covered", kind="per_visit", amount=500, each="journey",
         conditions="In an emergency, to the nearest hospital."),
]

ESSENTIAL_BENEFITS = [
    _ben("BEN-E01", "inpatient", "Hospital stay", "covered", kind="per_year", amount=100000, percent=10, cap=500, pre_auth=True,
         conditions="A stay of one night or more in a hospital of the provider network."),
    _ben("BEN-E02", "day_case", "Day-case surgery", "covered", kind="per_year", amount=8000, percent=10, cap=500, pre_auth=True,
         conditions="Surgery where the patient goes home the same day."),
    _ben("BEN-E03", "consultation", "Consultations with a general practitioner or a specialist", "covered", kind="per_visit", amount=80,
         percent=20, cap=200),
    _ben("BEN-E04", "diagnostics", "Blood tests, X-rays and ultrasound scans", "covered", kind="per_year", amount=600, percent=20, cap=200,
         conditions="Asked for by a doctor."),
    _ben("BEN-E05", "mri", "MRI scans", "covered_with_conditions", kind="per_year", amount=1500, percent=20, cap=200, pre_auth=True,
         conditions="Every MRI scan needs pre-authorisation. For a scan of the lower back, medical policy MP-301 applies."),
    _ben("BEN-E06", "medicines", "Medicines on prescription, outside hospital", "covered", kind="per_year", amount=800, percent=20, cap=300),
    _ben("BEN-E07", "physiotherapy", "Physiotherapy", "covered_with_conditions", sessions=6, percent=20, cap=200,
         conditions="On a doctor's referral. Sessions beyond 6 in a benefit year need pre-authorisation under medical policy MP-302."),
    _ben("BEN-E08", "maternity", "Maternity care", "not_covered"),
    _ben("BEN-E09", "dental", "Dental treatment", "not_covered"),
    _ben("BEN-E10", "ambulance", "Emergency ambulance", "covered", kind="per_visit", amount=300, each="journey",
         conditions="In an emergency, to the nearest hospital."),
]


def _exclusions(prefix):
    texts = ["Treatment whose only purpose is to change how a person looks.",
             "Treatment that is experimental or has not been shown to work.",
             "Fertility treatment.",
             "Injuries from sport played for pay."]
    return [{"exclusion_id": f"EXC-{prefix}{n}", "text": text} for n, text in enumerate(texts, start=1)]


def build_schemes(today: date) -> dict:
    rows = [
        {"scheme_id": "GRP-6101", "employer": "Calderwick Freight Ltd", "employer_place": "Port Ilvane, Meridia",
         "plan_name": "Thornmere Health Complete", "_start_ago": 240, "benefits": COMPLETE_BENEFITS, "exclusions": _exclusions("F")},
        {"scheme_id": "GRP-6102", "employer": "Brindlemoor Bakeries Ltd", "employer_place": "Tallowby, Meridia",
         "plan_name": "Thornmere Health Essential", "_start_ago": 150, "benefits": ESSENTIAL_BENEFITS, "exclusions": _exclusions("E")},
    ]
    schemes = {}
    for row in rows:
        start = today - timedelta(days=row.pop("_start_ago"))
        row = copy.deepcopy(row)
        row["status"] = "in_force"
        row["period_start"], row["period_end"] = start.isoformat(), (start + timedelta(days=364)).isoformat()
        row["benefit_year"] = (f"The benefit year is the scheme's period, {long_date(row['period_start'])} to "
                               f"{long_date(row['period_end'])}.")
        row["how_to_read"], row["currency"] = HOW_TO_READ, "USD"
        schemes[row["scheme_id"]] = row
    return schemes


# ---------------------------------------------------------------- members

def _member(member_id, name, born, scheme_id, *, relationship="employee", dependant_of=None, start_ago=None, end_ago=None,
            cover_note="", used=None):
    return {"member_id": member_id, "name": name, "date_of_birth": born, "scheme_id": scheme_id, "relationship": relationship,
            "dependant_of": dependant_of, "_start_ago": start_ago, "_end_ago": end_ago, "cover_note": cover_note,
            "used_this_benefit_year": {key: {"amount": float(a), "sessions": s, "member_share_paid": float(share)}
                                       for key, (a, s, share) in (used or {}).items()}}


def build_members(today: date, schemes: dict) -> dict:
    rows = [
        _member("MEM-7201", "Rosalind Etherby", "1979-02-14", "GRP-6101",
                used={"physiotherapy": (504.0, 12, 0.0), "medicines": (180.0, 0, 18.0)}),
        _member("MEM-7202", "Caspian Thorneloe", "1981-09-30", "GRP-6101", used={"diagnostics": (95.0, 0, 0.0)}),
        _member("MEM-7203", "Maren Thorneloe", "1984-05-22", "GRP-6101", relationship="dependant", dependant_of="MEM-7202",
                used={"medicines": (40.0, 0, 4.0)}),
        # Joined 40 days before the insurer date: the waiting period for maternity care is not over.
        _member("MEM-7204", "Odette Farrowby", "1993-11-03", "GRP-6101", start_ago=40),
        _member("MEM-7205", "Barnaby Quickfall", "1975-07-19", "GRP-6102",
                used={"physiotherapy": (126.0, 3, 25.2), "diagnostics": (22.0, 0, 4.4)}),
        # Cover ended 30 days before the insurer date.
        _member("MEM-7206", "Hesper Linnet", "1988-01-27", "GRP-6102", end_ago=30, cover_note="The member left the employer.",
                used={"medicines": (60.0, 0, 12.0)}),
        _member("MEM-7207", "Tobias Wrenfield", "1969-12-08", "GRP-6102", used={"medicines": (730.0, 0, 146.0)}),
        _member("MEM-7208", "Philippa Sandeman", "1990-04-11", "GRP-6102"),
    ]
    members = {}
    for row in rows:
        start_ago, end_ago = row.pop("_start_ago"), row.pop("_end_ago")
        row["cover_start"] = d_ago(today, start_ago) if start_ago is not None else schemes[row["scheme_id"]]["period_start"]
        row["cover_end"] = d_ago(today, end_ago) if end_ago is not None else None
        members[row["member_id"]] = row
    return members


def age_on(born_iso: str, on_iso: str) -> int:
    born, on = date.fromisoformat(born_iso), date.fromisoformat(on_iso)
    return on.year - born.year - ((on.month, on.day) < (born.month, born.day))


def member_cover_on(member: dict, on_iso: str) -> dict:
    """Whether the member's cover was in force on a date, with the reason in plain words. The system works out the days."""
    on, start = date.fromisoformat(on_iso), date.fromisoformat(member["cover_start"])
    out = {"member_id": member["member_id"], "on": on_iso}
    if on < start:
        days = (start - on).days
        return {**out, "in_force": False,
                "reason": f"The member's cover started on {long_date(member['cover_start'])}. {long_date(on_iso)} is "
                          f"{plural(days, 'day')} before the start."}
    if member["cover_end"] and on > date.fromisoformat(member["cover_end"]):
        days = (on - date.fromisoformat(member["cover_end"])).days
        return {**out, "in_force": False,
                "reason": f"The member's cover ended on {long_date(member['cover_end'])}: {member['cover_note']} {long_date(on_iso)} is "
                          f"{plural(days, 'day')} after the end."}
    if member["cover_end"]:
        return {**out, "in_force": True,
                "reason": f"The member's cover ran from {long_date(member['cover_start'])} to {long_date(member['cover_end'])}, and "
                          f"{long_date(on_iso)} is inside it."}
    return {**out, "in_force": True,
            "reason": f"The member's cover started on {long_date(member['cover_start'])} and no end of cover is recorded, so cover "
                      f"is in force on {long_date(on_iso)}."}


def benefit_of(scheme: dict, key: str) -> dict | None:
    return next((b for b in scheme["benefits"] if b["benefit"] == key), None)


def _zero():
    return {"amount": 0.0, "sessions": 0, "member_share_paid": 0.0}


def waiting_period(member: dict, benefit: dict, on_iso: str) -> dict | None:
    if not benefit.get("waiting_period_days"):
        return None
    first = (date.fromisoformat(member["cover_start"]) + timedelta(days=benefit["waiting_period_days"])).isoformat()
    over = date.fromisoformat(on_iso) >= date.fromisoformat(first)
    return {"days": benefit["waiting_period_days"], "can_be_used_from": first, "over": over,
            "sentence": f"The member's cover started on {long_date(member['cover_start'])}. This benefit can be used from "
                        f"{long_date(first)}, after {benefit['waiting_period_days']} days of cover. {long_date(on_iso)} is "
                        f"{'on or after' if over else 'before'} that date."}


def usage_row(member: dict, benefit: dict, on_iso: str) -> dict:
    """One benefit of the member's plan with what the member has used this benefit year and what is left."""
    row = copy.deepcopy(benefit)
    if benefit["state"] == "not_covered":
        return {**row, "used": None, "remaining": None, "usage_sentence": "This plan does not cover it."}
    used = member["used_this_benefit_year"].get(benefit["benefit"], _zero())
    limit, share = benefit["limit"], benefit["member_share"]
    if limit["kind"] == "per_year":
        left = money(max(0.0, limit["amount"] - used["amount"]))
        row["used"], row["remaining"] = {"amount": used["amount"]}, {"amount": left}
        row["usage_sentence"] = (f"{usd(used['amount'])} used of {usd(limit['amount'])} this benefit year. "
                                 f"{usd(left)} remains.")
    elif limit["kind"] == "sessions_per_year":
        left = max(0, limit["sessions"] - used["sessions"])
        row["used"], row["remaining"] = {"sessions": used["sessions"]}, {"sessions": left}
        row["usage_sentence"] = (f"{used['sessions']} of {limit['sessions']} sessions used this benefit year. "
                                 + (f"{plural(left, 'session')} remain{'s' if left == 1 else ''}." if left else "No session remains."))
    else:
        row["used"], row["remaining"] = None, None
        what = "pregnancy" if limit["kind"] == "per_pregnancy" else "visit or journey"
        row["usage_sentence"] = f"The limit applies to each {what}, so there is no running total."
    if share["percent"]:
        left = money(max(0.0, share["cap_per_year"] - used["member_share_paid"]))
        row["member_share_paid_this_benefit_year"] = used["member_share_paid"]
        row["member_share_left_before_the_cap"] = left
        row["usage_sentence"] += (f" The member has paid {usd(used['member_share_paid'])} of the share cap of "
                                  f"{usd(share['cap_per_year'])}; {usd(left)} is left before the cap.")
    wait = waiting_period(member, benefit, on_iso)
    if wait:
        row["waiting_period"] = wait
    return row


def apply_benefit(benefit: dict, used: dict, amount: float, quantity: int = 1) -> dict:
    """What the plan pays on an amount: the part within the limit, the part over it, the member's share and the plan's part.

    `used` is the member's running usage for this benefit and is updated, so several lines of one claim add up."""
    amount = money(amount)
    base = {"benefit_id": benefit["benefit_id"], "benefit_name": benefit["name"], "amount": amount, "quantity": quantity}
    if benefit["state"] == "not_covered":
        return {**base, "within_the_limit": 0.0, "over_the_limit": amount, "member_share": 0.0, "plan_pays": 0.0, "member_pays": amount,
                "sessions_within_the_plan": None, "sessions_beyond_the_plan": None,
                "note": f"{benefit['benefit_id']} {benefit['name']} is not covered by this plan. The plan pays nothing of {usd(amount)}."}
    limit, share = benefit["limit"], benefit["member_share"]
    within_s = beyond_s = None
    if limit["kind"] == "per_year":
        left = money(max(0.0, limit["amount"] - used["amount"]))
        within = min(amount, left)
        why = (f"{usd(within)} is within the limit of {usd(limit['amount'])} a benefit year "
               f"({usd(used['amount'])} already used, {usd(left)} left).")
    elif limit["kind"] == "per_visit":
        within = money(min(amount / quantity, limit["amount"]) * quantity)
        why = f"{usd(within)} is within the limit of {usd(limit['amount'])} for each visit or journey."
    elif limit["kind"] == "per_pregnancy":
        within = min(amount, limit["amount"])
        why = f"{usd(within)} is within the limit of {usd(limit['amount'])} for each pregnancy."
    else:
        left_s = max(0, limit["sessions"] - used["sessions"])
        within_s = min(quantity, left_s)
        beyond_s = quantity - within_s
        within = money(amount * within_s / quantity)
        if within_s:
            why = (f"{plural(within_s, 'session')} of {quantity} {'is' if within_s == 1 else 'are'} within the plan's "
                   f"{limit['sessions']} sessions a benefit year ({used['sessions']} already used, {left_s} left); that is {usd(within)}.")
        else:
            why = (f"The member has used all {limit['sessions']} sessions the plan gives in a benefit year, so nothing of "
                   f"{usd(amount)} is within the plan's sessions.")
        used["sessions"] += within_s
    within = money(within)
    over = money(amount - within)
    part = money(within * share["percent"] / 100)
    capped = False
    if share["percent"]:
        cap_left = money(max(0.0, share["cap_per_year"] - used["member_share_paid"]))
        if part > cap_left:
            part, capped = cap_left, True
    used["amount"] = money(used["amount"] + within)
    used["member_share_paid"] = money(used["member_share_paid"] + part)
    pays = money(within - part)
    if over:
        why += (f" {usd(over)} is over the limit." if beyond_s is None
                else f" {plural(beyond_s, 'session')} ({usd(over)}) {'is' if beyond_s == 1 else 'are'} beyond the plan's sessions.")
    if share["percent"]:
        why += (f" The member's share is {share['percent']} percent of {usd(within)} = {usd(money(within * share['percent'] / 100))}"
                + (f", held to {usd(part)} by the share cap of {usd(share['cap_per_year'])} a benefit year." if capped else "."))
    else:
        why += " The member pays no share."
    why += f" The plan pays {usd(pays)}."
    return {**base, "within_the_limit": within, "over_the_limit": over, "member_share": part, "plan_pays": pays,
            "member_pays": money(part + over), "sessions_within_the_plan": within_s, "sessions_beyond_the_plan": beyond_s, "note": why}


# ---------------------------------------------------------------- medical policies

def _policy(policy_id, title, code, rows):
    return {"medical_policy_id": policy_id, "title": title, "procedure_code": code, "procedure": CODES[code][0],
            "how_to_read": "Every criterion must be met. A criterion the provider's notes say nothing about is neither met nor "
                           "failed: the provider is asked. A clinician decides; nobody else declines a request.",
            "criteria": [{"number": str(n), "text": text} for n, text in enumerate(rows, start=1)]}


MEDICAL_POLICIES = {
    "MP-301": _policy("MP-301", "MRI scan of the lower back", "TMI-T-3010", [
        "The patient has had lower back pain for at least 6 weeks.",
        "Treatment has been tried for at least 4 weeks without enough improvement: physiotherapy, prescribed pain relief, or both.",
        "The examination found a sign that a nerve is affected: weakness, numbness or a reduced reflex in a leg or foot."]),
    "MP-302": _policy("MP-302", "Physiotherapy beyond the plan's sessions", "TMI-T-4020", [
        "The member has used every physiotherapy session the plan gives in the benefit year. The system gives the sessions used.",
        "A report by the treating physiotherapist shows improvement over the sessions so far, with a measurement taken before and "
        "after: range of movement, strength or a pain score.",
        "A doctor's referral asks for the further sessions, and asks for no more than 6."]),
    "MP-303": _policy("MP-303", "Day-case knee arthroscopy", "TMI-T-5030", [
        "The patient has had knee pain, locking or giving way for at least 3 months.",
        "Physiotherapy has been tried for at least 6 weeks without enough improvement.",
        "An MRI report shows a torn meniscus or a loose body in the knee."]),
}


# ---------------------------------------------------------------- providers, contracts and tariffs

def _provider(provider_id, name, place, doctor, discount, free_days, prices):
    clauses = [
        ("1.1", "Prices", "The provider charges the agreed price in the tariff for each service on the tariff, and no more."),
        ("2.1", "Quantity", "Each tariff price is for one unit: one consultation, one test, one session, one pack. A line is charged "
                            "as the quantity given times the agreed price."),
        ("3.1", "Medicines", f"Medicines are billed at the tariff price less {discount} percent."),
        ("4.1", "Follow-up consultations",
         f"A follow-up consultation with a general practitioner within {free_days} days of the same patient's first consultation is "
         "not charged."),
        ("5.1", "Services not on the tariff",
         "A service that is not on the tariff needs the insurer's agreement in writing before it is given. Without that agreement "
         "the line is not payable until a claims officer has decided."),
        ("6.1", "Queries", "A claims officer of the insurer decides which lines of an invoice are queried, and the provider relations "
                           "team writes to the provider. Nobody else contacts the provider about an invoice."),
    ]
    return {"provider_id": provider_id, "name": name, "place": place, "lead_doctor": doctor, "contract_id": f"CON-{provider_id[4:]}",
            "medicines_discount_percent": discount, "follow_up_free_within_days": free_days,
            "contract": [{"clause": number, "heading": heading, "text": text} for number, heading, text in clauses],
            "tariff": [{"code": code, "description": CODES[code][0], "agreed_price": float(price), "is_a_medicine": CODES[code][1] == "medicines"}
                       for code, price in prices],
            "agreements_in_writing": [], "currency": "USD"}


PROVIDERS = {
    "PRV-5101": _provider("PRV-5101", "Ilvane Harbour Clinic", "Port Ilvane, Meridia", "Dr Isolde Varnham", 10, 14, [
        ("TMI-T-1010", 60), ("TMI-T-1020", 40), ("TMI-T-1030", 110), ("TMI-T-2010", 25), ("TMI-T-2020", 70), ("TMI-T-3010", 620),
        ("TMI-T-3020", 130), ("TMI-T-4020", 45), ("TMI-T-5030", 2400), ("TMI-T-7010", 12), ("TMI-T-7020", 9), ("TMI-T-7030", 18)]),
    "PRV-5102": _provider("PRV-5102", "Marlow Reach Medical Centre", "Marlow Reach, Meridia", "Dr Emrys Calloway", 5, 7, [
        ("TMI-T-1010", 55), ("TMI-T-1020", 35), ("TMI-T-1030", 100), ("TMI-T-2010", 22), ("TMI-T-2020", 65), ("TMI-T-3010", 600),
        ("TMI-T-4020", 42), ("TMI-T-5030", 2300), ("TMI-T-6040", 380), ("TMI-T-7010", 12.5), ("TMI-T-7020", 9.5), ("TMI-T-7030", 19)]),
}


# ---------------------------------------------------------------- pre-authorisation requests

def pre_authorisation(pa_id, member, provider, code, requested_iso, planned_iso, notes, *, procedure=None):
    """One request with its two documents: the request form and the clinical notes."""
    form = (f"PRE-AUTHORISATION REQUEST\nProvider: {provider['name']} ({provider['provider_id']})\n"
            f"Patient: {member['name']}, member {member['member_id']}\nProcedure: {procedure or CODES[code][0]} ({code})\n"
            f"Planned date: {long_date(planned_iso)}\nRequested by: {provider['lead_doctor']}\nDated: {long_date(requested_iso)}")
    return {"pre_authorisation_id": pa_id, "status": "received", "member_id": member["member_id"], "member_name": member["name"],
            "provider_id": provider["provider_id"], "provider_name": provider["name"], "procedure_code": code,
            "procedure": procedure or CODES[code][0], "date_requested": requested_iso, "planned_date": planned_iso,
            "documents": [{"document_id": f"{pa_id}-D1", "doc_type": "request_form", "title": "Pre-authorisation request form", "text": form},
                          {"document_id": f"{pa_id}-D2", "doc_type": "clinical_notes", "title": "Clinical notes",
                           "text": f"CLINICAL NOTES, {provider['name']}, consultation of {long_date(requested_iso)}\n{notes}"}],
            "decision": None, "assessment_drafts": []}


def build_pre_authorisations(today: date, members: dict) -> dict:
    p1, p2 = PROVIDERS["PRV-5101"], PROVIDERS["PRV-5102"]
    L = lambda ago: long_date(d_ago(today, ago))
    rows = [
        # Every criterion of MP-301 met.
        pre_authorisation("PA-8101", members["MEM-7205"], p1, "TMI-T-3010", d_ago(today, 2), d_ahead(today, 7),
                          "Lower back pain for 9 weeks, spreading down the left leg.\nTreatment tried: physiotherapy for 5 weeks and "
                          "prescribed pain relief over the same 5 weeks. The pain is little changed.\nExamination: left ankle reflex "
                          "reduced. Numbness over the outer side of the left foot.\nPlan: MRI scan of the lumbar spine."),
        # Criterion 2 of MP-303 plainly not met: 2 weeks of physiotherapy where 6 are asked for.
        pre_authorisation("PA-8102", members["MEM-7202"], p1, "TMI-T-5030", d_ago(today, 3), d_ahead(today, 12),
                          "Pain and locking of the right knee for 4 months.\nTreatment tried: physiotherapy for 2 weeks, which the "
                          f"patient then stopped.\nMRI report of {L(10)}: tear of the medial meniscus of the right knee.\n"
                          "Plan: day-case arthroscopy of the right knee."),
        # The notes say nothing about the examination: criterion 3 of MP-301 cannot be read from them.
        pre_authorisation("PA-8103", members["MEM-7207"], p2, "TMI-T-3010", d_ago(today, 1), d_ahead(today, 9),
                          "Lower back pain for 8 weeks.\nTreatment tried: prescribed pain relief for 6 weeks, with little effect.\n"
                          "Plan: MRI scan of the lumbar spine."),
        # The member's cover ended before the planned date.
        pre_authorisation("PA-8104", members["MEM-7206"], p1, "TMI-T-5030", d_ago(today, 3), d_ahead(today, 10),
                          "Pain and giving way of the left knee for 5 months.\nTreatment tried: physiotherapy for 8 weeks without "
                          f"enough improvement.\nMRI report of {L(20)}: tear of the lateral meniscus of the left knee.\n"
                          "Plan: day-case arthroscopy of the left knee."),
        # Dental treatment is not covered by the member's plan.
        pre_authorisation("PA-8105", members["MEM-7208"], p2, "TMI-T-6040", d_ago(today, 2), d_ahead(today, 14),
                          "Lower right wisdom tooth partly through the gum, with two infections of the gum in 3 months.\n"
                          "Plan: surgical removal of the tooth."),
        # The member's plan needs no pre-authorisation for an MRI scan.
        pre_authorisation("PA-8106", members["MEM-7204"], p1, "TMI-T-3010", d_ago(today, 1), d_ahead(today, 6),
                          "Lower back pain for 7 weeks.\nTreatment tried: physiotherapy for 4 weeks, with little effect.\n"
                          "Examination: weakness lifting the right foot.\nPlan: MRI scan of the lumbar spine."),
    ]
    return {r["pre_authorisation_id"]: r for r in rows}


# ---------------------------------------------------------------- medical claims

HOLD_NOTES = {
    "duplicate": "The claims engine found an earlier claim for the same member with the same code.",
    "eligibility": "The claims engine could not confirm that the member's cover was in force on the date of service.",
    "limit": "The claims engine found that the claim may take the member over a limit of the plan.",
    "medical_necessity": "The claims engine holds this claim until the medical policy for the procedure is read against the file.",
}


def _claim(claim_id, member_id, provider_id, received, lines, *, hold=None, paid_on=None, documents=()):
    rows = [{"line_id": f"{claim_id}-L{n}", "code": code, "description": CODES[code][0], "quantity": qty, "amount": float(amount),
             "date_of_service": service} for n, (code, qty, amount, service) in enumerate(lines, start=1)]
    return {"claim_id": claim_id, "member_id": member_id, "provider_id": provider_id, "status": "held" if hold else "paid",
            "received": received, "hold_reason": hold, "hold_note": HOLD_NOTES.get(hold), "paid_on": paid_on,
            "amount_claimed": money(sum(r["amount"] for r in rows)), "currency": "USD", "lines": rows,
            "documents": [{"document_id": f"{claim_id}-D{n}", "doc_type": doc_type, "title": title, "text": text}
                          for n, (doc_type, title, text) in enumerate(documents, start=1)],
            "decision": None, "determination_drafts": []}


def build_medical_claims(today: date) -> dict:
    A = lambda ago: d_ago(today, ago)
    L = lambda ago: long_date(d_ago(today, ago))
    rows = [
        # Earlier claims, paid.
        _claim("MC-9011", "MEM-7201", "PRV-5102", A(18), [("TMI-T-1010", 1, 55.00, A(20))], paid_on=A(15)),
        _claim("MC-9012", "MEM-7205", "PRV-5102", A(14), [("TMI-T-4020", 1, 42.00, A(16))], paid_on=A(11)),
        _claim("MC-9013", "MEM-7207", "PRV-5101", A(38), [("TMI-T-7010", 2, 21.60, A(40))], paid_on=A(35)),
        # A true duplicate of MC-9011: same member, provider, date of service and code.
        _claim("MC-9101", "MEM-7201", "PRV-5102", A(6), [("TMI-T-1010", 1, 55.00, A(20))], hold="duplicate"),
        # A look-alike of MC-9012: same code and provider, a different date of service.
        _claim("MC-9102", "MEM-7205", "PRV-5102", A(5), [("TMI-T-4020", 1, 42.00, A(9))], hold="duplicate"),
        # The date of service is after the member's cover ended.
        _claim("MC-9103", "MEM-7206", "PRV-5101", A(8), [("TMI-T-1010", 1, 60.00, A(12))], hold="eligibility"),
        # Takes the member over the yearly limit for medicines.
        _claim("MC-9104", "MEM-7207", "PRV-5101", A(4), [("TMI-T-7010", 6, 64.80, A(7)), ("TMI-T-7030", 3, 48.60, A(7))], hold="limit"),
        # Medical necessity, and the notes meet MP-301.
        _claim("MC-9105", "MEM-7203", "PRV-5101", A(5), [("TMI-T-3010", 1, 620.00, A(8))], hold="medical_necessity", documents=[
            ("clinical_notes", "Clinical notes",
             f"CLINICAL NOTES, Ilvane Harbour Clinic, consultation of {L(13)}\nLower back pain for 10 weeks.\n"
             "Treatment tried: physiotherapy for 6 weeks without enough improvement.\nExamination: weakness lifting the right foot. "
             "Right ankle reflex reduced.\nPlan: MRI scan of the lumbar spine."),
            ("scan_report", "MRI report",
             f"MRI REPORT, Ilvane Harbour Clinic, scan of {L(8)}\nLumbar spine. A disc between the fourth and fifth lumbar vertebrae "
             "presses on the nerve root on the right.")]),
        # Medical necessity, and the file does not settle MP-302: there is no report from the physiotherapist.
        _claim("MC-9106", "MEM-7201", "PRV-5102", A(3),
               [("TMI-T-4020", 1, 42.00, A(14)), ("TMI-T-4020", 1, 42.00, A(10)), ("TMI-T-4020", 1, 42.00, A(6))],
               hold="medical_necessity", documents=[
                   ("referral", "Doctor's referral",
                    f"REFERRAL, Marlow Reach Medical Centre\nPatient: Rosalind Etherby, member MEM-7201\nI refer this patient for 3 "
                    f"further sessions of physiotherapy for the right shoulder.\nSigned: Dr Emrys Calloway\nDated: {L(16)}")]),
    ]
    return {r["claim_id"]: r for r in rows}


def compare_with_earlier(claim: dict, claims: dict) -> list[dict]:
    """Each line of a claim set beside every earlier line of the same member with the same code."""
    rows = []
    for line in claim["lines"]:
        for other in claims.values():
            if other["claim_id"] == claim["claim_id"] or other["member_id"] != claim["member_id"] or other["received"] > claim["received"]:
                continue
            if other["status"] == "held" and other["claim_id"] > claim["claim_id"]:
                continue
            for old in other["lines"]:
                if old["code"] != line["code"]:
                    continue
                same_provider = other["provider_id"] == claim["provider_id"]
                same_date = old["date_of_service"] == line["date_of_service"]
                days = abs((date.fromisoformat(line["date_of_service"]) - date.fromisoformat(old["date_of_service"])).days)
                state = (f"It was paid on {long_date(other['paid_on'])}." if other["status"] == "paid"
                         else f"Its status is {other['status']}.")
                if same_provider and same_date:
                    sentence = (f"{other['claim_id']} is for the same member, the same provider, the same code and the same date of "
                                f"service, {long_date(old['date_of_service'])}. {state}")
                else:
                    differs = []
                    if not same_provider:
                        differs.append(f"its provider is {other['provider_id']} and this claim's is {claim['provider_id']}")
                    if not same_date:
                        differs.append(f"its date of service is {long_date(old['date_of_service'])} and this line's is "
                                       f"{long_date(line['date_of_service'])}, {plural(days, 'day')} apart")
                    sentence = (f"{other['claim_id']} is for the same member and the same code, but {' and '.join(differs)}. {state}")
                rows.append({"line_id": line["line_id"], "earlier_claim_id": other["claim_id"], "earlier_line_id": old["line_id"],
                             "earlier_claim_status": other["status"], "earlier_paid_on": other["paid_on"],
                             "code": line["code"], "same_member": True, "same_code": True, "same_provider": same_provider,
                             "same_date_of_service": same_date, "same_amount": old["amount"] == line["amount"],
                             "date_of_service": line["date_of_service"], "earlier_date_of_service": old["date_of_service"],
                             "days_between_the_dates_of_service": days,
                             "member_provider_date_and_code_all_match": same_provider and same_date, "sentence": sentence})
    return rows


def claim_figures(claim: dict, member: dict, scheme: dict) -> dict:
    """What the plan would pay on a claim, line by line, with the totals. The system adds up."""
    running = {key: dict(value) for key, value in member["used_this_benefit_year"].items()}
    rows, beyond_amount, beyond_sessions = [], 0.0, 0
    for line in claim["lines"]:
        benefit = benefit_of(scheme, CODES[line["code"]][1])
        used = running.setdefault(benefit["benefit"], _zero())
        row = {"line_id": line["line_id"], "code": line["code"], **apply_benefit(benefit, used, line["amount"], line["quantity"])}
        if row["sessions_beyond_the_plan"]:
            beyond_amount, beyond_sessions = beyond_amount + row["over_the_limit"], beyond_sessions + row["sessions_beyond_the_plan"]
        rows.append(row)
    total = lambda field: money(sum(r[field] for r in rows))
    plus = lambda field: " + ".join(f"{r[field]:,.2f}" for r in rows)
    out = {"what_this_is": "What the plan's limits and the member's share give on these lines. It does not say the claim is to be "
                           "paid: the cover on the date of service, the earlier claims and the medical policy are separate.",
           "lines": rows, "total_claimed": total("amount"), "total_within_the_limits": total("within_the_limit"),
           "total_over_the_limits": total("over_the_limit"), "member_share": total("member_share"), "plan_pays": total("plan_pays"),
           "member_pays": total("member_pays"),
           "working": [f"Within the limits: {plus('within_the_limit')} = {total('within_the_limit'):,.2f}",
                       f"Over the limits: {total('amount'):,.2f} - {total('within_the_limit'):,.2f} = {total('over_the_limit'):,.2f}",
                       f"Less the member's share: {total('within_the_limit'):,.2f} - {total('member_share'):,.2f} = {total('plan_pays'):,.2f}",
                       f"The plan pays {usd(total('plan_pays'))}. The member pays {usd(total('member_pays'))}."]}
    if beyond_sessions:
        benefit = benefit_of(scheme, "physiotherapy")
        share = money(beyond_amount * benefit["member_share"]["percent"] / 100)
        if benefit["member_share"]["percent"]:
            share = min(share, money(max(0.0, benefit["member_share"]["cap_per_year"]
                                         - running["physiotherapy"]["member_share_paid"])))
        extra = money(beyond_amount - share)
        out["sessions_beyond_the_plan"] = beyond_sessions
        out["plan_pays_if_the_medical_policy_is_met"] = money(out["plan_pays"] + extra)
        out["working"].append(f"{plural(beyond_sessions, 'session')} ({usd(money(beyond_amount))}) "
                              f"{'is' if beyond_sessions == 1 else 'are'} beyond the plan's sessions. They are paid only if medical "
                              f"policy MP-302 is met and the assessor decides so; the plan would then pay "
                              f"{usd(out['plan_pays_if_the_medical_policy_is_met'])} in all.")
    return out


# ---------------------------------------------------------------- provider invoices

def _invoice(invoice_id, provider_id, received, lines):
    rows = []
    for n, (code, description, qty, unit, service, member_id) in enumerate(lines, start=1):
        rows.append({"line_id": f"{invoice_id}-L{n}", "code": code, "description": description or CODES[code][0], "quantity": qty,
                     "unit_price_charged": float(unit), "amount_charged": money(qty * unit), "date_of_service": service,
                     "patient_member_id": member_id})
    return {"invoice_id": invoice_id, "provider_id": provider_id, "provider_name": PROVIDERS[provider_id]["name"], "status": "received",
            "received": received, "currency": "USD", "total_charged": money(sum(r["amount_charged"] for r in rows)), "lines": rows,
            "decision": None, "difference_drafts": []}


def build_invoices(today: date) -> dict:
    A = lambda ago: d_ago(today, ago)
    rows = [
        # Agrees with the tariff throughout. The follow-up is 16 days after the first consultation, outside the 14 free days.
        _invoice("PI-9501", "PRV-5101", A(4), [("TMI-T-1010", "", 1, 60.00, A(30), "MEM-7205"), ("TMI-T-2010", "", 1, 25.00, A(30), "MEM-7205"),
                                               ("TMI-T-1020", "", 1, 40.00, A(14), "MEM-7205"), ("TMI-T-4020", "", 1, 45.00, A(12), "MEM-7203")]),
        # One line charged over the tariff: the X-ray at 80.00 where 65.00 is agreed.
        _invoice("PI-9502", "PRV-5102", A(3), [("TMI-T-1030", "", 1, 100.00, A(9), "MEM-7208"), ("TMI-T-2020", "", 1, 80.00, A(9), "MEM-7208")]),
        # One line whose code is not on the tariff.
        _invoice("PI-9503", "PRV-5101", A(5), [("TMI-T-1030", "", 1, 110.00, A(11), "MEM-7201"),
                                               ("TMI-T-8050", "Shockwave therapy session", 1, 55.00, A(11), "MEM-7201")]),
        # A follow-up charged 5 days after the first consultation, inside the 7 free days.
        _invoice("PI-9504", "PRV-5102", A(2), [("TMI-T-1010", "", 1, 55.00, A(12), "MEM-7207"), ("TMI-T-2010", "", 1, 22.00, A(12), "MEM-7207"),
                                               ("TMI-T-1020", "", 1, 35.00, A(7), "MEM-7207")]),
        # Medicines charged at the full tariff price: the 10 percent discount was not applied.
        _invoice("PI-9505", "PRV-5101", A(1), [("TMI-T-1010", "", 1, 60.00, A(6), "MEM-7203"), ("TMI-T-7010", "", 2, 12.00, A(6), "MEM-7203"),
                                               ("TMI-T-7030", "", 1, 18.00, A(6), "MEM-7203")]),
    ]
    return {r["invoice_id"]: r for r in rows}


def check_invoice(invoice: dict, provider: dict, invoices: dict) -> dict:
    """An invoice set against the provider's contract and tariff, line by line, with the totals."""
    tariff = {row["code"]: row for row in provider["tariff"]}
    discount, free_days, name = provider["medicines_discount_percent"], provider["follow_up_free_within_days"], provider["name"]
    firsts = [line for inv in invoices.values() if inv["provider_id"] == provider["provider_id"]
              for line in inv["lines"] if line["code"] == FIRST_CONSULTATION]
    rows = []
    for line in invoice["lines"]:
        qty, unit, charged = line["quantity"], line["unit_price_charged"], line["amount_charged"]
        row = {"line_id": line["line_id"], "code": line["code"], "description": line["description"], "quantity": qty,
               "unit_price_charged": unit, "amount_charged": charged, "on_the_tariff": line["code"] in tariff,
               "tariff_price": None, "agreed_unit_price": None, "follow_up": None}
        entry = tariff.get(line["code"])
        if entry is None:
            row.update(agreed_amount=0.0, difference=charged, kind="not_on_the_tariff", clause="5.1",
                       note=f"{line['code']} is not on the tariff of {name}. Under clause 5.1 a service not on the tariff needs the "
                            "insurer's agreement in writing before it is given, and no such agreement is on file. Nothing is agreed "
                            f"for this line, so the whole {usd(charged)} is a difference.")
            rows.append(row)
            continue
        price = agreed = entry["agreed_price"]
        row["tariff_price"] = price
        kind, clause, note = "agrees", None, ""
        if entry["is_a_medicine"]:
            agreed, clause = money(price * (100 - discount) / 100), "3.1"
            note = (f"A medicine: the tariff price of {usd(price)} less {discount} percent under clause 3.1 is {usd(agreed)} a unit.")
        if line["code"] == FOLLOW_UP:
            earlier = [f for f in firsts if f["patient_member_id"] == line["patient_member_id"]
                       and f["date_of_service"] <= line["date_of_service"]]
            if earlier:
                first = max(earlier, key=lambda f: f["date_of_service"])
                days = (date.fromisoformat(line["date_of_service"]) - date.fromisoformat(first["date_of_service"])).days
                inside = days <= free_days
                row["follow_up"] = {"first_consultation_line_id": first["line_id"], "first_consultation_date": first["date_of_service"],
                                    "days_after_the_first_consultation": days, "free_within_days": free_days,
                                    "inside_the_free_period": inside}
                note = (f"The same patient's first consultation was on {long_date(first['date_of_service'])} ({first['line_id']}). "
                        f"This follow-up on {long_date(line['date_of_service'])} is {plural(days, 'day')} later. Clause 4.1 gives "
                        f"{free_days} days, so the follow-up is {'not charged' if inside else 'charged'}.")
                if inside:
                    agreed, kind, clause = 0.0, "follow_up_inside_the_free_period", "4.1"
            else:
                note = "No first consultation for this patient is on this provider's invoices, so clause 4.1 does not take the charge away."
        agreed_amount = money(qty * agreed)
        difference = money(charged - agreed_amount)
        if kind == "agrees" and difference > 0:
            if entry["is_a_medicine"] and unit == price:
                kind = "medicines_discount_not_applied"
                note += f" The invoice charges the full tariff price of {usd(price)}: the discount was not applied."
            else:
                kind, clause = "over_the_tariff", "1.1"
                note = (note + " " if note else "") + f"Charged {usd(unit)} a unit where {usd(agreed)} is agreed (clause 1.1)."
        elif kind == "agrees" and difference < 0:
            kind = "under_the_tariff"
            note = (note + " " if note else "") + f"Charged {usd(unit)} a unit, which is less than the {usd(agreed)} agreed."
        elif kind == "agrees" and not note:
            note = "Charged at the agreed price."
        row.update(agreed_unit_price=agreed, agreed_amount=agreed_amount, difference=difference, kind=kind, clause=clause,
                   note=f"{note} {qty} x {agreed:,.2f} = {agreed_amount:,.2f} agreed; {charged:,.2f} charged; difference {difference:,.2f}.")
        rows.append(row)
    total = lambda field: money(sum(r[field] for r in rows))
    plus = lambda field: " + ".join(f"{r[field]:,.2f}" for r in rows)
    different = [r["line_id"] for r in rows if r["difference"] != 0]
    return {"invoice_id": invoice["invoice_id"], "provider_id": provider["provider_id"], "contract_id": provider["contract_id"],
            "currency": "USD", "lines": rows, "total_charged": total("amount_charged"), "total_agreed": total("agreed_amount"),
            "total_difference": total("difference"), "lines_with_a_difference": different,
            "agrees_with_the_contract": not different,
            "working": [f"Charged: {plus('amount_charged')} = {total('amount_charged'):,.2f}",
                        f"Agreed: {plus('agreed_amount')} = {total('agreed_amount'):,.2f}",
                        f"Difference: {total('amount_charged'):,.2f} - {total('agreed_amount'):,.2f} = {total('difference'):,.2f}"]}


# ---------------------------------------------------------------- the whole system

def build_health(today: date) -> dict:
    schemes = build_schemes(today)
    members = build_members(today, schemes)
    return {
        "health_schemes": schemes,
        "health_members": members,
        "medical_policies": copy.deepcopy(MEDICAL_POLICIES),
        "pre_authorisations": build_pre_authorisations(today, members),
        "medical_claims": build_medical_claims(today),
        "health_providers": copy.deepcopy(PROVIDERS),
        "provider_invoices": build_invoices(today),
        "call_back_requests": {},
    }
