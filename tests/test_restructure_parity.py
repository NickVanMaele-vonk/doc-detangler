"""Criterion 5 inside the command: does every source word survive the run?

The tests build small plans directly rather than through the CLI, because
what is under test is the accounting — which words the plan explains, which
the renderer explains, and which are simply gone. The last test runs the
real `U` plan and asserts the residue is empty, which is the property the
golden was verified on by hand.
"""

from pathlib import Path

from detangle.records.load import Record
from detangle.records.spans import block_hash, normalise, split_blocks
from detangle.restructure.execute import (
    AUTHORED,
    SOURCE,
    Drop,
    Part,
    Render,
    render,
)
from detangle.restructure.parity import check, measure
from detangle.restructure.plan import Plan, Section

SECTION = Section(id="u-00000001", title="1. Everything", kind="content")


def hashes(source: str) -> list[str]:
    return [block_hash(normalise(b)) for b in split_blocks(source)]


def plan_for(source: str, **overrides) -> Plan:
    """Every block assigned to one content section, unless overridden."""
    data = {
        "assignments": [{"block": h, "section": SECTION.id} for h in hashes(source)],
    }
    data.update(overrides)
    return Plan(
        path=Path("plan.yaml"),
        rel="plan.yaml",
        doc="U",
        pinned_blob=None,
        sections=[SECTION],
        **data,
    )


def measured(source: str, **overrides):
    plan = plan_for(source, **overrides)
    rendered = render(plan, [], source)
    return measure(plan, source, rendered), rendered


PROSE = """\
The engine flags a signal when the score is >= 0.85.

It must not downgrade the classification.
"""

TABLE = """\
Step   Dimension
----   ---------
1      Alpha runs first.

Step   Dimension
----   ---------
2      Beta runs second.
"""


def test_plain_prose_survives_whole():
    parity, _ = measured(PROSE)
    assert parity.clean
    assert parity.expected == parity.actual
    assert check(parity, "plan.yaml") == []


def test_a_declared_removal_is_explained_not_missing():
    """The plan decided those words go; the check does not re-litigate it."""
    block = hashes(PROSE)[0]
    parity, _ = measured(
        PROSE, inline_removals=[{"block": block, "remove": "when the score is >= 0.85"}]
    )
    assert parity.clean
    assert parity.removed["score"] == 1
    assert "score" not in parity.actual


def test_a_declared_repair_moves_words_across_both_sides():
    """`Per sistence` → `Persistence`: two words out, one in, both declared."""
    source = "The Per sistence Gate caps the classification.\n"
    parity, _ = measured(
        source,
        repairs=[
            {"block": hashes(source)[0], "from": "Per sistence", "to": "Persistence"}
        ],
    )
    assert parity.clean
    assert parity.removed["sistence"] == 1
    assert parity.added["Persistence"] == 1


def test_a_repeated_table_header_explains_itself():
    parity, rendered = measured(TABLE)
    assert parity.clean
    assert [d.reason for d in rendered.drops] == ["repeated-table-header"]
    assert "Dimension" in parity.dropped


def test_a_header_that_is_not_a_repeat_is_not_explained_away():
    """The dangerous case: text discarded as furniture that says something new."""
    source = TABLE.replace(
        "Step   Dimension\n----   ---------\n2",
        "Gate   Dimension\n----   ---------\n2",
    )
    parity, rendered = measured(source)
    assert [d.reason for d in rendered.drops] == ["dropped-table-header"]
    assert parity.missing["Gate"] == 1
    findings = check(parity, "plan.yaml")
    assert [f.check for f in findings] == ["token-parity"]
    assert "'Gate'" in findings[0].message


def test_noise_is_counted_but_never_expected():
    """A declared drop is the plan's decision — reported, not weighed."""
    block = hashes(PROSE)[1]
    parity, _ = measured(
        PROSE,
        assignments=[{"block": hashes(PROSE)[0], "section": SECTION.id}],
        noise=[{"block": block, "kind": "furniture"}],
    )
    assert parity.clean
    assert parity.noise["downgrade"] == 1
    assert "downgrade" not in parity.expected


def test_authored_parts_are_not_weighed_against_the_source():
    """A definition block copied from a record is not the document's own words."""
    record = Record(
        path=Path("concepts/widget.yaml"),
        rel="concepts/widget.yaml",
        data={
            "id": "widget",
            "term": "widget",
            "definition": "A widget is a device.",
            "aliases": [],
        },
        text="",
    )
    plan = plan_for(PROSE, definitions=[{"record": "widget", "section": SECTION.id}])
    rendered = render(plan, [record], PROSE)
    parity = measure(plan, PROSE, rendered)
    assert parity.clean
    assert "device." not in parity.actual


def test_invented_words_in_source_output_are_flagged():
    """The fabrication direction, forced: a source-tagged part with a new word."""
    plan = plan_for(PROSE)
    rendered = Render(
        parts=[
            Part(
                text="The engine invents a conclusion.",
                origin=SOURCE,
                kind="prose",
            )
        ]
    )
    parity = measure(plan, PROSE, rendered)
    assert parity.extra["invents"] == 1
    messages = [f.message for f in check(parity, "plan.yaml")]
    assert any("not in the source" in m for m in messages)


def test_an_unknown_drop_reason_explains_nothing():
    plan = plan_for(PROSE)
    rendered = render(plan, [], PROSE)
    kept = [p for p in rendered.parts if p.origin == SOURCE][1:]
    dropped = [p for p in rendered.parts if p.origin == SOURCE][0]
    rendered.parts = kept + [p for p in rendered.parts if p.origin == AUTHORED]
    rendered.drops.append(
        Drop(text=dropped.text, reason="because-i-said-so", block="x")
    )
    parity = measure(plan, PROSE, rendered)
    assert parity.missing, "an undeclared reason must not absorb words"


# -- the real run -----------------------------------------------------------


def test_the_real_plan_leaves_no_unexplained_word():
    from detangle.records import load_records
    from detangle.restructure import load_plan

    root = Path(__file__).resolve().parents[1]
    plan, findings = load_plan(root / "eval" / "golden" / "uce.plan.yaml", root)
    assert findings == []
    records, _ = load_records(root / "concepts", root)
    source = (root / "samples" / "blueprint-UCE-shortened.md").read_text(
        encoding="utf-8"
    )
    rendered = render(plan, records, source)
    parity = measure(plan, source, rendered)

    assert dict(parity.missing) == {}
    assert dict(parity.extra) == {}
    assert check(parity, plan.rel) == []
    # Every discarded word is discarded for a reason that shows its evidence.
    assert set(parity.drops_by_reason) == {
        "repeated-table-header",
        "history-table-header",
        "part-row-label",
    }
