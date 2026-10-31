"""Rule definitions and matching logic."""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path


class RuleError(ValueError):
    """Raised when a rule is malformed."""


def _parse_size(value: str | int) -> int:
    """Convert a human size such as '10MB' into bytes."""
    if isinstance(value, int):
        return value
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*([KMGT]?B?)\s*", str(value), re.IGNORECASE)
    if not match:
        raise RuleError(f"Cannot parse size: {value!r}")
    number, unit = float(match.group(1)), match.group(2).upper().rstrip("B")
    factor = {"": 1, "K": 1024, "M": 1024**2, "G": 1024**3, "T": 1024**4}[unit]
    return int(number * factor)


def _parse_age(value: str | int) -> timedelta:
    """Convert a human age such as '30d' into a timedelta."""
    if isinstance(value, int):
        return timedelta(days=value)
    match = re.fullmatch(r"\s*(\d+)\s*([dwmy])\s*", str(value), re.IGNORECASE)
    if not match:
        raise RuleError(f"Cannot parse age: {value!r}")
    number, unit = int(match.group(1)), match.group(2).lower()
    days = {"d": 1, "w": 7, "m": 30, "y": 365}[unit]
    return timedelta(days=number * days)


@dataclass
class Rule:
    """A single organizing rule.

    A file matches when *every* condition that is set evaluates to true.
    Conditions left as ``None`` are ignored.
    """

    name: str
    target: str
    patterns: list[str] = field(default_factory=list)
    extensions: list[str] = field(default_factory=list)
    larger_than: int | None = None
    smaller_than: int | None = None
    older_than: timedelta | None = None
    newer_than: timedelta | None = None

    @classmethod
    def from_dict(cls, data: dict) -> Rule:
        if "name" not in data:
            raise RuleError("Each rule needs a 'name'.")
        if "target" not in data:
            raise RuleError(f"Rule {data['name']!r} needs a 'target' directory.")

        extensions = [
            ext.lower() if ext.startswith(".") else f".{ext.lower()}"
            for ext in data.get("extensions", [])
        ]

        return cls(
            name=data["name"],
            target=data["target"],
            patterns=list(data.get("patterns", [])),
            extensions=extensions,
            larger_than=_parse_size(data["larger_than"]) if "larger_than" in data else None,
            smaller_than=_parse_size(data["smaller_than"]) if "smaller_than" in data else None,
            older_than=_parse_age(data["older_than"]) if "older_than" in data else None,
            newer_than=_parse_age(data["newer_than"]) if "newer_than" in data else None,
        )

    def matches(self, path: Path, now: datetime | None = None) -> bool:
        """Return True when *path* satisfies every condition of this rule."""
        if not path.is_file():
            return False

        if self.extensions and path.suffix.lower() not in self.extensions:
            return False

        if self.patterns and not any(
            fnmatch.fnmatch(path.name.lower(), pattern.lower()) for pattern in self.patterns
        ):
            return False

        if self.larger_than is not None or self.smaller_than is not None:
            size = path.stat().st_size
            if self.larger_than is not None and size <= self.larger_than:
                return False
            if self.smaller_than is not None and size >= self.smaller_than:
                return False

        if self.older_than is not None or self.newer_than is not None:
            now = now or datetime.now()
            age = now - datetime.fromtimestamp(path.stat().st_mtime)
            if self.older_than is not None and age <= self.older_than:
                return False
            if self.newer_than is not None and age >= self.newer_than:
                return False

        return True
