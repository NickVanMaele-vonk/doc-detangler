# Detangle — Document Restructuring Agent

Tooling to transform convoluted markdown documents into logically
structured, human-readable documents with clear definitions.

## Problem description

At times, supplied requirements documentation is dense and detail-first: 
- little to no top-down introduction of business concepts.
- cryptic terms are used before they are introduced
Representative examples: the `./samples/blueprint-*-shortened.md` files.

Doc detangler takes the following input: 
- source documents -> these will be restructured
- reference documents: will be consulted as context and definitions sources

Doc detangler generates the following output: 
- restructured source documents: order of text changed so that every term is defined before it is used
- glossary: for definitions of terms occurring in more than one document
- index: where each term is used in the documents

## Approach

A concept dependency graph drives the pipeline: extract domain terms, record
which definitions depend on which, then use topological ordering to restructure
documents so every concept is defined before first use. A verification harness
proves losslessness — no meaning lost, no meaning invented.

The input is **two sets of documents** (Nick, 2026-08-05). The **detangle
set** — three documents today — is what gets restructured; the output is
**five** documents: the three restructured documents, plus a glossary, plus
an index. The **reference set** is additional read-only documents that
supply definitions and context — never modified, never counted for term
placement, but a definition found only there is lifted into the output with
provenance pointing at the reference file. Both sets are declared in
`detangle.toml [documents]` (`components` and `references`).

A single `glossary.md` is read first and holds the definition of every term used in more than one detangle-set document; terms local to one document are defined there. No term is defined twice, and none is left undefined. 
Putting the shared definitions ahead of everything is what makes "defined before first use" achievable across a heavily interdependent set — and it turns cross-document definitional cycles, which no reordering can fix, into intra-glossary ones, which reordering can. The glossary is ordered **topologically**, so it reads start to finish without ever meeting an undefined term. 

Reading order and lookup order are separated rather than compromised. 

`index.md` is the fifth document: a single **alphabetical** list spanning all four others, giving each term and the location of its definition. `index.md` contains terms only, no definitions. It sits outside the reading order, is generated rather than written, and answers the one question a glossary ordered for reading cannot: *where is this term?*

If one term appears in more than one input document, then: 
- "what is this term's definition?" -> via glossary
- "where is this term used in the corpus?" -> via index 

## Hard constraints

- No meaning lost or invented; omissions require explicit human approval.
- No meaning *weakened*: numbers, thresholds, modality (`must` vs `should`),
  scoping qualifiers, citations, and classification markings are preserved
  verbatim. Source contradictions are surfaced, never silently fixed.
- Bridging/explanatory additions are allowed but must be marked as such;
  rewritten source text is marked separately, as *derived*.
- Any update on an existing document goes through pull requests ("PRs"); the tool posts findings as PR comments, which must be Resolved before merge.
- Glossary-first, single definition site: a term used in more than one
  document is defined in `glossary.md` and only there; a term used in only one
  document is defined in only that document.
- Reading order and lookup order are separate artifacts: `glossary.md` is
  topological, `index.md` is alphabetical and covers every term across all
  four other documents. The index is generated and contains no definitions.
- Links run forward only: each section links its first use of a glossary
  term to that term's entry. A glossary defines terms; it does not record
  where they are used. Usage locations are graph edges in
  `concept-graph.yaml`.
- A PR assembles changes relating to similar concepts and may touch any
  number of documents — document count is not the unit. A PR may not change
  more terms than `param-max-terms-changed-per-PR` (200). Each PR is two
  commits — moves only (machine-verified set-wide, no semantic review), then
  text changes (the only part a human reads). Comments are raised per
  cluster, not per instance, and a run exceeding either budget fails rather
  than opening an unreviewable PR.
- All artifacts (including the concept graph) are plain-text and git-friendly.

## Contents

| File | Purpose |
|------|---------|
| `./plan/detangle-agent-plan.md` | Full project plan: 10 phases, constraints, rubric, sequencing rationale |
| `./plan/definition-of-done.md` | Rubric for "logically structured, human-readable": 8 criteria, parameters, non-goals, per-phase applicability *(Phase 1 — approved)* |
| `./plan/research-memo.md` | Standards to follow and open-source components to reuse, with coverage gaps stated; carries the decision register D1–D10 *(Phase 2 — complete, all decisions signed off)* |
| `./plan/adr-001-form-factor.md` | Form factor and toolchain layout: Python package + CLI, CLI contract, repo layout, build order *(Phase 4.3/4.4 — accepted 2026-07-30)* |
| `./plan/adr-002-prototype.md` | Phase 6 prototype: the reorder plan is **data**, `detangle restructure` executes it and authors nothing *(approved 2026-08-05 — all four build steps merged)* |
| `./plan/adr-003-verification-harness.md` | Phase 7 losslessness harness: decomposition, coverage, fabrication, structure *(Decisions 1, 2, 4, 5 ruled and built; 3 deferred to backlog B-9; 6 and 7 proposals)* |
| `./plan/adr-004-iterative-rerun.md` | The operating model: the detangle run is a repeatable campaign, and **assurance** rather than corpus anchoring carries definitional strength *(all decisions ruled 2026-08-07; the normative-document edits for Decisions 1 and 3 are outstanding)* |
| `./plan/backlog.md` | Parked candidate work, `B-n`. Non-normative — nothing in it is approved or scheduled |
| `src/detangle/` | The toolchain: `validate`, `graph`, `generate`, `lift`, `restructure` and `verify` *(built)*. `generate` seeded `glossary.md`, which from 2026-08-04 is human-edited rather than regenerated and since 2026-08-08 is mirrored into the records by `lift`; `index.md` awaits the document bodies (step 3.6); the Mermaid render is designed as an on-demand command and **not built** (backlog B-6); `verify` runs deterministically and its two model-dependent stages are **not built** (backlog B-9) |
| `azure-pipelines.yml` | Branch policy: tests + lint, `detangle validate`, `detangle graph --check`, `detangle lift --check` — one job per gate *(built)*. The fourth gate is the glossary drift lint, not `detangle generate --check`: `glossary.md` is edited by humans, so byte-comparing it is incoherent — `lift --check` compares the records' derived copies against it instead |
| `detangle.toml` | Configuration: `param-*` values from the rubric, the document registry — the detangle set (`components`) and the read-only reference set (`references`, 2026-08-05) — and validation thresholds. No value is hard-coded in the package |
| `glossary.md` | Business domain glossary — first document of the output set; defines every term used in more than one document, ordered topologically. Seeded by `detangle generate` from the concept records *(step 3.5 — built; the overview is a marked gap and 77 entries are undefined)*. From Nick's ruling of 2026-08-04 it is the **fourth editable document**: humans edit it directly and `detangle lift` mirrors its definitions into the records, guarded by `lift --check` in CI (built 2026-08-08). The guard's *reorder* of an out-of-order entry remains Phase 10; today `lift-order` flags it for a human |
| `index.md` | Alphabetical index across all four other documents: every term plus the location of its definition. Generated *(Phase 3 — pending)* |
| `concepts/` | Canonical concept records — one YAML file per corpus-derived business term, and nothing else *(Phase 3)* |
| `registers/` | Canonical data that is not a corpus term: `cycles.yaml` (cycle dispositions, criterion 1), `reference-terms.md` (regulator- and industry-owned terms, criterion 3), `waivers.yaml` (findings dispositioned but not yet fixable, step 3.9) and `claim-splits.yaml` (approved claim boundaries the decomposer would not guess at, ADR-003 Decision 1 — home ruled by Nick 2026-08-07, empty until the Decision 7 dry-run rules the flags) *(Phase 3, Phase 7)* |
| `concept-graph.yaml` | Concept dependency + usage edge list (SKOS concept model). Written by `detangle graph` from the concept records and registers, which are the source of truth; never hand-edited *(dependency edges built; usage edges arrive with the bodies in Phase 5)* |
| *(no `concept-graph.mmd`)* | A whole-set diagram would be one 238-node tangle plus 108 loose dots, so none is committed *(Nick, 2026-08-04)*. The replacement — `detangle graph --mmd <id>`, printing one concept's neighbourhood to paste into a PR comment where GitHub and Azure DevOps render it natively — is **designed, not built**: the flag does not exist and nothing in the package renders Mermaid *(backlog B-6)* |
| *(no `state/notices.md`)* | Things worth knowing that are not defects — demotion candidates, review dates falling due, authoring debts — are to be generated into `state/notices.md`, committed so new entries show in the PR diff, and deliberately **unguarded**: a stale notices file must never block a PR *(Nick, 2026-08-04)*. **Designed, not built**: no generator exists and no `state/` directory is committed *(backlog B-7)* |
| `eval/` | Test inputs and golden reference outputs. `eval/README.md` designates the three shortened blueprints as test inputs, pinned to their git blobs, and names UCE as the golden target *(step 5.1 — done; the golden itself, step 5.2, is pending)* |

## Status

Phases 1, 2, 4 and 5 complete; Phase 3 nearly so; **Phase 6 all but closed**
(`plan/adr-002-prototype.md`, approved 2026-08-05 — all four of 6.1's build
steps merged and the 6.2 comparison written, but 6.2 stays open until
`param-low-confidence-threshold` is re-baselined, which needs Phase 7); and
**Phase 7 in progress** (`plan/adr-003-verification-harness.md` — four of
seven decisions ruled and built, the model-dependent half deferred).
`plan/adr-004-iterative-rerun.md`, ruled in full on 2026-08-07, resets the
operating model: the detangle run is a **repeatable campaign**, not a one-off,
and **assurance** — who wrote a claim and who approved it — rather than corpus
anchoring is what carries definitional strength.
Rubric approved (`plan/definition-of-done.md`);
research memo delivered (`plan/research-memo.md`) across three rounds. The
gating architecture decisions were signed off 2026-07-22: runtime is
**Python** (D7), and the definition layer is **ontology-first** (D9) —
structured concept records are the source of truth for the *ontology*:
identity, placement, provenance and dependency edges. Nick's ruling of
2026-08-04 moved the definition **prose** out to the documents that define it,
`glossary.md` included; `index.md` remains a generated view, and the Mermaid
render is produced on demand rather than committed.
Phase 4 closed 2026-07-30 with `plan/adr-001-form-factor.md`: the deliverable
is a Python package **`detangle`** with a CLI, and the Claude-skill wrapper is
deferred to Phase 9.2.

Phase 3 data is essentially complete — **359 concept records** under
`concepts/` with 402 `depends_on` edges, every cycle and definition conflict
dispositioned, and the criterion-3 reference terms and cycle rulings in
`registers/`.

All three ADR-001 commands are built — `restructure` came later with Phase 6
and `verify` with Phase 7, both below. **`detangle validate`** replaces the
throwaway per-PR scripts with a tested implementation of the record-set
integrity checks. **`detangle graph`** builds the concept graph from the
records' canonical `depends_on`, rolls up `registers/cycles.yaml`, and writes
the derived `concept-graph.yaml` — reading order, cycles, orphans, dead
entries, and reachability queries for impact analysis. **`detangle generate`**
seeded `glossary.md` from the records in that graph's topological order, with
every entry delimited by `concept:<id>:start`/`:end` markers (the bodies'
scheme, restamped 2026-08-08) so a comment resolves to the record behind it
(D9) and the lift knows where a definition's prose ends.

That file is now the starting point rather than the output: from 2026-08-04
`glossary.md` is the fourth **editable** document, its 78 definitions
canonical in the file and mirrored back into the records. The mirror is
**`detangle lift`** (built 2026-08-08): it lifts edited prose between an
entry's markers into the record's derived `definition` field, maintains the
mechanical lineage span — `origin: authored`, anchored by the prose's
`para_hash` and the glossary's git blob (ADR-004) — and never writes
assurance, ontology (`term`, `aliases`), or `depends_on`: a lifted definition
with no named author, or a heading/alias line contradicting its record, is a
finding a human resolves in the same PR. `lift --check` reports what a lift
would change and is the fourth CI gate. `generate` still **refuses to
overwrite** the file — a re-seed discards human edits deliberately, `--force`
only (it will be needed when B-1 rewrites the corpus). `index.md` still
needs the document bodies, which carry the definition site of the other 94
defined terms (criterion 4). The Mermaid render is no longer a file at all —
it became an on-demand command, since 359 nodes never made a readable
diagram.

A fourth command, **`detangle restructure`**, arrived with Phase 6 (ADR-002):
it executes a machine-readable reorder plan and writes the restructured
document. The judgment — what moves where, what is noise, which page-split
fragments rejoin, the Category C text — lives in the plan, an
AI-drafted/human-approved artifact landed by PR; the command is mechanical
and authors nothing. Two guarantees it enforces on every run:

- **Nothing undecided is executed.** Every source block must be covered by
  exactly one assignment or noise entry; an uncovered one is
  `plan-incomplete` and **no document is written**, because writing from an
  incomplete plan launders a coverage hole into an omission.
- **Criterion 5 is checked in-command.** `token-parity` is a multiset diff
  of word tokens: the blocks the plan assigns, after the plan's declared
  removals and repairs, against every part of the output tagged as carrying
  source words. Authored text — the overview, definition blocks copied from
  records — is excluded, because its words are not claiming to come from the
  document. Words that are in neither the output nor a declared drop, and
  words the output invents, are findings. Nothing is repaired: the
  disposition is a plan edit, and that is a human's.
- **A block moved by hand is reported, not silently undone** (ADR-004
  Decision 8). Fixes typed into the markdown split in two, and only one kind
  survives a re-run: wording fixes are carried through, because blocks move
  verbatim, while a paragraph you relocate by hand is put back, because the
  plan governs position. The rule is **wording goes in the markdown,
  position goes in the plan**, and `plan-position-conflict` makes breaking
  it visible — a **warning**, carrying the plan line that would ratify the
  move. It fires only on already-structured input (a document carrying
  `sec:` markers, which is what a previous run emits); run 1 reorders nearly
  everything by design, so there is nothing to contradict. A hand-move is a
  proposal, exactly as a body edit proposing a `depends_on` edge is:
  detection is automatic, the disposition is a human's.

The run also accounts for itself. `--report <dir>` writes the criterion-8f
self-report — `move-map.md` (every block, where it went, what was done to it,
what was dropped and why), `counts.md` (the category tallies and the
criterion-5 accounting) and `exceptions.md` (what a reviewer is being asked to
look at). They are derived artifacts: `--check` byte-compares them, and
`report-drift` is no more waivable than any other hand-edited generated file.

**The tool writes what it measured; a human writes the rulings.** Block moves,
drops, tallies, the undefined-term roster and forward references are
measurements, and the report states them in full. That the version skew stands
rather than being harmonised, or that OCR damage is carried verbatim, is
judgment — so the plan carries one line per ruling, a title and a pointer to
where the reasoning is written, and the report names it and points there
rather than reprinting it. The wording lives in one place. The tool needs the
line for one reason only: the 8c rule caps how many PR comments one
restructure may raise (`param-max-comments-per-PR`), and a comment it cannot
see is one it would count wrong. Over budget, the run reports and writes no
document.

A fifth command, **`detangle verify`**, arrived with Phase 7 (ADR-003): it is
the losslessness harness that constraints C1/C2 rest on. It decomposes the
source and the output into claims, places every claim that moved verbatim, and
checks that no term is used before its definition across the whole reading
order — glossary → UCE → SBSP → MCL, not each document alone, because C9
should make a cross-document forward reference impossible and an empty result
is the proof it did.

**It runs deterministically, and it says so loudly** (Nick, 2026-08-07). Two of
the four Phase 7 stages need a model and are deferred behind a
`--use-inference` flag that is backlog B-9: the scored coverage residue and the
fabrication check. So the command **cannot say whether the output contains
invented text**, and a run that exited `0` while skipping that would read as a
proof it never produced — the same trap as reading exit `2` as "no findings".
Three things prevent it: the report prints every stage including the ones that
did not run, the `--json` summary carries `fabrication: NOT CHECKED`, and a
`coverage-unscored` warning names, per document, how many claims the run
declined to rule on. That warning is one per document rather than one per
claim (rubric §8d) and is waivable, because nothing is wrong — work is
outstanding.

`--report <path>` writes the verification report, which carries the **step 7.5
version record**: the git blob of every document the run read, plus the commit.
A blob is the version — immutable, retrievable with `git show` however many
revisions follow — so a report from three re-runs ago still names exactly the
bytes it was talking about, and the next run has a baseline. `manifest.yaml`
(step 10.4) absorbs this when it exists. There is no timestamp in the report,
deliberately: the commit and the blobs date the run, and a clock would make it
irreproducible.

Where the decomposer cannot confidently split a span it **flags** it rather
than guessing, and the approved split lands in `registers/claim-splits.yaml`
(ADR-003 Decision 1; home ruled by Nick 2026-08-07). Judgment is data, reviewed
by PR and executed by the tool — the reorder-plan pattern one level down, and
the reason `verify` calls no model even when it is applying human judgment.
The register is read on every run and its blob goes into the report, because
the overrides move the claim list as surely as the decomposer version does.
It is empty today: the decomposer raises 44 flags on `U` and none has been
ruled, which the Decision 7 dry-run does.

`verify` is **not a CI gate** (ADR-003 Decision 5, reaffirmed with ADR-004
Decision 7). Every check it raises awaits a human disposition, so blocking a
merge on one converts a review prompt into a hard stop.

## Running it

`pandoc` must be on `PATH` — the `para_hash` scheme is defined in terms of its
plain-text output, so it is a hard dependency, not a convenience.

Run everything from the project root — the directory holding `detangle.toml`
(`detangler/` inside the MTSAM-docs repository, not the repository root):

```bash
python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"

.venv/bin/detangle validate            # the whole record set
.venv/bin/detangle validate concepts/widget.yaml   # just what a PR touches
.venv/bin/detangle validate --json     # machine-readable, for CI

.venv/bin/detangle graph               # rewrite concept-graph.yaml
.venv/bin/detangle graph --check       # CI: fail on a hand-edit or a stale graph
.venv/bin/detangle graph --impact gate # what breaks if this definition changes
.venv/bin/detangle graph --requires sb-26   # what must be defined first

.venv/bin/detangle generate            # seeded glossary.md; now refuses to
                                       # overwrite it (exit 2) unless --force
.venv/bin/detangle generate --check    # read-only: compare against a regeneration

.venv/bin/detangle lift                # mirror glossary.md edits into the records
.venv/bin/detangle lift --check        # CI: fail while the two disagree

.venv/bin/detangle restructure --plan eval/golden/uce.plan.yaml \
                    --out work/uce.md   # execute a reorder plan (ADR-002)
.venv/bin/detangle restructure --plan … --out … --report work/report/
                                       # also write the 8f self-report
.venv/bin/detangle restructure --plan … --out … --check   # re-execute and compare

.venv/bin/detangle verify --output U=eval/golden/uce.md
                                       # the Phase 7 harness, deterministic
.venv/bin/detangle verify --output U=… --report work/verification.md
                                       # also write the 7.5 version record
                                       # (--use-inference is backlog B-9)

.venv/bin/python -m pytest             # tests
.venv/bin/ruff check .                 # lint
```

### Exit codes

Exit codes are the branch-policy contract (ADR-001 Decision 2). The governing
distinction is that **`0` and `1` are verdicts; `2` is the absence of one.**

| Code | Name | Means | CI should |
|------|------|-------|-----------|
| `0` | clean | The command ran every check it was asked to and raised nothing | proceed |
| `1` | findings | The command ran to completion and has something a human must disposition | post the findings; block the merge until each is dispositioned (`param-false-positive-tolerance` is none, but "false positive" is a valid disposition) |
| `2` | usage or internal error | The command reached **no verdict** | fail the build loudly, and never read it as "no findings" |

What raises each:

- **`1`** — any `Finding` at all, `error` or `warn`. Severity ranks findings
  for a reader; it does not change the exit code, so a stale span cannot pass
  CI by being less severe than a malformed one. The one exception is a finding
  covered by the waiver register — see below.
- **`2`** — an unknown flag or missing subcommand; a missing or malformed
  `detangle.toml`; a `param-*` the rubric has not set; a `[paths]` entry that
  is not a directory; a path argument that is not a concept record; an unknown
  id passed to `--impact`/`--requires`; `pandoc` missing or failing; a failing
  `git rev-parse`; an unreadable source document; **and any unexpected
  exception** — the traceback goes to stderr and the code is still `2`, never
  `1`. `--json` does not apply: a usage error writes plain text to stderr,
  because there is no findings document to emit.

Reachability queries (`graph --impact`, `graph --requires`) report no findings
and exit `0` for any known id, `2` for an unknown one.

### Waived findings

`registers/waivers.yaml` (plan step 3.9) holds findings that have a human
disposition but no fix yet — today, three `definition-token` findings ruled
source-document defects, whose repair waits on the B-1 source-correction path.
**Every command reads the register** (Nick, 2026-08-05, when there were three;
`restructure` joined them and reads it too). Each prints a
covered finding in its own `waived` block and counts it in the summary, but
leaves it out of the exit-code decision, so a gate waiting on work elsewhere
can still be green and can therefore be marked required. Waiving is a separate
channel, not a third severity: everything left in the live list still blocks,
whatever its severity.

An entry matches on `check` + `where`, narrowed by an optional `match`
substring of the finding's message — exact strings only, no globs or regex.
Entries and live findings are 1:1, so an entry that matches nothing raises
`waiver-stale` (warn) and a fix must remove its waiver in the same PR.

**Staleness is judged only by the command that ran the check.** A command that
never ran one cannot prove its waiver dead — `validate` does not check the
glossary's overview, so without this it would report an `overview-gap` waiver
as stale on every run, and `waiver-stale` is a finding on a required gate.
Each module declares the checks it raises in a `CHECKS` constant, and
`tests/test_checks_declared.py` reads the slugs back out of the source so the
declaration cannot drift.

Two families cannot be waived. `register-parse`, the claim-split register's
`split-parse` and `split-schema`, and the `waiver-*` checks, because a
malformed register must not excuse itself. And the drift checks —
`graph-drift`, `graph-missing`, `glossary-drift`, `glossary-missing`,
`restructure-drift`, `restructure-missing`, `report-drift`, `report-missing` —
because a waiver defers work somebody must do later, and regenerating a derived
file is a single command: C6 and ADR-001 Decision 5 hold only while a
hand-edited artifact cannot excuse itself. The list is
`registers.NOT_WAIVABLE`, and every derived artifact the toolchain gains
extends it. A waiver is a deferral, not an
approval (`definition-of-done.md` §3) — the set is not done while waivers are
open, which is why a waived finding is still printed on every run.

### In branch policy

`azure-pipelines.yml` runs four gates on every PR to `main`, one job
each, so a red run names which gate failed and each can be marked required
separately (in Azure DevOps, PR validation is a Build Validation branch
policy pointing at the pipeline — the YAML `pr:` keyword is ignored for
Azure Repos; `.github/workflows/ci.yml` is the same four gates in their
original GitHub Actions form, kept until the move to MTSAM-docs completes):

| Job | Command | Guards |
|-----|---------|--------|
| `tests and lint` | `ruff check .`, `python -m pytest` | the toolchain itself |
| `detangle validate` | `detangle validate --json` | the **canonical** records against `samples/` — spans, blob ids, verbatim definition runs, conflict quotes, links, edge targets, one definition site — less whatever `registers/waivers.yaml` covers |
| `detangle graph --check` | `detangle graph --check --json` | the **derived** `concept-graph.yaml` against the canonical records and registers |
| `detangle lift --check` | `detangle lift --check --json` | `glossary.md` against the records' **derived** definition copies — plus entry order, marker hygiene, and ontology drift (a heading or alias line contradicting its record) |

The fourth gate was originally designed as `detangle generate --check`, and
that command is still built. It is **not** in the workflow, and after Nick's
ruling of 2026-08-04 it never will be: the glossary is a human-edited
document, and byte-comparing a file people edit is incoherent. The glossary
drift lint replaced it (2026-08-08): instead of comparing the file against a
regeneration, `lift --check` compares the records' derived copies against the
canonical file — the same regenerate-and-compare idea, pointed the direction
the D9 amendment turned it. The body-facing drift checks — new orphans,
inline redefinitions, placement crossings — remain Phase 10 work and arrive
with the bodies.

The gates are separate and none runs another; chaining them in
one process would collapse independent verdicts into one exit code. Order
does not matter — they share no state and `--check` never writes. None
subsumes another: records can be individually sound while the committed
graph is stale, and a byte-identical graph says nothing about whether a
definition still matches its source paragraph.

`validate` and `lift` need `pandoc`, because `para_hash` is *defined* as a
hash of pandoc's plain-text rendering — its version is part of the provenance
contract, so the workflow echoes it. `graph --check` reads YAML only and needs
no pandoc.

The workflow is pass/fail only. Posting findings as PR comments is Phase 10
work; the guard should not wait on it, because an unenforced "fails CI" is a
claim that quietly stops being true.

## Owner

Nick Van Maele (Vonk.ca)
