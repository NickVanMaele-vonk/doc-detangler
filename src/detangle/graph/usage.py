"""Extracting usage edges from document bodies (C11, step 3.7).

A usage edge says: this stamped section of this component document uses this
term in its prose. The edges are derived data (D10) — regenerated on every
run from the bodies registered in ``detangle.toml [bodies]``, never
hand-maintained — and the glossary never lists them: usage lives in the
graph only (C11).

What counts as a use (Nick, 2026-08-08): **body prose only.** Text inside a
``<!-- concept:<id>:start/end -->`` block is a definition, not a use — a
definition using another term is canonically that record's ``depends_on``
edge, and the graph must not duplicate canonical edge data (C11). The bold
intro line immediately above a concept's own block is definition-site
apparatus, not a use of the term on itself; other terms appearing there
still count. Text above the first stamped ``<!-- sec:… -->`` marker (the
title block) has no section to address an edge to and is skipped.

Matching is case-insensitive on each record's ``term`` and ``aliases``,
whole words only, longest surface wins, tolerating a trailing plural
(``s``/``es``) and prose line-wraps inside a multi-word surface.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..findings import Finding, warn
from ..records import Record

#: See ``records.checks.CHECKS``.
CHECKS = frozenset(
    {
        "usage-ambiguous-surface",
        "usage-unknown-concept",
        "usage-unclosed-block",
    }
)

COMMENT = re.compile(r"<!--(.*?)-->", re.DOTALL)
SEC = re.compile(r"^\s*sec:([A-Za-z0-9][\w-]*)\s*$")
CONCEPT = re.compile(r"^\s*concept:([a-z0-9][a-z0-9-]*):(start|end)\s*$")

#: Word characters and hyphen bound a surface: ``pre-alert`` is not a use of
#: ``alert``, and ``alerting`` is not either; ``alerts`` and ``alert's`` are.
_BOUNDARY_L = r"(?<![\w-])"
_BOUNDARY_R = r"(?![\w-])"


@dataclass(frozen=True, order=True)
class UsageEdge:
    """``section`` of component ``doc`` uses the concept ``term`` (a record id)."""

    doc: str
    section: str
    term: str


@dataclass(frozen=True)
class SurfaceIndex:
    """Every matchable surface form, compiled once per record set."""

    pattern: re.Pattern | None
    by_surface: dict[str, str]

    def resolve(self, matched: str) -> str | None:
        """Record id for a raw match, un-pluralising if the exact form is new."""
        surface = " ".join(matched.lower().split())
        for candidate in (surface, surface[:-1], surface[:-2]):
            rid = self.by_surface.get(candidate)
            if rid is not None:
                return rid
        return None


def build_index(records: list[Record]) -> tuple[SurfaceIndex, list[Finding]]:
    """Map every term and alias to its record; collisions match nothing.

    The record set has no colliding surfaces today; if one appears, matching
    it would attribute prose to an arbitrary record, so the surface is warned
    about and left out until a human splits the alias.
    """
    findings: list[Finding] = []
    by_surface: dict[str, str] = {}
    ambiguous: set[str] = set()
    for rec in records:
        forms = [rec.data.get("term") or rec.id, *rec.get_list("aliases")]
        for form in forms:
            if not isinstance(form, str) or not form.strip():
                continue
            surface = " ".join(form.lower().split())
            owner = by_surface.get(surface)
            if owner is not None and owner != rec.id:
                ambiguous.add(surface)
                findings.append(
                    warn(
                        "usage-ambiguous-surface",
                        rec.where("aliases"),
                        f"surface {form!r} also names {owner!r}; matches of it "
                        "are attributed to neither until the alias is split",
                    )
                )
                continue
            by_surface[surface] = rec.id
    for surface in ambiguous:
        by_surface.pop(surface, None)

    if not by_surface:
        return SurfaceIndex(pattern=None, by_surface={}), findings
    alternatives = sorted(by_surface, key=lambda s: (-len(s), s))
    body = "|".join(
        re.escape(s).replace(r"\ ", r"\s+") + r"(?:e?s)?" for s in alternatives
    )
    pattern = re.compile(
        _BOUNDARY_L + "(?:" + body + ")" + _BOUNDARY_R, re.IGNORECASE
    )
    return SurfaceIndex(pattern=pattern, by_surface=by_surface), findings


def extract(
    text: str, doc: str, index: SurfaceIndex, known: set[str], rel: str
) -> tuple[list[UsageEdge], list[Finding]]:
    """One body → its usage edges, deduplicated to one per (section, term)."""
    findings: list[Finding] = []
    edges: set[UsageEdge] = set()
    section: str | None = None
    block: str | None = None

    def scan(prose: str, next_block: str | None) -> None:
        """Match one prose run; its last paragraph may be an intro line."""
        if block is not None or section is None or index.pattern is None:
            return
        paragraphs = [p for p in re.split(r"\n\s*\n", prose) if p.strip()]
        for i, paragraph in enumerate(paragraphs):
            intro_for = next_block if i == len(paragraphs) - 1 else None
            flat = " ".join(paragraph.split())
            for match in index.pattern.finditer(flat):
                rid = index.resolve(match.group(0))
                if rid is None or rid == intro_for:
                    continue
                edges.add(UsageEdge(doc=doc, section=section, term=rid))

    pos = 0
    for comment in COMMENT.finditer(text):
        body = comment.group(1)
        concept = CONCEPT.match(body)
        sec = SEC.match(body)
        starting = concept.group(1) if concept and concept.group(2) == "start" else None
        scan(text[pos : comment.start()], starting)
        pos = comment.end()
        if concept:
            rid, kind = concept.group(1), concept.group(2)
            if kind == "start":
                if rid not in known:
                    findings.append(
                        warn(
                            "usage-unknown-concept",
                            rel,
                            f"definition block for {rid!r} has no concept "
                            "record; its text is still excluded from usage",
                        )
                    )
                block = rid
            elif block == rid:
                block = None
        elif sec:
            section = sec.group(1)
    scan(text[pos:], None)

    if block is not None:
        findings.append(
            warn(
                "usage-unclosed-block",
                rel,
                f"concept block {block!r} is never closed; everything after "
                "its start marker was excluded from usage extraction",
            )
        )
    return sorted(edges), findings


__all__ = ["CHECKS", "SurfaceIndex", "UsageEdge", "build_index", "extract"]
