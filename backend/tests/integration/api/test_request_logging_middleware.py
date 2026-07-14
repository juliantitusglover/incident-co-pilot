import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.exception_handlers import register_exception_handlers
from backend.api.middleware import (
    REQUEST_ID_HEADER,
    RequestIDMiddleware,
    RequestLoggingMiddleware,
)
from backend.core.config import get_settings
from backend.core.logging import configure_logging


REQUEST_LOGGER = "backend.api.request"


@pytest.fixture(autouse=True)
def logging_configured_after_db_setup(db_setup):
    configure_logging("info")


def _request_log_records(caplog):
    return [
        record
        for record in caplog.records
        if record.name == REQUEST_LOGGER
        and record.getMessage().startswith("request completed")
    ]


def _single_request_log(caplog):
    records = _request_log_records(caplog)
    assert len(records) == 1
    return records[0].getMessage()


def _assert_log_contains_request(
    log_text,
    *,
    request_id,
    method,
    path,
    status_code,
):
    assert "request completed" in log_text
    assert f"request_id={request_id}" in log_text
    assert f"method={method}" in log_text
    assert f"path={path}" in log_text
    assert f"status_code={status_code}" in log_text
    assert "duration_ms=" in log_text


def test_successful_liveness_request_logs_completion(client_fixture, caplog):
    caplog.set_level(logging.INFO, logger=REQUEST_LOGGER)

    response = client_fixture.get("/health/live")

    assert response.status_code == 200
    log_text = _single_request_log(caplog)
    _assert_log_contains_request(
        log_text,
        request_id=response.headers[REQUEST_ID_HEADER],
        method="GET",
        path="/health/live",
        status_code=200,
    )


def test_caller_provided_request_id_appears_in_request_log(client_fixture, caplog):
    caplog.set_level(logging.INFO, logger=REQUEST_LOGGER)

    response = client_fixture.get(
        "/health/live",
        headers={REQUEST_ID_HEADER: "caller-request-id"},
    )

    assert response.status_code == 200
    assert f"request_id={response.headers[REQUEST_ID_HEADER]}" in _single_request_log(
        caplog
    )


def test_domain_404_logs_status_and_request_id(client_fixture, caplog):
    caplog.set_level(logging.INFO, logger=REQUEST_LOGGER)

    response = client_fixture.get("/api/v1/incidents/999999")

    assert response.status_code == 404
    log_text = _single_request_log(caplog)
    _assert_log_contains_request(
        log_text,
        request_id=response.headers[REQUEST_ID_HEADER],
        method="GET",
        path="/api/v1/incidents/999999",
        status_code=404,
    )


def test_auth_401_logs_status_without_api_key(
    client_fixture,
    settings_fixture,
    caplog,
):
    api_key = "test-api-key"
    auth_settings = settings_fixture.model_copy(
        update={
            "API_AUTH_ENABLED": True,
            "API_KEY": api_key,
        }
    )
    client_fixture.app.dependency_overrides[get_settings] = lambda: auth_settings
    caplog.set_level(logging.INFO, logger=REQUEST_LOGGER)

    response = client_fixture.get(
        "/api/v1/incidents",
        headers={"X-API-Key": api_key},
    )

    assert response.status_code == 200
    caplog.clear()

    response = client_fixture.get(
        "/api/v1/incidents",
        headers={"X-API-Key": "wrong-api-key"},
    )

    assert response.status_code == 401
    log_text = _single_request_log(caplog)
    _assert_log_contains_request(
        log_text,
        request_id=response.headers[REQUEST_ID_HEADER],
        method="GET",
        path="/api/v1/incidents",
        status_code=401,
    )
    assert "wrong-api-key" not in caplog.text
    assert api_key not in caplog.text


def test_validation_422_logs_status(client_fixture, caplog):
    caplog.set_level(logging.INFO, logger=REQUEST_LOGGER)

    response = client_fixture.get("/api/v1/incidents", params={"limit": 0})

    assert response.status_code == 422
    log_text = _single_request_log(caplog)
    _assert_log_contains_request(
        log_text,
        request_id=response.headers[REQUEST_ID_HEADER],
        method="GET",
        path="/api/v1/incidents",
        status_code=422,
    )


def test_unhandled_500_logs_status_and_request_id(caplog):
    app = FastAPI()
    register_exception_handlers(app)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)

    @app.get("/boom")
    def boom():
        raise RuntimeError("boom")

    caplog.set_level(logging.INFO, logger=REQUEST_LOGGER)
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/boom")

    assert response.status_code == 500
    log_text = _single_request_log(caplog)
    _assert_log_contains_request(
        log_text,
        request_id=response.headers[REQUEST_ID_HEADER],
        method="GET",
        path="/boom",
        status_code=500,
    )


def test_post_body_content_is_not_logged(client_fixture, caplog):
    sensitive_description = "unique-sensitive-description-for-request-log-test"
    caplog.set_level(logging.INFO, logger=REQUEST_LOGGER)

    response = client_fixture.post(
        "/api/v1/incidents",
        json={
            "title": "Request Log Safety",
            "description": sensitive_description,
            "status": "open",
            "severity": "sev2",
        },
    )

    assert response.status_code == 201
    assert sensitive_description not in caplog.text
    _assert_log_contains_request(
        _single_request_log(caplog),
        request_id=response.headers[REQUEST_ID_HEADER],
        method="POST",
        path="/api/v1/incidents",
        status_code=201,
    )


def test_query_string_is_not_logged(client_fixture, caplog):
    caplog.set_level(logging.INFO, logger=REQUEST_LOGGER)

    response = client_fixture.get(
        "/api/v1/incidents",
        params={"api_key": "secret-query-value"},
    )

    assert response.status_code == 200
    assert "secret-query-value" not in caplog.text
    assert "api_key=" not in caplog.text
    _assert_log_contains_request(
        _single_request_log(caplog),
        request_id=response.headers[REQUEST_ID_HEADER],
        method="GET",
        path="/api/v1/incidents",
        status_code=200,
    )
