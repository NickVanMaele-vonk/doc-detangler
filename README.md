# Detangle — Document Restructuring Agent

Tooling to transform convoluted markdown documents into logically
structured, human-readable documents with clear definitions.

## Problem description

At times, supplied requirements documentation is dense and detail-first: 
- little to no top-down introduction of business concepts.
- cryptic terms are used before they are introduced
Representative examples: the `./samples/blueprint-*-shortened.md` files.

## Approach

A concept dependency graph drives the pipeline: extract domain terms, record
which definitions depend on which, then use topological ordering to restructure
documents so every concept is defined before first use. A verification harness
proves losslessness — no meaning lost, no meaning invented.

The input is three documents, the output is **five** documents - the three restructured documents, plus a glossary, plus an index. 

A single `glossary.md` is read first and holds the definition of every term used in more than one document; terms local to one document are defined there. No term is defined twice, and none is left undefined. 
Putting the shared definitions ahead of everything is what makes "defined before first use" achievable across a heavily interdependent set — and it turns cross-document definitional cycles, which no reordering can fix, into intra-glossary ones, which reordering can. The glossary is ordered **topologically**, so it reads start to finish without ever meeting an undefined term. 

Reading order and lookup order are separated rather than compromised. 

`index.md` is the fifth document: a single **alphabetical** list spanning all four others, giving each term and the location of its definition. `index.md` contains terms only, no definitions. It sits outside the reading order, is generated rather than written, and answers the one question a glossary ordered for reading cannot: *where is this term?*

If one term appears in more than one input document, then: 
- "what is this term's definition?" -> via glossary
- "where is this term used in the corpus?" -> via index 

## Hard constraints

- No meaning lost or invented; omissions require explicit human approval.
- No meaning *weakened*: numbers, thresholds, modality (`must` vs `should`),
  scoping qualifiers, citations, and classification markings are preserved
  verbatim. Source contradictions are surfaced, never silently fixed.
- Bridging/explanatory additions are allowed but must be marked as such;
  rewritten source text is marked separately, as *derived*.
- Any update on an existing document goes through pull requests ("PRs"); the tool posts findings as PR comments, which must be Resolved before merge.
- Glossary-first, single definition site: a term used in more than one
  document is defined in `glossary.md` and only there; a term used in only one
  document is defined in only that document.
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
| `./plan/detangle-agent-plan.md` | Full project plan: 10 phases, constraints, rubric, sequencing rationale |
| `./plan/definition-of-done.md` | Rubric for "logically structured, human-readable": 8 criteria, parameters, non-goals, per-phase applicability *(Phase 1 — approved)* |
| `./plan/research-memo.md` | Standards to follow and open-source components to reuse, with coverage gaps stated; carries the decision register D1–D10 *(Phase 2 — complete, all decisions signed off)* |
| `./plan/adr-001-form-factor.md` | Form factor and toolchain layout: Python package + CLI, CLI contract, repo layout, build order *(Phase 4.3/4.4 — accepted 2026-07-30)* |
| `src/detangle/` | The toolchain: `validate` and `graph` *(built)*, `generate` *(Phase 3 steps 3.5–3.7 — pending)* |
| `detangle.toml` | Configuration: `param-*` values from the rubric, the corpus document map, validation thresholds. No value is hard-coded in the package |
| `glossary.md` | Business domain glossary — first document of the output set; defines every term used in more than one document, ordered topologically *(Phase 3 — pending)* |
| `index.md` | Alphabetical index across all four other documents: every term plus the location of its definition. Generated *(Phase 3 — pending)* |
| `concepts/` | Canonical concept records — one YAML file per corpus-derived business term, and nothing else *(Phase 3)* |
| `registers/` | Canonical data that is not a corpus term: `cycles.yaml` (cycle dispositions, criterion 1) and `reference-terms.md` (regulator- and industry-owned terms, criterion 3) *(Phase 3)* |
| `concept-graph.yaml` | Concept dependency + usage edge list (SKOS concept model). Written by `detangle graph` from the concept records and registers, which are the source of truth; never hand-edited *(dependency edges built; usage edges arrive with the bodies in Phase 5)* |
| `concept-graph.mmd` | Mermaid render, generated from `concept-graph.yaml`; displays natively in Azure DevOps/GitHub *(Phase 3 — pending)* |
| `eval/` | Test inputs and golden reference outputs *(Phase 5 — pending)* |

## Status

Phases 1, 2 and 4 complete. Rubric approved (`plan/definition-of-done.md`);
research memo delivered (`plan/research-memo.md`) across three rounds. The
gating architecture decisions were signed off 2026-07-22: runtime is
**Python** (D7), and the definition layer is **ontology-first** (D9) —
structured concept records are the source of truth, with
`glossary.md`/`index.md`/`concept-graph.mmd` generated as anchored views.
Phase 4 closed 2026-07-30 with `plan/adr-001-form-factor.md`: the deliverable
is a Python package **`detangle`** with a CLI, and the Claude-skill wrapper is
deferred to Phase 9.2.

Phase 3 data is essentially complete — **358 concept records** under
`concepts/` with 404 `depends_on` edges, every cycle and definition conflict
dispositioned, and the criterion-3 reference terms and cycle rulings in
`registers/`.

Two of the three commands are built. **`detangle validate`** replaces the
throwaway per-PR scripts with a tested implementation of the record-set
integrity checks. **`detangle graph`** builds the concept graph from the
records' canonical `depends_on`, rolls up `registers/cycles.yaml`, and writes
the derived `concept-graph.yaml` — reading order, cycles, orphans, dead
entries, and reachability queries for impact analysis. Next is `generate`,
which closes Phase 3 steps 3.5–3.7 by producing `glossary.md`, `index.md` and
`concept-graph.mmd` as anchored views.

## Running it

`pandoc` must be on `PATH` — the `para_hash` scheme is defined in terms of its
plain-text output, so it is a hard dependency, not a convenience.

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"

.venv/bin/detangle validate            # the whole record set
.venv/bin/detangle validate concepts/widget.yaml   # just what a PR touches
.venv/bin/detangle validate --json     # machine-readable, for CI

.venv/bin/detangle graph               # rewrite concept-graph.yaml
.venv/bin/detangle graph --check       # CI: fail on a hand-edit or a stale graph
.venv/bin/detangle graph --impact gate # what breaks if this definition changes
.venv/bin/detangle graph --requires sb-26   # what must be defined first

.venv/bin/python -m pytest             # tests
.venv/bin/ruff check .                 # lint
```

Exit codes are the branch-policy contract: `0` clean, `1` findings raised,
`2` usage or internal error.

## Owner

Nick Van Maele (Vonk.ca)
