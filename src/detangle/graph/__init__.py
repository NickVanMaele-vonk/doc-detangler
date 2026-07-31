"""The concept graph (ADR-001 Decision 3, ``graph/``).

Edges run ``X -> Y`` for "the definition of X uses term Y", which is the
direction ``depends_on`` is written in and the direction criterion 1's formal
check is stated in. Reading order is therefore a topological sort of the
*reverse* graph: a term is defined before the definitions that use it.
"""

from .build import ConceptGraph, build
from .emit import render

__all__ = ["ConceptGraph", "build", "render"]
