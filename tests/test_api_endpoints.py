from urllib.parse import quote


def activity_path(name: str) -> str:
    return quote(name, safe="")


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_shape(client):
    response = client.get("/activities")
    data = response.json()

    assert response.status_code == 200
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert {"description", "schedule", "max_participants", "participants"}.issubset(
        data["Chess Club"].keys()
    )


def test_signup_succeeds_for_new_participant(client):
    activity = "Chess Club"
    email = "new.student@mergington.edu"

    response = client.post(
        f"/activities/{activity_path(activity)}/signup",
        params={"email": email},
    )
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity]["participants"]

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity}"
    assert email in participants


def test_signup_returns_404_for_unknown_activity(client):
    response = client.post(
        "/activities/Unknown%20Club/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_returns_400_for_duplicate_participant(client):
    activity = "Chess Club"
    existing_email = "michael@mergington.edu"

    response = client.post(
        f"/activities/{activity_path(activity)}/signup",
        params={"email": existing_email},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_removes_participant(client):
    activity = "Chess Club"
    email = "daniel@mergington.edu"

    response = client.delete(
        f"/activities/{activity_path(activity)}/participants",
        params={"email": email},
    )
    activities_response = client.get("/activities")
    participants = activities_response.json()[activity]["participants"]

    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity}"
    assert email not in participants


def test_unregister_returns_404_for_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown%20Club/participants",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_returns_404_for_missing_participant(client):
    activity = "Chess Club"

    response = client.delete(
        f"/activities/{activity_path(activity)}/participants",
        params={"email": "not.registered@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
