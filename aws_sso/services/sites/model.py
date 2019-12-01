from typing import NamedTuple


class SiteLogin(NamedTuple):
    domain: str
    username: str
    password: str
