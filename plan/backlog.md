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

---

## B-2 — Stop restating tool-computable counts in normative prose

**Raised:** 2026-08-04, out of an alignment pass over the three top-level
documents (PR #87).

**The idea.** The plan, the README and `CLAUDE.md` restate figures the tool
already computes — record counts, edge counts, defined/undefined splits,
per-document placement. Each is a hand-copied snapshot of a moment. Either
stop carrying them in prose, or let something compare them against live
output.

**What prompted it.** Four figures had drifted by 2026-08-04, none of them
through carelessness at the time of writing:

| Stated | Live | Why it drifted |
|---|---|---|
| 404 `depends_on` edges (×3 places) | 402 | true at PR #67; the 2026-07-31 narrowing rulings dropped two |
| 358 concept records | 359 | a later record landed |
| 104 document-placed defined terms | 94 | C9 limb 2 moved 28 records, 10 of them defined |
| 82 of 173 multi-clause | 81 of 172 | same limb-2 pass |

Every one was correct when written. That is the shape of the problem: these
are not errors, they are facts about a moment, written into documents that
outlive the moment.

**Nick's ruling, 2026-08-04: low priority.** Counts of edges, terms and
similar will vary continuously, and a document set that tracks them exactly
is not worth the machinery. Parked here rather than scheduled.

**The sharper reading, which came out of that ruling.** If the counts vary
continuously, the durable fix is not to police them — it is to **stop putting
volatile numbers in normative prose**. A check that compares prose against
live output keeps the numbers accurate and keeps the underlying habit, which
means it fires forever. Removing the count, or replacing it with a pointer to
where the tool reports it, ends the problem once.

Not every number is volatile, and the distinction matters more than the
mechanism:

- **Volatile** — record counts, edge counts, placement splits, orphan counts.
  These belong in tool output and in `state/notices.md`, not in a plan.
- **Load-bearing** — a figure an argument is built on, like "81 of 172
  records are multi-clause, and 99 cite more than one span, which is the
  laundering surface". Rewriting these silently would make the reasoning look
  as though it were made about numbers nobody had. They should be **dated in
  place**, which is what PR #87 did for the 2026-07-31 session block.

**What makes it non-trivial.**

1. **Telling the two apart is a judgement, not a pattern match.** A regex over
   digits cannot distinguish a status line from a premise.
2. **Any check must be a notice, not a finding.** A stale number in a plan is
   not a build failure, and raising it as one recreates the trap that caught
   the glossary overview gap and `code_quality` — see criterion 9,
   `state/notices.md`.
3. **`CLAUDE.md` is the hard case.** It is read cold by an assistant at the
   start of every session, so a wrong number there propagates into work
   before anyone reads the plan. It is also the file with the most restated
   figures.

**Depends on:** nothing. `detangle validate` and `detangle graph` already
report every figure involved; `state/notices.md` is the natural surface if a
check is ever wanted.
