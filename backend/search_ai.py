
from intent_classifier import classify_intent
from domain_router import route_domain
from realtime_fetch import fetch_realtime

def search(query):
    intent = classify_intent(query)
    domain = route_domain(intent)
    realtime = fetch_realtime(query)

    return {
        "query": query,
        "intent": intent,
        "domain": domain,
        "results": realtime["results"]
    }
