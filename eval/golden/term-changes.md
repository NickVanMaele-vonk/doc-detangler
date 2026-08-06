# Term changes — UCE golden (step 5.2 stage B, criterion 8f / 8b)

**155 terms in scope** (reorder plan §3): 82 UCE-placed records plus the 73
glossary-placed records `U` uses. **Terms changed under 8b: 35** — each is a
definition given a marked site in `uce.md`. No promotion, no demotion, no
placement change, no record edited. 35 ≤ `param-max-terms-changed-per-PR`
(200).

Definition prose between `<!-- concept:<id>:start/end -->` markers is a
verbatim one-line copy of the record's `definition` field (whitespace
collapsed, the glossary's own rendering rule).

## Placed in "Terms defined in this document" (used in ≥ 2 target sections)

C9's placement rule recursed one level down (reorder plan §3), dependency
order, dependent after dependency (`persistence-gate` after
`domain-independence-filter` and after `participant-interaction`), ties in
first-use order. **A definition block's own text is a use** — corrected
2026-08-05, see `exceptions.md` §9:

| Record | Used in |
|---|---|
| `derisking-assessment` | §3 (principle 7), §4 (step 22) |
| `signal-integrity-summary` | §3 (principle 10), §6 (Parts index XIII) |
| `domain-independence-filter` | §3 (principle 11), §4 (step 5b) |
| `participant-interaction` | §4 (step 11b, DIF domains), and this section — inside `persistence-gate`'s definition block |
| `persistence-gate` | §3 (principle 11), §4 (step 11b) |
| `qa-validation` | §3 (principle 12), §6 (v24 entry) |
| `escalation-likelihood-score` | §4 (step 19), §6 (Parts index XIII, XIV) |

## Placed in one section (used there only, definition blocks counted)

| Section | Records |
|---|---|
| §3 | `ai-hard-controls`, `replayobject`, `minimum-necessary-escalation`, `contextual-suppression-gate`, `early-disposal-layer` |
| §4 | `enrichment-gate`, `dif-analytical-domains`, `collusion-assessment`, `six-indicators`, `behaviour-centric-reweighting`, `kill-switch`, `mwbr-metric`, `explanation-fragility-score`, `minimum-evidence-requirement`, `three-tier-escalation-modifier`, `behavioural-distinctiveness-score` |
| §5 | `human-intervention-checkpoint` |
| §6 | `pir-amplifier-only-rule`, `assessment-basis`, `price-impact-gate`, `behavioural-causality-principle`, `behavioural-causality-indicator`, `bci-dimensions-d1-d4`, `bci-levels`, `follower-rule`, `production-operations-governance`, `stor-reporting-intelligence-layer`, `ecil-supplemental-specification` |

Within a section, blocks sit at the top of the section in first-use /
dependency order (e.g. `assessment-basis` after `pir-amplifier-only-rule`,
`bci-dimensions-d1-d4` and `follower-rule` after
`behavioural-causality-indicator`).

## The 47 UCE-placed orphans — positioned, not defined

No definition block is written for them; **zero definitions were drafted**
(rationale in `exceptions.md` §1). Position = first use in the reading
order, by the section their `U` anchor sits in:

- **§6 (38)** — used only in the version history / Parts index:
  `amendment-uce-amd-bvr-001`, `amplifier-suppressor-assessment`,
  `behaviour-category-taxonomy`, `behavioural-concern-framework`,
  `behavioural-concern-layer`, `behavioural-scenario-library`\*,
  `campaign-role`, `contextual-convergence-score`, `degraded-mode-doctrine`,
  `detection-signal-taxonomy`, `eight-dimension-assessment`,
  `event-cascade-object`, `event-driven-information-behaviour`,
  `evidence-confidence`, `false-negative-governance`,
  `gate-failure-cause-distinction`, `generic-alert-primitives`,
  `holistic-output-schema`, `nfil`, `nim-mar`, `no-data-no-risk-principle`,
  `os-bc`, `os-u-disclosure-requirements`, `qa-mar`, `raaf`, `rcs-mar`,
  `regime-transition-intelligence`, `rsaengine`, `rsn-trigger-fields`,
  `sdail`, `six-level-progressive-deployment-model`, `ssf-df`,
  `statistical-governance-and-calibration-assurance`, `summary-principle`,
  `three-level-review`, `three-level-suspicion-taxonomy`,
  `volume-materiality-index`, `xs-mar`.
  \* `behavioural-scenario-library` is also used in §3 (principle 12) — an
  undefined term used in two sections; see `exceptions.md` §2.
- **§4 (5)** — `attribution-confidence`, `auto-close`,
  `collusion-override-path`, `no-benign-explanation-challenge`,
  `outcome-persistence-layer`.
- **§3 (2)** — `level-0`, `medium-structured-review`.
- **§5 (2)** — `fp-code`, `human-review-required`.

## The 73 glossary-placed terms

Projected into `glossary-slice.md` from `glossary.md`, verbatim, same
topological order: 36 defined, 37 rendered with the "not defined in the
corpus" note. No entry text was changed.

## The 13 `notes` staging-post clauses — resolved: none belongs to `U`

The open item in reorder-plan §6, measured: all 13 records holding narrowed
corpus wording in `notes` (`anonymous-quote-driven-market-structure`,
`classification`, `close-window`, `cwps-intra`, `gate`,
`identity-driven-coordination`, `intent-score`, `liquidity-driven-reaction`,
`mtsam-l-data-limitation-register`, `mwbr-score-levels`,
`otc-bilateral-trading`, `rd03`, `rt01`) are **glossary-placed** — none is
UCE-placed, so no clause lands in `uce.md` prose. They land beside their
glossary definitions when the glossary's own body work happens, and beside
`S`/`M` definitions in those goldens where applicable. `uce.md` owes
nothing under criterion 4 on this account.
