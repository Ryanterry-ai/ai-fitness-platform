
from backend.intent_classifier import classify_intent
from backend.realtime_fetch import fetch_realtime_results
from backend.vector_search import vector_search
from backend.ai_ranker import rank_results
from backend.knowledge_learning import learn

def search_knowledge(query):
    intent = classify_intent(query)
    results = fetch_realtime_results(query, intent)
    results = vector_search(query, results)
    results = rank_results(results)
    learn(query, results)
    return results

def get_recommendations(query):
    return search_knowledge(query)
