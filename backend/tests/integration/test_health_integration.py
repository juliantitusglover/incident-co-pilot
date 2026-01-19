def test_health_database_success(client_fixture):
    response = client_fixture.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["connectivity"] == True
    assert "incidents" in response.json()["tables_found"]