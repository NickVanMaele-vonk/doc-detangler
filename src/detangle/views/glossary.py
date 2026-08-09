"""Rendering ``glossary.md`` — plan step 3.5, design approved 2026-08-03.

The glossary is the first document of the output set, so it is subject to the
rubric itself: criterion 1 (concept-before-use), criterion 2 (source-traceable
wording) and criterion 3 (one definition site, aliases recorded, no term left
undefined). Everything here follows from that plus D9's "the record is the
truth, the view is derived".

**Amended 2026-08-04.** That last part now holds for the ontology only. The
definition *prose* is canonical in the document that defines it, this file
included, so what this module produced is a **seed** rather than a standing
view: it ran once, and the file it wrote is edited by people from here on.
The rendering below is unchanged — a seed and a view are the same bytes — but
the banner says so, and `--check` is no longer a CI gate.

Three consequences shape the code:

- **Order is the graph's, not the alphabet's.** ``param-glossary-order`` is
  topological, so entries are the glossary-placed projection of
  ``ConceptGraph.reading_order()`` — which already condenses the accepted
  cycle and puts its entry point first. Alphabetical lookup is ``index.md``'s
  job (C10) and is deliberately absent here.
- **No word is invented.** The tool emits its own scaffolding — headings,
  notes, markers — but never domain prose (C2). So the overview is a marked
  gap rather than a summary, and an undefined term gets a note saying so
  rather than a definition.
- **Anchors are emitted markers, never line offsets** (D9, D10). Every entry
  is delimited by ``<!-- concept:<id>:start -->`` / ``:end`` markers — the
  bodies' scheme — so a PR comment on this file resolves to the nearest
  preceding marker and hence to the record that produced the entry, and the
  lift (``detangle lift``) knows exactly where a definition's prose ends. A
  regeneration reorders entries; line numbers would rot on the first reorder.

Definitions and alias lists are emitted on a single physical line each, not
wrapped. Wrapping would reflow a whole paragraph when one word changes, and
this file exists to be commented on: a one-line diff points at one record.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..config import DocumentRegistry
from ..findings import Finding, error, warn
from ..graph import ConceptGraph

GLOSSARY_PLACEMENT = "glossary"

#: See ``records.checks.CHECKS``. Split because ``--check`` and a write run
#: raise different things, and a command must only claim what it ran.
DRIFT_CHECKS = frozenset({"glossary-drift", "glossary-missing"})
RENDER_CHECKS = frozenset({"overview-gap", "sources-blob-skew"})
CHECKS = DRIFT_CHECKS | RENDER_CHECKS

BANNER = """\
<!--
SEEDED by `detangle generate` (plan step 3.5). Not a standing generated view.

Nick's ruling of 2026-08-04 makes this the fourth editable document: a
definition is canonical in the document that defines it, and the concept
record (`concepts/*.yaml`) holds a derived copy. So a definition below is
edited here, in place, and its record follows.

That ruling is enforced by the lift (built 2026-08-08): `detangle lift`
mirrors an edited definition into its record's derived copy, and
`detangle lift --check` runs in CI, so the file and the records cannot
silently disagree. Edit a definition between its markers; the heading and
the "Also known as" line belong to the record (`term`, `aliases`) and are
changed there, never here.

Re-running `detangle generate` REWRITES this file in full and discards every
human edit. It has done its job as the seeder.

Entry order is topological (`param-glossary-order`), taken from the concept
graph and the cycle register (`registers/cycles.yaml`), so the file reads
start to finish without meeting an undefined term.

Each entry sits between concept markers — `concept:<id>:start` and
`concept:<id>:end`, each in its own HTML comment — naming the record it came
from, so a comment on this file resolves to that record without any line
offset being involved (D10), and the lift knows exactly where a definition's
prose ends. Anything written outside the markers belongs to this file alone
and is mirrored nowhere.

(No literal marker is spelled out above: a closing comment bracket inside
this banner would end it early and leak the rest as visible text.)
-->
"""

TITLE = "# Glossary\n"

OVERVIEW_HEADING = "## Overview\n"

OVERVIEW_GAP = """\
<!-- gap:overview -->
> **Gap — the overview is not written.** Criterion 2 requires this document to
> open with a plain-language overview: what this body of documentation is
> about and how the three component documents relate, in
> `param-overview-max-words` words or fewer. `detangle generate` will not
> write it — every substantive word it emits traces to a concept record, and
> an overview of the domain would be invented text (C2, criterion 7). A human
> writes it **here**, replacing this block (Nick, 2026-08-04).
"""

SOURCES_HEADING = "## Sources\n"

SOURCES_LEAD = """\
Every source document the entries below draw on, each bound to the git blob
its records were verified against, with its role in the two input sets:
`component` documents are the detangle set, `reference` documents are
read-only context whose definitions may be lifted but whose bodies are never
in this set (Nick, 2026-08-05). Git carries release identity, so no version
string is typed here (ruling of 2026-07-31).
"""

UNDEFINED_NOTE = """\
> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
"""


@dataclass
class Glossary:
    """The rendered file plus what the run needs to report about it."""

    text: str
    findings: list[Finding] = field(default_factory=list)
    entries: list[str] = field(default_factory=list)
    undefined: list[str] = field(default_factory=list)
    forward_refs: list[tuple[str, str]] = field(default_factory=list)
    sources: dict[str, list[str]] = field(default_factory=dict)

    @property
    def summary(self) -> dict:
        return {
            "entries": len(self.entries),
            "defined": len(self.entries) - len(self.undefined),
            "undefined": len(self.undefined),
            "sources": len(self.sources),
            "forward_refs": len(self.forward_refs),
        }


def build(
    cg: ConceptGraph, rel: str = "glossary.md", registry: DocumentRegistry | None = None
) -> Glossary:
    """Render the glossary and report what only the rendering can see.

    ``registry`` labels each sources-table row by input set; without one the
    role column reads ``unregistered``, so a caller that forgets it produces
    output that says so rather than output that quietly claims a role.
    """
    order = [
        rid
        for rid in cg.reading_order()
        if cg.records[rid].data.get("placement") == GLOSSARY_PLACEMENT
    ]
    position = {rid: i for i, rid in enumerate(order)}
    undefined = [rid for rid in order if not cg.records[rid].defined]
    forward = _forward_refs(cg, order, position)
    sources, source_findings = _sources(cg, order, rel)

    parts = [
        BANNER,
        "\n",
        TITLE,
        "\n",
        OVERVIEW_HEADING,
        "\n",
        OVERVIEW_GAP,
        "\n",
        SOURCES_HEADING,
        "\n",
        SOURCES_LEAD,
        "\n",
        _sources_table(sources, registry),
    ]
    for rid in order:
        parts.append("\n")
        parts.append(_entry(cg, rid, forward))

    findings = [
        warn(
            "overview-gap",
            f"{rel}:overview",
            "the glossary has no overview; criterion 2 requires one. The "
            "generator will not write domain prose (C2), so the marked gap "
            "stands until a human writes the text into this file, replacing "
            "the gap block (Nick, 2026-08-04)",
        )
    ]
    findings.extend(source_findings)

    return Glossary(
        text="".join(parts),
        findings=findings,
        entries=order,
        undefined=undefined,
        forward_refs=forward,
        sources=sources,
    )


def render(
    cg: ConceptGraph, rel: str = "glossary.md", registry: DocumentRegistry | None = None
) -> str:
    """The file as text. Same records always give the same bytes."""
    return build(cg, rel, registry).text


# -- pieces ----------------------------------------------------------------


def _entry(cg: ConceptGraph, rid: str, forward: list[tuple[str, str]]) -> str:
    """One glossary entry, delimited: start marker, apparatus, prose, end.

    The ``:start``/``:end`` pair is the same scheme the document bodies carry
    (D9) — the DoD names these delimiters as what keeps the lift into the
    record deterministic. The end marker closes the whole entry, bridging
    notes included, attached to the last line rather than floated as its own
    block so it never becomes a block of its own in the ``para_hash`` split.
    """
    record = cg.records[rid]
    lines = [
        f"<!-- concept:{rid}:start -->\n",
        f"## {record.data.get('term') or rid}\n",
    ]

    aliases = [str(a) for a in record.get_list("aliases")]
    if aliases:
        lines.append("\n")
        lines.append(f"**Also known as:** {', '.join(aliases)}\n")

    lines.append("\n")
    if record.defined:
        lines.append(f"{' '.join(str(record.data['definition']).split())}\n")
    else:
        lines.append(UNDEFINED_NOTE)

    for source, target in forward:
        if source == rid:
            lines.append("\n")
            lines.append(_forward_note(cg, source, target))
    lines.append(f"<!-- concept:{rid}:end -->\n")
    return "".join(lines)


def _forward_note(cg: ConceptGraph, source: str, target: str) -> str:
    """Criterion 1 clause 2: the forward reference is marked as bridging text.

    A topological order has no forward references except inside a cycle, which
    reordering cannot fix. The mark is emitted rather than typed into the
    definition — the definition is corpus wording (C2), and a marker a human
    has to remember to write is a marker that goes missing (C12's rule for
    section IDs, applied to bridging text).
    """
    term = cg.records[target].data.get("term") or target
    entry = _cycle_entry(cg, source, target)
    citation = (
        f"accepted cycle `{entry.id}` in `{cg.register.rel}`"
        if entry is not None
        else "an undispositioned cycle — `detangle graph` names it"
    )
    return (
        "<!-- bridging:forward-ref -->\n"
        f"> **Forward reference (bridging text).** This definition uses "
        f"**{term}**, which is defined below rather than above: the two terms "
        f"define each other by contrast, so no order can put both first "
        f"({citation}; criterion 1, clause 2).\n"
    )


def _cycle_entry(cg: ConceptGraph, first: str, second: str):
    for cycle in cg.cycles:
        if first in cycle and second in cycle:
            return cg.entry_for(cycle)
    return None


def _forward_refs(
    cg: ConceptGraph, order: list[str], position: dict[str, int]
) -> list[tuple[str, str]]:
    """Edges that point at an entry rendered later — cycle members only.

    Computed from the rendered order rather than assumed from the cycle
    register, so a dependency the glossary cannot reach at all would show up
    here too. C9 limb 2 is what keeps that set empty: a term a glossary
    definition depends on joins the glossary, so no edge leaves this file
    forwards into a document body.
    """
    out: list[tuple[str, str]] = []
    for rid in order:
        for target in sorted(set(cg.records[rid].get_list("depends_on"))):
            if position.get(target, -1) > position[rid]:
                out.append((rid, target))
    return out


def _sources(
    cg: ConceptGraph, order: list[str], rel: str
) -> tuple[dict[str, list[str]], list[Finding]]:
    """Source document → the git blobs its spans were verified against.

    One blob per document is the healthy case, and `detangle validate`'s
    `git-blob-stale` check is what holds it: every record re-verifies against
    the same committed file. Two blobs for one document would mean the entries
    below were verified against different revisions of it, which is exactly
    the version skew the source-version binding exists to catch — so it is
    reported rather than resolved by picking one.
    """
    blobs: dict[str, set[str]] = {}
    for rid in order:
        for span in cg.records[rid].get_list("source"):
            if not isinstance(span, dict):
                continue
            # A lifted definition's authored span cites this file itself; a
            # document is not one of its own sources, so it gets no row.
            if span.get("doc") == rel:
                continue
            verified = span.get("verified_against")
            blob = verified.get("git_blob") if isinstance(verified, dict) else None
            if span.get("doc") and blob:
                blobs.setdefault(str(span["doc"]), set()).add(str(blob))

    findings = [
        error(
            "sources-blob-skew",
            f"{rel}:sources",
            f"{doc} is cited at {len(found)} different git blobs "
            f"({', '.join(sorted(found))}); the entries were verified against "
            "different revisions of one source",
        )
        for doc, found in sorted(blobs.items())
        if len(found) > 1
    ]
    return {doc: sorted(found) for doc, found in sorted(blobs.items())}, findings


def _sources_table(
    sources: dict[str, list[str]], registry: DocumentRegistry | None
) -> str:
    if not sources:
        return "No entry cites a source document.\n"
    rows = [
        "| Source document | Role | Verified git blob |\n",
        "| --- | --- | --- |\n",
    ]
    rows.extend(
        f"| `{doc}` | {registry.role(doc) if registry else 'unregistered'} "
        f"| `{', '.join(blobs)}` |\n"
        for doc, blobs in sources.items()
    )
    return "".join(rows)


# -- the regenerate-and-compare guard --------------------------------------


def check_current(text: str, path: Path, rel: str) -> list[Finding]:
    """Bytes, not structure — the same guard `concept-graph.yaml` carries.

    Reordering or rewrapping a generated file changes nothing semantically and
    everything about whether it was generated, so the comparison has to be
    exact for "never hand-edit a generated artifact" to be enforceable.
    """
    if not path.is_file():
        return [
            error(
                "glossary-missing",
                rel,
                "no generated glossary on disk; run `detangle generate` and "
                "commit the result",
            )
        ]
    if path.read_text(encoding="utf-8") != text:
        return [
            error(
                "glossary-drift",
                rel,
                "the committed glossary differs from a regeneration — it was "
                "hand-edited, or a record changed without regenerating. Edit "
                "the record named by the nearest `<!-- concept:… -->` marker, "
                "then run `detangle generate`",
            )
        ]
    return []


__all__ = ["Glossary", "build", "check_current", "render"]
