"""Reading ``registers/`` — canonical data that is not a corpus term.

A register's provenance is a PR thread and a standards clause, not a source
span, which is why it lives outside ``concepts/`` (Nick, 2026-07-30). Registers
are canonical *inputs* to generation and are never generated.

Only ``cycles.yaml`` is read here. ``reference-terms.md`` is prose consumed by
the view generator, and ``waivers.yaml`` arrives in Phase 10.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .findings import Finding, error

CYCLES_FILE = "cycles.yaml"


@dataclass(frozen=True)
class CycleEntry:
    """One human disposition for one live cycle (definition-of-done.md §1)."""

    id: str
    members: tuple[str, ...]
    disposition: str
    entry_point: str | None
    iso_704: str | None
    rationale: str | None
    authority: str | None

    @property
    def key(self) -> frozenset[str]:
        """Cycles are matched to entries by member set, not by order.

        ``simple_cycles`` picks its own starting node, so the register must not
        have to guess where the tool will begin walking.
        """
        return frozenset(self.members)


@dataclass
class CycleRegister:
    rel: str
    entries: list[CycleEntry] = field(default_factory=list)

    def by_members(self) -> dict[frozenset[str], CycleEntry]:
        return {e.key: e for e in self.entries}


def load_cycles(registers_dir: Path, root: Path) -> tuple[CycleRegister, list[Finding]]:
    """Load ``registers/cycles.yaml``.

    A missing file is not an error: a record set with no accepted cycle needs
    no register. An unreadable or malformed one is, because silently treating
    it as empty would turn every dispositioned cycle into a blocking finding.
    """
    path = registers_dir / CYCLES_FILE
    rel = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
    register = CycleRegister(rel=rel)
    if not path.is_file():
        return register, []

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return register, [error("register-parse", rel, str(exc).replace("\n", " "))]
    if data is None:
        return register, []
    if not isinstance(data, dict) or not isinstance(data.get("cycles"), list):
        return register, [error("register-parse", rel, "expected a 'cycles' list")]

    findings: list[Finding] = []
    for i, raw in enumerate(data["cycles"]):
        where = f"{rel}:cycles[{i}]"
        if not isinstance(raw, dict):
            findings.append(error("register-parse", where, "entry is not a mapping"))
            continue
        members = raw.get("members")
        if not isinstance(members, list) or len(members) < 1:
            findings.append(error("register-parse", where, "'members' must be a list"))
            continue
        if len(set(members)) != len(members):
            findings.append(error("register-parse", where, "'members' repeats an id"))
            continue
        entry = CycleEntry(
            id=str(raw.get("id") or f"cycle-{i}"),
            members=tuple(str(m) for m in members),
            disposition=str(raw.get("disposition") or ""),
            entry_point=raw.get("entry_point"),
            iso_704=raw.get("iso_704"),
            rationale=raw.get("rationale"),
            authority=raw.get("authority"),
        )
        if not entry.disposition:
            findings.append(
                error("register-parse", where, "entry has no 'disposition'")
            )
        findings.extend(_check_entry(entry, where))
        register.entries.append(entry)

    seen: dict[frozenset[str], str] = {}
    for entry in register.entries:
        if entry.key in seen:
            findings.append(
                error(
                    "cycle-duplicate-entry",
                    rel,
                    f"{entry.id!r} and {seen[entry.key]!r} disposition the same "
                    "member set; entries and live cycles are 1:1",
                )
            )
        else:
            seen[entry.key] = entry.id
    return register, findings


def _check_entry(entry: CycleEntry, where: str) -> list[Finding]:
    """Criterion 1 clause 2: the entry point is designated *in the entry*."""
    if entry.entry_point is None:
        return [
            error(
                "cycle-entry-point",
                where,
                f"cycle {entry.id!r} has no 'entry_point'; criterion 1 requires "
                "one member be designated and defined first",
            )
        ]
    if entry.entry_point not in entry.members:
        return [
            error(
                "cycle-entry-point",
                where,
                f"entry_point {entry.entry_point!r} is not one of the cycle's "
                f"members {list(entry.members)}",
            )
        ]
    return []


__all__ = ["CYCLES_FILE", "CycleEntry", "CycleRegister", "load_cycles"]
