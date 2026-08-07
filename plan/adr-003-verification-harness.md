# ADR-003 — Verification harness design (Phase 7)

**Status: PROPOSED** — nothing below is built; the working agreement says
Nick approves before any code is written. Decisions carry a recommendation
each; approving this document sets them, and any decision can be ruled
differently without reopening the others.

## Context

Phase 7 builds the losslessness harness that constraints C1/C2 and rubric
criterion 4 rest on: claim decomposition (7.1), coverage (7.2), fabrication
(7.3), structure (7.4). The plan marks it DO NOT DEFER, and 6.2 cannot close
without it — `param-low-confidence-threshold` (0.80, provisional) must be
re-baselined against the first artifact carrying a real mapping score, which
is this harness's dry-run (rubric §Parameters; `eval/review-load.md`).

Four prior results shape the design:

- **D4 is signed off** (Nick, 2026-07-21): fabrication checking reuses
  MiniCheck, MIT checkpoint (Flan-T5-Large or DeBERTa-v3-Large) only. It
  scores `(document, claim)` pairs one-directionally — coverage requires
  running it in reverse ourselves, and it does not decompose
  (research-memo §2.9).
- **The decomposer moves the scores** (Wanner et al., §2.8): fix it,
  version it, record it in every report, and treat our numbers as
  internally comparable only.
- **The harness's weakest regime is exactly our regime** (§1.1):
  grounded-factuality metrics are documented to degrade on heavily
  reordered, rewritten text. So the seeded-error test must seed into
  reordered output specifically, or it measures a regime the harness will
  never run in.
- **Phase 5/6 measured the workload**: 289 claims in `U`, of which 268
  moved verbatim; two input sets, with reference-set claims not required in
  the output (criterion 4) but the reference set needed by the fabrication
  check because lifted definitions resolve there (C2, 2026-08-05).

The approved tooling (ADR-001: Python, pytest, ruff, PyYAML, networkx,
pandoc) contains no ML stack; adding one needs approval, which Decision 3
requests.

## Decision 1 — decomposition: deterministic backbone, LLM-assisted overrides as data

Plan step 7.1 says "LLM-assisted". The granularity rule itself is
mechanical — `param-claim-granularity`: one claim per source sentence, one
per table cell carrying an independent assertion — and the 5.2 golden
decomposed the shortened `U` that way (289 claims counted by hand, no
judgment calls recorded). The question is where judgment enters when the
rule meets damaged or overloaded prose. Three candidates:

- **A — LLM decomposer.** What the plan sketched. Adds a nondeterministic
  component to the one place §2.8 says determinism matters most; every
  re-run can produce a different claim list, and every downstream number
  is counted per claim.
- **B — deterministic decomposer only.** Pandoc-based: split blocks the
  way the record-authoring pipeline already does, sentences within prose
  blocks, cells within grid tables; drop headings, navigation and pure
  formatting (non-claims per criterion 4). Sufficient for the shortened
  test inputs (the golden's 289 claims fell out of the rule with no
  judgment calls), but **Nick's assessment (2026-08-06) is that it will
  not survive the full documents** — OCR damage, run-on prose and cells
  carrying several assertions will need judgment.
- **C — deterministic backbone, LLM-assisted overrides as data.** B is
  the default path, and it must *flag* what it cannot confidently split
  (OCR-split rows, broken hyphens, over-long sentences, multi-assertion
  cells). Flagged spans are split by an LLM-assisted pass whose output is
  not consumed directly: it is written into a committed override file
  (span → claim boundaries, one entry per flagged span), reviewed and
  landed by PR like the reorder plan. `detangle verify` reads the
  override file and stays deterministic — same input plus same overrides
  gives the same claim list, so the claim-count tests still hold and the
  LLM runs only when new or changed flagged spans appear, not on every
  run.

**Recommendation: C**, ruled by Nick 2026-08-06: LLM assistance will be
needed on the full documents, so it is designed in now rather than
escalated to later. The ADR-002 pattern applies one level down — the
judgment lives in a human-approved data artifact, the command executes
it and authors nothing. This also keeps the LLM out of the package: the
assisted pass is a workflow that produces a PR, not a runtime dependency
of `detangle verify`, so ADR-001's tooling list is untouched by this
decision (Decision 3's ML stack request stands separately). The
decomposer version *and* the override file's blob are recorded in every
report, and our figures never compare against published FActScore
numbers.

## Decision 2 — coverage: match first, score the residue

Coverage (7.2) maps every detangle-set claim to an output location or flags
an omission. G1's bidirectional traceability frame applies: every source
claim gets an ID; an unlinked source ID is an omission, an unlinked output
claim is a fabrication candidate. Two stages:

1. **Deterministic match.** Normalized-text match (pandoc plain, collapsed
   whitespace — the `para_hash` normalization) locates verbatim moves.
   On the golden that resolves 268 of 289 claims at confidence 1.0, with
   the output location free — no model involved.
2. **Scored residue.** The remainder (derived text: page-split rejoins,
   dedup survivors, relocated definitions) is scored claim-by-claim
   against the output set with the D4 checkpoint run in the coverage
   direction. This produces the per-claim mapping confidence on [0, 1] —
   the distribution that re-baselines `param-low-confidence-threshold`.

Claims scoring below the threshold are findings for human review; merges
and relocations get report entries per criterion 4's pass condition.
Coverage runs over the detangle set only (C1) and is evaluated set-wide,
not per file.

## Decision 3 — fabrication: MiniCheck per D4, as an optional extra

Fabrication (7.3) traces each output claim to either input set or confirms
it is marked bridging text. Mechanics:

- Output claims inside generated bridging markers (`[AI addition]`,
  overview blocks) are exempt from tracing and reported as Category C —
  that is C2's second limb, not a hole in the first.
- Everything else is matched deterministically first (stage 1 above,
  reversed), then scored against the **union of both input sets** —
  lifted definitions resolve into `A`/`P` by design (`mts-spa` precedent).
- Dependency request: an extras group `detangle[verify]` carrying
  `transformers` + `torch`, pinned; the MIT checkpoint pinned by revision
  hash, downloaded and cached, never committed. The core package and the
  existing three CI gates stay exactly as they are.

## Decision 4 — structure: concept-before-use from the graph

7.4 is deterministic and mostly built: topological order from
`concept-graph.yaml` (networkx), checked against each document's actual
definition and first-use order, with a definition block's own text counting
as a use (the 2026-08-05 ruling) and the accepted cycle's entry point
honoured from `registers/cycles.yaml`. New code is the document-side
reader, not the graph side.

## Decision 5 — one new command: `detangle verify`, not a per-PR gate

`detangle verify` runs 7.1→7.4 over the output set and writes the
verification report committed alongside the documents. Same contract as
its three siblings: exit `0`/`1`/`2`, reads the waiver register (Nick,
2026-08-05: every command does), declares its checks in a `CHECKS`
constant — `omission`, `fabrication`, `low-confidence-mapping`,
`forward-use` — all waivable, since each is a finding awaiting human
disposition, not a drift.

It is **not** added to `ci.yml`. Model inference over ~300 claims is
minutes of CPU, and the DoD already says the full losslessness harness
runs at `param-full-verify-cadence`, not per PR. Wiring any part of it
into CI is a separate decision when that parameter is set.

**Update, 2026-08-07 — the parameter is now set** (ADR-004 Decision 7):
"every re-run; release tags additionally". The separate decision it
awaited was taken with it, and the answer was still no CI gate — for
reasons better than cost, since stage-1 matching resolves 268 of 289
claims deterministically and a per-PR run would score single digits.
The three grounds are that step 10.2's per-PR lint already carries the
deterministic half through its `lost-claim` check; that all four checks
above are waivable *because* each awaits a human disposition, so blocking
merge on one converts a review prompt into a hard stop; and that a
required gate depending on `detangle[verify]` would go red on a
checkpoint fetch failure. ADR-004 Decision 7 also adds one output to this
command: the report records the git blob of every document in both input
sets plus the commit (plan step 7.5), which identifies the set a run
verified and gives the next run its baseline.

## Decision 6 — the seeded-error test seeds into reordered output

The done-when requires catching a deleted claim, an invented claim, and a
weakened claim (threshold change + `must`→`should`, per C7). Per §1.1
these are seeded into the **golden output** — which is heavily reordered
relative to source by construction — never into lightly-edited text. Seeds
are scripted mutations of a copy of `eval/golden/uce.md`, held as pytest
tests: the harness must flag all three, and the weakened-claim seed must
be caught even though token-parity (criterion 5) would also catch it —
the harness is measured on its own, not behind the restructure check.

## Decision 7 — scope: `U` dry-run, then the re-baseline closes 6.2

Like ADR-002 Decision 5: the dry-run is `U` only — the golden triple
against the pinned blob — with `S` and `M` left to 9.1. The dry-run's
confidence distribution goes to Nick with a proposed threshold; ruling it
re-baselines `param-low-confidence-threshold` in the rubric and closes
6.2. Nothing from the run is committed except the verification report and
the rubric edit.

## Consequences

Build steps, in order, each its own PR:

1. Decomposer + claim IDs (Decision 1): the deterministic backbone, the
   flagging of spans it cannot confidently split, and the override-file
   loader — with its version string and unit tests over the pinned `U`
   blob (claim count reproduces 289 or the difference is explained in
   the PR). The shortened inputs are expected to need few or no
   overrides; the full documents are where the override path earns its
   keep.
2. Deterministic match + structure checks (Decisions 2 stage 1, 4) inside
   `detangle verify`; no model dependency yet.
3. The scored residue (Decisions 2 stage 2, 3): the `[verify]` extra, the
   pinned checkpoint, coverage + fabrication scoring, the report.
4. Seeded-error tests (Decision 6), then the `U` dry-run and the
   threshold re-baseline proposal (Decision 7).
