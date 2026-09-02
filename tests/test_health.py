from fastapi.testclient import TestClient

from gateway.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_root() -> None:
    response = client.get("/api/v1")

    assert response.status_code == 200
    assert response.json() == {"service": "api-gateway", "version": "v1"}
