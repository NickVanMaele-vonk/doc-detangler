"""Blocks a human moved by hand — ADR-004 Decision 8 (Nick, 2026-08-07).

Findings fixed by typing into the markdown split in two, and only one kind
survives a re-run. **Wording fixes survive**: ``restructure`` moves blocks
verbatim, so a corrected sentence is carried into the next version unchanged.
**Position fixes do not**: the plan governs placement, so a definition moved
by hand is moved back on the next run. The failure was silent — no error, no
finding, nothing in the report — which is the worst way for it to fail. You
would meet the same problem again three versions later.

The rule Nick ruled is that **wording goes in the markdown and position goes
in the plan**, and this module is what makes breaking it visible. It does not
make the plan win a fight with the document: those two hold different facts.
The document is authoritative about every word — token parity enforces that
independently, and a plan is structurally incapable of changing one. The plan
is authoritative about order, and only while a run executes. Moving a
paragraph by hand is editing the *order* through the file that owns the
*wording*, so the change never reaches the surface that carries it.

**A hand-move is a proposal, not a loss.** The run reports the disagreement
and emits the plan line that would ratify it; a human merges that line, or
does not. This is the shape the project already uses for a body edit that
implies a new ``depends_on`` edge — detection is automatic, disposition is
Nick's — and for the same reason: placement is a claim, and a run that
silently adopted an unreviewed hand-move would let two people move the same
block in opposite directions with no resolution.

So the finding is a **warning, never an error**. It must not block the run.
All the evidence is already in hand, which is why this is cheap: the plan
knows each block's intended section, and structured input carries a
``<!-- sec:… -->`` marker per section, so the block's current section is read
rather than inferred.

**It only fires on already-structured input.** Run 1 reorders nearly every
block by design, so "source order disagrees with the plan" is true almost
everywhere and means nothing. A document with no ``sec:`` markers has no
prior placement to contradict, and this module stays silent on it. The check
exists for the re-run, where the input is the previous run's output and the
plan's order and the document's order should already agree.

One limit, stated because the tool must not pretend otherwise: a hand-move
and an ordinary reorder look identical here. This reports *what* disagrees
and what the plan line would be; it never claims to know why.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..findings import Finding, warn
from ..records.spans import block_hash, normalise, split_blocks
from .plan import Plan

#: See ``records.checks.CHECKS`` for why every module declares its slugs.
#: The slug is deliberately *not* ``…-drift``: every member of
#: ``registers.NOT_WAIVABLE`` is an ``<artifact>-drift`` / ``-missing`` pair
#: for a hand-edited derived file, and this is the opposite kind of thing — a
#: disagreement awaiting a human, so waiving it is legitimate. Leaving the
#: plan to stand is a real disposition.
CHECKS = frozenset({"plan-position-conflict"})

#: The marker ``execute.render`` stamps before every headed section. The head
#: section carries no heading and so no marker, which is why blocks before the
#: first match are attributed to the plan's ``kind: head`` section.
SEC = re.compile(r"<!--\s*sec:([A-Za-z0-9][A-Za-z0-9-]*)\s*-->")

PREVIEW = 60
WS = re.compile(r"\s+")


@dataclass(frozen=True)
class Drift:
    """One block sitting somewhere the plan does not put it."""

    block: str
    planned: str
    current: str
    index: int
    preview: str

    @property
    def line(self) -> str:
        """The plan line that would ratify the move, ready to paste."""
        return (
            f"  - {{block: {self.block}, section: {self.current}}}"
            f"  # was {self.planned}"
        )


def is_structured(source: str) -> bool:
    """Has this document been through a run? Only then is order comparable."""
    return SEC.search(source) is not None


def current_sections(plan: Plan, source: str) -> tuple[dict[str, set[str]], dict]:
    """Block hash → the section ids it currently sits under, plus previews.

    A hash maps to a *set* because a document may carry the same block more
    than once — the four identical bare-rule blocks are the live example. A
    block is only drifted when **no** occurrence sits where the plan says, so
    a repeated block cannot raise a finding on the strength of one copy.
    """
    head = next((s.id for s in plan.sections if s.kind == "head"), None)
    where: dict[str, set[str]] = {}
    previews: dict[str, str] = {}
    section = head
    for raw in split_blocks(source):
        marker = SEC.search(raw)
        if marker:
            # The marker and its `## Heading` are one block: scaffolding the
            # renderer wrote, not a source block that can be assigned.
            section = marker.group(1)
            continue
        if section is None:
            continue  # before any section, and the plan declares no head
        digest = block_hash(normalise(raw))
        where.setdefault(digest, set()).add(section)
        previews.setdefault(digest, WS.sub(" ", raw).strip()[:PREVIEW])
    return where, previews


def measure(plan: Plan, source: str) -> list[Drift]:
    """Every assigned block whose current section contradicts the plan."""
    if not is_structured(source):
        return []
    where, previews = current_sections(plan, source)
    out: list[Drift] = []
    for i, entry in enumerate(plan.assignments):
        planned = str(entry.get("section", ""))
        for digest in plan.blocks_of(entry):
            now = where.get(digest)
            if not now or planned in now:
                continue
            out.append(
                Drift(
                    block=digest,
                    planned=planned,
                    current=sorted(now)[0],
                    index=i,
                    preview=previews.get(digest, ""),
                )
            )
    return out


def check(drifts: list[Drift], rel: str) -> list[Finding]:
    """One warning per drifted block, each carrying its own plan line."""
    return [
        warn(
            "plan-position-conflict",
            f"{rel}:assignments[{d.index}]",
            f"this block sits under section {d.current} in the document but "
            f"the plan assigns it to {d.planned}, so the run puts it back "
            f"and the move is lost — wording goes in the markdown, position "
            f"goes in the plan (ADR-004 Decision 8). Block {d.block[:19]}…: "
            f"{d.preview!r}. To ratify the move, replace this assignment "
            f"with:  {d.line.strip()}",
        )
        for d in drifts
    ]


def cluster_body(drifts: list[Drift]) -> str:
    """The 8f report's cluster text — the whole proposed patch in one place.

    The findings carry a line each, which is what a reader fixing one block
    wants; a reviewer looking at the run wants them together.
    """
    return (
        f"**{len(drifts)}** block(s) sit somewhere the plan does not put "
        "them. On already-structured input that means someone moved text by "
        "hand, and this run has moved it back: position is the plan's, not "
        "the document's (ADR-004 Decision 8). Nothing is lost from the "
        "document — only the placement. Ratify the moves by replacing these "
        "assignments in the plan, or leave them and the plan stands:\n\n"
        "```yaml\n" + "\n".join(d.line for d in drifts) + "\n```\n"
    )


__all__ = [
    "CHECKS",
    "Drift",
    "check",
    "cluster_body",
    "current_sections",
    "is_structured",
    "measure",
]
