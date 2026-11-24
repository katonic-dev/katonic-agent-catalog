# Delivery Discrepancy

Sets a delivery note against the purchase order, the goods received and the supplier's invoice, lists what does not match with each difference as an amount net of tax, and drafts the claim to the supplier. A receiving or accounts lead sends every claim.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A new delivery note arriving in the purchasing system. A person can also name a delivery note |
| How people meet it | An application: the accounts payable desk. It also works in a chat |
| Reads from | The company's purchasing system: delivery notes, purchase orders, goods received and supplier invoices |
| Changes | Saves its claim as a draft. The draft sends nothing and changes no status |
| State | Written. Not yet built on a platform |

## What it does

- Reads the delivery note with what was written on it at the dock, the purchase order with its prices and its buyer, the goods received against the order, and the invoice for the order if there is one.
- Compares each line of the note with what was booked in.
- Gives each difference one kind from the records: short delivery, wrong item or damaged. The amount is the quantity not booked in times the price on the order, net of tax.
- Names anything that arrived and is not on the order, with no amount.
- Says in one sentence when an invoice bills more than was booked in.
- Drafts the claim to the supplier, or says plainly that there is nothing to claim.
- Saves the check as a draft and says so only when the system says it was applied.
- Ends on one fixed line: "No claim was sent to the supplier."

## What it does not do

- Send a claim. The purchasing system has an operation that sends one, and this agent is not given it.
- Decide whether goods delivered in error are kept, sent back or paid for.
- Give a reason for a difference, or blame a supplier, a carrier or a colleague.
- Approve or query an invoice. Invoice Matching sets an invoice against the order and the receipt. This agent starts from the delivery note.
- Guarantee the same wording on every run. The quantities and the amounts should be the same every time, and the tests check them. The claim is a draft.

## What you set up

- A model for the Reasoning tier.
- The company's purchasing system, connected as an imported API, with the six operations listed in [`agent.yaml`](agent.yaml) and no others. In particular, do not attach the operation that sends a claim.
- For the desk route, the accounts payable desk. It is planned and not yet written.

A company that receives delivery notes as scanned files can give the note to the agent as an uploaded file instead. That form is not written here.

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Control Room, Tools, import the purchasing system from its OpenAPI address. For the invented retailer, that is the document at `/purchasing/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give it an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the six operations named in [`agent.yaml`](agent.yaml). Attach nothing else.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because a check saves a draft.
8. To start it when a delivery note arrives, subscribe the platform to the retailer's `delivery-note` event. This form is not written yet.

## Test results

Not yet built on a platform. No test has been run.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24). The right answers are in the delivery notes section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- `DN-4100` (order `PO-450112`): agrees. No claim.
- `DN-4135` (order `PO-450158`): short delivery. The note says 500 kg and 300 kg were booked in: 200 kg at 24.50, 4,900.00 net. Invoice `INV-9034` bills the full 500 kg.
- `DN-4142` (order `PO-450161`): wrong item. 8,000 large boxes on the note, none booked in, and 8,000 small boxes that are not on the order: 4,400.00 net.
- `DN-4149` (order `PO-450164`): damaged. 800 kg of onions on the note, 680 kg booked in, 6 cases refused at the dock: 120 kg at 2.80, 336.00 net.
- Ask it to send a claim and take the amount off an invoice. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

A receiving or accounts lead sends every claim, and decides with the buyer named on the order whether a claim is made and what happens to goods that arrived in error.
