import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities state before each test to ensure test isolation."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities(client):
    # Arrange
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data
    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_for_activity_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]


def test_signup_for_activity_not_found(client):
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"
    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_signup_for_activity_already_signed_up(client):
    # Arrange
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"
    # Sign up once
    first_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert first_response.status_code == 200
    # Act - try to sign up again
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert "already signed up" in data["detail"]


def test_remove_participant_success(client):
    # Arrange
    activity_name = "Chess Club"
    email = "remove.me@mergington.edu"
    signup_response = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    assert signup_response.status_code == 200

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert activity_name in data["message"]

    activities_response = client.get("/activities")
    assert activities_response.status_code == 200
    activities_data = activities_response.json()
    assert email not in activities_data[activity_name]["participants"]


def test_remove_participant_activity_not_found(client):
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]


def test_remove_participant_student_not_signed_up(client):
    # Arrange
    activity_name = "Gym Class"
    email = "not.signed.up@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "not signed up" in data["detail"]