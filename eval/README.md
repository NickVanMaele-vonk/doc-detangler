# Evaluation set — Phase 5

Step 5.1 of `plan/detangle-agent-plan.md`: designate the test inputs for the
evaluation set, and pin them.

This folder holds the test inputs' designation (this file), and — from step 5.2
— the golden reference output and the review-load baseline that step 5.3
measures from it.

## Test inputs

The three shortened component blueprints, and only those. Each is pinned to the
git blob it carried at commit `a088ee9`, the commit this designation was taken
at. Git carries release identity, so no version string is typed here — the same
rule the glossary's sources table follows (ruling of 2026-07-31).

| Code | File | Pinned blob | Words | Doc-placed records | Of which defined |
| --- | --- | --- | ---: | ---: | ---: |
| `U` | `samples/blueprint-UCE-shortened.md` | `4cae72dece7638c1ddec8206a3c6a24610196de0` | 3,835 | 82 | 35 |
| `S` | `samples/blueprint-SBSP-shortened.md` | `8a96710aac6c798eac3df1fbde0839725639ba95` | 6,350 | 63 | 32 |
| `M` | `samples/blueprint-MCL-shortened.md` | `71b9d9520ea205c72208fcc5d090b744f1e3e43b` | 5,472 | 59 | 27 |

The record counts are the terms whose definition site is that document, not the
terms it uses: the 155 glossary-placed records (78 defined) serve all three and
belong to no single input.

These are the same three documents `detangle.toml` names as `components` under
`[documents]`. That key governs the C9 placement count; this file governs what
the Phase 5 evaluation is run against. They coincide today, and the reasons are
different, so neither is derived from the other.

## Excluded, and why

| File | Reason |
| --- | --- |
| `samples/blueprint-analytical-layer.md` (`A`) | Read-only reference, excluded from the placement count (Nick, 2026-07-22); an `(A)` flag on a record is informational only |
| `samples/prototype-BC17.md` (`P`) | The prototype never counts (2026-07-26); `(P)`-only terms stay candidate rows until a U/S/M usage appears |
| `samples/dummydata-trades.csv`, `samples/dummydata-systemalerts.csv` | Data fixtures, not prose; nothing in the output set derives from them |

Excluding `A` and `P` costs the evaluation nothing, which was checked rather
than assumed: **all 359 concept records draw their `source` spans from `U`, `S`
and `M` only** — no record cites `A` or `P` for provenance. So no definition in
the output set traces to a document outside the test inputs, and the Phase 7
fabrication check (7.3) can resolve every claim against the three inputs above.

## Golden target for step 5.2

**`U` — `samples/blueprint-UCE-shortened.md`.** Step 5.2 says the smallest
file, and at 3,835 words `U` is the smallest of the three. It is also first in
the set's reading order (`glossary.md` → UCE → SBSP → MCL), so the golden is
produced in the order a reader meets it.

One caveat to carry into 5.3, because it changes how the baseline reads:
**smallest by words is not lightest by term load.** `U` carries 82
document-placed records, the most of the three, and 35 of them are defined. The
review-load figures 5.3 measures are therefore an upper-ish bound per word and
a middling one per term; do not scale them to `S` and `M` on word count alone.

The golden is a *triple* (5.2): the restructured document, the glossary slice
holding its shared terms, and the index slice. A restructured document without
its glossary slice cannot demonstrate criterion 1, and the rubric's unit of
assessment is the output set, not a single file.

## Re-baseline rule

A change to any pinned blob above voids the golden and the 5.3 baseline. Both
are **not done** until re-verified against the new blob — the rubric's
source-version binding, applied to the evaluation set.

**Pinned now, re-baselined later** (Nick, 2026-08-04). This is a known
collision, not an oversight: the three `definition-token` findings held in
`registers/waivers.yaml` are dispositioned as source-document defects — a
broken hyphen in `U`, a missing one in `S` and `M` — whose fix waits on the
backlog B-1 source-correction path. Applying those corrections rewrites all
three blobs and voids whatever golden exists at that moment. The ruling is to
pin against today's corpus and re-baseline when B-1 lands, rather than block
Phase 5 on it.

When a re-baseline happens, update the blob column here in the same PR as the
source correction, so the pin never silently lags the corpus.

