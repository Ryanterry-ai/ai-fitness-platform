import re
from typing import List, Dict, Any


# ================================
# Intent Detection
# ================================
def detect_intent(query: str) -> str:
    q = query.lower()

    if any(x in q for x in [
        "best", "top", "recommend", "which", "compare"
    ]):
        return "product"

    if any(x in q for x in [
        "what", "how", "cycle", "dosage", "benefits",
        "side effects", "explain"
    ]):
        return "research"

    if any(x in q for x in [
        "workout", "exercise", "routine", "split",
        "fat loss", "muscle gain"
    ]):
        return "training"

    return "general"


# ================================
# Fast Search
# ================================
def fast_results(query: str):

    return [
        {
            "title": "Creatine Monohydrate",
            "category": "supplement",
            "description": "Best supplement for muscle gain and strength"
        },
        {
            "title": "HIIT Fat Loss Workout",
            "category": "exercise",
            "description": "High intensity fat loss training"
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
            "title": "Push Pull Legs Split",
            "category": "exercise",
            "description": "Best hypertrophy workout split"
        }
    ]


# ================================
# Semantic Filter
# ================================
def semantic_filter(query, results):

    words = query.lower().split()

    filtered = []

    for r in results:
        text = (
            r.get("title", "").lower() +
            r.get("description", "").lower()
        )

        if any(w in text for w in words):
            filtered.append(r)

    return filtered if filtered else results


# ================================
# AI Ranking
# ================================
def rank_results(query, results):

    words = query.lower().split()

    def score(r):
        text = (
            r.get("title", "").lower() +
            r.get("description", "").lower()
        )

        return sum(3 if w in text else 0 for w in words)

    return sorted(results, key=score, reverse=True)


# ================================
# Option Filtering (Safe)
# ================================
def apply_option_filter(results, options):

    if not options:
        return results

    # options can be list
    if isinstance(options, list):

        filtered = []

        for opt in options:
            opt = opt.lower()

            for r in results:
                text = (
                    r.get("title", "").lower() +
                    r.get("description", "").lower()
                )

                if opt in text:
                    filtered.append(r)

        return filtered if filtered else results

    # options can be dict
    if isinstance(options, dict):

        goal = options.get("goal")

        if goal:
            goal = goal.lower()

            filtered = [
                r for r in results
                if goal in (
                    r.get("title", "").lower() +
                    r.get("description", "").lower()
                )
            ]

            return filtered if filtered else results

    return results


# ================================
# Main Search
# ================================
def search_knowledge(query, options=None):

    if not query:
        return {
            "intent": "none",
            "results": []
        }

    intent = detect_intent(query)

    results = fast_results(query)

    results = semantic_filter(query, results)

    results = rank_results(query, results)

    results = apply_option_filter(results, options)

    return {
        "intent": intent,
        "results": results
    }


# ================================
# Recommendations
# ================================
def get_recommendations(query, options=None):

    return search_knowledge(query, options)
