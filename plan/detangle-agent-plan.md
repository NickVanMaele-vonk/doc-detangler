# Document Detangling Agent — Project Plan

**Repo:** MTSAM-docs
**Owner:** Nick Van Maele
**Status:** Phases 1–2 complete; all Phase 4 gate decisions (D1–D9) signed off; D10 (continuous change) adopted 2026-07-23. Phase 3 in progress — 3.1 candidate extraction complete, merged candidate list under business review.
**Last updated:** 2026-07-23

---

## 1. Goal

Build a reusable agent or skill that transforms convoluted markdown documents —
dense, detail-first, using terms before defining them — into logically structured
markdown documents that:

- introduce concepts top-down (overview before detail),
- define every term before first use,
- are readable by humans without prior project context.

Representative "bad input" examples: `blueprint-UCE-shortened.md`,
`blueprint-SBSP-shortened.md`, `blueprint-MCL-shortened.md`.

**The output is a living document set, and the tool has two operating
modes.** After delivery the set keeps evolving: the glossary is completed
over time, and users or AI agents may reorder the core documents or add
clarifying paragraphs. The **detangle run** (Phases 5–9) restructures once;
the **steady-state guard** (Phase 10) then keeps the evolving bodies in sync
with each other and with the evolving glossary on every subsequent docs PR.
Decision D10 (research-memo §D10) records the design.

## 2. Constraints (non-negotiable)

| # | Constraint | Enforcement |
|---|-----------|-------------|
| C1 | **No meaning lost.** Every substantive claim in the source must appear in the output. | Verification harness (Phase 7) |
| C2 | **No meaning invented.** Every output claim traces to the source, or is explicitly marked as bridging text. | Verification harness (Phase 7) |
| C3 | **Omissions require human approval.** Any omission is surfaced as an Azure DevOps PR comment; branch policy requires all comments Resolved before merge. | DevOps integration (Phase 8) |
| C4 | **All document updates go through PRs with reviewer approval.** The tool posts findings as PR comments; it never merges. A PR assembles changes relating to similar concepts and may touch any number of documents; it may not change more terms than `param-max-terms-changed-per-PR`. | DevOps integration (Phase 8) |
| C5 | **Bridging/explanatory additions are allowed** but must be visually and mechanically distinguishable from source-derived text. | Rubric (Phase 1) + fabrication check (Phase 7) |
| C6 | **Version-controllable artifacts only.** Concept graph is a plain-text edge list (`concept-graph.yaml`, source of truth); a Mermaid render (`concept-graph.mmd`) is generated from it and displays natively in Azure DevOps (D2: SKOS concept model, Mermaid-compatible view). | Phase 3 |
| C7 | **No meaning weakened.** Numbers, thresholds, units, comparison operators, normative modality (`must` vs `should`), scoping qualifiers, internal codes, regulatory citations, and classification/version metadata are reproduced verbatim wherever their claim survives. A claim may map correctly and still have lost its force — so this is checked mechanically, independent of C1/C2. | Precision check (Phase 6), rubric criterion 5 |
| C8 | **Addressing survives restructuring.** Internal and cross-document references still resolve; section identifiers are preserved or aliased; source contradictions are surfaced for human disposition, never silently harmonised. | Reference check (Phase 6), rubric criterion 6 |
| C9 | **Glossary-first, single definition site.** The output set is five documents. Reading order is `glossary.md` → Doc 1 → Doc 2 → Doc 3; `index.md` sits outside it as a lookup companion. A term used in more than one document is defined in the glossary and only there; a term used in exactly one document is defined in that document. No term is defined twice, and no term is left undefined. | Phase 3 + rubric criteria 1 and 3 |
| C10 | **Reading order and lookup order are separated.** `glossary.md` is ordered topologically so it can be read start to finish; `index.md` is alphabetical and covers every term across the other four documents. The index is generated, contains no definitions, and is verified by regeneration rather than by review. | Phase 3 + rubric criteria 3 and 6 |
| C11 | **Links run forward only; usage data lives in the graph.** Each section links its first use of a glossary term to that term's entry. No document links back to where its terms are used: a glossary defines terms, it does not record usage. Usage locations are graph edges in `concept-graph.yaml`, **derived** from the bodies and regenerated on every change (D10) — dependency edges in the concept records are the only canonical edge data. | Phase 3 + rubric criteria 1 and 6 |
| C12 | **Coherence survives continuous change.** Bodies remain directly editable by humans and AI agents; the price of an edit is an incremental **drift lint** run by branch policy on every docs PR (new orphans, inline redefinitions, use-before-definition, placement-boundary crossings, contradiction candidates, provenance staleness). Addressing is two-layer: tool-stamped section IDs are the identity layer (authors — human or AI — are never asked to create one); content hashes in a generated section map are the change-detection layer; line numbers appear nowhere, and staleness is flagged, never silent. Derived artifacts (usage edges, first-use links, `index.md`, `concept-graph.mmd`, `state/section-map.yaml`, `manifest.yaml`) are regenerated, never hand-maintained. A generated `manifest.yaml` binds the versions of every artifact in the set. | Phase 10 (schema fields land in Phase 3) + rubric criterion 9 |

## 3. Scope

- **Domain:** MTSAM Analytical Layer documentation (MAR surveillance context).
- **Domain glossary:** does not yet exist — building it is Phase 3 and a
  standalone deliverable valuable to the MTSAM project regardless of agent outcome.
  It is the **first document of the output set**, read before the three
  blueprints, and holds the definition of every term used in more than one
  document (C9). It is reader-facing, not a tool artifact, and is subject to
  the full rubric itself.
- **Index:** a fifth document, `index.md` — alphabetical, spanning all four
  others, listing every term with the location of its definition and nothing
  else (C10). Generated, outside the reading order, exempt from
  concept-before-use.
- **Form factor:** undecided — Claude skill vs. standalone pipeline vs. hybrid.
  Decision is Phase 4.

## 4. Key design insight — the concept graph as backbone

The concept dependency graph is not a side feature; it drives the pipeline:

- **Edge model:** directed edges "definition of X uses term Y".
- **Forward reachability:** which downstream concepts use A, and which
  document sections use A — the graph is the single home for usage data, so
  no document carries a usage concordance. This is the impact-analysis query
  run when a definition changes.
- **Backward reachability:** which earlier concepts D depends on.
- **Topological sort** of the graph = the correct concept-introduction order
  across the output set, and the ordering of `glossary.md` itself.
- **Alphabetical projection** of the same term set = `index.md`. One graph,
  two renderings: topological for reading, alphabetical for lookup.
- **Placement** = a computed property, not a judgement: a term used in ≥ 2
  documents is defined in the glossary; a term used in exactly 1 is defined
  in that document (C9).
- **Cycle detection** = genuinely circular definitions that no reordering fixes
  → mandatory human decision. Glossary-first shrinks this problem: cross-document
  cycles collapse into intra-glossary cycles, which reordering *can* fix.
- **Canonical vs derived edges (D10):** dependency edges ("definition of X
  uses term Y", held in the concept records) are canonical data. Usage edges
  ("section S uses term X") are location-sensitive and therefore **derived**:
  regenerated from the bodies on every change, same status as `index.md`.
  Authored usage data would rot on the first reorder.
- **Orphan detection** (terms used but never defined) = a direct convolutedness
  measure of the source.
- **Concept model:** SKOS (concepts, and our project-local "definition of X
  uses term Y" dependency edge, which SKOS itself does not define). ISO 704
  supplies the definition shape and the cycle policy.
- **Storage:** a plain-text edge-list source of truth (`concept-graph.yaml`)
  → clean git diffs, with a Mermaid render (`concept-graph.mmd`) generated
  from it that displays natively in Azure DevOps and GitHub. Decision D2
  (2026-07-21): SKOS concept *model*, Mermaid-compatible *rendering* — chosen
  over Turtle so the graph displays without extra tooling. The exact
  source-of-truth format, and how close it can sit to Mermaid syntax, is
  being confirmed in round-2 research (C2). Mermaid is a compatible view, not
  the sole source of truth.

---

## Phase 1 — Definition of Done (rubric)
Model/effort recommendation: Opus/high

| Step | Description |
|------|-------------|
| 1.1 | Write `definition-of-done.md` with measurable criteria (below). |
| 1.2 | Nick approves or amends. |

**Rubric criteria** (expanded from five to eight during 1.1 — see
`definition-of-done.md` for the normative text):

1. **Concept-before-use** — no term used before its definition appears, in
   the reading order `glossary.md` → Doc 1 → Doc 2 → Doc 3. Shared terms are
   satisfied structurally by the glossary preceding everything; the check
   still bites inside the glossary, inside each document for its local terms,
   and at every first use **per section**, which must link to the glossary
   entry. Links run forward only — documents link to the glossary, never the
   reverse. Cycles
   require a human disposition plus a marked forward reference.
   *Automatically verifiable against the graph.*
2. **Abstraction pyramid** — every document, glossary included, opens with a
   plain-language overview; each section leads with its purpose and moves
   general → specific. The index is reduced to a lead sentence.
3. **Glossary and index completeness** — every domain term has exactly one
   one-sentence plain-language definition, at the site the placement test
   requires (≥ 2 documents → glossary; exactly 1 → that document), and
   exactly one alphabetical index entry resolving to it. Regulator-owned
   terms (MAR, ESMA, FSMA, …) go to a references list instead. Promotion and
   demotion between sites are tracked as term changes.
4. **Losslessness** — every source claim present in the output **set**;
   nothing invented; omissions only with explicit human approval (tracked as
   PR comments). Deduplication and relocation into the glossary are
   explicitly *not* omission, under stated conditions.
5. **Precision preservation** — numbers, thresholds, modality, scoping
   qualifiers, codes, citations, metadata, and house style reproduced
   verbatim. Checked mechanically, independent of the Phase 7 claim mapping.
6. **Reference and metadata integrity** — cross-references still resolve,
   section identifiers survive or are aliased, classification/version blocks
   preserved, source contradictions surfaced rather than harmonised.
7. **Provenance marking** — three categories: *moved* (verbatim, unmarked),
   *derived* (rewritten within an exhaustive list of permitted transforms,
   marked with `<!-- derived:start src="…" -->`), *added* (bridging, marked
   with `<!-- AI addition:start -->` plus a visible `[AI addition]` tag).
   Approved omissions leave an in-document trace.
8. **Reviewability** — a PR assembles changes relating to similar concepts
   and may touch any number of documents; document count is not the unit.
   Two caps bound the review load: `param-max-terms-changed-per-PR` (25) and
   `param-max-comments-per-PR`. Each PR is a moves-only commit
   (machine-verified set-wide, since content legitimately crosses files)
   followed by a text-changes commit — the only thing a human reads.
   Comments are raised per cluster, not per instance. Output ships with a
   move-map, a term-change list, counts, and an exceptions list, so the
   C3/C4 approval is a real review and not a rubber stamp on a near-100%
   diff.

Also fixed in 1.1: a non-goals list (blocking prohibitions), per-criterion
severity and adjudicator, and an interim-done subset per phase — the full
rubric only applies to tool output from Phase 6 onward.

**Added 2026-07-23 (v4, per D10):** a ninth criterion,
**continuous-change coherence** — the drift lint on every docs PR, derived
artifacts verified by regeneration, hash-stable provenance anchors with
visible staleness, manifest coherence, term lifecycle and waiver register.
See `definition-of-done.md` §9.

**Output:** `definition-of-done.md`
**Done when:** Nick signs off, including the parameter values listed in it.
**Status: complete.** Approved 2026-07-21. All parameters set except
`param-low-confidence-threshold`, deferred to measurement in Phase 5.3.

## Phase 2 — Research
Model/effort recommendation: Opus/high

| Step | Description |
|------|-------------|
| 2.1 | Search best practices: technical-writing structure frameworks (Diátaxis, minimalism, progressive disclosure); terminology standards (ISO 704, SKOS concept schemes); requirements-engineering document standards. |
| 2.2 | Search open-source prior art: document-restructuring agents; term/keyphrase extraction libraries; concept-graph tooling; LLM claim-decomposition and claim-verification projects (RAG-evaluation space is the likely home of these). |

**Output:** research memo with links (`plan/research-memo.md`).
**Done when:** Nick has chosen what to reuse.
**Status: complete.** 2026-07-21, three research rounds. Decided: adopt ISO 704
(D1); SKOS model + Mermaid render, `concept-graph.yaml` source of truth (D2);
no TBX (D3); reuse MiniCheck via the MIT Flan-T5-Large/DeBERTa-v3-Large
checkpoint only (D4); reuse Vale for term/acronym rules but build
concept-before-use ourselves (D5); no `language_tool_python` (D6). Components:
pandoc JSON AST for parsing (Marko/mistune ruled out on grid tables), NetworkX
for graph/topo/cycle, `azure-devops` SDK for PR threads. Method: 29148 RTM
frame for coverage; RefD/prerequisite-graph for criterion-1 ordering (low
confidence). **Signed off 2026-07-22:** D7 runtime is **Python**; D9 is
**ontology-first** for the definition layer — structured concept records are
the source of truth, glossary/index/mermaid are generated views. Phase 4's
gating decisions are closed and Phase 3 is unblocked.

## Phase 3 — Glossary + concept graph (MTSAM domain asset)
Model/effort recommendation: Fable or Opus/xhigh

Deliberately sequenced **before** the architecture decision: the graph is an
input to any architecture and de-risks everything downstream.

> **Resolved — D9 settled ontology-first (signed off 2026-07-22).** Steps 3.3
> and 3.5–3.7 no longer *author* `glossary.md`; they populate structured
> concept records (one file per concept) as the source of truth and
> **generate** `glossary.md`, `index.md`, and `concept-graph.mmd` as anchored
> views. The view-generator (with source-map anchors, per §D9) must exist
> before the first review, so reviewers always read markdown, never records.
> D7 (Python) does not gate Phase 3 — Phase 3 produces data, not code. See
> research-memo §D9 for the full decision, including the comment→edit
> round-trip.

> **D10 (2026-07-23) reaches into Phase 3.** The record schema must carry the
> continuous-change fields from the first populated record — `status`
> (lifecycle: candidate → approved → published → deprecated),
> `superseded_by` (renames/deprecated aliases), and source spans anchored by
> **stable section ID + content hash** with the source-doc version they were
> verified against (`verified_against`) — never raw line numbers. Hundreds of
> records are populated in 3.3+; schema retrofits multiply. See research-memo
> §D10.

| Step | Description |
|------|-------------|
| 3.1 | Extract candidate terms from the three shortened files + full Analytical Layer blueprint (UCE, SBSP, MCL, IBEB, CQS, BOA, …). LLM-assisted, human-reviewed. |
| 3.2 | Count each term's document usage and apply the **placement test** (C9): used in ≥ 2 documents → glossary; used in exactly 1 → that document. Placement is computed, not judged. |
| 3.3 | Draft one-sentence definitions per term, sourced from the documents. Flag terms used but never defined (orphans), and terms defined differently in two documents (conflicts — surface, do not reconcile). |
| 3.4 | Build the dependency edge list (`concept-graph.yaml`, source of truth); generate the Mermaid render (`concept-graph.mmd`); run topological sort and cycle detection. ISO 704 §6.5.2 defines the cycle policy (inner/outer circle), §6.4.4 the substitution-principle diagnostic; the self-loop check needs a documented-exception path per §6.5.2's graded prohibition. |
| 3.5 | Assemble `glossary.md`: an overview, then the definitions in **topological order** (`param-glossary-order`), so the glossary reads start to finish without ever meeting an undefined term. No alphabetical section — lookup lives in the index. The glossary is reader-facing and must pass criteria 1, 2, and 3 itself. |
| 3.6 | Generate `index.md`: an alphabetical list of **every** term defined anywhere in the set — glossary or document — each with the location of its definition, plus alias and acronym entries pointing at the same location. Terms only, no definitions. Generated and verified by regeneration, never hand-maintained. |
| 3.7 | Record term **usage locations as graph edges** in `concept-graph.yaml` — which document and section uses which term. Usage data lives in the graph only; the glossary defines terms and does not list where they are used. Forward reachability over these edges is what makes impact analysis possible when a definition changes. Also flag **dead entries**: glossary terms with no use anywhere in the set. **Usage edges are derived data (D10):** extracted from the bodies and regenerable at any time, never hand-maintained — the extraction that produces them here is the same one the steady-state guard re-runs incrementally on every later body edit. |
| 3.8 | Review via PR (Nick, optionally Ivo), within `param-max-terms-changed-per-PR` — the initial glossary will exceed 25 terms, so this lands as a sequence of concept-scoped PRs, not one. |

**Outputs:** `glossary.md`, `index.md`, `concept-graph.yaml` (edge-list
source of truth), `concept-graph.mmd` (Mermaid render)
**Done when:** PRs merged; every cycle, orphan, and conflicting definition has
a human disposition; every term has exactly one definition site and exactly
one index entry resolving to it.

## Phase 4 — Architecture decision
Model/effort recommendation: Opus/high

| Step | Description |
|------|-------------|
| 4.1 | **D9 — canonical home of a definition: DECIDED ontology-first (signed off 2026-07-22).** Structured concept records (one file per concept) are the source of truth; `glossary.md`/`index.md`/`concept-graph.mmd` are generated views with source-map anchors enabling a deterministic comment→edit round-trip; document bodies stay on the moved/derived/added model. Vector/graph DBs rejected as the truth store; NetworkX supplies the algorithms. Fold the C9/C10 framing into the rubric when Phase 3 starts. See research-memo §D9. |
| 4.2 | **D7 — runtime: DECIDED Python (signed off 2026-07-22).** Python-first ecosystem (MiniCheck checkpoints, NetworkX, pandoc filters, `azure-devops` SDK); Node would need ONNX conversion for the verifier. Did not gate Phase 3. See research-memo D7. |
| 4.2a | **D10 — continuous change: ADOPTED (2026-07-23, at Nick's direction).** The set is a living document set; the tool ships two operating modes — the one-shot detangle run and a steady-state guard on every subsequent docs PR. Hash-stable provenance anchors, incremental drift lint, derived-artifact regeneration, `manifest.yaml`, term lifecycle + waiver register, tiered verification cadence. Delivered as Phase 10; schema fields land in Phase 3. See research-memo §D10. |
| 4.3 | Present form-factor options with trade-offs (candidates below). The form factor must serve **both operating modes** (D10): the steady-state guard runs headless from branch policy, which weighs against a pure Claude-skill form. |
| 4.4 | Nick chooses; decision recorded with rationale. |

**Candidate architectures:**

- **A. Claude skill** (SKILL.md) — fastest to build; runs wherever Claude runs;
  weakest at deterministic verification.
- **B. Standalone pipeline** (Python/Node CLI) — deterministic stages
  (term extraction → graph → reorder plan → LLM rewrite → claim verification);
  scriptable into Azure DevOps; more build effort.
- **C. Hybrid** — deterministic scaffolding as scripts, LLM stages via API,
  packaged as a skill that orchestrates them.

**Output:** architecture decision record (ADR).
**Done when:** decision recorded.

## Phase 5 — Evaluation set
Model/effort recommendation: Opus/high

| Step | Description |
|------|-------------|
| 5.1 | Designate the three shortened files as test inputs. |
| 5.2 | Hand-produce (AI-assisted, human-approved) one **golden** restructured output for the smallest file — the reference standard. Because of C9/C10 the golden is a *triple*: the restructured document, the glossary slice holding its shared terms, and the index slice. A golden document without its glossary slice cannot demonstrate criterion 1. |
| 5.3 | **Measure the review load.** Record, for the golden output: claims moved / derived / merged / relocated-to-glossary / added / omitted; terms changed; contradictions, conflicting definitions, and orphans found; and how many exceptions would have become PR comments. This is the first and cheapest real data on reviewability; confirm `param-max-terms-changed-per-PR` and set `param-max-comments-per-PR` and `param-low-confidence-threshold` from it. |

Sizing for reference: the shortened files are 3,800–6,400 words, ~220–270
sentences, and an estimated 350–600 substantive claims each. The full
Analytical Layer blueprint is larger by a factor not yet established.

**Output:** `eval/` folder in repo; measured review-load baseline.
**Done when:** golden output approved by Nick, and the comment and
low-confidence parameters set from 5.3.

## Phase 6 — Prototype
Model/effort recommendation: Opus/high

| Step | Description |
|------|-------------|
| 6.1 | Smallest end-to-end version on one document: graph-driven reorder plan → rewrite → self-report of added / moved / unresolved content. |
| 6.2 | Compare to golden output against the rubric. |

**Done when:** prototype meets rubric on one document, or gaps are documented.

## Phase 7 — Verification harness (losslessness) — DO NOT DEFER
Model/effort recommendation: Fable or Opus/xhigh

| Step | Description |
|------|-------------|
| 7.1 | **Claim decomposition:** split source into atomic claims (LLM-assisted). |
| 7.2 | **Coverage check:** map each source claim to an output location, or flag as omission-pending-approval. |
| 7.3 | **Fabrication check:** trace each output claim to source, or confirm it is marked bridging text. |
| 7.4 | **Structure checks (automatic):** concept-before-use ordering validated against the graph. |

**Output:** verification report per run, committed alongside the document.
**Done when:** harness catches seeded errors — deliberately delete one claim,
invent one claim, and weaken one claim (change a threshold and downgrade a
`must` to a `should`, per C7); the harness must flag all three.

## Phase 8 — Azure DevOps integration
Model/effort recommendation: Opus/high

| Step | Description |
|------|-------------|
| 8.1 | Tool posts findings as PR comments via Azure DevOps REST API: omissions, cycles, contradictions, low-confidence rewrites. Existing branch policy ("comments must be Resolved before merge") becomes the enforcement mechanism for C3. Requires a PAT with Code read/write + PR thread scope (consistent with existing fine-grained PAT practice). |
| 8.2 | **Concept-scoped PRs.** A PR assembles changes relating to similar concepts and may touch any number of documents, glossary included; document count is not the unit. Splitting a term promotion across PRs is forbidden — it would leave a term defined twice or not at all. See DoD 8a. |
| 8.3 | **Two commits per PR:** moves-only, then derived-and-added text. Commit 1 is machine-verified **set-wide** (content line multiset unchanged across the four content documents, since content legitimately crosses files); the reviewer reads commit 2. `index.md` is regenerated, not reviewed. See DoD 8e. |
| 8.4 | **Budgets and aggregation:** a run exceeding `param-max-terms-changed-per-PR` splits along concept boundaries, or fails if it cannot split cleanly (8b). A run exceeding `param-max-comments-per-PR` fails and does not open a PR (8c). Comments are raised per cluster, not per instance (8d). |
| 8.5 | Dry run on a throwaway branch. |

**Done when:** a full pipeline run produces a reviewable PR with resolvable
comments, within both budgets, whose commit 1 passes the set-wide
unchanged-content check.

## Phase 9 — Iterate and package
Model/effort recommendation: Opus/high

| Step | Description |
|------|-------------|
| 9.1 | Run against remaining documents; fix failure modes. |
| 9.2 | Package per Phase 4 decision; write usage documentation. |

**Done when:** all three shortened files pass the rubric via the packaged tool.

## Phase 10 — Steady-state operation (living document set)
Model/effort recommendation: Opus/high

The permanent mode after delivery (D10, C12). The detangle run happens once;
this guard runs forever. It reuses Phase 8's PR plumbing (comment posting,
branch policy, budgets) and Phase 3's extraction.

| Step | Description |
|------|-------------|
| 10.1 | **Two-layer addressing + staleness check.** Identity: every body section carries a tool-stamped `<!-- sec:… -->` marker — a random slug, never ordinal, never heading-derived. Change detection: a generated snapshot `state/section-map.yaml` (ordered section IDs with section and per-paragraph content hashes over the normalised pandoc AST). Record source spans are `(doc, section ID, paragraph hash, verified_against)` — line numbers appear nowhere. CI re-hashes every span; a mismatch flips the record to a visible `provenance: stale` state. **IDs are stamped by the tool only — authors, human or AI, are never asked to create one:** the guard pushes a stamping commit onto the PR branch for unstamped new sections, machine-verified to change nothing but `sec:` markers. See research-memo §D10 element 2. |
| 10.2 | **Incremental drift lint as branch policy.** On every PR touching a body, classify each section against the section map (ID first, hash second): moved → re-run order-sensitive checks only; edited → re-extract that section only; new → extract + stamp; deleted → orphaned-edge and lost-claim checks. A pure reorder costs ~zero. Comment (per cluster, DoD 8d) on new orphans, inline redefinitions, use-before-definition regressions, placement-boundary crossings (promotion/demotion triggers), contradiction candidates, introduced staleness, and ID-hygiene violations (duplicate IDs from copy-paste, missing or malformed markers). Deterministic checks are code; only contradiction candidacy uses a model. Comments block merge via the existing C3 policy — this is the edit contract for humans and AI agents alike. |
| 10.3 | **Derived-artifact regeneration on merge.** Usage edges, first-use links, `index.md`, `concept-graph.mmd`, `state/section-map.yaml`, and `manifest.yaml` regenerate whenever bodies or records change; the regenerate-and-compare guard (D9) extends to all of them. Direct edits to derived artifacts remain forbidden. |
| 10.4 | **Version manifest.** Generated `manifest.yaml`: per-document version, record-set revision, dependency-graph hash, derived-artifact hashes, generation timestamp. The coherence check — "do these five documents + record set belong together?" — becomes mechanical. Version skew (already live: UCE v28 vs v30 citations; MCL v21/v22) becomes machine-checkable state. |
| 10.5 | **Term lifecycle + waiver register.** `status` transitions (candidate → approved → published → deprecated) and `superseded_by` renames; deprecated aliases in body text are flagged as such, not as unknown terms. The waiver register (extending the ISO 704 §6.5.2 documented-exception path) records ticketed orphans/conflicts with an owner, so during incremental glossary completion the lint separates accepted debt from new regressions. |
| 10.6 | **Tiered verification cadence.** Cheap structural lint on every PR (10.2); full C1/C2/C7 harness (Phase 7) at `param-full-verify-cadence` — release tags, not every edit. |
| 10.7 | **Lint test suite — part of the deliverable, not an afterthought.** Mirror the Phase 7 seeded-error pattern: a fixture corpus with one seeded scenario per lint flag type — reorder-only (must flag **nothing** and cost ~zero), typo edit (staleness only), new undefined term, inline redefinition, use-before-definition, placement-boundary crossing, deprecated-alias use, copy-paste duplicate section ID, missing/malformed marker, deleted section with live usage edges, section split, section merge. The guard is not wired into branch policy until every seeded scenario is caught and the reorder-only fixture stays silent. |

**Output:** the guard wired into branch policy; `state/section-map.yaml`;
`manifest.yaml`; waiver register; the lint test suite (10.7, all fixtures
green); steady-state usage documentation.
**Done when:** an ordinary body-edit PR (authored by a human or an AI agent)
that introduces an undefined term, redefines a term inline, or reorders
sections is flagged by the lint before merge; a merge regenerates all derived
artifacts and the manifest; an edit that invalidates a record's source span
produces a visible `provenance: stale` flag; the 10.7 test suite passes —
every seeded scenario flagged, the reorder-only fixture silent; and a
release-cadence run passes the full harness.

---

## Sequencing rationale

1. **Phase 3 before Phase 4:** the glossary and graph are architecture-independent
   inputs and retain standalone value for the MTSAM project even if the agent is
   never completed.
2. **Phase 7 is first-class, not an afterthought:** these documents are the
   authoritative specifications the tool is built from, so restructured
   documents that cannot be proven lossless are unusable — lost or invented
   meaning would propagate into the tool. (The specs are not FSMA-facing; only
   the resulting tool and its later documentation are.) The harness is the item
   most tempting to defer and the one to hold firm on.
3. **Steady-state is designed in from Phase 3, delivered last:** the
   continuous-change schema fields (status, `superseded_by`, hash-anchored
   spans) must exist before hundreds of records are populated — retrofits
   multiply — but the guard itself (Phase 10) lands after the detangle run,
   reusing Phase 8's plumbing. A tool that detangles once and then lets the
   set drift solves half the problem (D10).

## Working agreements (applies to all phases)

- Design decisions are proposed by the assistant; Nick approves before any code
  is written.
- Small sequential steps; verify each before starting the next.
- Never investigate and change in the same step.
- After every code change: concrete list of functional tests to verify.
- Documentation updated after every completed feature.
- No hard-coded values; if required data does not exist yet, stop and ask.
