from typing import List, Optional, Dict, NamedTuple
from requests_ntlm import HttpNtlmAuth
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from botocore.exceptions import ClientError

import getpass
import requests
import base64
import boto3
import re


def infer_domain(domain: str) -> Optional[str]:
    delimiter: chr = '.'
    parts: List[str] = domain.split(delimiter)
    if len(parts) > 1:
        return delimiter.join(parts[-2:])


def build_domain_username(domain: str, username: str) -> str:
    domain = infer_domain(domain)
    delimiter: chr = '\\'
    return delimiter.join([domain or '', username]).strip(delimiter)


def string_contains(text: str, keys: List[str]) -> bool:
    return any(key in text for key in keys)


class RoleTuple(NamedTuple):
    principle_arn: str
    role_arn: str

    @staticmethod
    def from_saml(saml: str) -> 'RoleTuple':
        principle, role = saml.split(',')
        if 'saml-provider' in role:
            principle, role = role, principle
        return RoleTuple(principle, role)


def test_entry():
    domain = input('domain: ')
    idp_entry_url = f'https://{domain}/adfs/ls/IdpInitiatedSignOn.aspx?loginToRp=urn:amazon:webservices'

    username = input('username: ')
    password = getpass.getpass()

    domain_username = build_domain_username(domain, username)

    verify_ssl = True
    session = requests.Session()
    session.auth = HttpNtlmAuth(domain_username, password)
    response = session.get(idp_entry_url, verify=verify_ssl)

    idp_submit_url: str = response.url
    payload: Dict[str, str] = dict()

    print(idp_entry_url)
    print(idp_submit_url)

    soup = BeautifulSoup(response.text, features="html5lib")
    for input_tag in soup.find_all(re.compile('input')):
        name, value = input_tag.get('name'), input_tag.get('value', '')
        if string_contains(text=name.lower(), keys=['user', 'email']):
            payload[name] = domain_username
        elif string_contains(text=name.lower(), keys=['pass']):
            payload[name] = password
        else:
            payload[name] = value

    print(payload)

    for tag in soup.find_all('form'):
        action, login_id = tag.get('action'), tag.get('id')
        if action and login_id == 'loginForm':
            parsed_url = urlparse(idp_entry_url)
            idp_submit_url = f'{parsed_url.scheme}://{parsed_url.netloc}{action}'

    print(idp_submit_url)

    response = session.post(idp_submit_url, data=payload, verify=verify_ssl)
    session.close()

    assertion: str = ''
    soup = BeautifulSoup(response.text, features="html5lib")
    for input_tag in soup.find_all(re.compile('input')):
        if input_tag.get('name') == 'SAMLResponse':
            assertion = input_tag.get('value')

    root = ET.fromstring(base64.b64decode(assertion))
    x = '{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'
    y = 'https://aws.amazon.com/SAML/Attributes/Role'
    z = '{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'
    role_tuples = [RoleTuple.from_saml(value.text) for attr in root.iter(x) if attr.get('Name') == y for value in attr.iter(z)]
    for role_tuple in role_tuples:
        # print(role_tuple)
        pass

    test_role_name, test_role_tuple = 'Sandbox-DevOps', None
    for role_tuple in role_tuples:
        if test_role_name in role_tuple.role_arn:
            test_role_tuple = role_tuple

    print(test_role_tuple)

    session = boto3.Session(region_name='us-east-1')
    client = session.client('sts')
    params = dict(RoleArn=test_role_tuple.role_arn, PrincipalArn=role_tuple.principle_arn,
                  SAMLAssertion=assertion, DurationSeconds=8*3600)
    try:
        token = client.assume_role_with_saml(**params)
    except ClientError as err:
        params['DurationSeconds'] = 3600
        token = client.assume_role_with_saml(**params)

    credentials = token['Credentials']

    assumed_session = boto3.Session(region_name='us-east-1', aws_access_key_id=credentials['AccessKeyId'],
                                    aws_secret_access_key=credentials['SecretAccessKey'], aws_session_token=credentials['SessionToken'])
    
    s3 = assumed_session.resource('s3')
    for bucket in s3.buckets.all():
        print(bucket)


if __name__ == '__main__':
    test_entry()
