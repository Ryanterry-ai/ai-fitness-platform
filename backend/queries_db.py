"""
queries_db.py — Store user queries and live web search results
================================================================
Captures every search query and stores live web results (Google) 
alongside it for future reference and enrichment.
"""
import os, sqlite3, json, threading
from datetime import datetime, timezone
from typing import Any

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, "database", "queries.db")
_lock    = threading.Lock()

def _init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS queries (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        query           TEXT    NOT NULL,
        query_hash      TEXT    NOT NULL,
        created_at      TEXT    DEFAULT (datetime('now')),
        results_count   INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS live_results (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        query_id        INTEGER NOT NULL,
        source          TEXT    NOT NULL DEFAULT 'google',
        result_data     TEXT    NOT NULL,
        created_at      TEXT    DEFAULT (datetime('now')),
        FOREIGN KEY(query_id) REFERENCES queries(id) ON DELETE CASCADE
    );
    CREATE INDEX IF NOT EXISTS idx_q_hash ON queries(query_hash);
    CREATE INDEX IF NOT EXISTS idx_lr_qid ON live_results(query_id);
    """)
    conn.commit()
    conn.close()

_init_db()

def _hash_query(q: str) -> str:
    import hashlib
    return hashlib.sha256(q.lower().strip().encode()).hexdigest()[:32]

def save_query(query: str) -> int:
    qhash = _hash_query(query)
    with _lock:
        conn = sqlite3.connect(DB_PATH)
        try:
            row = conn.execute(
                "SELECT id FROM queries WHERE query_hash=?", (qhash,)
            ).fetchone()
            if row:
                query_id = row[0]
                conn.execute(
                    "UPDATE queries SET created_at=datetime('now') WHERE id=?",
                    (query_id,)
                )
            else:
                cur = conn.execute(
                    "INSERT INTO queries (query, query_hash) VALUES (?, ?)",
                    (query, qhash)
                )
                query_id = cur.lastrowid
            conn.commit()
            return query_id
        finally:
            conn.close()

def save_live_results(query_id: int, source: str, results: list[dict]):
    if not results:
        return
    with _lock:
        conn = sqlite3.connect(DB_PATH)
        try:
            conn.execute(
                "DELETE FROM live_results WHERE query_id=? AND source=?",
                (query_id, source)
            )
            for r in results:
                conn.execute(
                    "INSERT INTO live_results (query_id, source, result_data) VALUES (?, ?, ?)",
                    (query_id, source, json.dumps(r))
                )
            conn.execute(
                "UPDATE queries SET results_count=? WHERE id=?",
                (len(results), query_id)
            )
            conn.commit()
        finally:
            conn.close()

def get_live_results(query: str, source: str = "google") -> list[dict]:
    qhash = _hash_query(query)
    with _lock:
        conn = sqlite3.connect(DB_PATH)
        try:
            row = conn.execute(
                "SELECT id FROM queries WHERE query_hash=?", (qhash,)
            ).fetchone()
            if not row:
                return []
            query_id = row[0]
            rows = conn.execute(
                "SELECT result_data FROM live_results WHERE query_id=? AND source=? ORDER BY id",
                (query_id, source)
            ).fetchall()
            return [json.loads(r[0]) for r in rows]
        finally:
            conn.close()

def get_or_fetch_live(query: str, fetch_func) -> tuple[list[dict], bool]:
    cached = get_live_results(query, "google")
    if cached:
        return cached, False
    
    fresh = fetch_func()
    if fresh:
        query_id = save_query(query)
        save_live_results(query_id, "google", fresh)
    return fresh, True

def get_recent_queries(limit: int = 50) -> list[dict]:
    with _lock:
        conn = sqlite3.connect(DB_PATH)
        try:
            rows = conn.execute(
                "SELECT id, query, created_at, results_count FROM queries ORDER BY created_at DESC LIMIT ?",
                (limit,)
            ).fetchall()
            return [{"id": r[0], "query": r[1], "created_at": r[2], "results_count": r[3]} for r in rows]
        finally:
            conn.close()

def get_query_count() -> int:
    with _lock:
        conn = sqlite3.connect(DB_PATH)
        try:
            row = conn.execute("SELECT COUNT(*) FROM queries").fetchone()
            return row[0] if row else 0
        finally:
            conn.close()
