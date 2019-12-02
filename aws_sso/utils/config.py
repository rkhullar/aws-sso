from configparser import ConfigParser
from pathlib import Path
from typing import Optional


def read_config(path: Path, config: Optional[ConfigParser] = None, raise_error: bool = False) -> ConfigParser:
    config: ConfigParser = config or ConfigParser()
    if path.exists():
        with path.open('r') as f:
            config.read_file(f)
    elif raise_error:
        raise ValueError(dict(message='file does not exist', path=str(path)))
    return config


def write_config(path: Path, config: ConfigParser):
    with path.open('w') as f:
        config.write(f)
