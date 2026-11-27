# Claims Leakage Review

Reviews closed claims against the insurer's numbered handling standards. For each claim it sets what was paid, line by line, beside what the system works out should have been paid, and lists the claims paid outside the standards with the standard, the amount and the reason. The claims quality team decides what follows. The agent recovers no money, reopens no claim and names no person.

| | |
|---|---|
| Type and form | Workflow, scheduled |
| What starts it | A schedule, at the end of each review period. Here it is built as a chat agent and a person sends the message; a clock has not started it |
| How people meet it | Its findings are sent to the claims quality team. There is no desk. It answers in a chat |
| Reads from | The insurer's investigations system: the handling standards, the closed claims of a period with their payment files, and the system's test of one claim against every standard |
| Changes | Saves one finding for each claim as a draft. The draft reopens no claim, asks nobody for money back and changes nothing on the claim |
| State | Written. Not yet built on a cluster. No test has been run |

## What it does

- Takes one of two requests: one closed claim by its id ("Review closed claim CLM-6103."), or a period ("Review the closed claims of the period."). With no dates the system uses its own period, the 30 days up to the insurer date, and says which.
- Reads the handling standards, and the closed claim with its payment file: the invoices with their lines, what was allowed on each line, the deductible taken, the approvals, every payment and whether a recovery was raised.
- Has the system work out what should have been paid and test the claim against every standard. Every result and every figure in the reply is the system's. The agent adds up nothing.
- For one claim, writes one table: a row for each invoice line, a row for each payment, a row for each standard with the system's sentence, and a last row with what was paid, what should have been paid and the difference. Each row has a mark: met, not met, cannot tell or worked out.
- For a period, writes one row for each claim of the period, also for a claim paid correctly, with the mark within the standards, outside the standards or cannot tell. It gives no total across claims, because the system gives none.
- Gives a claim that was paid correctly a finding that says so.
- Where the record is incomplete, says that it cannot tell, names what is missing in the system's words and gives no amount. A person looks at the file.
- Names the standard and the payment, not the person. Where the system's sentence gives the name of a member of staff who approved, the reply gives the role alone.
- Saves each finding as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: no action; for the claims quality team, with the standards not met and the difference; or cannot tell, needs a person, with what is missing.

## What it does not do

- Recover money or ask anybody for money back.
- Reopen a claim, change a payment or raise a recovery.
- Say who was at fault, name the member of staff who handled or approved a claim, or judge a person's work.
- Save a finding that differs from what the system works out, or leave a claim out of a review.
- Work out an amount of its own, or guess one where the record is incomplete.
- Contact a customer, a supplier or another party.
- Guarantee the same wording on every run. A finding is a draft for the claims quality team. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The insurer's investigations system, connected as an imported API, with the five operations listed in [`agent.yaml`](agent.yaml) and no others.
- For the scheduled use, a clock that sends the message at the end of each review period. This has not been set up or tried.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the five tools above and no others.
3. The reply keeps one shape so that a person can read it fast: a "Summary" heading whose last line starts "Saved:", the heading "Draft leakage finding. For the claims quality team. Not issued.", one eight-column table with a column called Mark, and a last line that starts "Proposal:". The summary holds no count and is not in the first person.
4. The ten tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`. Send "Review closed claim" and the claim id, or "Review the closed claims of the period."

- `CLM-6101`: paid correctly. The rear windscreen was invoiced at USD 610.00 and paid at its limit of USD 500.00 (clause 3.2). USD 1,680.00 should have been paid and was. No standard fires.
- `CLM-6102`: paid correctly. USD 6,854.00 is above a handler's authority; a senior adjuster's approval is on the file, and recovery REC-0412 was raised on 7 Nov 2026. No standard fires.
- `CLM-6103`: the deductible of USD 250.00 was not taken. LS-1 not met. USD 1,690.00 should have been paid, USD 1,940.00 was paid, difference USD 250.00.
- `CLM-6104`: the line `CLM-6104-L1`, a gold bracelet not listed in the schedule, was allowed at USD 3,400.00 where the limit is USD 2,500.00 (clause 3.2). LS-2 not met. USD 3,100.00 should have been paid, USD 4,000.00 was paid, difference USD 900.00.
- `CLM-6105`: payment `CLM-6105-P3` repeats `CLM-6105-P1` against invoice MRJ-0448. LS-5 not met. USD 2,690.00 should have been paid, USD 4,740.00 was paid, difference USD 2,050.00.
- `CLM-6106`: USD 6,850.00 was paid on a handler's approval alone. LS-3 not met. The amount is right: difference USD 0.00.
- `CLM-6107`: the file names another driver as at fault and no recovery is raised. LS-4 not met. The amount is right: difference USD 0.00.
- `CLM-6108`: a payment of USD 1,930.00 was made against invoice DDD-2291, which is not on the file. Cannot tell, needs a person. Nothing is worked out.
- The period: all eight claims, closed from 27 Oct 2026 to 26 Nov 2026. Five are paid outside the standards, one cannot be told and two are paid within the standards.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The claims quality team reads each finding and decides what follows: whether money is asked back, whether a claim is opened again, whether a recovery is raised late, and whether anything is said to anybody. Where the record is incomplete, a person finds the missing document. The agent does none of this.
