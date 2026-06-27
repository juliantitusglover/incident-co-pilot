# Roadmap

This roadmap is directional. It is not a commitment or guarantee, and priorities may change as the project evolves.

## Current Release

v0.1.0 shipped the initial local/self-hosted API baseline for Incident Co-Pilot.

Current capabilities include:

- FastAPI backend.
- Incident CRUD API.
- Timeline event API nested under incidents.
- Incident detail responses with timeline events.
- Status and severity filters for incident lists.
- PostgreSQL persistence with Alembic migrations.
- Health endpoints for liveness and readiness.
- Docker Compose local runtime.
- README setup and API examples.
- Security, privacy, contributing, changelog, and release checklist docs.
- OpenAPI metadata improvements.

## Near-Term Focus: v0.2.0

The current candidate theme for v0.2.0 is core API usability for the existing incident timeline API.

The goal is to improve the API that already shipped before adding large new surfaces such as AI features, a frontend UI, authentication, or third-party integrations. This keeps the next release focused on making the existing local/self-hosted API easier to use, document, and evolve.

## v0.2.0 Candidate Focus Areas

These are candidate areas for v0.2.0 planning, not guaranteed release contents.

### Incident List Usability

- Choose a pagination strategy.
- Document the current sort order.
- Improve filter ergonomics for status and severity.

### Timeline Event API Usability

- Decide whether dedicated read/list event endpoints are needed.
- Improve docs and examples around event workflows.

### API Contract Clarity

- Improve OpenAPI examples.
- Add clearer error examples.
- Add clearer request and response examples.

### Operational Polish

- Decide how to centralize or document version sources.
- Identify Docker/runtime hardening opportunities.
- Follow through on release checklist learnings.

### Security Posture Planning

- Decide whether the next step is local-only guidance or future API-key authentication.
- Avoid full authentication implementation until the strategy is clear.

## Explicit Non-Goals for v0.2.0

The following are intentionally out of scope for the current v0.2.0 planning target:

- Hosted service.
- Frontend UI.
- Slack, Jira, Zendesk, or PagerDuty integrations.
- AI summaries or provider calls.
- Full user model or RBAC.
- Multi-tenancy.
- Release automation.
- Production deployment hardening.

## Later Candidate Themes

- Authentication or API keys.
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

The future detailed issue breakdown should live in `docs/BACKLOG.md`.

That file does not exist yet. When added, it should contain candidate issues grouped by theme, priority labels, and guidance for splitting large items into smaller issues.
