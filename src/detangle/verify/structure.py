"""Concept-before-use — ADR-003 Decision 4, ruled by Nick 2026-08-07.

Plan step 7.4, and criterion 1's structural half: a reader must never meet a
term before its definition. The definition side comes from the graph and the
registers and is already built — reading order from `concept-graph.yaml`, the
accepted cycle's entry point from `registers/cycles.yaml`. This module is the
document side: where each definition actually sits, where each term is
actually first used, and which pairs are the wrong way round.

**What counts as a use** (the ruled question). Every occurrence of a record's
term or one of its aliases in the document's prose blocks and table rows,
matched with the edge-matching discipline the closing pass proved on 402 edges
(PRs #54–#58): case-sensitive for codes, case-insensitive with plurals for
phrases, token boundaries so ``MTSAM`` never matches inside ``MTSAM-L01``, and
occurrence-level containment suppression so a match sitting inside a longer
matched span is not an independent use. Headings, grid rules and marker-only
blocks are furniture and are not scanned.

Two things this rule deliberately does *not* do, and why. It does not count
occurrences anywhere at all, which would report forward references that are
artifacts of section headings and navigation — noise that trains a reviewer to
ignore the check. And it does not restrict itself to decomposed claims, which
would be tidier but blind: the decomposer yields no claim from a fragment with
no terminal punctuation, so a table cell reading ``Gate: CQT`` would be a use
the reader meets and the check never sees.

**A definition block's own text counts as a use** (Nick, 2026-08-05). That is
not a special case here — a definition block is prose, so it is scanned like
any other. The golden's second defect was a miscount that came from looking at
prose sections only, and this is what stops it recurring in `S` and `M`, whose
blast radius the 6.2 comparison recorded as unmeasured.

**Scope is the whole reading order**, glossary → UCE → SBSP → MCL, not each
document alone. C9 should make a cross-document forward reference structurally
impossible: a term used in two documents is defined in the glossary, which is
read first. So the cross-document result ought to be empty — and an empty
result is the proof that C9 held, which is worth having rather than assuming.

Positions are **block indices, never line numbers** (D10). Blocks are the
blank-line units the `para_hash` convention already uses, so a position here
means the same thing it means everywhere else in the toolchain.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..findings import Finding, error
from ..graph.build import ConceptGraph
from ..records.spans import WHITESPACE, split_blocks

#: See ``records.checks.CHECKS`` for why every module declares its slugs.
CHECKS = frozenset({"forward-use"})

#: ``<!-- concept:<id> -->`` (the glossary's form) and ``:start`` / ``:end``
#: (the form a restructured document carries, per D9). The id pattern refuses
#: ``<id>``, so the banner sentence in `glossary.md` that *describes* the
#: marker is not mistaken for one.
MARKER = re.compile(r"<!--\s*concept:([A-Za-z0-9][A-Za-z0-9-]*)(:start|:end)?\s*-->")

#: Any HTML comment: metadata, not text. Stripped before matching, exactly as
#: `para_hash` normalisation and the parity tokenizer strip it.
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)

#: Markdown decoration that can sit inside a term's surface (``**Derisking
#: Assessment**``). Removed so a surface is matched on its words.
DECORATION = re.compile(r"[*_`\\]")

#: A character that continues a token. A surface flanked by one of these is
#: part of a longer token and is not a use of the surface — this is what keeps
#: ``MTSAM`` out of ``MTSAM-L01``.
BOUNDARY = r"[A-Za-z0-9_-]"

#: A surface with no whitespace that carries an upper-case letter, a digit or
#: an underscore is a code (``SB-01``, ``MM_SAFEHARBOUR``, ``CQT``): matched
#: case-sensitively, because its casing is normative (criterion 5). Everything
#: else is a phrase.
CODE = re.compile(r"^(?=\S+$)(?=.*[A-Z0-9_])")

#: Endings that take ``es`` rather than ``s``.
SIBILANT = ("s", "x", "z", "ch", "sh")


@dataclass(frozen=True)
class Position:
    """Where something sits in the reading order."""

    doc: str
    index: int  # block index within the document
    order: int  # block index across the whole reading order

    def __str__(self) -> str:
        return f"{self.doc}:block[{self.index}]"


@dataclass(frozen=True)
class ForwardUse:
    concept: str
    defined_at: Position
    used_at: Position
    #: The record whose definition block the use sits in, if any.
    inside: str | None = None


@dataclass
class Structure:
    #: Document codes, in the reading order they were scanned in.
    documents: list[str] = field(default_factory=list)
    defined_at: dict[str, Position] = field(default_factory=dict)
    first_use: dict[str, Position] = field(default_factory=dict)
    #: Used before defined — the defect.
    forward: list[ForwardUse] = field(default_factory=list)
    #: Used before defined, but between two members of an accepted cycle, so
    #: it is criterion 1 clause 2's marked bridging reference, not a defect.
    exempt: list[ForwardUse] = field(default_factory=list)
    #: Records with a definition but no definition site in the documents
    #: scanned. Data, not a finding: today only the glossary and `U` exist, so
    #: every `S`/`M`-placed definition is legitimately absent.
    no_site: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Document:
    code: str
    text: str


def _variants(surface: str) -> list[str]:
    """A phrase and its plurals; a code on its own."""
    if CODE.match(surface):
        return [surface]
    lower = surface.lower()
    tail = "es" if lower.endswith(SIBILANT) else "s"
    return [surface, surface + tail]


def _surfaces(cg: ConceptGraph) -> tuple[dict[str, str], dict[str, str]]:
    """Lower-cased phrase variants and exact code variants, each to its record.

    A surface claimed by two records is a C9 violation that `detangle validate`
    already reports (`surface-collision`); here the first record in id order
    wins, so the scan stays deterministic rather than refusing to run.
    """
    codes: dict[str, str] = {}
    phrases: dict[str, str] = {}
    for rid in sorted(cg.records):
        record = cg.records[rid]
        raw = [record.data.get("term"), *record.get_list("aliases")]
        for surface in raw:
            if not isinstance(surface, str) or not surface.strip():
                continue
            surface = surface.strip()
            target = codes if CODE.match(surface) else phrases
            for variant in _variants(surface):
                key = variant if target is codes else variant.lower()
                target.setdefault(key, rid)
    return phrases, codes


def _pattern(surfaces: dict[str, str], flags: int) -> re.Pattern | None:
    """One alternation, longest surface first so the longest match wins."""
    if not surfaces:
        return None
    alternatives = "|".join(
        re.escape(s) for s in sorted(surfaces, key=lambda s: (-len(s), s))
    )
    return re.compile(f"(?<!{BOUNDARY})(?:{alternatives})(?!{BOUNDARY})", flags)


def _scannable(block: str) -> str:
    """The block's text, or empty if it is furniture.

    Markers are stripped **before** the heading test, not after: a section
    heading arrives carrying its own `sec:` marker, so testing the raw block
    would miss it and count the heading's words as uses. That is not
    hypothetical — it is what made the golden's `Human Intervention
    Checkpoint` heading look like a forward reference to the definition
    directly beneath it.
    """
    text = COMMENT.sub(" ", block)
    body = "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    )
    return WHITESPACE.sub(" ", DECORATION.sub("", body)).strip()


def _uses(text: str, phrases, codes, phrase_map, code_map) -> set[str]:
    """Records used in ``text``, after occurrence-level containment suppression."""
    spans: list[tuple[int, int, str]] = []
    lookups = ((phrases, phrase_map, True), (codes, code_map, False))
    for pattern, mapping, fold in lookups:
        if pattern is None:
            continue
        for m in pattern.finditer(text):
            key = m[0].lower() if fold else m[0]
            rid = mapping.get(key)
            if rid:
                spans.append((m.start(), m.end(), rid))
    found: set[str] = set()
    for start, end, rid in spans:
        # Suppressed when some *other* match strictly contains this one: the
        # occurrence is part of a longer surface, not an independent use.
        if any(
            (s, e) != (start, end) and s <= start and end <= e for s, e, _ in spans
        ):
            continue
        found.add(rid)
    return found


def scan(documents: list[Document], cg: ConceptGraph) -> Structure:
    """Walk the reading order once, recording definition sites and first uses."""
    phrase_map, code_map = _surfaces(cg)
    phrases = _pattern(phrase_map, re.IGNORECASE)
    codes = _pattern(code_map, 0)

    result = Structure(documents=[d.code for d in documents])
    order = 0
    owner_of: dict[int, str | None] = {}

    for document in documents:
        open_owner: str | None = None
        for index, block in enumerate(split_blocks(document.text)):
            here = Position(doc=document.code, index=index, order=order)
            owners = {open_owner} if open_owner else set()
            for rid, kind in MARKER.findall(block):
                if kind == ":end":
                    if open_owner == rid:
                        open_owner = None
                    continue
                # A marker on an undefined entry names the record, not a
                # definition: the glossary stamps all 155 entries and 77 of
                # them say "not defined in the corpus". Meeting such a term
                # early is not a forward reference, because there is nothing
                # ahead to have read first.
                record = cg.records.get(rid)
                if record is not None and record.defined:
                    result.defined_at.setdefault(rid, here)
                owners.add(rid)
                open_owner = rid
            owner_of[order] = next(iter(sorted(owners)), None) if owners else None

            text = _scannable(block)
            if text:
                for rid in _uses(text, phrases, codes, phrase_map, code_map):
                    if rid not in result.first_use:
                        result.first_use[rid] = here
            order += 1

    accepted = [set(c) for c in cg.cycles if cg.entry_for(c)]
    for rid, defined in result.defined_at.items():
        used = result.first_use.get(rid)
        if used is None or used.order >= defined.order:
            continue
        inside = owner_of.get(used.order)
        pair = {rid, inside} if inside else set()
        bridging = any(pair and pair <= members for members in accepted)
        entry = ForwardUse(rid, defined, used, inside)
        (result.exempt if bridging else result.forward).append(entry)

    result.forward.sort(key=lambda f: (f.used_at.order, f.concept))
    result.exempt.sort(key=lambda f: (f.used_at.order, f.concept))
    result.no_site = sorted(
        rid for rid, rec in cg.records.items()
        if rec.defined and rid not in result.defined_at
    )
    return result


def check(structure: Structure) -> list[Finding]:
    """One finding per term the reader meets before its definition.

    An error, not a warning: criterion 1 is a pass condition, and unlike a
    proposed `depends_on` edge there is no judgment to make — the reader
    either has the definition by then or does not. It is waivable, so a
    forward reference someone has decided to live with can be deferred with
    its reasoning written down.
    """
    out: list[Finding] = []
    for use in structure.forward:
        where = f"{use.used_at}"
        inside = f" inside the definition of `{use.inside}`" if use.inside else ""
        out.append(
            error(
                "forward-use",
                where,
                f"`{use.concept}` is used here{inside} but defined later, at "
                f"{use.defined_at} — a reader meets the term before its "
                "definition (criterion 1)",
            )
        )
    return out


__all__ = ["CHECKS", "Document", "ForwardUse", "Position", "Structure", "check", "scan"]
