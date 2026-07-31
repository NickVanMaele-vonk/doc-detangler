"""Markdown table well-formedness (ADR-001 Decision 4, command 1).

An edit in PR #65 silently collapsed a four-column row to three by dropping a
leading ``|``, and it survived review. **The cell count must be taken after
removing escaped ``\\|``** — an escaped pipe is literal content, not a
separator. The ad-hoc ``awk`` check used during that PR did not do this and
false-flagged an untouched row in ``concepts/README.md``, which is exactly the
kind of noise that trains a reviewer to ignore the check.
"""

from __future__ import annotations

import re
from pathlib import Path

from .findings import Finding, error

ESCAPED_PIPE = re.compile(r"\\\|")
FENCE = re.compile(r"^\s*(```|~~~)")
PLACEHOLDER = "\x00"


def cell_count(line: str) -> int:
    """Cells in a pipe-table row, escaped pipes counted as content.

    The outer pipes delimit rather than separate, so the empty strings they
    produce at either end are dropped.
    """
    masked = ESCAPED_PIPE.sub(PLACEHOLDER, line.strip())
    parts = masked.split("|")
    if parts and not parts[0].strip():
        parts = parts[1:]
    if parts and not parts[-1].strip():
        parts = parts[:-1]
    return len(parts)


def _is_table_line(line: str) -> bool:
    """A row of a pipe table, including one that has lost its leading pipe.

    Requiring a leading ``|`` would miss the exact defect this check exists for
    — PR #65 dropped a leading pipe, which is what collapsed the row — so a
    line that merely *ends* with a pipe counts too, and then reports one cell
    short against the header.
    """
    stripped = ESCAPED_PIPE.sub(PLACEHOLDER, line.strip())
    if stripped.count("|") < 2:
        return False
    return stripped.startswith("|") or stripped.endswith("|")


def check_text(text: str, where: str) -> list[Finding]:
    """Every row of a contiguous table must have the same cell count."""
    out: list[Finding] = []
    in_fence = False
    table: list[tuple[int, str]] = []

    def flush() -> None:
        if len(table) < 2:
            table.clear()
            return
        header_line, header = table[0]
        expected = cell_count(header)
        for lineno, row in table[1:]:
            found = cell_count(row)
            if found != expected:
                out.append(
                    error(
                        "table-cell-count",
                        f"{where}:{lineno}",
                        f"{found} cells, but the table's header row "
                        f"(line {header_line}) has {expected}",
                    )
                )
        table.clear()

    for lineno, line in enumerate(text.splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            flush()
            continue
        if in_fence:
            continue
        if _is_table_line(line):
            table.append((lineno, line))
        else:
            flush()
    flush()
    return out


def check_files(root: Path, globs: list[str]) -> list[Finding]:
    """Run the check over every file matched by the configured globs."""
    out: list[Finding] = []
    seen: set[Path] = set()
    for pattern in globs:
        for path in sorted(root.glob(pattern)):
            if not path.is_file() or path in seen:
                continue
            seen.add(path)
            out.extend(
                check_text(
                    path.read_text(encoding="utf-8"), str(path.relative_to(root))
                )
            )
    return out
