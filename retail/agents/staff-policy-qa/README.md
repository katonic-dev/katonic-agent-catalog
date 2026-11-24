# Staff Policy Q&A

Answers a colleague's question about workplace policy from the company's Staff Handbook, and cites the clause for each rule.

| | |
|---|---|
| Type and form | Conversational, answering agent |
| What starts it | A colleague's question |
| How people meet it | Chat |
| Reads from | A knowledge source that holds the Staff Handbook |
| Changes | Nothing. It has no tool that acts |
| State | Tested as a draft on a development cluster. Seven of eight tests pass three runs in a row. Not published |

## What it does

- Answers a question about leave, sickness, hours and shift swaps, expenses, uniform, training or raising a concern from the handbook, with the section and clause on each rule.
- Ends every answer with a line that starts "Source:" and names the document, its version and the clause.
- Says so plainly when the handbook is silent, when it covers only part of the question, and when a clause points to something the handbook does not hold, such as the speak-up line number.
- Leaves an exception, and anything about one person's pay, contract, visa status or leaving payments, to the People team.

## What it does not do

- Take any action. It does not book leave, approve a swap or an expense, or change a record.
- Guarantee the referral. Leaving decisions to the People team is an instruction to the model, not a control. Run the last two tests on your own model before you publish.
- Read personnel records, rosters or payslips. Attach the handbook only.
- Say what the law requires. It reports what the handbook says.
- Answer from general knowledge when the handbook is silent.

## What you set up

- A model for the Reasoning tier. The rules for the state with nothing connected have to hold against a question the model could answer from memory.
- An embedding model, chosen in Knowledge settings. Documents cannot be indexed without one.
- One knowledge source that holds the handbook: [`../../policy-library/staff-handbook.md`](../../policy-library/staff-handbook.md) for the invented company, or your own.

## Build it

Built this way as a draft on a development cluster on 24 November 2026. It was not published there.

1. In Katonic Studio, create a new agent of the kind that answers from your documents.
2. In Identity, give it a name and a description, and choose the owner team.
3. In Behavior, write the instructions yourself and paste [`instructions.md`](instructions.md) word for word.
4. Set the model tier to Reasoning.
5. Attach no tools.
6. In Knowledge, attach the source that holds the handbook.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). For the two tests with nothing connected, detach the source and tick "Test the prompt without tools".

## Test results

Run on a development cluster on 24 November 2026, three runs of each test.

- Seven of the eight tests pass three runs in a row.
- On the eighth, a question about one person's pay, every run sent the person to the People team and gave no figure. Half the runs still tripped a check phrase.
- The agent was tested as a draft and is not published.

A test counts as passed here only after five runs in a row. That has not been done yet.

## Try it

The handbook of the invented company is in [`../../policy-library/`](../../policy-library/README.md). Ask:

- How many days of annual leave in the third year? The answer is 21 working days, HR-01 clause 1.1.
- Who approves leave in the two busiest trading weeks? The area manager, HR-01 clause 1.4.
- What is the speak-up line number? The handbook does not publish it (HR-07 clause 7.2).
- Approve my shift swap. It must refuse and say the shift manager approves (HR-03 clause 3.2).

Everyone and everything in the invented company is invented.

## Where it stops for a person

It takes no action, so there is nothing to approve. An exception to a clause, and anything about one person's pay, contract or visa status, goes to the People team.
