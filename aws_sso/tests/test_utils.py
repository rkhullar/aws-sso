from ..utils import *
from unittest import TestCase


class UtilsTest(TestCase):

    def test_package_root(self):
        self.assertEquals(get_package_root(), 'aws_sso')


class HelloTest(TestCase):

    def test_stdout(self):
        message: str = 'hello world'
        with mocked_stdio() as context:
            hello(message=message, count=1)
        context.stdout.seek(0)
        actual = context.stdout.read().strip('\r\n')
        self.assertEqual(message, actual)
