"""Builds cases.json for the product data desk from the invented retailer's own records.

Nineteen cases, as the retailer's catalogue system holds them when the retailer's date is 24 November 2026:
the six new products that have no description yet, and a listing check for each of thirteen listings (the ten
that have an attribute missing or not matching the supplier's specification, and three that are clean). Nothing
is typed here by hand: listings, specifications, image descriptions and the style guide come from the seed of the
service in ../../../demo-retailer. No server is started.

Each case carries the records its agent needs, because the desk's agents work from the message alone. A new
product carries the supplier's specification, each image as a description in words, and the style guide. A
listing check carries the listing and the supplier's specification, one under the other, and the three rules of
the style guide on these attributes. The desk holds no images.

The service's own answer set (which listings were planted, which image description differs) is never read. The
thirteen listings are named below by line id, in order of line id, so that the clean ones do not stand apart.

Usage, from anywhere:
    python make_cases.py           writes cases.json beside this file
    python make_cases.py --check   exits 1 if cases.json differs from what would be written

The test demo-retailer/tests/test_product_data_desk_cases.py runs the same comparison, and builds every case
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
# The thirteen listings to check, in order of line id: ten with one attribute missing or not matching, three clean.
LISTINGS = ["AG-4401", "AG-4407", "AG-4412", "AG-4413", "BK-5703", "CH-5506", "CH-5507", "DR-5902", "DR-5905", "FP-5804",
            "FZ-5602", "HH-6104", "PC-6603"]

KIND_NEW = "New product"
KIND_CHECK = "Listing check"

COMMENT = ("Nineteen invented cases for the demo: six new products with no description yet, and a listing check for each of "
           "thirteen listings. Made by make_cases.py from the records the invented retailer (demo-retailer) holds at "
           "retailer date 2026-11-24. Do not edit by hand: change the service's seed and run the script. Rowanmere Group, "
           "its suppliers, its products and every record are invented.")

# The four attributes, each with the short label a case gives it: the allergen statement is "Allergens" and the
# country of origin is "Origin", so that a label stays on one line beside its value.
ATTRIBUTES = [("net_quantity", "Net quantity"), ("pack_size", "Pack size"), ("allergen_statement", "Allergens"),
              ("country_of_origin", "Origin")]
# The rules of the style guide on the four attributes: what a listing carries.
ATTRIBUTE_RULES = ["PS-5", "PS-6", "PS-7"]
NOTHING = "(nothing)"
ORDINALS = ["First", "Second", "Third", "Fourth"]


def words(value: str) -> str:
    return value.replace("_", " ")


def sentence_case(value: str) -> str:
    """Ambient grocery, for ambient_grocery."""
    text = words(value)
    return text[:1].upper() + text[1:]


def spec_ref(spec: dict) -> str:
    return f"{spec['specification_ref']}, version {spec['version']}"


def guide_ref(guide: dict) -> str:
    return f"{guide['document']}, version {guide['version']}"


def guide_lines(guide: dict, only: list | None = None) -> list:
    """The rules as the guide gives them. A rule is written "PS-1 Length: text"."""
    return [f"{r['rule_id']} {r['title']}: {r['text']}" for r in guide["rules"] if only is None or r["rule_id"] in only]


def spec_block(spec: dict, full: bool) -> list:
    lines = ["THE SUPPLIER'S SPECIFICATION", f"Specification: {spec_ref(spec)}, issued {spec['issued_on']}",
             f"Supplier: {spec['supplier_id']}, {spec['supplier_name']}", f"Product name: {spec['product_name']}"]
    lines += [f"{label}: {spec[key]}" for key, label in ATTRIBUTES]
    if full:
        lines += [f"Storage: {spec['storage']}", f"Shelf life: {spec['shelf_life_days']} days",
                  f"Claims: {', '.join(spec['claims']) or 'none'}"]
    return lines


# ---------------------------------------------------------------- a new product with no description

def new_text(listing: dict, spec: dict, images: list, images_note: str, guide: dict) -> str:
    lines = ["THE NEW PRODUCT", f"Line: {listing['sku']}", f"Name: {listing['name']}", f"Brand: {listing['brand']}",
             f"Category: {words(listing['category'])}", f"Listed: {listing['listed_on']}", f"Status: {words(listing['status'])}",
             f"Age restricted: {'yes' if listing['age_restricted'] else 'no'}"]
    lines += spec_block(spec, full=True)
    # The note is the catalogue system's own. It speaks of itself as "this service": the desk names the system.
    lines += ["THE IMAGES, AS DESCRIPTIONS IN WORDS", images_note.replace("This service holds", "The catalogue system holds")]
    lines += [f"{ORDINALS[n]} image: {text}" for n, text in enumerate(images)]
    lines += ["THE STYLE GUIDE", f"Document: {guide_ref(guide)}"] + guide_lines(guide)
    lines.append(f"Not decided by the guide: {guide['what_the_guide_does_not_decide']}")
    return "\n".join(lines)


def new_case(listing: dict, spec: dict, images: list, images_note: str, guide: dict) -> dict:
    return {"title": f"{listing['sku']} {listing['name']}", "kind": KIND_NEW, "supplier": spec["supplier_name"],
            "category": sentence_case(listing["category"]), "against": f"{spec_ref(spec)} · {guide_ref(guide)}",
            "received_on": listing["listed_on"], "text": new_text(listing, spec, images, images_note, guide),
            "arrived_via": "feed"}


# ---------------------------------------------------------------- a listing set against its specification

def check_text(listing: dict, spec: dict, guide: dict) -> str:
    lines = ["THE LISTING", f"Line: {listing['sku']}", f"Name: {listing['name']}", f"Brand: {listing['brand']}",
             f"Category: {words(listing['category'])}", f"Status: {words(listing['status'])}"]
    lines += [f"{label}: {listing['attributes'][key] or NOTHING}" for key, label in ATTRIBUTES]
    lines += spec_block(spec, full=False)
    lines += ["THE RULES FOR THESE ATTRIBUTES", f"Document: {guide_ref(guide)}"] + guide_lines(guide, ATTRIBUTE_RULES)
    return "\n".join(lines)


def check_case(listing: dict, spec: dict, guide: dict, checked_on: str) -> dict:
    return {"title": f"{listing['sku']} {listing['name']}", "kind": KIND_CHECK, "supplier": spec["supplier_name"],
            "category": sentence_case(listing["category"]), "against": spec_ref(spec), "received_on": checked_on,
            "text": check_text(listing, spec, guide), "arrived_via": "feed"}


# ---------------------------------------------------------------- the records

class SeedSource:
    """The records as the service's seed holds them. The test has the same readers over the API."""

    def __init__(self, data: dict):
        self.data = data

    def awaiting(self) -> list:
        """The new products with no description yet, in order of line id, each with its image descriptions."""
        rows = [x for x in self.data["catalogue_products"].values() if x["new_product"] and x["status"] == "awaiting_description"]
        return sorted(({"sku": x["sku"], "image_descriptions": x["image_descriptions"]} for x in rows), key=lambda x: x["sku"])

    def images_note(self) -> str:
        from retailer.seed_catalogue import IMAGES_NOTE  # noqa: E402

        return IMAGES_NOTE

    def listing(self, sku: str) -> dict:
        return self.data["catalogue_products"][sku]

    def spec(self, sku: str) -> dict:
        return self.data["supplier_specs"][sku]

    def guide(self) -> dict:
        from retailer.seed_catalogue import STYLE_GUIDE  # noqa: E402

        return STYLE_GUIDE


def cases_from(source) -> list:
    guide = source.guide()
    note = source.images_note()
    cases = [new_case(source.listing(x["sku"]), source.spec(x["sku"]), x["image_descriptions"], note, guide)
             for x in source.awaiting()]
    cases += [check_case(source.listing(sku), source.spec(sku), guide, RETAILER_DATE.isoformat()) for sku in LISTINGS]
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
