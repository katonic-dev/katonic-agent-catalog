# The desks

Eight desks. Each is a settings folder for the shared case desk, [katonic-case-desk](https://github.com/katonic-dev/katonic-case-desk): `desk.config.json`, `cases.json`, `demo-replies.json` and a `README.md`, under `telecom/desks/<desk>/`. The insurance desks in this repository are the model, and [BUILD-PLAN.md](../BUILD-PLAN.md), step 4, says how a desk is built and checked.

A desk shows a queue of cases. Opening a case shows the source on one side (the ticket, the request, the complaint) and the agent's review on the other: the summary, the table of findings read by its header, any long writing, and the proposal. The person approves, sends back with a reason, or closes with no action. A register keeps who decided what and when.

Read [00-operator-and-rules.md](00-operator-and-rules.md), "The reply shape of an agent behind a desk", first. The desk reads that shape and nothing else.

## What holds for every desk

- **A kind of case for each agent.** A desk with three agents has three kinds, each with its own instruction to the agent, its own table columns and marks, and its own decisions.
- **The message the desk sends** is the plain message a person would send, with the case's id: "Check change request CHG-9003 against the change rules." The same message is the agent's test input.
- **The decision is the person's.** Approve never does the thing itself. It records the decision in the register. Where the operator has a change operation for the decision (`record_change_decision`, `decide_sim_swap`), the desk does not call it in this pack: the README says so.
- **Marks have tones.** Met, related, inside the term, recorded: quiet. Worth a look, not stated, missing, cannot be told: amber. Not met, disagree, term missed: red. Rules silent: amber, with the words "a person decides".
- **The cases** in `cases.json` are the cases of the area files, by their ids, and the stand-in replies in `demo-replies.json` are the right answers of SCENARIOS.md in the agent's reply shape.
- **Every desk has one case of each outcome**: a case that goes straight through, one that goes back, one where the agent says the rules are silent, and one the system does not hold.
- **Gaps are written down.** Where the engine cannot draw something a case needs, the desk's README and the index say so in one line, and the engine is not changed for it.

## The desks

### Network operations desk (`network-operations`)

| Kind | Agent | Opens with | Who decides | Decisions |
|---|---|---|---|---|
| Ticket | Trouble Ticket Enrichment | the trouble ticket with its notes | The engineer who owns the ticket | Add to the ticket; send back; no action |
| Incident review | Post-incident Review | the incident with its bridge notes | The incident manager | Accept the draft; send back; no action |
| Fault | Fault Diagnosis | the service's fault view | The support engineer | Take the next step; send back; no action |
| Security alert | Network Security | the alert with its log lines | The security team | Open an investigation; close as known; send back |

Queue order: severity, then the time the case arrived. Register: case, kind, proposal, decision, who, when, the reason where sent back. The incident review shows the long writing (the seven sections) under the table. Cases: TT-6001 to TT-6006, INC-8001 to INC-8004, and the cases of [02](02-fraud-and-security.md) and [07](07-service-assurance-and-field.md) for the other two kinds.

### Change desk (`change`)

| Kind | Agent | Opens with | Who decides | Decisions |
|---|---|---|---|---|
| Change review | Change Request Review | the change request with its method of procedure and rollback plan | The change board | Put to the board as complete; back to the requester; to the change manager |
| Planned work notices | Planned Work Notification | the approved change with what it affects | The service manager | Send the notices; send back; no notice needed |

Queue order: planned start time. The change review shows nine rows, one for each rule, always in order. The notices kind shows each notice as long writing under the table. Cases: CHG-9001 to CHG-9012.

### Fraud desk (`fraud`)

| Kind | Agent | Who decides | Decisions |
|---|---|---|---|
| Flagged account | Fraud Detection | The fraud team | Open a case; watch; no action |
| SIM swap | SIM Swap Check | A member of staff | Approve the swap; refuse; ask the customer |
| Scam reports | Scam Report Triage | The fraud team | Submit the blocking request; send back; no action |

Queue order: SIM swaps first, by the time the request arrived. A SIM swap is the desk's time-bound kind: the queue shows how long each has waited.

### Customer care desk (`customer-care`)

| Kind | Agent | Who decides | Decisions |
|---|---|---|---|
| Complaint | Complaint Handling | The complaints officer | Send the response; send back; pass to the ombudsman's contact |
| Contact note | Contact Summary | The care agent who took the contact | Save the note to the case; correct and save; discard |
| Bill dispute | Bill Dispute Investigation | Billing staff | Credit in full; credit in part; no credit; ask the customer |

Queue order: complaints by the date the final response is due, as the system gives it. If the engine cannot sort by a date in the case, list the cases in that order by hand and say so. The complaint kind shows the draft response as long writing.

### Order desk (`orders`)

| Kind | Agent | Who decides | Decisions |
|---|---|---|---|
| Stopped order | Order Fallout | The order desk | Take the proposed fix; send back; cancel with the customer |
| Porting request | Number Porting Check | The porting desk | Approve the port; reject; ask the customer |
| Inventory difference | Inventory Reconciliation | The inventory team | Correct the record; send back; no action |

Stopped orders that share a cause open as one case with the orders listed.

### Revenue assurance desk (`revenue-assurance`)

| Kind | Agent | Who decides | Decisions |
|---|---|---|---|
| Bill cycle | Billing & Revenue | The revenue assurance team | Raise corrections; send back; no action |
| Settlement statement | Settlement Reconciliation | The settlement analyst | Dispute the rows marked; accept the statement; send back |

Each case is a table of differences with both figures in every row. The desk adds up nothing: totals are the system's.

### Business desk (`business`)

| Kind | Agent | Who decides | Decisions |
|---|---|---|---|
| Quote | Enterprise Quote Preparation | The account manager and the pricing desk | Send to pricing; send back; ask the customer |
| Tender | Tender Response | The bid manager | Accept the answers; send back; no bid |
| Service report | Service Level Report | The service manager | Send the report; send back |

The tender kind shows one row for each question, with the source id of each answer and "no source" where nothing answers.

### Compliance desk (`compliance`)

| Kind | Agent | Who decides | Decisions |
|---|---|---|---|
| Return | Regulatory Return Preparation | The compliance officer | Submit; send back |
| Data subject request | Data Subject Request | The privacy officer | Release; erase; send back; refuse with a reason |

Queue order: the date each is due, as the system gives it.

Regulatory Monitoring uses the regulatory change desk the catalog already has, with the operator's two regulators and its obligations register. It gets a settings folder `telecom/desks/regulatory-change/` and no new kind.

## What is not a desk

Five agents are met in chat (Bill Explanation, Plan and Product Q&A, Runbook Q&A, Policy and Procedure Q&A, Field Operations), and four send their result to a team (Churn Prediction, Network Optimization, Predictive Maintenance, Wholesale Agreement Review). Fault Diagnosis is met both ways. Every workflow agent, behind a desk or not, can also be started from Work Room, Automations.
