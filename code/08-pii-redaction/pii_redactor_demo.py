"""
Section 8 -- PII Redaction: a live demo of the real gateway's PII redactor,
imported directly from code/production-reference/src/pii_redactor.py -- not
a simplified teaching version, the actual production module.

Two parts:
  1. One message carrying four different PII types at once (email, PAN,
     Aadhaar, credit card) -- watch each get found AND replaced with a
     labeled placeholder, never just silently blocked.
  2. A real, sensitive identifier from OUTSIDE the format list this module
     was built for -- a US Social Security Number -- watch it pass straight
     through untouched.

Run: python3 code/08-pii-redaction/pii_redactor_demo.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "production-reference", "src"))
from pii_redactor import redact  # noqa: E402  (import must follow sys.path setup above)

print("=== Part 1: four PII types in one message ===")
print()
MULTI_PII_MESSAGE = (
    "Email me at anil@example.com or call 9876543210, my Aadhaar is "
    "1234 5678 9012 and my card number is 4111 1111 1111 1111."
)
cleaned, found = redact(MULTI_PII_MESSAGE)
print("Original: ", MULTI_PII_MESSAGE)
print("Redacted: ", cleaned)
print("Found:    ", found)

print()
print("=== Part 2: a real, sensitive ID this module was never built to recognize ===")
print()
US_SSN_MESSAGE = "My SSN is 123-45-6789, please update my file."
cleaned, found = redact(US_SSN_MESSAGE)
print("Original: ", US_SSN_MESSAGE)
print("Redacted: ", cleaned)
print("Found:    ", found)
print()
print("Untouched -- not because the check failed, but because it was never")
print("asked to look for this shape at all. Every one of the five patterns")
print("in _ORDERED_PATTERNS targets an Indian-market identifier format")
print("(Aadhaar, PAN, an Indian mobile prefix). A US SSN was simply never")
print("in scope for this specific module's pattern list.")
