# Step 6.2 — prototype output compared to the golden

ADR-002 build step 4. The prototype (`detangle restructure`) executed the
approved reorder plan against the pinned `U` blob; this records how its
output compares to the golden triple that step 5.2 approved by hand.

**Same input, same plan, two executions.** ADR-002 Decision 5 scoped 6.1 to
`U` precisely so this comparison would be controlled: hand execution (the
golden) against machine execution (the prototype), with nothing else
varying. `S` and `M` wait for Phase 9.1.

**The bar is per criterion, not byte equality** (ADR-002 Decision 4). The
golden's incidental formatting is not normative. Where the two disagree the
golden wins unless Nick rules the prototype found a golden defect — either
way the disagreement is recorded below.

**Reproduce every figure here with one command:**

```bash
detangle restructure --plan eval/golden/uce.plan.yaml \
                     --out <doc.md> --report <dir>
```

Exit `0`, no findings, `9/25` comments. Two consecutive runs are
byte-identical, and `--check` re-executes and byte-compares both the
document and the three report artifacts. Nothing from the run is committed:
the plan and the source blob are pinned, so the run is the record.

---

## 1. Section structure and order

| Measure | Machine | Golden |
|---|---|---|
| `<!-- sec:u-… -->` markers | 8 | 8 |
| Their order | identical | identical |
| `## ` headings | 8 | 8 |

The eight section IDs appear in the same order in both files. **Match.**

## 2. Definition-block placement and prose

35 blocks in each. The ordered list of `(concept id, block text)` pairs is
**equal**, so every definition sits in the same place and its prose is
byte-identical to the golden's — which is byte-identical to the record's, the
definition blocks being record copies. **Match.**

This includes the block the 2026-08-05 ruling moved:
`participant-interaction` renders in "Terms defined in this document", ahead
of `persistence-gate`, in both.

## 3. Token parity (criterion 5)

Multiset diff of word tokens over the whole document, normalised for
markdown escaping and table furniture, run in both directions:

| Direction | Result |
|---|---|
| In the golden, missing from the machine output | **none** |
| In the machine output, missing from the golden | **none** |
| Tokens counted each side | 4,855 |

The command's own in-run `token-parity` check, which compares the assigned
source blocks against the source-attributed output rather than golden against
machine, is also clean:

| Measure | Words |
|---|---|
| Source words expected | 3,473 |
| In source-attributed output | 3,427 |
| Explained renderer drops | 46 |
| Declared noise, never expected | 49 |
| Removed by declared removals | 18 |
| Added by declared repairs | 6 |
| **Missing — in no output section** | **0** |
| **Extra — in no source block** | **0** |

**Match**, and no unclassified difference in either direction. Criterion 5's
verbatim-sensitive tokens — numbers, thresholds, operators, modality, codes —
are inside that zero.

## 4. Marker discipline (criteria 7 and 9 forms)

| Measure | Machine | Golden |
|---|---|---|
| `concept:…:start` / `:end`, balanced and in the same order | 35 / 35 | 35 / 35 |
| `sec:` markers, all unique | 8 | 8 |

**Match.** No marker is orphaned, duplicated, or malformed on either side.

## 5. Orphan and exception rosters

The generated roster of 83 orphans is **exactly** the set derived
independently from the records: of the 155 terms in scope for `U` — 82
UCE-placed plus the 73 glossary slice entries — 83 carry `flags: [orphan]`.
No term is in one set and not the other, in either direction.

Exactly one in-scope term is undefined without an orphan flag —
`intraday-behavioural-event-builder`, by the IBE/IBEB ruling — which is why
84 terms carry no definition while 83 are orphans. The generator reports both
figures separately. **Match**, against the golden as corrected on 2026-08-05.

## 6. Comment clusters against the 5.3 baseline

Nine clusters, matching both the golden's nine and the 5.3 measurement in
`review-load.md`. Same nine subjects; the generator orders them differently,
putting forward references third where the golden appended it ninth.

| Cluster | Machine | Golden |
|---|---|---|
| Definitions drafted for undefined terms | none | zero, deliberately |
| Terms used here with no definition | 83 | 83 |
| Forward references | none | zero |
| Version skew carried, not harmonised | ✓ | ✓ |
| Normative rules left inside the change log | ✓ | ✓ |
| Source defects carried verbatim | ✓ | ✓ |
| Interleaved section boundaries reconstructed | ✓ | ✓ |
| Deviation: no generated navigation | ✓ | ✓ |
| Deviation: exceptions list instead of waiver entries | ✓ | ✓ |

Three are measured by the run and six are declared in the plan's
`exceptions:` list, per the 8f split. **Match**, and within
`param-max-comments-per-PR` (25) with the headroom 5.3 predicted.

---

## Findings

Five differences, none of them a failure of a rubric criterion. The first
three were golden-side measurement defects of the same family as the two
already ruled on 2026-08-05; **Nick ruled all three the same day and each is
now applied.** The rulings are recorded with their findings below.

### F-1 — "9 sections" and "8 sections" are both true — **ruled: 8**

The generated `counts.md` reports **9** sections; the golden's reports
**8**. Neither is wrong: the plan declares nine sections, one of which is
`{id: head, kind: head}` — the document identity block, which renders with
no heading and no `sec:` marker. The generator counts plan sections; the
golden counted headed sections. A reader comparing the two files sees a
discrepancy that is not one.

**Ruled by Nick, 2026-08-05: count the sections a reader can see.** The
generator now counts headed sections and reports **8**, matching the
golden, and says in `counts.md` what it is counting. Nothing is hidden by
the change: the move-map's Section IDs table still lists every plan
section, headed or not, so the identity block remains visible where its
identity matters. The run summary line moved with it —
`sections: 8`. Held by
`tests/test_restructure_report.py::test_the_headless_identity_block_is_not_a_counted_section`.

### F-2 — the golden's byte count is a character count — **ruled: relabel**

The golden's `counts.md` says `uce.md` is **42,172 bytes**. The file is
**42,429 bytes**; 42,172 is its length in characters, the two differing by
the document's non-ASCII characters (≥, σ, en-dashes). The generator reports
41,976 for its own output, which is bytes.

**Ruled by Nick, 2026-08-05: relabel it `characters`.** The number was a
real measurement wearing the wrong name, so the name changed and the number
did not. `counts.md` now reads "42,172 characters" and records the gap.

One consequence to know rather than discover: the two files now measure
different things on purpose — this one characters, the generated report
bytes — so the figures are not comparable and are not meant to be. Making
them comparable would mean the generator emitting both, which is a
one-line change nobody has asked for.

### F-3 — the golden's overview word count reproduces as neither figure — **ruled: 227**

The golden's `counts.md` says the overview is **214 words**. The overview
text is byte-identical in both files, and counts as **206** words as prose
alone or **227** with the visible `[AI addition]` tag block that opens the
section. 214 is neither.

The generator reports 227 — the whole section as a reader meets it. Both
figures are far below `param-overview-max-words` (400), so criterion 2's cap
is met on any reading and no verdict turns on this.

**Ruled by Nick, 2026-08-05: ink on the page counts** toward how long a
text is, even when AI wrote it. So the tag counts, 227 is the figure, and
the generator was already right. The golden now says 227.

This was worth ruling once rather than per artifact, so it is written into
the rubric beside the parameter it governs (`param-overview-max-words`,
`plan/definition-of-done.md`) — every future overview is measured the same
way, and no later run has to rediscover the question.

### F-4 — the category tallies are not comparable row for row

Criterion 7's A/B/C counts differ because the two carve the document
differently: the generator counts **plan assignments** (64 A, 13 transformed
B, 1 C), the golden counted **source groups** (14 A, 8 rejoins + 3
re-renderings B, 1 C). Both describe the same document. The generated
`counts.md` states this itself rather than inviting the subtraction.

*Not a defect.* Recorded so the next reader does not try to reconcile them.

### F-5 — the documents differ by 18 lines, all incidental

Byte equality is explicitly not the bar (Decision 4), and the whole
difference is:

- **9 lines** — the golden's `GOLDEN reference output` banner comment, which
  says what the file is and what it was built from. The machine writes no
  such banner.
- **5 lines** — stray blank lines in the golden.
- **2 lines** — markdown escaping: the machine writes `\|` inside a table
  cell and `\_` inside a word, where the golden left both bare.

No content line differs. *Not a defect on either side*, though the escaping
is worth knowing: the machine's is the safer rendering, and the golden's bare
`|` sits inside a table cell where it would split the row.

---

## What this does not close

**6.2 stays open until `param-low-confidence-threshold` is re-baselined**,
as ruled at 5.3 and reaffirmed in ADR-002 Decision 4. The honest reason is
in the ADR: under Decision 1 the prototype carries no machine confidence
scores at all — the judgment lives in a human-approved plan, and the command
executes it deterministically — so this run produces no confidence
distribution to baseline against. The first artifact that carries a mapping
score is the Phase 7 harness dry-run over this output. The value stays
provisional at 0.80 until that number has been looked at.

**The blast radius of the 2026-08-05 forward-reference ruling is still
unmeasured.** It was found in `U` and fixed in `U`. Whether `S` and `M` hold
terms in the same position — placed by a section count that saw prose
sections only — is not knowable until they have plans; the
forward-reference cluster in `restructure --report` is what will measure it.

**Everything here is one document.** ADR-002 Decision 5 scoped it that way
deliberately. A prototype that reproduces one hand-built golden has shown the
execution engine is faithful, not that the approach generalises; that is
Phase 9.1's question.
