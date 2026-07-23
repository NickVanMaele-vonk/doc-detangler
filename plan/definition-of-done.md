# Definition of Done — Restructured Documents

**Status:** **Approved** by Nick, 2026-07-21 (v3). **v4, 2026-07-23:**
criterion 9 (continuous-change coherence) and its supporting scope,
parameter, and criteria amendments added per decision D10, at Nick's
direction; new parameter values remain proposals until set.
**Phase:** 1.1 — complete; extended by D10
**Last updated:** 2026-07-23

A restructured document is "done" when it satisfies all nine criteria below,
subject to the phase-dependent applicability rules in
[Interim done by phase](#interim-done-by-phase).

---

## Scope and applicability

- **The output set is five documents.** Three input documents; a glossary
  which is created based on the input documents and ranks as the first
  document of the set; and an index. Both the glossary and the index are
  reader-facing deliverables, not tool artifacts.
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
  - a term used in **more than one document** is defined in `glossary.md`,
    and **only** there;
  - a term used in **exactly one document** is defined in that document, at
    or before its first use;
  - no term is defined in two places.
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
  `glossary.md` records the version of every source it draws on. When any
  source version changes, every output document depending on it is **not
  done** until re-verified.
- **Set version binding (D10):** a generated `manifest.yaml` binds the whole
  set — per-document version, record-set revision, dependency-graph hash,
  derived-artifact hashes, generation timestamp. Each concept record carries
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
| `param-max-terms-changed-per-PR` | **25** (set) | Maximum terms a single PR may change. See 8b. |
| `param-max-comments-per-PR` | 25 | Maximum blocking PR comments; set for real from Phase 5 measurements. |
| `param-overview-max-words` | 400 | Maximum length of the required opening overview. |
| `param-claim-granularity` | one claim per source sentence; one claim per table cell carrying an independent assertion | Governs criterion 4. |
| `param-false-positive-tolerance` | none | Every flag needs a disposition, but "false positive" is a valid disposition. |
| `param-manual-reviewer` | Nick, optionally Ivo for domain accuracy | Adjudicator for the manual criteria. |
| `param-low-confidence-threshold` | to be set from Phase 5 | This dial, and contradiction frequency, are the only unbounded contributors to comment volume. |
| `param-glossary-order` | **topological** (set) | `glossary.md` is ordered by topological sort throughout. Alphabetical lookup lives in `index.md`, not in the glossary. |
| `param-full-verify-cadence` | every release tag | How often the full C1/C2/C7 harness runs in steady state (the per-PR drift lint always runs). Proposal; set for real from steady-state experience (D10). |

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
- **Cycles:** a genuine definitional cycle cannot be fixed by reordering.
  A cycle satisfies this criterion when all of the following hold:
  1. the cycle is recorded in `concept-graph.yaml` with a human disposition;
  2. one member is designated the entry point and defined first, using a
     forward reference of the form "…see [Term] below", marked as bridging
     text per criterion 7;
  3. the forward reference is listed in the verification report.

  Because shared definitions now sit in one file that precedes the
  documents, cross-document cycles collapse into intra-glossary cycles,
  which are resolvable by reordering the glossary. This is a primary
  motivation for glossary-first.
- **Verification method:** automatic, against `concept-graph.yaml`.
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
- **Placement test:** term usage is counted across the source set. Used in
  ≥ 2 documents → glossary. Used in exactly 1 → that document. The count is
  derived mechanically from term extraction, so placement is a computed
  property, not a judgement call.
- **Promotion and demotion:** if a later revision introduces a second use of
  a document-local term, that term is **promoted** to the glossary; if a
  term falls to a single document, it may be **demoted**. Both count as
  changed terms under 8b and are listed in the move-map. In steady state,
  the drift lint (criterion 9) detects the boundary crossing and raises it;
  the promotion/demotion itself still lands as a concept-scoped PR.
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
  waivers are open.
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

Every substantive claim in the source set appears in the output set. Nothing
is invented. Any omission has explicit human approval, tracked as a PR
comment.

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
  it draws on. A CONFIDENTIAL definition does not become unclassified by
  moving.
- **Verification method:** automatic and mechanical — extract the above
  tokens from the source set and the output set and diff the multisets. This
  check is deliberately independent of the Phase 7 claim mapping, because a
  claim can map correctly and still have lost its modality or its qualifier.
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
machine-readably and visibly:

```markdown
<!-- AI addition:start -->
> [AI addition] Plain-language new sentence text goes here.
<!-- AI addition:end -->
```

- The marker string is exactly `AI addition:start` / `AI addition:end`, and
  the visible tag is exactly `[AI addition]`. Both are **case-sensitive**.
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
  but never defined anywhere in the source is an orphan (the plan's
  convolutedness measure). Its glossary entry is Category C in full, and it
  always raises a PR comment — an invented definition is the highest-risk
  output the tool can produce.

### Omissions

Approved omissions leave a trace in the document, not only in the PR:

```markdown
<!-- omitted src="MCL §11.6 ¶4" approved-by="<reviewer>" pr="<link>" -->
```

- **Verification method:** automatic — the Phase 7 fabrication check confirms
  every non-source-traceable claim falls inside an `AI addition` block, and
  every Category B block resolves to its `src`.
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
     violation);
  3. a term used before the position its topological order assumes
     (criterion-1 regression);
  4. a usage count crossing the placement boundary (promotion/demotion
     trigger, criterion 3);
  5. a candidate contradiction with the current glossary definition
     (LLM-assisted, dispositioned by `param-manual-reviewer`);
  6. provenance staleness introduced by the edit (criterion 6);
  7. use of a deprecated alias (criterion 3 lifecycle);
  8. an ID-hygiene violation — duplicate section-ID markers (copy-paste
     carries the marker along), missing markers, or malformed markers.
- **Section IDs are stamped by the tool, never by authors.** Addressing is
  two-layer (research-memo §D10 element 2): tool-stamped `<!-- sec:… -->`
  markers are the identity layer; content hashes in the generated
  `state/section-map.yaml` are the change-detection layer; line numbers are
  used nowhere. A PR adding unstamped sections receives a **stamping
  commit** from the guard, machine-verified to change nothing but `sec:`
  markers. Asking a human or AI author to mint or maintain IDs is a
  non-goal.
- **Derived artifacts are regenerated, never hand-maintained:** usage edges,
  first-use links, `index.md`, `concept-graph.mmd`,
  `state/section-map.yaml`, `manifest.yaml`. The
  regenerate-and-compare guard covers all of them; a hand-edit to any of
  them fails CI.
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
- **Tiered cadence:** this lint runs on every PR; the full losslessness
  harness (criterion 4) runs at `param-full-verify-cadence`. A release is
  not done until the full harness has passed on the current set.
- **Waivers:** findings covered by an open waiver-register entry do not
  re-fire (criterion 3); anything not waived flags every time.
- **Verification method:** automatic (the lint and regeneration checks are
  themselves CI); contradiction candidates and waiver dispositions go to
  `param-manual-reviewer`.
- **Status:** schema fields from Phase 3; delivered in Phase 10.

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
- Merge, split, or renumber the three source documents. Relocating a
  definition into the glossary is not a split; adding the glossary ahead of
  them is not a renumbering.
- Define the same term in two places, or leave a term defined nowhere.
- Merge a PR, resolve a PR comment, or approve its own omissions.
- Hand-edit a generated artifact (`index.md`, usage edges, first-use links,
  `concept-graph.mmd`, `state/section-map.yaml`, `manifest.yaml`) — or
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
