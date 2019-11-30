from typing import NamedTuple, Optional


class SiteParams(NamedTuple):
    domain: str
    username: str
    password: Optional[str]
