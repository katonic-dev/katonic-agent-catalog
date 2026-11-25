# Loan Document Verification

Compares the signed contract and the security documents of an approved loan with the terms the credit committee approved, and marks every difference.

| | |
|---|---|
| Type and form | Workflow, API agent |
| What starts it | A call from the Lending desk or from the bank's lending system, naming an approved loan |
| How people meet it | An application: the Lending desk |
| Reads from | The bank's lending system: the approved terms and the loan's documents |
| Changes | Saves a draft list of differences. The draft changes no loan |
| State | Built on a development cluster on 25 November 2026. All six tests pass five runs in a row. Not on the Catalog shelf |

## What it does

- Reads the approved terms and every document of the loan: the facility agreement, the schedules and the resolutions.
- Writes one row for each approved term, in the order of the approved terms: in order, differs, or missing.
- Gives both values on every row, the approved value and the contract's value, with the document id and the clause number.
- Reads the security documents against the security term and the contract's security clause.
- Gives a term in the contract that the approved terms do not mention its own row, marked as differing.
- Saves the differences as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: send the differences to a banker, naming each term and its clause.

## What it does not do

- Approve a loan, confirm that the contract is in order for release, or release funds. A banker decides.
- Say which side is right, the approval or the contract, or suggest a change to either.
- Read a signature or judge whether a document is genuine.
- Write to the borrower.
- Guarantee the same marks on every run. The list is a draft for the banker. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's lending system, connected as an imported API, with the four operations listed in [`agent.yaml`](agent.yaml) and no others.
- The [Lending desk](../../desks/lending/README.md), which sends the case, if you want to meet the agent through a screen. It needs the case desk engine that reads the `routing` setting. The agent also answers in a chat.
- An API key with the Chat scope for the desk, and the published agent's id.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the four tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft review. For the lending officer. Not issued.", a seven-column table, and a last line that starts "Proposal:". Change the instructions and the desk's `routing` setting for "Document check" together.
4. The six tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data:

- `LN-9001`: an approved term loan of USD 250,000 to Lanternfish Logistics Ltd whose signed contract differs from the approved terms in exactly three places. The rate margin is 3.25 percent approved and 3.75 percent in the contract (clause 3). The debt service cover covenant is 1.30 approved and 1.50 in the contract (clause 6a). The security is a first-ranking charge over the five delivery vehicles listed in Schedule A approved, and a general charge over all present and future assets in the contract (clause 7). Everything else agrees: the amount, the term, the repayment, the fees, the debt to equity covenant and the law.
- `LN-9002`: a loan the customer records hold but the lending system has no approved terms for. The agent must say so and compare nothing.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

A banker receives every difference and decides what to do about it. The agent confirms nothing as in order for release.
