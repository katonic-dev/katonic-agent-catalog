(function () {
  var log = document.getElementById("log");
  var form = document.getElementById("ask");
  var input = document.getElementById("q");
  var sendBtn = document.getElementById("send");
  var chips = document.getElementById("chips");
  var modeLine = document.getElementById("mode");
  var dot = document.getElementById("dot");
  var sessionId = ""; // one conversation per browser tab
  var busy = false;

  function escapeHtml(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  // Text with line breaks, and bold where the reply uses **bold**.
  function render(text) {
    var safe = escapeHtml(String(text || "").trim());
    safe = safe.replace(/\*\*([^*\n]+)\*\*/g, "<b>$1</b>");
    return safe.split(/\n{2,}/).map(function (p) { return "<p>" + p.replace(/\n/g, "<br>") + "</p>"; }).join("");
  }
  function add(cls, html) {
    var d = document.createElement("div");
    d.className = "msg " + cls;
    d.innerHTML = html;
    log.appendChild(d);
    log.scrollTop = log.scrollHeight;
    return d;
  }
  function ask(question) {
    question = String(question || "").trim();
    if (!question || busy) return;
    busy = true;
    sendBtn.disabled = true;
    chips.style.display = "none";
    add("me", render(question));
    var wait = add("bot", '<span class="typing" aria-label="The assistant is typing"><i></i><i></i><i></i></span>');
    fetch("api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: question, sessionId: sessionId }),
    })
      .then(function (r) { return r.json().then(function (data) { return { ok: r.ok, data: data }; }); })
      .then(function (res) {
        if (!res.ok || !res.data.reply) {
          wait.className = "msg err";
          wait.innerHTML = render(res.data.error || "The assistant did not answer.");
          return;
        }
        if (res.data.sessionId) sessionId = res.data.sessionId;
        wait.innerHTML = render(res.data.reply) + (res.data.source ? '<span class="src">' + escapeHtml(res.data.source) + "</span>" : "");
      })
      .catch(function () {
        wait.className = "msg err";
        wait.innerHTML = render("The assistant did not answer.");
      })
      .then(function () {
        busy = false;
        sendBtn.disabled = false;
        log.scrollTop = log.scrollHeight;
        input.focus();
      });
  }
  fetch("api/status")
    .then(function (r) { return r.json(); })
    .then(function (s) {
      if (s.mode === "stand-in") modeLine.textContent = "Stand-in mode: fixed answers, no agent";
      else if (s.mode === "none") {
        modeLine.textContent = "No agent connected";
        dot.className = "chatdot off";
      }
    })
    .catch(function () {});
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var q = input.value;
    input.value = "";
    ask(q);
  });
  chips.addEventListener("click", function (e) {
    if (e.target && e.target.tagName === "BUTTON") ask(e.target.textContent);
  });
})();
