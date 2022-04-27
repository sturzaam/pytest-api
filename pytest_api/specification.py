import functools
import subprocess  # nosec
import warnings
from multiprocessing import freeze_support

from .concurency import BehaviorManager, Responses, RoutesProxy, get_operator_module
from .types import ASGIApp

BEHAVIORS = dict()

BehaviorManager.register("responses", Responses)
BehaviorManager.register("operator", get_operator_module)
manager = BehaviorManager()


class SpecificationMiddleware:
    def __init__(self, app: ASGIApp):
        self._app = app
        manager.start()
        self._responses = manager.responses()
        BehaviorManager.register(
            "routes", self._responses.list(), proxytype=RoutesProxy
        )
        subprocess.Popen(["pytest", "tests", "-rP", "-vv"])  # nosec

    async def __call__(self, scope, send, receive):
        freeze_support()
        self._path = scope["path"]
        if self._path not in BEHAVIORS:
            warnings.warn(
                f"The consequence for not describing a behavior for {self._path}."
            )
        else:
            doc, status_code = BEHAVIORS[self._path]
            self.set_app_route()
            self.update_responses(doc, status_code)
            setattr(self._responses, self._path, self.app_route.responses)

        await self._app(scope, send, receive)

    @property
    def routes(self):
        return [item for item in self._responses.list()]

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
                    "content": {
                        "application/xml": {"example": {"message": "OK"}},
                        "description": doc,
                    }
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
