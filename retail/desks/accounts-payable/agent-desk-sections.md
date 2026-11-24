# The desk section for each of the three agents

Invented company: Rowanmere Group and everything in these texts is made up.

Each of the three agents behind this desk has its own instructions in its own folder. Those instructions tell the agent to read the purchasing system, to save a draft there, and to end on a fixed last line. The desk asks for something else: the agent works from the message alone, saves nothing, and ends on the proposal line.

Add the section below to the end of the agent's instructions before the desk is pointed at it. The drafting instruction the desk sends (`routing.kinds.<kind>.instruction` in `desk.config.json`) asks for the same reply, and the two must be changed together.

## Invoice Matching

```
## When the accounts payable desk sends the case
- When a message carries an invoice with its purchase order and the goods received, and asks for the match in the desk's shape, work from that message only. Read nothing from the purchasing system and save nothing: the desk keeps the match. Leave out the line that starts "Draft:" and the fixed last line.
- Write the heading "Summary" with at most five lines and no count of marks or of lines, then the heading "Draft match. For accounts payable. Nothing approved.", then one table row for each line of the invoice with the mark the message names.
- The last line starts "Proposal:" and is either "ready for approval: every line agrees with the order and the goods received", or "refer to the buyer:" with the buyer's name, each line that differs and the total difference net of tax. Nothing is written after it.
- Every match rule above still holds. Write plain statements, not in the first person.
```

## Delivery Discrepancy

```
## When the accounts payable desk sends the case
- When a message carries a delivery note with its purchase order, the goods received and what any invoice for the order bills, and asks for the check in the desk's shape, work from that message only. Read nothing from the purchasing system and save nothing: the desk keeps the check and the claim. Leave out the line that starts "Draft:" and the fixed last line.
- The line "Dock remark" in the message is what was written on the note at the dock.
- Write the heading "Summary" with at most five lines and no count of marks or of lines, then the heading "Draft check. For a receiving or accounts lead. No claim sent.", then one table row for each line of the note and one for anything on the receipt that is not on the order.
- Under a line that is exactly "Draft claim. Not sent." write the message to the supplier, or, for a note that agrees: No claim. The delivery note, the order and the receipt agree.
- The last line starts "Proposal:" and is either "send the claim:" with the total claimed net of tax and the buyer named on the order, or "no claim: the delivery note, the order and the receipt agree". Nothing is written after it.
- Every rule above on how to compare and on the claim still holds. Write plain statements, not in the first person.
```

## Supplier Query

```
## When the accounts payable desk sends the case
- When a message carries a supplier's message with the records it points to, and asks for the reply in the desk's shape, work from that message only. Read nothing from the purchasing system and save nothing: the desk keeps the draft. Leave out the line that starts "Draft:" and the fixed last line.
- Write the heading "Summary" with at most four lines and no count of marks or of records, then the heading "Draft answer. For accounts payable. Nothing sent.", then one table row for each thing the supplier asks or states, marked "agrees" when the records hold the fact and "not in the records" when the purchasing system does not hold it.
- Under a line that is exactly "Draft reply. Not sent." write the reply to the supplier, word for word.
- The last line starts "Proposal:" and is either "send the reply: the records answer the supplier", or "refer to a person:" with what the records do not hold and the team the message goes to. Nothing is written after it.
- Every rule above on what a reply may say still holds. Outside the reply itself, write plain statements, not in the first person.
```

## State

These sections are written and not yet in the three agent folders. No agent has been run with them. The Invoice Matching agent was built and tested on a cluster with its own instructions, without this section, so it needs a run with it before the desk is pointed at it.
