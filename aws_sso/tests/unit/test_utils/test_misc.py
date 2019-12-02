from ....utils import *
from nose.tools import assert_equal
from unittest import TestCase


class UtilsTest(TestCase):

    def test_package_root(self):
        assert_equal(get_package_root(), 'aws_sso')
