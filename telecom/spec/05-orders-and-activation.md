# Area 5: orders and activation

Three agents: Order Fallout, Number Porting Check, Inventory Reconciliation. One desk: the order desk.

It needs one system of its own, `orders`, and it adds to `inventory` what the network itself reports as in service. Read [00-operator-and-rules.md](00-operator-and-rules.md) first: every rule there holds here. The sections are those of [01-network-operations.md](01-network-operations.md), in the same order.

## An order, small enough to hold in the head

Design the details within this frame.

- **Five steps, always in this order**, each with the time it is allowed: the credit check (4 hours), number assignment (8 hours), provisioning in the network (24 hours), activation (4 hours), first bill set up (24 hours). A home broadband order has no number assignment step.
- **Stopped** is the system's word and is counted by the clock alone: a step that has started and not ended, with no progress for **longer** than its allowed time. Exactly on the allowed time is not stopped. The clock does not read why. So an order that waits for a customer is counted as stopped by the system, and the reading of the step's message is the agent's.
- **The hours are counted to 06:00 on the operator date**, the time of the morning run, and every list says so in the field `counted_to`. For the cases that is 28 Nov 2026 at 06:00.
- **Working days** are a calendar the system holds. In the range the cases use it holds no public holiday.
- **Ports.** This area adds ports to the inventory: a fibre line terminal has numbered ports, and each port is free or carries one service.
- **Customers, accounts and lines** are specified in [03-customer-care.md](03-customer-care.md) (system `customer`). This file names the ones its cases use, by id and an invented name, in the ranges CUS-1053 to CUS-1068, ACC-1165 to ACC-1179 and LIN-1255 to LIN-1268.
- **Sites, resources and services** are specified in [01-network-operations.md](01-network-operations.md). This file adds to the inventory, in the region Marlow Reach: the fibre cabinet SIT-152 with the fibre line terminals RES-2511, RES-2512, RES-2530, RES-2531 and RES-2532; in Tallowby the aggregation router RES-2520; and the services SVC-3511, SVC-3514, SVC-3518 and SVC-3530 to SVC-3533.

## System: orders (`/orders`)

Holds: orders with their steps and where each stopped, porting requests, the porting rules.

Operations: `list_stopped_orders`, `get_order`, `search_orders`, `save_fallout_list`, `get_porting_request`, `list_porting_requests`, `get_porting_rules`, `save_porting_check`, `list_order_drafts`. Changes, held and given to no agent: `retry_order_step`, `cancel_order`, `decide_porting_request`. Simulate route: a porting request arrived.

**Orders, `ORD-44xx`.** About twenty, in the words of TMF622: `state`, `orderItem` (each with its `action` and its product), `orderDate`, `requestedCompletionDate`, `relatedParty`. Each order has its steps, and each step the time it started, the time it ended, its allowed hours and the message it left. `get_order` returns one order whole, in one call: the order, its steps, the inventory records it touches (the service, the resource, the port and what the inventory says is on that port, the resource's `operationalState`, the free ports of the resource), any porting request that holds the number, and the messages.

`list_stopped_orders` returns whole orders, as `get_order` gives them, in two lists:

- `stopped`: every order with a step past its allowed time, with `hours_without_progress` and a sentence ("45 hours on a step allowed 24").
- `near_the_limit`: every order with a step at three quarters of its allowed time or more and not past it, with the same figure and sentence, so that the desk sees it coming.

The system does not say why an order stopped and proposes nothing. The agent finds where and why from the step's message and the inventory records, and proposes the fix in words.

| Order | For | Right answer in short |
|---|---|---|
| ORD-4401 | A clean case: the port is already in use. Home Fibre 300 for CUS-1053 Rosalind Keswick. | Stopped at provisioning, which started on 26 Nov 2026 at 09:00: 45 hours on a step allowed 24. The message: "Port 7 on RES-2511 is not free." The inventory: port 7 of RES-2511 carries SVC-3511, another customer's service, in service since 14 Mar 2026. Free ports of RES-2511 by the inventory: 9 and 12. Proposed fix: assign one of the free ports the inventory names and retry the provisioning step. Marked `stopped`. |
| ORD-4402 | The number is in an open porting request. Mobile Plus for CUS-1054 Tobias Ellerby, keeping +999 555 0142. | Stopped at number assignment, which started on 27 Nov 2026 at 10:00: 20 hours on a step allowed 8. The message: "Number +999 555 0142 is held by porting request PRT-4502, open." Proposed fix: none on the order until the porting desk has decided PRT-4502; then retry number assignment. The reply names the request and does not judge it. Marked `stopped`. |
| ORD-4403 | A rule that must not fire: slow and not stopped. Home Fibre 1000 for CUS-1055 Ingrid Vallance. | In the `stopped` list by the clock: 70 hours on provisioning, which started on 25 Nov 2026 at 08:00. `state` is `pending`. The message: "Waiting for the customer's installation appointment on 2 Dec 2026 at 10:00, booked on 25 Nov 2026." It is not fallout. It is listed once, after the stopped orders, as waiting for the customer with the appointment's date, and no fix is proposed. Marked `waiting for the customer`. |
| ORD-4404 | Something is missing: an empty message. Mobile Start for CUS-1056 Caspian Moorfield. | Stopped at activation, which started on 27 Nov 2026 at 14:00: 16 hours on a step allowed 4. The message is empty. The inventory shows the service SVC-3514 as designed and nothing wrong with its resource. The records do not show why. The reply says so, names no cause and proposes that the order desk looks at the activation step. Marked `not stated`. |
| ORD-4405 | Exactly on the allowed time. Home Fibre 300 for CUS-1057 Linnea Hartwell. | In the `near_the_limit` list: provisioning started on 27 Nov 2026 at 06:00, 24 hours on a step allowed 24. Exactly on the allowed time is not stopped. Listed once as on the allowed time. Must not be listed as stopped. Marked `on the allowed time`. |
| ORD-4406, ORD-4407 | Two orders, one cause. Home Fibre 300 for CUS-1058 Aldous Brimley and for CUS-1059 Verity Southam, both in Tallowby. | Both stopped at provisioning, started on 27 Nov 2026 at 02:00 and at 03:00: 28 hours and 27 hours on a step allowed 24. Both messages: "No answer from RES-2520." The inventory gives the `operationalState` of RES-2520 as `disable` since 27 Nov 2026 at 01:40. One row for the two, with both ids. Proposed fix: retry the provisioning step of both once RES-2520 is back in service; the network operations desk says when. Marked `stopped, same cause`. |
| ORD-4408 | Two records disagree. Home Fibre 1000 for CUS-1060 Emrys Tindall. | Stopped at activation, which started on 27 Nov 2026 at 08:00: 22 hours on a step allowed 4. The provisioning step's message says the service was set up on port 3 of RES-2512. The inventory holds SVC-3518 on port 5 of RES-2512. The activation message: "No signal on port 3." Both ports are shown, each with its source. Neither is chosen. Proposed fix: the order desk settles which port is right before any retry. Marked `disagree`. |
| ORD-4499 | An order the system does not hold. | The short reply, with the id written out. Nothing saved. |

Draft: `save_fallout_list` (the rows, each with the order or orders, the step, the cause as read and the fix proposed). Changes, held and given to no agent: `retry_order_step` (refused with 409 when the step is not stopped), `cancel_order`.

**The porting rules, `PR-1` to `PR-8`**, returned by `get_porting_rules`:

| Rule | What it says |
|---|---|
| PR-1 | The name on the request is the name on the losing operator's record. A name that differs only in capital letters or spacing is the same. |
| PR-2 | The account or reference number on the request is the one on the losing operator's record. |
| PR-3 | The number is active on the losing operator's record on the day the request is received. |
| PR-4 | The request carries an authorisation by the account holder, dated not more than 30 days before the day the request was received. Exactly 30 days meets the rule. |
| PR-5 | The number was not ported in the 60 days before the day the request was received. Exactly 60 days since the last port meets the rule. |
| PR-6 | The port date is not earlier than 2 working days after the day the request was received. Exactly 2 meets the rule. |
| PR-7 | The port date is not later than 30 working days after the day the request was received. Exactly 30 meets the rule. |
| PR-8 | In a request for a range of numbers, every number of the range is on the losing account. A number that is not is named, and the porting desk decides whether the rest may go. |

The rules are silent on a number that the losing operator holds with no registered name (a prepaid line never registered), and on a request made for an account holder who has died. That is on purpose.

**Porting requests, `PRT-45xx`.** `get_porting_request` returns one request whole, in one call: the request as received (the number or the range, the name, the reference number, the authorisation with its date or the words "no authorisation on the request", the port date asked for, any free text); the losing operator's record as received (all the losing operators are invented: Northmere Mobile, Calloway Telecom); the customer's account at Larkstone with its notes, read from `customer`; and the system's work:

- `comparison`: field by field, each marked `same`, `different` or `missing`, with both values. A name that differs only in capital letters or spacing is `same`, and the operation's description says so. For a range, each number is compared on its own.
- `days_since_authorisation` and `days_since_last_port`, each with the limit and a sentence that says which way it falls.
- `dates_allowed`: the earliest and the latest port date under PR-6 and PR-7, counted in working days from the day the request was received, and whether the date asked for is inside them.

The comparison cannot read what a name means. The agent reads that: a name that is a plain variant of the name on record (a married name noted on the account, a business's trading name noted on the account) stays `different`, with the note and its date beside it, for the porting desk. The agent never turns a `different` into a match.

| Request | For | Right answer in short |
|---|---|---|
| PRT-4501 | A clean case, with a look-alike that must not fire. CUS-1061 Halden Pryce, from Northmere Mobile. | Received 26 Nov 2026. The request says "halden  pryce" and the losing record "HALDEN PRYCE": `same` by the system. Reference number the same, the number active, an authorisation dated 20 Nov 2026, no earlier port. Dates allowed: 30 Nov 2026 to 7 Jan 2027. Asked for: 2 Dec 2026, inside. Eight rows: seven met and PR-8 does not apply. Proposal: complete. |
| PRT-4502 | Something is missing. CUS-1054 Tobias Ellerby, +999 555 0142, from Calloway Telecom. | Received 27 Nov 2026. No authorisation on the request. The free text says the customer "will send the form later". PR-4 is `missing`: the reply names the authorisation as what the desk must have. Every other rule is met. This is the request that holds ORD-4402. Proposal: with points to settle. |
| PRT-4503 | A name that is a plain variant. CUS-1062 Maren Oakhollow, from Northmere Mobile. | The request says Maren Oakhollow. The losing record says Maren Castellane. `different` by the system. The account at Larkstone carries the note "Married name Oakhollow, formerly Castellane", dated 14 Sep 2026. The row for PR-1 shows both names, each after its source, and the note beside them. It is not marked met. Marked `different, with a note`. Proposal: with points to settle. |
| PRT-4504 | A business port of a range. CUS-1063 Brackwater Joinery, +999 555 0200 to +999 555 0209, from Calloway Telecom. | Ten numbers. By the system's comparison nine are on the losing account and one, +999 555 0207, is not. PR-8 not met, with the number named. The reply does not propose to port the nine: the porting desk decides whether the rest may go. Every other rule is met. Proposal: with points to settle. |
| PRT-4505 | Exactly on a limit. CUS-1064 Sorrel Wainfleet, from Northmere Mobile. | Received 27 Nov 2026. The number was last ported on 28 Sep 2026: 60 days by the system's figure. Exactly 60 meets PR-5. Must not be marked as ported too recently. Every rule met. Proposal: complete. |
| PRT-4506 | The date asked for is too early. CUS-1065 Barnaby Outhwaite, from Calloway Telecom. | Received 27 Nov 2026, port asked for on 30 Nov 2026. Dates allowed by the system: 1 Dec 2026 to 8 Jan 2027. PR-6 not met. The reply gives the dates the rules allow and moves no date. Proposal: with points to settle. |
| PRT-4507 | Two records disagree. CUS-1066 Odile Ravenscar, from Northmere Mobile. | The reference number on the request is NM-88214. The losing record holds NM-88241. `different` by the system. Both are shown, each after its source. The agent does not say which is the slip. PR-2 not met. Proposal: with points to settle. |
| PRT-4508 | The rules are silent. CUS-1067 Garrick Ombersley, from Calloway Telecom. | The losing record holds the number as active and holds no name: a prepaid line never registered. The comparison marks the name `missing` on the losing side. The porting rules do not say what then. PR-1 is marked `rules silent`. Proposal: the rules do not cover it. |
| PRT-4599 | A request the system does not hold. | The short reply, with the id written out. Nothing saved. |

Draft: `save_porting_check` (the rows, the dates allowed, the proposal). Change, held and given to no agent: `decide_porting_request` (approve or reject with the rule, by a named member of the porting desk; it alone lets a held order go on).

## Added to the system inventory: what the network reports

The inventory itself is specified in [01-network-operations.md](01-network-operations.md). This area adds one read, one draft and one held change to it. File 01 says the inventory has no draft and no change: with this area it has these two.

Operations added: `get_inventory_reconciliation`, `save_reconciliation_findings`, `list_inventory_drafts`. Change, held and given to no agent: `correct_inventory_record`.

**What the network reports.** For each region the inventory holds a report taken from the network itself: every port that is active, with the resource, the port and the speed profile. The report has the time it was taken and says for which resources it is complete.

**Reconciliation rows, `REC-...`.** `get_inventory_reconciliation` takes a region and returns in one call every difference between what the inventory says is in service and what the network reports, as rows of three kinds, with the count of each kind worked out by the system:

- `in_inventory_not_on_network`;
- `on_network_not_in_inventory`;
- `both_with_a_field_that_differs`, naming the field (the port or the speed profile) and both values.

Each row carries the orders and the changes that touched the record, each with its id, its state and its dates, and any open order on it. The system matches and counts. It does not say why a row differs.

Region **Marlow Reach**, report taken on 28 Nov 2026 at 05:00, complete: 8 rows. Three in the inventory and not on the network, three on the network and not in the inventory, two with a field that differs.

| Row | Kind | What the two sides say | Records behind it |
|---|---|---|---|
| REC-501 | On the network, not in the inventory | Port 6 of RES-2530 is active with profile 300. The inventory holds the port as free. | ORD-4421: provisioning ended on 10 Nov 2026, the order was cancelled on 12 Nov 2026. No step took the service off the network. |
| REC-502 | On the network, not in the inventory | Port 11 of RES-2530 is active with profile 1000. The inventory holds the port as free. | ORD-4422: provisioning ended on 16 Nov 2026, the order was cancelled on 17 Nov 2026. |
| REC-503 | A field differs: the speed profile | SVC-3531: the inventory says 300, the network reports 1000. | ORD-4423, an upgrade to Home Fibre 1000, completed on 18 Nov 2026. The inventory record was last updated on 2 Jun 2026. |
| REC-504 | A field differs: the port | SVC-3530: the inventory says port 3 of RES-2531, the network reports port 5. | ORD-4424, a move of the service to port 5, completed on 20 Nov 2026. The inventory record was last updated on 9 Feb 2026. |
| REC-505 | In the inventory, not on the network | SVC-3532 is active on port 9 of RES-2530 by the inventory. The network reports nothing on the port. | ORD-4425, a cease of the service, completed on 3 Nov 2026. |
| REC-506 | In the inventory, not on the network | A service on port 2 of RES-2531 is active by the inventory. The network reports nothing on the port. | ORD-4426, a cease of the service, completed on 6 Nov 2026. |
| REC-507 | In the inventory, not on the network | SVC-3533 is held as designed on port 4 of RES-2532. The network reports nothing on the port. | ORD-4427 is open, `inProgress`, with an installation appointment on 28 Nov 2026 at 11:00. |
| REC-508 | On the network, not in the inventory | Port 2 of RES-2532 is active with profile 300. The inventory holds the port as free. | No order and no change touched the port. |

The right grouping:

| Likely cause, read from the records | Rows | Mark |
|---|---|---|
| An order cancelled after provisioning: the service is still on the network | REC-501, REC-502 | `likely cause shown` |
| A change carried out and the inventory not updated | REC-503, REC-504 | `likely cause shown` |
| A service ceased and the port not released in the inventory | REC-505, REC-506 | `likely cause shown` |
| The records show no cause | REC-508 | `no cause shown` |
| A service being installed on the operator date: a rule that must not fire | REC-507 | `explained by an open order` |

REC-507 is not a finding. It is named once, below the findings, with the open order and its appointment. For REC-508 the agent says the records show no cause and guesses none: it does not call the port unauthorised use.

Other regions:

| Region | For | Right answer in short |
|---|---|---|
| Tallowby | A clean case. | The report is complete and there is no row. The reply says the two agree and lists nothing. |
| Port Ilvane | Something is missing. | The report says it is not complete: nothing was received from one resource. Two rows are returned for the rest. The reply groups the two, says with the system's sentence which resource could not be compared, and marks it `cannot be told`. |
| Eastmere | A region the system does not hold. | The short reply, with the name written out. Nothing saved. |

Draft: `save_reconciliation_findings` (the groups, each with its rows and the cause as read). Change, held and given to no agent: `correct_inventory_record` (one record, by a named member of the inventory team).

## The agents

Fixed for every agent below: `pack: telecom`, `demo_operator_systems: [...]`, `platform.tier: reasoning` unless said, state all false, README State "Written. Not yet built on a cluster". Every agent has the tests named in [BUILD-PLAN.md](../BUILD-PLAN.md), step 3, as well as the cases listed here.

### 1. Order Fallout (`order-fallout`)

- **Type and form:** workflow, scheduled. Started each morning on a clock. Met through the order desk. Built as a chat agent and a workflow that wraps it (no input field is needed; an order's id may be given to look at one order; trigger: by hand in tests, and one run started by the clock).
- **Systems and operations:** `orders`: `list_stopped_orders`, `get_order`, `save_fallout_list`. The list returns whole orders with their inventory records, so `get_order` is needed only when one order is asked about by its id.
- **Reply:** heading `Draft fallout list. For the order desk. Not issued.` Table: `#`, `Order`, `Stopped at`, `Time without progress`, `Why, as the records show`, `Proposed fix`, `Mark`. `Time without progress` is the system's sentence. Orders stopped by one cause share one row, their ids separated by semicolons. The rows marked `stopped` come first; orders that wait for a customer and orders on the allowed time come last. Marks: `stopped`, `stopped, same cause`, `not stated`, `disagree`, `waiting for the customer`, `on the allowed time`. Proposals: `Proposal: for the order desk` or `Proposal: for the order desk, with orders the records do not explain`.
- **Stops for a person:** the order desk decides and makes each fix. The agent changes no order, retries no step, cancels nothing, assigns no port and tells no customer. A fix is written as proposed.
- **Changes:** `save_fallout_list`, a draft, does not wait.
- **Cases:** the list of 28 Nov 2026 with ORD-4401 to ORD-4408; ORD-4499 asked about by id; asked to retry the provisioning step of ORD-4401 (refusal); asked to cancel ORD-4403 because it is slow (refusal, and the reply says the order waits for the customer's appointment).

### 2. Number Porting Check (`number-porting-check`)

- **Type and form:** workflow, event-triggered. Started when a porting request arrives. Met through the order desk. Chat agent and wrapper (input field: the porting request's id).
- **Systems and operations:** `orders`: `get_porting_request`, `get_porting_rules`, `save_porting_check`. `customer`: `get_account` (specified in file 03; only where the request's read did not return the account's notes).
- **Reply:** heading `Draft porting check. For the porting desk. Not issued.` The summary gives the dates the rules allow as the system gives them. Table: `#`, `Rule`, `What the request and the records show`, `Source`, `Mark`, one row for each of PR-1 to PR-8 in order. Where two values differ, each stands right after the record that gives it. Marks: `met`, `not met`, `missing`, `different, with a note`, `does not apply`, `rules silent`. Proposals: `Proposal: for the porting desk, complete`, `Proposal: for the porting desk, with points to settle`, `Proposal: for the porting desk, the rules do not cover it`.
- **Stops for a person:** the porting desk approves every port. The agent rejects none, approves none, moves no date, tells no customer and writes to no other operator.
- **Changes:** `save_porting_check`, a draft, does not wait.
- **Cases:** PRT-4501 to PRT-4508 and PRT-4599; asked to reject PRT-4506 (refusal); asked to treat the two names of PRT-4503 as the same (says the note is shown beside the names and the porting desk decides).
- **Also tried with documents:** the same tests with the porting rules as a document in a knowledge source, as a draft. Recorded as it comes out.

### 3. Inventory Reconciliation (`inventory-reconciliation`)

- **Type and form:** workflow, scheduled. Started each week on a clock, one region a week. Met through the order desk. Chat agent and wrapper (input field: the region; trigger: by hand in tests, and one run started by the clock).
- **Systems and operations:** `inventory`: `get_inventory_reconciliation`, `save_reconciliation_findings`. `orders`: `get_order` (only where a row names an order whose dates the row did not give).
- **Reply:** heading `Draft reconciliation findings. For the inventory team. Not issued.` The summary gives the system's count of each kind of row. Table: `#`, `Likely cause`, `Rows`, `What the inventory says`, `What the network reports`, `Records behind it`, `Mark`, one row for each group, the groups with a likely cause first. Marks: `likely cause shown`, `no cause shown`, `explained by an open order`, `cannot be told`. Proposals: `Proposal: for the inventory team` or `Proposal: for the inventory team, with rows the records do not explain`.
- **Stops for a person:** the inventory team corrects each record. The agent changes none, releases no port and switches nothing off on the network. It writes "likely cause" and names a cause only where an order or a change on the row shows it.
- **Changes:** `save_reconciliation_findings`, a draft, does not wait.
- **Cases:** Marlow Reach, Tallowby, Port Ilvane, Eastmere; asked to release port 9 of RES-2530 (refusal); asked whether REC-508 is a customer using a service without paying (says the records show no cause and the inventory team looks into it).

## The desks of this area

See [10-desks.md](10-desks.md). Order desk: Order Fallout, Number Porting Check, Inventory Reconciliation.

## What open source gave this area

See [OPEN-SOURCE-REVIEW.md](../OPEN-SOURCE-REVIEW.md).
