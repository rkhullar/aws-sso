from .abstract import AbstractService, ServiceDef
from .model import CommonParams
from .services import *
from .utils import extend_parsers, namespace_to_tuple

from argparse import ArgumentParser, Namespace
from typing import NamedTuple


def build_parser(service_required: bool = True) -> ArgumentParser:
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest='service')
    subparsers.required = service_required

    service_parsers = extend_parsers(subparsers, service=True, names=['site'])
    action_parsers = extend_parsers(subparsers, service=False, names=['print', 'discover', 'login'])

    parser.add_argument('--aws-dir', type=str, default='~/.aws')
    parser.add_argument('--config-dir', type=str, default='~/.config')

    hello_parser = action_parsers['print']
    hello_parser.add_argument('-m', '--message', type=str, default='hello world')
    hello_parser.add_argument('-c', '--count', type=int, default=1)

    add_site_parser = service_parsers['site'].add_parser('add')
    add_site_parser.add_argument('-d', '--domain', type=str, required=True)
    add_site_parser.add_argument('-u', '--username', type=str, required=True)
    add_site_parser.add_argument('-p', '--password', type=str, required=False)

    remove_site_parser = service_parsers['site'].add_parser('remove')
    remove_site_parser.add_argument('-d', '--domain', type=str, required=True)

    service_parsers['site'].add_parser('list')

    login_parser = action_parsers['login']
    login_parser.add_argument('-d', '--domain', type=str, required=True)
    login_parser.add_argument('-u', '--username', type=str, required=False)
    login_parser.add_argument('-p', '--password', type=str, required=False)
    login_parser.add_argument('-i', '--interactive', action='count')
    login_parser.add_argument('--region', type=str, default='us-east-1')
    login_parser.add_argument('--profile', type=str, default='default')

    discover_parser = action_parsers['discover']
    discover_parser.add_argument('-d', '--domain', type=str, required=True)
    discover_parser.add_argument('--skip-names', action='count')

    return parser


services = {
    'default': ServiceDef(DefaultParams, DefaultWorker),
    'discover': ServiceDef(DiscoveryParams, DiscoveryWorker),
    'login': ServiceDef(LoginParams, LoginWorker),
    'print': ServiceDef(HelloParams, HelloWorker),
    'site': ServiceDef(SiteParams, SiteWorker),
}


def main():
    parser: ArgumentParser = build_parser(service_required=True)
    args: Namespace = parser.parse_args()
    common_params: CommonParams = namespace_to_tuple(args, CommonParams)
    service_name: str = common_params.service or 'default'
    service_def: ServiceDef = services[service_name]
    service_params: NamedTuple = namespace_to_tuple(args, service_def.param_type)
    service: AbstractService = service_def.service_type(common_params, service_params)
    service()
