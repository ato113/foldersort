"""Minimal terminal colouring.

Colour is switched off when stdout is not a terminal, when NO_COLOR is set,
or when TERM says the terminal is dumb — so piping output stays clean.
"""

from __future__ import annotations

import os
import sys

_CODES = {
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "cyan": "\033[36m",
}
_RESET = "\033[0m"


def supports_color(stream=None) -> bool:
    stream = stream or sys.stdout
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    return hasattr(stream, "isatty") and stream.isatty()


def paint(text: str, *styles: str, stream=None) -> str:
    """Wrap *text* in ANSI styles, or return it unchanged when colour is off."""
    if not styles or not supports_color(stream):
        return text
    prefix = "".join(_CODES[s] for s in styles if s in _CODES)
    return f"{prefix}{text}{_RESET}" if prefix else text
