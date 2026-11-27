# Treaty Recovery

Lists the paid claims that reach a treaty's attachment point with no recovery raised, or with too little raised, for a period or for one claim, each with the term and the system's working. The system does every sum. The reinsurance accountant raises recoveries. The agent never raises a recovery, never books anything and never writes to a reinsurer.

| | |
|---|---|
| Type and form | Workflow, scheduled |
| What starts it | A schedule, at the end of each period. Here it is built as a chat agent and a person sends the message; a clock has not started it |
| How people meet it | An application: the Reinsurance desk |
| Reads from | The insurer's reinsurance system: the paid claims of a period with what each recovers under the treaties, and one paid claim with its payments, its event and the system's working |
| Changes | Saves the recovery list as a draft. The draft raises no recovery, books nothing and tells no reinsurer |
| State | Written. Not yet built on a cluster. No test has been run |

## What it does

- Takes one of two requests: a period ("List the recoveries to raise on the paid claims of the period."), or one paid claim by its id ("Check paid claim RCL-8804 for a recovery."). With no dates the system uses its own period, from the first day of the treaty year to the insurer date, and says which.
- Reads the paid claims with the system's working for each: the treaty that answers, the loss measured, what is recoverable, what is raised so far, what is still to raise, and every step as a sentence with the number of the term.
- Writes one row for every claim checked, with the treaty, what was paid, what is to raise, the terms, a mark and the system's working. The marks are: to raise, raised for too little, needs a person and nothing due.
- Lists a claim with a recovery raised for too little with what is still to raise, not the whole recovery.
- Gives nothing on a claim that is exactly on the attachment point, on a recovery raised in full, or on a share collected in the quarterly account.
- Marks a claim whose date of loss is outside the treaty period as one that needs a person. It is not listed as a recovery and carries no amount.
- Reads the claims of one event together, where the treaty's term on one event says so. Asked about one claim of an event, it reads the other claims of the event as well and gives each its share as the system works it out.
- Ends the table with what is to raise in all, as the system adds it.
- Takes every amount from the system. It adds up nothing, takes no share and compares no amount with an attachment point or a limit.
- Saves the list as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: no action, or for the reinsurance accountant, with the claims to raise, the claims that need a person and the total.

## What it does not do

- Raise a recovery or a cash call. The reinsurance accountant raises them.
- Book a recovery or a reinstatement premium.
- Write to a reinsurer. The reinsurer is told by the reinsurance accountant and by nobody else.
- Work out an amount of its own, or put an amount on a claim the system says needs a person.
- Change an amount or a status, or leave a claim out.
- Run by itself on a clock. That is how it is meant to be used, and it has not been set up or tried.
- Guarantee the same wording on every run. The list is a draft for the reinsurance accountant. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The insurer's reinsurance system, connected as an imported API, with the three operations listed in [`agent.yaml`](agent.yaml) and no others.
- The Reinsurance desk, if you want to meet the agent through a screen. The desk is not built yet. The agent also answers in a chat.
- For the scheduled use, a clock that sends the message at the end of each period. This has not been set up or tried.

## Build it

This agent is written and has not been built on a cluster. It is meant to run on a schedule; here it is a chat agent that a person starts. The steps will be written here once they have been run. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the three tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading whose last line starts "Saved:", the heading "Draft recovery list. For the reinsurance accountant. Not issued.", an eight-column table (the seventh column is called Mark), and a last line that starts "Proposal:". The summary is not in the first person and holds no count but the system's.
4. The ten tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`.

- The period, with no dates: 11 paid claims with a payment from 1 Jan 2026 to 26 Nov 2026. Five have something to raise, USD 1,010,000.00 in all as the system adds it: `RCL-8803`, `RCL-8804`, `RCL-8806`, `RCL-8808` and `RCL-8809`. `RCL-8807` needs a person. Nothing is due on the other five.
- Payments from 1 Oct 2026 to 31 Oct 2026: `RCL-8806`, `RCL-8808` and `RCL-8809`, with USD 800,000.00 to raise.
- `RCL-8803`: USD 410,000.00 paid, no recovery raised. USD 160,000.00 to raise under `TRY-8651` (term 4).
- `RCL-8804`: USD 600,000.00 paid. USD 350,000.00 is recoverable and `RCV-8851` raised USD 300,000.00 before the last payment. USD 50,000.00 more to raise.
- `RCL-8805`: USD 250,000.00 paid, exactly on the attachment point. Nothing is recovered.
- `RCL-8806`: USD 1,150,000.00 paid. The recovery is capped at the limit of USD 750,000.00 (term 5), and USD 150,000.00 stays with the insurer.
- `RCL-8807`: the date of loss, 29 Dec 2025, is 3 days before the treaty period starts (term 3). Needs a person. No amount.
- `RCL-8808` and `RCL-8809`: two claims from one event, `EVT-8891`. Each alone is below the attachment point. Term 6 adds them: USD 300,000.00, so USD 50,000.00 is to raise, USD 30,000.00 on `RCL-8808` and USD 20,000.00 on `RCL-8809`.
- `RCL-8810`: quota share under `TRY-8652`, below the cash call threshold. The share goes in the quarterly account. Nothing to raise now.
- `RCL-8811`: quota share, the cash call `RCV-8852` is raised in full. Nothing more to raise.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The reinsurance accountant reads the list and decides which recoveries and cash calls are raised, books them with the reinstatement premium, and tells the reinsurer. Where a date of loss is outside the treaty period, a person checks which treaty year answers. The agent does none of this.
