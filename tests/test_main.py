from test_app.main import spec


@spec.describe
def test_default_route(client):
    """
    GIVEN
    WHEN root endpoint is called with GET method
    THEN response with status 200 and body OK is returned
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "OK"}
    assert in_content(client, response.status_code, test_default_route.__doc__)


@spec.describe(route="/health-check/", status_code=200)
def test_health_check(client):
    """
    GIVEN "/health-check/"
    WHEN health check endpoint is called with GET method
    THEN response with status 200 and body OK is returned
    """
    response = client.get("/health-check/")
    assert response.json() == {"message": "OK"}
    assert in_content(client, response.status_code, test_health_check.__doc__)


def in_content(client, status_code, doc):
    for route in filter(
        lambda route: route.include_in_schema, client.app.router.routes
    ):
        return route.responses[status_code]["content"]["description"] == doc
