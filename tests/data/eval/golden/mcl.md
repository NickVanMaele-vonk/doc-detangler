**VERIDICT INTELLIGENCE**

MTSAM Institution Calibration Layer \| Document 3 of 3

**Version 21**

<!-- sec:m-62d51646 -->
## Overview

<!-- AI addition:start scope="section" -->
> [AI addition] This section was written to introduce the document; it is
> not derived from a single source passage.

This document specifies the MTSAM Institution Calibration Layer, which
calibrates the Universal Core Engine (Document 1) and the Sovereign
Government Bond Sector Intelligence Pack (Document 2) for the MTS
Associated Markets interdealer venue. It is Document 3 of 3 and is read
last.

The document is organised general to specific. Section 1 holds the
regulatory positioning framework of source Section 0: how the surveillance
architecture is presented and defended before FSMA — the five-pillar
argument, the layered architecture narrative, and the approved and prohibited
formulations. Section 2 holds the market structure material of source
Section 1: the four-layer data architecture and its formally removed data
categories, the venue's key characteristics, the anonymous quoting
framework, and the new surveillance gap the source records. Section 3 holds document
control: the document reference table, the v22 change note, and the source
section banners. Terms used across several sections are defined directly
below this overview; terms local to one section are defined at the top of
that section; terms shared with the other documents of the set are defined
in the glossary, which is read first.

This extract contains source Sections 0 and 1 only; the v22 change note in
Section 3 summarises the Section 11 material that is not part of this
extract.
<!-- AI addition:end -->

<!-- sec:m-f0449e6b -->
## Terms defined in this document

Definitions used in more than one section of this document, in dependency
order — a term is defined before any definition below uses it.

**MTSAM-L07**
<!-- concept:mtsam-l07:start -->
MTSAM-L data limitation register entry L07: MTS surveillance export does not include order-level participant identifiers at quote event level (ORDER_NEW, ORDER_MODIFY, ORDER_CANCEL) — only aggregate market data and trade-level participant IDs are available.
<!-- concept:mtsam-l07:end -->

**RD01**
<!-- concept:rd01:start -->
Alert code RD01 (High EOD volume): Abnormal end-of-day volume concentration in CLOSE_WINDOW.
<!-- concept:rd01:end -->

**RT02**
<!-- concept:rt02:start -->
Alert code RT02 (Abnormal trade count): Abnormal number of trades in a session relative to participant's historical baseline.
<!-- concept:rt02:end -->

**RT05**
<!-- concept:rt05:start -->
Alert code RT05 (Opposite trades): Wash trading, economic neutrality violations, non-arm's-length transactions.
<!-- concept:rt05:end -->

<!-- sec:m-71fdf1cf -->
## 1. Regulatory positioning framework (Section 0)

**architectural separation principle** (also known as: Regulatory positioning doctrine)
<!-- concept:architectural-separation-principle:start -->
Regulatory positioning doctrine: the FSMA regulatory narrative contained in this section is institution-specific. It reflects MTSAM's particular market structure, implemented alert population, enhancement roadmap, and supervisory relationship with FSMA Belgium. It does not modify, supplement, or reinterpret the Universal Core Engine analytical architecture (Document 1).
<!-- concept:architectural-separation-principle:end -->

**behavioural intelligence overlay** (also known as: Behavioural adjudication, behavioural adjudication layer)
<!-- concept:behavioural-intelligence-overlay:start -->
Layer 2 (Behavioural adjudication): assesses each signal through non-compensatory convergence analysis, contextual causality assessment, legitimate explanation testing, and evidence hierarchy. Converts alerts into supervisory-defensible escalation packages.
<!-- concept:behavioural-intelligence-overlay:end -->

**block trade behavioural analysis** (also known as: block trade behavioural intelligence)
<!-- concept:block-trade-behavioural-analysis:start -->
Layer 3: applies behavioural and contextual indicators to high-risk block trade and liquidity-event scenarios already identified through existing RT/RD signals.
<!-- concept:block-trade-behavioural-analysis:end -->

**convergence gate** (also known as: non-compensatory gate architecture, non-compensatory gate methodology)
<!-- concept:convergence-gate:start -->
Non-compensatory gate architecture: convergence must be independently confirmed across multiple analytical dimensions. No single alert can independently drive HIGH or VERY HIGH classification.
<!-- concept:convergence-gate:end -->

**Core Regulatory Position**
<!-- concept:core-regulatory-position:start -->
The Core Regulatory Position: MTSAM considers the currently implemented RT/RD trade-based surveillance scenarios to provide a sufficient foundational detection framework for core trade-based market abuse risks, provided that this framework is complemented by enhanced behavioural analysis, block trade behavioural intelligence, and additional quote-driven surveillance capabilities reflecting the specific characteristics of anonymous quote-driven sovereign bond interdealer markets.
<!-- concept:core-regulatory-position:end -->

**Five-Layer Architecture** (also known as: Five-Layer Architecture for FSMA)
<!-- concept:five-layer-architecture:start -->
The Five-Layer Architecture for FSMA: the complete surveillance architecture as it should be described to FSMA.
<!-- concept:five-layer-architecture:end -->

**Five-Pillar FSMA Argument** (also known as: five-pillar position)
<!-- concept:five-pillar-fsma-argument:start -->
The regulatory position is built on five analytically distinct pillars. Each pillar must be present in any FSMA engagement narrative.
<!-- concept:five-pillar-fsma-argument:end -->

**language governance**
<!-- concept:language-governance:start -->
Approved and Prohibited Formulations: The following table defines which formulations are approved for FSMA engagement, internal compliance documentation, CCO reporting, and Board-level governance reporting.
<!-- concept:language-governance:end -->

**primary signal generation layer** (also known as: foundational detection layer, primary signal generation framework, core trade-based surveillance baseline)
<!-- concept:primary-signal-generation-layer:start -->
Layer 1: produces trade-based market abuse signals covering core MAR Article 12 manipulation risks in the MTSAM market.
<!-- concept:primary-signal-generation-layer:end -->

This section establishes the analytical and regulatory positioning basis for MTSAM's market abuse surveillance framework when engaging with the Financial Services and Markets Authority (FSMA). It defines how the existing RT/RD surveillance scenarios, the behavioural intelligence overlay, and the enhancement roadmap should be presented and defended. This is not a marketing narrative --- it is a formally structured analytical position that is defensible, transparent, and consistent with ESMA supervisory expectations.

*Regulatory positioning doctrine --- architectural separation principle: the FSMA regulatory narrative contained in this section is institution-specific. It reflects MTSAM's particular market structure, implemented alert population, enhancement roadmap, and supervisory relationship with FSMA Belgium. It does not modify, supplement, or reinterpret the Universal Core Engine analytical architecture (Document 1). The analytical logic --- convergence gates, evidence hierarchy, CCL causal requirements, EscalationReadiness conditions, derisking standards, AI governance prohibitions --- is unchanged by this positioning framework. An institution that adopts the same analytical engine with a different regulatory positioning narrative for a different national competent authority (CONSOB, AMF, BaFin, FCA) would implement the Universal Core Engine identically and produce a different Section 0 in their own Calibration Layer. The analytical framework is universal; the supervisory narrative is institutional.*

> The Core Regulatory Position: MTSAM considers the currently implemented RT/RD trade-based surveillance scenarios to provide a sufficient foundational detection framework for core trade-based market abuse risks, provided that this framework is complemented by enhanced behavioural analysis, block trade behavioural intelligence, and additional quote-driven surveillance capabilities reflecting the specific characteristics of anonymous quote-driven sovereign bond interdealer markets.

### 0.1 The five-pillar FSMA argument

The regulatory position is built on five analytically distinct pillars. Each pillar must be present in any FSMA engagement narrative. Together they constitute a coherent, nuanced, and supervisory-mature position that is materially stronger than either claiming complete coverage or conceding fundamental insufficiency.

**Pillar 1 --- The Existing RT/RD Framework Covers the Core Trade-Based Manipulation Universe**

MTSAM's implemented surveillance scenarios already cover the principal trade-based market abuse risks under MAR Article 12. This is a credible and demonstrable claim. It does not require claiming exhaustive or complete coverage --- it requires accurately characterising the scope of what is detected.

| Existing Scenario | MAR Abuse Type Covered | Coverage Assessment |
| --- | --- | --- |
| RT01 --- Momentum ignition | Artificial price movement through aggressive directional trading or order-book pressure | Strong --- both execution-based and quote-induced variants covered |
| RT02 --- Abnormal trade count | Abnormal number of trades in a session relative to participant's historical baseline | Moderate --- provides activity concentration signal, strongest when combined with RT04 or RT01 convergence |
| RT04 --- Price deviation | Off-market pricing, fixing manipulation, benchmark distortion | Strong --- deviation measured in basis points from prevailing MTS mid |
| RT05 --- Opposite trades | Wash trading, economic neutrality violations, non-arm's-length transactions | Strong --- counterparty clustering and net position neutrality assessed; OTC bilateral component limited by MTSAM-L05 |
| RT08 --- Liquidity stress proximity | Liquidity triggering, pre-suspension abuse, stress exploitation | Strong --- most important fixed income-specific alert; PRE_SUSPENSION_WINDOW captured. Primary detection pathway for pre-stress manipulation given RT22 is not yet implemented |
| RD01 --- High EOD volume | Abnormal end-of-day volume concentration in CLOSE_WINDOW | Moderate --- provides volume context for RD02/RD03/RD04 convergence; Marking-the-Close Triad requires RD01 + RD02 + RD04 simultaneously |
| RD02 --- Participant market share | Closing-window dominance, market control, concentration at reference price formation | Strong --- calibrated relative to dealer population (12--18 ADA primary dealers); primary EOD dominance signal |
| RD03 --- EOD price influence | Marking the close, reference price manipulation, NAV influence | Strong --- downstream exposure to repo, ECB collateral, NAV confirmed as mandatory assessment |
| RD04 --- Closing price deviation | Off-market closing execution, closing reference price distortion | Strong --- 2bps threshold for benchmark OLOs; 1bps for off-benchmark tenors |

> FSMA framing: the existing RT/RD framework should not be presented as the full surveillance architecture. It should be presented as the primary signal generation layer --- the detection foundation on which behavioural adjudication, contextual enrichment, and quote intelligence are built. That is a much stronger and more credible regulatory position.

**Pillar 2 --- The Remaining Gap Is Primarily Quote-Driven Behaviour**

The principal residual detection gap in the MTSAM surveillance framework does not relate to absent trade-based scenarios. It relates to the need for enhanced visibility over quote-driven behavioural dynamics that are inherent to anonymous interdealer sovereign bond markets. This framing is analytically accurate, intellectually honest, and significantly more credible than claiming trade-surveillance gaps.

| Residual Gap | Nature of Gap | Enhancement Layer Required |
| --- | --- | --- |
| Quote withdrawal patterns before stress events | Trade data alone cannot detect systematic pre-stress liquidity withdrawal that occurs through quoting behaviour without execution. The manipulation may leave no trade footprint. | Quote intelligence architecture (QBRS, QBLI, QBCCL) --- Document 2 Section H |
| Anonymous order-book manipulation | Spread conditioning, depth manipulation, and systematic quote pressure in the anonymous MTS order book are not visible in trade-level surveillance. The manipulation mechanism is quoting, not trading. | Quoting behaviour detection architecture --- Document 2 Section D; MTSAM anonymous attribution framework --- Section 1.2 of this document |
| Cross-session cumulative patterns below threshold | Gradual dominance building, systematic conditioning, and multi-session campaigns that remain below individual session thresholds are not detectable from individual alert assessments. | Behavioural Persistence Layer (BPL) --- Universal Core Engine Document 1 Part XVII |
| Contextual causality assessment | The distinction between market-driven behaviour and manipulative behaviour --- the single most important analytical question in sovereign bond markets --- cannot be resolved from alerts alone without structured contextual intelligence. | External Context Intelligence Layer (ECIL) --- Document 1 Part XVIII |

**Pillar 3 --- The Existing RT/RD Framework Becomes Materially Stronger Through Behavioural Analysis**

This is the analytically strongest pillar. The implemented surveillance scenarios should not be assessed in isolation. Their effectiveness materially increases when analysed through behavioural convergence, contextual enrichment, participant dominance analysis, repetition assessment, and cross-alert correlation. A single RT01 alert has limited analytical value. The same RT01 alert combined with RD02 dominance confirmation, RDCS cross-pass scoring, ECIL contextual assessment, and BPL session consistency confirmation constitutes a supervisory-defensible escalation package.

| Enhancement Layer | Role | Effect on Existing RT/RD Signals |
| --- | --- | --- |
| Behavioural convergence engine (Veridict Core Engine) | Non-compensatory gate architecture: convergence must be independently confirmed across multiple analytical dimensions. No single alert can independently drive HIGH or VERY HIGH classification. | RT01 assessed not as a standalone trigger but as one convergence dimension alongside intent confirmation, outcome materiality, causal evidence, and explanation failure. False positive rate materially reduced. |
| RT--RD cross-pass scoring (RDCS) | Intraday RT alerts combined with EOD RD materiality confirmation to produce a composite risk score that reflects both the behaviour and its market consequence. | RT04+RD04 combination (intraday price deviation + closing price influence) produces a presumptive STOR review signal. Neither alert alone achieves this --- the combination does. |
| Contextual enrichment (ECIL) | Structured assessment of whether each signal occurred in the context of a market-moving event that provides an alternative explanation --- ADA auction, ECB decision, macro release. | Where ECIL confirms an ECB announcement coincides with the RT01 event: the momentum signal may be CONTRADICTS_PATTERN (event provides a full alternative explanation). Where no event exists: absence_of_contemporaneous_exogenous_cause=TRUE strengthens CCL causal evidence. |
| Repetition and recurrence analysis (BPL) | Cross-session pattern detection converting isolated alert episodes into structural campaign evidence. | RT01 in a single session may be insufficient. The same RT01 pattern across six sessions in LOOKBACK_30D, combined with RD02 CLOSE_WINDOW dominance confirmation across the same sessions, produces a campaign-level dominance and momentum signal. |
| Participant-specific baseline comparison (QBBE/POFP) | Comparison of current behaviour against each participant's own historical profile --- not against a population threshold. | A primary dealer whose RD02 fires at 20% CLOSE_WINDOW share is assessed differently where their historical CLOSE_WINDOW share is 5% (highly anomalous) versus 18% (within normal range). False positives attributable to primary dealer market making obligations are systematically reduced. |

**Pillar 4 --- Block Trade Behavioural Analysis Closes an Important Structural Gap**

MTSAM has already initiated behavioural categorisation methodologies focusing on high-risk block trade and liquidity-event scenarios using behavioural and contextual indicators. This practical enhancement work is analytically significant and politically important.

| Existing Analytical Work | Significance for FSMA Positioning |
| --- | --- |
| RT/RD categorisation logic applied to alert population | Demonstrates structured analytical methodology already applied to the existing alert universe --- not an aspiration but an operational capability. |
| Behavioural indicators applied to block trade scenarios | Provides direct evidence that block trade manipulation --- including price positioning near close, execution at off-market prices, and downstream reference price exploitation --- is subject to behavioural assessment beyond alert-level detection. |
| Liquidity suspension analysis integrated with alert categorisation | The combination of RT08 (liquidity stress) with behavioural context (dominance, repetition, cross-alert) is already operationalised. This directly addresses one of the most important MAR risks in sovereign bond markets. |
| Risk-based prioritisation (LOW/MEDIUM/HIGH) | Demonstrates that the surveillance architecture already incorporates risk stratification --- a materially more sophisticated approach than simple alert counting that is directly aligned with ESMA's risk-based surveillance expectations. |

**Pillar 5 --- Quote Intelligence Is the Logical and Proportionate Enhancement Layer**

In a quote-driven sovereign bond interdealer market, effective behavioural surveillance requires not only trade surveillance but also visibility over liquidity formation, quote behaviour, and order-book dynamics.

> The argument is not: 'the current framework is insufficient.' The argument is: 'the current framework is sufficient as a foundational trade-surveillance layer, and the proposed quote intelligence enhancement closes the residual gap that is specific to the quote-driven nature of MTSAM's market structure.' These are materially different positions with very different regulatory implications.

### 0.2 The five-layer architecture for FSMA

The following table presents the complete surveillance architecture as it should be described to FSMA. Each layer's role is described precisely.

| Layer | Role --- Approved Formulation | Current Status |
| --- | --- | --- |
| Layer 1: Existing RT/RD surveillance scenarios | Primary signal generation layer --- produces trade-based market abuse signals covering core MAR Article 12 manipulation risks in the MTSAM market. | Operational. Nine implemented scenarios: RT01, RT02, RT04, RT05, RT08, RD01, RD02, RD03, RD04. Calibrated for MTSAM dealer population and OLO market structure. |
| Layer 2: Behavioural adjudication (Veridict Core Engine) | Behavioural intelligence overlay --- assesses each signal through non-compensatory convergence analysis, contextual causality assessment, legitimate explanation testing, and evidence hierarchy. Converts alerts into supervisory-defensible escalation packages. | In development. Pilot validation planned against 90 days historical MTSAM data. |
| Layer 3: Block trade behavioural analysis | Risk-based enhancement --- applies behavioural and contextual indicators to high-risk block trade and liquidity-event scenarios already identified through existing RT/RD signals. | Partially operational. PowerQuery-based categorisation logic applied to alert population. |
| Layer 4: Quote intelligence surveillance --- THE SINGLE MOST IMPORTANT STRATEGIC ENHANCEMENT DEPENDENCY | Quote-driven market enhancement --- extends surveillance to order-book-visible manipulation mechanisms (withdrawal cycling, spread conditioning, depth manipulation, pre-stress withdrawal) that are not visible in trade-level data. Pre-stress liquidity withdrawal (RT22) is the most important manipulation vector in sovereign bond dealer markets. This layer is the only pathway to its full detection --- RT08 provides compensating coverage, not equivalent replacement. | Specified in Document 2 (Sector Intelligence Pack). Dependent on MTS order book data availability. Addressable through MTSAM-L07 remediation. |
| Layer 5: Contextual enrichment and replayable audit | Supervisory defensibility layer --- structured ECIL contextual assessment, immutable audit trail, replay capability, and Supervisory Challenge Pack assembly ensuring every escalation and every closure can be analytically defended before FSMA. | Specified in Document 1 (Core Engine Part XVIII) and Document 6 (Audit Trail). Deployed with the behavioural adjudication layer. |

### 0.3 Language governance — approved and prohibited formulations

The following table defines which formulations are approved for FSMA engagement, internal compliance documentation, CCO reporting, and Board-level governance reporting.

| Context | Approved Formulations | Prohibited Formulations | Why Prohibited |
| --- | --- | --- | --- |
| Describing the existing RT/RD framework | Foundational detection layer; primary signal generation framework; core trade-based surveillance baseline; meaningful MAR coverage for trade-based manipulation risks | Complete coverage; full MAR coverage; exhaustive detection; sufficient standalone framework; all scenarios covered | Claims completeness that cannot be substantiated; creates regulatory exposure if any gap is subsequently identified |
| Describing the remaining gap | Principal residual enhancement area primarily concerns quote-driven behavioural dynamics; structural enhancement area relating to anonymous interdealer market characteristics; complement to the existing framework | Current scenarios are insufficient; significant gaps in surveillance; fundamental weaknesses in detection | Overstates weakness; undermines Pillar 1; creates regulatory leverage for FSMA that is disproportionate to the actual risk profile |
| Describing the enhancement plan | Complement the existing framework; extend detection capability; address the specific characteristics of the market structure; proportionate enhancement | Replace the existing framework; correct deficiencies; remediate fundamental failings | Implies the existing framework is defective rather than foundational; undermines the five-pillar position |
| Describing analytical capability | Structured behavioural intelligence architecture; converging analytical approach; non-compensatory gate methodology; supervisory-defensible escalation packages | The system catches all market abuse; zero false negatives; complete manipulation detection | No surveillance system provides complete detection; claiming this creates legal exposure and is not credible to any experienced regulator |
| Describing coverage limitations (ISGO) | Known analytical limitations documented and actively remediated; transparent surveillance coverage self-assessment; structured gap identification and quantification | No gaps identified; full data availability; complete analytical coverage | Contradicted by MTSAM-L01 through MTSAM-L07; creates false impressions that will be exposed at the first supervisory inspection |
| Describing RT22 absence and RT08 compensation | RT08 provides compensating coverage for the absent RT22 alert; RT08 timing analysis partially addresses pre-stress withdrawal; the RT22 gap remains a CRITICAL remediation priority | RT08 provides equivalent coverage for RT22; pre-stress withdrawal is fully detected; the RT22 gap has been closed through RT08 analysis | RT08 detects stress events --- it does not detect the anticipatory withdrawal that causes them. These are analytically distinct. RT08 is compensating coverage. It is not equivalent replacement. |
| Describing data limitation conclusions | Data limitation prevents full assessment; analytical capability constrained where data is absent; gap documented in ISGO; absence of data does not confirm absence of risk | No suspicious activity detected in OTC bilateral component; OTC activity cleared; no manipulation identified in quote behaviour | Data absence is not evidence of risk absence. Stating 'no suspicious activity detected' where data was absent is a false negative assertion with regulatory consequences. |
| Describing Market Maker safe-harbour outcomes | MM_SAFEHARBOUR_CONFIRMED removes the mandatory CCO escalation pathway --- this is a structural scoring effect, not only an explanatory label; safe-harbour provides a governed, auditable non-escalation basis; each criterion was specifically assessed and documented | Market making was considered and not an issue; no concerns with liquidity provision; behaviour is consistent with normal market making | MM_SAFEHARBOUR is a seven-criteria test with documented outcome codes. The correct formulation names the outcome code (CONFIRMED/PARTIAL/FAILED) and references the specific criteria assessed. |
| Describing non-filing decisions (CLOSED_JUSTIFIED) | Signal was assessed on [specific evidence]; alternative explanation [category] was accepted because [specific proportionality basis]; specific EscalationReadiness condition [named] was not met; non-filing documentation package completed per Document 7 §8b | Signal did not meet threshold; no reasonable grounds identified; no suspicious activity detected | Non-filing language must be as specific as filing language. A generic 'no reasonable grounds' closure is regulatorily equivalent to a STOR filed with 'suspicious activity detected' --- both are analytically empty. |
| Describing supervisory confidence (SCL tier) | SCL-COMPELLING: the convergent evidence across [n] dimensions constitutes a strong basis for reasonable grounds; SCL-PRECAUTIONARY: reasonable grounds exist notwithstanding [specific uncertainty] --- precautionary filing is appropriate because [specific basis] | The evidence clearly shows manipulation; the behaviour was obviously suspicious; we are certain that market abuse occurred | SCL language must match the SCL tier. Certainty language in a PRECAUTIONARY STOR is a language governance failure. Probabilistic framing in a COMPELLING STOR understates the analytical quality. |

> FSMA will evaluate MTSAM's surveillance posture on five dimensions that are more important than alert count: (1) Can suspicious behaviour be identified? (2) Can investigations be defended? (3) Is the methodology coherent? (4) Is the governance credible? (5) Are gaps acknowledged transparently and actively remediated? The five-pillar position in Section 0.1 and the language governance in Section 0.3 are designed to produce strong answers to all five questions.

<!-- sec:m-b7d82c27 -->
## 2. MTSAM market structure (Section 1)

**Alert Abstraction Layer**
<!-- concept:alert-abstraction-layer:start -->
Alert Abstraction Layer (Section 3.2): translates MTS alert names to UCE behavioural primitives.
<!-- concept:alert-abstraction-layer:end -->

**anonymity_attribution_narrative**
<!-- concept:anonymity-attribution-narrative:start -->
Every quote-domain interaction signal reaching HIGH or VERY HIGH classification must include an anonymity_attribution_narrative field. This is a MTSAM mandatory field not required in non-anonymous deployments.
<!-- concept:anonymity-attribution-narrative:end -->

**automated narrative generation**
<!-- concept:automated-narrative-generation:start -->
Automated narrative generation (§XX.5.1 Doc 1): the three narrative templates (MEDIUM-BATCH closure, MEDIUM-INVESTIGATE reviewed, STOR narrative input) are populated from structured Level 1–4 audit chain fields and passed to the LLM for fluent narrative assembly.
<!-- concept:automated-narrative-generation:end -->

**Client Portfolio / Order Flow Intelligence**
<!-- concept:client-portfolio-order-flow-intelligence:start -->
Any feed of client order books, pending RFQ flows, client portfolio positions, or institutional flow data received by dealers outside the MTS anonymous order book.
<!-- concept:client-portfolio-order-flow-intelligence:end -->

**correlated instrument pair**
<!-- concept:correlated-instrument-pair:start -->
Correlated instrument pairs active for this deployment: OLO/Bund (SD02), OLO/OAT (SD02), OLO cross-maturity.
<!-- concept:correlated-instrument-pair:end -->

**Cross-Venue Surveillance Feed**
<!-- concept:cross-venue-surveillance-feed:start -->
Any real-time or near-real-time data feed from other electronic trading venues (EuroMTS, Tradeweb, Bloomberg) or OTC reporting platforms.
<!-- concept:cross-venue-surveillance-feed:end -->

**Futures Position Intelligence**
<!-- concept:futures-position-intelligence:start -->
Bund futures, OAT futures, or any derivatives position data for MTSAM participants.
<!-- concept:futures-position-intelligence:end -->

**ISGO-02**
<!-- concept:isgo-02:start -->
ISGO-02: order-level quote attribution data absent from surveillance export.
<!-- concept:isgo-02:end -->

**Market Making explanation category**
<!-- concept:market-making-explanation-category:start -->
Market Making explanation category: requires positive confirmation that quoting was symmetric and consistent with ADA obligation. Obligation documentation must be on file.
<!-- concept:market-making-explanation-category:end -->

**MTS Trades**
<!-- concept:mts-trades:start -->
MTS Trades: Every executed trade on the MTS Associated Markets platform: instrument, price, size, timestamp, aggressor side, participant identifiers. The foundational trade stream for all RT alert primitive detection.
<!-- concept:mts-trades:end -->

**MTSAM API Stack**
<!-- concept:mtsam-api-stack:start -->
MTSAM API Stack: The MTSAM analytical engine operates across four data layers.
<!-- concept:mtsam-api-stack:end -->

**OTC Positions / Repo Intelligence**
<!-- concept:otc-positions-repo-intelligence:start -->
Any systematic feed of participant OTC bilateral book positions, repo positions, or net exposure across instruments.
<!-- concept:otc-positions-repo-intelligence:end -->

**supervisory challenge pre-emption**
<!-- concept:supervisory-challenge-pre-emption:start -->
FSMA or a regulatory authority reviewing a quote-based interaction signal will ask: 'How did you identify coordination if the order book was anonymous?' The answer must be in the case record, not produced in response to the challenge.
<!-- concept:supervisory-challenge-pre-emption:end -->

### 1.0 MTSAM API stack — data architecture and scope specification

The MTSAM analytical engine operates across four data layers. This section formally specifies which data feeds are in scope, what each feed contributes to the analytical architecture, and what feeds are explicitly excluded. The explicit exclusion register is architecturally important: it documents that the model was designed around what MTSAM can realistically obtain, not around what a theoretically complete surveillance system would require.

**Layer 1 --- Core Surveillance (Primary analytical inputs)**

| Layer | Data Feed / API | Status | Scope for MTSAM | Engine Integration Point | Key Limitation / Dependency |
| --- | --- | --- | --- | --- | --- |
| Core | MTS Trades | IN SCOPE | Every executed trade on the MTS Associated Markets platform: instrument, price, size, timestamp, aggressor side, participant identifiers. The foundational trade stream for all RT alert primitive detection. | UEEO primary trade stream. SRS, MWBR volume dimension, MDCS, CWPS, BPL, BEP_E constituent trades, BLOCK_TRADE primitive. | Trade timestamps may be EOD only for OTC bilateral component (MTSAM-L01). Aggressor flag availability from MTS export must be confirmed. |
| Core | MTS Alerts (RT/RD) | IN SCOPE | Nine implemented alert types from MTS S.p.A. surveillance system: RT01, RT02, RT04, RT05, RT08 (intraday RT); RD01, RD02, RD03, RD04 (end-of-day RD). | Alert Abstraction Layer (Section 3.2): translates MTS alert names to UCE behavioural primitives. All nine alerts mapped to Domain 3 primitive codes. | Nine of c.30 implemented MTS alerts mapped. RD05 and RD06 not yet implemented --- identified as high-priority additions in enhancement roadmap. |
| Core | MTS Quotes / Order Book | IN SCOPE (partial) | Aggregated order book data from MTS export: best bid/ask, depth at each level, spread, volume at touch. Anonymous at quote event level during session. Post-session participant attribution via order ID cross-referencing where MTS export includes order IDs. | QBBE quote baseline engine, MWBR quote dimension, PLCS, QDSP, SPREAD_WIDENING/QUOTE_WITHDRAWAL/LIQUIDITY_REMOVAL primitives, SRI, QML. | Order-level participant IDs at quote event level absent from current MTS surveillance export (MTSAM-L07). Quote intelligence operates at session-level aggregate precision until HQLD is obtained. |
| Core | Instrument Reference Data | IN SCOPE | Static and semi-static instrument master data for all OLO instruments: ISIN, maturity date, coupon, benchmark designation (on-the-run / off-the-run), instrument cluster assignment, OLO series classification. | Instrument cluster assignment for BEP_E episode grouping. IPI instrument persistence scoring. BLOCK_TRADE_THRESHOLD instrument-specific values. SD02 cross-instrument pair definitions. | Static feed; update required on each new ADA issuance. Benchmark designation changes with each new issuance cycle --- automated update from ADA new issuance notification preferred. |

**Layer 2 --- Context (External market context for ECIL enrichment)**

| Data Feed / API | Status | Scope for MTSAM | Engine Integration Point | Key Limitation / Dependency |
| --- | --- | --- | --- | --- |
| Belgian Debt Agency (ADA) Calendar | IN SCOPE | Scheduled OLO auction dates, target issue amounts (where published), auction results (clearing price, allotment ratio, bid-cover ratio) as published on the ADA website. Also: Belgian Treasury Certificate auction calendar. | ECIL auction calendar: SF_issuance flag, AUCTION_WINDOW activation, RD05 timing context. Pre-event positioning analysis (SB-05, SB-28/SB-29 frameworks). | Published auction calendar (dates, target size). Exact clearing price and allotment data available post-auction. Undisclosed changes to auction size or pricing are Level 4 data (outside MTSAM perimeter). |
| ECB Event Calendar | IN SCOPE | Scheduled ECB Governing Council meetings, monetary policy decision dates, APP/PEPP/TLTRO announcement dates. Published on ECB website. | ECIL ECB event calendar: CRS_VERY_HIGH for surprise ECB events. MANDATORY_ASSESS override where dominant pre-ECB positioning AND IS ≥ 2. | Scheduled events: fully available. Unscheduled ECB communications require real-time press release monitoring --- recommend ECB RSS feed integration. ECB internal deliberations are Level 4 data. |
| Economic Calendar | IN SCOPE | Macro economic data releases with market-moving potential for OLO yields: Eurozone inflation (CPI, HICP), German GDP, Belgian GDP, Eurozone PMI, US non-farm payrolls, ECB staff projections. | ECIL economic event calendar: CRS scoring by event type and surprise magnitude. ECIL SUPPORTS_EXPLANATION where participant behaviour coincides with high-CRS macro release and MWBR confirms population-wide reaction. | Scheduled release dates: fully available. Actual release values and surprise magnitude require real-time data feed. Surprise magnitude ≥ 2σ from consensus = CRS_VERY_HIGH for that release. |
| Eurex Public Market Data (Bund Futures) | IN SCOPE (Level 1+2 immediate; Level 3 subject to pilot evaluation) | Public Bund futures settlement price, daily volume, open interest, and intraday price bars from Eurex published market data. Level 1+2 (EOD): no additional cost. Level 3 (intraday 5-minute bars): requires Eurex Public Data Feed real-time or Bloomberg/Refinitiv real-time subscription. | ECIL integration: CICI Level 1 event type (FUTURES_ACTIVITY_ELEVATED). CMCS Level 2 adds +0.50 CQS as contextual amplifier for SB-26 hypothesis. CRITICAL BOUNDARY: public market data only. Participant futures positions remain outside the perimeter. | Six-component CMCS weighting: CMCS = (0.25 × cmcs_s1_olo_dominance) + (0.20 × cmcs_s2_futures_volume) + (0.15 × cmcs_s3_oi_change) + (0.15 × cmcs_s4_basis_move) + (0.15 × cmcs_s5_olo_yield) + (0.10 × cmcs_s6_sovereign_spread). cmcs_confirmed threshold = 0.55 standard / 0.45 with ECB or ADA event co-occurrence. |

**Layer 3 --- Intelligence (Participant and entity context)**

| Data Feed / API | Status | Scope for MTSAM | Engine Integration Point | Key Limitation / Dependency |
| --- | --- | --- | --- | --- |
| OpenSanctions | IN SCOPE | Open-source sanctions, regulatory enforcement, and financial crime database covering OFAC, EU sanctions, national regulatory actions, PEP lists, and adverse media. API access at opensanctions.org. Updated daily. | RRF (Regulatory Risk Factor) enrichment: participant LEI lookup against OpenSanctions sanctions lists and regulatory enforcement database. HSL_prior_stor proxy where formal enforcement action is in the database. | Coverage: comprehensive for OFAC, EU, and major national sanctions. Belgian-specific FSMA enforcement actions may not be present unless FSMA publishes to a machine-readable database. Recommend supplementing with manual FSMA enforcement database check. |
| OpenCorporates | IN SCOPE | Open database of global company registrations, corporate structures, beneficial ownership (where public), and registered addresses. Commercial API licence required for systematic use. | Participant entity mapping: for each participant LEI, OpenCorporates lookup provides corporate registration, group structure, and ownership information. Counterparty relationship mapping: where BT-06 counterparty concentration or PI09 block trade network is confirmed, can identify whether concentrated counterparties are corporate affiliates. | Coverage: strong for Western European entities. Beneficial ownership data may be incomplete where public registries have not yet implemented UBO disclosure. Commercial API licence required; confirm with legal/procurement. |

**Layer 4 --- AI (Narrative generation and analyst query interface)**

| Data Feed / API | Status | Scope for MTSAM | Engine Integration Point | Key Limitation / Dependency |
| --- | --- | --- | --- | --- |
| Azure OpenAI / AWS Bedrock (LLM) | IN SCOPE | Large Language Model API for automated analytical narrative generation and analyst augmentation. Azure OpenAI (GPT-4 class models) or AWS Bedrock (Claude class models). Selection between providers based on institutional data residency, procurement, and latency requirements. | Automated narrative generation (§XX.5.1 Doc 1): the three narrative templates (MEDIUM-BATCH closure, MEDIUM-INVESTIGATE reviewed, STOR narrative input) are populated from structured Level 1--4 audit chain fields and passed to the LLM for fluent narrative assembly. The LLM does not make analytical decisions --- it renders pre-computed structured fields into readable prose. | Strict governance: the LLM is a rendering and summarisation layer, not an analytical engine. All LLM outputs are reviewed by the analyst before any disposal decision is recorded. Data residency: OLO trade data and participant identifiers must not be transmitted to LLM endpoints outside approved data residency boundaries. Azure OpenAI (EU data residency) preferred for GDPR compliance. |
| Azure AI Search | IN SCOPE | Vector search and full-text search index for the analytical knowledge base: STOR precedents, FSMA guidance documents, MAR technical standards, internal policy documents, and historical signal/episode records. | Analyst query interface: analyst asks a natural language question about a signal or episode and receives ranked results from the indexed knowledge base. STOR precedent retrieval when drafting a STOR narrative. | Data classification: STOR documents and signal records contain confidential supervisory information. The Azure AI Search index must be deployed within the institution's secure environment, not a shared or public search instance. |

> Data stack governance: any addition of a new data feed to the MTSAM API stack requires CCO approval and documentation in the calibration change register. A new data feed changes the analytical perimeter of the model and may introduce new detection capabilities, new data quality risks, and new data residency obligations.

### 1.0.1 Formally removed data categories

Earlier design iterations of the MTSAM analytical architecture referenced data categories that are not obtainable on a systematic basis within the MTS surveillance perimeter. These are formally removed from the operational model.

| Feed / Data Type | Description | MTSAM Limitation | Removal Rationale and Residual Treatment |
| --- | --- | --- | --- |
| OTC Positions / Repo Intelligence | Any systematic feed of participant OTC bilateral book positions, repo positions, or net exposure across instruments. | MTSAM-L01, MTSAM-L10, MTSAM-L11. | Removed. MTSAM does not receive participant OTC book positions on a systematic basis. The OTC bilateral component of the MTS feed provides T+1 trade reports only. Building the model around an assumption of OTC position visibility would produce a framework that cannot be operationalised. |
| Futures Position Intelligence | Bund futures, OAT futures, or any derivatives position data for MTSAM participants. | MTSAM-L10: cross-asset futures data absent. | Removed. The SB-26 cash bond / futures interaction archetype is retained as a Tier 3 investigative hypothesis but is explicitly not a primary detection pillar. The model does not claim to detect confirmed cash-futures manipulation from MTSAM data alone. |
| Cross-Venue Surveillance Feed | Any real-time or near-real-time data feed from other electronic trading venues (EuroMTS, Tradeweb, Bloomberg) or OTC reporting platforms. | Outside MTS surveillance perimeter. | Removed. The Four-Level Observability Framework (§A.4.1 Doc 2) correctly positions MTS-only cross-instrument intelligence (Level 1) and public market context (Level 2) as the operational detection layers. Cross-venue analytical hypotheses (Level 3) use only data already in scope. |
| Client Portfolio / Order Flow Intelligence | Any feed of client order books, pending RFQ flows, client portfolio positions, or institutional flow data received by dealers outside the MTS anonymous order book. | MTSAM-L11: RFQ order flow absent. | Removed. MTSAM has no access to dealer client books or pending RFQ flows. The SB-30 misuse of confidential order information archetype uses a market footprint detection approach based solely on MTS trade timing. |

### 1.1 MTS Associated Markets — key characteristics

| Characteristic | MTSAM Specification | Calibration Consequence |
| --- | --- | --- |
| Market type | Electronic interdealer trading venue for Belgian OLO sovereign bonds (and selected other sovereign instruments). Quote-driven: price formation through dealer quotes, not through auction order matching. | Quote intelligence architecture (Document 2, Section D and H) is primary detection framework. QBRS is co-primary with PriorityScore for all signals generated on MTSAM. |
| Participant universe | Primary dealers authorised by the Belgian Debt Agency (ADA) to quote OLOs. Typically 12--18 dealers active at any given time. | All dominance thresholds calibrated relative to this dealer population size. DOMINANCE_THRESHOLD_PCT = session_ADV / active_dealer_count × sector_sensitivity_multiplier. dominance_population_size = documented ADA primary dealer list. |
| Trading hours | Electronic trading: 08:00--17:00 CET (Brussels). OTC bilateral trading may occur outside these hours. | CLOSE_WINDOW_START_MINUTES = 30 minutes before 17:00 CET. OTC bilateral trades outside 17:00 CET are not subject to RT pass but are assessed in a post-session OTC review pass. |
| Instrument scope | Belgian OLO sovereign bonds (primary); Belgian Treasury Certificates (secondary); selected Eurozone sovereign bonds where MTSAM has designated market activity. | Correlated instrument pairs active for this deployment: OLO/Bund (SD02), OLO/OAT (SD02), OLO cross-maturity. instrument_correlation_confirmed=TRUE for these pairs. |
| OTC bilateral component | A proportion of interdealer OLO trading occurs as bilateral OTC outside the electronic MTS platform. This trading is typically reported but may not include order book data. | OTC bilateral component: Lite data mode applied. os_liquidity_unmeasurable=TRUE for OTC bilateral sessions. QUOTE_DATA_ABSENT surveillance_gap_flag for OTC bilateral portion. |
| Primary dealer obligations | Authorised primary dealers hold market making obligations to the ADA including quoting obligations in normal and stressed market conditions. | Market Making explanation category: requires positive confirmation that quoting was symmetric and consistent with ADA obligation. Obligation documentation must be on file. Prior FSMA/ESMA findings about liquidity provision conduct feed RRF assessment. |
| Regulatory authority | Financial Services and Markets Authority (FSMA), Belgium. ESMA surveillance coordination applies. ECB is a significant user of OLO prices for collateral purposes. | RRF Jurisdiction Adjustment: FSMA findings receive +2 (EU regulator). ECB collateral downstream exposure: os_downstream_exposure=TRUE systematic for OLO benchmark tenors. |
| Anonymous quote-driven structure | MTS Associated Markets operates as an anonymous interdealer electronic order book. Quote activity is visible to all participants in the form of aggregated depth, best bid/ask, and spread --- but the identity of the dealer posting, modifying, or withdrawing any specific quote is not disclosed during the trading session. Participant attribution is only possible post-session through order ID cross-referencing. | All interaction-based quote conclusions must document anonymity_attribution_basis in the explanation_trace. ModelConfidence is capped at MEDIUM for any quote-domain interaction signal where attribution relies on anonymous order book observation alone. |

### 1.2 Anonymous quoting — MTSAM-specific analytical framework

> The anonymous quoting structure of MTSAM is the single most important market structure characteristic for analytical calibration. It does not prevent detection of quote-based manipulation --- it determines how that detection is framed, attributed, and escalated. A surveillance framework that ignores anonymity will produce interaction-based conclusions that cannot withstand regulatory challenge.

In the MTSAM quote-driven anonymous interdealer environment, manipulative behaviour may occur entirely through displayed quote behaviour --- spread conditioning, liquidity withdrawal, order book depth manipulation, or systematic quote pressure --- without requiring executed transactions. The absence of a trade does not mean the absence of manipulation.

| MTSAM Anonymity Implication | Calibration Rule | Governance Requirement |
| --- | --- | --- |
| Quote behaviour is observable but not immediately attributable | All quote-level signals are initially assessed as market-condition signals, not participant-specific signals. Participant attribution is assigned in post-session analysis through order ID cross-referencing from the MTS surveillance export. | MTS surveillance export must include order-level data with participant identifiers to enable post-session attribution. Where order-level participant IDs are absent from the MTS export: MTSAM-L07 surveillance gap flag applied. ISGO-02 finding generated. |
| Sequential quote behaviour defaults to liquidity-driven reaction | Where participant B's quote activity follows participant A's quote activity in the anonymous order book: default classification is LIQUIDITY_DRIVEN_REACTION. The reclassification to identity-driven coordination requires post-session order attribution. | anonymity_attribution_basis field mandatory in explanation_trace for all quote-domain interaction signals: 'order_id_post_session' (confirmed), 'market_pattern_probabilistic' (unconfirmed), or 'trade_execution_confirmed'. |
| ModelConfidence capped for anonymous attribution | Where quote-domain interaction conclusions rely on market_pattern_probabilistic attribution only: ModelConfidence = MEDIUM maximum. STOR assessment where ModelConfidence = MEDIUM requires CCO acknowledgment of the attribution limitation. | CCO non-STOR justification for MEDIUM-confidence interaction-based quote signals must explicitly address whether post-session order attribution was assessed and why it did or did not confirm the interaction hypothesis. |
| CCT defaults to IMPLICIT for anonymous quote interaction | Explicit coordination (CCT=EXPLICIT) in quote-domain signalling requires order_id_post_session attribution or statistical_specificity_confirmed. Observable anonymous order book patterns alone cannot support CCT=EXPLICIT. | CCT=EXPLICIT for quote-domain signals in MTSAM must be documented with specific evidence basis. Methodology Lead sign-off required before CCT=EXPLICIT is recorded on a quote-domain signal without order-level attribution. |
| Supervisory challenge pre-emption | FSMA or a regulatory authority reviewing a quote-based interaction signal will ask: 'How did you identify coordination if the order book was anonymous?' The answer must be in the case record, not produced in response to the challenge. | Every quote-domain interaction signal reaching HIGH or VERY HIGH classification must include an anonymity_attribution_narrative field. This is a MTSAM mandatory field not required in non-anonymous deployments. |

### 1.3 New surveillance gap — MTSAM-L07

| Limitation Code | Description | Analytical Impact | ISGO Finding | Remediation Priority |
| --- | --- | --- | --- | --- |
| MTSAM-L07 | MTS surveillance export does not include order-level participant identifiers at quote event level (ORDER_NEW, ORDER_MODIFY, ORDER_CANCEL) --- only aggregate market data and trade-level participant IDs are available. Post-session participant attribution for quote events is therefore not possible from the surveillance export alone. | anonymity_attribution_basis defaults to 'market_pattern_probabilistic' for all quote-domain interaction signals. ModelConfidence capped at MEDIUM for all quote-domain interaction conclusions. CCT cannot reach EXPLICIT for quote-domain signals. | ISGO-02: order-level quote attribution data absent from surveillance export | CRITICAL: without order-level participant IDs at quote event level, the anonymous quoting analytical framework cannot be fully operationalised. Engage MTS S.p.A. to confirm whether order-level participant identifiers can be included in the surveillance export. |

<!-- sec:m-6c1a3dba -->
## 3. Document control

**Three-Output Integration** (also known as: three-output model)
<!-- concept:three-output-integration:start -->
Section 11 — Three-Output Integration (new): formalises the BehaviouralConcern / EvidenceConfidence / EscalationReadiness three-output model and its MTSAM calibration.
<!-- concept:three-output-integration:end -->

### 3.1 Document reference

|  |  |
| --- | --- |
| **Document ref.** | Veridict-Doc3-MTSAM-v21 |
| **Document** | Document 3 of 3 |
| **Version** | v21 --- Full document release |
| **Date** | June 2026 |
| **Applies to** | UCE v28 (Document 1 of 3) \| Document 2 v20 \| MTS Belgium OLO sovereign bond market |

**Classification** **CONFIDENTIAL**

### 3.2 What is new in v22

**v22 changes**

Section 11 --- Three-Output Integration (new): formalises the BehaviouralConcern / EvidenceConfidence / EscalationReadiness three-output model and its MTSAM calibration. Includes the updated five-level BehaviouralConcern axis (NONE / LOW / MEDIUM / HIGH / VERY HIGH), the simplified four-outcome Review Action mapping with Monitoring / Auto-close resolution at LOW concern (aligned with BIVM v28 §10b), RSA indicator weights, MTSAM concern/confidence/suppressor driver codes, and the corrected MWBR downward adjustment scoping rule.

Section 11.4 --- RSA Framework (new): formal specification of the six-indicator weighted scoring with MTSAM-specific assessment basis for each indicator.

Section 11.5 --- MWBR correction (v5 fix): MWBR_ANOMALOUS downward adjustment now correctly scoped to non-LOW classifications only.

Section 11.6 --- Calibration targets (updated): CCO Assessment target reduced from ≤ 5% to ≤ 1%. Five-level output distribution targets introduced. Sections 1--10 unchanged from v20.

*Section 11 --- Three-Output Integration --- MTSAM Configuration*

### 3.3 Section banners

|  |  |
| --- | --- |
| 0 | Regulatory Positioning Framework --- FSMA Engagement Architecture |
| 1 | MTSAM Market Structure --- Operating Characteristics |
