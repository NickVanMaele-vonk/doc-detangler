"""The generated 8f self-report (ADR-002 Decision 3).

A restructure run has to account for itself: where every source block went,
what the run measures, and what a reviewer is being asked to look at. The
golden's hand-written ``move-map.md``, ``counts.md`` and ``exceptions.md``
are the format spec; these are their machine-written counterparts.

The division is the one Nick ruled on 2026-08-05. **The tool writes what it
measured** — block moves, rejoins, declared noise, category tallies, the
criterion-5 residue, the undefined-term roster, forward references. **A
human writes the rulings** — the version skew stands rather than being
harmonised, the change-log rules stay put, the OCR damage is carried
verbatim. Those sentences are judgment, and Decision 1C keeps judgment out
of the tool.

The tool still needs to *know about* them, for one reason only: the 8c rule
caps how many PR comments one restructure may raise, and a comment it cannot
see is one it would count wrong. So the plan carries a title and a pointer
per ruling — five words, not the paragraph — and the report names them and
says where to read them. The wording stays in one place.

Byte equality with the golden is not the bar and never was: Decision 4
compares the two per criterion. What must match is the accounting.
"""

from __future__ import annotations

import re
import textwrap
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from ..findings import Finding, error
from ..records.load import Record
from .execute import parse_blocks
from .parity import EXPLAINED, Parity
from .plan import Plan

# The function, not the module: `_forward_references` binds a loop variable
# named `position`, which would shadow a module import.
from .position import cluster_body

#: See ``records.checks.CHECKS`` for why every module declares its slugs.
CHECKS = frozenset({"comment-budget", "report-drift", "report-missing"})

MOVE_MAP = "move-map.md"
COUNTS = "counts.md"
EXCEPTIONS = "exceptions.md"
#: Fixed names, so a report directory is comparable to the golden's by name.
ARTIFACTS = (MOVE_MAP, COUNTS, EXCEPTIONS)

WS = re.compile(r"\s+")
PREVIEW = 64
#: Noise is quoted at length rather than previewed: the point of the
#: inventory is that the drop is visible, and a truncated page footer is not.
NOISE_PREVIEW = 160


@dataclass(frozen=True)
class Cluster:
    """One PR comment (8d), whether this run measured it or a human ruled it.

    ``where`` is empty for a measured cluster — the body below it *is* the
    statement. For a declared one it points at the file and section holding
    the reasoning, which the tool deliberately does not reproduce.
    """

    title: str
    body: str
    where: str = ""


@dataclass
class Report:
    files: dict[str, str] = field(default_factory=dict)
    clusters: list[Cluster] = field(default_factory=list)


# -- small formatting helpers ----------------------------------------------


def _flat(text: str) -> str:
    return WS.sub(" ", text).strip()


def _cut(text: str, width: int = PREVIEW) -> str:
    flat = _flat(text)
    return flat if len(flat) <= width else flat[:width].rstrip() + "…"


def _cell(text: str) -> str:
    """One cell, one line: a pipe would end the column and a newline the row."""
    return _flat(text).replace("|", "\\|")


def _short(block_hash: str) -> str:
    return block_hash.removeprefix("sha256:")[:8]


def _wrap(text: str) -> str:
    """Wrap prose to a readable width, one paragraph at a time.

    ``break_on_hyphens=False`` because record ids are hyphenated and a
    reviewer copying ``behavioural-drift-score`` out of a broken line gets
    half an id.
    """
    out = []
    for para in text.split("\n\n"):
        if para.lstrip().startswith("-"):
            out.append(para)  # a bullet list is already laid out
            continue
        out.append(
            "\n".join(
                textwrap.wrap(
                    _flat(para),
                    width=76,
                    break_on_hyphens=False,
                    break_long_words=False,
                )
            )
        )
    return "\n\n".join(out)


def _listing(items: list[str]) -> str:
    return _wrap(", ".join(items)) if items else "none"


def _table(header: list[str], rows: list[list[str]]) -> str:
    """Always preceded by a blank line — markdown will not start a table
    directly under a paragraph."""
    if not rows:
        return "\n_none_\n"
    out = ["", "| " + " | ".join(header) + " |"]
    out.append("|" + "|".join(["---"] * len(header)) + "|")
    out.extend("| " + " | ".join(_cell(c) for c in row) + " |" for row in rows)
    return "\n".join(out) + "\n"


def _sample(counter: Counter, limit: int = 12) -> str:
    items = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
    shown = ", ".join(f"`{t}`" + (f"×{n}" if n > 1 else "") for t, n in items[:limit])
    if len(items) > limit:
        shown += f", and {len(items) - limit} more"
    return shown or "—"


# -- what the run did to each block ----------------------------------------


def _derivations(plan: Plan, entry: dict, hashes: list[str]) -> list[str]:
    """The transforms that make an assignment Category B rather than A.

    Formatting applied to everything — pipe-table rendering, pandoc escape
    removal — is not listed here; it is stated once in the move-map, as the
    golden states it, rather than on every row.
    """
    touched = {e["block"] for e in plan.inline_removals} | {
        e["block"] for e in plan.repairs
    }
    marks = []
    if len(hashes) > 1:
        marks.append(f"rejoined from {len(hashes)} fragments")
    if entry.get("render"):
        marks.append(f"re-rendered as {entry['render']}")
    if any(h in touched for h in hashes):
        marks.append("declared repair/removal applied")
    return marks


def _category(marks: list[str]) -> str:
    return "A — moved verbatim" if not marks else "A — moved; B — " + ", ".join(marks)


def _definition_order(plan: Plan) -> list[str]:
    """Record ids in the order their definition blocks appear in the output."""
    out = []
    for section in plan.sections:
        out.extend(
            str(d["record"])
            for d in plan.definitions
            if d.get("section") == section.id
        )
    return out


def _forward_references(plan: Plan, records: list[Record]) -> list[tuple[str, str]]:
    """Definitions leaning on a term this document defines further down.

    Criterion 1's formal check, projected over the order the plan produces:
    a reader meeting a definition must already have met everything it uses.
    """
    order = {rid: i for i, rid in enumerate(_definition_order(plan))}
    by_id = {r.id: r for r in records}
    out = []
    for rid, position in order.items():
        record = by_id.get(rid)
        if record is None:
            continue
        for dep in record.get_list("depends_on"):
            if order.get(str(dep), -1) > position:
                out.append((rid, str(dep)))
    return sorted(out)


def _undefined(plan: Plan, records: list[Record], placement: str):
    """Terms this document uses that nothing defines, split by why.

    Most carry ``flags: [orphan]`` — the measure of how convoluted the source
    is. A few are undefined by ruling instead: where a business object and
    the software producing it share a definition site, only the business term
    is defined and the software record deliberately carries no orphan flag
    (the IBE/IBEB ruling, 2026-07-30). Conflating the two would overstate the
    orphan count, so they are counted apart.
    """
    orphans, by_ruling = [], []
    for record in records:
        if record.data.get("definition"):
            continue
        placed_here = record.data.get("placement") == placement
        used_here = plan.doc in record.get_list("used_in")
        if not (placed_here or used_here):
            continue
        target = orphans if "orphan" in record.get_list("flags") else by_ruling
        target.append(record.id)
    return sorted(orphans), sorted(by_ruling)


# -- the three artifacts ----------------------------------------------------


def _move_map(plan: Plan, source: str, parity: Parity, blob: str | None) -> str:
    parsed = {b.hash: b for b in parse_blocks(source)}
    by_section = {s.id: s for s in plan.sections}

    rows, rejoins = [], []
    for entry in plan.assignments:
        hashes = plan.blocks_of(entry)
        if not hashes:
            continue
        marks = _derivations(plan, entry, hashes)
        label = str(entry.get("label") or f"`{_short(hashes[0])}`")
        if len(hashes) > 1:
            label += f" +{len(hashes) - 1}"
        first = parsed.get(hashes[0])
        section = by_section.get(str(entry.get("section")))
        rows.append(
            [
                label,
                _cut(first.raw if first else ""),
                section.title if section else str(entry.get("section")),
                _category(marks),
            ]
        )
        if len(hashes) > 1:
            rejoins.append(
                [
                    label,
                    " + ".join(
                        f"`{_short(h)}` {_cut(parsed[h].raw, 40)!r}"
                        for h in hashes
                        if h in parsed
                    ),
                ]
            )

    hints = Counter(
        str(a["render"]) for a in plan.assignments if a.get("render")
    )
    noise_rows = [
        [
            f"`{_short(str(n.get('block')))}`",
            str(n.get("kind", "")),
            _cut(parsed[n["block"]].raw, NOISE_PREVIEW)
            if n.get("block") in parsed
            else "",
        ]
        for n in plan.noise
    ]
    drop_rows = [
        [
            reason,
            "explained" if reason in EXPLAINED else "**unexplained**",
            str(sum(counted.values())),
            _sample(counted, 8),
        ]
        for reason, counted in sorted(parity.drops_by_reason.items())
    ]

    parts = [
        f"# Move-map — {plan.doc} (criterion 8f, generated)\n\n",
        _wrap(
            f"Every source block of `{plan.doc}`"
            + (f" (blob `{blob}`)" if blob else "")
            + ", where it went, and what was done to it on the way. Generated "
            f"by `detangle restructure` from `{plan.rel}`; do not hand-edit."
        )
        + "\n",
        "\n## Block moves\n",
        _table(["Source", "Content", "Target section", "Category"], rows),
        "\n## Rejoined page-split fragments\n\n",
        "Each row below is one output unit assembled from several source "
        "blocks.\n",
        _table(["Unit", "Fragments, in order"], rejoins),
        "\n## Transforms applied throughout\n\n",
        "Claim-preserving and applied to every unit, so they are stated once "
        "rather\nthan on every row:\n\n",
        "- Pandoc simple/multiline tables re-rendered as markdown pipe "
        "tables; cell\n  text verbatim.\n",
        "- Pandoc escape backslashes removed — markdown syntax, not content.\n",
    ]
    for hint, count in sorted(hints.items()):
        parts.append(f"- Render hint `{hint}`: {count} assignment(s).\n")
    parts += [
        f"- Declared repairs: {len(plan.repairs)} (whitespace-only, so no word "
        "changes).\n",
        f"- Declared inline removals: {len(plan.inline_removals)}.\n",
        "\n## Dropped as declared noise\n\n",
        "The plan's decision, quoted so it is visible rather than silent "
        "(criterion 4).\n",
        _table(["Block", "Kind", "Text"], noise_rows),
        "\n## Discarded by the renderer\n\n",
        "Text the renderer removed on its own. A reason marked *explained* "
        "accounts\nfor its own words to the criterion-5 check; anything else "
        "is a finding.\n",
        _table(["Reason", "Standing", "Words", "Sample"], drop_rows),
        "\n## Section IDs (C12 two-layer addressing)\n",
        _table(
            ["Section", "ID", "Kind"],
            [[s.title or "—", f"`{s.id}`", s.kind] for s in plan.sections],
        ),
    ]
    return "".join(parts)


def _counts(plan: Plan, text: str, parity: Parity, clusters: int) -> str:
    derived = [
        a
        for a in plan.assignments
        if _derivations(plan, a, plan.blocks_of(a))
    ]
    verbatim = len(plan.assignments) - len(derived)
    addition_words = sum(len(str(a.get("text", "")).split()) for a in plan.additions)

    explained = Counter()
    unexplained = Counter()
    for reason, counted in parity.drops_by_reason.items():
        (explained if reason in EXPLAINED else unexplained).update(counted)

    return "".join(
        [
            f"# Counts — {plan.doc} (criterion 8f, generated)\n\n",
            "Measured from the run that produced the document, not predicted.\n"
            f"Generated by `detangle restructure` from `{plan.rel}`; do not "
            "hand-edit.\n",
            "\n## The document\n\n",
            "**Sections are counted as a reader meets them** (Nick, "
            "2026-08-05): a\nsection with a heading. The `head` identity "
            "block renders headless and\ncarries no `sec:` marker, so it is "
            "not counted here — every plan section,\nheaded or not, is "
            "listed in the Section IDs table of the move-map.\n",
            _table(
                ["Measure", "Count"],
                [
                    ["Sections", str(sum(1 for s in plan.sections
                                         if s.kind != "head"))],
                    ["Bytes", str(len(text.encode("utf-8")))],
                    ["Definition blocks", str(len(plan.definitions))],
                    ["Category C additions", str(len(plan.additions))],
                    ["— words in them", str(addition_words)],
                ],
            ),
            "\n## Units executed\n",
            _table(
                ["Measure", "Count"],
                [
                    ["Assignments", str(len(plan.assignments))],
                    ["— of them rejoins of split fragments",
                     str(sum(1 for a in plan.assignments if "fragments" in a))],
                    ["Declared noise blocks", str(len(plan.noise))],
                    ["Declared repairs", str(len(plan.repairs))],
                    ["Declared inline removals", str(len(plan.inline_removals))],
                ],
            ),
            "\n## Content categories (criterion 7)\n\n",
            "Counted in plan assignments, not in the golden's source groups — "
            "the two\ncarve the same document differently, so the numbers are "
            "not comparable\nrow for row.\n",
            _table(
                ["Category", "Instances"],
                [
                    ["A — moved, verbatim", f"{verbatim} assignments"],
                    [
                        "B — derived",
                        f"{len(derived)} transformed assignments + "
                        f"{len(plan.definitions)} definition blocks "
                        "(record copies, cross-file `src`)",
                    ],
                    ["C — added", f"{len(plan.additions)} (marked in the output)"],
                    [
                        "Omissions",
                        "0 — every source block is decided (`plan-incomplete`) "
                        "and every word\naccounted for below"
                        if parity.clean
                        else f"{sum(parity.missing.values())} unaccounted "
                        "words — see below",
                    ],
                ],
            ),
            "\n## Criterion-5 token parity (mechanical)\n\n",
            "Multiset diff of word tokens. The source side is every assigned "
            "block after\nthe plan's declared cleaning; the output side is "
            "every part the renderer\ntagged as carrying source words — "
            "authored scaffolding is excluded from both.\n",
            _table(
                ["Measure", "Words"],
                [
                    ["Source words expected", str(sum(parity.expected.values()))],
                    ["In source-attributed output", str(sum(parity.actual.values()))],
                    ["Explained renderer drops", str(sum(explained.values()))],
                    [
                        "Declared noise (never expected)",
                        str(sum(parity.noise.values())),
                    ],
                    ["Removed by declared removals", str(sum(parity.removed.values()))],
                    ["Added by declared repairs", str(sum(parity.added.values()))],
                    ["**Missing — in no output section**",
                     f"**{sum(parity.missing.values())}**"],
                    ["**Extra — in no source block**",
                     f"**{sum(parity.extra.values())}**"],
                ],
            ),
            (
                "\nNo unclassified difference in either direction.\n"
                if parity.clean
                else f"\nMissing: {_sample(parity.missing)}\n\n"
                f"Extra: {_sample(parity.extra)}\n"
            ),
            (
                f"\nUnexplained renderer drops: {_sample(unexplained)}\n"
                if unexplained
                else ""
            ),
            "\n## Review load (8c)\n\n",
            f"{clusters} PR comment cluster(s) — itemised in `{EXCEPTIONS}`.\n",
        ]
    )


def _exceptions(plan: Plan, clusters: list[Cluster], limit) -> str:
    parts = [
        f"# Exceptions — {plan.doc} (criterion 8f, generated)\n",
        "What would become PR comments in a real run, aggregated per cluster "
        "(8d).\nNothing here is fixed silently.\n",
        "\nClusters this run **measured** are stated in full below. Clusters a "
        "human\n**ruled** are named, with a pointer to where the reasoning is "
        "written — the\ntool counts them so the budget is honest, and does not "
        "reprint them, so the\nwording lives in one place.\n",
    ]
    for i, cluster in enumerate(clusters, start=1):
        parts.append(f"\n## {i}. {cluster.title}\n\n{_wrap(cluster.body).rstrip()}\n")
        if cluster.where:
            parts.append(f"\nStated in: {cluster.where}\n")
    parts.append(
        f"\n## Budget (8c)\n\n{len(clusters)} cluster(s) against "
        f"`param-max-comments-per-PR` = {limit}.\n"
    )
    return "".join(parts)


# -- assembly ---------------------------------------------------------------


def build(
    plan: Plan,
    records: list[Record],
    source: str,
    text: str,
    parity: Parity,
    placement: str,
    limit,
    blob: str | None = None,
    drifts: list | None = None,
) -> Report:
    """The three artifacts plus the cluster list the budget check reads.

    ``drifts`` are the hand-moved blocks ``position.measure`` found. They are
    a cluster like any other because the 8c budget counts PR comments, and a
    comment the tool cannot see is one it would count wrong (Nick,
    2026-08-05). Empty on unstructured input, so run 1 is unaffected.
    """
    clusters: list[Cluster] = []

    forms = sorted({str(a.get("form", "")) for a in plan.additions})
    clusters.append(
        Cluster(
            title="Definitions drafted for undefined terms",
            body=(
                "**None.** No plan addition uses a definition form"
                + (f" — the {len(plan.additions)} Category C addition(s) are "
                   f"section prose ({', '.join(f'`{f}`' for f in forms)})"
                   if plan.additions
                   else "")
                + ". Composing a definition from usage hints rather than "
                "definitional wording is what criterion 7 calls the "
                "highest-risk output the tool can produce, so the plan has to "
                "ask for one explicitly."
            ),
        )
    )

    orphans, by_ruling = _undefined(plan, records, placement)
    body = (
        f"**{len(orphans)} orphan(s)** — used here, defined nowhere in the "
        "detangle set. Each is positioned; none blocks reading.\n\n"
        f"{_listing(orphans)}\n"
    )
    if by_ruling:
        body += (
            f"\nA further **{len(by_ruling)}** term(s) are undefined by ruling "
            "rather than by omission: where a business object and the software "
            "producing it share a definition site, only the business term is "
            "defined (IBE/IBEB, 2026-07-30). They carry no orphan flag and are "
            "not counted above.\n\n"
            f"{_listing(by_ruling)}\n"
        )
    clusters.append(Cluster(title="Terms used here with no definition", body=body))

    forward = _forward_references(plan, records)
    clusters.append(
        Cluster(
            title="Forward references",
            body=(
                "**None.** Every definition block in this document is preceded "
                "by the definitions it depends on (criterion 1)."
                if not forward
                else f"**{len(forward)}**, each needing a bridging marker "
                "(criterion 1 clause 2):\n\n"
                + "\n".join(f"- `{a}` → `{b}`, defined later" for a, b in forward)
            ),
        )
    )

    if not parity.clean:
        clusters.append(
            Cluster(
                title="Words the run could not account for",
                body=(
                    f"Missing {sum(parity.missing.values())}, extra "
                    f"{sum(parity.extra.values())} — see the criterion-5 table "
                    f"in `{COUNTS}`. This is a `token-parity` finding, not a "
                    "note: the plan or the renderer has to change."
                ),
            )
        )

    if drifts:
        clusters.append(
            Cluster(
                title="Blocks moved by hand, which this run moved back",
                body=cluster_body(drifts),
            )
        )

    for declared in plan.exceptions:
        clusters.append(
            Cluster(
                title=str(declared["title"]),
                body="Ruled by a human; the reasoning is written where the "
                "pointer says, and is not reproduced here.",
                where=str(declared["where"]),
            )
        )

    return Report(
        files={
            MOVE_MAP: _move_map(plan, source, parity, blob),
            COUNTS: _counts(plan, text, parity, len(clusters)),
            EXCEPTIONS: _exceptions(plan, clusters, limit),
        },
        clusters=clusters,
    )


def check_budget(report: Report, limit, rel: str) -> list[Finding]:
    """8c: one restructure may not bury a reviewer.

    Over budget the run reports and writes nothing — a document nobody can
    review in one pass is not a deliverable, and the fix is to split the work
    or resolve clusters, both human decisions.
    """
    if not isinstance(limit, int) or len(report.clusters) <= limit:
        return []
    return [
        error(
            "comment-budget",
            rel,
            f"{len(report.clusters)} PR comment cluster(s) exceeds "
            f"param-max-comments-per-PR = {limit} — the restructured document "
            "is not written. Split the work, or resolve clusters first "
            f"(the roster is in {EXCEPTIONS})",
        )
    ]


def write(report: Report, directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for name, body in report.files.items():
        (directory / name).write_text(body, encoding="utf-8")


def check_current(report: Report, directory: Path, rel: str) -> list[Finding]:
    """Bytes, not structure — the guard every derived artifact carries."""
    out: list[Finding] = []
    for name, body in report.files.items():
        path = directory / name
        if not path.is_file():
            out.append(
                error(
                    "report-missing",
                    f"{rel}/{name}",
                    "no generated self-report on disk; run `detangle "
                    "restructure --report` and commit the result",
                )
            )
        elif path.read_text(encoding="utf-8") != body:
            out.append(
                error(
                    "report-drift",
                    f"{rel}/{name}",
                    "the committed self-report differs from a re-execution — "
                    "it was hand-edited, or the plan/source/records changed "
                    "without re-running `detangle restructure --report`",
                )
            )
    return out


__all__ = [
    "ARTIFACTS",
    "CHECKS",
    "COUNTS",
    "EXCEPTIONS",
    "MOVE_MAP",
    "Cluster",
    "Report",
    "build",
    "check_budget",
    "check_current",
    "write",
]
