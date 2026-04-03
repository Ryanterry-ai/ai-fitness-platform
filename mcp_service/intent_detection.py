"""Intent detection tool."""

from intent_patterns import INTENT_PATTERNS

def detect_intent(query):
    query_lower = query.lower()
    scores = {}
    for intent_name, config in INTENT_PATTERNS.items():
        score = 0
        for keyword in config["keywords"]:
            if keyword.lower() in query_lower:
                score += config["weight"]
        if score > 0:
            scores[intent_name] = score
    if scores:
        primary_intent = max(scores.keys(), key=lambda k: scores[k])
        confidence = min(scores[primary_intent] / 10, 1.0)
    else:
        primary_intent = "general"
        confidence = 0.3
    return {"primary_intent": primary_intent, "confidence": round(confidence, 2), "all_intents": dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))}
