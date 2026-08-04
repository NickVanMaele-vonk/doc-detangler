"""Generated views over the concept records (ADR-001 Decision 3, ``views/``).

D9 makes the records canonical and ``glossary.md`` / ``index.md`` /
``concept-graph.mmd`` derived: every word in a view traces to a record field,
so a view is regenerated rather than edited and a hand-edit is a CI failure.
Only the glossary is built — plan step 3.5 scopes ``index.md`` to the arrival
of the document bodies and leaves the Mermaid render its own scoping decision.
"""

from .glossary import Glossary, build, check_current, render

__all__ = ["Glossary", "build", "check_current", "render"]
