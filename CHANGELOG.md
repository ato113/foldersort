# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses
[semantic versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-10-31

### Added
- `tidy suggest` inspects a folder and proposes rules for what is actually in it,
  with `--write` to save them straight to a config file.
- `exclude` option in the config: filenames matching these globs are never touched
  (useful for `*.part` and other half-finished downloads).
- `tidy undo --list` shows recent runs so you can see what would be reversed.
- Coloured output, switched off automatically when piping or when `NO_COLOR` is set.

### Fixed
- `tidy run | head` no longer raises `BrokenPipeError`.

## [0.1.0] - 2026-10-31

### Added
- Rule-based organizing with conditions on extension, glob pattern, size and age.
- Conditions combine within a rule; the first matching rule wins.
- `--dry-run` shows the plan before anything moves.
- Every run is journaled, so `tidy undo` restores files to where they were.
- `tidy init` writes a sample config.
- Conflict policies: rename, skip, overwrite.

[Unreleased]: https://github.com/ato113/tidy/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/ato113/tidy/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ato113/tidy/releases/tag/v0.1.0
