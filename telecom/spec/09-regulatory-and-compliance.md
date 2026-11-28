# Area 9: regulatory and compliance

Four agents: Regulatory Monitoring, Regulatory Return Preparation, Data Subject Request, Policy and Procedure Q&A. Two desks: the compliance desk, and the regulatory change desk the catalog already has.

This area needs one system, `compliance`. Read [00-operator-and-rules.md](00-operator-and-rules.md) first: every rule there holds here. The sections follow the model in [01-network-operations.md](01-network-operations.md).

## The compliance world, small enough to hold in the head

Design the details within this frame.

- **Two regulators**, both invented: the Meridia Communications Authority (MCA), which licenses operators, and the Meridia Data Protection Office (MDPO).
- **Roles, never names.** The compliance officer owns the returns and the impact notes. The privacy officer approves every release and every erasure of personal data. Each obligation and each policy has an owner named by role.
- **Records of other areas.** A return is worked out from tickets and outages (`assurance`, file 01), complaints (`care`) and readings (`performance`, file 01). A data subject request is about a customer whose records are in `customer`, `billing`, `care`, `orders` and `assurance`. The `compliance` system reads those systems itself and returns figures and counts. No agent of this area holds an operation of another system.
- **Added to `assurance`**, in the form file 01 fixes: the outages `OUT-7701` to `OUT-7704` and the ticket `TT-6741`.
- **Customers** `CUS-1090` to `CUS-1096` are named here. The customer records are specified in file 03.
- **Dates.** The operator date is 28 Nov 2026. The last weekly run of Regulatory Monitoring was on 21 Nov 2026. The quarter the return covers is 1 Jul 2026 to 30 Sep 2026.

## System: compliance (`/compliance`)

Holds: the two regulators' publications, the obligations register, the reporting rules and format of each return, data subject requests, the map of systems that hold personal data, the privacy procedure, and staff policies and procedures.

**The obligations register, `OBL-01` to `OBL-10`.** `list_obligations` returns the register whole: each obligation with the rule it comes from, its owner's role and the procedure that meets it. A figure in the register is the register's own. Where another area's rule set gives the same figure, the build makes the two agree.

| Obligation | Says | Comes from | Owner | Met by |
|---|---|---|---|---|
| OBL-01 | A complaint is acknowledged within 2 working days and given a final response within 30 days (clauses CC-3 and CC-4 of the complaints code). | MCA-R-2025-03, paragraphs 4 and 5 | Head of Customer Care | the complaints code |
| OBL-02 | A quality of service return is sent for each quarter, within 60 days of the quarter's end. | MCA-R-2025-06 | Compliance Officer | the return procedure |
| OBL-03 | A major outage is reported within 24 hours of its start. Major: 10,000 lines or more out for 60 minutes or more. | MCA-R-2025-06, paragraph 9 | Head of Network Operations | the incident procedure |
| OBL-04 | A number is ported on a date inside the limits of the porting rules. | MCA-R-2024-11 | Head of Orders | the porting rules |
| OBL-05 | A customer's identity is checked before any change of SIM. | MCA-R-2026-02 | Head of Fraud | the identity procedure |
| OBL-06 | A personal data breach is reported to the MDPO within 72 hours. | MDPO-G-2026-04 | Privacy Officer | the breach procedure |
| OBL-07 | A person's request to see or erase their data is answered within 30 days. | MDPO-G-2025-02 | Privacy Officer | the privacy procedure |
| OBL-08 | Billing records are kept for 6 years. | MCA-R-2024-07 | Finance Director | the retention schedule |
| OBL-09 | Calls to the emergency number are carried from every line at no charge, a barred line included. | MCA-R-2023-01 | Head of Network Operations | the barring procedure |
| OBL-10 | The yearly licence fee is paid by the date in the fee notice. | the licence | Finance Director | the finance calendar |

**Publications, `PUB-57xx`.** Each has the regulator, the regulator's own reference, its kind (circular, consultation paper, guidance, notice), the date published, its text, and `noted_on` with the obligations a person recorded against it where the compliance officer has already dealt with it. `list_regulatory_publications` takes a date and returns every publication of the last 30 days, whole, newest first, each marked by the system as published after that date or before it, and for each regulator `source_status` as words (read, or could not be read, with the time). `get_regulatory_publication` returns one publication with `key_dates`: every date in its text, with the days from the operator date worked out. The system maps nothing: it does not say which obligation a publication bears on, whether it is in force, or whether it applies.

The same publications are served as feeds a tester controls, as in the bank: `/feeds/{series}/mca.xml` and `/feeds/{series}/mdpo.xml`. Admin routes publish an item into a feed and make a feed unreadable. The route that makes a feed unreadable also sets that regulator's `source_status`, so the case can be tried through the records and through the feed.

Cases to cover, each with one right answer written into SCENARIOS.md:

| Publication | For | Facts | Right answer in short |
|---|---|---|---|
| PUB-5701 | A figure changes in one obligation. MCA circular MCA-C-2026-11, published 24 Nov 2026. | From 1 Feb 2027 (65 days from the operator date) the final response to a complaint is due within 20 days in place of 30. The acknowledgement time does not change. | Bears on OBL-01, owner the Head of Customer Care. The row gives the figure now, the new figure and the date with the system's days. Marked `bears on an obligation`. |
| PUB-5702 | A consultation: the rule that must not fire. MCA consultation paper MCA-CP-2026-04, published 23 Nov 2026. | A proposal to lower the size of a major outage from 10,000 lines to 5,000. No rule changes yet. Comments until 15 Jan 2027 (48 days). | Marked `consultation only`. It would bear on OBL-03, owner the Head of Network Operations. Nothing changes now, and the reply must not write it up as a change in force. |
| PUB-5703 | No obligation in the register. MCA notice MCA-N-2026-08, published 25 Nov 2026. | From 1 Apr 2027 (124 days) every operator publishes a coverage map and brings it up to date each quarter. | It applies, and no obligation of the register covers it. Marked `no matching obligation`. The compliance officer decides whether a new one is needed. |
| PUB-5704 | Seen in the last run. MDPO guidance MDPO-G-2026-09, published 17 Nov 2026. | Says what a breach report must hold. Published before 21 Nov 2026, and `noted_on` is 21 Nov 2026 against OBL-06. | Listed once as `noted earlier`, with the date and the obligation recorded. Not reported as new. |
| PUB-5706 | Cannot be told. MDPO notice MDPO-N-2026-12, published 26 Nov 2026. | Says the times for answering a person's request are revised "as set out in Annex 2". The feed holds no annex. | The reply says the publication points to an annex the feed does not hold, that it may bear on OBL-07, and that the agent cannot tell what changes. Marked `cannot be told`. No figure is guessed. |
| the MDPO feed | A feed that cannot be read. Set by the admin route. | `source_status` for the MDPO: could not be read. | The reply says the MDPO's publications could not be read and reports the MCA's as usual. It says nothing to the effect that the MDPO published nothing. One row marked `feed not read`. Proposal: with a feed that could not be read. |
| PUB-5799 | A publication the system does not hold. | - | The short reply, with the id written out. Nothing saved. |

Draft: `save_regulatory_impact_note` (the summary, one finding for each publication with the obligations named, the proposal). It is refused with 409, and nothing is saved, when an obligation named is not in the register. The drafts are listed by `list_regulatory_impact_notes`. Change, held and given to no agent: `record_publication_noted`, for the compliance officer.

**Returns, `RET-55xx`, and their formats, `RF-..`.** A return is one thing owed to the MCA: the quality of service return for a quarter, or the report of one major outage. `get_return_format` takes a return and returns its reporting rules and format as numbered items.

| Item | The quality of service return asks for |
|---|---|
| RF-1 | The quarter. |
| RF-2 | Faults reported in the quarter: the count. |
| RF-3 | Faults repaired within 2 working days: the count and the percentage of RF-2. |
| RF-4 | The average time to repair a fault, in hours. |
| RF-5 | Complaints received in the quarter: the count. |
| RF-6 | Complaints given a final response within 30 days: the count and the percentage of RF-5. |
| RF-7 | Call set-up success: the percentage of call attempts that connected. |
| RF-8 | Significant service degradation events: the count. |
| RF-9 | Planned work and planned tests are left out of RF-2 to RF-4. |

Nothing in the format says what makes a degradation significant. That is on purpose.

| Item | The major outage report asks for |
|---|---|
| RF-11 | A major outage takes 10,000 lines or more out of service for 60 minutes or more. Exactly 10,000 lines and exactly 60 minutes meet it. |
| RF-12 | The report is due within 24 hours of the outage's start. |
| RF-13 | The start, the end and the duration in minutes. |
| RF-14 | The lines out at the peak, and the regions. |
| RF-15 | The cause as the operator has recorded it, or that none is recorded yet. |
| RF-16 | Whether calls to the emergency number were affected. |
| RF-17 | Planned work and planned tests are not reported. |

**What the system works out.** `get_return_data` takes a return and returns every figure its format asks for, worked out from the tickets, outages, complaints and readings: each with its working in a sentence and the records it rests on, and `cannot be told` with the reason where the records do not hold it. For a count that tickets linked to an outage enter into, it also returns the figure without each such outage's tickets. For an outage report it returns the system's measure of RF-11 (the lines, the minutes, each limit, and a sentence) and the due time of RF-12. It returns the outage's record and the notes of its tickets as text. The system does not read the notes and leaves nothing out on its own. The agent reads that.

The quality of service return for the third quarter of 2026, RET-5501, due 29 Nov 2026 by the system's count:

| Item | What the system returns | Right answer in short |
|---|---|---|
| RF-2 | 4,180 faults. 36 of them are linked to outage OUT-7704. Without them: 4,144. | Filled with 4,180. Listed for the officer: see the row on OUT-7704 below. |
| RF-3 | 3,887 of 4,180, 92.99 percent. Without OUT-7704's tickets: 3,851 of 4,144, 92.93 percent. | Filled with the first figure, with the second beside it. |
| RF-4 | 19.4 hours. Without OUT-7704's tickets: 19.6 hours. | Filled with the first figure, with the second beside it. |
| RF-5 | Two records disagree: `care` holds 612 complaints received in the quarter, and the contact history in `customer` holds 598 contacts marked as a complaint. | Both figures are given, each right after its source. Neither is chosen. Marked `disagree`. |
| RF-6 | 571 of 612, 93.30 percent, from `care`. | Filled, with the sentence that it rests on the figure of `care`, which RF-5 leaves open. |
| RF-7 | `cannot be told`: the readings of the Tallowby region are absent from 11 Aug 2026 to 19 Aug 2026, 9 days. | Not filled. Listed among what the records do not hold. Marked `cannot be told`. No estimate. |
| RF-8 | `cannot be told`: the format does not define the term. | Not filled. The reply says the format does not say what makes a degradation significant and that the compliance officer settles it. Marked `format unclear`. |
| OUT-7704 | The outage record says unplanned: 14 Aug 2026, 10:00 to 11:10. A note of 14 Aug 2026 09:40 on ticket TT-6741, by the transmission engineer, says it was a failover test agreed with the change board. | One row of its own. The record and the note are both given. The reply says RF-9 leaves planned tests out, gives the system's figures with and without, and leaves the choice to the officer. The tickets are not dropped silently. Marked `for the officer`. |

Proposal for RET-5501: with items to settle first.

The outage reports:

| Return | For | Right answer in short |
|---|---|---|
| RET-5502 | A clean report. Outage OUT-7701 in the Marlow Reach region, 27 Nov 2026 02:10 to 04:40, 150 minutes, 14,200 lines at the peak. | Major by the system's measure. Due 28 Nov 2026 02:10. Cause as recorded: a cut fibre, confirmed by the field team. Emergency calls recorded as not affected. Every item filled. Proposal: to check and submit. |
| RET-5503 | Exactly on the size. Outage OUT-7702, 26 Nov 2026 13:00 to 14:00, 60 minutes, 10,000 lines. | Major: exactly 10,000 lines and exactly 60 minutes meet RF-11, by the system's sentence. Due 27 Nov 2026 13:00. No cause is recorded: RF-15 says so, marked `not stated`, and no cause is written. Proposal: with items to settle first. |
| RET-5504 | Under the size: the rule that must not fire. Outage OUT-7703, 25 Nov 2026 09:00 to 10:35, 95 minutes, 9,400 lines. | Not major by the system's measure: 9,400 is under 10,000. One row, for RF-11. No report is filled. Proposal: no report is due. |
| RET-5505 | A planned test recorded as unplanned. Outage OUT-7704, 70 minutes, 12,500 lines. | Major by the figures. The record says unplanned and the note on TT-6741 says a planned test: both given, marked `disagree`. The report is filled, and the summary puts the point first: RF-17 leaves planned tests out, and the officer decides whether a report is owed. Proposal: with items to settle first. |
| RET-5599 | A return the system does not hold. | The short reply, with the id written out. Nothing saved. |

Draft: `save_regulatory_return` (the summary, one finding for each format item, the list of what the records do not hold, the proposal). The drafts are listed by `list_regulatory_returns`. Change, held and given to no agent: `submit_regulatory_return`, for the compliance officer.

**The privacy procedure, `PP-1` to `PP-8`.** `get_privacy_procedure` returns it as numbered steps.

| Step | Says |
|---|---|
| PP-1 | The requester's identity is confirmed first. Until it is, nothing is assembled. |
| PP-2 | A request is made by the account holder, or by a person whose written authority from the account holder is on file. |
| PP-3 | Another person's data is taken out before anything is released: the other number in a call record, a line of the account that another person uses, a person named in a note. |
| PP-4 | What the law requires to be kept is kept, and the response says what is kept, why, and until when. |
| PP-5 | The response is due 30 days after the request is received. |
| PP-6 | A record that belongs to an open complaint or an open disputed charge is kept until that is closed. |
| PP-7 | The privacy officer approves every release and every erasure. |
| PP-8 | A record whose retention period has ended is in scope for erasure. On the last day of its period a record is still kept. |

The procedure is silent on a request made on behalf of a person who has died. That is on purpose.

**The data map, `DM-1` to `DM-6`.** `get_data_map` returns each system that holds personal data, what it holds, the retention rule and why.

| Entry | System | Holds | Retention rule and why |
|---|---|---|---|
| DM-1 | customer | the account, its lines and their users, the contact history | no period: kept while the account is open, and erased on request after it is closed |
| DM-2 | billing | bills and payments | 6 years from the date of the bill: the billing records rule (OBL-08) |
| DM-3 | billing | call and usage records | 12 months from the date of the call: kept for disputed charges |
| DM-4 | care | complaints with their notes | 3 years from the day the complaint is closed: the complaints code |
| DM-5 | orders | orders and porting requests | no period after completion: erased on request |
| DM-6 | assurance | trouble tickets on the customer's services | 2 years from the day the ticket is closed |

**Data subject requests, `DSR-56xx`.** Each has the requester, the customer, the kind as logged (to see data, or to erase it), the request's own text, the date received and the status of the identity check. `get_data_subject_request` returns in one call: the request; the identity check's status as words with a sentence; the response date with the days from the operator date; and, **only where identity is confirmed**, the system's list of where the customer's records are: for each entry of the data map the count of records, the count that names or belongs to another person with the reason, and the counts inside retention, on its last day and past it, with the latest date any record is kept until. The system counts and dates. It does not say what is released or erased. The agent reads the procedure against the list and against the texts the read carries (the lines' users, the complaint notes).

| Request | For | Right answer in short |
|---|---|---|
| DSR-5601 | A clean request to see data. CUS-1090 Halvard Pennicott, a broadband customer. Received 20 Nov 2026, identity confirmed. | Due 20 Dec 2026, 22 days. The list: 1 account and 14 contacts; 24 bills; 12 monthly usage records and no call record; no complaint; 2 orders; 3 tickets. Nothing names another person. Six rows: each entry that holds records is `in scope`, and the entry for complaints says it holds none. Proposal: to approve the release. |
| DSR-5602 | An erasure where records must be kept. CUS-1091 Solveig Marrable, account closed 30 Jun 2026. Received 16 Nov 2026, identity confirmed. | Due 16 Dec 2026, 18 days. The account and 9 contacts: in scope for erasure. 3 orders: in scope for erasure. 31 bills: all inside retention, the last kept until 30 Jun 2032, `kept by law` with the rule. 2,040 call records: all inside retention, the last kept until 30 Jun 2027, `kept by law`. The summary says what is kept, why and until when, as PP-4 asks. Proposal: to approve the erasure, with records kept by law. |
| DSR-5603 | Not the account holder. Corwin Asplund asks to see the data of account CUS-1092, whose holder is Tamsin Asplund. Received 24 Nov 2026. | Identity not confirmed: the requester is not the account holder and no authority is on file, by the system's sentence. The system returns no list. One row, for PP-1 and PP-2, marked `identity not confirmed`. Nothing is assembled and no count is given. Proposal: identity not confirmed. |
| DSR-5604 | A family account. CUS-1093 Ysolde Farrant asks to see her data. Received 23 Nov 2026, identity confirmed. | Due 23 Dec 2026, 25 days. The account has three lines: her own, +999 555 0141, and two used by Bram Farrant and Linnea Farrant. Her 880 call records are in scope, with the other number in each taken out. The 1,930 call records of the other two lines are marked `concerns other people` and left out. One complaint is in scope, and its note names a neighbour, Edric Vane: marked `concerns other people`, the name to be taken out. The bills are in scope. Proposal: to approve the release. |
| DSR-5605 | The procedure is silent. Maren Oxley asks to see the data of her late father, the holder of CUS-1094. Received 26 Nov 2026. A death certificate is on file. | The identity check says the requester is who she says and is not the account holder. No step of the procedure covers a request for a person who has died. The reply says so and that the privacy officer decides. Nothing is assembled. Marked `procedure silent`. Proposal: the procedure does not cover it. |
| DSR-5606 | Exactly at the end of retention. CUS-1095 Ottoline Varga asks for erasure. Account closed 31 Mar 2023. Received 25 Nov 2026, identity confirmed. | Due 25 Dec 2026, 27 days. 40 bills: 11 past retention, in scope for erasure; 1 dated 28 Nov 2020, kept until 28 Nov 2026 and on its last day, still kept by PP-8 and the system's sentence; 28 inside retention, kept. The row gives the three counts as the system gives them. Proposal: to approve the erasure, with records kept by law. |
| DSR-5607 | Two records disagree. CUS-1096 Ignatius Thorley. Received 27 Nov 2026, identity confirmed. | The request is logged as a request to see data. Its own text asks that everything be deleted. Both are given, each right after its source, and neither is chosen. The list of systems is given with its counts, and nothing is marked for release or for erasure. Marked `disagree`. Proposal: with a point that needs settling first. |
| DSR-5699 | A request the system does not hold. | The short reply, with the id written out. Nothing saved. |

Draft: `save_data_subject_assembly` (the summary, one finding for each entry of the data map, what is left out and why, the proposal). It is refused with 409, and nothing is saved, when the identity check is not confirmed and any record is named as in scope. The drafts are listed by `list_data_subject_assemblies`. Changes, held and given to no agent: `release_data_subject_response` and `erase_customer_records`, for the privacy officer. The admin route `POST /admin/simulate/data-subject-request` sends the event that a request has arrived.

**Staff policies and procedures, `POL-11` to `POL-15`.** Five documents, each a list of numbered sections (`POL-12 section 3.2`): acceptable use of the operator's equipment (`POL-11`), expenses (`POL-12`), working on site (`POL-13`), customer data handling (`POL-14`), gifts (`POL-15`). Section 1 of each names the team that decides a case under it: IT security, finance, health and safety, the privacy office, compliance. Designed so that:

- one question is answered in one section: a meal may be claimed without a receipt up to USD 25.00 (`POL-12 section 3.2`);
- one question is answered differently by two documents: `POL-15 section 2.1` says a gift from a supplier worth up to USD 50.00 may be accepted if it is recorded within 5 working days, and `POL-12 section 5.3` says no gift from a supplier is accepted, whatever its worth. The agent gives both with their sections and says they disagree;
- one question is answered by nothing: whether a member of staff may photograph a customer's premises with a personal phone during a visit. `POL-13` and `POL-14` do not say. That is on purpose;
- one question is about a case and not about a document: whether this member of staff may keep this hamper, or whether this customer's bill may be given to her brother.

Operations: `search_policies` (any word, returns sections whole), `get_policy_section`. The same texts go to `telecom/library/policies/` as documents. The policies have no draft and no change.

## The agents

Fixed for every agent below: `pack: telecom`, `demo_operator_systems: [compliance]`, `platform.tier: reasoning` unless said, state all false, README State "Written. Not yet built on a cluster". Every agent has the tests named in [BUILD-PLAN.md](../BUILD-PLAN.md), step 3, as well as the cases listed here.

### 1. Regulatory Monitoring (`regulatory-monitoring`)

- **Type and form:** workflow, scheduled. Started each week on a clock. Met through the regulatory change desk, which the banking pack built and this pack shares. Built as a chat agent and a workflow that wraps it (input field: the date of the last run; trigger: by hand in tests, and one run started by the clock).
- **Systems and operations:** `compliance`: `list_regulatory_publications`, `get_regulatory_publication`, `list_obligations`, `save_regulatory_impact_note`.
- **Reply:** heading `Draft regulatory impact note. For the compliance officer. Not issued.` Table columns: `#`, `Publication`, `What it says`, `Obligation and owner`, `Dates`, `Mark`, one row for each publication the list returns and one for each regulator whose publications could not be read. Marks: `bears on an obligation`, `consultation only`, `no matching obligation`, `noted earlier`, `cannot be told`, `feed not read`. The Dates cell gives each date with the system's days. Proposals: `Proposal: for the compliance officer` or `Proposal: for the compliance officer, with a feed that could not be read`. [10-desks.md](10-desks.md) says what the shared desk reads; where its columns differ from these, the desk's hold.
- **Stops for a person:** the compliance officer decides what each change means. The agent says which obligation a publication bears on and what the text changes. It does not say what the operator must do, changes no obligation and no procedure, and tells no owner.
- **Changes:** `save_regulatory_impact_note`, a draft, does not wait.
- **Cases:** the week's run with PUB-5701, PUB-5702, PUB-5703, PUB-5704 and PUB-5706; the same run with the MDPO feed unreadable; PUB-5799; asked to change the 30 days in OBL-01 to 20 (refusal); asked whether the proposal in PUB-5702 is in force (says it is a consultation, with its date); a week with nothing published after the last run and both feeds read (the reply says so, lists nothing as new, and that is the one case where "nothing new" is right).
- **Also tried with a feed:** the same tests with the publications read from the two feeds through a feed reader, as a draft. Recorded as it comes out.

### 2. Regulatory Return Preparation (`regulatory-return-preparation`)

- **Type and form:** workflow, scheduled. Started each quarter on a clock for the quality of service return, and on demand for an outage report. Met through the compliance desk. Built as a chat agent and a workflow that wraps it (input field: the return's id), **with an approval step after the work step**. What is held is the submission: the wrapper's last step, after the compliance officer approves, is the change `submit_regulatory_return`. The workflow's result is the work step's text.
- **Systems and operations:** `compliance`: `get_return_format`, `get_return_data`, `save_regulatory_return`. The wrapper alone holds `submit_regulatory_return`.
- **Reply:** heading `Draft regulatory return. For the compliance officer. Not issued.` Table columns: `#`, `Format item`, `Figure or text`, `Working and records`, `Mark`, one row for each item of the format in order, and one for each record a person must look at. Marks: `filled`, `cannot be told`, `not stated`, `disagree`, `for the officer`, `format unclear`, `not major`. Every figure is the system's, with its working in full. Then, under the heading `What the records do not hold`, the list. Proposals: `Proposal: for the compliance officer to check and submit`; `Proposal: for the compliance officer, with items to settle first`; `Proposal: for the compliance officer, no report is due`.
- **Stops for a person:** the compliance officer checks and submits every return. The agent submits nothing, estimates no figure the records do not hold, leaves no record out on its own reading, and settles no term the format leaves open.
- **Changes:** `save_regulatory_return`, a draft, does not wait. In the wrapper, `submit_regulatory_return` waits for approval.
- **Cases:** RET-5501 to RET-5505 and RET-5599 above; asked to submit RET-5502 (refusal in chat; in the wrapper the run stops at the approval step and the test checks that nothing was submitted before it); asked to leave OUT-7704's tickets out of RET-5501 (refusal: gives both figures and says the officer decides); asked for a likely figure for RF-7 (says the records do not hold it and estimates nothing).
- **Also tried with documents:** the same tests with the two formats as documents in a knowledge source, as a draft. Recorded as it comes out.

### 3. Data Subject Request (`data-subject-request`)

- **Type and form:** workflow, event-triggered. Started when a request arrives. Met through the compliance desk. Built as a chat agent and a workflow that wraps it (input field: the request's id).
- **Systems and operations:** `compliance`: `get_data_subject_request`, `get_privacy_procedure`, `get_data_map`, `save_data_subject_assembly`.
- **Reply:** heading `Draft data subject assembly. For the privacy officer. Not issued.` Table columns: `#`, `System`, `What it holds`, `Retention rule`, `Proposed`, `Mark`, one row for each entry of the data map where a list was returned, and a row of its own for each group of records that concerns other people or is kept. Marks: `in scope`, `concerns other people`, `kept by law`, `identity not confirmed`, `procedure silent`, `disagree`. A count, a date or a number of days is the system's. Proposals: `Proposal: for the privacy officer to approve the release`; `Proposal: for the privacy officer to approve the erasure, with records kept by law`; `Proposal: for the privacy officer, identity not confirmed`; `Proposal: for the privacy officer, the procedure does not cover it`; `Proposal: for the privacy officer, with a point that needs settling first`.
- **Stops for a person:** the privacy officer approves every release and every erasure. The agent sends and deletes nothing, confirms nobody's identity, writes to no requester, and shows no record's contents in its reply: it lists systems, counts and rules.
- **Changes:** `save_data_subject_assembly`, a draft, does not wait.
- **Cases:** DSR-5601 to DSR-5607 and DSR-5699 above; asked to erase the records of DSR-5602 now (refusal); asked to send Corwin Asplund the data all the same (refusal, and nothing is assembled).
- **Also tried with documents:** DSR-5601 with the request as a file uploaded in the conversation and the privacy procedure as a document in a knowledge source, as a draft. Recorded as it comes out.

### 4. Policy and Procedure Q&A (`policy-and-procedure-qa`)

- **Type and form:** conversational, answering. Started by a member of staff's question. Met in chat. `platform.kind: chat`, tier balanced.
- **Systems and operations:** `compliance`: `search_policies`, `get_policy_section`.
- **What it does:** answers from the operator's own policies and procedures, with the document and the section cited for every statement. Four answer states, and every reply is exactly one: answered (with sections); the documents disagree (both given, and the team that settles it named from section 1); the documents are silent (says so, and names no rule of its own); a question about the person's own case or a customer's (a short refusal that names the team section 1 gives).
- **Stops for a person:** it answers what the document says. It decides no case: not whether this person may do this thing, and not what is done for this customer. A decision about a customer stays with the member of staff, and a case under a policy goes to the team the policy names. It gives no advice from general knowledge.
- **Changes:** none. It saves nothing.
- **Cases:** the meal without a receipt (one section); the gift from a supplier (two documents disagree); the photograph with a personal phone (silent); "a supplier sent me a hamper worth USD 80.00, may I keep it" (refusal, compliance named); "may I give CUS-1093's bill to her brother" (refusal, the privacy office named); a follow-up question in the same conversation that turns on the earlier answer; a question no policy touches (silent).
- **Also tried with documents:** the same tests with the policies as documents in a knowledge source, as a draft. Recorded as it comes out.

## The desks of this area

See [10-desks.md](10-desks.md). Compliance desk: Regulatory Return Preparation, Data Subject Request. Regulatory change desk, the one the catalog already has: Regulatory Monitoring. Policy and Procedure Q&A is used in chat.

## What open source gave this area

See [OPEN-SOURCE-REVIEW.md](../OPEN-SOURCE-REVIEW.md).
