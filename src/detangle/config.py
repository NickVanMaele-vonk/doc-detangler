"""Reading detangle.toml.

Lookups are strict on purpose (ADR-001 Decision 2, working agreement "no
hard-coded values"): a parameter the rubric has not set is absent from the
file, and asking for it raises rather than falling back to a guess.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from .findings import UsageError

CONFIG_NAME = "detangle.toml"

BASE_FLAGS = ("orphan", "conflict")
GLOSSARY = "glossary"


@dataclass(frozen=True)
class DocumentRegistry:
    """The two input sets, resolved from ``[documents]`` and ``[placements]``.

    ``components`` is the detangle set — restructured, counted for placement
    and the orphan measure. ``references`` is the read-only reference set —
    citable for provenance, never counted, never modified (Nick, 2026-08-05).
    Built by ``Config.registry()``, which validates the two lists partition
    the declared codes; nothing here re-checks that.
    """

    components: tuple[str, ...]
    references: tuple[str, ...]
    paths: dict[str, str]
    placements: dict[str, str]

    @property
    def component_docs(self) -> set[str]:
        return {self.paths[c] for c in self.components}

    @property
    def reference_docs(self) -> set[str]:
        return {self.paths[c] for c in self.references}

    @property
    def registered_docs(self) -> set[str]:
        return self.component_docs | self.reference_docs

    @property
    def placement_values(self) -> tuple[str, ...]:
        """Legal ``placement`` field values: the glossary plus one per component."""
        return (GLOSSARY, *(self.placements[c] for c in self.components))

    @property
    def flags(self) -> tuple[str, ...]:
        """Legal record flags: the structural two plus one per reference code."""
        return (*BASE_FLAGS, *self.references)

    def role(self, path: str) -> str:
        """``component`` / ``reference`` for a registered path — for labelling."""
        if path in self.component_docs:
            return "component"
        if path in self.reference_docs:
            return "reference"
        return "unregistered"


@dataclass
class Config:
    root: Path
    data: dict = field(default_factory=dict)

    @classmethod
    def load(cls, root: Path, path: Path | None = None) -> Config:
        path = path or (root / CONFIG_NAME)
        if not path.is_file():
            raise UsageError(f"no config at {path}")
        try:
            with path.open("rb") as fh:
                data = tomllib.load(fh)
        except tomllib.TOMLDecodeError as exc:
            raise UsageError(f"{path}: {exc}") from exc
        return cls(root=root, data=data)

    def _section(self, name: str) -> dict:
        section = self.data.get(name)
        if not isinstance(section, dict):
            raise UsageError(f"{CONFIG_NAME}: missing [{name}] section")
        return section

    def param(self, name: str):
        """A param-* value from definition-of-done.md §Parameters.

        Accepts the bare name; ``param-`` is the rubric's prefix, not a key.
        """
        key = name.removeprefix("param-")
        section = self._section("params")
        if key not in section:
            raise UsageError(
                f"{CONFIG_NAME}: param-{key} is not set. "
                "definition-of-done.md has not fixed a value, and the working "
                "agreement forbids inventing one — set it there first."
            )
        return section[key]

    def option(self, section: str, name: str, default=None):
        """A tool-level knob (thresholds, globs). Unlike param(), may default."""
        value = self.data.get(section, {}).get(name)
        return default if value is None else value

    def documents(self) -> dict[str, str]:
        """Corpus document code (``U``/``S``/``M``/``A``/``P``) → repo-relative path."""
        section = self._section("documents")
        return {k: v for k, v in section.items() if isinstance(v, str)}

    def _codes(self, key: str) -> list[str]:
        codes = self.data.get("documents", {}).get(key)
        if not isinstance(codes, list):
            raise UsageError(f"{CONFIG_NAME}: [documents] has no {key!r} list")
        return codes

    def bodies(self) -> dict[str, str]:
        """``[bodies]``: component code → restructured body path (step 3.7).

        The extraction source for the graph's usage edges. Only bodies that
        exist are listed; an absent entry is the normal "no body yet" state,
        not an error — the emitted graph states which components were scanned
        and which have no body. Keys must be component codes: reference
        documents are read-only and never scanned (C12).
        """
        section = self.data.get("bodies")
        if section is None:
            return {}
        if not isinstance(section, dict):
            raise UsageError(f"{CONFIG_NAME}: [bodies] is not a table")
        components = set(self._codes("components"))
        out: dict[str, str] = {}
        for code, path in section.items():
            if code not in components:
                raise UsageError(
                    f"{CONFIG_NAME}: [bodies] names {code!r}, which is not a "
                    "component code — only the detangle set has bodies to scan"
                )
            if not isinstance(path, str):
                raise UsageError(
                    f"{CONFIG_NAME}: [bodies] {code} wants a path string"
                )
            out[code] = path
        return out

    def registry(self) -> DocumentRegistry:
        """The two input sets (Nick, 2026-08-05), validated as a closed whole.

        Every document code must sit in exactly one of ``components`` and
        ``references`` — a code in neither would make its documents silently
        uncitable (``span-doc-unknown``), and a code in both would let one
        file be counted and not counted at once. Placement names come from
        ``[placements]``, one per component code, because nothing is ever
        placed in a reference document.
        """
        docs = self.documents()
        components = self._codes("components")
        references = self._codes("references")
        if not components:
            raise UsageError(f"{CONFIG_NAME}: [documents] 'components' is empty")

        both = sorted(set(components) & set(references))
        if both:
            raise UsageError(
                f"{CONFIG_NAME}: [documents] lists {both} as both a component "
                "and a reference — a document is in exactly one input set"
            )
        pathless = sorted(set(components + references) - set(docs))
        if pathless:
            raise UsageError(
                f"{CONFIG_NAME}: [documents] names {pathless} with no path"
            )
        unassigned = sorted(set(docs) - set(components) - set(references))
        if unassigned:
            raise UsageError(
                f"{CONFIG_NAME}: [documents] declares {unassigned} in neither "
                "'components' nor 'references' — every document belongs to "
                "one input set"
            )

        placements = self._section("placements")
        unplaced = sorted(set(components) - set(placements))
        if unplaced:
            raise UsageError(
                f"{CONFIG_NAME}: [placements] has no entry for {unplaced}"
            )
        stray = sorted(set(placements) - set(components))
        if stray:
            raise UsageError(
                f"{CONFIG_NAME}: [placements] names {stray}, which are not "
                "component codes — nothing is placed in a reference document"
            )

        return DocumentRegistry(
            components=tuple(components),
            references=tuple(references),
            paths=dict(docs),
            placements={c: str(placements[c]) for c in components},
        )

    def component_docs(self) -> set[str]:
        """Paths of the component blueprints — the only ones C9 counts."""
        return self.registry().component_docs

    def path(self, name: str) -> Path:
        """A declared path, existing or not — for outputs the tool will write."""
        paths = self._section("paths")
        if name not in paths:
            raise UsageError(f"{CONFIG_NAME}: [paths] has no {name!r}")
        return self.root / paths[name]

    def directory(self, name: str) -> Path:
        """A declared input directory, which must actually be one.

        ``Path.glob`` returns nothing for a missing directory rather than
        raising, so a mistyped ``[paths]`` entry would otherwise be reported as
        "0 records, clean" and exit 0 — a false green, which is worse than a
        crash because branch policy believes it.
        """
        path = self.path(name)
        if not path.is_dir():
            raise UsageError(
                f"{CONFIG_NAME}: [paths] {name} = {self._section('paths')[name]!r} "
                f"is not a directory ({path})"
            )
        return path


def find_root(start: Path | None = None) -> Path:
    """Nearest ancestor holding detangle.toml — so the CLI works from anywhere."""
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / CONFIG_NAME).is_file():
            return candidate
    raise UsageError(f"no {CONFIG_NAME} in {here} or any parent")
