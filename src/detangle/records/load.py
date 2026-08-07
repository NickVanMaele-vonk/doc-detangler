"""Loading concept records.

``concepts/`` holds only corpus-derived business terms — every file is a
record, no exclusions (Nick, 2026-07-30), which is what lets the loader treat
``concepts/*.yaml`` as a flat glob and lets the validator enforce the schema
flatly instead of carrying a carve-out. Registers live in ``registers/``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from ..findings import Finding, error

# concepts/README.md §Record schema, in schema order.
#: See ``records.checks.CHECKS``.
CHECKS = frozenset({"yaml-parse"})

REQUIRED_FIELDS = (
    "id",
    "term",
    "aliases",
    "status",
    "superseded_by",
    "placement",
    "used_in",
    "definition",
    "source",
    "assurance",
    "depends_on",
    "flags",
    "conflict",
    "review",
)
OPTIONAL_FIELDS = ("notes",)

STATUSES = ("candidate", "approved", "published", "deprecated")

# ADR-004 Decisions 1, 2 and 2b (Nick, 2026-08-07): lineage and assurance are
# separate axes, and they attach at different levels.
#
# LINEAGE is per span, because where wording came from varies span by span.
# `origin` says which: `corpus` is wording that was in the document when the
# tool first consumed it; `authored` is wording that entered in a later
# version. It deliberately does not say *who* wrote the later text — that is
# the assurance block's job, one level up, and splitting the two is the whole
# point of the decision. The git blob already pins *which* version, so no
# hand-typed version string is introduced (the 2026-07-31 ruling).
#
# What this replaces: the absence of a `para_hash` used to encode both "not in
# the original" and "not trustworthy". Decision 1 denies the second, so an
# authored span may now carry a real hash into the version it entered at, and
# re-anchoring is routine rather than forbidden.
SPAN_ORIGINS = ("corpus", "authored")

# ASSURANCE is per record, because approval is one human act covering the
# definition as a whole, not a thing repeated per citation. `author` is who
# produced the wording ("assistant" for text the tool assembled from corpus
# spans under C2, a person's name for text a human typed); `approved_by` is
# the named human who verified it, `null` until someone has; `pr` is where
# that happened. Whether a definition is human-approved is *computed* from
# `approved_by`, never stored — the same rule that keeps `placement` computed.
ASSURANCE_FIELDS = ("author", "approved_by", "pr")

# Statuses that assert a human has signed the definition off, so they may not
# be reached with `approved_by: null`. Under Decision 1 assurance carries all
# the definitional strength, which only holds if approval is a real act.
APPROVED_STATUSES = ("approved", "published")

# Document codes, placement names and flag values are NOT declared here: they
# come from `detangle.toml` via `Config.registry()` (two input sets, Nick
# 2026-08-05) — adding a reference document is a config edit, never a code
# change. The checks receive a `DocumentRegistry` for exactly this reason.


@dataclass
class Record:
    path: Path
    rel: str
    data: dict
    text: str

    @property
    def id(self) -> str:
        return self.data.get("id") or self.path.stem

    @property
    def defined(self) -> bool:
        return self.data.get("definition") is not None

    def get_list(self, key: str) -> list:
        value = self.data.get(key)
        return value if isinstance(value, list) else []

    def where(self, field: str | None = None) -> str:
        return f"{self.rel}:{field}" if field else self.rel


def load_records(concepts_dir: Path, root: Path) -> tuple[list[Record], list[Finding]]:
    """Every ``concepts/*.yaml``. A file that will not parse becomes a finding.

    A parse failure is reported and the file dropped rather than raised, so one
    broken record does not hide the state of the other 357.
    """
    records: list[Record] = []
    findings: list[Finding] = []
    for path in sorted(concepts_dir.glob("*.yaml")):
        rel = str(path.relative_to(root))
        text = path.read_text(encoding="utf-8")
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as exc:
            findings.append(error("yaml-parse", rel, str(exc).replace("\n", " ")))
            continue
        if not isinstance(data, dict):
            findings.append(
                error("yaml-parse", rel, "top level is not a mapping")
            )
            continue
        records.append(Record(path=path, rel=rel, data=data, text=text))
    return records, findings
