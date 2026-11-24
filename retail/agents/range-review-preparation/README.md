# Range Review Preparation

Prepares the pack for a category's range review and lists the lines below the company's own thresholds, each with the threshold. The buying team decides every listing and delisting.

| | |
|---|---|
| Type and form | Workflow, scheduled agent |
| What starts it | A clock, before each category's range review. A person can also name a category |
| How people meet it | The pack is sent to the buyer. It also works in a chat |
| Reads from | The company's pricing system: range review data by line and the thresholds. The stock system: stock on hand and recent sales |
| Changes | Saves its pack as a draft. The draft lists and delists nothing |
| State | Written. Not yet built on a platform |

## What it does

- Reads the thresholds first, and uses the limits they give.
- Reads the data of every line of the category: sales, margin, shelf facings, sales for each facing and availability.
- Lists each line that is below a threshold, once, with every threshold it is below and the figure. A line exactly on a threshold is not below it.
- Adds each listed line's days of stock cover, worked out from the stock system, and says when a line is also overstocked.
- Says so plainly when no line of the category is below a threshold.
- Saves the pack as a draft and says so only when the system says it was applied.
- Ends on one fixed line: "Nothing was listed or delisted. The buying team decides."

## What it does not do

- Say that a line should be delisted, kept, given more space or replaced.
- Give a reason for a line being below a threshold.
- List a line because it only looks weak. The thresholds decide.
- Prepare a pack for a category that does not exist: it names the eight that do.

## What you set up

- A model for the Reasoning tier.
- The company's pricing system, connected as an imported API, with the 3 operations listed for it in [`agent.yaml`](agent.yaml).
- The company's stock system, connected as an imported API, with the 2 operations listed for it in [`agent.yaml`](agent.yaml).

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Control Room, Tools, import the pricing system and the stock system from their OpenAPI addresses, one system at a time. For the invented retailer, those are the documents at `/pricing/openapi.json` and `/stock/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give each an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the 5 operations named in [`agent.yaml`](agent.yaml). Attach nothing else.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because a run saves a draft.
8. To run it on a clock, build a scheduled workflow that calls the agent once for each category before its review. This form is not written yet.

## Test results

Not yet built on a platform. No test has been run.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24, period 2026-10). The right answers are in the range review section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- `household`: `HH-6105` and `HH-6106` are below RT-1. `HH-6105` has 90.0 days of cover and is also overstocked.
- `frozen_food`: `FZ-5605` is below two thresholds, RT-2 and RT-3.
- `drinks`: `DR-5904` below RT-1 and `DR-5907` below RT-3. `DR-5903` is at a margin of exactly 20.0 percent and is not below.
- `fresh_produce`: no line is below a threshold.
- Ask it to delist batteries. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

The buying team decides every listing and delisting.
