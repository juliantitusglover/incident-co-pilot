from backend.domain.incidents.enums import Status


def test_create_and_read_incident(client_fixture):
    payload = {
        "title": "Test Incident",
        "description": "Something went wrong in the test environment",
        "status": "open",
        "severity": "sev2"
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
        "severity": "sev1"
    }
    create_res = client_fixture.post("/api/v1/incidents", json=incident_payload)
    incident_id = create_res.json()["id"]

    event_payload = {
        "event_type": "update",
        "message": "Restarting the primary node.",
        "occurred_at": "2026-01-23T12:00:00Z"
    }
    event_res = client_fixture.post(f"/api/v1/incidents/{incident_id}/events", json=event_payload)
    assert event_res.status_code == 201

    patch_res = client_fixture.patch(f"/api/v1/incidents/{incident_id}", json={"status": "resolved"})
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
        "severity": "sev1"
    }
    create_res = client_fixture.post("/api/v1/incidents", json=incident_payload)
    incident_id = create_res.json()["id"]
    incident_status = create_res.json()["status"]

    patch_res = client_fixture.patch(f"/api/v1/incidents/{incident_id}", json={"status": "open"})
    print(patch_res.json())
    assert patch_res.status_code == 400
    assert patch_res.json()["detail"] == f"invalid status transition: {Status.INVESTIGATING} -> {Status.OPEN}"