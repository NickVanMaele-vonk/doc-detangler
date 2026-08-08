"""Reading ``registers/`` — canonical data that is not a corpus term.

A register's provenance is a PR thread and a standards clause, not a source
span, which is why it lives outside ``concepts/`` (Nick, 2026-07-30). Registers
are canonical *inputs* to generation and are never generated.

``cycles.yaml`` and ``waivers.yaml`` are read here. ``reference-terms.md`` is
prose consumed by the view generator.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .findings import Finding, error, warn

CYCLES_FILE = "cycles.yaml"
WAIVERS_FILE = "waivers.yaml"

#: Split by loader, not by module: ``load_cycles`` runs in ``graph`` and
#: ``generate``, ``load_waivers`` only in ``validate``. A command that claimed
#: the whole module would claim checks it never ran, which is the mistake
#: ``stale_findings`` exists to stop. See ``records.checks.CHECKS``.
CYCLE_CHECKS = frozenset(
    {"register-parse", "cycle-duplicate-entry", "cycle-entry-point"}
)
WAIVER_CHECKS = frozenset(
    {
        "register-parse",
        "waiver-duplicate-entry",
        "waiver-not-waivable",
        "waiver-stale",
    }
)
CHECKS = CYCLE_CHECKS | WAIVER_CHECKS

#: Fields every waiver entry must carry. ``match`` is the sole optional one.
#: ``owner``, ``ticket`` and ``review_by`` are required by definition-of-done.md
#: §3, which asks for "each known, ticketed orphan or conflict with an owner and
#: a disposition deadline".
WAIVER_FIELDS = (
    "id",
    "check",
    "where",
    "disposition",
    "owner",
    "ticket",
    "review_by",
    "rationale",
    "authority",
)


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


#: Checks no entry can reach. ``register-parse``, the claim-split register's
#: ``split-parse``/``split-schema``, and the ``waiver-*`` hygiene checks,
#: because a malformed register must not excuse itself — and the drift
#: checks, because a waiver defers a problem somebody has to solve later, and a
#: derived file disagreeing with its source is not one: regenerating it is a
#: single command. C6 and ADR-001 Decision 5 make "never hand-edit a generated
#: artifact" enforceable only while that finding cannot be excused away.
NOT_WAIVABLE = frozenset(
    {
        "register-parse",
        "split-parse",
        "split-schema",
        "graph-drift",
        "graph-missing",
        "glossary-drift",
        "glossary-missing",
        "restructure-drift",
        "restructure-missing",
        "report-drift",
        "report-missing",
    }
)


def is_waivable(check: str) -> bool:
    """A malformed register, or a hand-edited derived file, cannot excuse itself.

    Everything else is waivable: a waiver is a deferral, and most findings name
    work that legitimately waits on someone.
    """
    return check not in NOT_WAIVABLE and not check.startswith("waiver-")


@dataclass(frozen=True)
class WaiverEntry:
    """One finding with a human disposition but no fix yet (plan step 3.9).

    A waiver is a deferral, not an approval (definition-of-done.md §3): the
    set is not fully done while waivers are open, which is why a waived
    finding is still reported.
    """

    id: str
    check: str
    where: str
    match: str | None
    disposition: str
    owner: str
    ticket: str
    review_by: str
    rationale: str
    authority: str

    @property
    def key(self) -> tuple[str, str, str | None]:
        """Two entries covering this triple would be indistinguishable."""
        return (self.check, self.where, self.match)

    def covers(self, finding: Finding) -> bool:
        """``check`` and ``where`` are a finding's stable half.

        ``message`` is the volatile half — it embeds tokens and shas — so
        ``match`` narrows by substring rather than the register having to
        reproduce a whole sentence that the validator may reword.
        """
        if finding.check != self.check or finding.where != self.where:
            return False
        return self.match is None or self.match in finding.message

    @property
    def label(self) -> str:
        return (
            f"waived: {self.disposition} ({self.owner}, {self.ticket}, "
            f"review by {self.review_by})"
        )

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "disposition": self.disposition,
            "owner": self.owner,
            "ticket": self.ticket,
            "review_by": self.review_by,
        }


@dataclass
class WaiverRegister:
    rel: str
    entries: list[WaiverEntry] = field(default_factory=list)

    def partition(
        self, findings: list[Finding]
    ) -> tuple[list[Finding], list[tuple[Finding, WaiverEntry]]]:
        """Split findings into the ones that block and the ones that do not."""
        live: list[Finding] = []
        waived: list[tuple[Finding, WaiverEntry]] = []
        for finding in findings:
            entry = self._covering(finding)
            if entry is None:
                live.append(finding)
            else:
                waived.append((finding, entry))
        return live, waived

    def _covering(self, finding: Finding) -> WaiverEntry | None:
        if not is_waivable(finding.check):
            return None
        return next((e for e in self.entries if e.covers(finding)), None)

    def stale_findings(
        self,
        waived: list[tuple[Finding, WaiverEntry]],
        ran: frozenset[str],
    ) -> list[Finding]:
        """Entries and live findings are 1:1, as for the cycle register.

        So a fix and the removal of its waiver land in the same PR — the same
        discipline that regenerating ``concept-graph.yaml`` already imposes.
        Only meaningful on a full run: a record the run never checked cannot
        prove its waiver dead.

        ``ran`` is the set of check slugs the calling command actually ran, and
        an entry for any other check is left alone. Without it a command reads
        "I did not look" as "it is not there": ``validate`` never runs the
        overview check, so a waiver for ``overview-gap`` would be reported
        stale on every run, telling a human to delete a waiver they still need
        — and ``waiver-stale`` is itself a finding, so that false alarm would
        block a required gate. The same hole existed for ``--no-tables``,
        which skips its own table checks.
        """
        hit = {entry.id for _, entry in waived}
        return [
            warn(
                "waiver-stale",
                f"{self.rel}:{entry.id}",
                f"waiver {entry.id!r} matched no finding; if {entry.check!r} on "
                f"{entry.where} is fixed, remove the entry",
            )
            for entry in self.entries
            if entry.id not in hit and entry.check in ran
        ]


def load_waivers(
    registers_dir: Path, root: Path
) -> tuple[WaiverRegister, list[Finding]]:
    """Load ``registers/waivers.yaml``.

    A missing file is not an error — a record set with nothing deferred needs
    no register. A malformed one is, and a malformed *entry* is skipped rather
    than kept: a half-read waiver must never suppress anything.
    """
    path = registers_dir / WAIVERS_FILE
    rel = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
    register = WaiverRegister(rel=rel)
    if not path.is_file():
        return register, []

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return register, [error("register-parse", rel, str(exc).replace("\n", " "))]
    if data is None:
        return register, []
    if not isinstance(data, dict) or not isinstance(data.get("waivers"), list):
        return register, [error("register-parse", rel, "expected a 'waivers' list")]

    findings: list[Finding] = []
    for i, raw in enumerate(data["waivers"]):
        where = f"{rel}:waivers[{i}]"
        if not isinstance(raw, dict):
            findings.append(error("register-parse", where, "entry is not a mapping"))
            continue
        missing = [f for f in WAIVER_FIELDS if not str(raw.get(f) or "").strip()]
        if missing:
            findings.append(
                error(
                    "register-parse",
                    where,
                    f"entry has no {', '.join(repr(m) for m in missing)}",
                )
            )
            continue
        entry = WaiverEntry(
            id=str(raw["id"]),
            check=str(raw["check"]),
            where=str(raw["where"]),
            match=None if raw.get("match") is None else str(raw["match"]),
            disposition=str(raw["disposition"]),
            owner=str(raw["owner"]),
            ticket=str(raw["ticket"]),
            review_by=str(raw["review_by"]),
            rationale=str(raw["rationale"]),
            authority=str(raw["authority"]),
        )
        if not is_waivable(entry.check):
            findings.append(
                error(
                    "waiver-not-waivable",
                    where,
                    f"{entry.check!r} cannot be waived: a malformed register "
                    "must not be able to excuse itself",
                )
            )
            continue
        register.entries.append(entry)

    findings.extend(_check_duplicates(register))
    return register, findings


def _check_duplicates(register: WaiverRegister) -> list[Finding]:
    findings: list[Finding] = []
    by_key: dict[tuple[str, str, str | None], str] = {}
    by_id: set[str] = set()
    for entry in register.entries:
        if entry.key in by_key:
            findings.append(
                error(
                    "waiver-duplicate-entry",
                    register.rel,
                    f"{entry.id!r} and {by_key[entry.key]!r} waive the same "
                    f"{entry.check!r} finding on {entry.where}; entries and "
                    "live findings are 1:1",
                )
            )
        else:
            by_key[entry.key] = entry.id
        if entry.id in by_id:
            findings.append(
                error(
                    "waiver-duplicate-entry",
                    register.rel,
                    f"id {entry.id!r} is used twice; ids are how a waiver is "
                    "cited in a PR thread and how staleness is tracked",
                )
            )
        by_id.add(entry.id)
    return findings


__all__ = [
    "CYCLES_FILE",
    "WAIVERS_FILE",
    "CycleEntry",
    "CycleRegister",
    "WaiverEntry",
    "WaiverRegister",
    "is_waivable",
    "load_cycles",
    "load_waivers",
]
