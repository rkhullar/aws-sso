from pathlib import Path
from typing import List, Optional


def get_package_root() -> str:
    return __package__.split('.')[0]


def infer_domain(domain: str) -> Optional[str]:
    delimiter: chr = '.'
    parts: List[str] = domain.split(delimiter)
    if len(parts) > 1:
        return delimiter.join(parts[-2:])


def build_domain_username(domain: str, username: str) -> str:
    delimiter: chr = '\\'
    domain: str = infer_domain(domain)
    parts: List[str] = [domain or '', username]
    return delimiter.join(parts).strip(delimiter)


def string_contains(text: str, keys: List[str]) -> bool:
    return any(key in text for key in keys)


def read_hello_txt() -> str:
    here: Path = Path(__file__).parents[1]
    target = here / 'data' / 'hello.txt'
    with target.open('r') as f:
        return f.read().strip()


__all__ = ['get_package_root', 'infer_domain', 'build_domain_username', 'string_contains', 'read_hello_txt']
