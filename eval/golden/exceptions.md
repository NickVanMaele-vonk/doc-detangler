# Exceptions — UCE golden (step 5.2 stage B, criterion 8f)

What would become PR comments in a real run, aggregated per cluster (8d).
Nothing here is fixed silently; each cluster names its disposition owner.

## 1. Orphan definitions drafted: zero — deliberately

The reorder plan allows drafting a Category C definition "where the corpus
supplies usages it can be assembled from". Measured position: **none was
drafted**, for three reasons. Step 3.3 was the exhaustive assembly pass —
every definition that corpus wording supports already exists on a record,
and the 47 UCE-placed orphans are orphans because that pass found nothing
definitional. Composing a definition from usage *hints* rather than
definitional wording is precisely what criterion 7 calls the highest-risk
output the tool can produce. And the overview already demonstrates the
Category C machinery the golden needs to show. **Nick may direct
otherwise** — any term below can be given a drafted definition in review.

## 2. Orphans left undefined: 84 terms

47 UCE-placed (roster in `term-changes.md`) and 37 glossary-placed
(rendered with the undefined note in `glossary-slice.md`). Each is
positioned; none blocks reading. One is notable:
`behavioural-scenario-library` is used in **two** sections (§3 principle
12, §6 v24 entry) while undefined — under C9-recursed it would sit in
"Terms defined in this document" the day it gains a definition; today it is
flagged here instead of holding an empty block there.

## 3. Version skew: carried, not harmonised

`U` is titled Version 29; `M` states it applies to UCE v28 and `S` cites
v30. Cross-document, so only `U`'s side is visible here — the title block
and the v29 history entry are reproduced verbatim, and the skew stands for
human disposition (criterion 6; recorded since the 2026-07-31 session).

## 4. Normative rules left inside the change log

Ruled by Nick 2026-08-05 (reorder plan §2): the amendment texts stay in the
version history, to be removed by hand in a later review pass. What a
reader therefore cannot find under a heading of its own: XI.1 PIR
Amplifier-Only Rule, XI.2 Price Impact Gate, XI.3 RSA Net Score Thresholds,
VI-A.3.7.1 BCI Engine Operational Status, VI-A.3.7.2 D1/D2 Data Dependency,
VI-A.3.7.3 CQS Uplift by BCI Level, and the §XIII.2a output-field addition.
Their definitions are surfaced (11 definition blocks at the top of §6), so
the terms are findable even though the rules sit in the log. Reported, not
fixed.

## 5. Source defects carried verbatim (B-1 candidates)

Defects are data (criterion 6); damaged tokens inside claim text are
reproduced exactly and listed here rather than repaired:

- **The step 11b garbled passage.** Exception (c) and the rationale of the
  Persistence Gate row are OCR-interleaved beyond reconstruction — two text
  streams merged character-wise ("MRaAtioNnDaleA: TgeOnRiYue…"; the caps
  spell fragments of one stream, the lowercase another). Carried
  byte-exact from the source. Partially legible content — a threshold that
  reads `≥ 0.75`, "genuine manipulation … persists across multiple
  sessions", "involves multiple participants", a sector-pack reference —
  **cannot be restored without inventing text (C2)**. Reconstruction needs
  the unshortened source, i.e. the B-1 path.
- **OCR-split tokens inside claims**, reproduced verbatim:
  `pattern_matc hed`, `ExplanationFa ilure`, `EscalationRead iness` (step
  21), `pre- EscalationRea diness` (step 20), `STOR_Readine ss`,
  `HUMAN_REVIE W_REQUIRED`, `notificatio n`, `governanc e`.
- **Broken hyphens inside claims**, reproduced verbatim: `code- level`,
  `supervisor- defensible`, `cost- aware`, `single- domain`,
  `MEDIUM- INVESTIGATE` (step 11b — the already-waived family-A defect),
  `MEDIUM- STRUCTURED REVIEW`, `quote- domain`, `market- wide`,
  `wide` variants, `CCO- initiated`, `No- Benign-Explanation`,
  `POST- VALIDATION`, `DAF dual- mechanism`. The three findings already
  waived in `registers/waivers.yaml` are this family; the rest join B-1's
  inventory when the source correction runs.
- **VI-A.3.7.3 "CQS Uplift by BCI Level:"** ends with a colon and no
  content — the table it introduced did not survive the shortening.
  Truncation carried as-is.
- **"Ten foundational principles govern the engine"** introduces a table of
  twelve. Contradiction surfaced, not corrected (the v24/v25 history rows
  even record principle 12's later addition — the intro sentence was never
  updated).

## 6. Interleaved section boundaries (reconstructed)

`S-13`/`S-14` overlap in the source: step 22's row and step 21b's
continuation sit inside §II.2's table. Boundaries were reconstructed from
content — step rows to §4.2, HCP rows to §5 — as the reorder plan
prescribes; the joins are itemised in the move-map.

## 7. Deviation: no generated navigation

The golden carries no first-use links into the glossary and no anchors
beyond the concept/section markers. First-use links and `index.md` linking
are **generated navigation** (criterion 7), verified by regeneration, and
the generator is step 3.6+/Phase 6 work that does not exist yet;
hand-writing them would create hand-maintained derived artifacts, which is
exactly what D10 prohibits. The golden demonstrates the content criteria;
navigation is regenerable. **Needs Nick's confirmation.**

## 8. Deviation: exceptions list instead of waiver entries

The reorder plan (§3, written before step 3.9's semantics were fixed) says
undefined orphans are flagged "with a waiver entry". No built check raises
per-orphan findings today, and a waiver matching no live finding raises
`waiver-stale` on a required gate. So the orphan roster lives here and in
`term-changes.md` — same visibility, no unsatisfiable gate. Waiver entries
can be minted when a check exists that raises these findings. **Needs
Nick's confirmation.**

## 9. Forward references: zero

Confirmed by projection: the accepted cycle
(`liquidity-driven-reaction` ↔ `identity-driven-coordination`) is not among
the 73 entries `U` uses, so the slice reads start to finish with no
bridging marker — matching the reorder plan's expectation and C9 limb 2's
guarantee for the rest.
