from typing import NamedTuple, Optional


class SiteParams(NamedTuple):
    domain: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
