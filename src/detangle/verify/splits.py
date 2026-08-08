"""The claim-split register — ADR-003 Decision 1's override data.

Where the deterministic decomposer flags a span it cannot confidently split,
the split a human approved lands here — drafted with LLM assistance, reviewed
and merged by PR, exactly the reorder-plan pattern (ADR-002): judgment is
data, the tool executes it and authors nothing. `detangle verify` reads this
file, so the run itself stays deterministic and never calls a model.

An entry replaces exactly one machine artifact:

.. code-block:: yaml

    version: 1
    splits:
      - claim: "U:1a2b3c4d:0:2"       # a machine claim, split into parts
        into:
          - "First sub-claim, wording preserved."
          - "Second sub-claim."
        owner: Nick
        pr: 118
        rationale: one line; the reasoning lives in the PR thread
      - block: "U:5e6f7a8b:0"         # an unparseable block, claims supplied
        into: ["The one claim the OCR-damaged row asserts."]
        owner: Nick
        pr: 118
        rationale: one line

Targets use the decomposer's hash-anchored IDs, never line numbers (D10).
Entries and live flags are meant to stay 1:1, like every register: an entry
whose target no longer exists is surfaced by ``Decomposition.unused_splits``
and raised as ``split-stale`` by the `verify` command.

The register lives at ``registers/claim-splits.yaml`` — one file for the whole
set, ruled by Nick on 2026-08-07. It is canonical data whose provenance is a
PR thread rather than a corpus span, which is the rule that governs what goes
in ``registers/``; claim ids already carry their document, so a per-document
view is a filter rather than a fact the file shape has to supply.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from ..findings import Finding, error, warn

#: See ``records.checks.CHECKS`` for why every module declares its slugs.
CHECKS = frozenset({"split-parse", "split-schema", "split-stale"})

CLAIM_ID_PARTS = (4, 5)  # doc:hash8:occ:n and doc:hash8:occ:n/i
BLOCK_KEY_PARTS = 3  # doc:hash8:occ


@dataclass(frozen=True)
class SplitEntry:
    target: str
    scope: str  # "claim" | "block"
    into: tuple[str, ...]
    owner: str
    pr: int | None
    rationale: str


def _entry_findings(raw: object, where: str) -> tuple[SplitEntry | None, list[Finding]]:
    if not isinstance(raw, dict):
        return None, [error("split-schema", where, "entry is not a mapping")]
    problems: list[Finding] = []
    has_claim = "claim" in raw
    has_block = "block" in raw
    if has_claim == has_block:
        problems.append(
            error("split-schema", where, "exactly one of `claim` or `block` required")
        )
        return None, problems
    scope = "claim" if has_claim else "block"
    target = raw.get("claim" if has_claim else "block")
    if not isinstance(target, str) or not target:
        problems.append(error("split-schema", where, f"`{scope}` must be a string"))
    else:
        parts = len(target.split(":"))
        expected = CLAIM_ID_PARTS if scope == "claim" else (BLOCK_KEY_PARTS,)
        if parts not in expected:
            problems.append(
                error(
                    "split-schema",
                    where,
                    f"`{target}` is not a {scope} id (doc:hash8:occ"
                    + (":n)" if scope == "claim" else ")"),
                )
            )
    into = raw.get("into")
    if (
        not isinstance(into, list)
        or not into
        or not all(isinstance(s, str) and s.strip() for s in into)
    ):
        problems.append(
            error("split-schema", where, "`into` must be a non-empty list of strings")
        )
    for key in ("owner", "rationale"):
        if not isinstance(raw.get(key), str) or not raw[key].strip():
            problems.append(error("split-schema", where, f"`{key}` is required"))
    pr = raw.get("pr")
    if pr is not None and not isinstance(pr, int):
        problems.append(error("split-schema", where, "`pr` must be an integer"))
    if problems:
        return None, problems
    return (
        SplitEntry(
            target=target,
            scope=scope,
            into=tuple(s.strip() for s in into),
            owner=raw["owner"].strip(),
            pr=pr,
            rationale=raw["rationale"].strip(),
        ),
        [],
    )


def load_splits(path: Path) -> tuple[list[SplitEntry], list[Finding]]:
    """Load the register; an absent file is the normal, empty state.

    A malformed register must not excuse itself: parse and schema findings
    come back as errors and the caller must not run with a partial read.
    """
    if not path.is_file():
        return [], []
    rel = path.name
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [], [error("split-parse", rel, f"unreadable register: {exc}")]
    if data is None:
        return [], []
    if not isinstance(data, dict) or not isinstance(data.get("splits"), list):
        return [], [error("split-schema", rel, "top level must be {version, splits}")]
    if data.get("version") != 1:
        return [], [error("split-schema", rel, "unknown `version` (expected 1)")]

    entries: list[SplitEntry] = []
    findings: list[Finding] = []
    seen: dict[str, int] = {}
    for i, raw in enumerate(data["splits"]):
        where = f"{rel}:splits[{i}]"
        entry, problems = _entry_findings(raw, where)
        findings.extend(problems)
        if entry is None:
            continue
        if entry.target in seen:
            findings.append(
                error(
                    "split-schema",
                    where,
                    f"duplicate target `{entry.target}` (first at splits"
                    f"[{seen[entry.target]}])",
                )
            )
            continue
        seen[entry.target] = i
        entries.append(entry)
    return entries, findings


def for_document(entries: list[SplitEntry], code: str) -> list[SplitEntry]:
    """The entries targeting document ``code``.

    **Source side only, and that is a live gap.** Every flag the decomposer
    raises is on a source document, so this is where entries are authored; but
    coverage compares a source decomposition against an *output* one, and a
    source claim split into two only matches if the output claim is split the
    same way. Propagating an entry by rebasing its id onto the output does not
    work: measured on the `U` golden, 4 of 84 source blocks keep their
    ``para_hash`` through the restructure, because a block re-emitted with
    section and concept markers hashes differently. So 95% of entries would be
    silently inert on the output side — worse than not trying, since the
    failure looks like a residue claim rather than a missed override.

    The rule that would work anchors on the claim's **text** rather than its
    id, which is what a split is really a ruling about. That is a design
    decision, not an implementation detail, so it is Nick's: until it is
    ruled, an entry splits the source and the parts fall to the residue, which
    is the same place they would have landed unsplit.
    """
    return [e for e in entries if e.target.partition(":")[0] == code]


def stale_splits(
    entries: list[SplitEntry], scanned: set[str], unused: set[str], rel: str
) -> list[Finding]:
    """Entries this run proved dead, so a ruling and its target stay 1:1.

    Scoped to the documents the run decomposed, for the reason waiver
    staleness is scoped to the checks the running command owns: a `verify`
    over ``U`` alone cannot prove an ``S`` entry dead, and the false alarm
    would land on a register a human curates by hand.

    A warn, not an error. The register is not malformed and no document is
    wrong — a target moved, which is what happens when the source is corrected
    (backlog B-1) or the flagging heuristics are recalibrated.
    """
    out: list[Finding] = []
    for entry in entries:
        doc = entry.target.partition(":")[0]
        if doc not in scanned or entry.target not in unused:
            continue
        out.append(
            warn(
                "split-stale",
                f"{rel}:{entry.target}",
                f"no {entry.scope} `{entry.target}` in {doc}: the split is "
                "ruled but its target has moved. Re-anchor it against the "
                "current decomposition or delete it — a register's entries "
                "and its live targets stay 1:1",
            )
        )
    return out


__all__ = [
    "CHECKS",
    "SplitEntry",
    "for_document",
    "load_splits",
    "stale_splits",
]
