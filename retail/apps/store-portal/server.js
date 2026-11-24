// Crew website for Rowanmere Kitchen (an invented company), with a chat box.
// The page talks to this server. This server talks to an agent on a Katonic
// platform through its public chat API (POST /public/v1/chat). The API key
// stays on the server and is never logged or sent to the page.
// With STORE_DEMO=true no platform is needed: a stand-in answers three questions.
"use strict";
const http = require("http");
const fs = require("fs");
const path = require("path");

// Settings come from the environment. A file named by STORE_ENV_FILE
// (lines of NAME=value) can supply any that the environment does not.
const settings = {};
const envFile = process.env.STORE_ENV_FILE || "";
if (envFile) {
  try {
    for (const line of fs.readFileSync(envFile, "utf8").split(/\r?\n/)) {
      const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/);
      if (m) settings[m[1]] = m[2];
    }
  } catch (err) {
    console.log("Store portal: settings file not readable");
  }
}
function setting(name) {
  return process.env[name] !== undefined && process.env[name] !== "" ? process.env[name] : settings[name] || "";
}
const BASE = String(setting("KATONIC_BASE_URL")).replace(/\/+$/, "");
const KEY = setting("KATONIC_API_KEY");
const AGENT_ID = setting("STORE_AGENT_ID");
const DEMO = String(setting("STORE_DEMO")).toLowerCase() === "true";
const PORT = Number(setting("PORT")) || 3460;
const PUBLIC = path.join(__dirname, "public");
const TYPES = { ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".svg": "image/svg+xml" };
const CONNECTED = Boolean(BASE && KEY && AGENT_ID);

const NO_AGENT = "No agent is connected. Set KATONIC_BASE_URL, KATONIC_API_KEY and STORE_AGENT_ID, or start the server with STORE_DEMO=true to try the stand-in.";
const UNREACHABLE = "The agent did not answer. Try again, or ask the restaurant manager.";

// ---- Stand-in answers (STORE_DEMO=true) ----
// Every fact is quoted from the sample documents: Allergen Matrix v4.1,
// Food Safety Plan v5.0 and Store Procedures Manual v3.1 (all invented).
const STAND_IN_LABEL = "Stand-in answer (fixed text, not from an agent)";
const STAND_IN = [
  {
    question: "Does the grilled chicken wrap contain sesame or milk?",
    answer:
      "Yes, both. Allergen Matrix v4.1, row B-05, Grilled chicken wrap, contains: Gluten (wheat), Milk, Sesame. Menu specification: flour tortilla, grilled chicken, lettuce, cheddar, tahini-yoghurt sauce.\n\n" +
      "Clause 1.5: nobody may tell a guest that a dish is suitable or safe for them. Read out the row. If the guest has an allergy, the restaurant manager speaks to the guest.",
  },
  {
    question: "What do I do if a walk-in chiller reads above 5 degrees?",
    answer:
      "Food Safety Plan v5.0, clause 2.3: a chiller reading above 5.0 °C is a deviation. A second reading is taken after 15 minutes. If the second reading is above 8.0 °C the restaurant manager is called before any food from that unit is used.\n\n" +
      "Store Procedures Manual, SP-04, clause 4.5: take a second reading with the probe thermometer after 15 minutes, tell the restaurant manager, and record both readings and the action taken. The restaurant manager decides what happens to the food.",
  },
  {
    question: "How do I remake a wrong order?",
    answer:
      "Store Procedures Manual, SP-07. Clause 7.2: the crew member who finds the fault tells the shift manager before remaking. The shift manager approves the remake.\n\n" +
      "Clause 7.3: record every remake on the point of sale with a reason code. R1 is wrong item.\n\n" +
      "Clause 7.4: for reason codes R1 and R2, take a photo of the faulty product on the store tablet before it is discarded.",
  },
];
const STAND_IN_REFUSAL = "The stand-in only knows three questions. Use one of the suggested questions, or connect an agent.";
function norm(s) {
  return String(s).toLowerCase().replace(/[^a-z0-9 ]+/g, " ").replace(/\s+/g, " ").trim();
}
function standIn(message) {
  const hit = STAND_IN.find((x) => norm(x.question) === norm(message));
  return { reply: hit ? hit.answer : STAND_IN_REFUSAL, source: STAND_IN_LABEL };
}

// ---- Platform call ----
// Streams the agent's reply and assembles it from the event stream.
async function askAgent(message, sessionId) {
  const body = { agent_id: AGENT_ID, messages: [{ role: "user", content: message }], stream: true };
  if (sessionId) body.session_id = sessionId;
  const r = await fetch(`${BASE}/public/v1/chat`, {
    method: "POST",
    headers: { Authorization: `Bearer ${KEY}`, "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const err = new Error("agent call failed");
    err.status = r.status;
    err.detail = (await r.text()).slice(0, 300);
    throw err;
  }
  const type = (r.headers.get("content-type") || "").toLowerCase();
  if (!type.includes("text/event-stream")) {
    const data = await r.json();
    const content = data.message && data.message.content ? data.message.content : data.content || data.response || "";
    return { content, sessionId: data.session_id || sessionId || "" };
  }
  const parts = [];
  let sid = sessionId || "";
  let ended = false;
  const reader = r.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  for (;;) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let nl;
    while ((nl = buffer.indexOf("\n")) >= 0) {
      const line = buffer.slice(0, nl).replace(/\r$/, "");
      buffer = buffer.slice(nl + 1);
      if (!line.startsWith("data:")) continue;
      const payload = line.slice(5).trim();
      if (!payload) continue;
      if (payload === "[DONE]") return { content: parts.join(""), sessionId: sid };
      let evt;
      try { evt = JSON.parse(payload); } catch (err) { continue; }
      if (evt.type === "RUN_STARTED" && evt.thread_id) sid = evt.thread_id;
      else if (evt.type === "TEXT_MESSAGE_CONTENT") parts.push(evt.delta || "");
      else if (evt.type === "TEXT_MESSAGE_END") ended = true;
      else if (evt.type === "RUN_ERROR") {
        // A reply that already ended is kept; an error before that fails.
        if (ended && parts.join("").trim()) return { content: parts.join(""), sessionId: sid };
        const err = new Error("agent run failed");
        err.status = 502;
        err.detail = String(evt.error || evt.message || "").slice(0, 300);
        throw err;
      }
    }
  }
  return { content: parts.join(""), sessionId: sid };
}

function send(res, status, type, body) {
  res.writeHead(status, { "Content-Type": type, "Cache-Control": "no-store" });
  res.end(body);
}
function json(res, status, obj) {
  send(res, status, "application/json", JSON.stringify(obj));
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, "http://localhost");
  if (req.method === "GET" && url.pathname === "/api/status") {
    return json(res, 200, { mode: DEMO ? "stand-in" : CONNECTED ? "agent" : "none" });
  }
  if (req.method === "POST" && url.pathname === "/api/chat") {
    let raw = "";
    req.on("data", (c) => { raw += c; if (raw.length > 20000) req.destroy(); });
    req.on("end", async () => {
      let message = "";
      let sessionId = "";
      try {
        const data = JSON.parse(raw || "{}");
        message = String(data.message || "").trim().slice(0, 2000);
        sessionId = String(data.sessionId || "").slice(0, 100);
      } catch (err) { /* empty message handled below */ }
      if (!message) return json(res, 400, { error: "Type a question first." });
      if (DEMO) return json(res, 200, standIn(message));
      if (!CONNECTED) {
        console.log("Store portal: no agent settings");
        return json(res, 503, { error: NO_AGENT });
      }
      try {
        const reply = await askAgent(message, sessionId);
        json(res, 200, { reply: reply.content, sessionId: reply.sessionId });
      } catch (err) {
        console.log("Store portal: agent call failed, status " + (err.status || "none"));
        json(res, 502, { error: UNREACHABLE, status: err.status || 0 });
      }
    });
    return;
  }
  if (req.method === "GET") {
    const rel = url.pathname === "/" ? "index.html" : url.pathname.replace(/^\/+/, "");
    const file = path.normalize(path.join(PUBLIC, rel));
    if (!file.startsWith(PUBLIC + path.sep)) return send(res, 403, "text/plain", "Forbidden");
    return fs.readFile(file, (err, buf) => {
      if (err) return send(res, 404, "text/plain", "Not found");
      send(res, 200, TYPES[path.extname(file)] || "application/octet-stream", buf);
    });
  }
  send(res, 405, "text/plain", "Method not allowed");
});

server.listen(PORT, () => {
  const mode = DEMO ? "stand-in mode" : CONNECTED ? "agent configured" : "NO agent configured";
  console.log(`Store portal: listening on ${PORT}, ${mode}`);
});
