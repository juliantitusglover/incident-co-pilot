from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.exception_handlers import register_exception_handlers
from backend.services.errors import NotFoundError, ValidationError


def _client_with_exception_routes():
    app = FastAPI()
    register_exception_handlers(app)

    @app.get("/not-found")
    def not_found():
        raise NotFoundError("missing")

    @app.get("/validation-error")
    def validation_error():
        raise ValidationError("bad input")

    return TestClient(app)


def test_not_found_error_maps_to_404_response():
    client = _client_with_exception_routes()

    response = client.get("/not-found")

    assert response.status_code == 404
    assert response.json() == {"detail": "missing"}


def test_validation_error_maps_to_400_response():
    client = _client_with_exception_routes()

    response = client.get("/validation-error")

    assert response.status_code == 400
    assert response.json() == {"detail": "bad input"}
