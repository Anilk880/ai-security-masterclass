"""
Section 10 -- Cost/DoS Guard: a live demo of the real gateway's token-cost
estimator, imported directly from code/production-reference/src/cost_guard.py
-- not a simplified teaching version, the actual production module.

Two parts:
  1. A short, ordinary request vs. a genuinely oversized one -- watch the
     cheap chars-per-token estimate correctly allow one and reject the
     other.
  2. A long, dense non-English (CJK) request -- the module's own
     chars-per-4 heuristic drastically UNDER-counts its real cost. Compared
     against tiktoken (the actual tokenizer this course's real backend
     uses), the request the estimate calls "well under budget" is actually
     well OVER it.

Run: python3 code/10-cost-dos-guard/cost_guard_demo.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "production-reference", "src"))
import cost_guard  # noqa: E402  (import must follow sys.path setup above)

print("=== Part 1: an ordinary request vs. a genuinely oversized one ===")
print()
SHORT_REQUEST = "Summarize the key risks of prompt injection in two sentences."
LONG_REQUEST = "Please explain in extreme detail. " * 500

for label, text in [("Short request", SHORT_REQUEST), ("Oversized request", LONG_REQUEST)]:
    est = cost_guard.estimate_tokens(text)
    verdict = "ALLOWED" if cost_guard.check_cost(text) else "BLOCKED"
    print(f"{label}: {len(text)} chars, estimated {est} tokens (budget {cost_guard._MAX_ESTIMATED_TOKENS}) -> {verdict}")

print()
print("=== Part 2: a long, dense CJK request -- estimate vs. REAL tokenizer ===")
print()
CJK_UNIT = "人工智能安全是一个非常重要的话题,我们需要认真对待每一个细节。"
CJK_REQUEST = CJK_UNIT * 195

est = cost_guard.estimate_tokens(CJK_REQUEST)
verdict = "ALLOWED" if cost_guard.check_cost(CJK_REQUEST) else "BLOCKED"
print(f"chars: {len(CJK_REQUEST)}")
print(f"cost_guard's estimate: {est} tokens (budget {cost_guard._MAX_ESTIMATED_TOKENS}) -> {verdict}")

import tiktoken  # noqa: E402
encoder = tiktoken.get_encoding("cl100k_base")
real_tokens = len(encoder.encode(CJK_REQUEST))
print(f"REAL tiktoken token count: {real_tokens}")
over_by = real_tokens - cost_guard._MAX_ESTIMATED_TOKENS
print(f"Actually over budget by {over_by} tokens -- the estimate said this request was safely under it.")
