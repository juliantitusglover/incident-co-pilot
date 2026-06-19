# Contributing

Thanks for helping improve Incident Co-Pilot.

## Before You Start

Read `README.md` for the current project setup, API examples, and database workflow.

Use small, focused pull requests. If a change is ambiguous or broad, open an issue or discussion first.

## Local Setup

The Docker quickstart is documented in `README.md`.

The local backend workflow without Docker is also documented in `README.md`.

## Development Guidelines

Keep API behavior covered by tests.

Keep validation schema-first where appropriate, using Pydantic schemas and OpenAPI behavior as the public contract.

Follow the existing FastAPI, Pydantic, SQLAlchemy, and Alembic patterns in the repository.

Avoid broad refactors in feature pull requests.

## Testing

Run tests from the backend directory:

```bash
cd backend
pytest -q
pytest -q tests/unit
pytest -q tests/integration
```

Migration or persistence changes should also run the relevant Alembic and Docker checks described in `README.md`.

## Documentation

Update `README.md`, environment examples, and API examples when behavior changes.

## Security Issues

Follow `SECURITY.md` for vulnerability reporting. Do not disclose vulnerabilities publicly.

## Pull Request Checklist

- Scope is small and focused.
- Tests were run, or the reason they were not run is documented.
- Documentation was updated if behavior changed.
- No secrets, real API keys, or local `.env` files are committed.
- Migrations are included when schema changes are made.
