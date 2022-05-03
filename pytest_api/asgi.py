import functools
import warnings

import pytest
from fastapi.openapi.utils import get_openapi

from .schemas import to_json_schema
from .types import ASGIApp

BEHAVIORS = dict()
ROUTES = dict()
OPEN_API = {
    "paths": {},
    "components": {
        "schemas": {},
    },
}


class ASGIMiddleware:
    openapi_schema = None

    def __init__(self, app: ASGIApp):
        self.app = app
        self.cache_openapi()

    async def __call__(self, scope, receive, send):
        self._path = scope["path"]
        self._method = scope["method"].lower()
        if self._path not in BEHAVIORS:
            warnings.warn(
                f"The consequence for not describing a behavior for {self._path}."
            )
        else:
            func, status_code = BEHAVIORS[self._path]
            self.set_app_route()
            self.update_responses(func, status_code)
            self.handle_request_body(func)

        await self.app(scope, receive, send)

    @classmethod
    def openapi_behaviors(cls, app):
        def custome_openapi():
            if app.openapi_schema:
                return app.openapi_schema
            cls.cache_openapi(app, routes=app.routes)
            pytest.main(["-x", "tests", "-rP", "-vv"])
            app.openapi_schema.update(OPEN_API)
            return OPEN_API

        return custome_openapi

    def cache_openapi(self, routes={}):
        self.openapi_schema = get_openapi(
            title="PyTest-API Generated",
            version="3.0.0",
            description="This OpenAPI schema was generated from PyTests",
            routes=routes,
        )
        OPEN_API.update(self.openapi_schema)

    def set_app_route(self):
        for app_route in self.app.app.app.routes:
            if not app_route.include_in_schema:
                continue
            if not app_route.path == self._path:
                continue
            self.app_route = app_route

    def update_responses(self, func, status_code):
        try:
            OPEN_API["paths"][self._path][self._method]["responses"][status_code][
                "description"
            ]
        except KeyError as e:
            if self._path in e.args:
                OPEN_API["paths"][self._path] = {
                    self._method: {"responses": {status_code: {}}}
                }
            if "responses" in e.args:
                OPEN_API["paths"][self._path][self._method]["responses"] = {
                    status_code: {}
                }

        OPEN_API["paths"][self._path][self._method]["responses"][status_code][
            "description"
        ] = func.__doc__

    def handle_request_body(self, func):
        if self._method == "get":
            return
        try:
            to_json_schema(OPEN_API, {"name": "behavior"}, "Behavior")
            request_example = OPEN_API["paths"][self._path][self._method][
                "requestBody"
            ]["content"]["application/json"]["examples"]
        except KeyError as e:
            if "requestBody" in e.args:
                OPEN_API["paths"][self._path][self._method]["requestBody"] = {
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Behavior"},
                            "examples": {func.__name__: {}},
                        }
                    }
                }
                request_example = OPEN_API["paths"][self._path][self._method][
                    "requestBody"
                ]["content"]["application/json"]["examples"]

            elif "examples" in e.args:
                OPEN_API["paths"][self._path][self._method]["requestBody"]["content"][
                    "application/json"
                ] = {
                    "schema": {"$ref": "#/components/schemas/Behavior"},
                    "examples": {func.__name__: {}},
                }
                request_example = OPEN_API["paths"][self._path][self._method][
                    "requestBody"
                ]["content"]["application/json"]["examples"]
            else:
                raise e

        request_example[func.__name__] = {
            "summary": self.summarize(func),
            "description": func.__doc__,
            "value": {"name": "behavior"},
        }

    def summarize(self, func):
        return func.__name__.replace("_", " ").title()

    def describe(_func=None, *, route="/", status_code=200, method="get"):
        def decorate_behavior(func):
            @functools.wraps(func)
            def wrap_behavior(*args, **kwargs):
                BEHAVIORS[route] = (func, status_code)
                return func(*args, **kwargs)

            return wrap_behavior

        if _func is None:
            return decorate_behavior
        else:
            return decorate_behavior(_func)
