from typing import Optional, Dict
import re


def parse(query: str) -> Optional[Dict]:
    q = query.lower().strip()
    filters = {}

    # Examples: "all single word palindromic strings"
    if "single word" in q or "one word" in q:
        filters["word_count"] = 1

    if "palindrom" in q:
        filters["is_palindrome"] = True

    m = re.search(r"longer than (\d+)", q)
    if m:
        filters["min_length"] = int(m.group(1)) + 0  # user said longer than N -> min_length = N+1? We'll use N

    m = re.search(r"strings longer than (\d+)", q)
    if m:
        filters["min_length"] = int(m.group(1)) + 1

    m = re.search(r"contain(?:ing)? the letter (\w)", q)
    if m:
        filters["contains_character"] = m.group(1)

    # heuristic: "contain the first vowel" -> 'a'
    if "first vowel" in q:
        filters["contains_character"] = "a"

    # If nothing parsed, return None
    if not filters:
        return None
    return filters
