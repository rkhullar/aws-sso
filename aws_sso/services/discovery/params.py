from typing import NamedTuple, Optional


class DiscoveryParams(NamedTuple):
    domain: str
    skip_names: Optional[int] = None
