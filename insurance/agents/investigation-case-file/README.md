# Investigation Case File

For a claim referred to the investigations desk, builds the case file: the parties, their earlier claims, the links between them and the public notices that name a person on the claim, each with its source. It states what the records show and leaves the judgement to the investigator. It never says that a person did wrong.

| | |
|---|---|
| Type and form | Autonomous agent: it works through many steps on its own |
| What starts it | A claim being referred to the investigations desk, or an investigator's request |
| How people meet it | An application: the Investigations desk |
| Reads from | The insurer's investigations system: the referred claim with its parties and the handler's referral, the measurement behind the referral, the earlier claims of every party, the links of the claim, and the public notices for each person on it |
| Changes | Saves a draft case file. The draft changes nothing on the claim and contacts nobody |
| State | Written. Not yet built on a cluster. Not on the Catalog shelf |

## What it does

- Reads the claim and its referral, then works through the other reads on its own: the measurement behind the referral, the earlier claims of every party, the links of the claim, and the public notices for each person on the claim.
- Writes one row for the referral, with each indicator in the form "Indicator FI-1 is met: 18 days against 30 days or fewer".
- Writes one row for each party. For a witness it gives the name, the id, the role and the date of birth, and nothing else from that person's record.
- Writes one row for each earlier claim of a party, with the claim's id, whose claim it was, the date of the loss and the amount paid.
- Writes one row for each link the system gives: "Linked through" the repairer, the witness, the phone number, the address or the bank account, with the id of the linked claim and of the party the link runs through. The system does the matching.
- Writes one row for each public notice that names a person with a party's name, with what the system says on whether it is about the party. A notice about the party is given as a public record of what it says. A notice about another person of the same name is marked as not about the party, with the reason, and what it says is not set out.
- Says so in a row where no earlier claim, no link or no notice was found. A file with nothing found reports the reason for the referral and adds nothing.
- Saves the case file as a draft, and says it was saved only if the system's reply says so.
- Ends with one proposal line: a case file with links to the claims named, or a case file with no links found, for the investigator to read.

## What it does not do

- Say that fraud took place, that a claim is false, or that a person did wrong. It does not call anyone a fraudster or a suspect, and does not call people a ring or a link suspicious.
- Say what a link, an earlier claim or a notice means about a person. The investigator decides.
- Attach a notice about another person to a party.
- Decline, delay, hold or pay a claim, or change a record.
- Contact a claimant, a witness, a repairer, the police or anyone else, or pass a person's details to anyone.
- Search for a person outside the insurer's records and its public notices.
- Guarantee the same rows or wording on every run. The case file is a draft for the investigator. Run the tests on your own model before you rely on it, and read the saved drafts for the wording as well as the replies.

Asked to name people as having done wrong or to decline a claim while it builds a file, it says in one line that it cannot, and still builds the case file exactly as the records give it.

## What you set up

- A model for the Reasoning tier.
- The insurer's investigations system, connected as an imported API, with the six operations listed in [`agent.yaml`](agent.yaml) and no others.
- The Investigations desk, which sends the claim's id, if you want to meet the agent through a screen. The agent also answers in a chat.

## Build it

This folder is written and has not yet been built on a cluster. The steps will be written here once they have been run. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the six tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading whose last line starts "Saved:", the heading "Draft case file. For the investigator. Not issued.", a six-column table (the fifth column is called Mark), and a last line that starts "Proposal:". The summary holds no count of marks and is not in the first person.
4. The ten tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`:

- `CLM-6301`, `CLM-6302`, `CLM-6303`: three claims by three claimants. Each is linked to the other two through the repairer, Brackenfold Motor Works (`PTY-3501`), and through the phone number +999 555 0142. The file names the claims, the repairer and the number, and says no more.
- `CLM-6304`: the public notice `PN-901` is about the claimant: the name, the date of birth and the address agree. The file gives it as a public record of what it says, lists the earlier claim `CLM-6041`, says that no link was found, and draws nothing from the notice about this claim.
- `CLM-6305`: the public notice `PN-902` names another person with the claimant's name. The year of birth and the address differ. The file marks it as not about the party and gives the reason.
- `CLM-6306`: no earlier claim, no link and no public notice. The file says so and reports the reason for the referral.
- `CLM-6307`: linked to `CLM-6031` through the witness only. Hester Quarmby (`PTY-3028`) is named as a witness on both claims, as a fact of the records, and nothing more is said about her.

Everyone and everything in the invented insurer is invented, and so is every notice.

## Where it stops for a person

The investigator reads the case file and decides what a link, an earlier claim or a public notice means, and what to do next. The agent makes no finding about a claim or a person, decides nothing about payment and contacts nobody.
