from ...abstract import AbstractService
from ...registry import register_handler


class DefaultWorker(AbstractService):

    @register_handler('default')
    def main(self):
        print('default service default action')
        print(self.params)
