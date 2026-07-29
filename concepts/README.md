# concepts/ — canonical concept records

Source of truth for the ontology (D9, signed off 2026-07-22). One YAML file
per concept. `glossary.md`, `index.md`, and `concept-graph.mmd` are
**generated views** of these records — never hand-edit a generated artifact.
Records change via PR only, within `param-max-terms-changed-per-PR` (25).

Schema and anchoring rules below were approved by Nick on 2026-07-28
(step 3.3 kickoff).

## Record schema

| Field | Meaning |
|---|---|
| `id` | Stable kebab-case slug; equals the filename |
| `term` | Canonical spelling, verbatim casing (criterion 5) |
| `aliases` | Acronyms and alternative names found in the sources |
| `status` | Lifecycle per D10 §6: `candidate → approved → published → deprecated`. New records start at `candidate`; promotion follows Nick's review |
| `superseded_by` | Record id that replaces this one (renames/deprecations), else `null` |
| `placement` | `glossary` \| `UCE` \| `SBSP` \| `MCL` — computed per C9, never judged |
| `used_in` | Component blueprints using the term: subset of `[U, S, M]`. (A)/(P) never count (Nick's rulings 2026-07-22 / 2026-07-26); they appear in `flags` |
| `definition` | One-sentence definition drafted from the sources (step 3.3). `null` for orphans — never invented (C2) |
| `source` | Provenance spans — see anchoring rules |
| `depends_on` | Canonical dependency edges, "definition of X uses term Y" (D10 §4). Populated at step 3.4 |
| `flags` | `orphan` (used but never defined in U/S/M), `conflict`, `A`, `P` |
| `conflict` | If defined differently in two documents: both spans verbatim, surfaced, never reconciled (C8 / criterion 6) |
| `review` | Nick's human review decision, carried from `work/term-extraction/candidate-terms-merged.md`. Nick's column — the assistant never fills in a decision |
| `notes` | Optional free text for reviewed caveats (naming variants, meaning drift, version skew). Informational only, never machine-processed |

Usage edges ("section S uses term X") are **derived** data (D10 §4) and do
not appear in records.

## Source-span anchoring (interim scheme, approved 2026-07-28)

D10 §2 anchors spans by tool-stamped section ID + content hash, but no
stamping tool exists yet and `samples/` is read-only, so source spans use
**heading-path + hash** — likely permanent for source anchors, since the
source corpus may never be stamped. Line numbers are provenance nowhere.

Each span:

```yaml
- doc: samples/<file>.md
  section: <section label>
  para_hash: sha256:<hash>
  verified_against:
    git_blob: <git blob sha of the sample file when verified>
    stated_version: <the version the document claims for itself, or null>
```

- **`section`** — the nearest preceding *numbered* section heading, verbatim
  (e.g. `"I.1 The Analytical Question"`, `"1.1 MTS Associated Markets ---
  Key Characteristics"`); `"Front matter"` when the span precedes the first
  numbered heading. UCE/MCL use bold-paragraph headings, not `#` headings.
- **`para_hash`** — sha256 over the enclosing pandoc block (paragraph, or
  the whole grid table when the span is a table cell), normalised as:
  `pandoc -f markdown -t plain --wrap=none`, then all whitespace runs
  collapsed to single spaces and trimmed. Hashes are tripwires, never
  pointers (D10 §2): a mismatch means the span needs re-verification
  (`provenance: stale`), not that the record is wrong.
- **`verified_against.git_blob`** — `git rev-parse HEAD:samples/<file>.md`
  at verification time. `stated_version` is the document's self-claimed
  version reproduced verbatim; version skew between documents is data, not
  a bug (criterion 6).
