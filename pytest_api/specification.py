import functools
import subprocess  # nosec
import warnings
from multiprocessing import freeze_support

from fastapi.openapi.utils import get_openapi
from .concurency import BehaviorManager, Examples
from .types import ASGIApp

BEHAVIORS = dict()
BehaviorManager.register("examples", Examples)
BehaviorManager.register("get_openapi", get_openapi)
behavior_manager = BehaviorManager()


#app = behavior_manager.App()
# examples = behavior_manager.examples()
# BehaviorManager.register("responses", Responses)
# BehaviorManager.register("spec", SpecificationMiddleware)
# BehaviorManager.register("operator", get_operator_module)
# BehaviorManager.register(
#     "routes", self._responses.list(), proxytype=RoutesProxy
# )
# behavior_manager = BehaviorManager()


class SpecificationMiddleware:
    def __init__(self, app: ASGIApp):
        self._app = app
        #self._examples = behavior_manager.examples()
        #behavior_manager.start()
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
            #setattr(self._examples, self._path, self.app_route.responses)

        await self._app(scope, send, receive)

    @classmethod
    def get_openapi_behaviors(cls, app):
        spec = cls(app)
        if spec._app.openapi_schema:
            return spec._app.openapi_schema
        openapi_schema = get_openapi(
            title="Custom title",
            version="2.5.0",
            description="This is a very custom OpenAPI schema",
            routes=spec._app.routes,
        )
        openapi_schema["info"]["x-logo"] = {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
        }
        spec._app.openapi_schema = openapi_schema
        return spec._app.openapi_schema


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
