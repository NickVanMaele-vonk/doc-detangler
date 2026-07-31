"""The record-set integrity checks, one rule at a time."""

from pathlib import Path

from conftest import BASE_RECORD

from detangle.records.checks import (
    check_cross_record,
    check_invariants,
    check_schema,
)
from detangle.records.load import Record

COMPONENTS = {"samples/mini.md", "samples/other.md", "samples/third.md"}


def make(**overrides) -> Record:
    data = dict(BASE_RECORD)
    data.update(overrides)
    rid = data.get("id") or "widget"
    return Record(
        path=Path(f"concepts/{rid}.yaml"),
        rel=f"concepts/{rid}.yaml",
        data=data,
        text=str(data),
    )


def checks(findings) -> list[str]:
    return sorted(f.check for f in findings)


# --- schema ---------------------------------------------------------------


def test_a_well_formed_record_passes_schema():
    rec = make(source=[_span()])
    assert check_schema(rec) == []


def test_missing_key_is_reported():
    data = dict(BASE_RECORD)
    del data["review"]
    rec = Record(Path("concepts/widget.yaml"), "concepts/widget.yaml", data, "")
    assert "schema-missing-key" in checks(check_schema(rec))


def test_unknown_key_is_reported():
    assert "schema-unknown-key" in checks(check_schema(make(colour="blue")))


def test_id_must_equal_the_filename():
    rec = make(id="widget")
    rec.data["id"] = "gadget"
    assert "id-filename" in checks(check_schema(rec))


def test_A_and_P_are_not_used_in_values():
    """(A) and (P) never count toward placement, so they never appear here."""
    assert "used-in-value" in checks(check_schema(make(used_in=["U", "A"])))


def test_span_missing_verified_against_is_reported():
    bad = {"doc": "samples/mini.md", "section": "x", "para_hash": "sha256:0"}
    assert "span-shape" in checks(check_schema(make(source=[bad])))


# --- invariants -----------------------------------------------------------


def test_placement_is_computed_from_used_in():
    assert check_invariants(make(used_in=["U"], placement="UCE"), COMPONENTS) == []
    assert check_invariants(
        make(used_in=["U", "M"], placement="glossary"), COMPONENTS
    ) == []


def test_placement_disagreeing_with_used_in_is_reported():
    findings = check_invariants(make(used_in=["M"], placement="glossary"), COMPONENTS)
    assert checks(findings) == ["placement-computed"]
    assert "computes to 'MCL'" in findings[0].message


def test_two_documents_place_a_term_in_the_glossary():
    findings = check_invariants(make(used_in=["U", "S"], placement="UCE"), COMPONENTS)
    assert checks(findings) == ["placement-computed"]


def test_an_undefined_record_cannot_carry_edges():
    rec = make(definition=None, depends_on=["gadget"], flags=["orphan"])
    assert "edges-on-undefined" in checks(check_invariants(rec, COMPONENTS))


def test_orphan_defined_only_in_the_analytical_layer_is_legitimate():
    """The mts-spa case: a set-level orphan, defined where C9 does not count."""
    rec = make(flags=["orphan", "A"], source=[_span(doc="samples/analytical.md")])
    assert check_invariants(rec, COMPONENTS) == []


def test_orphan_defined_in_a_component_blueprint_is_a_contradiction():
    rec = make(flags=["orphan"], source=[_span()])
    assert "orphan-flag" in checks(check_invariants(rec, COMPONENTS))


def test_conflict_and_its_flag_must_agree():
    assert "conflict-flag" in checks(
        check_invariants(make(conflict={"summary": "x", "spans": [1, 2]}), COMPONENTS)
    )
    assert "conflict-flag" in checks(
        check_invariants(make(flags=["conflict"]), COMPONENTS)
    )


def test_a_conflict_needs_both_sides():
    rec = make(flags=["conflict"], conflict={"summary": "x", "spans": [{}]})
    assert "conflict-shape" in checks(check_invariants(rec, COMPONENTS))


# --- cross-record ---------------------------------------------------------


def test_a_surface_claimed_by_two_records_is_a_second_definition_site():
    findings = check_cross_record(
        [make(id="widget", term="Widget"), make(id="gadget", term="gadget",
                                                aliases=["widget"])]
    )
    assert checks(findings) == ["one-definition-site"]


def test_an_alias_that_only_recases_its_own_term_is_not_a_collision():
    """`evidence hierarchy` / `Evidence Hierarchy` — both are source surfaces."""
    rec = make(id="widget", term="evidence hierarchy", aliases=["Evidence Hierarchy"])
    assert check_cross_record([rec]) == []


def test_edge_targets_must_exist():
    findings = check_cross_record([make(depends_on=["nonexistent"])])
    assert checks(findings) == ["edge-target"]


def test_links_must_resolve():
    rec = make()
    rec.text = "notes: see [[gadget]] and [[widget]]"
    findings = check_cross_record([rec])
    assert [f.check for f in findings] == ["dangling-link"]
    assert "[[gadget]]" in findings[0].message


def test_superseded_by_must_resolve():
    assert checks(check_cross_record([make(superseded_by="ghost")])) == [
        "superseded-target"
    ]


def _span(doc: str = "samples/mini.md") -> dict:
    return {
        "doc": doc,
        "section": "1.1 The Only Section",
        "para_hash": "sha256:" + "0" * 64,
        "verified_against": {"git_blob": "0" * 40, "stated_version": None},
    }
