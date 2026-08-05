"""The word tokens criterion 5 counts, and nothing else.

One tokenizer, used by the renderer (to tell a duplicated table header from
a different one) and by the parity check (to compare source against output).
It drops what markdown and pandoc contribute — escape backslashes, pipe and
rule furniture, emphasis markers — and keeps everything a reader would call
a word, including codes, numbers, operators and punctuation-bearing tokens
such as ``(0--24.3)``. Being generous is the point: a token this splitter
throws away is a token the parity check cannot notice going missing.
"""

from __future__ import annotations

import re
from collections import Counter

#: Characters that only ever carry table/markdown structure. A token made
#: exclusively of these is furniture; one containing anything else is a word.
FURNITURE = set("-=+|_*> #")


def tokens(text: str) -> Counter:
    """Multiset of word tokens in ``text``."""
    out: Counter = Counter()
    for word in text.replace("\\", "").split():
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


__all__ = ["FURNITURE", "same_words", "tokens"]
