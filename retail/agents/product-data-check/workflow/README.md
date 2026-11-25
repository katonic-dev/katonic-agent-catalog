# Product Data Check, the workflow form

This form is a workflow of fixed steps: a tool reads every listing, a Loop reads the supplier's specification of each line, a Python Code step compares the two, one step saves the check, and a model only writes the reply. Use it when the whole catalogue must be checked once and saved as a result a content lead can rely on. Use the chat form in the folder above for one line, one small category, questions and follow-ups.

## The steps

| # | Step | Kind | What it uses | What it hands on |
|---|---|---|---|---|
| 1 | Request | Request | The person's message, started by hand | Nothing that a later step reads |
| 2 | Read every listing | Tool | `list_product_listings` (catalogue connection), no arguments | The 60 listings, as `items` |
| 3 | For each line | Loop | Loop kind "Parallel", over `$<step 2>.items`, "Max iter" set to 60, parallel limit 4 | One list of 60 specifications, in order |
| 3a | Read the specification | Tool, the body of the Loop | `get_supplier_specification`, arguments `{"sku": "$item.sku"}` | One specification back to the Loop |
| 4 | Compare each listing with its specification | Code | [`code-step-1-compare.py.txt`](code-step-1-compare.py.txt), with the output of step 2 and the Loop step itself | The body of the save as JSON text: findings, summary, author |
| 5 | Save the check | Tool | `save_product_data_check` (catalogue connection), arguments `$<step 4>.json` | The answer of the catalogue system |
| 6 | Write the reply | LLM | The findings from step 4 and the answer from step 5 | The reply |
| 7 | Result | Output | The reply from step 6 | What the person sees |

Notes on the code:

- Nothing from the message goes into code. The workflow always checks the whole catalogue.
- The code compares four attributes as exact text: net quantity, pack size, allergen statement and country of origin.
- If a specification is missing for any line, the code stops and says which. So a short loop cannot pass as a full check.
- The names that start with `$n_` in the code file are the ids of the steps on the cluster where this was built. Put the ids of your own steps in their place.
- [`step.py`](step.py) is the same logic as a plain Python file. It runs on a laptop, and [`../../../../demo-retailer/tests/test_workflow_steps.py`](../../../../demo-retailer/tests/test_workflow_steps.py) holds it to the ten findings of [`SCENARIOS.md`](../../../../demo-retailer/SCENARIOS.md), value for value.

## How the Loop is built by hand

- The Loop step goes over a list from an earlier step. Here that is `$<step 2>.items`, the listings as the tool returned them. Each entry is `$item` in the body, so the argument of the body tool is `{"sku": "$item.sku"}`.
- The body is whatever sits on a path that leaves the Loop step and comes back to it. With no such path the run stops with: "Loop node has no body: nothing cycles back to it. Draw the repeat path (Loop, steps, back to Loop)."
- A body step may connect only to the Loop step. Adding the steps in a row in the Wizard leaves a connection from the body step to the step after the loop, and the run stops with: "Edge crosses the boundary of Loop through body node. Wire in and out of a loop only via the Loop node itself."
- No way was found to remove one connection. What worked: remove the body step, drag a new Tool step from the palette, then draw three connections by hand. They are Loop to the tool, the tool back to the Loop, and Loop to the step after it.
- The Loop has its own limit, the "Max iter" box. It shows 50. Set it to the number of lines or more: 60 here.
- The results reach the Code step as one list, in order, one entry for each pass. Here that is 60 dicts, each the full answer of the tool. The Code step reads it as `specs = $<loop step>`. The variable is the Loop step itself. The canvas also offers `$<loop step>.results` and `$<loop step>.items` under "Insert variable", but `.results` fails at run time: "tried to access field 'results' on a list value".
- "Arrange" lays a workflow with a loop out in a stack and not in a row. It still runs.

## Build it by hand

1. In Katonic Studio, choose New agent, "Automate a process", "Blank workflow". Name it and pick the owner team.
2. In the Wizard, under Steps, remove the three sample steps. Add Tool, Loop, Code, LLM in that order.
3. Switch to Visual. Click the Tool step, choose "Browse & pick a tool", pick the catalogue connection and `list_product_listings`.
4. Click the Loop step. Set the loop kind to "Parallel", "Iterate over" to `$<step 2>.items` and "Max iter" to 60.
5. Drag a new Tool step from the palette for the body. Pick `get_supplier_specification` and type the arguments `{"sku": "$item.sku"}`. Draw the connections as the section above says.
6. Run one test, so that the outputs appear under "Insert variable". Read the id of each step from its Input - Output tab.
7. Click the Code step and paste the code from the file here, with the ids of your own steps in place of the `$n_` names. A tool's output is pasted into the code as a Python value.
8. Add a Tool step after the Code step that prints the save, and connect it on to the LLM step. Choose "Browse & pick a tool", the catalogue connection and `save_product_data_check`. In the Arguments box put `$<step 4>.json`: the Code step prints the body of the save as one JSON object, and `.json` hands it to the tool as that object. This tool writes, so before publishing either put an Approve step before it or have an admin add a tool approval policy that auto-approves it.
9. Click the LLM step and write the prompt. Give it the output of step 4 and the answer of step 5. Tell it to add no finding, remove none and change no value, and to end on the fixed last line of the chat form.
10. On the Test tab, type a request. Reset the retailer before each run, because a run saves a draft. Then publish.

## Results on a development cluster

Run on 25 November 2026 against the invented retailer, with the request "Check the product data." The catalogue system was reset before each run and the saved check was read back after it.

| | This form | The chat form |
|---|---|---|
| Whole catalogue: saved check right | 5 of 5 | Could not be made in one turn. The cluster stopped a tool after eight calls |
| Specification reads in one run | 60, in every run | |
| Run time on the Test tab | 23.8 to 26.1 seconds | |
| Run time in the Work Room | 25.4 seconds | |
| Run time with the unused step removed, one run | 20.2 seconds | |
| Time of the Loop step, 60 reads | 6.7 to 8.4 seconds | |

- Right means the ten findings of SCENARIOS.md, with attribute, kind and both values, and no other. Three runs were on the Test tab and one in the Work Room. The fifth run came after an unused step was removed.
- The first four runs were made on a build that still held a Code step from a first attempt, between the listings and the Loop. No later step used it. It cost about 4.5 seconds a run, and the run times of those four runs include it. The steps and the build list here leave it out.
- That step was then removed, and the listings read was connected straight to the Loop. One run on the whole catalogue was right, value for value, in 20.2 seconds: listings 0.6 seconds, loop 6.9 for the 60 reads, compare 4.4, save 0.1, reply 8.2.
- The stop after eight calls belongs to a chat agent's turn. A workflow Loop is not held by it.
- Sixty reads at a parallel limit of 4 come to about 0.13 seconds a read.

A test counts as passed here only after five runs in a row. That has not been done yet.

On 25 November 2026 the save was changed from an HTTP request step to the connection's own save tool. The run after the change saved the right result, and no run waited for an approval.

## What this form does not do yet

- The save is the connection's own tool, and that tool writes. A workflow whose Tool step writes can be published only with an Approve step before it, or with a tool approval policy that auto-approves that tool. On the development cluster the save tool was auto-approved, because it saves a draft only and a person decides afterwards. With an Approve step instead, every run waits for a person before the draft is saved.
- A workflow does one job on one message. The question, follow-up and refusal tests of the folder above are not covered.
- The person's message reaches a workflow as text. Nothing is taken from it here: no Code step reads the message, and the workflow always checks the whole catalogue.
- A check of one category is not built. The code takes a category. The workflow would need a narrow Code step to take it from the message.
- A Loop that reaches the number in its "Max iter" box stops quietly. The run says the Loop succeeded and goes on. With the box at 20, the Loop made 20 of the 60 reads. Only the code's own guard stopped the run: "No specification was read for 40 of 60 lines", and nothing was saved. That guard, that every line has a specification, is what keeps a part check from being saved as the whole. Keep it in any change to the code.
- A builder must set "Max iter" to the number of lines or more, and check it again after any edit. When the published workflow was opened for editing, the box read 20 and not the 60 that had been set and published, and the "Iterate over" box was empty. Both had to be set again.
- The step list in the Work Room shows an extra line, "Tool dispatch 20.0s", beside the Loop step. The run still took 25.4 seconds in all, so that figure is not time added on top. What it measures is not known.
- The sandbox failed to start in a few runs of the five workflows built that day, about 4 runs in 60. Each such run saved nothing and said why. None of the five runs counted above was among them.
- The reply is still written by a model. The saved check does not pass through the model.
