# Roster Check, the workflow form

This form is a workflow of fixed steps: tools read the rules and the roster, a Python Code step finds every breach, one step saves the check, and a model only writes the reply. Use it when the whole check of one roster must be done once and saved as a result a person can rely on. Use the chat form in the folder above for questions and follow-ups.

## The steps

| # | Step | Kind | What it uses | What it hands on |
|---|---|---|---|---|
| 1 | Request | Request | The person's message, started by hand | The message |
| 2 | Read the rules | Tool | `get_working_time_rules`, no arguments | The rules, each with its limit |
| 3 | List the rosters | Tool | `list_draft_rosters`, no arguments | The six roster rows |
| 4 | Find the roster | Code | [`code-step-1-find-the-roster.py.txt`](code-step-1-find-the-roster.py.txt), with the message and the output of step 3 | One roster id as text, or `NONE` |
| 5 | Read the roster | Tool | `get_draft_roster`, arguments `{"roster_id": "$<step 4>.result"}` | The roster with its colleagues and shifts |
| 6 | Work out the breaches | Code | [`code-step-2-work-out-the-breaches.py.txt`](code-step-2-work-out-the-breaches.py.txt), with the output of step 5 and the list of rules from step 2 | The body of the save as JSON text: breaches, summary, author |
| 7 | Save the check | HTTP request | POST to the people system's save address for that roster (`/people/rosters/<roster id>/check` in the invented retailer), a Content-Type header, body `$<step 6>.result` | The answer of the people system |
| 8 | Write the reply | LLM | The list from step 6 and the answer from step 7. The prompt tells it to add no breach, remove none and change no figure | The reply |
| 9 | Result | Output | The reply from step 8 | What the person sees |

Notes on the code:

- Step 4 takes a roster id from the message, or a site id that it looks up in the list of step 3.
- Step 6 checks every rule from WT-1 to WT-8 and from SR-1 to SR-3. It reads eight limits from the rules of step 2. Two limits are given only in the words of a rule, so they are constants in the code: a break is due on a shift longer than 6 hours, and a young worker's shift starts no earlier than 06:00.
- The names that start with `$n_` in the two code files are the ids of the steps on the cluster where this was built. Put the ids of your own steps in their place.
- [`step.py`](step.py) is the same logic as a plain Python file. It runs on a laptop, and [`../../../../demo-retailer/tests/test_workflow_steps.py`](../../../../demo-retailer/tests/test_workflow_steps.py) holds it to the invented retailer's own answers.

## Build it by hand

1. In Katonic Studio, choose New agent, "Automate a process", "Blank workflow". Name it and pick the owner team.
2. In the Wizard, under Steps, remove the three sample steps. Add Tool, Tool, Code, Tool, Code, LLM in that order.
3. Switch to Visual. Click each Tool step, choose "Browse & pick a tool", pick the people connection and the tool, and type its arguments as JSON.
4. Run one test, so that the outputs of the Tool steps appear under "Insert variable". Read the id of each step from its Input - Output tab.
5. Click each Code step and paste the code from the two files here, with the ids of your own steps in place of the `$n_` names. A tool's output is pasted into the code as a Python value. The message is pasted as bare text, so it must sit inside quotes, as the file shows. Paste only the list of rules, as the file shows: the whole output of the rules gave a syntax error.
6. Drag "HTTP request" from the palette onto the canvas. Drag from the dot on the right of the second Code step to the dot on its left, and from its right dot to the LLM step. Set POST, the address, a Content-Type header and the body `$<step 6>.result`.
7. Click the LLM step and write the prompt. Give it the output of step 6 and the answer of step 7. Tell it to add no breach, remove none and change no figure, and to end on the fixed last line of the chat form.
8. On the Test tab, type a request, for example a roster id. Reset the retailer before each run, because a run saves a draft. Then publish.

With these answers known, the build takes about 15 to 20 minutes.

## Results on a development cluster

Run on 25 November 2026 against the invented retailer. The people system was reset before each run and the saved draft was read back after it.

| | This form | The chat form |
|---|---|---|
| Saved draft right, first build (limits as constants), tests 2 to 7, three runs each | 18 of 18 | 14 of 26 |
| Saved draft right, second build (limits read from the rules) | 7 of 7 runs that completed | |
| Saves in a run | One | |
| Run time on the Test tab | 12.2 to 17.0 seconds | |
| Run time in the Work Room, one run | 15.9 seconds, saved draft right | |

- In the first build the reply named exactly the rules the code found in 18 of 18 runs, with the last line exact.
- Nine runs were made on the second build. Seven completed and all seven saved the right draft. One stopped because the sandbox did not start. One was the site with no roster, which ends as a failed run. Neither saved anything.
- `step.py` has one guard more than the text that ran on the cluster: a shift that ends on the next day is given its true length, by adding 24 hours, and the rest before the next shift is counted from its true end. The result for every roster of the invented retailer is the same with and without it, because none has such a shift.
- The reads took about 0.3 seconds each, the two Code steps 3.7 and 4.4 seconds, the save 0.06 seconds and the reply 4.8 seconds.

A test counts as passed here only after five runs in a row. That has not been done yet.

## What this form does not do yet

- The save is an HTTP request step and not the connection's save tool, because a Tool step cannot take a list from a Code step. The HTTP request step takes public addresses only and accepts no sign-in header. So this form works only against a system with no sign-in.
- The save address is typed into the workflow.
- A workflow does one job on one message. The question, follow-up and refusal tests of the folder above are not covered. The test with nothing connected has no meaning here, because the tools are fixed steps.
- The person's message reaches a Code step as source text. Only a narrow pattern is taken from it: a roster id or a site id. A message that holds three single quotes in a row breaks step 4. A real build should not paste free text into code.
- There is no Branch step. For a site with no roster, step 4 prints `NONE` and step 5 fails the run with the people system's own words. Nothing is saved, but the person gets a failed run and not a plain sentence. The Branch step could not be placed between two steps by hand.
- The sandbox failed to start in a few runs: one of the nine runs on the second build, and one run earlier the same day. Each such run saved nothing and said why. The person has to run it again.
- The reply is still written by a model. It changed nothing in these runs, but nothing in the form stops it. The saved draft does not pass through the model.
- On the development cluster the model step ran on the Fast tier.
- A shift that runs past midnight is only partly handled. `step.py` gives it its true length and its true rest. The text that ran on the cluster does not. Neither counts such a shift as cover for the staffing rules, on either day, and neither tests the hours after midnight against the evening limit for a young worker.
- A person meets a workflow in the Work Room as a "Run workflow" button, an input box and a result page. There is no chat.
