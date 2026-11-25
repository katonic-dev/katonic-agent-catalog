# Banking pack

30 agents a bank can build on the Katonic platform, and the applications people use them through.

**Status: work in progress.** The State column says where each one stands. "Planned" means the folder is not written yet.

Every agent follows one rule: it prepares the work, and a person makes the decision. A tool that changes something waits for approval unless the bank has decided otherwise for that tool.

## The agents

| # | Agent | What it does | Type and form | How people meet it | State |
|---|---|---|---|---|---|
| | **Financial crime** | | | | |
| 1 | [Sanctions Alert Review](agents/sanctions-alert-review/README.md) | Compares the customer record with the list entry field by field and recommends clear or escalate, with reasons | Workflow, event-triggered | Sanctions desk | Built on a development cluster. All ten tests pass five runs in a row. Its desk is tested against a stand-in agent |
| 2 | [AML Investigation](agents/aml-investigation/README.md) | Builds the case file for a transaction-monitoring alert and drafts the narrative | Autonomous | Investigations desk | Written. Its desk is tested against a stand-in agent. Not yet built on a platform |
| 3 | [Adverse Media Screening](agents/adverse-media-screening/README.md) | Searches the sources the bank names and summarises what it finds, each point with its link | Autonomous | Returns its summary to whoever asked | Built on a development cluster. All nine tests pass five runs in a row. Its desk is tested against a stand-in agent |
| 4 | [Fraud Case Summary](agents/fraud-case-summary/README.md) | Gathers the transactions, earlier contacts and notes for a flagged card or payment and drafts the case summary | Workflow, event-triggered | Fraud desk | Written. Its desk is tested against a stand-in agent. Not yet built on a platform |
| | **Onboarding and know your customer** | | | | |
| 5 | [Customer Onboarding](agents/customer-onboarding/README.md) | Reads an applicant's documents, checks them against the application and the screening service, and prepares the account-opening file | Workflow, event-triggered | Onboarding and review desk | Written. Its desk is tested against a stand-in agent. Not yet built on a platform |
| 6 | [Business Onboarding](agents/business-onboarding/README.md) | Reads the registry extract, draws the ownership chain, lists directors and owners for screening, and prepares the file | Multi-agent, pipeline | Onboarding and review desk | Written. Its desk is tested against a stand-in agent. Not yet built on a platform |
| 7 | [Periodic Review](agents/periodic-review/README.md) | Compares what the bank holds with fresh documents and a fresh screening, and drafts the refreshed profile with every change marked | Workflow, scheduled | Onboarding and review desk | Written. Its desk is tested against a stand-in agent. Not yet built on a platform |
| | **Lending** | | | | |
| 8 | [Loan Application Intake](agents/loan-application-intake/README.md) | Checks an application pack for completeness, extracts the figures and lists what is missing | Workflow, event-triggered | Lending desk | Built on a development cluster. All six tests pass five runs in a row. Its desk is tested against a stand-in agent |
| 9 | [Credit Analysis](agents/credit-analysis/README.md) | Spreads the financial statements, works out the ratios the bank's policy names, and drafts the credit memo with the source of every figure | Workflow, API | Lending desk | Written. Its desk is tested against a stand-in agent. Not yet built on a platform |
| 10 | [Loan Document Verification](agents/loan-document-verification/README.md) | Compares the contract and security documents with the approved terms and marks every difference | Workflow, API | Lending desk | Written. Its desk is tested against a stand-in agent. Not yet built on a platform |
| 11 | [Collections Call Review](agents/collections-call-review/README.md) | Summarises a collections call, checks it against the bank's conduct rules, and drafts the follow-up note | Workflow, scheduled | Sent to the supervisor | Written. Not yet built on a platform |
| | **Customer service** | | | | |
| 12 | [Banking Support](agents/banking-support/README.md) | Drafts the reply to a customer's question from the bank's documents and the customer's own records | Conversational, acting | Chat | Written. Not yet built on a platform |
| 13 | [Card Servicing](agents/card-servicing/README.md) | For a member of staff on a call: card status, recent transactions and open disputes, and the block, replacement or dispute request prepared | Conversational, acting | Card servicing screen | Built and tested on a development cluster. Tests 2 to 5 pass three runs each on the published agent, and each change waits for approval. The step after a second person approves is not tried yet |
| 14 | [Complaint Handling](agents/complaint-handling/README.md) | Classifies a complaint, gathers the customer's history, and drafts the response and the log entry | Workflow, event-triggered | Complaints desk | Built on a development cluster. All eight tests pass five runs in a row. Its desk is tested against a stand-in agent |
| | **Payments operations** | | | | |
| 15 | [Payment Investigation](agents/payment-investigation/README.md) | Traces a payment's status, lines up the messages, and drafts the reply to the customer or the other bank | Workflow, event-triggered | Payments desk | Written. Its desk is tested against a stand-in agent. Not yet built on a platform |
| 16 | [Payment Exception Repair](agents/payment-exception-repair/README.md) | Reads a held payment and the reason it stopped, and proposes the correction with the rule it relied on | Workflow, event-triggered | Payments desk | Written. Its desk is tested against a stand-in agent. Not yet built on a platform |
| 17 | [Reconciliation Break](agents/reconciliation-break/README.md) | Gathers both sides of an unmatched item and proposes the match or the adjusting entry with the evidence | Workflow, scheduled | Reconciliation desk | Built on a development cluster. All seven tests pass five runs in a row. Its desk is tested against a stand-in agent |
| | **Compliance and audit** | | | | |
| 18 | [Regulatory Monitoring](agents/regulatory-monitoring/README.md) | Reads the regulators' publication feeds on a clock and writes a digest of what is new. The desk then drafts a gap analysis against the bank's policies | Workflow, scheduled | Regulatory change desk | Daily sweep built and run on a schedule on a development cluster |
| 19 | [Policy and Procedures Assistant](agents/policy-and-procedures-assistant/README.md) | Answers staff questions from the bank's own policies and procedures, citing the document | Conversational, answering | Chat | Built and tested as a draft. Not yet published |
| 20 | [Audit Evidence](agents/audit-evidence/README.md) | Collects the evidence a control test plan names and lists what is missing | Workflow, scheduled | Sent to the auditor | Written. Not yet built on a platform |
| 27 | [Third-Party Risk Assessment](agents/third-party-risk-assessment/README.md) | Reads a supplier's questionnaire and evidence, and drafts the assessment against the bank's requirements | Workflow, event-triggered | Third-party risk desk | Built and tested on a development cluster; its desk reads the real agent's replies. Three of six tests pass five runs in a row, three miss in one run of five |
| | **Finance and relationship management** | | | | |
| 21 | [Management Reporting](agents/management-reporting/README.md) | Answers questions on the finance warehouse in plain language, shows the query it ran, and drafts the commentary | Conversational, answering | Chat | Written. Not yet built on a platform |
| 22 | [Client Meeting Brief](agents/client-meeting-brief/README.md) | The client's holdings and exposure, recent contacts and public news, in one brief | Workflow, scheduled | Sent to the relationship manager | Written. Not yet built on a platform |
| | **Technology** | | | | |
| 23 | [Incident Response](agents/incident-response/README.md) | Gathers the dashboards, metrics and recent changes for an incident and drafts the first assessment | Multi-agent, manager | Posted on the incident ticket | Built on a development cluster as one chat agent: three of six tests pass five runs in a row, the three long assessments do not. Rewritten as a manager with three specialists; that form is not yet tested |
| 24 | [Legacy System Explainer](agents/legacy-system-explainer/README.md) | Explains the tables, keys and stored procedures of an old system and drafts the documentation nobody wrote | Conversational, answering | Chat | Written. Not yet built on a platform |
| 28 | [Post-Incident Review](agents/post-incident-review/README.md) | Investigates a closed incident across the connected systems and drafts the root cause and the review | Autonomous | Deployed app | Written. Not yet built on a platform |
| 29 | [Mainframe Modernisation](agents/mainframe-modernisation/README.md) | Converts a batch of legacy code in stages for an engineer to review | Multi-agent, pipeline | Deployed app | Written. Not yet built on a platform |
| | **Pensions and funds** | | | | |
| 25 | [Member Fund Assistant](agents/member-fund-assistant/README.md) | Answers a member's questions about funds and their own holdings, with every figure taken from the fund fact sheets | Conversational, answering | Chat | Written. Not yet built on a platform |
| 26 | [Contribution and Transfer Processing](agents/contribution-and-transfer-processing/README.md) | Checks contribution files and transfer forms against the written procedures and reports how many passed and how many need a person | Multi-agent, pipeline | Batch report, failed forms to a person | Built on a development cluster. Six of seven tests pass five runs in a row; one passed seven of eight |
| | **Capital markets** | | | | |
| 30 | [Equity Research Report](agents/equity-research-report/README.md) | Reads filings and market data and drafts an equity research report for an analyst | Autonomous | Research desk | Written. Its desk is tested against a stand-in agent. Not yet built on a platform |

## The desks

A desk is the shared case desk with a different queue. Each one shows the cases, the agent's findings and draft, approve or send back, and a register of who decided what.

| Desk | Agents behind it | State |
|---|---|---|
| Regulatory change desk | Regulatory Monitoring | Built, in [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk) |
| [Sanctions desk](desks/sanctions/README.md) | Sanctions Alert Review | Settings written and tested end to end against a stand-in agent. Runs on the engine's `main` |
| [Investigations desk](desks/investigations/README.md) | AML Investigation, Adverse Media Screening | Settings written and tested end to end against a stand-in agent. Runs on the engine's `main` |
| [Fraud desk](desks/fraud/README.md) | Fraud Case Summary | Settings written and tested end to end against a stand-in agent. Runs on the engine's `main` |
| [Onboarding and review desk](desks/onboarding-and-review/README.md) | Customer Onboarding, Business Onboarding, Periodic Review | Settings written and tested end to end against a stand-in agent. Runs on the engine's `main` |
| [Lending desk](desks/lending/README.md) | Loan Application Intake, Credit Analysis, Loan Document Verification | Settings written and tested end to end against a stand-in agent. Runs on the engine's `main` |
| [Complaints desk](desks/complaints/README.md) | Complaint Handling | Settings written and tested end to end against a stand-in agent. Runs on the engine's `main` |
| [Payments desk](desks/payments/README.md) | Payment Investigation, Payment Exception Repair | Settings written and tested end to end against a stand-in agent. Runs on the engine's `main` |
| [Reconciliation desk](desks/reconciliation/README.md) | Reconciliation Break | Settings written and tested end to end against a stand-in agent. Runs on the engine's `main` |
| [Card servicing screen](desks/card-servicing/README.md) | Card Servicing | Settings written and tested end to end against a stand-in agent. Runs on the engine's `main` |
| [Third-party risk desk](desks/third-party-risk/README.md) | Third-Party Risk Assessment | Settings written and tested end to end against a stand-in agent. Runs on the engine's `main` |
| [Research desk](desks/research/README.md) | Equity Research Report | Settings written and tested end to end against a stand-in agent. Runs on the engine's `main` |

## How an agent reaches a bank's systems

1. **An imported API.** The bank gives the platform the OpenAPI file of an API it already runs, and each operation becomes a tool.
2. **An MCP server** from the Catalog, running inside the bank's own cluster.
3. **A knowledge source.** Policies, procedures and product documents, indexed with each reader's permissions kept.
4. **A file the user uploads** in the conversation.

To try an agent before your own systems are connected, run the invented bank in [`demo-bank/`](../demo-bank/README.md). It offers the first two routes, and [its scenario list](../demo-bank/SCENARIOS.md) gives the right answer for every case. [The install guide](../demo-bank/docs/install-on-katonic.md) shows each step on the platform, with screens.
