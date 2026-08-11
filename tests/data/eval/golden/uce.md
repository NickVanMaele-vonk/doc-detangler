<!--
GOLDEN reference output — step 5.2 stage B (eval artifact, not the live set).
Restructured from samples/blueprint-UCE-shortened.md pinned at blob
4cae72dece7638c1ddec8206a3c6a24610196de0 (eval/README.md), on the approved
reorder plan eval/golden/reorder-plan.md. Section IDs are sha256-derived,
stamped once (recipe in eval/golden/move-map.md). Definition prose inside
<!== concept markers ==> is a verbatim copy of the concept records.
-->

**VERIDICT INTELLIGENCE**

**Universal Core Engine**

MAR Intelligence --- Sector-Agnostic Analytical Architecture

Document 1 of 3

**Version 29 | June 2026 | Confidential**

<!-- sec:u-a48738c9 -->
## Overview

<!-- AI addition:start scope="section" -->
> [AI addition] This section was written to introduce the document; it is
> not derived from a single source passage.

This document specifies the Universal Core Engine, the analytical
architecture shared by every Veridict MAR Intelligence deployment. It is
Document 1 of 3: Sector Intelligence Packs (Document 2) and Institution
Calibration Layers (Document 3) extend it for specific markets and
institutions without changing its core logic.

The document is organised general to specific. Section 1 states what the
engine is and the single analytical question it answers. Section 2 bounds
that scope by stating what the engine is not. Section 3 gives the core
design principles the architecture enforces. Section 4 specifies the
analytical pipeline — the pre-pipeline event builder and the twenty-two
sequential steps. Section 5 lists the checkpoints where a human, not the
engine, acts. Section 6 holds document control: the version history,
including the normative amendment texts recorded inside it, and the index
of Parts. Terms used across several sections are defined directly below
this overview; terms local to one section are defined at the top of that
section; terms shared with the other documents of the set are defined in
the glossary, which is read first.

This extract contains the content of Parts I and II only. Parts III–XX
exist here only as one-line summaries in the Parts index in section 6.
<!-- AI addition:end -->

<!-- sec:u-61b5f491 -->
## Terms defined in this document

Definitions used in more than one section of this document, in dependency
order — a term is defined before any definition below uses it.

**Derisking Assessment** (also known as: nine-condition standard, nine conditions)
<!-- concept:derisking-assessment:start -->
Derisking Assessment: nine conditions, all mandatory.
<!-- concept:derisking-assessment:end -->

**Signal Integrity Summary**
<!-- concept:signal-integrity-summary:start -->
Signal Integrity Summary: weakest_link and escalation_distance documented per signal.
<!-- concept:signal-integrity-summary:end -->

**Domain Independence Filter** (also known as: DIF, domain diversity check)
<!-- concept:domain-independence-filter:start -->
The Domain Independence Filter (DIF) requires cross-domain evidence before HIGH classification, reducing single-domain HIGH inflation; at Step 5b it verifies that CQS is built from contributions in ≥2 independent analytical domains. Single-domain CQT2 (all CQS contributions from domain A only) → HIGH blocked, retained at MEDIUM- INVESTIGATE for structured review. Exception: Collusion Override Path bypasses DIF.
<!-- concept:domain-independence-filter:end -->

**Participant interaction** (also known as: IDS, ISS, IQ, IQ gate, interaction_outcome_score)
<!-- concept:participant-interaction:start -->
IDS (0–3); ISS (0–3); IQ gate. interaction_outcome_score=0 suppresses escalation from interaction.
<!-- concept:participant-interaction:end -->

**Persistence Gate** (also known as: PG, Step 11b)
<!-- concept:persistence-gate:start -->
Persistence Gate (PG) requires behavioural repetition before HIGH absent explicit structures. At Step 11b, for signals reaching CQT2 that have not been blocked by DIF: where no BPL component is confirmed (bpl_drift_flag=FALSE AND session_consistency_confirmed=FALSE AND multi_day_conditioning_detected=FALSE AND cwps_intra < 0.50 AND escalating_dominance_trend=FALSE) AND no participant interaction is active (IDS=0, ISS=0): classification capped at MEDIUM-INVESTIGATE.
<!-- concept:persistence-gate:end -->

**QA Validation** (also known as: Core Design Principle 12)
<!-- concept:qa-validation:start -->
Every qualified signal at MEDIUM- STRUCTURED REVIEW or above must be validated against the Behavioural Scenario Library. Consistency between the engine's assessment and previously validated behavioural patterns is a required analytical output — not an optional quality check. An unvalidated signal is an analytically incomplete signal. QA Validation (§XV.5.4): PASS / PASS WITH VARIANCE / FAIL result recorded per signal.
<!-- concept:qa-validation:end -->

**Escalation Likelihood Score** (also known as: ELS, ELS bands, ELS weight governance)
<!-- concept:escalation-likelihood-score:start -->
ELS (0.0–1.0): f(ExplanationFailure×25%, CCL×25%, CFS×20%, OS×OPL×15%, RRF×10%, CCS_penalty×5%). Rebalanced from original ExplanationFailure×30% to reduce false-positive pressure from binary explanation flag.
<!-- concept:escalation-likelihood-score:end -->


<!-- sec:u-db14c483 -->
## 1. What the Universal Core Engine is

This document specifies the Universal Core Engine --- the sector-agnostic analytical architecture that underpins all Veridict MAR Intelligence deployments. It is independent of market type, instrument class, or institutional context. Sector Intelligence Packs (Document 2) and Institution Calibration Layers (Document 3) extend this engine for specific deployment contexts without modifying its core logic.

This engine is sector-agnostic. It is designed to operate identically across equities, fixed income, derivatives, FX, commodities, crypto, and structured products markets. Market-specific pattern detection, threshold calibration, and contextual enrichment are provided by Sector Intelligence Packs (Document 2). Institutional configuration is provided by Institution Calibration Layers (Document 3). This document specifies only the logic that is identical across all deployments.

The Universal Core Engine answers one question with analytical precision: "Is this behaviour consistent with market manipulation or insider dealing under MAR Article 12?"

<!-- sec:u-b30dd7df -->
## 2. What the engine is not

| The engine is NOT | The engine IS |
| --- | --- |
| A replacement for existing surveillance technology | An intelligence layer that makes surveillance signals analytically meaningful |
| An autonomous decision-maker on STOR filing | A deterministic adjudication system with documented human oversight at every escalation point |
| A sector-specific tool | A generic behavioural adjudication architecture extended by Sector Intelligence Packs |
| An alert management tool | A signal qualification and escalation governance architecture |
| An AI system that determines suspicion | A deterministic system with AI assistance for explanation and narrative drafting only |

<!-- sec:u-8b56eed5 -->
## 3. Core design principles

**AI_HARD controls** (also known as: AI_HARD_01 through AI_HARD_06, Tier 1 controls)
<!-- concept:ai-hard-controls:start -->
Tier 1 controls: AI_HARD_01 through AI_HARD_06 code- level enforcement.
<!-- concept:ai-hard-controls:end -->

**ReplayObject**
<!-- concept:replayobject:start -->
ReplayObject: full score chain and configuration snapshot archived per signal.
<!-- concept:replayobject:end -->

**Minimum Necessary Escalation** (also known as: MNE, MNE principle)
<!-- concept:minimum-necessary-escalation:start -->
Where two scoring approaches produce equally defensible escalation conclusions, the architecture must prefer the one that generates fewer analyst queue entries. The architecture is disposal-oriented first, escalation-oriented second. Detection must be complete; escalation must be selective.
<!-- concept:minimum-necessary-escalation:end -->

**Contextual Suppression Gate** (also known as: CSG, Contextual Suppression Gates)
<!-- concept:contextual-suppression-gate:start -->
Contextual Suppression Gates (CSG) allow classification downgrade under strong contextual legitimacy.
<!-- concept:contextual-suppression-gate:end -->

**Early Disposal Layer** (also known as: EDL)
<!-- concept:early-disposal-layer:start -->
The Early Disposal Layer (EDL) aggressively disposes benign signals before analyst review.
<!-- concept:early-disposal-layer:end -->


Ten foundational principles govern the engine. These are architectural commitments enforced by deterministic gate conditions and hard-coded controls --- not aspirational statements.

| Principle | Statement | Enforcement Mechanism |
| --- | --- | --- |
| 1. Behaviour precedes suspicion | Behavioural deviation is the primary evidentiary foundation. No escalation is driven by participant profile signals alone without corroborating behavioural evidence. | Pattern gate: mandatory at Step 2. No pattern → signal closed at Level 0. |
| 2. Profile alone never constitutes suspicion | Regulatory context (RRF), structural relationships (SRS), and network risk are corroborative amplifiers only. | Evidence Hierarchy (Part V): Level 3--5 cannot substitute Level 1--2. |
| 3. Convergence is required | HIGH and VERY HIGH require coherent alignment across multiple independent analytical dimensions. | CQT gate: CQT2 required for HIGH; CQT3 for VERY HIGH. |
| 4. Evidence gates prevent false convergence | The Dependency Filter ensures convergence is built on genuinely independent signals. | DS gate: DS=2 collapses DAF to 0.0. Convergence invalidated. |
| 5. Economic reality is independently tested | Every qualified signal is independently assessed for economic materiality. | OS gate: OS=0 → MEDIUM ceiling and PriorityScore=0. |
| 6. Causality is required for VERY HIGH | Correlation is insufficient. Causation must be demonstrated. | CCL gate: CCL=0 blocks VERY HIGH regardless of all other scores. |
| 7. Negative evidence reduces suspicion | Legitimate explanations are assessed with equal rigour as incriminatory signals. | Derisking Assessment: nine conditions, all mandatory. |
| 8. AI may assist but never decide | AI enriches explanation and drafts narratives. AI never determines suspicion or triggers STOR filing. | Tier 1 controls: AI_HARD_01 through AI_HARD_06 code- level enforcement. |
| 9. Every decision must be reproducible | Every score, source, and human action is immutably recorded. | ReplayObject: full score chain and configuration snapshot archived per signal. |
| 10. Every escalation must remain supervisor- defensible | Every classification must withstand regulatory examination. | Signal Integrity Summary: weakest_link and escalation_distance documented per signal. |
| 11. Minimum Necessary Escalation (MNE) --- cost- aware design | Where two scoring approaches produce equally defensible escalation conclusions, the architecture must prefer the one that generates fewer analyst queue entries. Escalation is not free --- every unnecessary medium/high classification consumes analyst time, QA resource, and documentation overhead without improving detection quality. The MNE principle embeds this cost awareness: the architecture is disposal-oriented first, escalation-oriented second. Detection must be complete; escalation must be selective. | Applied throughout: (a) Domain Independence Filter (DIF) requires cross-domain evidence before HIGH classification, reducing single- domain HIGH inflation; (b) Persistence Gate (PG) requires behavioural repetition before HIGH absent explicit structures; (c) Contextual Suppression Gates (CSG) allow classification downgrade under strong contextual legitimacy; (d) Early Disposal Layer (EDL) aggressively disposes benign signals before analyst review; (e) Market-Wide Behavioural Reference (MWBR) normalises quote signals against peer behaviour before classifying. |
| 12. QA Validation is a first-class control | Every qualified signal at MEDIUM- STRUCTURED REVIEW or above must be validated against the Behavioural Scenario Library. Consistency between the engine's assessment and previously validated behavioural patterns is a required analytical output --- not an optional quality check. An unvalidated signal is an analytically incomplete signal. | QA Validation (§XV.5.4): PASS / PASS WITH VARIANCE / FAIL result recorded per signal. qa_validation_result field in Output Schema (§XIII.2). FAIL without documented root-cause analysis is a governance failure equivalent to a classification without explanation_trace. |

*New in Version 25: Core Design Principle 12 is added to formalise QA Validation as a first-class architectural control, consistent with the elevation of the Behavioural Concern Framework to Part VI-A.*

<!-- sec:u-43d38f1e -->
## 4. The analytical pipeline

**Enrichment Gate** (also known as: Data enrichment and participant classification)
<!-- concept:enrichment-gate:start -->
IBE input: participant data loaded; SRS (0–3) assigned. SRS=3 assigns DS=2 and redirects to internal abuse pathway. Step 1 receives the IBE object from the IBEB (§XVII.10), not raw alert data.
<!-- concept:enrichment-gate:end -->

**DIF analytical domains**
<!-- concept:dif-analytical-domains:start -->
Domains: (A) Behavioural/Transactional — RT alert patterns, order book behaviour, execution sequences; (B) Persistence — BPL components (BDS, SCS_bpl, MDCS, CWPS, EDT); (C) Interaction — IDS/ISS/IQ participant interaction; (D) Outcome — OS, CCL, CFS, OPL; (E) Contextual — ECIL AMPLIFIES_SUSPICION (only where context amplifies rather than explains).
<!-- concept:dif-analytical-domains:end -->

**Collusion assessment** (also known as: CS, CCaS, CFPS)
<!-- concept:collusion-assessment:start -->
CS (0–3); CCT; CCaS (0–2); CFPS (0–2). CFPS=2 suspends collusion.
<!-- concept:collusion-assessment:end -->

**Six Indicators** (also known as: indicator confirmation)
<!-- concept:six-indicators:start -->
Step 9 indicator confirmation: six indicators reweighted for behaviour- centricity (Volume, Price, Dominance, Timing, Cross-alert, Repetition). IScore (0–24.3).
<!-- concept:six-indicators:end -->

**behaviour-centric reweighting** (also known as: behaviour-centricity)
<!-- concept:behaviour-centric-reweighting:start -->
Behaviour-centric reweighting: raw alert outputs (Volume, Price) are weighted lower than behavioural indicators (Cross-alert, Repetition, Dominance with persistence).
<!-- concept:behaviour-centric-reweighting:end -->

**Kill Switch**
<!-- concept:kill-switch:start -->
Kill Switch forces downgrade to MEDIUM/CLOSE where ≥3 negative conditions apply; it fires before classification lock.
<!-- concept:kill-switch:end -->

**MWBR_metric**
<!-- concept:mwbr-metric:start -->
MWBR_metric = (participant_behaviour_score − peer_median_score) / peer_std_dev.
<!-- concept:mwbr-metric:end -->

**Explanation Fragility Score** (also known as: EFS)
<!-- concept:explanation-fragility-score:start -->
EFS (0–2): three stress tests. EFS=2 → mandatory senior sign-off for closure.
<!-- concept:explanation-fragility-score:end -->

**Minimum Evidence Requirement** (also known as: MER, MER-1, MER-2, MER-3)
<!-- concept:minimum-evidence-requirement:start -->
MER-1: ≥2 MEDIUM+ indicators. MER-2: interaction confirmed. MER-3: OS≥1 OR CCL≥1. All three required.
<!-- concept:minimum-evidence-requirement:end -->

**Three-Tier Escalation modifier** (also known as: Tier 1 single-session signals)
<!-- concept:three-tier-escalation-modifier:start -->
Three-Tier Escalation modifier applies: for Tier 1 single-session signals (no BPL component confirmed, not in active episode), IS≥3 and CQS≥0.90 are required in place of IS≥2 and CQS≥0.85.
<!-- concept:three-tier-escalation-modifier:end -->

**Behavioural Distinctiveness Score** (also known as: BDRS, BDRS_THRESHOLD, BPL_distinctiveness_score)
<!-- concept:behavioural-distinctiveness-score:start -->
BDRS measures whether the participant's behaviour is materially different from peer participants in the same session. BDRS = max(MWBR_metric, BPL_distinctiveness_score). BDRS ≥ BDRS_THRESHOLD (reference: 1.0σ above peer on at least one primary dimension) required for HIGH classification that is not already eligible for AUTO_CLOSE or BATCH.
<!-- concept:behavioural-distinctiveness-score:end -->


### 4.1 Stage 0 and the Intraday Behavioural Event Builder

The analytical pipeline operates in two stages. Stage 0 (pre-pipeline): the Intraday Behavioural Event Builder (IBEB, §XVII.10) groups raw data streams --- trades, quotes, alerts, ECIL context, and participant history --- into Intraday Behavioural Events (IBEs) for each participant-instrument pair within a configurable temporal window. Each IBE is the primary input to Stage 1. Stage 1: twenty-two sequential steps, organised across three phases: structural qualification (Steps 1--11), causal and outcome validation (Steps 12--18), and explanatory adjudication (Steps 19--22). The pipeline receives IBEs, not individual alerts. The architecture is non-compensatory: no dimension in a later step can compensate for a failed gate in an earlier step. Classification is determined by the highest structural gate cleared. Scoring orders signals within classification bands for workload prioritisation. These two roles are strictly separated. Episode consolidation (BEP_E, §XVII.0) operates downstream of the pipeline: classified signals for the same participant are grouped into episodes that constitute the analyst review unit.

### 4.2 The twenty-two steps

| Step | Dimension | Gate/Output | Key Rules |
| --- | --- | --- | --- |
| 1 | Data enrichment and participant classification | ENRICHMENT GATE | IBE input: participant data loaded; SRS (0--3) assigned. SRS=3 assigns DS=2 and redirects to internal abuse pathway. Step 1 receives the IBE object from the IBEB (§XVII.10), not raw alert data. The IBE carries ibe_stream_count, ibe_primitives, ibe_score, ibe_sensitive_timing_flag, and constituent event references. These IBE fields are available to all subsequent pipeline steps as enrichment context. |
| 2 | Pattern detection | GATE: pattern_matc hed=TRUE | Behavioural structures identified across Tier 1/2/3 patterns. No pattern → signal closed at Level 0. |
| 3 | Pattern qualification and confidence | GATE: ≥1 pattern at MEDIUM+ confidence | Structural validation applied. LOW confidence cannot contribute to convergence. |
| 4 | Dependency filter | GATE: DS ≠ 2 | DS (0--2) assessed; DAF applied. DS=2 → convergence invalidated. DS=1 → weight reduced 30%. |
| 5 | Convergence validation (CQS/CQT) | GATE: CQT ≥ 1 | CQT1 (CQS 3--5) = MEDIUM minimum; CQT2 (CQS 6--8) = HIGH minimum; CQT3 (CQS ≥9) = VERY HIGH eligible. |
| 5b | Domain Independence Filter (DIF) | GATE: domain diversity check for HIGH | For signals reaching CQT2 (HIGH eligible): DIF verifies that CQS is built from contributions in ≥2 independent analytical domains. Domains: (A) Behavioural/Transactional --- RT alert patterns, order book behaviour, execution sequences; (B) Persistence --- BPL components (BDS, SCS_bpl, MDCS, CWPS, EDT); (C) Interaction --- IDS/ISS/IQ participant interaction; (D) Outcome --- OS, CCL, CFS, OPL; (E) Contextual --- ECIL AMPLIFIES_SUSPICION (only where context amplifies rather than explains). Single- domain CQT2 (all CQS contributions from domain A only) → HIGH blocked, retained at MEDIUM-INVESTIGATE for structured review. Exception: Collusion Override Path bypasses DIF. Rationale: a strong RT alert cluster in a single instrument session (domain A only, domains B--E absent) indicates an alert, not a behavioural pattern --- it does not warrant HIGH classification. Anonymous quoting attribution constraint: Interaction Domain (C) confirmation based solely on anonymous quote observation --- where no post-session order-level attribution is available and attribution_confidence is LOW --- may satisfy DIF domain C as a contributing domain, but may not independently satisfy DIF as the only non-transactional domain where model_confidence is below MEDIUM. Where domain C is the sole non-domain-A contribution and attribution_confidence = LOW: DIF is not satisfied; classification is retained at MEDIUM-INVESTIGATE pending additional domain evidence (B, D, or E) or post-session attribution confirmation. Consistent with CCT=IMPLICIT cap in anonymous markets (Document 3 §1.2; Document 2 §D.5.3). |
| 6 | Participant interaction (IDS, ISS, IQ) | SCORED OUTPUT + GATE | IDS (0--3); ISS (0--3); IQ gate. interaction_outcome_score=0 suppresses escalation from interaction. |
| 7 | Collusion assessment | SCORED OUTPUT | CS (0--3); CCT; CCaS (0--2); CFPS (0--2). CFPS=2 suspends collusion. |
| 8 | Intent assessment (IS) | SCORED OUTPUT + GATE | IS (0--3). IS=0 → IntentFactor=0 → PriorityScore collapses. EscalationReadiness cannot be TRUE. |
| 9 | Indicator confirmation | SCORED OUTPUT | Six indicators reweighted for behaviour- centricity (Volume, Price, Dominance, Timing, Cross-alert, Repetition). IScore (0--24.3). Behaviour-centric reweighting: raw alert outputs (Volume, Price) are weighted lower than behavioural indicators (Cross-alert, Repetition, Dominance with persistence). Rationale: Volume and Price are direct RT alert translations. Cross-alert, Repetition, and Dominance with BPL context are analytically richer evidence of intentional behaviour. See §IX.1 for indicator weights. |
| 10 | Outcome materiality (OS, OPL) | GATE: OS for classification ceiling | OS (0--2/U) = max(Price, Liquidity, Information Impact). OS=0 → PriorityScore=0; MEDIUM ceiling. |
| 11 | Behavioural consistency and Kill Switch | GATE: Kill Switch fires before classification lock | Kill Switch forces downgrade to MEDIUM/CLOSE where ≥3 negative conditions apply. |
| 11b | Persistence Gate (PG) | GATE: persistence requirement for HIGH without explicit structure | For signals reaching CQT2 that have not been blocked by DIF: where no BPL component is confirmed (bpl_drift_flag=FALSE AND session_consistency_confirmed=FALSE AND multi_day_conditioning_detected=FALSE AND cwps_intra < 0.50 AND escalating_dominance_trend=FALSE) AND no participant interaction is active (IDS=0, ISS=0): classification capped at MEDIUM- INVESTIGATE. The signal does not receive HIGH classification on convergence alone --- behavioural persistence or interaction evidence is required. Exception: (a) Collusion Override Path; (b) EscalationReadiness is confirmed (six gates all met --- EscalationReadiness requires IS≥2 which itself implies pattern persistence); (c) MRaAtioNnDaleA: TgeOnRuiYne\_ AmSanSipEuSlaStio tnr aiglmgoestr from calawmaysp paeirgsnist_ss accororses m≥u l0tip.l7e 5se. sRsiaontsionale: genuine mor ainnvoilpveusl amtuilotipnle i pna rstiocivpaenrtes.i Agnn bond dealer misoalartekde stisng alel-mseosssiotn a sligwnaaly, hso wpeevresrists across mconuvletrigpelnet, sise msosrieo lniksel yo ar fianlsveolves multiple ppoasrittivice.i p(Saencttosr-.s pAenci fiics oraltaiotnealde isningle-session signal, hDoocwumeevnet r2 .c)onvergent, is more likely a false positive than a manipulation event. The Persistence Gate operationalises this market reality without weakening the EscalationReadiness requirement. |
| 11c | Market-Wide Behavioural Reference (MWBR) | SCORED OUTPUT: peer normalisation for quote- domain signals | For quote-domain signals (where ADS/QBRS is the primary scoring dimension): MWBR computes the participant's behaviour relative to the observed peer distribution in the same session and instrument. MWBR_metric = (participant_behaviour_score − peer_median_score) / peer_std_dev. MWBR_score: ANOMALOUS (>2σ from peer median); ELEVATED (1σ--2σ); NORMAL (<1σ); BELOW_NORMAL (<0 --- participant is less active than peers). MWBR_NORMAL → CQS uplift from the quote-domain signal reduced by 30% (not eliminated --- the signal is still present, but it is not anomalous relative to market conditions). MWBR_ANOMALOUS → CQS uplift applied at full rate. Where all active dealers show similar withdrawal/spread widening pattern (market- wide synchronisation): MWBR systematically produces NORMAL or BELOW_NORMAL for all participants → quote-domain signals are contextualised as market-wide, not participant-specific. This is the primary mechanism for suppressing false positives in stressed sovereign bond sessions where legitimate market-wide quote withdrawal is common. |
| 12 | Classification | PRIMARY OUTPUT | LOW/MEDIUM/HIGH/VERY HIGH determined by structural gates. PriorityScore does not influence classification. |
| 13 | PriorityScore computation | SECONDARY OUTPUT (ranking only) | PriorityScore = IScore × CF × IntentFactor × DependencyFactor. Non-compensatory; bounded by gate strength. |
| 14 | Legitimate explanation framework | GATE: ExplanationFa ilure determination | Positive confirmation required (timing, structure, outcome). ExplanationFailure=TRUE where no sufficient explanation. |
| 15 | Causality Confidence Layer (CCL) | GATE: CCL≥1 required for VERY HIGH | CCL (0--2). CCL=0 caps classification at HIGH. |
| 16 | Counterfactual Strength and OPL | GATE (CFS) + SCORED (OPL) | CFS (0--2): but-for argument. CFS≥1 required where OS≥1. OPL (0--2): persistence. |
| 17 | Explanation Fragility Score (EFS) | POST- VALIDATION CHECK | EFS (0--2): three stress tests. EFS=2 → mandatory senior sign-off for closure. |
| 18 | Regulatory Context (RRF) | ADDITIVE AMPLIFIER | RRF (0--6). PriorityScore_final = PriorityScore + RRF. Requires CQT≥2. |
| 19 | Escalation Likelihood Score (ELS) | DERIVED OUTPUT | ELS (0.0--1.0): f(ExplanationFailure×25%, CCL×25%, CFS×20%, OS×OPL×15%, RRF×10%, CCS_penalty×5%). Rebalanced from original ExplanationFailure×30% to reduce false-positive pressure from binary explanation flag. CCS_penalty: where CCS ≥ HIGH and all active ECIL events are CONTRADICTS_PATTERN or FULLY_EXPLAINED, CCS_penalty = −0.05 applied before normalisation (active deduction, not just weight reduction). |
| 20 | Minimum Evidence Requirement (MER) | GATE (pre- EscalationRea diness) | MER-1: ≥2 MEDIUM+ indicators. MER-2: interaction confirmed. MER-3: OS≥1 OR CCL≥1. All three required. |
| 21 | EscalationRead iness gate | FINAL GATE for VERY HIGH | CQT3 AND IS≥2 AND OS≥1 AND ExplanationFailure=TRUE AND CCL≥1 AND CFS≥1. All six simultaneously. NBEC (No- Benign-Explanation Challenge) applied at this gate --- see §VI.3.1. Three-Tier Escalation modifier applies: for Tier 1 single-session signals (no BPL component confirmed, not in active episode), IS≥3 and CQS≥0.90 are required in place of IS≥2 and CQS≥0.85 --- see §VI.3.0. |
| 21b | Behavioural Distinctiveness Score (BDRS) | GATE: required for HIGH (not AUTO_CLOSE or BATCH) | BDRS measures whether the participant's behaviour is materially different from peer participants in the same session. BDRS = max(MWBR_metric, BPL_distinctiveness_score) where BPL_distinctiveness_score measures whether the participant's cross-session behaviour deviates from the peer group's cross-session distribution (not just their own baseline). BDRS ≥ BDRS_THRESHOLD (reference: 1.0σ above peer on at least one primary dimension) required for HIGH classification that is not already eligible for AUTO_CLOSE or BATCH. Where BDRS < threshold: signal retained at MEDIUM-INVESTIGATE. Exception: Collusion Override Path; EscalationReadiness confirmed. Rationale: in sovereign bond dealer markets, stress events cause market- wide behavioural synchronisation. A participant who is behaving similarly to their peers is not exhibiting manipulative distinctiveness --- they are responding to the same market conditions as everyone else. HIGH classification requires that the participant's behaviour is meaningfully different from what their peers are doing. |
| 22 | Derisking Assessment | CLOSURE GATE | Nine-condition standard. All mandatory. RRF≥3 elevates evidential standard. |

<!-- sec:u-03d2b71e -->
## 5. Human intervention checkpoints

**Human Intervention Checkpoint** (also known as: HCP, HCP-1: Analyst Review, HCP-2: CCO Notification, HCP-3: CCO Decision, HCP-4: STOR Filing, HCP-5: Calibration Review)
<!-- concept:human-intervention-checkpoint:start -->
HCP-1: Analyst Review; HCP-2: CCO Notification; HCP-3: CCO Decision; HCP-4: STOR Filing; HCP-5: Calibration Review.
<!-- concept:human-intervention-checkpoint:end -->


| Checkpoint | Trigger | Required Human Action | SLA | Audit Record |
| --- | --- | --- | --- | --- |
| HCP-1: Analyst Review | HUMAN_REVIE W_REQUIRED state | Analyst reviews signal, assesses explanation sufficiency, documents reasoning, assigns FP code or escalates. | HIGH: 5 bd / VERY HIGH: 24 hrs | Analyst ID, timestamp, action, any modification. |
| HCP-2: CCO Notification | HIGH within 5 bd; VERY HIGH within 24 hrs | CCO acknowledges notification. Documents awareness. Assigns priority. | HIGH: 5 bd / VERY HIGH: 24 hrs | CCO ID, acknowledgment timestamp, priority assigned. |
| HCP-3: CCO Decision | CCO_REVIEW state; STOR_Readine ss assessed | CCO reviews full case, approves or modifies STOR draft, or documents decision not to file. | VERY HIGH: 5 bd from notificatio n | CCO ID, decision timestamp, draft version, modifications, reasoning. |
| HCP-4: STOR Filing | CCO approval for filing | CCO executes filing action. System records as CCO- initiated human action. | Immediate upon CCO approval | Filing timestamp, authority, document reference, CCO ID. |
| HCP-5: Calibration Review | Analyst flags pattern or threshold after ≥3 closures of same type | Methodology lead reviews proposed calibration adjustment. Approves or rejects. Documents scope, evidence, version. | No SLA --- governanc e action. | Methodology lead approval, rationale, version increment. |

<!-- sec:u-2f87db53 -->
## 6. Document control

**PIR Amplifier-Only Rule** (also known as: PIR Amplifier Rule, PIR amplifier-only rule)
<!-- concept:pir-amplifier-only-rule:start -->
Participant History (PIR) cannot sole-drive a MEDIUM or HIGH preliminary RSA assessment. The PIR amplifier-only rule (Doc 3 v22 §11.4) is implemented as a capping gate in RSAEngine._assess(): where ALL suspicion factors OTHER THAN participant_history are ABSENT, WEAK, UNCONFIRMED, or POSSIBLE AND participant_history is STRONG or PRESENT, the preliminary assessment is capped at LOW regardless of raw net score.
<!-- concept:pir-amplifier-only-rule:end -->

**assessment_basis**
<!-- concept:assessment-basis:start -->
Audit field: assessment_basis records ‘PIR amplifier-only rule applied: capped at LOW. [Raw net=N]’.
<!-- concept:assessment-basis:end -->

**Price Impact Gate**
<!-- concept:price-impact-gate:start -->
If Price Impact is confirmed ABSENT (VMI LOW, no outcome score), the preliminary assessment is capped at LOW regardless of other factor weights.
<!-- concept:price-impact-gate:end -->

**Behavioural Causality Principle**
<!-- concept:behavioural-causality-principle:start -->
The universal principle that analytical assessments shall distinguish participants that materially influenced the observed pattern from those that merely reacted to prevailing conditions. Concern proportionate to demonstrated behavioural influence, not analytical coincidence.
<!-- concept:behavioural-causality-principle:end -->

**Behavioural Causality Indicator** (also known as: BCI, BCI engine, BCI composite)
<!-- concept:behavioural-causality-indicator:start -->
The Behavioural Causality Indicator (BCI) engine is fully implemented and operational in veridict_uce/bci.py. BCI composite range [0–12] = D1 + D2 + D3 + D4, each scored [0–3].
<!-- concept:behavioural-causality-indicator:end -->

**BCI dimensions D1–D4**
<!-- concept:bci-dimensions-d1-d4:start -->
BCI composite range [0–12] = D1 + D2 + D3 + D4, each scored [0–3]. D1 (Quote Leadership) and D2 (Liquidity Leadership) require HQLD, which is not currently available.
<!-- concept:bci-dimensions-d1-d4:end -->

**BCI levels** (also known as: BCI_PRIMARY_DRIVER)
<!-- concept:bci-levels:start -->
Five levels: Follower (0–2) · Contributor (3–4) · Amplifier (5–6) · Leader (7–9) · Primary Driver (10–12).
<!-- concept:bci-levels:end -->

**Follower Rule**
<!-- concept:follower-rule:start -->
Follower Rule: BCI < 3 → BehaviouralConcern capped at MEDIUM (hard cap, not overridable).
<!-- concept:follower-rule:end -->

**Production Operations Governance** (also known as: Part XX)
<!-- concept:production-operations-governance:start -->
Universal doctrine applying to every deployment regardless of institution or market: throughput governance, degraded-mode doctrine, resiliency and operational failure escalation, queue prioritisation. These principles cannot be varied by Calibration Layers — only operationalised.
<!-- concept:production-operations-governance:end -->

**STOR Reporting Intelligence Layer** (also known as: Doc 7, terminal supervisory articulation layer)
<!-- concept:stor-reporting-intelligence-layer:start -->
Terminal supervisory articulation layer: NIM-MAR four-layer narrative, FSMA fsma_2016_08_d six-section template mapping, RAAF alternative explanation governance, XS-MAR explainability scoring, SCL supervisory confidence tiers, NFIL non-filing defensibility, RCS-MAR challenge simulation, QA-MAR, EU AI Act
<!-- concept:stor-reporting-intelligence-layer:end -->

**ECIL Supplemental Specification**
<!-- concept:ecil-supplemental-specification:start -->
Full operational ECIL specification extending Document 1 Part XVIII: SDAIL (sovereign debt agencies), fifteen sovereign event types, sovereign benchmark mapping, CRS (Context Reliability Score), ECO (Event Cascade Objects), CCS (Contextual Convergence Score), missing context governance doctrine, human override governance.
<!-- concept:ecil-supplemental-specification:end -->


### 6.1 Version history

This document is the Universal Core Engine specification for the Veridict MAR Intelligence Platform. "Substantive" means additions, removals, or redefinitions of named analytical constructs, governance rules, or output fields.

**v23 --- Jun 2025**

Baseline document. Parts I--XX. Full 22-step pipeline, gate architecture (CQT/CQS, OS, IS, CCL, EscalationReadiness), PriorityScore formula, BOA, STOR philosophy, Evidence Hierarchy, Three-Level Review, Output Schema, Statistical Governance (XV.4), ECIL (XVIII), BEP_E / BPL (XVII).

**v24 --- Jun 2025**

Added: §VI.1a Behavioural Concern Layer --- Detection Signal Taxonomy, Behaviour Category Taxonomy (17 categories), Risk Archetype Taxonomy (45 archetypes). §VI.1b Amplifier/Suppressor Assessment, Final Behavioural Concern, Evidence Confidence. §VII.4 PIR. §XIII.2 explainability output fields. Part VI-A Behavioural Concern Framework. Core Design Principle 12 (QA Validation as first-class control). §XV.5 Behavioural Scenario Library (63 scenarios, 195 test cases).

**v25 --- Jun 2025**

Added: §VI.1c IScore mapping. §X.3 MM_SAFEHARBOUR twelve-criteria assessment. Part XI (Insider Dealing). Part XII (Reference Architecture). Behaviour Category 17 (Event-Driven Information Behaviour). §VI.1b shortened to forward-reference. §XVI.3 corrected.

**§XI Reasonable Suspicion Assessment --- PIR Amplifier Rule and Scoring (Amendment UCE-AMD-BVR-001)**

XI.1 PIR Amplifier-Only Rule. Participant History (PIR) cannot sole-drive a MEDIUM or HIGH preliminary RSA assessment. The PIR amplifier-only rule (Doc 3 v22 §11.4) is implemented as a capping gate in RSAEngine._assess(): where ALL suspicion factors OTHER THAN participant_history are ABSENT, WEAK, UNCONFIRMED, or POSSIBLE AND participant_history is STRONG or PRESENT, the preliminary assessment is capped at LOW regardless of raw net score. Audit field: assessment_basis records 'PIR amplifier-only rule applied: capped at LOW. [Raw net=N]'.

XI.2 Price Impact Gate. If Price Impact is confirmed ABSENT (VMI LOW, no outcome score), the preliminary assessment is capped at LOW regardless of other factor weights. Basis: MAR Article 16 requires that the transaction or order 'could have an impact on price'. Where confirmed zero market impact: scoring framework cannot support MEDIUM or HIGH.

XI.3 RSA Net Score Thresholds (v22). Scaling formula: rsa_scaled = min(100, round((net_score / 18) × 100)). Max net score = 18 (six factors × 3 = 18).

**v26 --- Jun 2025**

Added: Version history. All Version 24 change notes updated to Version 25. Sector-specific rationale annotated as Sector Pack examples. Page footer numbers corrected.

**v27 --- Jun 2025**

Added: §VI-A.4.1 Gate-Failure Cause Distinction and Evidence Confidence Caps. §VI-A.4.2 OS=U Disclosure Requirements --- tiered by signal priority.

**v28 --- Jun 2025**

Consolidation and clean-up release. No new constructs added. All changes from v23--v27 consolidated.

**v29 --- Jun 2026**

Added: §VI-A.3.7 Behavioural Causality Principle --- formalises the universal principle that analytical assessments shall distinguish participants that materially influenced the observed pattern from those that merely reacted to prevailing conditions. Concern proportionate to demonstrated behavioural influence, not analytical coincidence.

**§VI-A.3.7 BCI Engine --- Production Implementation (Amendment UCE-AMD-BVR-001)**

VI-A.3.7.1 BCI Engine Operational Status. The Behavioural Causality Indicator (BCI) engine is fully implemented and operational in veridict_uce/bci.py. BCI composite range [0--12] = D1 + D2 + D3 + D4, each scored [0--3]. Five levels: Follower (0--2) · Contributor (3--4) · Amplifier (5--6) · Leader (7--9) · Primary Driver (10--12). Follower Rule: BCI < 3 → BehaviouralConcern capped at MEDIUM (hard cap, not overridable). HIGH gate: BCI ≥ 3 required. VERY HIGH gate: BCI ≥ 7 required in general case. PRIMARY_DRIVER code: BCI ≥ 10 → bci_concern_driver_code = BCI_PRIMARY_DRIVER.

VI-A.3.7.2 D1/D2 Data Dependency --- MTSAM-L08. D1 (Quote Leadership) and D2 (Liquidity Leadership) require HQLD, which is not currently available. In all MTSAM sessions until HQLD is obtained: D1 = 0 (bci_d1_available = FALSE), D2 = 0 (bci_d2_available = FALSE), bci_data_limitation = TRUE. Maximum achievable BCI = D3 + D4 = 6 (Amplifier level maximum). VERY HIGH (BCI ≥ 7) cannot be reached via BCI alone until HQLD is obtained. HQLD remediation is the highest-priority MTSAM-L item (Doc 3 v22 §6 MTSAM-L08).

VI-A.3.7.3 CQS Uplift by BCI Level:

Added: §XIII.2a BCI and Campaign Role Output Fields --- 18 new output fields added to the Holistic Output Schema: bci_score, bci_level, four BCI component fields, bci_data_limitation, campaign_role, five HIGH gate fields, five VERY HIGH Eight-Dimension fields, rsn_triggered, rsn_trigger_code. Derived from Document 3 §12 and §11.9. Do not affect classification.

No changes to the 22-step pipeline, gate architecture, PriorityScore formula, or existing output fields.

*Change note convention: section notes ("New in Version 25") record the version a construct was first introduced. The current version of this document is v29.*

### 6.2 Parts index

| Part | Content |
| --- | --- |
| I | Engine Purpose and Core Design Principles |
| II | Execution Architecture --- Intraday Behavioural Event Builder and 22-Step Analytical Pipeline |
| X --- Review Framework | Three-level review, STOR decision architecture, legitimate explanation framework. §X.3: Market-Maker Safe-Harbour Scoring Integration --- structural effect of MM_SAFEHARBOUR outcomes on ELS, classification, and escalation pathways. |
| XI --- Deployment Maturity | Six-level progressive deployment model with BPL availability by maturity level. MVP specification (P0--P3). |
| XII --- Reference | All formulas, generic alert primitives, performance benchmarks, glossary. |
| XIII --- Analytical Precision | Signal Integrity Summary, ELS weight governance, DAF dual- mechanism, holistic output schema. |
| XIV --- Operational Precision | IS=0 path, SSF/DF, ELS bands, SCS, Summary Principle, CCL indicators, RRF doctrine, OS=U. |
| XV --- Institutional Governance | Model validation, false negative governance, supervisory challenge pack, board governance. §XV.4: Statistical Governance & Calibration Assurance. |
| XVI --- PDRP and Gap Architecture | Participant-Day Risk Profile, no-data-no-risk principle, synthetic testing, ISGO. |
| XVII --- Behavioural Intelligence Architecture | BPL (five persistence components), QBBE, directional RT--RD convergence, OS_BC, regime transition intelligence, adversarial adaptation, automated instability detection, three-level suspicion taxonomy, campaign intelligence roadmap. |
| XVIII --- External Context Intelligence Layer | ECIL: event ingestion, Event Object Schema, contextual directionality logic, event materiality scoring, Temporal Correlation Engine, scoring integration, evidence hierarchy governance. Extended specification in ECIL Supplemental Specification document. |
| XIX --- Operational Deployment Annex | Generic frameworks for Institution Calibration Layers to instantiate with institution-specific values: session processing, governance SLAs, alert throughput, degraded-mode procedures, replay and evidence reconstruction. Note: Part XIX provides frameworks; Part XX provides universal doctrine that cannot be varied by Calibration Layers. |
| XX --- Production Operations Governance | Universal doctrine applying to every deployment regardless of institution or market: throughput governance, degraded-mode doctrine, resiliency and operational failure escalation, queue prioritisation. These principles cannot be varied by Calibration Layers --- only operationalised. |
| Doc 7 --- STOR Reporting Intelligence Layer | Terminal supervisory articulation layer: NIM-MAR four-layer narrative, FSMA fsma_2016_08_d six-section template mapping, RAAF alternative explanation governance, XS-MAR explainability scoring, SCL supervisory confidence tiers, NFIL non-filing defensibility, RCS-MAR challenge simulation, QA-MAR, EU AI Act readiness. |
| ECIL Supplemental Specification | Full operational ECIL specification extending Document 1 Part XVIII: SDAIL (sovereign debt agencies), fifteen sovereign event types, sovereign benchmark mapping, CRS (Context Reliability Score), ECO (Event Cascade Objects), CCS (Contextual Convergence Score), missing context governance doctrine, human override governance. |
