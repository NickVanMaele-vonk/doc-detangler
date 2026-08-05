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
artifacts (`work/`), the Phase 5 evaluation set (`eval/`), and — from ADR-001
onward — the toolchain itself under `src/detangle/`.

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
.venv/bin/detangle validate            # all three commands built (ADR-001 D4)
.venv/bin/detangle graph               # built; rewrites concept-graph.yaml
.venv/bin/detangle graph --check       # regenerate-and-compare guard, for CI
.venv/bin/detangle graph --impact <id> # what depends on this definition
.venv/bin/detangle generate            # seeded glossary.md; refuses to
                                       # overwrite it (exit 2) — --force only
.venv/bin/detangle generate --check    # read-only compare against a regeneration
.venv/bin/detangle restructure --plan <plan.yaml> --out <doc.md>
                                       # execute a reorder plan (ADR-002);
                                       # refuses to write from a plan with an
                                       # error-grade finding, and runs the
                                       # criterion-5 token-parity check
.venv/bin/detangle restructure … --report <dir>
                                       # also write the 8f self-report:
                                       # move-map.md, counts.md, exceptions.md
.venv/bin/detangle restructure … --check   # re-execute and byte-compare
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
are the source of truth **for the ontology** — identity, placement,
provenance, dependency edges. `index.md` is a generated view with source-map
anchors, so a reviewer's PR comment round-trips deterministically back to the
record. Two things changed on 2026-08-04: the definition *prose* is canonical
in the document that defines it, `glossary.md` included, which is edited
rather than generated; and there is no `concept-graph.mmd` — the Mermaid
render is produced per concept on demand. Document
*bodies* are not ontology; they stay markdown tracked as moved / derived /
added (criterion 7).

**Canonical vs derived is the distinction that governs everything (D10 §4).**

- Canonical: concept records, including `depends_on` dependency edges, plus
  the registers (see below). **But not the definition prose, from
  2026-08-04 (D9 amendment): the definition site owns the definition.** Every
  definition is canonical in the document that defines it — **`glossary.md`
  included, which becomes the fourth editable document rather than a
  generated view** — and the record's `definition` field is a derived copy
  everywhere, byte-compared like any other derived artifact. All 172 defined
  terms: 78 in the glossary, 94 across the three documents. No exception to
  remember. The record still owns the **ontology**: identity, `placement`,
  `used_in`, `source` provenance, `depends_on`, `flags`, `conflict`,
  `review`, `notes`. Each document delimits the definitions it owns with
  tool-stamped `<!-- concept:<id>:start -->` / `<!-- concept:<id>:end -->`
  markers, which is what keeps the lift deterministic; without them the
  structural guarantees would rest on re-parsing prose, the exact failure D9
  exists to prevent. **Prospective** — it takes effect per document as each
  comes to exist, and for the glossary when the drift lint that guards it
  exists; today `glossary.md` is a **seed** that `detangle generate` wrote
  once, and **nothing guards it** — `generate --check` still exists as a
  command but was withdrawn as a CI gate, so an edit to the file is mirrored
  nowhere and checked by nothing until the drift lint is built. Re-running
  `detangle generate` rewrites the file in full and would discard every human
  edit; there is no guard against that either.
- Derived — regenerated, never hand-edited, hand-editing them fails CI:
  usage edges, first-use links, `index.md`, `concept-graph.yaml`,
  `state/section-map.yaml`, `manifest.yaml`. Not in this list: the Mermaid
  render, which is on-demand rather than committed, and `state/notices.md`,
  which is generated but deliberately unguarded (both Nick, 2026-08-04).
  (`concept-graph.yaml` was called the source of truth in plan C6 and the
  README until Nick's 2026-07-30 ruling in ADR-001 — that wording predated
  D9. Every edge in it is a copy of a record's `depends_on` or a derived
  usage edge, so nothing canonical remained in it.)

Anything location- or order-sensitive is derived, because a reorder rots it.

**A body edit proposes edges; it never applies them (Nick, 2026-08-04,
reaffirming D10 element 4).** The lint extracts candidate `depends_on` edges
from the changed definition block, diffs them against the record's canonical
list, and reports the difference. It changes nothing. The reason is that
identical-looking clauses have needed opposite rulings —
`close-window → mts-associated-markets` was dropped while
`persistence-gate → medium-investigate` was kept — and an edge sets reading
order, answers impact queries, and can relocate real text through a placement
change. Detection is automatic; the disposition is Nick's. Contrast the
promotion rule, which *is* applied automatically after informing the human,
because a placement flip is mechanical and an edge is a claim.

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
  decision**, so a command can be green while a fix waits elsewhere.
  **All three commands read the register** (Nick, 2026-08-05) — before that
  only `validate` did, so a finding raised by `generate` or `graph` could not
  be deferred at all. Entries and live findings are 1:1 like `cycles.yaml`: a
  stale entry raises `waiver-stale` (warn), so a fix deletes its waiver in the
  same PR — but **staleness is judged only by the command that ran the
  check**, because a command that never ran one cannot prove its waiver dead,
  and the false alarm would block a required gate. Each module declares the
  checks it raises in a `CHECKS` constant, kept honest by
  `tests/test_checks_declared.py`. Not waivable: `register-parse`, the
  `waiver-*` checks — a malformed register must not excuse itself — and the
  four **drift** checks (`graph-drift`, `graph-missing`, `glossary-drift`,
  `glossary-missing`), because a waiver defers work and regenerating a
  derived file is one command, so there is nothing to defer; C6 and ADR-001
  D5 hold only while a hand-edited artifact cannot excuse itself. Waiving is a separate channel,
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

**Two input sets (Nick, 2026-08-05).** The **detangle set** (`components` in
`detangle.toml [documents]` — U/S/M today) is what gets restructured, and it
is the only set that counts for placement, orphan measurement, omission
checking and the verbatim-token diff. The **reference set** (`references` —
A and P today, plus future side documents business users write) is
read-only: never modified, never restructured, never stamped, never
counted — but citable for provenance, and **a definition found only in a
reference document is lifted as the definition**, with a real span into the
reference file. The term keeps its `orphan` flag after the lift: the flag
measures the detangle set. `mts-spa` (defined entirely from A, `flags:
[orphan, A]`) is the live example. Adding a reference document is a config
edit, never a code change. See research-memo §Two input sets; the old
per-document A/P rulings are instances of this rule.

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
across 116 records; **402** edges set-wide today — PRs #59–#60 and #67 took
it to 404, and the 2026-07-31 narrowing rulings then dropped two). Step 3.5
is built; 3.6's `index.md` awaits the bodies and its Mermaid half was
cancelled; 3.7 awaits the bodies — **both now close behind Phase 5**, which
produces the first bodies, so neither is the next thing to work on.
**C9 limb 2 applied 2026-08-03**: 28
records moved to `placement: glossary`, so the glossary is 155 entries (77
undefined) and 204 records stay document-placed (110 undefined, to be
positioned and flagged when the bodies exist in Phase 5).
**Step 3.9 is closed** (2026-08-03):
`registers/waivers.yaml` is built and `detangle validate` exits `0` on
`main`, holding its three source-defect `definition-token` findings as
accepted debt. `detangle validate`, `detangle graph` and `detangle generate` are all built
(ADR-001 D4). `generate` seeded `glossary.md`, which is now edited by humans
rather than regenerated; `index.md` is left to step 3.6, and no
`concept-graph.mmd` is produced at all.
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

**Phase 5 has started — step 5.1 is done (PR #90, 2026-08-04).**
`eval/README.md` designates the three shortened blueprints as the test inputs,
each pinned to the git blob it carried at commit `a088ee9`; `A`, `P` and the
two CSV fixtures are excluded. **The claim that this exclusion was "verified
to cost nothing" was wrong** (corrected 2026-08-05): 2 records cite `A` and
17 cite `P` under `source:` — `mts-spa` is defined entirely from `A` — and
10 more cite `P` in `conflict:` blocks, so the fabrication check needs the
reference set available, and lifted definitions trace outside the test
inputs by design. **Phase 5 closed 2026-08-05.** Step 5.2's golden triple for `U` is approved
and merged (PR #99, on the reorder plan of PRs #93/#96): `eval/golden/uce.md`
(six sections plus overview and shared-terms section, 35 record-verbatim
definition blocks, stamped `sec:`/`concept:` markers), the 73-entry glossary
slice (zero forward references), the 155-term index slice (84 marked
undefined), and the four 8f artifacts. Zero orphan definitions were drafted
(step 3.3 was the exhaustive assembly pass); the overview is the only
Category C text. None of the 13 `notes` staging-post clauses belongs to `U` —
all are glossary-placed. Step 5.3 (`eval/review-load.md`) measured 289
claims, 35 terms changed, 84 orphans and 9 comment clusters, confirmed the
term cap (200), set `param-max-comments-per-PR` (25) and set
`param-low-confidence-threshold` (0.80, **provisional — mandatory
re-baseline at 6.2** against the prototype's first real confidence
distribution). Two approved deviations to remember from `exceptions.md`: the
golden carries no generated navigation (first-use links wait for their
generator), and the orphan roster lives in the exceptions list rather than
as waiver entries (an unmatched waiver would trip `waiver-stale`).
**Pinned now, re-baselined later** (Nick's ruling): the backlog B-1 source
correction that fixes the three waived `definition-token` hyphen defects
rewrites all three blobs and voids the golden; the re-baseline updates the
blob column in the same PR as the correction.

**Phase 6 is in progress**, on ADR-002 (approved 2026-08-05, PR #101): the
reorder plan is **data** — `eval/golden/uce.plan.yaml` — and `detangle
restructure` executes it deterministically, authoring nothing. Build steps
1 and 2 are merged (PRs #102, #104): the plan schema/loader/validation, and
the execution engine, whose machine run of the real plan **reproduces the
approved golden** (identical section markers, all 35 definition blocks
byte-equal, empty token diff both ways) — held as a test. Step 3 is merged
too, in halves: 3a the criterion-5 `token-parity` check inside the command
(PR #105), 3b the generated 8f self-report behind `--report <dir>`. Step 4
records the 6.2 comparison in `eval/`, and 6.2 is not
done until `param-low-confidence-threshold` has been re-baselined against
the first artifact carrying a mapping score (the Phase 7 harness dry-run).

**The 8f split (Nick, 2026-08-05).** The report generator writes only what
the run measured — block moves, drops, category tallies, the criterion-5
accounting, the undefined-term roster, forward references. A ruling is a
human's sentence and the tool never writes one: the plan carries an
`exceptions:` list of one line per ruling (`title` + `where`), and the
report names it and points at where the reasoning is written rather than
reprinting it, so the wording lives in one place. The declarations exist
because the 8c budget counts PR comments and a comment the tool cannot see
is one it would count wrong; over `param-max-comments-per-PR` the run
reports and writes no document. The real plan reports **9 clusters** — the
5.3 baseline exactly, 3 measured and 6 declared.

Two golden defects the generator surfaced, both awaiting Nick's disposition:
the golden's `exceptions.md` counts **84 orphans** where 83 are orphans and
`intraday-behavioural-event-builder` is undefined by the IBE/IBEB ruling
instead (it carries no orphan flag); and its §9 "forward references: zero"
checked the glossary slice, not `uce.md`'s own definition order, where
`persistence-gate` and `dif-analytical-domains` both depend on
`participant-interaction`, defined further down.

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

## Session state — 2026-08-04 (step 3.5 built; two rulings on definition homes)

**Two rulings landed this session, both prospective — nothing in `concepts/`
changes today.** They are written up in the research memo (§D9 amendment,
§D10 element 4 note), the rubric (criteria 3 and 9) and C12.

1. **The definition site owns the definition** — and after the second
   ruling, that means **all 172 definitions**, because `glossary.md` becomes
   the fourth editable document rather than a generated view. The record's
   `definition` is a derived copy everywhere; the record still owns the
   ontology. Conditional on tool-stamped `<!-- concept:<id>:start -->`
   markers, because a byte-comparable mirror needs a deterministic lift and
   D9's whole argument was that prose canonicity destroys provability.
2. **`depends_on` stays canonical; a body edit proposes edge changes and
   waits.** Detection automatic, disposition Nick's.
3. **The guard reorders the glossary when a human breaks topological order**,
   with a PR comment. This narrowed a hard prohibition into a rule: the guard
   may make word-preserving edits, verified to change no words, and must
   comment; it may never change meaning.
4. **Provenance for authored definitions.** One `definition` field, with
   provenance a secondary block. Authored text joins the document set but
   **never acquires a `para_hash`** — a span asserts the business wrote the
   wording, and tool output must never be able to claim that, or the next run
   reads its own output as source. `flags: [orphan]` therefore survives an
   authored definition. Change detection for everything is the section map's
   content hash, not `para_hash`; a provenance claim is asserted against that
   hash, and an edit breaking corpus provenance **auto-demotes** down
   criterion 7's moved → derived → added ladder with a comment. General rule:
   **the guard may weaken a provenance claim on its own; it may never
   strengthen one.**
5. **AI may draft a definition; a named human approves**, and the draft shows
   the corpus usages it was assembled from, or says there are none.
6. **`definition` is not split** into definition / illustration / note. The
   marked block is the definitional boundary: definition proper inside the
   markers, illustration and consequence as ordinary prose outside. 81 of the
   172 defined records are multi-clause and 99 cite more than one span, which
   is the surface the old field-splitting design was aimed at; narrowing the
   checked text to the block removes most of it. **`notes` is a staging post,
   not a destination** — records are not part of the output set, so the 13
   records holding narrowed corpus wording must land it in document prose in
   Phase 5 or it is an omission under criterion 4.
7. **Demotion is not automatic, unlike promotion.** Promotion is required
   (two documents means the glossary, or C9 breaks), so the tool acts and
   informs. Demotion is optional — the rubric says a single-document term
   *may* move — so the tool reports and waits, and the message says plainly
   that nothing is wrong. It also moves prose across files and rewrites
   first-use links, and usage counts wobble, so an automatic rule would shunt
   definitions back and forth.
8. **`state/notices.md`** carries what is worth knowing but is not a defect.
   Findings block, waivers defer a real problem, notices are neither — a
   notice raised as a finding would make "nothing is broken" a red build,
   which is the trap that already caught the overview gap and `code_quality`.
   Committed, so new entries appear in the PR diff; **unguarded**, because a
   stale notices file must never block a PR. Carries a "generated from commit
   X at time Y" header — visible age instead of enforcement, which
   `concept-graph.yaml` cannot have without breaking byte comparison.
9. **Inline redefinition blocks, but shows both texts.** Only bites for
   glossary-placed terms now. One-click fix offered *only* where the body
   text verbatim restates the glossary definition; otherwise show and wait,
   because the difference is either an improvement or a contradiction.
10. **No `concept-graph.mmd` is committed.** `detangle graph --mmd <id>`
   prints one concept's neighbourhood on demand. 359 nodes render as a
   238-node tangle plus 108 loose dots; a single concept is two or three
   boxes, eight one step out. Amends C6 and D2.
11. **`close-window-start-minutes` keeps `flags: [orphan]`** — already
   applied on `main`, and the open-questions list saying otherwise was
   stale. The IBE/IBEB carve-out needs the source to define the concept
   under its business name, and here it does not: `close-window` is itself
   an orphan.

**What the glossary ruling closed and re-opened.** Closed: where the overview
lives (it is just the document's own overview, written in place, so no
`registers/glossary-overview.md` is needed) and the waiver-staleness scoping
that existed only to waive the overview gap. Re-opened: `detangle generate
--check` cannot be the fourth CI gate — byte-comparing a file humans edit is
incoherent — so it becomes a drift lint, and **the gate stays out of
`ci.yml` until that lint exists**. `detangle generate` keeps its job as the
seeder: it produced the committed `glossary.md`, which is the seed the
editable file starts from.

**Watch the counts.** `104` document-placed defined terms was stale — it
predates C9 limb 2, which moved 28 records (10 defined) into the glossary.
The live figures: **359 records, 172 defined; glossary 155 (78 defined, 77
undefined); document 204 (94 defined, 110 undefined)**, UCE 82 / SBSP 63 /
MCL 59. Both `plan/detangle-agent-plan.md` and `README.md` carried `104` and
are fixed.

**Repo went public on 2026-08-04** so branch protection could be used. One
ruleset, `protect-main`, now covers everything: `deletion`,
`non_fast_forward`, `pull_request`, `required_status_checks` (the three CI
contexts, strict) and `code_scanning`. Two older overlapping rulesets were
deleted. CodeQL default setup is on (`python`, `actions`); `.claude/` is
untracked and gitignored because a single stray `.js` file made CodeQL detect
a JavaScript language it could not analyse. `code_quality` is deliberately
**not** in the ruleset until that feature is actually enabled — an
unsatisfiable gate blocks every PR, which is how PR #81 got stuck once
already.

## Session state — 2026-08-04 (`detangle generate`, step 3.5 built)

**Read this first.** `detangle generate [--check]` is built and `glossary.md`
is generated and committed: 155 entries in the graph's topological order, 78
defined, 77 rendered with an explicit "not defined in the corpus" note, a
`<!-- concept:<id> -->` marker before every heading, and a sources table
binding each of the five corpus documents to the git blob its spans were
verified against. All seven approved design points are implemented except
point 6, and the reason is worth carrying:

- **The fourth CI gate is held back.** Point 2 makes the overview a marked
  gap *and a finding*, so a clean `generate` run exits `1`. Adding
  `generate --check` to `ci.yml` now would put a permanently red job on
  `main`, which trains reviewers to ignore CI. It lands when the finding is
  dispositioned — the overview gets written, or it gets a waiver.
- **Waiving it needs one small change first.** `stale_findings` is called on
  every full `validate` run and flags any entry that matched nothing, so a
  waiver for a `generate`-raised finding would make `validate` report
  `waiver-stale`. Scoping staleness to the checks the running command owns
  fixes it — and fixes the same latent bug for `validate --no-tables`. Not
  built: it is a design decision, and the design is Nick's.
- **Where the overview text lives is open.** It cannot be typed into
  `glossary.md`, which is regenerated and byte-compared. A register, a
  front-matter file, or a record — Nick's call. The placeholder block says so
  rather than telling a reader to edit a generated file.

Two things were rendered beyond the seven points, both required by rubric
criteria the glossary is itself subject to: **aliases** per entry (criterion
3) and a **generated bridging marker** on the accepted cycle's forward
reference (criterion 1 clause 2, citing `registers/cycles.yaml`). Forward
references are computed from the rendered order, not assumed from the cycle
register — which confirmed C9 limb 2 empirically: no glossary definition
depends on a term outside the glossary, so that one cycle edge is the file's
only forward reference.

Definitions render as **one physical line each, unwrapped**. Wrapping reflows
a paragraph when one word changes; this file exists to be commented on, and a
one-line diff points at one record.

## Session state — 2026-08-03 (waiver register, C9 limb 2, generation design)

**Read this first.** Everything below is merged and green on `main`; the
2026-07-31 section that follows is still live for its unresolved items.

**Landed.** PR #78 built the waiver register (step 3.9) — `detangle validate`
now exits `0`, holding its three source-defect findings as accepted debt, so
it can be marked a required check in branch protection. **That marking is a
GitHub setting only Nick can apply, and it has not been done.** PR #79
applied C9 limb 2: 28 records moved to `placement: glossary`, the glossary is
155 entries (77 undefined), 204 records stay document-placed (110 undefined).

**Why limb 2 exists, because it will look surprising in a record.** Preparing
`glossary.md` surfaced 34 edges failing criterion 1's own formal check —
20 glossary entries lean on a term defined later, in a document body, and the
glossary is read first. Limb 1 counts uses across the three component
blueprints; the glossary is a fourth place terms get used, which nothing
counted. So `used_in: [U]` with `placement: glossary` is correct, not a bug.
Never hand-set `placement` — run `detangle validate`, which names the expected
value.

**`detangle generate` was the next task and is now built** — see the
2026-08-04 section above.

**Open questions from this session, none blocking 3.5:**

1. ~~`concept-graph.mmd` scoping.~~ **Closed 2026-08-04** — no whole-set file
   is committed; `detangle graph --mmd <id>` renders one concept's
   neighbourhood on demand.
2. `index.md` (step 3.6) stays blocked until the document bodies exist: DoD
   criterion 4 wants the document and section for each of the 104
   document-placed defined terms.
3. The 110 undefined document-placed terms need positioning before first use
   and a flag to a human (Case 1.a) — a Phase 5 surface, unbuilt.

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
  substitution principle as the test for what is definitional. **Ruled
  2026-08-04: not split — the marked definition block is the boundary
  instead.** Figures here are as of 2026-07-31 and predate C9 limb 2; the
  live counts are 81 of 172 multi-clause, 142 with a code-shaped token.
- **Edge-minting cannot be a blanket rule once clauses move out of the
  definition.** `close-window` → `mts-associated-markets` should go: you do
  not need the venue to understand what a close window is, and keeping it
  would order the glossary and answer impact queries wrongly.
  `persistence-gate` → `medium-investigate` must stay, though it sits in a
  structurally identical trailing clause, because the cap *is* the gate's
  point. An instantiation creates no comprehension prerequisite; a
  consequence naming a defined term usually does.
- **Definition sites are mostly not in the glossary.** *(Figures as of
  2026-07-31, before C9 limb 2 moved 28 records. Live: 155 glossary-placed,
  204 document-placed — UCE 82, SBSP 63, MCL 59 — and of the 172 defined, 78
  render to the glossary and 94 into document bodies.)* 127 records were
  glossary-placed, 231 document-placed (100 UCE, 71 SBSP, 60 MCL); of the
  173 defined, 69 rendered to the glossary and 104 into document bodies. So
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
  glosses or (P)-only expansions into definitions. **Narrowed, not
  repealed, 2026-08-05:** an expansion or gloss is still not a definition,
  but a genuine definition in a reference document is lifted with its
  provenance span, and the `orphan` flag survives the lift. **"Lightly stitched"
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
  edge is dropped. `notes` is a **staging post, not a destination** (Nick, 2026-08-04): records are not part of the output set, so a corpus clause left there is an omission under criterion 4. It lands in document prose beside its definition block when Phase 5 writes the body. A genuinely contrastive pair is kept as a documented
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
- **PR mechanics.** ≤ `param-max-terms-changed-per-PR` (200, raised from 25
  on 2026-08-05) files counting
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

**`samples/` cannot be untracked, and removing it would not do what it looks
like it does** (investigated 2026-08-04; a proposal to gitignore and purge it
was raised and withdrawn). Two reasons, both worth keeping so the idea is not
re-proposed blind. First, `detangle validate` reads the corpus from HEAD and
from disk — `git rev-parse HEAD:<doc>` in `records/checks.py`, then the file
itself in `records/spans.py`, which raises `UsageError` (**exit 2**) when it is
missing. It is a required check on `protect-main`, so untracking `samples/`
blocks every PR: the unsatisfiable-gate trap that already stuck PR #81. Second,
if the aim were keeping corpus wording out of a public repo, deleting
`samples/` does not achieve it — `concepts/` holds ~186k characters of verbatim
corpus wording in `notes` plus ~33k in `definition`, and `glossary.md` another
~56k, against ~369k for the three blueprints. A purge would have to take
`concepts/`, `glossary.md` and `work/term-extraction/` with it, which is the
whole project. Making the repo private is the coherent version of that wish;
the repo is public **only** so branch protection could be used.

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
hand-edit a generated artifact; never auto-"fix" a document body in steady
state — with one narrow exception ruled by Nick 2026-08-04: **the guard may
make word-preserving edits, machine-verified to change no words, and must
leave a PR comment when it does.** Stamping section IDs and reordering
glossary entries left out of topological order are the two authorised cases.
Changing meaning is never authorised — where the tool believes prose is
wrong, it comments and a human decides.
