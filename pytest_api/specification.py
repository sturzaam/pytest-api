import functools
import subprocess  # nosec

from fastapi.openapi.utils import get_openapi

from .types import ASGIApp

BEHAVIORS = dict()


class SpecificationMiddleware:
    def __init__(self, app: ASGIApp):
        self._app = app
        subprocess.Popen(["pytest", "tests", "-rP"])  # nosec

    async def __call__(self, scope, send, receive):
        for route in self._app.app.app.routes:
            if route.include_in_schema and scope["path"] in BEHAVIORS:
                func, status_code = BEHAVIORS[scope["path"]]
                route.responses.update(
                    {
                        status_code: {
                            "content": {
                                "application/json": {"example": {"message": "OK"}},
                                "description": func.__doc__,
                            }
                        }
                    }
                )
        await self._app(scope, send, receive)

    def custom_openapi(self):
        return get_openapi(
            title="PyTest-API",
            version="0.1.0",
            description="Test Driven OpenAPI schema",
            routes=self._app.routes,
        )

    def describe(_func=None, *, route="/", status_code=200):
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
