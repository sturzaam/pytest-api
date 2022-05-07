import pytest
from starlette.testclient import TestClient

from test_app.fast_api import app, spec

spec(app).cache_openapi(app.routes)


@pytest.fixture
def client():
    yield TestClient(app)
