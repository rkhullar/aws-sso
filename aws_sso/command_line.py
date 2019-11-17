from argparse import ArgumentParser
from .utils import *
import keyring
import getpass


def build_parser() -> ArgumentParser:
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='action')
    subparsers.required = False

    hello_parser = subparsers.add_parser('hello')
    hello_parser.add_argument('--message', '-m', type=str, default='hello world')
    hello_parser.add_argument('--count', '-c', type=int, default=1)

    add_site_parser = subparsers.add_parser('add-site')
    add_site_parser.add_argument('--domain', '-d', type=str, required=True)
    add_site_parser.add_argument('--username', '-u', type=str, required=True)
    add_site_parser.add_argument('--password', '-p', type=str, required=False)

    return parser


def add_site(domain: str, username: str, password: str):
    domain_username: str = build_domain_username(domain, username)
    keyring.set_password(service_name=get_package_root(), username=domain_username, password=password)
    temp = keyring.get_password(service_name=get_package_root(), username=domain_username)
    print(domain_username)


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.action == 'hello':
        hello(message=args.message, count=args.count)

    elif args.action == 'add-site':
        args.password = args.password or getpass.getpass(prompt='password: ', stream=None)
        add_site(domain=args.domain, username=args.username, password=args.password)

