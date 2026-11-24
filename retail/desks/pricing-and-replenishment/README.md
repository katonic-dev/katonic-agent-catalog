# Pricing and replenishment desk

The settings folder that turns the Katonic case desk into a desk for a retailer's merchants and buyers. Two kinds of case sit in one queue. A category's prices are set beside what two competitors publish and beside the pricing rules, and a price change is recommended only where the rules allow it. A supplier's lines are worked out by the replenishment rules, and one purchase order is drafted for the lines that run out. Each kind goes to its own agent. A person decides.

Rowanmere Group (an invented company in the invented country Meridia), its suppliers, the two competitors and every price, stock figure and order are invented.

## The two kinds of case

| Kind | Agent | What the agent does | What a person decides |
|---|---|---|---|
| Price change | [Price Optimization](../../agents/price-optimization/README.md) | For each line with a published competitor price: the reference price, the gap, and a decrease, an increase or a hold. A move a pricing rule forbids is held, and the rule is named | Approve the price changes, approve some and hold the rest, or close with no price change |
| Replenishment order | [Inventory Forecasting](../../agents/inventory-forecasting/README.md) | For each line of the supplier: the forecast, the days of cover and the days to the next delivery. One draft purchase order for the lines that run out | Approve the draft order, approve it with a changed quantity, hold it, or close with no order |

The desk sends the agent one message: the drafting instruction for the kind, then the case with its records and its rules. The agent works from that message. It reads nothing from the pricing system or the stock system and saves nothing.

**The desk records the decision and does nothing else.** It changes no price, places no order, tells no supplier anything, and calls no operation of the retailer's systems. "Approve the price changes" records that a named person approved them, and the draft as it read at that moment. The person makes the change in the pricing system. The same holds for an order.

## What the person sees

- **A queue of cases**, each with its kind and the number of lines in it.
- **The records beside the draft.** What the pricing and stock systems hold, with the rules, is on one side. The agent's draft is on the other.
- **One row for each line**, with the figures the rule needs, a mark and the reason in a sentence. Pressing a part of the count above the rows, such as "1 overstocked", shows only those rows.
- **The price changes, or the draft purchase order, on a card of its own** under the rows. "Edit the text" changes it before the decision, and the edit is kept as a new version.
- **The agent's proposal**, one line, and the button it points to.
- **The register** afterwards: who decided what, when, on which version, and with which agent.

### The marks

| Mark | Kind | Meaning |
|---|---|---|
| Decrease | Price change | Our price is above the reference price by more than the band, and every pricing rule allows the move down to it |
| Increase | Price change | Our price is below the reference price by more than the band, and every pricing rule allows the move up to it |
| Held by a rule | Price change | The line is outside the band and a pricing rule forbids the move. The rule is named. No other price is proposed |
| Hold | Price change | The gap is inside the band, the edge included. No change |
| To order | Replenishment order | The line runs out before its next delivery. The quantity is the one the replenishment rules give, in whole cases |
| No order | Replenishment order | The line does not run out before its next delivery |
| Overstocked | Replenishment order | More than 56 days of cover. No order. Listed for the buyer |
| Not checked | Both | A figure needed to work the line out was not with the case |

The agent's Summary carries no count of marks. The desk counts them from the table.

## The decisions

| Decision | Kind | What it records |
|---|---|---|
| Approve the price changes | Price change | The approval of the changes as drafted, in the person's name. One click |
| Approve some, hold the rest | Price change | Which changes are approved and which are held, and why |
| Close with no price change | Price change | Why no price changes. For a category where every line is inside the band, or a rule holds the only line outside it |
| Approve the draft order | Replenishment order | The approval of the draft purchase order, in the person's name. One click |
| Approve with a changed quantity | Replenishment order | The order as the person changed it, which quantity was changed and why |
| Hold the order | Replenishment order | Why nothing is ordered from this draft for now, and until when |
| Close with no order | Replenishment order | Why nothing is ordered. For a supplier with no line that runs out |
| Send back to the agent | Both | A note that the agent sees. The agent drafts again |

A case offers only the decisions of its kind, and the desk refuses any other. The person who entered a case cannot decide it.

## The twelve demo cases

| Case | Kind | What the agent should find |
|---|---|---|
| Ambient grocery | Price change | Six lines, all inside the band. No change |
| Chilled food | Price change | CH-5502 Salted butter is 8.7 percent above the reference price. Rule PR-4 forbids the decrease to 2.29: 2.5 days of stock cover. No change |
| Frozen food | Price change | FZ-5602 Garden peas is exactly 5.0 percent above. The edge of the band is inside it: a hold. No change |
| Bakery | Price change | Rule PR-1 forbids a decrease of BK-5701 White sliced loaf to 1.49: the margin would be 13.6 percent. No change |
| Fresh produce | Price change | FP-5804 Bananas: an increase from 1.15 to 1.25 |
| Drinks | Price change | DR-5901 Orange juice: a decrease from 2.69 to 2.49 |
| Household | Price change | HH-6102 Laundry liquid: a decrease from 8.99 to 8.49. Rule PR-3 forbids an increase of HH-6103 Kitchen towel to 2.49: a move of 13.7 percent |
| Personal care | Price change | Rule PR-3 forbids a decrease of PC-6604 Razor blades to 8.49: a move of 15.0 percent. No change |
| Ilvane Valley Dairy Ltd (SUP-301) | Replenishment order | CH-5502 87 cases (1,740 units) and CH-5505 73 cases (876 units). CH-5503 looks low and does not run out: an order arrives in 2 days |
| Tallowby Flour Mills Ltd (SUP-303) | Replenishment order | AG-4408 75 cases (750 units). AG-4410 has exactly 5.0 days of cover and 5 days of lead time: not a run-out |
| Orchard Gate Fresh Produce Ltd (SUP-304) | Replenishment order | FP-5801 75 cases (900 units), after the 360 units already on order. FP-5802 145 cases (1,160 units) |
| Drennock Home and Care Ltd (SUP-317) | Replenishment order | Nothing to order. HH-6105 Batteries is overstocked at 90.0 days. PC-6606 Toothpaste has exactly 56.0 days and is not |

These are the records the invented retailer holds when its date is 24 November 2026. [Its scenario list](../../../demo-retailer/SCENARIOS.md) gives the right answer for each line, under "Prices" and "Replenishment".

## Where the cases come from

`cases.json` is not typed by hand. [`make_cases.py`](make_cases.py) builds it from the seed of the invented retailer in [`demo-retailer/`](../../../demo-retailer/README.md). A price case carries every line of the category: price, cost, the competitors' published prices, stock on hand and sales in the last four weeks, and the pricing rules word for word. A replenishment case carries every line of the supplier: stock, sales, case size and open orders, the supplier's lead time and minimum order, and the replenishment rules word for word. The script works out which suppliers have a line that runs out. It starts no server.

```bash
python make_cases.py           # writes cases.json
python make_cases.py --check   # says whether cases.json is what the script would write
```

Run it with the Python of the retailer's own environment. A test of the retailer, `demo-retailer/tests/test_pricing_and_replenishment_desk_cases.py`, fails when `cases.json` differs from what the script would write, or when a case differs from what the service returns for that category or supplier.

## Which engine it needs

The settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk), at a version that takes a settings folder kept outside its own repository and reads the `routing` setting with a list of decisions for each kind, `draft.sections` for the price changes and the draft order, `draft.markIcons`, `draft.quietMarks`, `draft.tallyLabels`, `draft.rowFilter`, `draft.summaryAboveRows`, `case.foldOnPhone` and `intake.fields[].options`. That version is in `main` of the engine since 24 November 2026.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm install
DESK_CONFIG=../katonic-agent-catalog/retail/desks/pricing-and-replenishment/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
PRICE_OPTIMIZATION_AGENT_ID=<id of Price Optimization> \
INVENTORY_FORECASTING_AGENT_ID=<id of Inventory Forecasting> \
KATONIC_AGENT_ID=<either of the two, for a case of an unknown kind> \
LOCAL_USER=linnea.farthingale@rowanmere.invalid \
LOCAL_USER_NAME="Linnea Farthingale-Moss" \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json` |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `PRICE_OPTIMIZATION_AGENT_ID` | The agent for cases of the kind Price change. If it is empty, drafting such a case fails and says which setting to fill |
| `INVENTORY_FORECASTING_AGENT_ID` | The same, for Replenishment order |
| `KATONIC_AGENT_ID` | The agent for a case whose kind is neither of the two. The desk asks it only to say that the kind is not recognised, and such a case offers only "Send back to the agent" |
| `LOCAL_USER`, `LOCAL_USER_NAME` | The person the desk records when no sign-in stands in front of it. The demo user is an invented merchant |
| `SEED_DEMO` | `true` loads the twelve demo cases on the first start. Open one and press "Ask the agent to draft" |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: each case carries its records and its rules |

The kind of a case is the value of its "Kind of work" field, matched without regard to case.

Build the two agents from their folders. Each agent's own instructions tell it to read the retailer's systems and to save a draft there. The desk asks for another shape, so each agent needs one more section before the desk is pointed at it: [`agent-desk-sections.md`](agent-desk-sections.md) holds the two. The section and the drafting instruction for the kind in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine comes with a stand-in platform, `demo/fake-platform.js`, that plays the agents with canned text. Start it with the same `DESK_CONFIG` and point the desk's `KATONIC_BASE_URL` at it, with any value for the key and for each of the three agent ids. It answers from [`demo-replies.json`](demo-replies.json): one reply for each of the twelve demo cases, following the right answers above. Every stand-in reply says on its first line that it is canned text. A case you enter by hand gets one row saying the stand-in read none of the records.

The stand-in shows how the desk works. It does not test the agents.

## How it was tested

On 24 November 2026 the desk was run against the stand-in through twenty-three scenarios in a headless browser. All twenty-three pass.

- The queue shows the twelve cases, each with its kind.
- The right answers were worked out again from the text of each case, by the rules the case itself carries: the three changes the rules allow, the four moves they forbid with the rule for each, the hold exactly on the edge of the band, the five lines that run out with their cases and units, the two lines that look low and do not, and the overstocked line. They are the ones the retailer's scenario list gives.
- Each kind's draft comes from the agent its setting names, with its own instruction. Every message to an agent is under 9,000 characters.
- The rows, marks, prices, quantities, rules and proposals shown for all twelve cases match the scenario list, and the agent's proposal sits on the right button.
- Every decision: approve the price changes with one click, approve some and hold the rest, close with no price change, approve a draft order with one click, change a quantity in the draft order and approve it with a note, hold an order, close with no order, and send back to the agent.
- A decision of the other kind is refused. A kind whose agent setting is empty says which setting to fill. A kind the desk does not know offers only sending back.
- The register and its export, a question to the agent, the form for a new case, search by kind, by category, by supplier and by line, the filters, and a reload.
- Four eyes: the person who entered a case cannot decide it, on the page or by calling the desk directly, for each of the two kinds. A second merchant can.
- At phone width no screen scrolls sideways.

It was reviewed for visual design at desktop and phone width, in light and dark, and the settings and the cases script were changed after the first round. The retailer's test that keeps `cases.json` equal to the service passes.

Not yet done: a run against the two real agents on a platform, the desk section added to the two agent folders, the platform's sign-in in front of the desk, and the desk deployed as an app. No demo case holds two price changes, so "Approve some, hold the rest" was tried on a case with one. The queue has no filter by kind: a search for the kind's name lists its cases.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the `routing` setting with the two drafting instructions |
| `cases.json` | The twelve demo cases, written by `make_cases.py` |
| `make_cases.py` | Builds `cases.json` from the invented retailer's records |
| `demo-replies.json` | The canned replies for the stand-in platform |
| `agent-desk-sections.md` | The section each of the two agents needs before the desk is pointed at it |
