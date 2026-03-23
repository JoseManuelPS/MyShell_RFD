# Changelog

All notable changes relevant to users, reviewers, or distribution are documented in this file.

This project follows Semantic Versioning.

## v1.2.0 - 2026-03-23

### Added
- Support for Terragrunt configuration execution inside the shell.

### Changed
- Streamlined output configuration headers, shifting from `## Section: Name` to `## Name`.

### Fixed
- Error redirection to `/dev/null` for `rosa` completion to silence missing CLI outputs.
- Corrected `.local/bin/env` evaluation path for `nvm` initialization.
