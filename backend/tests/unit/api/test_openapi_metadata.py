def _response_schema(openapi: dict, path: str, method: str, status_code: int) -> dict:
    response = openapi["paths"][path][method]["responses"][str(status_code)]
    return response["content"]["application/json"]["schema"]


def test_health_openapi_documents_response_schemas(app_fixture):
    openapi = app_fixture.openapi()

    live_operation = openapi["paths"]["/health/live"]["get"]
    live_schema = _response_schema(openapi, "/health/live", "get", 200)
    ready_schema = _response_schema(openapi, "/health/ready", "get", 200)
    ready_error_schema = _response_schema(openapi, "/health/ready", "get", 503)

    assert live_operation["summary"] == "Check API liveness"
    assert live_schema["$ref"].endswith("/HealthLiveResponse")
    assert ready_schema["$ref"].endswith("/HealthReadyResponse")
    assert ready_error_schema["$ref"].endswith("/HealthReadyErrorResponse")


def test_incident_openapi_documents_custom_error_responses(app_fixture):
    openapi = app_fixture.openapi()

    incident_list = openapi["paths"]["/api/v1/incidents"]["get"]
    incident_detail = openapi["paths"]["/api/v1/incidents/{incident_id}"]["get"]
    incident_patch = openapi["paths"]["/api/v1/incidents/{incident_id}"]["patch"]
    event_patch = openapi["paths"][
        "/api/v1/incidents/{incident_id}/events/{event_id}"
    ]["patch"]
    event_delete = openapi["paths"][
        "/api/v1/incidents/{incident_id}/events/{event_id}"
    ]["delete"]

    assert incident_list["summary"] == "List incidents"
    assert _response_schema(openapi, "/api/v1/incidents/{incident_id}", "get", 404)[
        "$ref"
    ].endswith("/ErrorResponse")
    assert incident_detail["responses"]["404"]["description"] == "Incident not found"

    assert _response_schema(openapi, "/api/v1/incidents/{incident_id}", "patch", 400)[
        "$ref"
    ].endswith("/ErrorResponse")
    assert _response_schema(openapi, "/api/v1/incidents/{incident_id}", "patch", 404)[
        "$ref"
    ].endswith("/ErrorResponse")
    assert incident_patch["responses"]["400"]["description"] == "Service validation error"

    assert _response_schema(
        openapi,
        "/api/v1/incidents/{incident_id}/events/{event_id}",
        "patch",
        404,
    )["$ref"].endswith("/ErrorResponse")
    assert _response_schema(
        openapi,
        "/api/v1/incidents/{incident_id}/events/{event_id}",
        "delete",
        404,
    )["$ref"].endswith("/ErrorResponse")
    assert event_patch["responses"]["404"]["description"] == "Incident or event not found"
    assert event_delete["responses"]["404"]["description"] == "Incident or event not found"
