# Complaint Handling

Classifies a customer's complaint, gathers the customer's history and the records it points at, and drafts the response and the entry for the complaints log, with the dates the bank's procedure sets.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A complaint arriving at the bank. The bank's complaints system can announce one through its event for new complaints |
| How people meet it | An application: the Complaints desk |
| Reads from | The bank's complaints system: the complaint, its linked records, the customer's earlier complaints and the complaints procedure. The bank's customer records: the customer |
| Changes | Saves a draft classification and a draft response. The drafts send nothing and move no money |
| State | Written, not yet built. The instructions and tests have not been run on a model |

## What it does

- Reads the complaint with the customer's own words, the dates the procedure sets, the linked records (accounts, transactions, cards, payments, investigations, loans and loan applications) and the customer's earlier complaints.
- Classifies it by the procedure's categories, with a severity and a priority.
- Checks each fact the customer states against the linked records, and marks it supports the complaint, does not support it, procedure point or needs a person, with the record id or the procedure clause.
- Works out the acknowledgement date, whether it was on time or late or never sent, the final response date and the working days left.
- Flags a customer who may be vulnerable, with the reason from the customer's own words. It does not diagnose.
- Drafts the response to the customer in the order the procedure sets, with the right to escalate written in full, and the log entry.
- Saves the classification and the response as drafts, and says so only if the system's reply says they were applied.
- Writes every date as 18 Nov 2026, in plain statements, with no count of marks in the Summary, and a placeholder where the name and direct line of the person who answers go.
- Ends with one proposal line. Its first sentence gives the outcome, any redress and any priority handling or urgency.

## What it does not do

- Send a response, credit redress, replace or unblock a card, or change any record. The complaints officer approves and sends the response, and any redress is credited when the officer sends it.
- Offer redress the procedure does not allow, or offer it to end a complaint.
- Promise a result that a person decides, such as the review of a credit decision.
- State a cause that the records do not give, or invent the name and direct line of the person who answers further questions.
- Guarantee the same marks on every run. The review and the response are drafts for the officer. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's complaints system and customer records, connected as imported APIs, with the five operations listed in [`agent.yaml`](agent.yaml) and no others.
- The [Complaints desk](../../desks/complaints/README.md), which sends the case, if you want to meet the agent through a screen. It needs the case desk engine. The agent also answers in a chat.
- An API key with the Chat scope for the desk, and the published agent's id.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the five tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft review. For the complaints officer. Not issued.", a seven-column table, the draft response, the log entry, and a last line that starts "Proposal:". Change the instructions and the desk's `draft.instruction` setting together.
4. The eight tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data:

- `CMP-1001`: Anselm Drozdowich (CUS-1009). The monthly account fee of USD 12.00 was taken twice on ACC-1009-01. Fees and charges, severity low, upheld. Refund one fee, USD 12.00, and apologise. An earlier complaint, CMP-0901, was not upheld and is a different matter.
- `CMP-1002`: Rosalind Heathcote-Brae (CUS-1014). Payment PAY-6001 arrived late. Payments, not upheld, no bank error. Explain with the dates in the timeline of the payment, which was credited 3 days after it was sent, with status ACSC in its status report. The investigation INV-5001 is open. No redress.
- `CMP-1003`: Isolde Pennywhistle (CUS-1016). Loan LAP-8010 was declined. Lending decision, not upheld, not a service failure: debt to income is 0.48 against the 0.40 limit of MTB-POL-030. Explain the reason and how to ask for a review. Promise nothing.
- `CMP-1004`: Ilvane Marrowick (CUS-1001). Her husband died 18 days ago and her card CRD-2004 was blocked by the deceased accounts process. Possibly vulnerable, a recent bereavement. Priority, one named person, a kind plain letter. Upheld: the card is her own and the process is for the cards of the person who died. The card is to be replaced, by a person, with an apology.
- `CMP-1005`: Sabine Tarrowgate (CUS-1003). Received 13 working days ago and never acknowledged. Admit the acknowledgement is 11 working days late and apologise. The final response is due in 2 working days, so it is urgent. The customer says she has held her account for more than ten years. The customer record does not show that.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

The complaints officer approves every response and sends it. A card replacement or a refund is made by a person. A possibly vulnerable customer is handled by one named person.
