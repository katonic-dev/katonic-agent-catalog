# Roster Check

Checks a draft roster against the working time rules and the company's own staffing rules, and lists each breach with the rule, the colleague and the shift. The manager who owns the roster changes it.

| | |
|---|---|
| Type and form | Workflow, API agent |
| What starts it | A call from the rostering tool with a roster number. A person can also name a roster |
| How people meet it | Inside the company's own system: the rostering tool calls it and shows the list. It also works in a chat |
| Reads from | The company's rostering records: the draft roster with its colleagues and shifts, and the working time and staffing rules |
| Changes | Saves its check as a draft on the roster. The draft changes no shift |
| State | Written. Not yet built on a platform |

## What it does

- Reads the rules first, each with its number and its limit, and then the roster.
- Goes through the roster rule by rule: shift length, rest between shifts, weekly hours, breaks, the limits for young workers, the weekly rest day, a shift manager at every trading time, two people to open and to close, and a first aider at every trading time.
- Lists each breach with the rule number, the colleague's number, the shift's number, the day and the figures the roster shows.
- Treats a figure exactly on a limit as keeping the rule, and does not list it.
- Says so plainly when the roster keeps every rule.
- Saves the check as a draft and says so only when the records say it was applied.
- Ends on one fixed line: "This check lists breaches. The manager who owns the roster changes it."

## What it does not do

- Allocate, move, swap or shorten a shift, or say who should cover.
- Propose a change to the roster.
- Rate a colleague, or say anything about one. A colleague is a number and a role.
- Publish a roster. It is not given the operation that does.
- Use a rule of its own, or the working time rules of any country. The records give the rules.
- Guarantee the arithmetic of a model. Rest between two shifts and who is on shift at a given time are worked out by the model from the shift times, and a model can get that wrong. Run the tests on your own model before you rely on them.

## What you set up

- A model for the Reasoning tier.
- The company's rostering records, connected as an imported API, with the 4 operations listed for it in [`agent.yaml`](agent.yaml): list the rosters, read one roster, read the rules, and save a check as a draft.
- Your own rules. The invented company's rules are in [`../../policy-library/working-time-and-staffing-rules-v1.2.md`](../../policy-library/working-time-and-staffing-rules-v1.2.md). Its working time rules are the company's statement of the rules of an invented country: put your own in their place.

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Control Room, Tools, import the people system from its OpenAPI address. For the invented retailer, that is the document at `/people/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give it an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the 4 operations named in [`agent.yaml`](agent.yaml). Attach nothing else: leave out the operation that publishes a roster.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because a run saves a draft.
8. To let the rostering tool call it, publish the agent and call it through the platform's public API with the roster number. The key and the agent id go in the tool's settings, never in a file. This form is not written yet.

## Test results

Not yet built on a platform. No test has been run.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24, roster week 2026-11-30 to 2026-12-06). The right answers are in the draft rosters section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- `RS-261130-R014`: two breaches. `C-01407` has 10 hours 30 minutes of rest before shift `SH-R014-19` (WT-2), and shift `SH-R014-39` of `C-01409` is 7 hours with no break (WT-4).
- `RS-261130-R047`: two breaches. Shift `SH-R047-46` of the young worker `C-04712` ends at 23:00 (WT-7), and on Sunday no shift manager is on shift from 16:00 to 17:00 (SR-1).
- `RS-261130-S103`: two breaches. `C-10306` is rostered for 49 hours (WT-3), and on Thursday only `C-10301` is on shift at the opening time (SR-2).
- `RS-261130-R022`: no breach.
- `RS-261130-R063` and `RS-261130-S106`: no breach. Each sits exactly on a limit in three places: 11 hours of rest, a shift that ends at 22:00, a week of 48 hours.
- Ask it to move a shift or to publish the roster. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

The manager who owns the roster changes it and publishes it. The agent lists breaches and proposes nothing.
