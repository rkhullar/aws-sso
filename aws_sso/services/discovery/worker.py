from ...abstract import AbstractService
from ...utils import register_action


class DiscoveryWorker(AbstractService):

    @register_action('default')
    def main(self):
        print('discovering')
        # discover(domain=self.params.domain, skip_names=bool(self.params.skip_names))
