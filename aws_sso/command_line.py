from argparse import ArgumentParser
from pathlib import Path
from .utils import *

import configparser
import keyring
import getpass


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

    profile_parser = subparsers.add_parser('profile')
    profile_parser.add_argument('--domain', '-d', type=str, required=True)
    profile_parser.add_argument('--skip-names', action='count')

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


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.action == 'hello':
        hello(message=args.message, count=args.count)

    elif args.action == 'add-site':
        args.password = args.password or getpass.getpass(prompt='password: ', stream=None)
        add_site(domain=args.domain, username=args.username, password=args.password)

