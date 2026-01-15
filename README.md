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
Planned command (once tests exist):
- `pytest`

## Error handling
HTTPException will be used for client errors.
Default validation error behaviour won't be changed for now.
- `pytest`

## Database & ORM conventions
### ORM + migrations

ORM: SQLAlchemy 2.x ORM

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

## License
MIT (see `LICENSE`).
