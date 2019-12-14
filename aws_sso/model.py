from typing import NamedTuple


class CommonParams(NamedTuple):
    service: str
    action: str
    aws_dir: str = '~/.aws'
    config_dir: str = '~/.config'


class RoleTuple(NamedTuple):
    principle_arn: str
    role_arn: str

    @staticmethod
    def from_saml(saml: str) -> 'RoleTuple':
        principle, role = saml.split(',')
        if 'saml-provider' in role:
            principle, role = role, principle
        return RoleTuple(principle, role)
