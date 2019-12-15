from ...abstract import AbstractService
from ...model import CommonParams
from ..sites import *
from ...utils import register_action
from .core import part_1, part_2


class DiscoveryWorker(AbstractService):

    def build_site_worker(self) -> SiteWorker:
        return SiteWorker(common_params=CommonParams(config_dir=self.params.config_dir), service_params=SiteParams())

    def initialize(self):
        self.tools['sites'] = self.build_site_worker()

    def discover(self, domain: str, skip_names: bool = True):
        site_login: SiteLogin = self.tools['sites'].get_site_login(domain)
        idp_submit_url, payload = part_1(domain=site_login.domain, username=site_login.username, password=site_login.password)
        role_tuples = part_2(idp_submit_url, payload)
        for role_tuple in role_tuples:
            print(role_tuple)

    @register_action('default')
    def main(self):
        self.discover(domain=self.params.domain, skip_names=bool(self.params.skip_names))
