"""
handler.py -- The gateway's entry point and main pipeline: authenticates
the caller, then runs every guard (rate limiting, prompt-injection,
secrets, PII redaction, cost) on the inbound message, calls the AI model,
scans its reply too, and returns the final response.

Adapted for this course: the real, deployed gateway fetches its shared
auth secret from a shared secret store, common to every server instance.
This course-local copy reads it from an environment variable instead
(GATEWAY_SHARED_SECRET in .env, defaulting to a fixed local-dev value so
the test suite and a local run both work with zero setup) -- everything
from here down, the entire guard pipeline, is identical to the real
gateway's.
"""
import hmac
import json
import os

import audit_log
import cost_guard
import input_canonicalizer
import openai_client
import pii_redactor
import prompt_guard
import rate_limiter
import secrets_guard

_MAX_REQUEST_BYTES = int(os.environ.get("MAX_REQUEST_BYTES", "16384"))
_GATEWAY_SHARED_SECRET = os.environ.get("GATEWAY_SHARED_SECRET", "local-dev-secret-change-me")


def _get_gateway_secret():
    """Returns the shared gateway secret used to authenticate callers."""
    return _GATEWAY_SHARED_SECRET


def _client_hint(event):
    """Returns a one-way-hashed hint identifying the caller (from their API
    key if present, else their source IP), safe to write into audit_log lines.
    """
    # A one-way hint for audit_log lines -- never the raw api_key/IP itself,
    # per architecture.md Phase 6.7's DPDP-aware audit logging requirement.
    headers = event.get("headers") or {}
    api_key = headers.get("x-api-key") or headers.get("X-Api-Key")
    if api_key:
        return audit_log.hash_hint(f"key:{api_key}")
    source_ip = event.get("requestContext", {}).get("http", {}).get("sourceIp", "unknown")
    return audit_log.hash_hint(f"ip:{source_ip}")


def handler(event, context):
    """
    The gateway's entry point, invoked for every incoming request. Runs the
    full guard pipeline in order (auth, size cap, rate limiting, prompt
    injection, secrets, PII redaction, cost, the AI call, then egress
    scanning of the AI's own reply) and returns an HTTP-shaped response dict.
    """
    client_hint = _client_hint(event)

    headers = event.get("headers") or {}
    provided_secret = headers.get("x-gateway-secret") or headers.get("X-Gateway-Secret") or ""
    if not hmac.compare_digest(provided_secret, _get_gateway_secret()):
        audit_log.log_event("auth", "blocked", client_hint=client_hint)
        return _response(403, {"error": "unauthorized"})

    raw_body = event.get("body") or "{}"
    # Phase 6.4: reject oversized payloads before spending any CPU on
    # json.loads or the regex-based checks further down the pipeline --
    # a cheap defense against large-payload CPU/ReDoS-style abuse.
    if len(raw_body.encode("utf-8")) > _MAX_REQUEST_BYTES:
        audit_log.log_event(
            "request_size", "blocked", client_hint=client_hint,
            size_bytes=len(raw_body.encode("utf-8")),
        )
        return _response(413, {"error": "payload_too_large"})

    try:
        body = json.loads(raw_body)
    except json.JSONDecodeError:
        return _response(400, {"error": "invalid_json"})

    prompt = body.get("prompt")
    if not isinstance(prompt, str):
        return _response(400, {"error": "missing_prompt"})

    allowed, retry_after = rate_limiter.check(event)
    if not allowed:
        if audit_log.is_shadow_mode("rate_limiter"):
            audit_log.log_event("rate_limiter", "allowed", client_hint=client_hint, would_block=True)
        else:
            audit_log.log_event("rate_limiter", "blocked", client_hint=client_hint)
            return _response(
                429, {"error": "rate_limit_exceeded", "retry_after_seconds": retry_after}
            )

    # Phase 7.5 (OWASP LLM10 -- Model Theft/abuse): distinct from ordinary
    # volumetric rate limiting above -- this flags a client sending many
    # EXACT-duplicate prompts in a short window, more indicative of a
    # scraping/model-extraction script than of normal, varied usage.
    dup_allowed, dup_retry_after = rate_limiter.check_repetitive(event, prompt)
    if not dup_allowed:
        if audit_log.is_shadow_mode("rate_limiter_repetitive"):
            audit_log.log_event("rate_limiter_repetitive", "allowed", client_hint=client_hint, would_block=True)
        else:
            audit_log.log_event("rate_limiter_repetitive", "blocked", client_hint=client_hint)
            return _response(
                429, {"error": "repetitive_query_detected", "retry_after_seconds": dup_retry_after}
            )

    # Phase 6.2: scan a canonicalized copy so encoding tricks/invisible
    # characters can't slip a known-bad phrase past the regex checks below --
    # the ORIGINAL `prompt` (not this normalized copy) is still what gets
    # redacted and forwarded to the LLM further down.
    scan_text = input_canonicalizer.normalize_for_scanning(prompt)

    if prompt_guard.scan(scan_text):
        if audit_log.is_shadow_mode("prompt_guard"):
            audit_log.log_event("prompt_guard", "allowed", client_hint=client_hint, would_block=True)
        else:
            audit_log.log_event("prompt_guard", "blocked", client_hint=client_hint)
            return _response(403, {"error": "prompt_injection_detected"})

    if secrets_guard.scan(scan_text):
        if audit_log.is_shadow_mode("secrets_guard"):
            audit_log.log_event("secrets_guard", "allowed", client_hint=client_hint, would_block=True)
        else:
            audit_log.log_event("secrets_guard", "blocked", client_hint=client_hint)
            return _response(403, {"error": "secret_leak_detected"})

    sanitized_prompt, redactions = pii_redactor.redact(prompt)
    if redactions:
        audit_log.log_event("pii_redactor", "redacted", client_hint=client_hint, redaction_types=redactions)

    # Phase 7.1 (OWASP LLM04 -- Model Denial of Service): reject requests
    # whose estimated token cost exceeds budget, distinct from the raw
    # byte-size cap (Phase 6.4) -- this defends against sending an
    # unreasonably expensive request onward to the billed LLM backend, not
    # against CPU/ReDoS abuse on the gateway's own regex checks.
    if not cost_guard.check_cost(sanitized_prompt):
        audit_log.log_event(
            "cost_guard", "blocked", client_hint=client_hint,
            estimated_tokens=cost_guard.estimate_tokens(sanitized_prompt),
        )
        return _response(413, {"error": "estimated_token_budget_exceeded"})

    try:
        llm_response = openai_client.ask(sanitized_prompt)
    except openai_client.OpenAIError:
        return _response(502, {"error": "llm_upstream_error"})

    # Phase 6.1: egress scanning -- run the same secrets/PII checks on the
    # model's OWN response, symmetric to the inbound checks above, so a
    # secret or PII value that leaks back out via the model's output (rather
    # than the user's input) is still caught before it ever reaches the caller.
    if secrets_guard.scan(llm_response):
        if audit_log.is_shadow_mode("secrets_guard_egress"):
            audit_log.log_event("secrets_guard_egress", "allowed", client_hint=client_hint, would_block=True)
        else:
            audit_log.log_event("secrets_guard_egress", "blocked", client_hint=client_hint)
            return _response(502, {"error": "llm_response_blocked_secret_leak"})

    sanitized_response, response_redactions = pii_redactor.redact(llm_response)
    if response_redactions:
        audit_log.log_event(
            "pii_redactor_egress", "redacted", client_hint=client_hint,
            redaction_types=response_redactions,
        )

    audit_log.log_event("request", "completed", client_hint=client_hint)

    return _response(
        200,
        {
            "sanitized_prompt": sanitized_prompt,
            "redactions": redactions,
            "llm_response": sanitized_response,
            "response_redactions": response_redactions,
            # Phase 7.4 (OWASP LLM09 -- Overreliance): a lightweight, always-
            # present reminder that this content is model-generated and
            # unverified, since the gateway's other checks establish *safety*
            # (no injected instructions, no leaked secrets/PII) but say
            # nothing about the *factual accuracy* of what the model said.
            "advisory": "AI-generated response -- verify important facts independently.",
        },
    )


def _response(status_code, body_dict):
    """Builds the HTTP-shaped response dict the gateway returns to the caller."""
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body_dict),
    }
