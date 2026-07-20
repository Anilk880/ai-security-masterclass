import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import cost_guard


def test_estimate_tokens_is_roughly_length_over_four():
    assert cost_guard.estimate_tokens("a" * 400) == 100


def test_estimate_tokens_never_returns_zero_for_nonempty_text():
    assert cost_guard.estimate_tokens("hi") >= 1


def test_short_prompt_is_within_budget():
    assert cost_guard.check_cost("What's the weather like today?") is True


def test_prompt_at_default_budget_is_within_budget():
    # 4000 tokens * 4 chars/token = 16000 chars, at the default budget exactly.
    assert cost_guard.check_cost("a" * 16000) is True


def test_prompt_over_default_budget_is_rejected():
    assert cost_guard.check_cost("a" * 16001 * 4) is False


def test_custom_budget_env_var_is_respected(monkeypatch):
    import importlib

    monkeypatch.setenv("MAX_ESTIMATED_TOKENS", "10")
    try:
        reloaded = importlib.reload(cost_guard)
        assert reloaded.check_cost("a" * 44) is False  # 11 estimated tokens > 10
        assert reloaded.check_cost("a" * 40) is True   # 10 estimated tokens == 10
    finally:
        # The module-level constant is only recomputed on import/reload, so
        # explicitly restore it to the default before monkeypatch's own
        # teardown removes the env var -- otherwise every later test in this
        # session would keep seeing the budget-of-10 module state.
        monkeypatch.delenv("MAX_ESTIMATED_TOKENS", raising=False)
        importlib.reload(cost_guard)
