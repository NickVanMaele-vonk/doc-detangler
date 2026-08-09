"""Usage-edge extraction (C11, step 3.7): prose only, per stamped section.

The rulings under test are Nick's of 2026-08-08: a definition site is not a
use site — text inside ``<!-- concept:… -->`` blocks and a term's own intro
line match nothing — and text above the first ``<!-- sec:… -->`` marker has
no address, so it contributes no edges.
"""

import json
from pathlib import Path

import yaml

from detangle.cli import main
from detangle.findings import EXIT_CLEAN, EXIT_USAGE
from detangle.graph.usage import UsageEdge, build_index, extract
from detangle.records import load_records

REPO = Path(__file__).resolve().parents[1]

BODY = """\
Title block naming a widget before any section exists.

<!-- sec:u-11111111 -->
## Overview

The widget emits alerts; gizmos and Widgets do too.

**widget** (also known as: gizmo)
<!-- concept:widget:start -->
A widget is a device that uses a doohickey.
<!-- concept:widget:end -->

<!-- sec:u-22222222 -->
## Detail

A signal integrity
summary is produced per doohickey.
"""


def records_for(mini_repo, *specs):
    for spec in specs:
        mini_repo.write_record(**spec)
    records, findings = load_records(mini_repo.root / "concepts", mini_repo.root)
    assert findings == []
    return records


def edges_for(mini_repo, body=BODY, *extra_specs):
    records = records_for(
        mini_repo,
        {"id": "widget", "term": "widget", "aliases": ["gizmo"]},
        {"id": "doohickey", "term": "doohickey"},
        *extra_specs,
    )
    index, findings = build_index(records)
    assert findings == []
    return extract(body, "U", index, {r.id for r in records}, "work/u.md")


def test_prose_matches_attribute_to_the_enclosing_section(mini_repo):
    edges, findings = edges_for(mini_repo)
    assert findings == []
    assert UsageEdge("U", "u-11111111", "widget") in edges
    # The title block names the widget too, but has no section to address.
    assert not any(e.section not in {"u-11111111", "u-22222222"} for e in edges)


def test_definition_block_text_is_not_a_use(mini_repo):
    edges, _ = edges_for(mini_repo)
    # doohickey appears in section 1 only inside widget's definition block.
    assert UsageEdge("U", "u-11111111", "doohickey") not in edges
    # Outside a block it counts (section 2 prose).
    assert UsageEdge("U", "u-22222222", "doohickey") in edges


def test_intro_line_is_not_a_self_use(mini_repo):
    body = BODY.replace(
        "The widget emits alerts; gizmos and Widgets do too.", "Nothing here."
    )
    edges, _ = edges_for(mini_repo, body)
    # The only remaining matches of widget/gizmo in section 1 are its own
    # intro line — apparatus of the definition site, not prose usage.
    assert UsageEdge("U", "u-11111111", "widget") not in edges


def test_alias_case_and_plural_all_resolve_to_the_record(mini_repo):
    edges, _ = edges_for(mini_repo)
    # "gizmos" (alias, plural) and "Widgets" (case, plural) both landed on
    # the one record, deduplicated to a single edge for the section.
    assert edges.count(UsageEdge("U", "u-11111111", "widget")) == 1


def test_multiword_surface_matches_across_a_line_wrap(mini_repo):
    edges, _ = edges_for(
        mini_repo,
        BODY,
        {"id": "sis", "term": "signal integrity summary", "aliases": []},
    )
    assert UsageEdge("U", "u-22222222", "sis") in edges


def test_longest_surface_wins(mini_repo):
    edges, _ = edges_for(
        mini_repo,
        BODY,
        {"id": "sis", "term": "signal integrity summary", "aliases": []},
        {"id": "signal", "term": "signal", "aliases": []},
    )
    # "signal integrity summary" consumed the words; the bare "signal"
    # record gets no edge from inside the longer phrase.
    assert UsageEdge("U", "u-22222222", "signal") not in edges


def test_hyphenated_neighbours_do_not_match(mini_repo):
    body = BODY.replace("A signal integrity", "A pre-widget widgeting signal integrity")
    edges, _ = edges_for(mini_repo, body)
    assert UsageEdge("U", "u-22222222", "widget") not in edges


def test_colliding_surface_is_warned_and_matches_nothing(mini_repo):
    records = records_for(
        mini_repo,
        {"id": "widget", "term": "widget", "aliases": ["gizmo"]},
        {"id": "gadget", "term": "gadget", "aliases": ["gizmo"]},
    )
    index, findings = build_index(records)
    assert [f.check for f in findings] == ["usage-ambiguous-surface"]
    assert index.resolve("gizmo") is None
    assert index.resolve("widget") == "widget"


def test_unknown_concept_block_is_warned_but_still_excluded(mini_repo):
    body = BODY.replace("concept:widget:start", "concept:mystery:start").replace(
        "concept:widget:end", "concept:mystery:end"
    )
    edges, findings = edges_for(mini_repo, body)
    assert "usage-unknown-concept" in [f.check for f in findings]
    assert UsageEdge("U", "u-11111111", "doohickey") not in edges


def test_unclosed_block_is_warned(mini_repo):
    body = BODY.replace("<!-- concept:widget:end -->\n", "")
    edges, findings = edges_for(mini_repo, body)
    assert "usage-unclosed-block" in [f.check for f in findings]
    # Everything after the start marker stayed excluded.
    assert UsageEdge("U", "u-22222222", "doohickey") not in edges


# -- through the CLI ---------------------------------------------------------


def with_body(mini_repo, path="work/u.md", body=BODY):
    (mini_repo.root / "work").mkdir(exist_ok=True)
    (mini_repo.root / path).write_text(body, encoding="utf-8")
    toml = mini_repo.root / "detangle.toml"
    toml.write_text(
        toml.read_text(encoding="utf-8") + f'\n[bodies]\nU = "{path}"\n',
        encoding="utf-8",
    )


def test_graph_emits_usage_edges_and_check_passes(mini_repo, capsys):
    mini_repo.write_record(id="widget", term="widget", aliases=["gizmo"])
    mini_repo.write_record(id="doohickey", term="doohickey")
    with_body(mini_repo)
    assert main(["graph", "--root", str(mini_repo.root)]) == EXIT_CLEAN
    data = yaml.safe_load(
        (mini_repo.root / "concept-graph.yaml").read_text(encoding="utf-8")
    )
    assert data["counts"]["usage_edges"] == len(data["edges"]["usage"]) > 0
    assert {"doc": "U", "section": "u-22222222", "term": "doohickey"} in data[
        "edges"
    ]["usage"]
    text = (mini_repo.root / "concept-graph.yaml").read_text(encoding="utf-8")
    assert "Scanned: U=work/u.md" in text
    assert "No body yet: M, S" in text
    capsys.readouterr()
    assert main(["graph", "--root", str(mini_repo.root), "--check"]) == EXIT_CLEAN


def test_graph_without_bodies_emits_the_empty_state(mini_repo, capsys):
    mini_repo.write_record(id="widget", term="widget")
    assert main(["graph", "--root", str(mini_repo.root)]) == EXIT_CLEAN
    text = (mini_repo.root / "concept-graph.yaml").read_text(encoding="utf-8")
    assert "usage_edges: 0" in text
    assert "No body yet: M, S, U" in text


def test_missing_body_file_is_a_usage_error(mini_repo, capsys):
    mini_repo.write_record(id="widget", term="widget")
    toml = mini_repo.root / "detangle.toml"
    toml.write_text(
        toml.read_text(encoding="utf-8") + '\n[bodies]\nU = "work/absent.md"\n',
        encoding="utf-8",
    )
    assert main(["graph", "--root", str(mini_repo.root)]) == EXIT_USAGE


def test_impact_lists_using_sections(mini_repo, capsys):
    # widget's definition depends on doohickey, and section 1 uses widget:
    # a doohickey change impacts widget and so re-opens section 1.
    mini_repo.write_record(
        id="widget", term="widget", aliases=["gizmo"], depends_on=["doohickey"]
    )
    mini_repo.write_record(id="doohickey", term="doohickey")
    with_body(mini_repo)
    code = main(
        ["graph", "--root", str(mini_repo.root), "--impact", "doohickey", "--json"]
    )
    assert code == EXIT_CLEAN
    payload = json.loads(capsys.readouterr().out)
    assert payload["impact"] == ["widget"]
    assert "U#u-11111111" in payload["using_sections"]
    assert "U#u-22222222" in payload["using_sections"]


# -- the real thing ----------------------------------------------------------


def test_extraction_over_the_u_golden_is_nonempty_and_deterministic():
    records, findings = load_records(REPO / "concepts", REPO)
    assert findings == []
    index, index_findings = build_index(records)
    assert index_findings == []
    text = (REPO / "eval/golden/uce.md").read_text(encoding="utf-8")
    known = {r.id for r in records}
    edges, extract_findings = extract(text, "U", index, known, "eval/golden/uce.md")
    again, _ = extract(text, "U", index, known, "eval/golden/uce.md")
    assert edges == again
    assert extract_findings == []
    assert edges, "the U golden uses terms; zero edges would mean a broken scan"
    ids = {r.id for r in records}
    sections = {
        line.split("sec:")[1].split(" ")[0]
        for line in text.splitlines()
        if "<!-- sec:" in line
    }
    assert all(e.doc == "U" and e.term in ids and e.section in sections for e in edges)
