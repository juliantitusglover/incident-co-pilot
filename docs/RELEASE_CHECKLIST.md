# Release Checklist

This is a manual release checklist for Incident Co-Pilot.

It is intentionally lightweight for the current local/self-hosted project.

Release automation may be added later.

## Before Starting

- [ ] Confirm the working tree is clean.
- [ ] Confirm the target version.
- [ ] Confirm `CHANGELOG.md` has an entry for the target version.

```bash
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

- [ ] Prepare release notes from `CHANGELOG.md`.
- [ ] Create a git tag only when ready.
- [ ] Do not tag from a dirty working tree.

Suggested tag format:

```bash
git tag v0.1.0
```

## After Release

- [ ] Check the released README links.
- [ ] Check the Docker quickstart from a fresh clone if possible.
- [ ] Move released changelog items out of `Unreleased` when cutting the release.
