import pytest
from starlette.testclient import TestClient

from test_app.fast_api import app


@pytest.fixture
def client():
    yield TestClient(app)
