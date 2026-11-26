// Member website for the Meridian Trust Pension Scheme (invented), with a chat box.
// The page talks to this server. This server talks to an agent on a Katonic
// platform through its public chat API (POST /public/v1/chat). The API key
// stays on the server and is never logged or sent to the page.
// With PORTAL_DEMO=true no platform is needed: a stand-in answers three questions.
"use strict";
const http = require("http");
const fs = require("fs");
const path = require("path");

// Settings come from the environment. A file named by PORTAL_ENV_FILE
// (lines of NAME=value) can supply any that the environment does not.
const settings = {};
const envFile = process.env.PORTAL_ENV_FILE || "";
if (envFile) {
  try {
    for (const line of fs.readFileSync(envFile, "utf8").split(/\r?\n/)) {
      const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/);
      if (m) settings[m[1]] = m[2];
    }
  } catch (err) {
    console.log("Member portal: settings file not readable");
  }
}
function setting(name) {
  return process.env[name] !== undefined && process.env[name] !== "" ? process.env[name] : settings[name] || "";
}
const BASE = String(setting("KATONIC_BASE_URL")).replace(/\/+$/, "");
const KEY = setting("KATONIC_API_KEY");
const AGENT_ID = setting("PORTAL_AGENT_ID");
const DEMO = String(setting("PORTAL_DEMO")).toLowerCase() === "true";
const PORT = Number(setting("PORT")) || 3470;
// The member who is signed in to this example site. A real site takes it from its own sign-in.
const MEMBER_ID = setting("PORTAL_MEMBER_ID") || "MEM-5001";
const PUBLIC = path.join(__dirname, "public");
const TYPES = { ".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".svg": "image/svg+xml" };
const CONNECTED = Boolean(BASE && KEY && AGENT_ID);

const NO_AGENT = "No agent is connected. Set KATONIC_BASE_URL, KATONIC_API_KEY and PORTAL_AGENT_ID, or start the server with PORTAL_DEMO=true to try the stand-in.";
const UNREACHABLE = "The assistant did not answer. Try again, or call member services.";

// ---- Stand-in answers (PORTAL_DEMO=true) ----
// Every figure is as the invented bank's fund system holds it for member MEM-5001
// at its starting data (prices dated 31 Oct 2026).
const STAND_IN_LABEL = "Stand-in answer (fixed text, not from an agent)";
const STAND_IN = [
  {
    question: "What do I hold, and what is it worth?",
    answer:
      "You hold units in three funds. The values use the unit prices of 31 Oct 2026, not today's prices.\n\n" +
      "Meridia Cautious Income Fund (FND-3001): 4,210.50 units at USD 1.284, value USD 5,406.28\n" +
      "Meridia Balanced Growth Fund (FND-3002): 6,800.00 units at USD 2.0715, value USD 14,086.20\n" +
      "Meridia Global Equity Fund (FND-3003): 2,950.25 units at USD 3.452, value USD 10,184.26\n\n" +
      "Total: USD 29,676.74.",
  },
  {
    question: "What are the charges on the Balanced Growth Fund?",
    answer:
      "Meridia Balanced Growth Fund (FND-3002): the annual management charge is 0.65 percent and the ongoing charges figure is 0.73 percent, as the fund record shows them.",
  },
  {
    question: "Which fund should I move my savings into?",
    answer:
      "That is a question for advice, and this assistant gives information only. It can tell you what each fund's fact sheet says: its charges, its risk level and its unit price. For advice on which fund suits you, speak to a regulated financial adviser.",
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
  // The site knows who is signed in, so it tells the agent. The member does not type their own id.
  const content = `I am ${MEMBER_ID}. ${message}`;
  const body = { agent_id: AGENT_ID, messages: [{ role: "user", content }], stream: true };
  if (sessionId) body.session_id = sessionId;
  const r = await fetch(`${BASE}/public/v1/chat`, {
    method: "POST",
    headers: { Authorization: `Bearer ${KEY}`, "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify(body),
  });
  if (!r.ok) {
    const err = new Error("agent call failed");
    err.status = r.status;
    throw err;
  }
  const type = (r.headers.get("content-type") || "").toLowerCase();
  if (!type.includes("text/event-stream")) {
    const data = await r.json();
    const text = data.message && data.message.content ? data.message.content : data.content || data.response || "";
    return { content: text, sessionId: data.session_id || sessionId || "" };
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
  // The page asks with relative addresses, so the site works behind a path prefix.
  const route = url.pathname.replace(/^.*\/api\//, "/api/");
  if (req.method === "GET" && (route === "/api/status" || route === "/api/health")) {
    return json(res, 200, { ok: true, mode: DEMO ? "stand-in" : CONNECTED ? "agent" : "none" });
  }
  if (req.method === "POST" && route === "/api/chat") {
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
        console.log("Member portal: no agent settings");
        return json(res, 503, { error: NO_AGENT });
      }
      try {
        const reply = await askAgent(message, sessionId);
        json(res, 200, { reply: reply.content, sessionId: reply.sessionId });
      } catch (err) {
        console.log("Member portal: agent call failed, status " + (err.status || "none"));
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
  console.log(`Member portal: listening on ${PORT}, ${mode}`);
});
