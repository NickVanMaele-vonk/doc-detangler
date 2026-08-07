"""The word tokens criterion 5 counts, and nothing else.

One tokenizer, used by the renderer (to tell a duplicated table header from
a different one) and by the parity check (to compare source against output).
It drops what markdown and pandoc contribute — escape backslashes, pipe and
rule furniture, emphasis markers — and keeps everything a reader would call
a word, including codes, numbers, operators and punctuation-bearing tokens
such as ``(0--24.3)``. Being generous is the point: a token this splitter
throws away is a token the parity check cannot notice going missing.

The one deliberate exception is the tool's own markers — ADR-004 Decision 9,
ruled by Nick 2026-08-07. See ``COMMENT``.
"""

from __future__ import annotations

import re
from collections import Counter

#: Characters that only ever carry table/markdown structure. A token made
#: exclusively of these is furniture; one containing anything else is a word.
FURNITURE = set("-=+|_*> #")

#: An HTML comment: the shape every tool-stamped marker takes — ``sec:``,
#: ``concept:``, ``AI addition:``, ``omitted``. Removed before counting, per
#: ADR-004 Decision 9.
#:
#: The reason is that ``para_hash`` already treats a marker as metadata —
#: blocks are normalised through ``pandoc -t plain``, whose plain writer drops
#: raw HTML — so counting markers here made the project's two content
#: measures disagree about what content is. That cost nothing while the input
#: was always an unmarked document. In a re-run the input is the previous
#: run's marked output, so every marker becomes a *source* token that
#: criterion 5 would demand back — while the renderer re-emits its own markers
#: from the plan and the records rather than copying them, and does so as
#: authored parts the parity check never counts. The result would be a wall of
#: findings about hidden comments, none of them about lost wording.
#:
#: Only the comment goes. **Visible text still counts**, including the
#: ``[AI addition]`` tag, on both the alignment argument and the 2026-08-05
#: "ink on the page counts" ruling: pandoc keeps visible text, so keeping it
#: here is what agreement with ``para_hash`` actually requires.
COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def tokens(text: str) -> Counter:
    """Multiset of word tokens in ``text``."""
    out: Counter = Counter()
    for word in COMMENT.sub(" ", text).replace("\\", "").split():
        word = word.strip("|*_").strip()
        if word and not set(word) <= FURNITURE:
            out[word] += 1
    return out


def _squash(text: str) -> str:
    return re.sub(r"[\s\\|*_]+", "", text)


def same_words(a: str, b: str) -> bool:
    """Do two strings carry the same words?

    Same tokens, or the same characters once spacing and markdown emphasis
    are removed. The second limb matters because the OCR splits words
    (``St ep``) and the plan repairs the copy it keeps but not the copies it
    drops: ``St ep`` and ``Step`` are the same header, by the same
    whitespace-only test ``plan-repair-unsafe`` uses on repairs.
    """
    return tokens(a) == tokens(b) or _squash(a) == _squash(b)


__all__ = ["COMMENT", "FURNITURE", "same_words", "tokens"]
