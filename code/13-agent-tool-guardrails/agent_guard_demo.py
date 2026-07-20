"""
Section 13 -- Agent Tool Guardrails: a live demo of the real gateway's
least-privilege agent-action guard, imported directly from
code/production-reference/src/agent_guard.py -- not a simplified teaching
version, the actual production module (OWASP LLM07/LLM08).

Two parts:
  1. Three actions against the DEFAULT allowlist -- a low-risk allowed
     action, a high-risk action that's not even on the allowlist (denied
     outright), and an unknown action (denied). Watch evaluate_action's
     three-way decision.
  2. A hypothetically-extended allowlist adding two real financial actions,
     "transfer_funds" and "wire_funds" -- same real financial risk, but
     only one of their NAMES contains a word requires_confirmation()
     recognizes. Watch one correctly demand human confirmation, and the
     other get silently auto-approved.

Run: python3 code/13-agent-tool-guardrails/agent_guard_demo.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "production-reference", "src"))
import agent_guard  # noqa: E402  (import must follow sys.path setup above)

print("=== Part 1: three actions against the default allowlist ===")
print()
for action in ["read_calendar", "transfer_funds", "delete_the_database"]:
    print(f"{action:24} -> {agent_guard.evaluate_action(action)}")

print()
print("=== Part 2: two equally risky financial actions, one allowlist ===")
print()
EXTENDED_ALLOWLIST = agent_guard._ALLOWED_ACTIONS | {"wire_funds", "transfer_funds"}
for action in ["transfer_funds", "wire_funds"]:
    decision = agent_guard.evaluate_action(action, allowlist=EXTENDED_ALLOWLIST)
    print(f"{action:16} -> {decision}")

print()
print("Both actions move real money. Both are on the SAME allowlist. Only")
print("'transfer_funds' contains a word requires_confirmation() recognizes")
print("as high-risk -- 'wire_funds' means the same thing in different words")
print("and gets auto-approved with no human in the loop at all.")
