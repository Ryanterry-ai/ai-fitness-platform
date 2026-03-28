# Knowledge Base

KNOWLEDGE_BASE = {
    "supplements": {
        "whey protein": {
            "benefits": ["Muscle growth", "Recovery"],
            "side_effects": ["Bloating (some users)"],
            "best_for": ["Muscle Gain", "Fat Loss"]
        },
        "creatine": {
            "benefits": ["Strength", "Muscle fullness"],
            "side_effects": ["Water retention"],
            "best_for": ["Bulking", "Strength"]
        },
        "fish oil": {
            "benefits": ["Heart health", "Joint health"],
            "side_effects": ["Fishy burps"],
            "best_for": ["General Health"]
        }
    }
}


def search_knowledge(query, filters=None):
    filters = filters or []

    results = []

    for category, items in KNOWLEDGE_BASE.items():
        for name, data in items.items():
            if query.lower() in name.lower():
                results.append({
                    "name": name,
                    "category": category,
                    "data": data
                })

    return results


def get_recommendations(queries, user):

    return {
        "recommended_supplements": [
            "Whey Protein",
            "Creatine",
            "Fish Oil"
        ],
        "recommended_training": [
            "Push Pull Legs",
            "Upper Lower"
        ],
        "recommended_diet": [
            "High Protein Diet"
        ]
    }
