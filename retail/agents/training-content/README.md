# Training Content

Drafts a short training note or a quiz from one procedure of the company's Store Procedures Manual or one policy of its Staff Handbook, with every point tied to its clause. The training lead approves the content.

| | |
|---|---|
| Type and form | Conversational, answering agent |
| What starts it | A colleague's request that names a procedure or a policy |
| How people meet it | Chat |
| Reads from | A knowledge source that holds the Store Procedures Manual and the Staff Handbook |
| Changes | Nothing. It has no tool that acts |
| State | Tested as a draft on a development cluster. Seven of eight tests pass three runs in a row. Not published |

## What it does

- Drafts a training note from one procedure: what it covers, the key points in the order of the clauses, who decides, and what the procedure leaves to another document.
- Drafts a quiz from one procedure: five questions unless asked otherwise, never more than ten, with the answers.
- Ties every point and every answer to its clause, for example "(SP-07 clause 7.1)", and ends on a line that starts "Source:".
- Keeps the figures, times, codes and job titles exactly as the clause gives them.
- Writes one question for each clause, and says so, when a procedure has fewer clauses than the questions asked for.
- Says so and drafts nothing when the documents hold no such procedure.
- Marks every draft "Draft for the training lead to approve."

## What it does not do

- Write a procedure, add a rule or change a figure. The owner of the document does that.
- Add tips, reasons or good practice that the procedure does not give.
- Give a temperature limit. Those are set by the Food Safety Plan, so a note on temperature checks gives the schedule only.
- Publish a note, assign training, enrol anyone, mark a quiz or record a completion.
- Guarantee that a draft is complete. Leaving nothing out and adding nothing is an instruction to the model, not a control. The training lead reads every draft against the procedure.

## What you set up

- A model for the Reasoning tier.
- An embedding model, chosen in Knowledge settings.
- One knowledge source that holds both documents: [`../../policy-library/store-procedures-manual.md`](../../policy-library/store-procedures-manual.md) and [`../../policy-library/staff-handbook.md`](../../policy-library/staff-handbook.md) for the invented company, or your own. Keep the food safety plan and the allergen matrix out of this source, so that the agent can say a limit or an allergen belongs to another document.

## Build it

Built this way as a draft on a development cluster on 25 November 2026.

1. In Knowledge, connect a source by file upload and add the two documents.
2. In Katonic Studio, create a new agent of the kind that answers from your documents.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, write the instructions yourself and paste [`instructions.md`](instructions.md) word for word.
5. Set the model tier to Reasoning.
6. Attach no tools.
7. In Knowledge, attach the source that holds the two documents.
8. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). For the two tests with nothing connected, detach the source and tick "Test the prompt without tools".

## Test results

Run on a development cluster on 25 November 2026, three runs of each test.

- Tested as a draft, with the Store Procedures Manual and the Staff Handbook in a knowledge source. On that cluster an agent with a knowledge source could not be published.
- Seven of the eight tests pass three runs in a row.
- The eighth, a quiz on one procedure, fails every run. The search of the knowledge source never returned one of the procedure's four clauses, so the quiz has three questions. The search ran in a reduced mode on that cluster in every run. Words in the instructions did not cure it.
- One sentence was added so that the agent says when no knowledge source is connected.
- Four of the tests were run on the first text only. The sentence added since is in a part they do not reach.

A test counts as passed here only after five runs in a row. That has not been done yet.

## Try it

The documents of the invented company are in [`../../policy-library/`](../../policy-library/README.md). Ask:

- A training note on SP-07, order remakes. Six clauses, 7.1 to 7.6, with the reason codes R1 to R5.
- A four-question quiz on SP-12, cash handling. The answers are USD 20 (12.2), USD 2,000 (12.3) and USD 150 (12.4), and who counts a till (12.1).
- A five-question quiz on HR-02, sick leave. The policy has three clauses, so it must write three questions and say so.
- A note on SP-04 with the temperature limits. It must give the schedule and no limit (clause 4.4).
- A note on SP-10, lone working. The manual has no such procedure, so it must write nothing.
- Add a rule to SP-07 and publish it. It must refuse both.

Everyone and everything in the invented company is invented.

## Where it stops for a person

The training lead approves every note and every quiz before it is used. A change to a procedure or a policy is for the owner named on the document.
