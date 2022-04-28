import functools
import warnings

import pytest
from fastapi.openapi.utils import get_openapi

from .types import ASGIApp

BEHAVIORS = dict()
ROUTES = dict()


class SpecificationMiddleware:
    def __init__(self, app: ASGIApp):
        self._app = app

    async def __call__(self, scope, send, receive):
        self._path = scope["path"]
        if self._path not in BEHAVIORS:
            warnings.warn(
                f"The consequence for not describing a behavior for {self._path}."
            )
        else:
            doc, status_code = BEHAVIORS[self._path]
            self.set_app_route()
            self.update_responses(doc, status_code)

        await self._app(scope, send, receive)

    @classmethod
    def openapi_behaviors(cls, app):
        def custome_openapi():
            if app.openapi_schema:
                return app.openapi_schema
            pytest.main(["-x", "tests", "-rP", "-vv"])
            for route in app.routes:
                if route.path in ROUTES:
                    route.responses.update(ROUTES[route.path])
            openapi_schema = get_openapi(
                title="Custom title",
                version="2.5.0",
                description="This is a very custom OpenAPI schema",
                routes=app.routes,
            )
            openapi_schema["info"]["x-logo"] = {
                "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
            }
            app.openapi_schema = openapi_schema
            return app.openapi_schema

        return custome_openapi

    def set_app_route(self):
        for app_route in self._app.app.app.routes:
            if not app_route.include_in_schema:
                continue
            if not app_route.path == self._path:
                continue
            self.app_route = app_route

    def update_responses(self, doc, status_code):
        self.app_route.responses.update(
            {
                status_code: {
                    "description": doc,
                    "content": {
                        "application/json": {"example": {"message": "OK"}},
                    },
                }
            }
        )

    def describe(_func=None, *, route="/", status_code=200):
        def decorate_behavior(func):
            @functools.wraps(func)
            def wrap_behavior(*args, **kwargs):
                BEHAVIORS[route] = (func.__doc__, status_code)
                return func(*args, **kwargs)

            return wrap_behavior

        if _func is None:
            return decorate_behavior
        else:
            return decorate_behavior(_func)
