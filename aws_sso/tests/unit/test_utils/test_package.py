from ....utils import combine_contexts, get_package_root, iter_list_items
from contextlib import contextmanager
from nose.tools import assert_equal
from parameterized import parameterized
from typing import ContextManager, List
from unittest import TestCase


class PackageTest(TestCase):

    def test_package_root(self):
        assert_equal(get_package_root(), 'aws_sso')

    @classmethod
    def build_example_context_manager(cls, queue: list, stack: list) -> ContextManager:
        @contextmanager
        def example(n: int):
            queue.append(n)
            yield n
            stack.insert(0, n)
        return example

    def test_combine_contexts(self):
        queue, stack = [], []
        example_manager = self.build_example_context_manager(queue, stack)
        managers = [example_manager(i) for i in range(4)]
        with combine_contexts(managers):
            pass
        assert_equal(stack, queue)

    @parameterized.expand([
        ([[1, 2, 3, 4]], [1, 2, 3, 4]),
        ([1, 2, 3, 4], [1, 2, 3, 4]),
        ([[1], 2, 3, 4], [1, 2, 3, 4]),
        ([1, [2, 3, 4]], [1, 2, 3, 4]),
        ([1], [1]),
        ([[1]], [1]),
        ([], []),
        ([[]], [])
    ])
    def test_iter_list_items(self, args, expected: List[int]):
        actual: List[int] = list(iter_list_items(*args))
        assert_equal(expected, actual)
