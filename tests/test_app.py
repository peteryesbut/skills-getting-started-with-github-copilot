import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Tennis Club" in data
    assert "participants" in data["Tennis Club"]
    assert "max_participants" in data["Tennis Club"]

def test_signup_success():
    # Use a unique email to avoid conflicts
    email = "test_signup@example.com"
    response = client.post(f"/activities/Tennis Club/signup?email={email}")
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]

    # Verify added
    response2 = client.get("/activities")
    data = response2.json()
    assert email in data["Tennis Club"]["participants"]

def test_signup_duplicate():
    email = "test_duplicate@example.com"
    # First signup
    client.post(f"/activities/Tennis Club/signup?email={email}")
    # Second signup
    response = client.post(f"/activities/Tennis Club/signup?email={email}")
    assert response.status_code == 400
    result = response.json()
    assert "Already signed up" in result["detail"]

def test_signup_invalid_activity():
    response = client.post("/activities/Invalid Activity/signup?email=test@example.com")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]

def test_delete_success():
    email = "test_delete@example.com"
    # Signup first
    client.post(f"/activities/Tennis Club/signup?email={email}")
    # Delete
    response = client.delete(f"/activities/Tennis Club/signup?email={email}")
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]

    # Verify removed
    response2 = client.get("/activities")
    data = response2.json()
    assert email not in data["Tennis Club"]["participants"]

def test_delete_not_signed_up():
    response = client.delete("/activities/Tennis Club/signup?email=notsigned@example.com")
    assert response.status_code == 400
    result = response.json()
    assert "Not signed up" in result["detail"]

def test_delete_invalid_activity():
    response = client.delete("/activities/Invalid Activity/signup?email=test@example.com")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]

def test_root_redirect():
    response = client.get("/")
    assert response.status_code == 200
    # Since it's a redirect, but TestClient follows redirects by default? Wait, RedirectResponse returns 200 with the content?
    # Actually, TestClient follows redirects, so it should return the HTML.
    assert "text/html" in response.headers["content-type"]