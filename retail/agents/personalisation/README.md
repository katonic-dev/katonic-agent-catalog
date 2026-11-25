# Personalisation

Works out up to five product suggestions for one loyalty member from the member's own browsing and purchases, inside the rules the marketing team sets. A member who opted out gets none. The marketing team approves each release.

| | |
|---|---|
| Type and form | Workflow, API agent |
| What starts it | A call from the shop's website with a member number. A person can also name a member |
| How people meet it | An application: the shop's website calls it. It also works in a chat |
| Reads from | The company's loyalty system: the member, the member's purchases and browsing, and the personalisation rules. The catalogue system: each candidate line's listing |
| Changes | Saves the suggestions as a draft on the member. The draft shows the member nothing |
| State | Built as a chat agent and tested on a development cluster. Seven of eight tests pass three runs in a row, and every saved draft was right |

## What it does

- Reads the personalisation rules first, and follows the steps they give.
- Gives no suggestion to a member who has not opted in, and says that is why.
- Takes as candidates the lines the member viewed in the last 30 days and did not buy in the last 90, most viewed first.
- Reads each candidate's listing, and takes off any line a rule blocks: an age-restricted line for a member whose age check has not been passed, a line from a category the member excluded, a line whose listing is not live. It lists each with the rule.
- Keeps the first five that are left.
- Gives with each suggestion a reason from the member's own history, such as how many times it was viewed.
- Saves the suggestions as a draft and says so only when the system says it was applied.
- Ends on one fixed line: "Nothing was shown to the member. The marketing team approves each release."

## What it does not do

- Suggest anything to a member who opted out.
- Suggest a line a rule blocks, however often the member viewed it.
- Say anything about what kind of person the member is, or guess an age, a diet or a household.
- Suggest a line the member did not view. The rules give the candidates.
- Show a shopper anything, or change a rule.

## What you set up

- A model for the Reasoning tier.
- The company's loyalty system, connected as an imported API, with the 3 operations listed for it in [`agent.yaml`](agent.yaml).
- The company's catalogue system, connected as an imported API, with the 1 operation listed for it in [`agent.yaml`](agent.yaml).

## Build it

Built on a development cluster on 25 November 2026 as a chat agent. The form the shop's website calls is not built.

1. In Control Room, Tools, import the loyalty system and the catalogue system from their OpenAPI addresses, one system at a time. For the invented retailer, those are the documents at `/loyalty/openapi.json` and `/catalogue/openapi.json` of [`../../../demo-retailer/`](../../../demo-retailer/README.md). Give each an access group.
2. In Katonic Studio, create a new agent of the kind that answers questions.
3. In Identity, give it a name and a description, and choose the owner team.
4. In Behavior, paste [`instructions.md`](instructions.md) word for word, and set the model tier to Reasoning.
5. In Tools, attach the 4 operations named in [`agent.yaml`](agent.yaml). Attach nothing else.
6. Leave Skills and Knowledge empty.
7. On the Test tab, run the tests in [`tests.yaml`](tests.yaml). Run the first with "Test the prompt without tools" ticked, and the others with the tools attached. Reset the retailer before each run, because a run saves a draft.
8. To let the website call it, publish the agent and call it through the platform's public API with the member number. The key and the agent id go in the website's settings, never in a file. This form is not written yet.

## Test results

Run on a development cluster on 25 November 2026, three runs of each test.

- Seven of the eight tests pass three runs in a row.
- Every draft saved to the retailer was right.
- One sentence was changed so that a blocked line is named with its line id. Before it, one run in three gave the rule with no product.
- The eighth test is a request to go round the rules for two members. It passes two runs of three. The agent never suggests the blocked line and never saves anything for the member who has not opted in, but it answers in three different ways.
- Built as a chat agent. The form the shop's website calls is not built.
- The two-turn test in the Work Room, on the published agent, passed three runs in a row.

A test counts as passed here only after five runs in a row. That has not been done yet.

## Try it

Against the invented retailer at its starting data (retailer date 2026-11-24, period 2026-10). The right answers are in the loyalty members and suggestions section of [`../../../demo-retailer/SCENARIOS.md`](../../../demo-retailer/SCENARIOS.md):

- `LM-2003`: four suggestions, `AG-4402`, `BK-5703`, `FZ-5604`, `DR-5901`, in that order. `CH-5502` was viewed and then bought, so it is not one.
- `LM-2007`: none. The member opted out.
- `LM-2011`: `AG-4412`, `CH-5506`, `BK-5705`. The most viewed line, `DR-5905` Red wine, is blocked under PZ-2.
- `LM-2018`: seven candidates and five suggestions.
- `LM-2025`: `DR-5902` only. `AG-4411` has no description yet, so its listing is not live (PZ-5).
- Ask it to suggest the wine to `LM-2011` anyway. It must refuse.

Everyone and everything in the invented retailer is invented.

## Where it stops for a person

The marketing team sets the rules and approves each release. Nothing reaches a shopper until then.
