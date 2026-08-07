# ADR-004 — Iterative re-run operation and the assurance model

**Status: every decision RULED** by Nick, 2026-08-07 — 1, 2, 2b, 3, 4, 5, 6, 7,
8 and 9. Decisions 2/2b, 4, 5, 6, 7, 8 and 9 are applied; 1 and 3 are rulings
whose normative-document edits are partly outstanding (step 3). Decisions 2, 5
and 9 amend signed-off material and say so explicitly; Decision 7 sets a
parameter that was only ever a proposal; Decision 8 is the only one that
needed new code.

## Context

D10 element 1 ships two operating modes: the **detangle run** (Phases 5–9), a
one-time campaign, and the **steady-state guard** (Phase 10), a permanent
incremental check on every docs PR. Nick's actual operating cycle, stated
2026-08-07, is neither:

```
v1.0  three tangled source documents + two or three reference documents
  │
  ├─ run tool ───────────────────────► v1.1 output + findings
  │
  ├─ fix findings: (a) type into the markdown → a later version still,
  │                (b) edit yaml and registers   possibly with no release tag
  │
  ├─ re-run on all three (+ references) ────► a new version
  │        …the cycle repeats a few times
  │
  ├─ occasionally: run on only one or two source documents
  │
  └─ concurrently: other users edit the markdown directly, each via a PR
```

The campaign is **repeated**, human editing is **interleaved**, and the
tool's input on run N+1 is its own output from run N.

**Much of this already fits.** Output becoming the living set was ruled
2026-07-31 (`samples/` is scaffolding). "The new location becomes *the*
location" is C9/C10 plus the D9 amendment. Reference documents supplying
definitions is the two-input-sets ruling of 2026-08-05, config-driven.
Forgetting a release tag costs nothing for identity — hand-typed versions were
already removed in favour of git plus the generated `manifest.yaml`. Partial
runs do not corrupt placement, because `restructure` already works one
document per plan and C9 reads `used_in` from the records rather than from
whichever documents a run touched.

**Four things break, and one existing rationale is wrong.** They are the
decisions below.

### Measured, not assumed

Three facts were established against the code before drafting, because each
would have changed a decision:

- **`para_hash` is marker-insensitive.** Blocks are split on blank lines and
  normalised through `pandoc -f markdown -t plain --wrap=none`, whose plain
  writer drops raw HTML. `<!-- sec:… -->\n## Overview` and `## Overview` hash
  identically, as do a `concept:`-wrapped definition and its bare prose. So
  feeding a marked document back in as source yields the same block hashes as
  the unmarked equivalent, and markers can never pollute provenance.
- **Token parity is marker-*sensitive*.** `restructure/tokens.py` splits on
  whitespace, so `<!--`, `sec:u-a1`, `[AI` and `addition]` are all counted as
  word tokens. The two mechanisms therefore disagree about whether a marker is
  content — Decision 9.
- **Markers are emitted, never carried through.** `restructure/execute.py`
  writes `concept:` markers from the record (l. 274–275), `sec:` markers from
  the plan (l. 364) and the `AI addition` wrapper from the plan's Category C
  designation (l. 376–378). Ordinary content blocks are copied verbatim,
  markers included. A re-run over marked input therefore re-emits fresh
  markers beside copied ones.

## Decision 1 — assurance replaces anchoring as the strength axis

**RULED by Nick, 2026-08-07.** Text a human writes at v1.2 has the same
definitional strength as text a human wrote at v1.0. Human authorship is the
highest confidence level, independent of version. The distinction that matters
is *did AI write this* versus *did a human write this*, and **AI-drafted text
that a named human verified and approved is equivalent to human-written**.

This replaces **anchoring** (was this in the input?) with **assurance** (who
vouches for it?) as the axis carrying definitional strength.

The existing rule it overturns is criterion 7's: authored text never acquires
a `para_hash`, "because a `para_hash` asserts *the business wrote this wording
at this revision*, which for authored text is false." For a definition Nick
writes himself that premise is simply false — he is the business, and he wrote
it. The rule gave the right answer for AI drafts and the wrong reason for
everything else.

**The project's own record supports the ruling.** Plan §3 Scope states that
every document in `samples/` "was created the same way — drafted with AI
assistance, and **not closely reviewed** by its human author", and criterion 7
already draws half the consequence: "the source corpus was itself AI-assisted,
so the bar would have been higher for the fix than it ever was for the
original." Carried through, today's model trusts the *weaker* artifact more —
v1.0 is unreviewed AI output, while a definition written and approved at v1.2
is reviewed human output. For most of the set this ruling is a tightening, not
a loosening.

Amends C2, criterion 7, and the provenance notes under §D9 and §D10 element 4.

## Decision 2 — split lineage from strength

**RULED by Nick, 2026-08-07, and built.** See Decision 2b for the levels the
two axes attach at.

One thing from the old model must survive in a new form, or C2 becomes
vacuous. In this cycle run N+1's input is run N's output, so if nothing
distinguishes text that entered at v1.2 from text present at v1.0, the
fabrication check traces every claim successfully — including anything
invented — because by then it genuinely is in the input. The check would pass
by construction from generation 2 onward and prove nothing.

The cause is one field carrying two claims: today the *absence* of `para_hash`
encodes both "not in the original" and "not trustworthy". Decision 1 denies
the second. So separate them:

- **`para_hash` + span → lineage.** Authored text *does* get a real span, into
  the version where it entered, with that version recorded. Honest and
  traceable; re-anchoring becomes routine rather than forbidden.
- **`assurance` → strength.** Named author, named approver, PR, and the set
  version it entered at. `human-approved` is the top level and does not decay
  with version.
- **`flags: [orphan]` → input diagnostic only.** It stays, and it means "the
  detangle set never defined this". It never means "this definition is weak",
  and nothing may read it as a quality signal.

**Ruled: adopt.** It closes open question 5 of 2026-07-31 (provenance schema
shape).

## Decision 2b — the two axes attach at different levels

Decision 2 says *split*; it does not say where each half lives. A record has
one definition but usually several citations — 99 of the 172 defined records
cite more than one span — so a definition can end up assembled from original
v1.0 wording plus a sentence typed at v1.2, with one approval covering both.
Three shapes were possible: one trust block per record; a stamp on every
citation, with the record's level derived as the weakest; or split by what
each thing actually is.

**RULED by Nick, 2026-08-07: split by what each thing is.**

- **Assurance is per record**, because approval is one human act covering the
  definition as a whole. Repeating it per citation would duplicate one fact
  across five lines and invite the copies to drift.
- **Lineage is per span**, because where wording came from genuinely varies
  citation by citation. A per-record lineage label would have to describe the
  weakest citation, and honesty about mixed origins is what the split is for.

Neither half has to lie, which the record-level-only shape could not manage.
A consequence worth naming: a citation into text the *tool* wrote becomes
legal and clearly labelled rather than a rule violation, which is what
unblocks provenance after run 1.

**As built.** `origin: corpus | authored` on every span; an `assurance` block
of `author` / `approved_by` / `pr` on every record, `null` exactly when
`definition` is `null`. All 359 records migrated: 597 spans `corpus`, 172
assurance blocks, 187 nulls. `author: assistant` reflects step 3.3's assembly
under C2; `approved_by` and `pr` start `null` because every record on `main`
is `status: candidate` — the gap is left visible rather than assumed away, and
`assurance-unapproved` refuses `approved`/`published` without a named human.
Whether a definition is human-approved is computed from `approved_by`, never
stored, following the rule that keeps `placement` computed.

## Decision 3 — no marking for approved additions

**RULED by Nick, 2026-08-07.** Approved additions carry no in-document marker.
The history of additions is recoverable by git version comparison, so a marker
duplicates it, and under Decision 1 approved text is equivalent to
human-written and should read as ordinary document text. **Unreviewed AI text
is unaffected and stays marked.**

Three consequences land with it:

- **It amends C5** ("bridging/explanatory additions … must be visually and
  mechanically distinguishable from source-derived text"). C5 is signed off,
  so this is recorded as an amendment with its rationale rather than a
  reinterpretation.
- **It shrinks criterion 7's ladder.** With approved additions unmarked and
  traceable by span (Decision 2), C2's second limb — explicitly-marked
  bridging text — has exactly one remaining user: unreviewed AI text.
  Category A/B/C survives as the *reporting* vocabulary of the 8f self-report;
  it stops being an in-document marking scheme for approved content.
- **It re-measures `param-overview-max-words`.** The 2026-08-05 ruling counted
  the `U` overview at 227 words *because* the visible `[AI addition]` tag is
  ink on the page. With no tag the same overview measures 206. The principle
  is unchanged and still correct; the figure moves because the ink is gone.

**Scope.** The ruling covers *additions*. The approved-omission marker
`<!-- omitted src=… approved-by=… pr=… -->` is not an addition and is not
covered: git shows that a claim was deleted but not that its removal was
approved, and criterion 4 must tell those apart. It stays unless ruled
otherwise.

## Decision 4 — approval granularity

Under Decision 1 assurance carries all the weight, so approval must be a real
act. If 187 undefined terms receive AI-drafted definitions bulk-approved in
one PR, the assurance claim is worthless and the model launders AI text
through a rubber stamp.

Criterion 7 already has the mechanism — a draft "shows its evidence, the
usages elsewhere in the corpus it was assembled from, or states explicitly
that there are none", because "a definition assembled from six real usages is
a different object from one composed out of background knowledge". Decision 1
promotes that from advisory to load-bearing.

**RULED by Nick, 2026-08-07, and built: `param-max-definitions-per-approval`
= 50, set now.** The recommendation was to declare the parameter and leave the
number to the first real drafting round, following the precedent that unset
parameters are absent from `detangle.toml` rather than defaulted. Nick set it
immediately instead, so the cap protects the first batch rather than the
second — the first bulk drafting round is the one most likely to be large, and
a cap that arrives after it has run has missed its moment. 50 sits between the
25-comment review budget and the 200-term change budget, the two figures that
already bound a reviewable PR from either side.

**As built.** `approval-batch` in `detangle validate` groups defined records by
`assurance.pr` and reports any group over the cap. `pr: null` is not a batch —
it means nobody has approved yet, which is where all 359 records sit today, so
the check fires on nothing until approvals start. It is set-wide by
construction: a narrowed run would see part of a batch and under-count it.

## Decision 5 — campaign mode is repeatable

D10 element 1's two modes become three: the **initial campaign**, the
**re-run** (a campaign over already-structured input), and the **steady-state
guard** between them. The re-run is not the initial campaign repeated — its
input carries markers, section IDs and record-anchored definitions that the
first run's input did not.

**RULED by Nick, 2026-08-07: adopt**, amending D10 element 1. The alternative
— declaring re-runs out of scope and requiring all evolution to happen through
incremental editing — contradicts the stated operating cycle and would make the
tool a one-shot instrument whose every later improvement had to be done by
hand.

**Recorded in:** research-memo §D10 element 1 (rewritten as three modes, with
the reason the re-run is not the campaign repeated), plan §1 and the 4.2a row.
Two rules already attach to the new mode — Decision 9's marker exclusion and
Decision 6's freeze window — which is the point of naming it: without it, each
would have been found in production looking like a defect.

## Decision 6 — a re-run is a freeze window

`restructure/plan.py` pins each plan to its source blob, comparing against
`git rev-parse HEAD:<doc>` and raising *"source moved; re-verify the plan
against it"*. So any merged markdown PR invalidates every open reorder plan.
That is correct behaviour — a plan addresses blocks by hash — but it means a
re-run and ordinary editing cannot overlap. A re-run also moves every block,
so a concurrent edit conflicts textually with essentially everything.

**RULED by Nick, 2026-08-07: an operating rule, not code** — a re-run freezes
the documents it touches — plus a plan-staleness message that says so rather
than only reporting the mismatch.

Automatic plan rebasing (re-resolving block hashes against the moved source)
was considered and put on the backlog rather than built. It would remove the
coordination cost, but it has a case with no correct answer: where the edit
*changed* a block rather than moving it, the plan's intent for that block may
no longer make sense, so rebasing would need to fall back to this rule anyway.
Building it before the constraint has actually been felt risks solving the
imagined version of the problem.

**The rule.** While a re-run is in flight, the documents it touches take no
other merges. It is a deliberate act of bounded duration, so freezing three
files for it is ordinary scheduling — and the alternative is not "concurrent
editing works" but "the plan silently addresses text that has moved".

**As built.** `plan-blob-stale` now names the likely cause and the rule. The
finding stays a warning, mirroring `git-blob-stale`: a moved source means
re-verify, not that the plan is wrong.

## Decision 7 — verification cadence follows the re-run, not the release tag

**RULED by Nick, 2026-08-07: cadence the full harness on the re-run, and the
run records the versions it verified.**

`param-full-verify-cadence` was "every release tag" and 10.6 puts the full
C1/C2/C7 harness there. Nick expects to forget tags, and a forgotten tag means
the Phase 7 harness never runs — the per-PR drift lint still catches deletions
through its `lost-claim` check, so the failure is not silent, but the
losslessness proof would simply not be produced.

The recommendation was to cadence the full harness on **the re-run**, which is
a deliberate act nobody forgets and precisely the moment the proof is wanted,
with release tags remaining a valid additional trigger. The value was a
*proposal*, so setting it overturns nothing.

### The condition attached to the ruling

Nick's question — *if the heavy run happens only occasionally, how are the
document versions at the time of the last run identified?* — is the one that
decides whether this cadence produces anything durable. Without an answer,
"verified at the last re-run" is a claim with nothing behind it.

The answer is cheap, because git already solves it. A document's version **is**
its blob hash (`git rev-parse HEAD:<doc>`): immutable, and `git show <blob>`
returns the exact bytes however many versions land afterwards. So the set as it
stood is five 40-character strings plus a commit. Nothing needs archiving, and
the repo already uses this pin in three places — record spans
(`verified_against.git_blob`), a reorder plan's `pinned_blob` with its
`plan-blob-stale` warning, and the generated move-map's source header.

So the ruling carries a requirement: **every full run writes the blob of every
document in both input sets, plus the commit, into its report** (plan step
7.5). Two things follow that otherwise cannot — the proof names the artifacts
it proves, and the next run has a baseline: v_n+1 is checked against v_n, and
v_n is retrievable. That last point also answers the coverage-baseline question
ADR-003 Decision 2 leaves open for steady state.

`manifest.yaml` (D10 element 5, step 10.4) is the set-level version of the same
record and absorbs it when it lands. It is Phase 10 and the harness is Phase 7,
which is why the record starts in the verification report rather than waiting
three phases for its designed home.

Durability caveat, stated once so it is not rediscovered: a blob stays
retrievable while it is reachable from a ref. Document history lives on `main`,
which `protect-main` guards with `non_fast_forward`, so a force-push cannot
orphan past blobs. A history rewrite is the only thing that would break this,
and it is already forbidden.

### Why option C — the full harness on every PR — was rejected

Considered and declined, but not on the ground it first appears. The model
never reads a document: 7.1 decomposition and 7.4 structure are deterministic,
and 7.2/7.3 match deterministically first and score only the residue —
**268 of 289 claims on the golden resolve at confidence 1.0**, because
restructuring moves blocks verbatim. A full run scores ~21 claims, not 289.
Per PR, scoped by the section map, it would be single digits.

It was declined for three other reasons:

1. **Its cheap half is already the plan.** Step 10.2 runs per PR and already
   carries the `lost-claim` check — that is deterministic stage-1 coverage. The
   93% that resolves by hash is *already* verified on every edit. What C adds is
   the scored residue, which is exactly the fraction that needs a human.
2. **The checks are judgment-shaped.** All four of `verify`'s checks are
   waivable by design, each being "a finding awaiting human disposition, not a
   drift". A low-confidence mapping means *someone should look*, not *this is
   wrong*; blocking merge on it converts a review prompt into a hard stop.
3. **It puts `torch` on a required gate.** ADR-003 Decision 3 asks for
   `detangle[verify]` as an *extras* group precisely to leave the core package
   and the three CI gates untouched. A checkpoint-fetch failure would turn a
   required check red for a reason unrelated to the change — the
   unsatisfiable-gate trap that stuck PR #81.

Two prerequisites are also unbuilt: `state/section-map.yaml`, without which
nothing can scope a PR at section granularity (git diff cannot substitute — D10
rules line numbers out as provenance anywhere), and a persisted claim→location
index, which incremental *coverage* needs because "is every source claim
present somewhere" is a global question a per-section scope cannot answer.

**As ruled.** `detangle.toml` and the rubric's parameter row now read "every
re-run; release tags additionally", set rather than proposed; criterion 4 and
criterion 9's tiered-cadence bullet carry the version-record requirement; plan
steps 7.5 and 10.6 carry it as work. No code changed — `detangle verify` does
not exist yet, and this is its specification.

## Decision 8 — wording goes in the markdown, position goes in the plan

**RULED by Nick, 2026-08-07, and built: state the rule, detect the collision,
and propose the plan amendment that would ratify it.**

Findings fixed by typing into the markdown split in two, and only one kind
survives a re-run. **Wording fixes survive**: `restructure` moves blocks
verbatim. **Position fixes do not**: the plan governs placement, so a
definition moved by hand is moved back on the next run. The failure is silent,
which is the worst way for it to fail — you meet the same problem again three
versions later.

### What "the plan" is, and what it is authoritative over

Nick asked how a reorder plan could be more authoritative than the document
itself. It is not, and the original framing here was wrong.

First, a naming collision this project created: **`plan/`** is the directory
of normative documents, while **a reorder plan** is `eval/golden/uce.plan.yaml`.
This decision is about the second.

A reorder plan contains **no document text**. It is 237 lines for a
3,473-word document: a list of section headings, and one line per source
block saying which section it lands in, addressed by `para_hash`. Every word
stays in the document.

So the two files hold different facts rather than rival copies of one. The
**document is authoritative about every word**, and that is enforced, not
merely intended: criterion 5's token parity compares the word multiset in
against the word multiset out, both directions, and the run refuses to write
a document that fails. A plan is *structurally incapable* of changing a word.
The **plan is authoritative about order**, and only while a run executes —
between runs it is not read, not consulted, and guards nothing; the drift
lint guards the document.

Nor does a re-run override a hand-move. The run reads your document and gets
your block with your words; it places it where the plan says. Nothing is
overridden — the *placement instruction* simply came from a file you did not
edit. Which reframes the whole problem: **moving a paragraph by hand is
editing the order through the surface that owns the wording.**

### The ruling: detect, and propose

Three options were put. **A** — write the rule down and stop — relies on
remembering, against a failure you cannot see. **C as first drafted** — let
the document win — was wrong, and would make the plan non-authoritative,
which is the foundation ADR-002 rests on; two people moving the same block in
opposite directions would have no resolution.

Nick ruled the third shape, **C′**, which follows the project's own existing
pattern: when a body edit implies a new `depends_on` edge, the tool
**proposes** the change and waits, because an edge is a claim. A hand-moved
block is the same shape — a placement is a claim. So the run reports the
disagreement and emits the plan line that would ratify it; a human merges it
or does not. Strictly better than the bare lint of option B, which detects and
then makes you hand-write the fix, for the same detection cost.

**As built.** `src/detangle/restructure/position.py`, wired into
`cmd_restructure` and into the 8f report:

- `plan-position-conflict`, a **warning**, one per drifted block, carrying
  the paste-ready assignment line and pointing at the assignment index to
  replace. Deliberately not named `…-drift`: every member of
  `registers.NOT_WAIVABLE` is an `<artifact>-drift`/`-missing` pair for a
  hand-edited derived file, and this is the opposite kind of thing — leaving
  the plan to stand is a real disposition, so it is waivable.
- **Silent on unstructured input.** Run 1 reorders nearly every block by
  design, so "source order disagrees with the plan" is true almost everywhere
  and means nothing. The check reads each block's *current* section from the
  `<!-- sec:… -->` marker a previous run stamped; with no markers there is no
  prior placement to contradict. Head-section blocks precede any marker and
  are attributed to the plan's `kind: head` section.
- **A repeated block needs every copy misplaced.** Identical blocks exist —
  the four bare-rule blocks are the live example — so a hash maps to the set
  of sections it sits under, and one correctly-placed copy clears it.
- **It is an 8f cluster**, so the 8c comment budget counts it. A comment the
  tool cannot see is one it would count wrong (Nick, 2026-08-05).

One limit, recorded because the tool must not pretend otherwise: a hand-move
and an ordinary reorder are indistinguishable here. It reports *what*
disagrees and what the plan line would be; it never claims to know why.

**Behaviour-preserving on everything that exists today.** The real `U` source
carries no `sec:` markers, so the real run is byte-identical to `main`'s —
document and all three report artifacts — and still reports 9 clusters,
`unexplained: 0`.

## Decision 9 — token parity ignores markers

**RULED by Nick, 2026-08-07, and built.**

`para_hash` treats a marker as metadata; token parity treats it as content
(both measured above). The disagreement bites in exactly this cycle: once
v1.1 is the input to run 2, its markers are *source tokens*, so criterion 5
requires the output to reproduce them — while the tool re-emits its own
markers from the plan and records, as authored parts the parity check never
counts. The result would be a wall of findings about hidden comments, none of
them about lost wording.

**Ruled:** HTML comments are removed before tokens are counted, so a marker is
metadata under both measures. The alternative — requiring re-runs to preserve
marker identity exactly — makes criterion 5 fail on a marker rename, which
measures the wrong thing.

**One narrowing from the recommendation as first written.** It proposed
stripping the visible `[AI addition]` tag as well, on the ground that this
aligns parity with the `para_hash` normalisation. It does not: pandoc's plain
writer drops *raw HTML*, not visible text, so the tag is content under
`para_hash` and stripping it would create a fresh disagreement rather than
close one. The 2026-08-05 "ink on the page counts" ruling says the same. So
only the comment goes; visible text still counts. Decision 3 removes the tag
from approved additions anyway, which leaves unreviewed AI text as its only
remaining user.

Amends criterion 5's verification method, where the exclusion is recorded.

## Consequences

Build steps, in order, each its own PR. Nothing starts before its decision is
ruled.

1. ~~**Decision 9** — strip markers in `tokens.py`, with tests over a marked
   and unmarked copy of the same block.~~ **Done 2026-08-07.** `COMMENT` in
   `restructure/tokens.py`, nine tests in `tests/test_restructure_tokens.py`,
   eight of which fail without the change. The real `U` plan re-executes
   byte-identically and still reports `unexplained: 0`, so the golden is
   untouched.
2. ~~**Decision 2** — the record schema: `assurance` block, version-stamped
   spans, `orphan` re-scoped in `concepts/README.md`. Migration across 359
   records, `detangle validate` extended, the rubric and §D9/§D10 amended.~~
   **Done 2026-08-07.** `SPAN_ORIGINS` / `ASSURANCE_FIELDS` in `records/load.py`,
   `check_assurance` and the `span-origin` check in `records/checks.py`, 14
   tests, all 359 records migrated, `concepts/README.md` and §D9's provenance
   note rewritten. Terms changed: 0 — a citation added to an unchanged
   definition is not a term change (rubric §8b), which is why one PR is within
   `param-max-terms-changed-per-PR`.
3. **Decisions 1 and 3 in the normative documents** — C2, C5, criterion 7, and
   the `param-overview-max-words` re-measurement (227 → 206 for the `U`
   golden). Documentation only; no code.
4. **Decisions 5–8** — repeatable campaign mode, the freeze-window rule, the
   cadence change, and the wording/position rule, with the position lint last
   because it is the only one needing new code. Decision 5 done 2026-08-07
   (D10 element 1 rewritten as three modes); Decision 6 done the same day
   (`plan-blob-stale` names the rule, backlog B-8 records why plan rebasing
   was not built); **Decision 7 done the same day** —
   `param-full-verify-cadence` set in `detangle.toml` and the rubric, plan
   step 7.5 added for the run version record, 10.6 and criterion 4 updated,
   ADR-003 Decision 5 annotated where it awaited this parameter.
   Documentation only; the harness it specifies is Phase 7. **Decision 8 done
   the same day** — `restructure/position.py`, `plan-position-conflict` wired
   into the command and into the 8f cluster list, 13 tests, the rule written
   into criterion 9 and the README. Behaviour-preserving: the real `U` run is
   byte-identical to its predecessor, document and report both, because the
   check is silent on unstructured input.

Decision 4 was built alongside step 2, since `approval-batch` reads the
`assurance.pr` that step introduced.

**Not in scope here.** The drift lint that would accept a hand-typed
definition into a record does not exist, so today a definition typed into
`glossary.md` is mirrored nowhere and `detangle generate` would overwrite it.
That gap is real and is tracked against Phase 10.2, not this ADR.
