import re
import yaml
import json
import inspect
import xml.etree.ElementTree as elementTree
from urllib.parse import urlparse


class Open(object):
    _specification = {
        "openapi": "3.0.2",
        "info": {
            "title": "PyTest-API",
            "description": "Swagger specification for documenting the API",
            "version": "0.0.1",
        },
        "servers": [{"url": "http://localhost"}],
        "paths": {},
        "components": {
            "schemas": {},
            "securitySchemes": {"bearerAuth": {"type": "http", "scheme": "bearer"}},
        },
    }

    def __init__(self, app):
        self.__dict__ = self._specification
        self.app = app

    def dump_static_yaml(self):
        dict_file = {
            "openapi": self.openapi,
            "info": self.info,
            "servers": self.servers,
            "paths": self.paths,
            "components": self.components,
        }
        file_path = self.app.config["SPECIFICATION_PATH"]
        with open(file_path, "w") as file:
            yaml.dump(dict_file, file)

    def content_type(self, **kwargs):
        self._content_type = kwargs.get("content_type", "application/json")

    def security(self):
        return [{"bearerAuth": []}]

    def request_body(self):
        if self._request_data is None:
            return {"content": {self._content_type: {}}}
        self.to_request_schema()
        return {
            "content": {
                self._content_type: {
                    "schema": self._request_Schema,
                    "examples": self.examples(self._request_data),
                }
            }
        }

    def status_code(self, response):
        return str(response.status_code)

    def examples(self, data):
        return {self._example: {"value": data}}

    def responses(self):
        self._response_data = self._response.data.decode()
        self.to_response_schema()
        self._status_code = str(self._response.status_code)
        return {
            self._status_code: {
                "description": self._response.status,
                "content": {
                    self._content_type: {
                        "schema": self._response_Schema,
                        "examples": self.examples(self._response_data),
                    }
                },
            }
        }

    def path(self, responses):
        return {
            self._method: {
                "security": self.security(),
                "requestBody": self.request_body(),
                "responses": responses,
            }
        }

    def get(self, path, **kwargs):
        self.content_type(**kwargs)
        self._example = inspect.stack()[1].function
        self._method = inspect.stack()[0].function
        self._response = self.client.get(path, **kwargs)
        self._request_data = kwargs.get("data")
        self.update(path)
        return self._response

    def post(self, path, **kwargs):
        self.content_type(**kwargs)
        self._example = inspect.stack()[1].function
        self._method = inspect.stack()[0].function
        self._response = self.client.post(path, **kwargs)
        self._request_data = kwargs.get("data")
        self.update(path)
        return self._response

    def delete(self, path, **kwargs):
        self.content_type(**kwargs)
        self._example = inspect.stack()[1].function
        self._method = inspect.stack()[0].function
        self._response = self.client.delete(path, **kwargs)
        self._request_data = kwargs.get("data")
        self.update(path)
        return self._response

    def patch(self, path, **kwargs):
        self.content_type(**kwargs)
        self._example = inspect.stack()[1].function
        self._method = inspect.stack()[0].function
        self._response = self.client.patch(path, **kwargs)
        self._request_data = kwargs.get("data")
        self.update(path)
        return self._response

    def put(self, path, **kwargs):
        self.content_type(**kwargs)
        self._example = inspect.stack()[1].function
        self._method = inspect.stack()[0].function
        self._response = self.client.put(path, **kwargs)
        self._request_data = kwargs.get("data")
        self.update(path)
        return self._response

    def update(self, path):
        self._name = urlparse(path)
        self._name = self._name.path.rsplit("/", 1)[-1]
        responses = self.responses()
        if path not in self.paths.keys():
            self.paths[path] = self.path(responses)
        elif self._method not in self.paths[path].keys():
            self.paths[path][self._method] = {
                "security": self.security(),
                "requestBody": self.request_body(),
                "responses": responses,
            }
        else:
            if self._request_data is not None:
                self.paths[path][self._method]["requestBody"]["content"][
                    self._content_type
                ]["examples"].update(self.examples(self._request_data))
            if self._status_code in self.paths[path][self._method]["responses"].keys():
                self.paths[path][self._method]["responses"][self._status_code][
                    "content"
                ][self._content_type]["examples"].update(
                    self.examples(self._response_data)
                )
            else:
                self.paths[path][self._method]["responses"].update(responses)

    def namespace(self, element):
        matched = re.match(r"\{(.*)\}", element.tag)
        return matched.group(1) if matched else None

    def name(self, element):
        matched = re.search(r"(\{.*\})?(.*)", element.tag)
        return matched.group(2) if matched else None

    def has_children(self, element):
        return True if len(element) > 0 else False

    def to_request_schema(self):
        if "xml" in self._content_type:
            self._request_Schema = self.to_xml_schema(
                elementTree.fromstring(self._request_data)
            )
        else:
            self._request_Schema = self.to_json_schema(
                json.loads(self._request_data), self._name
            )

    def to_response_schema(self):
        if "xml" in self._content_type:
            self._response_Schema = self.to_xml_schema(
                elementTree.fromstring(self._response_data)
            )
        else:
            self._response_Schema = self.to_json_schema(
                json.loads(self._response_data), self._name
            )

    def to_xml_schema(self, elementTree, namespace=None):
        """Returns an OpenAPI standard dict of xml elements.

        Parameters
        ----------
        elementTree : Element, required
            An xml.etree.ElementTree Element instance
            or list of [Elements] to search
        """
        xml_schema = {}
        name = self.name(elementTree)
        xml_schema[name] = {"type": "object"}
        xml_schema[name]["properties"] = {}
        if name not in self.components["schemas"].keys():
            self.components["schemas"][name] = xml_schema[name]
        if self.namespace(elementTree) != namespace:
            namespace = self.namespace(elementTree)
            xml_schema[name]["xml"] = {"namespace": namespace}
        for element in elementTree:
            propertyName = self.name(element)
            if self.has_children(element):
                self.components["schemas"][name]["properties"].update(
                    {propertyName: self.to_xml_schema(element, namespace)}
                )
            else:
                self.components["schemas"][name]["properties"].update(
                    {propertyName: {"type": "string"}}
                )
        return {"$ref": f"#/components/schemas/{name}"}

    def to_json_schema(self, jsonObject, name):
        """Returns an OpenAPI standard dict of json elements.

        Parameters
        ----------
        jsonObject : Element, required
            An xml.etree.ElementTree Element instance
            or list of [Elements] to search
        """
        schema = {}
        schema[name] = {"type": "object"}
        schema[name]["properties"] = {}
        if name not in self.components["schemas"].keys():
            self.components["schemas"][name] = schema[name]
        for key, value in jsonObject.items():
            if isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        self.components["schemas"][name]["properties"].update(
                            {key: item}
                        )
                    else:
                        self.components["schemas"][name]["properties"].update(
                            {key: self.to_json_schema(item, name)}
                        )
            else:
                self.components["schemas"][name]["properties"].update(
                    {key: {"type": "string"}}
                )
        return {"$ref": f"#/components/schemas/{name}"}
