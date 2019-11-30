from ....utils import register_action
from nose.tools import *
from unittest import TestCase


class RegistryTest(TestCase):

    def test_root(self):

        class Worker:
            @register_action('test')
            def handle_test(self):
                pass

        actions = getattr(Worker, '__actions__')
        assert_is_not_none(actions)
        assert_in('test', actions)
        assert_equal(1, len(actions))
        assert_equal(Worker.handle_test, actions['test'])

    def test_child(self):

        class Parent:
            pass

        class Child(Parent):
            @register_action('test')
            def handle_test(self):
                pass

        actions = getattr(Child, '__actions__')
        assert_is_not_none(actions)
        assert_in('test', actions)
        assert_equal(1, len(actions))
        assert_equal(Child.handle_test, actions['test'])
