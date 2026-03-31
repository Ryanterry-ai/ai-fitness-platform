# search_ai.py

import requests
import sqlite3
import json
import time
import os
from concurrent.futures import ThreadPoolExecutor

CACHE_EXPIRY = 3600
TRENDING_LIMIT = 10

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
CLAUDE_URL = "https://api.anthropic.com/v1/messages"

SOURCE_WEIGHTS = {
    "pubmed": 100,
    "nih": 95,
    "examine": 90,
    "semantic": 85,
    "youtube": 60,
    "reddit": 40
}

ENTITY_GROUPS = {
    "creatine": ["creatine"],
    "whey": ["whey"],
    "fat_loss": ["fat loss"],
    "muscle_gain": ["muscle gain"],
    "sarms": ["sarms"],
    "steroids": ["testosterone"]
}


# ------------------------------
# INTENT
# ------------------------------

def classify_intent(query):

    q = query.lower()

    if "best" in q:
        return "product"

    if "what is" in q:
        return "informational"

    if "side effect" in q:
        return "safety"

    return "general"


# ------------------------------
# ENTITY
# ------------------------------

def extract_entity(query):

    q = query.lower()

    for key, values in ENTITY_GROUPS.items():

        for v in values:
            if v in q:
                return key

    return None


# ------------------------------
# QUERY EXPANSION
# ------------------------------

def expand_query(query):

    return [
        query,
        query + " research",
        query + " dosage",
        query + " benefits",
        query + " side effects"
    ]


# ------------------------------
# TRENDING
# ------------------------------

def init_trending():

    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trending (
    query TEXT,
    count INTEGER,
    timestamp REAL)
    """)

    conn.commit()


def update_trending(query):

    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT count FROM trending WHERE query=?",
        (query,)
    )

    result = cursor.fetchone()

    if result:

        cursor.execute(
            "UPDATE trending SET count=? WHERE query=?",
            (result[0] + 1, query)
        )

    else:

        cursor.execute(
            "INSERT INTO trending VALUES (?,?,?)",
            (query, 1, time.time())
        )

    conn.commit()


def get_trending():

    conn = sqlite3.connect("cache.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT query FROM trending ORDER BY count DESC LIMIT ?",
        (TRENDING_LIMIT,)
    )

    return [r[0] for r in cursor.fetchall()]


# ------------------------------
# SOURCES
# ------------------------------

def search_pubmed(query):

    return [
        {"title": query + " PubMed", "source": "pubmed"}
    ]


def search_youtube(query):

    return [
        {"title": query + " YouTube", "source": "youtube"}
    ]


def search_reddit(query):

    return [
        {"title": query + " Reddit", "source": "reddit"}
    ]


# ------------------------------
# MULTI SOURCE
# ------------------------------

def retrieve_sources(query):

    with ThreadPoolExecutor() as ex:

        pubmed = ex.submit(search_pubmed, query)
        youtube = ex.submit(search_youtube, query)
        reddit = ex.submit(search_reddit, query)

        return {
            "pubmed": pubmed.result(),
            "youtube": youtube.result(),
            "reddit": reddit.result()
        }


# ------------------------------
# DEEP RESEARCH
# ------------------------------

def deep_research(query):

    queries = expand_query(query)

    results = {}

    for q in queries:

        data = retrieve_sources(q)

        for k, v in data.items():

            if k not in results:
                results[k] = []

            results[k].extend(v)

    return results


# ------------------------------
# RANK
# ------------------------------

def rank(results):

    ranked = []

    for src, items in results.items():

        score = SOURCE_WEIGHTS.get(src, 10)

        for i in items:

            ranked.append({
                "data": i,
                "score": score,
                "credibility":
                "High" if score > 90 else
                "Medium" if score > 60 else
                "Low"
            })

    ranked.sort(key=lambda x: x["score"], reverse=True)

    return ranked


# ------------------------------
# CLAUDE
# ------------------------------

def claude_answer(query, summary):

    try:

        prompt = f"""
User Query: {query}

Summary:
{summary}

Generate conversational fitness answer
"""

        headers = {
            "x-api-key": CLAUDE_API_KEY,
            "anthropic-version": "2023-06-01"
        }

        r = requests.post(

            CLAUDE_URL,
            headers=headers,
            json={
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 600,
                "messages":[
                    {"role":"user","content":prompt}
                ]
            }

        )

        return r.json()["content"][0]["text"]

    except:

        return "AI answer unavailable"


# ------------------------------
# PRODUCTS
# ------------------------------

def products(entity):

    if entity == "creatine":

        return [

            {"name":"Optimum Nutrition Creatine","rating":4.8},
            {"name":"MuscleBlaze Creatine","rating":4.6}

        ]

    return []


# ------------------------------
# MAIN
# ------------------------------

def search(query, deep=False):

    init_trending()
    update_trending(query)

    intent = classify_intent(query)
    entity = extract_entity(query)

    results = deep_research(query) if deep else retrieve_sources(query)

    ranked = rank(results)

    summary = [r["data"] for r in ranked[:5]]

    ai = claude_answer(query, summary)

    return {

        "query": query,
        "intent": intent,
        "entity": entity,
        "ai_answer": ai,
        "summary": summary,
        "results": ranked,
        "products": products(entity),
        "trending": get_trending()

    }
