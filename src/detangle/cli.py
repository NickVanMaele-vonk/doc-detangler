"""The ``detangle`` command line (ADR-001 Decision 2).

Subcommands, one job each. ``--json`` on every command that reports findings.
Exit 0 clean, 1 findings raised, 2 usage or internal error. Never interactive,
no network, deterministic output.
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path

from . import __version__, graph, tables
from .config import Config, find_root
from .findings import EXIT_CLEAN, EXIT_USAGE, UsageError, report
from .graph import emit
from .records import BlockIndex, load_records
from .records import checks as record_checks
from .registers import load_cycles


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

    records, findings = load_records(config.directory("concepts"), root)
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


def cmd_graph(args: argparse.Namespace) -> int:
    root = find_root(Path(args.root) if args.root else None)
    config = Config.load(root, Path(args.config) if args.config else None)

    records, findings = load_records(config.directory("concepts"), root)
    register, register_findings = load_cycles(config.directory("registers"), root)
    findings.extend(register_findings)

    concept_graph, build_findings = graph.build(records, register)
    findings.extend(build_findings)

    if args.impact or args.requires:
        return _query(concept_graph, args)

    out_path = config.path("graph")
    rel = str(out_path.relative_to(root))
    if args.check:
        findings.extend(emit.check_current(concept_graph, out_path, rel))
    else:
        out_path.write_text(emit.render(concept_graph), encoding="utf-8")

    cycles = concept_graph.cycles
    summary = {
        "nodes": concept_graph.graph.number_of_nodes(),
        "edges": concept_graph.graph.number_of_edges(),
        "cycles": len(cycles),
        "orphans": len(concept_graph.orphans()),
        "dead_entries": len(concept_graph.dead_entries()),
        "wrote" if not args.check else "checked": rel,
    }
    return report(findings, args.json, summary)


def _query(cg, args: argparse.Namespace) -> int:
    """Reachability lookups. Read-only: they never write the graph."""
    node = args.impact or args.requires
    if node not in cg.records:
        raise UsageError(f"no concept record with id {node!r}")
    result = cg.impact(node) if args.impact else cg.requires(node)
    direction = "impact" if args.impact else "requires"
    if args.json:
        json.dump(
            {"node": node, direction: result, "count": len(result)},
            sys.stdout,
            indent=2,
        )
        sys.stdout.write("\n")
    else:
        for rid in result:
            print(rid)
        print(f"{len(result)} concepts", file=sys.stderr)
    return EXIT_CLEAN


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

    graph_cmd = sub.add_parser(
        "graph",
        help="build the concept graph and write concept-graph.yaml",
        description=(
            "Builds the dependency graph from the records' canonical "
            "depends_on, rolls up the cycle register, and writes the derived "
            "concept-graph.yaml. --check verifies the committed file instead."
        ),
    )
    graph_cmd.add_argument("--json", action="store_true", help="machine-readable")
    graph_cmd.add_argument("--config", help="config file (default: detangle.toml)")
    graph_cmd.add_argument("--root", help="repository root (default: nearest ancestor)")
    graph_cmd.add_argument(
        "--check",
        action="store_true",
        help="do not write; fail if the committed graph differs from a regeneration",
    )
    query = graph_cmd.add_mutually_exclusive_group()
    query.add_argument(
        "--impact",
        metavar="ID",
        help="list the concepts whose definitions transitively depend on ID",
    )
    query.add_argument(
        "--requires",
        metavar="ID",
        help="list everything that must be defined before ID can be read",
    )
    graph_cmd.set_defaults(func=cmd_graph)
    return parser


def main(argv: list[str] | None = None) -> int:
    """Exit 0 clean, 1 findings, 2 usage or internal error — ADR-001 D2.

    The blanket ``except`` is the "never 1 for a crash" half of that contract.
    Without it an unexpected exception leaves the interpreter to exit 1, and
    branch policy — which reads 1 as "findings raised, post them and block" —
    would treat a crashed run as a completed one that happened to find things.
    The traceback still reaches stderr, because 2 says only that no verdict
    was reached, not why.
    """
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except UsageError as exc:
        print(f"detangle: {exc}", file=sys.stderr)
        return EXIT_USAGE
    except Exception:  # noqa: BLE001 — deliberate: 2 is the contract for these
        traceback.print_exc()
        print(
            "detangle: internal error — exiting 2, not 1: this run reached no "
            "verdict, so it is not 'no findings'",
            file=sys.stderr,
        )
        return EXIT_USAGE


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
