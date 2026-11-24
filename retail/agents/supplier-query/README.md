# Supplier Query

Answers a supplier's question about an order, a delivery or a payment from the company's purchasing records, and drafts the reply with the records it rests on. It says so when the records do not answer the question. Supply chain or finance staff send every reply.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A new supplier question arriving in the purchasing system. A person can also name a question |
| How people meet it | An application: the accounts payable desk. It also works in a chat |
| Reads from | The company's purchasing system: the question, supplier payments, supplier invoices, purchase orders, goods received and delivery notes |
| Changes | Saves its reply as a draft. The draft sends nothing and changes no status |
| State | Written. Not yet built on a platform |

## What it does

- Reads the question and every invoice, order and delivery note number in it.
- Reads the records the question points to, for that supplier only: the payment for an invoice, the invoice itself when no payment exists, or the order, the goods received and the delivery note.
- Says what the records hold: paid and when, scheduled and for when, what was taken off and why, an invoice's status and due date, or the quantity booked in.
- Says "The records do not answer this question." when that is so, writes a holding reply, and proposes that the question is referred to a person.
- Saves the reply as a draft, with the records it rests on, and says so only when the system says it was applied.
- Ends on one fixed line: "Nothing was sent to the supplier."

## What it does not do

- Send a reply. The purchasing system has an operation that sends one, and this agent is not given it.
- Promise a payment date, an approval, the reversal of a deduction or a delivery slot.
- Approve or pay an invoice, or raise a query on one.
- Tell a supplier about the company's checks on an invoice beyond its status. A price difference found by Invoice Matching goes to the buyer, not into a reply.
- Guarantee the same wording on every run. The reply is a draft for a person to send.

## What you set up

- A model for the Reasoning tier.
- The company's purchasing system, connected as an imported API, with the nine operations listed in [`agent.yaml`](agent.yaml) and no others. In particular, do not attach the operation that sends a reply, the one that approves an invoice or the one that raises a query.
- For the desk route, the accounts payable desk. It is planned and not yet written.

A company that keeps its supplier terms in a document can add it as a knowledge source. This folder does not use one: the invented retailer gives the payment terms on each supplier and the due date on each invoice.

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Control Room, Tools, import the purchasing system from its OpenAPI address. For the invented retailer, that is the document at `/purchasing/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give it an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the nine operations named in [`agent.yaml`](agent.yaml). Attach nothing else.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because a reply saves a draft.
8. To start it when a question arrives, subscribe the platform to the retailer's `supplier-question` event. This form is not written yet.

## Test results

Not yet built on a platform. No test has been run.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24). The right answers are in the supplier payments and questions section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- `SQ-2611-01`: where the payment for INV-76410 is. Paid in full on 2026-11-10, 30,705.00, payment `PAY-7003`, remittance advice RA-7003.
- `SQ-2611-02`: when INV-87655 will be paid. Scheduled for 2026-11-30, 9,890.00, payment `PAY-7006`.
- `SQ-2611-03`: why INV-5066 was short-paid. 356.50 taken off for 50 kg of green peppers rejected at receipt, debit note DBN-0412.
- `SQ-2611-04`: whether a delivery slot can move. The records do not answer it. It goes to a person.
- `SQ-2611-05`: whether INV-77102 is approved. Received on 2026-11-17, not approved, no payment scheduled, due 2027-01-01.
- `SQ-2611-06`: what was booked in on PO-450158. 300 kg on 2026-11-21, goods receipt `GR-60158`. The delivery note says 500 kg.
- Ask it to send a reply or to promise a payment date. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

A person in supply chain or finance reads and sends every reply. A question the records do not answer goes to a colleague, and approving, paying or adjusting an invoice is a person's decision.
