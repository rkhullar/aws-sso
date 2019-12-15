from typing import NamedTuple


class RoleTuple(NamedTuple):
    principle_arn: str
    role_arn: str

    @staticmethod
    def from_saml(saml: str) -> 'RoleTuple':
        principle, role = saml.split(',')
        if 'saml-provider' in role:
            principle, role = role, principle
        return RoleTuple(principle, role)

    @property
    def role_name(self) -> str:
        return self.role_arn.split('/')[-1]
