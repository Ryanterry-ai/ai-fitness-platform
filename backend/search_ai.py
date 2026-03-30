from typing import List, Dict, Any


# ========================================
# Indian Multi-Language Intent Intelligence
# ========================================

INDIAN_QUERY_PATTERNS = {

    "supplement": [
        "creatine","whey","protein","pre workout",
        "fat burner","bcaa","mass gainer",
        "best creatine","best protein"
    ],

    "ped": [
        "steroid","testosterone","tren",
        "anavar","dianabol","cycle",
        "test","trenbolone"
    ],

    "gh": [
        "hgh","growth hormone","gh"
    ],

    "peptides": [
        "peptide","bpc","ipamorelin",
        "cjc","tb500","mk677"
    ],

    "fat_loss": [
        "fat loss","weight loss","cutting",
        "belly fat","lose weight",
        "fat burner"
    ],

    "muscle_gain": [
        "muscle gain","bulking",
        "hypertrophy","gain muscle"
    ],

    "training": [
        "workout","exercise","routine",
        "training","split"
    ]
}


# ========================================
# Intent Detection
# ========================================

def detect_intent(query):

    q = query.lower()

    for intent, keywords in INDIAN_QUERY_PATTERNS.items():

        for word in keywords:
            if word in q:
                return intent

    return "general"


# ========================================
# Fast Search Dataset
# ========================================

def fast_results():

    return [

        {
            "title": "Creatine Monohydrate",
            "category": "supplement",
            "description": "Best supplement for muscle gain and strength"
        },

        {
            "title": "Pre Workout Supplements",
            "category": "supplement",
            "description": "Energy and performance boosting supplements"
        },

        {
            "title": "Whey Protein",
            "category": "supplement",
            "description": "Protein powder for muscle building"
        },

        {
            "title": "HIIT Fat Loss Workout",
            "category": "exercise",
            "description": "High intensity fat loss workout"
        },

        {
            "title": "Push Pull Legs Workout",
            "category": "exercise",
            "description": "Best hypertrophy training split"
        },

        {
            "title": "Testosterone Cycle",
            "category": "ped",
            "description": "Anabolic steroid cycle for muscle gain"
        },

        {
            "title": "Trenbolone Cycle",
            "category": "ped",
            "description": "Advanced anabolic steroid cycle"
        },

        {
            "title": "HGH Growth Hormone",
            "category": "gh",
            "description": "Growth hormone for fat loss and recovery"
        },

        {
            "title": "MK677",
            "category": "gh",
            "description": "Growth hormone secretagogue"
        },

        {
            "title": "BPC-157",
            "category": "peptides",
            "description": "Healing peptide for recovery"
        },

        {
            "title": "CJC-1295",
            "category": "peptides",
            "description": "Growth hormone releasing peptide"
        }

    ]


# ========================================
# Semantic Search
# ========================================

def semantic_filter(query, results):

    words = query.lower().split()

    scored = []

    for r in results:

        text = (
            r.get("title","").lower() +
            r.get("description","").lower()
        )

        score = sum(1 for w in words if w in text)

        if score > 0:
            r["score"] = score
            scored.append(r)

    if not scored:
        return results

    return scored


# ========================================
# Ranking
# ========================================

def rank_results(results):

    return sorted(
        results,
        key=lambda x: x.get("score", 0),
        reverse=True
    )


# ========================================
# Option Filtering
# ========================================

def apply_option_filter(results, options):

    if not options:
        return results

    if isinstance(options, list):

        filtered = []

        for opt in options:

            opt = opt.lower()

            for r in results:

                text = (
                    r.get("title","").lower() +
                    r.get("description","").lower()
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
                    r.get("title","").lower() +
                    r.get("description","").lower()
                )
            ]

            return filtered if filtered else results

    return results


# ========================================
# Main Search Engine
# ========================================

def search_knowledge(query, options=None):

    if not query:
        return {
            "intent": "none",
            "results": []
        }

    intent = detect_intent(query)

    results = fast_results()

    # filter by intent category
    intent_filtered = [
        r for r in results
        if intent in r.get("category","")
    ]

    if intent_filtered:
        results = intent_filtered

    results = semantic_filter(query, results)

    results = rank_results(results)

    results = apply_option_filter(results, options)

    return {
        "intent": intent,
        "results": results
    }


# ========================================
# Recommendations
# ========================================

def get_recommendations(query, options=None):

    return search_knowledge(query, options)
