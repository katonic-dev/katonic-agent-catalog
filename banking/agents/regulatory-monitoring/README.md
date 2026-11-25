# Regulatory Monitoring Daily Sweep

Reads the publication feeds of two financial regulators on a clock, works out what is new since its last run, and writes a digest for a compliance officer.

| | |
|---|---|
| Type and form | Workflow, scheduled agent |
| What starts it | A clock. A person can also start a run by hand |
| How people meet it | An application: the Regulatory change desk |
| Reads from | Two public regulator feeds. No sign-in, no connector |
| Changes | Nothing. It has no step that acts |
| State | Built and run on a development cluster. Two of five tests pass five runs in a row; the other three cannot be run five times on live feeds |

## What it does

- Reads the FCA news feed and the ECB press feed each time it runs.
- Keeps a copy of each feed from the last run, and compares the new copy with it.
- Writes one section for each regulator. Under it, each new publication with its title, date and link, or the line "Nothing new since the last run."
- Says so when a feed cannot be read, and does not say that nothing is new.
- Says when a run is the first one for a feed, and reports nothing as new.

## What it does not do

- Change, send or file anything. The digest is the only output.
- Say what a publication means for the bank or what to do about it. That is for the officer.
- Invent a publication. Every item in the digest comes from the lines the comparison reports as added. This is an instruction to the model, backed by the workflow: the model is given only those lines. Check it on your own model.
- Keep the saved copy safe when a feed fails. See "Known limits" below.
- Read sites that need a sign-in. The HTTP step of this platform cannot carry sign-in headers.

## What you set up

- A model for the digest step. Pin one model by name on that step. A new workflow starts on the Balanced tier, and the cluster used here had no working model on that tier.
- Two feed addresses, in [`workflow.yaml`](workflow.yaml). Both must answer from the cluster, not only from your own computer. The Bank of England feed answered from an ordinary computer but was refused from the cluster, so it was not used.
- A schedule. The proof ran every 10 minutes. The folder is set to once a day at 06:00, Dubai time.
- An owner team, which the publish step asks for.

## Build it

These steps were run on a development cluster on 24 November 2026.

1. In Studio, start a new agent, choose to automate a process, pick the blank workflow and continue to build.
2. In **Identity**, give it the name and a one-sentence description, and choose the owner team.
3. In **Trigger**, choose **Schedule** and set the cron expression and the time zone. The time zone list in this view held six zones and not Dubai, so the zone was set in the YAML panel (see step 5).
4. In **Steps**, the blank flow comes with three model steps. They were replaced in step 5.
5. Switch to the **Visual** canvas, open the YAML panel and replace its text with [`workflow.yaml`](workflow.yaml). The panel's editor ignores pasted text, so the text was set through the editor's change handler and then applied with **Apply**. The result is nine steps: the clock, then for each feed an HTTP fetch, a small code step that writes one line per publication (date, title, link), and a `compare_last` step with its own key (`feed_a`, `feed_b`), then one model step and the output.
6. On the model step, in the Visual canvas, open **Model** and pin the model by name. Setting a default model on the agent does not change a step that already exists.
7. The model step's instructions are in [`instructions.md`](instructions.md), word for word. The `$n_...` words in it are references to earlier steps, not blanks to fill in.
8. On the **Test** tab, run the draft once to check that the steps wire up. A draft test neither reads nor writes the saved copy, so the comparison is not proved there. The first draft run failed because the code step's sandbox took more than 20 seconds to start. The second run passed.
9. **Publish** to the development environment, with the owner team and visible to the team. Only Work Room was ticked as the place it runs.
10. On the agent's **Run** tab, start a run by hand twice, then wait for one run started by the schedule. Then try a wrong feed address, put the right one back, and publish again.
11. Set the schedule to once a day, publish, and use **Pause** on the schedule card on the Run tab.

Promoting to production is not described. It was not done.

## Test results

Tests are in [`tests.yaml`](tests.yaml). Counts are real runs of the published version on the model that served the cluster that day.

| Test | Runs | Passed |
|---|---|---|
| 1. First run saves a first copy | 1 | 1 |
| 2. A second run finds nothing new | 2 (one by hand, one by the schedule) | 2 |
| 3. A feed that changed lists only what is new | 0 | not run |
| 4. A feed that cannot be read is said to be unreadable | 1 | 1 |
| 5. A request to add a publication is not followed | 0 | not run |

Each run took 11 to 14 seconds. The schedule started its run at 01:50:00 Dubai time, the set minute. No test has reached five runs, so none counts as passed.

One run gave a test of a kind by accident. After a failed read, the next run listed all 15 ECB items as new, and each matched the live feed.

## Known limits

- **A failed read spoils the saved copy.** The compare step saves what it is given, when it runs. When a feed address answered with an error page, the tidy step found no publications and the compare step saved an empty result. The next good run then listed every publication in the feed as new. The digest was right about that run and wrong in effect. A branch that skips the compare step when the fetch did not return 200 would stop it. That branch is not built.
- **The comparison works line by line.** The ECB feed has almost no line breaks, and a line is capped at 500 characters in the comparison output. That is why each feed goes through a code step first. The code step runs Python in a sandbox, which needs a pod to start.
- **At most 50 added lines are reported.** The digest says so when the comparison was cut short.
- **A publication that moves in the feed without changing is not new.** A reorder alone gives no added lines.
- **The first published run is never a test of change.** It saves a first copy and reports nothing as new.

## Try it

Run the agent by hand from its Run tab and read the digest. To see the state work, run it twice. To see a failed source, change one feed address to one that does not exist on the same site, publish, run, then put the right address back. To see a real change, wait until a regulator publishes something between two runs.

## Where it stops for a person

The compliance officer reads the digest. Nothing is changed, so there is nothing to approve. What a publication means for the bank is for the officer.
