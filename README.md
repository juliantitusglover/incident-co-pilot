# Incident Co-Pilot

Incident Co-Pilot is a lightweight incident timeline capture and summarisation tool.

## Tech stack
- Backend: FastAPI (Python)
- DB: Postgres
- Frontend: Vite + React
- Tests: pytest 

## Repo structure
- `backend/` — FastAPI API service
- `frontend/` — Vite/React UI

## Prerequisites
- Python 3.11+ recommended
- Node.js 20.19+ (or 22.12+) recommended for Vite 7+ tooling

## Backend: run locally (API)
Planned workflow:
1) Create environment file:
   - Copy `backend/.env.example` → `backend/.env`
2) Start the API:
   - `fastapi dev backend/main.py`

Health endpoints will be unversioned `/health/*`, while business APIs will be versioned under `/api/v1/*`.

## Environment variables
Environment variables are defined in `backend/.env.example`.
Local development uses `backend/.env` (not committed).

## Tests

The project uses `pytest` with a transactional isolation strategy. 

### 1. Requirements
Ensure you have created the local postgres test database:

```bash
createdb incident_co_pilot_test
```

### 2. Run Tests

```bash
pytest
```

## Error handling
HTTPException will be used for client errors.
Default validation error behaviour won't be changed for now.
- `pytest`

## Database & Migrations
### 1. Initial Setup

Ensure your local Postgres server is running and create the project database:

```bash
createdb incident_co_pilot
```

Ensure your .env file in the backend/ directory contains the correct connection string:

```
DATABASE_URL=postgresql://jtg@localhost:5432/incident_co_pilot
```

### 2. Run Migrations

Alembic migrations must be executed from the backend/ directory to ensure Python package paths resolve correctly for the autogenerate feature.

```bash
# Navigate to the backend directory
cd backend

# Apply all migrations to the latest version (Initialize Schema)
alembic upgrade head
```

### 3. Development Workflow

- Create a new migration: After modifying models in backend/db/models/, generate a new version script:
```bash
alembic revision --autogenerate -m "describe your changes"
```

- Check migration status: Verify which migration version your local DB is currently on:
```bash
alembic current
```

### Reset Local Database

If the database state becomes inconsistent or you wish to wipe all data for a fresh start:

1. Drop the database:
```bash
dropdb incident_co_pilot
```
2. Re-create the database:

```bash
createdb incident_co_pilot
```
3. Re-run migrations:

```bash
cd backend
alembic upgrade head
```
[!IMPORTANT]:Dropping the database is the recommended reset method because it also removes custom PostgreSQL types (like the severity and status Enums) and the alembic_version tracking table.

### Readiness Check

The application includes a built-in health check to verify database connectivity and schema integrity. You can verify this via the API:

- Endpoint: GET /ready

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

    Justification: Users frequently filter by "Open" or "Investigating" incidents. This composite index follows the Equality-Sort-Range (ESR) rule: it first narrows down the rows by the exact status and then provides them in the pre-sorted order of created_at.

## API Contract & Design Rules

This project follows a "Schema-First" approach using Pydantic for validation and OpenAPI (Swagger) for documentation.

1. Data Types & Formats

    Timestamps: All timestamps are handled as ISO-8601 UTC strings.

        Example: 2026-01-23T15:30:00Z

    Enumerations:

        Status: Strict string-based enum (IDENTIFIED, INVESTIGATING, DEGRADED, RESOLVED).

        Severity: Strict string-based enum (SEV1, SEV2, SEV3, SEV4).

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

## License
MIT (see `LICENSE`).
