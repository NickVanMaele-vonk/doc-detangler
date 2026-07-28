# Step 3.1 — Merged candidate term list (for human review)

**Status:** LLM-assisted extraction, human-reviewed as required by step 3.1. 

**Sources:** three component blueprints plus two additional documents containing terminology
| Source doc | Abbreviation | Notes |
|---|---|---|
| `blueprint-UCE-shortened.md` | (U) | | 
| `blueprint-SBSP-shortened.md` | (S) | |
| `blueprint-MCL-shortened.md` | (M) | |
| `blueprint-analytical-layer.md` | (A) | read-only reference that may contain explanation of terms, **excluded from the C9 placement test** per Nick's ruling 2026-07-22 | 
| `prototype-BC17.md` | (P) | read-only reference that may contain explanation of terms, not source material; **excluded from the C9 placement test** per Nick's ruling 2026-07-26 |

**Raw per-document extractions** (definition quotes, line spans, aliases, full
notes): `blueprint-*.terms.yaml` and `prototype-BC17.terms.yaml` in this directory. File `candidate-terms-merged.md` is the merge: one row per candidate concept, with per-document presence and computed placement.

**Placement rule (C9):** term used in ≥2 of {U, S, M} → `glossary.md`; term used in
exactly 1 document → defined locally in that document. Documents `A` and `P` never count
toward placement; an `(A)` or `(P)` flag is informational only.

**Why `(P)` is excluded.** `prototype-BC17.md` is a specification of a prototype tool different from the one we're building, but based on the same three core documents (U), (S), (M). It is not part of the detangler input set, so counting it would promote terms to the glossary on the strength of a document no reader of the set will ever see. It is read for **term discovery and definitional evidence only**. Two further cautions apply to anything sourced from it: several of its definitions are its own *proposed corrections* to values the blueprints leave undefined (it says so explicitly — "Correction basis (was undefined `T-095`)"), and its own §0.1 glossary is alphabetical, so it does not
model the ordering criterion 1 requires.

Raw record counts before merging: U ≈ 135, S ≈ 120, M ≈ 130, A ≈ 100, P = 125.
After cross-document identity merging: ~117 glossary candidates, ~150
single-document terms, ~36 regulator-owned terms. **The `(P)` extraction is
partially merged**: Nick reviewed §7a on 2026-07-28 and ruled "keep" — its 20
expansions are promoted into §1 and §3a (four single-document terms) and marked with `(P)` flags. Nick also reviewed §7b on 2026-07-28: `prototype-BC17.md`
sources its definitions from the **complete copies** of `(U)`, `(S)`, `(M)`
— not the `-shortened` files used for this extraction — so a term's absence
from the shortened blueprints is not evidence it is absent from the document
set. On that basis all 22 §7b candidate terms are accepted into the glossary
(§1) and one (HHI) is routed to §2 as externally owned. §7c–§7d remain held
separately pending Nick's review.
A `(P)` in a "Def?" or "Used in" cell is informational only (like `(A)`): the
expansion is sourced from `prototype-BC17.md`, which never counts toward the
mechanical C9 placement test — the §7b promotions are a separate human
ruling, not a C9 pass.

---

## 1. Glossary candidates (used in ≥2 component blueprints)

Grouped thematically. "Def?" = which doc(s) contain an explicit definition
(⊘ = defined nowhere in the three docs — orphan at set level).

### 1a. Product, documents, institutions

| Term | Acronym | Used in | Def? | Notes | Human review decision |
|---|---|---|---|---|---|
| Universal Core Engine | UCE | U,S,M (A) | U (A) | M also calls it "Veridict Core Engine"; version skew: M applies to v28, S cites v30 | Decision: keep |
| Sovereign Bond Sector Pack | SBSP | U,S,M (A) | U,S (A) | Alternatively also "Sector Intelligence Pack" or "Sovereign Government Bond Sector Intelligence Pack" - goal is replace these alternatives by "SBSP" / "Sovereign Bond Sector Pack" | Decision: keep |
| MTSAM Calibration Layer | MCL | U,M (A) | U (A) | Acronym MCL only in filename; alternatively also "Institution Calibration Layer" - a layer of the solution that contains any company-specific definitions and rules, with `MTSAM` being one company |  Decision: keep |
| Veridict MAR Intelligence Platform | — | U,S,M | ⊘ | Vendor/product family; never described |  Decision: `MTSAM Analytical Layer` is master term, `Veridict MAR Intelligence Platform` is only a synonym |
| Document set (Doc 1/2/3 + Doc 6, Doc 7, ECIL Suppl.) | — | U,S,M | ⊘ | "3 of 3" claimed, but Docs 6 & 7 cited — set-extent conflict |  Decision: cull - no business term |
| MTS Associated Markets | MTSAM | U,S,M (A) | M (A) | real definition: legal entity in Belgium; its meaning drifts: venue vs surveilling institution; (A) uses both "Associated" and "Associate" spellings | Decision: keep - it's a legal entity. Use "Associated" spelling as master |
| MTS S.p.A. | MTS | S,M (A) | A | real definition: legal entity in Italy, "Mercato dei Titoli di Stato", sister company of MTSAM; financial markets platform operator; high confusion risk with MTSAM |  Decision: keep |

### 1b. Pipeline objects and units of analysis

| Term | Acronym | Used in | Def? | Notes | Human review decision |
|---|---|---|---|---|---|
| Intraday Behavioural Event | IBE | U,S (A) | U (A) | S never expands IBE; verify IBE≡the object SBSP means (S notes "IBEB near-miss") | Decision: keep |
| Behavioural Episode Consolidation / episode | BEP_E | U,M | U | Episode = analyst review unit; BEP_E never letter-expanded | Decision: keep |
| signal (vs alert) | — | U,M | ⊘ | Doctrinal three-way distinction alert → IBE/signal → episode; never explicitly defined | Decision: keep |
| alert / RT alert | RT | U,S,M (A,P) | ⊘ (P) | RT = **Real-Time** alert, RD = **Reporting-Day** alert per (P) §0.1 — supersedes the earlier "real-time / end-of-day" inference for RD; (P)'s RT set is non-contiguous (RT01, RT02, RT04, RT05, RT08 — RT03/06/07 absent, unimplemented-vs-unmapped unstated) | Decision: keep |
| campaign | — | S,M | ⊘ (partial S) | BPL-owned cross-session construct; named campaign types in S | Decision: keep |
| behavioural primitive | — | S,M (U rel.) | ⊘ | Named instances: QUOTE_WITHDRAWAL, SPREAD_WIDENING, LIQUIDITY_REMOVAL, BLOCK_TRADE, AGGRESSIVE_BUY/SELL, SUSPENSION | Decision: keep |
| QUOTE_WITHDRAWAL | — | S,M | ⊘ | | Decision: keep |
| SPREAD_WIDENING | — | S,M | ⊘ | | Decision: keep |
| LIQUIDITY_REMOVAL | — | S,M | ⊘ | | Decision: keep |
| instrument cluster | — | S,M (A) | ⊘ | Aggregation unit for IBE and dominance shares; rule never given | Decision: keep |
| explanation_trace | — | U,S,M | ⊘ | Canonical explainability artifact; holds anonymity_attribution_basis | Decision: keep |
| classification (NONE/LOW/MEDIUM/HIGH/VERY HIGH) | — | U,S,M (A) | U (A) | U's four-level scale vs A/M five-level (NONE) — reconcile | Decision: keep - use five-level scale as leading |
| MEDIUM-INVESTIGATE | — | U,S,M | ⊘ | Sub-band; U also has MEDIUM-STRUCTURED REVIEW — same? | Decision: keep |
| Aggressor-on-Book / Adverse Outcome Behaviour | AOB | (P) | ⊘ (P) | Carries two competing expansions in the same (P) glossary cell — unresolved even in (P) | Decision: keep — expansion conflict to disposition |
| Participant-Day Risk Profile | PDRP | (P) | ⊘ (P) | Consolidated daily participant object; central to (P)'s own gap C-1 | Decision: keep |
| Participant Session Profile | PSP | (P) | ⊘ (P) | Role text near-identical to PDRP's — possible synonym or undocumented distinction | Decision: keep — disambiguate against PDRP |
| session / participant | — | (P) | ⊘ (P) | session = one trading day; participant = the dealer being assessed | Decision: keep |

### 1c. Scores, gates, engine components

| Term | Acronym | Used in | Def? | Notes | Human review decision |
|---|---|---|---|---|---|
| Convergence Quality Score | CQS | U,S,M (A,P) | ⊘ (P) | Role: summed confirmed evidence across five domains; **unit conflict**: integer bands (U Step 5) vs fractional ≥0.85 (U Step 21) vs additive +0.50 amplifier (S,M) | Decision: keep, refine definition |
| Outcome Score / Outcome Severity | OS | U,S | U | **Expansion conflict**: U implies "Outcome Score", S implies "Outcome Severity" | Decision: keep, refine definition |
| Intent Score | IS | U,M | U | Surface form "IS" dangerously ambiguous | Decision: keep, consider not abbreviating this or abbreviating it differently |
| IScore | — | U,S | ⊘ | Distinct from IS — easy to conflate | Decision: keep, disambiguate |
| PriorityScore | — | U,M | U | | Decision: keep |
| Causality Confidence Layer | CCL | U,M | U | QBCCL looks like a quote-domain variant — relationship unstated | Decision: keep, refine definition |
| Regulatory Risk Factor | RRF | U,M | M (expansion) | U only says "Regulatory Context (RRF)" | Decision: keep |
| EscalationReadiness | — | U,M (A rel.) | U | A has lowercase "escalation readiness" — same concept? | Decision: keep - "escalation readiness" is the human-readable term, "EscalationReadiness" is a software variable name to denote the same |
| Market-Wide Behavioural Reference | MWBR | U,M | U | M never expands | Decision: keep, refine definition |
| Reasonable Suspicion Assessment | RSA | U,M | U | M never expands | Decision: keep |
| MM_SAFEHARBOUR | — | U,M | M | **Conflict: twelve-criteria (U) vs seven-criteria (M) test** | Decision: keep, refine definition |
| Dependency Score / Dependency Filter | DS | U,S | U | U also has DAF vs DependencyFactor — verify same construct | Decision: keep - disambiguate later |
| Structural Relationship Score | SRS | U,M | U | | Decision: keep |
| SCS (and SCS_bpl) | SCS | U,S | ⊘ | Two distinct SCS constructs flagged in U; S has SCS_buyside/sellside family | Decision: keep - disambiguate later |
| ModelConfidence | — | S,M | M (cap rule only) | Relationship to U/M "EvidenceConfidence" unstated | Decision: keep, refine definition |
| SCL (supervisory confidence tier) | SCL | U,M | M (partial) | COMPELLING / PRECAUTIONARY tiers | Decision: keep - disambiguate "tier" from "layer" |
| Coordination Classification Tier | CCT | U,S,M (P) | ⊘ (P) | Expansion from (P) §0.1; blueprints give values EXPLICIT/IMPLICIT, (P) adds a third value STRUCTURAL — value-set difference to disposition | Decision: keep |
| evidence hierarchy | — | U,M | ⊘ | Levels 1–5; collides with many other Level scales | Decision: keep |
| Unified Enriched Event Object | UEEO | S,M (P) | ⊘ (P) | Event/episode data object; expansion + role from (P) §0.1: five-stream fused event record | Decision: keep  |
| Behavioural Objective Assessment | BOA | U,S (A,P) | ⊘ (P) | Expansion + role from (P) §0.1: deterministic risk-objective scoring for HIGH/VERY HIGH. Never expanded in U/S; S notes its enumerated values (BOA=MOMENTUM_IGNITION, …) mirror SB archetype names — potential concept overlap. See §4 item 23 | Decision: keep |
| CRS | CRS | U,S,M | ⊘ | **Expansion conflict**: U "Context Reliability Score" vs S/M usage as relevance/surprise score (CRS_VERY_HIGH) | Decision: keep, refine definition |
| ECIL event relationship states (AMPLIFIES_SUSPICION / CONTRADICTS_PATTERN / SUPPORTS_EXPLANATION / FULLY_EXPLAINED) | — | U,S,M | ⊘ | Membership varies per doc | Decision: keep only `ECIL event` in glossary or definition section (if in one document only) - its possible states are defined in its definition |
| Network Centrality Score | NCS | (P) | ⊘ (P) | Level set LOW/MEDIUM/HIGH/EXCEPTIONAL — a fourth enumerated scale, not a variant of the five-level classification | Decision: keep |
| Temporal Correlation Engine | TCE | (P) | ⊘ (P) | Owns the ECIL event/behaviour timeline mapping | Decision: keep |
| Temporal Correlation Score | TCS | (P) | ⊘ (P) | The one fully-written formula in (P) | Decision: keep |
| Timing Precision Score | TPS | (P) | ⊘ (P) | Banded in the RSA rubric | Decision: keep |
| Outcome Recurrence Score | ORS | (P) | ⊘ (P) | | Decision: keep |
| Outcome Sensitivity Score | OSS | (P) | ⊘ (P) | Instrument-sensitivity multiplier | Decision: keep |
| Block Trade Intelligence Score | BTI | (P) | ⊘ (P) | "composite of **nine** block-trade patterns" — count conflict with BT-01…BT-08 (§1e, eight codes); see conflict P-9 | Decision: keep |
| Follower Rule | — | (P) | ⊘ (P) | Named normative rule: BCI < 3 caps concern at MEDIUM; BCI ≥ 7 opens VERY HIGH | Decision: keep |
| data-availability contract | — | (P) | ⊘ (P) | Binds capability flags to which scores are computable | Decision: keep |

### 1d. Layers and frameworks

| Term | Acronym | Used in | Def? | Notes | Human review decision | 
|---|---|---|---|---|---|
| Behavioural Persistence Layer | BPL | U,S,M | M (expansion) | Components BDS, SCS_bpl, MDCS, CWPS, EDT (U) | Decision: keep |
| External Context Intelligence Layer | ECIL | U,S,M | M (expansion) | Only M expands it | Decision: keep |
| Cross-Instrument Context Intelligence | CICI | S,M | S | Internal Levels 1–3 clash with Four-Level Observability Framework | Decision: keep |
| Cross-Market Convergence Score | CMCS | S,M | S,M | Same formula both docs, but component names differ slightly; drift note in S ("original four-component formula") | Decision: keep |
| Four-Level Observability Framework | — | S,M | S | | Decision: keep |
| quote intelligence architecture (QBRS/QBLI/QBCCL) | — | S,M | M (partial) | "Single most important strategic enhancement dependency" (M) | Decision: keep |
| Quote Behaviour Risk Score | QBRS | S,M (P) | ⊘ (P) | Expansion + role from (P) §0.1: composite quote-domain risk score | Decision: keep - define later  |
| QBLI | QBLI | S,M | ⊘ | Never expanded anywhere | Decision: keep - define later |
| Quote Behaviour Contextual Confidence Layer | QBCCL | S,M (P) | ⊘ (P) | Expansion + role from (P) §0.1: contextual sensitivity multiplier | Decision: keep - define later  |
| Quote Behaviour Baseline Engine | QBBE | U,S,M (P) | M (functional), (P) | Letter-expansion + role from (P) §0.1: participant quote baselines | Decision: keep - define later  |
| Participant Order Flow Profile | POFP | S,M (P) | ⊘ (P) | Participant-own-baseline engine; expansion + role from (P) §0.1: per-participant behavioural baseline (mean + σ). Note (P) lookback discrepancy in §7e (90 days / 15 sessions code vs 45 days / 10 sessions methodology) | Decision: keep - define later  |
| RDCS (RT–RD cross-pass scoring) | RDCS | S,M | M | S never expands | Decision: keep - define later |
| Multi-Day Conditioning Score | MDCS | U,S,M (P) | ⊘ (P) | Expansion + role from (P) §0.1: pre-positioning across sessions | Decision: keep - define later  |
| Cross-Window Persistence Score | CWPS | U,S,M (P) | ⊘ (P) | _cross/_intra variants; expansion + role from (P) §0.1: same pattern across OPEN/CLOSE windows or sessions | Decision: keep - define later  |
| Quote Depth Share Position | QDSP | S,M (P) | ⊘ (P) | Expansion + role from (P) §0.1: share of visible book depth | Decision: keep - define later  |
| Participant Liquidity Contribution Score | PLCS | S,M (P) | ⊘ (P) | Expansion + role from (P) §0.1: net liquidity provided vs removed | Decision: keep - define later  |
| Spread Rationality Indicator | SRI | S,M (P) | ⊘ (P) | Expansion + role from (P) §0.1: economic rationality of spread crossing; see conflict P-12 (§7c: SRI both unavailable under gap MTSAM-L07 and consumed by (P)'s RSA rubric) | Decision: keep - define later  |
| QML (Quote Market Leadership) | QML | S,M | S (inline expansion) | | Decision: keep |
| IPI | IPI | S,M | ⊘ | Never expanded anywhere | Decision: keep - define later |
| Historical Quote Lifecycle Dataset | HQLD | U,S,M (P) | ⊘ (P) | Gate for quote intelligence & BCI D1/D2; expansion + role from (P) §0.1: quote-level history | Decision: keep - define later  |
| Behavioural Drift Score | BDS | U,S (P) | ⊘ (P) | BPL component; also near-collision with BDRS (U); expansion + role from (P) §0.1 (slow drift of behaviour from own baseline) — consistent with §4 item 27 ruling | Decision: keep - define later  |
| ISGO | ISGO | U,S,M | ⊘ | **Role conflict**: S = narrative/output object with mandatory language; M = gap-finding register (ISGO-02) | Decision: keep - define later |
| Quote Cancellation Ratio | QCR | (P) | ⊘ (P) | One of the few (P) glossary rows carrying a formula | Decision: keep |
| Quote Lifetime Score | QLS | (P) | ⊘ (P) | Unavailable in this deployment (gap MTSAM-L02) | Decision: keep |

### 1e. Alert codes and windows

| Term | Used in | Def? | Notes | Human review decision |
|---|---|---|---|---|
| RT/RD alert taxonomies | S,M (A) | S (counts), M (list) | S: 25 RT + 15 RD codes; M: 9 implemented of ~30 — count conflict to disposition | Decision: keep - refine later |
| RT01 Momentum ignition | S,M | M | Collides with SB-01 "Momentum Ignition" archetype (S) — alert vs archetype | Decision: keep |
| RT04 Price deviation | S,M | M | | Decision: keep |
| RT08 Liquidity stress proximity | S,M | M | Compensates for absent RT22 | Decision: keep |
| RD02 / RD03 / RD04 | S,M | M | RD-03 vs RD03 surface-form inconsistency in S | Decision: keep - disambiguate to separate terms `RD02`, `RD03`, `RD04` |
| RD05, RD06 | S,M | ⊘ | Not yet implemented (M) | Decision: keep - disambiguate to separate terms `RD05`, `RD06` |
| SD02 cross-instrument spread dislocation | S,M | ⊘ | Pairs OLO/Bund, OLO/OAT | Decision: keep - refine definition |
| CLOSE_WINDOW | S,M | M (parameterisation) | | Decision: keep |
| PRE_SUSPENSION_WINDOW | S,M | ⊘ | | Decision: keep |
| AUCTION_WINDOW | S,M | ⊘ | | Decision: keep |
| LOOKBACK_30D | S,M | ⊘ | | Decision: keep |
| Marking-the-Close Triad | S,M | M | **Membership conflict**: M = RD01+RD02+RD04 (omits RD03); S SB-04 row detects via RD03+RD04 | Decision: keep |
| DOMINANCE_THRESHOLD / DOMINANCE_THRESHOLD_PCT | S,M | M (formula) | Verify same parameter under two names | Decision: keep - disambiguate into 2 separate terms |
| SB risk archetypes (SB-01…SB-35) | S,M | S (table, truncated) | **Count conflict**: 35 (S) vs 45 (U "Risk Archetype Taxonomy"); SB-21..35 rows missing from S | Decision: keep - master term is `risk archetype`, possible values (SB-01...SB-35 or other IDs) to be listed separately in term definition section |
| SB-26 cash bond/futures | S,M | M | | Decision: keep |
| SB-30 | S,M | M | **Characterisation conflict**: "RFQ front-running footprint" (S) vs "misuse of confidential order information" (M) | Decision: keep |
| SB-05, SB-28/SB-29 | S,M | ⊘ | Pre-event positioning | Decision: keep - disambiguate into separate terms |
| BT block-trade code family | S,M | ⊘ | BT-01…BT-08 (S), BT-06 (M) | Decision: keep |
| FUTURES_ACTIVITY_ELEVATED | S,M | S | | Decision: keep |
| RT02 Excessive activity | (P) | ⊘ (P) | Abnormal trade count → Volume indicator | Decision: keep |
| RT05 Opposite interaction | (P) | ⊘ (P) | Wash-trade indicator → IDS | Decision: keep |
| RA-28 Insider Dealing Indicator — Sensitive Timing | (P) | ⊘ (P) | Separate identifier scheme from SB-##; see conflict P-4 | Decision: keep |
| RA-29 Front-Running Indicator | (P) | ⊘ (P) | Separate identifier scheme from SB-##; possible overlap with SB-30 (§4 conflict #8); see conflict P-4 | Decision: keep |

### 1f. Market structure and instruments

| Term | Used in | Def? | Notes | Human review decision |
|---|---|---|---|---|
| anonymous quote-driven market structure | S,M | S,M | Both define; wording differs — candidate for single glossary definition | Decision: keep, put in glossary, refine definition |
| liquidity-driven reaction / LIQUIDITY_DRIVEN_REACTION | S,M | S,M | Default classification | Decision: keep master term `liquidity-driven reaction`; the other term is its representation as variable in software code |
| identity-driven coordination | S,M | S | | Decision: keep |
| anonymity_attribution_basis | S,M | S,M | Same three enumerated values in both | Decision: keep |
| pre-stress liquidity withdrawal | S,M | M | S has it as "D.3 Pre-Stress Withdrawal" | Decision: keep |
| quote-driven manipulation vectors (spread conditioning, withdrawal cycling, depth manipulation…) | S,M | ⊘ | Family membership varies between enumerations | Decision: keep |
| OTC bilateral trading/component | S,M (A rel.) | M | Dual status: data limitation AND manipulation vector | Decision: keep |
| primary dealer | S,M | M | **Population conflict: 10–20 (S) vs 12–18 (M)** | Decision: keep |
| OLO | S,M (A rel.) | ⊘ | Never expanded (Obligation Linéaire) | Decision: keep |
| OAT | S,M | ⊘ | | Decision: keep |
| Bund | S,M | ⊘ | Bund futures = CICI context instrument | Decision: keep |
| Eurex | S,M (A) | ⊘ | | Decision: keep |
| downstream exposure / os_downstream_exposure | S,M | S (functional) | Field form in M | Decision: keep `downstream exposure` as master term; the latter term is a software variable representing the former |
| MTSAM-L data limitation register | S,M (A: L01,L03) | M (partial) | Register extent inconsistent (L01–L07 stated, L08/L10/L11 exist) | Decision: keep |
| Removal Register / explicit exclusion register | S,M | M | **Same artifact, two names** (S: "Removal Register", M: "Formally Removed Data Categories") | Decision: keep |
| Supervisory Challenge Pack | U,M | ⊘ | | Decision: keep |
| supervisory-defensible escalation package | M (S rel.) | ⊘ | S has "ISGO narrative" role; A has "supervisory-defensible evidence package" — cluster to reconcile | Decision: keep |
| CCO (Chief Compliance Officer) | U,M (A) | ⊘ | Expansion only inferable; escalation-authority conflict in A (CCO vs analyst) | Decision: keep |
| benchmark tier | (P) | ⊘ (P) | Ordered set OFF_THE_RUN / ACTIVE_SECONDARY / BENCHMARK / BENCHMARK_ANCHOR | Decision: keep |
| notional | (P) | ⊘ (P) | Defined by explicit contrast: "the euro nominal (face) value of a single fill — not a price, not a quantity" | Decision: keep |
| aggressor | (P) | ⊘ (P) | "TRUE if this participant took liquidity (crossed the spread)"; venue-tagged | Decision: keep |
| Methodology Lead | U,M | ⊘ | Named governance role | Decision: keep |

## 2. Regulator-owned terms → references list (rubric criterion 3)

- MAR
- FSMA (expanded only in M)
- ESMA
  - FIRDS
  - FITRS
- ECB (+APP/PEPP/TLTRO),
- Belgian Debt Agency (ADA), 
- EMIR, 
- LEI, 
- STOR, 
- MiFID II concepts 
  - LIS
  - SSTI
  transparency regime
- RTS23
- RTS24
- GDPR
- EU AI Act
- UBO
- DMO
- NCA (+CONSOB, AMF, BaFin, FCA)
- Eurex (exchange), 
- Belgian Treasury Certificate
- ISIN
- quote stuffing (industry term)
- Herfindahl–Hirschman Index (HHI) — sourced from §7b `(P)` per Nick's ruling
  2026-07-28; externally owned, so routed here rather than into §1

Per the rubric these get a references-list entry, not a glossary definition.
Borderline: STOR and ADA carry heavy project-specific rules on top of the
regulator meaning — likely need both a reference entry and a project-usage note.

Human review decision: keep all for now - revisit usefullness as design specifications evolve.

## 3. Single-document terms (define locally — summary)

Full lists in the per-document YAML files. Headline counts:

- **U only (~60):** the 22-step pipeline machinery (gates, DIF, PG, CSG, EDL,
  MNE, BDRS, Kill Switch, MER, ELS, EFS, CFS, OPL, NBEC, HCP-1..5, BCI family,
  PIR rules, Price Impact Gate, VMI, CQT, IntentFactor, CF, IDS/ISS/IQ,
  CS/CCaS/CFPS, ReplayObject, AI_HARD, QA Validation, Behavioural Scenario
  Library, Six Indicators, …)
- **S only (~45):** SBSP pack structure (pattern tiers, RT/RD full taxonomies,
  CLOSE_WINDOW framework details, cross-venue patterns (Liquidity Migration,
  Off-Platform Price Conditioning, Venue Arbitrage…), CICI thresholds, BVR +
  MediumReviewEngine + explanation_type + event_context (amendment
  SBSP-AMD-BVR-001), Liquid Regime Classification, EMT, PFNE, DQS, IBE-adjacent
  scoring fields, SB-01..SB-20 archetype rows, …)
- **M only (~45):** FSMA positioning (Five-Pillar Argument, Five-Layer
  Architecture, Core Regulatory Position, language governance, SCL tiers,
  CLOSED_JUSTIFIED, non-filing package), MTSAM API Stack (four data layers,
  feeds, LLM governance), calibration values (CLOSE_WINDOW_START_MINUTES,
  DOMINANCE_THRESHOLD_PCT formula, correlated instrument pairs), MTSAM-L07 +
  ISGO-02, anonymity_attribution_narrative, three-output model
  (BehaviouralConcern / EvidenceConfidence / EscalationReadiness), RT22, …

Human review decision: keep all for now - revisit usefullness as design specifications evolve. 

### 3a. Orphan expansions promoted from §7a — single-document terms (2026-07-28)

Four of the §7a expansions Nick ruled keep belong to terms used in exactly
**one** component blueprint (per the `*.terms.yaml` extractions), so they are
recorded here rather than in §1: C9 places their definitions locally in their
document, not in the glossary.

| Term | Acronym | Used in | Notes | Human review decision |
|---|---|---|---|---|
| Volume Materiality Index | VMI | U (P) | Expansion + role from (P) §0.1: volume-context amplifier; U uses it only in the Version History v25 row ("VMI LOW", Price Impact Gate) | Decision: keep |
| Historical STOR Linkage | HSL | M (P) | Expansion + role from (P) §0.1: amplifier for prior supervisory record; M extraction notes it as a participant history field proxied from enforcement data | Decision: keep |
| Outcome Persistence Layer | OPL | U (P) | Role from (P) §0.1: whether an outcome persisted. **Expansion discrepancy to disposition**: U glosses OPL only as "persistence" (Step 16) and its extraction inferred "likely Outcome Persistence Level" — Level (U, inferred) vs Layer ((P), sourced) | Decision: keep |
| Escalating Dominance Trend | EDT | U (P) | Expansion + role from (P) §0.1: upward trend in market control; BPL persistence component (U Step 5b) | Decision: keep |

## 4. Decision register — conflicts and dispositions needed (C8: surface, never harmonise)
<!-- Gaps in number list indicated previous questions that were resolved. --> 

Definition conflicts (two docs disagree):
1. **MM_SAFEHARBOUR**: twelve-criteria (U §X.3) vs seven-criteria (M 0.3).
2. **Risk archetype count**: 45 (U) vs 35 (S) — and S's table truncates at SB-20.
3. **Marking-the-Close Triad**: RD01+RD02+RD04 (M) vs SB-04 detection via RD03+RD04 (S).
4. **Primary dealer population**: 10–20 (S) vs 12–18 (M).
5. **CQS semantics**: integer bands vs fractional thresholds (within U!) vs additive amplifier (S,M).
6. **CRS expansion**: Context Reliability Score (U) vs relevance/surprise usage (S,M).
7. **OS expansion**: Outcome Score (U) vs Outcome Severity (S) — both inferred.
8. **SB-30**: RFQ front-running (S) vs misuse of confidential order information (M).
9. **ISGO role**: output/narrative object (S) vs gap register issuing findings (M).
10. **CMCS components**: s1–s6 names differ slightly S vs M; S records formula drift.
11. **Version skew**: M "applies to UCE v28" vs S citing "§VI-A.5.3 UCE v30"; M title v21 vs changelog v22.
12. **Document set extent**: "1/2/3 of 3" vs cited Documents 6 and 7 + ECIL Supplemental Specification.
13. **UCE self-count**: "Ten foundational principles" heading vs 12 principles enumerated.
14. **Classification scale**: four levels (U Step 12) vs five with NONE (M three-output, A).
15. **Alert provenance** (informational, A vs M): A attributes RT/RD alerts to Eagle/ATS; M to "MTS S.p.A. surveillance system".

Identity questions (same concept, different names? — resolve before records):
| Question | Human review response |
|---|---|
| 16. IBE (S usage) ≡ IBE (U/A definition)? and IBEB as separate concept. | `IBE` is `Intraday Behavioural Event` and all documents apply this definition; `IBEB` is `IBE Builder`, a software component that implements IBEs |
| 17. DAF ≡ DependencyFactor (U)? | `DAF` = Dependency Adjustment Factor, defined in (U) as a number that is determined based on another term `DS`. Other documents follow the definition in (U) |
| 18. Removal Register ≡ explicit exclusion register ≡ Formally Removed Data Categories. | `removal register` and `exclusion register` are synonyms denoting the list of excluded data sources - prefer the former as master term; the `formally removed data categories` are four entries (rows) in the `removal register` |
| 19. EvidenceConfidence (M/U) vs ModelConfidence (S/M). | `ModelConfidence` is a lower-level data-quality flag per data signal; `EvidenceConfidence` is an MTSAM-specific higher-level assessment that relies on `ModelConfidence` and other factors to indicate how the solution can substantiate its assessment based on available data vs MTSAM criteria |
| 20. escalation readiness (A, lowercase) vs EscalationReadiness (U/M output). | `escalation readiness` is the business term, `EscalationReadiness` its modellisation in software; the definition of either term has contradictions in the source documents: (U) has 6 conditions, (M) has 5 conditions in one place and contradicts itself by also listing 6 conditions elsewhere that are different from (U) - to be solved by business experts |
| 21. DOMINANCE_THRESHOLD (S) vs DOMINANCE_THRESHOLD_PCT (M). | `DOMINANCE_THRESHOLD` is just shorthand for `DOMINANCE_THRESHOLD_PCT`, one term that is defined in three different inconsistent ways - needs to be one definition, to be resolved by business |
| 22. "Quote Withdrawal" (S Tier-1 archetype) vs SB-08 Liquidity Withdrawal vs QUOTE_WITHDRAWAL primitive vs pre-stress withdrawal — a four-way near-synonym cluster. | `Quote withdrawal` (S) Tier-1 archetype is a single event (the removal of a quote by a market participant) - same concept as `QUOTE_WITHDRAWAL`; `SB-08 Liquidity Withdrawal` and its synomym `SB-08 Liquity Stress Pre-positioning` bundles `quote withdrawal` and other factors to create a scored and filed archetype; `Liquidity withdrawal` = `liquidity removal` is a more aggregate term indicating the overall reduction in liquidity by a market participant; `pre-stress withdrawal` is a shorter version of `Deliberate Pre-Stress Liquidity Withdrawal`: the detection pathway based on RT08 to compensate for the lack of RT22 input data |
| 23. Momentum Ignition: RT01 alert (M) vs SB-01 archetype (S) vs BOA=MOMENTUM_IGNITION value (S). | `RT01 alert` is defined as an alert primitive in (U) and calibrated for MTSAM usage in (M); `BOA=MOMENTUM_IGNITION` is defined in (U) as a deterministic BOA ("Behavioural Objective Assessment" - the objective most consistent with an observed behaviour) that requires `RT01` and other data; `SB-01 archetype` is defined in (S): it consumes `RT01` and `BOA=MOMENTUM_IGNITION` to define an archetype, which a different level concept from alert or BOA - note: there is a dangling document reference: SB-01's definition row cites "§A.4.0" in (S) but that paragraph does not exist |
| 24. MEDIUM-INVESTIGATE vs MEDIUM-STRUCTURED REVIEW (U). | `MEDIUM-INVESTIGATE` and `MEDIUM-STRUCTURED REVIEW` and `MEDIUM-BATCH` describe different investigation paths that the human analyst can take for a transaction with a `MEDIUM` label: `MEDIUM-BATCH` allows automatic closure of the investigation whereas `MEDIUM-INVESTIGATE` and its synonym `MEDIUM-STRUCTURED REVIEW` mandate a human investigation | 
| 25. Behaviour Categories vs Behavioural Categories (A naming drift; U has a 17-category taxonomy). | `Behaviour Categories` and `Behavioural Categories` are synonyms - prefer the latter as master term |
| 26. UCE ≡ Veridict Core Engine (M surface form). | `UCE` stands for "Universal Core Engine" - "Veridict Core Engine" is a less preferred term to be phased out |
| 27. BDRS acronym does not match its expansion (U note). | `BDRS` = "Behavioural Distinctiveness Score", defined in (U) as measuring if a participant's behaviour is materially different from peers in the same session - not to be confused with `BDS` = "Behavioural Drift Score" which measures cross-session drift over a LOOKBACK window; no document explains what the "R" in "BDRS" stands for; (M) calibrates `BDRS` for use at MTSAM but also contains a misinterpretation: it lists BDRS as a component of "pipeline Step 11" which contradicts the definition in (U) where BDRS is part of pipeline step 21b - in a part of the document that also contains the `EscalationReadiness` contradiction. |
| 28. SCS vs SCS_bpl — two constructs sharing a name. | `SCS` = "Signal Confidence Score" as defined in (U), operating on a single signal but occurring only twice in the document corpus; `SCS_bpl` = "Session Consistency Score" measures if a suspicious pattern or behaviour or bias is consistent across trading sessions. |

Word-overload cluster (glossary must disambiguate, criterion 1):

29. **"Tier"**: pattern tiers 1/2/3 · escalation Tier 1 · AI-governance Tier 1 controls · MTSAM supervisory tier · ECIL feed tiers · SB-26 "Tier 3 investigative hypothesis".
30. **"Level"**: Four-Level Observability (1–4) · CICI levels (1–3) · evidence hierarchy (1–5) · audit chain (L1–L5) · Level 0 closure · BCI levels (named) · classification levels · maturity levels.
31. **"Layer"**: Five-Layer FSMA architecture · four data layers (API stack) · six software layers (A) · three logical layers (A) · UCE/BPL/ECIL/CCL "layers" · Layer 2 feeds (Doc 3).
32. **"IS"**: Intent Score vs the English verb — extraction hazard; also IS vs IScore vs ISS.

Set-level orphans (used somewhere, letter-expanded nowhere): 

40. IPI, 
45. EMT, 
46. PFNE, 
47. DQS
48. BIVM
50. OAIC
52. RSN
53. SSF/DF
54. CF
57. ISGO
58. BEP_E
60. SDAIL
61. RAAF
62. NFIL
These become the step 3.3 orphan/flag list.

> **Update 2026-07-28:** definitions of items 33–39, 41–44, 49, 51, 55, 56, 59 and 63 were found 
> in (P); they > remain definition-orphans within the three blueprints (Def? = ⊘, expansion
> sourced from (P) only). 

Human review decision: keep all - definitions will be refined and conflicts will be resolved in a later stage. 

## 5. Source-document structural anomalies (feed into C8 reference checks)

- S: 
  - duplicated section number A.4.3.1 (two different sections); 
  - A.5 missing; 
  - §D.4 text embedded inside a table row; 
  - archetype table truncated at SB-20; 
  - UTF-8 mojibake in A.4.3; 
  - TOC promises absent Sections B–J.
- U: 
  - "XI" numbering reused (Insider Dealing vs Deployment Maturity); 
  - OCR-garbled Step 11b rationale; 
  - same amendment ID (UCE-AMD-BVR-001) on two change sets.
- M: 
  - v21 title vs v22 changelog; 
  - MTSAM-L register extent inconsistent.
- A: 
  - "Associated" vs "Associate" Markets; 
  - Phase 1 vs Phase 2 assignment of the five must-have external sources contradicts itself across §4.1/§8.2/§9.3; 
  - broken cross-reference (T+1 "as mentioned in 4.1 and 5.1" — absent).

  Human review decision: keep all - to be refined and corrected later
  - for A: "MTS Associated Markets" is the master term - "MTS Associate Markets" is a typo 


## 6. Next steps (per plan §Phase 3)

1. **Nick reviews this list**: cull false positives, rule on the identity
   questions (§4 items 16–28), and confirm the regulator-owned set (§2).
2. **Nick reviews the `(P)` delta in §7** and rules on each proposed expansion
   before it is folded into §1–§4. *(§7a reviewed 2026-07-28: all 20 expansions
   ruled keep and promoted into §1b–§1d and §3a. §7b reviewed 2026-07-28: all
   22 candidate terms accepted into the glossary (§1b–§1f); HHI routed to §2
   as externally owned. §7c–§7d still pending.)*
3. Step 3.2 placement is then mechanical (the "Used in" column already encodes it).
4. Step 3.3 drafts one-sentence definitions per surviving term — the ⊘ marks
   and the conflict register become the orphan and conflict flags that C8
   requires humans to disposition.

## 7. `(P)` delta — what `prototype-BC17.md` contributes

This paragraph was sourced from (P) and created separately from §1–§5 which were sourced from (U), (S), and (M). Source for every row: `prototype-BC17.terms.yaml` which carries the verbatim definition quote and section reference for each.

**Placement impact: none by default - must be human approved.** 
Per the exclusion above, no term is promoted, demoted, or moved on the strength of a `(P)` appearance - a human must approve. 

### 7a. Set-level orphans that `(P)` resolves

> **Reviewed by Nick 2026-07-28: all 20 expansions in this section were ruled "keep" and promoted** 
> into the matching §1 rows (with `(P)` flags), a new §1c row for BOA, 
> and §3a for the four single-document terms (VMI, HSL, OPL, EDT).

| # | Acronym | Expansion from (P) §0.1 | One-line role given | Human review decision |
|---|---|---|---|---|
| 33 | CQS | Convergence Quality Score | summed confirmed evidence across five domains | Keep — promoted to §1c (Nick, 2026-07-28) |
| 34 | CCT | Coordination Classification Tier | EXPLICIT / IMPLICIT / STRUCTURAL coordination | Keep — promoted to §1c (Nick, 2026-07-28) |
| 35 | MDCS | Multi-Day Conditioning Score | pre-positioning across sessions | Keep — promoted to §1d (Nick, 2026-07-28) |
| 36 | CWPS | Cross-Window Persistence Score | same pattern across OPEN/CLOSE windows or sessions | Keep — promoted to §1d (Nick, 2026-07-28) |
| 37 | QDSP | Quote Depth Share Position | share of visible book depth | Keep — promoted to §1d (Nick, 2026-07-28) |
| 38 | PLCS | Participant Liquidity Contribution Score | net liquidity provided vs removed | Keep — promoted to §1d (Nick, 2026-07-28) |
| 39 | SRI | Spread Rationality Indicator | economic rationality of spread crossing | Keep — promoted to §1d (Nick, 2026-07-28) |
| 41 | POFP | Participant Order Flow Profile | per-participant behavioural baseline (mean + σ) | Keep — promoted to §1d (Nick, 2026-07-28) |
| 42 | HQLD | Historical Quote Lifecycle Dataset | quote-level history | Keep — promoted to §1d (Nick, 2026-07-28) |
| 43 | UEEO | Unified Enriched Event Object | five-stream fused event record | Keep — promoted to §1c (Nick, 2026-07-28) |
| 44 | BOA | Behavioural Objective Assessment | deterministic risk-objective scoring for HIGH/VERY HIGH | Keep — promoted to §1c as new row, used in U,S (Nick, 2026-07-28) |
| 49 | VMI | Volume Materiality Index | volume-context amplifier | Keep — single-document (U); promoted to §3a (Nick, 2026-07-28) |
| 51 | HSL | Historical STOR Linkage | amplifier for prior supervisory record | Keep — single-document (M); promoted to §3a (Nick, 2026-07-28) |
| 55 | OPL | Outcome Persistence Layer | whether an outcome persisted | Keep — single-document (U); promoted to §3a; Level-vs-Layer expansion discrepancy noted there (Nick, 2026-07-28) |
| 56 | EDT | Escalating Dominance Trend | upward trend in market control | Keep — single-document (U); promoted to §3a (Nick, 2026-07-28) |
| 59 | BDS | Behavioural Drift Score | slow drift of behaviour from own baseline | Keep — promoted to §1d (Nick, 2026-07-28) |
| 63 | RT / RD | **Real-Time** alert / **Reporting-Day** alert | intraday primitive (RT01, RT02, RT04, RT05, RT08) / end-of-day primitive (RD01–RD04) | Keep — promoted to §1b; sourced "Reporting-Day" supersedes the "end-of-day" inference (Nick, 2026-07-28) |
| 1d | QBRS | Quote Behaviour Risk Score | composite quote-domain risk score | Keep — promoted to §1d (Nick, 2026-07-28) |
| 1d | QBCCL | Quote Behaviour Contextual Confidence Layer | contextual sensitivity multiplier | Keep — promoted to §1d (Nick, 2026-07-28) |
| 1d | QBBE | Quote Behaviour Baseline Engine | participant quote baselines | Keep — promoted to §1d (Nick, 2026-07-28) |

Two notes on this table. **RD expands to "Reporting-Day", not "end-of-day"** —
§1b currently records the inference "(real-time / end-of-day inferred)", which was
close but not exact; prefer the sourced expansion. And the RT set is **not
contiguous** — RT01, RT02, RT04, RT05, RT08, with RT03/RT06/RT07 absent and no
statement of whether they are unimplemented or unmapped.

Still unresolved after `(P)`: IPI (40), EMT (45), PFNE (46), DQS (47), BIVM (48),
OAIC (50), RSN (52), SSF/DF (53), CF (54), ISGO (57), BEP_E (58), SDAIL (60),
RAAF (61), NFIL (62), and QBLI from §1d.

### 7b. Candidate terms `(P)` introduces that are not on this list

`(P)`-only terms. They fail the mechanical C9 placement test (used in ≥2 of {U,S,M}). 
**Reviewed by Nick 2026-07-28: accepted into the glossary.** 
Rationale: `prototype-BC17.md` sources its definitions from the **complete copies** of `(U)`, `(S)`, `(M)`— not the `-shortened` files used for this extraction — so a term's absence
from the shortened blueprints is not evidence it is absent from the full document
set, only from the `blueprint-*-shortened.md` files. Every row below except
HHI (externally owned) is promoted into the matching §1 subsection and
flagged `(P)` in "Used in" there, since presence in the full `(U)/(S)/(M)`
text has not yet been independently verified against those complete copies.

| Term | Acronym | Note | Human review decision |
|---|---|---|---|
| Aggressor-on-Book / Adverse Outcome Behaviour | AOB | Carries **two competing expansions in the same glossary cell** — unresolved even in (P) | Keep — promoted to §1b (Nick, 2026-07-28) |
| Participant-Day Risk Profile | PDRP | Consolidated daily participant object; central to (P)'s own gap C-1 | Keep — promoted to §1b (Nick, 2026-07-28) |
| Participant Session Profile | PSP | Role text is near-identical to PDRP's — possible synonym, or an undocumented distinction | Keep — promoted to §1b (Nick, 2026-07-28) |
| Network Centrality Score | NCS | Level set LOW/MEDIUM/HIGH/**EXCEPTIONAL** — a fourth enumerated scale, not a variant of the five-level classification | Keep — promoted to §1c (Nick, 2026-07-28) |
| Temporal Correlation Engine | TCE | Owns the ECIL event/behaviour timeline mapping | Keep — promoted to §1c (Nick, 2026-07-28) |
| Temporal Correlation Score | TCS | The one fully-written formula in (P) | Keep — promoted to §1c (Nick, 2026-07-28) |
| Timing Precision Score | TPS | Banded in the RSA rubric | Keep — promoted to §1c (Nick, 2026-07-28) |
| Outcome Recurrence Score | ORS | | Keep — promoted to §1c (Nick, 2026-07-28) |
| Outcome Sensitivity Score | OSS | Instrument-sensitivity multiplier | Keep — promoted to §1c (Nick, 2026-07-28) |
| Block Trade Intelligence Score | BTI | "composite of **nine** block-trade patterns" | Keep — promoted to §1c (Nick, 2026-07-28) |
| Quote Cancellation Ratio | QCR | One of the few (P) glossary rows carrying a formula | Keep — promoted to §1d (Nick, 2026-07-28) |
| Quote Lifetime Score | QLS | Unavailable in this deployment (gap MTSAM-L02) | Keep — promoted to §1d (Nick, 2026-07-28) |
| Herfindahl–Hirschman Index | HHI | Externally owned → **references list**, not glossary | Routed to §2 as externally owned, not glossary (Nick, 2026-07-28) |
| RT02 Excessive activity | RT02 | Abnormal trade count → Volume indicator | Keep — promoted to §1e (Nick, 2026-07-28) |
| RT05 Opposite interaction | RT05 | Wash-trade indicator → IDS | Keep — promoted to §1e (Nick, 2026-07-28) |
| RA-28 Insider Dealing Indicator — Sensitive Timing | RA-28 | See conflict P-4 below | Keep — promoted to §1e (Nick, 2026-07-28) |
| RA-29 Front-Running Indicator | RA-29 | See conflict P-4 below | Keep — promoted to §1e (Nick, 2026-07-28) |
| Follower Rule | — | Named normative rule: BCI < 3 caps concern at MEDIUM; BCI ≥ 7 opens VERY HIGH | Keep — promoted to §1c (Nick, 2026-07-28) |
| data-availability contract | — | Binds capability flags to which scores are computable | Keep — promoted to §1c (Nick, 2026-07-28) |
| benchmark tier | — | Ordered set OFF_THE_RUN / ACTIVE_SECONDARY / BENCHMARK / BENCHMARK_ANCHOR | Keep — promoted to §1f (Nick, 2026-07-28) |
| notional | — | Defined by explicit contrast: "the euro nominal (face) value of a single fill — not a price, not a quantity" | Keep — promoted to §1f (Nick, 2026-07-28) |
| aggressor | — | "TRUE if this participant took liquidity (crossed the spread)"; venue-tagged | Keep — promoted to §1f (Nick, 2026-07-28) |
| session / participant | — | session = one trading day; participant = the dealer being assessed | Keep — promoted to §1b (Nick, 2026-07-28) |

### 7c. New conflicts and collisions `(P)` raises

Per C8 these are surfaced, never harmonised. Numbered `P-#` to keep them distinct
from the §4 register until Nick folds them in.

| # | Conflict | Human review decision |
|---|---|---|
| P-1 | **MTSAM expansion — three-way.** §1a records "MTS Associated Markets" (legal entity, Belgium) with the "Associated" spelling ruled master. (P) §0.1 gives a *third* expansion, "**MTS Analytical Market surveillance**", and uses it to mean the deployment/system rather than the institution. | The (P) definition is incorrect. |
| P-2 | **MTS sense conflict.** §1a records MTS S.p.A. as a legal entity (Italy). (P) uses MTS for the **trading venue** — "Mercato dei Titoli di Stato" — and supplies that expansion, which the blueprints may not. Same acronym, institution vs venue. | MTS is a legal entity. "Venue" is a confusion that only AI has. |
| P-3 | **MCL fourth naming variant.** (P) calls Document 3 the "**Market Configuration Layer**", alongside "MTSAM Calibration Layer", "Institution Calibration Layer", and MCL. | Keep this interpretation - flag to humans for disambiguation. |
| P-4 | **Third risk-archetype identifier scheme.** §1e/§4.2 record SB-01…SB-35 with a 45-vs-35 count conflict. (P) uses **RA-##** (RA-28, RA-29). Separate taxonomy, or a renumbering? RA-29 "Front-Running Indicator" may also overlap SB-30 (§4 conflict #8). | Keep - flag to humans for disambiguation|
| P-5 | **"BC" overloaded inside one table.** (P) §0.1 defines BC = Behaviour Category, then uses "BC Behavioural-Conditioning impact" for a different concept in the Outcome Score row of the same glossary. | Keep - flag to humans for disambiguation |
| P-6 | **"D1/D2" overloaded three ways.** BCI *dimensions* D1/D2 (Quote/Liquidity Leadership) vs signal *domains* D1/D2 (Volume and Participation / Timing) vs the plan's own decision register D1–D10. | Keep - flag to humans for disambiguation |
| P-7 | **Outcome Score sub-acronyms undefined.** The OS row introduces PI / LI / I / BC with no rows of their own, breaking (P)'s stated "every abbreviation is spelled out" rule. | Keep - flag to humans for disambiguation |
| P-8 | **Four-vs-five classification scale, again.** (P)'s Final Concern bands are LOW/MEDIUM/HIGH/VERY HIGH — no NONE — against the five-level scale ruled leading in §1b. Consistent with §4 conflict #14, now with a third witness. | Keep - flag to humans for disambiguation |
| P-9 | **Block-trade pattern count.** BTI is "composite of **nine** block-trade patterns"; §1e records the family as BT-01…BT-08 (**eight**). | Keep - flag to humans for disambiguation |
| P-10 | **Two unrelated "primitive" vocabularies.** (P)'s "nine implemented **alert** primitives" (RT/RD codes) vs §1b's "**behavioural** primitive" (QUOTE_WITHDRAWAL, SPREAD_WIDENING, …). Do not conflate. | Keep - flag to humans for disambiguation |
| P-11 | **MWBR band count.** (P) §0.1 lists three bands (NORMAL/ELEVATED/ANOMALOUS); its own §1.8 formula yields four, adding BELOW_NORMAL. | Keep - flag to humans for disambiguation |
| P-12 | **SRI both unavailable and in use.** (P) marks SRI undetermined under gap MTSAM-L07, yet its RSA rubric still consumes "Spread Rationality ≥2σ". | Keep - flag to humans for disambiguation |
| P-13 | **Test-identifier collision.** Validation footprint cites test cases **T287–T295** while the methodology register uses **T-###** codes (T-002, T-108, …). Similar shape, different namespace. | Flag to humans for disambiguation |
| P-14 | **Gap-code collision with the project's own numbering.** (P) Appendix C uses **C-1…C-6** for implementation gaps; the plan uses C1–C12 for constraints. Disambiguate on any quotation. | Flag to humans for disambiguation |

### 7d. Orphans `(P)` confirms rather than resolves

Useful negative evidence — these were flagged ⊘ in §1b and remain undefined even
in a document written specifically to spell everything out.

- **instrument cluster** — (P) states its *role* ("defines the population over
  which dominance/market-share are measured") but still never gives the
  clustering rule.
- **episode** — used as BC-17's co-occurrence scope ("all three detection signals
  co-occur on the same episode") and as a 14-day constant, never defined.
- **signal (vs alert)** — (P) offers "Detection signals are observations, not
  conclusions", the closest thing to a definition found so far, but it still does
  not distinguish signal from alert.

### 7e. Material worth reusing beyond term extraction

Not term rows; flagged because they bear on later phases.

- **(P) §1.7 explains *why* the mean and σ do different jobs in a z-score** — two
  paragraphs of genuine plain-language exposition. It is the best model of
  criterion 2 (abstraction pyramid) anywhere in the corpus, and worth holding as
  a style exemplar for Phase 5's golden output.
- **(P) Appendix F is a hand-built topological ordering** — 22 calculation steps
  from raw trade row to archetype. It is an independent cross-check on the
  concept graph's topological sort for this slice of the domain (step 3.4).
- **(P) Appendices C and D are a working waiver register in the wild** — six
  ticketed implementation gaps and three code-vs-methodology discrepancies, each
  recorded with its effect and left unresolved. Direct prior art for the DoD's
  waiver register (criterion 3) and evidence the client already documents
  contradictions rather than silently fixing them.
- **Two live discrepancies inherited from (P)**, both criterion 5 material if any
  of this text is reused: POFP lookback **90 days / 15 sessions** (code) vs
  **45 days / 10 sessions** (methodology `T-003`); RSA bands **LOW ≤40 / MEDIUM
  41–70 / HIGH 71–85 / VERY HIGH ≥86** (code) vs **"≥72 HIGH / 41–71 MEDIUM"**
  (methodology `T-117`).
