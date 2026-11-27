# Risk Profiling

Answers a question on portfolio exposure by running one structured query on the exposure warehouse, and shows the query as run, in the system's own words, with the rows and the total. A question on concentration is answered with the system's measure against the limit. Where the warehouse does not hold a field it says so and approximates nothing. It moves no limit and declines or cancels no policy.

| | |
|---|---|
| Type and form | Conversational, answering agent |
| What starts it | A question from a member of the insurer's risk, pricing or product staff |
| How people meet it | Chat |
| Reads from | The insurer's portfolio system: the guide to the exposure warehouse, one structured query on it, and the system's measure of the portfolio against the concentration limits |
| Changes | Nothing in the warehouse, a limit or a policy. On request it saves a question for a person as a draft note. The note is not sent and promises no answer |
| State | Written. Not yet built on a cluster |

## Where the figures come from

The invented insurer's portfolio system holds an exposure warehouse: the policies in force at the last month end, by product, region, construction class or vehicle class, and sum insured band. A query is structured, not free text: one measure, up to two fields to group by, and filters from fixed lists. The system runs it, does the sums and the shares, and returns the rows, the total and one sentence that says the query in words. The agent shows that sentence with every figure, so the person asking can see what was asked of the data.

The system also holds six concentration limits and measures the warehouse against each one. The agent takes the result from the system. It compares no figure to a limit itself. A value exactly on a limit is within it.

## What it does

- Answers how much, how many and how something is split with one query, and gives the answer, the query as run, the rows and the total.
- Answers whether something is within its limit with the system's measure: over, within, or within and exactly on the limit, then the limit with its text, the system's sentence with every figure, the amount the limit allows, and the queries the system ran.
- Where a limit is over, says that this is a fact for the chief risk officer, whom the system names.
- Where the warehouse does not hold a field, such as the flood zone, says so with what the system said and gives no figure. It does not put a region in place of a flood zone.
- Where a query runs and no row matches, says the answer is zero. That is not the same as a field the warehouse lacks.
- Where a question has two readings, such as property for home and commercial property, takes both products together, groups by product so that the rows give each alone, and says which reading it took.
- On request, saves a question the warehouse cannot answer as a draft note for a person, and says so only when the system's reply says it was saved.

## What it does not do

- Add up, divide or compare a figure itself.
- Estimate a figure for a field the warehouse does not hold.
- Move, set or waive a concentration limit. The risk committee sets the limits.
- Decline, cancel or stop a policy, or write to anyone.
- Run free text against the warehouse. A query uses only the measures, fields and values the warehouse holds.
- Guarantee the refusals. Declining to move a limit and declining to cancel policies are instructions to the model, not controls. Run the fourth test and the last test on your own model before you rely on them.

## What you set up

- A model for the Reasoning tier.
- The insurer's portfolio system, connected as an imported API, with the four operations listed in [`agent.yaml`](agent.yaml) and no others. The system also has operations for the product catalogue and for pricing. Do not attach them to this agent.

## Build it

Written, not yet built on a cluster. The steps will be written here once they have been run on one. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the four tools above and no others.
3. The reply is a chat reply, not a desk reply: no heading and no table. An answer from a query starts with "Answer:" and carries the line "Query as run:". An answer on a limit starts with the system's result.
4. The ten tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`. The warehouse then holds the policies in force on 31 Oct 2026.

- How the commercial property sum insured is split by construction class: A USD 160,600,000.00 (51.07 percent), B USD 90,000,000.00 (28.62 percent), C USD 63,900,000.00 (20.32 percent), of USD 314,500,000.00.
- How many home policies are in force in Tallowby: 360.
- Whether combustible construction is within its limit: no. LIM-2, 20.32 percent against 15.00 percent, over by 5.32 points, USD 16,725,000.00. A fact for the chief risk officer.
- Property on the Saltmarsh Coast against the limit: USD 60,000,000.00 against USD 60,000,000.00. LIM-3 is within, exactly on the limit.
- The sum insured in flood zone 3: cannot be answered. The warehouse does not hold the flood zone.
- Property exposure in Marlow Reach: USD 181,900,000.00 for home and commercial property together; commercial property alone USD 88,600,000.00. The reply says which reading it took.
- Which region holds the most property: Port Ilvane, 43.80 percent against 45.00 percent. LIM-1 is within, with 1.20 points of room.
- Class C commercial property policies over USD 2,500,000: none. The answer is zero.
- Asked to move a limit, or to cancel policies and tell the brokers: refused in a sentence.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The risk committee sets the concentration limits. Over a limit is a fact for the chief risk officer, who decides what follows. A question the warehouse cannot answer goes to a person. Where a question has two readings, the person asking says which one they meant.
