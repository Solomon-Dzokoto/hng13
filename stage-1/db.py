from typing import Dict, List, Optional, Any
import models


_STORE: Dict[str, Dict] = {}


def exists(value: str) -> bool:
    sha = models.compute_sha256(value)
    return sha in _STORE


def create_entry(value: str, properties: Dict) -> Dict:
    entry = models.make_entry(value, properties)
    _STORE[entry["id"]] = entry
    return entry


def get_by_value(value: str) -> Optional[Dict]:
    sha = models.compute_sha256(value)
    return _STORE.get(sha)


def delete_by_value(value: str) -> bool:
    sha = models.compute_sha256(value)
    if sha in _STORE:
        del _STORE[sha]
        return True
    return False


def _entry_matches(entry: Dict, is_palindrome: Optional[bool], min_length: Optional[int], max_length: Optional[int], word_count: Optional[int], contains_character: Optional[str]) -> bool:
    p = entry["properties"]
    if is_palindrome is not None and p.get("is_palindrome") != is_palindrome:
        return False
    if min_length is not None and p.get("length") < min_length:
        return False
    if max_length is not None and p.get("length") > max_length:
        return False
    if word_count is not None and p.get("word_count") != word_count:
        return False
    if contains_character is not None:
        if len(contains_character) != 1:
            raise ValueError("contains_character must be a single character")
        if contains_character not in entry["value"]:
            return False
    return True


def filter_entries(is_palindrome: Optional[bool] = None, min_length: Optional[int] = None, max_length: Optional[int] = None, word_count: Optional[int] = None, contains_character: Optional[str] = None) -> List[Dict]:
    results = []
    for entry in _STORE.values():
        if _entry_matches(entry, is_palindrome, min_length, max_length, word_count, contains_character):
            results.append(entry)
    return results
