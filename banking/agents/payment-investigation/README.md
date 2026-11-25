# Payment Investigation

Traces a payment's status, lines up the messages exchanged about it, and drafts the reply to the customer or the other bank. It stops before any recall, amendment or return.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A query on a payment. The bank's payments system can announce one through its event for new payment investigations |
| How people meet it | An application: the Payments desk |
| Reads from | The bank's payments system: the investigation with the bank rules it lists, the payment with its timeline and messages, and earlier payments to the same beneficiary |
| Changes | Saves a draft reply with the findings it rests on. The draft sends nothing and changes no status |
| State | Built on a development cluster on 25 November 2026. All seven tests pass five runs in a row. Not on the Catalog shelf |

## What it does

- Reads the investigation, the payment it concerns with its status timeline, and every message exchanged about it.
- Lines up the messages in date order, each with its id, its type, its direction and what its key fields say.
- Sets the amount instructed against the amount settled and the amount credited, and says the difference as a number.
- Reads the bank rules that the investigation lists (their ids, their text and the note that says why they apply), and says what they require. When it lists none, no rule applies and the table says No rule needed.
- Where the claim turns on earlier payments to the same beneficiary, finds them by the beneficiary's name or account.
- Writes one row for each finding: the evidence ids, what the records show, the rule, and a mark: confirmed, to correct, missing or unclear.
- Drafts the reply to the customer or the other bank as a message under its own heading, "Draft reply. Not sent.": a greeting, short paragraphs, a sign-off. It uses only what the findings support and names a rule in words. The desk shows it as a card the operator can edit.
- Saves the reply as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: approve the reply to the customer, approve the reply to the other bank, or refer the case to a person.

## What it does not do

- Recall a payment, amend one or return one, or ask another bank to. A person does that.
- Send the reply. The payments operator approves it and a person sends it.
- Claim a charge back from another bank. It says what the bank's rule says the bank does.
- Fill a gap. Where the records do not settle a point, it says so and refers the case to a person.
- Guarantee the same marks on every run. The proposal is a draft for the payments operator. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's payments system, connected as an imported API, with the five operations listed in [`agent.yaml`](agent.yaml) and no others.
- The [Payments desk](../../desks/payments/README.md), which sends the case, if you want to meet the agent through a screen. It needs the case desk engine that reads the `routing` setting. The agent also answers in a chat.
- An API key with the Chat scope for the desk, and the published agent's id.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the five tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft proposal. For the payments operator. Not issued.", a seven-column table (the fifth column is called Rule), the reply under the heading "Draft reply. Not sent.", and a last line that starts "Proposal:". The summary holds no count of marks and is not in the first person. Change the instructions and the desk's `routing` setting for "Investigation" together.
4. The seven tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data, started with `BANK_TODAY=2026-11-24` so that the dates agree with the desk's demo cases:

- `INV-5001`: a payment of USD 1,850.00 that the beneficiary says never arrived. It was credited on 21 Nov 2026, after a hold at the correspondent bank until its next processing day, 3 days after sending. The status report says ACSC. The system lists no bank rule, so none applies. The reply tells the customer it arrived, with the date.
- `INV-5002`: a payment of USD 25,000.00 that arrived short. An intermediary bank deducted USD 37.50, so 24,962.50 arrived. The charges were OUR, so the deduction is wrong under MTB-PAY-RULE-105, the one rule the system lists. The reply says the bank will claim it back.
- `INV-5003`: a payment of USD 3,200.00 that came back. The beneficiary account is closed (reason AC04). The money was credited back to ACC-1006-01. A new payment needs corrected details (MTB-PAY-RULE-106, the one rule the system lists).

Everyone and everything in the invented bank is invented.

## Where it stops for a person

The payments operator reads the proposal and approves the reply, asks for more, or refers the case. Nothing is sent by the agent. Any recall, amendment, return or claim on an intermediary bank is done by a person.
