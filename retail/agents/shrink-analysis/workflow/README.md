# Shrink Analysis, the workflow form

This form is a workflow of fixed steps: tools read the tolerance, the counts and the till rows, a Python Code step sets every store and every line against the tolerance, one step saves the analysis, and a model only writes the reply. Use it when the analysis of a whole period must be done once and saved as a result a person can rely on. Use the chat form in the folder above for a question about one store and for follow-ups.

## The steps

| # | Step | Kind | What it uses | What it hands on |
|---|---|---|---|---|
| 1 | Request | Request | The person's message, started by hand | The message |
| 2 | Find the period | Code | [`code-step-1-find-the-period.py.txt`](code-step-1-find-the-period.py.txt), with the message | A year and month such as `2026-10` as text, or `NONE` |
| 3 | Read the tolerance | Tool | `get_shrink_tolerance` (stock connection), no arguments | The store tolerance and the line tolerance |
| 4 | Read the counts by store | Tool | `list_stock_counts`, with the period of step 2 and the view `by_store` | The 8 stores |
| 5 | Read the counts by line | Tool | `list_stock_counts`, with the period of step 2 and the view `by_line` | The 60 lines |
| 6 | Read the till rows of the period | Tool | `list_till_entries` (tills connection), with the period of step 2 and a limit of 500 | All 180 rows of the month |
| 7 | Set stores and lines against the tolerance | Code | [`code-step-2-set-against-the-tolerance.py.txt`](code-step-2-set-against-the-tolerance.py.txt), with the outputs of steps 4, 5 and 6 and the two figures of step 3 | The body of the save as JSON text: stores, lines, summary, author |
| 8 | Save the analysis | HTTP request | POST to the stock system's analysis address for the period (`/stock/counts/<period>/analysis` in the invented retailer), a Content-Type header, body `$<step 7>.result` | The answer of the stock system |
| 9 | Write the reply | LLM | The analysis from step 7 and the answer from step 8 | The reply |
| 10 | Result | Output | The reply from step 9 | What the person sees |

Notes on the code:

- No loop is needed. One read returns the 8 stores, one the 60 lines, and one all 180 till rows of the month.
- Step 2 looks for one pattern in the message: four digits, a hyphen and a month from 01 to 12. Every later step gets the period from step 2, never the message.
- Both tolerances (1.5 and 2.5 percent) are read from step 3. The test is "loss value times 100 is more than the tolerance times the sales value", in exact fractions. So a store at 2.50 percent is beyond the store tolerance, and a store exactly on 1.5 percent is within it.
- The loss percent saved is the one the count gives.
- The till rows are added up by store and kind, for the stores beyond tolerance only. No cashier id and no approver id leaves the code.
- The names that start with `$n_` in the second code file are the ids of the steps on the cluster where this was built. Put the ids of your own steps in their place.
- [`step.py`](step.py) is the same logic as a plain Python file. It runs on a laptop, and [`../../../../demo-retailer/tests/test_workflow_steps.py`](../../../../demo-retailer/tests/test_workflow_steps.py) holds it to the invented retailer's own answers.

## Build it by hand

1. In Katonic Studio, choose New agent, "Automate a process", "Blank workflow". Name it and pick the owner team.
2. In the Wizard, under Steps, remove the three sample steps. Add Code, Tool, Tool, Tool, Tool, Code, LLM in that order.
3. Switch to Visual. Click the first Code step and paste the first code file. The message is pasted into the code as bare text, so it must sit inside quotes, as the file shows.
4. Click each Tool step, choose "Browse & pick a tool", pick the connection and the tool, and type its arguments as JSON. A value from an earlier step goes in as a string, for example `"$<step 2>.result"`.
5. Run one test, so that the outputs of the Tool steps appear under "Insert variable". Read the id of each step from its Input - Output tab.
6. Click the second Code step and paste the second code file, with the ids of your own steps in place of the `$n_` names. A tool's output is pasted into the code as a Python value.
7. Drag "HTTP request" from the palette onto the canvas. Drag from the dot on the right of the second Code step to the dot on its left, and from its right dot to the LLM step. Set POST, the address, a Content-Type header and the body `$<step 7>.result`.
8. Click the LLM step and write the prompt. Give it the output of step 7 and the answer of step 8. Tell it to add no store and no line, remove none and change no figure, and to end on the fixed last line of the chat form.
9. On the Test tab, type a request that names a month. Reset the retailer before each run, because a run saves a draft. Then publish.

## Results on a development cluster

Run on 25 November 2026 against the invented retailer, with the request "Run the shrink analysis for 2026-10." The stock system was reset before each run and the saved analysis was read back after it.

| | This form | The chat form |
|---|---|---|
| Whole-period analysis saved right | 6 of 6 runs that completed | 3 of 6 |
| Runs that did not complete | 2 of 8 | |
| Saves in a run | One | |
| Run time on the Test tab | 15.7 to 18.6 seconds | |
| Run time in the Work Room | 22.4 seconds | |

- Right means both stores, `S-106` and `S-103`, and the three lines, every time. The chat form left `S-106` out in its three misses.
- Five of the completed runs were on the Test tab and one in the Work Room. In all six the reply held 850.85, 489.24, 2.44, 6.68, 5.81, 5.48 and 1.33, and no cashier id or approver id.
- The two runs that did not complete stopped because the sandbox did not start. Nothing was saved in either.
- `step.py` has one guard more than the text that ran on the cluster: it stops, with nothing to save, when the till read says it holds more rows than it gave. The text that ran on the cluster would add up a part of the till rows and say nothing. One read at a limit of 500 holds a month of up to 500 till rows.
- In the Work Room run the period step took 4.7 seconds, the four reads 0.3 to 0.9 seconds each, the second Code step 3.9 seconds, the save 0.06 seconds and the reply 9.0 seconds.

A test counts as passed here only after five runs in a row. That has not been done yet.

## What this form does not do yet

- The save is an HTTP request step and not the connection's save tool, because a Tool step cannot take a list from a Code step. The HTTP request step takes public addresses only and accepts no sign-in header. So this form works only against a system with no sign-in.
- A workflow does one job on one message. The question, follow-up and refusal tests of the folder above are not covered: a question about one store, a request with no period, and the request to say who is at fault.
- The person's message reaches a Code step as source text. Only a narrow pattern is taken from it: the year and month.
- A month with no count fails the run. Asked for 2026-09, the run fails at step 4 with the stock system's own words, and nothing is saved. A message with no month also ends as a failed run. A plain sentence in place of a failed run needs a Branch step, which could not be placed between two steps by hand.
- The sandbox failed to start in a few runs: 2 of the 8 runs of this workflow, and about 4 runs in 60 across the five workflows built that day. Each such run saved nothing and said why. The person has to run it again.
- The reply is still written by a model. The saved analysis does not pass through the model.
