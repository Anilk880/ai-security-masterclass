# Code Examples — Run Commands

One runnable example per section. Run everything from the repo root
(`ai-security-masterclass/`), after completing the one-time setup in the
[repo root README](../README.md) (`pip install -r requirements.txt`, copy
`.env.example` to `.env`).

| Section | Topic | Run command | What it does |
|---|---|---|---|
| 00 | Setup check | `python3 code/00-setup/hello_openai.py` | Sends one real chat request to confirm your `.env` / API key is wired up before the rest of the course relies on it. |
| 02 | AI Security Fundamentals | `python3 code/02-ai-security-fundamentals/attack_surface_demo.py` | Runs the same adversarial string through a parameterized SQL query (neutralized) and an LLM prompt (no equivalent defense) to show the new attack surface. |
| 03 | AI & ML Foundations | `python3 code/03-ai-ml-foundations/tokens_embeddings_demo.py` | Tokenizes text with `tiktoken`, then compares embeddings of similar vs. unrelated sentences to show vector distance in action. |
| 04 | Understanding LLMs | `python3 code/04-understanding-llms/hallucination_demo.py` | Asks about a fabricated research study to show the model inventing confident, plausible-sounding "findings". |
| 05 | Rate Limiting | `python3 code/05-rate-limiting/rate_limit_demo.py` | Trips the real sliding-window rate limiter with a burst of requests, then shows it catching an attacker rotating API keys from one IP. |
| 06 | Prompt Injection | `python3 code/06-prompt-injection/prompt_injection_demo.py` | Runs known injection phrasings past the real denylist scanner, then shows a reworded phrasing bypassing it. |
| 07 | Secrets Detection | `python3 code/07-secrets-detection/secrets_guard_demo.py` | Catches known-shaped secrets (AWS key, GitHub token, bare JWT) via regex + entropy, then shows a low-entropy secret slipping through undetected. |
| 08 | PII Redaction | `python3 code/08-pii-redaction/pii_redactor_demo.py` | Finds and redacts email/PAN/Aadhaar/credit-card values in one message, then shows a US SSN (outside its supported formats) passing through untouched. |
| 09 | Evasion-Resistant Scanning | `python3 code/09-evasion-resistant-scanning/canonicalizer_demo.py` | Catches a zero-width-character injection that evaded raw scanning, then shows a homoglyph bypass that Unicode normalization can't fix. |
| 10 | Cost/DoS Guard | `python3 code/10-cost-dos-guard/cost_guard_demo.py` | Rejects an oversized request with the real token-cost estimator, then shows it under-counting a dense non-English request compared to the real tokenizer. |
| 11 | Safe Audit Logging | `python3 code/11-safe-audit-logging/audit_log_demo.py` | Writes safe, hashed/categorized audit log lines, then shows a careless call site leaking a raw secret straight into the log. |
| 12 | Supply Chain Guard | `python3 code/12-supply-chain-guard/check_dependencies_demo.py` | Runs the real AST-based import allowlist checker against clean source, then shows it missing a dynamic `__import__()` bypass. |
| 13 | Agent Tool Guardrails | `python3 code/13-agent-tool-guardrails/agent_guard_demo.py` | Evaluates allowed/denied/unknown agent actions against the real allowlist, then shows a risky financial action getting auto-approved due to its name. |
| 14 | Capstone Mini-Gateway | `python3 code/14-capstone-mini-gateway/handler_demo.py` | Sends 4 requests through the full real gateway pipeline (auth, rate limit, prompt injection, secrets, PII, cost guard, model call) to show each guard stage firing. |
| — | Production reference test suite | `cd code/production-reference && python3 -m pytest tests/ -v` | Runs the real gateway's 84-test suite, offline, no cloud account or API key required. |

No OpenAI key needed — every script falls back to an offline dummy backend
automatically (see `common.py`). Section 14 makes a real network call to the
model when a real `OPENAI_API_KEY` is set; set `LLM_BACKEND=dummy` in `.env`
to keep it fully offline like every other section.
