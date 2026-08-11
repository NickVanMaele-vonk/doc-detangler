# concepts/ — canonical concept records

Source of truth for the ontology (D9, signed off 2026-07-22). One YAML file
per concept. `glossary.md`, `index.md`, and `concept-graph.mmd` are
**generated views** of these records — never hand-edit a generated artifact.
Records change via PR only, within `param-max-terms-changed-per-PR` (200).

**This directory holds only corpus-derived business terms** (Nick's ruling,
2026-07-30). Every file here is a record obeying the schema below, with a
`source` span anchored in `samples/` — no exclusions, so the rule is
mechanically enforceable and records load as a flat `concepts/*.yaml`.

Canonical data that is *not* a corpus term lives in **`registers/`**: human
rulings whose provenance is a PR thread and a standards clause rather than a
source span. Today `registers/cycles.yaml` (cycle dispositions and entry
points, criterion 1), `registers/reference-terms.md` (regulator- and
industry-owned terms, criterion 3) and `registers/waivers.yaml` (findings with
a human disposition but no fix yet, step 3.9). Registers are canonical *inputs*
to generation, never generated.

Do not put a register in here: `concepts/removal-register.yaml` is a genuine
record for the corpus term "Removal Register", so a register file named the
same way would be indistinguishable from a malformed record.

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
| `placement` | `glossary` \| `UCE` \| `SBSP` \| `MCL` — computed per C9, never judged. Two limbs: used in ≥ 2 component blueprints → `glossary`; otherwise depended on by a glossary definition → `glossary` (Case 3, 2026-08-03); otherwise that document. So a record can read `used_in: [U]` with `placement: glossary` and be correct |
| `used_in` | Detangle-set documents using the term: subset of the `components` codes in `detangle.toml [documents]` (`[U, S, M]` today). Reference-set documents never count (Nick's rulings 2026-07-22 / 2026-07-26, generalized 2026-08-05); they appear in `flags` |
| `definition` | One-sentence definition drafted from the sources (step 3.3). `null` for orphans — never invented (C2). A definition found only in a **reference-set** document is lifted with its provenance span (2026-08-05); the `orphan` flag survives the lift, because the flag measures the detangle set |
| `source` | Provenance spans — see anchoring rules. `doc` must be a document registered in `detangle.toml [documents]`, from either set. Each span carries `origin`, its **lineage** (ADR-004 Decision 2) |
| `assurance` | Who vouches for the definition — its **strength** (ADR-004 Decisions 1 and 2b). `null` exactly when `definition` is `null`; otherwise `author` (who produced the wording: `assistant` for text assembled from spans under C2, a person's name for text a human typed), `approved_by` (the named human who verified it, `null` until someone has) and `pr` (where that happened, `null` with no approver). Whether a definition is human-approved is *computed* from `approved_by`, never stored — the rule that keeps `placement` computed. A status of `approved` or `published` may not be reached with `approved_by: null` |
| `depends_on` | Canonical dependency edges, "definition of X uses term Y" (D10 §4). Populated at step 3.4 |
| `flags` | `orphan` (used but never defined in the detangle set), `conflict`, plus any reference-set code (`A`, `P` today) marking informational presence in that document |
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
  origin: corpus | authored
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
- **`origin`** — lineage, one of `corpus` or `authored` (ADR-004 Decision 2,
  Nick 2026-08-07). `corpus` is wording the document already carried when the
  tool first consumed it; `authored` is wording that entered in a later
  version. It deliberately does not say *who* wrote the later text — that is
  the `assurance` block's job, and separating the two is the point of the
  decision. All 597 spans on `main` are `corpus`.

  What this replaces: the absence of a `para_hash` used to carry both "not in
  the original" and "not trustworthy". Decision 1 denies the second — text a
  human writes at v1.2 is as strong as text a human wrote at v1.0 — so an
  authored span now takes a real hash into the version it entered at, and
  re-anchoring is routine rather than forbidden. Lineage still has to be
  recorded, or the fabrication check goes vacuous: in a re-run cycle the input
  is the previous run's output, so without `origin` every claim would trace
  successfully by generation 2, inventions included.

  No hand-typed version string is introduced (the 2026-07-31 ruling):
  `verified_against.git_blob` already pins *which* version.
- **`verified_against.git_blob`** — `git rev-parse HEAD:samples/<file>.md`
  at verification time. `stated_version` is the document's self-claimed
  version reproduced verbatim; version skew between documents is data, not
  a bug (criterion 6).
