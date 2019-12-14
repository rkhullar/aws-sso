from ....services import KeyringAction, SiteLogin, SiteParams, SiteWorker
from ....model import CommonParams
from ....utils import mock_input_output,combine_contexts
from nose.tools import assert_equal
from parameterized import parameterized
from typing import Optional
from unittest import TestCase
from unittest.mock import patch, MagicMock
import keyring
import uuid


class SitesTest(TestCase):

    @parameterized.expand([
        ('localhost', None),
        ('example.com', 'example.com'),
        ('sso.example.com', 'example.com')
    ])
    def test_infer_domain(self, value, expected):
        actual = SiteWorker.infer_domain(value)
        assert_equal(expected, actual)

    @parameterized.expand([
        ('localhost', 'test_user', 'test_user'),
        ('example.com', 'test_user', 'example.com\\test_user'),
        ('sso.example.com', 'test_user', 'example.com\\test_user')
    ])
    def test_build_domain_username(self, domain, username, expected):
        actual = SiteWorker.build_domain_username(domain, username)
        assert_equal(expected, actual)

    @classmethod
    def build_keyring_mock(cls, action: KeyringAction, domain: str, username: str, password: Optional[str] = None):
        if action in {KeyringAction.write, KeyringAction.delete}:
            return MagicMock()
        elif action in {KeyringAction.read}:
            return MagicMock(return_value=SiteLogin(domain=domain, username=username, password=password))

    @classmethod
    def build_keyring_patch(cls, domain: str, username: str, password: Optional[str] = None, action: Optional[KeyringAction] = None):
        if action:
            mock = cls.build_keyring_mock(action=action, domain=domain, username=username, password=password)
            return patch.object(target=keyring, attribute=action.method, new=mock)
        else:
            params = dict(domain=domain, username=username, password=password)
            return [cls.build_keyring_patch(action=KeyringAction[action], **params) for action in KeyringAction.actions()]

    def test_add_site(self):
        common_params = CommonParams(service='sites', action='add')
        service_params = SiteParams(domain='sso.example.com', username='msdocs', password=str(uuid.uuid4()))
        domain_username = SiteWorker.build_domain_username(domain=service_params.domain, username=service_params.username)
        keyring_patches = self.build_keyring_patch(domain=service_params.domain, username=domain_username, password=service_params.password)
        worker = SiteWorker(common_params, service_params)
        with combine_contexts(keyring_patches, mock_input_output()):
            worker()
