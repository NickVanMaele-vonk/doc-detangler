"""Claim decomposition (ADR-003 Decision 1, build step 1).

The pinned-blob test at the bottom is the build-step gate: the machine
decomposition of `U` is held stable, and its reconciliation against the 5.3
hand count of 289 is written where the numbers are asserted.
"""

from __future__ import annotations

import subprocess
from collections import Counter
from pathlib import Path

from detangle.registers import is_waivable
from detangle.verify.claims import (
    DECOMPOSER_VERSION,
    decompose,
    split_sentences,
)
from detangle.verify.splits import SplitEntry, for_document, load_splits, stale_splits

#: The register's home, ruled by Nick 2026-08-07 — one file for the whole set.
REL = "registers/claim-splits.yaml"

#: eval/README.md's pinned blob for `U`. If the B-1 source correction lands,
#: this blob changes and the golden re-baseline updates it here in the same
#: PR (the "pinned now, re-baselined later" ruling).
PINNED_U_BLOB = "4cae72dece7638c1ddec8206a3c6a24610196de0"

DOC = """\
**Title Furniture**

A widget emits alerts. It is calibrated to 0.85. E.g. a test value stays attached.

## 2. Heading is furniture

+-----------+----------------------+
| **Code**  | **Rule**             |
+===========+======================+
| SB-01     | The widget must flag |
|           | MEDIUM- INVESTIGATE. |
+-----------+----------------------+
| SB-02     |                      |
+-----------+----------------------+

1. First principle sentence. Enforced at Step 2.
"""


# -- sentence splitting ------------------------------------------------------


def test_splits_on_terminal_punctuation():
    assert split_sentences("One rule here. Two rules there.") == [
        "One rule here.",
        "Two rules there.",
    ]


def test_abbreviations_and_initials_do_not_split():
    assert split_sentences("See e.g. The spec for detail.") == [
        "See e.g. The spec for detail."
    ]
    assert split_sentences("J. Smith rules. Done.") == ["J. Smith rules.", "Done."]


def test_a_bare_number_is_an_enumerator_not_a_sentence_end():
    # The guard that keeps "1. Behaviour precedes suspicion" whole also merges
    # a genuine boundary after a number — the documented v1 trade-off.
    assert split_sentences("1. First principle sentence.") == [
        "1. First principle sentence."
    ]


def test_fragments_without_terminal_punctuation_are_not_claims():
    assert split_sentences("Document 1 of 3") == []
    assert split_sentences("Key Rules:") == []
    assert split_sentences("") == []


# -- decomposition -----------------------------------------------------------


def test_decomposes_prose_and_cells_dropping_furniture():
    result = decompose(DOC, "U")
    kinds = [(c.kind, c.text) for c in result.claims]
    # Title (no terminal punctuation) and the heading yield nothing.
    assert kinds == [
        ("prose", "A widget emits alerts."),
        ("prose", "It is calibrated to 0.85."),
        ("prose", "E.g. a test value stays attached."),
        ("cell", "SB-01"),
        ("cell", "The widget must flag MEDIUM- INVESTIGATE."),
        ("cell", "SB-02"),  # its empty neighbour cell is dropped
        # pandoc consumes the "1." enumerator as list markup, not text.
        ("prose", "First principle sentence."),
        ("prose", "Enforced at Step 2."),
    ]
    assert result.anomalies == []
    assert result.version == DECOMPOSER_VERSION


def test_ids_are_hash_anchored_and_deterministic():
    first = decompose(DOC, "U")
    second = decompose(DOC, "U")
    assert first.claims == second.claims
    for claim in first.claims:
        doc, h8, occ, n = claim.id.split(":")
        assert doc == "U" and len(h8) == 8 and occ == "0" and int(n) >= 1
        assert claim.para_hash.startswith("sha256:")


def test_identical_blocks_get_distinct_occurrence_ids():
    doc = "A widget emits alerts.\n\nA widget emits alerts.\n"
    result = decompose(doc, "U")
    assert [c.id.split(":")[2] for c in result.claims] == ["0", "1"]
    assert len({c.id for c in result.claims}) == 2


def test_flags_mark_the_override_worklist():
    result = decompose(DOC, "U")
    by_text = {c.text: c.flags for c in result.claims}
    assert by_text["The widget must flag MEDIUM- INVESTIGATE."] == ("broken-hyphen",)
    fragment = decompose(
        "+--------------+\n| tested cells |\n+--------------+\n", "U"
    )
    assert fragment.claims[0].flags == ("fragment-suspect",)


# -- overrides ---------------------------------------------------------------


def _entry(**kw) -> SplitEntry:
    base = dict(scope="claim", owner="Nick", pr=1, rationale="test")
    base.update(kw)
    return SplitEntry(**base)


def test_a_claim_split_replaces_one_claim_in_place():
    machine = decompose(DOC, "U")
    target = machine.claims[4]  # the two-part rule cell
    entry = _entry(
        target=target.id,
        into=("The widget must flag.", "MEDIUM- INVESTIGATE is the flagged value."),
    )
    result = decompose(DOC, "U", splits=[entry])
    texts = [c.text for c in result.claims]
    assert "The widget must flag MEDIUM- INVESTIGATE." not in texts
    sub = [c for c in result.claims if c.id.startswith(target.id + "/")]
    assert [c.id for c in sub] == [f"{target.id}/1", f"{target.id}/2"]
    assert all(c.kind == "cell" for c in sub)
    assert result.unused_splits == []
    # Position preserved: sub-claims sit where the machine claim sat.
    assert texts.index("The widget must flag.") == 4


def test_a_block_override_supplies_the_blocks_claims_outright():
    machine = decompose(DOC, "U")
    block_key = machine.claims[0].id.rsplit(":", 1)[0]
    entry = _entry(
        target=block_key, scope="block", into=("One supplied claim, whole block.",)
    )
    result = decompose(DOC, "U", splits=[entry])
    supplied = [c for c in result.claims if c.kind == "override"]
    assert [c.text for c in supplied] == ["One supplied claim, whole block."]
    assert supplied[0].id == f"{block_key}:1"
    # The machine's three prose claims from that block are gone.
    assert "A widget emits alerts." not in [c.text for c in result.claims]


def test_an_unmatched_override_target_is_reported():
    entry = _entry(target="U:deadbeef:0:1", into=("Never matches.",))
    result = decompose(DOC, "U", splits=[entry])
    assert result.unused_splits == ["U:deadbeef:0:1"]


# -- the register loader -----------------------------------------------------


def test_an_absent_register_is_the_normal_empty_state(tmp_path: Path):
    entries, findings = load_splits(tmp_path / "claim-splits.yaml")
    assert entries == [] and findings == []


def test_register_schema_findings(tmp_path: Path):
    path = tmp_path / "claim-splits.yaml"
    path.write_text(
        """\
version: 1
splits:
  - claim: "U:1a2b3c4d:0:2"
    into: ["Good entry."]
    owner: Nick
    pr: 118
    rationale: fine
  - claim: "U:1a2b3c4d:0:3"
    block: "U:1a2b3c4d:0"
    into: ["Both scopes set."]
    owner: Nick
    rationale: bad
  - block: "U:1a2b3c4d:0"
    into: []
    owner: Nick
    rationale: empty into
""",
        encoding="utf-8",
    )
    entries, findings = load_splits(path)
    assert [e.target for e in entries] == ["U:1a2b3c4d:0:2"]
    assert {f.check for f in findings} == {"split-schema"}
    assert len(findings) == 2


def test_register_duplicate_targets_and_parse_errors(tmp_path: Path):
    path = tmp_path / "claim-splits.yaml"
    path.write_text("{unbalanced", encoding="utf-8")
    entries, findings = load_splits(path)
    assert entries == [] and [f.check for f in findings] == ["split-parse"]
    path.write_text(
        """\
version: 1
splits:
  - claim: "U:1a2b3c4d:0:2"
    into: ["First."]
    owner: Nick
    rationale: fine
  - claim: "U:1a2b3c4d:0:2"
    into: ["Second."]
    owner: Nick
    rationale: duplicate
""",
        encoding="utf-8",
    )
    entries, findings = load_splits(path)
    assert len(entries) == 1
    assert [f.check for f in findings] == ["split-schema"]


# -- scoping and staleness (register home ruled by Nick 2026-08-07) ----------


def test_entries_are_selected_by_the_document_their_target_names():
    entries = [
        _entry(target="U:1a2b3c4d:0:2", into=("U.",)),
        _entry(target="S:1a2b3c4d:0:2", into=("S.",)),
        _entry(target="M:1a2b3c4d:0", scope="block", into=("M.",)),
    ]
    assert [e.target for e in for_document(entries, "U")] == ["U:1a2b3c4d:0:2"]
    assert [e.target for e in for_document(entries, "M")] == ["M:1a2b3c4d:0"]
    assert for_document(entries, "A") == []


def test_a_target_that_matched_nothing_is_stale():
    entry = _entry(target="U:deadbeef:0:1", into=("Never matches.",))
    findings = stale_splits([entry], {"U"}, {"U:deadbeef:0:1"}, REL)
    assert [f.check for f in findings] == ["split-stale"]
    assert findings[0].severity == "warn"
    assert findings[0].where == f"{REL}:U:deadbeef:0:1"


def test_a_document_this_run_did_not_read_cannot_have_a_stale_entry():
    """The waiver-stale precedent: only the run that could see it may judge it.

    A `verify` over `U` alone says nothing about an `S` entry, and the false
    alarm would land on a register a human curates by hand.
    """
    entry = _entry(target="S:deadbeef:0:1", into=("Not read this run.",))
    assert stale_splits([entry], {"U"}, {"S:deadbeef:0:1"}, REL) == []


def test_an_entry_that_fired_is_not_stale():
    entry = _entry(target="U:1a2b3c4d:0:2", into=("Fired.",))
    assert stale_splits([entry], {"U"}, set(), REL) == []


def test_a_malformed_register_cannot_excuse_itself():
    """`split-parse`/`split-schema` join `register-parse` in NOT_WAIVABLE."""
    assert not is_waivable("split-parse")
    assert not is_waivable("split-schema")
    assert is_waivable("split-stale")  # a moved target is real, deferrable work


# -- the build-step gate: the pinned `U` blob --------------------------------


def test_pinned_u_blob_decomposition_is_stable():
    """The machine decomposition of `U`, held as the step-1 regression value.

    The 5.3 hand count is 289 (23 prose + 266 cells); the machine measures
    the raw pinned blob and reports 270 (24 prose + 246 cells). The
    difference is not noise and is explained where it was ruled to be
    (ADR-003 Decision 1, PR #116): the hand count worked from the golden,
    where the 7 OCR page-split rows are already rejoined and their repeated
    per-fragment header rows deduplicated; the machine sees the raw shards.
    Closing that gap is what the claim-split override register exists for —
    entries there are human judgment, so the machine number stays pinned
    here until overrides land by PR.
    """
    root = Path(__file__).resolve().parents[1]
    blob = subprocess.run(
        ["git", "-C", str(root), "cat-file", "blob", PINNED_U_BLOB],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    result = decompose(blob, "U")
    prose = [c for c in result.claims if c.kind == "prose"]
    cells = [c for c in result.claims if c.kind == "cell"]
    assert (len(result.claims), len(prose), len(cells)) == (270, 24, 246)
    assert result.anomalies == []
    flags = Counter(flag for c in result.claims for flag in c.flags)
    assert flags == {
        "broken-hyphen": 16,
        "multi-assertion": 10,
        "fragment-suspect": 10,
        "overlong": 8,
    }
    # Every claim anchored: the whole-document parse and the para_hash block
    # convention agree about where each claim lives.
    assert not [c for c in result.claims if "anchor-unresolved" in c.flags]
