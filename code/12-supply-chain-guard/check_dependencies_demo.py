"""
Section 12 -- Supply Chain Guard: a live demo of the real gateway's
dependency-allowlist checker, imported directly from
code/production-reference/scripts/check_dependencies.py -- not a simplified
teaching version, the actual production script (OWASP LLM05).

Two parts:
  1. Run the real check against the real code/production-reference/src/
     directory -- every file, every import, checked against the explicit
     allowlist. Watch it report clean.
  2. Run the SAME checking function against sneaky_dynamic_import.py (in
     this same folder) -- a file that imports a third-party-shaped package
     via the __import__() builtin instead of an `import` statement. Watch
     the static AST-based checker report zero violations, despite a real
     dynamic import sitting right there in the file.

Run: python3 code/12-supply-chain-guard/check_dependencies_demo.py
"""
import os
import pathlib
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "production-reference", "scripts"))
import check_dependencies as cd  # noqa: E402  (import must follow sys.path setup above)

print("=== Part 1: the real check, against the real production-reference/src/ ===")
print()
exit_code = cd.main()
print(f"(exit code: {exit_code})")

print()
print("=== Part 2: the SAME checking function, against a file using __import__() ===")
print()
sneaky_path = pathlib.Path(__file__).parent / "sneaky_dynamic_import.py"
print(f"File: {sneaky_path.name}")
print("Contains: totally_not_vetted = __import__('totally_not_vetted_package')")
print()
disallowed = cd._find_disallowed_imports(sneaky_path, allowed_modules=cd._ALLOWED_TOP_LEVEL_MODULES)
print(f"Disallowed imports found: {disallowed}")
print()
print("Empty list -- the checker walks the AST for Import/ImportFrom nodes")
print("only. __import__() is an ordinary function call as far as the AST is")
print("concerned, indistinguishable from any other call expression. A real")
print("third-party import happened. The static checker never saw it.")
