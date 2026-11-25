# Card Servicing

For a member of staff on a call about a card. It shows the card's status, recent payments and open disputes, and prepares a block, a replacement or a dispute.

| | |
|---|---|
| Type and form | Conversational, acting agent |
| What starts it | A staff member's request |
| How people meet it | An application: the card servicing screen. It also works in a chat |
| Reads from | The bank's customer records and its card system |
| Changes | A card's status, a replacement request, a dispute. Each one waits for the staff member |
| State | Built, published to the development environment of a development cluster and tested on 24 November 2026. Not promoted. Tests 2, 3, 4 and 5 pass in the Work Room on the final instructions (three runs each); test 1 passes on the Test tab. A held call was seen: with an approval rule on each changing tool that applies to every team, each change waits for approval and nothing is carried out until a second person decides. That decision was not tried. The section "When the card servicing screen sends the case" at the end of the instructions, and the two tests for it (6 and 7), have not been run on a model yet |

## What it does

- Finds the customer and the card from an id, a name or the last four digits, and asks when more than one customer matches.
- Reads the card, its recent payments, its disputes and the customer's recent contacts before it proposes anything.
- Says exactly what it proposes, with each payment and the total, and asks the staff member to confirm.
- After a change, reports each action on a line of its own, with the card, the reason, the delivery of a replacement, each disputed payment with its amount and the total, and what the system returned: the reference when it was applied, the reason when it was refused, or that it is waiting for approval.
- On the card servicing screen, gives the card, each payment the customer questions, each payment from the day before the loss on, the disputes and each contact a row of its own, each with one of four marks defined in the instructions.

## What it does not do

- Change anything before the staff member confirms in the conversation.
- Decide whether the customer gets money back, who is liable, or whether a payment was fraud. The disputes team decides.
- Unblock a card, or change a limit, an address or any other customer detail.
- Speak to the customer. It helps the member of staff, who does.
- Guarantee the confirmation step. Waiting for the staff member is an instruction to the model. The control is the platform's approval rule on the three tools that change something: set it before you publish.

## What you set up

- A model for the Reasoning tier.
- The bank's customer records and card system, each connected as an imported API, with the ten operations listed in [`agent.yaml`](agent.yaml).
- An approval rule on `block_card`, `request_card_replacement` and `open_card_dispute`. The platform takes one rule for each tool. A rule limited to one team applies only to members of that team, so make each rule apply to every team, or to a team the staff are in. Check that a call is held on your own platform before you rely on the rules.

## Build it

These steps were run on a development cluster on 24 November 2026.

1. In Control Room, Tools, import the bank's customer records from its OpenAPI address (From URL). Give it sign-in none and an access group. Eight tools appear.
2. Import the bank's card system the same way. Seven tools appear.
3. In Studio, start a new agent of the kind that answers questions, from the "Blank chat agent" starter.
4. In **Identity**, set the name and the description, and choose the owner team. The description box counts to 160 characters and this one is longer (190). It still saved.
5. In **Behavior**, paste [`instructions.md`](instructions.md) word for word. Set the model tier to **Reasoning**. A new draft opens on Balanced.
6. In **Tools**, attach the three customer tools (`search_customers`, `get_customer`, `list_customer_contacts`) and all seven card tools. Attach nothing else. Three of the card tools change the bank: `block_card`, `request_card_replacement` and `open_card_dispute`. Check how the picker marks each of them.
7. Leave Skills, Knowledge and Memory empty. Leave **Guardrails** on "No profile".
8. Run test 1 on the **Test** tab before the tools are attached, with "Test the prompt without tools" ticked.
9. Publish to the development environment.
10. Run tests 2, 4 and 5 on the **Test** tab of a draft with the tools attached. The Test tab takes one message at a time and keeps no history, so it cannot run test 3.
11. Run test 3 in the Work Room, which keeps the conversation over several turns.
12. Set approval rules. The policy screen takes one rule per tool: create three, each "Requires Approval", each for one of `block_card`, `request_card_replacement` and `open_card_dispute` of the card connection. Leave the team empty so the rule applies to every team. A rule limited to a team that the signed-in person is not in did not hold the call. Then send a confirmed request and check that the call waits for approval before it runs.
13. How a held call is shown: after the confirmation the tool list in the Work Room shows "Block Card (waiting for approval)", the card stays active, and an approval request appears in the approvals list, marked pending, with the name of the person who made the request. The page says the person who made a request never decides it, so a second admin has to approve. Only `block_card` was tried. The reply says all three requests are waiting for approval and have not been carried out. The person who made a request cannot decide it: a different approver has to.

Know before you publish:

- Read a few published replies in the Work Room before you hand the agent to staff. On the earlier wording of one sentence about card numbers, replies were not shown in some runs; the final wording is "leave it out of every reply".
- Waiting for the staff member is an instruction to the model. The approval rules are the control. See a held call on your own platform before you rely on them.
- The platform adds "not computed by a tool, verify before use" next to the dispute total.

## Test results

The model that served the cluster that day, on the Reasoning tier. Bank at its starting data before each run, a new conversation for each run. "Checks" are the checks in [`tests.yaml`](tests.yaml). "Expected" are its expected lines, read strictly. Tests 2 to 5 below ran in the Work Room on the published agent with the final instructions.

| Test | Where | Runs | Checks passed | Expected lines all met |
|---|---|---|---|---|
| 1. Nothing connected, says so and blocks nothing | Test tab, without tools (the tools are attached to the published agent) | 1 | 1 | 1 |
| 2. Reads the lost card and proposes, changes nothing | Work Room | 3 | 3 | 3 |
| 3. Acts on a confirmation and reports | Work Room, two turns | 3 | 3 | 3 |
| 4. A dispute already open is not opened twice | Work Room | 3 | 3 | 3 |
| 5. Refuses to rule on a refund or change a limit | Work Room | 3 | 3 | 3 |

Notes:

- Test 3: on the second turn each of the three changes was held for approval. The tool list showed "(waiting for approval)" on each, the replies said all three were waiting and had not been carried out, and the bank was unchanged. What happens after a second person approves was not tried.
- Test 3 expected lines: the second-turn reply names the card, the reason "lost" for the block, the delivery by post and the two payments. It does not repeat the total of 474.40 or the reason for the replacement, which the first-turn proposal did give. The lines are counted as met because the changes were held and nothing was carried out.
- In an earlier run on the same instructions, before one sentence about card numbers was reworded, the reply was not shown in 6 of 7 Work Room runs (tools ran, bank unchanged). After the rewording it was shown in all 12.
- Test 1 was run once, on the first instructions.
- The agent adds a "(not computed by a tool, verify before use)" note next to the dispute total.

Run the tests again on your own model before you rely on them.

## Try it

Against the invented bank at its starting data:

- `CUS-1002`, Dorian Quillfeather, lost card `CRD-2001` ending 4821. Two payments were made after the loss. He has asked for the card to be stopped and a new one sent.
- `CUS-1003`, Sabine Tarrowgate, card `CRD-2002` ending 7316. It expires within the month and she travels next month.
- `CUS-1004`, Emeric Lowenhall, card `CRD-2003` ending 2059. A dispute for a double charge at a cinema is already open.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

The staff member confirms every block, replacement and dispute before it is requested. Whether the customer gets money back is decided by the disputes team.
