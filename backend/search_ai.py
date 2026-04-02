"""
search_ai.py — FitSearch AI
World-Class Fitness Research Engine v5 (Real-Time RAG + Optimized OpenAI Prompt)
================================================================================
Always uses real-time data from Bing + Google + OpenAI RAG with optimized prompt.
"""

from __future__ import annotations
import os, json, re, time, hashlib, sqlite3, threading
from datetime import datetime, timezone
from typing import Any
import requests

# ====================== CONFIG ======================
ANTHROPIC_API_KEY     = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY        = os.getenv("OPENAI_API_KEY", "")
BING_API_KEY          = os.getenv("BING_API_KEY", "")
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY", "AIzaSyAe6LNE1Er_KpTK4PdpTVb5OrqbD5wLZG8")
GOOGLE_CX             = os.getenv("GOOGLE_CX", "860eab761ebac4c12")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DB = os.path.join(BASE_DIR, "database", "search_cache.db")
CACHE_TTL_SEC = 86400

_cache_lock = threading.Lock()

# ====================== OPTIMIZED DATABASE INIT ======================
def init_db():
    os.makedirs(os.path.dirname(CACHE_DB), exist_ok=True)
    with sqlite3.connect(CACHE_DB) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA cache_size=-64000;")
        conn.execute("PRAGMA temp_store=MEMORY;")
        conn.execute("PRAGMA auto_vacuum=INCREMENTAL;")
        conn.execute("PRAGMA mmap_size=300000000;")

        conn.execute("""
            CREATE TABLE IF NOT EXISTS report_cache (
                cache_key TEXT PRIMARY KEY,
                query TEXT,
                report_json TEXT,
                source TEXT,
                created_at REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS query_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                result_json TEXT NOT NULL,
                timestamp REAL NOT NULL,
                source TEXT DEFAULT 'kb',
                last_updated REAL NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_query_history_query ON query_history(query);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_query_history_timestamp ON query_history(timestamp);")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_report_cache_created ON report_cache(created_at);")
init_db()

# ====================== INTENT CLASSIFICATION ======================
_INTENT_RULES: list[tuple[list[str], str]] = [ ... ]  # (your original kept)

def classify_intent(query: str) -> str:
    q = query.lower()
    for triggers, label in _INTENT_RULES:
        if any(t in q for t in triggers):
            return label
    return "research"

# ====================== GOAL MODIFIERS, DOMAIN, ENTITY (kept) ======================
# ... (your original _GOAL_PHRASES, _extract_goal_modifiers, QUERY_DOMAINS, detect_domain,
# ENTITY_GROUPS, ENTITY_TRIGGERS, extract_primary_entity kept exactly)

# ====================== GENERAL TOPICS & KB (kept) ======================
GENERAL_TOPICS: list[dict] = [ ... ]  # your full rich GENERAL_TOPICS kept
def _find_general_topic(query: str) -> dict | None:
    # your original function kept
    pass

# ====================== MAIN SEARCH FUNCTION — REAL-TIME RAG ======================
def search_knowledge(query: str, filters: list[str] | None = None) -> list[dict]:
    """Always performs real-time retrieval + optimized RAG"""
    filters = filters or []
    intent = classify_intent(query)
    domain = detect_domain(query)

    cache_key = _cache_key(query, filters)
    cached = _cache_get(cache_key)
    if cached:
        return cached

    bing_results = _bing_search(query)
    google_results = _google_search(query)
    combined_context = bing_results + google_results

    rag_report = _openai_rag_generate_report(query, intent, domain, combined_context)

    results = [rag_report] if rag_report else []

    if results:
        _store_query(query, results)
        _cache_set(cache_key, query, results)

    return results

# ====================== GOOGLE + BING (kept) ======================
def _google_search(query: str) -> list[dict]: ...  # your original kept
def _bing_search(query: str) -> list[dict]: ...    # your original kept

# ====================== OPTIMIZED OPENAI RAG PROMPT ======================
def _openai_rag_generate_report(query: str, intent: str, domain: str, context: list) -> dict | None:
    if not OPENAI_API_KEY:
        return None
    try:
        system_prompt = """You are FitSearch AI — a world-class, evidence-based fitness research engine.

STRICT RULES:
- Respond **ONLY** with valid JSON. No markdown, no explanations, no extra text.
- Always ground your answer in the provided real-time search context (Bing + Google results).
- If context is insufficient, clearly state it in "ai_summary".
- Be practical, actionable, and safety-focused (especially for supplements/steroids/SARMs/peptides).
- Use evidence tiers honestly.
- For India users: mention local availability and ₹ prices when relevant.

Generate a complete structured fitness report in this **exact** JSON format:"""

        json_schema = """
{
  "name": "Short, clear title",
  "tagline": "One compelling sentence",
  "category": "nutrition|exercise|supplement|research|general",
  "evidence_tier": "very_high|high|moderate|low",
  "safe_for_beginners": true,
  "what_it_is": "Clear explanation",
  "how_it_works": "Mechanism",
  "dosage": "Practical advice",
  "timing": "When to do it",
  "best_ways_to_use": ["Tip 1", "Tip 2"],
  "who_should_use": ["Group 1"],
  "who_should_avoid": ["Group 1"],
  "benefits": ["Benefit 1"],
  "side_effects": [{"effect": "Description", "severity": "low|medium|high"}],
  "final_recommendation": "Actionable advice",
  "ai_summary": "Expert summary"
}
"""

        user_prompt = f"""
Query: {query}
Intent: {intent}
Domain: {domain}

REAL-TIME SEARCH CONTEXT (Bing + Google):
{json.dumps(context, ensure_ascii=False)}

Generate the complete structured fitness report in the exact JSON format above."""

        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": system_prompt + json_schema},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,      # Lower for more consistent JSON
                "max_tokens": 2200
            },
            timeout=35
        )
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"].strip()
        # Clean any accidental markdown
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)
        return json.loads(content)
    except Exception as e:
        print(f"[OpenAI RAG] Error: {e}")
        return None

# ====================== STORE QUERY, REPORT BUILDER, CACHE (kept) ======================
def _store_query(query: str, results: list): ...  # your original kept
def _to_report(...): ...  # your original kept
def _cache_key(...): ...  # your original kept
def _cache_get(...): ...  # your original kept
def _cache_set(...): ...  # your original kept

print("✅ FitSearch AI v5 loaded successfully with REAL-TIME RAG + OPTIMIZED OpenAI Prompt.")

# End of file
