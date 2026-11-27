# Policy Servicing

For servicing staff. Prepares a mid-term change from a change request: what is asked, which numbered servicing rule it touches, the premium adjustment as the system worked it out, and any gap in cover. The servicing officer decides and makes the change. The agent never changes a policy, charges or returns a premium, cancels a policy or contacts a customer or a broker.

This agent does not prepare renewal documents: the servicing system it reads has no operation for them, so a person prepares them.

| | |
|---|---|
| Type and form | Conversational, acting agent |
| What starts it | A servicing officer's request, with the id of a change request |
| How people meet it | An application: the Policy servicing desk. It also works in a chat |
| Reads from | The insurer's policy servicing system: one change request with the policy as it stands on the effective date, each referral rule with whether it applies, the premium adjustment with its working, the gap check and the points to raise |
| Changes | Saves the change as a draft. The draft changes no policy, charges and returns no premium, cancels nothing and contacts nobody |
| State | Written. Not yet built on a cluster |

## What it does

- Reads the change request once. It comes whole, so no second read is needed.
- Writes a table of eleven rows, always in the same order: the request, what changes, one row for each of the six referral rules (SR-1 backdating, SR-2 an address in another rating area, SR-3 an increase in a sum insured, SR-4 a cancellation with an open claim, SR-5 a young driver, SR-8 a policy not in force on the effective date), the premium adjustment (SR-6), a gap in cover (SR-7), and the effective date beside the insurer date (SR-7).
- Gives each rule's row the system's own sentence, word for word, and the mark the system gives: applies or does not apply. A value exactly on a limit does not make a rule apply.
- Gives the premium adjustment as the system worked it out, with the system's working. Where the system worked none out, it gives the system's reason and no figure.
- Points out a gap in cover with the system's dates and count of days, and an effective date that is before the insurer date.
- Takes every sum, percentage, age and count of days from the system. It adds up nothing and counts no days.
- Saves the change as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: ready for the servicing officer, refer to underwriting, refer to the team leader, or ask the requester. Where something must be raised under rule SR-7, the line names it.
- Asked in the same message to make the change now or to charge the premium, prepares the draft and refuses the rest in one sentence of the summary.

## What it does not do

- Change a policy, add a driver, change a vehicle, an address or a sum insured, or cancel a policy. The servicing officer does that.
- Charge or return a premium, or work one out. The system does the sum.
- Refer a request. A referral is a proposal that a person acts on.
- Set a rule aside or save a draft that leaves out a rule that applies.
- Tell or contact a customer or a broker.
- Prepare renewal documents. The servicing system has no operation for them. Asked for one, the agent says so in one sentence.
- Write the endorsement wording. Certificate and Endorsement Preparation does that.
- Guarantee the same wording on every run. The draft is for the servicing officer. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The insurer's policy servicing system, connected as an imported API, with the two operations listed in [`agent.yaml`](agent.yaml) and no others.
- The Policy servicing desk, which sends the officer's request, if you want to meet the agent through a screen. The agent also works in a chat.

## Build it

Written, not yet built on a cluster. The steps will be written here once they have been run on one. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the two tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading whose last line starts "Saved:", the heading "Draft policy change. For the servicing officer. Not issued.", a six-column table (the fifth column is called Mark), and a last line that starts "Proposal:".
4. The ten tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`. Each line is "Prepare the change on change request" and the id.

- `CHG-7301`: a change of address inside rating area RA-2. No rule applies and the premium does not change. Proposal: ready for the servicing officer.
- `CHG-7302`: a change of address from RA-3 to RA-1. SR-2 applies and no premium adjustment is worked out. Proposal: refer to underwriting.
- `CHG-7303`: the contents sum insured from USD 40,000.00 to USD 50,000.00, an increase of 25.00 percent. SR-3 applies. Proposal: refer to underwriting.
- `CHG-7304`: a driver added from 4 Nov 2026, 20 days before the request was received and 22 days before the insurer date. SR-1 applies. The driver is 45, so SR-5 does not. Proposal: refer to the team leader, with the 22 days to raise.
- `CHG-7305`: a cancellation of a policy with an open claim. SR-4 applies and no return premium is worked out. Proposal: refer to the team leader.
- `CHG-7306`: a cancellation on 6 Dec 2026 with new cover from 11 Dec 2026. A return premium of USD 381.00, and 4 days without cover, 7 Dec 2026 to 10 Dec 2026. Proposal: ready for the servicing officer, with the gap to raise.
- `CHG-7307`: a change of vehicle with a rating quote. An additional premium of USD 73.00. Proposal: ready for the servicing officer.
- `CHG-7308`: the sum insured for a vehicle raised by exactly 20.00 percent. SR-3 does not apply. An additional premium of USD 60.40. Proposal: ready for the servicing officer.

`CHG-7305` follows its claim in the claims system as it stands, so its answer changes once that claim is closed.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The servicing officer reads the draft, decides and makes the change. Where rule SR-2, SR-3 or SR-5 applies, underwriting reads the request first. Where rule SR-1, SR-4 or SR-8 applies, the servicing team leader does. A person decides what is done about a gap in cover, and a person contacts the customer or the broker. The agent changes nothing and contacts nobody.
