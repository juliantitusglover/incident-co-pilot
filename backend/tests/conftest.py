from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from backend.core.config import Settings, get_settings
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

@pytest.fixture(autouse=True)
def dependency_override_guard(app_fixture, settings_fixture: Settings):
    app_fixture.dependency_overrides[get_settings] = lambda: settings_fixture
    yield

    unexpected_overrides = {
        key: value 
        for key, value in app_fixture.dependency_overrides.items() 
        if key is not get_settings
    }
    assert unexpected_overrides == {}, (
        f"dependency_overrides leaked across test: {list(unexpected_overrides.keys())}"
    )
    
    app_fixture.dependency_overrides.clear()

@pytest.fixture
def client_fixture(app_fixture):
    with TestClient(app_fixture) as client:
        yield client
