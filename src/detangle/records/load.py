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
    "depends_on",
    "flags",
    "conflict",
    "review",
)
OPTIONAL_FIELDS = ("notes",)

STATUSES = ("candidate", "approved", "published", "deprecated")
PLACEMENTS = ("glossary", "UCE", "SBSP", "MCL")
DOCUMENTS = ("U", "S", "M")
FLAGS = ("orphan", "conflict", "A", "P")

# used_in of exactly one document places the term in that document (C9).
PLACEMENT_OF = {"U": "UCE", "S": "SBSP", "M": "MCL"}


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
