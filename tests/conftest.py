"""A miniature repository, so tests exercise the real code paths.

`validate` reads git blobs and shells out to pandoc, and stubbing either would
test the stub. The fixture builds a throwaway repo with a committed source
document instead, which is cheap: hashing is per block, and the fixture corpus
has three.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest
import yaml

from detangle.records.spans import block_hash, normalise, split_blocks

SAMPLE = """\
# Mini corpus

Front matter paragraph naming MTSAM and a threshold of 30 minutes.

## 1.1 The Only Section

A widget is a device that emits SB-01 alerts when the score is >= 0.85.

A gadget is used here but never defined anywhere in this corpus.
"""

CONFIG = """\
[paths]
concepts = "concepts"
registers = "registers"
samples = "samples"
graph = "concept-graph.yaml"

[documents]
U = "samples/mini.md"
S = "samples/other.md"
M = "samples/third.md"
components = ["U", "S", "M"]

[params]
max-terms-changed-per-PR = 25

[validate]
min-verbatim-run-chars = 10
table-globs = ["*.md"]
"""

BASE_RECORD = {
    "id": "widget",
    "term": "widget",
    "aliases": [],
    "status": "candidate",
    "superseded_by": None,
    "placement": "UCE",
    "used_in": ["U"],
    "definition": "A widget is a device that emits SB-01 alerts",
    "source": [],
    "depends_on": [],
    "flags": [],
    "conflict": None,
    "review": "test",
}


@dataclass
class MiniRepo:
    root: Path

    def blob(self, rel: str) -> str:
        return subprocess.run(
            ["git", "-C", str(self.root), "rev-parse", f"HEAD:{rel}"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()

    def para_hash(self, needle: str, doc: str = "samples/mini.md") -> str:
        """Hash of the block containing ``needle`` — how records are anchored."""
        text = (self.root / doc).read_text(encoding="utf-8")
        for block in split_blocks(text):
            if needle in block:
                return block_hash(normalise(block))
        raise AssertionError(f"no block contains {needle!r}")

    def span(self, needle: str, doc: str = "samples/mini.md") -> dict:
        return {
            "doc": doc,
            "section": "1.1 The Only Section",
            "para_hash": self.para_hash(needle, doc),
            "verified_against": {"git_blob": self.blob(doc), "stated_version": None},
        }

    def write_record(self, **overrides) -> Path:
        data = dict(BASE_RECORD)
        data.update(overrides)
        if not data["source"]:
            data["source"] = [self.span("A widget is a device")]
        path = self.root / "concepts" / f"{data['id']}.yaml"
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
        return path

    def write_cycles(self, *entries: dict) -> Path:
        """``registers/cycles.yaml`` — the canonical home of cycle rulings."""
        path = self.root / "registers" / "cycles.yaml"
        path.write_text(
            yaml.safe_dump({"cycles": list(entries)}, sort_keys=False),
            encoding="utf-8",
        )
        return path


@pytest.fixture
def mini_repo(tmp_path: Path) -> MiniRepo:
    root = tmp_path / "repo"
    (root / "concepts").mkdir(parents=True)
    (root / "registers").mkdir()
    (root / "samples").mkdir()
    (root / "samples" / "mini.md").write_text(SAMPLE, encoding="utf-8")
    (root / "detangle.toml").write_text(CONFIG, encoding="utf-8")

    def git(*args: str) -> None:
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)

    git("init", "-q")
    git("config", "user.email", "test@example.com")
    git("config", "user.name", "test")
    git("add", "-A")
    git("commit", "-qm", "fixture")
    return MiniRepo(root=root)
