"""Command line interface."""

from __future__ import annotations

import argparse
import contextlib
import os
import sys
from pathlib import Path

from . import __version__, journal, organizer, suggest
from .config import Config, ConfigError, find_config
from .journal import Move
from .ui import paint


def _resolve_config(argument: str | None) -> Path:
    if argument:
        path = Path(argument).expanduser()
        if not path.is_file():
            raise ConfigError(f"Config file not found: {path}")
        return path

    found = find_config()
    if found is None:
        raise ConfigError(
            "No config file found. Create a tidy.yaml here, or run 'tidy init' to start from a sample."
        )
    return found


def _print_moves(moves: list[Move], source: Path) -> None:
    width = max((len(Path(m.source).name) for m in moves), default=0)
    for move in moves:
        name = Path(move.source).name
        target = Path(move.destination).parent
        with contextlib.suppress(ValueError):
            target = target.relative_to(source)
        print(
            f"  {name:<{width}}  "
            f"{paint('->', 'dim')}  "
            f"{paint(f'{target}/', 'cyan')}   "
            f"{paint(f'[{move.rule}]', 'dim')}"
        )


def cmd_run(args: argparse.Namespace) -> int:
    config = Config.load(_resolve_config(args.config))
    moves = organizer.plan(config)

    if not moves:
        print(paint("Nothing to organize — every file is already in place.", "green"))
        return 0

    print(paint(f"{len(moves)} file(s) to move:", "bold") + "\n")
    _print_moves(moves, config.source)

    if args.dry_run:
        print(paint("\nDry run — nothing was moved. Drop --dry-run to apply.", "yellow"))
        return 0

    if not args.yes:
        answer = input(f"\nMove {len(moves)} file(s)? [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            print("Cancelled.")
            return 0

    performed = organizer.apply(moves, config.on_conflict)
    journal.record(performed)
    print(paint(f"\nMoved {len(performed)} file(s).", "green") + " Run 'tidy undo' to reverse this.")
    return 0


def cmd_undo(args: argparse.Namespace) -> int:
    if args.list:
        batches = journal.history()
        if not batches:
            print("No runs recorded yet.")
            return 0
        print(paint("Recent runs:", "bold") + "\n")
        for index, batch in enumerate(batches, start=1):
            marker = paint("<- 'tidy undo' reverses this", "dim") if index == 1 else ""
            count = len(batch["moves"])
            print(f"  {batch['timestamp']}   {count:>3} file(s)  {marker}")
        return 0

    batch = journal.last_batch()
    if batch is None:
        print("Nothing to undo.")
        return 0

    moves = [Move(**entry) for entry in batch["moves"]]
    print(f"Undoing {len(moves)} move(s) from {batch['timestamp']}.")

    if not args.yes:
        answer = input("Continue? [y/N] ").strip().lower()
        if answer not in ("y", "yes"):
            print("Cancelled.")
            return 0

    restored = organizer.undo(moves)
    journal.drop_last()
    print(f"Restored {len(restored)} file(s).")
    return 0


SAMPLE_CONFIG = """\
# Where to tidy. Use ~ for your home directory.
source: ~/Downloads

# Look inside subdirectories too.
recursive: false

# What to do when a file of that name already exists in the target:
# rename (default), skip, or overwrite.
on_conflict: rename

# Filenames matching these globs are never touched.
exclude:
  - "*.part"
  - "*.crdownload"
  - "*.tmp"

# The first matching rule wins, so put specific rules first.
rules:
  - name: Screenshots
    target: Images/Screenshots
    patterns: ["screenshot*", "Screen Shot*", "Ekran*"]

  - name: Images
    target: Images
    extensions: [jpg, jpeg, png, gif, webp, heic, svg]

  - name: Documents
    target: Documents
    extensions: [pdf, doc, docx, odt, txt, md, rtf]

  - name: Spreadsheets
    target: Documents/Spreadsheets
    extensions: [xls, xlsx, csv, ods]

  - name: Archives
    target: Archives
    extensions: [zip, tar, gz, bz2, xz, rar, 7z]

  - name: Installers
    target: Installers
    extensions: [dmg, pkg, exe, msi, deb, rpm, appimage]

  - name: Video
    target: Video
    extensions: [mp4, mkv, mov, avi, webm]

  - name: Audio
    target: Audio
    extensions: [mp3, wav, flac, m4a, ogg]

  # Conditions combine: a large old file, whatever its type.
  - name: Large and forgotten
    target: Review
    larger_than: 500MB
    older_than: 90d
"""


def cmd_init(args: argparse.Namespace) -> int:
    destination = Path(args.path or "tidy.yaml")
    if destination.exists() and not args.force:
        print(f"{destination} already exists. Use --force to overwrite.")
        return 1
    destination.write_text(SAMPLE_CONFIG, encoding="utf-8")
    print(f"Wrote {destination}. Edit it, then run 'tidy run --dry-run'.")
    return 0


def cmd_suggest(args: argparse.Namespace) -> int:
    source = Path(args.source or ".").expanduser()
    suggestions = suggest.scan(source, recursive=args.recursive)

    if not suggestions:
        print("Nothing to suggest — no files found worth a rule.")
        return 0

    if args.write:
        destination = Path(args.write)
        if destination.exists() and not args.force:
            print(f"{destination} already exists. Use --force to overwrite.")
            return 1
        destination.write_text(suggest.to_config(source, suggestions), encoding="utf-8")
        print(f"Wrote {destination} with {len(suggestions)} rule(s).")
        print("Review it, then run 'tidy run --dry-run'.")
        return 0

    print(paint(f"Found {len(suggestions)} rule(s) that would fit {source}:", "bold") + "\n")
    for item in suggestions:
        print(f"  {paint(item.name, 'cyan')}  {paint(f'({item.count} file(s))', 'dim')}")
    print("\n" + paint("--- suggested config ---", "dim"))
    print(suggest.to_config(source, suggestions))
    print(paint("Save it with: tidy suggest --write tidy.yaml", "dim"))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tidy",
        description="Organize a folder with rules you can read.",
    )
    parser.add_argument("--version", action="version", version=f"tidy {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="organize files according to the config")
    run.add_argument("-c", "--config", help="path to the config file")
    run.add_argument("-n", "--dry-run", action="store_true", help="show the plan without moving anything")
    run.add_argument("-y", "--yes", action="store_true", help="skip the confirmation prompt")
    run.set_defaults(func=cmd_run)

    undo = subparsers.add_parser("undo", help="reverse the most recent run")
    undo.add_argument("-y", "--yes", action="store_true", help="skip the confirmation prompt")
    undo.add_argument("-l", "--list", action="store_true", help="show recent runs instead of undoing")
    undo.set_defaults(func=cmd_undo)

    sug = subparsers.add_parser("suggest", help="propose rules based on what is in a folder")
    sug.add_argument("source", nargs="?", help="folder to inspect (default: current directory)")
    sug.add_argument("-r", "--recursive", action="store_true", help="look inside subfolders")
    sug.add_argument("-w", "--write", nargs="?", const="tidy.yaml", help="write the config to a file")
    sug.add_argument("-f", "--force", action="store_true", help="overwrite an existing file")
    sug.set_defaults(func=cmd_suggest)

    init = subparsers.add_parser("init", help="write a sample config file")
    init.add_argument("path", nargs="?", help="where to write it (default: tidy.yaml)")
    init.add_argument("-f", "--force", action="store_true", help="overwrite an existing file")
    init.set_defaults(func=cmd_init)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (ConfigError, NotADirectoryError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        return 130
    except BrokenPipeError:
        # The reader went away (e.g. `tidy run | head`). Silence the shutdown
        # warning Python would otherwise print when it flushes stdout.
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
        return 0


if __name__ == "__main__":
    sys.exit(main())
