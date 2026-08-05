"""Every check slug is declared by the module that raises it.

`WaiverRegister.stale_findings` judges a waiver only when the running command
declares it ran that check. The declaration is a hand-written `CHECKS` set per
module, so the failure mode is drift: add a check, forget to declare it, and
no command ever judges a waiver for it — the entry sits in the register
forever and nothing says so. That failure is silent, which is exactly the kind
this test exists to make loud.

The slugs are read back out of the source with `ast`, not by running anything:
a check that only fires on a rare input would otherwise never be observed.
"""

import ast
from importlib import import_module
from pathlib import Path

import pytest

from detangle import registers, tables
from detangle.graph import emit
from detangle.records import checks as record_checks
from detangle.records import load as records_load
from detangle.views import glossary

SRC = Path(__file__).resolve().parents[1] / "src" / "detangle"

# `detangle.graph` re-exports the *function* `build`, which shadows the
# submodule of the same name, so this one is fetched by module path.
graph_build = import_module("detangle.graph.build")

DECLARED = {
    "records/checks.py": record_checks.CHECKS,
    "records/load.py": records_load.CHECKS,
    "registers.py": registers.CHECKS,
    "tables.py": tables.CHECKS,
    "graph/build.py": graph_build.CHECKS,
    "graph/emit.py": emit.CHECKS,
    "views/glossary.py": glossary.CHECKS,
}


def slugs_in(path: Path) -> set[str]:
    """The first string argument of every `error(...)` / `warn(...)` call.

    `Finding(...)` takes severity first, so its slug is the second argument.
    """
    found: set[str] = set()
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
            continue
        if node.func.id not in ("error", "warn", "Finding"):
            continue
        i = 1 if node.func.id == "Finding" else 0
        if len(node.args) > i and isinstance(node.args[i], ast.Constant):
            value = node.args[i].value
            if isinstance(value, str):
                found.add(value)
    return found


@pytest.mark.parametrize("rel", sorted(DECLARED))
def test_a_module_declares_exactly_the_checks_it_raises(rel):
    assert slugs_in(SRC / rel) == set(DECLARED[rel])


def test_no_undeclared_module_raises_findings():
    """A new module with checks in it must join the table above."""
    for path in sorted(SRC.rglob("*.py")):
        rel = path.relative_to(SRC).as_posix()
        if rel in DECLARED:
            continue
        assert slugs_in(path) == set(), f"{rel} raises undeclared checks"
