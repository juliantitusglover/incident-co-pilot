# Operations

This document is practical operations guidance for local and self-hosted Incident Co-Pilot deployments. It covers startup, configuration, health checks, request IDs, request logs, and safe troubleshooting.

## Runtime Configuration

- `APP_ENV`: names the runtime environment.
- `LOG_LEVEL`: controls backend logger verbosity. Invalid values fall back to `INFO`.
- `DEBUG`: enables debug behavior. Use `DEBUG=true` carefully because SQLAlchemy SQL echo can expose sensitive operational or incident data in logs.
- `API_VERSION`: version reported by the API and liveness endpoint.
- `DATABASE_URL`: SQLAlchemy database connection string.
- `CORS_ORIGINS`: comma-separated list of allowed browser origins.
- `API_AUTH_ENABLED`: enables API key checks for incident and timeline routes when `true`.
- `API_KEY`: shared API key used when API authentication is enabled.

Real `.env` values should not be committed. Docker Compose reads the root `.env`; local non-Docker runs read `backend/.env`. Ignored local `.env` files can override the values rendered by `docker compose config`, so check local files when runtime settings look unexpected.

## Starting With Docker Compose

From the repository root:

```bash
cp .env.example .env
docker compose up --build -d
docker compose run --rm backend alembic -c backend/alembic.ini upgrade head
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

The backend Docker healthcheck uses `/health/live`, not `/health/ready`. That means the container can be live before the database schema is ready for API traffic.

## Starting Without Docker

Use this workflow when running the API against a local PostgreSQL server:

```bash
createdb incident_copilot
cp backend/.env.example backend/.env
cd backend
uv sync
uv run alembic upgrade head
PYTHONPATH=.. uv run fastapi dev main.py
```

Then check the API from another terminal:

```bash
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

## Migrations And Readiness

Readiness depends on database connectivity and required tables. Run migrations before expecting `/health/ready` to pass.

`/health/live` can pass while `/health/ready` fails. Treat that as a signal to check database connectivity, credentials, and whether migrations have been applied.

## Health Checks

- `GET /health/live`: confirms the API process is alive and returns the API version. It does not require database readiness.
- `GET /health/ready`: checks database connectivity and required tables.
- Use `/health/live` for container liveness.
- Use `/health/ready` before sending real traffic or running API smoke checks.

## Request IDs

Send `X-Request-ID` when debugging if you already have one. If the header is omitted, blank, or too long, the app generates a request ID.

The app returns `X-Request-ID` on responses, including handled errors and unhandled `500` responses. Use request IDs in bug reports and support notes instead of sharing sensitive payloads.

## Request Logging

Request-completion logs include:

- `request_id`
- `method`
- `path`
- `status_code`
- `duration_ms`

Request logs intentionally exclude query strings, request bodies, response bodies, headers, API keys, authorization headers, database URLs, incident descriptions, and timeline messages.

Use `request_id` to correlate a response with request-completion logs.

## Troubleshooting

- `/health/live` fails: confirm the backend process or container is running, the port mapping is correct, and the app started without import or configuration errors.
- `/health/ready` fails: confirm Postgres is reachable, `DATABASE_URL` is correct, and migrations have created the required tables.
- Docker Compose is running but the API is not ready: remember the backend healthcheck uses liveness; run `/health/ready` after migrations before API smoke checks.
- Unexpected `API_VERSION` or settings appear: inspect ignored local `.env` files and run `docker compose config` to see rendered Compose values.
- API returns `401` when `API_AUTH_ENABLED=true`: send the configured `X-API-Key` on incident and timeline API routes. Health and generated docs remain public.
- Finding logs by request: copy the response `X-Request-ID` and search request-completion logs for the same value.
- `DEBUG=true`: SQL echo can expose sensitive data. Prefer `LOG_LEVEL=debug` for backend logger verbosity and keep `DEBUG=false` unless SQL-level diagnostics are necessary.

## Safe Debugging And Issue Reports

When reporting an issue, share the status code, endpoint path, `X-Request-ID`, timestamp, and high-level symptoms.

Do not share API keys, database URLs, authorization headers, request or response bodies, incident descriptions, or timeline messages unless they have been intentionally redacted.
