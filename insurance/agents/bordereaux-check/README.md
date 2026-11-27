# Bordereaux Check

When a bordereau comes in, checks every row against the numbered terms of its binder or treaty and lists the differences for the reinsurance accountant. The system measures every figure and date and adds the totals again. The agent reads the description of each risk against the excluded risks, which the system does not read. The reinsurance accountant decides what is queried. The agent never rejects a bordereau, never changes a figure and never writes to a coverholder or a reinsurer.

| | |
|---|---|
| Type and form | Workflow, event-triggered |
| What starts it | A new bordereau being received |
| How people meet it | An application: the Reinsurance desk |
| Reads from | The insurer's reinsurance system: one bordereau with every row as it was sent, the binder or treaty with its numbered terms, and the system's measure of every row and total |
| Changes | Saves the list of differences as a draft. The draft rejects nothing, changes no premium and contacts nobody |
| State | Written. Not yet built on a cluster. No test has been run |

## What it does

- Reads the bordereau once. That one read gives the rows, the binder or treaty with its terms, and the system's measure.
- Lists each difference the system measures, with the row, the number and heading of the term, and the system's sentence with its figures: a risk over the maximum line, outside the territory or the period, a class that is not allowed, commission at the wrong rate, the wrong share, a claim over the claims authority with no agreement, a row that does not add up, a row declared twice.
- Gives the totals a row of their own where the system says they do not add up, under the term the system gives with the totals.
- Takes the age of machinery from the system, which measures it from the year of installation on the row. The agent compares no years.
- Reads the description of every risk against the excluded risks of the term, which the system does not measure. A row is listed only where the words of the description plainly put the risk in an excluded group. Where the description does not say, the row is not listed.
- Marks each row of its table: measured, where the system measured the difference, or read from the description, where the agent read it. The reader can see which is which.
- Does not list a row that is exactly on a limit, or a claim over the authority that carries the agreement the term asks for. It names them in the closing row as within.
- Ends the table with one closing row: how many rows are within every measured term, as the system counts them.
- Gives a bordereau with no difference a finding that says so, and saves it.
- Takes every figure, every count of days and every count of rows from the system. It adds up nothing.
- Saves the list as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: no differences, or query with the sender the rows named, for the reinsurance accountant to decide.

## What it does not do

- Reject or accept a bordereau. The reinsurance accountant decides.
- Change, correct or leave out a figure, a row or a difference.
- Write to a coverholder, a reinsurer or anybody else. A person writes to whoever sent the bordereau.
- Work out a figure of its own, or use one binder's terms for another.
- Decide that a risk in an excluded group stays bound or comes off.
- Guarantee the same wording on every run. The list is a draft for the reinsurance accountant. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The insurer's reinsurance system, connected as an imported API, with the two operations listed in [`agent.yaml`](agent.yaml) and no others.
- The Reinsurance desk, which sends the bordereau's id, if you want to meet the agent through a screen. The desk is not built yet. The agent also answers in a chat.

## Build it

This agent is written and has not been built on a cluster. The steps will be written here once they have been run. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the two tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading whose last line starts "Saved:", the heading "Draft bordereau differences. For the reinsurance accountant. Not issued.", a five-column table (the fourth column is called Mark), and a last line that starts "Proposal:". The summary is not in the first person and holds no count but the system's.
4. The nine tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`. Send "Check bordereau" and the id.

- `BDX-8701`: risks bound under the household binder `BND-8601`, 12 rows. Row 5 is USD 75,000.00 over the maximum line (term 3). Row 7 is at Lake Sorrin, Veldmark, outside the territory (term 2). Row 8 is a cottage with a thatched roof, an excluded risk (term 7): the agent reads this one, the system does not measure it. Row 3 is exactly on USD 750,000.00 and is not listed. The totals add up.
- `BDX-8702`: risks bound under the pleasure craft binder `BND-8602`, 10 rows. Row 5 took USD 270.00 of commission where 20.00 percent is USD 240.00 (term 5). Row 7 starts on 28 Mar 2026, 4 days before the period (term 4). Row 9 repeats row 4 (term 9). No description is an excluded risk.
- `BDX-8703`: claims paid under `BND-8601`, 9 rows. Row 5 states USD 3,850.00 where the indemnity and the fees add to USD 3,650.00, and the total is USD 200.00 too high for the same reason (term 9). It is one difference, seen in a row and in the total: the table and the saved draft show it twice, once for row 5 and once for the totals. Row 4, exactly on the claims authority, and row 7, with an agreement reference, are not listed.
- `BDX-8704`: cessions under the quota share treaty `TRY-8652`, 8 rows. No differences. Row 5 cedes USD 2,000,000.00, exactly on the maximum line. The system measures the age of the machinery on every row against term 7 (25 years): all are within. Proposal: no differences.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The reinsurance accountant reads the list and decides what is queried with whoever sent the bordereau, and whether the bordereau is accepted. A person writes to the coverholder or the reinsurer. The agent decides nothing, changes nothing and contacts nobody.
