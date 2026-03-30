import re
from typing import List, Dict, Any


# ================================
# Intent Detection (Perplexity Style)
# ================================
def detect_intent(query: str) -> str:
    q = query.lower()

    # Product / Recommendation
    if any(x in q for x in [
        "best", "top", "recommend", "which", "good", "compare"
    ]):
        return "product"

    # Research / Information
    if any(x in q for x in [
        "what", "how", "cycle", "dosage", "benefits",
        "side effects", "is", "are", "explain"
    ]):
        return "research"

    # Workout / Training
    if any(x in q for x in [
        "workout", "exercise", "routine", "split",
        "fat loss", "muscle gain", "training"
    ]):
        return "training"

    # Default
    return "general"


# ================================
# Semantic Understanding (ChatGPT Style)
# ================================
def semantic_filter(query: str, results: List[Dict]) -> List[Dict]:

    query_words = query.lower().split()
    filtered = []

    for result in results:
        title = result.get("title", "").lower()
        description = result.get("description", "").lower()

        if any(word in title or word in description for word in query_words):
            filtered.append(result)

    # fallback if nothing matched
    if not filtered:
        return results

    return filtered


# ================================
# Fast Results (Google Style)
# ================================
def fast_results(query: str) -> List[Dict]:

    # This is placeholder fast dataset
    # Can later plug DB / vector search

    return [
        {
            "title": "Creatine Monohydrate",
            "category": "supplement",
            "description": "Best studied supplement for strength and muscle gain"
        },
        {
            "title": "HIIT Fat Loss Training",
            "category": "exercise",
            "description": "High intensity fat loss workout"
        },
        {
            "title": "Whey Protein",
            "category": "supplement",
            "description": "Protein supplement for muscle growth"
        },
        {
            "title": "Testosterone Cycle",
            "category": "ped",
            "description": "Anabolic steroid cycle information"
        },
        {
            "title": "Push Pull Legs Workout",
            "category": "exercise",
            "description": "Best hypertrophy workout split"
        }
    ]


# ================================
# Ranking (AI Style)
# ================================
def rank_results(query: str, results: List[Dict]) -> List[Dict]:

    query = query.lower()

    def score(result):
        title = result.get("title", "").lower()
        description = result.get("description", "").lower()

        score = 0

        for word in query.split():
            if word in title:
                score += 3
            if word in description:
                score += 1

        return score

    return sorted(results, key=score, reverse=True)


# ================================
# Main Search Engine
# ================================
def search_knowledge(query: str, options: Dict = None) -> Dict:

    if not query:
        return {
            "intent": "none",
            "results": []
        }

    # 1. Detect Intent
    intent = detect_intent(query)

    # 2. Fast Search
    results = fast_results(query)

    # 3. Semantic Filter
    results = semantic_filter(query, results)

    # 4. AI Ranking
    results = rank_results(query, results)

    # 5. Option filtering (muscle gain, fat loss etc)
    if options:
        option = options.get("goal")

        if option:
            option = option.lower()
            results = [
                r for r in results
                if option in r.get("description", "").lower()
                or option in r.get("title", "").lower()
            ] or results

    return {
        "intent": intent,
        "results": results
    }


# ================================
# Recommendation API
# ================================
def get_recommendations(query: str, options: Dict = None):

    return search_knowledge(query, options)
