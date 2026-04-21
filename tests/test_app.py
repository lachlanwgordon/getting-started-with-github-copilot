
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

# Helper to reset activities state between tests
def reset_activities():
    for activity in activities.values():
        activity["participants"] = []

@pytest.fixture(autouse=True)
def run_before_and_after_tests():
    # Arrange: Reset state before each test
    reset_activities()
    yield
    reset_activities()

def test_get_activities():
    # Arrange: None needed, state is reset
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Science Club" in data

def test_signup_success():
    # Arrange
    email = "student1@mergington.edu"
    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    # Confirm participant is added
    activities = client.get("/activities").json()
    assert email in activities["Chess Club"]["participants"]

def test_signup_duplicate():
    # Arrange
    email = "student2@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    # Act
    response = client.post(f"/activities/Chess Club/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_invalid_activity():
    # Arrange
    email = "student3@mergington.edu"
    # Act
    response = client.post(f"/activities/Nonexistent/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]

def test_unregister_success():
    # Arrange
    email = "student4@mergington.edu"
    client.post(f"/activities/Chess Club/signup?email={email}")
    # Act
    response = client.post(f"/activities/Chess Club/unregister?email={email}")
    # Assert
    assert response.status_code == 200
    assert "Removed" in response.json()["message"]
    # Confirm participant is removed
    activities = client.get("/activities").json()
    assert email not in activities["Chess Club"]["participants"]

def test_unregister_not_registered():
    # Arrange
    email = "student5@mergington.edu"
    # Act
    response = client.post(f"/activities/Chess Club/unregister?email={email}")
    # Assert
    assert response.status_code == 404
    assert "not registered" in response.json()["detail"]
