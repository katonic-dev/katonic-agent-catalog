# Policy and Procedures Assistant

Answers staff questions from the bank's own policies and procedures, and cites the document for each statement.

| | |
|---|---|
| Type and form | Conversational, answering agent |
| What starts it | A staff member's question |
| How people meet it | Chat |
| Reads from | A knowledge source that holds the bank's policies and procedures |
| Changes | Nothing. It has no tool that acts |
| State | Built and tested as a draft on a development cluster. All five tests pass five runs in a row. Not yet published |
| Website page | [katonic.ai/use-cases/banking-policy-and-procedures-assistant](https://www.katonic.ai/use-cases/banking-policy-and-procedures-assistant) |

## What it does

- Answers a question about policy from the documents in the knowledge source you attach, with the policy's code and clause on each rule.
- Says so plainly when the documents do not hold the answer, when they cover only part of it, and when the detail sits in a document that is not attached.
- Is instructed to leave a decision, an exception or one customer's case to the owner the policy names, and to say who that is.

## What it does not do

- Take any action. It does not log a request, send a file, approve an exception or change a record.
- Guarantee the referral. Leaving decisions to the policy's owner is an instruction to the model, not a control. Run the fifth test on your own model before you publish.
- Read customer records, accounts or case files. Attach policy and procedure documents only: the agent can quote anything in an attached source to whoever uses it.
- Say what the law or a regulator requires. It reports what your documents say.
- Answer from general knowledge when your documents are silent.

## What you set up

- A model for the Reasoning tier. The rules for the state with nothing connected, and for leaving a decision to its owner, have to hold against a question the model could answer from memory.
- An embedding model, chosen in Knowledge settings. Documents cannot be indexed without one.
- One knowledge source with your policies and procedures. Make sure each policy names its owner: the agent gives that name and invents none.

## Build it

These steps were run on a development cluster on 24 November 2026.

1. In Studio, start a new agent of the kind that answers from your documents, from the blank starter ("Blank search your docs").
2. In **Identity**, give it a name and a description, and choose the owner team. The publish step asks for an owner team.
3. In **Behavior**, choose to write the instructions yourself from a blank prompt, and paste [`instructions.md`](instructions.md) word for word.
4. Set the model tier to **Reasoning**. A new draft opens on Balanced.
5. In **Tools**, attach nothing.
6. In **Skills**, attach `cite-with-sources`.
7. In **Knowledge**, attach the knowledge source that holds your policies.
8. On the **Test** tab, run the tests in [`tests.yaml`](tests.yaml). For the two tests with nothing connected, detach the source and tick "Test the prompt without tools". Without that tick the platform answers by itself and the instructions are never used.

Publishing is not described yet. On the cluster used for this build, the environment that receives a new agent keeps its own knowledge and did not hold the source, so the publish was refused. The agent was tested as a draft.

## Test results

With the three policies of the invented bank attached, on the model that served the cluster's Reasoning tier that day.

| Test | Runs | Passed |
|---|---|---|
| 1. Nothing connected, gives no answer | 2 | 2 |
| 2. Nothing connected, an action and a deadline | 2 | 2 |
| 3. Answers from the documents and cites | 8 | 8 |
| 4. The detail is in a document that is not there | 7 | 7 |
| 5. An exception is not granted and goes to the policy's owner, on the final instructions | 5 | 5 |

The instructions changed three times during testing, each time because of test 5. Its five runs are all on the final text. Of the runs of tests 1 to 4, only one of test 3 is on the final text. The rest are on the earlier versions, which differ only in the rules for clause numbers and for naming a policy's owner. Before the last change, test 5 passed two of five and then three of five: the answers were right, but some left out the owner or the clause number.

Every reply is in the test report kept with the build. Run the tests on your own model before you rely on them: the same question can get two different answers.

## Try it

The three policies of the invented bank are in [`../../policy-library/`](../../policy-library/README.md). The retention schedule is left out of that library on purpose, and the fourth test relies on it: the agent must say the schedule is not among its documents and give no number of years.

## Where it stops for a person

It takes no action, so there is nothing to approve. A decision, an exception or one customer's case goes to the owner the policy names.
