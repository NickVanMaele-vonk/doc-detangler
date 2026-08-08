# ADR-003 — Verification harness design (Phase 7)

**Status: partly ruled** — Decisions 1 (2026-08-06; its register's home ruled
2026-08-07, `registers/claim-splits.yaml`), 2, 4 and 5 (all 2026-08-07) are
ruled by Nick and built. **Decision 3 is deferred**, not
declined (Nick, 2026-08-07): the model path waits behind `--use-inference`,
parked as backlog B-9, and the dependency is not installed until that flag is
wanted. Decisions 6 and 7 are still proposals.

**Two things the build left open for Nick.** The single live `forward-use`
finding is a **sense collision, not a structural defect** — `gate` is a record
whose bare surface is the English word, and the hit is in `glossary.md`'s own
generated banner. It is deliberately not suppressed: the disposition is a
ruling (the 2026-07-30 word-overload ruling says a bare overloaded word gets
no head record; a waiver is the alternative). And how an approved claim split
reaches the restructured output is unruled — backlog B-10. The working agreement says Nick approves before
any code is written. Decisions carry a recommendation each, and any one can be
ruled differently without reopening the others.

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

**Where the register lives — ruled by Nick, 2026-08-07:
`registers/claim-splits.yaml`.** One file for the whole set. It is canonical
data whose provenance is a PR thread rather than a corpus span, which is
exactly the rule that governs `registers/`, and claim ids already carry their
document (`U:hash8:occ:n`), so a per-document view is a filter rather than a
fact the file layout has to supply. The alternatives considered were one
register per document (keeps a document's rulings together, but `registers/`
has a clean one-file-per-concern shape) and a file beside the reorder plan in
`eval/golden/` (groups the two human-approved data artifacts, but puts
canonical data under the evaluation set, and the splits outlive the golden).
`detangle verify` reads it on every run; `split-parse` and `split-schema` join
`register-parse` in `registers.NOT_WAIVABLE`, since a malformed register must
not excuse itself, and a target that matches nothing raises `split-stale`
(warn), scoped to the documents the run decomposed.

**Open, discovered while wiring it: how a split reaches the output.** Coverage
compares a source decomposition against an output one, so a source claim split
into two only matches if the output claim is split the same way. Propagating
an entry by rebasing its id onto the output does not work — measured on the
`U` golden, **4 of 84 source blocks keep their `para_hash` through the
restructure**, because a block re-emitted with `sec:`/`concept:` markers hashes
differently — so 95% of entries would be silently inert, failing as residue
rather than as a missed override. The rule that would work anchors on the
claim's **text**, which is what a split is a ruling about; that is a design
decision, so overrides apply to the source only until it is ruled and the parts
of a split claim land in the residue, where they would have landed unsplit.

## Decision 2 — coverage: match first, score the residue — **RULED**

**Ruled by Nick, 2026-08-07.** Stage 1 is built (build step 2); stage 2 waits
on Decision 3's dependency approval.

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

**Why stage 1 is a correctness property, not an optimisation.** A claim whose
wording provably did not change must not be able to fail. §1.1 records that
grounded-factuality metrics degrade on heavily reordered text, and the
restructure reorders by construction — so the fewer claims reach the model,
the less of the guarantee rests on its weakest regime.

**As built (build step 2, `src/detangle/verify/coverage.py`).** Stage 1
matches one source claim to one output claim on exact equality of the
decomposer's normalised text, and nothing looser. Its matches carry confidence
1.0 and no human reviews them, so the rule has to be incapable of being wrong;
a claim left in the residue costs one model call, a claim placed wrongly costs
the guarantee. Repeated text matches as a multiset — two identical source
claims need two identical output claims, and the second is a merge survivor
for stage 2, not a second hit on one location. Order is ignored; the choice
among identical output claims is the first still free in output order, so a
re-run reproduces the mapping. The module raises **no findings**: a residue
claim is not an omission, it is a claim stage 1 declined to rule on, so
`omission` belongs to the module that scores it.

**Two looser rules were measured and declined**, both held as live probes in
`tests/test_verify_coverage.py` so the numbers stay checkable. Case-folding
gains nothing at all on the golden, so strictness is free and a criterion-5
casing defect stays visible. Run-concatenation — one source claim equal to a
run of consecutive output claims, and the reverse — is deterministic too, so
the argument against it is yield: 9 claims out of 66.

**The measured rate is 204 of 270 source claims, 75.6%**, against the golden
and the pinned `U` blob. That is below the 268-of-289 quoted above for the
same reason PR #116 recorded for the decomposer's own 270-vs-289: the 5.3
figures were counted by hand from the golden, where the 7 OCR page-split rows
are already rejoined and their repeated header fragments deduplicated, while
the machine sees the raw shards. The 66 residue claims are those fragments
plus the version-history table, which the golden renders as prose — one grid
cell becoming several sentences. Both are criterion-4 relocations, which is
exactly what stage 2 exists to rule on. The claim-split register closes part
of the gap as entries land by PR.

## Decision 3 — fabrication: MiniCheck per D4, as an optional extra — **DEFERRED**

**Nick, 2026-08-07:** run deterministically by default for now; add a
`--use-inference` flag to the backlog which invokes a model; the installation
of PyTorch and `transformers` is postponed to the moment that flag is
activated. So this decision is neither approved nor refused — it comes back
when B-9 is picked up, and nothing below is built.

What that costs while it waits is recorded in B-9 and stated in every
verification report: C2's first limb is not machine-checked at all, and on the
`U` golden 66 of 270 source claims come back unresolved rather than placed.
Phase 7's done-when cannot be met on the invented-claim limb until it lands.


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

## Decision 4 — structure: concept-before-use from the graph — **RULED**

**Ruled by Nick, 2026-08-07**, together with the scope question below. Built
as `src/detangle/verify/structure.py`.

7.4 is deterministic and mostly built: topological order from
`concept-graph.yaml` (networkx), checked against each document's actual
definition and first-use order, with a definition block's own text counting
as a use (the 2026-08-05 ruling) and the accepted cycle's entry point
honoured from `registers/cycles.yaml`. New code is the document-side
reader, not the graph side.

**What counts as a use — the question that needed ruling.** The definition
side was settled; the document side was not, and the golden's second defect
(2026-08-05) was exactly a miscount of it. Three candidates:

- **A — every occurrence anywhere.** Maximum recall, but headings and
  navigation count, so the check reports forward references that are
  artifacts of furniture. Noise that trains a reviewer to ignore it.
- **B — the edge-matching discipline, over the blocks the decomposer walks.**
  The rules the closing pass proved on 402 edges (PRs #54–#58): case-sensitive
  for codes, case-insensitive with plurals for phrases, token boundaries so
  `MTSAM` never matches inside `MTSAM-L01`, occurrence-level containment
  suppression. Headings, grid rules and marker-only blocks drop out.
- **C — only inside decomposed claims.** Tidier — one notion of "text that
  says something" for the whole harness — but blind: the decomposer yields no
  claim from a fragment with no terminal punctuation, so a cell reading
  `Gate: CQT` is a use the reader meets and the check never sees.

**Ruled: B.** It gets C's furniture exclusion without C's blind spot, and it
reuses a discipline that has already survived contact with this corpus.

**Scope is the whole reading order** (glossary → UCE → SBSP → MCL), not each
document alone. C9 should make a cross-document forward reference structurally
impossible, so the result ought to be empty — and an empty result is the proof
that C9 held rather than an assumption that it did.

**A definition block's own text counts as a use** is not a special case in the
implementation: a definition block is prose, so it is scanned like any other.
A section heading is not, which is what the 2026-08-05 miscount got wrong.

**As built and measured.** Over the two output documents that exist —
`glossary.md` and the `U` golden — 113 definition sites (78 glossary, 35 in
the golden), **one** forward reference and **one** exemption. The exemption is
the accepted cycle's bridging reference, recognised from `registers/cycles.yaml`
and not raised: criterion 1 clause 2 working. Everything else is clean, which
is the C9 evidence.

The one finding is a **sense collision, not a structural defect**: the
glossary's generated banner says `detangle generate --check` was withdrawn "as
a CI gate", and `gate` is a record whose bare surface is the English word.
`param-false-positive-tolerance` is "none", so it needs a disposition — the
2026-07-30 word-overload ruling says a bare overloaded word gets no head
record, which would remove the surface; a waiver is the alternative. Pinned in
`tests/test_verify_structure.py` so the number cannot drift while it waits.

`forward-use` is an **error**, and waivable. Unlike a proposed `depends_on`
edge there is no judgment in the detection — the reader either has the
definition by then or does not — but a forward reference someone decides to
live with can be deferred with its reasoning written down.

## Decision 5 — one new command: `detangle verify`, not a per-PR gate — **RULED**

**Ruled by Nick, 2026-08-07**, in the form of the timing question the built
stages forced: ship it now, deterministic by default. Built.

The open question was not whether `verify` is a gate — that was settled with
ADR-004 Decision 7 — but whether the command waits for the model. Three
candidates: wait and build once; ship deterministic-only with the absence
reported; ship behind a flag that makes the limitation opt-in. The third is
worst, because it puts the honest label on the user's command line instead of
in the artifact, and a report read next month carries no trace of what it
skipped.

**As built.** `detangle verify --output CODE=PATH [--report PATH]` runs 7.1,
7.2 stage 1 and 7.4 over the reading order, and states the absence of the rest
three ways: the report's stage table prints every stage including the two that
did not run, the summary carries `fabrication: NOT CHECKED`, and
`coverage-unscored` names per document how many claims the run declined to
rule on. The last is a **warn** and waivable — nothing is wrong with the
document, work is outstanding — and is one finding per document, not one per
claim (rubric §8d). Without it a deterministic run over a clean document would
exit `0`, which reads as a proof the command did not produce.

The report carries the step 7.5 version record and **no timestamp**: the commit
and the blobs date the run, and a clock would make it irreproducible. The
claim-split register is **not** wired in, because its home is still unruled —
so the decomposer runs with no overrides, which is the state the 270-claim
figure was measured in.


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
   keep. **The register's home is ruled** (2026-08-07):
   `registers/claim-splits.yaml`, seeded empty, read by `detangle verify` and
   recorded in its report by blob.
2. Deterministic match + structure checks (Decisions 2 stage 1, 4) inside
   `detangle verify`; no model dependency yet. **Done as two libraries:** the
   matcher (204/270 on the golden) and the concept-before-use scan (1 finding,
   1 exemption over `glossary.md` + the `U` golden). Both wait on Decision 5
   for the command that runs them.
3. `detangle verify` itself (Decision 5), **deterministic by default and
   built**: it runs three of the four stages, writes the report with the step
   7.5 version record, and states the absence of the fourth three ways — the
   stage table, `fabrication: NOT CHECKED` in the summary, and the
   `coverage-unscored` warn. The claim-split register is wired in with it.
4. The scored residue (Decisions 2 stage 2, 3) behind `--use-inference`: the
   `[verify]` extra, the pinned checkpoint, coverage + fabrication scoring.
   **Deferred** — backlog B-9, to be picked up with Decision 3.
5. Seeded-error tests (Decision 6), then the `U` dry-run and the
   threshold re-baseline proposal (Decision 7). Note what step 4's deferral
   costs here: the invented-claim limb of Decision 6's done-when cannot be
   met by the deterministic build at all.
