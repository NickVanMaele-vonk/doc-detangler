# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Style

Answer factually and concisely. 

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
progress**: steps 3.1–3.2 are done, step 3.3 record authoring is complete
(all §1 sections, §3a promotions, multi-document leftovers, and the full
U/S/M single-document bulks, PRs #37–#53), and the closing step 3.4
`depends_on` pass over the whole set is merged (PRs #54–#58: 303 edges
across 116 records). `concepts/` holds 332 canonical records plus
`concepts/reference-terms.md` (the hand-authored criterion-3 references
list). Nick's 2026-07-30 rulings: RT*/RD* re-placement (PR #51 — codes
promoted via a §7b (P) ruling follow that ruling's placement even when
the shortened corpus shows the surface in one doc only); keep all
sense-collision edges; and the dangling-list ruling delivered in
PRs #59–#60 — 20 new records (BT/RD/MTSAM-L code families, QML
sub-metrics, singletons, `cwps-intra`) plus their 26 incoming edges.

- `work/term-extraction/blueprint-*.terms.yaml` — raw per-document extraction,
  LLM-assisted, headers state it is **not yet human-reviewed**. Its line
  numbers are approximate and explicitly not citable as provenance; its
  quotes paraphrase — **always re-verify wording against `samples/`**.
- `work/term-extraction/candidate-terms-merged.md` — the reviewed merge,
  carrying a "Human review decision" column per term. This column is Nick's;
  do not fill it in.

Remaining Phase 3 queue: the §4 decision-register dispositions (Nick's).
The §7c `(P)` dispositions are closed (PR #63): P-1/P-2 ruled incorrect
readings by `(P)` and recorded in `notes` without raising a conflict;
P-3 – P-12 carried into the records as machine-readable `conflict:`
entries. **P-13 and P-14 stay candidate-list rows only** (Nick,
2026-07-30) — neither names a corpus term, and P-14 collides with the
plan's own C1–C12 constraint IDs rather than with anything in `samples/`,
so no record and no `reference-terms.md` row is minted for them.
All cycles from the closing pass are dispositioned (Nick's rulings
2026-07-30, applied in PR #62): the concept graph is acyclic except the
one accepted contrastive pair (liquidity-driven-reaction ↔
identity-driven-coordination, condensed by the view generator). Direction
rulings worth remembering: classification precedes gate (a status
recommended by a tool precedes the decision moment about it), and RT01
precedes SB-01 (a raw-data alert precedes the calculated fraud-detection
item that shares its name). Nick builds the D9 view-generator himself;
the assistant delivers ontology content (records, edges) directly.

## Record-authoring conventions (learned in practice, steps 3.3–3.4)

Established across PRs #17–#35; follow them so records stay uniform.

- **Span anchoring.** Split the source into blank-line blocks;
  `para_hash` = sha256 over the block's pandoc plain rendering
  (`pandoc -f markdown -t plain --wrap=none`, whitespace collapsed to
  single spaces, trimmed). `section` = nearest preceding numbered heading,
  else "Front matter". `verified_against.git_blob` =
  `git rev-parse HEAD:samples/<file>`. Grid-table rows may be OCR-split
  across blocks — anchor the block carrying the operative sentence; a
  whole-table block shares one hash across every record citing it.
- **Definitions are assembled, never invented (C2).** Only corpus wording,
  lightly stitched; pandoc-normalized punctuation (en-dashes, ≥, σ) is the
  house form. A term that is used but never defined gets
  `definition: null` + `flags: [orphan]` — do not promote extraction
  glosses or (P)-only expansions into definitions. **"Lightly stitched"
  means ordinary English is free** (Nick, 2026-07-30): connective and
  descriptive words — *abuse*, *pattern*, *identified*, *catalogued* —
  are standard English, not project terms; they need no corpus
  provenance, no definition, and mint no `depends_on` edge. C2 constrains
  the domain wording: terms, codes, thresholds, modality. A validation
  check that tests every word against the anchored block is measuring the
  wrong thing — restrict it to domain-shaped tokens (codes, snake_case
  and CamelCase identifiers, and surfaces that have records).
- **Verify wording against the source, not the extraction.** The extraction
  paraphrases ("cleared" became "passed" once — a criterion-5 defect that
  reached main). Validation for every batch: YAML parse + required keys,
  blob match, every `para_hash` present in the recomputed block-hash set,
  a long verbatim run of each definition inside its anchored block, conflict
  quotes verbatim substrings, `[[links]]` resolve, edge targets exist.
- **One definition site per term (C9).** If a value token gets promoted to
  its own record, remove it from the other record's aliases in the same PR
  (MWBR_ANOMALOUS precedent). A measure and the archetype that uses it stay
  separate records without shared aliases (QML / SB-13 precedent).
- **Placement is computed, and ownership beats count.** Regulator- and
  industry-owned terms go to `concepts/reference-terms.md` rows, never
  records, even when used in ≥2 docs (criterion 3; MAR Article 12/16, ADA,
  quote stuffing, Eurex, OLO, HHI). (P)-only terms are held as candidate
  rows until a U/S/M usage appears (ruling on PR #18).
- **Code families get records per code.** SB-xx archetype rows and
  MTSAM-Lxx register entries used in ≥2 docs are records in their own
  right, as values of their master term (sb-26 precedent).
- **Cycle policy (applied 2026-07-29, ISO 704 §6.5.2).** A circular edge
  whose source clause is consequence/elaboration is resolved by narrowing
  the definition proper — the clause moves verbatim to `notes`, and the
  edge is dropped. A genuinely contrastive pair is kept as a documented
  outer circle (liquidity-driven-reaction ↔ identity-driven-coordination is
  the only accepted cycle); the view generator must condense that SCC for
  the topological sort.
- **PR mechanics.** ≤ `param-max-terms-changed-per-PR` (25) files counting
  new records, edited records, and edge changes together. Note the count in
  every PR body. When wrapping notes programmatically, keep `[[...]]`
  tokens atomic (`break_on_hyphens=False`) — split links reached main once.
- **Edges** ("definition of X uses term Y") are extracted from definition
  text only, live only on defined records, and are added in dedicated
  passes; targets that don't exist yet are logged in the PR body and added
  when they land.
- **Edge matching discipline (closing pass, PRs #54–#58).** Case-sensitive
  token match for codes, case-insensitive with plural for phrases,
  token-boundary rules (MTSAM ≠ MTSAM-L01), plus occurrence-level
  **containment suppression**: a match whose every occurrence sits inside
  a longer matched span or the record's own term/aliases is not an
  independent use and mints no edge; code-path composition
  (`IBE.metadata['event_context']`) is exempt. Sense-collision edges are
  kept as textual truth and listed in the PR body — Nick ruled keep-all
  on the closing-pass list (2026-07-30). New cycles are surfaced for
  disposition, never repaired unilaterally.
- **Business terms, not software components (IBE/IBEB ruling
  2026-07-30).** Where a business object and the software that produces
  it share a definition site, only the business term is defined. The
  software record stays (`definition: null`, corpus wording preserved
  verbatim in `notes`, outgoing edges dropped, **no** orphan flag — the
  orphan count measures source convolutedness, and the source does define
  it). Applied to `intraday-behavioural-event-builder`,
  `dataenrichmentorchestrator`, `mediumreviewengine`; cited for
  `rsaengine`, `mediumreviewgroup`.
- **External vendors are reference rows (2026-07-30 ruling, Eurex
  precedent).** OpenSanctions, OpenCorporates, Azure OpenAI / AWS
  Bedrock, Azure AI Search are criterion-3 rows in
  `concepts/reference-terms.md`, not records — even when a ruling
  loosely says "record", ownership beats it; flag the deviation.

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
