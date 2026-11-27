# Insurance pack

31 agents an insurer can build on the Katonic platform, and the desks people use them through. They are written against one invented company, Thornmere Mutual Insurance: motor, home, commercial property and group medical cover in the invented country Meridia.

**Status: work in progress.** The State column says where each one stands. "Planned" means the folder is not written yet. Nine agents are built on a development cluster and pass every test five runs in a row: six of the seven claims agents and the three health claims agents. The seventh claims agent is built and one of its tests is not finished.

Every agent follows one rule: it prepares the work, and a person makes the decision. No agent accepts cover, declines a claim, pays, sends a letter or contacts a customer. A tool that changes something waits for approval unless the insurer has decided otherwise for that tool.

## Three things to know before you read the tables

- **"Workflow" says how the agent is meant to be started, not how it is built here.** An agent marked "Workflow, event-triggered" or "Workflow, scheduled" is built in this pack as a chat agent, and in its tests a person sends the message. Where an event or a clock has really started an agent on a cluster, its State says so. Where it has not, it has not been tried.
- **Wordings and documents are records here.** A real insurer keeps policy wordings, tables of benefits and claim documents as files, many of them scanned. The invented insurer serves them as clean text with numbered clauses, so that an agent can be tried before any document store is connected. Where an agent has also been tried with the wording as a document in a knowledge source, its State says so, with the result as it was.
- **The system does the sums.** Days between dates, whether a policy was in force, limits, deductibles and totals come from the insurer's systems. The agent's work is the reading: which clause bears on the facts, which invoice line the wording does not cover, what is missing, where two records disagree.

## The agents

| # | Agent | What it does | Type and form | How people meet it | State |
|---|---|---|---|---|---|
| | **Claims intake** | | | | |
| 1 | [First Notice of Loss Intake](agents/first-notice-of-loss-intake/README.md) | Takes a new loss report, finds the policy, checks it was in force on the date of the loss, prepares the claim file and lists what is missing | Workflow, event-triggered | Claims intake desk | Built on a development cluster. Six of seven tests pass five runs in a row. The step that registers a claim did not wait for approval there, so the seventh test is not finished |
| 2 | [Claims Processing](agents/claims-processing/README.md) | Sorts a new claim by the handling guide's rules so it reaches the right team, with the reason | Workflow, event-triggered | Claims intake desk | Built on a development cluster. All eight tests pass five runs in a row |
| 3 | [Claim Pack Completeness](agents/claim-pack-completeness/README.md) | Compares a claim's documents with the checklist for its type and lists what is missing, unreadable or does not show what it must | Workflow, event-triggered | Claims intake desk | Built on a development cluster. All eight tests pass five runs in a row |
| 4 | [Claim Summary](agents/claim-summary/README.md) | Writes the summary an adjuster reads first: the loss, the cover, the documents, the open points, each with its source | Workflow, API | Claims intake desk | Built on a development cluster. All eight tests pass five runs in a row |
| | **Claims assessment** | | | | |
| 5 | [Coverage Check](agents/coverage-check/README.md) | Sets the loss against the policy wording, clause by clause, and says where the wording is silent | Workflow, API | Claims assessment desk | Built on a development cluster. All ten tests pass five runs in a row, with the wording as numbered clauses. With the wording as PDF files in a knowledge source it quoted every clause exactly but its save was refused in every run: not passed in that form |
| 6 | [Settlement Calculation](agents/settlement-calculation/README.md) | Says which invoice lines the wording does not cover and shows the amount payable, line by line | Workflow, API | Claims assessment desk | Built on a development cluster. All eight tests pass five runs in a row |
| 7 | [Claims Correspondence](agents/claims-correspondence/README.md) | Drafts the letter to the claimant from the claim file and the insurer's templates | Conversational, acting | Claims assessment desk | Built on a development cluster. All nine tests pass five runs in a row; the Arabic letter is not yet read by a reader of Arabic |
| 8 | [Claims Leakage Review](agents/claims-leakage-review/README.md) | Reviews closed claims against the handling standards and lists those paid outside them | Workflow, scheduled | Sent to the claims quality team | Written. Not yet built on a cluster |
| | **Fraud** | | | | |
| 9 | [Fraud Detection](agents/fraud-detection/README.md) | Checks a claim against the insurer's own indicators and the claimant's history and flags it with reasons, before payment | Workflow, event-triggered | Investigations desk | Written. Not yet built on a cluster |
| 10 | [Investigation Case File](agents/investigation-case-file/README.md) | Builds the case file for a flagged claim: earlier claims by the same parties, links between them, public reporting | Autonomous | Investigations desk | Written. Not yet built on a cluster |
| | **Underwriting** | | | | |
| 11 | [Underwriting Support](agents/underwriting-support/README.md) | Reads a broker's submission and prepares the file: within guidelines, outside, missing | Workflow, event-triggered | Underwriting desk | Written. Not yet built on a cluster |
| 12 | [Risk Appetite Check](agents/risk-appetite-check/README.md) | Says in a sentence whether a risk is within appetite and which rule says so | Conversational, answering | Chat | Written. Not yet built on a cluster |
| 13 | [Underwriting Referral Memo](agents/underwriting-referral-memo/README.md) | Drafts the referral memo: the risk, the terms, the rule that forced the referral, the precedents | Workflow, API | Underwriting desk | Written. Not yet built on a cluster |
| 14 | [Renewal Review](agents/renewal-review/README.md) | Sets expiring terms beside the period's claims and the changes in the risk | Workflow, scheduled | Underwriting desk | Written. Not yet built on a cluster |
| | **Policy servicing and distribution** | | | | |
| 15 | [Policy Servicing](agents/policy-servicing/README.md) | Prepares a mid-term change for staff: the rule it touches, the premium adjustment and any gap in cover | Conversational, acting | Policy servicing desk | Written. Not yet built on a cluster |
| 16 | [Certificate and Endorsement Preparation](agents/certificate-and-endorsement-preparation/README.md) | Prepares the certificate or endorsement from the policy as it stands, and says where the request asks for something the policy does not give | Workflow, event-triggered | Policy servicing desk | Written. Not yet built on a cluster |
| 17 | [Broker Query](agents/broker-query/README.md) | Answers a broker's question on a policy or a claim, with the source | Conversational, acting | Chat | Written. Not yet built on a cluster |
| 18 | [Member Policy Q&A](agents/member-policy-qa/README.md) | Answers a member's question on their own cover: covered, covered with conditions, not covered, needs a person | Conversational, answering | Chat | Built on a development cluster. Thirteen of fourteen tests pass five runs in a row; the fourteenth has four passing runs and one run still to make |
| | **Health claims** | | | | |
| 19 | [Pre-authorisation Preparation](agents/pre-authorisation-preparation/README.md) | Sets a request against the member's benefits and the medical policy: met, not met, missing | Workflow, event-triggered | Health claims desk | Built on a development cluster. All ten tests pass five runs in a row |
| 20 | [Medical Claims Adjudication Support](agents/medical-claims-adjudication-support/README.md) | For a held claim: why it was held, what the assessor needs, a suggested determination with reasons | Workflow, event-triggered | Health claims desk | Built on a development cluster. All ten tests pass five runs in a row |
| 21 | [Provider Invoice Check](agents/provider-invoice-check/README.md) | Checks a provider's invoice line by line against the tariff and the contract | Workflow, API | Health claims desk | Built on a development cluster. All nine tests pass five runs in a row |
| | **Compliance and conduct** | | | | |
| 22 | [Compliance Audit](agents/compliance-audit/README.md) | Checks policy, claims and sales files against the insurer's own rules and records what it checked | Workflow, scheduled | Sent to compliance | Written. Not yet built on a cluster |
| 23 | [Regulatory Monitoring](agents/regulatory-monitoring/README.md) | Reads the regulators the insurer names and maps each change to the obligations register | Workflow, scheduled | Regulatory change desk | Written. Not yet built on a cluster |
| 24 | [Complaint Handling](agents/complaint-handling/README.md) | Classifies a complaint, gathers the policy and claim history, drafts the response and the log entry | Workflow, event-triggered | Complaints desk | Written. Not yet built on a cluster |
| 25 | [Litigation Support](agents/litigation-support/README.md) | Sorts the documents of a disputed claim and flags what may be privileged | Autonomous | Sent to the lawyers | Written. Not yet built on a cluster |
| | **Product and pricing** | | | | |
| 26 | Product Change Analyst | Takes a proposed product change and returns what it touches and the questions it cannot answer | Conversational, answering | Chat | Planned |
| 27 | Pricing Analyst | Works out the premium that holds a target loss ratio and shows the calculation | Conversational, answering | Chat | Planned |
| 28 | Risk Profiling | Answers questions on portfolio exposure from the warehouse and shows the query it ran | Conversational, answering | Chat | Planned |
| | **Reinsurance and finance** | | | | |
| 29 | Bordereaux Check | Checks a bordereau against the treaty or binder terms | Workflow, event-triggered | Reinsurance desk | Planned |
| 30 | Treaty Recovery | Lists paid claims that reach a treaty's attachment point with no recovery raised | Workflow, scheduled | Reinsurance desk | Planned |
| | **Partners** | | | | |
| 31 | Partner Quality | Checks administrators, repair networks and suppliers against service levels and credentials | Workflow, scheduled | Sent to the supplier manager | Planned |

## The desks

A desk is the shared case desk ([katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk)) with a different queue. Each one shows the cases, the agent's findings and draft, approve or send back, and a register of who decided what.

| Desk | Agents behind it | Who decides | State |
|---|---|---|---|
| [Claims intake desk](desks/claims-intake/README.md) | First Notice of Loss Intake, Claims Processing, Claim Pack Completeness, Claim Summary | Claims handler | Settings written and tested end to end against a stand-in agent. Runs on the engine's `main` |
| [Claims assessment desk](desks/claims-assessment/README.md) | Coverage Check, Settlement Calculation, Claims Correspondence | Adjuster | Settings written and tested end to end against a stand-in agent. Runs on the engine's `main` |
| [Investigations desk](desks/investigations/README.md) | Fraud Detection, Investigation Case File | Investigator | Settings written and tested end to end against a stand-in agent. Runs on the engine's `main` |
| [Underwriting desk](desks/underwriting/README.md) | Underwriting Support, Underwriting Referral Memo, Renewal Review | Underwriter | Settings written and tested end to end against a stand-in agent. Runs on the engine's `main`. One gap: the note of a submission row is not drawn |
| [Policy servicing desk](desks/policy-servicing/README.md) | Policy Servicing, Certificate and Endorsement Preparation | Servicing officer | Settings written and tested end to end against a stand-in agent. Runs on the engine's `main` |
| [Health claims desk](desks/health-claims/README.md) | Pre-authorisation Preparation, Medical Claims Adjudication Support, Provider Invoice Check | Clinician or assessor | Settings written and tested end to end against a stand-in agent. Runs on the engine's `main`. One gap: the clause of an invoice line is not drawn in the row |
| Complaints desk | Complaint Handling | Complaints officer | Planned |
| Reinsurance desk | Bordereaux Check, Treaty Recovery | Reinsurance accountant | Planned |

## A short way in

Three agents show the pack in a quarter of an hour, against the invented insurer:

1. **Coverage Check** on claim `CLM-4004`: a car driven off from a petrol station with the key in the ignition. The wording says nothing about a key left in a vehicle. The agent says so and sends the point to the adjuster.
2. **Settlement Calculation** on claim `CLM-4001`: four repair lines. One is not covered, one is over a limit, the deductible comes off, and the working is shown.
3. **Claim Pack Completeness** on claim `CLM-4005`: a police report is missing, and the repair estimate names a different car.

## How an agent reaches an insurer's systems

1. **An imported API.** The insurer gives the platform the OpenAPI file of an API it already runs, and each operation becomes a tool.
2. **An MCP server** from the Catalog, running inside the insurer's own cluster.
3. **A knowledge source.** Wordings, tables of benefits, guidelines and procedures, indexed with each reader's permissions kept.
4. **A file the user uploads** in the conversation.

To try an agent before your own systems are connected, run the invented insurer in [`demo-insurer/`](../demo-insurer/README.md). It offers the first two routes, and [its scenario list](../demo-insurer/SCENARIOS.md) gives the right answer for every case.

## Where the designs come from

The agents and desks are our own. Three public claims applications were read in code for ideas, and no code or sample data was taken from them: Microsoft's content processing accelerator (MIT), and two claims samples from AWS (MIT-0). From them come three ideas used here: a finding is a missing document, two records that disagree, or a point worth a look; the working table comes first and the conclusion is written from it; and every case set includes one where a rule must not fire.
