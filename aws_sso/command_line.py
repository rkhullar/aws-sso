from typing import Dict, Optional, NamedTuple, Iterator
from requests_ntlm import HttpNtlmAuth
from argparse import ArgumentParser
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from pathlib import Path
from .utils import *

import configparser
import requests
import keyring
import getpass
import base64
import re


def build_parser() -> ArgumentParser:
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='action')
    subparsers.required = True

    hello_parser = subparsers.add_parser('hello')
    hello_parser.add_argument('--message', '-m', type=str, default='hello world')
    hello_parser.add_argument('--count', '-c', type=int, default=1)

    add_site_parser = subparsers.add_parser('add-site')
    add_site_parser.add_argument('--domain', '-d', type=str, required=True)
    add_site_parser.add_argument('--username', '-u', type=str, required=True)
    add_site_parser.add_argument('--password', '-p', type=str, required=False)

    discover_parser = subparsers.add_parser('discover')
    discover_parser.add_argument('--domain', '-d', type=str, required=True)
    discover_parser.add_argument('--skip-names', action='count')

    return parser


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


def fetch_saml_token(domain: str, username: str, password: str, verify_ssl: bool = True) -> Optional[str]:
    idp_entry_url: str = f'https://{domain}/adfs/ls/IdpInitiatedSignOn.aspx?loginToRp=urn:amazon:webservices'
    domain_username: str = build_domain_username(domain, username)
    session = requests.Session()
    session.auth = HttpNtlmAuth(domain_username, password)
    response = session.get(idp_entry_url, verify=verify_ssl)
    idp_submit_url: str = response.url
    payload: Dict[str, str] = dict()
    soup = BeautifulSoup(response.text, features='html5lib')
    for input_tag in soup.find_all(re.compile('input')):
        name, value = input_tag.get('name'), input_tag.get('value', '')
        if string_contains(text=name.lower(), keys=['user', 'email']):
            payload[name] = domain_username
        elif string_contains(text=name.lower(), keys=['pass']):
            payload[name] = password
        else:
            payload[name] = value
    for tag in soup.find_all('form'):
        action, login_id = tag.get('action'), tag.get('id')
        if action and login_id == 'loginForm':
            parsed_url = urlparse(idp_entry_url)
            idp_submit_url = f'{parsed_url.scheme}://{parsed_url.netloc}{action}'
    response = session.post(idp_submit_url, data=payload, verify=verify_ssl)
    session.close()
    soup = BeautifulSoup(response.text, features='html5lib')
    for input_tag in soup.find_all(re.compile('input')):
        if input_tag.get('name') == 'SAMLResponse':
            return input_tag.get('value')


class RoleTuple(NamedTuple):
    principle_arn: str
    role_arn: str

    @staticmethod
    def from_saml(saml: str) -> 'RoleTuple':
        principle, role = saml.split(',')
        if 'saml-provider' in role:
            principle, role = role, principle
        return RoleTuple(principle, role)


def read_roles_from_saml(assertion: str) -> Iterator[RoleTuple]:
    root = ET.fromstring(base64.b64decode(assertion))
    xml_attr = '{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'
    url_role = 'https://aws.amazon.com/SAML/Attributes/Role'
    xml_attr_val = '{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'
    return (RoleTuple.from_saml(value.text) for attr in root.iter(xml_attr) if attr.get('Name') == url_role for value in attr.iter(xml_attr_val))


def discover(domain: str, skip_names: bool = False):
    service_name: str = get_package_root()
    config_dir = Path('~/.config').expanduser() / service_name
    sites_path = config_dir / 'sites.ini'
    config = configparser.ConfigParser()
    if sites_path.exists():
        with sites_path.open('r') as f:
            config.read_file(f)
    if domain not in config.sections():
        raise EnvironmentError(dict(message='site not added', domain=domain))
    username: str = config[domain]['username']
    domain_username: str = build_domain_username(domain, username)
    password: str = keyring.get_password(service_name=service_name, username=domain_username)
    assertion = fetch_saml_token(domain, username, password)
    if not assertion:
        raise ValueError(dict(message='invalid credentials', domain=domain, username=username))
    for role_tuple in read_roles_from_saml(assertion):
        print(role_tuple)


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.action == 'hello':
        hello(message=args.message, count=args.count)

    elif args.action == 'add-site':
        args.password = args.password or getpass.getpass(prompt='password: ', stream=None)
        add_site(domain=args.domain, username=args.username, password=args.password)

    elif args.action == 'discover':
        discover(domain=args.domain, skip_names=bool(args.skip_names))
