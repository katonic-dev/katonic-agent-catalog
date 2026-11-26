"""Seed data, part 1: policy wordings with numbered clauses, and policies with their schedules and endorsements."""

from __future__ import annotations

from datetime import date, timedelta

HOME_COUNTRY = "Meridia"


def d_ago(today: date, n: int) -> str:
    return (today - timedelta(days=n)).isoformat()


def d_ahead(today: date, n: int) -> str:
    return (today + timedelta(days=n)).isoformat()


def long_date(iso: str) -> str:
    day = date.fromisoformat(iso)
    month = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")[day.month - 1]
    return f"{day.day} {month} {day.year}"


def _clauses(rows):
    return [{"clause": number, "section": section, "heading": heading, "text": text} for number, section, heading, text in rows]


WORDINGS = {
    "TMI-MOT-01": {
        "wording_id": "TMI-MOT-01", "title": "Private Motor Policy Wording", "version": "3", "product": "private_motor",
        "how_to_read": "Section 1 says what is covered. Section 2 says what is not covered. Section 3 gives the most that is paid. "
                       "Section 4 gives the deductible. Section 5 gives the conditions. Amounts in the policy schedule apply where a "
                       "clause says so. The wording covers nothing it does not name.",
        "clauses": _clauses([
            ("1.1", "What is covered", "Loss or damage", "We pay for accidental loss of or damage to the insured vehicle."),
            ("1.2", "What is covered", "Theft", "We pay for loss of or damage to the insured vehicle by theft or attempted theft."),
            ("1.3", "What is covered", "Damage to other people's property",
             "We pay what you are legally liable to pay for damage to another person's property caused by an accident involving the "
             "insured vehicle, up to the third party property limit in the schedule."),
            ("1.4", "What is covered", "Windscreen and glass", "We pay to repair or replace broken glass in the windscreen or windows of the insured vehicle."),
            ("1.5", "What is covered", "Hire car",
             "While the insured vehicle is being repaired after loss or damage we cover, or after its theft, we pay for a hire car."),
            ("2.1", "What is not covered", "No valid licence", "Loss or damage while the insured vehicle is driven by a person who does not hold a valid driving licence."),
            ("2.2", "What is not covered", "Wear and tear",
             "Wear and tear, mechanical or electrical breakdown, and damage to tyres by braking, punctures, cuts or bursts."),
            ("2.3", "What is not covered", "Hire or reward", "Loss or damage while the insured vehicle is used for hire or reward, or for racing or pace-making."),
            ("2.4", "What is not covered", "Alcohol or drugs", "Loss or damage while the driver is over the legal limit for alcohol or is under the influence of drugs."),
            ("2.5", "What is not covered", "Cleaning and servicing", "The cost of cleaning, valeting and routine servicing."),
            ("2.6", "What is not covered", "Loss of value", "Any loss of value of the insured vehicle after it has been repaired."),
            ("3.1", "The most we pay", "The vehicle",
             "The most we pay for the insured vehicle is its market value at the date of the loss, and never more than the sum insured in the schedule."),
            ("3.2", "The most we pay", "Windscreen and glass", "The most we pay under clause 1.4 is USD 500 for any one claim."),
            ("3.3", "The most we pay", "Personal belongings", "The most we pay for personal belongings in the insured vehicle is USD 300 for any one claim."),
            ("3.4", "The most we pay", "Hire car", "The most we pay under clause 1.5 is USD 40 a day, for up to 10 days, for any one claim."),
            ("4.1", "The deductible", "The deductible", "The deductible in the schedule is taken once from each claim."),
            ("4.2", "The deductible", "Young driver", "A further USD 300 is taken when the driver at the time of the loss is under 25 years of age."),
            ("5.1", "Conditions", "Telling us", "You must tell us about a loss within 30 days of the date it happened."),
            ("5.2", "Conditions", "The police",
             "Theft, attempted theft, and any accident in which a person is injured must be reported to the police. You must send us the police report."),
        ]),
    },
    "TMI-HOM-02": {
        "wording_id": "TMI-HOM-02", "title": "Home Buildings and Contents Policy Wording", "version": "2", "product": "home",
        "how_to_read": "Section 1 says what is covered. Section 2 says what is not covered. Section 3 gives the most that is paid. "
                       "Section 4 gives the deductible. Section 5 gives the conditions. Amounts in the policy schedule apply where a "
                       "clause says so. The wording covers nothing it does not name.",
        "clauses": _clauses([
            ("1.1", "What is covered", "Fire", "We pay for loss or damage caused by fire, lightning or explosion."),
            ("1.2", "What is covered", "Storm or flood", "We pay for loss or damage caused by storm or flood."),
            ("1.3", "What is covered", "Escape of water",
             "We pay for loss or damage caused by the sudden and accidental escape of water from a fixed water pipe, tank or appliance."),
            ("1.4", "What is covered", "Theft",
             "We pay for loss or damage caused by theft or attempted theft following forcible and violent entry to or exit from the home."),
            ("1.5", "What is covered", "Alternative accommodation",
             "When the home cannot be lived in after loss or damage we cover, we pay the reasonable cost of somewhere else to live."),
            ("1.6", "What is covered", "Trace and access",
             "We pay the cost of finding the source of an escape of water we cover, and of making good the damage done in finding it."),
            ("2.1", "What is not covered", "Gradual damage",
             "Water that escapes gradually, seepage, rising damp, and any damage that happened over a period of time."),
            ("2.2", "What is not covered", "Unoccupied home", "Loss or damage that happens after the home has been unoccupied for more than 60 days in a row."),
            ("2.3", "What is not covered", "Theft without forced entry", "Theft where there was no forcible and violent entry to or exit from the home."),
            ("2.4", "What is not covered", "Wear and tear", "Wear and tear, and damage caused by pets or vermin."),
            ("2.5", "What is not covered", "Improvements", "The cost of improving the home beyond its condition immediately before the loss."),
            ("3.1", "The most we pay", "Buildings and contents", "The most we pay is the sum insured for buildings and the sum insured for contents in the schedule."),
            ("3.2", "The most we pay", "Single items", "The most we pay for any one item of contents is USD 2,500, unless the item is listed in the schedule."),
            ("3.3", "The most we pay", "Alternative accommodation", "The most we pay under clause 1.5 is 10 percent of the sum insured for buildings."),
            ("3.4", "The most we pay", "Trace and access", "The most we pay under clause 1.6 is USD 1,500 for any one claim."),
            ("4.1", "The deductible", "The deductible", "The deductible in the schedule is taken once from each claim."),
            ("4.2", "The deductible", "Escape of water", "For a claim under clause 1.3 the deductible is USD 500, in place of the deductible in the schedule."),
            ("5.1", "Conditions", "Telling us", "You must tell us about a loss within 30 days of the date it happened."),
            ("5.2", "Conditions", "The police", "Theft or attempted theft must be reported to the police. You must send us the police report."),
            ("5.3", "Conditions", "Damaged items", "Keep damaged items until we have had the chance to see them."),
        ]),
    },
}


def _motor(pid, holder, address, vehicle, registration, sum_insured, deductible, start_ago, *, status="in_force", term=365,
           named_drivers=None, endorsements=None, note=""):
    return {"policy_id": pid, "product": "private_motor", "wording_id": "TMI-MOT-01", "wording_version": "3",
            "holder": holder, "address": address, "status": status, "_start_ago": start_ago, "_term": term, "status_note": note,
            "schedule": {"insured_vehicle": vehicle, "registration": registration, "sum_insured": float(sum_insured),
                         "deductible": float(deductible), "third_party_property_limit": 1000000.0,
                         "named_drivers": named_drivers or [], "currency": "USD"},
            "endorsements": endorsements or []}


def _home(pid, holder, address, buildings, contents, deductible, start_ago, *, status="in_force", term=365, listed_items=None,
          endorsements=None, note=""):
    return {"policy_id": pid, "product": "home", "wording_id": "TMI-HOM-02", "wording_version": "2",
            "holder": holder, "address": address, "status": status, "_start_ago": start_ago, "_term": term, "status_note": note,
            "schedule": {"insured_home": address, "buildings_sum_insured": float(buildings), "contents_sum_insured": float(contents),
                         "deductible": float(deductible), "alternative_accommodation_limit": round(buildings * 0.10, 2),
                         "listed_items": listed_items or [], "currency": "USD"},
            "endorsements": endorsements or []}


def build_policies(today: date) -> dict:
    rows = [
        _motor("POL-2001", "Corwin Ashgrove", "14 Larchfield Row, Marlow Reach, Meridia", "Tarn Vale 1.6 saloon, 2022", "MR-4417-K", 16500, 250, 210),
        _home("POL-2002", "Elspeth Marrowdene", "3 Weavers Yard, Tallowby, Meridia", 310000, 45000, 300, 150),
        # The period ended 20 days before the insurer date and the policy was not renewed.
        _motor("POL-2003", "Dariusz Kellhaven", "88 Saltmarsh Lane, Port Ilvane, Meridia", "Orrin Bay 2.0 estate, 2019", "PI-2086-T", 10500, 400,
               385, status="lapsed", note="The period ended and the policy was not renewed."),
        _motor("POL-2004", "Odalys Fenwright", "27 Cobblers Rise, Port Ilvane, Meridia", "Halden Crest 1.8 hatchback, 2023", "PI-9031-C", 15000, 400, 95),
        _motor("POL-2005", "Bram Tollermoor", "5 Quarry Bank, Marlow Reach, Meridia", "Vesper Lane 1.4 hatchback, 2021", "MR-7720-B", 12000, 300, 260),
        _home("POL-2006", "Henrietta Quillby", "61 Thistledown Close, Tallowby, Meridia", 265000, 38000, 250, 120),
        _home("POL-2007", "Aldous Pennicott", "9 Ferrymans Walk, Port Ilvane, Meridia", 240000, 30000, 250, 330),
        _motor("POL-2008", "Marisol Underhay", "40 Hawthorn Steps, Marlow Reach, Meridia", "Tarn Vale 1.2 hatchback, 2020", "MR-3358-D", 9000, 350, 175,
               named_drivers=["Marisol Underhay", "Piers Underhay"],
               endorsements=[{"endorsement_id": "END-2008-1", "title": "Named drivers only", "_effective_ago": 175,
                              "text": "Cover under clauses 1.1 and 1.2 applies only while the insured vehicle is driven by a person named as a "
                                      "driver in the schedule. This endorsement changes the wording for this policy."}]),
        _home("POL-2009", "Teodor Brackwell", "12 Millpond Court, Tallowby, Meridia", 285000, 42000, 300, 240),
        _home("POL-2010", "Yvaine Corrimond", "2 Heron Wharf, Port Ilvane, Meridia", 355000, 50000, 300, 290),
        _motor("POL-2011", "Isaura Venn", "33 Candlewick Street, Marlow Reach, Meridia", "Halden Crest 1.6 saloon, 2024", "MR-6104-H", 19500, 300, 60),
        _home("POL-2012", "Elric Stannaway", "7 Otterburn Gardens, Tallowby, Meridia", 298000, 40000, 250, 200),
        # Cancelled for non-payment 40 days before the insurer date.
        _motor("POL-2013", "Ludovic Harrowell", "19 Tanners Row, Port Ilvane, Meridia", "Orrin Bay 1.6 saloon, 2018", "PI-5570-M", 8200, 400, 190,
               status="cancelled", note="Cancelled for non-payment of the premium."),
        _motor("POL-2014", "Ansel Whitlocke", "52 Beacon Hill, Marlow Reach, Meridia", "Vesper Lane 2.0 estate, 2022", "MR-8842-P", 17800, 300, 130),
    ]
    policies = {}
    for row in rows:
        start = today - timedelta(days=row.pop("_start_ago"))
        end = start + timedelta(days=row.pop("_term")) - timedelta(days=1)
        row["period_start"], row["period_end"] = start.isoformat(), end.isoformat()
        row["cancelled_on"] = d_ago(today, 40) if row["status"] == "cancelled" else None
        for e in row["endorsements"]:
            e["effective"] = d_ago(today, e.pop("_effective_ago"))
        row["currency"] = "USD"
        policies[row["policy_id"]] = row
    return policies


def cover_on(policy: dict, on_iso: str) -> dict:
    """Whether the policy was in force on a date, with the reason in plain words. The system works out the days."""
    on = date.fromisoformat(on_iso)
    start, end = date.fromisoformat(policy["period_start"]), date.fromisoformat(policy["period_end"])
    pid = policy["policy_id"]
    if on < start:
        days = (start - on).days
        return {"policy_id": pid, "on": on_iso, "in_force": False,
                "reason": f"The policy period started on {long_date(policy['period_start'])}. {long_date(on_iso)} is {days} "
                          f"day{'s' if days != 1 else ''} before the start."}
    if policy.get("cancelled_on") and on >= date.fromisoformat(policy["cancelled_on"]):
        days = (on - date.fromisoformat(policy["cancelled_on"])).days
        return {"policy_id": pid, "on": on_iso, "in_force": False,
                "reason": f"The policy was cancelled on {long_date(policy['cancelled_on'])}: {policy['status_note']} {long_date(on_iso)} is "
                          f"{days} day{'s' if days != 1 else ''} after the cancellation."}
    if on > end:
        days = (on - end).days
        return {"policy_id": pid, "on": on_iso, "in_force": False,
                "reason": f"The policy period ended on {long_date(policy['period_end'])} and the policy was not renewed. "
                          f"{long_date(on_iso)} is {days} day{'s' if days != 1 else ''} after the end."}
    return {"policy_id": pid, "on": on_iso, "in_force": True,
            "reason": f"The policy period runs from {long_date(policy['period_start'])} to {long_date(policy['period_end'])}, and "
                      f"{long_date(on_iso)} is inside it."}
