"""Tills, version 1.1: refunds, voids and discounts for the period, and the company's till rules.

180 rows for the eight stores and twelve restaurants. 28 of them sit outside a rule, and they are written out
in PLANTED. Every other row is made inside the rules, some of them only just. Which rows were planted is kept
in its own record set (till_planted) and no operation serves it.
"""

from __future__ import annotations

import random
from datetime import date

from .seed_base import days_in, money, period_of, yymm
from .seed_stores import build_sites

TOTALS = {"refund": 72, "void": 48, "discount": 60}
REFUND_LIMIT, DISCOUNT_LIMIT = 50.00, 20.0

RULES = [
    {"rule_id": "TC-1", "applies_to": "refund",
     "text": "A refund above USD 50.00 needs a manager's approval. The approver's id is recorded on the row.",
     "how_to_test": "kind is refund, amount is above 50.00 and approver_id is empty. A refund of exactly 50.00 needs no approval."},
    {"rule_id": "TC-2", "applies_to": "refund",
     "text": "No refund is made without the original receipt number. It is recorded on the row.",
     "how_to_test": "kind is refund and original_receipt is empty, whatever the amount."},
    {"rule_id": "TC-3", "applies_to": "discount",
     "text": "A discount above 20 percent needs a reason code.",
     "how_to_test": "kind is discount, discount_percent is above 20 and reason_code is empty. A discount of exactly 20 percent needs no code."},
    {"rule_id": "TC-4", "applies_to": "void",
     "text": "A void after payment needs a second person. The second person's id is recorded on the row as the approver.",
     "how_to_test": "kind is void, after_payment is true and approver_id is empty. A void before payment needs no second person."},
]
REASON_CODES = {"D1": "colleague discount", "D2": "damaged packaging", "D3": "short date", "D4": "price match",
                "D5": "manager's goodwill"}
RULES_DOCUMENT = {
    "document": "Till Controls", "version": "1.3", "owner": "Head of Loss Prevention",
    "notice": "Rowanmere Group is invented, and so are these rules. They are not the rules of any real retailer.",
    "rules": RULES,
    "discount_reason_codes": REASON_CODES,
    "what_the_rules_do_not_decide": "A row outside a rule is a row for an auditor to look at. The rules do not say why it "
                                    "happened, and they do not say that any colleague did anything wrong. An auditor reviews "
                                    "every row.",
}

# day, time, site, till, cashier (1 to 4 at that site), kind, then what the kind needs:
#   refund:   amount, has an approver, has a receipt number
#   discount: sale amount, percent
#   void:     amount
# and the rules the row is outside.
PLANTED = [
    (3, "18:42", "S-106", "T2", 3, "refund", (84.50, False, True), ["TC-1"]),
    (9, "19:15", "S-106", "T2", 3, "refund", (129.99, False, True), ["TC-1"]),
    (12, "20:05", "S-106", "T2", 3, "refund", (76.00, False, False), ["TC-1", "TC-2"]),
    (17, "19:48", "S-106", "T2", 3, "refund", (210.00, False, False), ["TC-1", "TC-2"]),
    (21, "18:20", "S-106", "T2", 3, "refund", (32.40, False, False), ["TC-2"]),
    (14, "17:55", "S-106", "T2", 3, "discount", (48.00, 35), ["TC-3"]),
    (24, "20:31", "S-106", "T2", 3, "discount", (62.00, 50), ["TC-3"]),
    (27, "19:02", "S-106", "T2", 3, "void", (58.75,), ["TC-4"]),
    (6, "11:14", "S-106", "T1", 1, "refund", (61.20, False, True), ["TC-1"]),
    (19, "10:32", "S-106", "T1", 1, "refund", (18.99, False, False), ["TC-2"]),
    (8, "13:40", "S-106", "T1", 4, "discount", (80.00, 25), ["TC-3"]),
    (29, "15:07", "S-106", "T2", 4, "void", (23.10,), ["TC-4"]),
    (4, "12:26", "S-101", "T3", 2, "refund", (95.00, False, True), ["TC-1"]),
    (11, "16:09", "S-104", "T1", 1, "refund", (55.25, False, True), ["TC-1"]),
    (15, "13:51", "R-014", "T1", 2, "refund", (64.80, False, True), ["TC-1"]),
    (22, "19:37", "R-063", "T2", 1, "refund", (52.00, False, True), ["TC-1"]),
    (7, "09:48", "S-102", "T2", 3, "refund", (12.49, False, False), ["TC-2"]),
    (18, "14:22", "S-107", "T1", 2, "refund", (44.00, False, False), ["TC-2"]),
    (25, "21:10", "R-047", "T1", 1, "refund", (27.90, False, False), ["TC-2"]),
    (10, "15:33", "S-101", "T4", 4, "discount", (120.00, 30), ["TC-3"]),
    (13, "10:05", "S-105", "T1", 2, "discount", (50.00, 22), ["TC-3"]),
    (16, "20:44", "R-022", "T1", 1, "discount", (36.50, 40), ["TC-3"]),
    (20, "12:58", "R-058", "T2", 3, "discount", (21.00, 100), ["TC-3"]),
    (28, "18:16", "R-090", "T1", 2, "discount", (44.00, 25), ["TC-3"]),
    (5, "17:29", "S-103", "T1", 1, "void", (14.20,), ["TC-4"]),
    (23, "11:41", "S-104", "T2", 3, "void", (88.00,), ["TC-4"]),
    (26, "13:03", "R-031", "T1", 2, "void", (31.50,), ["TC-4"]),
    (30, "19:55", "R-104", "T1", 1, "void", (19.75,), ["TC-4"]),
]

REFUND_REASONS = ["customer changed their mind", "item faulty", "wrong item sold", "item out of date", "charged twice",
                  "order not as described"]
VOID_REASONS = ["wrong item rung up", "customer changed their mind", "price error", "payment declined", "duplicate scan"]


SITE_ORDER = sorted(build_sites())


def cashier_id(site_id: str, n: int) -> str:
    return f"C-{3000 + SITE_ORDER.index(site_id) * 10 + n}"


def manager_id(site_id: str) -> str:
    return f"M-{700 + SITE_ORDER.index(site_id)}"


def breaks(row: dict) -> list[str]:
    """The rules a row is outside, worked out from the row alone."""
    out = []
    if row["kind"] == "refund":
        if row["amount"] > REFUND_LIMIT and not row["approver_id"]:
            out.append("TC-1")
        if not row["original_receipt"]:
            out.append("TC-2")
    elif row["kind"] == "discount":
        if row["discount_percent"] > DISCOUNT_LIMIT and not row["reason_code"]:
            out.append("TC-3")
    elif row["kind"] == "void":
        if row["after_payment"] and not row["approver_id"]:
            out.append("TC-4")
    return out


def _row(period: str, day: int, time: str, site_id: str, till: str, cashier: str, kind: str) -> dict:
    return {"row_id": "", "date": f"{period}-{min(day, days_in(period)):02d}", "time": time, "site_id": site_id, "till": till,
            "cashier_id": cashier, "kind": kind, "amount": 0.0, "currency": "USD", "reason": "", "approver_id": "",
            "original_receipt": "", "sale_amount": None, "discount_percent": None, "reason_code": "", "after_payment": None}


def build_tills(today: date) -> dict:
    period = period_of(today)
    rng = random.Random(f"tills-{period}")
    sites = build_sites()
    made, planted_keys = [], {}

    def receipt(site_id: str) -> str:
        return f"RC-{site_id[2:]}-{rng.randint(10000, 99999)}"

    for day, time, site_id, till, n, kind, what, rules in PLANTED:
        row = _row(period, day, time, site_id, till, cashier_id(site_id, n), kind)
        if kind == "refund":
            amount, approved, has_receipt = what
            row.update(amount=amount, reason=rng.choice(REFUND_REASONS), approver_id=manager_id(site_id) if approved else "",
                       original_receipt=receipt(site_id) if has_receipt else "")
        elif kind == "discount":
            sale, percent = what
            row.update(sale_amount=sale, discount_percent=float(percent), amount=money(sale * percent / 100))
        else:
            row.update(amount=what[0], reason=rng.choice(VOID_REASONS), after_payment=True)
        assert breaks(row) == rules, (row, rules)
        made.append(row)
        planted_keys[id(row)] = rules

    weights = [3 if s["kind"] == "store" else 2 for s in sites.values()]
    ids = list(sites)
    for kind, total in TOTALS.items():
        for _ in range(total - sum(1 for p in PLANTED if p[5] == kind)):
            site_id = rng.choices(ids, weights)[0]
            tills = 4 if sites[site_id]["kind"] == "store" else 2
            n = rng.randint(1, 4)
            row = _row(period, rng.randint(1, days_in(period)), f"{rng.randint(8, 21):02d}:{rng.randint(0, 59):02d}", site_id,
                       f"T{rng.randint(1, tills)}", cashier_id(site_id, n), kind)
            other = cashier_id(site_id, n % 4 + 1)
            if kind == "refund":
                pick = rng.random()
                amount = 50.00 if pick < 0.10 else (money(rng.uniform(3, 49.99)) if pick < 0.65 else money(rng.uniform(50.01, 240)))
                needs = amount > REFUND_LIMIT
                row.update(amount=amount, reason=rng.choice(REFUND_REASONS), original_receipt=receipt(site_id),
                           approver_id=manager_id(site_id) if (needs or rng.random() < 0.15) else "")
            elif kind == "discount":
                percent = float(rng.choice([5, 10, 10, 15, 20, 20, 20, 25, 30, 50]))
                sale = money(rng.uniform(8, 150))
                code = rng.choice(sorted(REASON_CODES)) if (percent > DISCOUNT_LIMIT or rng.random() < 0.3) else ""
                row.update(sale_amount=sale, discount_percent=percent, amount=money(sale * percent / 100), reason_code=code,
                           reason=REASON_CODES.get(code, ""))
            else:
                after = rng.random() < 0.5
                row.update(amount=money(rng.uniform(2, 120)), reason=rng.choice(VOID_REASONS), after_payment=after,
                           approver_id=rng.choice([manager_id(site_id), other]) if after else "")
            assert breaks(row) == [], row
            made.append(row)

    made.sort(key=lambda r: (r["date"], r["time"], r["site_id"], r["till"]))
    rows, planted = {}, {}
    for n, row in enumerate(made, start=1):
        row["row_id"] = f"TR-{yymm(period)}-{n:04d}"
        rows[row["row_id"]] = row
        if id(row) in planted_keys:
            planted[row["row_id"]] = list(planted_keys[id(row)])
    return {"till_rows": rows, "till_planted": planted, "till_audits": {}}
