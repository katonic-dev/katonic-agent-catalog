# Third-Party Risk Assessment

Compares a supplier's answers to the bank's questionnaire, and the evidence it gave, with the bank's standard for suppliers, requirement by requirement, and drafts the assessment with a recommendation.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A supplier's completed questionnaire arriving at the bank |
| How people meet it | An application: the Third-party risk desk |
| Reads from | Nothing of its own. The desk sends the questionnaire and the passages of the standard in one message |
| Changes | Nothing. It has no tool |
| State | Written, not yet built. The instructions and tests have not been run on a model |

## What it does

- Finds the supplier's tier and, from the standard's clause on tiers, which requirements apply.
- Works through those requirements in the standard's order. For each one it gives the mark (met, partly met, not met or not answered), the supplier's answer in a few words, the evidence it relied on, and the reason.
- Applies the standard's rule on evidence strictly: an answer with no evidence, or with evidence that says something else, does not meet the requirement.
- Reads every date against the case date in the case.
- Leaves a blank answer blank, marks it not answered and says what is missing.
- Ends with one recommendation line, chosen by rule: do not recommend approval (three or more not met), ask the supplier (a blank answer, or missing or contradicting evidence), recommend approval with conditions (only shortfalls the supplier can cure), or recommend approval (all met).
- Says that a tier 1 supplier is approved by the Risk Committee, and that an unmet requirement can be accepted only as a recorded exception.

## What it does not do

- Approve a supplier, or say it did. The officer decides and the Risk Committee approves a tier 1 supplier.
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

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word. They are the same text as `agent-instructions.md` in the desk's folder.
2. The agent is a chat agent on the Reasoning tier with no tools, no skills and no knowledge source.
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft assessment. For review by the third-party risk officer. Not issued.", a seven-column table, and a last line that starts "Recommendation:". Change the instructions and the desk's `draft` settings together.
4. The six tests are in [`tests.yaml`](tests.yaml).

## Try it

Four invented suppliers are in [`../../desks/third-party-risk/cases.json`](../../desks/third-party-risk/cases.json). Each states its case date.

- Larkspur Cloud Archive Ltd: a weak tier 1 supplier. Do not recommend approval.
- Tessaly Payment Gateway Services: a strong tier 1 supplier that left 4.3 blank. Ask the supplier.
- Pennyfarthing Print and Mail Ltd: 2.3 contradicted by its own policy, 3.3 with no evidence. Ask the supplier.
- Harrowfield Records Storage Ltd: everything met except two shortfalls it states itself, 4.3 (partly met) and 5.4 (not met, USD 4 million). Recommend approval with conditions.

Everyone and everything here is invented.

## Where it stops for a person

The third-party risk officer makes every recommendation. A tier 1 supplier is approved by the Risk Committee (MTB-STD-041, clause 7.4), and an unmet requirement can be accepted only as a recorded exception with an end date (clause 7.5).
