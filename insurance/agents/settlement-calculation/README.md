# Settlement Calculation

Works out the amount payable on a claim from the invoice and estimate lines, the limits and the deductible, and shows the working line by line. It pays nothing and approves nothing.

| | |
|---|---|
| Type and form | Workflow, API agent |
| What starts it | A call from the insurer's claims system once the invoices are in |
| How people meet it | An application: the Claims assessment desk. It also answers in a chat |
| Reads from | The insurer's claims system (the claim with its whole file) and its policy system (the policy and its wording) |
| Changes | Saves the calculation as a draft. The draft approves nothing, pays nothing and changes no status |
| State | Written. Not yet built on a cluster |

## What it does

- Reads the claim, which comes with every document and every invoice or estimate line, and the wording of the claim's policy.
- Reads whether an adjuster's decision on cover is recorded on the claim. Cover accepted: the proposal is to pay. No decision: it still works the figure out, saves it as a draft and refers the claim to the adjuster with the figure. A decision to decline: it works nothing out and saves nothing, and says who declined, when and under which clause.
- Says which lines the wording does not cover, each with the clause from section 2 of the wording and the reason. That is its one judgement.
- Has the claims system work out the rest: the limits, the deductible, the totals, the amount payable and whose approval the amount needs under rule HG-5 of the claims handling guide. Every figure in the reply is the system's.
- Writes one row for each line with the amount claimed, the amount allowed, the clause and a mark (allowed, limited or not covered), then three rows marked worked out: the total allowed, the deductible and the amount payable.
- Gives the system's working, line by line, under the heading "Working".
- Saves the calculation as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: pay the amount, for the approval of the person rule HG-5 names; or refer to the adjuster.

## What it does not do

- Approve a settlement or pay a claim. The person with the authority for the amount does that.
- Accept cover or decline a claim. The adjuster decides.
- Leave a line out because a limit applies to it. The system applies limits and the deductible.
- Add up. It takes every amount, total and approver from the claims system.
- Contact the customer or anyone else.
- Guarantee the same reading of the wording on every run. The calculation is a draft for the adjuster. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The insurer's claims system and its policy system, each connected as an imported API, with the five operations listed in [`agent.yaml`](agent.yaml) and no others.
- The Claims assessment desk, which sends the claim, if you want to meet the agent through a screen. The agent also answers in a chat.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the five tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft settlement. For the adjuster. Not issued.", a seven-column table (Line, Claimed, Allowed, Clause, Mark, Note after the number), the heading "Working" with the system's working lines, and a last line that starts "Proposal:".
4. The eight tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`. Send "Work out the settlement for claim" and the claim id.

- `CLM-4009`: an escape of water, cover accepted by an adjuster on 6 Nov 2026. Four invoice lines, USD 8,400.00 in all. The new underfloor heating (USD 2,400.00) is not covered under clause 2.5. Trace and access (USD 1,900.00) is limited to USD 1,500.00 by clause 3.4. Total allowed USD 5,600.00, less the deductible of USD 500.00 under clause 4.2: USD 5,100.00, for the approval of the senior adjuster.
- `CLM-4001`: damage to a car, no decision on cover recorded. The interior valet (USD 80.00) is not covered under clause 2.5. The rear windscreen (USD 620.00) is limited to USD 500.00 by clause 3.2. Total allowed USD 2,150.00, less the deductible of USD 250.00: USD 1,900.00, for the approval of the handler. The claim is referred to the adjuster with the figure. An answer of USD 1,980.00 is wrong: it leaves the valet in.
- `CLM-4004`: theft of a car, no decision on cover recorded. No line is left out. The hire car (USD 540.00) is limited to 10 days at USD 40.00 a day by clause 3.4. Total allowed USD 14,600.00, less the deductible of USD 400.00: USD 14,200.00, for the approval of the senior adjuster.
- `CLM-4010`: declined by an adjuster on 20 Nov 2026 under clause 2.2. Nothing is worked out and nothing is saved.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The adjuster reads the draft and decides on cover where no decision is recorded. The person with the authority for the amount under rule HG-5 approves the settlement, and a person records the payment. The agent does neither.
