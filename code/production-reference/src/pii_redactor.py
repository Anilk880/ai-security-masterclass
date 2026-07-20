"""
pii_redactor.py -- Finds and blacks out personal information (emails, phone
numbers, card numbers, government ID numbers) in a message, replacing each
with a [REDACTED_<TYPE>] placeholder rather than blocking the request.
"""
import re

# Order matters: matched spans are replaced with a non-digit/non-alnum
# placeholder before the next pattern runs, so longer/more-specific shapes
# must be checked before shorter ones that could otherwise match a substring
# of an already-redacted value.
_ORDERED_PATTERNS = [
    ("EMAIL", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("PAN_ID", re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b")),
    ("CREDIT_CARD", re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{1,4}\b")),
    ("AADHAAR_ID", re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b")),
    ("PHONE_NUMBER", re.compile(r"\b(?:\+\d{1,3}[-\s]?)?[6-9]\d{9}\b")),
]


def redact(text):
    """
    Replaces every recognized PII match in `text` with a
    [REDACTED_<LABEL>] placeholder. Returns (cleaned_text, found_labels) --
    found_labels lists only the CATEGORIES found (e.g. ["EMAIL"]), never the
    actual sensitive values, so it's always safe to write to a log line.
    """
    found = []

    for label, pattern in _ORDERED_PATTERNS:
        def _sub(match, label=label):
            found.append(label)
            return f"[REDACTED_{label}]"

        text = pattern.sub(_sub, text)

    return text, found
