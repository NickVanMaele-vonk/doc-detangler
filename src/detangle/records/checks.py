"""The record-set integrity checks (ADR-001 Decision 4, command 1).

These replace the throwaway per-PR scripts that CLAUDE.md wrote out longhand.
Each check is a function returning findings; none of them repairs anything —
surfacing without judging is criterion 6, and cycles in particular are
"surfaced for disposition, never repaired unilaterally".
"""

from __future__ import annotations

import difflib
import re
import subprocess
from pathlib import Path

from ..findings import Finding, UsageError, error, warn
from .load import (
    DOCUMENTS,
    FLAGS,
    OPTIONAL_FIELDS,
    PLACEMENT_OF,
    PLACEMENTS,
    REQUIRED_FIELDS,
    STATUSES,
    Record,
)
from .spans import WHITESPACE, BlockIndex, block_hash, normalise, split_blocks

ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")

# "Domain-shaped" tokens — the only wording C2 constrains. Ordinary English is
# free (Nick, 2026-07-30): connective and descriptive words are standard
# English, not project terms, and a check that tests every word against the
# anchored block is measuring the wrong thing.
DOMAIN_TOKENS = (
    # SB-13, UCE-AMD-BVR-001, MTSAM-L01 — codes, casing significant (criterion 5)
    ("code", re.compile(r"\b[A-Z0-9]{2,}(?:[-_.][A-Za-z0-9]+)+\b")),
    # MTSAM, BCI, RT01 — acronyms, with or without a trailing index
    ("acronym", re.compile(r"\b[A-Z]{2,}\d*\b")),
    ("snake_case", re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")),
    ("CamelCase", re.compile(r"\b[A-Z][a-z]+(?:[A-Z][a-z0-9]+)+\b")),
)
# Numbers, thresholds and comparison operators are reproduced verbatim
# (criterion 5), so they are checked as their own class. Trailing punctuation
# is stripped afterwards: sentence-final "." and "," are English, and swallowing
# them turns "≥0.85." into a token that no source block can contain.
NUMERIC = re.compile(r"[≥≤<>]=?\s?\d[\d.,]*%?|\b\d[\d.,]*%?\b")
TRAILING_PUNCT = ".,;:"


# --------------------------------------------------------------------------
# git provenance
# --------------------------------------------------------------------------


def _git(root: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(root), *args], capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise UsageError(f"git {' '.join(args)}: {proc.stderr.strip()}")
    return proc.stdout.strip()


class GitBlobs:
    """``git rev-parse HEAD:<doc>`` per document, cached, plus a dirty check."""

    def __init__(self, root: Path):
        self.root = root
        self._head: dict[str, str] = {}
        self._dirty: dict[str, bool] = {}

    def head(self, rel_doc: str) -> str:
        if rel_doc not in self._head:
            self._head[rel_doc] = _git(self.root, "rev-parse", f"HEAD:{rel_doc}")
        return self._head[rel_doc]

    def worktree_differs(self, rel_doc: str) -> bool:
        """True when the file on disk is not what HEAD records.

        Records are verified against HEAD but hashed from the working tree, so
        the two must agree for a para_hash result to mean anything.
        """
        if rel_doc not in self._dirty:
            live = _git(self.root, "hash-object", rel_doc)
            self._dirty[rel_doc] = live != self.head(rel_doc)
        return self._dirty[rel_doc]


# --------------------------------------------------------------------------
# per-record checks
# --------------------------------------------------------------------------


def check_schema(rec: Record) -> list[Finding]:
    """Required keys, no unknown keys, enum membership, id equals filename."""
    out: list[Finding] = []
    data = rec.data
    for key in REQUIRED_FIELDS:
        if key not in data:
            out.append(error("schema-missing-key", rec.rel, f"missing key {key!r}"))
    known = set(REQUIRED_FIELDS) | set(OPTIONAL_FIELDS)
    for key in sorted(set(data) - known):
        out.append(error("schema-unknown-key", rec.rel, f"unknown key {key!r}"))

    if data.get("id") != rec.path.stem:
        out.append(
            error(
                "id-filename",
                rec.where("id"),
                f"id {data.get('id')!r} does not equal filename {rec.path.stem!r}",
            )
        )
    if isinstance(data.get("id"), str) and not ID_RE.match(data["id"]):
        out.append(error("id-format", rec.where("id"), "id is not kebab-case"))

    if data.get("status") not in STATUSES:
        out.append(
            error(
                "status-value",
                rec.where("status"),
                f"{data.get('status')!r} not one of {list(STATUSES)}",
            )
        )
    if data.get("placement") not in PLACEMENTS:
        out.append(
            error(
                "placement-value",
                rec.where("placement"),
                f"{data.get('placement')!r} not one of {list(PLACEMENTS)}",
            )
        )
    for doc in rec.get_list("used_in"):
        if doc not in DOCUMENTS:
            out.append(
                error(
                    "used-in-value",
                    rec.where("used_in"),
                    f"{doc!r} not one of {list(DOCUMENTS)} — (A) and (P) never count",
                )
            )
    for flag in rec.get_list("flags"):
        if flag not in FLAGS:
            out.append(
                error("flag-value", rec.where("flags"), f"unknown flag {flag!r}")
            )
    if not rec.get_list("source"):
        out.append(error("source-empty", rec.where("source"), "no provenance spans"))
    for i, span in enumerate(rec.get_list("source")):
        if not isinstance(span, dict):
            out.append(error("span-shape", rec.where(f"source[{i}]"), "not a mapping"))
            continue
        for key in ("doc", "section", "para_hash", "verified_against"):
            if key not in span:
                out.append(
                    error(
                        "span-shape", rec.where(f"source[{i}]"), f"missing {key!r}"
                    )
                )
        verified = span.get("verified_against")
        if isinstance(verified, dict):
            if "git_blob" not in verified:
                out.append(
                    error(
                        "span-shape",
                        rec.where(f"source[{i}].verified_against"),
                        "missing 'git_blob'",
                    )
                )
            if "stated_version" not in verified:
                out.append(
                    error(
                        "span-shape",
                        rec.where(f"source[{i}].verified_against"),
                        "missing 'stated_version'",
                    )
                )
    return out


def check_invariants(rec: Record, component_docs: set[str]) -> list[Finding]:
    """Structural rules the record set is supposed to hold set-wide."""
    out: list[Finding] = []
    used = [d for d in rec.get_list("used_in") if d in DOCUMENTS]
    flags = rec.get_list("flags")

    # C9: placement is computed, never judged.
    if not used:
        out.append(
            error(
                "placement-computed",
                rec.where("placement"),
                "used_in is empty, so placement cannot be computed",
            )
        )
    else:
        expected = "glossary" if len(set(used)) >= 2 else PLACEMENT_OF[used[0]]
        if rec.data.get("placement") != expected:
            out.append(
                error(
                    "placement-computed",
                    rec.where("placement"),
                    f"used_in {sorted(set(used))} computes to {expected!r}, "
                    f"record says {rec.data.get('placement')!r}",
                )
            )

    # Edges are extracted from definition text, so they live only on defined
    # records (CLAUDE.md, step 3.4 convention).
    if not rec.defined and rec.get_list("depends_on"):
        out.append(
            error(
                "edges-on-undefined",
                rec.where("depends_on"),
                "definition is null, so this record cannot carry edges",
            )
        )

    # An orphan is used but never defined *in U/S/M* (concepts/README.md), so
    # a definition drawn only from the analytical layer or the prototype leaves
    # the record a set-level orphan — `mts-spa` is the case. What contradicts
    # the flag is a definition anchored in a component blueprint.
    #
    # The converse does not hold and is deliberately unchecked: the IBE/IBEB
    # ruling leaves software records undefined and unflagged, because the
    # source does define them and the orphan count measures source
    # convolutedness.
    if "orphan" in flags and rec.defined:
        anchored_in = {
            span.get("doc")
            for span in rec.get_list("source")
            if isinstance(span, dict)
        }
        if anchored_in & component_docs:
            out.append(
                error(
                    "orphan-flag",
                    rec.where("flags"),
                    "flagged orphan but its definition is anchored in a "
                    "component blueprint: "
                    + ", ".join(sorted(anchored_in & component_docs)),
                )
            )

    conflict = rec.data.get("conflict")
    if ("conflict" in flags) != (conflict is not None):
        out.append(
            error(
                "conflict-flag",
                rec.where("flags"),
                "flags and conflict disagree: flag "
                f"{'present' if 'conflict' in flags else 'absent'}, conflict "
                f"{'present' if conflict is not None else 'null'}",
            )
        )
    if isinstance(conflict, dict):
        if not conflict.get("summary"):
            out.append(
                error("conflict-shape", rec.where("conflict"), "missing 'summary'")
            )
        spans = conflict.get("spans")
        if not isinstance(spans, list) or len(spans) < 2:
            out.append(
                error(
                    "conflict-shape",
                    rec.where("conflict.spans"),
                    "a conflict needs both sides: at least two spans",
                )
            )
    return out


# --------------------------------------------------------------------------
# cross-record checks
# --------------------------------------------------------------------------


def check_cross_record(records: list[Record]) -> list[Finding]:
    """One definition site per term (C9), and every reference resolves."""
    out: list[Finding] = []
    ids = {r.id for r in records}

    # C9 one-definition-site: a surface may be claimed by exactly one record,
    # whether it is claimed as a term or as an alias. The MWBR_ANOMALOUS
    # precedent is exactly this — promoting a value to its own record means
    # removing it from the other record's aliases in the same PR.
    # Surfaces are compared case-insensitively, because two records competing
    # for the same word in different casing is still two definition sites. A
    # record cannot collide with itself, though: an alias that differs from its
    # own term only in case is a real surface found in the sources
    # (concepts/README.md, `aliases`), not a second site.
    claims: dict[str, dict[str, str]] = {}
    for rec in records:
        surfaces = [(rec.data.get("term"), "term")]
        surfaces += [(a, "alias") for a in rec.get_list("aliases")]
        for surface, kind in surfaces:
            if isinstance(surface, str) and surface.strip():
                claims.setdefault(surface.strip().lower(), {}).setdefault(
                    rec.id, kind
                )
    for surface, owners in sorted(claims.items()):
        if len(owners) > 1:
            named = ", ".join(f"{rid} ({kind})" for rid, kind in sorted(owners.items()))
            out.append(
                error(
                    "one-definition-site",
                    "concepts/",
                    f"surface {surface!r} claimed by {len(owners)} records: {named}",
                )
            )

    for rec in records:
        for target in rec.get_list("depends_on"):
            if target not in ids:
                out.append(
                    error(
                        "edge-target",
                        rec.where("depends_on"),
                        f"edge target {target!r} has no record",
                    )
                )
        superseded = rec.data.get("superseded_by")
        if superseded is not None and superseded not in ids:
            out.append(
                error(
                    "superseded-target",
                    rec.where("superseded_by"),
                    f"{superseded!r} has no record",
                )
            )
        for link in sorted(set(LINK_RE.findall(rec.text))):
            if link not in ids:
                out.append(
                    error("dangling-link", rec.rel, f"[[{link}]] resolves to nothing")
                )
    return out


# --------------------------------------------------------------------------
# provenance and wording
# --------------------------------------------------------------------------


def _anchored_text(rec: Record, index: BlockIndex) -> list[str]:
    texts = []
    for span in rec.get_list("source"):
        if not isinstance(span, dict):
            continue
        doc, para_hash = span.get("doc"), span.get("para_hash")
        if not isinstance(doc, str) or not isinstance(para_hash, str):
            continue
        text = index.document(doc).text_for(para_hash)
        if text:
            texts.append(text)
    return texts


def check_provenance(
    rec: Record, index: BlockIndex, blobs: GitBlobs
) -> list[Finding]:
    """git_blob matches HEAD, and every para_hash is a block that exists now."""
    out: list[Finding] = []
    for i, span in enumerate(rec.get_list("source")):
        if not isinstance(span, dict):
            continue
        doc = span.get("doc")
        if not isinstance(doc, str):
            continue
        where = rec.where(f"source[{i}]")
        recorded = (span.get("verified_against") or {}).get("git_blob")
        try:
            head = blobs.head(doc)
        except UsageError as exc:
            out.append(error("git-blob", where, str(exc)))
            continue
        if recorded != head:
            out.append(
                warn(
                    "git-blob-stale",
                    where,
                    f"{doc} verified against {recorded}, HEAD is {head} — "
                    "span needs re-verification (provenance: stale), the "
                    "record is not thereby wrong",
                )
            )
        if blobs.worktree_differs(doc):
            out.append(
                warn(
                    "source-dirty",
                    doc,
                    "working tree differs from HEAD; para_hash results below "
                    "are computed from the working tree",
                )
            )
        para_hash = span.get("para_hash")
        if index.document(doc).text_for(para_hash) is None:
            out.append(
                warn(
                    "para-hash-stale",
                    where,
                    f"{para_hash} is not a block of {doc} — hashes are "
                    "tripwires, so re-verify the span",
                )
            )
    return out


def check_definition_wording(
    rec: Record, index: BlockIndex, min_run: int
) -> list[Finding]:
    """C2: definitions are assembled from corpus wording, never invented.

    Two independent tests, because either alone measures the wrong thing:

    * a verbatim run, which catches a definition unrelated to its own block but
      says nothing about a heavily stitched one;
    * every domain-shaped token present in the anchored text, which is the part
      C2 actually constrains — terms, codes, thresholds, modality.
    """
    out: list[Finding] = []
    definition = rec.data.get("definition")
    if not isinstance(definition, str) or not definition.strip():
        return out
    blocks = _anchored_text(rec, index)
    if not blocks:
        return out  # already reported as a stale para_hash
    definition = WHITESPACE.sub(" ", definition).strip()
    haystack = " ".join(blocks)

    best = 0
    for block in blocks:
        matcher = difflib.SequenceMatcher(None, definition, block, autojunk=False)
        match = matcher.find_longest_match(0, len(definition), 0, len(block))
        best = max(best, match.size)
    if best < min_run:
        out.append(
            error(
                "definition-not-verbatim",
                rec.where("definition"),
                f"longest verbatim run against its own anchored blocks is "
                f"{best} characters (floor {min_run}) — a definition must be "
                "assembled from corpus wording, not invented (C2)",
            )
        )

    # Numbers are scanned over a copy with the domain tokens blanked out, so
    # the "99" inside SB-99 is not a second, independent finding about the same
    # defect — the containment-suppression rule from the closing edge pass.
    masked = definition
    for kind, pattern in DOMAIN_TOKENS:
        for match in pattern.finditer(definition):
            blank = " " * len(match[0])
            masked = masked[: match.start()] + blank + masked[match.end() :]
        for token in sorted(set(pattern.findall(definition))):
            if token not in haystack:
                out.append(
                    error(
                        "definition-token",
                        rec.where("definition"),
                        f"{kind} {token!r} does not appear in the anchored "
                        "block(s) — C2 constrains domain wording",
                    )
                )
    numbers = {t.strip().rstrip(TRAILING_PUNCT) for t in NUMERIC.findall(masked)}
    for token in sorted(numbers):
        if token and token not in haystack:
            out.append(
                error(
                    "definition-number",
                    rec.where("definition"),
                    f"{token!r} does not appear in the anchored block(s) — "
                    "numbers, thresholds and operators are verbatim "
                    "(criterion 5)",
                )
            )
    return out


def check_conflict_quotes(rec: Record, index: BlockIndex) -> list[Finding]:
    """Both sides of a surfaced contradiction must be verbatim (C8/criterion 6)."""
    out: list[Finding] = []
    conflict = rec.data.get("conflict")
    if not isinstance(conflict, dict):
        return out
    spans = conflict.get("spans")
    if not isinstance(spans, list):
        return out
    for i, span in enumerate(spans):
        if not isinstance(span, dict):
            continue
        doc, para_hash = span.get("doc"), span.get("para_hash")
        quote = span.get("quote")
        where = rec.where(f"conflict.spans[{i}]")
        if not all(isinstance(v, str) for v in (doc, para_hash, quote)):
            out.append(error("conflict-shape", where, "span is missing a field"))
            continue
        text = index.document(doc).text_for(para_hash)
        if text is None:
            out.append(
                warn("para-hash-stale", where, f"{para_hash} is not a block of {doc}")
            )
            continue
        if WHITESPACE.sub(" ", quote).strip() not in text:
            out.append(
                error(
                    "conflict-quote",
                    where,
                    "quote is not a verbatim substring of its anchored block",
                )
            )
    return out


def check_source_blocks_current(index: BlockIndex, docs: list[str]) -> list[Finding]:
    """Cheap sanity check that a document still splits into blocks at all."""
    out: list[Finding] = []
    for doc in docs:
        if not index.document(doc).by_hash:
            out.append(error("source-empty-doc", doc, "document has no blocks"))
    return out


__all__ = [
    "GitBlobs",
    "block_hash",
    "check_conflict_quotes",
    "check_cross_record",
    "check_definition_wording",
    "check_invariants",
    "check_provenance",
    "check_schema",
    "check_source_blocks_current",
    "normalise",
    "split_blocks",
]
