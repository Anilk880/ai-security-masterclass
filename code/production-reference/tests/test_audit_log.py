import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import audit_log


def test_hash_hint_is_deterministic_and_does_not_contain_the_raw_value():
    hint_a = audit_log.hash_hint("key:super-secret-api-key")
    hint_b = audit_log.hash_hint("key:super-secret-api-key")
    assert hint_a == hint_b
    assert "super-secret-api-key" not in hint_a
    assert len(hint_a) == 12


def test_hash_hint_differs_for_different_inputs():
    assert audit_log.hash_hint("client-a") != audit_log.hash_hint("client-b")


def test_is_shadow_mode_defaults_to_false(monkeypatch):
    monkeypatch.delenv("PROMPT_GUARD_SHADOW_MODE", raising=False)
    assert audit_log.is_shadow_mode("prompt_guard") is False


def test_is_shadow_mode_true_variants(monkeypatch):
    for value in ["true", "True", "1", "yes", "YES"]:
        monkeypatch.setenv("SECRETS_GUARD_SHADOW_MODE", value)
        assert audit_log.is_shadow_mode("secrets_guard") is True


def test_is_shadow_mode_false_variants(monkeypatch):
    for value in ["false", "0", "no", ""]:
        monkeypatch.setenv("RATE_LIMITER_SHADOW_MODE", value)
        assert audit_log.is_shadow_mode("rate_limiter") is False


def test_log_event_prints_one_valid_json_line(capsys):
    audit_log.log_event("prompt_guard", "blocked", client_hint="abc123def456", would_block=True)
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record["check"] == "prompt_guard"
    assert record["decision"] == "blocked"
    assert record["client_hint"] == "abc123def456"
    assert record["would_block"] is True
    assert "ts" in record


def test_log_event_extra_fields_are_included(capsys):
    audit_log.log_event("pii_redactor", "redacted", redaction_types=["EMAIL", "PAN_ID"], redaction_count=2)
    record = json.loads(capsys.readouterr().out.strip())
    assert record["redaction_types"] == ["EMAIL", "PAN_ID"]
    assert record["redaction_count"] == 2
