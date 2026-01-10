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
Note: During repo bootstrap, the backend code may not exist yet. Once the FastAPI skeleton is added, the goal is:
- one command to start the API
- env vars via `.env`

Planned workflow:
1) Create environment file:
   - Copy `backend/.env.example` → `backend/.env`
2) Start the API:
   - `uvicorn app.main:app --reload`

Health endpoints will be unversioned `/health/*`, while business APIs will be versioned under `/api/v1/*`.

## Environment variables
Environment variables are defined in `backend/.env.example`.
Local development uses `backend/.env` (not committed).

## Tests
Planned command (once tests exist):
- `pytest`

## License
MIT (see `LICENSE`).
