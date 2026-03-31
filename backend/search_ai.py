import os
import json
import requests
from datetime import datetime

# ============================================
# Environment Variables
# ============================================

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or os.getenv("NEW_SECRET")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# ============================================
# Query Intent Detection
# ============================================

def detect_query_intent(query):

    query = query.lower()

    if any(x in query for x in ["what is", "kya hai", "meaning", "define"]):
        return "informational"

    if any(x in query for x in ["best", "top", "recommend"]):
        return "recommendation"

    if any(x in query for x in ["side effects", "safe", "danger"]):
        return "safety"

    if any(x in query for x in ["cycle", "plan", "diet", "workout"]):
        return "planning"

    if any(x in query for x in ["vs", "compare"]):
        return "comparison"

    return "general"


# ============================================
# Query Expansion
# ============================================

def expand_query(query):

    return [
        query,
        f"{query} benefits",
        f"{query} dosage",
        f"{query} side effects",
        f"{query} research",
        f"{query} guide"
    ]


# ============================================
# Claude Deep Research
# ============================================

def claude_deep_research(query):

    if not ANTHROPIC_API_KEY:
        return None

    try:

        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        prompt = f"""
You are an AI Health & Fitness Research Engine.

User Query: {query}

Generate structured answer:

WHAT IT IS
HOW IT WORKS
BENEFITS
DOSAGE
TIMING
SIDE EFFECTS
WHO SHOULD AVOID
BEST USE CASES
REFERENCES

Return clean structured paragraphs.
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
            timeout=30
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
# Real Time Research (SerpAPI)
# ============================================

def real_time_research(query):

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

        results = response.json()

        articles = []

        if "organic_results" in results:

            for r in results["organic_results"][:5]:

                articles.append({
                    "title": r.get("title"),
                    "link": r.get("link"),
                    "snippet": r.get("snippet"),
                    "source": "Google"
                })

        return articles

    except:
        return []


# ============================================
# Knowledge Base Fallback
# ============================================

def fallback_knowledge(query):

    return {
        "what_it_is": f"{query} is related to health, fitness, or performance optimization.",
        "how_it_works": "It works through physiological adaptation and performance improvement.",
        "benefits": [
            "Improves performance",
            "Supports muscle growth",
            "Enhances recovery"
        ],
        "dosage": "Depends on compound or training protocol",
        "timing": "Depends on usage",
        "side_effects": [
            "Individual variation",
            "Possible mild side effects"
        ],
        "references": []
    }


# ============================================
# Product Recommendation
# ============================================

def detect_product_query(query):

    keywords = [
        "best",
        "buy",
        "top",
        "recommend"
    ]

    return any(k in query.lower() for k in keywords)


def product_results(query):

    return [
        {
            "name": "Optimum Nutrition Whey Protein",
            "rating": 4.8,
            "badge": "Popular",
            "price": "₹4500"
        },
        {
            "name": "MuscleBlaze Whey",
            "rating": 4.6,
            "badge": "Best Value",
            "price": "₹3200"
        }
    ]


# ============================================
# Main Search Function
# ============================================

def search_ai(query, deep=False):

    intent = detect_query_intent(query)

    # Deep Research Mode
    claude_answer = None

    if deep:
        claude_answer = claude_deep_research(query)

    # Real Time Research
    sources = real_time_research(query)

    # Fallback
    fallback = fallback_knowledge(query)

    # Product Results
    products = []

    if detect_product_query(query):
        products = product_results(query)

    # Claude Success
    if claude_answer:

        return {
            "name": query,
            "category": intent,
            "evidence_tier": "High",
            "sections": {
                "what_it_is": claude_answer,
                "how_it_works": "",
                "benefits": [],
                "dosage": "",
                "timing": "",
                "side_effects": [],
                "references": sources
            },
            "products": products,
            "timestamp": datetime.now().isoformat()
        }

    # Fallback Response

    return {
        "name": query,
        "category": intent,
        "evidence_tier": "Moderate",
        "sections": {
            "what_it_is": fallback["what_it_is"],
            "how_it_works": fallback["how_it_works"],
            "benefits": fallback["benefits"],
            "dosage": fallback["dosage"],
            "timing": fallback["timing"],
            "side_effects": fallback["side_effects"],
            "references": sources
        },
        "products": products,
        "timestamp": datetime.now().isoformat()
    }
