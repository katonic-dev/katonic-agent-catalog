# Investigations desk

The settings folder that turns the Katonic case desk into a desk for a bank's investigators and compliance analysts. Two kinds of case sit in one queue. A transaction monitoring alert is investigated: the account's history, the counterparties, earlier alerts, the customer's contacts and press coverage are built into a case file with a drafted narrative, which the agent saves on the alert as a draft. A request to screen a subject is run against the press archive: each article is read and marked as adverse and about the subject, about someone else with the same name, or neutral. Each kind goes to its own agent. A person decides.

Meridian Trust Bank (an invented bank in the invented country Meridia), its customers, its alerts and its press archive are invented. Nothing here is a real investigation.

## The two kinds of case

| Kind | Agent | What the agent does | What goes to the person |
|---|---|---|---|
| Alert investigation | [AML Investigation](../../agents/aml-investigation/README.md) | Reads the alert and its rule, then follows each lookup to the next. Builds the case file, drafts the narrative and saves the findings and the narrative on the alert as a draft. Looks for what explains the activity as hard as for what supports concern | The case file, for the investigator, who decides whether to open a case and whether to file a report |
| Media screening | [Adverse Media Screening](../../agents/adverse-media-screening/README.md) | Searches the press archive for the subject, reads every article, and sets its facts beside the subject's record. Gives each article's id and page address | The findings, for the compliance analyst, who judges what is relevant |

The desk sends the agent one message: the drafting instruction for the kind, then the case. The agent reads the records itself from the bank's systems.

## What the person sees

- **A queue of cases**, each with its kind, its id and its customer or subject.
- **The case beside the case file.** The desk's short summary is on one side. The agent's draft is on the other.
- **One table for both kinds**, one row for each finding. Each row has the finding, its evidence ids, what the record shows, where it is found, a mark, and what to check. A media screening words the lines of its rows for its own work: Article, Who it is about, Found in, What to check. The canned replies give the article's place in words with its id ("The press archive, article ART-6005"); a real agent gives the page address the bank returns, and an address in a row is shown as a link.
- **The investigation narrative as a card of its own**, for an alert, under the rows. It is set as a document, kept in paragraphs, and can be edited on its own before the person decides. It states facts with their record ids and amounts and never says a customer is guilty of anything.
- **The agent's recommendation**, one line.
- **The register** afterwards: who decided what, when, on which version of the case file, and with which agent run and tool calls.

### The marks

| Mark | Meaning |
|---|---|
| supports concern | The record fits the pattern the rule describes, or the article is about the subject and adverse. It proves nothing by itself |
| explains the activity | The record gives an innocent reading of the same activity. It does not close the matter |
| neutral | Background that bears on neither side, or an article about the subject that reports nothing adverse |
| someone else | The article is about a person or a company with the same or a similar name, and a fact in it separates them from the subject |
| unclear | The record or article does not say enough to settle it, or two records disagree. The agent says which and chooses neither |
| missing | A record or document that should be there is not, or a search found nothing |

Alert investigation uses supports concern, explains the activity, neutral, unclear and missing. Media screening uses supports concern, neutral, someone else, unclear and missing, and shows them as Adverse, Not adverse, Someone else, Unclear and None found (in grey, because nothing found is not a fault; an alert keeps Missing, in amber, for evidence that should exist and does not). Colours: supports concern and Adverse are red, explains the activity is green, unclear and missing are amber (a screening's None found is grey), neutral is grey, and someone else is blue with its own sign, so that an article about a namesake is set apart at a glance. The count above the rows lists only the marks of the kind.

## What the person decides

| Decision | For | What it records |
|---|---|---|
| Open a case | Alert investigation | Why, and the priority. The desk opens no case in the monitoring system: the investigator does, and any report is filed by a person, elsewhere |
| No case needed | Alert investigation | What explains the activity. The desk closes no alert: the investigator does |
| Accept the findings | Media screening | The analyst takes the findings as the file note. It changes nothing in the bank's systems |
| Refer on | Both kinds | Who it goes to, and why |
| Ask for more | Alert investigation | What to ask for, one item to a line, for example a contract or invoices from the relationship manager. It is internal and nothing is sent to the customer. The case waits until the reply is added, then the agent reads the records again |
| Ask the agent to redo the case file | Both kinds | A note that the agent sees |

A case shows only the buttons that fit its kind: an alert offers Open a case, No case needed, Ask for more, Refer on and the redo; a media screening offers Accept the findings, Refer on and the redo. The server refuses any other decision (409). The button for the agent's recommendation is marked "Agent's proposal". The person who entered a case cannot decide it. The agents save only drafts. When a person opens a case from an alert, the latest saved narrative becomes the first narrative of the case. The desk opens no case, closes no alert and files no report. The bank's monitoring system has no operation that files a report: a person does that.

## The ten demo cases

| Case | Kind | What the agent should find |
|---|---|---|
| TMA-3001, Brightwater Cash and Carry Ltd | Alert investigation | Structuring. Seven cash deposits of USD 9,100 to 9,800 in 10 days, total USD 66,450, each under the USD 10,000 threshold. Earlier deposits were USD 1,400 to 3,100. A branch note, CNT-5008, says the owner brings deposits in batches. Open a case |
| TMA-3002, Nimbus Transit Consulting Ltd | Alert investigation | Pass-through. Three credits (48,000, 52,500, 39,000) from Tallowmere Holdings each leave the next day to Quillgate Trading, keeping about 1.36 percent (USD 1,900 of USD 139,500). The customer could not name its clients (CNT-5009). Open a case |
| TMA-3003, Copperfield Import Traders Ltd | Alert investigation | Four payments (14,800, 9,950, 12,300, 16,200; total 53,250) to Karn Harbour Freight Agency in Kharnovia, a new counterparty with no contract. A freight need is plausible, so the narrative says what is missing, the contract and the invoices, and calls nothing proven. Open a case at medium priority |
| TMA-3004, Saltmarsh Catering Co | Alert investigation | Not suspicious. 41 payroll payments against an average of 22, because 19 seasonal staff were hired, as the owner said 45 days earlier (CNT-5011). The 22 regular payees and amounts are unchanged, and a festival contract advance of USD 98,000 arrived the day before. No case |
| Valdis Orrenmoor (CUS-1007) | Media screening | Adverse and about him. ART-6001 and ART-6002: an asset freezing order for arms brokering, upheld. Born 30 September 1971, a Quenmark national who lives on Cinder Quay in Port Ilvane |
| Karn Harbour Freight Agency (CPY-4005) | Media screening | Adverse and about the agency. ART-6003, a customs inquiry, and ART-6004, an accusation of moving goods for listed buyers |
| Perdita Vanhollow (CUS-1010) | Media screening | No article names her. ART-6005 and ART-6006 are about her spouse and are not about her |
| Wynne Castellane (CUS-1005) | Media screening | A namesake. ART-6008 is about a 54-year-old machinery dealer in Brandymoor, Tessaly. The customer was born in 1990, in Marlow Reach, Meridia |
| Harrowgate Bakery Supplies Ltd (CUS-1017) | Media screening | A company namesake. ART-6011 is about a flour mill in Hartsfell, Quenmark, with no link to Meridia |
| Pinecrest Tooling Works Ltd (CUS-1018) | Media screening | Nothing adverse. ART-6012 reports an export award and names 24 staff, the same as the loan application LAP-8003 |

The AML Investigation agent saves its investigation on the alert as a draft: findings with the ids of the records that show them, the narrative, and a recommendation of open a case or no case. The system refuses a save when the alert is not open or an id does not exist, and takes no article id among the ids, so articles are named in the narrative. A last line of "ask for" is not saved, because the system holds only the two recommendations. The agent opens no case.

## Which engine it needs

It needs the case desk engine ([katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk)) in a version that reads `DESK_CONFIG` and the `routing` setting with per-kind `decisions`, `marks`, `markLabels`, `markTones` and `rowLabels`, the section cards of `draft.sections`, the `info` and `plain` mark tones and links in rows, and that supports `DESK_AGENT_ID` and `demo-replies.json` in a settings folder. That engine version is in `main` of katonic-case-desk since 24 November 2026 ([pull request 2](https://github.com/katonic-dev/katonic-case-desk/pull/2)). An earlier engine ignores `routing`, and every case would go to one agent with one instruction.

## Run it

Clone the engine and this catalog side by side, then, in the engine's folder:

```bash
npm install
DESK_CONFIG=../katonic-agent-catalog/banking/desks/investigations/desk.config.json \
KATONIC_BASE_URL=<the platform's agent API address> \
KATONIC_API_KEY=<a key with the Chat scope> \
AML_AGENT_ID=<id of AML Investigation> \
MEDIA_AGENT_ID=<id of Adverse Media Screening> \
KATONIC_AGENT_ID=<either one, for a case of an unknown kind> \
SEED_DEMO=true \
npm start
```

| Setting | What it does here |
|---|---|
| `DESK_CONFIG` | This folder's `desk.config.json`. Without it the engine is the regulatory change desk |
| `KATONIC_BASE_URL`, `KATONIC_API_KEY` | The platform's agent API, and a key with the Chat scope |
| `AML_AGENT_ID` | The agent for cases of the kind Alert investigation. If it is empty, drafting such a case fails and says which variable to set |
| `MEDIA_AGENT_ID` | The same, for Media screening |
| `KATONIC_AGENT_ID` | The agent for a case whose kind is neither. The desk asks it only to say that the kind is not recognised. It can be either of the two agents. `DESK_AGENT_ID` does the same and wins over it. A file cannot override it |
| `DESK_ENV_FILE` | A settings file to read in place of `.env`, for the platform address and key, when several desks share one |
| `SEED_DEMO` | `true` loads the ten demo cases on the first start |
| `DATA_DIR` | A folder for the desk's records, so they outlive a restart |
| `DATABASE_URL` | Keeps the records in PostgreSQL instead of a file |
| `INTAKE_TOKEN` | Turns on intake by webhook. The sender gives it as `X-Intake-Token` |
| `LOCAL_USER`, `LOCAL_USER_NAME` | The investigator's name when the desk does not trust sign-in headers. Every register row says which it was |
| `TRUST_SIGN_IN_HEADERS` | `true` only where nothing can reach the desk except through the platform's sign-in |
| `PORT`, `PUBLIC_URL` | The port the desk listens on, and its public address when it sits behind a prefix |
| `KATONIC_MAX_MESSAGE_CHARS` | The longest message the desk sends. The default is 15,000 characters |
| `DESK_LIBRARY_DIR`, `KATONIC_LIBRARY_NAME` | Not used. This desk has no library: the agents read the bank's systems |

The kind of a case is the value of its "Kind of work" field, matched without regard to case: `Alert investigation` or `Media screening`.

Build the two agents from [`aml-investigation`](../../agents/aml-investigation/README.md) and [`adverse-media-screening`](../../agents/adverse-media-screening/README.md). Each folder's `instructions.md` and the matching `routing` instruction in `desk.config.json` ask for the same reply, and must be changed together.

## Without a platform

The engine's stand-in platform answers from this folder's `demo-replies.json`, one canned reply for each demo case, keyed by a distinctive part of the customer's or subject's name in the case title. Each follows the right answers in the invented bank's scenario list. Each says that it comes from the stand-in and that nothing was saved. Start it with the same `DESK_CONFIG`:

```bash
DESK_CONFIG=../katonic-agent-catalog/banking/desks/investigations/desk.config.json node demo/fake-platform.js
```

Then start the desk with `KATONIC_BASE_URL` pointing at the stand-in, any value for `KATONIC_API_KEY`, and any value for each of the two agent ids. The stand-in does not read them. It shows the screens and the marks. It is not an agent, and it reads nothing from the bank.

## How a case reaches the desk

A member of the investigations team enters it, or a person or another agent asks for a media screening, or the bank's monitoring system sends an alert to `POST /api/intake` with the intake token. The bank has no event for new monitoring alerts, so something has to send the alert. For a media request, the sender gives the desk's fields, including the kind. The desk reads the case's fields, not the bank's own messages.

## Files

| File | What it is |
|---|---|
| `desk.config.json` | Every wording, field, mark, decision, status and register label, and the `routing` setting with the two drafting instructions |
| `cases.json` | The ten demo cases |
| `demo-replies.json` | The stand-in's canned reply for each demo case |

## How it was tested

On 24 Nov 2026, in a headless browser, against the engine with the stand-in platform and a recording proxy between the desk and the stand-in. 12 scenarios and 388 checks, all passing, with no console error, page error or failed request. The script checks:

- the desk opens with the ten cases, with kind, id and status on each line;
- every demo case: the rows, the mark on each row, the proposal and the marked button against the right answers in the invented bank's scenario list (figures such as USD 66,450, USD 139,500 and 1.36 percent are recomputed), the narrative card on each alert and none on a media screening, the namesake rows set apart, and no web address in the canned rows;
- routing: each draft request carried its own agent id and its own instruction, the same two instruction rules (no first person, no count of marks in the Summary), and the question about a case went to the agent that drafted it;
- send back with a note and a new version, then an edit of the narrative recorded as version 3 by the investigator;
- every decision on a case it fits (open a case, no case, ask for more with the wait and the reply, refer on for an alert and for a screening, accept the findings), and the server refusing a decision the kind does not allow;
- the register and its export, filters and search by kind, customer and id, a new case by hand (an empty form shows the error, a valid one is drafted from the stand-in's default reply, an unknown kind gets the desk's own instruction, a wrong entry is removed), the theme switch, a phone-width window at 390 and 360 (nothing wider than the screen, the queue folds, the jump bar works, every button at least 40 px high) and a reload that loses nothing.

Then every state was photographed at 1440 and 390 wide in light and dark and looked at. The faults found are in the visual design review. The ports used were 8403 (stand-in), 8413 (recording proxy) and 3417 (desk).
