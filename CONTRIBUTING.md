# Contributing to tidy

Thanks for taking the time to help. Issues and pull requests are both welcome.

## Getting set up

```bash
git clone https://github.com/ato113/tidy
cd tidy
pip install -e ".[dev]"
pytest
```

## Before you open a pull request

- `pytest` passes.
- `ruff check src tests` is clean.
- New behaviour comes with a test. A new rule condition belongs in
  `tests/test_rules.py`; anything about planning or moving files belongs in
  `tests/test_organizer.py`.
- Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/):
  `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.

CI runs the suite on Linux, macOS and Windows against Python 3.9, 3.11 and 3.13.
If it fails on an OS you don't have, say so in the PR and we'll work it out together.

## Adding a rule condition

Conditions live in `Rule` in `src/tidy/rules.py`. Each one is optional and ANDs with
the others. To add one:

1. Add the field to the `Rule` dataclass and parse it in `Rule.from_dict`.
2. Add the check to `Rule.matches` — return `False` as soon as it fails.
3. Add a test that proves it matches *and* that it rejects.
4. Document it in the rule options table in the README.

## Reporting a bug

Tell us what you ran, what you expected, and what happened — ideally with the
relevant part of your `tidy.yaml`. Your OS and `tidy --version` help too.

## AI-assisted contributions

This project accepts them, with two conditions: say so in the pull request, and be
able to explain every line you're submitting. Disclosure goes in the PR description —
a `Co-Authored-By:` trailer on the commit is good practice too.

Undisclosed AI-generated code is the one thing that will get a PR closed on sight.
Not because the tool is the problem, but because a reviewer who can't trust the
description can't trust the diff either.

## A note on scope

tidy moves files according to rules you write. Things that fit: new conditions,
better output, more reliable undo. Things that don't: renaming file contents,
syncing to cloud storage, or anything that needs a daemon. If you're unsure,
open an issue before writing the code.
