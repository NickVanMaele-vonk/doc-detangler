# ADR-004 — Iterative re-run operation and the assurance model

**Status: Decisions 1, 2, 2b, 3 and 9 RULED** by Nick, 2026-08-07. Decisions
4–8 are **PROPOSED** — each carries a recommendation and each can be ruled
independently. Decisions 2/2b and 9 are built; 1 and 3 are rulings whose
normative-document edits are partly outstanding (build step 3). Decisions 2
and 9 amend signed-off material and say so explicitly.

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

**Recommendation:** a `param-max-definitions-per-approval`, set from the first
real drafting round rather than guessed now, following the precedent that
unset parameters are absent from `detangle.toml` rather than defaulted.

## Decision 5 — campaign mode is repeatable

D10 element 1's two modes become three: the **initial campaign**, the
**re-run** (a campaign over already-structured input), and the **steady-state
guard** between them. The re-run is not the initial campaign repeated — its
input carries markers, section IDs and record-anchored definitions that the
first run's input did not.

**Recommendation: adopt**, amending D10 element 1. The alternative — declaring
re-runs out of scope and requiring all evolution to happen through incremental
editing — contradicts the stated operating cycle and is not recommended.

## Decision 6 — a re-run is a freeze window

`restructure/plan.py` pins each plan to its source blob, comparing against
`git rev-parse HEAD:<doc>` and raising *"source moved; re-verify the plan
against it"*. So any merged markdown PR invalidates every open reorder plan.
That is correct behaviour — a plan addresses blocks by hash — but it means a
re-run and ordinary editing cannot overlap. A re-run also moves every block,
so a concurrent edit conflicts textually with essentially everything.

**Recommendation:** an operating rule, not code — a re-run freezes the
documents it touches — plus a plan-staleness message that says so rather than
only reporting the mismatch. This will bite on the first cycle.

## Decision 7 — verification cadence follows the re-run, not the release tag

`param-full-verify-cadence` is "every release tag" and 10.6 puts the full
C1/C2/C7 harness there. Nick expects to forget tags, and a forgotten tag means
the Phase 7 harness never runs — the per-PR drift lint still catches deletions
through its `lost-claim` check, so the failure is not silent, but the
losslessness proof would simply not be produced.

**Recommendation:** cadence the full harness on **the re-run**, which is a
deliberate act nobody forgets and precisely the moment the proof is wanted.
Release tags remain a valid additional trigger.

## Decision 8 — wording goes in the markdown, position goes in the plan

Findings fixed by typing into the markdown split in two, and only one kind
survives a re-run. **Wording fixes survive**: `restructure` moves blocks
verbatim. **Position fixes do not**: the plan governs placement, so a
definition moved by hand is moved back on the next run. The failure is silent,
which is the worst way for it to fail.

**Recommendation:** state the rule in the DoD, and consider a lint that
detects a block whose position in the source contradicts the plan and says
which of the two to edit.

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
   because it is the only one needing new code.

**Not in scope here.** The drift lint that would accept a hand-typed
definition into a record does not exist, so today a definition typed into
`glossary.md` is mirrored nowhere and `detangle generate` would overwrite it.
That gap is real and is tracked against Phase 10.2, not this ADR.
