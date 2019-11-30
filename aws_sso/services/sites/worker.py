from ...abstract import AbstractService
from ...utils import register_action
import getpass


class SiteWorker(AbstractService):

    @register_action('add')
    def handle_add(self):
        password = self.params.password or getpass.getpass(prompt='password: ', stream=None)
        # add_site(domain=self.params.domain, username=self.params.username, password=password)
