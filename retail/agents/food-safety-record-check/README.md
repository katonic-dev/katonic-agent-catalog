# Food Safety Record Check

Reads a restaurant's temperature, cleaning and delivery records for a period and lists every reading outside the limits of the company's food safety plan and every entry that is missing, with the plan's section and the dates.

| | |
|---|---|
| Type and form | Workflow, scheduled agent |
| What starts it | A clock: once a month, for the period just ended. The food safety desk can also send one restaurant's case |
| How people meet it | An application: the food safety desk. It also works in a chat |
| Reads from | The company's food safety system (plan, records, review status) and its store and restaurant list |
| Changes | Saves its findings as a draft record check. The draft changes no status |
| State | Written. Not yet built on a platform |

## What it does

- Reads the plan first: each limit, its section, how often it is checked, and the rule that three or more readings outside the limit on the same unit go to the food safety lead (section 6.2).
- Goes through every line of the restaurant's records for the period and lists every reading outside a limit, every check recorded as MISSED and every day with no signed cleaning entry, with dates and times.
- Marks each row as exactly one of: repeated deviation, outside the limit, missing entry, missed check, within the plan. "Repeated deviation" is for three or more readings outside the limit on the same piece of equipment, and for nothing else.
- Treats a chilled delivery that was too warm and was accepted as outside the limit, and says the plan requires such an item to be refused.
- Saves the findings as a draft and says so only when the system says it was applied.
- Ends on one line that starts "Proposed next step:", chosen from three: approve, ask the restaurant manager for corrective actions, or refer to the food safety lead under section 6.2.
- Holds a last section for the food safety desk: when the desk sends the records and the plan in the message, it works from the message, saves nothing and writes the findings in the desk's shape. The Summary carries no count of marks, because the desk counts them from the table.

## What it does not do

- Sign the monthly review, request a corrective action or record one. It has no operation for any of them. A person does.
- Say whether food was safe, or whether it should have been thrown away. The restaurant manager and the food safety lead decide.
- Use a limit from outside the plan.
- Name a person as at fault.
- Guarantee the same marks on every run. The findings are a draft for the food safety lead. Run the tests on your own model before you rely on them.

## What you set up

- A model for the Reasoning tier.
- The company's food safety system and store and restaurant list, each connected as an imported API, with the seven operations listed in [`agent.yaml`](agent.yaml) and no others.
- For the desk route, the food safety desk, which sends the case. It needs the settings-driven case desk engine, and an API key for the desk and the published agent's id.

## Build it

Not yet built on a platform. The steps below are the plan, in general terms. None has been run for this agent.

1. In Control Room, Tools, import the food safety system from its OpenAPI address. For the invented retailer, that is the document at `/foodsafety/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give it an access group.
2. Import the store and restaurant system the same way (`/stores/openapi.json`).
3. In Katonic Studio, create a new agent of the kind that answers questions.
4. In Identity, give it a name and a description, and choose the owner team.
5. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
6. In Tools, attach the five food safety operations and the two store operations named in [`agent.yaml`](agent.yaml). Attach nothing else. Do not attach the operations that sign a review or request corrective actions.
7. Leave Skills and Knowledge empty.
8. On the Test tab, run test 1 with "Test the prompt without tools" ticked. Run the others with the tools attached. Reset the retailer before each run of a test that saves a draft.
9. For the desk route, publish the agent and give its id and an API key to the food safety desk's settings.

## Test results

Not yet built on a platform. No test has been run.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24, period 2026-10). The planted faults are the only ones in the records:

- `R-014`: the make-line chiller above 5.0 °C three times (day 8 afternoon 6.8, day 9 opening 7.4, day 21 afternoon 6.1), so a repeated deviation. Hot holding below 63.0 °C twice. Cleaning not signed on days 5, 17 and 26.
- `R-022`: nothing outside the plan.
- `R-031`: the freezer warmer than -18.0 °C on days 11 and 12. Cleaning not signed on day 19.
- `R-047`: hot holding below 63.0 °C four times, so a repeated deviation.
- `R-058`: the walk-in chiller afternoon check recorded as MISSED on days 6, 7, 13 and 20. Cleaning not signed on day 13.
- `R-063`: a chilled delivery at 6.5 °C on day 13, recorded as accepted.
- Ask it to sign the review for `R-014`. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

The restaurant manager records a corrective action for every deviation, and the food safety lead reviews it. The food safety lead decides whether a unit with three or more readings outside the limit stays in use. A person signs the monthly review.
