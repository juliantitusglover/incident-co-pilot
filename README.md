# Incident Co-Pilot

Incident Co-Pilot is a lightweight API for capturing incidents, tracking timeline events, and preparing incident summaries.

## Tech stack
- Backend: FastAPI (Python)
- DB: Postgres
- Tests: pytest via uv

## Prerequisites
- Python 3.11+ recommended
- uv for Python dependency management and command execution
- Docker Desktop or Docker Engine with Docker Compose for the Docker workflow
- PostgreSQL for the local non-Docker backend workflow

## Repo structure
- `backend/` — FastAPI API service
- `docs/` — release and project documentation

## Docker quickstart

The Docker workflow uses the root `.env` file. Start by copying the root example file:

```bash
cp .env.example .env
docker compose up --build -d
docker compose run --rm backend alembic -c backend/alembic.ini upgrade head
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

Migrations are manual in the current self-hosted version. `/health/live` can pass before migrations; `/health/ready` should only become healthy after migrations have been applied.

Stop the Docker services:

```bash
docker compose down
```

To reset the local Docker database, remove the Postgres volume:

```bash
docker compose down -v
```

## API docs and health checks

Interactive API docs are available after the backend is running:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Health endpoints are unversioned:

```bash
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
```

Business API routes are versioned under `/api/v1/*`.

## Try the API

These examples assume the backend is running on `http://localhost:8000`. They use `jq` to capture IDs; if you do not have `jq` installed, copy the `id` values from the JSON responses manually.

Create an incident:

```bash
INCIDENT_ID=$(curl -s -X POST http://localhost:8000/api/v1/incidents \
  -H 'Content-Type: application/json' \
  -d '{"title":"Database Outage","description":"Production DB is down","status":"investigating","severity":"sev1"}' | jq -r '.id')
```

List incidents:

```bash
curl http://localhost:8000/api/v1/incidents
```

Get the incident:

```bash
curl http://localhost:8000/api/v1/incidents/$INCIDENT_ID
```

Update the incident status:

```bash
curl -X PATCH http://localhost:8000/api/v1/incidents/$INCIDENT_ID \
  -H 'Content-Type: application/json' \
  -d '{"status":"resolved"}'
```

Add a timeline event:

```bash
EVENT_ID=$(curl -s -X POST http://localhost:8000/api/v1/incidents/$INCIDENT_ID/events \
  -H 'Content-Type: application/json' \
  -d '{"event_type":"update","message":"Restarting the primary node.","occurred_at":"2026-01-23T12:00:00Z"}' | jq -r '.id')
```

View the incident with its events:

```bash
curl http://localhost:8000/api/v1/incidents/$INCIDENT_ID
```

Update the timeline event:

```bash
curl -X PATCH http://localhost:8000/api/v1/incidents/$INCIDENT_ID/events/$EVENT_ID \
  -H 'Content-Type: application/json' \
  -d '{"message":"Primary node restarted."}'
```

Delete the timeline event:

```bash
curl -X DELETE http://localhost:8000/api/v1/incidents/$INCIDENT_ID/events/$EVENT_ID
```

Delete the incident:

```bash
curl -X DELETE http://localhost:8000/api/v1/incidents/$INCIDENT_ID
```

DELETE requests return `204 No Content` on success. Invalid status transitions return `400`; invalid payloads generally return `422` from FastAPI/Pydantic validation.

## Backend: run locally without Docker

Use this workflow when you want to run the API against a local PostgreSQL server instead of Docker Compose.

1. Create the local database:

```bash
createdb incident_copilot
```

2. Create a local backend environment file:

```bash
cp backend/.env.example backend/.env
```

3. From the `backend/` directory, install dependencies and run migrations:

```bash
cd backend
uv sync
uv run alembic upgrade head
```

4. Start the API from the `backend/` directory:

```bash
PYTHONPATH=.. uv run fastapi dev main.py
```

## Environment variables

- Docker Compose uses the root `.env` file copied from `.env.example`.
- Local non-Docker backend settings are documented in `backend/.env.example`.
- Local `.env` files are not committed.

## Tests

The project uses `pytest` with a transactional isolation strategy. 

Ensure you have created the local postgres test database:

```bash
createdb incident_co_pilot_test
```

Run the test suite from the backend directory:

```bash
cd backend
DATABASE_URL=postgresql+psycopg2://$USER@localhost:5432/incident_co_pilot_test uv run pytest -q
uv run pytest -q tests/unit
DATABASE_URL=postgresql+psycopg2://$USER@localhost:5432/incident_co_pilot_test uv run pytest -q tests/integration
```

The `DATABASE_URL` override avoids assuming a project-specific local PostgreSQL username.

## Troubleshooting

- `/health/ready` returns `503` before migrations because the readiness check requires the `incidents` and `timeline_events` tables.
- If port `8000` is already in use, stop the other process or change the backend port mapping/command for your local run.
- To reset the local Docker database, run `docker compose down -v` and then start the services and migrations again.

## Database & Migrations
### 1. Initial Setup

Ensure your local Postgres server is running and create the project database:

```bash
createdb incident_copilot
```

Ensure your .env file in the backend/ directory contains the correct connection string:

```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/incident_copilot
```

### 2. Run Migrations

Alembic migrations must be executed from the backend/ directory to ensure Python package paths resolve correctly for the autogenerate feature.

```bash
# Navigate to the backend directory
cd backend

# Apply all migrations to the latest version (Initialize Schema)
uv run alembic upgrade head
```

### 3. Development Workflow

- Create a new migration: After modifying models in backend/db/models/, generate a new version script:
```bash
uv run alembic revision --autogenerate -m "describe your changes"
```

- Check migration status: Verify which migration version your local DB is currently on:
```bash
uv run alembic current
```

### Reset Local Database

If the database state becomes inconsistent or you wish to wipe all data for a fresh start:

1. Drop the database:
```bash
dropdb incident_copilot
```
2. Re-create the database:

```bash
createdb incident_copilot
```
3. Re-run migrations:

```bash
cd backend
uv run alembic upgrade head
```

> [!IMPORTANT]
> Dropping the database is the recommended reset method because it removes local schema objects and the `alembic_version` tracking table.

### Readiness Check

The application includes a built-in health check to verify database connectivity and schema integrity. You can verify this via the API:

- Endpoint: `GET /health/ready`

- Expected Response:
```JSON
{
  "status": "healthy",
  "connectivity": true,
  "tables_found": [
    "alembic_version",
    "incidents",
    "timeline_events"
  ]
}
```

## Database & ORM conventions
### ORM + migrations

ORM: SQLAlchemy 2.0 ORM

Migrations: Alembic (schema changes are migration-driven, no manual DB edits)

### Primary keys (IDs)

Primary key type: BIGINT (auto-generated id) for all tables.

Sequential numeric keys are preferred over random UUIDs for index/storage efficiency. UUID remains an option later if externally-safe public identifiers or distributed ID generation is needed.

### Timestamps

All timestamps are timestamptz (timezone-aware) in Postgres.

created_at: set by the DB using a default, not by the application.

updated_at: set by the application on every update.

### Enum-ish fields (severity, status)

Stored as constrained strings: TEXT + CHECK constraint restricting allowed values.

Native Postgres ENUM types won't be used initially, to keep schema evolution simpler (CHECK constraints provide similar integrity with more flexibility).

### Table Naming conventions

snake_case everywhere.

Plural table names (e.g. incidents, timeline_events).

## Indexing Decisions

I have implemented three composite/ordered indexes. These were chosen because Postgres does not automatically index foreign keys, and default B-tree indexes do not always optimize for the specific "sort-by-newest" behavior common in dashboards.

1. Incident Timeline Lookup

    Columns: (incident_id, occurred_at)

    Index Name: ix_timeline_incident_occurred

    Justification: This is the most critical index for the "Incident Detail" view. When a user clicks an incident, we need to fetch all events for that specific ID. Adding occurred_at to the index allows Postgres to retrieve the events already sorted by time (Timeline) without a secondary sort operation.

2. Incident Dashboard (Newest First)

    Columns: (created_at DESC)

    Index Name: ix_incidents_created_at

    Justification: The main landing page will almost always show the most recent incidents first. By indexing created_at in descending order, the database can perform a "backward scan" extremely efficiently, ensuring the dashboard loads instantly even as the incidents table grows to thousands of rows.

3. Filtered Incident List

    Columns: (status, created_at)

    Index Name: ix_incidents_status_created_at

    Justification: Users frequently filter by `open` or `investigating` incidents. This composite index follows the Equality-Sort-Range (ESR) rule: it first narrows down the rows by the exact status and then provides them in the pre-sorted order of created_at.

## API Contract & Design Rules

This project follows a "Schema-First" approach using Pydantic for validation and OpenAPI (Swagger) for documentation.

1. Data Types & Formats

    Timestamps: All timestamps are handled as ISO-8601 UTC strings.

        Example: 2026-01-23T15:30:00Z

    Enumerations:

        Status: Strict string-based enum (open, investigating, mitigated, resolved).

        Severity: Strict string-based enum (sev1, sev2, sev3, sev4).

    Strings: All input strings are automatically stripped of leading/trailing whitespace.

2. Validation Constraints

    Incidents:

        title: Required, 1-255 characters.

        description: Required, 1-2000 characters.

    Timeline Events:

        event_type: Required, 1-50 characters.

        message: Required, 3-5000 characters.

        occurred_at: Required (The API does not default to "now"; the client must provide the event time).

3. Response Shapes

    List Views (IncidentListItem): Returns a summary of the incident. Does not include the nested timeline events to optimize performance and bandwidth.

    Detail Views (IncidentRead): Returns the complete incident record, including a nested list of all associated TimelineEvents.

4. Standard Error Responses

The API uses standard FastAPI/OpenAPI error shapes:

    422 Unprocessable Entity: Validation failed (e.g., string too long, missing required field).

    404 Not Found: The requested resource does not exist.

    503 Service Unavailable: Database or critical dependency health check failed.

## Project docs

- [Security policy](SECURITY.md)
- [Privacy notes](PRIVACY.md)
- [Contributing](CONTRIBUTING.md)
- [Roadmap](ROADMAP.md)
- [Backlog](docs/BACKLOG.md)
- [Pagination strategy](docs/PAGINATION_STRATEGY.md)
- [Changelog](CHANGELOG.md)
- [Release checklist](docs/RELEASE_CHECKLIST.md)
- [License](LICENSE)
