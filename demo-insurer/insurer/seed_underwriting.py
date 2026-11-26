"""Seed data, part 4: underwriting. The underwriting guidelines, the appetite statement, broker submissions, the authority
levels with the referral rules, referrals and precedents, the renewal rules, commercial policies and renewals.

The sums are here as well: a submission measured against the numeric guidelines, a referral measured against the authority
of the grade that asks, and a renewal with its claims totals and loss ratios. The system calls them, so an agent never
adds up and never compares two figures.
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


CLASSES = {"commercial_property": "Commercial property", "motor_fleet": "Motor fleet", "public_liability": "Public liability"}

CONSTRUCTION_CLASSES = {
    "A": "non-combustible: brick or concrete walls with a concrete or steel roof",
    "B": "mixed: brick or block walls with a timber roof or timber floors",
    "C": "combustible: a timber frame or composite panel walls",
}

# The figures the numeric guidelines turn on.
SUM_INSURED_LIMIT = {"A": 5000000.0, "B": 2500000.0, "C": 1000000.0}
SPRINKLERS_ABOVE = 1500000.0
MOST_CLAIMS_IN_FIVE_YEARS = 3
LARGEST_SINGLE_CLAIM = 250000.0
LOWEST_DEDUCTIBLE = ((1000000.0, 2500.0), (None, 5000.0))  # up to a total sum insured, the lowest deductible
FLEET_SMALLEST, FLEET_LARGEST = 5, 150
YOUNG_DRIVERS_PERCENT = 20.0
VEHICLES_FOR_EACH_CLAIM = 4


# ---------------------------------------------------------------- underwriting guidelines

def _rule(rule_id, class_of_business, heading, kind, text):
    return {"rule_id": rule_id, "class_of_business": class_of_business, "heading": heading, "kind": kind, "text": text}


GUIDELINES = {r["rule_id"]: r for r in [
    _rule("UG-1", "commercial_property", "The most sum insured at one location", "measured",
          "The total sum insured at one location is buildings plus contents plus stock. It must not be more than USD 5,000,000 for "
          "construction class A, USD 2,500,000 for class B and USD 1,000,000 for class C. A total exactly on the limit is within the "
          "guideline."),
    _rule("UG-2", "commercial_property", "Occupancies we do not write", "for_reading",
          "We do not write a location used for any of these: making or storing fireworks or explosives; waste recycling or a scrap "
          "yard; making foam or plastics; a nightclub. This rule is read against the occupancy and the documents. It is not measured."),
    _rule("UG-3", "commercial_property", "Sprinklers", "measured",
          "A location of construction class B or C with a total sum insured above USD 1,500,000 needs a sprinkler system that is in "
          "working order. The measure uses the sprinklers field of the submission form. A survey note or a broker's note may say "
          "something else: the documents are read as well, and where the form and a document disagree both are shown and neither is chosen."),
    _rule("UG-4", "commercial_property", "Claims history", "measured",
          "The submission must hold the claims history of the last five years. No more than 3 claims in the five years, and no "
          "single claim above USD 250,000. Exactly 3 claims is within the guideline. A submission with no claims history cannot be "
          "measured: the history is missing and the broker is asked for it."),
    _rule("UG-5", "commercial_property", "Flood", "measured",
          "The insurer sorts every location into flood zone 1, 2 or 3. A location in flood zone 3 is outside the guideline. Zones 1 "
          "and 2 are within it."),
    _rule("UG-6", "commercial_property", "The lowest deductible", "measured",
          "The lowest deductible is USD 2,500 where the total sum insured is up to USD 1,000,000, and USD 5,000 above that. A "
          "requested deductible equal to the lowest deductible is within the guideline."),
    _rule("UG-7", "motor_fleet", "The size of a fleet", "measured",
          "A fleet has at least 5 and at most 150 vehicles. A fleet of exactly 5 or exactly 150 vehicles is within the guideline."),
    _rule("UG-8", "motor_fleet", "Young drivers", "measured",
          "No more than 20 percent of the named drivers are under 25 years of age. Exactly 20 percent is within the guideline. The "
          "system works out the percentage."),
    _rule("UG-9", "motor_fleet", "Uses we do not write", "for_reading",
          "We do not write a fleet that carries hazardous goods, or one used as taxis or for private hire. This rule is read against "
          "the use of the fleet and the documents. It is not measured."),
    _rule("UG-10", "motor_fleet", "Claims history", "measured",
          "The submission must hold the claims history of the last three years. No more than one claim for every 4 vehicles in the "
          "three years; the system works out the number allowed, rounded down. A submission with no claims history cannot be "
          "measured: the history is missing and the broker is asked for it."),
]}

GUIDELINES_HOW_TO_READ = ("Each rule has an id, the class of business it is for, a heading, its text and a kind. A rule of the kind "
                          "measured has an exact test with figures: the system measures a submission against it and gives the measured "
                          "value, the limit and the result. A rule of the kind for_reading has no figure: it is read against the "
                          "occupancy or use and the documents of the submission. A submission outside a rule is not declined by the "
                          "rule: an underwriter decides, and the referral rules say which grade.")


# ---------------------------------------------------------------- appetite statement

def _appetite(rule_id, class_of_business, position, text):
    return {"rule_id": rule_id, "class_of_business": class_of_business, "class_name": CLASSES[class_of_business],
            "position": position, "text": text}


APPETITE = {r["rule_id"]: r for r in [
    _appetite("AP-P1", "commercial_property", "within",
              "Offices, shops, and warehouses for goods that do not burn easily, in construction class A or B."),
    _appetite("AP-P2", "commercial_property", "within", "Light manufacturing and food production, bakeries included."),
    _appetite("AP-P3", "commercial_property", "outside",
              "Making or storing fireworks or explosives; waste recycling and scrap yards; making foam or plastics; nightclubs."),
    _appetite("AP-P4", "commercial_property", "within",
              "Woodworking and joinery workshops where a dust extraction system is fitted and in use."),
    _appetite("AP-P5", "commercial_property", "refer", "Unoccupied buildings, and buildings on the heritage register of Meridia."),
    _appetite("AP-P6", "commercial_property", "refer", "Cold stores, and any building with composite panel walls."),
    _appetite("AP-M1", "motor_fleet", "within", "Fleets of cars, vans and light trucks that carry the insured's own goods or staff."),
    _appetite("AP-M2", "motor_fleet", "outside",
              "Carriage of hazardous goods; taxis and private hire; vehicles hired out to the public."),
    _appetite("AP-M3", "motor_fleet", "refer", "Coaches and buses, and courier fleets that carry parcels for other people."),
    _appetite("AP-M4", "motor_fleet", "within", "Refrigerated vans that deliver food."),
    _appetite("AP-L1", "public_liability", "within", "Offices, shops, cafes and restaurants."),
    _appetite("AP-L2", "public_liability", "outside", "Demolition, asbestos removal, and work offshore."),
    _appetite("AP-L3", "public_liability", "refer", "Roofing and scaffolding contractors, and events open to the public."),
]}

APPETITE_HOW_TO_READ = ("The appetite statement has numbered rules by class of business. Each rule has one position: within (we "
                        "want this kind of risk), outside (we do not write it) or refer (an underwriter of senior grade decides). "
                        "A rule speaks only of what it names. A risk that no rule names is not within and not outside: the "
                        "statement is silent on it, and an underwriter answers. The statement says nothing about price, limits or "
                        "terms: the underwriting guidelines hold the figures.")

SEARCH_STOP_WORDS = {"the", "and", "for", "with", "within", "outside", "refer", "appetite", "risk", "risks", "can", "write", "are",
                     "that", "this", "does", "our", "any", "insure", "cover", "would", "could", "about", "what", "say", "says",
                     "rule", "rules", "statement", "have", "has", "who", "one", "its", "their", "from"}


# ---------------------------------------------------------------- submissions

def _doc(sub_id, n, doc_type, title, text):
    return {"document_id": f"{sub_id}-D{n}", "type": doc_type, "title": title, "text": text}


def _property_risk(address, flood_zone, occupancy, construction_class, construction, buildings, contents, stock, sprinklers, alarm):
    return {"location": address, "flood_zone": flood_zone, "occupancy": occupancy, "construction_class": construction_class,
            "construction": construction, "buildings_sum_insured": float(buildings), "contents_sum_insured": float(contents),
            "stock_sum_insured": float(stock), "sprinklers": sprinklers, "alarm": alarm}


def _fleet_risk(base, use, vehicles, named_drivers, drivers_under_25, vehicle_types):
    return {"base": base, "use": use, "vehicles": vehicles, "named_drivers": named_drivers, "named_drivers_under_25": drivers_under_25,
            "vehicle_types": vehicle_types}


def _history(years, rows):
    return {"years_covered": years, "claims": [{"year": y, "cause": cause, "amount": float(amount)} for y, cause, amount in rows]}


BROKERS = {
    "QR": ("Quillfeather & Roe Insurance Brokers, Port Ilvane", "Imelda Roe"),
    "HL": ("Harbourlight Risk Brokers, Marlow Reach", "Cuthbert Wainfleet"),
    "TC": ("Tallowby Commercial Brokers, Tallowby", "Seraphine Oddy"),
}


def build_submissions(today: date) -> dict:
    L = lambda ago: long_date(d_ago(today, ago))
    A = lambda ahead: long_date(d_ahead(today, ahead))
    y = today.year
    subs = {}

    def add(sub_id, cls, broker, insured, received_ago, start_ahead, risk, terms, history, docs):
        name, contact = BROKERS[broker]
        subs[sub_id] = {"submission_id": sub_id, "status": "received", "class_of_business": cls, "class_name": CLASSES[cls],
                        "broker": name, "broker_contact": contact, "insured": insured, "received": d_ago(today, received_ago),
                        "cover_start_requested": d_ahead(today, start_ahead), "risk": risk, "requested_terms": terms,
                        "claims_history": history,
                        "documents": [_doc(sub_id, n, *spec) for n, spec in enumerate(docs, start=1)],
                        "currency": "USD", "file_drafts": []}

    add("SBM-6501", "commercial_property", "QR", "Larkspur Lane Stationers Ltd", 2, 35,
        _property_risk("4 Chandlers Quay, Port Ilvane, Meridia", 1, "Warehouse and office for paper, envelopes and office stationery.",
                       "A", "Brick walls, concrete floors, steel deck roof.", 1200000, 350000, 250000, "yes",
                       "Fire and intruder alarm linked to a monitoring station."),
        {"deductible": 7500.0, "covers": "Fire, storm, escape of water, theft."},
        _history(5, [(y - 3, "Storm damage to the roof", 12400)]),
        [("broker_presentation", "Broker's presentation",
          f"From Imelda Roe, Quillfeather & Roe Insurance Brokers. Sent {L(2)}.\nWe ask for terms for Larkspur Lane Stationers Ltd, a "
          "wholesaler of paper and office stationery, at 4 Chandlers Quay, Port Ilvane. One location. The building is brick with a "
          f"steel deck roof and is sprinklered throughout. Cover is wanted from {A(35)}. One claim in five years: storm damage to the "
          f"roof in {y - 3}, USD 12,400 paid.")])

    add("SBM-6502", "motor_fleet", "HL", "Wickerby Dairy Rounds Ltd", 3, 30,
        _fleet_risk("Wickerby Yard, Marlow Reach, Meridia", "Delivery of the company's own milk, cheese and butter to shops and homes.",
                    24, 32, 4, "24 light vans, none over 3.5 tonnes."),
        {"deductible": 500.0, "covers": "Comprehensive, any named driver."},
        _history(3, [(y - 2, "Van reversed into a wall", 1900), (y - 2, "Windscreen", 420), (y - 1, "Collision at a junction", 6300),
                     (y - 1, "Theft from a van", 800), (y, "Van struck while parked", 2100)]),
        [("broker_presentation", "Broker's presentation",
          f"From Cuthbert Wainfleet, Harbourlight Risk Brokers. Sent {L(3)}.\nWickerby Dairy Rounds Ltd runs 24 light vans from "
          "Wickerby Yard, Marlow Reach, and delivers its own dairy goods. There are 32 named drivers, of whom 4 are under 25. No "
          f"hazardous goods are carried. Cover is wanted from {A(30)}. Five claims in three years, listed on the form.")])

    add("SBM-6503", "commercial_property", "TC", "Pellow & Strand Furniture Showrooms Ltd", 4, 28,
        _property_risk("18 Drapers Meadow, Tallowby, Meridia", 1, "Furniture showroom with a stock room behind.", "C",
                       "Timber frame with timber cladding, tiled roof.", 800000, 150000, 400000, "no",
                       "Fire and intruder alarm, sounding on the premises only."),
        {"deductible": 7500.0, "covers": "Fire, storm, escape of water, theft."},
        _history(5, []),
        [("broker_presentation", "Broker's presentation",
          f"From Seraphine Oddy, Tallowby Commercial Brokers. Sent {L(4)}.\nPellow & Strand Furniture Showrooms Ltd sells sofas, beds "
          "and tables from a timber-framed showroom at 18 Drapers Meadow, Tallowby. There are no sprinklers. No claims in five years. "
          f"Cover is wanted from {A(28)}.")])

    add("SBM-6504", "commercial_property", "QR", "Grindlow Metals & Recycling Ltd", 5, 21,
        _property_risk("Yard 3, Coldharbour Sidings, Port Ilvane, Meridia", 2,
                       "Scrap metal yard and waste recycling: sorting, baling and storing metal, cardboard and mixed waste.", "A",
                       "Steel portal frame, block walls, steel roof.", 600000, 200000, 100000, "no", "Intruder alarm and yard cameras."),
        {"deductible": 3000.0, "covers": "Fire, storm, theft."},
        _history(5, [(y - 2, "Fire in a baling machine", 8200)]),
        [("broker_presentation", "Broker's presentation",
          f"From Imelda Roe, Quillfeather & Roe Insurance Brokers. Sent {L(5)}.\nGrindlow Metals & Recycling Ltd runs a scrap metal "
          "and waste recycling yard at Coldharbour Sidings, Port Ilvane. The building is steel and blockwork. One claim in five "
          f"years: a fire in a baling machine in {y - 2}, USD 8,200 paid. Cover is wanted from {A(21)}.")])

    add("SBM-6505", "motor_fleet", "TC", "Tarnbeck Garden Centres Ltd", 1, 40,
        _fleet_risk("Tarnbeck Nursery, Tallowby, Meridia", "Delivery of the company's own plants, compost and garden furniture to customers.",
                    40, 50, 6, "34 light vans and 6 light trucks."),
        {"deductible": 500.0, "covers": "Comprehensive, any named driver."},
        None,
        [("broker_presentation", "Broker's presentation",
          f"From Seraphine Oddy, Tallowby Commercial Brokers. Sent {L(1)}.\nTarnbeck Garden Centres Ltd runs 40 vehicles from Tarnbeck "
          "Nursery, Tallowby, and delivers its own goods. There are 50 named drivers, of whom 6 are under 25. No hazardous goods are "
          f"carried. Cover is wanted from {A(40)}. The claims history for the last three years will follow from the holding insurer: "
          "we do not have it yet.")])

    add("SBM-6506", "commercial_property", "HL", "Ottershaw Print Works Ltd", 3, 30,
        _property_risk("Ottershaw Mill, Weir Lane, Marlow Reach, Meridia", 1, "Commercial printer: presses, paper store and bindery.", "B",
                       "Brick walls, timber upper floor, slate roof on timber trusses.", 1400000, 500000, 300000, "yes",
                       "Fire and intruder alarm linked to a monitoring station."),
        {"deductible": 10000.0, "covers": "Fire, storm, escape of water, theft."},
        _history(5, [(y - 4, "Escape of water from a tank", 9700), (y - 1, "Theft of copper cable", 3300)]),
        [("broker_presentation", "Broker's presentation",
          f"From Cuthbert Wainfleet, Harbourlight Risk Brokers. Sent {L(3)}.\nOttershaw Print Works Ltd is a commercial printer at "
          "Ottershaw Mill, Marlow Reach. The mill is brick with a timber upper floor. The form shows sprinklers: yes. Two claims in "
          f"five years, listed on the form. Cover is wanted from {A(30)}. The survey note of the holding insurer is attached."),
         ("survey_note", "Survey note, Marlow Reach Risk Surveys",
          f"MARLOW REACH RISK SURVEYS, note MRS-0418\nSite: Ottershaw Mill, Weir Lane, Marlow Reach\nVisited: {L(40)}\n"
          f"Sprinklers: the sprinkler system was decommissioned on {L(70)}, when the water main to the mill was altered. The pipework "
          "and heads remain in place but the system is not live and there is no date to bring it back.\nHousekeeping: good. Paper "
          "stock kept clear of the presses.\nAlarm: tested and working.")])

    add("SBM-6507", "commercial_property", "QR", "Saltmarsh Chandlery & Rope Ltd", 6, 25,
        _property_risk("Rope Walk, Saltmarsh Lane, Port Ilvane, Meridia", 2, "Warehouse and trade counter for rope, sailcloth and boat fittings.",
                       "B", "Brick walls, timber roof.", 2000000, 600000, 500000, "yes",
                       "Fire and intruder alarm linked to a monitoring station."),
        {"deductible": 10000.0, "covers": "Fire, storm, escape of water, theft."},
        _history(5, [(y - 4, "Storm damage to the roof", 21000), (y - 3, "Theft of stock", 14500), (y - 2, "Escape of water", 48000),
                     (y - 1, "Fire in a waste bin", 6200)]),
        [("broker_presentation", "Broker's presentation",
          f"From Imelda Roe, Quillfeather & Roe Insurance Brokers. Sent {L(6)}.\nSaltmarsh Chandlery & Rope Ltd trades from Rope Walk, "
          "Port Ilvane. The warehouse is brick with a timber roof and is sprinklered. Four claims in five years, listed on the form. "
          f"Cover is wanted from {A(25)}.")])

    add("SBM-6508", "commercial_property", "TC", "Thimbleby Wool Merchants Ltd", 2, 45,
        _property_risk("The Wool Hall, Fleece Street, Tallowby, Meridia", 1, "Warehouse and shop for knitting wool and yarn.", "B",
                       "Stone and brick walls, timber roof.", 1600000, 500000, 400000, "yes",
                       "Fire and intruder alarm linked to a monitoring station."),
        {"deductible": 5000.0, "covers": "Fire, storm, escape of water, theft."},
        _history(5, [(y - 2, "Escape of water from a pipe", 5100)]),
        [("broker_presentation", "Broker's presentation",
          f"From Seraphine Oddy, Tallowby Commercial Brokers. Sent {L(2)}.\nThimbleby Wool Merchants Ltd trades from The Wool Hall, "
          "Tallowby: stone and brick walls with a timber roof, sprinklered throughout, system serviced this year. One claim in five "
          f"years. Cover is wanted from {A(45)}.")])
    return subs


def _row(rule_id, result, measured, limit, sentence, over_by=None):
    rule = GUIDELINES[rule_id]
    return {"rule_id": rule_id, "heading": rule["heading"], "kind": rule["kind"], "result": result, "measured": measured,
            "limit": limit, "over_by": over_by, "sentence": sentence}


def lowest_deductible(total: float) -> float:
    for up_to, lowest in LOWEST_DEDUCTIBLE:
        if up_to is None or total <= up_to:
            return lowest
    return LOWEST_DEDUCTIBLE[-1][1]


def total_sum_insured(risk: dict) -> float:
    return money(risk["buildings_sum_insured"] + risk["contents_sum_insured"] + risk["stock_sum_insured"])


def measure_submission(sub: dict) -> dict:
    """The submission against every guideline of its class. The system does every sum and every comparison."""
    risk, history, rows = sub["risk"], sub["claims_history"], []
    out = {"submission_id": sub["submission_id"], "class_of_business": sub["class_of_business"]}
    if sub["class_of_business"] == "commercial_property":
        total, cls = total_sum_insured(risk), risk["construction_class"]
        out["total_sum_insured"] = total
        out["total_sum_insured_working"] = (f"{usd(risk['buildings_sum_insured'])} buildings + {usd(risk['contents_sum_insured'])} "
                                            f"contents + {usd(risk['stock_sum_insured'])} stock = {usd(total)}.")
        limit = SUM_INSURED_LIMIT[cls]
        if total > limit:
            rows.append(_row("UG-1", "outside", total, limit,
                             f"The total sum insured is {usd(total)}. The limit for construction class {cls} is {usd(limit)}. "
                             f"The total is over the limit by {usd(money(total - limit))}.", money(total - limit)))
        else:
            on = " The total is exactly on the limit, which is within the guideline." if total == limit else ""
            rows.append(_row("UG-1", "within", total, limit,
                             f"The total sum insured is {usd(total)}. The limit for construction class {cls} is {usd(limit)}.{on}"))
        rows.append(_row("UG-2", "for_reading", None, None,
                         "Not measured. Read the occupancy and the documents against the list in UG-2."))
        needed = cls in ("B", "C") and total > SPRINKLERS_ABOVE
        if not needed:
            why = ("construction class A needs none" if cls == "A"
                   else f"the total sum insured of {usd(total)} is not above {usd(SPRINKLERS_ABOVE)}")
            rows.append(_row("UG-3", "within", risk["sprinklers"], "not needed",
                             f"The guideline needs no sprinklers here: {why}. The form's sprinklers field says {risk['sprinklers']}."))
        elif risk["sprinklers"] == "yes":
            rows.append(_row("UG-3", "within", "yes", "needed",
                             f"Sprinklers are needed: construction class {cls} and a total sum insured of {usd(total)}, above "
                             f"{usd(SPRINKLERS_ABOVE)}. The form's sprinklers field says yes. The measure uses the form's field only: "
                             "read the documents for anything that says the system is not in working order."))
        else:
            rows.append(_row("UG-3", "outside", risk["sprinklers"], "needed",
                             f"Sprinklers are needed: construction class {cls} and a total sum insured of {usd(total)}, above "
                             f"{usd(SPRINKLERS_ABOVE)}. The form's sprinklers field says {risk['sprinklers']}."))
        if history is None:
            rows.append(_row("UG-4", "cannot_be_measured", None, f"{MOST_CLAIMS_IN_FIVE_YEARS} claims in five years",
                             "The submission holds no claims history, so the rule cannot be measured. The history is missing: "
                             "nothing is assumed about it."))
        else:
            count = len(history["claims"])
            largest = max((c["amount"] for c in history["claims"]), default=0.0)
            ok = count <= MOST_CLAIMS_IN_FIVE_YEARS and largest <= LARGEST_SINGLE_CLAIM
            rows.append(_row("UG-4", "within" if ok else "outside", {"claims": count, "largest_claim": largest},
                             {"claims": MOST_CLAIMS_IN_FIVE_YEARS, "largest_claim": LARGEST_SINGLE_CLAIM},
                             f"The history shows {plural(count, 'claim')} in five years; the guideline allows {MOST_CLAIMS_IN_FIVE_YEARS}. "
                             f"The largest single claim is {usd(largest)}; the guideline allows {usd(LARGEST_SINGLE_CLAIM)}.",
                             count - MOST_CLAIMS_IN_FIVE_YEARS if count > MOST_CLAIMS_IN_FIVE_YEARS else None))
        zone = risk["flood_zone"]
        rows.append(_row("UG-5", "outside" if zone >= 3 else "within", zone, 2,
                         f"The location is in flood zone {zone}. Zones 1 and 2 are within the guideline; zone 3 is outside it."))
        lowest, asked = lowest_deductible(total), sub["requested_terms"]["deductible"]
        on = " The two are equal, which is within the guideline." if asked == lowest else ""
        rows.append(_row("UG-6", "within" if asked >= lowest else "outside", asked, lowest,
                         f"The requested deductible is {usd(asked)}. The lowest deductible for a total sum insured of {usd(total)} "
                         f"is {usd(lowest)}.{on}", money(lowest - asked) if asked < lowest else None))
    else:
        n = risk["vehicles"]
        rows.append(_row("UG-7", "within" if FLEET_SMALLEST <= n <= FLEET_LARGEST else "outside", n,
                         {"smallest": FLEET_SMALLEST, "largest": FLEET_LARGEST},
                         f"The fleet has {plural(n, 'vehicle')}. The guideline allows {FLEET_SMALLEST} to {FLEET_LARGEST}.",
                         n - FLEET_LARGEST if n > FLEET_LARGEST else None))
        percent = money(risk["named_drivers_under_25"] / risk["named_drivers"] * 100)
        rows.append(_row("UG-8", "within" if percent <= YOUNG_DRIVERS_PERCENT else "outside", percent, YOUNG_DRIVERS_PERCENT,
                         f"{risk['named_drivers_under_25']} of the {risk['named_drivers']} named drivers are under 25: "
                         f"{percent:,.2f} percent. The guideline allows {YOUNG_DRIVERS_PERCENT:,.2f} percent.",
                         money(percent - YOUNG_DRIVERS_PERCENT) if percent > YOUNG_DRIVERS_PERCENT else None))
        rows.append(_row("UG-9", "for_reading", None, None,
                         "Not measured. Read the use of the fleet and the documents against the list in UG-9."))
        allowed = n // VEHICLES_FOR_EACH_CLAIM
        if history is None:
            rows.append(_row("UG-10", "cannot_be_measured", None, allowed,
                             "The submission holds no claims history, so the rule cannot be measured. The history is missing: "
                             "nothing is assumed about it."))
        else:
            count = len(history["claims"])
            rows.append(_row("UG-10", "within" if count <= allowed else "outside", count, allowed,
                             f"The history shows {plural(count, 'claim')} in three years. For {plural(n, 'vehicle')} the guideline "
                             f"allows {allowed}: one for every {VEHICLES_FOR_EACH_CLAIM} vehicles, rounded down.",
                             count - allowed if count > allowed else None))
    pick = lambda result: [r["rule_id"] for r in rows if r["result"] == result]
    outside, cannot, reading = pick("outside"), pick("cannot_be_measured"), pick("for_reading")
    parts = [f"Outside on the figures: {', '.join(outside)}." if outside else "No measured rule is outside on the figures."]
    if cannot:
        parts.append(f"Cannot be measured, because the submission lacks what the rule needs: {', '.join(cannot)}.")
    parts.append(f"Left for reading: {', '.join(reading)}.")
    return {**out, "rules": rows, "within": pick("within"), "outside": outside, "cannot_be_measured": cannot, "for_reading": reading,
            "sentence": " ".join(parts),
            "what_this_is": "A measure of the form's fields against the guidelines with figures. It reads no free text and it is "
                            "not a decision: an underwriter decides."}


# ---------------------------------------------------------------- authority levels and referral rules

GRADE_ORDER = ["assistant_underwriter", "underwriter", "senior_underwriter", "head_of_underwriting"]
GRADE_NAMES = {"assistant_underwriter": "assistant underwriter", "underwriter": "underwriter",
               "senior_underwriter": "senior underwriter", "head_of_underwriting": "head of underwriting"}


def _grade(key, sum_insured, vehicles, discount, outside):
    return {"grade": key, "grade_name": GRADE_NAMES[key], "rank": GRADE_ORDER.index(key) + 1,
            "most_total_sum_insured": float(sum_insured), "most_vehicles_in_a_fleet": vehicles,
            "most_discount_percent": float(discount), "may_write_outside_a_guideline": outside,
            "sentence": f"A risk of the grade {GRADE_NAMES[key]}: a total sum insured up to {usd(sum_insured)} at one location, a "
                        f"fleet of up to {vehicles} vehicles, a discount from the technical premium of up to {discount} percent, "
                        f"and {'a risk outside a guideline as well' if outside else 'only a risk within every guideline'}."}


AUTHORITY_LEVELS = {g["grade"]: g for g in [
    _grade("assistant_underwriter", 500000, 25, 0, False),
    _grade("underwriter", 1500000, 75, 10, False),
    _grade("senior_underwriter", 5000000, 150, 20, True),
    _grade("head_of_underwriting", 15000000, 400, 35, True),
]}

REFERRAL_RULES = {r["rule_id"]: r for r in [
    {"rule_id": "RF-1", "heading": "Size above the authority of the grade",
     "text": "A commercial property risk whose total sum insured is above the authority of the underwriter who asks, or a fleet with "
             "more vehicles than that authority, goes to the lowest grade whose authority covers it. A size exactly on the "
             "authority needs no referral."},
    {"rule_id": "RF-2", "heading": "A risk outside a guideline",
     "text": "A risk that is outside any underwriting guideline (UG-1 to UG-10) is decided by a senior underwriter or above. An "
             "assistant underwriter or an underwriter refers it to a senior underwriter."},
    {"rule_id": "RF-3", "heading": "A discount above the authority of the grade",
     "text": "A discount from the technical premium above the discount authority of the underwriter who asks goes to the lowest "
             "grade whose discount authority covers it. The system works out the discount as a percentage of the technical "
             "premium. A discount exactly on the authority needs no referral."},
]}

AUTHORITY_HOW_TO_READ = ("Four grades, lowest first: assistant underwriter, underwriter, senior underwriter, head of underwriting. "
                         "Each has its own authority. The referral rules RF-1 to RF-3 say when a risk goes to a higher grade and to "
                         "which. Where several rules apply, the risk goes to the highest grade any of them names. The system "
                         "measures a referral against these rules: use its answer and do not compare figures yourself.")


def _lowest_grade(test) -> str | None:
    return next((g for g in GRADE_ORDER if test(AUTHORITY_LEVELS[g])), None)


def check_authority(ref: dict) -> dict:
    """Which referral rules apply to a referral, and the grade it goes to. The system does every comparison."""
    grade = ref["asked_by"]["grade"]
    mine, rank = AUTHORITY_LEVELS[grade], GRADE_ORDER.index(grade)
    name = GRADE_NAMES[grade]
    rows, needed = [], []

    def add(rule_id, fires, measured, limit, grade_needed, sentence):
        rows.append({"rule_id": rule_id, "heading": REFERRAL_RULES[rule_id]["heading"], "applies": fires, "measured": measured,
                     "authority_of_the_asking_grade": limit, "grade_needed": grade_needed if fires else None, "sentence": sentence})
        if fires and grade_needed:
            needed.append(grade_needed)

    if ref["class_of_business"] == "commercial_property":
        size, limit = ref["risk"]["total_sum_insured"], mine["most_total_sum_insured"]
        to = _lowest_grade(lambda g: g["most_total_sum_insured"] >= size)
        what, lim = f"The total sum insured is {usd(size)}", usd(limit)
    else:
        size, limit = ref["risk"]["vehicles"], mine["most_vehicles_in_a_fleet"]
        to = _lowest_grade(lambda g: g["most_vehicles_in_a_fleet"] >= size)
        what, lim = f"The fleet has {plural(size, 'vehicle')}", plural(limit, "vehicle")
    if size > limit:
        add("RF-1", True, size, limit, to,
            f"{what}. The authority of the grade {name} is {lim}. It is above the authority, and the lowest grade whose authority "
            f"covers it is {GRADE_NAMES[to] if to else 'none: it is above every grade'}.")
    else:
        on = " It is exactly on the authority, which needs no referral." if size == limit else ""
        add("RF-1", False, size, limit, None, f"{what}. The authority of the grade {name} is {lim}. It is not above the authority.{on}")

    outside = [o["rule_id"] for o in ref["outside_guidelines"]]
    if outside and not mine["may_write_outside_a_guideline"]:
        add("RF-2", True, outside, "only a risk within every guideline", "senior_underwriter",
            f"The risk is outside {', '.join(outside)}. The grade {name} decides only a risk within every guideline, so it goes to a "
            "senior underwriter.")
    elif outside:
        add("RF-2", False, outside, "may decide a risk outside a guideline", None,
            f"The risk is outside {', '.join(outside)}. The grade {name} may decide a risk outside a guideline, so this rule sends "
            "it nowhere.")
    else:
        add("RF-2", False, [], "not needed", None, "The referral records no guideline the risk is outside.")

    terms = ref["proposed_terms"]
    discount = money((terms["technical_premium"] - terms["proposed_premium"]) / terms["technical_premium"] * 100)
    limit = mine["most_discount_percent"]
    working = (f"The proposed premium of {usd(terms['proposed_premium'])} is {discount:,.2f} percent below the technical premium of "
               f"{usd(terms['technical_premium'])}.")
    if discount > limit:
        to = _lowest_grade(lambda g: g["most_discount_percent"] >= discount)
        add("RF-3", True, discount, limit, to,
            f"{working} The discount authority of the grade {name} is {limit:,.2f} percent. It is above the authority, and the lowest "
            f"grade whose discount authority covers it is {GRADE_NAMES[to] if to else 'none: it is above every grade'}.")
    else:
        on = " It is exactly on the authority, which needs no referral." if discount == limit and discount > 0 else ""
        add("RF-3", False, discount, limit, None,
            f"{working} The discount authority of the grade {name} is {limit:,.2f} percent. It is not above the authority.{on}")

    forced = [r["rule_id"] for r in rows if r["applies"]]
    if not forced:
        return {"referral_id": ref["referral_id"], "asking_grade": grade, "rules": rows, "referral_needed": False, "refer_to_grade": None,
                "forced_by": [], "discount_percent": discount,
                "sentence": f"No referral rule applies. The authority of the grade {name} covers this risk on these terms: "
                            f"{ref['asked_by']['name']} may decide it without a referral."}
    to = max(needed, key=GRADE_ORDER.index)
    assert GRADE_ORDER.index(to) > rank
    return {"referral_id": ref["referral_id"], "asking_grade": grade, "rules": rows, "referral_needed": True, "refer_to_grade": to,
            "forced_by": forced, "discount_percent": discount,
            "sentence": f"A referral is needed, forced by {' and '.join(forced)}. It goes to the grade {GRADE_NAMES[to]}, the "
                        "highest grade any of the rules names."}


# ---------------------------------------------------------------- referrals and precedents

MORROW = {"name": "Benedick Morrow", "grade": "underwriter"}
VARNEY = {"name": "Isolde Varney", "grade": "senior_underwriter"}
PRYCE = {"name": "Octavian Pryce", "grade": "head_of_underwriting"}


def _property_ref(occupancy, cls, construction, total, sprinklers, location):
    return {"occupancy": occupancy, "construction_class": cls, "construction": construction, "total_sum_insured": float(total),
            "sprinklers": sprinklers, "location": location}


def build_referrals(today: date) -> dict:
    refs = {}

    def add(ref_id, raised_ago, asked_by, cls, insured, risk, technical, proposed, deductible, conditions, outside, note,
            submission_id=None):
        refs[ref_id] = {"referral_id": ref_id, "status": "memo_to_be_drafted", "raised_on": d_ago(today, raised_ago),
                        "asked_by": dict(asked_by), "class_of_business": cls, "class_name": CLASSES[cls], "insured": insured,
                        "submission_id": submission_id, "risk": risk,
                        "proposed_terms": {"technical_premium": float(technical), "proposed_premium": float(proposed),
                                           "deductible": float(deductible), "conditions": conditions, "currency": "USD"},
                        "outside_guidelines": [{"rule_id": r, "note": n} for r, n in outside],
                        "underwriter_note": note, "memo_drafts": []}

    add("REF-6601", 1, MORROW, "commercial_property", "Pellow & Strand Furniture Showrooms Ltd",
        _property_ref("Furniture showroom with a stock room behind.", "C", "Timber frame with timber cladding, tiled roof.", 1350000,
                      "no", "18 Drapers Meadow, Tallowby, Meridia"),
        9400, 9400, 10000, "The alarm to be linked to a monitoring station before cover starts.",
        [("UG-1", "The total sum insured of USD 1,350,000.00 is over the limit of USD 1,000,000.00 for construction class C.")],
        "A tidy, well-run showroom with no claims in five years. I would like to write it with a higher deductible and a monitored alarm.",
        submission_id="SBM-6503")
    add("REF-6602", 2, MORROW, "commercial_property", "Marrowgate Grain & Seed Stores Ltd",
        _property_ref("Warehouse for bagged grain and seed.", "B", "Brick walls, timber roof.", 2900000, "no",
                      "Marrowgate Wharf, Port Ilvane, Meridia"),
        22000, 22000, 15000, "None proposed.",
        [("UG-1", "The total sum insured of USD 2,900,000.00 is over the limit of USD 2,500,000.00 for construction class B."),
         ("UG-3", "Construction class B with a total sum insured above USD 1,500,000.00 and no sprinkler system.")],
        "A long-standing client of the broker. The warehouse has no sprinklers and the insured does not plan to fit any.")
    add("REF-6603", 1, VARNEY, "motor_fleet", "Hollinsworth Builders' Merchants Ltd",
        {"use": "Delivery of the company's own bricks, timber and plumbing goods to building sites.", "vehicles": 180,
         "vehicle_types": "150 light trucks and 30 vans.", "base": "Hollinsworth Depot, Marlow Reach, Meridia"},
        96000, 96000, 1000, "None proposed.",
        [("UG-7", "A fleet of 180 vehicles is above the largest fleet of 150.")],
        "One depot, own goods only, a full-time fleet manager. The fleet has grown from 140 vehicles in two years.")
    add("REF-6604", 1, VARNEY, "commercial_property", "Quenby House Offices Ltd",
        _property_ref("Office building let to four firms of accountants and surveyors.", "A", "Concrete frame, brick cladding, concrete roof.",
                      3200000, "yes", "Quenby House, Assembly Row, Marlow Reach, Meridia"),
        21000, 17850, 10000, "None proposed.", [],
        "Within every guideline. The broker asks for a lower premium to move the account from the holding insurer.")
    add("REF-6605", 3, MORROW, "commercial_property", "Wrenlow Tea Importers Ltd",
        _property_ref("Warehouse for tea in chests and cartons.", "A", "Brick walls, concrete floors, steel roof.", 1200000, "yes",
                      "Bonded Store 2, Customs Quay, Port Ilvane, Meridia"),
        8000, 6560, 5000, "None proposed.", [],
        "Within every guideline. The broker says the holding insurer will renew at USD 6,600 and asks us to go under it.")
    return refs


def build_precedents(today: date) -> dict:
    rows = [
        ("PRC-6401", 410, "commercial_property", "Dovecote Beds & Bedding Ltd", "Showroom for beds and mattresses.", "C", 1280000, "no",
         ["RF-2"], ["UG-1"], "Technical premium, deductible USD 10,000.", "approved_with_conditions",
         "The fire and intruder alarm to be linked to a monitoring station before cover starts. Deductible USD 10,000.", VARNEY,
         "A timber-framed showroom over the class C limit. Approved: one location, good housekeeping, no claims in five years."),
        ("PRC-6402", 230, "commercial_property", "Summerlea Garden Furniture Ltd", "Showroom for garden furniture.", "C", 1150000, "no",
         ["RF-2"], ["UG-1"], "Technical premium, deductible USD 10,000.", "approved_with_conditions",
         "The fire and intruder alarm to be linked to a monitoring station before cover starts. Deductible USD 10,000.", VARNEY,
         "A timber-framed showroom over the class C limit. Approved on the same conditions as PRC-6401."),
        ("PRC-6403", 300, "commercial_property", "Aldercombe Grain Stores Ltd", "Warehouse for bagged grain and seed.", "B", 2850000, "yes",
         ["RF-1", "RF-2"], ["UG-1"], "Technical premium, deductible USD 15,000.", "approved_with_conditions",
         "The sprinkler system to be serviced every year and the certificate sent to us.", VARNEY,
         "A grain warehouse over the class B limit. Approved because the whole warehouse is protected by a sprinkler system in "
         "working order. The decision rests on the sprinklers."),
        ("PRC-6404", 180, "commercial_property", "Bexmoor Coffee Importers Ltd", "Warehouse for coffee in sacks.", "A", 1100000, "yes",
         ["RF-3"], [], "A discount of 18 percent from the technical premium.", "declined",
         "A discount of 10 percent was offered in its place, which the underwriter may give alone.", VARNEY,
         "A discount of 18 percent was asked for to match the holding insurer. Declined: matching another insurer's price is not a "
         "reason for a discount above 10 percent."),
        ("PRC-6405", 520, "commercial_property", "Farthingale Linen Stores Ltd", "Warehouse for household linen.", "A", 900000, "yes",
         ["RF-3"], [], "A discount of 15 percent from the technical premium.", "approved",
         "The insured signs a three-year agreement.", PRYCE,
         "A discount of 15 percent was approved because the insured signed a three-year agreement and had no claims in five years."),
    ]
    out = {}
    for (pid, ago, cls, insured, occupancy, ccls, total, sprinklers, forced, outside, terms, decision, conditions, by, summary) in rows:
        out[pid] = {"precedent_id": pid, "decided_on": d_ago(today, ago), "class_of_business": cls, "class_name": CLASSES[cls],
                    "insured": insured, "occupancy": occupancy, "construction_class": ccls, "total_sum_insured": float(total),
                    "sprinklers": sprinklers, "forced_by": forced, "outside_guidelines": outside, "terms_proposed": terms,
                    "decision": decision, "conditions": conditions, "decided_by": dict(by), "summary": summary, "currency": "USD"}
    return out


# ---------------------------------------------------------------- renewals

LOSS_RATIO_LIMIT = 70.0

RENEWAL_RULES = {r["rule_id"]: r for r in [
    {"rule_id": "RN-1", "heading": "Loss ratio",
     "text": "The loss ratio of the period is what the claims of the period have cost (paid plus the reserves on open claims) as a "
             "percentage of the period's premium. A loss ratio above 70 percent needs a referral to a senior underwriter before "
             "terms are offered. Exactly 70 percent needs none. The system works out the ratio."},
    {"rule_id": "RN-2", "heading": "A change of occupancy",
     "text": "A change of occupancy reported since the period started needs a survey before terms are offered."},
    {"rule_id": "RN-3", "heading": "A change in protections",
     "text": "A change in the protections reported since the period started (sprinklers, alarms, guards) needs a referral to a senior "
             "underwriter before terms are offered."},
    {"rule_id": "RN-4", "heading": "An open claim",
     "text": "A reserve on an open claim is an estimate and may move. Where a claim of the period is open, the review gives the loss "
             "ratio on payments alone and the loss ratio with the reserves, and says how much of the cost is reserve."},
    {"rule_id": "RN-5", "heading": "Records that disagree",
     "text": "Where the claims record and the policy record disagree on a date or an amount, the review shows both, chooses neither, "
             "and the claims team is asked to settle it before terms are offered."},
]}

RENEWAL_RULES_HOW_TO_READ = ("The renewal rules RN-1 to RN-5 say what a renewal review must look at. The system measures each "
                             "renewal against them: it adds up the claims, works out the loss ratios, and says which rules apply. "
                             "A renewal to which no rule applies is ready for the underwriter, who decides the terms. No rule "
                             "offers, changes or refuses terms.")


def _commercial(pid, insured, address, broker, days_to_end, occupancy, cls, total, deductible, sprinklers, premium, claims, today):
    end = today + timedelta(days=days_to_end)
    start = end - timedelta(days=364)
    return {"policy_id": pid, "class_of_business": "commercial_property", "class_name": CLASSES["commercial_property"],
            "insured": insured, "address": address, "broker": BROKERS[broker][0], "status": "in_force",
            "period_start": start.isoformat(), "period_end": end.isoformat(),
            "schedule": {"occupancy": occupancy, "construction_class": cls, "total_sum_insured": float(total),
                         "deductible": float(deductible), "sprinklers": sprinklers, "currency": "USD"},
            "annual_premium": float(premium), "currency": "USD",
            "claims": [{"claim_id": cid, "date_of_loss": (start + timedelta(days=after)).isoformat(), "cause": cause, "status": status,
                        "paid": float(paid), "outstanding_reserve": float(reserve)}
                       for cid, after, cause, status, paid, reserve in claims]}


def build_commercial_policies(today: date) -> dict:
    rows = [
        _commercial("CPL-6801", "Ivelet & Thorn Bookbinders Ltd", "2 Vellum Court, Marlow Reach, Meridia", "HL", 21,
                    "Bookbinding workshop and office.", "A", 900000, 2500, "no", 6000,
                    [("CCL-6901", 140, "Storm: broken glass in the workshop roof", "closed", 900, 0)], today),
        _commercial("CPL-6802", "Dunmarrow Catering Supplies Ltd", "Unit 7, Ladle Street, Tallowby, Meridia", "TC", 28,
                    "Warehouse for catering equipment and tableware.", "B", 1400000, 5000, "no", 10000,
                    [("CCL-6902", 80, "Escape of water from a ceiling pipe", "closed", 4600, 0),
                     ("CCL-6903", 215, "Theft of stock after a break-in", "closed", 3650, 0)], today),
        _commercial("CPL-6803", "Hartsease Garden Tools Ltd", "Hartsease Works, Spade Lane, Tallowby, Meridia", "TC", 33,
                    "Warehouse for garden tools.", "A", 1100000, 5000, "yes", 7500,
                    [("CCL-6904", 60, "Fork-lift truck struck a roller door", "closed", 1500, 0)], today),
        _commercial("CPL-6805", "Calloway & Finch Shopfitters Ltd", "Finch Yard, Counter Street, Port Ilvane, Meridia", "QR", 40,
                    "Workshop making shop counters and shelving.", "B", 1900000, 5000, "yes", 14000, [], today),
        _commercial("CPL-6806", "Merrowdown Marine Stores Ltd", "Merrowdown Slip, Port Ilvane, Meridia", "QR", 48,
                    "Warehouse and shop for boat engines and marine paint.", "A", 1000000, 2500, "no", 12500,
                    [("CCL-6905", 196, "Storm: flood water in the shop", "closed", 3875, 0),
                     ("CCL-6906", -9, "Theft of two outboard engines", "closed", 5625, 0)], today),
    ]
    return {r["policy_id"]: r for r in rows}


def build_renewals(today: date) -> dict:
    L = lambda ago: long_date(d_ago(today, ago))

    def change(ago, kind, by, text):
        return {"reported_on": d_ago(today, ago), "kind": kind, "reported_by": by, "text": text}

    rows = [
        ("RNW-6701", "CPL-6801", "underwriting", None, []),
        ("RNW-6702", "CPL-6802", "underwriting", None, []),
        ("RNW-6703", "CPL-6803", "underwriting", None,
         [change(150, "occupancy", BROKERS["TC"][0],
                 f"The broker wrote on {L(150)}: half of the warehouse is now let to a tenant, a tyre fitter, who stores car and van "
                 "tyres there. The insured keeps the other half for garden tools.")]),
        # A home policy and its claim, read from the policy and claims systems. The premium is kept here.
        ("RNW-6704", "POL-2007", "policy", 1240.0, []),
        ("RNW-6705", "CPL-6805", "underwriting", None,
         [change(45, "protections", BROKERS["QR"][0],
                 f"The broker wrote on {L(45)}: the sprinkler system has been out of service since {L(52)} while the water tank is "
                 "replaced. No date is given for its return.")]),
        ("RNW-6706", "CPL-6806", "underwriting", None, []),
    ]
    return {rid: {"renewal_id": rid, "status": "review_due", "policy_id": pid, "policy_held_in": held,
                  "expiring_premium_held_here": premium, "changes_reported": changes, "review_drafts": []}
            for rid, pid, held, premium, changes in rows}


def _ratio(cost: float, premium: float) -> float:
    return money(cost / premium * 100)


def renewal_pack(renewal: dict, data: dict, today_iso: str) -> dict:
    """Expiring terms, the period's claims with totals and loss ratios, the changes reported, and the renewal rules measured."""
    pid = renewal["policy_id"]
    if renewal["policy_held_in"] == "policy":
        p = data["policies"][pid]
        premium = renewal["expiring_premium_held_here"]
        sched = p["schedule"]
        if p["product"] == "home":
            total = money(sched["buildings_sum_insured"] + sched["contents_sum_insured"])
            insured_item = (f"Home at {p['address']}: buildings {usd(sched['buildings_sum_insured'])}, contents "
                            f"{usd(sched['contents_sum_insured'])}.")
        else:
            total = sched["sum_insured"]
            insured_item = f"{sched['insured_vehicle']}, registration {sched['registration']}."
        terms = {"policy_id": pid, "policy_held_in": "the policy system", "class_of_business": p["product"], "insured": p["holder"],
                 "address": p["address"], "insured_item": insured_item, "total_sum_insured": total, "deductible": sched["deductible"]}
        claims = []
        for c in data["claims"].values():
            if c["policy_id"] != pid:
                continue
            paid = money(sum(x["amount"] for x in c.get("payments", [])))
            declined = (c.get("decision") or {}).get("decision") == "declined"
            is_open = c["status"] != "closed" and not declined
            reserve = money(max(c["estimate"] - paid, 0.0)) if is_open else 0.0
            claims.append({"claim_id": c["claim_id"], "date_of_loss": c["loss_date"], "cause": c["claim_type_label"],
                           "status": "open" if is_open else ("declined" if declined else "closed"), "paid": paid,
                           "outstanding_reserve": reserve, "held_in": "the claims system"})
    else:
        p = data["uw_commercial_policies"][pid]
        premium = p["annual_premium"]
        sched = p["schedule"]
        terms = {"policy_id": pid, "policy_held_in": "this system", "class_of_business": p["class_of_business"], "insured": p["insured"],
                 "address": p["address"], "insured_item": sched["occupancy"], "construction_class": sched["construction_class"],
                 "sprinklers": sched["sprinklers"], "total_sum_insured": sched["total_sum_insured"], "deductible": sched["deductible"],
                 "broker": p["broker"]}
        claims = [{**c, "held_in": "the commercial claims ledger"} for c in p["claims"]]
    start, end, today = date.fromisoformat(p["period_start"]), date.fromisoformat(p["period_end"]), date.fromisoformat(today_iso)
    days = (end - today).days
    terms = {**terms, "period_start": p["period_start"], "period_end": p["period_end"], "annual_premium": premium, "currency": "USD",
             "days_until_the_period_ends": days,
             "sentence": f"The period runs from {long_date(p['period_start'])} to {long_date(p['period_end'])}, and ends "
                         f"{plural(days, 'day')} after {long_date(today_iso)}. The premium for the period is {usd(premium)}."}

    disagreements = []
    for c in claims:
        loss = date.fromisoformat(c["date_of_loss"])
        c["incurred"] = money(c["paid"] + c["outstanding_reserve"])
        c["date_of_loss_is_inside_the_period"] = start <= loss <= end
        if loss < start:
            n = (start - loss).days
            disagreements.append({"claim_id": c["claim_id"], "about": "date",
                                  "claims_record": f"Date of loss {long_date(c['date_of_loss'])}, booked to {pid}.",
                                  "policy_record": f"The period of {pid} started on {long_date(p['period_start'])}.",
                                  "sentence": f"The claims record gives {c['claim_id']} a date of loss of {long_date(c['date_of_loss'])}, "
                                              f"{plural(n, 'day')} before the period started on {long_date(p['period_start'])} by the "
                                              "policy record. The two records disagree: either the date of loss is wrong, or the "
                                              "claim does not belong to this period."})
        elif loss > end:
            n = (loss - end).days
            disagreements.append({"claim_id": c["claim_id"], "about": "date",
                                  "claims_record": f"Date of loss {long_date(c['date_of_loss'])}, booked to {pid}.",
                                  "policy_record": f"The period of {pid} ended on {long_date(p['period_end'])}.",
                                  "sentence": f"The claims record gives {c['claim_id']} a date of loss of {long_date(c['date_of_loss'])}, "
                                              f"{plural(n, 'day')} after the period ended on {long_date(p['period_end'])} by the "
                                              "policy record. The two records disagree."})

    def totals(rows):
        paid = money(sum(c["paid"] for c in rows))
        reserve = money(sum(c["outstanding_reserve"] for c in rows))
        cost = money(paid + reserve)
        return {"claims": len(rows), "open_claims": sum(1 for c in rows if c["status"] == "open"), "paid": paid,
                "outstanding_reserves": reserve, "incurred": cost, "loss_ratio_on_payments_percent": _ratio(paid, premium),
                "loss_ratio_percent": _ratio(cost, premium),
                "working": f"{usd(paid)} paid + {usd(reserve)} reserves = {usd(cost)}. {usd(cost)} / {usd(premium)} premium = "
                           f"{_ratio(cost, premium):,.2f} percent. On payments alone: {_ratio(paid, premium):,.2f} percent."}

    everything = totals(claims)
    disputed_ids = {x["claim_id"] for x in disagreements}
    undisputed = totals([c for c in claims if c["claim_id"] not in disputed_ids]) if disagreements else None

    def over(t):
        return t["loss_ratio_percent"] > LOSS_RATIO_LIMIT

    rules = []

    def rule(rule_id, applies, sentence, **extra):
        rules.append({"rule_id": rule_id, "heading": RENEWAL_RULES[rule_id]["heading"], "applies": applies, "sentence": sentence, **extra})

    if undisputed is not None and over(everything) != over(undisputed):
        rule("RN-1", "depends_on_the_disagreement",
             f"With every claim on the record the loss ratio is {everything['loss_ratio_percent']:,.2f} percent, above the limit of "
             f"{LOSS_RATIO_LIMIT:,.2f} percent. Leaving out {', '.join(sorted(disputed_ids))} it is "
             f"{undisputed['loss_ratio_percent']:,.2f} percent, not above the limit. Whether the rule applies depends on how the "
             "disagreement is settled.", measured=everything["loss_ratio_percent"], limit=LOSS_RATIO_LIMIT)
    elif over(everything):
        rule("RN-1", True, f"The loss ratio is {everything['loss_ratio_percent']:,.2f} percent, above the limit of "
                           f"{LOSS_RATIO_LIMIT:,.2f} percent: a referral to a senior underwriter is needed.",
             measured=everything["loss_ratio_percent"], limit=LOSS_RATIO_LIMIT)
    else:
        on = " It is exactly on the limit, which needs no referral." if everything["loss_ratio_percent"] == LOSS_RATIO_LIMIT else ""
        rule("RN-1", False, f"The loss ratio is {everything['loss_ratio_percent']:,.2f} percent, not above the limit of "
                            f"{LOSS_RATIO_LIMIT:,.2f} percent.{on}", measured=everything["loss_ratio_percent"], limit=LOSS_RATIO_LIMIT)
    changes = renewal["changes_reported"]
    for rule_id, kind, need in (("RN-2", "occupancy", "a survey is needed before terms are offered"),
                                ("RN-3", "protections", "a referral to a senior underwriter is needed")):
        hits = [c for c in changes if c["kind"] == kind]
        if hits:
            rule(rule_id, True, f"A change of the kind {kind} was reported on "
                                f"{' and '.join(long_date(c['reported_on']) for c in hits)}: {need}.")
        else:
            rule(rule_id, False, f"No change of the kind {kind} is reported since the period started.")
    if everything["open_claims"]:
        open_ids = [c["claim_id"] for c in claims if c["status"] == "open"]
        rule("RN-4", True, f"{' and '.join(open_ids)} {'is' if len(open_ids) == 1 else 'are'} open. Of the cost of "
                           f"{usd(everything['incurred'])}, {usd(everything['outstanding_reserves'])} is reserve and "
                           f"{usd(everything['paid'])} is paid. On payments alone the loss ratio is "
                           f"{everything['loss_ratio_on_payments_percent']:,.2f} percent; with the reserves it is "
                           f"{everything['loss_ratio_percent']:,.2f} percent. The reserve may move.")
    else:
        rule("RN-4", False, "No claim of the period is open, so no reserve is in the loss ratio.")
    if disagreements:
        rule("RN-5", True, "The claims record and the policy record disagree: " + " ".join(x["sentence"] for x in disagreements)
             + " Show both, choose neither, and ask the claims team.")
    else:
        rule("RN-5", False, "Every date of loss on the claims record is inside the period on the policy record.")
    applies = [r["rule_id"] for r in rules if r["applies"] is True]
    depends = [r["rule_id"] for r in rules if r["applies"] == "depends_on_the_disagreement"]
    if not applies and not depends:
        sentence = "No renewal rule applies. The renewal is ready for the underwriter, who decides the terms."
    else:
        sentence = (f"Rules that apply: {', '.join(applies) or 'none'}."
                    + (f" Depends on the disagreement: {', '.join(depends)}." if depends else ""))
    return {"expiring_terms": terms, "claims_of_the_period": claims,
            "claims_note": "" if claims else "No claim is recorded against this policy in the period.",
            "totals": everything, "totals_leaving_out_the_disputed_claims": undisputed,
            "record_disagreements": disagreements, "changes_reported": changes,
            "changes_note": "" if changes else "No change in the risk is reported since the period started.",
            "rules": rules, "rules_that_apply": applies, "rules_that_depend_on_the_disagreement": depends, "sentence": sentence,
            "what_this_is": "The figures of the expiring period set beside the renewal rules. It offers no terms: an underwriter decides."}


def renewal_expiry(renewal: dict, data: dict, today_iso: str) -> dict:
    """The policy of a renewal in brief, with the days until its period ends."""
    held = "policies" if renewal["policy_held_in"] == "policy" else "uw_commercial_policies"
    p = data[held][renewal["policy_id"]]
    days = (date.fromisoformat(p["period_end"]) - date.fromisoformat(today_iso)).days
    return {"insured": p.get("insured") or p.get("holder"), "class_of_business": p.get("class_of_business") or p.get("product"),
            "period_start": p["period_start"], "period_end": p["period_end"], "days_until_the_period_ends": days}


def build_underwriting(today: date) -> dict:
    return {
        "uw_guidelines": copy.deepcopy(GUIDELINES),
        "uw_appetite": copy.deepcopy(APPETITE),
        "uw_submissions": build_submissions(today),
        "uw_authority_levels": copy.deepcopy(AUTHORITY_LEVELS),
        "uw_referral_rules": copy.deepcopy(REFERRAL_RULES),
        "uw_referrals": build_referrals(today),
        "uw_precedents": build_precedents(today),
        "uw_renewal_rules": copy.deepcopy(RENEWAL_RULES),
        "uw_commercial_policies": build_commercial_policies(today),
        "uw_renewals": build_renewals(today),
    }
