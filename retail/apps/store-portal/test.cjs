// Checks the store portal in stand-in mode and with no agent. Built-in modules only.
// Run: node test.cjs
"use strict";
const { spawn } = require("child_process");
const http = require("http");
const net = require("net");
const path = require("path");
const assert = require("assert");

const SERVER = path.join(__dirname, "server.js");

// Tries ports 3460 to 3469 first, then any free port.
function tryPort(wanted) {
  return new Promise((resolve) => {
    const s = net.createServer();
    s.once("error", () => resolve(0));
    s.listen(wanted, "127.0.0.1", () => {
      const port = s.address().port;
      s.close(() => resolve(port));
    });
  });
}
async function freePort() {
  for (let p = 3460; p <= 3469; p++) {
    const got = await tryPort(p);
    if (got) return got;
  }
  return tryPort(0);
}

function request(port, method, urlPath, body) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const req = http.request(
      { host: "127.0.0.1", port, path: urlPath, method, headers: data ? { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(data) } : {} },
      (res) => {
        let text = "";
        res.setEncoding("utf8");
        res.on("data", (c) => (text += c));
        res.on("end", () => resolve({ status: res.statusCode, text }));
      }
    );
    req.on("error", reject);
    if (data) req.write(data);
    req.end();
  });
}

async function start(extraEnv) {
  const port = await freePort();
  const env = { ...process.env, PORT: String(port) };
  for (const name of ["STORE_DEMO", "KATONIC_BASE_URL", "KATONIC_API_KEY", "STORE_AGENT_ID", "STORE_ENV_FILE"]) delete env[name];
  Object.assign(env, extraEnv);
  const child = spawn(process.execPath, [SERVER], { env, stdio: ["ignore", "pipe", "pipe"] });
  await new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("server did not start")), 8000);
    child.stdout.on("data", (c) => {
      if (String(c).includes("listening")) { clearTimeout(timer); resolve(); }
    });
    child.on("exit", () => reject(new Error("server exited early")));
  });
  return { port, child };
}

function stop(s) {
  return new Promise((resolve) => {
    s.child.removeAllListeners("exit");
    s.child.on("exit", resolve);
    s.child.kill();
  });
}

const QUESTIONS = [
  { q: "Does the grilled chicken wrap contain sesame or milk?", must: ["B-05", "Gluten (wheat), Milk, Sesame"] },
  { q: "What do I do if a walk-in chiller reads above 5 degrees?", must: ["above 5.0 °C is a deviation", "8.0 °C", "SP-04"] },
  { q: "How do I remake a wrong order?", must: ["SP-07", "shift manager approves the remake", "R1"] },
];

let passed = 0;
function ok(name) { passed++; console.log("ok   " + name); }

(async () => {
  let s = await start({ STORE_DEMO: "true" });
  try {
    const page = await request(s.port, "GET", "/");
    assert.strictEqual(page.status, 200);
    assert.ok(page.text.includes("Rowanmere Kitchen"), "page names the company");
    assert.ok(/invented/i.test(page.text), "page says it is invented");
    assert.ok(!/https?:\/\//i.test(page.text), "page loads nothing from the internet");
    ok("page loads, says it is invented, links nothing external");

    for (const css of ["/portal.css", "/portal.js"]) {
      assert.strictEqual((await request(s.port, "GET", css)).status, 200);
    }
    ok("style and script load");

    for (const item of QUESTIONS) {
      const r = await request(s.port, "POST", "/api/chat", { message: item.q });
      assert.strictEqual(r.status, 200);
      const data = JSON.parse(r.text);
      for (const piece of item.must) assert.ok(data.reply.includes(piece), `answer to "${item.q}" holds "${piece}"`);
      assert.ok(/stand-in/i.test(data.source), "answer is labelled as from the stand-in");
      ok("fixed answer: " + item.q);
    }

    const unknown = JSON.parse((await request(s.port, "POST", "/api/chat", { message: "What is the wifi password?" })).text);
    assert.ok(unknown.reply.includes("only knows three questions"));
    assert.ok(/stand-in/i.test(unknown.source));
    ok("unknown question gets the stand-in refusal");

    const empty = await request(s.port, "POST", "/api/chat", { message: "  " });
    assert.strictEqual(empty.status, 400);
    ok("empty question is refused");

    const status = JSON.parse((await request(s.port, "GET", "/api/status")).text);
    assert.strictEqual(status.mode, "stand-in");
    ok("status says stand-in");
  } finally {
    await stop(s);
  }

  s = await start({});
  try {
    const page = await request(s.port, "GET", "/");
    assert.strictEqual(page.status, 200);
    ok("page loads with no agent settings");
    const r = await request(s.port, "POST", "/api/chat", { message: QUESTIONS[0].q });
    assert.strictEqual(r.status, 503);
    assert.ok(JSON.parse(r.text).error.startsWith("No agent is connected"));
    ok("chat says plainly that no agent is connected");
    assert.strictEqual(JSON.parse((await request(s.port, "GET", "/api/status")).text).mode, "none");
    ok("status says none");
  } finally {
    await stop(s);
  }

  console.log(`\n${passed} checks passed`);
})().catch((err) => {
  console.error("FAILED: " + err.message);
  process.exit(1);
});
