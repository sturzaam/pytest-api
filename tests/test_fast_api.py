import pytest

from pytest_api import BEHAVIORS, OPEN_API
from test_app.fast_api import spec


@spec.describe
def test_default_route(client):
    """
    GIVEN
    WHEN root endpoint is called with GET method
    THEN response with status 200 and body OK is returned
    """
    path = "/"
    response = client.get(path, headers={"spec-description": test_default_route.id})
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}
    assert path in BEHAVIORS
    assert response_description(path, "get", response.status_code, test_default_route)


@spec.describe(route="/health-check/")
def test_health_check(client):
    """
    GIVEN "/health-check/"
    WHEN health check endpoint is called with GET method
    THEN response with status 200 and body OK is returned
    """
    path = "/health-check/"
    response = client.get(path, headers={"spec-description": test_health_check.id})
    assert response.json() == {"message": "OK"}
    assert path in BEHAVIORS
    assert response_description(path, "get", response.status_code, test_health_check)


@spec.describe(route="/behavior-example/")
def test_example_body(client):
    """
    GIVEN behavior in body
    WHEN example behavior endpoint is called with POST method
    THEN response with status 200 and body OK is returned
    """
    path = "/behavior-example/"
    response = client.post(
        path, json={"name": "behavior"}, headers={"spec-example": test_example_body.id}
    )
    assert response.json() == {"message": "OK"}
    assert path in BEHAVIORS
    assert request_body_example_description(path, "post", test_example_body)


def test_consequences(client):
    with pytest.warns() as miss_behaved:
        client.get("/missing-description-decorator")
    assert "The consequence for not describing a behavior" in str(
        miss_behaved[0].message.args[0]
    )
    assert "/missing-description-decorator" not in BEHAVIORS


def response_description(path, method, status_code, func):
    return (
        OPEN_API["paths"][path][method]["responses"][status_code]["description"]
        == func.__doc__
    )


def request_body_example_description(path, method, func):
    return (
        OPEN_API["paths"][path][method]["requestBody"]["content"]["application/json"][
            "examples"
        ][func.__name__]["description"]
        == func.__doc__
    )
