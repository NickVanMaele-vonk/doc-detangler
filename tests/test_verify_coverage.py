"""Coverage stage 1 — the deterministic match (ADR-003 Decision 2, build step 2).

Two things are held here. The unit tests fix the matching rule, including the
multiset behaviour that makes a dedup survivor residue rather than a second
hit on one location. The pinned-blob tests at the bottom are the build-step
gate: the real rate on the golden, plus the two measurements that justify
stage 1 being as strict as it is — both are written as live probes so the
numbers cannot rot into a comment nobody rechecks.
"""

from __future__ import annotations

import subprocess
from dataclasses import replace
from pathlib import Path

from detangle.verify.claims import Claim, Decomposition, decompose
from detangle.verify.coverage import match

#: eval/README.md's pinned blob for `U`, as in `test_verify_claims.py`. The
#: B-1 source correction re-baselines both files in the same PR.
PINNED_U_BLOB = "4cae72dece7638c1ddec8206a3c6a24610196de0"

GOLDEN = Path(__file__).resolve().parents[1] / "eval" / "golden" / "uce.md"


def claim(cid: str, text: str, kind: str = "prose") -> Claim:
    return Claim(id=cid, doc="U", kind=kind, text=text, para_hash="sha256:00")


def decomposition(doc: str, texts: list[str]) -> Decomposition:
    return Decomposition(
        doc=doc,
        version="test",
        claims=[claim(f"{doc}:aaaaaaaa:0:{i}", t) for i, t in enumerate(texts, 1)],
    )


# -- the matching rule -------------------------------------------------------


def test_a_claim_that_moved_verbatim_is_placed_at_confidence_one():
    src = decomposition("U", ["The engine must flag MEDIUM."])
    out = decomposition("O", ["Other prose.", "The engine must flag MEDIUM."])
    result = match(src, out)
    assert [m.source for m in result.matched] == [src.claims[0].id]
    assert result.matched[0].location == out.claims[1].id
    assert result.matched[0].confidence == 1.0
    assert result.matched[0].method == "verbatim"
    assert result.residue == []


def test_reordering_does_not_affect_the_match():
    """The restructure reorders by construction, so order carries no signal."""
    src = decomposition("U", ["First claim.", "Second claim.", "Third claim."])
    out = decomposition("O", ["Third claim.", "First claim.", "Second claim."])
    assert match(src, out).residue == []


def test_a_claim_that_changed_at_all_falls_to_the_residue():
    src = decomposition("U", ["The score must be >= 0.85."])
    out = decomposition("O", ["The score must be <= 0.85."])
    result = match(src, out)
    assert [c.text for c in result.residue] == ["The score must be >= 0.85."]
    assert result.matched == []


def test_case_is_not_folded_so_a_criterion_five_defect_stays_visible():
    src = decomposition("U", ["The engine must flag MEDIUM."])
    out = decomposition("O", ["The engine must flag medium."])
    assert len(match(src, out).residue) == 1


def test_a_source_claim_contained_in_a_longer_output_claim_is_residue():
    """Containment would place `v23` inside anything; identity will not."""
    src = decomposition("U", ["v23"])
    out = decomposition("O", ["v23 was the baseline document."])
    assert len(match(src, out).residue) == 1


# -- repeated text -----------------------------------------------------------


def test_two_identical_source_claims_need_two_identical_output_claims():
    src = decomposition("U", ["Repeated header row.", "Repeated header row."])
    out = decomposition("O", ["Repeated header row."])
    result = match(src, out)
    assert len(result.matched) == 1
    assert len(result.residue) == 1  # the merge survivor, for stage 2 to rule on
    assert result.unplaced == []


def test_identical_output_claims_are_consumed_in_document_order():
    src = decomposition("U", ["Same text."])
    out = decomposition("O", ["Same text.", "Same text."])
    result = match(src, out)
    assert result.matched[0].location == out.claims[0].id
    assert [c.id for c in result.unplaced] == [out.claims[1].id]


def test_the_match_is_stable_across_runs():
    src = decomposition("U", ["A.", "A.", "B."])
    out = decomposition("O", ["B.", "A.", "A."])
    first = match(src, out)
    assert first == match(src, out)


# -- the other direction and the totals --------------------------------------


def test_output_claims_nothing_explains_are_reported_unplaced():
    src = decomposition("U", ["Carried over."])
    out = decomposition("O", ["Carried over.", "[AI addition] Written to bridge."])
    result = match(src, out)
    assert [c.text for c in result.unplaced] == ["[AI addition] Written to bridge."]


def test_the_rate_counts_source_claims_and_survives_an_empty_set():
    src = decomposition("U", ["One.", "Two.", "Three.", "Four."])
    out = decomposition("O", ["One.", "Three."])
    result = match(src, out)
    assert (result.source_claims, result.rate) == (4, 0.5)
    assert match(decomposition("U", []), decomposition("O", [])).rate == 0.0


def test_no_findings_are_raised_here():
    """A residue claim is not an omission; it is a claim stage 1 declined."""
    from detangle.verify import coverage

    assert not hasattr(coverage, "CHECKS")


# -- the build-step gate: the pinned `U` blob against the golden -------------


def pinned_source() -> Decomposition:
    root = Path(__file__).resolve().parents[1]
    blob = subprocess.run(
        ["git", "-C", str(root), "cat-file", "blob", PINNED_U_BLOB],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return decompose(blob, "U")


def test_the_real_deterministic_rate_on_the_golden_is_pinned():
    """204 of 270 source claims place with no model involved.

    The ADR quotes 268 of 289 from the 5.3 hand analysis. Both figures move
    for the reason PR #116 already recorded for the decomposer's 270-vs-289:
    the hand count worked from the golden, where the 7 OCR page-split rows are
    rejoined and their repeated header fragments deduplicated, while the
    machine sees the raw shards. The 66 residue claims are page-split
    fragments and the version-history table, which the golden renders as prose
    — one cell becoming several sentences. Both are criterion-4 relocations,
    which is what stage 2 is for.
    """
    result = match(pinned_source(), decompose(GOLDEN.read_text(encoding="utf-8"), "U"))
    assert (len(result.matched), len(result.residue)) == (204, 66)
    assert result.source_claims == 270
    assert round(result.rate, 3) == 0.756
    assert len(result.unplaced) == 155


def test_case_folding_would_gain_nothing_so_strictness_is_free():
    """Measured, not assumed: the reason stage 1 does not fold case."""
    source = pinned_source()
    output = decompose(GOLDEN.read_text(encoding="utf-8"), "U")

    def lowered(d: Decomposition) -> Decomposition:
        return replace(d, claims=[replace(c, text=c.text.lower()) for c in d.claims])

    folded = match(lowered(source), lowered(output))
    assert len(folded.matched) == len(match(source, output).matched)


def test_run_concatenation_would_buy_nine_claims_and_is_declined():
    """A source claim equal to a run of consecutive output claims, and back.

    The looser rule is deterministic too, so the argument against it is
    yield, not safety: 9 claims out of 66, for a rule that asserts coverage
    no human reviews. This probe is what makes that number checkable rather
    than a claim in a docstring.
    """
    source = pinned_source()
    output = decompose(GOLDEN.read_text(encoding="utf-8"), "U")
    result = match(source, output)
    placed = {m.location for m in result.matched}
    spare = [c.text for c in output.claims if c.id not in placed]
    residue = [c.text for c in result.residue]

    gained = 0
    for text in residue:  # one source claim split into a run of output claims
        if any(_run_equals(spare, start, text) for start in range(len(spare))):
            gained += 1
    start = 0
    while start < len(residue):  # a run of source claims joined into one
        span = max(
            (n for n in range(2, 9) if " ".join(residue[start : start + n]) in spare),
            default=0,
        )
        gained += span
        start += span or 1

    assert gained == 9


def _run_equals(texts: list[str], start: int, target: str) -> bool:
    joined = ""
    for piece in texts[start : start + 8]:
        joined = piece if not joined else f"{joined} {piece}"
        if len(joined) > len(target):
            return False
        if joined == target:
            return True
    return False
