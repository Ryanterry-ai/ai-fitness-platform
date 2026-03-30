# backend/search_ai.py

"""
World Class Search AI
- Intent Classification
- Domain Routing
- Real-time Retrieval
- Backward Compatibility (IMPORTANT)
"""

from typing import List, Dict, Optional

# Safe relative imports for Render deployment
try:
    from .intent_classifier import classify_intent
    from .domain_router import route_domain
    from .realtime_fetch import fetch_realtime_results
except Exception:
    # fallback if running locally
    from intent_classifier import classify_intent
    from domain_router import route_domain
    from realtime_fetch import fetch_realtime_results


# -----------------------------------
# World Class Search Engine
# -----------------------------------

def world_class_search(query: str, goal: Optional[str] = None) -> List[Dict]:
    """
    World-class search pipeline

    Query → Intent → Domain → Real-time → Results
    """

    try:
        # 1. Detect intent
        intent = classify_intent(query)

        # 2. Route domain
        domain = route_domain(intent)

        # 3. Fetch real-time data
        results = fetch_realtime_results(
            query=query,
            domain=domain,
            goal=goal
        )

        return results

    except Exception as e:
        print(f"Search error: {e}")
        return []


# -----------------------------------
# Backward Compatibility Functions
# (IMPORTANT - DO NOT REMOVE)
# -----------------------------------

def search_knowledge(query: str, goal: Optional[str] = None):
    """
    Backward compatibility
    Used by existing app.py
    """
    return world_class_search(query, goal)


def get_recommendations(query: str, goal: Optional[str] = None):
    """
    Backward compatibility
    Used by UI recommendation engine
    """
    return world_class_search(query, goal)


# -----------------------------------
# Optional Advanced Ranking
# -----------------------------------

def rank_results(results: List[Dict]) -> List[Dict]:
    """
    Rank results by relevance score
    """

    try:
        return sorted(
            results,
            key=lambda x: x.get("score", 0),
            reverse=True
        )
    except Exception:
        return results


# -----------------------------------
# Filter by Goal
# -----------------------------------

def filter_by_goal(results: List[Dict], goal: Optional[str]):
    """
    Filter results by user goal
    """

    if not goal:
        return results

    filtered = []

    for item in results:
        text = str(item).lower()

        if goal.lower() in text:
            filtered.append(item)

    return filtered
