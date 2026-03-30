import re
from typing import List, Dict, Any


# ================================
# Intent Detection
# ================================
def detect_intent(query: str) -> str:
    q = query.lower()

    if any(x in q for x in ["best", "top", "recommend", "which"]):
        return "product"

    if any(x in q for x in [
        "what", "how", "cycle", "dosage",
        "benefits", "side effects"
    ]):
        return "research"

    if any(x in q for x in [
        "workout", "exercise", "routine",
        "fat loss", "muscle gain"
    ]):
        return "training"

    return "general"


# ================================
# Fast Search Dataset
# ================================
def fast_results(query):

    return [
        {
            "title": "Creatine Monohydrate",
            "category": "supplement",
            "description": "Best supplement for muscle gain"
        },
        {
            "title": "Pre Workout Supplements",
            "category": "supplement",
            "description": "Best pre workout for energy and pumps"
        },
        {
            "title": "HIIT Fat Loss Workout",
            "category": "exercise",
            "description": "High intensity fat loss training"
        },
        {
            "title": "Push Pull Legs Split",
            "category": "exercise",
            "description": "Best hypertrophy workout"
        },
        {
            "title": "Testosterone Cycle",
            "category": "ped",
            "description": "Anabolic steroid cycle"
        },
        {
            "title": "Whey Protein",
            "category": "supplement",
            "description": "Protein for muscle growth"
        }
    ]


# ================================
# Semantic Search (Improved)
# ================================
def semantic_filter(query, results):

    words = query.lower().split()

    filtered = []

    for r in results:
        text = (
            r.get("title", "").lower() +
            r.get("description", "").lower()
        )

        score = sum(1 for w in words if w in text)

        if score > 0:
            r["score"] = score
            filtered.append(r)

    # fallback if empty
    if not filtered:
        return results

    return filtered


# ================================
# Ranking
# ================================
def rank_results(results):

    return sorted(
        results,
        key=lambda x: x.get("score", 0),
        reverse=True
    )


# ================================
# Option Filtering
# ================================
def apply_option_filter(results, options):

    if not options:
        return results

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

    results = rank_results(results)

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
