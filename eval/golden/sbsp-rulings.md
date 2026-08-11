# Rulings on the S golden (`eval/golden/sbsp.md`)

The human judgments behind `eval/golden/sbsp.plan.yaml`'s `exceptions`
entries — one section per entry, written once here and pointed at from the
plan, following the division ruled 2026-08-05: the tool writes what it
measured, a human writes the rulings. Drafted for step 9.1 and approved by
merging the PR that carries them.

## §1 Version skew carried, not harmonised

The source cites "§VI-A.5.3 UCE v30" (amendment SBSP-AMD-BVR-001) while the
`U` golden in this set renders UCE v29 content, and Document 3 is cited at
v20 while the `M` source in `samples/` carries v21. The skew is the
corpus's own state, and the same ruling as the `U` golden's §3 applies: the
restructure reproduces claims, it does not harmonise version references.
Harmonisation would be a meaning change, which is never authorised.

## §2 Amendment texts kept at their anchor points

The source carries two insertions marked SBSP-AMD-BVR-001: the ECIL
amplification auto-validation threshold (source §A.4.3.1) and the
mandatory audit language for BVR closures (source §A.6.1). Both are
normative rules, and both stay in the analytical sections they amend —
rendered as `### A.4.3.1` and `### A.6.1` — rather than being gathered
into a change log. This is the same ruling as the `U` golden's §4:
normative text is not relocated to document control just because it
arrived as an amendment.

## §3 Source defects carried verbatim (B-1 candidates)

The CICI blocks (source §A.4.3 and below) carry mojibake — `â` sequences
where em-dashes and quotation marks were mangled — and the archetype table
carries a stray cross-reference "§A.4.0" that resolves nowhere. Damage
inside claim text is carried verbatim, per the family-A precedent the `U`
golden set (its §5): a repair that changes characters is a meaning change
the tool may not make. These are backlog B-1 source-correction candidates.

## §4 Duplicate A.4.3.1 numbering resolved in authored headings

The source numbers two different subsections A.4.3.1: the
SBSP-AMD-BVR-001 amendment text and the "CICI Data Inputs and Three-Level
Framework" material. Headings are authored scaffolding, so the golden
renumbers deterministically: the amendment keeps `A.4.3.1` (its number is
part of the amendment's own citation), CICI data inputs becomes
`A.4.3.2`, and the three-position data types (source-numbered A.4.3.2)
becomes `A.4.3.3`. Body prose citing "§A.4.3.1" is untouched.

## §5 Misfiled CICI material restored to Section A

In the source, the whole A.4.3 CICI subsection sits *after* the SECTION B
banner — Section A content stranded on the wrong side of a section
boundary, the same interleaving defect the `U` golden's §6 recorded. The
plan moves it back under the Section A material it belongs to. No words
change; only position does, which is what a reorder plan is for.

## §6 Interleaved BVR grouping text carried inside the SB-12 row

Inside the 35-archetype grid table, the SB-12 row's cells carry several
paragraphs of §D.4 BVR grouping material (D.4.1, D.4.2 — another
SBSP-AMD-BVR-001 insertion) that was OCR-merged into the table. Splitting
one source block into several output units is not a transform the plan
schema declares, and inventing one for a single occurrence is not
justified: the text is carried verbatim inside the row where the source
holds it, rendered by the `grid-list` hint. A future claim-split override
(`registers/claim-splits.yaml`) is the designed home for dividing it.

## §7 Deviation: no generated navigation

Same deviation as the `U` golden's §7: the golden carries no generated
table of contents. The source's own "Section Content" index and its
SECTION banners are content and are kept (rendered in §4 Document
control); nothing navigational is invented beyond the authored section
headings themselves.
