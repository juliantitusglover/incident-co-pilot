# Release Checklist

This is a manual release checklist for Incident Co-Pilot.

It is intentionally lightweight for the current local/self-hosted project.

Release automation may be added later.

## Before Starting

- [ ] Confirm the working tree is clean.
- [ ] Confirm the target version.
- [ ] Confirm `CHANGELOG.md` has an entry for the target version.

```bash
TARGET_VERSION=0.6.0
TARGET_TAG=v0.6.0
git status --short
```

## Version Checks

- [ ] Check `backend/pyproject.toml`.
- [ ] Check `backend/core/config.py`.
- [ ] Check `backend/schemas/health.py`.
- [ ] Check `backend/uv.lock`.
- [ ] Check root `.env.example`.
- [ ] Check `backend/.env.example`.

Versioning is not centralized yet. Confirm each version source matches the target version before tagging a release.

## Backend Validation

- [ ] Run the full backend test suite.
- [ ] Run unit tests.
- [ ] Run integration tests.

```bash
cd backend
uv run pytest -q
uv run pytest -q tests/unit
uv run pytest -q tests/integration
```

## Docker Validation

From the repository root:

- [ ] Create a local root `.env` file from the example file.
- [ ] Validate the Docker Compose configuration.
- [ ] Reset local Docker services and volumes.
- [ ] Start Docker services with a fresh build.
- [ ] Run database migrations.
- [ ] Check liveness.
- [ ] Check readiness.
- [ ] Stop Docker services.

```bash
cp .env.example .env
docker compose config
docker compose down -v
docker compose up --build -d
docker compose run --rm backend alembic -c backend/alembic.ini upgrade head
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
docker compose down
```

## Manual API Smoke Test

- [ ] Open http://localhost:8000/docs.
- [ ] Open http://localhost:8000/redoc.
- [ ] Run the README curl examples for the incident and timeline event flow.
- [ ] Confirm timeline event list pagination returns an envelope.
- [ ] Confirm incident report JSON includes report fields and timeline ordering.
- [ ] Confirm incident report Markdown returns `text/markdown` with report sections.
- [ ] With default auth disabled, confirm liveness and incident list requests work without `X-API-Key`.
- [ ] With auth enabled and a disposable test key, confirm health stays public and incident routes require `X-API-Key`.
- [ ] Confirm request IDs are returned and caller-provided request IDs are echoed.
- [ ] Confirm request-completion logs include safe operational fields only.
- [ ] Confirm readiness passes after migrations.

Check request ID behavior:

```bash
curl -i http://localhost:8000/health/live
curl -i -H 'X-Request-ID: release-check' http://localhost:8000/health/live
```

Expected results: both responses include `X-Request-ID`; the second response echoes `X-Request-ID: release-check`.

Check request logging:

```bash
curl http://localhost:8000/health/live
```

Expected result: one request-completion log includes `request_id`, `method`, `path`, `status_code`, and `duration_ms`. Query strings, request bodies, API keys, authorization headers, database URLs, incident descriptions, and timeline messages should not appear in request logs.

Check readiness after migrations:

```bash
curl -i http://localhost:8000/health/ready
```

Expected result: readiness returns `200` after migrations. Liveness can pass before readiness when the database or migrations are not ready.

With default auth disabled, check timeline event list pagination:

```bash
INCIDENT_ID=$(curl -s -X POST http://localhost:8000/api/v1/incidents \
  -H 'Content-Type: application/json' \
  -d '{"title":"Pagination Smoke","description":"Release checklist pagination smoke","status":"open","severity":"sev2"}' | jq -r '.id')
curl -s -X POST http://localhost:8000/api/v1/incidents/$INCIDENT_ID/events \
  -H 'Content-Type: application/json' \
  -d '{"event_type":"update","message":"First pagination smoke event.","occurred_at":"2026-01-23T12:00:00Z"}' >/dev/null
curl -s -X POST http://localhost:8000/api/v1/incidents/$INCIDENT_ID/events \
  -H 'Content-Type: application/json' \
  -d '{"event_type":"update","message":"Second pagination smoke event.","occurred_at":"2026-01-23T12:01:00Z"}' >/dev/null
curl -i "http://localhost:8000/api/v1/incidents/$INCIDENT_ID/events?limit=1&offset=0"
```

Expected result: `200` with `items`, `limit`, `offset`, and `total`; `limit` is `1`, `offset` is `0`, and `total` is at least `2`.

With default auth disabled, check incident report JSON and Markdown export:

```bash
curl http://localhost:8000/api/v1/incidents/$INCIDENT_ID/report
curl -i http://localhost:8000/api/v1/incidents/$INCIDENT_ID/report/markdown
```

Expected JSON report result: `200` with `incident`, `timeline_events`, `timeline_order`, and `timeline_event_count`; `timeline_order` is `created_at_desc_id_desc`.

Expected Markdown report result: `200`, `Content-Type` starts with `text/markdown`, and the body includes `# Incident Report:`, `## Incident`, `## Timeline`, `Timeline order: created_at_desc_id_desc`, and `Timeline event count:`.

If `API_AUTH_ENABLED=true`, include `X-API-Key` on report/export requests as described in the auth smoke checks. Refresh ignored local `.env` files before Docker smoke tests if `docker compose config` renders stale local values.

Start the auth-enabled app from the `backend/` directory:

```bash
API_AUTH_ENABLED=true API_KEY=test-api-key PYTHONPATH=.. uv run fastapi dev main.py
```

Then check the expected status codes from another terminal:

```bash
curl -i http://localhost:8000/health/live
curl -i http://localhost:8000/api/v1/incidents
curl -i http://localhost:8000/api/v1/incidents -H 'X-API-Key: test-api-key'
```

Expected results: liveness returns `200`, incident list without a key returns `401`, and incident list with the test key returns `200`.

## Documentation Review

- [ ] Review `README.md`.
- [ ] Review `CHANGELOG.md`.
- [ ] Review `SECURITY.md`.
- [ ] Review `PRIVACY.md`.
- [ ] Review `CONTRIBUTING.md`.
- [ ] Review `LICENSE`.
- [ ] Review root `.env.example`.
- [ ] Review `backend/.env.example`.

## Release Notes and Tagging

- [ ] Prepare release notes for `$TARGET_TAG` from `CHANGELOG.md`.
- [ ] Create a git tag for `$TARGET_TAG` only when ready.
- [ ] Do not tag from a dirty working tree.

Suggested tag format:

```bash
git tag "$TARGET_TAG"
```

## After Release

- [ ] Check the released README links.
- [ ] Check the Docker quickstart from a fresh clone if possible.
- [ ] Move released changelog items out of `Unreleased` when cutting the release.
