import requests
import os
import json
from datetime import datetime

SERP_API_KEY = os.getenv("SERP_API_KEY")


# =========================================
# Evidence Knowledge Base (Structured)
# =========================================

KNOWLEDGE_BASE = {

    "creatine": {
        "sections": [
            {
                "title": "What is Creatine",
                "content": "Creatine is a naturally occurring compound that helps produce ATP energy during high intensity exercise."
            },
            {
                "title": "How Creatine Works",
                "content": "Creatine increases phosphocreatine stores allowing faster ATP regeneration and improved strength."
            },
            {
                "title": "Dosage",
                "content": "3-5g daily is recommended based on scientific research."
            }
        ],

        "sources": [
            {
                "name": "PubMed Creatine Research",
                "url": "https://pubmed.ncbi.nlm.nih.gov/?term=creatine"
            },
            {
                "name": "ISSN Creatine Position Stand",
                "url": "https://jissn.biomedcentral.com/articles/10.1186/s12970-017-0173-z"
            }
        ],

        "articles": [
            {
                "title": "ISSN Creatine Position Stand",
                "why": "Most cited creatine research",
                "sources": [
                    {
                        "name": "PubMed",
                        "url": "https://pubmed.ncbi.nlm.nih.gov/28615996/"
                    }
                ]
            }
        ],

        "books": [
            {
                "title": "Science and Development of Muscle Hypertrophy",
                "author": "Brad Schoenfeld",
                "links": [
                    {
                        "name": "Google Books",
                        "url": "https://books.google.com/"
                    }
                ]
            }
        ],

        "videos": [
            {
                "channel": "Jeff Nippard",
                "title": "Creatine: Everything You Need To Know"
            },
            {
                "channel": "Jeremy Ethier",
                "title": "Creatine Explained"
            }
        ]
    },


    "whey protein": {

        "sections": [
            {
                "title": "What is Whey Protein",
                "content": "Whey protein is a fast digesting protein derived from milk used for muscle growth."
            },
            {
                "title": "Benefits",
                "content": "Supports muscle growth, recovery and fat loss."
            }
        ],

        "sources": [
            {
                "name": "PubMed Whey Research",
                "url": "https://pubmed.ncbi.nlm.nih.gov/?term=whey+protein"
            }
        ],

        "videos": [
            {
                "channel": "Jeff Nippard",
                "title": "Best Protein for Muscle Growth"
            }
        ]
    }

}


# =========================================
# Main Search
# =========================================

def search_knowledge(query, filters=None):

    filters = filters or []
    query_lower = query.lower()

    try:

        # Layer 1 — Knowledge Base
        for key in KNOWLEDGE_BASE:

            if key in query_lower:

                data = KNOWLEDGE_BASE[key]

                return {
                    "query": query,
                    "timestamp": datetime.utcnow().isoformat(),
                    "sections": data.get("sections", []),
                    "sources": data.get("sources", []),
                    "articles": data.get("articles", []),
                    "books": data.get("books", []),
                    "videos": data.get("videos", []),
                    "results": [],
                    "recommendations": get_recommendations([query])
                }


        # Layer 2 — SERP API Research

        results = []

        if SERP_API_KEY:

            url = "https://serpapi.com/search.json"

            params = {
                "q": f"{query} supplement research benefits dosage",
                "api_key": SERP_API_KEY,
                "engine": "google",
                "num": 5
            }

            response = requests.get(url, params=params, timeout=8)

            if response.status_code == 200:

                data = response.json()

                for r in data.get("organic_results", [])[:5]:

                    results.append({
                        "title": r.get("title"),
                        "summary": r.get("snippet"),
                        "link": r.get("link"),
                        "source": r.get("displayed_link"),
                        "timestamp": datetime.utcnow().isoformat()
                    })


        if results:

            return {
                "query": query,
                "timestamp": datetime.utcnow().isoformat(),
                "sections": [],
                "sources": [],
                "articles": [],
                "books": [],
                "videos": [],
                "results": results,
                "recommendations": get_recommendations([query])
            }


        # Layer 3 — AI fallback
        return ai_generated_results(query)


    except Exception as e:

        print("Search Error:", e)

        return ai_generated_results(query)



# =========================================
# AI Generated Results
# =========================================

def ai_generated_results(query):

    return {
        "query": query,
        "timestamp": datetime.utcnow().isoformat(),

        "sections": [
            {
                "title": f"Scientific Overview: {query}",
                "content": f"{query} has been researched in sports science and medical literature."
            }
        ],

        "sources": [
            {
                "name": "Google Scholar",
                "url": "https://scholar.google.com"
            }
        ],

        "articles": [],
        "books": [],
        "videos": [],
        "results": [],
        "recommendations": get_recommendations([query])
    }



# =========================================
# Recommendations
# =========================================

def get_recommendations(queries, user=None):

    recommendations = []

    for q in queries[-5:]:

        recommendations.append({
            "title": q,
            "reason": "Based on your search"
        })

    recommendations.extend([

        {
            "title": "Creatine Benefits",
            "reason": "Trending"
        },
        {
            "title": "Best Whey Protein",
            "reason": "Trending"
        },
        {
            "title": "Fat Loss Supplements",
            "reason": "Trending"
        }
    ])

    return recommendations
