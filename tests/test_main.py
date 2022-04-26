from pprint import pprint
from io import UnsupportedOperation

import pytest
from test_app.main import spec
from pytest_api.specification import BEHAVIORS

@spec.describe
def test_default_route(client):
    """
    GIVEN
    WHEN root endpoint is called with GET method
    THEN response with status 200 and body OK is returned
    """
    path = "/"
    response = client.get(path)
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}
    assert in_content(client, path, response.status_code, test_default_route.__doc__)
    assert "/" in BEHAVIORS

@spec.describe(route="/health-check/", status_code=200)
def test_health_check(client):
    """
    GIVEN "/health-check/"
    WHEN health check endpoint is called with GET method
    THEN response with status 200 and body OK is returned
    """
    path = "/health-check/"
    response = client.get(path)
    assert response.json() == {"message": "OK"}
    assert in_content(client, path, response.status_code, test_health_check.__doc__)
    assert "/health-check/" in BEHAVIORS

def test_consequences(client):
    with pytest.warns() as miss_behaved:
        client.get("/missing-description-decorator")
    assert "The consequence for not describing a behavior" in str(miss_behaved[0].message.args[0])

def in_content(client, path, status_code, doc):
    for route in filter(
        lambda route: route.path == path, client.app.router.routes
    ):
        return route.responses[status_code]["content"]["description"] == doc
