import os
import requests
import sqlite3
import json
from datetime import datetime

# ============================================
# ENV
# ============================================

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or os.getenv("NEW_SECRET")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# ============================================
# CACHE
# ============================================

CACHE_DB = "search_cache.db"


def init_cache():

    conn = sqlite3.connect(CACHE_DB)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS report_cache(
        query TEXT PRIMARY KEY,
        data TEXT,
        created TEXT
    )
    """)

    conn.close()


init_cache()


def _cache_stats():

    conn = sqlite3.connect(CACHE_DB)

    count = conn.execute(
        "SELECT count(*) FROM report_cache"
    ).fetchone()[0]

    conn.close()

    return {"cached": count}


# ============================================
# Claude Research
# ============================================

def claude_research(query):

    if not ANTHROPIC_API_KEY:
        return None

    try:

        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        prompt = f"""
Explain {query} in fitness and bodybuilding.

Provide:

What it is
How it works
Benefits
Dosage
Timing
Side Effects
Best Use Cases
"""

        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1500,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=30
        )

        if r.status_code != 200:
            return None

        data = r.json()

        return data["content"][0]["text"]

    except Exception as e:

        print("Claude error:", e)

        return None


# ============================================
# Sources
# ============================================

def get_sources(query):

    if not SERPAPI_KEY:
        return []

    try:

        url = "https://serpapi.com/search"

        params = {
            "q": query,
            "api_key": SERPAPI_KEY,
            "engine": "google"
        }

        r = requests.get(url, params=params)

        data = r.json()

        sources = []

        if "organic_results" in data:

            for s in data["organic_results"][:5]:

                sources.append({

                    "title": s.get("title"),
                    "link": s.get("link"),
                    "snippet": s.get("snippet")

                })

        return sources

    except:

        return []


# ============================================
# fallback
# ============================================

def fallback(query):

    return f"""
{query} is commonly used in fitness and bodybuilding.

Benefits:
• Muscle growth
• Fat loss
• Better recovery

Dosage:
Depends on user goal

Side Effects:
Usually mild when used properly
"""


# ============================================
# Main Search
# ============================================

def search_knowledge(query, filters=None):

    conn = sqlite3.connect(CACHE_DB)

    row = conn.execute(
        "SELECT data FROM report_cache WHERE query=?",
        (query,)
    ).fetchone()

    if row:

        conn.close()

        return json.loads(row[0])

    answer = claude_research(query)

    if not answer:
        answer = fallback(query)

    sources = get_sources(query)

    results = [

        {

            "title": query,

            "content": answer,

            "sources": sources,

            "timestamp": datetime.now().isoformat()

        }

    ]

    conn.execute(
        "INSERT OR REPLACE INTO report_cache VALUES (?,?,?)",
        (query, json.dumps(results), datetime.now().isoformat())
    )

    conn.commit()

    conn.close()

    return results


# ============================================
# Recommendations
# ============================================

def get_recommendations(queries, user):

    return [

        {
            "title": "Creatine Guide"
        },

        {
            "title": "Best Whey Protein"
        }

    ]
