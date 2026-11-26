# Member portal (Meridian Trust Pension Scheme)

**Invented. The Meridian Trust Pension Scheme, its member Tobias Wrenfield (MEM-5001), the funds and every figure on the page are made up for a demonstration. They are not real.**

## What it is

A small website for one pension member, with a chat box. The member types a question. The server passes it to an agent on a Katonic platform and shows the answer.

It shows one more place a person can meet an agent: inside a website the organisation already runs. The agent behind it is the [Member Fund Assistant](../../agents/member-fund-assistant/README.md), the same one that answers in the Work Room.

The page has the member's pension pot, a notice and the holdings table. The links in the menu go nowhere. They are examples.

It is plain Node. It has no dependencies and needs Node 20 or later. The page loads nothing from the internet: no fonts, no scripts, no images.

## Run it with the stand-in (no platform needed)

```
PORTAL_DEMO=true PORT=3470 node server.js
```

On Windows PowerShell:

```
$env:PORTAL_DEMO = "true"; $env:PORT = "3470"; node server.js
```

Open `http://localhost:3470/`. The stand-in answers the three suggested questions from fixed texts. The figures are as the invented bank's fund system holds them for MEM-5001 at its starting data. Every stand-in answer is labelled as coming from the stand-in. For any other question it says that it only knows three.

## Run it against a platform

Build and publish the Member Fund Assistant first, with the invented bank's `funds` system connected. Then set these and start the server:

```
KATONIC_BASE_URL=<address of your platform> KATONIC_API_KEY=<your key> PORTAL_AGENT_ID=<the agent's id> node server.js
```

The key needs the Chat scope, and must belong to a person who can use the agent. If the key or the agent id is missing, the page still loads. The chat box says that no agent is connected.

The site knows which member is signed in, so the server puts the member's id in front of each question before it goes to the agent. The member never types it. A real site takes the id from its own sign-in.

## Settings

| Name | What it is | Default |
|---|---|---|
| `KATONIC_BASE_URL` | The address of the platform | none |
| `KATONIC_API_KEY` | A key with the Chat scope. Kept on the server, never sent to the page, never logged | none |
| `PORTAL_AGENT_ID` | The id of the published Member Fund Assistant | none |
| `PORTAL_MEMBER_ID` | The member this example site is signed in as | `MEM-5001` |
| `PORTAL_DEMO` | `true` answers from the stand-in and calls no platform | off |
| `PORTAL_ENV_FILE` | A file of `NAME=value` lines that supplies any setting the environment does not | none |
| `PORT` | The port the server listens on | `3470` |

## On App Studio

Source: this repository, branch `main`. Framework: Node/React. Main file: `banking/apps/member-portal/server.js`. Health check path: `/api/health`. Set the settings above as environment variables, the key as a secret. The page calls its own server with relative addresses, so it works behind the path App Studio gives it.

## What it does not do

- It has no sign-in. One invented member is fixed in a setting.
- It keeps nothing. A conversation lasts as long as the browser tab.
- It gives no advice. The agent behind it is instructed to give information only, and says so when asked which fund to choose.
