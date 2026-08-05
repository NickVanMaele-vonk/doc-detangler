"""The machine-readable reorder plan: loader and run-time losslessness.

ADR-002 Decision 2: every source block is covered by exactly one of
assignment, rejoin, or noise — the tool refuses to run a plan that has not
decided a block's fate. The last test validates the real `uce.plan.yaml`
against the real corpus, records and registry, which is the fixture the
prototype (6.1) will execute.
"""

from pathlib import Path

import pytest

from detangle.config import Config, DocumentRegistry
from detangle.records import BlockIndex, load_records
from detangle.records.spans import block_hash, normalise, split_blocks
from detangle.restructure import load_plan, validate_plan

REGISTRY = DocumentRegistry(
    components=("U", "S", "M"),
    references=("A",),
    paths={
        "U": "samples/mini.md",
        "S": "samples/other.md",
        "M": "samples/third.md",
        "A": "samples/analytical.md",
    },
    placements={"U": "UCE", "S": "SBSP", "M": "MCL"},
)

SEC = "u-00000001"


def mini_hashes(mini_repo) -> list[str]:
    text = (mini_repo.root / "samples" / "mini.md").read_text(encoding="utf-8")
    return [block_hash(normalise(b)) for b in split_blocks(text)]


def write_plan(mini_repo, text: str) -> Path:
    path = mini_repo.root / "samples" / "mini.plan.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def full_plan_text(mini_repo, records_line="") -> str:
    """A plan covering every block of the fixture corpus."""
    hashes = mini_hashes(mini_repo)
    assigned = "\n".join(
        f"  - {{block: {h}, section: {SEC}}}" for h in hashes
    )
    return (
        "doc: U\n"
        f"sections:\n  - {{id: {SEC}, title: Everything, kind: content}}\n"
        f"assignments:\n{assigned}\n"
        f"{records_line}"
    )


def run(mini_repo, plan_text: str, records=()):
    path = write_plan(mini_repo, plan_text)
    plan, findings = load_plan(path, mini_repo.root)
    assert findings == [], [f.message for f in findings]
    index = BlockIndex(root=mini_repo.root)
    return validate_plan(plan, REGISTRY, index, list(records))


def checks(findings):
    return sorted(f.check for f in findings)


def test_a_complete_plan_validates_clean(mini_repo):
    assert run(mini_repo, full_plan_text(mini_repo)) == []


def test_an_undecided_block_is_plan_incomplete(mini_repo):
    hashes = mini_hashes(mini_repo)
    line = f"  - {{block: {hashes[0]}, section: {SEC}}}\n"
    text = full_plan_text(mini_repo).replace(line, "")
    findings = run(mini_repo, text)
    assert checks(findings) == ["plan-incomplete"]
    assert hashes[0] in findings[0].message


def test_a_doubly_claimed_block_is_plan_overlap(mini_repo):
    hashes = mini_hashes(mini_repo)
    text = full_plan_text(mini_repo) + (
        f"noise:\n  - {{block: {hashes[0]}, kind: furniture}}\n"
    )
    assert checks(run(mini_repo, text)) == ["plan-overlap"]


def test_an_unknown_hash_is_reported(mini_repo):
    text = full_plan_text(mini_repo) + (
        "noise:\n  - {block: sha256:" + "0" * 64 + ", kind: artifact}\n"
    )
    assert checks(run(mini_repo, text)) == ["plan-block-unknown"]


def test_an_undeclared_section_is_reported(mini_repo):
    text = full_plan_text(mini_repo) + (
        "additions:\n  - {section: u-99999999, form: ai-addition-section}\n"
    )
    assert checks(run(mini_repo, text)) == ["plan-section-unknown"]


def test_a_definition_needs_a_concept_record(mini_repo):
    text = full_plan_text(mini_repo) + (
        f"definitions:\n  - {{record: ghost, section: {SEC}}}\n"
    )
    assert checks(run(mini_repo, text)) == ["plan-record-unknown"]


def test_only_the_detangle_set_is_restructured(mini_repo):
    """ADR-002 via the two-input-set ruling: reference docs are read-only."""
    text = full_plan_text(mini_repo).replace("doc: U", "doc: A")
    findings = run(mini_repo, text)
    assert checks(findings) == ["plan-doc"]
    assert "reference documents are read-only" in findings[0].message


def test_a_stale_pin_is_a_warning_not_an_error(mini_repo):
    path = write_plan(
        mini_repo, "pinned_blob: " + "f" * 40 + "\n" + full_plan_text(mini_repo)
    )
    plan, findings = load_plan(path, mini_repo.root)
    assert findings == []
    index = BlockIndex(root=mini_repo.root)
    findings = validate_plan(
        plan, REGISTRY, index, [], head_blob=mini_repo.blob("samples/mini.md")
    )
    assert checks(findings) == ["plan-blob-stale"]
    assert findings[0].severity == "warn"


def test_yaml_damage_is_a_finding_not_a_crash(mini_repo):
    path = write_plan(mini_repo, "doc: [unclosed\n")
    plan, findings = load_plan(path, mini_repo.root)
    assert plan is None
    assert checks(findings) == ["plan-parse"]


def test_a_missing_plan_file_is_reported(mini_repo):
    plan, findings = load_plan(mini_repo.root / "samples" / "nope.yaml", mini_repo.root)
    assert plan is None
    assert checks(findings) == ["plan-parse"]


@pytest.mark.parametrize(
    "text,where",
    [
        ("sections: 3\n", "sections"),
        ("sections:\n  - {id: bad_id, title: x, kind: content}\n", "sections[0]"),
        ("sections:\n  - {id: u-00000001, title: x, kind: banana}\n", "sections[0]"),
        ("assignments:\n  - {block: sha256:0}\n", "assignments[0]"),
        ("noise:\n  - {block: sha256:0, kind: mess}\n", "noise[0]"),
    ],
)
def test_shape_errors_are_plan_schema(mini_repo, text, where):
    path = write_plan(mini_repo, "doc: U\n" + text)
    _, findings = load_plan(path, mini_repo.root)
    assert "plan-schema" in checks(findings)
    assert any(where in f.where for f in findings)


def test_the_real_plan_validates_against_the_real_corpus():
    """The 6.1 fixture: uce.plan.yaml covers every block of the pinned U."""
    root = Path(__file__).resolve().parents[1]
    config = Config.load(root)
    plan, findings = load_plan(root / "eval" / "golden" / "uce.plan.yaml", root)
    assert findings == [], [f.message for f in findings]
    records, _ = load_records(root / "concepts", root)
    index = BlockIndex(root=root)
    findings = validate_plan(plan, config.registry(), index, records)
    assert findings == [], [f"{f.check}: {f.message}" for f in findings]
    assert len(plan.definitions) == 35
    assert len(plan.sections) == 9
