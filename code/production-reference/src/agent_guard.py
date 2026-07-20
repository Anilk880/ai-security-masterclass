"""
agent_guard.py -- Least-privilege guardrail for future AI "tool calling" /
agent actions: an explicit allowlist of permitted actions, plus a rule that
any high-risk action always requires human confirmation before it runs.
"""
import re

_TOKEN_SPLIT = re.compile(r"[_\s-]+")

# NOTE: RiskLumen does not currently implement any tool-calling/agent
# execution path -- there is nothing in handler.py that lets a request name
# an action for the model to actually perform. This module is a
# forward-compatible guardrail: it demonstrates the least-privilege
# allowlist + mandatory-human-confirmation-on-high-risk-actions pattern
# (OWASP LLM07 Insecure Plugin Design / LLM08 Excessive Agency) so that
# WHEN tool-calling is added, it's wired through a real, tested control from
# day one rather than retrofitted after the fact. It is not yet called from
# handler.py.

# The explicit allowlist of actions a future tool-calling/agent integration
# would be permitted to request at all. Anything not in this set is refused
# outright -- least-privilege by default, rather than a denylist of known-bad
# actions (which is always incomplete against a model that can phrase a
# request however it likes).
_ALLOWED_ACTIONS = frozenset({
    "read_calendar",
    "read_weather",
    "search_documents",
    "get_order_status",
})

# Actions whose name contains any of these words (split on "_"/"-"/space, so
# a snake_case or kebab-case action name like "transfer_funds" is correctly
# tokenized into ["transfer", "funds"]) are never auto-executed -- they
# require an explicit, separate human-in-the-loop confirmation step before
# actually running, regardless of how confident the model's own request
# seemed.
_HIGH_RISK_WORDS = frozenset({"delete", "send", "pay", "transfer", "purchase", "cancel"})


def is_action_allowed(action_name, allowlist=_ALLOWED_ACTIONS):
    """True if `action_name` is in the explicit allowlist at all. This is
    the first, least-privilege gate: refuse anything not explicitly
    enumerated, rather than trying to maintain a denylist of known-bad
    actions.
    """
    return action_name in allowlist


def requires_confirmation(action_name):
    """True if any token in `action_name` is a high-risk word -- and so must
    never be auto-executed, even if the action is in the allowlist, without
    a separate, explicit human-in-the-loop confirmation step first.
    """
    tokens = _TOKEN_SPLIT.split(action_name.lower())
    return any(token in _HIGH_RISK_WORDS for token in tokens)


def evaluate_action(action_name, allowlist=_ALLOWED_ACTIONS):
    """Combines both checks into the one decision a caller needs: returns
    "denied", "requires_confirmation", or "allowed".
    """
    if not is_action_allowed(action_name, allowlist):
        return "denied"
    if requires_confirmation(action_name):
        return "requires_confirmation"
    return "allowed"
