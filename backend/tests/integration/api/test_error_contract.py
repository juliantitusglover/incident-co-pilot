def test_unknown_route_returns_404(client_fixture):
    response = client_fixture.get("/does-not-exist")

    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
