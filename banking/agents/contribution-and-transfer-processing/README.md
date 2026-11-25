# Contribution and Transfer Processing

Checks an employer's contribution file row by row, or a member's transfer form field by field, against the scheme's written procedure, and reports how many passed and which items need a person.

| | |
|---|---|
| Type and form | Multi-agent, agent pipeline with four fixed stages |
| What starts it | A contribution file arriving (the funds system has an event for new contribution batches), or a person naming a transfer form. The bank has no event for transfer forms |
| How people meet it | The bank's own system: a batch report, with failed forms and failed rows going to a person |
| Reads from | The pension scheme's funds system: the written procedure, contribution batches, transfer forms and the member register |
| Changes | Saves a batch result as a draft. It posts nothing and puts nothing on any member's account |
| State | Built on a development cluster on 24 November 2026. Six of seven tests pass five runs in a row; the batch with three faulty rows passed seven runs of eight, the miss being a total added wrongly. Not on the Catalog shelf |

## What it does

The four stages run in this order.

1. Reads the procedure, then the contribution file or the transfer form. A form is text read by machine from a scan, and the reader marks its doubts in square brackets.
2. Checks every row of a file against the four rules for a contribution row, and every field of a form against the rules for a transfer form.
3. For a file, saves the result as a draft first. The funds system works out the counts and totals from the rows and the outcomes saved, and returns them: rows passed and failed, the total of the rows that passed, the total of the rows that failed, the control total and the difference between the control total and the sum of all rows. The agent adds no amount itself; each row's total is the one the system gives.
4. Reports the counts and totals the system returned, as returned, and lists every item that needs a person with the rule it failed and its exact value.

A doubtful field on a form is never guessed. The account number is quoted exactly as the scan was read, and a person reads it from the scan.

## What it does not do

- Post a batch. The funds system has an operation that posts the rows that passed, and the agent is not given it. A person approves every posting.
- Put a contribution on an account, buy units, or approve a transfer.
- Guess, complete or correct a digit, a name or a date.
- Send anything to an employer or a member. A person returns a failed row or contacts the member.
- Save the check of a transfer form. The bank has no operation for that, so a form's report is the agent's reply and nothing is saved. A form's result is not kept anywhere by the agent.
- Start itself on a transfer form. There is no event for one in the bank, so a person names the form, or a clock asks for a sweep.
- Guarantee the same wording on every run. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The pension scheme's funds system, connected as an imported API, with the six operations listed in [`agent.yaml`](agent.yaml) and no others. Do not attach the operation that posts a batch.
- If you want a file to start the agent by itself, a subscription to the funds system's event for new contribution batches, and a small adapter that turns the event's message into a request to the agent. The adapter is not written here.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the six tools above and no others. A platform that can run stages as a team may split the pipeline at the four stages.
3. The seven tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data (bank date 2026-11-24). Reset the bank before a run that saves.

- `BAT-4001`, Harbourlight Services, 5 rows, control total 1,959.10: every row passes, the sum agrees.
- `BAT-4002`, Stillwater Clinic, 6 rows, control total 1,883.00: row 4 names `MEM-5040`, who is not in the register. Row 5 repeats `MEM-5007`. Row 6 has an employee amount of -85.00. Rows 1 to 3 pass, 1,215.50. The control total includes the failed rows.
- `BAT-4003`, already posted: nothing to check or save.
- `FRM-4001`, a transfer form for `MEM-5003`: the account number reads `5 8 2 [unreadable] 7 1 [4 or 9] 3 0`. It goes to a person. The name, date of birth and signature are fine.
- `FRM-4002`, a transfer form for `MEM-5002`: the account number reads in full, `6 1 4 0 9 2 7 7 3 5`. Every check passes.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

A person approves every posting. A failed row goes back to the employer with its rule number, by a person. A form with a doubtful field goes to a person. A batch whose total does not match its control figure goes to a person.
