# Regulatory Monitoring

Reads the publications of the regulators the insurer names. For each publication it says whether it bears on the insurer and maps it to the numbered obligations of the obligations register, with the owner of each. The regulatory change owner decides. The agent gives no legal opinion, changes nothing in the register and never answers a regulator.

| | |
|---|---|
| Type and form | Workflow, scheduled |
| What starts it | A schedule, each working day. Here it is built as a chat agent and a person or the desk sends the message; a clock has not started it |
| How people meet it | An application: the Regulatory change desk. It also answers in a chat |
| Reads from | The insurer's conduct system: the publications feed with the dates of each item, the regulators the insurer names, the lines of business it writes, and the obligations register with the owner of each obligation |
| Changes | Saves one impact note for each publication as a draft. The draft changes no obligation and reports nothing to a regulator |
| State | Written. Not yet built on a cluster. No test has been run |

## What it does

- Takes one of two requests: one publication by its id ("Write the impact note for publication PUB-7301."), or the feed ("Go through the new publications in the feed."). Where the message names a regulator, it takes only that regulator's items.
- Reads the publication, the whole feed with the items noted earlier, and the obligations register.
- Gives each publication one finding, with a mark:
  - **bears on**: it changes, sets or restates what an obligation says. The row sets what the register says now beside what the publication says, with the owner.
  - **consultation only**: a proposal. The note says that it is not a rule yet and that nothing changes now, and names the obligation it would bear on.
  - **does not apply**: it is only for a line of business the insurer does not write. The note gives the reason and names no obligation.
  - **duplicate**: it repeats an earlier item under a new reference. The note names the earlier item and says nothing is new.
  - **no matching obligation**: it applies and the register is silent. The note says so and sends the point to compliance. No match is forced.
- Maps an amendment only to the obligation it changes, and names the earlier item it amends.
- Uses the system's own sentence for every date and every count of days. The agent counts nothing.
- Saves each note as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line for the regulatory change owner.

## What it does not do

- Give an opinion on the law, or say whether the insurer meets a rule.
- Change, add or remove an obligation in the register.
- Answer, report to or contact a regulator, or tell the owner of an obligation.
- Force a match where no obligation covers a publication.
- Treat a consultation as a rule.
- Guarantee the same wording on every run. A note is a draft for the regulatory change owner. Run the tests on your own model before you rely on it.

Asked to tell a regulator something or to change the register while it writes a note, it says in one line that it cannot, and still writes the note exactly as the publication and the register give it.

## What you set up

- A model for the Reasoning tier.
- The insurer's conduct system, connected as an imported API, with the four operations listed in [`agent.yaml`](agent.yaml) and no others.
- The Regulatory change desk, which sends the publication's id, if you want to meet the agent through a screen.
- For the scheduled use, a clock that sends the message each working day. This has not been set up or tried.

## Build it

This folder is written and has not yet been built on a cluster. The steps will be written here once they have been run. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the four tools above and no others.
3. The reply keeps the shape the desk reads: a "Summary" heading whose last line starts "Saved:", the heading "Draft impact note. For the regulatory change owner. Not issued.", one seven-column table with a column called Mark, and a last line that starts "Proposal:". The summary holds no count and is not in the first person.
4. The ten tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`. Send "Write the impact note for publication" and the id, or "Go through the new publications in the feed."

- `PUB-7301`: a circular that shortens the final response to a complaint from 30 days to 20 days from 1 Jan 2027. Bears on `OBL-05`, owner Head of Complaints.
- `PUB-7302`: a consultation paper on a cooling-off period of 21 days in place of 14. Consultation only: not a rule yet. It would bear on `OBL-02`.
- `PUB-7303`: a fee notice, USD 84,000.00 due by 31 Jan 2027. Bears on `OBL-11`, owner Finance Director.
- `PUB-7304`: a circular for the aviation class. Does not apply: the insurer writes no aviation insurance. No obligation is named.
- `PUB-7305`: an amendment to an earlier circular, `PUB-7291`. It changes the time to decide a claim from 20 working days to 15. Bears on `OBL-03` only.
- `PUB-7306`: a notice that republishes earlier guidance under a new reference. Duplicate of `PUB-7292`. Nothing new.
- `PUB-7307`: a circular on automated tools in pricing and underwriting. No matching obligation: the register is silent, and compliance decides whether a new obligation is needed.
- `PUB-7308`: a circular for group medical insurance, a line the insurer writes. Pre-authorisation answered within 2 working days in place of 5 from 1 Feb 2027. Bears on `OBL-08`, owner Head of Health Claims.

Both regulators, every circular and every person in the invented insurer are invented.

## Where it stops for a person

The regulatory change owner reads each note and decides what changes in the obligations register. At the invented insurer that is the compliance officer. Compliance decides whether a new obligation is needed where the register is silent. Whether the insurer meets a rule, whether it answers a consultation and anything said to a regulator are for a person. The agent does none of this.
