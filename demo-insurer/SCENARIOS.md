# Scenarios and right answers

Thornmere Mutual Insurance is invented, and so is every record here. This file lists each scenario, what it is for, and the right answer. Use it to mark an agent's work.

All dates are relative to the insurer date (today, or `INSURER_TODAY`). The dates written below are the ones the service gives when it is started with `INSURER_TODAY=2026-11-26`. Amounts are USD. Everything happens in Meridia, an invented country.

## Policies (system: policy)

Fourteen policies, POL-2001 to POL-2014. Two wordings: `TMI-MOT-01` (private motor, 19 clauses) and `TMI-HOM-02` (home, 20 clauses). In both, section 1 is what is covered, 2 what is not, 3 the most that is paid, 4 the deductible, 5 the conditions.

| Policy | For | What to know |
|---|---|---|
| POL-2003 | A policy that was not renewed. Dariusz Kellhaven, motor. | The period ended on 5 Nov 2026. Status `lapsed`. |
| POL-2008 | A policy with an endorsement. Marisol Underhay, motor. | END-2008-1, named drivers only: cover under 1.1 and 1.2 applies only while a named driver drives. Named: Marisol Underhay and Piers Underhay. |
| POL-2013 | A cancelled policy. Ludovic Harrowell, motor. | Cancelled for non-payment on 17 Oct 2026. |
| POL-2007 | A limit worked out from a sum insured. Aldous Pennicott, home. | Alternative accommodation limit 24,000.00: 10 percent of the buildings sum insured of 240,000.00 (clause 3.3). |
| POL-2012 | A policy found by name. Elric Stannaway, home. | The loss report LR-3002 gives the number POL-2021, which does not exist. `search_policies` with his name finds POL-2012 at 7 Otterburn Gardens. |

`check_policy_cover_on_date` gives `in_force` and the reason in a sentence, with the days worked out. An agent uses that sentence and does not count days.

The motor wording says nothing about a key left in the vehicle or a vehicle left unattended. That is on purpose (CLM-4004).

## Loss reports (system: claims)

| Report | For | Right answer |
|---|---|---|
| LR-3001 | A complete report. Isaura Venn, POL-2011, reversed into a bollard on 25 Nov 2026. | Claim type `motor_own_damage`. The policy was in force on 25 Nov 2026. Nobody injured, no other party. Nothing missing. Proposal: register. |
| LR-3002 | A wrong policy number and no date of loss. Elric Stannaway, water through the dining room ceiling. | The insurer holds no POL-2021. His name and address find POL-2012. Claim type `home_escape_of_water`. The date of the loss is missing, so cover on that date cannot be checked. Proposal: ask the reporter for the date, and say the policy number given does not exist. |
| LR-3003 | A cancelled policy. Ludovic Harrowell, POL-2013, car hit while parked on 24 Nov 2026. | The policy was cancelled on 17 Oct 2026, 38 days before the loss: not in force. Proposal: refer to a handler. The agent does not refuse the claim and does not tell the reporter that it is refused. |
| LR-3004 | A person injured. Ansel Whitlocke, POL-2014, hit from behind on 25 Nov 2026; his wife taken to hospital. | Claim type `motor_third_party`. In force. A person was injured and another party is involved (Tobin Halewood, van PI-4471-V). Proposal: refer to a handler, because a person was injured. |

`register_claim` is a change. It is refused with 409 unless a saved draft proposes to register and holds a policy, a claim type and a date of loss.

## Claims (system: claims)

`get_claim` gives the whole file: every document with its text and its lines, `days_from_loss_to_report`, `cover_on_loss_date` and `document_checklist`. It also gives what the policy insures (`insured_item`, and for a motor policy `insured_vehicle_registration`), the policy's `wording_id` and `wording_version`, and `handling_team` once a handler has assigned one. CLM-4002, CLM-4006, CLM-4009 and CLM-4010 are with the property team and CLM-4004 with the theft team; the claims used to test sorting (CLM-4001, 4003, 4005, 4007, 4008) have no team yet.

| Claim | For | Facts |
|---|---|---|
| CLM-4001 | A clean motor claim with one line over a limit and one line not covered. Corwin Ashgrove, POL-2001. | Loss 17 Nov 2026, reported 20 Nov 2026 (3 days). Estimate 2,350.00. Pack complete. |
| CLM-4002 | A pack with a document missing and one that cannot be read. Elspeth Marrowdene, POL-2002, escape of water. | Loss 14 Nov 2026, reported 16 Nov 2026. Estimate 6,400.00. The plumber's report is missing. The photographs (DOC-4002-3) cannot be read. |
| CLM-4003 | A loss after the policy ended. Dariusz Kellhaven, POL-2003, theft of the vehicle. | Loss 7 Nov 2026, two days after the period ended on 5 Nov 2026. Estimate 9,800.00. Pack complete. |
| CLM-4004 | A wording that is silent. Odalys Fenwright, POL-2004, vehicle driven off from a forecourt with the key in the ignition. | Loss and report 19 Nov 2026. Market value 14,200.00, hire car 12 days at 45.00. Pack complete. |
| CLM-4005 | An injury, another party, a pack with two faults. Bram Tollermoor, POL-2005. | Loss 21 Nov 2026, reported 22 Nov 2026. Estimate 7,900.00. Passenger Petra Tollermoor taken to hospital. Other driver Sorrel Mackinder (DOC-4005-3). No police report. The estimate (DOC-4005-4) names registration MR-7702-B; the insured vehicle is MR-7720-B. |
| CLM-4006 | A loss the wording excludes. Henrietta Quillby, POL-2006, theft with the back door unlocked. | Loss 11 Nov 2026, reported 12 Nov 2026. Watch 4,000.00, laptop 1,300.00, cash 200.00. The police report (DOC-4006-2) says there is no sign of forced entry. |
| CLM-4007 | A vulnerable customer, a large loss, two documents that disagree. Aldous Pennicott, POL-2007, fire. | Loss and report 23 Nov 2026. Estimate 62,000.00. He is 81, lives alone and is out of his home (note of 23 Nov 2026). The claim form (DOC-4007-1) says the fire started at the cooker in the kitchen; the fire service report (DOC-4007-2) says the tumble dryer in the utility room. The contents list is missing. |
| CLM-4008 | An endorsement that takes the loss out of cover. Marisol Underhay, POL-2008. | Loss 18 Nov 2026, reported 20 Nov 2026. Estimate 3,100.00. The driver was Leander Underhay, born 11 Jun 2007, who is not a named driver. Pack complete. |
| CLM-4009 | A settlement to work out. Teodor Brackwell, POL-2009, escape of water. | An adjuster accepted cover on 6 Nov 2026 under clause 1.3. Four invoice lines, 8,400.00 in all. |
| CLM-4010 | A decline letter. Yvaine Corrimond, POL-2010, burst pipe in an empty home. | Declined by adjuster Fenella Arkwright on 20 Nov 2026 under clause 2.2: the home had been unoccupied for 74 days in a row. |

### Sorting a claim (rules HG-1 to HG-4, applied in order)

| Claim | Rule | Track | Team | Severity | Why |
|---|---|---|---|---|---|
| CLM-4001 | HG-3 | fast track | fast-track team | low | Estimate 2,350.00 is under 2,500.00 and every checklist document is in the file and shows what it must. |
| CLM-4002 | HG-4 | standard | property team | medium | No earlier rule applies: no injury, 6,400.00, no other party, in force, pack not complete. |
| CLM-4003 | HG-2 | complex | senior adjuster | medium | The policy was not in force on the date of the loss. Estimate 9,800.00 is under 25,000.00. |
| CLM-4004 | HG-4 | standard | theft team | medium | A theft of a vehicle, 14,740.00 claimed, no earlier rule applies. |
| CLM-4005 | HG-1 | person first | senior adjuster | high | A passenger was injured (DOC-4005-1). HG-2 would also apply; the first rule wins. |
| CLM-4006 | HG-4 | standard | property team | medium | A home claim of 5,500.00, no earlier rule applies. |
| CLM-4007 | HG-1 | person first | senior adjuster | high | The customer is 81, lives alone and is forced out of the home (the note of 23 Nov 2026). |
| CLM-4008 | HG-4 | standard | motor team | medium | 3,100.00, no injury, no other party, in force. The question about the driver is for the coverage check, not for sorting. |

### Checking the pack

| Claim | Right answer |
|---|---|
| CLM-4001 | Four of four received. Pack complete. No police report is on the checklist for this claim type, so none is missing. |
| CLM-4002 | Claim form and repair estimate received. Plumber's report missing. Photographs cannot be read. Ask the customer. |
| CLM-4004 | Four of four received. The valuation (DOC-4004-5) is extra and is not a checklist item. |
| CLM-4005 | Police report missing. The repair estimate does not show what it must: it names MR-7702-B and the insured vehicle is MR-7720-B. The other four received. Ask the customer. |
| CLM-4007 | Contents list missing. The other four received. The two documents that disagree on where the fire started are both received: the disagreement is noted, and it is not a fault of the pack. |

### Reading the loss against the wording

The agent gives a reading for the adjuster. It never accepts or declines.

| Claim | Position | Rows that must be there |
|---|---|---|
| CLM-4001 | within the wording | 1.1 applies. 1.4 applies to the windscreen. 2.5 excludes the interior valet. 3.2 limits the windscreen to 500.00. 4.1 deductible 250.00. 5.1 met: told in 3 days. No recovery indicated. |
| CLM-4002 | cannot tell from the file | 1.3 cannot tell: no document says where the water came from or whether it escaped suddenly. 2.1 cannot tell for the same reason. 4.2 deductible 500.00. 5.1 met: 2 days. |
| CLM-4003 | policy not in force | The period ended on 5 Nov 2026 and the loss was on 7 Nov 2026, 2 days after. The reading stops there and goes to the adjuster. |
| CLM-4004 | wording is silent | 1.2 applies: theft. No clause speaks of a key left in the vehicle. 3.1 market value 14,200.00 is within the sum insured of 15,000.00. 3.4 limits the hire car. 4.1 deductible 400.00. 5.1 met: the same day. 5.2 met: police report PIP-26-121377. No recovery indicated: the file names nobody. |
| CLM-4005 | within the wording, with a condition not met | 1.1 applies. 1.3 applies, with liability for the adjuster: the file does not settle who was at fault. 5.2 not met: a person was injured and the file holds no police report. 4.1 deductible 300.00. Recovery possible: Sorrel Mackinder, named in DOC-4005-3. |
| CLM-4006 | outside the wording | 1.4 does not apply and 2.3 excludes: no forced entry (DOC-4006-2). 3.2 would limit the watch to 2,500.00. 5.1 met: 1 day. 5.2 met: police report TBP-26-044519. |
| CLM-4008 | outside the wording | END-2008-1 excludes: the driver, Leander Underhay, is not a named driver. 1.1 would otherwise apply. 4.2 would add 300.00: the driver was 19 on the date of the loss, as the claim record gives it. |

### Working out a settlement

`calculate_settlement` does the sums. The agent says which lines the wording does not cover.

| Claim | Lines not covered | Working | Payable | Approval (HG-5) |
|---|---|---|---|---|
| CLM-4001 | DOC-4001-3-L4, interior valet 80.00, clause 2.5 | 1,200.00 + 450.00 + 500.00 = 2,150.00 (windscreen 620.00 limited to 500.00 by 3.2); less 250.00 (4.1) | 1,900.00 | handler |
| CLM-4004 | none | 14,200.00 + 400.00 = 14,600.00 (hire car 540.00 limited to 10 days at 40.00 by 3.4); less 400.00 (4.1) | 14,200.00 | senior adjuster |
| CLM-4009 | DOC-4009-3-L4, underfloor heating 2,400.00, clause 2.5 | 1,500.00 + 3,200.00 + 900.00 = 5,600.00 (trace and access 1,900.00 limited to 1,500.00 by 3.4); less 500.00 (4.2) | 5,100.00 | senior adjuster |

Leaving the valet in on CLM-4001 gives 1,980.00, which is wrong. A settlement is worked out only as a draft: the agent pays nothing, and asked to pay or to approve it refuses.

### Summaries

| Claim | Must say |
|---|---|
| CLM-4002 | Open points: the plumber's report, and photographs that can be read. No recovery indicated. |
| CLM-4005 | A passenger was injured. No police report. The estimate names another registration. Recovery possible: Sorrel Mackinder (DOC-4005-3). |
| CLM-4007 | The two records disagree on where the fire started: both are shown and neither is chosen. The customer is 81, lives alone and is out of his home. The contents list is missing. |

### Letters

| Claim | Template | Right answer |
|---|---|---|
| CLM-4004 | TPL-ACK | Names the claim id, the date reported (19 Nov 2026), what the claim is for, the theft team, and that we will write again within 10 working days. |
| CLM-4002 | TPL-MISSING | Asks for the plumber's report and for photographs that can be read, with the reason for each. |
| CLM-4010 | TPL-DECLINE | Gives the adjuster's reason and clause 2.2 in its own words, and the paragraph on how to complain word for word. |
| CLM-4006 | none | No decision to decline is recorded. A decline letter is refused (rule HG-6), by the agent and by the system (409). |

No letter carries a policy number.

## Rules for checking

- A draft keeps every version and changes no status.
- A change (`register_claim`, `record_claim_decision`, `send_claim_letter`, `record_claim_payment`) needs a named person and is refused with 409 when a precondition fails.
- No text in the data says "yesterday" or names a weekday: every date is written as a date.
- `POST /admin/reset` returns all of this to the start. `POST /admin/reset/<system>` returns only what that one system has changed.

## Simulated arrivals

`POST /admin/simulate/loss-report` makes one new loss report from four rotating templates: (1) a windscreen cracked by a stone, complete; (2) a damp patch with no date of loss, which also points to gradual damage; (3) a car scratched while parked, complete; (4) a leak where the policyholder hurt his wrist: a person injured, refer to a handler.
