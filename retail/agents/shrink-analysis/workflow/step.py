"""Shrink Analysis, the code step: every store set against the store tolerance and every line against the line
tolerance, by code. Plain Python, standard library only.

analyse(by_store, by_line, tolerance, tills) takes what list_stock_counts returns with the views by_store and by_line,
what get_shrink_tolerance returns, and what list_till_entries returns for the same period, and gives back the body
save_shrink_analysis accepts: stores_beyond_tolerance, lines_beyond_tolerance, summary, drafted_by.

As the Stock Loss Tolerance version 1.4 states it:
- SL-1: a store is beyond tolerance when its loss value is more than the store tolerance (1.5 percent) of its sales value
- SL-2: a line, all counted stores together, when its loss value is more than the line tolerance (2.5 percent)
- exactly on the tolerance is within it
Both tolerances are read from get_shrink_tolerance. The loss percent saved is the one the count gives.
The till rows are added up by store and kind as figures only. No cashier id and no approver id leaves this code.
"""
import json
from fractions import Fraction


def _f(x):
    return Fraction(str(x))


def _money(x):
    return "{:,.2f}".format(float(x))


def analyse(by_store, by_line, tolerance, tills=None):
    store_tol, line_tol = _f(tolerance["store_tolerance_percent"]), _f(tolerance["line_tolerance_percent"])
    period = by_store.get("period", "")
    if tills and tills.get("total") is not None and int(tills["total"]) > len(tills.get("items", [])):
        raise SystemExit("Only %d of %s till rows of the period were read. Nothing was analysed." % (len(tills.get("items", [])), tills["total"]))

    def beyond(row, tol):
        return _f(row["loss_value"]) * 100 > tol * _f(row["sales_value"])

    held = {}
    for r in (tills or {}).get("items", []):
        d = held.setdefault(r["site_id"], {"refund": [0, Fraction(0)], "void": [0, Fraction(0)], "discount": [0, Fraction(0)]})
        if r["kind"] in d:
            d[r["kind"]][0] += 1
            d[r["kind"]][1] += _f(r["amount"])

    stores = sorted((r for r in by_store["items"] if beyond(r, store_tol)), key=lambda r: (-_f(r["loss_percent"]), r["site_id"]))
    within = sorted((r for r in by_store["items"] if not beyond(r, store_tol)), key=lambda r: (-_f(r["loss_percent"]), r["site_id"]))
    lines = sorted((r for r in by_line["items"] if beyond(r, line_tol)), key=lambda r: (-_f(r["loss_percent"]), r["sku"]))
    next_line = sorted((r for r in by_line["items"] if not beyond(r, line_tol)), key=lambda r: (-_f(r["loss_percent"]), r["sku"]))

    out_stores = []
    for r in stores:
        note = "Loss of %s on sales of %s, %.2f percent, %d units. The store tolerance is %s percent." % (
            _money(r["loss_value"]), _money(r["sales_value"]), float(r["loss_percent"]), r["loss_units"], tolerance["store_tolerance_percent"])
        t = held.get(r["site_id"])
        if t:
            note += " The tills hold for the period: %d refunds (%s), %d voids (%s), %d discounts (%s). A till row carries no line." % (
                t["refund"][0], _money(t["refund"][1]), t["void"][0], _money(t["void"][1]), t["discount"][0], _money(t["discount"][1]))
        out_stores.append({"site_id": r["site_id"], "loss_percent": r["loss_percent"], "note": note})
    out_lines = [{"sku": r["sku"], "loss_percent": r["loss_percent"],
                  "note": "%s: %d units lost, loss of %s on sales of %s, %.2f percent, %d stores counted. The line tolerance is %s percent." % (
                      r["name"], r["loss_units"], _money(r["loss_value"]), _money(r["sales_value"]), float(r["loss_percent"]),
                      r.get("stores_counted", 0), tolerance["line_tolerance_percent"])} for r in lines]
    summary = "Period %s. %d of %d stores are beyond the store tolerance of %s percent: %s." % (
        period, len(stores), len(by_store["items"]), tolerance["store_tolerance_percent"],
        ", ".join("%s (%.2f percent)" % (r["site_id"], float(r["loss_percent"])) for r in stores) or "none")
    if within:
        summary += " The nearest of the others is %s at %.2f percent, within tolerance." % (within[0]["site_id"], float(within[0]["loss_percent"]))
    summary += " %d of %d lines are beyond the line tolerance of %s percent: %s." % (
        len(lines), len(by_line["items"]), tolerance["line_tolerance_percent"],
        ", ".join("%s (%.2f percent)" % (r["sku"], float(r["loss_percent"])) for r in lines) or "none")
    if next_line:
        summary += " The next line is %s at %.2f percent, within tolerance." % (next_line[0]["sku"], float(next_line[0]["loss_percent"]))
    summary += " These are figures. They say nothing about why stock was lost."
    return {"stores_beyond_tolerance": out_stores, "lines_beyond_tolerance": out_lines, "summary": summary,
            "drafted_by": "Shrink Analysis (code step)"}


if __name__ == "__main__":
    import sys
    a, b, c, d = (json.load(open(p, encoding="utf-8")) for p in sys.argv[1:5])
    print(json.dumps(analyse(a, b, c, d), indent=1))
