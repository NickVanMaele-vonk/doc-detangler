"""Concept-before-use (ADR-003 Decision 4, build step 2b).

The unit tests fix the two rules Nick ruled on: what counts as a use, and
that the scan runs across the whole reading order rather than per document.
The real-data test at the bottom runs it over the two output documents that
exist — `glossary.md` and the `U` golden — and pins what it finds.
"""

from __future__ import annotations

from pathlib import Path

import networkx as nx

from detangle.graph.build import ConceptGraph
from detangle.records.load import Record
from detangle.registers import CycleEntry, CycleRegister
from detangle.verify.structure import Document, check, scan

ROOT = Path(__file__).resolve().parents[1]


def record(rid: str, term: str, aliases=(), definition="A definition.") -> Record:
    return Record(
        path=Path(f"concepts/{rid}.yaml"),
        rel=f"concepts/{rid}.yaml",
        data={
            "id": rid,
            "term": term,
            "aliases": list(aliases),
            "definition": definition,
        },
        text="",
    )


def graph_of(*records: Record, cycles=(), entries=()) -> ConceptGraph:
    by_id = {r.id: r for r in records}
    g = nx.DiGraph()
    g.add_nodes_from(by_id)
    return ConceptGraph(
        graph=g,
        records=by_id,
        register=CycleRegister(rel="registers/cycles.yaml", entries=list(entries)),
        cycles=[tuple(c) for c in cycles],
    )


def block(*lines: str) -> str:
    return "\n".join(lines)


def doc(*blocks: str, code: str = "U") -> Document:
    return Document(code=code, text="\n\n".join(blocks) + "\n")


# -- what counts as a use ----------------------------------------------------


def test_a_term_used_after_its_definition_is_fine():
    cg = graph_of(record("gate", "structural gate"))
    d = doc(
        block("<!-- concept:gate:start -->", "A structural gate blocks a step.",
              "<!-- concept:gate:end -->"),
        block("Every structural gate is evaluated in order."),
    )
    assert scan([d], cg).forward == []


def test_a_term_used_before_its_definition_is_a_forward_reference():
    cg = graph_of(record("gate", "structural gate"))
    d = doc(
        block("Every structural gate is evaluated in order."),
        block("<!-- concept:gate:start -->", "A structural gate blocks a step.",
              "<!-- concept:gate:end -->"),
    )
    result = scan([d], cg)
    assert [f.concept for f in result.forward] == ["gate"]
    assert result.forward[0].used_at.index == 0
    assert result.forward[0].defined_at.index == 1


def test_a_definition_blocks_own_text_counts_as_a_use():
    """Nick, 2026-08-05 — the miscount that produced the golden's §9 defect."""
    cg = graph_of(record("gate", "structural gate"), record("step", "pipeline step"))
    d = doc(
        block("<!-- concept:gate:start -->",
              "A structural gate ends a pipeline step.",
              "<!-- concept:gate:end -->"),
        block("<!-- concept:step:start -->", "A stage of the run.",
              "<!-- concept:step:end -->"),
    )
    assert [f.concept for f in scan([d], cg).forward] == ["step"]


def test_a_plural_phrase_is_a_use_and_casing_does_not_matter():
    cg = graph_of(record("gate", "structural gate"))
    d = doc(
        block("The Structural Gates are evaluated in order."),
        block("<!-- concept:gate:start -->", "A gate.", "<!-- concept:gate:end -->"),
    )
    assert [f.concept for f in scan([d], cg).forward] == ["gate"]


def test_a_code_is_matched_case_sensitively():
    """Casing is normative for a code (criterion 5), so `sb-01` is not `SB-01`."""
    cg = graph_of(record("sb-01", "SB-01"))
    lower = doc(
        block("The archetype sb-01 is listed."),
        block("<!-- concept:sb-01:start -->", "An archetype.",
              "<!-- concept:sb-01:end -->"),
    )
    assert scan([lower], cg).forward == []


def test_a_code_does_not_match_inside_a_longer_code():
    cg = graph_of(record("mtsam", "MTSAM"))
    d = doc(
        block("Register entry MTSAM-L01 applies."),
        block("<!-- concept:mtsam:start -->", "The venue.",
              "<!-- concept:mtsam:end -->"),
    )
    assert scan([d], cg).forward == []


def test_a_surface_inside_a_longer_matched_surface_is_not_an_independent_use():
    cg = graph_of(record("gate", "gate"), record("arch", "gate architecture"))
    d = doc(
        block("The gate architecture is described here."),
        block("<!-- concept:gate:start -->", "A gate.", "<!-- concept:gate:end -->"),
        block("<!-- concept:arch:start -->", "The whole.", "<!-- concept:arch:end -->"),
    )
    assert [f.concept for f in scan([d], cg).forward] == ["arch"]


# -- furniture ---------------------------------------------------------------


def test_a_heading_is_not_a_use_even_carrying_its_section_marker():
    """The golden's `Human Intervention Checkpoint` heading, exactly."""
    cg = graph_of(record("hcp", "Human Intervention Checkpoint"))
    d = doc(
        block("<!-- sec:u-03d2b71e -->", "## 5. Human intervention checkpoints"),
        block("<!-- concept:hcp:start -->", "A named stop.",
              "<!-- concept:hcp:end -->"),
    )
    assert scan([d], cg).forward == []


def test_a_marker_only_block_is_not_a_use():
    cg = graph_of(record("gate", "gate"))
    d = doc(
        block("<!-- sec:u-1111aaaa -->"),
        block("<!-- concept:gate:start -->", "A gate.", "<!-- concept:gate:end -->"),
    )
    assert scan([d], cg).forward == []


# -- definition sites --------------------------------------------------------


def test_the_glossarys_bare_marker_form_is_a_definition_site():
    cg = graph_of(record("gate", "structural gate"))
    d = doc(
        block("The structural gate is named."),
        block("<!-- concept:gate -->", "## structural gate"),
        block("A structural gate blocks a step."),
        code="glossary",
    )
    result = scan([d], cg)
    assert result.defined_at["gate"].index == 1
    assert [f.concept for f in result.forward] == ["gate"]


def test_an_undefined_records_marker_is_not_a_definition_site():
    """77 of the glossary's 155 entries say "not defined in the corpus"."""
    cg = graph_of(record("gate", "structural gate", definition=None))
    d = doc(
        block("The structural gate is named."),
        block("<!-- concept:gate -->", "## structural gate"),
        code="glossary",
    )
    result = scan([d], cg)
    assert result.defined_at == {}
    assert result.forward == []


def test_a_defined_record_with_no_site_is_reported_as_data_not_a_finding():
    cg = graph_of(record("gate", "structural gate"))
    result = scan([doc(block("Nothing here."))], cg)
    assert result.no_site == ["gate"]
    assert check(result) == []


# -- the reading order -------------------------------------------------------


def test_a_use_in_an_earlier_document_beats_a_definition_in_a_later_one():
    """C9 should make this impossible; the check is what proves it did."""
    cg = graph_of(record("gate", "structural gate"))
    result = scan(
        [
            doc(block("The structural gate is applied."), code="U"),
            doc(block("<!-- concept:gate:start -->", "A gate.",
                      "<!-- concept:gate:end -->"), code="M"),
        ],
        cg,
    )
    assert [(f.used_at.doc, f.defined_at.doc) for f in result.forward] == [("U", "M")]


def test_the_glossary_being_read_first_resolves_a_later_use():
    cg = graph_of(record("gate", "structural gate"))
    result = scan(
        [
            doc(block("<!-- concept:gate -->", "## structural gate"),
                block("A gate."), code="glossary"),
            doc(block("The structural gate is applied."), code="U"),
        ],
        cg,
    )
    assert result.forward == []
    assert result.documents == ["glossary", "U"]


# -- the accepted cycle ------------------------------------------------------


def cycle_graph() -> ConceptGraph:
    return graph_of(
        record("ldr", "liquidity-driven reaction"),
        record("idc", "identity-driven coordination"),
        cycles=[("idc", "ldr")],
        entries=[
            CycleEntry(
                id="contrast",
                members=("ldr", "idc"),
                disposition="accepted-outer-circle",
                entry_point="ldr",
                iso_704="6.5.2",
                rationale="Contrastive pair.",
                authority="Test fixture.",
            )
        ],
    )


def cycle_document() -> Document:
    return doc(
        block("<!-- concept:ldr:start -->",
              "The default, unless testing confirms identity-driven coordination.",
              "<!-- concept:ldr:end -->"),
        block("<!-- concept:idc:start -->", "The contrasting case.",
              "<!-- concept:idc:end -->"),
        code="glossary",
    )


def test_the_accepted_cycles_bridging_reference_is_exempt_not_a_finding():
    """Criterion 1 clause 2: the entry point's forward reference is marked."""
    result = scan([cycle_document()], cycle_graph())
    assert [f.concept for f in result.exempt] == ["idc"]
    assert result.exempt[0].inside == "ldr"
    assert result.forward == []
    assert check(result) == []


def test_the_same_forward_reference_outside_the_cycle_is_still_a_finding():
    cg = cycle_graph()
    d = doc(
        block("Ordinary prose naming identity-driven coordination early."),
        block("<!-- concept:idc:start -->", "The contrasting case.",
              "<!-- concept:idc:end -->"),
        code="glossary",
    )
    result = scan([d], cg)
    assert [f.concept for f in result.forward] == ["idc"]
    assert result.forward[0].inside is None


# -- findings ----------------------------------------------------------------


def test_the_finding_is_an_error_naming_both_positions():
    cg = graph_of(record("gate", "structural gate"))
    d = doc(
        block("The structural gate is applied."),
        block("<!-- concept:gate:start -->", "A gate.", "<!-- concept:gate:end -->"),
    )
    findings = check(scan([d], cg))
    assert [f.severity for f in findings] == ["error"]
    assert findings[0].check == "forward-use"
    assert findings[0].where == "U:block[0]"
    assert "U:block[1]" in findings[0].message


# -- the build-step gate: the documents that exist ---------------------------


def live_graph() -> ConceptGraph:
    from detangle.config import Config
    from detangle.graph.build import build
    from detangle.records.load import load_records
    from detangle.registers import load_cycles

    cfg = Config.load(ROOT)
    records, _ = load_records(cfg.directory("concepts"), ROOT)
    register, _ = load_cycles(cfg.directory("registers"), ROOT)
    cg, _ = build(records, register)
    return cg


def test_the_real_reading_order_holds_except_one_known_collision():
    """`glossary.md` then the `U` golden — the only output documents that exist.

    Two results worth keeping. The accepted cycle's forward reference is
    recognised and exempted, which is criterion 1 clause 2 working. And the
    cross-document result is otherwise empty, which is the evidence that C9
    limb 2 did its job: no definition in `U` is needed before the glossary
    that precedes it.

    A third result used to be pinned here: a sense collision, where the
    banner's phrase "withdrawn as a CI gate" matched the record `gate`, whose
    bare surface is the English word. The 2026-08-08 banner rewrite (for the
    lift) removed the phrase, which resolves that collision without a ruling
    — the forward list is now genuinely empty. If a bare "gate" ever appears
    in prose again the collision returns, and its disposition is still
    Nick's (word-overload ruling, 2026-07-30).
    """
    result = scan(
        [
            Document("glossary", (ROOT / "glossary.md").read_text(encoding="utf-8")),
            Document("U", (ROOT / "eval/golden/uce.md").read_text(encoding="utf-8")),
        ],
        live_graph(),
    )
    assert len(result.defined_at) == 113  # 78 glossary + 35 in the golden
    assert [(f.concept, f.used_at.doc) for f in result.forward] == []
    assert [f.concept for f in result.exempt] == ["identity-driven-coordination"]
    assert result.exempt[0].inside == "liquidity-driven-reaction"
    assert len(result.no_site) == 59  # 172 defined, less the 113 sited
