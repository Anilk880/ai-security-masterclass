# Production Reference

This folder is different from every other `code/` subfolder in this course:
everywhere else, the scripts are small, from-scratch demos built to teach one
concept. This folder is the source code of a real, production-grade AI
gateway — RiskLumen — that actually runs the guards this course teaches:
rate limiting, prompt injection detection, secrets detection, PII redaction,
evasion-resistant scanning, cost/DoS guarding, safe audit logging, and agent
tool guardrails, wired together in `src/handler.py`. Every guard's actual
logic — every regex, every check, every line that makes a decision — is
unchanged from the real deployed gateway.

## No cloud account needed -- adapted for this course, guard logic untouched

The real, deployed version of this gateway runs on a hosted server: it reads
and writes a shared, persistent database for rate limiting, and fetches its
OpenAI key from a shared secret store common to every server instance.
Students taking this course don't have (and shouldn't need) any of that
infrastructure just to read guard code, so exactly two things were adapted
for local use, both clearly marked in the affected files' docstrings:

- **`rate_limiter.py`** — the shared database swapped for an in-process
  dict. Same sliding-window algorithm, same public functions, just not
  persisted across restarts or shared across machines.
- **`openai_client.py`** and **`handler.py`**'s gateway-auth secret — the
  shared secret store swapped for `code/common.py`, the same real/dummy LLM
  client every other example in this course uses. Set your own
  `OPENAI_API_KEY` in `.env` to run it against the real API with your own
  key, or leave it unset to run fully offline against the dummy backend —
  `openai_client.py` doesn't know or care which one is active, same as
  everywhere else in this course.

Every other file — `prompt_guard.py`, `secrets_guard.py`, `pii_redactor.py`,
`input_canonicalizer.py`, `cost_guard.py`, `audit_log.py`, `agent_guard.py`,
`scripts/check_dependencies.py` — is copied verbatim, zero changes.

Run the real test suite — 84 tests, zero cloud account, zero OpenAI key
required:

```bash
pip install -r requirements.txt   # adds pytest
cd code/production-reference
python3 -m pytest tests/ -v
```

Reading `tests/test_rate_limiter.py` alongside `src/rate_limiter.py` is the
single best way to see this course's concepts proven correct against real,
adversarial edge cases — not just demonstrated once, but tested exhaustively.

To run the guard pipeline end to end with a real model reply:

```bash
cd code/production-reference/src
python3 -c "import openai_client; print(openai_client.ask('hello'))"
```

## Map: course section -> real module

| Section | Concept | Real module |
|---|---|---|
| 5 — Prompt Injection | Denylist guard | `src/prompt_guard.py` |
| 6 — OWASP LLM10, Model Theft | Duplicate-prompt rate limiting | `src/rate_limiter.py` |
| 7 — Agent Security | Tool-call validation | `src/agent_guard.py` |
| 9 — Data Security & Privacy | Secrets + PII detection | `src/secrets_guard.py`, `src/pii_redactor.py` |
| 10 — Supply Chain Security | Dependency allowlisting | `scripts/check_dependencies.py` |
| 11 — Guardrails | Evasion-resistant scanning, cost guard, safe logging | `src/input_canonicalizer.py`, `src/cost_guard.py`, `src/audit_log.py` |
| 17 — Capstone | The full pipeline, wired together | `src/handler.py` |

The masterclass's own `code/<section>/*.py` scripts (like
`05-prompt-injection/injection_demo.py`) are the place to start — small,
readable, built from scratch. Come here once you want to see the same idea
holding up as a real, tested, production system.
