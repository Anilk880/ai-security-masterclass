"""
secrets_guard.py -- Detects leaked credentials in a message: known-shaped
secrets (AWS keys, GitHub/Slack tokens, "password=...") via regex, plus
secrets with no recognizable shape at all via Shannon-entropy scoring of
long, random-looking token candidates.
"""
import math
import re

_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),                                  # AWS access key id
    re.compile(r"(?i)aws_secret_access_key\s*[:=]\s*\S+"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"),                        # GitHub tokens
    re.compile(r"(?i)\bpassword\s*[:=]\s*\S+"),
    re.compile(r"(?i)\bapi[_-]?key\s*[:=]\s*\S+"),
    re.compile(r"-----BEGIN[ A-Z]*PRIVATE KEY-----"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),                      # Slack tokens
]

# Phase 6.3: generic high-entropy secret detection, for tokens that carry no
# recognizable prefix at all (a bare JWT with no "Bearer " context, a PEM
# body with its "-----BEGIN...-----" wrapper stripped off, a raw random API
# token from a provider not in _PATTERNS above). Restricting the candidate
# charset to base64/base64url-ish characters (no ":", "?", "&", "@", ...)
# is deliberate: it excludes most URLs and sentences outright before entropy
# is even computed, since those routinely contain a scheme/query-string
# character this charset omits.
_CANDIDATE_TOKEN = re.compile(r"[A-Za-z0-9+/=_.-]{24,}")
_ENTROPY_THRESHOLD = 4.3  # bits/char; see docs/architecture.md Phase 6.3 for
                          # the empirical basis (JWTs/PEM bodies score ~4.7-5.5,
                          # ordinary long words/identifiers/hex hashes score ~3.4-3.8)


def _shannon_entropy(token):
    """
    Returns how random/unpredictable `token` looks, in bits per character.
    Ordinary words score low (common letters repeat); real random tokens
    score high (the character set is used close to evenly).
    """
    if not token:
        return 0.0
    counts = {}
    for ch in token:
        counts[ch] = counts.get(ch, 0) + 1
    length = len(token)
    return -sum((count / length) * math.log2(count / length) for count in counts.values())


def _has_high_entropy_token(text):
    """True if any long, token-shaped candidate span in `text` scores at or
    above `_ENTROPY_THRESHOLD` -- catches secrets with no recognizable
    prefix at all, at the cost of the documented false-positive tradeoff
    below.
    """
    # Known, accepted false-positive class (documented, not "fixed"): a
    # legitimate high-entropy public value with no semantic meaning as a
    # secret -- e.g. an npm/yarn lockfile's sha512 integrity hash pasted
    # while debugging a build -- can still score above the threshold and get
    # blocked. This mirrors pii_redactor's own documented Aadhaar
    # false-positive tradeoff: a cheap heuristic catches real secrets with
    # no known prefix at the cost of occasionally flagging a public,
    # non-sensitive high-entropy string. Shadow mode (Phase 6.6) is the
    # intended way to observe and tune this in a specific deployment before
    # hard-blocking on it.
    return any(
        _shannon_entropy(match.group(0)) >= _ENTROPY_THRESHOLD
        for match in _CANDIDATE_TOKEN.finditer(text)
    )


def scan(text):
    """True if `text` contains a known-shaped secret or a high-entropy token."""
    return any(p.search(text) for p in _PATTERNS) or _has_high_entropy_token(text)
