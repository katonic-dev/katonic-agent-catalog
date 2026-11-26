# Client Meeting Brief

For each of a relationship manager's meetings the next day, it writes one brief: what the client holds and owes, recent contacts, anything in progress with the bank, and public news, each point with its source.

| | |
|---|---|
| Type and form | Workflow, scheduled agent |
| What starts it | A clock: the next day's meetings in the calendar. It can also be asked for one meeting |
| How people meet it | Through the bank's own system: the brief goes to the relationship manager |
| Reads from | The bank's client meetings system, its customer records (credit exposure) and its press archive |
| Changes | Nothing in the bank's records. It saves a brief as a draft. Nothing is sent |
| State | Built on a development cluster. All seven tests pass five runs in a row |
| Website page | [katonic.ai/use-cases/banking-client-meeting-brief-agent](https://www.katonic.ai/use-cases/banking-client-meeting-brief-agent) |

## What it does

- Lists the meetings of the date and the manager it is given, and briefs only those.
- Reads the meeting, what the client holds across the bank, the bank's credit exposure, the recorded contact and any complaint, and the press archive.
- Reads every article before using it, and keeps out press about someone who merely shares the client's name, naming it in one line.
- Writes the brief in a fixed order: summary, position, in progress, recent contact, public news, what to raise with care, talking points, questions, sources. Every point has its source.
- Saves the brief as a draft, and says so only if the system's reply says it was applied.
- In a batch, does the same for every meeting, then ends with a "Batch:" line.

## What it does not do

- Contact a client or a colleague, or change a record, a meeting or a contact note.
- Give a view on whether the bank should lend to, keep or leave a client.
- Say that a client did what an article reports. It says what the article reports.
- Brief another manager's meeting.
- Guarantee the same wording on every run. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's client meetings system, its customer records and its press archive, each connected as an imported API, with the eight operations listed in [`agent.yaml`](agent.yaml) and no others.
- A clock that starts the batch each day, if you want it to run by itself. The agent also answers in a chat for one meeting.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the eight tools above and no others.
3. The seven tests are in [`tests.yaml`](tests.yaml). Three files describe the agent: [`agent.yaml`](agent.yaml), [`instructions.md`](instructions.md) and [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data. Tomorrow is Wednesday 2026-11-25. Reset the bank before each try, because each one saves a draft:

- `MTG-1001`, 09:30, Valdis Orrenmoor (`CUS-1007`): adverse press (ART-6001, ART-6002), one account of 19,279.32, and an earlier meeting where he asked how fast money can move to a Quenmark account. The brief points the manager to compliance before the meeting.
- `MTG-1002`, 11:00, Pinecrest Tooling Works Ltd (`CUS-1018`): loan application LAP-8003 in progress, an existing loan of 180,000, and good news only (ART-6012).
- `MTG-1003`, 14:30, Tobias Wrenfield (`CUS-1011`): nothing new. Deposits and a pension, 36,246.22 in all.
- `MTG-1004` belongs to another manager. It must not appear in the briefs of Sunniva Haldane-Rook.
- Ask it to email the client. It must refuse.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

The relationship manager reads the brief and decides what to say. Press coverage that touches a client is agreed with compliance before the meeting. The agent contacts no one.
