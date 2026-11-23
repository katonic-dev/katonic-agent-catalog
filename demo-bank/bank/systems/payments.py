"""Payments: payment search, investigations, repair queue, reference data."""

from __future__ import annotations

from typing import Literal

from fastapi import Path, Query
from pydantic import BaseModel, Field

from .. import ibanutil
from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..store import now_iso

KEY = "payments"
TITLE = "Payments"
LINE = "Payments, investigations, the repair queue, rules and reference data."


class ReplyDraft(BaseModel):
    reply_text: str = Field(..., min_length=1, description="The reply to the customer, in plain sentences.")
    key_findings: list[str] = Field(default_factory=list, description="Facts found, one per item, each with its source message id.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class Correction(BaseModel):
    field: Literal["beneficiary_iban", "beneficiary_bic", "beneficiary_address", "purpose_code"] = Field(
        ..., description="Field to correct.")
    old_value: str = Field("", description="Current value.")
    new_value: str = Field(..., min_length=1, description="Proposed value.")
    rule_relied_on: str = Field(..., description="Bank rule id, for example MTB-PAY-RULE-101.")


class Proposal(BaseModel):
    corrections: list[Correction] = Field(..., min_length=1, description="The proposed corrections.")
    explanation: str = Field(..., min_length=1, description="Why, and where each new value comes from.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class ReleaseBody(BaseModel):
    approved_by: str = Field(..., min_length=1, description="Name of the person who approves the release.")
    note: str = Field("", description="Optional note.")


class RecallBody(BaseModel):
    reason: Literal["duplicate", "fraud", "technical_error", "customer_request"] = Field(..., description="Why the payment is recalled.")
    requested_by: str = Field("agent", description="Who asks for the recall. Free text.")
    note: str = Field("", description="Optional note.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds payments, investigations and held payments waiting for repair.")
    st = ctx.store
    d = lambda: st.data
    pid_p = Path(..., description="Payment id, for example PAY-6001.")
    inv_p = Path(..., description="Investigation id, for example INV-5001.")
    rep_p = Path(..., description="Repair id, for example REP-7001.")

    def pay_or_404(pid):
        p = d()["payments"].get(pid)
        if not p:
            raise not_found("payment", pid, "Use search_payments to find ids.")
        return p

    def inv_or_404(i):
        x = d()["investigations"].get(i)
        if not x:
            raise not_found("investigation", i, "Use list_payment_investigations to find ids.")
        return x

    def rep_or_404(i):
        x = d()["repairs"].get(i)
        if not x:
            raise not_found("repair item", i, "Use list_repair_queue to find ids.")
        return x

    def prow(p):
        b = p["beneficiary"]
        return {"payment_id": p["payment_id"], "customer_id": p["customer_id"], "amount": p["amount"],
                "currency": p["currency"], "created": p["created"], "status": p["status"],
                "beneficiary_name": b["name"], "reference": p["reference"]}

    @reg(app, "get", "/payments", "search_payments", "Search payments",
         "Search payments by reference text, customer, status or earliest date. Each row has payment_id, customer, amount, "
         "currency, created date, status (credited, returned, held, released, recall_requested), beneficiary name and reference.")
    def search_payments(reference: str | None = Query(None, description="Part of the payment reference or narrative."),
                        customer_id: str | None = Query(None, description="Customer id, for example CUS-1011."),
                        status: str | None = Query(None, description="Payment status, for example credited or held."),
                        date_from: str | None = Query(None, description="Earliest created date, YYYY-MM-DD."),
                        limit: int = Query(25, ge=1, le=200, description="Most rows to return.")):
        rows = []
        for p in d()["payments"].values():
            if reference and reference.lower() not in (p["reference"] + " " + p["narrative"]).lower():
                continue
            if customer_id and p["customer_id"] != customer_id:
                continue
            if status and p["status"] != status:
                continue
            if date_from and p["created"] < date_from:
                continue
            rows.append(prow(p))
        rows.sort(key=lambda r: (r["created"], r["payment_id"]), reverse=True)
        return listing(rows[:limit], total_matches=len(rows))

    @reg(app, "get", "/payments/{payment_id}", "get_payment", "Get one payment in full",
         "Read one payment: amount, currency, charges bearer, purpose code, beneficiary (name, IBAN, BIC, bank, address), the "
         "status timeline, and the messages exchanged (type pacs.008, pacs.002, pacs.004, camt.056 or camt.029, each with a "
         "summary and key fields).")
    def get_payment(payment_id: str = pid_p):
        return pay_or_404(payment_id)

    @reg(app, "get", "/investigations", "list_payment_investigations", "List payment investigations",
         "List investigations raised on payments: id, payment, customer, type, status, raised date and the customer's claim.")
    def list_payment_investigations(status: Literal["open", "closed"] | None = Query(None, description="Only investigations with this status.")):
        return listing([{k: x[k] for k in ("investigation_id", "payment_id", "customer_id", "type", "status", "raised", "claim")}
                        for x in d()["investigations"].values() if not status or x["status"] == status])

    @reg(app, "get", "/investigations/{investigation_id}", "get_payment_investigation", "Get one investigation in full",
         "Read one investigation with the customer's claim, the full payment (timeline and messages) and any reply drafts.")
    def get_payment_investigation(investigation_id: str = inv_p):
        x = inv_or_404(investigation_id)
        return {**x, "payment": d()["payments"][x["payment_id"]]}

    @reg(app, "post", "/investigations/{investigation_id}/reply-draft", "save_investigation_reply",
         "Save a reply to the customer (draft)",
         "Save a draft reply for an investigation, with the findings it rests on. This is a draft: stored with who wrote it, a "
         "timestamp and a version number, earlier versions kept. Nothing is sent to the customer.")
    def save_investigation_reply(body: ReplyDraft, investigation_id: str = inv_p):
        x = inv_or_404(investigation_id)
        v = st.add_draft(x, "reply_drafts", {"reply_text": body.reply_text, "key_findings": body.key_findings}, body.drafted_by)
        return {"applied": True, "kind": "draft", "draft": v}

    @reg(app, "get", "/repairs", "list_repair_queue", "List the repair queue",
         "List held payments waiting for repair: repair_id, payment, status (held or released), held date, why it stopped and the rule.")
    def list_repair_queue(status: Literal["held", "released"] | None = Query(None, description="Only items with this status.")):
        return listing([{k: x[k] for k in ("repair_id", "payment_id", "status", "held_since", "stop_reason", "rule_id", "iso_reason_code")}
                        for x in d()["repairs"].values() if not status or x["status"] == status])

    @reg(app, "get", "/repairs/{repair_id}", "get_repair_item", "Get one held payment",
         "Read one repair item: the held message (type, summary, key fields), why it stopped, the bank rule that stopped it with "
         "its text, an ISO 20022 reason code where one applies, the payment, and any proposals.")
    def get_repair_item(repair_id: str = rep_p):
        x = rep_or_404(repair_id)
        return {**x, "rule": d()["payment_rules"][x["rule_id"]], "payment": d()["payments"][x["payment_id"]]}

    @reg(app, "get", "/rules/{rule_id}", "get_payment_rule", "Get a payment rule",
         "Read the text of one payment rule (id like MTB-PAY-RULE-101) so you can cite it.")
    def get_payment_rule(rule_id: str = Path(..., description="Rule id, for example MTB-PAY-RULE-101.")):
        r = d()["payment_rules"].get(rule_id)
        if not r:
            raise not_found("payment rule", rule_id, "Rule ids appear on repair items.")
        return r

    @reg(app, "post", "/repairs/{repair_id}/proposal", "propose_repair", "Save a repair proposal (draft)",
         "Save proposed corrections for a held payment: each with field, old value, new value and the rule relied on, plus an "
         "explanation. This is a draft: stored with who wrote it, a timestamp and a version number, earlier versions kept. The "
         "payment stays held until release_repaired_payment is called.")
    def propose_repair(body: Proposal, repair_id: str = rep_p):
        x = rep_or_404(repair_id)
        if x["status"] != "held":
            raise conflict(f"Repair {repair_id} is already {x['status']}. Nothing was changed.")
        v = st.add_draft(x, "proposals", {"corrections": [c.model_dump() for c in body.corrections],
                                          "explanation": body.explanation}, body.drafted_by)
        return {"applied": True, "kind": "draft", "repair_status": x["status"], "draft": v}

    @reg(app, "post", "/repairs/{repair_id}/release", "release_repaired_payment", "Release a repaired payment (change)",
         "Apply the latest proposal and release the held payment for sending. This is a change and needs the name of the person who "
         "approves. Refused with 409 if there is no proposal yet or the payment is already released.")
    def release_repaired_payment(body: ReleaseBody, repair_id: str = rep_p):
        x = rep_or_404(repair_id)
        with st.lock:
            if x["status"] == "released":
                raise conflict(f"Repair {repair_id} is already released. Nothing was changed.")
            if not x["proposals"]:
                raise conflict(f"Repair {repair_id} has no proposal yet. Save one with propose_repair first. Nothing was changed.")
            p = d()["payments"][x["payment_id"]]
            prop = x["proposals"][-1]
            for c in prop["corrections"]:
                f, v = c["field"], c["new_value"]
                if f == "beneficiary_iban":
                    p["beneficiary"]["iban"] = v
                elif f == "beneficiary_bic":
                    p["beneficiary"]["bic"] = v
                elif f == "beneficiary_address":
                    p["beneficiary"]["address"] = v
                elif f == "purpose_code":
                    p["purpose_code"] = v
            p["status"] = "released"
            p["timeline"].append({"date": ctx.settings.bank_today.isoformat(), "status": "released",
                                  "note": f"Repaired and released, approved by {body.approved_by}."})
            x["status"] = "released"
            x["release"] = {"approved_by": body.approved_by, "note": body.note, "released_at": now_iso(),
                            "proposal_version": prop["version"]}
            st.save()
        return {"applied": True, "kind": "change", "repair_id": repair_id, "status": "released", "payment_status": p["status"],
                "release": x["release"]}

    @reg(app, "post", "/payments/{payment_id}/recall", "request_payment_recall", "Request a recall of a sent payment (change)",
         "Ask for a payment that was already sent to be recalled (message camt.056). This is a change. Refused with 409 if the payment "
         "was never sent (held), was returned, or a recall is already requested.")
    def request_payment_recall(body: RecallBody, payment_id: str = pid_p):
        p = pay_or_404(payment_id)
        with st.lock:
            if p["status"] in ("held", "released"):
                raise conflict(f"Payment {payment_id} has not been sent ({p['status']}). A recall needs a sent payment. Nothing was changed.")
            if p["status"] == "returned":
                raise conflict(f"Payment {payment_id} was already returned. Nothing was changed.")
            if p["recall"]:
                raise conflict(f"A recall for {payment_id} was already requested. Nothing was changed.")
            p["recall"] = {"reason": body.reason, "requested_by": body.requested_by, "note": body.note,
                           "requested_at": now_iso()}
            p["status"] = "recall_requested"
            n = len(p["messages"]) + 1
            p["messages"].append({"message_id": f"MSG-{payment_id[4:]}-{n}", "type": "camt.056", "direction": "outbound",
                                  "date": ctx.settings.bank_today.isoformat(),
                                  "summary": "Request to cancel the payment (recall).", "key_fields": {"reason": body.reason}})
            p["timeline"].append({"date": ctx.settings.bank_today.isoformat(), "status": "recall_requested",
                                  "note": f"Recall requested by {body.requested_by}."})
            st.save()
        return {"applied": True, "kind": "change", "payment_id": payment_id, "status": p["status"], "recall": p["recall"]}

    @reg(app, "get", "/reference/iban/{iban}", "validate_iban", "Validate an IBAN",
         "Check an IBAN: shape (2 letters, 2 digits, 4-letter bank code, 14 digits), the mod-97 check digits, the country, and "
         "whether the bank code is in the bank directory (with its BIC and name). Always answers 200 with valid true or false and reasons.")
    def validate_iban(iban: str = Path(..., description="IBAN to check. Spaces are ignored.")):
        text = iban.replace(" ", "").upper()
        reasons = []
        shaped = bool(ibanutil.IBAN_SHAPE.match(text))
        if not shaped:
            reasons.append("The shape is wrong: expected 2 letters, 2 digits, 4 letters, 14 digits.")
        checks = shaped and ibanutil.is_valid(text)
        if shaped and not checks:
            reasons.append("The check digits fail the mod-97 test. A digit is wrong or two digits are swapped.")
        bank = next((b for b in d()["banks"].values() if shaped and b["bank_code"] == text[4:8]), None)
        if shaped and not bank:
            reasons.append("The bank code is not in the bank directory.")
        elif bank and bank["country"] != text[:2]:
            reasons.append("The bank code belongs to a bank in another country.")
        return {"iban": text, "valid": bool(checks), "well_formed": shaped, "country": text[:2] if shaped else None,
                "bank": bank, "reasons": reasons}

    @reg(app, "get", "/reference/banks", "lookup_bank", "Look up a bank in the directory",
         "Search the bank directory by BIC or by part of the bank name. Each row has bic, bank_code, name, country and city. "
         "Use it to find the right BIC for a bank name.")
    def lookup_bank(bic: str | None = Query(None, description="Full or partial BIC."),
                    name: str | None = Query(None, description="Part of the bank name. Not case sensitive.")):
        rows = [b for b in d()["banks"].values()
                if (not bic or bic.upper() in b["bic"]) and (not name or name.lower() in b["name"].lower())]
        return listing(rows)

    return app
