"""Reconciliation: breaks between the bank's ledger and the statements of its correspondent banks."""

from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, conflict, listing, make_subapp, not_found, reg
from ..store import now_iso

KEY = "recon"
TITLE = "Reconciliation"
LINE = "Reconciliation breaks between the ledger and bank statements, the matching rules, proposals and postings."


class ProposalBody(BaseModel):
    resolution: Literal["match", "match_with_adjustment", "reverse_duplicate", "refer_to_person"] = Field(
        ..., description="match: match the break with the named entries. match_with_adjustment: match and post an adjusting "
                         "entry for a small difference. reverse_duplicate: reverse a duplicate ledger entry. "
                         "refer_to_person: nothing can be resolved here, a person must decide.")
    matched_entry_ids: list[str] = Field(default_factory=list, description="Entry ids to match with the break item, for example LED-7101. Needed for match and match_with_adjustment.")
    reverse_entry_id: str = Field("", description="The ledger entry to reverse. Needed for reverse_duplicate.")
    adjusting_debit_account: str = Field("", description="Account to debit in the adjusting entry, for example GL-6120. Needed for match_with_adjustment.")
    adjusting_credit_account: str = Field("", description="Account to credit in the adjusting entry, for example NOS-TESL-01. Needed for match_with_adjustment.")
    adjusting_amount: float = Field(0, ge=0, description="Amount of the adjusting entry in the account currency. Needed for match_with_adjustment.")
    evidence: list[str] = Field(..., min_length=1, description="The facts the proposal rests on, one per item, each with an entry id. For refer_to_person list what was checked.")
    rule_relied_on: str = Field("", description="The matching rule id the proposal relies on, for example RECON-RULE-001.")
    explanation: str = Field("", description="Why, in plain sentences.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


class PostBody(BaseModel):
    approved_by: str = Field(..., min_length=1, description="Name of the person who approves the posting.")
    note: str = Field("", description="Optional note.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds reconciliation breaks, ledger and statement entries and the bank's matching rules.")
    st = ctx.store
    d = lambda: st.data
    brk_p = Path(..., description="Break id, for example BRK-4001.")

    def brk_or_404(bid):
        b = d()["recon_breaks"].get(bid)
        if not b:
            raise not_found("reconciliation break", bid, "Use list_reconciliation_breaks to find ids.")
        return b

    def entry(eid):
        return d()["recon_ledger"].get(eid) or d()["recon_statement"].get(eid)

    def age(b):
        return (ctx.settings.bank_today - date.fromisoformat(b["opened"])).days

    @reg(app, "get", "/breaks", "list_reconciliation_breaks", "List reconciliation breaks",
         "List reconciliation breaks: break_id, account, status (open or resolved), which side the item is on (ledger or "
         "statement), amount, currency, value date, reference and age in days. Filter by status or account.")
    def list_reconciliation_breaks(status: str = Query("", description="Only breaks with this status: open or resolved. Leave empty for all."),
                                   account: str = Query("", description="Only breaks on this reconciliation account, for example NOS-ALDB-01.")):
        rows = []
        for b in d()["recon_breaks"].values():
            if (status and b["status"] != status) or (account and b["account_id"] != account):
                continue
            e = entry(b["entry_id"])
            rows.append({"break_id": b["break_id"], "account_id": b["account_id"], "status": b["status"], "side": b["side"],
                         "entry_id": b["entry_id"], "amount": e["amount"], "currency": e["currency"],
                         "direction": e["direction"], "value_date": e["value_date"], "reference": e["reference"],
                         "age_days": age(b)})
        rows.sort(key=lambda r: (-r["age_days"], r["break_id"]))
        return listing(rows)

    @reg(app, "get", "/breaks/{break_id}", "get_reconciliation_break", "Get one break in full",
         "Read one break: the ledger side and the statement side (the entry, or which side is missing), the amount difference "
         "against the likely candidates, the value dates, the age in days, the candidate matches each with the reason it is a "
         "candidate and whether it is likely, the checks the automatic matcher already ran, the rules that exist, and any "
         "proposals. Use get_reconciliation_rule to read a rule.")
    def get_reconciliation_break(break_id: str = brk_p):
        b = brk_or_404(break_id)
        item = entry(b["entry_id"])
        cands = []
        for c in b["candidates"]:
            e = entry(c["entry_id"])
            cands.append({**c, "entry": e})
        likely = [c for c in cands if c["likely"]]
        diff = round(item["amount"] - sum(c["entry"]["amount"] for c in likely), 2) if likely else None
        sides = {"ledger": [], "statement": []}
        sides[b["side"]] = [item]
        missing = "statement" if b["side"] == "ledger" else "ledger"
        dates = [{"entry_id": item["entry_id"], "side": b["side"], "role": "break item", "value_date": item["value_date"]}]
        dates += [{"entry_id": c["entry_id"], "side": c["side"], "role": "candidate", "value_date": c["entry"]["value_date"]}
                  for c in cands]
        return {"break_id": b["break_id"], "account": d()["recon_accounts"][b["account_id"]], "status": b["status"],
                "opened": b["opened"], "age_days": age(b), "item_side": b["side"], "missing_side": missing,
                "ledger_side": sides["ledger"], "statement_side": sides["statement"],
                "amount_difference": diff, "difference_compared_with": [c["entry_id"] for c in likely],
                "value_dates": dates, "candidates": cands, "auto_match_checks": b["auto_match_checks"],
                "rules": [{"rule_id": r["rule_id"], "title": r["title"]} for r in d()["recon_rules"].values()],
                "proposals": b["proposals"], "resolution": b["resolution"]}

    @reg(app, "get", "/rules/{rule_id}", "get_reconciliation_rule", "Get a reconciliation rule",
         "Read the text of one matching or tolerance rule (id like RECON-RULE-001) so you can cite it. The rule ids are listed "
         "on every break.")
    def get_reconciliation_rule(rule_id: str = Path(..., description="Rule id, for example RECON-RULE-001.")):
        r = d()["recon_rules"].get(rule_id)
        if not r:
            raise not_found("reconciliation rule", rule_id, "Rule ids are listed on every break.")
        return r

    @reg(app, "post", "/breaks/{break_id}/proposal", "propose_break_resolution", "Save a break proposal (draft)",
         "Save a proposed resolution for a break: match with named entries, match with an adjusting entry (accounts and "
         "amount), reverse a duplicate entry, or refer to a person. Give the evidence and the rule relied on. This is a "
         "draft: stored with who wrote it, a timestamp and a version number, earlier versions kept. Nothing is posted until "
         "post_break_resolution is called.")
    def propose_break_resolution(body: ProposalBody, break_id: str = brk_p):
        b = brk_or_404(break_id)
        if b["status"] != "open":
            raise conflict(f"Break {break_id} is already {b['status']}. Nothing was changed.")
        if body.resolution != "refer_to_person" and body.rule_relied_on not in d()["recon_rules"]:
            raise HTTPException(422, "rule_relied_on must be a rule id such as RECON-RULE-001. Read the rules with get_reconciliation_rule.")
        if body.resolution in ("match", "match_with_adjustment") and not body.matched_entry_ids:
            raise HTTPException(422, "matched_entry_ids is needed for this resolution.")
        if body.resolution == "match_with_adjustment" and not (
                body.adjusting_debit_account and body.adjusting_credit_account and body.adjusting_amount > 0):
            raise HTTPException(422, "match_with_adjustment needs adjusting_debit_account, adjusting_credit_account and an adjusting_amount above 0.")
        if body.resolution == "reverse_duplicate" and not body.reverse_entry_id:
            raise HTTPException(422, "reverse_entry_id is needed for reverse_duplicate.")
        for eid in body.matched_entry_ids + ([body.reverse_entry_id] if body.reverse_entry_id else []):
            e = entry(eid)
            if not e or e["account_id"] != b["account_id"]:
                raise not_found("entry on this account", eid, "Entry ids are shown on the break.")
        v = st.add_draft(b, "proposals", {
            "resolution": body.resolution, "matched_entry_ids": body.matched_entry_ids,
            "reverse_entry_id": body.reverse_entry_id, "adjusting_debit_account": body.adjusting_debit_account,
            "adjusting_credit_account": body.adjusting_credit_account, "adjusting_amount": body.adjusting_amount,
            "evidence": body.evidence, "rule_relied_on": body.rule_relied_on, "explanation": body.explanation}, body.drafted_by)
        return {"applied": True, "kind": "draft", "break_status": b["status"], "draft": v}

    @reg(app, "post", "/breaks/{break_id}/post", "post_break_resolution", "Post the proposed resolution (change)",
         "Post the latest proposal: match the entries, and post the adjusting or reversing entry if the proposal has one. This "
         "is a change and needs the name of the person who approves. Refused with 409 if there is no proposal yet, if the "
         "latest proposal refers the break to a person, or if the break is already resolved.")
    def post_break_resolution(body: PostBody, break_id: str = brk_p):
        b = brk_or_404(break_id)
        with st.lock:
            if b["status"] == "resolved":
                raise conflict(f"Break {break_id} is already resolved. Nothing was changed.")
            if not b["proposals"]:
                raise conflict(f"Break {break_id} has no proposal yet. Save one with propose_break_resolution first. Nothing was changed.")
            prop = b["proposals"][-1]
            if prop["resolution"] == "refer_to_person":
                raise conflict(f"The latest proposal for {break_id} refers it to a person. There is nothing to post. "
                               "A person must resolve it. Nothing was changed.")
            item = entry(b["entry_id"])
            account = d()["recon_accounts"][b["account_id"]]
            created = []
            for eid in prop["matched_entry_ids"]:
                e = entry(eid)
                e["status"] = "matched"
                e["matched_with"] = sorted(set(e["matched_with"]) | {item["entry_id"]})
                item["matched_with"] = sorted(set(item["matched_with"]) | {eid})
            if prop["resolution"] in ("match", "match_with_adjustment"):
                item["status"] = "matched"
            if prop["resolution"] == "match_with_adjustment":
                new_id = f"LED-{st.next_number('recon_ledger', 7901)}"
                d()["recon_ledger"][new_id] = {
                    "entry_id": new_id, "side": "ledger", "account_id": b["account_id"], "value_date": item["value_date"],
                    "amount": prop["adjusting_amount"], "currency": account["currency"], "direction": "debit",
                    "reference": f"ADJ-{break_id}", "narrative": f"Adjusting entry: debit {prop['adjusting_debit_account']}, "
                    f"credit {prop['adjusting_credit_account']}", "status": "matched", "matched_with": [item["entry_id"]],
                    "batch_id": "", "posted_at": now_iso(), "debit_account": prop["adjusting_debit_account"],
                    "credit_account": prop["adjusting_credit_account"]}
                created.append(new_id)
            if prop["resolution"] == "reverse_duplicate":
                orig = entry(prop["reverse_entry_id"])
                new_id = f"LED-{st.next_number('recon_ledger', 7901)}"
                d()["recon_ledger"][new_id] = {
                    "entry_id": new_id, "side": "ledger", "account_id": b["account_id"], "value_date": orig["value_date"],
                    "amount": orig["amount"], "currency": orig["currency"],
                    "direction": "credit" if orig["direction"] == "debit" else "debit",
                    "reference": f"REV-{orig['entry_id']}", "narrative": f"Reversal of duplicate entry {orig['entry_id']}",
                    "status": "matched", "matched_with": [orig["entry_id"]], "batch_id": orig.get("batch_id", ""),
                    "posted_at": now_iso()}
                orig["status"] = "reversed"
                orig["matched_with"] = [new_id]
                created.append(new_id)
            b["status"] = "resolved"
            b["resolution"] = {"resolution": prop["resolution"], "approved_by": body.approved_by, "note": body.note,
                               "posted_at": now_iso(), "proposal_version": prop["version"],
                               "matched_entry_ids": prop["matched_entry_ids"], "entries_created": created}
            st.save()
        return {"applied": True, "kind": "change", "break_id": break_id, "status": b["status"], "resolution": b["resolution"]}

    return app
