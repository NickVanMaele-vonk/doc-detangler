"""Claim decomposition — ADR-003 Decision 1, build step 1.

The granularity rule is ``param-claim-granularity`` (rubric §Parameters): one
claim per prose sentence, one per table cell carrying an independent
assertion — header rows and grid rules are furniture, not claims. The 5.3
baseline applied the rule by hand to ``U`` and counted 289 claims (23 prose
sentences + 266 assertion-bearing cells); this module applies it mechanically,
and reproducing that count is held as a test.

Determinism is the point (research-memo §2.8: the decomposer moves the
scores). Same input plus same overrides gives the same claim list;
``DECOMPOSER_VERSION`` and the override register's blob go into every
verification report, so our figures are internally comparable only — never
against published FActScore numbers.

What the splitter cannot confidently split it **flags**, never guesses at.
The flags are the work-list for the LLM-assisted override pass (Nick's
2026-08-06 ruling on ADR-003 Decision 1): judgment lands as committed entries
in the claim-split register, reviewed by PR, and this module *executes* those
entries — the ADR-002 pattern one level down. No model is ever called here.

Structure comes from **one whole-document pandoc parse**, not from parsing
blank-line blocks one at a time: the corpus is full of multiline tables whose
rows are blank-line separated, so a per-block parse shatters them into prose
and loses every cell (measured: 38 cells where the hand count found 266).
Anchoring still follows the ``para_hash`` block convention — each claim is
tied back to its blank-line block by ordered token containment, so claim IDs
are hash-anchored, never line numbers (D10): ``doc:hash8:occ:n``, where
``hash8`` prefixes the block's ``para_hash``, ``occ`` disambiguates identical
blocks in document order, and ``n`` counts claims within the block. A
sub-claim minted by an override is ``…:n/i``.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field

from ..findings import UsageError
from ..records.spans import WHITESPACE, block_hash, normalise, split_blocks

#: Bump on any change that can move a claim count (research-memo §2.8).
DECOMPOSER_VERSION = "1.0"

#: v1 flagging heuristics, to be calibrated by the Decision 7 dry-run. A cell
#: with a couple of sentences is normal under the one-claim-per-cell rule;
#: these mark the spans a human should look at, not everything imperfect.
OVERLONG_WORDS = 60
MULTI_ASSERTION_SENTENCES = 4

#: Leading tokens of a containment key — enough to be unique, short enough
#: that a claim is findable inside its (much longer) block rendering.
ANCHOR_KEY_TOKENS = 8

PANDOC_JSON = ["pandoc", "-f", "markdown", "-t", "json"]

#: A letter, then ``- ``, then a letter: the OCR-broken-hyphen shape
#: (``MEDIUM- INVESTIGATE``, the family-A source defects). En/em dashes and
#: spaced hyphens (`` - ``) do not match.
BROKEN_HYPHEN = re.compile(r"[A-Za-z]- [A-Za-z]")

GRID_LINE = re.compile(r"^\s*\+[-=+]+\+\s*$", re.M)
PIPE_ROW = re.compile(r"^\s*\|.*\|\s*$", re.M)
TOKEN = re.compile(r"[a-z0-9]+")

#: A cell starting with a bare lowercase word is usually the tail of a row
#: the OCR page break cut ("independently tested", "readiness.") — unless the
#: word is code-shaped (``bci_score``, ``rsa_scaled``), which legitimately
#: starts lowercase. Measured on ``U``: this catches every shard of the
#: page-split rows the golden rejoins.
FRAGMENT_START = re.compile(r"^[a-z]+\b(?![_.\w]*[_0-9])")

#: Top-level pandoc blocks whose text is prose to sentence-split. ``Header``,
#: ``HorizontalRule`` and ``RawBlock`` are furniture; ``CodeBlock`` content is
#: not prose and the granularity rule assigns it no claims.
PROSE_BLOCKS = frozenset(
    {"Para", "Plain", "LineBlock", "BlockQuote", "BulletList", "OrderedList",
     "DefinitionList"}
)

#: Words that end with a period without ending a sentence. Single letters
#: (initials) and bare numbers (enumerators, "1.") are guarded separately.
ABBREVIATIONS = frozenset(
    {"e.g", "i.e", "etc", "vs", "cf", "viz", "approx", "no", "resp"}
)

#: A sentence boundary candidate: terminal punctuation (plus any closing
#: quotes/brackets), then whitespace, then something that looks like a
#: sentence opener. The preceding word is checked against the guards.
SENTENCE_BOUNDARY = re.compile(r"[.?!][\"'”’)\]]*(?=\s+[\"'“‘(\[]*[A-Z0-9§])")
TERMINAL_END = re.compile(r"[.?!][\"'”’)\]]*$")
LAST_WORD = re.compile(r"([\w§.&/–—-]+)[.?!][\"'”’)\]]*$")


def split_sentences(text: str) -> list[str]:
    """Sentences of ``text`` that end in terminal punctuation.

    A fragment with no terminal punctuation — a title, a label, a line ending
    in a colon — is not a sentence and yields no claim, which is what drops
    front-matter furniture without a special case.
    """
    text = text.strip()
    if not text:
        return []
    pieces: list[str] = []
    start = 0
    for match in SENTENCE_BOUNDARY.finditer(text):
        piece = text[start : match.end()]
        word = LAST_WORD.search(piece)
        if word:
            w = word.group(1).lower().rstrip(".")
            if (
                w in ABBREVIATIONS
                or (len(w) == 1 and w.isalpha())
                or w.isdigit()  # an enumerator ("1.") is a prefix, not a sentence
            ):
                continue
        pieces.append(piece.strip())
        start = match.end()
    tail = text[start:].strip()
    if tail:
        pieces.append(tail)
    return [p for p in pieces if TERMINAL_END.search(p)]


@dataclass(frozen=True)
class Claim:
    id: str
    doc: str
    kind: str  # "prose" | "cell" | "override"
    text: str
    para_hash: str
    flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class Anomaly:
    """A tabular-looking block no claim anchored to.

    Its content is invisible to the harness until an override supplies claims
    for it (by ``block`` key) or a human rules it furniture; this entry is
    what says so.
    """

    block: str
    para_hash: str
    reason: str
    text: str


@dataclass
class Decomposition:
    doc: str
    version: str
    claims: list[Claim] = field(default_factory=list)
    anomalies: list[Anomaly] = field(default_factory=list)
    #: Override targets that matched nothing — the future `verify` command
    #: raises these as stale-entry findings (the waiver-stale precedent).
    unused_splits: list[str] = field(default_factory=list)


def _collapse(text: str) -> str:
    return WHITESPACE.sub(" ", text).strip()


def _tokens(text: str) -> str:
    return " ".join(TOKEN.findall(text.lower()))


def _inlines(inlines: list) -> str:
    return "".join(_inline_text(i) for i in inlines)


def _inline_text(inline: dict) -> str:
    t = inline["t"]
    c = inline.get("c")
    if t == "Str":
        return c
    if t in ("Space", "SoftBreak", "LineBreak"):
        return " "
    if t in ("Emph", "Underline", "Strong", "Strikeout", "Superscript",
             "Subscript", "SmallCaps"):
        return _inlines(c)
    if t in ("Quoted", "Cite", "Link", "Image", "Span"):
        return _inlines(c[1])
    if t in ("Code", "Math"):
        return c[1]
    return ""  # RawInline, Note


def _blocks_text(blocks: list) -> str:
    return " ".join(filter(None, (_block_text(b) for b in blocks)))


def _block_text(block: dict) -> str:
    t = block["t"]
    c = block.get("c")
    if t in ("Para", "Plain"):
        return _inlines(c)
    if t == "LineBlock":
        return " ".join(_inlines(line) for line in c)
    if t == "CodeBlock":
        return c[1]
    if t == "BlockQuote":
        return _blocks_text(c)
    if t == "BulletList":
        return " ".join(_blocks_text(item) for item in c)
    if t == "OrderedList":
        return " ".join(_blocks_text(item) for item in c[1])
    if t == "DefinitionList":
        parts = []
        for term, defs in c:
            parts.append(_inlines(term))
            parts.extend(_blocks_text(d) for d in defs)
        return " ".join(parts)
    return ""  # Header, HorizontalRule, RawBlock, Table-in-cell


def _document_ast(text: str) -> list:
    """Pandoc's block list for the whole document.

    A whole-document parse failure is fatal: unlike a single damaged block
    there is nothing to fall back to, and a silent partial read would make
    every count wrong.
    """
    try:
        proc = subprocess.run(
            PANDOC_JSON, input=text, capture_output=True, text=True, check=True
        )
    except FileNotFoundError as exc:  # pandoc is a hard dependency (ADR-001 D3)
        raise UsageError("pandoc not found on PATH; it is a hard dependency") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip()
        raise UsageError(f"pandoc failed on the document: {detail}") from exc
    try:
        return json.loads(proc.stdout)["blocks"]
    except (json.JSONDecodeError, KeyError) as exc:
        raise UsageError(f"unreadable pandoc JSON: {exc}") from exc


def _table_cells(c: list) -> list[str]:
    """Non-furniture cell texts: body-row cells, in reading order.

    Header rows (``TableHead``), per-body intermediate header rows, and the
    footer are furniture per the 5.3 counting rule. Empty cells carry no
    assertion and are dropped.
    """
    _attr, _caption, _colspecs, _head, bodies, _foot = c
    out: list[str] = []
    for body in bodies:
        for row in body[3]:
            for cell in row[1]:
                text = _collapse(_blocks_text(cell[4]))
                if text:
                    out.append(text)
    return out


def _flags(text: str, kind: str) -> tuple[str, ...]:
    flags: list[str] = []
    if BROKEN_HYPHEN.search(text):
        flags.append("broken-hyphen")
    if len(text.split()) > OVERLONG_WORDS:
        flags.append("overlong")
    if kind == "cell":
        if len(split_sentences(text)) >= MULTI_ASSERTION_SENTENCES:
            flags.append("multi-assertion")
        if FRAGMENT_START.match(text):
            flags.append("fragment-suspect")
    return tuple(flags)


@dataclass
class _Block:
    index: int
    key: str  # doc:hash8:occ
    para_hash: str
    token_text: str  # for containment matching
    plain: str
    tabular: bool
    n_claims: int = 0


def _index_blocks(text: str, doc: str) -> list[_Block]:
    occurrences: dict[str, int] = {}
    out: list[_Block] = []
    for i, block in enumerate(split_blocks(text)):
        plain = normalise(block)
        para_hash = block_hash(plain)
        h8 = para_hash.removeprefix("sha256:")[:8]
        occ = occurrences.get(h8, 0)
        occurrences[h8] = occ + 1
        out.append(
            _Block(
                index=i,
                key=f"{doc}:{h8}:{occ}",
                para_hash=para_hash,
                token_text=f" {_tokens(plain)} ",
                plain=plain,
                tabular=bool(GRID_LINE.search(block) or PIPE_ROW.search(block)),
            )
        )
    return out


def _anchor(blocks: list[_Block], claim_text: str, cursor: int) -> int | None:
    """Index of the first block at or after ``cursor`` containing the claim.

    Claims arrive in document order (the AST walk preserves it), so the
    search never looks backwards and anchoring stays monotonic.
    """
    key_tokens = TOKEN.findall(claim_text.lower())[:ANCHOR_KEY_TOKENS]
    if not key_tokens:
        return None
    key = f" {' '.join(key_tokens)} "
    for j in range(cursor, len(blocks)):
        if key in blocks[j].token_text:
            return j
    return None


def decompose(text: str, doc: str, splits: list | None = None) -> Decomposition:
    """Split one source document into claims, applying any override entries.

    ``splits`` is the loaded claim-split register (``splits.load_splits``).
    Entries key on the machine claim or block they replace, so the walk
    applies them in place and the result stays in document order.
    """
    entries = {e.target: e for e in (splits or [])}
    used: set[str] = set()
    result = Decomposition(doc=doc, version=DECOMPOSER_VERSION)
    blocks = _index_blocks(text, doc)

    # The claim stream, in document order, from the whole-document parse.
    stream: list[tuple[str, str]] = []
    for node in _document_ast(text):
        if node["t"] == "Table":
            stream += [("cell", t) for t in _table_cells(node["c"])]
        elif node["t"] in PROSE_BLOCKS:
            stream += [
                ("prose", s) for s in split_sentences(_collapse(_block_text(node)))
            ]

    def emit(block: _Block, kind: str, claim_text: str, extra: tuple[str, ...]) -> None:
        block.n_claims += 1
        claim_id = f"{block.key}:{block.n_claims}"
        if claim_id in entries:
            entry = entries[claim_id]
            used.add(claim_id)
            for i, sub in enumerate(entry.into, start=1):
                sub = _collapse(sub)
                result.claims.append(
                    Claim(f"{claim_id}/{i}", doc, kind, sub, block.para_hash,
                          _flags(sub, kind))
                )
            return
        result.claims.append(
            Claim(claim_id, doc, kind, claim_text, block.para_hash,
                  _flags(claim_text, kind) + extra)
        )

    cursor = 0
    overridden: set[str] = set()
    taken: dict[int, set[str]] = {}
    for kind, claim_text in stream:
        j = _anchor(blocks, claim_text, cursor)
        if j is not None and claim_text in taken.get(j, set()):
            # This exact text already anchored here: an identical block later
            # in the document is the likelier home (blocks can repeat — page
            # headers did in the full corpus). Fall back if there is none.
            j = _anchor(blocks, claim_text, j + 1) or j
        if j is not None:
            taken.setdefault(j, set()).add(claim_text)
        if j is None:
            # Unanchorable: keep the claim rather than lose it, tied to the
            # current block and flagged for the override work-list.
            emit(blocks[cursor], kind, claim_text, ("anchor-unresolved",))
            continue
        cursor = j
        block = blocks[j]
        if block.key in entries:
            # A block-level override supplies this block's claims outright,
            # once, in place of everything the machine anchored to it.
            if block.key not in overridden:
                overridden.add(block.key)
                used.add(block.key)
                for i, sub in enumerate(entries[block.key].into, start=1):
                    sub = _collapse(sub)
                    result.claims.append(
                        Claim(f"{block.key}:{i}", doc, "override", sub,
                              block.para_hash, _flags(sub, "override"))
                    )
            continue
        emit(block, kind, claim_text, ())

    for block in blocks:
        if block.tabular and block.n_claims == 0 and block.key not in overridden:
            if not block.plain:
                continue  # a bare grid rule renders to nothing: furniture
            if block.key in entries:
                used.add(block.key)
                for i, sub in enumerate(entries[block.key].into, start=1):
                    sub = _collapse(sub)
                    result.claims.append(
                        Claim(f"{block.key}:{i}", doc, "override", sub,
                              block.para_hash, _flags(sub, "override"))
                    )
                continue
            result.anomalies.append(
                Anomaly(block.key, block.para_hash, "no-claims-anchored",
                        _collapse(block.plain))
            )

    result.unused_splits = sorted(set(entries) - used)
    return result


__all__ = [
    "DECOMPOSER_VERSION",
    "Anomaly",
    "Claim",
    "Decomposition",
    "decompose",
    "split_sentences",
]
