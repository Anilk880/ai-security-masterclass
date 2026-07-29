"""
Section 15 -- Second Project: a real local web chat UI wrapping the exact
same real gateway entry point Project 1 already read, ran, and broke --
code/production-reference/src/handler.py. Nothing in production-reference/
is touched or reimplemented here; this file only imports and calls the
real handler.handler(), exactly like handler_demo.py and test_handler.py
already do, and wraps it in a minimal local web server + chat frontend so
you can talk to the real gateway from a browser instead of a terminal.

Zero new dependencies: uses only Python's built-in http.server. No
external framework, no npm build step -- open the page, start chatting,
watch the real guards fire in your browser as you type.

Run:  python3 code/15-ai-chatbot-project/web_chat_demo.py
Then open: http://localhost:8787
"""
import json
import os
import sys
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "production-reference", "src"))
import handler  # noqa: E402  (import must follow sys.path setup above)
from common import _BACKEND  # noqa: E402

PORT = int(os.environ.get("WEB_CHAT_PORT", "8787"))
GATEWAY_SECRET = handler._get_gateway_secret()

# One demo client identity per server run -- enough to exercise rate
# limiting/repetitive-prompt detection realistically across a real chat
# session without the browser needing to know anything about auth headers.
DEMO_CLIENT_ID = f"web-chat-{uuid.uuid4().hex[:8]}"

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>AI Security Masterclass -- Live Gateway Chat</title>
<style>
  :root { color-scheme: dark; }
  body {
    margin: 0; font-family: 'Segoe UI', system-ui, sans-serif;
    background: linear-gradient(180deg, #0b1220 0%, #111a2e 100%);
    color: #e5e7eb; height: 100vh; display: flex; flex-direction: column;
  }
  header {
    padding: 18px 24px; border-bottom: 1px solid #22305233;
    display: flex; align-items: center; gap: 12px;
  }
  header .dot { width: 10px; height: 10px; border-radius: 50%; background: #22d3ee; box-shadow: 0 0 12px #22d3ee; }
  header h1 { font-size: 16px; letter-spacing: 0.08em; text-transform: uppercase; margin: 0; color: #93a0bd; }
  header .badge {
    margin-left: auto; font-size: 12px; color: #22d3ee; border: 1px solid #22d3ee55;
    padding: 4px 10px; border-radius: 999px;
  }
  #log { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 14px; }
  .msg { max-width: 70%; padding: 12px 16px; border-radius: 12px; line-height: 1.45; font-size: 15px; white-space: pre-wrap; }
  .user { align-self: flex-end; background: #22d3ee; color: #0b1220; font-weight: 600; }
  .reply { align-self: flex-start; background: #16213a; border: 1px solid #223052; }
  .blocked { align-self: flex-start; background: #2a1414; border: 1px solid #f87171aa; color: #f87171; }
  .blocked .code { font-family: Consolas, monospace; font-size: 12px; opacity: 0.85; display: block; margin-top: 6px; }
  .advisory { font-size: 12px; color: #93a0bd; margin-top: 8px; display: block; }
  .redactions { font-size: 12px; color: #22d3ee; margin-top: 6px; display: block; }
  form { display: flex; gap: 10px; padding: 18px 24px; border-top: 1px solid #22305233; }
  input {
    flex: 1; background: #0f1b2e; border: 1px solid #223052; color: #e5e7eb;
    padding: 12px 16px; border-radius: 10px; font-size: 15px; outline: none;
  }
  input:focus { border-color: #22d3ee; }
  button {
    background: #22d3ee; color: #0b1220; border: none; padding: 0 22px;
    border-radius: 10px; font-weight: 700; cursor: pointer; font-size: 15px;
  }
  button:disabled { opacity: 0.5; cursor: default; }
</style>
</head>
<body>
<header>
  <div class="dot"></div>
  <h1>AI Security Masterclass &mdash; Live Gateway Chat</h1>
  <div class="badge" id="backend-badge">connecting&hellip;</div>
</header>
<div id="log"></div>
<form id="form">
  <input id="input" autocomplete="off" placeholder="Try an ordinary question, or a real attack from this course&hellip;" />
  <button id="send">Send</button>
</form>
<script>
const log = document.getElementById('log');
const form = document.getElementById('form');
const input = document.getElementById('input');
const badge = document.getElementById('backend-badge');

function addMsg(text, cls) {
  const div = document.createElement('div');
  div.className = 'msg ' + cls;
  div.textContent = text;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
  return div;
}

fetch('/status').then(r => r.json()).then(s => {
  badge.textContent = s.backend + ' backend';
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = input.value.trim();
  if (!text) return;
  addMsg(text, 'user');
  input.value = '';
  input.disabled = true;

  const resp = await fetch('/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt: text }),
  });
  const data = await resp.json();

  if (resp.status !== 200) {
    const div = addMsg('Blocked by the real gateway.', 'blocked');
    const code = document.createElement('span');
    code.className = 'code';
    code.textContent = `statusCode: ${resp.status}   body: ${JSON.stringify(data)}`;
    div.appendChild(code);
  } else {
    const div = addMsg(data.llm_response, 'reply');
    if (data.redactions && data.redactions.length) {
      const r = document.createElement('span');
      r.className = 'redactions';
      r.textContent = 'Redacted before it reached the model: ' + data.redactions.join(', ');
      div.appendChild(r);
    }
    const a = document.createElement('span');
    a.className = 'advisory';
    a.textContent = data.advisory;
    div.appendChild(a);
  }
  input.disabled = false;
  input.focus();
});
</script>
</body>
</html>
"""


def _event(prompt: str) -> dict:
    """Builds the same Lambda-style event dict handler.handler() expects
    in production and in every other demo/test in this repo -- the
    browser never sees or sends the gateway secret itself; this server
    process holds it, the same way a real deployed gateway's own
    infrastructure would inject it before requests reach the handler."""
    return {
        "body": json.dumps({"prompt": prompt}),
        "headers": {
            "x-api-key": DEMO_CLIENT_ID,
            "x-gateway-secret": GATEWAY_SECRET,
        },
        "requestContext": {"http": {"sourceIp": "127.0.0.1"}},
    }


class ChatHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[web_chat_demo] {self.address_string()} - {fmt % args}")

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path == "/status":
            self._send_json(200, {"backend": _BACKEND})
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path != "/chat":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        try:
            prompt = json.loads(raw).get("prompt", "")
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid_json"})
            return

        # The real gateway entry point -- same function, same guard
        # pipeline, same order, as every other lecture in this course.
        result = handler.handler(_event(prompt), None)
        self._send_json(result["statusCode"], json.loads(result["body"]))


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), ChatHandler)
    print(f"AI Security Masterclass -- live gateway chat running.")
    print(f"Open http://localhost:{PORT} in your browser.")
    print("Every message you send goes through the real handler.py pipeline. Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
