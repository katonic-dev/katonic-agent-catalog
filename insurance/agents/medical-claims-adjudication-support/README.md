# Medical Claims Adjudication Support

For a medical claim the claims engine holds for review: says why it was held, sets out what the assessor needs from the file, and suggests a determination with its reasons. The assessor decides every held claim. The agent pays nothing and declines nothing.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A medical claim being held for review by the claims engine |
| How people meet it | An application: the Health claims desk |
| Reads from | The insurer's health claims system: the held claim with its lines and documents, the member's cover on the date of service, the earlier claims it is compared with, what the plan's terms give, and the medical policy for a medical necessity hold |
| Changes | Saves a suggested determination as a draft. The draft decides nothing, pays nothing and contacts nobody |
| State | Written. Not yet built on a cluster |

## What it does

- Reads the held claim once. The claim comes whole in one read.
- Starts with the hold reason the claims engine set: duplicate, eligibility, limit or medical necessity, with the engine's note.
- Sets each line beside the earlier claim lines the system compared it with. A line is a duplicate only when the member, the provider, the code and the date of service are all the same. The same code on another date is not a duplicate, and the days between the two dates are the system's.
- Gives the member's cover on the date of service in the system's own sentence.
- For a claim held for the limit, gives the system's note on each line: the amount within the limit and the amount over it.
- For a claim held for medical necessity, writes one row for each criterion of the medical policy, judged from the documents: met, not met, or not stated. A criterion the file says nothing about is not stated, and the provider is asked.
- Ends the table with what the plan's terms give, as the system works it out: within the limits, over the limits, the member's share and what the plan pays. That row is not a decision to pay.
- Adds up nothing and counts no days. Every figure is the system's.
- Saves the suggested determination as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: pay as the plan allows, do not pay, ask the provider, or refer to the medical reviewer. Each is for a person to decide.

## What it does not do

- Pay a claim, decline a claim or record a decision. The assessor decides every held claim.
- Decide that a medical policy is failed. Where a criterion is not met, the medical reviewer reads the claim.
- Query or contact a provider, or tell or contact a member.
- Work out a figure of its own, or guess a fact the file does not hold.
- Guarantee the same rows on every run. The determination is a draft for the assessor. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The insurer's health claims system, connected as an imported API, with the two operations listed in [`agent.yaml`](agent.yaml) and no others.
- The Health claims desk, which sends the claim's id, if you want to meet the agent through a screen. The agent also answers in a chat.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the two tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading whose last line starts "Saved:", the heading "Draft determination. For the assessor. Not issued.", a six-column table (the fifth column is called Mark), and a last line that starts "Proposal:". The summary holds no count of marks and is not in the first person.
4. The ten tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`:

- `MC-9101`: held as a duplicate, and it is one. `MC-9011` is for the same member, provider, code and date of service, 6 Nov 2026, and was paid on 11 Nov 2026. Proposal: do not pay, for the assessor to decide.
- `MC-9102`: held as a duplicate, and it is not one. `MC-9012` has the same code, but its date of service is 10 Nov 2026 against 17 Nov 2026, 7 days apart. Proposal: pay as the plan allows, USD 33.60.
- `MC-9103`: held for eligibility. The member's cover ended on 27 Oct 2026, and 14 Nov 2026 is 18 days after the end. Proposal: do not pay, for the assessor to decide.
- `MC-9104`: held for the limit. USD 70.00 is within the limits and USD 43.40 over them, the member's share is USD 14.00, and the plan pays USD 56.00. Proposal: pay as the plan allows, USD 56.00.
- `MC-9105`: held for medical necessity. The clinical notes, `MC-9105-D1`, meet all three criteria of MP-301. Proposal: pay as the plan allows, USD 620.00.
- `MC-9106`: held for medical necessity. Criteria 1 and 3 of MP-302 are met. The file holds no report by the treating physiotherapist, so criterion 2 is not stated. Proposal: ask the provider.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The assessor reads the draft determination and decides whether the claim is paid. Where a criterion of the medical policy is not met, the medical reviewer reads the claim. Where the file lacks what a criterion asks for, a person asks the provider. The agent decides nothing and contacts nobody.
