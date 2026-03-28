def search_knowledge(query, filters=None):
    filters = filters or []

    results = [
        {
            "title": "Best Protein for Muscle Gain",
            "category": "supplement",
            "description": "Whey isolate recommended for lean muscle growth"
        },
        {
            "title": "Fat Loss Diet Plan",
            "category": "diet",
            "description": "High protein, moderate carbs, low fat"
        },
        {
            "title": "Beginner Workout Plan",
            "category": "training",
            "description": "Push pull legs beginner split"
        }
    ]

    return results


def get_recommendations(queries, user):
    return {
        "recommended_supplements": [
            "Whey Protein",
            "Creatine",
            "Fish Oil"
        ],
        "recommended_diets": [
            "High Protein Diet",
            "Fat Loss Diet"
        ],
        "recommended_training": [
            "Push Pull Legs",
            "Upper Lower Split"
        ]
    }
