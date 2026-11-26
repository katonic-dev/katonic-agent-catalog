# Post-Incident Review

Given a closed incident, it plans its own investigation across the IT operations records, stops when it has a root cause the records support or has shown that they cannot settle it, and drafts the review. It blames no person.

| | |
|---|---|
| Type and form | Autonomous, autonomous agent |
| What starts it | A person choosing a closed incident |
| How people meet it | An application, a deployed app that lists closed incidents and shows the draft review. The app is not written yet. Until it is, the agent is used in a chat |
| Reads from | The bank's IT operations system: the incident, metrics, changes and runbooks |
| Changes | Nothing in the bank. It saves the review as a draft |
| State | Built on a development cluster. All six tests pass five runs in a row |
| Website page | [katonic.ai/use-cases/banking-post-incident-review-agent](https://www.katonic.ai/use-cases/banking-post-incident-review-agent) |

## What it does

- Plans its reads, then lets each answer decide the next, and stops when one cause is supported or when the records show they cannot settle it.
- Tests a first assumed cause in the timeline against the metrics and the later entries, and says what the records show.
- Notices when a change record was corrected after the event and keeps both times.
- Writes the review in a fixed order: root cause, timeline with sources, contributing factors, what went well, what did not, proposed actions, what is not known.
- Where the evidence does not settle the cause, lists the candidates with what supports and what weighs against each, and says what record would settle it.
- Leaves the owner and the date of every action empty. The bank's system refuses a review that names an owner.
- Saves the review once as a draft and says it was saved only if the system says it was applied.

## What it does not do

- Name a person as the cause or as at fault. It writes about steps, records, teams and systems.
- Assign an owner or a date to an action.
- Review an open incident, change any record or service, or mark the review approved.
- Say a cause is certain when the records only support it.
- Guarantee the same wording on every run. The review is a draft for the incident manager. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's IT operations system, connected as an imported API, with the six operations listed in [`agent.yaml`](agent.yaml) and no others.
- The application, if you want to meet the agent through a screen. It is not written yet.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the six tools above and no others.
3. The six tests are in [`tests.yaml`](tests.yaml). Three files describe the agent: [`agent.yaml`](agent.yaml), [`instructions.md`](instructions.md) and [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data (bank date 2026-11-24). Reset the bank before each try, because a review is saved as a draft:

- `INC-7004`: closed. Logins to online banking failed after the identity team rotated the token signing key at 14:02 (change ITC-8106), ahead of the 22:00 plan. The first assumed cause, database connection pool exhaustion, was wrong. The change record was corrected at 16:40.
- `INC-7001`: still open. It must say a review is written after the incident is closed, and save nothing.
- Ask who was at fault in `INC-7004`. It must refuse to name a person.
- Ask it to assign the actions to the engineer on call with a date. It must refuse.
- Ask for `INC-7999`. The system does not hold it.

The bank holds no closed incident whose evidence leaves the cause open, so the rule to list candidates has no test yet.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

A person assigns every owner and every date, decides what the review finally says, and approves it.
