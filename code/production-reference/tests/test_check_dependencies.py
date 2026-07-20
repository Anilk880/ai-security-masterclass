import importlib
import os
import subprocess
import sys

_SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
_SCRIPT_PATH = os.path.join(_SCRIPTS_DIR, "check_dependencies.py")

sys.path.insert(0, _SCRIPTS_DIR)
import check_dependencies  # noqa: E402  (import must follow sys.path setup above)


def test_real_src_directory_currently_passes_the_check():
    result = subprocess.run([sys.executable, _SCRIPT_PATH], capture_output=True, text=True)
    assert result.returncode == 0
    assert "OK" in result.stdout


def test_flags_a_disallowed_third_party_import(tmp_path):
    bad_file = tmp_path / "bad_module.py"
    bad_file.write_text("import requests\nfrom flask import Flask\n")

    disallowed = check_dependencies._find_disallowed_imports(bad_file)
    modules_found = {mod for _, mod, _ in disallowed}
    assert modules_found == {"requests", "flask"}


def test_allows_stdlib_imports(tmp_path):
    good_file = tmp_path / "good_module.py"
    good_file.write_text(
        "import re\nimport hashlib\nimport urllib.request\nfrom collections import defaultdict\n"
    )

    disallowed = check_dependencies._find_disallowed_imports(good_file)
    assert disallowed == []


def test_relative_imports_are_not_flagged(tmp_path):
    relative_import_file = tmp_path / "relative_module.py"
    relative_import_file.write_text("from . import sibling\n")

    disallowed = check_dependencies._find_disallowed_imports(relative_import_file)
    assert disallowed == []
