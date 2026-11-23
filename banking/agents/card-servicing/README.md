# Card Servicing

For a member of staff on a call about a card. It shows the card's status, recent payments and open disputes, and prepares a block, a replacement or a dispute.

| | |
|---|---|
| Type and form | Conversational, acting agent |
| What starts it | A staff member's request |
| How people meet it | An application: the card servicing screen. It also works in a chat |
| Reads from | The bank's customer records and its card system |
| Changes | A card's status, a replacement request, a dispute. Each one waits for the staff member |
| State | Written. Not yet built on a cluster, and its tests have not been run on a model |

## What it does

- Finds the customer and the card from an id, a name or the last four digits, and asks when more than one customer matches.
- Reads the card, its recent payments, its disputes and the customer's recent contacts before it proposes anything.
- Says exactly what it proposes, with each payment and the total, and asks the staff member to confirm.
- After a change, reports what the system returned: the reference when it was applied, the reason when it was refused.

## What it does not do

- Change anything before the staff member confirms in the conversation.
- Decide whether the customer gets money back, who is liable, or whether a payment was fraud. The disputes team decides.
- Unblock a card, or change a limit, an address or any other customer detail.
- Speak to the customer. It helps the member of staff, who does.
- Guarantee the confirmation step. Waiting for the staff member is an instruction to the model. The control is the platform's approval rule on the three tools that change something: set it before you publish.

## What you set up

- A model for the Reasoning tier.
- The bank's customer records and card system, each connected as an imported API, with the ten operations listed in [`agent.yaml`](agent.yaml).
- An approval rule on `block_card`, `request_card_replacement` and `open_card_dispute`.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the ten tools above and no others.
3. The five tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data:

- `CUS-1002`, Dorian Quillfeather, lost card `CRD-2001` ending 4821. Two payments were made after the loss. He has asked for the card to be stopped and a new one sent.
- `CUS-1003`, Sabine Tarrowgate, card `CRD-2002` ending 7316. It expires within the month and she travels next month.
- `CUS-1004`, Emeric Lowenhall, card `CRD-2003` ending 2059. A dispute for a double charge at a cinema is already open.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

The staff member confirms every block, replacement and dispute before it is requested. Whether the customer gets money back is decided by the disputes team.
