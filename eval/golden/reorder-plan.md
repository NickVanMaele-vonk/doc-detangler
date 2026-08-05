# Golden reorder plan — `U` (Universal Core Engine)

Step 5.2, stage A. This is the **8g two-stage review** artifact: a one-page
table of section moves and term placements, approved on its own before the
rewrite runs. Nothing here is output — no restructured prose exists yet.

**Status:** proposed, awaiting Nick's approval.
**Input:** `samples/blueprint-UCE-shortened.md`, pinned at blob
`4cae72dece7638c1ddec8206a3c6a24610196de0` (`eval/README.md`).
**Output of stage B:** `eval/golden/uce.md`, `eval/golden/glossary-slice.md`,
`eval/golden/index-slice.md`, plus the criterion-8f artifacts.

---

## 1. What the source actually contains

The shortened `U` is 3,835 words in 293 physical lines, almost all of it
pandoc-converted grid tables. It has **no markdown headings at all** — its
structure is carried by bold pseudo-headings (`**I.1 The Analytical
Question**`) and by table cells naming Parts.

| ID | Source block | Lines | Shape |
|----|--------------|------:|-------|
| `S-01` | Title block, document identity, purpose sentence | 1–11 | prose |
| `S-02` | Version History — v23…v29 rows | 13–39, 41, 53–56 | grid table |
| `S-03` | Amendment UCE-AMD-BVR-001 §XI.1–XI.3 (RSA/PIR rules) | 26–32 | table cell, normative |
| `S-04` | Amendment UCE-AMD-BVR-001 §VI-A.3.7.1–3 (BCI engine) | 43–49 | table cell, normative |
| `S-05` | §XIII.2a output-field addition note | 51 | table cell, normative |
| `S-06` | Parts index — Parts X–XX, Doc 7, ECIL Supplemental | 59–91 | grid table |
| `S-07` | Sector-agnostic scope paragraph | 94 | prose |
| `S-08` | §I.1 The Analytical Question | 96–98 | prose |
| `S-09` | §I.2 Core Design Principles — Principles 1–11 | 100–139 | grid table |
| `S-10` | Principle 12 (QA Validation) + its "New in Version 25" note | 143–147 | grid table |
| `S-11` | §I.3 What the Engine Is Not — IS/IS-NOT contrast | 150–163 | grid table |
| `S-12` | §II.1 Pipeline Overview — Stage 0 / IBEB prose | 166–168 | prose |
| `S-13` | The 22-step pipeline table, steps 1–22 | 171–279 | grid table, page-split |
| `S-14` | §II.2 Human Intervention Checkpoints HCP-1…HCP-5 | 272–293 | grid table |

Parts I and II are the only Parts whose content is present. Parts III–XX
exist only as one-line summaries in `S-06`.

### Damage that stage B must handle

- **Page-split table rows.** The pipeline table is broken across page
  boundaries and repeats its header row five times; six rows are split, with
  the continuation appearing before the header of the next fragment — step 5b
  continues at line 195, step 9 at 209, step 11c at 225, step 18 at 253, step
  21b at 277. Rejoining them is Category B transform 1 (joining several
  sentences into one) and is recorded in the move-map.
- **OCR noise.** `**St ep**`, `11 b`, `refi S ector Pack (Doc 2)`, and the
  page-footer lines (`Page 9 PPPPPPPPaaaaaaaa…`) are pure formatting, not
  claims (criterion 4). Dropping them is **not** an omission and raises no
  comment; the move-map records them as dropped noise so the decision is
  visible rather than silent.
- **Interleaved sections.** `S-13` and `S-14` overlap: the pipeline table's
  step 22 row sits at line 279, *after* the §II.2 heading at line 272, and
  step 21b's continuation at line 277 sits inside §II.2's table. Section
  boundaries in `U` therefore cannot be taken from reading order — they are
  reconstructed from content, and the reconstruction is recorded in the
  move-map rather than assumed.
- **Live version skew** — the document is titled Version 29 while `M` applies
  to UCE v28 and `S` cites v30. Surfaced in the exceptions list, **never
  harmonised** (criterion 6, non-goals).

---

## 2. Target outline

Reading order within the document, general → specific (criterion 2).

| # | Target section | Sources | Notes |
|---|----------------|---------|-------|
| — | `## Overview` | none | **Category C**, ≤ `param-overview-max-words` (400). What the document is for and what it contains. |
| — | `## Terms defined in this document` | records | Definitions used in more than one target section (rule in §3). Topological order. |
| 1 | `## 1. What the Universal Core Engine is` | `S-01` purpose sentence, `S-07`, `S-08` | Scope and the single analytical question, before anything else. |
| 2 | `## 2. What the engine is not` | `S-11` | The IS/IS-NOT contrast bounds the scope just stated. |
| 3 | `## 3. Core design principles` | `S-09`, `S-10` | Twelve principles; Principle 12's version note becomes a footnote, not a row. |
| 4 | `## 4. The analytical pipeline` | `S-12`, `S-13` | 4.1 Stage 0 and the IBEB; 4.2 the 22 steps, rejoined into one table. |
| 5 | `## 5. Human intervention checkpoints` | `S-14` | Where a human acts, after the machine pipeline that triggers them. |
| 6 | `## 6. Constructs specified in amendment notes` | `S-03`, `S-04`, `S-05` | **Relocated out of the change log.** These are normative rules (PIR amplifier-only cap, price-impact gate, RSA scaling formula, BCI levels and gates, 18 new output fields), not change metadata. |
| 7 | `## 7. Document control` | `S-02`, `S-06` | Version history and the Parts index, verbatim, moved to the end: a change log is the archetype of detail-first opening. |

Two moves carry the restructuring argument and are the ones worth
disagreeing with:

- **§6 exists because normative content is living in a change log.** The
  amendment blocks specify Parts VI-A, XI and XIII, none of which are present
  in this extract. Leaving them inside the version-history table would keep a
  reader from ever finding them; relocating them without comment would hide
  that the source put them there. So they move, and the relocation is raised
  as a criterion-6 finding for disposition.
- **Document control moves to the end.** Nothing in it is dropped and no
  number changes (criterion 5), so this is a Category A move.

---

## 3. Term placement

**155 terms are in scope** — the 82 records placed in UCE, plus the 73
glossary-placed records `U` uses. 71 carry a corpus definition; **84 do not.**

| Set | Terms | Defined | Undefined |
|-----|------:|--------:|----------:|
| UCE-placed records | 82 | 35 | 47 |
| Glossary-placed records used by `U` | 73 | 36 | 37 |
| **In scope** | **155** | **71** | **84** |

### Where the source anchors them

By the `section` of each UCE-placed record's `U` span:

| Source section | Records anchored there |
|----------------|-----------------------:|
| Front matter (`S-02`, `S-06`) | 51 |
| §II.1 Pipeline Overview | 22 |
| §I.2 Core Design Principles | 14 |
| §II.2 Human Intervention Checkpoints | 4 |

**51 of 82 are anchored in front matter** — that is, in a change log and a
table of contents for Parts that do not exist in this extract. This is the
convolutedness the tool measures, stated as a number for the first time, and
it is why 47 of the 82 are orphans.

### The placement rule inside the document

C9's placement logic, recursed one level down:

- A UCE-placed term used in **exactly one** target section is defined **in
  that section**, in a marked block at the top of it.
- A term used in **two or more** target sections is defined in
  `## Terms defined in this document`, immediately after the overview.

The rule is computable from the finished body rather than judged, matching
C9's "placement is computed, not judged". The split cannot be computed until
stage B writes the body; the source-section table above is the proxy.
Definitions are never inline inside a table cell — most of `U` is tables, and
a definition in a cell is unfindable and unmarkable.

### The 84 orphans

Per the approved design point 3: draft a definition where the corpus supplies
usages it can be assembled from, showing that evidence; where it does not,
leave the term positioned and flagged, with a waiver entry, rather than
composed out of background knowledge. Every drafted definition is Category C
in full, visibly tagged, and raises a PR comment (criterion 7).

### Markers

Every target section carries `<!-- sec:u-<8 hex> -->` and every definition
`<!-- concept:<id>:start -->` / `:end`. The ID is the first 8 hex of the
sha256 of the section's content **at first stamp** — stamped once and never
recomputed, so a reorder never renumbers, and change detection stays with the
section map's current-content hash (the two layers of C12). Hand-stamped
here; Phase 6's stamper must reproduce the scheme.

---

## 4. Expected exceptions

What stage B is expected to raise as PR comments, aggregated per cluster
(8d). Counts are the 5.3 measurement, not predictions to be met:

| Cluster | Expected |
|---------|---------|
| Orphan terms with a drafted definition | one comment, listing each |
| Orphan terms left undefined and waived | one comment, listing each |
| Normative content relocated out of the change log (§6) | one |
| Version skew across `U`/`S`/`M` | one |
| Source defects already waived (`definition-token` hyphens) | carried, not re-raised |
| Forward references | expected zero — the accepted cycle is not in `U`'s slice |

---

## 5. Not decided here

1. **Index coverage of undefined terms.** Criterion 3 defines the index over
   terms *defined* anywhere in the set. The generated glossary already renders
   the 77 undefined entries with a "not defined in the corpus" note, so those
   anchors exist. Proposal: the index slice covers all 155 and marks the
   placeholder targets, so a reader looking up an orphan learns it is
   undefined instead of finding nothing. Nick's call.
2. **`notes` staging-post clauses.** Corpus wording parked in records during
   the ISO 704 narrowing pass must land in `uce.md` prose beside its
   definition block, or it is an omission under criterion 4. Which of the
   thirteen belong to `U` is resolved in stage B.
3. **Whether §6 survives review.** If Nick rules the amendment blocks stay in
   the change log, §6 disappears and `S-03`–`S-05` fold back into §7.
