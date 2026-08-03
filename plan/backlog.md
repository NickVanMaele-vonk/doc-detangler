# Backlog — candidate work, not yet approved

Non-normative. Nothing here is committed to a phase or signed off; entries are
parked ideas with enough context to be picked up cold. The normative documents
remain `plan/detangle-agent-plan.md`, `plan/definition-of-done.md` and
`plan/research-memo.md`. Identifiers here are `B-n` and are stable once minted.

---

## B-1 — Assist human corrections in source documents directly

**Raised:** 2026-07-31 (Nick), out of the five open `definition-token`
findings on `main`.

**The idea.** Detangle flags an issue or ambiguity together with its file and
location; then (1) the human corrects the source document, and (2) marks the
ambiguity as done. The defect is eliminated at its root instead of being
absorbed downstream.

**What prompted it.** Three of the five findings are a token that *is* in the
corpus but in a different surface form — `BOA-archetype` vs "BOA archetype",
`EOD-only` vs "EOD only", and `MEDIUM-INVESTIGATE` vs the OCR-split
`MEDIUM- INVESTIGATE`. Nick's reading: **a hyphen, a space, or a `- ` can be a
source-document typo that does not change the meaning.** The two downstream
remedies both cost something — edit the record to reproduce the damage, or
loosen the validator to normalise across it — where correcting the source
removes the discrepancy for every record that cites the block, now and later.

**What makes it non-trivial.**

1. **It changes the status of `samples/`.** The corpus is currently
   input-never-output. Making it correctable is a policy change and Nick's to
   rule. The boundary has to be drawn explicitly and narrowly: **transcription
   defects are correctable, substantive contradictions are not.** OCR damage,
   split tokens and stray hyphens are transcription. The live contradictions —
   MCL titled v21 carrying a "what is new in v22" block, MCL applying to UCE
   v28 while SBSP cites v30 — are data, and harmonising them is a non-goal
   (criterion 6). A correction facility that cannot tell the two apart becomes
   a harmonisation facility.
2. **Every correction invalidates provenance.** `para_hash` is a hash of the
   block's pandoc-plain rendering and `verified_against.git_blob` pins the
   file, so touching a block breaks both for every record anchored to it. The
   feature is therefore a correct-plus-re-anchor pass, not an edit. Phase 10.1
   already builds the machinery it needs — span re-hashing on CI and a visible
   `provenance: stale` flip — so this lands naturally alongside or after it.
3. **Location must not be a line number.** Per D10, line numbers are
   provenance nowhere. The flag addresses `(doc, section, block hash)`, the
   same triple records use.
4. **"Marks as done" needs somewhere to live.** ~~Either a sibling register
   (`registers/source-corrections.yaml`) or a disposition column on the waiver
   register — decide when the waiver register is designed, not before.~~
   **Decided 2026-08-03, with the waiver register (step 3.9): one register.**
   `registers/waivers.yaml` carries the disposition in its `disposition`
   field — `source-defect` for all three of the findings that prompted B-1 —
   plus `owner`, `ticket` and `review_by`. A sibling register would have
   duplicated the loader, the staleness pass and the partition machinery to
   hold a single value. "Marks as done" is therefore: correct the source, then
   delete the waiver in the same PR, which `waiver-stale` enforces.

**Open questions for whoever picks this up.**

- Does the tool propose the corrected text, or only point at the defect? A
  proposal is more useful and more dangerous; C2 and criterion 5 both argue
  for pointing.
- What happens to a record authored against the pre-correction wording — does
  it re-anchor automatically, or does it go `provenance: stale` and wait for a
  human? (10.1 says stale-and-visible; corrections may deserve the same.)
- Is a correction to `samples/` allowed to land in the same PR as the records
  that re-anchor onto it, or must it be a separate reviewable commit — the
  Phase 8.3 moves-then-text split is the precedent.

**Depends on:** Phase 10.1 (span re-hashing, staleness) for the re-anchor
half. The flag-and-locate half needs nothing that does not already exist —
`detangle validate` produces exactly this information today.

**Amendment, same day (Nick, 2026-07-31).** Point 1 above is largely
overtaken. `samples/` is scaffolding: once the tool exists the sample files
are replaced by the full documents, and those *are* the living set that
humans and AI agents edit — so "input, never output" was a property of a
fixed test fixture, not a standing principle. Two things survive the change.
The transcription-defect versus substantive-contradiction line still has to
be drawn, because a correction facility that cannot tell them apart is a
harmonisation facility (criterion 6) whatever the corpus is called. And the
provenance cost in point 2 shrinks rather than disappears: `git_blob` is
per-file today, so one edit invalidates the blob for all ~190 spans citing
that file, but Phase 10.1 replaces the anchor with `(doc, section ID,
paragraph hash)`, after which an edit invalidates only the sections it
touched. Ruling recorded 2026-07-31: the three findings named above are
source-document defects, fixed later through this path, held as accepted
debt by the waiver register in the meantime (plan step 3.9).
