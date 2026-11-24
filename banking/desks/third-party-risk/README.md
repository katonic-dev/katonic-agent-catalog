# Third-party risk desk

The settings folder that turns the Katonic case desk into a desk for a bank's third-party risk officer. A supplier answers the bank's questionnaire and attaches evidence. The Third-Party Risk Assessment agent compares each answer and its evidence with the bank's standard, requirement by requirement, and drafts the assessment. The officer decides.

Meridian Trust Bank (an invented bank in the invented country Meridia), its standard MTB-STD-041, the four suppliers and all their documents are invented. Nothing here is a real assessment.

## What the officer sees

- **A list of supplier assessments**, each with its tier and the date the questionnaire arrived.
- **The questionnaire beside the review.** The supplier's answers and short extracts of its evidence are on one side. The agent's review is on the other.
- **One row per requirement of the standard that applies to the tier**, marked met, partly met, not met or not answered. Each row shows the clause, what the supplier says, the evidence the agent relied on, and the reason for the mark.
- **The agent's recommendation**, one line.
- **The register** afterwards: who decided what, when, on which version of the assessment, and with which agent run.

## What the officer decides

| Decision | What it records |
|---|---|
| Recommend approval | A recommendation to approve. Needs a reason if any requirement is not marked met |
| Recommend approval with conditions | The conditions, one to a line |
| Ask the supplier | What the supplier should send. A letter is written. The assessment waits until the supplier's reply is added, then the agent assesses again |
| Do not recommend approval | Which requirements are not met, and why |
| Ask the agent to redo the assessment | A note that the agent sees |

The desk has no decision called approve. A tier 1 supplier is approved by the Risk Committee (clause 7.4), and an unmet requirement can be accepted only as a recorded exception with an end date (clause 7.5). The person who entered an assessment cannot decide it.

## The four demo cases

| Supplier | What the answers show | What the agent should recommend |
|---|---|---|
| Larkspur Cloud Archive Ltd | Weak. Nine requirements not met, one partly met (2.3, administrators only) | Do not recommend approval |
| Tessaly Payment Gateway Services | Strong. Everything met with evidence except 4.3, which the supplier left blank | Ask the supplier for the 4.3 answer and its evidence |
| Pennyfarthing Print and Mail Ltd | 2.3 is answered "all staff" but the attached policy says remote access only. 3.3 has no evidence | Ask the supplier for a corrected access policy and the deletion evidence |
| Harrowfield Records Storage Ltd | Everything met with evidence except two shortfalls the supplier states itself: 4.3 backups tested once a year and 5.4 insurance of USD 4 million, both not met | Recommend approval with conditions: test backups twice a year, raise the insurance to USD 5 million |

Each case states its case date and the planned start of the service, on the two lines at the top of the questionnaire ("Case date" and "Planned start"). Every date in the questionnaire is read against the case date, and requirement 5.2 (an exit plan before the service starts) is read against the planned start.

| Supplier | Case date | Planned start of the service |
|---|---|---|
| Larkspur | 16 November 2026 | 1 March 2027 |
| Tessaly | 17 November 2026 | 4 January 2027 |
| Pennyfarthing | 18 November 2026 | 1 February 2027 |
| Harrowfield | 19 November 2026 | 15 February 2027 |

## What the marks mean

| Mark | Meaning |
|---|---|
| Met | The answer and the evidence both show what the requirement asks, in terms at least as strong as it asks |
| Partly met | Only partial coverage: some of the people or systems but not all, or one of two things the requirement names. A missed limit is never partly met |
| Not met | No evidence is attached, the evidence says something else, a limit is missed (a period, a frequency, an amount or the age of a document: backups tested once a year where twice a year is required are not met), or a condition the requirement sets is not shown in the evidence, such as an agreement in writing or a signature |
| Not answered | The supplier left the answer blank |

The agent's Summary carries no count of marks. The desk counts them from the table and shows the count above the rows.

## Which engine it needs

The last line of each row is labelled "Reason" (`draft.rowLabels.check`), because it gives why the mark follows and what the officer should check.

It needs the settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk), at a version that takes a settings folder kept outside its own repository: it reads `DESK_CONFIG`, `DESK_LIBRARY_DIR`, `DESK_ENV_FILE` and `DESK_AGENT_ID`, a `demo-replies.json` beside the settings, and the `case.queryFields`, `decisions[].proposalPrefix` and `draft.rowLabels` settings.

**That version of the engine is not published yet.** The engine on GitHub today can only be the regulatory change desk and will not run this folder. This page will name the version once it is out.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm install
DESK_CONFIG=../katonic-agent-catalog/banking/desks/third-party-risk/desk.config.json \
DESK_LIBRARY_DIR=../katonic-agent-catalog/banking/policy-library \
KATONIC_LIBRARY_NAME="Meridian standards library (invented)" \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json`. Without it the engine is the regulatory change desk |
| `DESK_LIBRARY_DIR` | A folder of Markdown files. The desk hands the agent the one that shares the most words with the case. Point it at `banking/policy-library`. The standard is read from there and is not copied into this folder |
| `DESK_ENV_FILE` | A settings file to read in place of `.env`, for the platform address, key and agent id |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY`, `KATONIC_AGENT_ID` | The platform's agent API, a key with the Chat scope, and the id of the built agent |
| `KATONIC_LIBRARY_NAME` | The name shown for the standards library in the register |
| `SEED_DEMO` | `true` loads the four demo cases on the first start |

Build the agent from [`../../agents/third-party-risk-assessment/`](../../agents/third-party-risk-assessment/README.md). Its `instructions.md` is the same text as `agent-instructions.md` here.

## How the standard reaches the agent

The desk reads the Markdown files in `DESK_LIBRARY_DIR` and sends the best match with the case, in one message. For the four demo cases the best match is `MTB-STD-041-third-party-security-and-resilience-standard.md`, because the standard field shares words with its opening lines. The desk matches on the case's `standard` field (`case.queryFields` in the settings), not on its title, so a case is titled with the supplier's name alone. The form fills the standard field in for you; a case with that field empty is given the same standard. A standard field with no words in common with the library finds no passage.

## Without a platform

The engine comes with a stand-in platform, `demo/fake-platform.js`, that plays the agent with canned text. Start it with the same `DESK_CONFIG` and it answers from [`demo-replies.json`](demo-replies.json) in this folder: one written assessment for each of the four demo cases, following the right answers above. Every stand-in reply says on its first line that it is canned text and not a real assessment. A supplier you enter by hand gets a plain line saying the stand-in has nothing for it.

The stand-in shows how the desk works. It does not test the agent. For that, build the agent and point the desk at it.

## How it was tested

On 24 November 2026 the desk was run against the stand-in through twelve scenarios in a headless browser: the four cases with their marks and recommendations, every decision, the letter to the supplier, send back and redraft, a question to the agent, the register and its export, filters and search, a case entered by hand, the three themes, a phone-width window and a reload. All twelve passed after two rounds of fixes. It was reviewed twice for visual design at desktop and phone width, in light and dark.

After the rules for marks changed (a second version of the agent's instructions), the cases, canned replies and checks were brought into line and the twelve scenarios were run again. They pass. The desk's own reader was also run over eleven replies written by a real agent under the first version of the instructions: it read all 17 rows of each reply and every mark.

Not yet done: a run against a real agent on the second version of the instructions.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label |
| `cases.json` | The four demo cases |
| `demo-replies.json` | The canned replies for the stand-in platform |
| `agent-instructions.md` | The agent's instructions (second version, the same text as the agent folder's `instructions.md`) |
