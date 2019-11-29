from typing import Any, Dict, NamedTuple, Type
from .utils import combine_named_tuples
from .model import CommonParams
import abc


class AbstractService(abc.ABC):

    # cannot define here
    # __actions__: Dict[str, Callable] = dict()

    def __init__(self, common_params: CommonParams, service_params: NamedTuple):
        self.params: NamedTuple = combine_named_tuples(common_params, service_params, handle_methods=True)
        self.tools: Dict[str, Any] = dict()
        self.data: Dict[str, Any] = dict()
        self.initialize()

    def __call__(self, *args, **kwargs):
        # TODO: enforce __actions__ defined in subclass
        action: str = self.params.action or 'default'
        if action in self.__actions__:
            handler = self.__actions__[action]
            result = handler(self, *args, **kwargs)
            return result

    def initialize(self) -> None:
        pass

    # TODO: add hooks for call method


class ServiceDef(NamedTuple):
    param_type: Type[NamedTuple]
    service_type: Type[AbstractService]
