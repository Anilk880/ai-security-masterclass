import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import agent_guard


def test_known_action_is_allowed():
    assert agent_guard.is_action_allowed("read_calendar") is True


def test_unknown_action_is_not_allowed():
    assert agent_guard.is_action_allowed("delete_database") is False


def test_custom_allowlist_overrides_default():
    assert agent_guard.is_action_allowed("transfer_funds", allowlist={"transfer_funds"}) is True
    assert agent_guard.is_action_allowed("read_calendar", allowlist={"transfer_funds"}) is False


def test_high_risk_action_names_require_confirmation():
    for name in ["delete_account", "send_email", "pay_invoice", "transfer_funds",
                 "purchase_item", "cancel_subscription"]:
        assert agent_guard.requires_confirmation(name) is True


def test_low_risk_action_names_do_not_require_confirmation():
    for name in ["read_calendar", "read_weather", "search_documents", "get_order_status"]:
        assert agent_guard.requires_confirmation(name) is False


def test_evaluate_action_denies_unknown_action():
    assert agent_guard.evaluate_action("delete_everything") == "denied"


def test_evaluate_action_allows_known_low_risk_action():
    assert agent_guard.evaluate_action("read_weather") == "allowed"


def test_evaluate_action_requires_confirmation_for_known_high_risk_action():
    custom_allowlist = {"transfer_funds", "read_calendar"}
    assert agent_guard.evaluate_action("transfer_funds", allowlist=custom_allowlist) == "requires_confirmation"


def test_evaluate_action_denied_takes_priority_over_high_risk_pattern():
    # "transfer_funds" matches the high-risk pattern, but since it's not in
    # the default allowlist at all, the correct decision is still "denied",
    # not "requires_confirmation" -- least-privilege is checked first.
    assert agent_guard.evaluate_action("transfer_funds") == "denied"
