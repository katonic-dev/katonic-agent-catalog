# Store portal (Rowanmere Kitchen)

**Invented. Rowanmere Kitchen, its restaurant R-014 (Port Ilvane, Harbour Street), its crew and every figure on the page are made up for a demonstration. They are not real.**

## What it is

A small crew website for one restaurant, with a chat box. The crew member types a question. The server passes it to an agent on a Katonic platform and shows the answer.

The page has today's shift, deliveries, the cleaning schedule, a notice and the temperature checks. The links in the menu go nowhere. They are examples.

It is plain Node. It has no dependencies and needs Node 20 or later. The page loads nothing from the internet: no fonts, no scripts, no images.

## Run it with the stand-in (no platform needed)

```
STORE_DEMO=true PORT=3460 node server.js
```

On Windows PowerShell:

```
$env:STORE_DEMO = "true"; $env:PORT = "3460"; node server.js
```

Open `http://localhost:3460/`. The stand-in answers the three suggested questions from fixed texts. The texts quote the sample Allergen Matrix v4.1, Food Safety Plan v5.0 and Store Procedures Manual v3.1. Every stand-in answer is labelled as coming from the stand-in. For any other question it says that it only knows those three.

## Run it against a platform

Set these, then start the server:

```
KATONIC_BASE_URL=<address of your platform> KATONIC_API_KEY=<your key> STORE_AGENT_ID=<your agent id> node server.js
```

The agent needs to know the sample documents above. If the key or the agent id is missing, the page still loads. The chat box says that no agent is connected.

## Settings

| Name | What it is | Default |
|---|---|---|
| `KATONIC_BASE_URL` | Address of the platform, for example `https://platform.example` | none |
| `KATONIC_API_KEY` | API key for the public chat API. Kept on the server | none |
| `STORE_AGENT_ID` | Id of the agent that answers | none |
| `PORT` | Port the server listens on | `3460` |
| `STORE_DEMO` | `true` turns on the stand-in. No platform is called | off |
| `STORE_ENV_FILE` | Path to an optional settings file with lines like `NAME=value` | none |

The environment wins over the settings file. No key, agent id or host name is written in any file here. Keep your own settings file outside this repository.

## What the server sends to the platform

One request for each question:

- `POST {KATONIC_BASE_URL}/public/v1/chat`
- Headers: `Authorization: Bearer <key>`, `Content-Type: application/json`, `Accept: text/event-stream`
- Body:

```json
{
  "agent_id": "<STORE_AGENT_ID>",
  "messages": [{ "role": "user", "content": "<the question>" }],
  "stream": true,
  "session_id": "<only after the first reply>"
}
```

The reply is a stream of events. The server joins the text events into one answer and keeps the thread id as the session id, so a follow-up question stays in the same conversation. The page never sees the key.

## What it does not do

- It has not been run against a platform by the author of this folder. Only stand-in mode and the "no agent" case are tested.
- It does not log in crew members. Anyone who can reach the page can use the chat box.
- It does not store questions or answers.
- It does not give allergen advice. The stand-in texts are fixed. A real agent's answers are only as good as the documents it holds.
- The shift, delivery and check figures on the page are fixed examples. Nothing is read from a real system.
- It is not meant to be put on the internet as it is.

## Test

```
node test.cjs
```

It starts the server in stand-in mode, checks the page, the three answers and the refusal, then starts it with no settings and checks the no-agent message. It stops the servers when done.

## Files

- `server.js`: the server, the stand-in and the platform call
- `public/`: the page (`index.html`, `portal.css`, `portal.js`)
- `test.cjs`: the test
