from ...abstract import AbstractService
from ...model import CommonParams
from ..sites import *
from ...utils import get_package_root, read_config, register_action, write_config
from .core import part_1, part_2
from configparser import ConfigParser
import logging
from pathlib import Path
from typing import List, Union


class DiscoveryWorker(AbstractService):

    def build_site_worker(self) -> SiteWorker:
        return SiteWorker(common_params=CommonParams(config_dir=self.params.config_dir), service_params=SiteParams())

    def initialize(self):
        self.tools['sites'] = self.build_site_worker()
        self.data['service_name']: str = get_package_root()
        self.data['config_dir']: Path = Path(self.params.config_dir).expanduser() / self.data['service_name']
        self.data['config_dir'].mkdir(parents=True, exist_ok=True)

    def build_profile_path(self, domain: str, base_name: str = 'profiles.ini') -> Path:
        path: Path = self.data['config_dir'] / domain / base_name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch(exist_ok=True)
        return path

    def discover(self, domain: str, skip_names: bool = True):
        site_login: SiteLogin = self.tools['sites'].get_site_login(domain)
        profile_path: Path = self.build_profile_path(domain=site_login.domain)
        config: ConfigParser = read_config(path=profile_path)

        idp_submit_url, payload = part_1(domain=site_login.domain, username=site_login.username, password=site_login.password)
        role_tuples = part_2(idp_submit_url, payload)

        for idx, role_tuple in enumerate(role_tuples):
            default_profile_name = self.build_default_profile_name(domain=site_login.domain, suffix=idx)
            if skip_names:
                profile_name = default_profile_name
            else:
                print(f'[default = {default_profile_name}] [role = {role_tuple.role_name}]')
                prompted = input('enter profile name: ')
                profile_name = prompted.strip() or default_profile_name
                # TODO: add ability to skip role

            logging.info('setting profile', extra=dict(name=profile_name, role=role_tuple.role_name, site=site_login.domain))
            if profile_name not in config.sections():
                config.add_section(profile_name)
            config[profile_name]['principle_arn'] = role_tuple.principle_arn
            config[profile_name]['role_arn'] = role_tuple.role_arn
            write_config(path=profile_path, config=config)
        print(f'edit profiles at {str(profile_path)}')

    @staticmethod
    def build_default_profile_name(domain: str, suffix: Union[int, str]) -> str:
        delimiter: chr = '.'
        parts: List[str] = domain.split(delimiter)
        basename = parts[-2:][0]
        if isinstance(suffix, int):
            return f'{basename}-{suffix:02}'
        else:
            return f'{basename}-{suffix}'

    @register_action('default')
    def main(self):
        self.discover(domain=self.params.domain, skip_names=bool(self.params.skip_names))
