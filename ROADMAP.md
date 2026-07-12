# Roadmap

This roadmap is directional. It is not a commitment or guarantee, and priorities may change as the project evolves.

## Current Release Baseline

The current self-hosted version includes core API usability improvements from v0.2.0 and API access control from v0.3.0.

Current capabilities include:

- FastAPI backend.
- Incident CRUD API.
- Timeline event API nested under incidents.
- Incident detail responses with timeline events.
- Dedicated timeline event read/list endpoints.
- Status and severity filters for incident lists.
- Limit/offset pagination for incident lists.
- PostgreSQL persistence with Alembic migrations.
- Health endpoints for liveness and readiness.
- Docker Compose local runtime.
- Optional shared API key authentication for incident and timeline event routes.
- README setup and API examples.
- Security, privacy, contributing, changelog, and release checklist docs.
- OpenAPI metadata improvements.

## Recent Milestone: v0.3.0

v0.3.0 completed basic API access control for the existing incident timeline API.

It added a small self-hosted security boundary before larger future surfaces such as AI features, a frontend UI, full user accounts, or third-party integrations.

## v0.3.0 Completed Focus Areas

These focus areas were completed for v0.3.0.

### API Access Control

- Added optional shared API key authentication.
- Protected incident and timeline event routes when API auth is enabled.
- Kept health endpoints and generated API docs public for the first API key implementation.

### Documentation and Metadata

- Documented API key usage and security expectations.
- Added OpenAPI security metadata for protected incident routes.
- Added release checklist coverage for auth-enabled smoke testing.

### Operational Polish

- Kept version sources aligned during release prep.
- Kept future hardening items separate from the first API key implementation.

## Near-Term Focus: M9 - Client-Ready API Contracts

The next planning theme is client-readiness API polish for the existing incident and timeline API.

The goal is to make the current API easier and safer for generated clients, scripts, and other non-human consumers without adding new product surfaces.

## M9 Focus Areas

These are planning candidates for M9.

### Timeline Event List Pagination

- Add limit/offset pagination to `GET /api/v1/incidents/{incident_id}/events`.
- Return a response envelope with `items`, `limit`, `offset`, and `total`.
- Keep ordering as `created_at DESC, id DESC`.
- Keep incident detail embedded events unchanged for now.

### OpenAPI and Error Metadata

- Add clearer OpenAPI metadata for auth and error responses on protected routes.
- Add focused examples for timeline event list, read, create, and update flows.
- Keep generated-schema checks targeted rather than broad snapshots.

## Explicit Non-Goals for M9

The following are intentionally out of scope for the current M9 target:

- Hosted service.
- Frontend UI.
- Slack, Jira, Zendesk, or PagerDuty integrations.
- AI summaries or provider calls.
- Full user model or RBAC.
- OAuth or JWT authentication.
- Multiple API keys or automated key rotation.
- Multi-tenancy.
- Search.
- Cursor pagination.
- Broad refactors.
- New event metadata.
- Event date filters unless later justified.

## Later Candidate Themes

- Multiple API keys or key rotation.
- Users and RBAC.
- AI incident summaries.
- Third-party integrations.
- Frontend incident dashboard.
- Richer incident workflow metadata.
- Export and reporting.
- Hosted or cloud deployment options.

## Priority Labels

- `must-have`: needed for the next target release.
- `should-have`: valuable but not release-blocking.
- `could-have`: useful if capacity allows.
- `later`: intentionally deferred.

## Backlog

The detailed issue breakdown lives in `docs/BACKLOG.md`.

That file contains candidate issues grouped by theme, priority labels, and guidance for splitting large items into smaller issues.
