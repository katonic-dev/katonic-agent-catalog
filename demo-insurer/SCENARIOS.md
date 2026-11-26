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

## Rules for checking

- A draft keeps every version and changes no status.
- A change (`register_claim`, `record_claim_decision`, `send_claim_letter`, `record_claim_payment`, `decide_pre_authorisation`, `decide_medical_claim`, `record_invoice_query`) needs a named person and is refused with 409 when a precondition fails.
- A saved draft is not part of a record's read. The read only counts the drafts, and a separate operation lists them.
- No text in the data says "yesterday" or names a weekday: every date is written as a date.
- `POST /admin/reset` returns all of this to the start. `POST /admin/reset/<system>` returns only what that one system has changed.

## Simulated arrivals

`POST /admin/simulate/loss-report` makes one new loss report from four rotating templates: (1) a windscreen cracked by a stone, complete; (2) a damp patch with no date of loss, which also points to gradual damage; (3) a car scratched while parked, complete; (4) a leak where the policyholder hurt his wrist: a person injured, refer to a handler.

`POST /admin/simulate/pre-authorisation-request` makes one new pre-authorisation request (PA-8201 onwards) from four rotating templates, requested on the insurer date and planned 10 days later: (1) MEM-7208, an MRI scan of the lumbar spine at PRV-5102, every criterion of MP-301 met: send to the assessor as met; (2) MEM-7202, the same scan at PRV-5101: the fuller plan needs no pre-authorisation, refer to the assessor; (3) MEM-7205, a day-case knee arthroscopy at PRV-5102: the notes hold no MRI report, so criterion 3 of MP-303 is not stated, ask the provider; (4) MEM-7207, removal of a wisdom tooth at PRV-5102: dental treatment is not covered by the plan, refer to the assessor.
