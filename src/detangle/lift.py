"""The glossary drift lint — the lift (D9 amendment, ruled 2026-08-04).

``glossary.md`` is the fourth editable document: a definition is canonical in
the file, and the concept record carries a derived copy. This module is what
enforces that ruling. ``detangle lift`` mirrors the file back into the
records; ``lift --check`` verifies the mirror is current and is the fourth CI
gate — the one `generate --check` could not be, because byte-comparing a file
humans edit is incoherent (step 3.5 note (a)).

Two rulings shape what the lift may write (Nick, 2026-08-08):

- **The tool lifts; the gate compares.** The record's ``definition`` field is
  derived data, so it is regenerated from the file, never hand-maintained
  (C12) — exactly the `graph --check` pattern, pointed at records.
- **Mechanical lineage, flagged assurance.** When lifted wording is no longer
  covered by the record's spans, the lift also maintains the lineage block:
  an ``authored`` span anchored by the prose's ``para_hash`` and the glossary
  blob (ADR-004 Decision 2 made lineage exactly this mechanical). Assurance
  stays human — authored wording with no ``assurance.author`` is a finding,
  filled by a person in the same PR, never by the tool.

Everything else on a record is ontology and is **never written**: a heading
or alias line disagreeing with the record's canonical ``term``/``aliases`` is
a finding for a human, because the record owns those fields (D9).

The definition's extent is delimited, never inferred: each entry's prose sits
between ``<!-- concept:<id>:start -->`` and ``<!-- concept:<id>:end -->``
markers, the same scheme the bodies carry — the DoD names these markers as
what keeps the lift deterministic. Inside a block, the heading, the alias
line, the "not defined" note and generated bridging notes are apparatus;
every other block is definition prose. Text outside the blocks — overview,
sources, any note a human adds between entries — belongs to the file alone
and is not mirrored anywhere.

Records are written surgically: only the ``definition:`` and ``source:``
regions of the YAML text are replaced, and the result is re-parsed and
compared field-for-field against the intended record before anything lands on
disk — a record the writer cannot edit provably-minimally is a finding, not a
silent reformat.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .findings import Finding, error
from .graph.build import ConceptGraph
from .records import Record
from .records.checks import GitBlobs
from .records.spans import block_hash, normalise, split_blocks

#: See ``records.checks.CHECKS``.
CHECKS = frozenset(
    {
        "lift-drift",
        "lift-assurance-missing",
        "lift-unknown-entry",
        "lift-missing-entry",
        "lift-duplicate-entry",
        "lift-unclosed-entry",
        "lift-ontology-drift",
        "lift-order",
        "lift-stale-note",
        "lift-unwritable-record",
    }
)

GLOSSARY_PLACEMENT = "glossary"

#: A whole line that is a concept delimiter. Anchored to the full line so the
#: banner sentence *describing* the marker can never be one.
MARKER = re.compile(r"^<!--\s*concept:([a-z0-9][a-z0-9-]*):(start|end)\s*-->$")

#: Any HTML comment span — apparatus, stripped from prose before matching.
#: DOTALL because a human's comment may span lines within a block; non-greedy
#: so ``a <!-- x --> b <!-- y --> c`` loses only the comments, never the text
#: between them. (A comment spanning a *blank line* spans blocks and cannot
#: be stripped here — the same limit the verify scanner has.)
COMMENT_SPAN = re.compile(r"<!--.*?-->", re.DOTALL)

ALIASES_PREFIX = "**Also known as:**"
GAP_NOTE_PREFIX = "> **Not defined in the corpus.**"
BRIDGING_MARKER = "<!-- bridging:"
BRIDGING_FALLBACK = "> **Forward reference"

#: Wrap width for the folded ``definition: >-`` scalar: 77-character lines at
#: 2-space indent, the style every existing record carries.
WRAP = 75


@dataclass
class Entry:
    """One glossary entry, as delimited in the file."""

    rid: str
    heading: str | None = None
    aliases_line: str | None = None
    #: Raw prose blocks (marker lines still attached — hashing needs the block
    #: exactly as ``BlockIndex`` will split it).
    prose_blocks: list[str] = field(default_factory=list)
    has_gap_note: bool = False
    closed: bool = False

    @property
    def prose(self) -> str:
        """The definition text: blocks minus comment spans, whitespace-flat."""
        text = " ".join(COMMENT_SPAN.sub(" ", block) for block in self.prose_blocks)
        return " ".join(text.split())


@dataclass
class Intent:
    """What one record should say after the lift."""

    record: Record
    definition: str | None
    source: list[dict]

    @property
    def differs(self) -> bool:
        current = self.record.data.get("definition")
        current = " ".join(str(current).split()) if current is not None else None
        return (current, self.record.data.get("source")) != (
            self.definition,
            self.source,
        )


def _classify(block: str) -> str:
    """What a block inside an entry is, judged with comment spans stripped.

    The bridging note is recognised by its marker before stripping — the
    marker is the generated identity (criterion 1 clause 2), the blockquote
    prefix only a fallback for a hand-repaired note that lost it.
    """
    if BRIDGING_MARKER in block:
        return "bridging"
    lines = [
        line for line in COMMENT_SPAN.sub(" ", block).splitlines() if line.strip()
    ]
    first = lines[0].strip() if lines else ""
    if not first:
        return "empty"
    if first.startswith("## "):
        return "heading"
    if first.startswith(ALIASES_PREFIX):
        return "aliases"
    if first.startswith(GAP_NOTE_PREFIX):
        return "gap-note"
    if first.startswith(BRIDGING_FALLBACK):
        return "bridging"
    return "prose"


def parse_entries(text: str, rel: str) -> tuple[list[Entry], list[Finding]]:
    """Every delimited entry, in file order, with the delimiter defects.

    An unclosed entry is best-effort terminated at the next ``start`` marker
    (or end of file) so one missing marker does not misattribute every entry
    after it, but its content is not trusted for lifting.
    """
    entries: list[Entry] = []
    findings: list[Finding] = []
    current: Entry | None = None

    for block in split_blocks(text):
        marker_ids = [
            (m.group(1), m.group(2))
            for line in block.splitlines()
            if (m := MARKER.match(line.strip()))
        ]
        starts = [rid for rid, kind in marker_ids if kind == "start"]
        ends = [rid for rid, kind in marker_ids if kind == "end"]

        if starts:
            if current is not None and not current.closed:
                findings.append(
                    error(
                        "lift-unclosed-entry",
                        rel,
                        f"entry `{current.rid}` has no end marker before "
                        f"`{starts[0]}` starts — its prose is not lifted "
                        "until the marker is restored",
                    )
                )
            current = Entry(rid=starts[0])
            entries.append(current)

        if current is None or current.closed:
            continue  # head matter, or free text between entries

        kind = _classify(block)
        if kind == "heading":
            stripped = [
                line.strip()
                for line in block.splitlines()
                if line.strip().startswith("## ")
            ]
            current.heading = stripped[0][3:].strip()
        elif kind == "aliases":
            line = next(
                line.strip()
                for line in block.splitlines()
                if line.strip().startswith(ALIASES_PREFIX)
            )
            current.aliases_line = line[len(ALIASES_PREFIX) :].strip()
        elif kind == "gap-note":
            current.has_gap_note = True
        elif kind == "prose":
            current.prose_blocks.append(block)

        if ends and current.rid in ends:
            current.closed = True

    if current is not None and not current.closed:
        findings.append(
            error(
                "lift-unclosed-entry",
                rel,
                f"entry `{current.rid}` has no end marker — its prose is not "
                "lifted until the marker is restored",
            )
        )
    return entries, findings


def _owned(span: object, rel: str) -> bool:
    """A span the lift maintains: authored wording anchored in the glossary."""
    return (
        isinstance(span, dict)
        and span.get("origin") == "authored"
        and span.get("doc") == rel
    )


def _spans_for(entry: Entry, rel: str, blob: str) -> list[dict]:
    """One authored span per prose block — the mechanical lineage axis.

    ``para_hash`` is computed by the same split/normalise/hash pipeline the
    ``BlockIndex`` uses, over the raw block exactly as it sits in the file, so
    ``detangle validate`` resolves it without special-casing the glossary.
    """
    return [
        {
            "doc": rel,
            "section": entry.rid,
            "para_hash": block_hash(normalise(block)),
            "origin": "authored",
            "verified_against": {"git_blob": blob, "stated_version": None},
        }
        for block in entry.prose_blocks
    ]


def compare(
    entries: list[Entry],
    cg: ConceptGraph,
    rel: str,
    blob: str,
) -> tuple[list[Intent], list[Finding]]:
    """The whole lint: structural findings plus the per-record lift intents.

    ``blob`` is the glossary's live git blob — computed once by the caller, so
    a run's spans all bind the same bytes it actually read.
    """
    findings: list[Finding] = []
    records = cg.records
    expected_order = [
        rid
        for rid in cg.reading_order()
        if records[rid].data.get("placement") == GLOSSARY_PLACEMENT
    ]
    glossary_ids = set(expected_order)

    seen: set[str] = set()
    in_file: list[str] = []
    intents: list[Intent] = []
    for entry in entries:
        rid = entry.rid
        if rid in seen:
            findings.append(
                error(
                    "lift-duplicate-entry",
                    rel,
                    f"`{rid}` has two entries — one definition site per term "
                    "(C9); remove one",
                )
            )
            continue
        seen.add(rid)
        if rid not in records:
            findings.append(
                error(
                    "lift-unknown-entry",
                    rel,
                    f"entry `{rid}` names no concept record — a new term "
                    "needs its record (and a computed placement) before the "
                    "lift can mirror it",
                )
            )
            continue
        if rid not in glossary_ids:
            findings.append(
                error(
                    "lift-unknown-entry",
                    rel,
                    f"entry `{rid}` is placed in "
                    f"{records[rid].data.get('placement')!r}, not the "
                    "glossary — placement is computed (C9), so its "
                    "definition site is not this file",
                )
            )
            continue
        in_file.append(rid)
        if not entry.closed:
            continue  # reported by parse_entries; content untrusted

        record = records[rid]
        findings.extend(_ontology_findings(entry, record, rel))
        prose = entry.prose
        if prose and entry.has_gap_note:
            findings.append(
                error(
                    "lift-stale-note",
                    rel,
                    f"entry `{rid}` carries both definition prose and the "
                    '"not defined in the corpus" note — the note is now '
                    "wrong; delete it",
                )
            )

        intent = _intent(entry, record, prose, rel, blob)
        if intent.differs:
            intents.append(intent)
        if intent.definition is not None and any(
            _owned(s, rel) for s in intent.source
        ):
            findings.extend(_assurance_findings(record))

    for rid in expected_order:
        if rid not in seen:
            findings.append(
                error(
                    "lift-missing-entry",
                    rel,
                    f"glossary-placed record `{rid}` has no entry in this "
                    "file — every glossary term holds its place in the "
                    "reading order (criterion 3)",
                )
            )
    findings.extend(_order_findings(in_file, expected_order, rel))
    return intents, findings


def _intent(
    entry: Entry, record: Record, prose: str, rel: str, blob: str
) -> Intent:
    """The record's intended state, given what the file says.

    The lift owns exactly the authored-in-glossary spans. They exist when the
    wording differs from the record (it entered by edit) or when the record
    already carries some (re-anchoring is routine, ADR-004); they are removed
    when the prose is gone. Corpus spans and spans into other documents are
    lineage history and are never touched.
    """
    kept = [s for s in record.get_list("source") if not _owned(s, rel)]
    current = record.data.get("definition")
    current = " ".join(str(current).split()) if current is not None else None
    had_owned = len(kept) != len(record.get_list("source"))

    if not prose:
        return Intent(record=record, definition=None, source=kept)
    if prose != current or had_owned:
        return Intent(
            record=record,
            definition=prose,
            source=kept + _spans_for(entry, rel, blob),
        )
    return Intent(record=record, definition=current, source=kept)


def _ontology_findings(entry: Entry, record: Record, rel: str) -> list[Finding]:
    """The heading and alias line must say what the record says (D9)."""
    out: list[Finding] = []
    term = str(record.data.get("term") or record.id)
    if entry.heading is not None and entry.heading != term:
        out.append(
            error(
                "lift-ontology-drift",
                rel,
                f"entry `{entry.rid}` is headed {entry.heading!r} but the "
                f"record's term is {term!r} — the record owns the ontology "
                "(D9); change the record or restore the heading",
            )
        )
    aliases = [str(a) for a in record.get_list("aliases")]
    expected = ", ".join(aliases) if aliases else None
    if entry.aliases_line != expected:
        out.append(
            error(
                "lift-ontology-drift",
                rel,
                f"entry `{entry.rid}` lists aliases "
                f"{entry.aliases_line or '(none)'!r} but the record says "
                f"{expected or '(none)'!r} — aliases are canonical on the "
                "record (D9); change the record or restore the line",
            )
        )
    return out


def _assurance_findings(record: Record) -> list[Finding]:
    """Authored wording must name who wrote it — the axis the lift never fills."""
    block = record.data.get("assurance")
    author = block.get("author") if isinstance(block, dict) else None
    if isinstance(author, str) and author.strip():
        return []
    return [
        error(
            "lift-assurance-missing",
            record.where("assurance"),
            "this definition carries authored wording, but no author is "
            "named — assurance carries the definitional strength (ADR-004 "
            "Decision 1) and is a human's to write, in this PR",
        )
    ]


def _order_findings(
    in_file: list[str], expected_order: list[str], rel: str
) -> list[Finding]:
    """Entries must sit in topological order (criterion 1).

    Compared on the sequence of entries the file actually has, so a missing
    entry is one finding (`lift-missing-entry`), not a cascade of order noise.
    """
    present = set(in_file)
    expected = [rid for rid in expected_order if rid in present]
    for got, want in zip(in_file, expected, strict=True):
        if got != want:
            return [
                error(
                    "lift-order",
                    rel,
                    f"entries leave topological order at `{got}` (expected "
                    f"`{want}`) — a reader would meet a term before its "
                    "definition (criterion 1); reorder the entries",
                )
            ]
    return []


# -- writing records --------------------------------------------------------


TOP_KEY = re.compile(r"^([a-z_]+):", re.MULTILINE)


def _regions(text: str) -> dict[str, tuple[int, int]]:
    """Each top-level key's [start, end) span of the record's raw text."""
    matches = list(TOP_KEY.finditer(text))
    out: dict[str, tuple[int, int]] = {}
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        out.setdefault(m.group(1), (m.start(), end))
    return out


def _render_definition(definition: str | None) -> str:
    if definition is None:
        return "definition: null\n"
    lines: list[str] = []
    line = ""
    for word in definition.split():
        if line and len(line) + 1 + len(word) > WRAP:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}" if line else word
    if line:
        lines.append(line)
    return "definition: >-\n" + "".join(f"  {ln}\n" for ln in lines)


def _render_scalar(value: object) -> str:
    if value is None:
        return "null"
    return f'"{value}"' if " " in str(value) else str(value)


def _render_span(span: dict, indent: str) -> str:
    """One span in house style, at the indentation the record already uses."""
    f = indent + "  "  # fields align after the "- " item introducer
    verified = span.get("verified_against") or {}
    return (
        f"{indent}- doc: {span['doc']}\n"
        f"{f}section: \"{span['section']}\"\n"
        f"{f}para_hash: {span['para_hash']}\n"
        f"{f}origin: {span['origin']}\n"
        f"{f}verified_against:\n"
        f"{f}  git_blob: {verified.get('git_blob')}\n"
        f"{f}  stated_version: {_render_scalar(verified.get('stated_version'))}\n"
    )


def _render_source(intent: Intent, raw_source: str) -> str | None:
    """The new ``source:`` region, keeping every unowned span's exact bytes.

    The existing region is split at its ``- `` item boundaries (whatever
    indentation the record uses, matched for the spans this run appends);
    chunks map to the parsed spans by position, so an unowned span keeps
    whatever quoting and wrapping its author gave it and the diff shows only
    the owned spans. Returns None when the region cannot be split that way.
    """
    old_spans = intent.record.get_list("source")
    items = list(re.finditer(r"^(\s*)- ", raw_source, re.MULTILINE))
    if len(items) != len(old_spans) or not items:
        return None
    indent = items[0].group(1)
    bounds = [m.start() for m in items] + [len(raw_source)]
    chunks = [raw_source[bounds[i] : bounds[i + 1]] for i in range(len(old_spans))]

    keep_ids = {id(s) for s in intent.source}
    kept = [
        chunk
        for span, chunk in zip(old_spans, chunks, strict=True)
        if id(span) in keep_ids
    ]
    new = [
        _render_span(span, indent)
        for span in intent.source
        if not any(span is old for old in old_spans)
    ]
    return "source:\n" + "".join(kept) + "".join(new)


def write_record(intent: Intent) -> list[Finding]:
    """Apply one intent surgically, or say exactly why it cannot be applied.

    The edited text is re-parsed and compared field-for-field against what
    the lift meant to write before it touches disk — so a record this writer
    cannot edit provably-minimally is reported, never silently reformatted.
    """
    record = intent.record
    unwritable = [
        error(
            "lift-unwritable-record",
            record.rel,
            "the record's definition/source regions cannot be edited "
            "surgically — fix its layout (top-level keys at column 0, "
            "spans introduced by '  - ') and re-run `detangle lift`",
        )
    ]
    regions = _regions(record.text)
    if "definition" not in regions or "source" not in regions:
        return unwritable

    d_start, d_end = regions["definition"]
    s_start, s_end = regions["source"]
    rendered_source = _render_source(
        intent, record.text[s_start:s_end]
    )
    if rendered_source is None:
        return unwritable

    pieces = sorted(
        [
            (d_start, d_end, _render_definition(intent.definition)),
            (s_start, s_end, rendered_source),
        ]
    )
    text = record.text
    for start, end, replacement in reversed(pieces):
        text = text[:start] + replacement + text[end:]

    parsed = yaml.safe_load(text)
    intended = dict(record.data)
    intended["definition"] = intent.definition
    intended["source"] = intent.source
    reloaded_def = parsed.get("definition")
    if reloaded_def is not None:
        reloaded_def = " ".join(str(reloaded_def).split())
    if (
        not isinstance(parsed, dict)
        or reloaded_def != intent.definition
        or parsed.get("source") != intent.source
        or {k: v for k, v in parsed.items() if k not in ("definition", "source")}
        != {k: v for k, v in intended.items() if k not in ("definition", "source")}
    ):
        return unwritable

    record.path.write_text(text, encoding="utf-8")
    record.data = parsed
    record.text = text
    return []


def check(intents: list[Intent]) -> list[Finding]:
    """`--check`'s verdict: every pending intent is drift, named per record."""
    return [
        error(
            "lift-drift",
            intent.record.rel,
            "the glossary and this record disagree — the file is canonical "
            "(D9 amendment, 2026-08-04), so run `detangle lift` and commit "
            "the record in the same PR",
        )
        for intent in intents
    ]


def glossary_blob(root: Path, rel: str) -> str:
    """The live blob of the file the run read — what the spans bind."""
    return GitBlobs(root).live(rel)


__all__ = [
    "CHECKS",
    "Entry",
    "Intent",
    "check",
    "compare",
    "glossary_blob",
    "parse_entries",
    "write_record",
]
