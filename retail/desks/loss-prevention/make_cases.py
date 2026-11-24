"""Builds cases.json for the loss prevention desk from the invented retailer's own records.

Fourteen cases, as the retailer's systems hold them when the retailer's date is 24 November 2026:
the four orders flagged for a fraud review, a till audit for each of four sites (the site with the
most rows outside the till rules, two sites with two such rows each, and a site with none), and six
stock loss cases (the two stores beyond tolerance, the nearest store within it, and the three lines
beyond tolerance). Nothing is typed here by hand: orders, earlier orders, till rows, till rules, stock
counts and the tolerance come from the seed of the service in ../../../demo-retailer. No server is
started.

Each case carries the records its agent needs, because the desk's agents work from the message
alone. A till audit is one site's rows for the period, not the whole month: a month of every site is
too long for one case. The service's own answer sets (which rows were planted, which stores and lines
are beyond tolerance, what a review should propose) are never read.

A customer appears by id only, and a cashier and an approver by the id the till row gives.

Usage, from anywhere:
    python make_cases.py           writes cases.json beside this file
    python make_cases.py --check   exits 1 if cases.json differs from what would be written

The test demo-retailer/tests/test_loss_prevention_desk_cases.py runs the same comparison, and
builds every case again from what the service returns.
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
PERIOD = "2026-10"
ORDERS = ["RM-58192", "RM-58194", "RM-58196", "RM-58198"]
# The site with the most rows outside the rules, two sites with two such rows each, and a site with none.
TILL_SITES = ["S-106", "S-101", "S-104", "R-117"]
# The two stores beyond tolerance, then the nearest store within it.
STOCK_STORES = ["S-103", "S-106", "S-102"]
STOCK_LINES = ["DR-5905", "HH-6105", "PC-6604"]
TOP_LINES = 10

KIND_ORDER = "Flagged order"
KIND_TILL = "Till audit"
KIND_STOCK = "Stock loss"

COMMENT = ("Fourteen invented cases for the demo: four orders flagged for a fraud review, four till audits (one site each) and "
           "six stock loss cases (three stores and three lines). Made by make_cases.py from the records the invented retailer "
           "(demo-retailer) holds at retailer date 2026-11-24. Do not edit by hand: change the service's seed and run the "
           "script. Rowanmere Group, its customers, its colleagues and every record are invented.")

NO_LINE = "A till row carries no line, so none of these can be tied to a line that lost stock."
AGAINST_ORDERS = "The customer's earlier orders"


def money(v) -> str:
    return f"{v:,.2f}"


def qty(v) -> str:
    return f"{v:,}"


def words(value: str) -> str:
    return value.replace("_", " ")


def percent(v) -> str:
    """35 for 35.0, 2.44 for 2.44: a percent as a person writes it."""
    return f"{v:.2f}".rstrip("0").rstrip(".") if v != int(v) else str(int(v))


def case_number(prefix: str, period: str, what: str) -> str:
    """TA-2610-S106, SL-2610-DR5905: a number for a case the retailer gives no number of its own."""
    return f"{prefix}-{period[2:4]}{period[5:7]}-{what.replace('-', '')}"


def site_label(site: dict) -> str:
    return f"{site['site_id']} {site['name']}"


def short_name(site: dict) -> str:
    """Causeway Park, for Rowanmere Market Causeway Park."""
    for brand in ("Rowanmere Market ", "Rowanmere Kitchen "):
        if site["name"].startswith(brand):
            return site["name"][len(brand):]
    return site["name"]


# ---------------------------------------------------------------- a flagged order

def seen(first: bool, first_words: str) -> str:
    return first_words if first else "used on earlier orders"


def earlier_line(o: dict) -> str:
    parts = [o["placed_on"], f"USD {money(o['total'])}", o["items"], words(o["delivery_method"])]
    if o["service"] != o["delivery_method"]:
        parts.append(words(o["service"]))
    parts += [o["address_ref"] or "no address", o["device_ref"], o["card_ref"], o["outcome"]]
    line = f"{o['order_number']}: " + ", ".join(parts)
    if o.get("refund"):
        r = o["refund"]
        line += f". Refund {r['where']}: USD {money(r['amount'])} on {r['date']} at {r['site_id']}, till row {r['till_row_id']}"
    return line


def till_row_line(r: dict, reason: bool = False) -> str:
    """One till row as the records give it. A cashier and an approver are ids.

    The reason typed at the till is given only where a case needs it (the refund on a customer's earlier order).
    No till rule turns on it, so an audit's rows leave it out and stay short enough to scan.
    """
    why = f", reason: {r['reason']}" if reason else ""
    head = f"{r['row_id']}: {r['date']} {r['time']}, till {r['till']}, cashier {r['cashier_id']}, "
    if r["kind"] == "refund":
        return (head + f"refund of {money(r['amount'])}, approver {r['approver_id'] or 'none'}, "
                f"receipt {r['original_receipt'] or 'none'}{why}")
    if r["kind"] == "discount":
        return (head + f"discount of {money(r['amount'])}, {percent(r['discount_percent'])} percent of {money(r['sale_amount'])}, "
                f"reason code {r['reason_code'] or 'none'}")
    when = "after payment" if r["after_payment"] else "before payment"
    return head + f"void of {money(r['amount'])}, {when}, second person {r['approver_id'] or 'none'}{why}"


def order_text(o: dict, history: dict, refund_rows: list) -> str:
    """One flagged order with the customer's earlier orders, any account change, and the till row of an earlier refund."""
    d, p = o["delivery"], o["payment"]
    cc = d["method"] == "click_and_collect"
    lines = ["THE ORDER", f"Order: {o['order_number']}", f"Placed: {o['placed_on']} at {o['placed_at'][11:16]}, by {o['channel']}",
             f"Customer: {o['customer_id']}", f"Status: {words(o['status'])}", "ORDER LINES"]
    lines += [f"{x['line_no']}. {x['item']}: {qty(x['quantity'])} at {money(x['unit_price'])}, amount {money(x['amount'])}"
              for x in o["lines"]]
    lines += [f"Goods: USD {money(o['goods_total'])}", f"Delivery charge: USD {money(o['delivery_charge'])}",
              f"Total: USD {money(o['total'])}"]
    if cc:
        lines += [f"Delivery: click and collect at {d['collect_site_id']}", f"Collector: {d['collector']}",
                  "Address: none, the order is collected"]
    else:
        lines += [f"Delivery: home delivery, {words(d['service'])}",
                  f"Address: {d['address_ref']}, {seen(d['address_first_used_on_this_order'], 'first used on this order')}"]
    lines += [f"Device: {o['device_ref']}, {seen(o['device_first_seen_on_this_order'], 'first seen on this order')}",
              f"Card: {p['card_ref']}, {seen(p['card_first_used_on_this_order'], 'first used on this order')}",
              "THE FLAG", f"Flagged: {o['flag']['flagged_on']}", f"Screening reasons: {'; '.join(o['flag']['reasons'])}",
              f"Screening note: {o['flag']['screening_note']}",
              "THE CUSTOMER'S EARLIER ORDERS", f"Earlier orders: {len(history['orders'])}",
              f"Average total: USD {money(history['average_total'])}", f"Highest total: USD {money(history['highest_total'])}"]
    lines += [earlier_line(x) for x in history["orders"]]
    lines.append("ACCOUNT CHANGES")
    lines += [f"{c['date']}: {c['change']}" for c in history["account_changes"]] or ["None."]
    if refund_rows:
        lines.append("TILL ROW OF THE EARLIER REFUND")
        lines += [till_row_line(r, reason=True) for r in refund_rows]
    return "\n".join(lines)


def order_case(o: dict, history: dict, refund_rows: list) -> dict:
    d = o["delivery"]
    site = f"Online shop, collect at {d['collect_site_id']}" if d["method"] == "click_and_collect" else "Online shop"
    return {"title": f"{o['order_number']} order of USD {money(o['total'])}", "kind": KIND_ORDER, "site": site,
            "about": f"USD {money(o['total'])}", "period": f"Placed {o['placed_on']}", "rules": AGAINST_ORDERS,
            "received_on": o["placed_on"], "text": order_text(o, history, refund_rows), "arrived_via": "feed"}


# ---------------------------------------------------------------- a till audit of one site

def rules_block(doc: dict) -> list:
    lines = ["THE TILL RULES", f"Document: {doc['document']}, version {doc['version']}"]
    for r in doc["rules"]:
        lines.append(f"{r['rule_id']}: {r['text']}{on_the_limit(r)}")
    lines.append(f"Not decided by the rules: {doc['what_the_rules_do_not_decide']}")
    return lines


def on_the_limit(rule: dict) -> str:
    """What the rule's test says about a row exactly on the limit: its last sentence, when it has more than one.

    The first sentence of the test names the fields of a row as the system spells them. The case gives each row in
    plain words, so that sentence is left out.
    """
    parts = rule["how_to_test"].split(". ", 1)
    return f" {parts[1]}" if len(parts) == 2 else ""


def till_text(site: dict, period: str, rows: list, doc: dict) -> str:
    lines = ["THE AUDIT", f"Site: {site['site_id']}, {site['name']}", f"Period: {period}", f"Rows: {len(rows)}"]
    lines += rules_block(doc)
    lines.append("THE TILL ROWS")
    lines += [till_row_line(r) for r in rows]
    return "\n".join(lines)


def till_case(site: dict, period: str, rows: list, doc: dict) -> dict:
    number = case_number("TA", period, site["site_id"])
    return {"title": f"{number} {short_name(site)}, {len(rows)} till rows", "kind": KIND_TILL, "site": site_label(site),
            "about": f"{len(rows)} till rows", "period": f"Period {period}", "rules": f"{doc['document']}, version {doc['version']}",
            "received_on": max(r["date"] for r in rows), "text": till_text(site, period, rows, doc), "arrived_via": "feed"}


# ---------------------------------------------------------------- stock loss: a store, or a line

def tolerance_block(doc: dict) -> list:
    lines = ["THE TOLERANCE", f"Document: {doc['document']}, version {doc['version']}"]
    lines += [f"{r['rule_id']}: {r['text']}" for r in doc["rules"]]
    lines.append(f"Not decided by the tolerance: {doc['what_the_tolerance_does_not_decide']}")
    return lines


def till_figures(rows: list) -> list:
    """Counts and totals by kind, and nothing else of a till row."""
    out = []
    for kind, label in (("refund", "Refunds"), ("void", "Voids"), ("discount", "Discounts")):
        mine = [r for r in rows if r["kind"] == kind]
        out.append(f"{label}: {len(mine)}, USD {money(round(sum(r['amount'] for r in mine), 2))}")
    return out


def store_text(site: dict, count: dict, count_rows: list, doc: dict, till_rows: list) -> str:
    top = sorted(count_rows, key=lambda r: (-r["loss_value"], r["sku"]))[:TOP_LINES]
    lines = ["THE STOCK COUNT", f"Count: {count['count_id']}", f"Store: {site['site_id']}, {site['name']}",
             f"Period: {count['period']}, counted {count['counted_on']}", f"Lines counted: {count['lines_counted']}",
             f"Sales value: USD {money(count['sales_value'])}", f"Loss units: {qty(count['loss_units'])}",
             f"Loss value: USD {money(count['loss_value'])}", f"Loss percent: {count['loss_percent']:.2f}"]
    lines += tolerance_block(doc)
    lines.append("LINES WITH THE MOST LOSS VALUE IN THIS STORE")
    lines += [f"{r['sku']} {r['name']}: {qty(r['loss_units'])} lost of {qty(r['book_units'])} on the books, loss value "
              f"{money(r['loss_value'])}, sales value {money(r['sales_value'])}" for r in top]
    lines.append("WHAT THE TILLS HOLD FOR THE STORE")
    lines += till_figures(till_rows) + [NO_LINE]
    return "\n".join(lines)


def store_case(site: dict, count: dict, count_rows: list, doc: dict, till_rows: list) -> dict:
    return {"title": f"{count['count_id']} {short_name(site)}, loss {count['loss_percent']:.2f} percent", "kind": KIND_STOCK,
            "site": site_label(site), "about": f"Loss {count['loss_percent']:.2f} percent of sales",
            "period": f"Period {count['period']}", "rules": f"{doc['document']}, version {doc['version']}",
            "received_on": count["counted_on"], "text": store_text(site, count, count_rows, doc, till_rows), "arrived_via": "feed"}


def line_text(line: dict, period: str, by_store: list, doc: dict) -> str:
    lines = ["THE LINE", f"Line: {line['sku']}, {line['name']}", f"Period: {period}, all counted stores together",
             f"Stores counted: {line['stores_counted']}", f"Units sold: {qty(line['units_sold'])}",
             f"Sales value: USD {money(line['sales_value'])}", f"Loss units: {qty(line['loss_units'])}",
             f"Loss value: USD {money(line['loss_value'])}", f"Loss percent: {line['loss_percent']:.2f}"]
    lines += tolerance_block(doc)
    lines.append("THE LINE BY STORE")
    lines += [f"{r['site_id']}: {qty(r['loss_units'])} lost of {qty(r['book_units'])} on the books, loss value "
              f"{money(r['loss_value'])}, sales value {money(r['sales_value'])}" for r in sorted(by_store, key=lambda r: r["site_id"])]
    return "\n".join(lines)


def line_case(line: dict, period: str, counted_on: str, by_store: list, doc: dict) -> dict:
    number = case_number("SL", period, line["sku"])
    return {"title": f"{number} {line['name']}, loss {line['loss_percent']:.2f} percent", "kind": KIND_STOCK, "site": "All stores",
            "about": f"Loss {line['loss_percent']:.2f} percent of sales", "period": f"Period {period}",
            "rules": f"{doc['document']}, version {doc['version']}", "received_on": counted_on,
            "text": line_text(line, period, by_store, doc), "arrived_via": "feed"}


# ---------------------------------------------------------------- the records

class SeedSource:
    """The records as the service's seed holds them. The test has the same readers over the API."""

    def __init__(self, data: dict):
        self.data = data

    def site(self, site_id: str) -> dict:
        return self.data["sites"][site_id]

    def order(self, number: str) -> dict:
        return self.data["orders"][number]

    def history(self, customer_id: str) -> dict:
        """The customer's orders that are not flagged, newest first, with their average and highest total."""
        c = self.data["customers"][customer_id]
        current = [{"order_number": o["order_number"], "placed_on": o["placed_on"], "total": o["total"],
                    "items": ", ".join(f"{x['quantity']} x {x['item']}" for x in o["lines"]),
                    "delivery_method": o["delivery"]["method"], "service": o["delivery"]["service"],
                    "address_ref": o["delivery"]["address_ref"], "device_ref": o["device_ref"],
                    "card_ref": o["payment"]["card_ref"], "outcome": o["status"], "refund": None}
                   for o in self.data["orders"].values() if o["customer_id"] == customer_id and not o["flag"]]
        rows = sorted(current + list(c["earlier_orders"]), key=lambda x: (x["placed_on"], x["order_number"]), reverse=True)
        totals = [x["total"] for x in rows]
        return {"orders": rows, "account_changes": c["account_changes"],
                "average_total": round(sum(totals) / len(totals) + 1e-9, 2) if totals else 0.0,
                "highest_total": max(totals) if totals else 0.0}

    def till_row(self, row_id: str):
        return self.data["till_rows"].get(row_id)

    def till_rows(self, period: str, site_id: str) -> list:
        return sorted((r for r in self.data["till_rows"].values() if r["date"].startswith(period) and r["site_id"] == site_id),
                      key=lambda r: r["row_id"])

    def till_rules(self) -> dict:
        from retailer.seed_tills import RULES_DOCUMENT  # noqa: E402

        return RULES_DOCUMENT

    def tolerance(self) -> dict:
        from retailer.seed_stock import SHRINK_TOLERANCE  # noqa: E402

        return SHRINK_TOLERANCE

    def count(self, period: str, site_id: str) -> dict:
        found = next(c for c in self.data["stock_counts"].values() if c["period"] == period and c["site_id"] == site_id)
        return {k: v for k, v in found.items() if k != "rows"}

    def count_rows(self, period: str, site_id: str) -> list:
        found = next(c for c in self.data["stock_counts"].values() if c["period"] == period and c["site_id"] == site_id)
        return [{"site_id": site_id, **r} for r in found["rows"]]

    def line(self, period: str, sku: str) -> dict:
        """One line, all counted stores together, added up the way the service adds it."""
        rows = self.line_rows(period, sku)
        sales = round(sum(r["sales_value"] for r in rows), 2)
        loss = round(sum(r["loss_value"] for r in rows), 2)
        return {"sku": sku, "name": rows[0]["name"], "units_sold": sum(r["units_sold"] for r in rows), "sales_value": sales,
                "loss_units": sum(r["loss_units"] for r in rows), "loss_value": loss, "stores_counted": len(rows),
                "loss_percent": round(loss / sales * 100 + 1e-9, 2) if sales else 0.0}

    def line_rows(self, period: str, sku: str) -> list:
        return [{"site_id": c["site_id"], **r} for c in self.data["stock_counts"].values() if c["period"] == period
                for r in c["rows"] if r["sku"] == sku]


def refund_rows_of(history: dict, source) -> list:
    """The till rows the earlier orders point to, in the order of the orders."""
    rows = [source.till_row(o["refund"]["till_row_id"]) for o in history["orders"] if o.get("refund")]
    return [r for r in rows if r]


def cases_from(source) -> list:
    cases = []
    for number in ORDERS:
        o = source.order(number)
        history = source.history(o["customer_id"])
        cases.append(order_case(o, history, refund_rows_of(history, source)))
    rules = source.till_rules()
    for site_id in TILL_SITES:
        cases.append(till_case(source.site(site_id), PERIOD, source.till_rows(PERIOD, site_id), rules))
    tolerance = source.tolerance()
    for site_id in STOCK_STORES:
        cases.append(store_case(source.site(site_id), source.count(PERIOD, site_id), source.count_rows(PERIOD, site_id), tolerance,
                                source.till_rows(PERIOD, site_id)))
    counted_on = source.count(PERIOD, STOCK_STORES[0])["counted_on"]
    for sku in STOCK_LINES:
        cases.append(line_case(source.line(PERIOD, sku), PERIOD, counted_on, source.line_rows(PERIOD, sku), tolerance))
    return cases


def _seed() -> dict:
    """The service's starting data for the retailer date. Imported, never served."""
    if str(RETAILER) not in sys.path:
        sys.path.insert(0, str(RETAILER))
    from retailer.seed import build_all  # noqa: E402

    return build_all(RETAILER_DATE)


def build() -> dict:
    return {"$comment": COMMENT, "cases": cases_from(SeedSource(_seed()))}


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
