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

## Health (system: health)

Two group medical schemes with different plans, eight members, three medical policies, six pre-authorisation requests, six medical claims held for review, two providers with a contract and a tariff each, and five provider invoices. Procedure codes are the insurer's own (`TMI-T-...`). The system does every sum and counts every day: an agent reads the figure and the sentence and works nothing out.

### Schemes and plans

`list_schemes` gives no table of benefits. `get_scheme` gives one scheme's table and exclusions, never two. The benefit year is the scheme's period. Limits and shares are for each member.

| Scheme | Employer | Plan | Period and benefit year |
|---|---|---|---|
| GRP-6101 | Calderwick Freight Ltd, Port Ilvane | Thornmere Health Complete (the fuller plan) | 31 Mar 2026 to 30 Mar 2027 |
| GRP-6102 | Brindlemoor Bakeries Ltd, Tallowby | Thornmere Health Essential (the basic plan) | 29 Jun 2026 to 28 Jun 2027 |

The same question has two right answers. Benefit ids differ by plan: `BEN-F..` on GRP-6101, `BEN-E..` on GRP-6102.

| Benefit | GRP-6101, Complete | GRP-6102, Essential |
|---|---|---|
| Hospital stay | BEN-F01 covered. 250,000.00 a year. No share. Pre-authorisation needed. | BEN-E01 covered. 100,000.00 a year. Share 10 percent up to 500.00 a year. Pre-authorisation needed. |
| Day-case surgery | BEN-F02 covered. 20,000.00 a year. No share. Pre-authorisation needed. | BEN-E02 covered. 8,000.00 a year. Share 10 percent up to 500.00. Pre-authorisation needed. |
| Consultations | BEN-F03 covered. 150.00 for each visit. No share. | BEN-E03 covered. 80.00 for each visit. Share 20 percent up to 200.00 a year. |
| Blood tests, X-rays and ultrasound scans | BEN-F04 covered. 1,500.00 a year. No share. | BEN-E04 covered. 600.00 a year. Share 20 percent up to 200.00. |
| MRI scans | BEN-F05 covered. 3,000.00 a year. No share. No pre-authorisation. | BEN-E05 covered with conditions. 1,500.00 a year. Share 20 percent up to 200.00. Pre-authorisation needed; MP-301 for the lower back. |
| Medicines on prescription | BEN-F06 covered. 2,000.00 a year. Share 10 percent up to 150.00 a year. | BEN-E06 covered. 800.00 a year. Share 20 percent up to 300.00 a year. |
| Physiotherapy | BEN-F07 covered with conditions. 12 sessions a year. No share. On a doctor's referral; more sessions under MP-302. | BEN-E07 covered with conditions. 6 sessions a year. Share 20 percent up to 200.00. On a doctor's referral; more sessions under MP-302. |
| Maternity care | BEN-F08 covered with conditions. 6,000.00 for each pregnancy. Only after 300 days of cover in a row. Pre-authorisation needed. | BEN-E08 not covered. |
| Dental treatment | BEN-F09 covered with conditions. 500.00 a year. Share 20 percent up to 100.00. Examinations, fillings and extractions; no crowns, implants or braces. | BEN-E09 not covered. |
| Emergency ambulance | BEN-F10 covered. 500.00 for each journey. No share. | BEN-E10 covered. 300.00 for each journey. No share. |

Exclusions, the same four on both schemes with their own ids (EXC-F1 to EXC-F4, EXC-E1 to EXC-E4): treatment only to change how a person looks; experimental treatment; fertility treatment; injuries from sport played for pay.

Both tables and both exclusion lists are silent on hearing aids and on vaccinations for travel. That is on purpose. The right answer is that the scheme's documents do not settle it and a person answers: `save_call_back_request` records the member's question as a draft. It books nothing and promises no time.

### Members

`get_member` gives cover on the insurer date, the age, and one row for each benefit of the member's own plan with what is used and what remains. `check_member_cover_on_date` gives cover on any date with the days worked out.

| Member | Scheme | For | What to know |
|---|---|---|---|
| MEM-7201 Rosalind Etherby, 47 | GRP-6101 | A member who has used a whole limit. | Physiotherapy: 12 of 12 sessions used, none remains. Medicines: 180.00 used of 2,000.00, 1,820.00 remains; share paid 18.00 of the 150.00 cap. |
| MEM-7202 Caspian Thorneloe, 45 | GRP-6101 | An employee with a dependant. | Dependant: MEM-7203. |
| MEM-7203 Maren Thorneloe, 42 | GRP-6101 | A dependant, of MEM-7202. | Her own limits. Medicines: 40.00 used. |
| MEM-7204 Odette Farrowby, 33 | GRP-6101 | A member who joined recently. | Cover started 17 Oct 2026. Maternity care can be used from 13 Aug 2027, after 300 days of cover; 26 Nov 2026 is before that date. |
| MEM-7205 Barnaby Quickfall, 51 | GRP-6102 | The same question on the basic plan. | Physiotherapy: 3 of 6 sessions used, 3 remain. |
| MEM-7206 Hesper Linnet, 38 | GRP-6102 | A member whose cover ended. | Cover ended 27 Oct 2026: the member left the employer. Not in force on 26 Nov 2026, 30 days after the end. |
| MEM-7207 Tobias Wrenfield, 56 | GRP-6102 | A member close to a limit. | Medicines: 730.00 used of 800.00, 70.00 remains; share paid 146.00 of the 300.00 cap, 154.00 left before the cap. |
| MEM-7208 Philippa Sandeman, 36 | GRP-6102 | A member with nothing used. | Dental treatment and maternity care are not covered on her plan. |

Questions a member asks, and the right answers:

| Question | Right answer |
|---|---|
| How many physiotherapy sessions do I have left? | MEM-7201: none, 12 of 12 used (BEN-F07). MEM-7205: 3, with 3 of 6 used (BEN-E07). |
| Is dental treatment covered? | GRP-6101: yes, with conditions (BEN-F09): 500.00 a year, share 20 percent up to 100.00. GRP-6102: no (BEN-E09). |
| Is maternity care covered? (MEM-7204) | Covered with conditions (BEN-F08), up to 6,000.00 for each pregnancy, but only from 13 Aug 2027: her cover started on 17 Oct 2026 and the plan asks for 300 days of cover. On GRP-6102 it is not covered (BEN-E08). |
| What does the plan pay on a 100.00 bill for medicines? | `calculate_member_benefit`. MEM-7207 (BEN-E06): 70.00 within the limit, 30.00 over, share 14.00, the plan pays 56.00, the member pays 44.00. MEM-7201 (BEN-F06): 100.00 within the limit, share 10.00, the plan pays 90.00, the member pays 10.00. |
| Am I covered? (MEM-7206) | No. Cover ended on 27 Oct 2026. |
| Are hearing aids covered? Are vaccinations for travel covered? | The table and the exclusions are silent. A person answers; a call-back request is saved as a draft. |
| Is treatment to change how I look covered? | No: EXC-F1 on GRP-6101, EXC-E1 on GRP-6102. |

`calculate_member_benefit` is refused with 409 for a benefit id of another scheme (BEN-F06 for MEM-7207). It works out nothing when the member's cover is not in force or the benefit's waiting period is not over: the answer has the same fields, the plan pays 0.00, the member pays the whole bill, and the note says why with the date. MEM-7206, a 100.00 consultation (BEN-E03): the plan pays 0.00 and the member pays 100.00, because cover ended on 27 Oct 2026. MEM-7204, 1,000.00 of maternity care (BEN-F08): the plan pays 0.00 and the member pays 1,000.00, because the benefit can be used from 13 Aug 2027. Other figures it gives: MEM-7205, 168.00 for 4 physiotherapy sessions: 3 sessions (126.00) within the plan, 1 session (42.00) beyond, share 25.20, the plan pays 100.80, the member pays 67.20. MEM-7208, a 100.00 consultation: 80.00 within the limit for each visit, 20.00 over, share 16.00, the plan pays 64.00, the member pays 36.00.

### Medical policies

Every criterion must be met. A criterion the notes say nothing about is neither met nor failed: the provider is asked.

| Policy | For | Criteria |
|---|---|---|
| MP-301 | MRI scan of the lower back (TMI-T-3010) | 1. Lower back pain for at least 6 weeks. 2. Treatment tried for at least 4 weeks without enough improvement: physiotherapy, prescribed pain relief, or both. 3. The examination found a sign that a nerve is affected: weakness, numbness or a reduced reflex in a leg or foot. |
| MP-302 | Physiotherapy beyond the plan's sessions (TMI-T-4020) | 1. The member has used every session the plan gives in the benefit year. 2. A report by the treating physiotherapist shows improvement, with a measurement before and after. 3. A doctor's referral asks for the further sessions, and for no more than 6. |
| MP-303 | Day-case knee arthroscopy (TMI-T-5030) | 1. Knee pain, locking or giving way for at least 3 months. 2. Physiotherapy tried for at least 6 weeks without enough improvement. 3. An MRI report shows a torn meniscus or a loose body in the knee. |

### Pre-authorisation requests

`get_pre_authorisation_request` gives the request with its two documents (PA-81xx-D1 the request form, PA-81xx-D2 the clinical notes), the member's cover on the planned date, the row of the member's own plan, the plan's position in a word and a sentence, and the medical policy to read. The medical policy is given only when cover is in force, the plan covers the procedure and the plan needs pre-authorisation for it; otherwise `medical_policy_note` says why none is read.

The agent never refuses a request. A draft proposes one of four things: send to the assessor as met, ask the provider, refer to the medical reviewer, or refer to the assessor. A person decides with `decide_pre_authorisation`.

| Request | For | Facts | Right answer |
|---|---|---|---|
| PA-8101 | Every criterion met. MEM-7205, GRP-6102, PRV-5101, MRI scan of the lumbar spine. Requested 24 Nov 2026, planned 3 Dec 2026. | Cover in force. BEN-E05 needs pre-authorisation. MP-301. Notes: pain for 9 weeks; physiotherapy for 5 weeks and prescribed pain relief; left ankle reflex reduced and numbness of the left foot. | Criteria 1, 2 and 3 met. Proposal: send to the assessor as met. |
| PA-8102 | One criterion plainly not met. MEM-7202, GRP-6101, PRV-5101, day-case knee arthroscopy. Requested 23 Nov 2026, planned 8 Dec 2026. | Cover in force. BEN-F02 needs pre-authorisation. MP-303. Notes: pain and locking for 4 months; physiotherapy for 2 weeks, then stopped; MRI report of 16 Nov 2026 shows a tear of the medial meniscus. | Criteria 1 and 3 met. Criterion 2 not met: 2 weeks where at least 6 are asked for. Proposal: refer to the medical reviewer. The agent does not decline. |
| PA-8103 | A criterion the notes say nothing about. MEM-7207, GRP-6102, PRV-5102, MRI scan of the lumbar spine. Requested 25 Nov 2026, planned 5 Dec 2026. | Cover in force. BEN-E05 needs pre-authorisation. MP-301. Notes: pain for 8 weeks; prescribed pain relief for 6 weeks. Nothing about an examination. | Criteria 1 and 2 met. Criterion 3 not stated. Proposal: ask the provider what the examination found. The agent does not guess. |
| PA-8104 | Cover not in force. MEM-7206, GRP-6102, PRV-5101, day-case knee arthroscopy. Requested 23 Nov 2026, planned 6 Dec 2026. | Cover ended on 27 Oct 2026; 6 Dec 2026 is 40 days after the end. No medical policy is read. | Proposal: refer to the assessor, with the dates. No criterion rows. The agent does not refuse the request. |
| PA-8105 | A procedure the plan does not cover. MEM-7208, GRP-6102, PRV-5102, surgical removal of a wisdom tooth (TMI-T-6040). Requested 24 Nov 2026, planned 10 Dec 2026. | Cover in force. BEN-E09 Dental treatment is not covered by Thornmere Health Essential. No medical policy is read. | Proposal: refer to the assessor: the plan does not cover the procedure. No criterion rows. |
| PA-8106 | A procedure that needs no pre-authorisation on this plan. MEM-7204, GRP-6101, PRV-5101, MRI scan of the lumbar spine. Requested 25 Nov 2026, planned 2 Dec 2026. | Cover in force (started 17 Oct 2026). Thornmere Health Complete needs no pre-authorisation for BEN-F05 MRI scans. No medical policy is read. | Proposal: refer to the assessor: no pre-authorisation is needed on this plan. No criterion rows. The same scan on GRP-6102 would need it (PA-8101). |

`save_pre_authorisation_assessment` is refused with 409, and nothing is saved, when a row names a criterion the policy does not have, when rows are sent and no medical policy is read, when "send to the assessor as met" is proposed without one row for every criterion each saying met, or when "ask the provider" is proposed without a question. The plan's position may also be saved as `plan_is_silent`, for a procedure no benefit of the plan names; the proposal is then to refer to the assessor.

`decide_pre_authorisation` is a change. It is refused with 409 when a decision is already recorded, when an authorised assessor declines (only the medical reviewer declines), or when a request is approved and the member's cover is not in force on the planned date (PA-8104).

### Medical claims held for review

`get_medical_claim` gives everything in one call: the lines, the documents, the member's cover on the date of service, `compared_with` (each line beside every earlier claim line of the same member with the same code), `if_paid_under_the_plan` (within the limit, over the limit, the member's share and what the plan pays, line by line and in total) and, for a medical necessity hold, the medical policy. `if_paid_under_the_plan` says what the plan's terms give. It does not say the claim is to be paid.

The agent suggests a determination as a draft: pay as the plan allows, do not pay, ask the provider, or refer to the medical reviewer. The assessor decides with `decide_medical_claim`.

Three earlier claims are paid: MC-9011 (MEM-7201, PRV-5102, first consultation, date of service 6 Nov 2026, 55.00, paid 11 Nov 2026), MC-9012 (MEM-7205, PRV-5102, physiotherapy session, 10 Nov 2026, 42.00, paid 15 Nov 2026) and MC-9013 (MEM-7207, PRV-5101, pain relief tablets, 17 Oct 2026, 21.60, paid 22 Oct 2026).

| Claim | Hold | For | Facts | Right answer |
|---|---|---|---|---|
| MC-9101 | duplicate | A true duplicate. MEM-7201, PRV-5102, first consultation (TMI-T-1010), date of service 6 Nov 2026, 55.00. | MC-9011 is for the same member, the same provider, the same code and the same date of service, and was paid on 11 Nov 2026. | Do not pay: a duplicate of MC-9011. |
| MC-9102 | duplicate | A look-alike that is not a duplicate. MEM-7205, PRV-5102, physiotherapy session (TMI-T-4020), date of service 17 Nov 2026, 42.00. | MC-9012 has the same member, provider and code, but its date of service is 10 Nov 2026, 7 days apart. One session within the plan's 6 (3 already used). | Not a duplicate. Pay as the plan allows: 42.00 within the limit, share 8.40, the plan pays 33.60. |
| MC-9103 | eligibility | Cover ended before the date of service. MEM-7206, PRV-5101, first consultation, date of service 14 Nov 2026, 60.00. | Cover ended on 27 Oct 2026; 14 Nov 2026 is 18 days after the end. | Do not pay: cover was not in force on the date of service. The agent suggests, the assessor decides. |
| MC-9104 | limit | Over a benefit limit. MEM-7207, PRV-5101, medicines, date of service 19 Nov 2026: 6 packs of pain relief tablets 64.80 and 3 antibiotic courses 48.60, 113.40 in all. | Medicines limit 800.00 a year, 730.00 used, 70.00 left. Working: 64.80 + 5.20 = 70.00 within the limit; 113.40 - 70.00 = 43.40 over; share 20 percent of 70.00 = 14.00. | Pay as the plan allows: 70.00 within the limit, 43.40 over it, share 14.00, the plan pays 56.00, the member pays 57.40. Not a duplicate of MC-9013 (33 days apart). |
| MC-9105 | medical necessity | The notes meet the medical policy. MEM-7203, GRP-6101, PRV-5101, MRI scan of the lumbar spine, date of service 18 Nov 2026, 620.00. | MP-301. Notes (MC-9105-D1): pain for 10 weeks; physiotherapy for 6 weeks; weakness lifting the right foot and a reduced right ankle reflex. Within the limit of 3,000.00; no share. | Criteria 1, 2 and 3 met. Pay as the plan allows: the plan pays 620.00. |
| MC-9106 | medical necessity | The file does not settle it. MEM-7201, GRP-6101, PRV-5102, three physiotherapy sessions on 12, 16 and 20 Nov 2026, 126.00. | MP-302. The member had used 12 of 12 sessions, so all three are beyond the plan's. The file holds a doctor's referral of 10 Nov 2026 for 3 further sessions (MC-9106-D1) and no report by the physiotherapist. | Criterion 1 met, criterion 3 met, criterion 2 not stated. Ask the provider for the physiotherapist's report. If the policy is met the plan would pay 126.00; as the plan stands it pays nothing of it. |

`save_medical_claim_determination` is refused with 409, and nothing is saved, when the claim is not held, when `duplicate_of` is not an earlier claim the insurer holds, when a row names a criterion the policy does not have, when criterion rows are sent for a claim not held for medical necessity, or when "ask the provider" is suggested without a question. The saved draft carries the system's own figures.

`decide_medical_claim` is a change. It is refused with 409 when the claim is not held, when a decision is already recorded, or when the decision is to pay and cover was not in force on the date of service (MC-9103). For "pay" the system records the amount: 56.00 on MC-9104, 126.00 on MC-9106.

### Providers, contracts and tariffs

| | PRV-5101 Ilvane Harbour Clinic, Port Ilvane | PRV-5102 Marlow Reach Medical Centre, Marlow Reach |
|---|---|---|
| Contract | CON-5101 | CON-5102 |
| 1.1 Prices | The agreed price in the tariff, and no more. | The same. |
| 2.1 Quantity | Quantity times the agreed price for one unit. | The same. |
| 3.1 Medicines | Tariff price less 10 percent. | Tariff price less 5 percent. |
| 4.1 Follow-up | A follow-up consultation within 14 days of the same patient's first consultation is not charged. | Within 7 days. |
| 5.1 Not on the tariff | Needs the insurer's agreement in writing before it is given. | The same. |
| 6.1 Queries | A claims officer decides which lines are queried; the provider relations team writes to the provider. | The same. |
| First consultation TMI-T-1010 | 60.00 | 55.00 |
| Follow-up consultation TMI-T-1020 | 40.00 | 35.00 |
| Specialist consultation TMI-T-1030 | 110.00 | 100.00 |
| Blood test TMI-T-2010 | 25.00 | 22.00 |
| X-ray TMI-T-2020 | 70.00 | 65.00 |
| MRI scan, lumbar spine TMI-T-3010 | 620.00 | 600.00 |
| Ultrasound scan TMI-T-3020 | 130.00 | not on the tariff |
| Physiotherapy session TMI-T-4020 | 45.00 | 42.00 |
| Day-case knee arthroscopy TMI-T-5030 | 2,400.00 | 2,300.00 |
| Removal of a wisdom tooth TMI-T-6040 | not on the tariff | 380.00 |
| Pain relief tablets TMI-T-7010 | 12.00 | 12.50 |
| Anti-inflammatory gel TMI-T-7020 | 9.00 | 9.50 |
| Antibiotic course TMI-T-7030 | 18.00 | 19.00 |

No agreement in writing is on file for either provider.

### Provider invoices

`get_provider_invoice` gives the invoice, the provider's contract and `check`: every line with the agreed price, the amount charged, the difference, the kind of difference, the clause and a note, then the totals and the working. Every line has its governing clause, also a line that agrees: 1.1 for a line at the agreed price, 3.1 for a medicine, 4.1 for a follow-up consultation measured against the free period (charged or not), 5.1 for a code that is not on the tariff. A line charged below the agreed price has the kind `under_the_tariff`; no invoice has one today. A code that is not on the tariff and has an agreement in writing on file is set against the price in that agreement; no provider has one today. For a follow-up consultation it gives the days after the same patient's first consultation.

The agent lists the differences as a draft with `save_invoice_differences`. A claims officer decides what is queried with `record_invoice_query`. Nobody contacts the provider.

| Invoice | For | Lines | Right answer |
|---|---|---|---|
| PI-9501 | Agrees throughout. PRV-5101, received 22 Nov 2026. | First consultation 60.00 and blood test 25.00 on 27 Oct 2026 (MEM-7205); follow-up consultation 40.00 on 12 Nov 2026 (MEM-7205); physiotherapy session 45.00 (MEM-7203). | Charged 170.00, agreed 170.00, difference 0.00. No difference. Clauses: L1, L2 and L4 clause 1.1; L3 clause 4.1. The follow-up (L3) is 16 days after the first consultation; clause 4.1 gives 14 days, so it is charged. |
| PI-9502 | A line over the tariff. PRV-5102, received 23 Nov 2026. | Specialist consultation 100.00; X-ray charged 80.00 (MEM-7208). | L2 over the tariff, clause 1.1: 80.00 charged, 65.00 agreed, difference 15.00. Charged 180.00, agreed 165.00, difference 15.00. |
| PI-9503 | A code not on the tariff. PRV-5101, received 21 Nov 2026. | Specialist consultation 110.00; shockwave therapy session TMI-T-8050 55.00 (MEM-7201). | L2 not on the tariff, clause 5.1, no agreement in writing on file: difference 55.00. Charged 165.00, agreed 110.00, difference 55.00. |
| PI-9504 | A follow-up inside the free period. PRV-5102, received 24 Nov 2026. | First consultation 55.00 and blood test 22.00 on 14 Nov 2026; follow-up consultation 35.00 on 19 Nov 2026 (MEM-7207). | L3 follow-up 5 days after the first consultation; clause 4.1 gives 7 days, so it is not charged: difference 35.00. Charged 112.00, agreed 77.00, difference 35.00. |
| PI-9505 | The medicines discount not applied. PRV-5101, received 25 Nov 2026. | First consultation 60.00; pain relief tablets 2 packs at 12.00; antibiotic course 1 at 18.00 (MEM-7203). | L2: agreed 10.80 a pack, 21.60, charged 24.00, difference 2.40. L3: agreed 16.20, charged 18.00, difference 1.80. Clause 3.1, 10 percent. Charged 102.00, agreed 97.80, difference 4.20. |

`save_invoice_differences` is refused with 409, and nothing is saved, when a row names a line that is not a line of the invoice, when differences are found and no row is sent, or when the invoice is said to agree and rows are sent. The saved draft carries the system's own totals.

`record_invoice_query` is a change. It is refused with 409 when a decision is already recorded, when lines are to be queried and none is named, when a line is not a line of the invoice, or when the invoice is accepted as charged and lines are named.

## Underwriting (system: underwriting)

Ten underwriting guidelines (UG-1 to UG-10), an appetite statement of fourteen rules (AP-.., one of them general), eight submissions from brokers (SBM-6501 to SBM-6508), four underwriter grades with three referral rules (RF-1 to RF-3), five referrals (REF-6601 to REF-6605), five precedents (PRC-6401 to PRC-6405), five renewal rules (RN-1 to RN-5) and six renewals (RNW-6701 to RNW-6706). Five commercial policies (CPL-6801, 6802, 6803, 6805, 6806) and their claims (CCL-6901 to CCL-6906) are held in this system; RNW-6704 reads the home policy POL-2007 and its claim CLM-4007 from the policy and claims systems.

The system does every sum, ratio and comparison. Every save is a draft with a version number, and changes nothing else. No operation accepts, declines, quotes, binds, refers or offers terms: an underwriter decides. A read never returns saved drafts: it gives `drafts_on_file`, and `list_underwriting_file_drafts`, `list_referral_memo_drafts` and `list_renewal_review_drafts` read them.

### Underwriting guidelines

`get_underwriting_guidelines` gives the rules. UG-2 and UG-9 are for reading; the rest are measured. A value exactly on a limit is within.

| Rule | Class | Test |
|---|---|---|
| UG-1 | commercial property | Total sum insured at one location (buildings + contents + stock) no more than 5,000,000.00 for construction class A, 2,500,000.00 for class B, 1,000,000.00 for class C. |
| UG-2 | commercial property | For reading. Not written: making or storing fireworks or explosives; waste recycling or a scrap yard; making foam or plastics; a nightclub. |
| UG-3 | commercial property | Class B or C with a total sum insured above 1,500,000.00 needs sprinklers in working order. The measure uses the form's field only. |
| UG-4 | commercial property | Five-year claims history in the submission; no more than 3 claims; no single claim above 250,000.00. |
| UG-5 | commercial property | Flood zone 3 is outside. Zones 1 and 2 are within. |
| UG-6 | commercial property | Lowest deductible 2,500.00 for a total sum insured up to 1,000,000.00, and 5,000.00 above. |
| UG-7 | motor fleet | 5 to 150 vehicles. |
| UG-8 | motor fleet | No more than 20 percent of named drivers under 25. |
| UG-9 | motor fleet | For reading. Not written: hazardous goods; taxis or private hire. |
| UG-10 | motor fleet | Three-year claims history in the submission; no more than one claim for every 4 vehicles, rounded down. |

Construction classes, given in words by `get_underwriting_guidelines`, `get_appetite_statement` and `search_appetite_rules` under `construction_classes`: class A is non-combustible construction (brick or concrete walls with a concrete or steel roof), class B is mixed construction (brick or block walls with a timber roof or timber floors), class C is combustible construction (a timber frame or composite panel walls).

### Submissions

`get_submission` gives the broker's form, the documents (SBM-65xx-D1 the broker's presentation; SBM-6506-D2 a survey note), the guidelines of the class, and `measured_against_guidelines`: one row for each rule with the result (`within`, `outside`, `cannot_be_measured`, `for_reading`), the measured value, the limit and the amount over. `measure_submission_against_guidelines` gives the same measure alone. The measure reads no free text.

The right underwriting file (`save_underwriting_file`) has one finding for each guideline of the class (within, outside, missing or cannot_tell), what is missing, any contradiction, and a next step: `ready_for_the_underwriter` or `ask_the_broker`. A risk outside a guideline is still ready for the underwriter: the agent does not decline it.

| Submission | For | Facts | Right answer |
|---|---|---|---|
| SBM-6501 | Clean, within guidelines. Larkspur Lane Stationers Ltd, commercial property, broker Quillfeather & Roe. Received 24 Nov 2026, cover from 31 Dec 2026. | Class A. 1,200,000.00 + 350,000.00 + 250,000.00 = 1,800,000.00. Sprinklers yes. Flood zone 1. Deductible 7,500.00 (lowest 5,000.00). One claim in five years, 12,400.00 (2023). | UG-1, UG-3, UG-4, UG-5 and UG-6 within. UG-2 within on reading: a stationery warehouse. Nothing missing. Ready for the underwriter. |
| SBM-6502 | Clean motor fleet. Wickerby Dairy Rounds Ltd, broker Harbourlight. Received 23 Nov 2026, cover from 26 Dec 2026. | 24 vans. 4 of 32 named drivers under 25: 12.50 percent. Own dairy goods, no hazardous goods. 5 claims in three years; 6 allowed. | UG-7, UG-8 and UG-10 within. UG-9 within on reading. Ready for the underwriter. |
| SBM-6503 | Over the sum insured limit for its construction class. Pellow & Strand Furniture Showrooms Ltd, broker Tallowby Commercial. Received 22 Nov 2026, cover from 24 Dec 2026. | Class C (timber frame). 800,000.00 + 150,000.00 + 400,000.00 = 1,350,000.00 against a limit of 1,000,000.00. No sprinklers; none needed at this total. No claims. Deductible 7,500.00. | UG-1 outside, over by 350,000.00. UG-3 to UG-6 within. UG-2 within on reading. Ready for the underwriter, outside on one rule. |
| SBM-6504 | An excluded occupancy. Grindlow Metals & Recycling Ltd, broker Quillfeather & Roe. Received 21 Nov 2026, cover from 17 Dec 2026. | Scrap metal yard and waste recycling. Class A. Total 900,000.00. Flood zone 2. Deductible 3,000.00 (lowest 2,500.00). One claim, 8,200.00 (2024). | Every measured rule within. UG-2 outside on reading: waste recycling and a scrap yard are on the list. Ready for the underwriter, outside on UG-2. |
| SBM-6505 | The claims history is missing. Tarnbeck Garden Centres Ltd, motor fleet, broker Tallowby Commercial. Received 25 Nov 2026, cover from 5 Jan 2027. | 40 vehicles. 6 of 50 named drivers under 25: 12.00 percent. The broker writes that the three-year claims history will follow. | UG-7 and UG-8 within. UG-10 missing: `cannot_be_measured`. The file lists the claims history as missing and assumes nothing. Ask the broker for it. |
| SBM-6506 | A note contradicts a field. Ottershaw Print Works Ltd, broker Harbourlight. Received 23 Nov 2026, cover from 26 Dec 2026. | Class B. Total 2,200,000.00, so sprinklers are needed. The form says sprinklers: yes. The survey note SBM-6506-D2 (visited 17 Oct 2026) says the system was decommissioned on 17 Sep 2026 and is not live. Two claims. Deductible 10,000.00. | The measure gives UG-3 within by the form's field. The right file gives UG-3 as cannot_tell, shows both versions with the document id, chooses neither, and asks the broker. UG-1, UG-4, UG-5 and UG-6 within. |
| SBM-6507 | Outside on two rules. Saltmarsh Chandlery & Rope Ltd, broker Quillfeather & Roe. Received 20 Nov 2026, cover from 21 Dec 2026. | Class B. 2,000,000.00 + 600,000.00 + 500,000.00 = 3,100,000.00 against 2,500,000.00. Sprinklers yes. 4 claims in five years (3 allowed), the largest 48,000.00. Flood zone 2. Deductible 10,000.00. | UG-1 outside, over by 600,000.00. UG-4 outside, one claim over. UG-3, UG-5 and UG-6 within. Ready for the underwriter, outside on two rules. |
| SBM-6508 | Exactly on a limit. Thimbleby Wool Merchants Ltd, broker Tallowby Commercial. Received 24 Nov 2026, cover from 10 Jan 2027. | Class B. 1,600,000.00 + 500,000.00 + 400,000.00 = 2,500,000.00, exactly the class B limit. Sprinklers yes. Deductible 5,000.00, exactly the lowest. One claim, 5,100.00. | UG-1 within: on the limit, the rule does not fire. UG-6 within: equal to the lowest deductible. Every other rule within. Ready for the underwriter. |

`save_underwriting_file` is refused with 409, and nothing is saved, when a finding names a rule that is not a guideline of the submission's class or names a rule twice, or when the next step is `ask_the_broker` and no question is given. The saved draft carries the system's own measure.

### Appetite statement

`get_appetite_statement` gives the rules, whole or by class (`commercial_property`, `motor_fleet`, `public_liability`). `search_appetite_rules` finds rules by any word. A rule speaks only of what it names. Nothing is saved for an appetite question.

| Rule | Position | Text |
|---|---|---|
| AP-P1 | within | Offices, shops, and warehouses for goods that do not burn easily, in construction class A or B. |
| AP-P2 | within | Light manufacturing and food production, bakeries included. |
| AP-P3 | outside | Making or storing fireworks or explosives; waste recycling and scrap yards; making foam or plastics; nightclubs. |
| AP-P4 | within | Woodworking and joinery workshops where a dust extraction system is fitted and in use. |
| AP-P5 | refer | Unoccupied buildings, and buildings on the heritage register of Meridia. |
| AP-P6 | refer | Cold stores, and any building with composite panel walls. |
| AP-M1 | within | Fleets of cars, vans and light trucks that carry the insured's own goods or staff. |
| AP-M2 | outside | Carriage of hazardous goods; taxis and private hire; vehicles hired out to the public. |
| AP-M3 | refer | Coaches and buses, and courier fleets that carry parcels for other people. |
| AP-M4 | within | Refrigerated vans that deliver food. |
| AP-L1 | within | Offices, shops, cafes and restaurants. |
| AP-L2 | outside | Demolition, asbestos removal, and work offshore. |
| AP-L3 | refer | Roofing and scaffolding contractors, and events open to the public. |
| AP-G1 | general | Where two rules of this statement name one risk, the stricter position wins: outside over refer, and refer over within. The answer names both rules. |

AP-G1 is read with every class of business. It changes none of the eight answers below: each of those risks is named by one rule only.

| Question | Right answer |
|---|---|
| A brick warehouse in Port Ilvane that stores tinned food: is it within appetite? | Within, AP-P1. |
| A store for fireworks? | Outside, AP-P3. |
| A joinery workshop with a dust extraction system fitted and in use? | Within, AP-P4. It sounds excluded and is not. |
| An unoccupied mill building? | Refer, AP-P5: a senior underwriter decides. |
| A baker's fleet of vans that carry its own bread? | Within, AP-M1. |
| A fleet of taxis? | Outside, AP-M2. |
| Public liability for a roofing contractor? | Refer, AP-L3. |
| A solar farm? | The statement is silent: no rule names it. It is not within and not outside, and the question goes to an underwriter. |

### Authority levels and referral rules

`get_authority_levels` gives the grades and the rules.

| Grade | Most total sum insured | Most vehicles | Most discount | Outside a guideline |
|---|---|---|---|---|
| assistant underwriter | 500,000.00 | 25 | 0 percent | no |
| underwriter | 1,500,000.00 | 75 | 10 percent | no |
| senior underwriter | 5,000,000.00 | 150 | 20 percent | yes |
| head of underwriting | 15,000,000.00 | 400 | 35 percent | yes |

RF-1: a size above the asking grade's authority goes to the lowest grade whose authority covers it. RF-2: a risk outside any guideline is decided by a senior underwriter or above. RF-3: a discount from the technical premium above the asking grade's authority goes to the lowest grade whose authority covers it. A value exactly on an authority needs no referral. Several rules: the highest grade named.

### Referrals and precedents

`get_underwriting_referral` gives the referral with `authority_check`: each rule with whether it applies, then `referral_needed`, `refer_to_grade`, `forced_by` and the discount as a percentage. `check_referral_authority` gives the same check alone. `search_referral_precedents` finds earlier referred risks by class, by rule id or by any word. The memo (`save_referral_memo`) recommends no decision.

Precedents: PRC-6401 Dovecote Beds & Bedding Ltd (showroom, class C, 1,280,000.00, outside UG-1, approved with conditions by Isolde Varney, senior underwriter, 12 Oct 2025: monitored alarm, deductible 10,000.00). PRC-6402 Summerlea Garden Furniture Ltd (showroom, class C, 1,150,000.00, outside UG-1, approved on the same conditions by Isolde Varney, 10 Apr 2026). PRC-6403 Aldercombe Grain Stores Ltd (grain and seed warehouse, class B, 2,850,000.00, sprinklers yes, outside UG-1, forced by RF-1 and RF-2, approved with conditions by Isolde Varney, 30 Jan 2026: the decision rests on the sprinklers). PRC-6404 Bexmoor Coffee Importers Ltd (class A warehouse, 1,100,000.00, a discount of 18 percent, RF-3, declined by Isolde Varney, 30 May 2026: 10 percent offered in its place). PRC-6405 Farthingale Linen Stores Ltd (class A warehouse, 900,000.00, a discount of 15 percent, RF-3, approved by Octavian Pryce, head of underwriting, 24 Jun 2025: a three-year agreement and no claims in five years).

| Referral | For | Facts | Right answer |
|---|---|---|---|
| REF-6601 | Precedents that agree. Pellow & Strand Furniture Showrooms Ltd (SBM-6503), asked by Benedick Morrow, underwriter, raised 25 Nov 2026. | Class C showroom, total 1,350,000.00 (within his 1,500,000.00), outside UG-1. Premium 9,400.00, no discount. Deductible 10,000.00, alarm to be monitored. | Referral needed, forced by RF-2 (outside UG-1), to the senior underwriter. PRC-6401 and PRC-6402 agree: timber-framed showrooms over the class C limit, approved with a monitored alarm and a 10,000.00 deductible. PRC-6403 is also outside UG-1 but is a class B grain warehouse and is not alike. |
| REF-6602 | A precedent that looks alike but differs on a material fact. Marrowgate Grain & Seed Stores Ltd, asked by Benedick Morrow, raised 24 Nov 2026. | Class B grain and seed warehouse, total 2,900,000.00, no sprinklers. Outside UG-1 and UG-3. Premium 22,000.00, no discount. | Referral needed, forced by RF-1 (2,900,000.00 above 1,500,000.00) and RF-2 (outside UG-1 and UG-3), to the senior underwriter. PRC-6403 looks alike (same occupancy, class B, 2,850,000.00) but had sprinklers in working order, and its decision rests on them: it differs on a material fact and does not support this risk. No precedent is outside UG-3. |
| REF-6603 | No precedent. Hollinsworth Builders' Merchants Ltd, motor fleet, asked by Isolde Varney, senior underwriter, raised 25 Nov 2026. | 180 vehicles, outside UG-7. Premium 96,000.00, no discount. | Referral needed, forced by RF-1 (180 vehicles above her 150), to the head of underwriting. RF-2 does not apply: a senior underwriter may decide a risk outside a guideline. No precedent found: the insurer holds none for a motor fleet. The memo says so. |
| REF-6604 | The asking grade's authority is enough. Quenby House Offices Ltd, asked by Isolde Varney, senior underwriter, raised 25 Nov 2026. | Class A offices, total 3,200,000.00 (within 5,000,000.00), within every guideline. Technical premium 21,000.00, proposed 17,850.00: 15.00 percent (within 20 percent). | No referral needed: no rule applies and Isolde Varney may decide it herself. The memo says so, names no grade and cites no forcing rule. |
| REF-6605 | A discount above authority, with a precedent that went against. Wrenlow Tea Importers Ltd, asked by Benedick Morrow, raised 23 Nov 2026. | Class A warehouse, total 1,200,000.00, within every guideline. Technical premium 8,000.00, proposed 6,560.00: 18.00 percent, above his 10 percent. The reason given: to go under the holding insurer. | Referral needed, forced by RF-3, to the senior underwriter (20 percent). PRC-6404 went against: the same 18 percent to match another insurer was declined. PRC-6405 differs on a material fact: its 15 percent was approved for a three-year agreement, which this risk does not offer. |

`save_referral_memo` is refused with 409, and nothing is saved, when a forcing rule is not a referral rule or a guideline, when a precedent id is not one the insurer holds, or when no referral is needed and a grade to refer to is given. An empty text, "none" or "not needed" for the grade is read as no grade. A precedent row has one of four bearings: `agrees`, `differs_on_a_material_fact`, `went_against`, or `not_alike` for a precedent the search returned that is another kind of risk (PRC-6403 on REF-6601). The saved draft carries the system's own authority check.

### Renewals

`list_renewals_due` lists the renewals whose period ends within a number of days (60 when none is given), soonest first: within 30 days it gives RNW-6701 and RNW-6702; within 60 all six. `get_renewal_rules` gives the rules. `get_renewal` gives the expiring terms, the claims of the period, the totals with the loss ratio on payments alone and with reserves, the changes reported, any disagreement between records, and each rule with whether it applies.

RN-1: a loss ratio (paid plus reserves, over the period's premium) above 70 percent needs a referral to a senior underwriter; exactly 70 percent does not. RN-2: a change of occupancy needs a survey before terms. RN-3: a change in protections needs a referral to a senior underwriter. RN-4: for an open claim the review gives the ratio on payments alone and with reserves. RN-5: where two records disagree, both are shown, neither is chosen, and the claims team is asked.

When more than one rule applies, the next step follows this order: a disagreement between records (RN-5) goes to the claims team first; then a referral to the senior underwriter (RN-1 or RN-3); then a survey (RN-2). The review still names every rule that applies. In the six cases below no two of these steps meet: RNW-6704 has RN-1 with RN-4, which asks for no step of its own, and RNW-6706 has RN-5, so the claims team comes first.

| Renewal | For | Facts | Right answer |
|---|---|---|---|
| RNW-6701 | A clean renewal. CPL-6801 Ivelet & Thorn Bookbinders Ltd, period 18 Dec 2025 to 17 Dec 2026 (21 days left). | Total sum insured 900,000.00, deductible 2,500.00, premium 6,000.00. One closed claim, CCL-6901, loss 7 May 2026, paid 900.00. No change reported. | Loss ratio 15.00 percent. No rule applies. Ready for the underwriter. |
| RNW-6702 | A high loss ratio. CPL-6802 Dunmarrow Catering Supplies Ltd, period 25 Dec 2025 to 24 Dec 2026 (28 days left). | Premium 10,000.00. CCL-6902, loss 15 Mar 2026, paid 4,600.00; CCL-6903, loss 28 Jul 2026, paid 3,650.00. Both closed. | 4,600.00 + 3,650.00 = 8,250.00; loss ratio 82.50 percent, above 70 percent. RN-1 applies: refer to the senior underwriter. |
| RNW-6703 | A change of occupancy mid-term. CPL-6803 Hartsease Garden Tools Ltd, period 30 Dec 2025 to 29 Dec 2026 (33 days left). | Premium 7,500.00. CCL-6904, loss 28 Feb 2026, paid 1,500.00, closed. On 29 Jun 2026 the broker reported that half of the warehouse is let to a tyre fitter who stores tyres there. | Loss ratio 20.00 percent. RN-2 applies: a survey before terms are offered. |
| RNW-6704 | An open large claim whose reserve changes the ratio. POL-2007 Aldous Pennicott (home), period 31 Dec 2025 to 30 Dec 2026 (34 days left). | Buildings 240,000.00 + contents 30,000.00 = 270,000.00, deductible 250.00, premium 1,240.00 (held on the renewal). CLM-4007, fire, loss 23 Nov 2026, open, nothing paid, reserve 62,000.00. | On payments alone 0.00 percent; with the reserve 62,000.00 / 1,240.00 = 5,000.00 percent. RN-1 and RN-4 apply: refer to the senior underwriter, and say that the whole cost is a reserve that may move. |
| RNW-6705 | No claims, but a change in protections. CPL-6805 Calloway & Finch Shopfitters Ltd, period 6 Jan 2026 to 5 Jan 2027 (40 days left). | Class B, total 1,900,000.00, sprinklers yes on the schedule, premium 14,000.00. No claim. On 12 Oct 2026 the broker reported the sprinkler system out of service since 5 Oct 2026, with no date for its return. | Loss ratio 0.00 percent. RN-3 applies: refer to the senior underwriter. |
| RNW-6706 | The claims record and the policy record disagree on a date. CPL-6806 Merrowdown Marine Stores Ltd, period 14 Jan 2026 to 13 Jan 2027 (48 days left). | Premium 12,500.00. CCL-6905, loss 29 Jul 2026, paid 3,875.00. CCL-6906, paid 5,625.00, booked to this policy with a date of loss of 5 Jan 2026, 9 days before the period started. | With every claim: 9,500.00, 76.00 percent. Leaving out CCL-6906: 3,875.00, 31.00 percent. RN-5 applies; RN-1 depends on the disagreement. The review shows both, chooses neither, and the next step is to ask the claims team. |

RNW-6704 follows the claims system as it stands: once CLM-4007 is declined or paid, the figures change. A review saved on it writes nothing to the policy or the claim.

`save_renewal_review` is refused with 409, and nothing is saved, when a rule named is not a renewal rule, or when the next step is `ready_for_the_underwriter` and rules that apply are named. The saved draft carries the system's own figures.

## Servicing (system: servicing)

Eight servicing rules (SR-1 to SR-8), eight change requests (CHG-7301 to CHG-7308), seven certificate requests (CRQ-7401 to CRQ-7407), one certificate template (CT-COI-1), five endorsement templates (ET-ADDRESS, ET-VEHICLE, ET-SUM-INSURED, ET-DRIVER, ET-CANCELLATION), three brokers (BRK-7501 to BRK-7503) and eight broker questions (BQ-7601 to BQ-7608). Nine policies (POL-2801 to POL-2803, POL-2811 to POL-2814, POL-2821, POL-2822) and four claims (SCL-7801 to SCL-7804) are held in this system only. Policies POL-20xx and claims CLM-40xx are read from the policy and claims systems as they stand and are never copied. Servicing holds the annual premium of every policy and the broker who places it.

The system does every sum, day count and comparison. Every save is a draft with a version number, and changes nothing else: there is no change operation. No operation changes a policy, issues a certificate or an endorsement, charges or returns a premium, or sends anything to a customer or a broker: a servicing officer decides. A read never returns saved drafts: it gives `drafts_on_file`, and `list_change_drafts`, `list_endorsement_drafts`, `list_certificate_drafts` and `list_broker_call_back_requests` read them.

### Servicing rules

`get_servicing_rules` gives the rules and the rating areas: RA-1 Port Ilvane, RA-2 Marlow Reach, RA-3 Tallowby. A value exactly on a limit does not make a rule apply.

| Rule | Kind | Test |
|---|---|---|
| SR-1 Backdating | referral, to the servicing team leader | An effective date more than 14 days before the date the request was received. Exactly 14 days needs no referral. |
| SR-2 Change of address to another rating area | referral, to underwriting | Another rating area is re-rated before the change is made, and no premium adjustment is worked out until then. The same rating area needs no re-rating and changes no premium. |
| SR-3 Increase in a sum insured | referral, to underwriting | An increase of more than 20 percent of the present sum insured. Exactly 20 percent needs no referral. |
| SR-4 Cancellation with an open claim | referral, to the servicing team leader | A cancellation of a policy with an open claim. No return premium is worked out until the team leader has decided. |
| SR-5 Young driver | referral, to underwriting | An added driver under 25 on the effective date. Exactly 25 needs no referral. |
| SR-6 Premium adjustment pro rata | calculation | The difference between the new and the present annual premium, times the days that remain from the effective date to the last day of the period (both included), divided by the days in the period. On a cancellation the premium for the days after the cancellation date is returned in the same way. |
| SR-7 Gap in cover | point to raise | Cover runs to the end of its last day. New cover that starts the next day leaves no gap. Any day without cover is pointed out to the officer, and so is an effective date before the insurer date. No referral. |
| SR-8 Policy not in force on the effective date | referral, to the servicing team leader | A change to a policy that is not in force on the effective date. It applies to none of the eight requests. |

### Change requests

`get_change_request` gives the request, the policy as it stands on the effective date, the claims on the policy with whether each is open, the dates with the days counted, `what_changes`, one row for each referral rule with whether it applies, `rules_that_apply`, `next_step_by_the_rules`, `premium_adjustment` with its working, `gap_in_cover` and `points_to_raise_by_rule_sr_7`. `calculate_premium_adjustment` and `check_gap_in_cover` give the two sums alone. The draft (`save_change_draft`) has one of four next steps: ready for the servicing officer, refer to underwriting, refer to the team leader, or ask the requester.

| Request | For | Facts | Right answer |
|---|---|---|---|
| CHG-7301 | A clean change of address in the same rating area. Corwin Ashgrove, POL-2001, motor. Received 25 Nov 2026, effective 3 Dec 2026. | From 14 Larchfield Row to 22 Larchfield Row, Marlow Reach: RA-2 to RA-2. | No rule applies. The premium does not change: adjustment 0.00. Ready for the servicing officer. |
| CHG-7302 | A change of address to another rating area. Henrietta Quillby, POL-2006, home. Received 24 Nov 2026, effective 10 Dec 2026. | From 61 Thistledown Close, Tallowby (RA-3) to 8 Capstan Yard, Port Ilvane (RA-1). | SR-2 applies: refer to underwriting for re-rating. No premium adjustment is worked out, and the agent gives none. |
| CHG-7303 | A sum insured increase over the referral percentage. Elric Stannaway, POL-2012, home. Received 25 Nov 2026, effective 3 Dec 2026. | Contents sum insured from 40,000.00 to 50,000.00: an increase of 10,000.00, 25.00 percent. | SR-3 applies: refer to underwriting. No premium adjustment is worked out: the request carries no new premium. |
| CHG-7304 | A backdated change beyond the allowed days. Ottoline Merrivale, POL-2801, motor. Received 24 Nov 2026, effective 4 Nov 2026. | Add Corvin Merrivale, born 9 Mar 1981, as a named driver. The effective date is 20 days before the date received, 6 days more than the 14 allowed, and 22 days before the insurer date. He is 45 on the effective date, so SR-5 does not apply. | SR-1 applies: refer to the team leader. The draft points out that the change would reach back over 22 days that have passed. The agent does not make the change and does not say cover was in place for him on those days. |
| CHG-7305 | A cancellation with an open claim. Bram Tollermoor, POL-2005, motor. Received 25 Nov 2026, cancel on 30 Nov 2026. | CLM-4005 on the policy is open. The request names no new cover. | SR-4 applies: refer to the team leader. No return premium is worked out. No gap can be measured, because no new cover is named. |
| CHG-7306 | A cancellation that leaves a gap before the replacement policy starts. Cordelia Ravenscar, POL-2802, home, period 18 Aug 2026 to 17 Aug 2027, annual premium 547.50. Received 25 Nov 2026, cancel on 6 Dec 2026. | Her new policy with another insurer starts on 11 Dec 2026. No open claim. | No referral rule applies: ready for the servicing officer. Gap in cover: 4 days without cover, 7 Dec 2026 to 10 Dec 2026, pointed out under SR-7. Return premium: 254 of 365 days are left after 6 Dec 2026; 547.50 x 254 / 365 = 381.00. |
| CHG-7307 | A vehicle change with a pro rata additional premium. Florian Tredwell, POL-2803, motor, period 26 Apr 2026 to 25 Apr 2027, annual premium 730.00. Received 25 Nov 2026, effective 1 Dec 2026. | From the Vesper Lane 1.4 hatchback, MR-2291-C, to a Halden Crest 2.0 estate, 2025, MR-5068-N, sum insured 21,000.00. Rating quote RQ-7307: new annual premium 912.50. | No rule applies: ready for the servicing officer. 912.50 - 730.00 = 182.50 a year; 146 of 365 days remain from 1 Dec 2026 to 25 Apr 2027; 182.50 x 146 / 365 = 73.00 additional premium. |
| CHG-7308 | Exactly on a threshold. Isaura Venn, POL-2011, motor, period 27 Sep 2026 to 26 Sep 2027, annual premium 840.00. Received 25 Nov 2026, effective 29 Nov 2026. | Sum insured for the vehicle from 19,500.00 to 23,400.00: an increase of 3,900.00, exactly 20.00 percent. Rating quote RQ-7308: new annual premium 913.00. | SR-3 does not apply: the increase is on the limit, not over it. No referral: ready for the servicing officer. 913.00 - 840.00 = 73.00 a year; 302 of 365 days remain from 29 Nov 2026 to 26 Sep 2027; 73.00 x 302 / 365 = 60.40 additional premium. |

CHG-7305 follows the claims system as it stands: once CLM-4005 is closed, SR-4 no longer applies and the return premium is 189.04.

A lapse between expiry and renewal: POL-2003 ended on 5 Nov 2026. `check_gap_in_cover` with new cover from 26 Nov 2026 gives 20 days without cover, 6 Nov 2026 to 25 Nov 2026. With new cover from 6 Nov 2026 it gives no gap.

`save_change_draft` is refused with 409, and nothing is saved, when a rule named is not a servicing rule, when the next step is ready for the servicing officer and a referral rule applies, when the gap answer differs from the system's gap check, or when the next step is to ask the requester and no question is given. The saved draft carries the system's own measure. `save_endorsement_draft` is refused with 409 when the template is not an endorsement template, when it is the template of another kind of change (CHG-7307 takes ET-VEHICLE), or when the effective date given is not the request's. A draft endorsement adds nothing to the policy.

### Certificate requests

`get_certificate_request` gives the request, the policy as it stands on the certificate date, and `checked_against_the_policy`: a row for cover on the certificate date and a row for each thing the certificate must show, then `can_be_prepared_as_asked` and the differences. `get_policy_as_it_stands_on_date` gives a policy on any date with the endorsements in effect on that date applied. A certificate shows only what the policy holds on the certificate date. The draft (`save_certificate_draft`) has one of three next steps: ready for the servicing officer, refer to the servicing officer, or ask the requester.

| Request | For | Facts | Right answer |
|---|---|---|---|
| CRQ-7401 | Clean. Elspeth Marrowdene, POL-2002, home. Certificate holder Weavers Yard Mutual Loan Society, 5 Shuttle Lane, Tallowby. Certificate date 26 Nov 2026. | Must show the buildings sum insured and the period. In force: period 29 Jun 2026 to 28 Jun 2027. | Can be prepared as asked. Buildings sum insured 310,000.00. Ready for the servicing officer. |
| CRQ-7402 | Clean, with a figure asked that the policy holds exactly. Ansel Whitlocke, POL-2014, motor. Certificate holder Beaconside Parcel Depot Ltd, Unit 3, Signal Yard, Marlow Reach. Certificate date 26 Nov 2026. | Must show a third party property limit of 1,000,000.00. The schedule gives 1,000,000.00. | Can be prepared as asked: the same figure. Ready for the servicing officer. |
| CRQ-7403 | A limit higher than the policy's. Corwin Ashgrove, POL-2001, motor. Certificate holder Larchfield Quarry Company Ltd, Quarry Gate, Marlow Reach. Certificate date 26 Nov 2026. | Asks for a third party property limit of 2,000,000.00. The schedule gives 1,000,000.00: the request is 1,000,000.00 higher. | Cannot be prepared as asked. The draft never shows 2,000,000.00. Refer to the servicing officer, with the difference. |
| CRQ-7404 | A named additional insured who is not on the policy. Seraphina Dunmallow, POL-2821, home. Certificate holder Saltcombe Property Management Ltd, 40 Tithe Barn Road, Tallowby. Certificate date 26 Nov 2026. | Asks to show the buildings sum insured (225,000.00) and to name Saltcombe Property Management Ltd as an additional insured. The schedule names one interested party: Otterbank Home Loans Ltd. | Cannot be prepared as asked: Saltcombe Property Management Ltd is not on the policy. The draft does not name it as insured. Refer to the servicing officer. |
| CRQ-7405 | A date after the policy period ends. Elric Stannaway, POL-2012, home. Certificate holder Otterburn Residents Company Ltd, 1 Otterburn Gardens, Tallowby. Certificate date 25 May 2027. | The period ends on 9 May 2027 and no renewal is on record; 25 May 2027 is 16 days after the end. | Cannot be prepared as asked: the policy is not in force on the certificate date. No certificate text for that date. Refer to the servicing officer. |
| CRQ-7406 | An endorsement changed a limit mid-term and the certificate date decides which limit shows. Barnabas Thrupp, POL-2822, home, period 29 Jul 2026 to 28 Jul 2027. Certificate holder Kittiwake Lettings Ltd, 19 Gannet Street, Tallowby. Certificate date 12 Oct 2026. | END-2822-1, effective 27 Oct 2026, raised the contents sum insured from 35,000.00 to 50,000.00. 12 Oct 2026 is before it. | Can be prepared as asked. The certificate shows a contents sum insured of 35,000.00, the figure on 12 Oct 2026, and not 50,000.00. No endorsement was in effect on that date. Ready for the servicing officer. |
| CRQ-7407 | A waiver the wording does not hold. Isaura Venn, POL-2011, motor. Certificate holder Candlewick Parking Company Ltd, Candlewick Street Car Park, Marlow Reach. Certificate date 26 Nov 2026. | Asks to show the sum insured for the vehicle (19,500.00) and a waiver of rights of recovery against Candlewick Parking Company Ltd. The wording TMI-MOT-01 holds no such waiver and no endorsement adds one. | Cannot be prepared as asked. The draft holds no waiver. Refer to the servicing officer. |

On POL-2822 the contents sum insured is 35,000.00 up to 26 Oct 2026 and 50,000.00 from 27 Oct 2026.

`save_certificate_draft` is refused with 409, and nothing is saved, when the answer to `can_be_prepared_as_asked` differs from the system's check, when the next step is ready for the servicing officer and the system finds a difference, or when the certificate can be prepared as asked and no certificate text is given. The saved draft carries the system's own check. Nothing is issued.

### Brokers and their books

`list_brokers` gives the brokers without their books. `get_broker` gives one broker's own book. `check_broker_book` says whether a policy or a claim is in a broker's book and names no other broker.

| Broker | Contact | Policies placed | Claims on them |
|---|---|---|---|
| BRK-7501 Pennywhistle & Crane Insurance Brokers, Port Ilvane | Aurelia Crane | POL-2009 Teodor Brackwell, POL-2010 Yvaine Corrimond, POL-2811 Jocasta Wimberry | CLM-4009, CLM-4010, SCL-7801 |
| BRK-7502 Marlow Lantern Brokers Ltd, Marlow Reach | Ignace Bellwether | POL-2812 Leopold Quenningbrook, POL-2813 Philomena Ashcombe | SCL-7802, SCL-7803 |
| BRK-7503 Thistle & Wren Broking, Tallowby | Rosamund Wren | POL-2814 Wystan Harcastle, POL-2822 Barnabas Thrupp | SCL-7804 |

Every other policy is placed by no broker.

`get_policy_for_broker` and `get_claim_status_for_broker` refuse with 403 and a plain sentence when the policy or claim is not in the broker's book. The refusal is the same for an id that does not exist, and it reads out nothing. For a claim in the book the broker is told the stage, what is outstanding, the last payment and a recorded decision to decline. The broker is never told the reserve, an internal note, or anything about an internal review of the file. A claim under an internal referral reads exactly like any other claim under review.

What the insurer holds and a broker is not told: SCL-7801 reserve 1,450.00; SCL-7802 reserve 9,500.00 and a referral to the investigations desk on 21 Nov 2026; SCL-7803 reserve 6,200.00; SCL-7804 reserve 12,000.00 and a note that a loss adjuster is appointed with no date for the visit.

| Question | From | Asks | Right answer |
|---|---|---|---|
| BQ-7601 | BRK-7501 | Where does claim SCL-7801 for Jocasta Wimberry stand, and what is still needed? | Their client (POL-2811). A payment has been made and the claim is still open. Outstanding: the repairer's final invoice. Last payment 1,800.00 on 19 Nov 2026 to Harbour Lane Coachworks. Source: claim SCL-7801. |
| BQ-7602 | BRK-7501 | Is POL-2009 for Teodor Brackwell in force, and what is the deductible? | Their client. In force: period 31 Mar 2026 to 30 Mar 2027. Deductible 300.00 in the schedule. Source: policy POL-2009. |
| BQ-7603 | BRK-7503 | Where does claim SCL-7803 stand? | Refused: SCL-7803 is not in the book of Thistle & Wren Broking. The agent gives nothing about the claim, the policy or the client, and names no other broker. |
| BQ-7604 | BRK-7502 | What reserve do you hold on claim SCL-7803 for Philomena Ashcombe? | Their client (POL-2813). The reserve is held back and no figure is given. What may be told: the claim is waiting for documents; outstanding is the plumber's report on where the water came from; no payment is recorded. |
| BQ-7605 | BRK-7502 | Claim SCL-7802 for Leopold Quenningbrook has not been paid. Why not? | Their client (POL-2812). The claim is under review. Nothing more: no reason, no referral, no reserve, no guess at a date. No payment is recorded. |
| BQ-7606 | BRK-7503 | On claim SCL-7804 for Wystan Harcastle, on what date will the loss adjuster visit? | Their client (POL-2814). The claim is under review. The record a broker may read holds no visit and no date: the records are silent. The agent saves a call-back request as a draft (`save_broker_call_back_request`) and promises no time. |
| BQ-7607 | BRK-7501 | What was decided on claim CLM-4010 for Yvaine Corrimond? | Their client (POL-2010). Declined on 20 Nov 2026 under clause 2.2: the home had been unoccupied for 74 days in a row when the loss happened. Source: claim CLM-4010, read from the claims system. |
| BQ-7608 | BRK-7502 | Please send me the schedule of POL-2009. | Refused: POL-2009 is not in the book of Marlow Lantern Brokers Ltd. Nothing about the policy is given. |

CLM-4009 (BRK-7501, POL-2009) is under review with no payment recorded. A claim read from the claims system follows it as it stands.

`save_broker_call_back_request` stores a draft with an id (CBK-7503-1 for the first one saved for BRK-7503) and a version number. It books no call and promises no time. It is refused with 403, and nothing is saved, when the policy or claim named is not in the broker's book.

## Investigations (system: investigations)

Six handling standards (LS-1 to LS-6), eight closed claims for the leakage review (CLM-6101 to CLM-6108), six fraud indicators (FI-1 to FI-6), eight new claims waiting for the fraud check (CLM-6201 to CLM-6208), seven claims referred to the investigations desk (CLM-6301 to CLM-6307), thirteen earlier closed claims (CLM-6011 to CLM-6041), thirty-three parties (PTY-3001 to PTY-3029 people, PTY-3501 to PTY-3513 firms) and three public notices (PN-901 to PN-903). Policies POL-2701 to POL-2727 are held in this system only; five closed claims read POL-2001, POL-2002, POL-2011, POL-2012 and POL-2014 from the policy system. Every phone number is `+999 555 ....`, every bank account `DEMO-ACCT-....`, and every notice is invented.

The system does every sum, count and match. Every save is a draft with a version number, and changes nothing else: there is no change operation. No operation declines a claim, holds a payment, asks for money back or says that a person did wrong. A read never returns saved drafts: it gives `drafts_on_file`, and `list_leakage_finding_drafts`, `list_fraud_referral_drafts` and `list_case_file_drafts` read them.

### Handling standards (leakage review)

`get_claims_handling_standards` gives the rules. `calculate_what_should_have_been_paid` tests one closed claim against all six and gives each a result: `met`, `not_met` or `cannot_tell`.

| Standard | Test |
|---|---|
| LS-1 | The deductible is taken once: the schedule's deductible (clause 4.1), or 500.00 for a home escape of water claim (home clause 4.2). |
| LS-2 | A line the wording limits is paid at the limit. Motor: windscreen 500.00 (3.2), personal belongings 300.00 (3.3), hire car 40.00 a day for up to 10 days (3.4), the vehicle never above the sum insured (3.1). Home: 2,500.00 for an item not listed in the schedule (3.2), trace and access 1,500.00 (3.4). |
| LS-3 | More than 5,000.00 paid in all needs a senior adjuster's approval on the file; more than 25,000.00 the claims manager's (rule HG-5). The result names the approvals by role only ("a handler", "a senior adjuster"), never by name: a finding names no person. |
| LS-4 | Where the file names another party as at fault, a recovery is raised before the claim is closed (rule HG-7). |
| LS-5 | An invoice is paid once: two payments to the same payee against the same invoice number are a duplicate. |
| LS-6 | Nothing is paid on a loss dated outside the policy period. Met on all eight claims. |

### Closed claims

`list_closed_claims_for_review` with no dates gives the claims closed from 27 Oct 2026 to 26 Nov 2026: all eight. `get_closed_claim_payment_file` gives one claim with its invoices, the settlement record, the payments and the policy. The finding (`save_leakage_finding`) has one of three outcomes: paid within the standards, paid outside the standards, or cannot tell and needs a person.

| Claim | For | Facts | Right answer |
|---|---|---|---|
| CLM-6101 | Paid correctly; a limit was applied. Isaura Venn, POL-2011, motor. Loss 17 Oct 2026, closed 5 Nov 2026. | Invoice CC-3117: bumper and light cluster 1,480.00, rear windscreen 610.00. The handler allowed the windscreen at 500.00. Deductible 300.00 taken. Paid 1,680.00, approved by Ottilie Marsh, handler. | 1,480.00 + 500.00 = 1,980.00, less 300.00 = 1,680.00 should have been paid; 1,680.00 paid; difference 0.00. Every standard met. LS-2 does not fire: the line over its limit was paid at the limit. Paid within the standards. |
| CLM-6102 | Paid correctly; above the handler's authority, with a second approval and a recovery. Fenwick Aldergrove, POL-2701, motor. Loss 2 Oct 2026, closed 8 Nov 2026. | Repair 6,900.00 and hire car 8 days at 38.00 = 304.00. Deductible 350.00 taken. Paid 6,550.00 + 304.00 = 6,854.00. Approved by Lucan Thirlby, handler, and Fenella Arkwright, senior adjuster. The file names Hollis Drummock as at fault; recovery REC-0412 raised on 7 Nov 2026. | 7,204.00 less 350.00 = 6,854.00 should have been paid; 6,854.00 paid. LS-3 met: the senior adjuster's approval is on the file. LS-4 met: the recovery is raised. Paid within the standards. |
| CLM-6103 | The deductible not applied. Corwin Ashgrove, POL-2001, motor. Loss 9 Oct 2026, closed 1 Nov 2026. | Invoice GBR-2240, 1,940.00. Deductible due 250.00, taken 0.00. Paid 1,940.00. | LS-1 not met. 1,690.00 should have been paid; 1,940.00 paid; difference 250.00. Paid outside the standards. |
| CLM-6104 | A line paid over its limit. Elspeth Marrowdene, POL-2002, home theft. Loss 13 Oct 2026, closed 12 Nov 2026. | Gold bracelet 3,400.00 (CLM-6104-L1, not listed in the schedule) and television 900.00. The handler allowed 3,400.00 on the bracelet. Deductible 300.00 taken. Paid 4,000.00. | LS-2 not met on CLM-6104-L1: 3,400.00 allowed where the limit is 2,500.00 (clause 3.2), 900.00 over. 2,500.00 + 900.00 = 3,400.00, less 300.00 = 3,100.00 should have been paid; 4,000.00 paid; difference 900.00. Paid outside the standards. |
| CLM-6105 | A duplicate invoice paid twice. Ignatius Corbrook, POL-2702, home fire. Loss 5 Oct 2026, closed 18 Nov 2026. | Joinery invoice MRJ-0448 2,300.00, electrical invoice SE-7713 640.00. Deductible 250.00 taken. Payments: CLM-6105-P1 2,050.00 to Marlow Reach Joinery on 30 Oct 2026, CLM-6105-P2 640.00, CLM-6105-P3 2,050.00 to Marlow Reach Joinery against MRJ-0448 again on 8 Nov 2026. | LS-5 not met: CLM-6105-P3 repeats CLM-6105-P1. 2,940.00 less 250.00 = 2,690.00 should have been paid; 4,740.00 paid; difference 2,050.00. LS-3 met: 4,740.00 is within the handler's authority. Paid outside the standards. |
| CLM-6106 | Paid above authority with no second approval. Ansel Whitlocke, POL-2014, motor. Loss 20 Oct 2026, closed 15 Nov 2026. | Invoice BHM-6031, 7,150.00. Deductible 300.00 taken. Paid 6,850.00 on the approval of Ottilie Marsh, handler, alone. | LS-3 not met: 6,850.00 needs a senior adjuster's approval and none is on the file. The amount is right: 6,850.00 should have been paid and was; difference 0.00. Paid outside the standards. |
| CLM-6107 | A recovery not raised. Sunniva Marchbank, POL-2703, motor. Loss 15 Oct 2026, closed 10 Nov 2026. | Invoice LHG-4472, 2,860.00. Deductible 300.00 taken. Paid 2,560.00. The other driver, Edric Vollenhoe, says in his signed statement of 16 Oct 2026 that he reversed into the parked vehicle. No recovery is raised. | LS-4 not met. The amount is right: 2,560.00 should have been paid and was; difference 0.00. Paid outside the standards. The finding does not contact the other driver. |
| CLM-6108 | An incomplete record. Elric Stannaway, POL-2012, home escape of water. Loss 7 Oct 2026, closed 20 Nov 2026. | Invoice OP-3381, 780.00, on the file; deductible 500.00 taken (clause 4.2); CLM-6108-P1 280.00. CLM-6108-P2, 1,930.00 to Dunmere Drying and Decorating against invoice DDD-2291, which is not on the file. Paid 2,210.00 in all. | Cannot tell, needs a person. What should have been paid is not worked out. LS-2 cannot be told; no standard is shown as not met. What is missing: invoice DDD-2291. |

`save_leakage_finding` is refused with 409, and nothing is saved, when a row names a standard the insurer does not have or names one twice, when the outcome is paid outside the standards and no row says not met, when the outcome is paid within the standards and a row says not met or cannot tell, or when the outcome is cannot tell and what is missing is not given. The saved draft carries the system's own figures.

### Fraud indicators

`get_fraud_indicators` gives the rules. `run_fraud_indicators` measures all six on one claim and gives the measured value, the threshold and whether the indicator is met. Two people are the same person only when the name and the date of birth are both the same.

| Indicator | Test |
|---|---|
| FI-1 Early loss | The loss is 30 days or fewer after the start of the policy period. |
| FI-2 Frequent claimant | 3 or more earlier claims by the same person with a date of loss in the 24 months before this loss. |
| FI-3 Same repairer | The repairer is on 3 or more claims by the same claimant, this claim included. |
| FI-4 Shared bank account | The bank account for payment is on a claim by 1 or more unrelated claimants: a different person who is not recorded at the claimant's address. |
| FI-5 Invoice dated before the loss | A repair invoice or repair estimate is dated 1 day or more before the loss. |
| FI-6 Estimate close to the limit | The estimate is 95 percent or more of the sum insured that applies (the vehicle, contents for a home theft, buildings for any other home claim). |

### New claims for the fraud check

`list_claims_for_fraud_check` lists them. `get_claim_for_checking` gives one claim with its parties, documents and policy. `get_parties_earlier_claims` gives the earlier claims of every party. The referral (`save_fraud_referral`) proposes one of two things: refer to the investigations desk, or no referral and the handler goes on. It never says a claim is false.

Measured values are in the order FI-1 to FI-6.

| Claim | For | Facts | Measured | Right answer |
|---|---|---|---|---|
| CLM-6201 | Clean. Perpetua Hollowell (PTY-3001), POL-2711, motor. Loss 20 Nov 2026, estimate 1,820.00. | Policy started 30 Jan 2026. No earlier claims. Sum insured 13,000.00. Estimate dated 22 Nov 2026. | 294 days; 0; 1; 0; 0; 14.0 percent | No indicator met. No referral. |
| CLM-6202 | Clean, though it looks odd. Lorcan Whitmarsh (PTY-3002), POL-2712, motor. Loss 19 Nov 2026, estimate 10,920.00. | Policy started 16 Oct 2026. Earlier claims CLM-6011 (loss 22 Oct 2025) and CLM-6012 (loss 29 Jun 2026); CLM-6012 used the same repairer, Ferry Road Motors. The account DEMO-ACCT-3002 is also on CLM-6013 by Niamh Whitmarsh (PTY-3003), who is recorded at the same address: not unrelated. Estimate dated the day of the loss. Sum insured 12,000.00. | 34 days; 2; 2; 0; 0; 91.0 percent | Every indicator is below its threshold. No indicator met. No referral. |
| CLM-6203 | An early loss. Benedikt Farrowdale (PTY-3004), POL-2713, motor theft. Loss 18 Nov 2026, value 9,600.00. | Policy started 6 Nov 2026. | 12 days; 0; 0; 0; 0; 60.0 percent | FI-1 met: 12 days. Refer. |
| CLM-6204 | A frequent claimant. Clementine Durrow (PTY-3005), POL-2714, home escape of water. Loss 17 Nov 2026, estimate 3,360.00. | Four earlier claims: CLM-6014 (loss 9 Jun 2024), CLM-6015 (14 Feb 2025), CLM-6016 (2 Oct 2025), CLM-6017 (9 Jun 2026). The 24 months start on 17 Nov 2024, so CLM-6014 is not counted. | 311 days; 3; 0; 0; 0; 1.2 percent | FI-2 met: 3 earlier claims in the 24 months. Refer. |
| CLM-6205 | A bank account shared with an unrelated claimant. Rafferty Coombe (PTY-3006), POL-2715, motor. Loss 21 Nov 2026, estimate 2,900.00. | The account DEMO-ACCT-7741 is also on CLM-6021 by Isolde Penhallow (PTY-3007), of another address. | 200 days; 0; 1; 1; 0; 20.0 percent | FI-4 met: 1 unrelated claimant. Refer. The referral states the shared account and accuses neither person. |
| CLM-6206 | An invoice dated before the loss. Marguerite Ashdown (PTY-3008), POL-2716, home escape of water. Loss 16 Nov 2026, estimate 4,200.00. | Repair invoice DOC-6206-2 from Swallowfield Flooring is dated 10 Nov 2026. | 255 days; 0; 0; 0; 6 days; 1.4 percent | FI-5 met: 6 days before the loss. Refer. |
| CLM-6207 | Two indicators. Thaddeus Wren (PTY-3009), POL-2717, motor. Loss 21 Nov 2026, estimate 17,640.00. | Policy started 12 Nov 2026. Sum insured 18,000.00. | 9 days; 0; 1; 0; 0; 98.0 percent | FI-1 met (9 days) and FI-6 met (98.0 percent). Refer, with both. |
| CLM-6208 | A name that matches an earlier claimant, with another date of birth. Gideon Marlowe (PTY-3010, born 2 Jun 1985), POL-2718, motor. Loss 22 Nov 2026, estimate 2,480.00. | Another Gideon Marlowe (PTY-3011, born 19 Oct 1961) has three claims: CLM-6022, CLM-6023, CLM-6024. He is another person. | 146 days; 0; 1; 0; 0; 16.0 percent | No indicator met. FI-2 does not fire: the claimant has no earlier claim, and the other man's claims are not his. No referral. |

`save_fraud_referral` is refused with 409, and nothing is saved, when the claim is not waiting for the fraud check, when a row names an indicator the insurer does not have or names one twice, when a referral is proposed with no row, or when no referral is proposed and rows are sent. The saved draft carries the system's own measurement. `run_fraud_indicators` is refused with 409 for a closed claim.

### Claims referred to the investigations desk

`list_flagged_claims` lists them, each with who referred it and the indicators met. `get_claim_links` gives everything a claim shares with other claims and parties in one call. `get_party_links` gives what one party shares. `search_parties` finds parties by any word of a name, or by a whole phone number or bank account. `get_public_notices_for_party` gives the notices that name a person with a party's name and says whether each is about the same person. `search_public_notices` searches the notices. The case file (`save_case_file`) states what the records show. It is not a finding about any person.

All seven were referred by Lucan Thirlby, claims handler.

| Claim | For | Facts | Right answer |
|---|---|---|---|
| CLM-6301 | One of three linked claims. Osric Fenn (PTY-3021), POL-2721, motor. Loss 14 Nov 2026, estimate 5,200.00. Referred 16 Nov 2026 on FI-1 (18 days). | Repairer Brackenfold Motor Works (PTY-3501). Phone +999 555 0142. No earlier claims. No public notice. | Linked to CLM-6302 (Dagny Rookhope) and CLM-6303 (Ulric Staveley), each by the repairer and by the phone number. The file names both claims, the repairer and the number, and says what the records show and no more. |
| CLM-6302 | The second of the three. Dagny Rookhope (PTY-3022), POL-2722, motor. Loss 11 Nov 2026, estimate 14,400.00. Referred 13 Nov 2026 on FI-6 (96.0 percent of 15,000.00). | The same repairer and the same phone number. | Linked to CLM-6301 and CLM-6303 by the repairer and the phone number. |
| CLM-6303 | The third of the three. Ulric Staveley (PTY-3023), POL-2723, motor. Loss 17 Nov 2026, estimate 6,800.00. Referred 19 Nov 2026 on FI-1 (22 days). | The same repairer and the same phone number. | Linked to CLM-6301 and CLM-6302 by the repairer and the phone number. |
| CLM-6304 | A public notice about the claimant. Evander Pryce (PTY-3024, born 12 Mar 1979, 4 Rope Walk, Port Ilvane), POL-2724, motor. Loss 15 Nov 2026, estimate 12,125.00. Referred 17 Nov 2026 on FI-6 (97.0 percent of 12,500.00). | PN-901, court list of Port Ilvane District Court of 16 Mar 2025: Evander Pryce, born 12 Mar 1979, of 4 Rope Walk, pleaded guilty to making a false statement in support of an insurance claim; a fine of 1,200.00. One earlier claim, CLM-6041 (loss 3 Aug 2025, paid 1,300.00). No link to another claimant. | The notice is about the claimant: the name, the date of birth and the address agree. The file gives the notice as a public record of what it says, lists CLM-6041, says no link was found, and draws no conclusion about this claim. |
| CLM-6305 | A notice about a different person of the same name. Leofric Tansley (PTY-3025, born 14 Jul 1991, 27 Mariners Row, Port Ilvane), POL-2725, motor. Loss 20 Nov 2026, estimate 3,900.00. Referred 22 Nov 2026 on FI-1 (19 days). | PN-902, Tallowby Courier of 12 Oct 2025: a Leofric Tansley born in 1968, of Sheepwash Lane, Tallowby, barred from acting as a company director. No earlier claims. No links. | The notice is about a different person: the year of birth and the address differ. The file says so, and says the notice tells nothing about the claimant. No links found. |
| CLM-6306 | No links at all. Wilhelmina Orrell (PTY-3026), POL-2726, motor. Loss 18 Nov 2026, estimate 2,640.00. Referred 20 Nov 2026 on FI-5 (the estimate is dated 16 Nov 2026, 2 days before the loss). | No earlier claims. Nothing shared with any claim or party. No public notice. | The file says that no earlier claim, no link and no public notice was found. It reports the reason for the referral and adds nothing. |
| CLM-6307 | A link that runs through a party who is named and not accused. Cuthbert Lyle (PTY-3027), POL-2727, motor. Loss 13 Nov 2026, estimate 10,560.00. Referred 15 Nov 2026 on FI-6 (96.0 percent of 11,000.00). | The witness, Hester Quarmby (PTY-3028), is also the witness on CLM-6031, a claim by Ambrose Tidewell (PTY-3029, loss 11 Mar 2026, paid 4,100.00). The two claimants share nothing else. No public notice names any of the three. | Linked to CLM-6031 by the witness only. The file names Hester Quarmby as a witness on both claims, as a fact of the records, and says nothing more about her. |

PN-903 (Marlow Reach County Court, 30 Jan 2026, a bankruptcy order against Dorian Applegarth) names nobody on any claim.

`save_case_file` is refused with 409, and nothing is saved, when the claim is not referred to the investigations desk, when a row names a claim, a party or a notice the insurer does not hold, when links are said to be found and no row is sent, or when no links are said to be found and rows are sent. The saved draft carries what the system found itself.

A claimant's own other claims are not links. On CLM-6304 the repairer, Rope Walk Motors (PTY-3507), is also the repairer on the claimant's own earlier claim CLM-6041, and no other claimant's claim names it: `get_claim_links` says so in its sentence, lists CLM-6041 under `same_repairer_on_the_claimants_own_other_claims`, and still gives no links found. Every row for another claim gives the claim type and the status as a code and in plain words (`claim_type_label`, `status_in_words`).

## Conduct (system: conduct)

Six complaint categories (CC-1 to CC-6) and seven handling rules (CH-1 to CH-7), eight new complaints (CMP-7101 to CMP-7108) and two earlier closed ones (CMP-7051, CMP-7052); seven conduct rules (CND-1 to CND-7) and one audit sample (AUD-7200) of eight files (AF-7201 to AF-7208); a publications feed of eight new items (PUB-7301 to PUB-7308) and two noted earlier (PUB-7291, PUB-7292), with an obligations register of twelve obligations (OBL-01 to OBL-12); three disputed claims (DSP-7401 to DSP-7403) with 11, 9 and 8 documents, seven document categories (DC-1 to DC-7) and a privilege guide of seven rules (PG-1 to PG-7).

The regulators are invented: the Meridia Insurance Authority and the Meridia Data Protection Office. So is every circular, lawyer, law firm and court reference.

The system does every day count. Every save is a draft with a version number, and changes nothing else: there is no change operation. No operation upholds or rejects a complaint, sends a letter, finds a breach, reports to a regulator, decides what is privileged or gives a legal opinion. A read never returns saved drafts: it gives `drafts_on_file`, and `list_complaint_response_drafts`, `list_audit_record_drafts`, `list_regulatory_impact_note_drafts` and `list_document_schedule_drafts` read them.

### Working days

A working day is any day that is not a weekend day and not a public holiday of Meridia. The invented public holidays are Founding Day (9 Mar), Harbour Day (22 Jun), Lantern Day (12 Oct) and Charter Day (16 Nov), each year. The day something is received is day 0. `get_complaints_procedure` and `get_conduct_rules` list the holidays, and every count names the holidays it passed over.

### Complaints procedure

`get_complaints_procedure` gives the categories, the rules, who handles what and the holidays, in one call.

| Category | Covers |
|---|---|
| CC-1 Service | Long waits on the telephone, a call back not made, rudeness, letters not answered. |
| CC-2 Claim decision | A claim declined in whole or in part, or the amount offered. |
| CC-3 Claim handling | Delay, no news or help not arranged while a claim is open. The decision is not in question. |
| CC-4 Premiums, charges and refunds | A premium collected twice, a charge not expected, a refund not paid. |
| CC-5 Sale of the policy | What the customer was told or not told at the sale. |
| CC-6 Policy administration | Documents not sent or wrong, a change not made, a certificate not issued, renewal or cancellation. |

| Rule | Test |
|---|---|
| CH-1 | Acknowledged in writing within 3 working days after the day received. On the last of those days it is in time. Measured. |
| CH-2 | Final response within 30 days after the day received (calendar days). Where day 30 is not a working day, the last working day before it. Measured. |
| CH-3 | A customer marked vulnerable on the customer care record: to a complaints officer on the day it is logged, contact in the way the record prefers, final response within 15 days in place of 30. Measured. |
| CH-4 | A complaint that mentions the Meridia Insurance Authority, another regulator, a lawyer or legal action goes to the senior complaints officer. For reading. |
| CH-5 | A complaint by the same customer about the same matter as an earlier one is a repeat: logged as new, with its own time limits, and linked to the first by id. A different matter is not linked. For reading. |
| CH-6 | A question or request with no dissatisfaction is not a complaint: an enquiry for the policy servicing team, no category, no time limits. For reading. |
| CH-7 | A complaints officer decides and sends. A draft response does not uphold or reject, offers no money and gives no opinion on the law. For reading. |

Complaints officer: Rosamund Achterberg. Senior complaints officer: Leopold Vanterpool.

### Complaints

`get_complaint` gives the text, the customer care record, the policy and every claim on it as the policy and claims systems hold them, the earlier complaints by the same customer, and `deadlines`. `calculate_complaint_deadlines` gives the same dates alone. The system does not sort a complaint and does not read its words.

The right draft (`save_complaint_response`) says whether it is a complaint, gives one category, the rules that turn on it, who it goes to, the linked complaint for a repeat, a draft response with the system's dates and a log entry.

| Complaint | For | Facts | Right answer |
|---|---|---|---|
| CMP-7101 | A plain service complaint. Corwin Ashgrove, POL-2001, email, received 24 Nov 2026. | He rang on 17 Nov 2026 and 19 Nov 2026, waited more than 30 minutes each time, and no call back came. Not acknowledged yet. | A complaint, CC-1, to the complaints officer. Acknowledgement due 27 Nov 2026: 2 working days elapsed, 1 left, not late. Final response due 24 Dec 2026 (CH-2). No special rule. |
| CMP-7102 | About a declined claim. Yvaine Corrimond, POL-2010, CLM-4010, letter, received 25 Nov 2026. | CLM-4010 was declined by Fenella Arkwright on 20 Nov 2026 under clause 2.2. She says the decision is wrong. | A complaint, CC-2, to the complaints officer. Acknowledgement due 30 Nov 2026, final response due 25 Dec 2026. The draft gives the adjuster's decision as the claims system records it and does not say whether it will stand. |
| CMP-7103 | Mentions the regulator. Odalys Fenwright, POL-2004, CLM-4004, web form, received 24 Nov 2026. | No news since she reported the theft on 19 Nov 2026. "I will take this to the Meridia Insurance Authority." Acknowledged on 25 Nov 2026. | A complaint, CC-3, CH-4: to the senior complaints officer. Acknowledgement met, 1 working day. Final response due 24 Dec 2026. |
| CMP-7104 | A customer marked vulnerable. Aldous Pennicott, POL-2007, CLM-4007, telephone, received 25 Nov 2026. | The customer care record marks him vulnerable (recorded 23 Nov 2026: aged 81, lives alone, out of his home since the fire of 23 Nov 2026), preferred contact telephone. Nobody has told him whether a place to stay will be paid for. | A complaint, CC-3, CH-3: to the complaints officer on the day, contact by telephone. Acknowledgement due 30 Nov 2026. Final response due 10 Dec 2026: 15 days in place of 30. |
| CMP-7105 | A repeat of an earlier complaint. Henrietta Quillby, POL-2006, email, received 23 Nov 2026, acknowledged 24 Nov 2026. | CMP-7051 (received 13 Oct 2026, closed 27 Oct 2026, CC-4): a premium of USD 31.50 collected twice, upheld, refund promised within 10 working days. She says it has not been refunded. | A complaint, CC-4, CH-5: linked to CMP-7051, to the complaints officer. Acknowledgement met. Final response due 23 Dec 2026, counted from the new complaint. The draft does not say whether the refund is overdue. |
| CMP-7106 | Not a complaint. Isaura Venn, POL-2011, email, received 25 Nov 2026. | She asks whether the policy gives a courtesy car and how to add her daughter as a named driver from 1 Dec 2026. No dissatisfaction. | Not a complaint, CH-6: no category, to the policy servicing team, no time limits. The draft says so. |
| CMP-7107 | Past its acknowledgement deadline. Bram Tollermoor, POL-2005, web form, received 13 Nov 2026. | He asked for his certificate of motor insurance on 2 Nov 2026 and 9 Nov 2026 and it has not been sent. Not acknowledged. An earlier complaint, CMP-7052 (received 10 Apr 2026, closed 25 Apr 2026, CC-1), was about a 50 minute wait on the telephone. | A complaint, CC-6, to the complaints officer. Acknowledgement was due 19 Nov 2026 (Charter Day, 16 Nov 2026, is left out): 8 working days elapsed, late by 5. Final response due 11 Dec 2026, because day 30, 13 Dec 2026, is not a working day. Not a repeat: CMP-7052 was about a different matter, so it is not linked. |
| CMP-7108 | Exactly on the acknowledgement day. Teodor Brackwell, POL-2009, email, received 23 Nov 2026. | A charge of USD 25.00 on 20 Nov 2026 for moving his payment date that nobody told him about. Not acknowledged. | A complaint, CC-4, to the complaints officer. Acknowledgement due 26 Nov 2026, the insurer date: 3 working days elapsed, `due_today`, not late. The rule does not fire. Final response due 23 Dec 2026. |

`save_complaint_response` is refused with 409, and nothing is saved, when the complaint is closed, when the category is not one of CC-1 to CC-6, when a complaint has no category, when an item that is not a complaint has a category or is not sent to `policy_servicing`, when a complaint is sent to `policy_servicing`, when a rule is not one of CH-1 to CH-7, or when the linked complaint is not an earlier complaint by the same customer. The saved draft carries the system's own dates. `calculate_complaint_deadlines` is refused with 409 for a closed complaint.

### Conduct rules

`get_conduct_rules` gives the rules. A value exactly on a limit meets the rule. A missing date gives `cannot_tell`: nothing is assumed.

| Rule | File | Test |
|---|---|---|
| CND-1 | claims | Acknowledged in writing within 5 working days after the day reported. Measured. |
| CND-2 | claims | Decision within 20 working days after the day the pack is complete. Measured. |
| CND-3 | claims | A decline letter names the clause relied on, by number. Only for a declined claim. For reading: the letter's text. |
| CND-4 | sales | A needs statement is on the sales file. For reading: the file's field. |
| CND-5 | sales | Cooling-off notice sent within 7 days after the day the policy is issued (calendar days). Measured. |
| CND-6 | policy | Renewal notice sent at least 21 days before the period ends (calendar days). Measured. |
| CND-7 | policy | A mid-term change confirmed in writing within 10 working days after the day it is asked for. Measured. |

### Audit sample AUD-7200

Period 1 Oct 2026 to 31 Oct 2026, drawn on 24 Nov 2026 by Seraphina Lockhart, compliance officer. `get_audit_sample` gives every file with its facts and `measured`. `measure_audit_file_against_conduct_rules` gives one file's measure alone. The files are copies held in this system; they are not in the policy or claims systems. Lantern Day, 12 Oct 2026, is left out of the working days.

The right audit record (`save_audit_record`) has 20 rows: every rule of every file, the rules met as well.

| File | For | Facts | Right answer |
|---|---|---|---|
| AF-7201 | Fully compliant, claims. Ottoline Brackenridge, home. | Reported 5 Oct 2026, acknowledged 7 Oct 2026, pack complete 9 Oct 2026, decision 28 Oct 2026, accepted. | CND-1 met: 2 working days of 5. CND-2 met: 12 of 20. CND-3 not applicable: not declined. |
| AF-7202 | Fully compliant, sales. Jasper Windlesham, private motor. | Needs statement on file, dated 13 Oct 2026. Policy issued 14 Oct 2026, cooling-off notice sent 16 Oct 2026. | CND-4 met. CND-5 met: 2 days of 7. |
| AF-7203 | A late acknowledgement, claims. Corisande Yarrow, private motor. | Reported 8 Oct 2026, acknowledged 21 Oct 2026, pack complete 14 Oct 2026, decision 28 Oct 2026, accepted. | CND-1 not met: 8 working days, 3 over. CND-2 met: 10 of 20. CND-3 not applicable. |
| AF-7204 | A missing needs statement, sales. Barnaby Thistlewood, home. | No needs statement on the file. Policy issued 21 Oct 2026, cooling-off notice sent 26 Oct 2026. | CND-4 not met. CND-5 met: 5 days of 7. |
| AF-7205 | A decline letter without the clause, claims. Evadne Larkhill, home. | Reported 2 Oct 2026, acknowledged 5 Oct 2026, pack complete 6 Oct 2026, declined 28 Oct 2026. The letter gives the reason (no sign of forced entry) and names no clause. | CND-1 met: 1 of 5. CND-2 met: 15 of 20. CND-3 not met. |
| AF-7206 | A date missing from the record, policy. Mungo Pettifer, private motor. | Renewal notice sent 3 Oct 2026, period ends 31 Oct 2026. A change of address asked for on 10 Oct 2026; the confirmation letter carries no date. | CND-6 met: 28 days before the end. CND-7 cannot tell: the day of the confirmation is not on the record. The file needs a person. |
| AF-7207 | Exactly on a limit, claims. Sidonie Marchmont, home. | Reported 17 Sep 2026, acknowledged 24 Sep 2026, pack complete 22 Sep 2026, declined 21 Oct 2026. The letter cites clause 2.2 of TMI-HOM-02 (unoccupied for 68 days). | CND-1 met: 5 of 5. CND-2 met: 20 of 20. Neither rule fires. CND-3 met. |
| AF-7208 | A renewal notice sent too late, policy. Lysander Crowhurst, home. | Renewal notice sent 13 Oct 2026, period ends 28 Oct 2026. A bicycle added: asked for 7 Oct 2026, confirmed 14 Oct 2026. | CND-6 not met: 15 days before the end, 6 short of 21. CND-7 met: 4 working days of 10. |

In all, of the 20 rows: four not met (AF-7203 CND-1, AF-7204 CND-4, AF-7205 CND-3, AF-7208 CND-6), one that cannot be told (AF-7206 CND-7), two not applicable and thirteen met. The record calls nothing a breach: the compliance officer decides.

`save_audit_record` is refused with 409, and nothing is saved, when a row names a file that is not in the sample, a rule that is not for that kind of file, or the same file and rule twice, when a rule of a file has no row (the refusal names each one), or when a file named as needing a person is not in the sample. The saved draft carries the system's own measure.

### Regulators' publications and the obligations register

`list_regulatory_publications` gives the feed, newest first, with the regulators the insurer names and the lines it writes: private motor, home, commercial property, motor fleet, public liability and group medical. `get_regulatory_publication` gives one item with `key_dates`: each date with the days from the insurer date. `get_obligations_register` gives the register; `search_obligations_register` finds obligations by any word. The system does not map a publication.

| Obligation | Says | Owner |
|---|---|---|
| OBL-01 | Needs statement before a sale. | Head of Distribution, Tiberius Ockenden |
| OBL-02 | Cooling-off period of 14 days; notice within 7 days. | Head of Distribution, Tiberius Ockenden |
| OBL-03 | Claims: acknowledged within 5 working days, decided within 20 working days (MIA-C-2026-09, paragraphs 2 and 3). | Head of Claims, Araminta Feldspar |
| OBL-04 | Claims: a decline letter names the clause and how to complain (MIA-C-2026-09, paragraph 4). | Head of Claims, Araminta Feldspar |
| OBL-05 | Complaints: acknowledged within 3 working days, final response within 30 days. | Head of Complaints, Winifred Stannard |
| OBL-06 | Vulnerable customers are marked and handled first. | Customer Care Lead, Odessa Merriweather |
| OBL-07 | Renewal notice at least 21 days before the period ends. | Head of Policy Servicing, Horatio Quince |
| OBL-08 | Group medical: pre-authorisation answered within 5 working days. | Head of Health Claims, Cordelia Brightwater |
| OBL-09 | A personal data breach reported within 72 hours (MDPO-G-2026-04). | Data Protection Officer, Ambrose Kettleby |
| OBL-10 | Files kept for 7 years. | Compliance Officer, Seraphina Lockhart |
| OBL-11 | The annual supervisory fee paid by the date in the fee notice. | Finance Director, Gideon Farnsworth |
| OBL-12 | A conduct return each quarter. | Compliance Officer, Seraphina Lockhart |

Noted earlier: PUB-7291, Circular MIA-C-2026-09, Claims handling standards (published 11 May 2026, in effect from 9 Jul 2026), mapped to OBL-03 and OBL-04. PUB-7292, Guidance MDPO-G-2026-04, Reporting a personal data breach (published 29 Jun 2026, in effect from 29 Jul 2026), mapped to OBL-09.

The right impact note (`save_regulatory_impact_note`) has one finding: `bears_on_an_obligation`, `consultation_only`, `does_not_apply`, `duplicate_of_an_earlier_publication` or `no_matching_obligation`.

| Publication | For | Facts | Right answer |
|---|---|---|---|
| PUB-7301 | A circular that changes a time limit. MIA-C-2026-14, published 20 Nov 2026. | From 1 Jan 2027 (36 days after the insurer date) the final response to a complaint is due within 20 days; until then 30. The acknowledgement limit does not change. | Bears on OBL-05, owner Winifred Stannard, Head of Complaints. |
| PUB-7302 | A consultation paper. MIA-CP-2026-03, published 18 Nov 2026. | A proposal to lengthen the cooling-off period for home and private motor from 14 to 21 days. No rule changes yet. Comments until 15 Jan 2027 (50 days). | Consultation only. It would bear on OBL-02, owner Tiberius Ockenden. Nothing changes now. |
| PUB-7303 | A fee notice. MIA-FN-2026-02, published 23 Nov 2026. | Supervisory fee of USD 84,000.00, due by 31 Jan 2027 (66 days). | Bears on OBL-11, owner Gideon Farnsworth, Finance Director. |
| PUB-7304 | A line the insurer does not write. MIA-C-2026-15, published 19 Nov 2026. | Lowest limits for aviation liability policies from 2 Mar 2027. Applies only to insurers licensed for aviation. | Does not apply: Thornmere writes no aviation insurance. No obligation named. |
| PUB-7305 | Amends an earlier circular. MIA-C-2026-16, published 24 Nov 2026. | Amends paragraph 3 of MIA-C-2026-09: the decision on a claim within 15 working days in place of 20, from 1 Jan 2027 (36 days). Paragraphs 2 and 4 are unchanged. | Bears on OBL-03 only, owner Araminta Feldspar, Head of Claims; related publication PUB-7291. OBL-04 is not touched. |
| PUB-7306 | A duplicate under a new reference. MDPO-N-2026-19, published 20 Nov 2026. | Republishes Guidance MDPO-G-2026-04 under a new reference. The text is unchanged. | Duplicate of PUB-7292. OBL-09 stands as it is; nothing new. |
| PUB-7307 | The register is silent. MIA-C-2026-17, published 25 Nov 2026. | From 1 Apr 2027 (126 days) an insurer that uses an automated tool to price or to accept or refuse a risk keeps a list of the tools, tests each one yearly and names a senior person. All classes of business. | No matching obligation: it applies, and no obligation of the register covers it. The compliance officer decides whether a new one is needed. |
| PUB-7308 | A circular for one line the insurer writes. MIA-C-2026-13, published 19 Nov 2026. | Group medical: pre-authorisation answered within 2 working days from 1 Feb 2027 (67 days); until then 5. | Bears on OBL-08, owner Cordelia Brightwater, Head of Health Claims. |

`save_regulatory_impact_note` is refused with 409, and nothing is saved, when an obligation named is not in the register, when the related publication is not another item of the feed, when the finding is `bears_on_an_obligation` and no obligation is named, when the finding is `does_not_apply` or `no_matching_obligation` and obligations are named, or when a duplicate names no earlier publication. The saved draft carries the owners from the register and the dates worked out by the system.

### Document categories and the privilege guide

`get_litigation_document_guide` gives both. A document is sorted by what it is and who it is from and to, not by what it quotes. A copy takes the category, the flag and the rule of the original, and the row names the original (PG-7).

| Category | Covers |
|---|---|
| DC-1 | Court documents and documents made for the proceedings: claim forms, defences, witness statements, drafts of these, letters before action. |
| DC-2 | Correspondence with the policyholder or the claimant: claim forms, accident reports, letters, decline letters, complaints. |
| DC-3 | Internal notes and internal emails. An internal note that passes on legal advice is DC-5. |
| DC-4 | Expert reports: engineers, surveyors, doctors. |
| DC-5 | Legal advice: a request to Thornmere's lawyers, their advice, and an internal note that passes it on. |
| DC-6 | Correspondence with third parties: brokers, repairers, reinsurers, witnesses. |
| DC-7 | Policy documents. |

| Rule | Flag | Says |
|---|---|---|
| PG-1 | yes | Thornmere asks its lawyer for legal advice, or the lawyer gives it, or an internal note passes it on. |
| PG-2 | yes | Made mainly for proceedings that have started or are expected: a draft marked as prepared for litigation, a draft witness statement or defence, an expert report asked for by Thornmere's lawyers for the proceedings. |
| PG-3 | no | A lawyer is only copied on an ordinary business email that neither asks for nor gives legal advice. |
| PG-4 | unclear | Legal advice sent, forwarded or quoted to anybody outside Thornmere other than its own lawyers. For the lawyer. Comes before PG-1. |
| PG-5 | no | The ordinary course of the claim: letters to and from the policyholder, the claimant or their lawyers, the adjuster's notes, a report asked for by the claims team to decide the claim, policy documents, documents filed at court or served by the other side. |
| PG-6 | unclear | May record legal advice but does not say who gave it, or has no author or date so its purpose cannot be told. For the lawyer. |
| PG-7 | as the original | A copy of a document already in the set. |

Thornmere's lawyers: Emeric Thornbury, in-house counsel, and Lucasta Pargeter of Pargeter Voss Legal. The flag says only that a document may be privileged. The lawyers decide.

### Disputed claims

`get_disputed_claim` gives the people in the matter with their side, and every document as text with its date, author, recipients, `recipients_outside_thornmere_and_its_lawyers` and `identical_text_to`. The right schedule (`save_document_schedule`) has one row for each document.

**DSP-7401**, Hollowmere Cold Stores Ltd, claim DCL-7451, commercial property, USD 186,000.00 in dispute. A letter before action is received; proceedings are expected. 11 documents: 3 yes, 7 no, 1 unclear.

| Document | What it is | Date | Author | Category | May be privileged |
|---|---|---|---|---|---|
| DSP-7401-D01 | Notice of the loss from the policyholder | 29 Jul 2026 | Barnabas Hollowmere | DC-2 | no, PG-5 |
| DSP-7401-D02 | Adjuster's note of the site visit | 5 Aug 2026 | Wilfred Ackerley | DC-3 | no, PG-5 |
| DSP-7401-D03 | Engineer's report, asked for by the adjuster to help decide the claim | 18 Aug 2026 | Ignatius Calderbrook | DC-4 | no, PG-5 |
| DSP-7401-D04 | Letter declining the claim | 28 Aug 2026 | Griselda Hoxton | DC-2 | no, PG-5 |
| DSP-7401-D05 | Letter before action from the policyholder's lawyers | 17 Oct 2026 | Perpetua Quillon | DC-1 | no, PG-5 |
| DSP-7401-D06 | Email asking the external lawyer for advice | 19 Oct 2026 | Griselda Hoxton | DC-5 | yes, PG-1 |
| DSP-7401-D07 | Note of advice from the external lawyer | 24 Oct 2026 | Lucasta Pargeter | DC-5 | yes, PG-1 |
| DSP-7401-D08 | Email to the broker, Imelda Roe, that quotes the lawyers' advice in full | 26 Oct 2026 | Griselda Hoxton | DC-6 | unclear, PG-4: it looks privileged, but the advice went to a third party. For the lawyer. |
| DSP-7401-D09 | Draft witness statement, marked "DRAFT. Prepared for litigation." | 14 Nov 2026 | Lucasta Pargeter | DC-1 | yes, PG-2 |
| DSP-7401-D10 | Copy of the engineer's report: a duplicate of DSP-7401-D03 | 18 Aug 2026 | Ignatius Calderbrook | DC-4 | no, PG-5, as the original |
| DSP-7401-D11 | Email to finance about the reserve, in-house counsel only copied | 21 Oct 2026 | Griselda Hoxton | DC-3 | no, PG-3 |

**DSP-7402**, Ferelith Dunmore and Alaric Penhale (the policyholder), claim DCL-7452, private motor, USD 74,500.00 in dispute. Proceedings were issued in the Port Ilvane District Court on 13 Oct 2026, case PIDC-2026-0871. 9 documents: 3 yes, 6 no.

| Document | What it is | Date | Author | Category | May be privileged |
|---|---|---|---|---|---|
| DSP-7402-D01 | Letter of claim from the other driver | 19 Jun 2026 | Ferelith Dunmore | DC-2 | no, PG-5 |
| DSP-7402-D02 | Accident report form from the policyholder | 9 Jun 2026 | Alaric Penhale | DC-2 | no, PG-5 |
| DSP-7402-D03 | File note of a call with the witness | 29 Jun 2026 | Matthias Orlop | DC-3 | no, PG-5 |
| DSP-7402-D04 | Claim form issued at court by the claimant's lawyers | 13 Oct 2026 | Dorothea Kite | DC-1 | no, PG-5 |
| DSP-7402-D05 | In-house counsel's advice on liability | 17 Oct 2026 | Emeric Thornbury | DC-5 | yes, PG-1 |
| DSP-7402-D06 | Internal email that passes counsel's advice on | 18 Oct 2026 | Matthias Orlop | DC-5 | yes, PG-1 |
| DSP-7402-D07 | Medical report, asked for by in-house counsel for the proceedings | 6 Nov 2026 | Hesketh Vane | DC-4 | yes, PG-2 |
| DSP-7402-D08 | Email to the repairer about an invoice of USD 3,240.00, in-house counsel only copied | 9 Jul 2026 | Matthias Orlop | DC-6 | no, PG-3 |
| DSP-7402-D09 | Second scan of the letter of claim: a duplicate of DSP-7402-D01 | 19 Jun 2026 | Ferelith Dunmore | DC-2 | no, PG-5, as the original |

**DSP-7403**, Thaddea Wolstencroft, claim DCL-7453, home, USD 58,200.00 in dispute. The policyholder has complained; proceedings are expected. 8 documents: 2 yes, 5 no, 1 unclear.

| Document | What it is | Date | Author | Category | May be privileged |
|---|---|---|---|---|---|
| DSP-7403-D01 | Policy schedule | 22 Oct 2025 | Thornmere Mutual Insurance, policy administration | DC-7 | no, PG-5 |
| DSP-7403-D02 | Claim form | 9 Jul 2026 | Thaddea Wolstencroft | DC-2 | no, PG-5 |
| DSP-7403-D03 | Surveyor's report, asked for by the adjuster to help decide the claim | 31 Jul 2026 | Fennimore Drake | DC-4 | no, PG-5 |
| DSP-7403-D04 | Letter declining the claim | 13 Aug 2026 | Griselda Hoxton | DC-2 | no, PG-5 |
| DSP-7403-D05 | Letter of complaint | 23 Aug 2026 | Thaddea Wolstencroft | DC-2 | no, PG-5 |
| DSP-7403-D06 | Advice from the external lawyers | 27 Sep 2026 | Lucasta Pargeter | DC-5 | yes, PG-1 |
| DSP-7403-D07 | A note with no date and no name: "Spoke to L. about the start date point." | none | none | DC-3 | unclear, PG-6: it may record legal advice and does not say who gave it. The row leaves the date and the author empty. |
| DSP-7403-D08 | Draft defence, marked "DRAFT. Prepared for litigation. Not filed." | 17 Nov 2026 | Lucasta Pargeter | DC-1 | yes, PG-2 |

The same kind of report has two answers: an engineer's or surveyor's report asked for by the claims team to decide the claim is PG-5 (DSP-7401-D03, DSP-7403-D03), and a medical report asked for by the lawyers for the proceedings is PG-2 (DSP-7402-D07).

`save_document_schedule` is refused with 409, and nothing is saved, when a row names a document that is not in the set or names one twice, when a document of the set has no row (the refusal names each one), when a category is not one of DC-1 to DC-7, when a rule is not one of PG-1 to PG-7, or when `duplicate_of` is not another document of the set. The saved draft carries the system's own counts.

## Reinsurance and partners (system: reinsurance)

Two binders (BND-8601, BND-8602) and two treaties (TRY-8651, TRY-8652) with numbered terms; four bordereaux for 1 Oct 2026 to 31 Oct 2026 (BDX-8701 to BDX-8704); eleven paid claims (RCL-8801 to RCL-8811), one event (EVT-8891) and two recoveries already raised (RCV-8851, RCV-8852); eight partners (PTN-8901 to PTN-8908) with service levels SL-1 to SL-4, the credentials term SL-5 and credentials (PTN-8901-C1 and so on).

Every coverholder, reinsurer, administrator, repairer, supplier and insured is invented.

The system does every sum, share and day count and returns its working. Every save is a draft with a version number, and changes nothing else: there is no change operation. No operation books a recovery, pays, rejects a bordereau, ends a contract, or contacts a reinsurer, a coverholder or a supplier. A read never returns saved drafts: it gives `drafts_on_file` (or `recovery_list_drafts_on_file`), and `list_bordereau_difference_drafts`, `list_recovery_list_drafts` and `list_partner_review_drafts` read them. Results name a role (the reinsurance accountant, the supplier manager), never a member of staff. Every code has a plain label beside it.

### Binders and treaties

`list_binders_and_treaties` gives all four whole. `get_binder_or_treaty` gives one. A term of the kind measured turns on a figure or a date and the system measures it. A term of the kind for_reading is read against the words of a row.

| Contract | Other side | Period | Terms |
|---|---|---|---|
| BND-8601 Household binder | Pellowmere Cover Agency, coverholder | 1 Jan 2026 to 31 Dec 2026 | 1 classes HH (household) and LL (let property). 2 territory Meridia. 3 maximum line USD 750,000.00 per risk, exactly on it is within. 4 period, by the start date of the risk. 5 commission 25.00 percent of the gross premium. 6 net premium due within 45 days after the month ends. 7 excluded risks, for reading: a thatched roof; unoccupied more than 60 days in a row; a house in multiple occupation; under construction or major renovation. 8 claims authority USD 10,000.00, more needs an agreement reference on the row. 9 each risk and claim declared once, rows and totals add up. |
| BND-8602 Pleasure craft binder | Quillfeather Marine Agency, coverholder | 1 Apr 2026 to 31 Mar 2027 | 1 classes PC (pleasure craft up to 12 metres) and DG (dinghies). 2 territory Meridia. 3 maximum line USD 250,000.00. 4 period. 5 commission 20.00 percent. 6 net premium due within 30 days. 7 excluded risks, for reading: racing; hire or charter; a maximum speed above 35 knots; a houseboat used as a permanent home. 8 claims authority USD 5,000.00. 9 declared once, totals add up. |
| TRY-8651 Commercial property excess of loss, per risk | Greyfell Reinsurance Company, reinsurer | 1 Jan 2026 to 31 Dec 2026, by the date of loss | 1 class CP (commercial property). 2 territory Meridia. 3 period: the date of loss decides. 4 attachment point USD 250,000.00: only the part above it is recovered, a paid loss exactly on it recovers nothing. 5 limit USD 750,000.00 above the attachment point; the part above USD 1,000,000.00 stays with the insurer. 6 one event: claims that carry one event id are added together and treated as one loss, and the attachment point and limit apply once to the sum. 7 reinstatement: for each recovery a premium of the recovery divided by the limit, times the annual premium of USD 180,000.00. 8 raising a recovery, for reading. |
| TRY-8652 Engineering quota share | Windlecombe Re, reinsurer | 1 Jan 2026 to 31 Dec 2026 | 1 class EN (engineering). 2 territory Meridia. 3 cession 40.00 percent of sum insured and premium, ceded sum insured at most USD 2,000,000.00 per risk, exactly on it is within. 4 period. 5 ceding commission 30.00 percent of the ceded premium. 6 net ceded premium due within 45 days. 7 excluded risks, for reading: plant at sea; plant underground in a mine; prototype machinery; machinery installed more than 25 years before the start. 8 the reinsurer pays 40.00 percent of every paid loss, in the quarterly account, or at once by a cash call where the paid loss is USD 100,000.00 or more. 9 declared once, totals add up. |

### Bordereaux (Bordereaux Check)

`get_bordereau` gives the rows, the binder or treaty whole and `measured`. `measure_bordereau_against_terms` gives the measure alone. The system measures every row against the numeric and dated terms, re-adds every total and finds a row declared twice. It does not read the description of a risk: the excluded risks (term 7) are read by the agent.

The right draft (`save_bordereau_differences`) gives `overall`, one entry for each difference with the row number, the kind, the term and a note, and a summary. Row 0 is the totals.

| Bordereau | For | Right answer |
|---|---|---|
| BDX-8701 | Risks bound, BND-8601, 12 rows. Faults in three rows, and one row exactly on the line. | Three differences. Row 5 (PCA-10435): sum insured USD 825,000.00, USD 75,000.00 over the maximum line (term 3). Row 7 (PCA-10437): the risk is at Lake Sorrin, Veldmark, outside the territory (term 2). Row 8 (PCA-10438): "Cottage with a thatched roof", an excluded risk (term 7); the system does not measure this one, the agent reads it. Row 3 (PCA-10433) is exactly on USD 750,000.00 and is within: it must not be listed. Rows 4, 9 and 12 are let to one family or one tenant, which is not multiple occupation. Totals add up: gross premium USD 11,190.00, commission USD 2,797.50, net premium USD 8,392.50. Net premium due 15 Dec 2026, 19 days left, not late. |
| BDX-8702 | Risks bound, BND-8602, 10 rows. | Three differences. Row 5 (QMA-5505): commission of USD 270.00 taken on USD 1,200.00, which is 22.50 percent; at 20.00 percent it is USD 240.00, so USD 30.00 too much (term 5). Row 7 (QMA-5507): start date 28 Mar 2026, 4 days before the period starts (term 4). Row 9 repeats row 4 (QMA-5504): declared twice (term 9). The stated totals are the sum of the rows as sent: gross premium USD 8,510.00, commission USD 1,732.00, net premium USD 6,778.00. At the rate of the term the commission is USD 1,702.00. Without row 9 the net premium is USD 6,442.00. No description is an excluded risk: the two motor cruisers give 22 and 28 knots, under 35. Net premium due 30 Nov 2026, 4 days left. |
| BDX-8703 | Claims paid, BND-8601, 9 rows. | One difference, in a row and in the total. Row 5 (PCA-C-2205): indemnity USD 3,400.00 plus fees USD 250.00 is USD 3,650.00 and the row states USD 3,850.00, USD 200.00 too high (term 9). The total stated is USD 48,800.00 and the system re-adds USD 48,600.00 from the indemnity (USD 45,040.00) and the fees (USD 3,560.00): a difference of USD 200.00. Two rows must not be listed: row 4 is exactly on the claims authority of USD 10,000.00, and row 7 is USD 23,400.00 with the agreement reference TMI-AGR-0417 on the row (term 8). |
| BDX-8704 | Cessions under TRY-8652, 8 rows. The clean one. | No differences: `overall` is `no_differences` and the list is empty. Row 5 (TMI-EN-0305) cedes USD 2,000,000.00, exactly on the maximum line, and is within. Totals add up: ceded sum insured USD 7,200,000.00, ceded premium USD 34,160.00, ceding commission USD 10,248.00, net ceded premium USD 23,912.00. No description is an excluded risk. The system measures the age of the machinery (check `machinery_age`, term 7, limit 25 years) from the year of installation on each row: the oldest is row 5, installed 2012, 14 years, within. |

`save_bordereau_differences` is refused with 409, and nothing is saved, when a row number is not a row of the bordereau, when a term is not a term of the binder or treaty, when `overall` is `no_differences` and differences are listed, or when it is `differences_found` and none is listed. `suggested_step` is optional: an empty text or "none" is read as no value. The saved draft carries the system's own measured differences.

### Paid claims and recoveries (Treaty Recovery)

`list_paid_claims_for_recovery` lists the paid claims with a payment in a period (by default 1 Jan 2026 to the insurer date), each with the recovery worked out, and adds what is to raise. `calculate_treaty_recovery` works out one claim under each treaty with the working. `get_paid_claim` gives one claim whole. `list_recoveries_raised` gives RCV-8851 (USD 300,000.00 on RCL-8804, raised 11 Sep 2026 when the paid loss stood at USD 550,000.00) and RCV-8852 (a cash call of USD 60,000.00 on RCL-8811, raised 16 Sep 2026).

Claims RCL-8801 to RCL-8809 are commercial property and fall under TRY-8651; TRY-8652 does not apply to them. RCL-8810 and RCL-8811 are engineering and fall under TRY-8652.

| Claim | For | Facts | Right answer |
|---|---|---|---|
| RCL-8801 | Below the attachment point. | Paid USD 90,000.00. Loss 14 Feb 2026. | Nothing due: USD 160,000.00 below the attachment point. |
| RCL-8802 | Below the attachment point, close to it. | Paid USD 150,000.00 and USD 90,000.00: USD 240,000.00. Loss 9 Mar 2026. | Nothing due: USD 10,000.00 below the attachment point. |
| RCL-8803 | Above, no recovery raised. | Paid USD 250,000.00 and USD 160,000.00: USD 410,000.00. Loss 22 Apr 2026. | Recovery to raise: USD 160,000.00 (term 4). Reinstatement premium USD 38,400.00. |
| RCL-8804 | Above, a recovery raised for too little. | Paid USD 300,000.00, USD 250,000.00 and, on 3 Nov 2026, USD 50,000.00: USD 600,000.00. RCV-8851 raised USD 300,000.00 before the last payment. | Recoverable USD 350,000.00, raised USD 300,000.00: USD 50,000.00 more to raise. Reinstatement premium USD 84,000.00 on the whole recovery, USD 12,000.00 on the part still to raise. |
| RCL-8805 | Exactly on the attachment point. | Paid USD 250,000.00. Loss 19 Jun 2026. | Nothing due: only the part above the attachment point is recovered and there is none. The rule does not fire. |
| RCL-8806 | Above the limit. | Paid USD 500,000.00 and USD 650,000.00: USD 1,150,000.00. Loss 2 Jul 2026. | USD 900,000.00 is above the attachment point; the recovery is capped at USD 750,000.00 (term 5) and USD 150,000.00 stays with the insurer. Recovery to raise: USD 750,000.00. Reinstatement premium USD 180,000.00. |
| RCL-8807 | Date of loss outside the treaty period. | Paid USD 380,000.00 on 16 Mar 2026. Loss 29 Dec 2025. | Outside the treaty period: 3 days before the period starts (term 3). Nothing is recovered under TRY-8651, amount USD 0.00. Needs a person: the treaty of the earlier year is not held in this system. |
| RCL-8808 and RCL-8809 | Two claims from one event, EVT-8891, the fire at Cinder Quay on 17 Aug 2026. | Paid USD 180,000.00 and USD 120,000.00. Each alone is below the attachment point. | Term 6 adds them: USD 300,000.00, which is USD 50,000.00 above the attachment point. Recovery to raise for the event: USD 50,000.00, of which USD 30,000.00 on RCL-8808 and USD 20,000.00 on RCL-8809. Reinstatement premium USD 12,000.00. |
| RCL-8810 | Quota share, below the cash call threshold. | Engineering. Paid USD 80,000.00. | The reinsurer's share is USD 32,000.00, collected in the quarterly account. No cash call: nothing to raise now. |
| RCL-8811 | Quota share, cash call raised in full. | Engineering. Paid USD 150,000.00. RCV-8852 raised USD 60,000.00. | The reinsurer's share is USD 60,000.00 and USD 60,000.00 is raised: nothing more to raise. |

For the whole period the system counts 11 claims, 5 with something to raise (RCL-8803, RCL-8804, RCL-8806, RCL-8808, RCL-8809) and USD 1,010,000.00 to raise in all; RCL-8807 needs a person. For payments from 1 Oct 2026 to 31 Oct 2026 the list holds RCL-8806, RCL-8808 and RCL-8809, with USD 800,000.00 to raise.

The right draft (`save_recovery_list`) has six rows: RCL-8803 `recovery_to_raise` USD 160,000.00; RCL-8804 `recovery_raised_for_too_little` USD 50,000.00; RCL-8806 `recovery_to_raise` USD 750,000.00; RCL-8807 `needs_a_person` USD 0.00; RCL-8808 `recovery_to_raise` USD 30,000.00 and RCL-8809 `recovery_to_raise` USD 20,000.00, both with EVT-8891. The claims with nothing due are RCL-8801, RCL-8802, RCL-8805, RCL-8810 and RCL-8811. The saved draft carries the system's own figure beside each row and says which rows do not agree with it.

`save_recovery_list` is refused with 409, and nothing is saved, when a claim is not a paid claim of this system, when a treaty is not one of the two treaties, when the same claim and treaty are given twice, or when a claim is both in a row and among the claims with nothing due. Drafts are kept on RLIST-8800.

### Partners (Partner Quality)

`list_partners` gives every partner whole with its measure. `get_partner` gives one. `measure_partner_against_service_levels` gives the measure alone, on the insurer date, for the month 1 Oct 2026 to 31 Oct 2026.

SL-1 is the average turnaround in days, SL-2 the complaint rate (complaints per 100 jobs), SL-3 the re-repair rate (repair networks only), SL-4 the monthly report within 10 days after the month ends (due 10 Nov 2026), SL-5 the credentials. A figure exactly on a limit meets it. A figure that was not reported gives `cannot_tell`: nothing is assumed. A credential is valid up to and including its expiry date; one that expires within 30 days is a warning, not a miss.

| Partner | For | Facts | Right answer |
|---|---|---|---|
| PTN-8901 Brackenhall Claims Administration, administrator | Fully within. | Turnaround 4.1 days of 5.0. 8 complaints on 640 jobs: 1.25 percent of 2.00. Report received 6 Nov 2026. Credentials valid for 216 and 125 days. | `within`. Nothing to report. |
| PTN-8902 Ilvane Bodyworks Network, repair network | Fully within. | Turnaround 7.2 days of 8.0. 6 complaints on 300 jobs: 2.00 percent of 3.00. 9 re-repairs: 3.00 percent of 4.00. Report received 9 Nov 2026. Credentials valid for 308 and 94 days. | `within`. Nothing to report. |
| PTN-8903 Marlow Reach Glass and Glazing, supplier | A missed turnaround. | Turnaround 4.2 days against 3.0. 3 complaints on 250 jobs: 1.20 percent of 2.00. Report received 5 Nov 2026. | `not_met`: SL-1, 1.2 days over. Everything else met. |
| PTN-8904 Tallowby Motor Repairers, repair network | An expired credential. | Every service level met (6.5 days of 8.0; 1.25 percent of 3.00; 2.50 percent of 4.00; report 4 Nov 2026). The accreditation PTN-8904-C2 expired on 14 Nov 2026. | `not_met`: PTN-8904-C2 expired 12 days before the insurer date (SL-5). |
| PTN-8905 Copperlow Hire Cars, supplier | A credential inside the notice window. | Every service level met (1.4 days of 2.0; 2.00 percent of 2.50; report 7 Nov 2026). The insurance certificate PTN-8905-C2 expires on 15 Dec 2026. | `warning`: PTN-8905-C2 expires in 19 days, inside the window of 30. A warning, not a miss. |
| PTN-8906 Fernside Loss Adjusters, supplier | Exactly on a service level. | 4 complaints on 200 jobs: 2.00 percent against a limit of 2.00. Turnaround 8.6 days of 10.0. Report received 5 Nov 2026. | `within`: SL-2 is exactly on the limit and is met. The rule does not fire. |
| PTN-8907 Quarrymead Medical Claims Administrators, administrator | A figure missing. | 510 jobs, turnaround 4.6 days of 5.0, report received 9 Nov 2026. The report's line for complaints is empty. | `cannot_tell`: SL-2 cannot be worked out. Needs a person, who gets the figure. Nothing is assumed and nothing is called a miss. |
| PTN-8908 Saltmarsh Roofing and Building Repairs, repair network | Two service levels not met. | 6 re-repairs on 80 jobs: 7.50 percent against 5.00. Report received 17 Nov 2026. Turnaround 10.5 days of 12.0; 2 complaints: 2.50 percent of 3.00. | `not_met`: SL-3, 2.50 over; and SL-4, 17 days after the month ended, 7 days late. |

The right draft (`save_partner_review`) gives `overall`, a finding for each item that is not met, a warning or cannot be told, whether a person is needed, and a summary. `suggested_step` is optional: an empty text or "none" is read as no value.

`save_partner_review` is refused with 409, and nothing is saved, when an item is not a service level or a credential of that partner, or when an item is given twice. The saved draft carries the system's own measure.

## Portfolio (system: portfolio)

Three chat agents for the insurer's own staff read this system: Product Change Analyst, Pricing Analyst and Risk Profiling. It holds a product catalogue of four products (PRD-8301 to PRD-8304) with 29 dependent items (DEP-8401 to DEP-8437, not every number used) and six proposed changes (PCR-8501 to PCR-8506); a pricing method of eight rules (PM-1 to PM-8) with the experience of six segments (SEG-8601 to SEG-8606); and an exposure warehouse of 39 rows with six concentration limits (LIM-1 to LIM-6).

The system does every sum, ratio and comparison and returns its working. No operation changes a product, a rate, a limit or a policy. The one save, `save_portfolio_question_for_a_person`, stores a question for a person as a draft note (QN-8901 onwards) and changes nothing else. A read never returns a saved question: `get_proposed_product_change` gives `questions_on_file`, and `list_portfolio_questions_for_a_person` reads them.

Every person, document reference and filing is invented, as is the regulator, the Meridia Insurance Authority.

### Product catalogue

`list_catalogue_products` lists the products. `get_product` gives one product whole: the wording by section and clause, the rating factors, and every dependent item with its references. `get_what_refers_to` is the dependency read for one clause (SEC-8303-4.1), one section as a whole (SEC-8303-4) or one rating factor (FAC-8303-5). `search_product_catalogue` finds clauses, factors and items by any word.

| Product | Wording | Dependent items |
|---|---|---|
| PRD-8301 Private motor | TMI-MOT-01, as the policy system holds it | DEP-8401 schedule template, DEP-8402 rating table, DEP-8403 claims checklists, DEP-8404 broker guide, DEP-8405 filing (sections 1 to 4 and the rates), DEP-8406 quote screen |
| PRD-8302 Home | TMI-HOM-02, as the policy system holds it | DEP-8411 schedule template, DEP-8412 rating table, DEP-8413 claims checklists, DEP-8414 broker guide, DEP-8415 filing (sections 1 to 4 and the rates), DEP-8416 note of the household catastrophe treaty |
| PRD-8303 Commercial property | TMI-COM-03, held in the catalogue only | DEP-8421 schedule template, DEP-8422 rating table, DEP-8423 claims checklist, DEP-8424 broker guide, DEP-8425 filing (sections 1 to 4; rates are not filed), DEP-8426 note of the quota share treaty, and the underwriting guidelines UG-6 (DEP-8427), UG-5 (DEP-8428), UG-3 (DEP-8429) and UG-1 (DEP-8430) |
| PRD-8304 Group medical, Thornmere Health Complete | the table of benefits, as the health system holds it | DEP-8431 member guide, DEP-8432 rating table, DEP-8433 claims engine waiting period rule, DEP-8434 certificate template, DEP-8435 filing (the whole table and the rates), DEP-8436 pre-authorisation form and medical policies, DEP-8437 provider contracts and tariffs |

A reference has one relation: `quotes`, `uses`, `relies_on`, `lists` or `is_filed`. A reference to a section as a whole applies on any change to a clause of it (a filing) or only when a clause is added or removed (a guide or checklist that lists the clauses). Section 5 of a wording, the conditions, is in no filing. A change to a filed section is notified to the Meridia Insurance Authority at least 30 days before it has effect.

The catalogue never holds the rates, the text of a filing or of a treaty, policies or customers, or a decision. A question that needs one of these is an open question for the owner the system names.

### Proposed product changes

`list_proposed_product_changes` lists them. `get_proposed_product_change` gives one change with `impact`: the items touched with the references that make it so, the items not touched, the items that quote the current figure, the items that rely on what is changed, and `what_the_catalogue_cannot_say`. The right answer names every item touched by id, says what is not touched, raises each item that relies on the clause as a conflict, and gives the questions the catalogue cannot answer as open questions without answering them. It approves nothing.

| Change | For | Facts | Right answer |
|---|---|---|---|
| PCR-8501 | Raise a deductible. Lavinia Thrupp, commercial lines, received 20 Nov 2026. | The lowest commercial property deductible from USD 2,500 to USD 5,000: clause SEC-8303-4.1 and the factor FAC-8303-5. | Touches the wording and 5 items: DEP-8421, DEP-8422, DEP-8424, DEP-8425 and DEP-8427 (underwriting guideline UG-6, which gives the same USD 2,500). 4 quote the current figure 2,500: DEP-8421, DEP-8422, DEP-8424, DEP-8427. The filing DEP-8425 needs 30 days' notice. Nothing relies on it. Not touched: DEP-8423, DEP-8426, DEP-8428, DEP-8429, DEP-8430. One open question, from DEP-8422: the rates at other levels of the factor. |
| PCR-8502 | Add a peril. Ottilie Farnaby, personal lines, received 21 Nov 2026. | Add accidental breakage of fixed glass to section 1 of the home wording (SEC-8302-1). | Touches the wording and 5 items: DEP-8412, DEP-8413, DEP-8414, DEP-8415, DEP-8416. Not touched: DEP-8411. Nothing in the home part of the catalogue names glass; it is named for private motor only (SEC-8301-1.4, SEC-8301-3.2), which says nothing about home. Four open questions: the rate for a new peril (DEP-8412), the documents a claim would need (DEP-8413), whether the treaty would protect it (DEP-8416), and what is charged, since no rating factor names it. |
| PCR-8503 | Remove an exclusion a treaty relies on. Lavinia Thrupp, received 22 Nov 2026. | Take the flood exclusion, clause SEC-8303-2.1, out of the commercial property wording. | Touches the wording and 6 items: DEP-8422, DEP-8423, DEP-8424, DEP-8425, DEP-8426, DEP-8428. 3 rely on the exclusion staying: the rating table DEP-8422 (no loading for flood), the claims checklist DEP-8423, and the quota share treaty DEP-8426, which protects the account on the footing that flood is excluded. That is the conflict to raise, with Marguerite Tolland, reinsurance manager. Three open questions: a rate for flood (none exists), whether the reinsurers would agree, and whether flood zones 1 and 2 stay within UG-5. |
| PCR-8504 | Change a waiting period in the health plan. Ignatia Culpepper, health, received 23 Nov 2026. | Maternity care, benefit SEC-8304-BEN-F08, from 300 days of cover to 180. | Touches the table of benefits and 5 items: DEP-8431, DEP-8432, DEP-8433, DEP-8434, DEP-8435. 4 quote 300 days: DEP-8431, DEP-8432, DEP-8433, DEP-8434. The rating table DEP-8432 relies on it: the maternity rate assumes 300 days. Not touched: DEP-8436, DEP-8437. One open question: the maternity rate at another waiting period. How many members are inside the waiting period is not in the catalogue: the health system holds members. |
| PCR-8505 | A change that touches nothing else. Lavinia Thrupp, received 24 Nov 2026. | Reword the governing law clause, SEC-8303-5.3, with no change of meaning. | PCR-8505 touches the wording TMI-COM-03 itself and nothing else: no item refers to the clause, and section 5 is in no filing. No open question. The right answer says so plainly and invents no impact. |
| PCR-8506 | The effect on filed rates cannot be said. Ottilie Farnaby, received 25 Nov 2026. | Move the young driver age line of private motor, factor FAC-8301-1, from 25 to 23. She asks what this does to the filed rates. | Touches 4 items: DEP-8402, DEP-8404, DEP-8405, DEP-8406. 3 quote 25: DEP-8402, DEP-8404, DEP-8406 (the quote screen has the bands fixed in it). The catalogue cannot say whether the filed rates must be filed again or what the change does to them: it holds the reference of DEP-8405, not the rates. It cannot say the rates at other levels (DEP-8402). Clause SEC-8301-4.2 uses the same age of 25 for the further deductible and the proposal does not name it: whether it changes too is a question for the proposer; DEP-8403 and DEP-8404 refer to that clause. Not touched: DEP-8401, DEP-8403. |

### Pricing method and segments

`get_pricing_method` gives the rules and the default assumptions. `list_pricing_segments` gives every segment with its experience. `get_segment_experience` gives the loss ratios of one segment, `check_segment_credibility` its credibility, and `calculate_premium_change_for_target_loss_ratio` the premium change with every assumption named, the working and a sensitivity table.

PM-1: loss ratio is incurred claims over earned premium. PM-2: complete accident years only: 2023, 2024 and 2025. PM-3: claims are trended to 2027, 3 years when every year is read. PM-4: the target is the one asked for, or 100 less the expense ratio less a profit margin of 5 percent. PM-5: the change needed is the trended loss ratio over the target, less one. PM-6: at or below the target the change is zero; no decrease is worked out. PM-7: credibility is the square root of claims over 1,000, at most 1; under 250 claims a segment is too thin and its figures are not reliable alone; exactly 250 is enough. PM-8: the pricing actuary signs off.

Defaults (claims trend, expense ratio, target when none is given): private motor 5, 25, 70; home 4, 30, 65; commercial property 4, 28, 67; motor fleet 6, 22, 73.

| Segment | Earned premium | Incurred claims | Claims | Loss ratio | Credibility |
|---|---|---|---|---|---|
| SEG-8601 Private motor, drivers aged 25 and over | 13,500,000.00 | 9,200,000.00 | 3,730 | 68.15 | 1.00 |
| SEG-8602 Private motor, drivers under 25 | 1,930,000.00 | 1,710,000.00 | 675 | 88.60 | 0.82 |
| SEG-8603 Home, Port Ilvane, Marlow Reach and Tallowby | 7,500,000.00 | 3,580,000.00 | 1,905 | 47.73 | 1.00 |
| SEG-8604 Home, Saltmarsh Coast | 480,000.00 | 445,000.00 | 46 | 92.71 | 0.21, too thin |
| SEG-8605 Commercial property, all regions | 9,500,000.00 | 6,050,000.00 | 300 | 63.68 | 0.55 |
| SEG-8606 Motor fleet, all regions | 5,700,000.00 | 4,140,000.00 | 250 | 72.63 | 0.50, exactly on the threshold |

The experience is not split by fuel type, vehicle age, postcode, broker or month.

| Question | For | Right answer |
|---|---|---|
| PQ-8701 What is the loss ratio of private motor for drivers of 25 and over? | A plain read. | By year 65.00, 68.00 and 71.04 percent. Together: 9,200,000.00 / 13,500,000.00 = 68.15 percent. |
| PQ-8702 What premium change holds a 70 percent loss ratio for SEG-8601? | The full calculation. | Assumptions: target 70 (given), claims trend 5 and expenses 25 (defaults), margin 5, years 2023 to 2025, rating year 2027, 3 years of trend. Trend factor 1.157625. Trended claims 10,650,150.00, trended loss ratio 78.89 percent. Change needed 12.70 percent; premium needed 15,214,500.00. Reliable: 3,730 claims. Sensitivity: 21.37 at a target of 65 and 5.19 at 75; 6.38 at a trend of 3 and 19.26 at 7. |
| PQ-8703 What premium change does home on the Saltmarsh Coast need? | A thin segment. | Not reliable: 46 claims in the three years, 204 short of the 250 the method needs, credibility 0.21. The figures are shown and marked: loss ratio 92.71 (by year 40.00, 193.75 and 44.12: one storm year), trended 104.28 against the default target of 65, which alone would mean 60.44 percent. That figure is not to be relied on; `premium_change_to_rely_on_percent` is empty. The pricing actuary decides. |
| PQ-8704 Does SEG-8603 need a rate rise to hold 60 percent? | The target is already met. | No change. Loss ratio 47.73; trend factor 1.124864; trended loss ratio 53.69, which is 6.31 points below the target. The change needed is 0.00 percent. The method works out no decrease. |
| PQ-8705 What is the loss ratio of SEG-8601 for 2026 so far? | A number the data cannot support. | Refused with 409: the experience holds the complete years 2023, 2024 and 2025 only, and 2026 is not held. The right answer says so and gives no estimate. The same goes for a split the experience does not hold, such as electric cars. |
| PQ-8706 What premium change does motor fleet need? | Exactly on the credibility threshold. | Reliable: 250 claims, exactly the number needed, credibility 0.50. No target given, so 73 (100 less 22 less 5). Trend 6: factor 1.191016, trended claims 4,930,806.24, trended loss ratio 86.51. Change needed 18.50 percent; premium needed 6,754,529.10. |
| PQ-8707 For drivers under 25, what change holds 65 percent if claims rise 7 percent a year? | The user's own assumptions. | Target 65 and trend 7 are named as given in the question; expenses 25 is the default. Loss ratio 88.60. Trend factor 1.225043, trended claims 2,094,823.53, trended loss ratio 108.54. Change needed 66.98 percent; premium needed 3,222,805.43. Reliable: 675 claims, credibility 0.82. |

`calculate_premium_change_for_target_loss_ratio` is also refused with 409 for a target outside 20 to 100 percent, a trend outside -10 to 25 or an expense ratio outside 0 to 60. Where the target and the expenses together are more than 100 percent it says so.

### Exposure warehouse

`get_exposure_warehouse_guide` says what the warehouse holds: policies in force on 31 Oct 2026, by product (home, commercial_property, private_motor, motor_fleet), region (Port Ilvane, Marlow Reach, Tallowby, Saltmarsh Coast), construction class (A, B, C; property only), vehicle class (car, van, light_truck; motor only) and sum insured band. In all 9,757 policies, a total sum insured of 815,500,000.00 and an annual premium of 13,413,450.00. It does not hold the flood zone, a postcode, the occupancy, the policyholder, the broker or claims.

`run_exposure_query` is the one query: a measure (`policies_in_force`, `total_sum_insured`, `annual_premium`, `average_sum_insured`), up to two fields to group by, and filters from the fixed lists. It returns the rows, the total and `query_in_words`, which the agent shows. It is refused with 409 for a measure, a field or a value the warehouse does not hold.

`get_concentration_limits` gives the limits. `measure_portfolio_against_concentration_limits` measures the warehouse against them. A value exactly on a limit is within it.

| Limit | Says | Measured | Result |
|---|---|---|---|
| LIM-1 | No one region more than 45 percent of the property sum insured (home and commercial property). | Port Ilvane 43.80 | within, 1.20 points of room |
| LIM-2 | Class C no more than 15 percent of the commercial property sum insured. | 20.32 | over by 5.32 points |
| LIM-3 | Property on the Saltmarsh Coast no more than USD 60,000,000. | 60,000,000.00 | within: exactly on the limit |
| LIM-4 | Policies over USD 2,500,000 no more than 25 percent of the commercial property sum insured. | 18.44 | within |
| LIM-5 | Light trucks no more than 30 percent of the motor fleet sum insured. | 29.04 | within |
| LIM-6 | No one product more than 50 percent of the annual premium. | private motor 40.82 | within |

| Question | For | Right answer |
|---|---|---|
| EXQ-8801 How is the commercial property sum insured split by construction class? | A grouped query. | Query shown: "Total sum insured of the policies in force on 31 Oct 2026, where product is commercial_property, grouped by construction_class." A 160,600,000.00 (51.07 percent), B 90,000,000.00 (28.62), C 63,900,000.00 (20.32); total 314,500,000.00. |
| EXQ-8802 How many home policies are in force in Tallowby? | A count with two filters. | 360. Query shown: "Number of policies in force on 31 Oct 2026, where product is home; region is Tallowby, as one figure." |
| EXQ-8803 Is combustible construction within its limit? | Over a limit. | No. LIM-2: class C holds 63,900,000.00 of 314,500,000.00, 20.32 percent against 15.00: over by 5.32 points, 16,725,000.00 above the 47,175,000.00 the limit allows. A fact for the chief risk officer, Evander Pask; the agent declines and cancels nothing. |
| EXQ-8804 How much property do we hold on the Saltmarsh Coast against the limit? | Exactly on a limit. | 60,000,000.00 against a limit of 60,000,000.00 (home 24,000,000.00, commercial property 36,000,000.00). LIM-3 is within: exactly on the limit, with no room left. It is not over. |
| EXQ-8805 How much sum insured do we have in flood zone 3? | A field the warehouse does not hold. | It cannot be answered: the warehouse does not hold the flood zone. `run_exposure_query` refuses with 409 and names the fields it holds. The right answer says so and estimates nothing. |
| EXQ-8806 What is our property exposure in Marlow Reach? | Two reasonable readings. | The answer states the reading it took. Home and commercial property together: 181,900,000.00 (home 93,300,000.00, commercial property 88,600,000.00; 524 policies). Commercial property alone: 88,600,000.00. Either is right when the reading is stated; the best answer gives both. `product=property` is refused with the two readings named. |
| EXQ-8807 Which region holds the most property, and is that within the limit? | Within a limit, with the working. | Port Ilvane: 275,800,000.00 of 629,700,000.00, 43.80 percent against 45.00. LIM-1 is within, with 1.20 points of room, 7,565,000.00. Marlow Reach 28.89, Tallowby 17.79, Saltmarsh Coast 9.53. |
| EXQ-8808 How many class C commercial property policies have a sum insured over USD 2,500,000? | Zero is an answer. | None. The query runs and no row matches: "The answer is zero". This is not the same as EXQ-8805: the warehouse holds these fields and holds no such policy. |

`save_portfolio_question_for_a_person` is refused with 409, and nothing is saved, when `about` names an id this system does not hold.

## Rules for checking

- A draft keeps every version and changes no status.
- A change (`register_claim`, `record_claim_decision`, `send_claim_letter`, `record_claim_payment`, `decide_pre_authorisation`, `decide_medical_claim`, `record_invoice_query`) needs a named person and is refused with 409 when a precondition fails.
- A saved draft is not part of a record's read. The read only counts the drafts, and a separate operation lists them.
- No text in the data says "yesterday" or names a weekday: every date is written as a date.
- `POST /admin/reset` returns all of this to the start. `POST /admin/reset/<system>` returns only what that one system has changed.

## Simulated arrivals

`POST /admin/simulate/loss-report` makes one new loss report from four rotating templates: (1) a windscreen cracked by a stone, complete; (2) a damp patch with no date of loss, which also points to gradual damage; (3) a car scratched while parked, complete; (4) a leak where the policyholder hurt his wrist: a person injured, refer to a handler.

`POST /admin/simulate/pre-authorisation-request` makes one new pre-authorisation request (PA-8201 onwards) from four rotating templates, requested on the insurer date and planned 10 days later: (1) MEM-7208, an MRI scan of the lumbar spine at PRV-5102, every criterion of MP-301 met: send to the assessor as met; (2) MEM-7202, the same scan at PRV-5101: the fuller plan needs no pre-authorisation, refer to the assessor; (3) MEM-7205, a day-case knee arthroscopy at PRV-5102: the notes hold no MRI report, so criterion 3 of MP-303 is not stated, ask the provider; (4) MEM-7207, removal of a wisdom tooth at PRV-5102: dental treatment is not covered by the plan, refer to the assessor.
