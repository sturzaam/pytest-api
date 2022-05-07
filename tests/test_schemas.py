from pytest_api.schemas import (
    OPEN_API,
    handle_request_body,
    handle_responses,
    to_json_schema,
)

path = "foo"
method = "bar"
status_code = 0


def test_handle_respones_path_exception():
    assert path not in OPEN_API["paths"]
    handle_responses(path, "GET", 200, test_handle_respones_path_exception)
    assert path in OPEN_API["paths"]


def test_handle_respones_method_exception():
    assert method not in OPEN_API["paths"][path]
    handle_responses(path, method, 200, test_handle_respones_method_exception)
    assert method in OPEN_API["paths"][path]


def test_handle_respones_status_code_exception():
    assert status_code not in OPEN_API["paths"][path][method]["responses"]
    handle_responses(
        path, method, status_code, test_handle_respones_status_code_exception
    )
    assert status_code in OPEN_API["paths"][path][method]["responses"]


def test_handle_request_body_exception():
    assert "requestBody" not in OPEN_API["paths"][path][method]
    handle_request_body({}, path, method, test_handle_request_body_exception)
    assert "requestBody" in OPEN_API["paths"][path][method]


def test_handle_request_method_exception():
    method = "PUT"
    assert method not in OPEN_API["paths"][path]
    handle_request_body({}, path, method, test_handle_request_method_exception)
    assert method in OPEN_API["paths"][path]


def test_to_json_schema():
    assert "foo" not in OPEN_API["components"]["schemas"]
    to_json_schema(
        {
            "bar": [{"baz": "test"}, "biz"],
        },
        "foo",
    )
    assert "foo" in OPEN_API["components"]["schemas"]
    assert OPEN_API["components"]["schemas"]["foo"]["type"] == "object"
    assert OPEN_API["components"]["schemas"]["foo"]["properties"]["bar"] == "biz"
    assert OPEN_API["components"]["schemas"]["foo"]["properties"]["baz"] == {
        "type": "string"
    }
