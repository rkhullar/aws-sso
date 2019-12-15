from ...abstract import AbstractService
from ...model import CommonParams
from ...utils import get_package_root, read_config, register_action, write_config
from ..sites import *
from .core import make_saml, iter_roles, assume_role
from .model import RoleTuple, Profile

from pathlib import Path
from typing import Iterator
import datetime as dt


class LoginWorker(AbstractService):

    def initialize(self):
        self.tools['sites'] = self.build_site_worker()
        self.data['service_name']: str = get_package_root()
        self.data['config_dir']: Path = Path(self.params.config_dir).expanduser() / self.data['service_name']
        self.data['config_dir'].mkdir(parents=True, exist_ok=True)
        self.data['aws_dir']: Path = Path(self.params.aws_dir).expanduser()
        self.data['aws_dir'].mkdir(parents=True, exist_ok=True)
        self.data['credentials'] = self.data['aws_dir'] / 'credentials'
        self.data['credentials'].touch(exist_ok=True)

    def build_site_worker(self) -> SiteWorker:
        return SiteWorker(common_params=CommonParams(config_dir=self.params.config_dir), service_params=SiteParams())

    def read_profiles(self, domain: str, base_name: str = 'profiles.ini') -> Iterator[Profile]:
        profile_path: Path = self.data['config_dir'] / domain / base_name
        config = read_config(path=profile_path)
        for section in config.sections():
            role_tuple = RoleTuple(role_arn=config[section]['role_arn'], principle_arn=config[section]['principle_arn'])
            profile = Profile(name=section, role_tuple=role_tuple)
            yield profile

    @register_action('default')
    def main(self):
        site_login: SiteLogin = self.tools['sites'].get_site_login(self.params.domain)
        assertion: str = make_saml(domain=site_login.domain, username=site_login.username, password=site_login.password)
        if not assertion:
            raise ValueError(dict(message='could not make saml assertion', domain=site_login.domain, username=site_login.username))

        config = read_config(path=self.data['credentials'])
        for profile in self.read_profiles(domain=site_login.domain):
            credentials = assume_role(role_tuple=profile.role_tuple, assertion=assertion, region=self.params.region)
            time_delta = credentials.expiration - dt.datetime.now(tz=credentials.expiration.tzinfo)
            seconds = int(time_delta.total_seconds())
            print(f'profile {profile.name} expires in {seconds} seconds')
            if profile.name not in config.sections():
                config.add_section(profile.name)
            item = config[profile.name]
            item['aws_access_key_id'] = credentials.access_key_id
            item['aws_secret_access_key'] = credentials.secret_access_key
            item['aws_session_token'] = credentials.session_token
            write_config(path=self.data['credentials'], config=config)

        '''
        test_role_name, test_role_tuple = 'sandbox', None
        for role_tuple in iter_roles(assertion):
            if test_role_name in role_tuple.role_arn.lower():
                test_role_tuple = role_tuple
        '''

        # TODO: cleanup, add interactive mode, and allow overriding username and password
