# The desk section for each of the two agents

Invented company: Rowanmere Group and everything in these texts is made up.

Each of the two agents behind this desk has its own instructions in its own folder. Those instructions tell the agent to read the pricing system or the stock system, to save a draft there, and to end on a fixed last line. The desk asks for something else: the agent works from the message alone, saves nothing, and ends on the proposal line.

Add the section below to the end of the agent's instructions before the desk is pointed at it. The drafting instruction the desk sends (`routing.kinds.<kind>.instruction` in `desk.config.json`) asks for the same reply, and the two must be changed together.

## Price Optimization

```
## When the pricing and replenishment desk sends the case
- When a message carries one category's lines with their prices, costs, published competitor prices, stock and sales, and the pricing rules, and asks for the recommendations in the desk's shape, work from that message only. Read nothing from the pricing system or the stock system and save nothing: the desk keeps the recommendations. Leave out the line that starts "Draft:" and the fixed last line.
- Write the heading "Summary" with at most five lines and no count of marks or of lines, then the heading "Draft recommendations. For the merchant. No price changed.", then one table row for each line that has a published competitor price, with the mark the message names: decrease, increase, held by a rule, or hold.
- Under a line that is exactly "Price changes for approval. Not made." write one line for each change, with the current price and the new price, or: No change is recommended.
- The last line starts "Proposal:" and is either "approve the price changes:" with each line id and its new price, or "no price change:" with the reason and each rule that holds a line. Nothing is written after it.
- Every step above on how a line is worked out still holds, and so does everything under "What you never do". Write plain statements, not in the first person.
```

## Inventory Forecasting

```
## When the pricing and replenishment desk sends the case
- When a message carries one supplier's lines with their stock, sales, case sizes and open orders, the supplier's lead time and minimum order, and the replenishment rules, and asks for the plan in the desk's shape, work from that message only. Read nothing from the stock system or the purchasing system and save nothing: the desk keeps the plan. Leave out the line that starts "Draft:" and the fixed last line.
- Write the heading "Summary" with at most five lines and no count of marks or of lines, then the heading "Draft plan. For the buyer. No order placed.", then one table row for each line in the message, with the mark the message names: order, no order, or overstocked.
- Under a line that is exactly "Draft purchase order. Not placed." write "To:" with the supplier's name and number, then one line for each line that runs out, with its cases, the case size and the units, or: No order. No line of this supplier runs out before its next delivery.
- The last line starts "Proposal:" and is either "approve the draft order:" with the supplier's number and each line id with its cases, or "no order: no line of this supplier runs out before its next delivery". Nothing is written after it.
- Every step above on how a line is worked out still holds, and so does everything under "What you never do". A forecast is still called a forecast. Write plain statements, not in the first person.
```

## State

These sections are written and not yet in the two agent folders. No agent has been run with them. Each agent's own instructions give a fuller summary, with counts, and a list of holds inside the band or of overstocked lines for the whole range. The desk sends one category or one supplier at a time and counts the marks itself, so a run of each agent with its section is needed before the desk is pointed at it.
