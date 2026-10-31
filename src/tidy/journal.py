"""Records every move so it can be undone later."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

JOURNAL_DIR = Path.home() / ".local" / "share" / "tidy"
JOURNAL_FILE = JOURNAL_DIR / "journal.jsonl"


@dataclass
class Move:
    source: str
    destination: str
    rule: str


def record(moves: list[Move], journal: Path = JOURNAL_FILE) -> None:
    """Append a batch of moves to the journal."""
    if not moves:
        return
    journal.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "moves": [{"source": m.source, "destination": m.destination, "rule": m.rule} for m in moves],
    }
    with journal.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry) + "\n")


def last_batch(journal: Path = JOURNAL_FILE) -> dict | None:
    """Return the most recent batch, or None when the journal is empty."""
    if not journal.is_file():
        return None
    lines = [line for line in journal.read_text(encoding="utf-8").splitlines() if line.strip()]
    if not lines:
        return None
    return json.loads(lines[-1])


def drop_last(journal: Path = JOURNAL_FILE) -> None:
    """Remove the most recent batch from the journal."""
    if not journal.is_file():
        return
    lines = [line for line in journal.read_text(encoding="utf-8").splitlines() if line.strip()]
    journal.write_text("\n".join(lines[:-1]) + ("\n" if len(lines) > 1 else ""), encoding="utf-8")
