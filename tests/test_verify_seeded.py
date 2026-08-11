"""Seeded-error tests — ADR-003 Decision 6, ruled by Nick 2026-08-10.

Phase 7's done-when requires the harness to catch three deliberately planted
errors: a deleted claim, an invented claim, and a weakened claim — a changed
threshold plus a `must` downgraded to `should`, per C7. The seeds are
scripted mutations of a copy of the approved golden output, which is heavily
reordered relative to source by construction — never lightly-edited text,
because reordered text is the regime the harness exists for.

What "caught" means in the deterministic build: a deleted or weakened claim
falls out of the verbatim matches into the residue, where the report's
roster names it and `coverage-unscored` counts it — surfaced for a
disposition rather than silently passing. The weakened seed is caught by the
harness on its own, not behind the restructure's token-parity check: this
file never runs `restructure`.

The invented claim is the known open limb. Deterministically it lands among
the unexplained output claims — the narrowing works — but ruling it
*fabricated* needs the model stage (ADR-003 Decision 3, deferred to backlog
B-9), so that leg is held as a strict xfail. B-9's build rewrites that test
to run under `--use-inference`; the strict marker is what forces the rewrite
to notice it.

Each mutated copy is written inside the repo root and removed again: the
step 7.5 version record resolves the output path against the root and
git-hashes the bytes, so the file has to live where `git hash-object` can
name it.
"""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest

from detangle.cli import main
from detangle.findings import EXIT_FINDINGS

ROOT = Path(__file__).resolve().parent / "data"
GOLDEN = ROOT / "eval" / "golden" / "uce.md"

#: The three seeds, each a full claim under `param-claim-granularity` (a cell
#: is one claim) that today places verbatim at confidence 1.0. Each must occur
#: exactly once in the golden, so the mutation is unambiguous — asserted
#: before every run, so a golden edit that duplicates one fails loudly here.
DELETED = "CCL gate: CCL=0 blocks VERY HIGH regardless of all other scores."
DOWNGRADED = "Every classification must withstand regulatory examination."
RETHRESHOLDED = (
    "Kill Switch forces downgrade to MEDIUM/CLOSE where ≥3 negative "
    "conditions apply."
)
INVENTED = (
    "The engine also archives every disposed signal to cold storage "
    "after 90 days."
)


def run_seeded(tmp_path_factory, name: str, mutate) -> tuple[int, dict, str]:
    """One `detangle verify` run over a mutated copy of the golden."""
    text = GOLDEN.read_text(encoding="utf-8")
    mutated = mutate(text)
    assert mutated != text
    rel = f".seeded-{name}.md"
    path = ROOT / rel
    report = tmp_path_factory.mktemp(name) / "report.md"
    path.write_text(mutated, encoding="utf-8")
    try:
        buffer = StringIO()
        with redirect_stdout(buffer):
            code = main(
                [
                    "verify", "--root", str(ROOT), "--json",
                    "--output", f"U={path}", "--report", str(report),
                ]
            )
    finally:
        path.unlink()
    return code, json.loads(buffer.getvalue()), report.read_text(encoding="utf-8")


def once(text: str, seed: str) -> str:
    assert text.count(seed) == 1, f"seed no longer unique in the golden: {seed!r}"
    return seed


# -- the deleted claim --------------------------------------------------------


@pytest.fixture(scope="module")
def deleted(tmp_path_factory) -> tuple[int, dict, str]:
    return run_seeded(
        tmp_path_factory, "deleted", lambda t: t.replace(once(t, DELETED), "")
    )


def test_a_deleted_claim_falls_out_of_the_verbatim_matches(deleted):
    """The source claim can no longer place: 204 → 203, and the residue —
    the roster of claims this run cannot vouch for — picks it up."""
    code, payload, _ = deleted
    assert code == EXIT_FINDINGS
    assert payload["summary"]["placed verbatim"] == 203
    assert payload["summary"]["unscored"] == 67


def test_the_deleted_claim_is_named_in_the_residue_roster(deleted):
    """Flagged means named: the next pass gets the claim, not a count."""
    _, payload, rendered = deleted
    assert DELETED in rendered.split("## Residue roster", 1)[1]
    unscored = [f for f in payload["findings"] if f["check"] == "coverage-unscored"]
    assert len(unscored) == 1
    assert "67 of 270" in unscored[0]["message"]


def test_deleting_an_output_claim_leaves_the_unexplained_count_alone(deleted):
    """The document lost a claim; it did not gain one nothing explains."""
    _, _, rendered = deleted
    assert "| U | 270 | 203 (75.2%) | 67 | 155 |" in rendered


# -- the weakened claim -------------------------------------------------------


@pytest.fixture(scope="module")
def weakened(tmp_path_factory) -> tuple[int, dict, str]:
    """Both C7 weakenings: a `must` downgraded, a threshold moved."""

    def mutate(text: str) -> str:
        text = text.replace(
            once(text, DOWNGRADED), DOWNGRADED.replace("must", "should")
        )
        return text.replace(
            once(text, RETHRESHOLDED), RETHRESHOLDED.replace("≥3", "≥4")
        )

    return run_seeded(tmp_path_factory, "weakened", mutate)


def test_a_weakened_claim_is_no_longer_verbatim_and_falls_to_the_residue(weakened):
    """Text identity is the whole rule, so one word or one digit is enough:
    both weakened source claims drop out of the matches."""
    code, payload, rendered = weakened
    assert code == EXIT_FINDINGS
    assert payload["summary"]["placed verbatim"] == 202
    assert payload["summary"]["unscored"] == 68
    roster = rendered.split("## Residue roster", 1)[1]
    assert DOWNGRADED in roster
    assert RETHRESHOLDED in roster


def test_the_weakened_text_is_also_unexplained_on_the_output_side(weakened):
    """Both directions move: the weakened wording matches no source claim, so
    it joins the fabrication candidates (155 → 157) — G1's bidirectional
    frame catching one edit twice."""
    _, _, rendered = weakened
    assert "| U | 270 | 202 (74.8%) | 68 | 157 |" in rendered


# -- the invented claim -------------------------------------------------------


@pytest.fixture(scope="module")
def invented(tmp_path_factory) -> tuple[int, dict, str]:
    return run_seeded(
        tmp_path_factory,
        "invented",
        lambda t: t.rstrip() + f"\n\n{INVENTED}\n",
    )


def test_an_invented_claim_is_narrowed_to_the_unexplained_set(invented):
    """The deterministic half of the catch: nothing else moves (204/66 hold),
    and the invention lands in the unexplained column (155 → 156). What it
    cannot do is tell the invention apart from the 155 legitimate entries —
    that verdict is Decision 3's."""
    _, payload, rendered = invented
    assert payload["summary"]["placed verbatim"] == 204
    assert payload["summary"]["unscored"] == 66
    assert "| U | 270 | 204 (75.6%) | 66 | 156 |" in rendered


@pytest.mark.xfail(
    strict=True,
    reason="fabrication needs the model stage: ADR-003 Decision 3, deferred "
    "behind --use-inference as backlog B-9. Decision 6's invented-claim limb "
    "stays open until B-9 lands and rewrites this test to run inference.",
)
def test_an_invented_claim_is_flagged_as_fabrication(invented):
    """The open limb of Decision 6's done-when, held here so it cannot be
    forgotten: no deterministic run raises a fabrication finding."""
    _, payload, _ = invented
    assert any(f["check"] == "fabrication" for f in payload["findings"])


def test_the_deterministic_run_says_it_did_not_check_for_invention(invented):
    """Until then, the run must say so — the absence reaches the summary."""
    _, payload, _ = invented
    assert payload["summary"]["fabrication"].startswith("NOT CHECKED")
