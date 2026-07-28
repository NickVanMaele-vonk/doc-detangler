# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Detangle — a planned agent/pipeline that turns convoluted markdown
specifications into a logically structured five-document set. **There is no
code yet.** The repo currently holds the normative specification (`plan/`),
the read-only source corpus (`samples/`), and in-progress Phase 3 data
artifacts (`work/`). The runtime is decided (Python, D7) but nothing is
implemented, so there is no build, no test runner, and no lint. Do not invent
one; if a task needs tooling, propose it and get approval first.

## Commands

Everything is git + `gh`. The only workflow that exists:

```bash
git checkout -b <area>/<slug>          # areas in use: plan/, work/, samples/
git add … && git commit                # then:
gh pr create --base main               # every change lands via PR — see C4
```

Branch naming follows the areas above (`plan/add-section-ids`,
`work/upd-candidate-terms`, `samples/new`). PRs are merged by Nick, not by the
assistant.

## The three normative documents — read before changing anything

| File | Role |
|------|------|
| `plan/detangle-agent-plan.md` | 10 phases, constraints **C1–C12**, sequencing rationale, working agreements |
| `plan/definition-of-done.md` | The rubric: **criteria 1–9**, parameters (`param-*`), non-goals, per-phase applicability. Approved 2026-07-21 (v4 2026-07-23) |
| `plan/research-memo.md` | Phase 2 research and the **decision register D1–D10** (§7), with full rationale notes for D9 and D10 |

These three are cross-referential and use stable identifiers. **Cite the
identifier, not a paraphrase** — write "per C9" or "criterion 3" or "§D10
element 4". When you change one document, check whether the other two assert
the same thing; a constraint typically appears once in each (e.g. glossary
placement is C9 *and* criterion 3 *and* plan §4).

Decisions D1–D10 are all signed off. Do not reopen a signed-off decision;
propose an amendment with rationale and let Nick rule.

## Architecture (the parts that require reading several files)

**The concept graph is the backbone, not a side artifact.** Directed edges
"definition of X uses term Y". Topological sort gives the reading order and
the glossary's own order; alphabetical projection of the same term set gives
`index.md`; forward reachability is impact analysis; cycle detection surfaces
genuinely circular definitions for human disposition; orphans (used but never
defined) measure how convoluted the source is.

**Ontology-first (D9).** Structured concept records — one file per concept —
are the source of truth. `glossary.md`, `index.md`, and `concept-graph.mmd`
are **generated views** with source-map anchors, so a reviewer's PR comment on
generated markdown round-trips deterministically back to the record. Document
*bodies* are not ontology; they stay markdown tracked as moved / derived /
added (criterion 7).

**Canonical vs derived is the distinction that governs everything (D10 §4).**

- Canonical: concept records, including `depends_on` dependency edges.
- Derived — regenerated, never hand-edited, hand-editing them fails CI:
  usage edges, first-use links, `index.md`, `concept-graph.mmd`,
  `state/section-map.yaml`, `manifest.yaml`.

Anything location- or order-sensitive is derived, because a reorder rots it.

**Five documents, one definition site (C9/C10).** Reading order is
`glossary.md` → UCE → SBSP → MCL. `index.md` sits outside it. Placement is
**computed, not judged**: a term used in ≥ 2 of the three component blueprints
goes in the glossary; used in exactly 1, it is defined in that document. Never
both. `samples/blueprint-analytical-layer.md` is a read-only reference and is
**excluded from the placement count** (Nick's ruling 2026-07-22) — an `(A)`
flag is informational only.

**Two operating modes (D10).** The one-shot detangle run (Phases 5–9) and the
steady-state drift lint that guards every later docs PR (Phase 10). Section
identity is two-layer: tool-stamped `<!-- sec:… -->` markers for identity,
content hashes in a generated section map for change detection. **Line numbers
are provenance nowhere**, and authors — human or AI — are never asked to mint
a section ID.

## Current state

Phases 1, 2 and the Phase 4 gate decisions are closed. **Phase 3 is in
progress**: step 3.1 candidate extraction is complete and the merged list is
under business review.

- `work/term-extraction/blueprint-*.terms.yaml` — raw per-document extraction,
  LLM-assisted, headers state it is **not yet human-reviewed**. Its line
  numbers are approximate and explicitly not citable as provenance.
- `work/term-extraction/candidate-terms-merged.md` — the merge Nick is
  reviewing, carrying a "Human review decision" column per term. This column
  is Nick's; do not fill it in.

Nothing in `work/` is a concept record yet. Records begin at step 3.3 and must
carry the D10 schema fields (`status`, `superseded_by`, hash-anchored spans
with `verified_against`) **from the first record** — retrofitting hundreds of
records is the failure mode this guards against.

Division of labour for Phase 3: Nick builds the D9 view-generator himself;
the assistant delivers ontology content (records, edges) directly.

## Working with the corpus

`samples/` is input, never output. The blueprints are pandoc-converted grid
tables with very long physical lines, OCR damage in places, and live
contradictions (MCL is titled v21 but contains a "what is new in v22" block;
MCL applies to UCE v28 while SBSP cites v30). **These contradictions are
data, not bugs** — surface them, never harmonise them (criterion 6, non-goals).

When reproducing source text anywhere, criterion 5 is absolute: numbers,
thresholds, comparison operators, modality (`must` vs `should`), scoping
qualifiers, internal codes and their casing, citations, classification
markings, and British spelling are reproduced verbatim. This is checked
mechanically and independently of claim mapping, because a claim can map
correctly and still have lost its force.

Regulator-owned terms (MAR, ESMA, FSMA, CONSOB, …) go to a references list,
not the glossary.

## Working agreements (from the plan, applies to all phases)

- Design decisions are proposed by the assistant; Nick approves before any
  code is written.
- Small sequential steps; verify each before starting the next.
- Never investigate and change in the same step.
- After every code change: a concrete list of functional tests to verify.
- Documentation updated after every completed feature.
- No hard-coded values; if required data does not exist yet, stop and ask.

## Hard prohibitions

Beyond the non-goals list in `plan/definition-of-done.md`: never merge a PR,
resolve a PR comment, or approve an omission on Nick's behalf; never
auto-"fix" a document body in steady state (the guard comments, humans
decide); never hand-edit a generated artifact.
