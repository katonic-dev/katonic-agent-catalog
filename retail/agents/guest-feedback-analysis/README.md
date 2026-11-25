# Guest Feedback Analysis

Reads a period's guest comments from the company's feedback system, groups them into themes by restaurant, counts them and quotes the comments behind each theme. Comments that describe harm go to the care lead and are never grouped.

| | |
|---|---|
| Type and form | Workflow, scheduled agent |
| What starts it | A clock: once a month, for the period just ended. A person can also name a period |
| How people meet it | Through the company's own system: the analysis is a draft kept in the feedback system and sent to operations |
| Reads from | The company's guest feedback and its restaurant list |
| Changes | Saves its analysis as a draft. The draft changes no comment and no status |
| State | Built and tested on a development cluster. The comments that describe harm are listed first, all seven, in every run. The counts by theme vary from run to run |

## What it does

- Reads every comment for the period, page by page, with its reference, date, restaurant, channel, rating and text.
- Sets aside first every comment that describes illness, an injury, an allergic reaction, a foreign object in food or a legal matter, and lists each one for the care lead. None is grouped or counted in a theme.
- Puts every other comment into exactly one of six themes (late delivery, wrong or missing items, food cold on arrival or at collection, app and payment, praise, other). A new theme is added only when at least five comments fit none of them.
- Counts each theme and each theme by restaurant, names the restaurant with the most, and quotes one comment for each theme with its reference.
- Checks that the theme counts and the set-aside count add up to the number of comments read, and shows that on a "Counts:" line.
- Saves the analysis as a draft and says so only when the system says it was applied.

## What it does not do

- Reply to a guest or draft a reply.
- Rate a restaurant, a manager or a crew member, or name anyone as at fault.
- Decide what to change. Operations staff check the themes and decide.
- Guarantee the same counts on every run. The system holds no theme for a comment, so the agent decides each one by reading. Counts can differ by a few between runs. The seven comments set aside are the part that must not move: check them on every run.

## What you set up

- A model for the Reasoning tier.
- The company's guest feedback and its restaurant list, each connected as an imported API, with the four operations listed in [`agent.yaml`](agent.yaml) and no others.
- A person to read the comments set aside, the care lead. The agent only lists them.

## Build it

Built this way on a development cluster on 24 November 2026.

1. In Control Room, Tools, import the customer care system from its OpenAPI address. For the invented retailer, that is the document at `/care/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give it an access group.
2. Import the store and restaurant system the same way (`/stores/openapi.json`).
3. In Katonic Studio, create a new agent of the kind that answers questions.
4. In Identity, give it a name and a description, and choose the owner team.
5. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
6. In Tools, attach the three care operations and the one stores operation named in [`agent.yaml`](agent.yaml). Attach nothing else.
7. Leave Skills and Knowledge empty.
8. On the Test tab, run test 1 with "Test the prompt without tools" ticked. Run the others with the tools attached. Reset the retailer before each run of a test that saves a draft.
9. To run it once a month, put it in a scheduled workflow that calls it with the period just ended. The schedule has not been tried.

## Test results

Run on a development cluster on 24 November 2026, against the invented retailer at its starting data, three runs of each test.

- Five of the seven tests pass three runs in a row.
- In every run that read the whole month, all seven comments that describe harm were listed first, by the right references.
- The counts by theme vary from run to run. The test on the counts failed one run in three, and the table was not always sorted largest first.
- In the saved draft the list of harm comments was right every time. The counts by restaurant were not reliable.
- Every reply in the Work Room, on the published agent, was delivered.

A model that reads 260 comments does not count them the same way twice. Where the counts matter, build the form with a code step that counts after the model has given each comment its theme. That form is built: see the workflow form below.

## The workflow form

The whole-month analysis is also built as a workflow, where a model gives each comment its theme and a code step checks the labels and counts them. On a development cluster on 25 November 2026 the counts added up in 6 of 6 runs and all seven harm comments were listed in every run. Five runs agreed on every label and a sixth moved three comments, where the counts of the chat form here vary from run to run. The steps, the code and the limits are in [`workflow/README.md`](workflow/README.md).

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24, period 2026-10):

- 260 comments. Seven describe harm or a safety matter and must be listed first, one by one, and left out of every theme.
- The rest fall in six themes. A careful reader lands near: late delivery 78 (most at R-047), wrong or missing items 52 (most at R-014), food cold 41 (most at R-031), app and payment 24, praise 30, other 28.
- The counts by theme, the restaurant with the most in each of the first three themes and the references of the seven comments are in [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md).
- Ask it to reply to a guest and to say which manager is to blame. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

Operations staff check the themes and decide what to change. The care lead reads every comment set aside. The agent names no one as at fault.
