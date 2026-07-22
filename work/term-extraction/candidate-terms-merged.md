# Step 3.1 — Merged candidate term list (for human review)

**Status:** LLM-assisted extraction, merged 2026-07-22. NOT yet human-reviewed.
Nothing here is a concept record yet; this is the review artifact that step 3.1
("LLM-assisted, human-reviewed") requires before records are created.

**Sources:** the three component blueprints 
| Source doc | Abbreviation | Notes |
|---|---|---|
| `blueprint-UCE-shortened.md` | (U) | | 
| `blueprint-SBSP-shortened.md` | (S) | |
| `blueprint-MCL-shortened.md` | (M) | |
| `blueprint-analytical-layer.md` | (A) | read-only reference, **excluded from the C9 placement test** per Nick's ruling 2026-07-22 | 

**Raw per-document extractions** (definition quotes, line spans, aliases, full
notes): `blueprint-*.terms.yaml` in this directory. File `candidate-terms-merged.md` is the merge: one row per candidate concept, with per-document presence and computed placement.

**Placement rule (C9):** used in ≥2 of {U, S, M} → `glossary.md`; used in
exactly 1 → defined locally in that document. Document `A` never counts toward
placement; an `(A)` flag is informational only.

Raw record counts before merging: U ≈ 135, S ≈ 120, M ≈ 130, A ≈ 100.
After cross-document identity merging: ~95 glossary candidates, ~150
single-document terms, ~35 regulator-owned terms.

---

## 1. Glossary candidates (used in ≥2 component blueprints)

Grouped thematically. "Def?" = which doc(s) contain an explicit definition
(⊘ = defined nowhere in the three docs — orphan at set level).

### 1a. Product, documents, institutions

| Term | Acronym | Used in | Def? | Notes |
|---|---|---|---|---|
| Universal Core Engine | UCE | U,S,M (A) | U (A) | M also calls it "Veridict Core Engine"; version skew: M applies to v28, S cites v30 |
| Sovereign Bond Sector Pack | SBSP | U,S,M (A) | U,S (A) | Alternatively also "Sector Intelligence Pack" or "Sovereign Government Bond Sector Intelligence Pack" - goal is replace these alternatives by "SBSP" / "Sovereign Bond Sector Pack" |
| MTSAM Calibration Layer | MCL | U,M (A) | U (A) | Acronym MCL only in filename; alternatively also "Institution Calibration Layer" - a layer of the solution that contains any company-specific definitions and rules, with `MTSAM` being one company |
| Veridict MAR Intelligence Platform | — | U,S,M | ⊘ | Vendor/product family; never described |
| Document set (Doc 1/2/3 + Doc 6, Doc 7, ECIL Suppl.) | — | U,S,M | ⊘ | "3 of 3" claimed, but Docs 6 & 7 cited — set-extent conflict |
| MTSAM (MTS Associated Markets) | MTSAM | U,S,M (A) | M (A) | real definition: legal entity in Belgium; its meaning drifts: venue vs surveilling institution; (A) uses both "Associated" and "Associate" spellings |
| MTS S.p.A. | MTS | S,M (A) | A | real definition: legal entity in Italy, sister company of MTSAM; financial markets platform operator; high confusion risk with MTSAM |

### 1b. Pipeline objects and units of analysis

| Term | Acronym | Used in | Def? | Notes |
|---|---|---|---|---|
| Intraday Behavioural Event | IBE | U,S (A) | U (A) | S never expands IBE; verify IBE≡the object SBSP means (S notes "IBEB near-miss") |
| Behavioural Episode Consolidation / episode | BEP_E | U,M | U | Episode = analyst review unit; BEP_E never letter-expanded |
| signal (vs alert) | — | U,M | ⊘ | Doctrinal three-way distinction alert → IBE/signal → episode; never explicitly defined |
| alert / RT alert | RT | U,S,M (A) | ⊘ | RT/RD never expanded anywhere in the set (real-time / end-of-day inferred) |
| campaign | — | S,M | ⊘ (partial S) | BPL-owned cross-session construct; named campaign types in S |
| behavioural primitive | — | S,M (U rel.) | ⊘ | Named instances: QUOTE_WITHDRAWAL, SPREAD_WIDENING, LIQUIDITY_REMOVAL, BLOCK_TRADE, AGGRESSIVE_BUY/SELL, SUSPENSION |
| QUOTE_WITHDRAWAL | — | S,M | ⊘ | |
| SPREAD_WIDENING | — | S,M | ⊘ | |
| LIQUIDITY_REMOVAL | — | S,M | ⊘ | |
| instrument cluster | — | S,M (A) | ⊘ | Aggregation unit for IBE and dominance shares; rule never given |
| explanation_trace | — | U,S,M | ⊘ | Canonical explainability artifact; holds anonymity_attribution_basis |
| classification (NONE/LOW/MEDIUM/HIGH/VERY HIGH) | — | U,S,M (A) | U (A) | U's four-level scale vs A/M five-level (NONE) — reconcile |
| MEDIUM-INVESTIGATE | — | U,S,M | ⊘ | Sub-band; U also has MEDIUM-STRUCTURED REVIEW — same? |

### 1c. Scores, gates, engine components

| Term | Acronym | Used in | Def? | Notes |
|---|---|---|---|---|
| Convergence Quality Score | CQS | U,S,M (A) | ⊘ | Expansion inferred; **unit conflict**: integer bands (U Step 5) vs fractional ≥0.85 (U Step 21) vs additive +0.50 amplifier (S,M) |
| Outcome Score / Outcome Severity | OS | U,S | U | **Expansion conflict**: U implies "Outcome Score", S implies "Outcome Severity" |
| Intent Score | IS | U,M | U | Surface form "IS" dangerously ambiguous |
| IScore | — | U,S | ⊘ | Distinct from IS — easy to conflate |
| PriorityScore | — | U,M | U | |
| Causality Confidence Layer | CCL | U,M | U | QBCCL looks like a quote-domain variant — relationship unstated |
| Regulatory Risk Factor | RRF | U,M | M (expansion) | U only says "Regulatory Context (RRF)" |
| EscalationReadiness | — | U,M (A rel.) | U | A has lowercase "escalation readiness" — same concept? |
| Market-Wide Behavioural Reference | MWBR | U,M | U | M never expands |
| Reasonable Suspicion Assessment | RSA | U,M | U | M never expands |
| MM_SAFEHARBOUR | — | U,M | M | **Conflict: twelve-criteria (U) vs seven-criteria (M) test** |
| Dependency Score / Dependency Filter | DS | U,S | U | U also has DAF vs DependencyFactor — verify same construct |
| Structural Relationship Score | SRS | U,M | U | |
| SCS (and SCS_bpl) | SCS | U,S | ⊘ | Two distinct SCS constructs flagged in U; S has SCS_buyside/sellside family |
| ModelConfidence | — | S,M | M (cap rule only) | Relationship to U/M "EvidenceConfidence" unstated |
| SCL (supervisory confidence tier) | SCL | U,M | M (partial) | COMPELLING / PRECAUTIONARY tiers |
| CCT (coordination classification) | CCT | U,S,M | ⊘ | Values EXPLICIT/IMPLICIT; expansion never given |
| evidence hierarchy | — | U,M | ⊘ | Levels 1–5; collides with many other Level scales |
| UEEO | UEEO | S,M | ⊘ | Event/episode data object; never expanded |
| CRS | CRS | U,S,M | ⊘ | **Expansion conflict**: U "Context Reliability Score" vs S/M usage as relevance/surprise score (CRS_VERY_HIGH) |
| ECIL event relationship states (AMPLIFIES_SUSPICION / CONTRADICTS_PATTERN / SUPPORTS_EXPLANATION / FULLY_EXPLAINED) | — | U,S,M | ⊘ | Membership varies per doc |

### 1d. Layers and frameworks

| Term | Acronym | Used in | Def? | Notes |
|---|---|---|---|---|
| Behavioural Persistence Layer | BPL | U,S,M | M (expansion) | Components BDS, SCS_bpl, MDCS, CWPS, EDT (U) |
| External Context Intelligence Layer | ECIL | U,S,M | M (expansion) | Only M expands it |
| Cross-Instrument Context Intelligence | CICI | S,M | S | Internal Levels 1–3 clash with Four-Level Observability Framework |
| Cross-Market Convergence Score | CMCS | S,M | S,M | Same formula both docs, but component names differ slightly; drift note in S ("original four-component formula") |
| Four-Level Observability Framework | — | S,M | S | |
| quote intelligence architecture (QBRS/QBLI/QBCCL) | — | S,M | M (partial) | "Single most important strategic enhancement dependency" (M) |
| QBRS | QBRS | S,M | ⊘ | Never expanded anywhere |
| QBLI | QBLI | S,M | ⊘ | Never expanded anywhere |
| QBCCL | QBCCL | S,M | ⊘ | Never expanded anywhere |
| QBBE | QBBE | U,S,M | M (functional) | Never letter-expanded |
| POFP | POFP | S,M | ⊘ | Participant-own-baseline engine; never expanded |
| RDCS (RT–RD cross-pass scoring) | RDCS | S,M | M | S never expands |
| MDCS | MDCS | U,S,M | ⊘ | Never expanded anywhere |
| CWPS | CWPS | U,S,M | ⊘ | Never expanded; _cross/_intra variants |
| QDSP | QDSP | S,M | ⊘ | Never expanded anywhere |
| PLCS | PLCS | S,M | ⊘ | Never expanded anywhere |
| SRI | SRI | S,M | ⊘ | Never expanded anywhere |
| QML (Quote Market Leadership) | QML | S,M | S (inline expansion) | |
| IPI | IPI | S,M | ⊘ | Never expanded anywhere |
| HQLD | HQLD | U,S,M | ⊘ | Gate for quote intelligence & BCI D1/D2; never expanded |
| BDS | BDS | U,S | ⊘ | BPL component; also near-collision with BDRS (U) |
| ISGO | ISGO | U,S,M | ⊘ | **Role conflict**: S = narrative/output object with mandatory language; M = gap-finding register (ISGO-02) |

### 1e. Alert codes and windows

| Term | Used in | Def? | Notes |
|---|---|---|---|
| RT/RD alert taxonomies | S,M (A) | S (counts), M (list) | S: 25 RT + 15 RD codes; M: 9 implemented of ~30 — count conflict to disposition |
| RT01 Momentum ignition | S,M | M | Collides with SB-01 "Momentum Ignition" archetype (S) — alert vs archetype |
| RT04 Price deviation | S,M | M | |
| RT08 Liquidity stress proximity | S,M | M | Compensates for absent RT22 |
| RD02 / RD03 / RD04 | S,M | M | RD-03 vs RD03 surface-form inconsistency in S |
| RD05, RD06 | S,M | ⊘ | Not yet implemented (M) |
| SD02 cross-instrument spread dislocation | S,M | ⊘ | Pairs OLO/Bund, OLO/OAT |
| CLOSE_WINDOW | S,M | M (parameterisation) | |
| PRE_SUSPENSION_WINDOW | S,M | ⊘ | |
| AUCTION_WINDOW | S,M | ⊘ | |
| LOOKBACK_30D | S,M | ⊘ | |
| Marking-the-Close Triad | S,M | M | **Membership conflict**: M = RD01+RD02+RD04 (omits RD03); S SB-04 row detects via RD03+RD04 |
| DOMINANCE_THRESHOLD / DOMINANCE_THRESHOLD_PCT | S,M | M (formula) | Verify same parameter under two names |
| SB risk archetypes (SB-01…SB-35) | S,M | S (table, truncated) | **Count conflict**: 35 (S) vs 45 (U "Risk Archetype Taxonomy"); SB-21..35 rows missing from S |
| SB-26 cash bond/futures | S,M | M | |
| SB-30 | S,M | M | **Characterisation conflict**: "RFQ front-running footprint" (S) vs "misuse of confidential order information" (M) |
| SB-05, SB-28/SB-29 | S,M | ⊘ | Pre-event positioning |
| BT block-trade code family | S,M | ⊘ | BT-01…BT-08 (S), BT-06 (M) |
| FUTURES_ACTIVITY_ELEVATED | S,M | S | |

### 1f. Market structure and instruments

| Term | Used in | Def? | Notes |
|---|---|---|---|
| anonymous quote-driven market structure | S,M | S,M | Both define; wording differs — candidate for single glossary definition |
| liquidity-driven reaction / LIQUIDITY_DRIVEN_REACTION | S,M | S,M | Default classification |
| identity-driven coordination | S,M | S | |
| anonymity_attribution_basis | S,M | S,M | Same three enumerated values in both |
| pre-stress liquidity withdrawal | S,M | M | S has it as "D.3 Pre-Stress Withdrawal" |
| quote-driven manipulation vectors (spread conditioning, withdrawal cycling, depth manipulation…) | S,M | ⊘ | Family membership varies between enumerations |
| OTC bilateral trading/component | S,M (A rel.) | M | Dual status: data limitation AND manipulation vector |
| primary dealer | S,M | M | **Population conflict: 10–20 (S) vs 12–18 (M)** |
| OLO | S,M (A rel.) | ⊘ | Never expanded (Obligation Linéaire) |
| OAT | S,M | ⊘ | |
| Bund | S,M | ⊘ | Bund futures = CICI context instrument |
| Eurex | S,M (A) | ⊘ | |
| downstream exposure / os_downstream_exposure | S,M | S (functional) | Field form in M |
| MTSAM-L data limitation register | S,M (A: L01,L03) | M (partial) | Register extent inconsistent (L01–L07 stated, L08/L10/L11 exist) |
| Removal Register / explicit exclusion register | S,M | M | **Same artifact, two names** (S: "Removal Register", M: "Formally Removed Data Categories") |
| Supervisory Challenge Pack | U,M | ⊘ | |
| supervisory-defensible escalation package | M (S rel.) | ⊘ | S has "ISGO narrative" role; A has "supervisory-defensible evidence package" — cluster to reconcile |
| CCO (Chief Compliance Officer) | U,M (A) | ⊘ | Expansion only inferable; escalation-authority conflict in A (CCO vs analyst) |
| Methodology Lead | U,M | ⊘ | Named governance role |

## 2. Regulator-owned terms → references list (rubric criterion 3)

MAR (+Art. 12, Art. 16), FSMA (expanded only in M), ESMA, ECB (+APP/PEPP/TLTRO),
Belgian Debt Agency (ADA), EMIR, LEI, STOR, MiFID II concepts (LIS, SSTI,
transparency regime), RTS23, RTS24, ESMA FIRDS, ESMA FITRS, GDPR, EU AI Act,
UBO, DMO, NCA (+CONSOB, AMF, BaFin, FCA), Eurex (exchange), Belgian Treasury
Certificate, ISIN, quote stuffing (industry term).

Per the rubric these get a references-list entry, not a glossary definition.
Borderline: STOR and ADA carry heavy project-specific rules on top of the
regulator meaning — likely need both a reference entry and a project-usage note.

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

## 4. Decision register — conflicts and dispositions needed (C8: surface, never harmonise)

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

16. IBE (S usage) ≡ IBE (U/A definition)? and IBEB as separate concept.
17. DAF ≡ DependencyFactor (U)?
18. Removal Register ≡ explicit exclusion register ≡ Formally Removed Data Categories.
19. EvidenceConfidence (M/U) vs ModelConfidence (S/M).
20. escalation readiness (A, lowercase) vs EscalationReadiness (U/M output).
21. DOMINANCE_THRESHOLD (S) vs DOMINANCE_THRESHOLD_PCT (M).
22. "Quote Withdrawal" (S Tier-1 archetype) vs SB-08 Liquidity Withdrawal vs QUOTE_WITHDRAWAL primitive vs pre-stress withdrawal — a four-way near-synonym cluster.
23. Momentum Ignition: RT01 alert (M) vs SB-01 archetype (S) vs BOA=MOMENTUM_IGNITION value (S).
24. MEDIUM-INVESTIGATE vs MEDIUM-STRUCTURED REVIEW (U).
25. Behaviour Categories vs Behavioural Categories (A naming drift; U has a 17-category taxonomy).
26. UCE ≡ Veridict Core Engine (M surface form).
27. BDRS acronym does not match its expansion (U note).
28. SCS vs SCS_bpl — two constructs sharing a name.

Word-overload cluster (glossary must disambiguate, criterion 1):

29. **"Tier"**: pattern tiers 1/2/3 · escalation Tier 1 · AI-governance Tier 1 controls · MTSAM supervisory tier · ECIL feed tiers · SB-26 "Tier 3 investigative hypothesis".
30. **"Level"**: Four-Level Observability (1–4) · CICI levels (1–3) · evidence hierarchy (1–5) · audit chain (L1–L5) · Level 0 closure · BCI levels (named) · classification levels · maturity levels.
31. **"Layer"**: Five-Layer FSMA architecture · four data layers (API stack) · six software layers (A) · three logical layers (A) · UCE/BPL/ECIL/CCL "layers" · Layer 2 feeds (Doc 3).
32. **"IS"**: Intent Score vs the English verb — extraction hazard; also IS vs IScore vs ISS.

Set-level orphans (used somewhere, letter-expanded nowhere): 
33. CQS
34. CCT
35. MDCS
36. CWPS, 
37. QDSP, 
38. PLCS
39. SRI, 
40. IPI, 
41. POFP, 
42. HQLD, 
43. UEEO, 
44. BOA, 
45. EMT, 
46. PFNE, 
47. DQS
48. BIVM
49. VMI
50. OAIC
51. HSL
52. RSN
53. SSF/DF
54. CF
55. OPL
56. EDT
57. ISGO
58. BEP_E
59. BDS
60. SDAIL
61. RAAF
62. NFIL
63. RT/RD
These become the step 3.3 orphan/flag list.

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

## 6. Next steps (per plan §Phase 3)

1. **Nick reviews this list**: cull false positives, rule on the identity
   questions (§4 items 16–28), and confirm the regulator-owned set (§2).
2. Step 3.2 placement is then mechanical (the "Used in" column already encodes it).
3. Step 3.3 drafts one-sentence definitions per surviving term — the ⊘ marks
   and the conflict register become the orphan and conflict flags that C8
   requires humans to disposition.
