import pytest

from backend.core.config import get_settings


AUTH_HEADER = {"X-API-Key": "test-api-key"}
WRONG_AUTH_HEADER = {"X-API-Key": "wrong-key"}


@pytest.fixture
def auth_enabled(client_fixture, settings_fixture):
    auth_settings = settings_fixture.model_copy(
        update={
            "API_AUTH_ENABLED": True,
            "API_KEY": "test-api-key",
        }
    )
    client_fixture.app.dependency_overrides[get_settings] = lambda: auth_settings
    yield
    client_fixture.app.dependency_overrides[get_settings] = lambda: settings_fixture


def _incident_payload():
    return {
        "title": "Auth Test Incident",
        "description": "Incident used for API key auth route tests",
        "status": "open",
        "severity": "sev2",
    }


def _event_payload():
    return {
        "event_type": "update",
        "message": "Investigating API key route protection.",
        "occurred_at": "2026-01-23T12:00:00Z",
    }


def test_auth_disabled_allows_incident_list_without_api_key(client_fixture):
    response = client_fixture.get("/api/v1/incidents")

    assert response.status_code == 200
    assert set(response.json()) >= {"items", "limit", "offset", "total"}


def test_auth_enabled_rejects_missing_key_on_incident_list(
    client_fixture,
    auth_enabled,
):
    response = client_fixture.get("/api/v1/incidents")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"


def test_auth_enabled_rejects_wrong_key_on_incident_list(
    client_fixture,
    auth_enabled,
):
    response = client_fixture.get(
        "/api/v1/incidents",
        headers=WRONG_AUTH_HEADER,
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"


def test_auth_enabled_allows_correct_key_on_incident_list(
    client_fixture,
    auth_enabled,
):
    response = client_fixture.get(
        "/api/v1/incidents",
        headers=AUTH_HEADER,
    )

    assert response.status_code == 200
    assert set(response.json()) >= {"items", "limit", "offset", "total"}


def test_auth_enabled_rejects_missing_key_on_incident_create(
    client_fixture,
    auth_enabled,
):
    response = client_fixture.post("/api/v1/incidents", json=_incident_payload())

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"


def test_auth_enabled_protects_nested_timeline_event_routes(
    client_fixture,
    auth_enabled,
):
    incident_response = client_fixture.post(
        "/api/v1/incidents",
        json=_incident_payload(),
        headers=AUTH_HEADER,
    )
    assert incident_response.status_code == 201
    incident_id = incident_response.json()["id"]

    missing_key_response = client_fixture.post(
        f"/api/v1/incidents/{incident_id}/events",
        json=_event_payload(),
    )
    assert missing_key_response.status_code == 401
    assert missing_key_response.json()["detail"] == "Invalid or missing API key"

    create_event_response = client_fixture.post(
        f"/api/v1/incidents/{incident_id}/events",
        json=_event_payload(),
        headers=AUTH_HEADER,
    )
    assert create_event_response.status_code == 201

    list_events_response = client_fixture.get(
        f"/api/v1/incidents/{incident_id}/events",
        headers=AUTH_HEADER,
    )
    assert list_events_response.status_code == 200


def test_auth_enabled_rejects_missing_key_on_incident_report(
    client_fixture,
    auth_enabled,
):
    incident_response = client_fixture.post(
        "/api/v1/incidents",
        json=_incident_payload(),
        headers=AUTH_HEADER,
    )
    assert incident_response.status_code == 201
    incident_id = incident_response.json()["id"]

    missing_key_response = client_fixture.get(
        f"/api/v1/incidents/{incident_id}/report"
    )

    assert missing_key_response.status_code == 401
    assert missing_key_response.json()["detail"] == "Invalid or missing API key"


def test_auth_enabled_rejects_missing_key_on_incident_report_markdown(
    client_fixture,
    auth_enabled,
):
    incident_response = client_fixture.post(
        "/api/v1/incidents",
        json=_incident_payload(),
        headers=AUTH_HEADER,
    )
    assert incident_response.status_code == 201
    incident_id = incident_response.json()["id"]

    missing_key_response = client_fixture.get(
        f"/api/v1/incidents/{incident_id}/report/markdown"
    )

    assert missing_key_response.status_code == 401
    assert missing_key_response.json()["detail"] == "Invalid or missing API key"


def test_auth_enabled_keeps_liveness_public(client_fixture, auth_enabled):
    response = client_fixture.get("/health/live")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
