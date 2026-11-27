# Compliance Audit

Checks each file of an audit sample against the insurer's own numbered conduct rules and records what it checked, the rules that are met as well. The compliance officer decides what follows. The agent marks no file as passed or failed, reports nothing and names the rule and the file, never a member of staff.

| | |
|---|---|
| Type and form | Workflow, scheduled |
| What starts it | A schedule, when an audit sample is drawn. Here it is built as a chat agent and a person sends the message; a clock has not started it |
| How people meet it | Its record is sent to compliance. There is no desk. It answers in a chat |
| Reads from | The insurer's conduct system: the audit samples, and one sample with the conduct rules, every file and the system's measure of each file |
| Changes | Saves one audit record for a whole sample as a draft. The draft changes no file, reports nothing and contacts nobody |
| State | Written. Not yet built on a cluster. No test has been run |

## What it does

- Takes one of two requests: a whole sample by its id ("Audit sample AUD-7200."), or one file ("Check file AF-7207 of audit sample AUD-7200.").
- Reads the sample: the conduct rules CND-1 to CND-7, every file with its facts, and the system's measure of each file against the rules that turn on dates.
- Takes every measured result and every figure from the system. It counts no days. A value exactly on a limit meets the rule.
- Reads the file for the two rules that need reading: whether a needs statement is on a sales file (CND-4), and whether a letter that declines a claim names the clause it relies on, by number (CND-3).
- Where a date a rule needs is not on the record, says that it cannot tell, names what is missing and says a person must look at the file. It never guesses.
- Writes one table: a row for each rule that is not met or cannot be told, with the other rules of the file in the Note, and one closing row for each file on which every rule is met or not applicable.
- For a whole sample, saves one audit record with a row for every rule of every file, the rules that are met as well, and says it was saved only if the system's reply says so.
- Names the rule and the file, not the person. It calls nothing a breach.
- Ends with one proposal line: for the compliance officer, with the files and rules not met and those that cannot be told; or no action.

## What it does not do

- Mark a file as passed or failed, or change a result because somebody asks.
- Call a result a breach, or say what a result means. The compliance officer decides.
- Report anything to a regulator, or contact anybody.
- Say who handled a file or who was at fault.
- Guess a missing date, or name the clause a letter should have given.
- Save a record for one file. The system keeps an audit record for a whole sample and refuses a part of one, so a check of one file is a reply only.
- Guarantee the same wording on every run. The record is a draft for the compliance officer. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The insurer's conduct system, connected as an imported API, with the three operations listed in [`agent.yaml`](agent.yaml) and no others.
- For the scheduled use, a clock or an event that sends the sample's id when a sample is drawn. This has not been set up or tried.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the three tools above and no others.
3. The reply keeps one shape so that a person can read it fast: a "Summary" heading whose last line starts "Saved:", the heading "Draft audit record. For compliance. Not issued.", one six-column table with a column called Mark, and a last line that starts "Proposal:". The summary holds no count and is not in the first person.
4. The nine tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`. Send "Audit sample AUD-7200." for the whole sample, or "Check file" with a file id "of audit sample AUD-7200." for one file. The sample covers 1 Oct 2026 to 31 Oct 2026.

- `AF-7201`, claims: every rule met. Acknowledged in 2 working days of 5, decided in 12 of 20. The claim was accepted, so the decline letter rule does not apply.
- `AF-7202`, sales: every rule met. A needs statement is on the file, and the cooling-off notice went in 2 days of 7.
- `AF-7203`, claims: CND-1 not met. Acknowledged after 8 working days, 3 over the limit.
- `AF-7204`, sales: CND-4 not met. No needs statement is on the file.
- `AF-7205`, claims: CND-3 not met. The decline letter of 28 Oct 2026 gives a reason and names no clause.
- `AF-7206`, policy: CND-7 cannot be told. The confirmation letter carries no date. A person must look at the file.
- `AF-7207`, claims: every rule met. Acknowledged on working day 5 of 5 and decided on working day 20 of 20: exactly on both limits, and neither rule fires. The decline letter names clause 2.2.
- `AF-7208`, policy: CND-6 not met. The renewal notice went 15 days before the period ended, 6 short of 21.
- The whole sample: the saved record has 20 rows. Four are not met, one cannot be told, two are not applicable and thirteen are met.

Everyone and everything in the invented insurer is invented, and so is the regulator it names.

## Where it stops for a person

The compliance officer reads the record and decides what each result means and what follows: whether a file is looked at again, whether anything is reported, and whether anything is said to anybody. Where a date is missing, a person finds it. The agent does none of this.
