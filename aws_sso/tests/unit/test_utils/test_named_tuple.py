from ....utils import combine_named_tuples, pick_class_mame
from nose.tools import assert_equal, assert_in
from parameterized import parameterized
from typing import Any, List, NamedTuple
from unittest import TestCase


class A(NamedTuple):
    message: str = 'hello world'


class B(NamedTuple):
    count: int = 1


class PickClassNameTest(TestCase):

    @parameterized.expand([
        ([A(), B()], True, False, 'A'),
        ([A(), B()], False, True, 'B'),
        (['text', 4], True, False, 'str'),
        (['text', 4], False, True, 'int')
    ])
    def test_normal(self, items: List[Any], pick_first, pick_last, expected: str):
        actual: str = pick_class_mame(items, pick_first, pick_last)
        assert_equal(expected, actual)

    def test_empty(self):
        with self.assertRaises(ValueError):
            pick_class_mame(items=[], pick_first=False, pick_last=True)

    @parameterized.expand([
        ([None], True),
        ([None], False)
    ])
    def test_control(self, items: List[Any], control: bool):
        with self.assertRaises(ValueError) as context:
            pick_class_mame(items=items, pick_first=control, pick_last=control)
        error = context.exception.args[0]
        assert_in('pick_first', error)
        assert_in('pick_last', error)
