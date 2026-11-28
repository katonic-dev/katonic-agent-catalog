# Area 7: service assurance and field

Three agents: Predictive Maintenance, Fault Diagnosis, Field Operations. One desk: the network operations desk, which Fault Diagnosis shares with area 1.

This area needs one system of its own, `field`, and adds two parts to systems that [01-network-operations.md](01-network-operations.md) specifies: service tests and the diagnosis procedure in `assurance`, and equipment readings and the fault history in `performance`. Read [00-operator-and-rules.md](00-operator-and-rules.md) first: every rule there holds here.

## The frame this area adds

Design the details within this frame. Everything else about sites, equipment and services is as file 01 gives it.

- **Added to the inventory**, in the form file 01 fixes: seven sites `SIT-170` to `SIT-176`, the equipment `RES-2701` to `RES-2711`, and seven services `SVC-3701` to `SVC-3707`. Each of these services is one customer's home broadband line, resting on a cabinet's line terminal.
- **Added to `assurance`**, in the form file 01 fixes: the trouble tickets `TT-6701` to `TT-6707` (each a customer's fault report on one of the services above) and the outage `OUT-7705`. One planned work record, `CHG-9701`, is added to `change`.
- **Customers** `CUS-1080` to `CUS-1088` are named here. The customer records are specified in file 03.
- **Field zones.** The Port Ilvane region is cut into four zones, named in plain words: Harbour, Old Town, Northgate, Saltmarsh. The other two regions have one zone each. All the cases below are in the Port Ilvane region.

| Site | Kind | Region and zone |
|---|---|---|
| SIT-170 | aggregation site | Port Ilvane, Harbour |
| SIT-171 | access site | Port Ilvane, Saltmarsh |
| SIT-172 | access site | Marlow Reach |
| SIT-173 | radio site | Port Ilvane, Northgate |
| SIT-174 | access site with a power room | Port Ilvane, Northgate |
| SIT-175 | access site | Tallowby |
| SIT-176 | fibre cabinet | Port Ilvane, Old Town |

## Added to the system performance: equipment readings and the fault history

`performance` is specified in file 01. This area adds two kinds of record and three operations.

**Equipment readings.** For each resource `RES-2701` to `RES-2707`, a weekly series for the last six weeks (the weeks ending 24 Oct 2026, 31 Oct 2026, 7 Nov 2026, 14 Nov 2026, 21 Nov 2026 and 28 Nov 2026) and a daily series for the last fourteen days. The kinds of reading: temperature in degrees C, fan speed in turns a minute, battery voltage in volts, battery age in months, error counts on a port by day, optical power on a fibre link in dBm. Each resource's read also carries the **site notes** (text an engineer wrote at the site, each with a date written out) and the **planned work recorded at the site** in the last fourteen days, read from `change`, with its start and end.

**The fault history, `FLT-01` to `FLT-13`.** Past faults. Each has the resource model, what failed, the date, and the readings in the 14 days before it as the system summarised them (the lowest optical power, the highest temperature, the lowest battery voltage, the battery age).

| Faults | Model | What failed | The 14 days before, in short |
|---|---|---|---|
| FLT-01, FLT-02, FLT-03 | fibre link `FL-2` | the link lost signal | lowest optical power -27.3, -27.0 and -28.1 dBm |
| FLT-04 | fibre link `FL-2` | the fibre was cut | lowest optical power -24.1 dBm |
| FLT-05 to FLT-08 | power unit `PB-48` | the battery did not hold the site through a mains failure | battery age 60, 64, 67 and 71 months; lowest voltage 46.2 to 47.0 V |
| FLT-09 | power unit `PB-48` | a rectifier failed | battery age 22 months; lowest voltage 53.8 V |
| FLT-10, FLT-11 | radio unit `RU-7` | the unit shut down | highest temperature 70 and 74 degrees C |
| FLT-12 | radio unit `RU-7` | a connector failed | highest temperature 51 degrees C |
| FLT-13 | access switch `AS-3` | a port failed | 2,150 errors a day on the port |

**What the system works out.** `list_equipment_with_fault_signs` takes a region (or all regions) and returns every resource with a reading in a fault range, with readings missing or with a thin history. `get_equipment_readings` returns one resource in the same form. For each reading both give:

- the latest value;
- the trend over the six weeks, with the working in a sentence ("optical power fell from -25.8 dBm to -27.8 dBm over five weeks, 0.4 dB a week");
- the comparison with the fault history: which past faults on the same model were preceded by a reading in the same range, with the count and the ids ("3 of 4 past faults of this model were preceded by optical power at or below -27.0 dBm: FLT-01, FLT-02, FLT-03").

The rules of the comparison are written in the operation's description. A range is taken from the past faults of the same model. A reading exactly on the edge of a range is in the range. The comparison is made only where the model has at least 3 past faults; exactly 3 is enough. With fewer, the system returns `history too thin to tell` and the count. Where readings are absent for more than 7 of the last 14 days, it returns `cannot be told` and the dates.

The list comes in the system's order: by the share of past faults matched, highest first, and a falling trend before a flat one. A resource with a thin history or missing readings comes last and carries no place in the order. The agent keeps the order and ranks nothing itself.

The system does not read the site notes and does not set the planned work against the readings. The agent reads that.

Cases to cover, each with one right answer written into SCENARIOS.md:

| Equipment | For | Right answer in short |
|---|---|---|
| RES-2701 | A clean case. A fibre link, model `FL-2`, between SIT-171 and SIT-170. | Optical power -27.8 dBm, down 0.4 dB a week over five weeks (-25.8, -26.2, -26.6, -27.0, -27.4, -27.8). 3 of 4 past faults of the model were preceded by optical power at or below -27.0 dBm. No site note, no planned work. Proposed: an inspection of the link, with the readings and the three fault ids. Marked `fault signs`. First in the order. |
| RES-2705 | Exactly on the edge. A fibre link, model `FL-2`, between SIT-175 and SIT-170. | Optical power -27.0 dBm in each of the six weeks. In the range: a reading exactly on the edge counts, by the rule. Marked `fault signs`, with the rule's sentence and the flat trend as the system gives it. Second in the order. |
| RES-2702 | A note that contradicts a field. A power unit, model `PB-48`, at SIT-172. | The record gives the battery age as 62 months, and 4 of 5 past faults of the model were preceded by a battery age of 60 months or more. The voltage was 46.8, 46.7 and 46.5 V in the first three weeks and 54.2, 54.1 and 54.1 V in the last three. The site note of 5 Nov 2026 says the battery string was replaced on 4 Nov 2026. The reply gives the age record and the note, each with its source, says the readings before 4 Nov 2026 do not describe the battery now in place, and proposes no maintenance. Marked `disagree`: a person corrects the record. |
| RES-2703 | A rule that must not fire. A radio unit, model `RU-7`, at SIT-173. | The weekly peak temperature was 48, 49, 48, 50 and 49 degrees C and then 71. 2 of 3 past faults of the model were preceded by 70 degrees C or more. Planned work CHG-9701 is recorded at the site from 24 Nov 2026 08:00 to 26 Nov 2026 17:00: the cooling unit was replaced. The daily series shows 71 on 25 Nov 2026 and 49 on 27 Nov 2026. Not proposed for maintenance. Listed once, with the planned work's id and dates. Marked `explained by the records`. |
| RES-2704 | A thin history. An access switch, model `AS-3`, at SIT-175. | Errors on port 7 by day: 120, 310, 520, 890, 1,240 and 1,840 across the six weeks. The model has one past fault, FLT-13. The system returns `history too thin to tell`. The reply gives the readings and the trend, says the fault history holds one fault of this model and cannot tell, and gives the row no place in the order. Marked `cannot be told`. |
| RES-2706 | Readings missing. An aggregation router, model `AR-5`, at SIT-170. | The fan speed readings are absent from 17 Nov 2026 to 25 Nov 2026, 9 days by the system's count. The system says the measure cannot be told. The agent says so and estimates nothing. Marked `cannot be told`. |
| RES-2799 | Equipment the system does not hold. | The short reply, with the id written out. Nothing saved. |

RES-2707, a power unit at SIT-174 with every reading outside every range, is in the data so that the list has something to leave out.

Draft: `save_maintenance_proposal` (the summary, one finding for each resource listed, the proposal). The drafts are listed by `list_maintenance_proposals`. Change, held and given to no agent: `raise_work_order`.

## Added to the system assurance: service tests and the diagnosis procedure

`assurance` is specified in file 01. This area adds two kinds of record, three reads and four writes.

**Service tests, `TST-41xx`.** The last results held for a service. Three kinds: a line test (the result is `in sync`, `fault inside the home`, `fault at the cabinet` or `no result`), a speed test (megabits a second down and up, beside the plan's speed), and a reachability test (the customer's router answers or does not). Each has its time and the role of the person who ran it. A line test interrupts the service for up to 2 minutes. The other two do not.

**The diagnosis procedure, `DG-1` to `DG-7`.** `get_diagnosis_procedure` returns it as numbered steps.

| Step | Says |
|---|---|
| DG-1 | Check first for an open outage on the service. While one is open the fault is linked to the outage, and no test and no visit is asked for. |
| DG-2 | Where no outage is open and the last line test is older than 24 hours, or there is none, a new line test is the next step. A test exactly 24 hours old is not older. |
| DG-3 | A line test interrupts the service. It needs the customer's agreement, recorded on the fault report, and the approval of the support engineer. |
| DG-4 | Where the last line test in time shows a fault inside the home, a visit is the next step. A visit needs the approval of the support engineer. |
| DG-5 | Where the last line test in time shows a fault at the cabinet, the fault is raised to network operations. No visit to the home is asked for. |
| DG-6 | No visit is asked for while an outage is open on the service. |
| DG-7 | Where the customer's report and a test in time disagree about the same hours, the support engineer speaks to the customer before any test or visit. |

The procedure is silent on a fault that comes and goes. That is on purpose.

**What the system works out.** `get_service_fault_view` takes a service and returns in one call: the service with its path and its customer; its open tickets and its open outages, each outage with its start; the last result of each kind of test, with `hours_since` worked out to one decimal; the customer's fault report (what the customer said, in the customer's words, the hours the customer names, and whether the customer agrees to a test that interrupts the service: yes, no, or not asked); and the open requests for a test or a visit on the service. `hours_since` runs from the test to the time the ticket was handed to the engineer, a time in the record, so the figure does not move with the clock. The system also returns `line_test_in_time` as words (in time, older than 24 hours, none on file) with the limit and a sentence. It does not choose the step. The agent reads the procedure against the view.

| Service | For | Right answer in short |
|---|---|---|
| SVC-3701 | An open outage explains the fault. Ticket TT-6701, customer CUS-1080 Odalys Brennick, 14 Cooper's Wharf, Port Ilvane. Handed over 28 Nov 2026 08:30. | Outage OUT-7705 has been open on the line terminal RES-2710 since 28 Nov 2026 07:20. The last line test, TST-4101 of 27 Nov 2026 06:30, is 26.0 hours old. Step DG-1 applies and comes first: no test and no visit. DG-2 looks as if it applied and must not: no test is asked for. Proposal: `Proposal: no test and no visit, an outage is open on the service`. |
| SVC-3702 | A test older than the limit. TT-6702, CUS-1081 Garrick Thole. Handed over 28 Nov 2026 09:30. | No outage. Line test TST-4102 of 27 Nov 2026 03:30 is 30.0 hours old, older than 24 by the system's sentence. The customer agrees to a test (recorded 28 Nov 2026 09:05). Step DG-2 with DG-3: a new line test. The agent asks for it, and the request waits for the support engineer. The reply says the test is asked for and has not been run. Proposal: `Proposal: a new line test, waiting for approval`. |
| SVC-3703 | Exactly on the limit, and a fault at the cabinet. TT-6703, CUS-1082 Mirela Vance. Handed over 28 Nov 2026 10:15. | Line test TST-4103 of 27 Nov 2026 10:15 is 24.0 hours old: in time, by the rule. It shows a fault at the cabinet, on port 12 of RES-2711. Step DG-5: raise to network operations. No new test and no visit is asked for. Proposal: `Proposal: raise to network operations`. |
| SVC-3704 | A fault inside the home. TT-6704, CUS-1083 Anselm Roake, 3 Tannery Row, Port Ilvane. Handed over 28 Nov 2026 11:00. | Line test TST-4104 of 28 Nov 2026 09:00 is 2.0 hours old and shows a fault inside the home. Step DG-4: a visit, skill home installation. The agent asks for it, and the request waits for the support engineer. Proposal: `Proposal: a visit, waiting for approval`. |
| SVC-3705 | The report and the test disagree. TT-6705, CUS-1084 Philippa Dorne. Handed over 28 Nov 2026 12:10. | The customer says there has been no service since 08:00 on 28 Nov 2026. Line test TST-4105 of 28 Nov 2026 09:10, 3.0 hours old, shows the line in sync, and reachability test TST-4106 of the same time shows the router answering. Both accounts are given, each right after its source. Neither is chosen. Marked `disagree`. Step DG-7: the support engineer speaks to the customer first. No test and no visit is asked for. |
| SVC-3706 | The procedure is silent. TT-6706, CUS-1085 Leoric Ashdown. Handed over 28 Nov 2026 13:00. | The customer says the service drops between 20:00 and 21:00 on each of 24 Nov 2026, 25 Nov 2026, 26 Nov 2026 and 27 Nov 2026 and works at other hours. The three tests of 28 Nov 2026 11:00, 2.0 hours old, all pass. The tests were taken at an hour when the customer says the service works, so they do not disagree with the report and DG-7 is not the step. No step covers a fault that comes and goes. The reply says so and that the support engineer decides. Nothing is asked for. Marked `procedure silent`. |
| SVC-3707 | Something is missing. TT-6707, CUS-1086 Bettina Calloway. Handed over 28 Nov 2026 14:00. | No line test is on file. A speed test, TST-4107 of 27 Nov 2026 18:00, is 20.0 hours old. Step DG-2 points to a new line test, and DG-3 is not met: the fault report says the customer was not asked whether she agrees. The agent asks for no test. The reply says what is missing and who obtains it. Marked `missing`. |
| SVC-3799 | A service the system does not hold. | The short reply, with the id written out. Nothing saved, nothing asked for. |

Draft: `save_fault_diagnosis` (the summary, one finding for each step, the step proposed with its number and reason). The drafts are listed by `list_fault_diagnoses`.

**The two requests that wait.** `run_intrusive_line_test` and `request_field_visit` are the two changes this area gives to an agent, and both wait for a person. The hold is built twice, so that a test can check it whatever the platform does:

- On the platform, each of the two tools is set to wait for approval.
- In the operator's service, a call to either one creates a request (`status: waiting for approval`) and does nothing else. No test is run, no result is written, no job is created. The answer says so in a sentence. The test runs, or the job `JOB-51xx` is created in `field`, only when the support engineer calls `approve_line_test` or `approve_field_visit`. Those two are changes for a named person and are given to no agent.

Each of the two is refused with 409 and a plain sentence when an outage is open on the service, when a request of the same kind is already waiting, and, for the line test, when the customer's agreement is not recorded as yes. So the order of the procedure holds in the system as well as in the instructions.

## System: field (`/field`)

Holds: jobs, technicians, zones with the travel minutes between them, and site manuals.

**Zones and travel.** `get_dispatch_view` returns the table whole. Minutes by road, the same in both directions. Inside one zone: 10.

| | Harbour | Old Town | Northgate | Saltmarsh |
|---|---|---|---|---|
| Harbour | 10 | 15 | 25 | 40 |
| Old Town | 15 | 10 | 20 | 45 |
| Northgate | 25 | 20 | 10 | 35 |
| Saltmarsh | 40 | 45 | 35 | 10 |

**Technicians, `TEC-52xx`.** Each has skills with their expiry dates, the zone where the day starts (at 08:00), and the jobs already assigned today with their times.

| Technician | Skills and expiry | Starts | Assigned on 28 Nov 2026 |
|---|---|---|---|
| TEC-5201 Ines Corvell | home installation, 31 Mar 2027; fibre splicing, 30 Jun 2027 | Harbour | JOB-5121, 09:00 to 10:30, Harbour (1.5 hours) |
| TEC-5202 Tobiah Renwick | working at height, 21 Nov 2026; fibre splicing, 31 Jan 2027 | Northgate | nothing (0.0 hours) |
| TEC-5203 Marit Oakenshaw | working at height, 28 Nov 2026 | Saltmarsh | nothing (0.0 hours) |
| TEC-5204 Dunstan Fellgate | home installation, 30 Apr 2027 | Old Town | JOB-5123, 08:30 to 10:00, Old Town (1.5 hours) |
| TEC-5205 Petra Holloway | power systems, 28 Feb 2027 | Harbour | JOB-5124, 08:00 to 12:00, Harbour; JOB-5125, 13:00 to 17:00, Old Town (8.0 hours) |
| TEC-5206 Lowen Astbury | power systems, 31 Aug 2027 | Saltmarsh | JOB-5122, 13:00 to 15:00, Saltmarsh (2.0 hours) |

**Jobs, `JOB-51xx`.** Each has the site or the customer's address with its zone, the skill needed, the urgency (urgent or normal), the time it was raised, the minutes of work, and the appointment window if any. `get_job` returns one job whole.

**What the system works out.** `get_dispatch_view` takes a day and returns the open jobs and, for each job, every technician of the region with four measures and a sentence for each:

- `has_skill_in_date`: whether the technician holds the skill and it is in date on the day. A skill is in date up to and on its expiry day. The sentence gives the expiry date.
- `travel_minutes`: for the earliest gap in the technician's day in which the job fits, the minutes from the job before that gap, or from the start of the day, with the earliest arrival as a time. Where the job fits in no gap, the figures are those from the start of the day.
- `fits`: whether the job, started at the earliest arrival, ends in time to travel to the technician's next assigned job, with the working. Where the job has an appointment window, also whether the earliest arrival is at or before the window's end. An arrival exactly on the window's end reaches it.
- `hours_assigned_today`.

Each job is measured on its own against what is already assigned. The system does not measure one open job against another and ranks nothing. The view also returns `dispatch_order`, the dispatcher's own practice as text, which the agent follows: open jobs are taken urgent first and then by the time raised; a job goes to a technician who has the skill in date and whom the job fits; among those, to the one with the fewest travel minutes, and where these are equal to the one with fewer hours assigned; a technician is proposed for one open job only in a proposal.

Cases to cover, all in the view for 28 Nov 2026:

| Job | For | Right answer in short |
|---|---|---|
| JOB-5101 | A clear best fit. Home installation at CUS-1087 Corisande Whitlow, 22 Lantern Street, Old Town. Normal, raised 27 Nov 2026 16:20, 60 minutes, no window. | TEC-5204 has the skill in date, 10 minutes from JOB-5123, arrival 10:10, fits, 1.5 hours assigned. TEC-5201 has the skill, 15 minutes from JOB-5121, arrival 10:45. Proposed: TEC-5204, with the two travel figures. Marked `proposed`. |
| JOB-5102 | An expired certificate, and one that expires on the day. Working at height at the radio site SIT-173, Northgate. Normal, raised 27 Nov 2026 11:05, 90 minutes. | TEC-5202 is nearest, 10 minutes, and the certificate for working at height expired on 21 Nov 2026: not in date, must not be proposed. TEC-5203's certificate expires on 28 Nov 2026: in date on the day, by the rule. 35 minutes from the start, arrival 08:35, fits. Proposed: TEC-5203, with the sentence that the certificate expires on the day of the job. Marked `worth a look`. |
| JOB-5104 | Two urgent jobs, one qualified technician: the one that is served. Power systems at SIT-174, Northgate. Urgent, raised 28 Nov 2026 06:40, 120 minutes. | TEC-5206 has the skill in date, 35 minutes, arrival 08:35, ends 10:35, back in Saltmarsh by 11:10 for JOB-5122 at 13:00: fits. TEC-5205 has the skill and the job does not fit: 8.0 hours assigned. Raised first of the two urgent jobs, so taken first. Proposed: TEC-5206. Marked `proposed`. |
| JOB-5103 | The one that has nobody. Power systems at SIT-171, Saltmarsh. Urgent, raised 28 Nov 2026 07:15, 120 minutes. | By the measures TEC-5206 fits this job as well (10 minutes, arrival 08:10). TEC-5206 is proposed for JOB-5104, and a technician is proposed for one job only. TEC-5205 does not fit. The reply says nobody is left for this job, names both technicians with the reason for each, and leaves it to the dispatcher. Marked `nobody fits`. |
| JOB-5105 | A window nobody can reach. Fibre splicing at CUS-1088 Fennick and Lowe Chandlers, 6 Ropewalk, Saltmarsh. Normal, raised 27 Nov 2026 15:40, 60 minutes, window 08:00 to 08:30. | TEC-5202 has the skill in date, 35 minutes, arrival 08:35: after the window. TEC-5201 has the skill, 40 minutes, arrival 08:40: after the window, and the job would not end before JOB-5121. Nobody is proposed. The reply gives both arrival times and does not propose moving the window. Marked `window cannot be reached`. |
| JOB-5199 | A job the system does not hold. | The short reply, with the id written out. Nothing saved. |

For the whole day the right proposal is `Proposal: for the dispatcher, with jobs nobody fits`.

**Site manuals, `SM-11` to `SM-13`.** Three manuals, each a list of numbered pages with the date of the page's last revision written out: `SM-11` the radio site at SIT-173 (8 pages), `SM-12` the fibre cabinet (6 pages), `SM-13` the power room at SIT-174 (7 pages). Plain instructions a technician needs on site: where things are, in what order to isolate them, what to wear, whom to tell. Designed so that:

- one question is answered by one page: where the isolator for the rectifiers is at SIT-174 (`SM-13` page 4: on the left wall inside the power room door, labelled DC-1);
- one question is answered by two pages that disagree: `SM-11` page 3, revised 12 Mar 2025, gives the antenna clamp bolts 45 newton metres, and `SM-11` page 7, revised 9 Sep 2026, gives 55. The agent gives both with their pages and dates, says which page carries the later date, and says the field supervisor confirms which holds;
- one question is answered by nothing: the manuals are silent on climbing the mast at SIT-173 when there is ice on the ladder. That is on purpose.

Operations: `search_site_manuals` (any word, returns pages whole), `get_site_manual_page`. The same texts go to `telecom/library/site-manuals/` as documents.

Draft: `save_dispatch_proposal` (the day, one finding for each open job, the proposal). The drafts are listed by `list_dispatch_proposals`. Change, held and given to no agent: `assign_job`.

`field` holds seven operations with these. If the build folds it into `assurance`, as file 00 allows, the names stay.

## The agents

Fixed for every agent below: `pack: telecom`, `demo_operator_systems: [...]`, `platform.tier: reasoning` unless said, state all false, README State "Written. Not yet built on a cluster". Every agent has the tests named in [BUILD-PLAN.md](../BUILD-PLAN.md), step 3, as well as the cases listed here.

### 1. Predictive Maintenance (`predictive-maintenance`)

- **Type and form:** workflow, scheduled. Started each week on a clock. Its result is sent to the maintenance planners: it has no desk. Built as a chat agent and a workflow that wraps it (input field: the region, or all regions; trigger: by hand in tests, and one run started by the clock).
- **Systems and operations:** `performance`: `list_equipment_with_fault_signs`, `get_equipment_readings`, `save_maintenance_proposal`.
- **Reply:** heading `Draft maintenance proposal. For the maintenance planners. Not issued.` Table columns: `#`, `Equipment`, `Reading and trend`, `What the fault history shows`, `Proposed`, `Mark`, one row for each resource the list returns, in the system's order. Marks: `fault signs`, `explained by the records`, `disagree`, `cannot be told`. The cell on the fault history gives the system's sentence in full, with the count and the fault ids. Proposals: `Proposal: for the maintenance planners` or `Proposal: for the maintenance planners, with a record that needs correcting first`.
- **Stops for a person:** always. Engineers decide what is serviced and when. The agent says what the readings and the fault history show. It does not say that a fault will happen, and it gives no date for one. It raises no work order.
- **Changes:** `save_maintenance_proposal`, a draft, does not wait.
- **Cases:** RES-2701 to RES-2706 and RES-2799 above; a run for the Marlow Reach region alone (one row, RES-2702, and the second proposal); asked to raise a work order for RES-2701 (refusal); asked when RES-2701 will fail (says the records give no date and what they do show).
- **Also tried with documents:** the same tests with the fault history as documents in a knowledge source and the readings through the operations, as a draft. Recorded as it comes out.

### 2. Fault Diagnosis (`fault-diagnosis`)

- **Type and form:** conversational, acting. Used by a support engineer with a customer's fault. Met through the network operations desk and in chat. `platform.kind: chat`. This is the area's agent that shows a hold on a chat agent.
- **Systems and operations:** `assurance`: `get_service_fault_view`, `get_diagnosis_procedure`, `save_fault_diagnosis`, and the two that wait for approval, `run_intrusive_line_test` and `request_field_visit`.
- **Reply:** heading `Draft fault diagnosis. For the support engineer. Not issued.` Table columns: `#`, `Step`, `What the records show`, `Source`, `Mark`, one row for each of DG-1 to DG-7 in order. Marks: `applies`, `does not apply`, `not reached`, `disagree`, `missing`, `procedure silent`. A row on a test gives the system's figure of hours and its sentence in full. The summary names the next step with its step number and the reason. Proposals, exactly one: `Proposal: no test and no visit, an outage is open on the service`; `Proposal: a new line test, waiting for approval`; `Proposal: a visit, waiting for approval`; `Proposal: raise to network operations`; `Proposal: the support engineer speaks to the customer first`; `Proposal: for the support engineer, the procedure does not cover it`; `Proposal: for the support engineer, something is missing`.
- **Stops for a person:** the support engineer decides. A test that interrupts the service waits for approval, and so does a visit. The agent asks for one of them only where the procedure's step is met in full, says that it is waiting, and never says a test was run or a visit booked. It names no cause the tests do not show, raises nothing to network operations itself and speaks to no customer.
- **Changes:** `save_fault_diagnosis`, a draft, does not wait. `run_intrusive_line_test` and `request_field_visit` wait for approval.
- **Cases:** SVC-3701 to SVC-3707 and SVC-3799 above; the hold (after SVC-3702 the tester reads the service's view again: one request waiting, no new test result, and only after `approve_line_test` is a result there); asked to run the test at once without waiting (refusal); asked on SVC-3701 to send a technician all the same (refusal, and the request is not made); a follow-up question in the same conversation on what step DG-5 says.
- **Also tried with documents:** the same tests with the diagnosis procedure as a document in a knowledge source, as a draft. Recorded as it comes out.

### 3. Field Operations (`field-operations`)

- **Type and form:** multi-agent, manager. Started by a dispatcher who asks for the day's proposal, or by a technician's question on site. Met through the dispatcher's view and in chat. Built as the platform's team kind: a manager with no tools of its own and two specialists. The dispatch specialist proposes which technician to send. The manuals specialist answers from the site manuals. The manager passes each message to the one it belongs to and returns that specialist's reply whole.
- **Systems and operations:** `field`. The dispatch specialist: `get_dispatch_view`, `get_job`, `save_dispatch_proposal`. The manuals specialist: `search_site_manuals`, `get_site_manual_page`.
- **Reply:** for a dispatch proposal, heading `Draft dispatch proposal. For the dispatcher. Not issued.` Table columns: `#`, `Job`, `Skill and urgency`, `Technician proposed`, `Why, from the measures`, `Mark`, one row for each open job. Marks: `proposed`, `worth a look`, `nobody fits`, `window cannot be reached`. The reason gives the system's figures for the technician proposed and for each technician passed over who was nearer. Proposals: `Proposal: for the dispatcher to assign` or `Proposal: for the dispatcher, with jobs nobody fits`. For a manual question, no table: the reply is exactly one of four answer states. Answered, with the manual and the page for every statement. The pages disagree, both given with their dates. The manuals are silent, said plainly, with the field supervisor named as the person who decides. Not a question for the manuals, a short refusal.
- **Stops for a person:** a dispatcher assigns every job. The agent assigns nothing, moves no appointment and tells no technician or customer anything. Where the manuals are silent it says so and gives no advice of its own, on safety least of all.
- **Changes:** `save_dispatch_proposal`, a draft, does not wait.
- **Cases:** the day's view with JOB-5101 to JOB-5105; JOB-5199; asked to assign JOB-5101 to TEC-5204 (refusal); asked why TEC-5202 was not proposed for JOB-5102 (a follow-up, answered from the measure); the isolator at SIT-174 (one page); the torque of the antenna clamp bolts (two pages that disagree); ice on the ladder at SIT-173 (silent, no advice); a dispatch question and a manual question in one conversation, each reaching its own specialist.
- **Also tried with documents:** the manual questions with the site manuals as documents in a knowledge source, as a draft. Recorded as it comes out.

## The desks of this area

See [10-desks.md](10-desks.md). Network operations desk: Fault Diagnosis, beside the agents of area 1. Predictive Maintenance has no desk: its result is sent to the maintenance planners. Field Operations is used in chat, and its dispatch proposal is read in the dispatcher's view.

## What open source gave this area

See [OPEN-SOURCE-REVIEW.md](../OPEN-SOURCE-REVIEW.md).
