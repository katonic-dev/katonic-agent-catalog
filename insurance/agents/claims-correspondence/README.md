# Claims Correspondence

Drafts the letter to the claimant from the claim file and the insurer's own letter templates. A claims handler reads and sends every letter.

| | |
|---|---|
| Type and form | Conversational, acting agent |
| What starts it | A handler's request |
| How people meet it | An application: the Claims assessment desk. It also works in a chat |
| Reads from | The insurer's claims system (the claim with its whole file, the claims handling guide, the letter templates) and its policy system (the words of a clause) |
| Changes | Saves the letter as a draft, with its language. The draft sends nothing and changes no status |
| State | Written. Not yet built on a cluster |

## What it does

- Writes one of three letters, each from the insurer's own template: an acknowledgement of a claim, a request for missing documents, or a decline of a claim.
- Takes every part of the letter from the records: the claim, the checklist of documents for the claim type, the adjuster's decision, the policy wording, the handling guide and the template.
- Works to rule HG-6 of the claims handling guide. Every letter names the claim by its id. No letter carries a policy number, a bank account or an identity number. A decline letter is written only when an adjuster's decision to decline is recorded on the claim, and it gives the adjuster's reason and the clause as the decision records them.
- Puts the template's closing paragraph into the letter word for word.
- Writes the letter in the language the handler asks for, English when none is asked for. In another language the claim id, the clause number and the digits stay as they are, and the summary, the table and the proposal stay in English.
- Checks the letter against the template's list of what it must include: one row for each item, with where it comes from and a mark, included or cannot include.
- Saves the letter as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: approve the letter, or refer to a handler with what could not be included and why.

## What it does not do

- Send a letter or contact the claimant. A claims handler reads and sends every letter.
- Decline a claim, accept cover or give a view on either. The adjuster decides.
- Write a decline letter where no decision to decline is recorded. It says why, cites rule HG-6 and writes nothing.
- Write a letter that offers a settlement. There is no template for one here.
- Fill a gap. Where the records do not give something the letter must include, it leaves it out, says so and refers the letter to a handler.
- Guarantee a translation. A letter in another language is a draft: a person who reads the language reads it before it is sent.

## What you set up

- A model for the Reasoning tier.
- The insurer's claims system and its policy system, each connected as an imported API, with the five operations listed in [`agent.yaml`](agent.yaml) and no others.
- The Claims assessment desk, which sends the handler's request, if you want to meet the agent through a screen. The agent also works in a chat.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the five tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft letter check. For the claims handler. Not issued.", a five-column table, the letter under the heading "Letter. Not sent.", and a last line that starts "Proposal:".
4. The nine tests are in [`tests.yaml`](tests.yaml).

Two things to know before the first build:

- The agent reads the words of a clause from the policy wording, and it finds the wording by the id the claim record gives.
- The team in an acknowledgement is the handling team the claim record names, and nothing else. Where the record names none, the letter is written without a team, the item is marked cannot include and the letter is referred to a handler.

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`.

- "Draft the acknowledgement letter for claim CLM-4004." The letter names the claim, the date it was reported (19 November 2026), what it is for, the theft team, and says that we will write again within 10 working days.
- "Draft the acknowledgement letter for claim CLM-4001." The claim record names no handling team yet, so the letter has none and the proposal refers to a handler.
- "Draft the letter that asks for the missing documents on claim CLM-4002." The letter asks for the plumber's report and for photographs that can be read, with the reason for each.
- "Draft the decline letter for claim CLM-4010." An adjuster declined the claim on 20 Nov 2026 under clause 2.2. The letter gives the adjuster's reason, clause 2.2 in its own words, and the paragraph on how to complain word for word.
- "Draft the decline letter for claim CLM-4006." No decision to decline is recorded, so no letter is written (rule HG-6).
- "Draft the decline letter for claim CLM-4010 in Arabic." The same letter in Arabic, saved with its language.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

A claims handler reads the draft, changes it if needed and sends it. An adjuster decides whether a claim is declined. The agent sends nothing and decides nothing.
