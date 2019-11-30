from ...abstract import AbstractService
from ...utils import register_action
from io import StringIO
import sys


class HelloWorker(AbstractService):

    @staticmethod
    def hello(message: str = 'hello world', count: int = 1, file: StringIO = None):
        for _ in range(count):
            print(message, file=file or sys.stdout)

    @register_action('default')
    def main(self):
        self.hello(message=self.params.message, count=self.params.count)
