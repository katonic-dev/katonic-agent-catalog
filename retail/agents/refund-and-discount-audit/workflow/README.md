# Refund and Discount Audit, the workflow form

This form is a workflow of fixed steps: tools read the till rules and every till row of a month, a Python Code step applies the rules to every row, one step saves the audit, and a model only writes the reply. Use it when the audit of a whole month must be done once and saved as a list an auditor can rely on. Use the chat form in the folder above for questions and follow-ups.

## The steps

| # | Step | Kind | What it uses | What it hands on |
|---|---|---|---|---|
| 1 | Request | Request | The person's message, started by hand | The message |
| 2 | Find the period | Code | [`code-step-1-find-the-period.py.txt`](code-step-1-find-the-period.py.txt), with the message | A year and month such as `2026-10` as text, or `NONE` |
| 3 | Read the till rules | Tool | `get_till_rules` (tills connection), no arguments | The rules in words |
| 4 | Read every till row of the period | Tool | `list_till_entries`, with the period of step 2 and a limit of 500 | All 180 rows of the month, and the total the system holds |
| 5 | Apply the rules to every row | Code | [`code-step-2-apply-the-rules.py.txt`](code-step-2-apply-the-rules.py.txt), with the output of step 4 | The body of the save as JSON text: rows with their rules, summary, author |
| 6 | Save the audit | HTTP request | POST to the tills system's audit address for the period (`/tills/audits/<period>` in the invented retailer), a Content-Type header, body `$<step 5>.result` | The answer of the tills system |
| 7 | Write the reply | LLM | The audit from step 5 and the status of the save from step 6 | The reply |
| 8 | Result | Output | The reply from step 7 | What the person sees |

Notes on the code:

- No loop is needed. One read returns all 180 rows of the month, because the limit is 500. The code stops with a plain message when the system says it holds more rows than it gave. So a month of more than 500 rows fails loudly and is not audited in part.
- Step 2 looks for one pattern in the message: four digits, a hyphen and a month from 01 to 12. Nothing else of the message is used.
- The two figures of the rules are constants in the code: 50.00 (TC-1) and 20 percent (TC-3). The till rules give them only in words and have no figure field to read.
- A row outside two rules is saved once, with both. Amounts are compared as exact fractions, so a refund of exactly 50.00 and a discount of exactly 20 percent are within the rules.
- The code counts the listed rows by site and by cashier id, and adds the sentence that a count of rows is not a finding about anyone. It gives no reason for any row.
- The name that starts with `$n_` in the second code file is the id of a step on the cluster where this was built. Put the id of your own step in its place.
- [`step.py`](step.py) is the same logic as a plain Python file. It runs on a laptop, and [`../../../../demo-retailer/tests/test_workflow_steps.py`](../../../../demo-retailer/tests/test_workflow_steps.py) holds it to the 28 rows of [`SCENARIOS.md`](../../../../demo-retailer/SCENARIOS.md), row for row and rule for rule.

## Build it by hand

1. In Katonic Studio, choose New agent, "Automate a process", "Blank workflow". Name it and pick the owner team.
2. In the Wizard, under Steps, remove the three sample steps. Add Code, Tool, Tool, Code, LLM in that order.
3. Switch to Visual. Click the first Code step and paste the first code file. The message is pasted into the code as bare text, so it must sit inside quotes, as the file shows.
4. Click each Tool step, choose "Browse & pick a tool", pick the tills connection and the tool, and type its arguments as JSON. A value from an earlier step goes in as a string, for example `"$<step 2>.result"`.
5. Run one test, so that the outputs of the Tool steps appear under "Insert variable". Read the id of each step from its Input - Output tab.
6. Click the second Code step and paste the second code file, with the id of your own step in place of the `$n_` name. A tool's output is pasted into the code as a Python value.
7. Drag "HTTP request" from the palette onto the canvas. Drag from the dot on the right of the second Code step to the dot on its left, and from its right dot to the LLM step. Set POST, the address, a Content-Type header and the body `$<step 5>.result`.
8. Click the LLM step and write the prompt. Give it the output of step 5 and the whole answer of step 6, so that the reply can give the version of the saved draft. Tell it to add no row, remove none and change no figure, and to end on the fixed last line of the chat form.
9. On the Test tab, type a request that names a month. Reset the retailer before each run, because a run saves a draft. Then publish.

## Results on a development cluster

Run on 25 November 2026 against the invented retailer, with the request "Audit refunds, voids and discounts for 2026-10." The tills system was reset before each run. The saved audit was read back and compared row by row and rule by rule.

| | This form | The chat form |
|---|---|---|
| List of rows saved right over the whole month | 7 of 7 | about 2 runs in 3 |
| Saves in a run | One | |
| Run time on the Test tab | 24.7 to 27.2 seconds | |
| Run time in the Work Room | 28.9 seconds | |

- Right means the 28 rows of SCENARIOS.md with their rules, and no other row. Six runs were on the Test tab and one in the Work Room.
- In all six Test tab runs the reply held all 28 row ids and no other row id, with the last line exact.
- Most of the run time is the model writing the table of 28 rows.

A test counts as passed here only after five runs in a row. That has not been done yet.

## What this form does not do yet

- The save is an HTTP request step and not the connection's save tool, because a Tool step cannot take a list from a Code step. The HTTP request step takes public addresses only and accepts no sign-in header. So this form works only against a system with no sign-in.
- A workflow does one job on one message. The question, follow-up and refusal tests of the folder above are not covered, and neither is a request with no month.
- The person's message reaches a Code step as source text. Only a narrow pattern is taken from it: the year and month.
- An audit of one site is not built. The code can do it: for the invented retailer it gives 12 rows for `S-106` and none for `R-117`. The site would have to be taken from the message by a second narrow Code step, at about 4 seconds more a run.
- A month that has not ended gets a thin answer. Asked for 2026-11, the run completes, the system holds no rows, the save is refused with status 409, and the reply says the audit was not saved. Nothing is saved. The reply prints an empty table and does not say in plain words that the month has not ended. That needs a Branch step, which could not be placed between two steps by hand.
- The reply lacks the version number of the saved draft. In the build that was tested, the model was given only the status of the save and not the text of its answer. That was a slip in the prompt and is not a limit of the form. Step 8 of the build list above gives the model the whole answer.
- The sandbox failed to start in a few runs of the five workflows built that day, about 4 runs in 60. Each such run saved nothing and said why. None of the seven runs counted above was among them.
- The reply is still written by a model. The saved audit does not pass through the model.
