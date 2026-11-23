# Policy and Procedures Assistant

Answers staff questions from the bank's own policies and procedures, and cites the document for each statement.

| | |
|---|---|
| Type and form | Conversational, answering agent |
| What starts it | A staff member's question |
| How people meet it | Chat |
| Reads from | A knowledge source that holds the bank's policies and procedures |
| Changes | Nothing. It has no tool that acts |
| State | Written. Not yet built on a cluster, and its tests have not been run on a model |

## What it does

- Answers a question about policy from the documents in the knowledge source you attach, with the policy's code and clause where the passage shows them.
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

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent of the kind that answers from documents, on the Reasoning tier, with no tools.
3. The five tests are in [`tests.yaml`](tests.yaml).

## Try it

The three policies of the invented bank are in [`../../policy-library/`](../../policy-library/README.md). The retention schedule is left out of that library on purpose, and the fourth test relies on it: the agent must say the schedule is not among its documents and give no number of years.

## Where it stops for a person

It takes no action, so there is nothing to approve. A decision, an exception or one customer's case goes to the owner the policy names.
