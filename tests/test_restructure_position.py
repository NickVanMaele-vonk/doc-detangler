"""ADR-004 Decision 8: a block moved by hand is reported, never silently undone.

The failure this guards is the silent one — a re-run putting a hand-moved
definition back with no error, no finding and nothing in the report. So the
tests are built around structured input (a document carrying `sec:` markers,
which is what a previous run emits) and check three things: that an agreeing
document is silent, that a disagreeing one raises exactly one warning per
block carrying a paste-ready plan line, and that unstructured input — run 1,
where the plan reorders nearly everything by design — stays silent.
"""

from pathlib import Path

from detangle.records.spans import block_hash, normalise, split_blocks
from detangle.restructure.plan import Plan, Section
from detangle.restructure.position import (
    check,
    cluster_body,
    current_sections,
    is_structured,
    measure,
)

HEAD = Section(id="head", title="Document identity", kind="head")
ONE = Section(id="u-1111aaaa", title="1. First", kind="content")
TWO = Section(id="u-2222bbbb", title="2. Second", kind="content")

#: What a run emits: an unmarked head, then one `sec:` marker per section.
STRUCTURED = """\
MTSAM Blueprint

<!-- sec:u-1111aaaa -->
## 1. First

The engine flags a signal when the score is >= 0.85.

<!-- sec:u-2222bbbb -->
## 2. Second

It must not downgrade the classification.
"""

#: The same words with no markers — raw corpus, the input to run 1.
UNSTRUCTURED = """\
MTSAM Blueprint

The engine flags a signal when the score is >= 0.85.

It must not downgrade the classification.
"""

FIRST = "The engine flags a signal"
SECOND = "It must not downgrade"


def digest_of(source: str, needle: str) -> str:
    for block in split_blocks(source):
        if needle in block:
            return block_hash(normalise(block))
    raise AssertionError(f"no block contains {needle!r}")


def plan_with(assignments: list[dict], sections=(HEAD, ONE, TWO)) -> Plan:
    return Plan(
        path=Path("uce.plan.yaml"),
        rel="uce.plan.yaml",
        doc="U",
        pinned_blob=None,
        sections=list(sections),
        assignments=assignments,
    )


def agreeing_plan(source: str = STRUCTURED) -> Plan:
    """A plan that puts every block exactly where the document already has it."""
    return plan_with(
        [
            {"block": digest_of(source, "MTSAM Blueprint"), "section": HEAD.id},
            {"block": digest_of(source, FIRST), "section": ONE.id},
            {"block": digest_of(source, SECOND), "section": TWO.id},
        ]
    )


# -- the quiet cases ---------------------------------------------------------


def test_a_document_that_agrees_with_its_plan_is_silent():
    assert measure(agreeing_plan(), STRUCTURED) == []


def test_unstructured_input_is_silent_even_when_it_disagrees():
    """Run 1 reorders nearly every block, so disagreement means nothing there."""
    plan = plan_with(
        [
            {"block": digest_of(UNSTRUCTURED, "MTSAM Blueprint"), "section": HEAD.id},
            {"block": digest_of(UNSTRUCTURED, FIRST), "section": TWO.id},
            {"block": digest_of(UNSTRUCTURED, SECOND), "section": ONE.id},
        ]
    )
    assert not is_structured(UNSTRUCTURED)
    assert measure(plan, UNSTRUCTURED) == []


def test_a_block_the_plan_never_assigns_raises_nothing():
    """Declared noise has no assignment, so it cannot contradict one."""
    plan = plan_with(
        [{"block": digest_of(STRUCTURED, FIRST), "section": ONE.id}],
    )
    assert measure(plan, STRUCTURED) == []


# -- the case the decision exists for ---------------------------------------


def test_a_hand_moved_block_is_reported_once():
    """The document has moved `SECOND` under section 1; the plan still says 2."""
    drifts = measure(agreeing_plan(), _move_second_into_one())
    assert len(drifts) == 1
    assert drifts[0].planned == TWO.id
    assert drifts[0].current == ONE.id


def test_the_finding_is_a_warning_and_never_blocks():
    moved = _move_second_into_one()
    findings = check(measure(agreeing_plan(), moved), "uce.plan.yaml")
    assert [f.severity for f in findings] == ["warn"]
    assert findings[0].check == "plan-position-conflict"


def test_the_finding_carries_a_paste_ready_plan_line():
    moved = _move_second_into_one()
    drifts = measure(agreeing_plan(), moved)
    message = check(drifts, "uce.plan.yaml")[0].message
    assert f"section: {ONE.id}" in message
    assert f"was {TWO.id}" in message
    assert drifts[0].block[:19] in message


def test_the_finding_points_at_the_assignment_to_edit():
    moved = _move_second_into_one()
    findings = check(measure(agreeing_plan(), moved), "uce.plan.yaml")
    # `SECOND` is the third assignment in `agreeing_plan`.
    assert findings[0].where == "uce.plan.yaml:assignments[2]"


def test_the_cluster_body_gathers_every_line_into_one_patch():
    moved = _move_second_into_one()
    body = cluster_body(measure(agreeing_plan(), moved))
    assert "```yaml" in body
    assert f"section: {ONE.id}" in body


# -- attribution edge cases --------------------------------------------------


def test_blocks_before_the_first_marker_belong_to_the_head_section():
    where, _ = current_sections(agreeing_plan(), STRUCTURED)
    assert where[digest_of(STRUCTURED, "MTSAM Blueprint")] == {HEAD.id}


def test_a_section_heading_block_is_scaffolding_not_an_assignable_block():
    where, _ = current_sections(agreeing_plan(), STRUCTURED)
    heading = block_hash(normalise("<!-- sec:u-1111aaaa -->\n## 1. First"))
    assert heading not in where
    assert len(where) == 3  # head + two prose blocks, no headings


def test_a_repeated_block_is_not_drifted_while_one_copy_sits_right():
    """Identical blocks exist (the bare-rule blocks); one right copy is enough."""
    repeated = STRUCTURED.replace(
        "It must not downgrade the classification.\n",
        "It must not downgrade the classification.\n"
        "\nThe engine flags a signal when the score is >= 0.85.\n",
    )
    where, _ = current_sections(agreeing_plan(), repeated)
    assert where[digest_of(repeated, FIRST)] == {ONE.id, TWO.id}
    assert measure(agreeing_plan(), repeated) == []


# -- end to end, through the command ----------------------------------------

#: A re-run's input: the previous run's output, markers and all. The tool
#: re-emits its own scaffolding, so the old heading blocks are declared noise
#: — which is what a re-run's plan has to say about them.
RERUN_INPUT = """\
# Mini corpus

<!-- sec:u-1111aaaa -->
## 1. First

A widget is a device that emits SB-01 alerts when the score is >= 0.85.

<!-- sec:u-2222bbbb -->
## 2. Second

A gadget is used here but never defined anywhere in this corpus.
"""

#: The same document with the widget paragraph moved into section 2 by hand.
HAND_MOVED = """\
# Mini corpus

<!-- sec:u-1111aaaa -->
## 1. First

Placeholder prose so the section is not empty.

<!-- sec:u-2222bbbb -->
## 2. Second

A widget is a device that emits SB-01 alerts when the score is >= 0.85.
"""


def _write_rerun(mini_repo, source: str) -> None:
    """Structured input plus a plan that keeps each block where it began."""
    from detangle.records.spans import block_hash, normalise, split_blocks

    doc = mini_repo.root / "samples" / "mini.md"
    doc.write_text(source, encoding="utf-8")
    assigned, noise = [], []
    section = "head"
    for raw in split_blocks(source):
        digest = block_hash(normalise(raw))
        if raw.lstrip().startswith("<!-- sec:"):
            section = raw.split("sec:", 1)[1].split(" ", 1)[0]
            noise.append(f"  - {{block: {digest}, kind: navigation}}")
            continue
        assigned.append(f"  - {{block: {digest}, section: {section}}}")
    (mini_repo.root / "samples" / "mini.plan.yaml").write_text(
        "doc: U\n"
        "sections:\n"
        '  - {id: head, title: "", kind: head}\n'
        '  - {id: u-1111aaaa, title: "1. First", kind: content}\n'
        '  - {id: u-2222bbbb, title: "2. Second", kind: content}\n'
        "assignments:\n" + "\n".join(assigned) + "\n"
        "noise:\n" + "\n".join(noise) + "\n",
        encoding="utf-8",
    )


def _run(mini_repo, capsys, report=None):
    import json

    from detangle.cli import main

    args = [
        "restructure",
        "--root",
        str(mini_repo.root),
        "--plan",
        str(mini_repo.root / "samples" / "mini.plan.yaml"),
        "--out",
        str(mini_repo.root / "restructured.md"),
        "--json",
    ]
    if report is not None:
        args += ["--report", str(report)]
    code = main(args)
    return code, json.loads(capsys.readouterr().out)


def test_a_rerun_over_an_unmoved_document_raises_nothing(mini_repo, capsys):
    mini_repo.write_record()
    _write_rerun(mini_repo, RERUN_INPUT)
    code, payload = _run(mini_repo, capsys)
    assert [f["check"] for f in payload["findings"]] == []
    assert code == 0


def test_the_command_reports_a_hand_moved_block_without_blocking(mini_repo, capsys):
    """The plan of the unmoved document, run against the moved one."""
    mini_repo.write_record()
    _write_rerun(mini_repo, RERUN_INPUT)
    plan_text = (mini_repo.root / "samples" / "mini.plan.yaml").read_text()
    (mini_repo.root / "samples" / "mini.md").write_text(HAND_MOVED, encoding="utf-8")

    # The moved document has one block the old plan never saw, so re-point the
    # plan at it as noise; every other assignment stands, which is the point.
    from detangle.records.spans import block_hash, normalise, split_blocks

    for raw in split_blocks(HAND_MOVED):
        if "Placeholder" in raw:
            fresh = block_hash(normalise(raw))
            plan_text += f"  - {{block: {fresh}, kind: navigation}}\n"
    for raw in split_blocks(RERUN_INPUT):
        if "gadget" in raw:
            stale = block_hash(normalise(raw))
            plan_text = plan_text.replace(
                f"  - {{block: {stale}, section: u-2222bbbb}}\n", ""
            )
    (mini_repo.root / "samples" / "mini.plan.yaml").write_text(plan_text)

    report = mini_repo.root / "report"
    code, payload = _run(mini_repo, capsys, report=report)
    found = [f for f in payload["findings"] if f["check"] == "plan-position-conflict"]
    assert len(found) == 1, payload["findings"]
    assert found[0]["severity"] == "warn"
    assert "u-2222bbbb" in found[0]["message"]  # where it sits now
    assert code == 1  # reported, and the document is still written
    assert (mini_repo.root / "restructured.md").is_file()

    body = (report / "exceptions.md").read_text(encoding="utf-8")
    assert "moved by hand" in body


def _move_second_into_one() -> str:
    """`SECOND` relocated under section 1, as a hand edit would leave it."""
    return """\
MTSAM Blueprint

<!-- sec:u-1111aaaa -->
## 1. First

The engine flags a signal when the score is >= 0.85.

It must not downgrade the classification.

<!-- sec:u-2222bbbb -->
## 2. Second

Placeholder prose so the section is not empty.
"""
