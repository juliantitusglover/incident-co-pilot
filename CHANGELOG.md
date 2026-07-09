# Changelog

All notable changes to this project will be documented in this file.

This project uses SemVer-style versions starting at 0.1.0.

The format is inspired by Keep a Changelog.

## Unreleased

### Added

- Added limit/offset pagination support for incident lists.
- Added incident list pagination strategy documentation for v0.2.0 planning.
- Added roadmap and backlog planning docs for v0.2.0 candidates.

### Changed

- GET `/api/v1/incidents` now returns a paginated response envelope instead of a bare array.

### Fixed

### Security

## 0.1.0 - 2026-06-27

### Added

- Initial local/self-hosted Incident Co-Pilot API.
- Incident CRUD API.
- Timeline event API nested under incidents.
- PostgreSQL persistence with Alembic migrations.
- Health endpoints for liveness and readiness.
- FastAPI-generated API docs.
- Docker Compose local runtime.
- README local setup and API examples.
- Security, privacy, and contributing docs.

### Changed

- None yet.

### Fixed

- None yet.

### Security

- Added initial vulnerability reporting and self-hosting security guidance.
