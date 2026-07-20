"""
Section 11 -- Safe Audit Logging: a live demo of the real gateway's audit
logger, imported directly from code/production-reference/src/audit_log.py
-- not a simplified teaching version, the actual production module.

Two parts:
  1. Two correct, real guard-decision log lines -- a blocked secrets_guard
     event and a redacted pii_redactor event -- watch client_hint hold a
     one-way hash, never the raw API key, and watch redaction_types record
     only CATEGORIES ("EMAIL"), never the actual redacted values.
  2. A careless call site that passes a raw, real secret through **extra
     "just for debugging" -- watch log_event happily write it out, verbatim,
     into what was supposed to be a safe log line.

Run: python3 code/11-safe-audit-logging/audit_log_demo.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "production-reference", "src"))
import audit_log  # noqa: E402  (import must follow sys.path setup above)

print("=== Part 1: two real, correctly-called guard-decision log lines ===")
print()
RAW_API_KEY = "sk-live-abc123XYZ"
client_hint = audit_log.hash_hint(f"key:{RAW_API_KEY}")
print(f"Raw API key:  {RAW_API_KEY}")
print(f"client_hint:  {client_hint}  <- one-way hash, never reversible back to the key")
print()
audit_log.log_event("secrets_guard", "blocked", client_hint=client_hint)
audit_log.log_event(
    "pii_redactor", "redacted", client_hint=client_hint,
    redaction_types=["EMAIL", "PHONE_NUMBER"],
)

print()
print("=== Part 2: a careless call site passes a raw secret 'just for debugging' ===")
print()
RAW_PROMPT_WITH_SECRET = "My AWS key is AKIAABCDEFGHIJKLMNOP, please fix my deploy script"
print(f"Raw prompt (never meant to be logged): {RAW_PROMPT_WITH_SECRET}")
print()
audit_log.log_event(
    "prompt_guard", "blocked", client_hint=client_hint,
    debug_prompt=RAW_PROMPT_WITH_SECRET,  # <- the mistake: a raw sensitive value via **extra
)
print()
print("That AWS key is now sitting in a log line, in plain text, forever --")
print("log_event() itself did nothing wrong. It has no way to know that")
print("'debug_prompt' wasn't supposed to be a raw value. Nothing in the")
print("function's signature stops a caller from passing one anyway.")
