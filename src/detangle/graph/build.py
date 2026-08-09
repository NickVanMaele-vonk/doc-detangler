"""Building and analysing the concept graph (ADR-001 Decision 4, command 2).

The canonical input is the records' ``depends_on`` (D9/D10); the cycle
dispositions come from ``registers/cycles.yaml`` (ADR-001 Decision 6).
Everything this module computes — reading order, cycles, reachability, orphan
and dead-entry counts — is derived, and is regenerated rather than stored.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import networkx as nx

from ..findings import Finding, error, warn
from ..records import Record
from ..registers import CycleEntry, CycleRegister
from .usage import UsageEdge

#: See ``records.checks.CHECKS``.
CHECKS = frozenset(
    {
        "cycle-member-unknown",
        "cycle-self-loop",
        "cycle-stale-ruling",
        "cycle-undispositioned",
        "edge-dropped",
    }
)

# A cycle is matched to its register entry by member set (see CycleEntry.key).
Members = frozenset


@dataclass
class ConceptGraph:
    """The dependency graph plus the human rulings that make it readable."""

    graph: nx.DiGraph
    records: dict[str, Record]
    register: CycleRegister
    cycles: list[tuple[str, ...]] = field(default_factory=list)
    #: Usage edges from the bodies in `[bodies]` (step 3.7), plus what was
    #: scanned to get them — `bodies` maps scanned code → path, `components`
    #: names the full detangle set so the emitted file can state which
    #: components have no body yet.
    usage: list[UsageEdge] = field(default_factory=list)
    bodies: dict[str, str] = field(default_factory=dict)
    components: tuple[str, ...] = ()

    # -- derived views -----------------------------------------------------

    def entry_for(self, cycle: tuple[str, ...]) -> CycleEntry | None:
        return self.register.by_members().get(Members(cycle))

    def reading_order(self) -> list[str]:
        """Every concept, ordered so no definition precedes a term it uses.

        Cycles cannot satisfy that, so each strongly connected component is
        condensed to a single unit and its members are emitted adjacently —
        the entry point first, per criterion 1 clause 2. This is the order
        ``param-glossary-order`` calls topological; a per-document view is the
        same order filtered by ``placement``, which preserves the partial
        order.
        """
        reverse = self.graph.reverse(copy=True)
        condensed = nx.condensation(reverse)
        order: list[str] = []
        for scc in nx.lexicographical_topological_sort(
            condensed, key=lambda n: min(condensed.nodes[n]["members"])
        ):
            order.extend(self._order_within(condensed.nodes[scc]["members"]))
        return order

    def _order_within(self, members: set[str]) -> list[str]:
        if len(members) == 1:
            return list(members)
        ordered = sorted(members)
        entry = self.entry_for(tuple(ordered))
        if entry and entry.entry_point in members:
            ordered.remove(entry.entry_point)
            ordered.insert(0, entry.entry_point)
        return ordered

    def impact(self, node: str) -> list[str]:
        """Concepts whose definitions transitively depend on ``node``.

        The impact-analysis question of Phase 3.7: if this definition changes,
        which definitions have to be re-read? Answered against the dependency
        edges; ``using_sections`` widens it to document sections.
        """
        return sorted(nx.ancestors(self.graph, node))

    def using_sections(self, node: str) -> list[str]:
        """Stamped sections whose prose uses ``node`` or anything it impacts.

        The other half of the impact question: a definition change is re-read
        not only in the definitions that depend on it but in every section
        that uses one of them. Empty until the section's body is registered
        in ``[bodies]``.
        """
        affected = set(self.impact(node)) | {node}
        return sorted(
            {f"{e.doc}#{e.section}" for e in self.usage if e.term in affected}
        )

    def requires(self, node: str) -> list[str]:
        """Everything that must be defined before ``node`` can be read."""
        return sorted(nx.descendants(self.graph, node))

    # -- measures ----------------------------------------------------------

    def orphans(self) -> list[str]:
        """Used in the corpus, never defined in it — criterion 3's measure.

        Read from the ``orphan`` flag rather than from ``definition is None``:
        the IBE/IBEB ruling leaves software records undefined but unflagged
        because the source does define them, and ``mts-spa`` is defined only
        from the analytical layer and so is a set-level orphan despite having
        a definition.
        """
        return sorted(
            rid for rid, rec in self.records.items()
            if "orphan" in rec.get_list("flags")
        )

    def undefined(self) -> list[str]:
        return sorted(
            rid for rid, rec in self.records.items() if not rec.defined
        )

    def dead_entries(self) -> list[str]:
        """Defined terms used nowhere in the set (step 3.7).

        Usage is read from ``used_in`` — the corpus documents the term occurs
        in — because the output bodies do not exist until Phase 5. When they
        do, usage edges extracted from them join this test; the set of dead
        entries can only grow, never shrink, so nothing computed here is
        invalidated by their arrival.
        """
        return sorted(
            rid for rid, rec in self.records.items()
            if rec.defined and not rec.get_list("used_in")
        )


def build(
    records: list[Record],
    register: CycleRegister,
    usage: list[UsageEdge] | None = None,
    bodies: dict[str, str] | None = None,
    components: tuple[str, ...] = (),
) -> tuple[ConceptGraph, list[Finding]]:
    """Assemble the graph and report what only the graph can see.

    Dangling edge targets are a ``validate`` finding, not one raised here, so
    this drops them with a note instead of duplicating the check.
    """
    by_id = {rec.id: rec for rec in records}
    graph = nx.DiGraph()
    findings: list[Finding] = []

    for rid in sorted(by_id):
        rec = by_id[rid]
        graph.add_node(
            rid,
            term=rec.data.get("term") or rid,
            placement=rec.data.get("placement"),
            defined=rec.defined,
        )
    for rid in sorted(by_id):
        for target in sorted(set(by_id[rid].get_list("depends_on"))):
            if target in by_id:
                graph.add_edge(rid, target)
            else:
                findings.append(
                    warn(
                        "edge-dropped",
                        by_id[rid].where("depends_on"),
                        f"target {target!r} has no record; edge left out of the "
                        "graph (validate reports the dangling target itself)",
                    )
                )

    cycles = _live_cycles(graph)
    cg = ConceptGraph(
        graph=graph,
        records=by_id,
        register=register,
        cycles=cycles,
        usage=sorted(set(usage or [])),
        bodies=dict(bodies or {}),
        components=tuple(components),
    )
    findings.extend(check_cycles(cg))
    return cg, findings


def _live_cycles(graph: nx.DiGraph) -> list[tuple[str, ...]]:
    """Every elementary cycle, in a canonical rotation so output is stable.

    ``simple_cycles`` chooses its own starting node and its own emission order;
    both are rotated and sorted here so the same record set always serialises
    to the same bytes (ADR-001 Decision 2, deterministic output).
    """
    out = []
    for cycle in nx.simple_cycles(graph):
        start = cycle.index(min(cycle))
        out.append(tuple(cycle[start:] + cycle[:start]))
    return sorted(out, key=lambda c: (len(c), c))


def check_cycles(cg: ConceptGraph) -> list[Finding]:
    """Criterion 1, Cycles: register entries and live cycles are 1:1.

    A live cycle with no entry is blocking — a new circular definition awaiting
    disposition. A stale entry is flagged rather than dropped, at ``warn``:
    the rubric calls only the first case blocking, and both exit 1 anyway.
    """
    out: list[Finding] = []
    entries = cg.register.by_members()
    live = {Members(c): c for c in cg.cycles}

    for key, cycle in sorted(live.items(), key=lambda kv: kv[1]):
        if key in entries:
            continue
        if len(cycle) == 1:
            out.append(
                error(
                    "cycle-self-loop",
                    f"concepts/{cycle[0]}.yaml:depends_on",
                    f"{cycle[0]!r} depends on itself. ISO 704 §6.5.2 prohibits "
                    "this except by documented exception — narrow the "
                    "definition, or disposition it in registers/cycles.yaml",
                )
            )
            continue
        out.append(
            error(
                "cycle-undispositioned",
                cg.register.rel,
                "no register entry for the live cycle "
                + " -> ".join(cycle + (cycle[0],))
                + " — narrow a definition (ISO 704 §6.5.2 inner circle) or "
                "record a disposition; the ruling is Nick's",
            )
        )

    for key, entry in sorted(entries.items(), key=lambda kv: kv[1].id):
        unknown = [m for m in entry.members if m not in cg.records]
        if unknown:
            out.append(
                error(
                    "cycle-member-unknown",
                    f"{cg.register.rel}:{entry.id}",
                    f"members {unknown} have no concept record",
                )
            )
            continue
        if key not in live:
            out.append(
                warn(
                    "cycle-stale-ruling",
                    f"{cg.register.rel}:{entry.id}",
                    f"entry {entry.id!r} dispositions {sorted(entry.members)}, "
                    "which is no longer a cycle — a narrowed definition leaves "
                    "no entry; flagged rather than silently dropped",
                )
            )
    return out


__all__ = ["ConceptGraph", "build", "check_cycles"]
