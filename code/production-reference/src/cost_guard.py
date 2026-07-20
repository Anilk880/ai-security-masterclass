"""
cost_guard.py -- Estimates the token cost of a request and rejects anything
over budget, protecting the billed LLM backend from oversized/expensive
requests (OWASP LLM04: Model Denial of Service).
"""
import os

# A commonly-cited rule of thumb for English text with GPT-style tokenizers
# is roughly 4 characters per token. This is deliberately approximate --
# adding a real tokenizer dependency would violate the project's
# zero-third-party-dependency goal (see scripts/check_dependencies.py) for a
# check whose job is only to catch grossly oversized/expensive requests
# before they reach the LLM, not to bill precisely.
_CHARS_PER_TOKEN_ESTIMATE = 4
_MAX_ESTIMATED_TOKENS = int(os.environ.get("MAX_ESTIMATED_TOKENS", "4000"))


def estimate_tokens(text):
    """A rough, dependency-free token-count estimate for `text`."""
    return max(1, len(text) // _CHARS_PER_TOKEN_ESTIMATE)


def check_cost(text):
    """True if `text`'s estimated token count is within the configured
    budget (Phase 7.1 -- OWASP LLM04 Model Denial of Service). This is a
    distinct, cost-oriented control from the raw request-size cap
    (Phase 6.4): the byte cap defends against CPU/ReDoS abuse on the
    gateway's own regex checks, while this defends against sending an
    unreasonably expensive request onward to the billed LLM backend, and can
    be tuned independently of the security-motivated byte limit.
    """
    return estimate_tokens(text) <= _MAX_ESTIMATED_TOKENS
