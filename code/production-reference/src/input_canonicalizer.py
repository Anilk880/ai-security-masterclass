"""
input_canonicalizer.py -- Produces a normalized copy of the input text for
prompt_guard/secrets_guard to SCAN (never what's actually redacted or sent
onward), so invisible Unicode characters and base64-encoded spans can't be
used to hide a known-bad phrase or secret from those regex-based checks.
"""
import base64
import re
import unicodedata

# Zero-width and other invisible/format characters sometimes used to split a
# forbidden phrase so a literal regex match no longer sees it as one token
# (e.g. "ignore​previous​instructions").
_INVISIBLE_CHARS = re.compile(
    "[" + "".join([
        "​",  # zero-width space
        "‌",  # zero-width non-joiner
        "‍",  # zero-width joiner
        "⁠",  # word joiner
        "﻿",  # zero-width no-break space / BOM
    ]) + "]"
)

# Long base64-alphabet spans worth attempting to decode and append (not
# replace) to the scanning text, so a phrase or secret hidden entirely inside
# a base64 blob is still visible to prompt_guard/secrets_guard's patterns.
# Minimum length keeps this from firing on short, ordinary-looking tokens.
_BASE64_SPAN = re.compile(r"\b[A-Za-z0-9+/]{24,}={0,2}\b")


def normalize_for_scanning(text):
    """Returns a normalized copy of `text` for prompt_guard/secrets_guard to
    scan, so that Unicode confusables, invisible characters, and base64-encoded
    spans can't be used to slip a known-bad phrase or secret past the regex
    checks. The ORIGINAL text (not this normalized copy) is still what's
    redacted and forwarded to the LLM -- this function only affects what the
    block-decision checks see, never what the caller/model actually receives.
    """
    normalized = unicodedata.normalize("NFKC", text)

    # Invisible characters are used two opposite ways, needing opposite fixes:
    # (1) mid-word, to break a single forbidden word's own literal match (e.g.
    #     "ig<ZWSP>nore") -- deleting the character reassembles "ignore".
    # (2) as a fake inter-word separator, replacing a real space (e.g.
    #     "ignore<ZWSP>previous<ZWSP>instructions") -- deleting it merges the
    #     words into one token and defeats an "ignore\s+previous" pattern that
    #     requires whitespace between them; only replacing it WITH a space
    #     catches this variant. Scanning both variants catches either.
    stripped = _INVISIBLE_CHARS.sub("", normalized)
    spaced = _INVISIBLE_CHARS.sub(" ", normalized)
    combined = stripped if stripped == spaced else stripped + "\n" + spaced

    return _append_decoded_base64_spans(combined)


def _append_decoded_base64_spans(text):
    """
    Finds long base64-alphabet spans in `text`, decodes any that decode
    cleanly into printable text, and appends those decoded chunks (the
    original span is kept too, not replaced) so hidden content becomes
    visible to the scanners downstream.
    """
    decoded_chunks = []
    for match in _BASE64_SPAN.finditer(text):
        candidate = match.group(0)
        # Pad to a multiple of 4 defensively; base64.b64decode requires it.
        padded = candidate + "=" * (-len(candidate) % 4)
        try:
            decoded = base64.b64decode(padded, validate=True).decode("utf-8")
        except Exception:
            continue
        if decoded.isprintable():
            decoded_chunks.append(decoded)

    if not decoded_chunks:
        return text
    return text + "\n" + "\n".join(decoded_chunks)
