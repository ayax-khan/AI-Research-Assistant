import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealth:
    def test_health_check(self):
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


class TestAuth:
    def test_register_validation(self):
        response = client.post("/api/auth/register", json={"name": "Test"})
        assert response.status_code == 422

    def test_login_validation(self):
        response = client.post("/api/auth/login", json={})
        assert response.status_code == 422

    def test_me_unauthorized(self):
        response = client.get("/api/auth/me")
        assert response.status_code == 401
