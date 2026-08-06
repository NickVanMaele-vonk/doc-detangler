# Counts — UCE golden (step 5.2 stage B; the 5.3 measurement input)

Measured from the delivered triple, not predicted. Word counts by
`wc -w`-style whitespace splitting; token parity by the multiset diff below.

## The triple

| Artifact | Measure |
|---|---|
| `uce.md` | 8 sections, 42,172 bytes; 35 definition blocks; 1 Category C section (the overview, 214 words, ≤ `param-overview-max-words` 400) |
| `glossary-slice.md` | 73 entries, 36 defined, 37 with the undefined note; 0 forward references within the slice (the accepted cycle is not in `U`'s slice — as the reorder plan expected). `uce.md`'s own definition order is measured separately, in the review-load table below |
| `index-slice.md` | 155 terms, 84 marked "not defined in the corpus" (Nick's ruling, 2026-08-05) |

## Terms (8b)

| Measure | Count |
|---|---|
| Terms in scope | 155 |
| Terms changed (definition given a marked site in `uce.md`) | 35 |
| — of which in "Terms defined in this document" | 7 (6 before the 2026-08-05 correction; see `exceptions.md` §9) |
| — of which in a single section | 28 |
| Promotions / demotions / placement changes | 0 |
| Definitions drafted (Category C) | 0 |
| Orphans positioned and flagged | 84 (47 UCE-placed + 37 glossary-placed) |
| Records edited | 0 |

## Content categories (criterion 7)

| Category | Instances |
|---|---|
| A — moved, verbatim | 14 source blocks (see move-map) |
| B — derived | 8 rejoins of page-split rows/IDs + 3 formatting re-renderings (pipe tables, version list, banner rows as index rows) + 35 definition blocks (record copies, cross-file `src` = the records) |
| C — added | 1 (the overview, section form, visibly tagged) |
| Omissions | 0 — every source claim is in the output; the noise inventory in the move-map is formatting, not claims |

## Criterion-5 token parity (mechanical)

Multiset diff of word tokens, source vs `uce.md` (authored scaffolding —
overview, definition blocks, target headings, table furniture — excluded
from the golden side; nothing excluded from the source side except grid
rules and page footers). Every residual difference is classified; there are
**no unclassified differences**:

| Residual | Explanation |
|---|---|
| golden-only: `11b`, `11c`, `21b`, `Step` | rejoined step IDs and table header (`11 b`→`11b`, `St ep`→`Step`) |
| golden-only: `where`, `bond` | the two inline OCR insertions removed (`wherefi S ector Pack (`, `bondfi S ector Pack (`) |
| source-only: `St`×6, `ep`×6, `Dimension`×5, `Gate/Output`×5, `Key`×5, `Rules`×5, `Principle`×2, `Statement`×2, `Enforcement`×2, `Mechanism`×2, `Part`, `Content`, `Version`×2, `Date`, `Substantive`, `changes`, `History` | repeated table headers on page-split fragments (one of each kept) and the version-history header row |
| source-only: `11`×2, `b`×2, `c`, `21` | the split step IDs |
| source-only: `S`×4, `ector`×4, `Pack`×4, `(`×4, `Doc`×2, `2)`×2, `refi`, `dfi`, `wherefi`, `bondfi` | the four copies of the page-boundary artifact (two standalone, two inline) |
| source-only: `PART`×2, `I.1`, `I.2`, `I.3`, `II.1`, `II.2`, `Overview`, `Pipeline`, `Analytical`, `Question`, `Core`, `Design`, `Principles`, `Engine`, `What`, `Is`, `Not`, `Human`, `Intervention`, `Checkpoints`, `The`, `the` | source pseudo-headings and PART banners, replaced by target headings; banner titles relocated into the Parts index |

Verbatim-sensitive tokens (codes, numbers, thresholds, operators, modality)
show **zero** residual difference.

## Review load (what 5.3 reads from `exceptions.md`)

| Expected PR-comment cluster (reorder plan §4) | Measured |
|---|---|
| Orphans with a drafted definition | 0 terms — cluster empty, rationale recorded |
| Orphans left undefined | 1 cluster, 84 terms |
| Version skew | 1 |
| Normative rules left inside the change log | 1 |
| Source defects carried verbatim (beyond the 3 already waived) | 1 cluster (damaged tokens + the step 11b garble + the truncated VI-A.3.7.3 list + the "Ten principles"/12 rows contradiction) |
| Forward references | 0 — after the 2026-08-05 correction; measured wrong before it (`exceptions.md` §9) |
| Deviations needing Nick's confirmation | 2 (no generated navigation; exceptions list instead of waiver entries) — see `exceptions.md` §7–8 |
