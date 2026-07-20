"""
audit_log.py -- Writes safe, structured audit-log lines for every guard's
decision (blocked/allowed/redacted). Uses one-way hashed identifiers so the
log itself never becomes a second copy of a secret, IP, or API key.
"""
import hashlib
import json
import os
import time


def hash_hint(value):
    """A short, one-way hint derived from a client identifier (or similar
    value), safe to put in a log line -- never the raw value itself. The
    real gateway ships stdout straight to a centralized, longer-retention
    log store, so anything printed here is effectively a second copy of
    whatever is included.
    """
    return hashlib.sha256(value.encode()).hexdigest()[:12]


def is_shadow_mode(check_name):
    """True if `check_name` (e.g. "prompt_guard") is configured to log-only
    rather than actually block, via a `<CHECK_NAME>_SHADOW_MODE` env var
    (Phase 6.6). Lets a check be soft-launched -- observe its false-positive
    rate in production logs before flipping it to a hard block.
    """
    env_var = f"{check_name.upper()}_SHADOW_MODE"
    return os.environ.get(env_var, "false").strip().lower() in ("1", "true", "yes")


def log_event(check, decision, client_hint=None, would_block=None, **extra):
    """Emits one structured JSON line to stdout -- captured automatically by
    the real gateway's centralized log store, no separate logging
    client/dependency needed.

    Phase 6.7 (DPDP-aware audit logging): this function does not itself
    scrub its arguments -- the CALLER is responsible for only ever passing
    categorical information here (which check fired, a redaction TYPE, a
    count, a boolean) and never a raw prompt, response, secret, or PII
    value. Every call site in handler.py that uses this module follows that
    rule; passing a raw sensitive value through `extra` would defeat the
    entire point of an audit log that's meant to be safe to retain and read
    without itself becoming a second exposure surface.
    """
    record = {"ts": time.time(), "check": check, "decision": decision}
    if client_hint is not None:
        record["client_hint"] = client_hint
    if would_block is not None:
        record["would_block"] = would_block
    record.update(extra)
    print(json.dumps(record, sort_keys=True))
