"""The structural safety test for this project's central design claim
(PROJECT.md Section 11): "the Supervisor Agent... does not directly query
raw department systems itself"; "What should NOT be exposed to the
Supervisor Agent: direct raw access to any department's underlying
system." This statically parses every file in `supervisor/` and asserts
none of them import `revops` or `investigator` -- the only modules allowed
to import those are the two adapters in `specialists/`, which is exactly
where "delegating to the specialist as a bounded subtask" is supposed to
happen. This is the same class of proof as project 10's
`test_architectural_separation.py`, applied here to two genuinely separate,
independently-built codebases rather than two modules in one repo -- a
stronger, more concrete instance of the same architectural principle.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

SRC_ROOT = Path(__file__).resolve().parents[1] / "src" / "execos"
SUPERVISOR_DIR = SRC_ROOT / "supervisor"
FORBIDDEN_MODULES = {"revops", "investigator"}


def _imported_top_level_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.add(node.module.split(".")[0])
    return modules


@pytest.mark.parametrize("path", sorted(SUPERVISOR_DIR.glob("*.py")), ids=lambda p: p.name)
def test_supervisor_module_never_imports_a_specialist_project_directly(path: Path):
    imported = _imported_top_level_modules(path)
    hits = imported & FORBIDDEN_MODULES
    assert not hits, f"{path.name} imports {hits} directly -- the Supervisor must only ever see execos.specialists.schemas.SpecialistFinding"


def test_only_the_two_adapter_modules_import_the_specialist_projects():
    specialist_dir = SRC_ROOT / "specialists"
    allowed_files_per_module = {"revops": "revenue_ops.py", "investigator": "data_investigation.py"}

    for path in SRC_ROOT.rglob("*.py"):
        if path.parent == specialist_dir and path.name in allowed_files_per_module.values():
            continue  # the adapters are allowed and expected to import their specialist
        imported = _imported_top_level_modules(path)
        hits = imported & FORBIDDEN_MODULES
        assert not hits, f"{path.relative_to(SRC_ROOT)} imports {hits} -- only the specialist adapters may do this"
