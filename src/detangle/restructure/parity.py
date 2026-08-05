"""Criterion 5 as a check the command runs: the verbatim-token parity diff.

The rubric's mechanical half — every word of the source is still in the
output, and the output invents none — was verified for the golden by a
scratchpad script. ADR-002 Decision 3 moves it into ``detangle restructure``,
where it runs on every execution.

The comparison is a multiset diff of word tokens, and it is exact because
both sides are known rather than guessed:

- the **source side** is every block the plan assigns, after the plan's own
  declared cleaning (inline removals and whitespace-only repairs). Blocks
  declared noise are not on this side at all — that drop is the plan's
  decision, reported but not re-litigated here.
- the **output side** is every part the renderer tagged ``source``.
  Authored scaffolding — the overview, definition blocks copied from
  records, headings, table furniture — is excluded, because its words are
  not claiming to come from the document.
- what the renderer discarded on the way (a repeated table header, the
  ``PART`` banner word) is subtracted only because it was recorded as a
  ``Drop``, verbatim and with a reason.

Anything left over is a ``token-parity`` finding. Words missing from the
output are the serious direction — a claim lost its wording, or lost its
force (criterion 5 counts modality, operators and thresholds as words like
any other). Words present in the output but not in the source are the
fabrication direction. Neither is repaired: the disposition is a plan edit
or a renderer fix, and both are human decisions.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from ..findings import Finding, error
from .execute import SOURCE, Render, cleaner, parse_blocks
from .plan import Plan
from .tokens import tokens

#: See ``records.checks.CHECKS`` for why every module declares its slugs.
CHECKS = frozenset({"token-parity"})

#: Drop reasons that account for their own words. Each is a declared
#: transform whose evidence the renderer can show: a header the output keeps
#: elsewhere, the header row of a table the plan asked to render as a headed
#: list, the banner word that becomes a column head. Every other reason —
#: ``dropped-table-header`` today — explains nothing, so its words stay in
#: the missing column and raise a finding.
EXPLAINED = frozenset(
    {"repeated-table-header", "history-table-header", "part-row-label"}
)

#: How many distinct tokens a finding lists before it says "and N more".
SAMPLE = 12


@dataclass
class Parity:
    """One run's token accounting, kept whole so the report can show it."""

    expected: Counter = field(default_factory=Counter)
    actual: Counter = field(default_factory=Counter)
    dropped: Counter = field(default_factory=Counter)
    noise: Counter = field(default_factory=Counter)
    removed: Counter = field(default_factory=Counter)
    added: Counter = field(default_factory=Counter)
    missing: Counter = field(default_factory=Counter)
    extra: Counter = field(default_factory=Counter)
    drops_by_reason: dict[str, Counter] = field(default_factory=dict)

    @property
    def clean(self) -> bool:
        return not self.missing and not self.extra


def _sample(counter: Counter) -> str:
    items = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
    shown = ", ".join(
        f"{tok!r}" + (f"×{n}" if n > 1 else "") for tok, n in items[:SAMPLE]
    )
    if len(items) > SAMPLE:
        shown += f", and {len(items) - SAMPLE} more"
    return shown


def measure(plan: Plan, source: str, rendered: Render) -> Parity:
    """Account for every word, source side and output side."""
    parsed = {b.hash: b for b in parse_blocks(source)}
    clean = cleaner(plan)
    out = Parity()

    for entry in plan.assignments:
        for h in plan.blocks_of(entry):
            block = parsed.get(h)
            if block is None:
                continue  # a bad hash is plan-block-unknown's finding, not ours
            raw, cleaned = tokens(block.raw), tokens(clean(block.raw, h))
            out.expected.update(cleaned)
            out.removed.update(raw - cleaned)
            out.added.update(cleaned - raw)
    for entry in plan.noise:
        block = parsed.get(entry.get("block", ""))
        if block is not None:
            out.noise.update(tokens(block.raw))

    for part in rendered.parts:
        if part.origin == SOURCE:
            out.actual.update(tokens(part.text))
    for drop in rendered.drops:
        counted = tokens(drop.text)
        if drop.reason in EXPLAINED:
            out.dropped.update(counted)
        out.drops_by_reason.setdefault(drop.reason, Counter()).update(counted)

    out.missing = out.expected - out.dropped - out.actual
    out.extra = out.actual - out.expected
    return out


def check(parity: Parity, rel: str) -> list[Finding]:
    """Findings for whatever the accounting could not explain."""
    out: list[Finding] = []
    if parity.missing:
        out.append(
            error(
                "token-parity",
                rel,
                f"{sum(parity.missing.values())} source word(s) are in no "
                f"output section and in no declared drop: {_sample(parity.missing)}"
                " — either the plan has not decided their fate (declare them "
                "noise, or assign the block) or the renderer lost them "
                "(criterion 5)",
            )
        )
    if parity.extra:
        out.append(
            error(
                "token-parity",
                rel,
                f"{sum(parity.extra.values())} word(s) in source-attributed "
                f"output are not in the source: {_sample(parity.extra)} — "
                "output claiming source provenance must carry source wording "
                "(C2); authored text belongs in a marked addition",
            )
        )
    return out


__all__ = ["CHECKS", "Parity", "check", "measure"]
