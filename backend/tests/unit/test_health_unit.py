from backend.db.health import is_database_ready

def test_health_liveness_success(client_fixture, settings_fixture):
    response = client_fixture.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": settings_fixture.API_VERSION}

def mock_is_database_ready_failure(settings=None):
    return {
        "status": "unhealthy", 
        "connectivity": False, 
        "tables_found": [], 
        "error": "Mocked failure"
    }

def test_health_readiness_failure(client_fixture):
    client_fixture.app.dependency_overrides[is_database_ready] = mock_is_database_ready_failure
    response = client_fixture.get("/health/ready")    
    assert response.status_code == 503
    data = response.json()
    assert "detail" in data
    assert data["detail"]["status"] == "unhealthy"
    assert data["detail"]["error"] == "Mocked failure"
    liveness_response = client_fixture.get("/health/live")
    assert liveness_response.status_code == 200
    client_fixture.app.dependency_overrides.pop(is_database_ready, None)