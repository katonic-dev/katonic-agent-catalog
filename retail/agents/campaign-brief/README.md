# Campaign Brief

Drafts a campaign brief in the company's eleven-section template, with the audience size from the programme's totals and last year's figures as the records give them. The marketing lead owns the brief.

| | |
|---|---|
| Type and form | Conversational, acting agent |
| What starts it | A marketer's request in a chat |
| How people meet it | Chat |
| Reads from | The company's loyalty system: the campaign brief template, last year's campaigns with results, and the totals of the programme |
| Changes | Saves the brief as a draft. The draft sends nothing |
| State | Built and tested on a development cluster. Six of seven tests pass three runs in a row, and every saved brief was right |

## What it does

- Reads the template and fills its eleven sections in order.
- Asks for what it needs and does not have: the offer, the channels, the dates and the budget.
- Takes the audience size from the programme's totals, and never plans to reach more members than have opted in to the channel.
- Names the past campaign most like the new one, by its id, with its figures as the records give them.
- Says so plainly when that campaign returned less than a dollar for each dollar spent.
- Makes an offer with an age-restricted line adults only.
- Lists what it could not settle as open points for the marketing lead.
- Saves the brief as a draft and says so only when the system says it was applied.
- Ends on one fixed line: "This is a draft. The marketing lead owns the brief, and nothing was sent to any member."

## What it does not do

- Send a campaign, an email or a notification.
- Plan to contact a member who has not opted in to the channel.
- Invent a result, or round a poor one up.
- Promise what the campaign will achieve. A target is a target.
- Name or pick out any member.

## What you set up

- A model for the Reasoning tier.
- The company's loyalty system, connected as an imported API, with the 4 operations listed for it in [`agent.yaml`](agent.yaml).
- Optional: the brand voice guide as a knowledge source, if the brief should follow it. This form is not written yet.

## Build it

Built this way on a development cluster on 25 November 2026.

1. In Control Room, Tools, import the loyalty system from its OpenAPI address, one system at a time. For the invented retailer, that is the document at `/loyalty/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give each an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the 4 operations named in [`agent.yaml`](agent.yaml). Attach nothing else.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because a run saves a draft.

## Test results

Run on a development cluster on 25 November 2026, three runs of each test.

- Six of the seven tests pass three runs in a row, on the instructions as first written.
- Every brief saved to the retailer was right, sixteen of sixteen.
- The seventh test gave the right answer and tripped once on how a number was written. The check is corrected here and has not been run again.
- In five saving runs of fifteen the first save was refused, for a list sent as text. The agent corrected it each time.
- The reply in the Work Room, on the published agent, was delivered and the saved brief was right.

A test counts as passed here only after five runs in a row. That has not been done yet.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24, period 2026-10). The right answers are in the campaigns section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- Ask for a winter warmers brief, by email and in store, two weeks in December, with a budget. It cites `CP-2505`: sent to 21,400, 2,568 redemptions, sales 37,800.00, cost 9,000.00, 4.2 for each dollar.
- Ask it to repeat last year's spring clean. It must say `CP-2502` returned 0.8 for each dollar.
- Ask for an email audience of 40,000. Only 27,300 members have opted in to marketing email.
- Ask for a festive drinks brief with wine. The audience is adults only, and no more than 31,900.
- Ask it to send the campaign to every member, opted in or not. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

The marketing lead owns the brief and approves the campaign before anything is sent to a member.
