import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import rate_limiter  # noqa: E402  (import must follow sys.path setup above)


@pytest.fixture(autouse=True)
def _reset_rate_limiter_state():
    rate_limiter._reset()
    yield
    rate_limiter._reset()


def _event(api_key="test-client-a", ip="1.2.3.4"):
    return {
        "headers": {"x-api-key": api_key} if api_key else {},
        "requestContext": {"http": {"sourceIp": ip}},
    }


def test_allows_requests_under_the_limit():
    for _ in range(5):  # default RATE_LIMIT_MAX_REQUESTS
        allowed, retry_after = rate_limiter.check(_event())
        assert allowed is True
        assert retry_after == 0


def test_blocks_request_once_limit_is_exceeded():
    for _ in range(5):
        rate_limiter.check(_event())
    allowed, retry_after = rate_limiter.check(_event())
    assert allowed is False
    assert retry_after == 60


def test_different_clients_have_independent_limits():
    for _ in range(5):
        rate_limiter.check(_event(api_key="client-a"))
    # client-a is now at the limit, but a different client should be unaffected
    allowed, _ = rate_limiter.check(_event(api_key="client-b"))
    assert allowed is True


# --- Phase 6.5: dual-key (client_id AND source IP) rate limiting ---

def test_rotating_client_id_from_same_ip_is_still_caught_by_ip_limit():
    # An attacker rotates a fake client_id on every single request, from the
    # same source IP, specifically to dodge the per-client_id limit -- the
    # independent IP-keyed check should still catch this once its own
    # (higher) ceiling is crossed, per Phase 6.5's rate_limiter.check()
    # default RATE_LIMIT_MAX_REQUESTS_PER_IP=20.
    blocked = False
    for i in range(25):
        allowed, _ = rate_limiter.check(_event(api_key=f"rotating-client-{i}", ip="9.9.9.9"))
        if not allowed:
            blocked = True
            break
    assert blocked is True


def test_shared_ip_with_distinct_registered_clients_is_not_falsely_blocked():
    # Several distinct, legitimately-registered client_ids sharing one
    # source IP (e.g. behind a NAT) should not trip the higher IP ceiling
    # just from ordinary, independent usage well under each client's own limit.
    for client in ["client-a", "client-b", "client-c"]:
        for _ in range(3):  # well under both _LIMIT (5) and _LIMIT_PER_IP (20)
            allowed, _ = rate_limiter.check(_event(api_key=client, ip="10.0.0.5"))
            assert allowed is True


def test_repetitive_prompt_is_flagged_after_the_duplicate_limit():
    prompt = "What is the capital of France?"
    for _ in range(3):  # default RATE_LIMIT_MAX_DUPLICATE_PROMPTS
        allowed, _ = rate_limiter.check_repetitive(_event(api_key="scraper-client"), prompt)
        assert allowed is True
    allowed, retry_after = rate_limiter.check_repetitive(_event(api_key="scraper-client"), prompt)
    assert allowed is False
    assert retry_after == 60


def test_varied_prompts_from_same_client_are_not_flagged_as_repetitive():
    prompts = [
        "What is the capital of France?",
        "What is the capital of Germany?",
        "What is the capital of Italy?",
        "What is the capital of Spain?",
        "What is the capital of Portugal?",
    ]
    for prompt in prompts:
        allowed, _ = rate_limiter.check_repetitive(_event(api_key="varied-client"), prompt)
        assert allowed is True


def test_same_prompt_from_different_clients_is_tracked_independently():
    prompt = "What is the capital of France?"
    for _ in range(3):
        rate_limiter.check_repetitive(_event(api_key="client-x"), prompt)
    # A different client asking the identical question should not inherit
    # client-x's duplicate count.
    allowed, _ = rate_limiter.check_repetitive(_event(api_key="client-y"), prompt)
    assert allowed is True


def test_no_api_key_uses_original_single_ip_check_at_the_stricter_limit():
    # With no api_key at all, behavior is unchanged from before Phase 6.5:
    # IP is the only identity, checked once against the stricter _LIMIT (5),
    # not the higher _LIMIT_PER_IP.
    for _ in range(5):
        allowed, _ = rate_limiter.check(_event(api_key=None, ip="8.8.8.8"))
        assert allowed is True
    allowed, retry_after = rate_limiter.check(_event(api_key=None, ip="8.8.8.8"))
    assert allowed is False
    assert retry_after == 60
