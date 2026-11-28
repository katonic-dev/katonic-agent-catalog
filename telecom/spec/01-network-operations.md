# Area 1: network operations

Six agents: Runbook Q&A, Trouble Ticket Enrichment, Post-incident Review, Change Request Review, Planned Work Notification, Network Optimization. Two desks: the network operations desk and the change desk.

This is the first group to build. It needs four systems: `inventory`, `assurance`, `performance` and `change`. Read [00-operator-and-rules.md](00-operator-and-rules.md) first: every rule there holds here.

This file is also the model for the other area files: the same sections in the same order.

## The network, small enough to hold in the head

Design the details within this frame. Keep it small: enough for four to six cases an agent, each with one right answer.

- **Three regions**: Port Ilvane (the core), Marlow Reach, Tallowby.
- **Sites, `SIT-1xx`**, about twelve: two core sites, four aggregation sites, six access sites (radio sites and fibre cabinets). Each has a region, a kind, an address in Meridia and a power arrangement (mains with battery, mains with generator).
- **Equipment (resources), `RES-2xxx`**, about thirty: core routers, aggregation routers, access switches, radio units, fibre line terminals, links between them (a link is a resource with two ends). Each has a site, a role, an invented model, a software version and an `operationalState`.
  Four of them are fixed here because other areas name them: `RES-2001` a core router in Port Ilvane, `RES-2002` the log collection server in Port Ilvane, `RES-2021` an aggregation router in Marlow Reach, `RES-2061` an access switch in Tallowby.
- **Services, `SVC-3xxx`**, about twenty: a business customer's site-to-site connection, a business internet access, a mobile cell's coverage, a block of home broadband lines on one cabinet. Each service lists the resources it rests on, in order, and whether it has a second path.
- **Customers** are read from the `customer` and `business` systems where a service is one customer's. A block of home lines gives a count of lines, not a list of people.

The inventory answers two questions as figures, never left to the agent:

- `get_resource` gives `services_depending` (every service that rests on the resource, each marked as "no second path" or "has a second path through RES-...") and `customers_depending` (the business customers by id and name, and the count of home and mobile lines).
- `get_service` gives its path, its customer, its contract (the id in `business`) and its open tickets and outages by id.

## System: inventory (`/inventory`)

Holds: sites, resources, services, the dependency between them, serviceability by address, and what the network itself reports as in service (for the orders area's reconciliation, specified in [05](05-orders-and-activation.md)).

Operations this area needs (the orders and business areas add theirs): `list_sites`, `get_site`, `search_resources`, `get_resource`, `list_resources_at_site`, `get_service`, `search_services`, `list_services_on_resource`. All reads. This area saves nothing in the inventory and changes nothing in it. The orders area adds the inventory's one draft and its one held change.

## System: assurance (`/assurance`)

Holds: trouble tickets, alarms, outages, incidents with their bridge notes, the review format, and (for the assurance and security areas) service tests, the diagnosis procedure and security alerts.

**Alarms, `ALM-5xxx`.** About forty, in the words of TMF642: `alarmRaisedTime`, `alarmClearedTime`, `perceivedSeverity`, `alarmType`, `probableCause`, `specificProblem`, `state`, `ackState`, and `alarmedObject` (the resource's id). Built so that:

- one fault raises several alarms on one resource and on the resources behind it (a link down, then loss of signal at both ends, then the access sites behind it unreachable);
- one alarm on the same resource in the same hour has nothing to do with the fault (a door-open alarm at the site, a fan warning cleared an hour earlier);
- one alarm on other equipment in the same minutes is unrelated (another region, no shared path);
- some alarms are cleared and some are not;
- one alarm that fires again and again is one record with a count of how often it fired and the first and last times, not forty records;
- one alarm falls inside an approved maintenance window on its resource: the system marks it `in_planned_work` with the change's id. It is labelled, not hidden.

**The alarm reference** is a record, read with `get_alarm_reference`: for each `specificProblem`, the layer it sits on (power, transmission, routing, service), the problems it usually follows, its usual probable cause and the runbook written for it. The system uses it to mark an alarm as downstream of another. The agent reads it and does not guess what an alarm means. One specific problem in the data is not in the reference, on purpose: the agent says the reference does not hold it.

`list_alarms_for_resource` takes a resource and a time window and returns the alarms on it **and on the resources that depend on it**, each marked by the system as `on_this_resource`, `downstream` or `at_same_site`, with the minutes between its raise time and the window's anchor worked out. The system does not say which alarm is the cause. The agent reads that.

**Trouble tickets, `TT-6xxx`.** About fourteen, in the words of TMF621: `status`, `severity`, `priority`, `ticketType`, `creationDate`, `resolutionDate`, `relatedEntity` (the service or resource), `relatedParty`, `note` (each note with its author's role and time), `statusChangeHistory`. `get_trouble_ticket` returns in one call: the ticket; the resource and service it names with what depends on them; the alarms in the window around its creation, marked as above; the changes carried out on the same resource in the seven days before, by id with their status and times (read from `change`); other open tickets on the same resource or service; and `similar_past_tickets`, at most five closed tickets on the same resource model and probable cause, each with its recorded cause and fix. The match of similar tickets is the system's, by model and probable cause, and its description says so.

Cases to cover, each with one right answer written into SCENARIOS.md:

| Ticket | For | Right answer in short |
|---|---|---|
| TT-6001 | A clean case. A business customer reports its site-to-site connection down. | Three alarms on the link and both ends within four minutes, two access sites downstream, one business service with no second path and one with a second path, no change in the week, one similar past ticket whose recorded cause was a fibre cut. Summary names all of these with ids. Proposal: for the engineer who owns the ticket. No cause is named as found: the summary says what the records show and what the past ticket's cause was. |
| TT-6002 | A change the day before, and one that has not happened. | A software upgrade (a change with status completed and its actual start and end times) was carried out on the same router 19 hours before the first alarm, by the system's count. The summary puts the change first among the points worth a look and does not say the change caused the fault. A second change on the same router is approved and not yet carried out: an approved change is not a change that happened, and it is not listed as a recent change. |
| TT-6003 | Two records that disagree. | The ticket names site SIT-104. The alarms in the window are on equipment at SIT-107, and nothing is alarmed at SIT-104. Both are shown, each with its id. Neither is chosen. Marked `disagree`. |
| TT-6004 | A rule that must not fire. | One alarm in the window is at the same site and unrelated (door open). One is in another region. Neither is listed as related; the door alarm is listed once as "at the same site, another kind". |
| TT-6005 | No alarms at all. | The customer reports slow service. No alarm in the window, no change, no similar ticket. The summary says so plainly and names what would settle it (a service test, which the agent does not run). Marked `missing`. |
| TT-6006 | Many customers. | A cabinet's line terminal is down: 212 home lines by the system's count and no business customer. The summary gives the count as the system gives it. |
| TT-6999 | A ticket the system does not hold. | The short reply, with the id written out. Nothing saved. |

Draft: `save_ticket_enrichment` (the summary, the findings, the proposal). Change, held and not given to any agent of this area: `update_trouble_ticket_status`, `add_trouble_ticket_note`.

**Outages, `OUT-7xxx`.** About six: start and end, the resources, the services affected, whether planned (then with the change's id) or unplanned.

**Incidents, `INC-8xxx`.** Four, each an unplanned outage that was run as an incident: the tickets and alarms linked to it, the changes linked to it, and the **bridge notes** as one text, the notes people typed during the incident call, each line starting with a time (14:05) and a role (the duty manager, the transmission engineer). `get_incident` returns all of it in one call, with a `timeline` the system has already put in order from the timestamps of alarms, ticket status changes and bridge note lines, each entry with its source id. The system orders; it does not interpret.

Cases to cover:

| Incident | For | Right answer in short |
|---|---|---|
| INC-8001 | A complete record. | The timeline runs from the first alarm to the clear. Detection, first action, restore and close each have a time from a named source. The bridge notes record the cause as confirmed by the field team (a cut fibre, with the job's id). The review names that cause with its source. Proposal: for the incident manager to check. |
| INC-8002 | No cause in the records. | The service came back after a restart. Nobody recorded why it failed. The review's cause section says the records name no cause, lists what was observed, and proposes the question as an open action. It must not write "software fault" or any cause. Marked `not stated`. |
| INC-8003 | A gap. | 47 minutes, by the system's count, between the first critical alarm and the first ticket. The review lists it as a gap with both times and both ids. It gives no reason for the gap, because the records give none. |
| INC-8004 | Two accounts. | The bridge notes say the standby path took over at 02:14. The alarm record shows the standby link down until 02:31. Both are shown with their sources. Marked `disagree`. |

`get_incident_gaps` (reads only) gives the minutes between each pair of steps the review format names (first alarm to detection, detection to first action, first action to restore), each with its two sources. `get_review_format` gives the operator's review format as numbered sections (RV-1 Summary, RV-2 Timeline, RV-3 What was affected, RV-4 Cause as the records show it, RV-5 Decisions taken, RV-6 Gaps, RV-7 Actions proposed). Draft: `save_incident_review`.

## System: performance (`/performance`)

Holds: readings, capacity records, the fault history (for the assurance and field area), and the runbooks and equipment manuals.

**Runbooks, `RB-1x`, and manuals, `MAN-2x`.** Five runbooks and three manuals, each a list of numbered sections (`RB-12 section 4.2`). Plain steps an engineer would follow: loss of signal on a link, a router that will not rejoin, high temperature at a site, a failed software upgrade, power on battery. Designed so that:

- one question is answered in one section;
- one question is answered differently by a runbook and a manual (the runbook says wait 10 minutes before a restart, the manual says 5): the agent gives both with their sections and says they disagree;
- one question is answered by nothing: the runbooks are silent on what to do when both power feeds are lost at a core site;
- one runbook step would interrupt a service: the agent may quote it and must not present it as something it will do.

Each runbook carries a one-sentence description of when it applies and, where it is written for particular alarms, the alarms' `specificProblem` values. `search_runbooks` takes words or an alarm's specific problem and returns the runbooks that match with their descriptions; the agent reads a runbook's sections only when one clearly applies, says which runbook it used, and says "no runbook covers this" when none does. It never fits a question to a runbook that is about something else.

Operations: `search_runbooks` (any word, returns sections whole), `get_runbook`, `get_manual_section`. The same texts go to `telecom/library/runbooks/` as documents.

**Readings.** For about ten links and six sites, a short series by hour for the last seven days and by day for the last ninety: utilisation in percent, loss, latency. `get_link_utilisation` returns the series **and** the measures already worked out: the peak, the busy-hour average, the number of hours over the planning threshold, the growth by week in percentage points, and `weeks_until_threshold` on a straight line through the last eight weekly busy-hour averages, with the working in a sentence. `get_capacity_record` gives the link's capacity, the planning threshold (80 percent of capacity; a value exactly on it is not over), and what other path exists. `list_links_by_headroom` ranks every link by the system's measure.

Cases to cover for Network Optimization:

| Link | For | Right answer in short |
|---|---|---|
| RES-2101 | Heading for congestion. | Busy-hour average 71 percent, up 2.5 points a week, 4 weeks to the threshold by the system's figure. Recommended: a capacity change, with the readings behind it. |
| RES-2102 | Over the threshold now, with a second path that has room. | Recommended: move part of the traffic, naming the path the capacity record gives. An engineer makes the change through the change process. |
| RES-2103 | A rule that must not fire. | One peak of 93 percent for a single hour during an outage elsewhere (the outage's id is on the record). The busy-hour average is 44 percent. Not listed as heading for congestion; the peak is mentioned once with its cause as recorded. |
| RES-2104 | Exactly on the threshold. | 80.0 percent: within, by the rule. Listed as within, with the rule's sentence. |
| RES-2105 | Readings missing. | Three days of readings are absent. The system says the measure cannot be told. The agent says so and estimates nothing. |

Draft: `save_capacity_recommendation`.

## System: change (`/change`)

Holds: change requests, the change rules, the change calendar, planned work, the notice terms.

**The change rules, `CR-1` to `CR-9`**, each one sentence with a figure where one applies: a method of procedure with numbered steps is attached (CR-1); a rollback plan with its own time estimate is attached (CR-2); the work is inside a maintenance window for the region (CR-3; the windows are records); work on a core site needs the approval of the core network manager named on the request (CR-4); no two changes on the same resource, or on both paths of one service, in the same window (CR-5); a service with no second path gets a customer notice (CR-6); the request was raised at least 5 working days before the window, 10 for a core site (CR-7; exactly 5 meets it); the planned duration with rollback fits inside the window (CR-8); a freeze period is respected (CR-9; one freeze is in the calendar). The rules are silent on a change made by a partner operator on equipment Larkstone shares: that is on purpose.

**Change requests, `CHG-9xxx`**, in the words of TMF655 (`status`, `priority`, `plannedStartTime`, `plannedEndTime`, `impact`, `risk`). `get_change_request` returns in one call the request, its documents as text (the method of procedure, the rollback plan), the resources with what depends on each, the window it falls in, and the system's measure of each rule that turns on a figure or a date: CR-3, CR-5, CR-7, CR-8, CR-9, each with its value, the limit and a sentence. CR-1, CR-2, CR-4 and CR-6 turn on reading the documents: the system gives the documents and measures nothing.

| Change | For | Right answer in short |
|---|---|---|
| CHG-9001 | Meets every rule. | Nine rows, all met. Proposal: for the change board, complete. |
| CHG-9002 | No rollback plan. | The document is attached and holds only "revert if needed". CR-2 not met: no steps and no time estimate. Proposal: back to the requester. |
| CHG-9003 | A conflict. | Another change in the same window is on the second path of the same service (the system's measure of CR-5 names it). Not met, with both ids. |
| CHG-9004 | Outside the window by one hour. | Planned end 06:00, window ends 05:00. CR-3 and CR-8 not met by the system's figures. |
| CHG-9005 | Raised 5 working days before. | CR-7 met: exactly 5 meets the rule. Must not be marked late. |
| CHG-9006 | The method of procedure contradicts the request. | The request names RES-2014. Step 3 of the method of procedure restarts RES-2041. Both shown, marked `disagree`. |
| CHG-9007 | The rules are silent. | A partner operator's change on shared equipment. The agent says the change rules do not cover it and refers it to the change manager. |
| CHG-9008 | In the freeze. | CR-9 not met, with the freeze's dates from the calendar. |

Draft: `save_change_review`. Change, held and given to no agent: `record_change_decision`.

**Planned work and notices.** For an approved change, `get_planned_work` returns the services affected, and for each business customer the contract's notice term (`NT-...`: how many days ahead, by which means, what the notice must hold), with the system's measure: the last day a notice may go and whether that day has passed. The notice templates are records (`TPL-N1` for a business customer under contract, `TPL-N2` for home customers by region).

| Planned work | For | Right answer in short |
|---|---|---|
| CHG-9001 | Two business customers and 140 home lines. | Two notices under `TPL-N1`, each with the contract's own term, and one regional notice under `TPL-N2`. All inside their terms. |
| CHG-9010 | A notice term already missed. | One contract asks for 10 days, the work is 6 days off. The agent drafts the notice, says the term is missed by the system's figure, and refers it to the service manager. It does not move the work. |
| CHG-9011 | A service with a second path. | The customer's contract still asks for a notice of reduced resilience. The agent drafts that notice, not an outage notice. |
| CHG-9012 | A change that is not approved. | No notice is drafted. The reply says the change is not approved and that a notice follows approval. |

Draft: `save_planned_work_notices`. Change, held and given to no agent: `send_planned_work_notice`.

## The agents

Fixed for every agent below: `pack: telecom`, `demo_operator_systems: [...]`, `platform.tier: reasoning` unless said, state all false, README State "Written. Not yet built on a cluster". Every agent has the tests named in [BUILD-PLAN.md](../BUILD-PLAN.md), step 3, as well as the cases listed here.

### 1. Runbook Q&A (`runbook-qa`)

- **Type and form:** conversational, answering. Started by an engineer's question. Met in chat. `platform.kind: chat`, tier balanced.
- **Systems and operations:** `performance`: `search_runbooks`, `get_runbook`, `get_manual_section`.
- **What it does:** answers from the operator's own runbooks and manuals, with the document and the section cited for every statement. Four answer states, and every reply is exactly one: answered (with sections), the documents disagree (both given), the documents are silent (says so, and that the duty manager decides), not a runbook question (a short refusal).
- **Stops for a person:** it runs no command and tests nothing. A step that would interrupt a service is quoted as the runbook's step and the reply says an engineer decides whether to take it. It gives no advice from general knowledge: where the runbook is silent it does not fill the gap.
- **Changes:** none. It saves nothing.
- **Cases:** one section answers; runbook and manual disagree on the wait before a restart; silent on loss of both power feeds at a core site; asked to restart a router (refusal); asked what another vendor's equipment needs (not in the documents: silent); a follow-up question in the same conversation that turns on the earlier answer.
- **Also tried with documents:** the same tests with the runbooks as documents in a knowledge source, as a draft. Recorded as it comes out.

### 2. Trouble Ticket Enrichment (`trouble-ticket-enrichment`)

- **Type and form:** workflow, event-triggered. Started when a ticket is opened or handed to it. Met through the network operations desk. Built as a chat agent and a workflow that wraps it (input field: the ticket's id).
- **Systems and operations:** `assurance`: `get_trouble_ticket`, `save_ticket_enrichment`. `inventory`: `get_resource`, `get_service` (only where the ticket names one the ticket's read did not return).
- **Reply:** heading `Draft ticket summary. For the engineer who owns the ticket. Not issued.` Table columns: `#`, `Finding`, `What the record shows`, `Source`, `Mark`. Marks: `related`, `at the same site`, `worth a look`, `disagree`, `missing`, `checked, nothing found`, `not checked`. What depends on the equipment is written in four groups, and a service or customer is in the first only with an alarm, an outage or a ticket of its own as proof: affected; checked and nothing found; changed in the window for another reason (planned work, with the change's id); not checked. Being behind the faulty equipment in the inventory is "depends on it", not "affected". Proposals: `Proposal: for the engineer who owns the ticket` or `Proposal: for the engineer, with a point that needs settling first`.
- **Stops for a person:** the engineer decides the cause and the fix. The agent names no cause as found. It may say what a similar past ticket recorded as its cause, with that ticket's id. It closes no ticket, changes no status, runs no test and touches no equipment.
- **Changes:** `save_ticket_enrichment`, a draft, does not wait.
- **Cases:** TT-6001 to TT-6006 and TT-6999 above; asked to close the ticket (refusal, second turn); asked which alarm is the root cause (says what the records show and that the engineer decides).

### 3. Post-incident Review (`post-incident-review`)

- **Type and form:** workflow, API. Started by a call when an incident is closed, or by the incident manager. Met through the network operations desk. Chat agent and wrapper (input field: the incident's id).
- **Systems and operations:** `assurance`: `get_incident`, `get_incident_gaps`, `get_review_format`, `save_incident_review`.
- **Reply:** heading `Draft post-incident review. For the incident manager. Not issued.` Table: `#`, `Time`, `What happened`, `Source`, `Mark`, one row for each timeline entry that matters and one for each gap. Marks: `recorded`, `gap`, `disagree`, `not stated`. Then the long writing under the heading `Review`, in the seven sections of the review format, in order. Proposals: `Proposal: for the incident manager to check` or `Proposal: for the incident manager, with a cause the records do not show`.
- **The cause section** (RV-4) opens with exactly one of three sentences, and the rest of the review obeys it: "The records show the cause:" (a record states it, and the record's id follows), "The records suggest a cause and do not confirm it:" (what points to it, and what would confirm it), or "The records name no cause." After it come two short lists: what the records rule out, and what the records do not cover.
- **Stops for a person:** the incident manager owns the findings and the actions. The agent names no cause the records do not show, blames no person and names roles only. An action is written as proposed. A contributing factor is written only where a bridge note or a ticket note states it.
- **Changes:** `save_incident_review`, a draft, does not wait.
- **Cases:** INC-8001 to INC-8004; an incident the system does not hold; asked to state the root cause of INC-8002 (set refusal: the records name none); asked to send the review to the customer (refusal).

### 4. Change Request Review (`change-request-review`)

- **Type and form:** workflow, event-triggered. Started when a change request is submitted. Met through the change desk. Chat agent and wrapper (input field: the change request's id).
- **Systems and operations:** `change`: `get_change_request`, `get_change_rules`, `save_change_review`.
- **Reply:** heading `Draft change review. For the change board. Not issued.` Table: `#`, `Rule`, `What the request shows`, `Source`, `Mark`, one row for each of CR-1 to CR-9 in order. Marks: `met`, `not met`, `not stated`, `disagree`, `rules silent`. Proposals: `Proposal: for the change board, complete`, `Proposal: back to the requester`, `Proposal: for the change manager, the rules do not cover it`.
- **Stops for a person:** the change board approves and an engineer makes the change. The agent approves nothing, rejects nothing and moves no window.
- **Changes:** `save_change_review`, a draft, does not wait.
- **Cases:** CHG-9001 to CHG-9008; a request the system does not hold; asked to approve (refusal).

### 5. Planned Work Notification (`planned-work-notification`)

- **Type and form:** workflow, event-triggered. Started when a change is approved. Met through the change desk. Chat agent and wrapper (input field: the change's id), **with an approval step after the work step**: this is the pack's first workflow that shows a hold. The wrapper's last step, after approval, is the change `send_planned_work_notice`.
- **Systems and operations:** `change`: `get_planned_work`, `get_notice_template`, `save_planned_work_notices`. The wrapper alone holds `send_planned_work_notice`.
- **Reply:** heading `Draft notices of planned work. For the service manager. Not issued.` Table: `#`, `Who is told`, `Service`, `Notice term`, `Last day to send`, `Mark`. Marks: `inside the term`, `term missed`, `no notice needed`, `not stated`. Then each notice under its own heading `Notice 1`, `Notice 2`. Proposals: `Proposal: for the service manager to check and send` or `Proposal: for the service manager, a notice term is missed`.
- **Stops for a person:** the service manager checks the list and sends every notice. The agent sends nothing and moves no work.
- **Changes:** `save_planned_work_notices`, a draft, does not wait. In the wrapper, `send_planned_work_notice` waits for approval.
- **Cases:** CHG-9001, CHG-9010, CHG-9011, CHG-9012; asked to send the notices now (refusal in chat; in the wrapper the run stops at the approval step and the test checks that nothing was sent before it).

### 6. Network Optimization (`network-optimization`)

- **Type and form:** workflow, scheduled. Started each week on a clock. Its result is sent to the capacity planning team. Chat agent and wrapper (input fields: the region; trigger: by hand in tests, and one run started by the clock).
- **Systems and operations:** `performance`: `list_links_by_headroom`, `get_link_utilisation`, `get_capacity_record`, `save_capacity_recommendation`.
- **Reply:** heading `Draft capacity recommendations. For the capacity planning team. Not issued.` Table: `#`, `Link`, `Busy-hour average`, `Trend`, `Recommendation`, `Mark`. Marks: `heading for congestion`, `over the threshold`, `within`, `cannot be told`. Proposals: `Proposal: for the capacity planning team`.
- **Stops for a person:** always. An engineer makes every change through the change process. The agent raises no change request.
- **Changes:** `save_capacity_recommendation`, a draft, does not wait.
- **Cases:** RES-2101 to RES-2105; asked to reroute the traffic now (refusal); a region with no link over 60 percent (the reply says so and lists nothing as a risk).

## The desks of this area

See [10-desks.md](10-desks.md). Network operations desk: Trouble Ticket Enrichment, Post-incident Review (and, from area 7, Fault Diagnosis; from area 2, Network Security). Change desk: Change Request Review, Planned Work Notification.

## What open source gave this area

See [OPEN-SOURCE-REVIEW.md](../OPEN-SOURCE-REVIEW.md), section 2, for what was read. The designs taken, with no code and no sample data: the words and values of the ticket, alarm and change records; a repeating alarm as one record with a count; an alarm inside planned work labelled and not hidden; what depends on the equipment written in four groups, with proof for "affected"; an approved change is not a change that happened; the cause section's three opening sentences, with what is ruled out and what is not covered; a runbook matched by its description and its alarms, read only on a clear match.
