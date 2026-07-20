"""
Section 5 -- Rate Limiting: a live demo of the real gateway's sliding-window
limiter, imported directly from code/production-reference/src/rate_limiter.py
-- not a simplified reimplementation, the actual production module.

Two parts:
  1. One client fires requests faster than the window allows -- watch the
     sliding window trip and start returning retry_after.
  2. An attacker tries to dodge the per-client_id limit by rotating a fake
     api_key on every single request, from one source IP -- watch the
     independent, higher-ceiling IP-level check catch it anyway (Phase 6.5's
     dual-key design in rate_limiter.check()).

Run: python3 code/05-rate-limiting/rate_limit_demo.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "production-reference", "src"))
import rate_limiter  # noqa: E402  (import must follow sys.path setup above)


def _event(api_key, ip):
    return {
        "headers": {"x-api-key": api_key} if api_key else {},
        "requestContext": {"http": {"sourceIp": ip}},
    }


print("=== Part 1: one client, sending requests faster than the window allows ===")
print(f"Limit: {rate_limiter._LIMIT} requests per {rate_limiter._WINDOW_SECONDS}s, per client_id.")
print()

for i in range(1, 7):
    allowed, retry_after = rate_limiter.check(_event(api_key="honest-client", ip="203.0.113.5"))
    status = "ALLOWED" if allowed else f"BLOCKED (retry after {retry_after}s)"
    print(f"Request {i}: {status}")

print()
print("=== Part 2: an attacker rotates a fake client_id on every request, same IP ===")
print(f"Per-client_id limit: {rate_limiter._LIMIT}   Per-IP limit: {rate_limiter._LIMIT_PER_IP}")
print()

rate_limiter._reset()
blocked_at = None
for i in range(1, 26):
    allowed, retry_after = rate_limiter.check(
        _event(api_key=f"rotating-client-{i}", ip="198.51.100.9")
    )
    status = "ALLOWED" if allowed else f"BLOCKED (retry after {retry_after}s)"
    print(f"Request {i} (client_id=rotating-client-{i}): {status}")
    if not allowed and blocked_at is None:
        blocked_at = i
        break

print()
print(f"Rotating client_id never once hit ITS OWN limit -- each new client_id starts")
print(f"a fresh count. It still got caught at request {blocked_at}, because every one of")
print("those requests shared the same source IP, and the independent IP-level check")
print(f"has its own ceiling ({rate_limiter._LIMIT_PER_IP}) that doesn't reset just because the client_id did.")
