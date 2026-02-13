from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.core.config import Settings
from backend.main import create_app


@pytest.fixture(scope="session")
def settings_fixture() -> Settings:
    return Settings(
        DATABASE_URL="postgresql+psycopg2://jtg@localhost:5432/incident_co_pilot_test",
        OPENAI_API_KEY="test-key-not-real",
        _env_file=None,
    )


@pytest.fixture(scope="session")
def app_fixture(settings_fixture: Settings):
    app = create_app(settings=settings_fixture)
    yield app
    app.dependency_overrides = {}


@pytest.fixture
def client_fixture(app_fixture):
    with TestClient(app_fixture) as client:
        yield client
