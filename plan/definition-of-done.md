# Definition of Done — Restructured Documents

**Status:** **Approved** by Nick, 2026-07-21 (v3). **v4, 2026-07-23:**
criterion 9 (continuous-change coherence) and its supporting scope,
parameter, and criteria amendments added per decision D10, at Nick's
direction; new parameter values remain proposals until set.
**Phase:** 1.1 — complete; extended by D10
**Last updated:** 2026-08-05 — three changes this day: (3) the 5.3
review-load baseline (`eval/review-load.md`) set `param-max-comments-per-PR`
(25) and `param-low-confidence-threshold` (0.80 provisional, re-baseline at
6.2), and confirmed `param-max-terms-changed-per-PR` (200). Earlier: (1)
`param-max-terms-changed-per-PR` raised from 25 to 200 (Nick); (2) **two
input sets** (Nick) — the detangle set and the read-only reference set are
defined in Scope, the placement count and orphan measure are scoped to the
detangle set, definitions found only in a reference document are lifted as
Category B with provenance, and "Modify a reference document" joins the
non-goals. Criteria 3, 4, 5 and 7 amended accordingly.

A restructured document is "done" when it satisfies all nine criteria below,
subject to the phase-dependent applicability rules in
[Interim done by phase](#interim-done-by-phase).

---

## Scope and applicability

- **The output set is five documents.** The detangle set (three documents
  today); a glossary which is created based on them and ranks as the first
  document of the set; and an index. Both the glossary and the index are
  reader-facing deliverables, not tool artifacts.
- **The input is two sets** (Nick, 2026-08-05). The **detangle set** is the
  documents being restructured; only its documents produce output documents,
  and everything in this rubric that quantifies over "the source" quantifies
  over it — placement counts, orphan measurement, omission checking,
  verbatim-token diffing. The **reference set** is additional read-only
  documents supplying definitions and context (today the full Analytical
  Layer blueprint `(A)` and the BC-17 prototype spec `(P)`; over time the
  smaller side documents business users write). Reference documents are
  never modified and their claims are never required in the output — but a
  definition found only in a reference document is **lifted as the
  definition**, with a provenance span into the reference file, and the term
  keeps its used-but-never-defined-here flag (see criteria 3 and 7). Both
  sets are declared in `detangle.toml [documents]`.
- **Reading order of the set:**
  `glossary.md` → Document 1 (UCE) → Document 2 (SBSP) → Document 3 (MCL).
  A term is "already defined" at any point after its definition site in this
  order.
- **`index.md` is outside the reading order.** It is a back-of-book index:
  an alphabetical list of every term across the other four documents, each
  with the location of its definition. It is consulted at any point, never
  read through, and it defines nothing — so it neither satisfies nor
  violates concept-before-use, and it is exempt from criterion 1. Placing it
  in the reading order would put a bare term list in front of a reader who
  has not yet met a single concept.
- **Where a term is defined — the single-definition rule:**
  - a term used in **more than one detangle-set document** is defined in
    `glossary.md`, and **only** there — reference documents never count
    toward the tally (2026-08-05);
  - a term used in **exactly one detangle-set document** is defined in that document, at
    or before its first use — **unless a glossary definition depends on it**,
    in which case it is defined in `glossary.md` too (Case 3, 2026-08-03);
  - no term is defined in two places.
- **Where a definition is canonical — the definition site owns it** (Nick,
  2026-08-04, amending D9). Every definition is canonical **in the document
  that defines it**, `glossary.md` included: it is the fourth editable
  document of the set, not a generated view. The concept record carries a
  derived copy, regenerated from the document and byte-compared, and
  hand-editing that copy fails CI with a pointer to the section. All 172
  defined terms work this way — 78 in the glossary, 94 across the three
  documents — so there is no exception to remember. A definition **lifted
  from a reference document** (2026-08-05) is no exception either: once
  lifted, its output-set definition site owns it like any other, and the
  span into the reference file is historical provenance — it records where
  the wording came from at lift time, per the standing principle that corpus
  provenance is a fact, not a status. If the reference document later
  changes, the recorded blob goes stale and the lift is re-verified; the
  reference file itself is never stamped with markers, so its spans stay on
  heading-path + hash anchoring.

  The record still owns the **ontology**: identity (`id`, `term`, `aliases`),
  `placement`, `used_in`, `source` provenance, `depends_on`, `flags`,
  `conflict`, `review`, `notes`. Only the definition prose moves.

  Each document delimits the definitions it owns with generated
  `<!-- concept:<id>:start -->` / `<!-- concept:<id>:end -->` markers, which
  is what keeps the lift into the record deterministic — without them the
  structural guarantees would rest on re-parsing prose, the failure D9 exists
  to prevent. Markers are stamped by the tool, never written by an author.

  Prospective: the direction flips per document as each comes to exist, and
  for the glossary when the drift lint that guards it exists. Until then every
  definition lives in its record and the committed `glossary.md` is the seed.
- **The glossary is subject to this rubric.** As the first document of the
  set it must satisfy all eight content criteria (1–8) itself, with the
  modifications noted per criterion; criterion 9 applies to the set's
  evolution, not to any single document.
- **The index is generated, and is held to a reduced subset.** It is derived
  mechanically from the other four documents and is never hand-edited, so it
  is exempt from criteria 1, 4, and 7 and subject to 2 (a lead sentence
  only), 3, 6, and 8. See "The index" under criterion 3.
- **Unit of assessment:** the output set. Criteria are evaluated set-wide;
  per-file evaluation is not meaningful once definitions relocate across
  files.
- **Source version binding:** every restructured document records the exact
  source version it was derived from (e.g. `source: blueprint-MCL v21`).
  `glossary.md` records the version of every source it draws on — reference
  documents included (2026-08-05): a lifted definition binds the reference
  blob it was verified against, and a change to that blob re-opens
  verification of the definitions lifted from it. When any
  source version changes, every output document depending on it is **not
  done** until re-verified.
- **Set version binding (D10):** a generated `manifest.yaml` binds the whole
  set — per-document version, record-set revision, dependency-graph hash,
  derived-artifact hashes, and the **git blob of every document in the set
  plus the commit** (~~generation timestamp~~, **amended 2026-08-08**). A blob
  *is* the version: the commit and the blobs date the manifest, while a clock
  would make it irreproducible and would break the byte comparison that guards
  every derived artifact — the same reason `concept-graph.yaml` cannot carry
  one, stated under criterion 9's `state/notices.md` note. The version record
  lives in the verification report today (plan step 7.5, ADR-003) because the
  harness is Phase 7 and the manifest is Phase 10; ADR-004 rules that the
  manifest **absorbs** it when it lands, which is what this amendment applies.
  Each concept record carries
  the source version its provenance span was verified against
  (`verified_against`), making version skew machine-checkable.
- **"Done" is a recurring state, not a one-time event (D10).** The set keeps
  evolving after delivery (glossary completed over time; bodies edited and
  reordered by humans and AI agents). The rubric therefore applies in two
  modes: in full to detangle-run output, and incrementally — via the
  steady-state drift lint (criterion 9) — to every ordinary docs PR
  afterwards.
- **What is assessed:** the output set plus its run artifacts (verification
  report, move-map) — not the diff alone.

## Parameters

Values below are proposals unless marked **set**. They are collected here so
the rubric can be signed off without silently pre-committing to numbers.

| Parameter | Value | Note |
|-----------|-------|------|
| `param-max-terms-changed-per-PR` | **200** (set) | Maximum terms a single PR may change. See 8b. **Raised from 25 to 200 on 2026-08-05** (Nick): the from-scratch build changes terms in far larger batches than steady state — the golden output for `U` alone is in scope for 155 terms — and a cap sized for steady-state edits would split that into seven PRs whose intermediate states leave terms defined twice or not at all, which 8b itself calls a failure. **Confirmed by the 5.3 baseline** (`eval/review-load.md`): 35 measured for the `U` golden; the glossary at 155 is the largest unit the build needs. |
| `param-max-definitions-per-approval` | **50** (set) | Maximum definitions one approval may cover — how many records may share an `assurance.pr`. **Set 2026-08-07** (Nick), with ADR-004 Decision 4. Under Decision 1 assurance carries all the definitional strength, so approval has to be a real act: 187 drafted definitions bulk-approved in one PR would launder AI text through a rubber stamp. Nick set the number now rather than waiting for the first drafting round, so the cap protects the very first batch. It sits between the 25-comment review budget and the 200-term change budget, the two figures that bound a reviewable PR from either side. Enforced by `approval-batch` in `detangle validate`. |
| `param-max-comments-per-PR` | **25** (set) | Maximum blocking PR comments; a run producing more does not open a PR — it fails and reports (8c). **Set 2026-08-05 from the 5.3 baseline** (`eval/review-load.md`): the `U` golden produced 9 aggregated clusters for a whole-document restructure, and the term cap forces PRs to roughly per-document scope, so 25 gives every real run 2.5–3× headroom. |
| `param-overview-max-words` | 400 | Maximum length of the required opening overview. **What counts, ruled 2026-08-05** (Nick): every word the reader meets in the section, including the visible `[AI addition]` marker that opens an authored one — ink on the page counts toward how long a text is, even when the tool wrote it. Raised at step 6.2, where the `U` golden's hand count of 214 reproduced as neither the prose alone (206) nor the whole section (227). **The principle is unchanged by ADR-004 Decision 3 as amended (2026-08-08); the figure moves with the state.** An approved addition has no visible tag, so its overview loses the blockquote's 21 words and the same `U` text measures 206. The golden stays at **227**: it renders unapproved tool output, and a renderer cannot know approval state. |
| `param-claim-granularity` | one claim per source sentence; one claim per table cell carrying an independent assertion | Governs criterion 4. |
| `param-false-positive-tolerance` | none | Every flag needs a disposition, but "false positive" is a valid disposition. |
| `param-manual-reviewer` | Nick, optionally Ivo for domain accuracy | Adjudicator for the manual criteria. |
| `param-low-confidence-threshold` | **0.80** (set, provisional — re-baseline at 6.2) | This dial, and contradiction frequency, are the only unbounded contributors to comment volume. **Set 2026-08-05 from the 5.3 baseline**, with the caveat stated there: the hand-produced golden yields the low-confidence *rate* (2 of 289 claims, both source damage), not a machine confidence distribution, so 0.80 on the Phase 7 [0, 1] mapping-confidence scale is provisional by construction and **must be re-baselined at step 6.2** against the prototype's first real distribution. |
| `param-glossary-order` | **topological** (set) | `glossary.md` is ordered by topological sort throughout. Alphabetical lookup lives in `index.md`, not in the glossary. |
| `param-full-verify-cadence` | **every re-run; release tags additionally** (set) | How often the full C1/C2/C7 harness runs in steady state (the per-PR drift lint always runs). **Set 2026-08-07, ADR-004 Decision 7**, replacing the "every release tag" proposal: a re-run is a deliberate act nobody forgets, and it is precisely the moment the losslessness proof is wanted. Tags remain a valid additional trigger, so nothing that ran before still runs less often. **The run must record the versions it verified** — the git blob of every document in both input sets, plus the commit — or "verified at the last re-run" is a claim with nothing behind it; that record is also the baseline the *next* run compares against (see criterion 4). |

---

## 1. Concept-before-use

For every domain term X, the definition of X appears before the first use of
X, in the reading order of the set.

- **Formal check:** for each edge `X depends-on Y` in `concept-graph.yaml`,
  `position(definition of Y) < position(first use of X)`, where position is
  taken over the concatenated reading order `glossary.md` → Doc 1 → Doc 2 →
  Doc 3. The order need only be *consistent with* the graph's partial order;
  it need not equal any particular topological sort.
- **Shared terms** (used in more than one document) are defined in the
  glossary, which precedes all three documents, so their ordering constraint
  against document text is satisfied structurally. The check still has real
  work to do in three places: inside the glossary, inside each document for
  its own local terms, and at every first use (below).
- **First-use citation — per section.** The first use of a glossary-defined
  term **in each section** carries an explicit link to its glossary entry.
  Not once per document: nobody reads documents of this size start to
  finish, and readers arriving mid-document via search or a cross-reference
  would otherwise meet an unexplained term whose only citation sits forty
  pages earlier. Subsequent uses within the same section are not linked —
  that would be link noise.
- **Links point forward only.** Documents link to the glossary; the glossary
  does not link back to the documents. A glossary defines terms, it does not
  record where they are used. Usage locations are derived data and live in
  `concept-graph.yaml`, not in prose (see criterion 6).
- A shared term's definition is **not** restated in the document — that would
  violate the single-definition rule and create two maintenance sites.
- **Ordering inside the glossary:** glossary entries use other domain terms,
  so the glossary has its own concept-before-use problem, and a conventional
  alphabetical glossary is *not* compliant. `param-glossary-order` is
  therefore **topological**: the glossary reads start to finish without ever
  meeting an undefined term. The criterion-1 check runs over the glossary in
  its rendered order.

  Alphabetical lookup is not lost — it moves to `index.md`, which is exempt
  from this criterion. Separating the two orderings is the point of the
  split: one document is optimised for reading, the other for retrieval, and
  neither compromises for the other.

  **The tool holds that order, and says so** (Nick, 2026-08-04). Because the
  glossary is editable, a person will append a new entry at the bottom or
  insert one alphabetically — that is what everyone does with a glossary. A
  PR leaving it out of topological order therefore receives a **reorder
  commit** from the guard, machine-verified to move whole entry blocks and
  change no words, plus a PR comment naming what moved and why. This is the
  stamping-commit pattern of criterion 9 applied to order instead of
  identity, and it is the reason an editable glossary does not decay into an
  unreadable one.
- **Cycles:** a genuine definitional cycle cannot be fixed by reordering.
  A cycle satisfies this criterion when all of the following hold:
  1. the cycle carries a human disposition in the **cycle register**,
     `registers/cycles.yaml` — the canonical home for cycle dispositions,
     which the generator rolls up into `concept-graph.yaml`. The register
     is authored; `concept-graph.yaml` is derived and is never hand-edited
     (C6, ADR-001 §5), so the disposition is read from the register and
     written to the graph, not the reverse;
  2. one member is designated the entry point **in that register entry**
     and defined first, using a forward reference of the form "…see [Term]
     below", marked as bridging text per criterion 7;
  3. the forward reference is listed in the verification report.

  Register entries and live cycles are **1:1**. A cycle in the graph with
  no register entry is a blocking finding — a new circular definition
  awaiting disposition. A register entry with no corresponding cycle is a
  stale ruling: a definition was narrowed and the exception is dead, so it
  is flagged rather than silently dropped. A cycle resolved by narrowing
  (ISO 704 §6.5.2 inner circle) gets no entry at all; its trace is the
  clause moved verbatim to the record's `notes`. `notes` is a **staging post, not a destination** (Nick, 2026-08-04): records are not part of the output set, so a corpus clause left there is an omission under criterion 4. It lands in document prose beside its definition block when Phase 5 writes the body.

  Because shared definitions now sit in one file that precedes the
  documents, cross-document cycles collapse into intra-glossary cycles,
  which are resolvable by reordering the glossary. This is a primary
  motivation for glossary-first.
- **Verification method:** automatic, against `concept-graph.yaml` and
  `registers/cycles.yaml`.
- **Status:** ⏸ Deferred to Phase 3 (the graph does not exist yet).
- **Interim (Phases 1–2):** manual reviewer check, advisory only.

## 2. Abstraction pyramid

The document opens with a plain-language overview before any detail, and each
section moves general → specific.

- **Checklist (all must pass):**
  - The document opens with an overview section stating, in plain language,
    what the document is for and what it contains, in
    ≤ `param-overview-max-words` words.
  - Every section opens with a lead sentence stating that section's purpose,
    before any table, list, or exception.
  - No section depends on a definition introduced only in a later section
    (criterion 1 applied at section granularity).
  - Within a section, definitions and context precede edge cases,
    exceptions, thresholds, and implementation detail.
- **Applied to the glossary:** the glossary opens with an overview of the
  domain — what this body of documentation is about and how the three
  documents relate — before the first entry. A glossary that is only a list
  of entries fails this criterion.
- **Applied to the index:** reduced to a single requirement — a lead
  sentence stating what the index is and how to use it. The index has no
  sections and no exposition, so the rest of the checklist does not apply.
- **Verification method:** the first three items are mechanically checkable
  (presence and length of the overview; presence of a lead sentence per
  section; the criterion-1 check restricted to intra-document edges). The
  fourth is manual/editorial review by `param-manual-reviewer`.
- **Status:** available from Phase 1 (manual); partly automatic from Phase 3.

## 3. Glossary and index completeness

Every domain term used anywhere in the set has exactly one one-sentence
plain-language definition, at the site required by the single-definition
rule — and exactly one index entry pointing at it.

- **What counts as a domain term:** a term whose meaning is specific to the
  MTSAM / Veridict analytical framework or to this domain's usage —
  including all internal codes and acronyms (RT01, RD02, MWBR, QBRS, QBLI,
  QBCCL, RSA, CCO, IBEB, CQS, BOA, …) and all named constructs (Universal
  Core Engine, EscalationReadiness, Marking-the-Close Triad).
- **What does not:** externally defined terms owned by a standards body or
  regulator (MAR, MAR Article 12, ESMA, FSMA, CONSOB, OLO, BTP, …). These go
  in a **references** list pointing at the authoritative source, not in the
  glossary.
- **Placement test:** term usage is counted across the **detangle set** —
  reference documents never count (2026-08-05, generalizing the `(A)` and
  `(P)` rulings of 2026-07-22 / 2026-07-26). Used in
  ≥ 2 documents → glossary. Used in exactly 1 → that document, **unless a
  glossary definition depends on it**, in which case it joins the glossary
  as well (Nick's Case 3 ruling, 2026-08-03). Both limbs are derived
  mechanically — the first from term extraction, the second as the
  dependency closure of the first over `depends_on`, taken to a fixpoint —
  so placement remains a computed property, not a judgement call.

  Limb 2 exists because the glossary is read first. Without it, a glossary
  entry can lean on a term whose definition sits in a document further down
  the reading order, which fails criterion 1's own formal check —
  `position(definition of Y) < position(first use of X)` — in the very
  first document of the set. Limb 1 counts uses across the three component
  blueprints only; the glossary is a fourth place terms get used, and limb 2
  is what counts it.
- **An undefined term still gets a place** (Nick's Case 1 ruling,
  2026-08-03). Having no definition changes nothing about *where* the term
  belongs: the placement test runs on usage and dependency, both of which
  exist whether or not anyone ever wrote a definition. So an undefined term
  is positioned by the same two limbs — in the glossary if it qualifies, in
  its document at or before first use otherwise — and the missing definition
  is **flagged to a human** rather than invented (C2, criterion 7) or
  silently dropped. Dropping it would hide the gap; inventing one is the
  highest-risk output the tool can produce. One narrowing (2026-08-05): if a
  **reference document** defines the term, that definition is lifted with
  its provenance span rather than the gap being flagged as unfillable — the
  term still carries the flag saying the detangle set never defines it, so
  the convolutedness measure is undisturbed (see criterion 7).
- **A definition that sits after its first use is the ordinary case**
  (Case 2, same ruling), not a defect to disposition: reordering the text is
  what the tool is for. Only the two cases above need a human.
- **Promotion and demotion are not symmetric** (Nick, 2026-08-04). Both count
  as changed terms under 8b and are listed in the move-map, and in steady
  state the drift lint (criterion 9) detects the boundary crossing. What
  differs is who acts.
  - **Promotion is required, so the tool performs it.** A term used in two
    documents *must* be defined in the glossary; leaving it in a body breaks
    the single-definition rule. The tool has no choice, so it informs the
    human and reconfigures (ruling of 2026-07-31).
  - **Demotion is optional, so a human decides.** A term used in one document
    *may* be defined there — the rubric's word. Leaving it in the glossary
    breaks nothing; it only makes the glossary longer than it needs to be. So
    the tool reports that the term qualifies and **waits**, and the message
    says plainly that nothing is wrong. Two further reasons: moving a
    definition out of the glossary is a content change across files with
    every first-use link rewritten, not the word-preserving tidy-up the guard
    is allowed to make alone; and usage counts wobble, so an automatic rule
    would shunt a definition back and forth on successive edits.
  - Limb 2 keeps the case rare: a single-document term stays in the glossary
    if any glossary definition depends on it, so demotion only arises when
    both limbs stop applying.
- **Term lifecycle (D10):** every concept record carries a `status`
  (`candidate → approved → published → deprecated`). A renamed term records
  its successor in `superseded_by`; the old spelling becomes a deprecated
  alias, and body text using it is flagged as deprecated usage, not as an
  unknown term.
- **Known-orphan waivers (D10):** "no term left undefined" is an
  **end-state invariant**. During incremental glossary completion, a
  **waiver register** records each known, ticketed orphan or conflict with
  an owner and a disposition deadline — extending the documented-exception
  pattern already used for cycles (ISO 704 §6.5.2). The lint distinguishes
  waived debt (does not re-fire) from new regressions (always flag). A
  waiver is a deferral, not an approval: the set is not fully done while
  waivers are open. **Built 2026-08-03 in Phase 3 (step 3.9), pulled forward
  from 10.5 by Nick's ruling of 2026-07-31** — `detangle validate` already
  reports findings that are dispositioned but not yet fixable, and without
  the register it cannot become a required check. "Does not re-fire" is
  implemented as *does not block*: `registers/waivers.yaml` entries carry
  `owner`, `ticket` and `review_by`, and a covered finding is still printed
  and counted, because a deferral that disappears from the log reads as an
  approval. `review_by` is recorded but not enforced — a gate whose verdict
  turned on wall-clock would go red with no commit behind it.
- **Acronyms:** every acronym is expanded at first use in each section,
  matching the citation rule in criterion 1. The definition is keyed on the
  expansion, with the acronym as an alias.
- **Synonyms and aliases:** recorded explicitly; two entries may not define
  the same concept.
- **No dead entries.** Every glossary entry has at least one use somewhere in
  the set. An entry no document uses is cruft and is raised for disposition —
  either the usage was lost in restructuring, which is an omission, or the
  term does not belong in the glossary. Computed from term extraction.
- **Scope:** one `glossary.md` for the set, never per-document.

### The index

`index.md` is the single lookup surface for the whole set.

- **Coverage:** every term defined anywhere in the set — in the glossary or
  in any of the three documents — appears exactly once, in alphabetical
  order. A reader must never need to know in advance whether a term is
  shared or document-local in order to find it; resolving that is the
  index's entire job.
- **Entry shape:** `term → location of its definition`. The location is the
  glossary anchor for a shared term, or the document and section for a
  document-local term. Aliases and acronyms appear as their own alphabetical
  entries pointing at the same location, so a reader who only knows "QBCCL"
  need not already know its expansion.
- **Terms only.** No definitions, no prose, no commentary. A definition
  appearing in the index would violate the single-definition rule.
- **Generated, never hand-maintained.** The index is derived mechanically
  from the other four documents and is verified by regeneration
  (criterion 6). It is not a place where content can be lost or invented.
- **Definition locations only.** The index answers "where is this term
  defined". It does not answer "where is this term used" — no document
  carries a usage concordance. Usage locations are derived data and live in
  `concept-graph.yaml`, queryable there when needed.

- **Verification method:** automatic — every term flagged by term extraction
  (Phase 3.1) has exactly one definition at the site the placement test
  requires, or a references entry, or an explicitly approved omission; and
  exactly one index entry resolving to that site.
- **Status:** depends on `glossary.md` and `index.md` existing (Phase 3).

## 4. Losslessness

Every substantive claim in the **detangle set** appears in the output set.
Nothing is invented. Any omission has explicit human approval, tracked as a
PR comment. **Reference-document claims are not required in the output**
(2026-08-05): the reference set supplies definitions and context, it is not
detangled, and the absence of its claims from the output set is not an
omission — with one carve-out: a definition actually lifted from a reference
document is output content like any other, and criteria 5 and 7 apply to it
in full.

- **Substantive claim:** an independently assertable statement of fact, rule,
  threshold, or relationship. Granularity per `param-claim-granularity`.
  Headings, navigation text, and pure formatting are not claims.
- **Losslessness is evaluated set-wide, not per file.** A claim that leaves
  Document 3 and lands in `glossary.md` is present in the output set and is
  therefore not an omission.
- **Relocation to the glossary is not omission.** Moving a definition out of
  a document and into the glossary needs no per-instance approval, provided:
  1. the term satisfies the placement test in criterion 3;
  2. the glossary definition is at least as specific as every document
     instance it replaces (no loss of qualifier, scope, or threshold);
  3. the relocation is recorded in the move-map with all source locations;
  4. each document's first use cites the glossary entry, per criterion 1.
- **Deduplication is not omission.** Collapsing semantically equivalent
  claims into one is permitted **without** per-instance approval, provided:
  1. the surviving instance is at least as specific as every instance it
     replaces;
  2. the merge is recorded in the verification report, with all source
     locations listed;
  3. the surviving instance sits where the earliest source instance would
     have been needed, or earlier.

  If the instances differ in any qualifier, it is not a merge — it is either
  two distinct claims or a contradiction (see criterion 6).
- **Pass condition:** the harness reports zero unresolved omissions and zero
  unresolved fabrications across the output set, and every merge and
  relocation has a report entry.
- **Records are not part of the output set** (Nick, 2026-08-04). The output
  set is the five documents; the Phase 7 harness opens those and never opens
  a concept record. So a corpus claim parked in a record's `notes` — as the
  ISO 704 narrowing pass did for thirteen records — is an **omission**, not a
  relocation, and must land in document prose beside its definition block
  when the body is written. `notes` is a staging post, not a destination.
- **Every run records the versions it verified** (ADR-004 Decision 7, Nick
  2026-08-07). The harness runs at `param-full-verify-cadence` — every re-run
  — not on every PR, so documents move between runs and "the set as it stood
  at the last run" has to be identifiable afterwards. It is, cheaply: a
  document's version *is* its git blob (`git rev-parse HEAD:<doc>`), immutable
  and retrievable with `git show` however many versions follow. So the run
  writes the blob of every document in **both** input sets, plus the commit,
  into its report — the same pin `eval/README.md`, a reorder plan's
  `pinned_blob` and the generated move-map already carry. Two things then
  work that otherwise cannot: the proof names what it proved, and the next
  run has a baseline — v_n+1 is checked against v_n, and v_n is a blob. This
  is deliberately not a new mechanism; `manifest.yaml` (step 10.4) is the
  set-level version of the same record and absorbs it when it lands.
- **Verification method:** automatic — Phase 7 harness (claim decomposition →
  coverage check → fabrication check), run over the set.
- **Status:** depends on the harness existing (Phase 7).

## 5. Precision preservation

Restructuring must not weaken, strengthen, or blur a source statement
(constraint C7).

The following are reproduced **verbatim** wherever the claim they belong to
survives into the output set — including when the claim relocates to the
glossary:

- numbers, percentages, thresholds, ranges, units, and comparison operators
  (`≤ 1%`, `15%`, `10–20`, basis points);
- modal verbs and normative force (`must` / `shall` / `should` / `may`) — a
  paraphrase may not change modality;
- scoping qualifiers (`non-LOW classifications only`, `intragroup`,
  `where quote-domain patterns are dominant`);
- internal codes and identifiers (RT01, RD02, QDSP, MWBR_ANOMALOUS) and
  their exact casing;
- regulatory and document citations (MAR Article 12, BIVM v28 §10b, ESMA,
  FSMA);
- enumerated level sets and their order (NONE / LOW / MEDIUM / HIGH /
  VERY HIGH);
- document metadata and classification markings (Document ref., Version,
  Date, Applies to, **CONFIDENTIAL**);
- source spelling and house style (British spelling — "behavioural",
  "formalises" — is preserved, not normalised).

- **Glossary inheritance:** where a definition relocates to the glossary, the
  glossary entry inherits the strictest classification marking of any source
  it draws on — a reference document included, when the definition was
  lifted from one (2026-08-05). A CONFIDENTIAL definition does not become
  unclassified by moving.
- **Verification method:** automatic and mechanical — extract the above
  tokens from the **detangle set plus the spans lifted from reference
  documents**, and from the output set, and diff the multisets. Whole
  reference documents are never in the diff: their unclaimed content would
  make the comparison fail by construction (2026-08-05). This
  check is deliberately independent of the Phase 7 claim mapping, because a
  claim can map correctly and still have lost its modality or its qualifier.
- **Tool-stamped markers are not words** (ADR-004 Decision 9, Nick,
  2026-08-07). Every HTML comment the tool stamps — `sec:`, `concept:`,
  `AI addition:`, `omitted` — is removed before the multisets are built.
  `para_hash` has always ignored them, pandoc's plain writer dropping raw
  HTML, and the two measures must agree about what content is. The exposure
  is the re-run: once a run's input is the previous run's marked output,
  every marker is a *source* token this check would demand back, while the
  renderer re-emits its own from the plan and the records rather than
  copying them. **Visible text still counts, the `[AI addition]` tag
  included** — pandoc keeps visible text, so keeping it here is what
  agreement requires, and it is what "ink on the page counts"
  (`param-overview-max-words`, 2026-08-05) already says. The tag counts only
  while it is there: an approved addition keeps its comment and loses its
  blockquote (criterion 7, ADR-004 Decision 3 as amended 2026-08-08), so on a
  re-run the comment is stripped as any other and the blockquote is simply
  absent from both sides. Neither state needs a special case here.
- **Status:** buildable from Phase 6; specified now.

## 6. Reference and metadata integrity

Restructuring must not break addressing, into or out of the set
(constraint C8).

- Every internal cross-reference ("see Section H", "§11.5") resolves to an
  existing location in the restructured set.
- Every inbound reference target that existed in the source remains
  reachable: either the section identifier is preserved, or the output
  carries an alias table mapping the old identifier to the new location.
- Cross-document references ("Document 1 of 3", "UCE v28") resolve to the
  correct document and version.
- **Document numbering is unchanged.** The three documents remain
  "Document 1/2/3 of 3". The glossary and the index sit **outside** the
  numbering as named companions; they are not "Document 0" or "of 5", and
  they renumber nothing. The glossary's position in the reading order is
  editorial, not a change to any document's identity metadata.
- **Every first use of a glossary term in a section links to its glossary
  entry, and every such link resolves.** Links run forward only — no
  document carries back-references to where its terms are used.
- **Usage locations live in `concept-graph.yaml`.** Which documents and
  sections use a term is recorded as graph edges, not duplicated into prose.
  This is what makes impact analysis possible when a definition changes:
  forward reachability over the graph names every section needing
  re-verification. Storing the same data in the glossary would denormalise
  it and churn the glossary on every content edit — including edits that
  touch no definition, which would then wrongly count against
  `param-max-terms-changed-per-PR`.
- **The index is complete and resolving:** every term defined anywhere in the
  set appears exactly once in `index.md`; every index location resolves to
  the actual definition site; no index entry points at a term that no longer
  exists; no defined term is missing from it. Because the index is
  generated, any failure here is a tool bug rather than a review finding,
  and it is fixed rather than dispositioned — it must not consume comment
  budget.
- **Provenance anchors are hash-stable and staleness is visible (D10).**
  Record source spans are `(document, section ID, paragraph hash,
  verified_against)` — the tool-stamped section ID carries identity, the
  content hash (computed over the normalised pandoc AST, so reflow is not
  a change) detects edits, and raw line numbers are used nowhere. A span
  whose hash no longer matches flips the record to `provenance: stale` — a
  visible state requiring re-verification, never silent rot. A stale
  record's definition remains published but its losslessness evidence is no
  longer current.
- **Manifest coherence (D10):** `manifest.yaml` matches the actual set —
  every derived artifact regenerates byte-identical from the current bodies
  and records. A mismatch means a derived artifact was hand-edited or a
  regeneration was skipped; like an index failure, it is a tool/process bug,
  fixed rather than dispositioned.
- The metadata/front-matter block of each document is preserved verbatim
  (see criterion 5).
- **Source contradictions are surfaced, never silently resolved.** Where the
  source contradicts itself, the output preserves both statements, marks the
  conflict, and the tool raises a PR comment. A live example in the current
  corpus: `blueprint-MCL-shortened.md` is headed "Version 21 / v21 — Full
  document release" and then contains a "What is new in v22" block.
  Harmonising this without approval would violate "no meaning invented".
- **Conflicting definitions across documents** are a contradiction, not a
  merge: where two documents define the same term differently, both are
  preserved, the conflict is raised as a PR comment, and
  `param-manual-reviewer` decides which becomes the glossary entry.
- **Verification method:** automatic (link/anchor resolution, metadata diff,
  first-use link resolution); contradictions detected LLM-assisted and
  dispositioned by `param-manual-reviewer`.
- **Status:** buildable from Phase 6; specified now.

## 7. Provenance marking

Every part of the output is classifiable into exactly one of three provenance
categories, and the two non-verbatim categories are visually and mechanically
distinguishable from source-derived text.

**Two axes, recorded separately** (ADR-004 Decisions 1, 2 and 2b, Nick
2026-08-07). *Lineage* — where wording came from — is per span, `origin:
corpus | authored` on each of a record's citations, because a definition can
be assembled from original wording plus a sentence typed later. *Assurance* —
who vouches for it — is per record, `author` / `approved_by` / `pr`, because
approval is one human act covering the definition as a whole.

The two must not be collapsed. Withholding a `para_hash` used to do both jobs
at once, and Decision 1 rules that the second is wrong: text a human writes at
v1.2 has the same definitional strength as text a human wrote at v1.0, and
AI-drafted text a named human approved is equivalent to human-written. The
first job still has to be done — in a re-run cycle run N+1's input is run N's
output, so without recorded lineage the fabrication check would trace every
claim successfully by generation 2, inventions included.

Two consequences for this criterion. **An authored definition may carry a real
span** into the version it entered at; it is no longer the case that authored
text can never be anchored. And **because assurance now carries all the
definitional strength, approval has to be a real act** — the requirement below
that a draft show the usages it was assembled from is load-bearing, not
advisory. How many definitions one approval may cover is ADR-004 Decision 4,
unruled, and its parameter is absent from `detangle.toml` rather than guessed.

### Category A — moved

Source text reproduced verbatim, possibly relocated — including relocated
into `glossary.md` from another file. **No marking required**; the move-map
records where it came from.

### Category B — derived

Source text rewritten while preserving its meaning. **Permitted transforms,
exhaustively:**

1. splitting one sentence into several, or joining several into one;
2. resolving a pronoun or a "this / the above" reference to its explicit
   noun phrase;
3. converting a table row or cell into prose, or prose into a table row;
4. converting a nested parenthetical or footnote into a standalone sentence;
5. reordering clauses within a sentence;
6. expanding an acronym at first use;
7. merging duplicate claims under the rules in criterion 4;
8. condensing a document's definitional passage into a one-sentence glossary
   entry under the relocation rules in criterion 4.

Any transform not on this list is Category C. Derived text is marked at block
level:

```markdown
<!-- derived:start src="MCL §11.4 ¶2" -->
Rewritten text goes here.
<!-- derived:end -->
```

The `src` attribute is required and names the source location(s), qualified
by document where the source is a different file from the output. Derived
text carries **no** visible tag in the rendered document — it is source
meaning, and visible tagging at this volume would make the document
unreadable. It stays machine-traceable through the comment markers and the
move-map (criterion 8).

**A definition lifted from a reference document is Category B**
(2026-08-05): the wording is the business's, reproduced verbatim or lightly
stitched, and the `src` attribute names the reference document — the
cross-file qualification above already covers it, so no new category is
needed. Unlike Category C text it carries a real provenance span
(`para_hash` + git blob) into the reference file. Every lift is recorded in
the move-map and listed in the PR's aggregated comments so a reviewer sees
it, but it needs no per-item approval — the ruling that a named human must
approve applies to *invented* text, and a lift invents nothing.

### Generated navigation — outside the categories

`index.md` in its entirety, the first-use glossary links inside the
documents, and the move-map are **generated navigation**, not content. A
first-use link asserts nothing about the domain — it points at a definition
that already exists elsewhere in the set. They carry no
provenance marking: they assert nothing about the domain, they are derived
mechanically from the body text, and marking them would flood the
fabrication check with noise — every index line would otherwise read as an
invented claim.

They are verified differently, by **regeneration**: the check rebuilds them
from the four content documents and compares. Anything a reader could
mistake for a claim about the domain belongs in a content document, not in
navigation.

### Category C — added (bridging)

New explanatory text with no source claim behind it. Marked both
machine-readably and visibly.

**Who may write one** (Nick, 2026-08-04). **AI may draft; a named human
approves**, and the approval is recorded in the record's provenance block
along with the PR and the set version. The draft **shows its evidence** — the
usages elsewhere in the corpus it was assembled from — or states explicitly
that there are none. A definition assembled from six real usages is a
different object from one composed out of background knowledge, and the
approver must be able to tell which they are approving. Barring AI drafting
outright was rejected: 187 undefined terms is not work that gets done by
hand, an unwritten definition fails criterion 3's end-state invariant, and
the source corpus was itself AI-assisted, so the bar would have been higher
for the fix than it ever was for the original.

**Authored text carries a real span into the version it entered at**
(ADR-004 Decisions 1 and 2, Nick 2026-08-07). This reverses the earlier rule
that authored text never acquires a `para_hash`. That rule read the hash as
asserting *the business wrote this wording at this revision* and concluded it
was false for authored text — but it was doing two jobs with one field, and
Decision 1 rules the second one wrong. The hash records **lineage**: which text,
which version. Whether anyone vouches for it is `assurance`, a separate field,
and the two no longer share a mechanism.

What the old rule protected against still has to be handled, and Decision 2
handles it: without recorded lineage, run N+1 traces every claim to run N's
output — inventions included — and the fabrication check proves nothing from
generation 2 onward. `origin: corpus | authored` on the span is what keeps the
two apart. `flags: [orphan]` survives an authored definition as before, and
means only "the detangle set never defined this".

**Provenance is asserted against a content hash, and breaking it demotes.**
Change a definition's text and any provenance claim attached to it is
invalidated until re-established. Where an edit breaks corpus provenance —
someone rewords a Category A or B definition so it no longer traces to its
anchored block — the tool **drops it one rung down this ladder and comments;
it does not block**. Demotion never over-claims, and blocking makes people
stop fixing typos. The general rule: the guard may weaken a provenance claim
on its own; it may never strengthen one.

**Marking format — an addition has two states** (ADR-004 Decision 3 as amended,
Nick 2026-08-08). Approval removes the visible tag and keeps the machine-readable
marker.

*Drafted, not yet approved:*

```markdown
<!-- AI addition:start -->
> [AI addition] Plain-language new sentence text goes here.
<!-- AI addition:end -->
```

*Reviewed and approved* — the blockquote goes, the comment gains the approver
and the PR:

```markdown
<!-- AI addition:start approved-by="<reviewer>" pr="<link>" -->
Plain-language new sentence text goes here.
<!-- AI addition:end -->
```

- The marker string is exactly `AI addition:start` / `AI addition:end`, and
  the visible tag is exactly `[AI addition]`. Both are **case-sensitive**.
- **Why the comment survives approval.** For a definition, AI authorship is
  recorded in the record's `assurance.author`. But assurance is per *concept
  record*, and the largest Category C text in the set — criterion 2's required
  overview — is a section, not a concept, so it has no record and no assurance
  block. The comment is that text's only in-document authorship trace. Keeping
  it costs nothing: `tokens.COMMENT` strips every HTML comment before counting
  (ADR-004 Decision 9), so it is invisible to criterion 5 and to the re-run
  cycle alike.
- **Why the visible tag goes.** Under Decision 1 approved text is equivalent to
  human-written and should read as ordinary document text. The blockquote is
  what a reader meets; the comment is not.
- **Who performs the transition is not settled**, and the tool may not assume
  it: dropping the blockquote deletes words, so it falls outside the
  word-preserving exception that lets the guard edit a body at all. Today a
  human makes the edit in the approving PR. See `plan/backlog.md`.
- `approved-by` and `pr` mirror the approved-omission marker below, which
  carries the same two attributes for the same reason.
- **Section-level bridging:** where the addition is a whole section — most
  importantly the overview required by criterion 2 — use the section form,
  which marks the section once instead of wrapping every sentence:

  ```markdown
  <!-- AI addition:start scope="section" -->
  ## Overview

  > [AI addition] This section was written to introduce the document; it is
  > not derived from a single source passage.

  …overview body…
  <!-- AI addition:end -->
  ```

  Where the overview restates source claims, those sentences are Category B
  and are marked as derived **inside** the section, so the fabrication check
  does not treat restated source content as invented.
- **Inside tables:** HTML comments and blockquotes cannot live inside a
  markdown table cell. Bridging content in a table is written as
  `[AI addition] …` at the start of the cell, and the whole table is preceded
  by `<!-- AI addition:contains-additions -->` so the check knows to parse
  cells.
- **Nested blockquotes:** where the source text is already a blockquote, the
  bridging blockquote is written one level deeper (`>>`) to stay
  distinguishable.
- **Glossary entries with no source definition.** A term used across the set
  but never defined anywhere in the **detangle set** is an orphan (the
  plan's convolutedness measure — narrowed 2026-08-05; reference documents
  were never part of the count). If a reference document defines it, the
  definition is lifted as Category B (above) and the orphan-style flag
  survives the lift. Only where **neither set** defines the term is its
  glossary entry Category C in full, and that always raises a PR comment —
  an invented definition is the highest-risk output the tool can produce.

### Omissions

Approved omissions leave a trace in the document, not only in the PR:

```markdown
<!-- omitted src="MCL §11.6 ¶4" approved-by="<reviewer>" pr="<link>" -->
```

- **Verification method:** automatic — the Phase 7 fabrication check confirms
  every non-source-traceable claim falls inside an `AI addition` block, and
  every Category B block resolves to its `src`. The check keys off the **HTML
  comment**, never the visible tag, because an approved addition has only the
  comment (Decision 3 as amended). Both states satisfy it identically; the
  attributes are read, not required.
- **Status:** conventions fixed now (Phase 1); automatic check from Phase 7.

## 8. Reviewability

A human must be able to approve the change. A full restructure rewrites whole
files, so the diff is near-100% and is not reviewable as a diff — and
constraints C3/C4 depend entirely on that review being real.

For scale: the three shortened samples are 3,800–6,400 words, ~220–270
sentences, and an estimated 350–600 substantive claims each. A review process
that surfaces a meaningful fraction of those to a human does not work.

### 8a. The PR unit is a concept, not a file

**A PR assembles changes relating to similar concepts.** The number of
documents it touches is irrelevant — a PR may change one document, all five,
or only the glossary. `index.md` is regenerated by any PR that changes a
term, and its regeneration is never itself the subject of a PR. This follows from glossary-first: promoting a term to
the glossary inherently changes the glossary *and* every document that used
to define or restate it, and splitting that across PRs would produce
intermediate states where a term is defined twice or not at all.

A PR is coherent when a reviewer can state its subject in one line — "define
the quote intelligence terms (QBRS, QBLI, QBCCL) in the glossary and cite
them from Documents 2 and 3."

### 8b. Term budget

**A PR may not change more terms than `param-max-terms-changed-per-PR`.**
A run that would exceed the cap splits into multiple PRs along concept
boundaries; if it cannot split without leaving a term defined twice or not
at all, it fails and reports rather than opening the PR.

A PR **changes a term** when it:

- adds, removes, or edits that term's definition;
- moves the definition between documents, or between a document and the
  glossary (promotion or demotion per criterion 3);
- changes the term's name, expansion, or aliases;
- changes an edge incident to that term in `concept-graph.yaml`.

Adding or updating a *citation* to an unchanged definition does not count as
changing the term; nor does relocating text that merely uses it.

### 8c. Comment budget

Because C3 makes every PR comment a blocking item a human must Resolve,
comment volume is the second binding constraint on workability.

- A run producing more than `param-max-comments-per-PR` blocking comments
  **does not open a PR.** It fails and reports. Exceeding the human's
  capacity is a tool failure surfaced at run time, not a problem discovered
  at review time.
- Only exceptions produce comments: omissions, fabrications, cycles,
  contradictions, conflicting definitions, orphan terms, and low-confidence
  rewrites. Moves, derived rewrites, merges, and relocations are silent —
  they are recorded in the move-map and counts, and are reviewable there.

### 8d. Comment aggregation

Comments are raised **per cluster, not per instance**. One comment reading
"12 duplicate claims merged, listed below" rather than twelve comments. A
comment covering multiple instances lists every instance and its source
location, so one Resolve dispositions the whole cluster.

### 8e. Two-commit structure

Every PR contains exactly two commits, in this order:

1. **Moves only.** Content relocated — within a file or across files, into
   the glossary included — with zero text changes. The diff is large but
   carries **no semantic review load**: it is verified mechanically by
   confirming that the multiset of content lines across **the whole output
   set** is unchanged. The check is set-wide precisely because content
   legitimately crosses file boundaries.
2. **Derived and added text.** Everything that changed wording.

The reviewer reads commit 2. Commit 1 is machine-verified. A PR whose commit
1 fails the set-wide unchanged-content check is rejected before review.

### 8f. Required artifacts

The output is not done unless the PR ships with:

- a **move-map**: every source section mapped to its location(s) in the
  output set, and every output section mapped back to its source(s),
  including cross-file relocations into the glossary;
- a **term-change list**: every term the PR changes, with its before/after
  definition site — this is what `param-max-terms-changed-per-PR` is counted
  against, and it is the reviewer's index into the change;
- **counts**: claims moved / derived / merged / relocated / added / omitted;
- an **exceptions list**: every cycle, forward reference, contradiction,
  conflicting definition, orphan term, approved omission, and low-confidence
  rewrite, each with its PR comment link.

All are plain-text and committed alongside the documents (constraint C6).

### 8g. Optional two-stage review

Where a change is large or unusually tangled, the reorder plan (a one-page
table of section moves and term placements) may be approved in its own PR
*before* the rewrite runs. The content PR then confirms a structure already
agreed, rather than asking the reviewer to discover it. Not mandatory; at the
reviewer's request.

- **Verification method:** presence and completeness check (automatic); the
  reviewer's approval is the pass signal.
- **Status:** specifiable now; produced from Phase 6.

## 9. Continuous-change coherence (steady-state)

The document set remains coherent while it evolves after delivery
(constraint C12, decision D10). Bodies stay directly editable — by humans
and by AI agents — and every such edit is guarded, not forbidden.

- **Drift lint on every docs PR.** Branch policy runs an incremental check
  on the changed sections only: terms are re-extracted and diffed against
  the record set. It raises PR comments (per cluster, 8d; blocking via C3)
  for:
  1. a new term with no definition site (orphan regression);
  2. an inline (re)definition of an existing term (single-definition-site
     violation). This is narrow now that documents own their own
     definitions: a body defining a term *it* owns is the normal case, not a
     finding. It bites only when the term belongs to the glossary. The lint
     **blocks** — this is a real violation, unlike demotion — and blocks by
     showing both texts and offering two routes: remove the body text and
     link, or update the glossary definition to the new wording. It never
     merges them and never deletes the new wording by itself, because which
     text is better is a judgement (Nick, 2026-08-04). **A one-click
     suggested fix is offered only where the body text is a verbatim
     restatement of the glossary definition** — the case where deleting it
     provably loses nothing. Where the texts differ, the difference is either
     an improvement worth promoting or a contradiction worth surfacing, and
     both need a person. Promoting body wording into the glossary is never
     one-click: it spans two files, so it could only be delivered as a commit
     from the guard, which is the guard editing prose;
  3. a term used before the position its topological order assumes
     (criterion-1 regression);
  4. a usage count crossing the placement boundary (promotion/demotion
     trigger, criterion 3);
  4a. a change to the `depends_on` edges a definition mints — **reported,
     never applied** (Nick, 2026-08-04, reaffirming D10 element 4). The
     lint extracts candidate edges from the changed definition block, diffs
     them against the record's canonical `depends_on`, and lists the
     difference for a human to rule on. It changes nothing itself: an edge
     is a judgement about what a definition is for, it sets reading order
     and impact answers, and a silently minted one can restructure the set
     or create a cycle nobody dispositioned;
  5. a candidate contradiction with the current glossary definition
     (LLM-assisted, dispositioned by `param-manual-reviewer`);
  6. provenance staleness introduced by the edit (criterion 6);
  7. use of a deprecated alias (criterion 3 lifecycle);
  8. an ID-hygiene violation — duplicate section-ID markers (copy-paste
     carries the marker along), missing markers, or malformed markers.
- **What the guard may change, and what it may never change** (Nick,
  2026-08-04). The guard may make **word-preserving** edits — machine-verified
  to change no words — and must leave a PR comment whenever it does. Stamping
  section IDs and reordering glossary entries are both of this kind. It may
  never change meaning: rewriting prose the tool believes is wrong stays
  forbidden, and every such case is a comment for a human to act on.
- **Section IDs are stamped by the tool, never by authors.** Addressing is
  two-layer (research-memo §D10 element 2): tool-stamped `<!-- sec:… -->`
  markers are the identity layer; content hashes in the generated
  `state/section-map.yaml` are the change-detection layer; line numbers are
  used nowhere. A PR adding unstamped sections receives a **stamping
  commit** from the guard, machine-verified to change nothing but `sec:`
  markers. Asking a human or AI author to mint or maintain IDs is a
  non-goal.
- **Derived artifacts are regenerated, never hand-maintained:** usage edges,
  first-use links, `index.md`, `state/section-map.yaml`, `manifest.yaml`. The
  regenerate-and-compare guard covers all of them; a hand-edit to any of
  them fails CI. Two deliberate exclusions (Nick, 2026-08-04): the Mermaid
  render is produced on demand by `detangle graph --mmd <id>` rather than
  committed, so there is nothing to keep in sync; and `state/notices.md` is
  **generated but unguarded**.
- **`state/notices.md` — things worth knowing that are not defects** (Nick,
  2026-08-04). Findings block; waivers defer a real problem with an owner and
  a date; notices are neither. A demotion candidate, a review date falling
  due, a Phase 5 authoring debt — none of these is wrong, so none may raise a
  finding, or "nothing is broken" becomes a red build. They are written to a
  committed markdown file instead, so a new notice appears as a line in the
  PR diff, which a green CI log cannot achieve.

  The file is **not** covered by the regenerate-and-compare guard: reading it
  is the responsibility of the people writing and reviewing documents, and a
  stale notices file must never block a PR. Because it is not byte-compared
  it carries a header naming the commit it was generated from and when —
  visible age in place of enforcement, which `concept-graph.yaml` cannot have
  without breaking its byte comparison.
- **The lint ships with its test suite — part of the deliverable.** One
  seeded fixture per flag type above, plus the negative case (a
  reorder-only PR must flag nothing) and the structural edge cases (section
  split; section merge; deleted section with live usage edges), per the
  Phase 7 seeded-error pattern. This criterion is not satisfiable by a lint
  whose checks have never caught a seeded error: the guard is not wired
  into branch policy until every fixture passes (Phase 10.7).
- **The edit contract:** the guard checks and comments; it never auto-fixes
  a body and never merges (C4). Resolving its comments is the whole price of
  a direct edit. The moved/derived/added provenance marking of criterion 7
  applies to tool restructuring runs, not to ordinary steady-state body
  edits — those are governed by this criterion.
- **Wording goes in the markdown; position goes in the plan** (ADR-004
  Decision 8, Nick 2026-08-07). A fix typed into a document survives a
  re-run when it changes *words* — `restructure` moves blocks verbatim — and
  does not survive when it changes *where text sits*, because a reorder plan
  governs position and puts the block back. The two files hold different
  facts: the document is authoritative about every word, which criterion 5's
  token parity enforces independently, and the plan is authoritative about
  order, and only while a run executes. Moving a paragraph by hand is
  editing the order through the file that owns the wording, so the change
  never reaches the surface that carries it. This used to fail **silently**,
  which is the worst way for it to fail; `plan-position-conflict` now
  reports each hand-moved block and emits the plan line that would ratify
  the move. It is a warning, never a block: placement is a claim, so
  detection is automatic and the disposition is a human's — the same
  division as a body edit proposing a `depends_on` edge (D10 element 4).
- **Tiered cadence:** this lint runs on every PR; the full losslessness
  harness (criterion 4) runs at `param-full-verify-cadence` — **every
  re-run**, and additionally at any release tag (ADR-004 Decision 7). A
  release is not done until the full harness has passed on the current set.
  Between full runs the documents move, so each full run records the blob of
  every document it verified: that is what identifies "the set as it stood
  at the last run", and what the next run reads as its baseline.
- **Waivers:** findings covered by an open waiver-register entry do not
  re-fire (criterion 3); anything not waived flags every time.
- **Verification method:** automatic (the lint and regeneration checks are
  themselves CI); contradiction candidates and waiver dispositions go to
  `param-manual-reviewer`.
- **Status:** schema fields from Phase 3; delivered in Phase 10 — except the
  waiver register, which is built in Phase 3 (step 3.9) under Nick's ruling of
  2026-07-31.

---

## Non-goals — what the tool must never do

A violation here is blocking regardless of any other criterion passing.

- Change any number, threshold, unit, or comparison operator.
- Change normative modality (`must` ↔ `should`).
- Alter or drop classification markings, version identifiers, or metadata.
- Alter regulatory citations, or add citations not present in the source.
- Resolve a source contradiction, correct a perceived source error, or update
  stale content.
- Reconcile two documents that define the same term differently — surface it,
  do not choose.
- Normalise spelling, terminology, or house style.
- Invent section headings that assert structure not implied by the source. A
  purely navigational heading over existing content is Category C bridging
  and is allowed, marked.
- Merge, split, or renumber the detangle-set documents. Relocating a
  definition into the glossary is not a split; adding the glossary ahead of
  them is not a renumbering.
- Modify a reference document (2026-08-05). The reference set is read-only:
  never edited, never restructured, never stamped with markers. This was
  previously only a comment in `detangle.toml`; it is a non-goal in its own
  right now that reference documents are a first-class input set.
- Define the same term in two places, or leave a term defined nowhere.
- Merge a PR, resolve a PR comment, or approve its own omissions.
- Hand-edit a generated artifact (`index.md`, usage edges, first-use links,
  `concept-graph.yaml`, `state/section-map.yaml`, `manifest.yaml`) — or
  auto-"fix" a document body in steady state: the guard comments, humans
  decide. (The stamping commit is the sole exception, and it is
  machine-verified to touch only `sec:` markers.)
- Ask an author — human or AI — to create or maintain a section ID.

## Adjudication and severity

| Criterion | Severity | Adjudicator |
|-----------|----------|-------------|
| 1 Concept-before-use | Blocking | Automatic; cycles → reviewer |
| 2 Abstraction pyramid | Blocking (checklist), advisory (editorial) | Reviewer |
| 3 Glossary and index completeness | Blocking | Automatic; omissions → reviewer |
| 4 Losslessness | Blocking | Automatic; omissions → reviewer |
| 5 Precision preservation | Blocking | Automatic |
| 6 Reference/metadata integrity | Blocking | Automatic; contradictions and conflicting definitions → reviewer |
| 7 Provenance marking | Blocking | Automatic; orphan-term definitions → reviewer |
| 8 Reviewability | Blocking | Automatic (both budgets); PR coherence → reviewer |
| 9 Continuous-change coherence | Blocking | Automatic; contradiction candidates and waivers → reviewer |
| Non-goals | Blocking | Automatic where checkable, else reviewer |

"Reviewer" is `param-manual-reviewer`. Every automatic flag needs a
disposition before merge (`param-false-positive-tolerance`); "false positive"
is an acceptable disposition and is recorded in the verification report.
Where automatic and human judgement disagree, the reviewer decides and the
decision is recorded.

## Interim done by phase

The full rubric applies to tool output from Phase 6 onward. Before that, a
reduced subset gates each deliverable.

| Phase | Deliverable | Criteria in force |
|-------|-------------|-------------------|
| 1–2 | this rubric, research memo | none — the rubric is the deliverable |
| 3 | glossary, index, concept graph | 1, 2, 3, and 6 — the glossary is a reader-facing document, so its overview and topological ordering are in force, not just the graph; the index must be complete and resolving. Records carry the criterion-9 schema fields (`status`, `superseded_by`, hash-anchored spans) from the start |
| 5 | golden restructured output | all eight content criteria, verified **manually** — the golden output is the reference standard, so it must satisfy the full rubric even though no harness exists yet |
| 6 | prototype output | 1, 2, 5, 6, 7, 8 automatic where buildable; 4 manual |
| 7+ | tool output | criteria 1–8, automatic where specified |
| 10 | steady-state guard | 9 in full — and via it, incremental enforcement of 1, 3, and 6 on every subsequent docs PR |

## Summary — verifiability by phase

| # | Criterion | Verifiable from |
|---|-----------|------------------|
| 1 | Concept-before-use | Phase 3 (manual until then) |
| 2 | Abstraction pyramid | Phase 1 manual; partly automatic from Phase 3 |
| 3 | Glossary and index completeness | Phase 3 |
| 4 | Losslessness | Phase 7 |
| 5 | Precision preservation | Phase 6 (mechanical, independent of the harness) |
| 6 | Reference/metadata integrity | Phase 6 |
| 7 | Provenance marking | Conventions fixed now; automatic check from Phase 7 |
| 8 | Reviewability | Phase 6 |
| 9 | Continuous-change coherence | Phase 10 (schema fields from Phase 3) |

**Done when:** Nick signs off on this document, including the parameter
values.
