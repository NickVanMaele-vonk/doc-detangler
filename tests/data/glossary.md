<!--
SEEDED by `detangle generate` (plan step 3.5). Not a standing generated view.

Nick's ruling of 2026-08-04 makes this the fourth editable document: a
definition is canonical in the document that defines it, and the concept
record (`concepts/*.yaml`) holds a derived copy. So a definition below is
edited here, in place, and its record follows.

That ruling is enforced by the lift (built 2026-08-08): `detangle lift`
mirrors an edited definition into its record's derived copy, and
`detangle lift --check` runs in CI, so the file and the records cannot
silently disagree. Edit a definition between its markers; the heading and
the "Also known as" line belong to the record (`term`, `aliases`) and are
changed there, never here.

Re-running `detangle generate` REWRITES this file in full and discards every
human edit. It has done its job as the seeder.

Entry order is topological (`param-glossary-order`), taken from the concept
graph and the cycle register (`registers/cycles.yaml`), so the file reads
start to finish without meeting an undefined term.

Each entry sits between concept markers — `concept:<id>:start` and
`concept:<id>:end`, each in its own HTML comment — naming the record it came
from, so a comment on this file resolves to that record without any line
offset being involved (D10), and the lift knows exactly where a definition's
prose ends. Anything written outside the markers belongs to this file alone
and is mirrored nowhere.

(No literal marker is spelled out above: a closing comment bracket inside
this banner would end it early and leak the rest as visible text.)
-->

# Glossary

## Overview

<!-- gap:overview -->
> **Gap — the overview is not written.** Criterion 2 requires this document to
> open with a plain-language overview: what this body of documentation is
> about and how the three component documents relate, in
> `param-overview-max-words` words or fewer. `detangle generate` will not
> write it — every substantive word it emits traces to a concept record, and
> an overview of the domain would be invented text (C2, criterion 7). A human
> writes it **here**, replacing this block (Nick, 2026-08-04).

## Sources

Every source document the entries below draw on, each bound to the git blob
its records were verified against, with its role in the two input sets:
`component` documents are the detangle set, `reference` documents are
read-only context whose definitions may be lifted but whose bodies are never
in this set (Nick, 2026-08-05). Git carries release identity, so no version
string is typed here (ruling of 2026-07-31).

| Source document | Role | Verified git blob |
| --- | --- | --- |
| `samples/blueprint-MCL-shortened.md` | component | `71b9d9520ea205c72208fcc5d090b744f1e3e43b` |
| `samples/blueprint-SBSP-shortened.md` | component | `8a96710aac6c798eac3df1fbde0839725639ba95` |
| `samples/blueprint-UCE-shortened.md` | component | `4cae72dece7638c1ddec8206a3c6a24610196de0` |
| `samples/blueprint-analytical-layer.md` | reference | `7d88ad14949875467adea94e452433e2417e7f4a` |
| `samples/prototype-BC17.md` | reference | `36ad20437886a1883a547599a368c28c794b179a` |

<!-- concept:ads:start -->
## ADS

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:ads:end -->

<!-- concept:alert:start -->
## alert

**Also known as:** RT alert, Real-Time alert, Reporting-Day alert

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:alert:end -->

<!-- concept:22-step-analytical-pipeline:start -->
## 22-step analytical pipeline

**Also known as:** 22-step pipeline, twenty-two sequential steps, Stage 1, the analytical pipeline

Stage 1 of the analytical pipeline: twenty-two sequential steps, organised across three phases: structural qualification (Steps 1–11), causal and outcome validation (Steps 12–18), and explanatory adjudication (Steps 19–22). The pipeline receives IBEs, not individual alerts.
<!-- concept:22-step-analytical-pipeline:end -->

<!-- concept:anonymous-quote-driven-market-structure:start -->
## anonymous quote-driven market structure

**Also known as:** anonymous quoting, anonymous interdealer electronic order book

The market structure in which quote activity is visible to all participants but is not immediately attributable.
<!-- concept:anonymous-quote-driven-market-structure:end -->

<!-- concept:auction-window:start -->
## AUCTION_WINDOW

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:auction-window:end -->

<!-- concept:batch:start -->
## BATCH

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:batch:end -->

<!-- concept:behavioural-drift-score:start -->
## Behavioural Drift Score

**Also known as:** BDS

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:behavioural-drift-score:end -->

<!-- concept:behavioural-objective-assessment:start -->
## Behavioural Objective Assessment

**Also known as:** BOA

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:behavioural-objective-assessment:end -->

<!-- concept:behavioural-primitive:start -->
## behavioural primitive

**Also known as:** primitive

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:behavioural-primitive:end -->

<!-- concept:behaviouralconcern:start -->
## BehaviouralConcern

**Also known as:** five-level BehaviouralConcern axis

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:behaviouralconcern:end -->

<!-- concept:bt-03:start -->
## BT-03

Block-trade indicator BT-03: block trade reversal (profitable bt03_profitable and adverse bt03_adverse sub-types).
<!-- concept:bt-03:end -->

<!-- concept:bt-block-trade-code-family:start -->
## BT block-trade code family

**Also known as:** BT-01…BT-08

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:bt-block-trade-code-family:end -->

<!-- concept:bund:start -->
## Bund

**Also known as:** Bund futures

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:bund:end -->

<!-- concept:campaign:start -->
## campaign

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:campaign:end -->

<!-- concept:cco:start -->
## CCO

**Also known as:** Chief Compliance Officer

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:cco:end -->

<!-- concept:cf:start -->
## CF

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:cf:end -->

<!-- concept:close-window:start -->
## CLOSE_WINDOW

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:close-window:end -->

<!-- concept:contextual-directionality-logic:start -->
## contextual directionality logic

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:contextual-directionality-logic:end -->

<!-- concept:convergence-quality-score:start -->
## Convergence Quality Score

**Also known as:** CQS

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:convergence-quality-score:end -->

<!-- concept:convergence-quality-tier:start -->
## Convergence Quality Tier

**Also known as:** CQT, CQT1, CQT2, CQT3, CQT gate

CQT1 (CQS 3–5) = MEDIUM minimum; CQT2 (CQS 6–8) = HIGH minimum; CQT3 (CQS ≥9) = VERY HIGH eligible. CQT gate: CQT2 required for HIGH; CQT3 for VERY HIGH.
<!-- concept:convergence-quality-tier:end -->

<!-- concept:coordination-classification-tier:start -->
## Coordination Classification Tier

**Also known as:** CCT

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:coordination-classification-tier:end -->

<!-- concept:cross-window-persistence-score:start -->
## Cross-Window Persistence Score

**Also known as:** CWPS, CWPS_cross

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:cross-window-persistence-score:end -->

<!-- concept:crs:start -->
## CRS

**Also known as:** Context Reliability Score

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:crs:end -->

<!-- concept:cwps-intra:start -->
## CWPS_intra

**Also known as:** cwps_intra

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:cwps-intra:end -->

<!-- concept:d6-open-close-framing:start -->
## D.6 Open-Close Framing

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:d6-open-close-framing:end -->

<!-- concept:daf:start -->
## DAF

**Also known as:** DAF dual-mechanism

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:daf:end -->

<!-- concept:dominance-threshold:start -->
## DOMINANCE_THRESHOLD

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:dominance-threshold:end -->

<!-- concept:dqs:start -->
## DQS

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:dqs:end -->

<!-- concept:ecil-event:start -->
## ECIL event

**Also known as:** ecil_event_type

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:ecil-event:end -->

<!-- concept:escalating-dominance-trend:start -->
## Escalating Dominance Trend

**Also known as:** EDT, escalating_dominance_trend

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:escalating-dominance-trend:end -->

<!-- concept:event-materiality-scoring:start -->
## event materiality scoring

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:event-materiality-scoring:end -->

<!-- concept:event-object-schema:start -->
## Event Object Schema

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:event-object-schema:end -->

<!-- concept:evidence-hierarchy:start -->
## evidence hierarchy

**Also known as:** Evidence Hierarchy

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:evidence-hierarchy:end -->

<!-- concept:explanation-framework:start -->
## Explanation Framework

**Also known as:** explanation category constraints, legitimate explanation framework

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:explanation-framework:end -->

<!-- concept:explanation-trace:start -->
## explanation_trace

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:explanation-trace:end -->

<!-- concept:explanationfailure:start -->
## ExplanationFailure

**Also known as:** binary explanation flag

Positive confirmation required (timing, structure, outcome). ExplanationFailure=TRUE where no sufficient explanation.
<!-- concept:explanationfailure:end -->

<!-- concept:external-context-intelligence-layer:start -->
## External Context Intelligence Layer

**Also known as:** ECIL

The layer supplying structured contextual intelligence — event ingestion, Event Object Schema, contextual directionality logic, event materiality scoring, and scoring integration — for the analytical distinction between market-driven and manipulative behaviour, which cannot be resolved from alerts alone.
<!-- concept:external-context-intelligence-layer:end -->

<!-- concept:historical-quote-lifecycle-dataset:start -->
## Historical Quote Lifecycle Dataset

**Also known as:** HQLD

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:historical-quote-lifecycle-dataset:end -->

<!-- concept:instrument-cluster:start -->
## instrument cluster

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:instrument-cluster:end -->

<!-- concept:intent-score:start -->
## Intent Score

**Also known as:** IS

The scored output of the pipeline's intent assessment, IS (0–3).
<!-- concept:intent-score:end -->

<!-- concept:intentfactor:start -->
## IntentFactor

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:intentfactor:end -->

<!-- concept:internal-abuse-pathway:start -->
## internal abuse pathway

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:internal-abuse-pathway:end -->

<!-- concept:intraday-behavioural-event-builder:start -->
## Intraday Behavioural Event Builder

**Also known as:** IBEB

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:intraday-behavioural-event-builder:end -->

<!-- concept:ipi:start -->
## IPI

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:ipi:end -->

<!-- concept:iscore:start -->
## IScore

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:iscore:end -->

<!-- concept:isgo:start -->
## ISGO

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:isgo:end -->

<!-- concept:four-level-observability-framework:start -->
## Four-Level Observability Framework

The framework assigning each cross-instrument or cross-venue analytical finding to one of four observability levels — answering "what can we reliably observe, and what is the correct epistemological status of each observation?" — with the ISGO language required to reflect which level applies to each finding.
<!-- concept:four-level-observability-framework:end -->

<!-- concept:liquidity-removal:start -->
## LIQUIDITY_REMOVAL

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:liquidity-removal:end -->

<!-- concept:lookback-30d:start -->
## LOOKBACK_30D

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:lookback-30d:end -->

<!-- concept:medium-investigate:start -->
## MEDIUM-INVESTIGATE

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:medium-investigate:end -->

<!-- concept:methodology-lead:start -->
## Methodology Lead

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:methodology-lead:end -->

<!-- concept:mm-safeharbour:start -->
## MM_SAFEHARBOUR

The market-maker safe-harbour test with documented outcome codes (CONFIRMED / PARTIAL / FAILED); MM_SAFEHARBOUR_CONFIRMED removes the mandatory CCO escalation pathway as a structural scoring effect, not only an explanatory label.
<!-- concept:mm-safeharbour:end -->

<!-- concept:mts-mid:start -->
## MTS mid

**Also known as:** prevailing MTS mid

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:mts-mid:end -->

<!-- concept:mts-spa:start -->
## MTS S.p.A.

**Also known as:** MTS, MTS platform, MTS surveillance system, MTS surveillance export, MTS export

An Italian firm operating an electronic fixed income trading market for European government bonds, corporate bonds, covered bonds and repo, with average daily trading volume exceeding EUR 85 billion.
<!-- concept:mts-spa:end -->

<!-- concept:mts-associated-markets:start -->
## MTS Associated Markets

**Also known as:** MTSAM, MTS Associated Markets N.V., MTS Associate Markets N.V., MTS AM, the MTSAM market, MTS Belgium OLO sovereign bond market

The Belgian legal entity — MTS Associated Markets N.V., a joint venture between MTS and a consortium of banks, supervised by the FSMA and subject to the EU Market Abuse Regulation (MAR) — operating the electronic interdealer trading venue for Belgian OLO sovereign bonds.
<!-- concept:mts-associated-markets:end -->

<!-- concept:mtsam-analytical-layer:start -->
## MTSAM Analytical Layer

**Also known as:** Veridict MAR Intelligence Platform, Veridict Intelligence, MAR Intelligence

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:mtsam-analytical-layer:end -->

<!-- concept:mtsam-l-data-limitation-register:start -->
## MTSAM-L data limitation register

**Also known as:** MTSAM-L

The register of numbered data-limitation codes recording which data absences constrain which analytical capabilities at MTSAM.
<!-- concept:mtsam-l-data-limitation-register:end -->

<!-- concept:mtsam-l10:start -->
## MTSAM-L10

MTSAM-L data limitation register entry L10: cross-asset futures data absent.
<!-- concept:mtsam-l10:end -->

<!-- concept:mtsam-l11:start -->
## MTSAM-L11

MTSAM-L data limitation register entry L11: RFQ order flow absent.
<!-- concept:mtsam-l11:end -->

<!-- concept:multi-day-conditioning-score:start -->
## Multi-Day Conditioning Score

**Also known as:** MDCS

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:multi-day-conditioning-score:end -->

<!-- concept:mwbr-score-levels:start -->
## MWBR score levels

**Also known as:** MWBR_score, MWBR_NORMAL

MWBR_score: ANOMALOUS (>2σ from peer median); ELEVATED (1σ–2σ); NORMAL (<1σ); BELOW_NORMAL (<0 — participant is less active than peers).
<!-- concept:mwbr-score-levels:end -->

<!-- concept:mwbr-anomalous:start -->
## MWBR_ANOMALOUS

MWBR_score level ANOMALOUS: >2σ from peer median.
<!-- concept:mwbr-anomalous:end -->

<!-- concept:oat:start -->
## OAT

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:oat:end -->

<!-- concept:off-the-run:start -->
## off-the-run

**Also known as:** benchmark vs off-the-run

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:off-the-run:end -->

<!-- concept:otc-bilateral-trading:start -->
## OTC bilateral trading

**Also known as:** OTC bilateral component

Bilateral off-book trading in Belgian OLOs, in scope as T+1 trade reports (direction and size) with EOD-only timestamps; trades outside 17:00 CET are not subject to the RT pass but are assessed in a post-session OTC review pass.
<!-- concept:otc-bilateral-trading:end -->

<!-- concept:mtsam-l01:start -->
## MTSAM-L01

MTSAM-L data limitation register entry L01: trade timestamps may be EOD only for the OTC bilateral component; intraday OTC timestamps require MTSAM-L01 remediation.
<!-- concept:mtsam-l01:end -->

<!-- concept:participant-history:start -->
## Participant History

**Also known as:** PIR, participant_history

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:participant-history:end -->

<!-- concept:intraday-behavioural-event:start -->
## Intraday Behavioural Event

**Also known as:** IBE

A grouping of raw data streams — trades, quotes, alerts, ECIL context, and participant history — built by the Intraday Behavioural Event Builder for one participant-instrument pair within a configurable temporal window; each IBE is the primary input to Stage 1 of the analytical pipeline.
<!-- concept:intraday-behavioural-event:end -->

<!-- concept:participant-liquidity-contribution-score:start -->
## Participant Liquidity Contribution Score

**Also known as:** PLCS

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:participant-liquidity-contribution-score:end -->

<!-- concept:participant-order-flow-profile:start -->
## Participant Order Flow Profile

**Also known as:** POFP

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:participant-order-flow-profile:end -->

<!-- concept:bt-06:start -->
## BT-06

**Also known as:** BT-06 counterparty concentration, bt06_counterparty_hhi

Block-trade indicator BT-06, counterparty concentration: bt06_counterparty_hhi ≥ HHI threshold, with POFP baseline comparison for regime change.
<!-- concept:bt-06:end -->

<!-- concept:pre-suspension-window:start -->
## PRE_SUSPENSION_WINDOW

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:pre-suspension-window:end -->

<!-- concept:primary-dealer:start -->
## primary dealer

**Also known as:** ADA primary dealer

A dealer authorised by the Belgian Debt Agency (ADA) to quote OLOs; the documented ADA primary dealer list is the dominance population for calibration.
<!-- concept:primary-dealer:end -->

<!-- concept:dominance-population-size:start -->
## dominance_population_size

dominance_population_size = documented ADA primary dealer list.
<!-- concept:dominance-population-size:end -->

<!-- concept:dominance-threshold-pct:start -->
## DOMINANCE_THRESHOLD_PCT

The dominance threshold parameter computed as DOMINANCE_THRESHOLD_PCT = session_ADV / active_dealer_count × sector_sensitivity_multiplier, with dominance_population_size taken from the documented ADA primary dealer list.
<!-- concept:dominance-threshold-pct:end -->

<!-- concept:qbli:start -->
## QBLI

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:qbli:end -->

<!-- concept:qml-direction:start -->
## QML_direction

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:qml-direction:end -->

<!-- concept:qml-lead-rate:start -->
## QML_lead_rate

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:qml-lead-rate:end -->

<!-- concept:qml-market-impact:start -->
## QML_market_impact

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:qml-market-impact:end -->

<!-- concept:quote-behaviour-contextual-confidence-layer:start -->
## Quote Behaviour Contextual Confidence Layer

**Also known as:** QBCCL

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:quote-behaviour-contextual-confidence-layer:end -->

<!-- concept:quote-behaviour-risk-score:start -->
## Quote Behaviour Risk Score

**Also known as:** QBRS

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:quote-behaviour-risk-score:end -->

<!-- concept:quote-depth-share-position:start -->
## Quote Depth Share Position

**Also known as:** QDSP

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:quote-depth-share-position:end -->

<!-- concept:quote-driven-manipulation-vectors:start -->
## quote-driven manipulation vectors

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:quote-driven-manipulation-vectors:end -->

<!-- concept:quote-withdrawal:start -->
## QUOTE_WITHDRAWAL

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:quote-withdrawal:end -->

<!-- concept:rd03:start -->
## RD03

**Also known as:** RD-03

Alert code RD03 (EOD price influence): marking the close, reference price manipulation, NAV influence.
<!-- concept:rd03:end -->

<!-- concept:rd04:start -->
## RD04

Alert code RD04 (Closing price deviation): off-market closing execution and closing reference price distortion, with a 2bps threshold for benchmark instruments.
<!-- concept:rd04:end -->

<!-- concept:rd05:start -->
## RD05

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:rd05:end -->

<!-- concept:rd06:start -->
## RD06

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:rd06:end -->

<!-- concept:rd07:start -->
## RD07

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:rd07:end -->

<!-- concept:rd12:start -->
## RD12

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:rd12:end -->

<!-- concept:rdcs:start -->
## RDCS

**Also known as:** RT–RD cross-pass scoring

The RT–RD cross-pass score: intraday RT alerts combined with EOD RD materiality confirmation, producing a composite risk score that reflects both the behaviour and its market consequence.
<!-- concept:rdcs:end -->

<!-- concept:reasonable-suspicion-assessment:start -->
## Reasonable Suspicion Assessment

**Also known as:** RSA

The assessment establishing whether reasonable grounds for suspicion exist, specified as a six-indicator weighted scoring with an institution-specific assessment basis for each indicator.
<!-- concept:reasonable-suspicion-assessment:end -->

<!-- concept:regulatory-risk-factor:start -->
## Regulatory Risk Factor

**Also known as:** RRF, Regulatory Context (RRF)

A corroborative amplifier capturing regulatory context — never sole grounds for suspicion — enriched for MTSAM by participant LEI lookup against the OpenSanctions sanctions and regulatory enforcement database.
<!-- concept:regulatory-risk-factor:end -->

<!-- concept:removal-register:start -->
## Removal Register

**Also known as:** explicit exclusion register

The register of data categories formally removed from the operational model, recording for each exclusion the nature of the absent data and the detection approach that replaces it.
<!-- concept:removal-register:end -->

<!-- concept:rt-rd-alert-taxonomies:start -->
## RT/RD alert taxonomies

**Also known as:** RT alert taxonomy, RD alert taxonomy, RT/RD framework

The paired alert-code taxonomies of the existing surveillance framework: the intraday RT alert taxonomy and the end-of-day RD alert taxonomy.
<!-- concept:rt-rd-alert-taxonomies:end -->

<!-- concept:rt01:start -->
## RT01

Alert code RT01: artificial price movement through aggressive directional trading or order-book pressure.
<!-- concept:rt01:end -->

<!-- concept:rt04:start -->
## RT04

Alert code RT04 (Price deviation): off-market pricing, fixing manipulation, benchmark distortion, with deviation measured in basis points.
<!-- concept:rt04:end -->

<!-- concept:sb-05:start -->
## SB-05

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:sb-05:end -->

<!-- concept:sb-28:start -->
## SB-28

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:sb-28:end -->

<!-- concept:sb-29:start -->
## SB-29

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:sb-29:end -->

<!-- concept:sb-30:start -->
## SB-30

The archetype covering abuse of non-public order information, detected at MTSAM through a market footprint approach based solely on MTS trade timing (no access to dealer client books or pending RFQ flows).
<!-- concept:sb-30:end -->

<!-- concept:scl:start -->
## SCL

**Also known as:** supervisory confidence tier, SCL tier

The supervisory confidence tier attached to an escalation: SCL-COMPELLING — the convergent evidence across [n] dimensions constitutes a strong basis for reasonable grounds; SCL-PRECAUTIONARY — reasonable grounds exist notwithstanding specific gaps.
<!-- concept:scl:end -->

<!-- concept:scs:start -->
## SCS

**Also known as:** SCS_bpl

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:scs:end -->

<!-- concept:sd02:start -->
## SD02

**Also known as:** SD02 cross-instrument spread dislocation

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:sd02:end -->

<!-- concept:sf-issuance:start -->
## SF_issuance

**Also known as:** SF_issuance flag

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:sf-issuance:end -->

<!-- concept:signal:start -->
## signal

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:signal:end -->

<!-- concept:behavioural-episode-consolidation:start -->
## Behavioural Episode Consolidation

**Also known as:** BEP_E, episode, Episode consolidation

The consolidation stage operating downstream of the analytical pipeline in which classified signals for the same participant are grouped into episodes, the episode being the analyst review unit.
<!-- concept:behavioural-episode-consolidation:end -->

<!-- concept:classification:start -->
## classification

**Also known as:** classification band

The analytical pipeline's primary output: a band on the five-level scale NONE / LOW / MEDIUM / HIGH / VERY HIGH; scoring orders signals within a band and does not influence classification.
<!-- concept:classification:end -->

<!-- concept:contradicts-pattern:start -->
## CONTRADICTS_PATTERN

ECIL assessment outcome code recording that an external context event provides a full alternative explanation for the signal.
<!-- concept:contradicts-pattern:end -->

<!-- concept:convergence:start -->
## convergence

**Also known as:** convergence validation, coherent alignment

Coherent alignment across multiple independent analytical dimensions, required for HIGH and VERY HIGH classification; convergence must be independently confirmed across multiple analytical dimensions.
<!-- concept:convergence:end -->

<!-- concept:cross-market-convergence-score:start -->
## Cross-Market Convergence Score

**Also known as:** CMCS

A composite score combining six signals within a configurable window (reference: a 30-minute intraday window centred on the OLO activity IBE), computed as the weighted sum (0.25 × s1) + (0.20 × s2) + (0.15 × s3) + (0.15 × s4) + (0.15 × s5) + (0.10 × s6).
<!-- concept:cross-market-convergence-score:end -->

<!-- concept:cross-instrument-context-intelligence:start -->
## Cross-Instrument Context Intelligence

**Also known as:** CICI

The layer adding Bund futures public market data to the ECIL context enrichment, enabling a Cross-Market Convergence Score that contextually amplifies OLO manipulation hypotheses without asserting participant-level futures positions.
<!-- concept:cross-instrument-context-intelligence:end -->

<!-- concept:gate:start -->
## gate

**Also known as:** structural gate, gate architecture

A step condition: no dimension in a later step can compensate for a failed gate in an earlier step, and classification is determined by the highest structural gate cleared.
<!-- concept:gate:end -->

<!-- concept:causality-confidence-layer:start -->
## Causality Confidence Layer

**Also known as:** CCL

The gate scoring causal confidence, CCL (0–2): CCL≥1 is required for VERY HIGH and CCL=0 caps classification at HIGH.
<!-- concept:causality-confidence-layer:end -->

<!-- concept:dependency-score:start -->
## Dependency Score

**Also known as:** DS, Dependency Filter

The gate ensuring convergence is built on genuinely independent signals: DS (0–2) is assessed and DAF applied; DS=2 invalidates convergence, DS=1 reduces weight by 30%.
<!-- concept:dependency-score:end -->

<!-- concept:liquidity-driven-reaction:start -->
## liquidity-driven reaction

**Also known as:** LIQUIDITY_DRIVEN_REACTION

The default classification for sequential quote behaviour in the anonymous order book — participant B's quotes moving in response to observable market conditions following participant A's quote activity — unless post-session order attribution or statistical specificity testing confirms identity-driven coordination.

<!-- bridging:forward-ref -->
> **Forward reference (bridging text).** This definition uses **identity-driven coordination**, which is defined below rather than above: the two terms define each other by contrast, so no order can put both first (accepted cycle `liquidity-identity-contrast` in `registers/cycles.yaml`; criterion 1, clause 2).
<!-- concept:liquidity-driven-reaction:end -->

<!-- concept:identity-driven-coordination:start -->
## identity-driven coordination

Quote behaviour in which participant B deliberately tracks participant A's specific order activity — using order IDs, sizes, timing patterns, or pre-arranged signals — and responds to A's specific orders rather than to the anonymous market condition, producing an observable pattern identical to liquidity-driven reaction.
<!-- concept:identity-driven-coordination:end -->

<!-- concept:marking-the-close-triad:start -->
## Marking-the-Close Triad

The convergence requirement for marking-the-close detection in which the constituent RD alerts must fire simultaneously.
<!-- concept:marking-the-close-triad:end -->

<!-- concept:non-compensatory-architecture:start -->
## non-compensatory architecture

**Also known as:** non-compensatory

The architecture is non-compensatory: no dimension in a later step can compensate for a failed gate in an earlier step. Classification is determined by the highest structural gate cleared.
<!-- concept:non-compensatory-architecture:end -->

<!-- concept:pattern-gate:start -->
## Pattern gate

**Also known as:** Pattern detection

Pattern gate: mandatory at Step 2. No pattern → signal closed at Level 0.
<!-- concept:pattern-gate:end -->

<!-- concept:behavioural-persistence-layer:start -->
## Behavioural Persistence Layer

**Also known as:** BPL

The layer performing cross-session pattern detection — converting isolated alert episodes into structural campaign evidence — with five persistence components: BDS, SCS_bpl, MDCS, CWPS, EDT.
<!-- concept:behavioural-persistence-layer:end -->

<!-- concept:priorityscore:start -->
## PriorityScore

The pipeline's secondary, ranking-only output, computed as PriorityScore = IScore × CF × IntentFactor × DependencyFactor; non-compensatory and bounded by gate strength, it orders signals but does not influence classification.
<!-- concept:priorityscore:end -->

<!-- concept:outcome-score:start -->
## Outcome Score

**Also known as:** OS, Outcome Severity

The outcome-materiality gate score, OS (0–2/U) = max(Price, Liquidity, Information Impact); OS=0 zeroes PriorityScore and imposes a MEDIUM classification ceiling.
<!-- concept:outcome-score:end -->

<!-- concept:counterfactual-strength:start -->
## Counterfactual Strength

**Also known as:** CFS, but-for argument

CFS (0–2): but-for argument. CFS≥1 required where OS≥1.
<!-- concept:counterfactual-strength:end -->

<!-- concept:downstream-exposure:start -->
## downstream exposure

**Also known as:** os_downstream_exposure

The propagation of a manipulated price into downstream consequences — repo market margins, ECB collateral haircuts, covered bond pool valuations, NAV — assessed mandatorily for RD03, RD04, RD07, RD12 signals; confirmed downstream exposure makes OS=2 automatic.
<!-- concept:downstream-exposure:end -->

<!-- concept:escalationreadiness:start -->
## EscalationReadiness

**Also known as:** escalation readiness

The final gate for VERY HIGH: CQT3 AND IS≥2 AND OS≥1 AND ExplanationFailure=TRUE AND CCL≥1 AND CFS≥1 — all six simultaneously.
<!-- concept:escalationreadiness:end -->

<!-- concept:quote-domain-signal:start -->
## quote-domain signal

**Also known as:** quote-domain signals, quote-domain interaction signal

A signal where ADS/QBRS is the primary scoring dimension.
<!-- concept:quote-domain-signal:end -->

<!-- concept:anonymity-attribution-basis:start -->
## anonymity_attribution_basis

The mandatory explanation_trace field recording the attribution basis for quote-domain interaction signals, with three enumerated values: 'order_id_post_session' (confirmed), 'market_pattern_probabilistic' (unconfirmed), 'trade_execution_confirmed'.
<!-- concept:anonymity-attribution-basis:end -->

<!-- concept:market-wide-behavioural-reference:start -->
## Market-Wide Behavioural Reference

**Also known as:** MWBR

The reference that normalises quote-domain signals against peer behaviour before classification: MWBR_NORMAL reduces the quote-domain CQS uplift by 30% (not eliminated), MWBR_ANOMALOUS applies it at full rate.
<!-- concept:market-wide-behavioural-reference:end -->

<!-- concept:rd02:start -->
## RD02

Alert code RD02 (Participant market share): closing-window dominance, market control, concentration at reference price formation — calibrated relative to the dealer population (12–18 ADA primary dealers); the primary EOD dominance signal.
<!-- concept:rd02:end -->

<!-- concept:risk-archetype:start -->
## risk archetype

**Also known as:** SB risk archetype, Risk Archetype Taxonomy

A named market-abuse behaviour pattern in the sector risk universe, identified by an SB-## code and catalogued with its abuse type, detection signal mapping, and tier.
<!-- concept:risk-archetype:end -->

<!-- concept:sb-01:start -->
## SB-01

**Also known as:** Momentum Ignition

Price-family risk archetype Momentum Ignition; detection basis RT01, AGGRESSIVE_BUY/SELL primitives, SCS_bpl directional, MDCS, BT-03 reversal, BOA=MOMENTUM_IGNITION.
<!-- concept:sb-01:end -->

<!-- concept:sb-04:start -->
## SB-04

**Also known as:** Marking-the-Close

Price-family risk archetype Marking the Close; detection basis RD03 (quote), RD04 (execution), CWPS_intra CLOSE_WINDOW, D.6 Open-Close Framing, BOA=REFERENCE_PRICE_INFLUENCE.
<!-- concept:sb-04:end -->

<!-- concept:sb-08:start -->
## SB-08

**Also known as:** Liquidity Withdrawal, QUOTE_WITHDRAWAL primitive

Liquidity-family risk archetype Liquidity Withdrawal; detection basis QUOTE_WITHDRAWAL primitive, anticipatory withdrawal, BPL_liquidity_drift_confirmed, LIQUIDITY_CONDITIONING campaign.
<!-- concept:sb-08:end -->

<!-- concept:pre-stress-liquidity-withdrawal:start -->
## pre-stress liquidity withdrawal

**Also known as:** D.3 Pre-Stress Withdrawal

Systematic liquidity withdrawal before stress events occurring through quoting behaviour without execution — undetectable from trade data alone because the manipulation may leave no trade footprint.
<!-- concept:pre-stress-liquidity-withdrawal:end -->

<!-- concept:rt22:start -->
## RT22

Alert code RT22: Pre-stress liquidity withdrawal.
<!-- concept:rt22:end -->

<!-- concept:rt08:start -->
## RT08

Alert code RT08 (Liquidity stress proximity): liquidity triggering, pre-suspension abuse, and stress exploitation — the primary detection pathway for pre-stress manipulation given RT22 is not yet implemented.
<!-- concept:rt08:end -->

<!-- concept:sb-26:start -->
## SB-26

**Also known as:** SB-26 cash bond / futures hypothesis

The cash bond / futures cross-market hypothesis archetype: an investigative hypothesis supported by CICI/CMCS contextual amplification rather than participant-level futures position data.
<!-- concept:sb-26:end -->

<!-- concept:futures-activity-elevated:start -->
## FUTURES_ACTIVITY_ELEVATED

The named ECIL event type (ecil_event_type = FUTURES_ACTIVITY_ELEVATED) produced by CICI Level 1, contributing to ECIL CRS scoring for SB-26 hypothesis support.
<!-- concept:futures-activity-elevated:end -->

<!-- concept:sovereign-bond-dealer-market:start -->
## sovereign bond dealer market

**Also known as:** bond dealer markets, stressed sovereign bond sessions

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:sovereign-bond-dealer-market:end -->

<!-- concept:spread-rationality-indicator:start -->
## Spread Rationality Indicator

**Also known as:** SRI

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:spread-rationality-indicator:end -->

<!-- concept:spread-widening:start -->
## SPREAD_WIDENING

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:spread-widening:end -->

<!-- concept:structural-relationship-score:start -->
## Structural Relationship Score

**Also known as:** SRS

The structural-relationship score assigned at the enrichment step, SRS (0–3); SRS=3 assigns DS=2 and redirects the signal to the internal abuse pathway.
<!-- concept:structural-relationship-score:end -->

<!-- concept:supervisory-challenge-pack:start -->
## Supervisory Challenge Pack

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:supervisory-challenge-pack:end -->

<!-- concept:supports-explanation:start -->
## SUPPORTS_EXPLANATION

**Also known as:** ECIL SUPPORTS_EXPLANATION

ECIL assessment outcome code set where participant behaviour coincides with a high-CRS macro release and MWBR confirms population-wide reaction.
<!-- concept:supports-explanation:end -->

<!-- concept:unified-enriched-event-object:start -->
## Unified Enriched Event Object

**Also known as:** UEEO

> **Not defined in the corpus.** The source documents use this term but never
> define it. No definition is written here — inventing one is prohibited (C2)
> and is the highest-risk output the tool can produce (criterion 7). The entry
> holds the term's place in the reading order; supplying the definition is a
> human task (criterion 3, Case 1).
<!-- concept:unified-enriched-event-object:end -->

<!-- concept:modelconfidence:start -->
## ModelConfidence

The confidence output assessed purely on data quality dimensions (DQS, UEEO completeness), additionally adjusted for attribution confidence and capped at MEDIUM for any quote-domain interaction signal where attribution relies on anonymous order book observation alone.
<!-- concept:modelconfidence:end -->

<!-- concept:universal-core-engine:start -->
## Universal Core Engine

**Also known as:** UCE, the engine, Core Engine, Veridict Core Engine

The sector-agnostic analytical architecture that underpins all Veridict MAR Intelligence deployments, independent of market type, instrument class, or institutional context.
<!-- concept:universal-core-engine:end -->

<!-- concept:mtsam-calibration-layer:start -->
## MTSAM Calibration Layer

**Also known as:** MCL, Institution Calibration Layer, MTSAM Institution Calibration Layer, Calibration Layer, Document 3

The layer (Document 3 of 3) that provides institutional configuration for the Universal Core Engine; the MTSAM Calibration Layer is MTSAM's institution-specific instance.
<!-- concept:mtsam-calibration-layer:end -->

<!-- concept:quote-behaviour-baseline-engine:start -->
## Quote Behaviour Baseline Engine

**Also known as:** QBBE

The engine maintaining participant quote baselines, comparing current quote behaviour against each participant's own historical profile — not against a population threshold.
<!-- concept:quote-behaviour-baseline-engine:end -->

<!-- concept:sovereign-bond-sector-pack:start -->
## Sovereign Bond Sector Pack

**Also known as:** SBSP, Sovereign Government Bond Sector Intelligence Pack, Sector Intelligence Pack, Sector Pack, the Pack, Document 2

The pattern taxonomy, alert architecture, scoring calibration, and analytical doctrine that extend the Universal Core Engine (Document 1) for sovereign bond market surveillance.
<!-- concept:sovereign-bond-sector-pack:end -->

<!-- concept:qml:start -->
## QML

**Also known as:** Quote Market Leadership

The quote market leadership measure, carried as the fields QML_lead_rate, QML_direction, and QML_market_impact (Document 2 §D.5.5).
<!-- concept:qml:end -->

<!-- concept:quote-intelligence-architecture:start -->
## quote intelligence architecture

The architecture (Document 2 Section H: QBRS, QBLI, QBCCL) providing composite quote risk scoring and contextual enrichment for dealer markets, addressing anonymous order-book manipulation — spread conditioning, depth manipulation, and systematic quote pressure — which may leave no trade footprint.
<!-- concept:quote-intelligence-architecture:end -->

<!-- concept:sb-13:start -->
## SB-13

**Also known as:** Quote Leadership

Quote-family risk archetype Quote Leadership; detection basis §D.5.5 QML (Quote Market Leadership): QML_lead_rate, QML_direction, QML_market_impact.
<!-- concept:sb-13:end -->

<!-- concept:mtsam-l08:start -->
## MTSAM-L08

MTSAM-L data limitation register entry L08: D1 (Quote Leadership) and D2 (Liquidity Leadership) require HQLD, which is not currently available; HQLD remediation is the highest-priority MTSAM-L item.
<!-- concept:mtsam-l08:end -->
