# Roadmap

This roadmap is directional. It is not a commitment or guarantee, and priorities may change as the project evolves.

## Current Release Baseline

v0.2.0 shipped core API usability improvements for the local/self-hosted API.

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

## Near-Term Focus: v0.3.0

The current release-prep theme for v0.3.0 is basic API access control for the existing incident timeline API.

The goal is to add a small self-hosted security boundary before adding larger surfaces such as AI features, a frontend UI, full user accounts, or third-party integrations.

## v0.3.0 Focus Areas

These are release-prep focus areas for v0.3.0.

### API Access Control

- Added optional shared API key authentication.
- Protected incident and timeline event routes when API auth is enabled.
- Kept health endpoints and generated API docs public for the first API key implementation.

### Documentation and Metadata

- Documented API key usage and security expectations.
- Added OpenAPI security metadata for protected incident routes.
- Added release checklist coverage for auth-enabled smoke testing.

### Operational Polish

- Keep version sources aligned during release prep.
- Keep future hardening items separate from the first API key implementation.

## Explicit Non-Goals for v0.3.0

The following are intentionally out of scope for the current v0.3.0 release target:

- Hosted service.
- Frontend UI.
- Slack, Jira, Zendesk, or PagerDuty integrations.
- AI summaries or provider calls.
- Full user model or RBAC.
- Multiple API keys or automated key rotation.
- Multi-tenancy.
- Release automation.
- Production deployment hardening.

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
