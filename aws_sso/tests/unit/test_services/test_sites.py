from ....services import SiteParams, SiteWorker
from ....model import CommonParams
from ....utils import mock_input_output
from unittest import TestCase
import uuid


class SitesTest(TestCase):

    def test_sites_add(self):
        common_params = CommonParams(service='sites', action='add')
        service_params = SiteParams(domain='sso.example.com', username='msdocs', password=str(uuid.uuid4()))
        worker = SiteWorker(common_params, service_params)
        with mock_input_output():
            worker()
