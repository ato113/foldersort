# tidy

**Organize a folder with rules you can read.**

[![CI](https://github.com/ato113/tidy/actions/workflows/ci.yml/badge.svg)](https://github.com/ato113/tidy/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Your Downloads folder has 400 files in it. `tidy` sorts them into folders based on
a YAML file you write once — and puts everything back if you don't like the result.

```
$ tidy run --dry-run

12 file(s) to move:

  invoice-march.pdf        ->  Documents/      [Documents]
  Screenshot 2026-03-14.png ->  Images/Screenshots/   [Screenshots]
  ubuntu-24.04.iso         ->  Review/         [Large and forgotten]
  ...

Dry run — nothing was moved. Drop --dry-run to apply.
```

## Why another file organizer?

Most of them hardcode the categories, so the moment your workflow differs from the
author's you're out of luck. `tidy` has three things they usually miss:

- **Conditions combine.** A rule can match on extension *and* size *and* age at once —
  "PDFs larger than 50 MB that I haven't touched in six months" is one rule.
- **Dry run by default in the docs.** You always see the plan before anything moves.
- **Real undo.** Every run is journaled, so `tidy undo` puts every file back where it was.

## Install

```bash
pip install tidy-cli
```

Or from source:

```bash
git clone https://github.com/ato113/tidy
cd tidy
pip install -e .
```

## Quick start

```bash
tidy init              # writes a sample tidy.yaml you can edit
tidy run --dry-run     # see what would happen
tidy run               # do it (asks for confirmation)
tidy undo              # changed your mind
```

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

A file matches a rule only when **every** condition set on that rule is true.
Conditions you leave out are ignored.

## Good to know

- Hidden files (starting with `.`) are never touched.
- Files already inside a target folder are left alone, so running twice is safe.
- `tidy undo` reverses the most recent run only. The journal lives in
  `~/.local/share/tidy/journal.jsonl`.

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check src tests
```

## Contributing

Issues and pull requests are welcome. If you're adding a rule condition, please add a
test for it in `tests/test_rules.py`.

## License

MIT — see [LICENSE](LICENSE).
