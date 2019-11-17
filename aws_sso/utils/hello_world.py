from io import StringIO
import sys


def hello(message: str = 'hello world', count: int = 1, file: StringIO = None):
    for _ in range(count):
        print(message, file=file or sys.stdout)
