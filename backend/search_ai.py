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

def claude_research(query, deep=False):

    if not ANTHROPIC_API_KEY:
        return None

    try:

        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }

        research_mode = "Deep Research Mode" if deep else "Standard Research"

        prompt = f"""
You are an AI Health & Fitness Answer Engine.

Query: {query}

Mode: {research_mode}

Generate ChatGPT-style response:

1. Conversational Answer

2. What it is

3. How it Works

4. Benefits

5. Dosage

6. Timing

7. Side Effects

8. Who Should Avoid

9. Best Use Cases

Also Provide Sources:

Return structured response.
"""

        payload = {
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 2500,
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
# Real Time Research
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

        data = response.json()

        sources = []

        if "organic_results" in data:

            for r in data["organic_results"][:6]:

                sources.append({
                    "title": r.get("title"),
                    "link": r.get("link"),
                    "snippet": r.get("snippet"),
                    "source": "Google"
                })

        return sources

    except Exception as e:
        print("SERP Error:", str(e))
        return []


# ============================================
# Product Detection
# ============================================

def detect_product_query(query):

    keywords = ["best", "top", "buy", "recommend"]

    return any(k in query.lower() for k in keywords)


# ============================================
# Product Results
# ============================================

def product_results(query):

    return [

        {
            "name": "Optimum Nutrition Gold Standard Whey",
            "rating": 4.8,
            "badge": "Best Seller",
            "price": "₹4500"
        },

        {
            "name": "MuscleBlaze Whey Protein",
            "rating": 4.6,
            "badge": "Best Value",
            "price": "₹3200"
        },

        {
            "name": "MyProtein Impact Whey",
            "rating": 4.7,
            "badge": "Popular",
            "price": "₹3900"
        }

    ]


# ============================================
# Main Search Function
# ============================================

def search_knowledge(query):

    intent = detect_query_intent(query)

    expanded_queries = expand_query(query)

    sources = []

    for q in expanded_queries:
        sources.extend(real_time_research(q))

    claude_answer = claude_research(query)

    products = []

    if detect_product_query(query):
        products = product_results(query)

    return {

        "answer": claude_answer,
        "intent": intent,
        "sources": sources,
        "products": products,
        "timestamp": datetime.now().isoformat()

    }


# ============================================
# Deep Research
# ============================================

def deep_research(query):

    intent = detect_query_intent(query)

    sources = real_time_research(query)

    claude_answer = claude_research(query, deep=True)

    return {

        "answer": claude_answer,
        "intent": intent,
        "sources": sources,
        "timestamp": datetime.now().isoformat()

    }


# ============================================
# Recommendations
# ============================================

def get_recommendations(query):

    products = product_results(query)

    return {

        "answer": "Top recommended products based on query",
        "products": products,
        "timestamp": datetime.now().isoformat()

    }


# ============================================
# Backward Compatible Function
# ============================================

def search_ai(query, deep=False):

    if deep:
        return deep_research(query)

    return search_knowledge(query)
