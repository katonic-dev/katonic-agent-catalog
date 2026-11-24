# Research desk

The settings folder that turns the Katonic case desk into a desk for a bank's research analysts. An analyst opens a request: a company, the period and what the report is for. The Equity Research Report agent drafts the report. The analyst reviews it row by row and decides. The desk publishes nothing, gives no rating and sets no price target.

Meridian Trust Bank (an invented bank in the invented country Meridia), the exchange, the companies and their filings are invented. Nothing here is investment research.

**The figures hold only at the bank date 2026-11-24.** The filing years and the prices depend on the date, so start the invented bank with `BANK_TODAY=2026-11-24` before you try the real agent against it. The stand-in's canned replies are written for that date.

## The request

| Request | Agent | What the agent does | What goes to the person |
|---|---|---|---|
| A company, a period and a purpose | [Equity Research Report](../../agents/equity-research-report/README.md) | Plans what to read, reads the filings, prices and consensus, and drafts the report: the business, the figures with the filing and line of each, the valuation measures with the working shown, the risks the filings state, and what it could not find | The draft, for the analyst, who checks it and writes the report. The agent gives no rating, no price target and no recommendation to buy or sell |

The desk sends the agent one message: the drafting instruction, then the request. The request names the company by its id. The agent reads the filings themselves from the bank's research system.

## What the person sees

- **A queue of research requests**, each with its title, its company id and its status.
- **The request beside the draft.** The case head shows the company, the period and the purpose. Under it are the filings on file with their ids. The agent's draft is on the other side. On a phone the filings are folded under their heading and the proposal is on the first screen.
- **The agent's proposal first**, in large type: "Accept the draft for your own writing." or "Ask for more.", then the reason, then the count of marks. The desk makes the count from the table. The agent writes none.
- **One table**, one row for each checkable statement, in this order: the business, the figures of the full year, the figures of the half year, growth and margins, the outlook, the share price, the valuation measures, the consensus against the filing, the risks, then what could not be found. A row is short. It has the item with its period, a mark, what it shows with its unit, its source, and only where there is something to say, a basis and a note.
- **The register** afterwards: who decided what, when, on which version of the draft.

### The rows

| Line | What it holds |
|---|---|
| Item (the row's title) | The figure or the measure, with its period |
| Basis | Only for a worked measure (the formula in words) or a restated figure (where the restatement is). A figure a filing states as it is has none |
| Shows | The value with its unit. A worked measure has two labelled lines, Result and Working ("16.2 times" and "5.80 / 0.357"), so the working is never split. A restated figure has three lines: Corrected (in bold, "USD 398.9 million, restated"), Held ("USD 412.6 million, as first published") and the year before as a line that starts with its period ("FY2024: USD 388.0 million"). Every figure carries its unit and its period, also inside a bracket and in a note |
| Source | The filing id and the line, or prices, or consensus, with the date |
| Note | Only where there is something to say: why, and what the analyst should check |

### The marks

The marks are not passes and failures. Two are quiet and two need the analyst's eye.

| Mark | Sign and colour | Meaning |
|---|---|---|
| Sourced | `•` grey | Stated in a filing, or in the price or consensus data, and given as read |
| Worked out | `=` grey | The agent's own arithmetic from sourced figures, with the working shown. Check the working |
| Differs | `≠` brand colour | Two sources give different values, or a later filing restates an earlier one. Both are shown and the note says which one the report uses |
| Missing | `○` amber | Something the report needs is not in any source the agent read |

No mark is green or red. The count above the rows reads, for example, "12 sourced, 10 worked out, 4 differ, 2 missing".

## What the person decides

| Decision | What it records |
|---|---|
| Accept the draft | The analyst takes the draft as the starting point for their own report. Nothing is published, no rating is given and nothing changes in the research system. One click, no note |
| Ask for more | What to find or work out, one item to a line, for example an updated consensus. The request waits until a reply is added, then the agent reads the sources again |
| Send back with a note | A note that the agent sees. The agent drafts again. It is a text button under the decision buttons |

The desk has no decision that publishes a report, gives a rating or sets a price target. The analyst does that, elsewhere. The analyst who opens a request can decide it: the four-eyes rule is off, because the analyst who asks for a report is the one who reads it.

## The three demo cases

| Case | What the agent should find | Rows | Marks |
|---|---|---|---|
| RSC-6001 Kestrelmoor Foods plc | Clean results. FY2025 revenue 842.3 (801.9), operating profit 96.8, profit 71.4, EPS 35.7, dividend 14.0. H1 2026 revenue 438.6 (415.2). Nothing restated. The consensus, updated after the filing, agrees. Proposal: accept | 29 | 15 sourced, 11 worked out, 3 missing |
| RSC-6002 Tarnholt Marine Holdings plc | The half-year filing restates FY2025: revenue 398.9 (412.6), operating profit 52.9 (61.3), profit 37.8 (44.0), EPS 18.9 (22.0). 13.7 of charter income moves into H1 2026. The share fell about 9 percent on 21 Aug 2026. Proposal: accept, with the restated figures to check | 28 | 12 sourced, 10 worked out, 4 differs, 2 missing |
| RSC-6003 Brindlewick Retail Group plc | H1 2026 revenue 521.3 (548.0), operating profit 22.7 (36.4), EPS 7.1 (12.6), interim dividend cut from 6.0 to 4.0. The consensus on file, updated 9 Aug 2026, is older than the filing and above the company's own outlook. The share fell about 27 percent. Proposal: ask for more, an updated consensus | 33 | 18 sourced, 10 worked out, 2 differs, 3 missing |

Amounts are USD million and per share figures are cents. The canned replies are built by a script that works every measure out again from the bank's numbers and stops if a figure differs from the text. The end to end script checks every row, mark and key figure of the three cases against the answers in the bank's scenario list.

## Which engine it needs

It needs the settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk), at a version that takes a settings folder kept outside its own repository. It reads `DESK_CONFIG`, `DESK_ENV_FILE` and `DESK_AGENT_ID`, a `demo-replies.json` beside the settings, and these settings:

- `case.queryFields`, `case.jumpLabel`, `case.foldOnPhone`, `desk.issuedVerb`
- `decisions[].proposalPrefix`
- `draft.rowLabels`, `draft.plainSource`, `draft.markTones`, `draft.markIcons`, `draft.tallyLabels`, `draft.proposalFirst`
- labelled lines in a row (`Label: value` lines separated by `<br>`)

An earlier engine ignores some of these and shows the table without its labels, signs or lines.

**That version of the engine is not published yet.** The engine on GitHub today can only be the regulatory change desk and will not run this folder. This page will name the version once it is out.

## Run it

Start the invented bank with `BANK_TODAY=2026-11-24`. Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm install
DESK_CONFIG=../katonic-agent-catalog/banking/desks/research/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
KATONIC_AGENT_ID=<id of Equity Research Report> \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json`. Without it the engine is the regulatory change desk |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `KATONIC_AGENT_ID` | The agent every request goes to. `DESK_AGENT_ID` does the same and wins over it |
| `DESK_ENV_FILE` | A settings file to read in place of `.env`, for the platform address and key, when several desks share one |
| `SEED_DEMO` | `true` loads the three demo requests on the first start |
| `DATA_DIR` | A folder for the desk's records, so they outlive a restart |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: the agent reads the bank's research system |

Build the agent from [`equity-research-report`](../../agents/equity-research-report/README.md). Its `instructions.md` and the `draft.instruction` setting in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine's stand-in platform answers from this folder's `demo-replies.json`, one canned reply for each demo request, keyed by a distinctive part of the case title. Each follows the right answers in the invented bank's scenario list, for the bank date 2026-11-24. Each says that it comes from the stand-in and that nothing was saved. Start it with the same `DESK_CONFIG`:

```bash
DESK_CONFIG=../katonic-agent-catalog/banking/desks/research/desk.config.json node demo/fake-platform.js
```

Then start the desk with `KATONIC_BASE_URL` pointing at the stand-in, and any value for `KATONIC_API_KEY` and `KATONIC_AGENT_ID`. The stand-in does not read them. It shows the screens and the marks. It is not an agent, and it reads nothing from the bank. The ports used in the tests were 8425 for the stand-in and 3434 for the desk.

## How a case reaches the desk

A member of the research team enters it, or the bank's research system sends it to `POST /api/intake` with the intake token. The bank's research system has no event of its own, so something that knows the analyst's request has to send it. It is not written here.

## How it was tested

On 24 November 2026 the desk was run against the stand-in through thirteen scenarios in a headless browser, 296 checks. They cover: the three seeded requests; each case drafted, with every row, its mark, its key figure and the proposal checked against the bank's scenario list (90 rows in all); the sign, the colour and the count of marks; what the desk sent to the agent (one agent, the desk's instruction, the company id); a question to the agent; a send back with a note and a new version; an edit of the text; every decision (accept with and without an edit, ask for more and the reply coming back, send back); a decision the desk does not have, refused by the server; the register and its export; filters and search by id, company and period; a new request entered by hand, with its error and the stand-in's default reply; the light and dark themes; a phone window at 390 and 360 (nothing wider than the screen, the queue and the request text fold, the jump bar, tap targets, figures not split); and a reload. No console error, page error or failed request was seen. A senior visual design review of every state at 1440 and 390 wide, in light and dark, was done and its faults fixed.

Not yet done: a run against a real agent on a platform. The agent's instructions and tests have not been run on a model.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the drafting instruction |
| `cases.json` | The three demo requests |
| `demo-replies.json` | The stand-in's canned reply for each demo request, and a plain default for any other request |
