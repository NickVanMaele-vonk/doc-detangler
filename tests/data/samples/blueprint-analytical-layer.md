---
type: blueprint
---


# MTSAM — Market Surveillance & Transaction Monitoring Platform

## Blueprint Document
**Version:** 0.1 — Draft for Review  
**Date:** July 2026  
**Prepared by:** TriFinance Belgium N.V. 
**Client:** MTS Associated Markets N.V. 
**Classification:** Confidential

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Business Context](#2-business-context)
3. [Stakeholders & Roles](#3-stakeholders--roles)
4. [Scope](#4-scope)
5. [Functional Requirements](#5-functional-requirements)
6. [Non-Functional Requirements](#6-non-functional-requirements)
7. [Architecture Overview](#7-architecture-overview)
8. [Data Model (Conceptual)](#8-data-model-conceptual)
9. [Integrations](#9-integrations)
10. [Assumptions & Dependencies](#10-assumptions--dependencies)
11. [Constraints](#11-constraints)
12. [Open Issues & Decisions Pending](#12-open-issues--decisions-pending)
13. [Acceptance Criteria](#13-acceptance-criteria)
14. [Sign-off](#14-sign-off)

---

## 0. Definitions
MTS S.p.A. (hereafter, "MTS") is an Italian firm operating an electronic fixed income trading market for European government bonds, corporate bonds, covered bonds and repo, with average daily trading volume exceeding EUR 85 billion. 

MTS Associate Markets N.V. (hereafter, "MTSAM"), is a joint venture between MTS and a consortium of banks. As a Belgian investment firm, it is supervised by the FSMA and subject to the EU Market Abuse Regulation (MAR). 

TriFinance Belgium N.V. (hereafter "TriFinance"), is a Belgian firm active in consulting and staffing. 


## 1. Executive Summary

This Blueprint document is the primary deliverable of Phase 0 of the engagement between TriFinance and MTSAM, as defined in the assignment agreement signed in June 2026.

The Blueprint defines the target architecture, functional scope, delivery phasing, and governance framework for the MTSAM Market Surveillance and Transaction Monitoring Platform (hereafter, "the Solution"). 

MTSAM's existing alert-based surveillance capability is based on the Eagle system provided by vendor ATS and operated by MTS. The Solution will extend MTSAM's surveillance capability with a behavioural intelligence platform capable of detecting, scoring, and documenting potential market abuse patterns across all trading activity, in a manner that is auditable, replayable, and defensible to FSMA. 

The Solution will consists of three logically independent layers: 
- Universal Core Engine (UCE): the core capability of turning input data into analyst-ready output
- Sovereign Bond Sector Pack: extends the UCE with business rules related to bond markets  
- MTSAM Calibration Layer: technical configuration specific to MTSAM

This document represents agreement between MTSAM and TriFinance on what will be built. Changes to scope, architecture, or phasing after sign-off must follow the change management process defined in the TriFinance General Terms and Conditions.

**Target delivery date of solution:** End of December 2026 (best effort)
**FSMA deadline for delivery of the full remediation process (=solution+manual review of high/very high cases):** End of Q1 2027

---

## 2. Business Context

### 2.1 Regulatory Driver

 Following an internal audit, MTSAM identified that its existing surveillance arrangements did not meet the standard of documented, reproducible, and behaviourally grounded analysis required under MAR. Specifically:

- Alert analysis conclusions were not systematically documented (a "no case" finding could not be reconstructed after the fact).
- Monitoring was limited to single-line thresholds (e.g., trade amount) rather than holistic participant behaviour.
- The existing Eagle system monitored trading data only; it did not cover the full data universe required.

MTSAM is under a remediation obligation and has engaged TriFinance to deliver a solution that satisfies FSMA requirements and enables BAU surveillance enhancement.

### 2.2 Strategic Objectives

The Solution is intended to support the following outcomes, as agreed in the assignment contract:

- Enable reassessment of behaviour that might be indicative for market abuse, both forward and backward looking (up to 1 January 2025).
- Support prioritisation of potentially suspicious behaviour through structured, risk-based analytical methodologies.
- Reduce the volume of manual review activities through automation and analytical intelligence, while maintaining regulatory defensibility.
- Improve the quality, consistency, and reproducibility of case analysis, decision-making, and documentation.
- Provide an auditable and replayable record of analytical outputs, risk assessments, and review decisions.
- Support the production of supervisory-defensible evidence packages and management information.
- Support MTSAM in executing its MAR surveillance remediation programme and enhancing its business-as-usual surveillance arrangements.

### 2.3 Current State

| Dimension | Current State |
|---|---|
| Surveillance system | Eagle system: alert-based, no behavioural insights |
| Data coverage | Trading data only (RTS24) |
| Documentation | Manual, inconsistent, not reproducible |
| Case output | Alerts (no severity scoring model) |
| Analyst tooling | Manual review; no structured workstation |
| Replayability | Not supported |

---

## 3. Main Stakeholders & Project Roles

### 3.1 Client — MTSAM

| Name | Role | Responsibility |
|---|---|---|
| Frank Staelens | CRO/CCO, MTSAM | Primary client contact; requirements owner; sole responsible for QA/UAT sign-off |
| Jurgen De Corte | CEO, MTSAM | Steerco member |
| Jacob Knight | Business Manager MTS| point of contact for raw data delivery from MTS|

### 3.2 TriFinance

| Name | Role | Responsibility |
|---|---|---|
| Serge Vigoureux | Head of Pragmatic Advisory | Steerco member |
| Annemie Pelgrims | Practice Lead Risk | Steerco member |
| Maarten Lauwaert | Practice Lead Data & Reporting | Steerco member |
| Nick Van Maele | IT Project Manager / Consultant | Overall delivery management; client governance; blueprint and documentation |
| Stephanie Kelberg | Senior Manager Risk | Lead of Risk track; overseeing risk-related activities |
| Hans Hermans | Risk Consultant | Risk framework validation; regulatory input; business requirement modelling |
| Ivo Merchiers | Senior Data Engineer | Lead of Tech track; architecture; overseeing IT implementation |
| Matthias Arrabal Serran | Data engineer | Implementation; technical build pack |


### 3.3 Decision Rights

- Requirements decisions: Frank Staelens (MTSAM)
- Data residency decisions and related AI architecture: Frank Staelens (final authority)
- Regulatory compliance decisions: Frank Staelens, supported by Hans Hermans
- Technical architecture decisions: Ivo Merchiers, ratified by Frank Staelens
- Project & change management: Nick Van Maele, requires written agreement from both parties

---

## 4. Scope

### 4.1 In Scope

**Phase 0 - Blueprint**
Scope: writing and signing off a mutually agreed blueprint document. 
Status: this Blueprint document, once signed, finalizes Phase 0. 

Overview of the Solution components and data flow: 

![Solution component diagram](MTSAM_Analytical-Layer_blueprint.png)


**Phase 1 — Foundation**

- Technical infrastructure setup (Azure tenant, security model, RBAC)
- Data ingestion pipeline for internal data
    - trading data RTS24, 
    - RT/RD alerts, including high volumes and liquidity suspension alerts
    - participant reference data
    - product reference data (financial instruments)
- Data ingestion pipeline for five must-have external data sources (via API) 
- Main Surveillance Pipeline: from ingested raw data to final behavioural concern 
    - Case generation with severity classification: NONE / LOW / MEDIUM / HIGH / VERY HIGH
- Simplified Analyst Workstation (React-based): minimum viable version 
- Replayability: full logging of inputs, pipeline outputs, and analyst decisions
- End-to-end analyst workflow: from raw data ingestion to case decision

Exclusion: Quality Assurance Pipeline - will be built in Phase 2. 

**Phase 2 — Enrichment**

- Quality Assurance Pipeline
    - independent assessment of the final behavioural concern 
    - outcome is used to verify the Main Surveillance Pipeline
- Integration of additional external data sources (via API) 
    - For example: Belgian, Danish and Finnish Debt Agency (DMO), Eurex, OpenSanctions, ratings feeds, macro events, news
- STOR file generation for FSMA submission
    - STOR = Suspicious Transaction and Order Report
- Extension of Analyst Workstation core functionality (excluding workflow management)
- Additional behavioural test modules with limited implementation uncertainty
- Main Surveillance Pipeline additions
    - Confidence score
    - Escalation readiness
- AI reasoning engine (case narrative generation and supporting evidence assembly)


**Phase 3 — Extensions**
The Extensions may optionally be built if the project has budget and time left. 

- Power BI reporting and management information dashboards
- Analyst Workstation workflow management
- Advanced or exploratory features requiring further investigation (e.g., AI-driven pattern discovery, adaptive test calibration)

### 4.2 Explicitly Out of Scope

- Replacement or decommissioning of Eagle system (MTS) — the legacy system remains in parallel
- Direct integration with FSMA systems (STOR file export is in scope; transmission is out of scope)
- Real-time (sub-second) or intra-day surveillance — the system operates on daily batch increments, , i.e. T+1 feeds as mentioned in section 4.1 and 5.1
- Surveillance of asset classes other than those currently traded by MTSAM
- Bloomberg data feed (MTS uses Bloomberg; Belgium does not — the below list of external sources will be used as an alternative)
- Any features not listed above unless agreed in writing via change request process

---

## 5. Functional Requirements

### 5.1 Data Ingestion

| ID | Requirement |
|---|---|
| FR-D01 | The system shall ingest trading data in RTS24 format (EU standard) |
| FR-D02 | The system shall ingest RT/RD alert outputs from the Eagle system (MTS) |
| FR-D03 | The system shall ingest participant data, including ultimate beneficial owner (UBO) information |
| FR-D04 | The system shall ingest reference data (instruments, ISINs, products) |
| FR-D05 | The system shall support ingestion of external data sources |
| FR-D06 | The system shall support a data volume of up to 20 million records per day |
| FR-D07 | The system shall support re-ingestion of corrected data records |

### 5.2 Main Surveillance Pipeline

| ID | Requirement |
|---|---|
| FR-P01 | The system shall implement the Intraday Behavioural Event Builder (IBEB) to aggregate raw data streams per participant, per instrument cluster, per time window into a structured Intraday Behavioural Event (IBE) |
| FR-P02 | The system shall implement the Universal Core Engine (UCE) 22-step analytical pipeline |
| FR-P03 | The system shall implement the Sovereign Bond Sector Pack (behaviour categories and detection signal mappings) |
| FR-P04 | The system shall implement the MTSAM Calibration Layer (Risk Archetypes, Behavioural Categories, CQS/CQT/BOA scoring) |
| FR-P05 | The pipeline shall be deterministic: identical inputs shall always produce identical outputs |
| FR-P06 | The system shall document which tests were executed and what conclusions were reached for every case |
| FR-P07 | The system shall generate a concern and confidence score for each IBE (Phase 2 or Phase 3)|
| FR-P08 | The system shall classify each case as NONE, LOW, MEDIUM, HIGH, or VERY HIGH |
| FR-P09 | The system shall support cross-venue pattern detection, subject to data availability constraints MTSAM-L01 and MTSAM-L03 |

### 5.3 AI Reasoning Engine

| ID | Requirement |
|---|---|
| FR-A01 | The AI reasoning engine shall generate a human-readable narrative summary for each case |
| FR-A02 | The AI shall gather and assemble supporting evidence for analyst review |
| FR-A03 | The AI shall not function as the decision-maker; all scoring and classification decisions shall be made by the deterministic pipeline |
| FR-A04 | The system shall implement a two-stage AI QA pattern: AI 1 generates the risk file; AI 2 reviews and challenges it |
| FR-A05 | Slight non-determinism in AI narrative output is acceptable, provided the underlying scoring is deterministic and the human analyst is in the loop |

### 5.4 Analyst Workstation

| ID | Requirement |
|---|---|
| FR-W01 | The analyst workstation shall display a prioritised list of cases with elevated risk |
| FR-W02 | Each case view shall show: high-level trading information, test outcomes, AI-generated narrative, and proposed severity classification |
| FR-W03 | The analyst shall be able to confirm or override the proposed severity classification |
| FR-W04 | Case status shall be tracked: New / Ongoing / Closed |
| FR-W05 | The system shall record who performed each action and when (user tracking) |
| FR-W06 | The system shall maintain a full audit trail of all steps taken to reach a case decision |
| FR-W07 | The workstation shall allow usage by different types of profiles |

### 5.5 Replayability

| ID | Requirement |
|---|---|
| FR-R01 | The system shall store all input data, pipeline outputs, AI outputs, and analyst decisions in a manner that allows any case to be fully replayed at a later date |
| FR-R02 | Replayability shall support both new and past assessments |
| FR-R03 | The replayability implementation shall comply with the MAR definition of replayability (to be confirmed by Hans Hermans and to be validated by Frank Staelens) |

### 5.6 STOR Generation (Phase 2)

| ID | Requirement |
|---|---|
| FR-S01 | The system shall generate a STOR (Suspicious Transaction and Order Report) file in the format required by FSMA |
| FR-S02 | STOR generation shall be triggered by the CCO's decision to escalate a case |

---

## 6. Non-Functional Requirements

### 6.1 Security

| ID | Requirement |
|---|---|
| NFR-SEC01 | Role-Based Access Control (RBAC) shall govern all access to the system and its data |
| NFR-SEC02 | No personally identifiable information (PII) shall be transmitted to external AI inference infrastructure (see Section 9.2) |
| NFR-SEC03 | The Azure tenant shall be owned by MTSAM; TriFinance shall act as tenant administrator during the engagement |
| NFR-SEC04 | The solution shall be designed to be transferable to MTSAM's sole ownership and operation at end of engagement |
| NFR-SEC05 | Microsoft guarantees regarding data not leaving the Azure tenant must be obtained in writing before data onboarding begins |

### 6.2 Data Residency

| ID | Requirement |
|---|---|
| NFR-DR01 | All data must remain within the European Union at all times |
| NFR-DR02 | AI inference infrastructure must operate within EU boundaries; AWS Bedrock EU inference profiles (Frankfurt, Ireland, or Paris) are the preferred mechanism |
| NFR-DR03 | If AWS Bedrock is used, data encryption keys must remain in Europe |
| NFR-DR04 | Azure AI Foundry is not approved for use until Microsoft can provide equivalent EU data residency guarantees |

### 6.3 Regulatory Compliance

| ID | Requirement |
|---|---|
| NFR-REG01 | The system shall comply with the EU Market Abuse Regulation (MAR) |
| NFR-REG02 | All analytical outputs shall be supervisory-defensible and suitable for FSMA submission |
| NFR-REG03 | The system shall comply with GDPR with respect to personal data handling and cross-border transfer |
| NFR-REG04 | AI infrastructure providers must demonstrate compliance with applicable EU data protection requirements |

### 6.4 Auditability

| ID | Requirement |
|---|---|
| NFR-AUD01 | Every analytical output shall be traceable to the input data and pipeline steps that produced it |
| NFR-AUD02 | Immutability of concluded case records shall be enforced via RBAC (records cannot be altered after conclusion by an analyst |
| NFR-AUD03 | The system shall maintain logs sufficient for internal audit review |

### 6.5 Performance & Availability

| ID | Requirement |
|---|---|
| NFR-PERF01 | The system shall process daily data volumes of approximately 15-20 million records within the intraday processing window |
| NFR-PERF02 | Specific throughput SLAs and availability targets to be defined during Phase 0 technical design |

---

## 7. Architecture Overview

### 7.1 Six-Layer Software Architecture

The Solution is structured in six logical layers:

| Layer | Description |
|---|---|
| **1. Data Ingestion** | Connectivity to all internal MTSAM data sources and external data sources |
| **2. Data Persistence** | Storage of all ingested data, pipeline outputs, AI outputs, and audit records; EU-hosted |
| **3. Main Surveillance Pipeline** | Deterministic behavioural scoring engine; implements UCE, Sector Pack, and MTSAM Calibration Layer; currently comprises approximately 186 tests across 55 modules |
| **4. QA Pipeline** | Scores data independently of Main Surveillance Pipeline and verifies the outcome |
| **5. AI reasoning engine** | Non-deterministic layer responsible for narrative generation, evidence assembly, and QA review; human-in-the-loop by design | 
| **6. Analyst Workstation** | React-based front end for case review, decision recording, and audit trail |

### 7.2 Main Surveillance Pipeline Architecture

The Main Surveillance Pipeline itself is composed of three logically distinct layers:

| Layer | Description |
|---|---|
| **Universal Core Engine (UCE)** | The base detection and scoring framework; implements an analytical pipeline from IBE ingestion to case classification |
| **Sovereign Bond Sector Pack** | Sector-specific Behaviour Categories and Detection Signal mappings applied on top of the UCE |
| **MTSAM Calibration Layer** | Client-specific calibration: Risk Archetypes, Behavioural Categories, CQS/CQT/BOA thresholds, and data limitation constraints (MTSAM-L01, MTSAM-L03) |

### 7.3 Hosting & Infrastructure

- Primary cloud: **Microsoft Azure** (MTSAM tenant)
- AI inference: **AWS Bedrock** (EU inference profiles) with Anthropic Claude as primary model; OpenAI/GPT as fallback
- Data residency: **EU-only** (see NFR-DR01 through NFR-DR04)
- Document and Code Repository: Azure DevOps (`https://dev.azure.com/TF-DR-PreSales/MTSAM/`)

### 7.4 Key Architectural Principles

- **Determinism in scoring:** The surveillance pipeline is fully deterministic; identical inputs produce identical outputs. AI is used only for narrative and evidence assembly, not for scoring.
- **Human in the loop:** No case is concluded without an analyst decision. AI outputs are advisory.
- **Replayability by design:** All inputs, intermediate outputs, and decisions are persisted in a form that allows any case to be reconstructed at any later date.
- **Separation of PII:** Personally Identifiable Information shall be isolated from data passed to AI inference infrastructure. 
- **Transferability:** The solution architecture shall be designed for transfer to MTSAM ownership and operation without TriFinance dependency.

---

## 8. Data Model (Conceptual)

### 8.1 Summary Internal Data Entities
The table below is not an exhaustive list. 

| Entity | Description | Source |
|---|---|---|
| Trading Event | Individual trade or order in RTS24 format | MTSAM trading systems |
| Quotes | Individual quote in RTS23 format | MTSAM trading systems | 
| Legacy Alerts | RT/RD alert output from ATS (Eagle) and High and medium risk blocktrade & Liquidity suspension alerts (developed by TriFinance in powerquery) | Eagle system |
High and medium risk blocktrade and 
| Participant | Trading counterparty including UBO | MTSAM participant database |
| Instrument / ISIN | Financial instrument reference data | Reference data feed |
| Intraday Behavioural Event (IBE) | Aggregated behavioural object produced by IBEB for one participant, one instrument cluster, one time window | Pipeline (derived) |
| Case | Scored and classified surveillance output; primary analyst-facing object | Pipeline (derived) |
| Case Decision | Analyst verdict and rationale, linked to Case | Analyst Workstation |
| Audit Record | For a Case with scoring LOW / MEDIUM / HIGH / VERY HIGH, keep an immutable log of all pipeline steps and analyst actions for that Case | System-generated |

### 8.2 External Data Entities (Phase 2)

| Entity | Source | Phase |
|---|---|---|
1.	OpenSanctions – participant intelligence. 
2.	Belgian Debt Agency Calendar – sovereign issuance and auction events. 
3.	ESMA FIRDS – instrument reference data. 
4.	ECB Data API – macroeconomic and monetary policy context. 
5.	GDELT – geopolitical and news-event intelligence. 
6. OpenCorporates	/Corporate ownership & participant relationships
7.	ESMA FITRS	/Liquidity status, LIS, SSTI, transparency regime
8.	Eurex Market Data	/Cash vs futures behaviour
9.	ECB SDMX Yield Curve Data	/Sovereign curve analytics
10.	Additional Sovereign Debt Agency Calendars (Finland, Denmark)	/Multi-market event context

### 8.3 Data Governance Notes

- News data does not require persistent storage (metadata only).
- All other data should be stored to the maximum extent possible to support replayability.
- PII must be isolated from data flows that pass to external AI inference.
- Country-dependent parameters must be modelled explicitly (approach TBD by Ivo Merchiers).

---

## 9. Integrations

### 9.1 Internal Integrations

| Integration | Direction | Interface | Owner |
|---|---|---|---|
| ATS Italy (Eagle) | Inbound | RT/RD alert export (format TBD) | MTSAM IT / Italy team |
| MTSAM trading systems | Inbound | RTS24 data feed | MTSAM IT |
| MTSAM participant database | Inbound | API or batch export (TBD) | MTSAM IT |
| Azure DevOps | Internal | Source control and CI/CD | TriFinance (Ivo) |

### 9.2 AI Infrastructure

| Integration | Provider | Protocol | Data Residency |
|---|---|---|---|
| Primary AI inference | AWS Bedrock (Anthropic Claude) | HTTPS / Bedrock API | EU inference profiles (Frankfurt / Ireland / Paris) |
| Fallback AI inference | AWS Bedrock (OpenAI / GPT) | HTTPS / Bedrock API | EU inference profiles |

Note: Only non-PII data shall be transmitted to AI inference endpoints. Frank Staelens holds final decision authority on AI infrastructure selection and data sharing policy.

### 9.3 External Data (Phase 2)

All must-have external data integrations are classified as Phase 1 scope; with others in Phase 2 scope. 

Are considered to be a part of the Phase 1 scope: 
1.	OpenSanctions – participant intelligence. 
2.	Belgian Debt Agency Calendar – sovereign issuance and auction events. 
3.	ESMA FIRDS – instrument reference data. 
4.	ECB Data API – macroeconomic and monetary policy context. 
5.	GDELT – geopolitical and news-event intelligence. 
Are considered to be a part of the Phase 2 scope: 
1.	OpenCorporates	/Corporate ownership & participant relationships
2.	ESMA FITRS	/Liquidity status, LIS, SSTI, transparency regime
3.	Eurex Market Data	/Cash vs futures behaviour
4.	ECB SDMX Yield Curve Data	/Sovereign curve analytics
5.	Additional Sovereign Debt Agency Calendars (Finland, Denmark, Italy)	/Multi-market event context

Specific APIs, data formats, licensing arrangements, and ownership (TriFinance vs MTSAM) are to be confirmed during Phase 1 delivery. 

### 9.4 Regulatory Output

| Output | Destination | Trigger | Phase |
|---|---|---|---|
| STOR file | FSMA (manual submission by analyst) | Analyst escalation decision | Phase 2 |

---

## 10. Assumptions & Dependencies

| ID | Assumption / Dependency | Owner | Impact if Wrong |
|---|---|---|---|
| A-01 | MTS will provide trading data in RTS24 format from Day 1 of data onboarding (target: end of July) | MTS AM + MTS | Ingestion pipeline redesign required |
| A-02 | ATS Italy (Eagle) will continue to operate in parallel and will export RT/RD alerts in an agreed format | MTS AM + MTS | Alert data integration blocked |
| A-03 | Frank Staelens will be available for requirements review twice weekly | Frank Staelens | Requirements instability; delivery delay |
| A-04 | The MAR definition of replayability will be confirmed by Hans Hermans before the end of Phase 0 | Hans Hermans | Validation by Frank Staelens | FR-R01 through FR-R03 may need revision |
| A-05 | AWS Bedrock EU inference profiles provide sufficient EU data residency guarantees for MTSAM's regulatory obligations | MTSAM | AI infrastructure must be redesigned |
| A-06 | Microsoft will provide written guarantees that no data leaves the Azure tenant before data onboarding begins | MTSAM | Data onboarding blocked |
| A-07 | Wouter Pinkhof from PC-Hulp - PINKH bv will be the IT responsible contact for the Azure tenant setup | MTSAM | Infrastructure setup blocked |
| A-08 | External data sources listed in Section 9.3 are accessible via API or structured feed at reasonable cost | Frank + Hans | Phase 2 scope may need revision |
| A-09 | The FSMA deadline of end-Q1 2027 applies to Phase 2 (end-to-end analyst workflow operational); Phase 3 is post-deadline | MTSAM + TriFinance | Phase 1 & 2 scope and timeline at risk |
| A-10 | PII isolation (party data only to AI inference) is legally sufficient; full anonymisation is not required | MTSAM | AI data handling approach must change |
| A-11 | Underlying logic & rules for all steps in the pipeline is the responsibility of MTSAM. TriFinance will assist with implementation and quality testing. | MTSAM | Logic may be incorrect |
| A-12 | No extra (data) analysis is needed to determine parameters or validate logic. | MTSAM | Additional workload and/or delay in project | 
| A-13 | For the HIGH and VERY HIGH cases, sufficient internal MTS analyst capacity will be available to manually review cases. | MTSAM | Risk for FSMA ratification by end Q1 2027 | 

---

## 11. Constraints

| ID | Constraint | Type |
|---|---|---|
| C-01 | All data must remain within the EU at all times | Regulatory / Legal |
| C-02 | Phase 1 and 2 must be operational before the end of Q1 2027 (FSMA remediation deadline) | Timeline |
| C-03 | The solution must be built on the MTSAM Azure tenant | Infrastructure |
| C-04 | The surveillance pipeline must be deterministic (no probabilistic scoring) | Technical |
| C-05 | AI must not be the final decision-maker; human analyst approval is mandatory | Regulatory |
| C-06 | The solution must be transferable to MTSAM independent operation at end of engagement | Commercial |
| C-07 | Scope changes after blueprint sign-off require written agreement from both parties | Governance |
| C-08 | Azure AI Foundry is not approved for use pending Microsoft EU data residency guarantee | Technical |
| C-09 | Bloomberg data is not available in Belgium and shall not be included in scope | Data |

---

## 12. Open Issues & Decisions Pending

| ID | Issue | Owner | Target Resolution |
|---|---|---|---|
| OI-01 | Which specific analyst actions must be captured in the Analyst Workstation audit trail? | Frank Staelens | End of Phase 0 |
| OI-02 | MAR definition of replayability — exact technical and legal requirements | Hans Hermans | To be validated by Frank Staelens  | End of Phase 0 |
| OI-04 | AI infrastructure final decision: AWS Bedrock confirmed or alternative? | Frank Staelens | Before Phase 1 start |
| OI-05 | Microsoft written guarantee: no data leaves MTSAM Azure tenant | Ivo + MTSAM IT | Before data onboarding |
| OI-06 | Data privacy / data impact assessment | Frank Staelens  | MTSAM | Phase 0 |
| OI-07 | Identification of MTSAM IT contact for Azure tenant setup | Frank Staelens | Before Phase 1 start |
| OI-08 | Country-dependent parameter modelling approach in the pipeline | Ivo Merchiers | Phase 1 design |
| OI-09 | Phase 1 / Phase 2 / Phase 3 detailed scope breakdown and sequencing | Nick + Ivo | End of Phase 0 |
| OI-10 | API → test → scenario dependency mapping | Nick + Hans + Ivo | Phase 1 planning |
| OI-11 | Re-ingestion of corrected data records: phase and approach | Nick + Ivo | Phase 1 design |
| OI-12 | Frank Staelens' documentation of required external data sources (full list) | Frank Staelens | Phase 0 |
| OI-13 | Board-level reporting cadence and format | Frank Staelens | Phase 2 planning |

---

## 13. Acceptance Criteria

The following criteria define when each phase is considered complete and accepted by MTSAM.

### Phase 0 (Blueprint)

- This Blueprint document is reviewed, amended if necessary, and signed off by Frank Staelens on behalf of MTSAM and Nick Van Maele on behalf of TriFinance.
- All Open Issues in Section 12 that are marked "End of Phase 0" are resolved and documented.
- The Phase 1 delivery plan and roadmap are agreed in writing.

### Phase 1 (Foundation)

- An analyst can complete an end-to-end workflow: internal and must-have external data are ingested, the main pipeline runs, a case is generated with scoring and AI narrative, and the analyst can review, decide, and record their decision with a full audit trail.
- The system is deployed and operational in the MTSAM Azure tenant.
- All replayability requirements (FR-R01 through FR-R03) are demonstrably met.
- Security requirements (NFR-SEC01 through NFR-SEC06) and data residency requirements (NFR-DR01 through NFR-DR04) are met and documented.

Frank Staelens (sole QA/UAT owner) confirms acceptance in writing.

### Phase 2 (Enrichment)

Must have: 
- QA Pipeline is operational. 

Nice to have - could move to Phase 3 if necessary: 
- STOR file generation is operational and output is validated against FSMA format requirements.
- Additional external data integrations are live and feeding the pipeline.

Frank Staelens confirms acceptance in writing.

### Phase 3 (Extensions)

- Power BI reports are operational and validated by MTSAM management.
- Any additional features agreed for Phase 3 are delivered and accepted per individual feature acceptance criteria defined at time of build.


--- 

## 14. Summary of project approach 

The project methodology will be hybrid. 
- Design done upfront using Waterfall
- Software development using Agile (to be decided: Scrum or Kanban)

In principle, we will seek stability of requirements. What has been defined in this blueprint document will be built and tested in Phase 1 before fundamental changes to the Solution are requested. In other words, during Phase 1: 
- Major re-architecting of the Solution mid-way through the development cycle will be avoided as much as possible: the Solution components and their mutual dependencies will be built as specified. If a fundamental change is unavoidable, a Change Request must be submitted. 
- Clarifications and additional details about the Main Surveillance Pipeline components will be accepted and added without a formal Change Request process provided that they do not fundamentally affect multiple other components or the overall architecture of the Solution. 

---

## 15. Summary of Change Request Process

Change Requests are formal instruments for modifying the agreed project scope. Scope changes carry cost and risk by default; the Change Request Process exists to ensure they are evaluated rigorously before any modification is made to the scope baseline.

**Who can raise a Change Request**
Any project stakeholder may identify a need for change, but Change Requests must be formally submitted by a designated project representative on either the client or delivery side. Ad-hoc verbal requests do not constitute a Change Request.

**Change Request content**
Every Change Request must contain at minimum: 
- a description of the proposed change, 
- the reason for the change, 
- the deliverable(s) or requirement(s) affected, 
- the requestor name and date, 
- an initial priority indication (critical / high / medium / low).

**Steps in the Change Request Process**
1. Submission. The requestor submits the Change Request using the standard template. The Project Manager registers it in the Change Request log and assigns a unique identifier to it. 
2. Impact assessment. The Project Manager, in consultation with the technical lead, assesses the impact on scope, budget, timeline, and risk. The assessment is documented and attached to the Change Request record.
3. Decision. The Steerco reviews the Change Request and its impact assessment. The Steerco issues one of four possible decisions and records it with the rationale: 
    1. Approved 
    2. Approved with modifications 
    3. Deferred 
    4. Rejected. 
4. Execution. Change Requests which were 'Approved' or 'Approved with modifications' are incorporated into the project scope baseline. The project plan is updated accordingly, and the change is communicated to all affected parties. The Change Request log is updated to reflect the new status.

**Traceability**
Every approved Change Request must be traceable to the affected requirements, deliverables, and any revised budget or timeline commitments.

---

## 16. Sign-off

By signing this document, the Parties confirm that they have read, understood, and agreed to the contents of this Blueprint as the basis for the development of the MTSAM Market Surveillance & Transaction Monitoring Platform.

Changes to this document after sign-off require a written change request agreed by both Parties.

| Party | Name | Title | Signature | Date |
|---|---|---|---|---|
| MTSAM | Frank Staelens | CRO/CCO | | |
| TriFinance | Serge Vigoureux | Head of Pragmatic Advisory | | |

---

*Document prepared by TriFinance Belgium NV. Confidential — not for distribution outside the Parties.*
