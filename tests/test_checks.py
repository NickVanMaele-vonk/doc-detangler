"""The record-set integrity checks, one rule at a time."""

from pathlib import Path

from conftest import BASE_RECORD

from detangle.config import DocumentRegistry
from detangle.records.checks import (
    check_assurance,
    check_cross_record,
    check_invariants,
    check_placement,
    check_schema,
    check_span_docs,
)
from detangle.records.load import Record

#: The fixture's two input sets (Nick, 2026-08-05): three component
#: blueprints and one read-only reference document, mirroring conftest CONFIG.
REGISTRY = DocumentRegistry(
    components=("U", "S", "M"),
    references=("A",),
    paths={
        "U": "samples/mini.md",
        "S": "samples/other.md",
        "M": "samples/third.md",
        "A": "samples/analytical.md",
    },
    placements={"U": "UCE", "S": "SBSP", "M": "MCL"},
)


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
    assert check_schema(rec, REGISTRY) == []


def test_missing_key_is_reported():
    data = dict(BASE_RECORD)
    del data["review"]
    rec = Record(Path("concepts/widget.yaml"), "concepts/widget.yaml", data, "")
    assert "schema-missing-key" in checks(check_schema(rec, REGISTRY))


def test_unknown_key_is_reported():
    assert "schema-unknown-key" in checks(check_schema(make(colour="blue"), REGISTRY))


def test_id_must_equal_the_filename():
    rec = make(id="widget")
    rec.data["id"] = "gadget"
    assert "id-filename" in checks(check_schema(rec, REGISTRY))


def test_reference_codes_are_not_used_in_values():
    """Reference documents never count toward placement, so never appear here."""
    findings = check_schema(make(used_in=["U", "A"]), REGISTRY)
    assert "used-in-value" in checks(findings)


def test_a_reference_code_is_a_legal_flag():
    """The registry's reference codes double as informational record flags."""
    assert check_schema(make(flags=["orphan", "A"], source=[_span()]), REGISTRY) == []


def test_an_undeclared_flag_is_reported():
    """`P` is a real code in the live repo but not in this fixture's registry —
    flags follow the config, not a hard-coded list."""
    assert "flag-value" in checks(check_schema(make(flags=["P"]), REGISTRY))


def test_span_missing_verified_against_is_reported():
    bad = {"doc": "samples/mini.md", "section": "x", "para_hash": "sha256:0"}
    assert "span-shape" in checks(check_schema(make(source=[bad]), REGISTRY))


# --- span registration (two input sets, 2026-08-05) ------------------------


def test_a_span_may_cite_either_input_set():
    rec = make(source=[_span(), _span(doc="samples/analytical.md")])
    assert check_span_docs(rec, REGISTRY) == []


def test_a_span_citing_an_unregistered_document_is_reported():
    findings = check_span_docs(make(source=[_span(doc="notes/scratch.md")]), REGISTRY)
    assert checks(findings) == ["span-doc-unknown"]
    assert "notes/scratch.md" in findings[0].message


def test_a_conflict_span_is_held_to_the_same_registry():
    conflict = {
        "summary": "x",
        "spans": [_span(), {**_span(), "doc": "samples/rogue.md"}],
    }
    findings = check_span_docs(make(flags=["conflict"], conflict=conflict), REGISTRY)
    assert checks(findings) == ["span-doc-unknown"]
    assert findings[0].where.endswith("conflict.spans[1]")


# --- placement (C9, both limbs) -------------------------------------------


def test_placement_is_computed_from_used_in():
    assert check_placement([make(used_in=["U"], placement="UCE")], REGISTRY) == []
    assert (
        check_placement([make(used_in=["U", "M"], placement="glossary")], REGISTRY)
        == []
    )


def test_placement_disagreeing_with_used_in_is_reported():
    findings = check_placement([make(used_in=["M"], placement="glossary")], REGISTRY)
    assert checks(findings) == ["placement-computed"]
    assert "computes to 'MCL'" in findings[0].message


def test_two_documents_place_a_term_in_the_glossary():
    findings = check_placement([make(used_in=["U", "S"], placement="UCE")], REGISTRY)
    assert checks(findings) == ["placement-computed"]


def test_an_empty_used_in_cannot_be_computed():
    findings = check_placement([make(used_in=[], placement="UCE")], REGISTRY)
    assert checks(findings) == ["placement-computed"]
    assert "used_in is empty" in findings[0].message


def test_a_glossary_definitions_dependency_joins_the_glossary():
    """Limb 2 (Nick, 2026-08-03): the glossary is read first, so a term it
    leans on has nowhere else to be looked up."""
    shared = make(id="shared", used_in=["U", "S"], placement="glossary",
                  depends_on=["local"])
    local = make(id="local", used_in=["U"], placement="glossary")
    assert check_placement([shared, local], REGISTRY) == []


def test_a_dependency_left_in_its_document_is_reported():
    shared = make(id="shared", used_in=["U", "S"], placement="glossary",
                  depends_on=["local"])
    local = make(id="local", used_in=["U"], placement="UCE")
    findings = check_placement([shared, local], REGISTRY)
    assert checks(findings) == ["placement-computed"]
    assert findings[0].where == "concepts/local.yaml:placement"
    assert "a glossary definition depends on it" in findings[0].message


def test_the_closure_is_transitive():
    shared = make(id="shared", used_in=["U", "S"], placement="glossary",
                  depends_on=["mid"])
    mid = make(id="mid", used_in=["U"], placement="glossary", depends_on=["deep"])
    deep = make(id="deep", used_in=["U"], placement="UCE")
    findings = check_placement([shared, mid, deep], REGISTRY)
    assert [f.where for f in findings] == ["concepts/deep.yaml:placement"]


def test_a_document_local_dependency_chain_stays_in_its_document():
    """Limb 2 fires only from the glossary. A document term's own
    dependencies have no reason to move."""
    local = make(id="local", used_in=["U"], placement="UCE", depends_on=["deeper"])
    deeper = make(id="deeper", used_in=["U"], placement="UCE")
    assert check_placement([local, deeper], REGISTRY) == []


def test_a_wrongly_glossary_marked_record_does_not_drag_its_tree_in():
    """The closure is seeded from `used_in`, never from the field it checks —
    otherwise one bad placement would justify itself."""
    wrong = make(id="wrong", used_in=["U"], placement="glossary", depends_on=["dep"])
    dep = make(id="dep", used_in=["U"], placement="UCE")
    findings = check_placement([wrong, dep], REGISTRY)
    assert [f.where for f in findings] == ["concepts/wrong.yaml:placement"]


# --- invariants -----------------------------------------------------------


def test_an_undefined_record_cannot_carry_edges():
    rec = make(definition=None, depends_on=["gadget"], flags=["orphan"])
    assert "edges-on-undefined" in checks(check_invariants(rec, REGISTRY))


def test_orphan_defined_only_in_a_reference_document_is_legitimate():
    """The mts-spa case, now the rule (2026-08-05): a definition lifted from
    the reference set leaves the record a set-level orphan."""
    rec = make(flags=["orphan", "A"], source=[_span(doc="samples/analytical.md")])
    assert check_invariants(rec, REGISTRY) == []


def test_orphan_defined_in_a_component_blueprint_is_a_contradiction():
    rec = make(flags=["orphan"], source=[_span()])
    assert "orphan-flag" in checks(check_invariants(rec, REGISTRY))


def test_conflict_and_its_flag_must_agree():
    assert "conflict-flag" in checks(
        check_invariants(make(conflict={"summary": "x", "spans": [1, 2]}), REGISTRY)
    )
    assert "conflict-flag" in checks(
        check_invariants(make(flags=["conflict"]), REGISTRY)
    )


def test_a_conflict_needs_both_sides():
    rec = make(flags=["conflict"], conflict={"summary": "x", "spans": [{}]})
    assert "conflict-shape" in checks(check_invariants(rec, REGISTRY))


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


def _span(doc: str = "samples/mini.md", origin: str = "corpus") -> dict:
    return {
        "doc": doc,
        "section": "1.1 The Only Section",
        "para_hash": "sha256:" + "0" * 64,
        "origin": origin,
        "verified_against": {"git_blob": "0" * 40, "stated_version": None},
    }


# --- lineage and assurance (ADR-004 Decisions 1, 2, 2b) --------------------

ASSURED = {"author": "assistant", "approved_by": None, "pr": None}


def test_a_defined_record_with_an_assurance_block_passes():
    assert check_assurance(make(assurance=dict(ASSURED))) == []


def test_a_defined_record_without_assurance_is_reported():
    """Under Decision 1 assurance carries the strength, so it cannot be absent."""
    assert checks(check_assurance(make(assurance=None))) == ["assurance-shape"]


def test_an_undefined_record_has_nothing_to_vouch_for():
    assert check_assurance(make(definition=None, assurance=None)) == []


def test_an_undefined_record_may_not_claim_an_approver():
    """An orphan with an approver would read as a definition nobody can see."""
    rec = make(definition=None, assurance={**ASSURED, "approved_by": "Nick"})
    assert checks(check_assurance(rec)) == ["assurance-shape"]


def test_an_unknown_assurance_key_is_reported():
    """A misspelt key would leave a check silently finding no approver."""
    rec = make(assurance={**ASSURED, "approver": "Nick"})
    assert checks(check_assurance(rec)) == ["assurance-shape"]


def test_a_missing_assurance_key_is_reported():
    assert checks(check_assurance(make(assurance={"author": "Nick"}))) == [
        "assurance-shape",
        "assurance-shape",
    ]


def test_an_author_must_be_a_name():
    assert checks(check_assurance(make(assurance={**ASSURED, "author": ""}))) == [
        "assurance-shape"
    ]


def test_a_pr_without_an_approver_is_reported():
    """A PR number is where an approval happened, not the approval itself."""
    rec = make(assurance={**ASSURED, "pr": 120})
    assert checks(check_assurance(rec)) == ["assurance-shape"]


def test_a_signed_off_status_needs_a_named_approver():
    rec = make(status="approved", assurance=dict(ASSURED))
    assert checks(check_assurance(rec)) == ["assurance-unapproved"]


def test_a_signed_off_status_with_an_approver_passes():
    rec = make(
        status="published",
        assurance={"author": "assistant", "approved_by": "Nick", "pr": 120},
    )
    assert check_assurance(rec) == []


def test_a_candidate_may_sit_unapproved():
    """Every record on `main` today is candidate; the gate must not fire."""
    assert check_assurance(make(status="candidate", assurance=dict(ASSURED))) == []


def test_a_span_must_declare_its_origin():
    span = _span()
    del span["origin"]
    assert "span-shape" in checks(check_schema(make(source=[span]), REGISTRY))


def test_an_unknown_span_origin_is_reported():
    rec = make(source=[_span(origin="invented")])
    assert "span-origin" in checks(check_schema(rec, REGISTRY))


def test_an_authored_span_is_legal():
    """The point of Decision 2: text that entered later gets a real span.

    Before the split, the absence of a hash carried both "not in the original"
    and "not trustworthy". Lineage now says the first and assurance the
    second, so an authored span is honest data rather than a violation.
    """
    assert check_schema(make(source=[_span(origin="authored")]), REGISTRY) == []
