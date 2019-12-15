from ..discovery.model import RoleTuple
from typing import Dict, NamedTuple
import datetime as dt


class Credentials(NamedTuple):
    access_key_id: str
    secret_access_key: str
    session_token: str
    expiration: dt.datetime

    @classmethod
    def from_token(cls, token: Dict):
        data = token['Credentials']
        return cls(data['AccessKeyId'], data['SecretAccessKey'], data['SessionToken'], data['Expiration'])


class Profile(NamedTuple):
    name: str
    role_tuple: RoleTuple

