"""Product Data Check, the code step: every listing compared with its supplier specification, by code.
Plain Python, standard library only.

compare(listings, specs) takes what list_product_listings returns and a list of what get_supplier_specification
returned for each line (in any order), and gives back the body save_product_data_check accepts:
findings (sku, attribute, kind, listing_value, specification_value), category, summary, drafted_by.

Four attributes are compared, exactly as text: net_quantity, pack_size, allergen_statement, country_of_origin.
- missing: the listing has nothing for the attribute and the specification has a value
- does_not_match: both have a value and they differ
No allergen is worked out and no listing is corrected. A line with no specification read is reported, never guessed.
"""
import json

ATTRIBUTES = ["net_quantity", "pack_size", "allergen_statement", "country_of_origin"]


def compare(listings, specs, category=""):
    by_sku = {}
    for s in specs:
        if isinstance(s, str):
            s = json.loads(s)
        if isinstance(s, dict) and s.get("sku"):
            by_sku[s["sku"]] = s
    findings, not_read, n = [], [], 0
    for row in sorted(listings["items"], key=lambda r: r["sku"]):
        if category and row.get("category") != category:
            continue
        n += 1
        spec = by_sku.get(row["sku"])
        if spec is None:
            not_read.append(row["sku"])
            continue
        for a in ATTRIBUTES:
            listed = str((row.get("attributes") or {}).get(a) or "").strip()
            given = str(spec.get(a) or "").strip()
            if not given or listed == given:
                continue
            findings.append({"sku": row["sku"], "attribute": a, "kind": "missing" if not listed else "does_not_match",
                             "listing_value": listed, "specification_value": given})
    if not_read:
        raise SystemExit("No specification was read for %d of %d lines: %s. Nothing was checked." % (len(not_read), n, ", ".join(not_read)))
    by_attr = {}
    for f in findings:
        by_attr[f["attribute"]] = by_attr.get(f["attribute"], 0) + 1
    missing = len([f for f in findings if f["kind"] == "missing"])
    summary = "%d listings compared with their specifications, four attributes each. %d findings: %d missing and %d that do not match." % (
        n, len(findings), missing, len(findings) - missing)
    if findings:
        summary += " By attribute: %s." % ", ".join("%s %d" % (a, by_attr[a]) for a in ATTRIBUTES if a in by_attr)
        allergen = [f["sku"] for f in findings if f["attribute"] == "allergen_statement"]
        if allergen:
            summary += " The allergen findings, for the content lead to see first: %s." % ", ".join(allergen)
    return {"findings": findings, "category": category, "summary": summary, "drafted_by": "Product Data Check (code step)"}


if __name__ == "__main__":
    import sys
    listings = json.load(open(sys.argv[1], encoding="utf-8"))
    specs = [json.load(open(p, encoding="utf-8")) for p in sys.argv[2:]]
    print(json.dumps(compare(listings, specs), indent=1))
