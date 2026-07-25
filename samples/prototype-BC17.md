# BC-17 — Event-Driven Information Behaviour — Comprehensive Specification

One end-to-end explanatory document for the whole of **Behaviour Category 17 (BC-17) — Event-Driven Information Behaviour**: from raw-data ingestion, through the scoring objects and detection signals, to the final behavioural-category classification and the risk archetypes it resolves to. It merges the raw-data lineage of "BC-17 (3)" with the full corrected formulas and category/archetype logic of "BC-17 (2)" into a single structure that follows the flowchart:

```
Layer 1: Raw Data Ingestion → Layer 2: Scoring Objects → Layer 3: Detection Signals → Layer 4: Behavioural Category (BC-17) → Layer 5: Risk Archetypes
```

Every value is linked back to the layer it is computed from, so the chain is traceable in both directions. **Translation tables** (value → computation → raw field) and **theoretical-framework tables** (the `T-###` term definitions) are retained. **Every abbreviation is spelled out** — in prose, in the glossary (§0.1), and inside the tables themselves.

**Sources.** `MTSAM-ref-1` → `blueprint-UCE.md` (Document 1, Universal Core Engine v30), `blueprint-SBSP.md` (Document 2, Sovereign Bond Sector Pack), `blueprint-MCL.md` (Document 3, Market Configuration Layer §12.2); the reference implementation `source_code/veridict_uce_v6_doc_updated/`; and [MTSAM_Scoring_Objects.md](../Scoring%20Objects/MTSAM_Scoring_Objects.md). MAR/ESMA basis and calibration constants are in [Appendix A](#appendix-a--regulatory-basis-and-global-constants).

---

## §0.1 Master glossary — every abbreviation spelled out

| Abbreviation | Full name | One-line role |
| --- | --- | --- |
| **ADA** | Agence de la Dette (Belgian Debt Agency) | issuer of OLO bonds; auction calendar feeds ECIL |
| **AOB** | Aggressor-on-Book / Adverse Outcome Behaviour | scoring object behind the Aggressor Dominance signal |
| **BC** | Behaviour Category | the classification unit; BC-17 is one of seventeen |
| **BCI** | Behavioural Causality Indicator | leader-vs-follower score; four dimensions D1–D4 |
| **BDS** | Behavioural Drift Score | slow drift of behaviour from own baseline |
| **BOA** | Behavioural Objective Assessment | deterministic risk-objective scoring for HIGH/VERY HIGH |
| **BPL** | Behavioural Persistence Layer | cross-session persistence engine |
| **BT-02** | Block Trade pattern 2 (systematic directional) | block-trade directional confirmation |
| **BTI** | Block Trade Intelligence Score | composite of nine block-trade patterns |
| **CCL** | Causality Confidence Layer | validates behaviour caused the outcome |
| **CCT** | Coordination Classification Tier | EXPLICIT / IMPLICIT / STRUCTURAL coordination |
| **CFS** | Counterfactual Strength Score | the "but-for" causal argument |
| **CQS** | Convergence Quality Score | summed confirmed evidence across five domains |
| **CQT** | Convergence Quality Tier | banded CQS (CQT1 MEDIUM, CQT2 HIGH, CQT3 VERY HIGH) |
| **CWPS** | Cross-Window Persistence Score | same pattern across OPEN/CLOSE windows or sessions |
| **ECB** | European Central Bank | primary information-event source for OLO prices |
| **ECIL** | External Context Intelligence Layer | scored external-event context; drives both timing signals |
| **EDT** | Escalating Dominance Trend | upward trend in market control |
| **ESMA** | European Securities and Markets Authority | EU markets regulator; MAR guidance |
| **HHI** | Herfindahl–Hirschman Index | concentration measure, 0–10,000 scale |
| **HQLD** | Historical Quote Lifecycle Dataset | quote-level history (absent = gap MTSAM-L08) |
| **HSL** | Historical STOR Linkage | amplifier for prior supervisory record |
| **IBE** | Intraday Behavioural Event | clustered trade/quote/alert activity in a time window |
| **IBEB** | Intraday Behavioural Event Builder | assembles IBEs from raw alerts + trades |
| **IDS** | Interaction Detection Score | whether cross-participant interaction exists |
| **IQ** | Interaction Quality (gate) | suppresses interaction evidence with no outcome effect |
| **ISIN** | International Securities Identification Number | the bond identifier (`instrument_id`) |
| **ISS** | Interaction Strength Score | strength/concentration of detected interaction |
| **LEI** | Legal Entity Identifier | the participant identifier |
| **MAR** | Market Abuse Regulation — Regulation (EU) No 596/2014 | the governing regulation |
| **MDCS** | Multi-Day Conditioning Score | pre-positioning across sessions |
| **MTS** | Mercato dei Titoli di Stato | the electronic trading venue |
| **MTSAM** | MTS Analytical Market surveillance | this deployment |
| **MTSAM-L02/L07/L08** | data-limitation codes | order-cancel events / order-level attribution / HQLD absent |
| **MWBR** | Market-Wide Behavioural Reference | peer normalisation (NORMAL/ELEVATED/ANOMALOUS) |
| **NCS** | Network Centrality Score | leader-vs-follower centrality in the network |
| **OLO** | Obligation Linéaire / Lineaire Obligatie | Belgian linear government bond (the instrument) |
| **OPL** | Outcome Persistence Layer | whether an outcome persisted |
| **ORS** | Outcome Recurrence Score | cross-session causal consistency |
| **OS** | Outcome Score | PI Price / LI Liquidity / I Information / BC Behavioural-Conditioning impact |
| **OSS** | Outcome Sensitivity Score | instrument-sensitivity multiplier |
| **PDRP** | Participant-Day Risk Profile | consolidated daily participant assessment object |
| **PIR** | Participant Intelligence Repository | the engine's behavioural memory (amplifier-only) |
| **PLCS** | Participant Liquidity Contribution Score | net liquidity provided vs removed |
| **POFP** | Participant Order Flow Profile | per-participant behavioural baseline (mean + σ) |
| **PSP** | Participant Session Profile | daily per-participant behavioural object |
| **QBBE** | Quote Behaviour Baseline Engine | participant quote baselines |
| **QBCCL** | Quote Behaviour Contextual Confidence Layer | contextual sensitivity multiplier |
| **QBRS** | Quote Behaviour Risk Score | composite quote-domain risk score |
| **QCR** | Quote Cancellation Ratio | cancelled ÷ (executed+cancelled+expired) |
| **QDSP** | Quote Depth Share Position | share of visible book depth |
| **QLS** | Quote Lifetime Score | short-cancel vs long-survive ratio |
| **RA** | Risk Archetype | the narrative explaining potential abuse |
| **RA-28** | Insider Dealing Indicator — Sensitive Timing | primary archetype of BC-17 |
| **RA-29** | Front-Running Indicator | primary archetype of BC-17 |
| **RD** | Reporting-Day alert | end-of-day alert primitive (RD01–RD04) |
| **RSA** | Reasonable Suspicion Assessment | six-indicator MAR Article 16 score |
| **RT** | Real-Time alert | intraday alert primitive (RT01, RT02, RT04, RT05, RT08) |
| **SCS_bpl** | Session Consistency Score (Behavioural Persistence Layer) | recurrence of a pattern across sessions |
| **SRI** | Spread Rationality Indicator | economic rationality of spread crossing |
| **SRS** | Structural Relationship Score | reference-data relationship level |
| **STOR** | Suspicious Transaction and Order Report | the MAR Article 16 filing |
| **TCE** | Temporal Correlation Engine | maps events vs behaviour on a timeline |
| **TCS** | Temporal Correlation Score | the Event Proximity signal's formula output |
| **TPS** | Timing Precision Score | cross-session timing precision |
| **UBO** | Ultimate Beneficial Owner | ownership link (feeds SRS) |
| **UEEO** | Unified Enriched Event Object | five-stream fused event record |
| **VMI** | Volume Materiality Index | volume-context amplifier |

## §0.2 Notation & symbols

| Symbol | Reads as | Meaning |
| --- | --- | --- |
| `p` | *participant* | the dealer being assessed (`MTSTrade.participant_id`, maps to the Legal Entity Identifier) |
| `s` | *session* | one trading day (`MTSTrade.session_date`) |
| `τ` (tau) | *a trade* | one row of the MTS (Mercato dei Titoli di Stato) Trades feed = one execution |
| `e` | *an event* | one benchmark-window episode |
| `notional` / `notional_eur` | *euro size of a trade* | the euro nominal (face) value of a single fill — not a price, not a quantity |
| `Σ` | *"sum over…"* | iterate the matching rows and total the named field |
| `mean` | *average* | the centre of a series of values |
| `σ` (sigma) | *standard deviation* | how much a series typically wanders around its mean |
| `dev` / z-score | *deviation* | `(value − mean) ÷ σ` — "how many standard deviations from normal" |
| subscript `_p` / `_s` | *"for p" / "in s"* | scopes a value to a participant and/or session |

- **A subscript is a filter, not a new quantity.** `X_p_s` is `X` computed on the rows where `participant_id = p` **and** `session_date = s`.
- **"POFP baseline applied to a series" returns *two* numbers** — a `mean` and a `σ` — from the same series; they are used differently (see §1.7).

---

# Layer 1 — Raw Data Ingestion

Everything BC-17 computes reduces to the records below. These are the actual schemas from the reference adapter (`mts_adapter/mts_adapter.py`, `mts_adapter/alert_map.py`), with the source feed each field arrives on. This is the foundation the whole flowchart stands on.

## §1.1 `MTSTrade` — one executed trade (MTS Trades feed, "Layer 1 Core Surveillance")

| Field | Type | Meaning | Origin |
| --- | --- | --- | --- |
| `participant_id` | str | MTS (Mercato dei Titoli di Stato) member identifier — **maps to the LEI (Legal Entity Identifier)** | delivered |
| `instrument_id` | str | the bond's **ISIN (International Securities Identification Number)** | delivered |
| `session_date` | str `YYYY-MM-DD` | trading day | delivered |
| `timestamp` | datetime | execution time | delivered |
| `notional_eur` | float | **euro nominal value of the trade** | **delivered, pre-computed** |
| `direction` | str | `BUY` / `SELL` (participant's side) | delivered |
| `price` | float | execution price | delivered |
| `is_aggressor` | bool | **TRUE if this participant took liquidity (crossed the spread)** | **delivered boolean** |
| `is_block_trade` | bool | TRUE if `notional_eur ≥ block_trade_threshold_eur` | delivered / derived at ingest |
| `counterparty_id` | str? | counterparty member id (often null in the anonymous book) | delivered where available |

**The two fields the whole of Aggressor Dominance rests on:**
- **`notional_eur`** — the MTS feed delivers the trade's euro nominal directly. If a feed instead delivered `price` + `quantity`, notional would be derived at ingest as the face amount, with cash consideration `= dirty_price ÷ 100 × nominal`. In the MTSAM (MTS Analytical Market) data contract this has already happened upstream — `notional_eur` arrives ready to sum.
- **`is_aggressor`** — on MTS every trade is an incoming order matching a *resting* quote; the venue tags the incoming (liquidity-taking) side as aggressor and exports this boolean. The engine consumes it as-is (configuration flag `has_aggressor_flag = True`, §1.5). Only if that flag were `False` would it have to be inferred from trade-price-vs-quote, which needs quote data (gap MTSAM-L07).

⤷ *Feeds:* AOB, BCI dimension 3, Volume Materiality Index, Block Trade Intelligence Score, the Participant Order Flow Profile baseline, and the market-share denominators throughout Layer 2.

## §1.2 `RawMTSAlert` — one surveillance alert (MTS S.p.A. surveillance export)

| Field | Type | Meaning |
| --- | --- | --- |
| `alert_code` | str | one of `RT01, RT02, RT04, RT05, RT08` (Real-Time) or `RD01–RD04` (Reporting-Day) |
| `participant_id` | str | MTS member id → LEI (Legal Entity Identifier) |
| `instrument_id` | str | ISIN (International Securities Identification Number) |
| `session_date` | str | trading day |
| `alert_timestamp` | datetime? | `None` for end-of-day (Reporting-Day) alerts |
| `alert_score` | float [0–1] | raw MTS alert score where provided |
| `notional` | float | alert notional |
| `direction` | str? | `BUY` / `SELL` / `NEUTRAL` |

The nine implemented alert primitives and their mapping (from `alert_map.py`), with abbreviations spelled out:

| Alert code | Meaning | Domain | Feeds |
| --- | --- | --- | --- |
| **RT01** (Real-Time 01) | Momentum ignition | A (execution) | **AOB / BCI-D3 confirmation** → Aggressor Dominance |
| **RT02** (Real-Time 02) | Excessive activity (abnormal trade count) | A | Volume indicator |
| **RT04** (Real-Time 04) | Price deviation from reference | A | Reference-price influence |
| **RT05** (Real-Time 05) | Opposite interaction (wash-trade indicator) | C (interaction) | IDS (Interaction Detection Score) |
| **RT08** (Real-Time 08) | Liquidity stress proximity | A | Liquidity conditioning |
| **RD01–RD04** (Reporting-Day 01–04) | End-of-day volume / dominance / quote / execution | B (cross-session) | Market Dominance (BCI-D4), reference-price marking |

The venue's **internal trigger logic is proprietary** — the engine consumes only the fired record. For BC-17 the single relevant alert is **RT01**, which gates Aggressor Dominance (§2.1, §3.1).

⤷ *Feeds:* the Domain-A Convergence Quality Score contribution (`Σ(confirmed primitive × 0.50)`, cap 4.0), the Intraday Behavioural Event assembly, and the RT01 gate inside AOB/BCI-D3.

## §1.3 `InstrumentRef` — instrument reference (MTS Instrument Reference feed)

`instrument_id`, `isin`, `instrument_cluster_id`, `benchmark_tier ∈ {OFF_THE_RUN, ACTIVE_SECONDARY, BENCHMARK, BENCHMARK_ANCHOR}`, `maturity_date`, `is_benchmark`, `block_trade_threshold_eur` (default **€25,000,000**). This is **static master data** — one row per bond, keyed by ISIN — joined to each trade via `instrument_id`.

⤷ *Why it matters:* `benchmark_tier` defines what a "benchmark-window event" is (used in Aggressor Dominance level 3 and the Outcome Sensitivity Score); `block_trade_threshold_eur` sets `is_block_trade` (feeds Block Trade pattern 2 → BCI-D3); `instrument_cluster_id` defines the population over which dominance/market-share are measured.

## §1.4 `SessionContext` and `PeerSession` — market-wide and peer data

`SessionContext` (`mts_adapter.py` 45–70): `total_session_volume_eur`, `peer_count`, `peer_median_qcr`, `peer_std_qcr`, External Context Intelligence Layer flags (`has_ecb_event`, `has_ada_auction`, `has_suspension`, `ecil_crs`), and the sensitive windows (`close_window_start/end`, `auction_window_start/end`, `suspension_time`).
`PeerSession` (`mwbr.py` 8–17), one per active dealer: `participant_id`, `volume_eur`, `market_share`, `quote_withdrawal_rate` (−1 = not available), `spread_contribution`, `block_trade_share`, `had_rt_alert`, `had_rd_alert`.

⤷ *Feeds:* the Market-Wide Behavioural Reference peer baseline (§1.8), the External Context Intelligence Layer amplification, and the Sensitive Timing window overlap.

## §1.5 Data-availability contract (what is and isn't computable)

Source: `config.py` `MTSAMConfig`. This governs every "requires…" note in Layer 2.

| Flag | Value | Consequence |
| --- | --- | --- |
| `has_intraday_trade_timestamps` | **True** | trade-time windowing available |
| `has_aggressor_flag` | **True** | **Aggressor Dominance computable from trades** |
| `has_participant_ids_trade` | **True** | per-participant trade aggregation available |
| `has_participant_ids_quote` | **False** | quote attribution absent → gap **MTSAM-L07** (caps CCT at IMPLICIT; QDSP, SRI = undetermined) |
| `has_order_cancel_events` | **False** | gap **MTSAM-L02** (QLS, layering unavailable) |
| `has_hqld` | **False** | gap **MTSAM-L08** — Historical Quote Lifecycle Dataset absent (BCI D1/D2, quote leadership → 0) |
| `has_otc_intraday` / `has_eurex_intraday` / `has_rfq_order_flow` | **False** | cross-venue / cross-market patterns unavailable |

## §1.6 The processing chain (raw → scored)

```
MTS Trades feed ─┐
MTS Alerts feed ─┤→ MTSSessionAdapter.build_ibes()  →  IBE objects  →  PDRP / POFP aggregation  →  Layer 2 scoring objects
Instrument Ref ──┤     (IBEB windowing, 20 min)         (per window)     (participant-day / 45–90-day baselines)
SessionContext ──┘
```
- **IBEB (Intraday Behavioural Event Builder) windowing** (`mts_adapter.py` 265–321): intraday timestamps are sorted; activity within `IBEB_WINDOW_MINUTES = 20` minutes is merged into one **IBE (Intraday Behavioural Event)** window.
- **Sensitive-timing flag** (`_is_sensitive_timing`, 367–379): the IBE window overlaps a `close_window`, `auction_window`, or is within **600 seconds** of `suspension_time`. *This is the raw origin of the Sensitive Timing detection signal (§3.2).*
- **PDRP (Participant-Day Risk Profile)** consolidates a participant's day; **POFP (Participant Order Flow Profile)** builds the multi-session baselines (§1.7).

## §1.7 The Participant Order Flow Profile (POFP) baseline — the "σ factory"

Every `σ`/deviation in BC-17 is produced here (`pofp.py`).

**Inputs.** A list of `POFPSession` records (one per past session): `daily_volume_eur`, `session_market_share`, `close_window_share`, `block_trade_count`, `block_trade_volume_eur`, `quote_cancellation_rate`, `spread_contribution`. **Each is itself aggregated from that session's raw `MTSTrade` rows** (e.g. `daily_volume_eur = Σ notional_eur` over the participant's trades that day; `session_market_share = daily_volume_eur ÷ total_session_volume_eur`).

**Computation** (`compute_profile`), for a metric `X`:
```
window   = [ sessions with cutoff ≤ session_date < as_of ]        # cutoff = as_of − lookback_days
values   = [ s.X for s in window if s.X > 0 ]                     # zero/empty sessions excluded
mean(X)  = statistics.mean(values)
std(X)   = statistics.stdev(values)  if len(values) > 1 else 0.0  # SAMPLE stdev (n−1) ← this is "σ"
sigma(current) = (current − mean(X)) / std(X)   if std(X) > 0 else 0.0
sufficient_history = len(window) ≥ min_sessions
```

### Why the mean and the σ are used *differently* (the z-score logic)
The `mean` and the `σ` come from the **same** history, so their lineage is identical — but they are **two different statistics** doing **two different jobs** in `dev = (current − mean) ÷ σ`:
- **The mean is *subtracted* → it *centres* the value.** It answers *"how far is today above this participant's own normal?"* Without it a raw value is meaningless — a level that is high for one participant may be perfectly ordinary for another whose baseline is higher.
- **σ is *divided* → it *scales* the value.** It answers *"is that gap large relative to how much this participant normally wanders?"* A fixed distance above the mean is alarming for a participant whose metric barely moves, but unremarkable for one whose metric swings widely; dividing by σ makes the distance comparable across participants.

So the mean supplies the *distance from normal* (location) and σ supplies the *unit that distance is measured in* (dispersion). Every `2σ`/`1σ` threshold below reads this way.

⚠ **Calibration discrepancy.** The reference engine defaults to **90 days / 15 sessions**; the methodology (T-003) specifies **45 days / 10 sessions**. See [Appendix D](#appendix-d--constants-and-discrepancies).

## §1.8 The Market-Wide Behavioural Reference (MWBR) peer baseline

Where a test is peer-relative (not own-baseline), the σ comes from here (`mwbr.py`):
```
mean = statistics.mean(peers)     # peers = the metric across all OTHER active dealers that session
std  = statistics.stdev(peers)
sigma = (target − mean) / std
bands: sigma ≥ 2.0 → ANOMALOUS · ≥ 1.0 → ELEVATED · < 0 → BELOW_NORMAL · else NORMAL
```
Requires **≥ 3 peer sessions**; the target is excluded from its own peer set. Peer values come from the `PeerSession` records (§1.4).

---

# Layer 2 — Scoring Objects

The scoring objects sit between raw data and detection signals. The BC-17 diagram groups them into two families: **Interaction & relationship** (Category 5 of the Scoring Objects Reference: IDS, ISS, IQ, CCT, SRS, NCS, AOB) and **Context, history, instrument & intent** (Category 7: ECIL, HSL, PIR, BCI, RSA). Of these, only **AOB**, **BCI dimension 3** and **ECIL** are *inputs* to BC-17's three detection signals; the rest are corroborative or downstream amplifiers.

## §2.1 AOB — Aggressor-on-Book / Adverse Outcome Behaviour  *(required)*

- **Definition.** Repeated economic irrationality — loss-making reversals and persistent aggressor dominance.
- **Formula (full, corrected):**
```
aggr_dev_s        = (aggressor_share_s − POFP_aggr_mean) ÷ POFP_aggr_σ
AOB_reversal_rate = adverse_aggressor_reversals ÷ total_aggressor_round_trips     # over EPISODE_SESSION_WINDOW = 14 days
n_anom_sessions   = |{ s : aggr_dev_s > 2σ AND RT01 (Real-Time 01) fires in s }|

           ⎧ 0 LOW         if AOB_reversal_rate < 0.20  AND  max_s aggr_dev_s ≤ 1σ
AOB_level =⎨ 1 MODERATE    if 0.20 ≤ rate < 0.40   OR   1σ < aggr_dev ≤ 2σ (RT01 non-systematic)
           ⎪ 2 SIGNIFICANT if 0.40 ≤ rate < 0.60   AND  n_anom_sessions ≥ 2
           ⎩ 3 DOMINANT    if rate ≥ 0.60   OR   primary aggressor in ≥3 benchmark-window events (BT-02 OR SCS_direction)
```
- **Translation table — every term traced to raw data (Layer 1):**

| Value | Computation from raw data | Raw fields (Layer 1) |
| --- | --- | --- |
| `agg_notional_p_s` | `Σ notional_eur` over `MTSTrade` rows where `participant_id = p` AND `session_date = s` AND `is_aggressor = TRUE` | `MTSTrade.participant_id`, `.session_date`, `.is_aggressor`, `.notional_eur` (§1.1) |
| `agg_notional_market_s` | same sum, all participants (`session_date = s`, `is_aggressor = TRUE`) | `MTSTrade.session_date`, `.is_aggressor`, `.notional_eur` |
| `aggressor_share_s` | `agg_notional_p_s ÷ agg_notional_market_s` | the two above |
| `POFP_aggr_mean`, `POFP_aggr_σ` | POFP baseline (§1.7) over the series of prior `aggressor_share` values | historical `MTSTrade` rows |
| `aggr_dev_s` | `(aggressor_share_s − POFP_aggr_mean) ÷ POFP_aggr_σ` | the three above |
| `adverse_aggressor_reversal` | aggressor round-trip with realised P&L `< 0`, ≥ `REVERSAL_FRACTION` (0.50) unwound within same session, notional ≥ `REVERSAL_MATERIALITY` (≥25% session volume or ≥€25m) | `MTSTrade.timestamp`, `.direction`, `.price`, `.notional_eur`, `.is_aggressor` |
| `RT01 fires` | Real-Time 01 momentum-ignition alert boolean | `RawMTSAlert.alert_code = RT01` (§1.2) |
| `AOB_level` | the piecewise rule — **computed, not looked up** | all the above |

- **Correction basis (was undefined `T-095`).** "Adverse reversal", the level bands, and `EPISODE_SESSION_WINDOW` are proposed calibrations grounded in MAR (Market Abuse Regulation) Article 12(1)(a) and Delegated Regulation (EU) 2016/522 Annex II (reversal indicator); the 2σ bar matches the MWBR (Market-Wide Behavioural Reference) ANOMALOUS band. See [Appendix A](#appendix-a--regulatory-basis-and-global-constants).
- ⚠ **Implementation gap (C-1).** The reference `POFPSession` has **no aggressor-share dimension**; `two_axis.py` reads the aggressor σ as `getattr(pdrp, "pdrp_aggressor_share_sigma", 0.0)` — defaulting to 0, which collapses the signal unless the aggregation `MTSTrade → aggressor_share_s → POFP baseline → pdrp_aggressor_share_sigma` is added. See [Appendix C](#appendix-c--implementation-grounding-gap-register).
- ⤷ *Feeds:* Detection Signal **Aggressor Dominance** (§3.1); RSA (Reasonable Suspicion Assessment) Economic Irrationality indicator (§2.9).

## §2.2 BCI — Behavioural Causality Indicator  *(dimension 3 required)*

- **Definition.** The participant's causal role — leader vs follower — across four dimensions. **Formula:** `BCI = D1 + D2 + D3 + D4` (each 0–3; composite 0–12).
- **Dimension 3 — Aggressor Dominance** (the BC-17-relevant one; `two_axis.py` / Document 3 §12.2):
```
      ⎧ 0  aggr_dev ≤ 1σ
D3 =  ⎨ 1  1σ < aggr_dev ≤ 2σ                 (RT01 fires, non-systematic)
      ⎪ 2  aggr_dev > 2σ in ≥2 sessions       AND RT01 fires in those sessions
      ⎩ 3  primary aggressor in ≥3 benchmark-window events (BT-02 OR SCS_direction_confirmed)
```

| Value | Computation | Raw source |
| --- | --- | --- |
| `aggr_dev` | own-baseline aggression deviation | = `aggr_dev_s` (§2.1) |
| `RT01 fires` | Real-Time 01 alert | `RawMTSAlert` (§1.2) |
| `benchmark-window event` | activity in a benchmark-sensitive window on a `BENCHMARK`/`BENCHMARK_ANCHOR` instrument | `InstrumentRef.benchmark_tier` (§1.3) + sensitive windows (§1.4) |
| `BT-02` (Block Trade pattern 2) | systematic same-direction block pattern | block trades (`MTSTrade.is_block_trade`, `.direction`) |
| `SCS_direction_confirmed` | one-sided persistence, `max(buy,sell) ÷ min ≥ 3.0` | Behavioural Persistence Layer |

- **Other dimensions (context only for BC-17):** **D1 Quote Leadership** and **D2 Liquidity Leadership** require the Historical Quote Lifecycle Dataset / order-book depth (gaps MTSAM-L08 / L02) → default **0**. **D4 Market Dominance** is live (from the Reporting-Day 02 alert close-share, the Escalating Dominance Trend, and the Behavioural Persistence Layer campaign score) but is not one of BC-17's three signals.
- **Correction basis (was undefined `T-114`).** 0-vs-1 boundary fixed at 1σ (MWBR ELEVATED band). ⚠ Implementation gaps C-1, C-2, C-3 ([Appendix C](#appendix-c--implementation-grounding-gap-register)).
- ⤷ *Feeds:* Detection Signal **Aggressor Dominance** (§3.1); the Follower Rule (BCI < 3 caps concern at MEDIUM) and VERY HIGH gate (BCI ≥ 7) in Layer 4.

## §2.3 ECIL — External Context Intelligence Layer  *(required)*

- **Definition.** Structured, scored, provenance-chained external-event context with explicit directionality.
- **Formula:** `context_effect = classify(event, behaviour_window) → {SUPPORTS_EXPLANATION | AMPLIFIES_SUSPICION | CONTRADICTS_PATTERN | INSUFFICIENT_CONTEXT}`.

| Value | Computation | Raw source |
| --- | --- | --- |
| `has_ecb_event`, `has_ada_auction`, `has_suspension`, `ecil_crs` | populated from the External Context Intelligence Layer event catalogue | `SessionContext` (§1.4) |
| `ecil_amplification` | `+0.40` European Central Bank event `+ 0.30` ADA (Agence de la Dette) auction `+ 0.20` sensitive `+ (0.20 CRS=VERY_HIGH | 0.10 HIGH) +` coherence, capped 1.0 | `SessionContext` flags |
| `context_effect`, `event_materiality` | Temporal Correlation Engine classification; materiality tier | ECIL event object — **materiality rubric `T-108` deferred (D2)** |

- ⤷ *Feeds:* Detection Signals **Sensitive Timing** (§3.2) and **Event Proximity** (§3.3); the amplifier/suppressor overlay in Layer 4.

## §2.4–§2.9 Corroborative / amplifier scoring objects (full formulas, traced)

These do not feed BC-17's three signals directly, but are given full formulas and lineage so the two families are completely computable. Abbreviations spelled out in each heading.

**§2.4 IDS — Interaction Detection Score.** `z_ids = (ids_response_rate − peer_baseline_rate) ÷ peer_baseline_σ`; levels 0 (≤1σ) / 1 (>1σ, p<0.05) / 2 (≥2σ, ≥3 sessions) / 3 (≥3σ, recurring pair). Raw: `MTSTrade` (aggressor actions + peer same-direction responses within 60 s) + control-window baseline. *Partial* — quote responses need gap MTSAM-L07. Basis: MAR Article 12(1)(a)(ii) "acting in collaboration."

**§2.5 ISS — Interaction Strength Score.** `iss_hhi = Σ(pair_interaction_share)²` (0–10,000); 0 (<1,500) / 1 (1,500–2,499) / 2 (2,500–4,999) / 3 (≥5,000). Raw: interactions tagged by `MTSTrade.counterparty_id`. Basis: European Commission Herfindahl–Hirschman Index concentration tiers.

**§2.6 IQ — Interaction Quality (gate).** `interaction_outcome_score = max over clusters(Outcome Score attributable to cluster)`; if `= 0` → suppress the interaction dimension. Basis: MAR Article 16 proportionality.

**§2.7 CCT — Coordination Classification Tier.** `cct_specificity = (observed − expected clustering) ÷ σ_expected`; STRUCTURAL (<2σ but SRS≥2) / IMPLICIT (2σ–<3σ) / EXPLICIT (≥3σ, order-ID). **Capped at IMPLICIT** in Standard mode (gap MTSAM-L07). Basis: MAR Article 12(1)(a)(ii); Delegated Regulation (EU) 2016/957 (STOR technical standards).

**§2.7b SRS — Structural Relationship Score.** 0 (none) / 1 (indirect) / 2 (same group or UBO, net group position changed) / 3 (same legal entity → internal-abuse pathway). Raw: participant reference data (`group_id`, `ubo_id` = Ultimate Beneficial Owner). Basis: MAR Article 3(1)(26) "persons closely associated."

**§2.8 NCS — Network Centrality Score.** `NCS = 0.35·followership_peer_rank + 0.25·reinforcement + 0.25·quote_leadership + 0.15·block_network`; levels LOW <0.25 / MEDIUM 0.25–0.50 / HIGH 0.50–0.75 / EXCEPTIONAL ≥0.75. `quote_leadership` needs Historical Quote Lifecycle Dataset (gap MTSAM-L08 → 0). Already fully specified in source.

**§2.8b HSL — Historical STOR Linkage.** `CQS_uplift = 0.50·[prior_STOR] + 0.50·[pattern_match] + 0.25·[prior_escalation]`. Raw: the STOR (Suspicious Transaction and Order Report) register (3-year lookback) + signal archive (12 months). Fully specified.

**§2.8c PIR — Participant Intelligence Repository.** `PIR_recurrence_count = COUNT(prior confirmed Behaviour Categories of same type)`; `PIR_history = STRONG (≥3/12mo) | MODERATE (1–2) | NONE (0)`; amplifier-only capping gate (never sole-drives MEDIUM/HIGH — MAR proportionality). Raw: the engine's own `behaviour_categories_history` store.

**§2.9 RSA — Reasonable Suspicion Assessment.** `RSA_net = Σ(indicator_score × weight)`; `rsa_scaled = min(100, round(RSA_net ÷ 18 × 100))`. Weights: Price Impact 0.20, Economic Irrationality 0.20, Repetition 0.15, Participant Intelligence 0.20, Timing 0.15, Coordination 0.10. Each `indicator_score` (0–3) is produced by an object above (Economic Irrationality ← AOB; Coordination ← IDS/ISS/CCT; Participant Intelligence ← PIR/HSL; Timing ← TPS/sensitive-timing; Price ← Outcome Score; Repetition ← SCS_bpl). Bands: LOW ≤40 / MEDIUM 41–70 / HIGH 71–85 / VERY HIGH ≥86. Basis: MAR Article 16. Full 0–3 rubric in [Appendix A](#appendix-a--regulatory-basis-and-global-constants).

---

# Layer 3 — Detection Signals

Detection signals are observations, not conclusions. BC-17's three constituent signals sit in two domains: **D1 — Volume and Participation** (Aggressor Dominance) and **D2 — Timing** (Sensitive Timing, Event Proximity).

## §3.1 Aggressor Dominance (Domain D1 — Volume and Participation)

- **Engine mapping.** AOB (Aggressor-on-Book, §2.1) with numeric anchors from BCI (Behavioural Causality Indicator) dimension 3 (§2.2).
- **Formula:** `AggressorDominance_level = max(AOB_level, BCI_D3_level)` → **fires where ≥ 2**. Risk Archetype RA-29 form fires where `≥ 2 AND SCS_direction_confirmed = TRUE`.
- **Links back to raw data:** `MTSTrade.is_aggressor` + `.notional_eur` + `.direction` + `.timestamp` (§1.1); `RawMTSAlert.alert_code = RT01` (§1.2); the POFP σ (§1.7). Fully raw-grounded, subject to gap C-1.

## §3.2 Sensitive Timing (Domain D2 — Timing)

- **Engine mapping.** ECIL (External Context Intelligence Layer, §2.3) event-proximity scoring; construct `IBE_sensitive_timing_flag = TRUE` where the Intraday Behavioural Event window overlaps an information-event window (`ibe_event_type = INFORMATION_EVENT`).
- **Formula / lineage.** `IBE_sensitive_timing_flag` = `_is_sensitive_timing` (§1.6): the IBE window (from `MTSTrade.timestamp` clustering) overlaps `SessionContext.close_window_*` / `auction_window_*` / within 600 s of `suspension_time`, and — for BC-17 — the ECIL information-event window.
- **Deferred (D2):** the `INFORMATION_EVENT` subtype crosswalk, per-event `event_window_minutes`, Intraday-Behavioural-Event score weights (`T-013`), and `PRE_EVENT_CONDITIONING_WINDOW` value ([Appendix B](#appendix-b--deferred-d2--timing)).

## §3.3 Event Proximity (Domain D2 — Timing)

- **Engine mapping.** ECIL Temporal Correlation Engine (§2.3). The one signal with a fully written formula.
- **Formula:**
```
TCS (Temporal Correlation Score) = event_materiality_weight × co_occurrence_weight × direction_alignment_score   (∈ [0,1])
  event_materiality_weight: VERY_HIGH 1.0 · HIGH 0.75 · MEDIUM 0.50 · LOW 0.25
  co_occurrence_weight:     strict 1.0 · pre_event 0.85 · post_event 0.80 · proximate 0.7
  direction_alignment:      consistent 1.0 · opposite 0.3 · neutral/unknown 0.5
```
- **Links back to raw data:** `co_occurrence_weight` from comparing `MTSTrade.timestamp` to the ECIL `event_window_*`; `direction_alignment_score` from `MTSTrade.direction` vs the ECIL `actual_direction`.
- **Deferred (D2):** materiality rubric (`T-108`), window sizes, `SURPRISE_THRESHOLD`, `historical_std_dev` basis ([Appendix B](#appendix-b--deferred-d2--timing)).

---

# Layer 4 — Behavioural Category (BC-17)

## §4.1 The deterministic combination

BC-17 fires only when **all three** detection signals co-occur on the same episode (Document 1 §VI.1a.2, row 17):
```
Event Proximity (ECIL Temporal Correlation Engine: an INFORMATION_EVENT with a confirmed TCS)
   +  Sensitive Timing (IBE_sensitive_timing_flag = TRUE inside that event window)
   +  Aggressor Dominance (AggressorDominance_level ≥ 2)
   =  BC-17 — Event-Driven Information Behaviour
```
Read plainly: **an information event happened (ECIL), the participant's trading concentrated in that event's window (Sensitive Timing), and in that window the participant was the dominant aggressor (AOB / BCI dimension 3).**

## §4.2 Distinct from Behaviour Category 9 (Auction Conditioning)

- **Category 9** — scheduled, recurring **market-structure** events (auctions, benchmark fixings) → optimisation of market structure.
- **Category 17** — **information** events (central-bank decisions, rating actions, issuer/regulatory announcements) where concentration suggests **information advantage**. This is why `ibe_event_type` must resolve to `INFORMATION_EVENT`, and why the ECIL `surprise_score` / participant-benefit-alignment test (the intersection with MAR Article 14, insider dealing) matters here.

## §4.3 Amplifier / suppressor overlay (`Base Concern + Amplifiers − Suppressors = Final Concern`)

Once BC-17 assembles, the scoring objects that were *not* signal inputs drive the concern calculus:
- **ECIL `context_effect`** — `AMPLIFIES_SUSPICION` tightens proportionality; `CONTRADICTS_PATTERN` can attribute the move to the event and downgrade.
- **BCI level** — Follower Rule: BCI < 3 caps concern at MEDIUM; BCI ≥ 7 opens VERY HIGH.
- **HSL / PIR** — prior-STOR and recurrence amplifiers (§2.8b, §2.8c).
- **RSA** — aggregates the fired signals into the MAR Article 16 score (§2.9).

## §4.4 Validation footprint

Document 1 §XV.5: BC-17 is exercised by scenarios **S61–S63** and test cases **T287–T295**.

---

# Layer 5 — Risk Archetypes

BC-17 is the **primary** Behaviour Category for two Risk Archetypes (Document 1 §VI.1a.3). Risk Archetypes provide the explanatory narrative once a signal has qualified — they do not drive scoring.

| Risk Archetype | Full name | Definition | Requires |
| --- | --- | --- | --- |
| **RA-28** | Insider Dealing Indicator — Sensitive Timing | Sensitive Timing + Event Proximity + Aggressor Dominance convergence | `IBE_sensitive_timing_flag = TRUE` + ECIL event proximity confirmed |
| **RA-29** | Front-Running Indicator | Event Proximity + Aggressor Dominance, ECIL event = information-type | ECIL proximity confirmed + aggressor dominance (AOB + SCS_direction) confirmed |

## §5.1 End-to-end trace (the whole flowchart in one line)

```
MTSTrade.is_aggressor + .notional_eur + .direction          RawMTSAlert.RT01        ECIL event object
        │  (Layer 1)                                              │                      │
        ▼                                                         ▼                      ▼
   aggressor_share_s ──POFP σ──▶ aggr_dev_s ──┐            RT01 gate            TCS + sensitive-window overlap
        (Layer 2: AOB / BCI-D3)               ├──▶ AggressorDominance ≥ 2   (Layer 3: Event Proximity + Sensitive Timing)
                                              │        (Layer 3)                        │
                                              └───────────────┬───────────────────────┘
                                                              ▼
                                             BC-17 (Layer 4)  =  Event Proximity + Sensitive Timing + Aggressor Dominance
                                                              ▼
                                             RA-28 / RA-29 (Layer 5)  +  Final Concern via amplifier/suppressor overlay
```

---

# Appendix A — Regulatory basis and global constants

**Regulatory note.** MAR (Market Abuse Regulation — Regulation (EU) No 596/2014) and the ESMA (European Securities and Markets Authority) texts are principles-based: they define the qualitative indicator, not the numeric trigger. Every threshold below is a proposed supervisory calibration for the OLO (Obligation Linéaire / Lineaire Obligatie) sovereign-bond interdealer context, anchored to the cited indicator and to conventions the engine already uses.

| Reference | Source | Used for |
| --- | --- | --- |
| MAR Article 8 / Article 14 | insider dealing | BC-17 purpose; participant-benefit alignment |
| MAR Article 12(1)(a) | manipulation — false signals / price securing | Aggressor Dominance, AOB reversals |
| MAR Article 12(1)(a)(ii) | "acting in collaboration" | IDS, ISS, CCT |
| MAR Article 16 | Suspicious Transaction and Order Report obligation | RSA, IQ effect gate |
| Delegated Regulation (EU) 2016/522, Annex II | indicators of manipulation (momentum ignition, reversals) | AOB, Aggressor Dominance |
| Delegated Regulation (EU) 2016/957 | STOR regulatory technical standards | SRS, coordination evidence |
| MAR Article 3(1)(26) | "persons closely associated" / group | SRS tiers |
| European Commission Horizontal Merger Guidelines | Herfindahl–Hirschman Index tiers 1,500 / 2,500 / 5,000 | ISS, NCS, CCT |

**Global constants** (`veridict_uce/constants.py`):

| Constant | Value | Meaning |
| --- | --- | --- |
| `IBEB_WINDOW_MINUTES` | 20 | Intraday Behavioural Event Builder window |
| `EPISODE_SESSION_WINDOW_DAYS` | 14 | AOB / BCI episode window |
| `LOOKBACK_30D` / `LOOKBACK_3Y_DAYS` | 30 / 1095 | Escalating Dominance Trend / Historical STOR Linkage |
| `block_trade_threshold_eur` | 25,000,000 | `is_block_trade` cut-off |
| MWBR bands | 1.0σ / 2.0σ | ELEVATED / ANOMALOUS |
| `REVERSAL_FRACTION` / `REVERSAL_MATERIALITY` | 0.50 / 25% or €25m | adverse-reversal definition |
| NCS weights | 0.35 / 0.25 / 0.25 / 0.15 | Network Centrality Score |
| RSA weights | 0.20 / 0.20 / 0.15 / 0.20 / 0.15 / 0.10 | Reasonable Suspicion Assessment |
| HSL Convergence-Quality-Score uplift | 0.50 / 0.50 / 0.25 | Historical STOR Linkage |

**RSA (Reasonable Suspicion Assessment) per-indicator rubric (0–3):**

| Indicator (weight) | 0 | 1 | 2 | 3 |
| --- | --- | --- | --- | --- |
| Price Impact (20%) | Outcome Score Price Impact = 0 | =1 transient | =2 or Counterfactual Strength ≥1 | =2 with Causality Confidence ≥1 and Outcome Persistence ≥1 |
| Economic Irrationality (20%) | AOB level 0 | 1 | 2 or Spread Rationality ≥2σ | 3 |
| Repetition (15%) | SCS_bpl <0.30 | 0.30–0.60 | ≥0.60 | ≥0.60 + directional confirmation |
| Participant Intelligence (20%) | PIR clean | prior monitoring | HSL prior escalation | HSL prior STOR + pattern match |
| Timing (15%) | TPS <0.30 | 0.30–0.55 | 0.55–0.75 or sensitive-timing confirmed | TPS ≥0.75 (PRECISE) |
| Coordination (10%) | IDS = 0 | IDS ≥1 | ISS ≥2 or CCT IMPLICIT | CCT EXPLICIT |

# Appendix B — Deferred (Domain D2 — Timing)

| Signal / object | Still-open variable |
| --- | --- |
| Sensitive Timing | `INFORMATION_EVENT` subtype crosswalk; per-event `event_window_minutes`; Intraday-Behavioural-Event score weights (`T-013`); `PRE_EVENT_CONDITIONING_WINDOW` value |
| Event Proximity / ECIL | event materiality rubric (`T-108`); `ECIL_PROXIMITY_WINDOW_MINUTES` / `POST_EVENT_EXPLOITATION_WINDOW_MINUTES`; `SURPRISE_THRESHOLD`; `historical_std_dev` basis for `surprise_score` |

# Appendix C — Implementation-grounding gap register

| # | Value | Nature of gap | Effect |
| --- | --- | --- | --- |
| C-1 | `pdrp_aggressor_share_sigma` (AOB / BCI-D3) | `POFPSession` has no aggressor-share dimension; read via `getattr(...,0.0)` | Aggressor Dominance → 0 unless upstream aggregation added |
| C-2 | BCI dimension 3 `=3` branch | absent in the Participant-Day-Risk-Profile proxy; `d3_directional` computed but unused | D3 caps at 2 |
| C-3 | BCI dimensions 1 / 2 | need Historical Quote Lifecycle Dataset (L08) / order-book depth (L02) | default 0 |
| C-4 | CCT = EXPLICIT | needs per-quote / order-ID attribution (L07) | capped at IMPLICIT |
| C-5 | NCS quote-leadership; QLS; QDSP; SRI | need HQLD / quote / order-cancel atoms | 0 / undetermined |
| C-6 | `counterparty_id`-based terms (ISS, Block Trade pattern 6, NCS block-network) | counterparty often null in the anonymous book | partial |

# Appendix D — Constants and discrepancies (code vs methodology)

- **POFP (Participant Order Flow Profile) lookback:** code **90 days / 15 sessions** (`pofp.py`) vs methodology **45 days / 10 sessions** (`T-003`).
- **RSA (Reasonable Suspicion Assessment) bands:** code LOW ≤40 / MEDIUM 41–70 / HIGH 71–85 / VERY HIGH ≥86 vs methodology "≥72 HIGH / 41–71 MEDIUM" (`T-117`).
- **Aggressor-share baseline dimension:** specified (`T-113`) but not present in `POFPSession` (gap C-1).

# Appendix E — Theoretical-framework terms referenced (spelled out)

| Term code | Name | Definition |
| --- | --- | --- |
| `T-002` | POFP deviation | `(current_session_value − POFP_baseline_mean) ÷ POFP_baseline_σ`, in σ units |
| `T-003` | POFP baseline mean / σ | per-dimension mean and standard deviation over the baseline window (methodology: 45 days, ≥10 sessions) |
| `T-004` | Peer deviation (Market-Wide Behavioural Reference) | `(participant_value − peer_session_median) ÷ peer_σ` across the 12–18 active dealers |
| `T-011` | Intraday-Behavioural-Event sensitive-timing flag | TRUE where the event window overlaps CLOSE / AUCTION / PRE-SUSPENSION (or, for BC-17, the information-event window) |
| `T-013` | Intraday-Behavioural-Event score | weighted composite of stream count, primitive count, sensitive timing, context (weights not stated — deferred) |
| `T-081` | Directionally consistent peer response | a peer action in the same direction within the 60-second peer-timing window |
| `T-095` | AOB frequency score | cross-session frequency of aggressor executions and adverse reversals (no closed formula in source — corrected §2.1) |
| `T-108` | External-Context-Intelligence-Layer event materiality score | weighting of a matched event (rubric outside the document set — deferred) |
| `T-113` | Aggressor-share deviation (BCI-D3) | participant aggressor share vs own POFP baseline; test >2σ in ≥2 sessions with RT01 |
| `T-114` | BCI dimension levels | 0–3 per dimension (0-vs-1 boundary not enumerated in source — corrected §2.2) |
| `T-115` / `T-117` | RSA indicator level / scaled score | per-indicator 0–3 (corrected §2.9); `rsa_scaled = min(100, round(net ÷ 18 × 100))` |

# Appendix F — Chronological calculation sequence (raw data → classification)

Every calculation in the BC-17 chain, in the order it is executed, with its output. Read top-to-bottom, this is the full pipeline from a raw trade row to the final risk archetype. (Abbreviations per §0.1.)

| # | Layer | Calculation | Operation / formula | Output |
| --- | --- | --- | --- | --- |
| 1 | 1 | Ingest raw records | read `MTSTrade`, `RawMTSAlert`, `InstrumentRef`, `SessionContext`, `PeerSession` | raw rows (no computation) |
| 2 | 1 | `agg_notional_p_s` | `Σ notional_eur` where `participant_id=p AND session_date=s AND is_aggressor=TRUE` | euro total |
| 3 | 1 | `agg_notional_market_s` | `Σ notional_eur` where `session_date=s AND is_aggressor=TRUE` (all participants) | euro total |
| 4 | 1 | `aggressor_share_s` | `agg_notional_p_s ÷ agg_notional_market_s` | ratio ∈ [0,1] |
| 5 | 1 | POFP baseline | `mean`, `σ` over the participant's prior `aggressor_share` series (§1.7) | `POFP_aggr_mean`, `POFP_aggr_σ` |
| 6 | 1 | IBEB windowing | cluster intraday `timestamp`s into 20-minute Intraday Behavioural Event windows | IBE windows |
| 7 | 1 | Sensitive-window overlap | IBE window ∩ (CLOSE / AUCTION / suspension / ECIL event window) | boolean |
| 8 | 2 | `aggr_dev_s` | `(aggressor_share_s − POFP_aggr_mean) ÷ POFP_aggr_σ` | value in σ units |
| 9 | 2 | Aggressor round-trips | detect build-then-unwind cycles from signed aggressor-position path | `total_aggressor_round_trips`, `adverse_aggressor_reversals` |
| 10 | 2 | `AOB_reversal_rate` | `adverse_aggressor_reversals ÷ total_aggressor_round_trips` | ratio ∈ [0,1] |
| 11 | 2 | `n_anom_sessions` | count sessions where `aggr_dev_s > 2σ AND RT01 fires` | count |
| 12 | 2 | **AOB_level** | piecewise on `AOB_reversal_rate`, `aggr_dev_s`, `n_anom_sessions` (§2.1) | {0,1,2,3} |
| 13 | 2 | **BCI dimension 3** | threshold on `aggr_dev` + RT01 + benchmark-window events (§2.2) | {0,1,2,3} |
| 14 | 2 | BCI dimensions 1/2/4 + composite | `BCI = D1+D2+D3+D4` (D1/D2 = 0 without HQLD) | BCI 0–12; level (Follower…Primary Driver) |
| 15 | 2 | ECIL classification | `context_effect = classify(event, behaviour_window)`; `event_materiality` tier | {SUPPORTS / AMPLIFIES / CONTRADICTS / INSUFFICIENT}; materiality |
| 16 | 2 | Corroborative objects | IDS, ISS, IQ, CCT, SRS, NCS, HSL, PIR, RSA (§2.4–§2.9) | per-object scores/levels |
| 17 | 3 | **Aggressor Dominance** signal | `max(AOB_level, BCI_D3_level)` → fires ≥ 2 | {0,1,2,3}; fires? |
| 18 | 3 | **Sensitive Timing** signal | `IBE_sensitive_timing_flag` (step 7) with `ibe_event_type = INFORMATION_EVENT` | boolean |
| 19 | 3 | **Event Proximity** signal (TCS) | `event_materiality_weight × co_occurrence_weight × direction_alignment_score` | TCS ∈ [0,1] |
| 20 | 4 | **BC-17 classification** | AND of steps 17 + 18 + 19 (all three signals present) | BC-17 fires / does not fire |
| 21 | 4 | Final Concern | `Base Concern + Amplifiers − Suppressors` (ECIL `context_effect`, BCI level, HSL, PIR, RSA) | LOW / MEDIUM / HIGH / VERY HIGH |
| 22 | 5 | Risk Archetype resolution | RA-28 (Insider Dealing — Sensitive Timing) and/or RA-29 (Front-Running) | archetype(s) resolved |
