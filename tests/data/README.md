# Frozen test fixtures — not the corpus

This directory is a byte-exact snapshot of the first detangle campaign's data
(the shortened-blueprint corpus, its 359 concept records, registers, glossary,
graph, and the three approved goldens), taken 2026-08-11 when the project
prepared to leave the shortened corpus behind and start a new campaign on the
full-length blueprints.

Its only job is to give the test suite known inputs with known-correct
answers: `restructure` must reproduce the approved goldens byte for byte,
`verify` must catch the seeded errors, the pinned `U` blob
(`4cae72dece7638c1ddec8206a3c6a24610196de0`) must decompose to the pinned
claim counts. The tests prove the **tool**; the live corpus is checked by the
`detangle` commands themselves, in CI.

Consequences:

- **Never edit anything here.** A byte change breaks the pinned blob ids and
  `para_hash` values the tests assert on. There is nothing to update — when a
  new campaign approves a golden, *add* it as a new fixture; do not touch
  these.
- This snapshot has no relationship to the live `[documents]` registry in the
  project's `detangle.toml`. It carries its own `detangle.toml`, and tests
  point at this directory as their root.
- Provenance: the full history of how this data was built lives in the
  original GitHub repository (`NickVanMaele-vonk/doc-detangler`, kept
  private) — its PR numbers are what the ADRs and test docstrings cite.
