"""`detangle restructure` — executing a plan, end to end.

The decisive test runs the real `uce.plan.yaml` against the real corpus and
compares the machine output to the approved golden: identical section
markers, byte-identical definition blocks, and an empty token diff in both
directions. That is 6.2's comparison bar, held in CI.
"""

import json
import re
from collections import Counter
from pathlib import Path

from conftest import BASE_WAIVER  # noqa: F401 (fixture parity with siblings)

from detangle.cli import main
from detangle.findings import EXIT_CLEAN, EXIT_FINDINGS

SEC = "u-00000001"


def mini_plan(mini_repo) -> Path:
    from detangle.records.spans import block_hash, normalise, split_blocks

    text = (mini_repo.root / "samples" / "mini.md").read_text(encoding="utf-8")
    hashes = [block_hash(normalise(b)) for b in split_blocks(text)]
    assigned = "\n".join(f"  - {{block: {h}, section: {SEC}}}" for h in hashes)
    plan = (
        "doc: U\n"
        "sections:\n"
        "  - {id: u-aaaaaaaa, title: Overview, kind: generated}\n"
        f"  - {{id: {SEC}, title: \"1. Everything\", kind: content}}\n"
        f"assignments:\n{assigned}\n"
        "definitions:\n"
        f"  - {{record: widget, section: {SEC}}}\n"
        "additions:\n"
        "  - section: u-aaaaaaaa\n"
        "    form: ai-addition-section\n"
        "    text: |\n"
        "      > [AI addition] Written to introduce the document.\n"
        "\n"
        "      A short overview.\n"
    )
    path = mini_repo.root / "samples" / "mini.plan.yaml"
    path.write_text(plan, encoding="utf-8")
    return path


def run(mini_repo, *extra, capsys=None):
    plan = mini_repo.root / "samples" / "mini.plan.yaml"
    out = mini_repo.root / "restructured.md"
    code = main(
        [
            "restructure",
            "--root",
            str(mini_repo.root),
            "--plan",
            str(plan),
            "--out",
            str(out),
            "--json",
            *extra,
        ]
    )
    payload = json.loads(capsys.readouterr().out) if capsys else None
    return code, payload, out


def test_a_complete_plan_executes_clean(mini_repo, capsys):
    mini_repo.write_record()
    mini_plan(mini_repo)
    code, payload, out = run(mini_repo, capsys=capsys)
    assert code == EXIT_CLEAN
    assert payload["findings"] == []
    text = out.read_text(encoding="utf-8")
    assert f"<!-- sec:{SEC} -->" in text
    assert "<!-- concept:widget:start -->" in text
    assert "A widget is a device that emits SB-01 alerts" in text
    assert "<!-- AI addition:start" in text and "[AI addition]" in text
    assert "A gadget is used here but never defined" in text


def test_an_incomplete_plan_blocks_execution(mini_repo, capsys):
    """Writing from an undecided plan would launder a hole into an omission."""
    mini_repo.write_record()
    path = mini_plan(mini_repo)
    text = path.read_text(encoding="utf-8")
    first_assignment = next(
        line for line in text.splitlines() if line.startswith("  - {block:")
    )
    path.write_text(text.replace(first_assignment + "\n", ""), encoding="utf-8")
    code, payload, out = run(mini_repo, capsys=capsys)
    assert code == EXIT_FINDINGS
    assert "plan-incomplete" in [f["check"] for f in payload["findings"]]
    assert not out.exists()


def test_check_catches_a_hand_edit(mini_repo, capsys):
    mini_repo.write_record()
    mini_plan(mini_repo)
    _, _, out = run(mini_repo, capsys=capsys)
    out.write_text(
        out.read_text(encoding="utf-8").replace("widget", "Widget"), "utf-8"
    )
    code, payload, _ = run(mini_repo, "--check", capsys=capsys)
    assert code == EXIT_FINDINGS
    assert "restructure-drift" in [f["check"] for f in payload["findings"]]


def test_check_is_clean_after_an_execute(mini_repo, capsys):
    mini_repo.write_record()
    mini_plan(mini_repo)
    run(mini_repo, capsys=capsys)
    code, payload, _ = run(mini_repo, "--check", capsys=capsys)
    assert code == EXIT_CLEAN
    assert payload["findings"] == []


def test_the_render_is_deterministic(mini_repo, capsys):
    mini_repo.write_record()
    mini_plan(mini_repo)
    _, _, out = run(mini_repo, capsys=capsys)
    first = out.read_text(encoding="utf-8")
    run(mini_repo, capsys=capsys)
    assert out.read_text(encoding="utf-8") == first


# -- the 6.2 bar: machine execution reproduces the approved golden ----------


def _tokens(text: str) -> Counter:
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S).replace("\\", "")
    out = []
    for word in text.split():
        word = word.strip("|+*_").strip()
        if word and not set(word) <= set("-=+|_*> #"):
            out.append(word)
    return Counter(out)


def test_the_real_plan_reproduces_the_golden():
    from detangle.config import Config
    from detangle.records import load_records
    from detangle.restructure import load_plan
    from detangle.restructure.execute import execute

    root = Path(__file__).resolve().parent / "data"
    Config.load(root)  # asserts the real config parses
    plan, findings = load_plan(root / "eval" / "golden" / "uce.plan.yaml", root)
    assert findings == []
    records, _ = load_records(root / "concepts", root)
    source = (root / "samples" / "blueprint-UCE-shortened.md").read_text(
        encoding="utf-8"
    )
    text = execute(plan, records, source)
    golden = (root / "eval" / "golden" / "uce.md").read_text(encoding="utf-8")

    assert re.findall(r"<!-- sec:(u-[0-9a-f]{8}) -->", text) == re.findall(
        r"<!-- sec:(u-[0-9a-f]{8}) -->", golden
    )
    def_pattern = r"<!-- concept:([a-z0-9-]+):start -->\n(.*?)\n<!-- concept"
    assert re.findall(def_pattern, text, re.S) == re.findall(
        def_pattern, golden, re.S
    )
    gold_tokens, ours = _tokens(golden), _tokens(text)
    assert not (gold_tokens - ours), dict(gold_tokens - ours)
    assert not (ours - gold_tokens), dict(ours - gold_tokens)


def test_the_real_s_plan_reproduces_the_s_golden():
    """The step 9.1 bar, same shape as U's: markers, definitions, tokens."""
    from detangle.config import Config
    from detangle.records import load_records
    from detangle.restructure import load_plan
    from detangle.restructure.execute import execute

    root = Path(__file__).resolve().parent / "data"
    Config.load(root)
    plan, findings = load_plan(root / "eval" / "golden" / "sbsp.plan.yaml", root)
    assert findings == []
    records, _ = load_records(root / "concepts", root)
    source = (root / "samples" / "blueprint-SBSP-shortened.md").read_text(
        encoding="utf-8"
    )
    text = execute(plan, records, source)
    golden = (root / "eval" / "golden" / "sbsp.md").read_text(encoding="utf-8")

    assert re.findall(r"<!-- sec:(s-[0-9a-f]{8}) -->", text) == re.findall(
        r"<!-- sec:(s-[0-9a-f]{8}) -->", golden
    )
    def_pattern = r"<!-- concept:([a-z0-9-]+):start -->\n(.*?)\n<!-- concept"
    assert re.findall(def_pattern, text, re.S) == re.findall(
        def_pattern, golden, re.S
    )
    gold_tokens, ours = _tokens(golden), _tokens(text)
    assert not (gold_tokens - ours), dict(gold_tokens - ours)
    assert not (ours - gold_tokens), dict(ours - gold_tokens)


# -- the grid-list hint (step 9.1) -------------------------------------------


GRID = (
    "+---------------+------+\n"
    "| **Domain 1**  |      |\n"
    "+===============+======+\n"
    "| **SB-01**     | One  |\n"
    "|               |      |\n"
    "|               | Two  |\n"
    "+---------------+------+\n"
)


def test_grid_list_renders_every_row_and_drops_nothing():
    """Unlike `history-list`, no row is read as a header: the archetype and
    change-log grids open with content, and a drop there is a content loss."""
    from detangle.records.spans import block_hash, normalise, split_blocks
    from detangle.restructure.execute import render
    from detangle.restructure.plan import Plan, Section

    [block] = split_blocks(GRID)
    h = "sha256:" + block_hash(normalise(block)).removeprefix("sha256:")
    plan = Plan(
        path=Path("x"),
        rel="x",
        doc="S",
        pinned_blob=None,
        sections=[Section(id="s-00000001", title="T", kind="content")],
        assignments=[{"block": h, "section": "s-00000001", "render": "grid-list"}],
    )
    rendered = render(plan, [], GRID)
    text = rendered.text()
    assert "**Domain 1**" in text and "****" not in text
    assert "**SB-01**" in text
    assert "One" in text and "Two" in text
    assert rendered.drops == []


def test_the_real_m_plan_reproduces_the_m_golden():
    """The step 9.1 bar for the third document, completing the set."""
    from detangle.config import Config
    from detangle.records import load_records
    from detangle.restructure import load_plan
    from detangle.restructure.execute import execute

    root = Path(__file__).resolve().parent / "data"
    Config.load(root)
    plan, findings = load_plan(root / "eval" / "golden" / "mcl.plan.yaml", root)
    assert findings == []
    records, _ = load_records(root / "concepts", root)
    source = (root / "samples" / "blueprint-MCL-shortened.md").read_text(
        encoding="utf-8"
    )
    text = execute(plan, records, source)
    golden = (root / "eval" / "golden" / "mcl.md").read_text(encoding="utf-8")

    assert re.findall(r"<!-- sec:(m-[0-9a-f]{8}) -->", text) == re.findall(
        r"<!-- sec:(m-[0-9a-f]{8}) -->", golden
    )
    def_pattern = r"<!-- concept:([a-z0-9-]+):start -->\n(.*?)\n<!-- concept"
    assert re.findall(def_pattern, text, re.S) == re.findall(
        def_pattern, golden, re.S
    )
    gold_tokens, ours = _tokens(golden), _tokens(text)
    assert not (gold_tokens - ours), dict(gold_tokens - ours)
    assert not (ours - gold_tokens), dict(ours - gold_tokens)
