# Price Optimization

Recommends a decrease, an increase or a hold for each line that has a published competitor price, with the reason, and proposes no price the company's pricing rules forbid. A merchant approves every change.

| | |
|---|---|
| Type and form | Workflow, scheduled agent |
| What starts it | A clock, once a week. A person can also ask for the whole price file or for one line |
| How people meet it | An application: the pricing and replenishment desk. It also works in a chat |
| Reads from | The company's pricing system: the price file, the competitors' published prices and the pricing rules. The stock system: stock on hand and recent sales |
| Changes | Saves its recommendations as a draft. The draft changes no price |
| State | Written. Not yet built on a platform |

## What it does

- Reads the pricing rules first, and uses the limits and the method they give.
- Takes the lower published competitor price as the reference price of a line, and works out the gap.
- Recommends a hold inside the band, and a move to the reference price outside it.
- Checks the move against every rule: the floor margin, the price endings, the maximum weekly move, and the rule that a line running short is not reduced. The last one needs days of cover, which it works out from the stock system.
- Where a rule forbids the move, recommends a hold and names the rule. It puts no other price in its place.
- Gives the reason for every line, with the figures.
- Saves the recommendations as a draft and says so only when the system says it was applied.
- Ends on one fixed line: "No price was changed. A merchant approves every change."

## What it does not do

- Change a price, or approve its own recommendations.
- Propose a price the rules forbid, or a price of its own between ours and the competitor's.
- Recommend anything for a line with no published competitor price.
- Say what a competitor will do next.
- Guarantee its arithmetic. A gap, a move and a margin are worked out line by line, and a model can slip. The system refuses a price that breaks the margin, ending or move rules, and the merchant checks the rest. For a large price file, do the sums in a code step and leave the wording to the model: that form is not written yet.

## What you set up

- A model for the Reasoning tier.
- The company's pricing system, connected as an imported API, with the 4 operations listed for it in [`agent.yaml`](agent.yaml).
- The company's stock system, connected as an imported API, with the 2 operations listed for it in [`agent.yaml`](agent.yaml).
- For the desk route, the pricing and replenishment desk. It is planned and not yet written.

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Control Room, Tools, import the pricing system and the stock system from their OpenAPI addresses, one system at a time. For the invented retailer, those are the documents at `/pricing/openapi.json` and `/stock/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give each an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the 6 operations named in [`agent.yaml`](agent.yaml). Attach nothing else: the operation that changes a record (`approve_price_changes`) stays out of this agent on purpose.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because a run saves a draft.
8. To run it on a clock, build a scheduled workflow that calls the agent once a week. This form is not written yet.

## Test results

Not yet built on a platform. No test has been run.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24, period 2026-10). The right answers are in the prices section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- The whole price file: three changes the rules allow (`DR-5901` down to 2.49, `HH-6102` down to 8.49, `FP-5804` up to 1.25) and four holds a rule forces (`BK-5701` PR-1, `PC-6604` PR-3, `CH-5502` PR-4, `HH-6103` PR-3).
- `CH-5502` Salted butter: the price rules alone would allow a cut to 2.29. Its 2.5 days of stock cover forbid it.
- `FZ-5602` Garden peas: exactly 5.0 percent above the reference price, so a hold.
- `AG-4403` Pasta sauce: no competitor publishes a price, so no recommendation.
- Ask it to approve the changes. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

A merchant approves every price change, and decides what to do where the rules forbid the move the method asks for.
