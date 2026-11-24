# Invoice Matching

Matches a supplier invoice to its purchase order and to the goods received against it, line by line, and lists what does not agree, with each difference as an amount net of tax. A person in accounts payable decides.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A new supplier invoice arriving in the purchasing system. A person can also name an invoice |
| How people meet it | An application: the accounts payable desk. It also works in a chat |
| Reads from | The company's purchasing system: supplier invoices, purchase orders, goods received |
| Changes | Saves its match as a draft. The draft changes no status |
| State | Written. Not yet built on a platform |

## What it does

- Reads the invoice, finds the purchase order number printed on it, and reads that order with its lines, the buyer's name and the goods received against it.
- Compares line by line: item, unit price, quantity ordered, quantity received so far, quantity invoiced.
- Gives each invoice one result: agrees, price differs, quantity differs, not on the order, not received, several differences, or no purchase order found.
- Gives each difference as an amount net of tax: the price gap times the quantity invoiced, the extra quantity times the order price, or the net of a line that is not on the order.
- Applies no tolerance. A person decides whether a small difference is accepted.
- Says that an invoice that agrees is ready for the approver, and that one that differs goes to the buyer named on the order.
- Saves the match as a draft and says so only when the system says it was applied.
- Ends on one fixed line: "Nothing was approved and no query was sent to the supplier."

## What it does not do

- Approve an invoice, reject it or pay it. The purchasing system has operations for approving and for raising a query, and this agent is not given them.
- Contact a supplier or resolve a mismatch.
- Invent an order, a line or an amount.
- Guarantee the same wording on every run. The match is a draft for accounts payable. Run the tests on your own model before you rely on them.

## What you set up

- A model for the Reasoning tier.
- The company's purchasing system, connected as an imported API, with the five operations listed in [`agent.yaml`](agent.yaml) and no others. In particular, do not attach the operation that approves an invoice or the one that raises a query.
- For the desk route, the accounts payable desk. It is planned and not yet written.

## Two forms

- **As a chat agent,** from [`instructions.md`](instructions.md). This is the form the tests in [`tests.yaml`](tests.yaml) are written for.
- **As four steps,** in [`workflow.yaml`](workflow.yaml): read the invoice, compare it with the purchase order and the goods received, write the result for accounts payable, and a person approves. An earlier version of this form was run with the order register pasted into the second step. It has not been run in the form written here, which reads the order and the receipts through the purchasing system. Its paths and its trigger are marked in the file as provisional.

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Control Room, Tools, import the purchasing system from its OpenAPI address. For the invented retailer, that is the document at `/purchasing/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give it an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the five operations named in [`agent.yaml`](agent.yaml). Attach nothing else.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run test 1 with "Test the prompt without tools" ticked. Run the others with the tools attached. Reset the retailer before each run, because each one saves a draft.
8. To build the four-step form instead, create a workflow in Studio and follow [`workflow.yaml`](workflow.yaml), matching its paths to the purchasing system's OpenAPI document.

## Test results

Not yet built on a platform. No test has been run.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24). Reset the retailer before each try, because each one saves a draft:

- `INV-88214` (Ilvane Valley Dairy Ltd, order `PO-450112`): agrees. Net 11,660.00, tax 1,749.00, total 13,409.00.
- `INV-3391` (Marlow Reach Packaging Ltd, order `PO-450127`): agrees. Net 16,650.00, tax 2,497.50, total 19,147.50.
- `INV-77102` (Tallowby Flour Mills Ltd, order `PO-450131`): price differs. Invoiced at 46.00 against 44.50 on 600 bags, so 900.00 net. Total invoiced 31,740.00.
- `INV-5120` (Orchard Gate Fresh Produce Ltd, order `PO-450140`): quantity differs. 800 kg of peppers invoiced, 720 ordered and received, so 80 kg at 6.20, 496.00 net. Total invoiced 8,602.00.
- `INV-6417` (Marlow Reach Packaging Ltd, order `PO-450152`): a delivery charge of 180.00 that is not on the order.
- `INV-9034` (Ilvane Valley Dairy Ltd, order `PO-450158`): 500 invoiced, 300 received so far. The amount is worked out in [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md).
- Ask it to approve `INV-88214` and write to a supplier. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

A person in accounts payable approves every invoice for payment. A difference goes to the buyer named on the purchase order, and a person decides whether a supplier is queried.
