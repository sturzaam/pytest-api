from .api import API
from .middleware import Middleware
from .response import Response
from .specification import Open


class Specification(Open):
    def __init__(self, app=None):
        self.app = app
        if None not in {app}:
            self.init_app(app)

    def init_app(self, app=None):
        self.app = app
        self.client = app.test_client()
        Open.__init__(self, app)