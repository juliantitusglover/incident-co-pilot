# Changelog

All notable changes to this project will be documented in this file.

This project uses SemVer-style versions starting at 0.1.0.

The format is inspired by Keep a Changelog.

## Unreleased

### Added

- Added an operational readiness and diagnostics strategy for M10.
- Added request ID middleware that returns `X-Request-ID` on API responses, including unhandled 500 responses.
- Added central logging configuration using `LOG_LEVEL`.
- Added safe request-completion logging with request IDs.
- Added operations documentation and release-checklist diagnostics checks.

### Changed

### Fixed

### Security

## 0.4.0 - 2026-07-13

### Added

- Added a client-readiness API strategy for M9.

### Changed

- Paginated timeline event list responses with an `{ items, limit, offset, total }` envelope.
- Improved OpenAPI metadata for API key auth errors and timeline event pagination.
- Updated README/API docs for paginated timeline event list responses.

### Fixed

### Security

## 0.3.0 - 2026-07-11

### Added

- Added API access strategy documentation for optional API key authentication.
- Added API auth configuration settings and environment examples.
- Added a reusable API key authentication dependency.
- Added OpenAPI security metadata for protected incident routes.
- Added an API auth smoke check to the release checklist.

### Changed

- Documented optional API key authentication usage and security expectations in README, SECURITY, and API access strategy docs.

### Fixed

### Security

- Protected incident and timeline event API routes with optional API key authentication.

## 0.2.0 - 2026-07-10

### Added

- Added dedicated timeline event list and read endpoints.
- Added timeline event read/list strategy documentation for v0.2.0 planning.
- Added OpenAPI descriptions and examples for incident list pagination.
- Added limit/offset pagination support for incident lists.
- Added incident list pagination strategy documentation for v0.2.0 planning.
- Added roadmap and backlog planning docs for v0.2.0 candidates.

### Changed

- Aligned incident detail nested timeline event ordering with the dedicated event list endpoint.
- GET `/api/v1/incidents` now returns a paginated response envelope instead of a bare array.
- Made the release checklist target-version oriented for future releases.

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
