from ...abstract import AbstractService
from ...utils import register_action


class LoginWorker(AbstractService):

    @register_action('default')
    def main(self):
        print(self.params)
