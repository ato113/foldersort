"""Works out which files move where, and performs the moves."""

from __future__ import annotations

import fnmatch
import shutil
from pathlib import Path

from .config import Config
from .journal import Move


def _unique_destination(destination: Path) -> Path:
    """Return a free path by appending ' (1)', ' (2)', ... to the stem."""
    if not destination.exists():
        return destination
    counter = 1
    while True:
        candidate = destination.with_name(f"{destination.stem} ({counter}){destination.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1


def plan(config: Config) -> list[Move]:
    """Build the list of moves without touching the filesystem.

    The first matching rule wins, so order rules from most to least specific.
    """
    if not config.source.is_dir():
        raise NotADirectoryError(f"Source directory not found: {config.source}")

    files = config.source.rglob("*") if config.recursive else config.source.iterdir()
    target_dirs = {(config.source / rule.target).resolve() for rule in config.rules}

    moves: list[Move] = []
    for path in sorted(files):
        if not path.is_file() or path.name.startswith("."):
            continue
        if any(fnmatch.fnmatch(path.name, pattern) for pattern in config.exclude):
            continue
        # Never re-organize files that already sit in a target directory.
        if any(parent in target_dirs for parent in path.parents):
            continue

        for rule in config.rules:
            if rule.matches(path):
                destination = config.source / rule.target / path.name
                moves.append(Move(str(path), str(destination), rule.name))
                break

    return moves


def apply(moves: list[Move], on_conflict: str = "rename") -> list[Move]:
    """Carry out *moves*, returning the ones that actually happened."""
    performed: list[Move] = []

    for move in moves:
        source = Path(move.source)
        destination = Path(move.destination)

        if not source.exists():
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)

        if destination.exists():
            if on_conflict == "skip":
                continue
            if on_conflict == "rename":
                destination = _unique_destination(destination)

        shutil.move(str(source), str(destination))
        performed.append(Move(str(source), str(destination), move.rule))

    return performed


def undo(moves: list[Move]) -> list[Move]:
    """Move files back to where they came from."""
    restored: list[Move] = []

    for move in reversed(moves):
        current = Path(move.destination)
        original = Path(move.source)

        if not current.exists():
            continue

        original.parent.mkdir(parents=True, exist_ok=True)
        target = _unique_destination(original)
        shutil.move(str(current), str(target))
        restored.append(Move(str(current), str(target), move.rule))

    return restored
