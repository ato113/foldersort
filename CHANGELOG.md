# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project uses
[semantic versioning](https://semver.org/).

## [Unreleased]

## [0.2.0] - 2026-10-31

### Changed
- **Renamed from `tidy` to `foldersort`.** The old command name collided with
  HTML Tidy, which ships with macOS and is in the Debian and Ubuntu repositories,
  so a `tidy` on your PATH could have been either tool. The command is now
  `foldersort`, with `fsort` as a shorter alias, and the package is `foldersort`
  on PyPI. Config files are `foldersort.yaml`; the journal moved to
  `~/.local/share/foldersort/`.

### Added
- `foldersort suggest` inspects a folder and proposes rules for what is actually in it,
  with `--write` to save them straight to a config file.
- `exclude` option in the config: filenames matching these globs are never touched
  (useful for `*.part` and other half-finished downloads).
- `foldersort undo --list` shows recent runs so you can see what would be reversed.
- Coloured output, switched off automatically when piping or when `NO_COLOR` is set.

### Fixed
- `foldersort run | head` no longer raises `BrokenPipeError`.

## [0.1.0] - 2026-10-31

### Added
- Rule-based organizing with conditions on extension, glob pattern, size and age.
- Conditions combine within a rule; the first matching rule wins.
- `--dry-run` shows the plan before anything moves.
- Every run is journaled, so `foldersort undo` restores files to where they were.
- `foldersort init` writes a sample config.
- Conflict policies: rename, skip, overwrite.

[Unreleased]: https://github.com/ato113/foldersort/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/ato113/foldersort/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ato113/foldersort/releases/tag/v0.1.0
