import operator
from multiprocessing.managers import BaseManager, BaseProxy


class Responses:
    def add(self, path, response):
        self.__dict__[path] = response

    def list(self):
        return [response for response in self.__dict__.items()]


class RoutesProxy(BaseProxy):
    _exposed_ = ["__next__"]

    def __iter__(self):
        return self

    def __next__(self):
        return self._callmethod("__next__")


class BehaviorManager(BaseManager):
    pass


def get_operator_module():
    return operator
