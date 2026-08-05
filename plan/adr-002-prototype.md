# ADR-002 — Prototype design (Phase 6)

**Status: PROPOSED** — nothing below is built; the working agreement says
Nick approves before any code is written. Decisions carry a recommendation
each; approving this document sets them, and any decision can be ruled
differently without reopening the others.

## Context

Phase 6 wants the smallest end-to-end version on one document: reorder plan
→ rewrite → self-report (6.1), compared to the golden against the rubric
(6.2). Phase 5 left three inputs this design builds on: an approved golden
triple for `U`, a measured review-load baseline (289 claims, 9 comment
clusters), and the observation that made this ADR's shape obvious — **almost
everything the golden did was mechanical.** 268 of 289 claims moved
verbatim; the ~21 derived ones were page-split rejoins with recorded joins;
the judgment lived in exactly two places: the reorder plan (which blocks go
where, what is noise), and the overview (the one Category C text). The
approved tooling list (ADR-001: Python, pytest, ruff, PyYAML, networkx,
pandoc) contains no LLM, and adding one needs approval.

## Decision 1 — where the judgment lives: **the reorder plan is data**

The pipeline splits cleanly into judgment and mechanics, and the split is
already institutional (8g two-stage review; "detection is automatic, the
disposition is Nick's"). Three candidates:

- **A — fully deterministic tool.** Impossible in full: a deterministic
  engine can *execute* a reorder plan but cannot *author* one — authoring
  is the judgment 8g exists to review.
- **B — LLM API inside the toolchain.** A new dependency needing approval,
  plus nondeterminism inside commands whose exit codes branch policy
  trusts, plus secrets in CI. Nothing in Phase 6 needs it.
- **C — the plan is data; the tool executes plans and never authors them.**
  A machine-readable reorder plan is authored the way everything else in
  this project is authored — AI-drafted, human-approved, landed by PR (8g
  stage A). `detangle restructure` then executes it deterministically and
  produces the self-report. The judgment stays reviewable and the tool
  stays deterministic.

**Recommendation: C.** It matches how Phases 3–5 actually worked, keeps the
tooling list unchanged, and makes 8g's stage A a first-class artifact
instead of prose. Candidate B is not rejected forever — it becomes a
Phase 9 question, after the harness exists to check its output.

## Decision 2 — the machine-readable plan: `eval/golden/uce.plan.yaml`

The stage-A artifact gains a machine-readable twin the tool consumes.
Schema, mirroring what the golden's move-map already records:

- `doc`: the source path (must be a registered document); `pinned_blob`.
- `sections`: ordered list — `id` (the stamped `u-<8 hex>`), `title`, and
  for generated sections (`overview`, `terms`) their role.
- `assignments`: source block → target section, blocks addressed by
  `para_hash` (+ heading path), **never line numbers** (D10).
- `rejoins`: ordered fragment lists (the seven page-split rows), each
  producing one output row.
- `noise`: verbatim strings dropped as formatting, so the drop is declared
  data, not tool behaviour.
- `definitions`: record id → target section (the 35 placements).
- `additions`: Category C blocks by section, each carrying its marker form.

The human-readable `reorder-plan.md` stays the review surface; the YAML is
what runs. Drift between them is caught the usual way: the self-report is
regenerated and compared. A block in the source that no assignment, rejoin
or noise entry covers is a **finding** (`plan-incomplete`) — losslessness
enforced at run time, before criterion 4 ever has to catch it.

## Decision 3 — one new command: `detangle restructure`

`detangle restructure <doc>` reads the registry and the plan, and writes
the restructured document plus the generated 8f artifacts (move-map,
counts, exceptions — the golden's hand-written ones become the format
spec). `--check` re-runs and byte-compares against the committed output,
same contract as `graph --check`. Exit codes per ADR-001: `0` clean, `1`
findings (plan-incomplete, token-parity residue, budget breaches), `2`
usage. The criterion-5 **token-parity check** — the multiset diff used to
verify the golden — moves from a scratchpad script into the command, which
is the "buildable from Phase 6" the rubric already promises. The 8c budget
rule is enforced here too: more clusters than `param-max-comments-per-PR`
→ the command fails and reports rather than emitting output.

## Decision 4 — 6.2 comparison: per-criterion, not byte equality

The prototype's output is compared to the golden mechanically where the
rubric is mechanical: section structure and order, definition-block
placement and byte-identical prose, token parity (criterion 5), marker
discipline (criteria 7/9 forms), orphan and exception rosters, comment
clusters against the 5.3 baseline. Byte equality of the whole document is
**not** the bar — the golden's incidental formatting is not normative.
Where the two disagree, the golden wins unless Nick rules the prototype
found a golden defect; either way the disagreement is a recorded finding.
The `param-low-confidence-threshold` re-baseline stays tied to 6.2 as
ruled, with one honesty note: under Decision 1C the run has no machine
confidence scores, so the re-baseline uses the first artifact that carries
a mapping score — the Phase 7 harness dry-run over the prototype output —
and 6.2 is not done until that number has been looked at.

## Decision 5 — scope of 6.1: `U`, executing the approved plan

The prototype runs on `U` against the pinned blob, executing a
`uce.plan.yaml` transcribed from the approved reorder plan. That makes 6.2
a controlled comparison: same input, same plan, hand execution (the
golden) vs machine execution (the prototype). `S` and `M` wait for
Phase 9.1, as the plan already says.

## Consequences

- No new dependency; the approved tooling list stands.
- The build order inside Phase 6: (1) plan schema + loader + validation,
  (2) `restructure` execution + self-report, (3) token-parity check,
  (4) the 6.2 comparison run, recorded in `eval/`.
- `CHECKS` grows new slugs (`plan-incomplete`, `token-parity`, …) declared
  per module as `tests/test_checks_declared.py` requires; waivability to be
  decided per slug when built (drift-style checks stay non-waivable).
- The Claude-skill wrapper (ADR-001 candidate C) is unaffected: what it
  would wrap later is exactly the plan-authoring workflow Decision 1
  keeps outside the tool.
