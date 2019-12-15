from typing import NamedTuple, Optional


class LoginParams(NamedTuple):
    domain: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    interactive: Optional[int] = None
    profile: Optional[str] = None
