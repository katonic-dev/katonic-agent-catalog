# Lending desk

The settings folder that turns the Katonic case desk into a desk for a bank's lending team. Three kinds of case sit in one queue. An application pack is checked against the documents the product requires. An application's figures are spread and its ratios worked out for a credit memo. The signed documents of an approved loan are compared with the approved terms. Each kind goes to its own agent. A person decides.

Meridian Trust Bank (an invented bank in the invented country Meridia), its customers, its applications, its loan and all their documents are invented. Nothing here is a real lending decision.

## The three kinds of case

| Kind | Agent | What the agent does | What goes to the person |
|---|---|---|---|
| Application intake | [Loan Application Intake](../../agents/loan-application-intake/README.md) | Checks the pack against the documents the product requires, extracts the figures, lists what is missing and what differs | The list, for the loan officer. The agent approves and declines nothing |
| Credit analysis | [Credit Analysis](../../agents/credit-analysis/README.md) | Spreads the figures, works out the ratios the policy names with their limits, drafts the credit memo with the source of every figure | The memo, for the credit officer, who decides |
| Document check | [Loan Document Verification](../../agents/loan-document-verification/README.md) | Compares the contract and the security documents with the approved terms and marks every difference | Every difference, for a banker |

The desk sends the agent one message: the drafting instruction for the kind, then the case. The case names the application or the loan. The agent reads the documents themselves from the bank's lending system.

## What the person sees

- **A queue of lending cases**, each with its kind, its id and its customer.
- **The case beside the review.** The desk's short summary of the case is on one side: who, what product, how much, and the documents on file with their ids. The agent's review is on the other.
- **One table for every kind**, one row for each item checked. Each row has what the file shows, what it was checked against, the source (the document id and the line or clause), a mark and a note.
- **The agent's proposal**, one line.
- **The register** afterwards: who decided what, when, on which version of the review, and with which agent run and tool calls.

### The marks

| Mark | Meaning |
|---|---|
| in order | The file shows what the policy, the approved terms or the form requires |
| missing | Not on file, not stated in the contract, or a figure a ratio needs is not in the file |
| differs | Two sources give different values. Both are shown and neither is chosen |
| outside policy | A ratio is beyond the limit the lending policy names |

Application intake uses in order, missing and differs. Credit analysis uses all four. Document check uses in order, differs and missing.

## What the person decides

| Decision | What it records |
|---|---|
| Accept the draft | The person takes the review as the file note. Needs a reason if any item is not marked in order. It approves or declines no loan and changes nothing in the lending system |
| Ask for more | What to ask for, one item to a line. A letter is written. The case waits until the reply is added, then the agent reads the case again |
| Refer on | Who it goes to and why: a banker, the credit officer or the credit committee |
| Ask the agent to redo the review | A note that the agent sees |

The desk has no decision that approves or declines a loan. The loan officer, the credit officer or the credit committee does that, elsewhere. The person who entered a case cannot decide it.

## The six demo cases

| Case | Kind | What the agent should find |
|---|---|---|
| LAP-8001, a personal loan of USD 18,000 | Application intake | All four required documents on file. Income agrees across the form, payslips and statements (gross 5,200, net 4,010) |
| LAP-8002, a small business loan of USD 60,000 | Application intake | Two documents missing, the latest tax return and the declaration of ultimate owners. Average monthly turnover differs: 62,000 on the form, 51,400 in the bank statements |
| LAP-8003, a small business loan of USD 120,000 | Application intake | A complete pack, with three years of financial statements |
| LAP-8003 | Credit analysis | Current ratio 1.43, debt to equity 0.26, debt service cover 3.31, and 2.39 with the new loan. All within policy |
| LAP-8001 | Credit analysis | Debt to income 0.197 against a limit of at most 0.40 |
| LN-9001, a term loan of USD 250,000 | Document check | Exactly three differences: the rate margin (clause 3), the debt service cover covenant (clause 6a) and the security (clause 7) |

## What each kind shows

Each kind names its own decisions and marks (`routing.kinds.<kind>.decisions` and `.marks`). The server refuses a decision the kind does not offer.

| Kind | Decisions | Marks |
|---|---|---|
| Application intake | Accept the draft, Ask for more, Refer on, redo | in order, missing, differs |
| Credit analysis | Accept the draft, Refer on, redo | in order, outside policy, missing, differs |
| Document check | Accept the draft, Refer on, redo | in order, differs, missing |

Credit analysis and document check do not ask the applicant for documents: that is intake's work. The last line of each row is labelled "Note" (`draft.rowLabels.check`), because it is the agent's note on the row.

## Which engine it needs

It needs the settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk), at a version that takes a settings folder kept outside its own repository: it reads `DESK_CONFIG`, `DESK_ENV_FILE` and `DESK_AGENT_ID`, a `demo-replies.json` beside the settings, the `routing` setting, and the `case.queryFields`, `case.jumpLabel`, `decisions[].proposalPrefix` (one prefix or a list), `draft.rowLabels`, `draft.plainSource`, `desk.issuedVerb` and `intake.fields[].options` settings. An earlier engine ignores `routing`, and every case would go to one agent with one instruction.

**That version is in `main` of katonic-case-desk** since 24 November 2026 ([pull request 2](https://github.com/katonic-dev/katonic-case-desk/pull/2)). A copy of the engine cloned before that date will not run this folder.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm install
DESK_CONFIG=../katonic-agent-catalog/banking/desks/lending/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
INTAKE_AGENT_ID=<id of Loan Application Intake> \
CREDIT_AGENT_ID=<id of Credit Analysis> \
DOCUMENT_AGENT_ID=<id of Loan Document Verification> \
KATONIC_AGENT_ID=<any one of the three, for a case of an unknown kind> \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json`. Without it the engine is the regulatory change desk |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `INTAKE_AGENT_ID` | The agent for cases of the kind Application intake. If it is empty, drafting such a case fails and says which variable to set |
| `CREDIT_AGENT_ID` | The same, for Credit analysis |
| `DOCUMENT_AGENT_ID` | The same, for Document check |
| `KATONIC_AGENT_ID` | The agent for a case whose kind is none of the three. The desk asks it only to say that the kind is not recognised. It can be any one of the three agents. `DESK_AGENT_ID` does the same and wins over it |
| `DESK_ENV_FILE` | A settings file to read in place of `.env`, for the platform address and key, when several desks share one |
| `SEED_DEMO` | `true` loads the six demo cases on the first start |
| `DATA_DIR` | A folder for the desk's records, so they outlive a restart |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: the agents read the bank's lending system |

The kind of a case is the value of its "Kind of work" field, matched without regard to case: `Application intake`, `Credit analysis` or `Document check`.

Build the three agents from [`loan-application-intake`](../../agents/loan-application-intake/README.md), [`credit-analysis`](../../agents/credit-analysis/README.md) and [`loan-document-verification`](../../agents/loan-document-verification/README.md). Each folder's `instructions.md` and the matching `routing` instruction in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine's stand-in platform answers from this folder's `demo-replies.json`, one canned reply for each demo case, keyed by a distinctive part of the case title. Each follows the right answers in the invented bank's scenario list. Each says that it comes from the stand-in and that nothing was saved. Start it with the same `DESK_CONFIG`:

```bash
DESK_CONFIG=../katonic-agent-catalog/banking/desks/lending/desk.config.json node demo/fake-platform.js
```

Then start the desk with `KATONIC_BASE_URL` pointing at the stand-in, any value for `KATONIC_API_KEY`, and any value for each of the four agent ids. The stand-in does not read them. It shows the screens and the marks. It is not an agent, and it reads nothing from the bank.

## How a case reaches the desk

A member of the lending team enters it, or the bank's lending system sends it to `POST /api/intake` with the intake token. The bank's own loan-application event carries a message and an id, not the desk's fields, so a small adapter between the two is needed. It is not written here.

## How it was tested

On 24 November 2026 the desk was run against the stand-in through twelve scenarios in a headless browser: the six demo cases with their rows, marks and proposals, which agent and which instruction each kind used, every decision (accept with and without a reason, ask for more with its letter and reply, refer on, redo), a question to the agent, the register and its export, filters and search by kind, a case entered by hand for each kind and one with a kind the desk does not know, the three themes, a phone-width window at 390 and 360, and a reload. All twelve passed (213 checks) after one round of fixes. It was reviewed for visual design at desktop and phone width, in light and dark.

Not yet done: a run against real agents on a platform.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the `routing` setting with the three drafting instructions |
| `cases.json` | The six demo cases |
| `demo-replies.json` | The stand-in's canned reply for each demo case, and a plain default for any other case |
