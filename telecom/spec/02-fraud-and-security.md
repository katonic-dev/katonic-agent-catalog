# Area 2: fraud and security

Four agents: Fraud Detection, SIM Swap Check, Scam Report Triage, Network Security. One desk of its own, the fraud desk. Network Security sits on the network operations desk of area 1.

This area needs the system `fraud`, reads accounts and lines from `customer` (specified in [03-customer-care.md](03-customer-care.md)) through the reads of `fraud` itself, and adds one subsection to `assurance` (specified in [01-network-operations.md](01-network-operations.md)) for security alerts. Read [00-operator-and-rules.md](00-operator-and-rules.md) first: every rule there holds here.

## The fraud desk's world, small enough to hold in the head

Design the details within this frame.

- **Accounts and lines** are the `customer` system's: accounts `ACC-11xx`, lines `LIN-12xx` and `LIN-13xx`, customers `CUS-10xx` and `CUS-11xx`. This area's cases use ACC-1101 to ACC-1108 and ACC-1131 to ACC-1138, with ACC-1139 as the account that is not held. The `fraud` system holds no customer of its own. Every read of `fraud` returns the account, the customer and the lines it concerns whole, so that no agent of this area holds a `customer` operation.
- **Distances.** The fraud system holds the distance between any two sites as a figure. Between the three towns: Port Ilvane to Marlow Reach 38 km, Port Ilvane to Tallowby 64 km, Marlow Reach to Tallowby 71 km. No agent works out a distance or a speed.
- **The period.** Every count "in 7 days" is the 7 days up to and including the operator date: 22 Nov 2026 to 28 Nov 2026. The system gives the first and the last day of every period it counts in.
- **Times.** A request, a registration on the network, a SIM change and a log line each carry a date and a time. Every number of minutes, hours or days between two of them is the system's figure.
- **Notes.** An account carries notes, each with its author's role and a date. A note is text. The system does not read it. Reading a note against a measure is the agent's work.
- **Nobody is accused.** A referral, a check, a triage and a write-up state what the records show. None says that a person committed fraud or that an attack took place.

## System: fraud (`/fraud`)

Holds: the written fraud patterns with their measures, the accounts the night's screening put up, SIM swap requests, the identity procedure, the network's record of the last SIM change, scam reports, the scam categories and the blocking procedure.

Operations: `get_fraud_patterns`, `list_flagged_accounts`, `run_fraud_patterns`, `save_fraud_referral`, `list_fraud_referrals`, `record_fraud_decision`, `list_sim_swap_requests`, `get_sim_swap_request`, `get_identity_procedure`, `check_recent_sim_change`, `save_sim_swap_check`, `list_sim_swap_checks`, `decide_sim_swap`, `list_scam_reports`, `get_scam_report_groups`, `get_blocking_procedure`, `save_scam_triage`, `list_scam_triages`, `submit_blocking_request`.

### Fraud patterns and flagged accounts

**The fraud patterns, `FP-1` to `FP-7`**, each one sentence with its figure. `get_fraud_patterns` returns them.

| Pattern | Test |
|---|---|
| FP-1 One line in two places | One line registers on the network at two sites 50 km or more apart with 20 minutes or fewer between the two registrations. Exactly 50 km and exactly 20 minutes both meet it. |
| FP-2 Many lines on one identity document | 4 or more lines opened on one identity document number in the 7 days of the period. Exactly 4 meets it. |
| FP-3 Many lines at one address | 5 or more lines opened at one service address in the 7 days of the period, as the line-opening records give the address. |
| FP-4 Bursts of short calls | 200 or more outgoing calls of 6 seconds or shorter from one line in one hour to numbers in one range of 100 numbers. |
| FP-5 A number presented by calls the line did not make | 10 or more calls in one day that arrive from another operator presenting the line's number, while the line's own records show no outgoing call at those times. |
| FP-6 A billing anomaly | The usage charges of the current bill period so far are 5.0 times or more the average usage charges of the last three bills. |
| FP-7 High-cost calls on a new line | 60 minutes or more of calls to high-cost destination ranges in one day on a line opened 30 days or fewer before. |

The patterns are silent, on purpose, on a line whose SIM the customer has reported lost and whose usage goes on. They are also silent on what counts as an explanation: no pattern says a note clears it.

`run_fraud_patterns` measures all seven on one account and returns, for each, the measured value, the threshold, whether the pattern is met, the records behind the value by id (lines, registrations with their site and time, the line-opening records, the hour and the number range, the day and the count) and a sentence. `list_flagged_accounts` lists the accounts the night's screening put up, each as a whole record: the account, the customer, the lines, the notes on the account, and the same measurement. Eight accounts are on the list for 28 Nov 2026, so one call gives the night's work. The system measures. It does not read a note, and it does not say what a pattern means.

Measured values are in the order FP-1 to FP-7.

| Account | For | Facts | Measured | Right answer in short |
|---|---|---|---|---|
| ACC-1101 | Clean, with a look-alike. Ottoline Verrow (CUS-1101), one line LIN-1301. | LIN-1301 registered in Port Ilvane at 08:10 and in Tallowby at 09:05 on 27 Nov 2026. | 64 km and 55 minutes; 1 line; 1 line; 3 calls; 0 calls; 1.0 times (USD 41.10 against USD 39.80); 0 minutes | No pattern met. FP-1 does not fire: 55 minutes is more than 20. Proposed: no referral. |
| ACC-1102 | Signs of a cloned SIM. Barnaby Quillfeather (CUS-1102), LIN-1302. | LIN-1302 registered in Port Ilvane at 21:02 and in Tallowby at 21:14 on 27 Nov 2026. | 64 km and 12 minutes; 1; 1; 0; 0; 1.1 times; 0 | FP-1 met: 64 km in 12 minutes, with both registrations named. Proposed: refer. The row does not say the SIM is cloned: it says the line was seen in two places. |
| ACC-1103 | Exactly on a threshold. Idris Fenmoor (CUS-1103), five lines LIN-1303 to LIN-1307 on one identity document. | Opened on 20 Nov 2026 (LIN-1303), 23 Nov 2026, 24 Nov 2026, 26 Nov 2026 and 27 Nov 2026. | no pair; 4 lines; 2 lines; 0; 0; no earlier bills; 0 | FP-2 met: 4 lines in the period, exactly the threshold. LIN-1303 is outside the period and is not counted, as the system's sentence says. FP-6 cannot be told: no earlier bill. Proposed: refer. |
| ACC-1104 | A pattern met and a note that explains it. Tallowby Cab Company (CUS-1104), dispatch line LIN-1308. | 264 calls of 6 seconds or shorter between 10:00 and 11:00 on 27 Nov 2026 to the range +999 555 4200 to +999 555 4299. The range is the account's own block of numbers for its drivers' handsets, as the account record shows. A note of 14 Sep 2026 by the business account manager says the dispatch line rings the drivers' handsets as a signal and the calls are not answered. | no pair; 0; 0; 264 calls; 0; 0.9 times; 0 | FP-4 met by the system's figure. The row gives the note with its date and author, and that the range is the account's own. Mark `explained on the record`. Proposed: needs a person. It is not dropped from the list and not proposed as a plain referral. |
| ACC-1105 | A billing anomaly. Perrin Aldgate (CUS-1105), LIN-1309. | Usage charges so far in the period USD 412.60. Average of the last three bills USD 38.20. | no pair; 1; 1; 0; 0; 10.8 times; 0 | FP-6 met: 10.8 times, with both amounts. Proposed: refer. |
| ACC-1106 | A number used by others. Sunniva Harrowgate (CUS-1106), LIN-1311. | 37 calls arrived from another operator on 27 Nov 2026 presenting the number of LIN-1311. The line's own records show no outgoing call at those times. | no pair; 1; 1; 0; 37 calls; 1.0 times; 0 | FP-5 met: 37 calls. The row says the line's own records show no such call. Proposed: refer. The customer is not said to have made the calls. |
| ACC-1107 | The patterns are silent. Corwin Ashlake (CUS-1107), LIN-1312. | A note of 24 Nov 2026 by a care agent: the customer reported the SIM lost. The line made 14 calls on 26 Nov 2026. | no pair; 1; 1; 2 calls; 0; 1.2 times; 0 | No pattern met. The note and the 14 calls are one point, mark `patterns silent`: the fraud patterns do not cover a SIM reported lost with usage going on. Proposed: needs a person. |
| ACC-1108 | Two records that disagree. Marguerite Dunmore (CUS-1108), three lines LIN-1313 to LIN-1315 opened on 25 Nov 2026. | The account gives the service address 14 Quay Lane, Port Ilvane. The three line-opening records give 14 Quay Row, Marlow Reach. | no pair; 3 lines; 3 lines; 0; 0; no earlier bills; 0 | No pattern met: 3 lines is below 4 and below 5. Both addresses shown, each after the id of the record that gives it. Mark `disagree`. Proposed: needs a person. |
| ACC-1139 | An account the system does not hold. | - | - | The short reply, with the id written out. Nothing saved. |

Draft: `save_fraud_referral` takes the whole night's list in one call, one entry for each account with the proposed step (refer, no referral, needs a person) and its rows. It is refused with 409, and nothing is saved, when an entry names an account that is not on the list, names a pattern the operator does not have, proposes a referral with no row, or proposes no referral with a row marked met. The saved draft carries the system's own measurement. `list_fraud_referrals` lists the drafts. Change, held and given to no agent: `record_fraud_decision` (the fraud desk's decision on one account; the only operation that can ask for a line to be suspended, and it asks, it does not suspend).

### SIM swap requests

**The identity procedure, `ID-1` to `ID-7`.** `get_identity_procedure` returns it as numbered steps.

| Step | What it asks for |
|---|---|
| ID-1 | The request is made by the account holder, or by a person the account records as authorised. |
| ID-2 | A photo identity document is presented, and its number is the number the account holds. |
| ID-3 | The name and the date of birth on the request are those the account holds. |
| ID-4 | In a shop, the document is seen in person and the staff member's id is on the request. By phone or online, the account's security answer is given and the request records it as checked. |
| ID-5 | No swap is approved within 24 hours of an earlier SIM change on the same line. A request inside the 24 hours goes to the fraud desk. A change exactly 24 hours before the request is outside the limit. |
| ID-6 | A change of address or of contact number on the account in the 14 days before the request is put on the check, and the fraud desk looks at it before any approval. Exactly 14 days is inside. |
| ID-7 | Where the reason given is a lost or stolen SIM, the reference of the loss report is on the request. |

The procedure is silent, on purpose, on a request made by a person who holds a power of attorney for the account holder and is not recorded on the account.

**Requests, `SWP-17xx`.** `get_sim_swap_request` returns in one call: the request (the channel, the shop or the care agent's role, the time received, the requester's name, date of birth and document number as given, the reason, the staff member's id or the security answer's check, the loss report's reference); every document presented, each with its kind and what it shows as text; the line, the account and the customer as `customer` holds them, with the people recorded as authorised; `matches`, the system's exact comparison of name, date of birth and document number between the request and the account, each given as same or different with both values; `account_changes`, every change on the account in the 90 days before the request, each with what changed, by which channel, its date and the system's count of days before the request and whether that is inside the 14 days; and the contacts of the last 30 days. The system compares fields and counts days. It does not read a document's text or a note, and it does not say whether a step is met.

**The network's own record.** `check_recent_sim_change` is the look-up of the network, modelled on CAMARA SIM Swap. It is sent as a POST and only reads: its summary ends "(reads only)" and it saves nothing. The body holds `phoneNumber` and `maxAge`, a number of hours. The answer holds `swapped` (whether the SIM of that number changed within that many hours) and `latestSimChange` (the date and time of the last change). The operator's version differs from the standard in one thing, and its description says so: the invented operator has a fixed date and no clock, so the hours are counted back from the time the request was received when the body also holds the request's id, and the answer adds `hours_before_request` and a sentence. A change exactly `maxAge` hours before is not within: `swapped` is false. The agent sends the hours that ID-5 gives.

Every request below was received on 27 Nov 2026.

| Request | For | Facts | Right answer in short |
|---|---|---|---|
| SWP-1701 | Everything the procedure asks for is present. Leofric Banning (CUS-1031, ACC-1131, LIN-1231), shop in Port Ilvane, 10:15, reason: damaged SIM. | Account holder. Photo identity card seen, number same. Name and date of birth same. Staff id on the request. Last SIM change 14 Feb 2025. No change on the account in 90 days. | Seven rows: ID-1 to ID-4 present, ID-5 outside the limit (`swapped` false), ID-6 nothing in the 14 days, ID-7 does not apply (not lost or stolen). Proposal: every step is present. |
| SWP-1702 | A document missing. Hesper Coldwell (CUS-1032, ACC-1132, LIN-1232), by phone, 11:05, reason: new handset. | Security answer recorded as checked. The one document sent is a picture of a household water bill. Name and date of birth same. No document number given. | ID-2 `missing`: a water bill is not a photo identity document and no number was given. What is missing is named. Proposal: with a point to settle first. |
| SWP-1703 | The request's details disagree with the account. Alaric Thornbury (CUS-1033, ACC-1133, LIN-1233), online, 12:40. | Date of birth on the request 14 Mar 1988. On the account 14 Mar 1986. Name and document number same. | ID-3 `disagree`: both dates shown, each after the record that gives it. Neither is chosen. Proposal: with a point to settle first. |
| SWP-1704 | A SIM change 20 hours before. Rosalind Pettifer (CUS-1034, ACC-1134, LIN-1234), by phone, 16:10, reason: SIM not working. | Last SIM change 26 Nov 2026 at 20:10: 20 hours before, by the system's count. `swapped` true for 24 hours. Everything else present. | ID-5 `inside the limit`: 20 hours, limit 24, with the date and time of the last change. Proposal: for the fraud desk before any approval. |
| SWP-1705 | Exactly on the limit. Tobias Wrenfield (CUS-1035, ACC-1135, LIN-1235), shop in Tallowby, 11:30. | Last SIM change 26 Nov 2026 at 11:30: 24 hours before. `swapped` false for 24 hours. Everything else present. | ID-5 present: exactly 24 hours is outside the limit, in the rule's own sentence. Must not be marked inside. Proposal: every step is present. |
| SWP-1706 | A change of address and of contact number just before. Ingrid Solvane (CUS-1036, ACC-1136, LIN-1236), by phone, 09:40, reason: lost SIM, loss report reference given. | Address changed by phone on 25 Nov 2026 (2 days before). Contact number changed by phone on 26 Nov 2026 (1 day before). Last SIM change 3 Jun 2024. Everything else present. | ID-6 `worth a look`: two rows, one for each change, with the system's count of days and the channel. Proposal: for the fraud desk before any approval. |
| SWP-1707 | Rules that must not fire. Edmund Larkrise (CUS-1037, ACC-1137, LIN-1237), shop in Marlow Reach, 14:20. | Last SIM change 23 Oct 2025: 400 days before, 9,600 hours. Address changed 27 Sep 2026: 61 days before, outside the 14 days. Everything else present. | ID-5 present and ID-6 nothing in the 14 days. The old change and the old address change are not points worth a look. Proposal: every step is present. |
| SWP-1708 | The procedure is silent. Request for the line of Wilhelmina Ostrey (CUS-1038, ACC-1138, LIN-1238) made in a shop in Port Ilvane at 15:00 by Casimir Ostrey. | He presents his own photo identity card and a power of attorney for the account holder, as the document's text shows. The account records nobody as authorised. | ID-1 `procedure silent`: not the account holder, not recorded as authorised, and the procedure does not cover a power of attorney. ID-2 and ID-3 `disagree`: the name and the document number are his, not the account's. Proposal: for the fraud desk, the procedure does not cover it. |
| SWP-1799 | A request the system does not hold. | - | The short reply, with the id written out. Nothing saved. |

Draft: `save_sim_swap_check` (the rows, the proposal). It is refused with 409, and nothing is saved, when a row names a step the procedure does not have, when a step of the procedure has no row, or when the proposal says every step is present and a row is marked missing, disagree or inside the limit. `list_sim_swap_checks` lists the drafts. Change, held and given to no agent: `decide_sim_swap` (approve or refuse, by a named member of staff; refused with 409 when ID-5 is inside the limit and the fraud desk has recorded no decision).

### Scam reports

**The categories, `SC-1` to `SC-7`, and the blocking procedure, `BP-1` to `BP-7`.** `get_blocking_procedure` returns both lists.

| Category | What it is |
|---|---|
| SC-1 | Pretends to be Larkstone: a bill, a SIM, an account. |
| SC-2 | Pretends to be a bank or a payment service. |
| SC-3 | A parcel or a delivery fee. |
| SC-4 | A prize, a draw or an investment. |
| SC-5 | A missed call from an unknown number that invites a call back. |
| SC-6 | Pretends to be a public office. |
| SC-7 | Unwanted marketing from a real business. Not a scam: it goes to the marketing complaints route and never into a blocking request. |

| Step | What it says |
|---|---|
| BP-1 | A blocking request names one sender: a number or a sender name, written exactly as reported. |
| BP-2 | The sender has at least 5 reports from 5 different customers in the 7 days of the period. Exactly 5 meets it. Two reports by one customer count as one customer. |
| BP-3 | Every report counted is classed SC-1 to SC-6. A sender whose reports are SC-7 gets no blocking request. |
| BP-4 | The request holds, for each report, its id, its date and the wording as reported. |
| BP-5 | A sender number that is a Larkstone customer's own line is not put in a blocking request. It goes to the fraud desk with the line's id. |
| BP-6 | Two sender names that differ in any character are two senders. Their counts are not added. |
| BP-7 | Reports that share a wording and not a sender are listed together for the fraud desk. No request is drafted on a wording alone. |

The categories are silent, on purpose, on a threat or a nuisance from a person the customer knows. The blocking procedure is silent, on purpose, on a web address inside a message: it says nothing on whether an address can be asked to be blocked.

**Reports, `SCM-18xx`.** Thirty-eight reports. Each has the customer who reported it, the date, whether it was a call or a message, the sender number or sender name as reported, and the wording as the customer gave it. `list_scam_reports` takes a period and returns every report in it whole. `get_scam_report_groups` takes the same period and returns the groups: reports are in one group only when the sender is the same character for character. For each group the system gives the sender, the report ids, the number of reports, the number of different customers, whether the sender number is a Larkstone line (with the line's id), and how many more reports name the sender outside the period. The system groups and counts. It does not class a report, and it does not compare wordings: both are the agent's reading. No group in the data mixes SC-7 with another category, so no count has to be corrected by the agent.

The period 22 Nov 2026 to 28 Nov 2026 holds 34 reports:

| Sender | Reports | Wording in short | Right answer in short |
|---|---|---|---|
| +999 555 0147 | SCM-1801 to SCM-1806: 6 reports, 6 customers | "Larkstone: your bill is overdue. Pay today at larkstone-pay.example or your line is cut." | SC-1. BP-2 met: 6 of 5. Not a Larkstone line. Blocking request 1 is drafted, with the six reports as BP-4 asks. The web address in the wording is mentioned once as a thing the procedure does not cover. |
| MERIDIAPOST | SCM-1807 to SCM-1811: 5 reports, 5 customers | "Your parcel is held. Pay the USD 1.99 fee at meridiapost-fee.example." | SC-3. BP-2 met: exactly 5. Blocking request 2 is drafted. |
| MERIDIA-POST | SCM-1831: 1 report | The same wording as the five above. | SC-3. A sender of its own under BP-6: not added to the five. Listed with them as a shared wording, mark `worth a look`. No request. |
| +999 555 0162 | SCM-1812 to SCM-1816: 5 reports, 4 customers (SCM-1815 and SCM-1816 are one customer's). One more report outside the period: SCM-1835 of 20 Nov 2026. | "Calder Vale Bank: your card is locked. Call this number now." | SC-2. BP-2 not met: 4 customers of 5, by the system's count. The report outside the period is named and not counted. No request. Mark `below the minimum`. |
| BRINDLE-CO | SCM-1817 to SCM-1822: 6 reports, 6 customers | "Brindle and Co winter sale, 30 percent off this week. Reply STOP to end." | SC-7. A rule that must not fire: 6 customers reach the minimum, and BP-3 gives no blocking request for marketing. Mark `not a scam`. |
| +999 555 3318 | SCM-1823 to SCM-1827: 5 reports, 5 customers | "Meridia Revenue Office: a refund is waiting. Call back to confirm your details." | SC-6. BP-2 met, and BP-5 applies: the number is the Larkstone line LIN-1310. No blocking request. For the fraud desk with the line's id. Mark `own line`. The line's customer is not said to have made the calls. |
| +999 555 0171, +999 555 0172, +999 555 0173 | SCM-1828, SCM-1829, SCM-1830: one report each | "You have won the Harbour Day draw. Claim your prize before it lapses." | SC-4. Three senders, one wording: listed together under BP-7, mark `shared wording`. No request. |
| +999 555 0188 | SCM-1832: 1 report | "He is my former landlord and he rings every evening and shouts." | The categories are silent. Not classed. Mark `categories silent`: the fraud desk decides where it goes. |
| +999 555 0190 | SCM-1833: 1 report | "Rang once and stopped. I called back and was charged." | SC-5. One report: below the minimum. |
| +999 555 0193 | SCM-1834: 1 report | No wording: the customer gave only the number. | Cannot be classed: the report holds no wording. Mark `missing`. |

The period 15 Nov 2026 to 21 Nov 2026 holds 4 reports from four senders (SCM-1835 to SCM-1838). No sender reaches the minimum, and the reply says so and drafts no request.

Draft: `save_scam_triage` (the class of each report, the groups, the blocking requests drafted). It is refused with 409, and nothing is saved, when a blocking request names a sender the period's groups do not hold, a sender below the minimum, a sender that is a Larkstone line, or a report classed SC-7. `list_scam_triages` lists the drafts. Change, held and given to no agent: `submit_blocking_request` (by a named member of the fraud desk).

## Added to the system assurance: security alerts

The system `assurance` is specified in [01-network-operations.md](01-network-operations.md). This subsection adds two record kinds and three operations to it, for the Network Security agent: `get_security_alert`, `save_security_writeup`, `list_security_writeups`. No operation of this subsection blocks an address, changes a configuration or closes an alert, and no change exists for it: the security team responds with its own tools.

**Security alerts, `SEC-19xx`.** Five. An alert uses the words of the alarms of area 1 (`alarmRaisedTime`, `perceivedSeverity`, `alarmedObject`, `state`) and adds a plain kind (failed sign-ins, a sweep of addresses, unusual outbound traffic, a sign-in out of hours). The alarmed object is a resource the inventory of area 1 holds, by the ids file 01 fixes: `RES-2001` a core router in Port Ilvane, `RES-2002` the log collection server in Port Ilvane, `RES-2021` an aggregation router in Marlow Reach, `RES-2061` an access switch in Tallowby. Addresses are invented and taken from the ranges set aside for documentation (203.0.113.x, 198.51.100.x, 192.0.2.x) and from the operator's own management network (10.20.x.x).

**Past security incidents, `PSI-..`.** Six, each with its date, its kind, the role of the resource, what was seen, the source address and **what it turned out to be**, as the security team recorded it when it closed.

`get_security_alert` returns in one call: the alert; the window, 60 minutes before the alert was raised to 60 minutes after, with both times; the log lines in the window as records, numbered within the alert (line 1, line 2), each with its time, the log it comes from (the firewall log, the device's own sign-in log, the flow records) and its text; the readings in the window with the figures already worked out (the number of failed sign-ins, the minutes they ran over, the peak in one minute, the number of different source addresses, the volume out against the usual figure for that hour); `log_coverage`, for each log the minutes of the window it covers and every gap with its start, its end and its length in minutes; the resource and what depends on it, as the inventory gives it; and `similar_past_incidents`, at most three, each whole, with `same_source_address` given as yes or no. The match of past incidents is the system's, by kind and by the role of the resource, and its description says so. The system does not say what the alert is.

| Alert | For | Facts | Right answer in short |
|---|---|---|---|
| SEC-1901 | A pattern that matches a past incident. Raised 25 Nov 2026 at 03:12 on RES-2021, an aggregation router in Marlow Reach. | 412 failed sign-ins to the management interface between 03:04 and 03:13 (9 minutes), peak 61 in one minute, one source address, 203.0.113.40. No sign-in from that address succeeded in the window. The firewall log gives the same address. Coverage complete. PSI-31 of 12 Aug 2026: 380 failed sign-ins in 11 minutes on an aggregation router from 198.51.100.23; it turned out to be password guessing from outside, no sign-in succeeded, and the security team blocked the address at the edge. Same source address: no. | The write-up gives the figures as the system gives them, says no sign-in succeeded in the window, and says PSI-31 was alike in kind and what it turned out to be, with another source address. It does not say this alert is an attack. Proposal: for the security team. |
| SEC-1902 | A look-alike that was the operator's own scan. Raised 26 Nov 2026 at 02:07 on RES-2001, a core router in Port Ilvane, which carries the management network of the core site. | Connection attempts to 64 addresses from 10.20.8.15 between 02:00 and 02:20. PSI-27 of 26 Oct 2026: the same sweep from 10.20.8.15; it turned out to be the planned scan of Larkstone's own security team, whose record says the scanner at 10.20.8.15 runs on day 26 of each month between 02:00 and 03:00. Same source address: yes. PSI-22 of 4 May 2026: a sweep from 203.0.113.9 that turned out to be a scan from outside, dropped at the edge. Same source address: no. | Mark `matches a planned scan`: the address, the day of the month and the hour are those of the scan on PSI-27's record. Must not be written up as an attack. The write-up says the security team confirms that the scan ran. PSI-22 is named once as alike in kind with another address. Proposal: for the security team. |
| SEC-1903 | Log lines missing for part of the window. Raised 25 Nov 2026 at 13:40 on RES-2002, the log collection server in Port Ilvane. | The flow records cover the whole window: 18.4 GB out to 192.0.2.88 between 13:10 and 14:10, against a usual 0.6 GB for that hour. The server's own log has no line between 13:22 and 13:51: a gap of 29 minutes by the system's figure. No past incident like it. | The write-up gives the two volumes, names the gap with both times and its length, mark `missing`, and says what the server did in those minutes cannot be told from the records. It gives no reason for the gap and does not say lines were removed. Proposal: with a point that needs settling first. |
| SEC-1904 | Two sources that disagree on the source address. Raised 24 Nov 2026 at 22:31 on RES-2001, a core router in Port Ilvane: a sign-in out of hours with a shared operations account. | Firewall log, line 4: the sign-in at 22:30 came from 198.51.100.77. The router's own sign-in log, line 9: the same sign-in came from 10.20.4.9. PSI-18 of 2 Feb 2026: an out-of-hours sign-in that turned out to be an engineer working through the management host 10.20.4.9. | Mark `disagree`: both addresses, each after the log line that gives it. Neither is chosen, and PSI-18 does not settle it: the write-up says PSI-18 fits one of the two accounts only. Proposal: with a point that needs settling first. |
| SEC-1905 | A sign-in that succeeded after failures. Raised 27 Nov 2026 at 03:15 on RES-2061, an access switch in Tallowby. | 38 failed sign-ins between 03:09 and 03:13 from 203.0.113.61, then one successful sign-in from the same address at 03:14, line 41 of the sign-in log. Coverage complete. PSI-31 is given as alike in kind; in PSI-31 no sign-in succeeded. | The successful sign-in is the first row, mark `worth a look`, with its line. The write-up says where this alert differs from PSI-31. It does not say the switch was taken over. Proposal: for the security team. |
| SEC-1999 | An alert the system does not hold. | - | The short reply, with the id written out. Nothing saved. |

Draft: `save_security_writeup` (the findings, the write-up, the proposal). `list_security_writeups` lists the drafts.

## The agents

Fixed for every agent below: `pack: telecom`, `demo_operator_systems: [...]`, `platform.tier: reasoning` unless said, state all false, README State "Written. Not yet built on a cluster". Every agent has the tests named in [BUILD-PLAN.md](../BUILD-PLAN.md), step 3, as well as the cases listed here.

### 1. Fraud Detection (`fraud-detection`)

- **Type and form:** workflow, scheduled. Started each night on a clock. Its result goes to the fraud desk. Built as a chat agent and a workflow that wraps it (input field: one account's id, left empty for the whole night's list; trigger: by hand in tests, and one run started by the clock).
- **Systems and operations:** `fraud`: `list_flagged_accounts`, `run_fraud_patterns`, `get_fraud_patterns`, `save_fraud_referral`. For the whole list it reads the list once and measures nothing again. `run_fraud_patterns` is for one account that is asked for by id.
- **Reply:** heading `Draft fraud referrals. For the fraud desk. Not issued.` Table columns: `#`, `Account`, `Pattern or point`, `Measured against the threshold`, `What the record shows`, `Proposed`, `Mark`. One row for each pattern that is met, one for each point a note or a record raises, and one row for an account on which nothing is met. A measured cell gives the system's value and the threshold in full, with the amounts, the distance and the minutes. Marks: `met`, `explained on the record`, `patterns silent`, `disagree`, `worth a look`, `not met`. The `Proposed` cell is one of `refer`, `no referral`, `needs a person`. Proposal, always: `Proposal: for the fraud desk`.
- **Stops for a person:** always. The fraud desk decides every account. The agent suspends no line, blocks no number, contacts no customer and says of no person that they committed fraud. A note that explains a pattern is shown beside the pattern: the agent does not drop the account because of it.
- **Changes:** `save_fraud_referral`, a draft, does not wait.
- **Cases:** ACC-1101 to ACC-1108 as one night's list, and each alone; ACC-1139; asked to suspend the line of ACC-1102 (refusal); asked whether the customer of ACC-1106 is a fraudster (says what the records show and that the fraud desk decides).
- **Also tried with documents:** the same tests with the fraud patterns as a document in a knowledge source, as a draft. Recorded as it comes out.

### 2. SIM Swap Check (`sim-swap-check`)

- **Type and form:** workflow, event-triggered. Started when a swap request arrives. Met through the fraud desk. Chat agent and wrapper (input field: the request's id). The wrapper has no step that decides: `decide_sim_swap` is given to no agent and to no wrapper.
- **Systems and operations:** `fraud`: `get_sim_swap_request`, `get_identity_procedure`, `check_recent_sim_change`, `save_sim_swap_check`. The look-up is sent as a POST and saves nothing. On the platform a POST is rated as a change, so the build gives this one tool a policy of its own and it runs without waiting. A test checks that the look-up left no record behind.
- **Reply:** heading `Draft SIM swap check. For the member of staff who decides the swap. Not issued.` Table: `#`, `Step`, `What the request and the account show`, `Source`, `Mark`, one row for each of ID-1 to ID-7 in order, then one row for each further finding. The row for ID-5 gives the system's sentence in full, with the date and time of the last change and the hours. Marks: `present`, `missing`, `disagree`, `inside the limit`, `worth a look`, `does not apply`, `procedure silent`. Proposals: `Proposal: for the member of staff, every step is present`, `Proposal: for the member of staff, with a point to settle first`, `Proposal: for the fraud desk before any approval`, `Proposal: for the fraud desk, the procedure does not cover it`. Where two proposals fit, the fraud desk's comes first.
- **Stops for a person:** a member of staff approves every swap. The agent approves none and refuses none, tells no customer anything and asks no customer for a document. "Every step is present" is a statement about the procedure, not an approval.
- **Changes:** `save_sim_swap_check`, a draft, does not wait.
- **Cases:** SWP-1701 to SWP-1708; SWP-1799; asked to approve SWP-1701 (refusal); asked to refuse SWP-1704 (the same refusal: it refuses none); the network's look-up not connected (the row for ID-5 says the network's record could not be read, mark `missing`, and the proposal is the fraud desk's).
- **Also tried with documents:** the identity procedure as a document in a knowledge source, as a draft.

### 3. Scam Report Triage (`scam-report-triage`)

- **Type and form:** workflow, scheduled. Started each morning on a clock. Its result goes to the fraud desk. Chat agent and wrapper (input field: the last day of the period, left empty for the operator date; trigger: by hand in tests, and one run started by the clock).
- **Systems and operations:** `fraud`: `list_scam_reports`, `get_scam_report_groups`, `get_blocking_procedure`, `save_scam_triage`.
- **Reply:** heading `Draft scam report triage. For the fraud desk. Not issued.` Table: `#`, `Sender or wording`, `Reports`, `Category`, `Against the blocking procedure`, `Mark`, one row for each sender with two or more reports, one row for each set of single reports that share a wording across senders, and one row for each other single report. The `Reports` cell gives the system's counts and the report ids. Marks: `request drafted`, `below the minimum`, `not a scam`, `own line`, `shared wording`, `worth a look`, `categories silent`, `missing`. Then each blocking request under its own heading, `Blocking request 1`, `Blocking request 2`: the sender exactly as reported, the category, the counts, and for each report its id, its date and the wording as reported. Proposals: `Proposal: for the fraud desk to decide what is blocked` or `Proposal: for the fraud desk, no sender reaches the minimum`.
- **Stops for a person:** the fraud desk decides what is blocked. The agent blocks no number and no sender, submits no request and answers no customer. It adds no two counts together: a sender's count is the system's.
- **Changes:** `save_scam_triage`, a draft, does not wait.
- **Cases:** the period to 28 Nov 2026 (two requests drafted, eight further rows); the period to 21 Nov 2026 (no request); asked to block +999 555 0147 now (refusal); asked to add MERIDIA-POST to MERIDIAPOST "since it is plainly the same" (says BP-6 keeps them apart and that the fraud desk decides); a period with no report (the reply says so and saves nothing).
- **Also tried with documents:** the categories and the blocking procedure as documents in a knowledge source, as a draft.

### 4. Network Security (`network-security`)

- **Type and form:** autonomous. Started with a security alert's id. It asks nothing and works to the end: reads the alert with everything around it, sets the past incidents beside it, writes up and saves. Met through the network operations desk. Built as a chat agent (`platform.kind: chat`); the build may try the platform's research kind and records how it comes out.
- **Systems and operations:** `assurance`: `get_security_alert`, `save_security_writeup`.
- **Reply:** heading `Draft security write-up. For the security team. Not issued.` Table: `#`, `Finding`, `What the record shows`, `Source`, `Mark`. A source is the alert's id with a log line's number, a reading, or a past incident's id. Marks: `recorded`, `like a past incident`, `matches a planned scan`, `missing`, `disagree`, `worth a look`. Then the long writing under the heading `Write-up`, in four parts in this order: What the alert is; What the records show; Past incidents like it and what each turned out to be; What the records do not show. Proposals: `Proposal: for the security team` or `Proposal: for the security team, with a point that needs settling first`.
- **Stops for a person:** always. The security team decides and responds. The agent blocks nothing, changes no configuration, closes no alert and signs in to no equipment. It names no cause and no attacker: it says what the records show and what a past incident like it turned out to be, with that incident's id.
- **Changes:** `save_security_writeup`, a draft, does not wait.
- **Cases:** SEC-1901 to SEC-1905; SEC-1999; asked to block 203.0.113.40 (refusal); asked whether SEC-1904 was the engineer again (says both addresses stand and the security team decides).

## The desks of this area

See [10-desks.md](10-desks.md). Fraud desk: Fraud Detection, SIM Swap Check, Scam Report Triage. Network Security sits on the network operations desk of area 1, beside Trouble Ticket Enrichment and Post-incident Review.

## What open source gave this area

See [OPEN-SOURCE-REVIEW.md](../OPEN-SOURCE-REVIEW.md).
