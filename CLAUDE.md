# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Style

- Answer factually and concisely in plain English. 
- Save tokens: avoid multiple hits against the same text, use scratchpads to optimize your token use. 

## Interaction with other knowledge stores
Use the following places as master system:  
- historical state of this project: git (pull requests and commits) 
- user-facing instructions: `README.md`
- best practices for writing software code: `ENGINEERING_PRINCIPLES.md`
- future to do's: `plan/backlog.md`
- architecture decision record (ADR): `plan/adr-*.md`
- tool architecture: `plan/ARCHITECTURE.md`

Do not restate in this file what those own. In particular: no session logs, no
counts a command can compute (backlog B-2), no design rationale that belongs in
`plan/ARCHITECTURE.md`.

## What this repository is

Detangle — an agent/pipeline that turns convoluted markdown specifications
into a logically structured five-document set. The repo holds the normative
specification (`plan/`), a read-only set of examples (sometimes calles "source corpus") (`samples/`), the canonical Phase 3 data (`concepts/`, `registers/`), in-progress working artifacts (`work/`), the Phase 5 evaluation set (`eval/`), and — from ADR-001 onward — the toolchain itself under `src/detangle/`.

**Form factor (ADR-001, approved 2026-07-30):** a Python package `detangle`
with a CLI. The Claude-skill wrapper is candidate C staged, deferred to
Phase 9.2, and explicitly not built now. Approved tooling: Python ≥ 3.11,
`pytest`, `ruff`, `PyYAML`, `networkx`, and `pandoc` invoked as a subprocess.
Anything beyond that list still needs approval before use — which is exactly
why the Phase 7 harness runs deterministically: its model stages would need
PyTorch and `transformers`, so they wait behind `--use-inference` (ADR-003
Decision 3, deferred by Nick 2026-08-07; backlog B-9).

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
.venv/bin/detangle validate            # record-set integrity, always set-wide too
.venv/bin/detangle graph               # rewrites concept-graph.yaml
.venv/bin/detangle graph --check       # regenerate-and-compare guard, for CI
.venv/bin/detangle graph --impact <id> # what depends on this definition
.venv/bin/detangle graph --requires <id>   # what must be defined first
                                       # (there is no --mmd: backlog B-6)
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
.venv/bin/detangle verify --output U=<doc.md>
                                       # the Phase 7 losslessness harness
                                       # (ADR-003); --output CODE=PATH once
                                       # per document, detangle set only.
                                       # DETERMINISTIC: it does NOT check for
                                       # invented text — that stage needs a
                                       # model and waits behind
                                       # --use-inference (backlog B-9)
.venv/bin/detangle verify … --report <path>
                                       # write the verification report: stage
                                       # table, the 7.5 blob version record,
                                       # coverage, forward references, and
                                       # the roster of unplaced claims
```

`.venv/` is gitignored. `detangle validate` replaces the throwaway per-PR
validation scripts — run it on the records a PR touches instead of writing a
new script each time.

**Exit codes are the contract:** `0` clean, `1` findings, `2` usage or internal
error. **`0` and `1` are verdicts; `2` is the absence of one** — never read `2`
as "no findings". Any unexpected exception exits `2`, never `1`, because branch
policy reads `1` as a completed run that found things. Full table in the README.

`.github/workflows/ci.yml` runs three jobs on every PR to `main` — tests+lint,
`validate`, and `graph --check` — each as its own job, so a red run names the
gate that failed. `verify` is deliberately **not** a gate (ADR-003 D5,
reaffirmed by ADR-004 D7): every check it raises awaits a human disposition, so
blocking merge on one turns a review prompt into a hard stop. It runs at
`param-full-verify-cadence` — every re-run — not per PR.

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
| `plan/definition-of-done.md` | The rubric: **criteria 1–9**, parameters (`param-*`), non-goals, per-phase applicability |
| `plan/research-memo.md` | Phase 2 research and the **decision register D1–D10** (§7), with full rationale notes for D9 and D10 |

These three are cross-referential and use stable identifiers. **Cite the
identifier, not a paraphrase** — write "per C9" or "criterion 3" or "§D10
element 4". When you change one document, check whether the other two assert
the same thing; a constraint typically appears once in each (e.g. glossary
placement is C9 *and* criterion 3 *and* plan §4).

Decisions D1–D10 are all signed off. Do not reopen a signed-off decision;
propose an amendment with rationale and let Nick rule. The same holds for the
ADRs' ruled decisions.

`plan/backlog.md` (`B-n` entries) is **not** normative — parked candidate work,
nothing in it approved or scheduled. Add to it rather than to the three above
when an idea has no phase yet.

## Architecture

**`plan/ARCHITECTURE.md` is the master.** Read it before changing anything
structural. The load-bearing ideas, so you know when to go there:

- **The concept graph is the backbone**, not a side artifact — reading order,
  glossary order, `index.md`, impact analysis, cycles and orphans all fall out
  of one edge set (§1).
- **Ontology-first (D9)**: records own the *ontology*; the **definition site
  owns the definition prose**, `glossary.md` included (§2).
- **Canonical vs derived (D10 §4)** governs everything; anything location- or
  order-sensitive is derived (§3).
- **Placement is computed, not judged** (C9, two limbs) — never hand-set
  `placement`, run `detangle validate` (§4).
- **Two input sets**: the detangle set is restructured and counted; the
  reference set is read-only but citable (§5).
- **`concepts/` vs `registers/`** — two canonical trees, one rule each; four
  registers (§6).
- **Findings block, waivers defer, notices are neither** (§7).
- **Record-authoring conventions** — span anchoring, C2 assembly, edge
  discipline, PR mechanics (§10).
- **Working with the corpus** — criterion 5 verbatim reproduction, and why
  `samples/` cannot be untracked (§11).

## Current state

Phases 1, 2, 4 and 5 are closed. Phase 3's data work is done; steps 3.6
(`index.md`) and 3.7 stay blocked behind Phase 5's document bodies, so neither
is the next thing to work on. Phase 6 is all but closed on ADR-002 — all build
steps merged and the 6.2 comparison written — but **6.2 stays open** until
`param-low-confidence-threshold` is re-baselined against the first artifact
carrying a mapping score. Phase 7 is in progress on ADR-003: Decisions 1, 2, 4
and 5 are ruled and built, 3 is deferred (backlog B-9), 6 and 7 are proposals.

**Outstanding, in rough order:**

1. **ADR-004 build step 3** — write Decisions 1 and 3 into C2, C5 and criterion
   7, including the `param-overview-max-words` re-measurement from 227 to 206.
2. **Awaiting Nick's disposition:** the one live `forward-use` finding, on
   `gate` in the glossary's own generated banner — a sense collision (the record
   is a business term; the banner uses the English word), deliberately not
   suppressed. And the claim-split flags on `U`, none ruled yet;
   `registers/claim-splits.yaml` is empty.
3. **Unbuilt, with a ruling behind them:** the glossary drift lint (which is
   what unblocks the fourth CI gate), `graph --mmd` (B-6), the
   `state/notices.md` generator (B-7).

For counts — records, defined terms, placement split, edges — run `detangle
validate` or `detangle graph` rather than trusting a number written down
anywhere. For what landed when, read the PRs.

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
