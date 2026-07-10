def _response_schema(openapi: dict, path: str, method: str, status_code: int) -> dict:
    response = openapi["paths"][path][method]["responses"][str(status_code)]
    return response["content"]["application/json"]["schema"]


def _parameters_by_name(operation: dict) -> dict:
    return {parameter["name"]: parameter for parameter in operation["parameters"]}


def _parameter_example(parameter: dict):
    if "example" in parameter:
        return parameter["example"]
    if "examples" in parameter["schema"]:
        return parameter["schema"]["examples"][0]
    return parameter["schema"].get("example")


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


def test_incident_list_openapi_documents_pagination_metadata(app_fixture):
    openapi = app_fixture.openapi()
    operation = openapi["paths"]["/api/v1/incidents"]["get"]
    parameters = _parameters_by_name(operation)
    response_content = operation["responses"]["200"]["content"]["application/json"]
    example = response_content["example"]

    assert response_content["schema"]["$ref"].endswith("/IncidentListResponse")
    assert set(parameters) >= {
        "status_filter",
        "severity_filter",
        "limit",
        "offset",
    }

    limit_schema = parameters["limit"]["schema"]
    assert limit_schema["default"] == 50
    assert limit_schema["minimum"] == 1
    assert limit_schema["maximum"] == 100
    assert _parameter_example(parameters["limit"]) == 25

    offset_schema = parameters["offset"]["schema"]
    assert offset_schema["default"] == 0
    assert offset_schema["minimum"] == 0
    assert _parameter_example(parameters["offset"]) == 0

    for name in ("status_filter", "severity_filter", "limit", "offset"):
        assert parameters[name]["description"]

    assert _parameter_example(parameters["status_filter"]) == "open"
    assert _parameter_example(parameters["severity_filter"]) == "sev1"
    assert set(example) == {"items", "limit", "offset", "total"}
    assert example["items"][0]["status"] == "investigating"
    assert example["items"][0]["severity"] == "sev1"


def test_timeline_event_read_routes_openapi_metadata(app_fixture):
    openapi = app_fixture.openapi()
    list_operation = openapi["paths"]["/api/v1/incidents/{incident_id}/events"][
        "get"
    ]
    get_operation = openapi["paths"][
        "/api/v1/incidents/{incident_id}/events/{event_id}"
    ]["get"]

    list_schema = _response_schema(
        openapi,
        "/api/v1/incidents/{incident_id}/events",
        "get",
        200,
    )
    get_schema = _response_schema(
        openapi,
        "/api/v1/incidents/{incident_id}/events/{event_id}",
        "get",
        200,
    )

    assert list_operation["summary"] == "List timeline events"
    assert list_operation["description"]
    assert get_operation["summary"] == "Get timeline event"
    assert get_operation["description"]

    assert list_schema["type"] == "array"
    assert list_schema["items"]["$ref"].endswith("/TimelineEventRead")
    assert get_schema["$ref"].endswith("/TimelineEventRead")

    assert _response_schema(
        openapi,
        "/api/v1/incidents/{incident_id}/events",
        "get",
        404,
    )["$ref"].endswith("/ErrorResponse")
    assert _response_schema(
        openapi,
        "/api/v1/incidents/{incident_id}/events/{event_id}",
        "get",
        404,
    )["$ref"].endswith("/ErrorResponse")
    assert list_operation["responses"]["404"]["description"] == "Incident not found"
    assert (
        get_operation["responses"]["404"]["description"]
        == "Incident or event not found"
    )
