# Review-load baseline — step 5.3

Measured from the approved `U` golden (PR #99, approved 2026-08-05) — the
first real data on reviewability. Everything here is measurement or
proposal; the parameter values become set when Nick approves this document.

## Method

Claim counts follow `param-claim-granularity`: one claim per prose
sentence, one claim per table cell carrying an independent assertion. The
source is almost entirely tables, so cells dominate. Counting is
mechanical (sentence-final punctuation for prose; non-furniture cells for
tables, header rows and grid rules excluded). A sensitivity bound counts
sentences *inside* cells instead of cells, since a Key Rules cell can hold
a dozen rules.

## The 5.3 measures

| Measure | Value |
|---|---:|
| Claims in `U` at parameter granularity | **289** (23 prose sentences + 266 assertion-bearing cells) |
| — sensitivity bound (sentences inside cells) | 415 |
| Claims **moved** (Category A, verbatim) | 268 (everything not listed below) |
| Claims **derived** (Category B: the 7 rejoined page-split rows, ~3 cells each) | ~21 |
| Claims **merged** | 0 |
| Claims **relocated to the glossary in this run** | 0 — C9 placement ran in Phase 3; the 73 slice entries pre-date the golden and 36 of them carry definitions assembled from spans, many in `U` |
| Claims **added** (Category C) | 1 (the overview) |
| Claims **omitted** | 0 |
| Terms changed (8b) | 35 of 155 in scope |
| Contradictions surfaced in-document | 2 ("Ten foundational principles" over a twelve-row table; the version-skew cluster) |
| Conflicting definitions carried on in-scope records (`conflict:` blocks) | 13 records |
| Orphans | 84 (47 UCE-placed, 37 glossary-placed) |
| Source-damage items carried verbatim | 1 unreconstructable passage (step 11b), 1 truncated list (VI-A.3.7.3), ~20 damaged tokens |
| **PR comments that would have been raised (8d, per cluster)** | **9** — 7 content clusters (one of them empty: zero drafted definitions) + 2 recorded deviations |
| Low-confidence rewrites | 2 instances — the step 11b garble and the truncated VI-A.3.7.3 list; every other rewrite was a verbatim move or a mechanical rejoin |

Scaling caveat, carried from `eval/README.md`: `U` is smallest by words but
heaviest by term load (82 document-placed records against 63 in `S` and 59
in `M`). Per-term figures scale to `S`/`M`; per-word figures do not.

## Parameter analysis

### `param-max-terms-changed-per-PR` = 200 — **confirmed**

Measured: 35 for the whole-document `U` golden. The largest single unit the
build will ever need is the glossary itself at 155 entries; 200 covers it.
The steady-state figure this cap was originally sized for (25) would have
covered this run too — the raise matters for the glossary and for set-wide
passes, exactly as the 2026-08-05 rationale said.

### `param-max-comments-per-PR` = 25 — **propose: set at 25**

Measured: 9 aggregated clusters for a whole-document restructure, the
largest reviewable unit that fits the term cap. `S` and `M` have the same
bounded cluster *types* and lighter term loads, so 7–9 each is the
expectation. A single PR carrying all three documents plus the glossary
cannot exist — 155 + 204 term changes breaches the term cap first — so the
term cap already forces PRs to roughly per-document scope, and 25 gives a
per-document run 2.5–3× headroom. The rule it buys (8c): a run producing
more than 25 blocking comments does not open a PR; it fails and reports.

### `param-low-confidence-threshold` — **propose: 0.80, provisional, re-baselined at step 6.2**

What the golden can and cannot measure, stated plainly. The golden was
hand-produced, so no machine confidence scores exist — a numeric threshold
cannot be *derived* yet, and pretending otherwise would be a guess wearing
a measurement's clothes. What the golden does measure is the **rate**: 2
low-confidence spots in 289 claims (0.7%), both source damage rather than
mapping ambiguity. The dial's job is therefore to catch damage-grade
uncertainty without flooding the review, and the comment budget has room
for far more than the measured rate (one 8d cluster regardless of instance
count; instance volume is what the dial bounds).

Proposal: set **0.80 on the Phase 7 harness's [0, 1] mapping-confidence
scale** — flagged as provisional in the rubric, with a mandatory
re-baseline at step 6.2, where the prototype produces the first real
confidence distribution against this golden. If 6.2 shows 0.80 flagging
much more than the measured ~0.7% of claims, the threshold moves, not the
rubric text. This satisfies Phase 5's "set from 5.3" with the honest
caveat attached, instead of leaving the parameter open for another phase.

## What this baseline does not measure

- Machine mapping-confidence distribution (needs the Phase 6 prototype).
- False-positive rate of the harness (Phase 7 seeded-error test).
- `S`/`M` review load — predicted by term-load scaling above, measured
  when their goldens or prototype runs exist.
