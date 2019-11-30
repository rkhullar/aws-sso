from ...abstract import AbstractService
from ...utils import build_domain_username, get_package_root, register_action
from pathlib import Path

import configparser
import getpass
import keyring


class SiteWorker(AbstractService):

    @staticmethod
    def add_site(domain: str, username: str, password: str):
        service_name: str = get_package_root()
        domain_username: str = build_domain_username(domain, username)
        keyring.set_password(service_name=service_name, username=domain_username, password=password)

        config_dir = Path('~/.config').expanduser() / service_name
        config_dir.mkdir(parents=True, exist_ok=True)

        sites_path = config_dir / 'sites.ini'
        config = configparser.ConfigParser()
        if sites_path.exists():
            with sites_path.open('r') as f:
                config.read_file(f)
        if domain not in config.sections():
            config.add_section(domain)
        config[domain]['username'] = username
        with sites_path.open('w') as f:
            config.write(f)

    @register_action('add')
    def handle_add(self):
        password = self.params.password or getpass.getpass(prompt='password: ', stream=None)
        self.add_site(domain=self.params.domain, username=self.params.username, password=password)
