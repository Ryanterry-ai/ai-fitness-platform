"""Deep research tool."""

import concurrent.futures
from datetime import datetime, timezone
from web_search import web_search
from intent_detection import detect_intent

def deep_research(query):
    research = {
        "query": query,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "intent": detect_intent(query),
        "articles": [],
        "verified_sources": [],
        "references": [],
        "source_stats": {"verified": 0, "scientific": 0, "general": 0}
    }
    results = web_search(query, 15)
    for result in results.get("results", []):
        if result["is_verified"]:
            research["source_stats"]["verified"] += 1
            research["verified_sources"].append(result)
        else:
            research["source_stats"]["general"] += 1
        research["articles"].append({
            "title": result["title"],
            "url": result["url"],
            "source": result["domain"],
            "snippet": result["snippet"],
            "is_verified": result["is_verified"],
            "trust_score": result["trust_score"]
        })
    return research
