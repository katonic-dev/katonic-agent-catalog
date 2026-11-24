# Search Terms Analysis

Lists what shoppers searched for and did not find in a month, grouped by what they seem to have wanted, with the searches behind each group. The e-commerce team decides what to change.

| | |
|---|---|
| Type and form | Workflow, scheduled agent |
| What starts it | A clock, once a month, for the period just ended. A person can also name a period |
| How people meet it | The analysis is sent to the e-commerce team. It also works in a chat |
| Reads from | The company's catalogue system: a month of the shop's search log, and the product listings |
| Changes | Saves its analysis as a draft. The draft changes nothing in the shop |
| State | Written. Not yet built on a platform |

## What it does

- Reads the search log of the period and keeps the terms that found nothing.
- Groups those terms by what the shoppers seem to have wanted, and gives each group a plain name.
- Reads the listings, so that it can tell a product the shop does not sell from a product it sells that was spelled another way.
- Gives each term with its searches, and each group with its total, largest first.
- Says that the groups are its reading of the words, for a person to check.
- Saves the analysis as a draft and says so only when the system says it was applied.
- Ends on one fixed line: "Nothing in the shop was changed. The e-commerce team decides what to change."

## What it does not do

- Change the search, the range or a listing.
- Say that a product should be added to the range.
- List a term that found results, however few.
- Say who searched. The log holds terms and counts, and no shopper.
- Analyse a month that has not ended.

## What you set up

- A model for the Reasoning tier.
- The company's catalogue system, connected as an imported API, with the 3 operations listed for it in [`agent.yaml`](agent.yaml).

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Control Room, Tools, import the catalogue system from its OpenAPI address, one system at a time. For the invented retailer, that is the document at `/catalogue/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give each an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the 3 operations named in [`agent.yaml`](agent.yaml). Attach nothing else.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because a run saves a draft.
8. To run it on a clock, build a scheduled workflow that calls the agent once after the month ends. This form is not written yet.

## Test results

Not yet built on a platform. No test has been run.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24, period 2026-10). The right answers are in the search terms section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- Period `2026-10`: twenty terms found nothing, 2,429 searches, in five groups. The largest is milk made from plants, 597 searches, and the most searched term is `oat milk`, 301.
- Four terms are misspellings of products the shop sells: `yogurt`, `mozarella`, `spagetti`, `shampo`.
- `almond` found two results and is not on the list.
- Period `2026-11`: the month has not ended.
- Ask it to add oat milk to the range. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

The e-commerce team decides what to change in the shop.
