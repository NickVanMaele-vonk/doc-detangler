"""Findings and exit codes — the CLI contract of ADR-001 Decision 2.

Exit codes: 0 clean, 1 findings raised (the branch-policy signal), 2 usage or
internal error. Never 1 for a crash.

Severity ranks findings for a reader; it does not change the exit code. Any
finding at all means "findings raised", so a stale span cannot pass CI merely
by being less severe than a malformed one. Machine consumers filter on the
severity field in ``--json`` output.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass

EXIT_CLEAN = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 2

ERROR = "error"
WARN = "warn"

_RANK = {ERROR: 0, WARN: 1}


class UsageError(Exception):
    """Anything that must exit 2: bad invocation, missing config, no pandoc."""


@dataclass(frozen=True)
class Finding:
    """One thing wrong, addressed to whoever has to fix it.

    ``check`` is a stable slug so a finding can be cited in a PR thread and
    grepped for later; ``where`` is a repo-relative path, optionally with a
    field or line suffix.
    """

    severity: str
    check: str
    where: str
    message: str

    @property
    def sort_key(self) -> tuple:
        return (_RANK.get(self.severity, 9), self.check, self.where, self.message)

    def as_dict(self) -> dict:
        return {
            "severity": self.severity,
            "check": self.check,
            "where": self.where,
            "message": self.message,
        }


def error(check: str, where: str, message: str) -> Finding:
    return Finding(ERROR, check, where, message)


def warn(check: str, where: str, message: str) -> Finding:
    return Finding(WARN, check, where, message)


def report(findings: list[Finding], as_json: bool, summary: dict | None = None) -> int:
    """Print findings in a stable order and return the exit code.

    Deterministic output is part of the CLI contract, so the sort is total and
    the JSON keys are fixed.
    """
    ordered = sorted(findings, key=lambda f: f.sort_key)
    if as_json:
        payload = {
            "findings": [f.as_dict() for f in ordered],
            "counts": {
                ERROR: sum(1 for f in ordered if f.severity == ERROR),
                WARN: sum(1 for f in ordered if f.severity == WARN),
            },
        }
        if summary:
            payload["summary"] = summary
        json.dump(payload, sys.stdout, indent=2, sort_keys=False)
        sys.stdout.write("\n")
    else:
        for f in ordered:
            print(f"{f.severity:5}  {f.check:24}  {f.where}\n       {f.message}")
        if summary:
            print("  ".join(f"{k}: {v}" for k, v in summary.items()))
        if ordered:
            n_err = sum(1 for f in ordered if f.severity == ERROR)
            n_warn = len(ordered) - n_err
            print(f"{len(ordered)} findings ({n_err} error, {n_warn} warn)")
        else:
            print("clean — no findings")
    return EXIT_FINDINGS if ordered else EXIT_CLEAN
