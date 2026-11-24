"""Builds cases.json for the pricing and replenishment desk from the invented retailer's own records.

Twelve cases, as the pricing and stock systems hold them when the retailer's date is 24 November 2026:
one price review for each category that has a line with a published competitor price (eight), one
replenishment case for each supplier that has a line running out before its next delivery (three),
and one for a supplier with nothing to order. Nothing is typed here by hand: lines, prices, costs,
competitor prices, stock, sales, supply terms, open orders and both sets of rules come from the seed
of the service in ../../../demo-retailer. No server is started.

Each case carries the records its agent needs, because the desk's agents work from the message
alone. Which suppliers have a line that runs out is worked out here from stock, sales and open
orders, by the replenishment rules. The service's own answer sets are never read.

Usage, from anywhere:
    python make_cases.py           writes cases.json beside this file
    python make_cases.py --check   exits 1 if cases.json differs from what would be written

The test demo-retailer/tests/test_pricing_and_replenishment_desk_cases.py runs the same comparison,
and builds every case again from what the service returns.
Rowanmere Group is invented, and so is every record.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
RETAILER = HERE.parents[2] / "demo-retailer"
OUT = HERE / "cases.json"

RETAILER_DATE = date(2026, 11, 24)
CATEGORIES = ["ambient_grocery", "chilled_food", "frozen_food", "bakery", "fresh_produce", "drinks", "household",
              "personal_care"]
# The supplier with nothing to order. It is the one whose lines hold an overstocked line and a line exactly on the
# overstock limit. The three suppliers with a line that runs out are found from the records.
NOTHING_TO_ORDER = "SUP-317"

KIND_PRICE = "Price change"
KIND_ORDER = "Replenishment order"

COMMENT = ("Twelve invented cases for the demo: eight price reviews, one for each category with a published competitor "
           "price, and four replenishment cases, one for each supplier with a line that runs out and one with nothing to "
           "order. Made by make_cases.py from the records the invented retailer (demo-retailer) holds at retailer date "
           "2026-11-24. Do not edit by hand: change the service's seed and run the script. Rowanmere Group, its suppliers, "
           "its competitors and every record are invented.")


def money(v) -> str:
    return f"{v:,.2f}"


def qty(v) -> str:
    return f"{v:,}"


def plural(n: int, word: str) -> str:
    return f"{qty(n)} {word}{'' if n == 1 else 's'}"


def category_name(category: str) -> str:
    """ambient_grocery as a person writes it: Ambient grocery."""
    return category.replace("_", " ").capitalize()


def line_name(row: dict) -> str:
    return f"{row['sku']} {row['name']}"


def rule_lines(heading: str, document: dict, rows: list, id_key: str) -> list:
    lines = [heading, f"Document: {document['document']}, version {document['version']}"]
    for r in rows:
        lines.append("")
        lines.append(f"{r[id_key]} {r['title']}: {r['text']}" if r.get("title") else f"{r[id_key]}: {r['text']}")
    return lines


# ---------------------------------------------------------------- a price review

def price_text(category: str, prices: list, competitors: dict, levels: dict, rules: dict, retailer_date: str) -> str:
    """One category of the price file with what the competitors publish, the stock behind each line and the pricing rules.

    prices: the price file's rows for the category. competitors: by line id, the row of published prices. levels: by
    line id, the stock row for all stores together. Each as the service returns it.
    """
    with_price = [p for p in prices if p["sku"] in competitors]
    without = [p for p in prices if p["sku"] not in competitors]
    published = sorted({x["published_on"] for p in with_price for x in competitors[p["sku"]]["prices"]})
    names = sorted({x["competitor"] for p in with_price for x in competitors[p["sku"]]["prices"]}, reverse=True)
    lines = ["THE REVIEW", f"Category: {category_name(category)}", f"Retailer date: {retailer_date}",
             f"Competitors: {' and '.join(names)}", f"Published on: {', '.join(published)}",
             "LINES WITH A PUBLISHED COMPETITOR PRICE"]
    for n, p in enumerate(with_price):
        level = levels[p["sku"]]
        lines += [""] if n else []
        shown = ", ".join(f"{x['competitor']} {money(x['price'])}" for x in competitors[p["sku"]]["prices"])
        lines += [line_name(p), f"Our price: {money(p['price'])}, cost {money(p['cost'])}", f"Published: {shown}",
                  f"Stock: {qty(level['on_hand'])} on hand, {qty(level['units_sold_last_four_weeks'])} sold in the last four weeks"]
    lines.append("LINES WITH NO PUBLISHED COMPETITOR PRICE")
    lines += [f"{line_name(p)}: {money(p['price'])}" for p in without] or ["None. Every line of the category has one."]
    lines += rule_lines("THE PRICING RULES", rules, rules["rules"], "rule_id")
    lines.append("HOW A RECOMMENDATION IS WORKED OUT")
    for n, s in enumerate(rules["how_a_recommendation_is_worked_out"]):
        lines += ([""] if n else []) + [f"{s['step']}: {s['text']}"]
    lines += ["WHAT THE RULES DO NOT DECIDE", rules["what_the_rules_do_not_decide"]]
    return "\n".join(lines)


def price_case(category: str, prices: list, competitors: dict, levels: dict, rules: dict, retailer_date: str) -> dict:
    with_price = [p for p in prices if p["sku"] in competitors]
    return {"title": f"{category_name(category)}: price review", "kind": KIND_PRICE,
            "about": f"{plural(len(with_price), 'line')} to review",
            "category": category_name(category), "supplier": "", "lines": ", ".join(p["sku"] for p in prices),
            "rules": f"{rules['document']}, version {rules['version']}", "received_on": retailer_date,
            "text": price_text(category, prices, competitors, levels, rules, retailer_date), "arrived_via": "feed"}


# ---------------------------------------------------------------- a replenishment case

def runs_out(term: dict, level: dict, retailer_date: str) -> bool:
    """Rules RP-1 to RP-3: cover in days is fewer than the days to the next delivery. Exactly the same is not a run-out."""
    daily = level["units_sold_last_four_weeks"] / 28
    cover = level["on_hand"] / daily
    dues = sorted(o["due_on"] for o in term["open_orders"])
    days = (date.fromisoformat(dues[0]) - date.fromisoformat(retailer_date)).days if dues else term["lead_time_days"]
    return cover < days


def suppliers_to_show(terms: list, levels: dict, retailer_date: str) -> list:
    """The suppliers with a line that runs out, in order of number, then the one with nothing to order."""
    short = sorted({t["supplier_id"] for t in terms if runs_out(t, levels[t["sku"]], retailer_date)})
    assert NOTHING_TO_ORDER not in short, f"{NOTHING_TO_ORDER} has a line that runs out"
    return short + [NOTHING_TO_ORDER]


def order_text(terms: list, levels: dict, rules: dict, retailer_date: str) -> str:
    """One supplier's lines with stock, sales, supply terms and open orders, and the replenishment rules.

    terms: the supply terms of the supplier's lines. levels: by line id, the stock row for all stores together.
    """
    first = terms[0]
    assert all((t["lead_time_days"], t["minimum_order_cases"]) == (first["lead_time_days"], first["minimum_order_cases"])
               for t in terms), "the lines of one supplier differ in lead time or minimum order"
    record = (f"Held in the purchasing system. Payment terms {first['payment_terms_days']} days"
              if first["supplier_in_purchasing"] else "None in the purchasing system. The supply terms hold the supplier")
    lines = ["THE SUPPLIER", f"Supplier: {first['supplier_name']} ({first['supplier_id']})", f"Retailer date: {retailer_date}",
             f"Lead time: {plural(first['lead_time_days'], 'day')}", f"Minimum order: {plural(first['minimum_order_cases'], 'case')}",
             f"Record: {record}", "THE LINES"]
    for n, t in enumerate(terms):
        level = levels[t["sku"]]
        lines += [""] if n else []
        on_order = "; ".join(f"{o['order_ref']}, {plural(o['units'], 'unit')}, due {o['due_on']}" for o in t["open_orders"])
        lines += [line_name(t),
                  f"Stock: {qty(level['on_hand'])} on hand, {qty(level['units_sold_last_four_weeks'])} sold in the last four weeks",
                  f"Supply: case of {qty(t['case_size'])}. On order: {on_order or 'nothing'}"]
    lines += rule_lines("THE REPLENISHMENT RULES", rules, rules["rules"], "rule_id")
    lines += ["WHAT THE RULES DO NOT DECIDE", rules["what_the_rules_do_not_decide"]]
    return "\n".join(lines)


def order_case(terms: list, levels: dict, rules: dict, retailer_date: str) -> dict:
    first = terms[0]
    return {"title": f"{first['supplier_name']}: replenishment", "kind": KIND_ORDER,
            "about": plural(len(terms), "line"),
            "category": "", "supplier": f"{first['supplier_name']} ({first['supplier_id']})",
            "lines": ", ".join(t["sku"] for t in terms), "rules": f"{rules['document']}, version {rules['version']}",
            "received_on": retailer_date, "text": order_text(terms, levels, rules, retailer_date), "arrived_via": "feed"}


# ---------------------------------------------------------------- the records, from the seed

class SeedSource:
    """The records as the service's seed holds them, in the shape the service returns. The test has the same readers over the API."""

    def __init__(self, data: dict, rules: dict):
        self.data, self.rules = data, rules

    def prices(self, category: str) -> list:
        return sorted((p for p in self.data["price_file"].values() if p["category"] == category), key=lambda p: p["sku"])

    def competitors(self) -> dict:
        return {sku: {**x, "our_price": self.data["price_file"][sku]["price"]} for sku, x in self.data["competitor_prices"].items()}

    def levels(self) -> dict:
        out = {}
        for sku, x in self.data["stock_levels"].items():
            stores = x["by_store"].values()
            out[sku] = {"sku": sku, "name": x["name"], "category": x["category"], "on_hand": sum(s["on_hand"] for s in stores),
                        "units_sold_last_four_weeks": sum(sum(s["weekly_sales"][-4:]) for s in stores)}
        return out

    def terms(self, supplier_id: str | None = None) -> list:
        rows = []
        for t in self.data["supply_terms"].values():
            if supplier_id and t["supplier_id"] != supplier_id:
                continue
            held = self.data["suppliers"].get(t["supplier_id"])
            rows.append({**t, "units_on_order": sum(o["units"] for o in t["open_orders"]), "supplier_in_purchasing": bool(held),
                         "payment_terms_days": held["payment_terms_days"] if held else None})
        return sorted(rows, key=lambda t: t["sku"])

    def pricing_rules(self) -> dict:
        return self.rules["pricing"]

    def replenishment_rules(self) -> dict:
        return self.rules["replenishment"]


def _seed() -> SeedSource:
    """The service's starting data for the retailer date. Imported, never served."""
    if str(RETAILER) not in sys.path:
        sys.path.insert(0, str(RETAILER))
    from retailer.seed import build_all  # noqa: E402
    from retailer.seed_pricing import PRICING_RULES  # noqa: E402
    from retailer.seed_stock import REPLENISHMENT_RULES  # noqa: E402

    return SeedSource(build_all(RETAILER_DATE), {"pricing": PRICING_RULES, "replenishment": REPLENISHMENT_RULES})


def build_from(source) -> list:
    """The twelve cases, from any source with the six readers of SeedSource."""
    today = RETAILER_DATE.isoformat()
    competitors, levels = source.competitors(), source.levels()
    cases = []
    for category in CATEGORIES:
        prices = source.prices(category)
        if any(p["sku"] in competitors for p in prices):
            cases.append(price_case(category, prices, competitors, levels, source.pricing_rules(), today))
    for supplier_id in suppliers_to_show(source.terms(), levels, today):
        cases.append(order_case(source.terms(supplier_id), levels, source.replenishment_rules(), today))
    return cases


def build() -> dict:
    return {"$comment": COMMENT, "cases": build_from(_seed())}


def render() -> str:
    return json.dumps(build(), ensure_ascii=False, indent=2) + "\n"


def main(argv: list[str]) -> int:
    text = render()
    if "--check" in argv:
        held = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if held != text:
            print("cases.json differs from what make_cases.py would write. Run make_cases.py.")
            return 1
        print("cases.json is what make_cases.py would write.")
        return 0
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {OUT.name}: {len(json.loads(text)['cases'])} cases")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
