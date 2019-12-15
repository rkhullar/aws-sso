from ...utils import string_contains
from .model import RoleTuple

from bs4 import BeautifulSoup
from requests_ntlm import HttpNtlmAuth
from typing import Callable, Dict, Iterator, Optional
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

import base64
import logging
import requests
import re


def part_1(domain: str, username: str, password: str, verify_ssl: bool = True):
    # TODO: use better function name
    session = requests.Session()
    session.auth = HttpNtlmAuth(username, password)
    idp_entry_url = build_idp_entry_url(domain)
    response = session.get(idp_entry_url, verify=verify_ssl)
    idp_submit_url = response.url
    logging.info('set idp url', extra=dict(entry=idp_entry_url, submit=idp_submit_url))
    payload = build_payload(response, username, password)
    logging.debug('payload', extra=payload)
    new_idp_submit_url = find_new_idp_submit_url(response, idp_entry_url)
    if new_idp_submit_url:
        old_idp_submit_url = idp_submit_url
        idp_submit_url = new_idp_submit_url
        logging.info('set idp url', extra=dict(urls=[idp_entry_url, old_idp_submit_url, idp_submit_url]))
    session.close()
    return idp_submit_url, payload


def build_payload(response, username: str, password: str) -> Dict:
    soup = BeautifulSoup(response.text, features='html5lib')
    process_tag = build_payload_tag_engine(username, password)
    return {tag.get('name'): process_tag(tag) for tag in soup.find_all(re.compile('input'))}


def build_payload_tag_engine(username: str, password: str) -> Callable:
    def engine(tag) -> str:
        name, value = tag.get('name'), tag.get('value', '')
        if string_contains(text=name.lower(), keys=['user', 'email']):
            value = username
        elif string_contains(text=name.lower(), keys=['pass']):
            value = password
        return value
    return engine


def build_idp_entry_url(domain: str) -> str:
    return f'https://{domain}/adfs/ls/IdpInitiatedSignOn.aspx?loginToRp=urn:amazon:webservices'


def find_new_idp_submit_url(response, idp_entry_url: str) -> Optional[str]:
    soup = BeautifulSoup(response.text, features='html5lib')
    for tag in soup.find_all('form'):
        action, login_id = tag.get('action'), tag.get('id')
        if action and login_id == 'loginForm':
            parsed_url = urlparse(idp_entry_url)
            return f'{parsed_url.scheme}://{parsed_url.netloc}{action}'


def part_2(idp_submit_url: str, payload: Dict[str, str], verify_ssl: bool = True) -> Iterator[RoleTuple]:
    # TODO: use better function name
    response = requests.post(url=idp_submit_url, data=payload, verify=verify_ssl)
    assertion = find_assertion(response)
    root = parse_assertion(assertion)
    return (RoleTuple.from_saml(data) for data in iter_saml_data(root))


def find_assertion(response) -> Optional[str]:
    soup = BeautifulSoup(response.text, features="html5lib")
    for input_tag in soup.find_all(re.compile('input')):
        if input_tag.get('name') == 'SAMLResponse':
            return input_tag.get('value')


def parse_assertion(assertion: str) -> ET.Element:
    byte_string = base64.b64decode(assertion)
    root = ET.fromstring(byte_string)
    return root


def iter_saml_data(root: ET.Element) -> Iterator[str]:
    attr_tag = '{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'
    role_tag = 'https://aws.amazon.com/SAML/Attributes/Role'
    value_tag = '{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'
    return (value.text for attr in root.iter(attr_tag) if attr.get('Name') == role_tag for value in attr.iter(value_tag))
