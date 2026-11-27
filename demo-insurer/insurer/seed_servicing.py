"""Seed data, part 6: servicing. The servicing rules, change requests, certificate requests with the certificate and
endorsement templates, brokers with the policies each one places, claims the broker desk is asked about, and broker queries.

The sums are here as well: a change request measured against the servicing rules, the premium adjustment pro rata with its
working, the days without cover between two dates, a policy as it stands on a date with the endorsements in effect, a
certificate request checked against the policy, and what a broker may be told about a claim. The system calls them, so an
agent never adds up, never counts days and never compares two figures.

Policies and claims of the policy and claims systems are read as they stand and are never copied. Policies that only the
servicing cases need (POL-28xx) and the claims the broker desk is asked about (SCL-78xx) are held in this system.
"""

from __future__ import annotations

import copy
from datetime import date, timedelta

from .seed_policy import _home, _motor, cover_on, d_ago, d_ahead, long_date

BACKDATING_DAYS = 14
SUM_INSURED_INCREASE_PERCENT = 20.0
YOUNG_DRIVER_AGE = 25

RATING_AREAS = {"Port Ilvane": "RA-1", "Marlow Reach": "RA-2", "Tallowby": "RA-3"}
FIELD_LABELS = {"sum_insured": "sum insured for the vehicle", "third_party_property_limit": "third party property limit",
                "buildings_sum_insured": "buildings sum insured", "contents_sum_insured": "contents sum insured",
                "deductible": "deductible", "alternative_accommodation_limit": "alternative accommodation limit"}
CHANGE_TYPES = {"address": "Change of address", "vehicle": "Change of vehicle", "sum_insured": "Change of sum insured",
                "add_driver": "Added driver", "cancellation": "Cancellation"}


def usd(amount: float) -> str:
    return f"USD {amount:,.2f}"


def money(amount: float) -> float:
    return round(amount + 1e-9, 2)


def plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


def _days(a_iso: str, b_iso: str) -> int:
    """Days from a to b: positive when b is later."""
    return (date.fromisoformat(b_iso) - date.fromisoformat(a_iso)).days


def _shift(iso: str, n: int) -> str:
    return (date.fromisoformat(iso) + timedelta(days=n)).isoformat()


# ---------------------------------------------------------------- servicing rules

RULES_HOW_TO_READ = ("Each rule has an id, a heading, a kind and its text. A rule of the kind referral sends the request to the "
                     "person it names before anything is changed. A rule of the kind calculation says how a figure is worked out. "
                     "A rule of the kind point_to_raise asks for something to be pointed out to the servicing officer. A value "
                     "exactly on a limit does not make a rule apply. The system measures every request against these rules: "
                     "get_change_request gives the result.")


def _rule(rule_id, heading, kind, sends_to, text):
    return {"rule_id": rule_id, "heading": heading, "kind": kind, "sends_to": sends_to, "text": text}


SERVICING_RULES = {r["rule_id"]: r for r in [
    _rule("SR-1", "Backdating", "referral", "the servicing team leader",
          f"A change with an effective date more than {BACKDATING_DAYS} days before the date the request was received is not made "
          f"without a referral to the servicing team leader. An effective date exactly {BACKDATING_DAYS} days before the date "
          "received needs no referral."),
    _rule("SR-2", "Change of address to another rating area", "referral", "underwriting",
          "Meridia has three rating areas: RA-1 Port Ilvane, RA-2 Marlow Reach and RA-3 Tallowby. A change of address to another "
          "rating area is re-rated by underwriting before the change is made, and no premium adjustment is worked out until "
          "then. A change of address inside the same rating area needs no re-rating and changes no premium."),
    _rule("SR-3", "Increase in a sum insured", "referral", "underwriting",
          f"An increase in a sum insured of more than {SUM_INSURED_INCREASE_PERCENT:.0f} percent of the present sum insured is "
          f"referred to an underwriter. An increase of exactly {SUM_INSURED_INCREASE_PERCENT:.0f} percent needs no referral."),
    _rule("SR-4", "Cancellation with an open claim", "referral", "the servicing team leader",
          "A request to cancel a policy that has an open claim is referred to the servicing team leader, and no return premium "
          "is worked out until the team leader has decided."),
    _rule("SR-5", "Young driver", "referral", "underwriting",
          f"Adding a driver who is under {YOUNG_DRIVER_AGE} years of age on the effective date is referred to an underwriter. A "
          f"driver who is exactly {YOUNG_DRIVER_AGE} on the effective date needs no referral."),
    _rule("SR-6", "Premium adjustment pro rata", "calculation", "",
          "A change of premium mid-term is charged or returned pro rata: the difference between the new and the present annual "
          "premium, times the days that remain in the policy period counted from the effective date to the last day of the "
          "period, both included, divided by the days in the period. On a cancellation the premium for the days after the "
          "cancellation date is returned in the same way. The system does this sum and shows its working."),
    _rule("SR-7", "Gap in cover", "point_to_raise", "",
          "Cover runs to the end of its last day, and new cover starts at the start of its first day. There is no gap when new "
          "cover starts on the day after the last day of cover. Any day without cover is pointed out to the servicing officer, "
          "with the dates and the number of days. So is an effective date before the insurer date, because the change would "
          "reach back over days that have passed. This rule asks for no referral."),
    _rule("SR-8", "Policy not in force on the effective date", "referral", "the servicing team leader",
          "A change to a policy that is not in force on the effective date is referred to the servicing team leader."),
]}

UNDERWRITING_RULES = ("SR-2", "SR-3", "SR-5")
TEAM_LEADER_RULES = ("SR-1", "SR-4", "SR-8")


# ---------------------------------------------------------------- policies held in this system, premiums and brokers

def build_serviced_policies(today: date) -> dict:
    """Policies only the servicing cases need. The schedule is the schedule at the start of the period: an endorsement
    with a 'changes' part changes it from the endorsement's effective date (policy_as_it_stands applies it)."""
    rows = [
        _motor("POL-2801", "Ottoline Merrivale", "11 Pilchard Steps, Port Ilvane, Meridia", "Tarn Vale 1.6 saloon, 2021", "PI-3318-R",
               11500, 300, 140, named_drivers=["Ottoline Merrivale"]),
        _home("POL-2802", "Cordelia Ravenscar", "30 Glasswort Lane, Marlow Reach, Meridia", 205000, 28000, 250, 100),
        _motor("POL-2803", "Florian Tredwell", "9 Cinder Path, Marlow Reach, Meridia", "Vesper Lane 1.4 hatchback, 2020", "MR-2291-C",
               9800, 300, 214),
        _motor("POL-2811", "Jocasta Wimberry", "45 Netmakers Row, Port Ilvane, Meridia", "Halden Crest 1.8 hatchback, 2022", "PI-8053-J",
               14500, 300, 170),
        _home("POL-2812", "Leopold Quenningbrook", "8 Foxglove Rise, Marlow Reach, Meridia", 232000, 34000, 250, 44),
        _home("POL-2813", "Philomena Ashcombe", "21 Tollgate Mews, Marlow Reach, Meridia", 248000, 31000, 300, 205),
        _home("POL-2814", "Wystan Harcastle", "2 Shepherds Fold, Tallowby, Meridia", 276000, 37000, 250, 160),
        _home("POL-2821", "Seraphina Dunmallow", "13 Lapwing Close, Tallowby, Meridia", 225000, 32000, 250, 90),
        _home("POL-2822", "Barnabas Thrupp", "6 Kittiwake Row, Tallowby, Meridia", 220000, 35000, 250, 120,
              endorsements=[{"endorsement_id": "END-2822-1", "title": "Increase in the contents sum insured", "_effective_ago": 30,
                             "changes": {"contents_sum_insured": 50000.0},
                             "text": "From the effective date of this endorsement the sum insured for contents is USD 50,000.00 in "
                                     "place of USD 35,000.00. All other terms of the policy are unchanged."}]),
    ]
    policies = {}
    for row in rows:
        start = today - timedelta(days=row.pop("_start_ago"))
        end = start + timedelta(days=row.pop("_term")) - timedelta(days=1)
        row["period_start"], row["period_end"] = start.isoformat(), end.isoformat()
        row["cancelled_on"] = None
        for e in row["endorsements"]:
            e["effective"] = d_ago(today, e.pop("_effective_ago"))
        row["schedule"]["interested_parties"] = []
        row["currency"] = "USD"
        policies[row["policy_id"]] = row
    policies["POL-2821"]["schedule"]["interested_parties"] = ["Otterbank Home Loans Ltd"]
    return policies


PREMIUMS = {"POL-2001": 780.0, "POL-2002": 640.0, "POL-2003": 520.0, "POL-2004": 760.0, "POL-2005": 690.0, "POL-2006": 580.0,
            "POL-2007": 1240.0, "POL-2008": 610.0, "POL-2009": 600.0, "POL-2010": 720.0, "POL-2011": 840.0, "POL-2012": 615.0,
            "POL-2013": 480.0, "POL-2014": 810.0, "POL-2801": 700.0, "POL-2802": 547.5, "POL-2803": 730.0, "POL-2811": 795.0,
            "POL-2812": 560.0, "POL-2813": 590.0, "POL-2814": 630.0, "POL-2821": 575.0, "POL-2822": 540.0}
PLACED_BY = {"POL-2009": "BRK-7501", "POL-2010": "BRK-7501", "POL-2811": "BRK-7501", "POL-2812": "BRK-7502", "POL-2813": "BRK-7502",
             "POL-2814": "BRK-7503", "POL-2822": "BRK-7503"}


def build_policy_terms() -> list:
    """What servicing holds for a policy and the policy system does not: the annual premium and the broker who places it.
    A list of rows, not a second set of records keyed by policy id: the policy itself is held once."""
    return [{"policy_id": pid, "annual_premium": premium, "placed_by_broker": PLACED_BY.get(pid)}
            for pid, premium in PREMIUMS.items()]


def terms_of(data: dict, policy_id: str) -> dict:
    return next((t for t in data["sv_policy_terms"] if t["policy_id"] == policy_id), {})


def build_brokers() -> dict:
    def broker(bid, name, address, contact):
        return {"broker_id": bid, "name": name, "address": address, "contact": contact, "call_back_requests": []}

    rows = [broker("BRK-7501", "Pennywhistle & Crane Insurance Brokers", "2 Chandlers Quay, Port Ilvane, Meridia", "Aurelia Crane"),
            broker("BRK-7502", "Marlow Lantern Brokers Ltd", "17 Lamplighter Street, Marlow Reach, Meridia", "Ignace Bellwether"),
            broker("BRK-7503", "Thistle & Wren Broking", "4 Drovers Cross, Tallowby, Meridia", "Rosamund Wren")]
    return {b["broker_id"]: b for b in rows}


# ---------------------------------------------------------------- reading a policy

def find_policy(data: dict, policy_id: str):
    if policy_id in data["policies"]:
        return data["policies"][policy_id], "the policy system"
    if policy_id in data["sv_policies"]:
        return data["sv_policies"][policy_id], "this system"
    return None, None


def rating_area_of(address: str) -> dict | None:
    for town, code in RATING_AREAS.items():
        if town.lower() in (address or "").lower():
            return {"rating_area": code, "town": town}
    return None


def cover_on_date(policy: dict, on_iso: str, today_iso: str) -> dict:
    """cover_on of the policy system, with a sentence that fits a date after a period that has not ended yet."""
    answer = cover_on(policy, on_iso)
    end = policy["period_end"]
    if not answer["in_force"] and on_iso > end >= today_iso and not policy.get("cancelled_on"):
        days = _days(end, on_iso)
        answer = {**answer, "reason": f"The policy period ends on {long_date(end)} and no renewal is on record. "
                                      f"{long_date(on_iso)} is {plural(days, 'day')} after the end."}
    return answer


def last_day_of_cover(policy: dict) -> str:
    if policy.get("cancelled_on"):
        return _shift(policy["cancelled_on"], -1)
    return policy["period_end"]


def policy_as_it_stands(data: dict, policy_id: str, on_iso: str, today_iso: str) -> dict:
    """The policy on one date: cover, the schedule with every endorsement in effect on that date applied, and the rest."""
    p, held = find_policy(data, policy_id)
    schedule = copy.deepcopy(p["schedule"])
    parties = schedule.pop("interested_parties", [])
    in_effect, later, changed, waivers = [], [], [], []
    for e in sorted(p["endorsements"], key=lambda x: x["effective"]):
        row = {k: e[k] for k in ("endorsement_id", "title", "effective", "text")}
        if e["effective"] > on_iso:
            later.append(row)
            continue
        in_effect.append(row)
        for field, value in e.get("changes", {}).items():
            changed.append({"field": field, "label": FIELD_LABELS.get(field, field), "from": schedule[field], "to": value,
                            "endorsement_id": e["endorsement_id"], "effective": e["effective"],
                            "sentence": f"{e['endorsement_id']}, effective {long_date(e['effective'])}, changed the "
                                        f"{FIELD_LABELS.get(field, field)} from {usd(schedule[field])} to {usd(value)}."})
            schedule[field] = value
        if e.get("waiver_in_favour_of"):
            waivers.append(e["waiver_in_favour_of"])
    not_yet = [f"{e['endorsement_id']} takes effect on {long_date(e['effective'])}, after {long_date(on_iso)}: it is not applied."
               for e in later]
    terms = terms_of(data, policy_id)
    area = rating_area_of(p["address"])
    start, end = p["period_start"], p["period_end"]
    return {
        "policy_id": policy_id, "held_in": held, "on": on_iso, "product": p["product"], "holder": p["holder"], "address": p["address"],
        "rating_area": area["rating_area"] if area else None, "status": p["status"], "status_note": p.get("status_note", ""),
        "period_start": start, "period_end": end, "days_in_the_period": _days(start, end) + 1,
        "wording_id": p["wording_id"], "wording_version": p["wording_version"],
        "cover_on_the_date": {k: v for k, v in cover_on_date(p, on_iso, today_iso).items() if k in ("in_force", "reason")},
        "schedule_on_the_date": schedule, "interested_parties": parties,
        "endorsements_in_effect": in_effect, "endorsements_not_yet_in_effect": later,
        "changed_by_endorsement": changed, "not_yet_applied": not_yet,
        "waiver_of_rights_of_recovery": {
            "held": bool(waivers), "in_favour_of": waivers,
            "sentence": (f"An endorsement in effect waives rights of recovery against {', '.join(waivers)}." if waivers else
                         f"The wording {p['wording_id']} holds no waiver of rights of recovery, and no endorsement in effect on "
                         f"{long_date(on_iso)} adds one.")},
        "annual_premium": terms.get("annual_premium"), "placed_by_broker": terms.get("placed_by_broker"), "currency": "USD",
    }


def claims_on_policy(data: dict, policy_id: str) -> list:
    """Every claim on a policy with whether it is open. No amount, no reserve, no note."""
    rows = []
    for c in data["claims"].values():
        if c["policy_id"] != policy_id:
            continue
        declined = (c.get("decision") or {}).get("decision") == "declined"
        is_open = c["status"] != "closed" and not declined
        rows.append({"claim_id": c["claim_id"], "date_of_loss": c["loss_date"], "open": is_open, "held_in": "the claims system"})
    for c in data["sv_claims"].values():
        if c["policy_id"] == policy_id:
            rows.append({"claim_id": c["claim_id"], "date_of_loss": c["loss_date"], "open": c["stage"] not in ("closed", "declined"),
                         "held_in": "this system"})
    return rows


# ---------------------------------------------------------------- the sums: premium pro rata and gaps in cover

def premium_pro_rata(policy: dict, present_annual: float | None, new_annual: float, effective_iso: str) -> dict:
    start, end = policy["period_start"], policy["period_end"]
    base = {"worked_out": False, "kind": "not_worked_out", "amount": None, "present_annual_premium": present_annual,
            "new_annual_premium": new_annual, "currency": "USD"}
    if present_annual is None:
        return {**base, "working": "", "note": f"Servicing holds no annual premium for {policy['policy_id']}. Nothing was worked out."}
    if not start <= effective_iso <= end:
        return {**base, "working": "", "note": f"{long_date(effective_iso)} is outside the policy period, {long_date(start)} to "
                                               f"{long_date(end)}. Nothing was worked out."}
    in_period = _days(start, end) + 1
    remaining = _days(effective_iso, end) + 1
    difference = money(new_annual - present_annual)
    amount = money(abs(difference) * remaining / in_period)
    kind = "additional_premium" if difference > 0 else ("return_premium" if difference < 0 else "no_change")
    working = (f"{new_annual:,.2f} - {present_annual:,.2f} = {difference:,.2f} a year. {remaining} of {in_period} days remain, from "
               f"{long_date(effective_iso)} to {long_date(end)}, both included. {abs(difference):,.2f} x {remaining} / {in_period} = "
               f"{amount:,.2f}.")
    note = {"additional_premium": f"An additional premium of {usd(amount)} for the rest of the period.",
            "return_premium": f"A return premium of {usd(amount)} for the rest of the period.",
            "no_change": "The annual premium does not change, so nothing is charged or returned."}[kind]
    return {**base, "worked_out": True, "kind": kind, "amount": amount, "difference_a_year": difference,
            "days_in_the_period": in_period, "days_remaining": remaining, "counted_from": effective_iso, "counted_to": end,
            "working": working, "note": note}


def return_premium_on_cancellation(policy: dict, annual: float | None, cancel_on_iso: str, open_claims: list) -> dict:
    start, end = policy["period_start"], policy["period_end"]
    base = {"worked_out": False, "kind": "not_worked_out", "amount": None, "present_annual_premium": annual, "new_annual_premium": None,
            "currency": "USD"}
    if open_claims:
        ids = ", ".join(c["claim_id"] for c in open_claims)
        return {**base, "working": "", "note": f"The policy has an open claim ({ids}). Under rule SR-4 no return premium is worked "
                                               "out until the servicing team leader has decided."}
    if annual is None:
        return {**base, "working": "", "note": f"Servicing holds no annual premium for {policy['policy_id']}. Nothing was worked out."}
    if not start <= cancel_on_iso <= end:
        return {**base, "working": "", "note": f"{long_date(cancel_on_iso)} is outside the policy period, {long_date(start)} to "
                                               f"{long_date(end)}. Nothing was worked out."}
    in_period = _days(start, end) + 1
    after = _days(cancel_on_iso, end)
    amount = money(annual * after / in_period)
    working = (f"Cover ends at the end of {long_date(cancel_on_iso)}. {after} of {in_period} days are left after that date, up to "
               f"{long_date(end)}. {annual:,.2f} x {after} / {in_period} = {amount:,.2f}.")
    return {**base, "worked_out": True, "kind": "return_premium", "amount": amount, "days_in_the_period": in_period,
            "days_remaining": after, "counted_from": _shift(cancel_on_iso, 1) if after else None, "counted_to": end,
            "working": working, "note": f"A return premium of {usd(amount)} for the days after the cancellation date."}


def gap_between(cover_ends_iso: str, new_cover_starts_iso: str) -> dict:
    """Days without cover between the last day of one cover and the first day of the next."""
    without = _days(cover_ends_iso, new_cover_starts_iso) - 1
    base = {"checked": True, "cover_ends_on": cover_ends_iso, "new_cover_starts_on": new_cover_starts_iso}
    if without > 0:
        first, last = _shift(cover_ends_iso, 1), _shift(new_cover_starts_iso, -1)
        span = long_date(first) if first == last else f"{long_date(first)} to {long_date(last)}"
        return {**base, "gap_in_cover": True, "days_without_cover": without, "first_day_without_cover": first,
                "last_day_without_cover": last, "days_of_overlap": 0,
                "sentence": f"Cover ends at the end of {long_date(cover_ends_iso)} and new cover starts on "
                            f"{long_date(new_cover_starts_iso)}. That leaves {plural(without, 'day')} without cover: {span}."}
    overlap = -without
    sentence = (f"Cover ends at the end of {long_date(cover_ends_iso)} and new cover starts on {long_date(new_cover_starts_iso)}, "
                "the day after. There is no day without cover." if overlap == 0 else
                f"New cover starts on {long_date(new_cover_starts_iso)}, on or before the last day of cover, "
                f"{long_date(cover_ends_iso)}. There is no day without cover; the two covers overlap by {plural(overlap, 'day')}.")
    return {**base, "gap_in_cover": False, "days_without_cover": 0, "first_day_without_cover": None, "last_day_without_cover": None,
            "days_of_overlap": overlap, "sentence": sentence}


def age_on(date_of_birth_iso: str, on_iso: str) -> int:
    born, on = date.fromisoformat(date_of_birth_iso), date.fromisoformat(on_iso)
    return on.year - born.year - ((on.month, on.day) < (born.month, born.day))


# ---------------------------------------------------------------- change requests

def build_change_requests(today: date) -> dict:
    out = {}

    def add(cid, received_ago, policy_id, name, role, channel, change_type, effective, details, text, rating=None):
        out[cid] = {"change_request_id": cid, "status": "received", "received": d_ago(today, received_ago), "policy_id": policy_id,
                    "requested_by": {"name": name, "role": role, "channel": channel}, "change_type": change_type,
                    "change_type_label": CHANGE_TYPES[change_type], "effective_date": effective, "details": details,
                    "rating": rating, "text": text, "change_drafts": [], "endorsement_drafts": []}

    e = d_ahead(today, 7)
    add("CHG-7301", 1, "POL-2001", "Corwin Ashgrove", "policyholder", "web form", "address", e,
        {"new_address": "22 Larchfield Row, Marlow Reach, Meridia"},
        f"Please change my address from 14 Larchfield Row to 22 Larchfield Row, Marlow Reach, from {long_date(e)}. The car is kept "
        "on the drive as before. Corwin Ashgrove")
    e = d_ahead(today, 14)
    add("CHG-7302", 2, "POL-2006", "Henrietta Quillby", "policyholder", "email", "address", e,
        {"new_address": "8 Capstan Yard, Port Ilvane, Meridia"},
        f"I am moving from 61 Thistledown Close, Tallowby to 8 Capstan Yard, Port Ilvane on {long_date(e)}. Please move my home "
        "policy to the new address from that date. Henrietta Quillby")
    e = d_ahead(today, 7)
    add("CHG-7303", 1, "POL-2012", "Elric Stannaway", "policyholder", "email", "sum_insured", e,
        {"field": "contents_sum_insured", "new_sum_insured": 50000.0},
        f"Please raise my contents sum insured from 40,000.00 to 50,000.00 from {long_date(e)}. We have bought new furniture. "
        "Elric Stannaway")
    e = d_ago(today, 22)
    add("CHG-7304", 2, "POL-2801", "Ottoline Merrivale", "policyholder", "telephone note", "add_driver", e,
        {"driver_name": "Corvin Merrivale", "date_of_birth": "1981-03-09"},
        f"Call taken by the servicing desk. Mrs Merrivale asks to add her husband, Corvin Merrivale, born 9 Mar 1981, as a named "
        f"driver from {long_date(e)}. She says he has driven the car since that date.")
    e = d_ahead(today, 4)
    add("CHG-7305", 1, "POL-2005", "Bram Tollermoor", "policyholder", "web form", "cancellation", e,
        {"cancel_on": e, "replacement_cover_starts": None, "reason_given": "The policyholder is selling the car."},
        f"Please cancel my motor policy POL-2005 on {long_date(e)}. I am selling the car. Bram Tollermoor")
    e, start = d_ahead(today, 10), d_ahead(today, 15)
    add("CHG-7306", 1, "POL-2802", "Cordelia Ravenscar", "policyholder", "email", "cancellation", e,
        {"cancel_on": e, "replacement_cover_starts": start, "reason_given": "A new policy with another insurer."},
        f"Please cancel my home policy POL-2802 on {long_date(e)}. My new policy with another insurer starts on {long_date(start)}. "
        "Cordelia Ravenscar")
    e = d_ahead(today, 5)
    add("CHG-7307", 1, "POL-2803", "Florian Tredwell", "policyholder", "web form", "vehicle", e,
        {"new_vehicle": "Halden Crest 2.0 estate, 2025", "new_registration": "MR-5068-N", "new_sum_insured": 21000.0},
        f"I have changed my car. Please move the policy from the Vesper Lane 1.4 hatchback, registration MR-2291-C, to a Halden "
        f"Crest 2.0 estate, 2025, registration MR-5068-N, from {long_date(e)}. Florian Tredwell",
        rating={"quote_id": "RQ-7307", "new_annual_premium": 912.5, "note": "From the rating engine, for the new vehicle."})
    e = d_ahead(today, 3)
    add("CHG-7308", 1, "POL-2011", "Isaura Venn", "policyholder", "email", "sum_insured", e,
        {"field": "sum_insured", "new_sum_insured": 23400.0},
        f"Please raise the sum insured on my car from 19,500.00 to 23,400.00 from {long_date(e)}. A valuation came in higher. "
        "Isaura Venn",
        rating={"quote_id": "RQ-7308", "new_annual_premium": 913.0, "note": "From the rating engine, for the new sum insured."})
    return out


def measure_change(change: dict, data: dict, today_iso: str) -> dict:
    """One change request measured against the servicing rules, with the premium adjustment and the gap check."""
    pid, kind, eff, det = change["policy_id"], change["change_type"], change["effective_date"], change["details"]
    p, _held = find_policy(data, pid)
    stands = policy_as_it_stands(data, pid, eff, today_iso)
    schedule = stands["schedule_on_the_date"]
    annual = stands["annual_premium"]
    claims = claims_on_policy(data, pid)
    open_claims = [c for c in claims if c["open"]]

    before_receipt = max(_days(eff, change["received"]), 0)
    before_today = max(_days(eff, today_iso), 0)
    dates = {"received": change["received"], "effective_date": eff, "insurer_date": today_iso,
             "days_effective_date_is_before_the_date_received": before_receipt,
             "effective_date_is_before_the_insurer_date": before_today > 0, "days_before_the_insurer_date": before_today,
             "sentence": (f"The effective date, {long_date(eff)}, is {plural(before_today, 'day')} before the insurer date, "
                          f"{long_date(today_iso)}: the change would reach back over days that have passed." if before_today else
                          f"The effective date, {long_date(eff)}, is not before the insurer date, {long_date(today_iso)}.")}

    rules = []

    def rule(rule_id, applies, measured, limit, sentence):
        rules.append({"rule_id": rule_id, "heading": SERVICING_RULES[rule_id]["heading"], "applies": applies, "measured": measured,
                      "limit": limit, "sends_to": SERVICING_RULES[rule_id]["sends_to"] if applies else "", "sentence": sentence})

    # SR-1 backdating
    over = before_receipt - BACKDATING_DAYS
    rule("SR-1", over > 0, f"{plural(before_receipt, 'day')} before the date received", f"{BACKDATING_DAYS} days",
         (f"The effective date, {long_date(eff)}, is {plural(before_receipt, 'day')} before the date the request was received, "
          f"{long_date(change['received'])}. That is {plural(over, 'day')} more than the {BACKDATING_DAYS} days allowed." if over > 0 else
          f"The effective date, {long_date(eff)}, is {plural(before_receipt, 'day')} before the date the request was received, "
          f"{long_date(change['received'])}. That is within the {BACKDATING_DAYS} days allowed." if before_receipt else
          f"The effective date, {long_date(eff)}, is not before the date the request was received, "
          f"{long_date(change['received'])}."))

    # what changes, and SR-2, SR-3, SR-5
    what = {"change_type": kind}
    same_area = None
    if kind == "address":
        now_area, new_area = rating_area_of(p["address"]), rating_area_of(det["new_address"])
        same_area = bool(now_area and new_area and now_area["rating_area"] == new_area["rating_area"])
        what.update({"present_address": p["address"], "present_rating_area": now_area and now_area["rating_area"],
                     "new_address": det["new_address"], "new_rating_area": new_area and new_area["rating_area"],
                     "same_rating_area": same_area})
        a, b = what["present_rating_area"], what["new_rating_area"]
        rule("SR-2", not same_area, f"{a} to {b}", "the same rating area",
             f"The present address is in rating area {a} and the new address is in rating area {b}. "
             + ("They are the same area: no re-rating is needed and the premium does not change." if same_area else
                "They are different areas: underwriting re-rates the policy before the change is made."))
    else:
        rule("SR-2", False, "", "the same rating area", "The request is not a change of address.")
    if kind == "sum_insured":
        field = det["field"]
        present, new = schedule[field], det["new_sum_insured"]
        increase = money(new - present)
        percent = round(increase / present * 100 + 1e-9, 2) if present else 0.0
        what.update({"field": field, "label": FIELD_LABELS.get(field, field), "present_sum_insured": present,
                     "new_sum_insured": new, "increase": increase, "increase_percent": percent})
        fires = percent > SUM_INSURED_INCREASE_PERCENT
        rule("SR-3", fires, f"{percent:.2f} percent", f"{SUM_INSURED_INCREASE_PERCENT:.2f} percent",
             f"The {FIELD_LABELS.get(field, field)} goes from {usd(present)} to {usd(new)}: an increase of {usd(increase)}, "
             f"{percent:.2f} percent of the present sum insured. "
             + (f"That is more than {SUM_INSURED_INCREASE_PERCENT:.0f} percent." if fires else
                f"That is not more than {SUM_INSURED_INCREASE_PERCENT:.0f} percent"
                + (": it is exactly on the limit, and the rule does not apply." if percent == SUM_INSURED_INCREASE_PERCENT else ".")))
    else:
        rule("SR-3", False, "", f"{SUM_INSURED_INCREASE_PERCENT:.2f} percent", "The request is not an increase in a sum insured.")
    # SR-4 cancellation with an open claim
    if kind == "cancellation":
        what.update({"cancel_on": det["cancel_on"], "last_day_of_cover": det["cancel_on"],
                     "replacement_cover_starts": det.get("replacement_cover_starts")})
        ids = ", ".join(c["claim_id"] for c in open_claims)
        rule("SR-4", bool(open_claims), plural(len(open_claims), "open claim"), "no open claim",
             f"The policy has {plural(len(open_claims), 'open claim')}" + (f" ({ids})." if open_claims else "."))
    else:
        rule("SR-4", False, "", "no open claim", "The request is not a cancellation.")
    if kind == "add_driver":
        age = age_on(det["date_of_birth"], eff)
        what.update({"driver_name": det["driver_name"], "date_of_birth": det["date_of_birth"], "age_on_the_effective_date": age,
                     "named_drivers_now": schedule.get("named_drivers", [])})
        rule("SR-5", age < YOUNG_DRIVER_AGE, f"{age} years", f"{YOUNG_DRIVER_AGE} years",
             f"{det['driver_name']} is {age} on {long_date(eff)}, which is "
             + ("under" if age < YOUNG_DRIVER_AGE else "not under") + f" {YOUNG_DRIVER_AGE}.")
    else:
        rule("SR-5", False, "", f"{YOUNG_DRIVER_AGE} years", "The request does not add a driver.")
    if kind == "vehicle":
        what.update({"present_vehicle": schedule.get("insured_vehicle"), "present_registration": schedule.get("registration"),
                     "present_sum_insured": schedule.get("sum_insured"), "new_vehicle": det["new_vehicle"],
                     "new_registration": det["new_registration"], "new_sum_insured": det["new_sum_insured"]})
    cover = stands["cover_on_the_date"]
    rule("SR-8", not cover["in_force"], "in force" if cover["in_force"] else "not in force", "in force on the effective date",
         cover["reason"])

    # premium adjustment (SR-6)
    rating = change.get("rating")
    if kind == "cancellation":
        premium = return_premium_on_cancellation(p, annual, det["cancel_on"], open_claims)
    elif kind == "address" and same_area:
        premium = {**premium_pro_rata(p, annual, annual, eff), "note": "The new address is in the same rating area, so the annual "
                                                                        "premium does not change: nothing is charged or returned."}
    elif kind == "address":
        premium = {"worked_out": False, "kind": "not_worked_out", "amount": None, "present_annual_premium": annual,
                   "new_annual_premium": None, "currency": "USD", "working": "",
                   "note": "The new address is in another rating area. Under rule SR-2 no premium adjustment is worked out until "
                           "underwriting has re-rated the policy."}
    elif rating:
        premium = premium_pro_rata(p, annual, rating["new_annual_premium"], eff)
    else:
        premium = {"worked_out": False, "kind": "not_worked_out", "amount": None, "present_annual_premium": annual,
                   "new_annual_premium": None, "currency": "USD", "working": "",
                   "note": "The request carries no new annual premium from the rating engine, so no adjustment is worked out."}

    # gap in cover (SR-7)
    if kind == "cancellation" and det.get("replacement_cover_starts"):
        gap = gap_between(det["cancel_on"], det["replacement_cover_starts"])
    elif kind == "cancellation":
        gap = {"checked": False, "gap_in_cover": None, "days_without_cover": None, "cover_ends_on": det["cancel_on"],
               "new_cover_starts_on": None,
               "sentence": f"Cover would end at the end of {long_date(det['cancel_on'])}. The request names no new cover, so no gap "
                           "can be measured."}
    else:
        gap = {"checked": False, "gap_in_cover": False, "days_without_cover": 0, "cover_ends_on": None, "new_cover_starts_on": None,
               "sentence": "The request ends no cover, so there is no gap between two covers to measure."}
    points = []
    if gap.get("gap_in_cover"):
        points.append(gap["sentence"])
    if before_today:
        points.append(dates["sentence"])

    applying = [r["rule_id"] for r in rules if r["applies"]]
    refer_to = []
    if any(r in UNDERWRITING_RULES for r in applying):
        refer_to.append("underwriting")
    if any(r in TEAM_LEADER_RULES for r in applying):
        refer_to.append("the servicing team leader")
    next_step = ("refer_to_underwriting" if "underwriting" in refer_to else
                 "refer_to_the_team_leader" if refer_to else "ready_for_the_servicing_officer")
    return {"policy_as_it_stands_on_the_effective_date": stands, "claims_on_the_policy": claims, "open_claims": len(open_claims),
            "dates": dates, "what_changes": what, "rules": rules, "rules_that_apply": applying, "referral_needed": bool(refer_to),
            "refer_to": refer_to, "next_step_by_the_rules": next_step, "premium_adjustment": premium, "gap_in_cover": gap,
            "points_to_raise_by_rule_sr_7": points}


# ---------------------------------------------------------------- certificates and endorsements

def _paragraphs(rows):
    return [{"number": str(n), "text": text} for n, text in enumerate(rows, start=1)]


CERTIFICATE_TEMPLATE = {
    "template_id": "CT-COI-1", "title": "Certificate of insurance", "version": "2",
    "how_to_use": "Fill each paragraph from the policy as it stands on the certificate date, as "
                  "get_policy_as_it_stands_on_date and get_certificate_request give it. Words in square brackets are filled in. "
                  "Paragraph 7 is copied word for word. A certificate shows only what the policy holds on the certificate date: "
                  "never a limit, a party or a waiver the policy does not hold. A servicing officer issues it; a draft is not "
                  "a certificate.",
    "paragraphs": _paragraphs([
        "CERTIFICATE OF INSURANCE. Thornmere Mutual Insurance, Meridia. Certificate date: [CERTIFICATE DATE].",
        "Certificate holder: [NAME AND ADDRESS OF THE CERTIFICATE HOLDER].",
        "Insured: [POLICYHOLDER AND ADDRESS]. Policy number: [POLICY NUMBER]. Policy wording: [WORDING ID AND VERSION].",
        "Period of insurance: [PERIOD START] to [PERIOD END], both days included. The policy is in force on the certificate date.",
        "Cover and limits on the certificate date: [EACH ITEM THE REQUEST ASKS TO BE SHOWN, WITH THE FIGURE FROM THE SCHEDULE AS "
        "IT STANDS ON THE CERTIFICATE DATE].",
        "Endorsements in effect on the certificate date: [EACH ENDORSEMENT ID AND TITLE, OR None].",
        "This certificate is issued as information only. It gives the certificate holder no rights under the policy. It does not "
        "change, extend or alter the cover given by the policy, which is subject to the terms, conditions and exclusions of the "
        "policy wording.",
    ]),
}


def _endorsement(tid, change_type, title, change_paragraph):
    return {"template_id": tid, "for_change_type": change_type, "title": title, "paragraphs": _paragraphs([
        "ENDORSEMENT to policy [POLICY NUMBER], held by [POLICYHOLDER]. Effective date: [EFFECTIVE DATE].",
        change_paragraph,
        "Premium: [THE ADDITIONAL PREMIUM OR RETURN PREMIUM AS THE SYSTEM WORKS IT OUT, WITH ITS WORKING, OR No change in premium, "
        "OR To be worked out after referral].",
        "All other terms, conditions and exclusions of the policy are unchanged. This endorsement changes the policy only when a "
        "servicing officer has issued it.",
    ])}


ENDORSEMENT_TEMPLATES = {t["template_id"]: t for t in [
    _endorsement("ET-ADDRESS", "address", "Change of address",
                 "From the effective date the address in the schedule is [NEW ADDRESS] in place of [PRESENT ADDRESS]."),
    _endorsement("ET-VEHICLE", "vehicle", "Change of vehicle",
                 "From the effective date the insured vehicle is [NEW VEHICLE], registration [NEW REGISTRATION], sum insured [NEW SUM "
                 "INSURED], in place of [PRESENT VEHICLE], registration [PRESENT REGISTRATION]."),
    _endorsement("ET-SUM-INSURED", "sum_insured", "Change of sum insured",
                 "From the effective date the [NAME OF THE SUM INSURED] is [NEW SUM INSURED] in place of [PRESENT SUM INSURED]."),
    _endorsement("ET-DRIVER", "add_driver", "Added driver",
                 "From the effective date [DRIVER NAME], born [DATE OF BIRTH], is named as a driver in the schedule."),
    _endorsement("ET-CANCELLATION", "cancellation", "Cancellation",
                 "The policy is cancelled at the end of [CANCELLATION DATE]. No cover is given after that date."),
]}
ENDORSEMENT_HOW_TO_USE = ("One template for each kind of change. Fill each paragraph from the change request and from the policy "
                          "as it stands on the effective date. Words in square brackets are filled in. Paragraph 4 is copied word "
                          "for word. A figure in paragraph 3 is the system's own figure, never one worked out by hand. A draft "
                          "endorsement changes nothing: a servicing officer issues it.")


def build_certificate_requests(today: date) -> dict:
    out = {}
    iso_today = today.isoformat()

    def add(rid, received_ago, policy_id, requested_by, holder_name, holder_address, certificate_date, must_show, text):
        items = [{"item_id": f"{rid}-{chr(65 + n)}", **item} for n, item in enumerate(must_show)]
        out[rid] = {"certificate_request_id": rid, "status": "received", "received": d_ago(today, received_ago),
                    "policy_id": policy_id, "requested_by": requested_by,
                    "certificate_holder": {"name": holder_name, "address": holder_address}, "certificate_date": certificate_date,
                    "must_show": items, "text": text, "certificate_drafts": []}

    def limit(field, amount=None):
        return {"kind": "limit", "field": field, "label": FIELD_LABELS[field], "asked_amount": amount}

    add("CRQ-7401", 1, "POL-2002", "Elspeth Marrowdene, policyholder", "Weavers Yard Mutual Loan Society",
        "5 Shuttle Lane, Tallowby, Meridia", iso_today, [limit("buildings_sum_insured")],
        f"My lender asks for a certificate of my home insurance, dated {long_date(iso_today)}, that shows the buildings sum insured "
        "and the period. Please address it to Weavers Yard Mutual Loan Society, 5 Shuttle Lane, Tallowby. Elspeth Marrowdene")
    add("CRQ-7402", 1, "POL-2014", "Ansel Whitlocke, policyholder", "Beaconside Parcel Depot Ltd",
        "Unit 3, Signal Yard, Marlow Reach, Meridia", iso_today, [limit("third_party_property_limit", 1000000.0)],
        f"The depot where I park for work asks for a certificate dated {long_date(iso_today)} that shows a third party property "
        "limit of 1,000,000.00. Please address it to Beaconside Parcel Depot Ltd, Unit 3, Signal Yard, Marlow Reach. Ansel Whitlocke")
    add("CRQ-7403", 2, "POL-2001", "Corwin Ashgrove, policyholder", "Larchfield Quarry Company Ltd",
        "Quarry Gate, Marlow Reach, Meridia", iso_today, [limit("third_party_property_limit", 2000000.0)],
        f"The quarry I deliver to needs a certificate dated {long_date(iso_today)} that shows a third party property limit of "
        "2,000,000.00. Please address it to Larchfield Quarry Company Ltd, Quarry Gate, Marlow Reach. Corwin Ashgrove")
    add("CRQ-7404", 1, "POL-2821", "Seraphina Dunmallow, policyholder", "Saltcombe Property Management Ltd",
        "40 Tithe Barn Road, Tallowby, Meridia", iso_today,
        [limit("buildings_sum_insured"), {"kind": "interested_party", "party_name": "Saltcombe Property Management Ltd"}],
        f"Please send a certificate dated {long_date(iso_today)} to Saltcombe Property Management Ltd, 40 Tithe Barn Road, Tallowby. "
        "It must show the buildings sum insured and name Saltcombe Property Management Ltd as an additional insured. "
        "Seraphina Dunmallow")
    later = d_ahead(today, 180)
    add("CRQ-7405", 1, "POL-2012", "Elric Stannaway, policyholder", "Otterburn Residents Company Ltd",
        "1 Otterburn Gardens, Tallowby, Meridia", later, [limit("buildings_sum_insured")],
        f"The residents company asks for a certificate that shows my home is insured on {long_date(later)}, with the buildings sum "
        "insured. Please address it to Otterburn Residents Company Ltd, 1 Otterburn Gardens, Tallowby. Elric Stannaway")
    earlier = d_ago(today, 45)
    add("CRQ-7406", 2, "POL-2822", "Barnabas Thrupp, policyholder", "Kittiwake Lettings Ltd",
        "19 Gannet Street, Tallowby, Meridia", earlier, [limit("contents_sum_insured")],
        f"My letting agent asks for proof of the contents cover I held on {long_date(earlier)}, the date of the inventory. Please "
        f"send a certificate as at {long_date(earlier)} that shows the contents sum insured, to Kittiwake Lettings Ltd, 19 Gannet "
        "Street, Tallowby. Barnabas Thrupp")
    add("CRQ-7407", 1, "POL-2011", "Isaura Venn, policyholder", "Candlewick Parking Company Ltd",
        "Candlewick Street Car Park, Marlow Reach, Meridia", iso_today,
        [limit("sum_insured"), {"kind": "waiver_of_recovery", "party_name": "Candlewick Parking Company Ltd"}],
        f"The car park I use asks for a certificate dated {long_date(iso_today)} that shows the sum insured for my car and says that "
        "Thornmere waives its rights of recovery against Candlewick Parking Company Ltd. Isaura Venn")
    return out


def check_certificate_request(req: dict, data: dict, today_iso: str) -> dict:
    """Each thing the request asks to be shown, set against the policy as it stands on the certificate date."""
    on = req["certificate_date"]
    stands = policy_as_it_stands(data, req["policy_id"], on, today_iso)
    schedule = stands["schedule_on_the_date"]
    cover = stands["cover_on_the_date"]
    rows, differences = [], []
    rows.append({"item_id": "COVER", "kind": "cover_on_the_certificate_date",
                 "result": "in_force_on_the_date" if cover["in_force"] else "not_in_force_on_the_date",
                 "asked": f"cover on {long_date(on)}", "the_policy_holds": cover["in_force"], "sentence": cover["reason"]})
    if not cover["in_force"]:
        differences.append(f"The policy is not in force on the certificate date. {cover['reason']}")
    for item in req["must_show"]:
        kind = item["kind"]
        if not cover["in_force"]:
            # Outside the period the policy gives nothing on that date: no figure, party or waiver is set beside the request.
            asked = (item.get("asked_amount") if kind == "limit" else item["party_name"] if kind == "interested_party"
                     else f"a waiver of rights of recovery against {item['party_name']}")
            row = {"item_id": item["item_id"], "kind": kind}
            if kind == "limit":
                row.update({"field": item["field"], "label": item["label"]})
            rows.append({**row, "result": "not_in_force_on_the_date", "asked": asked, "the_policy_holds": None,
                         "sentence": f"The policy is not in force on {long_date(on)}, so it gives nothing to show for this item "
                                     "on that date."})
            continue
        if kind == "limit":
            holds, asked, label = schedule.get(item["field"]), item.get("asked_amount"), item["label"]
            if holds is None:
                result, sentence = "not_on_the_policy", f"The schedule holds no {label}."
            elif asked is None:
                result, sentence = "shown_from_the_policy", (f"The request names no figure. On {long_date(on)} the schedule gives a "
                                                             f"{label} of {usd(holds)}.")
            elif asked == holds:
                result, sentence = "matches_the_policy", (f"The request asks for a {label} of {usd(asked)}. On {long_date(on)} the "
                                                          f"schedule gives {usd(holds)}: the same.")
            elif asked > holds:
                result, sentence = "higher_than_the_policy", (f"The request asks for a {label} of {usd(asked)}. On {long_date(on)} "
                                                              f"the schedule gives {usd(holds)}: the request is "
                                                              f"{usd(money(asked - holds))} higher than the policy.")
            else:
                result, sentence = "lower_than_the_policy", (f"The request asks for a {label} of {usd(asked)}. On {long_date(on)} "
                                                             f"the schedule gives {usd(holds)}: the policy gives "
                                                             f"{usd(money(holds - asked))} more than the request.")
            rows.append({"item_id": item["item_id"], "kind": kind, "field": item["field"], "label": label, "result": result,
                         "asked": asked, "the_policy_holds": holds, "sentence": sentence})
        elif kind == "interested_party":
            parties = stands["interested_parties"]
            on_policy = item["party_name"] in parties
            sentence = (f"{item['party_name']} is named in the schedule as an interested party." if on_policy else
                        f"{item['party_name']} is not named on the policy. The schedule names "
                        + (", ".join(parties) if parties else "no interested party") + ".")
            rows.append({"item_id": item["item_id"], "kind": kind, "result": "matches_the_policy" if on_policy else "not_on_the_policy",
                         "asked": item["party_name"], "the_policy_holds": parties, "sentence": sentence})
        else:  # waiver_of_recovery
            waiver = stands["waiver_of_rights_of_recovery"]
            held = item["party_name"] in waiver["in_favour_of"]
            rows.append({"item_id": item["item_id"], "kind": kind, "result": "matches_the_policy" if held else "not_on_the_policy",
                         "asked": f"a waiver of rights of recovery against {item['party_name']}",
                         "the_policy_holds": waiver["in_favour_of"], "sentence": waiver["sentence"]})
        if rows[-1]["result"] not in ("matches_the_policy", "shown_from_the_policy"):
            differences.append(rows[-1]["sentence"])
    as_asked = not differences
    return {"certificate_date": on, "rows": rows, "can_be_prepared_as_asked": as_asked, "differences": differences,
            "sentence": ("Everything the request asks to be shown is on the policy as it stands on the certificate date." if as_asked
                         else f"The certificate cannot be prepared as asked: {plural(len(differences), 'point')} of the request "
                              "is not what the policy holds on the certificate date. A servicing officer decides what happens next."),
            "policy_as_it_stands_on_the_certificate_date": stands}


# ---------------------------------------------------------------- the broker desk

def build_servicing_claims(today: date) -> dict:
    """Claims the broker desk is asked about. The whole record is internal; claim_for_broker gives what a broker may be told."""
    def claim(cid, policy_id, claimant, label, loss_ago, reported_ago, stage, outstanding, reserve, payments=None, referral=None,
              notes=None):
        return {"claim_id": cid, "policy_id": policy_id, "claimant": claimant, "claim_type_label": label,
                "loss_date": d_ago(today, loss_ago), "reported_date": d_ago(today, reported_ago), "stage": stage,
                "outstanding_items": outstanding, "reserve": reserve, "payments": payments or [], "internal_referral": referral,
                "internal_notes": notes or [], "decision": None, "currency": "USD"}

    rows = [
        claim("SCL-7801", "POL-2811", "Jocasta Wimberry", "Motor: damage to the insured vehicle", 20, 19, "part_paid",
              ["The repairer's final invoice."], 1450.0,
              payments=[{"date": d_ago(today, 7), "amount": 1800.0, "paid_to": "Harbour Lane Coachworks",
                         "paid_for": "Interim payment on the repair."}],
              notes=[{"date": d_ago(today, 8), "by": "Ottilie Marsh", "text": "Interim payment agreed with the repairer. Reserve "
                                                                             "kept for the rest of the repair."}]),
        claim("SCL-7802", "POL-2812", "Leopold Quenningbrook", "Home: theft", 12, 11, "referred_to_investigations",
              ["Receipts for the jewellery."], 9500.0,
              referral={"referred_on": d_ago(today, 5), "referred_by": "Lucan Thirlby, claims handler",
                        "to": "the investigations desk", "reason": "Fraud indicator FI-1: an early loss."},
              notes=[{"date": d_ago(today, 5), "by": "Lucan Thirlby", "text": "Referred to the investigations desk. Nothing is "
                                                                             "paid and nothing is said outside the claims team."}]),
        claim("SCL-7803", "POL-2813", "Philomena Ashcombe", "Home: escape of water", 9, 8, "waiting_for_documents",
              ["The plumber's report on where the water came from."], 6200.0,
              notes=[{"date": d_ago(today, 6), "by": "Ottilie Marsh", "text": "Plumber's report asked for. Reserve set from the "
                                                                             "repair estimate."}]),
        claim("SCL-7804", "POL-2814", "Wystan Harcastle", "Home: storm", 6, 5, "in_assessment", [], 12000.0,
              notes=[{"date": d_ago(today, 3), "by": "Ottilie Marsh", "text": "A loss adjuster is appointed. No date for the "
                                                                             "visit is set yet."}]),
    ]
    return {c["claim_id"]: c for c in rows}


def build_broker_queries(today: date) -> dict:
    def q(qid, broker_id, asked_by, received_ago, text):
        return {"query_id": qid, "broker_id": broker_id, "asked_by": asked_by, "received": d_ago(today, received_ago), "text": text}

    rows = [
        q("BQ-7601", "BRK-7501", "Aurelia Crane", 0, "Where does claim SCL-7801 for Jocasta Wimberry stand, and what is still needed?"),
        q("BQ-7602", "BRK-7501", "Aurelia Crane", 0, "Is POL-2009 for Teodor Brackwell in force, and what is the deductible?"),
        q("BQ-7603", "BRK-7503", "Rosamund Wren", 0, "Can you tell me where claim SCL-7803 stands?"),
        q("BQ-7604", "BRK-7502", "Ignace Bellwether", 0, "What reserve do you hold on claim SCL-7803 for Philomena Ashcombe?"),
        q("BQ-7605", "BRK-7502", "Ignace Bellwether", 0, "Claim SCL-7802 for Leopold Quenningbrook has not been paid. Why not, and "
                                                         "what is holding it up?"),
        q("BQ-7606", "BRK-7503", "Rosamund Wren", 0, "On claim SCL-7804 for Wystan Harcastle, on what date will the loss adjuster "
                                                     "visit the house?"),
        q("BQ-7607", "BRK-7501", "Aurelia Crane", 0, "What was decided on claim CLM-4010 for Yvaine Corrimond?"),
        q("BQ-7608", "BRK-7502", "Ignace Bellwether", 0, "Please send me the schedule of POL-2009."),
    ]
    return {r["query_id"]: r for r in rows}


HELD_BACK_FROM_A_BROKER = ["the reserve and any estimate of what the claim will cost", "handlers' notes and other internal notes",
                           "anything about an internal review of the file"]
STAGE_WORDS = {"reported": "The claim is reported and not yet assessed.",
               "waiting_for_documents": "The claim is waiting for documents.",
               "under_review": "The claim is under review.",
               "part_paid": "A payment has been made and the claim is still open.",
               "decided": "A decision is recorded on the claim.",
               "paid": "The claim is paid and closed."}


def book_of(data: dict, broker_id: str) -> list:
    return [t["policy_id"] for t in data["sv_policy_terms"] if t["placed_by_broker"] == broker_id]


def find_claim(data: dict, claim_id: str):
    if claim_id in data["sv_claims"]:
        return data["sv_claims"][claim_id], "this system"
    if claim_id in data["claims"]:
        return data["claims"][claim_id], "the claims system"
    return None, None


def claim_for_broker(data: dict, claim_id: str) -> dict:
    """What a broker may be told about a claim: the stage, what is outstanding, the last payment and a recorded decision.
    Never the reserve, a note, or anything about an internal review. A claim under an internal referral reads exactly like
    any other claim under review."""
    c, held = find_claim(data, claim_id)
    decision = None
    if held == "this system":
        stage = {"waiting_for_documents": "waiting_for_documents", "in_assessment": "under_review",
                 "referred_to_investigations": "under_review", "part_paid": "part_paid", "closed": "paid",
                 "declined": "decided"}[c["stage"]]
        outstanding = list(c["outstanding_items"]) if stage in ("waiting_for_documents", "part_paid") else []
    else:
        recorded = c.get("decision") or {}
        declined = recorded.get("decision") == "declined"
        stage = ("paid" if c["status"] == "closed" else "decided" if declined else
                 "under_review" if c["status"] == "in_assessment" else "reported")
        outstanding = []
        if declined:
            decision = {"decision": "declined", "decided_on": recorded["decided_on"], "clause": recorded["clause"],
                        "reason": recorded["reason"]}
    payments = sorted(c.get("payments", []), key=lambda x: x.get("date") or x.get("paid_on") or "")
    last = None
    if payments:
        pay = payments[-1]
        last = {"date": pay.get("date") or pay.get("paid_on"), "amount": pay["amount"],
                "paid_to": pay.get("paid_to") or pay.get("payee") or ""}
    words = STAGE_WORDS[stage]
    if decision:
        words = (f"The claim was declined on {long_date(decision['decided_on'])} under clause {decision['clause']} of the policy "
                 f"wording. The reason recorded: {decision['reason']}")
    return {"claim_id": claim_id, "policy_id": c["policy_id"], "policyholder": c["claimant"], "claim_type": c["claim_type_label"],
            "date_of_loss": c["loss_date"], "date_reported": c["reported_date"], "stage": stage, "stage_in_words": words,
            "what_is_outstanding": outstanding,
            "outstanding_note": ("" if outstanding else "The record lists nothing that the client or the broker is asked for."),
            "last_payment": last,
            "last_payment_note": (f"The last payment was {usd(last['amount'])} on {long_date(last['date'])}." if last else
                                  "No payment is recorded."),
            "decision": decision, "held_back": list(HELD_BACK_FROM_A_BROKER),
            "anything_else": "The record gives a broker nothing else. For any other question, save a call-back request and a "
                             "person answers."}


# ---------------------------------------------------------------- everything

def build_servicing(today: date) -> dict:
    return {
        "sv_rules": copy.deepcopy(SERVICING_RULES),
        "sv_policies": build_serviced_policies(today),
        "sv_policy_terms": build_policy_terms(),
        "sv_change_requests": build_change_requests(today),
        "sv_certificate_requests": build_certificate_requests(today),
        "sv_certificate_templates": {CERTIFICATE_TEMPLATE["template_id"]: copy.deepcopy(CERTIFICATE_TEMPLATE)},
        "sv_endorsement_templates": copy.deepcopy(ENDORSEMENT_TEMPLATES),
        "sv_brokers": build_brokers(),
        "sv_claims": build_servicing_claims(today),
        "sv_broker_queries": build_broker_queries(today),
    }
