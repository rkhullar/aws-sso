from typing import List


def string_contains(text: str, keys: List[str]) -> bool:
    return any(key in text for key in keys)
