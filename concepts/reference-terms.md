# Reference terms — regulator- and externally-owned

Per **criterion 3** (`plan/definition-of-done.md`): externally defined terms
owned by a standards body or regulator get a **references entry pointing at
the authoritative source, not a glossary definition**. This file is that
references list. It is **canonical and hand-authored** (not a generated
view); the reader-facing references section of the output set will be
derived from it.

Populated at step 3.3 from `work/term-extraction/candidate-terms-merged.md`
§2. Nick's review decision on §2 (2026-07-29): *"keep all for now — revisit
usefulness as design specifications evolve."* Location `reference-terms.md`
per Nick's ruling 2026-07-29.

"Used in" is measured mechanically against the shortened corpus at the blob
versions current on this branch; (A) and (P) are informational only (Nick's
rulings 2026-07-22 / 2026-07-26). Expansions marked "(corpus: …)" are taken
verbatim from the named source; all others are supplied from the owning
authority's own terminology and are **not** corpus text.

| Term | Full name / expansion | Owner / authoritative source | Used in | Notes |
|---|---|---|---|---|
| MAR | Market Abuse Regulation — Regulation (EU) No 596/2014 (corpus: (P) §0.1) | European Union; ESMA guidance | U, S, M, (A), (P) | Article-level citations (MAR Article 12, Article 16) appear throughout; criterion 5 protects them verbatim wherever reproduced. |
| FSMA | Financial Services and Markets Authority, Belgium (corpus: MCL 1.1) | Kingdom of Belgium | U, S, M, (A) | Expanded only in M (candidate-list note). MCL SECTION 0 is built around FSMA engagement; the *engagement architecture* is project content, the authority itself is external. |
| ESMA | European Securities and Markets Authority (corpus gloss: (P) §0.1 "EU markets regulator; MAR guidance") | European Union | M, (A), (P) | |
| FIRDS | Financial Instruments Reference Data System | ESMA | (A) only | |
| FITRS | Financial Instruments Transparency System | ESMA | (A) only | |
| ECB | European Central Bank (corpus gloss: (P) §0.1 "primary information-event source for OLO prices") | European Union | S, M, (A), (P) | Named programmes APP, PEPP, TLTRO appear in M only; they stay under this entry, not as separate terms. |
| Belgian Debt Agency (ADA) | Agence de la Dette (Belgian Debt Agency) (corpus: (P) §0.1) | Kingdom of Belgium | S, M, (A), (P) | **Borderline per §2:** carries heavy project-specific rules (primary-dealer authorisation, auction calendar feeding ECIL, dominance population). Reference entry here; project usage lives in the concept records that cite it (e.g. `primary-dealer`, `dominance-threshold-pct`). |
| EMIR | European Market Infrastructure Regulation | European Union | S only | |
| LEI | Legal Entity Identifier (corpus: (P) §1.2) | ISO 17442 / GLEIF | S, M, (P) | M Layer 3 uses LEI lookup for RRF enrichment — see `regulatory-risk-factor`. |
| STOR | Suspicious Transaction and Order Report (MAR Article 16) | ESMA / MAR | U, S, M, (A), (P) | **Borderline per §2:** heavy project-specific rules (STOR decision architecture, STOR narrative input template, Historical STOR Linkage). Reference entry here; project usage lives in the records and documents that cite it. |
| MiFID II | Markets in Financial Instruments Directive II — Directive 2014/65/EU | European Union | — (via (A)-only concepts) | Never verbatim in the corpus; enters via the (A)-only concepts LIS, SSTI, and the transparency regime. |
| LIS | Large in Scale | ESMA / MiFID II transparency regime | (A) only | |
| SSTI | Size Specific to the Instrument | ESMA / MiFID II transparency regime | (A) only | |
| RTS23 | Regulatory Technical Standard 23 — instrument reference data reporting | ESMA / MiFID II | (A) only | Surface form "RTS23" as in corpus. |
| RTS24 | Regulatory Technical Standard 24 — order record keeping | ESMA / MiFID II | (A) only | |
| GDPR | General Data Protection Regulation — Regulation (EU) 2016/679 | European Union | M, (A) | |
| EU AI Act | Regulation (EU) 2024/1689 on artificial intelligence | European Union | U only | Cited in U's Doc 7 governance row. |
| UBO | Ultimate Beneficial Owner (corpus: (P) §0.1 "ownership link (feeds SRS)") | EU AML framework | M, (A), (P) | Feeds SRS — see `structural-relationship-score`. |
| DMO | Debt Management Office | national governments (generic) | (A) only | |
| NCA | National Competent Authority | ESMA framework | instances only: M | Bare "NCA" never appears in U/S/M; the corpus names instances — CONSOB, AMF, BaFin, FCA (all M). Instances stay under this entry. |
| Belgian Treasury Certificate | — | Kingdom of Belgium / ADA | M only | "Belgian Treasury Certificates (secondary)" in MCL 1.1 instrument scope. |
| ISIN | International Securities Identification Number (corpus: (P) §1.2) | ISO 6166 | M, (A), (P) | |
| quote stuffing | — (industry term) | market-abuse practitioner literature | S only | Industry-owned rather than regulator-owned; routed here per §2. |
| Eurex | — (derivatives exchange) | Deutsche Börse Group | S, M, (A) | External industry term (Nick's ruling 2026-07-29; formerly a §1f glossary record, removed). Its published public market data (Bund futures settlement price, volume, open interest, intraday bars) feeds CICI/ECIL enrichment — see `cross-instrument-context-intelligence`. |
| OLO | Obligation Linéaire / Lineaire Obligatie — Belgian linear government bond (corpus: (P) §0.1) | Kingdom of Belgium / ADA | S, M, (A rel.), (P) | External industry term (Nick's ruling 2026-07-29; formerly a §1f glossary record, removed) — consistent with criterion 3's own example list. Never expanded in U/S/M; the expansion is (P)-only. |
| HHI | Herfindahl–Hirschman Index (corpus gloss: (P) §0.1 "concentration measure, 0–10,000 scale") | economics literature / antitrust practice | S (as `bt06_counterparty_hhi`), (P) | Sourced from §7b (P) per Nick's ruling 2026-07-28; externally owned, routed here rather than into §1. |
| market manipulation | — (MAR legal concept) | European Union / MAR | U only | The engine's adjudication target: "market manipulation or insider dealing under MAR Article 12" (U I.1). From the §3 bulk (author-as-is ruling 2026-07-29); regulator-owned per the extraction, so routed here per criterion 3 despite the single-document count. |
| insider dealing | — (MAR legal concept) | European Union / MAR | U only | Adjudication target alongside market manipulation (U I.1). The full UCE has a Part XI on insider dealing, absent from the shortened version — whose Part-contents table reuses "XI" for Deployment Maturity (numbering conflict; surfaced, not fixed). Routed here per criterion 3, same basis as the row above. |
| BTP | Buono del Tesoro Poliennale — Italian multi-year government bond | Republic of Italy / Ministry of Economy and Finance | S only | Corpus surface "BTPs", once, in the S front-matter scope sentence: "OLOs, OATs, Bunds, BTPs, Gilts, and equivalent sovereign debt instruments". Named in criterion 3's own example list as external; routed here from the §3 bulk (Nick's ruling 2026-07-30). |
| Gilt | — (UK government bond; from "gilt-edged security") | United Kingdom / HM Treasury, UK Debt Management Office | S only | Corpus surface "Gilts", once, same scope sentence as BTP. Externally owned by analogy with BTP and OLO — analogy confirmed by Nick's ruling 2026-07-30. |

## Resolved tensions

1. **Eurex** and **OLO** — each briefly held both a §1f glossary record and
   external-ownership status. **Resolved by Nick's ruling 2026-07-29:
   both are external industry terms, not project-specific** — reference
   entries above; the concept records were removed in the same PR. (BTP,
   the other instrument example in criterion 3, does not occur in the
   §1/§2 lists.)
