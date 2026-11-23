"""Seed data, part 2: contacts, exposure, cards, screening, monitoring."""

from __future__ import annotations

from datetime import date, timedelta

from .seed_base import COUNTRIES, TxnBuilder, d_ago

LIST_NAME = "Meridia Consolidated Demonstration List (invented)"


def add_ids(customers: dict) -> None:
    for cid, c in customers.items():
        if c["type"] == "individual":
            num = int(cid.split("-")[1])
            c["id_number"] = f"MID-{num * 7919 % 10 ** 6:06d}"
    customers["CUS-1007"]["id_number"] = "QNP-4417-2290"


def build_contacts(customers: dict, today: date) -> dict:
    rows = [
        ("CUS-1002", "call", 2, "inbound", "Lost card reported",
         "Customer phoned at 18:40 and said the debit card was lost on the evening train at about 17:00. "
         "He did not yet ask for a block. Advised to call back or use the app.", "Contact centre"),
        ("CUS-1002", "email", 1, "inbound", "Unrecognised card payments",
         "Customer emailed that two payments on the lost card are not his: the online electronics purchase "
         "and the fuel station payment. He asks the bank to stop the card and send a new one.", "Contact centre"),
        ("CUS-1003", "branch_note", 18, "internal", "Card expiry",
         "Customer visited the branch. Mentioned the card runs out soon and travels next month. No action taken.",
         "Branch, Marlow Reach"),
        ("CUS-1004", "call", 9, "inbound", "Double charge at cinema",
         "Customer says the cinema charged him twice for the same booking. Dispute started by phone.",
         "Contact centre"),
        ("CUS-1010", "branch_note", 35, "internal", "Relationship note",
         "Customer's spouse holds a senior public office in Quenmark. Enhanced due diligence applies to this relationship.",
         "Branch, Port Ilvane"),
        ("CUS-1017", "call", 14, "inbound", "Loan enquiry",
         "Owner asked about a loan for a second delivery van and a cold-storage unit. Application LAP-8002 started.",
         "Business banking"),
        ("CUS-1018", "email", 20, "inbound", "Equipment loan",
         "Finance director sent the three years of accounts for the machine replacement loan (LAP-8003).",
         "Business banking"),
        ("CUS-1020", "branch_note", 6, "internal", "Cash deposits",
         "Cashier noted the owner now brings deposits in batches 'to keep things tidy'. Several in the last two weeks.",
         "Branch, Tallowby"),
        ("CUS-1021", "call", 25, "inbound", "Account use",
         "Customer says the account is used for client fees. Could not name the clients paying large sums.",
         "Business banking"),
        ("CUS-1022", "email", 30, "inbound", "New freight agent",
         "Customer says they began using a freight agent in Kharnovia. No contract was sent to the bank.",
         "Business banking"),
        ("CUS-1023", "call", 45, "inbound", "Seasonal staff",
         "Owner says about twenty seasonal staff will be hired for the harvest festival season, starting in about "
         "five weeks. Payroll will be larger for a few weeks.", "Business banking"),
        ("CUS-1019", "email", 80, "inbound", "Facility signed",
         "Facility LN-9001 signed. Customer asked for a copy of the facility agreement.", "Business banking"),
    ]
    out = {}
    for n, (cid, channel, ago, direction, subject, summary, by) in enumerate(rows, start=1):
        cnt = f"CNT-{5000 + n}"
        out[cnt] = {"contact_id": cnt, "customer_id": cid, "channel": channel, "date": d_ago(today, ago),
                    "direction": direction, "subject": subject, "summary": summary, "recorded_by": by,
                    "drafted_by": by, "version": 1}
    return out


def build_loans_and_exposure(customers: dict, today: date) -> tuple[dict, dict]:
    loans = {
        "LN-9001": {"loan_id": "LN-9001", "customer_id": "CUS-1019", "product": "Term loan (vehicles)",
                    "currency": "USD", "principal": 250000.0, "outstanding": 250000.0, "status": "active",
                    "start_date": d_ago(today, 75), "maturity_date": d_ago(today, -1750)},
        "LN-9002": {"loan_id": "LN-9002", "customer_id": "CUS-1018", "product": "Equipment loan",
                    "currency": "USD", "principal": 300000.0, "outstanding": 180000.0, "status": "active",
                    "start_date": d_ago(today, 1500), "maturity_date": d_ago(today, -1095)},
        "LN-9003": {"loan_id": "LN-9003", "customer_id": "CUS-1013", "product": "Home loan",
                    "currency": "USD", "principal": 240000.0, "outstanding": 201500.0, "status": "active",
                    "start_date": d_ago(today, 1100), "maturity_date": d_ago(today, -5500)},
        "LN-9004": {"loan_id": "LN-9004", "customer_id": "CUS-1024", "product": "Equipment loan",
                    "currency": "USD", "principal": 90000.0, "outstanding": 61200.0, "status": "active",
                    "start_date": d_ago(today, 800), "maturity_date": d_ago(today, -1000)},
        "LN-9005": {"loan_id": "LN-9005", "customer_id": "CUS-1012", "product": "Car loan",
                    "currency": "USD", "principal": 12000.0, "outstanding": 4300.0, "status": "active",
                    "start_date": d_ago(today, 520), "maturity_date": d_ago(today, -300)},
    }
    exposure = {}
    for cid in customers:
        exposure[cid] = {"customer_id": cid, "currency": "USD", "loans": [], "limits": [], "collateral": []}
    for ln in loans.values():
        exposure[ln["customer_id"]]["loans"].append(
            {k: ln[k] for k in ("loan_id", "product", "principal", "outstanding", "status", "maturity_date")})
    exposure["CUS-1019"]["collateral"].append(
        {"type": "vehicles", "description": "Five delivery vehicles listed in Schedule A of LN-9001", "value": 310000.0})
    exposure["CUS-1018"]["collateral"].append(
        {"type": "equipment", "description": "Two CNC machines financed by LN-9002", "value": 240000.0})
    exposure["CUS-1013"]["collateral"].append(
        {"type": "property", "description": "Residential property at 5 Thistledown Mews", "value": 330000.0})
    exposure["CUS-1017"]["limits"].append({"type": "overdraft", "limit": 15000.0, "drawn": 11200.0})
    exposure["CUS-1020"]["limits"].append({"type": "overdraft", "limit": 10000.0, "drawn": 0.0})
    exposure["CUS-1023"]["limits"].append({"type": "overdraft", "limit": 25000.0, "drawn": 9400.0})
    exposure["CUS-1002"]["limits"].append({"type": "card credit limit", "limit": 3000.0, "drawn": 410.0})
    for e in exposure.values():
        for lim in e["limits"]:
            lim["utilisation_pct"] = round(100 * lim["drawn"] / lim["limit"], 1)
        e["total_outstanding_loans"] = round(sum(x["outstanding"] for x in e["loans"]), 2)
        e["total_limits"] = round(sum(x["limit"] for x in e["limits"]), 2)
        e["total_drawn_on_limits"] = round(sum(x["drawn"] for x in e["limits"]), 2)
        e["total_collateral_value"] = round(sum(x["value"] for x in e["collateral"]), 2)
    return loans, exposure


def build_cards(customers: dict, accounts: dict, today: date) -> tuple[dict, dict, dict]:
    cards, ctx, disputes = {}, {}, {}
    counter = {"n": 0}

    def add_card(card_id, cid, last4, status="active", expiry=None, issued=None):
        acc = next(a for a in accounts.values() if a["customer_id"] == cid)
        cards[card_id] = {
            "card_id": card_id, "customer_id": cid, "account_id": acc["account_id"],
            "masked_number": f"**** **** **** {last4}", "last4": last4, "network": "Meridia Pay",
            "type": "debit", "status": status, "expiry": expiry or (today + timedelta(days=700)).strftime("%Y-%m"),
            "issued": issued or d_ago(today, 600), "block_reason": "", "replacement_requested": False,
            "contactless_limit": 100.0,
        }

    def add_tx(card_id, ago, amount, merchant, channel, status="posted", hour="12:00", tx_id=None):
        counter["n"] += 1
        tid = tx_id or f"CTX-{card_id[4:]}-{counter['n']:03d}"
        ctx[tid] = {"card_transaction_id": tid, "card_id": card_id, "date": d_ago(today, ago), "time": hour,
                    "amount": float(amount), "currency": "USD", "merchant": merchant, "channel": channel,
                    "status": status, "disputed": False}
        return tid

    add_card("CRD-2001", "CUS-1002", "4821")
    add_card("CRD-2002", "CUS-1003", "7316", expiry=(today + timedelta(days=21)).strftime("%Y-%m"), issued=d_ago(today, 1400))
    add_card("CRD-2003", "CUS-1004", "2059")
    other = [("CUS-1001", "9143"), ("CUS-1005", "3382"), ("CUS-1006", "6670"), ("CUS-1011", "1904"),
             ("CUS-1012", "5527"), ("CUS-1013", "8801"), ("CUS-1014", "4416"), ("CUS-1016", "7039")]
    for i, (cid, l4) in enumerate(other, start=4):
        add_card(f"CRD-{2000 + i}", cid, l4)
    merchants = ["Marlow Reach Grocers", "Copperpot Cafe", "Tallowby Pharmacy", "Lantern Books", "Pennyfarthing Bakery"]
    for cid in cards:
        for k in range(4):
            add_tx(cid, 3 + k * 9 + (int(cid[-1]) % 3), 12 + k * 7.35, merchants[(k + int(cid[-1])) % 5], "chip",
                   hour=f"1{k}:{20 + k}")
    # Lost card: two payments made after the card was lost (lost at about 17:00, 2 days ago)
    add_tx("CRD-2001", 3, 46.20, "Copperpot Cafe", "chip", hour="08:15", tx_id="CTX-2001-A01")
    add_tx("CRD-2001", 2, 31.80, "Marlow Reach Grocers", "chip", hour="12:40", tx_id="CTX-2001-A02")
    add_tx("CRD-2001", 2, 389.00, "Ironwood Electronics Online", "online", hour="19:55", tx_id="CTX-2001-U01")
    add_tx("CRD-2001", 1, 85.40, "Quickfuel Station 44", "contactless", hour="08:10", tx_id="CTX-2001-U02")
    # Open dispute: charged twice
    t1 = add_tx("CRD-2003", 12, 42.00, "Harbourlight Cinema", "chip", hour="18:05", tx_id="CTX-2003-D01")
    t2 = add_tx("CRD-2003", 12, 42.00, "Harbourlight Cinema", "chip", hour="18:06", tx_id="CTX-2003-D02")
    ctx[t2]["disputed"] = True
    disputes["DSP-6001"] = {
        "dispute_id": "DSP-6001", "card_id": "CRD-2003", "customer_id": "CUS-1004",
        "transaction_ids": [t2], "reason": "duplicate_charge", "amount": 42.00, "currency": "USD",
        "status": "open", "opened": d_ago(today, 9), "opened_by": "Contact centre",
        "note": "Charged twice one minute apart for one booking. Waiting for the merchant's reply.",
        "provisional_credit": False,
    }
    return cards, ctx, disputes


def build_screening(customers: dict, today: date) -> tuple[dict, dict]:
    wl = {}

    def entry(eid, category, name, dob=None, yob=None, nat=None, idn="", aliases=(), reason="", related=()):
        wl[eid] = {"entry_id": eid, "list_name": LIST_NAME, "category": category, "name": name,
                   "aliases": list(aliases), "date_of_birth": dob, "year_of_birth": yob,
                   "nationality": nat, "nationality_name": COUNTRIES.get(nat or "", None),
                   "id_number": idn, "listed_on": d_ago(today, 900 + len(wl) * 31),
                   "reason": reason, "related_persons": list(related)}

    entry("WL-9001", "sanctions", "Wynn Castellano", "1962-02-02", 1962, "XB", "BRV-559120",
          reason="Invented example: trade in restricted goods.")
    entry("WL-9002", "sanctions", "Oscar Brindlemore", "1955-05-17", 1955, "XR", "ROV-220871",
          reason="Invented example: fraud against a state fund.")
    entry("WL-9003", "sanctions", "Valdis Orrenmoor", "1971-09-30", 1971, "XQ", "QNP-4417-2290",
          aliases=["V. Orrenmoor"], reason="Invented example: asset freezing order for arms brokering.")
    entry("WL-9004", "sanctions", "Katrin Elsdottir", None, 1969, None, "",
          reason="Invented example: shipping network front company. The record holds a birth year only.")
    entry("WL-9005", "sanctions", "Anselm Drozdovic", "1980-01-09", 1980, "XR", "",
          aliases=["Anselm Drozdovich", "A. Drozdowicz"], reason="Invented example: smuggling network.")
    entry("WL-9006", "pep", "Leopold Vanhollow", "1972-03-03", 1972, "XQ", "QNP-3300-1180",
          reason="Politically exposed person: Minister of Public Works, Quenmark.",
          related=[{"name": "Perdita Vanhollow", "relationship": "spouse"}])
    fillers = [("WL-9007", "sanctions", "Brannoch Ulverstone", "1966-08-09", "QP"),
               ("WL-9008", "sanctions", "Marisol Quennell-Ardt", "1983-12-12", "QN"),
               ("WL-9009", "sanctions", "Torvald Hasselgrave", "1959-01-27", "XA"),
               ("WL-9010", "pep", "Edda Mournbrook", "1968-10-05", "XB"),
               ("WL-9011", "sanctions", "Ignatius Calderwick", "1975-04-21", "QP"),
               ("WL-9012", "sanctions", "Zenobia Larkfield", "1987-07-15", "XT"),
               ("WL-9013", "pep", "Hadrian Pellowes", "1961-06-01", "XR"),
               ("WL-9014", "sanctions", "Odalys Tramontane", "1992-02-28", "QN")]
    for eid, cat, name, dob, nat in fillers:
        entry(eid, cat, name, dob, int(dob[:4]), nat, f"LST-{eid[-4:]}", reason="Invented example entry.")

    alerts = {}

    def alert(aid, cid, eid, score, matched, days, earlier=()):
        alerts[aid] = {"alert_id": aid, "status": "open", "created": d_ago(today, days), "customer_id": cid,
                       "entry_id": eid, "match_score": score, "matched_fields": list(matched),
                       "earlier_alert_ids": list(earlier), "screening_type": "customer onboarding review"
                       if aid.endswith("1") else "periodic rescreen",
                       "recommendations": [], "closure": None}

    # earlier closed alerts on the same pair
    alerts["SCR-1990"] = {"alert_id": "SCR-1990", "status": "closed", "created": d_ago(today, 430),
                          "customer_id": "CUS-1005", "entry_id": "WL-9001", "match_score": 76,
                          "matched_fields": ["name"], "earlier_alert_ids": [], "screening_type": "onboarding",
                          "recommendations": [],
                          "closure": {"disposition": "false_positive", "decided_by": "Analyst R. Teague",
                                      "note": "Different date of birth and nationality.", "closed_at": d_ago(today, 429)}}
    alerts["SCR-1991"] = {"alert_id": "SCR-1991", "status": "closed", "created": d_ago(today, 300),
                          "customer_id": "CUS-1010", "entry_id": "WL-9006", "match_score": 81,
                          "matched_fields": ["surname"], "earlier_alert_ids": [], "screening_type": "periodic rescreen",
                          "recommendations": [],
                          "closure": {"disposition": "true_match", "decided_by": "Analyst R. Teague",
                                      "note": "Relationship confirmed: spouse of a politically exposed person. "
                                              "Enhanced due diligence applied; customer kept.",
                                      "closed_at": d_ago(today, 298)}}
    alert("SCR-2001", "CUS-1005", "WL-9001", 78, ["name (similar)"], 2, ["SCR-1990"])
    alert("SCR-2002", "CUS-1006", "WL-9002", 74, ["name (similar)"], 2)
    alert("SCR-2003", "CUS-1007", "WL-9003", 99, ["name", "date_of_birth", "nationality", "id_number"], 1)
    alert("SCR-2004", "CUS-1008", "WL-9004", 71, ["name (partly)", "year_of_birth"], 3)
    alert("SCR-2005", "CUS-1009", "WL-9005", 88, ["name (variant spelling)", "date_of_birth", "nationality"], 3)
    alert("SCR-2006", "CUS-1010", "WL-9006", 84, ["surname", "related person (spouse)"], 1, ["SCR-1991"])
    return wl, alerts


def build_aml(customers: dict, accounts: dict, tb: TxnBuilder, today: date) -> tuple[dict, dict, dict, dict, dict]:
    rules = {
        "MTB-AML-RULE-001": {"rule_id": "MTB-AML-RULE-001", "name": "Cash deposits just under the reporting threshold",
                             "policy": "MTB-POL-022",
                             "text": "Fires when an account receives three or more cash deposits between USD 9,000 and "
                                     "USD 9,999 within 14 days, or when cash deposits just under the USD 10,000 reporting "
                                     "threshold total USD 30,000 or more in 14 days. Pattern known as structuring."},
        "MTB-AML-RULE-002": {"rule_id": "MTB-AML-RULE-002", "name": "Rapid movement of funds",
                             "policy": "MTB-POL-023",
                             "text": "Fires when a credit of USD 25,000 or more leaves the account again within two "
                                     "business days, with at least 90 percent of the amount, and this happens three "
                                     "times in 30 days."},
        "MTB-AML-RULE-003": {"rule_id": "MTB-AML-RULE-003", "name": "Payments to higher-risk jurisdictions",
                             "policy": "MTB-POL-024",
                             "text": "Fires when payments to counterparties in a country on the bank's higher-risk "
                                     "jurisdiction list total USD 20,000 or more in 30 days. The list now holds "
                                     "Kharnovia (QP)."},
        "MTB-AML-RULE-004": {"rule_id": "MTB-AML-RULE-004", "name": "Unusual number of outgoing payments",
                             "policy": "MTB-POL-025",
                             "text": "Fires when the count of outgoing payments in a calendar month is 1.5 times the "
                                     "three-month average or more. Common causes: payroll growth, one-off campaigns."},
    }
    cp = {}

    def cparty(cid, name, cc, bank, risk, first_seen, note=""):
        cp[cid] = {"counterparty_id": cid, "name": name, "country": cc, "country_name": COUNTRIES[cc],
                   "bank": bank, "risk_rating": risk, "first_seen": d_ago(today, first_seen), "notes": note,
                   "higher_risk_jurisdiction": cc == "QP"}

    cparty("CPY-4001", "Tallowmere Holdings", "XA", "Aldoria Commerce Bank", "medium", 60,
           "Holding company. No public information on its trade.")
    cparty("CPY-4002", "Quillgate Trading", "XB", "Brevnia Savings Union", "medium", 60,
           "Trading company. Receives large transfers from several unrelated senders.")
    cparty("CPY-4005", "Karn Harbour Freight Agency", "QP", "Kharnovia Development Bank", "high", 24,
           "New counterparty. Located in a higher-risk jurisdiction. No contract on file.")
    cparty("CPY-4006", "Greywater Packaging Supply", "XT", "Tessaly Mutual Bank", "low", 400,
           "Long-standing supplier of the bank's customers.")

    def acc(num, idx=1):
        return accounts[f"ACC-{num}-{idx:02d}"]

    alerts = {}

    def alert(aid, cid, account_id, rule, days_from, days_to, txn_ids, summary, score, status="open", closure=None):
        alerts[aid] = {"alert_id": aid, "status": status, "customer_id": cid, "account_id": account_id,
                       "rule_id": rule, "period_start": d_ago(today, days_from), "period_end": d_ago(today, days_to),
                       "created": d_ago(today, max(days_to - 1, 0)), "transaction_ids": txn_ids,
                       "summary": summary, "risk_score": score, "case_id": None, "closure": closure}

    # 3001 structuring
    a = acc(1020)
    for ago, amt in [(70, 1850), (64, 2200), (58, 1400), (52, 3100)]:
        tb.add(a, ago, amt, "credit", "cash_deposit", "Cash", "Cash deposit, till takings")
    ids = []
    for n, (ago, amt) in enumerate([(11, 9400), (10, 9650), (8, 9100), (7, 9800), (5, 9300), (4, 9700), (2, 9500)], 1):
        ids.append(tb.add(a, ago, amt, "credit", "cash_deposit", "Cash", "Cash deposit",
                          txn_id=f"TXN-S3001-{n:02d}"))
    for ago, amt in [(15, 8200), (9, 12100), (3, 11800)]:
        tb.add(a, ago, amt, "debit", "transfer_out", "Alder and Vine Wholesale", "Supplier payment")
    alert("TMA-3001", "CUS-1020", a["account_id"], "MTB-AML-RULE-001", 12, 2, ids,
          "Seven cash deposits between USD 9,100 and USD 9,800 in 10 days, total USD 66,450.", 86)
    # 3002 pass-through
    a = acc(1021)
    ids = []
    for n, (ago, amt, back) in enumerate([(20, 48000, 47400), (12, 52500, 51800), (5, 39000, 38400)], 1):
        ids.append(tb.add(a, ago, amt, "credit", "transfer_in", "Tallowmere Holdings", "Consulting fee",
                          counterparty_id="CPY-4001", country="XA", txn_id=f"TXN-S3002-{n}A"))
        ids.append(tb.add(a, ago - 1, back, "debit", "transfer_out", "Quillgate Trading", "Services",
                          counterparty_id="CPY-4002", country="XB", txn_id=f"TXN-S3002-{n}B"))
    alert("TMA-3002", "CUS-1021", a["account_id"], "MTB-AML-RULE-002", 21, 4, ids,
          "Three credits of USD 39,000 to 52,500 each left the account the next day, keeping about 1.3 percent.", 82)
    # 3003 higher-risk jurisdiction
    a = acc(1022)
    ids = []
    for n, (ago, amt) in enumerate([(24, 14800), (17, 9950), (9, 12300), (3, 16200)], 1):
        ids.append(tb.add(a, ago, amt, "debit", "transfer_out", "Karn Harbour Freight Agency", "Freight and handling",
                          counterparty_id="CPY-4005", country="QP", txn_id=f"TXN-S3003-{n}"))
    tb.add(a, 30, 18400, "debit", "transfer_out", "Greywater Packaging Supply", "Packaging", counterparty_id="CPY-4006",
           country="XT")
    tb.add(a, 8, 17900, "debit", "transfer_out", "Greywater Packaging Supply", "Packaging", counterparty_id="CPY-4006",
           country="XT")
    alert("TMA-3003", "CUS-1022", a["account_id"], "MTB-AML-RULE-003", 30, 3, ids,
          "Four payments to one new counterparty in Kharnovia, total USD 53,250 in 24 days.", 74)
    # 3004 benign payroll spike
    a = acc(1023)
    staff = [f"Employee {chr(65 + i)}" for i in range(22)]
    seasonal = [f"Seasonal {chr(65 + i)}" for i in range(19)]
    for ago in (60, 30):
        for i, nm in enumerate(staff):
            tb.add(a, ago, 1850 + (i % 6) * 120, "debit", "payroll", nm, "Payroll")
    ids = []
    for i, nm in enumerate(staff):
        ids.append(tb.add(a, 2, 1850 + (i % 6) * 120, "debit", "payroll", nm, "Payroll",
                          txn_id=f"TXN-S3004-{i + 1:02d}"))
    for i, nm in enumerate(seasonal):
        ids.append(tb.add(a, 2, 1500 + (i % 4) * 90, "debit", "payroll", nm, "Seasonal payroll",
                          txn_id=f"TXN-S3004-{23 + i:02d}"))
    tb.add(a, 3, 98000, "credit", "transfer_in", "Foxfield Hospitality", "Festival catering contract, advance")
    alert("TMA-3004", "CUS-1023", a["account_id"], "MTB-AML-RULE-004", 7, 1, ids,
          "41 outgoing payroll payments this month against an average of 22.", 52)
    # older closed alerts for history
    alert("TMA-2901", "CUS-1020", acc(1020)["account_id"], "MTB-AML-RULE-001", 215, 205, [],
          "Two deposits just under the threshold.", 55, "closed",
          {"disposition": "no_further_action", "decided_by": "Analyst M. Okonjo-Vale", "note": "Single event, explained by a market day.", "closed_at": d_ago(today, 204)})
    alert("TMA-2902", "CUS-1023", acc(1023)["account_id"], "MTB-AML-RULE-004", 130, 120, [],
          "Payment count above average.", 50, "closed",
          {"disposition": "no_further_action", "decided_by": "Analyst M. Okonjo-Vale", "note": "Summer event staff.", "closed_at": d_ago(today, 119)})
    cases = {
        "CASE-4001": {"case_id": "CASE-4001", "customer_id": "CUS-1013", "alert_ids": [], "status": "closed",
                      "priority": "low", "summary": "Old review of a large property deposit. Explained by a house sale.",
                      "opened": d_ago(today, 260), "opened_by": "Analyst M. Okonjo-Vale", "narratives": [],
                      "closure_note": "Closed. No further action."},
    }
    return rules, cp, alerts, cases, {}
