"""Phase 7 verification harness (ADR-003).

Build step 1: the claim decomposer and the claim-split override register.
Build step 2: coverage stage 1, the deterministic match (Decision 2), and
concept-before-use over the reading order (Decision 4).
The `detangle verify` command composes these once Decision 5 is ruled.
"""

from .claims import DECOMPOSER_VERSION, Anomaly, Claim, Decomposition, decompose
from .coverage import VERBATIM, Coverage, Match, match
from .splits import CHECKS as SPLIT_CHECKS
from .splits import SplitEntry, load_splits
from .structure import CHECKS as STRUCTURE_CHECKS
from .structure import Document, ForwardUse, Position, Structure, scan

__all__ = [
    "DECOMPOSER_VERSION",
    "Anomaly",
    "Claim",
    "Coverage",
    "Decomposition",
    "Match",
    "VERBATIM",
    "decompose",
    "match",
    "SPLIT_CHECKS",
    "STRUCTURE_CHECKS",
    "Document",
    "ForwardUse",
    "Position",
    "Structure",
    "scan",
    "SplitEntry",
    "load_splits",
]
