# Coverage Check

Sets a loss against the policy wording: the clause that covers, the exclusions, the limits, the deductible, the conditions and the endorsements, each with its clause number, and says where the wording is silent. It gives a reading for the adjuster and never accepts or declines.

| | |
|---|---|
| Type and form | Workflow, API agent |
| What starts it | A call from the claims system when a claim reaches assessment |
| How people meet it | An application: the Claims assessment desk |
| Reads from | The insurer's claims system (the claim with its whole file, and the claims handling guide) and the policy system (the policy with its schedule and endorsements, and the policy wording with its numbered clauses) |
| Changes | Saves a draft coverage check. The draft decides nothing about the claim |
| State | Written. Not yet built on a cluster |

## What it does

- Reads the claim with its whole file, the policy with its schedule and endorsements, and the whole wording, every time.
- Starts with whether the policy was in force on the date of the loss, as the system gives it. If it was not, the reading stops there with one row.
- Otherwise writes one row for each finding, in order: the covering clause, every endorsement on the policy, each exclusion that the facts touch, each fact the wording is silent on, the limits on what is claimed, the deductible, the conditions.
- Quotes each clause by its number and in its own words. An endorsement changes the wording for that policy and has a row of its own.
- Gives each row one mark: applies, does not apply, excludes, limits, condition met, condition not met, cannot tell or wording silent.
- Says so in a row of its own where a fact matters and no clause speaks of it, and infers nothing.
- Marks cannot tell where the file does not hold the fact a clause turns on, and names the document that would settle it.
- Takes the days from the loss to the report from the system. It works out no amount payable: the settlement calculation does that.
- Writes what rule HG-7 asks: "Recovery possible" with the party and the document that names them, or "No recovery indicated".
- Saves the coverage check as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: within the wording, outside the wording, the policy was not in force, or refer to the adjuster.

## What it does not do

- Accept cover or decline a claim. The reading is for the adjuster, who decides.
- Pay, send a letter, or tell or contact a customer or another party.
- State a clause the wording does not hold, or infer anything from a clause that is not there.
- Guess a fact the file does not hold.
- Pursue a recovery. The recoveries team decides.
- Guarantee the same rows on every run. The coverage check is a draft for the adjuster. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The insurer's claims system and policy system, connected as imported APIs, with the five operations listed in [`agent.yaml`](agent.yaml) and no others.
- The Claims assessment desk, which sends the claim's id, if you want to meet the agent through a screen. The agent also answers in a chat.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the five tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft coverage check. For the adjuster. Not issued.", a six-column table (the fifth column is called Mark), and a last line that starts "Proposal:". The summary holds no count of marks and is not in the first person.
4. The ten tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`:

- `CLM-4001`: a car reversed into a gate post. Clause 1.1 applies, 1.4 applies to the windscreen, 2.5 excludes the interior valet, 3.2 limits the windscreen to USD 500, the deductible under 4.1 is USD 250.00, and 5.1 is met. Proposal: within the wording, for the adjuster to confirm.
- `CLM-4004`: a car driven off from a forecourt with the key in the ignition. Clause 1.2 applies. No clause speaks of a key left in the vehicle. Proposal: refer to the adjuster.
- `CLM-4006`: a theft from a home with the back door unlocked. Clause 1.4 does not apply and 2.3 excludes: the police report (DOC-4006-2) says there is no sign of forced entry. Proposal: outside the wording, for the adjuster to decide.
- `CLM-4008`: the driver was not a named driver. The endorsement END-2008-1 excludes. Proposal: outside the wording, for the adjuster to decide.
- `CLM-4003`: the loss was on 7 Nov 2026, 2 days after the policy period ended on 5 Nov 2026. The reading stops there.
- `CLM-4002`: no document says where the water came from. Clauses 1.3 and 2.1 cannot be told from the file. Proposal: refer to the adjuster.
- `CLM-4005`: clauses 1.1 and 1.3 apply. Condition 5.2 is not met: a person was injured and the file holds no police report. Recovery possible: Sorrel Mackinder, named in DOC-4005-3.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The adjuster reads the coverage check and decides whether cover is accepted or the claim is declined. Where the wording is silent or the file does not hold a fact, the point goes to the adjuster. The recoveries team decides on any recovery. The agent decides nothing and contacts nobody.
