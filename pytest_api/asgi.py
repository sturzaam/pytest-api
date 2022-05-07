import functools
import warnings

import pytest
from fastapi.openapi.utils import get_openapi
from starlette.types import ASGIApp

from .responders import SpecificationResponder
from .schemas import BEHAVIORS, OPEN_API


class ASGIMiddleware:
    openapi_schema = None

    def __init__(self, app: ASGIApp):
        self.app = app
        self.cache_openapi()

    async def __call__(self, scope, receive, send):
        if scope["path"] not in BEHAVIORS:
            warnings.warn(
                f"The consequence for not describing a behavior for {scope['path']}."
            )
        elif scope["type"] == "http":
            responder = SpecificationResponder(self.app)
            await responder(scope, receive, send)
            return
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

    def describe(_func=None, *, route="/"):
        def decorate_behavior(func):
            @functools.wraps(func)
            def wrap_behavior(*args, **kwargs):
                try:
                    BEHAVIORS[route]
                except KeyError as e:
                    if route in e.args:
                        BEHAVIORS[route] = {str(id(func)): func}
                BEHAVIORS[route][str(id(func))] = func
                return func(*args, **kwargs)

            wrap_behavior.id = str(id(func))
            return wrap_behavior

        if _func is None:
            return decorate_behavior
        else:
            return decorate_behavior(_func)
