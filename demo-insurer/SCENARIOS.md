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

## Investigations (system: investigations)

Six handling standards (LS-1 to LS-6), eight closed claims for the leakage review (CLM-6101 to CLM-6108), six fraud indicators (FI-1 to FI-6), eight new claims waiting for the fraud check (CLM-6201 to CLM-6208), seven claims referred to the investigations desk (CLM-6301 to CLM-6307), thirteen earlier closed claims (CLM-6011 to CLM-6041), thirty-three parties (PTY-3001 to PTY-3029 people, PTY-3501 to PTY-3513 firms) and three public notices (PN-901 to PN-903). Policies POL-2701 to POL-2727 are held in this system only; five closed claims read POL-2001, POL-2002, POL-2011, POL-2012 and POL-2014 from the policy system. Every phone number is `+999 555 ....`, every bank account `DEMO-ACCT-....`, and every notice is invented.

The system does every sum, count and match. Every save is a draft with a version number, and changes nothing else: there is no change operation. No operation declines a claim, holds a payment, asks for money back or says that a person did wrong. A read never returns saved drafts: it gives `drafts_on_file`, and `list_leakage_finding_drafts`, `list_fraud_referral_drafts` and `list_case_file_drafts` read them.

### Handling standards (leakage review)

`get_claims_handling_standards` gives the rules. `calculate_what_should_have_been_paid` tests one closed claim against all six and gives each a result: `met`, `not_met` or `cannot_tell`.

| Standard | Test |
|---|---|
| LS-1 | The deductible is taken once: the schedule's deductible (clause 4.1), or 500.00 for a home escape of water claim (home clause 4.2). |
| LS-2 | A line the wording limits is paid at the limit. Motor: windscreen 500.00 (3.2), personal belongings 300.00 (3.3), hire car 40.00 a day for up to 10 days (3.4), the vehicle never above the sum insured (3.1). Home: 2,500.00 for an item not listed in the schedule (3.2), trace and access 1,500.00 (3.4). |
| LS-3 | More than 5,000.00 paid in all needs a senior adjuster's approval on the file; more than 25,000.00 the claims manager's (rule HG-5). |
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

## Rules for checking

- A draft keeps every version and changes no status.
- A change (`register_claim`, `record_claim_decision`, `send_claim_letter`, `record_claim_payment`, `decide_pre_authorisation`, `decide_medical_claim`, `record_invoice_query`) needs a named person and is refused with 409 when a precondition fails.
- A saved draft is not part of a record's read. The read only counts the drafts, and a separate operation lists them.
- No text in the data says "yesterday" or names a weekday: every date is written as a date.
- `POST /admin/reset` returns all of this to the start. `POST /admin/reset/<system>` returns only what that one system has changed.

## Simulated arrivals

`POST /admin/simulate/loss-report` makes one new loss report from four rotating templates: (1) a windscreen cracked by a stone, complete; (2) a damp patch with no date of loss, which also points to gradual damage; (3) a car scratched while parked, complete; (4) a leak where the policyholder hurt his wrist: a person injured, refer to a handler.

`POST /admin/simulate/pre-authorisation-request` makes one new pre-authorisation request (PA-8201 onwards) from four rotating templates, requested on the insurer date and planned 10 days later: (1) MEM-7208, an MRI scan of the lumbar spine at PRV-5102, every criterion of MP-301 met: send to the assessor as met; (2) MEM-7202, the same scan at PRV-5101: the fuller plan needs no pre-authorisation, refer to the assessor; (3) MEM-7205, a day-case knee arthroscopy at PRV-5102: the notes hold no MRI report, so criterion 3 of MP-303 is not stated, ask the provider; (4) MEM-7207, removal of a wisdom tooth at PRV-5102: dental treatment is not covered by the plan, refer to the assessor.
