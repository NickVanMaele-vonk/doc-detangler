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

from . import __version__, graph, registers, restructure, tables, verify, views
from .config import Config, find_root
from .findings import EXIT_CLEAN, EXIT_FINDINGS, EXIT_USAGE, UsageError, report
from .graph import emit

# `graph` re-exports the *function* `build`, which shadows the submodule.
from .graph.build import CHECKS as BUILD_CHECKS
from .records import BlockIndex, load_records
from .records import checks as record_checks
from .records import load as records_load
from .registers import load_cycles, load_waivers
from .restructure import execute as restructure_execute
from .restructure import parity as restructure_parity
from .restructure import position as restructure_position
from .restructure import report as restructure_report
from .verify import report as verify_report
from .verify import structure as verify_structure


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


def _waived(config, root: Path, findings: list, ran: frozenset, full: bool = True):
    """Apply ``registers/waivers.yaml`` to one command's findings.

    Every command that reports findings goes through here, so a disposition
    means the same thing whichever command surfaced the finding. ``ran`` is the
    set of checks this command actually performed: staleness is judged against
    that and nothing else (``WaiverRegister.stale_findings``).

    ``full`` is false for a narrowed run — a record the run never looked at
    cannot prove its waiver dead.
    """
    waivers, register_findings = load_waivers(config.directory("registers"), root)
    live, waived = waivers.partition(findings)
    live.extend(register_findings)
    if full:
        live.extend(waivers.stale_findings(waived, ran))
    return live, waived


def cmd_validate(args: argparse.Namespace) -> int:
    root = find_root(Path(args.root) if args.root else None)
    config = Config.load(root, Path(args.config) if args.config else None)

    records, findings = load_records(config.directory("concepts"), root)
    targets = _selected(records, root, args.paths)
    if args.paths and not targets:
        raise UsageError("none of the given paths is a concept record")

    registry = config.registry()
    findings.extend(record_checks.check_cross_record(records))
    findings.extend(record_checks.check_placement(records, registry))
    findings.extend(
        record_checks.check_approval_batches(
            records, int(config.param("max-definitions-per-approval"))
        )
    )

    index = BlockIndex(root=root)
    blobs = record_checks.GitBlobs(root)
    min_run = int(config.option("validate", "min-verbatim-run-chars", 10))

    for rec in targets:
        findings.extend(record_checks.check_schema(rec, registry))
        findings.extend(record_checks.check_span_docs(rec, registry))
        findings.extend(record_checks.check_assurance(rec))
        findings.extend(record_checks.check_invariants(rec, registry))
        findings.extend(record_checks.check_provenance(rec, index, blobs))
        findings.extend(record_checks.check_definition_wording(rec, index, min_run))
        findings.extend(record_checks.check_conflict_quotes(rec, index))

    # The checks this run owns, composed rather than assumed: a waiver for a
    # check nobody ran here must not be judged by it (registers.stale_findings).
    ran = record_checks.CHECKS | records_load.CHECKS | registers.WAIVER_CHECKS
    if not args.no_tables:
        ran |= tables.CHECKS
        globs = config.option("validate", "table-globs", [])
        findings.extend(tables.check_files(root, globs))

    live, waived = _waived(config, root, findings, ran, full=not args.paths)

    summary = {
        "records": len(records),
        "checked": len(targets),
        "defined": sum(1 for r in targets if r.defined),
        "waived": len(waived),
    }
    return report(live, args.json, summary, waived)


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
    ran = records_load.CHECKS | registers.CYCLE_CHECKS | BUILD_CHECKS
    ran |= registers.WAIVER_CHECKS
    if args.check:
        ran |= emit.CHECKS
        findings.extend(emit.check_current(concept_graph, out_path, rel))
    else:
        out_path.write_text(emit.render(concept_graph), encoding="utf-8")

    findings, waived = _waived(config, root, findings, ran)

    cycles = concept_graph.cycles
    summary = {
        "nodes": concept_graph.graph.number_of_nodes(),
        "edges": concept_graph.graph.number_of_edges(),
        "cycles": len(cycles),
        "orphans": len(concept_graph.orphans()),
        "dead_entries": len(concept_graph.dead_entries()),
        "wrote" if not args.check else "checked": rel,
        "waived": len(waived),
    }
    return report(findings, args.json, summary, waived)


def cmd_generate(args: argparse.Namespace) -> int:
    """Write ``glossary.md`` from the records — plan step 3.5.

    Scope is the glossary alone: ``index.md`` needs the document bodies, which
    carry the definition site of 94 defined terms (criterion 4), and
    ``concept-graph.mmd`` needs a scoping decision before 359 nodes are drawn
    as one diagram. Both are step 3.6, not this command.

    The graph's own findings are reported here as well as by ``detangle
    graph``. The duplication is deliberate: an undispositioned cycle makes the
    reading order this command renders wrong, so the gate that produces the
    file must not be green while it stands.
    """
    root = find_root(Path(args.root) if args.root else None)
    config = Config.load(root, Path(args.config) if args.config else None)

    records, findings = load_records(config.directory("concepts"), root)
    register, register_findings = load_cycles(config.directory("registers"), root)
    findings.extend(register_findings)

    concept_graph, build_findings = graph.build(records, register)
    findings.extend(build_findings)

    out_path = config.path("glossary")
    rel = str(out_path.relative_to(root))
    glossary = views.build(concept_graph, rel, config.registry())
    findings.extend(glossary.findings)

    ran = records_load.CHECKS | registers.CYCLE_CHECKS | BUILD_CHECKS
    ran |= views.glossary.RENDER_CHECKS | registers.WAIVER_CHECKS
    if args.check:
        ran |= views.glossary.DRIFT_CHECKS
        findings.extend(views.check_current(glossary.text, out_path, rel))
    else:
        # This command is the seeder, and it ran (2026-08-04). Nick's ruling of
        # the same day made the file the fourth *editable* document, so a
        # second run would silently destroy human work that nothing else holds
        # a copy of — the drift lint that would mirror it into the records does
        # not exist yet. Refuse rather than warn: a warning arrives after the
        # bytes are gone.
        if out_path.exists() and not args.force:
            raise UsageError(
                f"{rel} already exists, and it is edited by people (Nick, "
                "2026-08-04) — generate would rewrite it in full and discard "
                "every edit. Use --check to compare it against a "
                "regeneration, or --force to overwrite it deliberately."
            )
        out_path.write_text(glossary.text, encoding="utf-8")

    findings, waived = _waived(config, root, findings, ran)

    summary = {
        **glossary.summary,
        "checked" if args.check else "wrote": rel,
        "waived": len(waived),
    }
    return report(findings, args.json, summary, waived)


def cmd_restructure(args: argparse.Namespace) -> int:
    """Execute a reorder plan — ADR-002 Decision 3, the detangle run itself.

    The plan is data the tool never authors; an error-grade plan finding
    (an undecided block, a broken reference, an unsafe repair) blocks
    execution outright — writing a document from an incomplete plan would
    launder a coverage hole into an omission.
    """
    root = find_root(Path(args.root) if args.root else None)
    config = Config.load(root, Path(args.config) if args.config else None)
    registry = config.registry()

    records, findings = load_records(config.directory("concepts"), root)
    plan, plan_findings = restructure.load_plan(Path(args.plan), root)
    findings.extend(plan_findings)

    ran = (
        restructure.CHECKS
        | restructure_execute.CHECKS
        | restructure_parity.CHECKS
        | restructure_position.CHECKS
        | restructure_report.CHECKS
        | records_load.CHECKS
        | registers.WAIVER_CHECKS
    )
    out_path = Path(args.out)
    try:
        rel = str(out_path.resolve().relative_to(root.resolve()))
    except ValueError:
        rel = str(out_path)  # outside the repo is fine for an output

    if plan is not None:
        index = BlockIndex(root=root)
        blobs = record_checks.GitBlobs(root)
        doc_path = registry.paths.get(plan.doc)
        head = blobs.head(doc_path) if doc_path in registry.component_docs else None
        findings.extend(
            restructure.validate_plan(plan, registry, index, records, head)
        )

    blocked = plan is None or any(f.severity == "error" for f in findings)
    summary: dict = {"plan": args.plan}
    if not blocked:
        source = (root / registry.paths[plan.doc]).read_text(encoding="utf-8")
        rendered = restructure_execute.render(plan, records, source)
        text = rendered.text()

        # Criterion 5 runs on every execution, write or check: a document
        # that lost a word is wrong whether or not it also drifted.
        parity = restructure_parity.measure(plan, source, rendered)
        findings.extend(restructure_parity.check(parity, plan.rel))

        # ADR-004 Decision 8: a block a human moved by hand is put back by
        # this run, so say so and offer the plan line that would ratify the
        # move. A warning, never an error — placement is a claim and the
        # disposition is a human's, exactly as for a proposed `depends_on`
        # edge. Silent on unstructured input, where the plan reorders nearly
        # everything by design.
        drifts = restructure_position.measure(plan, source)
        findings.extend(restructure_position.check(drifts, plan.rel))

        # The 8f self-report is built on every run, not only when it is
        # written: the 8c budget counts the clusters it found, and a run that
        # buries its reviewer is over budget whether or not files were asked
        # for.
        limit = config.param("param-max-comments-per-PR")
        built = restructure_report.build(
            plan,
            records,
            source,
            text,
            parity,
            registry.placements[plan.doc],
            limit,
            blob=plan.pinned_blob or head,
            drifts=drifts,
        )
        budget = restructure_report.check_budget(built, limit, plan.rel)
        findings.extend(budget)

        report_dir = Path(args.report) if args.report else None
        if args.check:
            findings.extend(restructure_execute.check_current(text, out_path, rel))
            if report_dir is not None:
                findings.extend(
                    restructure_report.check_current(built, report_dir, args.report)
                )
        elif budget:
            # Reported, not emitted (ADR-002 Decision 3).
            if report_dir is not None:
                restructure_report.write(built, report_dir)
        else:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(text, encoding="utf-8")
            if report_dir is not None:
                restructure_report.write(built, report_dir)
        summary.update(
            {
                "doc": plan.doc,
                # Headed sections only — what a reader meets (Nick,
                # 2026-08-05). The headless `head` identity block is
                # listed in the report's Section IDs table, not counted.
                "sections": sum(1 for s in plan.sections if s.kind != "head"),
                "units": len(plan.assignments),
                "definitions": len(plan.definitions),
                "source words": sum(parity.expected.values()),
                "unexplained": sum(parity.missing.values())
                + sum(parity.extra.values()),
                "comments": f"{len(built.clusters)}/{limit}",
            }
        )
        if budget:
            summary["blocked"] = "over the comment budget; document not written"
        else:
            summary["checked" if args.check else "wrote"] = rel
        if report_dir is not None:
            summary["report"] = args.report
    else:
        summary["blocked"] = "plan findings prevent execution"

    findings, waived = _waived(config, root, findings, ran)
    summary["waived"] = len(waived)
    code = report(findings, args.json, summary, waived)
    return max(code, EXIT_FINDINGS) if blocked and code == EXIT_CLEAN else code


def _outputs(pairs: list[str], registry) -> dict[str, Path]:
    """Parse ``--output CODE=PATH`` into a mapping, rejecting unknown codes."""
    out: dict[str, Path] = {}
    for pair in pairs:
        code, _, path = pair.partition("=")
        if not code or not path:
            raise UsageError(f"--output wants CODE=PATH, got {pair!r}")
        if code not in registry.components:
            raise UsageError(
                f"{code!r} is not a detangle-set document; only these are "
                f"restructured and verified: {', '.join(registry.components)}"
            )
        if code in out:
            raise UsageError(f"--output {code} given twice")
        out[code] = Path(path)
    return out


def cmd_verify(args: argparse.Namespace) -> int:
    """The losslessness harness — ADR-003 Decision 5, ruled by Nick 2026-08-07.

    Deterministic by default, and today that is the only mode: the scored
    stages wait behind ``--use-inference``, which is backlog work. The command
    therefore has to be loud about what it did not do, or a clean exit reads as
    a proof it never produced. That is the job of the report's stage table and
    of the ``coverage-unscored`` finding.

    Not a CI gate (Decision 5, reaffirmed with ADR-004 Decision 7): every check
    here awaits a human disposition, so blocking merge on one converts a review
    prompt into a hard stop.
    """
    root = find_root(Path(args.root) if args.root else None)
    config = Config.load(root, Path(args.config) if args.config else None)
    registry = config.registry()
    outputs = _outputs(args.output, registry)

    records, findings = load_records(config.directory("concepts"), root)
    register, cycle_findings = load_cycles(config.directory("registers"), root)
    findings.extend(cycle_findings)
    cg, graph_findings = graph.build(records, register)
    findings.extend(graph_findings)

    blobs = record_checks.GitBlobs(root)
    built = verify_report.Report(commit=blobs.commit())

    def _version(code: str, role: str, path: Path) -> None:
        rel = str(path.relative_to(root)) if path.is_absolute() else str(path)
        if not (root / rel).is_file():
            raise UsageError(f"{rel} does not exist; nothing to verify")
        built.versions.append(
            verify_report.Version(
                code=code,
                role=role,
                rel=rel,
                blob=blobs.live(rel),
                committed=not blobs.worktree_differs(rel),
            )
        )

    # The glossary is read first and is part of the reading order, so its
    # absence would silently make every forward-reference verdict wrong.
    glossary = config.path("glossary")
    _version("glossary", "glossary", glossary)
    reading = [
        verify_structure.Document(
            "glossary", glossary.read_text(encoding="utf-8")
        )
    ]

    for code in registry.components:
        if code not in outputs:
            continue
        source_rel = registry.paths[code]
        _version(code, "detangle set (source)", Path(source_rel))
        _version(code, "output", outputs[code])
        source_text = (root / source_rel).read_text(encoding="utf-8")
        output_text = outputs[code].read_text(encoding="utf-8")

        source = verify.decompose(source_text, code)
        output = verify.decompose(output_text, f"{code}-out")
        built.coverage[code] = verify.match(source, output)
        reading.append(verify_structure.Document(code, output_text))

    built.structure = verify_structure.scan(reading, cg)
    findings.extend(verify_structure.check(built.structure))
    findings.extend(verify_report.check_unscored(built))

    ran = (
        records_load.CHECKS
        | registers.CYCLE_CHECKS
        | BUILD_CHECKS
        | verify_structure.CHECKS
        | verify_report.CHECKS
        | registers.WAIVER_CHECKS
    )

    summary: dict = {
        "commit": built.commit,
        "documents": ", ".join(sorted(outputs)),
        "reading order": " → ".join(d.code for d in reading),
        "placed verbatim": sum(len(c.matched) for c in built.coverage.values()),
        "unscored": built.unscored,
        "forward references": len(built.structure.forward),
        "exempt": len(built.structure.exempt),
        "fabrication": "NOT CHECKED — deterministic run, no model",
    }
    if args.report:
        verify_report.write(built, Path(args.report))
        summary["report"] = args.report

    findings, waived = _waived(config, root, findings, ran)
    summary["waived"] = len(waived)
    return report(findings, args.json, summary, waived)


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

    generate = sub.add_parser(
        "generate",
        help="write the generated views — glossary.md",
        description=(
            "Renders glossary.md from the canonical concept records, in the "
            "concept graph's topological order (param-glossary-order). "
            "--check verifies the committed file instead of writing it. "
            "This command seeded glossary.md, which is now edited by people, "
            "so it refuses to overwrite an existing file unless --force. "
            "index.md and concept-graph.mmd are step 3.6 and are not written."
        ),
    )
    generate.add_argument("--json", action="store_true", help="machine-readable")
    generate.add_argument("--config", help="config file (default: detangle.toml)")
    generate.add_argument("--root", help="repository root (default: nearest ancestor)")
    generate.add_argument(
        "--check",
        action="store_true",
        help="do not write; fail if a committed view differs from a regeneration",
    )
    generate.add_argument(
        "--force",
        action="store_true",
        help="overwrite an existing glossary.md, discarding any human edits",
    )
    generate.set_defaults(func=cmd_generate)

    restructure_cmd = sub.add_parser(
        "restructure",
        help="execute a reorder plan and write the restructured document",
        description=(
            "Executes a machine-readable reorder plan (ADR-002): source "
            "blocks move verbatim, declared fragments rejoin, declared noise "
            "drops, definitions render from the records, and the authored "
            "Category C additions come from the plan. An error-grade plan "
            "finding blocks execution. --check re-executes and compares "
            "against the committed output instead of writing."
        ),
    )
    restructure_cmd.add_argument("--plan", required=True, help="the plan file")
    restructure_cmd.add_argument(
        "--out", required=True, help="output path for the restructured document"
    )
    restructure_cmd.add_argument(
        "--report",
        help="directory for the generated 8f self-report "
        f"({', '.join(restructure_report.ARTIFACTS)}); omitted, none is written",
    )
    restructure_cmd.add_argument(
        "--json", action="store_true", help="machine-readable"
    )
    restructure_cmd.add_argument(
        "--config", help="config file (default: detangle.toml)"
    )
    restructure_cmd.add_argument(
        "--root", help="repository root (default: nearest ancestor)"
    )
    restructure_cmd.add_argument(
        "--check",
        action="store_true",
        help="do not write; fail if the committed output differs from a re-execution",
    )
    restructure_cmd.set_defaults(func=cmd_restructure)

    verify_cmd = sub.add_parser(
        "verify",
        help="run the losslessness harness over the restructured documents",
        description=(
            "Checks the output against the source (ADR-003): every claim that "
            "moved verbatim is placed deterministically, and no term is used "
            "before its definition across the reading order. Runs "
            "DETERMINISTICALLY — it does NOT check for invented text, and it "
            "does not score claims whose wording changed. Those need a model, "
            "which waits behind --use-inference (backlog B-9). Not a CI gate."
        ),
    )
    verify_cmd.add_argument(
        "--output",
        action="append",
        required=True,
        metavar="CODE=PATH",
        help="a restructured document to verify, e.g. U=eval/golden/uce.md; "
        "repeatable",
    )
    verify_cmd.add_argument(
        "--report", help="path for the verification report; omitted, none is written"
    )
    verify_cmd.add_argument("--json", action="store_true", help="machine-readable")
    verify_cmd.add_argument("--config", help="config file (default: detangle.toml)")
    verify_cmd.add_argument(
        "--root", help="repository root (default: nearest ancestor)"
    )
    verify_cmd.set_defaults(func=cmd_verify)
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
