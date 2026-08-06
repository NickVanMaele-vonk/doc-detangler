"""Phase 7 verification harness (ADR-003).

Build step 1: the claim decomposer and the claim-split override register.
The `detangle verify` command arrives with build step 2 and composes these.
"""

from .claims import DECOMPOSER_VERSION, Anomaly, Claim, Decomposition, decompose
from .splits import CHECKS as SPLIT_CHECKS
from .splits import SplitEntry, load_splits

__all__ = [
    "DECOMPOSER_VERSION",
    "Anomaly",
    "Claim",
    "Decomposition",
    "decompose",
    "SPLIT_CHECKS",
    "SplitEntry",
    "load_splits",
]
