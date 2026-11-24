# Fraud Case Summary

Gathers the facts on a flagged card payment or payment and drafts the case summary, the recommended action and a message to the customer.

| | |
|---|---|
| Type and form | Workflow, event-triggered agent |
| What starts it | A flagged card payment or payment arriving at the bank. The bank's fraud system can announce one through its event for new fraud cases |
| How people meet it | An application: the Fraud desk |
| Reads from | The bank's fraud system, cards system and payments system: the case, the rule, the card's payments and the payments |
| Changes | Saves a draft summary, a recommended action and a message to the customer. The case stays open and nothing is sent |
| State | Written, not yet built. The instructions and tests have not been run on a model |

## What it does

- Reads the case, the flagged payments, the channel and device details, the security events, the customer's earlier contacts, the notes and the earlier cases.
- Reads the rule that flagged the case, and the card's other payments or the customer's other payments. Every card payment shows its country, its town and whether the card was present, so the agent can say whether the card's earlier payments were all at home.
- Writes one row for each fact with its record id, in the order the analyst reads the case: the rule, the card's usual payments together in one row (one line to each payment), the flagged payments (each in a row of its own), how they were made, the security events, what the customer said, the notes and the earlier cases. A payment row gives When, Amount, Where and Card on lines of their own.
- Marks each row points to fraud, points away from fraud, not known or background. It writes no count of marks: the desk counts them.
- Keeps what the bank recorded apart from what the customer said. A statement starts "Customer says:" and is the customer's account.
- Writes the account for the case file ("What the records show") and the message to the customer as two sections of their own. Dates are written like 22 Nov 2026, 02:14, never as a count of days.
- Looks as hard for facts that point away from fraud as for those that point to it.
- Drafts a message to the customer, as a short letter in the bank's own voice, that accuses no one and claims no action has been taken.
- Ends with one recommendation line: block, release or refund, as a next step for the analyst, and why.

## What it does not do

- Block a card, cancel or release a payment, refund or recall money, or decide a case. The fraud analyst decides.
- Send anything to the customer, open a dispute or request a replacement card.
- Call a customer a fraudster or a liar. It shows the statement beside the records.
- Fill a gap or assume where a payment was made or whether the card was present.
- Guarantee the same marks on every run. The draft is for the fraud analyst. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's fraud system, cards system and payments system, connected as imported APIs, with the six operations listed in [`agent.yaml`](agent.yaml) and no others.
- The [Fraud desk](../../desks/fraud/README.md), which sends the case, if you want to meet the agent through a screen. It needs the case desk engine that reads `DESK_CONFIG`. The agent also answers in a chat.
- An API key with the Chat scope for the desk, and the published agent's id.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft case summary. For the fraud analyst. Not decided.", a seven-column table (# | Fact | Record | What it shows | Found at | Mark | Note), and a last line that starts "Recommendation:". Change the instructions and the desk's `draft.instruction` together.
4. The tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data, started with BANK_TODAY=2026-11-24:

- `FRD-3001`: card fraud. Three online purchases, card not present, in Norvania at 02:14, 02:31 and 03:05, total USD 2,219.90, on a card whose earlier payments were all chip payments in Meridia. Two calls from home. Refund, which also blocks the card.
- `FRD-3002`: a genuine payment. USD 18,500 to Brookhaven Joinery Works, held. He confirmed it on a call-back and had asked about a builder's deposit. Release.
- `FRD-3003`: account takeover. A new device, a password reset, a new payee and a payment of USD 7,400 within 39 minutes, from another country. Refund, which recalls the payment and blocks online banking.
- `FRD-3004`: a forgotten subscription. USD 11.99 to Streamline Video Club, with three earlier identical payments, all online in Port Ilvane. Release, and it belongs with disputes in the cards system.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

The fraud analyst reads the summary and decides to block, release or refund, in the fraud system, under their own name. The agent sends nothing to the customer.
