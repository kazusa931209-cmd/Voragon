from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_200_and_status() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["service"] == "voragon-realtime-backend"
    assert body["asr"]["ready"] is True
    assert body["asr"]["backend"] == "mock"
    assert body["asr"]["model"] == "large-v3-turbo"
