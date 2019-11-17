from parameterized import parameterized
from nose.tools import assert_equal
from unittest import TestCase
from ..utils import *


class UtilsTest(TestCase):

    def test_package_root(self):
        assert_equal(get_package_root(), 'aws_sso')

    @parameterized.expand([
        ('localhost', None),
        ('example.com', 'example.com'),
        ('sso.example.com', 'example.com')
    ])
    def test_infer_domain(self, value, expected):
        actual = infer_domain(value)
        assert_equal(expected, actual)

    @parameterized.expand([
        ('localhost', 'test_user', 'test_user'),
        ('example.com', 'test_user', 'example.com\\test_user'),
        ('sso.example.com', 'test_user', 'example.com\\test_user')
    ])
    def test_build_domain_username(self, domain, username, expected):
        actual = build_domain_username(domain, username)
        assert_equal(expected, actual)


class HelloTest(TestCase):

    def test_stdout(self):
        message: str = 'this is the kitchen'
        with mocked_stdio() as context:
            hello(message=message, count=1)
        context.stdout.seek(0)
        actual = context.stdout.read().strip('\r\n')
        assert_equal(message, actual)
