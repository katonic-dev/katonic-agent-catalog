"""Inventory Forecasting, the code step: the replenishment plan worked out by code. Plain Python, standard library only.

make_plan(levels, terms, rules) takes what list_stock_levels, list_supply_terms and get_replenishment_rules return
and gives back {"positions": [...one row for every line...], "plan": {...the body save_replenishment_plan accepts...}}.

As the Replenishment Rules version 2.1 state them (RP-1 to RP-6):
- weekly forecast = units sold in the last four full weeks / 4; daily forecast = weekly / 7
- days of cover = stock on hand / daily forecast
- days to the next delivery = days from the retailer date to the earliest due date among open orders,
  or the lead time of the supplier when nothing is on order
- a line runs out when its cover is fewer days than that (exactly on does not run out)
- quantity = daily forecast x (lead time + target cover days) - on hand - units on order, rounded up to whole cases,
  never fewer than the minimum order of the supplier
- a line is overstocked above the overstock days (exactly on is not)
The target cover days (14) and the overstock days (56) are read from the rules.
"""
import json
from datetime import date
from fractions import Fraction


def _num(fr, places=1):
    return ("%%.%df" % places) % float(fr)


def make_plan(levels, terms, rules):
    today = date.fromisoformat(levels.get("retailer_date") or terms["retailer_date"])
    target, over = int(rules["target_cover_days"]), int(rules["overstock_days"])
    by_sku = {t["sku"]: t for t in terms["items"]}
    positions, lines, overstocked = [], [], []
    for row in sorted(levels["items"], key=lambda r: r["sku"]):
        t = by_sku[row["sku"]]
        on_hand = int(row["on_hand"])
        weekly = Fraction(int(row["units_sold_last_four_weeks"]), 4)
        daily = weekly / 7
        cover = Fraction(on_hand) / daily if daily else None
        on_order = sum(int(o["units"]) for o in t["open_orders"])
        dues = sorted(o["due_on"] for o in t["open_orders"])
        to_next = (date.fromisoformat(dues[0]) - today).days if dues else int(t["lead_time_days"])
        runs_out = cover is not None and cover < to_next
        is_over = cover is not None and cover > over
        cases = units = 0
        if runs_out:
            need = daily * (int(t["lead_time_days"]) + target) - on_hand - on_order
            cases = max(-((-need.numerator) // (need.denominator * int(t["case_size"]))), int(t["minimum_order_cases"]), 0)
            units = cases * int(t["case_size"])
        pos = {"sku": row["sku"], "name": row["name"], "supplier_id": t["supplier_id"], "supplier_name": t["supplier_name"],
               "supplier_in_purchasing": t.get("supplier_in_purchasing"), "on_hand": on_hand,
               "weekly_forecast": _num(weekly), "daily_forecast": _num(daily, 2), "days_of_cover": _num(cover) if cover is not None else "",
               "lead_time_days": int(t["lead_time_days"]), "units_on_order": on_order,
               "open_orders": [{"order_ref": o["order_ref"], "units": o["units"], "due_on": o["due_on"]} for o in t["open_orders"]],
               "days_to_next_delivery": to_next, "case_size": int(t["case_size"]), "runs_out": runs_out, "overstocked": is_over,
               "cases": cases, "units": units}
        positions.append(pos)
        if runs_out and cases > 0:
            reason = ("%d units on hand, a forecast of %s units a day, %s days of cover, and %d days to the next delivery. "
                      "Forecast need for the lead time of %d days plus %d days, less %d on hand and %d on order: %d cases of %d."
                      % (on_hand, _num(daily, 2), _num(cover), to_next, int(t["lead_time_days"]), target, on_hand, on_order, cases, int(t["case_size"])))
            lines.append({"sku": row["sku"], "supplier_id": t["supplier_id"], "cases": cases, "reason": reason})
        if is_over:
            overstocked.append(row["sku"])
    suppliers = sorted({x["supplier_id"] for x in lines})
    summary = ("%d lines run out before their next delivery, on the forecast of the last four weeks. %d draft purchase orders: %s. "
               "%d lines are overstocked and get no order%s" % (len(lines), len(suppliers), ", ".join(suppliers) or "none", len(overstocked),
               ": " + ", ".join("%s (%s days of cover)" % (x["sku"], x["days_of_cover"]) for x in positions if x["overstocked"]) + "." if overstocked else "."))
    plan = {"lines": lines, "overstocked": overstocked, "summary": summary, "drafted_by": "Inventory Forecasting (code step)"}
    return {"retailer_date": today.isoformat(), "target_cover_days": target, "overstock_days": over, "positions": positions, "plan": plan}


if __name__ == "__main__":
    import sys
    a, b, c = (json.load(open(p, encoding="utf-8")) for p in sys.argv[1:4])
    print(json.dumps(make_plan(a, b, c)["plan"], indent=1))
