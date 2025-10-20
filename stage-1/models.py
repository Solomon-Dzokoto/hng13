from typing import Dict
from hashlib import sha256
from collections import Counter
from datetime import datetime, timezone


def compute_sha256(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def analyze_string(value: str) -> Dict:
    length = len(value)
    lowered = value.lower()
    is_palindrome = lowered == lowered[::-1]
    unique_characters = len(set(value))
    word_count = 0
    if value.strip():
        word_count = len(value.split())
    sha = compute_sha256(value)
    freq_map = dict(Counter(value))

    return {
        "length": length,
        "is_palindrome": is_palindrome,
        "unique_characters": unique_characters,
        "word_count": word_count,
        "sha256_hash": sha,
        "character_frequency_map": freq_map,
    }


def make_entry(value: str, properties: Dict) -> Dict:
    return {
        "id": properties["sha256_hash"],
        "value": value,
        "properties": properties,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
