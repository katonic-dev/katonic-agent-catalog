# Loss prevention desk

The settings folder that turns the Katonic case desk into a desk for a retailer's loss prevention team. Three kinds of case sit in one queue. An order that the screening rules flagged is set against the customer's earlier orders. One site's refunds, voids and discounts are checked against the till rules. A stock count is set against the tolerance. Each kind goes to its own agent. A person decides.

Rowanmere Group (an invented company in the invented country Meridia), its customers, its colleagues and every order, till row and stock count are invented.

## The three kinds of case

| Kind | Agent | What the agent does | What a person decides |
|---|---|---|---|
| Flagged order | [Fraud Prevention](../../agents/fraud-prevention/README.md) | Compares the order with the customer's earlier orders on eight points, and says in plain words where it departs and where the history explains it | Release the order, or hold it |
| Till audit | [Refund and Discount Audit](../../agents/refund-and-discount-audit/README.md) | Checks every till row of one site against the till rules, lists each row outside a rule with the rule, and drafts the note to the store manager | Close the rows as reviewed, or open a review with the store manager |
| Stock loss | [Shrink Analysis](../../agents/shrink-analysis/README.md) | Sets a store's loss, or a line's loss in all stores together, against the tolerance, and says where the loss sits | Note the loss as explained, or ask for a recount |

The desk sends the agent one message: the drafting instruction for the kind, then the case with its records. The agent works from that message. It reads nothing from the retailer's systems and saves nothing.

**The desk records the decision and does nothing else.** It releases no order, holds none, changes no till row and no count, sends nothing to a store manager, and calls no operation of the retailer. "Hold the order" records that a named person decided the order is held, and why. The person holds it in the orders system.

## Nothing here accuses a person

- A flag is a request to look. A review describes the order and the record. It makes no finding about the customer, and a customer appears by id only.
- A till row outside a rule is a row for an auditor to look at, and an auditor reviews each one. The rows carry cashier ids as the records give them. No name is used, and no reason is given for a row.
- The note of a till review is written to the store manager. It lists rows and rules, and carries no cashier id, no approver id and no name. It is never to or about a named colleague.
- A count says that stock is missing, and never why. The analysis gives no cause and names no one. The till figures beside a store's count are counts and totals, and no till row can be tied to a line that lost stock.

## What the person sees

- **A queue of cases**, each with its kind and one fact in its title: the order's total, how many till rows, or the loss percent.
- **The records beside the draft.** What the retailer's systems hold is on one side. The agent's draft is on the other.
- **One row for each thing compared**: a point of the order, a till row outside a rule, or the store or line against its limit, each with a mark.
- **A card under the rows** for the longer text: the order in plain words, where the listed till rows sit, the note to the store manager, or what the tills hold for a store. "Edit the text" changes the note's wording before the decision, and the edit is kept as a new version.
- **The agent's proposal**, one line, and the button it points to.
- **The register** afterwards: who decided what, when, on which version, and with which agent.

### The marks

| Mark | Kind | Meaning |
|---|---|---|
| In line with the history | Flagged order | On this point the order is the same as the customer's earlier orders |
| Explained by the history | Flagged order | The point is new on this order, and the rest of the record explains it |
| Departs from the pattern | Flagged order | The point is new, or far from every earlier order, and nothing in the history explains it. It describes the order |
| Outside a rule | Till audit | The row is outside a till rule. A row for an auditor to look at |
| Within the rules | Till audit | No row of the site is outside a rule |
| Beyond tolerance | Stock loss | The loss percent is above the limit |
| Within tolerance | Stock loss | The loss percent is on or under the limit |
| Where the loss sits | Stock loss | The lines or the stores with the most loss value. No limit is applied and no cause is given |
| Not checked | All | The record needed was not with the case |

The agent's Summary carries no count of marks. The desk counts them from the table.

## The decisions

| Decision | Kind | What it records |
|---|---|---|
| Release the order | Flagged order | The decision to release, in the person's name. One click when every point is in line with the history. Needs a reason when a point is not |
| Hold the order | Flagged order | Why the order is held, written about the order and not about the customer |
| Close the rows as reviewed | Till audit | What the auditor found on the rows |
| Open a review with the store manager | Till audit | That the note goes to the store manager, who sends it, and the note as it reads |
| Note the loss as explained | Stock loss | What explains the loss, for example that it is within tolerance |
| Ask for a recount | Stock loss | What is counted again, and by when |
| Ask the agent again | All | A note that the agent sees. The agent drafts again |

A case offers only the decisions of its kind, and the desk refuses any other. The person who entered a case cannot decide it.

## The fourteen demo cases

| Case | Kind | What the agent should find |
|---|---|---|
| RM-58192, USD 1,255.95 | Flagged order | Departs on six points: device, delivery address, basket value, items, next-day delivery, and an email address changed the day before. Hold |
| RM-58194, USD 890.00 | Flagged order | Departs on four points: a new card, the basket value, the items, and a first click and collect order with a collector who is not the account holder. Hold |
| RM-58196, USD 578.00 | Flagged order | The value looks high and the history explains it: two earlier orders of the same kind, USD 605.50 and USD 574.00. Release |
| RM-58198, USD 77.00 | Flagged order | A new device, with the same address, card and usual value. The refund on the previous order is an ordinary till refund. Release |
| TA-2610-S106, 27 till rows | Till audit | Twelve rows outside a rule: TC-1 five times, TC-2 four, TC-3 three, TC-4 two. Review with the store manager |
| TA-2610-S101, 14 till rows | Till audit | Two rows: a refund of 95.00 with no approver (TC-1) and a discount of 30 percent with no reason code (TC-3). Review |
| TA-2610-S104, 6 till rows | Till audit | Two rows: a refund of 55.25 with no approver (TC-1) and a void of 88.00 after payment with no second person (TC-4). Review |
| TA-2610-R117, 9 till rows | Till audit | No row outside a rule. Two rows are exactly on a limit and within the rules. Close as reviewed |
| SC-2610-103, store S-103 | Stock loss | 2.44 percent against a limit of 1.5. Beyond tolerance. Recount |
| SC-2610-106, store S-106 | Stock loss | 2.50 percent against 1.5. Beyond tolerance. Recount |
| SC-2610-102, store S-102 | Stock loss | 1.33 percent against 1.5. Within tolerance. No recount |
| SL-2610-DR5905, red wine | Stock loss | 6.68 percent against a line limit of 2.5, all stores together. Recount |
| SL-2610-HH6105, batteries | Stock loss | 5.81 percent against 2.5. Recount |
| SL-2610-PC6604, razor blades | Stock loss | 5.48 percent against 2.5. Recount |

These are the records the invented retailer holds when its date is 24 November 2026. [Its scenario list](../../../demo-retailer/SCENARIOS.md) gives the right answer for each.

A till audit is one site's rows for the period. The retailer holds 180 till rows for the month, and that is too long for one case, so the desk takes the month one site at a time: the site with the most rows outside the rules, two sites with two each, and a site with none.

## Where the cases come from

`cases.json` is not typed by hand. [`make_cases.py`](make_cases.py) builds it from the seed of the invented retailer in [`demo-retailer/`](../../../demo-retailer/README.md). Each case carries the records its agent needs: the order with the flag, the customer's earlier orders and the till row of any earlier refund; the till rules with one site's rows; or the count with the tolerance, the lines with the most loss value and the store's till figures. The script reads none of the service's answer sets. It starts no server.

```bash
python make_cases.py           # writes cases.json
python make_cases.py --check   # says whether cases.json is what the script would write
```

Run it with the Python of the retailer's own environment. A test of the retailer, `demo-retailer/tests/test_loss_prevention_desk_cases.py`, fails when `cases.json` differs from what the script would write, when a case differs from what the service returns, or when the rows outside a rule that can be read from a case are not the ones the service holds.

## Which engine it needs

The settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk), at a version that takes a settings folder kept outside its own repository and reads the `routing` setting with a list of decisions and its own wording for each kind, `draft.sections`, `draft.markIcons`, `draft.quietMarks`, `draft.summaryAboveRows`, lines with labels in a row, `case.foldOnPhone` and `intake.fields[].options`. That version is in `main` of the engine since 24 November 2026.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm install
DESK_CONFIG=../katonic-agent-catalog/retail/desks/loss-prevention/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
FRAUD_PREVENTION_AGENT_ID=<id of Fraud Prevention> \
REFUND_AND_DISCOUNT_AUDIT_AGENT_ID=<id of Refund and Discount Audit> \
SHRINK_ANALYSIS_AGENT_ID=<id of Shrink Analysis> \
KATONIC_AGENT_ID=<any one of the three, for a case of an unknown kind> \
LOCAL_USER=merrin.ashcombe-vale@rowanmere.invalid \
LOCAL_USER_NAME="Merrin Ashcombe-Vale" \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json` |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `FRAUD_PREVENTION_AGENT_ID` | The agent for cases of the kind Flagged order. If it is empty, drafting such a case fails and says which setting to fill |
| `REFUND_AND_DISCOUNT_AUDIT_AGENT_ID` | The same, for Till audit |
| `SHRINK_ANALYSIS_AGENT_ID` | The same, for Stock loss |
| `KATONIC_AGENT_ID` | The agent for a case whose kind is none of the three. The desk asks it only to say that the kind is not recognised, and such a case offers only "Ask the agent again" |
| `LOCAL_USER`, `LOCAL_USER_NAME` | The person the desk records when no sign-in stands in front of it. The demo user is an invented loss prevention lead |
| `SEED_DEMO` | `true` loads the fourteen demo cases on the first start. Open one and press "Ask the agent to draft" |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: each case carries its records |

The kind of a case is the value of its "Kind of work" field, matched without regard to case.

Build the three agents from their folders. Each agent's own instructions tell it to read the retailer's systems and to save a draft there. The desk asks for another shape, so each agent needs one more section before the desk is pointed at it: [`agent-desk-sections.md`](agent-desk-sections.md) holds the three. The section and the drafting instruction for the kind in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine comes with a stand-in platform, `demo/fake-platform.js`, that plays the agents with canned text. Start it with the same `DESK_CONFIG` and point the desk's `KATONIC_BASE_URL` at it, with any value for the key and for each of the four agent ids. It answers from [`demo-replies.json`](demo-replies.json): one reply for each of the fourteen demo cases, following the right answers above. Every stand-in reply says on its first line that it is canned. A case you enter by hand gets one row saying the stand-in read none of the records.

The stand-in shows how the desk works. It does not test the agents.

## How it was tested

On 24 November 2026 the desk was run against the stand-in through twenty-three scenarios in a headless browser. All twenty-three pass.

- The queue shows the fourteen cases, each with its kind.
- The right answers were worked out again from the text of each case, by the till rules and the tolerance: the rows outside a rule with their rules, the stores and lines beyond tolerance, the averages of the earlier orders. They are the ones the retailer's scenario list gives.
- Each kind's draft comes from the agent its setting names, with its own instruction. Every message to an agent is under 9,500 characters.
- What is shown for all fourteen cases matches the scenario list: which orders to hold and which to release and why, each row outside a rule with its rule, each store and line with its figures. The agent's proposal sits on the right button.
- Every decision: release with one click, release with a reason while a point is not in line, hold, open a review as drafted and after editing the note, close the rows as reviewed, ask for a recount, note the loss as explained, and ask the agent again.
- The note to the store manager lists rows and rules and carries no cashier id. No screen, note, document or export holds a word that accuses a person.
- A decision of another kind is refused. A kind whose agent setting is empty says which setting to fill. A kind the desk does not know offers only asking again.
- The register and its export, a question to the agent, the form for a new case, search by kind, by site and by number, the filters, and a reload.
- Four eyes: the person who entered a case cannot decide it, on the page or by calling the desk directly, for each of the three kinds. A second loss prevention lead can.
- At phone width no screen scrolls sideways.

It was reviewed for visual design at desktop and phone width, in light and dark, and the settings and the cases script were changed after each of two rounds. The retailer's test that keeps `cases.json` equal to the service passes.

Not yet done: a run against the three real agents on a platform, the desk section added to the three agent folders, the platform's sign-in in front of the desk, and the desk deployed as an app. The queue has no filter by kind: a search for the kind's name lists its cases.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the `routing` setting with the three drafting instructions |
| `cases.json` | The fourteen demo cases, written by `make_cases.py` |
| `make_cases.py` | Builds `cases.json` from the invented retailer's records |
| `demo-replies.json` | The canned replies for the stand-in platform |
| `agent-desk-sections.md` | The section each of the three agents needs before the desk is pointed at it |
