"""The generated 8f self-report, and the 8c comment budget that gates it.

Two properties carry the design. The tool writes what it measured and never
writes a ruling: a declared cluster appears as a title and a pointer, and the
reasoning it points at is not reproduced. And the budget counts every
cluster, measured or declared — a comment the tool cannot see is one it would
count wrong, which is the whole reason the plan carries the declarations.
"""

import json
from pathlib import Path

import yaml
from conftest import BASE_RECORD, BASE_WAIVER  # noqa: F401 (fixture parity)

from detangle import registers
from detangle.cli import main
from detangle.findings import EXIT_CLEAN, EXIT_FINDINGS
from detangle.restructure.report import ARTIFACTS, COUNTS, EXCEPTIONS, MOVE_MAP

SEC = "u-00000001"


def write_plan(
    mini_repo, *, extra: str = "", definitions: str = "", head: bool = False
) -> Path:
    from detangle.records.spans import block_hash, normalise, split_blocks

    text = (mini_repo.root / "samples" / "mini.md").read_text(encoding="utf-8")
    hashes = [block_hash(normalise(b)) for b in split_blocks(text)]
    assigned = "\n".join(f"  - {{block: {h}, section: {SEC}}}" for h in hashes)
    plan = (
        "doc: U\n"
        "sections:\n"
        + ('  - {id: head, title: "", kind: head}\n' if head else "")
        + f"  - {{id: {SEC}, title: \"1. Everything\", kind: content}}\n"
        f"assignments:\n{assigned}\n"
        "definitions:\n"
        f"  - {{record: widget, section: {SEC}}}\n"
        f"{definitions}"
        f"{extra}"
    )
    path = mini_repo.root / "samples" / "mini.plan.yaml"
    path.write_text(plan, encoding="utf-8")
    return path


def write_undefined(mini_repo, rid: str, flags: list[str]) -> None:
    """A record with no definition — an orphan, or undefined by ruling."""
    data = dict(BASE_RECORD)
    data.update(
        id=rid, term=rid, definition=None, source=[], depends_on=[], flags=flags
    )
    (mini_repo.root / "concepts" / f"{rid}.yaml").write_text(
        yaml.safe_dump(data, sort_keys=False), encoding="utf-8"
    )


def run(mini_repo, *extra, report: Path | None = None, capsys=None):
    args = [
        "restructure",
        "--root",
        str(mini_repo.root),
        "--plan",
        str(mini_repo.root / "samples" / "mini.plan.yaml"),
        "--out",
        str(mini_repo.root / "restructured.md"),
        "--json",
        *extra,
    ]
    if report is not None:
        args += ["--report", str(report)]
    code = main(args)
    payload = json.loads(capsys.readouterr().out) if capsys else None
    return code, payload


def checks(payload) -> list[str]:
    return [f["check"] for f in payload["findings"]]


# -- writing the artifacts --------------------------------------------------


def test_no_report_directory_means_no_report(mini_repo, capsys):
    """The flag is opt-in; a plain run still writes only the document."""
    mini_repo.write_record()
    write_plan(mini_repo)
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_CLEAN
    assert (mini_repo.root / "restructured.md").is_file()
    assert list(mini_repo.root.rglob(MOVE_MAP)) == []
    # The budget still ran, because clusters exist whether or not files do.
    assert payload["summary"]["comments"] == "3/25"


def test_the_three_artifacts_are_written_and_name_themselves(mini_repo, capsys):
    mini_repo.write_record()
    write_plan(mini_repo)
    out = mini_repo.root / "report"
    code, _ = run(mini_repo, report=out, capsys=capsys)
    assert code == EXIT_CLEAN
    assert sorted(p.name for p in out.iterdir()) == sorted(ARTIFACTS)
    assert "generated" in (out / MOVE_MAP).read_text(encoding="utf-8")
    assert "do not hand-edit" in (out / COUNTS).read_text(encoding="utf-8")


def test_the_move_map_accounts_for_every_block_and_drop(mini_repo, capsys):
    mini_repo.write_record()
    write_plan(mini_repo)
    out = mini_repo.root / "report"
    run(mini_repo, report=out, capsys=capsys)
    move_map = (out / MOVE_MAP).read_text(encoding="utf-8")
    assert "A widget is a device" in move_map
    assert "1. Everything" in move_map  # the target section, by title
    assert "## Section IDs" in move_map and SEC in move_map


def test_the_headless_identity_block_is_not_a_counted_section(mini_repo, capsys):
    """Sections are counted as a reader meets them (Nick, 2026-08-05).

    A ``head`` section renders with no heading and no ``sec:`` marker, so it
    is not one of the sections the count is about — but it is not hidden
    either: the move-map's Section IDs table lists every plan section.
    """
    mini_repo.write_record()
    write_plan(mini_repo, head=True)
    out = mini_repo.root / "report"
    _, payload = run(mini_repo, report=out, capsys=capsys)
    # Two plan sections, one of them headless.
    assert payload["summary"]["sections"] == 1
    counts = (out / COUNTS).read_text(encoding="utf-8")
    assert "| Sections | 1 |" in counts
    assert "head" in (out / MOVE_MAP).read_text(encoding="utf-8")


def test_the_counts_carry_the_criterion_5_accounting(mini_repo, capsys):
    mini_repo.write_record()
    write_plan(mini_repo)
    out = mini_repo.root / "report"
    run(mini_repo, report=out, capsys=capsys)
    counts = (out / COUNTS).read_text(encoding="utf-8")
    assert "Missing — in no output section** | **0**" in counts
    assert "No unclassified difference in either direction." in counts


# -- the guard --------------------------------------------------------------


def test_check_catches_a_hand_edited_report(mini_repo, capsys):
    mini_repo.write_record()
    write_plan(mini_repo)
    out = mini_repo.root / "report"
    run(mini_repo, report=out, capsys=capsys)
    (out / EXCEPTIONS).write_text("hand-written\n", encoding="utf-8")
    code, payload = run(mini_repo, "--check", report=out, capsys=capsys)
    assert code == EXIT_FINDINGS
    assert checks(payload) == ["report-drift"]


def test_check_reports_a_report_that_was_never_committed(mini_repo, capsys):
    mini_repo.write_record()
    write_plan(mini_repo)
    run(mini_repo, capsys=capsys)  # writes the document, not the report
    code, payload = run(
        mini_repo, "--check", report=mini_repo.root / "report", capsys=capsys
    )
    assert code == EXIT_FINDINGS
    assert checks(payload) == ["report-missing"] * len(ARTIFACTS)


def test_a_hand_edited_report_cannot_be_waived():
    """Same rule as every other derived artifact: regenerating it is one
    command, so there is nothing to defer (C6, ADR-001 D5)."""
    assert not registers.is_waivable("report-drift")
    assert not registers.is_waivable("report-missing")
    assert registers.is_waivable("comment-budget")


# -- measured clusters ------------------------------------------------------


def test_undefined_terms_are_split_by_why_they_are_undefined(mini_repo, capsys):
    """An orphan measures a convoluted source; the IBE/IBEB shape does not."""
    mini_repo.write_record()
    write_undefined(mini_repo, "gadget", ["orphan"])
    write_undefined(mini_repo, "sprocketengine", [])
    write_plan(mini_repo)
    out = mini_repo.root / "report"
    run(mini_repo, report=out, capsys=capsys)
    orphans, ruled = (
        (out / EXCEPTIONS).read_text(encoding="utf-8").split("undefined by ruling")
    )
    assert "**1 orphan(s)**" in orphans
    assert "gadget" in orphans and "sprocketengine" not in orphans
    assert "A further **1** term(s) are " in orphans
    assert "sprocketengine" in ruled and "gadget" not in ruled.split("##")[0]


def test_a_forward_reference_is_reported(mini_repo, capsys):
    """A definition leaning on one defined below it (criterion 1 clause 2)."""
    mini_repo.write_record(depends_on=["gizmo"])
    mini_repo.write_record(
        id="gizmo", term="gizmo", definition="A gizmo is a small device"
    )
    write_plan(mini_repo, definitions=f"  - {{record: gizmo, section: {SEC}}}\n")
    out = mini_repo.root / "report"
    run(mini_repo, report=out, capsys=capsys)
    text = (out / EXCEPTIONS).read_text(encoding="utf-8")
    assert "`widget` → `gizmo`, defined later" in text
    assert "**1**, each needing a bridging marker" in text


def test_no_forward_reference_says_so_rather_than_going_quiet(mini_repo, capsys):
    mini_repo.write_record()
    write_plan(mini_repo)
    out = mini_repo.root / "report"
    run(mini_repo, report=out, capsys=capsys)
    assert "**None.** Every definition block" in (out / EXCEPTIONS).read_text(
        encoding="utf-8"
    )


# -- declared clusters and the budget ---------------------------------------

DECLARED = (
    "exceptions:\n"
    "  - title: Version skew carried, not harmonised\n"
    "    where: notes/rulings.md §3\n"
)


def test_a_declared_ruling_is_named_and_pointed_at_never_reproduced(
    mini_repo, capsys
):
    mini_repo.write_record()
    write_plan(mini_repo, extra=DECLARED)
    out = mini_repo.root / "report"
    code, payload = run(mini_repo, report=out, capsys=capsys)
    assert code == EXIT_CLEAN
    text = (out / EXCEPTIONS).read_text(encoding="utf-8")
    assert "Version skew carried, not harmonised" in text
    assert "Stated in: notes/rulings.md §3" in text
    # The tool says where to read it and writes no reasoning of its own.
    assert "not reproduced here" in text
    assert payload["summary"]["comments"] == "4/25"


def test_a_declared_ruling_needs_both_a_title_and_a_pointer(mini_repo, capsys):
    """A cluster nobody can find is not a declaration."""
    mini_repo.write_record()
    write_plan(mini_repo, extra="exceptions:\n  - title: Something happened\n")
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_FINDINGS
    assert "plan-schema" in checks(payload)


def _set_budget(mini_repo, value: int) -> None:
    config = mini_repo.root / "detangle.toml"
    config.write_text(
        config.read_text(encoding="utf-8").replace(
            "max-comments-per-PR = 25", f"max-comments-per-PR = {value}"
        ),
        encoding="utf-8",
    )


def test_over_budget_reports_and_writes_no_document(mini_repo, capsys):
    """8c: a document nobody can review in one pass is not a deliverable."""
    mini_repo.write_record()
    write_plan(mini_repo, extra=DECLARED)
    _set_budget(mini_repo, 2)
    out = mini_repo.root / "report"
    code, payload = run(mini_repo, report=out, capsys=capsys)
    assert code == EXIT_FINDINGS
    assert checks(payload) == ["comment-budget"]
    assert not (mini_repo.root / "restructured.md").exists()
    # The report is still written: it is how the reviewer sees what to cut.
    assert (out / EXCEPTIONS).is_file()
    assert payload["summary"]["blocked"].startswith("over the comment budget")


def test_exactly_at_the_budget_is_within_it(mini_repo, capsys):
    mini_repo.write_record()
    write_plan(mini_repo)
    _set_budget(mini_repo, 3)
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_CLEAN
    assert payload["summary"]["comments"] == "3/3"


# -- the real run -----------------------------------------------------------


def test_the_real_plan_reports_the_5_3_baseline_of_nine_clusters():
    """5.3 measured 9 clusters for a whole-document run; the tool finds 9."""
    from detangle.config import Config
    from detangle.records import load_records
    from detangle.restructure import load_plan
    from detangle.restructure.execute import render
    from detangle.restructure.parity import measure
    from detangle.restructure.report import build

    root = Path(__file__).resolve().parent / "data"
    config = Config.load(root, None)
    registry = config.registry()
    plan, findings = load_plan(root / "eval" / "golden" / "uce.plan.yaml", root)
    assert findings == []
    records, _ = load_records(root / "concepts", root)
    source = (root / registry.paths[plan.doc]).read_text(encoding="utf-8")
    rendered = render(plan, records, source)
    text = rendered.text()
    parity = measure(plan, source, rendered)
    limit = config.param("param-max-comments-per-PR")

    report = build(
        plan,
        records,
        source,
        text,
        parity,
        registry.placements[plan.doc],
        limit,
        blob=plan.pinned_blob,
    )
    assert len(report.clusters) == 9
    assert sum(1 for c in report.clusters if c.where) == 6  # ruled by a human
    assert sum(1 for c in report.clusters if not c.where) == 3  # measured here

    # Zero forward references — but only since the plan was corrected. This
    # generator found two the golden's hand-written §9 had missed (it checked
    # the glossary slice, not this document's own definition order), both on
    # `participant-interaction`. Nick ruled a definition block's text counts
    # as a use, which moves it into "Terms defined in this document"; see
    # eval/golden/exceptions.md §9. The regression this guards is the plan
    # drifting back, not the generator.
    forward = next(c for c in report.clusters if c.title == "Forward references")
    assert "**None.**" in forward.body

    # 84 undefined terms, split: 83 orphans and the one IBE/IBEB ruling.
    undefined = next(c for c in report.clusters if "no definition" in c.title)
    assert "**83 orphan(s)**" in undefined.body
    assert "intraday-behavioural-event-builder" in undefined.body
