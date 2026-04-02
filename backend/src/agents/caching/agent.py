"""
Caching Agent - Simple in-memory cache
"""
import time
import hashlib
from typing import Dict, Any, Optional

class CachingAgent:
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = 3600  # 1 hour

    def get(self, query: str) -> Optional[Dict[str, Any]]:
        key = self._make_key(query)
        entry = self.cache.get(key)
        if entry and entry["expires"] > time.time():
            entry["hits"] += 1
            return entry["data"]
        elif entry:
            del self.cache[key]
        return None

    def set(self, query: str, data: Dict[str, Any]):
        key = self._make_key(query)
        self.cache[key] = {
            "data": data,
            "created": time.time(),
            "expires": time.time() + self.ttl,
            "hits": 0
        }

    def _make_key(self, query: str) -> str:
        return hashlib.md5(query.lower().encode()).hexdigest()

    def get_stats(self) -> Dict[str, Any]:
        total = len(self.cache)
        hits = sum(e["hits"] for e in self.cache.values())
        expired = sum(1 for e in self.cache.values() if e["expires"] <= time.time())
        return {
            "total_entries": total,
            "total_hits": hits,
            "avg_hits": hits / total if total > 0 else 0,
            "expired_entries": expired,
            "active_entries": total - expired,
            "cache_ttl_seconds": self.ttl
        }

    def clear(self):
        self.cache = {}


caching_agent = CachingAgent()

def get_cache_stats() -> Dict[str, Any]:
    return caching_agent.get_stats()
