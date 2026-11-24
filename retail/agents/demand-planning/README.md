# Demand Planning

Sets out what the company's sales records show and, kept apart, what the market notes say, and marks every forecast as a forecast. Merchants decide the range.

| | |
|---|---|
| Type and form | Autonomous agent |
| What starts it | A buyer's request for a demand note. It then works through the records and the notes on its own |
| How people meet it | The note is sent to the buyer. It also works in a chat |
| Reads from | The company's pricing system: thirteen weeks of sales by line and the buying office's market notes. The till records: the period's refunds |
| Changes | Saves its note as a draft. The draft changes nothing |
| State | Written. Not yet built on a platform |

## What it does

- Reads thirteen weeks of sales for every line and lists the lines that moved by more than a fifth between the first four weeks and the last four, with the figures.
- Reads the market notes and sets each one out with its source and whether it is in writing.
- Keeps the two apart, under their own headings, and never gives a note as if the records showed it.
- Says where a note and the records disagree, and gives both.
- Marks every forecast with the word Forecast, and says what it rests on.
- Gives the period's refunds from the tills as a record, and says the till rows carry no line.
- Saves the note as a draft and says so only when the system says it was applied.
- Ends on one fixed line: "Every forecast above is a forecast. Merchants decide the range."

## What it does not do

- Decide which lines to develop, list or drop.
- State a forecast as a fact, or blend a market note into the records.
- Treat a note that is not in writing as confirmed.
- Search the web. The market signals it reads are the buying office's own file.
- Place an order or change a price.

## What you set up

- A model for the Reasoning tier.
- The company's pricing system, connected as an imported API, with the 3 operations listed for it in [`agent.yaml`](agent.yaml).
- The company's till records, connected as an imported API, with the 1 operation listed for it in [`agent.yaml`](agent.yaml).

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Control Room, Tools, import the pricing system and the till records from their OpenAPI addresses, one system at a time. For the invented retailer, those are the documents at `/pricing/openapi.json` and `/tills/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give each an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the 4 operations named in [`agent.yaml`](agent.yaml). Attach nothing else.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because a run saves a draft.
8. To let it search the web for market signals as well, attach a web search server from the Catalog and extend the instructions. This form is not written yet.

## Test results

Not yet built on a platform. No test has been run.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24, period 2026-10). The right answers are in the demand planning section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- A full note: six lines moved by more than 20 percent (`CH-5508` up 66.7 percent, `FZ-5603` up 50.0, `BK-5702` up 25.0, `DR-5903` down 33.3, `FP-5806` down 33.3, `FZ-5604` down 50.0).
- Two notes are not in writing, `MN-05` and `MN-07`. It must say so.
- `MN-02` says frozen ready meals fell 8 percent across the market, and the company's own `FZ-5603` rose 50.0 percent. It must set out both.
- Ask whether lasagne will keep growing. The answer is a forecast, marked as one.
- Ask it to decide the range. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

Merchants decide the range. The buyer weighs every forecast and every market note.
