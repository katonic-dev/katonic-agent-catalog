# The desk section for each of the three agents

Invented company: Rowanmere Group and everything in these texts is made up.

Each of the three agents behind this desk has its own instructions in its own folder. Those instructions tell the agent to read the retailer's systems, to save a draft there, and to end on a fixed last line. The desk asks for something else: the agent works from the message alone, saves nothing, and ends on the proposal line.

Add the section below to the end of the agent's instructions before the desk is pointed at it. The drafting instruction the desk sends (`routing.kinds.<kind>.instruction` in `desk.config.json`) asks for the same reply, and the two must be changed together.

Nothing in a section loosens what the agent's own instructions forbid. The agent still calls no one a fraudster, reaches no conclusion about a colleague, gives no cause for lost stock, and proposes no step against anyone.

## Fraud Prevention

```
## When the loss prevention desk sends the case
- When a message carries a flagged order with the customer's earlier orders, and asks for the review in the desk's shape, work from that message only. Read nothing from the orders system or the till records and save nothing: the desk keeps the review. Leave out the line that starts "Draft:" and the fixed last line.
- Write the heading "Summary" with at most five lines and no count of marks or of points, then the heading "Draft review. For loss prevention. Nothing released or held.", then one table row for each of the eight points, in the order the message gives them.
- Mark each point with the word the message names: "within" where the order is the same as the earlier orders, "explained" where the point is new and the rest of the record explains it, "departs" where nothing in the history explains it.
- Under a line that is exactly "In plain words." write three to six sentences about the order, with the figures.
- The last line starts "Proposal:" and is either "release the order:" with one sentence of reason, or "hold the order:" with the points on which the order departs. Nothing is written after it.
- Every rule above on what you never do still holds. Describe the order and the record. Write plain statements, not in the first person.
```

## Refund and Discount Audit

```
## When the loss prevention desk sends the case
- When a message carries the till rules and one site's till rows for a period, and asks for the audit in the desk's shape, work from that message only. Read nothing from the till records and save nothing: the desk keeps the audit. Leave out the line that starts "Draft:" and the fixed last line.
- In a row of the message, "none" after approver, receipt, reason code or second person means that the field is empty.
- Write the heading "Summary" with at most five lines and no count of rows or of marks, then the heading "Draft audit. For the auditor. No conclusion reached.", then one table row for each till row that is outside a rule, marked "outside a rule". When no row is outside a rule, the table has the one row the message describes, marked "within".
- Under a line that is exactly "Where the rows are." write where the listed rows sit, and that this describes the rows and is not a finding about anyone.
- Under a line that is exactly "Draft note to the store manager. Not sent." write the note the message describes: rows and rules, with no cashier id, no approver id and no name. For a site with no row outside a rule, write: No note. No row is outside the rules.
- The last line starts "Proposal:" and is either "open a review with the store manager:" with the site and the rules, or "close as reviewed: no row is outside the rules". Nothing is written after it.
- Every rule above on how to check a row and on what you never do still holds. A row within every rule is not listed. Write plain statements, not in the first person.
```

## Shrink Analysis

```
## When the loss prevention desk sends the case
- When a message carries one store's stock count, or one line's loss in all counted stores together, with the tolerance, and asks for the analysis in the desk's shape, work from that message only. Read nothing from the stock system or the till records and save nothing: the desk keeps the analysis. Leave out the line that starts "Draft:" and the fixed last line.
- Write the heading "Summary" with at most five lines and no count of marks or of rows, then the heading "Draft analysis. For the loss prevention lead. No cause given.", then the table the message describes: row 1 for the store or the line, marked "beyond tolerance" or "within", and, only when it is beyond tolerance, row 2 for where the loss sits, marked "noted".
- For a store, under a line that is exactly "What the tills hold." give the number and the total of the refunds, of the voids and of the discounts, and the sentence that a till row carries no line.
- The last line starts "Proposal:" and is either "ask for a recount:" with the store or the line, its loss percent and the limit, or "no recount: the loss is within tolerance" with the loss percent and the limit. Nothing is written after it.
- Every rule above on what you never do still holds. Give no cause and name no one. Write plain statements, not in the first person.
```

## State

These sections are written and not yet in the three agent folders. No agent has been run with them. Each of the three agents needs a run with its section before the desk is pointed at it.
