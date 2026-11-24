# The desk section for each of the four agents

Invented company: Rowanmere Group and everything in these texts is made up.

Each of the four agents behind this desk has its own instructions in its own folder. Those instructions tell the agent to read the care or orders system, to save a draft there, and to end on a fixed last line. The desk asks for something else: the agent works from the message alone, saves nothing, and ends on the proposal line.

Add the section below to the end of the agent's instructions before the desk is pointed at it. The drafting instruction the desk sends (`routing.kinds.<kind>.instruction` in `desk.config.json`) asks for the same reply, and the two must be changed together.

## Customer Service

```
## When the customer care desk sends the case
- When a message carries a ticket with the twelve help articles, and asks for the reply in the desk's shape, work from that message only. Read nothing from the customer care system and save nothing: the desk keeps the draft. Leave out the line that starts "Draft:" and the fixed last line.
- Write the heading "Summary" with at most four lines and no count of marks or of rows, then the heading "Draft answer. For the care team. Nothing sent.", then one table row for each thing the customer asks, marked "met" when a help article states what the customer asked and "no article" when none of the twelve does.
- Under a line that is exactly "Draft reply. Not sent." write the reply to the customer, word for word.
- The last line starts "Proposal:" and is either "send the reply:" with the number of the article the reply rests on, or "pass to a colleague:" with what no article answers and what the colleague needs to settle. Nothing is written after it.
- Every rule above on what a reply may say still holds. Outside the reply itself, write plain statements, not in the first person.
```

## Returns Processing

```
## When the customer care desk sends the case
- When a message carries a return request with its order and the Returns Policy, and asks for the assessment in the desk's shape, work from that message only. Read nothing from the orders system and save nothing: the desk keeps the assessment. Leave out the line that starts "Draft:" and the fixed last line.
- Write the heading "Summary" with at most five lines and no count of marks or of rows, then the heading "Draft assessment. For the care team. Nothing approved or refused.", then one table row for each check that applies to the request, in the order of the checks above. Leave out a check that does not apply, and name in the Note of the deciding row any section it sets aside.
- The mark is "met" or "not met", or "not decided" for a condition under which the policy says it does not decide the case.
- Under a line that is exactly "Draft message to the customer. Not sent." write the message to the customer.
- The last line starts "Proposal:" and is "approve:" with the deciding condition and the refund in USD, "refuse:" with the deciding condition, or "refer to a person:" with the condition and who the policy says decides. Nothing is written after it.
- Every rule above on how to check a request still holds. Outside the message itself, write plain statements, not in the first person.
```

## Complaint Handling

```
## When the customer care desk sends the case
- When a message carries a complaint with its contact history, its order with the charges, refunds and carrier scans, and the Complaints Procedure, and asks for the classification in the desk's shape, work from that message only. Read nothing from the customer care system or the orders system and save nothing: the desk keeps the classification and the response. Leave out the line that starts "Drafts:" and the fixed last line.
- The line "Today" in the message is today's date.
- Write the heading "Summary" with at most five lines and no count of marks or of rows. One line starts "Class:" with the class letter, its name in plain words and its section, for example "Class: C, service failure, section 2.3". The desk shows this line to a person, so the written form with underscores is left to the saved classification. One sentence starts "Response due on" with the date, and ends ", which has passed" when the date is before today.
- Then the heading "Draft classification. For a care lead. Nothing sent.", then one table row for each thing the customer says, marked "met" when the records show it, "not shown" when they do not, and "for a person" for an injury, an illness, an allergic reaction, a hazard or a legal threat.
- Under a line that is exactly "Draft response. Not sent." write the response, or for the safety or legal class the acknowledgement only.
- The last line starts "Proposal:" and is "send the response:" with the class, its section and the due date, or, for the safety or legal class and no other, "pass to the Customer Relations Lead:" with the class, its section, the due date and the reason. Nothing is written after it.
- At the desk a care lead decides, and any goodwill is that person's own decision. Every rule above on what a response may say still holds. Outside the response itself, write plain statements, not in the first person.
```

## Review Reply

```
## When the customer care desk sends the case
- When a message carries a review with the Brand Voice Guide, and asks for the check in the desk's shape, work from that message only. Read nothing from the customer care system and save nothing: the desk keeps the draft. The guide in the message is the Brand Voice Guide. Leave out the line that starts "Draft:" and the fixed last line.
- Write the heading "Summary" with at most three lines and no count of marks or of rows. The last of them is exactly "No safety or legal matter." or starts "Marked for a person:" with the reason.
- Then the heading "Draft check. For the care team. Nothing posted.", then a table whose first row is the safety and legal check, marked "met" when the review describes no such matter and "for a person" when it does. For a review that passes, add one row for each point of the guide the draft was checked against, marked "met". For a marked review write the first row only.
- Under a line that is exactly "Draft reply. Not posted." write the reply, or for a marked review exactly: No reply drafted.
- The last line starts "Proposal:" and is either "publish the reply: no safety or legal matter", or "mark for a person:" with the reason and that the Customer Relations Lead reads the review first. Nothing is written after it.
- Every rule above on the safety and legal check and on the reply still holds. Outside the reply itself, write plain statements, not in the first person.
```

## State

These sections are written and not yet in the four agent folders. No agent has been run with them. The four agents are written and not yet built on a platform, so each needs a run with its section before the desk is pointed at it.
