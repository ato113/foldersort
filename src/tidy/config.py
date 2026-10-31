"""Loading and validating the YAML configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

from .rules import Rule, RuleError

DEFAULT_CONFIG_NAMES = ("tidy.yaml", "tidy.yml", ".tidy.yaml")


class ConfigError(ValueError):
    """Raised when the configuration file cannot be used."""


@dataclass
class Config:
    source: Path
    rules: list[Rule]
    recursive: bool = False
    on_conflict: str = "rename"  # rename | skip | overwrite
    exclude: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, path: Path) -> Config:
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise ConfigError(f"{path} is not valid YAML: {exc}") from exc
        except OSError as exc:
            raise ConfigError(f"Cannot read {path}: {exc}") from exc

        if not isinstance(raw, dict):
            raise ConfigError(f"{path} must contain a YAML mapping at the top level.")

        if "source" not in raw:
            raise ConfigError("Config needs a 'source' directory.")
        if not raw.get("rules"):
            raise ConfigError("Config needs at least one entry under 'rules'.")

        on_conflict = raw.get("on_conflict", "rename")
        if on_conflict not in ("rename", "skip", "overwrite"):
            raise ConfigError(
                f"on_conflict must be rename, skip or overwrite — got {on_conflict!r}."
            )

        try:
            rules = [Rule.from_dict(entry) for entry in raw["rules"]]
        except RuleError as exc:
            raise ConfigError(str(exc)) from exc

        exclude = raw.get("exclude", [])
        if not isinstance(exclude, list):
            raise ConfigError("'exclude' must be a list of glob patterns.")

        return cls(
            source=Path(raw["source"]).expanduser(),
            rules=rules,
            recursive=bool(raw.get("recursive", False)),
            on_conflict=on_conflict,
            exclude=list(exclude),
        )


def find_config(start: Path | None = None) -> Path | None:
    """Look for a config file in *start* (or the working directory)."""
    start = start or Path.cwd()
    for name in DEFAULT_CONFIG_NAMES:
        candidate = start / name
        if candidate.is_file():
            return candidate
    return None
