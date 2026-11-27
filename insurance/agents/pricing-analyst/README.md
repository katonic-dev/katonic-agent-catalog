# Pricing Analyst

Answers a pricing question on a segment with the pricing system's own calculation: the loss ratio, or the premium change that holds a target loss ratio, with every assumption named with its value and whose it is, the working, and the credibility check. Where a segment has too few claims it says the figure is not reliable and why. It works out no number itself, recommends no rate and files nothing.

| | |
|---|---|
| Type and form | Conversational, answering agent |
| What starts it | A question from a member of the insurer's pricing, product or risk staff |
| How people meet it | Chat |
| Reads from | The insurer's portfolio system: the pricing method, the pricing segments, the experience and loss ratios of a segment, and the system's calculation of the premium change that holds a target loss ratio |
| Changes | Nothing in a rate, the method or the experience. On request it saves a question for a person as a draft note. The note is not sent and promises no answer |
| State | Written. Not yet built on a cluster |

## Where the figures come from

The invented insurer's portfolio system holds a pricing method of eight numbered rules and the experience of six pricing segments over three complete accident years. The system does every sum: the loss ratio of a year and of the years together, the trend factor, the trended loss ratio, the premium change, the premium needed, the credibility and a table of sensitivity. Each figure comes back with its working as a sentence, and each assumption comes back with its value and where it came from. The agent sends the values the question gives, leaves out the ones it does not give, and lays the answer out. A model that divides or compounds in its head gets a different second decimal from run to run. This agent does not divide.

## What it does

- Finds the segment by its id, or by its name in the list of pricing segments.
- For a loss ratio, gives the ratio of the years together and of each year, each with the system's working.
- For a premium change, gives the change needed to hold the target, every assumption with its value and whose it is (the asker's own, or the insurer's standard), the system's working step by step, and four figures of sensitivity.
- Gives the credibility check with every answer, in the system's own sentence.
- Where a segment has too few claims, says in the first line that the figure is not reliable alone, gives the reason, shows the figure the system returns marked so, and says the pricing actuary decides what to set beside it.
- Where the target is already met, says that no change is needed and that the method works out no decrease.
- Where the experience does not hold a year or a split, says so with what the system said and estimates nothing. On request it saves the question as a draft note for the pricing actuary.
- Ends every answer with one sentence: an indication, not a rate.

## What it does not do

- Work out a figure itself, or fill in an assumption the question did not give.
- Set, recommend, approve or file a rate. The pricing actuary signs off a rate change and the product committee approves it.
- Work out or suggest a decrease.
- Give a figure for a year, a split or a segment the experience does not hold.
- Change the pricing method, its standard assumptions or the experience.
- Guarantee the refusals. Declining to set a rate and declining to change the method are instructions to the model, not controls. Run the third test and the last test on your own model before you rely on them.

## What you set up

- A model for the Reasoning tier.
- The insurer's portfolio system, connected as an imported API, with the five operations listed in [`agent.yaml`](agent.yaml) and no others. The system also has operations for the product catalogue and for the exposure warehouse. Do not attach them to this agent.

## Build it

Written, not yet built on a cluster. The steps will be written here once they have been run on one. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the five tools above and no others.
3. The reply is a chat reply, not a desk reply: no heading and no table. Each part is a line of its own, and the first line carries the answer.
4. The ten tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented insurer at its starting data, started with `INSURER_TODAY=2026-11-26`:

- The loss ratio of private motor for drivers of 25 and over (`SEG-8601`): 68.15 percent, from USD 9,200,000.00 over USD 13,500,000.00. By year 65.00, 68.00 and 71.04 percent.
- The premium change that holds 70 percent for `SEG-8601`: 12.70 percent. Trend factor 1.157625, trended loss ratio 78.89 percent, premium needed USD 15,214,500.00.
- Home on the Saltmarsh Coast (`SEG-8604`): not reliable alone. 46 claims, 204 short of the 250 the method needs. On these figures 60.44 percent, marked as not reliable.
- Whether `SEG-8603` needs a rise to hold 60 percent: no. The trended loss ratio is 53.69 percent, 6.31 points below the target. No decrease is worked out.
- The loss ratio of `SEG-8601` for 2026 so far: cannot be answered. The experience holds 2023, 2024 and 2025 only.
- Motor fleet (`SEG-8606`): 18.50 percent to hold 73.00 percent. 250 claims is exactly the number needed, so the figures can be relied on.
- Drivers under 25 (`SEG-8602`) at a target of 65 percent and a claims trend of 7 percent a year, both the asker's own: 66.98 percent.
- The loss ratio of electric cars: cannot be answered. The experience is not split by fuel type.
- Asked to set the new rate, to change the method or to file rates: refused in a sentence.

Everyone and everything in the invented insurer is invented.

## Where it stops for a person

The pricing actuary signs off a rate change and the product committee approves it. Where a segment is too thin, the pricing actuary decides what to set beside its figures. A decrease is a commercial decision. A question the experience cannot answer goes to the pricing actuary.
