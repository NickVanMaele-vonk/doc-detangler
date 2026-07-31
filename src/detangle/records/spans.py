"""Source-span anchoring: block splitting, pandoc normalisation, para_hash.

The scheme is normative in ``concepts/README.md`` §Source-span anchoring and
was approved 2026-07-28. It is reimplemented here exactly, because every one
of the 358 records was authored against it:

    split the file on blank lines; for each block run
    ``pandoc -f markdown -t plain --wrap=none``, collapse whitespace runs to
    single spaces, trim, and sha256 the result.

Hashes are tripwires, never pointers (D10 §2): a mismatch means the span needs
re-verification, not that the record is wrong.
"""

from __future__ import annotations

import hashlib
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from ..findings import UsageError

BLOCK_SPLIT = re.compile(r"\n\s*\n")
WHITESPACE = re.compile(r"\s+")
PANDOC = ["pandoc", "-f", "markdown", "-t", "plain", "--wrap=none"]


def split_blocks(text: str) -> list[str]:
    """Blank-line separated blocks, in document order, empties dropped."""
    return [b for b in BLOCK_SPLIT.split(text) if b.strip()]


def normalise(block: str) -> str:
    """Pandoc plain rendering with whitespace collapsed — what gets hashed."""
    try:
        proc = subprocess.run(
            PANDOC, input=block, capture_output=True, text=True, check=True
        )
    except FileNotFoundError as exc:  # pandoc is a hard dependency (ADR-001 D3)
        raise UsageError("pandoc not found on PATH; it is a hard dependency") from exc
    except subprocess.CalledProcessError as exc:
        raise UsageError(f"pandoc failed: {exc.stderr.strip()}") from exc
    return WHITESPACE.sub(" ", proc.stdout).strip()


def block_hash(normalised: str) -> str:
    return "sha256:" + hashlib.sha256(normalised.encode("utf-8")).hexdigest()


@dataclass
class Document:
    """One source file's blocks, keyed by para_hash."""

    path: Path
    by_hash: dict[str, str]

    def text_for(self, para_hash: str) -> str | None:
        return self.by_hash.get(para_hash)


@dataclass
class BlockIndex:
    """Lazily hashes each source document once per run.

    Hashing the corpus costs a pandoc process per block (~600 blocks across
    ``samples/``), so documents are indexed on first use and only the documents
    actually cited by the records under validation are ever touched.
    """

    root: Path
    _docs: dict[str, Document] = field(default_factory=dict)

    def document(self, rel_doc: str) -> Document:
        if rel_doc not in self._docs:
            path = self.root / rel_doc
            if not path.is_file():
                raise UsageError(f"source document not found: {rel_doc}")
            by_hash = {}
            for block in split_blocks(path.read_text(encoding="utf-8")):
                normalised = normalise(block)
                by_hash[block_hash(normalised)] = normalised
            self._docs[rel_doc] = Document(path=path, by_hash=by_hash)
        return self._docs[rel_doc]
