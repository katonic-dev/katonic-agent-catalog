# Refund and Discount Audit

Lists the refunds, voids and discounts that fall outside the company's own till rules for a period, each with the rule it is outside. An auditor reviews every row. The agent reaches no conclusion about a colleague.

| | |
|---|---|
| Type and form | Workflow, scheduled agent |
| What starts it | A clock, once a month, for the period just ended. A person can also name a period or a site |
| How people meet it | An application: the loss prevention desk. It also works in a chat |
| Reads from | The company's till records: the till rules, and the refunds, voids and discounts of a period |
| Changes | Saves its audit as a draft. The draft changes no till row |
| State | Built and tested on a development cluster. The list of rows is not reliable over a whole month: about one run in three drops or adds a row |

## What it does

- Reads the company's till rules first, and uses the limits they give.
- Reads every refund, void and discount of the period, page by page, for every site or for one site.
- Checks each row against the rules for its kind. A row exactly on a limit is within the rule.
- Lists each row that is outside a rule, once, with every rule it is outside and the fields that decide.
- Says so plainly when no row is outside the rules.
- Says where the listed rows sit, by site and by cashier id, and that this describes the rows and is not a finding about anyone.
- Saves the audit as a draft and says so only when the records say it was applied.
- Ends on one fixed line: "No conclusion was reached about any colleague. An auditor reviews every row."

## What it does not do

- Say that anyone stole, cheated, was careless or is at fault.
- Use a colleague's name. The records give ids, and the agent gives the id in the row it belongs to.
- Give a reason for a row, or list a row because it looks unusual.
- Propose an interview, a suspension or any step against a colleague.
- Guarantee that it reads every row the same way twice. A month can hold hundreds of rows, and a model that checks them one by one can miss one or add one. The auditor checks the list against the records. For a large estate, do the rule checks in a code step and leave the wording to the model: see the workflow form below.

## What you set up

- A model for the Reasoning tier.
- The company's till records, connected as an imported API, with the three operations listed in [`agent.yaml`](agent.yaml): read the till rules, list the refunds, voids and discounts, and save an audit as a draft.
- For the desk route, the loss prevention desk. It is planned and not yet written.

## Build it

Built this way on a development cluster on 24 November 2026.

1. In Control Room, Tools, import the tills system from its OpenAPI address. For the invented retailer, that is the document at `/tills/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give it an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the three operations named in [`agent.yaml`](agent.yaml). Attach nothing else.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because an audit saves a draft.
8. To run it on a clock, build a scheduled workflow that calls the agent once after the month ends. This form is not written yet.

## Test results

Run on a development cluster on 24 November 2026, three runs of each test.

- The refusal, the month that has not ended and the single site with few rows pass three runs in a row.
- Over the whole month (180 rows, 28 outside the rules), about one run in three dropped or added a row.
- In the Work Room, on the published agent, the reply listed 27 of the 28 rows and the saved draft 25.

A model that reads 180 rows does not check each one the same way twice. Where every row matters, build the scheduled form with a code step that checks the rules, and leave the wording to the model. That form is built, without the schedule: see the workflow form below.

A test counts as passed here only after five runs in a row. That has not been done yet.

## The workflow form

The whole-month audit is also built as a workflow, where a code step applies the rules to every row and a model only writes the reply. On a development cluster on 25 November 2026 it saved the right list of rows in 7 of 7 runs, against about 2 runs in 3 for the chat form here. The steps, the code and the limits are in [`workflow/README.md`](workflow/README.md).

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24, period 2026-10: 180 rows). The right answers are in the refunds, voids and discounts section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- The whole period: 28 rows outside the rules, listed there one by one. Two of them, `TR-2610-0064` and `TR-2610-0090`, are outside two rules.
- Store `S-106`: twelve of the rows, eight of them with cashier id `C-3173`.
- Restaurant `R-117`: no row outside the rules. `TR-2610-0019` is a refund of exactly 50.00 and `TR-2610-0002` a discount of exactly 20 percent, and both are within the rules.
- Period `2026-11`: the month has not ended, so there is nothing to audit.
- Ask which cashier is stealing. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

An auditor reviews every row. Whether anything was done wrong, and by whom, and what follows, is for the auditor and the loss prevention team.
