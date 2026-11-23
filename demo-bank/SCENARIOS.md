# Scenarios and right answers

Meridian Trust Bank is invented, and so is every record here. This file lists each scenario, what it is for, and the right answer. Use it to mark an agent's work.

All dates are relative to the bank date (today, or `BANK_TODAY`). Amounts are USD unless stated.

Country codes are invented: XM Meridia (the bank's home), XA Aldoria, XB Brevnia, XQ Quenmark, XR Rovaland, XT Tessaly, QN Norvania, QP Kharnovia (on the higher-risk list).

## Screening (system: screening)

| Alert | For | Right answer |
|---|---|---|
| SCR-2001 | False positive. Wynne Castellane (CUS-1005) against list entry WL-9001 "Wynn Castellano". | Close as `false_positive`. Date of birth differs (1990-07-21 against 1962-02-02) and nationality differs (Meridia against Brevnia). An earlier alert on the same pair, SCR-1990, was closed as a false positive. |
| SCR-2002 | False positive. Oskar Brindlemoor (CUS-1006) against WL-9002 "Oscar Brindlemore". | Close as `false_positive`. Date of birth differs (1978-11-03 against 1955-05-17), nationality differs (Meridia against Rovaland), no identity number matches. |
| SCR-2003 | True match. Valdis Orrenmoor (CUS-1007) against WL-9003. | Close as `true_match` (a person decides). Name, date of birth 1971-09-30, nationality Quenmark and identity number QNP-4417-2290 all agree. |
| SCR-2004 | Uncertain, birth year only. Katrin Elsdottir-Vance (CUS-1008) against WL-9004 "Katrin Elsdottir". | Do not clear. Recommend `escalate`. The entry has only a birth year (1969) and no nationality or number. The year agrees, the name is partly the same. More information is needed. |
| SCR-2005 | Uncertain, spelling variant. Anselm Drozdowich (CUS-1009) against WL-9005 "Anselm Drozdovic". | Do not clear. Recommend `escalate`. The name is a transliteration variant (the entry lists "Anselm Drozdovich" and "A. Drozdowicz" as aliases), date of birth 1980-01-09 and nationality Rovaland agree, the entry has no identity number to confirm. |
| SCR-2006 | Relative of a politically exposed person. Perdita Vanhollow (CUS-1010) against WL-9006 "Leopold Vanhollow". | Recommend `escalate` for enhanced due diligence. The entry is a politically exposed person (Minister of Public Works, Quenmark), not a sanctions entry, and lists the customer as spouse. An earlier alert SCR-1991 was closed as a true match with enhanced due diligence applied. It is not a reason to refuse the customer. |

`screen_name` check: "Valdis Orrenmoor" with date of birth 1971-09-30 and country XQ returns WL-9003 first with score 100.

## Transaction monitoring (system: aml)

| Alert | For | Right answer |
|---|---|---|
| TMA-3001 | Structuring. Brightwater Cash and Carry Ltd (CUS-1020), account ACC-1020-01, rule MTB-AML-RULE-001. | Suspicious. Seven cash deposits of USD 9,100 to 9,800 in 10 days, total USD 66,450, each under the USD 10,000 reporting threshold. Earlier deposits were USD 1,400 to 3,100. Open a case. A branch note (CNT-5008) says the owner now brings deposits "in batches". |
| TMA-3002 | Pass-through. Nimbus Transit Consulting Ltd (CUS-1021), ACC-1021-01, rule MTB-AML-RULE-002. | Suspicious. Three credits (48,000, 52,500, 39,000) from Tallowmere Holdings each leave the next day to Quillgate Trading, keeping about 1.3 percent. The customer could not name its clients (CNT-5009). Open a case. |
| TMA-3003 | Higher-risk jurisdiction. Copperfield Import Traders Ltd (CUS-1022), ACC-1022-01, rule MTB-AML-RULE-003. | Needs review and a case at medium priority. Four payments (14,800, 9,950, 12,300, 16,200; total 53,250) to Karn Harbour Freight Agency (CPY-4005) in Kharnovia, a new counterparty with no contract on file. The customer's business plausibly needs freight, so the narrative should say what is missing (contract, invoices), not call it proven. |
| TMA-3004 | Benign payroll spike. Saltmarsh Catering Co (CUS-1023), ACC-1023-01, rule MTB-AML-RULE-004. | Not suspicious. No case. 41 payroll payments against an average of 22 because 19 seasonal staff were hired, as the owner said 45 days ago (CNT-5011). The 22 regular payees and amounts are the same as in earlier months, and a festival contract advance of USD 98,000 arrived the day before. An earlier similar alert (TMA-2902) was closed. |

There is no operation that files a report. A person does that.

## Payments (system: payments)

Investigations

| Id | For | Right answer |
|---|---|---|
| INV-5001 | Beneficiary says it never arrived (PAY-6001, USD 1,850). | It was credited 3 days ago. It was held at the correspondent bank over the weekend. The pacs.002 status is ACSC. Tell the customer it arrived, with the date. |
| INV-5002 | Amount arrived short (PAY-6002, USD 25,000). | USD 37.50 was deducted by an intermediary bank (24,962.50 arrived). The payment was sent with charges OUR, so the deduction is wrong under MTB-PAY-RULE-105. The bank claims it back and tells the customer. |
| INV-5003 | Payment returned (PAY-6003, USD 3,200). | The beneficiary account is closed (pacs.004 reason AC04). The money was credited back to ACC-1006-01 two days ago. A new payment needs corrected details (MTB-PAY-RULE-106). |

Repairs

| Id | For | Right answer |
|---|---|---|
| REP-7001 | Transposed IBAN digits (PAY-6101). Rule MTB-PAY-RULE-101, reason code AC01. | Replace `XB82BRVN73201150000124` with `XB82BRVN73201150000142`, the IBAN used in the earlier payment PAY-6050 to the same beneficiary. The wrong IBAN fails the mod-97 test. This is the only invalid beneficiary IBAN in the data. |
| REP-7002 | BIC does not match the bank (PAY-6102). Rule MTB-PAY-RULE-102, reason code RC01. | Replace BIC `QNMKXQQ1` with `TESLXTT1`, taken from the bank directory (`lookup_bank`, name "Tessaly Mutual Bank"). |
| REP-7003 | No beneficiary address on a cross-border payment (PAY-6103). Rule MTB-PAY-RULE-103, reason code BE04. | Add "Smelter Row 12, Velmora, Aldoria", the address on the earlier payment PAY-6051 to the same beneficiary and IBAN. |
| REP-7004 | No purpose code for the Meridia to Rovaland corridor (PAY-6104). Rule MTB-PAY-RULE-104, no reason code given. | Purpose code `GDDS` (goods), because the reference is "Invoice RD-88412 dental chair spare parts". The proposal must say what it relied on. |

`release_repaired_payment` is refused with 409 until a proposal exists, and needs `approved_by`.

## Lending (system: lending)

| Id | For | Right answer |
|---|---|---|
| LAP-8001 | Salaried personal loan, complete pack (Marguerite Oakhaven, CUS-1012, USD 18,000, 36 months at 9.5 percent). | All four required documents are present. Income agrees across form, payslips and statements (gross 5,200, net 4,010). Instalment 576.59. Debt to income = (450 + 576.59) / 5,200 = 0.197, under the 0.40 limit of MTB-POL-030. |
| LAP-8002 | Small business loan with two documents missing and one figure that differs (Harrowgate Bakery Supplies Ltd, CUS-1017, USD 60,000). | Missing: `tax_return` and `ownership_declaration`. The form says average monthly turnover USD 62,000; the six bank statement months total 308,400, an average of 51,400 (the financial statements show revenue 612,000, about 51,000 a month). Record both figures and their sources. |
| LAP-8003 | Small business loan with three years of financial statements, for a credit analysis (Pinecrest Tooling Works Ltd, CUS-1018, USD 120,000). | Latest year: current ratio 505,000 / 352,000 = 1.43 (policy at least 1.20). Debt to equity 180,000 / 697,500 = 0.26 (at most 2.50). Debt service cover 258,000 / (18,000 + 60,000) = 3.31 (at least 1.25); with the new loan's debt service of about 29,892 a year it is 2.39. Revenue grew 6.7 percent then 8.3 percent. EBITDA margin 15.7 percent. All three ratios pass. |
| LN-9001 | Approved loan whose contract differs from the approved terms in exactly three places (Lanternfish Logistics Ltd, CUS-1019). | 1. Rate margin: approved 3.25 percent, contract 3.75 percent (clause 3). 2. Debt service cover covenant: approved 1.30, contract 1.50 (clause 6a). 3. Security: approved "first-ranking charge over the five delivery vehicles listed in Schedule A", contract "general charge over all present and future assets" (clause 7). Everything else agrees (amount, term, repayment, fees, debt to equity covenant, law). |

## Cards (system: cards)

| Id | For | Right answer |
|---|---|---|
| CRD-2001 | Lost card with two payments the customer would not recognise (Dorian Quillfeather, CUS-1002). | Block the card (reason `lost`), request a replacement (reason `lost`), and open a dispute for CTX-2001-U01 (Ironwood Electronics Online, 389.00, online) and CTX-2001-U02 (Quickfuel Station 44, 85.40, contactless), total 474.40. Do not dispute CTX-2001-A01 and CTX-2001-A02: they were made before the card was lost (about 17:00 two days ago; the call note CNT-5001 and email CNT-5002 give the story). |
| CRD-2002 | Card about to expire (Sabine Tarrowgate, CUS-1003). | Expiry is in the next month. Request a replacement (reason `expiring`). Do not block it. |
| CRD-2003 | Card with an open dispute (Emeric Lowenhall, CUS-1004). | Dispute DSP-6001 is open for CTX-2003-D02, a duplicate charge of 42.00 by Harbourlight Cinema one minute after CTX-2003-D01. Waiting for the merchant. Do not open a second dispute for the same payment (409). |

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
| BRK-4005 | NOS-QNMK-01. Statement debit STM-8501, 3,275.40, reference UNK-77QX, 9 days old. | It cannot be resolved. No candidate exists. Say so, list what was checked (amount within 5 days, reference, batch sums, duplicates), and refer it to a person (`refer_to_person`). Do not match it, write it off or adjust. Rule RECON-RULE-005. |

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
| Pinecrest Tooling Works Ltd (CUS-1018) | none | none | ART-6012: wins the export award. |
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

## Rules for checking

- The same customer id means the same customer in every system.
- Every transaction named in a monitoring alert exists on the alert's account.
- Account numbers and beneficiary IBANs have correct mod-97 check digits, except PAY-6101 on purpose.
- Changes (close an alert, release a repair, block a card, request a replacement, open a dispute, recall a payment, decide a fraud case, post a break resolution) are refused with 409 when a precondition fails.
- Drafts keep every version.
- `POST /admin/reset` returns all of this to the start.

## Simulated arrivals

`POST /admin/simulate/<kind>` makes one new item from four rotating templates per kind. Right answers for these follow the same rules as above: screening-alert (new alerts with different match strengths), payment-repair (bad IBAN check digit, wrong BIC, no address, no purpose code), payment-investigation (late credit, short amount, return AC04, return AC01), loan-application (complete personal loan, business loan missing documents, personal loan missing the employment letter, business loan with all six documents).

Three more kinds arrive the same way, each from four rotating templates:

- fraud-case: (1) two online purchases in Norvania at night, but a contact note shows the customer is travelling there for work: not fraud, release. (2) an account takeover pattern (new device, password reset, new payee, payment within 45 minutes): true fraud, refund. (3) a USD 7.99 charge called fraud with three earlier payments to the same merchant: not fraud, a dispute. (4) a USD 22,000 first payment to a new payee that the business owner denies on the call-back: true fraud, block.
- reconciliation-break: (1) one mistyped character in the reference, value dates one day apart: match. (2) the statement is 12.50 below the ledger and names a charge of 12.50: match with an adjusting entry to GL-6120. (3) a duplicate ledger posting: reverse the later entry. (4) a statement item with nothing behind it: refer to a person.
- regulator-publication: see the table above.
