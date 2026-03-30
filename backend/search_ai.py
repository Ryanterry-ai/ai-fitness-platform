
from typing import List, Dict, Optional

try:
    from .intent_classifier import classify_intent
    from .domain_router import route_domain
    from .realtime_fetch import fetch_realtime_results
except:
    from intent_classifier import classify_intent
    from domain_router import route_domain
    from realtime_fetch import fetch_realtime_results


def world_class_search(query: str, goal: Optional[str] = None) -> List[Dict]:

    intent = classify_intent(query)

    domain = route_domain(intent)

    results = fetch_realtime_results(
        query=query,
        domain=domain,
        goal=goal
    )

    return results


def search_knowledge(query: str, goal: Optional[str] = None):
    return world_class_search(query, goal)


def get_recommendations(query: str, goal: Optional[str] = None):
    return world_class_search(query, goal)
