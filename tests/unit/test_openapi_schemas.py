from pytest_api.schemas import (
    Body,
    Callable,
    Components,
    Method,
    OpenApi,
    Path,
    Schema,
    Status_Code,
)


def test_openapi_components():
    openApi = OpenApi()
    assert openApi is not None
    assert openApi.components is not None
    assert isinstance(openApi.components, Components)


def test_openapi_schemas():
    openApi = OpenApi(components=Components())
    assert openApi is not None
    assert openApi.components.schemas is not None
    assert isinstance(openApi.components.schemas, Schema)


def test_foo_schema():
    openApi = OpenApi()
    m = openApi.components.copy(update={"schemas": dict(Schema(title="foo"))})
    assert "foo" in m.schemas.keys()
    assert isinstance(m.schemas["foo"], Schema)

    foo = m.schemas["foo"]
    assert not hasattr(foo, "title")
    assert foo.type == "object"


def test_path():
    path = Path(method=str())
    assert isinstance(path.method, bytes)


def test_method():
    method = Method(status_code=int())
    assert isinstance(method.status_code, int)


def test_status_code():
    status_code = Status_Code(func=Callable)
    assert isinstance(status_code.func, Callable)


def test_body():
    body = Body(path=str())
    assert isinstance(body.path, bytes)
