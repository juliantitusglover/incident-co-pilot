from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from backend.api.exception_handlers import register_exception_handlers
from backend.api.middleware import REQUEST_ID_HEADER, RequestIDMiddleware
from backend.api.middleware.request_id import MAX_REQUEST_ID_LENGTH
from backend.core.config import get_settings


def _request_id(response):
    return response.headers.get(REQUEST_ID_HEADER)


def test_missing_request_id_generates_header_on_liveness(client_fixture):
    response = client_fixture.get("/health/live")

    assert response.status_code == 200
    assert _request_id(response)


def test_provided_request_id_is_trimmed_and_preserved(client_fixture):
    response = client_fixture.get(
        "/health/live",
        headers={REQUEST_ID_HEADER: "  caller-request-id  "},
    )

    assert response.status_code == 200
    assert _request_id(response) == "caller-request-id"


def test_blank_request_id_generates_non_blank_header(client_fixture):
    response = client_fixture.get(
        "/health/live",
        headers={REQUEST_ID_HEADER: "   "},
    )

    assert response.status_code == 200
    assert _request_id(response)


def test_overlong_request_id_generates_new_header(client_fixture):
    overlong_request_id = "a" * (MAX_REQUEST_ID_LENGTH + 1)

    response = client_fixture.get(
        "/health/live",
        headers={REQUEST_ID_HEADER: overlong_request_id},
    )

    assert response.status_code == 200
    assert _request_id(response)
    assert _request_id(response) != overlong_request_id


def test_domain_404_includes_request_id_without_body_change(client_fixture):
    response = client_fixture.get("/api/v1/incidents/999999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Incident not found"}
    assert _request_id(response)


def test_incident_report_response_includes_request_id(client_fixture):
    create_response = client_fixture.post(
        "/api/v1/incidents",
        json={
            "title": "Request ID Report",
            "description": "Incident used for report request ID test",
            "status": "open",
            "severity": "sev2",
        },
    )
    assert create_response.status_code == 201
    incident_id = create_response.json()["id"]

    response = client_fixture.get(f"/api/v1/incidents/{incident_id}/report")

    assert response.status_code == 200
    assert _request_id(response)


def test_auth_401_includes_request_id_without_body_change(
    client_fixture,
    settings_fixture,
):
    auth_settings = settings_fixture.model_copy(
        update={
            "API_AUTH_ENABLED": True,
            "API_KEY": "test-api-key",
        }
    )
    client_fixture.app.dependency_overrides[get_settings] = lambda: auth_settings

    response = client_fixture.get("/api/v1/incidents")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing API key"}
    assert _request_id(response)


def test_422_validation_response_includes_request_id(client_fixture):
    response = client_fixture.get(
        "/api/v1/incidents",
        params={"limit": 0},
    )

    assert response.status_code == 422
    assert _request_id(response)


def test_docs_response_includes_request_id(client_fixture):
    response = client_fixture.get("/docs")

    assert response.status_code == 200
    assert _request_id(response)


def test_request_id_is_available_on_request_state():
    app = FastAPI()
    app.add_middleware(RequestIDMiddleware)

    @app.get("/state")
    def state(request: Request):
        return {"request_id": request.state.request_id}

    with TestClient(app) as client:
        response = client.get(
            "/state",
            headers={REQUEST_ID_HEADER: "state-request-id"},
        )

    assert response.status_code == 200
    assert response.json() == {"request_id": "state-request-id"}
    assert _request_id(response) == "state-request-id"


def test_unhandled_500_includes_request_id_without_body_change():
    app = FastAPI()
    register_exception_handlers(app)
    app.add_middleware(RequestIDMiddleware)

    @app.get("/boom")
    def boom():
        raise RuntimeError("boom")

    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/boom")

    assert response.status_code == 500
    assert response.text == "Internal Server Error"
    assert _request_id(response)
