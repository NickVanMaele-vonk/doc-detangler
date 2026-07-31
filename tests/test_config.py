"""Config strictness — the working agreement's "no hard-coded values"."""

import pytest

from detangle.config import Config, find_root
from detangle.findings import UsageError


def test_a_set_parameter_is_read_from_the_file(mini_repo):
    config = Config.load(mini_repo.root)
    assert config.param("param-max-terms-changed-per-PR") == 25
    assert config.param("max-terms-changed-per-PR") == 25


def test_an_unset_parameter_raises_rather_than_defaulting(mini_repo):
    """param-low-confidence-threshold is "to be set from Phase 5"."""
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


def test_the_real_config_names_the_three_component_blueprints():
    from pathlib import Path

    root = Path(__file__).resolve().parent.parent
    docs = Config.load(root).documents()
    assert Config.load(root).component_docs() == {docs["U"], docs["S"], docs["M"]}
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
