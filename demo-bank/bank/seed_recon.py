"""Seed data, part 5: reconciliation accounts, ledger and statement entries, breaks and rules."""

from __future__ import annotations

import copy
from datetime import date

from .seed_base import d_ago

ACCOUNTS = {
    "NOS-ALDB-01": {"account_id": "NOS-ALDB-01", "name": "Nostro account, USD, at Aldoria Commerce Bank", "currency": "USD",
                    "correspondent_bank": "Aldoria Commerce Bank"},
    "NOS-QNMK-01": {"account_id": "NOS-QNMK-01", "name": "Nostro account, USD, at Quenmark National Bank", "currency": "USD",
                    "correspondent_bank": "Quenmark National Bank"},
    "NOS-TESL-01": {"account_id": "NOS-TESL-01", "name": "Nostro account, USD, at Tessaly Mutual Bank", "currency": "USD",
                    "correspondent_bank": "Tessaly Mutual Bank"},
}

RULES = {
    "RECON-RULE-001": {
        "rule_id": "RECON-RULE-001", "title": "Match on amount, value date and reference",
        "text": "A ledger entry and a statement entry match when the amount is exactly the same, the value dates are no more "
                "than three days apart and the references are the same or differ by one character (a mistyped or missing "
                "character). Name the entry you match with. No adjusting entry is needed."},
    "RECON-RULE-002": {
        "rule_id": "RECON-RULE-002", "title": "One statement entry for a batch of ledger entries",
        "text": "One statement entry matches several ledger entries when the ledger entries were posted in the same batch "
                "and their amounts add up exactly to the statement amount. Name every ledger entry in the match."},
    "RECON-RULE-003": {
        "rule_id": "RECON-RULE-003", "title": "Difference caused by a bank charge",
        "text": "When the amounts differ by a bank charge of up to USD 25.00 and the statement narrative or a charge advice "
                "names the charge, match the two entries and post the difference with an adjusting entry: debit GL-6120 "
                "(Bank charges) and credit the nostro account. A difference above USD 25.00 is never adjusted. Refer it "
                "to a person."},
    "RECON-RULE-004": {
        "rule_id": "RECON-RULE-004", "title": "Duplicate ledger posting",
        "text": "When the same ledger entry (same account, amount, value date, reference and batch) is posted twice and the "
                "statement shows it once, the later entry is the duplicate. Reverse it with a reversing entry. Never "
                "reverse the entry that is matched to the statement."},
    "RECON-RULE-005": {
        "rule_id": "RECON-RULE-005", "title": "No candidate: do not force a match",
        "text": "When the checks find no ledger entry that could belong to a statement item, do not match it, do not write "
                "it off and do not post an adjusting entry. Record what was checked and refer the break to the "
                "Reconciliation Team lead, who decides. A break older than five days is escalated the same day."},
}

CHECKS = ["Same amount within 5 days either side of the value date, on this account.",
          "Same reference, or a reference that differs by one character.",
          "Sum of entries posted in the same batch equals the amount.",
          "Same entry posted twice on the ledger."]


def _entry(side: str, eid: str, account: str, today: date, vd: int, amount: float, direction: str, ref: str,
           narrative: str, status: str = "unmatched", batch: str = "", posted: str = "", matched_with=()) -> dict:
    e = {"entry_id": eid, "side": side, "account_id": account, "value_date": d_ago(today, vd), "amount": float(amount),
         "currency": "USD", "direction": direction, "reference": ref, "narrative": narrative, "status": status,
         "matched_with": list(matched_with)}
    if side == "ledger":
        e["batch_id"] = batch
        e["posted_at"] = posted or f"{d_ago(today, vd)} 09:00"
    return e


def make_break(d: dict, today: date, brk_id: str, account: str, side: str, entry_id: str, opened_ago: int,
               candidates: list, checks: list | None = None) -> dict:
    rec = {"break_id": brk_id, "account_id": account, "status": "open", "side": side, "entry_id": entry_id,
           "opened": d_ago(today, opened_ago),
           "candidates": [{"entry_id": c[0], "side": "ledger" if c[0].startswith("LED") else "statement",
                           "likely": c[1], "reason": c[2]} for c in candidates],
           "auto_match_checks": checks or CHECKS, "proposals": [], "resolution": None}
    d["recon_breaks"][brk_id] = rec
    return rec


def build_recon(today: date) -> tuple[dict, dict, dict, dict]:
    led: dict = {}
    stm: dict = {}
    d = {"recon_breaks": {}}

    def L(*a, **k):
        e = _entry("ledger", *a, **k)
        led[e["entry_id"]] = e
        return e

    def S(*a, **k):
        e = _entry("statement", *a, **k)
        stm[e["entry_id"]] = e
        return e

    # background: matched pairs on each account, so the statements look real
    n = 0
    for acct, base in (("NOS-ALDB-01", 40), ("NOS-QNMK-01", 44), ("NOS-TESL-01", 48)):
        for k in range(5):
            n += 1
            amt = 1500.0 + 275.5 * k + n * 10
            direction = "credit" if k % 2 == 0 else "debit"
            ref = f"SET-{3100 + n}"
            L(f"LED-6{n:03d}", acct, today, base + k * 6, amt, direction, ref, "Settlement", status="matched",
              batch=f"BATCH-03{n:02d}", matched_with=[f"STM-6{n:03d}"])
            S(f"STM-6{n:03d}", acct, today, base + k * 6, amt, direction, ref, "Settlement", status="matched",
              matched_with=[f"LED-6{n:03d}"])

    # BRK-4001: one mistyped character in the reference, value dates one day apart
    S("STM-8101", "NOS-ALDB-01", today, 5, 12480.00, "credit", "INV-558210-AQ", "Incoming transfer, Corrowick Alloy Works")
    L("LED-7101", "NOS-ALDB-01", today, 6, 12480.00, "credit", "INV-558210-AO", "Expected receipt, alloy bar invoice")
    L("LED-7102", "NOS-ALDB-01", today, 5, 12408.00, "credit", "INV-558901-AL", "Expected receipt, another invoice")
    make_break(d, today, "BRK-4001", "NOS-ALDB-01", "statement", "STM-8101", 5, [
        ("LED-7101", True, "Same amount, value date one day earlier, reference differs by one character (AO against AQ)."),
        ("LED-7102", False, "Amount is close (the digits 80 and 08 are swapped), but the reference is for a different invoice.")])

    # BRK-4002: one statement credit, two ledger entries posted as a batch
    S("STM-8201", "NOS-QNMK-01", today, 4, 8000.00, "credit", "SETT-BATCH-0457", "Batch settlement credit")
    L("LED-7201", "NOS-QNMK-01", today, 4, 5250.00, "credit", "SETT-BATCH-0457-01", "Batch line 1", batch="BATCH-0457")
    L("LED-7202", "NOS-QNMK-01", today, 4, 2750.00, "credit", "SETT-BATCH-0457-02", "Batch line 2", batch="BATCH-0457")
    L("LED-7203", "NOS-QNMK-01", today, 13, 5250.00, "credit", "SETT-BATCH-0399-01", "Batch line 1, older batch",
      batch="BATCH-0399")
    make_break(d, today, "BRK-4002", "NOS-QNMK-01", "statement", "STM-8201", 4, [
        ("LED-7201", True, "Posted in batch BATCH-0457, which the statement reference names. 5,250.00 of the 8,000.00."),
        ("LED-7202", True, "Posted in the same batch BATCH-0457. 2,750.00. Together with LED-7201 it makes 8,000.00."),
        ("LED-7203", False, "Same amount as LED-7201 but posted in an older batch, BATCH-0399, nine days earlier.")])

    # BRK-4003: bank charge of 15.00 taken from the credit
    S("STM-8301", "NOS-TESL-01", today, 3, 9985.00, "credit", "TRF-77120", "Incoming transfer TRF-77120, less charges 15.00")
    L("LED-7301", "NOS-TESL-01", today, 3, 10000.00, "credit", "TRF-77120", "Expected receipt, transfer TRF-77120")
    make_break(d, today, "BRK-4003", "NOS-TESL-01", "statement", "STM-8301", 3, [
        ("LED-7301", True, "Same reference TRF-77120 and same value date. The statement is 15.00 lower, and its narrative "
                           "says charges of 15.00.")])

    # BRK-4004: the same ledger entry posted twice
    S("STM-8401", "NOS-ALDB-01", today, 7, 4175.50, "debit", "PO-3382", "Payment to supplier, PO-3382", status="matched",
      matched_with=["LED-7401"])
    L("LED-7401", "NOS-ALDB-01", today, 7, 4175.50, "debit", "PO-3382", "Supplier payment PO-3382", status="matched",
      batch="BATCH-0460", posted=f"{d_ago(today, 7)} 14:02", matched_with=["STM-8401"])
    L("LED-7402", "NOS-ALDB-01", today, 7, 4175.50, "debit", "PO-3382", "Supplier payment PO-3382",
      batch="BATCH-0460", posted=f"{d_ago(today, 7)} 14:04")
    make_break(d, today, "BRK-4004", "NOS-ALDB-01", "ledger", "LED-7402", 7, [
        ("LED-7401", True, "Same account, amount, value date, reference and batch, posted two minutes earlier. It is already "
                           "matched to statement entry STM-8401.")])

    # BRK-4005: a statement item with nothing behind it
    S("STM-8501", "NOS-QNMK-01", today, 9, 3275.40, "debit", "UNK-77QX", "ADJ 77-QX NO REMITTANCE INFORMATION")
    make_break(d, today, "BRK-4005", "NOS-QNMK-01", "statement", "STM-8501", 9, [])

    # an older break that was already resolved
    S("STM-8001", "NOS-TESL-01", today, 30, 2200.00, "credit", "REF-5521", "Incoming transfer", status="matched",
      matched_with=["LED-7001"])
    L("LED-7001", "NOS-TESL-01", today, 31, 2200.00, "credit", "REF-5512", "Expected receipt", status="matched",
      matched_with=["STM-8001"])
    b = make_break(d, today, "BRK-3901", "NOS-TESL-01", "statement", "STM-8001", 29, [
        ("LED-7001", True, "Same amount, value date one day earlier, reference differs by one character.")])
    b["status"] = "resolved"
    b["resolution"] = {"resolution": "match", "approved_by": "Analyst M. Okonjo-Vale", "posted_at": d_ago(today, 28),
                       "proposal_version": 1, "matched_entry_ids": ["LED-7001"], "entries_created": []}
    return copy.deepcopy(ACCOUNTS), led, stm, d["recon_breaks"]


def sim_break(d: dict, today: date, kind: int, n: int) -> tuple[str, str]:
    """One new break from four rotating templates. Returns the break id and a plain sentence."""
    base = 9100 + n * 10
    acct = ["NOS-ALDB-01", "NOS-TESL-01", "NOS-QNMK-01", "NOS-ALDB-01"][kind]
    bid = f"BRK-{4100 + n}"

    def put(e):
        (d["recon_ledger"] if e["side"] == "ledger" else d["recon_statement"])[e["entry_id"]] = e

    if kind == 0:
        put(_entry("statement", f"STM-{base}", acct, today, 2, 6320.00, "credit", f"INV-770{n}4-Z", "Incoming transfer"))
        put(_entry("ledger", f"LED-{base}", acct, today, 3, 6320.00, "credit", f"INV-770{n}4-2", "Expected receipt"))
        make_break(d, today, bid, acct, "statement", f"STM-{base}", 2, [
            (f"LED-{base}", True, "Same amount, value date one day earlier, reference differs by one character.")])
        text = "The same amount arrived one day apart and the references differ by one character."
    elif kind == 1:
        put(_entry("statement", f"STM-{base}", acct, today, 2, 4487.50, "credit", f"TRF-880{n}", "Incoming transfer, charges 12.50"))
        put(_entry("ledger", f"LED-{base}", acct, today, 2, 4500.00, "credit", f"TRF-880{n}", "Expected receipt"))
        make_break(d, today, bid, acct, "statement", f"STM-{base}", 2, [
            (f"LED-{base}", True, "Same reference and value date. The statement is 12.50 lower and says charges of 12.50.")])
        text = "The statement amount is 12.50 lower than the ledger amount."
    elif kind == 2:
        put(_entry("statement", f"STM-{base}", acct, today, 3, 980.00, "debit", f"PO-41{n}7", "Payment to supplier", "matched",
                   matched_with=[f"LED-{base}"]))
        put(_entry("ledger", f"LED-{base}", acct, today, 3, 980.00, "debit", f"PO-41{n}7", "Supplier payment", "matched",
                   batch=f"BATCH-05{n}0", posted=f"{d_ago(today, 3)} 10:00", matched_with=[f"STM-{base}"]))
        put(_entry("ledger", f"LED-{base + 1}", acct, today, 3, 980.00, "debit", f"PO-41{n}7", "Supplier payment",
                   batch=f"BATCH-05{n}0", posted=f"{d_ago(today, 3)} 10:01"))
        make_break(d, today, bid, acct, "ledger", f"LED-{base + 1}", 3, [
            (f"LED-{base}", True, "Same account, amount, value date, reference and batch, posted a minute earlier. Already "
                                  f"matched to STM-{base}.")])
        text = "A ledger entry looks like a second posting of an entry that is already matched."
    else:
        put(_entry("statement", f"STM-{base}", acct, today, 6, 1840.10, "debit", f"UNK-{n}Z9", "ADJ NO REMITTANCE INFORMATION"))
        make_break(d, today, bid, acct, "statement", f"STM-{base}", 6, [])
        text = "A statement item has no ledger entry behind it and nothing close to it was found."
    return bid, (f"A new reconciliation break {bid} has arrived in the recon system on account {acct}. {text} "
                 f"It is open and needs a proposal. Read it with get_reconciliation_break in the recon system.")
