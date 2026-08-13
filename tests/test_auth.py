from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_register_and_login():
    register_response = client.post("/v1/register", json={
        "name": "Test User",
        "email": "testuser_pytest@example.com",
        "password": "TestPass123",
        "phone": "9999999999"
    })

    assert register_response.status_code in [200, 400]

    login_response = client.post("/v1/login", json={
        "email": "testuser_pytest@example.com",
        "password": "TestPass123"
    })

    assert login_response.status_code == 200
    data = login_response.json()
    assert "access_token" in data
    assert data["role"] == "user"


def test_login_wrong_password_fails():
    response = client.post("/v1/login", json={
        "email": "testuser_pytest@example.com",
        "password": "WrongPassword"
    })

    assert response.status_code == 401

