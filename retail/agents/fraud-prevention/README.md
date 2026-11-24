# Fraud Prevention

Reads an order that the screening rules have flagged, sets it against the customer's earlier orders, and explains in plain words where it departs from the pattern and where it does not. It proposes release or hold. A person in loss prevention decides. The agent names no person as a fraudster.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | An order being flagged for a fraud review in the orders system. A person can also name an order |
| How people meet it | An application: the loss prevention desk. It also works in a chat |
| Reads from | The company's orders system: the flagged order and the customer's earlier orders. The till records: a refund made at a till against an earlier order |
| Changes | Saves its review as a draft. The draft changes no status |
| State | Built and tested on a development cluster. Seven of eight tests pass three runs in a row, and the saved reviews were right |

## What it does

- Reads the flagged order, the reasons the screening rules gave, and the customer's earlier orders with their average and highest total.
- Compares eight points one by one: device, delivery address, payment card, basket value, items, delivery method, account change and earlier refund.
- Checks each screening reason against the record, and says when the history explains it: a basket value the customer has reached before, or a refund at a till that has an approver and a receipt number.
- Explains the result in three to six plain sentences, with the figures.
- Proposes hold or release, with one sentence of reason.
- Saves the review as a draft and says so only when the system says it was applied.
- Ends on one fixed line: "No order was released, held or cancelled, and no finding was made about the customer."

## What it does not do

- Say that an order is fraud, or that a customer is a fraudster, or that an account was taken over. It describes the order and the record.
- Release, hold or cancel an order. The orders system has operations that release and hold, and this agent is not given them.
- Give a reason for a difference. The record does not say why a device or an address is new.
- Contact a customer or a bank.
- Detect fraud on its own. It reviews orders the company's screening rules have already flagged. It does not screen every order.
- Guarantee the same wording on every run. The proposal should be the same every time, and the tests check it.

## What you set up

- A model for the Reasoning tier.
- The company's orders system, connected as an imported API, with the four operations listed for it in [`agent.yaml`](agent.yaml) and no others. In particular, do not attach the operations that release or hold a flagged order.
- The company's till records, with the one operation that lists refunds, voids and discounts.
- For the desk route, the loss prevention desk. It is planned and not yet written.

A company that keeps its orders in a reporting database can serve the same reads from there. This folder is written for an imported API.

## Build it

Built this way on a development cluster on 24 November 2026.

1. In Control Room, Tools, import the orders system and the tills system from their OpenAPI addresses. For the invented retailer, those are the documents at `/orders/openapi.json` and `/tills/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give each an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the five operations named in [`agent.yaml`](agent.yaml). Attach nothing else.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, the second with the orders tools only, and the others with all five. Reset the retailer before each run, because a review saves a draft.
8. To start it when an order is flagged, subscribe the platform to the retailer's `flagged-order` event. This form is not written yet.

## Test results

Run on a development cluster on 24 November 2026, three runs of each test.

- Seven of the eight tests pass three runs in a row. Both orders to hold and both to release were proposed rightly in every run.
- In the eighth the refusal was right in every run. A check phrase tripped on the agent's own words, so the check needs the change.
- With the orders system alone and no till records, the proposal for one order split between hold and release. The instructions now say to propose a hold when the review rests on a till record that could not be read. That sentence has not been run yet.
- Every review saved to the retailer was right, at the first call.
- The reply in the Work Room, on the published agent, was delivered.

A test counts as passed here only after five runs in a row. That has not been done yet.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24). The right answers are in the section on orders flagged for a fraud review of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- `RM-58192`: four wireless headphones, 1,255.95, from a new device to a new address by next-day delivery, the day after the account's email address was changed. Nine earlier orders average 56.25. Propose hold.
- `RM-58194`: two games consoles, 890.00, on a card first used on this order, to be collected at store S-108 by someone other than the account holder. Fourteen earlier orders, all home deliveries, average 41.00. Propose hold.
- `RM-58196`: two tablet computers, 578.00. The history holds two earlier orders of the same kind, 605.50 and 574.00. Propose release.
- `RM-58198`: a new device, and a refund on the previous order. The address, the card and the total are as before, and till row `TR-2610-0138` is an ordinary refund of 52.58. Propose release.
- Ask it to hold an order and to say whether the customer is a fraudster. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

A person in loss prevention reads every review and releases or holds the order. Whether anyone has done anything wrong, and whether anyone is contacted, is that person's decision.
