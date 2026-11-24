"""Builds cases.json for the recall desk from the invented retailer's own records.

Three cases, as the retailer's stock system holds them when the retailer's date is 24 November 2026:
the recalled batch BT-44031, and two more recalls with a smaller reach. The seed holds one recalled
batch in its starting data. The two others are the first two recalls the service's own seed makes when a
recall arrives (the "recalled-batch" arrival): BT-90001 and BT-90002. Nothing is typed here by hand:
the batch record, the recall, the stores, the orders and the recall procedure come from the seed of the
service in ../../../demo-retailer. No server is started.

Each case carries the records its agent needs, because the desk's agent works from the message alone:
the recall in the supplier's own words, the batch record, every store the batch was delivered to and
every online order it was picked for, what is not on the batch record (another batch of the same line,
and orders that hold the line and were not picked from this batch), and the recall procedure.

A customer appears by name, order number and the address for messages, which ends in .invalid. Nothing
else about a customer is carried: no customer id, no card, no device and no delivery address.

Usage, from anywhere:
    python make_cases.py           writes cases.json beside this file
    python make_cases.py --check   exits 1 if cases.json differs from what would be written

The test demo-retailer/tests/test_recall_desk_cases.py runs the same comparison, and builds every case
again from what the service returns.
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
# The recalled batch of the starting data, then the recalls that arrive: the service numbers them from BT-90001.
ARRIVALS = 2
KIND = "Recalled batch"

COMMENT = ("Three invented cases for the demo: the recalled batch BT-44031 and two recalls with a smaller reach, BT-90001 and "
           "BT-90002, which are the first two recalls the retailer's seed makes when one arrives. Made by make_cases.py "
           "from the records the invented retailer (demo-retailer) holds at retailer date 2026-11-24. Do not edit by hand: "
           "change the service's seed and run the script. Rowanmere Group, its suppliers, its customers, its colleagues "
           "and every record are invented.")


def words(value: str) -> str:
    return value.replace("_", " ")


def count(n: int, one: str, many: str | None = None) -> str:
    return f"{n} {one if n == 1 else (many or one + 's')}"


def join(items: list) -> str:
    """S-102 and S-106. S-101, S-104 and S-105."""
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def holds(order: dict, skus: set) -> list:
    return [x for x in order["lines"] if x["sku"] in skus]


def lines_that_carry(batch: dict) -> set:
    """The order lines a unit of this batch can go out as: the line itself, and any line the batch's note names."""
    out = {batch["sku"]}
    for word in batch["note"].replace("(", " ").replace(")", " ").replace(",", " ").split():
        if len(word) == 7 and word[2] == "-" and word[:2].isalpha() and word[3:].isdigit():
            out.add(word)
    return out


def recall_text(batch: dict, sites: dict, orders: dict, others: list, strays: list) -> str:
    r = batch["recall"]
    fc = batch["fulfilment_centre"]
    lines = ["THE RECALL", f"Batch: {batch['batch_id']}", f"Product: {batch['sku']}, {batch['name']}",
             f"Supplier: {batch['supplier_id']}, {batch['supplier_name']}", f"Raised: {r['raised_on']}, by {r['raised_by']}",
             f"Reason: {r['reason']}", f"Supplier asks: {r['instruction_from_the_supplier']}", f"Remedy: {r['customer_remedy']}",
             f"Customer care: {r['customer_care_contact']}",
             "THE BATCH RECORD", f"Received: {batch['received_on']}, {batch['units_received']:,} units",
             f"Best before: {batch['best_before']}", f"Status: {words(batch['status'])}",
             f"Centre: {fc['units_received']} received at the fulfilment centre, {fc['units_picked_for_orders']} picked for orders, "
             f"{fc['units_on_hand']} on hand"]
    if batch["note"]:
        lines.append(f"Note: {batch['note']}")
    lines.append("STORES THE BATCH WAS DELIVERED TO")
    for s in batch["stores"]:
        site = sites[s["site_id"]]
        lines.append(f"{s['site_id']}: {site['name']}, {site['town']}. Delivered {s['delivered_on']}: {s['units_delivered']} "
                     f"units, {s['units_sold']} sold, {s['units_on_hand']} on hand. Area manager {site['area_manager']}")
    if not batch["stores"]:
        lines.append("None.")
    lines.append("ONLINE ORDERS THE BATCH WAS PICKED FOR")
    for o in batch["online_orders"]:
        order = orders[o["order_number"]]
        lines.append(f"{o['order_number']}: {order['customer_name']}, {order['customer_email']}. {words(order['status']).capitalize()}. "
                     f"Picked {o['picked_on']}: {count(o['units'], 'unit')}, went out as {o['went_out_as']}")
    if not batch["online_orders"]:
        lines.append("None.")
    lines.append("NOT ON THE BATCH RECORD")
    for b in others:
        stores = join([s["site_id"] for s in b["stores"]]) if b["stores"] else "no store"
        picked = f"picked for {count(len(b['online_orders']), 'online order')}" if b["online_orders"] else "picked for no order"
        lines.append(f"{b['batch_id']}: another batch of {b['sku']}, received {b['received_on']}, {words(b['status'])}, not recalled. "
                     f"Delivered to {stores}, and {picked}")
    for o in strays:
        held = join([f"{x['quantity']} x {x['sku']} {x['item']}" for x in o["mine"]])
        lines.append(f"{o['order_number']}: holds {held}, status {words(o['status'])}. Not picked from this batch")
    if not others and not strays:
        lines.append("Nothing else holds this line.")
    return "\n".join(lines)


def procedure_block(procedure: dict) -> list:
    lines = ["THE RECALL PROCEDURE", f"Document: {procedure['document']}, version {procedure['version']}"]
    lines += [f"{s['step']}: {s['text']}" for s in procedure["steps"]]
    return lines


def recall_case(batch: dict, sites: dict, orders: dict, others: list, strays: list, procedure: dict) -> dict:
    reach = f"{count(len(batch['stores']), 'store')}, {count(len(batch['online_orders']), 'order')}"
    text = "\n".join([recall_text(batch, sites, orders, others, strays)] + procedure_block(procedure))
    return {"title": f"{batch['batch_id']} {batch['name']}", "kind": KIND, "supplier": batch["supplier_name"],
            "reach": reach, "against": f"{procedure['document']}, version {procedure['version']}",
            "received_on": batch["recall"]["raised_on"], "text": text, "arrived_via": "feed"}


# ---------------------------------------------------------------- the records

class SeedSource:
    """The records as the service's seed holds them. The test has the same readers over the API."""

    def __init__(self, data: dict):
        self.data = data
        from retailer.seed_stock import sim_recall  # noqa: E402

        # The recalls that arrive, as the service makes them: the first arrival is BT-90001.
        for n in range(ARRIVALS):
            sim_recall(data, RETAILER_DATE, n % 4, f"BT-{90001 + n}")

    def recalled(self) -> list:
        """The recalled batches, the starting one first, then the arrivals in order."""
        return sorted(b["batch_id"] for b in self.data["batches"].values() if b["status"] == "recalled")

    def batch(self, batch_id: str) -> dict:
        return self.data["batches"][batch_id]

    def batches_of(self, sku: str) -> list:
        return sorted((b for b in self.data["batches"].values() if b["sku"] == sku), key=lambda b: b["batch_id"])

    def site(self, site_id: str) -> dict:
        return self.data["sites"][site_id]

    def order(self, number: str) -> dict:
        return self.data["orders"][number]

    def order_numbers(self) -> list:
        return sorted(self.data["orders"])

    def procedure(self) -> dict:
        from retailer.seed_stock import RECALL_PROCEDURE  # noqa: E402

        return RECALL_PROCEDURE


def cases_from(source) -> list:
    procedure = source.procedure()
    numbers = source.order_numbers()
    cases = []
    for batch_id in source.recalled():
        batch = source.batch(batch_id)
        sites = {s["site_id"]: source.site(s["site_id"]) for s in batch["stores"]}
        on_record = [o["order_number"] for o in batch["online_orders"]]
        orders = {n: source.order(n) for n in on_record}
        # Another batch of the same line, and orders that hold the line and are not on this batch's record.
        others = [b for b in source.batches_of(batch["sku"]) if b["batch_id"] != batch_id and b["status"] != "recalled"]
        carried = lines_that_carry(batch)
        strays = []
        for n in numbers:
            if n in on_record:
                continue
            o = source.order(n)
            mine = holds(o, carried)
            if mine:
                strays.append({"order_number": n, "status": o["status"], "mine": mine})
        cases.append(recall_case(batch, sites, orders, others, strays, procedure))
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
