from .model import CommonParams
from .utils import combine_named_tuples

from abc import ABC
from typing import Any, Dict, NamedTuple, Type


class AbstractService(ABC):

    # cannot define here
    # __actions__: Dict[str, Callable] = dict()

    def __init__(self, common_params: CommonParams, service_params: NamedTuple, default_action: str = 'default', initialize: bool = True):
        self.params: NamedTuple = combine_named_tuples(common_params, service_params, handle_methods=True)
        self.default_action: str = default_action
        self.tools: Dict[str, Any] = dict()
        self.data: Dict[str, Any] = dict()
        if initialize:
            self.initialize()

    # TODO: add hooks for call method

    def __call__(self, *args, **kwargs):
        # TODO: enforce __actions__ defined in subclass
        action: str = self.params.action or self.default_action
        if action in self.__actions__:
            handler = self.__actions__[action]
            result = handler(self, *args, **kwargs)
            return result
        # TODO: handle when action not found

    def initialize(self) -> None:
        pass

    def patch_params(self, **kwargs):
        self.params = self.params._replace(**kwargs)
        self.initialize()


class ServiceDef(NamedTuple):
    param_type: Type[NamedTuple]
    service_type: Type[AbstractService]
