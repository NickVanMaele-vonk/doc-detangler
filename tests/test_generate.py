"""`detangle generate` — the glossary view (plan step 3.5).

The cases that matter are the ones the rubric turns on: entries come out in
the graph's order and not the alphabet's, an undefined term is rendered rather
than dropped, the forward reference inside the accepted cycle is marked, and
a hand-edit of the generated file is caught by comparing bytes.

Every clean run still exits 1, because the overview is a marked gap and the
gap raises a finding by design. That is asserted once, in
``test_a_clean_run_reports_only_the_overview_gap``; the other tests read the
JSON payload rather than the exit code.
"""

import json

from conftest import BASE_WAIVER

from detangle.cli import main
from detangle.findings import EXIT_CLEAN, EXIT_FINDINGS, EXIT_USAGE

GLOSSARY = {"placement": "glossary", "used_in": ["U", "S"]}


def run(mini_repo, *extra, capsys=None):
    code = main(["generate", "--root", str(mini_repo.root), "--json", *extra])
    payload = json.loads(capsys.readouterr().out) if capsys else None
    return code, payload


def text(mini_repo):
    return (mini_repo.root / "glossary.md").read_text(encoding="utf-8")


def checks(payload):
    return sorted(f["check"] for f in payload["findings"])


def test_a_clean_run_reports_only_the_overview_gap(mini_repo, capsys):
    mini_repo.write_record(**GLOSSARY)
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_FINDINGS
    assert checks(payload) == ["overview-gap"]
    assert payload["summary"] == {
        "entries": 1,
        "defined": 1,
        "undefined": 0,
        "sources": 1,
        "forward_refs": 0,
        "wrote": "glossary.md",
        "waived": 0,
    }


def test_entries_follow_the_graph_not_the_alphabet(mini_repo, capsys):
    """param-glossary-order is topological: a term precedes its users."""
    mini_repo.write_record(id="alpha", term="alpha", depends_on=["omega"], **GLOSSARY)
    mini_repo.write_record(id="omega", term="omega", **GLOSSARY)
    run(mini_repo, capsys=capsys)
    body = text(mini_repo)
    assert body.index("<!-- concept:omega -->") < body.index("<!-- concept:alpha -->")


def test_a_document_placed_record_is_not_in_the_glossary(mini_repo, capsys):
    """C9: a term used in one document is defined there, not here."""
    mini_repo.write_record(id="local", term="local", placement="UCE", used_in=["U"])
    mini_repo.write_record(id="shared", term="shared", **GLOSSARY)
    _, payload = run(mini_repo, capsys=capsys)
    assert payload["summary"]["entries"] == 1
    assert "concept:local" not in text(mini_repo)


def test_an_undefined_term_gets_an_entry_and_a_note(mini_repo, capsys):
    """Case 1: the placement test runs on usage, not on having a definition."""
    mini_repo.write_record(
        id="gadget", term="gadget", definition=None, flags=["orphan"], **GLOSSARY
    )
    _, payload = run(mini_repo, capsys=capsys)
    assert payload["summary"] == {
        "entries": 1,
        "defined": 0,
        "undefined": 1,
        "sources": 1,
        "forward_refs": 0,
        "wrote": "glossary.md",
        "waived": 0,
    }
    assert "**Not defined in the corpus.**" in text(mini_repo)
    # No per-record finding: the rendered note is the flag (design point 7).
    assert checks(payload) == ["overview-gap"]


def test_aliases_are_recorded_in_the_entry(mini_repo, capsys):
    """Criterion 3: synonyms and acronyms are recorded, keyed on the term."""
    mini_repo.write_record(aliases=["thingummy", "WDG"], **GLOSSARY)
    run(mini_repo, capsys=capsys)
    assert "**Also known as:** thingummy, WDG" in text(mini_repo)


def test_every_entry_carries_its_record_id_as_a_marker(mini_repo, capsys):
    """D9's comment round-trip: the anchor is a marker, never a line offset."""
    mini_repo.write_record(**GLOSSARY)
    run(mini_repo, capsys=capsys)
    body = text(mini_repo)
    assert body.index("<!-- concept:widget -->") < body.index("## widget")


def test_the_accepted_cycle_marks_its_forward_reference(mini_repo, capsys):
    """Criterion 1 clause 2: entry point first, its reference marked."""
    mini_repo.write_record(id="alpha", term="alpha", depends_on=["beta"], **GLOSSARY)
    mini_repo.write_record(id="beta", term="beta", depends_on=["alpha"], **GLOSSARY)
    mini_repo.write_cycles(
        {
            "id": "ab-contrast",
            "members": ["alpha", "beta"],
            "disposition": "accepted-outer-circle",
            "entry_point": "beta",
            "iso_704": "6.5.2",
        }
    )
    _, payload = run(mini_repo, capsys=capsys)
    assert payload["summary"]["forward_refs"] == 1
    body = text(mini_repo)
    assert body.index("<!-- concept:beta -->") < body.index("<!-- concept:alpha -->")
    marker = body.index("<!-- bridging:forward-ref -->")
    assert body.index("<!-- concept:beta -->") < marker < body.index("concept:alpha")
    assert "`ab-contrast`" in body


def test_the_sources_block_binds_each_document_to_a_git_blob(mini_repo, capsys):
    mini_repo.write_record(**GLOSSARY)
    run(mini_repo, capsys=capsys)
    blob = mini_repo.blob("samples/mini.md")
    assert f"| `samples/mini.md` | component | `{blob}` |" in text(mini_repo)


def test_a_reference_source_row_is_labelled_as_such(mini_repo, capsys):
    """Two input sets (2026-08-05): a reader auditing provenance sees that a
    reference document supplied lifted definitions, not detangled content."""
    mini_repo.write_record(
        id="doohickey",
        term="doohickey",
        definition="A doohickey is a reference-defined device",
        flags=["orphan", "A"],
        source=[mini_repo.span("A doohickey", doc="samples/analytical.md")],
        **GLOSSARY,
    )
    run(mini_repo, capsys=capsys)
    blob = mini_repo.blob("samples/analytical.md")
    assert f"| `samples/analytical.md` | reference | `{blob}` |" in text(mini_repo)


def test_two_blobs_for_one_document_are_reported_as_skew(mini_repo, capsys):
    """Version skew is what the source-version binding exists to catch."""
    stale = mini_repo.span("A widget is a device")
    stale["verified_against"]["git_blob"] = "0" * 40
    mini_repo.write_record(**GLOSSARY)
    mini_repo.write_record(id="other", term="other", source=[stale], **GLOSSARY)
    _, payload = run(mini_repo, capsys=capsys)
    assert "sources-blob-skew" in checks(payload)


def test_check_does_not_write(mini_repo, capsys):
    mini_repo.write_record(**GLOSSARY)
    _, payload = run(mini_repo, "--check", capsys=capsys)
    assert checks(payload) == ["glossary-missing", "overview-gap"]
    assert not (mini_repo.root / "glossary.md").exists()
    assert payload["summary"]["checked"] == "glossary.md"


def test_check_is_clean_after_a_generate(mini_repo, capsys):
    mini_repo.write_record(**GLOSSARY)
    run(mini_repo, capsys=capsys)
    _, payload = run(mini_repo, "--check", capsys=capsys)
    assert checks(payload) == ["overview-gap"]


def test_a_hand_edit_of_the_generated_file_is_caught(mini_repo, capsys):
    """ADR-001 Decision 5, applied to the views: bytes, not structure."""
    mini_repo.write_record(**GLOSSARY)
    run(mini_repo, capsys=capsys)
    path = mini_repo.root / "glossary.md"
    path.write_text(text(mini_repo).replace("## widget", "## Widget"), encoding="utf-8")
    _, payload = run(mini_repo, "--check", capsys=capsys)
    assert "glossary-drift" in checks(payload)


def test_a_record_change_without_regenerating_is_caught(mini_repo, capsys):
    mini_repo.write_record(**GLOSSARY)
    run(mini_repo, capsys=capsys)
    mini_repo.write_record(aliases=["WDG"], **GLOSSARY)
    _, payload = run(mini_repo, "--check", capsys=capsys)
    assert "glossary-drift" in checks(payload)


def test_the_render_is_byte_stable(mini_repo, capsys):
    """Deterministic output is what lets --check compare bytes at all."""
    mini_repo.write_record(id="alpha", term="alpha", depends_on=["omega"], **GLOSSARY)
    mini_repo.write_record(id="omega", term="omega", **GLOSSARY)
    run(mini_repo, capsys=capsys)
    first = text(mini_repo)
    # --force because the second run is exactly what the overwrite guard
    # exists to stop; here it is deliberate, which is what the flag says.
    run(mini_repo, "--force", capsys=capsys)
    assert text(mini_repo) == first


def test_a_second_run_refuses_to_overwrite_the_seeded_file(mini_repo, capsys):
    """The file is edited by people (Nick, 2026-08-04) and nothing mirrors it.

    A warning would arrive after the bytes were gone, so the command refuses.
    Exit 2, not 1: no verdict was reached, and nothing was written.
    """
    mini_repo.write_record(**GLOSSARY)
    run(mini_repo, capsys=capsys)
    seeded = text(mini_repo)

    code = main(["generate", "--root", str(mini_repo.root)])
    assert code == EXIT_USAGE
    assert "--force" in capsys.readouterr().err
    assert text(mini_repo) == seeded


def test_force_overwrites_a_file_that_has_been_edited(mini_repo, capsys):
    """The escape hatch is real: a re-seed must stay possible after B-1."""
    mini_repo.write_record(**GLOSSARY)
    run(mini_repo, capsys=capsys)
    (mini_repo.root / "glossary.md").write_text("hand-written\n", encoding="utf-8")

    run(mini_repo, "--force", capsys=capsys)
    assert text(mini_repo) != "hand-written\n"


def test_check_still_reads_an_existing_file(mini_repo, capsys):
    """--check never writes, so the guard must not stand in its way."""
    mini_repo.write_record(**GLOSSARY)
    run(mini_repo, capsys=capsys)

    code, payload = run(mini_repo, "--check", capsys=capsys)
    assert code == EXIT_FINDINGS
    assert checks(payload) == ["overview-gap"]


def test_an_undeclared_output_path_is_a_usage_error(mini_repo, capsys):
    """No hard-coded values: the path comes from detangle.toml or not at all."""
    config = mini_repo.root / "detangle.toml"
    config.write_text(
        config.read_text(encoding="utf-8").replace('glossary = "glossary.md"\n', ""),
        encoding="utf-8",
    )
    mini_repo.write_record(**GLOSSARY)
    code, _ = run(mini_repo)
    assert code == EXIT_USAGE


def test_generate_honours_a_waiver(mini_repo, capsys):
    """A disposition means the same thing whichever command surfaced it.

    Before this, only `validate` read the register, so a finding raised here
    could not be deferred at all.
    """
    mini_repo.write_record(**GLOSSARY)
    mini_repo.write_waivers(
        {
            **BASE_WAIVER,
            "id": "overview-deferred",
            "check": "overview-gap",
            "where": "glossary.md:overview",
        }
    )
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_CLEAN
    assert payload["findings"] == []
    assert len(payload["waived"]) == 1
    assert payload["summary"]["waived"] == 1


def test_generate_does_not_judge_a_validate_only_waiver(mini_repo, capsys):
    """The scoping holds in both directions, not just for `validate`."""
    mini_repo.write_record(**GLOSSARY)
    mini_repo.write_waivers(BASE_WAIVER)  # check: placement-computed
    _, payload = run(mini_repo, capsys=capsys)
    assert checks(payload) == ["overview-gap"]


def test_a_hand_edited_view_cannot_be_waived(mini_repo, capsys):
    """C6 and ADR-001 Decision 5 survive only if drift cannot be excused.

    Regenerating is one command, so there is nothing to defer — which is what
    a waiver is for.
    """
    mini_repo.write_record(**GLOSSARY)
    run(mini_repo, capsys=capsys)
    path = mini_repo.root / "glossary.md"
    path.write_text(text(mini_repo).replace("## widget", "## Widget"), encoding="utf-8")
    mini_repo.write_waivers(
        {
            **BASE_WAIVER,
            "id": "drift-excuse",
            "check": "glossary-drift",
            "where": "glossary.md",
        }
    )
    code, payload = run(mini_repo, "--check", capsys=capsys)
    assert code == EXIT_FINDINGS
    assert "glossary-drift" in checks(payload)
    assert "waiver-not-waivable" in checks(payload)
    assert payload["waived"] == []
