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

from ..config import DocumentRegistry
from ..findings import Finding, UsageError, error, warn
from .load import (
    APPROVED_STATUSES,
    ASSURANCE_FIELDS,
    OPTIONAL_FIELDS,
    REQUIRED_FIELDS,
    SPAN_ORIGINS,
    STATUSES,
    Record,
)
from .spans import WHITESPACE, BlockIndex, block_hash, normalise, split_blocks

#: Every check slug this module can raise. Declared so a command can say which
#: checks it actually ran, which is what keeps waiver staleness honest (see
#: ``WaiverRegister.stale_findings``). ``tests/test_checks_declared.py`` reads
#: the slugs back out of the source and fails if this set drifts from them, so
#: adding a check without declaring it is caught rather than silently
#: un-judged.
CHECKS = frozenset(
    {
        "assurance-shape",
        "assurance-unapproved",
        "conflict-flag",
        "conflict-quote",
        "conflict-shape",
        "dangling-link",
        "definition-not-verbatim",
        "definition-number",
        "definition-token",
        "edge-target",
        "edges-on-undefined",
        "flag-value",
        "git-blob",
        "git-blob-stale",
        "id-filename",
        "id-format",
        "one-definition-site",
        "orphan-flag",
        "para-hash-stale",
        "placement-computed",
        "placement-value",
        "schema-missing-key",
        "schema-unknown-key",
        "source-dirty",
        "source-empty",
        "source-empty-doc",
        "span-doc-unknown",
        "span-origin",
        "span-shape",
        "status-value",
        "superseded-target",
        "used-in-value",
    }
)

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


def check_schema(rec: Record, registry: DocumentRegistry) -> list[Finding]:
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
    if data.get("placement") not in registry.placement_values:
        out.append(
            error(
                "placement-value",
                rec.where("placement"),
                f"{data.get('placement')!r} not one of "
                f"{list(registry.placement_values)}",
            )
        )
    for doc in rec.get_list("used_in"):
        if doc not in registry.components:
            out.append(
                error(
                    "used-in-value",
                    rec.where("used_in"),
                    f"{doc!r} not a component code {list(registry.components)} "
                    "— reference-set documents never count toward placement",
                )
            )
    for flag in rec.get_list("flags"):
        if flag not in registry.flags:
            out.append(
                error(
                    "flag-value",
                    rec.where("flags"),
                    f"unknown flag {flag!r} — not one of {list(registry.flags)}",
                )
            )
    if not rec.get_list("source"):
        out.append(error("source-empty", rec.where("source"), "no provenance spans"))
    for i, span in enumerate(rec.get_list("source")):
        if not isinstance(span, dict):
            out.append(error("span-shape", rec.where(f"source[{i}]"), "not a mapping"))
            continue
        for key in ("doc", "section", "para_hash", "origin", "verified_against"):
            if key not in span:
                out.append(
                    error(
                        "span-shape", rec.where(f"source[{i}]"), f"missing {key!r}"
                    )
                )
        if "origin" in span and span["origin"] not in SPAN_ORIGINS:
            out.append(
                error(
                    "span-origin",
                    rec.where(f"source[{i}].origin"),
                    f"{span['origin']!r} not one of {list(SPAN_ORIGINS)} — "
                    "'corpus' is wording the document already carried when the "
                    "tool first consumed it, 'authored' is wording that entered "
                    "in a later version (ADR-004 Decision 2)",
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


def check_assurance(rec: Record) -> list[Finding]:
    """Who vouches for this definition — ADR-004 Decisions 1, 2 and 2b.

    Assurance carries all the definitional strength under Decision 1, which
    only holds if the claim is present, well-formed, and cannot be reached
    without a named human. So three things are checked:

    - a record has an assurance block exactly when it has a definition. There
      is nothing to vouch for otherwise, and an orphan carrying an approver
      would read as a definition nobody can see;
    - the block's shape is exact, because a check reading a misspelt key would
      silently find no approver and report nothing;
    - a status that asserts sign-off (``approved``, ``published``) may not be
      reached with ``approved_by: null``. Today every record is ``candidate``,
      so this fires on nothing — it is the gate that keeps the field
      load-bearing rather than decorative once records start being promoted.

    Deliberately *not* checked here: how many definitions one approval may
    cover. That is ADR-004 Decision 4, unruled, and its parameter is absent
    from ``detangle.toml`` rather than guessed.
    """
    out: list[Finding] = []
    where = rec.where("assurance")
    block = rec.data.get("assurance")

    if not rec.defined:
        if block is not None:
            out.append(
                error(
                    "assurance-shape",
                    where,
                    "record has no definition, so there is nothing to vouch "
                    "for — assurance must be null (ADR-004 Decision 2)",
                )
            )
        return out

    if block is None:
        out.append(
            error(
                "assurance-shape",
                where,
                "a defined record must say who wrote the definition and who "
                "approved it — assurance carries the definitional strength "
                "(ADR-004 Decision 1)",
            )
        )
        return out
    if not isinstance(block, dict):
        out.append(error("assurance-shape", where, "not a mapping"))
        return out

    for key in ASSURANCE_FIELDS:
        if key not in block:
            out.append(error("assurance-shape", where, f"missing {key!r}"))
    for key in sorted(set(block) - set(ASSURANCE_FIELDS)):
        out.append(error("assurance-shape", where, f"unknown key {key!r}"))

    author = block.get("author")
    if not isinstance(author, str) or not author.strip():
        out.append(
            error(
                "assurance-shape",
                rec.where("assurance.author"),
                f"{author!r} is not a name — who produced this wording?",
            )
        )
    approver = block.get("approved_by")
    if approver is not None and (not isinstance(approver, str) or not approver.strip()):
        out.append(
            error(
                "assurance-shape",
                rec.where("assurance.approved_by"),
                f"{approver!r} is neither a name nor null",
            )
        )
    pr = block.get("pr")
    if pr is not None and not isinstance(pr, int):
        out.append(
            error(
                "assurance-shape",
                rec.where("assurance.pr"),
                f"{pr!r} is neither a PR number nor null",
            )
        )
    if approver is None and pr is not None:
        out.append(
            error(
                "assurance-shape",
                where,
                f"PR {pr} is recorded but no approver is named — a PR number "
                "is where an approval happened, not the approval itself",
            )
        )

    if rec.data.get("status") in APPROVED_STATUSES and approver is None:
        out.append(
            error(
                "assurance-unapproved",
                where,
                f"status {rec.data.get('status')!r} asserts a human signed "
                "this definition off, but approved_by is null — approval must "
                "be a real act (ADR-004 Decision 1)",
            )
        )
    return out


def check_span_docs(rec: Record, registry: DocumentRegistry) -> list[Finding]:
    """Every span's ``doc`` names a registered document, from either set.

    Before the registry existed, any git-tracked path was silently accepted —
    a typo'd path produced a hard ``git-blob`` error at best, and a span into
    an arbitrary repo file was treated as provenance. Registration is what
    makes "the reference set is citable, everything else is not" enforceable
    (two input sets, Nick 2026-08-05).
    """
    out: list[Finding] = []
    spans = [
        (f"source[{i}]", span) for i, span in enumerate(rec.get_list("source"))
    ]
    conflict = rec.data.get("conflict")
    if isinstance(conflict, dict) and isinstance(conflict.get("spans"), list):
        spans += [
            (f"conflict.spans[{i}]", span)
            for i, span in enumerate(conflict["spans"])
        ]
    for where, span in spans:
        if not isinstance(span, dict):
            continue  # span-shape reports it
        doc = span.get("doc")
        if isinstance(doc, str) and doc not in registry.registered_docs:
            out.append(
                error(
                    "span-doc-unknown",
                    rec.where(where),
                    f"{doc!r} is not registered in detangle.toml [documents] "
                    "— spans may only cite the detangle set or the reference "
                    "set",
                )
            )
    return out


def expected_placements(
    records: list[Record], registry: DocumentRegistry
) -> dict[str, str]:
    """Where each definition belongs. C9: computed, never judged.

    Two limbs, both mechanical (Nick's Case 3 ruling, 2026-08-03):

    1. used in ≥ 2 component blueprints → the glossary;
    2. otherwise, if a glossary-placed definition depends on it → the
       glossary as well, because the glossary is read first and a reader who
       meets the term there has nowhere to look it up;
    3. otherwise → the one document that uses it.

    Limb 2 is a closure taken to a fixpoint, seeded from limb 1 alone — never
    from the ``placement`` field being checked. Reading the field would make
    the rule self-justifying: one wrongly-placed record would drag its whole
    dependency tree into the glossary and the check would agree.

    Records with no usable ``used_in`` are absent from the result; they are
    reported separately, because nothing can be computed for them.
    """
    used_of = {
        rec.id: [d for d in rec.get_list("used_in") if d in registry.components]
        for rec in records
    }
    known = {rec.id for rec in records}
    edges = {
        rec.id: [t for t in rec.get_list("depends_on") if t in known] for rec in records
    }

    glossary = {rid for rid, used in used_of.items() if len(set(used)) >= 2}
    frontier = set(glossary)
    while frontier:
        pulled = {t for rid in frontier for t in edges[rid]} - glossary
        glossary |= pulled
        frontier = pulled

    return {
        rid: "glossary" if rid in glossary else registry.placements[used[0]]
        for rid, used in used_of.items()
        if used
    }


def check_placement(
    records: list[Record], registry: DocumentRegistry
) -> list[Finding]:
    """C9's placement test. Set-wide, because limb 2 is a graph query.

    This cannot be a per-record check: whether a term belongs in the glossary
    depends on what every other record's definition leans on.
    """
    out: list[Finding] = []
    expected_of = expected_placements(records, registry)
    for rec in records:
        if rec.id not in expected_of:
            out.append(
                error(
                    "placement-computed",
                    rec.where("placement"),
                    "used_in is empty, so placement cannot be computed",
                )
            )
            continue
        expected = expected_of[rec.id]
        if rec.data.get("placement") != expected:
            used = sorted(
                set(d for d in rec.get_list("used_in") if d in registry.components)
            )
            because = (
                "a glossary definition depends on it"
                if expected == "glossary" and len(used) < 2
                else f"used_in {used}"
            )
            out.append(
                error(
                    "placement-computed",
                    rec.where("placement"),
                    f"{because} computes to {expected!r}, "
                    f"record says {rec.data.get('placement')!r}",
                )
            )
    return out


def check_invariants(rec: Record, registry: DocumentRegistry) -> list[Finding]:
    """Structural rules the record set is supposed to hold set-wide."""
    out: list[Finding] = []
    flags = rec.get_list("flags")
    component_docs = registry.component_docs

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

    # An orphan is used but never defined *in the detangle set*
    # (concepts/README.md), so a definition lifted from a reference document
    # leaves the record a set-level orphan — `mts-spa` is the case, and the
    # 2026-08-05 two-input-set ruling made it the rule. What contradicts the
    # flag is a definition anchored in a component blueprint.
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
    "check_assurance",
    "check_conflict_quotes",
    "check_cross_record",
    "check_definition_wording",
    "check_invariants",
    "check_provenance",
    "check_schema",
    "check_source_blocks_current",
    "check_span_docs",
    "normalise",
    "split_blocks",
]
