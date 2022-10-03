from pytest_api.schemas import Components, OpenApi


def test_openapi_components():
    openApi = OpenApi()
    assert openApi is not None
    assert openApi.components is None


def test_openapi_schemas():
    openApi = OpenApi(components=Components())
    assert openApi is not None
    assert openApi.components.schemas is not None
