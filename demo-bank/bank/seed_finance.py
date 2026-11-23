"""Seed data, part 14: a small finance warehouse. A general ledger and management accounts for 24 months, as plain rows.

The rows are loaded into an in-memory SQLite database when the finance system starts. Amounts depend on the month number only, so the
shape of the answers does not change with the bank date. SCENARIOS.md gives the known answers for the bank date 2026-11-24.

Operating cost is every account with is_operating_cost = 1: salaries, pension contributions, premises, technology, marketing and
professional fees. Interest, fees and the loan impairment charge are not operating cost.
Year to date is January to the last full month of the bank date's year.
"""

from __future__ import annotations

from datetime import date

MONTHS = 24

COST_CENTRES = [
    ("CC100", "Retail Branch Network", "Retail", "Ottoline Brackenridge"),
    ("CC200", "Business Banking", "Business", "Harlan Wyvernstone"),
    ("CC300", "Technology", "Technology", "Isobel Quartermain-Fox"),
    ("CC400", "Operations", "Operations", "Desmond Larkspur-Ayre"),
    ("CC500", "Risk and Compliance", "Risk", "Philippa Stonebridge-Marsh"),
    ("CC600", "Marketing", "Marketing", "Leander Foxcroft-Dane"),
    ("CC700", "Finance and Corporate", "Finance", "Margit Oldacre"),
    ("CC800", "Trust and Pensions", "Trust", "Evander Mossgrove"),
]
ACCOUNTS = [  # code, name, type, category, is_operating_cost
    (4100, "Interest income on loans", "income", "interest income", 0),
    (4200, "Fee income", "income", "fee income", 0),
    (5100, "Interest expense on deposits", "expense", "interest expense", 0),
    (6100, "Salaries", "expense", "staff costs", 1),
    (6110, "Pension contributions", "expense", "staff costs", 1),
    (6200, "Premises and rent", "expense", "premises", 1),
    (6300, "Cloud and hosting", "expense", "technology", 1),
    (6310, "Software licences", "expense", "technology", 1),
    (6400, "Advertising", "expense", "marketing", 1),
    (6500, "Consultancy", "expense", "professional fees", 1),
    (7100, "Loan impairment charge", "expense", "impairment", 0),
]
PRODUCTS = [("NONE", "Not product specific", "none"), ("P-HOME", "Home loans", "lending"), ("P-PERS", "Personal loans", "lending"),
            ("P-BIZ", "Business loans", "lending"), ("P-CUR", "Current accounts", "deposits"), ("P-SAV", "Savings accounts", "deposits")]
BRANCHES = [("BR00", "Head office", "Port Ilvane"), ("BR01", "Port Ilvane Main", "Port Ilvane"), ("BR02", "Tallowby", "Tallowby"),
            ("BR03", "Marlow Reach", "Marlow Reach")]
SHARE = {"BR01": 0.45, "BR02": 0.30, "BR03": 0.25}

# operating cost: cost centre -> account -> monthly budget at the start
COST_BASE = {
    "CC100": {6100: 410000, 6110: 41000, 6200: 96000},
    "CC200": {6100: 220000, 6110: 22000, 6200: 38000, 6500: 9000},
    "CC300": {6100: 330000, 6110: 33000, 6300: 120000, 6310: 85000, 6500: 25000},
    "CC400": {6100: 260000, 6110: 26000, 6200: 54000, 6500: 12000},
    "CC500": {6100: 150000, 6110: 15000, 6500: 30000, 6310: 14000},
    "CC600": {6100: 60000, 6110: 6000, 6400: 90000, 6500: 8000},
    "CC700": {6100: 120000, 6110: 12000, 6200: 22000, 6500: 40000},
    "CC800": {6100: 80000, 6110: 8000, 6310: 6000},
}
# account -> product -> monthly budget at the start, cost centre
INTEREST = [(4100, "P-HOME", 920000, "CC100"), (4100, "P-PERS", 410000, "CC100"), (4100, "P-BIZ", 640000, "CC200"),
            (5100, "P-CUR", 150000, "CC100"), (5100, "P-SAV", 520000, "CC100"), (4200, "P-CUR", 210000, "CC100"),
            (4200, "P-PERS", 60000, "CC100"), (7100, "P-PERS", 55000, "CC500"), (7100, "P-BIZ", 80000, "CC500")]


def month_label(today: date, back: int) -> str:
    """back = 1 is the last full month before the bank date."""
    m = today.year * 12 + today.month - 1 - back
    return f"{m // 12}-{m % 12 + 1:02d}"


def wobble(i: int, a: int, b: int) -> float:
    return ((i * 7 + a * 5 + b * 3) % 11 - 5) / 200.0


def cost_factor(cc: str, acct: int, i: int, n_ytd: int) -> float:
    """Extra over or under budget, as a fraction. i = 0 is 24 months back, i = 23 is the last full month."""
    ytd = i >= MONTHS - n_ytd  # January to the last full month of the year
    if cc == "CC300" and acct == 6300 and ytd:
        return 0.18
    if cc == "CC300" and acct == 6310 and ytd:
        return 0.08
    if cc == "CC300" and acct == 6500 and ytd:
        return 0.10
    if cc == "CC600" and acct == 6400 and ytd:
        return 0.22
    if cc == "CC400" and acct == 6100 and i == MONTHS - 1:
        return 0.09
    return wobble(i, int(cc[2:]) // 100, acct % 97)


def build_finance(today: date) -> dict:
    gl = []
    n_ytd = int(month_label(today, 1)[5:])
    for i in range(MONTHS):
        period = month_label(today, MONTHS - i)
        for cc, accts in COST_BASE.items():
            for acct, base in accts.items():
                budget = round(base * (1 + 0.004 * i))
                actual = round(budget * (1 + cost_factor(cc, acct, i, n_ytd)))
                if cc == "CC100":
                    for br, share in SHARE.items():
                        gl.append([period, cc, acct, "NONE", br, round(actual * share), round(budget * share)])
                else:
                    gl.append([period, cc, acct, "NONE", "BR00", actual, budget])
        for acct, prod, base, cc in INTEREST:
            budget_total = base * (1 + 0.005 * i)
            f = wobble(i, acct % 53, len(prod)) / 1.5
            if acct == 5100 and prod == "P-SAV" and i >= MONTHS - 6:
                f += 0.12
            if acct == 4100 and prod == "P-HOME" and i >= MONTHS - 6:
                f -= 0.02
            actual_total = budget_total * (1 + f)
            if acct == 7100:
                gl.append([period, cc, acct, prod, "BR00", round(actual_total), round(budget_total)])
                continue
            for br, share in SHARE.items():
                gl.append([period, cc, acct, prod, br, round(actual_total * share), round(budget_total * share)])
    tables = {
        "cost_centres": {"description": "The cost centres of the bank and who runs each one.", "columns": [
            ("cc_code", "TEXT", "Cost centre code, for example CC300."), ("cc_name", "TEXT", "Name of the cost centre."),
            ("department", "TEXT", "Department the cost centre belongs to."), ("manager", "TEXT", "The manager who answers for the budget.")],
            "rows": [list(r) for r in COST_CENTRES]},
        "accounts": {"description": "The ledger accounts. is_operating_cost is 1 for accounts that count as operating cost.", "columns": [
            ("account_code", "INTEGER", "Ledger account number."), ("account_name", "TEXT", "Name of the account."),
            ("account_type", "TEXT", "income or expense."), ("category", "TEXT", "Group of accounts, for example technology or interest income."),
            ("is_operating_cost", "INTEGER", "1 if the account counts as operating cost, else 0.")],
            "rows": [list(r) for r in ACCOUNTS]},
        "products": {"description": "Products. NONE is used for costs that belong to no product.", "columns": [
            ("product_code", "TEXT", "Product code."), ("product_name", "TEXT", "Name of the product."), ("product_group", "TEXT", "lending, deposits or none.")],
            "rows": [list(r) for r in PRODUCTS]},
        "branches": {"description": "Branches. BR00 is the head office, used for costs that are not split by branch.", "columns": [
            ("branch_id", "TEXT", "Branch code."), ("branch_name", "TEXT", "Name of the branch."), ("town", "TEXT", "Town.")],
            "rows": [list(r) for r in BRANCHES]},
        "gl_monthly": {"description": "Monthly actuals and budget by cost centre, account, product and branch for 24 months. Amounts are in USD. "
                                      "Income and expense are both positive numbers: use accounts.account_type to tell them apart.", "columns": [
            ("period", "TEXT", "Month as YYYY-MM."), ("cc_code", "TEXT", "Cost centre code, see cost_centres."),
            ("account_code", "INTEGER", "Ledger account, see accounts."), ("product_code", "TEXT", "Product, see products."),
            ("branch_id", "TEXT", "Branch, see branches."), ("actual", "INTEGER", "Actual amount for the month in USD."),
            ("budget", "INTEGER", "Budgeted amount for the month in USD.")], "rows": gl},
    }
    return {"finance": tables, "finance_commentaries": {}}
