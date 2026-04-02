
def classify_intent(query):
    query = query.lower()
    if any(x in query for x in ["exercise","workout","training","fat loss","routine"]):
        return "exercise"
    if any(x in query for x in ["creatine","protein","whey","supplement"]):
        return "supplement"
    if any(x in query for x in ["steroid","sarm","cycle","testosterone"]):
        return "ped"
    if any(x in query for x in ["diet","nutrition","meal"]):
        return "diet"
    return "exercise"
