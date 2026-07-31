"""The concept graph: order, cycles, reachability, and the derived-file guard.

The cases that matter are the ones criterion 1 and ADR-001 Decision 6 turn on:
a cycle without a ruling must block, a ruling without a cycle must be flagged
and not dropped, and the accepted cycle's entry point must come first.
"""

import json

import pytest
import yaml

from detangle import graph as graph_pkg
from detangle.cli import main
from detangle.findings import EXIT_CLEAN, EXIT_FINDINGS, EXIT_USAGE
from detangle.graph import emit
from detangle.records import load_records
from detangle.registers import load_cycles

ACCEPTED = {
    "id": "ab-contrast",
    "members": ["alpha", "beta"],
    "disposition": "accepted-outer-circle",
    "entry_point": "beta",
    "iso_704": "6.5.2",
}


def build(mini_repo):
    root = mini_repo.root
    records, findings = load_records(root / "concepts", root)
    assert findings == []
    register, register_findings = load_cycles(root / "registers", root)
    cg, build_findings = graph_pkg.build(records, register)
    return cg, register_findings + build_findings


def chain(mini_repo):
    """alpha uses beta uses gamma — so gamma reads first, alpha last."""
    mini_repo.write_record(id="alpha", term="alpha", depends_on=["beta"])
    mini_repo.write_record(id="beta", term="beta", depends_on=["gamma"])
    mini_repo.write_record(id="gamma", term="gamma")


def test_edges_follow_depends_on(mini_repo):
    chain(mini_repo)
    cg, findings = build(mini_repo)
    assert findings == []
    assert sorted(cg.graph.edges()) == [("alpha", "beta"), ("beta", "gamma")]


def test_reading_order_defines_before_use(mini_repo):
    chain(mini_repo)
    cg, _ = build(mini_repo)
    assert cg.reading_order() == ["gamma", "beta", "alpha"]


def test_reachability_runs_both_ways(mini_repo):
    chain(mini_repo)
    cg, _ = build(mini_repo)
    assert cg.impact("gamma") == ["alpha", "beta"]
    assert cg.requires("alpha") == ["beta", "gamma"]
    assert cg.impact("alpha") == []


def test_an_undispositioned_cycle_blocks(mini_repo):
    mini_repo.write_record(id="alpha", term="alpha", depends_on=["beta"])
    mini_repo.write_record(id="beta", term="beta", depends_on=["alpha"])
    _, findings = build(mini_repo)
    assert [f.check for f in findings] == ["cycle-undispositioned"]
    assert findings[0].severity == "error"


def test_a_dispositioned_cycle_is_clean_and_reads_entry_point_first(mini_repo):
    mini_repo.write_record(id="alpha", term="alpha", depends_on=["beta"])
    mini_repo.write_record(id="beta", term="beta", depends_on=["alpha"])
    mini_repo.write_cycles(ACCEPTED)
    cg, findings = build(mini_repo)
    assert findings == []
    # Condensed to one unit, entry point first — criterion 1 clause 2.
    assert cg.reading_order() == ["beta", "alpha"]


def test_a_stale_ruling_is_flagged_not_dropped(mini_repo):
    """A narrowed definition kills the cycle; the ruling must not vanish."""
    chain(mini_repo)
    mini_repo.write_cycles(ACCEPTED)
    _, findings = build(mini_repo)
    assert [f.check for f in findings] == ["cycle-stale-ruling"]
    assert findings[0].severity == "warn"


def test_an_entry_point_outside_the_cycle_is_an_error(mini_repo):
    mini_repo.write_record(id="alpha", term="alpha", depends_on=["beta"])
    mini_repo.write_record(id="beta", term="beta", depends_on=["alpha"])
    mini_repo.write_cycles({**ACCEPTED, "entry_point": "gamma"})
    _, findings = build(mini_repo)
    assert "cycle-entry-point" in [f.check for f in findings]


def test_a_missing_entry_point_is_an_error(mini_repo):
    mini_repo.write_record(id="alpha", term="alpha", depends_on=["beta"])
    mini_repo.write_record(id="beta", term="beta", depends_on=["alpha"])
    entry = {k: v for k, v in ACCEPTED.items() if k != "entry_point"}
    mini_repo.write_cycles(entry)
    _, findings = build(mini_repo)
    assert "cycle-entry-point" in [f.check for f in findings]


def test_a_self_loop_is_named_as_one(mini_repo):
    """ISO 704 §6.5.2 prohibits self-definition except by documented exception."""
    mini_repo.write_record(id="alpha", term="alpha", depends_on=["alpha"])
    _, findings = build(mini_repo)
    assert [f.check for f in findings] == ["cycle-self-loop"]


def test_a_dispositioned_self_loop_passes(mini_repo):
    mini_repo.write_record(id="alpha", term="alpha", depends_on=["alpha"])
    mini_repo.write_cycles(
        {
            "id": "alpha-recursive",
            "members": ["alpha"],
            "disposition": "accepted-documented-exception",
            "entry_point": "alpha",
        }
    )
    _, findings = build(mini_repo)
    assert findings == []


def test_a_dangling_target_is_dropped_with_a_warning(mini_repo):
    """validate owns the dangling-target error; the graph just says it left."""
    mini_repo.write_record(id="alpha", term="alpha", depends_on=["nowhere"])
    cg, findings = build(mini_repo)
    assert [f.check for f in findings] == ["edge-dropped"]
    assert list(cg.graph.edges()) == []


def test_a_register_entry_naming_no_record_is_an_error(mini_repo):
    mini_repo.write_record(id="alpha", term="alpha")
    mini_repo.write_cycles(
        {**ACCEPTED, "members": ["alpha", "ghost"], "entry_point": "alpha"}
    )
    _, findings = build(mini_repo)
    assert [f.check for f in findings] == ["cycle-member-unknown"]


def test_orphans_come_from_the_flag_not_from_a_null_definition(mini_repo):
    """The IBE/IBEB ruling leaves software records undefined but unflagged."""
    mini_repo.write_record(id="alpha", term="alpha", definition=None, flags=["orphan"])
    mini_repo.write_record(id="beta", term="beta", definition=None, flags=[])
    cg, _ = build(mini_repo)
    assert cg.orphans() == ["alpha"]
    assert cg.undefined() == ["alpha", "beta"]


def test_dead_entries_are_defined_terms_used_nowhere(mini_repo):
    mini_repo.write_record(id="alpha", term="alpha", used_in=[])
    mini_repo.write_record(id="beta", term="beta", used_in=["U"])
    cg, _ = build(mini_repo)
    assert cg.dead_entries() == ["alpha"]


def test_render_is_byte_stable(mini_repo):
    chain(mini_repo)
    cg, _ = build(mini_repo)
    assert emit.render(cg) == emit.render(cg)


def test_the_rendered_graph_round_trips(mini_repo):
    chain(mini_repo)
    cg, _ = build(mini_repo)
    data = yaml.safe_load(emit.render(cg))
    assert data["counts"]["nodes"] == 3
    assert data["counts"]["dependency_edges"] == 2
    assert data["edges"]["dependency"] == [
        {"from": "alpha", "to": "beta"},
        {"from": "beta", "to": "gamma"},
    ]
    assert data["edges"]["usage"] == []
    assert data["reading_order"] == ["gamma", "beta", "alpha"]
    assert data["cycles"] == []


def test_the_rendered_graph_rolls_up_the_cycle_ruling(mini_repo):
    """Criterion 1 clause 1: the disposition is readable in the graph file."""
    mini_repo.write_record(id="alpha", term="alpha", depends_on=["beta"])
    mini_repo.write_record(id="beta", term="beta", depends_on=["alpha"])
    mini_repo.write_cycles(ACCEPTED)
    cg, _ = build(mini_repo)
    data = yaml.safe_load(emit.render(cg))
    assert data["cycles"][0]["id"] == "ab-contrast"
    assert data["cycles"][0]["disposition"] == "accepted-outer-circle"
    assert data["cycles"][0]["entry_point"] == "beta"
    assert data["cycles"][0]["iso_704"] == "6.5.2"
    assert data["reading_order"] == ["beta", "alpha"]


# -- CLI ------------------------------------------------------------------


def run(mini_repo, *extra, capsys=None):
    code = main(["graph", "--root", str(mini_repo.root), "--json", *extra])
    payload = json.loads(capsys.readouterr().out) if capsys else None
    return code, payload


def test_cli_writes_the_graph(mini_repo, capsys):
    chain(mini_repo)
    code, payload = run(mini_repo, capsys=capsys)
    assert code == EXIT_CLEAN
    assert payload["summary"]["nodes"] == 3
    assert (mini_repo.root / "concept-graph.yaml").is_file()


def test_check_fails_before_the_graph_is_generated(mini_repo, capsys):
    chain(mini_repo)
    code, payload = run(mini_repo, "--check", capsys=capsys)
    assert code == EXIT_FINDINGS
    assert payload["findings"][0]["check"] == "graph-missing"
    assert not (mini_repo.root / "concept-graph.yaml").exists()


def test_check_passes_on_a_freshly_generated_graph(mini_repo, capsys):
    chain(mini_repo)
    run(mini_repo, capsys=capsys)
    code, payload = run(mini_repo, "--check", capsys=capsys)
    assert code == EXIT_CLEAN
    assert payload["findings"] == []


def test_a_hand_edit_of_the_generated_graph_fails(mini_repo, capsys):
    """ADR-001 Decision 5: hand-editing this file is a CI failure."""
    chain(mini_repo)
    run(mini_repo, capsys=capsys)
    path = mini_repo.root / "concept-graph.yaml"
    path.write_text(path.read_text().replace("- id: alpha", "- id: alfa"))
    code, payload = run(mini_repo, "--check", capsys=capsys)
    assert code == EXIT_FINDINGS
    assert payload["findings"][0]["check"] == "graph-drift"


def test_a_record_change_without_regeneration_fails_check(mini_repo, capsys):
    chain(mini_repo)
    run(mini_repo, capsys=capsys)
    mini_repo.write_record(id="delta", term="delta")
    code, payload = run(mini_repo, "--check", capsys=capsys)
    assert code == EXIT_FINDINGS
    assert payload["findings"][0]["check"] == "graph-drift"


def test_cli_impact_query(mini_repo, capsys):
    chain(mini_repo)
    code, payload = run(mini_repo, "--impact", "gamma", capsys=capsys)
    assert code == EXIT_CLEAN
    assert payload == {"node": "gamma", "impact": ["alpha", "beta"], "count": 2}


def test_a_query_never_writes_the_graph(mini_repo, capsys):
    chain(mini_repo)
    run(mini_repo, "--requires", "alpha", capsys=capsys)
    assert not (mini_repo.root / "concept-graph.yaml").exists()


def test_an_unknown_id_is_a_usage_error(mini_repo, capsys):
    chain(mini_repo)
    code, _ = run(mini_repo, "--impact", "nowhere")
    assert code == EXIT_USAGE


def test_impact_and_requires_are_mutually_exclusive(mini_repo):
    with pytest.raises(SystemExit):
        main(
            ["graph", "--root", str(mini_repo.root), "--impact", "a", "--requires", "b"]
        )
