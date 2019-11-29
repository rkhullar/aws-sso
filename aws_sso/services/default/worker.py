from ...abstract import AbstractService
from ...utils import register_handler


class DefaultWorker(AbstractService):

    @register_handler('default')
    def main(self):
        print('stub method for default service and action')
