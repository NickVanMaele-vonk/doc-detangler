# Rulings on the M golden (`eval/golden/mcl.md`)

The human judgments behind `eval/golden/mcl.plan.yaml`'s `exceptions`
entries, written once here and pointed at from the plan — the same
division as the `U` and `S` goldens: the tool writes what it measured, a
human writes the rulings. Drafted for step 9.1 and approved by merging
the PR that carries them.

## §1 Version skew carried, not harmonised

The document is released as v21 yet carries a "What is new in v22"
change note; it declares "Applies to UCE v28" while the `S` source cites
"UCE v30" and the `U` golden renders v29 content; and the change note
cites "BIVM v28 §10b". All of it is the corpus's own state and all of it
is carried verbatim, per the ruling the `U` golden's §3 set: the
restructure reproduces claims, it does not harmonise version references.

## §2 Source defects carried verbatim (B-1 candidates)

The Layer 4 table cites "§XX.5.1 Doc 1" — a placeholder section number
that resolves nowhere — and the classification row of the document
reference table arrives OCR-damaged, its value glued to runs of dashes
(the runs are dropped as the rule-line furniture they are; the words are
kept). Damage inside claim text is carried verbatim, per the family-A
precedent; these are backlog B-1 source-correction candidates.

## §3 Head names Section 11 this extract does not contain

The source's title area carries the line "Section 11 — Three-Output
Integration — MTSAM Configuration": a banner for the v22 material this
shortened extract does not include, leaked into the title block. It is
not the document's title, so the golden does not keep it in the head. It
is placed in §3 Document control, directly after the v22 change note
that explains what Section 11 is — which also puts it after the
Three-Output Integration definition instead of before it, where it
raised a criterion-1 forward reference the verification harness caught.

## §4 Deviation: no generated navigation

Same deviation as the `U` golden's §7 and the `S` golden's §7: no
generated table of contents. The source's own section banners are
content and are kept (rendered in §3 Document control); nothing
navigational is invented beyond the authored section headings.
