"""Seed data, part 12: a pension scheme run by the bank's trust arm. Funds, members, holdings, contribution batches and transfer forms.

Members who are also customers take their name, date of birth, address and employer from the core system data, so the records agree.
SCENARIOS.md has the right answers: MEM-5001 holds three funds, BAT-4001 is clean, BAT-4002 has three faults, FRM-4001 has an account number that cannot be read.
"""

from __future__ import annotations

from datetime import date, timedelta

from .seed_base import d_ago

SCHEME = "Meridian Trust Pension Scheme"
TRUST_ARM = "Meridian Trust Pensions"
MIN_EMPLOYER_RATE = 0.03

# fund_id, name, risk (1 to 7), amc %, ongoing %, launched days ago, price, returns [1m, 3m, 6m, 1y, 3y ann, 5y ann, since launch ann], asset mix
FUNDS = [
    ("FND-3001", "Meridia Cautious Income Fund", 2, 0.45, 0.52, 3300, 1.2840, [0.3, 1.1, 2.4, 4.6, 3.9, 3.1, 3.6], "70 percent bonds, 20 percent cash, 10 percent shares"),
    ("FND-3002", "Meridia Balanced Growth Fund", 4, 0.65, 0.73, 1520, 2.0715, [0.8, 2.2, 4.9, 8.3, 6.7, None, 6.2], "50 percent shares, 40 percent bonds, 10 percent property"),
    ("FND-3003", "Meridia Global Equity Fund", 6, 0.75, 0.84, 3400, 3.4520, [1.4, 3.9, 8.8, 14.2, 11.5, 9.4, 8.9], "100 percent shares in 14 countries"),
    ("FND-3004", "Meridia Index-Linked Bond Fund", 3, 0.40, 0.47, 2200, 1.0950, [0.2, 0.9, 1.7, 2.9, 1.8, 1.2, 2.0], "100 percent inflation-linked bonds"),
    ("FND-3005", "Meridia Sustainable Equity Fund", 6, 0.80, 0.89, 760, 1.3180, [1.2, 3.5, 7.9, 12.6, None, None, 11.0], "100 percent shares chosen by the fund's environmental screen"),
]
PERIODS = ["1 month", "3 months", "6 months", "1 year", "3 years a year", "5 years a year", "since launch a year"]

# member_id, customer_id or "", name, dob, address, employer, joined days ago, fund holdings {fund: units}, contribution fund
MEMBERS = [
    ("MEM-5001", "CUS-1011", "", "", "", "", 2900, {"FND-3001": 4210.5, "FND-3002": 6800.0, "FND-3003": 2950.25}, "FND-3002"),
    ("MEM-5002", "CUS-1003", "", "", "", "", 2400, {"FND-3003": 5120.0}, "FND-3003"),
    ("MEM-5003", "", "Idony Carrowmere", "1983-03-14", "27 Wicker Lane, Tallowby, Meridia", "Harbourlight Services", 1800, {"FND-3001": 2100.0, "FND-3004": 3300.5}, "FND-3004"),
    ("MEM-5004", "", "Casimir Thornwhistle", "1976-09-02", "4 Gull Quay, Port Ilvane, Meridia", "Harbourlight Services", 3100, {"FND-3002": 9800.75}, "FND-3002"),
    ("MEM-5005", "", "Odalys Penrhoss-Vale", "1990-12-19", "61 Hawthorn Rise, Marlow Reach, Meridia", "Harbourlight Services", 900, {"FND-3005": 3000.0}, "FND-3005"),
    ("MEM-5006", "CUS-1006", "", "", "", "", 2600, {"FND-3002": 1500.0}, "FND-3002"),
    ("MEM-5007", "CUS-1014", "", "", "", "", 1100, {"FND-3003": 800.5, "FND-3005": 410.0}, "FND-3003"),
    ("MEM-5008", "", "Wilmot Ashdene", "1969-05-30", "12 Cooper Row, Tallowby, Meridia", "Stillwater Clinic", 4200, {"FND-3001": 12000.0}, "FND-3001"),
    ("MEM-5009", "", "Corisande Whitlow", "1995-08-08", "8 Brindle Court, Port Ilvane, Meridia", "Stillwater Clinic", 600, {"FND-3003": 150.0}, "FND-3003"),
]

PROCEDURE = {
    "procedure_id": "MTP-PROC-PEN-1", "title": "Contribution and transfer processing rules (invented)",
    "applies_to": "Every row of a contribution batch (rules 1 to 4) and every transfer form (rules 5 to 8).",
    "rules": [
        {"rule_no": 1, "applies_to": "contribution row", "text": "The member id on the row must exist in the scheme register. A row with an unknown member id fails."},
        {"rule_no": 2, "applies_to": "contribution row", "text": "The employee amount and the employer amount must each be zero or more. A negative amount fails."},
        {"rule_no": 3, "applies_to": "contribution row", "text": "A member may appear once in a batch. The second and any later row for the same member fails. The first row is judged on its own."},
        {"rule_no": 4, "applies_to": "contribution row", "text": "The employer amount must be at least 3 percent of the pensionable salary on the row."},
        {"rule_no": 5, "applies_to": "transfer form", "text": "The form must name the receiving scheme and give its account number so that every digit can be read. A digit that cannot be read, or can be read two ways, fails."},
        {"rule_no": 6, "applies_to": "transfer form", "text": "The form must carry the member's signature and a signing date no more than 90 days before the date the form was received."},
        {"rule_no": 7, "applies_to": "transfer form", "text": "The member's name and date of birth on the form must match the register."},
        {"rule_no": 8, "applies_to": "transfer form", "text": "A form that fails rule 5, or that cannot be read with confidence in any other field, goes to a person. An account number is never guessed or completed."}],
    "posting": "Only the rows that passed are posted, and only after a person approves. A failed row is returned to the employer with the rule number.",
}


def fact_sheet_text(f: dict) -> str:
    lines = [f"{f['name']}", f"Fact sheet as at {f['as_of']}", f"Scheme: {SCHEME}, run by {TRUST_ARM}.", "",
             f"Risk level: {f['risk_level']} on a scale of 1 (lowest) to 7 (highest).", f"Launched: {f['launched']}.",
             f"What it holds: {f['asset_mix']}.", f"Unit price at {f['as_of']}: USD {f['unit_price']:.4f}.", "",
             f"Annual management charge: {f['annual_management_charge_pct']:.2f} percent.", f"Ongoing charges: {f['ongoing_charges_pct']:.2f} percent.", "",
             "Returns after charges, in percent:"]
    for label, v in zip(PERIODS, f["returns_pct"]):
        lines.append(f"  {label}: " + (f"{v:.1f}" if v is not None else "not shown, the fund is younger than this period"))
    lines += ["", "The fact sheet shows these periods only. It does not show calendar years or any other period."]
    return "\n".join(lines)


def build_funds_table(today: date) -> dict:
    out = {}
    as_of = (today.replace(day=1) - timedelta(days=1)).isoformat()
    for fid, name, risk, amc, ocf, ago, price, rets, mix in FUNDS:
        f = {"fund_id": fid, "name": name, "risk_level": risk, "annual_management_charge_pct": amc, "ongoing_charges_pct": ocf,
             "launched": d_ago(today, ago), "unit_price": price, "price_date": as_of, "as_of": as_of, "asset_mix": mix,
             "returns_pct": rets, "currency": "USD"}
        f["fact_sheet_text"] = fact_sheet_text(f)
        out[fid] = f
    return out


def employer_of(customer_id: str, accounts: dict, txns: dict) -> str:
    acc = customer_id.replace("CUS-", "ACC-") + "-01"
    names = sorted({t["counterparty"] for t in txns.values() if t["account_id"] == acc and t["type"] == "salary"})
    return names[0] if names else ""


def build_members(today: date, customers: dict, accounts: dict, txns: dict) -> tuple[dict, dict]:
    members, holdings = {}, {}
    for mid, cid, name, dob, addr, employer, joined, held, fund in MEMBERS:
        if cid:
            c = customers[cid]
            name, dob, addr = c["name"], c["date_of_birth"], c["address"]
            employer = employer_of(cid, accounts, txns)
        members[mid] = {"member_id": mid, "customer_id": cid, "name": name, "date_of_birth": dob, "address": addr, "employer": employer,
                        "joined": d_ago(today, joined), "status": "active", "contribution_fund_id": fund, "scheme": SCHEME}
        holdings[mid] = dict(held)
    return members, holdings


def row(n, mid, name, salary, ee, er):
    return {"row_no": n, "member_id": mid, "member_name": name, "pensionable_salary": salary, "employee_amount": ee, "employer_amount": er,
            "currency": "USD"}


def period_of(today: date) -> str:
    first = today.replace(day=1) - timedelta(days=1)
    return f"{first.year}-{first.month:02d}"


def build_batches(today: date, members: dict) -> dict:
    per = period_of(today)
    nm = lambda m: members[m]["name"]
    b = {}
    b["BAT-4001"] = {"batch_id": "BAT-4001", "employer": "Harbourlight Services", "period": per, "received_on": d_ago(today, 3), "status": "received",
                     "control_total": 3170.0, "rows": [
        row(1, "MEM-5001", nm("MEM-5001"), 3590.0, 179.5, 215.4), row(2, "MEM-5002", nm("MEM-5002"), 3920.0, 196.0, 235.2),
        row(3, "MEM-5003", nm("MEM-5003"), 3100.0, 155.0, 186.0), row(4, "MEM-5004", nm("MEM-5004"), 4400.0, 220.0, 264.0),
        row(5, "MEM-5005", nm("MEM-5005"), 2800.0, 140.0, 168.0)]}
    b["BAT-4001"]["control_total"] = round(sum(r["employee_amount"] + r["employer_amount"] for r in b["BAT-4001"]["rows"]), 2)
    b["BAT-4002"] = {"batch_id": "BAT-4002", "employer": "Stillwater Clinic", "period": per, "received_on": d_ago(today, 2), "status": "received",
                     "control_total": 0.0, "rows": [
        row(1, "MEM-5006", nm("MEM-5006"), 3200.0, 160.0, 192.0), row(2, "MEM-5007", nm("MEM-5007"), 2750.0, 137.5, 165.0),
        row(3, "MEM-5008", nm("MEM-5008"), 5100.0, 255.0, 306.0), row(4, "MEM-5040", "Alaric Brightmore", 3000.0, 150.0, 180.0),
        row(5, "MEM-5007", nm("MEM-5007"), 2750.0, 137.5, 165.0), row(6, "MEM-5009", nm("MEM-5009"), 3000.0, -85.0, 120.0)]}
    b["BAT-4002"]["control_total"] = round(sum(r["employee_amount"] + r["employer_amount"] for r in b["BAT-4002"]["rows"]), 2)
    earlier = f"{(today.replace(day=1) - timedelta(days=1)).replace(day=1) - timedelta(days=1):%Y-%m}"
    b["BAT-4003"] = {"batch_id": "BAT-4003", "employer": "Harbourlight Services", "period": earlier, "received_on": d_ago(today, 33), "status": "posted",
                     "control_total": 0.0, "rows": [row(1, "MEM-5001", nm("MEM-5001"), 3590.0, 179.5, 215.4), row(2, "MEM-5003", nm("MEM-5003"), 3100.0, 155.0, 186.0)],
                     "posted": {"posted_on": d_ago(today, 31), "approved_by": "Tamsin Verrinder", "rows_posted": [1, 2], "rows_not_posted": [], "amount_posted": 735.9}}
    b["BAT-4003"]["control_total"] = 735.9
    for x in b.values():
        x["results"] = []
        x["posted"] = x.get("posted", None)
    return b


def build_forms(today: date) -> dict:
    sig_date = (today - timedelta(days=14)).strftime("%d/%m/%Y")
    f = {}
    f["FRM-4001"] = {
        "form_id": "FRM-4001", "member_id": "MEM-5003", "received_on": d_ago(today, 12), "scan_quality": "poor on the lower half",
        "text": "TRANSFER OUT REQUEST, FORM TF-2 (text read from a scan by machine; marks in square brackets are the reader's doubts)\n"
                "Member name: Idony Carrowmere\nMember id: MEM-5003\nDate of birth: 14/03/1983\n"
                "Receiving scheme: Hallowmere Workplace Pension\n"
                "Receiving scheme account number: 5 8 2 [unreadable] 7 1 [4 or 9] 3 0\n"
                "Amount to transfer: whole fund value\nSignature: present\n"
                f"Date signed: {sig_date}\nReceived by the trust arm: {(today - timedelta(days=12)).strftime('%d/%m/%Y')}"}
    f["FRM-4002"] = {
        "form_id": "FRM-4002", "member_id": "MEM-5002", "received_on": d_ago(today, 9), "scan_quality": "good",
        "text": "TRANSFER OUT REQUEST, FORM TF-2 (text read from a scan by machine)\n"
                "Member name: Sabine Tarrowgate\nMember id: MEM-5002\nDate of birth: 02/12/1979\n"
                "Receiving scheme: Brindlemoor Retirement Trust\nReceiving scheme account number: 6 1 4 0 9 2 7 7 3 5\n"
                "Amount to transfer: whole fund value\nSignature: present\n"
                f"Date signed: {(today - timedelta(days=10)).strftime('%d/%m/%Y')}\nReceived by the trust arm: {(today - timedelta(days=9)).strftime('%d/%m/%Y')}"}
    return f


def build_funds(today: date, customers: dict, accounts: dict, txns: dict) -> dict:
    members, holdings = build_members(today, customers, accounts, txns)
    return {"pension_funds": build_funds_table(today), "pension_members": members, "pension_holdings": holdings,
            "pension_batches": build_batches(today, members), "pension_forms": build_forms(today), "pension_procedure": PROCEDURE}


# ------------------------------------------------------------------ simulated batches (rotating templates)

def sim_batch(data: dict, today: date, kind: int, num: int) -> tuple[str, str]:
    members = data["pension_members"]
    bid = f"BAT-{4100 + num}"
    per = period_of(today)
    nm = lambda m: members[m]["name"]
    templates = [
        ("Harbourlight Services", [row(1, "MEM-5003", nm("MEM-5003"), 3100.0, 155.0, 186.0), row(2, "MEM-5004", nm("MEM-5004"), 4400.0, 220.0, 264.0),
                                   row(3, "MEM-5005", nm("MEM-5005"), 2800.0, 140.0, 168.0), row(4, "MEM-5001", nm("MEM-5001"), 3590.0, 179.5, 215.4)],
         "Every row looks clean."),
        ("Stillwater Clinic", [row(1, "MEM-5008", nm("MEM-5008"), 5100.0, 255.0, 306.0), row(2, "MEM-5009", nm("MEM-5009"), 3000.0, 150.0, 180.0),
                               row(3, "MEM-5077", "Benedikt Aldermoor", 2900.0, 145.0, 174.0)],
         "One row names a member id that is not in the register."),
        ("Harbourlight Services", [row(1, "MEM-5003", nm("MEM-5003"), 3100.0, 155.0, 186.0), row(2, "MEM-5004", nm("MEM-5004"), 4400.0, 220.0, 264.0),
                                   row(3, "MEM-5003", nm("MEM-5003"), 3100.0, 155.0, 186.0)],
         "One member appears twice."),
        ("Stillwater Clinic", [row(1, "MEM-5006", nm("MEM-5006"), 3200.0, 160.0, 192.0), row(2, "MEM-5007", nm("MEM-5007"), 2750.0, -137.5, 165.0),
                               row(3, "MEM-5009", nm("MEM-5009"), 3000.0, 150.0, 180.0)],
         "One row has a negative employee amount."),
    ]
    employer, rows, _ = templates[kind % 4]
    total = round(sum(r["employee_amount"] + r["employer_amount"] for r in rows), 2)
    data["pension_batches"][bid] = {"batch_id": bid, "employer": employer, "period": per, "received_on": today.isoformat(), "status": "received",
                                    "control_total": total, "rows": rows, "results": [], "posted": None}
    msg = (f"A new contribution batch {bid} has arrived in the funds system from {employer} for {per}. It has {len(rows)} rows and a control total of "
           f"USD {total:,.2f}. Read it with get_contribution_batch and check every row against the processing procedure.")
    return bid, msg
