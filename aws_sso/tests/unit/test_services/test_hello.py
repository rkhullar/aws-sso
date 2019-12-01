from ....model import CommonParams
from ....services import HelloParams, HelloWorker
from ....utils import mock_input_output
from nose.tools import assert_equal
from parameterized import parameterized
from unittest import TestCase
import os


class HelloTest(TestCase):

    @staticmethod
    def build_hello(message: str, count: int):
        return os.linesep.join([message] * count)

    @parameterized.expand([
        ('this is the kitchen', 4),
        ('hello world', 1)
    ])
    def test_hello(self, message: str, count: int):
        common_params = CommonParams(service='hello', action='default')
        service_params = HelloParams(message=message, count=count)
        worker = HelloWorker(common_params, service_params)
        with mock_input_output() as mocked:
            worker()
        actual = mocked.stdout.read().strip('\r\n')
        expected = self.build_hello(message=message, count=count)
        assert_equal(expected, actual)
