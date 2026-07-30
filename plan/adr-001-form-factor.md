# ADR-001 — Form factor and toolchain layout

**Phase:** 4.3 / 4.4
**Status:** **Accepted.** Decisions 1–4 approved by Nick 2026-07-30, as
proposed and without amendment. Decisions 5 and 6 ruled by Nick the same day
and applied.
**Date:** 2026-07-30
**Depends on:** D7 (Python), D9 (ontology-first), D10 (continuous change)

---

## Context

Phase 4's gating decisions are closed (4.1 D9, 4.2 D7, 4.2a D10). What
remains open is 4.3/4.4 — the form factor, chosen from the plan's three
candidates:

- **A. Claude skill** — fastest to build, weakest at deterministic verification.
- **B. Standalone Python pipeline** — deterministic stages, scriptable into CI.
- **C. Hybrid** — deterministic scripts, LLM stages via API, packaged as a skill.

Phase 3 data is essentially complete — 356 concept records, 303 dependency
edges, all cycles and `(P)` conflicts dispositioned — and **no code exists**.
Steps 3.5–3.7 (glossary, index, mermaid) were inverted by D9 from authoring
tasks into generation tasks, so they are now the first code the project needs.

A constraint surfaced during this decision: business users have VS Code with
the Claude extension, which raises the question of whether a skill is the
easier invocation surface for them.

## Decision 1 — form factor: **B now, C later** (approved 2026-07-30)

**The deliverable is a Python package `detangle` with a CLI. A Claude skill
wrapper is deferred to Phase 9.2 and is explicitly not built now.**

This is candidate C, staged — not a rejection of the hybrid. The two are not
alternatives: the Python package is required under any of the three
candidates, and "hybrid" adds a `SKILL.md` that shells out to the same CLI.
The only real question is *when* that wrapper is worth writing.

**Rationale.**

1. **A is ruled out by Phase 10.** The drift lint runs headless from Azure
   DevOps branch policy on every docs PR (10.2). Branch policy invokes a
   process, not a chat session. A skill cannot be the artifact.
2. **Deterministic verification needs importable code.** Phase 7's
   seeded-error acceptance test and Phase 10.7's twelve-fixture lint suite
   both require unit-testable functions with stable exit codes. Prose
   instructions cannot be asserted against.
3. **Business users do not invoke the tool.** D9's confirmed premise is that
   they *read and comment*; they never hand-edit the store. Their two working
   surfaces — reading generated `glossary.md`/`index.md`, and commenting on
   the PR (C3/C4) — are zero-install and identical under every candidate.
   The form factor does not touch their workflow.
4. **The VS Code extension does not lower the install floor.** Invoking the
   toolchain through the Claude extension still requires the repo cloned and
   a Python environment present, exactly as the bare CLI does. A skill buys
   natural phrasing for the person who already has both, not access for the
   person who has neither.
5. **Deferring is free if the CLI is wrapper-ready** (Decision 2). Building
   the wrapper now would mean wrapping commands whose shape is not yet known.

**Where the wrapper will earn its keep,** and why Phase 9 rather than never:
ad-hoc impact analysis (*"which concepts break if we redefine exposure?"* →
forward reachability) and D9 round-trip step 3 (propose a field value from a
PR comment). The latter needs a model regardless, but D9 stages it as
assisted-manual first, so neither is on the critical path.

## Decision 2 — CLI contract (approved 2026-07-30)

Rules that keep the package wrapper-ready and CI-ready from the first commit,
so adding `SKILL.md` in Phase 9 costs no rework:

- **Subcommands, one job each.** `detangle <verb> [args]`.
- **`--json` on every command** that reports findings; human-readable tables
  are the default, JSON is the machine contract.
- **Exit codes:** `0` clean, `1` findings raised (the branch-policy signal),
  `2` usage or internal error. Never `1` for a crash.
- **Never interactive.** No prompts, no TTY assumptions, no hidden state
  between runs.
- **No network by default.** Any command that reaches Azure DevOps or a model
  API says so in its name and requires an explicit flag.
- **Deterministic output.** Stable sort order everywhere, so the
  regenerate-and-compare guard (D9) compares bytes, not sets.
- **No hard-coded values** (working agreement). Every `param-*` from
  `definition-of-done.md` §Parameters is read from a config file
  (`detangle.toml`); the code ships no default that contradicts the rubric.

## Decision 3 — repo layout (approved 2026-07-30, tooling included)

```
src/detangle/
    records/      load, schema validation, span re-hashing
    graph/        NetworkX build; topo sort, cycles, reachability, orphans
    views/        glossary.md, index.md, concept-graph.mmd + gen: anchors
    cli.py
tests/
    fixtures/     seeded-error corpora (Phase 7, Phase 10.7)
detangle.toml     param-* values, sourced from definition-of-done.md
pyproject.toml
```

Packages deliberately absent until their phase: `extract/` (Phase 6),
`verify/` (Phase 7, MiniCheck), `devops/` (Phase 8), `lint/` (Phase 10).

**Tooling proposed** (per CLAUDE.md, tooling needs approval before use):
Python ≥ 3.11 (3.12.3 present), `pytest`, `ruff`, `PyYAML`, `networkx`.
`pandoc` is already a hard dependency — the `para_hash` scheme in
`concepts/README.md` is defined in terms of `pandoc -t plain` output — and is
invoked as a subprocess, not a library. Confirmed present: pandoc 3.1.3.

## Decision 4 — build order (approved 2026-07-30)

Three commands, in dependency order, none of which touches an LLM:

1. **`detangle validate`** — the record-set integrity checks currently run as
   throwaway scripts per PR and written out longhand in CLAUDE.md: YAML parse
   and required keys, `git_blob` match, `para_hash` present in the recomputed
   block-hash set, a verbatim run of each definition inside its anchored
   block, conflict quotes as verbatim substrings, `[[links]]` resolve, edge
   targets exist. Plus the structural invariants: C9 one-definition-site,
   `placement` recomputed against `used_in`, alias uniqueness across records.
   The C2 wording check is restricted to domain-shaped tokens per Nick's
   2026-07-30 ruling — ordinary English is exempt.

   It also checks **markdown table well-formedness** across `plan/`,
   `registers/`, the READMEs and the generated views: every row in a
   contiguous table has the same cell count. An edit in PR #65 silently
   collapsed a four-column row to three by dropping a leading `|`, and it
   survived review. **The cell count must be taken after removing escaped
   `\|`** — an escaped pipe is literal content, not a separator. The ad-hoc
   `awk` check used during that PR did not do this and false-flagged an
   untouched row in `concepts/README.md`, which is exactly the kind of noise
   that trains a reviewer to ignore the check.
2. **`detangle graph`** — build the NetworkX graph from `depends_on`; topo
   sort, `simple_cycles`, orphan and dead-entry detection, forward/backward
   reachability. Emits `concept-graph.yaml` (see the open ruling below).
3. **`detangle generate`** — the three views with `gen:` source-map anchors
   per D9, plus the regenerate-and-compare guard that makes hand-editing a
   generated artifact a CI failure.

This closes Phase 3 steps 3.5–3.7 and produces the standalone MTSAM
deliverable named in the sequencing rationale.

## Decision 5 — `concept-graph.yaml` is derived (ruled 2026-07-30)

**Nick's ruling, 2026-07-30: `concept-graph.yaml` is a derived artifact.**
Regenerated from the concept records (canonical `depends_on`) plus the bodies
(derived usage edges, C11); never hand-edited; hand-edits fail the
regenerate-and-compare guard. The concept records are the only source of
truth.

**The conflict was internal to the plan, not D9-versus-C6.** C6 called the
file the source of truth, citing D2 (2026-07-21). C11, as amended by D10
(2026-07-23), said "dependency edges in the concept records are the only
canonical edge data". Both sit in the same constraints table and cannot both
be operative. D2 simply predates D9 (2026-07-22), which moved canonicity into
the records, and was never revisited.

The substance follows: after D9 and D10 every edge in the file is either a
copy of a record's `depends_on` or a usage edge that is explicitly derived.
Nothing canonical remained in it. The charitable reading of C6 — that "source
of truth" meant only "the `.mmd` is generated from this, not hand-drawn" —
was plausible, which is why this was raised as a ruling rather than edited
unilaterally.

**Rejected alternative:** drop the file and render `concept-graph.mmd`
straight from the records. That would leave C11's usage edges without a home,
and `.mmd` diffs poorly.

**Consequence for the code:** `detangle graph` **writes** this file rather
than reading it, `depends_on` has exactly one edit site (the record), and
hand-editing the graph is a CI failure rather than a reconciliation problem.

**Applied in this PR:** plan C6, plan §4 Storage, plan §Phase 2 status, plan
step 3.4, plan Phase 3 Outputs, README Contents table, CLAUDE.md derived
list, and research-memo §D2 and §2.4. Nick ruled that §D2 be **rewritten
clean** rather than carrying an amendment note, so this ADR is the only
record of why the canonicity claim changed.

## Decision 6 — cycle dispositions get a canonical home (ruled 2026-07-30)

Decision 5 left `definition-of-done.md` §1 requiring each cycle to be
"recorded in `concept-graph.yaml` with a human disposition" — a hand-authored
datum in a file that is now purely derived. **Nick's ruling: dispositions
live in a canonical register, `registers/cycles.yaml`, which the generator
rolls up into `concept-graph.yaml`.**

**Not a record field.** A cycle is a property of a *set*, not of a concept.
On both members it has two edit sites and will drift, defeating the
single-edit-site guarantee D9 exists to provide; on one member the record
carries data about another concept and deleting it orphans the ruling. The
record schema is also corpus-anchored — every substantive field traces to a
`source` span — and a disposition has no corpus wording to anchor to. `notes`
cannot take it either: `concepts/README.md` declares that field "never
machine-processed", and the generator must read this datum.

**Not the waiver register.** `definition-of-done.md` §3 settles it: "A waiver
is a deferral, not an approval: the set is not fully done while waivers are
open." An accepted outer circle is an approval and permanent — filing it as a
waiver would block done-ness forever and destroy the register's signal
(accepted debt vs new regressions). The DoD has the direction right: waivers
*extend* the documented-exception pattern already used for cycles, so cycles
are the parent and waivers the sibling.

**A separate top-level tree, not `concepts/registers/` (Nick).** `concepts/`
then holds only corpus-derived business terms, one uniform schema, no
exclusions — a rule the validator can enforce flatly instead of carrying a
carve-out that rots. It also removes rather than fences the glob collision:
`concepts/removal-register.yaml` is a real record for the corpus term
"Removal Register". `concepts/reference-terms.md` moved to `registers/` under
the same rule, being a list of terms deliberately *excluded* from the record
set.

**The invariant this buys:** register entries are 1:1 with live cycles. A
cycle with no entry is a blocking finding; an entry with no cycle is a stale
ruling, flagged rather than dropped; a cycle resolved by narrowing gets no
entry, its trace being the clause moved verbatim to the record's `notes`.

**Entry point ruled 2026-07-30.** Criterion 1 clause 2 requires a designated
`entry_point` per cycle, and the 2026-07-29 ruling had accepted the cycle
without naming one. Nick ruled `liquidity-driven-reaction`: default before
exception, general before specific (criterion 2), and — the deciding
argument — it leaves the *identical-observable-pattern* clause resolving
backwards rather than deferred, that clause being what the records call the
load-bearing analytical difficulty of the anonymous market. Its own trailing
"unless … confirms identity-driven coordination" carries the forward
reference, marked as bridging text per criterion 7.

## Decision 7 — the assistant builds the whole toolchain (ruled 2026-07-30)

**Nick's ruling: the assistant builds `validate`, `graph` **and** the D9
view-generator, alongside delivering ontology content.** This supersedes the
earlier split — recorded in CLAUDE.md and in the assistant's memory — under
which Nick built the view-generator himself and the assistant supplied only
records and edges.

The two statements had already diverged in practice, and Decision 4 makes the
divergence load-bearing: `generate` is step 3 of the build order, so leaving
its ownership ambiguous would have stalled the sequence exactly where
`validate` and `graph` hand off. Nothing else in the ADR changes — the
generator still emits the three views with `gen:` anchors per D9, and the
regenerate-and-compare guard still makes a hand-edited view a CI failure.

## Consequences

**Already amended (Decision 5, ruled):** plan C6, plan §4 Storage, plan
§Phase 2 status, plan step 3.4, plan Phase 3 Outputs, README Contents table,
CLAUDE.md derived list, research-memo §D2 (rewritten) and §2.4.

**Amended on approval of Decisions 1–4 (2026-07-30, this PR):** plan §Status
and Phase 4.3/4.4 (form-factor decision recorded), README §Status (it still
said "Next: Phase 3 — build the concept records", which the 356 landed records
had overtaken), CLAUDE.md's "no build, no test runner, no lint" statement,
which stopped being true at the first commit of `src/`, and CLAUDE.md's
division-of-labour sentence per Decision 7.

**Not decided here** — deferred to their own phases: how LLM stages are
packaged and prompted (Phase 6), Azure DevOps authentication and PAT scope
(Phase 8), where the MiniCheck checkpoint is hosted and cached (Phase 7), and
whether the steady-state guard runs as a CI job or a pre-merge hook (Phase 10).

**Reversibility.** Decision 1 is cheap to revisit: adding the skill wrapper
later is additive. Decision 3 is a rename away from any other layout.
Decision 4's order is the constraining one — `validate` before `generate` is
what stops a malformed record set from silently producing a clean-looking
glossary.
