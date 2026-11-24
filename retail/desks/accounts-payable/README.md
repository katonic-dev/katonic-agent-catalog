# Accounts payable desk

The settings folder that turns the Katonic case desk into a desk for a retailer's accounts payable team. Three kinds of case sit in one queue. A supplier invoice is matched to its purchase order and the goods received. A delivery note is set against what was booked in, and a claim is drafted. A supplier's message is answered from the purchasing records. Each kind goes to its own agent. A person decides.

Rowanmere Group (an invented company in the invented country Meridia), its suppliers, its buyers and every invoice, delivery note, payment and question are invented.

## The three kinds of case

| Kind | Agent | What the agent does | What a person decides |
|---|---|---|---|
| Invoice match | [Invoice Matching](../../agents/invoice-matching/README.md) | Compares the invoice with the order and the goods received, line by line, and gives each difference as an amount | Approve for payment, or send to the buyer |
| Delivery discrepancy | [Delivery Discrepancy](../../agents/delivery-discrepancy/README.md) | Sets the delivery note against what was booked in, names each difference and its amount, and drafts the claim | Send the claim to the supplier, or close with no claim |
| Supplier question | [Supplier Query](../../agents/supplier-query/README.md) | Says what the records hold for each thing the supplier asks, and drafts the reply | Send the reply to the supplier, pass to a colleague, or ask the agent again |

The desk sends the agent one message: the drafting instruction for the kind, then the case with its records. The agent works from that message. It reads nothing from the purchasing system and saves nothing.

**The desk records the decision and does nothing else.** It pays nothing, sends nothing to a supplier or a buyer, and calls no operation of the purchasing system. "Send the claim" records that a named person decided the claim goes out, and the claim as it read at that moment. The person sends it.

## What the person sees

- **A queue of cases**, each with its kind and one fact: the invoice total, the day of delivery, or the supplier's subject.
- **The records beside the draft.** What the purchasing system holds is on one side. The agent's draft is on the other.
- **One row for each line** of the invoice or the delivery note, or for each thing the supplier asks, with the two records compared, a mark and the difference.
- **The claim or the reply on a card of its own**, under the rows. "Edit the text" changes its wording before the decision, and the edit is kept as a new version.
- **The agent's proposal**, one line, and the button it points to.
- **The register** afterwards: who decided what, when, on which version, and with which agent.

### The marks

| Mark | Kind | Meaning |
|---|---|---|
| In agreement | Invoice, delivery | The item, the unit price and the quantity are the same in the records compared |
| Price differs | Invoice | The unit price on the invoice is not the unit price on the order |
| Quantity differs | Invoice | The invoice bills more than was ordered |
| Not received | Invoice | The invoice bills more than has been booked in so far |
| Not on the order | Invoice, delivery | An invoice line, or something on the receipt, that is on no line of the order |
| Short delivery | Delivery | Less was booked in than the delivery note says |
| Wrong item | Delivery | The item on the note was not booked in, and another item came in its place |
| Damaged | Delivery | Goods were refused at the dock as damaged, as written on the note |
| In the records | Supplier question | The records hold the fact, and the reply states it as the records give it |
| Not in the records | Supplier question | The purchasing system does not hold it. A person answers |
| Not checked | All | The record needed was not with the case |

The agent's Summary carries no count of marks. The desk counts them from the table.

## The decisions

| Decision | Kind | What it records |
|---|---|---|
| Approve for payment | Invoice match | The approval, in the person's name. One click when every line agrees. Needs a reason when a line does not agree |
| Send to the buyer | Invoice match | What the buyer named on the order should settle |
| Send the claim to the supplier | Delivery discrepancy | That the claim goes out, who sends it, and the claim as it reads |
| Close with no claim | Delivery discrepancy | Why no claim goes to the supplier. This is also how a drafted claim is dropped |
| Send the reply to the supplier | Supplier question | That the reply goes out, who sends it, and the reply as it reads |
| Pass to a colleague | Supplier question | Who the message goes to and why, when the records do not answer it |
| Ask the agent again | All | A note that the agent sees. The agent drafts again |

A case offers only the decisions of its kind, and the desk refuses any other. The person who entered a case cannot decide it. A query to the supplier about an invoice is not a decision on this desk: the buyer raises it.

## The sixteen demo cases

| Case | Kind | What the agent should find |
|---|---|---|
| INV-88214, USD 13,409.00 | Invoice match | Agrees. Ready for approval |
| INV-3391, USD 19,147.50 | Invoice match | Agrees. Ready for approval |
| INV-77102, USD 31,740.00 | Invoice match | Price differs: 46.00 a bag invoiced, 44.50 ordered. USD 900.00 net. To the buyer |
| INV-5120, USD 8,602.00 | Invoice match | Quantity differs: 800 kg invoiced, 720 kg ordered and received. USD 496.00 net. To the buyer |
| INV-6417, USD 7,452.00 | Invoice match | A delivery charge of USD 180.00 that is not on the order. To the buyer |
| INV-9034, USD 14,087.50 | Invoice match | Not received: 500 kg invoiced, 300 kg received so far. USD 4,900.00 net. To the buyer |
| DN-4135 | Delivery discrepancy | Short delivery: 500 kg on the note, 300 kg booked in. Claim USD 4,900.00 net |
| DN-4142 | Delivery discrepancy | Wrong item: 8,000 large boxes on the note, 8,000 small boxes booked in. Claim USD 4,400.00 net |
| DN-4149 | Delivery discrepancy | Damaged: 120 kg of onions refused at the dock. Claim USD 336.00 net |
| DN-4100 | Delivery discrepancy | Agrees. No claim |
| SQ-2611-01 | Supplier question | INV-76410 was paid in full on 2026-11-10 |
| SQ-2611-02 | Supplier question | INV-87655 is scheduled for payment on 2026-11-30 |
| SQ-2611-03 | Supplier question | INV-5066 was short-paid by USD 356.50, a deduction under debit note DBN-0412 |
| SQ-2611-04 | Supplier question | A delivery slot. The records do not answer it. To a colleague |
| SQ-2611-05 | Supplier question | INV-77102 is received and not approved, due on 2027-01-01 |
| SQ-2611-06 | Supplier question | 300 kg was booked in on PO-450158. The delivery note says 500 kg |

These are the records the invented retailer holds when its date is 24 November 2026. [Its scenario list](../../../demo-retailer/SCENARIOS.md) gives the right answer for each.

## Where the cases come from

`cases.json` is not typed by hand. [`make_cases.py`](make_cases.py) builds it from the seed of the invented retailer in [`demo-retailer/`](../../../demo-retailer/README.md). Each case carries the records its agent needs: the invoice with its order and receipt, the delivery note with its order, its receipt and any invoice for the order, or the supplier's message with the payments, invoices, orders and notes it names. For a supplier's message the records are found by the numbers the supplier wrote, for that supplier only. It starts no server.

```bash
python make_cases.py           # writes cases.json
python make_cases.py --check   # says whether cases.json is what the script would write
```

Run it with the Python of the retailer's own environment. A test of the retailer, `demo-retailer/tests/test_accounts_payable_desk_cases.py`, fails when `cases.json` differs from what the script would write, or when a case differs from what the service returns for that record.

## Which engine it needs

The settings-driven case desk engine, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk), at a version that takes a settings folder kept outside its own repository and reads the `routing` setting with a list of decisions and its own wording for each kind, `draft.sections` for the claim and the reply, `draft.markIcons`, `draft.summaryAboveRows`, `case.foldOnPhone`, `intake.fields[].options` and `intake.fields[].shownAs`. That version is in `main` of the engine since 24 November 2026.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm install
DESK_CONFIG=../katonic-agent-catalog/retail/desks/accounts-payable/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
INVOICE_MATCHING_AGENT_ID=<id of Invoice Matching> \
DELIVERY_DISCREPANCY_AGENT_ID=<id of Delivery Discrepancy> \
SUPPLIER_QUERY_AGENT_ID=<id of Supplier Query> \
KATONIC_AGENT_ID=<any one of the three, for a case of an unknown kind> \
LOCAL_USER=ysolde.marrington@rowanmere.invalid \
LOCAL_USER_NAME="Ysolde Marrington" \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json` |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `INVOICE_MATCHING_AGENT_ID` | The agent for cases of the kind Invoice match. If it is empty, drafting such a case fails and says which setting to fill |
| `DELIVERY_DISCREPANCY_AGENT_ID` | The same, for Delivery discrepancy |
| `SUPPLIER_QUERY_AGENT_ID` | The same, for Supplier question |
| `KATONIC_AGENT_ID` | The agent for a case whose kind is none of the three. The desk asks it only to say that the kind is not recognised, and such a case offers only "Ask the agent again" |
| `LOCAL_USER`, `LOCAL_USER_NAME` | The person the desk records when no sign-in stands in front of it. The demo user is an invented accounts payable lead |
| `SEED_DEMO` | `true` loads the sixteen demo cases on the first start. Open one and press "Ask the agent to draft" |
| `DESK_LIBRARY_DIR` | Not used. This desk has no library: each case carries its records |

The kind of a case is the value of its "Kind of work" field, matched without regard to case.

Build the three agents from their folders. Each agent's own instructions tell it to read the purchasing system and to save a draft there. The desk asks for another shape, so each agent needs one more section before the desk is pointed at it: [`agent-desk-sections.md`](agent-desk-sections.md) holds the three. The section and the drafting instruction for the kind in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine comes with a stand-in platform, `demo/fake-platform.js`, that plays the agents with canned text. Start it with the same `DESK_CONFIG` and point the desk's `KATONIC_BASE_URL` at it, with any value for the key and for each of the four agent ids. It answers from [`demo-replies.json`](demo-replies.json): one reply for each of the sixteen demo cases, following the right answers above. Every stand-in reply says on its first line that it is canned text. A case you enter by hand gets one row saying the stand-in read none of the records.

The stand-in shows how the desk works. It does not test the agents.

## How it was tested

On 24 November 2026 the desk was run against the stand-in through twenty-three scenarios in a headless browser. All twenty-three pass.

- The queue shows the sixteen cases, each with its kind.
- The results and amounts in `cases.json` were worked out again from the text of each case, by the match rules: they are the ones the retailer's scenario list gives.
- Each kind's draft comes from the agent its setting names, with its own instruction. Every message to an agent is under 6,000 characters.
- The rows, marks, amounts, claims, replies and proposals shown for all sixteen cases match the scenario list, and the agent's proposal sits on the right button.
- Every decision: approve for payment with one click, approve with a reason while a line differs, send to the buyer, send a claim as drafted and after editing its wording, close with no claim, send a reply, pass to a colleague, and ask the agent again.
- A decision of another kind is refused. A kind whose agent setting is empty says which setting to fill. A kind the desk does not know offers only asking again.
- The register and its export, a question to the agent, the form for a new case, search by kind, by supplier and by number, the filters, and a reload.
- Four eyes: the person who entered a case cannot decide it, on the page or by calling the desk directly, for each of the three kinds. A second accounts payable lead can.
- At phone width no screen scrolls sideways.

It was reviewed for visual design at desktop and phone width, in light and dark, and the settings and the cases script were changed after the first round. The retailer's test that keeps `cases.json` equal to the service passes.

Not yet done: a run against the three real agents on a platform, the desk section added to the three agent folders, the platform's sign-in in front of the desk, and the desk deployed as an app. The queue has no filter by kind: a search for the kind's name lists its cases.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the `routing` setting with the three drafting instructions |
| `cases.json` | The sixteen demo cases, written by `make_cases.py` |
| `make_cases.py` | Builds `cases.json` from the invented retailer's records |
| `demo-replies.json` | The canned replies for the stand-in platform |
| `agent-desk-sections.md` | The section each of the three agents needs before the desk is pointed at it |
