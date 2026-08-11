"""The glossary drift lint (`detangle lift`) — the fourth CI gate.

The rulings under test are Nick's of 2026-08-08: the tool lifts and
``--check`` gates (the record's definition copy is derived data, C12), and
lineage is maintained mechanically while assurance stays a human's to write
(ADR-004). Ontology — headings, aliases — is never written, only flagged.
"""

import json
import subprocess
from pathlib import Path

import yaml

from detangle.cli import main
from detangle.findings import EXIT_CLEAN, EXIT_FINDINGS
from detangle.records import load_records
from detangle.records.spans import BlockIndex

REPO = Path(__file__).resolve().parent / "data"

GLOSSARY = """\
<!--
Banner: metadata only.
-->

# Glossary

## Overview

Free text above the first marker is the file's own and is never lifted.

<!-- concept:doohickey:start -->
## doohickey

> **Not defined in the corpus.** The source documents use this term but never
> define it.
<!-- concept:doohickey:end -->

<!-- concept:widget:start -->
## widget

**Also known as:** gizmo

A widget is a device that emits SB-01 alerts
<!-- concept:widget:end -->

A note between entries belongs to the file alone.
"""


def seed(mini_repo, glossary=GLOSSARY):
    # Both glossary-placed: used in two components (C9 limb 1). The edge
    # makes the topological order deterministic: doohickey defines first.
    mini_repo.write_record(
        id="widget",
        term="widget",
        aliases=["gizmo"],
        placement="glossary",
        used_in=["U", "S"],
        depends_on=["doohickey"],
    )
    mini_repo.write_record(
        id="doohickey",
        term="doohickey",
        placement="glossary",
        used_in=["U", "S"],
        definition=None,
    )
    (mini_repo.root / "glossary.md").write_text(glossary, encoding="utf-8")


def run(mini_repo, *extra, capsys=None):
    code = main(["lift", "--root", str(mini_repo.root), "--json", *extra])
    payload = json.loads(capsys.readouterr().out) if capsys else None
    return code, payload


def checks_of(payload) -> list[str]:
    return [f["check"] for f in payload["findings"]]


def record_data(mini_repo, rid: str) -> dict:
    path = mini_repo.root / "concepts" / f"{rid}.yaml"
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_untouched_file_is_clean_both_ways(mini_repo, capsys):
    seed(mini_repo)
    code, payload = run(mini_repo, "--check", capsys=capsys)
    assert code == EXIT_CLEAN
    assert payload["findings"] == []
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_CLEAN
    assert "nothing" in payload["summary"]["lifted"]


def test_an_edit_is_drift_until_lifted(mini_repo, capsys):
    seed(mini_repo, GLOSSARY.replace("emits SB-01 alerts", "emits loud alerts"))
    code, payload = run(mini_repo, "--check", capsys=capsys)
    assert code == EXIT_FINDINGS
    assert checks_of(payload) == ["lift-drift"]
    assert "concepts/widget.yaml" in payload["findings"][0]["where"]


def test_lift_mirrors_the_edit_and_check_then_passes(mini_repo, capsys):
    seed(mini_repo, GLOSSARY.replace("emits SB-01 alerts", "emits loud alerts"))
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_CLEAN
    assert payload["summary"]["lifted"] == "widget"

    data = record_data(mini_repo, "widget")
    assert data["definition"] == "A widget is a device that emits loud alerts"
    # Mechanical lineage (ADR-004): the corpus span is history and stays; the
    # authored span binds the glossary's live blob and the prose's block hash.
    origins = [s["origin"] for s in data["source"]]
    assert origins == ["corpus", "authored"]
    authored = data["source"][-1]
    assert authored["doc"] == "glossary.md"
    assert authored["verified_against"]["stated_version"] is None
    index = BlockIndex(root=mini_repo.root)
    assert index.document("glossary.md").text_for(authored["para_hash"])

    # Everything else on the record is untouched.
    assert data["aliases"] == ["gizmo"]
    assert data["assurance"] == {"author": "assistant", "approved_by": None, "pr": None}

    code, payload = run(mini_repo, "--check", capsys=capsys)
    assert code == EXIT_CLEAN
    assert payload["findings"] == []


def test_filling_an_undefined_entry_lifts_but_demands_an_author(
    mini_repo, capsys
):
    filled = GLOSSARY.replace(
        "> **Not defined in the corpus.** The source documents use this term "
        "but never\n> define it.",
        "A doohickey is a device that a widget uses.",
    )
    seed(mini_repo, filled)
    code, payload = run(mini_repo, capsys=capsys)
    # Written, and still exit 1: the human owes the assurance block.
    assert code == EXIT_FINDINGS
    assert checks_of(payload) == ["lift-assurance-missing"]
    data = record_data(mini_repo, "doohickey")
    assert data["definition"] == "A doohickey is a device that a widget uses."
    assert data["source"][-1]["origin"] == "authored"

    # The human names themselves; the gate goes green.
    path = mini_repo.root / "concepts" / "doohickey.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "assurance: null",
            "assurance:\n  author: Nick\n  approved_by: null\n  pr: null",
        ),
        encoding="utf-8",
    )
    code, payload = run(mini_repo, "--check", capsys=capsys)
    assert code == EXIT_CLEAN


def test_a_filled_definition_survives_validate_once_committed(mini_repo, capsys):
    """The authored span satisfies the C2 wording checks and span checks."""
    test_filling_an_undefined_entry_lifts_but_demands_an_author(mini_repo, capsys)
    subprocess.run(
        ["git", "-C", str(mini_repo.root), "add", "-A"],
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "-C", str(mini_repo.root), "commit", "-qm", "fill doohickey"],
        check=True,
        capture_output=True,
    )
    code = main(["validate", "--root", str(mini_repo.root), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert code == EXIT_CLEAN, payload["findings"]


def test_deleting_prose_mirrors_null_and_drops_the_owned_span(mini_repo, capsys):
    test_lift_mirrors_the_edit_and_check_then_passes(mini_repo, capsys)
    reverted = GLOSSARY.replace(
        "A widget is a device that emits SB-01 alerts",
        "> **Not defined in the corpus.** No more.",
    )
    (mini_repo.root / "glossary.md").write_text(reverted, encoding="utf-8")
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_CLEAN
    data = record_data(mini_repo, "widget")
    assert data["definition"] is None
    assert [s["origin"] for s in data["source"]] == ["corpus"]


def test_a_multiline_comment_in_an_entry_is_not_prose(mini_repo, capsys):
    """GHAS review on PR #138: comments are stripped as spans, not lines, so
    a comment spanning lines inside a block cannot leak into the lift."""
    noted = GLOSSARY.replace(
        "A widget is a device that emits SB-01 alerts",
        "A widget <!-- reviewer\nnote spanning lines --> is a device that "
        "emits <!-- inline --> SB-01 alerts",
    )
    seed(mini_repo, noted)
    code, payload = run(mini_repo, "--check", capsys=capsys)
    # Comment innards gone, the text around the inline comment kept — the
    # prose equals the record's definition, so there is nothing to lift.
    assert code == EXIT_CLEAN
    assert payload["findings"] == []


def test_a_changed_heading_is_flagged_never_written(mini_repo, capsys):
    seed(mini_repo, GLOSSARY.replace("## widget", "## Widget (Device)"))
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_FINDINGS
    assert checks_of(payload) == ["lift-ontology-drift"]
    assert record_data(mini_repo, "widget")["term"] == "widget"


def test_a_changed_alias_line_is_flagged_never_written(mini_repo, capsys):
    seed(mini_repo, GLOSSARY.replace("**Also known as:** gizmo", ""))
    code, payload = run(mini_repo, "--check", capsys=capsys)
    assert code == EXIT_FINDINGS
    assert checks_of(payload) == ["lift-ontology-drift"]
    assert record_data(mini_repo, "widget")["aliases"] == ["gizmo"]


def test_prose_beside_the_gap_note_is_a_stale_note(mini_repo, capsys):
    stale = GLOSSARY.replace(
        "<!-- concept:doohickey:end -->",
        "\nA doohickey is a device that a widget uses.\n"
        "<!-- concept:doohickey:end -->",
    )
    seed(mini_repo, stale)
    code, payload = run(mini_repo, "--check", capsys=capsys)
    assert code == EXIT_FINDINGS
    assert "lift-stale-note" in checks_of(payload)


def test_an_entry_without_a_record_is_unknown(mini_repo, capsys):
    extra = GLOSSARY + (
        "\n<!-- concept:mystery:start -->\n## mystery\n\nSome prose.\n"
        "<!-- concept:mystery:end -->\n"
    )
    seed(mini_repo, extra)
    code, payload = run(mini_repo, "--check", capsys=capsys)
    assert code == EXIT_FINDINGS
    assert "lift-unknown-entry" in checks_of(payload)


def test_a_document_placed_record_may_not_have_an_entry(mini_repo, capsys):
    seed(mini_repo)
    mini_repo.write_record(id="gadget", term="gadget", placement="UCE")
    with_entry = GLOSSARY + (
        "\n<!-- concept:gadget:start -->\n## gadget\n\nSome prose.\n"
        "<!-- concept:gadget:end -->\n"
    )
    (mini_repo.root / "glossary.md").write_text(with_entry, encoding="utf-8")
    code, payload = run(mini_repo, "--check", capsys=capsys)
    assert code == EXIT_FINDINGS
    assert "lift-unknown-entry" in checks_of(payload)


def test_a_glossary_record_without_an_entry_is_missing(mini_repo, capsys):
    seed(mini_repo, GLOSSARY.split("<!-- concept:widget:start -->")[0])
    code, payload = run(mini_repo, "--check", capsys=capsys)
    assert code == EXIT_FINDINGS
    assert "lift-missing-entry" in checks_of(payload)


def test_a_duplicated_entry_is_flagged(mini_repo, capsys):
    dup = GLOSSARY + (
        "\n<!-- concept:widget:start -->\n## widget\n\n"
        "**Also known as:** gizmo\n\nA widget is a device that emits SB-01 "
        "alerts\n<!-- concept:widget:end -->\n"
    )
    seed(mini_repo, dup)
    code, payload = run(mini_repo, "--check", capsys=capsys)
    assert code == EXIT_FINDINGS
    assert "lift-duplicate-entry" in checks_of(payload)


def test_an_unclosed_entry_is_flagged_and_not_lifted(mini_repo, capsys):
    broken = GLOSSARY.replace("<!-- concept:doohickey:end -->\n", "").replace(
        "> define it.", "> define it.\n\nOrphaned prose that must not lift."
    )
    seed(mini_repo, broken)
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_FINDINGS
    assert "lift-unclosed-entry" in checks_of(payload)
    assert record_data(mini_repo, "doohickey")["definition"] is None


def test_entries_out_of_topological_order_are_flagged(mini_repo, capsys):
    head, doohickey_entry, widget_entry = (
        GLOSSARY.split("<!-- concept:doohickey:start -->")[0],
        "<!-- concept:doohickey:start -->"
        + GLOSSARY.split("<!-- concept:doohickey:start -->")[1].split(
            "<!-- concept:widget:start -->"
        )[0],
        "<!-- concept:widget:start -->"
        + GLOSSARY.split("<!-- concept:widget:start -->")[1],
    )
    seed(mini_repo, head + widget_entry.rstrip() + "\n\n" + doohickey_entry)
    code, payload = run(mini_repo, "--check", capsys=capsys)
    assert code == EXIT_FINDINGS
    assert "lift-order" in checks_of(payload)


# -- the real thing ----------------------------------------------------------


def test_the_real_glossary_and_records_agree(capsys):
    """The restamped seed and the 359 records lift-check clean, from git."""
    code = main(["lift", "--check", "--root", str(REPO), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert code == EXIT_CLEAN, payload["findings"]
    assert payload["summary"]["entries"] == 155
    assert payload["summary"]["drift"] == 0


def test_every_real_record_is_surgically_writable():
    """The writer's layout assumptions hold for the whole record set.

    Regions for ``definition`` and ``source`` must be locatable and the span
    list splittable in every record, or the first real edit would meet
    ``lift-unwritable-record`` instead of a mirror.
    """
    from detangle.lift import _regions

    records, findings = load_records(REPO / "concepts", REPO)
    assert findings == []
    for rec in records:
        regions = _regions(rec.text)
        assert "definition" in regions and "source" in regions, rec.rel
        s_start, s_end = regions["source"]
        items = rec.text[s_start:s_end]
        assert len(
            [ln for ln in items.splitlines() if ln.startswith("  - ")]
        ) == len(rec.get_list("source")), rec.rel
