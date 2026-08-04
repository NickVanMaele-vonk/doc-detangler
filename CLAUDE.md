# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Style

- Answer factually and concisely. 
- Save tokens - avoid multiple hits against the same text, use scratchpads to avoid them. 


## What this repository is

Detangle — an agent/pipeline that turns convoluted markdown specifications
into a logically structured five-document set. The repo holds the normative
specification (`plan/`), the read-only source corpus (`samples/`), the
canonical Phase 3 data (`concepts/`, `registers/`), in-progress working
artifacts (`work/`), and — from ADR-001 onward — the toolchain itself under
`src/detangle/`.

**Form factor (ADR-001, approved 2026-07-30):** a Python package `detangle`
with a CLI. The Claude-skill wrapper is candidate C staged, deferred to
Phase 9.2, and explicitly not built now. Approved tooling: Python ≥ 3.11,
`pytest`, `ruff`, `PyYAML`, `networkx`, and `pandoc` invoked as a subprocess.
Anything beyond that list still needs approval before use.

## Commands

Everything is git + `gh`, plus the package's own tooling:

```bash
git checkout -b <area>/<slug>          # areas in use: plan/, work/, samples/, src/
git add … && git commit                # then:
gh pr create --base main               # every change lands via PR — see C4

python3 -m venv .venv                  # system python is externally-managed
.venv/bin/pip install -e ".[dev]"      # editable install, pytest + ruff
.venv/bin/python -m pytest             # tests/
.venv/bin/ruff check .                 # lint
.venv/bin/detangle validate            # built; `generate` follows (ADR-001 D4)
.venv/bin/detangle graph               # built; rewrites concept-graph.yaml
.venv/bin/detangle graph --check       # regenerate-and-compare guard, for CI
.venv/bin/detangle graph --impact <id> # what depends on this definition
```

`.venv/` is gitignored. `detangle validate` replaces the throwaway per-PR
validation scripts — run it on the records a PR touches (it always runs the
set-wide checks too) instead of writing a new script each time. Exit codes are
the contract: `0` clean, `1` findings, `2` usage or internal error. **`0` and
`1` are verdicts; `2` is the absence of one** — never read `2` as "no
findings". Any unexpected exception exits `2`, never `1`, because branch
policy reads `1` as a completed run that found things. Full table in the
README; `validate` and `graph --check` are separate gates, and
`.github/workflows/ci.yml` runs each as its own job — alongside tests and lint
— on every PR to `main`, so a red run names the gate that failed.

Branch naming follows the areas above (`plan/add-section-ids`,
`work/upd-candidate-terms`, `samples/new`, `src/validate-cmd`). PRs are merged
by Nick, not by the assistant.

`concept-graph.yaml` is derived: never hand-edit it, and regenerate it in the
same PR as any change to a record's `depends_on`, to `registers/cycles.yaml`,
or to the record set itself — `detangle graph --check` fails otherwise.

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

`plan/backlog.md` (`B-n` entries) is **not** normative — parked candidate work,
nothing in it approved or scheduled. Add to it rather than to the three above
when an idea has no phase yet.

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

- Canonical: concept records, including `depends_on` dependency edges, plus
  the registers (see below).
- Derived — regenerated, never hand-edited, hand-editing them fails CI:
  usage edges, first-use links, `index.md`, `concept-graph.yaml`,
  `concept-graph.mmd`, `state/section-map.yaml`, `manifest.yaml`.
  (`concept-graph.yaml` was called the source of truth in plan C6 and the
  README until Nick's 2026-07-30 ruling in ADR-001 — that wording predated
  D9. Every edge in it is a copy of a record's `depends_on` or a derived
  usage edge, so nothing canonical remained in it.)

Anything location- or order-sensitive is derived, because a reorder rots it.

**`concepts/` vs `registers/` — two canonical trees, one rule each (Nick,
2026-07-30).** `concepts/` holds **only** corpus-derived business terms: one
YAML record per concept, every one obeying the same schema and the same
provenance contract (`source` span, `para_hash`, `verified_against`,
definitions assembled from corpus wording per C2). That uniformity is
enforceable — every file under `concepts/` is a record, with no exclusions —
and a carve-out inside it would rot the first time a non-record file landed
there.

`registers/` holds canonical data that is **not** a corpus term: human
rulings whose provenance is a PR thread and a standards clause, not a source
span. Three registers exist:

- `registers/cycles.yaml` — cycle dispositions and entry points
  (criterion 1). Entries are 1:1 with live cycles in the graph; a cycle
  resolved by narrowing gets no entry.
- `registers/reference-terms.md` — the criterion-3 list of regulator- and
  industry-owned terms, which are deliberately *excluded* from the record
  set. Moved out of `concepts/` under this rule.
- `registers/waivers.yaml` — findings with a human disposition but no fix
  yet (step 3.9, built 2026-08-03). An entry matches on `check` + `where`,
  narrowed by an optional `match` substring of the message; a covered
  finding is **printed and counted but excluded from the exit-code
  decision**, so `detangle validate` can be green while a fix waits
  elsewhere. Entries and live findings are 1:1 like `cycles.yaml`: a stale
  entry raises `waiver-stale` (warn), so a fix deletes its waiver in the
  same PR. `register-parse` and the `waiver-*` checks are not waivable — a
  malformed register must not excuse itself. Waiving is a separate channel,
  not a third severity: everything left live still blocks. Do **not** file
  an accepted cycle here (ADR-001 D6): that is an approval and permanent,
  and a waiver is a deferral.

Registers are canonical inputs to generation, never generated. Do not put a
register under `concepts/`: records are loaded as `concepts/*.yaml`, and a
register file there is indistinguishable from a malformed record —
`concepts/removal-register.yaml` is a genuine concept record for the corpus
term "Removal Register", which is exactly the collision to avoid.

**Five documents, one definition site (C9/C10).** Reading order is
`glossary.md` → UCE → SBSP → MCL. `index.md` sits outside it. Placement is
**computed, not judged**, in two limbs: a term used in ≥ 2 of the three
component blueprints goes in the glossary; used in exactly 1, it is defined in
that document — **unless a glossary definition depends on it, in which case it
joins the glossary too** (Nick's Case 3 ruling, 2026-08-03). Never both. Limb 2
is the dependency closure of limb 1 over `depends_on`, taken to a fixpoint, and
it is seeded from `used_in` alone: reading the `placement` field it computes
would let one wrongly-placed record drag its dependency tree in behind it. It
moved 28 records on 2026-08-03 and settled in one hop. The reason it exists is
that limb 1 counts uses in the three blueprints, and the glossary — read before
all of them — is a fourth place terms get used.
`samples/blueprint-analytical-layer.md` is a read-only reference and is
**excluded from the placement count** (Nick's ruling 2026-07-22) — an `(A)`
flag is informational only.

**Two operating modes (D10).** The one-shot detangle run (Phases 5–9) and the
steady-state drift lint that guards every later docs PR (Phase 10). Section
identity is two-layer: tool-stamped `<!-- sec:… -->` markers for identity,
content hashes in a generated section map for change detection. **Line numbers
are provenance nowhere**, and authors — human or AI — are never asked to mint
a section ID.

## Current state

Phases 1, 2 and **all** of Phase 4 are closed — the gate decisions (4.1 D9,
4.2 D7, 4.2a D10) plus 4.3/4.4, settled by ADR-001 (Decisions 1–4 approved
2026-07-30, Decisions 5–6 ruled the same day). **Phase 3 is in
progress**: steps 3.1–3.2 are done, step 3.3 record authoring is complete
(all §1 sections, §3a promotions, multi-document leftovers, and the full
U/S/M single-document bulks, PRs #37–#53), and the closing step 3.4
`depends_on` pass over the whole set is merged (PRs #54–#58: 303 edges
across 116 records; 404 edges set-wide after PRs #59–#60 and #67). Steps
3.5–3.7 are now **generation** tasks. **C9 limb 2 applied 2026-08-03**: 28
records moved to `placement: glossary`, so the glossary is 155 entries (77
undefined) and 204 records stay document-placed (110 undefined, to be
positioned and flagged when the bodies exist in Phase 5).
**Step 3.9 is closed** (2026-08-03):
`registers/waivers.yaml` is built and `detangle validate` exits `0` on
`main`, holding its three source-defect `definition-token` findings as
accepted debt. `detangle validate` and `detangle graph` are built;
`generate` is the remaining command (ADR-001 D4).
`concept-graph.yaml` is generated and committed — dependency edges and the
cycle roll-up now, usage edges when the bodies exist in Phase 5. `concepts/`
holds 359 canonical records; `registers/` holds `cycles.yaml`,
`reference-terms.md` (the hand-authored criterion-3 references list) and
`waivers.yaml`. Nick's 2026-07-30 rulings: the RT*/RD* re-placement of PR #51 is
**superseded** — the first `detangle validate` run surfaced `rd01`,
`rt02`, `rt05` and `rt22` as the only four records in the set whose
`placement` contradicted their `used_in`, and Nick ruled that **the
standard C9 rule governs on the corpus we have**, so all four moved to
`MCL` (each occurs in M only; `rt22` has no (P) presence at all, so the
(P)-promotion rationale never applied to it). Expect this to change
against the full documents; until then placement is computed with no
exceptions, and no override register is needed. Also: keep all
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

The §4 decision register is closed. Its last open row, the word-overload
cluster (items 29–32: "Tier", "Level", "Layer", "IS"), was ruled by Nick
2026-07-30 — **distinct records per sense**, qualified surfaces with one
definition site each, so criterion 1's disambiguation requirement is met
by the record set rather than by a note in the generated glossary — and
applied in PR #67: step 3.3 had already minted ~26 qualified records
whose C9-hygiene notes refused to alias the bare surfaces, so only the
two undefined senses were missing (`level-0`, `sovereign-auction-calendar`,
both orphans). No head record is minted for a bare overloaded word:
nothing in the corpus defines one, so it would violate C2. The §4
definition conflicts (items 1–15) are carried into the records as
`conflict:` blocks and the identity questions (16–28) are answered. The §7c `(P)` dispositions are
closed (PR #63): P-1/P-2 ruled incorrect
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
item that shares its name). **Division of labour (Nick, 2026-07-30):** the
assistant builds the whole toolchain — validator, graph, and the D9
view-generator — as well as delivering ontology content (records, edges).
This supersedes the earlier split in which Nick built the view-generator
himself.

## Session state — 2026-07-31 (family B, provenance, editing surfaces)

**Read this first when picking the thread back up.** The session ran from the
five open `definition-token` findings into the record schema, the C2
provenance model, and how end users will edit the set in steady state. Nothing
in this section is implemented; the record edits below are agreed but not
written.

**We stopped on one question.** `CLOSE_WINDOW_START_MINUTES` is to become its
own record. Does it get `flags: [orphan]`, or `flags: []` following the
IBE/IBEB software-record precedent? The corpus never defines it — it only
assigns it a value — which argues orphan. But its business term owns the
concept, which is the shape the IBE ruling covers, and those records
(`intraday-behavioural-event-builder`, `dataenrichmentorchestrator`) carry
`definition: null`, `depends_on: []` and **no** orphan flag, because the
orphan count measures source convolutedness and in those cases the source
does define the thing. Rule collision; Nick's call.

### Ruled this session

- **Family A — the three `definition-token` findings on `explanation-type`,
  `otc-bilateral-trading` and `persistence-gate` are source-document
  defects.** UCE's `MEDIUM- INVESTIGATE` is a broken hyphen; MCL's
  "EOD only" and SBSP's "BOA Archetype" lack one the record's attributive
  use wants. Fixed later by a human through the B-1 source-correction path,
  held as accepted debt until then. Records are **not** edited and the
  validator is **not** loosened.
- **The waiver register moves from Phase 10.5 to Phase 3, step 3.9** — see
  the registers section above. Designed, approved and built 2026-08-03; the
  three family-A findings are its first entries.
- **Family B resolves structurally, so the C2-unit question never needs
  ruling.** The three options considered were: check a definition's tokens
  against the anchored block only, against the whole corpus for acronyms
  resolving to a record's alias, or against the block plus its `section`
  heading. Both flagged records are fixed by narrowing instead, so the
  status quo (anchored block) stands unchanged.
  - `anonymous-quote-driven-market-structure` → definition narrows to *"The
    market structure in which quote activity is visible to all participants
    but is not immediately attributable."* The MTSAM clause is an
    illustration and the trailing "which determines how quote-based
    manipulation is detected…" clause is a project consequence; both move to
    `notes` verbatim per the ISO 704 §6.5.2 narrowing pattern. Drop
    `depends_on: [mts-associated-markets]`; regenerate the graph. The M
    source span still needs a decision — keep it because `notes` will quote
    that row, or drop it.
  - `close-window` → `definition: null`, `flags: [orphan]`, `depends_on: []`,
    `aliases: []`. The general sense is genuinely absent from the corpus
    (searched: "assessment window", "preceding the close", "end-of-day
    assessment" appear nowhere). Nick supplies it post-deployment, into the
    documents, not as an authored record field.
  - New record `close-window-start-minutes` — `term:
    CLOSE_WINDOW_START_MINUTES`, `placement: MCL`, `used_in: [M]`,
    `definition: null` pending Nick's eventual *"the software variable
    denoting the close window"*, `depends_on: []` because edges come from
    definition text and there is no definition yet. Corpus value preserved
    verbatim in `notes`: `CLOSE_WINDOW_START_MINUTES = 30 minutes before
    17:00 CET`. The alias leaves `close-window` either way (MWBR_ANOMALOUS
    precedent) — a parameter name is not a synonym for a business term.
- **Declared document versions are to be removed**; git is the version
  control, and hand-typed version strings never reflect reality. Carry two
  things: the existing skew (MCL titled v21 with a v22 block; MCL applying
  to UCE v28 while SBSP cites v30) must survive as a recorded finding rather
  than being harmonised away with the numbers, and release identity has to
  land somewhere for audit — git tags bound by `manifest.yaml`.
- **Promotion is automatic, after informing the human.** When an edit makes a
  term cross from one document into two, the message is: *"Your latest edit
  leads to `<concept>` being used in more than one source document. The
  definition will be moved to the glossary and all documents that use it,
  including this one, will receive links to it."* Then the tool reconfigures.
- **`glossary.md` and `index.md` are committed and tracked in git**, like
  `concept-graph.yaml`. They still get a regenerate-and-compare guard, a
  banner, and a CI failure that names the record to edit instead.

### Design learnings that outlive the session

- **`samples/` is scaffolding.** It is replaced by the full documents once
  the tool exists, and those documents are the living set humans edit.
  "Input, never output" was a property of a fixed test fixture, not a
  standing principle. It follows that **`corpus` provenance is a historical
  fact, not a status anything can migrate into** — it says the wording
  traces to what the business had written when the run consumed it, and
  `verified_against.git_blob` keeps that verifiable however the file is
  later rewritten. Authored content never becomes corpus content.
- **Provenance is two axes, not one enum.** Anchoring — is there a source
  span? — is separate from authorship and assurance. `corpus`/`human`/`AI`
  as one field cannot express AI-written text sitting inside the corpus,
  which is exactly this project's situation (see the corpus-provenance
  bullet in plan §3 Scope). Authored content carries author, approver, PR
  and the set version it entered at; it has no `para_hash`, and that absence
  is what stops the next version's analysis reading it as source.
- **The `definition-token` check is a proxy for C2, not C2.** C2 is
  claim-level, checked by the Phase 7 harness, and has two limbs: every
  claim traces to the source **or is explicitly marked as bridging text**.
  The record-layer check is deliberately stricter because the harness does
  not exist yet. Criterion 7 already covers the orphan case — a glossary
  entry with no source definition is Category C in full and always raises a
  PR comment.
- **Bridging markers must be generated, never typed.** Same principle as
  C12's section IDs: marking that depends on a human remembering to write
  `<!-- AI addition:start -->` is marking that goes missing exactly where it
  mattered.
- **The `definition` field conflates three things and `source:` is
  record-level.** A definition proper, an illustration, and a consequence
  sit in one string, while the token check tests the whole string against
  the **union** of every anchored block — so a span imported for one clause
  can launder another. On `anonymous-quote-driven-market-structure`, adding
  MCL block `881a98c9…` as a third span would have cleared the MTSAM finding
  outright without improving the record. **82 of 173 defined records are
  multi-clause** (em-dash, semicolon, or over 35 words); 153 contain a
  code-shaped token. The fix is provenance per clause, with ISO 704 §6.4.4's
  substitution principle as the test for what is definitional. Not designed.
- **Edge-minting cannot be a blanket rule once clauses move out of the
  definition.** `close-window` → `mts-associated-markets` should go: you do
  not need the venue to understand what a close window is, and keeping it
  would order the glossary and answer impact queries wrongly.
  `persistence-gate` → `medium-investigate` must stay, though it sits in a
  structurally identical trailing clause, because the cap *is* the gate's
  point. An instantiation creates no comprehension prerequisite; a
  consequence naming a defined term usually does.
- **Definition sites are mostly not in the glossary.** 127 records are
  glossary-placed, 231 document-placed (100 UCE, 71 SBSP, 60 MCL); of the
  173 defined, 69 render to the glossary and 104 into document bodies. So
  D9's "single definition site becomes structurally impossible to violate"
  holds for the glossary-placed only. Nick's leaning is body-canonical for
  the 231, not yet ruled.
- **Editing surfaces.** Direct markdown editing stays the norm (C12) — the
  corpus is overwhelmingly non-definitional. The tool is required for one
  class only: definitions of glossary-placed terms. Nobody edits
  `glossary.md` or `index.md`. A PR diff is not a viable surface for
  non-IT-literate business users: it shows hunks with ~3 lines of context in
  raw markdown with `+`/`-` gutters, commenting requires the source view
  rather than the rendered one, and a topologically-ordered generated file
  turns a one-word fix into large reorder churn. **So the tool UI is
  load-bearing, not a convenience**, and nothing in Phase 8 or 9 scopes it
  yet. The reading-time route only has to serve the team, not external
  readers (Nick, 2026-07-31).
- **The comment→edit round-trip only exists inside a PR.** D9's source-map
  anchors resolve a comment on generated markdown back to its record, but
  that requires an open PR with `glossary.md` in the diff. Someone reading
  the published glossary who spots a wrong definition has no comment
  surface at all — which is the common case, and why the UI matters.
- **Anchors must be emitted markers, never line offsets** — a regenerated
  glossary reorders topologically, and line numbers are provenance nowhere
  (D10).

### Open questions, roughly in blocking order

1. `close-window-start-minutes` orphan flag — the stopping point above.
2. Inline redefinition: when someone writes a glossary term's definition into
   a body, does the lint propose lifting it into the record, or only block
   with a pointer? Asked twice, unanswered.
3. May an authored definition be AI-drafted and human-approved, or must a
   human write it? Criterion 7 calls an invented definition the highest-risk
   output the tool can produce.
4. Body-canonical for the 231 document-placed definitions — stated as
   probably fine, never ruled.
5. Provenance schema shape: field names, whether authored text sits in
   `definition:` or its own field, and whether `flags: [orphan]` survives an
   authored definition. It must, or the convolutedness measure decays as
   fast as the work gets done.
6. ~~Waiver register design (step 3.9) — schema plus suppression semantics.~~
   **Closed 2026-08-03** — designed, approved and built; see the registers
   section above. Two sub-decisions ruled with it: one register, not a
   separate `registers/source-corrections.yaml` (closing backlog B-1 point
   4), and `review_by` recorded but not enforced, because an expiry check
   would make CI's verdict turn on wall-clock.
7. Splitting `definition` into definition / illustration / note with
   per-clause provenance — whether to do it at all, and whether in Phase 3.
8. Demotion: a term losing its second usage drops out of the glossary, which
   under body-canonical migrates its definition from record to body text.
   The reverse of the promotion ruling, unexamined.
9. Guarding the two newly committed views: regenerate-and-compare, banner,
   CI redirect message.
10. ~~PR #71 — merge red now, or hold until 3.9 makes `detangle validate`
    green.~~ **Closed** — merged 2026-07-31 (commit `0f40522`); 3.9 has since
    made the gate green, so `detangle validate` can now be marked required in
    branch protection.

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
  industry-owned terms go to `registers/reference-terms.md` rows, never
  records, even when used in ≥2 docs (criterion 3; MAR Article 12/16, ADA,
  quote stuffing, Eurex, OLO, HHI). (P)-only terms are held as candidate
  rows until a U/S/M usage appears (ruling on PR #18). **Never hand-set
  `placement`**: run `detangle validate`, which computes both limbs and
  names the expected value. A record with `used_in: [U]` and
  `placement: glossary` is limb 2, not a mistake.
- **Code families get records per code.** SB-xx archetype rows and
  MTSAM-Lxx register entries used in ≥2 docs are records in their own
  right, as values of their master term (sb-26 precedent).
- **Cycle policy (applied 2026-07-29, ISO 704 §6.5.2).** A circular edge
  whose source clause is consequence/elaboration is resolved by narrowing
  the definition proper — the clause moves verbatim to `notes`, and the
  edge is dropped. A genuinely contrastive pair is kept as a documented
  outer circle (liquidity-driven-reaction ↔ identity-driven-coordination is
  the only accepted cycle); the view generator must condense that SCC for
  the topological sort. **Accepted cycles are recorded in
  `registers/cycles.yaml`**, one entry per live cycle, and the generator
  rolls them into `concept-graph.yaml` — a narrowed cycle gets no entry,
  so entries and live cycles stay 1:1. Each entry also carries the
  criterion-1 `entry_point`: the member defined first, whose cross-reference
  becomes the marked forward reference. For the accepted pair that is
  `liquidity-driven-reaction` (Nick, 2026-07-30) — default before exception,
  so the identical-observable-pattern clause is never the deferred one.
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
  `registers/reference-terms.md`, not records — even when a ruling
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
