# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Architecture section in README with file structure and design decisions

## [0.2.0] - 2025-01-15

### Added
- FastAPI web application with server-side rendered UI
- World map visualization with 27 coffee regions
- Coffee passport — track countries you've had coffee in
- QR code summary sharing
- Annual filter with top-3 countries stats
- PWA manifest and offline caching support
- API endpoints: `/api/stats`, `/api/world`, `/api/streak`, `/health`
- 99% test coverage (117 tests)
- CI pipeline: GitHub Actions for tests and Docker
- Docker image published to GHCR
- Railway deployment configuration

### Changed
- Migrated from CLI (Airtable) to web app (SQLite + FastAPI)
- Split main.py into routes.py + constants.py for modularity

### Fixed
- CORS credentials and CSRF protection
- Input validation and error handling
- Delete endpoint authorization
- Dockerfile healthcheck and DB_PATH configuration

### Security
- CORS credentials handling
- CSRF protection middleware
- Input validation on all endpoints
- Authorized entry deletion

## [0.1.0] - 2024-06-01

### Added
- Initial CLI expense tracker with Airtable integration
- Basic CLI commands: `kohv log`, `kohv today`

[Unreleased]: https://github.com/stennu718/kohvilogi/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/stennu718/kohvilogi/releases/tag/v0.2.0
[0.1.0]: https://github.com/stennu718/kohvilogi/commit/764f518
