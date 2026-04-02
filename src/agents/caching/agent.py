"""Caching Agent - Simple in-memory cache"""
import time, hashlib
from typing import Dict, Any

class CachingAgent:
    def __init__(self):
        self.cache: Dict[str, Dict] = {}
        self.ttl = 3600

    def get(self, query: str) -> Any:
        key = hashlib.md5(query.lower().encode()).hexdigest()
        entry = self.cache.get(key)
        if entry and entry["expires"] > time.time():
            entry["hits"] += 1
            return entry["data"]
        return None

    def set(self, query: str, data: Dict):
        key = hashlib.md5(query.lower().encode()).hexdigest()
        self.cache[key] = {"data": data, "created": time.time(), "expires": time.time() + self.ttl, "hits": 0}

    def get_stats(self) -> Dict:
        total = len(self.cache)
        hits = sum(e["hits"] for e in self.cache.values())
        return {"total_entries": total, "total_hits": hits, "avg_hits": hits / total if total > 0 else 0, "expired": sum(1 for e in self.cache.values() if e["expires"] <= time.time())}

    def clear(self):
        self.cache = {}

caching_agent = CachingAgent()

def get_cache_stats() -> Dict:
    return caching_agent.get_stats()
