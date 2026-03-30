
import re

def detect_intent(query):
    q = query.lower()

    if any(x in q for x in ["best","top","recommend"]):
        return "product"

    if any(x in q for x in ["how","what","cycle","dosage","benefits"]):
        return "research"

    if any(x in q for x in ["workout","exercise","routine","split"]):
        return "training"

    return "general"


def semantic_filter(query, results):
    q = query.lower()
    filtered = []

    for r in results:
        title = r.get("title","").lower()
        if any(word in title for word in q.split()):
            filtered.append(r)

    return filtered if filtered else results


def fast_results(query):

    return [
        {"title":"Creatine Monohydrate","category":"supplement"},
        {"title":"HIIT Fat Loss Training","category":"exercise"},
        {"title":"Whey Protein","category":"supplement"},
        {"title":"Testosterone Cycle","category":"ped"}
    ]


def search_knowledge(query):

    intent = detect_intent(query)

    results = fast_results(query)

    results = semantic_filter(query, results)

    return {
        "intent": intent,
        "results": results
    }


def get_recommendations(query):
    return search_knowledge(query)
