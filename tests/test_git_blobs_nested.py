"""GitBlobs when the detangle root is a subfolder of the git worktree.

The mini_repo fixture colocates the git root and the detangle root, so it can
never catch a path form that silently resolves from the tree root instead of
the project root. `git rev-parse HEAD:<path>` is exactly that form: it ignores
`-C` for the path part unless the path is written `./<path>`. This suite pins
the `HEAD:./<path>` behaviour against the layout the MTSAM-docs move creates
(git root = monorepo, detangle root = monorepo/detangler).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from detangle.records.checks import GitBlobs

DOC = "samples/mini.md"


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True
    ).stdout.strip()


@pytest.fixture
def nested_root(tmp_path: Path) -> Path:
    """A git repo at tmp_path/monorepo with the project one level down."""
    monorepo = tmp_path / "monorepo"
    project = monorepo / "detangler"
    (project / "samples").mkdir(parents=True)
    (project / "samples" / "mini.md").write_text("# Mini\n\nA widget.\n", "utf-8")
    (monorepo / "README.md").write_text("# Monorepo\n", "utf-8")
    def git(*args: str) -> None:
        subprocess.run(
            ["git", "-C", str(monorepo), *args], check=True, capture_output=True
        )

    git("init", "-q")
    git("config", "user.email", "test@example.com")
    git("config", "user.name", "test")
    git("add", "-A")
    git("commit", "-qm", "fixture")
    return project


def test_head_resolves_from_project_root(nested_root: Path):
    blob = GitBlobs(nested_root).head(DOC)
    assert blob == _git(nested_root.parent, "rev-parse", f"HEAD:detangler/{DOC}")


def test_committed_true_for_clean_tracked_file(nested_root: Path):
    assert GitBlobs(nested_root).committed(DOC) is True


def test_committed_false_after_edit(nested_root: Path):
    (nested_root / DOC).write_text("# Mini\n\nA gadget.\n", "utf-8")
    blobs = GitBlobs(nested_root)
    assert blobs.worktree_differs(DOC) is True
    assert blobs.committed(DOC) is False


def test_committed_false_for_untracked_file(nested_root: Path):
    (nested_root / "samples" / "new.md").write_text("fresh\n", "utf-8")
    assert GitBlobs(nested_root).committed("samples/new.md") is False
