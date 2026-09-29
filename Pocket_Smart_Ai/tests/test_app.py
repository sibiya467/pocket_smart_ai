import os

os.environ["USE_MOCK_AI"] = "true"
os.environ["SECRET_KEY"] = "test-secret"


from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert (
        response.json()["status"]
        == "ok"
    )


def test_register_and_login():

    email = (
        "test_project_user@example.com"
    )

    response = client.post(
        "/register",
        json={
            "name": "Test User",
            "email": email,
            "password": "secret123"
        }
    )

    assert response.status_code in (
        200,
        409
    )


    response = client.post(
        "/login",
        json={
            "email": email,
            "password": "secret123"
        },
        follow_redirects=False
    )

    assert response.status_code == 303


def test_protected_home_requires_login():

    response = client.post(
        "/generate-home",
        json={
            "budget": 10000,
            "rooms": [
                "Bedroom"
            ],
            "style": "Modern",
            "items": {}
        }
    )

    assert response.status_code == 401