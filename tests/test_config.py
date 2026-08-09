"""Config strictness — the working agreement's "no hard-coded values"."""

import pytest

from detangle.config import Config, find_root
from detangle.findings import UsageError


def test_a_set_parameter_is_read_from_the_file(mini_repo):
    config = Config.load(mini_repo.root)
    assert config.param("param-max-terms-changed-per-PR") == 25
    assert config.param("max-terms-changed-per-PR") == 25


def test_an_unset_parameter_raises_rather_than_defaulting(mini_repo):
    """The fixture config deliberately omits this parameter (the real one
    sets it since 5.3); asking for an absent value must raise, not guess."""
    config = Config.load(mini_repo.root)
    with pytest.raises(UsageError, match="low-confidence-threshold"):
        config.param("param-low-confidence-threshold")


def test_only_the_component_blueprints_count(mini_repo):
    config = Config.load(mini_repo.root)
    assert config.component_docs() == {
        "samples/mini.md",
        "samples/other.md",
        "samples/third.md",
    }


def test_the_registry_resolves_both_input_sets(mini_repo):
    """Two input sets (Nick, 2026-08-05): components and references."""
    registry = Config.load(mini_repo.root).registry()
    assert registry.reference_docs == {"samples/analytical.md"}
    # The glossary registers as a span target — authored wording is canonical
    # in it (D9 amendment), so a lifted span may cite it — but it joins
    # neither input set: not restructured, not counted, not a reference.
    assert registry.registered_docs == registry.component_docs | {
        "samples/analytical.md",
        "glossary.md",
    }
    assert registry.role("glossary.md") == "glossary"
    assert registry.placement_values == ("glossary", "UCE", "SBSP", "MCL")
    assert registry.flags == ("orphan", "conflict", "A")
    assert registry.role("samples/mini.md") == "component"
    assert registry.role("samples/analytical.md") == "reference"
    assert registry.role("notes/scratch.md") == "unregistered"


def _rewrite_config(mini_repo, old: str, new: str) -> None:
    path = mini_repo.root / "detangle.toml"
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new), encoding="utf-8")


def test_a_code_in_both_sets_is_a_usage_error(mini_repo):
    _rewrite_config(mini_repo, 'references = ["A"]', 'references = ["A", "U"]')
    with pytest.raises(UsageError, match="both a component and a reference"):
        Config.load(mini_repo.root).registry()


def test_a_code_in_neither_set_is_a_usage_error(mini_repo):
    """An unassigned code would make its document silently uncitable."""
    _rewrite_config(mini_repo, 'references = ["A"]', "references = []")
    with pytest.raises(UsageError, match="neither 'components' nor 'references'"):
        Config.load(mini_repo.root).registry()


def test_a_missing_references_list_is_a_usage_error(mini_repo):
    _rewrite_config(mini_repo, 'references = ["A"]\n', "")
    with pytest.raises(UsageError, match="'references'"):
        Config.load(mini_repo.root).registry()


def test_a_component_without_a_placement_name_is_a_usage_error(mini_repo):
    _rewrite_config(mini_repo, 'U = "UCE"\n', "")
    with pytest.raises(UsageError, match=r"\[placements\] has no entry"):
        Config.load(mini_repo.root).registry()


def test_a_placement_for_a_reference_code_is_a_usage_error(mini_repo):
    """Nothing is ever placed in a reference document."""
    _rewrite_config(mini_repo, 'M = "MCL"', 'M = "MCL"\nA = "ANA"')
    with pytest.raises(UsageError, match="not component codes"):
        Config.load(mini_repo.root).registry()


def test_the_real_config_names_the_two_input_sets():
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    config = Config.load(root)
    docs = config.documents()
    registry = config.registry()
    assert registry.component_docs == {docs["U"], docs["S"], docs["M"]}
    assert registry.reference_docs == {docs["A"], docs["P"]}
    assert docs["A"].endswith("blueprint-analytical-layer.md")
    assert docs["P"].endswith("prototype-BC17.md")


def test_the_root_is_the_nearest_ancestor_with_a_config(mini_repo):
    nested = mini_repo.root / "concepts"
    assert find_root(nested) == mini_repo.root.resolve()


def test_no_config_anywhere_raises(tmp_path):
    with pytest.raises(UsageError):
        find_root(tmp_path)


def test_a_declared_input_directory_must_exist(mini_repo):
    """A mistyped [paths] entry must not read as "0 records, clean"."""
    config = Config.load(mini_repo.root)
    (mini_repo.root / "concepts").rename(mini_repo.root / "elsewhere")
    with pytest.raises(UsageError, match="is not a directory"):
        config.directory("concepts")


def test_an_output_path_need_not_exist(mini_repo):
    """`graph` writes concept-graph.yaml, so its absence is not an error."""
    config = Config.load(mini_repo.root)
    assert config.path("graph") == mini_repo.root / "concept-graph.yaml"
