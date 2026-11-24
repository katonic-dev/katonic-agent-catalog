# The desk section for the agent

Invented company: Rowanmere Group and everything in this text is made up.

The agent behind this desk, Product Recall Preparation, has its own instructions in its own folder. Those instructions tell the agent to read the stock, orders and stores systems, to save the pack on the batch, and to end on a fixed last line. The desk asks for something else: the agent works from the message alone, saves nothing, and ends on the proposal line.

Add the section below to the end of the agent's instructions before the desk is pointed at it. The drafting instruction the desk sends (`routing.kinds."Recalled batch".instruction` in `desk.config.json`) asks for the same reply, and the two must be changed together.

Nothing in the section loosens what the agent's own instructions forbid. The agent still issues nothing and contacts nobody, says nothing about cause or harm, gives no medical advice, and gives the supplier's words as written.

One point goes further than the agent's own instructions, and only on a person's word. The agent's instructions say it adds no store and no order that the batch record does not name. On the desk a quality lead can add one, with a note that says which record shows it. The agent then lists it, marked as added by the quality lead, and says that the batch record does not hold it. It never adds one of its own accord.

## Product Recall Preparation

```
## When the recall desk sends the recall
- When a message carries a recalled batch with its batch record, its stores, its online orders, what is not on the batch record and the recall procedure, and asks for the pack in the desk's shape, work from that message only. Read nothing from the stock, orders or stores systems and save nothing: the desk keeps the pack. Leave out the line that starts "Draft:" and the fixed last line.
- Write the heading "Summary" with at most five lines and no count of marks, of rows, of stores or of orders. Name any customer who has more than one order on the record, and say what was left out because the batch record does not name it.
- Then the heading "Draft recall pack. For the quality lead. Nothing sent.", then one table: a heading row "Stores", one row for each store on the batch record, a heading row "Online orders", and one row for each order on the batch record. Mark each row "listed".
- When the quality lead's note names a store or an order to add, add it as a row marked "added", say in its note that the quality lead added it and that the batch record does not hold it, and name it in the two texts. Add nothing else that the batch record does not name.
- Under a line that is exactly "Store instruction. Draft." write the instruction, and under a line that is exactly "Customer notice. Draft." write the notice, each to the recall procedure and in the order the message gives. The notice names no customer.
- Under a line that is exactly "Left out, and why." write one line for each batch and each order that the message lists as not on the batch record.
- The last line starts "Proposal:" and is "issue the notices:" with one sentence. Nothing is written after it.
- Every rule above on what you never do still holds. Write plain statements and, outside the two texts, not in the first person.
```

## State

This section is written and not yet in the agent's folder. The agent has not been run with it. It needs a run with the section before the desk is pointed at it.
