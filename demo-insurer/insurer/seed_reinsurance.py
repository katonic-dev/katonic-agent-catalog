"""Seed data, part 7: reinsurance and partners. Two binders and two treaties with numbered terms, four bordereaux, paid claims
with the recoveries already raised, and eight partners with their service levels and credentials.

The sums are here as well: a bordereau measured row by row against the terms with every total re-added, the amount a paid
claim recovers under each treaty with its working, and a partner measured against its service levels and credentials. The
system calls them, so an agent never adds, takes a share or counts a day.

Everything is invented: every coverholder, reinsurer, administrator, repairer, supplier, insured and person.
"""

from __future__ import annotations

import copy
import re
from datetime import date, timedelta

from .seed_policy import long_date

REF = date(2026, 11, 26)  # the dates below are written as they stand on this insurer date and move with it


def rel(today: date, iso: str) -> str:
    return (today + (date.fromisoformat(iso) - REF)).isoformat()


def usd(amount: float) -> str:
    return f"USD {amount:,.2f}"


def plain(amount: float) -> str:
    return f"{amount:,.2f}"


def plural(n, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


def days_from(first_iso: str, last_iso: str) -> int:
    return (date.fromisoformat(last_iso) - date.fromisoformat(first_iso)).days


def plus_days(iso: str, n: int) -> str:
    return (date.fromisoformat(iso) + timedelta(days=n)).isoformat()


WHO_DECIDES = {"reinsurance": "the reinsurance accountant", "partners": "the supplier manager"}

RESULT_LABELS = {"within": "within the term", "outside": "outside the term", "not_applicable": "the term does not apply to this row"}
CHECK_LABELS = {"class": "class of business allowed", "territory": "territory", "maximum_line": "maximum line per risk",
                "period": "period", "commission": "commission rate", "share": "share ceded", "claims_authority": "claims authority",
                "row_total": "the row adds up", "declared_once": "declared once",
                "machinery_age": "age of the machinery at the start of the risk"}
BORDEREAU_KINDS = {"risks_bound": "risks bound in the month", "claims_paid": "claims paid in the month",
                   "cessions": "risks ceded to a treaty in the month"}
CONTRACT_KINDS = {"binder": "binding authority (binder): a coverholder binds risks for the insurer",
                  "excess_of_loss_per_risk": "excess of loss treaty, per risk: the reinsurer pays the part of a loss above the "
                                             "attachment point, up to the limit",
                  "quota_share": "quota share treaty: the reinsurer takes a fixed share of every risk and of every loss"}
CLASS_LABELS = {"HH": "household buildings and contents", "LL": "let property (landlord's buildings and contents)",
                "PC": "pleasure craft up to 12 metres", "DG": "dinghies and small open boats",
                "EN": "engineering: machinery and plant", "CP": "commercial property"}

AGE_NOTE = (" The age of the machinery is the one exception: where a row gives the year of installation, the system "
            "measures it against this term (the check machinery_age) and the agent does not count the years.")
EXCLUDED_NOTE = ("The system does not read the description of a risk. Read each description against the excluded risks of this "
                 "term yourself. A risk that the description plainly puts in an excluded group is a difference; where the "
                 "description does not say, it is not.")


# ---------------------------------------------------------------- binders and treaties

def _terms(rows):
    return [{"term": number, "heading": heading, "kind": kind, "text": text} for number, heading, kind, text in rows]


def build_contracts(today: date) -> dict:
    R = lambda iso: rel(today, iso)
    L = lambda iso: long_date(rel(today, iso))
    out = {}

    def classes(*codes):
        return [{"code": c, "label": CLASS_LABELS[c]} for c in codes]

    # Binder 1: household, Pellowmere Cover Agency.
    out["BND-8601"] = {
        "contract_id": "BND-8601", "kind": "binder", "kind_label": CONTRACT_KINDS["binder"],
        "title": "Household binding authority", "status": "in_force",
        "counterparty": {"role": "coverholder", "name": "Pellowmere Cover Agency"},
        "period_start": R("2026-01-01"), "period_end": R("2026-12-31"), "currency": "USD",
        "figures": {"classes_allowed": classes("HH", "LL"), "territory": ["Meridia"], "maximum_line": 750000.0,
                    "commission_rate_percent": 25.0, "premium_due_days": 45, "claims_authority": 10000.0},
        "terms": _terms([
            ("1", "Classes allowed", "measured",
             "The coverholder may bind household buildings and contents (class HH) and let property (class LL). No other class."),
            ("2", "Territory", "measured", "The risk must be in Meridia. A risk in any other country is outside this binder."),
            ("3", "Maximum line per risk", "measured",
             "The sum insured of one risk must not be more than USD 750,000.00. A risk exactly on USD 750,000.00 is within the line."),
            ("4", "Period", "measured",
             f"The coverholder may bind risks that start from {L('2026-01-01')} to {L('2026-12-31')}, both days included. The "
             "start date of the risk decides."),
            ("5", "Commission", "measured",
             "The coverholder keeps a commission of 25.00 percent of the gross premium of each risk and pays the rest to the insurer."),
            ("6", "Premium due date", "measured",
             "The net premium of a month is due to the insurer within 45 days after the last day of that month."),
            ("7", "Excluded risks", "for_reading",
             "The coverholder may not bind: a property with a thatched roof; a property left unoccupied for more than 60 days in a "
             "row; a house in multiple occupation (let room by room to people who are not one household); a property under "
             "construction or major renovation."),
            ("8", "Claims authority", "measured",
             "The coverholder may pay a claim of up to USD 10,000.00 in all, fees included. A claim of more needs the insurer's "
             "agreement in writing before it is paid, and the row of the bordereau carries the agreement reference. A claim exactly "
             "on USD 10,000.00 is within the authority."),
            ("9", "Bordereaux", "measured",
             "The coverholder sends one bordereau of risks bound and one of claims paid for each month. Each risk and each claim is "
             "declared once. Every row adds up and the totals are the sum of the rows."),
        ])}

    # Binder 2: pleasure craft, Quillfeather Marine Agency.
    out["BND-8602"] = {
        "contract_id": "BND-8602", "kind": "binder", "kind_label": CONTRACT_KINDS["binder"],
        "title": "Pleasure craft binding authority", "status": "in_force",
        "counterparty": {"role": "coverholder", "name": "Quillfeather Marine Agency"},
        "period_start": R("2026-04-01"), "period_end": R("2027-03-31"), "currency": "USD",
        "figures": {"classes_allowed": classes("PC", "DG"), "territory": ["Meridia"], "maximum_line": 250000.0,
                    "commission_rate_percent": 20.0, "premium_due_days": 30, "claims_authority": 5000.0},
        "terms": _terms([
            ("1", "Classes allowed", "measured",
             "The coverholder may bind pleasure craft up to 12 metres (class PC) and dinghies and small open boats (class DG). No "
             "other class."),
            ("2", "Territory", "measured",
             "The craft must be kept in Meridia, on its coastal or inland waters. A craft kept in any other country is outside this "
             "binder."),
            ("3", "Maximum line per risk", "measured",
             "The sum insured of one craft must not be more than USD 250,000.00. A craft exactly on USD 250,000.00 is within the line."),
            ("4", "Period", "measured",
             f"The coverholder may bind risks that start from {L('2026-04-01')} to {L('2027-03-31')}, both days included. The "
             "start date of the risk decides."),
            ("5", "Commission", "measured",
             "The coverholder keeps a commission of 20.00 percent of the gross premium of each risk and pays the rest to the insurer."),
            ("6", "Premium due date", "measured",
             "The net premium of a month is due to the insurer within 30 days after the last day of that month."),
            ("7", "Excluded risks", "for_reading",
             "The coverholder may not bind: a craft used for racing; a craft let out for hire or charter; a craft with a maximum "
             "speed above 35 knots; a houseboat used as a permanent home."),
            ("8", "Claims authority", "measured",
             "The coverholder may pay a claim of up to USD 5,000.00 in all, fees included. A claim of more needs the insurer's "
             "agreement in writing before it is paid, and the row of the bordereau carries the agreement reference."),
            ("9", "Bordereaux", "measured",
             "The coverholder sends one bordereau of risks bound and one of claims paid for each month. Each risk and each claim is "
             "declared once. Every row adds up and the totals are the sum of the rows."),
        ])}

    # Treaty 1: commercial property, excess of loss per risk, Greyfell Reinsurance Company.
    out["TRY-8651"] = {
        "contract_id": "TRY-8651", "kind": "excess_of_loss_per_risk", "kind_label": CONTRACT_KINDS["excess_of_loss_per_risk"],
        "title": "Commercial property excess of loss treaty, per risk", "status": "in_force",
        "counterparty": {"role": "reinsurer", "name": "Greyfell Reinsurance Company"},
        "period_start": R("2026-01-01"), "period_end": R("2026-12-31"), "treaty_year": R("2026-01-01")[:4], "currency": "USD",
        "figures": {"classes_covered": classes("CP"), "territory": ["Meridia"], "attachment_point": 250000.0, "limit": 750000.0,
                    "reinstatements": 2, "annual_premium": 180000.0},
        "terms": _terms([
            ("1", "Class covered", "measured", "Commercial property (class CP) written by the insurer. No other class."),
            ("2", "Territory", "measured", "Risks in Meridia."),
            ("3", "Period", "measured",
             f"Losses that happen from {L('2026-01-01')} to {L('2026-12-31')}, both days included. The date of loss decides, not "
             "the date a claim is paid. A loss that happened before or after the period is not recovered under this treaty."),
            ("4", "Attachment point", "measured",
             "The insurer keeps the first USD 250,000.00 of each loss. The reinsurer pays only the part of the paid loss that is "
             "above USD 250,000.00. A paid loss exactly on USD 250,000.00 gives no recovery."),
            ("5", "Limit", "measured",
             "The reinsurer pays at most USD 750,000.00 for each loss, above the attachment point. The part of a paid loss above "
             "USD 1,000,000.00 stays with the insurer."),
            ("6", "One event", "measured",
             "Where two or more claims arise from one event, they are added together and treated as one loss: the attachment point "
             "and the limit apply once, to the sum. The claims handler records the event on each claim with an event id. Claims "
             "that carry no event id are each a loss alone."),
            ("7", "Reinstatement", "measured",
             "After a recovery the limit is reinstated in full, up to two times in the treaty year. For each recovery the insurer "
             "pays a reinstatement premium: the recovery divided by the limit, times the annual premium of USD 180,000.00."),
            ("8", "Raising a recovery", "for_reading",
             "A recovery is raised when the paid loss passes the attachment point, and again for each later payment on the same "
             "loss. The reinsurance accountant raises it; the reinsurer is told by the reinsurance accountant and by nobody else."),
        ])}

    # Treaty 2: engineering, quota share, Windlecombe Re.
    out["TRY-8652"] = {
        "contract_id": "TRY-8652", "kind": "quota_share", "kind_label": CONTRACT_KINDS["quota_share"],
        "title": "Engineering quota share treaty", "status": "in_force",
        "counterparty": {"role": "reinsurer", "name": "Windlecombe Re"},
        "period_start": R("2026-01-01"), "period_end": R("2026-12-31"), "treaty_year": R("2026-01-01")[:4], "currency": "USD",
        "figures": {"classes_covered": classes("EN"), "territory": ["Meridia"], "cession_percent": 40.0, "maximum_line": 2000000.0,
                    "commission_rate_percent": 30.0, "premium_due_days": 45, "cash_loss_limit": 100000.0,
                    "maximum_machinery_age_years": 25},
        "terms": _terms([
            ("1", "Class covered", "measured", "Engineering: machinery and plant (class EN) written by the insurer. No other class."),
            ("2", "Territory", "measured", "Risks in Meridia."),
            ("3", "Cession", "measured",
             "The insurer cedes 40.00 percent of the sum insured and of the premium of every risk. The ceded sum insured of one "
             "risk must not be more than USD 2,000,000.00. A cession exactly on USD 2,000,000.00 is within the line."),
            ("4", "Period", "measured",
             f"Risks that start, and losses that happen, from {L('2026-01-01')} to {L('2026-12-31')}, both days included."),
            ("5", "Ceding commission", "measured",
             "The reinsurer allows the insurer a commission of 30.00 percent of the ceded premium of each risk."),
            ("6", "Premium due date", "measured",
             "The net ceded premium of a month is due to the reinsurer within 45 days after the last day of that month."),
            ("7", "Excluded risks", "for_reading",
             "Not ceded: plant at sea or on an offshore platform; plant used underground in a mine; prototype or experimental "
             "machinery; machinery installed more than 25 years before the start of the risk."),
            ("8", "Losses and cash calls", "measured",
             "The reinsurer pays 40.00 percent of every paid loss, from the first dollar. Its share is collected in the quarterly "
             "account. Where the paid loss is USD 100,000.00 or more, the share is collected at once by a cash call, which the "
             "reinsurance accountant raises."),
            ("9", "Cession lists", "measured",
             "The insurer sends one list of risks ceded for each month. Each risk is declared once. Every row adds up and the totals "
             "are the sum of the rows."),
        ])}
    return out


# ---------------------------------------------------------------- bordereaux

def build_bordereaux(today: date) -> dict:
    R = lambda iso: rel(today, iso)
    out = {}

    def risks(rows):
        return [{"row_number": n, "certificate": cert, "insured": insured, "description": text, "class_code": code,
                 "class_label": CLASS_LABELS[code], "location": place, "country": country, "sum_insured": float(si),
                 "inception": R(start), "gross_premium": float(gp), "commission_stated": float(com), "net_premium_stated": float(net)}
                for n, (cert, insured, text, code, place, country, si, start, gp, com, net) in enumerate(rows, 1)]

    def add(bid, kind, contract_id, sent_by, rows, columns, sent_to=None):
        out[bid] = {"bordereau_id": bid, "status": "received", "kind": kind, "kind_label": BORDEREAU_KINDS[kind],
                    "contract_id": contract_id, "sent_by": sent_by, "sent_to": sent_to or {"role": "insurer", "name": "Thornmere Mutual Insurance"},
                    "period_start": R("2026-10-01"), "period_end": R("2026-10-31"), "received_on": R("2026-11-09"),
                    "currency": "USD", "premium_received_on": None, "rows": rows,
                    "stated_totals": {c: round(sum(r[c] for r in rows), 2) for c in columns}, "difference_drafts": []}

    pellowmere = {"role": "coverholder", "name": "Pellowmere Cover Agency"}
    quillfeather = {"role": "coverholder", "name": "Quillfeather Marine Agency"}

    add("BDX-8701", "risks_bound", "BND-8601", pellowmere, risks([
        ("PCA-10431", "Ines Calloway", "Three-bedroom brick house with a tiled roof, owner occupied.", "HH", "Port Ilvane", "Meridia",
         420000, "2026-10-02", 840.00, 210.00, 630.00),
        ("PCA-10432", "Dorian Pell", "Two-bedroom flat on the second floor, owner occupied.", "HH", "Marlow Reach", "Meridia",
         310000, "2026-10-05", 620.00, 155.00, 465.00),
        ("PCA-10433", "Marguerite Ostley", "Detached stone house with a slate roof, owner occupied.", "HH", "Tallowby", "Meridia",
         750000, "2026-10-06", 1500.00, 375.00, 1125.00),
        ("PCA-10434", "Lucan Verrier", "Terraced house let to one family on a 12 month tenancy.", "LL", "Port Ilvane", "Meridia",
         380000, "2026-10-08", 912.00, 228.00, 684.00),
        ("PCA-10435", "Philippa Dunmore", "Detached house with outbuildings and a tiled roof, owner occupied.", "HH", "Marlow Reach",
         "Meridia", 825000, "2026-10-09", 1650.00, 412.50, 1237.50),
        ("PCA-10436", "Tobias Wrenfield", "Semi-detached house with a tiled roof, owner occupied.", "HH", "Tallowby", "Meridia",
         295000, "2026-10-12", 590.00, 147.50, 442.50),
        ("PCA-10437", "Annelise Corby", "Four-bedroom house with a tiled roof, owner occupied all year.", "HH", "Lake Sorrin", "Veldmark",
         340000, "2026-10-14", 680.00, 170.00, 510.00),
        ("PCA-10438", "Greta Halloran", "Cottage with a thatched roof, owner occupied.", "HH", "Tallowby", "Meridia",
         360000, "2026-10-15", 900.00, 225.00, 675.00),
        ("PCA-10439", "Benedict Aylward", "Ground-floor flat let to one tenant.", "LL", "Port Ilvane", "Meridia",
         240000, "2026-10-19", 576.00, 144.00, 432.00),
        ("PCA-10440", "Rosalind Tew", "Three-bedroom bungalow with a tiled roof, owner occupied.", "HH", "Marlow Reach", "Meridia",
         455000, "2026-10-21", 910.00, 227.50, 682.50),
        ("PCA-10441", "Casimir Oakes", "Town house on three floors with a slate roof, owner occupied.", "HH", "Port Ilvane", "Meridia",
         610000, "2026-10-26", 1220.00, 305.00, 915.00),
        ("PCA-10442", "Odette Farrow", "Semi-detached house let to one family.", "LL", "Tallowby", "Meridia",
         330000, "2026-10-29", 792.00, 198.00, 594.00),
    ]), ("gross_premium", "commission_stated", "net_premium_stated"))

    coralie = ("QMA-5504", "Coralie Finch", "7 metre day boat with an outboard engine, private pleasure use.", "PC", "Port Ilvane",
               "Meridia", 42000, "2026-10-08", 420.00, 84.00, 336.00)
    add("BDX-8702", "risks_bound", "BND-8602", quillfeather, risks([
        ("QMA-5501", "Evander Stroud", "8 metre sailing yacht moored at the Port Ilvane marina, private pleasure use.", "PC",
         "Port Ilvane", "Meridia", 95000, "2026-10-01", 950.00, 190.00, 760.00),
        ("QMA-5502", "Liesel Marchbank", "4 metre sailing dinghy kept ashore, private pleasure use.", "DG", "Marlow Reach", "Meridia",
         6000, "2026-10-03", 120.00, 24.00, 96.00),
        ("QMA-5503", "Rufus Tannery", "10 metre motor cruiser, maximum speed 22 knots, private pleasure use.", "PC", "Port Ilvane",
         "Meridia", 180000, "2026-10-06", 1800.00, 360.00, 1440.00),
        coralie,
        ("QMA-5505", "Magnus Ollerton", "9 metre sailing yacht, private pleasure use.", "PC", "Marlow Reach", "Meridia",
         120000, "2026-10-12", 1200.00, 270.00, 930.00),
        ("QMA-5506", "Thea Brandreth", "5 metre rowing skiff kept at the Marlow Reach boat club.", "DG", "Marlow Reach", "Meridia",
         4500, "2026-10-13", 90.00, 18.00, 72.00),
        ("QMA-5507", "Ansel Greaves", "11 metre motor cruiser, maximum speed 28 knots, private pleasure use.", "PC", "Port Ilvane",
         "Meridia", 235000, "2026-03-28", 2350.00, 470.00, 1880.00),
        ("QMA-5508", "Imogen Vasey", "6 metre fishing boat, private use.", "PC", "Tallowby", "Meridia",
         28000, "2026-10-20", 280.00, 56.00, 224.00),
        coralie,
        ("QMA-5509", "Lorcan Abney", "8 metre sailing yacht, laid up ashore for the winter, private pleasure use.", "PC", "Port Ilvane",
         "Meridia", 88000, "2026-10-27", 880.00, 176.00, 704.00),
    ]), ("gross_premium", "commission_stated", "net_premium_stated"))

    claims = [
        ("PCA-C-2201", "PCA-10102", "Hester Bly", "Escape of water from a washing machine hose. Kitchen floor replaced.",
         "2026-09-03", "2026-10-06", 2150.00, 180.00, 2330.00, ""),
        ("PCA-C-2202", "PCA-10117", "Jonas Akerman", "Storm damage to roof tiles.", "2026-09-18", "2026-10-08", 1480.00, 120.00, 1600.00, ""),
        ("PCA-C-2203", "PCA-10056", "Mirela Dunstan", "Theft of a bicycle from a locked shed.", "2026-09-22", "2026-10-09",
         640.00, 0.00, 640.00, ""),
        ("PCA-C-2204", "PCA-10203", "Hugo Parrish", "Fire in the kitchen. Units and ceiling replaced.", "2026-09-11", "2026-10-13",
         9400.00, 600.00, 10000.00, ""),
        ("PCA-C-2205", "PCA-10088", "Sabine Lorrimer", "Burst pipe in the loft. Ceilings and carpets replaced.", "2026-09-27",
         "2026-10-15", 3400.00, 250.00, 3850.00, ""),
        ("PCA-C-2206", "PCA-10150", "Edmund Vane", "Accidental damage to a television.", "2026-10-02", "2026-10-19", 520.00, 0.00, 520.00, ""),
        ("PCA-C-2207", "PCA-10231", "Clarice Monkton", "Subsidence. Rear wall underpinned.", "2026-07-14", "2026-10-21",
         21500.00, 1900.00, 23400.00, "TMI-AGR-0417"),
        ("PCA-C-2208", "PCA-10175", "Wilfred Garrow", "Storm damage to a garden wall.", "2026-10-05", "2026-10-26", 1150.00, 90.00, 1240.00, ""),
        ("PCA-C-2209", "PCA-10199", "Petra Lindqvist", "Escape of oil from a heating tank.", "2026-09-30", "2026-10-29",
         4800.00, 420.00, 5220.00, ""),
    ]
    add("BDX-8703", "claims_paid", "BND-8601", pellowmere, [
        {"row_number": n, "claim_reference": ref, "certificate": cert, "insured": insured, "description": text,
         "date_of_loss": R(loss), "date_paid": R(paid), "indemnity": ind, "fees": fees, "total_stated": total,
         "agreement_reference": agreement}
        for n, (ref, cert, insured, text, loss, paid, ind, fees, total, agreement) in enumerate(claims, 1)],
        ("indemnity", "fees", "total_stated"))

    cessions = [
        ("TMI-EN-0301", "Harbourline Cold Stores", "Refrigeration plant at a cold store, installed 2018.", "Port Ilvane",
         1200000, "2026-10-01", 6000.00),
        ("TMI-EN-0302", "Penhallow Printing Works", "Two offset printing presses, installed 2016.", "Marlow Reach",
         2500000, "2026-10-05", 11500.00),
        ("TMI-EN-0303", "Marlow Reach Dairy Co-operative", "Pasteurising and bottling line, installed 2020.", "Marlow Reach",
         3750000, "2026-10-07", 16000.00),
        ("TMI-EN-0304", "Tallowby Sawmills", "Band saws and a drying kiln, installed 2014.", "Tallowby", 900000, "2026-10-12", 5400.00),
        ("TMI-EN-0305", "Ilvane Grain Terminal", "Conveyors and grain elevators at the grain terminal, installed 2012.", "Port Ilvane",
         5000000, "2026-10-15", 21000.00),
        ("TMI-EN-0306", "Emberwick Foundry", "Induction furnaces, installed 2019.", "Tallowby", 2200000, "2026-10-19", 13000.00),
        ("TMI-EN-0307", "Northgate Bakeries", "Ovens and dough mixers at two bakeries, installed 2022.", "Port Ilvane",
         650000, "2026-10-22", 3500.00),
        ("TMI-EN-0308", "Sorrel Valley Bottlers", "Filling and labelling machines, installed 2021.", "Marlow Reach",
         1800000, "2026-10-28", 9000.00),
    ]
    rows = []
    for n, (ref, insured, text, place, si, start, gp) in enumerate(cessions, 1):
        ceded_premium = round(gp * 0.40, 2)
        commission = round(ceded_premium * 0.30, 2)
        rows.append({"row_number": n, "policy_reference": ref, "insured": insured, "description": text, "class_code": "EN",
                     "class_label": CLASS_LABELS["EN"], "location": place, "country": "Meridia", "sum_insured": float(si),
                     "ceded_sum_insured_stated": round(si * 0.40, 2), "inception": R(start), "gross_premium": gp,
                     "ceded_premium_stated": ceded_premium, "commission_stated": commission,
                     "net_premium_stated": round(ceded_premium - commission, 2),
                     "installed_year": int(re.search("installed ([0-9]{4})", text).group(1))})
    add("BDX-8704", "cessions", "TRY-8652", {"role": "reinsurance accounts team", "name": "Thornmere Mutual Insurance"}, rows,
        ("ceded_sum_insured_stated", "ceded_premium_stated", "commission_stated", "net_premium_stated"),
        sent_to={"role": "reinsurer", "name": "Windlecombe Re"})
    return out


def _check(check, term, ok, measured, limit, difference, sentence, unit="USD"):
    result = "within" if ok else "outside"
    return {"check": check, "check_label": CHECK_LABELS[check], "term": term, "result": result,
            "result_label": RESULT_LABELS[result], "measured": measured, "limit": limit, "difference": difference, "unit": unit,
            "sentence": sentence}


def _class_check(row, allowed):
    codes = [c["code"] for c in allowed]
    ok = row["class_code"] in codes
    return _check("class", "1", ok, row["class_code"], codes, None,
                  f"Class {row['class_code']} ({row['class_label']}) is {'one of' if ok else 'not one of'} the classes allowed "
                  f"({', '.join(codes)}).", unit="class code")


def _territory_check(row, territory):
    ok = row["country"] in territory
    return _check("territory", "2", ok, row["country"], territory, None,
                  f"The risk is at {row['location']}, {row['country']}: {'inside' if ok else 'outside'} the territory "
                  f"({', '.join(territory)}).", unit="country")


def _line_check(amount, limit, what):
    over = round(amount - limit, 2)
    if over > 0:
        sentence = f"The {what} is {usd(amount)}: {usd(over)} over the maximum line of {usd(limit)}."
    elif over == 0:
        sentence = f"The {what} is {usd(amount)}: exactly on the maximum line of {usd(limit)}, which is within it."
    else:
        sentence = f"The {what} is {usd(amount)}: within the maximum line of {usd(limit)}."
    return _check("maximum_line", "3", over <= 0, amount, limit, max(over, 0.0), sentence)


def _period_check(day_iso, contract, what, term="4"):
    start, end = contract["period_start"], contract["period_end"]
    span = f"{long_date(start)} to {long_date(end)}"
    if day_iso < start:
        n = days_from(day_iso, start)
        return _check("period", term, False, day_iso, [start, end], n,
                      f"The {what} is {long_date(day_iso)}: {plural(n, 'day')} before the period starts ({span}).", unit="days")
    if day_iso > end:
        n = days_from(end, day_iso)
        return _check("period", term, False, day_iso, [start, end], n,
                      f"The {what} is {long_date(day_iso)}: {plural(n, 'day')} after the period ends ({span}).", unit="days")
    return _check("period", term, True, day_iso, [start, end], 0,
                  f"The {what} is {long_date(day_iso)}: inside the period ({span}).", unit="days")


def _commission_check(base, stated, rate, of_what):
    expected = round(base * rate / 100, 2)
    diff = round(stated - expected, 2)
    taken = round(stated / base * 100, 2) if base else None
    if diff == 0:
        sentence = f"{rate:.2f} percent of the {of_what} of {usd(base)} is {usd(expected)}, and {usd(stated)} was taken: the right rate."
    else:
        sentence = (f"{rate:.2f} percent of the {of_what} of {usd(base)} is {usd(expected)}. {usd(stated)} was taken, which is "
                    f"{taken:.2f} percent: {usd(abs(diff))} {'too much' if diff > 0 else 'too little'}.")
    c = _check("commission", "5", diff == 0, stated, expected, diff, sentence)
    c["rate_taken_percent"], c["rate_of_the_term_percent"] = taken, rate
    return c


def _total_check(parts_text, expected, stated, what):
    diff = round(stated - expected, 2)
    if diff == 0:
        sentence = f"{parts_text} = {usd(expected)}, and the row states {usd(stated)}: the {what} adds up."
    else:
        sentence = (f"{parts_text} = {usd(expected)}, and the row states {usd(stated)}: the {what} does not add up. The row is "
                    f"{usd(abs(diff))} {'too high' if diff > 0 else 'too low'}.")
    return _check("row_total", "9", diff == 0, stated, expected, diff, sentence)


def _once_check(row, key, seen, what):
    first = seen.get(key)
    if first is None:
        seen[key] = row["row_number"]
        return _check("declared_once", "9", True, 1, 1, 0, f"This {what} is on the bordereau once.", unit="rows")
    c = _check("declared_once", "9", False, 2, 1, 1,
               f"Row {row['row_number']} repeats row {first}: the same {what}, with the same figures. It is declared twice.", unit="rows")
    c["duplicate_of_row"] = first
    return c


def _age_check(row, limit):
    start_year = int(row["inception"][:4])
    age = start_year - row["installed_year"]
    over = max(age - limit, 0)
    if over:
        tail = f"{plural(over, 'year')} over the limit of {limit} years: an excluded risk."
    elif age == limit:
        tail = f"exactly on the limit of {limit} years, which is within it."
    else:
        tail = f"within the limit of {limit} years."
    c = _check("machinery_age", "7", not over, age, limit, over,
               f"The machinery was installed in {row['installed_year']} and the risk starts in {start_year}: "
               f"{start_year} - {row['installed_year']} = {plural(age, 'year')}, {tail}", unit="years")
    c["installed_year"], c["year_the_risk_starts"] = row["installed_year"], start_year
    return c


def _column(label, stated, re_added):
    return {"column_label": label, "stated_on_the_bordereau": stated, "re_added_by_the_system": re_added,
            "difference": round(stated - re_added, 2)}


def measure_bordereau(bdx: dict, contract: dict, today_iso: str) -> dict:
    """Every row of a bordereau against the numeric and dated terms of its binder or treaty, with every total re-added."""
    f, kind, rows, seen, duplicates = contract["figures"], bdx["kind"], [], {}, []
    for row in bdx["rows"]:
        if kind == "risks_bound":
            reference = row["certificate"]
            checks = [
                _class_check(row, f["classes_allowed"]), _territory_check(row, f["territory"]),
                _line_check(row["sum_insured"], f["maximum_line"], "sum insured"),
                _period_check(row["inception"], contract, "start date of the risk"),
                _commission_check(row["gross_premium"], row["commission_stated"], f["commission_rate_percent"], "gross premium"),
                _total_check(f"Gross premium {plain(row['gross_premium'])} less commission {plain(row['commission_stated'])}",
                             round(row["gross_premium"] - row["commission_stated"], 2), row["net_premium_stated"], "net premium"),
                _once_check(row, (row["certificate"], row["insured"], row["inception"], row["sum_insured"], row["gross_premium"]),
                            seen, "certificate"),
            ]
        elif kind == "cessions":
            reference = row["policy_reference"]
            share = f["cession_percent"]
            want_si, want_premium = round(row["sum_insured"] * share / 100, 2), round(row["gross_premium"] * share / 100, 2)
            share_ok = row["ceded_sum_insured_stated"] == want_si and row["ceded_premium_stated"] == want_premium
            share_check = _check(
                "share", "3", share_ok, {"ceded_sum_insured": row["ceded_sum_insured_stated"], "ceded_premium": row["ceded_premium_stated"]},
                {"ceded_sum_insured": want_si, "ceded_premium": want_premium},
                {"ceded_sum_insured": round(row["ceded_sum_insured_stated"] - want_si, 2),
                 "ceded_premium": round(row["ceded_premium_stated"] - want_premium, 2)},
                f"{share:.2f} percent of the sum insured of {usd(row['sum_insured'])} is {usd(want_si)} and of the premium of "
                f"{usd(row['gross_premium'])} is {usd(want_premium)}. The row states {usd(row['ceded_sum_insured_stated'])} and "
                f"{usd(row['ceded_premium_stated'])}: {'the right share' if share_ok else 'not the share of the treaty'}.")
            checks = [
                _class_check(row, f["classes_covered"]), _territory_check(row, f["territory"]), share_check,
                _line_check(row["ceded_sum_insured_stated"], f["maximum_line"], "ceded sum insured"),
                _period_check(row["inception"], contract, "start date of the risk"),
                _commission_check(row["ceded_premium_stated"], row["commission_stated"], f["commission_rate_percent"], "ceded premium"),
                _total_check(f"Ceded premium {plain(row['ceded_premium_stated'])} less commission {plain(row['commission_stated'])}",
                             round(row["ceded_premium_stated"] - row["commission_stated"], 2), row["net_premium_stated"],
                             "net ceded premium"),
                _once_check(row, row["policy_reference"], seen, "policy"),
            ]
            if row.get("installed_year") and f.get("maximum_machinery_age_years"):
                checks.append(_age_check(row, f["maximum_machinery_age_years"]))
        else:  # claims_paid
            reference = row["claim_reference"]
            total = round(row["indemnity"] + row["fees"], 2)
            authority, agreement = f["claims_authority"], row["agreement_reference"]
            over = round(total - authority, 2)
            if over > 0 and agreement:
                sentence = (f"The claim is {usd(total)} in all: {usd(over)} over the claims authority of {usd(authority)}. The row "
                            f"carries the agreement reference {agreement}, so the term is met.")
            elif over > 0:
                sentence = (f"The claim is {usd(total)} in all: {usd(over)} over the claims authority of {usd(authority)}, and the "
                            "row carries no agreement reference.")
            elif over == 0:
                sentence = f"The claim is {usd(total)} in all: exactly on the claims authority of {usd(authority)}, which is within it."
            else:
                sentence = f"The claim is {usd(total)} in all: within the claims authority of {usd(authority)}."
            authority_check = _check("claims_authority", "8", over <= 0 or bool(agreement), total, authority, max(over, 0.0), sentence)
            authority_check["agreement_reference"] = agreement or None
            checks = [
                _period_check(row["date_of_loss"], contract, "date of loss"), authority_check,
                _total_check(f"Indemnity {plain(row['indemnity'])} plus fees {plain(row['fees'])}", total, row["total_stated"], "row total"),
                _once_check(row, row["claim_reference"], seen, "claim"),
            ]
        outside = [c["check"] for c in checks if c["result"] == "outside"]
        if "declared_once" in outside:
            duplicates.append(row["row_number"])
        rows.append({"row_number": row["row_number"], "reference": reference, "insured": row["insured"],
                     "result": "outside" if outside else "within",
                     "result_label": "one or more measured terms are not met" if outside else "every measured term is met",
                     "checks_outside": outside, "checks": checks})

    stated, src = bdx["stated_totals"], bdx["rows"]
    add = lambda field, items=None: round(sum(r[field] for r in (src if items is None else items)), 2)
    if kind == "claims_paid":
        from_parts = round(add("indemnity") + add("fees"), 2)
        columns = {"indemnity": _column("indemnity", stated["indemnity"], add("indemnity")),
                   "fees": _column("fees", stated["fees"], add("fees")),
                   "total": _column("total paid, re-added from the indemnity and the fees of every row", stated["total_stated"], from_parts)}
        columns["total"]["sum_of_the_row_totals_as_stated"] = add("total_stated")
    elif kind == "cessions":
        columns = {c: _column(label, stated[c], add(c)) for c, label in (
            ("ceded_sum_insured_stated", "ceded sum insured"), ("ceded_premium_stated", "ceded premium"),
            ("commission_stated", "ceding commission"), ("net_premium_stated", "net ceded premium"))}
    else:
        columns = {c: _column(label, stated[c], add(c)) for c, label in (
            ("gross_premium", "gross premium"), ("commission_stated", "commission"), ("net_premium_stated", "net premium"))}
    adds_up = all(c["difference"] == 0 for c in columns.values())
    if adds_up:
        total_sentence = "The totals stated on the bordereau are the sum of its rows."
    else:
        wrong = [f"{c['column_label']}: stated {usd(c['stated_on_the_bordereau'])}, re-added {usd(c['re_added_by_the_system'])}, a "
                 f"difference of {usd(abs(c['difference']))}" for c in columns.values() if c["difference"] != 0]
        total_sentence = "The totals do not add up. " + "; ".join(wrong) + "."
    totals_term = next((t for t in contract["terms"] if t["heading"] in ("Bordereaux", "Cession lists")), None)
    totals = {"term": totals_term["term"] if totals_term else None,
              "term_heading": totals_term["heading"] if totals_term else None,
              "columns": columns, "adds_up": adds_up, "sentence": total_sentence}

    if kind != "claims_paid":
        base_field = "gross_premium" if kind == "risks_bound" else "ceded_premium_stated"
        rate = f["commission_rate_percent"]
        base = add(base_field)
        due = round(sum(round(r[base_field] * rate / 100, 2) for r in src), 2)
        taken = add("commission_stated")
        totals["commission_at_the_rate_of_the_term"] = {
            "rate_percent": rate, "commission_due_at_that_rate": due, "commission_taken": taken, "difference": round(taken - due, 2),
            "net_premium_at_that_rate": round(base - due, 2),
            "sentence": f"At {rate:.2f} percent the commission on {usd(base)} is {usd(due)}. {usd(taken)} was taken: "
                        + ("the same." if taken == due else f"{usd(abs(round(taken - due, 2)))} {'too much' if taken > due else 'too little'}.")}
        if duplicates:
            kept = [r for r in src if r["row_number"] not in duplicates]
            totals["without_the_rows_declared_twice"] = {
                "rows_left_out": duplicates, base_field: add(base_field, kept), "commission_stated": add("commission_stated", kept),
                "net_premium_stated": add("net_premium_stated", kept),
                "sentence": f"Without row {', '.join(str(n) for n in duplicates)}, which repeats an earlier row, the net premium is "
                            f"{usd(add('net_premium_stated', kept))} in place of {usd(add('net_premium_stated'))}."}

    premium_due = None
    if kind != "claims_paid":
        due_on = plus_days(bdx["period_end"], f["premium_due_days"])
        lead = (f"The net premium of the month is due within {f['premium_due_days']} days after {long_date(bdx['period_end'])}, by "
                f"{long_date(due_on)}.")
        got = bdx["premium_received_on"]
        if got:
            late = max(days_from(due_on, got), 0)
            status = "paid_late" if late else "paid_in_time"
            sentence = f"{lead} It was received on {long_date(got)}: " + (f"{plural(late, 'day')} late." if late else "in time.")
            left = None
        elif today_iso > due_on:
            late, left, status = days_from(due_on, today_iso), 0, "overdue"
            sentence = f"{lead} No payment is recorded and {long_date(today_iso)} is {plural(late, 'day')} after that date."
        else:
            late, left = 0, days_from(today_iso, due_on)
            status = "due_today" if left == 0 else "not_yet_due"
            sentence = f"{lead} No payment is recorded. On {long_date(today_iso)} there are {plural(left, 'day')} left: not late."
        labels = {"paid_in_time": "paid in time", "paid_late": "paid late", "overdue": "overdue", "due_today": "due on this day, not late",
                  "not_yet_due": "not yet due"}
        premium_due = {"term": "6", "due_on": due_on, "received_on": got, "status": status, "status_label": labels[status],
                       "days_left": left, "days_late": late, "late": status in ("paid_late", "overdue"), "sentence": sentence}

    found = [{"row_number": r["row_number"], "reference": r["reference"], "check": c["check"], "check_label": c["check_label"],
              "term": c["term"], "sentence": c["sentence"]}
             for r in rows for c in r["checks"] if c["result"] == "outside"]
    excluded = next((t for t in contract["terms"] if t["heading"] == "Excluded risks"), None)
    for_reading = None
    if kind != "claims_paid" and excluded:
        for_reading = {"term": excluded["term"], "heading": excluded["heading"], "text": excluded["text"],
                       "note": EXCLUDED_NOTE + (AGE_NOTE if f.get("maximum_machinery_age_years") else "")}
    return {"bordereau_id": bdx["bordereau_id"], "contract_id": contract["contract_id"], "kind": kind, "kind_label": bdx["kind_label"],
            "measured_on": today_iso, "rows": rows, "totals": totals, "premium_due": premium_due,
            "differences_measured": found,
            "counted": {"rows": len(rows), "rows_within_every_measured_term": sum(1 for r in rows if r["result"] == "within"),
                        "rows_with_a_measured_difference": sum(1 for r in rows if r["result"] == "outside"),
                        "differences_measured": len(found), "totals_add_up": adds_up},
            "excluded_risks_for_reading": for_reading,
            "goes_to": WHO_DECIDES["reinsurance"]}


# ---------------------------------------------------------------- paid claims and recoveries

RECOVERY_LABELS = {
    "nothing_due": "nothing due: the paid loss does not pass the attachment point",
    "recovery_to_raise": "a recovery is due and none is raised",
    "recovery_raised_for_too_little": "a recovery is raised, for less than is due",
    "recovery_raised_in_full": "the recovery is raised in full: nothing more to raise",
    "recovery_raised_for_too_much": "more is raised than is due",
    "outside_the_treaty_period": "the date of loss is outside the treaty period: a person checks which treaty year answers",
    "collected_in_the_quarterly_account": "the reinsurer's share is collected in the quarterly account: no cash call",
    "does_not_apply": "this treaty does not cover the class of the claim",
}


def build_claims(today: date) -> dict:
    R = lambda iso: rel(today, iso)
    out = {}

    def add(cid, policy, insured, code, text, loss, payments, event_id=None):
        out[cid] = {"claim_id": cid, "status": "paid", "policy_reference": policy, "insured": insured, "class_code": code,
                    "class_label": CLASS_LABELS[code], "description": text, "date_of_loss": R(loss),
                    "payments": [{"paid_on": R(day), "amount": float(amount)} for day, amount in payments], "event_id": event_id}

    add("RCL-8801", "TMI-CP-0114", "Wexcombe Furniture Makers", "CP", "Fire in the spray shop.", "2026-02-14",
        [("2026-04-20", 90000)])
    add("RCL-8802", "TMI-CP-0131", "Dunmallow Garden Centre", "CP", "Storm damage to the glasshouses.", "2026-03-09",
        [("2026-05-12", 150000), ("2026-06-30", 90000)])
    add("RCL-8803", "TMI-CP-0147", "Ilvane Cordage Works", "CP", "Fire in the rope walk and the store.", "2026-04-22",
        [("2026-06-15", 250000), ("2026-08-04", 160000)])
    add("RCL-8804", "TMI-CP-0152", "Marrowby Cannery", "CP", "Explosion of a retort. The production hall was damaged.", "2026-05-06",
        [("2026-07-10", 300000), ("2026-09-02", 250000), ("2026-11-03", 50000)])
    add("RCL-8805", "TMI-CP-0169", "Tallowby Tannery", "CP", "Flood from a burst water main.", "2026-06-19", [("2026-08-28", 250000)])
    add("RCL-8806", "TMI-CP-0175", "Greyhaven Warehousing", "CP", "Fire destroyed warehouse 3 and its stock.", "2026-07-02",
        [("2026-09-01", 500000), ("2026-10-20", 650000)])
    add("RCL-8807", "TMI-CP-0098", "Osprey Mill Textiles", "CP", "The roof of the weaving shed fell in under snow.", "2025-12-29",
        [("2026-03-16", 380000)])
    add("RCL-8808", "TMI-CP-0183", "Cinder Quay Chandlers", "CP", "Fire at Cinder Quay: unit 4 and its stock.", "2026-08-17",
        [("2026-10-12", 180000)], event_id="EVT-8891")
    add("RCL-8809", "TMI-CP-0184", "Cinder Quay Sailmakers", "CP", "Fire at Cinder Quay, spread from unit 4: unit 5 and its stock.",
        "2026-08-17", [("2026-10-26", 120000)], event_id="EVT-8891")
    add("RCL-8810", "TMI-EN-0212", "Harbourline Cold Stores", "EN", "Breakdown of a refrigeration compressor.", "2026-06-03",
        [("2026-07-21", 80000)])
    add("RCL-8811", "TMI-EN-0227", "Penhallow Printing Works", "EN", "Press 2 seized. Gearbox and rollers replaced.", "2026-07-12",
        [("2026-09-09", 150000)])
    return out


def build_events(today: date) -> dict:
    day = rel(today, "2026-08-17")
    return {"EVT-8891": {"event_id": "EVT-8891", "description": f"Fire at Cinder Quay, Port Ilvane, on {long_date(day)}. It began in "
                                                                "unit 4 and spread to unit 5.",
                         "date": day, "recorded_by": {"role": "claims handler"}, "claim_ids": ["RCL-8808", "RCL-8809"]}}


def build_recoveries(today: date) -> dict:
    R = lambda iso: rel(today, iso)
    return {
        "RCV-8851": {"recovery_id": "RCV-8851", "claim_id": "RCL-8804", "treaty_id": "TRY-8651", "kind": "recovery",
                     "kind_label": "recovery under the excess of loss treaty", "amount": 300000.0, "raised_on": R("2026-09-11"),
                     "raised_by": {"role": "reinsurance accountant"}, "paid_loss_when_raised": 550000.0,
                     "note": f"Raised on the paid loss as it stood on {long_date(R('2026-09-11'))}: USD 550,000.00."},
        "RCV-8852": {"recovery_id": "RCV-8852", "claim_id": "RCL-8811", "treaty_id": "TRY-8652", "kind": "cash_call",
                     "kind_label": "cash call under the quota share treaty", "amount": 60000.0, "raised_on": R("2026-09-16"),
                     "raised_by": {"role": "reinsurance accountant"}, "paid_loss_when_raised": 150000.0,
                     "note": "Cash call for the reinsurer's share of a paid loss of USD 150,000.00."},
    }


def paid_total(claim: dict) -> float:
    return round(sum(p["amount"] for p in claim["payments"]), 2)


def _sum_text(amounts) -> str:
    return " + ".join(plain(a) for a in amounts)


def _raised_status(recoverable, raised):
    if recoverable == 0 and raised == 0:
        return "nothing_due"
    if raised == 0:
        return "recovery_to_raise"
    if raised < recoverable:
        return "recovery_raised_for_too_little"
    return "recovery_raised_in_full" if raised == recoverable else "recovery_raised_for_too_much"


def _treaty_line(treaty, status, sentence, **more):
    return {"treaty_id": treaty["contract_id"], "treaty": treaty["title"], "treaty_kind": treaty["kind"],
            "treaty_kind_label": treaty["kind_label"], "reinsurer": treaty["counterparty"]["name"],
            "applies": status not in ("does_not_apply", "outside_the_treaty_period"), "status": status,
            "status_label": RECOVERY_LABELS[status], **more, "sentence": sentence}


def _outside_period(claim, treaty):
    start, end, loss = treaty["period_start"], treaty["period_end"], claim["date_of_loss"]
    if start <= loss <= end:
        return None
    if loss < start:
        n, side = days_from(loss, start), "before the period starts"
    else:
        n, side = days_from(end, loss), "after the period ends"
    return (f"The date of loss is {long_date(loss)}: {plural(n, 'day')} {side} ({long_date(start)} to {long_date(end)}, term "
            f"{'3' if treaty['kind'] == 'excess_of_loss_per_risk' else '4'}). Nothing is recovered under {treaty['contract_id']}. "
            "The treaty of the other year is not held in this system: a person checks which treaty answers.", n, side)


def recovery_for_claim(claim: dict, data: dict) -> dict:
    """What a paid claim recovers under each treaty, with the working. The system does every sum and share."""
    cid, paid = claim["claim_id"], paid_total(claim)
    amounts = [p["amount"] for p in claim["payments"]]
    paid_working = (f"Paid on {cid}: {_sum_text(amounts)} = {usd(paid)}." if len(amounts) > 1 else f"Paid on {cid}: {usd(paid)}.")
    raised_on = lambda ids, tid: [r for r in data["ri_recoveries"].values() if r["claim_id"] in ids and r["treaty_id"] == tid]
    lines = []
    for treaty in data["ri_contracts"].values():
        if treaty["kind"] == "binder":
            continue
        f, tid = treaty["figures"], treaty["contract_id"]
        covered = [c["code"] for c in f["classes_covered"]]
        if claim["class_code"] not in covered:
            lines.append(_treaty_line(treaty, "does_not_apply",
                                      f"{tid} covers {', '.join(CLASS_LABELS[c] for c in covered)} (term 1). This claim is "
                                      f"{claim['class_label']}: the treaty does not apply.",
                                      recoverable=0.0, raised_so_far=0.0, still_to_raise=0.0, to_raise_on_this_claim=0.0, working=[]))
            continue
        outside = _outside_period(claim, treaty)
        if outside:
            lines.append(_treaty_line(treaty, "outside_the_treaty_period", outside[0], recoverable=0.0, raised_so_far=0.0,
                                      still_to_raise=0.0, to_raise_on_this_claim=0.0, days_outside_the_period=outside[1],
                                      working=[paid_working, outside[0]]))
            continue
        if treaty["kind"] == "excess_of_loss_per_risk":
            attach, limit = f["attachment_point"], f["limit"]
            working, event, group = [paid_working], None, [claim]
            loss = paid
            if claim["event_id"]:
                group = [c for c in data["ri_claims"].values() if c["event_id"] == claim["event_id"]]
                loss = round(sum(paid_total(c) for c in group), 2)
                parts = ", ".join(f"{c['claim_id']} {plain(paid_total(c))}" for c in group)
                working.append(f"One event (term 6): {claim['event_id']} is recorded on {len(group)} claims ({parts}). They are "
                               f"added together and treated as one loss: {_sum_text([paid_total(c) for c in group])} = {usd(loss)}.")
            over = round(max(loss - attach, 0.0), 2)
            recoverable = round(min(over, limit), 2)
            above_limit = round(max(over - limit, 0.0), 2)
            if loss < attach:
                working.append(f"Attachment point (term 4): {usd(attach)}. The loss of {usd(loss)} is {usd(round(attach - loss, 2))} "
                               "below it: nothing is recovered.")
            elif loss == attach:
                working.append(f"Attachment point (term 4): {usd(attach)}. The loss of {usd(loss)} is exactly on it. Only the part "
                               "above the attachment point is recovered, and there is none: nothing is recovered.")
            else:
                working.append(f"Attachment point (term 4): {usd(attach)}. Above it: {plain(loss)} - {plain(attach)} = {usd(over)}.")
                if above_limit > 0:
                    working.append(f"Limit (term 5): {usd(limit)}. {usd(over)} is {usd(above_limit)} over the limit: the recovery is "
                                   f"capped at {usd(limit)} and {usd(above_limit)} stays with the insurer.")
                else:
                    working.append(f"Limit (term 5): {usd(limit)}. {usd(over)} is within the limit.")
            raised_rows = raised_on([c["claim_id"] for c in group], tid)
            raised = round(sum(r["amount"] for r in raised_rows), 2)
            still = round(recoverable - raised, 2)
            status = _raised_status(recoverable, raised)
            if recoverable > 0:
                ids = ", ".join(r["recovery_id"] for r in raised_rows)
                working.append(f"Recoverable: {usd(recoverable)}. Raised so far: {usd(raised)}{' (' + ids + ')' if ids else ''}. "
                               f"Still to raise: {plain(recoverable)} - {plain(raised)} = {usd(still)}.")
            premium = lambda amount: round(amount / limit * f["annual_premium"], 2)
            reinstatement = None
            if recoverable > 0:
                reinstatement = {"term": "7", "on_the_whole_recovery": premium(recoverable),
                                 "on_the_part_still_to_raise": premium(max(still, 0.0)),
                                 "working": f"{plain(recoverable)} / {plain(limit)} x {plain(f['annual_premium'])} = "
                                            f"{usd(premium(recoverable))} on the whole recovery; {plain(max(still, 0.0))} / {plain(limit)} "
                                            f"x {plain(f['annual_premium'])} = {usd(premium(max(still, 0.0)))} on the part still to raise.",
                                 "note": "A reinstatement premium is owed to the reinsurer with the recovery. The reinsurance "
                                         "accountant books it."}
                working.append("Reinstatement premium (term 7): " + reinstatement["working"])
            mine = still
            if len(group) > 1:
                shares, left = {}, recoverable
                for c in group[:-1]:
                    shares[c["claim_id"]] = round(recoverable * paid_total(c) / loss, 2) if loss else 0.0
                    left = round(left - shares[c["claim_id"]], 2)
                shares[group[-1]["claim_id"]] = left
                raised_mine = round(sum(r["amount"] for r in raised_rows if r["claim_id"] == cid), 2)
                mine = round(shares[cid] - raised_mine, 2)
                event = {"event_id": claim["event_id"], "description": data["ri_events"][claim["event_id"]]["description"],
                         "claims": [{"claim_id": c["claim_id"], "insured": c["insured"], "paid": paid_total(c),
                                     "share_of_the_recovery": shares[c["claim_id"]]} for c in group],
                         "loss_of_the_event": loss, "recovery_of_the_event": recoverable,
                         "note": "The recovery is raised once for the event. Each claim's share is in proportion to what was paid on it."}
                if recoverable > 0:
                    split = "; ".join(f"{c['claim_id']} {plain(recoverable)} x {plain(paid_total(c))} / {plain(loss)} = "
                                      f"{usd(shares[c['claim_id']])}" for c in group)
                    working.append(f"Share of each claim, in proportion to what was paid: {split}.")
            if status == "nothing_due":
                sentence = working[-1]
            elif status == "recovery_to_raise":
                sentence = (f"{usd(recoverable)} is recoverable under {tid} and no recovery is raised: {usd(still)} to raise"
                            + (f", of which {usd(mine)} on {cid}." if event else "."))
            elif status == "recovery_raised_for_too_little":
                sentence = (f"{usd(recoverable)} is recoverable under {tid} and {usd(raised)} is raised: {usd(still)} more to raise.")
            elif status == "recovery_raised_in_full":
                sentence = f"{usd(recoverable)} is recoverable under {tid} and {usd(raised)} is raised: nothing more to raise."
            else:
                sentence = (f"{usd(recoverable)} is recoverable under {tid} and {usd(raised)} is raised: {usd(-still)} more than is "
                            "due. A person looks at it.")
            lines.append(_treaty_line(treaty, status, sentence, loss_measured=loss, attachment_point=attach, limit=limit,
                                      above_the_attachment_point=over, above_the_limit_kept_by_the_insurer=above_limit,
                                      recoverable=recoverable, raised_so_far=raised,
                                      recoveries_raised=[r["recovery_id"] for r in raised_rows], still_to_raise=still,
                                      to_raise_on_this_claim=max(mine, 0.0) if status != "recovery_raised_for_too_much" else 0.0,
                                      reinstatement_premium=reinstatement, event=event, working=working))
        else:  # quota share
            share_pct, cash = f["cession_percent"], f["cash_loss_limit"]
            share = round(paid * share_pct / 100, 2)
            working = [paid_working, f"The reinsurer's share (term 8): {share_pct:.2f} percent of {plain(paid)} = {usd(share)}."]
            raised_rows = raised_on([cid], tid)
            raised = round(sum(r["amount"] for r in raised_rows), 2)
            if paid < cash:
                status, still = "collected_in_the_quarterly_account", 0.0
                working.append(f"Cash call (term 8): the paid loss of {usd(paid)} is below {usd(cash)}, so the share is collected "
                               "in the quarterly account. No cash call is raised.")
                sentence = (f"The reinsurer's share is {usd(share)}. The paid loss is below the cash call threshold of {usd(cash)}: "
                            "the share goes in the quarterly account and there is nothing to raise now.")
            else:
                still = round(share - raised, 2)
                status = _raised_status(share, raised)
                ids = ", ".join(r["recovery_id"] for r in raised_rows)
                working.append(f"Cash call (term 8): the paid loss of {usd(paid)} is {usd(cash)} or more, so the share is collected "
                               f"by a cash call. Raised so far: {usd(raised)}{' (' + ids + ')' if ids else ''}. Still to raise: "
                               f"{plain(share)} - {plain(raised)} = {usd(still)}.")
                sentence = (f"The reinsurer's share is {usd(share)}, collected by a cash call. {usd(raised)} is raised: "
                            + ("nothing more to raise." if still == 0 else f"{usd(abs(still))} {'to raise' if still > 0 else 'more than is due'}."))
            lines.append(_treaty_line(treaty, status, sentence, loss_measured=paid, cession_percent=share_pct,
                                      share_of_the_reinsurer=share, cash_call_threshold=cash, recoverable=share, raised_so_far=raised,
                                      recoveries_raised=[r["recovery_id"] for r in raised_rows], still_to_raise=still,
                                      to_raise_on_this_claim=max(still, 0.0), working=working))
    main = next((x for x in lines if x["status"] != "does_not_apply"), None)
    status = main["status"] if main else "does_not_apply"
    year = None
    if main and main["applies"]:
        t = data["ri_contracts"][main["treaty_id"]]
        year = {"treaty_id": t["contract_id"], "treaty_year": t["treaty_year"],
                "sentence": f"The date of loss, {long_date(claim['date_of_loss'])}, falls in the {t['treaty_year']} year of "
                            f"{t['contract_id']} ({long_date(t['period_start'])} to {long_date(t['period_end'])})."}
    elif main:
        year = {"treaty_id": main["treaty_id"], "treaty_year": None, "sentence": main["sentence"]}
    return {"claim_id": cid, "paid_total": paid, "paid_working": paid_working, "treaty_year": year, "under_each_treaty": lines,
            "status": status, "status_label": RECOVERY_LABELS[status],
            "treaty_that_answers": main["treaty_id"] if main and main["applies"] else None,
            "to_raise_on_this_claim": round(sum(x["to_raise_on_this_claim"] for x in lines), 2),
            "needs_a_person": status in ("outside_the_treaty_period", "recovery_raised_for_too_much", "does_not_apply"),
            "sentence": main["sentence"] if main else "No treaty held in this system covers the class of this claim.",
            "goes_to": WHO_DECIDES["reinsurance"]}


# ---------------------------------------------------------------- partners

PARTNER_KINDS = {"administrator": "claims administrator (handles claims for the insurer)", "repair_network": "repair network",
                 "supplier": "supplier"}
METRIC_LABELS = {"turnaround_days": "average turnaround in days", "complaint_rate": "complaint rate: complaints per 100 jobs",
                 "re_repair_rate": "re-repair rate: repairs done again per 100 repairs",
                 "report_on_time": "monthly report received on time"}
CREDENTIAL_KINDS = {"licence": "licence", "insurance_certificate": "insurance certificate", "accreditation": "accreditation"}
SL_RESULT_LABELS = {"met": "the service level is met", "not_met": "the service level is not met",
                    "cannot_tell": "cannot tell: a figure for the period is missing"}
CREDENTIAL_RESULT_LABELS = {"valid": "valid", "expires_within_the_notice_window": "valid, and expires within the notice window: a warning",
                            "expired": "expired"}
PARTNER_OVERALL_LABELS = {"within": "every service level is met and every credential is valid",
                          "warning": "nothing is missed; a credential expires within the notice window",
                          "not_met": "one or more service levels are not met or a credential has expired",
                          "cannot_tell": "a figure is missing: a person must get it before the partner can be measured"}
NOTICE_WINDOW_DAYS = 30
REPORT_DAYS = 10


def build_partners(today: date) -> dict:
    R = lambda iso: rel(today, iso)
    out = {}

    def add(pid, name, kind, service, turnaround_what, limits, figures, credentials):
        levels = [{"term": "SL-1", "metric": "turnaround_days", "metric_label": METRIC_LABELS["turnaround_days"],
                   "limit": limits["turnaround"], "unit": "days",
                   "text": f"The average time {turnaround_what} in a month is not more than {limits['turnaround']:.1f} days. An "
                           "average exactly on the limit meets the service level."},
                  {"term": "SL-2", "metric": "complaint_rate", "metric_label": METRIC_LABELS["complaint_rate"],
                   "limit": limits["complaints"], "unit": "percent",
                   "text": f"Complaints about the partner in a month are not more than {limits['complaints']:.2f} percent of the jobs "
                           "of that month. A rate exactly on the limit meets the service level."}]
        if "re_repairs" in limits:
            levels.append({"term": "SL-3", "metric": "re_repair_rate", "metric_label": METRIC_LABELS["re_repair_rate"],
                           "limit": limits["re_repairs"], "unit": "percent",
                           "text": f"Repairs that had to be done again in a month are not more than {limits['re_repairs']:.2f} "
                                   "percent of the repairs of that month. A rate exactly on the limit meets the service level."})
        levels.append({"term": "SL-4", "metric": "report_on_time", "metric_label": METRIC_LABELS["report_on_time"],
                       "limit": REPORT_DAYS, "unit": "days after the month ends",
                       "text": f"The partner sends its monthly report within {REPORT_DAYS} days after the last day of the month. A "
                               "report on the last of those days is on time."})
        out[pid] = {
            "partner_id": pid, "name": name, "kind": kind, "kind_label": PARTNER_KINDS[kind], "service": service, "status": "active",
            "contract": {"service_levels": levels,
                         "credentials_term": {"term": "SL-5", "heading": "Credentials",
                                              "text": "Every credential the contract names is valid on every day of the contract. "
                                                      "A credential is valid up to and including its expiry date and has expired "
                                                      f"from the day after. A credential that expires within {NOTICE_WINDOW_DAYS} "
                                                      "days is a warning for the supplier manager, not a miss.",
                                              "notice_window_days": NOTICE_WINDOW_DAYS}},
            "period": {"period_start": R("2026-10-01"), "period_end": R("2026-10-31"), "figures": figures},
            "credentials": [{"credential_id": f"{pid}-C{n}", "kind": k, "kind_label": CREDENTIAL_KINDS[k], "name": label,
                             "issued_by": issuer, "expires_on": R(expiry)}
                            for n, (k, label, issuer, expiry) in enumerate(credentials, 1)],
            "review_drafts": []}

    def fig(jobs, turnaround, complaints, report, re_repairs="none"):
        f = {"jobs": jobs, "average_turnaround_days": turnaround, "complaints": complaints,
             "report_received_on": R(report) if report else None}
        if re_repairs != "none":
            f["re_repairs"] = re_repairs
        return f

    add("PTN-8901", "Brackenhall Claims Administration", "administrator", "Handles travel claims for the insurer.",
        "from a complete claim to its settlement", {"turnaround": 5.0, "complaints": 2.0}, fig(640, 4.1, 8, "2026-11-06"),
        [("licence", "Claims administrator's licence", "Meridia Trades Register (invented)", "2027-06-30"),
         ("insurance_certificate", "Professional indemnity insurance", "Stonebeck Assurance (invented)", "2027-03-31")])
    add("PTN-8902", "Ilvane Bodyworks Network", "repair_network", "Repairs motor vehicles after a claim.",
        "from the car's arrival to its return", {"turnaround": 8.0, "complaints": 3.0, "re_repairs": 4.0},
        fig(300, 7.2, 6, "2026-11-09", re_repairs=9),
        [("insurance_certificate", "Public liability insurance", "Stonebeck Assurance (invented)", "2027-09-30"),
         ("accreditation", "Motor repair standard", "Meridia Vehicle Repair Board (invented)", "2027-02-28")])
    add("PTN-8903", "Marlow Reach Glass and Glazing", "supplier", "Replaces windscreens and household glass.",
        "from the order to the glass being fitted", {"turnaround": 3.0, "complaints": 2.0}, fig(250, 4.2, 3, "2026-11-05"),
        [("insurance_certificate", "Public liability insurance", "Stonebeck Assurance (invented)", "2027-05-31")])
    add("PTN-8904", "Tallowby Motor Repairers", "repair_network", "Repairs motor vehicles after a claim.",
        "from the car's arrival to its return", {"turnaround": 8.0, "complaints": 3.0, "re_repairs": 4.0},
        fig(160, 6.5, 2, "2026-11-04", re_repairs=4),
        [("insurance_certificate", "Public liability insurance", "Harrowmere Mutual (invented)", "2027-07-31"),
         ("accreditation", "Motor repair standard", "Meridia Vehicle Repair Board (invented)", "2026-11-14")])
    add("PTN-8905", "Copperlow Hire Cars", "supplier", "Supplies a hire car while a customer's car is repaired.",
        "from the order to the hire car being delivered", {"turnaround": 2.0, "complaints": 2.5}, fig(200, 1.4, 4, "2026-11-07"),
        [("licence", "Vehicle hire operator's licence", "Meridia Trades Register (invented)", "2027-04-30"),
         ("insurance_certificate", "Motor fleet insurance", "Harrowmere Mutual (invented)", "2026-12-15")])
    add("PTN-8906", "Fernside Loss Adjusters", "supplier", "Visits and reports on larger property claims.",
        "from the instruction to the first report", {"turnaround": 10.0, "complaints": 2.0}, fig(200, 8.6, 4, "2026-11-05"),
        [("licence", "Loss adjuster's licence", "Meridia Trades Register (invented)", "2027-12-31"),
         ("insurance_certificate", "Professional indemnity insurance", "Stonebeck Assurance (invented)", "2027-06-30")])
    add("PTN-8907", "Quarrymead Medical Claims Administrators", "administrator", "Handles medical claims for the insurer.",
        "from a complete claim to its settlement", {"turnaround": 5.0, "complaints": 2.0}, fig(510, 4.6, None, "2026-11-09"),
        [("licence", "Claims administrator's licence", "Meridia Trades Register (invented)", "2027-08-31"),
         ("insurance_certificate", "Professional indemnity insurance", "Harrowmere Mutual (invented)", "2027-01-31")])
    out["PTN-8907"]["period"]["note"] = ("The monthly report gives the jobs and the turnaround. Its line for complaints is empty: no "
                                         "figure was given for the period.")
    add("PTN-8908", "Saltmarsh Roofing and Building Repairs", "repair_network", "Repairs buildings after a claim.",
        "from the instruction to the repair being finished", {"turnaround": 12.0, "complaints": 3.0, "re_repairs": 5.0},
        fig(80, 10.5, 2, "2026-11-17", re_repairs=6),
        [("insurance_certificate", "Public liability insurance", "Stonebeck Assurance (invented)", "2027-10-31"),
         ("accreditation", "Building repair standard", "Meridia Builders' Guild (invented)", "2027-04-30")])
    return out


def measure_partner(partner: dict, today_iso: str) -> dict:
    """A partner against its service levels and credentials on the insurer date. Every rate and day count is the system's."""
    period, figures, rows = partner["period"], partner["period"]["figures"], []
    month = f"{long_date(period['period_start'])} to {long_date(period['period_end'])}"

    def row(level, result, measured, difference, working, sentence):
        rows.append({"term": level["term"], "metric": level["metric"], "metric_label": level["metric_label"], "result": result,
                     "result_label": SL_RESULT_LABELS[result], "measured": measured, "limit": level["limit"], "unit": level["unit"],
                     "difference": difference, "working": working, "sentence": sentence})

    for level in partner["contract"]["service_levels"]:
        limit, term = level["limit"], level["term"]
        if level["metric"] == "turnaround_days":
            got = figures.get("average_turnaround_days")
            if got is None:
                row(level, "cannot_tell", None, None, None, f"{term}: no average turnaround was reported for {month}. It cannot be told.")
                continue
            diff = round(got - limit, 1)
            if diff > 0:
                row(level, "not_met", got, diff, None, f"{term}: the average turnaround was {got:.1f} days against a limit of "
                                                       f"{limit:.1f} days: {diff:.1f} days over.")
            else:
                row(level, "met", got, 0.0, None, f"{term}: the average turnaround was {got:.1f} days against a limit of {limit:.1f} "
                                                  f"days: {'exactly on the limit, which meets it' if diff == 0 else 'within it'}.")
        elif level["metric"] in ("complaint_rate", "re_repair_rate"):
            field, noun = ("complaints", "complaints") if level["metric"] == "complaint_rate" else ("re_repairs", "repairs done again")
            count, jobs = figures.get(field), figures.get("jobs")
            if count is None or not jobs:
                missing = f"number of {noun}" if count is None else "number of jobs"
                row(level, "cannot_tell", None, None, None,
                    f"{term}: the {missing} for {month} is not on the record. The rate cannot be worked out and nothing is assumed. "
                    "A person must get the figure.")
                continue
            rate = round(count / jobs * 100, 2)
            diff = round(rate - limit, 2)
            working = f"{count} / {jobs} x 100 = {rate:.2f} percent"
            if diff > 0:
                row(level, "not_met", rate, diff, working, f"{term}: {count} {noun} on {jobs} jobs is {rate:.2f} percent against a "
                                                           f"limit of {limit:.2f} percent: {diff:.2f} over.")
            else:
                row(level, "met", rate, 0.0, working, f"{term}: {count} {noun} on {jobs} jobs is {rate:.2f} percent against a limit "
                                                      f"of {limit:.2f} percent: "
                                                      f"{'exactly on the limit, which meets it' if diff == 0 else 'within it'}.")
        else:  # report_on_time
            due = plus_days(period["period_end"], limit)
            got = figures.get("report_received_on")
            lead = f"{term}: the report for the month was due by {long_date(due)}, {limit} days after {long_date(period['period_end'])}."
            if got:
                taken = days_from(period["period_end"], got)
                late = max(taken - limit, 0)
                row(level, "not_met" if late else "met", taken, late, None,
                    f"{lead} It was received on {long_date(got)}, {plural(taken, 'day')} after the month ended: "
                    + (f"{plural(late, 'day')} late." if late else "on time."))
            elif today_iso > due:
                late = days_from(due, today_iso)
                row(level, "not_met", None, late, None, f"{lead} No report is recorded and {long_date(today_iso)} is "
                                                        f"{plural(late, 'day')} after that date.")
            else:
                row(level, "met", None, 0, None, f"{lead} No report is recorded yet and the date has not passed.")
            rows[-1]["due_on"], rows[-1]["received_on"] = due, got

    window = partner["contract"]["credentials_term"]["notice_window_days"]
    creds = []
    for c in partner["credentials"]:
        left = days_from(today_iso, c["expires_on"])
        if left < 0:
            result = "expired"
            sentence = (f"SL-5: the {c['kind_label']} ({c['name']}) expired on {long_date(c['expires_on'])}, {plural(-left, 'day')} "
                        f"before {long_date(today_iso)}.")
        elif left <= window:
            result = "expires_within_the_notice_window"
            sentence = (f"SL-5: the {c['kind_label']} ({c['name']}) is valid and expires on {long_date(c['expires_on'])}, in "
                        f"{plural(left, 'day')}: inside the notice window of {window} days. A warning, not a miss.")
        else:
            result = "valid"
            sentence = (f"SL-5: the {c['kind_label']} ({c['name']}) is valid until {long_date(c['expires_on'])}, {plural(left, 'day')} "
                        f"from {long_date(today_iso)}.")
        creds.append({"credential_id": c["credential_id"], "term": "SL-5", "kind": c["kind"], "kind_label": c["kind_label"],
                      "name": c["name"], "expires_on": c["expires_on"], "days_to_expiry": left, "notice_window_days": window,
                      "result": result, "result_label": CREDENTIAL_RESULT_LABELS[result], "sentence": sentence})

    not_met = [r["term"] for r in rows if r["result"] == "not_met"] + [c["credential_id"] for c in creds if c["result"] == "expired"]
    cannot = [r["term"] for r in rows if r["result"] == "cannot_tell"]
    warnings = [c["credential_id"] for c in creds if c["result"] == "expires_within_the_notice_window"]
    overall = "not_met" if not_met else "cannot_tell" if cannot else "warning" if warnings else "within"
    return {"partner_id": partner["partner_id"], "name": partner["name"], "measured_on": today_iso,
            "period_start": period["period_start"], "period_end": period["period_end"], "service_levels": rows, "credentials": creds,
            "not_met": not_met, "cannot_tell": cannot, "warnings": warnings, "overall": overall,
            "overall_label": PARTNER_OVERALL_LABELS[overall], "needs_a_person": bool(cannot),
            "counted": {"service_levels": len(rows), "service_levels_met": sum(1 for r in rows if r["result"] == "met"),
                        "service_levels_not_met": sum(1 for r in rows if r["result"] == "not_met"),
                        "service_levels_that_cannot_be_told": len(cannot), "credentials": len(creds),
                        "credentials_expired": sum(1 for c in creds if c["result"] == "expired"), "credential_warnings": len(warnings)},
            "goes_to": WHO_DECIDES["partners"]}


# ---------------------------------------------------------------- the whole set

def build_reinsurance(today: date) -> dict:
    return copy.deepcopy({
        "ri_contracts": build_contracts(today),
        "ri_bordereaux": build_bordereaux(today),
        "ri_claims": build_claims(today),
        "ri_events": build_events(today),
        "ri_recoveries": build_recoveries(today),
        "ri_recovery_lists": {"RLIST-8800": {"recovery_list_id": "RLIST-8800", "what": "Draft recovery lists of the reinsurance desk.",
                                             "drafts": []}},
        "ri_partners": build_partners(today),
    })
