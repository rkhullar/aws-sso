from ....utils import mock_input_output
from nose.tools import assert_equal
from unittest import TestCase


class HelloTest(TestCase):

    def test_mock_io(self):
        message: str = 'this is the kitchen'
        with mock_input_output() as mocked:
            print(message)
        actual = mocked.stdout.read().strip('\r\n')
        assert_equal(message, actual)
