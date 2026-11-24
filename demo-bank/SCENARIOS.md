# Scenarios and right answers

Meridian Trust Bank is invented, and so is every record here. This file lists each scenario, what it is for, and the right answer. Use it to mark an agent's work.

All dates are relative to the bank date (today, or `BANK_TODAY`). Amounts are USD unless stated.

Country codes are invented: XM Meridia (the bank's home), XA Aldoria, XB Brevnia, XQ Quenmark, XR Rovaland, XT Tessaly, QN Norvania, QP Kharnovia (on the higher-risk list).

## Screening (system: screening)

| Alert | For | Right answer |
|---|---|---|
| SCR-2001 | False positive. Wynne Castellane (CUS-1005) against list entry WL-9001 "Wynn Castellano". | Close as `false_positive`. Date of birth differs (1990-07-21 against 1962-02-02), nationality differs (Meridia against Brevnia), place of birth differs (Marlow Reach, Meridia against Corrowick, Brevnia) and address differs (9 Orchard Gate, Marlow Reach, Meridia against Foundry Lane 40, Corrowick, Brevnia). An earlier alert on the same pair, SCR-1990, was closed as a false positive. |
| SCR-2002 | False positive. Oskar Brindlemoor (CUS-1006) against WL-9002 "Oscar Brindlemore". | Close as `false_positive`. Date of birth differs (1978-11-03 against 1955-05-17), nationality differs (Meridia against Rovaland), place of birth differs (Tallowby, Meridia against Duskmere, Rovaland), address differs (51 Foxglove Walk, Tallowby, Meridia against Saw Lane 22, Duskmere, Rovaland), no identity number matches. |
| SCR-2003 | True match. Valdis Orrenmoor (CUS-1007) against WL-9003. | Close as `true_match` (a person decides). Name, date of birth 1971-09-30, nationality Quenmark and identity number QNP-4417-2290 all agree. Place of birth (Hartsfell, Quenmark) and address (6 Cinder Quay, Port Ilvane, Meridia) agree too, and the address is the one in the press articles ART-6001 and ART-6002. |
| SCR-2004 | Uncertain, birth year only. Katrin Elsdottir-Vance (CUS-1008) against WL-9004 "Katrin Elsdottir". | Do not clear. Recommend `escalate`. The entry has only a birth year (1969) and no nationality or number. The year agrees, the name is partly the same. The entry gives the country of birth only (Tessaly), which agrees with the customer's place of birth (Ambrel, Tessaly) but is not enough to identify anyone, and it has no address. More information is needed. |
| SCR-2005 | Uncertain, spelling variant. Anselm Drozdowich (CUS-1009) against WL-9005 "Anselm Drozdovic". | Do not clear. Recommend `escalate`. The name is a transliteration variant (the entry lists "Anselm Drozdovich" and "A. Drozdowicz" as aliases), date of birth 1980-01-09 and nationality Rovaland agree, the entry has no identity number to confirm. Place of birth also agrees (Duskmere, Rovaland). The entry's address (Fenwick Row 8, Duskmere, Rovaland) differs from the customer's current address in Meridia, which could be a move, so it does not clear the customer. |
| SCR-2006 | Relative of a politically exposed person. Perdita Vanhollow (CUS-1010) against WL-9006 "Leopold Vanhollow". | Recommend `escalate` for enhanced due diligence. The entry is a politically exposed person (Minister of Public Works, Quenmark), not a sanctions entry, and lists the customer as spouse. An earlier alert SCR-1991 was closed as a true match with enhanced due diligence applied. It is not a reason to refuse the customer. The entry's address (2 Larkspur Terrace, Port Ilvane, Meridia) is the customer's own address, as a spouse sharing the home would have. Place of birth differs (Brindlecombe against Hartsfell, Quenmark): she is not the listed person. |

In `get_screening_alert` each comparison row is `match`, `partial` (the entry gives only the country), `differs` or `unknown` (one side has no value). The rows now include `place_of_birth` and `address`. When an agent saves a recommendation with `record_alert_recommendation`, the result of each field comparison row is one of `matches`, `partly_matches`, `differs`, `not_on_entry` or `noted`; any other word is refused with 422. Read-side `match` is written `matches`, `partial` is `partly_matches` and `unknown` is `not_on_entry` when the entry has no value. The recommendation itself stays `clear` or `escalate`.

`screen_name` check: "Valdis Orrenmoor" with date of birth 1971-09-30 and country XQ returns WL-9003 first with score 100.

## Transaction monitoring (system: aml)

| Alert | For | Right answer |
|---|---|---|
| TMA-3001 | Structuring. Brightwater Cash and Carry Ltd (CUS-1020), account ACC-1020-01, rule MTB-AML-RULE-001. | Suspicious. Seven cash deposits of USD 9,100 to 9,800 in 10 days, total USD 66,450, each under the USD 10,000 reporting threshold. Earlier deposits were USD 1,400 to 3,100. Open a case. A branch note (CNT-5008) says the owner now brings deposits "in batches". |
| TMA-3002 | Pass-through. Nimbus Transit Consulting Ltd (CUS-1021), ACC-1021-01, rule MTB-AML-RULE-002. | Suspicious. Three credits (48,000, 52,500, 39,000) from Tallowmere Holdings each leave the next day to Quillgate Trading, keeping about 1.36 percent (together USD 139,500 came in and USD 137,600 went out, so USD 1,900 stayed; each round keeps 1.25, 1.33 and 1.54 percent). The customer could not name its clients (CNT-5009). Open a case. |
| TMA-3003 | Higher-risk jurisdiction. Copperfield Import Traders Ltd (CUS-1022), ACC-1022-01, rule MTB-AML-RULE-003. | Needs review and a case at medium priority. Four payments (14,800, 9,950, 12,300, 16,200; total 53,250) to Karn Harbour Freight Agency (CPY-4005) in Kharnovia, a new counterparty with no contract on file. The customer's business plausibly needs freight, so the narrative should say what is missing (contract, invoices), not call it proven. |
| TMA-3004 | Benign payroll spike. Saltmarsh Catering Co (CUS-1023), ACC-1023-01, rule MTB-AML-RULE-004. | Not suspicious. No case. 41 payroll payments against an average of 22 because 19 seasonal staff were hired, as the owner said 45 days ago (CNT-5011). The 22 regular payees and amounts are the same as in earlier months, and a festival contract advance of USD 98,000 arrived the day before. An earlier similar alert (TMA-2902) was closed. |

An agent saves its work on an alert with `save_alert_investigation` before a person opens a case: findings, each with the ids of the records that show it (transactions, alerts, rules, contacts, counterparties), a narrative and a recommendation of `open_case` or `no_case`. `get_monitoring_alert` returns every version in `investigation_drafts`. When a person opens a case from the alert, the latest saved narrative becomes version 1 of the case's narratives, and the next `save_case_narrative` is version 2. For TMA-3004 the right recommendation is `no_case`; for the other three it is `open_case`.

There is no operation that files a report. A person does that.

## Payments (system: payments)

Investigations

| Id | For | Right answer |
|---|---|---|
| INV-5001 | Beneficiary says it never arrived (PAY-6001, USD 1,850). | It was credited 3 days ago. It was held at the correspondent bank over the weekend. The pacs.002 status is ACSC. Tell the customer it arrived, with the date. No bank rule applies: `rule_ids` is empty. |
| INV-5002 | Amount arrived short (PAY-6002, USD 25,000). | USD 37.50 was deducted by an intermediary bank (24,962.50 arrived). The payment was sent with charges OUR, so the deduction is wrong under MTB-PAY-RULE-105. The bank claims it back and tells the customer. `rule_ids`: MTB-PAY-RULE-105 (the rule on charges). |
| INV-5003 | Payment returned (PAY-6003, USD 3,200). | The beneficiary account is closed (pacs.004 reason AC04). The money was credited back to ACC-1006-01 two days ago. A new payment needs corrected details (MTB-PAY-RULE-106). `rule_ids`: MTB-PAY-RULE-106 (the rule on returned payments). |

Repairs

| Id | For | Right answer |
|---|---|---|
| REP-7001 | Transposed IBAN digits (PAY-6101). Rule MTB-PAY-RULE-101, reason code AC01. | Replace `XB82BRVN73201150000124` with `XB82BRVN73201150000142`, the IBAN used in the earlier payment PAY-6050 to the same beneficiary (`search_payments` with `beneficiary_account` XB82BRVN73201150000142 finds PAY-6050 alone, and with `beneficiary_name` "Alder Wharf Marine Supplies" it finds PAY-6050 and PAY-6101). The wrong IBAN fails the mod-97 test. This is the only invalid beneficiary IBAN in the data. |
| REP-7002 | BIC does not match the bank (PAY-6102). Rule MTB-PAY-RULE-102, reason code RC01. | Replace BIC `QNMKXQQ1` with `TESLXTT1`, taken from the bank directory (`lookup_bank`, name "Tessaly Mutual Bank"). |
| REP-7003 | No beneficiary address on a cross-border payment (PAY-6103). Rule MTB-PAY-RULE-103, reason code BE04. | Add "Smelter Row 12, Velmora, Aldoria", the address on the earlier payment PAY-6051 to the same beneficiary and IBAN. |
| REP-7004 | No purpose code for the Meridia to Rovaland corridor (PAY-6104). Rule MTB-PAY-RULE-104, no reason code given. | Purpose code `GDDS` (goods), because the reference is "Invoice RD-88412 dental chair spare parts". The proposal must say what it relied on. |

`get_payment_investigation` returns `rule_ids` (the bank rules that apply), `rules` (their full text) and `rule_note` (why they apply). Simulated investigations follow the same rule: a late credit has none, a short amount has MTB-PAY-RULE-105, both kinds of return have MTB-PAY-RULE-106.

`search_payments` also filters on `beneficiary_name` (part of the name) and `beneficiary_account` (the IBAN, or a part of at least 6 characters), so earlier payments to the same beneficiary can be found. Each row shows `beneficiary_account`.

`release_repaired_payment` is refused with 409 until a proposal exists, and needs `approved_by`.

## Lending (system: lending)

| Id | For | Right answer |
|---|---|---|
| LAP-8001 | Salaried personal loan, complete pack (Marguerite Oakhaven, CUS-1012, USD 18,000, 36 months at 9.5 percent). | All four required documents are present. Income agrees across form, payslips and statements (gross 5,200, net 4,010). Instalment 576.59. Debt to income = (450 + 576.59) / 5,200 = 0.197, under the 0.40 limit of MTB-POL-030. |
| LAP-8002 | Small business loan with two documents missing and one figure that differs (Harrowgate Bakery Supplies Ltd, CUS-1017, USD 60,000). | Missing: `tax_return` and `ownership_declaration`. The form says average monthly turnover USD 62,000; the six bank statement months total 308,400, an average of 51,400 (the financial statements show revenue 612,000, about 51,000 a month). Record both figures and their sources. |
| LAP-8003 | Small business loan with three years of financial statements, for a credit analysis (Pinecrest Tooling Works Ltd, CUS-1018, USD 120,000). | Latest year: current ratio 505,000 / 352,000 = 1.43 (policy at least 1.20). Debt to equity 180,000 / 697,500 = 0.26 (at most 2.50). Debt service cover 258,000 / (18,000 + 60,000) = 3.31 (at least 1.25); with the new loan's debt service of about 29,892 a year it is 2.39. Revenue grew 6.7 percent then 8.3 percent. EBITDA margin 15.7 percent. All three ratios pass. The form says 24 employees, and so does the press article ART-6012. |
| LN-9001 | Approved loan whose contract differs from the approved terms in exactly three places (Lanternfish Logistics Ltd, CUS-1019). | 1. Rate margin: approved 3.25 percent, contract 3.75 percent (clause 3). 2. Debt service cover covenant: approved 1.30, contract 1.50 (clause 6a). 3. Security: approved "first-ranking charge over the five delivery vehicles listed in Schedule A", contract "general charge over all present and future assets" (clause 7). Everything else agrees (amount, term, repayment, fees, debt to equity covenant, law). |

`get_customer_exposure` gives each loan's `monthly_instalment`, and it agrees with the statements and the collections calls: LN-9005 450.00 (the car loan instalment on the statement in LAP-8001, and CAL-1001), LN-9003 930.00 (CAL-1002), LN-9101 210.00 (CAL-1003), LN-9102 275.00 (CAL-1004), LN-9103 520.00 (CAL-1005). LN-9002 is 6,500.00, which is the debt service in the LAP-8003 analysis: (18,000 interest + 60,000 principal) / 12. LN-9001 is 4,979.84 and LN-9004 is 2,072.17.

The documents that name figures in an application are read with `get_application_document`. In `save_missing_items` and `save_credit_memo` the source of a figure is a document id of the application (for example DOC-8203) or `FORM` when the figure is on the application form itself (LAP-8002: the form says average monthly turnover 62,000, source `FORM`).

## Cards (system: cards)

| Id | For | Right answer |
|---|---|---|
| CRD-2001 | Lost card with two payments the customer would not recognise (Dorian Quillfeather, CUS-1002). | Block the card (reason `lost`), request a replacement (reason `lost`), and open a dispute for CTX-2001-U01 (Ironwood Electronics Online, 389.00, online) and CTX-2001-U02 (Quickfuel Station 44, 85.40, contactless), total 474.40. Do not dispute CTX-2001-A01 and CTX-2001-A02: they were made before the card was lost (about 17:00 two days ago; the call note CNT-5001 and email CNT-5002 give the story). |
| CRD-2002 | Card about to expire (Sabine Tarrowgate, CUS-1003). | Expiry is in the next month. Request a replacement (reason `expiring`). Do not block it. |
| CRD-2003 | Card with an open dispute (Emeric Lowenhall, CUS-1004). | Dispute DSP-6001 is open for CTX-2003-D02, a duplicate charge of 42.00 by Harbourlight Cinema one minute after CTX-2003-D01. Waiting for the merchant. Do not open a second dispute for the same payment (409). |

Every card payment carries `country` (a code, XM is Meridia, the home country), `town` and `card_present` (true for chip and contactless, false for online). In the starting data every card payment is in Meridia except the three of FRD-3001, which are in Norvania (QN): Silverkeld, Norvik and Kaldmoor. That is how "the customer's earlier payments were all at home" can be read from the data: for card CRD-2008 every payment before CTX-2008-F01 is a chip payment in Meridia (XM), in Port Ilvane, Tallowby or Marlow Reach.

## Fraud (system: fraud)

A decision is `block` (fraud confirmed: the card is blocked, or a held payment is cancelled, or online access is blocked), `release` (not fraud) or `refund` (as block, and the money is returned: card payments are refunded, a sent payment is recalled). The right answer for a true fraud case is `refund`.

| Case | For | Right answer |
|---|---|---|
| FRD-3001 | Card-not-present purchases abroad at night. Marguerite Oakhaven (CUS-1012), card CRD-2008, rule FRD-RULE-001. | True fraud: `refund` (which also blocks the card). Three online purchases in Norvania at 02:14, 02:31 and 03:05 (CTX-2008-F01 to F03, total 2,219.90). All of the card's earlier payments were chip payments in Meridia. Two contacts show she was at home: CNT-5201 (a call from her home number at 22:40 the evening before) and CNT-5202 (a call from home at 07:15 the same morning, saying the payments are not hers). Offer a replacement card. |
| FRD-3002 | Large first payment to a new payee. Leopold Fenwick-Aral (CUS-1015), PAY-6401, USD 18,500 to Brookhaven Joinery Works, rule FRD-RULE-002. | Not fraud: `release`. The payment is held. Contact CNT-5204 is a call-back in which he passed the security questions, said he added the payee himself, named it as his kitchen builder and read back the payee and the amount. CNT-5203 (20 days ago) shows he asked how to pay a builder's deposit. His earlier case FRD-2902 was also released. |
| FRD-3003 | Account takeover. Rosalind Heathcote-Brae (CUS-1014), PAY-6402, USD 7,400 to Marrowfield Remittance Agents in Aldoria, rule FRD-RULE-003. | True fraud: `refund`. A new device signed in at 10:02, the password was reset at 10:09, a payee was added at 10:15 and the payment was made at 10:41, 39 minutes after the first event. The device was never seen on the profile, the sign-in came from another country, and she has never paid anyone outside Meridia (CNT-5205). The refund recalls the payment and blocks online banking. |
| FRD-3004 | A subscription called fraud. Oskar Brindlemoor (CUS-1006), card CRD-2006, CTX-2006-S04, USD 11.99 to Streamline Video Club, rule FRD-RULE-004. | Not fraud: `release`. The card's own list shows three earlier payments of 11.99 to the same merchant (CTX-2006-S01 to S03, 92, 62 and 32 days ago). It is a subscription the customer forgot. It belongs with disputes in the cards system (`open_card_dispute`, or the merchant to cancel). His earlier case FRD-2901 was also released. |

Earlier closed cases for history: FRD-2901 (CUS-1006) and FRD-2902 (CUS-1015), both released.

## Reconciliation (system: recon)

All three accounts are nostro accounts. The break item is the unmatched entry. Candidates are other entries on the same account that could belong to it. A proposal of `refer_to_person` cannot be posted: `post_break_resolution` answers 409.

| Break | For | Right answer |
|---|---|---|
| BRK-4001 | NOS-ALDB-01. Statement credit STM-8101, 12,480.00, reference INV-558210-AQ, value date 5 days ago. | Match with ledger entry LED-7101 (same amount, value date one day earlier, reference INV-558210-AO differs by one character). Rule RECON-RULE-001. LED-7102 (12,408.00, another invoice) is not the match. |
| BRK-4002 | NOS-QNMK-01. Statement credit STM-8201, 8,000.00, reference SETT-BATCH-0457. | Match one to two: LED-7201 (5,250.00) and LED-7202 (2,750.00), both posted in BATCH-0457. Rule RECON-RULE-002. LED-7203 (5,250.00, an older batch) is not part of it. |
| BRK-4003 | NOS-TESL-01. Statement credit STM-8301, 9,985.00, narrative "less charges 15.00". | Match with LED-7301 (10,000.00, same reference) and post an adjusting entry of 15.00: debit GL-6120 (bank charges), credit NOS-TESL-01. Rule RECON-RULE-003. The difference is -15.00. |
| BRK-4004 | NOS-ALDB-01. Ledger entry LED-7402, 4,175.50 debit, reference PO-3382. | Duplicate of LED-7401 (same amount, value date, reference and batch, posted two minutes earlier and already matched to STM-8401). Reverse LED-7402 (`reverse_duplicate`, `reverse_entry_id` LED-7402). Rule RECON-RULE-004. Never reverse LED-7401. |
| BRK-4005 | NOS-QNMK-01. Statement debit STM-8501, 3,275.40, reference UNK-77QX, 9 days old. | It cannot be resolved. No candidate exists. Say so, list what was checked (amount within 5 days, reference, batch sums, duplicates), and refer it to a person (`refer_to_person`). Do not match it, write it off or adjust. Rule RECON-RULE-005. These searches prove that nothing was found, and an agent can show them: `search_ledger_entries` with `amount_from` and `amount_to` both 3275.40 (any account, any date) finds nothing; the same with `account` NOS-QNMK-01, `date_from` and `date_to` five days either side of the value date (9 days ago), finds nothing; `reference` UNK-77QX finds nothing. In that window the account has only LED-7201 and LED-7202 (5,250.00 and 2,750.00, batch BATCH-0457, which add up to 8,000.00) and LED-7203 (5,250.00), none of them 3,275.40. `search_statement_entries` for the same amount finds STM-8501 itself and nothing else, so it is not a duplicate on the statement. |

`get_ledger_entry` (GET /ledger/{entry_id}) and `get_statement_entry` (GET /statements/{entry_id}) read one entry, with `related_break_ids`. `search_ledger_entries` (GET /ledger) and `search_statement_entries` (GET /statements) filter by `account`, `amount_from`, `amount_to`, `date_from`, `date_to` (value dates) and `reference` (part of it), and answer with the filters in `searched`.

BRK-3901 is an older break that was already resolved (a match with one character different in the reference).

## Media screening (system: news)

Search is by words in the title or body. Names are shared, so each article must be read before it is called adverse. Ages in the articles are fixed in the text. Articles ART-6016 to ART-6025 are noise and mention nobody in the data.

| Subject | Adverse and about the subject | Namesake (someone else) | Neutral or good news |
|---|---|---|---|
| Valdis Orrenmoor (CUS-1007, SCR-2003, WL-9003) | ART-6001, ART-6002. Born 30 September 1971, Quenmark national, lives on Cinder Quay in Port Ilvane. Arms brokering, asset freeze upheld. | none | none |
| Karn Harbour Freight Agency (CPY-4005, TMA-3003) | ART-6003 (customs inquiry, mislabelled cargo), ART-6004 (accused of moving goods for listed buyers). | none | none |
| Leopold Vanhollow (WL-9006, politically exposed person) | ART-6005, ART-6006. Minister of Public Works, Quenmark. Questioned over a road contract, audit inquiry widened. | none | none |
| Perdita Vanhollow (CUS-1010, his spouse) | none. No article names her. | none | none |
| Ilvane Marrowick (CUS-1001, born 1984, Port Ilvane) | none | ART-6007: aged 63, trawler skipper in Corrowick, Brevnia, fined over a fish quota. | none |
| Wynne Castellane (CUS-1005, born 1990, Meridia) | none | ART-6008: aged 54, machinery dealer in Brandymoor, Tessaly, jailed for tax fraud. | none |
| Oskar Brindlemoor (CUS-1006, born 1978, Meridia) | none | ART-6009: aged 19, student sprinter in Silverkeld, Norvania, doping ban. | none |
| Sabine Tarrowgate (CUS-1003, born 1979, Marlow Reach) | none | ART-6010: aged 71, hospital administrator in Velmora, Aldoria, convicted of embezzlement. | none |
| Harrowgate Bakery Supplies Ltd (CUS-1017, wholesaler in Tallowby) | none | ART-6011: a flour mill in Hartsfell, Quenmark, in administration. The article says it has no link to any business in Meridia. | none |
| Pinecrest Tooling Works Ltd (CUS-1018) | none | none | ART-6012: wins the export award, and names its 24 staff (the application LAP-8003 says 24 employees). |
| Lanternfish Logistics Ltd (CUS-1019) | none | none | ART-6013: adds five vehicles and a second depot. |
| Saltmarsh Catering Co (CUS-1023) | none | none | ART-6014: wins the harvest festival contract. |
| Marguerite Oakhaven (CUS-1012) | none | none | ART-6015: elected chair of a parents' group. |

Right answer for a summary: for the three adverse subjects, report the articles with the facts that tie them to the subject. For a namesake, say the article is not about the customer and give the difference. For a neutral subject, report no adverse media. Each finding names its article id and gives the article's page address (`page_url`).

## The regulator's publications (the Meridia Financial Conduct Authority, invented)

The policies are in `banking/policy-library`. Dates are relative to the bank date.

| Publication | Days old | Bears on | Right verdict |
|---|---|---|---|
| MFCA-2026-045 Circular: customer information shared through a shared platform (consent mechanism, data format, dispute process) | 3 | MTB-POL-021 clause 7.1, which says the policy does not cover this. Clauses 3.1, 3.2 and 4.3 cover consent and records only for ordinary sharing. | Gap. |
| MFCA-2026-036 Guideline: assessing a supplier's own use of artificial intelligence | 31 | MTB-POL-033 clause 7.1 and MTB-STD-041 clause 8.1. Both say they do not cover it. | Gap. |
| MFCA-2026-040 Notice: report a technology incident that affects customers to the regulator within four hours | 18 | MTB-POL-033 clause 4.1, which says "within the period the regulator sets". | Partly covered. The period (four hours) must be written into clause 4.1. The one-hour report to the Head of Operational Risk already fits inside it. |
| MFCA-2026-033 Guideline: human review of generative AI output sent to customers | 44 | MTB-POL-014 clauses 5.2 (a person reviews every customer-facing output, the reviewer's name is recorded) and 5.3 (staff are told which systems use AI). | Covered. |
| MFCA-2026-029 Circular: handling of coins and banknotes at branches | 57 | None of the four documents. | No action. |
| MFCA-2026-043 Consultation paper: telling customers when AI contributed to a decision | 9 | MTB-POL-014 clause 7.2 would be affected if it became binding. It is not binding. | Note only. |

Publications that arrive by `POST /admin/simulate/regulator-publication`, in this order, then again from the first:

| Arrives | Bears on | Right verdict |
|---|---|---|
| Circular: records of sharing arrangements for customer information | MTB-POL-021 clause 4.3 (recipient, categories, purpose, legal basis). | Covered. |
| Circular: telling customers when AI was used in a decision about them | MTB-POL-014 clause 7.2, which says the policy does not cover it. | Gap. |
| Notice: holiday opening hours of the regulator's counters | None. | No action. |
| Guideline: recovery time of no more than four hours for each critical system, tested yearly | MTB-POL-033 clauses 2.1 and 2.2 (a recovery time objective and a yearly test, but no four-hour limit; MTB-STD-041 clause 4.2 sets four hours for suppliers only). | Partly covered. |

## Onboarding (system: onboarding)

Documents are text. Dates are relative to the bank date. A proof of address must be dated within 3 months (90 days). A watchlist hit is checked with `screen_name`. The decision `refer_to_compliance` is only a recommendation in the file: the decision call takes approve, decline or ask_applicant.

| Application | For | Right answer |
|---|---|---|
| ONB-1001 | Individual, Odalys Merrowby, clean pack. | Approve. Name, date of birth, nationality, identity number and address agree. The bill is 26 days old, the card is valid, screening finds no hit. |
| ONB-1002 | Individual, form says Isadora Fenimore, identity card says Isadora Fennimore. Proof of address (a water bill) is 150 days old. | Ask the applicant. Two problems: the one-letter name difference (never assume a typing error) and a proof of address older than 3 months. Date of birth and number agree. |
| ONB-1003 | Individual, Wynn Castellano, born 1962-02-02, Brevnia, identity number BRV-559120. | Do not open. Recommend `refer_to_compliance`. `screen_name` returns WL-9001 first with score 100, date of birth and nationality both match, and the entry has the same identity number. Say nothing to the applicant about the reason. |
| ONB-1004 | Company, Cobblegate Print Supplies Ltd, one owner and director with 100 percent. | Approve. All three documents are in, the registry extract and the declaration agree with the form. |
| ONB-1005 | Company, Larkfield Marine Services Ltd. 60 percent held by Vardane Holdings Ltd (Quenmark), 40 percent by Corwin Ashdown. | Ask the applicant. The ownership chain has a gap: no document shows who owns Vardane Holdings Ltd, so 60 percent is not traced to people (above the 25 percent threshold). List the gap and the missing document. Never name or guess the owners. |
| ONB-1006 | Company, Thistlewick Bakehouse Ltd. The registry extract lists directors Nerys Hallowfield and Garrick Oldacre. The form lists only Nerys Hallowfield. | Ask the applicant. Garrick Oldacre (appointed 21 days ago, also a 30 percent owner) is not on the form. He must be listed, identified and screened. |

| Review | For | Right answer |
|---|---|---|
| KYR-1001 | Cassius Dunmore (CUS-1013), individual. | Nothing changed. The fresh identity card and proof of address agree with the profile. Rating stays standard. Sign-off only. |
| KYR-1002 | Leopold Fenwick-Aral (CUS-1015). | Two changes: address (8 Kestrel Hill, Marlow Reach to 22 Barley Mill Lane, Tallowby, Meridia, source KYD-1002-01) and occupation (employee, quantity surveyor, to self-employed building surveyor, source KYD-1002-02). Rating stays standard. Sign-off only. |
| KYR-1003 | Orchard Lane Dental Group (CUS-1024). | Ownership changed from Ottoline Brackenridge 55 and Hamish Brackenridge 45 to 40, 30 and Tavish Orrelby 30 (Gallowmere, Kharnovia, the higher-risk country). Propose the rating `high` (from standard) with that reason. The change needs `rating_change_approved_by`; without it `complete_kyc_review` answers 409. |

## Complaints (system: complaints)

The procedure is in `get_complaints_procedure`: acknowledge within 2 working days, final response within 15, redress when the bank erred, a declined loan is not a service failure. Its rule for severity: low for a small sum or an inconvenience while the customer can still use the account and the card, medium when the customer was without money or a service for a time or a time limit of the procedure was missed, high when the customer cannot reach their money or their card or may be vulnerable. The highest level that fits is the severity.

`get_complaint` returns the linked records read from the other systems. A linked card comes with the `customer_id` of its holder and its block note. A linked payment comes with its timeline and, in `status_reports`, the inbound status reports the payments system holds for it (message id, type, date, summary and the fields of the report, such as `status` and `credited_on`).

| Complaint | For | Right answer |
|---|---|---|
| CMP-1001 | Anselm Drozdowich (CUS-1009). Monthly account fee of 12.00 taken twice on ACC-1009-01, 8 days ago. | Fees and charges, severity low (a small sum, and he can still use the account), upheld. Refund one fee (USD 12.00 to ACC-1009-01), apologise. An earlier complaint CMP-0901 was not upheld, a different matter. |
| CMP-1002 | Rosalind Heathcote-Brae (CUS-1014). Payment PAY-6001 arrived late. | Payments, not upheld, no bank error. Explain with the dates in the timeline of PAY-6001 (investigation INV-5001 is open): sent 6 days ago, held at the correspondent bank over the weekend, credited 3 days ago. The status report MSG-6001-2 on the linked payment gives status ACSC and the date credited. No redress. |
| CMP-1003 | Isolde Pennywhistle (CUS-1016). Loan LAP-8010 declined. | Lending decision, not upheld, not a service failure. Debt to income is 0.48 against the 0.40 limit of MTB-POL-030. Explain the reason and how to ask for a review: write to the Credit Review Desk within 30 days with new information. Promise nothing. |
| CMP-1004 | Ilvane Marrowick (CUS-1001). Husband died 18 days ago, card CRD-2004 blocked 6 days ago by the deceased accounts process. | Possible vulnerability (recent bereavement): yes. Priority handling, one named person, a kind plain letter. Upheld: the block was applied to her own card by mistake. The linked card names its holder, CUS-1001, and the block note says the process is for cards held by the person who died. Replace the card, apologise. |
| CMP-1005 | Sabine Tarrowgate (CUS-1003). Received 13 working days ago, never acknowledged. | Admit the late acknowledgement (11 working days late) and apologise. The final response is due in 2 working days: urgent. |

## Collections calls (system: collections)

Rules CR-01 to CR-07 are in `get_conduct_rules`. Each rule is followed, breached or not applicable, with the words from the transcript.

| Call | For | Right answer |
|---|---|---|
| CAL-1001 | Marguerite Oakhaven, LN-9005, 12 days overdue. | All rules followed (CR-05 and CR-06 not applicable). Identity confirmed before the debt, the promise (USD 450.00, a named day, by card in the app) is read back. No supervisor. |
| CAL-1002 | Cassius Dunmore, LN-9003. | CR-02 breached: the caller states USD 1,860.00 and 38 days overdue before asking for the date of birth. The rest is followed, the promise is recorded exactly. Supervisor review. |
| CAL-1003 | Dorian Quillfeather, LN-9101. | CR-05 breached: the customer says he lost his job six weeks ago and no hardship option is offered. Identity and the promise (USD 100.00, by card) are fine. Supervisor review. |
| CAL-1004 | Emeric Lowenhall, LN-9102, 18:50. | CR-06 breached: his sister answers and the caller says the loan is behind by USD 275.00. CR-02 and CR-07 not applicable, the customer never came on the line. Supervisor review. |
| CAL-1005 | Wynne Castellane, LN-9103, 19:35. | No breach. The call is firm: the caller states what the loan terms say (recovery team after 45 days, the account is at 33) and asks whether anything makes it hard to pay. That is calm and accurate, not a threat. 19:35 is inside the hours. The promise is read back. No supervisor. |

## Audit evidence (system: audit)

Each test names a clause of MTB-POL-033 and an evidence plan. The pack lists what was found (with record ids), what is missing (with what was searched) and the exceptions. It never concludes.

| Test | Clause | What the records show |
|---|---|---|
| CTL-1001 Access reviewed quarterly | 6.1 | Three systems (core-banking, payments-hub, card-platform) times four quarters (2025-Q4 to 2026-Q3 on the bank date 2026-11-24) is 12 reviews expected. 11 exist. Missing: payments-hub, 2026-Q2. A ticket says it was postponed, with no review record attached. |
| CTL-1002 Change control | 3.1 | Five sampled changes CHG-2201 to CHG-2205, all on critical systems. CHG-2203 (card-platform) has no rollback plan. CHG-2204 (online-banking, emergency) has no named approver, and an open ticket says approval was to be recorded afterwards. The other three have both. CHG-2208 has no rollback plan but is on a system that is not critical and is not in the sample. |
| CTL-1003 Recovery tested yearly | 2.2 | Four critical systems. Card-platform was last tested 14 months before the bank date (2025-09-24); a ticket says the test moved again with no new date. The other three were tested within 12 months (payments-hub took 4.5 hours against the 4 hour target, a finding). |
| CTL-1004 Multi-factor sign-in | 6.2 | The latest reviews (2026-Q3) show two service accounts exempt: svc-recon-batch (payments-hub) and svc-card-feed (card-platform), each with an exemption ticket and no end date. Core-banking has none. Report them as exceptions. |

## IT operations (system: itops)

The service clock stands at 10:00 on the bank date (Tuesday 2026-11-24). Times are local. No operation runs a runbook step or changes a service: an agent reads, assesses and drafts. An assessment is refused with 409 on a closed incident, and a post-incident review is refused with 409 on an incident that is not closed. A review action that names an owner or a date is refused with 422: people assign owners.

| Incident | For | Right answer |
|---|---|---|
| INC-7001 | Payments slow down 20 minutes after a release. Alert ALT-9101, opened 08:46, severity high. | The likely cause is release 4.18.0 of payment-service (change ITC-8101, deployed 08:00). The release adds a duplicate-payment check behind the flag `duplicate_check_enabled`, which the release schedule switched on 15 minutes later. p95 latency was 415 to 430 ms until 08:10, 612 ms at 08:20, 1,480 ms at 08:30 and 3,200 ms at 10:00. Error rate went from 0.2 to 2.9 percent. Payments database CPU went from 34 to 95 percent, first above 50 at 08:20. Volume fell from about 210 to 156 a minute (customers retry or give up). The other changes of the day (ITC-8102 receipt wording, ITC-8103 reporting database indexes) do not touch the payment path. Check next: the CPU of the payments database and the flag. The runbook says that switching the flag off needs the incident manager and a rollback needs the change manager: they are for people to run. Customer impact: slow payment screens and timeouts, 14 calls by 08:55. |
| INC-7002 | Card authorisations fail because a certificate expired, with no recent change. Alert ALT-9102, opened 05:08, severity critical. | Cause: the client certificate `cardproc-mtls-client` for the link to the card processor expired at 04:58 (dashboard DASH-1003 and the log line "certificate has expired"). Error rate stepped from 0.4 to about 97 percent at the 05:00 sample and has stayed there. Volume did not drop (36 to 130 a minute): the calls arrive and fail. Latency fell from about 180 to 40 ms because calls fail fast. There was no change to card-authorisation in the last 168 hours: the last one, ITC-8104, was 12 days ago and touched one rule, not a certificate. The other four certificates are valid. Next: the renewal is requested and not yet issued, and installing it needs a change record and the change manager. Customer impact: about 97 percent of card purchases declined since 05:00. |
| INC-7003 | A false alarm from a monitoring gap. Alert ALT-9103, opened 09:36, severity medium. | The service is fine. The collector on host stmt-app-02 sent no volume samples from 09:10 to 09:40 (last sample before the gap 09:00, next after 09:50, 50 minutes without data). The service's own measures are normal throughout: application log volume 29 to 33 a minute, error rate 0.1 to 0.2 percent, p95 latency 255 to 270 ms. No change in the last 7 days. The collector restarted under its watchdog at 09:44. Next: record the gap and read volume reports for 09:10 to 09:40 with care. Do not restart the statement service. |
| INC-7004 | A closed incident for a post-incident review. Opened nine days ago at 14:08, resolved 15:32, closed eight days ago. | Root cause: the identity team rotated the token signing key at 14:02 (change ITC-8106), ahead of the plan for 22:00, and online banking kept the old public key in its cache for up to 24 hours, so logins failed with "token signature invalid". The first assumed cause, database connection pool exhaustion, was wrong: the pool was at 40 to 43 percent throughout (14:50 entry: "The pool is not the cause"), and restarting it at 14:35 changed nothing. The assumption came from login latency rising from 320 to about 1,100 ms. The fix was flushing the key cache on both nodes at 15:25. The change record shows 22:00 as the plan and 14:02 as the real time, corrected at 16:40, which is why nobody linked the change at first. Went well: the alert fired in 6 minutes and the database team ruled out the pool. Did not go well: the first guess, the 14:35 restart and the wrong time on the change record. Likely actions (owners left blank): record the real time of a change when it is done, show linked identity changes on the incident, check the log text before restarting anything. |

## Legacy core system (system: legacy)

An old core banking system, read only. Its customers and account numbers are its own and are not the records of the `core` system. The meaning of most columns is not written down: it is worked out from the stored procedures, the four programs and the sample rows. The right answer for a column that cannot be worked out is to say so.

| Column | Meaning and where it shows |
|---|---|
| ACMAST.AC_TY | Product: 10 current, 20 saver, 30 business current, 40 term deposit (decode in STMTEXT). |
| ACMAST.AC_ST | Status: A active, D dormant, C closed, F frozen (SP_POST_TXN, SP_FLAG_DORMANT, DORMSWP). |
| ACMAST.AC_BAL | Balance in the smallest unit (cents), negative when overdrawn. SP_BAL_ENQ and INTACCR divide by 100. Sample 1234567 is 12,345.67. |
| ACMAST.AC_ACR | Interest accrued and not yet posted, in currency units with six decimals (INTACCR). In the sample it equals the daily amount times the days since the 1st. |
| ACMAST.AC_RT | Rate code, looked up in RTTAB. RT_BP is the yearly rate in basis points (INTACCR divides by 10000). R03 is 3.25 percent. |
| ACMAST.AC_LTX | Date of the last transaction the customer started, as year and day of year (YYYYDDD). SP_POST_TXN moves it only for codes 101, 102, 201, 401 and 402, not for interest (301) or fees (302). In the sample, a fee posted today did not move it. |
| ACMAST.AC_FLG1 | Agreed overdraft, Y or N. It chooses the overdraft rate ROD against the higher unarranged rate RUN. |
| ACMAST.AC_FLG2 | Statement by post (P) or electronic (E): medium confidence, from the STMTEXT comment and the sample values. |
| ACMAST.AC_X1 | CANNOT be worked out. No procedure or program reads or writes it. It has no catalogue comment. The sample values (0, 12, 7, 3) do not follow the type, the status, the flags or the balance. The right answer is to say the meaning is unknown and who could know (the people who ran the system). |
| TXHIST.TX_CD | 101 cash deposit, 102 cheque deposit, 201 cash withdrawal, 301 interest, 302 fee, 401 standing order, 402 transfer (STMTEXT). TX_AM is unsigned in the smallest unit and TX_SN (C or D) is the sign. |
| CUMAST.CU_SG | R retail and B business from the sample names. P is a priority customer: STMTEXT prints a banner for it. |
| SOMAST.SO_FQ, SO_ST | W weekly, M monthly, Q quarterly (SORUN). A active (SORUN, DORMSWP). The sample also has S: its meaning is not stated anywhere, so say low confidence. |

The rounding rule. INTACCR keeps rule FIN-14: daily interest is truncated at six decimals and never rounded, at month end the accrued total is rounded to two decimals with halves away from zero, what is left below one cent stays in AC_ACR and carries into next month, and the day basis is 365 also in a leap year. Worked example: balance 12,345.67 at R03 gives 1.099271 a day. Thirty days are 32.97813, so 32.98 is posted and -0.00187 carries. A conversion that rounds each day to 1.10 posts 33.00. A conversion that uses binary floating point, rounds half to even, drops the carry or uses 366 days also changes the result. A good conversion keeps decimal arithmetic and lists the rule in the points an engineer must check.

Other points a good explanation of the programs makes: DORMSWP sweeps after 730 days idle, never touches term deposits (type 40) or an account with a live standing order, and counts only customer-started activity. SORUN skips an order the account cannot cover (unless the account has an agreed overdraft), does not retry, and moves the next date on, so an order on the 31st goes 31 Jan, 28 Feb, 28 Mar (marked "this is known" in the code). STMTEXT works out the opening balance as the closing balance minus the net movement, and skips closed accounts but not dormant ones.

## Pension funds (system: funds)

Fund fact sheets are dated at the last month end (2026-10-31). They show 1 month, 3 months, 6 months, 1 year, 3 years a year, 5 years a year and since launch a year. They never show calendar years.

| Id | For | Right answer |
|---|---|---|
| MEM-5001 | Tobias Wrenfield (CUS-1011), a member with holdings in three funds. | FND-3001 4,210.5 units at 1.2840 is 5,406.28. FND-3002 6,800 units at 2.0715 is 14,086.20. FND-3003 2,950.25 units at 3.4520 is 10,184.26. Total 29,676.74. His name, date of birth, address and employer (Harbourlight Services) are the same as in the core system. |
| Fact sheets | A question they cannot answer. | "What was the 5 year return of the Balanced Growth Fund (FND-3002)?" The sheet says the fund is younger than 5 years (launched 2022-09-26) and shows no figure. The answer is that the fact sheets do not say. The same holds for any calendar year, for the Sustainable Equity Fund (FND-3005) over 3 or 5 years, and for any date after the sheet date. |
| BAT-4001 | Harbourlight Services, period 2026-10, a clean batch of 5 rows, control total 1,959.10. | Every row passes rules 1 to 4. Posting (needs a saved result and `approved_by`) posts 5 rows, 1,959.10, and buys units in each member's contribution fund. |
| BAT-4002 | Stillwater Clinic, period 2026-10, 6 rows, control total 1,883.00. | Row 4 names member MEM-5040, who does not exist: rule 1. Row 5 repeats MEM-5007 from row 2: rule 3 (row 2 passes). Row 6 has an employee amount of -85.00: rule 2. Rows 1, 2 and 3 pass. Posting posts rows 1 to 3 only, 1,215.50. If a saved result passes a failing row, posting is refused with 409. |
| BAT-4003 | Already posted (Harbourlight Services, 2026-09). | Saving a result or posting is refused with 409. |
| FRM-4001 | A transfer form for MEM-5003 with an unreadable account number. | The receiving scheme account number has one digit that cannot be read and one that could be 4 or 9: rule 5 fails and rule 8 sends the form to a person. Never guess the digits. The name, date of birth (14/03/1983) and signature are fine and the form was received 12 days ago (rules 6 and 7 pass). |
| FRM-4002 | A clean transfer form for MEM-5002. | The account number reads in full (10 digits), the name and date of birth (02/12/1979) match the register, signed 10 days ago: rules 5 to 7 pass. |

## Client meetings (system: crm)

Tomorrow is Wednesday 2026-11-25. Relationship manager Sunniva Haldane-Rook has three meetings. Holdings are read from the other systems, so the totals agree with them.

| Meeting | Client | Right answer for the brief |
|---|---|---|
| MTG-1001, 09:30 | Valdis Orrenmoor (CUS-1007), savings review. | Adverse press in the news system: ART-6001 (his assets were frozen in Quenmark, 410 days ago) and ART-6002 (a court upheld the order 95 days ago, his lawyer says he will appeal). The last meeting (MTG-1006, 120 days ago) noted that he is in a legal dispute in Quenmark and asked how fast money can move to a Quenmark account. He holds one deposit account, ACC-1007-01, 19,279.32, and no loans or investments. The screening system also holds an open alert on him (SCR-2003, a true match): that is a compliance matter, so the brief may say compliance is involved but must not tell the client. Raise the press and the question about moving money with care and agree with compliance before the meeting. |
| MTG-1002, 11:00 | Pinecrest Tooling Works Ltd (CUS-1018), loan update. | A loan application is in progress: LAP-8003, USD 120,000, received. The client already owes 180,000 on LN-9002. Deposits are 65,611.13 (ACC-1018-01 250.00 and ACC-1018-02 65,361.13). The only press is good news (ART-6012, the export award). Earlier contact: meeting MTG-1005 (35 days ago) and an email with three years of accounts (20 days ago). The credit analysis of LAP-8003 is in the lending scenarios. |
| MTG-1003, 14:30 | Tobias Wrenfield (CUS-1011), yearly review. | Nothing new: no press, no application, no complaint, no contact note, no loans. Deposits 6,569.48 (ACC-1011-01), pension 29,676.74 in three funds (MEM-5001), total 36,246.22. |

MTG-1004 (10:00 tomorrow, Lanternfish Logistics) belongs to another manager, Bertil Ashgrove-Nye: a brief for Sunniva must not include it.

## Finance warehouse (system: finance)

Tables: `cost_centres` (8), `accounts` (11), `products` (6), `branches` (4) and `gl_monthly` (1,440 rows, 24 months, 2024-11 to 2026-10, USD, actual and budget). Operating cost is every account with `is_operating_cost = 1`: salaries, pension contributions, premises, technology, marketing and professional fees. Interest, fees and the loan impairment charge are not operating cost. Year to date is January to October 2026. Net interest income is interest income on loans (account 4100) minus interest expense on deposits (5100).

| Question | Right answer |
|---|---|
| Total operating cost last month (2026-10) against budget | Actual 2,743,079 against a budget of 2,666,664: 76,415 over, 2.87 percent. (Counting every expense account would give a higher and wrong number.) |
| The cost centre with the largest overspend year to date | CC300 Technology, 338,325 over budget (cloud and hosting, software licences and consultancy). Second is CC600 Marketing, 212,869 over, which is the largest in percent (12.09 against 5.31 for Technology). The cost centres under budget are CC200 Business Banking (-2,354) and CC700 Finance and Corporate (-4,388). Technology is also the largest in October alone (33,202), ahead of Operations (26,919). |
| Net interest income by month for the last six months | 2026-05 1,348,295. 2026-06 1,308,599. 2026-07 1,321,319. 2026-08 1,362,059. 2026-09 1,321,715. 2026-10 1,388,881. (For October: interest income 2,205,506 minus interest expense 816,625.) |
| A question the warehouse cannot answer | For example "What was the average headcount in Technology last month?" No table has headcount, staff numbers, customers or churn. The right answer is to say so and name what is missing. A query for a column that does not exist is refused with a readable 400. |

`run_finance_query` runs one SELECT. These are refused with 400 and change nothing: insert, update, delete, drop, create, attach, pragma, vacuum, a comment, a second statement after a semicolon, and a statement that does not start with SELECT or WITH. At most 200 rows come back.

## Equity research (system: research)

Invented companies on the Port Ilvane Securities Market (invented). Amounts are USD millions, per-share figures are cents. Annual results were published on 2026-03-31 and half-year results on 2026-08-21.

| Company | For | Right answer |
|---|---|---|
| RSC-6001 Kestrelmoor Foods plc | Clean results. | FY2025 revenue 842.3 (801.9 the year before, +5.0 percent), operating profit 96.8, profit 71.4, EPS 35.7, dividend 14.0. H1 2026 revenue 438.6 (415.2, +5.6 percent), operating profit 51.9, profit 38.6, EPS 19.3, interim dividend 7.0. Nothing restated. Consensus (updated 2026-09-05, after the filing) FY2026 revenue 880.0, EPS 37.3 (range 36.4 to 38.0). Filing and consensus agree. |
| RSC-6002 Tarnholt Marine Holdings plc | The half-year filing restates a figure from the annual filing. | The annual filing FIL-6103 says FY2025 revenue 412.6, operating profit 61.3, profit 44.0, EPS 22.0. The half-year filing FIL-6104 restates them: revenue 398.9, operating profit 52.9, profit 37.8, EPS 18.9. USD 13.7 million of charter income for voyages that finished in January 2026 moves into H1 2026. Net debt (205.4) and the dividend (9.0) are unchanged. The report must use the restated figures and say so. H1 2026 revenue 213.4 includes the 13.7 (199.7 without it, against 184.0). The share fell about 9 percent on 2026-08-21. |
| RSC-6003 Brindlewick Retail Group plc | Consensus and the filing disagree. | H1 2026 revenue 521.3 (548.0, -4.9 percent), operating profit 22.7 (36.4), EPS 7.1 (12.6), interim dividend cut from 6.0 to 4.0. The filing's outlook is revenue 1,020 to 1,060 and operating profit 55 to 62 for the full year. The consensus on file (updated 2026-08-09, 12 days before the filing) says revenue 1,150, operating profit 88.5 and EPS 30.2: above the top of the company's own range. It is stale. The report must say so, use the filing, and flag the consensus as not yet updated. The share fell about 27 percent on 2026-08-21 (4.31 to 3.15). |

A research report is a draft for an analyst to check. Every figure carries its source (a filing id of the same company, `consensus` or `prices`), and at least one point to check is required.

## Differences between records on purpose

- The legacy estate is separate from the core system: its customers and account numbers are not the core records.
- The change record ITC-8106 was first written with the plan time 22:00 and was corrected to the real time 14:02 (INC-7004). The record keeps both.
- The consensus for Brindlewick (RSC-6003) is older than its half-year filing, and the figures differ.
- The BAT-4002 control total (1,883.00) includes the rows that fail.
- The screening alert read side names a comparison `match`, `partial`, `differs` or `unknown`, and a recommendation names it `matches`, `partly_matches`, `differs`, `not_on_entry` or `noted`. The words differ on purpose: the first is what the system found, the second is what an agent says.
- Watchlist entries may leave place of birth or address empty where the list does not know it (WL-9004 has no address and a country of birth only, WL-9010, WL-9011 and the simulated entries have no address, WL-9014 has no place of birth).
- Valdis Orrenmoor (MTG-1001) appears in the news archive, in the screening system and in the crm system: each record is true on its own, and what a brief may say about each is different.

## Rules for checking

- The same customer id means the same customer in every system.
- Every transaction named in a monitoring alert exists on the alert's account.
- Account numbers and beneficiary IBANs have correct mod-97 check digits, except PAY-6101 on purpose.
- Changes (close an alert, release a repair, block a card, request a replacement, open a dispute, recall a payment, decide a fraud case, post a break resolution, decide an application, complete a review, send a complaint response, mark a call reviewed, post a contribution batch) are refused with 409 when a precondition fails.
- Drafts keep every version.
- `POST /admin/reset` returns all of this to the start. `POST /admin/reset/<system>` returns only what that one system has changed.

## Simulated arrivals

`POST /admin/simulate/<kind>` makes one new item from four rotating templates per kind. Right answers for these follow the same rules as above: screening-alert (new alerts with different match strengths), payment-repair (bad IBAN check digit, wrong BIC, no address, no purpose code), payment-investigation (late credit, short amount, return AC04, return AC01), loan-application (complete personal loan, business loan missing documents, personal loan missing the employment letter, business loan with all six documents).

Three more kinds arrive the same way, each from four rotating templates:

- fraud-case: (1) two online purchases in Norvania at night, but a contact note shows the customer is travelling there for work: not fraud, release. (2) an account takeover pattern (new device, password reset, new payee, payment within 45 minutes): true fraud, refund. (3) a USD 7.99 charge called fraud with three earlier payments to the same merchant: not fraud, a dispute. (4) a USD 22,000 first payment to a new payee that the business owner denies on the call-back: true fraud, block.
- reconciliation-break: (1) one mistyped character in the reference, value dates one day apart: match. (2) the statement is 12.50 below the ledger and names a charge of 12.50: match with an adjusting entry to GL-6120. (3) a duplicate ledger posting: reverse the later entry. (4) a statement item with nothing behind it: refer to a person.
- regulator-publication: see the table above.

Four more kinds, each from four rotating templates:

- onboarding-application: (1) individual, complete pack: approve. (2) individual whose identity card expired 20 days ago: ask the applicant. (3) company, one owner of 100 percent, complete: approve. (4) company half owned by Torvald Holdings Ltd (Rovaland) whose owners are in no document: gap, ask the applicant.
- kyc-review: (1) nothing changed (CUS-1003). (2) a new address, same rating (CUS-1005). (3) a new 30 percent owner in Kharnovia (CUS-1018): rating up, needs approval. (4) a new employer, same rating (CUS-1009).
- complaint: (1) a card replacement fee taken twice: uphold, refund one. (2) a card declined abroad by the fraud rule that worked as designed: not upheld. (3) written to nine working days ago and never acknowledged: admit it. (4) a customer who lost her job charged an overdraft fee: possible vulnerability, priority.
- collections-call: (1) clean call, exact promise. (2) call starts 20:25: CR-04 breached. (3) the caller says someone will come tonight and the customer will lose their home: CR-03 breached. (4) the customer says they have been ill and the hardship options are offered: no breach.

Four more kinds arrive the same way (kinds: incident, contribution-batch, client-meeting, monitoring-alert), each from four rotating templates:

- incident (opened 09:50, with 13 samples of metrics for the service and a runbook): (1) notification-service: the queue of messages grows from 12 to 960, receipts are late, no money is affected. (2) reporting-database: disk use rises from 61 to 93 percent because a nightly job kept its temporary files. (3) ledger-posting: an alert storm from rule LR-12 that reads a counter reset by a monitoring upgrade, while the service's own measures are normal. (4) mobile-gateway: login failures rise from 0.2 to 11 percent at 08:40 after a mobile app release at 08:30.
- contribution-batch (received today): (1) Harbourlight Services, 4 rows, all pass. (2) Stillwater Clinic, row 3 names member MEM-5077, who does not exist: rule 1. (3) Harbourlight Services, MEM-5003 appears twice: rule 3 on row 3. (4) Stillwater Clinic, row 2 has an employee amount of -137.50: rule 2.
- client-meeting (booked for tomorrow with Sunniva Haldane-Rook): (1) Isolde Pennywhistle (CUS-1016), who has a personal loan application in progress. (2) Anselm Drozdowich (CUS-1009), who has complaints. (3) Cassius Dunmore (CUS-1013), who has a home loan and a missed payment. (4) Lanternfish Logistics (CUS-1019), a routine check-in with nothing new.
- monitoring-alert (a new alert in the aml system, with its transactions): (1) four cash deposits of USD 9,250 to 9,700 in 6 days for Harrowgate Bakery Supplies (CUS-1017), total USD 38,000: structuring, open a case. (2) three credits of USD 26,000 to 31,500 from Brackenmere Holdings that each leave the next day to Vantor Trading, keeping about 1.17 percent, for Lanternfish Logistics (CUS-1019): pass-through, open a case. (3) three payments of USD 7,200 to Gallowmere Dental Supply in Kharnovia, total USD 21,600, for Orchard Lane Dental Group (CUS-1024), with a contact note that has the supply contract and invoices: higher-risk jurisdiction but explained, review and no case. (4) 13 outgoing payments in a month against an average of 8 for Pinecrest Tooling Works (CUS-1018), because suppliers are now paid monthly (a contact note says so): not suspicious, no case.
