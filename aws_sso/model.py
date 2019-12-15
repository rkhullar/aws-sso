from typing import NamedTuple


class CommonParams(NamedTuple):
    service: str = None
    action: str = None
    aws_dir: str = '~/.aws'
    config_dir: str = '~/.config'
