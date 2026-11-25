# Inventory Forecasting, the workflow form

This form is a workflow of fixed steps: tools read the rules, the stock and the supply terms, a Python Code step works out the whole plan, one step saves it, and a model only writes the reply. Use it when the whole weekly plan must be worked out once and saved as a result a buyer can rely on. Use the chat form in the folder above for a question about one line and for follow-ups.

## The steps

| # | Step | Kind | What it uses | What it hands on |
|---|---|---|---|---|
| 1 | Request | Request | The person's message, started by hand | Nothing that a later step reads |
| 2 | Read the rules | Tool | `get_replenishment_rules` (stock connection), no arguments | The target cover days and the overstock days |
| 3 | Read stock and sales | Tool | `list_stock_levels`, no arguments | All 60 lines with stock on hand and four weeks of sales |
| 4 | Read supply terms and open orders | Tool | `list_supply_terms`, no arguments | All 60 lines with supplier, lead time, case size and open orders |
| 5 | Work out the plan | Code | [`code-step-1-work-out-the-plan.py.txt`](code-step-1-work-out-the-plan.py.txt), with the outputs of steps 3 and 4 and the two figures of step 2 | The body of the save as JSON text: lines, overstocked lines, summary, author |
| 6 | Save the plan | HTTP request | POST to the stock system's replenishment plan address (`/stock/replenishment-plan` in the invented retailer), a Content-Type header, body `$<step 5>.result` | The answer of the stock system |
| 7 | Write the reply | LLM | The plan from step 5 and the answer from step 6 | The reply |
| 8 | Result | Output | The reply from step 7 | What the person sees |

Notes on the code:

- No loop is needed. Two list reads return all 60 lines. Nothing is read line by line or supplier by supplier.
- The supplier's record in the purchasing system is not read. The supply terms already carry the supplier's name and whether the purchasing system holds it, and the save needs only the supplier id. This is one read fewer than the chat form lists.
- The target cover (14 days) and the overstock limit (56 days) are read from the rules. The code uses exact fractions, so 72.5 cases rounds up to 73 with no floating-point slip.
- The names that start with `$n_` in the code file are the ids of the steps on the cluster where this was built. Put the ids of your own steps in their place.
- [`step.py`](step.py) is the same logic as a plain Python file. It runs on a laptop, and [`../../../../demo-retailer/tests/test_workflow_steps.py`](../../../../demo-retailer/tests/test_workflow_steps.py) holds it to the invented retailer's own answer for every one of the 60 lines.

## Build it by hand

1. In Katonic Studio, choose New agent, "Automate a process", "Blank workflow". Name it and pick the owner team.
2. In the Wizard, under Steps, remove the three sample steps. Add Tool, Tool, Tool, Code, LLM in that order.
3. Switch to Visual. Click each Tool step, choose "Browse & pick a tool", pick the stock connection and the tool. These three tools take no arguments here.
4. Run one test, so that the outputs of the Tool steps appear under "Insert variable". Read the id of each step from its Input - Output tab.
5. Click the Code step and paste the code from the file here, with the ids of your own steps in place of the `$n_` names. A tool's output is pasted into the code as a Python value.
6. Drag "HTTP request" from the palette onto the canvas. Drag from the dot on the right of the Code step to the dot on its left, and from its right dot to the LLM step. Set POST, the address, a Content-Type header and the body `$<step 5>.result`.
7. Click the LLM step and write the prompt. Give it the output of step 5 and the answer of step 6. Tell it to add no line, remove none and change no figure, and to end on the fixed last line of the chat form.
8. On the Test tab, type a request. Reset the retailer before each run, because a run saves a draft. Then publish.

## Results on a development cluster

Run on 25 November 2026 against the invented retailer, with the request "Prepare this week's replenishment plan." The stock system was reset before each run and the saved plan was read back after it.

| | This form | The chat form |
|---|---|---|
| Whole plan saved right, Test tab | 6 of 6 | 5 of 10 |
| Whole plan saved right, Work Room | 1 of 1 | |
| Saves in a run | One | |
| Run time on the Test tab | 12.8 to 16.8 seconds | |
| Run time in the Work Room | 14.9 seconds | |

- Right means the five lines with their cases and suppliers, the three overstocked lines, and three draft orders with their units.
- In all six runs the reply held the figures 87, 73, 145, 1740, 876 and 1160 and the three overstocked lines, with the last line exact.
- In the Work Room run the reads took 0.2 to 0.4 seconds each, the Code step 3.9 seconds, the save 0.03 seconds and the reply 8.4 seconds.

A test counts as passed here only after five runs in a row. That has not been done yet.

## What this form does not do yet

- The save is an HTTP request step and not the connection's save tool, because a Tool step cannot take a list from a Code step. The HTTP request step takes public addresses only and accepts no sign-in header. So this form works only against a system with no sign-in.
- A workflow does one job on one message. The question, follow-up and refusal tests of the folder above are not covered. A question about one line gets the whole plan, saved. Answering a question with no save needs a Branch step, which could not be placed between two steps by hand.
- The person's message reaches a workflow as text. Nothing is taken from it here: no Code step reads the message, and the workflow always works out the whole plan.
- The workflow has no step that approves a plan, and it cannot refuse a request, because it does not read the request.
- The sandbox failed to start in a few runs of the five workflows built that day, about 4 runs in 60. Each such run saved nothing and said why. None of the seven runs counted above was among them.
- The reply is still written by a model. The saved plan does not pass through the model.
