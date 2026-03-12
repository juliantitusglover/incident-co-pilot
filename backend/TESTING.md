# Testing

## Prerequisites
- Python virtual environment activated
- PostgreSQL running locally
- Test database created:
  - `incident_co_pilot_test`

## Test configuration
The test suite uses the following test database URL by default:

```bash
postgresql+psycopg2://jtg@localhost:5432/incident_co_pilot_test
```

This is provided by the pytest `settings_fixture` in `tests/conftest.py`.

## Running tests

### Run the full suite
```bash
pytest -q
```
### Run unit tests only
```bash
pytest -q tests/unit
```
### Run integration tests only
```bash
pytest -q tests/integration
```

## How integration tests work

Integration tests:

- run Alembic migrations against the test database

- open a fresh database connection per test

- start an outer transaction per test

- use an ORM session joined with join_transaction_mode="create_savepoint"

- roll back the outer transaction after each test

This means writes made during an integration test should not leak into the next test.

## Dependency overrides

Tests use FastAPI dependency overrides to inject:

- test settings

- test database sessions

Override cleanup is enforced so test state does not leak across tests.

## Notes

- If integration tests fail with database connection errors, verify PostgreSQL is running and the test database exists.

- If migrations fail, check Alembic configuration and ensure the database user has permission to create/update schema objects.

**Then run:**
```bash
pytest -q
```