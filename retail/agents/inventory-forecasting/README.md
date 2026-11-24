# Inventory Forecasting

Finds the lines that run out before their next delivery, works out the cases to order under the company's own rules, and drafts a purchase order for each supplier. A buyer approves the plan before any order is placed.

| | |
|---|---|
| Type and form | Workflow, scheduled agent |
| What starts it | A clock, once a week. A person can also ask for the plan or about one line |
| How people meet it | An application: the pricing and replenishment desk. It also works in a chat |
| Reads from | The company's stock system: stock on hand, recent sales, supply terms with open orders, and the replenishment rules. The purchasing system: the supplier's record |
| Changes | Saves its plan as a draft, with draft purchase orders. The draft places no order |
| State | Built and tested on a development cluster. A question about one line is answered rightly. The whole weekly plan is not reliable: it was right in five runs of ten |

## What it does

- Reads the replenishment rules first, and uses the method and the limits they give.
- Works out the forecast and the days of cover of every line from the last four weeks' sales, and calls the forecast a forecast.
- Finds the lines whose cover is shorter than the days to their next delivery: the earliest open order, or the lead time when nothing is on order.
- Works out the cases for each of those lines, with stock on hand and units on order taken off, rounded up to whole cases.
- Reads the supplier's record for each draft order, and says when the purchasing system holds none.
- Lists the overstocked lines for the buyer, with no order.
- Saves the plan as a draft and says so only when the system says it was applied.
- Ends on one fixed line: "No order was placed. A buyer approves the plan."

## What it does not do

- Place an order, approve a plan or tell a supplier anything.
- Order for a line that does not run out, however low it looks.
- Adjust a quantity for a promotion, the weather or a hunch. The rules give the quantity and the buyer changes it.
- Guarantee its arithmetic. Sixty lines are worked out one by one and a model can slip. The buyer checks the plan. For a large range, do the sums in a code step: that form is not written yet.

## What you set up

- A model for the Reasoning tier.
- The company's stock system, connected as an imported API, with the 4 operations listed for it in [`agent.yaml`](agent.yaml).
- The company's purchasing system, connected as an imported API, with the 1 operation listed for it in [`agent.yaml`](agent.yaml).
- For the desk route, the pricing and replenishment desk. It is planned and not yet written.

## Build it

Built this way on a development cluster on 25 November 2026.

1. In Control Room, Tools, import the stock system and the purchasing system from their OpenAPI addresses, one system at a time. For the invented retailer, those are the documents at `/stock/openapi.json` and `/purchasing/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give each an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the 5 operations named in [`agent.yaml`](agent.yaml). Attach nothing else: the operation that changes a record (`approve_replenishment_plan`) stays out of this agent on purpose.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because a run saves a draft.
8. To run it on a clock, build a scheduled workflow that calls the agent once a week. This form is not written yet.

## Test results

Run on a development cluster on 24 and 25 November 2026, three runs of each test.

- A question about one line is answered rightly: three tests pass three runs in a row and a fourth passes two of three.
- The whole weekly plan is not reliable. It was saved right in five runs of ten across the texts tried, and in two runs of three on the instructions here.
- The five lines that run out are nearly always in the plan. The fault is extra lines that do not run out: in one run five lines with 15 to 19 days of cover were ordered against 10 days to delivery.
- Comparing days of cover with days to delivery over sixty lines is arithmetic the model does without a tool. A step in code that does the comparison is the cure. It is not built.
- One sentence was added after the first round: name an open order by its reference.
- One test asks two things and its checks want four, so it fails on a right answer. The check needs the change.
- The reply in the Work Room, on the published agent, was delivered. The plan it saved was wrong in the way described above.

A test counts as passed here only after five runs in a row. That has not been done yet.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24, period 2026-10). The right answers are in the replenishment section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- The whole plan: five lines run out (`AG-4408` 75 cases, `CH-5502` 87, `CH-5505` 73, `FP-5801` 75, `FP-5802` 145), in three draft orders, for SUP-301, SUP-303 and SUP-304.
- `FP-5801` Green peppers: 360 units are already on order, due in four days, and come off the quantity.
- `CH-5503` Unsalted butter: 2.5 days of cover, and an order due in two days. It does not run out, so no order.
- `AG-4410` Pizza flour: exactly 5.0 days of cover and a lead time of 5 days. No order.
- Three lines are overstocked: `DR-5904`, `FZ-5604` and `HH-6105`. `PC-6606` at exactly 56.0 days is not.
- Ask it to approve the plan and send the orders. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

A buyer approves every plan before an order is placed, and may change any quantity.
