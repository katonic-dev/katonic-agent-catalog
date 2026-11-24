# Policy library of an invented company

Rowanmere Group does not exist. These nine documents were written so that agents in this pack have something to read, cite and compare against. Each one says on its first line that the company is invented. Amounts are US dollars.

| File | Document | Used by |
|---|---|---|
| `staff-handbook.md` | Staff Handbook, version 2.4 (clauses HR-01 to HR-07) | Staff Policy Q&A |
| `store-procedures-manual.md` | Store Procedures Manual, version 3.1 (procedures SP-01 to SP-18) | Store Procedures Q&A |
| `allergen-matrix-v4.1.md` | Allergen Matrix and Menu Specifications, version 4.1 (rows A-01 to D-05) | Menu and Allergen Q&A |
| `food-safety-plan-v5.0.md` | Food Safety Plan, version 5.0 (sections 1 to 7) | Food Safety Record Check, which also reads the same plan through the invented retailer's food safety system |
| `brand-standards-v2.0.md` | Brand Standards, version 2.0 (standards BS-1 to BS-8, written on a visit checklist as BS-1.1 to BS-8.2) | Store Visit Report, which reads the visits themselves through the invented retailer's stores system |
| `returns-policy-v3.0.md` | Returns Policy, version 3.0 (conditions 1.1 to 6.2) | Returns Processing, which also reads the same policy through the invented retailer's orders system |
| `help-articles.md` | Help Articles of the online shop (articles HA-01 to HA-12) | Customer Service, which also reads the same articles through the invented retailer's care system |
| `complaints-procedure-v2.1.md` | Complaints Procedure, version 2.1 (sections 1 to 5, classes A to D) | Complaint Handling, which also reads the same procedure through the invented retailer's care system |
| `brand-voice-guide.md` | Brand Voice Guide, version 1.2 (rules V-1 to V-13) | Review Reply. The invented retailer does not serve it |

## How to use them

In Knowledge, choose Connect Source, then File Upload, and add the files. Indexing needs an embedding model. Give each knowledge agent its own source: the handbook for Staff Policy Q&A, the manual for Store Procedures Q&A, the matrix for Menu and Allergen Q&A. Keeping them apart is what lets each agent say that a question belongs to another document.

## What is left out on purpose

So that an agent can be tested on what it does when the documents are silent:

- The Guest Recovery Policy. Procedure SP-07 clause 7.6 and SP-09 clause 9.2 point to it, and it is not in the library.
- The disciplinary procedure, which the handbook says is a separate document.
- The speak-up line number. Clause 7.2 of the handbook says it is on the notice board.
- Any dish that is not a row of the allergen matrix.
