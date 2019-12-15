from contextlib import contextmanager, ExitStack
from typing import ContextManager, Iterator, List, TypeVar, Union

T = TypeVar('T')
ItemOrList = Union[T, List[T]]


def get_package_root() -> str:
    return __package__.split('.')[0]


def iter_list_items(*args: ItemOrList[T]) -> Iterator[T]:
    for item_or_list in args:
        if isinstance(item_or_list, List):
            yield from item_or_list
        else:
            yield item_or_list


@contextmanager
def combine_contexts(*managers: ItemOrList[ContextManager]):
    managers: List[ContextManager] = list(iter_list_items(*managers))
    stack = ExitStack()
    for manager in managers:
        stack.enter_context(manager)
    yield stack
    stack.close()
