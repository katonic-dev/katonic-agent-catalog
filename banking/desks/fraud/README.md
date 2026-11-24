# Fraud desk

The settings folder that turns the Katonic case desk into a desk for a bank's fraud analyst. A card payment or a payment is flagged. The Fraud Case Summary agent gathers the flagged payments, the customer's usual pattern, where and how each payment was made (country, town, card present or not), what the customer has told the bank and any earlier case, and writes a summary for the analyst: what points to fraud, what points away from it and what is not known. The analyst decides. The agent blocks nothing, refunds nothing and never says that a payment is fraud: it says what the records show.

Meridian Trust Bank (an invented bank in the invented country Meridia), its customers, its cards and its fraud cases are invented. Nothing here is a real fraud decision.

## What the person sees

- **A queue of fraud cases.** Each title leads with who and what ("Marguerite Oakhaven, online purchases abroad"). The line under it starts with the case id: "FRD-3001 · USD 2,219.90 at risk".
- **The case beside the review.** The desk's short account of the case is on the left (on a phone it is folded under a heading, so the review is what the reader sees first). The agent's draft is on the right.
- **The proposal first.** The agent's next step for the analyst is the first thing in the review, in large type, with the reason, the desk's own count of the marks and the four decision buttons. The button the agent names is marked "Agent's proposal".
- **One row for each fact, in the order the analyst reads the case:** the rule that flagged it, the card's usual payments together in one row (one line to each payment, oldest first, one note), the flagged payments (each in a row of its own), how they were made, the security events in time order, what the customer said, the notes, the earlier cases. A flagged payment row gives its When, Amount, Where and Card on lines of their own, so time, amount, place and whether the card was present can be compared down the rows.
- **The bank's records and the customer's account kept apart.** What the customer said starts "Customer says:" and its "Found at" line says that the words are the customer's. Where one contact holds both, the row has a "Bank" line (for example, the customer passed the security questions) and a "Customer" line.
- **Two cards of their own**, set as documents: "What the records show" (the account for the case file, every sentence resting on record ids) and "Message to the customer" (a short letter, not sent).
- **The register** afterwards: who decided what, when, on which version of the summary, with which agent run and tool calls.

A card is shown by its last four digits only. Every date is written like 22 Nov 2026, 02:14, and never as a count of days.

### The marks

None of the marks is a pass or a failure. A fact that points to fraud is the one that stands out.

| Mark | Sign and tone | Meaning |
|---|---|---|
| Points to fraud | ▲ red | The record fits a fraud pattern, or it is the customer's statement that a payment is not theirs. It proves nothing by itself |
| Points away from fraud | ▽ in the brand colour | The record fits a payment the customer made or agreed to. It does not close the case |
| Not known | ? amber | A statement or a record that the other records do not settle |
| Background | • grey | The rule that flagged the case, the card's usual payments, a note that adds nothing, an earlier case. It points neither way |

## What the person decides

| Button | What it records |
|---|---|
| Fraud: block | Fraud confirmed: stop the card, or the held payment. Needs a reason |
| Fraud: refund | Fraud confirmed and the money returned: a card payment is refunded and a sent payment is recalled, which asks the receiving bank and does not guarantee the money back. Needs a reason |
| Not fraud: release | Not fraud: release a held payment, or close the case. Needs a reason |
| Not fraud: send to disputes | Not fraud, but the customer disputes the charge, for example a subscription the customer forgot. A person opens the dispute in the cards system. Needs a reason |
| Ask the agent to redo the summary | A note that the agent sees. The agent drafts again as a new version |

The desk blocks, releases and refunds nothing. The analyst decides the case in the bank's fraud system, under their own name. The agent saves only a draft summary, and the case stays open. The person who entered a case cannot decide it.

## The four demo cases

The dates below are those of the bank at the bank date 24 Nov 2026. **Start the bank with `BANK_TODAY=2026-11-24`** so that its records agree with the desk's cases and replies. They were worked out from the bank's data with a script. With another bank date the bank's dates move and the desk's cases no longer match them.

| Case | What the agent should find | Recommendation |
|---|---|---|
| FRD-3001, Marguerite Oakhaven (CUS-1012), card CRD-2008 (ending 5527) | Three online purchases, card not present, in Norvania (Silverkeld, Norvik, Kaldmoor) on 22 Nov 2026 at 02:14, 02:31 and 03:05 (CTX-2008-F01 to CTX-2008-F03), USD 2,219.90 in all. The card's four earlier payments (23 Oct 2026 to 19 Nov 2026, CTX-2008-029 to CTX-2008-032) are chip payments, card present, all in Meridia (Port Ilvane, Tallowby, Marlow Reach). Two calls from her home number: CNT-5201 on 21 Nov 2026 at 22:40 and CNT-5202 on 22 Nov 2026 at 07:15 | Refund, which also blocks the card. Offer a replacement card |
| FRD-3002, Leopold Fenwick-Aral (CUS-1015), PAY-6401 | USD 18,500 to Brookhaven Joinery Works on 23 Nov 2026, held. CNT-5204 (23 Nov 2026) is a call-back in which he passed the security questions and confirmed the payee and the amount. CNT-5203 (4 Nov 2026) shows he asked how to pay a builder's deposit. The earlier case FRD-2902 (28 Jan 2026) was released on 29 Jan 2026 | Release |
| FRD-3003, Rosalind Heathcote-Brae (CUS-1014), PAY-6402 | USD 7,400 to Marrowfield Remittance Agents in Aldoria. On 23 Nov 2026 a new device at 10:02, a password reset at 10:09, a payee added at 10:15 and the payment at 10:41, 39 minutes after the first event. The sign-in came from Brevnia. She has never paid anyone outside Meridia (CNT-5205, 25 Sep 2026) | Refund, which recalls the payment and blocks online banking |
| FRD-3004, Oskar Brindlemoor (CUS-1006), card CRD-2006 (ending 6670) | USD 11.99 to Streamline Video Club on 22 Nov 2026 (CTX-2006-S04). The card's own list shows three earlier payments of 11.99 to the same merchant on 24 Aug 2026, 23 Sep 2026 and 23 Oct 2026 (CTX-2006-S01 to CTX-2006-S03), all at 03:10, all online, card not present, in Port Ilvane. A subscription the customer forgot | Release. It belongs with disputes in the cards system |

## Which engine it needs

It needs the case desk engine ([katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk)) in a version that reads `DESK_CONFIG`, the `case`, `closedStatuses` and `draft.marks` settings, and the settings this desk uses: the sections of the draft shown as cards, a sign and a tone for each mark (`markIcons`, `markTones`), the proposal first (`proposalFirst`), the tally words, words round the amount (`shownAs`), the case text folded on a phone (`foldOnPhone`), the label of the last line of a row ("Note"), and labelled lines in a row (`<br>`).

**That version of the engine is not published yet.** The engine on GitHub today can only be the regulatory change desk and will not run this folder. This page will name the version once it is out.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm install
DESK_CONFIG=../katonic-agent-catalog/banking/desks/fraud/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
KATONIC_AGENT_ID=<id of Fraud Case Summary> \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json`. Without it the engine is the regulatory change desk |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `KATONIC_AGENT_ID` | The agent the desk calls: Fraud Case Summary. `DESK_AGENT_ID` does the same and wins over it. A file cannot override it |
| `DESK_ENV_FILE` | A settings file to read in place of `.env`, for the platform address, key and agent id, when several desks share one |
| `SEED_DEMO` | `true` loads the four demo cases on the first start |
| `DATA_DIR` | A folder for the desk's records, so they outlive a restart |
| `DATABASE_URL` | Keeps the records in PostgreSQL instead of a file |
| `INTAKE_TOKEN` | Turns on intake by webhook. The sender gives it as `X-Intake-Token` |
| `LOCAL_USER`, `LOCAL_USER_NAME` | The analyst's name when the desk does not trust sign-in headers. Every register row says which it was |
| `TRUST_SIGN_IN_HEADERS` | `true` only where nothing can reach the desk except through the platform's sign-in |
| `PORT`, `PUBLIC_URL` | The port the desk listens on, and its public address when it sits behind a prefix |
| `KATONIC_MAX_MESSAGE_CHARS` | The longest message the desk sends. The default is 15,000 characters |
| `DESK_LIBRARY_DIR`, `KATONIC_LIBRARY_NAME` | Not used. This desk has no library: the agent reads the bank's fraud, cards and payments systems |

When the agent reads the invented bank, start the bank with `BANK_TODAY=2026-11-24`. The four demo cases, their dates and the canned replies are written for that bank date.

Build the agent from [`fraud-case-summary`](../../agents/fraud-case-summary/README.md). Its `instructions.md` and the `draft.instruction` setting in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine's stand-in platform answers from this folder's `demo-replies.json`, one canned reply for each demo case, keyed by the case id in the case title, and a plain default for any other case. Each follows the right answers in the invented bank's scenario list, and each says that it comes from the stand-in and that nothing was saved. Start it with the same `DESK_CONFIG`:

```bash
DESK_CONFIG=../katonic-agent-catalog/banking/desks/fraud/desk.config.json node demo/fake-platform.js
```

Then start the desk with `KATONIC_BASE_URL` pointing at the stand-in, and any value for `KATONIC_API_KEY` and `KATONIC_AGENT_ID`. The stand-in shows the screens and the marks. It is not an agent, and it reads nothing from the bank.

## How a case reaches the desk

A member of the fraud team enters it, or the bank's fraud system sends it to `POST /api/intake` with the intake token. The bank's own event for a new fraud case carries a message and an id, not the desk's fields, so a small adapter between the two is needed. It is not written here.

## How it was tested

On 24 November 2026 the desk was run against the stand-in through 12 scenarios in a headless browser, on the stand-in port 8404, a recording proxy on 8414 and the desk on 3418: the four demo cases with every row, the mark on each row (sign and tone), the record id and the date, time, amount, place and card-present lines of each payment row checked against the invented bank's scenario list and its data at the bank date 24 Nov 2026; the usual payments in one row and the flagged ones each in a row of their own, in time order, with the values lined up down the rows; the titles (who and what) and the line under them (the case id and the amount at risk); every customer statement marked as the customer's account; the proposal and the button it marks; the two cards (the account for the case file and the letter to the customer); no count of marks written by the agent, no date as 2026-11-22 and no "days ago", cards by their last four digits; what the desk sent to the agent (one agent, the desk's own instruction); a question to the agent; a redo with a note and an edit of the text (each a new version); every decision (refund after an edit, release, block, send to disputes, redo); a decision without a note and a decision the desk does not have (both refused); the register and its export; filters and search by case id, customer name, customer id, card id and a double-barrelled surname; a new case entered by hand (an invalid form, a valid one and the stand-in's plain default reply, then a removal); the three themes; a phone-width window at 390 and 360 (the queue folds, the jump bar works, every control is 40 px or taller); and a reload. All 12 passed (270 checks) after the fixes the first run and the design review called for. It was reviewed screen by screen for visual design at desktop and phone width, in light and dark.

Not yet done: a run against a real agent on a platform. The wording a real agent gives to the four marks, the labelled lines of a payment row, the dates and the recommendation line is asked for in `instructions.md` and has not been tried on a model.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the drafting instruction |
| `cases.json` | The four demo cases, written for the bank date 24 Nov 2026 |
| `demo-replies.json` | The stand-in's canned reply for each demo case, and a plain default for any other case |
