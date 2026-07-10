def _create_incident(client_fixture):
    payload = {
        "title": "Event Test Incident",
        "description": "Incident used for event endpoint tests",
        "status": "open",
        "severity": "sev2",
    }

    response = client_fixture.post("/api/v1/incidents", json=payload)
    assert response.status_code == 201
    return response.json()["id"]


def _create_list_incident(
    client_fixture,
    title,
    status="open",
    severity="sev2",
):
    response = client_fixture.post(
        "/api/v1/incidents",
        json={
            "title": title,
            "description": f"{title} description",
            "status": status,
            "severity": severity,
        },
    )
    assert response.status_code == 201
    return response.json()


def _create_event(
    client_fixture,
    incident_id,
    event_type="update",
    message="Restarting the primary node.",
    occurred_at="2026-01-23T12:00:00Z",
):
    payload = {
        "event_type": event_type,
        "message": message,
        "occurred_at": occurred_at,
    }

    response = client_fixture.post(
        f"/api/v1/incidents/{incident_id}/events", json=payload
    )
    assert response.status_code == 201
    return response.json()


def test_create_and_read_incident(client_fixture):
    payload = {
        "title": "Test Incident",
        "description": "Something went wrong in the test environment",
        "status": "open",
        "severity": "sev2",
    }

    response = client_fixture.post("/api/v1/incidents", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["title"] == payload["title"]
    assert "id" in data

    incident_id = data["id"]
    get_response = client_fixture.get(f"/api/v1/incidents/{incident_id}")
    assert get_response.status_code == 200
    assert get_response.json()["description"] == payload["description"]


def test_incident_lifecycle_with_events(client_fixture):
    incident_payload = {
        "title": "Database Outage",
        "description": "Production DB is down",
        "status": "investigating",
        "severity": "sev1",
    }
    create_res = client_fixture.post("/api/v1/incidents", json=incident_payload)
    incident_id = create_res.json()["id"]

    event_payload = {
        "event_type": "update",
        "message": "Restarting the primary node.",
        "occurred_at": "2026-01-23T12:00:00Z",
    }
    event_res = client_fixture.post(
        f"/api/v1/incidents/{incident_id}/events", json=event_payload
    )
    assert event_res.status_code == 201

    patch_res = client_fixture.patch(
        f"/api/v1/incidents/{incident_id}", json={"status": "resolved"}
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "resolved"

    final_res = client_fixture.get(f"/api/v1/incidents/{incident_id}")
    data = final_res.json()
    assert len(data["events"]) == 1
    assert data["events"][0]["message"] == event_payload["message"]

    del_res = client_fixture.delete(f"/api/v1/incidents/{incident_id}")
    assert del_res.status_code == 204
    assert client_fixture.get(f"/api/v1/incidents/{incident_id}").status_code == 404


def test_get_incident_returns_timeline_events_newest_first(client_fixture):
    incident_id = _create_incident(client_fixture)
    first = _create_event(
        client_fixture,
        incident_id,
        message="First nested event.",
    )
    second = _create_event(
        client_fixture,
        incident_id,
        message="Second nested event.",
    )

    response = client_fixture.get(f"/api/v1/incidents/{incident_id}")

    assert response.status_code == 200
    events = response.json()["events"]
    assert len(events) == 2
    assert [event["id"] for event in events] == [second["id"], first["id"]]


def test_get_incident_with_non_existent_id(client_fixture):
    response = client_fixture.get(f"/api/v1/incidents/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Incident not found"


def test_update_incident_with_invalid_status_transition(client_fixture):
    incident_payload = {
        "title": "Database Outage",
        "description": "Production DB is down",
        "status": "investigating",
        "severity": "sev1",
    }
    create_res = client_fixture.post("/api/v1/incidents", json=incident_payload)
    incident_id = create_res.json()["id"]
    incident_status = create_res.json()["status"]

    patch_res = client_fixture.patch(
        f"/api/v1/incidents/{incident_id}", json={"status": "open"}
    )
    assert patch_res.status_code == 400
    assert (
        patch_res.json()["detail"]
        == f"invalid status transition: {incident_status} -> open"
    )


def test_list_incidents_returns_default_pagination_envelope(client_fixture):
    first = _create_list_incident(client_fixture, "Older Incident")
    second = _create_list_incident(client_fixture, "Middle Incident")
    third = _create_list_incident(client_fixture, "Newer Incident")

    res = client_fixture.get("/api/v1/incidents")

    assert res.status_code == 200
    body = res.json()

    assert isinstance(body, dict)
    assert set(body) >= {"items", "limit", "offset", "total"}
    assert body["limit"] == 50
    assert body["offset"] == 0
    assert body["total"] == 3
    assert [item["id"] for item in body["items"]] == [
        third["id"],
        second["id"],
        first["id"],
    ]
    assert set(body["items"][0]) >= {
        "id",
        "title",
        "status",
        "severity",
        "created_at",
        "updated_at",
    }
    assert body["items"][0]["title"] == "Newer Incident"
    assert body["items"][1]["title"] == "Middle Incident"
    assert body["items"][2]["title"] == "Older Incident"


def test_list_incidents_returns_newest_first(client_fixture):
    first = _create_list_incident(client_fixture, "Older Incident")
    second = _create_list_incident(client_fixture, "Newer Incident")

    list_res = client_fixture.get("/api/v1/incidents")

    assert list_res.status_code == 200
    body = list_res.json()

    assert [item["id"] for item in body["items"]] == [second["id"], first["id"]]
    assert body["items"][0]["title"] == "Newer Incident"
    assert body["items"][1]["title"] == "Older Incident"


def test_list_incidents_honors_limit_parameter(client_fixture):
    _create_list_incident(client_fixture, "Oldest Incident")
    _create_list_incident(client_fixture, "Middle Incident")
    _create_list_incident(client_fixture, "Newest Incident")

    res = client_fixture.get("/api/v1/incidents", params={"limit": 2})

    assert res.status_code == 200
    body = res.json()
    assert len(body["items"]) == 2
    assert body["limit"] == 2
    assert body["offset"] == 0
    assert body["total"] == 3


def test_list_incidents_honors_offset_parameter(client_fixture):
    first = _create_list_incident(client_fixture, "Oldest Incident")
    second = _create_list_incident(client_fixture, "Middle Incident")
    third = _create_list_incident(client_fixture, "Newest Incident")

    res = client_fixture.get(
        "/api/v1/incidents",
        params={"limit": 1, "offset": 1},
    )

    assert res.status_code == 200
    body = res.json()
    assert len(body["items"]) == 1
    assert body["limit"] == 1
    assert body["offset"] == 1
    assert body["total"] == 3
    assert [item["id"] for item in body["items"]] == [second["id"]]


def test_list_incidents_filters_by_status(client_fixture):
    _create_list_incident(client_fixture, "Open Incident")
    _create_list_incident(
        client_fixture,
        "Investigating Incident",
        status="investigating",
    )

    res = client_fixture.get("/api/v1/incidents", params={"status_filter": "open"})

    assert res.status_code == 200
    body = res.json()
    items = body["items"]

    assert len(items) == 1
    assert items[0]["status"] == "open"
    assert items[0]["title"] == "Open Incident"


def test_list_incidents_filters_by_severity(client_fixture):
    _create_list_incident(client_fixture, "SEV1 Incident", severity="sev1")
    _create_list_incident(client_fixture, "SEV3 Incident", severity="sev3")

    res = client_fixture.get("/api/v1/incidents", params={"severity_filter": "sev3"})

    assert res.status_code == 200
    body = res.json()
    items = body["items"]

    assert len(items) == 1
    assert items[0]["severity"] == "sev3"
    assert items[0]["title"] == "SEV3 Incident"


def test_list_incidents_filters_by_status_and_severity(client_fixture):
    _create_list_incident(client_fixture, "Matching Incident", severity="sev1")
    _create_list_incident(client_fixture, "Wrong Severity", severity="sev3")
    _create_list_incident(
        client_fixture,
        "Wrong Status",
        status="investigating",
        severity="sev1",
    )

    res = client_fixture.get(
        "/api/v1/incidents",
        params={"status_filter": "open", "severity_filter": "sev1"},
    )

    assert res.status_code == 200
    body = res.json()
    items = body["items"]

    assert len(items) == 1
    assert items[0]["title"] == "Matching Incident"
    assert items[0]["status"] == "open"
    assert items[0]["severity"] == "sev1"


def test_list_incidents_combines_filters_with_pagination(client_fixture):
    first_match = _create_list_incident(
        client_fixture,
        "Older Matching Incident",
        severity="sev1",
    )
    _create_list_incident(client_fixture, "Wrong Severity", severity="sev3")
    _create_list_incident(
        client_fixture,
        "Wrong Status",
        status="investigating",
        severity="sev1",
    )
    second_match = _create_list_incident(
        client_fixture,
        "Newer Matching Incident",
        severity="sev1",
    )

    res = client_fixture.get(
        "/api/v1/incidents",
        params={
            "status_filter": "open",
            "severity_filter": "sev1",
            "limit": 1,
            "offset": 0,
        },
    )

    assert res.status_code == 200
    body = res.json()
    assert len(body["items"]) == 1
    assert body["limit"] == 1
    assert body["offset"] == 0
    assert body["total"] == 2
    assert body["items"][0]["id"] == second_match["id"]
    assert body["items"][0]["id"] != first_match["id"]
    assert body["items"][0]["status"] == "open"
    assert body["items"][0]["severity"] == "sev1"


def test_create_incident_response_returns_trimmed_values(client_fixture):
    payload = {
        "title": "  Trimmed Title  ",
        "description": "  Trimmed Description  ",
        "status": "open",
        "severity": "sev2",
    }

    response = client_fixture.post("/api/v1/incidents", json=payload)

    assert response.status_code == 201
    body = response.json()

    assert body["title"] == "Trimmed Title"
    assert body["description"] == "Trimmed Description"
    assert body["status"] == "open"
    assert body["severity"] == "sev2"


def test_create_incident_rejects_schema_invalid_payload_with_422(client_fixture):
    payload = {
        "title": "Bad Severity Incident",
        "description": "Invalid enum should fail at schema layer",
        "status": "open",
        "severity": "sev0",
    }

    response = client_fixture.post("/api/v1/incidents", json=payload)

    assert response.status_code == 422


def test_create_incident_rejects_stripped_empty_title_with_422(client_fixture):
    payload = {
        "title": "   ",
        "description": "Valid description",
        "status": "open",
        "severity": "sev2",
    }

    response = client_fixture.post("/api/v1/incidents", json=payload)

    assert response.status_code == 422


def test_create_incident_rejects_stripped_empty_description_with_422(client_fixture):
    payload = {
        "title": "Valid title",
        "description": "   ",
        "status": "open",
        "severity": "sev2",
    }

    response = client_fixture.post("/api/v1/incidents", json=payload)

    assert response.status_code == 422


def test_update_incident_partial_update_preserves_other_fields(client_fixture):
    create_payload = {
        "title": "Original Title",
        "description": "Original Description",
        "status": "open",
        "severity": "sev2",
    }

    create_res = client_fixture.post("/api/v1/incidents", json=create_payload)
    assert create_res.status_code == 201
    incident_id = create_res.json()["id"]

    patch_res = client_fixture.patch(
        f"/api/v1/incidents/{incident_id}",
        json={"title": "Updated Title"},
    )

    assert patch_res.status_code == 200
    body = patch_res.json()

    assert body["title"] == "Updated Title"
    assert body["description"] == "Original Description"
    assert body["status"] == "open"
    assert body["severity"] == "sev2"


def test_update_incident_returns_trimmed_values(client_fixture):
    create_payload = {
        "title": "Original Title",
        "description": "Original Description",
        "status": "open",
        "severity": "sev2",
    }

    create_res = client_fixture.post("/api/v1/incidents", json=create_payload)
    assert create_res.status_code == 201
    incident_id = create_res.json()["id"]

    patch_res = client_fixture.patch(
        f"/api/v1/incidents/{incident_id}",
        json={
            "title": "  Trimmed Updated Title  ",
            "description": "  Trimmed Updated Description  ",
        },
    )

    assert patch_res.status_code == 200
    body = patch_res.json()

    assert body["title"] == "Trimmed Updated Title"
    assert body["description"] == "Trimmed Updated Description"


def test_update_incident_missing_incident_returns_404(client_fixture):
    patch_res = client_fixture.patch(
        "/api/v1/incidents/999",
        json={"title": "Updated"},
    )

    assert patch_res.status_code == 404
    assert patch_res.json()["detail"] == "Incident not found"


def test_update_incident_rejects_schema_invalid_payload_with_422(client_fixture):
    create_payload = {
        "title": "Original Title",
        "description": "Original Description",
        "status": "open",
        "severity": "sev2",
    }

    create_res = client_fixture.post("/api/v1/incidents", json=create_payload)
    assert create_res.status_code == 201
    incident_id = create_res.json()["id"]

    patch_res = client_fixture.patch(
        f"/api/v1/incidents/{incident_id}",
        json={"status": "closed"},
    )

    assert patch_res.status_code == 422


def test_update_incident_rejects_stripped_empty_title_with_422(client_fixture):
    create_payload = {
        "title": "Original Title",
        "description": "Original Description",
        "status": "open",
        "severity": "sev2",
    }

    create_res = client_fixture.post("/api/v1/incidents", json=create_payload)
    assert create_res.status_code == 201
    incident_id = create_res.json()["id"]

    patch_res = client_fixture.patch(
        f"/api/v1/incidents/{incident_id}",
        json={"title": "   "},
    )

    assert patch_res.status_code == 422


def test_delete_incident_missing_returns_404(client_fixture):
    response = client_fixture.delete("/api/v1/incidents/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Incident not found"


def test_list_incidents_rejects_invalid_status_filter_with_422(client_fixture):
    response = client_fixture.get(
        "/api/v1/incidents",
        params={"status_filter": "closed"},
    )

    assert response.status_code == 422


def test_list_incidents_rejects_invalid_severity_filter_with_422(client_fixture):
    response = client_fixture.get(
        "/api/v1/incidents",
        params={"severity_filter": "sev0"},
    )

    assert response.status_code == 422


def test_list_incidents_rejects_invalid_pagination_params_with_422(client_fixture):
    invalid_params = (
        {"limit": 0},
        {"limit": 101},
        {"offset": -1},
    )

    for params in invalid_params:
        response = client_fixture.get("/api/v1/incidents", params=params)

        assert response.status_code == 422, params


def test_update_incident_rejects_stripped_empty_description_with_422(client_fixture):
    create_payload = {
        "title": "Original Title",
        "description": "Original Description",
        "status": "open",
        "severity": "sev2",
    }

    create_res = client_fixture.post("/api/v1/incidents", json=create_payload)
    assert create_res.status_code == 201
    incident_id = create_res.json()["id"]

    patch_res = client_fixture.patch(
        f"/api/v1/incidents/{incident_id}",
        json={"description": "   "},
    )

    assert patch_res.status_code == 422


def test_create_event_returns_trimmed_values(client_fixture):
    incident_id = _create_incident(client_fixture)
    payload = {
        "event_type": "  update  ",
        "message": "  Restarting the primary node.  ",
        "occurred_at": "2026-01-23T12:00:00Z",
    }

    response = client_fixture.post(
        f"/api/v1/incidents/{incident_id}/events", json=payload
    )

    assert response.status_code == 201
    body = response.json()

    assert body["event_type"] == "update"
    assert body["message"] == "Restarting the primary node."


def test_create_event_missing_incident_returns_404(client_fixture):
    payload = {
        "event_type": "update",
        "message": "Restarting the primary node.",
        "occurred_at": "2026-01-23T12:00:00Z",
    }

    response = client_fixture.post("/api/v1/incidents/999/events", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Incident not found"


def test_create_event_rejects_invalid_payload_with_422(client_fixture):
    incident_id = _create_incident(client_fixture)
    payload = {
        "event_type": "update",
        "message": "Restarting the primary node.",
        "occurred_at": "not-a-datetime",
    }

    response = client_fixture.post(
        f"/api/v1/incidents/{incident_id}/events", json=payload
    )

    assert response.status_code == 422


def test_create_event_rejects_stripped_empty_event_type_with_422(client_fixture):
    incident_id = _create_incident(client_fixture)
    payload = {
        "event_type": "   ",
        "message": "Restarting the primary node.",
        "occurred_at": "2026-01-23T12:00:00Z",
    }

    response = client_fixture.post(
        f"/api/v1/incidents/{incident_id}/events", json=payload
    )

    assert response.status_code == 422


def test_create_event_rejects_stripped_empty_message_with_422(client_fixture):
    incident_id = _create_incident(client_fixture)
    payload = {
        "event_type": "update",
        "message": "   ",
        "occurred_at": "2026-01-23T12:00:00Z",
    }

    response = client_fixture.post(
        f"/api/v1/incidents/{incident_id}/events", json=payload
    )

    assert response.status_code == 422


def test_list_timeline_events_returns_ordered_events(client_fixture):
    incident_id = _create_incident(client_fixture)
    first = _create_event(
        client_fixture,
        incident_id,
        message="Investigation started.",
    )
    second = _create_event(
        client_fixture,
        incident_id,
        message="Primary node restarted.",
    )

    response = client_fixture.get(f"/api/v1/incidents/{incident_id}/events")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert [event["id"] for event in body] == [second["id"], first["id"]]
    assert [event["created_at"] for event in body] == [
        second["created_at"],
        first["created_at"],
    ]
    assert set(body[0]) >= {
        "id",
        "incident_id",
        "message",
        "created_at",
        "updated_at",
    }


def test_list_timeline_events_returns_empty_list_for_incident_with_no_events(
    client_fixture,
):
    incident_id = _create_incident(client_fixture)

    response = client_fixture.get(f"/api/v1/incidents/{incident_id}/events")

    assert response.status_code == 200
    assert response.json() == []


def test_list_timeline_events_missing_incident_returns_404(client_fixture):
    response = client_fixture.get("/api/v1/incidents/999999/events")

    assert response.status_code == 404
    assert response.json()["detail"] == "Incident not found"


def test_get_timeline_event_returns_event(client_fixture):
    incident_id = _create_incident(client_fixture)
    event = _create_event(
        client_fixture,
        incident_id,
        event_type="mitigation",
        message="Primary node restarted.",
        occurred_at="2026-01-24T15:30:00Z",
    )

    response = client_fixture.get(
        f"/api/v1/incidents/{incident_id}/events/{event['id']}"
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == event["id"]
    assert body["incident_id"] == incident_id
    assert body["event_type"] == "mitigation"
    assert body["message"] == "Primary node restarted."
    assert body["occurred_at"] == "2026-01-24T15:30:00Z"
    assert body["created_at"] == event["created_at"]
    assert body["updated_at"] == event["updated_at"]


def test_get_timeline_event_missing_incident_returns_404(client_fixture):
    response = client_fixture.get("/api/v1/incidents/999999/events/1")

    assert response.status_code == 404
    assert response.json()["detail"] == "Incident not found"


def test_get_timeline_event_missing_event_returns_404(client_fixture):
    incident_id = _create_incident(client_fixture)

    response = client_fixture.get(f"/api/v1/incidents/{incident_id}/events/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_get_timeline_event_for_wrong_incident_returns_404(client_fixture):
    first_incident_id = _create_incident(client_fixture)
    second_incident_id = _create_incident(client_fixture)
    event = _create_event(client_fixture, second_incident_id)

    response = client_fixture.get(
        f"/api/v1/incidents/{first_incident_id}/events/{event['id']}"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_update_event_partial_update_preserves_other_fields(client_fixture):
    incident_id = _create_incident(client_fixture)
    event = _create_event(client_fixture, incident_id)

    response = client_fixture.patch(
        f"/api/v1/incidents/{incident_id}/events/{event['id']}",
        json={"message": "Primary node restarted."},
    )

    assert response.status_code == 200
    body = response.json()

    assert body["message"] == "Primary node restarted."
    assert body["event_type"] == event["event_type"]
    assert body["occurred_at"] == event["occurred_at"]


def test_update_event_returns_trimmed_values(client_fixture):
    incident_id = _create_incident(client_fixture)
    event = _create_event(client_fixture, incident_id)

    response = client_fixture.patch(
        f"/api/v1/incidents/{incident_id}/events/{event['id']}",
        json={
            "event_type": "  mitigation  ",
            "message": "  Primary node restarted.  ",
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert body["event_type"] == "mitigation"
    assert body["message"] == "Primary node restarted."


def test_update_event_can_change_occurred_at(client_fixture):
    incident_id = _create_incident(client_fixture)
    event = _create_event(client_fixture, incident_id)
    new_occurred_at = "2026-01-24T15:30:00Z"

    response = client_fixture.patch(
        f"/api/v1/incidents/{incident_id}/events/{event['id']}",
        json={"occurred_at": new_occurred_at},
    )

    assert response.status_code == 200
    assert response.json()["occurred_at"] == new_occurred_at


def test_update_event_rejects_invalid_payload_with_422(client_fixture):
    incident_id = _create_incident(client_fixture)
    event = _create_event(client_fixture, incident_id)

    response = client_fixture.patch(
        f"/api/v1/incidents/{incident_id}/events/{event['id']}",
        json={"occurred_at": "not-a-datetime"},
    )

    assert response.status_code == 422


def test_update_event_rejects_stripped_empty_event_type_with_422(client_fixture):
    incident_id = _create_incident(client_fixture)
    event = _create_event(client_fixture, incident_id)

    response = client_fixture.patch(
        f"/api/v1/incidents/{incident_id}/events/{event['id']}",
        json={"event_type": "   "},
    )

    assert response.status_code == 422


def test_update_event_rejects_stripped_empty_message_with_422(client_fixture):
    incident_id = _create_incident(client_fixture)
    event = _create_event(client_fixture, incident_id)

    response = client_fixture.patch(
        f"/api/v1/incidents/{incident_id}/events/{event['id']}",
        json={"message": "   "},
    )

    assert response.status_code == 422


def test_update_event_missing_event_returns_404(client_fixture):
    incident_id = _create_incident(client_fixture)

    response = client_fixture.patch(
        f"/api/v1/incidents/{incident_id}/events/999",
        json={"message": "Primary node restarted."},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_update_event_missing_incident_returns_404(client_fixture):
    response = client_fixture.patch(
        "/api/v1/incidents/999/events/999",
        json={"message": "Primary node restarted."},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Incident not found"


def test_delete_event_missing_event_returns_404(client_fixture):
    incident_id = _create_incident(client_fixture)

    response = client_fixture.delete(f"/api/v1/incidents/{incident_id}/events/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_delete_event_missing_incident_returns_404(client_fixture):
    response = client_fixture.delete("/api/v1/incidents/999/events/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Incident not found"


def test_delete_event_success_returns_204(client_fixture):
    incident_id = _create_incident(client_fixture)
    event = _create_event(client_fixture, incident_id)

    response = client_fixture.delete(
        f"/api/v1/incidents/{incident_id}/events/{event['id']}"
    )

    assert response.status_code == 204

    incident_response = client_fixture.get(f"/api/v1/incidents/{incident_id}")
    assert incident_response.status_code == 200
    assert incident_response.json()["events"] == []
