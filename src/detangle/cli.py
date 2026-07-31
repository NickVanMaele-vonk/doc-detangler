"""The ``detangle`` command line (ADR-001 Decision 2).

Subcommands, one job each. ``--json`` on every command that reports findings.
Exit 0 clean, 1 findings raised, 2 usage or internal error. Never interactive,
no network, deterministic output.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import __version__, tables
from .config import Config, find_root
from .findings import EXIT_USAGE, UsageError, report
from .records import BlockIndex, load_records
from .records import checks as record_checks


def _selected(records, root: Path, paths: list[str]):
    """Restrict per-record checks to the paths given, if any.

    Set-wide checks — one-definition-site, edge targets, dangling links — always
    run over the whole set, because a PR that touches one record can break an
    invariant that lives between two.
    """
    if not paths:
        return records
    wanted = {Path(p).resolve() for p in paths}
    return [r for r in records if r.path.resolve() in wanted]


def cmd_validate(args: argparse.Namespace) -> int:
    root = find_root(Path(args.root) if args.root else None)
    config = Config.load(root, Path(args.config) if args.config else None)

    records, findings = load_records(config.path("concepts"), root)
    targets = _selected(records, root, args.paths)
    if args.paths and not targets:
        raise UsageError("none of the given paths is a concept record")

    findings.extend(record_checks.check_cross_record(records))

    index = BlockIndex(root=root)
    blobs = record_checks.GitBlobs(root)
    min_run = int(config.option("validate", "min-verbatim-run-chars", 10))
    components = config.component_docs()

    for rec in targets:
        findings.extend(record_checks.check_schema(rec))
        findings.extend(record_checks.check_invariants(rec, components))
        findings.extend(record_checks.check_provenance(rec, index, blobs))
        findings.extend(record_checks.check_definition_wording(rec, index, min_run))
        findings.extend(record_checks.check_conflict_quotes(rec, index))

    if not args.no_tables:
        globs = config.option("validate", "table-globs", [])
        findings.extend(tables.check_files(root, globs))

    summary = {
        "records": len(records),
        "checked": len(targets),
        "defined": sum(1 for r in targets if r.defined),
    }
    return report(findings, args.json, summary)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="detangle", description="Restructure convoluted specifications."
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser(
        "validate", help="check record-set integrity and table well-formedness"
    )
    validate.add_argument(
        "paths",
        nargs="*",
        help="concept records to check; default is every record",
    )
    validate.add_argument("--json", action="store_true", help="machine-readable")
    validate.add_argument("--config", help="config file (default: detangle.toml)")
    validate.add_argument("--root", help="repository root (default: nearest ancestor)")
    validate.add_argument(
        "--no-tables", action="store_true", help="skip the markdown table check"
    )
    validate.set_defaults(func=cmd_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except UsageError as exc:
        print(f"detangle: {exc}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
