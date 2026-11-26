# Collections Call Review

For a recorded collections call, it writes a short summary, marks each of the bank's conduct rules followed, breached or not applicable with the exact words from the transcript, drafts the follow-up note, and says whether a supervisor should look.

| | |
|---|---|
| Type and form | Workflow, scheduled agent |
| What starts it | A clock: the day's batch of unreviewed calls. It can also be asked for one call |
| How people meet it | Through the bank's own system: flagged calls and notes go to the supervisor |
| Reads from | The bank's collections system: call transcripts and the conduct rules |
| Changes | Nothing in the bank's records. It saves a call review as a draft, and the call stays unreviewed |
| State | Built on a development cluster. All eight tests pass five runs in a row |
| Website page | [katonic.ai/use-cases/banking-collections-call-review-agent](https://www.katonic.ai/use-cases/banking-collections-call-review-agent) |

## What it does

- Reads the seven conduct rules and then the call: transcript, start time, arrears, customer and member of staff.
- Marks every rule followed, breached or not applicable, each with the exact words from the transcript and the time.
- Writes a short summary and records any promise to pay exactly as it was said.
- Drafts the follow-up note and says whether a supervisor should look.
- Saves the review as a draft and says it was saved only if the system's reply says so.
- In a batch, does the same for every unreviewed call, then ends with a "Batch:" line.

## What it does not do

- Mark a call as reviewed. A supervisor closes the review.
- Contact a customer or anyone else. The note is a draft and is not sent.
- Decide what happens to a caller, or judge a person beyond the words in the transcript.
- Offer a hardship option itself. It says whether the caller did.
- Guarantee the same marks on every run. A transcript shows words, not tone, and the calls that are firm are the hard ones. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's collections system, connected as an imported API, with the four operations listed in [`agent.yaml`](agent.yaml) and no others. The operation that marks a call reviewed is not attached.
- A clock that starts the batch each day, if you want it to run by itself. The agent also answers in a chat for one call.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the four tools above and no others.
3. The eight tests are in [`tests.yaml`](tests.yaml). Three files describe the agent: [`agent.yaml`](agent.yaml), [`instructions.md`](instructions.md) and [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data. Reset the bank before each try, because each one saves a draft:

- `CAL-1001`, Marguerite Oakhaven, loan LN-9005: every rule followed or not applicable, the promise read back. No supervisor.
- `CAL-1002`, Cassius Dunmore, loan LN-9003: the caller states the debt before asking for the date of birth. CR-02 breached. Supervisor.
- `CAL-1003`, Dorian Quillfeather, loan LN-9101: the customer says he lost his job and no hardship option is offered. CR-05 breached. Supervisor.
- `CAL-1004`, Emeric Lowenhall, loan LN-9102: his sister answers and is told the amount. CR-06 breached. The customer never came on the line, so the rules on how he is treated are not applicable. Supervisor.
- `CAL-1005`, Wynne Castellane, loan LN-9103, at 19:35: a firm call that is calm and accurate, inside the hours. No breach. No supervisor.
- Ask it to mark `CAL-1002` reviewed. It must refuse.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

A supervisor reads each flagged call and its note, and closes the review. The agent never marks a call as reviewed and contacts no customer.
