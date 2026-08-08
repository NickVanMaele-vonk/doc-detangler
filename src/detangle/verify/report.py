"""The verification report — ADR-003 Decision 5 and plan step 7.5.

Two jobs, and the second is the reason the first is not enough.

**It records what the run verified.** Step 7.5: the git blob of every document
the run read, plus the commit. A blob *is* a version — immutable, retrievable
with `git show` however many versions follow — so a report from three re-runs
ago still names exactly the bytes it was talking about, and the next run has a
baseline to check against. `manifest.yaml` (step 10.4) is the set-level version
of the same record and absorbs this when it exists.

**It records what the run did not do**, and that is load-bearing. Nick ruled on
2026-08-07 that `detangle verify` runs deterministically by default, with the
model path behind a `--use-inference` flag that is backlog work. So today the
command runs three of the four stages: it can say what moved verbatim and
whether any term is used before its definition, and it cannot say whether the
output contains invented text. A command that exits `0` having skipped the
fabrication check would read as *verified*, which is the same trap as reading
exit `2` as "no findings". So the absence is stated in the report, in the
summary, and — for the coverage residue, which is a countable quantity — as a
finding, so the run does not come back clean about claims it never ruled on.

`coverage-unscored` is a **warn**, and waivable. Nothing is wrong with the
document; work is outstanding, which is precisely what the waiver register is
for. It is one finding per document carrying the count, not one per claim:
comments are raised per cluster, not per instance (rubric §8d).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from ..findings import Finding, warn
from .claims import DECOMPOSER_VERSION
from .coverage import Coverage
from .structure import Structure

#: See ``records.checks.CHECKS`` for why every module declares its slugs.
CHECKS = frozenset({"coverage-unscored"})

#: Stage → whether the deterministic build can run it. The rows are printed
#: whatever the answer, because a stage missing from the report is a stage a
#: reader assumes ran.
STAGES = (
    ("7.1", "claim decomposition", True),
    ("7.2a", "coverage — deterministic match", True),
    ("7.2b", "coverage — scored residue", False),
    ("7.3", "fabrication", False),
    ("7.4", "concept-before-use", True),
)

NOT_RUN = (
    "needs a model; deferred behind `--use-inference` (backlog B-9, "
    "ADR-003 Decision 3 unruled)"
)

PREVIEW = 90


@dataclass(frozen=True)
class Version:
    """One document as this run read it."""

    code: str
    role: str  # "detangle" | "reference" | "output" | "glossary"
    rel: str
    blob: str
    committed: bool

    @property
    def note(self) -> str:
        return "" if self.committed else " (working tree — not committed)"


@dataclass
class Report:
    commit: str
    #: Claim-split entries the run loaded (ADR-003 Decision 1). Recorded
    #: because the decomposer moves the scores and its overrides move with it.
    overrides: int = 0
    versions: list[Version] = field(default_factory=list)
    coverage: dict[str, Coverage] = field(default_factory=dict)
    structure: Structure | None = None

    @property
    def unscored(self) -> int:
        return sum(len(c.residue) for c in self.coverage.values())


def check_unscored(report: Report) -> list[Finding]:
    """Say, per document, how much of it this run declined to rule on."""
    out: list[Finding] = []
    for code, coverage in sorted(report.coverage.items()):
        if not coverage.residue:
            continue
        out.append(
            warn(
                "coverage-unscored",
                f"{code}:coverage",
                f"{len(coverage.residue)} of {coverage.source_claims} claims did "
                "not move verbatim and were not scored: this run cannot say "
                "whether they survived. Deterministic mode has no model — see "
                "the residue roster in the verification report",
            )
        )
    return out


def _overrides(count: int) -> str:
    """Say the register was read even when it had nothing to say.

    Zero overrides and no register at all produce identical claim lists, and
    only one of them means a human ruled nothing yet. The blob in the version
    table settles which; this line makes a reader look for it.
    """
    if not count:
        return "no claim-split overrides (the register is empty)"
    return f"{count} claim-split override{'' if count == 1 else 's'} applied"


def _stage_table() -> list[str]:
    lines = ["| Step | Stage | This run |", "|---|---|---|"]
    for step, name, ran in STAGES:
        status = "ran" if ran else f"**not run** — {NOT_RUN}"
        lines.append(f"| {step} | {name} | {status} |")
    return lines


def _version_table(report: Report) -> list[str]:
    lines = ["| Document | Role | Blob |", "|---|---|---|"]
    for v in report.versions:
        lines.append(f"| `{v.rel}` | {v.role} | `{v.blob}`{v.note} |")
    return lines


def render(report: Report) -> str:
    """The committed report. No timestamp: the commit and the blobs date it."""
    out: list[str] = [
        "# Verification report",
        "",
        "<!-- Generated by `detangle verify`. Do not hand-edit: re-run the "
        "command. -->",
        "",
        f"Run at commit `{report.commit}`, decomposer `{DECOMPOSER_VERSION}`, "
        f"{_overrides(report.overrides)}.",
        "",
        "## What this run checked",
        "",
        *_stage_table(),
        "",
        "**This run did not check for invented text.** Constraint C2's first "
        "limb — every output claim traces to one of the input sets — is not "
        "verified here. Nor is coverage of any claim whose wording changed: "
        "those are listed below as the residue, unresolved rather than lost.",
        "",
        "## Versions verified (step 7.5)",
        "",
        *_version_table(report),
        "",
        "A blob is the version. `git show <blob>` retrieves these exact bytes "
        "however many revisions follow, so this report keeps meaning after the "
        "documents move on, and the next run has a baseline.",
        "",
        "## Coverage",
        "",
        "| Document | Source claims | Placed verbatim | Residue "
        "| Output claims unexplained |",
        "|---|---|---|---|---|",
    ]
    for code, coverage in sorted(report.coverage.items()):
        out.append(
            f"| {code} | {coverage.source_claims} | {len(coverage.matched)} "
            f"({coverage.rate:.1%}) | {len(coverage.residue)} | "
            f"{len(coverage.unplaced)} |"
        )
    out += [
        "",
        "A placed claim moved verbatim: text identity, confidence 1.0, no "
        "model involved. A residue claim changed in some way and is "
        "**unresolved, not missing** — scoring it is what `--use-inference` "
        "will do. Unexplained output claims are fabrication candidates and are "
        "equally unresolved: definitions lifted from the records and the "
        "authored overview both land there by construction.",
        "",
        "## Concept-before-use",
        "",
    ]
    structure = report.structure
    if structure is None:
        out.append("Not run.")
    else:
        out += [
            f"Reading order scanned: {' → '.join(structure.documents)}.",
            "",
            f"- Definition sites found: **{len(structure.defined_at)}**",
            f"- Terms used before their definition: **{len(structure.forward)}**",
            f"- Accepted-cycle bridging references (criterion 1 clause 2), "
            f"exempt: **{len(structure.exempt)}**",
            f"- Defined records with no definition site in these documents: "
            f"**{len(structure.no_site)}**",
            "",
        ]
        if structure.forward:
            out += ["| Term | Used at | Defined at | Inside |", "|---|---|---|---|"]
            for f in structure.forward:
                inside = f"`{f.inside}`" if f.inside else "—"
                out.append(
                    f"| `{f.concept}` | {f.used_at} | {f.defined_at} | {inside} |"
                )
            out.append("")
    out += ["## Residue roster", ""]
    if not report.unscored:
        out.append("Empty — every source claim moved verbatim.")
    else:
        out.append(
            "Every claim this run could not place, so the next pass has a "
            "work-list rather than a number."
        )
        out.append("")
        for code, coverage in sorted(report.coverage.items()):
            if not coverage.residue:
                continue
            out += [f"### {code}", ""]
            for claim in coverage.residue:
                text = claim.text if len(claim.text) <= PREVIEW else (
                    claim.text[:PREVIEW].rstrip() + "…"
                )
                out.append(f"- `{claim.id}` ({claim.kind}) — {text}")
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def write(report: Report, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render(report), encoding="utf-8")


__all__ = ["CHECKS", "Report", "Version", "check_unscored", "render", "write"]
