
import re

GOALS = ["muscle gain","fat loss","strength","endurance"]

def detect_intent(query):
    q = query.lower()

    if any(k in q for k in ["best","top","price","buy"]):
        intent = "product"
    elif any(k in q for k in ["diet","workout","plan"]):
        intent = "training"
    else:
        intent = "research"

    goal=None
    for g in GOALS:
        if g in q:
            goal=g

    return {
        "intent":intent,
        "goal":goal
    }
