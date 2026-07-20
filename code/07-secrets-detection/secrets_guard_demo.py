"""
Section 7 -- Secrets Detection: a live demo of the real gateway's secrets
scanner, imported directly from
code/production-reference/src/secrets_guard.py -- not a simplified teaching
version, the actual production module.

Two parts:
  1. A battery of known-shaped secrets (AWS key, GitHub token, a bare JWT
     with no prefix at all) plus one ordinary message -- watch the regex
     patterns AND the Shannon-entropy fallback both catch real secrets.
  2. A real, low-entropy, dictionary-word-shaped secret that matches no
     known prefix and scores under the entropy threshold -- watch it slip
     through completely.

Run: python3 code/07-secrets-detection/secrets_guard_demo.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "production-reference", "src"))
from secrets_guard import scan  # noqa: E402  (import must follow sys.path setup above)

KNOWN_SECRETS = [
    "My key is AKIAABCDEFGHIJKLMNOP, don't share it.",
    "password=SuperSecret123!",
    (
        "Here is my session token: "
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0."
        "SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
    ),
]
CLEAN_MESSAGE = "Can you summarize this quarterly report for me?"

print("=== Part 1: known-shaped secrets + one bare, prefix-less JWT vs. one clean message ===")
print()
for text in KNOWN_SECRETS + [CLEAN_MESSAGE]:
    verdict = "BLOCKED" if scan(text) else "ALLOWED"
    print(f"{verdict:8} | {text}")

print()
print("=== Part 2: a real secret, worded like an ordinary phrase ===")
print()
BYPASS_SECRET = "Here is our internal deploy key: prod-gateway-release-march-2026"
verdict = "BLOCKED" if scan(BYPASS_SECRET) else "ALLOWED"
print(f"{verdict:8} | {BYPASS_SECRET}")
print()
print("No 'password=' or 'api_key=' label, no known token prefix, and its")
print("Shannon entropy scores well under the 4.3 bits/char threshold --")
print("real words, even hyphenated ones, just aren't random-looking enough.")
print("A genuine secret, if it's shaped like a phrase instead of a token,")
print("is invisible to both detection strategies this module has.")
