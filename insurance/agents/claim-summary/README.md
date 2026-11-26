# Claim Summary

Writes the summary an adjuster reads first: the loss, the policy and whether it was in force, the documents, the amounts, the people, recovery and the open points, each with its source. It does not say whether the loss is covered.

| | |
|---|---|
| Type and form | Workflow, API agent |
| What starts it | A call from the claims system when an adjuster opens a claim file |
| How people meet it | An application: the Claims intake desk |
| Reads from | The insurer's claims system (the claim with its whole file, and the claims handling guide) and the policy system (the policy) |
| Changes | Saves a draft summary. The draft changes no status and sends nothing |
| State | Written. Not yet built on a cluster |

## What it does

- Reads the claim with its whole file, the policy it is made under and the claims handling guide.
- Checks first that the documents describe one claim: the same policyholder, the same vehicle or home, the same date of loss. Where a document names another, it shows both values with both ids.
- Writes seven rows, always in the same order: the loss, the policy, the documents, the amounts, the people, recovery, the open points. Each row has its source and one mark: stated, not provided, records disagree or open.
- Says whether the policy was in force on the date of the loss, as the system gives it.
- Names anyone injured and each sign of a vulnerable customer that rule HG-1 lists, with the document or note it comes from.
- Writes what rule HG-7 asks: "Recovery possible" with the party and the document that names them, or "No recovery indicated".
- Shows both records, with both ids, where two records disagree about the loss, and chooses neither.
- Saves the summary as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: ready for the adjuster, open points first, or refer to a handler.

## What it does not do

- Say whether the loss is covered. The coverage check gives a reading and the adjuster decides.
- Accept cover, decline a claim, pay, close a file, assign a claim, send a letter or contact anyone.
- Choose between two records that disagree. A handler settles which one stands.
- Test each document against everything the checklist says it must show. The pack check does that.
- Add up amounts or count days. Those come from the system.
- Guarantee the same wording on every run. The summary is a draft for the adjuster. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The insurer's claims system and policy system, connected as imported APIs, with the four operations listed in [`agent.yaml`](agent.yaml) and no others.
- The Claims intake desk, which sends the claim's id, if you want to meet the agent through a screen. The agent also answers in a chat.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the four tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft claim summary. For the adjuster. Not issued.", a six-column table of seven rows (the fifth column is called Mark), and a last line that starts "Proposal:". The summary holds no count of marks and is not in the first person.
4. The eight tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`:

- `CLM-4001`: a clean motor claim. The policy was in force on 17 Nov 2026, the four documents are in the file, nobody was injured. No recovery indicated, no open points. Proposal: ready for the adjuster.
- `CLM-4002`: an escape of water. The plumber's report is not in the file and the photographs (DOC-4002-3) cannot be read. Proposal: open points first.
- `CLM-4005`: a collision with another car. A passenger was taken to hospital. No police report. The repair estimate names another registration than the policy. Recovery possible: Sorrel Mackinder, named in DOC-4005-3. Proposal: refer to a handler.
- `CLM-4007`: a fire. The claim form (DOC-4007-1) and the fire service report (DOC-4007-2) disagree on where it started: both are shown and neither is chosen. The customer is 81, lives alone and is out of his home. The contents list is missing. Proposal: refer to a handler.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The adjuster reads the summary and decides what happens to the claim. A handler settles a point on which two records disagree, and takes a claim where a person was injured or the customer may be vulnerable. The recoveries team decides on any recovery. The agent contacts nobody.
