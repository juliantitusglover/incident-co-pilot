from backend.db.health import is_database_ready


def test_liveness_endpoint_returns_exact_contract(client_fixture, settings_fixture):
    response = client_fixture.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "version": settings_fixture.API_VERSION,
    }


def test_readiness_endpoint_returns_healthy_contract(client_fixture):
    response = client_fixture.get("/health/ready")

    assert response.status_code == 200
    body = response.json()

    assert body["status"] == "healthy"
    assert body["connectivity"] is True
    assert "incidents" in body["tables_found"]
    assert "timeline_events" in body["tables_found"]


def test_readiness_endpoint_returns_503_with_unhealthy_detail(client_fixture):
    def unhealthy_readiness():
        return {
            "status": "unhealthy",
            "connectivity": False,
            "tables_found": [],
        }

    client_fixture.app.dependency_overrides[is_database_ready] = unhealthy_readiness
    try:
        response = client_fixture.get("/health/ready")
    finally:
        client_fixture.app.dependency_overrides.pop(is_database_ready, None)

    assert response.status_code == 503
    body = response.json()

    assert "detail" in body
    assert body["detail"]["status"] == "unhealthy"
    assert body["detail"]["connectivity"] is False
