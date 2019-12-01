from ....services import KeyringAction, SiteLogin, SiteParams, SiteWorker
from ....model import CommonParams
from ....utils import build_domain_username, mock_input_output
from nose.tools import assert_equal
from typing import Optional
from unittest import TestCase
from unittest.mock import patch, MagicMock
import keyring
import uuid


class SitesTest(TestCase):

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
        domain_username = build_domain_username(domain=service_params.domain, username=service_params.username)
        keyring_patches = self.build_keyring_patch(domain=service_params.domain, username=domain_username, password=service_params.password)
        worker = SiteWorker(common_params, service_params)
        with keyring_patches[0], keyring_patches[1], keyring_patches[2], mock_input_output():
            worker()
