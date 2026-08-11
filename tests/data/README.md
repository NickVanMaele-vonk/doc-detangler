# Frozen test fixtures — a known "pre" and "post" detangle set

This directory holds one complete, known-good detangle run, frozen in time:

- the **"pre" side** — the source documents as they went into the tool
  (`samples/`), together with everything the run derived from them: the 359
  concept records, the registers, the glossary, the concept graph, and the
  approved reorder plans;
- the **"post" side** — the three restructured output documents
  (`eval/golden/uce.md`, `sbsp.md`, `mcl.md`) that a human reviewed and
  approved as correct.

Because both sides are known and the pair was verified once by a human, any
future change — to the tool or to the test suite itself — can be checked
against it: run the changed tool on the known "pre", and it must still
produce exactly the known "post". `restructure` must rebuild the goldens
byte for byte, `verify` must still catch the errors the tests deliberately
seed into them, and the pinned source document must still decompose into the
same claim counts. If any of that stops holding, the change broke the tool.

That is this directory's only job. It has **no relationship to the live
corpus**: the tool never compares these files against the documents the
project currently works on, and a new campaign starts from zero records and
mints its own hashes. The tests point here explicitly (this directory
carries its own `detangle.toml` and acts as the tests' project root); the
live commands resolve the real project root and never look here.

The data is a byte-exact snapshot of the first detangle campaign (the
shortened-blueprint corpus), taken 2026-08-11 when the project moved on to a
new campaign on the full-length blueprints. Byte-exact matters: the records
anchor to content hashes (`para_hash`, git blob ids — e.g. the pinned `U`
blob `4cae72dece7638c1ddec8206a3c6a24610196de0`), and the expected test
numbers are properties of these exact bytes.

Consequences:

- **Never edit anything here.** A single changed byte breaks the hashes and
  the known answers, and the pair stops being ground truth. There is nothing
  to update — when a new campaign approves its own golden, *add* that as a
  second pre/post fixture; do not touch this one.
- Provenance: the full history of how this data was built lives in the
  original GitHub repository (`NickVanMaele-vonk/doc-detangler`, kept
  private) — its PR numbers are what the ADRs and test docstrings cite.
