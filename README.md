# Detangle — Document Restructuring Agent

Tooling to transform convoluted markdown documents into logically
structured, human-readable documents with clear definitions.

## Problem

Supplied documentation is dense and detail-first: 
- terms are used before they are introduced
- there is little top-down introduction of business concepts.
Representative examples: the `./samples/blueprint-*-shortened.md` files.

## Approach

A concept dependency graph drives the pipeline: extract domain terms, record
which definitions depend on which, then use topological ordering to restructure
documents so every concept is defined before first use. A verification harness
proves losslessness — no meaning lost, no meaning invented.

The output is **five** documents, not three. A single `glossary.md` is read
first and holds the definition of every term used in more than one document;
terms local to one document are defined there. No term is defined twice, and
none is left undefined. Putting the shared definitions ahead of everything is
what makes "defined before first use" achievable across a heavily
interdependent set — and it turns cross-document definitional cycles, which
no reordering can fix, into intra-glossary ones, which reordering can.

Reading order and lookup order are separated rather than compromised. The
glossary is ordered **topologically**, so it reads start to finish without
ever meeting an undefined term. `index.md` is the fifth document: a single
**alphabetical** list spanning all four others, giving each term and the
location of its definition — terms only, no definitions. It sits outside the
reading order, is generated rather than written, and answers the one
question a glossary ordered for reading cannot: *where is this term?*

## Hard constraints

- No meaning lost or invented; omissions require explicit human approval.
- No meaning *weakened*: numbers, thresholds, modality (`must` vs `should`),
  scoping qualifiers, citations, and classification markings are preserved
  verbatim. Source contradictions are surfaced, never silently fixed.
- Bridging/explanatory additions are allowed but must be marked as such;
  rewritten source text is marked separately, as *derived*.
- Any update on an existing document goes through pull requests ("PRs"); the tool posts findings as PR comments, which must be Resolved before merge.
- Glossary-first, single definition site: a term used in more than one
  document is defined in `glossary.md` and only there; a term used in one
  document is defined in that document.
- Reading order and lookup order are separate artifacts: `glossary.md` is
  topological, `index.md` is alphabetical and covers every term across all
  four other documents. The index is generated and contains no definitions.
- Links run forward only: each section links its first use of a glossary
  term to that term's entry. A glossary defines terms; it does not record
  where they are used. Usage locations are graph edges in
  `concept-graph.yaml`.
- A PR assembles changes relating to similar concepts and may touch any
  number of documents — document count is not the unit. A PR may not change
  more terms than `param-max-terms-changed-per-PR` (25). Each PR is two
  commits — moves only (machine-verified set-wide, no semantic review), then
  text changes (the only part a human reads). Comments are raised per
  cluster, not per instance, and a run exceeding either budget fails rather
  than opening an unreviewable PR.
- All artifacts (including the concept graph) are plain-text and git-friendly.

## Contents

| File | Purpose |
|------|---------|
| `./plan/detangle-agent-plan.md` | Full project plan: 9 phases, constraints, rubric, sequencing rationale |
| `./plan/definition-of-done.md` | Rubric for "logically structured, human-readable": 8 criteria, parameters, non-goals, per-phase applicability *(Phase 1 — draft v3, pending sign-off)* |
| `glossary.md` | Business domain glossary — first document of the output set; defines every term used in more than one document, ordered topologically *(Phase 3 — pending)* |
| `index.md` | Alphabetical index across all four other documents: every term plus the location of its definition. Generated *(Phase 3 — pending)* |
| `concept-graph.yaml` | Concept dependency edge list — source of truth *(Phase 3 — pending)* |
| `concept-graph.mmd` | Mermaid render of the graph *(Phase 3 — pending)* |
| `eval/` | Test inputs and golden reference outputs *(Phase 5 — pending)* |

## Status

Plan approved. Phase 1.1 drafted: `plan/definition-of-done.md` (v3).
Next step: Phase 1.2 — Nick approves or amends, including the parameter
values listed in that document.

## Owner

Nick Van Maele (Vonk.ca)
