# Partner Quality

Reviews the insurer's partners (claims administrators, repair networks and suppliers) against their contracts. For one partner or for all of them it sets the month's figures against the numbered service levels and each credential against its expiry date, and lists what is not met, what has expired, what expires within the notice window and what cannot be told. The supplier manager decides what follows. The agent suspends no partner, ends no contract, applies no penalty and writes to no partner.

| | |
|---|---|
| Type and form | Workflow, scheduled |
| What starts it | A schedule, after each month's reports are in. Here it is built as a chat agent and a person sends the message; a clock has not started it |
| How people meet it | Its reviews are sent to the supplier manager. There is no desk. It answers in a chat |
| Reads from | The insurer's reinsurance and partners system: the partners with their service levels, the figures reported for the month, their credentials, and the system's measure of each partner |
| Changes | Saves one review for each partner as a draft. The draft ends no contract, suspends nobody, contacts no partner and changes nothing on the partner's record |
| State | Written. Not yet built on a cluster. No test has been run |

## What it does

- Takes one of two requests: one partner by its id ("Review partner PTN-8908."), or all partners ("Review all partners for the period."). Two or more ids in one message are answered like a list.
- Reads the partner: the numbered service levels of its contract (SL-1 to SL-4), the credentials term (SL-5) with its notice window, the figures reported for the month, the credentials with their expiry dates, and the system's measure.
- Takes every result, every rate, every difference and every count of days from the system. It compares nothing and counts nothing itself.
- For one partner, writes one table: a row for each service level and a row for each credential, each with the measured figure, the limit, a mark and the system's sentence. The marks are met, not met, cannot tell, valid, warning and expired.
- For all partners, writes one row for each partner, also for a partner that is fully within, with the mark within, warning, not met or cannot tell.
- Treats a figure exactly on its limit as met, as the system does.
- Treats a credential that expires within the notice window as a warning, not a miss.
- Where a figure was not reported, says that it cannot tell, gives what is missing in the system's words and says a person must get the figure. It never guesses a rate.
- Gives a partner that is fully within a review that says so.
- Names the contract term and the figure, not a person.
- Saves each review as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: no action; or for the supplier manager, with the items not met, the warnings and what cannot be told.

## What it does not do

- Suspend a partner, end or change a contract, or apply, work out or propose a penalty.
- Write to a partner or contact anybody.
- Say who was at fault, or name a member of staff.
- Save a review that differs from what the system measures, or leave a partner out.
- Work out a rate or a count of days of its own, or guess a figure that was not reported.
- Review a period other than the one the system holds. The system holds the figures of one month and says which.
- Guarantee the same wording on every run. A review is a draft for the supplier manager. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The insurer's reinsurance and partners system, connected as an imported API, with the three operations listed in [`agent.yaml`](agent.yaml) and no others.
- For the scheduled use, a clock that sends the message after each month's reports are in. This has not been set up or tried.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the three tools above and no others.
3. The reply keeps one shape so that a person can read it fast: a "Summary" heading whose last line starts "Saved:", the heading "Draft partner review. For the supplier manager. Not issued.", one seven-column table with a column called Mark, and a last line that starts "Proposal:". The summary holds no count and is not in the first person.
4. The ten tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`. Send "Review partner" and the partner id, or "Review all partners for the period." The figures are for 1 Oct 2026 to 31 Oct 2026 and the measure is taken on 26 Nov 2026.

- `PTN-8901`, claims administrator: fully within. Turnaround 4.1 days of 5.0, complaints 1.25 percent of 2.00, report received 6 Nov 2026, both credentials valid.
- `PTN-8902`, repair network: fully within. Turnaround 7.2 days of 8.0, complaints 2.00 percent of 3.00, re-repairs 3.00 percent of 4.00, report received 9 Nov 2026.
- `PTN-8903`, supplier: SL-1 not met. Turnaround 4.2 days against 3.0, 1.2 days over. Everything else is met.
- `PTN-8904`, repair network: every service level met. The accreditation `PTN-8904-C2` expired on 14 Nov 2026, 12 days before the insurer date. Not met.
- `PTN-8905`, supplier: every service level met. The insurance certificate `PTN-8905-C2` expires on 15 Dec 2026, in 19 days, inside the notice window of 30 days. A warning, not a miss.
- `PTN-8906`, supplier: fully within. 4 complaints on 200 jobs is 2.00 percent against a limit of 2.00 percent: exactly on the limit, which meets it.
- `PTN-8907`, claims administrator: the report's line for complaints is empty, so SL-2 cannot be told. A person must get the figure. Nothing is assumed.
- `PTN-8908`, repair network: SL-3 not met (re-repairs 7.50 percent against 5.00, 2.50 over) and SL-4 not met (report received 17 Nov 2026, 7 days late).
- All partners: three not met, one warning, one that cannot be told and three within.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The supplier manager reads each review and decides what follows: whether a partner is spoken to, whether a renewed credential is asked for, whether a penalty of the contract is applied, and whether a partner is suspended or a contract ended. Where a figure is missing, a person gets it. The agent does none of this.
