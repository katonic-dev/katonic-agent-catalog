"""Seed data, part 3: payments, investigations, repairs, rules."""

from __future__ import annotations

import random
from datetime import date

from .ibanutil import make_iban
from .seed_base import BANK_BY_CODE, TxnBuilder, d_ago

PURPOSE_CODES = {
    "GDDS": "Purchase or sale of goods",
    "SCVE": "Purchase or sale of services",
    "SUPP": "Payment to a supplier",
    "SALA": "Salary payment",
    "TRAD": "Trade settlement",
    "INTC": "Intra-company payment",
}

RULES = {
    "MTB-PAY-RULE-101": {
        "rule_id": "MTB-PAY-RULE-101", "title": "IBAN must pass the check-digit test",
        "text": "A payment whose beneficiary IBAN fails the mod-97 check must not be sent. It is held for repair. "
                "The IBAN may be corrected only from a verified earlier payment to the same beneficiary (same name "
                "and same bank), or from a written confirmation by the customer. A guessed correction is not allowed.",
        "reason_code": "AC01", "reason_text": "Incorrect account number"},
    "MTB-PAY-RULE-102": {
        "rule_id": "MTB-PAY-RULE-102", "title": "BIC must match the beneficiary bank",
        "text": "The BIC in the payment must belong to the beneficiary bank named in the payment and must agree with the "
                "bank code inside the beneficiary IBAN. A mismatch is held for repair. The correct BIC is taken from "
                "the bank directory (see lookup_bank).",
        "reason_code": "RC01", "reason_text": "Bank identifier incorrect"},
    "MTB-PAY-RULE-103": {
        "rule_id": "MTB-PAY-RULE-103", "title": "Cross-border payments need the beneficiary address",
        "text": "Every payment to another country must carry the beneficiary's name and postal address (at least town "
                "and country). A payment without it is held. The address may be taken from a verified earlier payment "
                "to the same beneficiary.",
        "reason_code": "BE04", "reason_text": "Missing creditor address"},
    "MTB-PAY-RULE-104": {
        "rule_id": "MTB-PAY-RULE-104", "title": "Purpose code for the Meridia to Rovaland corridor",
        "text": "Payments from Meridia to Rovaland must carry a valid purpose code from this list: "
                "GDDS (goods), SCVE (services), SUPP (supplier payment), SALA (salary), TRAD (trade settlement), "
                "INTC (intra-company). A missing or other code holds the payment. Choose the code from the invoice "
                "or contract reference, and record what it was based on.",
        "reason_code": None, "reason_text": ""},
    "MTB-PAY-RULE-105": {
        "rule_id": "MTB-PAY-RULE-105", "title": "Charges instructed as OUR",
        "text": "When a payment is sent with charges OUR, the sender pays all charges and the beneficiary must receive "
                "the full amount. If an intermediary bank deducts a charge anyway, the bank claims it back from that "
                "bank and tells the customer the shortfall is being recovered.",
        "reason_code": None, "reason_text": ""},
    "MTB-PAY-RULE-106": {
        "rule_id": "MTB-PAY-RULE-106", "title": "Returned payments",
        "text": "When a payment comes back, the full returned amount is credited to the sender's account and the "
                "customer is told the reason. A new payment needs corrected beneficiary details from the customer.",
        "reason_code": "AC04", "reason_text": "Closed account number"},
}


# Why a rule applies to an investigation, by rule id. Investigations of a kind with no rule carry an empty list and say so.
RULE_NOTES = {
    "MTB-PAY-RULE-105": "The payment was sent with charges OUR, so a deduction by an intermediary bank is not allowed (charges rule).",
    "MTB-PAY-RULE-106": "The payment came back, so the returned amount is credited to the sender and a new payment needs "
                        "corrected details (returned payments rule).",
}
NO_RULE_NOTE = "No bank rule applies. The payment was correct and was credited late, not lost."


def _bene(name, bank_code, bban, street, town, country, address=True):
    bank = BANK_BY_CODE[bank_code]
    return {"name": name, "iban": make_iban(country, bank_code, bban), "bic": bank[3], "bank_name": bank[1],
            "address": f"{street}, {town}" if address else "", "country": country}


def build_payments(customers: dict, accounts: dict, tb: TxnBuilder, rng: random.Random, today: date):
    payments, investigations, repairs = {}, {}, {}

    def acct(num):
        return accounts[f"ACC-{num}-01"]

    def pay(pid, num, amount, ccy, days, bene, status, timeline, messages, bearer="SHA", purpose="",
            reference="", narrative="", corridor_to=None):
        a = acct(num)
        payments[pid] = {
            "payment_id": pid, "customer_id": f"CUS-{num}", "debit_account_id": a["account_id"],
            "amount": float(amount), "currency": ccy, "created": d_ago(today, days), "status": status,
            "beneficiary": bene, "charges_bearer": bearer, "purpose_code": purpose, "reference": reference,
            "narrative": narrative, "corridor": f"XM->{bene['country']}", "timeline": timeline, "messages": messages,
            "recall": None, "repair_id": None}
        if status != "held":
            tb.add(a, days, amount, "debit", "transfer_out", bene["name"], f"Payment {pid} {reference}".strip(),
                   txn_id=f"TXN-{pid}")
        return payments[pid]

    def tl(*items):
        return [{"date": d_ago(today, ago), "status": st, "note": note} for ago, st, note in items]

    def msg(pid, n, mtype, direction, ago, summary, **key):
        return {"message_id": f"MSG-{pid[4:]}-{n}", "type": mtype, "direction": direction,
                "date": d_ago(today, ago), "summary": summary, "key_fields": key}

    # ---- INV-5001: beneficiary says it never arrived, credited late
    b = _bene("Gideon Faircloth", "TESL", "61000220004417", "Willow Mews 4", "Ambrel, Tessaly", "XT")
    pay("PAY-6001", 1014, 1850.00, "USD", 6, b, "credited",
        tl((6, "submitted", "Customer submitted the payment."), (6, "sent", "Sent to the correspondent bank."),
           (5, "in_transit", "Held at the correspondent bank over the weekend; next processing day is 3 days after sending."),
           (3, "credited", "Beneficiary bank credited the account.")),
        [msg("PAY-6001", 1, "pacs.008", "outbound", 6, "Customer credit transfer sent.", amount="1850.00 USD",
             charges="SHA", end_to_end="E2E-6001"),
         msg("PAY-6001", 2, "pacs.002", "inbound", 3, "Status report: settlement completed, credited to the beneficiary.",
             status="ACSC", credited_on=d_ago(today, 3))],
        reference="Deposit for rented flat", narrative="Rent deposit")
    investigations["INV-5001"] = {
        "investigation_id": "INV-5001", "payment_id": "PAY-6001", "customer_id": "CUS-1014", "status": "open",
        "type": "beneficiary_not_received", "raised": d_ago(today, 4), "raised_by": "Contact centre",
        "claim": "The customer says her friend has not received the USD 1,850 sent 6 days ago and asks where it is.",
        "rule_ids": [], "rule_note": NO_RULE_NOTE,
        "reply_drafts": []}
    # ---- INV-5002: arrived short, intermediary deducted charges (instructed OUR)
    b = _bene("Corrowick Alloy Works", "BRVN", "40550990001207", "Foundry Lane 31", "Corrowick, Brevnia", "XB")
    pay("PAY-6002", 1018, 25000.00, "USD", 8, b, "credited",
        tl((8, "submitted", "Customer submitted the payment with charges OUR."), (8, "sent", "Sent."),
           (7, "in_transit", "Passed through an intermediary bank."), (6, "credited", "Credited USD 24,962.50.")),
        [msg("PAY-6002", 1, "pacs.008", "outbound", 8, "Customer credit transfer sent, charges OUR.",
             amount="25000.00 USD", charges="OUR", end_to_end="E2E-6002"),
         msg("PAY-6002", 2, "pacs.008", "inbound", 7,
             "Onward message from the intermediary bank. It deducted a charge of USD 37.50.",
             instructed_amount="25000.00 USD", settled_amount="24962.50 USD", deducted_charge="37.50 USD",
             charges="OUR"),
         msg("PAY-6002", 3, "pacs.002", "inbound", 6, "Status report: settlement completed.", status="ACSC")],
        bearer="OUR", reference="Invoice A-2291 alloy bars", narrative="Alloy bars")
    investigations["INV-5002"] = {
        "investigation_id": "INV-5002", "payment_id": "PAY-6002", "customer_id": "CUS-1018", "status": "open",
        "type": "amount_short", "raised": d_ago(today, 5), "raised_by": "Business banking",
        "claim": "The supplier says USD 24,962.50 arrived, not USD 25,000. The customer asks why it is short.",
        "rule_ids": ["MTB-PAY-RULE-105"], "rule_note": RULE_NOTES["MTB-PAY-RULE-105"],
        "reply_drafts": []}
    # ---- INV-5003: returned, account closed (AC04)
    b = _bene("Hartsfell Rentals", "QNMK", "88100340007725", "Quay Street 12", "Hartsfell, Quenmark", "XQ")
    pay("PAY-6003", 1006, 3200.00, "USD", 5, b, "returned",
        tl((5, "submitted", "Customer submitted the payment."), (5, "sent", "Sent."),
           (3, "returned", "Beneficiary bank returned the payment: account closed."),
           (2, "credited_back", "USD 3,200.00 credited back to the sender's account.")),
        [msg("PAY-6003", 1, "pacs.008", "outbound", 5, "Customer credit transfer sent.", amount="3200.00 USD",
             end_to_end="E2E-6003"),
         msg("PAY-6003", 2, "pacs.004", "inbound", 3, "Payment return. Reason: the account number is closed.",
             return_reason="AC04", returned_amount="3200.00 USD")],
        reference="Deposit, garage unit", narrative="Garage rental deposit")
    tb.add(acct(1006), 2, 3200.00, "credit", "transfer_in", "Hartsfell Rentals", "Returned payment PAY-6003",
           txn_id="TXN-PAY-6003-RET")
    investigations["INV-5003"] = {
        "investigation_id": "INV-5003", "payment_id": "PAY-6003", "customer_id": "CUS-1006", "status": "open",
        "type": "payment_returned", "raised": d_ago(today, 2), "raised_by": "Contact centre",
        "claim": "The customer sees a credit of USD 3,200 and asks why his payment came back.",
        "rule_ids": ["MTB-PAY-RULE-106"], "rule_note": RULE_NOTES["MTB-PAY-RULE-106"],
        "reply_drafts": []}

    # ---- earlier payments to the same beneficiaries (sources for repairs)
    good_iban_b = _bene("Alder Wharf Marine Supplies", "BRVN", "73201150000142", "Wharf Road 8", "Corrowick, Brevnia", "XB")
    pay("PAY-6050", 1011, 2750.00, "USD", 50, good_iban_b, "credited",
        tl((50, "submitted", "Submitted."), (50, "sent", "Sent."), (48, "credited", "Credited.")),
        [msg("PAY-6050", 1, "pacs.008", "outbound", 50, "Customer credit transfer sent.", amount="2750.00 USD"),
         msg("PAY-6050", 2, "pacs.002", "inbound", 48, "Settlement completed.", status="ACSC")],
        reference="Invoice AW-5521 rope and fenders", narrative="Marine supplies")
    pay("PAY-6051", 1018, 9400.00, "USD", 75, _bene("Aldoria Steel Merchants", "ALDB", "55210030008816",
                                                    "Smelter Row 12", "Velmora, Aldoria", "XA"), "credited",
        tl((75, "submitted", "Submitted."), (75, "sent", "Sent."), (73, "credited", "Credited.")),
        [msg("PAY-6051", 1, "pacs.008", "outbound", 75, "Customer credit transfer sent.", amount="9400.00 USD"),
         msg("PAY-6051", 2, "pacs.002", "inbound", 73, "Settlement completed.", status="ACSC")],
        reference="Invoice AS-0912 steel plate", narrative="Steel plate")

    # ---- REP-7001: transposed digits in the IBAN
    wrong = dict(good_iban_b)
    wrong["iban"] = make_iban("XB", "BRVN", "73201150000142")[:-2] + "24"
    # swap the last two digits of the account number: ...42 -> ...24 gives a wrong check digit
    p = pay("PAY-6101", 1011, 4200.00, "USD", 1, wrong, "held",
            tl((1, "submitted", "Customer submitted the payment."),
               (1, "held", "Held in the repair queue: the IBAN failed the check-digit test.")),
            [msg("PAY-6101", 1, "pacs.008", "outbound (held)", 1, "Customer credit transfer, not yet sent.",
                 amount="4200.00 USD", beneficiary_iban=wrong["iban"], beneficiary_name=wrong["name"])],
            reference="Invoice AW-5604 anchors", narrative="Anchors")
    repairs["REP-7001"] = _repair("REP-7001", "PAY-6101", today, 1, wrong_msg=p["messages"][0],
                                  reason="The beneficiary IBAN fails the check-digit test (two digits look swapped).",
                                  rule="MTB-PAY-RULE-101", code="AC01")
    p["repair_id"] = "REP-7001"
    # ---- REP-7002: BIC does not match the bank name
    b = _bene("Tessaly Vineyards Co-operative", "TESL", "61000770002203", "Press Lane 3", "Ambrel, Tessaly", "XT")
    b["bic"] = "QNMKXQQ1"
    p = pay("PAY-6102", 1013, 1275.00, "USD", 1, b, "held",
            tl((1, "submitted", "Customer submitted the payment."),
               (1, "held", "Held: the BIC does not match the bank named in the payment.")),
            [msg("PAY-6102", 1, "pacs.008", "outbound (held)", 1, "Customer credit transfer, not yet sent.",
                 amount="1275.00 USD", beneficiary_bic="QNMKXQQ1", beneficiary_bank_name="Tessaly Mutual Bank",
                 beneficiary_iban=b["iban"])],
            reference="Wine order 0331", narrative="Wine order")
    repairs["REP-7002"] = _repair("REP-7002", "PAY-6102", today, 1, wrong_msg=p["messages"][0],
                                  reason="The BIC QNMKXQQ1 belongs to another bank than the bank named in the payment "
                                         "(Tessaly Mutual Bank), and the bank code TESL inside the IBAN agrees with the name.",
                                  rule="MTB-PAY-RULE-102", code="RC01")
    p["repair_id"] = "REP-7002"
    # ---- REP-7003: no beneficiary address on a cross-border payment
    b = _bene("Aldoria Steel Merchants", "ALDB", "55210030008816", "", "", "XA", address=False)
    p = pay("PAY-6103", 1018, 18750.00, "USD", 1, b, "held",
            tl((1, "submitted", "Customer submitted the payment."),
               (1, "held", "Held: cross-border payment without a beneficiary address.")),
            [msg("PAY-6103", 1, "pacs.008", "outbound (held)", 1, "Customer credit transfer, not yet sent.",
                 amount="18750.00 USD", beneficiary_name="Aldoria Steel Merchants", beneficiary_address="(missing)",
                 beneficiary_iban=b["iban"])],
            reference="Invoice AS-1044 steel coil", narrative="Steel coil")
    repairs["REP-7003"] = _repair("REP-7003", "PAY-6103", today, 1, wrong_msg=p["messages"][0],
                                  reason="No postal address for the beneficiary in a payment to Aldoria.",
                                  rule="MTB-PAY-RULE-103", code="BE04")
    p["repair_id"] = "REP-7003"
    # ---- REP-7004: purpose code missing for the Rovaland corridor
    b = _bene("Rovaland Dental Supplies", "ROVA", "30770120009954", "Clinic Row 21", "Duskmere, Rovaland", "XR")
    p = pay("PAY-6104", 1024, 6300.00, "USD", 1, b, "held",
            tl((1, "submitted", "Customer submitted the payment."),
               (1, "held", "Held: no purpose code for the Meridia to Rovaland corridor.")),
            [msg("PAY-6104", 1, "pacs.008", "outbound (held)", 1, "Customer credit transfer, not yet sent.",
                 amount="6300.00 USD", purpose_code="(missing)", remittance="Invoice RD-88412 dental chair spare parts",
                 beneficiary_iban=b["iban"])],
            purpose="", reference="Invoice RD-88412 dental chair spare parts", narrative="Spare parts")
    repairs["REP-7004"] = _repair("REP-7004", "PAY-6104", today, 1, wrong_msg=p["messages"][0],
                                  reason="The payment has no purpose code, which the Rovaland corridor requires.",
                                  rule="MTB-PAY-RULE-104", code=None)
    p["repair_id"] = "REP-7004"

    # ---- background payments
    names = [("Kettlebridge Utilities", "TESL", "XT"), ("Fernhollow Office Supplies", "ALDB", "XA"),
             ("Winterbourne Stationers", "BRVN", "XB"), ("Oakmeadow Maintenance", "QNMK", "XQ")]
    for i, num in enumerate([1001, 1012, 1016, 1013, 1017, 1019, 1020, 1024], start=1):
        nm, bank, cc = names[i % 4]
        bene = _bene(nm, bank, f"{50000000000000 + i * 7919:014d}", f"Row {i}", "Town", cc)
        pid = f"PAY-62{i:02d}"
        pay(pid, num, 400 + i * 130, "USD", 10 + i * 8, bene, "credited",
            tl((10 + i * 8, "submitted", "Submitted."), (10 + i * 8, "sent", "Sent."),
               (8 + i * 8, "credited", "Credited.")),
            [msg(pid, 1, "pacs.008", "outbound", 10 + i * 8, "Customer credit transfer sent."),
             msg(pid, 2, "pacs.002", "inbound", 8 + i * 8, "Settlement completed.", status="ACSC")],
            reference=f"Invoice {1000 + i}", narrative="Payment", purpose="GDDS" if cc == "XR" else "")
    return payments, investigations, repairs


def _repair(rid, pid, today, ago, wrong_msg, reason, rule, code):
    return {"repair_id": rid, "payment_id": pid, "status": "held", "held_since": d_ago(today, ago),
            "held_message": {"type": wrong_msg["type"], "summary": wrong_msg["summary"],
                             "key_fields": wrong_msg["key_fields"]},
            "stop_reason": reason, "rule_id": rule, "iso_reason_code": code, "proposals": [], "release": None}
