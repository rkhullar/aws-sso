from ....utils import *
from nose.tools import assert_equal
from parameterized import parameterized
from unittest import TestCase


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
