# Phase 2 — Research Memo

**Status:** Draft — pending Nick's decisions
**Phase:** 2.1 / 2.2
**Last updated:** 2026-07-21
**Method:** fan-out web research with adversarial verification. 21 sources
fetched, 100 candidate claims extracted, 25 verified by 3-vote adversarial
check (2 of 3 refutations kill a claim). 21 confirmed, 4 refuted.

This memo covers what to **follow** (standards, published technique) and what
to **reuse** (self-hostable open-source components) when building the
pipeline. It is not a procurement exercise: we are building the tool.

> **Read the coverage gaps section before acting on this.** Roughly half the
> brief produced no verified finding and must be treated as *unresearched*,
> not as an absence of options.

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

### 2.4 SKOS — concept-scheme serialisation **(model adopted; serialisation is Mermaid, not Turtle — see D2)**

> **Decision D2 overrides the serialisation recommendation below.** We keep
> the SKOS concept *model* and the project-local dependency edge, but serialise
> in a single Mermaid flowchart (`concept-graph.mmd`) that is both source and
> render, not Turtle. The SKOS-limits findings (no dependency edge, cycles
> permitted) still hold and still fall to us to handle.


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

---

## 3. Per-stage mapping

| Stage | Standard / technique | Component to reuse | We build |
|---|---|---|---|
| Term extraction | — | **not researched** | unknown |
| Definition drafting | **ISO 704 §6.2/§6.3** intensional template | — | definition-shape linter |
| Graph serialisation | **SKOS** model, **Mermaid**-compatible view (D2) | Mermaid tooling (round 2) | `concept-graph.yaml` source of truth + generated `concept-graph.mmd` render, local dependency edge |
| Cycle detection | **ISO 704 §6.5.2 + §6.4.4** substitution | **NetworkX** `simple_cycles`/`find_cycle` (unverified); qSKOS/Skosify | exception path + disposition flow |
| Markdown parsing / structure | — | **Marko / mistune** AST (unverified; grid-table round-trip is the deciding test) | section-move logic |
| Topological ordering | **none — refuted** | **NetworkX** `topological_sort` (unverified) | consistent-with-partial-order logic (not a total order) |
| Reorder planning | none | — | **all of it** |
| LLM rewriting | ASD-STE100 technique | Vale (style lint, MIT) | rewriter |
| Claim decomposition | **Wanner et al.** atomicity/coverage/coherence | — | decomposer, fixed + versioned |
| Fabrication checking | — | **MiniCheck** (Apache-2.0) | wrapper, sentence splitting |
| Coverage checking | — | **none exists** | MiniCheck run in reverse |
| Precision preservation (C7) | — | — | token-multiset diff |
| Index generation | — | — | trivial |
| PR integration | — | **not researched** | unknown |

---

## 4. Coverage gaps — treat as unresearched

This round clustered heavily on normative standards and core verification. The
following produced **no verified claim** and must not be read as "nothing
exists":

**Strand A:** ISO 24495-1 plain language · ISO/IEC/IEEE 29148 requirements
traceability across revisions · Information Mapping · minimalism (Carroll) ·
progressive disclosure · ISO 1087 · prerequisite-relation extraction and
prerequisite-aware sequencing · text-reuse and near-duplicate detection

**Strand B:** *all* term-extraction libraries (spaCy, KeyBERT, YAKE, pyate,
TermSuite, LLM-based) · graph libraries and DOT/YAML/Turtle diff ergonomics ·
SKOS tooling at single-corpus scale (Skosmos, VocBench) · most of the
verification field (RAGAS, DeepEval, FActScore code, AlignScore, RefChecker,
SAFE) · dependency-driven reordering prior art in docs/curriculum/legal
drafting · semantic diff and pandoc grid-table round-tripping · Azure DevOps
REST PR-comment-thread integration

Two of these are load-bearing and should be prioritised in a second round:

- **ISO/IEC/IEEE 29148 traceability** — central to the losslessness goal, and
  the closest thing to an existing standard for proving no claim was lost.
- **The prerequisite-graph literature** — now the *only* candidate foundation
  for criterion 1, since ISO 704 was refuted as a basis for ordering.

---

## 5. Claims actively refuted — do not repeat these

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
| D4 | Reuse MiniCheck for fabrication checking? | Yes, subject to checks | **Deferred — needs more info** (round 2, priority D4) |
| D5 | Reuse Vale for mechanical style checking? | Yes | **Deferred — needs more info** (round 2, priority D5) |
| D6 | Accept GPL-3.0-only `language_tool_python`? | Defer | **No** |
| D7 | Runtime | Python, provisional | **Undecided — research further** (round 2, priority D7) |
| D8 | Second research round for the gaps? | Yes | **Yes** — launched 2026-07-21 (run `wiw1vdh4y`) |

### D2 — SKOS model, Mermaid-compatible rendering

Keep the SKOS *concept model* (concepts, plus our project-local "definition
of X uses term Y" dependency edge), and require a **Mermaid-compatible
format** so the graph displays natively in Azure DevOps and GitHub, rather
than Turtle. The two-artifact arrangement is retained: a plain-text edge-list
**source of truth** (`concept-graph.yaml`) with a **Mermaid render**
(`concept-graph.mmd`) generated from it. Mermaid is a compatible *view*, not
the sole source of truth.

Open sub-questions, folded into round 2 (C2):

- Whether the source-of-truth format could itself be Mermaid-native (one
  artifact) without losing the ability to carry typed edges and cycle
  dispositions — or whether keeping a separate data source is the right call.
  This is an open question, **not** a settled collapse to a single file.
- Whether existing SKOS-to-Mermaid or graph-to-Mermaid tooling exists, or the
  conversion is ours to write.

### D6 — note on the reasoning

Recorded as **No**, so `language_tool_python` is out. One clarification for
future licence calls: GPL-3.0 copyleft attaches to distributing the *tool*,
not to the *documents it produces* — the restructured output is not a
derivative work of the checker. The "cannot make the documents public"
concern is real but is a separate matter (document confidentiality), not a
GPL consequence. The decision stands regardless, since we did not need the
component.

### What is now settled for Phase 4 / build

Adopt ISO 704 (D1). SKOS model + Mermaid serialisation, single
`concept-graph.mmd` (D2). No TBX (D3). No `language_tool_python` (D6).
MiniCheck, Vale, and the runtime remain open pending round 2.
