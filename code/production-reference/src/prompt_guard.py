"""
prompt_guard.py -- Detects common prompt-injection / AI-manipulation
phrases (e.g. "ignore your previous instructions") using a fixed list of
regular expressions. A denylist smoke detector, not a judge of intent.
"""
import re

_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in [
        r"ignore\s+(all\s+)?(the\s+)?previous\s+instructions",
        r"ignore\s+(the\s+)?above\s+instructions",
        r"disregard\s+(your|the)\s+(system|original)\s+prompt",
        r"you\s+are\s+now\s+in\s+(developer|dan|jailbreak)\s+mode",
        r"act\s+as\s+if\s+you\s+have\s+no\s+restrictions",
        r"pretend\s+you\s+have\s+no\s+(rules|restrictions)",
        r"forget\s+(everything|all)\s+(you\s+)?(know|learned|were\s+told)",
        r"reveal\s+your\s+(system\s+)?prompt",
        r"this\s+is\s+a\s+jailbreak",
        r"<script[\s>]",
        r"javascript:",
    ]
]


def scan(text):
    """True if `text` matches any known prompt-injection phrase."""
    return any(p.search(text) for p in _PATTERNS)
