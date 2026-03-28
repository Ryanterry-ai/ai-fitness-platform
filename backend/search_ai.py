import requests
import os
import json
from datetime import datetime

SERP_API_KEY = os.getenv("SERP_API_KEY")


# Evidence Based Knowledge Base
KNOWLEDGE_BASE = {
    "whey protein": {
        "name": "Whey Protein",
        "category": "supplement",
        "summary": "Whey protein supports muscle growth, recovery, and strength development.",
        "dosage": "20-40g post workout",
        "timing": "Post workout or morning",
        "cycle_length": "Continuous",
        "benefits": [
            "Muscle growth",
            "Recovery",
            "Strength increase"
        ],
        "side_effects": [
            {"effect": "Digestive discomfort (rare)", "severity": "low"}
        ],
        "safe_for_beginners": True,
        "legal_status": "Legal",
        "evidence_tier": "high"
    },

    "creatine": {
        "name": "Creatine Monohydrate",
        "category": "supplement",
        "summary": "Creatine improves strength, muscle mass, and performance.",
        "dosage": "5g daily",
        "timing": "Post workout",
        "cycle_length": "Continuous",
        "benefits": [
            "Strength increase",
            "Muscle growth",
            "Performance"
        ],
        "side_effects": [
            {"effect": "Water retention", "severity": "low"}
        ],
        "safe_for_beginners": True,
        "legal_status": "Legal",
        "evidence_tier": "high"
    },

    "fat loss": {
        "name": "Fat Loss",
        "category": "fitness",
        "summary": "Fat loss occurs through calorie deficit and resistance training.",
        "dosage": "N/A",
        "timing": "Daily",
        "cycle_length": "8-12 weeks",
        "benefits": [
            "Reduced body fat",
            "Improved health"
        ],
        "side_effects": [
            {"effect": "Low energy (temporary)", "severity": "low"}
        ],
        "safe_for_beginners": True,
        "legal_status": "N/A",
        "evidence_tier": "high"
    }
}


# Main Search Function
def search_knowledge(query, filters=None):

    filters = filters or []
    results = []

    try:

        query_lower = query.lower()

        # Layer 1 — Knowledge Base
        for key in KNOWLEDGE_BASE:

            if key in query_lower:

                item = KNOWLEDGE_BASE[key].copy()
                item["timestamp"] = datetime.utcnow().isoformat()

                results.append(item)


        # Layer 2 — SERP Research
        if SERP_API_KEY:

            url = "https://serpapi.com/search.json"

            params = {
                "q": f"{query} supplement benefits dosage research",
                "api_key": SERP_API_KEY,
                "engine": "google",
                "num": 3
            }

            response = requests.get(url, params=params, timeout=8)

            if response.status_code == 200:

                data = response.json()

                for r in data.get("organic_results", [])[:3]:

                    results.append({
                        "name": r.get("title", query),
                        "category": detect_category(query),
                        "summary": r.get("snippet"),
                        "dosage": "Research Based",
                        "timing": "Varies",
                        "cycle_length": "Varies",
                        "benefits": [
                            "Evidence based benefits"
                        ],
                        "side_effects": [
                            {
                                "effect": "Varies",
                                "severity": "low"
                            }
                        ],
                        "safe_for_beginners": True,
                        "legal_status": "Check local laws",
                        "evidence_tier": "moderate",
                        "source": r.get("displayed_link"),
                        "timestamp": datetime.utcnow().isoformat()
                    })


        # Layer 3 — AI Generated
        if not results:
            results = ai_generated_results(query)


        return results


    except Exception as e:

        print("Search Error:", e)

        return ai_generated_results(query)



# AI Generated Research
def ai_generated_results(query):

    return [

        {
            "name": query.title(),
            "category": detect_category(query),
            "summary": f"{query} has been researched for performance, muscle growth, and recovery.",
            "dosage": "Research based",
            "timing": "Daily",
            "cycle_length": "4-8 weeks",
            "benefits": [
                "Muscle growth",
                "Recovery",
                "Performance"
            ],
            "side_effects": [
                {
                    "effect": "Mild side effects possible",
                    "severity": "low"
                }
            ],
            "safe_for_beginners": True,
            "legal_status": "Check regulations",
            "evidence_tier": "moderate",
            "timestamp": datetime.utcnow().isoformat()
        }

    ]


# Category Detection
def detect_category(query):

    q = query.lower()

    if "sarm" in q:
        return "sarm"

    if "steroid" in q:
        return "steroid"

    if "peptide" in q:
        return "peptide"

    return "supplement"


# Recommendation Engine
def get_recommendations(queries, user=None):

    recommendations = []

    for q in queries[-5:]:

        recommendations.append({
            "name": q,
            "category": detect_category(q),
            "reason": "Based on your searches",
            "safe_for_beginners": True,
            "timestamp": datetime.utcnow().isoformat()
        })


    # Trending Recommendations
    recommendations.append({
        "name": "Creatine",
        "category": "supplement",
        "reason": "Trending",
        "safe_for_beginners": True
    })


    recommendations.append({
        "name": "Whey Protein",
        "category": "supplement",
        "reason": "Trending",
        "safe_for_beginners": True
    })


    return recommendations
