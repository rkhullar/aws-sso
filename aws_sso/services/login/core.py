from ..discovery.core import part_1 as build_request
from ..discovery.core import find_assertion, parse_assertion, iter_saml_data
from ..discovery.model import RoleTuple
from .model import Credentials

from botocore.exceptions import ClientError
from typing import Iterator, Optional

import requests
import boto3


def make_saml(domain: str, username: str, password: str, verify_ssl: bool = True) -> Optional[str]:
    idp_submit_url, payload = build_request(domain, username, password, verify_ssl)
    response = requests.post(url=idp_submit_url, data=payload, verify=verify_ssl)
    return find_assertion(response)


def iter_roles(assertion: str) -> Iterator[RoleTuple]:
    root = parse_assertion(assertion)
    return (RoleTuple.from_saml(data) for data in iter_saml_data(root))


def assume_role(role_tuple: RoleTuple, assertion: str, region: str = 'us-east-1') -> Credentials:
    session = boto3.Session(region_name=region)
    client = session.client('sts')
    params = dict(RoleArn=role_tuple.role_arn, PrincipalArn=role_tuple.principle_arn,
                  SAMLAssertion=assertion, DurationSeconds=8 * 3600)
    try:
        token = client.assume_role_with_saml(**params)
    except ClientError as err:
        params['DurationSeconds'] = 3600
        token = client.assume_role_with_saml(**params)
    return Credentials.from_token(token)
