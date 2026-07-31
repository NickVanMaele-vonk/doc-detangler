"""Span anchoring — the scheme concepts/README.md declares normative."""

import pytest
import yaml

from detangle.records.spans import BlockIndex, block_hash, normalise, split_blocks


def test_blocks_split_on_blank_lines_and_drop_empties():
    blocks = split_blocks("one\n\n\n  \n\ntwo\n\nthree\n")
    assert blocks == ["one", "two", "three\n"]


def test_normalise_collapses_whitespace_runs():
    assert normalise("a   b\nc") == "a b c"


def test_hash_is_over_the_normalised_text_only():
    """Reflowing a paragraph must not move its hash — that is the whole point."""
    assert normalise("word   word") == normalise("word\nword")
    assert block_hash(normalise("word   word")) == block_hash(normalise("word\nword"))


def test_hash_is_prefixed_and_stable():
    digest = block_hash("abc")
    assert digest.startswith("sha256:")
    assert digest == block_hash("abc")


def test_index_finds_the_block_a_record_anchors_to(mini_repo):
    index = BlockIndex(root=mini_repo.root)
    para_hash = mini_repo.para_hash("A widget is a device")
    text = index.document("samples/mini.md").text_for(para_hash)
    assert text is not None
    assert "A widget is a device" in text


def test_index_returns_none_for_an_unknown_hash(mini_repo):
    index = BlockIndex(root=mini_repo.root)
    assert index.document("samples/mini.md").text_for("sha256:" + "0" * 64) is None


def test_real_records_still_hash_to_their_anchored_blocks(repo_root):
    """One live record against the real corpus, so the scheme cannot drift.

    A single record is enough: this asserts the implementation still agrees
    with how all 358 were authored, and the full sweep is `detangle validate`.
    """
    record = yaml.safe_load(
        (repo_root / "concepts" / "pattern-gate.yaml").read_text(encoding="utf-8")
    )
    index = BlockIndex(root=repo_root)
    span = record["source"][0]
    assert index.document(span["doc"]).text_for(span["para_hash"]) is not None


@pytest.fixture
def repo_root():
    from pathlib import Path

    return Path(__file__).resolve().parent.parent
