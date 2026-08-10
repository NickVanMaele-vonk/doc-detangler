"""Executing a reorder plan (ADR-002 Decision 3) — mechanics only.

The renderer implements exactly the transforms the plan declares and nothing
discretionary: source blocks move verbatim; page-split fragments rejoin
cell-wise; declared noise is dropped; declared repairs (whitespace-only,
validated) rejoin split characters; declared render hints apply fixed
presentation transforms. Prose it cannot attribute to the source comes only
from the plan's authored ``additions`` and from the concept records'
definitions — the tool itself writes scaffolding (headings, markers, table
furniture) and no domain prose (C2).

The render is emitted as **provenance-tagged parts**, not one string: every
piece of the output says whether it carries source words or is authored
scaffolding, and which source blocks it came from. That is what lets the
criterion-5 parity check compare like with like instead of re-parsing its
own output, and what the generated move-map reports from.

Anything the renderer discards that is not declared noise is recorded as a
``Drop`` with a reason, verbatim. Nothing leaves the document silently: a
drop is either explained to the parity check or it fails it.

Table parsing: the corpus is pandoc simple/multiline tables whose rows are
blank-line-separated blocks. Column geometry comes from the multi-run ruler
lines; a block with no ruler of its own is sliced by the most recent ruler
seen in source order. The one grid table (the version history) is rendered
by the ``history-list`` hint, because its cells hold whole paragraphs no
pipe row can carry.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass, field, replace

from ..findings import UsageError
from ..records.load import Record
from ..records.spans import block_hash, normalise, split_blocks
from .plan import Plan
from .tokens import same_words

WS = re.compile(r"\s+")
#: A line that is only dashes/equals and spaces. One run = a border; two or
#: more runs = a column ruler whose dash spans are the column geometry.
RULE_LINE = re.compile(r"^\s*[-=]+[\s\-=]*$")
RUN = re.compile(r"[-=]+")

SOURCE = "source"
AUTHORED = "authored"


def _runs(line: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for m in RUN.finditer(line)]


@dataclass
class ParsedBlock:
    """One source block, parsed once, in source order."""

    raw: str
    hash: str
    header: list[str] | None = None  # header row cells, if the block has one
    row: list[str] | None = None  # the block's single data row, if tabular
    grid_rows: list[list[str]] | None = None  # grid-table rows (history)
    prose: str | None = None  # collapsed text, if not tabular


@dataclass(frozen=True)
class Part:
    """One piece of the output, with its provenance.

    ``origin`` is ``source`` when the words come from the document being
    restructured and ``authored`` when they come from anywhere else — the
    plan's Category C additions, a concept record's definition, or the
    tool's own scaffolding. Only source parts are weighed against the source
    by the parity check.
    """

    text: str
    origin: str
    kind: str
    blocks: tuple[str, ...] = ()
    section: str = ""
    #: Join to the previous part with a single newline (a table's rows) rather
    #: than a blank line (a paragraph).
    glue: bool = False


@dataclass(frozen=True)
class Drop:
    """Source text the renderer discarded, recorded verbatim with its reason.

    The reason is what the parity check weighs. Three of them are declared
    transforms — a repeat of a header the output keeps, the header row of a
    grid table the plan asked to render as a headed list, the ``PART`` banner
    word that becomes the index column head — and explain the words away.
    ``dropped-table-header`` is the residual bucket: header-shaped text the
    renderer could not match against any header the output kept. It explains
    nothing, so those words surface as a parity finding.
    """

    text: str
    reason: str
    block: str
    section: str = ""


@dataclass
class Render:
    """The output as parts plus everything discarded on the way."""

    parts: list[Part] = field(default_factory=list)
    drops: list[Drop] = field(default_factory=list)
    #: Table headers the output kept, for classifying header drops at the end.
    kept_headers: list[str] = field(default_factory=list)

    def text(self) -> str:
        out = ""
        for part in self.parts:
            body = part.text.rstrip("\n")
            if not body.strip():
                continue
            if not out:
                out = body
            else:
                out += ("\n" if part.glue else "\n\n") + body
        return out + "\n" if out else ""

    def source_text(self) -> str:
        return "\n".join(p.text for p in self.parts if p.origin == SOURCE)


def _slice(line: str, spans: list[tuple[int, int]]) -> list[str]:
    cells = []
    for i, (start, _end) in enumerate(spans):
        stop = spans[i + 1][0] if i + 1 < len(spans) else len(line)
        cells.append(line[start:stop].strip())
    return cells


def _join_cells(rows: list[list[str]], width: int) -> list[str]:
    out = [""] * width
    for cells in rows:
        for i in range(min(width, len(cells))):
            if cells[i]:
                out[i] = f"{out[i]} {cells[i]}".strip()
    return out


def _parse_grid(raw: str) -> list[list[str]]:
    """Rows of a pandoc grid table: ``+---+`` separators, ``|`` cell walls.

    Blank in-row lines (cells all empty) become paragraph breaks inside the
    cell, which is what lets a version cell carry a whole amendment text.
    """
    rows: list[list[str]] = []
    current: list[list[str]] = []

    def flush() -> None:
        if not current:
            return
        width = max(len(r) for r in current)
        cells = []
        for i in range(width):
            paragraphs: list[str] = []
            para: list[str] = []
            for line_cells in current:
                piece = line_cells[i].strip() if i < len(line_cells) else ""
                if piece:
                    para.append(piece)
                elif para:
                    paragraphs.append(" ".join(para))
                    para = []
            if para:
                paragraphs.append(" ".join(para))
            cells.append("\n\n".join(paragraphs))
        rows.append(cells)
        current.clear()

    for line in raw.splitlines():
        if re.match(r"^\s*\+[-=+]+\+\s*$", line):
            flush()
            continue
        if line.lstrip().startswith("|"):
            current.append(line.strip().strip("|").split("|"))
    flush()
    return rows


def parse_blocks(source: str) -> list[ParsedBlock]:
    """Parse every block once, tracking column geometry in source order."""
    spans: list[tuple[int, int]] = []
    out: list[ParsedBlock] = []
    for raw in split_blocks(source):
        block = ParsedBlock(raw=raw, hash=block_hash(normalise(raw)))
        if re.search(r"^\s*\+[-=]", raw, re.M):
            block.grid_rows = _parse_grid(raw)
            out.append(block)
            continue

        header_lines: list[str] = []
        row_lines: list[str] = []
        own_ruler: list[tuple[int, int]] | None = None
        for line in raw.splitlines():
            if RULE_LINE.match(line):
                runs = _runs(line)
                if len(runs) >= 2:
                    own_ruler = runs
                continue  # borders and rulers are furniture
            (row_lines if own_ruler else header_lines).append(line)

        gappy = any(re.search(r"\S\s{3,}\S", ln) for ln in raw.splitlines())
        if own_ruler is None and (not gappy or not spans):
            block.prose = WS.sub(" ", raw).strip()
            out.append(block)
            continue
        if own_ruler is not None:
            spans = own_ruler
            if header_lines:
                block.header = _join_cells(
                    [_slice(line, spans) for line in header_lines], len(spans)
                )
            lines = row_lines
        else:
            lines = header_lines  # no ruler in this block: all lines are row
        if lines:
            block.row = _join_cells(
                [_slice(line, spans) for line in lines], len(spans)
            )
        out.append(block)
    return out


# -- rendering --------------------------------------------------------------


def _strip_furniture(cells: list[str]) -> list[str]:
    return [WS.sub(" ", c).strip().strip("*").strip() for c in cells]


def cleaner(plan: Plan) -> Callable[[str, str], str]:
    """The plan's declared text transforms, as one function of (text, block).

    Shared with the parity check, so what it measures as "the source, after
    what the plan said to do to it" is exactly what the renderer emitted.
    """
    removals: dict[str, list[str]] = {}
    for entry in plan.inline_removals:
        removals.setdefault(entry["block"], []).append(str(entry["remove"]))
    repairs: dict[str, list[tuple[str, str]]] = {}
    for entry in plan.repairs:
        repairs.setdefault(entry["block"], []).append(
            (str(entry["from"]), str(entry["to"]))
        )

    def clean(text: str, h: str) -> str:
        for needle in removals.get(h, []):
            text = text.replace(needle, "")
        for frm, to in repairs.get(h, []):
            text = text.replace(frm, to)
        # pandoc escape backslashes are markdown syntax, not content
        return WS.sub(" ", text.replace("\\", "")).strip()

    return clean


def _definition_block(record: Record) -> str:
    prose = WS.sub(" ", str(record.data["definition"])).strip()
    head = f"**{record.data.get('term')}**"
    aliases = [str(a) for a in record.get_list("aliases")]
    if aliases:
        head += " (also known as: " + ", ".join(aliases) + ")"
    return (
        f"{head}\n<!-- concept:{record.id}:start -->\n{prose}\n"
        f"<!-- concept:{record.id}:end -->\n"
    )


@dataclass
class _Table:
    """A pipe table under construction, remembering where each row came from."""

    header: list[str] | None = None
    header_origin: str = SOURCE
    header_block: str = ""
    rows: list[tuple[list[str], str]] = field(default_factory=list)

    def parts(self, section: str) -> list[Part]:
        used = 0
        for cells in ([self.header] if self.header else []) + [
            r for r, _ in self.rows
        ]:
            for i, cell in enumerate(cells):
                if cell.strip():
                    used = max(used, i + 1)
        width = max(used, 1)
        header = ((self.header or []) + [""] * width)[:width]
        out = [
            Part(
                text="| " + " | ".join(header) + " |",
                origin=self.header_origin,
                kind="table-header",
                blocks=(self.header_block,) if self.header_block else (),
                section=section,
            ),
            Part(
                text="| " + " | ".join(["---"] * width) + " |",
                origin=AUTHORED,
                kind="table-rule",
                section=section,
                glue=True,
            ),
        ]
        for row, block in self.rows:
            padded = (row + [""] * width)[:width]
            out.append(
                Part(
                    text="| " + " | ".join(padded) + " |",
                    origin=SOURCE,
                    kind="table-row",
                    blocks=(block,),
                    section=section,
                    glue=True,
                )
            )
        return out


def render(plan: Plan, records: list[Record], source: str) -> Render:
    """The restructured document as provenance-tagged parts, deterministically."""
    parsed = {b.hash: b for b in parse_blocks(source)}
    by_id = {r.id: r for r in records}
    clean = cleaner(plan)
    out = Render()

    def cells_of(h: str) -> tuple[list[str] | None, list[str] | None]:
        b = parsed[h]
        header = (
            [clean(c, h) for c in _strip_furniture(b.header)] if b.header else None
        )
        row = [clean(c, h) for c in b.row] if b.row else None
        return header, row

    for section in plan.sections:
        assigned = [a for a in plan.assignments if a.get("section") == section.id]
        defs = [d for d in plan.definitions if d.get("section") == section.id]
        adds = [a for a in plan.additions if a.get("section") == section.id]

        if section.kind == "head":
            for a in assigned:
                for h in plan.blocks_of(a):
                    out.parts.append(
                        Part(
                            text=parsed[h].raw.strip() + "\n",
                            origin=SOURCE,
                            kind="head",
                            blocks=(h,),
                            section=section.id,
                        )
                    )
            continue
        out.parts.append(
            Part(
                text=f"<!-- sec:{section.id} -->\n## {section.title}\n",
                origin=AUTHORED,
                kind="section-heading",
                section=section.id,
            )
        )

        for a in adds:
            if a.get("form") != "ai-addition-section":
                raise UsageError(f"unknown addition form {a.get('form')!r}")
            out.parts.append(
                Part(
                    text='<!-- AI addition:start scope="section" -->\n'
                    + str(a["text"]).strip()
                    + "\n<!-- AI addition:end -->\n",
                    origin=AUTHORED,
                    kind="addition",
                    section=section.id,
                )
            )
        if section.kind == "generated" and defs and not adds:
            out.parts.append(
                Part(
                    text="Definitions used in more than one section of this "
                    "document, in dependency\norder — a term is defined "
                    "before any definition below uses it.\n",
                    origin=AUTHORED,
                    kind="lead",
                    section=section.id,
                )
            )
        for d in defs:
            out.parts.append(
                Part(
                    text=_definition_block(by_id[d["record"]]),
                    origin=AUTHORED,
                    kind="definition",
                    blocks=(),
                    section=section.id,
                )
            )

        table: _Table | None = None

        def flush_table(section_id: str = section.id) -> None:
            nonlocal table
            if table is not None:
                out.parts.extend(table.parts(section_id))
                table = None

        def drop(
            text: str, reason: str, block: str, section_id: str = section.id
        ) -> None:
            if text.strip():
                out.drops.append(
                    Drop(
                        text=text.strip(),
                        reason=reason,
                        block=block,
                        section=section_id,
                    )
                )

        for a in assigned:
            hashes = plan.blocks_of(a)
            hint = a.get("render")
            first = parsed[hashes[0]]
            sub = a.get("subheading")
            if sub:
                flush_table()
                out.parts.append(
                    Part(
                        text=str(sub).strip() + "\n",
                        origin=AUTHORED,
                        kind="subheading",
                        section=section.id,
                    )
                )

            if hint == "history-list":
                flush_table()
                rows = first.grid_rows or []
                if len(rows) > 1:
                    # The grid header row has no place in a headed list.
                    drop(" ".join(rows[0]), "history-table-header", hashes[0])
                    rows = rows[1:]
                for cells in rows:
                    version = WS.sub(" ", cells[0]).strip().strip("*")
                    date = WS.sub(" ", cells[1]).strip()
                    out.parts.append(
                        Part(
                            text=f"**{version} --- {date}**\n",
                            origin=SOURCE,
                            kind="history-head",
                            blocks=(hashes[0],),
                            section=section.id,
                        )
                    )
                    for cell in cells[2:]:
                        for para in cell.split("\n\n"):
                            out.parts.append(
                                Part(
                                    text=clean(para, hashes[0]) + "\n",
                                    origin=SOURCE,
                                    kind="history-body",
                                    blocks=(hashes[0],),
                                    section=section.id,
                                )
                            )
                continue
            if hint == "grid-list":
                # A grid table as a headed list, dropping nothing: the first
                # non-empty cell of each row is the head, every other cell a
                # paragraph. Unlike `history-list` this assumes no header row
                # — the archetype and change-log grids open with content.
                flush_table()
                for cells in first.grid_rows or []:
                    filled = [c for c in cells if c.strip()]
                    if not filled:
                        continue
                    head = clean(filled[0], hashes[0]).strip("*").strip()
                    out.parts.append(
                        Part(
                            text=f"**{head}**\n",
                            origin=SOURCE,
                            kind="grid-head",
                            blocks=(hashes[0],),
                            section=section.id,
                        )
                    )
                    for cell in filled[1:]:
                        for para in cell.split("\n\n"):
                            out.parts.append(
                                Part(
                                    text=clean(para, hashes[0]) + "\n",
                                    origin=SOURCE,
                                    kind="grid-body",
                                    blocks=(hashes[0],),
                                    section=section.id,
                                )
                            )
                continue
            if hint == "part-row":
                lines = [
                    ln for ln in first.raw.splitlines() if not RULE_LINE.match(ln)
                ]
                # Emphasis is presentation, not content: some banners are
                # bold, and the row carries the words either way.
                content = WS.sub(" ", " ".join(lines)).replace("**", "").strip()
                m = re.match(r"(PART|SECTION)\s+(\S+)\s+(.*)$", content)
                if not m:
                    raise UsageError(f"part-row block does not parse: {content!r}")
                # "PART"/"SECTION" is the banner's own label; the row keeps
                # the part number and its title.
                drop(m.group(1), "part-row-label", hashes[0])
                if table is None:
                    # Headerless on purpose: the index table's real header is
                    # a source block further down, and the tool does not write
                    # column names of its own.
                    table = _Table()
                table.rows.append(
                    ([m.group(2), clean(m.group(3), hashes[0])], hashes[0])
                )
                continue
            if hint == "note-italic":
                flush_table()
                note = " ".join(first.header or [])
                if first.row:
                    drop(" ".join(first.row), "table-header", hashes[0])
                out.parts.append(
                    Part(
                        text=f"*{clean(note, hashes[0])}*\n",
                        origin=SOURCE,
                        kind="note",
                        blocks=(hashes[0],),
                        section=section.id,
                    )
                )
                continue

            tabular = any(parsed[h].row for h in hashes)
            if not tabular:
                flush_table()
                for h in hashes:
                    # Rule lines glued to a prose block are the same table
                    # furniture the tabular path drops.
                    body = "\n".join(
                        ln
                        for ln in parsed[h].raw.splitlines()
                        if not RULE_LINE.match(ln)
                    )
                    out.parts.append(
                        Part(
                            text=clean(body, h) + "\n",
                            origin=SOURCE,
                            kind="prose",
                            blocks=(h,),
                            section=section.id,
                        )
                    )
                continue

            header, row = cells_of(hashes[0])
            for h in hashes[1:]:
                extra_header, extra_row = cells_of(h)
                if extra_header:
                    # A fragment's own header repeats the table's; the kept
                    # header is always the first fragment's, so this one goes.
                    drop(" ".join(extra_header), "table-header", h)
                if extra_row:
                    row = _join_cells(
                        [row or [], extra_row], max(len(row or []), len(extra_row))
                    )
            if table is None:
                table = _Table(header=header, header_block=hashes[0] if header else "")
                if header:
                    out.kept_headers.append(" ".join(header))
            elif header and table.header is None:
                # A table opened by a render hint takes the first header the
                # source offers, rather than one the tool invented.
                table.header, table.header_block = header, hashes[0]
                out.kept_headers.append(" ".join(header))
            elif header:
                # A page-split table repeats its header on every page; one is
                # kept and the repeats are furniture. Whether this really is a
                # repeat is settled after the render, against every header the
                # output kept — one that matches none is not explained away.
                drop(" ".join(header), "table-header", hashes[0])
            if row and any(row):
                table.rows.append((row, hashes[0]))
        flush_table()

    _classify_header_drops(out)
    return out


def _classify_header_drops(rendered: Render) -> None:
    """Settle every ``table-header`` drop against the headers the output kept.

    Order-independent on purpose: a repeated header can be discarded before
    the run has seen the copy it repeats, and "is this the same header?" is a
    question about the finished document, not about where the renderer was.
    """
    for i, drop in enumerate(rendered.drops):
        if drop.reason != "table-header":
            continue
        repeat = any(same_words(drop.text, kept) for kept in rendered.kept_headers)
        rendered.drops[i] = replace(
            drop,
            reason="repeated-table-header" if repeat else "dropped-table-header",
        )


def execute(plan: Plan, records: list[Record], source: str) -> str:
    """The restructured document, deterministically, from plan + source."""
    return render(plan, records, source).text()


#: Split like the glossary's: a write run and a --check run raise different
#: things. Drift on a derived output is never waivable (C6 policy).
CHECKS = frozenset({"restructure-drift", "restructure-missing"})


def check_current(text: str, path, rel: str) -> list:
    """Bytes, not structure — the guard every derived artifact carries."""
    from ..findings import error

    if not path.is_file():
        return [
            error(
                "restructure-missing",
                rel,
                "no restructured document on disk; run `detangle restructure` "
                "and commit the result",
            )
        ]
    if path.read_text(encoding="utf-8") != text:
        return [
            error(
                "restructure-drift",
                rel,
                "the committed document differs from a re-execution of the "
                "plan — it was hand-edited, or the plan/source/records "
                "changed without re-running `detangle restructure`",
            )
        ]
    return []


__all__ = [
    "AUTHORED",
    "CHECKS",
    "SOURCE",
    "Drop",
    "ParsedBlock",
    "Part",
    "Render",
    "check_current",
    "cleaner",
    "execute",
    "parse_blocks",
    "render",
]
