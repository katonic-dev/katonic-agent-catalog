# Promotion Review

Sets a finished promotion against its plan: what sold, what it displaced, what it cost and what it did to profit. The category manager draws the conclusions.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A promotion ending and its result arriving in the pricing system. A person can also name a promotion |
| How people meet it | The review is sent to the buyer. It also works in a chat |
| Reads from | The company's pricing system: the promotion's plan, result, the 14 days before, its neighbouring lines and its costs. The till records: discounts rung by hand on the same days |
| Changes | Saves its review as a draft. The draft changes nothing |
| State | Built and tested on a development cluster. The promotion's own figures were saved right in 21 runs of 24; the count of till discounts is not steady |

## What it does

- Reads the promotion and says so when it is still running and has no result to review.
- Sets units sold against the plan, as a percent, and against the 14 days before.
- Lists each neighbouring line whose units fell, with the units and the profit lost.
- Adds up the net effect on profit the way the record says: profit in the promotion, minus profit before, minus profit lost on neighbours, minus the display cost, plus the supplier's funding.
- Gives the discounts rung by hand at the stores' tills on the same days, as a count and a total, and says a till row carries no line.
- Saves the review as a draft and says so only when the system says it was applied.
- Ends on one fixed line: "The figures are set out. The category manager draws the conclusions."

## What it does not do

- Say that a promotion succeeded or failed, or that it should run again.
- Review a promotion that is still running.
- Tie a till discount to the promoted line. The till rows do not say what was sold.
- Guarantee its arithmetic. The net effect is a sum of five figures and a model can slip. The category manager checks it.

## What you set up

- A model for the Reasoning tier.
- The company's pricing system, connected as an imported API, with the 3 operations listed for it in [`agent.yaml`](agent.yaml).
- The company's till records, connected as an imported API, with the 1 operation listed for it in [`agent.yaml`](agent.yaml).

## Build it

Built this way on a development cluster on 25 November 2026.

1. In Control Room, Tools, import the pricing system and the till records from their OpenAPI addresses, one system at a time. For the invented retailer, those are the documents at `/pricing/openapi.json` and `/tills/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give each an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the 4 operations named in [`agent.yaml`](agent.yaml). Attach nothing else.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because a run saves a draft.
8. To start it when a promotion ends, add a webhook trigger on the retailer's `promotion-ended` event. This form is not written yet.

## Test results

Run on a development cluster on 25 November 2026, three runs of each test.

- The review saved to the retailer was right in 21 runs of 24. The three wrong ones left one neighbouring line out. A sentence was added, and the three runs after it were right.
- The total of till discounts is not steady: right in 5 of 21 runs on the test page, and in 3 of 3 in the Work Room. The cause was not found.
- The first save was refused every time until the findings were asked for as a list, one sentence to an entry. After that change every save went through.
- Three tests gave the right answer and tripped on how a negative amount or a date was written. Those checks are corrected here and have not been run again.
- The two-turn test in the Work Room, on the published agent, passed three runs in a row.

A test counts as passed here only after five runs in a row. That has not been done yet.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24, period 2026-10). The right answers are in the promotions section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- `PM-3101`: sold 1,040 units against a plan of 400 (260.0 percent) and took 1,167.20 from profit. It sold well and lost money.
- `PM-3102`: sold 640 against 600, and `BK-5705` Fruit scones fell by 160 units (113.60). Net effect -262.00.
- `PM-3103`: net effect 165.95 once the supplier's funding of 200.00 is counted.
- `PM-3107`: still running, so there is nothing to review.
- Ask whether to run the fish promotion again. It must leave that to the category manager.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

The category manager draws the conclusions and decides what follows.
