from ...abstract import AbstractService
from ...utils import build_domain_username, get_package_root, register_action
from .model import SiteLogin
from configparser import ConfigParser
from pathlib import Path
from typing import Iterator, Optional
import getpass
import keyring


class SiteWorker(AbstractService):

    def initialize(self):
        self.data['service_name']: str = get_package_root()
        self.data['config_dir']: Path = Path('~/.config').expanduser() / self.data['service_name']
        self.data['config_dir'].mkdir(parents=True, exist_ok=True)
        self.data['sites_path']: Path = self.data['config_dir'] / 'sites.ini'

    @staticmethod
    def read_config(path: Path, config: Optional[ConfigParser] = None, raise_error: bool = False) -> ConfigParser:
        config: ConfigParser = config or ConfigParser()
        if path.exists():
            with path.open('r') as f:
                config.read_file(f)
        elif raise_error:
            raise ValueError(dict(message='file does not exist', path=str(path)))
        return config

    @staticmethod
    def write_config(path: Path, config: ConfigParser):
        with path.open('w') as f:
            config.write(f)

    def add_site(self, domain: str, username: str, password: str):
        domain_username: str = build_domain_username(domain, username)
        keyring.set_password(service_name=self.data['service_name'], username=domain_username, password=password)
        sites_path: Path = self.data['sites_path']
        config: ConfigParser = self.read_config(path=sites_path)
        if domain not in config.sections():
            config.add_section(domain)
        config[domain]['username'] = username
        self.write_config(path=sites_path, config=config)

    @register_action('add')
    def handle_add(self):
        password = self.params.password or getpass.getpass(prompt='password: ', stream=None)
        self.add_site(domain=self.params.domain, username=self.params.username, password=password)

    def list_domains(self) -> Iterator:
        config: ConfigParser = self.read_config(path=self.data['sites_path'])
        yield from config.sections()

    @register_action('list')
    def handle_list(self):
        for domain in self.list_domains():
            print(domain)

    def remove_site(self, domain: str, raise_error: bool = False):
        sites_path: Path = self.data['sites_path']
        config: ConfigParser = self.read_config(path=sites_path, raise_error=raise_error)
        if domain in config.sections():
            username: str = config[domain]['username']
            domain_username: str = build_domain_username(domain, username)
            config.remove_section(domain)
            keyring.delete_password(service_name=self.data['service_name'], username=domain_username)
            self.write_config(path=sites_path, config=config)
        elif raise_error:
            raise ValueError(dict(message='site not available', domain=domain, path=str(sites_path)))

    @register_action('remove')
    def handle_remove(self):
        self.remove_site(domain=self.params.domain, raise_error=True)

    def get_site_login(self, domain: str) -> SiteLogin:
        sites_path: Path = self.data['sites_path']
        config: ConfigParser = self.read_config(path=sites_path)
        if domain in config.sections():
            username: str = config[domain]['username']
            domain_username: str = build_domain_username(domain, username)
            password: str = keyring.get_password(service_name=self.data['service_name'], username=domain_username)
            return SiteLogin(domain=domain, username=domain_username, password=password)
        else:
            raise ValueError(dict(message='site not available', domain=domain, path=str(sites_path)))
