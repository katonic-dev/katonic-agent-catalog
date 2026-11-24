# Equity Research Report

Given a company and a goal, plans what to read, reads the filings and market data, and drafts a research report for an analyst, with the filing and line of every figure.

| | |
|---|---|
| Type and form | Autonomous agent |
| What starts it | An analyst's request, naming a company, the period and what the report is for |
| How people meet it | An application: the Research desk |
| Reads from | The bank's research data: the listed companies, their filings, share prices and consensus estimates |
| Changes | Saves a draft report. Nothing is published |
| State | Written, not yet built. The instructions and tests have not been run on a model |

## What it does

- Plans its own reading: the company, its filings, each filing in full, the share prices around the results, and the consensus. It reads each source once, then writes, and stops when the draft is complete or when it has shown what it could not find.
- Drafts the report as a table the analyst checks row by row: the business, the figures over the periods the filings give, the growth and margins it worked out, the share price, the valuation measures with the working shown, the consensus compared with the filing, the risks the filings state, and what it could not find.
- Uses the restated figure where a later filing restates an earlier one, shows both, and says so.
- Never sets a half-year figure against a full-year figure and never annualises a half year.
- Says when a consensus was last updated before the latest filing, shows how it differs, and uses none of it in a measure.
- Marks every row: sourced, worked out, differs or missing.
- Ends with one proposal line for the analyst.

## What it does not do

- Give a rating, a price target or a recommendation to buy, sell or hold, or call a share cheap or dear. The analyst does.
- Forecast.
- Estimate a missing figure, or take one from memory or from another company.
- Describe the business from memory. The research system holds no description of what a company does that an operation returns, so the report gives the sector and what the filings state, and marks the description missing.
- Publish or send the report.
- Work out measures the filings cannot support. The filings give no equity, no EBITDA and no cash flow, so price to book and enterprise value to EBITDA are marked missing.
- Guarantee the same figures on every run. The report is a draft, and its arithmetic should be checked. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's research data, connected as an imported API, with the six operations listed in [`agent.yaml`](agent.yaml) and no others.
- The [Research desk](../../desks/research/README.md), which sends the request, if you want to meet the agent through a screen. The agent also answers in a chat.
- An API key with the Chat scope for the desk, and the published agent's id.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the six tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft report. For the analyst. Not issued.", a seven-column table, and a last line that starts "Proposal:". Change the instructions and the desk's drafting instruction together.
4. The seven tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data, started with `BANK_TODAY=2026-11-24` (the figures hold only at that date). Amounts are USD million, per share figures are cents.

- `RSC-6001` Kestrelmoor Foods plc: clean results. FY2025 revenue 842.3 (801.9), operating profit 96.8, profit 71.4, EPS 35.7, dividend 14.0. H1 2026 revenue 438.6 (415.2). Nothing restated. Consensus updated after the filing, FY2026 revenue 880.0 and EPS 37.3. Filing and consensus agree.
- `RSC-6002` Tarnholt Marine Holdings plc: the half-year filing FIL-6104 restates FY2025 of FIL-6103. Revenue 412.6 becomes 398.9, operating profit 61.3 becomes 52.9, profit 44.0 becomes 37.8, EPS 22.0 becomes 18.9. 13.7 of charter income moves into H1 2026, so H1 revenue of 213.4 is 199.7 without it, against 184.0.
- `RSC-6003` Brindlewick Retail Group plc: H1 2026 revenue 521.3 (548.0), operating profit 22.7 (36.4), EPS 7.1 (12.6), interim dividend cut from 6.0 to 4.0. The filing's outlook is revenue 1,020 to 1,060 and operating profit 55 to 62. The consensus on file, updated 2026-08-09, twelve days before the filing, says revenue 1,150 and operating profit 88.5. It is out of date, and the report says so and uses the filing.
- A request for a price target and a buy call: refused.
- A request for price to book or enterprise value to EBITDA: marked missing.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

The analyst reads the draft, checks it and writes the report. The agent gives no rating, no price target and no recommendation to buy or sell. Every difference between two sources, every restated figure and every figure it could not find is for the analyst to weigh.
