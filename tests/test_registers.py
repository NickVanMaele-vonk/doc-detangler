"""The waiver register (plan step 3.9) and its suppression semantics.

A waiver is a deferral, not an approval, so the tests here assert two things
in pairs: that a covered finding stops blocking, and that it stays visible.
Cycle-register coverage lives in `test_graph.py`, next to the graph that
consumes it.
"""

import json

from conftest import BASE_WAIVER

from detangle.cli import main
from detangle.findings import EXIT_CLEAN, EXIT_FINDINGS


def waiver(**overrides) -> dict:
    return {**BASE_WAIVER, **overrides}


def run(mini_repo, *extra, capsys):
    code = main(["validate", "--root", str(mini_repo.root), "--json", *extra])
    return code, json.loads(capsys.readouterr().out)


def misplaced(mini_repo):
    """A record raising exactly one finding: `placement-computed`."""
    return mini_repo.write_record(used_in=["U"], placement="MCL")


def test_no_register_is_not_an_error(mini_repo, capsys):
    """A set with nothing deferred needs no register."""
    mini_repo.write_record()
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_CLEAN
    assert payload["waived"] == []


def test_a_malformed_register_is_a_finding(mini_repo, capsys):
    misplaced(mini_repo)
    (mini_repo.root / "registers" / "waivers.yaml").write_text(
        "waivers: [unclosed\n", encoding="utf-8"
    )
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_FINDINGS
    assert "register-parse" in [f["check"] for f in payload["findings"]]


def test_a_wrong_shaped_top_level_is_a_finding(mini_repo, capsys):
    misplaced(mini_repo)
    (mini_repo.root / "registers" / "waivers.yaml").write_text(
        "entries: []\n", encoding="utf-8"
    )
    _, payload = run(mini_repo, capsys=capsys)
    assert [f["check"] for f in payload["findings"]].count("register-parse") == 1


def test_an_incomplete_entry_is_skipped_and_waives_nothing(mini_repo, capsys):
    """A half-read waiver must never suppress anything."""
    misplaced(mini_repo)
    entry = waiver()
    del entry["owner"]
    del entry["review_by"]
    mini_repo.write_waivers(entry)
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_FINDINGS
    checks = [f["check"] for f in payload["findings"]]
    assert "register-parse" in checks
    assert "placement-computed" in checks  # not suppressed
    assert payload["waived"] == []
    message = next(f for f in payload["findings"] if f["check"] == "register-parse")
    assert "'owner'" in message["message"] and "'review_by'" in message["message"]


def test_a_covered_finding_stops_blocking_but_stays_visible(mini_repo, capsys):
    misplaced(mini_repo)
    mini_repo.write_waivers(waiver())
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_CLEAN
    assert payload["findings"] == []
    assert [f["check"] for f in payload["waived"]] == ["placement-computed"]
    assert payload["counts"] == {"error": 0, "warn": 0, "waived": 1}
    assert payload["summary"]["waived"] == 1
    assert payload["waived"][0]["waiver"] == {
        "id": "placement-deferred",
        "disposition": "source-defect",
        "owner": "Nick",
        "ticket": "B-1",
        "review_by": "2026-12-31",
    }


def test_match_narrows_to_one_message(mini_repo, capsys):
    misplaced(mini_repo)
    mini_repo.write_waivers(waiver(match="computes to 'UCE'"))
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_CLEAN
    assert len(payload["waived"]) == 1


def test_a_match_that_misses_leaves_the_finding_live(mini_repo, capsys):
    """The narrowing is a substring test, so a typo fails open, not shut."""
    misplaced(mini_repo)
    mini_repo.write_waivers(waiver(match="no such wording"))
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_FINDINGS
    assert payload["waived"] == []
    assert sorted(f["check"] for f in payload["findings"]) == [
        "placement-computed",
        "waiver-stale",
    ]


def test_a_waiver_matching_nothing_is_stale(mini_repo, capsys):
    """Entries and live findings are 1:1: the fix removes the waiver with it."""
    mini_repo.write_record()
    mini_repo.write_waivers(waiver())
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_FINDINGS
    assert payload["findings"][0]["check"] == "waiver-stale"
    assert payload["findings"][0]["severity"] == "warn"
    where = payload["findings"][0]["where"]
    assert where == "registers/waivers.yaml:placement-deferred"


def test_staleness_is_not_computed_on_a_narrowed_run(mini_repo, capsys):
    """A record the run never checked cannot prove its waiver dead."""
    path = mini_repo.write_record()
    mini_repo.write_waivers(waiver())
    code, payload = run(mini_repo, str(path), capsys=capsys)
    assert code == EXIT_CLEAN
    assert payload["findings"] == []


def test_two_entries_for_one_finding_are_flagged(mini_repo, capsys):
    misplaced(mini_repo)
    mini_repo.write_waivers(waiver(), waiver(id="placement-deferred-again"))
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_FINDINGS
    assert "waiver-duplicate-entry" in [f["check"] for f in payload["findings"]]


def test_a_repeated_id_is_flagged(mini_repo, capsys):
    """Ids are how a waiver is cited and how staleness is tracked."""
    misplaced(mini_repo)
    mini_repo.write_waivers(waiver(), waiver(where="concepts/widget.yaml:definition"))
    _, payload = run(mini_repo, capsys=capsys)
    duplicates = [
        f for f in payload["findings"] if f["check"] == "waiver-duplicate-entry"
    ]
    assert len(duplicates) == 1
    assert "used twice" in duplicates[0]["message"]


def test_the_register_cannot_excuse_itself(mini_repo, capsys):
    """A malformed register must not be able to waive its own parse failure."""
    misplaced(mini_repo)
    broken = waiver(id="incomplete")
    del broken["ticket"]
    mini_repo.write_waivers(
        broken,
        waiver(
            id="self-excusing",
            check="register-parse",
            where="registers/waivers.yaml:waivers[0]",
        ),
    )
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_FINDINGS
    checks = [f["check"] for f in payload["findings"]]
    assert "waiver-not-waivable" in checks
    assert "register-parse" in checks  # still live
    assert payload["waived"] == []


def test_a_waiver_cannot_waive_staleness_findings(mini_repo, capsys):
    mini_repo.write_record()
    mini_repo.write_waivers(
        waiver(),
        waiver(
            id="stale-suppressor",
            check="waiver-stale",
            where="registers/waivers.yaml:placement-deferred",
        ),
    )
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_FINDINGS
    assert "waiver-not-waivable" in [f["check"] for f in payload["findings"]]


def test_the_text_report_names_the_disposition(mini_repo, capsys):
    """The point of reporting rather than dropping: debt stays in the log."""
    misplaced(mini_repo)
    mini_repo.write_waivers(waiver())
    code = main(["validate", "--root", str(mini_repo.root)])
    out = capsys.readouterr().out
    assert code == EXIT_CLEAN
    assert "waived (1) — accepted debt, not blocking" in out
    assert "waived: source-defect (Nick, B-1, review by 2026-12-31)" in out
    assert "clean — no findings" in out
