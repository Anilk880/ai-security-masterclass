#!/usr/bin/env python3
"""
Phase 7.2 (OWASP LLM05 -- Supply Chain Vulnerabilities): a lightweight,
dependency-free static check enforcing RiskLumen's own "zero third-party pip
dependencies" design goal (docs/architecture.md, Goals, §2) as an
automatable, testable control rather than just a documented assertion.

Run manually, or wire into CI:
    python scripts/check_dependencies.py

Exits non-zero (and prints exactly what's disallowed) if any file under
src/ imports a module outside the explicit allowlist below.
"""
import ast
import pathlib
import sys

# Everything genuinely available at runtime without adding a pip dependency:
# the Python standard library modules this gateway's src/ files actually use.
_ALLOWED_TOP_LEVEL_MODULES = frozenset({
    "base64",
    "collections",
    "hashlib",
    "hmac",
    "json",
    "math",
    "os",
    "re",
    "sys",
    "time",
    "unicodedata",
    "urllib",
    # Course-local only: openai_client.py imports code/common.py (this
    # course's real/dummy LLM client picker) instead of a shared
    # production secret store, since students run this on their own
    # machine with their own key. Not a pip package, not a supply-chain
    # risk -- it's this repo's own code, one directory up from src/.
    "common",
})

_SRC_DIR = pathlib.Path(__file__).resolve().parent.parent / "src"


def _top_level_module(name):
    """"a.b.c" -> "a" -- only the outermost package name needs to be allowed."""
    return name.split(".")[0]


def _local_module_names():
    """Returns every module name found under src/, so a file importing a
    sibling module (e.g. handler.py importing prompt_guard) is never
    mistaken for a third-party dependency.
    """
    # Every RiskLumen module under src/ is a legitimate sibling import (e.g.
    # handler.py importing prompt_guard) -- not a third-party dependency.
    # Computed from the actual files present, so a newly-added module never
    # needs a matching manual entry here to avoid a false positive.
    if not _SRC_DIR.is_dir():
        return frozenset()
    return frozenset(path.stem for path in _SRC_DIR.glob("*.py"))


def _find_disallowed_imports(path, allowed_modules=None):
    """Parses the Python file at `path` (without executing it) and returns a
    list of (path, module_name, line_number) for every import whose
    top-level module isn't in `allowed_modules`.
    """
    if allowed_modules is None:
        allowed_modules = _ALLOWED_TOP_LEVEL_MODULES | _local_module_names()

    tree = ast.parse(path.read_text(), filename=str(path))
    disallowed = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod = _top_level_module(alias.name)
                if mod not in allowed_modules:
                    disallowed.append((path, mod, node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue  # relative import ("from . import x") -- not a third-party dependency
            mod = _top_level_module(node.module)
            if mod not in allowed_modules:
                disallowed.append((path, mod, node.lineno))
    return disallowed


def main():
    """Checks every file under src/ for disallowed imports, prints what it
    finds, and returns a process exit code (0 = clean, 1 = violation found).
    """
    allowed_modules = _ALLOWED_TOP_LEVEL_MODULES | _local_module_names()
    all_disallowed = []
    for path in sorted(_SRC_DIR.glob("*.py")):
        all_disallowed.extend(_find_disallowed_imports(path, allowed_modules))

    if all_disallowed:
        print("Disallowed imports found (violates the zero-third-party-dependency goal):")
        for path, mod, lineno in all_disallowed:
            print(f"  {path.relative_to(_SRC_DIR.parent)}:{lineno}: import of '{mod}'")
        print(
            "\nIf this is a genuine, deliberate new dependency, add it to "
            "_ALLOWED_TOP_LEVEL_MODULES in this script AND confirm it's "
            "either standard library or a package the deployment already "
            "vets and ships -- adding an unvetted third-party package here "
            "is exactly the supply-chain risk this check exists to catch "
            "(OWASP LLM05)."
        )
        return 1

    print(f"OK -- all imports across {_SRC_DIR} are within the approved allowlist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
