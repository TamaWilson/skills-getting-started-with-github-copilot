from urllib.parse import quote


def activity_path(name: str) -> str:
    return quote(name, safe="")


def test_all_activities_follow_payload_contract(client):
    response = client.get("/activities")
    activities = response.json()

    assert response.status_code == 200
    for details in activities.values():
        assert isinstance(details["description"], str)
        assert isinstance(details["schedule"], str)
        assert isinstance(details["max_participants"], int)
        assert details["max_participants"] > 0
        assert isinstance(details["participants"], list)


def test_activity_name_matching_is_case_sensitive(client):
    response = client.post(
        "/activities/chess%20club/signup",
        params={"email": "student.case@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_then_unregister_keeps_state_consistent(client):
    activity = "Science Club"
    email = "stateful.student@mergington.edu"

    signup_response = client.post(
        f"/activities/{activity_path(activity)}/signup",
        params={"email": email},
    )
    after_signup = client.get("/activities").json()[activity]["participants"]

    unregister_response = client.delete(
        f"/activities/{activity_path(activity)}/participants",
        params={"email": email},
    )
    after_unregister = client.get("/activities").json()[activity]["participants"]

    assert signup_response.status_code == 200
    assert unregister_response.status_code == 200
    assert email in after_signup
    assert email not in after_unregister


def test_current_behavior_allows_over_capacity_signup(client):
    activity = "Chess Club"
    initial = client.get("/activities").json()[activity]
    initial_count = len(initial["participants"])
    max_participants = initial["max_participants"]

    # This captures current behavior (no max capacity validation yet).
    extra_signups = (max_participants - initial_count) + 1
    for index in range(extra_signups):
        email = f"overflow{index}@mergington.edu"
        response = client.post(
            f"/activities/{activity_path(activity)}/signup",
            params={"email": email},
        )
        assert response.status_code == 200

    final_count = len(client.get("/activities").json()[activity]["participants"])
    assert final_count > max_participants
