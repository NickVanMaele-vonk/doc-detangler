# Detangle — tool architecture

The master document for **how the parts fit together**. It is descriptive, not
normative: the binding statements live in `plan/detangle-agent-plan.md`
(constraints **C1–C12**), `plan/definition-of-done.md` (criteria **1–9**,
`param-*`), `plan/research-memo.md` (decision register **D1–D10**) and the
ADRs (`plan/adr-*.md`). Cite those identifiers, not this file, when something
has to hold. What this file adds is the connective tissue — the rulings and
design learnings that no single one of those documents owns, and that would
otherwise have to be reconstructed by reading several of them at once.

Historical project state is in git (commits and PRs); future candidate work is
in `plan/backlog.md`; user-facing operation is in `README.md`.

Counts in this file are avoided deliberately (backlog **B-2**): the record set
is the authority, and `detangle validate` / `detangle graph` recompute every
figure on demand.

---

## 1. The concept graph is the backbone, not a side artifact

Directed edges "definition of X uses term Y". From that one structure:

- **topological sort** gives the reading order and the glossary's own order;
- **alphabetical projection** of the same term set gives `index.md`;
- **forward reachability** is impact analysis (`graph --impact`);
- **backward reachability** answers what must be defined first
  (`graph --requires`);
- **cycle detection** surfaces genuinely circular definitions for human
  disposition;
- **orphans** (used but never defined) measure how convoluted the source is.

Anything location- or order-sensitive is derived, because a reorder rots it.

## 2. Ontology-first (D9)

Structured concept records — one YAML file per concept under `concepts/` — are
the source of truth **for the ontology**: identity, `placement`, `used_in`,
`source` provenance, `depends_on`, `flags`, `conflict`, `review`, `notes`.

`index.md` is a generated view with source-map anchors, so a reviewer's PR
comment round-trips deterministically back to the record. **Anchors must be
emitted markers, never line offsets** — a regenerated view reorders
topologically, and line numbers are provenance nowhere (D10).

Document *bodies* are not ontology; they stay markdown, tracked as
moved / derived / added (criterion 7).

### The definition prose is canonical at the definition site (D9 amendment, 2026-08-04)

Every definition is canonical in the document that defines it — **`glossary.md`
included, which is the fourth editable document rather than a generated view** —
and the record's `definition` field is a derived copy everywhere, byte-compared
like any other derived artifact. No exception to remember.

This is conditional on tool-stamped `<!-- concept:<id>:start -->` /
`<!-- concept:<id>:end -->` markers delimiting the definitions a document owns.
They are what keeps the lift deterministic; without them the structural
guarantees would rest on re-parsing prose, the exact failure D9 exists to
prevent.

It is **prospective**: it takes effect per document as each comes to exist, and
for the glossary when the drift lint that guards it exists. Until then
`glossary.md` is a **seed** that `detangle generate` wrote once, and **nothing
guards it** — `generate --check` exists as a command but was withdrawn as a CI
gate, so an edit to the file is mirrored nowhere and checked by nothing.
Re-running `detangle generate` would rewrite the file in full and discard every
human edit; the command therefore refuses to overwrite (exit `2`) without
`--force`.

### What the seeded glossary renders, and why

Entries in the graph's topological order, one `<!-- concept:<id> -->` marker
before every heading (so a PR comment resolves to the record behind it), and a
sources table binding each corpus document to the git blob its spans were
verified against. Two things beyond the approved design points, both required by
rubric criteria the glossary is itself subject to: **aliases** per entry
(criterion 3), and a **generated bridging marker** on the accepted cycle's
forward reference (criterion 1 clause 2, citing `registers/cycles.yaml`).

Forward references are computed from the rendered order, not assumed from the
cycle register — which confirmed C9 limb 2 empirically: no glossary definition
depends on a term outside the glossary, so that one cycle edge is the file's
only forward reference.

Definitions render as **one physical line each, unwrapped** (§12).

Terms with no corpus definition render with an explicit "not defined in the
corpus" note rather than being omitted.

**The overview lives in the file itself.** It is just the document's own
overview, written in place; no `registers/glossary-overview.md` is needed. The
question was open only while `glossary.md` was byte-compared, and the 2026-08-04
ruling closed it by making the file editable.

## 3. Canonical vs derived — the distinction that governs everything (D10 §4)

**Canonical**: concept records (including `depends_on`) and the registers.
**But not the definition prose** — see §2.

**Derived** — regenerated, never hand-edited; hand-editing fails CI: usage
edges, first-use links, `index.md`, `concept-graph.yaml`,
`state/section-map.yaml`, `manifest.yaml`.

Two deliberate exclusions from the derived list: the per-concept Mermaid
render, which is on-demand rather than committed, and `state/notices.md`,
which is to be generated but deliberately unguarded (both Nick, 2026-08-04).
Neither is built (backlog B-6, B-7).

`concept-graph.yaml` was called the source of truth in plan C6 and the README
until Nick's 2026-07-30 ruling in ADR-001 — that wording predated D9. Every
edge in it is a copy of a record's `depends_on` or a derived usage edge, so
nothing canonical remained in it. Regenerate it in the same PR as any change to
a record's `depends_on`, to `registers/cycles.yaml`, or to the record set
itself; `detangle graph --check` fails otherwise.

### A body edit proposes edges; it never applies them (Nick, 2026-08-04, reaffirming D10 element 4)

The lint extracts candidate `depends_on` edges from the changed definition
block, diffs them against the record's canonical list, and reports the
difference. It changes nothing. The reason is that identical-looking clauses
have needed opposite rulings — `close-window → mts-associated-markets` was
dropped while `persistence-gate → medium-investigate` was kept — and an edge
sets reading order, answers impact queries, and can relocate real text through a
placement change. Detection is automatic; the disposition is Nick's.

Contrast the promotion rule (§12), which *is* applied automatically after
informing the human, because a placement flip is mechanical and an edge is a
claim.

## 4. Placement is computed, not judged (C9/C10)

Five documents, one definition site. Reading order is `glossary.md` → UCE →
SBSP → MCL; `index.md` sits outside it.

**Limb 1** — a term used in ≥ 2 of the three component blueprints goes in the
glossary; used in exactly 1, it is defined in that document. Never both.

**Limb 2** (Nick's Case 3 ruling, 2026-08-03) — unless a glossary definition
depends on it, in which case it joins the glossary too. Limb 2 is the
dependency closure of limb 1 over `depends_on`, taken to a fixpoint, and it is
seeded from `used_in` alone: reading the `placement` field it computes would let
one wrongly-placed record drag its dependency tree in behind it. Applied
2026-08-03; it settled in one hop.

**Why limb 2 exists, because it looks surprising in a record.** Preparing
`glossary.md` surfaced 34 edges failing criterion 1's own formal check — glossary
entries leaning on a term defined later, in a document body, with the glossary
read first. Limb 1 counts uses across the three component blueprints; the
glossary is a fourth place terms get used, which nothing counted. So
`used_in: [U]` with `placement: glossary` is correct, not a bug.

**Never hand-set `placement`** — run `detangle validate`, which computes both
limbs and names the expected value.

**No override register exists, and none is needed** (Nick, 2026-07-30). The
first `validate` run surfaced four records whose `placement` contradicted their
`used_in` (`rd01`, `rt02`, `rt05`, `rt22`), superseding an earlier hand
re-placement; Nick ruled that **the standard C9 rule governs on the corpus we
have** and all four moved. Expect this to be revisited against the full
documents; until then placement is computed with no exceptions.

`samples/blueprint-analytical-layer.md` is a read-only reference and is
**excluded from the placement count** (Nick, 2026-07-22) — an `(A)` flag is
informational only.

### A definition block's text counts as a use (Nick, 2026-08-05)

The same miscount, one level down. An in-document section count that looks at
prose sections only misses that a definition block renders in "Terms defined in
this document" and is itself a use. `participant-interaction` sat in §4 of the
`U` golden for exactly that reason, producing two forward references; counting
its use inside `persistence-gate`'s definition block put it in the section read
first and cleared both. No exception is recorded, because the existing rule —
define it in the section read first — already covers it.

The blast radius beyond `U` is unmeasured: `restructure --report`'s
forward-reference cluster is what detects the rest, so `S` and `M` get
measured, not assumed.

## 5. Two input sets (Nick, 2026-08-05)

The **detangle set** (`components` in `detangle.toml [documents]`) is what gets
restructured, and it is the only set that counts for placement, orphan
measurement, omission checking and the verbatim-token diff.

The **reference set** (`references` — plus future side documents business users
write) is read-only: never modified, never restructured, never stamped, never
counted — but citable for provenance, and **a definition found only in a
reference document is lifted as the definition**, with a real span into the
reference file. The term keeps its `orphan` flag after the lift: the flag
measures the detangle set. `mts-spa` (defined entirely from A, `flags:
[orphan, A]`) is the live example.

Adding a reference document is a config edit, never a code change. See
research-memo §Two input sets; the older per-document A/P rulings are instances
of this rule.

## 6. Two canonical trees — `concepts/` and `registers/` (Nick, 2026-07-30)

`concepts/` holds **only** corpus-derived business terms: one YAML record per
concept, every one obeying the same schema and the same provenance contract
(`source` span, `para_hash`, `verified_against`, definitions assembled from
corpus wording per C2). That uniformity is enforceable — every `*.yaml` file
under `concepts/` is a record, with no exclusions — and a carve-out inside it
would rot the first time a non-record file landed there.

`registers/` holds canonical data that is **not** a corpus term: human rulings
whose provenance is a PR thread and a standards clause, not a source span.

Do not put a register under `concepts/`: records are loaded as
`concepts/*.yaml`, and a register file there is indistinguishable from a
malformed record — `concepts/removal-register.yaml` is a genuine concept record
for the corpus term "Removal Register", which is exactly the collision to avoid.

Registers are canonical **inputs** to generation, never generated.

### `registers/cycles.yaml`

Cycle dispositions and entry points (criterion 1). Entries are 1:1 with live
cycles in the graph; a cycle resolved by narrowing gets no entry. Each entry
carries the criterion-1 `entry_point`: the member defined first, whose
cross-reference becomes the marked forward reference. For the one accepted pair
that is `liquidity-driven-reaction` (Nick, 2026-07-30) — default before
exception, so the identical-observable-pattern clause is never the deferred one.

### `registers/reference-terms.md`

The criterion-3 list of regulator- and industry-owned terms, deliberately
*excluded* from the record set. Moved out of `concepts/` under the rule above.

### `registers/waivers.yaml`

Findings with a human disposition but no fix yet (step 3.9, built 2026-08-03).
An entry matches on `check` + `where`, narrowed by an optional `match`
substring of the message; a covered finding is **printed and counted but
excluded from the exit-code decision**, so a command can be green while a fix
waits elsewhere.

**Every command reads the register** (Nick, 2026-08-05, ruled when there were
three commands; `restructure` and `verify` read it too) — before that only
`validate` did, so a finding raised by `generate` or `graph` could not be
deferred at all.

Entries and live findings are 1:1 like `cycles.yaml`: a stale entry raises
`waiver-stale` (warn), so a fix deletes its waiver in the same PR. But
**staleness is judged only by the command that ran the check**, because a
command that never ran one cannot prove its waiver dead, and the false alarm
would block a required gate. Each module declares the checks it raises in a
`CHECKS` constant, kept honest by `tests/test_checks_declared.py`.

Not waivable: `register-parse`, `split-parse`/`split-schema` and the `waiver-*`
checks — a malformed register must not excuse itself — and the **drift** checks,
one pair per derived artifact, because a waiver defers work and regenerating a
derived file is one command, so there is nothing to defer. C6 and ADR-001 D5
hold only while a hand-edited artifact cannot excuse itself. The authoritative
list is `registers.NOT_WAIVABLE` — read it there rather than from memory, since
every new derived artifact extends it.

Waiving is a separate channel, not a third severity: everything left live still
blocks. Do **not** file an accepted cycle here (ADR-001 D6) — that is an
approval and permanent, and a waiver is a deferral.

`review_by` is **recorded but not enforced**: an expiry check would make CI's
verdict turn on wall-clock time. There is deliberately no sibling
`registers/source-corrections.yaml` — the `disposition` field carries
`source-defect` and a separate register would have duplicated the loader, the
staleness pass and the partition machinery to hold one value (backlog B-1
point 4).

The register's first entries are the three `definition-token` findings on
`explanation-type`, `otc-bilateral-trading` and `persistence-gate`, ruled
**source-document defects** (Nick, 2026-07-31): `persistence-gate`'s
`MEDIUM-INVESTIGATE` meets the OCR-split `MEDIUM- INVESTIGATE` in UCE, while
`otc-bilateral-trading`'s `EOD-only` and `explanation-type`'s `BOA-archetype`
want a hyphen the source ("EOD only" in MCL, "BOA archetype" in SBSP) does not
carry. They are fixed later by a human through the B-1
source-correction path and held as accepted debt until then. **Records are not
edited and the validator is not loosened** — either remedy would absorb a source
defect downstream.

### `registers/claim-splits.yaml`

Approved claim boundaries (ADR-003 D1; home ruled by Nick 2026-08-07). Where the
decomposer will not guess how to split a damaged span it **flags** it, and the
split a human approved lands here for `detangle verify` to execute — the
reorder-plan pattern one level down, which is how the harness applies judgment
without calling a model.

One file for the whole set: claim ids carry their document (`U:hash8:occ:n`), so
the per-document view is a filter. Entries and live flags stay 1:1
(`split-stale`, warn), scoped to the documents a run decomposed.

Overrides apply to the **source only**: rebasing an entry onto the restructured
output is inert — few `U` blocks keep their `para_hash` through the restructure
— so how a split propagates to the output is unruled (backlog B-10) and the
parts land in the coverage residue meanwhile.

## 7. Three channels: findings, waivers, notices

Findings **block**. Waivers **defer** a real problem. Notices are neither — they
carry what is worth knowing but is not a defect (`state/notices.md`, ruled
2026-08-04, **generator not built**, backlog B-7).

A notice raised as a finding would make "nothing is broken" a red build, which
is the trap that already caught the glossary overview gap and `code_quality`.
`state/notices.md` is committed, so new entries appear in the PR diff, and
**unguarded**, because a stale notices file must never block a PR. It carries a
"generated from commit X at time Y" header — visible age instead of enforcement,
which `concept-graph.yaml` cannot have without breaking byte comparison.

The same trap governs which gates go into `ci.yml`: an unsatisfiable gate blocks
every PR (it stuck PR #81 once), and a permanently red job trains reviewers to
ignore CI.

### Repository, CI and branch protection

The repo is public **only** so branch protection could be used (2026-08-04).
One ruleset, `protect-main`, covers `deletion`, `non_fast_forward`,
`pull_request`, `required_status_checks` (the CI contexts, strict) and
`code_scanning`; earlier overlapping rulesets were deleted.

CodeQL default setup is on for `python` and `actions`. **`.claude/` is untracked
and gitignored** because a single stray `.js` file there made CodeQL detect a
JavaScript language it could not analyse.

`code_quality` is deliberately **not** in the ruleset until that feature is
actually enabled — see the unsatisfiable-gate trap above.

## 8. Two operating modes (D10)

The one-shot detangle run (Phases 5–9) and the steady-state drift lint that
guards every later docs PR (Phase 10).

Section identity is two-layer: tool-stamped `<!-- sec:… -->` markers for
identity, content hashes in a generated section map for change detection.
**Line numbers are provenance nowhere**, and authors — human or AI — are never
asked to mint a section ID.

## 9. The reorder plan and the verification harness

**The reorder plan is data** (ADR-002, approved 2026-08-05):
`eval/golden/uce.plan.yaml` is the plan and `detangle restructure` executes it
deterministically, authoring nothing. The machine run of the real plan
reproduces the approved golden — identical section markers, all definition
blocks byte-equal, empty token diff both ways — and that is held as a test.

**The evaluation set** (`eval/`) is what both the prototype and the harness are
measured against:

- `eval/README.md` designates the three shortened blueprints as the test inputs,
  each **pinned to the git blob** it carried at a named commit. The reference
  documents and the CSV fixtures are excluded from the inputs — but the
  reference set still has to be *available*, because the fabrication check needs
  it and lifted definitions trace outside the test inputs by design (§5).
- `eval/golden/uce.md` plus its glossary and index slices and the four 8f
  artifacts — the hand-approved golden for `U`, with stamped `sec:`/`concept:`
  markers and record-verbatim definition blocks.
- `eval/golden/uce.plan.yaml` — the reorder plan that reproduces it.
- `eval/review-load.md` — the 5.3 measurement that set `param-max-comments-per-
  PR` and the provisional `param-low-confidence-threshold`.
- `eval/prototype-comparison.md` — the 6.2 comparison against the golden.

**Pinned now, re-baselined later** (Nick's ruling): the backlog B-1 source
correction rewrites all three blobs and voids the golden; the re-baseline
updates the blob column in the **same PR** as the correction. Nothing from a
prototype run is committed — the plan and the blobs are pinned, so one command
reproduces every figure.

Two approved deviations recorded in the golden's `exceptions.md`: it carries no
generated navigation (first-use links wait for their generator), and the orphan
roster lives in the exceptions list rather than as waiver entries, because an
unmatched waiver would trip `waiver-stale`.

**The 8f report split (Nick, 2026-08-05).** The report generator writes only
what the run measured: block moves, drops, category tallies, the criterion-5
accounting, the undefined-term roster, forward references. A ruling is a human's
sentence and the tool never writes one — the plan carries an `exceptions:` list
of one line per ruling (`title` + `where`), and the report names it and points
at where the reasoning is written rather than reprinting it, so the wording
lives in one place. The declarations exist because the 8c budget counts PR
comments and a comment the tool cannot see is one it would count wrong; over
`param-max-comments-per-PR` the run reports and writes no document.

**The harness** (ADR-003, `plan/adr-003-verification-harness.md`):

- **D1 — the decomposer flags, it never guesses.** Deterministic backbone from
  one *whole-document* pandoc parse, not a per-block one: the corpus is full of
  multiline tables whose rows are blank-line separated, and a per-block parse
  shatters them. Claim ids are hash-anchored — `doc:hash8:occ:n`, never line
  numbers. Judgment lands as data in `registers/claim-splits.yaml`; the LLM pass
  is a workflow that produces a PR, not a runtime dependency.
- **D2 — match first, score the residue.** Stage 1 is exact normalised-text
  identity at confidence 1.0, and it is a **correctness property, not an
  optimisation**: §1.1 of the memo records that grounded-factuality metrics
  degrade on heavily reordered text, which is what a restructure produces, so
  the fewer claims reach a model the less of the guarantee rests on its weakest
  regime. Measured, then declined: case-folding gained nothing and
  run-concatenation gained little — both held as live probes in tests rather
  than as claims in a comment.
- **D3 — deferred, not declined** (Nick, 2026-08-07): the model stages need
  PyTorch and `transformers`, outside the approved tooling, so they wait behind
  `--use-inference` (backlog B-9).
- **D4 — a use is scoped to the whole reading order**, glossary → U → S → M, not
  per document: C9 should make a cross-document forward reference impossible, so
  an empty result is the *proof* it held. One exemption: the accepted cycle's
  bridging reference.
- **D5 — `detangle verify` runs deterministically** (Nick, 2026-08-07). It
  cannot say whether the output contains invented text, and a clean exit that
  skipped the fabrication check would read as a proof it never produced — the
  same trap as reading exit `2` as "no findings". Three mitigations: the
  report's stage table prints the stages that did **not** run, the summary
  carries `fabrication: NOT CHECKED`, and `coverage-unscored` (warn, one per
  document, per rubric §8d) names how many claims the run declined to rule on.
- **Step 7.5 — a blob is the version.** The report records the git blob of every
  document the run read plus the commit, and **no timestamp**: the commit and
  the blobs date it, and a clock would make it irreproducible. `manifest.yaml`
  (10.4) absorbs this later.

**ADR-004 (ruled in full, Nick 2026-08-07)** resets the operating model: the
detangle run is a **repeatable campaign**, not a one-off, and **assurance** —
who wrote a claim, who approved it — rather than corpus anchoring is what
carries definitional strength. Text a human writes in v1.2 is as strong as text
a human wrote in v1.0, which matters here because `samples/` was itself
AI-drafted and not closely reviewed. Two consequences already in code and
config: approved additions are **not** marked (D3 — git already records the
history, so an in-document marker duplicates it; unreviewed AI text stays
marked), and `param-full-verify-cadence` is **every re-run, with release tags an
additional trigger**. It moved *off* "every release tag" as the sole trigger
because a tag is the thing Nick expects to forget, while a re-run is deliberate
and is exactly the moment the proof is wanted — but tags were kept alongside, so
nothing that ran before now runs less often. (`definition-of-done.md` parameter
table and plan step 10.6 are authoritative on this.)

## 10. Record-authoring conventions (learned in practice, steps 3.3–3.4)

Established across PRs #17–#35; follow them so records stay uniform.

- **Span anchoring.** Split the source into blank-line blocks; `para_hash` =
  sha256 over the block's pandoc plain rendering (`pandoc -f markdown -t plain
  --wrap=none`, whitespace collapsed to single spaces, trimmed). `section` =
  nearest preceding numbered heading, else "Front matter".
  `verified_against.git_blob` = `git rev-parse HEAD:samples/<file>`. Grid-table
  rows may be OCR-split across blocks — anchor the block carrying the operative
  sentence; a whole-table block shares one hash across every record citing it.
- **Definitions are assembled, never invented (C2).** Only corpus wording,
  lightly stitched; pandoc-normalized punctuation (en-dashes, ≥, σ) is the house
  form. A term used but never defined gets `definition: null` + `flags:
  [orphan]` — do not promote extraction glosses or (P)-only expansions into
  definitions. **Narrowed, not repealed, 2026-08-05:** an expansion or gloss is
  still not a definition, but a genuine definition in a reference document is
  lifted with its provenance span, and the `orphan` flag survives the lift.
- **"Lightly stitched" means ordinary English is free** (Nick, 2026-07-30).
  Connective and descriptive words — *abuse*, *pattern*, *identified*,
  *catalogued* — are standard English, not project terms; they need no corpus
  provenance, no definition, and mint no `depends_on` edge. C2 constrains the
  domain wording: terms, codes, thresholds, modality. A validation check that
  tests every word against the anchored block is measuring the wrong thing —
  restrict it to domain-shaped tokens (codes, snake_case and CamelCase
  identifiers, and surfaces that have records).
- **Verify wording against the source, not the extraction.** The extraction
  paraphrases ("cleared" became "passed" once — a criterion-5 defect that
  reached main). Validation for every batch: YAML parse + required keys, blob
  match, every `para_hash` present in the recomputed block-hash set, a long
  verbatim run of each definition inside its anchored block, conflict quotes
  verbatim substrings, `[[links]]` resolve, edge targets exist.
- **One definition site per term (C9).** If a value token gets promoted to its
  own record, remove it from the other record's aliases in the same PR
  (MWBR_ANOMALOUS precedent). A measure and the archetype that uses it stay
  separate records without shared aliases (QML / SB-13 precedent).
- **Placement is computed, and ownership beats count.** Regulator- and
  industry-owned terms go to `registers/reference-terms.md` rows, never records,
  even when used in ≥ 2 docs (criterion 3; MAR Article 12/16, ADA, quote
  stuffing, Eurex, OLO, HHI). (P)-only terms are held as candidate rows until a
  U/S/M usage appears (ruling on PR #18). Two `(P)` items name no corpus term at
  all and stay candidate-list rows — no record and no `reference-terms.md` row
  (Nick, 2026-07-30); one of them collides with the plan's own C1–C12 constraint
  IDs rather than with anything in `samples/`.
- **External vendors are reference rows** (2026-07-30, Eurex precedent).
  OpenSanctions, OpenCorporates, Azure OpenAI / AWS Bedrock, Azure AI Search are
  criterion-3 rows in `registers/reference-terms.md`, not records — even when a
  ruling loosely says "record", ownership beats it; flag the deviation.
- **Business terms, not software components (IBE/IBEB ruling, 2026-07-30).**
  Where a business object and the software that produces it share a definition
  site, only the business term is defined. The software record stays
  (`definition: null`, corpus wording preserved verbatim in `notes`, outgoing
  edges dropped, **no** orphan flag — the orphan count measures source
  convolutedness, and the source does define it). Applied to
  `intraday-behavioural-event-builder`, `dataenrichmentorchestrator`,
  `mediumreviewengine`; cited for `rsaengine`, `mediumreviewgroup`. The
  carve-out needs the source to define the concept under its business name:
  `close-window-start-minutes` keeps `flags: [orphan]` because `close-window` is
  itself an orphan.
- **Code families get records per code.** SB-xx archetype rows and MTSAM-Lxx
  register entries used in ≥ 2 docs are records in their own right, as values of
  their master term (sb-26 precedent).
- **Distinct records per sense for overloaded words** (Nick, 2026-07-30, on
  "Tier", "Level", "Layer", "IS"). Qualified surfaces with one definition site
  each, so criterion 1's disambiguation requirement is met by the record set
  rather than by a note in the generated glossary. No head record is minted for
  a bare overloaded word: nothing in the corpus defines one, so it would violate
  C2. C9-hygiene notes on the qualified records refuse to alias the bare
  surface.
- **Cycle policy (applied 2026-07-29, ISO 704 §6.5.2).** A circular edge whose
  source clause is consequence/elaboration is resolved by narrowing the
  definition proper — the clause moves verbatim to `notes`, and the edge is
  dropped. A genuinely contrastive pair is kept as a documented outer circle
  (liquidity-driven-reaction ↔ identity-driven-coordination is the only accepted
  cycle); the view generator condenses that SCC for the topological sort.
  Accepted cycles go in `registers/cycles.yaml`. Direction rulings worth
  remembering: classification precedes gate (a status recommended by a tool
  precedes the decision moment about it), and RT01 precedes SB-01 (a raw-data
  alert precedes the calculated fraud-detection item that shares its name).
- **`notes` is a staging post, not a destination** (Nick, 2026-08-04). Records
  are not part of the output set, so a corpus clause left there is an omission
  under criterion 4. It lands in document prose beside its definition block when
  the body is written.
- **Edges** ("definition of X uses term Y") are extracted from definition text
  only, live only on defined records, and are added in dedicated passes; targets
  that don't exist yet are logged in the PR body and added when they land.
- **Edge matching discipline (closing pass, PRs #54–#58).** Case-sensitive token
  match for codes, case-insensitive with plural for phrases, token-boundary
  rules (MTSAM ≠ MTSAM-L01), plus occurrence-level **containment suppression**:
  a match whose every occurrence sits inside a longer matched span or the
  record's own term/aliases is not an independent use and mints no edge;
  code-path composition (`IBE.metadata['event_context']`) is exempt.
  Sense-collision edges are kept as textual truth and listed in the PR body —
  Nick ruled keep-all on the closing-pass list (2026-07-30). New cycles are
  surfaced for disposition, never repaired unilaterally.
- **Edge-minting is not a blanket rule once clauses move out of the
  definition.** `close-window → mts-associated-markets` should go: you do not
  need the venue to understand what a close window is, and keeping it would
  order the glossary and answer impact queries wrongly. `persistence-gate →
  medium-investigate` must stay, though it sits in a structurally identical
  trailing clause, because the cap *is* the gate's point. An instantiation
  creates no comprehension prerequisite; a consequence naming a defined term
  usually does.
- **PR mechanics.** ≤ `param-max-terms-changed-per-PR` files, counting new
  records, edited records, and edge changes together. Note the count in every PR
  body. When wrapping notes programmatically, keep `[[...]]` tokens atomic
  (`break_on_hyphens=False`) — split links reached main once.

## 11. Working with the corpus

`samples/` blueprints are pandoc-converted grid tables with very long physical
lines, OCR damage in places, and live contradictions (MCL is titled v21 but
contains a "what is new in v22" block; MCL applies to UCE v28 while SBSP cites
v30). **These contradictions are data, not bugs** — surface them, never
harmonise them (criterion 6, non-goals).

When reproducing source text anywhere, criterion 5 is absolute: numbers,
thresholds, comparison operators, modality (`must` vs `should`), scoping
qualifiers, internal codes and their casing, citations, classification markings,
and British spelling are reproduced verbatim. This is checked mechanically and
independently of claim mapping, because a claim can map correctly and still have
lost its force.

Regulator-owned terms (MAR, ESMA, FSMA, CONSOB, …) go to
`registers/reference-terms.md`, not the glossary.

**`samples/` is scaffolding**, not a permanent fixture. It is replaced by the
full documents once the tool exists, and those documents are the living set
humans edit. "Input, never output" was a property of a fixed test fixture, not a
standing principle. It follows that **`corpus` provenance is a historical fact,
not a status anything can migrate into** — it says the wording traces to what
the business had written when the run consumed it, and `verified_against.
git_blob` keeps that verifiable however the file is later rewritten. Authored
content never becomes corpus content.

**`samples/` cannot be untracked, and removing it would not do what it looks
like it does** (investigated 2026-08-04; a proposal to gitignore and purge it
was raised and withdrawn). First, `detangle validate` reads the corpus from HEAD
and from disk — `git rev-parse HEAD:<doc>` in `records/checks.py`, then the file
itself in `records/spans.py`, which raises `UsageError` (**exit 2**) when it is
missing. It is a required check on `protect-main`, so untracking `samples/`
blocks every PR: the unsatisfiable-gate trap again. Second, if the aim were
keeping corpus wording out of a public repo, deleting `samples/` does not
achieve it — `concepts/` holds ~186k characters of verbatim corpus wording in
`notes` plus ~33k in `definition`, and `glossary.md` another ~56k, against ~369k
for the three blueprints. A purge would have to take `concepts/`, `glossary.md`
and `work/term-extraction/` with it, which is the whole project. Making the repo
private is the coherent version of that wish; the repo is public **only** so
branch protection could be used.

### Working artifacts

- `work/term-extraction/blueprint-*.terms.yaml` — raw per-document extraction,
  LLM-assisted, headers state it is **not yet human-reviewed**. Its line numbers
  are approximate and explicitly not citable as provenance; its quotes
  paraphrase — **always re-verify wording against `samples/`**.
- `work/term-extraction/candidate-terms-merged.md` — the reviewed merge,
  carrying a "Human review decision" column per term. That column is Nick's; do
  not fill it in.

## 12. Design rulings that outlive their session

Beyond those already stated above.

- **Promotion is automatic, after informing the human.** When an edit makes a
  term cross from one document into two, the message is: *"Your latest edit
  leads to `<concept>` being used in more than one source document. The
  definition will be moved to the glossary and all documents that use it,
  including this one, will receive links to it."* Then the tool reconfigures.
  Promotion is required — two documents means the glossary, or C9 breaks.
- **Demotion is not automatic.** The rubric says a single-document term *may*
  move, so the tool reports and waits, and the message says plainly that nothing
  is wrong. Demotion also moves prose across files and rewrites first-use links,
  and usage counts wobble, so an automatic rule would shunt definitions back and
  forth.
- **The guard may make word-preserving edits, and must comment.** This narrowed
  a hard prohibition into a rule: edits verified to change no words, with a PR
  comment. The two authorised cases are stamping section IDs and reordering
  glossary entries left out of topological order. It may never change meaning.
- **Provenance is two axes, not one enum.** Anchoring — is there a source span?
  — is separate from authorship and assurance. `corpus`/`human`/`AI` as one
  field cannot express AI-written text sitting inside the corpus, which is
  exactly this project's situation (see the corpus-provenance bullet in plan §3
  Scope). Authored content carries author, approver, PR and the set version it
  entered at.
- **Authored text never acquires a `para_hash`.** A span asserts the business
  wrote the wording, and tool output must never be able to claim that, or the
  next run reads its own output as source. `flags: [orphan]` therefore survives
  an authored definition — otherwise the convolutedness measure decays as fast
  as the work gets done. Change detection for everything is the section map's
  content hash, not `para_hash`; a provenance claim is asserted against that
  hash, and an edit breaking corpus provenance **auto-demotes** down criterion
  7's moved → derived → added ladder with a comment. General rule: **the guard
  may weaken a provenance claim on its own; it may never strengthen one.**
- **AI may draft a definition; a named human approves**, and the draft shows the
  corpus usages it was assembled from, or says there are none.
- **`definition` is not split** into definition / illustration / note. The marked
  block is the definitional boundary: definition proper inside the markers,
  illustration and consequence as ordinary prose outside. The field-splitting
  design was aimed at multi-clause records that cite more than one span, and
  narrowing the checked text to the block removes most of that surface.
  What it was aimed *at* is still real and worth knowing: a definition proper,
  an illustration and a consequence sit in one string, while `source:` is
  **record-level**, so the token check tests the whole string against the
  **union** of every anchored block — a span imported for one clause can launder
  another. On `anonymous-quote-driven-market-structure`, adding a third MCL span
  would have cleared the finding outright without improving the record. ISO 704
  §6.4.4's substitution principle is the test for what is definitional; the
  §6.5.2 narrowing pattern is how the non-definitional clauses come out.
- **Inline redefinition blocks, but shows both texts.** A one-click fix is
  offered *only* where the body text verbatim restates the glossary definition;
  otherwise show and wait, because the difference is either an improvement or a
  contradiction.
- **No `concept-graph.mmd` is committed.** `detangle graph --mmd <id>` is to
  print one concept's neighbourhood on demand: the whole set renders as a large
  tangle plus loose dots, while a single concept is two or three boxes and eight
  one step out. Amends C6 and D2. The half that removes the file is done; the
  half that replaces it is not (backlog B-6).
- **Bridging markers must be generated, never typed.** Same principle as C12's
  section IDs: marking that depends on a human remembering to write
  `<!-- AI addition:start -->` is marking that goes missing exactly where it
  mattered.
- **The `definition-token` check is a proxy for C2, not C2.** C2 is claim-level,
  checked by the Phase 7 harness, and has two limbs: every claim traces to the
  source **or is explicitly marked as bridging text**. The record-layer check is
  deliberately stricter because the harness is incomplete. Criterion 7 already
  covers the orphan case — a glossary entry with no source definition is
  Category C in full and always raises a PR comment.
- **Declared document versions are to be removed**; git is the version control,
  and hand-typed version strings never reflect reality. Two things must survive
  the removal: the existing skew (MCL titled v21 with a v22 block; MCL applying
  to UCE v28 while SBSP cites v30) as a recorded finding rather than being
  harmonised away with the numbers, and release identity landing somewhere for
  audit — git tags bound by `manifest.yaml`.
- **Glossary definitions render as one physical line each, unwrapped.** Wrapping
  reflows a paragraph when one word changes; this file exists to be commented
  on, and a one-line diff points at one record.
- **Ink on the page counts** toward a text's length even when the tool wrote it —
  the visible `[AI addition]` tag included. Written into the rubric beside
  `param-overview-max-words`.
- **Sections are counted as a reader meets them** — headed sections. A headless
  `head` block still appears in the move-map's Section IDs table, so nothing is
  hidden.
- **Two measurements can be right and still not comparable, so name them
  precisely.** The golden's document-length figure counts `characters`; the
  generated report counts bytes. Relabelling was the fix — the measurement was
  right and its name was wrong — and the two are deliberately not compared.
  Same shape one level up: the harness counts more claims on the pinned source
  blob than the 5.3 hand count found, because the hand count worked from the
  golden, where page-split table rows are rejoined and repeated headers
  deduplicated. Neither is an error; they measure different texts.
- **Division of labour (Nick, 2026-07-30):** the assistant builds the whole
  toolchain — validator, graph, and the D9 view-generator — as well as
  delivering ontology content (records, edges). This supersedes the earlier
  split in which Nick built the view-generator himself.

### Editing surfaces — why the tool UI is load-bearing

Direct markdown editing stays the norm (C12); the corpus is overwhelmingly
non-definitional. The tool is required for one class only: definitions of
glossary-placed terms.

A PR diff is not a viable surface for non-IT-literate business users: it shows
hunks with ~3 lines of context in raw markdown with `+`/`-` gutters, commenting
requires the source view rather than the rendered one, and a topologically
ordered generated file turns a one-word fix into large reorder churn. **So the
tool UI is load-bearing, not a convenience**, and nothing in Phase 8 or 9 scopes
it yet. The reading-time route only has to serve the team, not external readers
(Nick, 2026-07-31).

Related: **the comment → edit round-trip only exists inside a PR.** D9's
source-map anchors resolve a comment on generated markdown back to its record,
but that requires an open PR with the file in the diff. Someone reading the
published glossary who spots a wrong definition has no comment surface at all —
which is the common case, and why the UI matters.

## 13. Open design questions

Not backlog items (those are `plan/backlog.md`, B-n) — these are unruled design
questions with no phase.

1. **The glossary drift lint.** `generate --check` cannot be a CI gate:
   byte-comparing a file humans edit is incoherent. It becomes a drift lint that
   mirrors human edits back into the records, and the fourth gate stays out of
   `ci.yml` until that lint exists. Until then `glossary.md` is unguarded (§2).
2. **Guarding the committed views generally** — regenerate-and-compare, banner,
   CI redirect message naming the record to edit.
3. **Provenance schema shape** — field names, and whether authored text sits in
   `definition:` or its own field.
4. **The `M` source span on `anonymous-quote-driven-market-structure`** — keep
   it because `notes` quotes that row, or drop it with the narrowed definition.
5. **`close-window`'s general sense** is genuinely absent from the corpus
   (searched: "assessment window", "preceding the close", "end-of-day
   assessment" appear nowhere). Nick supplies it post-deployment, into the
   documents, not as an authored record field.
