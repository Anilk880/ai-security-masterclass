"""
rate_limiter.py -- Sliding-window request counting: caps how many requests
a client (by API key and/or source IP) may make per window, plus a
separate, stricter cap on exact-duplicate prompts.

Adapted for this course: the real, deployed gateway backs this with a
shared, persistent database, so counts survive restarts and are shared
across concurrent server instances. This course-local copy swaps that for
a plain in-process dict -- same sliding-window algorithm, same public
functions, just not persisted or shared across processes. That's the only
thing that changed; every guard decision below is identical to the real
gateway's.
"""
import hashlib
import os
import time
from collections import defaultdict

_LIMIT = int(os.environ.get("RATE_LIMIT_MAX_REQUESTS", "5"))
# Phase 6.5: a separate, higher ceiling for the IP dimension than the
# per-client_id limit above -- several distinct, legitimately-registered
# client_ids can share one source IP (an office NAT, a mobile carrier CGNAT
# pool), so the IP-level check needs enough headroom not to false-positive
# on that, while still bounding an attacker's ability to defeat _LIMIT by
# simply rotating a fake client_id on every request from one machine.
_LIMIT_PER_IP = int(os.environ.get("RATE_LIMIT_MAX_REQUESTS_PER_IP", "20"))
_WINDOW_SECONDS = int(os.environ.get("RATE_LIMIT_WINDOW_SECONDS", "60"))
# Phase 7.5 (OWASP LLM10 -- Model Theft/abuse): a much stricter threshold
# than ordinary volumetric limiting, applied only to EXACT-duplicate prompts
# from the same client within the window -- a pattern more indicative of
# scraping/model-extraction scripting than of normal, varied human usage.
_DUPLICATE_PROMPT_LIMIT = int(os.environ.get("RATE_LIMIT_MAX_DUPLICATE_PROMPTS", "3"))

# client_id -> list of request timestamps (ms), the in-process stand-in for
# the real gateway's shared, persistent database.
_store = defaultdict(list)


def _reset():
    """Test-only: clears all in-memory state between test cases, the same
    isolation a fresh database gave each test in the real gateway's suite."""
    _store.clear()


def _source_ip_client_id(event):
    """Builds a one-way-hashed tracking key from the request's source IP."""
    source_ip = (
        event.get("requestContext", {}).get("http", {}).get("sourceIp", "unknown")
    )
    return "ip:" + hashlib.sha256(source_ip.encode()).hexdigest()


def _check_window(client_id, limit):
    """One exact-sliding-window check for a single (client_id, limit) pair.
    Returns (allowed: bool, retry_after_seconds: int)."""
    now_ms = int(time.time() * 1000)
    window_start_ms = now_ms - _WINDOW_SECONDS * 1000

    timestamps = _store[client_id]
    # Drop anything that's aged out of the window before counting.
    timestamps[:] = [ts for ts in timestamps if ts >= window_start_ms]

    if len(timestamps) >= limit:
        return False, _WINDOW_SECONDS

    timestamps.append(now_ms)
    return True, 0


def check(event):
    """Returns (allowed: bool, retry_after_seconds: int).

    Phase 6.5 (dual-key limiting): when a client-identifying api_key is
    present, the request is checked against BOTH its own per-client_id
    window (the original, stricter _LIMIT) AND an independent, higher-
    ceiling per-source-IP window (_LIMIT_PER_IP) -- so an attacker rotating
    a fake api_key on every request from one machine still gets caught once
    the IP dimension's own threshold is crossed; rotating the client_id
    alone no longer resets that count. With no api_key at all, IP is the
    only identity available and is checked once, at the original _LIMIT --
    unchanged from pre-Phase-6.5 behavior.
    """
    headers = event.get("headers") or {}
    api_key = headers.get("x-api-key") or headers.get("X-Api-Key")
    ip_client_id = _source_ip_client_id(event)

    if not api_key:
        return _check_window(ip_client_id, _LIMIT)

    allowed, retry_after = _check_window(f"key:{api_key}", _LIMIT)
    if not allowed:
        return False, retry_after
    return _check_window(ip_client_id, _LIMIT_PER_IP)


def _identity(event):
    """The same client-identity string check() uses, minus the "key:"/"ip:"
    prefix distinction mattering here -- just something stable to key the
    duplicate-prompt window on.
    """
    headers = event.get("headers") or {}
    api_key = headers.get("x-api-key") or headers.get("X-Api-Key")
    return f"key:{api_key}" if api_key else _source_ip_client_id(event)


def check_repetitive(event, prompt):
    """Returns (allowed: bool, retry_after_seconds: int).

    Phase 7.5 (OWASP LLM10 -- Model Theft/abuse): flags a client sending
    many EXACT-duplicate prompts in a short window -- a pattern distinct
    from ordinary volumetric rate limiting (check(), above) and more
    indicative of a scraping/model-extraction script replaying the same
    query than of normal, varied human usage. Reuses the same sliding-window
    mechanism as check(), keyed by client identity PLUS a hash of the
    prompt's own content, so it only trips on genuinely repeated requests,
    not on ordinary varied usage from the same client.
    """
    prompt_digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
    dup_client_id = f"dup:{_identity(event)}:{prompt_digest}"
    return _check_window(dup_client_id, _DUPLICATE_PROMPT_LIMIT)
