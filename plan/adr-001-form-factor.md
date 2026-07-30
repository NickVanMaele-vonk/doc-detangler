# ADR-001 — Form factor and toolchain layout

**Phase:** 4.3 / 4.4
**Status:** Proposed — awaiting Nick's sign-off
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

## Decision 1 — form factor: **B now, C later**

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

## Decision 2 — CLI contract

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

## Decision 3 — repo layout

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

## Decision 4 — build order

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
2. **`detangle graph`** — build the NetworkX graph from `depends_on`; topo
   sort, `simple_cycles`, orphan and dead-entry detection, forward/backward
   reachability. Emits `concept-graph.yaml` (see the open ruling below).
3. **`detangle generate`** — the three views with `gen:` source-map anchors
   per D9, plus the regenerate-and-compare guard that makes hand-editing a
   generated artifact a CI failure.

This closes Phase 3 steps 3.5–3.7 and produces the standalone MTSAM
deliverable named in the sequencing rationale.

## Open ruling required — is `concept-graph.yaml` canonical or derived?

Three documents still call it the source of truth — plan C6, plan §4
("Storage: a plain-text edge-list source of truth"), and the README Contents
table. D9/D10 make the **concept records** canonical, and CLAUDE.md's derived
list does not mention `concept-graph.yaml` at all. Under D9 it cannot be
canonical; the wording predates the decision.

C11 settles what it is *for*: derived usage edges ("section S uses term X")
live there. So:

- **Recommended:** `concept-graph.yaml` is a **derived artifact** —
  regenerated from the records (canonical `depends_on`) plus the bodies
  (derived usage edges), never hand-edited, hand-editing fails CI. Add it to
  the CLAUDE.md derived list; amend C6, plan §4, and the README table to say
  "generated from the records" rather than "source of truth".
- **Alternative:** drop the file entirely and generate `concept-graph.mmd`
  straight from the records. Rejected — it would leave derived usage edges
  (C11) without a home, and the `.mmd` render is lossy for diffing.

This needs Nick's ruling because C6 is a signed constraint, not just prose.

## Consequences

**Documents to amend on approval:** plan §Status and Phase 4.3/4.4 (record
the decision), plan C6 and §4 storage note (the ruling above), README
Contents table and Status, CLAUDE.md (derived list; the "no build, no test
runner" statement stops being true at the first commit).

**Not decided here** — deferred to their own phases: how LLM stages are
packaged and prompted (Phase 6), Azure DevOps authentication and PAT scope
(Phase 8), where the MiniCheck checkpoint is hosted and cached (Phase 7), and
whether the steady-state guard runs as a CI job or a pre-merge hook (Phase 10).

**Reversibility.** Decision 1 is cheap to revisit: adding the skill wrapper
later is additive. Decision 3 is a rename away from any other layout.
Decision 4's order is the constraining one — `validate` before `generate` is
what stops a malformed record set from silently producing a clean-looking
glossary.
