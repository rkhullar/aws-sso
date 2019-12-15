from ...abstract import AbstractService
from ...model import CommonParams
from ...utils import get_package_root, register_action
from ..sites import *
from .core import make_saml, iter_roles, assume_role

from pathlib import Path
import datetime as dt


class LoginWorker(AbstractService):

    def initialize(self):
        self.tools['sites'] = self.build_site_worker()
        self.data['service_name']: str = get_package_root()
        self.data['config_dir']: Path = Path(self.params.config_dir).expanduser() / self.data['service_name']
        self.data['config_dir'].mkdir(parents=True, exist_ok=True)
        self.data['aws_dir']: Path = Path(self.params.aws_dir).expanduser()

    def build_site_worker(self) -> SiteWorker:
        return SiteWorker(common_params=CommonParams(config_dir=self.params.config_dir), service_params=SiteParams())

    @register_action('default')
    def main(self):
        site_login: SiteLogin = self.tools['sites'].get_site_login(self.params.domain)
        assertion: str = make_saml(domain=site_login.domain, username=site_login.username, password=site_login.password)
        if not assertion:
            raise ValueError(dict(message='could not make saml assertion', domain=site_login.domain, username=site_login.username))

        test_role_name, test_role_tuple = 'Sandbox-DevOps', None

        for role_tuple in iter_roles(assertion):
            if test_role_name in role_tuple.role_arn:
                test_role_tuple = role_tuple

        print(test_role_tuple)

        credentials = assume_role(role_tuple=test_role_tuple, assertion=assertion, region=self.params.region)
        time_delta = credentials.expiration - dt.datetime.now(tz=credentials.expiration.tzinfo)
        seconds = int(time_delta.total_seconds())
        print(seconds)
