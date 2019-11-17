from contextlib import contextmanager
from typing import NamedTuple
from io import StringIO

import sys


class MockedContext(NamedTuple):
    stdin: StringIO
    stdout: StringIO
    stderr: StringIO


@contextmanager
def mocked_stdio():
    real = sys.stdin, sys.stdout, sys.stderr
    fake = StringIO(), StringIO(), StringIO()
    sys.stdin, sys.stdout, sys.stderr = fake
    yield MockedContext(*fake)
    sys.stdin, sys.stdout, sys.stderr = real
