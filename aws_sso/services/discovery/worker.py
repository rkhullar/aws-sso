from ...abstract import AbstractService
from ...model import CommonParams
from ..sites import *
from ...utils import register_action


class DiscoveryWorker(AbstractService):

    def build_site_worker(self) -> SiteWorker:
        return SiteWorker(common_params=CommonParams(config_dir=self.params.config_dir), service_params=SiteParams())

    def initialize(self):
        self.tools['sites'] = self.build_site_worker()

    def discover(self, domain: str, skip_names: bool = True):
        print(self.tools['sites'].get_site_login(domain))

    @register_action('default')
    def main(self):
        self.discover(domain=self.params.domain, skip_names=bool(self.params.skip_names))
