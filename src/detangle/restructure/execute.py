"""Executing a reorder plan (ADR-002 Decision 3) — mechanics only.

The renderer implements exactly the transforms the plan declares and nothing
discretionary: source blocks move verbatim; page-split fragments rejoin
cell-wise; declared noise is dropped; declared repairs (whitespace-only,
validated) rejoin split characters; declared render hints apply fixed
presentation transforms. Prose it cannot attribute to the source comes only
from the plan's authored ``additions`` and from the concept records'
definitions — the tool itself writes scaffolding (headings, markers, table
furniture) and no domain prose (C2).

Table parsing: the corpus is pandoc simple/multiline tables whose rows are
blank-line-separated blocks. Column geometry comes from the multi-run ruler
lines; a block with no ruler of its own is sliced by the most recent ruler
seen in source order. The one grid table (the version history) is rendered
by the ``history-list`` hint, because its cells hold whole paragraphs no
pipe row can carry.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..findings import UsageError
from ..records.load import Record
from ..records.spans import block_hash, normalise, split_blocks
from .plan import Plan

WS = re.compile(r"\s+")
#: A line that is only dashes/equals and spaces. One run = a border; two or
#: more runs = a column ruler whose dash spans are the column geometry.
RULE_LINE = re.compile(r"^\s*[-=]+[\s\-=]*$")
RUN = re.compile(r"[-=]+")


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

        gappy = any(
            re.search(r"\S\s{3,}\S", ln) for ln in raw.splitlines()
        )
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
    header: list[str] | None = None
    rows: list[list[str]] = field(default_factory=list)

    def render(self) -> str:
        used = 0
        for cells in ([self.header] if self.header else []) + self.rows:
            for i, cell in enumerate(cells):
                if cell.strip():
                    used = max(used, i + 1)
        width = max(used, 1)
        lines = []
        header = ((self.header or []) + [""] * width)[:width]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("| " + " | ".join(["---"] * width) + " |")
        for row in self.rows:
            padded = (row + [""] * width)[:width]
            lines.append("| " + " | ".join(padded) + " |")
        return "\n".join(lines) + "\n"


def execute(plan: Plan, records: list[Record], source: str) -> str:
    """The restructured document, deterministically, from plan + source."""
    parsed = {b.hash: b for b in parse_blocks(source)}
    by_id = {r.id: r for r in records}

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

    def cells_of(h: str) -> tuple[list[str] | None, list[str] | None]:
        b = parsed[h]
        header = (
            [clean(c, h) for c in _strip_furniture(b.header)] if b.header else None
        )
        row = [clean(c, h) for c in b.row] if b.row else None
        return header, row

    out: list[str] = []
    for section in plan.sections:
        assigned = [a for a in plan.assignments if a.get("section") == section.id]
        defs = [d for d in plan.definitions if d.get("section") == section.id]
        adds = [a for a in plan.additions if a.get("section") == section.id]

        if section.kind == "head":
            for a in assigned:
                for h in plan.blocks_of(a):
                    out.append(parsed[h].raw.strip() + "\n")
            continue
        out.append(f"<!-- sec:{section.id} -->\n## {section.title}\n")

        for a in adds:
            if a.get("form") != "ai-addition-section":
                raise UsageError(f"unknown addition form {a.get('form')!r}")
            out.append(
                '<!-- AI addition:start scope="section" -->\n'
                + str(a["text"]).strip()
                + "\n<!-- AI addition:end -->\n"
            )
        if section.kind == "generated" and defs and not adds:
            out.append(
                "Definitions used in more than one section of this document, "
                "in dependency\norder — a term is defined before any "
                "definition below uses it.\n"
            )
        for d in defs:
            out.append(_definition_block(by_id[d["record"]]))

        table: _Table | None = None

        def flush_table() -> None:
            nonlocal table
            if table is not None:
                out.append(table.render())
                table = None

        for a in assigned:
            hashes = plan.blocks_of(a)
            hint = a.get("render")
            first = parsed[hashes[0]]
            sub = a.get("subheading")
            if sub:
                flush_table()
                out.append(str(sub).strip() + "\n")

            if hint == "history-list":
                flush_table()
                rows = first.grid_rows or []
                for cells in rows[1:] if len(rows) > 1 else rows:
                    cells = [c for c in cells]
                    version = WS.sub(" ", cells[0]).strip().strip("*")
                    date = WS.sub(" ", cells[1]).strip()
                    out.append(f"**{version} --- {date}**\n")
                    for para in cells[2].split("\n\n"):
                        out.append(clean(para, hashes[0]) + "\n")
                continue
            if hint == "part-row":
                lines = [
                    ln for ln in first.raw.splitlines() if not RULE_LINE.match(ln)
                ]
                content = WS.sub(" ", " ".join(lines)).strip()
                m = re.match(r"PART\s+(\S+)\s+(.*)$", content)
                if not m:
                    raise UsageError(f"part-row block does not parse: {content!r}")
                if table is None:
                    table = _Table(header=["Part", "Content"])
                table.rows.append([m.group(1), clean(m.group(2), hashes[0])])
                continue
            if hint == "note-italic":
                flush_table()
                note = " ".join(first.header or [])
                out.append(f"*{clean(note, hashes[0])}*\n")
                continue

            tabular = any(parsed[h].row for h in hashes)
            if not tabular:
                flush_table()
                for h in hashes:
                    out.append(clean(parsed[h].raw, h) + "\n")
                continue

            header, row = cells_of(hashes[0])
            for h in hashes[1:]:
                _extra_header, extra_row = cells_of(h)
                if extra_row:
                    row = _join_cells(
                        [row or [], extra_row], max(len(row or []), len(extra_row))
                    )
            if table is None:
                table = _Table(header=header)
            if row and any(row):
                table.rows.append(row)
        flush_table()

    return "\n".join(part.rstrip("\n") + "\n" for part in out if part.strip())


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


__all__ = ["CHECKS", "check_current", "execute", "parse_blocks"]
