# Restaurant Performance Review

Sets a restaurant's sales, labour and food waste for a period against its plan and its peer group, and lists where it departs, with the figures. The area manager draws the conclusions.

| | |
|---|---|
| Type and form | Workflow, scheduled agent |
| What starts it | A clock, once a month, for the period just ended. A person can also name a restaurant and a period |
| How people meet it | Inside the company's own system: the review is sent to the area manager. It also works in a chat |
| Reads from | The company's reporting on restaurant performance (figures, plan, peer group, the company's rules) and its restaurant list |
| Changes | Saves its review as a draft. The draft changes no figure |
| State | Built and tested on a development cluster. All eight tests pass three runs in a row, and the saved reviews were right |

## What it does

- Reads the restaurant's sales, labour cost, labour hours and food waste for the period, each with its plan, and the figures of its peer group.
- Applies the company's own rules, which come with the figures: how far from plan counts as a departure, and how many times the peer average.
- Lists each departure with the restaurant's figure, the plan figure or the peer average, and the difference.
- Lists a figure that is well ahead of plan as a departure too, and says that it is ahead.
- Says so plainly when nothing departs.
- Gives the difference from plan for the two months before, figures only.
- Writes at most three questions for the area manager to look into, with no answer in them.
- Saves the review as a draft and says so only when the system says it was applied.
- Ends on one fixed line: "The figures show what departs, not why. The area manager draws the conclusions."

## What it does not do

- Say why a figure departs.
- Say anything about a restaurant manager or any colleague.
- Propose an action, a roster change or a new plan.
- Rank restaurants or give a score of its own.
- Guarantee the arithmetic of a model. The system gives every difference from plan ready made, and the instructions tell the agent to copy it. The comparison with the peer group is one division, which a model can get wrong. Run the tests on your own model before you rely on them.

## What you set up

- A model for the Reasoning tier.
- The company's reporting on restaurant performance, connected as an imported API, with the four operations listed in [`agent.yaml`](agent.yaml): list the periods, read a restaurant's figures, read its peer group's figures, and save a review as a draft.
- The company's store and restaurant list, connected as an imported API, with the one operation that reads a site.

## Build it

Built this way on a development cluster on 24 November 2026.

1. In Control Room, Tools, import the performance system and the stores system from their OpenAPI addresses. For the invented retailer, those are the documents at `/performance/openapi.json` and `/stores/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give each an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the five operations named in [`agent.yaml`](agent.yaml). Attach nothing else.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because a review saves a draft.
8. To run it on a clock, build a scheduled workflow that calls the agent once for each restaurant after the month ends. This form is not written yet.

## Test results

Run on a development cluster on 24 November 2026, three runs of each test.

- All eight tests pass three runs in a row.
- Every review saved to the retailer was right, at the first call.
- The reply in the Work Room, on the published agent, was delivered.

A test counts as passed here only after five runs in a row. That has not been done yet.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24, period 2026-10). The right answers are in the restaurant performance section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- `R-047`: sales 18.6 percent below plan, labour cost 8.5 percent above, labour hours 9.0 percent above. Nothing against the peer group.
- `R-031`: food waste 110.1 percent above plan, and 2.1 times the average of the other restaurants in its group.
- `R-022`: ahead of plan. Sales 7.4 percent above and food waste 12.0 percent below are both listed as departures.
- `R-058`: no departure.
- `S-101`: a store. It must say there are no figures and write nothing.
- Ask who is to blame at `R-047`. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

The area manager draws the conclusions, finds out why a figure departs, and agrees the actions with the restaurant.
