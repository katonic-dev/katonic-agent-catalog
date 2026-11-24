# Loan Application Intake

Checks a loan application pack against the documents the bank's lending policy requires for the product, extracts the figures, and lists what is missing and what differs.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A loan application arriving at the bank. The bank's lending system can announce one through its event for new loan applications |
| How people meet it | An application: the Lending desk |
| Reads from | The bank's lending system: the application, its documents and the lending policy |
| Changes | Saves a draft list of missing items and figures. The draft sends nothing and changes no status |
| State | Written, not yet built. The instructions and tests have not been run on a model |

## What it does

- Reads the application, its checklist of required documents, its documents and the lending policy for the product.
- Writes one row for each required document, in the policy's order: in order, missing, or differs.
- Extracts the figures from the form and from the documents, each with the document id and the line it came from.
- Compares each form figure with the documents. Where they differ it shows both values and both sources, and chooses neither.
- Works out an average or a sum where a document gives only the lines, for example average monthly credits from six months of bank statements, and shows the working. A figure it worked out is in order when it is less than 1 percent away from the form figure, and the gap is in the note. Change the 1 percent in the instructions to your bank's own rule.
- Compares the documents with each other where two give the same figure, for example net pay on the payslips against the salary credits on the bank statements.
- Saves the list of missing documents and the figures as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: send the pack to the loan officer, or send the list with what to ask the applicant for.

## What it does not do

- Approve or decline an application, or say one is likely to be approved or declined. The loan officer decides.
- Price a loan or comment on the applicant's creditworthiness.
- Write to the applicant. It proposes what to ask for.
- Fill a gap, estimate a missing figure or choose between two figures that differ.
- Guarantee the same marks on every run. The list is a draft for the loan officer. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's lending system, connected as an imported API, with the five operations listed in [`agent.yaml`](agent.yaml) and no others.
- The [Lending desk](../../desks/lending/README.md), which sends the case, if you want to meet the agent through a screen. It needs the case desk engine that reads the `routing` setting. The agent also answers in a chat.
- An API key with the Chat scope for the desk, and the published agent's id.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the five tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft review. For the lending officer. Not issued.", a seven-column table, and a last line that starts "Proposal:". Change the instructions and the desk's `routing` setting for "Application intake" together.
4. The six tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data:

- `LAP-8001`: a salaried personal loan with a complete pack. All four required documents are on file. Income agrees across the form, the payslips and the statements.
- `LAP-8002`: a small business loan with two documents missing, the latest tax return and the declaration of ultimate owners, and turnover that differs: average monthly turnover is 62,000 on the form and 51,400 in the bank statements, and annual turnover is 744,000 on the form against revenue of 612,000 in the financial statements.
- `LAP-8003`: a small business loan with a complete pack, including three years of financial statements. Average monthly turnover is 136,667 on the form and 136,566.67 worked out from the bank statements, less than 1 percent apart, so it is in order with both values shown.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

The loan officer reads the list and decides what to ask the applicant for, and whether a figure that differs matters. Nothing is sent to the applicant by the agent.
