"""Fraud: cases raised on card payments and payments, the rules that raise them, and decisions."""

from __future__ import annotations

from typing import Literal

from fastapi import Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..store import now_iso

KEY = "fraud"
TITLE = "Fraud cases"
LINE = "Fraud cases on card payments and payments, the rules that raise them, and decisions."


class SummaryDraft(BaseModel):
    summary: str = Field(..., min_length=1, description="The case summary in plain sentences: what was flagged, the evidence for and against, and the conclusion.")
    recommended_action: Literal["block", "release", "refund"] = Field(..., description="The action you recommend: block, release or refund.")
    customer_message: str = Field("", description="A draft message to the customer, in plain sentences. It is not sent.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class DecisionBody(BaseModel):
    decision: Literal["block", "release", "refund"] = Field(
        ..., description="block: fraud confirmed, stop the card or the payment. release: not fraud. "
                         "refund: fraud confirmed, stop the card or the payment and return the money.")
    decided_by: str = Field(..., min_length=1, description="Name of the person who decides.")
    note: str = Field("", description="Optional note with the reason.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds fraud cases on card payments and payments. Some operations change a card or a payment.")
    st = ctx.store
    d = lambda: st.data
    case_p = Path(..., description="Fraud case id, for example FRD-3001.")

    def case_or_404(cid):
        c = d()["fraud_cases"].get(cid)
        if not c:
            raise not_found("fraud case", cid, "Use list_fraud_cases to find ids.")
        return c

    def item_detail(item):
        if item["kind"] == "card_payment":
            t = d()["card_transactions"][item["id"]]
            card = d()["cards"][t["card_id"]]
            return {"kind": "card_payment", "id": item["id"], "card_id": t["card_id"], "card": card["masked_number"],
                    "date": t["date"], "time": t["time"], "amount": t["amount"], "currency": t["currency"],
                    "merchant": t["merchant"], "channel": t["channel"], "merchant_country": t.get("country", "XM"),
                    "card_present": t.get("card_present", True), "status": t["status"]}
        p = d()["payments"][item["id"]]
        b = p["beneficiary"]
        return {"kind": "payment", "id": item["id"], "date": p["created"], "amount": p["amount"], "currency": p["currency"],
                "beneficiary_name": b["name"], "beneficiary_country": b["country"], "beneficiary_bank": b["bank_name"],
                "reference": p["reference"], "status": p["status"], "debit_account_id": p["debit_account_id"]}

    @reg(app, "get", "/cases", "list_fraud_cases", "List fraud cases",
         "List fraud cases: case_id, customer, status (open or decided), opened date, source (rule or customer report), the "
         "rule that flagged it, the amount at risk and why it was flagged. Use it to find the cases that need a decision.")
    def list_fraud_cases(status: str = Query("", description="Only cases with this status: open or decided. Leave empty for all.")):
        rows = [{k: c[k] for k in ("case_id", "customer_id", "status", "opened", "source", "rule_id", "priority",
                                   "amount_at_risk", "currency", "why_flagged")}
                for c in d()["fraud_cases"].values() if not status or c["status"] == status]
        rows.sort(key=lambda r: (r["opened"], r["case_id"]), reverse=True)
        return listing(rows)

    @reg(app, "get", "/cases/{case_id}", "get_fraud_case", "Get one fraud case in full",
         "Read one fraud case: the flagged card payments or payments (amount, merchant or payee, country, status), the rule "
         "that flagged them and why, device and channel details, security events in time order, the customer's earlier "
         "contacts with the bank (newest first), notes on the case, the customer's earlier fraud cases with their decisions, "
         "and any saved summaries. Look at the card's other payments in the cards system before you decide.")
    def get_fraud_case(case_id: str = case_p):
        c = case_or_404(case_id)
        cust = d()["customers"][c["customer_id"]]
        contacts = sorted((x for x in d()["contacts"].values() if x["customer_id"] == c["customer_id"]),
                          key=lambda x: (x["date"], x["contact_id"]), reverse=True)
        earlier = [{k: x[k] for k in ("case_id", "status", "opened", "rule_id", "why_flagged", "decision")}
                   for x in d()["fraud_cases"].values() if x["customer_id"] == c["customer_id"] and x["case_id"] != case_id]
        return {**c, "flagged_items": [item_detail(i) for i in c["flagged_items"]],
                "customer": {k: cust[k] for k in ("customer_id", "name", "type", "risk_rating")},
                "rule": d()["fraud_rules"][c["rule_id"]], "earlier_contacts": contacts, "earlier_fraud_cases": earlier}

    @reg(app, "get", "/rules/{rule_id}", "get_fraud_rule", "Get a fraud rule",
         "Read the text of one fraud rule (id like FRD-RULE-001) so you can cite it. The rule id is on every fraud case.")
    def get_fraud_rule(rule_id: str = Path(..., description="Rule id, for example FRD-RULE-001.")):
        r = d()["fraud_rules"].get(rule_id)
        if not r:
            raise not_found("fraud rule", rule_id, "Rule ids appear on fraud cases.")
        return r

    @reg(app, "post", "/cases/{case_id}/summary", "save_fraud_case_summary", "Save a case summary (draft)",
         "Save your summary of a fraud case, the action you recommend (block, release or refund) and a draft message to the "
         "customer. This is a draft: stored with who wrote it, a timestamp and a version number, earlier versions kept. "
         "Nothing is sent and the case stays open. Refused with 409 if the case is already decided.")
    def save_fraud_case_summary(body: SummaryDraft, case_id: str = case_p):
        c = case_or_404(case_id)
        if c["status"] != "open":
            raise conflict(f"Case {case_id} is already {c['status']}. Nothing was changed.")
        v = st.add_draft(c, "summaries", {"summary": body.summary, "recommended_action": body.recommended_action,
                                          "customer_message": body.customer_message}, body.drafted_by)
        return {"applied": True, "kind": "draft", "case_status": c["status"], "draft": v}

    @reg(app, "post", "/cases/{case_id}/decision", "decide_fraud_case", "Decide a fraud case (change)",
         "Decide a fraud case: block (fraud confirmed, stop the card, or stop or keep the payment), release (not fraud, release "
         "a held payment) or refund (as block, and also return the money). This is a change and needs the name of the person "
         "who decides. Refused with 409 if the case is already decided.")
    def decide_fraud_case(body: DecisionBody, case_id: str = case_p):
        c = case_or_404(case_id)
        today = ctx.settings.bank_today.isoformat()
        with st.lock:
            if c["status"] != "open":
                raise conflict(f"Case {case_id} is already decided ({c['decision']['decision']}). Nothing was changed.")
            actions = []
            fraud = body.decision in ("block", "refund")
            if c["card_id"] and fraud:
                card = d()["cards"][c["card_id"]]
                if card["status"] != "blocked":
                    card.update(status="blocked", block_reason="fraud", blocked_by=body.decided_by, blocked_at=now_iso(),
                                block_note=f"Fraud case {case_id}")
                    actions.append(f"Card {card['card_id']} blocked.")
            for item in c["flagged_items"]:
                if item["kind"] == "card_payment":
                    t = d()["card_transactions"][item["id"]]
                    if body.decision == "refund":
                        t["status"] = "refunded"
                        t["refund"] = {"amount": t["amount"], "refunded_at": now_iso(), "case_id": case_id}
                        actions.append(f"Card payment {t['card_transaction_id']} refunded: {t['currency']} {t['amount']:.2f}.")
                    continue
                p = d()["payments"][item["id"]]
                if body.decision == "release":
                    if p["status"] == "held":
                        p["status"] = "released"
                        p["timeline"].append({"date": today, "status": "released",
                                              "note": f"Released after fraud review, decided by {body.decided_by}."})
                        actions.append(f"Payment {p['payment_id']} released for sending.")
                elif p["status"] == "held":
                    p["status"] = "cancelled"
                    p["timeline"].append({"date": today, "status": "cancelled",
                                          "note": f"Cancelled after fraud review, decided by {body.decided_by}."})
                    actions.append(f"Held payment {p['payment_id']} cancelled.")
                elif body.decision == "refund" and not p["recall"] and p["status"] in ("credited", "released"):
                    p["recall"] = {"reason": "fraud", "requested_by": body.decided_by, "note": f"Fraud case {case_id}",
                                   "requested_at": now_iso()}
                    p["status"] = "recall_requested"
                    p["messages"].append({"message_id": f"MSG-{p['payment_id'][4:]}-{len(p['messages']) + 1}", "type": "camt.056",
                                          "direction": "outbound", "date": today,
                                          "summary": "Request to cancel the payment (recall).", "key_fields": {"reason": "fraud"}})
                    p["timeline"].append({"date": today, "status": "recall_requested",
                                          "note": f"Recall requested after fraud review, decided by {body.decided_by}."})
                    actions.append(f"Recall requested for payment {p['payment_id']}.")
            if fraud and c["security_events"]:
                d()["customers"][c["customer_id"]]["online_banking"] = "blocked"
                actions.append("Online banking access for the customer blocked.")
            if not actions:
                actions.append("Case closed as not fraud. Nothing was changed on the card or the payments.")
            c["status"] = "decided"
            c["decision"] = {"decision": body.decision, "decided_by": body.decided_by, "note": body.note,
                             "decided_at": now_iso(), "actions": actions}
            st.save()
        return {"applied": True, "kind": "change", "case_id": case_id, "status": c["status"], "decision": c["decision"]}

    return app
