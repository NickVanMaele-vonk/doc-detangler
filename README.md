# Detangle — Document Restructuring Agent

Tooling to transform convoluted MTSAM markdown documents into logically
structured, human-readable documents with clear definitions.

## Problem

Client-supplied documentation is dense and detail-first: 
- terms are used before they are introduced
- there is little top-down introduction of business concepts.
Representative examples: the `MTSAM-ref/requirements/10-sample-files/blueprint-*-shortened.md` files.

## Approach

A concept dependency graph drives the pipeline: extract domain terms, record
which definitions depend on which, then use topological ordering to restructure
documents so every concept is defined before first use. A verification harness
proves losslessness — no meaning lost, no meaning invented.

## Hard constraints

- No meaning lost or invented; omissions require explicit human approval.
- All document updates go through Azure DevOps PRs; the tool posts findings as
  PR comments, which must be Resolved before merge.
- Bridging/explanatory additions are allowed but must be marked as such.
- All artifacts (including the concept graph) are plain-text and git-friendly.

## Contents

| File | Purpose |
|------|---------|
| `detangle-agent-plan.md` | Full project plan: 9 phases, constraints, rubric, sequencing rationale |
| `definition-of-done.md` | Rubric for "logically structured, human-readable" *(Phase 1 — pending)* |
| `glossary.md` | MTSAM domain glossary *(Phase 3 — pending)* |
| `concept-graph.yaml` | Concept dependency edge list — source of truth *(Phase 3 — pending)* |
| `concept-graph.mmd` | Mermaid render of the graph *(Phase 3 — pending)* |
| `eval/` | Test inputs and golden reference outputs *(Phase 5 — pending)* |

## Status

Plan approved. Execution not started. Next step: Phase 1.1 —
draft `definition-of-done.md`.

## Owner

Nick Van Maele (TriFinance) — MTSAM project
