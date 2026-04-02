"""
Caching Agent
=============
Manages caching of search results and responses.
"""

import hashlib
import json
import os
import sqlite3
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from threading import Lock
from src.config import settings


class CachingAgent:
    """
    Agent responsible for caching search results and responses.
    
    Responsibilities:
    - Cache query results for faster repeat queries
    - Manage cache expiration
    - Store search results
    - Track cache statistics
    """
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or self._get_default_db_path()
        self.cache_ttl = settings.CACHE_TTL_SECONDS
        self.lock = Lock()
        self._init_cache()
    
    def _get_default_db_path(self) -> str:
        """Get default cache database path"""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(base_dir, "database", "cache.db")
    
    def _init_cache(self) -> None:
        """Initialize cache database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS query_cache (
                    cache_key TEXT PRIMARY KEY,
                    query TEXT NOT NULL,
                    response_json TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    expires_at REAL NOT NULL,
                    hit_count INTEGER DEFAULT 0,
                    query_hash TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_expires
                ON query_cache(expires_at)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_query_hash
                ON query_cache(query_hash)
            """)
    
    def _generate_cache_key(self, query: str, filters: Optional[List[str]] = None) -> str:
        """Generate cache key from query and filters"""
        cache_data = {
            "query": query.lower().strip(),
            "filters": sorted(filters) if filters else []
        }
        cache_json = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_json.encode()).hexdigest()[:32]
    
    def _generate_query_hash(self, query: str) -> str:
        """Generate shorter hash for lookup"""
        return hashlib.md5(query.lower().strip().encode()).hexdigest()[:16]
    
    def get(self, query: str, filters: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached response for query.
        
        Args:
            query: Search query string
            filters: Optional filter list
            
        Returns:
            Cached response dict or None if not found/expired
        """
        cache_key = self._generate_cache_key(query, filters)
        
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        """
                        SELECT response_json, expires_at, hit_count
                        FROM query_cache
                        WHERE cache_key = ?
                        """,
                        (cache_key,)
                    )
                    row = cursor.fetchone()
                    
                    if not row:
                        return None
                    
                    response_json, expires_at, hit_count = row
                    current_time = time.time()
                    
                    # Check if expired
                    if current_time > expires_at:
                        # Delete expired entry
                        conn.execute(
                            "DELETE FROM query_cache WHERE cache_key = ?",
                            (cache_key,)
                        )
                        return None
                    
                    # Increment hit count
                    conn.execute(
                        "UPDATE query_cache SET hit_count = ? WHERE cache_key = ?",
                        (hit_count + 1, cache_key)
                    )
                    
                    return json.loads(response_json)
                    
            except Exception as e:
                print(f"Cache get error: {e}")
                return None
    
    def set(
        self,
        query: str,
        response: Dict[str, Any],
        filters: Optional[List[str]] = None,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Cache a response for a query.
        
        Args:
            query: Search query string
            response: Response dictionary to cache
            filters: Optional filter list
            ttl: Optional custom TTL in seconds
            
        Returns:
            True if cached successfully
        """
        cache_key = self._generate_cache_key(query, filters)
        query_hash = self._generate_query_hash(query)
        current_time = time.time()
        expires_at = current_time + (ttl or self.cache_ttl)
        
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO query_cache
                        (cache_key, query, response_json, created_at, expires_at, hit_count, query_hash)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            cache_key,
                            query,
                            json.dumps(response),
                            current_time,
                            expires_at,
                            0,
                            query_hash
                        )
                    )
                    return True
                    
            except Exception as e:
                print(f"Cache set error: {e}")
                return False
    
    def invalidate(self, query: str, filters: Optional[List[str]] = None) -> bool:
        """
        Invalidate cached response for query.
        
        Args:
            query: Search query string
            filters: Optional filter list
            
        Returns:
            True if invalidated successfully
        """
        cache_key = self._generate_cache_key(query, filters)
        
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute(
                        "DELETE FROM query_cache WHERE cache_key = ?",
                        (cache_key,)
                    )
                    return True
                    
            except Exception as e:
                print(f"Cache invalidate error: {e}")
                return False
    
    def clear_expired(self) -> int:
        """
        Clear all expired cache entries.
        
        Returns:
            Number of entries cleared
        """
        current_time = time.time()
        
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        "DELETE FROM query_cache WHERE expires_at < ?",
                        (current_time,)
                    )
                    return cursor.rowcount
                    
            except Exception as e:
                print(f"Cache clear error: {e}")
                return 0
    
    def clear_all(self) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            True if cleared successfully
        """
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM query_cache")
                    return True
                    
            except Exception as e:
                print(f"Cache clear all error: {e}")
                return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute(
                        """
                        SELECT
                            COUNT(*) as total,
                            SUM(hit_count) as total_hits,
                            MAX(hit_count) as max_hits,
                            AVG(hit_count) as avg_hits,
                            MIN(created_at) as oldest,
                            MAX(created_at) as newest
                        FROM query_cache
                        """
                    )
                    row = cursor.fetchone()
                    
                    total, total_hits, max_hits, avg_hits, oldest, newest = row
                    
                    # Count expired
                    current_time = time.time()
                    cursor = conn.execute(
                        "SELECT COUNT(*) FROM query_cache WHERE expires_at < ?",
                        (current_time,)
                    )
                    expired = cursor.fetchone()[0]
                    
                    return {
                        "total_entries": total or 0,
                        "total_hits": total_hits or 0,
                        "max_hits": max_hits or 0,
                        "avg_hits": round(avg_hits or 0, 2),
                        "expired_entries": expired,
                        "active_entries": (total or 0) - expired,
                        "oldest_entry": datetime.fromtimestamp(oldest).isoformat() if oldest else None,
                        "newest_entry": datetime.fromtimestamp(newest).isoformat() if newest else None,
                        "cache_ttl_seconds": self.cache_ttl
                    }
                    
            except Exception as e:
                print(f"Cache stats error: {e}")
                return {
                    "total_entries": 0,
                    "total_hits": 0,
                    "error": str(e)
                }


# Singleton instance
caching_agent = CachingAgent()


def get_cached_response(query: str, filters: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    """
    Convenience function to get cached response.
    
    Args:
        query: Search query string
        filters: Optional filter list
        
    Returns:
        Cached response or None
    """
    return caching_agent.get(query, filters)


def cache_response(
    query: str,
    response: Dict[str, Any],
    filters: Optional[List[str]] = None,
    ttl: Optional[int] = None
) -> bool:
    """
    Convenience function to cache response.
    
    Args:
        query: Search query string
        response: Response dictionary
        filters: Optional filter list
        ttl: Optional custom TTL
        
    Returns:
        True if cached successfully
    """
    return caching_agent.set(query, response, filters, ttl)


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics"""
    return caching_agent.get_stats()
