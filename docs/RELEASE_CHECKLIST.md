# Release Checklist

This is a manual release checklist for Incident Co-Pilot.

It is intentionally lightweight for the current local/self-hosted project.

Release automation may be added later.

## Before Starting

- [ ] Confirm the working tree is clean.
- [ ] Confirm the target version.
- [ ] Confirm `CHANGELOG.md` has an entry for the target version.

```bash
TARGET_VERSION=0.3.0
TARGET_TAG=v0.3.0
git status --short
```

## Version Checks

- [ ] Check `backend/pyproject.toml`.
- [ ] Check `backend/core/config.py`.
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
- [ ] With default auth disabled, confirm liveness and incident list requests work without `X-API-Key`.
- [ ] With auth enabled and a disposable test key, confirm health stays public and incident routes require `X-API-Key`.

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
