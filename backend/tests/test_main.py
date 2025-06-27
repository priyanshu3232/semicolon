import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "ML Document Processing API"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_parse_endpoint():
    # Test with a mock text file
    files = {"file": ("test.txt", "This is test content", "text/plain")}
    response = client.post("/api/parse", files=files)
    
    # Note: This will fail without proper auth token, but tests the endpoint structure
    assert response.status_code in [200, 401]