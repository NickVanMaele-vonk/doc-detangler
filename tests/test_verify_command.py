"""`detangle verify` — ADR-003 Decision 5, ruled by Nick 2026-08-07.

The command runs deterministically, and the thing most worth testing is what
it says about the half it did not run. A clean exit on a run that never
checked for invented text would be a proof the tool did not produce, so the
absence has to reach the report, the summary and the exit code.
"""

from __future__ import annotations

import json
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path

import pytest

from detangle.cli import main
from detangle.findings import EXIT_FINDINGS, EXIT_USAGE
from detangle.verify import report as verify_report

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = "eval/golden/uce.md"


# -- usage -------------------------------------------------------------------


def test_output_wants_code_equals_path():
    assert main(["verify", "--root", str(ROOT), "--output", "eval/x.md"]) == EXIT_USAGE


def test_a_reference_document_cannot_be_verified():
    """`A` and `P` are read-only: never restructured, so never an output."""
    assert main(["verify", "--root", str(ROOT), "--output", "A=x.md"]) == EXIT_USAGE


def test_a_missing_output_exits_two_not_one():
    """Exit 2 is the absence of a verdict, never "no findings"."""
    code = main(["verify", "--root", str(ROOT), "--output", "U=eval/nope.md"])
    assert code == EXIT_USAGE


# -- the real run ------------------------------------------------------------


@pytest.fixture(scope="module")
def real() -> tuple[int, dict]:
    """One real run over the golden, shared: it decomposes two documents."""
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(
            ["verify", "--root", str(ROOT), "--json", "--output", f"U={GOLDEN}"]
        )
    return code, json.loads(buffer.getvalue())


def test_the_golden_run_reports_the_known_finding(real):
    """`coverage-unscored` alone: the once-pinned `forward-use` was the
    banner's "CI gate" phrase colliding with the record `gate`, and the
    2026-08-08 banner rewrite removed the phrase (test_verify_structure)."""
    code, payload = real
    assert code == EXIT_FINDINGS
    checks = sorted(f["check"] for f in payload["findings"])
    assert checks == ["coverage-unscored"]


def test_the_summary_says_fabrication_was_not_checked(real):
    """The one line a reader of a green-looking run must not be able to miss."""
    _, payload = real
    assert payload["summary"]["fabrication"].startswith("NOT CHECKED")


def test_the_summary_carries_the_measured_numbers(real):
    _, payload = real
    summary = payload["summary"]
    assert summary["placed verbatim"] == 204
    assert summary["unscored"] == 66
    assert summary["forward references"] == 0
    assert summary["exempt"] == 1
    assert summary["reading order"] == "glossary → U"


def test_the_unscored_finding_is_one_per_document_not_one_per_claim(real):
    """Comments are raised per cluster, not per instance (rubric §8d)."""
    _, payload = real
    unscored = [f for f in payload["findings"] if f["check"] == "coverage-unscored"]
    assert len(unscored) == 1
    assert unscored[0]["severity"] == "warn"
    assert "66 of 270" in unscored[0]["message"]


# -- the report --------------------------------------------------------------


@pytest.fixture(scope="module")
def rendered(tmp_path_factory) -> str:
    out = tmp_path_factory.mktemp("verify") / "report.md"
    main(
        [
            "verify", "--root", str(ROOT), "--json",
            "--output", f"U={GOLDEN}", "--report", str(out),
        ]
    )
    return out.read_text(encoding="utf-8")


def test_the_report_prints_the_stages_it_did_not_run(rendered):
    """A stage missing from the table is a stage a reader assumes ran."""
    for step, name, _ran in verify_report.STAGES:
        assert f"| {step} | {name} |" in rendered
    assert rendered.count("**not run**") == 2
    assert "did not check for invented text" in rendered


def test_the_report_records_the_version_of_every_document_read(rendered):
    """Step 7.5 — a blob is the version, and it stays retrievable."""
    assert "## Versions verified (step 7.5)" in rendered
    for rel in ("glossary.md", "samples/blueprint-UCE-shortened.md", GOLDEN):
        assert f"`{rel}`" in rendered
    # The pinned `U` blob, as `eval/README.md` records it.
    assert "4cae72dece7638c1ddec8206a3c6a24610196de0" in rendered


def test_the_report_carries_no_timestamp_so_it_is_reproducible(rendered):
    """The commit and the blobs date the run; a clock would make it drift."""
    assert "Run at commit `" in rendered
    lowered = rendered.lower()
    assert "generated at" not in lowered
    assert "timestamp" not in lowered


def test_the_residue_roster_lists_every_unplaced_claim(rendered):
    """A work-list, not a number — the next pass needs the claims themselves."""
    section = rendered.split("## Residue roster", 1)[1]
    assert section.count("\n- `U:") == 66


def test_the_report_names_the_decomposer_version(rendered):
    """§2.8: the decomposer moves the scores, so every report records it."""
    assert f"decomposer `{verify_report.DECOMPOSER_VERSION}`" in rendered


# -- the claim-split register (home ruled by Nick 2026-08-07) ----------------


def test_the_register_is_read_and_counted_even_when_empty(real):
    """Zero overrides and no register at all give identical claim lists.

    Only one of those two means nobody has ruled yet, so the run says which.
    """
    _, payload = real
    assert payload["summary"]["claim-split overrides"] == 0


def test_the_report_records_the_register_as_a_version_of_the_run(rendered):
    """The overrides move the claim list, so the report names the blob."""
    assert "| `registers/claim-splits.yaml` | override register |" in rendered
    assert "no claim-split overrides (the register is empty)" in rendered


def test_a_malformed_register_blocks_the_run_and_cannot_be_waived(tmp_path):
    """It is not a partial read: nothing downstream may proceed on one."""
    config = tmp_path / "detangle.toml"
    config.write_text(
        (ROOT / "detangle.toml")
        .read_text(encoding="utf-8")
        .replace(
            'claim-splits = "registers/claim-splits.yaml"',
            'claim-splits = "detangle.toml"',  # real file, not a register
        ),
        encoding="utf-8",
    )
    buffer = StringIO()
    with redirect_stdout(buffer):
        code = main(
            [
                "verify", "--root", str(ROOT), "--json", "--config", str(config),
                "--output", f"U={GOLDEN}",
            ]
        )
    payload = json.loads(buffer.getvalue())
    assert code == EXIT_FINDINGS
    assert [f["check"] for f in payload["findings"]] == ["split-parse"]
    assert payload["waived"] == []
    assert "placed verbatim" not in payload["summary"]
