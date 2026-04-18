# Changelog

## 1.1.0 - 2026-04-18

### Added
- `configure(filename=...)` now wires up both a StreamHandler (terminal) and a FileHandler in one call, with `filemode`, `file_level`, `file_formatter`, and `encoding` kwargs.

### Changed
- Promoted `rich` from an optional extra to a required runtime dependency; removed the `[rich]` install extra and lazy-loading scaffolding.

## 1.0.0 - 2026-04-11

Initial stable release.

### Added

- thread-safe logger and logger-manager mutation paths
- `RichHandler` behind optional `mollog[rich]`
- exception and stack logging via `exc_info`, `stack_info`, and `logger.exception(...)`
- context-local structured fields via `bind_context()`, `scoped_context()`, and related helpers
- top-level `configure()` and `shutdown()` helpers for application setup and teardown
- Zensical documentation site, API guide, behavior notes, and Rich usage guide
- packaging, build, and release workflows for GitHub Actions

### Changed

- reserved formatter fields are protected from `extra` collisions
- queue listener shutdown now drains late-arriving records briefly before exit
- rotating handlers validate invalid configuration eagerly

### Verification

- full test suite passing
- package build and `twine check`
- Zensical site build
