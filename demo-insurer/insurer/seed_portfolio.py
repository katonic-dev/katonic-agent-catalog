"""Seed data, part 8: portfolio. The product catalogue with what depends on each section and rating factor, proposed product
changes, the experience of each pricing segment with the pricing method, and the exposure warehouse with the concentration limits.

The sums are here as well: what a proposed change touches, a loss ratio, the premium change that holds a target loss ratio,
the credibility of a segment, a query of the warehouse and the measure of the portfolio against each limit. The system calls
them, so an agent never adds, divides or compares.

Everything is invented: every product document, filing reference, person, segment and figure.
"""

from __future__ import annotations

import copy
import math
from datetime import date, timedelta

from .seed_health import COMPLETE_BENEFITS
from .seed_policy import WORDINGS, d_ago, long_date
from .seed_underwriting import GUIDELINES


def usd(amount: float) -> str:
    return f"USD {amount:,.2f}"


def r2(x: float) -> float:
    return round(x + 1e-9, 2)


def plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


class Refused(Exception):
    """A request the data cannot answer. The system turns it into a 409 with this sentence."""


# ================================================================ the product catalogue

CATALOGUE_HOW_TO_READ = (
    "The catalogue holds each product with its wording by section, its rating factors and the documents and systems that depend on "
    "it. A section id that ends in a clause number (SEC-8303-4.1) is one clause; one that ends in a section number (SEC-8303-4) is "
    "that section as a whole. A dependent item (DEP-..) carries one reference for each clause, section or rating factor it refers "
    "to, with a relation: quotes (it repeats the words or a figure), uses (it works from it), relies_on (it is built on the clause "
    "staying as it is), lists (it lists the clauses of a section) or is_filed (the section or factor is part of a filing with the "
    "regulator). A reference to a section as a whole says when it applies: on any change to a clause of the section, or only when a "
    "clause is added or removed. Where no item refers to a clause, the catalogue says so: then only the wording itself changes.")

CATALOGUE_NEVER_HOLDS = [
    "The rates themselves. The catalogue holds each rating factor and its levels, not what is charged.",
    "The text of a filing or of a reinsurance treaty. It holds the reference and a note of what each one covers or relies on.",
    "Policies, members and claims. It does not say how many customers a change reaches: the policy, health and claims systems do.",
    "A decision. A product change is approved by the product committee, not here.",
]

ITEM_KINDS = {
    "schedule_template": "Schedule template", "rating_table": "Rating table", "claims_checklist": "Claims checklist",
    "broker_guide": "Broker guide", "member_guide": "Member guide", "regulatory_filing": "Regulatory filing",
    "reinsurance_treaty": "Reinsurance treaty (note of terms)", "underwriting_guideline": "Underwriting guideline",
    "system": "System",
}

RELATIONS = ("quotes", "uses", "relies_on", "lists", "is_filed")
ANY_CHANGE, ADDED_OR_REMOVED = "any_change_to_a_clause_of_the_section", "a_clause_is_added_or_removed"

FILING_NOTICE = ("A change to a section that is part of a filing is notified to the Meridia Insurance Authority at least 30 days "
                 "before it has effect.")
RATES_NOT_HELD = ("Whether the filed rates must be filed again, and what the change does to them. The catalogue holds the filing's "
                  "reference and what it covers, not the filed rates.")
OTHER_LEVELS = ("What the rates would be with other levels of this factor. The catalogue holds the factor and its levels, not the "
                "rates.")

QUINCE = "Horatio Quince, Head of Policy Servicing"
AINSCOUGH = "Cuthbert Ainscough, pricing actuary"
FELDSPAR = "Araminta Feldspar, Head of Claims"
OCKENDEN = "Tiberius Ockenden, Head of Distribution"
LOCKHART = "Seraphina Lockhart, compliance officer"
TOLLAND = "Marguerite Tolland, reinsurance manager"
PRYCE = "Octavian Pryce, head of underwriting"
BRIGHTWATER = "Cordelia Brightwater, Head of Health Claims"


def _sid(product_id: str, tail: str) -> str:
    return f"SEC-{product_id[4:]}-{tail}"


def _fid(product_id: str, n: int) -> str:
    return f"FAC-{product_id[4:]}-{n}"


def _sections_from_clauses(product_id: str, clauses: list) -> list:
    """Sections of a wording: one row for each section as a whole, then one for each clause of it."""
    out, seen = [], []
    for c in clauses:
        number = c["clause"].split(".")[0]
        if number not in seen:
            seen.append(number)
            out.append({"section_id": _sid(product_id, number), "kind": "section", "clause": number, "part_of": None,
                        "heading": c["section"],
                        "text": f"Section {number} of the wording as a whole: every clause numbered {number}.x."})
        out.append({"section_id": _sid(product_id, c["clause"]), "kind": "clause", "clause": c["clause"],
                    "part_of": _sid(product_id, number), "heading": c["heading"], "text": c["text"]})
    return out


def _clauses(rows):
    return [{"clause": number, "section": section, "heading": heading, "text": text} for number, section, heading, text in rows]


# The commercial property wording is held here only: the policy system holds the private motor and home wordings.
COMMERCIAL_WORDING = _clauses([
    ("1.1", "What is covered", "Fire", "We pay for loss or damage caused by fire, lightning or explosion."),
    ("1.2", "What is covered", "Storm", "We pay for loss or damage caused by storm."),
    ("1.3", "What is covered", "Escape of water",
     "We pay for loss or damage caused by the sudden and accidental escape of water from a fixed water pipe, tank or appliance."),
    ("1.4", "What is covered", "Theft",
     "We pay for loss or damage caused by theft or attempted theft following forcible and violent entry to or exit from the premises."),
    ("2.1", "What is not covered", "Flood",
     "Loss or damage caused by flood: water from a river, a lake or the sea, or surface water after rain."),
    ("2.2", "What is not covered", "Unoccupied premises",
     "Loss or damage that happens after the premises have been unoccupied for more than 30 days in a row."),
    ("2.3", "What is not covered", "Wear and tear", "Wear and tear, and any damage that happened over a period of time."),
    ("3.1", "The most we pay", "Buildings, contents and stock",
     "The most we pay is the sum insured for buildings, for contents and for stock in the schedule."),
    ("3.2", "The most we pay", "Theft of stock", "The most we pay for theft of stock is USD 25,000 for any one claim."),
    ("4.1", "The deductible", "The deductible",
     "The deductible in the schedule is taken once from each claim. The lowest deductible we offer is USD 2,500 where the total sum "
     "insured is up to USD 1,000,000, and USD 5,000 above that."),
    ("5.1", "Conditions", "Telling us", "You must tell us about a loss within 30 days of the date it happened."),
    ("5.2", "Conditions", "Protections", "Sprinklers and alarms named in the schedule must be kept in working order."),
    ("5.3", "Conditions", "Governing law", "This policy is governed by the law of Meridia."),
])


def _benefit_sections(product_id: str) -> list:
    out = [{"section_id": _sid(product_id, "BENEFITS"), "kind": "section", "clause": "BENEFITS", "part_of": None,
            "heading": "Table of benefits", "text": "The table of benefits as a whole: every benefit BEN-F01 to BEN-F10."}]
    for b in COMPLETE_BENEFITS:
        text = " ".join(x for x in (b["limit_sentence"], b["member_share_sentence"], b["conditions"]) if x)
        out.append({"section_id": _sid(product_id, b["benefit_id"]), "kind": "clause", "clause": b["benefit_id"],
                    "part_of": _sid(product_id, "BENEFITS"), "heading": b["name"], "text": text})
    return out


def _factor(product_id, n, name, levels, wording_clauses=()):
    return {"factor_id": _fid(product_id, n), "name": name, "levels": levels,
            "wording_clauses_that_name_it": [{"section_id": _sid(product_id, clause), "says": says} for clause, says in wording_clauses]}


def _ref(target_id, relation, says, figures=(), applies_when=None, cannot_say=""):
    return {"target_id": target_id, "relation": relation, "says": says, "figures_quoted": [float(x) for x in figures],
            "applies_when": applies_when, "cannot_say": cannot_say}


def _item(item_id, product_id, kind, name, reference, owner, holds, does_not_hold, on_a_change, refs):
    return {"item_id": item_id, "product_id": product_id, "kind": kind, "kind_name": ITEM_KINDS[kind], "name": name,
            "reference": reference, "owner": owner, "the_catalogue_holds": holds, "the_catalogue_does_not_hold": does_not_hold,
            "on_a_change": on_a_change, "refers_to": refs}


def _filing_refs(product_id, section_tails, factor_numbers):
    refs = [_ref(_sid(product_id, t), "is_filed", "This section of the wording is part of the filing.", applies_when=ANY_CHANGE)
            for t in section_tails]
    refs += [_ref(_fid(product_id, n), "is_filed", "The filed rates use this rating factor.", cannot_say=RATES_NOT_HELD)
             for n in factor_numbers]
    return refs


def _guideline_item(item_id, product_id, rule_id, refs):
    rule = GUIDELINES[rule_id]
    return _item(item_id, product_id, "underwriting_guideline", f"Underwriting guideline {rule_id}: {rule['heading']}", rule_id, PRYCE,
                 f"The guideline as the underwriting system holds it: {rule['text']}",
                 "Which submissions and policies the guideline has been applied to.",
                 "The head of underwriting changes a guideline. Until then underwriters measure against the text as it stands.", refs)


MOT, HOM, COM, MED = "PRD-8301", "PRD-8302", "PRD-8303", "PRD-8304"


def build_products() -> dict:
    motor, home = WORDINGS["TMI-MOT-01"], WORDINGS["TMI-HOM-02"]
    products = [
        {"product_id": MOT, "name": "Private motor", "line_of_business": "private_motor",
         "wording": {"wording_id": "TMI-MOT-01", "title": motor["title"], "version": motor["version"], "held_in": "policy system"},
         "sections": _sections_from_clauses(MOT, motor["clauses"]),
         "rating_factors": [
             _factor(MOT, 1, "Age band of the driver", "under 25; 25 to 69; 70 and over",
                     [("4.2", "Clause 4.2 takes a further deductible when the driver is under 25: the same age line.")]),
             _factor(MOT, 2, "Vehicle group", "groups 1 to 20"),
             _factor(MOT, 3, "Region", "Port Ilvane; Marlow Reach; Tallowby; Saltmarsh Coast"),
             _factor(MOT, 4, "Years without a claim", "0, 1, 2, 3, 4, 5 or more"),
             _factor(MOT, 5, "Deductible chosen", "USD 250; USD 500; USD 1,000",
                     [("4.1", "Clause 4.1 takes the deductible in the schedule from each claim.")]),
         ]},
        {"product_id": HOM, "name": "Home buildings and contents", "line_of_business": "home",
         "wording": {"wording_id": "TMI-HOM-02", "title": home["title"], "version": home["version"], "held_in": "policy system"},
         "sections": _sections_from_clauses(HOM, home["clauses"]),
         "rating_factors": [
             _factor(HOM, 1, "Buildings sum insured band", "up to USD 250,000; USD 250,001 to 500,000; over USD 500,000"),
             _factor(HOM, 2, "Region", "Port Ilvane; Marlow Reach; Tallowby; Saltmarsh Coast"),
             _factor(HOM, 3, "Construction class", "A; B; C"),
             _factor(HOM, 4, "Deductible chosen", "USD 250; USD 500; USD 1,000",
                     [("4.1", "Clause 4.1 takes the deductible in the schedule from each claim.")]),
             _factor(HOM, 5, "Years without a claim", "0, 1, 2, 3 or more"),
         ]},
        {"product_id": COM, "name": "Commercial property", "line_of_business": "commercial_property",
         "wording": {"wording_id": "TMI-COM-03", "title": "Commercial Property Policy Wording", "version": "1",
                     "held_in": "this catalogue"},
         "sections": _sections_from_clauses(COM, COMMERCIAL_WORDING),
         "rating_factors": [
             _factor(COM, 1, "Construction class", "A; B; C"),
             _factor(COM, 2, "Total sum insured band", "up to USD 1,000,000; USD 1,000,001 to 2,500,000; over USD 2,500,000"),
             _factor(COM, 3, "Occupancy group", "offices and shops; warehouses; light manufacturing; workshops"),
             _factor(COM, 4, "Sprinklers", "yes; no", [("5.2", "Clause 5.2 says the protections in the schedule must be kept working.")]),
             _factor(COM, 5, "Deductible chosen", "USD 2,500; USD 5,000; USD 10,000",
                     [("4.1", "Clause 4.1 names the lowest deductible offered: the first step of this factor.")]),
         ]},
        {"product_id": MED, "name": "Group medical: Thornmere Health Complete", "line_of_business": "group_medical",
         "wording": {"wording_id": "TOB-COMPLETE", "title": "Table of benefits, Thornmere Health Complete", "version": "as the health "
                     "system holds it", "held_in": "health system"},
         "sections": _benefit_sections(MED),
         "rating_factors": [
             _factor(MED, 1, "Age band of the member", "under 30; 30 to 44; 45 to 59; 60 and over"),
             _factor(MED, 2, "Size of the scheme", "up to 50 members; 51 to 250; over 250"),
             _factor(MED, 3, "Region", "Port Ilvane; Marlow Reach; Tallowby; Saltmarsh Coast"),
         ]},
    ]
    return {p["product_id"]: {**p, "status": "on sale"} for p in products}


def build_items() -> dict:
    S, F = _sid, _fid
    lists_cover = "Lists what is covered, clause by clause."
    lists_not = "Lists what is not covered, clause by clause."
    items = [
        # ---- private motor
        _item("DEP-8401", MOT, "schedule_template", "Private motor schedule template", "TPL-MOT-SCH version 4", QUINCE,
              "The template and the clauses whose figures it prints.", "The schedules already issued.",
              "Policy servicing issues a new version of the template.",
              [_ref(S(MOT, "4.1"), "uses", "Prints the deductible the customer chose."),
               _ref(S(MOT, "3.1"), "uses", "Prints the sum insured."),
               _ref(S(MOT, "1.3"), "uses", "Prints the third party property limit.")]),
        _item("DEP-8402", MOT, "rating_table", "Private motor rating table", "RT-MOT-2026", AINSCOUGH,
              "Which rating factors the table uses and their levels.", "The rates.",
              "The pricing actuary rebuilds the table and signs it off.",
              [_ref(F(MOT, 1), "uses", "Holds a rate for each age band: under 25, 25 to 69, 70 and over.", [25, 70],
                    cannot_say=OTHER_LEVELS)] +
              [_ref(F(MOT, n), "uses", "Holds a rate for each level of this factor.", cannot_say=OTHER_LEVELS) for n in (2, 3, 4)] +
              [_ref(F(MOT, 5), "uses", "Holds a discount for each deductible: USD 250, USD 500, USD 1,000.", [250, 500, 1000],
                    cannot_say=OTHER_LEVELS)]),
        _item("DEP-8403", MOT, "claims_checklist", "Motor claims checklists", "claims system, checklists by claim type", FELDSPAR,
              "Which clauses each checklist step works from.", "The claims that were handled with it.",
              "The claims team changes the checklist in the claims system.",
              [_ref(S(MOT, "5.2"), "relies_on", "The theft checklist asks for the police report that clause 5.2 requires."),
               _ref(S(MOT, "5.1"), "quotes", "The first step checks that the loss was reported within 30 days.", [30]),
               _ref(S(MOT, "4.2"), "quotes", "The settlement step takes the further USD 300 where the driver was under 25.", [300, 25])]),
        _item("DEP-8404", MOT, "broker_guide", "Broker guide to private motor", "BG-MOT edition 6", OCKENDEN,
              "Which clauses and factors the guide quotes.", "Which brokers hold which edition.",
              "Distribution issues a new edition to brokers.",
              [_ref(F(MOT, 1), "quotes", "Tells brokers that a driver under 25 is rated in the young driver band.", [25]),
               _ref(S(MOT, "3.2"), "quotes", "Quotes the windscreen limit of USD 500.", [500]),
               _ref(S(MOT, "3.4"), "quotes", "Quotes the hire car limit of USD 40 a day for up to 10 days.", [40, 10]),
               _ref(S(MOT, "4.2"), "quotes", "Quotes the further USD 300 for a driver under 25.", [300, 25]),
               _ref(S(MOT, "1"), "lists", lists_cover, applies_when=ADDED_OR_REMOVED),
               _ref(S(MOT, "2"), "lists", lists_not, applies_when=ADDED_OR_REMOVED)]),
        _item("DEP-8405", MOT, "regulatory_filing", "Private motor filing with the Meridia Insurance Authority", "MIA-F-MOT-2025-02",
              LOCKHART, "The reference and what the filing covers: sections 1 to 4 of the wording, and the rates with every rating "
              "factor. Section 5, the conditions, is not part of the filing.",
              "The filed rates and the regulator's conditions.", FILING_NOTICE, _filing_refs(MOT, "1234", (1, 2, 3, 4, 5))),
        _item("DEP-8406", MOT, "system", "Quote screen of the policy administration system", "PAS quote screen, private motor", QUINCE,
              "Which factors and levels are fixed in the screen.", "The quotes that were given.",
              "A change request to the systems team: the levels are fixed in the screen, not read from the rating table.",
              [_ref(F(MOT, 1), "quotes", "The age bands are fixed in the screen: under 25, 25 to 69, 70 and over.", [25, 70]),
               _ref(F(MOT, 5), "quotes", "Offers the deductibles USD 250, USD 500 and USD 1,000.", [250, 500, 1000])]),
        # ---- home
        _item("DEP-8411", HOM, "schedule_template", "Home schedule template", "TPL-HOM-SCH version 3", QUINCE,
              "The template and the clauses whose figures it prints.", "The schedules already issued.",
              "Policy servicing issues a new version of the template.",
              [_ref(S(HOM, "4.1"), "uses", "Prints the deductible the customer chose."),
               _ref(S(HOM, "3.1"), "uses", "Prints the sums insured for buildings and contents."),
               _ref(S(HOM, "3.2"), "uses", "Prints the items listed above the single item limit.")]),
        _item("DEP-8412", HOM, "rating_table", "Home rating table", "RT-HOM-2026", AINSCOUGH,
              "Which rating factors the table uses, their levels, and the groups of perils that are rated.", "The rates.",
              "The pricing actuary rebuilds the table and signs it off.",
              [_ref(F(HOM, n), "uses", "Holds a rate for each level of this factor.", cannot_say=OTHER_LEVELS) for n in (1, 2, 3, 4, 5)] +
              [_ref(S(HOM, "1"), "uses", "Holds a rate for each group of perils in section 1: fire, storm or flood, escape of water, "
                    "theft.", applies_when=ADDED_OR_REMOVED,
                    cannot_say="What the rate for a new peril would be. The catalogue holds the groups of perils that are rated, "
                               "not the rates, and no group exists for a peril that is not in section 1 today.")]),
        _item("DEP-8413", HOM, "claims_checklist", "Home claims checklists", "claims system, checklists by claim type", FELDSPAR,
              "Which clauses each checklist works from.", "The claims that were handled with it.",
              "The claims team changes the checklist in the claims system.",
              [_ref(S(HOM, "1"), "uses", "One checklist for each kind of claim in section 1: fire, storm or flood, escape of water, "
                    "theft.", applies_when=ADDED_OR_REMOVED,
                    cannot_say="Which documents a claim for a new peril would need. No checklist exists for it."),
               _ref(S(HOM, "5.2"), "relies_on", "The theft checklist asks for the police report that clause 5.2 requires."),
               _ref(S(HOM, "2.2"), "quotes", "The escape of water and theft checklists ask how long the home was unoccupied, against "
                    "60 days.", [60])]),
        _item("DEP-8414", HOM, "broker_guide", "Broker guide to home", "BG-HOM edition 5", OCKENDEN,
              "Which clauses and factors the guide quotes.", "Which brokers hold which edition.",
              "Distribution issues a new edition to brokers.",
              [_ref(S(HOM, "1"), "lists", lists_cover, applies_when=ADDED_OR_REMOVED),
               _ref(S(HOM, "2"), "lists", lists_not, applies_when=ADDED_OR_REMOVED),
               _ref(S(HOM, "2.2"), "quotes", "Quotes the 60 days a home may be unoccupied.", [60]),
               _ref(S(HOM, "3.2"), "quotes", "Quotes the single item limit of USD 2,500.", [2500]),
               _ref(S(HOM, "3.4"), "quotes", "Quotes the trace and access limit of USD 1,500.", [1500]),
               _ref(S(HOM, "4.2"), "quotes", "Quotes the escape of water deductible of USD 500.", [500])]),
        _item("DEP-8415", HOM, "regulatory_filing", "Home filing with the Meridia Insurance Authority", "MIA-F-HOM-2025-01", LOCKHART,
              "The reference and what the filing covers: sections 1 to 4 of the wording, and the rates with every rating factor. "
              "Section 5, the conditions, is not part of the filing.",
              "The filed rates and the regulator's conditions.", FILING_NOTICE, _filing_refs(HOM, "1234", (1, 2, 3, 4, 5))),
        _item("DEP-8416", HOM, "reinsurance_treaty", "Household catastrophe treaty: note of terms", "TN-HOM-2026", TOLLAND,
              "A note of the clauses and perils the treaty names.", "The treaty itself. The reinsurance team holds it.",
              "The reinsurance manager asks the reinsurers before the change has effect.",
              [_ref(S(HOM, "1.2"), "relies_on", "The treaty protects storm and flood losses under clause 1.2."),
               _ref(S(HOM, "1.1"), "relies_on", "The treaty protects fire losses under clause 1.1."),
               _ref(S(HOM, "1"), "lists", "The note lists the perils the treaty protects: fire, and storm or flood. A peril that is "
                    "not on the list is kept by Thornmere in full.", applies_when=ADDED_OR_REMOVED,
                    cannot_say="Whether the treaty would protect a new peril. The catalogue holds a note of the perils the treaty "
                               "names, not the treaty.")]),
        # ---- commercial property
        _item("DEP-8421", COM, "schedule_template", "Commercial property schedule template", "TPL-COM-SCH version 2", QUINCE,
              "The template and the clauses whose figures it prints or checks.", "The schedules already issued.",
              "Policy servicing issues a new version of the template.",
              [_ref(S(COM, "4.1"), "quotes", "Prints the deductible, and refuses one below USD 2,500.", [2500]),
               _ref(S(COM, "3.1"), "uses", "Prints the sums insured for buildings, contents and stock."),
               _ref(S(COM, "5.2"), "uses", "Prints the sprinklers and alarms the policy relies on.")]),
        _item("DEP-8422", COM, "rating_table", "Commercial property rating table", "RT-COM-2026", AINSCOUGH,
              "Which rating factors the table uses, their levels, and the clauses it is built on.", "The rates.",
              "The pricing actuary rebuilds the table and signs it off.",
              [_ref(F(COM, n), "uses", "Holds a rate for each level of this factor.", cannot_say=OTHER_LEVELS) for n in (1, 2, 3, 4)] +
              [_ref(F(COM, 5), "uses", "Holds a discount for each deductible step. The steps start at USD 2,500: 2,500, 5,000, 10,000.",
                    [2500, 5000, 10000], cannot_say=OTHER_LEVELS),
               _ref(S(COM, "2.1"), "relies_on", "The rates hold no loading for flood, because clause 2.1 excludes it.",
                    cannot_say="What a rate for flood would be. The catalogue holds no flood rate: none exists.")]),
        _item("DEP-8423", COM, "claims_checklist", "Commercial property claims checklist", "CK-COM version 3", FELDSPAR,
              "Which clauses each checklist step works from.", "The claims that were handled with it.",
              "The claims team changes the checklist.",
              [_ref(S(COM, "5.1"), "quotes", "The first step checks that the loss was reported within 30 days.", [30]),
               _ref(S(COM, "2.1"), "relies_on", "Step 2 asks the adjuster to confirm that the damage is not flood, which clause 2.1 "
                    "excludes."),
               _ref(S(COM, "2.2"), "quotes", "Step 3 asks how long the premises were unoccupied, against 30 days.", [30])]),
        _item("DEP-8424", COM, "broker_guide", "Broker guide to commercial property", "BG-COM edition 3", OCKENDEN,
              "Which clauses and factors the guide quotes.", "Which brokers hold which edition.",
              "Distribution issues a new edition to brokers.",
              [_ref(S(COM, "4.1"), "quotes", "Tells brokers that deductibles start at USD 2,500.", [2500]),
               _ref(S(COM, "2.1"), "quotes", "Tells brokers that flood is not covered and must be placed elsewhere."),
               _ref(S(COM, "2.2"), "quotes", "Quotes the 30 days the premises may be unoccupied.", [30]),
               _ref(S(COM, "1"), "lists", lists_cover, applies_when=ADDED_OR_REMOVED),
               _ref(S(COM, "2"), "lists", lists_not, applies_when=ADDED_OR_REMOVED)]),
        _item("DEP-8425", COM, "regulatory_filing", "Commercial property wording filing with the Meridia Insurance Authority",
              "MIA-F-COM-2024-03", LOCKHART,
              "The reference and what the filing covers: sections 1 to 4 of the wording. Section 5, the conditions, is not part of the "
              "filing. Commercial property rates are not filed in Meridia, so no rating factor is part of it.",
              "The regulator's conditions.", FILING_NOTICE, _filing_refs(COM, "1234", ())),
        _item("DEP-8426", COM, "reinsurance_treaty", "Commercial property quota share treaty: note of terms", "TN-COM-2026", TOLLAND,
              "A note of the clauses the treaty relies on.", "The treaty itself. The reinsurance team holds it.",
              "The reinsurance manager asks the reinsurers before the change has effect.",
              [_ref(S(COM, "2.1"), "relies_on", "The treaty protects the commercial property account on the footing that flood is "
                    "excluded: the note names clause 2.1.",
                    cannot_say="Whether the reinsurers would agree to flood being covered, and on what terms. The catalogue holds a "
                               "note of the clauses the treaty relies on, not the treaty.")]),
        _guideline_item("DEP-8427", COM, "UG-6",
                        [_ref(S(COM, "4.1"), "quotes", "The guideline gives the same lowest deductibles as clause 4.1: USD 2,500 up to "
                              "a total sum insured of USD 1,000,000, and USD 5,000 above.", [2500, 5000])]),
        _guideline_item("DEP-8428", COM, "UG-5",
                        [_ref(S(COM, "2.1"), "uses", "The guideline keeps locations in flood zone 3 out. It was written while flood is "
                              "excluded.",
                              cannot_say="Whether flood zones 1 and 2 would stay within the guideline once flood is covered. UG-5 "
                                         "does not say.")]),
        _guideline_item("DEP-8429", COM, "UG-3",
                        [_ref(S(COM, "5.2"), "uses", "The guideline asks for sprinklers in working order, which clause 5.2 then "
                              "requires for the life of the policy."),
                         _ref(F(COM, 4), "uses", "The guideline reads the same sprinklers field that the factor rates on.")]),
        _guideline_item("DEP-8430", COM, "UG-1",
                        [_ref(F(COM, 1), "uses", "The guideline sets the most sum insured by construction class."),
                         _ref(F(COM, 2), "uses", "The guideline limits the total sum insured the bands are built on.")]),
        # ---- group medical
        _item("DEP-8431", MED, "member_guide", "Member guide to Thornmere Health Complete", "MG-COMP edition 4", BRIGHTWATER,
              "Which benefits the guide quotes.", "Which members hold which edition.",
              "The health team issues a new edition to the schemes.",
              [_ref(S(MED, "BEN-F08"), "quotes", "Tells members that maternity care can be used after 300 days of cover.", [300]),
               _ref(S(MED, "BEN-F07"), "quotes", "Quotes the 12 physiotherapy sessions in a benefit year.", [12]),
               _ref(S(MED, "BEN-F09"), "quotes", "Quotes the dental limit of USD 500 in a benefit year.", [500])]),
        _item("DEP-8432", MED, "rating_table", "Group medical rating table", "RT-MED-2026", AINSCOUGH,
              "Which rating factors the table uses, their levels, and the benefits it is built on.", "The rates.",
              "The pricing actuary rebuilds the table and signs it off.",
              [_ref(F(MED, n), "uses", "Holds a rate for each level of this factor.", cannot_say=OTHER_LEVELS) for n in (1, 2, 3)] +
              [_ref(S(MED, "BEN-F08"), "relies_on", "The maternity rate assumes a waiting period of 300 days.", [300],
                    cannot_say="What the maternity rate would be with another waiting period. The catalogue holds what the rate "
                               "assumes, not the rate.")]),
        _item("DEP-8433", MED, "system", "Health claims engine: waiting period rule", "claims engine rule WP-MAT", BRIGHTWATER,
              "Which benefits the rule works from, and the figure fixed in it.", "The claims the rule has held.",
              "A change request to the systems team: the figure is fixed in the rule.",
              [_ref(S(MED, "BEN-F08"), "quotes", "Holds a claim for maternity care where the member has fewer than 300 days of cover.",
                    [300])]),
        _item("DEP-8434", MED, "schedule_template", "Scheme schedule and member certificate template", "TPL-MED-CERT version 2", QUINCE,
              "The template and the benefits whose figures it prints.", "The certificates already issued.",
              "Policy servicing issues a new version of the template.",
              [_ref(S(MED, "BEN-F08"), "quotes", "Prints the date from which maternity care can be used, worked out from 300 days.",
                    [300]),
               _ref(S(MED, "BEN-F01"), "uses", "Prints the hospital stay limit.")]),
        _item("DEP-8435", MED, "regulatory_filing", "Group medical filing with the Meridia Insurance Authority", "MIA-F-MED-2025-04",
              LOCKHART, "The reference and what the filing covers: the whole table of benefits, and the rates with every rating "
              "factor.", "The filed rates and the regulator's conditions.", FILING_NOTICE, _filing_refs(MED, ["BENEFITS"], (1, 2, 3))),
        _item("DEP-8436", MED, "claims_checklist", "Pre-authorisation form and the medical policies MP-301 to MP-303",
              "health system", BRIGHTWATER, "Which benefits the form and the medical policies work from.",
              "The requests that were decided.", "The medical reviewer changes a medical policy.",
              [_ref(S(MED, "BEN-F05"), "uses", "Medical policy MP-301 is for an MRI scan of the lower back."),
               _ref(S(MED, "BEN-F07"), "quotes", "Medical policy MP-302 is for physiotherapy beyond 12 sessions.", [12]),
               _ref(S(MED, "BEN-F02"), "uses", "Medical policy MP-303 is for a day-case knee procedure.")]),
        _item("DEP-8437", MED, "system", "Provider contracts and tariffs", "health system, PRV-5101 and PRV-5102", BRIGHTWATER,
              "Which benefits the tariffs price.", "The invoices that were checked.", "The provider manager agrees a change in writing.",
              [_ref(S(MED, "BEN-F03"), "uses", "The tariffs price a first consultation and a follow-up."),
               _ref(S(MED, "BEN-F06"), "uses", "The contracts bill medicines at the tariff less a percentage.")]),
    ]
    return {i["item_id"]: i for i in items}


CHANGE_KINDS = {
    "change_a_figure": "A figure in a clause changes.",
    "add_a_clause": "A new clause is added to a section.",
    "remove_a_clause": "A clause is taken out.",
    "reword_a_clause": "The words of a clause change and its meaning does not.",
    "change_a_rating_factor": "The levels of a rating factor change.",
}


def build_change_requests(today: date) -> dict:
    L = lambda n: long_date(d_ago(today, n))
    S, F = _sid, _fid

    def change(change_id, ago, who, role, product_id, kind, title, text, targets, current=None, proposed=None, unit="", new_term=""):
        return {"change_id": change_id, "status": "proposed", "received": d_ago(today, ago),
                "proposed_by": {"name": who, "role": role}, "product_id": product_id, "kind_of_change": kind,
                "kind_of_change_in_words": CHANGE_KINDS[kind], "title": title, "text": text, "targets": targets,
                "current_figure": float(current) if current is not None else None,
                "proposed_figure": float(proposed) if proposed is not None else None, "figure_is_in": unit,
                "new_term": new_term}

    rows = [
        change("PCR-8501", 6, "Lavinia Thrupp", "product manager, commercial lines", COM, "change_a_figure",
               "Raise the lowest commercial property deductible to USD 5,000",
               f"Proposal of {L(6)}. Clause 4.1 of TMI-COM-03 offers a lowest deductible of USD 2,500 where the total sum insured is up "
               "to USD 1,000,000. We propose USD 5,000 for every sum insured, so that the first step of the deductible factor is "
               "USD 5,000 as well. Small claims cost more to handle than they pay.",
               [S(COM, "4.1"), F(COM, 5)], 2500, 5000, "USD"),
        change("PCR-8502", 5, "Ottilie Farnaby", "product manager, personal lines", HOM, "add_a_clause",
               "Add accidental breakage of fixed glass to the home wording",
               f"Proposal of {L(5)}. Add a clause to section 1 of TMI-HOM-02: we pay for accidental breakage of fixed glass in windows, "
               "doors and conservatories. Two competitors give it as standard.",
               [S(HOM, "1")], new_term="glass"),
        change("PCR-8503", 4, "Lavinia Thrupp", "product manager, commercial lines", COM, "remove_a_clause",
               "Take the flood exclusion out of the commercial property wording",
               f"Proposal of {L(4)}. Remove clause 2.1 of TMI-COM-03 so that flood is covered as storm is. Brokers ask for it on every "
               "second quote.",
               [S(COM, "2.1")]),
        change("PCR-8504", 3, "Ignatia Culpepper", "product manager, health", MED, "change_a_figure",
               "Shorten the maternity waiting period of Thornmere Health Complete to 180 days",
               f"Proposal of {L(3)}. Benefit BEN-F08, maternity care, can be used only after 300 days of cover in a row. We propose "
               "180 days. Two large schemes have asked for it at renewal.",
               [S(MED, "BEN-F08")], 300, 180, "days"),
        change("PCR-8505", 2, "Lavinia Thrupp", "product manager, commercial lines", COM, "reword_a_clause",
               "Put the governing law clause of the commercial property wording into plainer words",
               f"Proposal of {L(2)}. Clause 5.3 of TMI-COM-03 reads: This policy is governed by the law of Meridia. We propose: The law "
               "of Meridia applies to this policy. The meaning does not change.",
               [S(COM, "5.3")]),
        change("PCR-8506", 1, "Ottilie Farnaby", "product manager, personal lines", MOT, "change_a_rating_factor",
               "Move the young driver age line of private motor from 25 to 23",
               f"Proposal of {L(1)}. The age band factor of private motor rates a driver under 25 as a young driver. We propose under "
               "23, so that drivers of 23 and 24 are rated in the main band. What would this do to the rates we have filed?",
               [F(MOT, 1)], 25, 23, "years of age"),
    ]
    return {c["change_id"]: c for c in rows}


# ---------------------------------------------------------------- the dependency read

def find_target(data: dict, target_id: str):
    """(product, record, kind) of a section, a clause or a rating factor; None when the catalogue holds no such id."""
    for product in data["pf_products"].values():
        for s in product["sections"]:
            if s["section_id"] == target_id:
                return product, s, s["kind"]
        for f in product["rating_factors"]:
            if f["factor_id"] == target_id:
                return product, f, "rating_factor"
    return None


def _target_view(product, record, kind):
    if kind == "rating_factor":
        return {"target_id": record["factor_id"], "kind": kind, "product_id": product["product_id"], "product": product["name"],
                "heading": record["name"], "text": f"Levels: {record['levels']}."}
    return {"target_id": record["section_id"], "kind": kind, "product_id": product["product_id"], "product": product["name"],
            "clause": record["clause"], "heading": record["heading"], "text": record["text"], "part_of": record["part_of"]}


def _item_brief(item):
    return {"item_id": item["item_id"], "kind": item["kind"], "name": item["name"], "reference": item["reference"],
            "owner": item["owner"]}


def _refs_on(data, product_id, target_ids):
    """Every (item, reference) of the product whose reference names one of the targets, in the order of the item ids."""
    return [(item, ref) for item in data["pf_items"].values() if item["product_id"] == product_id
            for ref in item["refers_to"] if ref["target_id"] in target_ids]


def _group(pairs, current=None):
    """Pairs of (item, reference) gathered into one row for each item."""
    rows: dict = {}
    for item, ref in pairs:
        row = rows.setdefault(item["item_id"], {**_item_brief(item), "the_catalogue_holds": item["the_catalogue_holds"],
                                                "the_catalogue_does_not_hold": item["the_catalogue_does_not_hold"],
                                                "on_a_change": item["on_a_change"], "references": []})
        view = dict(ref)
        if current is not None:
            view["quotes_the_current_figure"] = current in ref["figures_quoted"]
        row["references"].append(view)
    return list(rows.values())


def what_refers_to(data: dict, target_id: str) -> dict | None:
    found = find_target(data, target_id)
    if not found:
        return None
    product, record, kind = found
    pid = product["product_id"]
    direct = _group(_refs_on(data, pid, {target_id}))
    out = {"target": _target_view(product, record, kind), "items_that_refer_to_it": direct}
    names = {target_id: record.get("heading") or record.get("name")}
    if kind == "clause":
        out["items_that_refer_to_its_section_as_a_whole"] = _group(_refs_on(data, pid, {record["part_of"]}))
        out["section_note"] = ("A reference to the section as a whole applies as its applies_when says: on any change to a clause of "
                               "the section, or only when a clause is added or removed.")
    elif kind == "section":
        clauses = {s["section_id"] for s in product["sections"] if s["part_of"] == target_id}
        out["items_that_refer_to_a_clause_of_it"] = _group(_refs_on(data, pid, clauses))
    else:
        out["wording_clauses_that_name_it"] = [
            {**c, "items_that_refer_to_this_clause": [r["item_id"] for r in _group(_refs_on(data, pid, {c["section_id"]}))]}
            for c in record["wording_clauses_that_name_it"]]
    mine = {r["item_id"] for r in direct}
    others = [_item_brief(i) for i in data["pf_items"].values() if i["product_id"] == pid and i["item_id"] not in mine]
    relations = [ref["relation"] for row in direct for ref in row["references"]]
    out["items_of_the_product_that_do_not_refer_to_it"] = others
    out["counts"] = {"items_that_refer_to_it": len(direct), "that_quote_it": relations.count("quotes"),
                     "that_rely_on_it": relations.count("relies_on"), "items_of_the_product_that_do_not": len(others)}
    name = names[target_id]
    if direct:
        out["sentence"] = (f"{plural(len(direct), 'item')} of the catalogue {'refers' if len(direct) == 1 else 'refer'} to {target_id} "
                           f"({name}): {', '.join(r['item_id'] for r in direct)}.")
    else:
        out["sentence"] = f"No item of the catalogue refers to {target_id} ({name}). A change to it changes the wording itself only."
    return out


SEARCH_STOP_WORDS = {"the", "and", "for", "with", "what", "which", "that", "does", "refer", "refers", "product", "change", "clause",
                     "section", "our", "are", "any", "all", "this", "from", "have", "has", "how", "will", "would"}


def search_catalogue(data: dict, text: str) -> dict:
    raw = (text or "").lower()
    for ch in ",.?:;()'\"":
        raw = raw.replace(ch, " ")
    words = [w for w in raw.split() if len(w) > 2 and w not in SEARCH_STOP_WORDS]
    rows = []
    for product in data["pf_products"].values():
        pid = product["product_id"]
        for s in product["sections"]:
            if s["kind"] == "clause":
                rows.append(({"kind": "clause", "id": s["section_id"], "product_id": pid, "heading": s["heading"], "text": s["text"]},
                             f"{s['section_id']} {s['heading']} {s['text']}"))
        for f in product["rating_factors"]:
            rows.append(({"kind": "rating_factor", "id": f["factor_id"], "product_id": pid, "heading": f["name"],
                          "text": f"Levels: {f['levels']}."}, f"{f['factor_id']} {f['name']} {f['levels']}"))
    for item in data["pf_items"].values():
        says = " ".join(ref["says"] for ref in item["refers_to"])
        rows.append(({"kind": item["kind"], "id": item["item_id"], "product_id": item["product_id"], "heading": item["name"],
                      "text": f"{item['reference']}. {says}"}, f"{item['item_id']} {item['name']} {item['reference']} {says}"))
    hits = []
    for row, hay in rows:
        matched = [w for w in words if w in hay.lower()]
        if matched or not words:
            hits.append({**row, "matched_words": matched})
    hits.sort(key=lambda r: -len(r["matched_words"]))
    note = ""
    if words and not hits:
        note = "No clause, rating factor or dependent item of the catalogue names any of these words. The catalogue is silent on them."
    return {"count": len(hits), "items": hits, "searched_for": text or "", "words_used": words, "note": note}


def change_impact(data: dict, change: dict) -> dict:
    """What a proposed change touches: worked out from the references of the catalogue, never from the proposal's own words."""
    product = data["pf_products"][change["product_id"]]
    pid, kind_of_change, current = product["product_id"], change["kind_of_change"], change["current_figure"]
    targets, pairs, same_thing = [], [], []
    for target_id in change["targets"]:
        _, record, kind = find_target(data, target_id)
        targets.append(_target_view(product, record, kind))
        if kind == "clause":
            pairs += _refs_on(data, pid, {target_id})
            pairs += [(i, r) for i, r in _refs_on(data, pid, {record["part_of"]})
                      if r["applies_when"] == ANY_CHANGE or (r["applies_when"] == ADDED_OR_REMOVED and kind_of_change == "remove_a_clause")]
        elif kind == "section":
            pairs += _refs_on(data, pid, {target_id})
        else:
            pairs += _refs_on(data, pid, {target_id})
            for c in record["wording_clauses_that_name_it"]:
                if c["section_id"] not in change["targets"]:
                    same_thing.append({**c, "items_that_refer_to_this_clause":
                                       [r["item_id"] for r in _group(_refs_on(data, pid, {c["section_id"]}))],
                                       "note": "The proposal does not name this clause. Whether it changes as well is a question for "
                                               "the person who proposed the change."})
    pairs.sort(key=lambda p: p[0]["item_id"])
    touched = _group(pairs, current)
    ids = [r["item_id"] for r in touched]
    not_touched = [_item_brief(i) for i in data["pf_items"].values() if i["product_id"] == pid and i["item_id"] not in ids]
    quoting = [r["item_id"] for r in touched if any(ref.get("quotes_the_current_figure") for ref in r["references"])]
    relying = [r["item_id"] for r in touched if any(ref["relation"] == "relies_on" for ref in r["references"])]
    cannot = []
    for row in touched:
        for ref in row["references"]:
            if ref["cannot_say"] and (row["item_id"], ref["cannot_say"]) not in [(c["item_id"], c["cannot_say"]) for c in cannot]:
                cannot.append({"item_id": row["item_id"], "owner": row["owner"], "cannot_say": ref["cannot_say"]})
    for c in same_thing:
        cannot.append({"item_id": None, "owner": f"{change['proposed_by']['name']}, {change['proposed_by']['role']}",
                       "cannot_say": f"Whether {c['section_id']} changes as well. {c['says']} The proposal does not name it."})
    new_term = None
    if change["new_term"]:
        found = search_catalogue(data, change["new_term"])["items"]
        here = [f["id"] for f in found if f["product_id"] == pid]
        elsewhere = [f["id"] for f in found if f["product_id"] != pid]
        if here:
            sentence = f"This product's part of the catalogue names '{change['new_term']}' in: {', '.join(here)}."
        else:
            sentence = (f"Nothing in this product's part of the catalogue names '{change['new_term']}': no clause, no rating factor "
                        "and no dependent item.")
            if elsewhere:
                sentence += (f" It is named for another product ({', '.join(elsewhere)}), which says nothing about this one.")
            cannot.append({"item_id": None, "owner": AINSCOUGH,
                           "cannot_say": f"What is charged for the new cover. No rating factor of this product names "
                                         f"'{change['new_term']}'."})
        new_term = {"term": change["new_term"], "named_in_this_product": here, "named_in_other_products": elsewhere,
                    "sentence": sentence}
    wording = product["wording"]
    if touched:
        sentence = (f"{change['change_id']} touches the wording {wording['wording_id']} itself and {plural(len(touched), 'item')} of the "
                    f"catalogue: {', '.join(ids)}.")
        if relying:
            sentence += (f" {plural(len(relying), 'item')} {'relies' if len(relying) == 1 else 'rely'} on what is changed staying as it "
                         f"is: {', '.join(relying)}.")
        if current is not None:
            sentence += (f" {plural(len(quoting), 'item')} {'quotes' if len(quoting) == 1 else 'quote'} the current figure "
                         f"{current:,.0f}" + (f": {', '.join(quoting)}." if quoting else "."))
    else:
        sentence = (f"{change['change_id']} touches the wording {wording['wording_id']} itself and nothing else: no item of the "
                    "catalogue refers to what it changes.")
    return {"targets": targets, "the_wording_itself": wording, "items_touched": touched, "items_of_the_product_not_touched": not_touched,
            "wording_clauses_that_name_the_same_thing": same_thing, "the_new_term_in_the_catalogue": new_term,
            "what_the_catalogue_cannot_say": cannot,
            "counts": {"items_touched": len(touched), "items_that_quote_the_current_figure": len(quoting),
                       "items_that_rely_on_what_is_changed": len(relying), "items_of_the_product_not_touched": len(not_touched),
                       "questions_the_catalogue_cannot_answer": len(cannot)},
            "items_that_quote_the_current_figure": quoting, "items_that_rely_on_what_is_changed": relying, "sentence": sentence}


# ================================================================ pricing

FULL_CREDIBILITY_CLAIMS = 1000
RELIABLE_FROM_CLAIMS = 250
PROFIT_MARGIN_PERCENT = 5.0
YEARS_HELD = 3

PRICING_ASSUMPTIONS = {
    "private_motor": {"claims_trend_percent": 5.0, "expense_ratio_percent": 25.0},
    "home": {"claims_trend_percent": 4.0, "expense_ratio_percent": 30.0},
    "commercial_property": {"claims_trend_percent": 4.0, "expense_ratio_percent": 28.0},
    "motor_fleet": {"claims_trend_percent": 6.0, "expense_ratio_percent": 22.0},
}

PRICING_HOW_TO_READ = ("The pricing method has numbered rules PM-1 to PM-8. The system applies them and returns every figure with its "
                       "working and every assumption by name. Nothing here changes a rate: the pricing actuary signs off.")


def experience_years(today: date) -> list[int]:
    return [today.year - n for n in range(YEARS_HELD, 0, -1)]


def rating_year(today: date) -> int:
    return today.year + 1


def build_pricing_method(today: date) -> dict:
    years, new = experience_years(today), rating_year(today)
    rules = [
        ("PM-1", "Loss ratio", "The loss ratio of a segment is its incurred claims divided by its earned premium, as a percentage to "
                               "two decimal places."),
        ("PM-2", "The experience that is read", f"The experience holds complete accident years only: {years[0]}, {years[1]} and "
                 f"{years[2]}. Every year held is read unless fewer are asked for. A year that is not complete is not held."),
        ("PM-3", "Claims trend", f"Incurred claims are carried forward to {new}, the year the new rates apply, at the annual claims "
                 "trend, compounded from the middle of the years read to the middle of that year. With every year read that is 3 "
                 "years."),
        ("PM-4", "Target loss ratio", "The target loss ratio is the one asked for. Where none is asked for it is 100 percent less the "
                 f"expense ratio less a profit margin of {PROFIT_MARGIN_PERCENT:.0f} percent."),
        ("PM-5", "Premium change needed", "The premium change needed is the trended loss ratio divided by the target loss ratio, less "
                 "one. The premium needed is the trended incurred claims divided by the target loss ratio."),
        ("PM-6", "Target already met", "Where the trended loss ratio is at or below the target, the target is met and the premium "
                 "change needed is zero. The method works out no decrease: that is a commercial decision."),
        ("PM-7", "Credibility", f"Credibility is the square root of the number of claims in the years read divided by "
                 f"{FULL_CREDIBILITY_CLAIMS:,}, and never more than 1. A segment with fewer than {RELIABLE_FROM_CLAIMS} claims "
                 "(credibility under 0.50) is too thin: its figures are shown and marked as not reliable alone, and the pricing "
                 f"actuary decides what to set beside them. Exactly {RELIABLE_FROM_CLAIMS} claims is enough."),
        ("PM-8", "Who decides", "A figure worked out here is an indication. The pricing actuary signs off a rate change and the "
                 "product committee approves it."),
    ]
    return {rule_id: {"rule_id": rule_id, "heading": heading, "text": text} for rule_id, heading, text in rules}


def build_segments(today: date) -> dict:
    years = experience_years(today)

    def seg(segment_id, name, product, exposure_unit, rows, note=""):
        return {"segment_id": segment_id, "name": name, "product": product, "exposure_unit": exposure_unit, "note": note,
                "experience": [{"year": y, "earned_premium": float(ep), "incurred_claims": float(inc), "claims": n,
                                "exposure": float(exp)} for y, (ep, inc, n, exp) in zip(years, rows)]}

    rows = [
        seg("SEG-8601", "Private motor, drivers aged 25 and over", "private_motor", "vehicle years",
            [(4200000, 2730000, 1180, 7000), (4500000, 3060000, 1240, 7300), (4800000, 3410000, 1310, 7600)]),
        seg("SEG-8602", "Private motor, drivers under 25", "private_motor", "vehicle years",
            [(600000, 510000, 210, 520), (640000, 560000, 225, 545), (690000, 640000, 240, 570)]),
        seg("SEG-8603", "Home, Port Ilvane, Marlow Reach and Tallowby", "home", "policy years",
            [(2400000, 1150000, 610, 1250), (2500000, 1180000, 640, 1300), (2600000, 1250000, 655, 1330)]),
        seg("SEG-8604", "Home, Saltmarsh Coast", "home", "policy years",
            [(150000, 60000, 14, 125), (160000, 310000, 21, 132), (170000, 75000, 11, 140)],
            note="A small book on the coast. One storm in the middle year makes up most of that year's claims."),
        seg("SEG-8605", "Commercial property, all regions", "commercial_property", "policy years",
            [(3000000, 1900000, 95, 330), (3200000, 2150000, 104, 350), (3300000, 2000000, 101, 366)]),
        seg("SEG-8606", "Motor fleet, all regions", "motor_fleet", "vehicle years",
            [(1800000, 1260000, 80, 1500), (1900000, 1380000, 84, 1560), (2000000, 1500000, 86, 1620)]),
    ]
    return {s["segment_id"]: s for s in rows}


EXPERIENCE_SPLIT = ("The experience is split by product and by the named segments only: driver age band for private motor (under 25, "
                    "25 and over) and the Saltmarsh Coast against the other regions for home. It is not split by fuel type, vehicle "
                    "age, postcode, broker or month, and it holds no year that is not complete.")


def parse_years(text: str | None, held: list[int]) -> list[int]:
    raw = (text or "").replace(";", ",").replace(" and ", ",").replace(" to ", "-").replace(" ", "")
    if not raw or raw.lower() == "all":
        return list(held)
    wanted: list[int] = []
    for part in raw.split(","):
        if not part:
            continue
        ends = part.split("-")
        if not all(e.isdigit() for e in ends) or len(ends) > 2:
            raise Refused(f"{text} is not a list of years. Give years as {held[0]},{held[-1]} or {held[0]}-{held[-1]}, or leave it "
                          "empty for every year held. Nothing was worked out.")
        span = range(int(ends[0]), int(ends[-1]) + 1)
        wanted += [y for y in span if y not in wanted]
    missing = [y for y in wanted if y not in held]
    if missing or not wanted:
        raise Refused(f"The experience holds the complete accident years {', '.join(str(y) for y in held)} only. "
                      f"{', '.join(str(y) for y in missing)} {'is' if len(missing) == 1 else 'are'} not held: a year that is not "
                      "complete, or one before the experience starts, cannot be read. Nothing was worked out and no figure is "
                      "estimated.")
    return sorted(wanted)


def credibility(claims: int, years: list[int]) -> dict:
    z = min(1.0, math.sqrt(claims / FULL_CREDIBILITY_CLAIMS))
    reliable = claims >= RELIABLE_FROM_CLAIMS
    span = ", ".join(str(y) for y in years)
    if reliable:
        sentence = (f"{claims:,} claims in {span}: at or above the {RELIABLE_FROM_CLAIMS} the method needs (PM-7). Credibility "
                    f"{z:.2f}. The figures can be relied on.")
    else:
        sentence = (f"{claims:,} claims in {span}: {RELIABLE_FROM_CLAIMS - claims} short of the {RELIABLE_FROM_CLAIMS} the method "
                    f"needs (PM-7). Credibility {z:.2f}, under 0.50. The segment is too thin: its figures are not reliable alone.")
    return {"rule_id": "PM-7", "claims_in_the_years_read": claims, "claims_for_full_credibility": FULL_CREDIBILITY_CLAIMS,
            "claims_needed_to_rely_on_a_figure": RELIABLE_FROM_CLAIMS, "credibility": round(z, 2), "credibility_threshold": 0.50,
            "reliable": reliable, "claims_short_of_the_threshold": max(0, RELIABLE_FROM_CLAIMS - claims), "sentence": sentence}


def segment_experience(segment: dict, years: list[int]) -> dict:
    unit = segment["exposure_unit"]
    rows = []
    for r in segment["experience"]:
        if r["year"] not in years:
            continue
        ratio = r2(100 * r["incurred_claims"] / r["earned_premium"])
        rows.append({**r, "loss_ratio_percent": ratio,
                     "claims_per_100_exposure_units": r2(100 * r["claims"] / r["exposure"]),
                     "average_cost_of_a_claim": r2(r["incurred_claims"] / r["claims"]),
                     "average_premium": r2(r["earned_premium"] / r["exposure"]),
                     "working": f"{r['year']}: {usd(r['incurred_claims'])} / {usd(r['earned_premium'])} = {ratio:.2f} percent."})
    ep, inc = sum(r["earned_premium"] for r in rows), sum(r["incurred_claims"] for r in rows)
    claims, exposure = sum(r["claims"] for r in rows), sum(r["exposure"] for r in rows)
    ratio = r2(100 * inc / ep)
    return {"segment_id": segment["segment_id"], "segment": segment["name"], "product": segment["product"], "exposure_unit": unit,
            "note": segment["note"], "years_read": years, "by_year": rows,
            "totals": {"earned_premium": r2(ep), "incurred_claims": r2(inc), "claims": claims, "exposure": r2(exposure),
                       "loss_ratio_percent": ratio, "claims_per_100_exposure_units": r2(100 * claims / exposure),
                       "average_cost_of_a_claim": r2(inc / claims), "average_premium": r2(ep / exposure),
                       "working": f"{usd(inc)} / {usd(ep)} = {ratio:.2f} percent (PM-1)."},
            "credibility": credibility(claims, years)}


def _in_range(name, value, low, high):
    if not (low <= value <= high):
        raise Refused(f"{name} of {value:g} percent is outside what the method works with ({low:g} to {high:g} percent). Nothing "
                      "was worked out.")


def premium_change(segment: dict, today: date, years: list[int], target: float | None = None, expense: float | None = None,
                   trend: float | None = None) -> dict:
    defaults = PRICING_ASSUMPTIONS[segment["product"]]
    exp_given, trend_given, target_given = expense is not None, trend is not None, target is not None
    expense = defaults["expense_ratio_percent"] if expense is None else float(expense)
    trend = defaults["claims_trend_percent"] if trend is None else float(trend)
    _in_range("An expense ratio", expense, 0, 60)
    _in_range("A claims trend", trend, -10, 25)
    if target is None:
        target = 100.0 - expense - PROFIT_MARGIN_PERCENT
    target = float(target)
    _in_range("A target loss ratio", target, 20, 100)
    seen = segment_experience(segment, years)
    ep, inc = seen["totals"]["earned_premium"], seen["totals"]["incurred_claims"]
    new = rating_year(today)
    trend_years = new - sum(years) / len(years)

    def trended_ratio(t):
        return 100 * inc * (1 + t / 100) ** trend_years / ep

    factor = (1 + trend / 100) ** trend_years
    trended_inc = inc * factor
    trended = trended_ratio(trend)
    met = r2(trended) <= r2(target)
    raw_change = 0.0 if met else 100 * (trended / target - 1)
    needed = ep if met else trended_inc / target * 100
    cred = seen["credibility"]
    src = lambda given: "given in the question" if given else "the method's default for this product"
    assumptions = [
        {"name": "target_loss_ratio_percent", "value": r2(target),
         "source": "given in the question" if target_given else f"worked out under PM-4: 100 less the expense ratio of {expense:g} "
                   f"less the profit margin of {PROFIT_MARGIN_PERCENT:g}"},
        {"name": "expense_ratio_percent", "value": r2(expense), "source": src(exp_given)},
        {"name": "claims_trend_percent_a_year", "value": r2(trend), "source": src(trend_given)},
        {"name": "profit_margin_percent", "value": PROFIT_MARGIN_PERCENT, "source": "fixed by the method (PM-4)"},
        {"name": "years_read", "value": years, "source": "given in the question" if len(years) < YEARS_HELD else "every year held (PM-2)"},
        {"name": "rating_year", "value": new, "source": "the year the new rates apply (PM-3)"},
        {"name": "trend_years", "value": r2(trend_years),
         "source": f"from the middle of the years read to the middle of {new} (PM-3)"},
    ]
    working = [
        f"Loss ratio of the years read: {usd(inc)} / {usd(ep)} = {seen['totals']['loss_ratio_percent']:.2f} percent (PM-1).",
        f"Trend factor: (1 + {trend:g} percent) to the power {trend_years:g} = {factor:.6f} (PM-3).",
        f"Trended incurred claims: {usd(inc)} x {factor:.6f} = {usd(r2(trended_inc))}.",
        f"Trended loss ratio: {usd(r2(trended_inc))} / {usd(ep)} = {r2(trended):.2f} percent.",
    ]
    if met:
        working.append(f"The trended loss ratio of {r2(trended):.2f} percent is at or below the target of {r2(target):.2f} percent, by "
                       f"{r2(target - trended):.2f} points. The target is met: the premium change needed is 0.00 percent (PM-6).")
    else:
        working.append(f"Premium change needed: {r2(trended):.2f} / {r2(target):.2f} - 1 = {r2(raw_change):.2f} percent (PM-5).")
        working.append(f"Premium needed for the same exposure: {usd(r2(trended_inc))} / {r2(target):.2f} percent = {usd(r2(needed))}, "
                       f"against {usd(ep)} earned.")
    combined = r2(target + expense)
    grid = []
    for t_target in (target - 5, target, target + 5):
        for t_trend in (trend - 2, trend, trend + 2):
            if not 20 <= t_target <= 100:
                continue
            tr = trended_ratio(t_trend)
            grid.append({"target_loss_ratio_percent": r2(t_target), "claims_trend_percent_a_year": r2(t_trend),
                         "trended_loss_ratio_percent": r2(tr),
                         "premium_change_needed_percent": 0.0 if r2(tr) <= r2(t_target) else r2(100 * (tr / t_target - 1))})
    if not cred["reliable"]:
        sentence = (f"{segment['segment_id']} is too thin to rely on: {cred['claims_in_the_years_read']} claims against the "
                    f"{RELIABLE_FROM_CLAIMS} the method needs, credibility {cred['credibility']:.2f} (PM-7). On these figures alone "
                    f"the change would be {r2(raw_change):.2f} percent, and that figure is not reliable. The pricing actuary decides "
                    "what to set beside it.")
    elif met:
        sentence = (f"The target is already met for {segment['segment_id']}: the trended loss ratio is {r2(trended):.2f} percent "
                    f"against a target of {r2(target):.2f} percent. No premium change is needed (PM-6).")
    else:
        sentence = (f"{segment['segment_id']} needs a premium change of {r2(raw_change):.2f} percent to hold a loss ratio of "
                    f"{r2(target):.2f} percent: a trended loss ratio of {r2(trended):.2f} percent, on {cred['claims_in_the_years_read']:,} "
                    f"claims (credibility {cred['credibility']:.2f}).")
    return {"segment_id": segment["segment_id"], "segment": segment["name"], "product": segment["product"],
            "assumptions": assumptions, "experience": seen["totals"],
            "trend_factor": round(factor, 6), "trended_incurred_claims": r2(trended_inc), "trended_loss_ratio_percent": r2(trended),
            "target_loss_ratio_percent": r2(target), "target_already_met": met,
            "points_below_the_target": r2(target - trended) if met else 0.0,
            "points_above_the_target": 0.0 if met else r2(trended - target),
            "premium_change_on_these_figures_percent": r2(raw_change),
            "premium_change_to_rely_on_percent": r2(raw_change) if cred["reliable"] else None,
            "premium_needed_for_the_same_exposure": r2(needed), "earned_premium_of_the_years_read": ep,
            "reliable": cred["reliable"], "credibility": cred,
            "combined_ratio_at_the_target_percent": combined,
            "target_and_expenses_fit_within_the_premium": combined <= 100,
            "combined_ratio_note": (f"At the target, claims and expenses take {combined:.2f} percent of the premium."
                                    + ("" if combined <= 100 else " That is more than the premium: at this target the segment does "
                                       "not cover its claims and expenses.")),
            "working": working, "sensitivity": grid,
            "sensitivity_note": "Each row gives the premium change needed at another target (5 points either side) and another claims "
                                "trend (2 points either side), worked out the same way. Zero means the target is met.",
            "sentence": sentence}


# ================================================================ the exposure warehouse

PRODUCTS = ["home", "commercial_property", "private_motor", "motor_fleet"]
REGIONS = ["Port Ilvane", "Marlow Reach", "Tallowby", "Saltmarsh Coast"]
CONSTRUCTION = ["A", "B", "C"]
VEHICLES = ["car", "van", "light_truck"]
BANDS = ["up_to_250000", "250001_to_1000000", "1000001_to_2500000", "over_2500000"]
BAND_WORDS = {"up_to_250000": "up to USD 250,000", "250001_to_1000000": "USD 250,001 to 1,000,000",
              "1000001_to_2500000": "USD 1,000,001 to 2,500,000", "over_2500000": "over USD 2,500,000"}
FIELDS = {"product": PRODUCTS, "region": REGIONS, "construction_class": CONSTRUCTION, "vehicle_class": VEHICLES,
          "sum_insured_band": BANDS}
FIELD_NOTES = {
    "product": "The product of the policy.",
    "region": "The region of Meridia where the risk is.",
    "construction_class": "For home and commercial property only: A non-combustible, B mixed, C combustible. Motor rows hold none.",
    "vehicle_class": "For private motor and motor fleet only: car, van or light_truck. Property rows hold none.",
    "sum_insured_band": "The band of the sum insured of one policy.",
}
MEASURES = {
    "policies_in_force": "Number of policies in force",
    "total_sum_insured": "Total sum insured",
    "annual_premium": "Annual premium",
    "average_sum_insured": "Average sum insured of a policy",
}
NOT_HELD = {
    "flood_zone": "the flood zone of a location (the underwriting system holds it for a submission, the warehouse does not)",
    "postcode": "a postcode or a street address", "address": "a postcode or a street address",
    "occupancy": "the occupancy of a building", "year_built": "the age of a building", "building_age": "the age of a building",
    "sprinklers": "whether a building has sprinklers", "policyholder": "the name of a policyholder", "customer": "the name of a "
    "policyholder", "broker": "the broker of a policy", "driver_age": "the age of a driver", "vehicle_age": "the age of a vehicle",
    "claims": "claims (the experience of a pricing segment holds them)", "loss_ratio": "claims (the experience of a pricing segment "
    "holds them)", "probable_maximum_loss": "a modelled loss", "vehicles": "the number of vehicles in a fleet",
    "deductible": "the deductible of a policy", "date": "any date other than the one the warehouse is as at",
}
RATE = {"home": 0.0085, "commercial_property": 0.0105, "private_motor": 0.04, "motor_fleet": 0.04}
NA = "not_applicable"

_WAREHOUSE = [
    # product, region, class, band, policies, total sum insured
    ("home", "Port Ilvane", "A", 0, 420, 79800000), ("home", "Port Ilvane", "B", 1, 150, 52500000),
    ("home", "Marlow Reach", "A", 0, 310, 55800000), ("home", "Marlow Reach", "B", 1, 90, 31500000),
    ("home", "Marlow Reach", "C", 0, 40, 6000000),
    ("home", "Tallowby", "A", 0, 260, 44200000), ("home", "Tallowby", "B", 1, 40, 13000000), ("home", "Tallowby", "C", 0, 60, 8400000),
    ("home", "Saltmarsh Coast", "B", 0, 110, 19800000), ("home", "Saltmarsh Coast", "C", 0, 30, 4200000),
    ("commercial_property", "Port Ilvane", "A", 2, 30, 54000000), ("commercial_property", "Port Ilvane", "A", 3, 12, 42000000),
    ("commercial_property", "Port Ilvane", "B", 1, 40, 26000000), ("commercial_property", "Port Ilvane", "C", 1, 25, 17500000),
    ("commercial_property", "Port Ilvane", "C", 0, 20, 4000000),
    ("commercial_property", "Marlow Reach", "A", 2, 18, 30600000), ("commercial_property", "Marlow Reach", "B", 2, 14, 23800000),
    ("commercial_property", "Marlow Reach", "B", 1, 22, 13200000), ("commercial_property", "Marlow Reach", "C", 1, 30, 21000000),
    ("commercial_property", "Tallowby", "A", 3, 5, 16000000), ("commercial_property", "Tallowby", "B", 1, 25, 15000000),
    ("commercial_property", "Tallowby", "C", 0, 35, 7000000), ("commercial_property", "Tallowby", "C", 1, 12, 8400000),
    ("commercial_property", "Saltmarsh Coast", "A", 2, 10, 18000000), ("commercial_property", "Saltmarsh Coast", "B", 1, 20, 12000000),
    ("commercial_property", "Saltmarsh Coast", "C", 1, 8, 6000000),
    ("private_motor", "Port Ilvane", "car", 0, 2900, 52200000), ("private_motor", "Port Ilvane", "van", 0, 300, 6600000),
    ("private_motor", "Marlow Reach", "car", 0, 2100, 35700000), ("private_motor", "Marlow Reach", "van", 0, 250, 5000000),
    ("private_motor", "Tallowby", "car", 0, 1500, 24000000), ("private_motor", "Tallowby", "van", 0, 200, 3800000),
    ("private_motor", "Saltmarsh Coast", "car", 0, 600, 9600000),
    ("motor_fleet", "Port Ilvane", "van", 2, 12, 18000000), ("motor_fleet", "Port Ilvane", "light_truck", 1, 15, 9000000),
    ("motor_fleet", "Marlow Reach", "van", 1, 20, 11000000), ("motor_fleet", "Marlow Reach", "car", 1, 10, 4500000),
    ("motor_fleet", "Tallowby", "light_truck", 1, 8, 5200000), ("motor_fleet", "Saltmarsh Coast", "van", 0, 6, 1200000),
]


def warehouse_as_at(today: date) -> str:
    """The warehouse is loaded at each month end: the last day of the month before the insurer date."""
    return (today.replace(day=1) - timedelta(days=1)).isoformat()


def build_warehouse() -> dict:
    rows = {}
    for n, (product, region, cls, band, policies, total) in enumerate(_WAREHOUSE, start=1):
        motor = product in ("private_motor", "motor_fleet")
        rows[f"WR-{n:03d}"] = {"row_id": f"WR-{n:03d}", "product": product, "region": region,
                               "construction_class": NA if motor else cls, "vehicle_class": cls if motor else NA,
                               "sum_insured_band": BANDS[band], "policies_in_force": policies, "total_sum_insured": float(total),
                               "annual_premium": float(round(total * RATE[product]))}
    return rows


def _plain(value: str) -> str:
    return "_".join(str(value).strip().lower().replace(",", "").replace("-", " ").replace("_", " ").split())


def _field_of(name: str) -> str:
    key = _plain(name)
    aliases = {"class": None, "construction": "construction_class", "vehicle": "vehicle_class", "band": "sum_insured_band",
               "sum_insured": "sum_insured_band", "products": "product", "regions": "region", "line_of_business": "product"}
    key = aliases.get(key) or key
    if key in FIELDS:
        return key
    held = ", ".join(FIELDS)
    if key in NOT_HELD:
        raise Refused(f"The warehouse does not hold {NOT_HELD[key]}, so it cannot answer by {name}. It holds these fields only: "
                      f"{held}. Nothing was read and no figure is estimated.")
    raise Refused(f"The warehouse holds no field called {name}. It holds these fields only: {held}. Nothing was read and no figure "
                  "is estimated.")


def _value_of(field: str, raw: str) -> str:
    key = _plain(raw)
    if field == "construction_class" and key.startswith("class_"):
        key = key[6:]
    if field == "sum_insured_band":
        key = key.replace("usd_", "")
    for allowed in FIELDS[field]:
        if _plain(allowed) == key:
            return allowed
    extra = ""
    if field == "product" and key in ("property", "motor"):
        both = "home,commercial_property" if key == "property" else "private_motor,motor_fleet"
        extra = (f" '{raw}' can be read two ways here: one product alone, or both ({both}). Choose one reading, send it, and say "
                 "which reading you took.")
    raise Refused(f"{raw} is not a value of {field}. The values are: {', '.join(FIELDS[field])}.{extra} Nothing was read.")


def _list(raw) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, (list, tuple)):
        return [str(x) for x in raw if str(x).strip()]
    text = str(raw).replace(";", ",")
    kept = "".join(ch for i, ch in enumerate(text)  # a comma inside a number (2,500,000) is not a separator
                   if not (ch == "," and 0 < i < len(text) - 3 and text[i - 1].isdigit() and text[i + 1:i + 4].isdigit()))
    return [x for x in kept.split(",") if x.strip()]


def exposure_query(data: dict, as_at: str, measure: str, group_by=None, filters: dict | None = None) -> dict:
    key = _plain(measure or "")
    if key not in MEASURES:
        why = f" The warehouse does not hold {NOT_HELD[key]}." if key in NOT_HELD else ""
        raise Refused(f"{measure} is not a measure of the warehouse.{why} The measures are: {', '.join(MEASURES)}. Nothing was read "
                      "and no figure is estimated.")
    groups = []
    for g in _list(group_by):
        f = _field_of(g)
        if f not in groups:
            groups.append(f)
    if len(groups) > 2:
        raise Refused("A query groups by at most two fields. Nothing was read.")
    wanted: dict = {}
    for name, raw in (filters or {}).items():
        values = _list(raw)
        if not values:
            continue
        field = _field_of(name)
        wanted[field] = [v for v in dict.fromkeys(_value_of(field, v) for v in values)]
    rows = [r for r in data["pf_warehouse"].values() if all(r[f] in vals for f, vals in wanted.items())]

    def measure_of(part):
        policies, total = sum(r["policies_in_force"] for r in part), sum(r["total_sum_insured"] for r in part)
        if key == "policies_in_force":
            return policies
        if key == "total_sum_insured":
            return r2(total)
        if key == "annual_premium":
            return r2(sum(r["annual_premium"] for r in part))
        return r2(total / policies) if policies else 0.0

    total = measure_of(rows)
    out = []
    if groups:
        order = lambda r: tuple((FIELDS[g] + [NA]).index(r[g]) for g in groups)
        seen: dict = {}
        for r in sorted(rows, key=order):
            seen.setdefault(tuple(r[g] for g in groups), []).append(r)
        for combo, part in seen.items():
            row = {g: v for g, v in zip(groups, combo)}
            row["value"] = measure_of(part)
            if key == "average_sum_insured":
                row["worked_from"] = {"total_sum_insured": r2(sum(r["total_sum_insured"] for r in part)),
                                      "policies_in_force": sum(r["policies_in_force"] for r in part)}
            else:
                row["share_of_the_total_percent"] = r2(100 * row["value"] / total) if total else 0.0
            row["warehouse_rows"] = len(part)
            out.append(row)
    where = "; ".join(f"{f} is {' or '.join(v)}" for f, v in wanted.items())
    words = (f"Number of policies in force on {long_date(as_at)}" if key == "policies_in_force"
             else f"{MEASURES[key]} of the policies in force on {long_date(as_at)}")
    words += f", where {where}" if where else ", with no filter (the whole portfolio)"
    words += f", grouped by {' and '.join(groups)}." if groups else ", as one figure."
    notes = []
    if not rows:
        notes.append("No row of the warehouse matches these filters. The answer is zero: the warehouse holds the fields asked for and "
                     "holds no policy of that kind.")
    if any(row.get(g) == NA for row in out for g in groups):
        notes.append("A row grouped under not_applicable is a product that holds no such field: motor rows hold no construction "
                     "class, property rows hold no vehicle class.")
    if key == "average_sum_insured":
        notes.append("An average is the total sum insured divided by the policies in force. Averages are not added up: the total is "
                     "the average over every row read.")
    result = {"query": {"measure": key, "group_by": groups, "filters": wanted, "as_at": as_at}, "query_in_words": words,
              "unit": "policies" if key == "policies_in_force" else "USD", "rows": out, "rows_returned": len(out), "total": total,
              "warehouse_rows_read": len(rows), "notes": notes}
    if key == "average_sum_insured":
        result["total_worked_from"] = {"total_sum_insured": r2(sum(r["total_sum_insured"] for r in rows)),
                                       "policies_in_force": sum(r["policies_in_force"] for r in rows)}
    return result


# ---------------------------------------------------------------- concentration limits

PROPERTY = ["home", "commercial_property"]
LIMITS_HOW_TO_READ = ("The concentration limits LIM-1 to LIM-6 are set by the risk committee. Each is a share of a part of the "
                      "portfolio or an amount. The system measures the warehouse against each one. A value exactly on a limit is "
                      "within it. Over a limit is a fact for the chief risk officer, Evander Pask: nothing here declines or cancels "
                      "a policy.")


def build_limits() -> dict:
    rows = [
        {"limit_id": "LIM-1", "heading": "Property in one region",
         "text": "No one region holds more than 45 percent of the total sum insured of property: home and commercial property together.",
         "kind": "share", "measure": "total_sum_insured", "of": {"product": PROPERTY}, "any_one": "region", "part": {}, "limit": 45.0},
        {"limit_id": "LIM-2", "heading": "Combustible construction",
         "text": "Construction class C is no more than 15 percent of the total sum insured of commercial property.",
         "kind": "share", "measure": "total_sum_insured", "of": {"product": ["commercial_property"]}, "any_one": None,
         "part": {"construction_class": ["C"]}, "limit": 15.0},
        {"limit_id": "LIM-3", "heading": "The Saltmarsh Coast",
         "text": "The total sum insured of property on the Saltmarsh Coast, home and commercial property together, is no more than "
                 "USD 60,000,000.",
         "kind": "amount", "measure": "total_sum_insured", "of": {}, "any_one": None,
         "part": {"product": PROPERTY, "region": ["Saltmarsh Coast"]}, "limit": 60000000.0},
        {"limit_id": "LIM-4", "heading": "Large commercial risks",
         "text": "Policies with a sum insured over USD 2,500,000 are no more than 25 percent of the total sum insured of commercial "
                 "property.",
         "kind": "share", "measure": "total_sum_insured", "of": {"product": ["commercial_property"]}, "any_one": None,
         "part": {"sum_insured_band": ["over_2500000"]}, "limit": 25.0},
        {"limit_id": "LIM-5", "heading": "Light trucks in the fleet book",
         "text": "Light trucks are no more than 30 percent of the total sum insured of motor fleet.",
         "kind": "share", "measure": "total_sum_insured", "of": {"product": ["motor_fleet"]}, "any_one": None,
         "part": {"vehicle_class": ["light_truck"]}, "limit": 30.0},
        {"limit_id": "LIM-6", "heading": "One product",
         "text": "No one product brings more than 50 percent of the annual premium of the whole portfolio.",
         "kind": "share", "measure": "annual_premium", "of": {}, "any_one": "product", "part": {}, "limit": 50.0},
    ]
    return {r["limit_id"]: r for r in rows}


def measure_limit(data: dict, as_at: str, limit: dict) -> dict:
    measure = limit["measure"]
    base = {"limit_id": limit["limit_id"], "heading": limit["heading"], "text": limit["text"]}
    if limit["kind"] == "amount":
        q = exposure_query(data, as_at, measure, None, limit["part"])
        measured, cap = q["total"], limit["limit"]
        over = measured > cap
        sentence = (f"{limit['limit_id']}: {usd(measured)} against a limit of {usd(cap)}. "
                    + (f"Over the limit by {usd(r2(measured - cap))}." if over else
                       ("Exactly on the limit, which is within it: no room is left." if measured == cap else
                        f"Within the limit, with {usd(r2(cap - measured))} of room.")))
        return {**base, "unit": "USD", "measured": measured, "limit": cap, "result": "over" if over else "within",
                "exactly_on_the_limit": measured == cap, "over_by": r2(measured - cap) if over else 0.0,
                "room_left": 0.0 if over else r2(cap - measured), "queries_run": [q["query_in_words"]], "sentence": sentence}
    whole = exposure_query(data, as_at, measure, None, limit["of"])
    queries = [whole["query_in_words"]]
    each = []
    if limit["any_one"]:
        split = exposure_query(data, as_at, measure, limit["any_one"], limit["of"])
        queries.append(split["query_in_words"])
        each = [{"value_of": limit["any_one"], "is": row[limit["any_one"]], "amount": row["value"]} for row in split["rows"]]
    else:
        part = exposure_query(data, as_at, measure, None, {**limit["of"], **limit["part"]})
        queries.append(part["query_in_words"])
        each = [{"value_of": next(iter(limit["part"])), "is": " or ".join(next(iter(limit["part"].values()))), "amount": part["total"]}]
    for row in each:
        row["share_percent"] = r2(100 * row["amount"] / whole["total"])
        row["over"] = row["amount"] * 100 > limit["limit"] * whole["total"]
    top = max(each, key=lambda row: row["amount"])
    at_limit = r2(limit["limit"] * whole["total"] / 100)
    over = top["over"]
    on = top["amount"] * 100 == limit["limit"] * whole["total"]
    points = r2(abs(top["share_percent"] - limit["limit"]))
    sentence = (f"{limit['limit_id']}: {top['is']} holds {usd(top['amount'])} of {usd(whole['total'])}, {top['share_percent']:.2f} "
                f"percent against a limit of {limit['limit']:.2f} percent. "
                + (f"Over the limit by {points:.2f} points, {usd(r2(top['amount'] - at_limit))}." if over else
                   ("Exactly on the limit, which is within it." if on else
                    f"Within the limit, with {points:.2f} points of room, {usd(r2(at_limit - top['amount']))}.")))
    return {**base, "unit": "percent", "measured": top["share_percent"], "limit": limit["limit"], "measured_for": top["is"],
            "amount": top["amount"], "of_a_total_of": whole["total"], "amount_at_the_limit": at_limit,
            "result": "over" if over else "within", "exactly_on_the_limit": on,
            "over_by_points": points if over else 0.0, "over_by_amount": r2(top["amount"] - at_limit) if over else 0.0,
            "room_left_points": 0.0 if over else points, "room_left_amount": 0.0 if over else r2(at_limit - top["amount"]),
            "every_value_measured": each, "queries_run": queries, "sentence": sentence}


# ================================================================ the whole data set of the system

def build_portfolio(today: date) -> dict:
    return copy.deepcopy({
        "pf_products": build_products(),
        "pf_items": build_items(),
        "pf_change_requests": build_change_requests(today),
        "pf_pricing_method": build_pricing_method(today),
        "pf_segments": build_segments(today),
        "pf_warehouse": build_warehouse(),
        "pf_limits": build_limits(),
        "pf_questions": {},
    })
