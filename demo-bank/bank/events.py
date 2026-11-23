"""Events: simulate new items and tell subscribers with a plain-language message."""

from __future__ import annotations

import json
import threading
import urllib.error
import urllib.request

from .ibanutil import make_iban
from .seed_base import BANK_BY_CODE, d_ago
from .seed_lend import installment
from .seed_pay import _bene
from .store import Store, now_iso

KINDS = ["screening-alert", "payment-repair", "payment-investigation", "loan-application"]
SYSTEM_OF = {"screening-alert": "screening", "payment-repair": "payments", "payment-investigation": "payments",
             "loan-application": "lending"}
TIMEOUT = 10


# ----------------------------------------------------------------- sending

def _post(store: Store, sub: dict, payload: dict, event_id: str) -> None:
    started = now_iso()
    outcome = {"event_id": event_id, "subscription_id": sub["subscription_id"], "url": sub["url"],
               "sent_at": started, "status": "failed", "http_status": None, "error": ""}
    try:
        headers = {"Content-Type": "application/json"}
        if sub.get("header_name"):
            headers[sub["header_name"]] = sub.get("secret_value", "")
        req = urllib.request.Request(sub["url"], data=json.dumps(payload).encode(), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            outcome["http_status"] = resp.status
            outcome["status"] = "delivered" if 200 <= resp.status < 300 else "failed"
    except urllib.error.HTTPError as exc:
        outcome["http_status"] = exc.code
        outcome["error"] = f"HTTP {exc.code}"
    except Exception as exc:  # never fails the caller
        outcome["error"] = f"{type(exc).__name__}: {exc}"
    with store.lock:
        store.events.append(outcome)


def dispatch(store: Store, kind: str, item_id: str, message: str, wait: bool = False) -> list[dict]:
    """Send to every matching subscription in the background. Returns what was queued."""
    event_id = f"EVT-{store.next_number('event', 1):04d}"
    payload = {"message": message, "event_type": kind, "item_id": item_id, "system": SYSTEM_OF[kind], "demo_data": True}
    queued, threads = [], []
    with store.lock:
        subs = [s for s in store.subscriptions if s["event_kind"] in ("*", kind)]
        store.events.append({"event_id": event_id, "subscription_id": None, "url": None, "sent_at": now_iso(),
                             "status": "created", "http_status": None, "error": "", "event_type": kind,
                             "item_id": item_id, "subscribers": len(subs)})
    for s in subs:
        t = threading.Thread(target=_post, args=(store, s, payload, event_id), daemon=True)
        t.start()
        threads.append(t)
        queued.append({"subscription_id": s["subscription_id"], "status": "queued"})
    if wait:
        for t in threads:
            t.join(TIMEOUT + 2)
    return queued


# ----------------------------------------------------------------- simulate

def _screening(store: Store, n: int) -> tuple[str, str]:
    d, today = store.data, store.settings.bank_today
    templates = [
        ("CUS-1001", dict(name="Ilvana Marrowitz", dob="1957-06-06", nat="XA", idn="ALD-770112", category="sanctions"), 77),
        ("CUS-1011", dict(name="Tobias Wrenfeld", dob=None, nat=None, idn="", category="sanctions"), 83),
        ("CUS-1013", dict(name="Cassius Dunmoor", dob="1965-09-04", nat="XM", idn="", category="pep"), 90),
        ("CUS-1016", dict(name="Isolda Pennywhistle-Rae", dob="1999-11-22", nat="XM", idn=d["customers"]["CUS-1016"]["id_number"],
                          category="sanctions"), 97),
    ]
    cid, e, score = templates[n % 4]
    eid = f"WL-{9500 + store.next_number('sim_wl', 1)}"
    d["watchlist"][eid] = {"entry_id": eid, "list_name": "Meridia Consolidated Demonstration List (invented)",
                           "category": e["category"], "name": e["name"], "aliases": [], "date_of_birth": e["dob"],
                           "year_of_birth": int(e["dob"][:4]) if e["dob"] else None, "nationality": e["nat"],
                           "nationality_name": None, "id_number": e["idn"], "listed_on": d_ago(today, 20),
                           "reason": "Invented example entry.", "related_persons": []}
    aid = f"SCR-{2100 + store.next_number('sim_scr', 1)}"
    d["screening_alerts"][aid] = {"alert_id": aid, "status": "open", "created": today.isoformat(), "customer_id": cid,
                                  "entry_id": eid, "match_score": score, "matched_fields": ["name (similar)"],
                                  "earlier_alert_ids": [], "screening_type": "periodic rescreen",
                                  "recommendations": [], "closure": None}
    name = d["customers"][cid]["name"]
    return aid, (f"A new screening alert {aid} has arrived in the screening system. It compares customer {cid} ({name}) "
                 f"with list entry {eid} ({e['name']}) and has a match score of {score}. It is open and needs a recommendation. "
                 f"Read it with get_screening_alert in the screening system.")


def _new_payment(store: Store, num: int, amount: float, bene: dict, status: str, bearer="SHA", purpose="", reference="",
                 messages=None, timeline=None) -> dict:
    d, today = store.data, store.settings.bank_today
    pid = f"PAY-{6300 + store.next_number('sim_pay', 1)}"
    acc = d["accounts"][f"ACC-{num}-01"]
    d["payments"][pid] = {"payment_id": pid, "customer_id": f"CUS-{num}", "debit_account_id": acc["account_id"],
                          "amount": amount, "currency": "USD", "created": today.isoformat(), "status": status,
                          "beneficiary": bene, "charges_bearer": bearer, "purpose_code": purpose, "reference": reference,
                          "narrative": reference, "corridor": f"XM->{bene['country']}",
                          "timeline": timeline or [{"date": today.isoformat(), "status": "submitted", "note": "Submitted."}],
                          "messages": [], "recall": None, "repair_id": None}
    p = d["payments"][pid]
    for i, (mtype, direction, summary, key) in enumerate(messages or [], start=1):
        p["messages"].append({"message_id": f"MSG-{pid[4:]}-{i}", "type": mtype, "direction": direction,
                              "date": today.isoformat(), "summary": summary, "key_fields": key})
    return p


def _repair(store: Store, n: int) -> tuple[str, str]:
    d, today = store.data, store.settings.bank_today
    kind = n % 4
    if kind == 0:
        good = make_iban("XT", "TESL", "61000330001118")
        b = _bene("Ambrel Tile Merchants", "TESL", "61000330001118", "Kiln Row 5", "Ambrel, Tessaly", "XT")
        b["iban"] = good[:-1] + str((int(good[-1]) + 1) % 10)
        rule, code, why, fields = "MTB-PAY-RULE-101", "AC01", "The beneficiary IBAN fails the check-digit test.", {"beneficiary_iban": b["iban"]}
    elif kind == 1:
        b = _bene("Duskmere Timber Yard", "ROVA", "30770440002290", "Saw Lane 9", "Duskmere, Rovaland", "XR")
        b["bic"] = "ALDBXAA1"
        rule, code, why, fields = "MTB-PAY-RULE-102", "RC01", "The BIC does not match the bank named in the payment.", {"beneficiary_bic": "ALDBXAA1"}
    elif kind == 2:
        b = _bene("Brevnia Cable Supply", "BRVN", "40550770003345", "", "", "XB", address=False)
        rule, code, why, fields = "MTB-PAY-RULE-103", "BE04", "Cross-border payment with no beneficiary address.", {"beneficiary_address": "(missing)"}
    else:
        b = _bene("Rovaland Lab Equipment", "ROVA", "30770550004471", "Test Street 2", "Duskmere, Rovaland", "XR")
        rule, code, why, fields = "MTB-PAY-RULE-104", None, "No purpose code for the Meridia to Rovaland corridor.", {"purpose_code": "(missing)"}
    num = [1011, 1013, 1018, 1024][kind]
    p = _new_payment(store, num, 2100.0 + 350 * kind, b, "held", reference=f"Invoice SIM-{kind + 1}",
                     messages=[("pacs.008", "outbound (held)", "Customer credit transfer, not yet sent.",
                                {"beneficiary_name": b["name"], **fields})],
                     timeline=[{"date": today.isoformat(), "status": "submitted", "note": "Customer submitted the payment."},
                               {"date": today.isoformat(), "status": "held", "note": f"Held: {why}"}])
    rid = f"REP-{7100 + store.next_number('sim_rep', 1)}"
    p["repair_id"] = rid
    m = p["messages"][0]
    d["repairs"][rid] = {"repair_id": rid, "payment_id": p["payment_id"], "status": "held", "held_since": today.isoformat(),
                         "held_message": {"type": m["type"], "summary": m["summary"], "key_fields": m["key_fields"]},
                         "stop_reason": why, "rule_id": rule, "iso_reason_code": code, "proposals": [], "release": None}
    return rid, (f"A payment of USD {p['amount']:.2f} ({p['payment_id']}) from customer {p['customer_id']} was held and is now "
                 f"repair item {rid} in the payments system. It stopped because: {why} The bank rule is {rule}. "
                 f"Read it with get_repair_item and propose a correction.")


def _investigation(store: Store, n: int) -> tuple[str, str]:
    d, today = store.data, store.settings.bank_today
    kind = n % 4
    bene = _bene("Velmora Garden Centre", "ALDB", "55210440005512", "Market Street 3", "Velmora, Aldoria", "XA")
    specs = [
        ("beneficiary_not_received", "SHA", "The customer says the beneficiary has not received the payment.",
         [("pacs.008", "outbound", "Customer credit transfer sent.", {}),
          ("pacs.002", "inbound", "Settlement completed.", {"status": "ACSC"})]),
        ("amount_short", "OUR", "The beneficiary says the amount received was lower than the amount sent.",
         [("pacs.008", "outbound", "Sent with charges OUR.", {"charges": "OUR"}),
          ("pacs.008", "inbound", "Intermediary onward message with a deducted charge.", {"deducted_charge": "25.00 USD"})]),
        ("payment_returned", "SHA", "The customer sees the money back and asks why.",
         [("pacs.008", "outbound", "Customer credit transfer sent.", {}),
          ("pacs.004", "inbound", "Payment return. The account number is closed.", {"return_reason": "AC04"})]),
        ("payment_returned", "SHA", "The customer sees the money back and asks why.",
         [("pacs.008", "outbound", "Customer credit transfer sent.", {}),
          ("pacs.004", "inbound", "Payment return. The account number is incorrect.", {"return_reason": "AC01"})]),
    ]
    typ, bearer, claim, msgs = specs[kind]
    num = [1014, 1018, 1006, 1016][kind]
    p = _new_payment(store, num, 1500.0 + 200 * kind, bene, "returned" if typ == "payment_returned" else "credited",
                     bearer=bearer, reference=f"Invoice SIM-I{kind + 1}", messages=msgs)
    iid = f"INV-{5100 + store.next_number('sim_inv', 1)}"
    d["investigations"][iid] = {"investigation_id": iid, "payment_id": p["payment_id"], "customer_id": p["customer_id"],
                                "status": "open", "type": typ, "raised": today.isoformat(), "raised_by": "Contact centre",
                                "claim": claim, "reply_drafts": []}
    return iid, (f"A new payment investigation {iid} has arrived in the payments system for payment {p['payment_id']} "
                 f"(customer {p['customer_id']}). Claim: {claim} Read it with get_payment_investigation and draft a reply.")


def _application(store: Store, n: int) -> tuple[str, str]:
    d, today = store.data, store.settings.bank_today
    kind = n % 4
    aid = f"LAP-{8100 + store.next_number('sim_lap', 1)}"
    specs = [
        (1014, "personal_loan", 9000.0, 24, 9.5, "Car purchase", ["identity_document", "payslips_3_months",
                                                                "bank_statements_3_months", "employment_letter"]),
        (1024, "business_loan_small", 40000.0, 36, 10.5, "New dental scanner", ["company_registration", "financial_statements"]),
        (1016, "personal_loan", 5000.0, 18, 9.5, "Laptop and desk", ["identity_document", "payslips_3_months",
                                                                    "bank_statements_3_months"]),
        (1017, "business_loan_small", 25000.0, 24, 10.5, "Cold-room repairs", ["company_registration", "financial_statements",
                                                                              "bank_statements_6_months", "tax_return",
                                                                              "ownership_declaration", "directors_identity"]),
    ]
    num, product, amount, term, apr, purpose, have = specs[kind]
    cust = d["customers"][f"CUS-{num}"]
    app = {"application_id": aid, "status": "received", "customer_id": cust["customer_id"], "applicant": cust["name"],
           "product": product, "amount": amount, "currency": "USD", "term_months": term, "indicative_apr_pct": apr,
           "purpose": purpose, "received": today.isoformat(),
           "form_fields": {"note": "Simulated application."}, "missing_items_drafts": [], "credit_memo_drafts": []}
    if product == "personal_loan":
        app["indicative_monthly_installment"] = installment(amount, apr, term)
    d["applications"][aid] = app
    d["application_docs"][aid] = {}
    for i, t in enumerate(have, start=1):
        did = f"DOC-{aid[4:]}{i:02d}"
        d["application_docs"][aid][did] = {"document_id": did, "application_id": aid, "doc_type": t, "title": t.replace("_", " ").title(),
                                           "received": today.isoformat(), "format": "extracted text",
                                           "text": f"Simulated {t.replace('_', ' ')} for {cust['name']}. Summary page only."}
    return aid, (f"A new loan application {aid} has arrived in the lending system from {cust['name']} ({cust['customer_id']}): "
                 f"a {product.replace('_', ' ')} of USD {amount:,.0f} for {purpose.lower()}. Read it with get_loan_application, "
                 f"check which required documents are missing and draft the missing items.")


MAKERS = {"screening-alert": _screening, "payment-repair": _repair, "payment-investigation": _investigation,
          "loan-application": _application}


def simulate(store: Store, kind: str, wait: bool = False) -> dict:
    with store.lock:
        n = store.simulated.get(kind, 0)
        store.simulated[kind] = n + 1
        item_id, message = MAKERS[kind](store, n)
        store.save()
    queued = dispatch(store, kind, item_id, message, wait=wait)
    return {"event_type": kind, "item_id": item_id, "system": SYSTEM_OF[kind], "message": message, "deliveries": queued}
