# Banking pack

30 agents a bank can build on the Katonic platform, and the applications people use them through.

**Status: work in progress.** The State column says where each one stands. "Planned" means the folder is not written yet.

Every agent follows one rule: it prepares the work, and a person makes the decision. A tool that changes something waits for approval unless the bank has decided otherwise for that tool.

## The agents

| # | Agent | What it does | Type and form | How people meet it | State |
|---|---|---|---|---|---|
| | **Financial crime** | | | | |
| 1 | Sanctions Alert Review | Compares the customer record with the list entry field by field and recommends clear or escalate, with reasons | Workflow, event-triggered | Sanctions desk | Planned |
| 2 | AML Investigation | Builds the case file for a transaction-monitoring alert and drafts the narrative | Autonomous | Investigations desk | Planned |
| 3 | Adverse Media Screening | Searches the sources the bank names and summarises what it finds, each point with its link | Autonomous | Returns its summary to whoever asked | Planned |
| 4 | Fraud Case Summary | Gathers the transactions, earlier contacts and notes for a flagged card or payment and drafts the case summary | Workflow, event-triggered | Fraud desk | Planned |
| | **Onboarding and know your customer** | | | | |
| 5 | Customer Onboarding | Reads an applicant's documents, checks them against the application and the screening service, and prepares the account-opening file | Workflow, event-triggered | Onboarding and review desk | Planned |
| 6 | Business Onboarding | Reads the registry extract, draws the ownership chain, lists directors and owners for screening, and prepares the file | Multi-agent, pipeline | Onboarding and review desk | Planned |
| 7 | Periodic Review | Compares what the bank holds with fresh documents and a fresh screening, and drafts the refreshed profile with every change marked | Workflow, scheduled | Onboarding and review desk | Planned |
| | **Lending** | | | | |
| 8 | Loan Application Intake | Checks an application pack for completeness, extracts the figures and lists what is missing | Workflow, event-triggered | Lending desk | Planned |
| 9 | Credit Analysis | Spreads the financial statements, works out the ratios the bank's policy names, and drafts the credit memo with the source of every figure | Workflow, API | Lending desk | Planned |
| 10 | Loan Document Verification | Compares the contract and security documents with the approved terms and marks every difference | Workflow, API | Lending desk | Planned |
| 11 | Collections Call Review | Summarises a collections call, checks it against the bank's conduct rules, and drafts the follow-up note | Workflow, scheduled | Sent to the supervisor | Planned |
| | **Customer service** | | | | |
| 12 | Banking Support | Drafts the reply to a customer's question from the bank's documents and the customer's own records | Conversational, acting | Chat | Planned |
| 13 | [Card Servicing](agents/card-servicing/README.md) | For a member of staff on a call: card status, recent transactions and open disputes, and the block, replacement or dispute request prepared | Conversational, acting | Card servicing screen | Written, not yet built |
| 14 | Complaint Handling | Classifies a complaint, gathers the customer's history, and drafts the response and the log entry | Workflow, event-triggered | Complaints desk | Planned |
| | **Payments operations** | | | | |
| 15 | Payment Investigation | Traces a payment's status, lines up the messages, and drafts the reply to the customer or the other bank | Workflow, event-triggered | Payments desk | Planned |
| 16 | Payment Exception Repair | Reads a held payment and the reason it stopped, and proposes the correction with the rule it relied on | Workflow, event-triggered | Payments desk | Planned |
| 17 | Reconciliation Break | Gathers both sides of an unmatched item and proposes the match or the adjusting entry with the evidence | Workflow, scheduled | Reconciliation desk | Planned |
| | **Compliance and audit** | | | | |
| 18 | [Regulatory Monitoring](agents/regulatory-monitoring/README.md) | Reads the regulators' publication feeds on a clock and writes a digest of what is new. The desk then drafts a gap analysis against the bank's policies | Workflow, scheduled | Regulatory change desk | Daily sweep built and run on a schedule on a development cluster |
| 19 | [Policy and Procedures Assistant](agents/policy-and-procedures-assistant/README.md) | Answers staff questions from the bank's own policies and procedures, citing the document | Conversational, answering | Chat | Built and tested as a draft. Not yet published |
| 20 | Audit Evidence | Collects the evidence a control test plan names and lists what is missing | Workflow, scheduled | Sent to the auditor | Planned |
| 27 | Third-Party Risk Assessment | Reads a supplier's questionnaire and evidence, and drafts the assessment against the bank's requirements | Workflow, event-triggered | Third-party risk desk | Planned |
| | **Finance and relationship management** | | | | |
| 21 | Management Reporting | Answers questions on the finance warehouse in plain language, shows the query it ran, and drafts the commentary | Conversational, answering | Chat | Planned |
| 22 | Client Meeting Brief | The client's holdings and exposure, recent contacts and public news, in one brief | Workflow, scheduled | Sent to the relationship manager | Planned |
| | **Technology** | | | | |
| 23 | Incident Response | Gathers the dashboards, metrics and recent changes for an incident and drafts the first assessment | Multi-agent, manager | Posted on the incident ticket | Planned |
| 24 | Legacy System Explainer | Explains the tables, keys and stored procedures of an old system and drafts the documentation nobody wrote | Conversational, answering | Chat | Planned |
| 28 | Post-Incident Review | Investigates a closed incident across the connected systems and drafts the root cause and the review | Autonomous | Deployed app | Planned |
| 29 | Mainframe Modernisation | Converts a batch of legacy code in stages for an engineer to review | Multi-agent, pipeline | Deployed app | Planned |
| | **Pensions and funds** | | | | |
| 25 | Member Fund Assistant | Answers a member's questions about funds and their own holdings, with every figure taken from the fund fact sheets | Conversational, answering | Chat | Planned |
| 26 | Contribution and Transfer Processing | Checks contribution files and transfer forms against the written procedures and reports how many passed and how many need a person | Multi-agent, pipeline | Batch report, failed forms to a person | Planned |
| | **Capital markets** | | | | |
| 30 | Equity Research Report | Reads filings and market data and drafts an equity research report for an analyst | Autonomous | Research desk | Planned |

## The desks

A desk is the shared case desk with a different queue. Each one shows the cases, the agent's findings and draft, approve or send back, and a register of who decided what.

| Desk | Agents behind it | State |
|---|---|---|
| Regulatory change desk | Regulatory Monitoring | Built, in [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk) |
| Sanctions desk | Sanctions Alert Review | Planned |
| Investigations desk | AML Investigation, Adverse Media Screening | Planned |
| Fraud desk | Fraud Case Summary | Planned |
| Onboarding and review desk | Customer Onboarding, Business Onboarding, Periodic Review | Planned |
| Lending desk | Loan Application Intake, Credit Analysis, Loan Document Verification | Planned |
| Complaints desk | Complaint Handling | Planned |
| Payments desk | Payment Investigation, Payment Exception Repair | Planned |
| Reconciliation desk | Reconciliation Break | Planned |
| Card servicing screen | Card Servicing | Planned |
| Third-party risk desk | Third-Party Risk Assessment | Planned |
| Research desk | Equity Research Report | Planned |

## How an agent reaches a bank's systems

1. **An imported API.** The bank gives the platform the OpenAPI file of an API it already runs, and each operation becomes a tool.
2. **An MCP server** from the Catalog, running inside the bank's own cluster.
3. **A knowledge source.** Policies, procedures and product documents, indexed with each reader's permissions kept.
4. **A file the user uploads** in the conversation.

To try an agent before your own systems are connected, run the invented bank in [`demo-bank/`](../demo-bank/README.md). It offers the first two routes, and [its scenario list](../demo-bank/SCENARIOS.md) gives the right answer for every case.
