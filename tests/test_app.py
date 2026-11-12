import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(
        app_module,
        "activities",
        {
            "Chess Club": {
                "description": "Learn chess",
                "schedule": "Fridays",
                "max_participants": 12,
                "participants": ["existing@mergington.edu"],
            }
        },
    )

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_details_and_participants(client):
    response = client.get("/activities")

    assert response.status_code == 200
    assert response.json()["Chess Club"]["participants"] == ["existing@mergington.edu"]


def test_signup_adds_participant(client):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "new@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Signed up new@mergington.edu for Chess Club"
    assert "new@mergington.edu" in client.get("/activities").json()["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "existing@mergington.edu"},
    )

    assert response.status_code == 409
    assert client.get("/activities").json()["Chess Club"]["participants"] == [
        "existing@mergington.edu"
    ]


def test_signup_returns_not_found_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404


def test_unregister_removes_participant(client):
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "existing@mergington.edu"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Unregistered existing@mergington.edu from Chess Club"
    assert client.get("/activities").json()["Chess Club"]["participants"] == []


def test_unregister_returns_not_found_for_unregistered_participant(client):
    response = client.delete(
        "/activities/Chess%20Club/signup",
        params={"email": "unknown@mergington.edu"},
    )

    assert response.status_code == 404
    assert client.get("/activities").json()["Chess Club"]["participants"] == [
        "existing@mergington.edu"
    ]


def test_unregister_returns_not_found_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
