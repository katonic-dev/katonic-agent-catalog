# Food safety desk

The settings folder that turns the Katonic case desk into a desk for a restaurant operator's food safety team. A month of records arrives for each restaurant. The Food Safety Record Check agent lists every reading outside the limits of the company's food safety plan, every check that was not made and every missing entry. A food safety lead decides what happens next.

Rowanmere Kitchen (the restaurant arm of Rowanmere Group, an invented company in the invented country Meridia), its restaurants, their readings and its food safety plan are invented. Nothing here is food safety guidance.

## What the food safety lead sees

- **A queue of record checks**, one for each restaurant and month, with the town and the status.
- **The records beside the findings.** The month's logs are on one side, as the desk holds them. The agent's findings are on the other.
- **One row for each unit or check that deviates**, with the plan's section and limit, what the records show, the dates and a mark. A last row names the checks with no deviation.
- **The agent's proposed next step**, one line, and the button it points to.
- **The register** afterwards: who decided what, when, on which version of the findings, and with which agent run.

## What the food safety lead decides

| Decision | What it records |
|---|---|
| Sign the monthly review | The review, signed in the lead's name. Needs a reason if any deviation is listed |
| Ask the restaurant manager for corrective actions | What the restaurant manager must record, one item to a line. A note to the restaurant manager is written. The record check waits until the corrective actions are added, then the agent lists the deviations again |
| Record a decision on the unit (plan 6.2) | The lead's decision on a unit with three or more readings outside the limit: whether it stays in use or is taken out of use until it is serviced |
| Ask the agent to check the records again | A note that the agent sees |

The desk has no decision about whether food was safe, and the agent does not say so either. The plan leaves that to the restaurant manager and the food safety lead (sections 1.3 and 7.1). The person who entered a record check cannot decide it.

## The six demo record checks (October 2026)

| Restaurant | Town | What the records hold | What the agent should propose |
|---|---|---|---|
| R-014 Rowanmere Kitchen Harbour Street | Port Ilvane | Make-line chiller above 5.0 °C three times, hot holding below 63.0 °C twice, three cleaning sign-offs missing | Refer to the food safety lead under section 6.2 |
| R-022 Rowanmere Kitchen Malting Lane | Port Ilvane | Nothing outside the plan | Sign the monthly review |
| R-031 Rowanmere Kitchen Quayside | Marlow Reach | Freezer warmer than −18.0 °C twice, one cleaning sign-off missing | Ask the restaurant manager for corrective actions |
| R-047 Rowanmere Kitchen Kiln Road | Tallowby | Hot holding below 63.0 °C four times | Refer to the food safety lead under section 6.2 |
| R-058 Rowanmere Kitchen Lantern Square | Port Ilvane | Four afternoon checks on the walk-in chiller recorded as not made, one cleaning sign-off missing | Ask the restaurant manager for corrective actions |
| R-063 Rowanmere Kitchen Station Parade | Marlow Reach | A chilled delivery at 6.5 °C recorded as accepted | Ask the restaurant manager for corrective actions |

These are the records the invented retailer holds for the period `2026-10` when its date is 24 November 2026. [Its scenario list](../../../demo-retailer/SCENARIOS.md) gives the right answer for each restaurant.

## What the marks mean

| Mark | Meaning |
|---|---|
| Repeated deviation | Three or more readings outside the limit on the same piece of equipment in the month. Section 6.2 of the plan applies, and the food safety lead decides about the unit |
| Outside the limit | One or two readings on the unit are outside the plan's limit. A delivery item outside its limit that was accepted is marked this way too (section 4.3) |
| Missing entry | A day with no signed daily cleaning entry |
| Missed check | A check recorded as not made. Section 6.2 counts readings outside the limit, so checks that were not made do not bring it in |
| Within the plan | No deviation |

The agent's Summary carries no count of marks. The desk counts them from the table and shows the count above the rows.

## Where the cases come from

`cases.json` is not typed by hand. [`make_cases.py`](make_cases.py) builds it from the seed of the invented retailer in [`demo-retailer/`](../../../demo-retailer/README.md): the six restaurants with their towns, streets and area managers, the plan's name, and every reading of the month. It starts no server.

```bash
python make_cases.py           # writes cases.json
python make_cases.py --check   # says whether cases.json is what the script would write
```

Run it with the Python of the retailer's own environment. A test of the retailer, `demo-retailer/tests/test_food_safety_desk_cases.py`, fails when `cases.json` differs from what the script would write, or from what the service returns for a restaurant.

The service keeps one temperature log with a row a day. The desk shows it as four short logs (cold storage, hot holding, cooking and cleaning, deliveries), so that a line fits the pane and a phone. Each log names its columns. Every value the service returns is there once. A blank cleaning sign-off is written `(blank)`.

## Which engine it needs

The settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk), at a version that takes a settings folder kept outside its own repository: it reads `DESK_CONFIG`, `DESK_LIBRARY_DIR`, a `demo-replies.json` beside the settings, and the `case.queryFields`, `case.foldOnPhone`, `decisions[].proposalPrefix`, `draft.rowLabels` and `draft.summaryAboveRows` settings. That version is in `main` of the engine since 24 November 2026.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm install
DESK_CONFIG=../katonic-agent-catalog/retail/desks/food-safety/desk.config.json \
DESK_LIBRARY_DIR=../katonic-agent-catalog/retail/policy-library \
KATONIC_LIBRARY_NAME="Rowanmere policy library (invented)" \
LOCAL_USER=maelys.thornquay@rowanmere.invalid \
LOCAL_USER_NAME="Maelys Thornquay" \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json`. Without it the engine is the regulatory change desk |
| `DESK_LIBRARY_DIR` | A folder of Markdown files. Point it at `retail/policy-library`. The plan is read from there and is not copied into this folder |
| `DESK_ENV_FILE` | A settings file to read in place of `.env`, for the platform address, key and agent id |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY`, `KATONIC_AGENT_ID` | The platform's agent API, a key with the Chat scope, and the id of the built agent |
| `KATONIC_LIBRARY_NAME` | The name shown for the library in the findings and the register |
| `LOCAL_USER`, `LOCAL_USER_NAME` | The person the desk records when no sign-in stands in front of it. The demo user is an invented food safety lead |
| `SEED_DEMO` | `true` loads the six demo record checks on the first start. Open one and press "Ask the agent to draft" |

Build the agent from [`../../agents/food-safety-record-check/`](../../agents/food-safety-record-check/README.md). Its `instructions.md` is the same text as `agent-instructions.md` here. Its last section says what the agent does when the desk sends the case: it works from the message alone, reads nothing from the systems and saves nothing.

## How the plan reaches the agent

The desk reads the Markdown files in `DESK_LIBRARY_DIR` and sends the one that best matches the case, whole, in the same message as the records. It matches on the case's "Plan to check against" field (`case.queryFields` in the settings), not on the restaurant's name. For the demo cases, and for any case that leaves the field at its default, the match is `food-safety-plan-v5.0.md`. The other documents in the library (the staff handbook, the store procedures and the allergen matrix) are not sent. A plan field with no words in common with the library finds nothing, and the agent is told so.

The message with the instruction, a month of records and the plan is about 12,500 characters, inside the 15,000 the engine allows by default.

## Without a platform

The engine comes with a stand-in platform, `demo/fake-platform.js`, that plays the agent with canned text. Start it with the same `DESK_CONFIG` and point the desk's `KATONIC_BASE_URL` at it. It answers from [`demo-replies.json`](demo-replies.json) in this folder: one set of findings for each of the six demo record checks, following the right answers above. Every stand-in reply says on its first line that it is canned text. A record check you enter by hand gets one row saying the stand-in did not read the records.

The stand-in shows how the desk works. It does not test the agent, and it gives the same findings when the corrective actions are added. For a real check, build the agent and point the desk at it.

## How it was tested

On 24 November 2026 the desk was run against the stand-in through twenty scenarios in a headless browser. All twenty pass.

- The queue shows the six record checks, and each gets its findings.
- The rows, marks, counts and readings shown for each restaurant match the retailer's scenario list. The faults were also worked out again from the records in `cases.json` and the plan's limits: they are the listed ones and no others.
- The plan sent with each case is the food safety plan from `retail/policy-library`, and only that.
- Each decision: signing the monthly review, signing with a reason while a deviation is listed, asking the restaurant manager for corrective actions with its note, adding the corrective actions and seeing the deviations listed again as version 2, recording a decision on the unit for R-014 and R-047, and sending the findings back to the agent.
- A question to the agent, the register and its export, the form for a new record check, filters and search, and a reload.
- Four eyes: the person who entered a record check cannot decide it, on the page or by calling the desk directly. A second food safety lead can.
- At phone width no screen scrolls sideways and no line of a log wraps.

It was reviewed for visual design at desktop and phone width, in light and dark, and the settings were changed after the first round. The retailer's tests, with the test that keeps `cases.json` equal to the service, pass.

Not yet done: a run against a real agent on a platform, the platform's sign-in in front of the desk, and the desk deployed as an app. No food safety professional has reviewed the plan, the records or the findings.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label |
| `cases.json` | The six demo record checks, written by `make_cases.py` |
| `make_cases.py` | Builds `cases.json` from the invented retailer's records |
| `demo-replies.json` | The canned findings for the stand-in platform |
| `agent-instructions.md` | The agent's instructions, the same text as the agent folder's `instructions.md` |
