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

---

## B-3 — Pin pandoc, and record the version the hashes were computed with

**Raised:** 2026-08-04 (Nick), after a CI stall on PR #88.

**The idea.** CI installs whatever pandoc Ubuntu ships, and nothing in the
repository records which pandoc version the record set's `para_hash` values
were computed with. Pin the version explicitly, and state it somewhere the
tool can check.

**What prompted it.** `tests and lint` hung for over seven minutes on
`apt-get install pandoc`, downloading 26.9 MB from `azure.archive.ubuntu.com`,
while the same step in the same run's `detangle validate` job succeeded and
the same step on the previous PR took 13 seconds. A transient mirror stall,
cleared by re-running. The stall is not the problem worth fixing; it is what
made the real one visible.

**Why the version matters.** `para_hash` is *defined* as a sha256 over
`pandoc -f markdown -t plain --wrap=none` output (`concepts/README.md`), so
the pandoc version is part of the provenance contract for all 359 records.
Today it is implicit twice over:

1. **In CI**, the version is whatever `ubuntu-24.04` ships — currently
   `3.1.3+ds-2`. A runner image update that moves pandoc could change the
   plain-text rendering, and every `para_hash` in the set would mismatch at
   once, turning `detangle validate` red with no commit behind it.
   `.github/workflows/ci.yml` already anticipates this in a comment: "a
   provenance failure that appears out of nowhere is almost certainly this."
2. **Locally**, nothing states the expected version at all. `detangle.toml`
   does not record it, and `concepts/README.md` gives the recipe without
   naming the interpreter. A contributor with a different pandoc gets
   hundreds of `para-hash-stale` findings and no explanation. The current
   development environment runs 3.1.3, matching CI by coincidence rather
   than by declaration.

**Candidate fix, in two independent halves.**

- **Pin CI.** `r-lib/actions/setup-pandoc@v2` with `pandoc-version: '3.1.3'`
  fetches the release from GitHub's own CDN — same network as the checkout,
  and not dependent on Ubuntu's mirrors.
- **Declare the contract.** Record the expected version (`detangle.toml`, or
  the `manifest.yaml` of D10 element 5, which already binds derived-artifact
  hashes). `detangle validate` compares `pandoc --version` against it and
  says so plainly on a mismatch, instead of reporting hundreds of stale
  spans. Whether that is a finding or a `state/notices.md` notice is open —
  it is not wrong to run a different pandoc, it is only wrong to trust the
  hashes afterwards.

The second half is the more valuable one and needs no change to CI.

**What makes it non-trivial.**

1. **Debian patches the package.** CI and local both run `3.1.3+ds-2`, not
   upstream `3.1.3`. Switching to the upstream tarball may or may not produce
   identical plain-text output. If it differs, every hash in the set breaks
   simultaneously. **Verify before pinning:** run `detangle validate` under
   both builds and compare, rather than switching and finding out.
2. **A version bump means re-anchoring, not a fix.** If a future pandoc does
   render differently, the remedy is to recompute every `para_hash` in one
   deliberate pass with a recorded rationale — not to loosen the check. That
   is a whole-set PR, well past `param-max-terms-changed-per-PR`.
3. **Two jobs need pandoc, one does not.** `tests and lint` (the fixtures
   shell out to real pandoc, deliberately — stubbing it would test the stub)
   and `detangle validate`. `detangle graph --check` reads YAML only.

**Depends on:** nothing. Both halves are independent of the document bodies
and of each other.

---

## B-4 — `glossary.md`'s sources table lists documents no record draws on

**Raised:** 2026-08-04 (assistant), while verifying the Phase 5 test-input
exclusions for step 5.1.

**What is wrong.** The generated sources table in `glossary.md` is introduced
as "Every source document the entries below draw on, each bound to the git blob
its records were verified against", and then lists all five corpus documents —
including `samples/blueprint-analytical-layer.md` and
`samples/prototype-BC17.md`. Neither is a provenance source for anything:
**all 359 records draw their `source` spans from U, S and M only.** The
generator lists every document in `detangle.toml [documents]` rather than the
documents the rendered entries actually cite.

**Why it matters more than it looks.** The table is the glossary's answer to
the rubric's source-version binding — "`glossary.md` records the version of
every source it draws on". A reader auditing provenance is told to check two
blobs that contribute nothing, and a future reader may reasonably infer that
`A` and `P` content is present in the set. It also mis-states the position on
`P` specifically, which by the 2026-07-26 ruling never counts.

**The fix.** Compute the table from the spans of the records being rendered,
not from the config map — a document appears if and only if some rendered
entry cites it. Config stays the place that says which documents exist and
what their C9 role is; the table says what this file drew on.

**Watch one thing.** The glossary is human-edited from the 2026-08-04 ruling,
so this is a change to seed output that a drift lint will later guard. Fixing
it now, while the file is still exactly what `detangle generate` produced, is
cheaper than after human edits have landed on top.

**Depends on:** nothing. Independent of the document bodies.
