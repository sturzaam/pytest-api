from typing import Any, AnyStr, Callable

BEHAVIORS = dict()
OPEN_API = dict()


def handle_responses(path: AnyStr, method: AnyStr, status_code: int, func: Callable):
    """_summary_

    Args:
        path (AnyStr): which is also called payload
        method (AnyStr): GET, POST, UPDATE, PUT and DELETE
        status_code (int): also call the verb
        func (Callable): reference to the pytest function

    Raises:
        e: The KeyError from the open api schema
    """

    try:
        response_status_code(path, method, status_code)["description"] = func.__doc__
    except KeyError as e:
        if path in e.args:
            init_path(path, method, status_code)
        elif method in e.args:
            init_method(path, method, func)
        elif "responses" in e.args:
            init_responses(path, method, status_code)
        elif status_code in e.args:
            init_status_code(path, method, status_code)
        else:
            raise e
        handle_responses(path, method, status_code, func)


def handle_request_body(body: Any, path: AnyStr, method: AnyStr, func: Callable):
    """_summary_

    Args:
        body (Any): also called the payload
        path (AnyStr): also called the endpoint
        method (AnyStr): also call the verb
        func (Callable): reference to the pytest function

    Raises:
        e: The KeyError from the open api schema
    """
    example = {
        "summary": summarize(func),
        "description": func.__doc__,
        "value": body,
    }
    try:
        request_body_exampl(path, method)[func.__name__] = example
    except KeyError as e:
        if method in e.args:
            init_method(path, method, func)
        elif "requestBody" in e.args:
            init_request_body(path, method, func)
        elif "examples" in e.args:
            init_example(path, method, func)
        else:
            raise e
        handle_request_body(body, path, method, func)


def to_json_schema(body: Any, name: AnyStr):

    """Returns an OpenAPI standard dict of json elements.

    Parameters
    ----------
    body : dict, required
        A tuple of key, value pairs where value is \n
            a string or \n
            a list of strings or \n
            a list of key, value pairs
    """

    """Returns an OpenAPI standard dict of json elements.

    Args:
        body (Any): A tuple of key, value pairs where value is \n
            a string or \n
            a list of strings or \n
            a list of key, value pairs
        name (AnyStr): Name of the open api component schema

    Returns:
        dict: _description_
    """
    schema = {}
    schema[name] = {"type": "object"}
    schema[name]["properties"] = {}
    if name not in OPEN_API["components"]["schemas"].keys():
        OPEN_API["components"]["schemas"][name] = schema[name]
    for key, value in body.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    OPEN_API["components"]["schemas"][name]["properties"].update(
                        {key: item}
                    )
                else:
                    OPEN_API["components"]["schemas"][name]["properties"].update(
                        {key: to_json_schema(item, name)}
                    )
        else:
            OPEN_API["components"]["schemas"][name]["properties"].update(
                {key: {"type": "string"}}
            )
    return {"$ref": f"#/components/schemas/{name}"}


def response_status_code(path, method, status_code):
    status_code_string = str(status_code)
    responses = OPEN_API["paths"][path][method]["responses"]
    if status_code_string in responses:
        responses[status_code] = responses[status_code_string]
        del responses[status_code_string]
    return responses[status_code]


def request_body_exampl(path, method):
    return OPEN_API["paths"][path][method]["requestBody"]["content"][
        "application/json"
    ]["examples"]


def init_status_code(path, method, status_code):
    OPEN_API["paths"][path][method]["responses"][status_code] = {}


def init_responses(path, method, status_code):
    OPEN_API["paths"][path][method]["responses"] = {status_code: {}}


def init_path(path, method, status_code):
    OPEN_API["paths"][path] = {method: {"responses": {status_code: {}}}}


def init_method(path, method, func):
    OPEN_API["paths"][path][method] = {}


def init_request_body(path, method, func):
    OPEN_API["paths"][path][method]["requestBody"] = {
        "content": {
            "application/json": {
                "schema": {"$ref": f"#/components/schemas/{pascal(func)}"},
                "examples": {func.__name__: {}},
            }
        }
    }


def init_example(path, method, func):
    OPEN_API["paths"][path][method]["requestBody"]["content"]["application/json"] = {
        "schema": {"$ref": f"#/components/schemas/{pascal(func)}"},
        "examples": {func.__name__: {}},
    }


def summarize(func):
    return func.__name__.replace("_", " ").title()


def pascal(func):
    return func.__name__.replace("_", " ").title().replace(" ", "")
