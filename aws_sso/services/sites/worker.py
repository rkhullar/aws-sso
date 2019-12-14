from ...abstract import AbstractService
from ...utils import get_package_root, read_config, register_action, write_config
from .model import SiteLogin
from configparser import ConfigParser
from pathlib import Path
from typing import Iterator, List, Optional
import getpass
import keyring


class SiteWorker(AbstractService):

    @classmethod
    def infer_domain(cls, domain: str) -> Optional[str]:
        delimiter: chr = '.'
        parts: List[str] = domain.split(delimiter)
        if len(parts) > 1:
            return delimiter.join(parts[-2:])

    @classmethod
    def build_domain_username(cls, domain: str, username: str) -> str:
        delimiter: chr = '\\'
        domain: str = cls.infer_domain(domain)
        parts: List[str] = [domain or '', username]
        return delimiter.join(parts).strip(delimiter)

    def initialize(self):
        self.data['service_name']: str = get_package_root()
        self.data['config_dir']: Path = Path(self.params.config_dir).expanduser() / self.data['service_name']
        self.data['config_dir'].mkdir(parents=True, exist_ok=True)
        self.data['sites_path']: Path = self.data['config_dir'] / 'sites.ini'

    def add_site(self, domain: str, username: str, password: str):
        domain_username: str = self.build_domain_username(domain, username)
        keyring.set_password(service_name=self.data['service_name'], username=domain_username, password=password)
        sites_path: Path = self.data['sites_path']
        config: ConfigParser = read_config(path=sites_path)
        if domain not in config.sections():
            config.add_section(domain)
        config[domain]['username'] = username
        write_config(path=sites_path, config=config)

    @register_action('add')
    def handle_add(self):
        password = self.params.password or getpass.getpass(prompt='password: ', stream=None)
        self.add_site(domain=self.params.domain, username=self.params.username, password=password)

    def list_domains(self) -> Iterator:
        config: ConfigParser = read_config(path=self.data['sites_path'])
        yield from config.sections()

    @register_action('list')
    def handle_list(self):
        for domain in self.list_domains():
            print(domain)

    def remove_site(self, domain: str, raise_error: bool = False):
        sites_path: Path = self.data['sites_path']
        config: ConfigParser = read_config(path=sites_path, raise_error=raise_error)
        if domain in config.sections():
            username: str = config[domain]['username']
            domain_username: str = self.build_domain_username(domain, username)
            config.remove_section(domain)
            keyring.delete_password(service_name=self.data['service_name'], username=domain_username)
            write_config(path=sites_path, config=config)
        elif raise_error:
            raise ValueError(dict(message='site not available', domain=domain, path=str(sites_path)))

    @register_action('remove')
    def handle_remove(self):
        self.remove_site(domain=self.params.domain, raise_error=True)

    def get_site_login(self, domain: str) -> SiteLogin:
        sites_path: Path = self.data['sites_path']
        config: ConfigParser = read_config(path=sites_path)
        if domain in config.sections():
            username: str = config[domain]['username']
            domain_username: str = self.build_domain_username(domain, username)
            password: str = keyring.get_password(service_name=self.data['service_name'], username=domain_username)
            return SiteLogin(domain=domain, username=domain_username, password=password)
        else:
            raise ValueError(dict(message='site not available', domain=domain, path=str(sites_path)))
