"""Seed data, part 4: fraud rules, fraud cases and the card payments, payments and contacts they need."""

from __future__ import annotations

from datetime import date

from .seed_base import TxnBuilder, d_ago
from .seed_pay import _bene

RULES = {
    "FRD-RULE-001": {
        "rule_id": "FRD-RULE-001", "title": "Card not present purchases in another country at night",
        "text": "Fires when a card makes two or more online (card not present) purchases in a country other than Meridia "
                "between 23:00 and 05:00 local time within 24 hours, and the card's earlier purchases were made in "
                "Meridia. Check the customer's recent contacts for travel or a call from home before deciding."},
    "FRD-RULE-002": {
        "rule_id": "FRD-RULE-002", "title": "Large first payment to a new payee",
        "text": "Fires when a payment of USD 10,000 or more goes to a payee the customer has never paid before. The payment "
                "is held. A payment the customer has confirmed by phone with the bank (a contact note records the call "
                "and the checks passed) is released. A payment the customer denies is blocked."},
    "FRD-RULE-003": {
        "rule_id": "FRD-RULE-003", "title": "Account takeover pattern",
        "text": "Fires when, within 60 minutes, a new device signs in, a password is reset, a payee is added and a payment "
                "is made to that payee. Treat as a likely account takeover: block online access and recall the payment."},
    "FRD-RULE-004": {
        "rule_id": "FRD-RULE-004", "title": "Customer reports a card charge as fraud",
        "text": "Raised when a customer says a card payment is fraud. Look at the card's earlier payments before "
                "deciding. Repeat payments to the same merchant for the same amount are usually a subscription the "
                "customer forgot. That is a dispute for the cards system, not a fraud case."},
}


def _card_tx(card_txns: dict, tid: str, card_id: str, today: date, ago: int, hour: str, amount: float,
             merchant: str, channel: str, country: str = "XM", card_present: bool | None = None, town: str = "Port Ilvane") -> str:
    card_txns[tid] = {"card_transaction_id": tid, "card_id": card_id, "date": d_ago(today, ago), "time": hour,
                      "amount": float(amount), "currency": "USD", "merchant": merchant, "channel": channel,
                      "status": "posted", "disputed": False, "country": country, "town": town,
                      "card_present": channel != "online" if card_present is None else card_present}
    return tid


def _contact(contacts: dict, n: int, cid: str, channel: str, today: date, ago: int, direction: str, subject: str,
             summary: str, by: str) -> None:
    key = f"CNT-{5200 + n}"
    contacts[key] = {"contact_id": key, "customer_id": cid, "channel": channel, "date": d_ago(today, ago),
                     "direction": direction, "subject": subject, "summary": summary, "recorded_by": by,
                     "drafted_by": by, "version": 1}


def _payment(payments: dict, accounts: dict, tb: TxnBuilder, today: date, pid: str, num: int, amount: float, ago: int,
             bene: dict, status: str, reference: str, timeline: list, ledger: bool = True) -> None:
    acc = accounts[f"ACC-{num}-01"]
    held = status == "held"
    msgs = [{"message_id": f"MSG-{pid[4:]}-1", "type": "pacs.008", "direction": "outbound (held)" if held else "outbound",
             "date": d_ago(today, ago), "summary": "Customer credit transfer, not yet sent." if held
             else "Customer credit transfer sent.", "key_fields": {"amount": f"{amount:.2f} USD"}}]
    payments[pid] = {"payment_id": pid, "customer_id": f"CUS-{num}", "debit_account_id": acc["account_id"],
                     "amount": float(amount), "currency": "USD", "created": d_ago(today, ago), "status": status,
                     "beneficiary": bene, "charges_bearer": "SHA", "purpose_code": "", "reference": reference,
                     "narrative": reference, "corridor": f"XM->{bene['country']}",
                     "timeline": [{"date": d_ago(today, a), "status": s, "note": n} for a, s, n in timeline],
                     "messages": msgs, "recall": None, "repair_id": None}
    if ledger and not held:
        tb.add(acc, ago, amount, "debit", "transfer_out", bene["name"], f"Payment {pid} {reference}".strip(),
               txn_id=f"TXN-{pid}")


def build_fraud(customers: dict, accounts: dict, cards: dict, card_txns: dict, payments: dict, contacts: dict,
                tb: TxnBuilder, today: date) -> tuple[dict, dict]:
    cases: dict = {}

    def case(cid, rule, opened, source, why, items, amount, card_id="", channel=None, events=None, notes=(),
             status="open", decision=None, priority="medium"):
        num = int(cid.split("-")[1])
        acc = cards[card_id]["account_id"] if card_id else f"ACC-{num}-01"
        cases[cid_of[0]] = {
            "case_id": cid_of[0], "status": status, "customer_id": cid, "card_id": card_id, "account_id": acc,
            "opened": d_ago(today, opened), "source": source, "rule_id": rule, "priority": priority,
            "why_flagged": why, "flagged_items": [{"kind": k, "id": i} for k, i in items],
            "amount_at_risk": float(amount), "currency": "USD", "channel_details": channel or {},
            "security_events": events or [],
            "notes": [{"note_id": f"FN-{cid_of[0][4:]}-{n}", "date": d_ago(today, ago), "author": by, "text": text}
                      for n, (ago, by, text) in enumerate(notes, start=1)],
            "summaries": [], "decision": decision}

    cid_of = [""]

    # ---- FRD-3001: card not present purchases abroad at night, customer was at home
    num, card = 1012, "CRD-2008"
    t1 = _card_tx(card_txns, "CTX-2008-F01", card, today, 2, "02:14", 640.00, "Silverkeld Gadget Mart", "online", "QN", False, "Silverkeld")
    t2 = _card_tx(card_txns, "CTX-2008-F02", card, today, 2, "02:31", 1150.00, "Norvik Duty Free Online", "online", "QN", False, "Norvik")
    t3 = _card_tx(card_txns, "CTX-2008-F03", card, today, 2, "03:05", 429.90, "Kaldmoor Travel Gear", "online", "QN", False, "Kaldmoor")
    _contact(contacts, 1, "CUS-1012", "call", today, 3, "inbound", "Statement date question",
             "Customer phoned at 22:40 from her registered home number to ask when her statement is issued. She said she "
             "was at home for the evening with a cold and not going out.", "Contact centre")
    _contact(contacts, 2, "CUS-1012", "call", today, 2, "inbound", "Text alert about card payments",
             "Customer phoned at 07:15 from her home number. She saw the overnight text alerts for three card payments "
             "abroad and says she did not make them. She has not left Meridia and the card is in her purse.",
             "Contact centre")
    cid_of[0] = "FRD-3001"
    case("CUS-1012", "FRD-RULE-001", 2, "rule",
         "Three online purchases in Norvania between 02:14 and 03:05 local time, total USD 2,219.90. All of the card's "
         "earlier purchases were chip payments in Meridia.",
         [("card_payment", t1), ("card_payment", t2), ("card_payment", t3)], 2219.90, card_id=card,
         channel={"channel": "online card payment", "card_present": False, "merchant_country": "QN", "ip_country": "QN",
                  "device_seen_before": False, "three_d_secure": "not used"},
         notes=[(2, "Fraud monitoring", "Alert raised by FRD-RULE-001. The card was last used in person in Meridia three days ago."),
                (2, "Contact centre", "Customer phoned at 07:15 and says the purchases are not hers. See contact CNT-5202.")],
         priority="high")

    # ---- FRD-3002: large first payment to a new payee, confirmed by the customer by phone
    num = 1015
    bene = _bene("Brookhaven Joinery Works", "TESL", "61000880003361", "Mill Lane 6", "Ambrel, Tessaly", "XT")
    _payment(payments, accounts, tb, today, "PAY-6401", num, 18500.00, 1, bene, "held", "Deposit, kitchen fit-out contract",
             [(1, "submitted", "Customer submitted the payment in online banking."),
              (1, "held", "Held by the fraud check: large first payment to a new payee.")])
    _contact(contacts, 3, "CUS-1015", "call", today, 20, "inbound", "Builder deposit",
             "Customer asked how to pay a builder's deposit by bank transfer. He is having his kitchen refitted and has "
             "a written quote.", "Contact centre")
    _contact(contacts, 4, "CUS-1015", "call", today, 1, "outbound", "Call-back about payment PAY-6401",
             "The fraud team phoned the customer on his registered mobile. He passed the security questions and said he "
             "added the payee himself. Brookhaven Joinery Works is his kitchen builder and USD 18,500 is the 40 percent "
             "deposit on the quote. He read back the payee name and the amount correctly.", "Fraud team")
    cid_of[0] = "FRD-3002"
    case("CUS-1015", "FRD-RULE-002", 1, "rule",
         "Payment of USD 18,500 to Brookhaven Joinery Works in Tessaly. It is the customer's first payment to this payee.",
         [("payment", "PAY-6401")], 18500.00,
         channel={"channel": "online banking (web)", "device_seen_before": True, "ip_country": "XM",
                  "session": "usual device, usual location"},
         notes=[(1, "Fraud monitoring", "Payment held by FRD-RULE-002. Waiting for a decision.")])

    # ---- FRD-3003: account takeover
    num = 1014
    bene = _bene("Marrowfield Remittance Agents", "ALDB", "55210660007120", "Counter 5, Quay Street", "Velmora, Aldoria", "XA")
    _payment(payments, accounts, tb, today, "PAY-6402", num, 7400.00, 1, bene, "credited", "Transfer",
             [(1, "submitted", "Submitted in the mobile app."), (1, "sent", "Sent."), (1, "credited", "Credited.")])
    _contact(contacts, 5, "CUS-1014", "call", today, 60, "inbound", "Mobile app question",
             "Customer said she only uses the app on her own phone. She has never paid anyone outside Meridia.",
             "Contact centre")
    d1 = d_ago(today, 1)
    cid_of[0] = "FRD-3003"
    case("CUS-1014", "FRD-RULE-003", 1, "rule",
         "A new device signed in, the password was reset, a new payee was added and USD 7,400 was paid to that payee, all "
         "within 39 minutes.",
         [("payment", "PAY-6402")], 7400.00,
         channel={"channel": "mobile app", "device_id": "DEV-77A1C", "device_seen_before": False,
                  "device_model": "phone not used before on this profile", "ip_country": "XB",
                  "usual_ip_country": "XM"},
         events=[{"time": f"{d1} 10:02", "event": "new_device_signed_in", "detail": "Sign-in from device DEV-77A1C, never seen on this profile."},
                 {"time": f"{d1} 10:09", "event": "password_reset", "detail": "Password reset with a code sent by text message."},
                 {"time": f"{d1} 10:15", "event": "payee_added", "detail": "New payee added: Marrowfield Remittance Agents, Aldoria."},
                 {"time": f"{d1} 10:41", "event": "payment_made", "detail": "PAY-6402, USD 7,400.00, to the new payee."}],
         notes=[(1, "Contact centre", "Customer phoned at 13:50. She cannot sign in and did not ask for a password reset.")],
         priority="high")

    # ---- FRD-3004: subscription the customer forgot
    card = "CRD-2006"
    for n, ago in enumerate((92, 62, 32), start=1):
        _card_tx(card_txns, f"CTX-2006-S0{n}", card, today, ago, "03:10", 11.99, "Streamline Video Club", "online")
    t4 = _card_tx(card_txns, "CTX-2006-S04", card, today, 2, "03:10", 11.99, "Streamline Video Club", "online")
    _contact(contacts, 6, "CUS-1006", "call", today, 2, "inbound", "Card charge not recognised",
             "Customer says the USD 11.99 charge from Streamline Video Club is fraud and asks for his money back. He says "
             "he never signed up to anything.", "Contact centre")
    cid_of[0] = "FRD-3004"
    case("CUS-1006", "FRD-RULE-004", 2, "customer report",
         "The customer reports one card payment of USD 11.99 to Streamline Video Club as fraud.",
         [("card_payment", t4)], 11.99, card_id=card,
         channel={"channel": "online card payment", "card_present": False, "merchant_country": "XM", "ip_country": "XM",
                  "device_seen_before": True, "three_d_secure": "not used"},
         notes=[(2, "Contact centre", "Customer reported the charge by phone. See contact CNT-5206.")], priority="low")

    # ---- earlier closed cases, for the customer's history
    _card_tx(card_txns, "CTX-2006-H01", card, today, 211, "15:20", 129.00, "Kestrel Sports", "online")
    cid_of[0] = "FRD-2901"
    case("CUS-1006", "FRD-RULE-004", 210, "customer report",
         "The customer reported an online payment of USD 129.00 to Kestrel Sports as fraud.",
         [("card_payment", "CTX-2006-H01")], 129.00, card_id=card, status="decided",
         decision={"decision": "release", "decided_by": "Analyst M. Okonjo-Vale",
                   "note": "His son made the purchase with the card. Not fraud.", "decided_at": d_ago(today, 208),
                   "actions": ["Case closed as not fraud. Nothing was changed."]},
         notes=[(209, "Analyst M. Okonjo-Vale", "Customer's son confirmed the purchase on a call.")], priority="low")
    bene = _bene("Hartsfell Motor Auctions", "QNMK", "88100660002145", "Auction Yard 2", "Hartsfell, Quenmark", "XQ")
    _payment(payments, accounts, tb, today, "PAY-6390", 1015, 12000.00, 300, bene, "credited", "Vehicle purchase",
             [(300, "submitted", "Submitted."), (300, "sent", "Sent."), (298, "credited", "Credited.")], ledger=False)
    cid_of[0] = "FRD-2902"
    case("CUS-1015", "FRD-RULE-002", 300, "rule",
         "Payment of USD 12,000 to Hartsfell Motor Auctions in Quenmark, a new payee.",
         [("payment", "PAY-6390")], 12000.00, status="decided",
         decision={"decision": "release", "decided_by": "Analyst R. Teague",
                   "note": "Customer confirmed the vehicle purchase by phone. Not fraud.", "decided_at": d_ago(today, 299),
                   "actions": ["Payment released."]},
         notes=[(300, "Analyst R. Teague", "Customer confirmed by phone.")], priority="medium")
    return RULES, cases
