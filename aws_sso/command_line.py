from argparse import ArgumentParser, Namespace
from .utils import extend_parsers, namespace_to_tuple
from .abstract import AbstractService, ServiceDef
from .model import CommonParams
from typing import NamedTuple
from .services import *


def build_parser() -> ArgumentParser:
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='service')
    subparsers.required = True

    service_parsers = extend_parsers(subparsers, service=True, names=['site'])
    action_parsers = extend_parsers(subparsers, service=False, names=['print', 'discover'])

    hello_parser = action_parsers['print']
    hello_parser.add_argument('-m', '--message', type=str, default='hello world')
    hello_parser.add_argument('-c', '--count', type=int, default=1)

    add_site_parser = service_parsers['site'].add_parser('add')
    add_site_parser.add_argument('--domain', '-d', type=str, required=True)
    add_site_parser.add_argument('--username', '-u', type=str, required=True)
    add_site_parser.add_argument('--password', '-p', type=str, required=False)

    discover_parser = action_parsers['discover']
    discover_parser.add_argument('--domain', '-d', type=str, required=True)
    discover_parser.add_argument('--skip-names', action='count')

    return parser


services = {
    'print': ServiceDef(HelloParams, HelloWorker),
    'sites': ServiceDef(SiteParams, SiteWorker),
    'default': ServiceDef(DefaultParams, DefaultWorker)
}


def main():
    parser: ArgumentParser = build_parser()
    args: Namespace = parser.parse_args()
    common_params: CommonParams = namespace_to_tuple(args, CommonParams)
    service_name: str = common_params.service
    service_def: ServiceDef = services[service_name]
    service_params: NamedTuple = namespace_to_tuple(args, service_def.param_type)
    service: AbstractService = service_def.service_type(common_params, service_params)
    service()

    '''
    if args.action == 'hello':
        hello(message=args.message, count=args.count)

    elif args.action == 'add-site':
        args.password = args.password or getpass.getpass(prompt='password: ', stream=None)
        add_site(domain=args.domain, username=args.username, password=args.password)

    elif args.action == 'discover':
        discover(domain=args.domain, skip_names=bool(args.skip_names))
    '''
