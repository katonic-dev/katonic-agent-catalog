# Product Recall Preparation

For a recalled batch, lists the stores and online orders that received it and drafts the store instruction and the customer notice, in three stages. The Head of Quality approves every instruction and notice before it goes out.

| | |
|---|---|
| Type and form | Multi-agent, pipeline |
| What starts it | A batch being recalled in the stock system. A person can also name a batch |
| How people meet it | An application: the recall desk. It also works in a chat |
| Reads from | The company's stock system: the batch, where it went, the supplier's recall and the recall procedure. The orders system: each order on the list. The stores system: each store on the list |
| Changes | Saves a recall pack as a draft. The draft sends nothing |
| State | Written. Not yet built on a platform |

## What it does

- Stage one: reads the batch record and lists every store and every online order it names, with units. The batch record is the only list.
- Reads each order for the customer and the status, and each store for its name, town and area manager.
- Stage two: drafts the store instruction to the recall procedure: the product, the batch number, the best-before date, off sale at once, hold apart, count and report, refunds without a receipt.
- Stage three: drafts the customer notice to the recall procedure: the product, the batch number, the best-before date, the supplier's own words, do not use it, a full refund without a receipt.
- Says so when a batch is not recalled, and prepares nothing for it.
- Saves the pack as a draft and says so only when the system says it was applied.
- Ends on one fixed line: "Nothing was sent to any store or customer. The Head of Quality approves every instruction and notice."

## What it does not do

- Issue a notice, or send anything to a store or a customer.
- Add an order because it holds the same product. An order that is not on the batch record came from another batch.
- Say what caused the fault, say that anyone was or was not harmed, or give medical advice.
- Soften or sharpen the supplier's words. It gives them as the supplier wrote them.

## What you set up

- A model for the Reasoning tier.
- The company's stock system, connected as an imported API, with the 3 operations listed for it in [`agent.yaml`](agent.yaml).
- The company's orders system, connected as an imported API, with the 1 operation listed for it in [`agent.yaml`](agent.yaml).
- The company's stores system, connected as an imported API, with the 1 operation listed for it in [`agent.yaml`](agent.yaml).
- For the desk route, the recall desk. It is planned and not yet written.

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Control Room, Tools, import the stock system and the orders system and the stores system from their OpenAPI addresses, one system at a time. For the invented retailer, those are the documents at `/stock/openapi.json` and `/orders/openapi.json` and `/stores/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give each an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the 5 operations named in [`agent.yaml`](agent.yaml). Attach nothing else: the operation that changes a record (`issue_recall_notice`) stays out of this agent on purpose.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because a run saves a draft.
8. To start it when a batch is recalled, add a webhook trigger on the retailer's `recalled-batch` event. This form is not written yet.

## Test results

Not yet built on a platform. No test has been run.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24, period 2026-10). The right answers are in the recalled batch section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- Batch `BT-44031` of pasta sauce: four stores (`S-101` 240 units, `S-104` 180, `S-105` 60, `S-107` 200) and seven orders for five customers.
- Ask whether order `RM-58188` is affected. It holds a grocery box and is not on the batch record: no.
- Ask about stores `S-102` and `S-106`. They received `BT-44032`, a later batch that is not recalled.
- Ask for a pack for `BT-44032`. It is not recalled, so there is nothing to prepare.
- Ask it to send the notice to the customers. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

The Head of Quality approves every store instruction and every customer notice before it goes out, and issues them.
