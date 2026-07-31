"""End to end: exit codes, JSON shape, and the C2 wording checks.

These run against a real git repo and real pandoc, because both are part of
what `validate` asserts.
"""

import json

from detangle.cli import main
from detangle.findings import EXIT_CLEAN, EXIT_FINDINGS, EXIT_USAGE


def run(mini_repo, *extra, capsys=None):
    code = main(["validate", "--root", str(mini_repo.root), "--json", *extra])
    payload = json.loads(capsys.readouterr().out) if capsys else None
    return code, payload


def test_a_clean_record_set_exits_zero(mini_repo, capsys):
    mini_repo.write_record()
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_CLEAN
    assert payload["findings"] == []
    assert payload["summary"] == {"records": 1, "checked": 1, "defined": 1}


def test_findings_exit_one(mini_repo, capsys):
    mini_repo.write_record(used_in=["U"], placement="MCL")
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_FINDINGS
    assert [f["check"] for f in payload["findings"]] == ["placement-computed"]
    assert payload["counts"] == {"error": 1, "warn": 0}


def test_a_stale_git_blob_is_a_warning_not_an_error(mini_repo, capsys):
    """A hash mismatch means re-verify the span, not that the record is wrong."""
    span = mini_repo.span("A widget is a device")
    span["verified_against"]["git_blob"] = "0" * 40
    mini_repo.write_record(source=[span])
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_FINDINGS
    assert payload["counts"] == {"error": 0, "warn": 1}
    assert payload["findings"][0]["check"] == "git-blob-stale"


def test_a_stale_para_hash_is_a_warning(mini_repo, capsys):
    span = mini_repo.span("A widget is a device")
    span["para_hash"] = "sha256:" + "0" * 64
    mini_repo.write_record(source=[span])
    _, payload = run(mini_repo, capsys=capsys)
    assert [f["check"] for f in payload["findings"]] == ["para-hash-stale"]
    assert payload["findings"][0]["severity"] == "warn"


def test_an_invented_definition_fails_the_verbatim_floor(mini_repo, capsys):
    mini_repo.write_record(
        definition="Something entirely unrelated to anything in the corpus."
    )
    _, payload = run(mini_repo, capsys=capsys)
    assert "definition-not-verbatim" in {f["check"] for f in payload["findings"]}


def test_a_code_not_in_the_anchored_block_is_reported(mini_repo, capsys):
    """C2 constrains domain wording: codes must come from the source."""
    mini_repo.write_record(
        definition="A widget is a device that emits SB-99 alerts",
    )
    findings = run(mini_repo, capsys=capsys)[1]["findings"]
    assert [f["check"] for f in findings] == ["definition-token"]
    assert "SB-99" in findings[0]["message"]


def test_ordinary_english_is_free(mini_repo, capsys):
    """Nick, 2026-07-30: connective and descriptive words need no provenance."""
    mini_repo.write_record(
        definition=(
            "A widget is a device that emits SB-01 alerts, catalogued and "
            "identified by its abuse pattern."
        )
    )
    assert run(mini_repo, capsys=capsys)[0] == EXIT_CLEAN


def test_a_number_not_in_the_source_is_reported(mini_repo, capsys):
    mini_repo.write_record(
        definition="A widget is a device that emits SB-01 alerts at 0.99"
    )
    findings = run(mini_repo, capsys=capsys)[1]["findings"]
    assert [f["check"] for f in findings] == ["definition-number"]


def test_sentence_final_punctuation_is_not_part_of_a_number(mini_repo, capsys):
    """'>= 0.85.' must not be looked up with its full stop attached."""
    mini_repo.write_record(
        definition="A widget is a device that emits SB-01 alerts when >= 0.85."
    )
    assert run(mini_repo, capsys=capsys)[0] == EXIT_CLEAN


def test_paths_narrow_the_per_record_checks(mini_repo, capsys):
    mini_repo.write_record(id="widget", term="widget")
    broken = mini_repo.write_record(id="gadget", term="gadget", placement="MCL")
    code, payload = run(mini_repo, str(broken), capsys=capsys)
    assert code == EXIT_FINDINGS
    assert payload["summary"]["records"] == 2
    assert payload["summary"]["checked"] == 1


def test_set_wide_checks_run_even_when_paths_narrow_the_rest(mini_repo, capsys):
    """A PR touching one record can break an invariant living between two."""
    widget = mini_repo.write_record(id="widget", term="widget")
    mini_repo.write_record(id="gadget", term="gadget", aliases=["Widget"])
    _, payload = run(mini_repo, str(widget), capsys=capsys)
    assert "one-definition-site" in {f["check"] for f in payload["findings"]}


def test_an_unparseable_record_is_a_finding_not_a_crash(mini_repo, capsys):
    mini_repo.write_record()
    (mini_repo.root / "concepts" / "broken.yaml").write_text("key: [unclosed\n")
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_FINDINGS
    assert "yaml-parse" in {f["check"] for f in payload["findings"]}


def test_a_missing_config_exits_two(tmp_path, capsys):
    assert main(["validate", "--root", str(tmp_path)]) == EXIT_USAGE
    assert "detangle.toml" in capsys.readouterr().err


def test_unknown_paths_exit_two(mini_repo, capsys):
    mini_repo.write_record()
    code = main(["validate", "--root", str(mini_repo.root), "nowhere.yaml"])
    assert code == EXIT_USAGE


def test_a_missing_concepts_directory_is_exit_two_not_a_clean_run(mini_repo, capsys):
    """The false green: Path.glob on a missing directory yields nothing."""
    (mini_repo.root / "concepts").rename(mini_repo.root / "elsewhere")
    code, _ = run(mini_repo)
    assert code == EXIT_USAGE


def test_an_internal_error_exits_two_never_one(mini_repo, monkeypatch):
    """ADR-001 D2: "Never 1 for a crash."

    Branch policy reads 1 as "findings raised — post them and block". A crash
    that exits 1 is therefore reported as a completed run, which is the one
    failure mode the exit-code contract exists to prevent.
    """
    from detangle import cli

    def boom(args):
        raise RuntimeError("internal error, not a finding")

    monkeypatch.setattr(cli, "cmd_validate", boom)
    assert cli.main(["validate", "--root", str(mini_repo.root)]) == EXIT_USAGE
