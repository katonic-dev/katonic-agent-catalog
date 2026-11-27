# Litigation Support

For a disputed claim, sorts every document of the set into the insurer's numbered document categories and flags what may be privileged, with the numbered rule of the insurer's privilege guide, for the lawyers. The lawyers decide. The agent never says that a document is privileged, withholds and discloses nothing, and gives no view on the merits of the dispute.

| | |
|---|---|
| Type and form | Autonomous agent: it works through many steps on its own |
| What starts it | A lawyer's or a claims manager's request to sort the documents of a disputed claim |
| How people meet it | Its schedule is sent to the lawyers. There is no desk. It answers in a chat |
| Reads from | The insurer's conduct system: the disputed claim with the people in the matter and every document as text, the document categories and the privilege guide |
| Changes | Saves a draft document schedule. The draft decides nothing about privilege, changes no document and discloses nothing |
| State | Written. Not yet built on a cluster. No test has been run |

## What it does

- Reads the disputed claim and the document guide, then works through every document of the set on its own, in the order of the ids.
- Names a copy as a duplicate of its original, where the system says the two texts are the same. A duplicate carries the category, the flag and the rule of the original.
- Sorts each document into one category by what it is and who it is from and to, not by what it quotes.
- Flags each document yes, no or unclear, with the rule of the privilege guide:
  - **yes**: the guide says it may be privileged. A request for legal advice, the advice, an internal note that passes it on, or a document made for the proceedings.
  - **no**: the ordinary course of the claim, or an ordinary email on which a lawyer is only copied.
  - **unclear**: the guide does not settle it. Legal advice that was sent to a third party, or a note with no date and no author. The row gives the reason and leaves it to the lawyer.
- Reads who asked for a report, and why. A report the claims team asked for to decide the claim is not flagged. A report the lawyers asked for, for the proceedings, is.
- Writes one row for every document, each document once: id, date, author, category, the flag, the rule, a mark and a note of one sentence.
- Says what a document is and does. It does not set out what legal advice says.
- Saves the schedule as a draft, and says it was saved only if the system's reply says so, with the system's own count of rows and documents.
- Ends with one proposal line that names the documents flagged unclear, for the lawyers.

## What it does not do

- Say that a document is or is not privileged. It says "may be", and the lawyers decide.
- Withhold, disclose, send, remove or change a document, or leave one out of the schedule.
- Give a view on the merits of the dispute, on who will win or on what it is worth.
- Give a legal opinion, or carry a lawyer's advice from a document into its reply.
- Guess a flag where the guide does not settle a document.
- Contact the other side, a court, a broker, a witness or anybody else.
- Guarantee the same wording on every run. The schedule is a draft for the lawyers. Run the tests on your own model before you rely on it, and read the saved notes for the wording as well as the replies.

Asked to say who will win or to confirm a flag as final while it sorts a set, it says in one line that it cannot, and still writes the schedule exactly as the documents and the guide give it.

## What you set up

- A model for the Reasoning tier.
- The insurer's conduct system, connected as an imported API, with the three operations listed in [`agent.yaml`](agent.yaml) and no others.

## Build it

This folder is written and has not yet been built on a cluster. The steps will be written here once they have been run. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the three tools above and no others.
3. The reply keeps one shape: a "Summary" heading whose last line starts "Saved:", the heading "Draft document schedule. For the lawyers. Not issued.", one nine-column table with a column called Mark, and a last line that starts "Proposal:". The summary holds no count of marks and is not in the first person.
4. The nine tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`. Send "Sort the documents of disputed claim" and the id.

- `DSP-7401`: a cold store roof, 11 documents. `DSP-7401-D06`, `DSP-7401-D07` and `DSP-7401-D09` are flagged yes. `DSP-7401-D08`, an email to the broker that quotes the lawyers' advice, is unclear under PG-4. `DSP-7401-D10` is a duplicate of `DSP-7401-D03`. `DSP-7401-D11`, an email to finance with the in-house counsel only copied, is not flagged, under PG-3.
- `DSP-7402`: a road accident, 9 documents, proceedings issued. `DSP-7402-D05`, `DSP-7402-D06` and `DSP-7402-D07` are flagged yes: the medical report was asked for by the in-house counsel for the proceedings (PG-2). `DSP-7402-D08`, an email to the repairer with counsel only copied, is not flagged. `DSP-7402-D09` is a duplicate of `DSP-7402-D01`. Nothing is unclear.
- `DSP-7403`: subsidence at a home, 8 documents. `DSP-7403-D06` and `DSP-7403-D08` are flagged yes. `DSP-7403-D07`, a note with no date and no author, is unclear under PG-6, and its date and author stay empty. The surveyor's report, `DSP-7403-D03`, was asked for by the claims team and is not flagged.

Every person, lawyer, law firm and court reference in the invented insurer is invented.

## Where it stops for a person

The lawyers read the schedule and decide what is privileged, what is withheld and what is disclosed. They look first at the documents flagged unclear. Any view on the merits of the dispute is theirs. The agent does none of this.
