import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


_INITIAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities_state():
    """Keep tests independent by restoring the in-memory database per test."""
    activities.clear()
    activities.update(copy.deepcopy(_INITIAL_ACTIVITIES))
    yield
    activities.clear()
    activities.update(copy.deepcopy(_INITIAL_ACTIVITIES))


@pytest.fixture
def client():
    return TestClient(app)
