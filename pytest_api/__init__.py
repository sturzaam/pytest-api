from .concurency import BehaviorManager, RoutesProxy, Examples
from .specification import SpecificationMiddleware, BEHAVIORS

BehaviorManager.register("responses", Examples)
BehaviorManager.register("spec", SpecificationMiddleware)
#BehaviorManager.register("operator", get_operator_module)
# BehaviorManager.register(
#     "routes", self._responses.list(), proxytype=RoutesProxy
# )
behavior_manager = BehaviorManager()

__all__ = ["SpecificationMiddleware", "BehaviorManager", "RoutesProxy", "behavior_manager", "BEHAVIORS"]
