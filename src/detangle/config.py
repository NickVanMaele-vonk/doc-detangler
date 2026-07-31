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

    def component_docs(self) -> set[str]:
        """Paths of the three component blueprints — the only ones C9 counts."""
        docs = self.documents()
        codes = self.data.get("documents", {}).get("components")
        if not isinstance(codes, list) or not codes:
            raise UsageError(f"{CONFIG_NAME}: [documents] has no 'components' list")
        missing = [c for c in codes if c not in docs]
        if missing:
            raise UsageError(
                f"{CONFIG_NAME}: [documents] components names {missing}, "
                "which have no path"
            )
        return {docs[c] for c in codes}

    def path(self, name: str) -> Path:
        paths = self._section("paths")
        if name not in paths:
            raise UsageError(f"{CONFIG_NAME}: [paths] has no {name!r}")
        return self.root / paths[name]


def find_root(start: Path | None = None) -> Path:
    """Nearest ancestor holding detangle.toml — so the CLI works from anywhere."""
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / CONFIG_NAME).is_file():
            return candidate
    raise UsageError(f"no {CONFIG_NAME} in {here} or any parent")
