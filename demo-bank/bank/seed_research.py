"""Seed data, part 15: invented listed companies on an invented exchange, with filings, prices and consensus estimates for equity research.

The exchange is the Port Ilvane Securities Market (invented). Amounts are USD millions unless the label says cents.
RSC-6001 Kestrelmoor Foods: clean results.
RSC-6002 Tarnholt Marine Holdings: the half-year filing restates revenue, operating profit, profit and EPS of the previous year.
RSC-6003 Brindlewick Retail Group: the half-year filing cuts its outlook and the consensus on file is older than the filing and does not reflect it.
"""

from __future__ import annotations

from datetime import date, timedelta

from .seed_base import d_ago

EXCHANGE = "Port Ilvane Securities Market (invented)"
SHARES_M = 200.0


def weekday_on_or_before(d: date) -> date:
    while d.weekday() >= 5:
        d -= timedelta(days=1)
    return d


COMPANIES = [
    ("RSC-6001", "Kestrelmoor Foods plc", "KSTM.PISM", "Food and drink", "Makes and sells packaged bread, flour and ready meals in Meridia and Aldoria."),
    ("RSC-6002", "Tarnholt Marine Holdings plc", "TRNH.PISM", "Shipping", "Owns 22 coastal cargo ships and charters them to traders in six countries."),
    ("RSC-6003", "Brindlewick Retail Group plc", "BRWK.PISM", "Retail", "Runs 412 high street and out-of-town shops selling clothes and home goods."),
]


def fmt(x: float) -> str:
    return f"{x:,.1f}"


def statement(title, cols, rows) -> str:
    out = [title, "  " + " " * 34 + "".join(f"{c:>14}" for c in cols)]
    for label, vals in rows:
        out.append("  " + f"{label:<34}" + "".join(f"{v:>14}" for v in vals))
    return "\n".join(out)


def annual_text(name, fy, published, cur, prev, dps, notes) -> str:
    head = (f"{name}\nAnnual results for the year ended 31 December {fy}\nPublished {published}\n\n"
            f"Headlines\n  Revenue was USD {fmt(cur['rev'])} million ({fmt(prev['rev'])} million in {fy - 1}).\n"
            f"  Operating profit was USD {fmt(cur['op'])} million ({fmt(prev['op'])} million).\n"
            f"  Profit after tax was USD {fmt(cur['pat'])} million ({fmt(prev['pat'])} million).\n"
            f"  Earnings per share were {cur['eps']:.1f} cents ({prev['eps']:.1f} cents).\n"
            f"  The board proposes a final dividend that makes the full-year dividend {dps[0]:.1f} cents per share ({dps[1]:.1f} cents).\n\n")
    table = statement("Summary income statement and balance sheet (USD million, cents for per share)", [f"FY{fy}", f"FY{fy - 1}"], [
        ("Revenue", [fmt(cur["rev"]), fmt(prev["rev"])]), ("Operating profit", [fmt(cur["op"]), fmt(prev["op"])]),
        ("Profit after tax", [fmt(cur["pat"]), fmt(prev["pat"])]), ("Earnings per share (cents)", [f"{cur['eps']:.1f}", f"{prev['eps']:.1f}"]),
        ("Dividend per share (cents)", [f"{dps[0]:.1f}", f"{dps[1]:.1f}"]), ("Net debt at year end", [fmt(cur["debt"]), fmt(prev["debt"])])])
    return head + table + "\n\nNotes\n" + "\n".join(f"  {i}. {n}" for i, n in enumerate(notes, start=1)) + "\n"


def half_text(name, fy, published, cur, prev, interim, notes, extra_before_notes="") -> str:
    head = (f"{name}\nHalf-year results for the six months ended 30 June {fy}\nPublished {published}\n\n"
            f"Headlines\n  Revenue was USD {fmt(cur['rev'])} million ({fmt(prev['rev'])} million in the first half of {fy - 1}).\n"
            f"  Operating profit was USD {fmt(cur['op'])} million ({fmt(prev['op'])} million).\n"
            f"  Profit after tax was USD {fmt(cur['pat'])} million ({fmt(prev['pat'])} million).\n"
            f"  Earnings per share were {cur['eps']:.1f} cents ({prev['eps']:.1f} cents).\n"
            f"  Interim dividend {interim[0]:.1f} cents per share ({interim[1]:.1f} cents).\n\n")
    table = statement("Summary income statement and balance sheet (USD million, cents for per share)", [f"H1 {fy}", f"H1 {fy - 1}"], [
        ("Revenue", [fmt(cur["rev"]), fmt(prev["rev"])]), ("Operating profit", [fmt(cur["op"]), fmt(prev["op"])]),
        ("Profit after tax", [fmt(cur["pat"]), fmt(prev["pat"])]), ("Earnings per share (cents)", [f"{cur['eps']:.1f}", f"{prev['eps']:.1f}"]),
        ("Net debt at 30 June", [fmt(cur["debt"]), "n/a"])])
    return head + table + "\n\n" + extra_before_notes + "Notes\n" + "\n".join(f"  {i}. {n}" for i, n in enumerate(notes, start=1)) + "\n"


def build_filings(today: date) -> dict:
    f = {}
    ann_date = weekday_on_or_before(today - timedelta(days=238)).isoformat()
    half_date = weekday_on_or_before(today - timedelta(days=95)).isoformat()
    fy = (today - timedelta(days=238)).year - 1 if (today - timedelta(days=238)).month < 7 else (today - timedelta(days=238)).year
    hy = (today - timedelta(days=95)).year

    def put(fid, cid, kind, period, published, title, text):
        f[fid] = {"filing_id": fid, "company_id": cid, "type": kind, "period": period, "published": published, "title": title, "text": text}

    # ---- Kestrelmoor, clean
    n = "Kestrelmoor Foods plc"
    put("FIL-6101", "RSC-6001", "annual", f"FY{fy}", ann_date, f"{n} annual results {fy}",
        annual_text(n, fy, ann_date, dict(rev=842.3, op=96.8, pat=71.4, eps=35.7, debt=118.5), dict(rev=801.9, op=90.2, pat=66.2, eps=33.1, debt=126.0), (14.0, 13.0),
                    ["Earnings per share use 200.0 million shares in both years.", "Revenue grew 5.0 percent. Volume grew 3.1 percent and price 1.9 percent.",
                     "Staff numbers at year end were 4,120 (4,085).", "No figure in this report has been restated."]))
    put("FIL-6102", "RSC-6001", "half_year", f"H1 {hy}", half_date, f"{n} half-year results {hy}",
        half_text(n, hy, half_date, dict(rev=438.6, op=51.9, pat=38.6, eps=19.3, debt=109.2), dict(rev=415.2, op=47.1, pat=35.0, eps=17.5, debt=0), (7.0, 6.5),
                  ["Earnings per share use 200.0 million shares.", f"The full-year figures for {fy} in the annual report are unchanged.",
                   f"The board expects full-year revenue growth of about 4 to 6 percent."]))
    # ---- Tarnholt, restatement
    n = "Tarnholt Marine Holdings plc"
    put("FIL-6103", "RSC-6002", "annual", f"FY{fy}", ann_date, f"{n} annual results {fy}",
        annual_text(n, fy, ann_date, dict(rev=412.6, op=61.3, pat=44.0, eps=22.0, debt=205.4), dict(rev=388.0, op=55.2, pat=40.2, eps=20.1, debt=214.9), (9.0, 8.5),
                    ["Earnings per share use 200.0 million shares in both years.", "Revenue includes charter income of USD 112.4 million from time charters.",
                     "Staff numbers at year end were 1,540 (1,512)."]))
    restate = (f"Restatement of {fy} figures\n  During the half the company found that charter income for voyages that finished in January {hy} had been counted in {fy}.\n"
               f"  USD 13.7 million of revenue belongs to {hy}. The {fy} figures are restated as follows.\n"
               + statement("", ["As published", "Restated"], [
                   (f"Revenue FY{fy}", [fmt(412.6), fmt(398.9)]), (f"Operating profit FY{fy}", [fmt(61.3), fmt(52.9)]),
                   (f"Profit after tax FY{fy}", [fmt(44.0), fmt(37.8)]), (f"Earnings per share FY{fy} (cents)", ["22.0", "18.9"])]).lstrip("\n")
               + f"\n  Net debt and the dividend for {fy} are not affected. The restated amount moves into the first half of {hy}.\n\n")
    put("FIL-6104", "RSC-6002", "half_year", f"H1 {hy}", half_date, f"{n} half-year results {hy}",
        half_text(n, hy, half_date, dict(rev=213.4, op=33.6, pat=24.2, eps=12.1, debt=198.7), dict(rev=184.0, op=25.1, pat=18.0, eps=9.0, debt=0), (4.5, 4.0),
                  [f"Revenue for H1 {hy} includes the USD 13.7 million moved from {fy}.", "Earnings per share use 200.0 million shares.",
                   f"Comparatives for the first half of {hy - 1} are as first published."], extra_before_notes=restate))
    # ---- Brindlewick, outlook cut
    n = "Brindlewick Retail Group plc"
    put("FIL-6105", "RSC-6003", "annual", f"FY{fy}", ann_date, f"{n} annual results {fy}",
        annual_text(n, fy, ann_date, dict(rev=1094.7, op=78.4, pat=55.0, eps=27.5, debt=233.0), dict(rev=1081.3, op=80.9, pat=57.8, eps=28.9, debt=228.3), (12.0, 12.0),
                    ["Earnings per share use 200.0 million shares in both years.", "The group traded from 412 shops at the year end (409).",
                     "Like-for-like sales rose 0.6 percent."]))
    outlook = (f"Outlook\n  Trading in the first half was weaker than the board expected, mainly in out-of-town shops. The board now expects full-year revenue of between\n"
               f"  USD 1,020 million and USD 1,060 million and operating profit of between USD 55 million and USD 62 million.\n\n")
    put("FIL-6106", "RSC-6003", "half_year", f"H1 {hy}", half_date, f"{n} half-year results {hy}",
        half_text(n, hy, half_date, dict(rev=521.3, op=22.7, pat=14.2, eps=7.1, debt=261.4), dict(rev=548.0, op=36.4, pat=25.2, eps=12.6, debt=0), (4.0, 6.0),
                  ["Earnings per share use 200.0 million shares.", "The interim dividend is cut from 6.0 cents to 4.0 cents.",
                   f"Figures for {fy} in the annual report are unchanged."], extra_before_notes=outlook))
    return f


def build_prices(today: date) -> dict:
    out = {}
    half_day = weekday_on_or_before(today - timedelta(days=95)).isoformat()
    events = {"RSC-6001": {half_day: 0.021}, "RSC-6002": {half_day: -0.09}, "RSC-6003": {half_day: -0.27}}
    start = {"RSC-6001": 5.40, "RSC-6002": 3.15, "RSC-6003": 4.35}
    for ci, (cid, *_rest) in enumerate(COMPANIES):
        rows, price = [], start[cid]
        days = []
        d = today - timedelta(days=1)
        while len(days) < 130:
            if d.weekday() < 5:
                days.append(d)
            d -= timedelta(days=1)
        days.reverse()
        for k, day in enumerate(days):
            move = ((k * 37 + ci * 11) % 17 - 8) / 8 * 0.006 + (0.0004 if cid == "RSC-6001" else -0.0002 if cid == "RSC-6003" else 0.0)
            move = events[cid].get(day.isoformat(), move)
            close = round(price * (1 + move), 2)
            hi, lo = round(max(price, close) * 1.004, 2), round(min(price, close) * 0.996, 2)
            rows.append({"date": day.isoformat(), "open": round(price, 2), "high": hi, "low": lo, "close": close,
                         "volume": 410000 + (k * 7919 + ci * 104729) % 260000 + (900000 if day.isoformat() in events[cid] else 0)})
            price = close
        out[cid] = rows
    return out


def build_estimates(today: date) -> dict:
    hy = (today - timedelta(days=95)).year
    after = d_ago(today, 80)
    before_half = d_ago(today, 107)  # twelve days before the half-year filing: Brindlewick's consensus is this old
    return {
        "RSC-6001": {"company_id": "RSC-6001", "as_of": after, "currency": "USD", "analyst_count": 8, "note": "Updated after the half-year results.",
                     "estimates": [{"year": f"FY{hy}", "revenue_m": 880.0, "operating_profit_m": 101.0, "eps_cents": 37.3, "dps_cents": 14.5, "eps_low_cents": 36.4, "eps_high_cents": 38.0},
                                   {"year": f"FY{hy + 1}", "revenue_m": 921.0, "operating_profit_m": 108.5, "eps_cents": 40.0, "dps_cents": 15.5, "eps_low_cents": 38.6, "eps_high_cents": 41.8}]},
        "RSC-6002": {"company_id": "RSC-6002", "as_of": after, "currency": "USD", "analyst_count": 6, "note": "Updated after the half-year results and the restatement.",
                     "estimates": [{"year": f"FY{hy}", "revenue_m": 421.5, "operating_profit_m": 62.0, "eps_cents": 20.4, "dps_cents": 9.0, "eps_low_cents": 19.0, "eps_high_cents": 21.9},
                                   {"year": f"FY{hy + 1}", "revenue_m": 436.0, "operating_profit_m": 66.1, "eps_cents": 22.1, "dps_cents": 9.5, "eps_low_cents": 20.0, "eps_high_cents": 23.7}]},
        "RSC-6003": {"company_id": "RSC-6003", "as_of": before_half, "currency": "USD", "analyst_count": 9, "note": "Last updated before the half-year results.",
                     "estimates": [{"year": f"FY{hy}", "revenue_m": 1150.0, "operating_profit_m": 88.5, "eps_cents": 30.2, "dps_cents": 12.5, "eps_low_cents": 28.4, "eps_high_cents": 32.0},
                                   {"year": f"FY{hy + 1}", "revenue_m": 1195.0, "operating_profit_m": 95.0, "eps_cents": 32.8, "dps_cents": 13.0, "eps_low_cents": 30.0, "eps_high_cents": 35.1}]},
    }


def build_research(today: date) -> dict:
    prices = build_prices(today)
    filings = build_filings(today)
    companies = {}
    for cid, name, ticker, sector, desc in COMPANIES:
        companies[cid] = {"company_id": cid, "name": name, "ticker": ticker, "exchange": EXCHANGE, "sector": sector, "currency": "USD",
                          "shares_million": SHARES_M, "year_end": "31 December", "description": desc, "reports": []}
    return {"research_companies": companies, "research_filings": filings, "research_prices": prices, "research_estimates": build_estimates(today)}
