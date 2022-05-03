def to_json_schema(openapi_schema, body, name):
    """Returns an OpenAPI standard dict of json elements.

    Parameters
    ----------
    body : dict, required
        A tuple of key, value pairs where value is \n
            a string or \n
            a list of strings or \n
            a list of key, value pairs
    """
    schema = {}
    schema[name] = {"type": "object"}
    schema[name]["properties"] = {}
    if name not in openapi_schema["components"]["schemas"].keys():
        openapi_schema["components"]["schemas"][name] = schema[name]
    for key, value in body.items():
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    openapi_schema["components"]["schemas"][name]["properties"].update(
                        {key: item}
                    )
                else:
                    openapi_schema["components"]["schemas"][name]["properties"].update(
                        {key: to_json_schema(openapi_schema, item, name)}
                    )
        else:
            openapi_schema["components"]["schemas"][name]["properties"].update(
                {key: {"type": "string"}}
            )
    return {"$ref": f"#/components/schemas/{name}"}
