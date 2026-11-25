# Guest Feedback Analysis, the workflow form

This form is a workflow of fixed steps: a tool reads the comments of one month, a model gives each distinct comment a theme and a yes or no for harm, a Python Code step checks and counts the labels, one step saves the analysis, and a model writes the summary. Use it when a whole month must be analysed once and saved with counts that add up. Use the chat form in the folder above for questions and follow-ups.

## What this form guarantees, and what it does not

- **The counts are guaranteed.** They are the true counts of the labels, by theme and by restaurant, and they always add up to the comments read. If they do not, the code stops and nothing is saved.
- **The labels are not guaranteed.** A label is a model's judgement. The labels were steady here and not fixed. The five test runs agreed on every one of the 260 labels. One further run moved three comments between two themes.
- **Six comments are labelled differently from the retailer's own theme in every test run.** They are two sentences, three comments each: "No napkins or chilli flakes in the bag." and "Too much sauce on the pizza this time." The retailer's data calls them Other. The model calls them Wrong or missing item. Both readings can be defended.
- **The harm list rests on the model.** It held all seven harm comments in every run. Code cannot tell that a harm comment was missed. It only makes sure that none that was marked is dropped.

## The steps

| # | Step | Kind | What it uses | What it hands on |
|---|---|---|---|---|
| 1 | Request | Request | The person's message, started by hand | The message |
| 2 | Find the period | Code | One pattern taken from the message: a year and month. It is the same pattern as [`../../shrink-analysis/workflow/code-step-1-find-the-period.py.txt`](../../shrink-analysis/workflow/code-step-1-find-the-period.py.txt). The text of this step is not kept in this folder | A year and month such as `2026-10` as text |
| 3 | Read the comments of the period | Tool | `list_guest_feedback` (care connection), with the period of step 2 and a limit of 500 | The 260 comments of the month, and the total the system holds |
| 4 | Cut the comments into batches | Code | [`code-step-2-cut-into-batches.py.txt`](code-step-2-cut-into-batches.py.txt), with the output of step 3 | A list of 6 batches as JSON text. Each batch is up to 20 lines of "key, bar, comment" |
| 5 | For each batch | Loop | Loop kind "Parallel", over `$<step 4>.result`, parallel limit 4 | One list of 6 replies, in order |
| 5a | Label one batch | LLM, the body of the Loop | The batch as `$item` in the prompt. Temperature 0 | One line for each line given: "key, bar, theme, bar, yes or no" |
| 6 | Count and check the labels | Code | [`code-step-3-count-and-check.py.txt`](code-step-3-count-and-check.py.txt), with the output of step 3, the Loop step itself and the period of step 2 | The body of the save as JSON text: period, themes with counts and quotes, harm comments, summary, author |
| 7 | Save the analysis | HTTP request | POST to the care system's analysis address (`/care/analysis` in the invented retailer), a Content-Type header, body `$<step 6>.result` | The answer of the care system |
| 8 | Write the summary | LLM | The analysis from step 6 and the answer from step 7 | The reply |
| 9 | Result | Output | The reply from step 8 | What the person sees |

A run makes seven model calls: six to label and one to write the summary.

## The Loop, and why it works in batches

- **What the Loop holds.** An LLM step works as a loop body. Drag an LLM step from the palette and draw two connections: Loop to the LLM step, and the LLM step back to the Loop.
- **What it goes over.** A list printed by a Code step. Step 4 prints `json.dumps` of a list, and "Iterate over" in the Loop is set to `$<step 4>.result`. Each entry is `$item` in the model's prompt.
- **How the labels come back.** As one list, one entry for each pass, each a dict with the model's reply under `text`. The checking Code step reads it as `replies = $<loop step>`. The variable is the Loop step itself.
- **Distinct texts.** Step 4 takes the distinct comment texts: 119 for the 260 comments of October, because guests' words repeat. It gives each a key, K001 to K119. The same words get one label, so they cannot get two labels in one run.
- **Batches of 20.** The 119 lines are cut into batches of 20. That is 6 passes. One comment a pass would be 260 model calls and several minutes. Twenty short lines are few enough for the model to keep its place, and the key on every line lets code catch a line that is dropped or doubled.
- **The "Max iter" box.** It shows 50 and was not touched. At 20 lines a batch, 50 passes cover 1,000 distinct comments. A Loop that reaches the number in that box stops quietly and the run goes on. Here the checking code would then mark every comment whose batch was not labelled as Unlabelled. For a larger month, set the box to the number of batches or more.
- **Real feedback.** Where few comments repeat, labelling each distinct text once saves little. The batches still hold.

What the labelling prompt asks for, in words: one line back for each line given, as "key, bar, theme, bar, yes or no". The theme is one of six fixed names: Late delivery, Wrong or missing item, Cold food, App and payment, Praise, Other. Yes or no says whether the comment describes harm or a safety matter. Nothing else comes back. The text of the prompt that ran is not kept in this folder.

What the checking code does:

- A label that is not on the list, a key the model left out, and a key given two different labels all become "Unlabelled". None is guessed.
- A comment marked as harm goes to the harm list and to no theme.
- It counts by theme and by restaurant, takes the first three comments of each theme by reference as its quotes, and puts the harm comments first.
- If the theme counts and the harm count do not add up to the comments read, it stops and nothing is saved.
- Step 4 stops if the system says the period holds more comments than were read.

Other notes:

- The retailer serves no theme list. So the six theme names are fixed in the code and in the labelling prompt.
- The names that start with `$n_` in the two code files are the ids of the steps on the cluster where this was built. Put the ids of your own steps in their place.
- The body that step 6 prints carries one extra field, `label_codes`: one letter for each comment, so that the labels of two runs can be compared. The save ignores it and it is not kept.
- [`step.py`](step.py) is the same logic as a plain Python file. It runs on a laptop. [`../../../../demo-retailer/tests/test_workflow_steps.py`](../../../../demo-retailer/tests/test_workflow_steps.py) plays the model's part with the retailer's own theme for each comment, and holds the counts to [`SCENARIOS.md`](../../../../demo-retailer/SCENARIOS.md).

## Build it by hand

1. In Katonic Studio, choose New agent, "Automate a process", "Blank workflow". Name it and pick the owner team.
2. In the Wizard, under Steps, remove the three sample steps. Add Code, Tool, Code, Loop, Code, LLM in that order.
3. Switch to Visual. Click the first Code step and paste the period pattern. The message is pasted into the code as bare text, so it must sit inside quotes.
4. Click the Tool step, choose "Browse & pick a tool", pick the care connection and `list_guest_feedback`, and type its arguments as JSON. The period goes in as a string, for example `"$<step 2>.result"`.
5. Run one test, so that the outputs appear under "Insert variable". Read the id of each step from its Input - Output tab.
6. Click the second Code step and paste the first code file here, with the id of your own Tool step in place of the `$n_` name.
7. Click the Loop step. Set the loop kind to "Parallel" and "Iterate over" to `$<step 4>.result`.
8. Drag an LLM step from the palette for the body. Draw Loop to the LLM step and the LLM step back to the Loop. A body step may connect only to the Loop step. Write the labelling prompt as described above, with `$item` in it, and set the temperature to 0.
9. Click the third Code step and paste the second code file here, with the ids of your own steps in place of the `$n_` names.
10. Drag "HTTP request" from the palette onto the canvas. Drag from the dot on the right of the third Code step to the dot on its left, and from its right dot to the last LLM step. Set POST, the address, a Content-Type header and the body `$<step 6>.result`.
11. Click the last LLM step and write the prompt. Give it the output of step 6 and the answer of step 7. Tell it to list the harm comments first, to change no count, and to add no comment and no theme.
12. On the Test tab, type a request that names a month. Reset the retailer before each run, because a run saves a draft. Then publish.

## Results on a development cluster

Run on 25 November 2026 against the invented retailer, with the request "Group the guest feedback for 2026-10 into themes and save the analysis." The feedback system was reset before each run. The saved analysis was read back, and in the five Test tab runs the label of every comment was read from the checking step.

| | This form | The chat form |
|---|---|---|
| The seven harm comments, saved and in the reply | 5 of 5 on the Test tab, and saved in the Work Room run | Listed first in every run that read the whole month |
| Counts by theme the same from run to run | The same in all 5 Test tab runs, label for label over 260 comments. The Work Room run differed by three comments | They vary from run to run. The test on the counts failed one run in three |
| Counts add up to 260 | 6 of 6 | |
| Saved analysis equals what the code printed | 5 of 5 on the Test tab | |
| Run time on the Test tab | 39.8 to 41.6 seconds | |
| Run time in the Work Room | 40.2 seconds | |
| Model calls in a run | 7 | |

- The five Test tab runs gave Late delivery 78, Wrong or missing item 58, Cold food 41, App and payment 24, Praise 30, Other 22. Two earlier runs during the build gave the same counts.
- The retailer's own plan is 78, 52, 41, 24, 30, 28. The difference is the six comments named at the top.
- The Work Room run gave Wrong or missing item 55 and Other 25. Three comments moved. Its labels were not read one by one.
- The first three themes kept their top restaurant in every run: `R-047` 36, `R-014` 20, `R-031` 20. Late delivery and Cold food match the plan exactly.
- No comment was Unlabelled in any run.
- Where the time goes: period step 4 seconds, read 0.5, batches 4.5, loop 13, checking 4, save under 0.1, summary 11 to 15. The Loop step took 12.9 to 13.3 seconds for its six passes.

A test counts as passed here only after five runs in a row. That has not been done yet.

## What this form does not do yet

- It cannot make the labels identical every time. See the section at the top.
- The harm list rests on the model. A harm comment that the model does not mark is not caught by code. A person should still read the comments.
- The save is an HTTP request step and not the connection's save tool, because a Tool step cannot take a list from a Code step. The HTTP request step takes public addresses only and accepts no sign-in header. So this form works only against a system with no sign-in.
- A workflow does one job on one message. The question, follow-up and refusal tests of the folder above are not covered: the three top restaurants as a question, one theme for one restaurant, one restaurant only, a request with no period, and the refusal.
- The person's message reaches a Code step as source text. Only a narrow pattern is taken from it: the year and month.
- The guests' comments and the model's replies also reach the Code steps as text the platform pastes into the code, as Python values. That worked in every run here. It is still a weakness, because a comment is text a stranger wrote.
- The workflow reads one month, the one named in the request. It does not count across months.
- Three Code steps cost about 13 seconds of sandbox starts between them. The period step and the batches step could be one.
- The sandbox failed to start in a few runs of the other workflows built that day, about 4 runs in 60. Each such run saved nothing and said why. None of the six runs counted above was among them.
- The summary is still written by a model. The saved analysis does not pass through that model.
