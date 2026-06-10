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


def _create_event(client_fixture, incident_id):
    payload = {
        "event_type": "update",
        "message": "Restarting the primary node.",
        "occurred_at": "2026-01-23T12:00:00Z",
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


def test_list_incidents_returns_empty_list_initially(client_fixture):
    res = client_fixture.get("/api/v1/incidents")

    assert res.status_code == 200
    assert res.json() == []


def test_list_incidents_returns_newest_first(client_fixture):
    first_payload = {
        "title": "Older Incident",
        "description": "Older description",
        "status": "open",
        "severity": "sev2",
    }
    second_payload = {
        "title": "Newer Incident",
        "description": "Newer description",
        "status": "open",
        "severity": "sev2",
    }

    first_res = client_fixture.post("/api/v1/incidents", json=first_payload)
    second_res = client_fixture.post("/api/v1/incidents", json=second_payload)

    assert first_res.status_code == 201
    assert second_res.status_code == 201

    first_id = first_res.json()["id"]
    second_id = second_res.json()["id"]

    list_res = client_fixture.get("/api/v1/incidents")

    assert list_res.status_code == 200
    body = list_res.json()

    assert [item["id"] for item in body] == [second_id, first_id]
    assert body[0]["title"] == "Newer Incident"
    assert body[1]["title"] == "Older Incident"


def test_list_incidents_filters_by_status(client_fixture):
    client_fixture.post(
        "/api/v1/incidents",
        json={
            "title": "Open Incident",
            "description": "Open description",
            "status": "open",
            "severity": "sev2",
        },
    )
    client_fixture.post(
        "/api/v1/incidents",
        json={
            "title": "Investigating Incident",
            "description": "Investigating description",
            "status": "investigating",
            "severity": "sev2",
        },
    )

    res = client_fixture.get("/api/v1/incidents", params={"status_filter": "open"})

    assert res.status_code == 200
    body = res.json()

    assert len(body) == 1
    assert body[0]["status"] == "open"
    assert body[0]["title"] == "Open Incident"


def test_list_incidents_filters_by_severity(client_fixture):
    client_fixture.post(
        "/api/v1/incidents",
        json={
            "title": "SEV1 Incident",
            "description": "SEV1 description",
            "status": "open",
            "severity": "sev1",
        },
    )
    client_fixture.post(
        "/api/v1/incidents",
        json={
            "title": "SEV3 Incident",
            "description": "SEV3 description",
            "status": "open",
            "severity": "sev3",
        },
    )

    res = client_fixture.get("/api/v1/incidents", params={"severity_filter": "sev3"})

    assert res.status_code == 200
    body = res.json()

    assert len(body) == 1
    assert body[0]["severity"] == "sev3"
    assert body[0]["title"] == "SEV3 Incident"


def test_list_incidents_filters_by_status_and_severity(client_fixture):
    client_fixture.post(
        "/api/v1/incidents",
        json={
            "title": "Matching Incident",
            "description": "Matching description",
            "status": "open",
            "severity": "sev1",
        },
    )
    client_fixture.post(
        "/api/v1/incidents",
        json={
            "title": "Wrong Severity",
            "description": "Wrong severity description",
            "status": "open",
            "severity": "sev3",
        },
    )
    client_fixture.post(
        "/api/v1/incidents",
        json={
            "title": "Wrong Status",
            "description": "Wrong status description",
            "status": "investigating",
            "severity": "sev1",
        },
    )

    res = client_fixture.get(
        "/api/v1/incidents",
        params={"status_filter": "open", "severity_filter": "sev1"},
    )

    assert res.status_code == 200
    body = res.json()

    assert len(body) == 1
    assert body[0]["title"] == "Matching Incident"
    assert body[0]["status"] == "open"
    assert body[0]["severity"] == "sev1"


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
