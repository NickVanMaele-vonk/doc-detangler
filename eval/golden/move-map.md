# Move-map — UCE golden (step 5.2 stage B, criterion 8f)

Every source block of `samples/blueprint-UCE-shortened.md` (pinned blob
`4cae72dece7638c1ddec8206a3c6a24610196de0`), where it went, and every
transform applied. Source block IDs `S-01`–`S-14` are the reorder plan's
(`eval/golden/reorder-plan.md` §1).

## Block moves

| Source | Content | Target in `uce.md` | Category |
|---|---|---|---|
| `S-01` (lines 1–9) | Title block, document identity, classification marking | Document head, before the overview | A — verbatim, in place |
| `S-01` (line 11) | Purpose paragraph | §1 | A — moved |
| `S-02` (incl. `S-03`, `S-04`, `S-05`) | Version history v23–v29, with the three amendment blocks inside their version cells | §6.1, amendments kept inside the version history (Nick, 2026-08-05 via the amended reorder plan) | A — moved; B — table rendered as headed list (see transforms) |
| line 15 | Version-history lead ("Substantive" definition) | §6.1, first paragraph | A — moved |
| line 56 | Change-note convention | §6.1, closing italic line | A — moved |
| `S-06` | Parts index (X–XX, Doc 7, ECIL Supplemental) | §6.2 | A — moved; B — Doc 7 row rejoined with its page-split continuation "readiness." |
| `S-07` (line 94) | Sector-agnostic scope paragraph | §1 | A — moved |
| `S-08` (§I.1) | The analytical question | §1 | A — moved |
| `S-09` | Principles 1–11 | §3 | A — moved; B — principle 5's page-split row rejoined |
| `S-10` | Principle 12 + "New in Version 25" note | §3; the note becomes an italic table note, not a row | A — moved |
| `S-11` (§I.3) | IS/IS-NOT contrast | §2 | A — moved |
| `S-12` (§II.1 prose) | Stage 0 / IBEB paragraph | §4.1 | A — moved |
| `S-13` | 22-step pipeline table | §4.2, rejoined into one table | A — moved; B — six page-split rows rejoined |
| `S-14` (§II.2) | HCP-1–HCP-5 table | §5 | A — moved; the step-22 row that sat inside it returns to the pipeline table (§4.2) |
| PART I / PART II banner rows | Part titles | §6.2, first two rows of the Parts index | B — banner reformatted as index rows |

## Category B transforms (rejoined page-split rows)

Each is transform "several fragments joined", recorded with its join:

1. **Principle 5** — "5. Economic reality is" + "independently tested";
   "Every qualified signal is independently assessed for" + "economic
   materiality."
2. **Step 5b** — dimension "Domain" + "Independence Filter (DIF)"; gate
   "GATE: domain" + "diversity check for HIGH"; key rules "…: DIF" +
   "verifies that CQS is built…".
3. **Step 9** — "…(Volume, Price, Dominance, Timing," + "Cross-alert,
   Repetition). IScore (0--24.3)…".
4. **Step 11c** — dimension "Market-Wide Behavioural" + "Reference (MWBR)";
   gate "SCORED OUTPUT: peer" + "normalisation for quote- domain signals";
   key rules "…: MWBR" + "computes the participant's behaviour…".
5. **Step 18** — dimension "Regulatory" + "Context (RRF)"; gate "ADDITIVE"
   + "AMPLIFIER"; key rules "…PriorityScore_final = PriorityScore" +
   "+ RRF. Requires CQT≥2.".
6. **Step 21b** — key rules "…they are responding to the" + "same market
   conditions as everyone else. HIGH classification requires…" (the
   continuation sat inside the §II.2 table fragment).
7. **Doc 7 Parts-index row** — "…QA-MAR, EU AI Act" + "readiness." (the
   continuation sat in the second Parts-index fragment).
8. **Step IDs** — `11 b` → `11b`, `11 c` → `11c`, `21 b` → `21b` (split in
   the Step column by the OCR; column furniture, not claim text).

Formatting-only transforms, applied throughout and claim-preserving:

- Grid tables re-rendered as markdown pipe tables; cell text verbatim, one
  row per physical line (unwrapped, same rationale as the glossary).
- The version-history table re-rendered as a headed list (`**v23 --- Jun
  2025**` + paragraphs), because its v25 and v29 cells hold multi-paragraph
  amendment texts that cannot live in a pipe-table cell. No token added or
  dropped.
- Pandoc escape backslashes (`\"`, `\|`, `\'`, `1\.`) removed — markdown
  escaping, not content.

## Dropped as noise (criterion 4: pure formatting, not claims)

Inventory, verbatim, so the decision is visible rather than silent:

- Three page footers: `Page 9 PPPPPPPPaaaaaaaaggggggggeeeeeeee 99111111000022`,
  `Page 10 PPPPPPPPaaaaaaaaggggggggeeeeeeee 1111111100111133`,
  `Page 11 PPPPPPPPaaaaaaaaggggggggeeeeeeee 1111111111222244`.
- Two stray page-boundary fragments rendered as their own one-cell tables:
  `refi S ector Pack ( Doc 2)` and `dfi S ector Pack ( Doc 2)`.
- Two inline copies of the same artifact, spliced mid-sentence by the OCR:
  step 11c "…sessions wherefi S ector Pack ( legitimate…" → "…sessions
  where legitimate…", and step 21b "…sovereign bondfi S ector Pack ( dealer
  markets…" → "…sovereign bond dealer markets…".
- Five repeated pipeline-table header rows and one repeated header on the
  fragment holding step 22 (`**St ep** | Dimension | Gate/Output | Key
  Rules`), one repeated Parts-index header (`Part | Content`), one repeated
  principles-table header — one header of each table is kept, rejoined
  (`St ep` → `Step`).
- Source pseudo-headings (`**Version History**`, `**I.1 The Analytical
  Question**`, `**I.2 Core Design Principles**`, `**I.3 What the Engine Is
  Not**`, `**II.1 Pipeline Overview**`, `**II.2 Human Intervention
  Checkpoints**`) — navigation, replaced by the target section headings;
  their content is carried by those sections.

**Not dropped:** OCR damage *inside claim text* is reproduced verbatim and
surfaced instead — see `exceptions.md` (source-defect cluster and the step
11b garbled passage). The line: table furniture is formatting; a damaged
token inside a claim is a source defect, and defects are data (criterion 6,
family-A precedent of 2026-07-31).

## Section IDs (C12 two-layer addressing, hand-stamped)

`<!-- sec:u-<8 hex> -->` per target section; the ID is the first 8 hex of
sha256 over the section's content — everything after the marker line up to
the next marker or end of file, UTF-8, exactly as first stamped — computed
once and never recomputed. Change detection is the section map's job
(Phase 10), not these IDs. Phase 6's stamper must reproduce this recipe.

| Section | ID |
|---|---|
| Overview | `u-a48738c9` |
| Terms defined in this document | `u-61b5f491` |
| §1 | `u-db14c483` |
| §2 | `u-b30dd7df` |
| §3 | `u-8b56eed5` |
| §4 | `u-43d38f1e` |
| §5 | `u-03d2b71e` |
| §6 | `u-2f87db53` |
