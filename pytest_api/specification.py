import functools
import warnings
from io import UnsupportedOperation
from pprint import pprint
import subprocess # nosec

from fastapi.openapi.utils import get_openapi

from .types import ASGIApp

BEHAVIORS = dict()


class SpecificationMiddleware:
    def __init__(self, app: ASGIApp):
        self._app = app
        subprocess.Popen(["pytest", "tests", "-rP", "-vv"])  # nosec


    async def __call__(self, scope, send, receive):
        self._path = scope["path"]
        if not self._path in BEHAVIORS:
            warnings.warn(f"The consequence for not describing a behavior for {self._path}.")
        else:
            func, status_code = BEHAVIORS[self._path]
            self.example(func, status_code)
        await self._app(scope, send, receive)

    def example(self, func, status_code):
        for app_route in self._app.app.app.routes:
            if not app_route.include_in_schema:
                continue
            if app_route.path == self._path:
                app_route.responses.update(
                    {
                        status_code: {
                            "content": {
                                "application/xml": {"example": {"message": "OK"}},
                                "description": func.__doc__,
                            }
                        }
                    }
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
