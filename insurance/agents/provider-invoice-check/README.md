# Provider Invoice Check

Checks a provider's invoice line by line against the agreed tariff and the contract, and lists the differences, each with the clause of the contract. A claims officer decides what is queried with the provider. The agent contacts no provider and corrects nothing.

| | |
|---|---|
| Type and form | Workflow, API agent |
| What starts it | A call from the claims system when a provider's invoice is received |
| How people meet it | An application: the Health claims desk |
| Reads from | The insurer's health system: one provider invoice with its lines, the provider's contract as numbered clauses, and the system's check of every line with the totals and the working |
| Changes | Saves the differences as a draft. The draft queries nothing, pays nothing and contacts nobody |
| State | Built on a development cluster on 26 November 2026. All nine tests pass five runs in a row. Not on the Catalog shelf |

## What it does

- Reads the invoice once. That one read gives the lines, the provider's contract and the system's check of every line.
- Writes one row for every line of the invoice, in the invoice's order: what was charged, what the system says is agreed, the difference, the clause that governs the line in the clause's own words, a mark and a note.
- Gives each line one mark, from the kind the system gives it: agrees, over the tariff, under the tariff, not on the tariff, not chargeable, or discount not applied. The clause is the one the system gives for the line.
- Says plainly why a line differs: charged over the agreed price; a service that is not on the tariff, with no agreement in writing on file; a follow-up consultation inside the contract's free period, with the days the system gives; a medicine charged without the contract's discount.
- Says when a line that looks wrong is right: a follow-up consultation outside the free period is charged.
- Gives the three totals as the system gives them, in rows marked worked out, and the system's working lines unchanged.
- Takes every figure and every count of days from the system. It adds up nothing, rounds nothing and proposes no new price.
- Saves the differences as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: the invoice agrees with the tariff and the contract, query with the provider the lines named, or refer to a claims officer.

## What it does not do

- Write to, call or contact a provider. The provider relations team writes to the provider.
- Decide which lines are queried, or accept an invoice as charged. The claims officer decides.
- Pay or reduce an invoice, or correct a line or an amount.
- Propose a price, a credit or an amount to pay.
- Work out a figure of its own, or use one provider's clause or price for another provider.
- Guarantee the same wording on every run. The invoice check is a draft for the claims officer. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The insurer's health system, connected as an imported API, with the two operations listed in [`agent.yaml`](agent.yaml) and no others.
- The Health claims desk, which sends the invoice's id, if you want to meet the agent through a screen. The agent also answers in a chat.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the two tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading whose last line starts "Saved:", the heading "Draft invoice check. For the claims officer. Not issued.", an eight-column table (the seventh column is called Mark), the heading "Working" with the system's working lines, and a last line that starts "Proposal:". The summary holds no count of marks and is not in the first person.
4. The nine tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`:

- `PI-9501`: every line agrees. The follow-up consultation, `PI-9501-L3`, is 16 days after the first consultation; clause 4.1 gives 14 days, so it is rightly charged. Charged USD 170.00, agreed USD 170.00, difference USD 0.00. Proposal: the invoice agrees with the tariff and the contract.
- `PI-9502`: the X-ray, `PI-9502-L2`, is over the tariff under clause 1.1: USD 80.00 charged, USD 65.00 agreed. Total difference USD 15.00. Proposal: query with the provider, for the claims officer to decide.
- `PI-9503`: the shockwave therapy session, `PI-9503-L2`, is not on the tariff, and no agreement in writing is on file (clause 5.1). Total difference USD 55.00.
- `PI-9504`: the follow-up consultation, `PI-9504-L3`, is 5 days after the first consultation; clause 4.1 gives 7 days, so it is not chargeable. Total difference USD 35.00.
- `PI-9505`: the medicines discount of clause 3.1 was not applied on `PI-9505-L2` (difference USD 2.40) and `PI-9505-L3` (difference USD 1.80). Total difference USD 4.20.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The claims officer reads the invoice check and decides which lines are queried with the provider, or accepts the invoice as charged. The provider relations team writes to the provider. The agent decides nothing, pays nothing and contacts nobody.
