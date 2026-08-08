"""Coverage stage 1 — ADR-003 Decision 2, ruled by Nick 2026-08-07.

Coverage (plan step 7.2) maps every detangle-set source claim to a location in
the output, or leaves it for a human. G1's bidirectional traceability frame
applies: an unlinked source claim is an omission candidate, an unlinked output
claim is a fabrication candidate. This module is the **deterministic half** —
the claims that moved verbatim, placed with no model involved.

Why the deterministic pass is a correctness property and not an optimisation:
a claim whose wording provably did not change must not be able to fail. Model
scoring is the weakest part of the harness in exactly our regime
(research-memo §1.1: grounded-factuality metrics degrade on heavily reordered
text), and the restructure is reordering by construction. So everything that
can be settled by text identity is settled here, and the model only ever sees
text that genuinely changed.

**Stage 1 must be incapable of being wrong.** Its matches carry confidence 1.0
and no human ever reviews them, so the rule is the strictest one available:
one source claim to one output claim, exact equality of the decomposer's
normalised text. Nothing looser — not case-folding, not substring containment,
not concatenating a run of claims to reach an equal string. Two measurements
back that (`tests/test_verify_coverage.py`): case-folding gains nothing at all
on the golden, so strictness is free and a criterion-5 casing defect stays
visible; and run-concatenation would place 9 further claims out of 66, which
is not worth a rule that asserts coverage a human never sees. A claim left in
the residue costs one model call. A claim placed wrongly costs the guarantee
the harness exists to produce.

What lands in the residue is therefore precisely what criterion 4 wants
reported anyway — page-split rejoins, dedup survivors, relocated definitions,
and table-to-prose conversions where one cell became several sentences. Stage
2 scores it (ADR-003 Decision 2's second half, build step 3).

**This module raises no findings, deliberately.** A residue claim is not an
omission — it is a claim stage 1 declined to rule on. `omission` is decidable
only once the residue has been scored, so the check is declared by the module
that scores it, and there is no `CHECKS` constant here.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .claims import Claim, Decomposition

#: Every stage-1 match is text identity, so its score is not an estimate.
VERBATIM = 1.0


@dataclass(frozen=True)
class Match:
    """One source claim placed at one output claim, by text identity."""

    source: str
    location: str
    confidence: float = VERBATIM
    method: str = "verbatim"


@dataclass
class Coverage:
    doc: str
    #: Placed deterministically, in source document order.
    matched: list[Match] = field(default_factory=list)
    #: Source claims stage 1 declined to place — the work-list for scoring.
    residue: list[Claim] = field(default_factory=list)
    #: Output claims no source claim explains — fabrication candidates, in
    #: output document order. Stage 1 only narrows this set; Decision 3 rules
    #: on it, and marked bridging text is exempt there, not here.
    unplaced: list[Claim] = field(default_factory=list)

    @property
    def source_claims(self) -> int:
        return len(self.matched) + len(self.residue)

    @property
    def rate(self) -> float:
        """Share of source claims placed without a model. 0.0 on an empty set."""
        total = self.source_claims
        return len(self.matched) / total if total else 0.0


def match(source: Decomposition, output: Decomposition) -> Coverage:
    """Place every source claim that survives verbatim into the output.

    Repeated text is matched as a multiset: two identical source claims need
    two identical output claims, and the second one is a merge survivor for
    stage 2 to rule on rather than a second hit on the same location. Order is
    ignored — the restructure reorders by design — but the *choice* among
    identical output claims is the first still free in output document order,
    so the result is stable under re-run.
    """
    free: dict[str, list[str]] = {}
    for claim in output.claims:
        free.setdefault(claim.text, []).append(claim.id)

    result = Coverage(doc=source.doc)
    taken: set[str] = set()
    for claim in source.claims:
        pending = free.get(claim.text)
        if pending:
            location = pending.pop(0)
            taken.add(location)
            result.matched.append(Match(source=claim.id, location=location))
        else:
            result.residue.append(claim)

    result.unplaced = [c for c in output.claims if c.id not in taken]
    return result


__all__ = ["VERBATIM", "Coverage", "Match", "match"]
