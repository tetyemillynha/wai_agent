import hashlib

_summary_cache = {}

def get_cache_key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def get_summary_from_cache(markdown: str) -> str | None:
    key = get_cache_key(markdown)
    return _summary_cache.get(key)

def save_summary_to_cache(markdown: str, summary: str):
    key = get_cache_key(markdown)
    _summary_cache[key] = summary