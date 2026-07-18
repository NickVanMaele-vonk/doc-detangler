# Document Detangling Agent — Project Plan

**Repo:** MTSAM-docs
**Owner:** Nick Van Maele
**Status:** Plan approved — execution not started
**Last updated:** 2026-07-18

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

## 2. Constraints (non-negotiable)

| # | Constraint | Enforcement |
|---|-----------|-------------|
| C1 | **No meaning lost.** Every substantive claim in the source must appear in the output. | Verification harness (Phase 7) |
| C2 | **No meaning invented.** Every output claim traces to the source, or is explicitly marked as bridging text. | Verification harness (Phase 7) |
| C3 | **Omissions require human approval.** Any omission is surfaced as an Azure DevOps PR comment; branch policy requires all comments Resolved before merge. | DevOps integration (Phase 8) |
| C4 | **All document updates go through PRs with reviewer approval.** The tool posts findings as PR comments; it never merges. | DevOps integration (Phase 8) |
| C5 | **Bridging/explanatory additions are allowed** but must be visually and mechanically distinguishable from source-derived text. | Rubric (Phase 1) + fabrication check (Phase 7) |
| C6 | **Version-controllable artifacts only.** Concept graph stored as plain-text edge list; rendered views generated from it. | Phase 3 |

## 3. Scope

- **Domain:** MTSAM Analytical Layer documentation (MAR surveillance context).
- **Domain glossary:** does not yet exist — building it is Phase 3 and a
  standalone deliverable valuable to the MTSAM project regardless of agent outcome.
- **Form factor:** undecided — Claude skill vs. standalone pipeline vs. hybrid.
  Decision is Phase 4.

## 4. Key design insight — the concept graph as backbone

The concept dependency graph is not a side feature; it drives the pipeline:

- **Edge model:** directed edges "definition of X uses term Y".
- **Forward reachability:** which downstream concepts use A.
- **Backward reachability:** which earlier concepts D depends on.
- **Topological sort** of the graph = the correct concept-introduction order
  for the restructured document.
- **Cycle detection** = genuinely circular definitions that no reordering fixes
  → mandatory human decision.
- **Orphan detection** (terms used but never defined) = a direct convolutedness
  measure of the source.
- **Storage:** sorted plain-text edge list (YAML or DOT) as source of truth →
  clean git diffs. Mermaid generated from it → renders natively in Azure DevOps.

---

## Phase 1 — Definition of Done (rubric)
Model/effort recommendation: Opus/high

| Step | Description |
|------|-------------|
| 1.1 | Write `definition-of-done.md` with measurable criteria (below). |
| 1.2 | Nick approves or amends. |

**Rubric criteria:**

1. **Concept-before-use** — no term used before its definition appears.
   *Automatically verifiable against the glossary/graph.*
2. **Abstraction pyramid** — document opens with a plain-language overview;
   each section moves general → specific.
3. **Glossary completeness** — every domain term has a one-sentence
   plain-language definition in the glossary.
4. **Losslessness** — every source claim present in output; nothing invented;
   omissions only with explicit human approval (tracked as PR comments).
5. **Bridging text marked** — added explanatory text distinguishable from
   source-derived text via a fixed convention (to be chosen in 1.1, e.g.
   blockquote with a `[bridge]` tag or HTML comment markers).

**Output:** `definition-of-done.md`
**Done when:** Nick signs off.

## Phase 2 — Research
Model/effort recommendation: Opus/high

| Step | Description |
|------|-------------|
| 2.1 | Search best practices: technical-writing structure frameworks (Diátaxis, minimalism, progressive disclosure); terminology standards (ISO 704, SKOS concept schemes); requirements-engineering document standards. |
| 2.2 | Search open-source prior art: document-restructuring agents; term/keyphrase extraction libraries; concept-graph tooling; LLM claim-decomposition and claim-verification projects (RAG-evaluation space is the likely home of these). |
| 2.3 | Write buy-vs-build memo: what we adopt, what we build. |

**Output:** research memo with links.
**Done when:** Nick has chosen what to reuse.

## Phase 3 — Glossary + concept graph (MTSAM domain asset)
Model/effort recommendation: Fable or Opus/xhigh

Deliberately sequenced **before** the architecture decision: the graph is an
input to any architecture and de-risks everything downstream.

| Step | Description |
|------|-------------|
| 3.1 | Extract candidate terms from the three shortened files + full Analytical Layer blueprint (UCE, SBSP, MCL, IBEB, CQS, BOA, …). LLM-assisted, human-reviewed. |
| 3.2 | Draft one-sentence definitions per term, sourced from the documents. Flag terms used but never defined. |
| 3.3 | Build dependency edge list; generate Mermaid render; run topological sort and cycle detection. |
| 3.4 | Review via PR (Nick, optionally Ivo). |

**Outputs:** `glossary.md`, `concept-graph.yaml`, `concept-graph.mmd`
**Done when:** PR merged; every cycle and undefined term has a human disposition.

## Phase 4 — Architecture decision
Model/effort recommendation: Opus/high

| Step | Description |
|------|-------------|
| 4.1 | Present options with trade-offs (candidates below). |
| 4.2 | Nick chooses; decision recorded with rationale. |

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
| 5.2 | Hand-produce (AI-assisted, human-approved) one **golden** restructured output for the smallest file — the reference standard. |

**Output:** `eval/` folder in repo.
**Done when:** golden output approved by Nick.

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
**Done when:** harness catches seeded errors — deliberately delete one claim and
invent one claim; the harness must flag both.

## Phase 8 — Azure DevOps integration
Model/effort recommendation: Opus/high

| Step | Description |
|------|-------------|
| 8.1 | Tool posts findings as PR comments via Azure DevOps REST API: omissions, cycles, low-confidence rewrites, bridging additions. Existing branch policy ("comments must be Resolved before merge") becomes the enforcement mechanism for C3. Requires a PAT with Code read/write + PR thread scope (consistent with existing fine-grained PAT practice). |
| 8.2 | Dry run on a throwaway branch. |

**Done when:** a full pipeline run produces a reviewable PR with resolvable
comments.

## Phase 9 — Iterate and package
Model/effort recommendation: Opus/high

| Step | Description |
|------|-------------|
| 9.1 | Run against remaining documents; fix failure modes. |
| 9.2 | Package per Phase 4 decision; write usage documentation. |

**Done when:** all three shortened files pass the rubric via the packaged tool.

---

## Sequencing rationale

1. **Phase 3 before Phase 4:** the glossary and graph are architecture-independent
   inputs and retain standalone value for the MTSAM project even if the agent is
   never completed.
2. **Phase 7 is first-class, not an afterthought:** for FSMA-facing documentation,
   restructured documents that cannot be proven lossless are unusable. The harness
   is the item most tempting to defer and the one to hold firm on.

## Working agreements (applies to all phases)

- Design decisions are proposed by the assistant; Nick approves before any code
  is written.
- Small sequential steps; verify each before starting the next.
- Never investigate and change in the same step.
- After every code change: concrete list of functional tests to verify.
- Documentation updated after every completed feature.
- No hard-coded values; if required data does not exist yet, stop and ask.
