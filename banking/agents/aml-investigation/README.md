# AML Investigation

Builds the case file for a transaction monitoring alert and drafts the narrative, which it saves on the alert. It decides which lookup to make next from what the last one found.

| | |
|---|---|
| Type and form | Autonomous agent |
| What starts it | A transaction monitoring alert. The bank's monitoring system can announce a new alert through its event for new monitoring alerts, and a person, or the Investigations desk, can also start the investigation |
| How people meet it | An application: the Investigations desk |
| Reads from | The bank's monitoring system, core system and press archive: the alert with its rule and the investigations already saved on it, the account's transactions, the counterparties, the customer's alert history and contacts, and press coverage |
| Changes | Saves a draft investigation on the alert: the findings with the ids of the records that show them, the narrative and a recommendation. It opens no case and has no operation that does |
| State | Written, not yet built. The instructions and tests have not been run on a model |

## What it does

- Reads the alert and the rule, checks each condition of the rule against the transactions, and compares the alert's period with the account's earlier history.
- Follows each lookup to the next: a counterparty, the customer's contacts, earlier alerts, press coverage.
- Looks as hard for what explains the activity as for what supports concern, and says plainly when the records explain it.
- Marks each finding supports concern, explains the activity, neutral, unclear or missing, with the ids of the records. A press article about someone else with the same name is set aside in the narrative and is not a finding.
- Drafts the narrative in plain sentences, each resting on ids, under its own heading apart from the table, and says what is missing and who could supply it. The Summary above the table is four lines at most and holds no count of marks.
- Saves the findings, the narrative and a recommendation on the alert as a draft. When a person opens a case from the alert, the latest saved narrative becomes the first narrative of the case.
- Names an article in the narrative and keeps its id out of the saved ids, because the system takes only ids of transactions, alerts, rules, contacts and counterparties there.
- Says what the system said when it refuses a save, for example because the alert is no longer open, and does not claim anything was saved.
- Ends with one recommendation line: open a case, no case, or what to ask for. The system holds only open a case and no case, so a line that asks for something is not saved.

## What it does not do

- Open a case, close an alert or file a report. The investigator decides and files.
- Call anything proven, suspicious beyond the records, or illegal. It says the records fit the pattern the rule describes, or explain it.
- Fill a gap: a contract, an invoice or a reason that is not on record is missing.
- Tell the customer or anyone outside the investigation that an alert exists.
- Guarantee the same marks on every run. The draft is for the investigator. Run the tests on your own model before you rely on it.

## What you set up

- A model for the Reasoning tier.
- The bank's monitoring system, core system and press archive, connected as imported APIs, with the eleven operations listed in [`agent.yaml`](agent.yaml) and no others.
- The [Investigations desk](../../desks/investigations/README.md), which sends the case, if you want to meet the agent through a screen. It needs the case desk engine that reads the `routing` setting, and the agent's id in `AML_AGENT_ID`. The agent also answers in a chat.
- An API key with the Chat scope for the desk, and the published agent's id.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the tools above and no others.
3. The reply must keep the shape the desk reads: a "Summary" heading, the heading "Draft case file. For the investigator. Not decided.", a seven-column table, the heading "Investigation narrative. Draft. Not decided." with the narrative under it, and a last line that starts "Recommendation:". Change the instructions and the desk's `routing` setting for "Alert investigation" together.
4. The tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data:

- `TMA-3001`: structuring. Brightwater Cash and Carry Ltd made seven cash deposits of USD 9,100 to 9,800 in 10 days, total USD 66,450, each under the USD 10,000 threshold. Earlier deposits were USD 1,400 to 3,100. Open a case.
- `TMA-3002`: pass-through. Three credits (USD 48,000, 52,500, 39,000) from Tallowmere Holdings each left the next day to Quillgate Trading, keeping about 1.36 percent (USD 1,900 of USD 139,500). The customer could not name its clients. Open a case.
- `TMA-3003`: higher-risk country. Four payments to Karn Harbour Freight Agency in Kharnovia, total USD 53,250, a new counterparty with no contract. Open a case at medium priority, and say that the contract and invoices are missing. Nothing is proven.
- `TMA-3004`: a benign payroll spike. 41 payroll payments against an average of 22, because 19 seasonal staff were hired, as the owner said 45 days before. No case. The recommendation saved on the alert is no case.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

The investigator reads the case file and decides whether to open a case, how urgent it is and whether to file a report. The agent saves its work on the alert as a draft and opens nothing.
