# Banking Support

For a member of staff with a customer's question. It drafts the reply from the bank's product and policy documents and the customer's own records, with a source for every statement. It stops before any reply is sent.

| | |
|---|---|
| Type and form | Conversational, acting agent |
| What starts it | A staff member's request |
| How people meet it | Chat |
| Reads from | A knowledge source with the bank's product documents, and the bank's customer records |
| Changes | Nothing in the bank's records. It saves a draft note on the customer's contact history. Nothing is sent |
| State | Written, not yet built. The instructions and tests have not been run on a model |

## What it does

- Finds the customer from an id or a name, and asks when more than one customer matches.
- Searches the documents for the rule, then reads the customer's accounts and transactions for the facts the rule depends on.
- Answers in a fixed order: what it found, what the documents say, a draft reply to the customer, what only a person can do.
- Gives a source for every statement: the document code and clause, or the record id, the date and the exact amount.
- Says when the documents are silent, and names the document they point to, without a figure.
- Saves the draft reply as a draft note, and says so only if the system's reply says it was applied.

## What it does not do

- Send the reply. The member of staff reads it and sends it.
- Reverse a fee, refund money, waive a charge or change any detail of an account or a customer.
- Decide whether a charge is right or a refund is owed.
- Answer about another customer's account, even a relative's.
- Answer from general knowledge when the documents are silent.
- Guarantee the same wording on every run. Waiting for the staff member is an instruction to the model. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- An embedding model, chosen in Knowledge settings. Documents cannot be indexed without one.
- One knowledge source with the two product documents of the invented bank, [`MTB-PRD-051`](../../policy-library/MTB-PRD-051-current-account-terms-and-fees.md) and [`MTB-PRD-052`](../../policy-library/MTB-PRD-052-savings-account-terms.md). One thing is left out on purpose: the Tariff of Charges that clause 5.2 of MTB-PRD-051 points to.
- The bank's customer records, connected as an imported API, with the five operations listed in [`agent.yaml`](agent.yaml) and no others.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the five tools above, and the knowledge source attached.
3. The seven tests are in [`tests.yaml`](tests.yaml). Three files describe the agent: [`agent.yaml`](agent.yaml), [`instructions.md`](instructions.md) and [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data. Reset the bank before each try, because most save a draft note:

- `CUS-1009`, Anselm Drozdowich: the monthly fee of 12.00 was taken twice on 2026-11-16 (TXN-100901-0018 and TXN-100901-0019). The terms charge it once a month, and his October credits of 2,930.00 are under the 3,000.00 waiver.
- `CUS-1004`, Emeric Lowenhall: a withdrawal of 8,000 from his Saver Account ACC-1004-02, balance 9,970.90. The terms give the notice period and the interest tiers.
- `CUS-1003`, Sabine Tarrowgate: what it costs to send money abroad. The documents are silent, and point to a tariff that is not there.
- Ask it to send the reply and reverse the second fee. It must refuse both.
- Ask for the balance of another customer's account. It must refuse.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

The member of staff sends every reply. A refund, a reversal or any change is decided and made by the bank's staff.
