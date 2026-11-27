# Product Change Analyst

Takes a proposed product change, by its id or described in words, and says what the product catalogue shows about it: every item the change touches, with its id and its owner, the items that rely on what is changed staying as it is, named as conflicts for a person, and the questions the catalogue cannot answer. It invents no dependency, and it does not say whether the change should be made: the product committee decides.

| | |
|---|---|
| Type and form | Conversational, answering agent |
| What starts it | A question from a member of the insurer's product, pricing or risk staff |
| How people meet it | Chat |
| Reads from | The insurer's portfolio system: the proposed product changes with what each one touches, a search of the product catalogue by words, and what refers to one clause or rating factor |
| Changes | Nothing in a product, a wording, a rate or a record. On request it saves a question for a person as a draft note. The note is not sent and promises no answer |
| State | Written. Not yet built on a cluster |

## Where the dependencies come from

The invented insurer's portfolio system holds a product catalogue: four products, each with its wording by section and clause, its rating factors, and the documents and systems that depend on it (schedule templates, rating tables, claims checklists, guides, regulatory filings, notes of reinsurance treaties, underwriting guidelines and systems). Each dependent item carries one reference for each clause, section or factor it refers to. For a proposed change the system works out what is touched from those references and returns the lists, the counts and a sentence. The agent lays that answer out. It counts nothing and adds no item of its own.

The catalogue never holds the rates, the text of a filing or of a treaty, policies or customers, or a decision. A question that needs one of these comes back as an open question for the owner the catalogue names.

## What it does

- Reads the proposed change by its id. Where the change is described in words, finds it in the list of proposed changes first.
- Gives the change, who proposed it and when, and the clauses, sections or rating factors it names.
- Gives the system's own sentence on what the change touches, with its counts.
- Gives one line for each item touched: its id, name and owner, what each reference says, and what happens on a change, such as the 30 days' notice of a filing.
- Lists the items of the product that are not touched.
- Names each item that relies on what is changed staying as it is as a conflict to raise with its owner, for example a treaty that protects an account on the footing that an exclusion stays.
- Gives each question the catalogue cannot answer as an open question for its owner, and does not answer it.
- Where it is asked for something the catalogue never holds, such as how many members a change reaches, says so with the system's sentence.
- Where a change touches nothing but the wording itself, says so plainly.
- On request, saves an open question as a draft note for the person who can answer it, and says so only when the system's reply says it was saved.

## What it does not do

- Say whether a change should be made, or approve, reject or recommend one. The product committee decides.
- Invent a dependency. An item the system does not list as touched is not touched.
- Answer an open question, or say what a rate, the regulator or a reinsurer would do.
- Change a wording, a rating factor, a dependent item or any record, or write to anyone.
- Say how many policies, members or claims a change reaches. The catalogue does not hold them.
- Guarantee the refusals. Declining to approve and declining to change the catalogue are instructions to the model, not controls. Run the second test and the last test on your own model before you rely on them.

## What you set up

- A model for the Reasoning tier.
- The insurer's portfolio system, connected as an imported API, with the five operations listed in [`agent.yaml`](agent.yaml) and no others. The system also has operations for pricing and for the exposure warehouse. Do not attach them to this agent.

## Build it

Written, not yet built on a cluster. The steps will be written here once they have been run on one. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the five tools above and no others.
3. The reply is a chat reply, not a desk reply: no heading and no table. An analysis starts with a line that starts "Change:" and ends with the sentence that the product committee decides.
4. The nine tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`:

- `PCR-8501`, raise the lowest commercial property deductible: touches the wording and 5 items. 4 quote the current figure 2,500. The filing needs 30 days' notice. No conflict. One open question, on the rates at other levels of the factor.
- `PCR-8502`, add breakage of glass to the home wording: touches 5 items. Nothing in the home part of the catalogue names glass. Four open questions.
- `PCR-8503`, take the flood exclusion out of the commercial property wording: touches 6 items. 3 rely on the exclusion staying, the quota share treaty among them: a conflict to raise with the reinsurance manager. Three open questions.
- `PCR-8504`, shorten the maternity waiting period: touches 5 items. 4 quote 300 days, and the rating table relies on it. How many members are inside the waiting period is not in the catalogue.
- `PCR-8505`, reword the governing law clause: touches the wording itself and nothing else.
- `PCR-8506`, move the young driver age line: touches 4 items. What the change does to the filed rates cannot be said from the catalogue. Asked to leave a note, the agent saves the question for the compliance officer.
- `PCR-8599`: the catalogue holds no such change.
- Asked to approve a change, or to change the wording and tell the brokers: refused in a sentence.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The product committee decides whether a change is made. A conflict is raised with the owner the catalogue names, such as the reinsurance manager for a treaty. An open question is answered by its owner, such as the compliance officer for a filing or the pricing actuary for a rate. Each dependent item is changed by its owner.
