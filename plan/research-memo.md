# Phase 2 — Research Memo

**Status:** Rounds 1–3 complete. D1–D9 all decided — D7 (runtime) and D9
(ontology-first) signed off by Nick 2026-07-22. Phase 2 closed.
D10 (continuous change / steady-state operation) added 2026-07-23 from
Nick's post-delivery use case — see §D10.
**Phase:** 2.1 / 2.2
**Last updated:** 2026-07-23
**Method:** fan-out web research with adversarial verification (2 of 3
refutations kill a claim).
- **Round 1:** 21 sources, 100 candidate claims, 25 verified → 21 confirmed,
  4 refuted.
- **Round 2:** 28 sources, 123 candidate claims, 25 verified → 22 confirmed,
  3 refuted. Targeted D4/D5/D7 and the round-1 gaps.

This memo covers what to **follow** (standards, published technique) and what
to **reuse** (self-hostable open-source components) when building the
pipeline. It is not a procurement exercise: we are building the tool.

> **Read the coverage gaps section before acting on this.** Roughly half the
> brief produced no verified finding and must be treated as *unresearched*,
> not as an absence of options. Round 2 resolved D4 and D5; **round 3 (lean,
> single-source, not adversarially verified)** returned reusable method for
> the two load-bearing gaps and resolved C5/C6 — see the round-3 addendum
> and §4.

## Round 2 addendum (2026-07-21)

**D4 — MiniCheck: reuse, but only the MIT checkpoints.** Confirmed 3-0: the
repo is Apache-2.0 and installs as a pip library running local in-process
inference (self-hostable, nothing leaves the environment). But the flagship
**Bespoke-MiniCheck-7B weights are CC BY-NC 4.0 — non-commercial**, paid
licence required from Bespoke Labs. The smaller checkpoints under the `lytang`
namespace are **MIT**: **MiniCheck-Flan-T5-Large** (~0.8B, described as the
best sub-1B fact-checker, GPT-4-level) and **MiniCheck-DeBERTa-v3-Large**
(~0.4B). Standardise on one of those, not the 7B — also far lighter to host
(runs on modest GPU/CPU). **Caveat:** the "MiniCheck is dormant" claim was
*refuted* (1-2), so maintenance status is genuinely unverified — we can assert
neither healthy nor abandoned. Verify the RoBERTa checkpoint's weight licence
and each checkpoint's base-model licence before vendoring.

**D5 — Vale: reuse for term rules, but it cannot do concept-before-use.**
Confirmed 3-0: MIT core; enforces controlled-language word rules via
`Vale.Terms` (preferred) and `Vale.Avoid` (banned); the `conditional` check
enforces acronym-definition **co-existence**. Packages vendor offline from a
local dir/zip — no network at lint time. **But `conditional` checks
co-existence in scope, not relative order** — the Vale docs themselves answer
"Not directly" to definition-ordering. So **criterion 1 (concept-before-use)
must be built by us**; Vale cannot enforce it. This confirms round 1's
refutation. Integration is the Go binary as a subprocess. Bundled style
packages (write-good, proselint, Microsoft, Google) carry separate licences —
still unverified.

**D7 — Python (signed off 2026-07-22).** Only one slice was verified: Node
**can** do offline ML inference via **Transformers.js** (server-side, ONNX-only,
inference-only, ~2-4× slower than native). But the claim that Transformers.js
is functionally equivalent to Python `transformers` was **refuted 0-3** — so
Node cannot be assumed to run an arbitrary MiniCheck checkpoint without ONNX
conversion, and the per-stage comparison (term extraction, graph, pandoc,
Azure DevOps client) produced no verified claims. That ONNX-only friction on
the chosen verifier, plus the Python-first ecosystem (MiniCheck checkpoints,
NetworkX, pandoc filters, `azure-devops` SDK), settled it: **Nick chose Python
2026-07-22.**

**C1 datapoint:** KeyBERT is MIT (but pulls sentence-transformers + model
weights with their own licences).

## Round 3 addendum (2026-07-21) — lean, single-source, NOT adversarially verified

Three budget-capped agents (no 3-vote check; ~74k tokens total, deliberately
cheap). **Treat these as leads at lower confidence than rounds 1–2** — verify
before relying on them; do not elevate them to rounds-1–2 confidence.

- **C5 — pandoc grid tables: RESOLVED (build steer).** Marko and mistune are
  CommonMark parsers with **no grid-table support** — they corrupt pandoc
  grid tables. Drive the pipeline off **pandoc's JSON AST**
  (`pandoc -t json` → panflute/Lua filter on `Table` nodes →
  `pandoc -t markdown+grid_tables`), or mask each table as an opaque block and
  restore it verbatim. This rules Marko/mistune out for our corpus — the
  round-1 "deciding test" resolves against them.
- **C6 — Azure DevOps: RESOLVED (reuse a client).** MIT `azure-devops` Python
  SDK `GitClient` wraps PR threads (`create_thread`/`create_comment`/
  `update_thread`), API 7.1; anchor to file+line via `threadContext`; status
  enum `active → fixed/closed`. The merge gate is a **branch policy**, not the
  tool; the PAT needs only **Code Read & Write** (`vso.code_write`), no merge
  scope. Confirms the Phase 8 plan.
- **G1 — ISO/IEC/IEEE 29148: method found.** A **bidirectional Requirements
  Traceability Matrix** — unique ID per requirement, backward (derived-from) +
  forward (coverage) links. Maps directly onto losslessness: give each atomic
  source claim an ID; an unlinked source ID = a dropped claim, an unlinked
  output element = an unsourced addition. A named frame for our coverage and
  fabrication checks. Standard is paywalled; free secondary summaries only.
- **G2 — prerequisite graphs: foundation found (reverses "no external basis").**
  RefD metric (Liang et al. 2015) with released code+data
  (`harrylclc/RefD-dataset`), the **AL-CPL** dataset, R-VGAE unsupervised
  prerequisite-chain learning, and an ACM Computing Surveys 2025 survey.
  Ordering follows from topo-sort / link-prediction on the extracted graph.
  **Licences NOT FOUND** — per-repo due diligence before reuse. **Criterion 1
  now has a candidate external foundation**, at low confidence — the earlier
  "no external basis at all" is softened, not overturned.

---

## 1. Headline findings

### 1.1 The single biggest risk to the project

Published work finds that grounded-factuality metrics are **biased against
heavily paraphrased output and against evidence drawn from distant parts of
the source document** (Godbole & Jia, [arXiv:2501.14883]). Our rewrite stage
produces exactly that: text that is deliberately reordered across the whole
document and rewritten in place.

That means the Phase 7 harness — the thing constraint C1/C2 rests on — is
operating in the regime where the state of the art is documented to be
weakest. A second finding compounds it: GraphCheck ([arXiv:2502.16514], ACL
2025) reports weak out-of-domain generalisation for MiniCheck, and MiniCheck's
own limitations section concedes it.

This does not sink the approach, but it does mean **Phase 7's seeded-error
test is not optional and is not sufficient**. We should extend it: seed errors
into *heavily reordered and rewritten* output specifically, not into
lightly-edited text, or we will measure the harness in a regime it will never
actually run in.

### 1.2 What the standards give us, and what they don't

Three things we hoped a standard would settle — one is settled, two are not:

| Question | Answer |
|---|---|
| How should a definition be shaped? | **Settled by ISO 704.** Adopt it. |
| How should definitional cycles be handled? | **Settled in principle by ISO 704 §6.5.2.** Adopt the policy, build the detector. |
| Does any standard mandate define-before-use ordering? | **No.** Refuted 0–3. Our criterion 1 has no standards backing — it is ours. |

### 1.3 Recommended runtime: Python

Not a strong finding, but every reusable component verified in this round is
either Python (MiniCheck, language_tool_python) or a Go binary invoked as a
subprocess (Vale). Nothing here argues for Node/TypeScript. Treat as a lean,
not a decision — the term-extraction and graph libraries that would most
inform this were not researched.

---

## 2. Strand A — standards and technique to follow

### 2.1 ISO 704 — definition drafting **(adopt)**

Intensional definitions **shall** state the immediate superordinate concept
followed by the delimiting characteristic(s); definitions of nominal
designations begin with a noun, verbal designations with a verb (§6.2, §6.3.3,
§6.3.5; normative "shall"). ISO 704:2022 retains this verbatim.

This gives criterion 3's "one-sentence plain-language definition" a
standards-grounded shape, and part of it is mechanically checkable.

Two verified limits on the check:

- Adjectival designations legitimately begin with gerunds, participles or
  adjectives ("of or relating to…"), so a strict noun-or-verb head test
  produces false positives.
- §6.3.6 requires deciding which concepts are "so basic and familiar that
  they need not be defined". So the parent-concept test must be *"head
  resolves to a known concept **or** is a flagged undefined-by-design
  primitive"*, not hard glossary membership.

Correctness of the characteristics themselves stays editorial (§6.3.2, §6.5).

*Source:* [ISO 704:2009 full text (IPPC-hosted PDF)](https://www.ippc.int/static/media/files/publications/en/2013/06/05/1347459701_TPG_2012_Oct_30_ISO_704_2009(E).pdf) — freely readable. **Cite ISO 704:2022**, the current edition; 704:2009 is withdrawn.

### 2.2 ISO 704 §6.5.2 — cycle policy **(adopt)**

The standard names and prohibits both forms of circularity:

- **inner circle** — self-reference within a single definition → our self-loops
- **outer circle** — "two or more concepts defined by means of each other"
  within a system of definitions → our multi-node cycles

and §6.3.4 (renumbered **§6.4.4** in ISO 704:2022) makes the **substitution
principle** the standard's own diagnostic: a definition is valid if it can
replace the designation in discourse "without loss of or change in meaning".
§6.5.2 states outright that "the substitution principle clearly reveals
repetition and circularity", and works a two-node cycle as an explicit
recursive expansion.

This is a better foundation for our cycle rule than anything we would have
invented. One important qualification: **the inner-circle prohibition is
graded.** Repeating the designation "is not permissible", but using an element
of it "should be avoided as far as possible" and is expressly allowed for an
adjective forming part of the term "provided it is clearly defined elsewhere".
So the self-loop detector needs a documented-exception path, not a hard fail.

ISO specifies no graph model, no edge semantics and no algorithm — the
dependency-graph framing remains ours.

### 2.3 Ordering — **no standard backs criterion 1** *(refuted claim)*

The proposition that ISO 704 mandates a definition-ordering rule mapping onto
a topological order was **refuted 0–3**.

Separately, Diátaxis was verified to be a *classification* scheme, not a
sequencing one. diataxis.fr/map states "it describes a two-dimensional
structure, rather than a list" and explicitly disclaims order. It says nothing
about introducing terms before first use. Its pedagogical heuristic — "all
learning moves… from the concrete and particular, towards the general and
abstract" — is arguably in *tension* with our abstraction-pyramid criterion,
which moves general → specific.

A related proposition, that Diátaxis mode-mixing is a mechanically classifiable
per-section property, was also refuted 0–3.

**Consequence:** criterion 1 and the reorder-planning stage are a build, and we
should stop expecting external validation for them. The nearest candidate
foundations — Information Mapping and the prerequisite-graph literature — were
not researched (see gaps).

### 2.4 SKOS — concept-scheme serialisation **(model adopted; serialisation is a YAML edge list with a Mermaid render, not Turtle — see D2)**

> **Decision D2 overrides the serialisation recommendation below.** We keep
> the SKOS concept *model* and the project-local dependency edge, but serialise
> as a plain-text edge list (`concept-graph.yaml`) with a Mermaid render
> (`concept-graph.mmd`), not Turtle — both generated from the concept records,
> which are the source of truth (D9). The SKOS-limits findings (no dependency
> edge, cycles permitted) still hold and still fall to us to handle.


SKOS is a W3C Recommendation (18 Aug 2009, Miles & Bechhofer), not superseded.
SKOS data are RDF triples encodable in any concrete RDF syntax; **Turtle** is
the git-diff-friendly choice, satisfying constraint C6.

Adopting it means we are not inventing a file format. But three verified limits
matter:

1. **No dependency edge exists in SKOS.** `skos:broader`/`narrower` model
   conceptual *generality* and are explicitly non-transitive;
   `skos:definition` is a documentation *annotation* carrying a literal, not a
   relation between concepts. Our "definition of X uses term Y" edge must be
   **minted as a project-local property** — still inside a standard
   serialisation, not a bespoke format.
2. **SKOS permits cycles.** §8.6.8: "there is no condition requiring that
   `skos:broaderTransitive` be irreflexive", and how an application should
   handle such statements "is not defined in this specification". The working
   group declined irreflexivity deliberately. So the serialisation layer gives
   us **no free cycle rejection** — ISO 704 supplies the policy, we supply the
   detector.
3. In practice `broader`/`narrower` are used loosely for generic, instance and
   partitive links alike, so they will not cleanly carry our semantics anyway.

*Sources:* [SKOS Reference](https://www.w3.org/TR/skos-reference/), [SKOS Primer](https://www.w3.org/TR/skos-primer/), [Baker et al., Key Choices in the Design of SKOS (arXiv:1302.1224)](https://arxiv.org/abs/1302.1224)

### 2.5 TBX / ISO 30042:2019 — glossary format **(consider, do not assume)**

TBX is an existing standardised XML format for terminological data, defining a
metamodel, data categories, two XML styles (DCA/DCT), and — importantly — a
**methodology for defining private dialects**, which require no ISO approval.
So extra fields such as dependency edges are not blocked by the base standard.

Against it, verified:

- **Adoption is weak.** Commentary states TBX "never quite lived up to its
  potential", nominally-supporting vendors failed to interoperate, and
  spreadsheets/CSV remain the practical exchange format.
- **Defining a dialect is non-trivial** — an RNG/XSD over TBX-Core enumerating
  permitted data categories, probably a Schematron for co-constraints, data
  categories drawn from the TBX Master List, ideally a superset of TBX-Basic.
- ISO lists 30042:2019 as **"to be revised"** (ISO/AWI 30042).
- Nothing in the evidence shows TBX defines a dependency or ordering edge
  either.

**Recommendation:** TBX buys us little that Turtle does not, at meaningfully
higher cost, unless external terminology-tool interchange becomes a
requirement. Note it and move on.

*Sources:* [ISO 30042:2019](https://www.iso.org/standard/62510.html), [TBX dialects](https://www.tbxinfo.net/tbx-dialects/)

### 2.6 ASD-STE100 — controlled language **(technique transfers, tooling does not)**

STE's approved-word rules **are** mechanically checkable, via part-of-speech
disambiguation: a word is approved only in a specific POS role. ASD itself
states "each word has only one meaning and is approved with only one part of
speech". The reference implementation does exactly this, pattern-matching POS
tags.

Two hard caveats:

- It is a **recall-favouring heuristic with a documented false-positive rate**,
  not a sound decision procedure; rule-based POS tagging is ~90% accurate.
- **Refuted 0–3:** the claim that the TechScribe STE checker is a self-hostable
  LanguageTool customisation. **Only the technique transfers, not the
  component.**

### 2.7 Style checking components

| Component | Licence | Self-host | Verdict |
|---|---|---|---|
| **Vale** | MIT | Yes — offline by design | **Reuse**, as a subprocess |
| **language_tool_python** | **GPL-3.0-only** | Yes — local Java server | Caution: copyleft |

**Vale** is verified at the artifact, not the marketing page: MIT
(`vale-cli/vale`), actively maintained (v3.15.1, 2026-06-12; 192 releases;
pushed 2026-07-10), and "runs entirely offline… your content is never sent to
a remote server". Caveats: it is a **Go binary invoked as a subprocess, not an
importable library**; `vale sync` makes outbound requests to fetch style
packages, so **vendor styles into `StylesPath`** and lint-time needs no
network; bundled style packages carry separate licences; the canonical repo
moved `errata-ai/vale` → `vale-cli/vale`.

**Refuted 0–3:** that Vale's `conditional` check is the standard mechanism for
enforcing define-before-first-use. **Do not assume Vale gives us criterion 1.**

**language_tool_python** is **GPL-3.0-only** — strong copyleft, versus the
LanguageTool core at LGPL-2.1+. Obligations attach on distribution, so an
internal non-distributed pipeline has weaker practical exposure, but this needs
a deliberate decision. It ships **no STE or ISO 24495-1 ruleset**.

### 2.8 Claim decomposition — published criteria to follow **(adopt the rubric, build the tool)**

Wanner et al., *A Closer Look at Claim Decomposition* (\*SEM 2024) defines
three evaluation criteria — **atomicity, coverage, coherence** — and these map
directly onto our two verification directions:

- **coherence** ("whether a subclaim accurately reflects what is stated in the
  original") → our **fabrication** check
- **coverage** ("cover all parts of the claim") → our **coverage** check

Two findings with direct operational consequences:

1. **Decomposer choice materially moves the scores.** Holding source texts
   constant, seven decomposers produced materially different FActScore values
   and subclaim counts. Therefore: **fix and version the decomposer**, record
   it in the verification report, and treat our numbers as **internally
   comparable only** — never against published FActScore figures.
2. **The criteria are a human rubric with no mechanical guarantee.** The
   authors warn there is "no mechanism to guarantee they are reflected in the
   output" of an LLM decomposer. Atomicity is never formally defined.

*Sources:* [arXiv:2403.11903](https://arxiv.org/html/2403.11903), [ACL Anthology](https://aclanthology.org/2024.starsem-1.13/); follow-on work: [Optimizing Decomposition for Optimal Claim Verification (ACL 2025)](https://aclanthology.org/2025.acl-long.254), DnDScore ([arXiv:2412.13175](https://arxiv.org/abs/2412.13175))

### 2.9 MiniCheck — the one strong reusable verification component **(reuse, with eyes open)**

The best-verified component in this round.

- **Apache-2.0** repo code, **self-hostable**
- Operates on **arbitrary `(document, claim)` pairs** — the API is
  `scorer.score(docs=[...], claims=[...])`, parallel lists, with no
  question/answer field anywhere. Each claim may carry its own evidence
  document. This is what makes it usable for document-pair work rather than
  only QA.
- **MiniCheck-FT5 is 770M parameters and scores 74.7% balanced accuracy on
  LLM-AggreFact against GPT-4's 75.3%** — "more than 400× cheaper". The live
  leaderboard shows self-hostable Bespoke-MiniCheck-7B at **77.4, ranked #1**,
  above Claude-3.5 Sonnet (77.2) and gpt-4o (75.9).

What it does **not** do:

- **It is one-directional.** Aggregation is "supported if and only if there
  exists some document that supports it" — per-claim precision only, no recall
  over the source. **Coverage checking requires running it in reverse
  ourselves.**
- **It does not decompose.** It scores whole sentences; the caller must split.
- Repo activity appears to trail off after the Sept 2024 release — **verify
  maintenance before vendoring**.
- Repo code is Apache-2.0 but **Bespoke-MiniCheck-7B weights carry a separate
  Bespoke Labs licence** — check per checkpoint.
- Plus the paraphrase/long-range bias in §1.1.

*Sources:* [arXiv:2404.10774](https://arxiv.org/html/2404.10774v1) (EMNLP 2024), [github.com/Liyan06/MiniCheck](https://github.com/Liyan06/MiniCheck), [LLM-AggreFact leaderboard](https://llm-aggrefact.github.io/)

### 2.10 Externally-suggested components — **unverified, captured for round 2**

Surfaced 2026-07-21 by a second AI tool asked to propose an architecture, and
recorded here as candidates for the round-2 C-sweep. **None has been through
our adversarial verification** (round 2 is paused). Licence and maintenance
claims below are as-reported / from general knowledge, not vetted this round —
treat them as leads, not facts, and hold them to the same check we applied to
MiniCheck and Vale.

- **NetworkX** — Python graph library; the concrete answer to the
  ordering-engine stage that round 1 left unresearched. Provides
  `topological_sort`, and `simple_cycles` / `find_cycle` /
  `is_directed_acyclic_graph` — the detector our ISO 704 §6.5.2 cycle policy
  needs. Believed BSD-3, mature, widely used. **Strongest of the batch;
  verify licence/maintenance in C2.** Caveat carried from our own criterion 1:
  a topological sort yields a *total* order, but document order need only be
  *consistent with* the graph's partial order — use NetworkX for the sort and
  cycle detection, not as "topo-sort = document order".
- **Marko** / **mistune** — Python Markdown parsers exposing an AST, for
  deterministic heading/section manipulation instead of regex. Candidates for
  the markdown-parsing stage. **Open question for C5: do either round-trip the
  heavily tabular pandoc grid tables in our corpus without loss?** — that is
  the known-hard case, and it is what actually decides this choice.

Also mentioned and **deliberately not adopted:**

- **Flowmark** (LLM-oriented Markdown formatter) — its "smart typography"
  rewrites quotes, dashes and spacing, which collides with C7 (verbatim
  preservation of numbers, codes, citations). If used at all, whitespace/
  wrapping only, never on content characters. Not a fit as described.
- **`llm` CLI / LangChain / LlamaIndex** — orchestration; a Phase 4
  architecture-decision matter, not a Phase 2 component. `llm` fits the
  Unix-pipeline / hybrid candidate and can target self-hosted models.
- **PyMuPDF4LLM** — PDF→Markdown ingestion; only relevant if source originals
  arrive as PDF/Word rather than the pandoc-converted Markdown we already
  have. Low priority.

The proposal these came from omitted losslessness verification, provenance
marking, the PR/review layer, and the five-document set entirely, and its
cycle handling (auto-summarise into an overview) is a non-goal violation for
us. See the conversation review; the components are worth harvesting, the
architecture is not.

### 2.11 Design note — ontology-first definitions (externally suggested; a decision, not adopted)

Surfaced 2026-07-21 by a second AI tool. Unlike §2.10 (components), this is an
*architectural* refinement worth capturing. It correctly observes that C9–C11
are graph properties, not document properties, and agrees with us against the
first tool that cycles must never be auto-resolved.

**The idea:** make the definition itself a structured **graph record with a
source span**, and treat `glossary.md` and `index.md` as **generated views**
of the concept graph, rather than authoring `glossary.md` directly. A concept
record:

```yaml
exposure:
  definition:
    source: [docA.md#L190-L225]   # span back to source text
  depends_on: [position, instrument]
  used_in: [risk-engine.md, fraud-detection.md]
  aliases: [trading exposure]
  classification: business-concept
```

**Why it is attractive:** if the concept record is canonical, three rules we
currently specify separately fall out for free —

- C10's "index is generated" and the dead-entry check become plain graph
  queries;
- the single-definition site becomes structurally impossible to violate
  (one record; glossary entry and citations are views of it);
- the definition's `source` span gives the precision and fabrication
  validators a direct anchor, instead of re-deriving provenance.

**The scope boundary — the reason it is not adopted wholesale.** Its headline
("concept-graph compiler that emits Markdown; never Markdown → AI-rewrite →
Markdown") is right for the *definition layer* and wrong for the *document
bodies*. Our corpus is overwhelmingly non-definitional — scenarios, calibration
tables, doctrine, worked examples, thresholds in prose. That cannot be
regenerated from an ontology without the ontology becoming a verbatim copy of
the document. The workable shape is **two layers**:

- **Definition layer** — ontology-first: definitions are graph records;
  glossary and index are generated views; regeneration, not rewrite; paraphrase
  drift (C1/C2/C7) genuinely avoided here.
- **Body layer** — restructured *source text*, tracked as moved / derived /
  added, graph-driven reorder. Unchanged from the current plan; "never rewrite"
  is unachievable here because reordering and bridging real prose is the point.

**Open decision this raises (for Phase 4, or a rubric amendment):** does the
canonical home of a definition become the **concept record** (glossary
generated from it), or stay the **authored `glossary.md`**? This changes how
the single-definition rule (C9) and the verification anchors are framed. Listed
in §7 as an open item; not decided here.

**Candidate command decomposition** (also from this tool; a Phase 4 skeleton,
each step independently testable):

```
extract-concepts · infer-dependencies · build-graph · detect-cycles ·
generate-glossary · generate-index · regenerate-docs ·
verify-meaning · verify-precision · verify-references · create-pr-comments
```

Keep it, but split `regenerate-docs` into `generate-definition-views` (layer
one, regenerated) and `restructure-bodies` (layer two, moved/derived/added),
per the boundary above.

---

## 3. Per-stage mapping

| Stage | Standard / technique | Component to reuse | We build |
|---|---|---|---|
| Term extraction | — | **KeyBERT** (MIT; deps carry own licences) — one datapoint, rest not researched | unknown |
| Definition drafting | **ISO 704 §6.2/§6.3** intensional template | — | definition-shape linter |
| Graph serialisation | **SKOS** model, **Mermaid**-compatible view (D2) | Mermaid tooling (round 2) | generated `concept-graph.yaml` edge list + generated `concept-graph.mmd` render (the records are canonical), local dependency edge |
| Cycle detection | **ISO 704 §6.5.2 + §6.4.4** substitution | **NetworkX** `simple_cycles`/`find_cycle` (unverified); qSKOS/Skosify | exception path + disposition flow |
| Markdown parsing / structure | — | **pandoc JSON AST** via panflute/Lua (R3); **Marko/mistune ruled out — no grid-table support** | section-move logic on the AST |
| Topological ordering | **none — refuted** | **NetworkX** `topological_sort` (unverified) | consistent-with-partial-order logic (not a total order) |
| Reorder planning | none | — | **all of it** |
| LLM rewriting | ASD-STE100 technique | Vale (MIT) — term/acronym rules only, **not** ordering | rewriter |
| Concept-before-use (C1) | **RefD / prerequisite-graph literature** (R3, low-confidence, licences unchecked) | none — Vale confirmed it cannot | ordering algorithm (RefD baseline + topo sort) |
| Claim decomposition | **Wanner et al.** atomicity/coverage/coherence | — | decomposer, fixed + versioned |
| Fabrication checking | — | **MiniCheck** (repo Apache-2.0; **use MIT Flan-T5-Large / DeBERTa-v3-Large, not CC BY-NC 7B**) | wrapper, sentence splitting |
| Coverage checking | **bidirectional RTM** framing (ISO 29148, R3) | **none exists** | per-claim IDs + MiniCheck run in reverse |
| Precision preservation (C7) | — | — | token-multiset diff |
| Index generation | — | — | trivial |
| PR integration | Azure DevOps REST 7.1 thread model | **`azure-devops` Python SDK `GitClient`** (MIT, R3) | finding→thread mapping; branch policy is the merge gate |

---

## 4. Coverage gaps — treat as unresearched

**Still open after round 2.** Round 2 was aimed squarely at these and closed
D4/D5 plus one C1 datapoint (KeyBERT), but the two load-bearing gaps and most
of the component sweep **still produced no verified claim** and remain
unresearched — not negative findings:

**Closed in round 3 (low confidence — single-source, not adversarially
verified):** G1 (29148 RTM method), G2 (RefD / prerequisite-graph foundation),
C5 (pandoc grid tables → pandoc JSON AST), C6 (Azure DevOps `GitClient`). See
the round-3 addendum. These need a verification pass before being relied on,
but each has a concrete primary source.

**Still genuinely unresearched:**

- graph libraries and Mermaid-serialisation ergonomics (C2) — NetworkX and the
  AST question remain *externally-suggested / partly-resolved*, not fully
  vetted (§2.10)
- rest of the verification field (C3): RAGAS, DeepEval, FActScore code,
  AlignScore, RefChecker, SAFE — and whether any does the **coverage**
  direction (still believed: none does; we build it)
- dependency-driven reordering prior art (C4) — though G2's prerequisite-graph
  work (§Round 3) partly covers this
- most term-extraction libraries (C1): spaCy, YAKE, pyate, TermSuite,
  LLM-based — only KeyBERT has a datapoint

**From round 1, never researched:** ISO 24495-1 · Information Mapping ·
minimalism (Carroll) · progressive disclosure · ISO 1087 · text-reuse /
near-duplicate detection · SKOS tooling at single-corpus scale.

**Recommendation:** research is complete enough to build. Every stage now has
either a component, a method, or an explicit "we build this". The remaining
gaps (C3 coverage-checker field, C1 term-extraction sweep) are best resolved
during Phase 3/6 against the real corpus, not by more desk research. Verify
the round-3 leads (especially G2 licences and the RTM framing) when they are
actually implemented.

---

## 5. Claims actively refuted — do not repeat these

**Round 2 refutations:**

5. MiniCheck is dormant / lightly-maintained (last update Sept 2024). **1-2**
   — so maintenance status is *unverified*, not "abandoned".
6. Transformers.js is functionally equivalent to Python `transformers`. **0-3**
   — Node cannot be assumed to run arbitrary NLI checkpoints without ONNX
   conversion.
7. Vale exposes exactly 11 fixed regex-only check types. **0-3** — do not
   treat the check list as a closed boundary (but ordering is still not among
   them; see §2.7).

**Round 1 refutations:**

1. ISO 704 mandates a topological define-before-use ordering. **0–3.**
2. The TechScribe ASD-STE100 checker is a self-hostable LanguageTool
   customisation. **0–3.**
3. Diátaxis mode-mixing is a mechanically classifiable per-section property.
   **0–3.**
4. Vale's `conditional` check is the standard define-before-first-use
   mechanism. **0–3.**

## 6. Time-sensitivity

- **ISO 704:2009 is withdrawn.** Cite **ISO 704:2022**, with the substitution
  principle at the renumbered **§6.4.4** — otherwise readers land on the wrong
  clause.
- ISO 30042:2019 is flagged "to be revised" (ISO/AWI 30042).
- Vale and language_tool_python metadata were checked within days of
  2026-07-21 and will drift.
- MiniCheck's repo may be dormant; the LLM-AggreFact leaderboard moves.
- Several ISO facts rest on a freely-hosted ISO-licensed PDF and on
  reseller-mirrored abstracts, because iso.org returns 403 to fetchers.

---

## 7. Decisions — recorded 2026-07-21

| # | Decision | Recommendation | **Nick's decision** |
|---|---|---|---|
| D1 | Adopt ISO 704 for definition shape and cycle policy? | Yes | **Yes** |
| D2 | Concept-graph serialisation | SKOS/Turtle + local edge | **SKOS concept model, but a Mermaid-compatible file format** — see below |
| D3 | Adopt TBX for the glossary? | No | **No** |
| D4 | Reuse MiniCheck for fabrication checking? | Yes — via the MIT MiniCheck-Flan-T5-Large or DeBERTa-v3-Large checkpoint, not the CC BY-NC 7B | **Confirmed by Nick 2026-07-21** — MIT checkpoint only |
| D5 | Reuse Vale for mechanical style checking? | Yes for term/acronym rules; it CANNOT do concept-before-use, which we build | **Confirmed by Nick 2026-07-21** |
| D6 | Accept GPL-3.0-only `language_tool_python`? | Defer | **No** |
| D7 | Runtime | Python | **Python — signed off by Nick 2026-07-22** (Python-first ecosystem; Node needs ONNX conversion for the verifier) |
| D8 | Second research round for the gaps? | Yes | **Yes** — launched 2026-07-21 (run `wiw1vdh4y`) |
| D9 | Canonical home of a definition: concept record (glossary generated) vs authored `glossary.md`? | Ontology-first, definition layer only; structured plain-text records as truth, views generated, anchored comment→edit round-trip — full note below | **Signed off by Nick 2026-07-22** — see §D9. **Amended 2026-08-04:** the definition site owns the definition. All 172 definitions become body-canonical, `glossary.md` included — it becomes the fourth editable document rather than a generated view — with the record's `definition` field a derived copy everywhere, conditional on generated start/end markers making the lift deterministic. The record still owns the ontology: identity, placement, provenance, `depends_on`. See §D9 amendment. **Amended 2026-08-05:** two input sets — the read-only reference set may supply definitions, lifted with provenance; see §Two input sets |
| D10 | How does the set stay coherent under continuous post-delivery change (glossary completed over time; bodies reordered/extended by humans and AI agents)? | Two operating modes (detangle run + steady-state guard); hash-stable provenance anchors; derived artifacts regenerated, never hand-maintained; set-level version manifest; term lifecycle — full note below | **Adopted 2026-07-23 at Nick's direction** (the continuous-change use case is a stated requirement) — see §D10. **Element 4 reaffirmed 2026-08-04:** `depends_on` stays canonical; a body edit proposes edge changes and waits for a human ruling |

### D2 — SKOS model, Mermaid-compatible rendering

Adopt the SKOS *concept model* — concepts, plus our project-local "definition
of X uses term Y" dependency edge, which SKOS itself does not define. The
graph is serialised as a plain-text edge list, `concept-graph.yaml`, and
rendered to `concept-graph.mmd`, which displays natively in Azure DevOps and
GitHub. Turtle is rejected: it needs extra tooling to display.

The edge list stays a separate data file rather than collapsing into a single
Mermaid-native artifact, because it carries typed edges — concept→concept
dependency edges and section→concept usage edges — and cycle dispositions,
none of which Mermaid syntax can express.

Both files are generated, in the chain records → `concept-graph.yaml` →
`concept-graph.mmd`. The concept records are the source of truth (D9): the
edge list is a roll-up of their canonical `depends_on` plus usage edges
derived from the bodies (D10, C11). Neither file is hand-edited; hand-edits
are caught byte-wise by the regenerate-and-compare guard and fail CI.

### D6 — note on the reasoning

Recorded as **No**, so `language_tool_python` is out. One clarification for
future licence calls: GPL-3.0 copyleft attaches to distributing the *tool*,
not to the *documents it produces* — the restructured output is not a
derivative work of the checker. The "cannot make the documents public"
concern is real but is a separate matter (document confidentiality), not a
GPL consequence. The decision stands regardless, since we did not need the
component.

### D9 — ontology-first definition layer (decision — signed off 2026-07-22)

Decided 2026-07-22 after reasoning through the **business-user review
workflow** (the lens §2.11 did not apply). Confirmed premise: business users
**read and comment**; they do not hand-edit the store. The tool proposes,
they approve via PR comments (C3/C4).

**Decision: adopt ontology-first for the definition layer only.**
Definitions are the canonical data; `glossary.md`, `index.md`, and
`concept-graph.mmd` are **generated views**. Document *bodies* are unchanged —
restructured source text tracked as moved / derived / added (§2.11's two-layer
boundary).

**Why, not mainly tokens — provability.** If prose is canonical, every
structural guarantee (defined-before-use, single-definition-site, index,
cycles, orphans, impact analysis) rests on an LLM re-parse of prose: fuzzy,
non-deterministic, and repeated every review round. These documents are the
**authoritative specifications the tool is built from** — lost or invented
meaning propagates straight into the tool — so Phase 7 must *prove*
losslessness, and a proof cannot rest on a re-parse. (The specs themselves are
not FSMA-facing; only the resulting tool and its later documentation are.)
Structured-canonical makes C9/C10/C11 structural — impossible to violate
rather than checked-and-hopefully-caught — and makes every graph query
deterministic code (zero tokens, same answer every time). The token saving is
real and recurs across versions, but provability is the headline.

**Storage — structured plain-text records in git; not a database.** The data
is exact, relational, and small (hundreds of terms), and must stay plain-text
and git-reviewable (C6). Therefore:

- **Source of truth:** structured records in git, **one file per concept**
  (`concepts/exposure.yaml`) rather than one monolith — surgical diffs,
  per-concept PR review that matches concept-scoped PRs (DoD-8), fewer merge
  conflicts across versions, and "edit one definition" = change one flat field.
- **Algorithms:** **NetworkX** in memory at runtime (topo sort, `simple_cycles`,
  reachability) — every query a graph DB would give, no server.
- **Views:** generated `index.md`; `glossary.md` authored from 2026-08-04
  (D9 amendment); the Mermaid render produced on demand per concept by
  `detangle graph --mmd <id>` rather than committed as a whole-set file
  (Nick, 2026-08-04 — 359 nodes is a tangle, one concept's neighbourhood
  is two or three boxes).
- **Rejected as the truth store:** *vector DB* — wrong tool; embeddings are
  fuzzy/lossy and cannot topologically sort or guarantee defined-before-use
  (legitimate only as an *extraction-time* synonym/duplicate helper in Phase 3).
  *Graph DB (Neo4j)* — right model, wrong medium; binary store, running server,
  breaks C6 and PR review; NetworkX covers the algorithms at this scale.
  *SQLite* — binary, not git-diff-reviewable; permissible only as a *derived
  cache* rebuilt from the records, never canonical.

**The round-trip — comment → precise edit of the truth.** This is the
mechanism that makes generated-views safe, and it is a required part of the
decision, not an afterthought:

1. **Source-map anchors.** The generator emits, on every human-visible block,
   a machine anchor back to `record-id + field`, e.g.
   `<!-- gen:concept=exposure field=definition src=blueprint-UCE.md#L190-L225 -->`.
   Reviewers never see them; they make the return trip exact.
2. **Resolve location — deterministic, no LLM.** A PR comment pins to a line;
   walk up to the enclosing `gen:` marker → exact record + field. No guessing
   which part of the truth the comment touches.
3. **Propose the value — bounded LLM (or human).** One small call gets only the
   current field, the comment, and the source span, and proposes the new field
   value. Not a glossary re-parse.
4. **Verify before accepting.** Localised-to-a-field edits are checkable: does
   the new definition still trace to its `source` span (C2)? new `depends_on`
   term (orphan check)? re-run topo/cycle on the changed subgraph; forward
   reachability lists affected downstream concepts/docs. Reviewer-supplied facts
   not in source are recorded as `added`/`derived` with the **PR thread** as
   provenance — never laundered to look like source text (a C1/C2/C7 strength).
5. **Regenerate + re-present.** New views, PR (moves commit, then field-level
   text change); reviewer confirms their comment in a fresh readable view.

**Hard cases.** Comments on *computed* regions (order, index, mermaid) carry a
distinct anchor (`gen:computed=…`) and route to the upstream cause (usually a
dependency edge), not to a field. One comment may map to a *set* of records
(per-cluster comments, DoD-8d) — verified as a set within
`param-max-terms-changed-per-PR`. Key off the embedded anchor, **not** the line
number (robust to regeneration reflow). Direct edits to generated files are
**forbidden** initially and caught by a CI regenerate-and-compare guard plus a
visible "GENERATED — comment, don't edit" banner.

**Staging.** Location resolution is deterministic, so the round-trip is precise
even with a human doing step 3. Ship **assisted-manual** first (tool resolves
the anchor, operator confirms the value); automate value-proposal later. The
precision comes from the source map, not the AI.

**Consequences for the plan.**

- **Phase 3 inverts (unblocks it).** Steps 3.3, 3.5–3.7 no longer *author*
  `glossary.md`; they populate concept records and **generate** the glossary,
  index, and mermaid. The build-early requirement: the view-generator (with
  anchors) must exist before the first review, so reviewers always see markdown.
- **Rubric framing.** C9 (single definition site) and C10 (index generated)
  become structural properties of the record set; the verification anchors
  (C7 precision, C2 fabrication) attach to each record's `source` span. Fold in
  as a C9/C10 note when Phase 3 starts; no criterion is weakened.
- **Body layer unchanged.** Moved / derived / added, graph-driven reorder.

**Scope guard:** ontology-first is the *definition* layer only. The corpus is
overwhelmingly non-definitional (scenarios, tables, doctrine, prose thresholds)
and cannot be regenerated from an ontology without the ontology becoming a
verbatim copy of the document. "Never rewrite" applies to definitions, not
bodies.

#### D9 amendment — the definition site owns the definition (Nick, 2026-08-04)

**Ruling, in two steps taken the same day.** The first scoped canonicity to
placement; the second removed the remaining exception, because the glossary
is a definition site too.

- **Document-placed terms — body-canonical, record mirrors.** The definition
  lives in the document body, where it is read and where a person edits it.
  The record carries a **derived copy**, regenerated from the body and
  byte-compared like every other derived artifact; hand-editing the record's
  `definition` field fails CI, which names the document section to edit
  instead. 204 records today, 94 of them defined.
- **`glossary.md` becomes the fourth editable document** (Nick, later the
  same day). It is no longer a generated view. Its 78 definitions are
  canonical in the file, humans edit it directly, and the record mirrors
  them exactly as it does for the other three documents. So **all 172
  definitions are body-canonical** and the record's `definition` field is
  derived everywhere, with no exception left to remember.

**What the record still owns.** D9's scope narrows from "the definition" to
**the concept ontology**: identity (`id`, `term`, `aliases`), placement,
`used_in`, `source` provenance, `depends_on`, `flags`, `conflict`, `review`
and `notes` all stay canonical in `concepts/*.yaml`. Only the definition
*prose* moves. Ontology-first survives; it was never the prose that made
C9/C10/C11 checkable.

**Why the glossary could not stay the exception.** The rubric already calls
it "the first document of the set", subject to all eight content criteria
itself. Leaving it generated meant the one definition site that did not own
its definitions, reachable only by editing a YAML field — which is precisely
the surface the 2026-07-31 session found unusable for the people who own the
domain knowledge. It also left the overview homeless: generated prose the
tool is forbidden to write (C2), in a file no human may edit.

**What is still generated inside it.** `index.md`, `concept-graph.yaml`, the
sources table, the anchors, first-use links, and the entry blocks for terms
promoted into the glossary by a placement change. These are generated regions
inside a human-owned file — the same mixed ownership the other three
documents already carry through section markers and `derived:` blocks.

**Ordering — the tool reorders, and says so (Nick, 2026-08-04).** The
glossary's order is computed, not authored: topological, so it reads start to
finish without meeting an undefined term (`param-glossary-order`). A human
editing in place will append at the bottom or insert alphabetically. So a PR
that leaves the glossary out of topological order receives a **reorder
commit** from the guard, machine-verified to move whole entry blocks and
change no words, and the guard leaves a PR comment saying what it moved and
why. This extends the stamping-commit pattern criterion 9 already authorises
for section IDs.

This narrows the standing prohibition on the guard editing a body, and the
narrowing is stated as a rule rather than an exception: **the guard may make
word-preserving changes, machine-verified to change no words, and must
comment when it does; it may never change meaning.** Rewriting prose the tool
believes is wrong stays forbidden.

**The cost, stated.** D9 chose record-canonical so C9's single definition
site and criterion 1's ordering would be structurally impossible to violate
rather than checked and hopefully caught. An editable glossary can be made to
define a term twice, or to define one that belongs in a document. Those
become findings instead of impossibilities. The condition below is what keeps
them *mechanically* caught on every PR rather than caught in review if
someone notices.

**Why the original decision does not cover these cases.** D9's headline
argument is provability: if prose is canonical, every structural guarantee
rests on an LLM re-parse of prose. That argument holds. It is also why the
amendment carries a condition rather than simply inverting the direction.

D9 was decided when the plan was for the tool to *author* definitions into
their sites. The 2026-07-31 session established that direct markdown editing
stays the norm (C12), that the corpus is overwhelmingly non-definitional, and
that the tool is required for one class only — definitions of glossary-placed
terms, which nobody can reach any other way. A document-local definition is
not in that class: it is one sentence of ordinary prose, in the document a
reader is already in, and routing its edit through a YAML field would make the
tool mandatory for the common case in order to protect a guarantee that the
next clause protects more cheaply.

**Condition — the lift must be deterministic.** The record's copy is only
byte-comparable if the body says exactly where the definition begins and ends.
So a document body delimits each definition it owns with generated markers:

```markdown
<!-- concept:persistence-gate:start -->
The persistence gate caps an alert at MEDIUM-INVESTIGATE unless …
<!-- concept:persistence-gate:end -->
```

Copying the definition into the record is then string-slicing, not
interpretation. C9, C10 and C11 stay structural properties of the record set
exactly as D9 requires, and the `depends_on` edges a definition mints are
computed from a known block rather than from a whole section.

The markers are **generated, never typed by an author** — the same rule D10
element 2 applies to section IDs and criterion 7 applies to `derived:start`
and `AI addition:start`. A marker that depends on a human remembering to write
it is a marker that goes missing exactly where it mattered.

**What does not change.** Placement itself is still computed (C9, two limbs).
`depends_on` stays canonical — see the D10 element 4 note below. The orphan
measure is untouched: the 187 undefined terms have nothing to mirror.

**Timing — prospective, and deliberately so.** The direction flips per
document as each one comes to exist, and for the glossary when the drift lint
that will guard it exists. Today `glossary.md` is generated and held by
`detangle generate --check`, a byte comparison; dropping that guard before
the lint replaces it would leave the file with no guard at all. Until then
every definition lives in its record, the first golden body is seeded from
those records, and the committed `glossary.md` is the seed for the editable
one.

#### Provenance and authorship of definitions (Nick, 2026-08-04)

Settled once `glossary.md` became editable and authored definitions turned
from an edge case into the normal way the 187 undefined terms get filled.

**One field, not two.** Authored text sits in the same `definition` field as
corpus-derived text. The document already distinguishes them — criterion 7
marks a block moved, derived or added — and the record mirrors one marked
block into one string, so a second field would force the lift to choose a
target and reintroduce a judgement into the one step the marker scheme just
made deterministic. Provenance is a **secondary block on the record**, not a
front-and-centre attribute: what a reader needs is the definition as it
stands now, with the history available to query (Nick's framing).

**Two axes, not one enum.** *Anchoring* — is there a source span? — is
separate from *authorship*. A single `corpus`/`human`/`AI` field cannot
express AI-written text sitting inside the corpus, which is this project's
actual situation: `samples/` was AI-assisted and not closely reviewed. So
`source` spans answer anchoring; the provenance block answers authorship —
author, approver, PR, and the set version the text entered at.

**Authored text joins the document set but never acquires a `para_hash`.**
It is fully part of the document from then on; nothing marks it second-class
to a reader. What it never gets is a source span, because a span asserts
*the business wrote this wording at this revision*. If tool output could
acquire one, the next run would read its own output as evidence the business
defined the term — C2's "traces to the source **or** is marked as bridging"
goes circular, and the 187 undefined terms would silently look closed. The
absence of the hash is the mechanism; nothing has to remember to mark
anything. It follows that `flags: [orphan]` survives an authored definition:
orphan records that the *corpus* never defined the term, which stays true
however good the definition someone later writes. Without that, the
convolutedness measure would decay exactly as fast as the work got done.

**Two hashes, two jobs.** `para_hash` answers "did the business write this?"
and applies to corpus-derived text only. The section map's content hash
(element 2 below) answers "has this changed?" and applies to everything,
authored included. Change detection never depended on `para_hash`.

**A provenance claim is asserted against a content hash.** Change the text
and the claim is invalidated until re-established — re-verified against the
source, or re-approved. For authored text that means a rewrite always needs a
human to re-affirm, which is a stronger guard than corpus text carries.

**Breaking corpus provenance auto-demotes.** Editable documents mean someone
will reword a corpus-derived definition, at which point the record's
`para_hash` and `git_blob` assert something false — and that is the *stronger*
false claim, worse than the authored case. The verbatim-run check detects it
exactly. The tool then drops the provenance one rung down criterion 7's
moved → derived → added ladder and comments; it does not block. Demotion
never over-claims, and blocking has the worse failure mode: people stop
fixing typos in definitions and the documents rot around them.

This generalises the guard rule recorded above: **the guard may weaken a
provenance claim on its own; it may never strengthen one.**

**AI may draft; a named human approves.** Criterion 7 calls an invented
definition the highest-risk output the tool can produce, and a term the
corpus never defines has no source to draw on — so an AI draft is the model
reaching for general knowledge and applying it to a specific surveillance
programme. Against that: 187 definitions is not work that gets done by hand,
and an unwritten definition is itself a failure against criterion 3's
end-state invariant. Barring AI drafting would also set a higher bar for the
fix than the source ever met. So drafting is permitted, approval is by a
named human and recorded, and **the draft shows its evidence** — the usages
elsewhere in the corpus it was assembled from, or an explicit statement that
there are none. A definition assembled from six real usages is a different
object from one composed out of background knowledge, and the approver has to
be able to see which they are approving.

#### The definition block is the definitional boundary (Nick, 2026-08-04)

**Ruling: `definition` is not split into definition / illustration / note.**
The marker boundary does that work instead. The definition proper sits inside
`<!-- concept:<id>:start -->` … `:end`; illustrations and consequences are
ordinary document prose outside it. The record mirrors only the block, so it
cannot conflate three things — there is one thing in it by construction.

This retires the field-splitting design sketched on 2026-07-31 without
retiring its diagnosis. The problem was real: of 172 defined records, **81
are multi-clause** and **99 draw on more than one source span**, and the token
check tests a whole definition against the *union* of every span the record
cites, so a span imported for one clause can vouch for another. Narrowing the
checked text to the definition proper removes most of that surface, and
ISO 704 §6.4.4's substitution principle becomes the test for **where the
marker goes** rather than for how to divide a YAML field.

**Consequence — `notes` is a staging post, not a destination.** Thirteen
records park corpus wording in `notes`, moved out of their definitions by the
ISO 704 narrowing pass: `anonymous-quote-driven-market-structure`,
`classification`, `close-window`, `cwps-intra`, `gate`,
`identity-driven-coordination`, `intent-score`,
`mtsam-l-data-limitation-register`, `mwbr-score-levels`,
`otc-bilateral-trading`, `rd03` and the rest. `notes` renders nowhere and
records are not part of the output set, so criterion 4 — evaluated over the
output set — would count that wording as omitted, and the Phase 7 harness
would never see it because it opens documents, not records. **Those clauses
land in document prose beside their definition block when Phase 5 writes the
body** (Nick, 2026-08-04). Their `notes` entries are authoring instructions
in the meantime.

#### Two input sets — detangle set and reference set (Nick, 2026-08-05)

**The ruling.** The tool accepts two input sets. The **detangle set** is the
documents being restructured — the three component blueprints today. The
**reference set** is read-only documents supplying definitions and context —
the full Analytical Layer blueprint `(A)` and the BC-17 prototype spec `(P)`
today, and over time the smaller side documents business users write.
Reference documents are never modified, never restructured, never stamped
with markers, and never produce an output document. They never count toward
placement (C9) or the orphan measure. But **a definition found only in a
reference document is lifted as the definition**: a real provenance span
(`para_hash` + git blob) into the reference file, C2 satisfied because the
business wrote the wording. The term keeps a flag saying the detangle set
itself never defines it, so the convolutedness measure survives the lift.
Both sets are declared in `detangle.toml [documents]` (`components` and
`references`); adding a side document is a config edit, never a code change.

**What this generalizes.** The per-document rulings of 2026-07-22 (`A` is
excluded from the placement count) and 2026-07-26 (`P` never counts;
`(P)`-only terms stay candidate rows) become instances of a rule, and
`concepts/mts-spa.yaml` — defined entirely from `(A)`, full provenance,
`flags: [orphan, A]` — turns out to have been the first lift, legitimized by
`check_invariants` all along. What changes is that the old prohibition "do
not promote `(P)`-only expansions into definitions" is **narrowed, not
repealed**: an expansion or gloss is still not a definition; a genuine
definition in a reference document now is one.

**A third provenance axis.** The 2026-08-04 section above established two
axes: anchoring (is there a source span?) and authorship. This ruling adds a
third, carried by the span itself rather than a new field: **which input set
the span points into**. A detangle-set span supports placement, orphan
accounting and the criterion-4/5 checks; a reference-set span supports only
the definition it anchors. No schema change is needed — the set membership
of `span.doc` is read from `detangle.toml`.

**Canonical home of a lifted definition.** Once lifted into the output set,
the output-set definition site owns it, like every other definition under
the D9 amendment — there is still no exception to remember. The span into
the reference file is **historical provenance**: it records where the
wording came from at lift time, per the standing principle that corpus
provenance is a fact, not a status. A later edit to the lifted definition
demotes the provenance claim down the criterion-7 ladder exactly as for any
Category A/B text; a later change to the reference document itself surfaces
as a stale blob and re-opens verification of the definitions lifted from it.
Reference files are never stamped, so their spans stay on heading-path +
hash anchoring permanently.

**Scope of the D10 edit contract.** "Humans and AI agents may edit bodies
directly" applies to the detangle set and the glossary only. The reference
set sits outside the edit contract: the tool neither edits it nor guards it,
and business users go on writing those documents by whatever process they
already use.

**Correction recorded with this ruling.** Step 5.1 and `eval/README.md`
claimed no record cites `A` or `P` for provenance. Measured against the
records, that was false: 2 records cite `A` and 17 cite `P` under
`source:`, and 10 more cite `P` in `conflict:` blocks. The claim is
corrected in both places in the same PR as this section.

**Known exposure, parked.** The `definition-token` check tests a definition
against the union of every anchored block the record cites, so a reference
span in a mixed-provenance record could vouch for wording claimed against
the detangle set. Per-clause provenance was considered and rejected on
2026-08-04 ("the definition block is the definitional boundary"); the
exposure is recorded in `plan/backlog.md` rather than reopening that ruling.

### D10 — continuous change / steady-state operation (adopted 2026-07-23)

**The use case (Nick, 2026-07-23).** After delivery the document set does not
freeze: (1) the glossary is completed over time; (2) users and AI agents may
reorder the three core documents or add clarifying paragraphs. Different
versions of the documents will coexist. The tool must keep the evolving
bodies in sync with each other and with the evolving glossary — continuous
change is a requirement, not an edge case.

**Assessment that motivated this decision.** D9 makes the *record-set →
views* direction evolution-proof by construction (regeneration, `gen:`
anchors, CI regenerate-and-compare). The exposed flank is the *bodies →
record-set* direction: nothing in D1–D9 detects drift when a body is edited
directly, and the record-to-source provenance is raw line numbers, which the
first reorder silently invalidates. Six gaps were identified; the six design
elements below close them.

**1. Two operating modes.** The **detangle run** (Phases 5–9) is a campaign:
full restructure, full verification. The **steady-state guard** is the
permanent mode afterwards: an incremental check that runs on every ordinary
docs PR via branch policy. Both modes are deliverables; a tool that only
detangles once solves half the problem.

**2. Two-layer addressing — stamped IDs for identity, hashes for change
detection (scheme agreed with Nick 2026-07-23).** Line numbers appear
nowhere. A hash cannot be an address — it self-destructs on the first edit
(the tool would see "paragraph deleted + unrelated paragraph added" and
every pointer would dangle) — so each layer does the one job it is good at:

- **Identity layer — stamped section IDs.** Every body section carries one
  invisible marker under its heading, `<!-- sec:UCE-7f3a -->`: a short
  random slug, **not** derived from the heading text (heading renames must
  not change it — the failure mode of GitHub-style slug anchors) and
  **not** ordinal (reordering must not renumber it). The section is the
  addressing unit: C11 defines usage per section and criterion 1's
  first-use rule is per section. Paragraphs get no IDs — a marker per
  paragraph is comment noise authors would break — they get hashes.
- **Change-detection layer — content hashes in a generated snapshot.**
  `state/section-map.yaml` (derived, committed) records, per document, the
  ordered section IDs, each with a section hash and per-paragraph hashes.
  Hashes are computed over the **normalised pandoc-AST rendering** of each
  block, so a hard-wrap reflow or whitespace change is not an edit. Hashes
  are tripwires, never pointers.
- **Sync on a PR is a three-way match** of the new parse against the
  snapshot — ID first, hash second: same ID + same hash + new position →
  **moved** (re-run order-sensitive checks only: concept-before-use,
  first-use links); same ID + changed hash → **edited** (re-extract that
  section only; paragraph hashes localise the change; affected provenance
  spans go stale); no ID → **new** (full extraction + stamping); ID
  vanished → **deleted** (orphaned-usage-edge and lost-claim checks). A
  pure reorder therefore costs ~zero — every hash matches — and an added
  paragraph costs one section's re-extraction. Git's file diff is only the
  *trigger*; the section map is the identity layer git does not have
  (analogous to git's own rename detection, which is a similarity pass
  layered over content hashes).
- **Usage edges and links store IDs only** — `(term, doc, sec-ID)`, no
  offsets, ever. First-use positions are recomputed from the parsed AST at
  generation time and never persisted, and an unrelated reorder leaves the
  regenerated usage file near-diff-free. Record provenance spans become
  `(doc, section-ID, paragraph-hash, verified_against)`; a CI re-hash
  mismatch flips the record to a visible `provenance: stale` state
  requiring re-verification. Staleness is a first-class state, never
  silent rot — Phase 7's losslessness proof is only as durable as its
  weakest anchor.
- **Authors never create IDs (Nick, 2026-07-23).** Stamping is the tool's
  job, and asking a human or AI author to mint markers is a non-goal. For
  unstamped new sections the guard pushes a **stamping commit** onto the PR
  branch, machine-verified to change nothing but `<!-- sec: -->` markers
  (the content multiset is otherwise unchanged — same verification trick as
  the moves-only commit). This is the one permitted mechanical write to a
  body. **ID hygiene** is a lint class of its own: duplicate IDs (copy-paste
  carries the marker along, giving two sections one identity — the classic
  failure), missing IDs, malformed markers. Section splits resolve as
  edited + new, merges as deleted-with-survivor-found-by-paragraph-hash;
  both are mandatory lint test cases.

**3. Incremental drift lint (the per-PR check).** On every PR that touches a
body: re-extract terms from the changed sections only and diff against the
record set. It flags, as PR comments under the existing C3
resolve-before-merge policy:

- a new term with no definition site (orphan regression);
- an inline (re)definition of an existing term (single-definition-site
  violation, C9);
- a term used before the position its topological order assumes
  (concept-before-use regression, criterion 1);
- a usage count crossing the placement boundary (promotion/demotion trigger,
  criterion 3);
- a candidate contradiction with the current glossary definition
  (LLM-assisted, same machinery as criterion 6 contradiction detection);
- provenance staleness introduced by the edit (element 2);
- an ID-hygiene violation: duplicate, missing, or malformed section
  markers (element 2).

Deterministic checks are code, not LLM calls; only contradiction candidacy
needs a model. This is deliberately cheap — cost tiers are element 6.
**The lint ships with its own seeded test suite** (Nick, 2026-07-23):
mirroring the Phase 7 seeded-error pattern, one fixture scenario per flag
type — plus a reorder-only fixture that must flag *nothing* — and the guard
is not wired into branch policy until all of them pass. See Phase 10.7.

**4. Canonical vs derived edges — usage is derived.** Definition dependency
edges (`depends_on`, "definition of X uses term Y") are **canonical data** in
the concept records. Usage edges ("section S uses term X"), first-use links
in the bodies, `index.md`, `concept-graph.mmd`, the section map
`state/section-map.yaml` (element 2), and the manifest (element 5)
are **derived artifacts**: regenerated from the bodies and records on every
change, never hand-maintained, and covered by the regenerate-and-compare
guard. Anything order- or location-sensitive rots if authored; the reorder
scenario makes first-use positions and usage locations exactly that. This
reframes Phase 3 step 3.7: usage edges are *extracted output that stays
regenerable*, not a hand-kept register.

**Reaffirmed 2026-08-04 (Nick): `depends_on` stays canonical — the tool
proposes edge changes and waits for a human.** The D9 amendment above makes
94 definitions body-canonical, which raised the question of whether their
edges should follow the text and regenerate on every body edit. They do not.
Element 4 stands as written.

The reason is that an edge is a judgement about what a definition is *for*,
and the corpus has already produced pairs a machine cannot separate. Both of
these are trailing clauses of identical shape, ruled opposite ways on
2026-07-31: `close-window → mts-associated-markets` was **dropped** — you do
not need the venue to understand what a close window is — while
`persistence-gate → medium-investigate` was **kept**, because the cap is the
gate's point. An instantiation creates no comprehension prerequisite; a
consequence naming a defined term usually does. Nothing in the text
distinguishes them.

The cost of getting one wrong is not a stray edge. Edges set the glossary's
reading order and answer impact queries, and a placement change can relocate
real text between documents — so a silently minted edge can restructure the
set without anyone having asked. A silently minted *cycle* is worse, and the
existing discipline already says new cycles are surfaced for disposition and
never repaired unilaterally.

So the steady-state flow for a body edit is: extract the candidate edges from
the changed definition block, **diff against the record's canonical
`depends_on`, report the difference, and change nothing**. This matches the
promotion ruling of 2026-07-31 in spirit — the tool detects automatically and
tells the human — and differs in what follows: promotion is mechanical once
the placement test flips, whereas an edge is a claim, so it waits for a
ruling. The detection is automatic; the disposition is Nick's.

**5. Set-level version manifest.** A generated `manifest.yaml` binds the
set: per-document version, record-set revision, dependency-graph hash,
derived-artifact hashes, generation timestamp. It answers "is this doc set
coherent?" mechanically. The failure mode is already live in the corpus (MCL
applies to UCE v28 while SBSP cites v30; MCL's title says v21, its changelog
v22) — under continuous change it multiplies. Records carry the source-doc
version their span was verified against (element 2), so version skew becomes
machine-checkable state instead of archaeology.

**6. Term lifecycle and verification cadence.** The record schema carries a
`status` field (`candidate → approved → published → deprecated`) and
`superseded_by` for renames — old spellings in body text are then flagged as
deprecated aliases, not unknown terms. During incremental glossary
completion, C9's "no term left undefined" is an **end-state invariant**: a
**waiver register** (extending the ISO 704 §6.5.2 documented-exception
pattern already used for cycles) records known, ticketed orphans and
conflicts with an owner, so the lint distinguishes accepted debt from new
regressions — new violations always flag; waived ones don't re-fire.
Verification runs in two tiers: the cheap structural lint on every PR
(element 3); the full C1/C2/C7 harness at release cadence
(`param-full-verify-cadence`), not on every edit.

**The edit contract.** Humans and AI agents may edit bodies directly — bodies
are prose, not generated (D9 scope guard unchanged). The price of a direct
edit is the drift lint: branch policy runs it, and its comments block merge
until resolved, which makes AI agents first-class citizens (they receive
machine-readable PR feedback exactly as humans do). Direct edits to
*generated* artifacts remain forbidden (D9). The moved/derived/added
provenance model applies to tool restructuring runs; ordinary steady-state
body edits are governed by the lint, not by provenance marking.

**Consequences for the plan.**

- **Phase 3 must carry the schema fields from the start** — `status`,
  `superseded_by`, hash-anchored source spans with `verified_against`
  version — because hundreds of records are populated in 3.3+ and schema
  retrofits multiply. Step 3.7 is reframed per element 4.
- **New Phase 10 (steady-state operation)** delivers the guard: two-layer
  addressing and staleness check, drift lint as branch policy,
  derived-artifact regeneration, manifest, lifecycle and waiver register,
  tiered cadence, and the seeded lint test suite (10.7) — the tests are part
  of the deliverable, and the guard is not wired into branch policy until
  they pass. It reuses Phase 8's PR plumbing.
- **New constraint C12** and **rubric criterion 9** state the invariant:
  coherence survives continuous change.
- **New parameter** `param-full-verify-cadence` (DoD parameters table;
  value a proposal until set from steady-state experience).

**Scope guard:** the guard checks and comments; it never auto-fixes bodies
and never merges (C4 unchanged). Regeneration applies only to the derived
artifacts enumerated in element 4.

### What is now settled for Phase 4 / build

Adopt ISO 704 (D1). SKOS concept model + Mermaid-compatible render:
generated `concept-graph.yaml` edge list and generated `concept-graph.mmd`
render, both derived from the concept records, which are the source of truth
(D2). No TBX (D3). Reuse **MiniCheck** for fabrication checking, MIT
Flan-T5-Large / DeBERTa-v3-Large checkpoint only (D4, confirmed). Reuse
**Vale** for term/acronym rules only, not concept-before-use (D5, confirmed).
No `language_tool_python` (D6). Runtime is **Python** (D7, signed off
2026-07-22). Definition layer is **ontology-first** — structured plain-text
concept records as the source of truth, `glossary.md`/`index.md`/`.mmd`
generated as anchored views, comment→edit round-trip per §D9 (D9, signed off
2026-07-22). The set is a **living document set**: two operating modes, with
a steady-state guard on every subsequent docs PR, hash-stable provenance
anchors, derived artifacts regenerated, a version manifest, and a term
lifecycle per §D10 (D10, adopted 2026-07-23). Phase 4's architecture-gate
decisions are closed; Phase 3 is unblocked.
