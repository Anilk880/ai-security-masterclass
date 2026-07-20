"""
A deliberately adversarial example file for Section 12's demo -- NOT part
of the real gateway's src/, never imported by anything else in this course.

It imports a third-party-shaped package the way an attacker (or a careless
contributor) actually could: via the __import__() BUILTIN FUNCTION, called
with a string, rather than a Python `import` or `from ... import` STATEMENT.
check_dependencies.py's static checker walks the file's AST looking only
for ast.Import / ast.ImportFrom nodes -- a call to the __import__ builtin
produces neither, so this line is structurally invisible to that check,
even though it does the exact same thing an `import totally_not_vetted`
statement would do.
"""


def load_package(name):
    return __import__(name)


# In a real attack, `name` might not even be a literal string here -- it
# could be built at runtime (e.g. from a config value or decoded from
# base64) to make it even less obvious to a human reviewer skimming the file.
totally_not_vetted = load_package("totally_not_vetted_package")
