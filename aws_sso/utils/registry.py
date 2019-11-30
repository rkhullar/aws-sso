from typing import Callable, Dict, Type


def register_action(action: str, mapping_name: str = '__actions__'):

    # https://stackoverflow.com/questions/3589311/get-defining-class-of-unbound-method-object-in-python-3/25959545#25959545

    class RegistryHandler:
        def __init__(self, fn: Callable):
            self.fn = fn

        def __set_name__(self, owner: Type, name: str):
            if not hasattr(owner, mapping_name):
                setattr(owner, mapping_name, dict())

            mapping: Dict[str: Callable] = getattr(owner, mapping_name)
            mapping[action] = self.fn

            setattr(owner, name, self.fn)

    return RegistryHandler


def register_service(cls):
    """discover methods within a class with prefix "handle_" and populate the actions"""
