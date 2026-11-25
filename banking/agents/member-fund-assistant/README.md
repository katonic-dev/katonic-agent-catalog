# Member Fund Assistant

Answers a scheme member's questions about the scheme's funds and the member's own holdings, with every figure taken from a fund fact sheet or the member's record.

| | |
|---|---|
| Type and form | Conversational, answering agent |
| What starts it | A member's question, or a staff member's question on a member's behalf |
| How people meet it | Chat |
| Reads from | The pension scheme's funds system: the funds, their fact sheets, a member and the member's holdings |
| Changes | Nothing. It has no tool that acts, and it saves no draft |
| State | Built on a development cluster on 25 November 2026. All seven tests pass five runs in a row. Not on the Catalog shelf |

## What it does

- Answers a question about a fund from its fact sheet, and names the fact sheet and its date in the answer.
- Gives the member's holdings: each fund with its units, unit price, price date and value, and the total.
- Gives both charges a fact sheet shows, the annual management charge and the ongoing charges, each by its own name, and says they are different measures.
- Says plainly when the fact sheets do not hold the answer: a calendar year, a period longer than the fund's life, a date after the sheet date.
- Reads only the member who is asking.

## What it does not do

- Advise. It does not say which fund is better for the member, predict a return, or say what to hold, sell or move into.
- Switch funds, change contributions, start a transfer or change any detail of a member.
- Read or talk about any other member.
- Answer from general knowledge when the fact sheets are silent.
- Check who the person asking is. The funds system has no sign-in for a member, so the agent takes the member id the conversation names. Put the agent behind a sign-in that already knows who the member is before you give it to members.
- Guarantee the refusals. Declining advice and declining another member's records are instructions to the model, not controls. Run tests 5 and 6 on your own model before you rely on them.

## What you set up

- A model for the Reasoning tier.
- The pension scheme's funds system, connected as an imported API, with the four operations listed in [`agent.yaml`](agent.yaml) and no others. The system also has operations that save a batch result and post a contribution batch. Do not attach them to this agent.
- A way for the conversation to name the member asking.

## Build it

The steps will be written here once they have been run on a cluster. Until then:

1. The instructions are in [`instructions.md`](instructions.md), word for word.
2. The agent is a chat agent on the Reasoning tier with the four read tools above and no others.
3. The seven tests are in [`tests.yaml`](tests.yaml).

## Try it

Against the invented bank at its starting data, with the fact sheets dated 2026-10-31 (bank date 2026-11-24):

- `MEM-5001`, Tobias Wrenfield: three funds. FND-3001 4,210.5 units at 1.2840 is 5,406.28. FND-3002 6,800 units at 2.0715 is 14,086.20. FND-3003 2,950.25 units at 3.4520 is 10,184.26. Total 29,676.74.
- `FND-3002`, Meridia Balanced Growth Fund: launched 2022-09-26, so no 5 year return. The sheet says the fund is younger than the period.
- `FND-3005`, Meridia Sustainable Equity Fund: no 3 year or 5 year return either. Calendar years are never on a sheet.
- `FND-3003`, Meridia Global Equity Fund: annual management charge 0.75 percent, ongoing charges 0.84 percent. Two measures, not one.
- A request for advice, a forecast or a switch, and a question about `MEM-5004`: all refused.
- `MEM-5002`: holds FND-3003 only, 5,120 units, value 17,674.24 at the sheet's price. Asked for today's price, the agent gives the sheet's date and says it has no later one.

Everyone and everything in the invented bank is invented.

## Where it stops for a person

It gives information and never advice. A choice of fund, a switch, a change of contributions or a transfer is for the member to decide, with the scheme's own team or an adviser. Anything the fact sheets do not hold goes to the scheme's member services team.
