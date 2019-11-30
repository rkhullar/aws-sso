from ...abstract import AbstractService
from ...utils import register_action


class DefaultWorker(AbstractService):

    @register_action('default')
    def main(self):
        print('stub method for default service and action')
