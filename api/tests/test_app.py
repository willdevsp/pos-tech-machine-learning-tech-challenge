"""Tests for FastAPI endpoints."""

from fastapi.testclient import TestClient

from rocket_tail_api.app import app


def test_health_check() -> None:
    """Verifies health check endpoint returns 200 and healthy status."""
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "model_loaded" in data


def test_recommend_endpoint() -> None:
    """Verifies recommendation endpoint processes POST requests successfully."""
    with TestClient(app) as client:
        response = client.post("/recommend", json={"visitorid": 123, "k": 3})
        assert response.status_code == 200
        data = response.json()
        assert data["visitorid"] == 123
        assert len(data["recommendations"]) == 3
