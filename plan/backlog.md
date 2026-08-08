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

**CI half done (Nick, 2026-08-05).** The stall recurred on PR #102 — the
same one-job mirror hang, this time killed by the 5-minute step timeout
instead of a human. Nick approved the pin, and the point-1 verification ran
first: the upstream 3.1.3 release binary renders **all 359 records to the
same hashes** as Debian's 3.1.3+ds-2 — `detangle validate` exits 0 under
both — so pinning is hash-safe. `ci.yml` now installs pandoc via
`r-lib/actions/setup-pandoc@v2` pinned to `3.1.3`, from GitHub's own CDN.
The second half — declaring the expected version in `detangle.toml` and
having `validate` compare `pandoc --version` against it — **stays parked**,
including its open finding-vs-notice question.

---

## B-4 — Label the sources table rows by input set

**Raised:** 2026-08-04 (assistant), while verifying the Phase 5 test-input
exclusions for step 5.1. **Rewritten 2026-08-05:** the original entry rested
on a premise that measurement disproved.

**The original complaint, and why it was wrong twice.** The entry claimed
the sources table in `glossary.md` lists documents no record draws on,
because "all 359 records draw their `source` spans from U, S and M only",
and blamed the generator for listing the config map instead of the cited
documents. Both halves are false. The generator already computes the table
from the spans of the records it renders (`views/glossary.py::_sources`).
And the rendered entries genuinely cite all five documents — 2 records cite
`A` and 17 cite `P` under `source:` (`mts-spa`'s definition comes entirely
from `A`). The table was telling the truth; the surprise was the false
belief about the records, which also sat in `eval/README.md` and plan step
5.1 and is corrected there.

**What is still worth doing.** Under the two-input-set ruling (Nick,
2026-08-05 — see research-memo §Two input sets), the table should say which
role each document plays: label each row `component` or `reference`, read
from `detangle.toml [documents]`. A reader auditing provenance then sees
that `A` and `P` supply lifted definitions and context, not detangled
content, without inferring that their bodies are in the set.

**Watch one thing.** The glossary is human-edited from the 2026-08-04
ruling, so this is a change to seed output that a drift lint will later
guard. Fixing it now, while the file is still exactly what `detangle
generate` produced, is cheaper than after human edits have landed on top.

**Depends on:** the two-input-set config change (`references` key in
`detangle.toml`). Independent of the document bodies.

---

## B-5 — A reference span can vouch for detangle-set wording in a mixed definition

**Raised:** 2026-08-05 (assistant), while designing the two-input-set
amendment.

**The exposure.** The `definition-token` check (and the
`min-verbatim-run-chars` tripwire) test a definition against the **union**
of every anchored block its record cites. A record whose definition mixes
detangle-set wording with a reference-set span therefore lets the reference
block vouch for tokens claimed against the detangle set — the same
laundering shape already noted on 2026-07-31 for multi-span records
("a span imported for one clause can launder another"), now reaching across
the input-set boundary. 81 of 172 defined records are multi-clause and 99
cite more than one span, so the surface is real.

**Why it is parked rather than fixed.** The clean fix is per-clause
provenance, which Nick considered and rejected on 2026-08-04 ("the
definition block is the definitional boundary"). The exposure is already
live, but small: exactly three defined records cite spans from both sets
today (`mts-associated-markets`, `mtsam-l-data-limitation-register`,
`quote-behaviour-baseline-engine` — measured 2026-08-05), which is
reviewable by hand. A cheaper partial guard, if wanted later: warn when one
definition cites spans from both input sets, so each new mixed record gets
one human look.

**Depends on:** nothing. Grows with every new definition that cites spans
from both sets.

---

## B-6 — Build `detangle graph --mmd <id>`, the per-concept Mermaid render

**Raised:** 2026-08-05 (assistant), auditing the three normative documents
against the code.

**The gap.** Nick's ruling of 2026-08-04 has two halves. The first — no
whole-set `concept-graph.mmd` is committed, because 359 nodes render as one
238-node tangle plus 108 unconnected dots — is in force. The second, the
replacement, was never built: `detangle graph --mmd persistence-gate` exits
`2` with "unrecognized arguments", and nothing in `src/detangle/` renders
Mermaid at all. `README.md`, `CLAUDE.md` and plan C6/§4 all described the
command as a live capability until this entry was minted; they now say
designed-not-built and point here.

**Why it matters more than a missing convenience.** C6 justifies committing
no diagram by pointing at this command. Until it exists there is no way to
look at the graph at all except by reading `concept-graph.yaml`, which is
exactly the question the render answers — what does this definition rest on,
and what breaks if it changes.

**Shape, from the ruling.** One concept's neighbourhood: the node, its
`depends_on` targets, its dependents, typically two or three boxes and about
eight at one step further out. Printed to stdout for pasting into a PR
comment, where GitHub and Azure DevOps render Mermaid natively. Nothing is
written to disk, so no drift check and no CI gate arise from it.

**Depends on:** nothing. `ConceptGraph` already holds the edges and the
reachability queries `--impact` and `--requires` use.

---

## B-7 — Build the `state/notices.md` generator

**Raised:** 2026-08-05 (assistant), same audit as B-6.

**The gap.** Nick ruled on 2026-08-04 that things worth knowing but not
defects — demotion candidates, review dates falling due, authoring debts —
belong in a generated, committed, deliberately unguarded `state/notices.md`,
carrying a "generated from commit X at time Y" header so it shows visible age
instead of enforcement. Nothing was built: there is no `state/` directory and
no code writes one. The plan listed the file among Phase 3's outputs and
`README.md` listed it among the repo's contents, both as though it existed.

**Why it is worth keeping.** The ruling exists because a notice raised as a
finding makes "nothing is broken" a red build — the trap that already caught
the glossary overview gap and the `code_quality` ruleset entry. Every future
check that wants to say something non-blocking has nowhere to say it until
this exists, so the pressure is to raise a finding instead.

**What has to be decided first.** Which command generates it (a fifth, or a
side effect of `validate`), and what the first entries are — demotion
candidates need the document bodies, and `review_by` dates falling due are
available today from `registers/waivers.yaml`. Unguarded means no
`--check`, no drift pair in `NOT_WAIVABLE`, and no CI job.

**Depends on:** nothing hard. Demotion candidates want Phase 5 bodies; the
waiver review dates do not.

---

## B-8 — Rebase a reorder plan onto a moved source

**Raised:** 2026-08-07 (assistant), with ADR-004 Decision 6.

**The gap.** A reorder plan addresses blocks by content hash and is pinned to
one source blob. `validate_plan` compares the pin against
`git rev-parse HEAD:<doc>` and raises `plan-blob-stale`, so any merged docs PR
invalidates every open plan. Nick ruled the operating rule instead — a re-run
freezes the documents it touches — and this entry parks the automation.

**What it would do.** Re-resolve the plan's block hashes against the moved
source: a block whose normalised text is unchanged keeps its assignment under
its new hash, and the plan is rewritten with a fresh pin.

**Why it was not built.** The coordination cost the freeze imposes has not been
felt yet, so the shape of the real problem is unknown — and one case has no
correct automatic answer. Where an edit *changed* a block rather than moving
it, the plan's intent for that block may no longer hold: the text it was
assigned for may be gone. Rebasing would have to fall back to re-authoring for
exactly the cases that motivate it, so the honest scope is "carry the
unchanged blocks, report the rest", which is a smaller win than it first looks.

**What has to be decided first.** Whether a rebase writes the plan (a
generated edit to a human-authored artifact, which no command does today) or
emits a diff for a human to apply. The second fits ADR-002's rule that the
plan is data a human owns.

**Depends on:** one real re-run, to know how often this actually bites.

---

## B-9 — `detangle verify --use-inference`, the scored half of the harness

**Raised:** 2026-08-07 (Nick), ruling on ADR-003 Decision 5.

**The gap.** `detangle verify` runs deterministically: it places every claim
that moved verbatim, and it checks concept-before-use across the reading
order. Two of the four Phase 7 stages need a model and are absent — the scored
coverage residue (7.2b) and the fabrication check (7.3). So C2's first limb,
"every output claim traces to one of the input sets", is not machine-checked
at all today, and on the `U` golden 66 of 270 source claims are reported
unresolved rather than placed.

**What it would do.** Add a `--use-inference` flag that scores the residue and
the unexplained output claims with the D4 checkpoint — MiniCheck, MIT
checkpoint only (Nick, 2026-07-21). Deterministic stays the default, so the
common path never loads a model.

**Why it was not built.** Nick's ruling of 2026-08-07: run deterministically
for now, and postpone the dependency to the moment the flag is actually
wanted. ADR-003 **Decision 3 is therefore deferred rather than declined** —
the extras group `detangle[verify]` carrying pinned `transformers` + `torch`,
with the checkpoint pinned by revision hash, downloaded and cached, never
committed. ADR-001's tooling list does not cover it, so it needs approval
before any of it is written.

**What has to be decided first.** Decision 3 itself. Two things ride on it
that are worth deciding together: whether the checkpoint download may happen
on first use or must be a separate deliberate step (the command is documented
as "no network"), and what `verify` does when the extra is not installed —
today's answer would be to say so and stay deterministic, never to fail.

**Consequences while it waits.** `verify` raises `coverage-unscored` per
document so a run cannot come back clean about claims it never ruled on, and
the verification report's stage table prints the two absent stages rather than
omitting them. Phase 7's done-when — catching a deleted, an invented and a
weakened claim — cannot be met on the invented-claim limb until this lands.

**Depends on:** Decision 3 being ruled.
