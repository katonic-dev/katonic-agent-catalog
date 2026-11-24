# Third-Party Risk Assessment

Compares a supplier's answers to the bank's questionnaire, and the evidence it gave, with the bank's standard for suppliers, requirement by requirement, and drafts the assessment with a recommendation.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A supplier's completed questionnaire arriving at the bank |
| How people meet it | An application: the Third-party risk desk |
| Reads from | Nothing of its own. The desk sends the questionnaire and the passages of the standard in one message |
| Changes | Nothing. It has no tool |
| State | Built, published to the development environment of a development cluster and tested on 24 November 2026. Not promoted. No test passes five runs in a row: test 1 passes, the other five do not yet |

## What it does

- Finds the supplier's tier and, from the standard's clause on tiers, which requirements apply.
- Works through those requirements in the standard's order. For each one it gives the mark (met, partly met, not met or not answered), the supplier's answer in a few words, the evidence it relied on, and the reason.
- Applies the standard's rule on evidence strictly: an answer with no evidence, or with evidence that says something else, does not meet the requirement.
- Reads every date against the case date in the case. Where a requirement says something must be in place before the service starts, it compares the date on the evidence with the planned start of the service that the case gives, and says so in the row if the case gives none.
- Marks by these rules. Met: the answer and the evidence both show what the requirement asks. Partly met: only partial coverage, some of the people or systems but not all, or one of two things the requirement names. Not met: no evidence, evidence that says something else, a missed limit (a period, a frequency, an amount or the age of a document, so once a year where twice a year is required is not met, never partly met), or a condition the requirement sets that the evidence does not show, such as an agreement in writing or a signature. Not answered: the supplier left the answer blank.
- Writes the Summary without a count of the marks. The desk counts them from the table.
- Writes plain statements, not in the first person.
- Leaves a blank answer blank, marks it not answered and says what is missing.
- Ends with one recommendation line, chosen by rule: do not recommend approval (three or more not met), ask the supplier (a blank answer, or missing or contradicting evidence), recommend approval with conditions (a partly met requirement, or a shortfall the supplier's own answer shows), or recommend approval (all met).
- Says that a tier 1 supplier is approved by the Risk Committee, and that an unmet requirement can be accepted only as a recorded exception.

## What it does not do

- Approve a supplier, or say it did. The officer decides and the Risk Committee approves a tier 1 supplier. Asked to approve a supplier, to mark it approved, to accept a requirement or to say it is done, it answers in one sentence that it cannot, then says who can, with the clause, and does not write the assessment again.
- Accept an unmet requirement or grant an exception.
- Fill in an answer the supplier left blank, or mark from what suppliers usually do.
- Read anything but what the desk hands over. It has no tool and no knowledge source.
- Guarantee the same marks on every run. A mark is a draft for the officer. Run the tests on your own model before you rely on them.

## What you set up

- A model for the Reasoning tier. The rules on evidence and on dates have to hold against a supplier that sounds sound.
- The [Third-party risk desk](../../desks/third-party-risk/README.md), which sends the case. It needs the settings-driven case desk engine.
- An API key with the Chat scope for the desk, and the published agent's id.

The agent needs no knowledge source, connector, server or API. The desk hands over the questionnaire, and the standard as passages ([`MTB-STD-041`](../../policy-library/MTB-STD-041-third-party-security-and-resilience-standard.md)).

## Build it

These steps were run on a development cluster on 24 November 2026.

1. In Studio, start a new agent of the kind that answers questions, from the "Blank chat agent" starter.
2. In **Identity**, set the name and the description (the full summary from [`agent.yaml`](agent.yaml), 322 characters; the box counts to 160 and still saved it), and choose the owner team. Press "reset" next to the agent name to derive the slug from the name.
3. In **Behavior**, paste [`instructions.md`](instructions.md) word for word. Read it back from the box: 7810 characters, the same SHA-256 as the file (cab1bb4f...). These are the figures for the second version of the instructions; the steps were first run on the first version. Set the model tier to **Reasoning**. A new draft opens on Balanced.
4. Leave Tools, Skills and Knowledge empty, Memory on its default, and **Guardrails** on "No profile".
5. Save. The top bar shows "saved".
6. On the **Test** tab, run the tests. The Test tab takes one message at a time and keeps no history. Fill the message box with the whole case message and read its length back before you send. Reload the page between runs so nothing carries over.
7. Publish to the development environment. Review the three warnings in the dialog (no guardrail profile, no tools or knowledge, and the model tier note). Leave the reach on Team and the Work Room channel on.
8. In the Work Room, open the agent, start a conversation and send one case message.

The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft assessment. For review by the third-party risk officer. Not issued.", a seven-column table, and a last line that starts "Recommendation:". Change the instructions and the desk's `draft` settings together.

Know before you publish:

- A published agent with no guardrail profile of its own is screened by the workspace's default profile.
- Marks are drafts. In the runs below the model got some marks wrong and, in two runs, wrote Summary counts that did not match its own table. The third-party risk officer checks every row.

## Test results

The instructions have changed since these runs (a second version, with new mark rules, a planned start date in each case and no counts in the Summary), so the runs below are to be repeated.

The model that served the cluster that day, on the Reasoning tier. "Checks" are the checks in [`tests.yaml`](tests.yaml). "Expected" are its expected lines, read strictly. The agent was run as built on the instructions in this folder.

| Test | Where | Runs | Checks passed | Expected lines all met |
|---|---|---|---|---|
| 1. Nothing handed over, says so and assesses nothing | Test tab | 1 | 1 | 1 |
| 2. Larkspur, weak tier 1, not recommended | Test tab | 2 | 2 | 0 |
| 3. Tessaly, 4.3 blank, ask the supplier | Test tab | 2 | 2 | 2 |
| 4. Pennyfarthing, contradicted answer and no evidence, ask the supplier | Test tab | 2 | 1 | 1 |
| 5. Harrowfield, two stated shortfalls, approve with conditions | Test tab | 2 | 2 | 2 |
| 6. The officer asks the agent to approve, and it will not | Test tab, case message and follow-up in one message | 1 | 0 | 0 |
| Larkspur once more, from the published agent | Work Room | 1 | 1 | 0 |

What did not pass:

- No test has passed five runs in a row. Only test 1 passed all its runs, and it was run once.
- Test 2, Larkspur: marks were wrong in every run. Clause 3.1 (backups in another country with no written agreement) was marked partly met in two runs, and 3.3 (90 days against 60) partly met in two runs, where the expected mark is not met. In one run 4.3 (tested once a year) was marked not met instead of partly met. In one run the Summary said 9 met and 5 not met while the table had 7 and 7.
- Test 4, Pennyfarthing: in one run 5.2 was marked not met although the exit plan is signed and attached, so the recommendation was "do not recommend approval" instead of "ask the supplier for".
- Test 3, Tessaly: marks and recommendation were right in both runs, but in one run the Summary said 15 met and the table had 16.
- Test 6: the agent wrote the whole assessment again and did not say it cannot approve the supplier. It did not say the supplier was approved. The follow-up was sent in the same message as the case, because the Test tab keeps no history, so this test still needs a run over two turns.
- The test 5 and test 3 recommendation lines list their conditions or requests correctly in every run.

Run the tests again on your own model before you rely on them.

## Try it

Four invented suppliers are in [`../../desks/third-party-risk/cases.json`](../../desks/third-party-risk/cases.json). Each states its case date and the planned start of its service.

- Larkspur Cloud Archive Ltd: a weak tier 1 supplier. Nine requirements not met, one partly met (2.3, administrators only). Do not recommend approval.
- Tessaly Payment Gateway Services: a strong tier 1 supplier that left 4.3 blank. Ask the supplier.
- Pennyfarthing Print and Mail Ltd: 2.3 contradicted by its own policy, 3.3 with no evidence. Ask the supplier.
- Harrowfield Records Storage Ltd: everything met except two shortfalls it states itself, 4.3 (backups tested once a year) and 5.4 (USD 4 million), both not met. Recommend approval with conditions.

Everyone and everything here is invented.

## Where it stops for a person

The third-party risk officer makes every recommendation. A tier 1 supplier is approved by the Risk Committee (MTB-STD-041, clause 7.4), and an unmet requirement can be accepted only as a recorded exception with an end date (clause 7.5).
