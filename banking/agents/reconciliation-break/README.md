# Reconciliation Break

Gathers both sides of an unmatched item after a reconciliation run, examines each candidate entry, and proposes the match or the adjusting entry with the evidence and the matching rule it relied on. Nothing is posted without approval.

| | |
|---|---|
| Type and form | Workflow, scheduled agent |
| What starts it | A reconciliation run finishing, once for every unmatched item. The bank's reconciliation system can also announce a new break through its event for reconciliation breaks |
| How people meet it | An application: the Reconciliation desk |
| Reads from | The bank's reconciliation system: the break, its candidates, the checks the matcher ran, the matching rules, and the ledger and statement entries, which it reads one by one and searches by account, amount, value date and reference |
| Changes | Saves a draft proposal. The draft matches, posts and reverses nothing |
| State | Built on a development cluster on 24 November 2026. All seven tests pass five runs in a row. Not on the Catalog shelf |
| Website page | [katonic.ai/use-cases/banking-reconciliation-break-agent](https://www.katonic.ai/use-cases/banking-reconciliation-break-agent) |

## What it does

- Reads the break: the unmatched item, its candidate entries and why each is a candidate, and the checks the automatic matcher already ran.
- Reads the entries it relies on, and searches the ledger and the statement to prove what it says: that a match is the only one, that an entry is not repeated, or that nothing exists. Each search is shown with what it was given and what it found.
- Writes one row for the unmatched item, then one for each candidate and one for each search or check that found nothing. Each row puts the break item and the entry it is compared with in the same form (entry id, amount with its currency, value date, reference) so the desk can show them side by side, then the ids and the rule, a mark, and a note with the difference in amount (with its working) or in days.
- Marks each row: unmatched, matches, differs or no counterpart. A search that finds nothing is marked no counterpart: it is a finding, not a failure.
- Writes the last line so that its first sentence names the action and the kind of break (for example "approve the match: mistyped reference."), which the desk shows first.
- Tests each candidate against the matching rules in the rules' own words. A candidate matches only if a rule says so.
- Proposes one of four things: a match, a match with an adjusting entry, the reversal of a duplicate, or a referral to a person.
- Where no entry could belong to the item, says so, shows the searches that prove it and lists every check, and refers the break to a person. It does not force a match.
- Saves the proposal as a draft, and says it was saved only if the system's reply says so.

## What it does not do

- Post a match, post an adjusting entry, reverse an entry or write an item off. A person approves and posts.
- Reverse an entry that is matched to a statement entry.
- Force a match to make the books balance, or adjust a difference that no rule allows.
- Fill a gap, or invent an entry, an amount, a date or a rule.
- Guarantee the same marks on every run. The proposal is a draft for the reconciliation analyst. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's reconciliation system, connected as an imported API, with the eight operations listed in [`agent.yaml`](agent.yaml) and no others. The operation that posts a resolution is not attached.
- The [Reconciliation desk](../../desks/reconciliation/README.md), which sends the case, if you want to meet the agent through a screen. The agent also answers in a chat.
- A schedule, or the bank's event for a new break, to start a run for each unmatched item. The desk can also be filled by hand.
- An API key with the Chat scope for the desk, and the published agent's id.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the eight tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft proposal. For the reconciliation analyst. Not issued.", a seven-column table, and a last line that starts "Proposal:". Change the instructions and the desk's `draft.instruction` setting together.
4. The seven tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data, started with `BANK_TODAY=2026-11-24` so that its dates agree with these answers:

- `BRK-4001`: statement credit STM-8101, 12,480.00. Match with LED-7101: same amount, value date one day earlier, reference differs by one character (RECON-RULE-001). LED-7102 is not the match.
- `BRK-4002`: statement credit STM-8201, 8,000.00. Match with LED-7201 (5,250.00) and LED-7202 (2,750.00), both posted in BATCH-0457 (RECON-RULE-002). LED-7203 is not part of it.
- `BRK-4003`: statement credit STM-8301, 9,985.00. Match with LED-7301 (10,000.00) and propose an adjusting entry of 15.00, debit GL-6120, credit NOS-TESL-01 (RECON-RULE-003).
- `BRK-4004`: ledger debit LED-7402, 4,175.50. A duplicate of LED-7401. Reverse LED-7402, never LED-7401 (RECON-RULE-004).
- `BRK-4005`: statement debit STM-8501, 3,275.40. It cannot be resolved. No candidate exists. The agent proves it with searches: the ledger has no entry for 3,275.40 on any account and none for the reference UNK-77QX, the account holds only LED-7201, LED-7202 (BATCH-0457, 8,000.00 together) and LED-7203 (5,250.00) in the 5 days either side of the value date, and the statement holds STM-8501 once. It lists what it checked and refers the break to a person (RECON-RULE-005).

Everyone and everything in the invented bank is invented.

## Where it stops for a person

The reconciliation analyst approves the match, the adjusting entry or the reversal, or refers the break to the team lead. A person with the authority posts it in the reconciliation system, with their name. Nothing is posted by the agent.
