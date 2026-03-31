import os
import requests
from datetime import datetime


# ============================================
# Environment Variables
# ============================================

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or os.getenv("NEW_SECRET")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")


# ============================================
# Intent Detection
# ============================================

def detect_query_intent(query):

    query = query.lower()

    if "best" in query or "top" in query:
        return "recommendation"

    if "side effect" in query:
        return "safety"

    if "cycle" in query or "plan" in query:
        return "planning"

    if "vs" in query or "compare" in query:
        return "comparison"

    return "general"


# ============================================
# Claude Research
# ============================================

def claude_research(query, deep=False):

    if not ANTHROPIC_API_KEY:
        return None

    try:

        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        mode = "Deep Research" if deep else "Standard Research"

        prompt = f"""
You are a Professional Health & Fitness AI.

User Query: {query}

Mode: {mode}

Generate response in this format:

Conversational Answer:

What It Is:
How It Works:
Benefits:
Dosage:
Timing:
Side Effects:
Who Should Avoid:
Best Use Cases:

Return clean text.
"""

        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 2000,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=40
        )

        if response.status_code != 200:
            print("Claude Error:", response.text)
            return None

        data = response.json()

        return data["content"][0]["text"]

    except Exception as e:
        print("Claude Exception:", str(e))
        return None


# ============================================
# Real Time Sources
# ============================================

def real_time_sources(query):

    if not SERPAPI_KEY:
        return []

    try:

        url = "https://serpapi.com/search"

        params = {
            "q": query,
            "api_key": SERPAPI_KEY,
            "engine": "google"
        }

        response = requests.get(url, params=params)

        data = response.json()

        sources = []

        if "organic_results" in data:

            for r in data["organic_results"][:5]:

                sources.append({
                    "title": r.get("title"),
                    "link": r.get("link"),
                    "snippet": r.get("snippet")
                })

        return sources

    except:
        return []


# ============================================
# Fallback Answer
# ============================================

def fallback_answer(query):

    return f"""
Here is information about {query}.

{query} is commonly used in fitness and health.

Benefits:
• Improves performance
• Supports muscle growth
• Helps recovery

Dosage:
Depends on individual needs

Side Effects:
Usually mild if used properly
"""


# ============================================
# Product Recommendations
# ============================================

def get_recommendations(query):

    return [

        {
            "name": "Optimum Nutrition Whey",
            "rating": 4.8,
            "price": "₹4500"
        },

        {
            "name": "MuscleBlaze Whey",
            "rating": 4.6,
            "price": "₹3200"
        }

    ]


# ============================================
# Main Search
# ============================================

def search_knowledge(query):

    intent = detect_query_intent(query)

    answer = claude_research(query)

    if not answer:
        answer = fallback_answer(query)

    sources = real_time_sources(query)

    return {

        "query": query,
        "answer": answer,
        "intent": intent,
        "sources": sources,
        "products": get_recommendations(query),
        "timestamp": datetime.now().isoformat()

    }


# ============================================
# Deep Research
# ============================================

def deep_research(query):

    answer = claude_research(query, deep=True)

    if not answer:
        answer = fallback_answer(query)

    return {

        "query": query,
        "answer": answer,
        "sources": real_time_sources(query),
        "timestamp": datetime.now().isoformat()

    }


# ============================================
# Main API Entry
# ============================================

def search_ai(query, deep=False):

    if deep:
        return deep_research(query)

    return search_knowledge(query)
