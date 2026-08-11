"""The machine-readable reorder plan (ADR-002 Decision 2).

A plan says, in data, everything the golden's move-map said in prose: which
source block lands in which target section, which page-split fragments
rejoin, what is declared noise, where each definition block goes, and which
sections are generated rather than moved. Blocks are addressed by
``para_hash`` — never line numbers (D10) — so a plan survives any edit that
does not change the block it names, and breaks loudly on one that does.

A plan also carries ``exceptions``: one short line per ruling a human made
about this document — the version skew stands, the change-log rules stay
put, the OCR damage is carried verbatim. Only the title and a pointer to
where the reasoning is written; the wording lives in one place and the tool
never reprints it. The tool needs them because the 8c comment budget counts
comments, and a comment it cannot see is one it would count wrong (Nick,
2026-08-05).

Validation enforces the ADR's losslessness-at-run-time rule: every block of
the source must be covered by exactly one of assignment, rejoin, or noise.
An uncovered block is ``plan-incomplete``; a doubly covered one is
``plan-overlap``. The tool never decides what a block means — it refuses to
run a plan that has not decided.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from ..config import DocumentRegistry
from ..findings import Finding, error, warn
from ..records.load import Record
from ..records.spans import BlockIndex

#: See ``records.checks.CHECKS`` for why every module declares its slugs.
CHECKS = frozenset(
    {
        "plan-parse",
        "plan-schema",
        "plan-doc",
        "plan-blob-stale",
        "plan-block-unknown",
        "plan-incomplete",
        "plan-overlap",
        "plan-section-unknown",
        "plan-record-unknown",
        "plan-repair-unsafe",
    }
)

SECTION_KINDS = ("head", "generated", "content")
NOISE_KINDS = ("furniture", "artifact", "navigation")
#: Presentation transforms an assignment may declare. Each is implemented
#: deterministically by the renderer; declaring one is a stage-A judgment.
RENDER_HINTS = ("history-list", "part-row", "note-italic", "grid-list")
SECTION_ID = re.compile(r"^head$|^[a-z]-[0-9a-f]{8}$")
HASH = re.compile(r"^sha256:[0-9a-f]{64}$")


@dataclass(frozen=True)
class Section:
    id: str
    title: str
    kind: str


@dataclass
class Plan:
    path: Path
    rel: str
    doc: str
    pinned_blob: str | None
    sections: list[Section] = field(default_factory=list)
    assignments: list[dict] = field(default_factory=list)
    noise: list[dict] = field(default_factory=list)
    inline_removals: list[dict] = field(default_factory=list)
    repairs: list[dict] = field(default_factory=list)
    definitions: list[dict] = field(default_factory=list)
    additions: list[dict] = field(default_factory=list)
    exceptions: list[dict] = field(default_factory=list)

    def section_ids(self) -> set[str]:
        return {s.id for s in self.sections}

    def blocks_of(self, entry: dict) -> list[str]:
        """The block hashes an assignment claims — one, or a fragment list.

        A page-split rejoin is an assignment with ``fragments``: one output
        unit from several source blocks, sitting at one position in the
        section's ordered stream — order within a section is a stage-A
        judgment, so it lives in the plan, not in source order.
        """
        if "fragments" in entry:
            return [h for h in entry.get("fragments", []) if isinstance(h, str)]
        block = entry.get("block")
        return [block] if isinstance(block, str) else []

    def covered(self) -> dict[str, list[str]]:
        """Block hash → the roles claiming it (for coverage/overlap checks).

        A noise entry covers every occurrence of its hash, which is what
        makes the four identical bare-rule blocks one entry rather than four.
        """
        roles: dict[str, list[str]] = {}
        for a in self.assignments:
            for h in self.blocks_of(a):
                roles.setdefault(h, []).append("assignment")
        for n in self.noise:
            roles.setdefault(n.get("block", ""), []).append("noise")
        return roles


LIST_FIELDS = (
    "sections",
    "assignments",
    "noise",
    "inline_removals",
    "repairs",
    "definitions",
    "additions",
    "exceptions",
)


def load_plan(path: Path, root: Path) -> tuple[Plan | None, list[Finding]]:
    """Parse and shape-check a plan file. Reference errors are validate's job."""
    rel = str(path.relative_to(root)) if path.is_absolute() else str(path)
    if not path.is_file():
        return None, [error("plan-parse", rel, "no such plan file")]
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return None, [error("plan-parse", rel, str(exc).replace("\n", " "))]
    if not isinstance(data, dict):
        return None, [error("plan-parse", rel, "top level is not a mapping")]

    findings: list[Finding] = []
    if not isinstance(data.get("doc"), str):
        findings.append(error("plan-schema", rel, "missing or non-string 'doc'"))
        return None, findings

    # str(), because YAML reads an all-digit blob as an integer and an
    # integer pin would compare unequal to every real blob string.
    pinned = data.get("pinned_blob")
    plan = Plan(
        path=path,
        rel=rel,
        doc=data["doc"],
        pinned_blob=str(pinned) if pinned is not None else None,
    )
    for key in LIST_FIELDS:
        value = data.get(key, [])
        if not isinstance(value, list):
            findings.append(error("plan-schema", f"{rel}:{key}", "not a list"))
            continue
        if key == "sections":
            for i, s in enumerate(value):
                if not isinstance(s, dict) or not SECTION_ID.match(str(s.get("id"))):
                    findings.append(
                        error("plan-schema", f"{rel}:sections[{i}]", "bad section")
                    )
                    continue
                if s.get("kind") not in SECTION_KINDS:
                    findings.append(
                        error(
                            "plan-schema",
                            f"{rel}:sections[{i}]",
                            f"kind {s.get('kind')!r} not one of {list(SECTION_KINDS)}",
                        )
                    )
                    continue
                plan.sections.append(
                    Section(id=s["id"], title=str(s.get("title", "")), kind=s["kind"])
                )
        else:
            getattr(plan, key).extend(v for v in value if isinstance(v, dict))
            for i, v in enumerate(value):
                if not isinstance(v, dict):
                    findings.append(
                        error("plan-schema", f"{rel}:{key}[{i}]", "not a mapping")
                    )

    for key, entries, req in (
        ("noise", plan.noise, ("block", "kind")),
        ("inline_removals", plan.inline_removals, ("block", "remove")),
        ("repairs", plan.repairs, ("block", "from", "to")),
        ("definitions", plan.definitions, ("record", "section")),
        ("additions", plan.additions, ("section", "form", "text")),
        ("exceptions", plan.exceptions, ("title", "where")),
    ):
        for i, entry in enumerate(entries):
            missing = [k for k in req if k not in entry]
            if missing:
                findings.append(
                    error("plan-schema", f"{rel}:{key}[{i}]", f"missing {missing}")
                )
    for i, a in enumerate(plan.assignments):
        if "section" not in a or not (("block" in a) ^ ("fragments" in a)):
            findings.append(
                error(
                    "plan-schema",
                    f"{rel}:assignments[{i}]",
                    "needs 'section' and exactly one of 'block' / 'fragments'",
                )
            )
        hint = a.get("render")
        if hint is not None and hint not in RENDER_HINTS:
            findings.append(
                error(
                    "plan-schema",
                    f"{rel}:assignments[{i}]",
                    f"render {hint!r} not one of {list(RENDER_HINTS)}",
                )
            )
    for i, n in enumerate(plan.noise):
        if n.get("kind") is not None and n["kind"] not in NOISE_KINDS:
            findings.append(
                error(
                    "plan-schema",
                    f"{rel}:noise[{i}]",
                    f"kind {n['kind']!r} not one of {list(NOISE_KINDS)}",
                )
            )
    return plan, findings


def validate_plan(
    plan: Plan,
    registry: DocumentRegistry,
    index: BlockIndex,
    records: list[Record],
    head_blob: str | None = None,
) -> list[Finding]:
    """Every reference resolves and every source block is decided.

    ``head_blob`` is the source's current ``git rev-parse HEAD:<doc>`` where
    the caller has it; the pin check is a warning, mirroring
    ``git-blob-stale`` — a moved corpus means re-verify, not that the plan
    is wrong.
    """
    out: list[Finding] = []
    rel = plan.rel

    if plan.doc not in registry.components:
        out.append(
            error(
                "plan-doc",
                f"{rel}:doc",
                f"{plan.doc!r} is not a component code "
                f"{list(registry.components)} — only the detangle set is "
                "restructured; reference documents are read-only (ADR-002)",
            )
        )
        return out
    doc_path = registry.paths[plan.doc]

    if plan.pinned_blob and head_blob and plan.pinned_blob != head_blob:
        out.append(
            warn(
                "plan-blob-stale",
                f"{rel}:pinned_blob",
                f"plan pinned {plan.pinned_blob}, HEAD is {head_blob} — the "
                "source moved, so this plan's block hashes address a version "
                "that no longer exists; re-verify the plan against it. If a "
                "docs PR merged while this run was in flight, that is the "
                "cause: a re-run freezes the documents it touches, because a "
                "run moves nearly every block and a plan addresses blocks by "
                "hash (ADR-004 Decision 6)",
            )
        )

    source_hashes = set(index.document(doc_path).by_hash)
    section_ids = plan.section_ids()
    known_records = {r.id for r in records}

    def check_hash(where: str, h) -> None:
        if not isinstance(h, str) or not HASH.match(h):
            out.append(error("plan-block-unknown", where, f"malformed hash {h!r}"))
        elif h not in source_hashes:
            out.append(
                error(
                    "plan-block-unknown",
                    where,
                    f"{h} is not a block of {doc_path}",
                )
            )

    for i, a in enumerate(plan.assignments):
        for h in plan.blocks_of(a):
            check_hash(f"{rel}:assignments[{i}]", h)
        if a.get("section") not in section_ids:
            out.append(
                error(
                    "plan-section-unknown",
                    f"{rel}:assignments[{i}]",
                    f"section {a.get('section')!r} is not declared",
                )
            )
    for i, n in enumerate(plan.noise):
        check_hash(f"{rel}:noise[{i}]", n.get("block"))
    for i, entry in enumerate(plan.inline_removals):
        check_hash(f"{rel}:inline_removals[{i}]", entry.get("block"))
    for i, r in enumerate(plan.repairs):
        check_hash(f"{rel}:repairs[{i}]", r.get("block"))
        frm, to = str(r.get("from", "")), str(r.get("to", ""))
        if re.sub(r"\s+", "", frm) != re.sub(r"\s+", "", to):
            out.append(
                error(
                    "plan-repair-unsafe",
                    f"{rel}:repairs[{i}]",
                    f"{frm!r} → {to!r} is not whitespace-only — a repair may "
                    "rejoin split characters, never change them (the guard "
                    "may make word-preserving edits only)",
                )
            )
    for kind, entries in (
        ("definitions", plan.definitions),
        ("additions", plan.additions),
    ):
        for i, entry in enumerate(entries):
            if entry.get("section") not in section_ids:
                out.append(
                    error(
                        "plan-section-unknown",
                        f"{rel}:{kind}[{i}]",
                        f"section {entry.get('section')!r} is not declared",
                    )
                )
    for i, d in enumerate(plan.definitions):
        if d.get("record") not in known_records:
            out.append(
                error(
                    "plan-record-unknown",
                    f"{rel}:definitions[{i}]",
                    f"record {d.get('record')!r} has no concept record",
                )
            )

    roles = plan.covered()
    for h in sorted(source_hashes - set(roles)):
        text = index.document(doc_path).text_for(h) or ""
        out.append(
            error(
                "plan-incomplete",
                f"{rel}",
                f"source block {h} is covered by no assignment, rejoin or "
                f"noise entry — losslessness is enforced at run time "
                f"(ADR-002): {text[:60]!r}…",
            )
        )
    for h, claimed in sorted(roles.items()):
        if len(claimed) > 1 and h in source_hashes:
            out.append(
                error(
                    "plan-overlap",
                    f"{rel}",
                    f"source block {h} is claimed {len(claimed)} times "
                    f"({', '.join(claimed)}) — a block has exactly one fate",
                )
            )
    return out


__all__ = ["CHECKS", "Plan", "Section", "load_plan", "validate_plan"]
