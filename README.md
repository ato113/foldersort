# foldersort

**Organize a folder with rules you can read.**

[![CI](https://github.com/ato113/foldersort/actions/workflows/ci.yml/badge.svg)](https://github.com/ato113/foldersort/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Your Downloads folder has 400 files in it. `foldersort` sorts them into folders based on
a YAML file you write once — and puts everything back if you don't like the result.

```
$ foldersort run --dry-run

12 file(s) to move:

  invoice-march.pdf        ->  Documents/      [Documents]
  Screenshot 2026-03-14.png ->  Images/Screenshots/   [Screenshots]
  ubuntu-24.04.iso         ->  Review/         [Large and forgotten]
  ...

Dry run — nothing was moved. Drop --dry-run to apply.
```

## Why another file organizer?

Most of them hardcode the categories, so the moment your workflow differs from the
author's you're out of luck. `foldersort` has four things they usually miss:

- **It writes the rules for you.** `foldersort suggest` looks at what's actually in the
  folder and hands you a working config. No staring at a blank YAML file.
- **Conditions combine.** A rule can match on extension *and* size *and* age at once —
  "PDFs larger than 50 MB that I haven't touched in six months" is one rule.
- **Dry run by default in the docs.** You always see the plan before anything moves.
- **Real undo.** Every run is journaled, so `foldersort undo` puts every file back where it was.

## Install

```bash
pip install foldersort
```

The command is `foldersort`, and `fsort` is a shorter alias for it.

Or from source:

```bash
git clone https://github.com/ato113/foldersort
cd foldersort
pip install -e .
```

## Quick start

```bash
foldersort suggest ~/Downloads --write   # look at the folder, write a config for it
foldersort run --dry-run                 # see what would happen
foldersort run                           # do it (asks for confirmation)
foldersort undo                          # changed your mind
```

Prefer to start from a blank slate? `foldersort init` writes a commented sample config.

### Let foldersort write the rules

`foldersort suggest` scans a folder and proposes a rule for each group it finds — including
one for screenshots, which it recognises by name in several languages.

```
$ foldersort suggest ~/Downloads

Found 6 rule(s) that would fit /home/you/Downloads:

  Screenshots  (14 file(s))
  Images       (31 file(s))
  Documents    (22 file(s))
  Archives     (5 file(s))
  Audio        (9 file(s))
  BLEND files  (3 file(s))
```

Add `--write` to save it as `foldersort.yaml`. It's a normal config file — edit it freely.

## Configuration

```yaml
source: ~/Downloads
recursive: false        # look inside subfolders too
on_conflict: rename     # rename | skip | overwrite

rules:
  # The first matching rule wins, so put specific rules first.
  - name: Screenshots
    target: Images/Screenshots
    patterns: ["screenshot*", "Ekran*"]

  - name: Images
    target: Images
    extensions: [jpg, png, gif, webp, heic]

  - name: Large and forgotten
    target: Review
    larger_than: 500MB
    older_than: 90d
```

### Rule options

| Key | Meaning | Example |
|-----|---------|---------|
| `name` | Shown in the plan output. Required. | `Invoices` |
| `target` | Destination, relative to `source`. Required. | `Documents/Invoices` |
| `extensions` | File extensions, with or without the dot. | `[pdf, docx]` |
| `patterns` | Glob patterns against the filename, case-insensitive. | `["invoice*", "*-receipt"]` |
| `larger_than` / `smaller_than` | Size thresholds. | `500MB`, `10KB` |
| `older_than` / `newer_than` | Age by last modification. | `90d`, `2w`, `1y` |

Top-level options: `source`, `recursive`, `on_conflict` (`rename` / `skip` / `overwrite`)
and `exclude` — a list of globs that are never touched, which is where half-finished
downloads like `*.part` and `*.crdownload` belong.

A file matches a rule only when **every** condition set on that rule is true.
Conditions you leave out are ignored.

## Good to know

- Hidden files (starting with `.`) are never touched.
- Files already inside a target folder are left alone, so running twice is safe.
- `foldersort undo` reverses the most recent run only; `foldersort undo --list` shows the history.
  The journal lives in `~/.local/share/foldersort/journal.jsonl`.
- Output is coloured when you're at a terminal and plain when you pipe it.
  `NO_COLOR=1` turns it off everywhere.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check src tests
```

## Contributing

Issues and pull requests are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for the
setup, the checklist, and how to add a new rule condition.

AI-assisted contributions are fine as long as you disclose them in the pull request
and can explain what you're submitting.

## License

MIT — see [LICENSE](LICENSE).
