def discover(domain: str, skip_names: bool = False):
    service_name: str = get_package_root()
    config_dir = Path('~/.config').expanduser() / service_name
    sites_path = config_dir / 'sites.ini'
    config = configparser.ConfigParser()
    if sites_path.exists():
        with sites_path.open('r') as f:
            config.read_file(f)
    if domain not in config.sections():
        raise EnvironmentError(dict(message='site not added', domain=domain))
    username: str = config[domain]['username']
    domain_username: str = build_domain_username(domain, username)
    password: str = keyring.get_password(service_name=service_name, username=domain_username)
    assertion = fetch_saml_token(domain, username, password)
    if not assertion:
        raise ValueError(dict(message='invalid credentials', domain=domain, username=username))
    for role_tuple in read_roles_from_saml(assertion):
        print(role_tuple)


def read_roles_from_saml(assertion: str) -> Iterator[RoleTuple]:
    root = ET.fromstring(base64.b64decode(assertion))
    xml_attr = '{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'
    url_role = 'https://aws.amazon.com/SAML/Attributes/Role'
    xml_attr_val = '{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'
    return (RoleTuple.from_saml(value.text) for attr in root.iter(xml_attr) if attr.get('Name') == url_role for value in attr.iter(xml_attr_val))


def fetch_saml_token(domain: str, username: str, password: str, verify_ssl: bool = True) -> Optional[str]:
    idp_entry_url: str = f'https://{domain}/adfs/ls/IdpInitiatedSignOn.aspx?loginToRp=urn:amazon:webservices'
    domain_username: str = build_domain_username(domain, username)
    session = requests.Session()
    session.auth = HttpNtlmAuth(domain_username, password)
    response = session.get(idp_entry_url, verify=verify_ssl)
    idp_submit_url: str = response.url
    payload: Dict[str, str] = dict()
    soup = BeautifulSoup(response.text, features='html5lib')
    for input_tag in soup.find_all(re.compile('input')):
        name, value = input_tag.get('name'), input_tag.get('value', '')
        if string_contains(text=name.lower(), keys=['user', 'email']):
            payload[name] = domain_username
        elif string_contains(text=name.lower(), keys=['pass']):
            payload[name] = password
        else:
            payload[name] = value
    for tag in soup.find_all('form'):
        action, login_id = tag.get('action'), tag.get('id')
        if action and login_id == 'loginForm':
            parsed_url = urlparse(idp_entry_url)
            idp_submit_url = f'{parsed_url.scheme}://{parsed_url.netloc}{action}'
    response = session.post(idp_submit_url, data=payload, verify=verify_ssl)
    session.close()
    soup = BeautifulSoup(response.text, features='html5lib')
    for input_tag in soup.find_all(re.compile('input')):
        if input_tag.get('name') == 'SAMLResponse':
            return input_tag.get('value')
