"""
Tests for the Mergington High School API
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirect(self, client):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    """Tests for the activities endpoints"""

    def test_get_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_structure(self, client):
        """Test that activity data has correct structure"""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_chess_club_exists(self, client):
        """Test that Chess Club activity exists with correct data"""
        response = client.get("/activities")
        activities = response.json()
        
        chess = activities["Chess Club"]
        assert chess["description"] == "Learn strategies and compete in chess tournaments"
        assert chess["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess["max_participants"] == 12


class TestSignupEndpoint:
    """Tests for the signup endpoint"""

    def test_signup_for_existing_activity(self, client):
        """Test signing up for an existing activity"""
        response = client.post("/activities/Chess Club/signup", params={"email": "newstudent@mergington.edu"})
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
        assert "Chess Club" in data["message"]

    def test_signup_for_nonexistent_activity(self, client):
        """Test that signing up for non-existent activity returns 404"""
        response = client.post("/activities/Nonexistent Club/signup", params={"email": "student@mergington.edu"})
        assert response.status_code == 404
        
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant"""
        # Get initial participants
        response = client.get("/activities")
        initial_participants = response.json()["Programming Class"]["participants"].copy()
        initial_count = len(initial_participants)
        
        # Sign up a new student
        client.post("/activities/Programming Class/signup", params={"email": "newprogrammer@mergington.edu"})
        
        # Verify participant was added
        response = client.get("/activities")
        updated_participants = response.json()["Programming Class"]["participants"]
        assert len(updated_participants) == initial_count + 1
        assert "newprogrammer@mergington.edu" in updated_participants

    def test_multiple_signups(self, client):
        """Test multiple signups to different activities"""
        email = "multisport@mergington.edu"
        
        # Sign up for multiple activities
        response1 = client.post("/activities/Chess Club/signup", params={"email": email})
        response2 = client.post("/activities/Gym Class/signup", params={"email": email})
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Verify both signups were recorded
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Gym Class"]["participants"]


class TestAPIMetadata:
    """Tests for API metadata and configuration"""

    def test_api_title(self, client):
        """Test that API has correct title"""
        assert app.title == "Mergington High School API"

    def test_api_description(self, client):
        """Test that API has correct description"""
        assert "extracurricular activities" in app.description
