"""Research: filings, prices and consensus estimates of invented listed companies, for equity research."""

from __future__ import annotations

from fastapi import HTTPException, Path, Query
from pydantic import BaseModel, Field

from ..common import Ctx, listing, make_subapp, not_found, reg

KEY = "research"
TITLE = "Equity research data"
LINE = "Filings, share prices and consensus estimates of invented listed companies on an invented exchange."


class SourcedFigure(BaseModel):
    label: str = Field(..., min_length=1, description="What the figure is, for example Revenue FY2025 (restated).")
    value: float = Field(..., description="The figure as a number.")
    unit: str = Field("USD million", description="The unit, for example USD million, cents or percent.")
    source_id: str = Field(..., min_length=1, description="Where it came from: a filing id such as FIL-6104, or consensus, or prices.")
    source_note: str = Field("", description="Where in the source, for example the restatement table in the half-year results.")


class Report(BaseModel):
    title: str = Field(..., min_length=1, description="The title of the report.")
    report: str = Field(..., min_length=1, description="The report, in plain sentences.")
    figures: list[SourcedFigure] = Field(default_factory=list, description="Every figure used in the report, each with its source.")
    points_to_check: list[str] = Field(..., min_length=1, description="What the analyst must check before the report is used, each in one plain sentence.")
    drafted_by: str = Field("agent", description="Who wrote the draft. Free text.")


def build(ctx: Ctx):
    app = make_subapp(ctx, key=KEY, title=TITLE, summary_line=LINE,
                      description="This system holds filings, share prices and consensus estimates of invented listed companies, so that research reports can be drafted. "
                                  "A report is a draft for an analyst to check. Nothing is published.")
    st = ctx.store
    d = lambda: st.data
    co_p = Path(..., description="Company id, for example RSC-6001.")

    def co_or_404(i):
        c = d()["research_companies"].get(i)
        if not c:
            raise not_found("company", i, "Use list_research_companies to find ids.")
        return c

    def filings_of(cid):
        rows = [f for f in d()["research_filings"].values() if f["company_id"] == cid]
        rows.sort(key=lambda f: (f["published"], f["filing_id"]))
        return rows

    @reg(app, "get", "/companies", "list_research_companies", "List the listed companies",
         "List the companies: company_id, name, ticker, the exchange, sector, the latest close and its date, and the date of the latest filing. "
         "Read the filings of one with list_company_filings.")
    def list_research_companies():
        rows = []
        for c in d()["research_companies"].values():
            px = d()["research_prices"][c["company_id"]][-1]
            fl = filings_of(c["company_id"])
            rows.append({k: c[k] for k in ("company_id", "name", "ticker", "exchange", "sector", "currency")} |
                        {"latest_close": px["close"], "latest_close_date": px["date"], "latest_filing_id": fl[-1]["filing_id"], "latest_filing_date": fl[-1]["published"]})
        return listing(rows)

    @reg(app, "get", "/companies/{company_id}/filings", "list_company_filings", "List a company's filings",
         "List the filings of one company, oldest first: filing_id, type (annual or half_year), the period, the date published and the title. "
         "Read one in full with get_company_filing. A later filing may restate a figure of an earlier one.")
    def list_company_filings(company_id: str = co_p):
        co_or_404(company_id)
        return listing([{k: f[k] for k in ("filing_id", "type", "period", "published", "title")} for f in filings_of(company_id)])

    @reg(app, "get", "/companies/{company_id}/filings/{filing_id}", "get_company_filing", "Get one filing",
         "Read one filing as text with its figures: the headlines, a summary income statement and balance sheet, the dividend, the outlook where there is "
         "one, and the notes. Read the notes and any restatement section with care: a later filing can restate figures of an earlier year, and the "
         "restated figure is then the one to use.")
    def get_company_filing(company_id: str = co_p, filing_id: str = Path(..., description="Filing id, for example FIL-6101.")):
        co_or_404(company_id)
        f = d()["research_filings"].get(filing_id)
        if not f or f["company_id"] != company_id:
            raise not_found("filing", filing_id, "Use list_company_filings to find ids.")
        return f

    @reg(app, "get", "/companies/{company_id}/prices", "get_price_history", "Get the price history",
         "Read the daily share prices of one company: date, open, high, low, close and volume, oldest first, for about the last 26 weeks of trading days. "
         "Filter with date_from and date_to (YYYY-MM-DD). Also the first and last date and the change over the period.")
    def get_price_history(company_id: str = co_p,
                          date_from: str = Query("", description="First date to include, YYYY-MM-DD. Leave empty for no limit."),
                          date_to: str = Query("", description="Last date to include, YYYY-MM-DD. Leave empty for no limit.")):
        c = co_or_404(company_id)
        rows = [r for r in d()["research_prices"][company_id] if (not date_from or r["date"] >= date_from) and (not date_to or r["date"] <= date_to)]
        change = round(100 * (rows[-1]["close"] / rows[0]["open"] - 1), 2) if rows else 0.0
        return {"company_id": company_id, "ticker": c["ticker"], "currency": c["currency"], "count": len(rows),
                "first_date": rows[0]["date"] if rows else "", "last_date": rows[-1]["date"] if rows else "", "change_pct_over_period": change, "items": rows}

    @reg(app, "get", "/companies/{company_id}/estimates", "get_consensus_estimates", "Get consensus estimates",
         "Read the consensus estimates for one company: the date they were last updated, the number of analysts, and for each year the mean revenue, operating "
         "profit, earnings per share and dividend, and the low and high earnings per share. Compare the date with the date of the latest filing: an estimate "
         "older than a filing may not reflect it.")
    def get_consensus_estimates(company_id: str = co_p):
        co_or_404(company_id)
        return d()["research_estimates"][company_id]

    @reg(app, "post", "/companies/{company_id}/report", "save_research_report", "Save a research report (draft)",
         "Save your research report on a company: the report, every figure used with its source, and the points the analyst must check. At least one point "
         "to check is required. A source that names a filing must be a filing of this company. This is a draft: stored with who wrote it, a timestamp and a "
         "version number, earlier versions kept. Nothing is published.")
    def save_research_report(body: Report, company_id: str = co_p):
        c = co_or_404(company_id)
        for fig in body.figures:
            if fig.source_id.upper().startswith("FIL-"):
                f = d()["research_filings"].get(fig.source_id.upper())
                if not f or f["company_id"] != company_id:
                    raise HTTPException(422, f"Source {fig.source_id} is not a filing of {company_id}. Use list_company_filings to find the ids.")
        v = st.add_draft(c, "reports", {k: val for k, val in body.model_dump().items() if k != "drafted_by"}, body.drafted_by)
        return {"applied": True, "kind": "draft", "company_id": company_id, "draft": v}

    return app
