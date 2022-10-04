from pytest_api.schemas import Components, OpenApi, Schema


def test_openapi_components():
    openApi = OpenApi()
    assert openApi is not None
    assert openApi.components is not None


def test_openapi_schemas():
    openApi = OpenApi(components=Components())
    assert openApi is not None
    assert openApi.components.schemas is not None

def test_foo_schema():
    openApi = OpenApi()
    foo = Schema()
    m = openApi.components.copy(update={"schemas":{"foo":foo}})
    assert "foo" in m.schemas.keys()