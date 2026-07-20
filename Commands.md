# Code Examples — Run Commands

One runnable example per section. Run everything from the `code/` directory
(this file's location), after completing the one-time setup in the
[repo root README](../README.md) (`pip install -r requirements.txt`, copy
`.env.example` to `.env`).

| Section | Topic | Run command |
|---|---|---|
| 00 | Setup check | `python3 00-setup/hello_openai.py` |
| 02 | AI Security Fundamentals | `python3 02-ai-security-fundamentals/attack_surface_demo.py` |
| 03 | AI & ML Foundations | `python3 03-ai-ml-foundations/tokens_embeddings_demo.py` |
| 04 | Understanding LLMs | `python3 04-understanding-llms/hallucination_demo.py` |
| 05 | Rate Limiting | `python3 05-rate-limiting/rate_limit_demo.py` |
| 06 | Prompt Injection | `python3 06-prompt-injection/prompt_injection_demo.py` |
| 07 | Secrets Detection | `python3 07-secrets-detection/secrets_guard_demo.py` |
| 08 | PII Redaction | `python3 08-pii-redaction/pii_redactor_demo.py` |
| 09 | Evasion-Resistant Scanning | `python3 09-evasion-resistant-scanning/canonicalizer_demo.py` |
| 10 | Cost/DoS Guard | `python3 10-cost-dos-guard/cost_guard_demo.py` |
| 11 | Safe Audit Logging | `python3 11-safe-audit-logging/audit_log_demo.py` |
| 12 | Supply Chain Guard | `python3 12-supply-chain-guard/check_dependencies_demo.py` |
| 13 | Agent Tool Guardrails | `python3 13-agent-tool-guardrails/agent_guard_demo.py` |
| 14 | Capstone Mini-Gateway | `python3 14-capstone-mini-gateway/handler_demo.py` |
| — | Production reference test suite | `cd production-reference && python3 -m pytest tests/ -v` |

No OpenAI key needed — every script falls back to an offline dummy backend
automatically (see `common.py`).
